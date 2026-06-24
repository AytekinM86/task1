"""Shared fixtures for unit and integration tests."""

from __future__ import annotations

from datetime import datetime

import pytest

from hospital_datagen.config import Settings
from hospital_datagen.factory import build_generators
from hospital_datagen.orchestrator import Generators

# A pinned reference time so every temporal assertion is deterministic.
REFERENCE_TIME = datetime(2026, 6, 23, 12, 0, 0)
SEED = 12345


@pytest.fixture
def reference_time() -> datetime:
    return REFERENCE_TIME


@pytest.fixture
def settings() -> Settings:
    return Settings(
        _env_file=None,
        faker_seed=SEED,
        reference_time=REFERENCE_TIME,
        window_days=30,
    )


@pytest.fixture
def generators(settings: Settings, reference_time: datetime) -> Generators:
    return build_generators(settings, reference_time)
