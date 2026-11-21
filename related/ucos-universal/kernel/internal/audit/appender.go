// Package audit seals pending audit records into the per-tenant, per-day hash chain (U68, KERNEL-DESIGN §12)
// and verifies chains. Hashes are computed by the database function kernel.audit_hash, the same function the
// insert trigger and kernel.audit_verify use, so there is one definition of the chain.
package audit

import (
	"context"
	"time"

	"github.com/jackc/pgx/v5"

	"ucos.io/kernel/internal/store"
)

type Appender struct{ DB *store.DB }

// Seal moves up to limit pending records into their chains and returns how many it sealed.
func (a *Appender) Seal(ctx context.Context, limit int) (int, error) {
	n := 0
	err := a.DB.AsRole(ctx, store.RoleAppender, func(tx pgx.Tx) error {
		rows, err := tx.Query(ctx, `SELECT id, tenant_id, record, (created_at AT TIME ZONE 'UTC')::date
			FROM kernel.audit_pending ORDER BY id LIMIT $1 FOR UPDATE SKIP LOCKED`, limit)
		if err != nil {
			return err
		}
		type pending struct {
			id     int64
			tenant string
			rec    []byte
			day    time.Time
		}
		var ps []pending
		for rows.Next() {
			var p pending
			if err := rows.Scan(&p.id, &p.tenant, &p.rec, &p.day); err != nil {
				return err
			}
			ps = append(ps, p)
		}
		if err := rows.Err(); err != nil {
			return err
		}
		locked := map[string]bool{}
		for _, p := range ps {
			key := p.tenant + "/" + p.day.Format("2006-01-02")
			if !locked[key] { // one writer per chain
				if _, err := tx.Exec(ctx, `SELECT pg_advisory_xact_lock(hashtextextended($1, 0))`, key); err != nil {
					return err
				}
				locked[key] = true
			}
			_, err := tx.Exec(ctx, `
				WITH prev AS (
				  SELECT coalesce(max(seq), 0) AS seq,
				         coalesce((SELECT hash FROM kernel.audit_records r WHERE r.tenant_id = $1 AND r.day = $2 ORDER BY seq DESC LIMIT 1),
				                  decode(repeat('00', 32), 'hex')) AS hash
				  FROM kernel.audit_records WHERE tenant_id = $1 AND day = $2)
				INSERT INTO kernel.audit_records (tenant_id, day, seq, id, rec, prev_hash, hash)
				SELECT $1, $2, prev.seq + 1, $3, $4::jsonb, prev.hash, kernel.audit_hash(prev.hash, $4::jsonb) FROM prev`,
				p.tenant, p.day, "audit-"+itoa(p.id), string(p.rec))
			if err != nil {
				return err
			}
			if _, err := tx.Exec(ctx, `DELETE FROM kernel.audit_pending WHERE id = $1`, p.id); err != nil {
				return err
			}
			n++
		}
		return nil
	})
	return n, err
}

// Verify returns 0 when the chain of tenant on day is intact, otherwise the first broken sequence number.
func (a *Appender) Verify(ctx context.Context, tenant string, day time.Time) (int64, error) {
	var broken *int64
	err := a.DB.AsRole(ctx, store.RoleAppender, func(tx pgx.Tx) error {
		return tx.QueryRow(ctx, `SELECT kernel.audit_verify($1, $2)`, tenant, day).Scan(&broken)
	})
	if err != nil || broken == nil {
		return 0, err
	}
	return *broken, nil
}

func itoa(n int64) string {
	if n == 0 {
		return "0"
	}
	var b [20]byte
	i := len(b)
	for n > 0 {
		i--
		b[i] = byte('0' + n%10)
		n /= 10
	}
	return string(b[i:])
}
