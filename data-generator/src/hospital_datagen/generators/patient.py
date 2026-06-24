"""Generator for ``patients`` (unique, name-derived emails)."""

from __future__ import annotations

from collections.abc import Iterable

from hospital_datagen.generators.base import BaseGenerator
from hospital_datagen.generators.uniqueness import UniqueValuePool
from hospital_datagen.models import GENDERS, PatientInsert

_NAME_MAX = 50
_PHONE_MAX = 20
_EMAIL_MAX = 120
_MAX_AGE = 95


class PatientGenerator(BaseGenerator):
    """Produces patients with realistic DOBs and unique emails."""

    def generate(self, n: int, *, existing_emails: Iterable[str] = ()) -> list[PatientInsert]:
        email_pool = UniqueValuePool(reserved=existing_emails)
        return [self._one(email_pool) for _ in range(n)]

    def _one(self, email_pool: UniqueValuePool) -> PatientInsert:
        first = self.truncate(self._faker.first_name(), _NAME_MAX)
        last = self.truncate(self._faker.last_name(), _NAME_MAX)
        email = email_pool.next(lambda attempt: self._email_for(first, last, attempt))
        phone = self.truncate(self._faker.numerify("+1-###-###-####"), _PHONE_MAX)
        dob = self._faker.date_of_birth(minimum_age=0, maximum_age=_MAX_AGE)
        return PatientInsert(
            first_name=first,
            last_name=last,
            dob=dob,
            gender=self._rng.choice(GENDERS),
            phone=phone,
            email=email,
        )

    def _email_for(self, first: str, last: str, attempt: int) -> str:
        stem = f"{first}.{last}".lower().replace(" ", "")
        suffix = "" if attempt == 0 else str(self._rng.randint(1, 99_999))
        return self.truncate(f"{stem}{suffix}@example.com", _EMAIL_MAX)
