from typing import List

from overzetten import DTO, DTOConfig
from fixtures.sqlalchemy_models import User, Address


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
    assert user_fields["addresses"].annotation is List[AddressDTO]

    # Test child DTO excluding parent reference
    address_fields = AddressDTO.model_fields
    assert "user" not in address_fields
