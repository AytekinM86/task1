"""Custom exception hierarchy for the data generator.

A single base (:class:`DataGenError`) lets the CLI catch every domain error in
one place and map error categories to distinct process exit codes, while still
preserving the original cause via ``raise ... from`` at each translation point.
"""

from __future__ import annotations


class DataGenError(Exception):
    """Base class for every error raised by this application."""


class ConfigError(DataGenError):
    """Configuration is missing or invalid."""


# --------------------------------------------------------------------------- #
# Database errors
# --------------------------------------------------------------------------- #
class DatabaseError(DataGenError):
    """Base class for database-related failures."""


class DatabaseConnectionError(DatabaseError):
    """Could not connect to or authenticate against the database."""


class InsertError(DatabaseError):
    """An ``INSERT`` failed for a specific table."""

    def __init__(self, table: str, message: str) -> None:
        self.table = table
        super().__init__(f"insert into {table!r} failed: {message}")


class DuplicateValueError(DatabaseError):
    """A unique constraint was violated (e.g. duplicate email or name)."""

    def __init__(self, table: str, message: str) -> None:
        self.table = table
        super().__init__(f"duplicate value for {table!r}: {message}")


# --------------------------------------------------------------------------- #
# Generation errors
# --------------------------------------------------------------------------- #
class GenerationError(DataGenError):
    """Base class for fake-data generation failures."""


class UniquenessExhaustedError(GenerationError):
    """A unique-value pool could not produce another distinct value."""


class DependencyError(DataGenError):
    """A child entity was requested without the parent rows it depends on."""
