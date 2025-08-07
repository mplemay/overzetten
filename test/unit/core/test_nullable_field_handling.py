
import pytest
from typing import Optional
from pydantic import EmailStr

from overzetten import DTO, DTOConfig
from test.fixtures.sqlalchemy_models import NullableTestModel


def test_nullable_field_handling(db_engine):
    """Test that nullable fields become Optional[T] correctly."""

    class NullableTestDTO(DTO[NullableTestModel]):
        pass

    fields = NullableTestDTO.model_fields

    assert fields["required_field"].annotation == str
    assert fields["nullable_field"].annotation == Optional[str]
    assert fields["already_optional_field"].annotation == Optional[int]


def test_no_double_optional_wrapping(db_engine):
    """Test that Optional[T] fields aren't double-wrapped."""

    class NullableTestDTO(DTO[NullableTestModel]):
        pass

    fields = NullableTestDTO.model_fields
    # The type should be Optional[int], not Optional[Optional[int]]
    assert fields["already_optional_field"].annotation == Optional[int]
    assert str(fields["already_optional_field"].annotation).startswith("typing.Optional[int")


def test_nullable_field_with_custom_type_mapping(db_engine):
    """Test nullable fields with custom type mappings (nullable + EmailStr -> Optional[EmailStr])."""

    class NullableEmailDTO(DTO[NullableTestModel]):
        config = DTOConfig(
            mapped={NullableTestModel.nullable_email: EmailStr}
        )

    fields = NullableEmailDTO.model_fields
    assert fields["nullable_email"].annotation == Optional[EmailStr]
