from typing import Any, Union

import pytest
from pydantic import ValidationError
from pydantic.errors import PydanticUndefinedAnnotation
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from overzetten import DTO, DTOConfig
from overzetten.__tests__.fixtures.models import User


class Base(DeclarativeBase):
    pass


def test_abstract_model_error():
    """Test that creating a DTO from an abstract model raises TypeError."""

    class AbstractModel(Base):
        __abstract__ = True
        id: Mapped[int] = mapped_column(Integer, primary_key=True)
        name: Mapped[str] = mapped_column(String)

    with pytest.raises(
        TypeError,
        match="Cannot create DTO from abstract or unmapped SQLAlchemy model",
    ):

        class InvalidDTO(DTO[AbstractModel]):
            pass


def test_excluding_and_including_same_field():
    """Test that excluding and including the same field results in exclusion."""

    class UserConflictDTO(DTO[User]):
        config = DTOConfig(include={User.id, User.name}, exclude={User.id})

    fields = UserConflictDTO.model_fields
    assert "id" not in fields
    assert "name" in fields


def test_invalid_type_mapping_non_type_object():
    """Test that mapping to a non-type object raises an appropriate error."""

    class InvalidMappedDTO(DTO[User]):
        config = DTOConfig(mapped={User.name: "not_a_type"})

    with pytest.raises(PydanticUndefinedAnnotation):
        InvalidMappedDTO.model_rebuild()


def test_mapping_to_incompatible_type():
    """Test that mapping to an incompatible type results in Pydantic validation error on instantiation."""

    class IncompatibleMappedDTO(DTO[User]):
        config = DTOConfig(mapped={User.age: str})  # Mapping int to str

    # DTO creation should succeed, but instantiation with non-string age should fail
    with pytest.raises(ValidationError):
        IncompatibleMappedDTO(
            id=1,
            name="Test",
            age=30,
            is_active=True,
            created_at="2023-01-01T10:00:00",
            registered_on="2023-01-01",
            last_login="10:00:00",
            balance=100.0,
            rating=4.5,
        )


def test_generic_type_edge_cases():
    """Test generic type edge cases (e.g., Mapped[Any], Mapped[Union])."""

    class GenericEdgeCaseModel(Base):
        __tablename__ = "generic_edge_case_test"
        id: Mapped[int] = mapped_column(Integer, primary_key=True)
        any_field: Mapped[Any] = mapped_column(String)
        union_field: Mapped[str | int] = mapped_column(String)

    class GenericEdgeCaseDTO(DTO[GenericEdgeCaseModel]):
        pass

    fields = GenericEdgeCaseDTO.model_fields
    assert fields["any_field"].annotation is Any
    assert fields["union_field"].annotation == Union[str, int]
