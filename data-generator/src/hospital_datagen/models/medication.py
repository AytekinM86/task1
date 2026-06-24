"""Models for the ``medications`` table."""

from __future__ import annotations

from pydantic import Field

from hospital_datagen.models.base import RowModel


class MedicationInsert(RowModel):
    """Fields produced by the generator for an INSERT."""

    name: str = Field(min_length=1, max_length=120)
    form: str | None = Field(default=None, max_length=40)
    strength: str | None = Field(default=None, max_length=40)


class MedicationRow(MedicationInsert):
    """A persisted medication including its DB-assigned primary key."""

    medication_id: int
