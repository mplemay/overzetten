"""Tests for DTO generation with deep inheritance."""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase

from overzetten import DTO


class Base(DeclarativeBase):
    """Base class for SQLAlchemy declarative models in tests."""


def create_deep_inheritance_model(depth: int) -> type[DeclarativeBase]:
    """Dynamically creates a chain of deeply inherited SQLAlchemy models."""
    # Create a chain of inherited models
    current_base = Base
    for i in range(depth):
        model_name = f"Level{i}Model"
        attrs = {
            "__tablename__": f"level_{i}_model",
            "id": Column(Integer, ForeignKey(f"level_{i - 1}_model.id"), primary_key=True)
            if i > 0
            else Column(Integer, primary_key=True),
            f"data_level_{i}": Column(String, nullable=False),
        }
        # Inherit from the previous level's model
        current_base = type(model_name, (current_base,), attrs)
    return current_base


def test_deep_inheritance_dto_creation() -> None:
    """Test DTO creation for a SQLAlchemy model with deep inheritance."""
    depth = 10
    deepest_model = create_deep_inheritance_model(depth)

    class DeepestModelDTO(DTO[deepest_model]):
        pass

    fields = DeepestModelDTO.model_fields

    # Check that all fields from all levels of inheritance are present
    expected_fields = {"id"}
    for i in range(depth):
        expected_fields.add(f"data_level_{i}")

    assert len(fields) == len(expected_fields)
    for field_name in expected_fields:
        if field_name == "id":
            assert fields[field_name].annotation is int
        else:
            assert fields[field_name].annotation is str
