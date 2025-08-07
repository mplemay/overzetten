import pytest

from overzetten import DTO, DTOConfig
from test.fixtures.sqlalchemy_models import User


def test_field_exclusion(db_engine):
    """Test excluding various field types."""

    class UserExcludedDTO(DTO[User]):
        config = DTOConfig(exclude={User.id, User.is_active})

    fields = UserExcludedDTO.model_fields

    assert "id" not in fields
    assert "is_active" not in fields
    assert "name" in fields
    assert "age" in fields


def test_exclude_all_fields_except_one(db_engine):
    """Test excluding all fields except one (edge case)."""

    class UserMinimalDTO(DTO[User]):
        config = DTOConfig(
            exclude={
                User.id,
                User.fullname,
                User.age,
                User.is_active,
                User.created_at,
                User.registered_on,
                User.last_login,
                User.balance,
                User.rating,
                User.data,
                User.preferences,
                User.tags,
                User.uuid_field,
                User.secret_field,
                User.json_field,
            }
        )

    fields = UserMinimalDTO.model_fields

    assert list(fields.keys()) == ["name"]


def test_exclude_overrides_mapped(db_engine):
    """Test that exclude takes precedence over mapped."""

    class ExcludeMappedDTO(DTO[User]):
        config = DTOConfig(
            exclude={User.name},
            mapped={User.name: str}  # This should be ignored
        )

    fields = ExcludeMappedDTO.model_fields
    assert "name" not in fields