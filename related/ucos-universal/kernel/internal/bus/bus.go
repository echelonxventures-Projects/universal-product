// Package bus is the command bus (KERNEL-DESIGN §3). Every state change enters through Execute, which runs in
// one tenant transaction:
//
//  1. claim the idempotency key (a concurrent duplicate blocks on the unique key, then reads the stored answer);
//  2. run the pack's handler in a savepoint, with object writes, outbox events and a trigger scheduler;
//  3. append the audit record (AUD-L1: no audit, no change);
//  4. store the response under the key and commit.
//
// A handler Problem rolls back to the savepoint, so its state changes vanish but its answer is still stored.
package bus

import (
	"context"
	"crypto/sha256"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/jackc/pgx/v5"

	"ucos.io/kernel/internal/metrics"
	"ucos.io/kernel/internal/store"
	"ucos.io/kernel/pkg/ctxenv"
	"ucos.io/kernel/pkg/money"
	"ucos.io/kernel/pkg/ugid"
	"ucos.io/kernel/sdk/pack"
)

// Request is one command invocation.
type Request struct {
	OperationID    string // "<slug>:<Command>"
	TargetID       string
	Payload        json.RawMessage
	IdempotencyKey string
	Envelope       *ctxenv.Envelope
}

// Response is what the caller receives (and what a retry with the same key receives again).
type Response struct {
	Status  int             `json:"status"`
	Body    json.RawMessage `json:"body,omitempty"`
	Problem *pack.Problem   `json:"problem,omitempty"`
}

type Bus struct {
	db       *store.DB
	cell     string
	clock    func() time.Time
	commands map[string]pack.CommandHandler
	queries  map[string]pack.QueryHandler
	caps     map[string]string // operation -> capability id
	ttl      time.Duration
	// Active, when set, gates every operation on the tenant's active blueprint (activation, U73).
	Active func(ctx context.Context, tenant, capability string) (bool, error)
	// PEP, when set, authorizes every operation before it reaches a pack (policy enforcement point, U03).
	// It returns an empty code to allow, or a registry code (POL_DENIED, …) and a detail to refuse.
	PEP func(env *ctxenv.Envelope, op, kind, capability, target string) (code, detail string)
}

func New(db *store.DB, cell string, clock func() time.Time) *Bus {
	if clock == nil {
		clock = time.Now
	}
	return &Bus{db: db, cell: cell, clock: clock, commands: map[string]pack.CommandHandler{}, queries: map[string]pack.QueryHandler{}, caps: map[string]string{}, ttl: 24 * time.Hour}
}

// Register adds a pack's commands under "<slug>:<Command>", slug being the first segment of its capability id.
func (b *Bus) Register(p pack.Pack) {
	slug := strings.SplitN(p.CapabilityID(), ".", 2)[0]
	for name, h := range p.Commands() {
		op := slug + ":" + name
		b.commands[op] = h
		b.caps[op] = p.CapabilityID()
	}
	for name, h := range p.Queries() {
		op := slug + ":" + name
		b.queries[op] = h
		b.caps[op] = p.CapabilityID()
	}
}

var (
	opsTotal = metrics.NewCounter("ucos_bus_operations_total",
		"Commands and queries by operation, outcome status and problem code.", "kind", "operation", "status", "code")
	opsDuration = metrics.NewHistogram("ucos_bus_operation_duration_seconds",
		"Command and query latency, including the tenant transaction.", metrics.DurationBuckets, "kind", "operation")
)

func (b *Bus) observe(kind, op string, resp Response, err error, start time.Time) {
	if _, ok := b.caps[op]; !ok {
		op = "unknown" // bounded label values: only registered operations are named
	}
	status, code := strconv.Itoa(resp.Status), ""
	if resp.Problem != nil {
		code = resp.Problem.Code
	}
	if err != nil {
		status, code = "error", "INFRASTRUCTURE"
	}
	opsTotal.Inc(kind, op, status, code)
	opsDuration.Since(start, kind, op)
}

func problem(status int, code, title string) Response {
	return Response{Status: status, Problem: pack.NewProblem(status, code, title, "")}
}

// Execute runs a command. The returned error is reserved for infrastructure failures (retry is safe);
// business outcomes, including problems, come back in the Response.
func (b *Bus) Execute(ctx context.Context, req Request) (Response, error) {
	start := time.Now()
	resp, err := b.execute(ctx, req)
	b.observe("command", req.OperationID, resp, err, start)
	return resp, err
}

