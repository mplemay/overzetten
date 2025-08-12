"""Tests for required field logic in DTO generation."""

from pydantic import Field

from overzetten import DTO, DTOConfig
from overzetten.__tests__.fixtures.models import RequiredFieldTestModel


def test_required_no_default() -> None:
    """Test that not nullable fields with no default become required."""

    class RequiredDTO(DTO[RequiredFieldTestModel]):
        pass

    fields = RequiredDTO.model_fields
    assert fields["required_no_default"].is_required()
    assert fields["required_no_default"].annotation is str


def test_nullable_no_default() -> None:
    """Test that nullable fields with no default become Optional[T] with None default."""

    class NullableDTO(DTO[RequiredFieldTestModel]):
        pass

    fields = NullableDTO.model_fields
    assert not fields["nullable_no_default"].is_required()
    assert fields["nullable_no_default"].annotation == str | None
    assert fields["nullable_no_default"].default is None


def test_required_with_default() -> None:
    """Test that not nullable fields with a default become T with default."""

    class DefaultDTO(DTO[RequiredFieldTestModel]):
        pass

    fields = DefaultDTO.model_fields
    assert not fields["required_with_default"].is_required()
    assert fields["required_with_default"].annotation is str
    assert fields["required_with_default"].default == "default_value"


def test_nullable_with_default() -> None:
    """Test that nullable fields with a default become Optional[T] with default."""

    class NullableDefaultDTO(DTO[RequiredFieldTestModel]):
        pass

    fields = NullableDefaultDTO.model_fields
    assert not fields["nullable_with_default"].is_required()
    assert fields["nullable_with_default"].annotation == str | None
    assert fields["nullable_with_default"].default == "nullable_default"


def test_required_with_server_default() -> None:
    """Test that not nullable fields with a server_default become T with default."""

    class ServerDefaultDTO(DTO[RequiredFieldTestModel]):
        pass

    fields = ServerDefaultDTO.model_fields
    assert not fields["required_with_server_default"].is_required()
    assert fields["required_with_server_default"].annotation is str
    # SQLAlchemy's server_default is not directly reflected in Pydantic's default
    # unless explicitly handled by overzetten. For now, we check it's not required.
    # Further tests might involve checking the actual default value if overzetten handles it.
    assert fields["required_with_server_default"].default is None  # Pydantic default is None if not explicitly set


def test_nullable_with_server_default() -> None:
    """Test that nullable fields with a server_default become Optional[T] with None default."""

    class NullableServerDefaultDTO(DTO[RequiredFieldTestModel]):
        pass

    fields = NullableServerDefaultDTO.model_fields
    assert not fields["nullable_with_server_default"].is_required()
    assert fields["nullable_with_server_default"].annotation == str | None
    assert fields["nullable_with_server_default"].default is None


def test_boolean_with_default() -> None:
    """Test boolean fields with a default value."""

    class BooleanDefaultDTO(DTO[RequiredFieldTestModel]):
        pass

    fields = BooleanDefaultDTO.model_fields
    assert not fields["boolean_with_default"].is_required()
    assert fields["boolean_with_default"].annotation is bool
    assert fields["boolean_with_default"].default is False


def test_interaction_with_custom_field_defaults() -> None:
    """Test interaction with custom field_defaults in DTOConfig."""

    class CustomDefaultsDTO(DTO[RequiredFieldTestModel]):
        config = DTOConfig(
            field_defaults={
                RequiredFieldTestModel.required_no_default: Field(
                    default="custom_default_for_required",
                ),
                RequiredFieldTestModel.nullable_no_default: Field(
                    "custom_default_for_nullable",
                ),
            },
        )

    fields = CustomDefaultsDTO.model_fields
    assert not fields["required_no_default"].is_required()
    assert fields["required_no_default"].default == "custom_default_for_required"

    assert not fields["nullable_no_default"].is_required()
    assert fields["nullable_no_default"].annotation == str | None
    assert fields["nullable_no_default"].default == "custom_default_for_nullable"

    # Ensure existing SQLAlchemy defaults are not overridden unless specified
    assert fields["required_with_default"].default == "default_value"
    assert fields["nullable_with_default"].default == "nullable_default"
