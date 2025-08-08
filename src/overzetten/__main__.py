from collections.abc import Callable
from dataclasses import dataclass, field
from typing import (
    Annotated,
    Any,
    Dict,
    Generic,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

from pydantic import BaseModel, ConfigDict, Field, create_model
from pydantic.fields import FieldInfo
from sqlalchemy import Sequence, inspect
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.orm.attributes import InstrumentedAttribute

T = TypeVar("T", bound=DeclarativeBase)


@dataclass(frozen=True, slots=True, kw_only=True)
class DTOConfig:
    """Configuration for DTO generation."""

    # Field mappings: SQLAlchemy attribute -> Pydantic type
    mapped: Dict[InstrumentedAttribute, Any] = field(default_factory=dict)

    # Fields to exclude
    exclude: Set[InstrumentedAttribute] = field(default_factory=set)

    # Fields to include (if set, only these fields will be included)
    include: Optional[Set[InstrumentedAttribute]] = None

    # Custom model name (if None, will be auto-generated)
    model_name: Optional[str] = None

    # Pydantic config
    pydantic_config: ConfigDict = field(default_factory=lambda: ConfigDict(from_attributes=True))

    # Base model to inherit from
    base_model: Type[BaseModel] = BaseModel

    # Whether to include relationships
    include_relationships: bool = False

    # Custom field defaults
    field_defaults: Dict[InstrumentedAttribute, Any] = field(default_factory=dict)

    # Prefix for auto-generated model names
    model_name_prefix: str = ""

    # Suffix for auto-generated model names
    model_name_suffix: str = "DTO"


class DTOMeta(type):
    """Metaclass for DTO classes that handles the generic type resolution."""

    def __new__(mcs, name, bases, namespace, **kwargs):
        # Check if this is a concrete DTO class (not the base DTO class)
        sqlalchemy_model = None
        config = None
        is_concrete_dto = False

        # Look for DTO[Model] in the bases
        if "__orig_bases__" in namespace:
            for base in namespace["__orig_bases__"]:
                if (
                    hasattr(base, "__origin__")
                    and base.__origin__ is not None
                    and getattr(base.__origin__, "__name__", None) == "DTO"
                ):
                    # Extract the SQLAlchemy model type
                    args = get_args(base)
                    if args:
                        sqlalchemy_model = args[0]
                        config = namespace.get("config", DTOConfig())
                        is_concrete_dto = True
                        break

        # If this is a concrete DTO, create it as a Pydantic model
        if is_concrete_dto and sqlalchemy_model is not None:
            # Generate model name
            model_name = config.model_name or mcs._generate_model_name(sqlalchemy_model, config)

            # Use our mapper to create the Pydantic model
            pydantic_model = mcs._create_pydantic_model(sqlalchemy_model, config, namespace.get('__doc__'))

            # Instead of creating a new class, return the Pydantic model directly
            # but give it the name that was requested
            pydantic_model.__name__ = model_name
            pydantic_model.__qualname__ = model_name
            pydantic_model.__module__ = namespace.get("__module__")

            return pydantic_model
        else:
            # This is the base DTO class - create it normally
            return super().__new__(mcs, name, bases, namespace)

    @staticmethod
    def _generate_model_name(sqlalchemy_model: Type[DeclarativeBase], config: DTOConfig) -> str:
        """Generate a model name based on the SQLAlchemy model and config."""
        base_name = sqlalchemy_model.__name__
        return f"{config.model_name_prefix}{base_name}{config.model_name_suffix}"

    @staticmethod
    def _create_pydantic_model(sqlalchemy_model: Type[DeclarativeBase], config: DTOConfig, doc: Optional[str] = None) -> Type[BaseModel]:
        """Create a Pydantic model from SQLAlchemy model using DTO config."""
        # Generate model name
        model_name = config.model_name or DTOMeta._generate_model_name(sqlalchemy_model, config)

        # Extract fields from SQLAlchemy model
        fields = DTOMeta._extract_fields(sqlalchemy_model, config)

        # Create the Pydantic model
        pydantic_model = create_model(
            model_name,
            __config__=config.pydantic_config,
            __base__=config.base_model,
            __doc__=doc,
            **fields,
        )

        return pydantic_model

    @staticmethod
    def _extract_fields(sqlalchemy_model: Type[DeclarativeBase], config: DTOConfig) -> Dict[str, Any]:
        """Extract fields from SQLAlchemy model and convert to Pydantic format."""
        fields = {}

        # Get SQLAlchemy inspector
        if not hasattr(sqlalchemy_model, "__table__"):
            raise TypeError(
                f"Cannot create DTO from abstract or unmapped SQLAlchemy model '{(sqlalchemy_model.__name__)}'."
            )

        inspector = inspect(sqlalchemy_model)

        # Process each column
        for column_name, column in inspector.columns.items():
            attr = getattr(sqlalchemy_model, column_name)

            # Apply include/exclude logic
            if not DTOMeta._should_include_field(attr, config):
                continue

            # Get field type
            field_type = DTOMeta._get_field_type(sqlalchemy_model, attr, column, config)

            # Get default value
            default_value = DTOMeta._get_field_default(attr, column, config)

            fields[column_name] = (field_type, default_value)

        # Process column properties
        if hasattr(inspector, 'column_properties'):
            for prop_name, prop in inspector.column_properties.items():
                attr = getattr(sqlalchemy_model, prop_name)
                if not DTOMeta._should_include_field(attr, config):
                    continue

                # For column_property, the type is usually derived from its expression
                # and it's generally not nullable unless explicitly defined.
                # We'll pass the property itself to _get_field_type for specific handling.
                field_type = DTOMeta._get_field_type(sqlalchemy_model, attr, prop, config)
                default_value = DTOMeta._get_field_default(attr, prop, config) # Pass prop as column for default handling

                fields[prop_name] = (field_type, default_value)

        # Validate mapped fields that are not columns
        for mapped_attr, _ in config.mapped.items():
            if isinstance(mapped_attr, InstrumentedAttribute) and not hasattr(sqlalchemy_model, mapped_attr.key):
                raise ValueError(
                    f"Mapped attribute '{(mapped_attr.key)}' does not exist on SQLAlchemy model "
                    f"'{(sqlalchemy_model.__name__)}'."
                )

        for synonym_name, synonym_obj in inspector.synonyms.items():
            attr = getattr(sqlalchemy_model, synonym_name)
            if not DTOMeta._should_include_field(attr, config):
                continue

            # Get the column that the synonym refers to
            column = inspector.columns.get(synonym_obj.name)

            field_type = DTOMeta._get_field_type(sqlalchemy_model, attr, column, config)
            default_value = DTOMeta._get_field_default(attr, column, config)

            fields[synonym_name] = (field_type, default_value)

        # Process relationships if enabled
        if config.include_relationships:
            for rel_name, relationship in inspector.relationships.items():
                attr = getattr(sqlalchemy_model, rel_name)

                if not DTOMeta._should_include_field(attr, config):
                    continue

                # Check if relationship has custom mapping
                if attr in config.mapped:
                    field_type = config.mapped[attr]
                else:
                    # Default to Any for relationships without explicit mapping
                    field_type = Any

                # Get default value
                default_value = config.field_defaults.get(attr, None)

                # Handle collection vs. scalar relationships
                if relationship.uselist:
                    # For lists (one-to-many, many-to-many), the type is the list itself
                    fields[rel_name] = (field_type, default_value or [])
                else:
                    # For scalar (many-to-one, one-to-one), it can be optional
                    fields[rel_name] = (Optional[field_type], default_value)

        return fields

    @staticmethod
    def _should_include_field(attr: InstrumentedAttribute, config: DTOConfig) -> bool:
        """Determine if a field should be included based on config."""
        # Check exclusions first
        if attr in config.exclude:
            return False

        # If include is specified, only include those fields
        if config.include is not None:
            return attr in config.include

        return True

    @staticmethod
    def _get_field_type(
        sqlalchemy_model: Type[DeclarativeBase],
        attr: InstrumentedAttribute,
        obj, # Renamed from 'column' to 'obj' to be more generic
        config: DTOConfig,
    ) -> Type:
        """Get the Pydantic field type for a SQLAlchemy column or column_property."""
        # Check if field has custom mapping
        if attr in config.mapped:
            mapped_value = config.mapped[attr]
            # If the mapped value is a FieldInfo (like from Field()),
            # the type is the python_type of the column, and the FieldInfo
            # is handled as a default value.
            if isinstance(mapped_value, FieldInfo):
                if hasattr(obj, 'type'): # For Column objects
                    field_type = obj.type.python_type
                else: # For column_property or other non-column objects
                    field_type = Any # Fallback for column_property if type cannot be inferred
            elif get_origin(mapped_value) is Annotated:
                field_type = mapped_value  # Keep the Annotated type as is
            else:
                field_type = mapped_value
        else:
            # Try to get the type from the Mapped annotation first
            if hasattr(sqlalchemy_model, "__annotations__") and attr.key in sqlalchemy_model.__annotations__:
                mapped_annotation = sqlalchemy_model.__annotations__[attr.key]
                # Extract the inner type from Mapped[T]
                if get_origin(mapped_annotation) is Mapped:
                    mapped_args = get_args(mapped_annotation)
                    if mapped_args:
                        field_type = mapped_args[0]
                    else:
                        if hasattr(obj, 'type'):
                            field_type = obj.type.python_type
                        else:
                            field_type = Any # Fallback for column_property
                else:
                    field_type = mapped_annotation
            else:
                # Fallback to SQLAlchemy's python_type or Any for column_property
                if hasattr(obj, 'type'):
                    field_type = obj.type.python_type
                else:
                    field_type = Any # Fallback for column_property

        # Handle nullable columns/properties
        # For column_property, assume non-nullable unless explicitly mapped or inferred
        if (hasattr(obj, 'nullable') and obj.nullable) and not DTOMeta._is_optional_type(field_type):
            field_type = Optional[field_type]

        return field_type

    @staticmethod
    def _get_field_default(attr: InstrumentedAttribute, obj, config: DTOConfig) -> Any:
        """Get the default value for a field."""
        # Check for a mapped Field() object first
        if attr in config.mapped:
            mapped_value = config.mapped[attr]
            if isinstance(mapped_value, FieldInfo):
                return mapped_value
            elif get_origin(mapped_value) is Annotated:  # Add this block
                for arg in get_args(mapped_value)[1:]:  # Iterate through metadata arguments
                    if isinstance(arg, FieldInfo):
                        return arg  # Return the FieldInfo object

        # Check custom defaults
        if attr in config.field_defaults:
            custom_default = config.field_defaults[attr]
            if isinstance(custom_default, Callable):
                return Field(default_factory=custom_default)
            return custom_default

        # Use SQLAlchemy column default or server_default
        # For column_property, they typically don't have defaults in the same way columns do
        if hasattr(obj, 'primary_key') and obj.primary_key and hasattr(obj, 'autoincrement') and obj.autoincrement:
            return None  # Pydantic default is None for autoincrementing PKs

        if hasattr(obj, 'default') and obj.default is not None:
            # Handle Sequence objects directly
            if isinstance(obj.default, Sequence):
                return None  # Sequences are handled by DB, not Pydantic default
            # Handle callable defaults from SQLAlchemy
            elif hasattr(obj.default, "arg") and isinstance(obj.default.arg, Callable):
                return Field(default_factory=obj.default.arg)
            # Handle scalar defaults from SQLAlchemy
            elif hasattr(obj.default, "arg"):
                return obj.default.arg
            # Fallback for other types of obj.default (e.g., literal values directly)
            else:
                return obj.default
        elif hasattr(obj, 'server_default') and obj.server_default is not None:
            # Fields with server_default are not required in Pydantic
            return None
        elif hasattr(obj, 'nullable') and obj.nullable:
            return None
        else:
            # If obj is not a column or has no default/server_default/nullable, it's required unless it's a relationship
            # For column_property, they are generally required unless explicitly made optional via mapping
            if isinstance(obj, InstrumentedAttribute) and obj.is_property and not obj.is_column_property:
                # This is a relationship, which is typically optional
                return None
            elif isinstance(obj, InstrumentedAttribute) and obj.is_column_property:
                # Column properties are generally required unless explicitly optional
                return ...
            else:
                return ...  # Required field by default for columns without defaults

    @staticmethod
    def _is_optional_type(field_type) -> bool:
        """Check if a type annotation represents an Optional type."""
        origin = get_origin(field_type)
        if origin is Union:
            args = get_args(field_type)
            return len(args) == 2 and type(None) in args
        return False


class DTO(Generic[T], metaclass=DTOMeta):
    """
    Base DTO class for creating Pydantic models from SQLAlchemy models.

    Usage:
        class UserWriteDTO(DTO[User]):
            config = DTOConfig(
                exclude={User.id, User.created_at},
                mapped={User.email: EmailStr}
            )
    """

    config: DTOConfig = DTOConfig()
