"""Tests for handling circular references in DTO generation."""

from typing import Optional

from overzetten import DTO, DTOConfig
from overzetten.__tests__.fixtures.models import Address, User


def test_circular_mapping_references() -> None:
    """Test that circular mapping references between DTOs are handled correctly."""

    class UserCircleDTO(DTO[User]):
        config = DTOConfig(
            include_relationships=True,
            mapped={User.addresses: list["AddressCircleDTO"]},
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

    assert user_fields["addresses"].annotation == list[AddressCircleDTO]
    assert address_fields["user"].annotation == UserCircleDTO | None
