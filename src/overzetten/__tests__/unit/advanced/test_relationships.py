"""Tests for relationship handling in DTO generation."""

from typing import Union, get_args, get_origin

import pytest
from pydantic import EmailStr, Field, ValidationError

from overzetten import DTO, DTOConfig
from overzetten.__tests__.fixtures.models import (
    Address,
    Left,
    LeftThrough,
    Right,
    RightThrough,
    ThroughModel,
    User,
)


def test_one_to_many_relationship() -> None:
    """Test one-to-many relationship handling."""

    class AddressDTO(DTO[Address]):
        config = DTOConfig(exclude={Address.user})

    class UserWithAddressesDTO(DTO[User]):
        config = DTOConfig(
            include_relationships=True,
            mapped={User.addresses: list[AddressDTO]},
        )

    # Test parent DTO with children collection
    user_fields = UserWithAddressesDTO.model_fields  # type: ignore[attr-defined]  # type: ignore[attr-defined]
    assert "addresses" in user_fields
    assert user_fields["addresses"].annotation == list[AddressDTO]

    # Test child DTO excluding parent reference
    address_fields = AddressDTO.model_fields  # type: ignore[attr-defined]
    assert "user" not in address_fields


def test_many_to_one_foreign_key_handling() -> None:
    """Test foreign key field handling in many-to-one relationships."""

    class AddressFKDTO(DTO[Address]):
        # By default, user_id (FK) should be included
        pass

    fields = AddressFKDTO.model_fields  # type: ignore[attr-defined]
    assert "user_id" in fields
    assert fields["user_id"].annotation == int | None


def test_many_to_one_relationship_object_inclusion() -> None:
    """Test relationship object inclusion in many-to-one relationships."""

    class AddressWithUserDTO(DTO[Address]):
        config = DTOConfig(
            include_relationships=True,
            mapped={Address.user: Field(default=None)},  # Mapped to provide a default
        )

    fields = AddressWithUserDTO.model_fields  # type: ignore[attr-defined]
    assert "user" in fields

    # The type should be an Optional union with the auto-generated UserDTO
    field_type = fields["user"].annotation
    origin = get_origin(field_type)
    # In Python 3.10+, the origin of `X | Y` is `types.UnionType`, not `typing.Union`
    assert origin in (Union, __import__("types").UnionType)

    # Check that one of the arguments in the Union is the generated DTO
    type_args = get_args(field_type)
    assert len(type_args) == 2
    assert type(None) in type_args

    # Find the DTO type in the Union arguments
    dto_type = next((t for t in type_args if t is not type(None)), None)
    assert dto_type is not None
    assert dto_type.__name__ == "UserDTO"

    # Check that the field is not required
    assert not fields["user"].is_required()


def test_many_to_many_association_table_handling() -> None:
    """Test many-to-many relationship handling with an association table."""

    class RightDTO(DTO[Right]):
        config = DTOConfig(exclude={Right.lefts})  # Exclude to avoid circular dependency

    class LeftDTO(DTO[Left]):
        config = DTOConfig(
            include_relationships=True,
            mapped={Left.rights: list[RightDTO]},
        )

    fields = LeftDTO.model_fields  # type: ignore[attr-defined]  # type: ignore[attr-defined]
    assert "rights" in fields
    assert fields["rights"].annotation == list[RightDTO]

    fields = RightDTO.model_fields  # type: ignore[attr-defined]  # type: ignore[attr-defined]
    assert "lefts" not in fields


def test_many_to_many_through_model_handling() -> None:
    """Test many-to-many relationship handling with a through model (association object)."""

    class ThroughModelDTO(DTO[ThroughModel]):
        config = DTOConfig(exclude={ThroughModel.left, ThroughModel.right})  # Exclude to avoid circular dependency

    class RightThroughDTO(DTO[RightThrough]):
        config = DTOConfig(
            exclude={RightThrough.lefts, RightThrough.left_associations},
        )  # Exclude to avoid circular dependency

    class LeftThroughDTO(DTO[LeftThrough]):
        config = DTOConfig(
            include_relationships=True,
            mapped={
                LeftThrough.rights: list[RightThroughDTO],
                LeftThrough.right_associations: list[ThroughModelDTO],
            },
        )

    fields = LeftThroughDTO.model_fields  # type: ignore[attr-defined]  # type: ignore[attr-defined]
    assert "rights" in fields
    assert fields["rights"].annotation == list[RightThroughDTO]
    assert "right_associations" in fields
    assert fields["right_associations"].annotation == list[ThroughModelDTO]

    fields = RightThroughDTO.model_fields  # type: ignore[attr-defined]  # type: ignore[attr-defined]
    assert "lefts" not in fields
    assert "left_associations" not in fields

    fields = ThroughModelDTO.model_fields  # type: ignore[attr-defined]  # type: ignore[attr-defined]
    assert "left" not in fields
    assert "right" not in fields


