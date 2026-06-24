"""Models for the ``prescription_items`` junction table (composite PK)."""

from __future__ import annotations

from pydantic import Field

from hospital_datagen.models.base import RowModel


class PrescriptionItemInsert(RowModel):
    """Fields produced by the generator for an INSERT.

    The primary key is the ``(prescription_id, medication_id)`` pair, so there
    is no separate surrogate key to return.
    """

    prescription_id: int
    medication_id: int
    dosage: str = Field(min_length=1, max_length=80)


class PrescriptionItemRow(PrescriptionItemInsert):
    """A persisted prescription item (PK is the column pair already present)."""
