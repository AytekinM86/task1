"""Models for the ``appointments`` table."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import Field

from hospital_datagen.models.base import AppointmentStatus, RowModel


class AppointmentInsert(RowModel):
    """Fields produced by the generator for an INSERT."""

    patient_id: int
    doctor_id: int
    scheduled_at: datetime
    status: AppointmentStatus = "scheduled"
    reason: str | None = Field(default=None, max_length=255)
    cost: Decimal | None = Field(default=None, max_digits=10, decimal_places=2, ge=0)


class AppointmentRow(AppointmentInsert):
    """A persisted appointment including its DB-assigned primary key."""

    appointment_id: int
