import datetime

import pytest

from overzetten import DTO, DTOConfig
from overzetten.__tests__.fixtures.models import (
    AbstractBaseModel,
    BaseMappedModel,
    ChildMappedModel,
    ConcreteModel,
    ConcreteTableBase,
    ConcreteTableChild,
    Employee,
    Engineer,
    Manager,
    Product,
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
        TypeError,
        match="Cannot create DTO from abstract or unmapped SQLAlchemy model",
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


def test_discriminator_column_handling():
    """Test that the discriminator column is included in single table inheritance DTOs."""

    class EmployeeDTO(DTO[Employee]):
        pass

    class ManagerDTO(DTO[Manager]):
        pass

    class EngineerDTO(DTO[Engineer]):
        pass

    # The 'type' column is the discriminator and should be present
    assert "type" in EmployeeDTO.model_fields
    assert "type" in ManagerDTO.model_fields
    assert "type" in EngineerDTO.model_fields
    assert EmployeeDTO.model_fields["type"].annotation is str


def test_inherited_field_exclusion_and_mapping():
    """Test inherited field exclusion and mapping in joined table inheritance."""

    class BaseMappedDTO(DTO[BaseMappedModel]):
        config = DTOConfig(
            exclude={BaseMappedModel.base_field},
            mapped={BaseMappedModel.common_field: str},  # Ensure it's explicitly str
        )

    class ChildMappedDTO(DTO[ChildMappedModel]):
        config = DTOConfig(
            exclude={ChildMappedModel.child_field},
            mapped={ChildMappedModel.common_field: str},  # Ensure it's explicitly str
        )

    # Base DTO should exclude base_field and map common_field
    base_fields = BaseMappedDTO.model_fields
    assert "base_field" not in base_fields
    assert base_fields["common_field"].annotation is str
    assert "id" in base_fields

    # Child DTO should exclude child_field and map common_field, and inherit base_field (which was excluded in BaseMappedDTO)
    # Note: The base_field will still be present in ChildMappedDTO if it's not explicitly excluded in ChildMappedDTO
    # and if it's part of the ChildMappedModel's columns. This tests the behavior.
    child_fields = ChildMappedDTO.model_fields
    assert "child_field" not in child_fields
    assert child_fields["common_field"].annotation is str
    assert "id" in child_fields
    # base_field should be present in ChildMappedDTO as it's part of ChildMappedModel's columns
    # and not explicitly excluded in ChildMappedDTO
    assert "base_field" in child_fields


def test_concrete_table_inheritance_dtos():
    """Test DTO creation from models with concrete table inheritance."""

    class ConcreteTableBaseDTO(DTO[ConcreteTableBase]):
        pass

    class ConcreteTableChildDTO(DTO[ConcreteTableChild]):
        pass

    # Base DTO should only have its own fields
    base_fields = ConcreteTableBaseDTO.model_fields
    assert list(base_fields.keys()) == ["id", "base_data"]

    # Child DTO should have its own fields (including inherited ones if they are part of its table)
    # In concrete table inheritance, child tables have all columns, including those from the base.
    child_fields = ConcreteTableChildDTO.model_fields
    assert list(child_fields.keys()) == ["id", "base_data", "child_data"]


def test_joined_table_inheritance_foreign_key():
    """Test that the foreign key in joined table inheritance is handled correctly."""

    class ChildMappedDTO(DTO[ChildMappedModel]):
        pass

    # The foreign key column (id) should be present and correctly typed
    child_fields = ChildMappedDTO.model_fields
    assert "id" in child_fields
    assert child_fields["id"].annotation is int
