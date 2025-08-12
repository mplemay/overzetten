"""Main module for the overzetten package, handling DTO generation from SQLAlchemy models."""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import (
    Annotated,
    Any,
    Generic,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

from pydantic import BaseModel, ConfigDict, Field, create_model
from pydantic.fields import FieldInfo
from sqlalchemy import Sequence, inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, RelationshipProperty
from sqlalchemy.orm.attributes import InstrumentedAttribute

T = TypeVar("T", bound=DeclarativeBase)

UNION_OPTIONAL_ARGS_COUNT = 2


@dataclass(frozen=True, slots=True, kw_only=True)
class DTOConfig:
    """Configuration for DTO generation."""

    # Field mappings: SQLAlchemy attribute -> Pydantic type
    mapped: dict[InstrumentedAttribute, Any] = field(default_factory=dict)

    # Fields to exclude
    exclude: set[InstrumentedAttribute] = field(default_factory=set)

    # Fields to include (if set, only these fields will be included)
    include: set[InstrumentedAttribute] | None = None

    # Custom model name (if None, will be auto-generated)
    model_name: str | None = None

    # Pydantic config
    pydantic_config: ConfigDict = field(default_factory=lambda: ConfigDict(from_attributes=True))

    # Base model to inherit from
    base_model: type[BaseModel] = BaseModel

    # Whether to include relationships
    include_relationships: bool = False

    # Custom field defaults
    field_defaults: dict[InstrumentedAttribute, Any] = field(default_factory=dict)

    # Prefix for auto-generated model names
    model_name_prefix: str = ""

    # Suffix for auto-generated model names
    model_name_suffix: str = "DTO"


class DTOMeta(type):
    """Metaclass for DTO classes that handles the generic type resolution."""

    _dto_cache: dict[type[DeclarativeBase], type[BaseModel]] = {}

    def __new__(
        mcs: type[type],
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **_kwargs: Any,  # noqa: ANN401
    ) -> type:
        """Create a new DTO class based on a SQLAlchemy model."""
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
            pydantic_model = mcs._create_pydantic_model(
                sqlalchemy_model,
                config,
                namespace.get("__doc__"),
                processing=set(),
            )

            # Instead of creating a new class, return the Pydantic model directly
            # but give it the name that was requested
            pydantic_model.__name__ = model_name
            pydantic_model.__qualname__ = model_name
            pydantic_model.__module__ = namespace.get("__module__")

            return pydantic_model
        # This is the base DTO class - create it normally
        return super().__new__(mcs, name, bases, namespace)

    @classmethod
    def _get_or_create_dto_for_model(
        mcs: type[type],
        sqlalchemy_model: type[DeclarativeBase],
        config: DTOConfig,
        doc: str | None = None,
        processing: set[type[DeclarativeBase]] | None = None,
    ) -> type[BaseModel] | str:
        """Get a DTO from cache or create it, handling circular references."""
        if sqlalchemy_model in mcs._dto_cache:
            return mcs._dto_cache[sqlalchemy_model]

        if processing and sqlalchemy_model in processing:
            # Circular reference detected, return forward reference
            return mcs._generate_model_name(sqlalchemy_model, config)

        # Add to processing set
        current_processing = (processing or set()) | {sqlalchemy_model}

        # Create the DTO
        dto = mcs._create_pydantic_model(sqlalchemy_model, config, doc, current_processing)
        mcs._dto_cache[sqlalchemy_model] = dto
        return dto

    @staticmethod
    def _generate_model_name(sqlalchemy_model: type[DeclarativeBase], config: DTOConfig) -> str:
        """Generate a model name based on the SQLAlchemy model and config."""
        base_name = sqlalchemy_model.__name__
        return f"{config.model_name_prefix}{base_name}{config.model_name_suffix}"

    @staticmethod
    def _create_pydantic_model(
        sqlalchemy_model: type[DeclarativeBase],
        config: DTOConfig,
        doc: str | None = None,
        processing: set[type[DeclarativeBase]] | None = None,
    ) -> type[BaseModel]:
        """Create a Pydantic model from SQLAlchemy model using DTO config."""
        # Generate model name
        model_name = config.model_name or DTOMeta._generate_model_name(sqlalchemy_model, config)

        # Extract fields from SQLAlchemy model
        fields = DTOMeta._extract_fields(sqlalchemy_model, config, processing)

        # Create the Pydantic model
        return create_model(
            model_name,
            __config__=config.pydantic_config,
            __base__=config.base_model,
            __doc__=doc,
            **fields,
        )

    @staticmethod
    def _process_columns(
        sqlalchemy_model: type[DeclarativeBase],
        inspector: inspect,
        config: DTOConfig,
        fields: dict[str, Any],
    ) -> None:
        """Process SQLAlchemy columns and add them to the fields dictionary."""
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

    @staticmethod
    def _process_column_properties(
        sqlalchemy_model: type[DeclarativeBase],
        inspector: inspect,
        config: DTOConfig,
        fields: dict[str, Any],
    ) -> None:
        """Process SQLAlchemy column properties and add them to the fields dictionary."""
        if hasattr(inspector, "column_properties"):
            for prop_name, prop in inspector.column_properties.items():
                attr = getattr(sqlalchemy_model, prop_name)
                if not DTOMeta._should_include_field(attr, config):
                    continue

                # For column_property, the type is usually derived from its expression
                # and it's generally not nullable unless explicitly defined.
                # We'll pass the property itself to _get_field_type for specific handling.
                field_type = DTOMeta._get_field_type(sqlalchemy_model, attr, prop, config)
                default_value = DTOMeta._get_field_default(
                    attr,
                    prop,
                    config,
                )  # Pass prop as column for default handling

                fields[prop_name] = (field_type, default_value)

    @staticmethod
    def _process_synonyms(
        sqlalchemy_model: type[DeclarativeBase],
        inspector: inspect,
        config: DTOConfig,
        fields: dict[str, Any],
    ) -> None:
        """Process SQLAlchemy synonyms and add them to the fields dictionary."""
        for synonym_name, synonym_obj in inspector.synonyms.items():
            attr = getattr(sqlalchemy_model, synonym_name)
            if not DTOMeta._should_include_field(attr, config):
                continue

            # Get the column that the synonym refers to
            column = inspector.columns.get(synonym_obj.name)

            field_type = DTOMeta._get_field_type(sqlalchemy_model, attr, column, config)
            default_value = DTOMeta._get_field_default(attr, column, config)

            fields[synonym_name] = (field_type, default_value)

    @staticmethod
    def _process_relationships(
        sqlalchemy_model: type[DeclarativeBase],
        inspector: inspect,
        config: DTOConfig,
        fields: dict[str, Any],
        processing: set[type[DeclarativeBase]] | None = None,
    ) -> None:
        """Process SQLAlchemy relationships and add them to the fields dictionary."""
        if not config.include_relationships:
            return

        for rel_name, relationship_obj in inspector.relationships.items():
            attr = getattr(sqlalchemy_model, rel_name)

            # Apply include/exclude logic
            if not DTOMeta._should_include_field(attr, config):
                continue

            # Use existing _get_field_type and _get_field_default for consistency
            field_type = DTOMeta._get_field_type(sqlalchemy_model, attr, relationship_obj, config, processing)
            default_value = DTOMeta._get_field_default(attr, relationship_obj, config)

            fields[rel_name] = (field_type, default_value)

    @staticmethod
    def _extract_fields(
        sqlalchemy_model: type[DeclarativeBase],
        config: DTOConfig,
        processing: set[type[DeclarativeBase]] | None = None,
    ) -> dict[str, Any]:
        """Extract fields from SQLAlchemy model and convert to Pydantic format."""
        fields = {}

        # Get SQLAlchemy inspector
        if not hasattr(sqlalchemy_model, "__table__"):
            error_message = (
                f"Cannot create DTO from abstract or unmapped SQLAlchemy model '{(sqlalchemy_model.__name__)}'."
            )
            raise TypeError(error_message)

        inspector = inspect(sqlalchemy_model)

        DTOMeta._process_columns(sqlalchemy_model, inspector, config, fields)

        DTOMeta._process_column_properties(sqlalchemy_model, inspector, config, fields)

        # Validate mapped fields that are not columns
        for mapped_attr in config.mapped:
            if isinstance(mapped_attr, InstrumentedAttribute) and not hasattr(sqlalchemy_model, mapped_attr.key):
                error_message = (
                    f"Mapped attribute '{(mapped_attr.key)}' does not exist on SQLAlchemy model "
                    f"'{(sqlalchemy_model.__name__)}'."
                )
                raise ValueError(error_message)

        DTOMeta._process_synonyms(sqlalchemy_model, inspector, config, fields)

        DTOMeta._process_relationships(sqlalchemy_model, inspector, config, fields, processing)

        return fields

    @staticmethod
    def _get_mapped_field_type(
        mapped_value: Any,  # noqa: ANN401
        obj: Any,
    ) -> type:
        """Determine the field type when a custom mapping is provided."""
        if isinstance(mapped_value, FieldInfo):
            return obj.type.python_type if hasattr(obj, "type") else Any
        if get_origin(mapped_value) is Annotated:
            return mapped_value  # Keep the Annotated type as is
        return mapped_value

    @staticmethod
    def _get_mapped_field_default(attr: InstrumentedAttribute, config: DTOConfig) -> Any:  # noqa: ANN401
        """Get the default value for a mapped field."""
        mapped_value = config.mapped[attr]
        if isinstance(mapped_value, FieldInfo):
            return mapped_value
        if get_origin(mapped_value) is Annotated:
            for arg in get_args(mapped_value)[1:]:  # Iterate through metadata arguments
                if isinstance(arg, FieldInfo):
                    return arg  # Return the FieldInfo object
        return None  # Or some other appropriate default if no FieldInfo is found

    @staticmethod
    def _get_custom_field_default(attr: InstrumentedAttribute, config: DTOConfig) -> Any:  # noqa: ANN401
        """Get the custom default value for a field."""
        if attr in config.field_defaults:
            custom_default = config.field_defaults[attr]
            if isinstance(custom_default, Callable):
                return Field(default_factory=custom_default)
            return custom_default
        return None

    @staticmethod
    def _get_sqlalchemy_default(obj: Any) -> Any:  # noqa: ANN401
        """Get the default value from SQLAlchemy column or server default."""
        if hasattr(obj, "primary_key") and obj.primary_key and hasattr(obj, "autoincrement") and obj.autoincrement:
            return Field(default=None)  # Pydantic default is None for autoincrementing PKs
        if hasattr(obj, "default") and obj.default is not None:
            # Handle Sequence objects directly
            if isinstance(obj.default, Sequence):
                return Field(default=None)  # Sequences are handled by DB, not Pydantic default
            # Handle callable defaults from SQLAlchemy
            if hasattr(obj.default, "arg") and isinstance(obj.default.arg, Callable):
                return Field(default_factory=obj.default.arg)
            # Handle scalar defaults from SQLAlchemy
            if hasattr(obj.default, "arg"):
                return Field(default=obj.default.arg)
            # Fallback for other types of obj.default (e.g., literal values directly)
            return Field(default=obj.default)
        if hasattr(obj, "server_default") and obj.server_default is not None:
            # Fields with server_default are not required in Pydantic
            return Field(default=None)
        if hasattr(obj, "nullable") and obj.nullable:
            return Field(default=None)
        return None

    @staticmethod
    def _get_final_default(attr: InstrumentedAttribute, obj: Any) -> Any:  # noqa: ANN401
        """Determine the final default value based on relationship or column property."""
        if isinstance(attr.property, RelationshipProperty):
            # This is a relationship, which is typically optional
            return Field(default=None)

        # For column_property, they are generally required unless explicitly made optional via mapping
        # For regular columns, they are required by default
        return ...

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
        sqlalchemy_model: type[DeclarativeBase],
        attr: InstrumentedAttribute,
        obj: Any,  # Renamed from 'column' to 'obj' to be more generic  # noqa: ANN401
        config: DTOConfig,
        processing: set[type[DeclarativeBase]] | None = None,
    ) -> type:
        """Get the Pydantic field type for a SQLAlchemy column or column_property."""
        field_type = Any  # Default type
        mapped_type_is_set = False

        # 1. Check for an explicit mapping in the DTOConfig.
        if attr in config.mapped:
            mapped_value = config.mapped[attr]
            # Check if the mapping provides a concrete type.
            # A Field() with no annotation does not count as a type mapping.
            if not (isinstance(mapped_value, FieldInfo) and mapped_value.annotation is None):
                field_type = DTOMeta._get_mapped_field_type(mapped_value, obj)
                mapped_type_is_set = True

        # 2. If not mapped, or if the mapping didn't set a type, infer the type.
        if not mapped_type_is_set:
            if isinstance(attr.property, RelationshipProperty):
                related_model = attr.property.mapper.class_
                related_dto_config = DTOConfig(model_name_suffix=config.model_name_suffix)
                related_dto = DTOMeta._get_or_create_dto_for_model(
                    related_model,
                    related_dto_config,
                    processing=processing,
                )
                field_type = list[related_dto] if attr.property.uselist else related_dto  # type: ignore

            elif hasattr(sqlalchemy_model, "__annotations__") and attr.key in sqlalchemy_model.__annotations__:
                mapped_annotation = sqlalchemy_model.__annotations__[attr.key]
                if get_origin(mapped_annotation) is Mapped:
                    mapped_args = get_args(mapped_annotation)
                    if mapped_args:
                        field_type = mapped_args[0]
                    elif hasattr(obj, "type"):
                        field_type = obj.type.python_type
                else:
                    field_type = mapped_annotation

            elif hasattr(obj, "type"):
                field_type = obj.type.python_type

        # 3. Finally, apply nullability based on the SQLAlchemy column's properties.
        is_nullable = (hasattr(obj, "nullable") and obj.nullable) or (
            isinstance(attr.property, RelationshipProperty) and not attr.property.uselist
        )
        if is_nullable and not DTOMeta._is_optional_type(field_type):
            field_type = field_type | None

        return field_type

    @staticmethod
    def _get_field_default(attr: InstrumentedAttribute, obj: Any, config: DTOConfig) -> Any:  # noqa: ANN401
        """Get the default value for a field."""
        # Check for a mapped Field() object first
        if attr in config.mapped:
            result = DTOMeta._get_mapped_field_default(attr, config)
            if result is not None:
                return result

        # Check custom defaults
        result = DTOMeta._get_custom_field_default(attr, config)
        if result is not None:
            return result

        # Use SQLAlchemy column default or server_default
        result = DTOMeta._get_sqlalchemy_default(obj)
        if result is not None:
            return result
        # If obj is not a column or has no default/server_default/nullable, it's required unless it's a relationship
        # For column_property, they are generally required unless explicitly made optional via mapping
        return DTOMeta._get_final_default(attr, obj)

    @staticmethod
    def _is_optional_type(field_type: Any) -> bool:  # noqa: ANN401
        """Check if a type annotation represents an Optional type."""
        origin = get_origin(field_type)
        if origin is Union:
            args = get_args(field_type)
            return len(args) == UNION_OPTIONAL_ARGS_COUNT and type(None) in args
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
