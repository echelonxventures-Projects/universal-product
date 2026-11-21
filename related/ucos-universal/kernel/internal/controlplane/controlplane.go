// Package controlplane implements compose -> certify -> activate (U58, U74, U73, U01; KERNEL-DESIGN §8–§11):
// signed registry snapshots, blueprint records, certification runs with DSSE attestations, decision records and
// activations. Activation is what makes a tenant's capabilities runnable: the command bus checks it (Active).
package controlplane

import (
	"context"
	"crypto/ed25519"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"sync"
	"time"

	"github.com/jackc/pgx/v5"
	"go.yaml.in/yaml/v3"

	"ucos.io/kernel/internal/composer"
	"ucos.io/kernel/internal/store"
	"ucos.io/kernel/internal/trust"
)

const roleControl = "ucos_control"

type Plane struct {
	DB       *store.DB
	Registry *composer.Registry
	Signer   *trust.Signer
	Root     string // repository root (spec/)
	Gates    []Gate
	Profiles map[string][]string
	Clock    func() time.Time
}

type Gate struct {
	ID        string   `yaml:"id"`
	Method    string   `yaml:"method"`
	AppliesTo []string `yaml:"appliesTo"`
	Blocking  bool     `yaml:"blocking"`
}

// New loads the registry (rules, manifests, facts) and the gate catalogue from root.
func New(db *store.DB, root string, signer *trust.Signer) (*Plane, error) {
	reg, err := composer.LoadRegistry(root)
	if err != nil {
		return nil, err
	}
	raw, err := os.ReadFile(filepath.Join(root, "spec", "certification", "gates.yaml"))
	if err != nil {
		return nil, err
	}
	var cat struct {
		Gates    []Gate              `yaml:"gates"`
		Profiles map[string][]string `yaml:"profiles"`
	}
	if err := yaml.Unmarshal(raw, &cat); err != nil {
		return nil, err
	}
	return &Plane{DB: db, Registry: reg, Signer: signer, Root: root, Gates: cat.Gates, Profiles: cat.Profiles, Clock: time.Now}, nil
}

// ---------------------------------------------------------------- snapshots

var snapshotDirs = []string{"spec/capabilities/packs", "spec/rules", "spec/policies", "spec/decisions", "spec/certification"}

// Snapshot digests every file composition and certification read, signs the manifest and records it.
func (p *Plane) Snapshot(ctx context.Context, gitCommit string) (string, error) {
	type entry struct {
		Path   string `json:"path"`
		SHA256 string `json:"sha256"`
	}
	var files []entry
	for _, d := range snapshotDirs {
		err := filepath.WalkDir(filepath.Join(p.Root, d), func(path string, de os.DirEntry, err error) error {
			if err != nil || de.IsDir() {
				return err
			}
			b, err := os.ReadFile(path)
			if err != nil {
				return err
			}
			rel, _ := filepath.Rel(p.Root, path)
			sum := sha256.Sum256(b)
			files = append(files, entry{filepath.ToSlash(rel), hex.EncodeToString(sum[:])})
			return nil
		})
		if err != nil {
			return "", err
		}
	}
	sort.Slice(files, func(i, j int) bool { return files[i].Path < files[j].Path })
	manifest, _ := json.Marshal(files)
	sum := sha256.Sum256(manifest)
	id := "sha256:" + hex.EncodeToString(sum[:])
	env := p.Signer.Sign("application/vnd.ucos.snapshot+json", manifest)
	sig, _ := json.Marshal(env)
	err := p.DB.AsRole(ctx, roleControl, func(tx pgx.Tx) error {
		_, err := tx.Exec(ctx, `INSERT INTO registry.snapshots (id, merkle_root, signature, git_commit) VALUES ($1, $2, $3, $4)
			ON CONFLICT (id) DO NOTHING`, id, id, string(sig), gitCommit)
		return err
	})
	return id, err
}

// ---------------------------------------------------------------- compose

