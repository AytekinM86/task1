"""Generator for ``doctors`` (depends on departments and specialties)."""

from __future__ import annotations

from collections.abc import Sequence

from hospital_datagen.exceptions import DependencyError
from hospital_datagen.generators.base import BaseGenerator
from hospital_datagen.models import DepartmentRow, DoctorInsert, SpecialtyRow

_NAME_MAX = 50


class DoctorGenerator(BaseGenerator):
    """Produces doctors referencing existing departments and specialties."""

    def generate(
        self,
        n: int,
        *,
        departments: Sequence[DepartmentRow],
        specialties: Sequence[SpecialtyRow],
    ) -> list[DoctorInsert]:
        if n > 0 and (not departments or not specialties):
            raise DependencyError("cannot generate doctors without departments and specialties")
        return [self._one(departments, specialties) for _ in range(n)]

    def _one(
        self,
        departments: Sequence[DepartmentRow],
        specialties: Sequence[SpecialtyRow],
    ) -> DoctorInsert:
        return DoctorInsert(
            first_name=self.truncate(self._faker.first_name(), _NAME_MAX),
            last_name=self.truncate(self._faker.last_name(), _NAME_MAX),
            department_id=self._rng.choice(departments).department_id,
            specialty_id=self._rng.choice(specialties).specialty_id,
        )
