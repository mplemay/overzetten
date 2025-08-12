"""Tests for basic DTO creation and functionality."""

import datetime
from decimal import Decimal

from pydantic import BaseModel

from overzetten import DTO, DTOConfig
from overzetten.__tests__.fixtures.models import User


def test_basic_dto_creation() -> None:
    """Test creating a basic DTO with no configuration."""

    class UserDTO(DTO[User]):
        pass

    # 1. Test that all SQLAlchemy fields are properly converted with correct Python types
    # and that the generated Pydantic model has correct field names.
    fields = UserDTO.model_fields
    assert list(fields.keys()) == [
        "id",
        "name",
        "fullname",
        "age",
        "is_active",
        "created_at",
        "registered_on",
        "last_login",
        "balance",
        "rating",
        "data",
        "preferences",
        "tags",
        "uuid_field",
        "secret_field",
        "json_field",
    ]

    # 2. Test that the returned class is actually a Pydantic model
    assert issubclass(UserDTO, BaseModel)

    # 3. Test that the field types are correct
    assert fields["id"].annotation is int
    assert fields["name"].annotation is str
    assert fields["fullname"].annotation == str | None
    assert fields["age"].annotation is int
    assert fields["is_active"].annotation is bool
    assert fields["created_at"].annotation is datetime.datetime
    assert fields["registered_on"].annotation is datetime.date
    assert fields["last_login"].annotation is datetime.time
    assert fields["balance"].annotation is float
    assert fields["rating"].annotation is Decimal
    assert fields["data"].annotation == bytes | None


def test_dto_naming_and_module() -> None:
    """Test that __name__, __qualname__, and __module__ are set correctly."""

    class UserDTO(DTO[User]):
        pass

    assert UserDTO.__name__ == "UserDTO"
    assert UserDTO.__qualname__ == "UserDTO"
    assert UserDTO.__module__ is not None
    assert UserDTO.__module__ != "overzetten.__main__"


def test_multiple_dtos_from_same_model() -> None:
    """Test creating multiple DTOs from the same SQLAlchemy model with different configs."""

    class UserReadDTO(DTO[User]):
        pass

    class UserWriteDTO(DTO[User]):
        config = DTOConfig(exclude={User.id, User.created_at})

    # Verify UserReadDTO has all fields
    assert "id" in UserReadDTO.model_fields
    assert "created_at" in UserReadDTO.model_fields

    # Verify UserWriteDTO has excluded fields removed
    assert "id" not in UserWriteDTO.model_fields
    assert "created_at" not in UserWriteDTO.model_fields
    assert "name" in UserWriteDTO.model_fields
