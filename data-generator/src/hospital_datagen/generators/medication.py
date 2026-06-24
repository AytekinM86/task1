"""Generator for ``medications``."""

from __future__ import annotations

from collections.abc import Iterable

from hospital_datagen.generators.base import BaseGenerator
from hospital_datagen.generators.pools import (
    MEDICATION_FORMS,
    MEDICATION_NAMES,
    MEDICATION_STRENGTHS,
)
from hospital_datagen.generators.uniqueness import UniqueValuePool
from hospital_datagen.models import MedicationInsert

_NAME_MAX = 120
_FORM_MAX = 40
_STRENGTH_MAX = 40


class MedicationGenerator(BaseGenerator):
    """Produces medications with names unique within the run and the database."""

    def generate(self, n: int, *, existing_names: Iterable[str] = ()) -> list[MedicationInsert]:
        pool = UniqueValuePool(reserved=existing_names)
        return [self._one(i, pool) for i in range(n)]

    def _one(self, index: int, pool: UniqueValuePool) -> MedicationInsert:
        name = pool.next(lambda attempt: self._candidate(index, attempt))
        return MedicationInsert(
            name=self.truncate(name, _NAME_MAX),
            form=self.truncate(self._rng.choice(MEDICATION_FORMS), _FORM_MAX),
            strength=self.truncate(self._rng.choice(MEDICATION_STRENGTHS), _STRENGTH_MAX),
        )

    def _candidate(self, index: int, attempt: int) -> str:
        base = MEDICATION_NAMES[index % len(MEDICATION_NAMES)]
        cycle = index // len(MEDICATION_NAMES)
        if attempt == 0 and cycle == 0:
            return base
        suffix = cycle + 1 if attempt == 0 else self._rng.randint(2, 9_999)
        return f"{base} {suffix}"
