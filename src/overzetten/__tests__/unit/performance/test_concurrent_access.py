"""Conceptual tests for concurrent DTO access."""

from overzetten import DTO, DTOConfig
from overzetten.__tests__.fixtures.models import User


def test_concurrent_access_conceptual() -> None:
    """Conceptual test for concurrent access. Requires proper threading/multiprocessing setup."""
    # This test is a placeholder to acknowledge the need for concurrent access testing.
    # Actual concurrent access testing would involve:
    # 1. Creating multiple threads or processes.
    # 2. Each thread/process attempting to create DTOs concurrently.
    # 3. Asserting consistency and lack of race conditions or deadlocks.

    # For now, we will just ensure the DTO creation process itself is not inherently broken
    # by a single, sequential creation.
    class SimpleUserDTO(DTO[User]):
        config = DTOConfig(model_name="SimpleUserDTO")

    instance = SimpleUserDTO(
        id=1,
        name="Test User",
        age=30,
        is_active=True,
        created_at="2023-01-01T10:00:00",
        registered_on="2023-01-01",
        last_login="10:00:00",
        balance=100.0,
        rating=4.5,
    )
    assert instance.id == 1
