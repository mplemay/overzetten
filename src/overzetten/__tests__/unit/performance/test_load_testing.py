"""Tests for load testing DTO generation."""

from overzetten import DTO, DTOConfig
from overzetten.__tests__.fixtures.models import User


def test_load_testing_dto_creation() -> None:
    """Test generating a large number of DTOs rapidly."""
    num_dtos = 1000
    dtos = []
    for i in range(num_dtos):

        class DynamicUserDTO(DTO[User]):
            config = DTOConfig(model_name=f"DynamicUserDTO_{i}")

        dtos.append(DynamicUserDTO)

    assert len(dtos) == num_dtos
    # Basic check to ensure DTOs are functional
    for i, dto_class in enumerate(dtos):
        instance = dto_class(
            id=i,
            name=f"User_{i}",
            age=25,
            is_active=True,
            created_at="2023-01-01T10:00:00",
            registered_on="2023-01-01",
            last_login="10:00:00",
            balance=100.0,
            rating=4.5,
        )
        assert instance.id == i
        assert instance.name == f"User_{i}"
