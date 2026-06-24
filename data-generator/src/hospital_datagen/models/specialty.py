"""Models for the ``specialties`` table."""

from __future__ import annotations

from pydantic import Field

from hospital_datagen.models.base import RowModel


class SpecialtyInsert(RowModel):
    """Fields produced by the generator for an INSERT."""

    name: str = Field(min_length=1, max_length=100)


class SpecialtyRow(SpecialtyInsert):
    """A persisted specialty including its DB-assigned primary key."""

    specialty_id: int