func (b *Bus) execute(ctx context.Context, req Request) (Response, error) {
	now := b.clock().UTC()
	if req.Envelope == nil {
		return problem(http.StatusUnauthorized, "CTX_MISSING", "context envelope required"), nil
	}
	if err := req.Envelope.Validate(now); err != nil {
		return problem(http.StatusUnauthorized, "CTX_INVALID", err.Error()), nil
	}
	h, ok := b.commands[req.OperationID]
	if !ok {
		return problem(http.StatusNotFound, "OPERATION_UNKNOWN", "unknown operation "+req.OperationID), nil
	}
	if r, err := b.activated(ctx, req); err != nil || r != nil {
		return derefOr(r), err
	}
	if r := b.authorize(req, "command"); r != nil {
		return *r, nil
	}
	if len(req.IdempotencyKey) < 8 {
		return problem(http.StatusBadRequest, "IDEMPOTENCY_KEY_REQUIRED", "an Idempotency-Key of at least 8 characters is required"), nil
	}
	sum := sha256.Sum256([]byte(req.OperationID + "\x00" + req.TargetID + "\x00" + string(req.Payload)))
	hash := sum[:]
	tenant := req.Envelope.Tenant

	var resp Response
	err := b.db.InTenant(ctx, tenant, store.RoleApp, func(tx pgx.Tx) error {
		tag, err := tx.Exec(ctx, `INSERT INTO kernel.cmd_idempotency (tenant_id, key, request_hash, status, expires_at)
			VALUES ($1, $2, $3, 'in_progress', $4) ON CONFLICT DO NOTHING`, tenant, req.IdempotencyKey, hash, now.Add(b.ttl))
		if err != nil {
			return err
		}
		if tag.RowsAffected() == 0 { // the key was used before: replay or reject
			var prevHash []byte
			var status string
			var stored []byte
			if err := tx.QueryRow(ctx, `SELECT request_hash, status, coalesce(response_raw, convert_to(response::text, 'UTF8')) FROM kernel.cmd_idempotency
				WHERE tenant_id = $1 AND key = $2`, tenant, req.IdempotencyKey).Scan(&prevHash, &status, &stored); err != nil {
				return err
			}
			switch {
			case string(prevHash) != string(hash):
				resp = problem(http.StatusConflict, "IDEMPOTENCY_KEY_REUSED", "this Idempotency-Key was used with a different request")
			case status != "completed":
				resp = problem(http.StatusConflict, "IN_PROGRESS", "the original request is still running")
			default:
				return json.Unmarshal(stored, &resp)
			}
			return nil
		}

		k := &kernelTx{ctx: ctx, tx: tx, bus: b, tenant: tenant, capability: b.caps[req.OperationID], now: now}
		cc := &pack.CommandCtx{Context: req.Envelope, Tx: k, Temporal: k, Allocate: money.Allocate}
		if _, err := tx.Exec(ctx, `SAVEPOINT handler`); err != nil {
			return err
		}
		result, herr := h(cc, withTarget(req))
		var p *pack.Problem
		switch {
		case errors.As(herr, &p):
			if _, err := tx.Exec(ctx, `ROLLBACK TO SAVEPOINT handler`); err != nil {
				return err
			}
			resp = Response{Status: p.Status, Problem: p}
		case herr != nil:
			return herr // infrastructure failure: roll everything back, the key is released
		default:
			body, err := json.Marshal(result.Body)
			if err != nil {
				return err
			}
			resp = Response{Status: result.Status, Body: body}
		}

		audit := map[string]any{
			"action": req.OperationID, "target": req.TargetID, "status": resp.Status,
			"actor": req.Envelope.Actor, "idempotencyKey": req.IdempotencyKey,
			"requestHash": fmt.Sprintf("%x", hash), "at": now.Format(time.RFC3339Nano),
		}
		if resp.Problem != nil {
			audit["problem"] = resp.Problem.Code
		}
		rec, _ := json.Marshal(audit)
		if _, err := tx.Exec(ctx, `INSERT INTO kernel.audit_pending (tenant_id, record) VALUES ($1, $2::jsonb)`, tenant, string(rec)); err != nil {
			return err
		}
		stored, _ := json.Marshal(resp)
		_, err = tx.Exec(ctx, `UPDATE kernel.cmd_idempotency SET status = 'completed', response = $3::jsonb, response_raw = $5, http_status = $4
			WHERE tenant_id = $1 AND key = $2`, tenant, req.IdempotencyKey, string(stored), resp.Status, stored)
		return err
	})
	return resp, err
}

// Query runs a read-only query in a tenant transaction (no idempotency, no audit of reads in Phase 0).
func (b *Bus) Query(ctx context.Context, req Request) (Response, error) {
	start := time.Now()
	resp, err := b.query(ctx, req)
	b.observe("query", req.OperationID, resp, err, start)
	return resp, err
}

