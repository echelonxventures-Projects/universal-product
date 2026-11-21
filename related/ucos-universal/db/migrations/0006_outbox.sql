-- 0006 Transactional outbox (ADR-007, KERNEL-DESIGN §6). Written in the same transaction as the state change.
CREATE TABLE kernel.outbox (
  seq           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  tenant_id     text NOT NULL,
  event_id      text NOT NULL,
  topic         text NOT NULL CHECK (topic ~ '^ucos\.[a-z0-9-]+\.[a-z0-9-]+\.[a-z0-9-]+\.v[0-9]+$'),
  partition_key text NOT NULL,                        -- aggregate id
  event         jsonb NOT NULL,                       -- CloudEvent (spec/events/cloudevent-envelope.schema.json)
  created_at    timestamptz NOT NULL DEFAULT now(),
  published_at  timestamptz,
  UNIQUE (tenant_id, event_id)
);
CREATE INDEX outbox_unpublished ON kernel.outbox (seq) WHERE published_at IS NULL;
ALTER TABLE kernel.outbox ENABLE ROW LEVEL SECURITY;
ALTER TABLE kernel.outbox FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON kernel.outbox
  USING (tenant_id = kernel.current_tenant()) WITH CHECK (tenant_id = kernel.current_tenant());
GRANT SELECT, INSERT ON kernel.outbox TO ucos_app;
-- The relay runs as its own role with a cross-tenant read of unpublished rows only.
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ucos_relay') THEN
    CREATE ROLE ucos_relay NOLOGIN NOBYPASSRLS; END IF;
END $$;
GRANT USAGE ON SCHEMA kernel TO ucos_relay;
GRANT SELECT, UPDATE (published_at) ON kernel.outbox TO ucos_relay;
CREATE POLICY relay_reads_all ON kernel.outbox FOR SELECT TO ucos_relay USING (true);
CREATE POLICY relay_marks_published ON kernel.outbox FOR UPDATE TO ucos_relay USING (true) WITH CHECK (true);