// Compose composes pd twice (determinism, L18), records the blueprint for tenant against snapshotID and returns it.
func (p *Plane) Compose(ctx context.Context, tenant, snapshotID string, pd *composer.PD) (*composer.Result, error) {
	a, err := p.Registry.Compose(pd)
	if err != nil {
		return nil, err
	}
	b, err := p.Registry.Compose(pd)
	if err != nil {
		return nil, err
	}
	report := map[string]any{"gaps": a.Gaps, "deterministic": a.ID == b.ID}
	body, _ := json.Marshal(a.Blueprint)
	rep, _ := json.Marshal(report)
	err = p.DB.AsRole(ctx, roleControl, func(tx pgx.Tx) error {
		_, err := tx.Exec(ctx, `INSERT INTO registry.blueprints (id, tenant, pd_ref, snapshot_id, body, gap_report, status)
			VALUES ($1, $2, $3, $4, $5::jsonb, $6::jsonb, 'composed') ON CONFLICT (id) DO NOTHING`,
			a.ID, tenant, pd.Metadata.ID+"@"+pd.Metadata.Version, snapshotID, string(body), string(rep))
		return err
	})
	return a, err
}

// ---------------------------------------------------------------- certify

// Evidence supports a gate that the runner cannot compute itself (test runs, restore tests, audits).
type Evidence struct {
	Gate        string    `json:"gate"`
	Ref         string    `json:"ref"`
	CollectedAt time.Time `json:"collectedAt"`
}

// Waiver accepts a failing or unevidenced gate for a reason, approved by someone (U02).
type Waiver struct {
	Gate       string `json:"gate"`
	Reason     string `json:"reason"`
	ApprovedBy string `json:"approvedBy"`
}

type GateResult struct {
	Gate   string `json:"gate"`
	Result string `json:"result"` // pass | fail | waived
	Detail string `json:"detail"`
}

type Certification struct {
	ID          string         `json:"id"`
	Subject     string         `json:"subject"`
	Profile     string         `json:"profile"`
	Passed      bool           `json:"passed"`
	Results     []GateResult   `json:"results"`
	Attestation trust.Envelope `json:"attestation"`
	ValidUntil  time.Time      `json:"validUntil"`
}

func (p *Plane) expand(profile string) ([]string, error) {
	items, ok := p.Profiles[profile]
	if !ok {
		return nil, fmt.Errorf("controlplane: unknown certification profile %q", profile)
	}
	seen := map[string]bool{}
	var out []string
	for _, it := range items {
		if fam, ok := strings.CutSuffix(it, "-*"); ok {
			for _, g := range p.Gates {
				if strings.HasPrefix(g.ID, fam+"-") && contains(g.AppliesTo, "blueprint") && !seen[g.ID] {
					seen[g.ID] = true
					out = append(out, g.ID)
				}
			}
			continue
		}
		if !seen[it] {
			seen[it] = true
			out = append(out, it)
		}
	}
	sort.Strings(out)
	return out, nil
}

