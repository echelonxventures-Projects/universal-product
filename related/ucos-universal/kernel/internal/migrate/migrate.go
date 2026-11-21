// Package migrate applies db/migrations/*.sql to any PostgreSQL 16+ server (managed or self-hosted) in file-name
// order. Each file runs in its own transaction and is recorded with its digest; an applied file that later
// changes is refused, so migrations are append-only. A session advisory lock lets several replicas start at once.
package migrate

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"path/filepath"
	"sort"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

const lockKey = 0x75636f73 // "ucos"

// Apply runs pending migrations from dir and returns the names applied.
func Apply(ctx context.Context, pool *pgxpool.Pool, dir string) ([]string, error) {
	files, err := filepath.Glob(filepath.Join(dir, "*.sql"))
	if err != nil {
		return nil, err
	}
	if len(files) == 0 {
		return nil, fmt.Errorf("migrate: no migrations in %s", dir)
	}
	sort.Strings(files)
	conn, err := pool.Acquire(ctx)
	if err != nil {
		return nil, err
	}
	defer conn.Release()
	if _, err := conn.Exec(ctx, `SELECT pg_advisory_lock($1)`, lockKey); err != nil {
		return nil, err
	}
	defer conn.Exec(context.WithoutCancel(ctx), `SELECT pg_advisory_unlock($1)`, lockKey) //nolint:errcheck
	if _, err := conn.Exec(ctx, `CREATE TABLE IF NOT EXISTS public.ucos_schema_migrations (
		name text PRIMARY KEY, sha256 text NOT NULL, applied_at timestamptz NOT NULL DEFAULT now())`); err != nil {
		return nil, err
	}
	applied := map[string]string{}
	rows, err := conn.Query(ctx, `SELECT name, sha256 FROM public.ucos_schema_migrations`)
	if err != nil {
		return nil, err
	}
	for rows.Next() {
		var n, s string
		if err := rows.Scan(&n, &s); err != nil {
			return nil, err
		}
		applied[n] = s
	}
	if err := rows.Err(); err != nil {
		return nil, err
	}
	var done []string
	for _, f := range files {
		sql, err := os.ReadFile(f)
		if err != nil {
			return done, err
		}
		sum := sha256.Sum256(sql)
		digest, name := hex.EncodeToString(sum[:]), filepath.Base(f)
		if prev, ok := applied[name]; ok {
			if prev != digest {
				return done, fmt.Errorf("migrate: %s changed after it was applied (migrations are append-only)", name)
			}
			continue
		}
		err = pgx.BeginFunc(ctx, conn.Conn(), func(tx pgx.Tx) error {
			if _, err := tx.Exec(ctx, string(sql)); err != nil {
				return err
			}
			_, err := tx.Exec(ctx, `INSERT INTO public.ucos_schema_migrations (name, sha256) VALUES ($1, $2)`, name, digest)
			return err
		})
		if err != nil {
			return done, fmt.Errorf("migrate: %s: %w", name, err)
		}
		done = append(done, name)
	}
	return done, nil
}

// Pending returns how many migrations in dir are not yet applied (readiness: the kernel serves only on a current
// schema). A database that was never migrated by this package counts every file as pending.
func Pending(ctx context.Context, pool *pgxpool.Pool, dir string) (int, error) {
	files, err := filepath.Glob(filepath.Join(dir, "*.sql"))
	if err != nil {
		return 0, err
	}
	var applied int
	err = pool.QueryRow(ctx, `SELECT count(*) FROM public.ucos_schema_migrations WHERE name = ANY($1)`, names(files)).Scan(&applied)
	if err != nil {
		var exists bool
		if e := pool.QueryRow(ctx, `SELECT to_regclass('public.ucos_schema_migrations') IS NOT NULL`).Scan(&exists); e == nil && !exists {
			return len(files), nil
		}
		return 0, err
	}
	return len(files) - applied, nil
}

func names(files []string) []string {
	out := make([]string, len(files))
	for i, f := range files {
		out[i] = filepath.Base(f)
	}
	return out
}
