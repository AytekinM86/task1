"""Generator for ``specialties``."""

from __future__ import annotations

from collections.abc import Iterable

from hospital_datagen.generators.base import BaseGenerator
from hospital_datagen.generators.pools import SPECIALTY_NAMES
from hospital_datagen.generators.uniqueness import UniqueValuePool
from hospital_datagen.models import SpecialtyInsert

_NAME_MAX = 100


class SpecialtyGenerator(BaseGenerator):
    """Produces specialties with names unique within the run and the database."""

    def generate(self, n: int, *, existing_names: Iterable[str] = ()) -> list[SpecialtyInsert]:
        pool = UniqueValuePool(reserved=existing_names)
        return [self._one(i, pool) for i in range(n)]

    def _one(self, index: int, pool: UniqueValuePool) -> SpecialtyInsert:
        name = pool.next(lambda attempt: self._candidate(index, attempt))
        return SpecialtyInsert(name=self.truncate(name, _NAME_MAX))

    def _candidate(self, index: int, attempt: int) -> str:
        base = SPECIALTY_NAMES[index % len(SPECIALTY_NAMES)]
        cycle = index // len(SPECIALTY_NAMES)
        if attempt == 0 and cycle == 0:
            return base
        suffix = cycle + 1 if attempt == 0 else self._rng.randint(2, 9_999)
        return f"{base} {suffix}"