func (b *Bus) query(ctx context.Context, req Request) (Response, error) {
	now := b.clock().UTC()
	if req.Envelope == nil {
		return problem(http.StatusUnauthorized, "CTX_MISSING", "context envelope required"), nil
	}
	if err := req.Envelope.Validate(now); err != nil {
		return problem(http.StatusUnauthorized, "CTX_INVALID", err.Error()), nil
	}
	h, ok := b.queries[req.OperationID]
	if !ok {
		return problem(http.StatusNotFound, "OPERATION_UNKNOWN", "unknown operation "+req.OperationID), nil
	}
	if r, err := b.activated(ctx, req); err != nil || r != nil {
		return derefOr(r), err
	}
	if r := b.authorize(req, "query"); r != nil {
		return *r, nil
	}
	var resp Response
	err := b.db.InTenant(ctx, req.Envelope.Tenant, store.RoleApp, func(tx pgx.Tx) error {
		if _, err := tx.Exec(ctx, `SET TRANSACTION READ ONLY`); err != nil {
			return err
		}
		k := &kernelTx{ctx: ctx, tx: tx, bus: b, tenant: req.Envelope.Tenant, capability: b.caps[req.OperationID], now: now}
		result, herr := h(&pack.CommandCtx{Context: req.Envelope, Tx: k, Temporal: k, Allocate: money.Allocate}, withTarget(req))
		var p *pack.Problem
		switch {
		case errors.As(herr, &p):
			resp = Response{Status: p.Status, Problem: p}
		case herr != nil:
			return herr
		default:
			body, err := json.Marshal(result.Body)
			if err != nil {
				return err
			}
			resp = Response{Status: result.Status, Body: body}
		}
		return nil
	})
	return resp, err
}

// activated returns a problem response when the capability is not in the tenant's active blueprint.
func (b *Bus) activated(ctx context.Context, req Request) (*Response, error) {
	if b.Active == nil {
		return nil, nil
	}
	ok, err := b.Active(ctx, req.Envelope.Tenant, b.caps[req.OperationID])
	if err != nil {
		return nil, err
	}
	if !ok {
		r := problem(http.StatusForbidden, "ACTIVATION_DENIED", "this capability is not active for the tenant")
		return &r, nil
	}
	return nil, nil
}

// authorize asks the policy enforcement point; a refusal is a 403 problem with the policy's code.
func (b *Bus) authorize(req Request, kind string) *Response {
	if b.PEP == nil {
		return nil
	}
	code, detail := b.PEP(req.Envelope, req.OperationID, kind, b.caps[req.OperationID], req.TargetID)
	if code == "" {
		return nil
	}
	r := Response{Status: http.StatusForbidden, Problem: pack.NewProblem(http.StatusForbidden, code, "refused by policy", detail)}
	return &r
}

func derefOr(r *Response) Response {
	if r == nil {
		return Response{}
	}
	return *r
}

// Operations lists registered command and query ids (the gateway routes only to these).
func (b *Bus) Operations() map[string]bool {
	out := map[string]bool{}
	for op := range b.commands {
		out[op] = true
	}
	for op := range b.queries {
		out[op] = true
	}
	return out
}

// The payload handed to handlers carries the target id as "_target" so handlers stay pure functions of input.
func withTarget(req Request) json.RawMessage {
	if req.TargetID == "" {
		return req.Payload
	}
	var m map[string]any
	if json.Unmarshal(req.Payload, &m) != nil || m == nil {
		m = map[string]any{}
	}
	m["_target"] = req.TargetID
	out, _ := json.Marshal(m)
	return out
}

// kernelTx implements pack.Tx and pack.Temporal on the command's transaction.
type kernelTx struct {
	ctx        context.Context
	tx         pgx.Tx
	bus        *Bus
	tenant     string
	capability string
	now        time.Time
}

var errNotFound = pack.NewProblem(http.StatusNotFound, "OBJECT_NOT_FOUND", "object not found", "")

func (k *kernelTx) Get(typ, id string) (*pack.Object, error) {
	o := &pack.Object{ID: id, Type: typ}
	var status *string
	var attrs, custom []byte
	err := k.tx.QueryRow(k.ctx, `SELECT version, status, attributes, custom FROM kernel.objects WHERE type = $1 AND id = $2`,
		typ, id).Scan(&o.Version, &status, &attrs, &custom)
	if errors.Is(err, pgx.ErrNoRows) {
		return nil, errNotFound
	}
	if err != nil {
		return nil, err
	}
	if status != nil {
		o.Status = *status
	}
	o.Attributes, o.Custom = attrs, custom
	return o, nil
}

