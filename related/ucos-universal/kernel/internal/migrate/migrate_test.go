package migrate

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

// Applies every migration to an empty database, then proves re-runs are no-ops and edits are refused.
func TestApplyToEmptyDatabase(t *testing.T) {
	dsn := os.Getenv("UCOS_TEST_DATABASE_URL")
	if dsn == "" {
		t.Skip("UCOS_TEST_DATABASE_URL not set (run through tools/db_test.sh --exec)")
	}
	ctx := context.Background()
	admin, err := pgxpool.New(ctx, dsn)
	if err != nil {
		t.Fatal(err)
	}
	defer admin.Close()
	name := fmt.Sprintf("ucos_migrate_%d", time.Now().UnixNano())
	if _, err := admin.Exec(ctx, "CREATE DATABASE "+name); err != nil {
		t.Fatal(err)
	}
	defer admin.Exec(context.Background(), "DROP DATABASE "+name+" WITH (FORCE)") //nolint:errcheck
	pool, err := pgxpool.New(ctx, strings.Replace(dsn, "dbname=ucos_it", "dbname="+name, 1))
	if err != nil {
		t.Fatal(err)
	}
	defer pool.Close()
	if n, err := Pending(ctx, pool, "../../../db/migrations"); err != nil || n == 0 {
		t.Fatalf("an empty database must report pending migrations: %d %v", n, err)
	}

	src, _ := filepath.Glob("../../../db/migrations/*.sql")
	done, err := Apply(ctx, pool, "../../../db/migrations")
	if err != nil {
		t.Fatal(err)
	}
	if len(done) != len(src) {
		t.Fatalf("applied %d of %d migrations", len(done), len(src))
	}
	var forced bool
	if err := pool.QueryRow(ctx, `SELECT relforcerowsecurity FROM pg_class WHERE oid = 'kernel.objects'::regclass`).Scan(&forced); err != nil || !forced {
		t.Fatalf("kernel schema not in place: forced=%v err=%v", forced, err)
	}
	if n, err := Pending(ctx, pool, "../../../db/migrations"); err != nil || n != 0 {
		t.Fatalf("pending after apply: %d %v", n, err)
	}
	if again, err := Apply(ctx, pool, "../../../db/migrations"); err != nil || len(again) != 0 {
		t.Fatalf("second run must be a no-op: %v %v", again, err)
	}

	// An applied migration that changes is refused.
	dir := t.TempDir()
	for _, f := range src {
		b, _ := os.ReadFile(f)
		if strings.HasPrefix(filepath.Base(f), "0001") {
			b = append(b, []byte("\n-- edited\n")...)
		}
		_ = os.WriteFile(filepath.Join(dir, filepath.Base(f)), b, 0o644)
	}
	if _, err := Apply(ctx, pool, dir); err == nil || !strings.Contains(err.Error(), "append-only") {
		t.Fatalf("edited migration must be refused, got %v", err)
	}
}
