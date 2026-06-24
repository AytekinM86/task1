"""Shared base for all row models and column-level type aliases."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

# Domain enums backed by the DB CHECK constraints.
Gender = Literal["M", "F", "O"]
AppointmentStatus = Literal["scheduled", "completed", "cancelled", "no_show"]

GENDERS: tuple[Gender, ...] = ("M", "F", "O")
APPOINTMENT_STATUSES: tuple[AppointmentStatus, ...] = (
    "scheduled",
    "completed",
    "cancelled",
    "no_show",
)
# Statuses a past appointment may settle into (never "scheduled").
PAST_STATUSES: tuple[AppointmentStatus, ...] = ("completed", "cancelled", "no_show")


class RowModel(BaseModel):
    """Immutable base model rejecting unknown fields and stripping whitespace."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )
