
import pytest

from overzetten import DTO
from test.fixtures.sqlalchemy_models import Employee, Manager, Engineer


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
