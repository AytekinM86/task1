"""Database connection lifecycle.

:class:`ConnectionManager` owns a single non-autocommit psycopg connection and
exposes a :meth:`transaction` context manager so the whole seed runs atomically:
commit on success, rollback (and re-raise as a domain error) on any failure.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from types import TracebackType

import psycopg

from hospital_datagen.config import Settings
from hospital_datagen.exceptions import DatabaseConnectionError, DataGenError

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Owns one psycopg connection and provides transactional scoping."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._connection: psycopg.Connection | None = None

    def connect(self) -> psycopg.Connection:
        """Open the connection if needed and return it."""
        if self._connection is None or self._connection.closed:
            try:
                self._connection = psycopg.connect(
                    self._settings.dsn,
                    autocommit=False,
                )
            except psycopg.Error as exc:
                raise DatabaseConnectionError(
                    f"could not connect to {self._settings.db_name!r} at "
                    f"{self._settings.db_host}:{self._settings.db_port}: {exc}"
                ) from exc
            logger.info(
                "connected to database name=%s host=%s port=%s",
                self._settings.db_name,
                self._settings.db_host,
                self._settings.db_port,
            )
        return self._connection

    def close(self) -> None:
        """Close the connection if it is open."""
        if self._connection is not None and not self._connection.closed:
            self._connection.close()
            logger.debug("database connection closed")
        self._connection = None

    @contextmanager
    def transaction(self) -> Iterator[psycopg.Connection]:
        """Yield the connection, committing on success or rolling back on error."""
        conn = self.connect()
        try:
            yield conn
        except DataGenError:
            conn.rollback()
            logger.error("transaction rolled back due to a data-generation error")
            raise
        except psycopg.Error as exc:
            conn.rollback()
            logger.error("transaction rolled back due to a database error: %s", exc)
            raise DataGenError(f"database transaction failed: {exc}") from exc
        else:
            conn.commit()
            logger.debug("transaction committed")

    def __enter__(self) -> ConnectionManager:
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()
