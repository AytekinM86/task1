# Flyway + Liquibase learning sandbox — task runner.
#
# Most commands take a MODEL variable selecting which schema to act on:
#     make fw-migrate MODEL=hospital     (default)
#     make fw-migrate MODEL=ecommerce
#
# Run `make help` (or just `make`) for the full list.

# NOTE: do not add trailing inline comments to these assignments — Make keeps the
# whitespace before the '#' in the value (e.g. "hospital   "), which breaks
# $(MODEL).conf and similar expansions.
MODEL ?= hospital
COUNT ?= 1
DB ?= flyway_hospital

COMPOSE := docker compose
# One-shot tool invocations (containers live under the "tools" profile).
FLYWAY    := $(COMPOSE) run --rm flyway -configFiles=/flyway/conf/$(MODEL).conf
LIQUIBASE := $(COMPOSE) run --rm liquibase --defaults-file=/liquibase/conf/$(MODEL).properties

.DEFAULT_GOAL := help

# ----------------------------------------------------------------------------
# Infrastructure
# ----------------------------------------------------------------------------
.PHONY: up down reset nuke ps logs psql

up: ## Start PostgreSQL (waits until it is healthy)
	$(COMPOSE) up -d --wait postgres

down: ## Stop containers (keeps data volume)
	$(COMPOSE) down

reset: ## Destroy everything (incl. data) and start fresh
	$(COMPOSE) down -v
	$(COMPOSE) up -d --wait postgres

nuke: ## Remove all project containers, networks and volumes (keeps images; no restart)
	$(COMPOSE) down -v --remove-orphans

ps: ## Show container status
	$(COMPOSE) ps

logs: ## Tail PostgreSQL logs
	$(COMPOSE) logs -f postgres

psql: ## Open a psql shell: make psql DB=flyway_hospital
	$(COMPOSE) exec postgres psql -U postgres -d $(DB)

# ----------------------------------------------------------------------------
# Flyway   (MODEL=hospital|ecommerce)
# ----------------------------------------------------------------------------
.PHONY: fw-info fw-migrate fw-validate fw-clean fw-repair

fw-info: ## Flyway: show migration status / history
	$(FLYWAY) info

fw-migrate: ## Flyway: apply pending migrations
	$(FLYWAY) migrate

fw-validate: ## Flyway: validate applied migrations against the files
	$(FLYWAY) validate

fw-clean: ## Flyway: DROP every object in the schema (sandbox only!)
	$(FLYWAY) -cleanDisabled=false clean

fw-repair: ## Flyway: fix the schema history table after a failed/edited migration
	$(FLYWAY) repair

# ----------------------------------------------------------------------------
# Liquibase   (MODEL=hospital|ecommerce)
# ----------------------------------------------------------------------------
.PHONY: lb-status lb-update lb-validate lb-history lb-rollback

lb-status: ## Liquibase: list changesets not yet applied
	$(LIQUIBASE) status --verbose

lb-update: ## Liquibase: apply pending changesets
	$(LIQUIBASE) update

lb-validate: ## Liquibase: validate the changelog
	$(LIQUIBASE) validate

lb-history: ## Liquibase: show the applied changeset history
	$(LIQUIBASE) history

lb-rollback: ## Liquibase: undo the last N changesets — make lb-rollback COUNT=1
	$(LIQUIBASE) rollback-count $(COUNT)

# ----------------------------------------------------------------------------
# Data generator (Python) — seeds liquibase_hospital with fake data
# ----------------------------------------------------------------------------
.PHONY: datagen-build datagen datagen-dry

ARGS ?= seed          # passed to the generator (e.g. ARGS="seed --last-90-days")

datagen-build: ## Build the data-generator Docker image
	$(COMPOSE) build datagen

datagen: ## Run the generator: make datagen ARGS="seed --last-30-days" (needs lb-update first)
	$(COMPOSE) run --rm datagen $(ARGS)

datagen-dry: ## Generate + validate against the live schema, then roll back
	$(COMPOSE) run --rm datagen seed --dry-run

# ----------------------------------------------------------------------------
# Combos
# ----------------------------------------------------------------------------
.PHONY: migrate-all clean-all demo

migrate-all: ## Apply ALL migrations: Flyway + Liquibase, both models
	$(COMPOSE) run --rm flyway -configFiles=/flyway/conf/hospital.conf migrate
	$(COMPOSE) run --rm flyway -configFiles=/flyway/conf/ecommerce.conf migrate
	$(COMPOSE) run --rm liquibase --defaults-file=/liquibase/conf/hospital.properties update
	$(COMPOSE) run --rm liquibase --defaults-file=/liquibase/conf/ecommerce.properties update

clean-all: ## Wipe all four schemas (Flyway clean + Liquibase drop-all)
	$(COMPOSE) run --rm flyway -configFiles=/flyway/conf/hospital.conf -cleanDisabled=false clean
	$(COMPOSE) run --rm flyway -configFiles=/flyway/conf/ecommerce.conf -cleanDisabled=false clean
	$(COMPOSE) run --rm liquibase --defaults-file=/liquibase/conf/hospital.properties drop-all
	$(COMPOSE) run --rm liquibase --defaults-file=/liquibase/conf/ecommerce.properties drop-all

demo: up migrate-all ## Full demo: start DB, run every migration, then show status
	@echo "\n=== Flyway info (hospital) ==="
	@$(COMPOSE) run --rm flyway -configFiles=/flyway/conf/hospital.conf info
	@echo "\n=== Liquibase history (ecommerce) ==="
	@$(COMPOSE) run --rm liquibase --defaults-file=/liquibase/conf/ecommerce.properties history

# ----------------------------------------------------------------------------
# Help
# ----------------------------------------------------------------------------
.PHONY: help
help: ## Show this help
	@echo "Flyway + Liquibase learning sandbox"
	@echo ""
	@echo "Usage: make <target> [MODEL=hospital|ecommerce]"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'