// Certify evaluates a profile for a recorded blueprint and records a signed attestation.
func (p *Plane) Certify(ctx context.Context, blueprintID, profile string, evidence []Evidence, waivers []Waiver) (*Certification, error) {
	now := p.Clock().UTC()
	gates, err := p.expand(profile)
	if err != nil {
		return nil, err
	}
	var snapshot string
	var rep struct {
		Gaps          []composer.Gap `json:"gaps"`
		Deterministic bool           `json:"deterministic"`
	}
	var repRaw []byte
	err = p.DB.AsRole(ctx, roleControl, func(tx pgx.Tx) error {
		return tx.QueryRow(ctx, `SELECT snapshot_id, gap_report FROM registry.blueprints WHERE id = $1`, blueprintID).Scan(&snapshot, &repRaw)
	})
	if err != nil {
		return nil, fmt.Errorf("controlplane: blueprint %s: %w", blueprintID, err)
	}
	_ = json.Unmarshal(repRaw, &rep)
	gapKinds := map[string]int{}
	mandatory := 0
	for _, g := range rep.Gaps {
		gapKinds[g.Kind]++
		if g.Severity == "MANDATORY" {
			mandatory++
		}
	}
	ev := map[string]Evidence{}
	for _, e := range evidence {
		ev[e.Gate] = e
	}
	wv := map[string]Waiver{}
	for _, w := range waivers {
		wv[w.Gate] = w
	}
	var results []GateResult
	passed := true
	for _, g := range gates {
		r := GateResult{Gate: g}
		switch g {
		case "GAP-000":
			r.Result, r.Detail = verdict(mandatory == 0, fmt.Sprintf("%d mandatory gaps", mandatory))
		case "TEST-COMP-01":
			r.Result, r.Detail = verdict(rep.Deterministic, "composed twice against the same snapshot")
		case "ARCH-CAP-02":
			n := gapKinds["MISSING_CAPABILITY"] + gapKinds["PHASE_NOT_AVAILABLE"] + gapKinds["CONFLICT_EXCLUDED"]
			r.Result, r.Detail = verdict(n == 0, fmt.Sprintf("%d capability gaps", n))
		case "CMP-MAP-01":
			n := gapKinds["CONTROL_NOT_IMPLEMENTED"]
			r.Result, r.Detail = verdict(n == 0, fmt.Sprintf("%d controls not implemented", n))
		default:
			if e, ok := ev[g]; ok && e.Ref != "" && now.Sub(e.CollectedAt) <= 30*24*time.Hour && !e.CollectedAt.After(now.Add(time.Minute)) {
				r.Result, r.Detail = "pass", "evidence "+e.Ref
			} else {
				r.Result, r.Detail = "fail", "no evidence collected in the last 30 days"
			}
		}
		if r.Result == "fail" {
			if w, ok := wv[g]; ok && w.Reason != "" && w.ApprovedBy != "" {
				r.Result, r.Detail = "waived", w.Reason+" (approved by "+w.ApprovedBy+")"
			} else {
				passed = false
			}
		}
		results = append(results, r)
	}
	validUntil := now.Add(90 * 24 * time.Hour)
	pred, _ := json.Marshal(map[string]any{"profile": profile, "snapshot": snapshot, "results": results,
		"passed": passed, "certifiedAt": now.Format(time.RFC3339), "validUntil": validUntil.Format(time.RFC3339)})
	digest := strings.TrimPrefix(blueprintID, "ucos:blueprint:sha256:")
	stmt, _ := json.Marshal(trust.Statement{Type: "https://in-toto.io/Statement/v1",
		Subject:       []trust.Subject{{Name: blueprintID, Digest: map[string]string{"sha256": digest}}},
		PredicateType: "https://ucos.io/certification/v1", Predicate: pred})
	env := p.Signer.Sign(trust.InTotoType, stmt)
	sum := sha256.Sum256(stmt)
	c := &Certification{ID: "ucos:cert:" + hex.EncodeToString(sum[:16]), Subject: blueprintID, Profile: profile,
		Passed: passed, Results: results, Attestation: env, ValidUntil: validUntil}
	resJSON, _ := json.Marshal(results)
	envJSON, _ := json.Marshal(env)
	err = p.DB.AsRole(ctx, roleControl, func(tx pgx.Tx) error {
		if _, err := tx.Exec(ctx, `INSERT INTO registry.certifications (id, subject, snapshot_id, profile, results, passed, attestation, valid_until)
			VALUES ($1, $2, $3, $4, $5::jsonb, $6, $7::jsonb, $8)`, c.ID, blueprintID, snapshot, profile, string(resJSON), passed, string(envJSON), validUntil); err != nil {
			return err
		}
		status := "composed"
		if passed {
			status = "certified"
		}
		_, err := tx.Exec(ctx, `UPDATE registry.blueprints SET status = $2, certification = $3 WHERE id = $1 AND status = 'composed'`, blueprintID, status, c.ID)
		return err
	})
	return c, err
}

func verdict(ok bool, detail string) (string, string) {
	if ok {
		return "pass", detail
	}
	return "fail", detail
}

func contains(xs []string, x string) bool {
	for _, v := range xs {
		if v == x {
			return true
		}
	}
	return false
}

// ---------------------------------------------------------------- decide and activate

type DecisionRecord struct {
	ID          string   `json:"id"`
	Authority   string   `json:"authority"`
	Subject     string   `json:"subject"`
	Decision    string   `json:"decision"`
	RequestedBy string   `json:"requestedBy"`
	ApprovedBy  []string `json:"approvedBy"`
	Rationale   string   `json:"rationale"`
}

