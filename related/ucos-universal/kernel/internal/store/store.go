// Package store opens the kernel database and runs work inside role- and tenant-scoped transactions.
// Every tenant transaction sets app.tenant_id and switches to a non-bypass role, so row-level security
// (ADR-020) applies even when the pool connects as a privileged user.
package store

import (
	"context"
	"fmt"
	"regexp"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

// Roles created by db/migrations.
const (
	RoleApp      = "ucos_app"
	RoleAppender = "ucos_audit_appender"
	RoleRelay    = "ucos_relay"
	RoleTriggers = "ucos_trigger_engine"
)

var roleRe = regexp.MustCompile(`^ucos_[a-z_]+$`)

type DB struct{ Pool *pgxpool.Pool }

func Open(ctx context.Context, dsn string) (*DB, error) {
	pool, err := pgxpool.New(ctx, dsn)
	if err != nil {
		return nil, err
	}
	if err := pool.Ping(ctx); err != nil {
		pool.Close()
		return nil, err
	}
	return &DB{Pool: pool}, nil
}

func (d *DB) Close() { d.Pool.Close() }

// InTenant runs fn in a transaction scoped to tenant and role. fn's error rolls the transaction back.
func (d *DB) InTenant(ctx context.Context, tenant, role string, fn func(pgx.Tx) error) error {
	if tenant == "" {
		return fmt.Errorf("store: empty tenant")
	}
	return d.inRole(ctx, role, func(tx pgx.Tx) error {
		if _, err := tx.Exec(ctx, `SELECT set_config('app.tenant_id', $1, true)`, tenant); err != nil {
			return err
		}
		return fn(tx)
	})
}

// AsRole runs fn as a cross-tenant system role (relay, appender, trigger engine) with no tenant context.
func (d *DB) AsRole(ctx context.Context, role string, fn func(pgx.Tx) error) error {
	return d.inRole(ctx, role, fn)
}

func (d *DB) inRole(ctx context.Context, role string, fn func(pgx.Tx) error) (err error) {
	if !roleRe.MatchString(role) {
		return fmt.Errorf("store: invalid role %q", role)
	}
	tx, err := d.Pool.Begin(ctx)
	if err != nil {
		return err
	}
	defer func() {
		if err != nil {
			_ = tx.Rollback(ctx)
		}
	}()
	if _, err = tx.Exec(ctx, "SET LOCAL ROLE "+pgx.Identifier{role}.Sanitize()); err != nil {
		return err
	}
	if err = fn(tx); err != nil {
		return err
	}
	return tx.Commit(ctx)
}
