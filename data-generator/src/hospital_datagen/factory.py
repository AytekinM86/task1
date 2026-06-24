"""Dependency-injection wiring.

Builds the seeded Faker/RNG, the generator and repository bundles, and a fully
constructed :class:`SeedOrchestrator` from a :class:`Settings`. Keeping all
construction here makes the CLI thin and lets tests build pieces in isolation.
"""

from __future__ import annotations

import random
from datetime import UTC, datetime

from faker import Faker

from hospital_datagen.config import Settings
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
from hospital_datagen.generators.appointment import AppointmentGenerator
from hospital_datagen.generators.department import DepartmentGenerator
from hospital_datagen.generators.doctor import DoctorGenerator
from hospital_datagen.generators.medication import MedicationGenerator
from hospital_datagen.generators.patient import PatientGenerator
from hospital_datagen.generators.prescription import PrescriptionGenerator
from hospital_datagen.generators.prescription_item import PrescriptionItemGenerator
from hospital_datagen.generators.specialty import SpecialtyGenerator
from hospital_datagen.orchestrator import (
    Generators,
    Repositories,
    SeedOrchestrator,
    SeedPlan,
)


def resolve_reference_time(settings: Settings) -> datetime:
    """Return the run's reference 'now' as a naive UTC timestamp.

    The schema's TIMESTAMP columns are timezone-naive; standardising on UTC keeps
    generated timestamps consistent with the database's ``now()`` regardless of the
    host's local timezone. A pinned ``reference_time`` (tests) is used verbatim.
    """
    if settings.reference_time is not None:
        return settings.reference_time
    return datetime.now(UTC).replace(tzinfo=None)


def build_generators(settings: Settings, reference_time: datetime) -> Generators:
    """Construct every generator sharing one seeded Faker and RNG."""
    faker = Faker(settings.faker_locale)
    rng = random.Random(settings.faker_seed)
    if settings.faker_seed is not None:
        faker.seed_instance(settings.faker_seed)

    args = (faker, rng, settings, reference_time)
    return Generators(
        departments=DepartmentGenerator(*args),
        specialties=SpecialtyGenerator(*args),
        medications=MedicationGenerator(*args),
        doctors=DoctorGenerator(*args),
        patients=PatientGenerator(*args),
        appointments=AppointmentGenerator(*args),
        prescriptions=PrescriptionGenerator(*args),
        prescription_items=PrescriptionItemGenerator(*args),
    )


def build_repositories(settings: Settings) -> Repositories:
    """Construct every repository with the configured batch size."""
    batch = settings.batch_size
    return Repositories(
        departments=DepartmentRepository(batch),
        specialties=SpecialtyRepository(batch),
        medications=MedicationRepository(batch),
        doctors=DoctorRepository(batch),
        patients=PatientRepository(batch),
        appointments=AppointmentRepository(batch),
        prescriptions=PrescriptionRepository(batch),
        prescription_items=PrescriptionItemRepository(batch),
    )


def build_orchestrator(settings: Settings, conn_mgr: ConnectionManager) -> SeedOrchestrator:
    """Build a ready-to-run orchestrator from settings and a connection manager."""
    reference_time = resolve_reference_time(settings)
    return SeedOrchestrator(
        conn_mgr=conn_mgr,
        repos=build_repositories(settings),
        gens=build_generators(settings, reference_time),
    )


def plan_from_settings(settings: Settings) -> SeedPlan:
    """Derive a :class:`SeedPlan` from the configured default counts."""
    return SeedPlan(
        departments=settings.n_departments,
        specialties=settings.n_specialties,
        medications=settings.n_medications,
        doctors=settings.n_doctors,
        patients=settings.n_patients,
        appointments=settings.n_appointments,
        prescriptions=settings.n_prescriptions,
        max_items_per_prescription=settings.max_items_per_prescription,
    )
