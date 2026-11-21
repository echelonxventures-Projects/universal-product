// Package pack is the Pack SDK contract (KERNEL-DESIGN §7). Packs implement Pack; the kernel provides CommandCtx.
// Packs must not import net/http, database drivers, time.Now, math/rand, schedulers or vendor SDKs outside
// adapters (enforced by `ucos lint` and gates ARCH-TMP-01, ARCH-CTX-01, ARCH-CUR-01).
package pack

import (
	"encoding/json"

	"ucos.io/kernel/pkg/ctxenv"
	"ucos.io/kernel/pkg/money"
)

// Object is a canonical object as seen by a pack (spec/meta/canonical-object.schema.json).
type Object struct {
	ID         string          `json:"id"`
	Type       string          `json:"type"`
	Version    int64           `json:"version"`
	Status     string          `json:"status,omitempty"`
	Attributes json.RawMessage `json:"attributes"`
	Custom     json.RawMessage `json:"customAttributes,omitempty"`
}

// Tx is the tenant-scoped transaction: row-level security is set, and writes, events and audit records
// commit together (transactional outbox, ADR-007; AUD-L1).
type Tx interface {
	Get(typ, id string) (*Object, error)
	Save(obj *Object, expectedVersion int64) error
	Emit(eventType, subject string, data any) error
	NewID(kind string) (string, error)
	// List returns up to limit objects of typ ordered by id, starting after the cursor id ("" for the first page).
	List(typ string, limit int, after string) ([]*Object, error)
}

// Temporal is the only way a pack reads the clock or schedules work (TMP-L4).
type Temporal interface {
	Now() string // TimePoint (RFC 3339 UTC); respects asOf in simulations
	Schedule(idempotencyKey, at, targetOperation, targetID string, payload any) (triggerID string, err error)
}

// Decisions evaluates U53 decision tables.
type Decisions interface {
	Evaluate(decisionID string, inputs map[string]any) (map[string]any, error)
}

// Entitlements checks U28 features and quotas; packs never hard-code plans (ENT-L1).
type Entitlements interface {
	Check(feature string) (bool, error)
	Consume(quota string, amount int64) error
}

// Ports calls outbound ports through the connector runtime (U62); adapters are selected by the blueprint.
type Ports interface {
	Call(port, operation string, request any, response any) error
}

// CommandCtx is what a command handler receives.
type CommandCtx struct {
	Context  *ctxenv.Envelope
	Tx       Tx
	Temporal Temporal
	Decide   Decisions
	Entitled Entitlements
	Ports    Ports
	Allocate func(total money.Money, weights []int64) ([]money.Money, error)
}

type Result struct {
	Status int
	Body   any
}

// Problem is a business error with a registered code (spec/registries/errors.yaml) and an HTTP status.
// A handler that returns a Problem has its state changes rolled back; the problem response is stored under
// the idempotency key, so a retry gets the same answer.
type Problem struct {
	Status int    `json:"status"`
	Code   string `json:"code"`
	Title  string `json:"title"`
	Detail string `json:"detail,omitempty"`
}

func (p *Problem) Error() string { return p.Code + ": " + p.Title }

// NewProblem is a convenience constructor.
func NewProblem(status int, code, title, detail string) *Problem {
	return &Problem{Status: status, Code: code, Title: title, Detail: detail}
}

type CommandHandler func(c *CommandCtx, payload json.RawMessage) (Result, error)
type QueryHandler func(c *CommandCtx, params json.RawMessage) (Result, error)
type EventHandler func(c *CommandCtx, cloudEvent json.RawMessage) error

// Pack is implemented by every capability pack; Describe must match the manifest (gate ARCH-CAP-01).
type Pack interface {
	CapabilityID() string
	Commands() map[string]CommandHandler
	Queries() map[string]QueryHandler
	Events() map[string]EventHandler
}
