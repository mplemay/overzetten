
import pytest
from pydantic import EmailStr, HttpUrl, UUID4, Json, SecretStr, Field, BaseModel
from typing import List, Dict, Union, Literal, Optional

from overzetten import DTO, DTOConfig
from test.fixtures.sqlalchemy_models import User, UnionLiteralTestModel


def test_field_mapping_to_pydantic_types(db_engine):
    """Test mapping to various Pydantic-specific types."""

    class UserMappedDTO(DTO[User]):
        config = DTOConfig(
            mapped={
                User.name: EmailStr,
                User.fullname: HttpUrl,
            }
        )

    fields = UserMappedDTO.model_fields
    assert fields["name"].annotation == EmailStr
    assert fields["fullname"].annotation == Optional[HttpUrl]


def test_field_mapping_with_field_constraints(db_engine):
    """Test mapping to Pydantic Field with constraints."""

    class UserConstrainedDTO(DTO[User]):
        config = DTOConfig(
            mapped={
                User.name: Field(min_length=3, max_length=50),
            }
        )

    fields = UserConstrainedDTO.model_fields
    # Check that the metadata contains the constraints from the Field object.
    # We iterate through the metadata to find the respective constraint objects.
    assert any(getattr(m, 'min_length', None) == 3 for m in fields["name"].metadata)
    assert any(getattr(m, 'max_length', None) == 50 for m in fields["name"].metadata)


def test_field_mapping_to_complex_types(db_engine):
    """Test mapping to complex types like List and Dict."""

    class UserComplexMapDTO(DTO[User]):
        config = DTOConfig(
            mapped={
                User.preferences: Dict[str, Union[int, str]],
                User.tags: List[str],
            }
        )

    fields = UserComplexMapDTO.model_fields
    assert fields["preferences"].annotation == Optional[Dict[str, Union[int, str]]]
    assert fields["tags"].annotation == Optional[List[str]]


def test_field_mapping_to_specific_pydantic_types(db_engine):
    """Test mapping to UUID4, Json, and SecretStr."""

    class UserSpecificMappedDTO(DTO[User]):
        config = DTOConfig(
            mapped={
                User.uuid_field: UUID4,
                User.secret_field: SecretStr,
                User.json_field: Json,
            }
        )

    fields = UserSpecificMappedDTO.model_fields
    assert fields["uuid_field"].annotation == Optional[UUID4]
    assert fields["secret_field"].annotation == Optional[SecretStr]
    assert fields["json_field"].annotation == Optional[Json]


def test_field_mapping_to_union_literal_and_custom_pydantic_models(db_engine):
    """Test mapping to Union, Literal, and custom Pydantic models."""

    class CustomPydanticModel(BaseModel):
        value: int

    class UnionLiteralMappedDTO(DTO[UnionLiteralTestModel]):
        config = DTOConfig(
            mapped={
                UnionLiteralTestModel.status: Union[Literal["active"], Literal["inactive"]],
                UnionLiteralTestModel.value: CustomPydanticModel,
            }
        )

    fields = UnionLiteralMappedDTO.model_fields
    assert fields["status"].annotation == Union[Literal["active"], Literal["inactive"]]
    assert fields["value"].annotation == CustomPydanticModel
