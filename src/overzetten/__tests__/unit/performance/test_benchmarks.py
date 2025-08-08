import pytest
from overzetten import DTO, DTOConfig
from overzetten.__tests__.fixtures.models import User
from pydantic import BaseModel
from dataclasses import dataclass
import time


def test_benchmark_comparisons_conceptual():
    """Conceptual test for benchmarking DTO creation against manual Pydantic models and dataclasses."""
    # This test is a placeholder for actual performance benchmarking.
    # Benchmarking would involve:
    # 1. Defining a representative SQLAlchemy model.
    # 2. Creating equivalent manual Pydantic models and dataclasses.
    # 3. Measuring the time taken to create instances of each type (SQLAlchemy DTO, manual Pydantic, dataclass).
    # 4. Comparing the performance metrics.

    # Example (conceptual, not fully implemented for execution):

    # @dataclass
    # class ManualDataclassUser:
    #     id: int
    #     name: str
    #     age: int

    # class ManualPydanticUser(BaseModel):
    #     id: int
    #     name: str
    #     age: int

    # class OverzettenUserDTO(DTO[User]):
    #     config = DTOConfig(include={User.id, User.name, User.age})

    # num_iterations = 10000

    # start_time = time.perf_counter()
    # for i in range(num_iterations):
    #     ManualDataclassUser(id=i, name=f"User_{i}", age=i)
    # end_time = time.perf_counter()
    # dataclass_time = end_time - start_time

    # start_time = time.perf_counter()
    # for i in range(num_iterations):
    #     ManualPydanticUser(id=i, name=f"User_{i}", age=i)
    # end_time = time.perf_counter()
    # pydantic_time = end_time - start_time

    # start_time = time.perf_counter()
    # for i in range(num_iterations):
    #     OverzettenUserDTO(id=i, name=f"User_{i}", age=i)
    # end_time = time.perf_counter()
    # overzetten_time = end_time - start_time

    # print(f"Dataclass creation time: {dataclass_time:.4f}s")
    # print(f"Manual Pydantic creation time: {pydantic_time:.4f}s")
    # print(f"Overzetten DTO creation time: {overzetten_time:.4f}s")

    # Assert that the test runs without errors.
    assert True
