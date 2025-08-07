from typing import (
    Any,
    Dict,
    Set,
    Type,
    Optional,
    get_origin,
    get_args,
    Union,
    TypeVar,
    Generic,
)
from sqlalchemy.orm import MappedAsDataclass
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy import inspect
from pydantic import BaseModel, ConfigDict, create_model
from dataclasses import dataclass, field


T = TypeVar("T", bound=MappedAsDataclass)


@dataclass
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
    pydantic_config: ConfigDict = field(
        default_factory=lambda: ConfigDict(from_attributes=True)
    )

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
            model_name = config.model_name or mcs._generate_model_name(
                sqlalchemy_model, config
            )

            # Use our mapper to create the Pydantic model
            pydantic_model = mcs._create_pydantic_model(sqlalchemy_model, config)

            # Instead of creating a new class, return the Pydantic model directly
            # but give it the name that was requested
            pydantic_model.__name__ = model_name
            pydantic_model.__qualname__ = model_name

            return pydantic_model
        else:
            # This is the base DTO class - create it normally
            return super().__new__(mcs, name, bases, namespace)

    @staticmethod
    def _generate_model_name(
        sqlalchemy_model: Type[MappedAsDataclass], config: DTOConfig
    ) -> str:
        """Generate a model name based on the SQLAlchemy model and config."""
        base_name = sqlalchemy_model.__name__
        return f"{config.model_name_prefix}{base_name}{config.model_name_suffix}"

    @staticmethod
    def _create_pydantic_model(
        sqlalchemy_model: Type[MappedAsDataclass], config: DTOConfig
    ) -> Type[BaseModel]:
        """Create a Pydantic model from SQLAlchemy model using DTO config."""

        # Generate model name
        model_name = config.model_name or DTOMeta._generate_model_name(
            sqlalchemy_model, config
        )

        # Extract fields from SQLAlchemy model
        fields = DTOMeta._extract_fields(sqlalchemy_model, config)

        # Create the Pydantic model
        pydantic_model = create_model(
            model_name,
            __config__=config.pydantic_config,
            __base__=config.base_model,
            **fields,
        )

        return pydantic_model

    @staticmethod
    def _extract_fields(
        sqlalchemy_model: Type[MappedAsDataclass], config: DTOConfig
    ) -> Dict[str, Any]:
        """Extract fields from SQLAlchemy model and convert to Pydantic format."""
        fields = {}

        # Get SQLAlchemy inspector
        inspector = inspect(sqlalchemy_model)

        # Process each column
        for column_name, column in inspector.columns.items():
            attr = getattr(sqlalchemy_model, column_name)

            # Apply include/exclude logic
            if not DTOMeta._should_include_field(attr, config):
                continue

            # Get field type
            field_type = DTOMeta._get_field_type(attr, column, config)

            # Get default value
            default_value = DTOMeta._get_field_default(attr, column, config)

            fields[column_name] = (field_type, default_value)

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
    def _get_field_type(attr: InstrumentedAttribute, column, config: DTOConfig) -> Type:
        """Get the Pydantic field type for a SQLAlchemy column."""
        # Check if field has custom mapping
        if attr in config.mapped:
            field_type = config.mapped[attr]
        else:
            # Convert SQLAlchemy type to Python type
            field_type = column.type.python_type

        # Handle nullable columns
        if column.nullable and not DTOMeta._is_optional_type(field_type):
            field_type = Optional[field_type]

        return field_type

    @staticmethod
    def _get_field_default(
        attr: InstrumentedAttribute, column, config: DTOConfig
    ) -> Any:
        """Get the default value for a field."""
        # Check custom defaults first
        if attr in config.field_defaults:
            return config.field_defaults[attr]

        # Use SQLAlchemy column default
        if column.default is not None:
            if hasattr(column.default, "arg"):
                return column.default.arg
            else:
                return ...  # Required field
        elif column.nullable:
            return None
        else:
            return ...  # Required field

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
