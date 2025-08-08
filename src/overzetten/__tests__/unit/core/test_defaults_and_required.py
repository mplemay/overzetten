from overzetten import DTO, DTOConfig
from overzetten.__tests__.fixtures.models import DefaultValueTestModel, User


def test_default_values_and_required_fields():
    """Test handling of SQLAlchemy defaults and required fields."""

    class DefaultValueTestDTO(DTO[DefaultValueTestModel]):
        pass

    fields = DefaultValueTestDTO.model_fields

    # Test scalar default
    assert fields["scalar_default"].default == "default_value"

    # Test callable default
    assert callable(fields["callable_default"].default_factory)

    # Test required field
    assert fields["required_field"].is_required()


def test_custom_defaults():
    """Test setting custom defaults with field_defaults."""

    class CustomDefaultDTO(DTO[DefaultValueTestModel]):
        config = DTOConfig(
            field_defaults={
                DefaultValueTestModel.scalar_default: "overridden",
                DefaultValueTestModel.required_field: "custom_default",
            }
        )

    fields = CustomDefaultDTO.model_fields

    # Test overriding SQLAlchemy defaults
    assert fields["scalar_default"].default == "overridden"

    # Test setting defaults for required fields
    assert fields["required_field"].default == "custom_default"


def test_server_default():
    """Test handling of server_default."""

    class ServerDefaultDTO(DTO[DefaultValueTestModel]):
        pass

    fields = ServerDefaultDTO.model_fields

    # Fields with server_default are not required in Pydantic
    assert not fields["server_default_field"].is_required()
    # Pydantic default is None if not explicitly set by overzetten
    assert fields["server_default_field"].default is None


def test_defaults_for_excluded_fields_ignored():
    """Test that field_defaults for excluded fields are ignored."""

    class UserExcludedWithDefaultDTO(DTO[User]):
        config = DTOConfig(
            exclude={User.name}, field_defaults={User.name: "should_be_ignored"}
        )

    fields = UserExcludedWithDefaultDTO.model_fields

    # The field should not be present at all
    assert "name" not in fields
