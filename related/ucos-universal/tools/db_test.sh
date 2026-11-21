#!/usr/bin/env bash
# Apply db/migrations to a throwaway PostgreSQL cluster and run db/tests/*.sql.
# The cluster listens only on a private Unix socket in a temp directory and is deleted afterwards,
# so it never touches a database already running on the machine.
#   tools/db_test.sh                       (needs PostgreSQL 16+ server binaries: initdb, pg_ctl, psql)
#   tools/db_test.sh --exec <command...>   also runs <command> with UCOS_TEST_DATABASE_URL pointing at a fresh,
#                                          migrated database (used for the Go integration tests)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
find_bin() {
  if command -v initdb >/dev/null 2>&1; then dirname "$(command -v initdb)"; return; fi
  for d in /usr/lib/postgresql/*/bin /opt/homebrew/opt/postgresql@*/bin /usr/local/opt/postgresql@*/bin; do
    [[ -x "$d/initdb" ]] && { echo "$d"; return; }
  done
  return 1
}
BIN="$(find_bin)" || { echo "PostgreSQL server binaries not found (initdb)" >&2; exit 3; }
WORK="$(mktemp -d)"
trap '"$BIN/pg_ctl" -D "$WORK/data" -m immediate stop >/dev/null 2>&1 || true; rm -rf "$WORK"' EXIT
"$BIN/initdb" -D "$WORK/data" -U postgres --auth=trust -E UTF8 --locale=C >/dev/null
"$BIN/pg_ctl" -D "$WORK/data" -o "-k $WORK -c listen_addresses='' -c fsync=off" -l "$WORK/log" -w start >/dev/null
PSQL=("$BIN/psql" -h "$WORK" -U postgres -X -q -v ON_ERROR_STOP=1)
"${PSQL[@]}" -d postgres -c "CREATE DATABASE ucos_test"
for m in "$ROOT"/db/migrations/*.sql; do
  "${PSQL[@]}" -d ucos_test -f "$m" || { echo "migration failed: $(basename "$m")" >&2; exit 1; }
done
echo "applied $(ls "$ROOT"/db/migrations/*.sql | wc -l | tr -d ' ') migrations ($("$BIN/postgres" --version))"
for t in "$ROOT"/db/tests/*.sql; do
  "${PSQL[@]}" -d ucos_test -f "$t"
done
if [[ "${1:-}" == "--exec" ]]; then
  shift
  "${PSQL[@]}" -d postgres -c "CREATE DATABASE ucos_it"
  for m in "$ROOT"/db/migrations/*.sql; do "${PSQL[@]}" -d ucos_it -f "$m"; done
  UCOS_TEST_DATABASE_URL="host=$WORK user=postgres dbname=ucos_it sslmode=disable" "$@"
fi
