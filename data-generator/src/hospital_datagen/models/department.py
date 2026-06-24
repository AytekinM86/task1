"""Models for the ``departments`` table."""

from __future__ import annotations

from pydantic import Field

from hospital_datagen.models.base import RowModel


class DepartmentInsert(RowModel):
    """Fields produced by the generator for an INSERT."""

    name: str = Field(min_length=1, max_length=100)
    location: str | None = Field(default=None, max_length=100)


class DepartmentRow(DepartmentInsert):
    """A persisted department including its DB-assigned primary key."""

    department_id: int
