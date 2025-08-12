"""Tests for metaclass and generic behavior in DTO generation."""

from overzetten import DTO, DTOConfig
from overzetten.__tests__.fixtures.models import Address, User


def test_dto_model_syntax_variations() -> None:
    """Test DTO[Model] syntax variations."""

    # Basic DTO[Model]
    class UserDTO(DTO[User]):
        pass

    assert UserDTO.__name__ == "UserDTO"
    assert "id" in UserDTO.model_fields

    # DTO[Model] with explicit config
    class UserConfigDTO(DTO[User]):
        config = DTOConfig(model_name="UserConfigDTO")

    assert UserConfigDTO.__name__ == "UserConfigDTO"
    assert "id" in UserConfigDTO.model_fields

    # DTO[Model] with no explicit config (should use default)
    class UserDefaultConfigDTO(DTO[User]):
        pass

    assert UserDefaultConfigDTO.__name__ == "UserDTO"
    assert "id" in UserDefaultConfigDTO.model_fields

    # Test with a different model
    class AddressDTO(DTO[Address]):  # Corrected to use Address model
        pass

    assert AddressDTO.__name__ == "AddressDTO"
    assert "id" in AddressDTO.model_fields


def test_multiple_type_parameters_future_expansion() -> None:
    """Test multiple type parameters (future expansion)."""
    # This test is a placeholder for future expansion.
    # It would involve defining DTOs with multiple generic type parameters
    # and asserting their correct resolution.
    assert True
