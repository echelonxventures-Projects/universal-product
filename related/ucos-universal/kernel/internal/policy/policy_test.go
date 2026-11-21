package policy

import (
	"strings"
	"testing"
	"time"

	"ucos.io/kernel/pkg/ctxenv"
)

func env(kind string) *ctxenv.Envelope {
	now := time.Date(2027, 1, 10, 9, 0, 0, 0, time.UTC)
	return &ctxenv.Envelope{V: 1, Tenant: "ucos:tenant:t1", Actor: ctxenv.Actor{Identity: "ucos:identity:asha", Kind: kind},
		Time: ctxenv.Time{Now: now}, Frame: ctxenv.Frame{Reality: "simulated", SideEffectPolicy: "none"}, Risk: ctxenv.Risk{Band: "low"}, Channel: "api"}
}

// The kernel evaluates the real policy files: the sample permit plus the platform baseline.
func TestEnforcementPoint(t *testing.T) {
	e, err := Load("../../..")
	if err != nil {
		t.Fatal(err)
	}
	ok := func(d Decision) bool { return d.Allowed }
	if d := e.Authorize(Request{Envelope: env("human"), Operation: "sample:CreateNote", Kind: "command", Capability: "sample.notes"}); !ok(d) {
		t.Fatalf("member create: %+v", d)
	}
	if d := e.Authorize(Request{Envelope: env("human"), Operation: "sample:GetNote", Kind: "query", Capability: "sample.notes", Target: "ucos:note:1"}); !ok(d) {
		t.Fatalf("member read: %+v", d)
	}
	if d := e.Authorize(Request{Envelope: env("human"), Operation: "other:DoThing", Kind: "command", Capability: "other.thing"}); ok(d) || d.Code != "POL_DENIED" {
		t.Fatalf("capability without a permit must be denied: %+v", d)
	}
	past := time.Date(2027, 1, 1, 0, 0, 0, 0, time.UTC)
	tt := env("human")
	tt.Time.AsOf = &past
	if d := e.Authorize(Request{Envelope: tt, Operation: "sample:CreateNote", Kind: "command", Capability: "sample.notes"}); ok(d) || !strings.Contains(d.Detail, "P-005") {
		t.Fatalf("time-travel write must be forbidden by P-005: %+v", d)
	}
	// An agent has no delegated authority in the envelope yet: P-003 cannot be evaluated, so the request fails closed.
	if d := e.Authorize(Request{Envelope: env("agent"), Operation: "sample:CreateNote", Kind: "command", Capability: "sample.notes"}); ok(d) {
		t.Fatalf("agent without authority must be denied: %+v", d)
	}
}
