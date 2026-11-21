-- 0008 Temporal trigger store (U13 TMP-L4). The trigger engine is the only scheduler.
CREATE TABLE kernel.triggers (
  tenant_id        text NOT NULL,
  id               text NOT NULL,
  idempotency_key  text NOT NULL,
  fire_at          timestamptz,                         -- next firing (UTC)
  recurrence       text,                                -- RFC 5545 RRULE, evaluated by U13 only
  tz               text,                                -- IANA zone for wall-clock recurrences
  calendar         text,                                -- business calendar for business-time rules
  target_operation text NOT NULL,                       -- "<slug>:<Command>"
  target_id        text,
  payload          jsonb NOT NULL DEFAULT '{}',
  status           text NOT NULL CHECK (status IN ('scheduled', 'firing', 'fired', 'cancelled', 'failed')),
  attempts         int  NOT NULL DEFAULT 0,
  created_at       timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (tenant_id, id),
  UNIQUE (tenant_id, idempotency_key),
  CHECK (fire_at IS NOT NULL OR recurrence IS NOT NULL),
  CHECK (recurrence IS NULL OR tz IS NOT NULL)
);
CREATE INDEX triggers_due ON kernel.triggers (fire_at) WHERE status = 'scheduled';
ALTER TABLE kernel.triggers ENABLE ROW LEVEL SECURITY;
ALTER TABLE kernel.triggers FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON kernel.triggers
  USING (tenant_id = kernel.current_tenant()) WITH CHECK (tenant_id = kernel.current_tenant());
GRANT SELECT, INSERT, UPDATE ON kernel.triggers TO ucos_app;
