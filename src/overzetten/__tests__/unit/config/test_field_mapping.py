from typing import Annotated, Literal, Optional

import pytest
from pydantic import UUID4, BaseModel, EmailStr, Field, HttpUrl, Json, SecretStr
from sqlalchemy.orm.attributes import InstrumentedAttribute

from overzetten import DTO, DTOConfig
from overzetten.__tests__.fixtures.models import UnionLiteralTestModel, User


def test_field_mapping_to_pydantic_types():
    """Test mapping to various Pydantic-specific types."""

    class UserMappedDTO(DTO[User]):
        config = DTOConfig(
            mapped={
                User.name: EmailStr,
                User.fullname: HttpUrl,
            },
        )

    fields = UserMappedDTO.model_fields
    assert fields["name"].annotation is EmailStr
    assert fields["fullname"].annotation is Optional[HttpUrl]


def test_field_mapping_with_field_constraints():
    """Test mapping to Pydantic Field with constraints."""

    class UserConstrainedDTO(DTO[User]):
        config = DTOConfig(
            mapped={
                User.name: Field(min_length=3, max_length=50),
            },
        )

    fields = UserConstrainedDTO.model_fields
    # Check that the metadata contains the constraints from the Field object.
    # We iterate through the metadata to find the respective constraint objects.
    assert any(getattr(m, "min_length", None) == 3 for m in fields["name"].metadata)
    assert any(getattr(m, "max_length", None) == 50 for m in fields["name"].metadata)


def test_field_mapping_to_complex_types():
    """Test mapping to complex types like List and Dict."""

    class UserComplexMapDTO(DTO[User]):
        config = DTOConfig(
            mapped={
                User.preferences: dict[str, int | str],
                User.tags: list[str],
            },
        )

    fields = UserComplexMapDTO.model_fields
    assert fields["preferences"].annotation is Optional[dict[str, int | str]]
    assert fields["tags"].annotation is Optional[list[str]]


def test_field_mapping_to_specific_pydantic_types():
    """Test mapping to UUID4, Json, and SecretStr."""

    class UserSpecificMappedDTO(DTO[User]):
        config = DTOConfig(
            mapped={
                User.uuid_field: UUID4,
                User.secret_field: SecretStr,
                User.json_field: Json,
            },
        )

    fields = UserSpecificMappedDTO.model_fields
    assert fields["uuid_field"].annotation == Optional[UUID4]
    assert fields["secret_field"].annotation is Optional[SecretStr]
    assert fields["json_field"].annotation is Optional[Json]


def test_field_mapping_to_union_literal_and_custom_pydantic_models():
    """Test mapping to Union, Literal, and custom Pydantic models."""

    class CustomPydanticModel(BaseModel):
        value: int

    class UnionLiteralMappedDTO(DTO[UnionLiteralTestModel]):
        config = DTOConfig(
            mapped={
                UnionLiteralTestModel.status: Literal["active", "inactive"],
                UnionLiteralTestModel.value: CustomPydanticModel,
            },
        )

    fields = UnionLiteralMappedDTO.model_fields
    assert fields["status"].annotation is Literal["active", "inactive"]
    assert fields["value"].annotation is CustomPydanticModel


def test_mapping_same_field_to_different_types():
    """Test mapping the same SQLAlchemy field to different Pydantic types in different DTOs."""

    class UserDTOMappedNameStr(DTO[User]):
        config = DTOConfig(mapped={User.name: str})

    class UserDTOMappedNameEmail(DTO[User]):
        config = DTOConfig(mapped={User.name: EmailStr})

    # Verify the name field in the first DTO
    assert UserDTOMappedNameStr.model_fields["name"].annotation is str

    # Verify the name field in the second DTO
    assert UserDTOMappedNameEmail.model_fields["name"].annotation is EmailStr


def test_mapping_non_existent_field_errors():
    """Test that mapping a non-existent SQLAlchemy field raises an error."""

    # Create a dummy InstrumentedAttribute that doesn't exist on the User model
    class NonExistentAttr(InstrumentedAttribute):
        def __init__(self, key):
            self.key = key

    non_existent_field = NonExistentAttr("non_existent_field")

    with pytest.raises(ValueError) as excinfo:

        class UserDTOWithNonExistentMapping(DTO[User]):
            config = DTOConfig(mapped={non_existent_field: str})

    assert "Mapped attribute 'non_existent_field' does not exist on SQLAlchemy model 'User'." in str(excinfo.value)


def test_annotated_types_with_metadata():
    """Test mapping to Annotated types with metadata."""

    class UserAnnotatedDTO(DTO[User]):
        config = DTOConfig(
            mapped={User.name: Annotated[str, Field(min_length=5, max_length=10)]},
        )

    fields = UserAnnotatedDTO.model_fields
    assert fields["name"].annotation is str
    assert any(hasattr(m, "min_length") and m.min_length == 5 for m in fields["name"].metadata)
    assert any(hasattr(m, "max_length") and m.max_length == 10 for m in fields["name"].metadata)
