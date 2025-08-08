from typing import List, Optional

from overzetten import DTO, DTOConfig
from overzetten.__tests__.fixtures.models import (
    User,
    Address,
    Left,
    Right,
    LeftThrough,
    RightThrough,
    ThroughModel,
)


def test_one_to_many_relationship():
    """Test one-to-many relationship handling."""

    class AddressDTO(DTO[Address]):
        config = DTOConfig(exclude={Address.user})

    class UserWithAddressesDTO(DTO[User]):
        config = DTOConfig(
            include_relationships=True,
            mapped={User.addresses: List[AddressDTO]},
        )

    # Test parent DTO with children collection
    user_fields = UserWithAddressesDTO.model_fields
    assert "addresses" in user_fields
    assert user_fields["addresses"].annotation == List[AddressDTO]

    # Test child DTO excluding parent reference
    address_fields = AddressDTO.model_fields
    assert "user" not in address_fields


def test_many_to_one_foreign_key_handling():
    """Test foreign key field handling in many-to-one relationships."""

    class AddressFKDTO(DTO[Address]):
        # By default, user_id (FK) should be included
        pass

    fields = AddressFKDTO.model_fields
    assert "user_id" in fields
    assert fields["user_id"].annotation is int


def test_many_to_one_relationship_object_inclusion():
    """Test relationship object inclusion in many-to-one relationships."""

    class UserSimpleDTO(DTO[User]):
        config = DTOConfig(exclude={User.addresses}) # Exclude to avoid circular dependency for this test

    class AddressWithUserDTO(DTO[Address]):
        config = DTOConfig(
            include_relationships=True,
            mapped={Address.user: UserSimpleDTO}
        )

    fields = AddressWithUserDTO.model_fields
    assert "user" in fields
    assert fields["user"].annotation == Optional[UserSimpleDTO]
    assert not fields["user"].is_required()

    # Test nullable many-to-one relationship
    # For this, we need a model with a nullable FK
    # Let's assume Address.user_id could be nullable for this test scenario
    # (though in our fixture it's not, this tests the DTO generation logic)
    class NullableUserAddress(DTO[Address]):
        config = DTOConfig(
            include_relationships=True,
            mapped={Address.user: Optional[UserSimpleDTO]}
        )
    fields = NullableUserAddress.model_fields
    assert fields["user"].annotation == Optional[UserSimpleDTO]
    assert not fields["user"].is_required()


def test_many_to_many_association_table_handling():
    """Test many-to-many relationship handling with an association table."""

    class RightDTO(DTO[Right]):
        config = DTOConfig(exclude={Right.lefts}) # Exclude to avoid circular dependency

    class LeftDTO(DTO[Left]):
        config = DTOConfig(
            include_relationships=True,
            mapped={Left.rights: List[RightDTO]}
        )

    fields = LeftDTO.model_fields
    assert "rights" in fields
    assert fields["rights"].annotation == List[RightDTO]

    fields = RightDTO.model_fields
    assert "lefts" not in fields


def test_many_to_many_through_model_handling():
    """Test many-to-many relationship handling with a through model (association object)."""

    class ThroughModelDTO(DTO[ThroughModel]):
        config = DTOConfig(exclude={ThroughModel.left, ThroughModel.right}) # Exclude to avoid circular dependency

    class RightThroughDTO(DTO[RightThrough]):
        config = DTOConfig(exclude={RightThrough.lefts, RightThrough.left_associations}) # Exclude to avoid circular dependency

    class LeftThroughDTO(DTO[LeftThrough]):
        config = DTOConfig(
            include_relationships=True,
            mapped={
                LeftThrough.rights: List[RightThroughDTO],
                LeftThrough.right_associations: List[ThroughModelDTO]
            }
        )

    fields = LeftThroughDTO.model_fields
    assert "rights" in fields
    assert fields["rights"].annotation == List[RightThroughDTO]
    assert "right_associations" in fields
    assert fields["right_associations"].annotation == List[ThroughModelDTO]

    fields = RightThroughDTO.model_fields
    assert "lefts" not in fields
    assert "left_associations" not in fields

    fields = ThroughModelDTO.model_fields
    assert "left" not in fields
    assert "right" not in fields