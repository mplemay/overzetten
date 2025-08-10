from typing import Optional

from pydantic import EmailStr

from overzetten import DTO, DTOConfig
from overzetten.__tests__.fixtures.models import NullableTestModel, ServerNullableTestModel


def test_server_side_nullable_handling():
    """Test handling of server-side nullable fields."""

    class ServerNullableDTO(DTO[ServerNullableTestModel]):
        pass

    fields = ServerNullableDTO.model_fields

    # Field is nullable in DB and has server_default, should be Optional[str] with default None
    assert fields["server_nullable_field"].annotation is Optional[str]
    assert fields["server_nullable_field"].default is None

    # Field is not nullable in DB but has server_default, should be str with default None
    assert fields["server_not_nullable_field"].annotation is str
    assert fields["server_not_nullable_field"].default is None


def test_nullable_field_handling():
    """Test that nullable fields become Optional[T] correctly."""

    class NullableTestDTO(DTO[NullableTestModel]):
        pass

    fields = NullableTestDTO.model_fields

    assert fields["required_field"].annotation is str
    assert fields["nullable_field"].annotation is Optional[str]
    assert fields["already_optional_field"].annotation is Optional[int]


def test_no_double_optional_wrapping():
    """Test that Optional[T] fields aren't double-wrapped."""

    class NullableTestDTO(DTO[NullableTestModel]):
        pass

    fields = NullableTestDTO.model_fields
    # The type should be Optional[int], not Optional[Optional[int]]
    assert fields["already_optional_field"].annotation is Optional[int]
    assert str(fields["already_optional_field"].annotation).startswith(
        "typing.Optional[int",
    )


def test_nullable_field_with_custom_type_mapping():
    """Test nullable fields with custom type mappings (nullable + EmailStr -> Optional[EmailStr])."""

    class NullableEmailDTO(DTO[NullableTestModel]):
        config = DTOConfig(mapped={NullableTestModel.nullable_email: EmailStr})

    fields = NullableEmailDTO.model_fields
    assert fields["nullable_email"].annotation is Optional[EmailStr]
