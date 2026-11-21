// Package policy is the kernel's policy enforcement point (U03, KERNEL-DESIGN §1). Every command and query is
// authorized with Cedar against spec/policies/*.cedar (platform baseline P-001…P-007 plus universe defaults)
// before it reaches a pack. The engine is embedded (cedar-go), so there is no policy service to operate.
//
// Rules on top of Cedar's semantics:
//   - Fail closed: if any policy errors while evaluating, the request is denied (Cedar alone would skip an
//     erroring forbid, which could allow the request).
//   - Obligations (@obligation, comma-separated) on the deciding policies must be ones the kernel enforces;
//     otherwise the request is denied with POL_OBLIGATION_UNSUPPORTED rather than allowed without them.
package policy

import (
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/cedar-policy/cedar-go"

	"ucos.io/kernel/pkg/ctxenv"
)

// Supported obligations: the kernel audits every command, so full audit is always met.
var supported = map[string]bool{"audit:full": true}

type Engine struct {
	set   *cedar.PolicySet
	ids   map[cedar.PolicyID]string
	oblig map[cedar.PolicyID][]string
	Files []string
}

// Load parses every spec/policies/*.cedar file under root.
func Load(root string) (*Engine, error) {
	files, _ := filepath.Glob(filepath.Join(root, "spec", "policies", "*.cedar"))
	if len(files) == 0 {
		return nil, fmt.Errorf("policy: no policies under %s/spec/policies", root)
	}
	sort.Strings(files)
	e := &Engine{set: cedar.NewPolicySet(), ids: map[cedar.PolicyID]string{}, oblig: map[cedar.PolicyID][]string{}}
	for _, f := range files {
		b, err := os.ReadFile(f)
		if err != nil {
			return nil, err
		}
		ps, err := cedar.NewPolicySetFromBytes(filepath.Base(f), b)
		if err != nil {
			return nil, fmt.Errorf("policy: %s: %w", filepath.Base(f), err)
		}
		for id, p := range ps.All() {
			gid := cedar.PolicyID(filepath.Base(f) + "#" + string(id))
			e.set.Add(gid, p)
			ann := p.Annotations()
			e.ids[gid] = string(ann["id"])
			if e.ids[gid] == "" {
				e.ids[gid] = string(gid)
			}
			if o := strings.TrimSpace(string(ann["obligation"])); o != "" {
				for _, x := range strings.Split(o, ",") {
					e.oblig[gid] = append(e.oblig[gid], strings.TrimSpace(x))
				}
			}
		}
		e.Files = append(e.Files, filepath.Base(f))
	}
	return e, nil
}

// Request describes one operation for authorization.
type Request struct {
	Envelope   *ctxenv.Envelope
	Operation  string // e.g. sample:PublishNote
	Kind       string // command | query
	Capability string // e.g. sample.notes
	Target     string // object id, empty for creates and lists
}

// Decision is the outcome; Code is set when Allowed is false.
type Decision struct {
	Allowed bool
	Code    string   // POL_DENIED | POL_OBLIGATION_UNSUPPORTED
	Reasons []string // @id of the deciding policies
	Detail  string
}

var principalTypes = map[string]cedar.EntityType{"human": "User", "agent": "Agent", "service": "Service", "device": "Device", "anonymous": "Anonymous"}

