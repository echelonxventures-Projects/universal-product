// End-to-end test of the Phase 0 exit flow (spec/acceptance/p0-exit/*.feature) against a real, migrated
// PostgreSQL. Run through `tools/db_test.sh --exec go test ./...` (tools/ci.sh does this); skipped otherwise.
package e2e

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"strings"
	"sync"
	"testing"
	"time"

	"ucos.io/kernel/internal/audit"
	"ucos.io/kernel/internal/bus"
	"ucos.io/kernel/internal/policy"
	"ucos.io/kernel/internal/relay"
	"ucos.io/kernel/internal/store"
	"ucos.io/kernel/internal/triggers"
	"ucos.io/kernel/packs/sample"
	"ucos.io/kernel/pkg/ctxenv"
)

type memPub struct {
	mu   sync.Mutex
	msgs []string
}

func (m *memPub) Publish(_ context.Context, topic, key string, value []byte) error {
	var ev struct {
		Type string `json:"type"`
	}
	_ = json.Unmarshal(value, &ev)
	m.mu.Lock()
	m.msgs = append(m.msgs, topic+"|"+ev.Type+"|"+key)
	m.mu.Unlock()
	return nil
}

// pep loads the real policy files, so every end-to-end test runs with policy enforcement as in production.
func pep(t *testing.T) func(*ctxenv.Envelope, string, string, string, string) (string, string) {
	t.Helper()
	e, err := policy.Load("../../..")
	if err != nil {
		t.Fatal(err)
	}
	return e.PEP
}

func envelope(tenant, actor string, roles []string, now time.Time) *ctxenv.Envelope {
	return &ctxenv.Envelope{
		V: 1, Tenant: tenant, Actor: ctxenv.Actor{Identity: actor, Kind: "human"}, Roles: roles,
		Jurisdiction: map[string][]string{"actor": {"ucos:jur:IN"}}, Locale: "en-IN", Currency: "INR", TZ: "Asia/Kolkata",
		Time: ctxenv.Time{Now: now}, Frame: ctxenv.Frame{Reality: "simulated", SideEffectPolicy: "none"}, Channel: "api",
		Risk: ctxenv.Risk{Band: "unknown"}, Exp: now.Add(time.Hour).Unix(),
	}
}

