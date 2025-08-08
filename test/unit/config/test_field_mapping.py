import pytest
from pydantic import EmailStr, HttpUrl, UUID4, Json, SecretStr, Field, BaseModel
from pydantic.fields import FieldInfo
from typing import List, Dict, Union, Literal, Optional, Annotated
import uuid

from overzetten import DTO, DTOConfig
from test.fixtures.sqlalchemy_models import User, UnionLiteralTestModel
from sqlalchemy.orm.attributes import InstrumentedAttribute


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
    assert fields["uuid_field"].annotation == Optional[uuid.UUID]
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


def test_mapping_same_field_to_different_types(db_engine):
    """Test mapping the same SQLAlchemy field to different Pydantic types in different DTOs."""

    class UserDTOMappedNameStr(DTO[User]):
        config = DTOConfig(
            mapped={User.name: str}
        )

    class UserDTOMappedNameEmail(DTO[User]):
        config = DTOConfig(
            mapped={User.name: EmailStr}
        )

    # Verify the name field in the first DTO
    assert UserDTOMappedNameStr.model_fields["name"].annotation == str

    # Verify the name field in the second DTO
    assert UserDTOMappedNameEmail.model_fields["name"].annotation == EmailStr


def test_mapping_non_existent_field_errors(db_engine):
    """Test that mapping a non-existent SQLAlchemy field raises an error."""
    # Create a dummy InstrumentedAttribute that doesn't exist on the User model
    class NonExistentAttr(InstrumentedAttribute):
        def __init__(self, key):
            self.key = key

    non_existent_field = NonExistentAttr("non_existent_field")

    with pytest.raises(ValueError) as excinfo:
        class UserDTOWithNonExistentMapping(DTO[User]):
            config = DTOConfig(
                mapped={non_existent_field: str}
            )
    assert "Mapped attribute 'non_existent_field' does not exist on SQLAlchemy model 'User'." in str(excinfo.value)


def test_annotated_types_with_metadata(db_engine):
    """Test mapping to Annotated types with metadata."""

    class UserAnnotatedDTO(DTO[User]):
        config = DTOConfig(
            mapped={User.name: Annotated[str, Field(min_length=5, max_length=10)]}
        )

    fields = UserAnnotatedDTO.model_fields
    assert fields["name"].annotation == str
    assert any(isinstance(m, FieldInfo) and getattr(m, 'min_length', None) == 5 for m in fields["name"].metadata)
    assert any(isinstance(m, FieldInfo) and getattr(m, 'max_length', None) == 10 for m in fields["name"].metadata)