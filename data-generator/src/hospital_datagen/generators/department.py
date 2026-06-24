"""Generator for ``departments``."""

from __future__ import annotations

from collections.abc import Iterable

from hospital_datagen.generators.base import BaseGenerator
from hospital_datagen.generators.pools import DEPARTMENT_NAMES
from hospital_datagen.generators.uniqueness import UniqueValuePool
from hospital_datagen.models import DepartmentInsert

_NAME_MAX = 100
_LOCATION_MAX = 100


class DepartmentGenerator(BaseGenerator):
    """Produces departments with names unique within the run and the database."""

    def generate(self, n: int, *, existing_names: Iterable[str] = ()) -> list[DepartmentInsert]:
        pool = UniqueValuePool(reserved=existing_names)
        return [self._one(i, pool) for i in range(n)]

    def _one(self, index: int, pool: UniqueValuePool) -> DepartmentInsert:
        name = pool.next(lambda attempt: self._candidate(index, attempt))
        building = self._rng.choice("ABCD")
        floor = self._rng.randint(1, 6)
        return DepartmentInsert(
            name=self.truncate(name, _NAME_MAX),
            location=self.truncate(f"Building {building}, Floor {floor}", _LOCATION_MAX),
        )

    def _candidate(self, index: int, attempt: int) -> str:
        base = DEPARTMENT_NAMES[index % len(DEPARTMENT_NAMES)]
        cycle = index // len(DEPARTMENT_NAMES)
        if attempt == 0 and cycle == 0:
            return base
        suffix = cycle + 1 if attempt == 0 else self._rng.randint(2, 9_999)
        return f"{base} {suffix}"
