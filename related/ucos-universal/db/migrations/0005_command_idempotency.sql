-- 0005 Command idempotency (KERNEL-DESIGN §3).
CREATE TABLE kernel.cmd_idempotency (
  tenant_id     text NOT NULL,
  key           text NOT NULL,
  request_hash  bytea NOT NULL,
  status        text NOT NULL CHECK (status IN ('in_progress', 'completed')),
  response      jsonb,
  http_status   int,
  created_at    timestamptz NOT NULL DEFAULT now(),
  expires_at    timestamptz NOT NULL,
  PRIMARY KEY (tenant_id, key)
) PARTITION BY HASH (tenant_id);
CREATE TABLE kernel.cmd_idempotency_p0 PARTITION OF kernel.cmd_idempotency FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE kernel.cmd_idempotency_p1 PARTITION OF kernel.cmd_idempotency FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE kernel.cmd_idempotency_p2 PARTITION OF kernel.cmd_idempotency FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE kernel.cmd_idempotency_p3 PARTITION OF kernel.cmd_idempotency FOR VALUES WITH (MODULUS 4, REMAINDER 3);
CREATE INDEX cmd_idempotency_expiry ON kernel.cmd_idempotency (expires_at);
ALTER TABLE kernel.cmd_idempotency ENABLE ROW LEVEL SECURITY;
ALTER TABLE kernel.cmd_idempotency FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON kernel.cmd_idempotency
  USING (tenant_id = kernel.current_tenant()) WITH CHECK (tenant_id = kernel.current_tenant());
GRANT SELECT, INSERT, UPDATE, DELETE ON kernel.cmd_idempotency TO ucos_app;
