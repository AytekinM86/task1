"""Models for the ``prescriptions`` table."""

from __future__ import annotations

from datetime import datetime

from hospital_datagen.models.base import RowModel


class PrescriptionInsert(RowModel):
    """Fields produced by the generator for an INSERT.

    ``issued_at`` is always supplied explicitly so the timestamp is realistic
    (tied to the appointment) rather than relying on the DB ``now()`` default.
    """

    appointment_id: int
    issued_at: datetime


class PrescriptionRow(PrescriptionInsert):
    """A persisted prescription including its DB-assigned primary key."""

    prescription_id: int
