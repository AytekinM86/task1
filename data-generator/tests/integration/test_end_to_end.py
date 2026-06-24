"""End-to-end integration test: a full seed run, rolled back via --dry-run.

Exercises every generator, repository, and the FK-ordered orchestration against
the real schema (validating SQL and constraints) without persisting anything.
"""

from __future__ import annotations

import pytest

from hospital_datagen.config import Settings
from hospital_datagen.db.connection import ConnectionManager
from hospital_datagen.exceptions import DatabaseConnectionError
from hospital_datagen.factory import build_orchestrator
from hospital_datagen.orchestrator import SeedPlan

pytestmark = pytest.mark.integration

_PLAN = SeedPlan(
    departments=3,
    specialties=3,
    medications=6,
    doctors=5,
    patients=20,
    appointments=60,
    prescriptions=15,
    max_items_per_prescription=3,
)


def test_full_seed_dry_run() -> None:
    settings = Settings(faker_seed=42, window_days=90)
    manager = ConnectionManager(settings)
    try:
        manager.connect()
    except DatabaseConnectionError as exc:
        pytest.skip(f"PostgreSQL not reachable: {exc}")

    try:
        orchestrator = build_orchestrator(settings, manager)
        result = orchestrator.run(_PLAN, dry_run=True)
    finally:
        manager.close()

    assert result.counts["departments"] == 3
    assert result.counts["patients"] == 20
    assert result.counts["appointments"] == 60
    assert result.counts["prescriptions"] == 15
    assert result.counts["prescription_items"] >= 15
