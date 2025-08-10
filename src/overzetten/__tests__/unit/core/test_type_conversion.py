import datetime
import uuid
from decimal import Decimal
from typing import Any, Optional

from overzetten import DTO
from overzetten.__tests__.fixtures.models import (
    CustomTypeModel,
    GenericMappedTestModel,
    MappedAnnotationTestModel,
    MyEnum,
    MySQLEnum,
    MySQLSpecificTypesModel,
    NoPythonTypeModel,
    PostgresSpecificTypesModel,
    SQLiteSpecificTypesModel,
    TypeConversionTestModel,
)


def test_no_python_type_conversion():
    """Test handling of SQLAlchemy types that don't have a python_type defined."""

    class NoPythonTypeDTO(DTO[NoPythonTypeModel]):
        pass

    fields = NoPythonTypeDTO.model_fields
    assert fields["no_python_field"].annotation is Any


def test_type_conversion():
    """Test conversion of all basic SQLAlchemy types."""

    class TypeConversionTestDTO(DTO[TypeConversionTestModel]):
        pass

    fields = TypeConversionTestDTO.model_fields

    assert fields["string_field"].annotation is str
    assert fields["integer_field"].annotation is int
    assert fields["boolean_field"].annotation is bool
    assert fields["datetime_field"].annotation is datetime.datetime
    assert fields["date_field"].annotation is datetime.date
    assert fields["time_field"].annotation is datetime.time
    assert fields["text_field"].annotation is str
    assert fields["float_field"].annotation is float
    assert fields["numeric_field"].annotation is Decimal
    assert fields["large_binary_field"].annotation is bytes


def test_custom_sqlalchemy_type():
    """Test a custom SQLAlchemy type with python_type property."""

    class CustomTypeDTO(DTO[CustomTypeModel]):
        pass

    fields = CustomTypeDTO.model_fields
    assert fields["custom_field"].annotation is int


def test_mapped_annotations_vs_raw_column_types():
    """Test handling of Mapped[T] annotations vs raw column types."""

    class MappedAnnotationDTO(DTO[MappedAnnotationTestModel]):
        pass

    fields = MappedAnnotationDTO.model_fields
    assert fields["mapped_str"].annotation is str
    assert fields["raw_str"].annotation is str


def test_generic_type_conversion():
    """Test type conversion with generic types (Mapped[List[str]], Mapped[Dict[str, int]])."""

    class GenericMappedDTO(DTO[GenericMappedTestModel]):
        pass

    fields = GenericMappedDTO.model_fields
    assert fields["list_of_strings"].annotation is Optional[list[str]]
    assert fields["dict_of_int"].annotation is Optional[dict[str, int]]


def test_postgresql_specific_types():
    """Test PostgreSQL-specific types (UUID, JSONB, ARRAY, ENUM)."""

    class PostgresSpecificTypesDTO(DTO[PostgresSpecificTypesModel]):
        pass

    fields = PostgresSpecificTypesDTO.model_fields
    assert fields["uuid_field"].annotation is uuid.UUID
    assert fields["jsonb_field"].annotation is dict
    assert fields["array_field"].annotation is list[str]
    assert fields["enum_field"].annotation is MyEnum


def test_mysql_specific_types():
    """Test MySQL-specific types (YEAR, SET, ENUM variations)."""

    class MySQLSpecificTypesDTO(DTO[MySQLSpecificTypesModel]):
        pass

    fields = MySQLSpecificTypesDTO.model_fields
    assert fields["year_field"].annotation is int
    assert fields["set_field"].annotation is str
    assert fields["enum_field"].annotation is MySQLEnum


def test_sqlite_specific_types():
    """Test SQLite-specific types (boolean as int, date/time as text)."""

    class SQLiteSpecificTypesDTO(DTO[SQLiteSpecificTypesModel]):
        pass

    fields = SQLiteSpecificTypesDTO.model_fields
    assert fields["boolean_as_int"].annotation is bool
    assert fields["date_as_text"].annotation is datetime.date
    assert fields["time_as_text"].annotation is datetime.time
    assert fields["datetime_as_text"].annotation is datetime.datetime
