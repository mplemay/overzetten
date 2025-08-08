from typing import List, Optional

from fastapi import APIRouter, FastAPI, Query
from fastapi.testclient import TestClient

from overzetten import DTO, DTOConfig
from overzetten.__tests__.fixtures.models import Address, User


# Define DTOs for User and Address
class AddressDTO(DTO[Address]):
    config = DTOConfig(exclude={Address.user}, model_name="AddressDTO")  # Exclude user to prevent circular reference


class UserCreateDTO(DTO[User]):
    config = DTOConfig(
        exclude={User.id, User.created_at, User.addresses}, model_name="UserCreateDTO"
    )  # Exclude auto-generated fields


class UserResponseDTO(DTO[User]):
    config = DTOConfig(
        include_relationships=True, mapped={User.addresses: List[AddressDTO]}, model_name="UserResponseDTO"
    )


class UserSimpleResponseDTO(DTO[User]):
    config = DTOConfig(include={User.id, User.name, User.age}, model_name="UserSimpleResponseDTO")


# Create a FastAPI app and router
app = FastAPI()
router = APIRouter()


@router.post("/users/", response_model=UserResponseDTO)
async def create_user(user: UserCreateDTO):
    # In a real application, you would save the user to the database
    # For testing, we'll simulate a created user with an ID and created_at
    created_user_data = user.model_dump()
    created_user_data["id"] = 1  # Simulate DB assigned ID
    created_user_data["created_at"] = "2023-01-01T12:00:00"  # Simulate DB assigned timestamp
    created_user_data["addresses"] = []  # Simulate no addresses on creation
    return UserResponseDTO(**created_user_data)


@router.get("/users/search", response_model=List[UserResponseDTO])
async def search_users(
    name: Optional[str] = Query(None),
    min_age: Optional[int] = Query(None),
):
    # Simulate searching users based on query parameters
    users = []
    if name == user_response_dto.name and (min_age is None or min_age <= user_response_dto.age):
        users.append(user_response_dto)
    
    return users


@router.get("/users/{user_id}", response_model=UserResponseDTO)
async def get_user(user_id: int):
    # Simulate fetching a user from the database
    if user_id == 1:
        return UserResponseDTO(
            id=1,
            name="Test User",
            fullname="Test Fullname",
            age=30,
            is_active=True,
            created_at="2023-01-01T10:00:00",
            registered_on="2023-01-01",
            last_login="10:00:00",
            balance=100.0,
            rating=4.5,
            data=None,
            preferences=None,
            tags=None,
            uuid_field=None,
            secret_field=None,
            json_field=None,
            addresses=[AddressDTO(id=1, email_address="test@example.com", user_id=1)],
        )
    return None


user_response_dto = UserResponseDTO(
    id=1,
    name="Test User",
    fullname="Test Fullname",
    age=30,
    is_active=True,
    created_at="2023-01-01T10:00:00",
    registered_on="2023-01-01",
    last_login="10:00:00",
    balance=100.0,
    rating=4.5,
    data=None,
    preferences=None,
    tags=None,
    uuid_field=None,
    secret_field=None,
    json_field=None,
    addresses=[AddressDTO(id=1, email_address="test@example.com", user_id=1)],
)

app.include_router(router)
client = TestClient(app)


def test_fastapi_request_response_models():
    """Test DTOs as request bodies and response models in FastAPI."""
    # Test POST request with UserCreateDTO as request body
    response = client.post(
        "/users/",
        json={
            "name": "New User",
            "fullname": "New User Fullname",
            "age": 25,
            "is_active": True,
            "registered_on": "2023-01-01",
            "last_login": "10:00:00",
            "balance": 50.0,
            "rating": 3.0,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New User"
    assert "id" in data  # Should be included in response_model
    assert "created_at" in data  # Should be included in response_model
    assert "addresses" in data

    # Test GET request with UserResponseDTO as response model
    response = client.get("/users/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Test User"
    assert len(data["addresses"]) == 1
    assert data["addresses"][0]["email_address"] == "test@example.com"


def test_fastapi_validation_behavior():
    """Test FastAPI validation errors with DTOs."""
    # Test missing required field
    response = client.post(
        "/users/",
        json={
            "fullname": "New User Fullname",
            "age": 25,
            "is_active": True,
            "registered_on": "2023-01-01",
            "last_login": "10:00:00",
            "balance": 50.0,
            "rating": 3.0,
        },
    )
    assert response.status_code == 422  # Unprocessable Entity
    assert "name" in response.json()["detail"][0]["loc"]

    # Test invalid data type
    response = client.post(
        "/users/",
        json={
            "name": "New User",
            "fullname": "New User Fullname",
            "age": "not-an-int",  # Invalid type
            "is_active": True,
            "registered_on": "2023-01-01",
            "last_login": "10:00:00",
            "balance": 50.0,
            "rating": 3.0,
        },
    )
    assert response.status_code == 422
    assert "age" in response.json()["detail"][0]["loc"]


def test_fastapi_path_query_parameters():
    """Test DTOs in path parameters and query parameters."""
    # Path parameter is directly handled by FastAPI, no DTO conversion needed there.
    # Query parameters are handled by Pydantic, so we test that.

    # Test query parameters
    response = client.get("/users/search?name=Test User&min_age=25")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test User"
    assert data[0]["age"] == 30

    response = client.get("/users/search?name=NonExistentUser")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 0  # Should be 0, not 1

    response = client.get("/users/search?min_age=abc")  # Invalid type for min_age
    assert response.status_code == 422
    assert "min_age" in response.json()["detail"][0]["loc"]


def test_fastapi_openapi_schema_generation():
    """Test OpenAPI schema generation correctness."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    openapi_schema = response.json()

    # Check UserCreateDTO schema
    user_create_schema = openapi_schema["components"]["schemas"]["UserCreateDTO"]
    assert "name" in user_create_schema["properties"]
    assert "id" not in user_create_schema["properties"]
    assert "created_at" not in user_create_schema["properties"]

    # Check UserResponseDTO schema
    user_response_schema = openapi_schema["components"]["schemas"]["UserResponseDTO"]
    assert "id" in user_response_schema["properties"]
    assert "name" in user_response_schema["properties"]
    assert "addresses" in user_response_schema["properties"]
    assert user_response_schema["properties"]["addresses"]["type"] == "array"
    assert user_response_schema["properties"]["addresses"]["items"]["$ref"] == "#/components/schemas/AddressDTO"

    # Check AddressDTO schema
    address_schema = openapi_schema["components"]["schemas"]["AddressDTO"]
    assert "id" in address_schema["properties"]
    assert "email_address" in address_schema["properties"]
    assert "user" not in address_schema["properties"]
