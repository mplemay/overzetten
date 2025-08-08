import datetime
import enum
import uuid
from decimal import Decimal
from typing import Any, Dict, List, Optional

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
    pass


class PostgresBase(DeclarativeBase):
    pass


class MySQLBase(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]
    age: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    registered_on: Mapped[datetime.date] = mapped_column(Date)
    last_login: Mapped[datetime.time] = mapped_column(Time)
    balance: Mapped[float] = mapped_column(Float)
    rating: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    data: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    preferences: Mapped[Optional[dict]] = mapped_column(JSON)
    tags: Mapped[Optional[list]] = mapped_column(JSON)
    uuid_field: Mapped[Optional[str]] = mapped_column(String(36))
    secret_field: Mapped[Optional[str]] = mapped_column(Text)
    json_field: Mapped[Optional[dict]] = mapped_column(JSON)
    addresses: Mapped[List["Address"]] = relationship(back_populates="user")

    @hybrid_property
    def full_name(self):
        if self.fullname:
            return f"{self.name} {self.fullname}"
        return self.name

    @full_name.expression
    def full_name(cls):
        return case((cls.fullname is not None, cls.name + " " + cls.fullname), else_=cls.name)


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship(back_populates="addresses")


class TypeConversionTestModel(Base):
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
    __tablename__ = "nullable_test"

    id: Mapped[int] = mapped_column(primary_key=True)
    required_field: Mapped[str]
    nullable_field: Mapped[Optional[str]]
    already_optional_field: Mapped[Optional[int]]
    nullable_email: Mapped[Optional[str]] = mapped_column(String)


class ServerNullableTestModel(Base):
    __tablename__ = "server_nullable_test"
    id: Mapped[int] = mapped_column(primary_key=True)
    # Nullable with a server default
    server_nullable_field: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, server_default="server_default_value"
    )
    # Not nullable with a server default
    server_not_nullable_field: Mapped[str] = mapped_column(String, server_default="another_server_default")


class DefaultValueTestModel(Base):
    __tablename__ = "default_value_test"

    id: Mapped[int] = mapped_column(primary_key=True)
    required_field: Mapped[str]
    server_default_field: Mapped[str] = mapped_column(server_default="server_default_value")
    scalar_default: Mapped[str] = mapped_column(default="default_value")
    callable_default: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)


class RequiredFieldTestModel(Base):
    __tablename__ = "required_field_test_model"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Not nullable, no default = required
    required_no_default: Mapped[str] = mapped_column(String)
    # Nullable, no default = Optional[T] with None default
    nullable_no_default: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    # Not nullable, has default = T with default
    required_with_default: Mapped[str] = mapped_column(String, default="default_value")
    # Nullable, has default = Optional[T] with default
    nullable_with_default: Mapped[Optional[str]] = mapped_column(String, nullable=True, default="nullable_default")
    # Not nullable, has server_default = T with default
    required_with_server_default: Mapped[str] = mapped_column(String, server_default="server_default_value")
    # Boolean field with default
    boolean_with_default: Mapped[bool] = mapped_column(Boolean, default=False)
    # Nullable, has server_default = Optional[T] with None default (from Pydantic perspective)
    nullable_with_server_default: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, server_default="nullable_server_default"
    )


class Node(Base):
    __tablename__ = "nodes"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    # Self-referential relationship
    parent_node_id: Mapped[Optional[int]] = mapped_column(ForeignKey("nodes.id"))
    parent_node: Mapped[Optional["Node"]] = relationship(back_populates="child_nodes", remote_side=[id])
    child_nodes: Mapped[List["Node"]] = relationship(back_populates="parent_node")


class BaseMappedModel(Base):
    __tablename__ = "base_mapped_model"
    id: Mapped[int] = mapped_column(primary_key=True)
    base_field: Mapped[str]
    common_field: Mapped[str]


class ChildMappedModel(BaseMappedModel):
    __tablename__ = "child_mapped_model"
    id: Mapped[int] = mapped_column(ForeignKey("base_mapped_model.id"), primary_key=True)
    child_field: Mapped[str]
    common_field: Mapped[str]


class TimestampMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now, onupdate=datetime.datetime.now)


class Product(TimestampMixin, Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[Optional[str]]


class AbstractBaseModel(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)
    abstract_field: Mapped[str]


class ConcreteModel(AbstractBaseModel):
    __tablename__ = "concrete_model"
    concrete_field: Mapped[str]


class Employee(Base):
    __tablename__ = "employee"
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str]

    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_identity": "employee",
    }


class Manager(Employee):
    __mapper_args__ = {
        "polymorphic_identity": "manager",
    }

    manager_data: Mapped[str]


class Engineer(Employee):
    __mapper_args__ = {
        "polymorphic_identity": "engineer",
    }

    engineer_info: Mapped[str]


