# Schema Management: With and Without Liquibase

## What is schema management?

**Database schema management** (also called *database change management* or *migrations*) is
the practice of evolving a database's structure — tables, columns, indexes, constraints, views,
stored procedures, and reference data — in a controlled, repeatable, and auditable way.

The core problem it solves: an application's database changes constantly over its lifetime, and
those changes must be applied **consistently** across every environment (a developer's laptop,
CI, staging, production) and by **every team member**, in the **same order**, without anyone
losing track of what has already been applied. Done badly, schemas *drift* apart, deployments
break, and "it works on my machine" becomes a database problem.

Every approach to schema management — tool or no tool — ultimately has to answer the same three
questions:

1. **What changes exist?** (the change scripts / definitions)
2. **In what order are they applied?** (ordering / versioning)
3. **Which changes have already run on this database?** (tracking / state)

---

## Schema management WITHOUT Liquibase

You do not strictly need a dedicated tool to manage a schema. Below are the common
tool-free (or lighter-tooling) approaches, from least to most disciplined.

### 1. Manual / ad-hoc SQL

A DBA or developer writes `CREATE` / `ALTER` / `DROP` statements and runs them by hand against
each database (via a SQL client, `psql`, etc.).

**Pros**
- Dead simple — no tooling, no learning curve.
- Full, direct control over the exact SQL executed.
- Fine for one-off scripts, spikes, or throwaway databases.

**Cons**
- **No history** of what was applied, when, or by whom.
- **Schema drift** — environments silently diverge.
- **Error-prone** — easy to forget a step, run a script twice, or skip one.
- **No rollback** strategy beyond "remember what you did and undo it manually."
- Hard to reproduce a known-good schema from scratch.

### 2. Versioned SQL scripts in source control

Changes are written as ordered, immutable files — for example `V1__create_users.sql`,
`V2__add_orders.sql`, `V3__add_index.sql` — checked into version control and applied in order.
Application is often done by a small homegrown runner script, a CI step, or a lightweight
migration tool.

**Pros**
- **Auditable** — every change is a reviewed, version-controlled artifact.
- **Ordered and repeatable** — the numbering defines a single, deterministic sequence.
- Plain SQL, so the exact statements are transparent and use native database features.
- Reviewable via normal pull-request workflows.

**Cons**
- You must **build and maintain the runner** (or adopt a tool), including logic to record
  what has been applied.
- **Rollback is manual** — to undo `V3`, you typically write a new forward script `V4`.
- Easy to apply scripts **out of order** or skip one without a tracking mechanism.
- SQL is usually **database-specific**, so porting to another engine means rewriting.

### 3. ORM / framework-generated migrations

Many application frameworks ship their own migration tooling that generates migration files
(often by diffing model definitions against the current schema).

**Pros**
- Tightly **integrated with the application** and its deployment lifecycle.
- Can **autogenerate** migrations from model/entity changes.
- Familiar to developers already using that framework.

**Cons**
- **Language/framework lock-in** — the migrations live inside one stack.
- Generated SQL can be **opaque** or suboptimal, and may miss edge cases.
- Less suitable when the database is shared by multiple apps written in different languages.

### What these approaches share

Regardless of the approach, *something* must **track which changes have already been applied** —
whether that is a history table, a naming convention, or a human's memory. The weaker that
tracking is, the more drift and risk you accumulate. This is precisely the gap that dedicated
tools like Liquibase are built to close.

---

## Schema management WITH Liquibase

