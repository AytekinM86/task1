"""Generator for ``appointments`` — owns the temporal-realism logic.

``scheduled_at`` is spread across ``[now - window_days, now + future_tail]``.
Status is consistent with time: past appointments settle into completed /
cancelled / no_show (weighted toward completed), future ones stay scheduled.
``cost`` is billed only for completed appointments. All time math uses the
injected reference time — never a hidden ``datetime.now()``.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import timedelta
from decimal import Decimal

from hospital_datagen.exceptions import DependencyError
from hospital_datagen.generators.base import BaseGenerator
from hospital_datagen.generators.pools import APPOINTMENT_REASONS
from hospital_datagen.models import (
    PAST_STATUSES,
    AppointmentInsert,
    AppointmentStatus,
    DoctorRow,
    PatientRow,
)

_REASON_MAX = 255
_FUTURE_TAIL_DAYS = 14
_PAST_STATUS_WEIGHTS = (0.7, 0.15, 0.15)  # completed, cancelled, no_show
_MIN_COST_CENTS = 5_000
_MAX_COST_CENTS = 150_000


class AppointmentGenerator(BaseGenerator):
    """Produces time-consistent appointments referencing patients and doctors."""

    def generate(
        self,
        n: int,
        *,
        patients: Sequence[PatientRow],
        doctors: Sequence[DoctorRow],
    ) -> list[AppointmentInsert]:
        if n > 0 and (not patients or not doctors):
            raise DependencyError("cannot generate appointments without patients and doctors")
        return [self._one(patients, doctors) for _ in range(n)]

    def _one(
        self,
        patients: Sequence[PatientRow],
        doctors: Sequence[DoctorRow],
    ) -> AppointmentInsert:
        is_future = self._rng.random() < self._settings.future_appointment_ratio
        if is_future:
            offset = self._rng.randint(60, _FUTURE_TAIL_DAYS * 86_400)
            scheduled_at = self._now + timedelta(seconds=offset)
            status: AppointmentStatus = "scheduled"
        else:
            offset = self._rng.randint(60, self._settings.window_days * 86_400)
            scheduled_at = self._now - timedelta(seconds=offset)
            status = self._rng.choices(PAST_STATUSES, weights=_PAST_STATUS_WEIGHTS, k=1)[0]

        return AppointmentInsert(
            patient_id=self._rng.choice(patients).patient_id,
            doctor_id=self._rng.choice(doctors).doctor_id,
            scheduled_at=scheduled_at,
            status=status,
            reason=self.truncate(self._rng.choice(APPOINTMENT_REASONS), _REASON_MAX),
            cost=self._cost() if status == "completed" else None,
        )

    def _cost(self) -> Decimal:
        cents = self._rng.randint(_MIN_COST_CENTS, _MAX_COST_CENTS)
        return Decimal(cents) / Decimal(100)
