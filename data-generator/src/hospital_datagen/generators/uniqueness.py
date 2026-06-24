"""Helper for producing distinct values within a single generation run."""

from __future__ import annotations

from collections.abc import Callable, Iterable

from hospital_datagen.exceptions import UniquenessExhaustedError


class UniqueValuePool:
    """Tracks values already handed out and guarantees the next is distinct.

    A candidate ``factory`` is retried up to ``max_attempts`` times; if it cannot
    produce an unseen value, :class:`UniquenessExhaustedError` is raised so the
    caller fails loudly rather than silently emitting a duplicate. The factory is
    supplied per call so callers can derive candidates from per-row context
    (e.g. a patient's own name). ``reserved`` pre-marks values that already exist
    (e.g. rows already in the database) so generated values never collide with them.
    """

    def __init__(self, max_attempts: int = 50, *, reserved: Iterable[str] = ()) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        self._max_attempts = max_attempts
        self._seen: set[str] = set(reserved)

    def next(self, factory: Callable[[int], str]) -> str:
        """Return a distinct value; ``factory`` receives the 0-based attempt index."""
        for attempt in range(self._max_attempts):
            value = factory(attempt)
            if value not in self._seen:
                self._seen.add(value)
                return value
        raise UniquenessExhaustedError(
            f"could not produce a unique value after {self._max_attempts} attempts"
        )
