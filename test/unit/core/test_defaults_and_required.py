
import pytest
import datetime

from overzetten import DTO, DTOConfig
from test.fixtures.sqlalchemy_models import DefaultValueTestModel


def test_default_values_and_required_fields(db_engine):
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


def test_custom_defaults(db_engine):
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
