import pytest
import datetime

from overzetten import DTO
from overzetten.__tests__.fixtures.models import (
    Employee,
    Manager,
    Engineer,
    BaseMappedModel,
    ChildMappedModel,
    Product,
    AbstractBaseModel,
    ConcreteModel,
)


def test_single_table_inheritance():
    """Test DTO creation from models with single table inheritance."""

    class EmployeeDTO(DTO[Employee]):
        pass

    class ManagerDTO(DTO[Manager]):
        pass

    class EngineerDTO(DTO[Engineer]):
        pass

    # Test parent DTO
    assert list(EmployeeDTO.model_fields.keys()) == ["id", "type"]

    # Test child DTOs
    assert list(ManagerDTO.model_fields.keys()) == ["id", "type", "manager_data"]
    assert list(EngineerDTO.model_fields.keys()) == ["id", "type", "engineer_info"]


def test_joined_table_inheritance_field_distribution():
    """Test DTO creation from models with joined table inheritance, ensuring all fields are present."""

    class BaseMappedDTO(DTO[BaseMappedModel]):
        pass

    class ChildMappedDTO(DTO[ChildMappedModel]):
        pass

    # Test base DTO
    base_fields = BaseMappedDTO.model_fields
    assert "id" in base_fields
    assert "base_field" in base_fields
    assert "common_field" in base_fields

    # Test child DTO - should contain fields from both base and child tables
    child_fields = ChildMappedDTO.model_fields
    assert "id" in child_fields
    assert "base_field" in child_fields
    assert "common_field" in child_fields
    assert "child_field" in child_fields


def test_mixin_inheritance():
    """Test DTO creation from models that use mixin classes."""

    class ProductDTO(DTO[Product]):
        pass

    fields = ProductDTO.model_fields

    assert "id" in fields
    assert "name" in fields
    assert "description" in fields
    assert "created_at" in fields
    assert "updated_at" in fields

    # Check types for mixin fields
    assert fields["created_at"].annotation is datetime.datetime
    assert fields["updated_at"].annotation is datetime.datetime


def test_abstract_base_model_dto_creation():
    """Test that DTOs cannot be created directly from abstract SQLAlchemy models."""
    with pytest.raises(
        TypeError, match="Cannot create DTO from abstract or unmapped SQLAlchemy model"
    ):  # Adjust match string if needed

        class AbstractDTO(DTO[AbstractBaseModel]):
            pass

    # Ensure concrete model can still create a DTO
    class ConcreteDTO(DTO[ConcreteModel]):
        pass

    fields = ConcreteDTO.model_fields
    assert "id" in fields
    assert "abstract_field" in fields
    assert "concrete_field" in fields
