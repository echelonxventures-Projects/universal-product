-- 0001 Roles, schemas and the tenant context (ADR-020, KERNEL-DESIGN §4).
-- ucos_app: runtime role for kernel services; never bypasses row-level security.
-- ucos_audit_appender: the only role that may write sealed audit records.
-- ucos_readonly: analytics and support tooling (still subject to RLS).
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ucos_app') THEN
    CREATE ROLE ucos_app NOLOGIN NOBYPASSRLS; END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ucos_audit_appender') THEN
    CREATE ROLE ucos_audit_appender NOLOGIN NOBYPASSRLS; END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ucos_readonly') THEN
    CREATE ROLE ucos_readonly NOLOGIN NOBYPASSRLS; END IF;
END $$;

CREATE SCHEMA IF NOT EXISTS registry;   -- control-plane registries (platform scope, no RLS)
CREATE SCHEMA IF NOT EXISTS kernel;     -- tenant data plane (RLS everywhere)
CREATE SCHEMA IF NOT EXISTS packs;      -- generated physical tables for core object types (ADR-003)

-- The object service sets app.tenant_id with SET LOCAL at the start of every transaction.
-- An unset tenant yields NULL, which matches no row: fail closed.
CREATE OR REPLACE FUNCTION kernel.current_tenant() RETURNS text
  LANGUAGE sql STABLE AS $$ SELECT nullif(current_setting('app.tenant_id', true), '') $$;

GRANT USAGE ON SCHEMA kernel, packs TO ucos_app, ucos_readonly, ucos_audit_appender;
GRANT USAGE ON SCHEMA registry TO ucos_app, ucos_readonly;
