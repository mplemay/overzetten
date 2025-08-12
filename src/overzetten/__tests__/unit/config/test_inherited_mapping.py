"""Tests for inherited field mapping in DTO generation."""

from pydantic import EmailStr

from overzetten import DTO, DTOConfig
from overzetten.__tests__.fixtures.models import (
    BaseMappedModel,
    ChildMappedModel,
)


def test_mapping_with_inheritance() -> None:
    """Test that mapped configurations are correctly applied with inheritance."""

    class BaseMappedDTO(DTO[BaseMappedModel]):
        config = DTOConfig(mapped={BaseMappedModel.base_field: EmailStr})

    class ChildMappedDTO(DTO[ChildMappedModel]):
        config = DTOConfig(mapped={ChildMappedModel.child_field: str})

    # Test base DTO
    base_fields = BaseMappedDTO.model_fields
    assert base_fields["base_field"].annotation is EmailStr
    assert base_fields["common_field"].annotation is str

    # Test child DTO
    child_fields = ChildMappedDTO.model_fields
    assert child_fields["child_field"].annotation is str
    assert child_fields["common_field"].annotation is str
    assert (
        child_fields["base_field"].annotation is str
    )  # base_field is not inherited as EmailStr, it's its original type
