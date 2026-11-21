// Package relay publishes outbox rows to the event bus (ADR-007, KERNEL-DESIGN §6). Delivery is at least once:
// a row is marked published only after the publisher accepted it, so consumers must be idempotent (EVT-L6).
package relay

import (
	"context"

	"github.com/jackc/pgx/v5"

	"ucos.io/kernel/internal/store"
)

// Publisher sends one event; implementations exist for Kafka-API buses and for tests.
type Publisher interface {
	Publish(ctx context.Context, topic, key string, value []byte) error
}

type Relay struct {
	DB  *store.DB
	Pub Publisher
}

// Drain publishes up to limit unpublished rows, oldest first, and returns how many were published.
// Several relays can run at once: rows are claimed with SKIP LOCKED.
func (r *Relay) Drain(ctx context.Context, limit int) (int, error) {
	n := 0
	err := r.DB.AsRole(ctx, store.RoleRelay, func(tx pgx.Tx) error {
		rows, err := tx.Query(ctx, `SELECT seq, topic, partition_key, event FROM kernel.outbox
			WHERE published_at IS NULL ORDER BY seq LIMIT $1 FOR UPDATE SKIP LOCKED`, limit)
		if err != nil {
			return err
		}
		type row struct {
			seq        int64
			topic, key string
			event      []byte
		}
		var rs []row
		for rows.Next() {
			var x row
			if err := rows.Scan(&x.seq, &x.topic, &x.key, &x.event); err != nil {
				return err
			}
			rs = append(rs, x)
		}
		if err := rows.Err(); err != nil {
			return err
		}
		var done []int64
		for _, x := range rs {
			if err := r.Pub.Publish(ctx, x.topic, x.key, x.event); err != nil {
				return err // nothing is marked; the batch is retried
			}
			done = append(done, x.seq)
		}
		if len(done) > 0 {
			if _, err := tx.Exec(ctx, `UPDATE kernel.outbox SET published_at = now() WHERE seq = ANY($1)`, done); err != nil {
				return err
			}
		}
		n = len(done)
		return nil
	})
	return n, err
}
