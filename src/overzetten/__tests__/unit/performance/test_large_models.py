from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase

from overzetten import DTO


# Dynamically create a SQLAlchemy model with many fields
class Base(DeclarativeBase):
    pass


def create_large_model(num_fields):
    attrs = {
        "__tablename__": "large_model",
        "id": Column(Integer, primary_key=True),
    }
    for i in range(num_fields):
        attrs[f"field_{i}"] = Column(String, nullable=False)
    return type(f"LargeModel{num_fields}", (Base,), attrs)


def test_large_model_dto_creation():
    """Test DTO creation for a SQLAlchemy model with a large number of fields."""
    num_fields = 100
    LargeModel = create_large_model(num_fields)

    class LargeModelDTO(DTO[LargeModel]):
        pass

    fields = LargeModelDTO.model_fields
    assert len(fields) == num_fields + 1  # +1 for the 'id' field

    # Basic check to ensure fields are correctly typed
    assert fields["id"].annotation is int
    for i in range(num_fields):
        assert fields[f"field_{i}"].annotation is str
