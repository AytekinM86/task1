"""Tests for the Settings configuration."""

from __future__ import annotations

import pytest

from hospital_datagen.config import Settings


def test_defaults_target_liquibase_hospital() -> None:
    settings = Settings(_env_file=None)
    assert settings.db_name == "liquibase_hospital"
    assert settings.db_host == "localhost"
    assert settings.db_port == 5432
    assert settings.window_days == 30


def test_dsn_includes_credentials_and_database() -> None:
    settings = Settings(_env_file=None)
    assert settings.dsn == "postgresql://postgres:postgres@localhost:5432/liquibase_hospital"


def test_password_is_masked_in_repr() -> None:
    settings = Settings(_env_file=None)
    assert "postgres" not in repr(settings.db_password)
    assert settings.db_password.get_secret_value() == "postgres"


def test_env_var_overrides_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATAGEN_DB_NAME", "other_db")
    monkeypatch.setenv("DATAGEN_WINDOW_DAYS", "90")
    settings = Settings(_env_file=None)
    assert settings.db_name == "other_db"
    assert settings.window_days == 90


def test_negative_window_is_rejected() -> None:
    with pytest.raises(ValueError):
        Settings(_env_file=None, window_days=0)
