"""Per-table repositories.

Repositories know SQL; they do not know Faker. They never open their own
connection — the caller passes one in — which keeps them transaction-friendly
and trivially testable. All statements are parameterised; identifiers are
composed with :mod:`psycopg.sql` so nothing is interpolated by hand.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Any, ClassVar, Generic, TypeVar

import psycopg
from psycopg import sql

from hospital_datagen.exceptions import DuplicateValueError, InsertError
from hospital_datagen.models import (
    AppointmentInsert,
    AppointmentRow,
    DepartmentInsert,
    DepartmentRow,
    DoctorInsert,
    DoctorRow,
    MedicationInsert,
    MedicationRow,
    PatientInsert,
    PatientRow,
    PrescriptionInsert,
    PrescriptionItemInsert,
    PrescriptionItemRow,
    PrescriptionRow,
    RowModel,
    SpecialtyInsert,
    SpecialtyRow,
)

logger = logging.getLogger(__name__)

TInsert = TypeVar("TInsert", bound=RowModel)
TRow = TypeVar("TRow", bound=RowModel)


class BaseRepository(Generic[TInsert, TRow]):
    """Generic INSERT ... RETURNING repository for one table."""

    table: ClassVar[str]
    insert_columns: ClassVar[tuple[str, ...]]
    returning_columns: ClassVar[tuple[str, ...]]
    row_model: type[TRow]

    def __init__(self, batch_size: int = 500) -> None:
        if batch_size < 1:
            raise ValueError("batch_size must be >= 1")
        self._batch_size = batch_size

    # -- SQL helpers -------------------------------------------------------- #
    def _values_clause(self, count: int) -> sql.Composed:
        placeholders = sql.SQL("({})").format(
            sql.SQL(", ").join(sql.Placeholder() * len(self.insert_columns))
        )
        return sql.SQL(", ").join([placeholders] * count)

    def _insert_sql(self, count: int) -> sql.Composed:
        statement = sql.SQL("INSERT INTO {table} ({cols}) VALUES {values}").format(
            table=sql.Identifier(self.table),
            cols=sql.SQL(", ").join(sql.Identifier(c) for c in self.insert_columns),
            values=self._values_clause(count),
        )
        if self.returning_columns:
            statement += sql.SQL(" RETURNING {ret}").format(
                ret=sql.SQL(", ").join(sql.Identifier(c) for c in self.returning_columns)
            )
        return statement

    def _params(self, item: TInsert) -> list[Any]:
        return [getattr(item, column) for column in self.insert_columns]

    def _build_row(self, item: TInsert, returned: dict[str, Any]) -> TRow:
        return self.row_model(**{**item.model_dump(), **returned})

    # -- Public API --------------------------------------------------------- #
    def existing_values(self, conn: psycopg.Connection, column: str) -> set[str]:
        """Return the current set of values in ``column`` (for unique columns).

        Used to reserve values already present (seed rows, prior runs) so newly
        generated unique values never collide with them.
        """
        if column not in self.insert_columns:
            raise ValueError(f"{column!r} is not an insertable column of {self.table!r}")
        statement = sql.SQL("SELECT {col} FROM {table} WHERE {col} IS NOT NULL").format(
            col=sql.Identifier(column),
            table=sql.Identifier(self.table),
        )
        try:
            with conn.cursor() as cur:
                cur.execute(statement)
                return {str(row[0]) for row in cur.fetchall()}
        except psycopg.Error as exc:
            raise InsertError(self.table, str(exc).strip()) from exc

    def insert(self, conn: psycopg.Connection, item: TInsert) -> TRow:
        """Insert a single row and return the persisted model."""
        return self.insert_many(conn, [item])[0]

    def insert_many(self, conn: psycopg.Connection, items: Sequence[TInsert]) -> list[TRow]:
        """Insert rows in batches, returning the persisted models in order."""
        rows: list[TRow] = []
        for start in range(0, len(items), self._batch_size):
            batch = items[start : start + self._batch_size]
            rows.extend(self._insert_batch(conn, batch))
        if rows:
            logger.info("inserted %d row(s) into %s", len(rows), self.table)
        return rows

    def _insert_batch(self, conn: psycopg.Connection, batch: Sequence[TInsert]) -> list[TRow]:
        params: list[Any] = []
        for item in batch:
            params.extend(self._params(item))
        statement = self._insert_sql(len(batch))
        try:
            with conn.cursor() as cur:
                cur.execute(statement, params)
                rows = cur.fetchall() if self.returning_columns else []
        except psycopg.errors.UniqueViolation as exc:
            raise DuplicateValueError(self.table, str(exc).strip()) from exc
        except psycopg.Error as exc:
            raise InsertError(self.table, str(exc).strip()) from exc

        if not self.returning_columns:
            return [self._build_row(item, {}) for item in batch]
        return [
            self._build_row(item, dict(zip(self.returning_columns, row, strict=True)))
            for item, row in zip(batch, rows, strict=True)
        ]


class DepartmentRepository(BaseRepository[DepartmentInsert, DepartmentRow]):
    table = "departments"
    insert_columns = ("name", "location")
    returning_columns = ("department_id",)
    row_model = DepartmentRow


class SpecialtyRepository(BaseRepository[SpecialtyInsert, SpecialtyRow]):
    table = "specialties"
    insert_columns = ("name",)
    returning_columns = ("specialty_id",)
    row_model = SpecialtyRow


class MedicationRepository(BaseRepository[MedicationInsert, MedicationRow]):
    table = "medications"
    insert_columns = ("name", "form", "strength")
    returning_columns = ("medication_id",)
    row_model = MedicationRow


class DoctorRepository(BaseRepository[DoctorInsert, DoctorRow]):
    table = "doctors"
    insert_columns = ("first_name", "last_name", "department_id", "specialty_id")
    returning_columns = ("doctor_id",)
    row_model = DoctorRow


class PatientRepository(BaseRepository[PatientInsert, PatientRow]):
    table = "patients"
    insert_columns = ("first_name", "last_name", "dob", "gender", "phone", "email")
    returning_columns = ("patient_id",)
    row_model = PatientRow


class AppointmentRepository(BaseRepository[AppointmentInsert, AppointmentRow]):
    table = "appointments"
    insert_columns = ("patient_id", "doctor_id", "scheduled_at", "status", "reason", "cost")
    returning_columns = ("appointment_id",)
    row_model = AppointmentRow


class PrescriptionRepository(BaseRepository[PrescriptionInsert, PrescriptionRow]):
    table = "prescriptions"
    insert_columns = ("appointment_id", "issued_at")
    returning_columns = ("prescription_id",)
    row_model = PrescriptionRow


class PrescriptionItemRepository(BaseRepository[PrescriptionItemInsert, PrescriptionItemRow]):
    table = "prescription_items"
    insert_columns = ("prescription_id", "medication_id", "dosage")
    # Composite PK; RETURNING the pair confirms the write without a surrogate key.
    returning_columns = ("prescription_id", "medication_id")
    row_model = PrescriptionItemRow
