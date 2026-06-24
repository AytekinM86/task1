"""Pydantic row models for the hospital schema."""

from __future__ import annotations

from hospital_datagen.models.appointment import AppointmentInsert, AppointmentRow
from hospital_datagen.models.base import (
    APPOINTMENT_STATUSES,
    GENDERS,
    PAST_STATUSES,
    AppointmentStatus,
    Gender,
    RowModel,
)
from hospital_datagen.models.department import DepartmentInsert, DepartmentRow
from hospital_datagen.models.doctor import DoctorInsert, DoctorRow
from hospital_datagen.models.medication import MedicationInsert, MedicationRow
from hospital_datagen.models.patient import PatientInsert, PatientRow
from hospital_datagen.models.prescription import PrescriptionInsert, PrescriptionRow
from hospital_datagen.models.prescription_item import (
    PrescriptionItemInsert,
    PrescriptionItemRow,
)
from hospital_datagen.models.specialty import SpecialtyInsert, SpecialtyRow

__all__ = [
    "APPOINTMENT_STATUSES",
    "GENDERS",
    "PAST_STATUSES",
    "AppointmentInsert",
    "AppointmentRow",
    "AppointmentStatus",
    "DepartmentInsert",
    "DepartmentRow",
    "DoctorInsert",
    "DoctorRow",
    "Gender",
    "MedicationInsert",
    "MedicationRow",
    "PatientInsert",
    "PatientRow",
    "PrescriptionInsert",
    "PrescriptionItemInsert",
    "PrescriptionItemRow",
    "PrescriptionRow",
    "RowModel",
    "SpecialtyInsert",
    "SpecialtyRow",
]
