
import pytest
from pydantic import EmailStr

from overzetten import DTO, DTOConfig
from test.fixtures.sqlalchemy_models import User


def test_field_inclusion(db_engine):
    """Test including only a specific subset of fields."""

    class UserIncludedDTO(DTO[User]):
        config = DTOConfig(include={User.name, User.age})

    fields = UserIncludedDTO.model_fields
    assert list(fields.keys()) == ["name", "age"]
    assert "id" not in fields
    assert "is_active" not in fields


def test_exclude_overrides_include(db_engine):
    """Test that exclude takes precedence over include."""

    class UserIncludeExcludeDTO(DTO[User]):
        config = DTOConfig(
            include={User.name, User.age, User.id},
            exclude={User.id, User.age},
        )

    fields = UserIncludeExcludeDTO.model_fields
    assert list(fields.keys()) == ["name"]
    assert "id" not in fields
    assert "age" not in fields


def test_empty_include_set(db_engine):
    """Test that an empty include set results in no fields."""

    class UserEmptyIncludeDTO(DTO[User]):
        config = DTOConfig(include=set())

    fields = UserEmptyIncludeDTO.model_fields
    assert list(fields.keys()) == []


def test_include_with_mapped(db_engine):
    """Test combining include and mapped configurations."""

    class UserIncludeMappedDTO(DTO[User]):
        config = DTOConfig(
            include={User.name, User.age},
            mapped={User.name: EmailStr},
        )

    fields = UserIncludeMappedDTO.model_fields
    assert list(fields.keys()) == ["name", "age"]
    assert fields["name"].annotation == EmailStr
    assert fields["age"].annotation == int
