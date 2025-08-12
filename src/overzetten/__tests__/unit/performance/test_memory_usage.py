"""Conceptual tests for DTO memory usage."""

from overzetten import DTO, DTOConfig
from overzetten.__tests__.fixtures.models import User


def test_memory_profiling_conceptual() -> None:
    """Conceptual test for memory profiling. Requires external tools for actual measurement."""
    # This test is a placeholder to acknowledge the need for memory profiling.
    # Actual memory profiling would involve:
    # 1. Running the application/library with a memory profiler (e.g., `memory_profiler`, `objgraph`).
    # 2. Analyzing the output to identify memory leaks or excessive memory consumption.
    # 3. Setting a baseline and monitoring changes over time.

    num_dtos = 100
    dtos = []
    for i in range(num_dtos):

        class DynamicUserDTO(DTO[User]):
            config = DTOConfig(model_name=f"MemUserDTO_{i}")

        dtos.append(DynamicUserDTO)
    assert len(dtos) == num_dtos
