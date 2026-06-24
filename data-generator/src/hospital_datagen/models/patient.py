"""Models for the ``patients`` table."""

from __future__ import annotations

from datetime import date

from pydantic import Field

from hospital_datagen.models.base import Gender, RowModel


class PatientInsert(RowModel):
    """Fields produced by the generator for an INSERT."""

    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    dob: date
    gender: Gender | None = None
    phone: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=120)


class PatientRow(PatientInsert):
    """A persisted patient including its DB-assigned primary key."""

    patient_id: int
