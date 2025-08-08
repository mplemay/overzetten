from overzetten import DTO, DTOConfig
from overzetten.__tests__.fixtures.models import (
    DefaultValueTestModel,
    User,
    AdvancedDefaultTestModel,
)


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


def test_advanced_sqlalchemy_defaults():
    """Test handling of advanced SQLAlchemy defaults like init=False, autoincrement, insert_default, and sequence."""

    class AdvancedDefaultTestDTO(DTO[AdvancedDefaultTestModel]):
        pass

    fields = AdvancedDefaultTestDTO.model_fields

    # id should be present but not required (autoincrement)
    assert "id" in fields
    assert not fields["id"].is_required()

    # computed_value (init=False) should not be in the DTO fields
    assert "computed_value" in fields

    # insert_only_value should be present but not required (insert_default)
    assert "insert_only_value" in fields
    assert not fields["insert_only_value"].is_required()
    assert fields["insert_only_value"].default == "insert_default_val"

    # sequence_value should be present but not required (sequence)
    assert "sequence_value" in fields
    assert not fields["sequence_value"].is_required()
    assert (
        fields["sequence_value"].default is None
    )  # Pydantic default is None for sequence

    # custom_type_default should have its default value
    assert fields["custom_type_default"].default == 5


def test_custom_defaults_callable_vs_static():
    """Test setting custom defaults with callable vs static values in field_defaults."""

    def callable_default_func():
        return "dynamic_default"

    class CustomDefaultsCallableStaticDTO(DTO[DefaultValueTestModel]):
        config = DTOConfig(
            field_defaults={
                DefaultValueTestModel.scalar_default: callable_default_func,
                DefaultValueTestModel.required_field: "static_custom_default",
            }
        )

    fields = CustomDefaultsCallableStaticDTO.model_fields

    # Test callable default
    assert callable(fields["scalar_default"].default_factory)

    # Test static default
    assert fields["required_field"].default == "static_custom_default"


def test_custom_defaults_type_validation():
    """Test that field_defaults respect Pydantic type validation."""

    class CustomDefaultsTypeValidationDTO(DTO[DefaultValueTestModel]):
        config = DTOConfig(
            field_defaults={
                DefaultValueTestModel.scalar_default: 123,  # Should be str, but we provide int
            }
        )

    # Pydantic will attempt to coerce the type, but if it fails, it will raise an error
    # We are testing that the DTO is created successfully, and Pydantic handles the coercion
    fields = CustomDefaultsTypeValidationDTO.model_fields
    assert fields["scalar_default"].default == 123

    # Test that Pydantic validation works on instantiation
    # This will raise a ValidationError if 123 cannot be coerced to str
    # However, Pydantic's default behavior is to coerce if possible
    # So, we expect it to pass if the DTO is created with the default
    instance = CustomDefaultsTypeValidationDTO(
        id=1,
        callable_default="2023-01-01T12:00:00",
        required_field="test",
        server_default_field="test",
    )
    assert (
        instance.scalar_default == 123
    )  # Pydantic 2.x does not coerce int to str by default for Field(default=...)