func TestPhase0ExitFlow(t *testing.T) {
	dsn := os.Getenv("UCOS_TEST_DATABASE_URL")
	if dsn == "" {
		t.Skip("UCOS_TEST_DATABASE_URL not set (run through tools/db_test.sh --exec)")
	}
	ctx := context.Background()
	db, err := store.Open(ctx, dsn)
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()

	now := time.Now().UTC().Truncate(time.Second)
	clock := func() time.Time { return now }
	b := bus.New(db, "sandbox-1", clock)
	b.Register(sample.Pack{})
	b.PEP = pep(t)
	tenant := fmt.Sprintf("ucos:tenant:it-%d", now.UnixNano())
	other := tenant + "-other"
	asha := envelope(tenant, "ucos:identity:asha", []string{"sample-editor"}, now)

	exec := func(env *ctxenv.Envelope, op, target, key string, payload string) bus.Response {
		t.Helper()
		r, err := b.Execute(ctx, bus.Request{OperationID: op, TargetID: target, Payload: json.RawMessage(payload), IdempotencyKey: key, Envelope: env})
		if err != nil {
			t.Fatalf("%s: infrastructure error: %v", op, err)
		}
		return r
	}

	// Create, then replay with the same key: identical answer, one object, one event.
	r1 := exec(asha, "sample:CreateNote", "", "key-create-0001", `{"title":{"en":"Kernel works"}}`)
	if r1.Status != 201 {
		t.Fatalf("create: %+v", r1)
	}
	var created struct{ ID string }
	_ = json.Unmarshal(r1.Body, &created)
	r2 := exec(asha, "sample:CreateNote", "", "key-create-0001", `{"title":{"en":"Kernel works"}}`)
	if string(r2.Body) != string(r1.Body) || r2.Status != r1.Status {
		t.Fatalf("replay differs: %s vs %s", r2.Body, r1.Body)
	}
	r3 := exec(asha, "sample:CreateNote", "", "key-create-0001", `{"title":{"en":"Different"}}`)
	if r3.Status != 409 || r3.Problem.Code != "IDEMPOTENCY_KEY_REUSED" {
		t.Fatalf("reused key with different body: %+v", r3)
	}

	// Policy enforcement: a write "as of" a past time outside simulation is refused by P-005 before any pack runs.
	past := now.Add(-24 * time.Hour)
	tt := envelope(tenant, "ucos:identity:asha", []string{"sample-editor"}, now)
	tt.Time.AsOf = &past
	if r := exec(tt, "sample:CreateNote", "", "key-time-travel", `{"title":{"en":"x"}}`); r.Status != 403 || r.Problem.Code != "POL_DENIED" ||
		!strings.Contains(r.Problem.Detail, "P-005") {
		t.Fatalf("time-travel write must be refused by policy: %+v", r)
	}

	// Tenant isolation: another tenant cannot see or change the note.
	intruder := envelope(other, "ucos:identity:mallory", []string{"sample-editor"}, now)
	if r := exec(intruder, "sample:PublishNote", created.ID, "key-intrude-01", `{}`); r.Status != 404 {
		t.Fatalf("cross-tenant publish must look like not-found, got %+v", r)
	}

	// Lifecycle with role check; a failed rule leaves no partial state.
	viewer := envelope(tenant, "ucos:identity:ravi", nil, now)
	if r := exec(viewer, "sample:PublishNote", created.ID, "key-publish-noRole", `{}`); r.Status != 403 {
		t.Fatalf("publish without role: %+v", r)
	}
	if r := exec(asha, "sample:PublishNote", created.ID, "key-publish-0001", `{}`); r.Status != 200 || !strings.Contains(string(r.Body), `"version":2`) {
		t.Fatalf("publish: %+v %s", r, r.Body)
	}
	if r := exec(asha, "sample:EditNote", created.ID, "key-edit-after-pub", `{"body":"x"}`); r.Status != 422 || r.Problem.Code != "SAMPLE_INVALID_STATE" {
		t.Fatalf("edit after publish: %+v", r)
	}

	// Reminder through the trigger engine.
	at := now.Add(30 * time.Minute).Format(time.RFC3339)
	if r := exec(asha, "sample:ScheduleNoteReminder", created.ID, "key-remind-0001", fmt.Sprintf(`{"at":%q}`, at)); r.Status != 200 {
		t.Fatalf("schedule: %+v", r)
	}
	eng := &triggers.Engine{DB: db, Bus: b}
	if n, err := eng.FireDue(ctx, now.Add(10*time.Minute)); err != nil || n != 0 {
		t.Fatalf("nothing is due yet: n=%d err=%v", n, err)
	}
	if n, err := eng.FireDue(ctx, now.Add(31*time.Minute)); err != nil || n != 1 {
		t.Fatalf("reminder should fire once: n=%d err=%v", n, err)
	}
	if n, _ := eng.FireDue(ctx, now.Add(32*time.Minute)); n != 0 {
		t.Fatal("a fired one-off trigger must not fire again")
	}

	// Relay: every event is published exactly once per drain cycle.
	pub := &memPub{}
	rl := &relay.Relay{DB: db, Pub: pub}
	if _, err := rl.Drain(ctx, 1000); err != nil {
		t.Fatal(err)
	}
	mine := 0
	for _, m := range pub.msgs {
		if strings.HasSuffix(m, "|"+created.ID) {
			mine++
		}
	}
	if mine != 3 { // created, published, reminded
		t.Fatalf("expected 3 events for the note, got %d: %v", mine, pub.msgs)
	}
	if n, _ := rl.Drain(ctx, 1000); n != 0 {
		t.Fatalf("second drain republished %d events", n)
	}

	// Audit: every command (including rejected ones) is sealed into a verifiable chain; tampering is detected.
	ap := &audit.Appender{DB: db}
	if _, err := ap.Seal(ctx, 1000); err != nil {
		t.Fatal(err)
	}
	day := time.Date(now.Year(), now.Month(), now.Day(), 0, 0, 0, 0, time.UTC)
	if broken, err := ap.Verify(ctx, tenant, day); err != nil || broken != 0 {
		t.Fatalf("chain should verify: broken=%d err=%v", broken, err)
	}
	var count int
	if err := db.Pool.QueryRow(ctx, `SELECT count(*) FROM kernel.audit_records WHERE tenant_id = $1`, tenant).Scan(&count); err != nil {
		t.Fatal(err)
	}
	// create, publish without role (rejected), publish, edit after publish (rejected), schedule, remind.
	// Replays return the stored answer and run nothing, so they add no record.
	if count != 6 {
		t.Fatalf("expected 6 audit records, got %d", count)
	}
	if _, err := db.Pool.Exec(ctx, `UPDATE kernel.audit_records SET rec = '{"tampered":true}' WHERE tenant_id = $1 AND seq = 2`, tenant); err != nil {
		t.Fatal(err)
	}
	if broken, _ := ap.Verify(ctx, tenant, day); broken != 2 {
		t.Fatalf("tampering at seq 2 must be detected, got %d", broken)
	}
}

// Two identical requests racing on the same key apply once and return the same answer.
func TestConcurrentDuplicateAppliesOnce(t *testing.T) {
	dsn := os.Getenv("UCOS_TEST_DATABASE_URL")
	if dsn == "" {
		t.Skip("UCOS_TEST_DATABASE_URL not set")
	}
	ctx := context.Background()
	db, err := store.Open(ctx, dsn)
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()
	now := time.Now().UTC()
	b := bus.New(db, "sandbox-1", func() time.Time { return now })
	b.Register(sample.Pack{})
	b.PEP = pep(t)
	tenant := fmt.Sprintf("ucos:tenant:race-%d", now.UnixNano())
	env := envelope(tenant, "ucos:identity:asha", nil, now)
	var wg sync.WaitGroup
	bodies := make([]string, 8)
	for i := range bodies {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			r, err := b.Execute(ctx, bus.Request{OperationID: "sample:CreateNote", Payload: json.RawMessage(`{"title":{"en":"race"}}`),
				IdempotencyKey: "key-race-000001", Envelope: env})
			if err != nil {
				t.Error(err)
				return
			}
			bodies[i] = string(r.Body)
		}(i)
	}
	wg.Wait()
	for _, x := range bodies[1:] {
		if x != bodies[0] {
			t.Fatalf("racing duplicates got different answers: %q vs %q", x, bodies[0])
		}
	}
	var n int
	_ = db.Pool.QueryRow(ctx, `SELECT count(*) FROM kernel.outbox WHERE tenant_id = $1`, tenant).Scan(&n)
	if n != 1 {
		t.Fatalf("expected exactly one event, got %d", n)
	}
}
