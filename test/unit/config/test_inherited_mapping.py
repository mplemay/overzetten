import pytest
from pydantic import EmailStr

from overzetten import DTO, DTOConfig
from test.fixtures.sqlalchemy_models import BaseMappedModel, ChildMappedModel


def test_mapping_with_inheritance(db_engine):
    """Test that mapped configurations are correctly applied with inheritance."""

    class BaseMappedDTO(DTO[BaseMappedModel]):
        config = DTOConfig(
            mapped={BaseMappedModel.base_field: EmailStr}
        )

    class ChildMappedDTO(DTO[ChildMappedModel]):
        config = DTOConfig(
            mapped={ChildMappedModel.child_field: str}
        )

    # Test base DTO
    base_fields = BaseMappedDTO.model_fields
    assert base_fields["base_field"].annotation == EmailStr
    assert base_fields["common_field"].annotation == str

    # Test child DTO
    child_fields = ChildMappedDTO.model_fields
    assert child_fields["child_field"].annotation == str
    assert child_fields["common_field"].annotation == str
    assert child_fields["base_field"].annotation == str # base_field is not inherited as EmailStr, it's its original type
