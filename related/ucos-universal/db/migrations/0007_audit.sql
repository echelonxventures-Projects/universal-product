-- 0007 Tamper-evident audit chain (U68, KERNEL-DESIGN §12, AUD-L1).
-- The SDK writes audit_pending in the command's transaction; the appender seals records into the per-tenant,
-- per-day hash chain. Sealed records can never be updated or deleted, not even by the appender.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE kernel.audit_pending (
  id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  tenant_id     text NOT NULL,
  record        jsonb NOT NULL,
  created_at    timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE kernel.audit_pending ENABLE ROW LEVEL SECURITY;
ALTER TABLE kernel.audit_pending FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON kernel.audit_pending
  USING (tenant_id = kernel.current_tenant()) WITH CHECK (tenant_id = kernel.current_tenant());
GRANT INSERT ON kernel.audit_pending TO ucos_app;

CREATE TABLE kernel.audit_records (
  tenant_id     text NOT NULL,
  day           date NOT NULL,
  seq           bigint NOT NULL,
  id            text NOT NULL,
  rec           jsonb NOT NULL,
  prev_hash     bytea NOT NULL,
  hash          bytea NOT NULL,
  PRIMARY KEY (tenant_id, day, seq)
) PARTITION BY RANGE (day);
CREATE TABLE kernel.audit_records_default PARTITION OF kernel.audit_records DEFAULT;

-- hash = sha256(prev_hash || canonical record); the first record of a day chains from 32 zero bytes.
CREATE OR REPLACE FUNCTION kernel.audit_hash(prev bytea, rec jsonb) RETURNS bytea
  LANGUAGE sql IMMUTABLE AS $$ SELECT digest(prev || convert_to(rec::text, 'UTF8'), 'sha256') $$;

CREATE OR REPLACE FUNCTION kernel.audit_check_chain() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE expected_prev bytea;
BEGIN
  SELECT hash INTO expected_prev FROM kernel.audit_records
   WHERE tenant_id = NEW.tenant_id AND day = NEW.day AND seq = NEW.seq - 1;
  IF NEW.seq = 1 THEN expected_prev := decode(repeat('00', 32), 'hex'); END IF;
  IF expected_prev IS NULL THEN
    RAISE EXCEPTION 'audit chain gap: seq % has no predecessor', NEW.seq;
  END IF;
  IF NEW.prev_hash <> expected_prev OR NEW.hash <> kernel.audit_hash(NEW.prev_hash, NEW.rec) THEN
    RAISE EXCEPTION 'audit chain mismatch at seq %', NEW.seq;
  END IF;
  RETURN NEW;
END $$;
CREATE TRIGGER audit_chain BEFORE INSERT ON kernel.audit_records
  FOR EACH ROW EXECUTE FUNCTION kernel.audit_check_chain();

-- Verification used by the daily anchoring job and by auditors: returns the first broken seq, or NULL.
CREATE OR REPLACE FUNCTION kernel.audit_verify(p_tenant text, p_day date) RETURNS bigint
  LANGUAGE plpgsql STABLE AS $$
DECLARE r record; prev bytea := decode(repeat('00', 32), 'hex'); expect_seq bigint := 1;
BEGIN
  FOR r IN SELECT * FROM kernel.audit_records WHERE tenant_id = p_tenant AND day = p_day ORDER BY seq LOOP
    IF r.seq <> expect_seq OR r.prev_hash <> prev OR r.hash <> kernel.audit_hash(r.prev_hash, r.rec) THEN
      RETURN r.seq;
    END IF;
    prev := r.hash; expect_seq := expect_seq + 1;
  END LOOP;
  RETURN NULL;
END $$;

ALTER TABLE kernel.audit_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE kernel.audit_records FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_read ON kernel.audit_records FOR SELECT
  USING (tenant_id = kernel.current_tenant());
CREATE POLICY appender_insert ON kernel.audit_records FOR INSERT TO ucos_audit_appender WITH CHECK (true);
REVOKE UPDATE, DELETE, TRUNCATE ON kernel.audit_records FROM PUBLIC;
GRANT SELECT ON kernel.audit_records TO ucos_app, ucos_readonly;
GRANT INSERT, SELECT ON kernel.audit_records TO ucos_audit_appender;
GRANT SELECT, DELETE ON kernel.audit_pending TO ucos_audit_appender;
CREATE POLICY appender_drains ON kernel.audit_pending FOR ALL TO ucos_audit_appender USING (true);

CREATE TABLE kernel.audit_anchors (
  tenant_id     text NOT NULL,
  day           date NOT NULL,
  last_seq      bigint NOT NULL,
  root_hash     bytea NOT NULL,
  signature     text NOT NULL,
  anchored_to   text[] NOT NULL,
  at            timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (tenant_id, day)
);
REVOKE UPDATE, DELETE, TRUNCATE ON kernel.audit_anchors FROM PUBLIC;
GRANT INSERT, SELECT ON kernel.audit_anchors TO ucos_audit_appender;
