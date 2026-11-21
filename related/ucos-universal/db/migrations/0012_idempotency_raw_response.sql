-- 0012 Replays must return the original response byte for byte. jsonb normalises whitespace and reorders keys,
-- so the stored answer is also kept as raw bytes; `response` (jsonb) stays for querying and support tooling.
ALTER TABLE kernel.cmd_idempotency ADD COLUMN response_raw bytea;
