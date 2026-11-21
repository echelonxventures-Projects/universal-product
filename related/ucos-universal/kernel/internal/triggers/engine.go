// Package triggers fires due Temporal triggers (U13 TMP-L4). Each firing runs the trigger's target command
// through the command bus in the trigger's tenant, with a deterministic idempotency key, so a firing that is
// retried after a crash cannot apply twice.
package triggers

import (
	"context"
	"fmt"
	"strconv"
	"strings"
	"time"

	"github.com/jackc/pgx/v5"

	"ucos.io/kernel/internal/bus"
	"ucos.io/kernel/internal/store"
	"ucos.io/kernel/pkg/ctxenv"
	"ucos.io/kernel/pkg/temporal"
)

const maxAttempts = 5

type Engine struct {
	DB  *store.DB
	Bus *bus.Bus
}

type due struct {
	tenant, id, op, target, rrule, tz string
	payload                           []byte
	fireAt                            time.Time
	attempts                          int
}

// FireDue runs every trigger due at now and returns how many fired successfully.
func (e *Engine) FireDue(ctx context.Context, now time.Time) (int, error) {
	fired := 0
	err := e.DB.AsRole(ctx, store.RoleTriggers, func(tx pgx.Tx) error {
		rows, err := tx.Query(ctx, `SELECT tenant_id, id, target_operation, coalesce(target_id, ''), coalesce(recurrence, ''),
			coalesce(tz, ''), payload, fire_at, attempts
			FROM kernel.triggers WHERE status = 'scheduled' AND fire_at <= $1 ORDER BY fire_at LIMIT 100 FOR UPDATE SKIP LOCKED`, now)
		if err != nil {
			return err
		}
		var ds []due
		for rows.Next() {
			var d due
			if err := rows.Scan(&d.tenant, &d.id, &d.op, &d.target, &d.rrule, &d.tz, &d.payload, &d.fireAt, &d.attempts); err != nil {
				return err
			}
			ds = append(ds, d)
		}
		if err := rows.Err(); err != nil {
			return err
		}
		for _, d := range ds {
			resp, err := e.Bus.Execute(ctx, bus.Request{
				OperationID: d.op, TargetID: d.target, Payload: d.payload,
				IdempotencyKey: fmt.Sprintf("trigger:%s:%d", d.id, d.fireAt.Unix()),
				Envelope:       systemEnvelope(d.tenant, now),
			})
			if err != nil || resp.Status >= 500 {
				backoff := time.Duration(1<<min(d.attempts, 6)) * time.Minute
				status := "scheduled"
				if d.attempts+1 >= maxAttempts {
					status = "failed"
				}
				if _, err := tx.Exec(ctx, `UPDATE kernel.triggers SET attempts = attempts + 1, fire_at = $3, status = $4
					WHERE tenant_id = $1 AND id = $2`, d.tenant, d.id, now.Add(backoff), status); err != nil {
					return err
				}
				continue
			}
			next, recurring, err := Next(d.rrule, d.tz, d.fireAt)
			if err != nil {
				return err
			}
			if recurring {
				_, err = tx.Exec(ctx, `UPDATE kernel.triggers SET fire_at = $3, attempts = 0 WHERE tenant_id = $1 AND id = $2`, d.tenant, d.id, next)
			} else {
				_, err = tx.Exec(ctx, `UPDATE kernel.triggers SET status = 'fired' WHERE tenant_id = $1 AND id = $2`, d.tenant, d.id)
			}
			if err != nil {
				return err
			}
			fired++
		}
		return nil
	})
	return fired, err
}

// systemEnvelope is the context under which the trigger engine acts for a tenant.
func systemEnvelope(tenant string, now time.Time) *ctxenv.Envelope {
	return &ctxenv.Envelope{
		V: 1, Tenant: tenant, Actor: ctxenv.Actor{Identity: "ucos:service:trigger-engine", Kind: "service"},
		Roles: []string{"system"}, Jurisdiction: map[string][]string{}, Locale: "en", Currency: "XXX", TZ: "UTC",
		Time: ctxenv.Time{Now: now}, Frame: ctxenv.Frame{Reality: "physical"}, Channel: "system",
		Risk: ctxenv.Risk{Band: "unknown"}, Purpose: "scheduled-work", Exp: now.Add(time.Minute).Unix(),
	}
}

// Next returns the next firing after prev for the supported RRULE subset:
// FREQ=DAILY;BYHOUR=h;BYMINUTE=m in an IANA zone (wall-clock time kept across daylight-saving changes).
// An empty rule means a one-off trigger.
func Next(rrule, tz string, prev time.Time) (time.Time, bool, error) {
	if rrule == "" {
		return time.Time{}, false, nil
	}
	parts := map[string]string{}
	for _, kv := range strings.Split(rrule, ";") {
		k, v, _ := strings.Cut(kv, "=")
		parts[strings.ToUpper(k)] = v
	}
	if parts["FREQ"] != "DAILY" || len(parts) > 3 {
		return time.Time{}, false, fmt.Errorf("triggers: unsupported recurrence %q (supported: FREQ=DAILY;BYHOUR;BYMINUTE)", rrule)
	}
	h, err1 := strconv.Atoi(parts["BYHOUR"])
	m, err2 := strconv.Atoi(parts["BYMINUTE"])
	loc, err3 := time.LoadLocation(tz)
	if err1 != nil || err2 != nil || err3 != nil || h > 23 || m > 59 {
		return time.Time{}, false, fmt.Errorf("triggers: invalid recurrence %q in %q", rrule, tz)
	}
	occ := temporal.DailyAt(loc, h, m, prev.Add(time.Second), prev.Add(49*time.Hour))
	if len(occ) == 0 {
		return time.Time{}, false, fmt.Errorf("triggers: no next occurrence for %q", rrule)
	}
	return occ[0], true, nil
}
