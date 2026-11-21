-- 0013 The appender claims pending audit rows with SELECT ... FOR UPDATE SKIP LOCKED so several appenders can run.
-- Row locking needs an UPDATE privilege; grant it on one column only (the rows are deleted, never changed).
GRANT UPDATE (created_at) ON kernel.audit_pending TO ucos_audit_appender;
