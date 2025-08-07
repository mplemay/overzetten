
import pytest
from typing import Optional

from overzetten import DTO
from test.fixtures.sqlalchemy_models import NullableTestModel


def test_nullable_field_handling():
    """Test that nullable fields become Optional[T] correctly."""

    class NullableTestDTO(DTO[NullableTestModel]):
        pass

    fields = NullableTestDTO.model_fields

    assert fields["required_field"].annotation == str
    assert fields["nullable_field"].annotation == Optional[str]
    assert fields["already_optional_field"].annotation == Optional[int]