[Liquibase](https://www.liquibase.org/) is a dedicated, open-source database schema change
management tool. Instead of ad-hoc scripts, you describe changes declaratively and let Liquibase
decide what needs to run, track what has run, and (where possible) reverse it.

### Core concepts

- **Changelog** — the master list of changes. Typically a small *master* changelog that
  `include`s many smaller changelog files, keeping changes modular and reviewable.
- **changeSet** — the atomic unit of change, uniquely identified by `id` + `author` (+ file
  path). A changeSet is applied exactly once and never edited after release.
- **Tracking tables** — Liquibase creates `DATABASECHANGELOG` (a record of every applied
  changeSet) and `DATABASECHANGELOGLOCK` (prevents two processes from migrating at once).
- **Checksums** — each applied changeSet stores a hash. If a released changeSet is later
  modified, Liquibase detects the mismatch and fails fast, protecting against accidental
  tampering and drift.

### Authoring formats

Liquibase lets you write changeSets in **XML, YAML, JSON, or formatted SQL**. The XML/YAML/JSON
forms use a **database-agnostic DSL** (e.g. `createTable`, `addColumn`) that Liquibase translates
into the correct dialect per target database; the formatted-SQL form lets you drop down to raw,
database-specific SQL when you need it.

### Key capabilities

- **Rollback** — many standard changes (e.g. `createTable`, `addColumn`) can be **automatically
  reversed**; for raw SQL you provide an explicit `rollback` block. You can roll back by count,
  tag, or date.
- **Contexts and labels** — apply a subset of changeSets per environment (e.g. only run seed
  data in `dev`).
- **Preconditions** — guard a changeSet so it runs only if the database is in an expected state.
- **`runOnChange` / `runAlways`** — re-apply a changeSet when its content changes (useful for
  views, procedures).
- **`diff` and `generateChangelog`** — compare two databases or reverse-engineer a changelog
  from an existing schema.
- **CI/CD integration** — a mature CLI, plus Maven/Gradle plugins and Docker images, make it
  straightforward to run migrations as a pipeline step.

### Illustrative changeSet (YAML)

```yaml
databaseChangeLog:
  - changeSet:
      id: 1-create-customers
      author: data_engineer
      changes:
        - createTable:
            tableName: customers
            columns:
              - column:
                  name: customer_id
                  type: SERIAL
                  constraints:
                    primaryKey: true
              - column:
                  name: email
                  type: VARCHAR(255)
                  constraints:
                    nullable: false
                    unique: true
      # createTable is auto-reversible, so an explicit rollback is optional here.

  - changeSet:
      id: 2-add-loyalty-points
      author: data_engineer
      changes:
        - sql:
            sql: ALTER TABLE customers ADD COLUMN loyalty_points INT DEFAULT 0
      rollback:
        # Raw SQL is NOT auto-reversible, so we declare how to undo it.
        - sql:
            sql: ALTER TABLE customers DROP COLUMN loyalty_points
```

---

## Pros and cons of Liquibase

### Pros

- **Database-agnostic abstraction** — the DSL targets many engines (PostgreSQL, MySQL, Oracle,
  SQL Server, etc.), so the same changelog can run against different databases.
- **Built-in rollback** — automatic reversal for standard changes and explicit rollback blocks
  for the rest; roll back by count, tag, or date.
- **Precise change tracking + checksums** — `DATABASECHANGELOG` gives a complete, queryable
  audit trail, and checksums detect drift or tampering with already-released changes.
- **Multiple authoring formats** — XML, YAML, JSON, or formatted SQL, so teams can pick what
  fits their workflow.
- **Powerful targeting** — contexts, labels, and preconditions allow environment-specific and
  conditional execution.
- **Reverse-engineering** — `diff` and `generateChangelog` help adopt Liquibase on an existing
  database and catch out-of-band changes.
- **Mature ecosystem** — solid CLI, build-tool plugins, Docker images, and broad CI/CD support.

### Cons

- **Learning curve & added abstraction** — concepts (changelogs, changeSets, contexts,
  preconditions) and a new layer to reason about, on top of SQL you may already know.
- **Verbosity** — XML/YAML changeSets are wordier than the equivalent plain SQL.
- **Rollback isn't free for raw SQL** — auto-rollback only covers standard, structured changes;
  raw SQL requires you to hand-write the reverse, and some operations are simply irreversible
  (e.g. dropping data).
- **Possible overkill** — for a tiny, single-database, single-developer project, manual or
  versioned SQL may be entirely sufficient.
- **Abstraction can hide details** — the database-agnostic DSL doesn't expose every
  engine-specific feature; you sometimes fall back to raw SQL anyway, losing portability.
- **Edition split** — some advanced features (e.g. certain quality checks, observability,
  targeted rollback enhancements) are part of the paid **Pro** edition rather than open-source.

---

## Quick comparison

| Aspect              | Manual SQL            | Versioned SQL scripts        | Liquibase                                  |
|---------------------|-----------------------|------------------------------|--------------------------------------------|
| **Change tracking** | None (manual/memory)  | Convention or homegrown table| Built-in `DATABASECHANGELOG` + checksums   |
| **Ordering**        | Ad-hoc                | Filename/version convention  | Changelog order, enforced                  |
| **Rollback**        | Manual, undocumented  | Manual (write a new script)  | Auto for standard changes; explicit for SQL|
| **Portability**     | DB-specific           | DB-specific                  | DB-agnostic DSL (raw SQL optional)         |
| **Tooling cost**    | None                  | Build/own a runner           | Adopt & learn Liquibase                    |
| **Learning curve**  | Lowest                | Low–medium                   | Medium                                     |
| **Audit trail**     | Weak                  | Moderate (via Git + runner)  | Strong (history table + checksums)         |

---

## When to choose what

- **Small, solo, or throwaway projects** — manual SQL or simple versioned SQL scripts are often
  enough; the overhead of a dedicated tool isn't justified.
- **Single application, single database engine, one team** — versioned SQL scripts (optionally
  via a lightweight migration tool) give a good balance of discipline and simplicity.
- **Multiple environments, larger teams, multiple database engines, regulated/audited systems,
  or CI/CD-driven deployments** — Liquibase's tracking, rollback, portability, and audit trail
  pay for their learning curve, and the structured change history becomes a real asset.

The right answer is rarely "always use a tool" or "never use one" — it's matching the rigor of
your schema-management approach to the size, longevity, and risk profile of the project.
