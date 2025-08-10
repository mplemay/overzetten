from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import column_property, synonym

from overzetten import DTO
from overzetten.__tests__.fixtures.models import Base, Employee, Engineer, Manager


class SynonymModel(Base):
    __tablename__ = "synonym_model"

    id = Column(Integer, primary_key=True)
    _name = Column("name", String, nullable=False)

    name = synonym("_name")


def test_synonym_handling():
    """Test that synonyms are handled correctly."""

    class SynonymDTO(DTO[SynonymModel]):
        pass

    fields = SynonymDTO.model_fields
    assert "name" in fields
    assert "_name" not in fields  # The internal column should not be exposed by default
    assert fields["name"].annotation is str


class ColumnPropertyModel(Base):
    __tablename__ = "column_property_model"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    full_name = column_property(first_name + " " + last_name)


def test_column_property_handling():
    """Test that column properties are handled correctly."""

    class ColumnPropertyDTO(DTO[ColumnPropertyModel]):
        pass

    fields = ColumnPropertyDTO.model_fields
    assert "first_name" in fields
    assert "last_name" in fields
    assert "full_name" in fields
    assert fields["full_name"].annotation is str


class MultiSchemaModel(Base):
    __tablename__ = "multi_schema_model"
    __table_args__ = {"schema": "test_schema"}

    id = Column(Integer, primary_key=True)
    data = Column(String)


def test_multi_schema_handling():
    """Test that models in different schemas are handled correctly."""

    class MultiSchemaDTO(DTO[MultiSchemaModel]):
        pass

    fields = MultiSchemaDTO.model_fields
    assert "id" in fields
    assert "data" in fields


def test_polymorphic_models():
    """Test that polymorphic models are handled correctly."""

    class EmployeeDTO(DTO[Employee]):
        pass

    class ManagerDTO(DTO[Manager]):
        pass

    class EngineerDTO(DTO[Engineer]):
        pass

    # Employee DTO should have base fields
    assert "id" in EmployeeDTO.model_fields
    assert "type" in EmployeeDTO.model_fields

    # Manager DTO should have manager_data
    assert "id" in ManagerDTO.model_fields
    assert "type" in ManagerDTO.model_fields
    assert "manager_data" in ManagerDTO.model_fields

    # Engineer DTO should have engineer_info
    assert "id" in EngineerDTO.model_fields
    assert "type" in EngineerDTO.model_fields
    assert "engineer_info" in EngineerDTO.model_fields
