"""Tests for the UniqueValuePool helper."""

from __future__ import annotations

import pytest

from hospital_datagen.exceptions import UniquenessExhaustedError
from hospital_datagen.generators.uniqueness import UniqueValuePool


def test_returns_distinct_values() -> None:
    pool = UniqueValuePool()
    counter = {"n": 0}

    def factory(_attempt: int) -> str:
        counter["n"] += 1
        return f"value-{counter['n']}"

    values = {pool.next(factory) for _ in range(100)}
    assert len(values) == 100


def test_raises_when_factory_cannot_produce_unique() -> None:
    pool = UniqueValuePool(max_attempts=5)
    pool.next(lambda _attempt: "constant")
    with pytest.raises(UniquenessExhaustedError):
        pool.next(lambda _attempt: "constant")
