
from sqlalchemy import (
    create_engine,
    String,
    Integer,
    Boolean,
    DateTime,
    Date,
    Time,
    Float,
    Numeric,
    LargeBinary,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List
import datetime
from decimal import Decimal
from sqlalchemy import ForeignKey


class Base(DeclarativeBase):
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
    addresses: Mapped[List["Address"]] = relationship(back_populates="user")


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


class DefaultValueTestModel(Base):
    __tablename__ = "default_value_test"

    id: Mapped[int] = mapped_column(primary_key=True)
    scalar_default: Mapped[str] = mapped_column(default="default_value")
    callable_default: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    required_field: Mapped[str]


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


engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
