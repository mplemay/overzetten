from pydantic import EmailStr
from typing import List

from overzetten import DTO, DTOConfig
from overzetten.__tests__.fixtures.models import User, Address, BaseMappedModel, ChildMappedModel


def test_field_inclusion():
    """Test including only a specific subset of fields."""

    class UserIncludedDTO(DTO[User]):
        config = DTOConfig(include={User.name, User.age})

    fields = UserIncludedDTO.model_fields
    assert list(fields.keys()) == ["name", "age"]
    assert "id" not in fields
    assert "is_active" not in fields


def test_exclude_overrides_include():
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


def test_empty_include_set():
    """Test that an empty include set results in no fields."""

    class UserEmptyIncludeDTO(DTO[User]):
        config = DTOConfig(include=set())

    fields = UserEmptyIncludeDTO.model_fields
    assert list(fields.keys()) == []


def test_include_with_mapped():
    """Test combining include and mapped configurations."""

    class UserIncludeMappedDTO(DTO[User]):
        config = DTOConfig(
            include={User.name, User.age},
            mapped={User.name: EmailStr},
        )

    fields = UserIncludeMappedDTO.model_fields
    assert list(fields.keys()) == ["name", "age"]
    assert fields["name"].annotation is EmailStr
    assert fields["age"].annotation is int


def test_include_relationships_vs_columns():
    """Test including relationships vs columns."""

    class AddressDTO(DTO[Address]):
        config = DTOConfig(include={Address.email_address})

    class UserWithAddressesIncludedDTO(DTO[User]):
        config = DTOConfig(
            include={User.name, User.addresses},
            include_relationships=True,
            mapped={User.addresses: List[AddressDTO]}
        )

    fields = UserWithAddressesIncludedDTO.model_fields
    assert list(fields.keys()) == ["name", "addresses"]
    assert fields["name"].annotation is str
    assert fields["addresses"].annotation is List[AddressDTO]


def test_include_inherited_fields_selectively():
    """Test including inherited fields selectively."""

    class ChildMappedIncludedDTO(DTO[ChildMappedModel]):
        config = DTOConfig(
            include={ChildMappedModel.id, ChildMappedModel.child_field, ChildMappedModel.common_field}
        )

    fields = ChildMappedIncludedDTO.model_fields
    assert set(fields.keys()) == {"id", "child_field", "common_field"}
    assert fields["id"].annotation is int
    assert fields["child_field"].annotation is str
    assert fields["common_field"].annotation is str

    class BaseMappedIncludedDTO(DTO[BaseMappedModel]):
        config = DTOConfig(
            include={BaseMappedModel.id, BaseMappedModel.base_field}
        )

    fields = BaseMappedIncludedDTO.model_fields
    assert list(fields.keys()) == ["id", "base_field"]
    assert fields["id"].annotation is int
    assert fields["base_field"].annotation is str