# Database and Recovery Runbook

## What has to survive

| Item | Where | Without it |
|---|---|---|
| Database | `LX_DB`, default `/app/data/luxora.db` (+ `-wal`, `-shm` while running) | all business data is gone |
| Master keyring | `LUXORA_MASTER_KEY` in the secret store, **or** `/app/data/master.json` | sealed gateway and connector credentials cannot be decrypted; re-enter them in the consoles |
| Password pepper | `LUXORA_PEPPER` in the secret store | **no one can sign in**; every password must be reset |
| Registry seal key | `LX_REGISTRY_KEY`, or `/app/data/registry.json` | harmless: the registry is recompiled and resealed at boot (refused only with `LX_REGISTRY_STRICT=1`) |

Keep the keys and the pepper in a secret store that is backed up separately from the database
backups. A backup that carries the key to its own secrets protects nothing, so `scripts/backup.js`
deliberately does not include them.

### The server refuses to boot: `data/master.json …`

The keyring exists but cannot be used, so the server stopped rather than write a new key over it.
The file has not been changed.

1. Restore `master.json` from its escrow copy and start again.
2. If `LUXORA_MASTER_KEY` is set, the file only names the key version: restore it the same way, and
   do not change the key.
3. Only if no copy exists: move the damaged file aside (never delete it) and start. The server creates
   a new keyring, and every sealed gateway and connector credential must be re-entered in the consoles.
   This is a deliberate, permanent loss of those secrets, so record who decided it and when.

## Database engine

Production runs on **SQLite** (`node:sqlite`, WAL mode, `busy_timeout` 3 s), one process, one
host. The PostgreSQL path (`LX_DB_DRIVER=postgres`) is not supported for production in this
release — see PRODUCTION_READINESS.md PR-007 for the measured defects.

Limits to plan around: one writer at a time (writes are serialized, measured at about 60
checkouts/s on 4 vCPU), no replication, the database must be on local disk (not NFS/SMB).

## Backups

```bash
# inside the container (the volume is mounted at /app/data)
docker compose exec luxora sh -c 'LX_BACKUP_PASSPHRASE=… node scripts/backup.js --out /app/data/backups'
# or on the host, against the database file directly
LX_BACKUP_PASSPHRASE=… node scripts/backup.js --db /path/to/luxora.db --out /backups
```

- `VACUUM INTO` takes a consistent point-in-time copy while the server keeps serving; copying
  the `.db` file directly is not a backup (committed pages may still be in `-wal`).
- The copy is checked with `PRAGMA integrity_check`, and `manifest.json` records its sha256, size
  and per-table row counts.
- With `LX_BACKUP_PASSPHRASE` the snapshot is written as AES-256-GCM (`luxora.db.enc`, scrypt
  key derivation). Without it the backup is plaintext and the tool says so.
- `backups/` is git- and docker-ignored.
- `--keep N` (or `LX_BACKUP_KEEP`) keeps the newest N sets in the output directory; without it
  nothing is deleted. Only sets this tool wrote are ever pruned.
- `--upload` (or any `LX_BACKUP_S3_BUCKET`) copies each set to S3-compatible storage
  (`LX_BACKUP_S3_ACCESS`, `_SECRET`, `_REGION`, `_ENDPOINT`, `_PREFIX`). Only encrypted sets are
  uploaded unless `LX_BACKUP_ALLOW_PLAINTEXT_UPLOAD=1`; an upload failure exits non-zero.
- The last line of output is JSON (`ok`, `backup`, `uploaded`, `kept`, `pruned`) for a timer or
  cron job. `systemd/luxora-backup.{service,timer}` runs it nightly with `--keep 14` semantics and
  reads the passphrase and S3 credentials from `/etc/luxora/backup.env`.

### Schedule and retention (recommended — to be confirmed by the owner)

| | Value |
|---|---|
| Frequency | hourly (cron or a systemd timer on the host) |
| Retention | 48 hourly, 30 daily, 12 monthly |
| Off-host copy | every backup copied to object storage in a different account or region, with versioning and an expiry policy |
| Encryption | always set `LX_BACKUP_PASSPHRASE`; store it in the secret store, not with the backups |
| Alert | the job exits non-zero on any failure — alert on a failed run and on no new backup for 2 hours |

