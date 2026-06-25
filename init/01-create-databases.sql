-- Runs once, the first time the Postgres data volume is initialized
-- (Postgres executes every *.sql in /docker-entrypoint-initdb.d/ in name order).
--
-- One database per (tool x model) so Flyway and Liquibase never collide and
-- each can be wiped/re-applied independently.

CREATE DATABASE flyway_hospital;
CREATE DATABASE flyway_ecommerce;
CREATE DATABASE liquibase_hospital;
CREATE DATABASE liquibase_ecommerce;
CREATE DATABASE flyway_library;
CREATE DATABASE liquibase_library;
