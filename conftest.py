import sys
import os
import pytest
from sqlalchemy import create_engine
from test.fixtures.sqlalchemy_models import (
    Base,
    PostgresBase,
    MySQLBase,
    User,
    Address,
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="function")
def db_engine():
    engine = create_engine("sqlite:///:memory:")

    # Drop all tables from both metadata objects to ensure a clean slate
    Base.metadata.drop_all(engine)
    PostgresBase.metadata.drop_all(engine)
    MySQLBase.metadata.drop_all(engine)

    # Create tables only for SQLite-compatible models
    Base.metadata.create_all(engine, tables=[
        User.__table__,
        Address.__table__,
    ])
    yield engine

    # Drop all tables from both metadata objects after tests
    Base.metadata.drop_all(engine)
    PostgresBase.metadata.drop_all(engine)
    MySQLBase.metadata.drop_all(engine)
