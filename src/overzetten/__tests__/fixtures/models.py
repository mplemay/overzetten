"""SQLAlchemy models for testing DTO generation."""

import datetime
import enum
import uuid
from decimal import Decimal
from typing import Any, ClassVar, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    Numeric,
    Sequence,
    String,
    Table,
    Text,
    Time,
    TypeDecorator,
    case,
)
from sqlalchemy.dialects import mysql, postgresql
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    """Define base class for SQLAlchemy declarative models."""


class PostgresBase(DeclarativeBase):
    """Define base class for PostgreSQL-specific SQLAlchemy models."""


class MySQLBase(DeclarativeBase):
    """Define base class for MySQL-specific SQLAlchemy models."""


class User(Base):
    """Represent a user in the database."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[str | None]
    age: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    registered_on: Mapped[datetime.date] = mapped_column(Date)
    last_login: Mapped[datetime.time] = mapped_column(Time)
    balance: Mapped[float] = mapped_column(Float)
    rating: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    data: Mapped[bytes | None] = mapped_column(LargeBinary)
    preferences: Mapped[dict | None] = mapped_column(JSON)
    tags: Mapped[list | None] = mapped_column(JSON)
    uuid_field: Mapped[str | None] = mapped_column(String(36))
    secret_field: Mapped[str | None] = mapped_column(Text)
    json_field: Mapped[dict | None] = mapped_column(JSON)
    addresses: Mapped[list["Address"]] = relationship(back_populates="user")

    @hybrid_property
    def full_name(self) -> str:
        """Return the full name of the user."""
        if self.fullname:
            return f"{self.name} {self.fullname}"
        return self.name

    @full_name.expression
    def full_name(cls) -> Any:  # noqa: N805, ANN401
        """Provide SQL expression for the full name of the user."""
        return case((cls.fullname is not None, cls.name + " " + cls.fullname), else_=cls.name)


class Address(Base):
    """Represent an address in the database."""

    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    user: Mapped[User | None] = relationship(back_populates="addresses")


class TypeConversionTestModel(Base):
    """Define model for testing type conversions."""

    __tablename__ = "type_conversion_test"

    id: Mapped[int] = mapped_column(primary_key=True)
    string_field: Mapped[str] = mapped_column(String)
    integer_field: Mapped[int] = mapped_column(Integer)
    boolean_field: Mapped[bool] = mapped_column(Boolean)
    datetime_field: Mapped[datetime.datetime] = mapped_column(DateTime)
    date_field: Mapped[datetime.date] = mapped_column(Date)
    time_field: Mapped[datetime.time] = mapped_column(Time)
    text_field: Mapped[str] = mapped_column(String)
    float_field: Mapped[float] = mapped_column(Float)
    numeric_field: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    large_binary_field: Mapped[bytes] = mapped_column(LargeBinary)


class NullableTestModel(Base):
    """Define model for testing nullable field handling."""

    __tablename__ = "nullable_test"

    id: Mapped[int] = mapped_column(primary_key=True)
    required_field: Mapped[str]
    nullable_field: Mapped[str | None]
    already_optional_field: Mapped[int | None]
    nullable_email: Mapped[str | None] = mapped_column(String)


class ServerNullableTestModel(Base):
    """Define model for testing server-side nullable fields and defaults."""

    __tablename__ = "server_nullable_test"
    id: Mapped[int] = mapped_column(primary_key=True)
    # Nullable with a server default
    server_nullable_field: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        server_default="server_default_value",
    )
    # Not nullable with a server default
    server_not_nullable_field: Mapped[str] = mapped_column(String, server_default="another_server_default")


class DefaultValueTestModel(Base):
    """Define model for testing various default value scenarios."""

    __tablename__ = "default_value_test"

    id: Mapped[int] = mapped_column(primary_key=True)
    required_field: Mapped[str]
    server_default_field: Mapped[str] = mapped_column(server_default="server_default_value")
    scalar_default: Mapped[str] = mapped_column(default="default_value")
    callable_default: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)


class RequiredFieldTestModel(Base):
    """Define model for testing required field logic."""

    __tablename__ = "required_field_test_model"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Not nullable, no default = required
    required_no_default: Mapped[str] = mapped_column(String)
    # Nullable, no default = Optional[T] with None default
    nullable_no_default: Mapped[str | None] = mapped_column(String, nullable=True)
    # Not nullable, has default = T with default
    required_with_default: Mapped[str] = mapped_column(String, default="default_value")
    # Nullable, has default = Optional[T] with default
    nullable_with_default: Mapped[str | None] = mapped_column(String, nullable=True, default="nullable_default")
    # Not nullable, has server_default = T with default
    required_with_server_default: Mapped[str] = mapped_column(String, server_default="server_default_value")
    # Boolean field with default
    boolean_with_default: Mapped[bool] = mapped_column(Boolean, default=False)
    # Nullable, has server_default = Optional[T] with None default (from Pydantic perspective)
    nullable_with_server_default: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        server_default="nullable_server_default",
    )


class Node(Base):
    """Define SQLAlchemy Node model for self-referential relationships."""

    __tablename__ = "nodes"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    # Self-referential relationship
    parent_node_id: Mapped[int | None] = mapped_column(ForeignKey("nodes.id"))
    parent_node: Mapped[Optional["Node"]] = relationship(back_populates="child_nodes", remote_side=[id])
    child_nodes: Mapped[list["Node"]] = relationship(back_populates="parent_node")


class BaseMappedModel(Base):
    """Define base model for testing inheritance and field mapping."""

    __tablename__ = "base_mapped_model"
    id: Mapped[int] = mapped_column(primary_key=True)
    base_field: Mapped[str]
    common_field: Mapped[str]


class ChildMappedModel(BaseMappedModel):
    """Define child model for testing inheritance and field mapping."""

    __tablename__ = "child_mapped_model"
    id: Mapped[int] = mapped_column(ForeignKey("base_mapped_model.id"), primary_key=True)
    child_field: Mapped[str]


class TimestampMixin:
    """Provide mixin for created_at and updated_at timestamps."""

    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now, onupdate=datetime.datetime.now)


class Product(TimestampMixin, Base):
    """Represent a product in the database."""

    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str | None]


class AbstractBaseModel(Base):
    """Define abstract base model for inheritance testing."""

    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)
    abstract_field: Mapped[str]


class ConcreteModel(AbstractBaseModel):
    """Define concrete model inheriting from AbstractBaseModel."""

    __tablename__ = "concrete_model"
    concrete_field: Mapped[str]


class Employee(Base):
    """Define base class for polymorphic Employee models."""

    __tablename__ = "employee"
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str]

    __mapper_args__: ClassVar[dict] = {
        "polymorphic_on": "type",
        "polymorphic_identity": "employee",
    }


class Manager(Employee):
    """Define manager model in polymorphic inheritance."""

    __mapper_args__: ClassVar[dict] = {
        "polymorphic_identity": "manager",
    }

    manager_data: Mapped[str]


class Engineer(Employee):
    """Define engineer model in polymorphic inheritance."""

    __mapper_args__: ClassVar[dict] = {
        "polymorphic_identity": "engineer",
    }

    engineer_info: Mapped[str]


# Custom Types (moved to appear before AdvancedDefaultTestModel)
class CustomInt(TypeDecorator):
    """Define custom SQLAlchemy Integer type that multiplies/divides by 10."""

    impl = Integer
    cache_ok = True

    def process_bind_param(self, value: Any, _dialect: Any) -> Any:  # noqa: ANN401
        """Process value before binding to database."""
        return value * 10 if value is not None else None

    def process_result_value(self, value: Any, _dialect: Any) -> Any:  # noqa: ANN401
        """Process value after fetching from database."""
        return value // 10 if value is not None else None

    @property
    def python_type(self) -> type:
        """Return the Python type for this custom type."""
        return int


class CustomTypeModel(Base):
    """Define model using a custom SQLAlchemy type."""

    __tablename__ = "custom_type_test"
    id: Mapped[int] = mapped_column(primary_key=True)
    custom_field: Mapped[int] = mapped_column(CustomInt)


class NoPythonType(TypeDecorator):
    """Define custom SQLAlchemy type without a defined python_type."""

    impl = String
    cache_ok = True

    def process_bind_param(self, value: Any, _dialect: Any) -> Any:  # noqa: ANN401
        """Process value before binding to database."""
        return value

    def process_result_value(self, value: Any, _dialect: Any) -> Any:  # noqa: ANN401
        """Process value after fetching from database."""
        return value


class NoPythonTypeModel(Base):
    """Define model using a custom SQLAlchemy type without a python_type."""

    __tablename__ = "no_python_type_test"
    id: Mapped[int] = mapped_column(primary_key=True)
    no_python_field: Mapped[Any] = mapped_column(NoPythonType)


# AdvancedDefaultTestModel (now after CustomInt and CustomTypeModel)
class AdvancedDefaultTestModel(MappedAsDataclass, Base):
    """Define model for testing advanced default value scenarios."""

    __tablename__ = "advanced_default_test"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Field with init=False, should not appear in DTO constructor
    computed_value: Mapped[int] = mapped_column(Integer, init=False, default=100)
    # Field with insert_default
    insert_only_value: Mapped[str] = mapped_column(String, insert_default="insert_default_val")
    # Field with a sequence (for non-PK, though less common)
    sequence_value: Mapped[int] = mapped_column(Integer, default=Sequence("my_seq"))
    # Field with a custom type and default
    custom_type_default: Mapped[int] = mapped_column(CustomInt, default=5)


class MappedAnnotationTestModel(Base):
    """Define model for testing Mapped annotations vs raw type hints."""

    __tablename__ = "mapped_annotation_test"
    __allow_unmapped__ = True
    id: Mapped[int] = mapped_column(primary_key=True)
    mapped_str: Mapped[str]
    raw_str: str = mapped_column(String)  # type: ignore[attr-defined]


class GenericMappedTestModel(Base):
    """Define model for testing generic types mapped to JSON columns."""

    __tablename__ = "generic_mapped_test"
    id: Mapped[int] = mapped_column(primary_key=True)
    list_of_strings: Mapped[list[str] | None] = mapped_column(JSON)
    dict_of_int: Mapped[dict[str, int] | None] = mapped_column(JSON)


class UnionLiteralTestModel(Base):
    """Define model for testing union and literal types."""

    __tablename__ = "union_literal_test"
    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String)
    value: Mapped[int] = mapped_column(Integer)


class SQLiteSpecificTypesModel(Base):
    """Define model for testing SQLite-specific type handling."""

    __tablename__ = "sqlite_types_model_test"
    id: Mapped[int] = mapped_column(primary_key=True)
    # SQLite stores booleans as INTEGER (0 or 1)
    boolean_as_int: Mapped[bool] = mapped_column(Integer)
    # SQLite stores dates/times as TEXT
    date_as_text: Mapped[datetime.date] = mapped_column(String)
    time_as_text: Mapped[datetime.time] = mapped_column(String)
    datetime_as_text: Mapped[datetime.datetime] = mapped_column(String)


class MyEnum(enum.Enum):
    """Define example Enum for database type testing."""

    ONE = "one"
    TWO = "two"


class PostgresSpecificTypesModel(PostgresBase):
    """Define model for testing PostgreSQL-specific type handling."""

    __tablename__ = "postgres_specific_types"
    id: Mapped[int] = mapped_column(primary_key=True)
    uuid_field: Mapped[uuid.UUID] = mapped_column(postgresql.UUID(as_uuid=True))
    jsonb_field: Mapped[dict] = mapped_column(postgresql.JSONB)
    array_field: Mapped[list[str]] = mapped_column(postgresql.ARRAY(String))
    enum_field: Mapped[MyEnum] = mapped_column(postgresql.ENUM(MyEnum))


class MySQLEnum(enum.Enum):
    """Define example Enum for MySQL database type testing."""

    OPTION_A = "A"
    OPTION_B = "B"


class MySQLSpecificTypesModel(MySQLBase):
    """Define model for testing MySQL-specific type handling."""

    __tablename__ = "mysql_specific_types"
    id: Mapped[int] = mapped_column(primary_key=True)
    year_field: Mapped[int] = mapped_column(mysql.YEAR)
    set_field: Mapped[str] = mapped_column(mysql.SET("val1", "val2"))
    enum_field: Mapped[MySQLEnum] = mapped_column(mysql.ENUM(MySQLEnum))


class ConcreteTableBase(Base):
    """Define base model for concrete table inheritance."""

    __tablename__ = "concrete_table_base"
    id: Mapped[int] = mapped_column(primary_key=True)
    base_data: Mapped[str]


class ConcreteTableChild(ConcreteTableBase):
    """Define child model for concrete table inheritance."""

    __tablename__ = "concrete_table_child"
    id: Mapped[int] = mapped_column(ForeignKey("concrete_table_base.id"), primary_key=True)
    child_data: Mapped[str]


# Many-to-Many Relationship (Association Table)
association_table = Table(
    "association",
    Base.metadata,
    Column("left_id", ForeignKey("left_table.id"), primary_key=True),
    Column("right_id", ForeignKey("right_table.id"), primary_key=True),
)


class Left(Base):
    """Define model for the left side of a many-to-many relationship."""

    __tablename__ = "left_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    rights: Mapped[list["Right"]] = relationship(secondary=association_table, back_populates="lefts")


class Right(Base):
    """Define model for the right side of a many-to-many relationship."""

    __tablename__ = "right_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    lefts: Mapped[list["Left"]] = relationship(secondary=association_table, back_populates="rights")


# Many-to-Many Relationship (Association Object / Through Model)
class ThroughModel(Base):
    """Define association model for a many-to-many relationship with extra data."""

    __tablename__ = "through_table"
    left_id: Mapped[int] = mapped_column(ForeignKey("left_through_table.id"), primary_key=True)
    right_id: Mapped[int] = mapped_column(ForeignKey("right_through_table.id"), primary_key=True)
    extra_data: Mapped[str]

    left: Mapped["LeftThrough"] = relationship(back_populates="right_associations")
    right: Mapped["RightThrough"] = relationship(back_populates="left_associations")


class LeftThrough(Base):
    """Define left model for a many-to-many relationship with an association object."""

    __tablename__ = "left_through_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    right_associations: Mapped[list["ThroughModel"]] = relationship(back_populates="left", overlaps="rights")
    rights: Mapped[list["RightThrough"]] = relationship(
        secondary="through_table",
        back_populates="lefts",
        overlaps="left_associations,right,left",
    )


class RightThrough(Base):
    """Define right model for a many-to-many relationship with an association object."""

    __tablename__ = "right_through_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    left_associations: Mapped[list["ThroughModel"]] = relationship(back_populates="right", overlaps="lefts")
    lefts: Mapped[list["LeftThrough"]] = relationship(
        secondary="through_table",
        back_populates="rights",
        overlaps="left_associations,right,left,right_associations",
    )
