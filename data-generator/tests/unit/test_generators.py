"""Tests for the entity generators, including temporal realism."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from hospital_datagen.config import Settings
from hospital_datagen.exceptions import DependencyError
from hospital_datagen.factory import build_generators
from hospital_datagen.models import (
    GENDERS,
    PAST_STATUSES,
    AppointmentRow,
    DepartmentRow,
    DoctorRow,
    MedicationRow,
    PatientRow,
    PrescriptionRow,
    SpecialtyRow,
)
from hospital_datagen.orchestrator import Generators


# --------------------------------------------------------------------------- #
# Helpers to build parent rows with synthetic IDs.
# --------------------------------------------------------------------------- #
def _departments(n: int) -> list[DepartmentRow]:
    return [DepartmentRow(department_id=i, name=f"Dept {i}") for i in range(1, n + 1)]


def _specialties(n: int) -> list[SpecialtyRow]:
    return [SpecialtyRow(specialty_id=i, name=f"Spec {i}") for i in range(1, n + 1)]


def _doctors(n: int) -> list[DoctorRow]:
    return [
        DoctorRow(doctor_id=i, first_name="A", last_name="B", department_id=1, specialty_id=1)
        for i in range(1, n + 1)
    ]


def _patients(n: int) -> list[PatientRow]:
    return [
        PatientRow(patient_id=i, first_name="P", last_name="Q", dob=datetime(1990, 1, 1).date())
        for i in range(1, n + 1)
    ]


def _medications(n: int) -> list[MedicationRow]:
    return [MedicationRow(medication_id=i, name=f"Med {i}") for i in range(1, n + 1)]


# --------------------------------------------------------------------------- #
# Lookup generators
# --------------------------------------------------------------------------- #
def test_departments_are_unique_and_bounded(generators: Generators) -> None:
    rows = generators.departments.generate(50)
    assert len(rows) == 50
    assert len({r.name for r in rows}) == 50
    assert all(len(r.name) <= 100 for r in rows)
    assert all(r.location is not None and len(r.location) <= 100 for r in rows)


def test_specialties_are_unique(generators: Generators) -> None:
    rows = generators.specialties.generate(40)
    assert len({r.name for r in rows}) == 40


def test_medications_are_unique_and_valid(generators: Generators) -> None:
    rows = generators.medications.generate(60)
    assert len({r.name for r in rows}) == 60
    assert all(len(r.name) <= 120 for r in rows)


# --------------------------------------------------------------------------- #
# FK generators
# --------------------------------------------------------------------------- #
def test_doctors_reference_supplied_parents(generators: Generators) -> None:
    departments = _departments(3)
    specialties = _specialties(3)
    rows = generators.doctors.generate(20, departments=departments, specialties=specialties)
    dept_ids = {d.department_id for d in departments}
    spec_ids = {s.specialty_id for s in specialties}
    assert all(r.department_id in dept_ids for r in rows)
    assert all(r.specialty_id in spec_ids for r in rows)
    assert all(len(r.first_name) <= 50 and len(r.last_name) <= 50 for r in rows)


def test_doctors_require_parents(generators: Generators) -> None:
    with pytest.raises(DependencyError):
        generators.doctors.generate(5, departments=[], specialties=_specialties(1))


def test_patients_have_unique_emails_and_valid_values(generators: Generators) -> None:
    rows = generators.patients.generate(300)
    emails = [r.email for r in rows if r.email is not None]
    assert len(emails) == len(set(emails))
    assert all(r.gender in GENDERS for r in rows)
    assert all(r.phone is not None and len(r.phone) <= 20 for r in rows)
    assert all(len(e) <= 120 for e in emails)


# --------------------------------------------------------------------------- #
# Temporal realism
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("window_days", [30, 90])
def test_appointments_respect_window_and_status(
    settings: Settings, reference_time: datetime, window_days: int
) -> None:
    scoped = settings.model_copy(update={"window_days": window_days})
    gens = build_generators(scoped, reference_time)
    rows = gens.appointments.generate(400, patients=_patients(10), doctors=_doctors(5))

    lower = reference_time - timedelta(days=window_days)
    upper = reference_time + timedelta(days=14)
    for appt in rows:
        assert lower <= appt.scheduled_at <= upper
        if appt.scheduled_at < reference_time:
            assert appt.status in PAST_STATUSES
        else:
            assert appt.status == "scheduled"
        if appt.status == "completed":
            assert appt.cost is not None
        else:
            assert appt.cost is None


def test_appointments_require_parents(generators: Generators) -> None:
    with pytest.raises(DependencyError):
        generators.appointments.generate(5, patients=[], doctors=_doctors(1))


def test_prescriptions_only_for_completed_past_appointments(
    generators: Generators, reference_time: datetime
) -> None:
    now = reference_time
    appointments = [
        AppointmentRow(
            appointment_id=1,
            patient_id=1,
            doctor_id=1,
            scheduled_at=now - timedelta(days=2),
            status="completed",
        ),
        AppointmentRow(
            appointment_id=2,
            patient_id=1,
            doctor_id=1,
            scheduled_at=now + timedelta(days=2),
            status="scheduled",
        ),
        AppointmentRow(
            appointment_id=3,
            patient_id=1,
            doctor_id=1,
            scheduled_at=now - timedelta(days=1),
            status="cancelled",
        ),
    ]
    rows = generators.prescriptions.generate(20, appointments=appointments)
    assert rows  # the one completed past appointment is eligible
    assert all(r.appointment_id == 1 for r in rows)
    for presc in rows:
        assert presc.issued_at > appointments[0].scheduled_at
        assert presc.issued_at <= now


def test_prescriptions_empty_when_no_eligible_appointments(
    generators: Generators, reference_time: datetime
) -> None:
    now = reference_time
    appointments = [
        AppointmentRow(
            appointment_id=1,
            patient_id=1,
            doctor_id=1,
            scheduled_at=now + timedelta(days=1),
            status="scheduled",
        )
    ]
    assert generators.prescriptions.generate(10, appointments=appointments) == []


def test_prescription_items_are_distinct_per_prescription(generators: Generators) -> None:
    prescriptions = [
        PrescriptionRow(prescription_id=i, appointment_id=i, issued_at=datetime(2026, 6, 1, 9))
        for i in range(1, 6)
    ]
    medications = _medications(5)
    items = generators.prescription_items.generate(
        prescriptions=prescriptions, medications=medications, max_items=4
    )
    by_prescription: dict[int, list[int]] = {}
    for item in items:
        by_prescription.setdefault(item.prescription_id, []).append(item.medication_id)
    for med_ids in by_prescription.values():
        assert len(med_ids) == len(set(med_ids))
        assert 1 <= len(med_ids) <= 4


def test_prescription_items_require_medications(generators: Generators) -> None:
    prescriptions = [
        PrescriptionRow(prescription_id=1, appointment_id=1, issued_at=datetime(2026, 6, 1, 9))
    ]
    with pytest.raises(DependencyError):
        generators.prescription_items.generate(
            prescriptions=prescriptions, medications=[], max_items=3
        )
