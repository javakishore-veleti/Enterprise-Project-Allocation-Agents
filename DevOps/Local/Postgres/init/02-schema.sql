-- Application schema namespace. Tables are created in milestone M2
-- (see DevelopmentPlan.md §5 — M2 Data Layer) via 03-tables.sql.

CREATE SCHEMA IF NOT EXISTS epaa AUTHORIZATION epaa;

-- Make `epaa` the default schema for the app user.
ALTER ROLE epaa SET search_path TO epaa, public;
