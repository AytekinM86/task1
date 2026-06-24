"""Models for the ``doctors`` table."""

from __future__ import annotations

from pydantic import Field

from hospital_datagen.models.base import RowModel


class DoctorInsert(RowModel):
    """Fields produced by the generator for an INSERT."""

    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    department_id: int
    specialty_id: int


class DoctorRow(DoctorInsert):
    """A persisted doctor including its DB-assigned primary key."""

    doctor_id: int