# Custom Types (moved to appear before AdvancedDefaultTestModel)
class CustomInt(TypeDecorator):
    impl = Integer
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return value * 10 if value is not None else None

    def process_result_value(self, value, dialect):
        return value // 10 if value is not None else None

    @property
    def python_type(self):
        return int


class CustomTypeModel(Base):
    __tablename__ = "custom_type_test"
    id: Mapped[int] = mapped_column(primary_key=True)
    custom_field: Mapped[int] = mapped_column(CustomInt)


class NoPythonType(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        return value


class NoPythonTypeModel(Base):
    __tablename__ = "no_python_type_test"
    id: Mapped[int] = mapped_column(primary_key=True)
    no_python_field: Mapped[Any] = mapped_column(NoPythonType)


# AdvancedDefaultTestModel (now after CustomInt and CustomTypeModel)
class AdvancedDefaultTestModel(MappedAsDataclass, Base):
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
    __tablename__ = "mapped_annotation_test"
    __allow_unmapped__ = True
    id: Mapped[int] = mapped_column(primary_key=True)
    mapped_str: Mapped[str]
    raw_str: str = mapped_column(String)


class GenericMappedTestModel(Base):
    __tablename__ = "generic_mapped_test"
    id: Mapped[int] = mapped_column(primary_key=True)
    list_of_strings: Mapped[Optional[List[str]]] = mapped_column(JSON)
    dict_of_int: Mapped[Optional[Dict[str, int]]] = mapped_column(JSON)


class UnionLiteralTestModel(Base):
    __tablename__ = "union_literal_test"
    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String)
    value: Mapped[int] = mapped_column(Integer)


class SQLiteSpecificTypesModel(Base):
    __tablename__ = "sqlite_types_model_test"
    id: Mapped[int] = mapped_column(primary_key=True)
    # SQLite stores booleans as INTEGER (0 or 1)
    boolean_as_int: Mapped[bool] = mapped_column(Integer)
    # SQLite stores dates/times as TEXT
    date_as_text: Mapped[datetime.date] = mapped_column(String)
    time_as_text: Mapped[datetime.time] = mapped_column(String)
    datetime_as_text: Mapped[datetime.datetime] = mapped_column(String)


class MyEnum(enum.Enum):
    ONE = "one"
    TWO = "two"


class PostgresSpecificTypesModel(PostgresBase):
    __tablename__ = "postgres_specific_types"
    id: Mapped[int] = mapped_column(primary_key=True)
    uuid_field: Mapped[uuid.UUID] = mapped_column(postgresql.UUID(as_uuid=True))
    jsonb_field: Mapped[dict] = mapped_column(postgresql.JSONB)
    array_field: Mapped[List[str]] = mapped_column(postgresql.ARRAY(String))
    enum_field: Mapped[MyEnum] = mapped_column(postgresql.ENUM(MyEnum))


class MySQLEnum(enum.Enum):
    OPTION_A = "A"
    OPTION_B = "B"


class MySQLSpecificTypesModel(MySQLBase):
    __tablename__ = "mysql_specific_types"
    id: Mapped[int] = mapped_column(primary_key=True)
    year_field: Mapped[int] = mapped_column(mysql.YEAR)
    set_field: Mapped[str] = mapped_column(mysql.SET("val1", "val2"))
    enum_field: Mapped[MySQLEnum] = mapped_column(mysql.ENUM(MySQLEnum))


class ConcreteTableBase(Base):
    __tablename__ = "concrete_table_base"
    id: Mapped[int] = mapped_column(primary_key=True)
    base_data: Mapped[str]


class ConcreteTableChild(ConcreteTableBase):
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
    __tablename__ = "left_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    rights: Mapped[List["Right"]] = relationship(secondary=association_table, back_populates="lefts")


class Right(Base):
    __tablename__ = "right_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    lefts: Mapped[List["Left"]] = relationship(secondary=association_table, back_populates="rights")


# Many-to-Many Relationship (Association Object / Through Model)
class ThroughModel(Base):
    __tablename__ = "through_table"
    left_id: Mapped[int] = mapped_column(ForeignKey("left_through_table.id"), primary_key=True)
    right_id: Mapped[int] = mapped_column(ForeignKey("right_through_table.id"), primary_key=True)
    extra_data: Mapped[str]

    left: Mapped["LeftThrough"] = relationship(back_populates="right_associations")
    right: Mapped["RightThrough"] = relationship(back_populates="left_associations")


class LeftThrough(Base):
    __tablename__ = "left_through_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    right_associations: Mapped[List["ThroughModel"]] = relationship(back_populates="left")
    rights: Mapped[List["RightThrough"]] = relationship(secondary="through_table", back_populates="lefts")


class RightThrough(Base):
    __tablename__ = "right_through_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    left_associations: Mapped[List["ThroughModel"]] = relationship(back_populates="right")
    lefts: Mapped[List["LeftThrough"]] = relationship(secondary="through_table", back_populates="rights")