// Decide records a decision (U01). The database refuses records where the requester approves their own request.
func (p *Plane) Decide(ctx context.Context, d DecisionRecord) error {
	return p.DB.AsRole(ctx, roleControl, func(tx pgx.Tx) error {
		_, err := tx.Exec(ctx, `INSERT INTO registry.decision_records (id, authority, subject, decision, requested_by, approved_by, rationale)
			VALUES ($1, $2, $3, $4, $5, $6, $7)`, d.ID, d.Authority, d.Subject, d.Decision, d.RequestedBy, d.ApprovedBy, d.Rationale)
		return err
	})
}

var (
	ErrNotCertified = errors.New("controlplane: blueprint is not certified (or the attestation does not verify)")
	ErrNoApproval   = errors.New("controlplane: no approving decision record for this blueprint (ARCH-AUTH-01)")
)

// Activate makes blueprintID the tenant's active blueprint. It verifies the certification's signature and subject,
// its validity, and the approving decision, then records the activation phases. Returns the previous blueprint.
func (p *Plane) Activate(ctx context.Context, tenant, cell, blueprintID, decisionID, certID string, trusted ed25519.PublicKey) (string, error) {
	now := p.Clock().UTC()
	var previous string
	err := p.DB.AsRole(ctx, roleControl, func(tx pgx.Tx) error {
		var subject string
		var passed bool
		var validUntil time.Time
		var envRaw []byte
		if err := tx.QueryRow(ctx, `SELECT subject, passed, valid_until, attestation FROM registry.certifications WHERE id = $1`, certID).
			Scan(&subject, &passed, &validUntil, &envRaw); err != nil {
			return ErrNotCertified
		}
		var env trust.Envelope
		_ = json.Unmarshal(envRaw, &env)
		payload, err := trust.Verify(env, trusted)
		if err != nil || !passed || subject != blueprintID || now.After(validUntil) {
			return ErrNotCertified
		}
		var stmt trust.Statement
		if json.Unmarshal(payload, &stmt) != nil || len(stmt.Subject) != 1 || stmt.Subject[0].Name != blueprintID ||
			stmt.Subject[0].Digest["sha256"] != strings.TrimPrefix(blueprintID, "ucos:blueprint:sha256:") {
			return ErrNotCertified
		}
		var decision, dSubject string
		if err := tx.QueryRow(ctx, `SELECT decision, subject FROM registry.decision_records WHERE id = $1`, decisionID).Scan(&decision, &dSubject); err != nil ||
			decision != "approve-activation" || dSubject != blueprintID {
			return ErrNoApproval
		}
		var bpTenant string
		if err := tx.QueryRow(ctx, `SELECT tenant FROM registry.blueprints WHERE id = $1`, blueprintID).Scan(&bpTenant); err != nil || bpTenant != tenant {
			return fmt.Errorf("controlplane: blueprint %s was not composed for %s", blueprintID, tenant)
		}
		slug := tenant[strings.LastIndex(tenant, ":")+1:]
		if _, err := tx.Exec(ctx, `INSERT INTO registry.tenants (id, slug, cell, status) VALUES ($1, $2, $3, 'active')
			ON CONFLICT (id) DO NOTHING`, tenant, slug, cell); err != nil {
			return err
		}
		var prev *string
		if err := tx.QueryRow(ctx, `SELECT active_blueprint FROM registry.tenants WHERE id = $1 FOR UPDATE`, tenant).Scan(&prev); err != nil {
			return err
		}
		if prev != nil {
			previous = *prev
		}
		var actID int64
		if err := tx.QueryRow(ctx, `INSERT INTO registry.activations (tenant, blueprint, decision_record, certification, previous, phase)
			VALUES ($1, $2, $3, $4, $5, 'DEPLOYING') RETURNING id`, tenant, blueprintID, decisionID, certID, prev).Scan(&actID); err != nil {
			return err
		}
		// Phase 0: packs run in-process, so deploying and expand migrations are no-ops; routing is the flip below.
		if _, err := tx.Exec(ctx, `UPDATE registry.tenants SET active_blueprint = $2, status = 'active' WHERE id = $1`, tenant, blueprintID); err != nil {
			return err
		}
		if _, err := tx.Exec(ctx, `UPDATE registry.blueprints SET status = 'active' WHERE id = $1`, blueprintID); err != nil {
			return err
		}
		if prev != nil && *prev != blueprintID {
			if _, err := tx.Exec(ctx, `UPDATE registry.blueprints SET status = 'superseded' WHERE id = $1`, *prev); err != nil {
				return err
			}
		}
		_, err = tx.Exec(ctx, `UPDATE registry.activations SET phase = 'COMPLETE', updated_at = now() WHERE id = $1`, actID)
		return err
	})
	return previous, err
}