// Authorize evaluates the request.
func (e *Engine) Authorize(r Request) Decision {
	env := r.Envelope
	ptype := principalTypes[env.Actor.Kind]
	if ptype == "" {
		ptype = "Anonymous"
	}
	principal := cedar.NewEntityUID(ptype, cedar.String(env.Actor.Identity))
	roles := make([]cedar.Value, 0, len(env.Roles))
	for _, role := range env.Roles {
		roles = append(roles, cedar.String(role))
	}
	var parents []cedar.EntityUID
	for _, role := range env.Roles {
		parents = append(parents, cedar.NewEntityUID("Role", cedar.String(role)))
	}
	group := "group:write"
	if r.Kind == "query" {
		group = "group:read"
	}
	action := cedar.NewEntityUID("Action", cedar.String(r.Operation))
	resource := cedar.NewEntityUID("Tenant", cedar.String(env.Tenant))
	if r.Target != "" {
		resource = cedar.NewEntityUID("Object", cedar.String(r.Target))
	}
	entities := cedar.EntityMap{
		principal: {UID: principal, Parents: cedar.NewEntityUIDSet(parents...), Attributes: cedar.NewRecord(cedar.RecordMap{
			"tenant": cedar.String(env.Tenant), "status": cedar.String("active"), "roles": cedar.NewSet(roles...)})},
		action: {UID: action, Parents: cedar.NewEntityUIDSet(cedar.NewEntityUID("Action", cedar.String(group)),
			cedar.NewEntityUID("Action", cedar.String("group:capability:"+r.Capability)))},
		// Row-level security already confines objects to the caller's tenant; the resource carries it for P-001.
		resource: {UID: resource, Attributes: cedar.NewRecord(cedar.RecordMap{"tenant": cedar.String(env.Tenant)})},
	}
	tm := cedar.RecordMap{"now": cedar.String(env.Time.Now.UTC().Format("2006-01-02T15:04:05Z"))}
	if env.Time.AsOf != nil {
		tm["asOf"] = cedar.String(env.Time.AsOf.UTC().Format("2006-01-02T15:04:05Z"))
	}
	ctx := cedar.NewRecord(cedar.RecordMap{
		"frame":      cedar.NewRecord(cedar.RecordMap{"reality": cedar.String(env.Frame.Reality), "sideEffectPolicy": cedar.String(env.Frame.SideEffectPolicy)}),
		"time":       cedar.NewRecord(tm),
		"simulation": cedar.Boolean(env.Simulation),
		"risk":       cedar.NewRecord(cedar.RecordMap{"band": cedar.String(env.Risk.Band)}),
		"channel":    cedar.String(env.Channel),
		"purpose":    cedar.String(env.Purpose),
	})
	dec, diag := cedar.Authorize(e.set, entities, cedar.Request{Principal: principal, Action: action, Resource: resource, Context: ctx})
	var reasons []string
	for _, rs := range diag.Reasons {
		reasons = append(reasons, e.ids[rs.PolicyID])
	}
	if len(diag.Errors) > 0 {
		var ids []string
		for _, er := range diag.Errors {
			ids = append(ids, e.ids[er.PolicyID])
		}
		return Decision{Code: "POL_DENIED", Reasons: ids, Detail: "a policy could not be evaluated for this request (fail closed): " + strings.Join(ids, ", ")}
	}
	if dec != cedar.Allow {
		detail := "no policy permits this operation"
		if len(reasons) > 0 {
			detail = "forbidden by " + strings.Join(reasons, ", ")
		}
		return Decision{Code: "POL_DENIED", Reasons: reasons, Detail: detail}
	}
	for _, rs := range diag.Reasons {
		for _, o := range e.oblig[rs.PolicyID] {
			if !supported[o] {
				return Decision{Code: "POL_OBLIGATION_UNSUPPORTED", Reasons: reasons,
					Detail: fmt.Sprintf("policy %s requires %q, which this kernel cannot enforce yet", e.ids[rs.PolicyID], o)}
			}
		}
	}
	return Decision{Allowed: true, Reasons: reasons}
}

// PEP adapts the engine to the command bus hook (bus.Bus.PEP).
func (e *Engine) PEP(env *ctxenv.Envelope, op, kind, capability, target string) (string, string) {
	d := e.Authorize(Request{Envelope: env, Operation: op, Kind: kind, Capability: capability, Target: target})
	if d.Allowed {
		return "", ""
	}
	return d.Code, d.Detail
}
