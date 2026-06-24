# Flyway + Liquibase Learning Sandbox

A self-contained playground for learning and teaching **database migration tools**.
A single PostgreSQL instance runs in Docker; **Flyway** and **Liquibase** each apply the
*same* two 3NF schemas (a **hospital** model and an **e-commerce** model) so you can
compare the two tools head-to-head.

> ⚠️ **Sandbox only.** Credentials are hardcoded (`postgres`/`postgres`) and destructive
> commands like `clean` are enabled. Never point this at anything real.

---

## Requirements
- Docker + Docker Compose v2 (`docker compose ...`)
- `make`

## Quick start
```bash
make up            # start PostgreSQL (creates the 4 databases on first boot)
make demo          # apply EVERY migration (both tools, both models) + show status
make psql DB=flyway_hospital   # poke around: \dt, then SELECT * FROM patients;
```
That's it. `make demo` is the fastest way to see everything work.

---

## How it's wired

One Postgres container hosts **four databases**, one per (tool × model), so the tools never
collide and each can be wiped independently:

| Database              | Managed by | Model      |
|-----------------------|------------|------------|
| `flyway_hospital`     | Flyway     | hospital   |
| `flyway_ecommerce`    | Flyway     | e-commerce |
| `liquibase_hospital`  | Liquibase  | hospital   |
| `liquibase_ecommerce` | Liquibase  | e-commerce |

The databases are created by [init/01-create-databases.sql](init/01-create-databases.sql),
which Postgres runs automatically the first time the data volume is initialized.

Flyway and Liquibase run as **one-shot containers** (under the Compose `tools` profile), so
`docker compose up` only starts Postgres. The `Makefile` invokes the tools with
`docker compose run --rm`.

---

## Project layout
```
docker-compose.yml          Postgres + (profiled) Flyway & Liquibase services
.env                        credentials + pinned image tags
init/                       runs once to CREATE the 4 databases
Makefile                    all the `make` commands

flyway/
  conf/<model>.conf         JDBC url + migration locations per model
  sql/<model>/              V1__, V2__, V3__ versioned + R__ repeatable migrations

liquibase/
  conf/<model>.properties   JDBC url + master changelog per model
  changelog/<model>/        db.changelog-master.yaml + v1/v2/v3 changesets (YAML)
```

Both tools follow the same staged story so the comparison is apples-to-apples:

| Step | What it does            | Flyway file              | Liquibase changeSet            |
|------|-------------------------|--------------------------|--------------------------------|
| V1   | core tables             | `V1__create_core_tables` | `*-1-*`                        |
| V2   | add a table/relationship| `V2__add_*`              | `*-2-*`                        |
| V3   | seed sample data        | `V3__seed_reference_data`| `*-3-seed`                     |
| R/view | a re-runnable view    | `R__*_view` (repeatable) | view changeSet w/ `runOnChange`|

---

## The two data models (both 3NF)

**Hospital:** `departments`, `specialties`, `doctors`, `patients`, `appointments`,
`medications`, `prescriptions`, `prescription_items` (junction).

**E-commerce:** `customers`, `addresses`, `categories` (self-referencing hierarchy),
`products`, `orders`, `order_items` (junction), `payments`.

Both avoid redundancy by pushing repeating attributes into lookup tables and resolving
many-to-many relationships with junction tables — the essence of third normal form.

---

## Command cheat sheet

Every tool command takes `MODEL=hospital` (default) or `MODEL=ecommerce`.

### Flyway
```bash
make fw-info      MODEL=hospital    # status / history of each migration
make fw-migrate   MODEL=hospital    # apply pending migrations
make fw-validate  MODEL=hospital    # checksums still match the files?
make fw-repair    MODEL=hospital    # fix history table after an edit/failure
make fw-clean     MODEL=hospital    # DROP everything in the schema
```

### Liquibase
```bash
make lb-status   MODEL=ecommerce    # which changesets are pending
make lb-update   MODEL=ecommerce    # apply pending changesets
make lb-validate MODEL=ecommerce    # validate the changelog
make lb-history  MODEL=ecommerce    # what has been applied
make lb-rollback MODEL=ecommerce COUNT=1   # undo the last N changesets
```

### Infra & combos
```bash
make up | down | reset | ps | logs
make psql DB=liquibase_hospital     # interactive SQL shell
make migrate-all                    # both tools, both models
make clean-all                      # wipe all four schemas
make demo                           # up + migrate-all + status
make help                           # list every target
```

---

## Flyway ↔ Liquibase: the same ideas, different words

| Concept                    | Flyway                          | Liquibase                                   |
|----------------------------|---------------------------------|---------------------------------------------|
| Unit of change             | a versioned SQL file `V1__…sql` | a `changeSet` (id + author)                 |
| Apply pending changes      | `migrate`                       | `update`                                    |
| Show status                | `info`                          | `status` / `history`                        |
| Bookkeeping table          | `flyway_schema_history`         | `DATABASECHANGELOG` (+ `DATABASECHANGELOGLOCK`) |
| Change format              | raw SQL                         | YAML/XML/JSON/SQL (DB-agnostic; here: YAML) |
| Re-run on edit             | `R__` repeatable migration      | `runOnChange: true`                         |
| Roll back                  | not built-in (Community)        | `rollback-count` / `rollback` (first-class) |
| Reset schema               | `clean`                         | `drop-all`                                  |
| Recover history table      | `repair`                        | `clear-checksums`                           |

**Key takeaways**
- **Flyway** is *forward-only and SQL-first*: simple, you write plain `.sql`, versions are
  immutable. Rollback isn't part of the open-source edition — you write a new migration.
- **Liquibase** is *database-agnostic and reversible*: changes are described declaratively,
  it can generate rollbacks for many change types, and the same changelog can target
  different database engines.

---

## Try it yourself (suggested lab)
1. `make up` then `make fw-migrate MODEL=hospital` — watch `V1→V2→V3→R` apply in order.
2. `make psql DB=flyway_hospital` → `\dt` (note `flyway_schema_history`), then
   `SELECT * FROM active_appointments;`.
3. `make lb-update MODEL=hospital` then `make psql DB=liquibase_hospital` → `\dt`
   (note `DATABASECHANGELOG`). Same schema, different bookkeeping.
4. **Rollback example (V4):** `make lb-update MODEL=hospital` applies
   `v4__add_appointment_billing.yaml`, which adds an `appointments.cost` column via a raw `sql`
   change with an explicit `rollback:` block. Run `make lb-rollback MODEL=hospital COUNT=1` and
   the column is dropped again (`\d appointments` confirms, and `databasechangelog` no longer
   lists `hospital-4-appointment-billing`). Re-apply with `make lb-update`. Try the equivalent in
   Flyway… and discover it has no built-in rollback. (E-commerce has the twin example,
   `v4__add_order_discount.yaml` → `orders.discount`.)
5. Edit `flyway/sql/hospital/R__active_appointments_view.sql`, re-run `make fw-migrate` —
   the repeatable migration re-applies because its checksum changed.
6. `make clean-all` then `make migrate-all` to rebuild everything from scratch.
