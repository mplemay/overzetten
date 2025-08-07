
import pytest
import datetime

from overzetten import DTO
from test.fixtures.sqlalchemy_models import DefaultValueTestModel


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
