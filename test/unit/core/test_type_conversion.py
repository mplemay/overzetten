
import pytest
from pydantic import BaseModel
from typing import Optional
import datetime
from decimal import Decimal

from overzetten import DTO
from test.fixtures.sqlalchemy_models import TypeConversionTestModel


def test_type_conversion():
    """Test conversion of all basic SQLAlchemy types."""

    class TypeConversionTestDTO(DTO[TypeConversionTestModel]):
        pass

    fields = TypeConversionTestDTO.model_fields

    assert fields["string_field"].annotation == str
    assert fields["integer_field"].annotation == int
    assert fields["boolean_field"].annotation == bool
    assert fields["datetime_field"].annotation == datetime.datetime
    assert fields["date_field"].annotation == datetime.date
    assert fields["time_field"].annotation == datetime.time
    assert fields["text_field"].annotation == str
    assert fields["float_field"].annotation == float
    assert fields["numeric_field"].annotation == Decimal
    assert fields["large_binary_field"].annotation == bytes
