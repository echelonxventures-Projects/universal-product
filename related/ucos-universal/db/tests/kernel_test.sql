-- Kernel schema tests: tenant isolation (SEC-TENANT-01), versioning (ADR-011), idempotency, outbox,
-- tamper-evident audit (AUD-L1), trigger constraints, generated pack table. Any failure raises and stops psql.
\set ON_ERROR_STOP 1
\o /dev/null
CREATE OR REPLACE FUNCTION pg_temp.expect_error(sql text, needle text) RETURNS void LANGUAGE plpgsql AS $$
BEGIN
  EXECUTE sql;
  RAISE EXCEPTION 'expected an error containing "%" but the statement succeeded: %', needle, sql;
EXCEPTION WHEN raise_exception THEN
  IF SQLERRM LIKE 'expected an error%' THEN RAISE; END IF;
  IF position(needle IN SQLERRM) = 0 THEN RAISE EXCEPTION 'wrong error for %: %', sql, SQLERRM; END IF;
WHEN OTHERS THEN
  IF position(needle IN SQLERRM) = 0 THEN RAISE EXCEPTION 'wrong error for %: %', sql, SQLERRM; END IF;
END $$;
CREATE OR REPLACE FUNCTION pg_temp.expect_eq(got bigint, want bigint, what text) RETURNS void LANGUAGE plpgsql AS $$
BEGIN IF got IS DISTINCT FROM want THEN RAISE EXCEPTION '%: expected %, got %', what, want, got; END IF; END $$;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA pg_temp TO PUBLIC;

-- 1. Tenant isolation on objects --------------------------------------------------------------
SET ROLE ucos_app;
SET app.tenant_id = 't1';
INSERT INTO kernel.objects (tenant_id, type, id, version, attributes) VALUES ('t1', 'ucos.sample.Note', 'ucos:note:A1', 1, '{"title":"t1 note"}');
SET app.tenant_id = 't2';
SELECT pg_temp.expect_eq((SELECT count(*) FROM kernel.objects), 0, 'tenant t2 must not see t1 objects');
SELECT pg_temp.expect_error($$INSERT INTO kernel.objects (tenant_id, type, id, version) VALUES ('t1', 'x', 'ucos:note:B1', 1)$$, 'row-level security');
SELECT pg_temp.expect_eq((SELECT count(*) FROM kernel.object_versions), 0, 'tenant t2 must not see t1 history');
RESET app.tenant_id;
SELECT pg_temp.expect_eq((SELECT count(*) FROM kernel.objects), 0, 'no tenant context must see nothing (fail closed)');

-- 2. Versioning ---------------------------------------------------------------------------------
SET app.tenant_id = 't1';
UPDATE kernel.objects SET version = 2, attributes = '{"title":"edited"}' WHERE id = 'ucos:note:A1';
SELECT pg_temp.expect_eq((SELECT count(*) FROM kernel.object_versions WHERE id = 'ucos:note:A1'), 2, 'two versions recorded');
SELECT pg_temp.expect_eq((SELECT count(*) FROM kernel.object_versions WHERE id = 'ucos:note:A1' AND version = 1 AND upper(recorded) IS NOT NULL), 1, 'v1 transaction time closed');
SELECT pg_temp.expect_error($$UPDATE kernel.objects SET version = 4 WHERE id = 'ucos:note:A1'$$, 'version must increase by one');

-- 3. Command idempotency ------------------------------------------------------------------------
INSERT INTO kernel.cmd_idempotency (tenant_id, key, request_hash, status, expires_at) VALUES ('t1', 'k-1', '\x01', 'in_progress', now() + interval '1 hour');
SELECT pg_temp.expect_error($$INSERT INTO kernel.cmd_idempotency (tenant_id, key, request_hash, status, expires_at) VALUES ('t1', 'k-1', '\x02', 'in_progress', now())$$, 'duplicate key');
SET app.tenant_id = 't2';
INSERT INTO kernel.cmd_idempotency (tenant_id, key, request_hash, status, expires_at) VALUES ('t2', 'k-1', '\x01', 'in_progress', now() + interval '1 hour');

-- 4. Outbox: tenants see their own rows; the relay sees all unpublished rows ----------------------
INSERT INTO kernel.outbox (tenant_id, event_id, topic, partition_key, event) VALUES ('t2', 'e-2', 'ucos.sandbox-1.sample.note.v1', 'ucos:note:B2', '{}');
SET app.tenant_id = 't1';
INSERT INTO kernel.outbox (tenant_id, event_id, topic, partition_key, event) VALUES ('t1', 'e-1', 'ucos.sandbox-1.sample.note.v1', 'ucos:note:A1', '{}');
SELECT pg_temp.expect_eq((SELECT count(*) FROM kernel.outbox), 1, 'tenant sees only its outbox rows');
SELECT pg_temp.expect_error($$INSERT INTO kernel.outbox (tenant_id, event_id, topic, partition_key, event) VALUES ('t1', 'e-3', 'not-a-topic', 'k', '{}')$$, 'outbox_topic_check');
RESET ROLE;
SET ROLE ucos_relay;
SELECT pg_temp.expect_eq((SELECT count(*) FROM kernel.outbox WHERE published_at IS NULL), 2, 'relay sees all unpublished rows');
UPDATE kernel.outbox SET published_at = now() WHERE event_id = 'e-1';
SELECT pg_temp.expect_error($$UPDATE kernel.outbox SET event = '{"x":1}' WHERE event_id = 'e-2'$$, 'permission denied');
RESET ROLE;

