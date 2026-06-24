"""Fixtures for integration tests against a live PostgreSQL database.

Every test runs inside a transaction that is always rolled back, so the
database (including the three seed rows) is left untouched. If Postgres is not
reachable, the tests are skipped rather than failing.
"""

from __future__ import annotations

from collections.abc import Iterator

import psycopg
import pytest

from hospital_datagen.config import Settings
from hospital_datagen.db.connection import ConnectionManager
from hospital_datagen.exceptions import DatabaseConnectionError


@pytest.fixture(scope="session")
def integration_settings() -> Settings:
    return Settings()


@pytest.fixture
def db_conn(integration_settings: Settings) -> Iterator[psycopg.Connection]:
    manager = ConnectionManager(integration_settings)
    try:
        conn = manager.connect()
    except DatabaseConnectionError as exc:
        pytest.skip(f"PostgreSQL not reachable: {exc}")
    try:
        yield conn
    finally:
        conn.rollback()
        manager.close()
