"""Tests for SeedOrchestrator using in-memory fake repositories (no DB)."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from datetime import datetime
from typing import Any, cast

import pytest

from hospital_datagen.config import Settings
from hospital_datagen.db.connection import ConnectionManager
from hospital_datagen.db.repositories import (
    AppointmentRepository,
    DepartmentRepository,
    DoctorRepository,
    MedicationRepository,
    PatientRepository,
    PrescriptionItemRepository,
    PrescriptionRepository,
    SpecialtyRepository,
)
from hospital_datagen.exceptions import DataGenError, InsertError
from hospital_datagen.factory import build_generators
from hospital_datagen.orchestrator import (
    Generators,
    Repositories,
    SeedOrchestrator,
    SeedPlan,
)

_PLAN = SeedPlan(
    departments=3,
    specialties=3,
    medications=5,
    doctors=4,
    patients=10,
    appointments=50,
    prescriptions=10,
    max_items_per_prescription=3,
)


class FakeConnectionManager:
    """Mimics ConnectionManager.transaction commit/rollback semantics."""

    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False

    @contextmanager
    def transaction(self) -> Iterator[object]:
        try:
            yield object()
        except BaseException:
            self.rolled_back = True
            raise
        else:
            self.committed = True


class FakeRepository:
    """Assigns synthetic IDs (beyond the seeded 1-3) without touching a DB."""

    def __init__(self, repo_cls: Any, call_log: list[str]) -> None:
        self._row_model = repo_cls.row_model
        self._returning = repo_cls.returning_columns
        self._table = repo_cls.table
        self._call_log = call_log
        self._counter = 3  # seed rows occupy 1-3

    def existing_values(self, _conn: object, _column: str) -> set[str]:
        return set()

    def insert_many(self, _conn: object, items: Sequence[Any]) -> list[Any]:
        self._call_log.append(self._table)
        rows: list[Any] = []
        for item in items:
            fields = type(item).model_fields
            returned: dict[str, Any] = {}
            for col in self._returning:
                if col in fields:
                    returned[col] = getattr(item, col)
                else:
                    self._counter += 1
                    returned[col] = self._counter
            rows.append(self._row_model(**{**item.model_dump(), **returned}))
        return rows


class FailingRepository(FakeRepository):
    def insert_many(self, _conn: object, items: Sequence[Any]) -> list[Any]:
        raise InsertError(self._table, "boom")


def _generators(settings: Settings, reference_time: datetime) -> Generators:
    return build_generators(settings, reference_time)


def _repositories(call_log: list[str]) -> Repositories:
    return Repositories(
        departments=cast(DepartmentRepository, FakeRepository(DepartmentRepository, call_log)),
        specialties=cast(SpecialtyRepository, FakeRepository(SpecialtyRepository, call_log)),
        medications=cast(MedicationRepository, FakeRepository(MedicationRepository, call_log)),
        doctors=cast(DoctorRepository, FakeRepository(DoctorRepository, call_log)),
        patients=cast(PatientRepository, FakeRepository(PatientRepository, call_log)),
        appointments=cast(AppointmentRepository, FakeRepository(AppointmentRepository, call_log)),
        prescriptions=cast(
            PrescriptionRepository, FakeRepository(PrescriptionRepository, call_log)
        ),
        prescription_items=cast(
            PrescriptionItemRepository,
            FakeRepository(PrescriptionItemRepository, call_log),
        ),
    )


def test_seeds_in_fk_order_and_commits(settings: Settings, reference_time: datetime) -> None:
    call_log: list[str] = []
    conn_mgr = FakeConnectionManager()
    orchestrator = SeedOrchestrator(
        cast(ConnectionManager, conn_mgr),
        _repositories(call_log),
        _generators(settings, reference_time),
    )

    result = orchestrator.run(_PLAN)

    assert call_log == [
        "departments",
        "specialties",
        "medications",
        "doctors",
        "patients",
        "appointments",
        "prescriptions",
        "prescription_items",
    ]
    assert result.counts["departments"] == 3
    assert result.counts["appointments"] == 50
    assert result.counts["prescriptions"] == 10
    assert result.counts["prescription_items"] >= 10
    assert conn_mgr.committed is True
    assert conn_mgr.rolled_back is False


def test_dry_run_rolls_back(settings: Settings, reference_time: datetime) -> None:
    conn_mgr = FakeConnectionManager()
    orchestrator = SeedOrchestrator(
        cast(ConnectionManager, conn_mgr),
        _repositories([]),
        _generators(settings, reference_time),
    )

    result = orchestrator.run(_PLAN, dry_run=True)

    assert result.counts["patients"] == 10
    assert conn_mgr.committed is False
    assert conn_mgr.rolled_back is True


def test_error_rolls_back_and_propagates(settings: Settings, reference_time: datetime) -> None:
    call_log: list[str] = []
    base = _repositories(call_log)
    # Force the first insert to fail.
    repos = Repositories(
        departments=cast(DepartmentRepository, FailingRepository(DepartmentRepository, call_log)),
        specialties=base.specialties,
        medications=base.medications,
        doctors=base.doctors,
        patients=base.patients,
        appointments=base.appointments,
        prescriptions=base.prescriptions,
        prescription_items=base.prescription_items,
    )
    conn_mgr = FakeConnectionManager()
    orchestrator = SeedOrchestrator(
        cast(ConnectionManager, conn_mgr),
        repos,
        _generators(settings, reference_time),
    )

    with pytest.raises(DataGenError):
        orchestrator.run(_PLAN)

    assert conn_mgr.committed is False
    assert conn_mgr.rolled_back is True