func (k *kernelTx) List(typ string, limit int, after string) ([]*pack.Object, error) {
	if limit <= 0 || limit > 500 {
		limit = 50
	}
	rows, err := k.tx.Query(k.ctx, `SELECT id, version, coalesce(status, ''), attributes, custom FROM kernel.objects
		WHERE type = $1 AND id > $2 ORDER BY id LIMIT $3`, typ, after, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var out []*pack.Object
	for rows.Next() {
		o := &pack.Object{Type: typ}
		var attrs, custom []byte
		if err := rows.Scan(&o.ID, &o.Version, &o.Status, &attrs, &custom); err != nil {
			return nil, err
		}
		o.Attributes, o.Custom = attrs, custom
		out = append(out, o)
	}
	return out, rows.Err()
}

func (k *kernelTx) Save(o *pack.Object, expectedVersion int64) error {
	attrs := string(o.Attributes)
	if attrs == "" {
		attrs = "{}"
	}
	custom := string(o.Custom)
	if custom == "" {
		custom = "{}"
	}
	if expectedVersion == 0 {
		if _, err := k.tx.Exec(k.ctx, `INSERT INTO kernel.objects (tenant_id, type, id, version, status, attributes, custom)
			VALUES ($1, $2, $3, 1, $4, $5::jsonb, $6::jsonb)`, k.tenant, o.Type, o.ID, o.Status, attrs, custom); err != nil {
			return err
		}
		o.Version = 1
		return nil
	}
	tag, err := k.tx.Exec(k.ctx, `UPDATE kernel.objects SET version = version + 1, status = $5, attributes = $6::jsonb, custom = $7::jsonb
		WHERE tenant_id = $1 AND type = $2 AND id = $3 AND version = $4`, k.tenant, o.Type, o.ID, expectedVersion, o.Status, attrs, custom)
	if err != nil {
		return err
	}
	if tag.RowsAffected() == 0 {
		return pack.NewProblem(http.StatusConflict, "VERSION_CONFLICT", "the object changed since it was read", "")
	}
	o.Version = expectedVersion + 1
	return nil
}

// Emit writes a CloudEvent to the outbox in the same transaction (ADR-007).
func (k *kernelTx) Emit(eventType, subject string, data any) error {
	parts := strings.Split(eventType, ".")
	if len(parts) != 3 {
		return fmt.Errorf("bus: event type %q must be <universe>.<object>.<verb>", eventType)
	}
	id, err := ugid.New("event", k.now)
	if err != nil {
		return err
	}
	ev := map[string]any{
		"specversion": "1.0", "id": id[len("ucos:event:"):], "type": eventType, "subject": subject,
		"source": "ucos://" + k.bus.cell + "/" + k.capability, "time": k.now.Format(time.RFC3339Nano),
		"datacontenttype": "application/json", "ucostenant": k.tenant, "data": data,
	}
	body, err := json.Marshal(ev)
	if err != nil {
		return err
	}
	topic := fmt.Sprintf("ucos.%s.%s.%s.v1", k.bus.cell, parts[0], parts[1])
	_, err = k.tx.Exec(k.ctx, `INSERT INTO kernel.outbox (tenant_id, event_id, topic, partition_key, event) VALUES ($1, $2, $3, $4, $5::jsonb)`,
		k.tenant, ev["id"], topic, subject, string(body))
	return err
}

func (k *kernelTx) NewID(kind string) (string, error) { return ugid.New(kind, k.now) }

// Now is the command's clock reading (TMP-L1: packs never call time.Now).
func (k *kernelTx) Now() string { return k.now.Format(time.RFC3339Nano) }

// Schedule registers a trigger in the same transaction; the same idempotency key returns the same trigger.
func (k *kernelTx) Schedule(idempotencyKey, at, targetOperation, targetID string, payload any) (string, error) {
	fireAt, err := time.Parse(time.RFC3339, at)
	if err != nil {
		return "", pack.NewProblem(http.StatusBadRequest, "TMP_INVALID_TIMEPOINT", "trigger time must be RFC 3339", err.Error())
	}
	id, err := ugid.New("trigger", k.now)
	if err != nil {
		return "", err
	}
	p, _ := json.Marshal(payload)
	if string(p) == "null" {
		p = []byte("{}")
	}
	var got string
	err = k.tx.QueryRow(k.ctx, `INSERT INTO kernel.triggers (tenant_id, id, idempotency_key, fire_at, target_operation, target_id, payload, status)
		VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, 'scheduled')
		ON CONFLICT (tenant_id, idempotency_key) DO UPDATE SET idempotency_key = EXCLUDED.idempotency_key
		RETURNING id`, k.tenant, id, idempotencyKey, fireAt, targetOperation, targetID, string(p)).Scan(&got)
	return got, err
}
