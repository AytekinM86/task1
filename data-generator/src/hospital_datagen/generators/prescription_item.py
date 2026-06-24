"""Generator for ``prescription_items`` (composite-PK safe)."""

from __future__ import annotations

from collections.abc import Sequence

from hospital_datagen.exceptions import DependencyError
from hospital_datagen.generators.base import BaseGenerator
from hospital_datagen.generators.pools import DOSAGE_PATTERNS
from hospital_datagen.models import (
    MedicationRow,
    PrescriptionItemInsert,
    PrescriptionRow,
)

_DOSAGE_MAX = 80


class PrescriptionItemGenerator(BaseGenerator):
    """Attaches 1..max_items distinct medications to each prescription.

    Medications are sampled without replacement per prescription, so the
    ``(prescription_id, medication_id)`` composite primary key never collides.
    """

    def generate(
        self,
        *,
        prescriptions: Sequence[PrescriptionRow],
        medications: Sequence[MedicationRow],
        max_items: int,
    ) -> list[PrescriptionItemInsert]:
        if prescriptions and not medications:
            raise DependencyError("cannot generate prescription items without medications")
        items: list[PrescriptionItemInsert] = []
        ceiling = min(max_items, len(medications))
        for prescription in prescriptions:
            count = self._rng.randint(1, ceiling)
            for medication in self._rng.sample(list(medications), count):
                items.append(
                    PrescriptionItemInsert(
                        prescription_id=prescription.prescription_id,
                        medication_id=medication.medication_id,
                        dosage=self.truncate(self._rng.choice(DOSAGE_PATTERNS), _DOSAGE_MAX),
                    )
                )
        return items
