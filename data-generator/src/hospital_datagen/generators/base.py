"""Shared state for all generators.

Every generator is constructed with the *same* seeded :class:`Faker` and
:class:`random.Random` instances and a single, concrete ``reference_time`` so a
full run is deterministic for a given seed and the temporal logic never reaches
for a hidden ``datetime.now()``.
"""

from __future__ import annotations

import random
from datetime import datetime

from faker import Faker

from hospital_datagen.config import Settings


class BaseGenerator:
    """Holds the seeded Faker/RNG and the run's reference time."""

    def __init__(
        self,
        faker: Faker,
        rng: random.Random,
        settings: Settings,
        reference_time: datetime,
    ) -> None:
        self._faker = faker
        self._rng = rng
        self._settings = settings
        self._now = reference_time

    @staticmethod
    def truncate(value: str, max_length: int) -> str:
        """Trim a string to fit a column, preserving meaningful content."""
        return value if len(value) <= max_length else value[:max_length].rstrip()
