"""Generator for ``prescriptions`` (only for completed past appointments)."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import timedelta

from hospital_datagen.generators.base import BaseGenerator
from hospital_datagen.models import AppointmentRow, PrescriptionInsert

_MIN_DELAY_SECONDS = 300  # 5 minutes after the appointment
_MAX_DELAY_SECONDS = 6 * 3_600  # up to 6 hours after


class PrescriptionGenerator(BaseGenerator):
    """Issues prescriptions tied to completed past appointments.

    ``issued_at`` is always after the appointment's ``scheduled_at`` and never in
    the future (clamped to the reference time).
    """

    def generate(
        self, n: int, *, appointments: Sequence[AppointmentRow]
    ) -> list[PrescriptionInsert]:
        eligible = [
            appt
            for appt in appointments
            if appt.status == "completed" and appt.scheduled_at <= self._now
        ]
        if not eligible:
            return []
        return [self._one(self._rng.choice(eligible)) for _ in range(n)]

    def _one(self, appointment: AppointmentRow) -> PrescriptionInsert:
        delay = self._rng.randint(_MIN_DELAY_SECONDS, _MAX_DELAY_SECONDS)
        issued_at = min(appointment.scheduled_at + timedelta(seconds=delay), self._now)
        return PrescriptionInsert(
            appointment_id=appointment.appointment_id,
            issued_at=issued_at,
        )
