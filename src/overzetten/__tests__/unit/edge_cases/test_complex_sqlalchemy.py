import pytest
from sqlalchemy import Column, Integer, String, func
from sqlalchemy.orm import synonym, column_property

from overzetten import DTO
from overzetten.__tests__.fixtures.models import Base


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
