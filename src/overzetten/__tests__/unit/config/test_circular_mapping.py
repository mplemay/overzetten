import pytest
from typing import List, Optional

from overzetten import DTO, DTOConfig
from overzetten.__tests__.fixtures.models import User, Address


def test_circular_mapping_references():
    """Test that circular mapping references between DTOs are handled correctly."""

    class UserCircleDTO(DTO[User]):
        config = DTOConfig(
            include_relationships=True,
            mapped={User.addresses: List["AddressCircleDTO"]},
        )

    class AddressCircleDTO(DTO[Address]):
        config = DTOConfig(
            include_relationships=True,
            mapped={Address.user: Optional["UserCircleDTO"]},
        )

    # Manually rebuild the models to resolve forward references
    UserCircleDTO.model_rebuild()
    AddressCircleDTO.model_rebuild()

    # The models should be created without errors
    assert UserCircleDTO is not None
    assert AddressCircleDTO is not None

    # Test that the fields are correctly typed
    user_fields = UserCircleDTO.model_fields
    address_fields = AddressCircleDTO.model_fields

    assert user_fields["addresses"].annotation == List[AddressCircleDTO]
    assert address_fields["user"].annotation == Optional[UserCircleDTO]