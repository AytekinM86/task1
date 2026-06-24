"""Tests for Pydantic model constraints."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from hospital_datagen.models import (
    AppointmentInsert,
    PatientInsert,
    PrescriptionItemInsert,
)


def test_patient_rejects_overlong_first_name() -> None:
    with pytest.raises(ValidationError):
        PatientInsert(first_name="x" * 51, last_name="Doe", dob=date(2000, 1, 1))


def test_patient_rejects_invalid_gender() -> None:
    with pytest.raises(ValidationError):
        PatientInsert(
            first_name="Jane",
            last_name="Doe",
            dob=date(2000, 1, 1),
            gender="X",  # type: ignore[arg-type]
        )


def test_appointment_rejects_invalid_status() -> None:
    with pytest.raises(ValidationError):
        AppointmentInsert(
            patient_id=1,
            doctor_id=1,
            scheduled_at=datetime(2026, 1, 1, 9, 0),
            status="pending",  # type: ignore[arg-type]
        )


def test_appointment_rejects_cost_with_three_decimals() -> None:
    with pytest.raises(ValidationError):
        AppointmentInsert(
            patient_id=1,
            doctor_id=1,
            scheduled_at=datetime(2026, 1, 1, 9, 0),
            cost=Decimal("10.123"),
        )


def test_prescription_item_rejects_overlong_dosage() -> None:
    with pytest.raises(ValidationError):
        PrescriptionItemInsert(prescription_id=1, medication_id=1, dosage="d" * 81)


def test_models_are_frozen() -> None:
    patient = PatientInsert(first_name="Jane", last_name="Doe", dob=date(2000, 1, 1))
    with pytest.raises(ValidationError):
        patient.first_name = "Changed"  # type: ignore[misc]


def test_models_reject_extra_fields() -> None:
    with pytest.raises(ValidationError):
        PatientInsert(
            first_name="Jane",
            last_name="Doe",
            dob=date(2000, 1, 1),
            unexpected="value",  # type: ignore[call-arg]
        )
