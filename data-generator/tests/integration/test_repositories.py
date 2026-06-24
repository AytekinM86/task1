"""Integration tests for the repositories (real DB, always rolled back)."""

from __future__ import annotations

from datetime import date

import psycopg
import pytest

from hospital_datagen.db.repositories import (
    DepartmentRepository,
    PatientRepository,
    PrescriptionItemRepository,
)
from hospital_datagen.exceptions import DuplicateValueError
from hospital_datagen.models import (
    DepartmentInsert,
    PatientInsert,
    PrescriptionItemInsert,
)

pytestmark = pytest.mark.integration

_SEED_ROWS = 3  # the schema ships with three hand-written rows per table


def test_department_insert_returns_generated_id(db_conn: psycopg.Connection) -> None:
    repo = DepartmentRepository()
    row = repo.insert(db_conn, DepartmentInsert(name="ittest-dept", location="Wing X"))
    assert row.department_id > _SEED_ROWS
    assert row.name == "ittest-dept"


def test_patient_insert_returns_generated_id(db_conn: psycopg.Connection) -> None:
    repo = PatientRepository()
    row = repo.insert(
        db_conn,
        PatientInsert(
            first_name="Ittest",
            last_name="Patient",
            dob=date(1990, 1, 1),
            gender="F",
            phone="+1-555-0000",
            email="ittest.patient@example.com",
        ),
    )
    assert row.patient_id > _SEED_ROWS


def test_duplicate_email_raises(db_conn: psycopg.Connection) -> None:
    repo = PatientRepository()
    # john.doe@example.com is one of the seeded patient emails (UNIQUE).
    with pytest.raises(DuplicateValueError):
        repo.insert(
            db_conn,
            PatientInsert(
                first_name="Dup",
                last_name="Licate",
                dob=date(1980, 5, 5),
                email="john.doe@example.com",
            ),
        )


def test_prescription_item_composite_insert(db_conn: psycopg.Connection) -> None:
    repo = PrescriptionItemRepository()
    # Seed prescription_id=1 has item medication_id=3; (1,1) is a free pairing.
    row = repo.insert(
        db_conn,
        PrescriptionItemInsert(prescription_id=1, medication_id=1, dosage="1 tablet daily"),
    )
    assert row.prescription_id == 1
    assert row.medication_id == 1
