"""Application configuration via ``pydantic-settings``.

Resolution precedence (highest first): explicit constructor args (CLI) > env
vars > ``.env`` file > field defaults. Every env var is prefixed ``DATAGEN_``
to coexist with the repository's existing ``POSTGRES_*`` variables.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed runtime configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DATAGEN_",
        extra="ignore",
    )

    # --- Database connection ------------------------------------------------
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "liquibase_hospital"
    db_user: str = "postgres"
    db_password: SecretStr = SecretStr("postgres")

    # --- Behaviour ----------------------------------------------------------
    log_level: str = "INFO"
    batch_size: int = Field(default=500, ge=1)
    faker_seed: int | None = None
    faker_locale: str = "en_US"

    # --- Temporal window ----------------------------------------------------
    window_days: int = Field(default=30, ge=1)
    future_appointment_ratio: float = Field(default=0.1, ge=0.0, le=1.0)
    # Injectable "now". Defaults to the real current time when not supplied,
    # but can be pinned in tests for deterministic temporal assertions.
    reference_time: datetime | None = None

    # --- Default row counts (overridable by the CLI) ------------------------
    n_departments: int = Field(default=5, ge=0)
    n_specialties: int = Field(default=8, ge=0)
    n_medications: int = Field(default=30, ge=0)
    n_doctors: int = Field(default=20, ge=0)
    n_patients: int = Field(default=200, ge=0)
    n_appointments: int = Field(default=500, ge=0)
    n_prescriptions: int = Field(default=150, ge=0)
    max_items_per_prescription: int = Field(default=4, ge=1)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def dsn(self) -> str:
        """PostgreSQL connection string (password resolved at access time)."""
        password = self.db_password.get_secret_value()
        return (
            f"postgresql://{self.db_user}:{password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