Example host cron (the destination, copy command and alerting are environment-specific):

```cron
17 * * * *  cd /srv/luxora && LX_BACKUP_PASSPHRASE="$(cat /run/secrets/backup_pass)" node scripts/backup.js --db /srv/luxora/data/luxora.db --out /srv/backups || /usr/local/bin/alert "luxora backup failed"
```

### Recovery objectives

| | Target with hourly backups | Measured |
|---|---|---|
| RPO (data loss) | ≤ 1 hour | — depends on the schedule |
| RTO (time to restore) | ≤ 30 minutes | encrypted 27 MB / 103k-row backup: restore + full verification 0.4 s, boot to ready 4.7 s (4 vCPU) — the rest of the RTO is people and access |

Orders taken between the last backup and the failure are lost from the database. Reconcile them
against the payment provider's records and order notification mail.

## Restore

```bash
# 1. verify without touching anything
LX_BACKUP_PASSPHRASE=… node scripts/restore.js /backups/luxora-<stamp> --verify-only
# 2. stop the application (it must not hold the database open)
docker compose stop luxora
# 3. see the plan (verifies everything, changes nothing), then restore into place — refuses to
#    overwrite unless --force, and refuses while a serve.sh server's pid file is live. The current
#    database and its -wal/-shm are moved aside to <db>.pre-restore-<stamp>, never deleted.
LX_BACKUP_PASSPHRASE=… node scripts/restore.js /backups/luxora-<stamp> --to /path/to/luxora.db --force --dry-run
LX_BACKUP_PASSPHRASE=… node scripts/restore.js /backups/luxora-<stamp> --to /path/to/luxora.db --force
# 4. start, with the SAME LUXORA_MASTER_KEY / LUXORA_PEPPER (or the same master.json)
docker compose start luxora
curl -fsS https://<host>/readyz
```

`restore.js` refuses, without changing anything, when: the file's checksum differs from the
manifest, the passphrase is wrong or the ciphertext was altered (GCM authentication), the
decrypted data's checksum differs, `integrity_check` fails, or any table's row count differs
from the manifest.

A set written by the earlier tool (a `files` checksum map, possibly with `master.json` /
`registry.json` beside the database) still restores: its database is checksummed and integrity-
checked, and any key files in it are reported and **left unrestored** — keys come back only from
the secret store, by the procedure above.

## Restore drill

Run monthly and after every change to the backup job, on a machine that is **not** production:

1. Take the latest off-host backup.
2. `scripts/restore.js <dir> --to /tmp/drill/luxora.db`.
3. Boot a server on it: `LX_DB=/tmp/drill/luxora.db PORT=8999 NODE_ENV=production … node server.js`
   with the production key and pepper (from the secret store, never copied to disk).
4. `curl localhost:8999/readyz`, sign in to the console, open the latest orders.
5. Record the date, backup stamp, row counts and time taken.

CI runs a backup and a restore of the boot-smoke database on every push
(`.github/workflows/ci.yml`); `test/production.js` covers live backup, encryption, wrong
passphrase, tampering and no-overwrite, and `test/backup.js` the CLI end to end: retention,
dry run, the replaced file kept aside, no keyring in any set, no plaintext upload, older sets.

## Disk-full behaviour (measured)

When the volume fills, every API request fails with `500 {"error":"internal"}` — reads included,
because each request touches the session table — while `/healthz` and `/readyz` keep answering
200. `/readyz` reports `diskFreeMb`; alert on it (OPERATIONS_RUNBOOK.md). When space is freed the
server recovers without a restart, and the database passed `integrity_check` after the episode.

## Schema changes

The schema is created and evolved at boot by `lib/db.js` (`CREATE TABLE IF NOT EXISTS` and
additive `ADD COLUMN` checks; no destructive DDL). There is no down-migration: to undo a release,
redeploy the previous image (additive columns are ignored by older code) or restore the
pre-upgrade backup. Always back up before an upgrade.