def test_back_populates_and_backref_handling() -> None:
    """Test that DTOs are correctly generated for models with back_populates/backref relationships."""

    class AddressDTO(DTO[Address]):
        config = DTOConfig(exclude={Address.user})  # Exclude to prevent recursion

    class UserDTO(DTO[User]):
        config = DTOConfig(
            include_relationships=True,
            mapped={User.addresses: list[AddressDTO]},
            include={User.id, User.name},  # Only include id and name for this test
        )

    # This test primarily ensures that the DTOs can be created without errors
    # when back_populates/backref are defined in the SQLAlchemy models.
    # The actual structure is tested by one_to_many_relationship test.
    user_data = {
        "id": 1,
        "name": "Test User",
    }
    user_dto = UserDTO.model_validate(user_data)  # type: ignore[attr-defined]
    assert user_dto.id == 1  # type: ignore[attr-defined]


def test_relationship_validation() -> None:
    """Test that Pydantic validates relationships based on the mapped DTO types."""

    class AddressDTO(DTO[Address]):
        config = DTOConfig(exclude={Address.user}, mapped={Address.email_address: EmailStr})  # Add EmailStr mapping

    class UserWithAddressesDTO(DTO[User]):
        config = DTOConfig(
            include_relationships=True,
            mapped={User.addresses: list[AddressDTO]},
        )

    # Valid data
    valid_user_data = {
        "id": 1,
        "name": "Test User",
        "age": 30,
        "is_active": True,
        "created_at": "2023-01-01T10:00:00",
        "registered_on": "2023-01-01",
        "last_login": "10:00:00",
        "balance": 100.0,
        "rating": 4.5,
        "addresses": [
            {"id": 1, "email_address": "test@example.com", "user_id": 1},
        ],
    }
    user_dto = UserWithAddressesDTO(**valid_user_data)
    assert user_dto.addresses[0].email_address == "test@example.com"  # type: ignore[attr-defined]

    # Invalid data (addresses is not a list of AddressDTO)
    invalid_user_data = {
        "id": 1,
        "name": "Test User",
        "age": 30,
        "is_active": True,
        "created_at": "2023-01-01T10:00:00",
        "registered_on": "2023-01-01",
        "last_login": "10:00:00",
        "balance": 100.0,
        "rating": 4.5,
        "addresses": "not a list",
    }
    with pytest.raises(ValidationError):
        UserWithAddressesDTO(**invalid_user_data)

    # Invalid data (addresses contains an invalid item)
    invalid_user_data_item = {
        "id": 1,
        "name": "Test User",
        "age": 30,
        "is_active": True,
        "created_at": "2023-01-01T10:00:00",
        "registered_on": "2023-01-01",
        "last_login": "10:00:00",
        "balance": 100.0,
        "rating": 4.5,
        "addresses": [
            {"id": 1, "email_address": "invalid-email", "user_id": 1},
        ],
    }
    with pytest.raises(ValidationError):
        UserWithAddressesDTO(**invalid_user_data_item)


def test_lazy_loading_behavior() -> None:
    """Test that lazy loading behavior is preserved."""

    class AddressDTO(DTO[Address]):
        config = DTOConfig(exclude={Address.user})

    class UserWithAddressesDTO(DTO[User]):
        config = DTOConfig(
            include_relationships=True,
            mapped={User.addresses: list[AddressDTO]},
        )

    # This test is conceptual and depends on the testing environment with a database.
    # It would involve creating a user with addresses, loading the user from the DB,
    # and then checking that the addresses are not loaded until accessed.
    # For now, we will just ensure the DTO is created correctly.
    assert "addresses" in UserWithAddressesDTO.model_fields  # type: ignore[attr-defined]


def test_cascade_option_preservation() -> None:
    """Test that cascade options are preserved."""

    class AddressDTO(DTO[Address]):
        config = DTOConfig(exclude={Address.user})

    class UserWithAddressesDTO(DTO[User]):
        config = DTOConfig(
            include_relationships=True,
            mapped={User.addresses: list[AddressDTO]},
        )

    # This test is conceptual and depends on the testing environment with a database.
    # It would involve checking the cascade options on the relationship.
    # For now, we will just ensure the DTO is created correctly.
    assert "addresses" in UserWithAddressesDTO.model_fields  # type: ignore[attr-defined]


def test_secondary_table_relationships() -> None:
    """Test that secondary table relationships are handled correctly."""

    class RightDTO(DTO[Right]):
        config = DTOConfig(exclude={Right.lefts})

    class LeftDTO(DTO[Left]):
        config = DTOConfig(
            include_relationships=True,
            mapped={Left.rights: list[RightDTO]},
        )

    # This test is conceptual and depends on the testing environment with a database.
    # It would involve checking the secondary table relationships.
    # For now, we will just ensure the DTO is created correctly.
    assert "rights" in LeftDTO.model_fields  # type: ignore[attr-defined]
