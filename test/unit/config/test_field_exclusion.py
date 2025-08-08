from overzetten import DTO, DTOConfig
from fixtures.sqlalchemy_models import User, ChildMappedModel, Address


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
            mapped={User.name: str},  # This should be ignored
        )

    fields = ExcludeMappedDTO.model_fields
    assert "name" not in fields


def test_exclude_inherited_field(db_engine):
    """Test excluding a field inherited from a parent model."""

    class ChildMappedExcludedDTO(DTO[ChildMappedModel]):
        config = DTOConfig(exclude={ChildMappedModel.base_field})

    fields = ChildMappedExcludedDTO.model_fields

    assert "base_field" not in fields
    assert "child_field" in fields
    assert "common_field" in fields


def test_exclude_foreign_key_field(db_engine):
    """Test excluding a foreign key field."""

    class AddressExcludedDTO(DTO[Address]):
        config = DTOConfig(exclude={Address.user_id})

    fields = AddressExcludedDTO.model_fields

    assert "user_id" not in fields
    assert "id" in fields
    assert "email_address" in fields


def test_exclude_hybrid_property(db_engine):
    """Test excluding a hybrid property."""

    class UserHybridExcludedDTO(DTO[User]):
        config = DTOConfig(exclude={User.full_name})

    fields = UserHybridExcludedDTO.model_fields

    assert "full_name" not in fields
    assert "name" in fields
