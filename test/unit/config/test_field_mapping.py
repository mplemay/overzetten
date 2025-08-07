
import pytest
from pydantic import EmailStr, HttpUrl, UUID4, Json, SecretStr, Field
from typing import List, Dict, Union, Literal, Optional

from overzetten import DTO, DTOConfig
from test.fixtures.sqlalchemy_models import User


def test_field_mapping_to_pydantic_types():
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


def test_field_mapping_with_field_constraints():
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
