-- 0011 The audit appender runs without a tenant context and must read the previous hash of each chain it extends
-- (and verify chains). 0007 granted SELECT but no policy, so under forced RLS it saw nothing.
CREATE POLICY appender_reads_chain ON kernel.audit_records FOR SELECT TO ucos_audit_appender USING (true);
