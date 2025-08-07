
import pytest

from overzetten import DTO, DTOConfig
from test.fixtures.sqlalchemy_models import User


def test_field_exclusion():
    """Test excluding various field types."""

    class UserExcludedDTO(DTO[User]):
        config = DTOConfig(exclude={User.id, User.is_active})

    fields = UserExcludedDTO.model_fields

    assert "id" not in fields
    assert "is_active" not in fields
    assert "name" in fields
    assert "age" in fields


def test_exclude_all_fields_except_one():
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
            }
        )

    fields = UserMinimalDTO.model_fields

    assert list(fields.keys()) == ["name"]
