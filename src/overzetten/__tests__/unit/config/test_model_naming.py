from overzetten import DTO, DTOConfig
from overzetten.__tests__.fixtures.models import User, Address


def test_model_name_override():
    """Test the model_name override."""

    class CustomNameDTO(DTO[User]):
        config = DTOConfig(model_name="MyCustomUserModel")

    assert CustomNameDTO.__name__ == "MyCustomUserModel"
    assert CustomNameDTO.__qualname__ == "MyCustomUserModel"


def test_model_name_prefix_and_suffix():
    """Test the model_name_prefix and model_name_suffix."""

    class PrefixedSuffixedDTO(DTO[User]):
        config = DTOConfig(model_name_prefix="Prefix", model_name_suffix="Suffix")

    assert PrefixedSuffixedDTO.__name__ == "PrefixUserSuffix"
    assert PrefixedSuffixedDTO.__qualname__ == "PrefixUserSuffix"


def test_default_model_naming():
    """Test the default model naming pattern."""

    class UserDTO(DTO[User]):
        pass

    assert UserDTO.__name__ == "UserDTO"
    assert UserDTO.__qualname__ == "UserDTO"


def test_naming_does_not_affect_functionality():
    """Test that naming doesn't affect the functionality of the DTO."""

    class MyDTO(DTO[User]):
        config = DTOConfig(model_name="FunctionalityTest")

    # Check if fields are still correctly populated
    fields = MyDTO.model_fields
    assert "id" in fields
    assert "name" in fields
    assert fields["id"].annotation is int

    # Check instantiation
    instance = MyDTO(
        id=1,
        name="test",
        age=30,
        is_active=True,
        created_at="2023-01-01T12:00:00",
        registered_on="2023-01-01",
        last_login="12:00:00",
        balance=100.0,
        rating=4.5,
        data=None,
    )
    assert instance.id == 1
    assert instance.name == "test"

def test_name_conflicts():
    """Test that name conflicts are handled gracefully."""

    class UserDTO(DTO[User]):
        pass

    class AddressDTO(DTO[Address]):
        config = DTOConfig(model_name="UserDTO")

    assert UserDTO.__name__ == "UserDTO"
    assert AddressDTO.__name__ == "UserDTO"
    assert UserDTO is not AddressDTO

def test_very_long_model_name():
    """Test that a very long model name can be used."""
    long_name = "a" * 1000

    class LongNameDTO(DTO[User]):
        config = DTOConfig(model_name=long_name)

    assert LongNameDTO.__name__ == long_name
    assert LongNameDTO.__qualname__ == long_name

def test_model_name_with_special_characters():
    """Test that a model name with special characters can be used."""
    special_name = "My_Special-Model.Name"

    class SpecialNameDTO(DTO[User]):
        config = DTOConfig(model_name=special_name)

    assert SpecialNameDTO.__name__ == special_name
    assert SpecialNameDTO.__qualname__ == special_name