// Rollback re-activates the tenant's previous blueprint (U73: routing flips back first).
func (p *Plane) Rollback(ctx context.Context, tenant string) error {
	return p.DB.AsRole(ctx, roleControl, func(tx pgx.Tx) error {
		var actID int64
		var bp string
		var prev *string
		err := tx.QueryRow(ctx, `SELECT id, blueprint, previous FROM registry.activations WHERE tenant = $1 AND phase = 'COMPLETE'
			ORDER BY id DESC LIMIT 1 FOR UPDATE`, tenant).Scan(&actID, &bp, &prev)
		if err != nil {
			return fmt.Errorf("controlplane: nothing to roll back for %s", tenant)
		}
		if _, err := tx.Exec(ctx, `UPDATE registry.tenants SET active_blueprint = $2 WHERE id = $1`, tenant, prev); err != nil {
			return err
		}
		if _, err := tx.Exec(ctx, `UPDATE registry.blueprints SET status = 'rolled-back' WHERE id = $1`, bp); err != nil {
			return err
		}
		if prev != nil {
			if _, err := tx.Exec(ctx, `UPDATE registry.blueprints SET status = 'active' WHERE id = $1`, *prev); err != nil {
				return err
			}
		}
		_, err = tx.Exec(ctx, `UPDATE registry.activations SET phase = 'ROLLED_BACK', updated_at = now() WHERE id = $1`, actID)
		return err
	})
}

// ---------------------------------------------------------------- the bus's activation check

// Active reports whether capability is part of tenant's active blueprint. Results are cached for ttl.
type Active struct {
	DB  *store.DB
	TTL time.Duration
	mu  sync.Mutex
	c   map[string]cached
	bp  map[string]cachedID
}

type cached struct {
	ok bool
	at time.Time
}

func (a *Active) Check(ctx context.Context, tenant, capability string) (bool, error) {
	k := tenant + "\x00" + capability
	a.mu.Lock()
	if a.c == nil {
		a.c = map[string]cached{}
	}
	if v, ok := a.c[k]; ok && time.Since(v.at) < a.TTL {
		a.mu.Unlock()
		return v.ok, nil
	}
	a.mu.Unlock()
	var ok bool
	err := a.DB.AsRole(ctx, store.RoleApp, func(tx pgx.Tx) error {
		return tx.QueryRow(ctx, `SELECT EXISTS (SELECT 1 FROM registry.tenants t JOIN registry.blueprints b ON b.id = t.active_blueprint
			WHERE t.id = $1 AND t.status = 'active' AND b.body->'capabilities' @> jsonb_build_array(jsonb_build_object('id', $2::text)))`,
			tenant, capability).Scan(&ok)
	})
	if err != nil {
		return false, err
	}
	a.mu.Lock()
	a.c[k] = cached{ok, time.Now()}
	a.mu.Unlock()
	return ok, nil
}

// Blueprint returns the tenant's active blueprint id ("" when none), cached for TTL like Check.
func (a *Active) Blueprint(ctx context.Context, tenant string) string {
	k := tenant + "\x00#blueprint"
	a.mu.Lock()
	if a.bp == nil {
		a.bp = map[string]cachedID{}
	}
	if v, ok := a.bp[k]; ok && time.Since(v.at) < a.TTL {
		a.mu.Unlock()
		return v.id
	}
	a.mu.Unlock()
	var id *string
	_ = a.DB.AsRole(ctx, store.RoleApp, func(tx pgx.Tx) error {
		return tx.QueryRow(ctx, `SELECT active_blueprint FROM registry.tenants WHERE id = $1 AND status = 'active'`, tenant).Scan(&id)
	})
	out := ""
	if id != nil {
		out = *id
	}
	a.mu.Lock()
	a.bp[k] = cachedID{out, time.Now()}
	a.mu.Unlock()
	return out
}

type cachedID struct {
	id string
	at time.Time
}
