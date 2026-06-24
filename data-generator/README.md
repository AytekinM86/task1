# Hospital data generator

A best-practices Python app that populates the `liquibase_hospital` PostgreSQL
schema with realistic, internally-consistent fake data. Built with Poetry,
Pydantic v2, psycopg3, Faker, mypy (strict), ruff, and pytest.

## What it does

- Connects directly to Postgres and inserts rows in correct foreign-key order,
  inside a **single transaction** (all-or-nothing).
- Respects every constraint: `VARCHAR` lengths, `gender`/`status` CHECKs,
  unique `email`/`name`, and the composite PK on `prescription_items`.
- Never assumes IDs — it uses `INSERT ... RETURNING`, so it coexists with the
  three hand-written seed rows already in the schema.
- Generates **realistic timestamps** over a configurable window (last 30 or 90
  days): past appointments are `completed`/`cancelled`/`no_show`, future ones
  stay `scheduled`, and prescriptions are issued only for completed past
  appointments (`issued_at` after the appointment, never in the future).

## Prerequisites

The target database is the repository's Docker Postgres. From the repo root:

```bash
make up                      # start Postgres
make lb-update MODEL=hospital  # apply the hospital schema (incl. appointments.cost)
```

## Run on the host

```bash
cd data-generator
make install                 # poetry install
make run-dry                 # generate + validate against the live schema, roll back
make run                     # seed with defaults
poetry run hospital-datagen seed --last-90-days --patients 500 --appointments 1200
```

Configuration is read from env vars / `.env` (see `.env.example`); CLI flags
override both. Defaults target `localhost:5432/liquibase_hospital`.

## Run via Docker

From the repo root (the `datagen` compose service is on the same network as
Postgres):

```bash
make datagen-build
make datagen ARGS="seed --last-30-days"
make datagen ARGS="seed --last-90-days --dry-run"
```

## Development

```bash
make check      # ruff lint + format-check + mypy strict + unit tests
make test       # unit tests only (no DB)
make test-int   # integration tests (needs Postgres up)
```

## Layout

```
src/hospital_datagen/
  config.py          pydantic-settings configuration
  logging_config.py  stdout structured logging
  exceptions.py      DataGenError hierarchy
  cli.py             Typer `seed` command
  models/            Pydantic Insert/Row models per table
  db/                ConnectionManager + repositories (INSERT ... RETURNING)
  generators/        Faker-backed generators + temporal logic + uniqueness
  orchestrator.py    FK-ordered, single-transaction seeding
tests/
  unit/              no DB required
  integration/       real DB, every test rolled back
```
