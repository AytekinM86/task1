"""Command-line interface (Typer).

Builds effective settings from flags, configures logging, wires the
orchestrator, and runs the seed — mapping domain errors to distinct exit codes.
"""

import logging
from typing import Annotated

import typer

from hospital_datagen.config import Settings
from hospital_datagen.db.connection import ConnectionManager
from hospital_datagen.exceptions import (
    ConfigError,
    DatabaseError,
    DataGenError,
    DependencyError,
    GenerationError,
)
from hospital_datagen.factory import build_orchestrator
from hospital_datagen.logging_config import configure_logging
from hospital_datagen.orchestrator import SeedPlan

logger = logging.getLogger(__name__)

app = typer.Typer(add_completion=False, help="Seed the hospital database with fake data.")


@app.callback()
def main() -> None:
    """Hospital fake-data generator (keeps the ``seed`` subcommand explicit)."""


# Exit codes by error category.
_EXIT_CONFIG = 2
_EXIT_DATABASE = 3
_EXIT_GENERATION = 4
_EXIT_DEPENDENCY = 5
_EXIT_GENERIC = 1


def _resolve_window(
    window_days: int | None, last_30_days: bool, last_90_days: bool, default: int
) -> int:
    if last_90_days:
        return 90
    if last_30_days:
        return 30
    if window_days is not None:
        return window_days
    return default


@app.command()
def seed(  # noqa: PLR0913 - each option is a distinct, documented knob
    departments: Annotated[int | None, typer.Option(help="Number of departments.")] = None,
    specialties: Annotated[int | None, typer.Option(help="Number of specialties.")] = None,
    medications: Annotated[int | None, typer.Option(help="Number of medications.")] = None,
    doctors: Annotated[int | None, typer.Option(help="Number of doctors.")] = None,
    patients: Annotated[int | None, typer.Option(help="Number of patients.")] = None,
    appointments: Annotated[int | None, typer.Option(help="Number of appointments.")] = None,
    prescriptions: Annotated[int | None, typer.Option(help="Number of prescriptions.")] = None,
    max_items_per_prescription: Annotated[
        int | None, typer.Option(help="Max medications per prescription.")
    ] = None,
    window_days: Annotated[
        int | None, typer.Option(help="Span of generated data, in days back from now.")
    ] = None,
    last_30_days: Annotated[bool, typer.Option(help="Shortcut for --window-days 30.")] = False,
    last_90_days: Annotated[bool, typer.Option(help="Shortcut for --window-days 90.")] = False,
    faker_seed: Annotated[int | None, typer.Option(help="Seed for reproducible fake data.")] = None,
    log_level: Annotated[str, typer.Option(help="Logging level.")] = "INFO",
    dry_run: Annotated[
        bool, typer.Option(help="Generate and validate, then roll back (insert nothing).")
    ] = False,
) -> None:
    """Generate and insert fake data into the hospital database."""
    configure_logging(log_level)

    try:
        base = Settings()
    except Exception as exc:  # pydantic validation / env errors
        raise typer.Exit(code=_EXIT_CONFIG) from _log_and_return(
            ConfigError(f"invalid configuration: {exc}")
        )

    settings = base.model_copy(
        update={
            "log_level": log_level,
            "window_days": _resolve_window(
                window_days, last_30_days, last_90_days, base.window_days
            ),
            "faker_seed": faker_seed if faker_seed is not None else base.faker_seed,
        }
    )

    plan = SeedPlan(
        departments=_pick(departments, base.n_departments),
        specialties=_pick(specialties, base.n_specialties),
        medications=_pick(medications, base.n_medications),
        doctors=_pick(doctors, base.n_doctors),
        patients=_pick(patients, base.n_patients),
        appointments=_pick(appointments, base.n_appointments),
        prescriptions=_pick(prescriptions, base.n_prescriptions),
        max_items_per_prescription=_pick(
            max_items_per_prescription, base.max_items_per_prescription
        ),
    )

    try:
        with ConnectionManager(settings) as conn_mgr:
            orchestrator = build_orchestrator(settings, conn_mgr)
            result = orchestrator.run(plan, dry_run=dry_run)
    except DependencyError as exc:
        raise typer.Exit(code=_EXIT_DEPENDENCY) from _log_and_return(exc)
    except GenerationError as exc:
        raise typer.Exit(code=_EXIT_GENERATION) from _log_and_return(exc)
    except DatabaseError as exc:
        raise typer.Exit(code=_EXIT_DATABASE) from _log_and_return(exc)
    except DataGenError as exc:
        raise typer.Exit(code=_EXIT_GENERIC) from _log_and_return(exc)

    typer.echo(f"{'Dry run' if dry_run else 'Seed'} complete: {result.counts}")


def _pick(override: int | None, default: int) -> int:
    return override if override is not None else default


def _log_and_return(exc: DataGenError) -> DataGenError:
    logger.error("%s: %s", type(exc).__name__, exc)
    return exc


if __name__ == "__main__":
    app()
