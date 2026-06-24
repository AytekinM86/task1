"""Seed orchestration.

:class:`SeedOrchestrator` wires generators and repositories together in strict
foreign-key order and runs the whole seed inside one transaction, so the
database is never left half-populated. Dependencies are injected (the two
bundles below), which lets tests substitute in-memory fakes.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from hospital_datagen.db.connection import ConnectionManager
from hospital_datagen.db.repositories import (
    AppointmentRepository,
    DepartmentRepository,
    DoctorRepository,
    MedicationRepository,
    PatientRepository,
    PrescriptionItemRepository,
    PrescriptionRepository,
    SpecialtyRepository,
)
from hospital_datagen.exceptions import DataGenError
from hospital_datagen.generators.appointment import AppointmentGenerator
from hospital_datagen.generators.department import DepartmentGenerator
from hospital_datagen.generators.doctor import DoctorGenerator
from hospital_datagen.generators.medication import MedicationGenerator
from hospital_datagen.generators.patient import PatientGenerator
from hospital_datagen.generators.prescription import PrescriptionGenerator
from hospital_datagen.generators.prescription_item import PrescriptionItemGenerator
from hospital_datagen.generators.specialty import SpecialtyGenerator

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SeedPlan:
    """How many rows to generate per entity."""

    departments: int
    specialties: int
    medications: int
    doctors: int
    patients: int
    appointments: int
    prescriptions: int
    max_items_per_prescription: int


@dataclass
class SeedResult:
    """Number of rows actually inserted per table."""

    counts: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class Repositories:
    """Bundle of every table repository."""

    departments: DepartmentRepository
    specialties: SpecialtyRepository
    medications: MedicationRepository
    doctors: DoctorRepository
    patients: PatientRepository
    appointments: AppointmentRepository
    prescriptions: PrescriptionRepository
    prescription_items: PrescriptionItemRepository


@dataclass(frozen=True)
class Generators:
    """Bundle of every entity generator."""

    departments: DepartmentGenerator
    specialties: SpecialtyGenerator
    medications: MedicationGenerator
    doctors: DoctorGenerator
    patients: PatientGenerator
    appointments: AppointmentGenerator
    prescriptions: PrescriptionGenerator
    prescription_items: PrescriptionItemGenerator


class _DryRunRollbackError(DataGenError):
    """Internal signal used to force a rollback after a dry run."""


class SeedOrchestrator:
    """Generates and inserts data for all tables in FK-dependency order."""

    def __init__(
        self,
        conn_mgr: ConnectionManager,
        repos: Repositories,
        gens: Generators,
    ) -> None:
        self._conn_mgr = conn_mgr
        self._repos = repos
        self._gens = gens

    def run(self, plan: SeedPlan, *, dry_run: bool = False) -> SeedResult:
        """Seed the database; on ``dry_run`` everything is rolled back."""
        result = SeedResult()
        try:
            with self._conn_mgr.transaction() as conn:
                # 1-3: lookup tables (no FK dependencies). Reserve names already in
                # the DB (seed rows / prior runs) so unique constraints never clash.
                departments = self._repos.departments.insert_many(
                    conn,
                    self._gens.departments.generate(
                        plan.departments,
                        existing_names=self._repos.departments.existing_values(conn, "name"),
                    ),
                )
                specialties = self._repos.specialties.insert_many(
                    conn,
                    self._gens.specialties.generate(
                        plan.specialties,
                        existing_names=self._repos.specialties.existing_values(conn, "name"),
                    ),
                )
                medications = self._repos.medications.insert_many(
                    conn,
                    self._gens.medications.generate(
                        plan.medications,
                        existing_names=self._repos.medications.existing_values(conn, "name"),
                    ),
                )

                # 4: doctors depend on departments + specialties.
                doctors = self._repos.doctors.insert_many(
                    conn,
                    self._gens.doctors.generate(
                        plan.doctors, departments=departments, specialties=specialties
                    ),
                )

                # 5: patients (independent); reserve existing emails (UNIQUE).
                patients = self._repos.patients.insert_many(
                    conn,
                    self._gens.patients.generate(
                        plan.patients,
                        existing_emails=self._repos.patients.existing_values(conn, "email"),
                    ),
                )

                # 6: appointments depend on patients + doctors.
                appointments = self._repos.appointments.insert_many(
                    conn,
                    self._gens.appointments.generate(
                        plan.appointments, patients=patients, doctors=doctors
                    ),
                )

                # 7: prescriptions depend on (completed, past) appointments.
                prescriptions = self._repos.prescriptions.insert_many(
                    conn,
                    self._gens.prescriptions.generate(
                        plan.prescriptions, appointments=appointments
                    ),
                )

                # 8: prescription items depend on prescriptions + medications.
                items = self._gens.prescription_items.generate(
                    prescriptions=prescriptions,
                    medications=medications,
                    max_items=plan.max_items_per_prescription,
                )
                inserted_items = self._repos.prescription_items.insert_many(conn, items)

                result.counts = {
                    "departments": len(departments),
                    "specialties": len(specialties),
                    "medications": len(medications),
                    "doctors": len(doctors),
                    "patients": len(patients),
                    "appointments": len(appointments),
                    "prescriptions": len(prescriptions),
                    "prescription_items": len(inserted_items),
                }

                if dry_run:
                    raise _DryRunRollbackError
        except _DryRunRollbackError:
            logger.info("dry-run complete: %s rows generated, nothing persisted", result.counts)
            return result

        logger.info("seed complete: %s", result.counts)
        return result
