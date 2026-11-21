-- 0010 The trigger engine finds due triggers across tenants (TMP-L4) and marks them fired.
-- It reads and updates kernel.triggers only; firing a trigger runs its target command through the command bus,
-- inside the trigger's own tenant context.
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ucos_trigger_engine') THEN
    CREATE ROLE ucos_trigger_engine NOLOGIN NOBYPASSRLS; END IF;
END $$;
GRANT USAGE ON SCHEMA kernel TO ucos_trigger_engine;
GRANT SELECT, UPDATE (status, attempts, fire_at) ON kernel.triggers TO ucos_trigger_engine;
CREATE POLICY engine_reads_due ON kernel.triggers FOR SELECT TO ucos_trigger_engine USING (true);
CREATE POLICY engine_updates_state ON kernel.triggers FOR UPDATE TO ucos_trigger_engine USING (true) WITH CHECK (true);
