package e2e

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"go.yaml.in/yaml/v3"

	"ucos.io/kernel/internal/bus"
	"ucos.io/kernel/internal/composer"
	"ucos.io/kernel/internal/controlplane"
	"ucos.io/kernel/internal/store"
	"ucos.io/kernel/internal/trust"
	"ucos.io/kernel/packs/sample"
)

// Phase 0 exit (master §32.1): the sample pack is composed, certified and activated, and only then can the
// tenant run it. Uncertified or unapproved blueprints cannot be activated; rollback takes the capability away.
func TestComposeCertifyActivate(t *testing.T) {
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

	signer, _ := trust.NewSigner(make([]byte, 32))
	cp, err := controlplane.New(db, "../../..", signer)
	if err != nil {
		t.Fatal(err)
	}
	now := time.Now().UTC().Truncate(time.Second)
	cp.Clock = func() time.Time { return now }

	b := bus.New(db, "sandbox-1", func() time.Time { return now })
	b.Register(sample.Pack{})
	b.PEP = pep(t)
	act := &controlplane.Active{DB: db} // TTL 0: no caching, so the test sees each change
	b.Active = act.Check

	tenant := fmt.Sprintf("ucos:tenant:act-%d", now.UnixNano())
	asha := envelope(tenant, "ucos:identity:asha", []string{"sample-editor"}, now)
	create := func(key string) bus.Response {
		t.Helper()
		r, err := b.Execute(ctx, bus.Request{OperationID: "sample:CreateNote", Payload: json.RawMessage(`{"title":{"en":"gated"}}`),
			IdempotencyKey: key, Envelope: asha})
		if err != nil {
			t.Fatal(err)
		}
		return r
	}
	if r := create("key-before-activation"); r.Status != 403 || r.Problem.Code != "ACTIVATION_DENIED" {
		t.Fatalf("before activation the capability must be refused: %+v", r)
	}

	snap, err := cp.Snapshot(ctx, strings.Repeat("0", 40))
	if err != nil {
		t.Fatal(err)
	}
	var pd composer.PD
	raw, _ := os.ReadFile(filepath.Join("../../..", "spec", "composition", "golden", "sample-p0.pd.yaml"))
	if err := yaml.Unmarshal(raw, &pd); err != nil {
		t.Fatal(err)
	}
	res, err := cp.Compose(ctx, tenant, snap, &pd)
	if err != nil {
		t.Fatal(err)
	}

	// Without evidence the certification fails, and a failed certification cannot be activated.
	failed, err := cp.Certify(ctx, res.ID, "blueprint", nil, nil)
	if err != nil {
		t.Fatal(err)
	}
	if failed.Passed {
		t.Fatal("certification without evidence must fail")
	}
	for _, r := range failed.Results {
		if (r.Gate == "GAP-000" || r.Gate == "TEST-COMP-01" || r.Gate == "ARCH-CAP-02") && r.Result != "pass" {
			t.Fatalf("computed gate %s should pass: %+v", r.Gate, r)
		}
	}
	decision := controlplane.DecisionRecord{ID: "ucos:decision:" + tenant, Authority: "ucos:authority:release",
		Subject: res.ID, Decision: "approve-activation", RequestedBy: "ucos:identity:asha", ApprovedBy: []string{"ucos:identity:ravi"},
		Rationale: "Phase 0 exit test"}
	if err := cp.Decide(ctx, decision); err != nil {
		t.Fatal(err)
	}
	if _, err := cp.Activate(ctx, tenant, "sandbox-1", res.ID, decision.ID, failed.ID, signer.Public()); !errors.Is(err, controlplane.ErrNotCertified) {
		t.Fatalf("activating a failed certification: %v", err)
	}

	// The requester cannot approve their own activation (separation of duties).
	self := decision
	self.ID += ":self"
	self.ApprovedBy = []string{"ucos:identity:asha"}
	if err := cp.Decide(ctx, self); err == nil {
		t.Fatal("self-approval must be refused")
	}

	var evidence []controlplane.Evidence
	for _, r := range failed.Results {
		if r.Result == "fail" {
			evidence = append(evidence, controlplane.Evidence{Gate: r.Gate, Ref: "ci://run/42#" + r.Gate, CollectedAt: now.Add(-time.Hour)})
		}
	}
	cert, err := cp.Certify(ctx, res.ID, "blueprint", evidence, nil)
	if err != nil {
		t.Fatal(err)
	}
	if !cert.Passed {
		t.Fatalf("certification with evidence should pass: %+v", cert.Results)
	}

	// The attestation is a standard DSSE in-toto statement about this blueprint.
	payload, err := trust.Verify(cert.Attestation, signer.Public())
	if err != nil || !strings.Contains(string(payload), res.ID) {
		t.Fatalf("attestation does not verify: %v", err)
	}
	other, _ := trust.NewSigner(append(make([]byte, 31), 1))
	if _, err := cp.Activate(ctx, tenant, "sandbox-1", res.ID, decision.ID, cert.ID, other.Public()); !errors.Is(err, controlplane.ErrNotCertified) {
		t.Fatalf("an attestation from an untrusted key must be refused: %v", err)
	}
	if _, err := cp.Activate(ctx, tenant, "sandbox-1", res.ID, "ucos:decision:none", cert.ID, signer.Public()); !errors.Is(err, controlplane.ErrNoApproval) {
		t.Fatalf("activation without a decision record: %v", err)
	}
	if _, err := cp.Activate(ctx, tenant, "sandbox-1", res.ID, decision.ID, cert.ID, signer.Public()); err != nil {
		t.Fatal(err)
	}
	if r := create("key-after-activation"); r.Status != 201 {
		t.Fatalf("after activation the command must run: %+v", r)
	}

	var status, phase string
	_ = db.Pool.QueryRow(ctx, `SELECT status FROM registry.blueprints WHERE id = $1`, res.ID).Scan(&status)
	_ = db.Pool.QueryRow(ctx, `SELECT phase FROM registry.activations WHERE tenant = $1 ORDER BY id DESC LIMIT 1`, tenant).Scan(&phase)
	if status != "active" || phase != "COMPLETE" {
		t.Fatalf("blueprint %s, activation %s", status, phase)
	}

	// Rollback to "nothing active" takes the capability away again.
	if err := cp.Rollback(ctx, tenant); err != nil {
		t.Fatal(err)
	}
	if r := create("key-after-rollback"); r.Status != 403 {
		t.Fatalf("after rollback the capability must be refused: %+v", r)
	}
}