-- 5. Audit chain (the appender runs with no tenant context) -------------------------------------------
RESET app.tenant_id;
SET ROLE ucos_audit_appender;
INSERT INTO kernel.audit_records (tenant_id, day, seq, id, rec, prev_hash, hash)
SELECT 't1', '2027-01-10', 1, 'a1', r, decode(repeat('00', 32), 'hex'), kernel.audit_hash((decode(repeat('00', 32), 'hex'))::bytea, r)
  FROM (SELECT '{"action":"sample:CreateNote","actor":"asha"}'::jsonb AS r) s;
INSERT INTO kernel.audit_records (tenant_id, day, seq, id, rec, prev_hash, hash)
SELECT 't1', '2027-01-10', 2, 'a2', r, p.hash, kernel.audit_hash(p.hash, r)
  FROM (SELECT '{"action":"sample:PublishNote","actor":"asha"}'::jsonb AS r) s,
       (SELECT hash FROM kernel.audit_records WHERE tenant_id = 't1' AND day = '2027-01-10' AND seq = 1) p;
SELECT pg_temp.expect_error($$INSERT INTO kernel.audit_records (tenant_id, day, seq, id, rec, prev_hash, hash) VALUES ('t1', '2027-01-10', 3, 'a3', '{}', '\x00', '\x00')$$, 'audit chain mismatch');
SELECT pg_temp.expect_error($$INSERT INTO kernel.audit_records (tenant_id, day, seq, id, rec, prev_hash, hash) VALUES ('t1', '2027-01-10', 9, 'a9', '{}', '\x00', '\x00')$$, 'audit chain gap');
SELECT pg_temp.expect_error($$UPDATE kernel.audit_records SET rec = '{}' WHERE seq = 1$$, 'permission denied');
SELECT pg_temp.expect_error($$DELETE FROM kernel.audit_records WHERE seq = 1$$, 'permission denied');
RESET ROLE;
SET ROLE ucos_app;
SET app.tenant_id = 't1';
SELECT pg_temp.expect_error($$UPDATE kernel.audit_records SET rec = '{}' WHERE seq = 1$$, 'permission denied');
SELECT pg_temp.expect_eq(kernel.audit_verify('t1', '2027-01-10'), NULL, 'intact chain verifies');
RESET ROLE;
-- An operator with direct database access (superuser) alters a record: verification must find it.
UPDATE kernel.audit_records SET rec = '{"action":"sample:PublishNote","actor":"mallory"}' WHERE tenant_id = 't1' AND seq = 2;
SELECT pg_temp.expect_eq(kernel.audit_verify('t1', '2027-01-10'), 2, 'tampered record detected at seq 2');

-- 6. Triggers -------------------------------------------------------------------------------------
SET ROLE ucos_app;
SET app.tenant_id = 't1';
INSERT INTO kernel.triggers (tenant_id, id, idempotency_key, fire_at, target_operation, status) VALUES ('t1', 'tr1', 'idem-1', '2027-01-10T09:30:00Z', 'sample:RemindNote', 'scheduled');
SELECT pg_temp.expect_error($$INSERT INTO kernel.triggers (tenant_id, id, idempotency_key, recurrence, target_operation, status) VALUES ('t1', 'tr2', 'idem-2', 'FREQ=DAILY', 'x:y', 'scheduled')$$, 'triggers_check');
SELECT pg_temp.expect_error($$INSERT INTO kernel.triggers (tenant_id, id, idempotency_key, fire_at, target_operation, status) VALUES ('t1', 'tr3', 'idem-1', now(), 'x:y', 'scheduled')$$, 'duplicate key');

-- 6b. Trigger engine sees due triggers of every tenant but cannot change their target
RESET ROLE;
SET ROLE ucos_trigger_engine;
SELECT pg_temp.expect_eq((SELECT count(*) FROM kernel.triggers WHERE status = 'scheduled'), 1, 'engine sees due triggers');
UPDATE kernel.triggers SET status = 'fired' WHERE id = 'tr1';
SELECT pg_temp.expect_error($$UPDATE kernel.triggers SET target_operation = 'x:evil' WHERE id = 'tr1'$$, 'permission denied');
RESET ROLE;
SET ROLE ucos_app;
SET app.tenant_id = 't1';

-- 7. Generated pack table -----------------------------------------------------------------------------
INSERT INTO packs.sample_note (tenant_id, id, title, status, author) VALUES ('t1', 'ucos:note:A1', '{"en":"Kernel works"}', 'draft', 'asha');
SELECT pg_temp.expect_error($$UPDATE packs.sample_note SET status = 'published' WHERE id = 'ucos:note:A1'$$, 'sample_note_check');
UPDATE packs.sample_note SET status = 'published', published_at = now() WHERE id = 'ucos:note:A1';
SET app.tenant_id = 't2';
SELECT pg_temp.expect_eq((SELECT count(*) FROM packs.sample_note), 0, 'pack table isolated by tenant');
RESET ROLE;
\o
\echo 'kernel schema tests: all passed'
