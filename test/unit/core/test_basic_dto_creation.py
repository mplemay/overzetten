from pydantic import BaseModel
from typing import Optional
import datetime
from decimal import Decimal

from overzetten import DTO, DTOConfig
from fixtures.sqlalchemy_models import User


def test_basic_dto_creation(db_engine):
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
    assert fields["id"].annotation == int
    assert fields["name"].annotation == str
    assert fields["fullname"].annotation == Optional[str]
    assert fields["age"].annotation == int
    assert fields["is_active"].annotation == bool
    assert fields["created_at"].annotation == datetime.datetime
    assert fields["registered_on"].annotation == datetime.date
    assert fields["last_login"].annotation == datetime.time
    assert fields["balance"].annotation == float
    assert fields["rating"].annotation == Decimal
    assert fields["data"].annotation == Optional[bytes]


def test_dto_naming_and_module(db_engine):
    """Test that __name__, __qualname__, and __module__ are set correctly."""

    class UserDTO(DTO[User]):
        pass

    assert UserDTO.__name__ == "UserDTO"
    assert UserDTO.__qualname__ == "UserDTO"
    assert UserDTO.__module__ == __name__  # It should be the module where it's defined


def test_multiple_dtos_from_same_model(db_engine):
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
