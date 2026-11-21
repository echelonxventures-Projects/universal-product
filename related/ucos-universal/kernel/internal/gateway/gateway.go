// Package gateway serves the tenant REST API (master §15.2). Routes come only from the generated OpenAPI files
// (API-L1): an operation is served when it appears there and a pack registered it with the command bus.
package gateway

import (
	"context"
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"time"

	"go.yaml.in/yaml/v3"

	"ucos.io/kernel/internal/auth"
	"ucos.io/kernel/internal/bus"
	"ucos.io/kernel/sdk/pack"
)

const base = "/api/v1"

type route struct {
	method string
	re     *regexp.Regexp
	op     string
	hasID  bool
	query  bool
}

type Gateway struct {
	bus      *bus.Bus
	verifier *auth.Verifier
	routes   []route
	clock    func() time.Time
	maxBody  int64
	// Ready, when set, backs GET /api/v1/ready (readiness: dependencies reachable, schema current).
	Ready func(context.Context) error
	// Blueprint, when set, returns the tenant's active blueprint id for the context envelope ("" if none).
	Blueprint func(ctx context.Context, tenant string) string
}

// New loads routes from spec/api/openapi/capabilities/*.yaml under repoRoot, keeping registered operations only.
func New(repoRoot string, b *bus.Bus, v *auth.Verifier, clock func() time.Time) (*Gateway, error) {
	if clock == nil {
		clock = time.Now
	}
	g := &Gateway{bus: b, verifier: v, clock: clock, maxBody: 1 << 20}
	ops := b.Operations()
	files, _ := filepath.Glob(filepath.Join(repoRoot, "spec", "api", "openapi", "capabilities", "*.yaml"))
	for _, f := range files {
		raw, err := os.ReadFile(f)
		if err != nil {
			return nil, err
		}
		var doc struct {
			Paths map[string]map[string]struct {
				OperationID string `yaml:"operationId"`
			} `yaml:"paths"`
		}
		if err := yaml.Unmarshal(raw, &doc); err != nil {
			return nil, err
		}
		for path, methods := range doc.Paths {
			for method, op := range methods {
				if !ops[op.OperationID] {
					continue
				}
				pattern := "^" + regexp.QuoteMeta(base+path) + "$"
				// UGIDs contain colons (ucos:note:01J...) and commands append ":verb", so the id is matched lazily up
				// to the route's literal suffix; ids never contain "/" (master §15.2, A-77).
				pattern = strings.ReplaceAll(pattern, regexp.QuoteMeta("{id}"), `([^/]+?)`)
				g.routes = append(g.routes, route{method: strings.ToUpper(method), re: regexp.MustCompile(pattern),
					op: op.OperationID, hasID: strings.Contains(path, "{id}"), query: strings.EqualFold(method, "get")})
			}
		}
	}
	if len(g.routes) == 0 {
		return nil, errors.New("gateway: no routes (are packs registered and OpenAPI files present?)")
	}
	return g, nil
}

// Routes reports "METHOD path-pattern -> operation" for diagnostics.
func (g *Gateway) Routes() []string {
	var out []string
	for _, r := range g.routes {
		out = append(out, r.method+" "+r.re.String()+" -> "+r.op)
	}
	return out
}

func (g *Gateway) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodGet && r.URL.Path == base+"/health" {
		writeJSON(w, http.StatusOK, map[string]string{"status": "ok"})
		return
	}
	if r.Method == http.MethodGet && r.URL.Path == base+"/ready" {
		if g.Ready != nil {
			if err := g.Ready(r.Context()); err != nil {
				writeProblem(w, r, pack.NewProblem(http.StatusServiceUnavailable, "KERNEL_UNAVAILABLE", "not ready", err.Error()))
				return
			}
		}
		writeJSON(w, http.StatusOK, map[string]string{"status": "ready"})
		return
	}
	var rt *route
	var id string
	methodMismatch := false
	for i := range g.routes {
		m := g.routes[i].re.FindStringSubmatch(r.URL.Path)
		if m == nil {
			continue
		}
		if g.routes[i].method != r.Method {
			methodMismatch = true
			continue
		}
		rt = &g.routes[i]
		if rt.hasID {
			id = m[1]
		}
		break
	}
	if rt == nil {
		if methodMismatch {
			writeProblem(w, r, pack.NewProblem(http.StatusMethodNotAllowed, "METHOD_NOT_ALLOWED", "method not allowed", ""))
			return
		}
		writeProblem(w, r, pack.NewProblem(http.StatusNotFound, "OPERATION_UNKNOWN", "no such endpoint", r.URL.Path))
		return
	}
	authz := r.Header.Get("Authorization")
	if !strings.HasPrefix(authz, "Bearer ") {
		writeProblem(w, r, pack.NewProblem(http.StatusUnauthorized, "AUTH_REQUIRED", "a bearer token is required", ""))
		return
	}
	claims, tc, err := g.verifier.Verify(r.Context(), strings.TrimPrefix(authz, "Bearer "))
	if err != nil {
		writeProblem(w, r, pack.NewProblem(http.StatusUnauthorized, "AUTH_INVALID_TOKEN", "the token was rejected", err.Error()))
		return
	}
	env := auth.Envelope(claims, tc, "api", g.clock().UTC())
	if err := auth.Narrow(env, tc, r.Header); err != nil {
		writeProblem(w, r, pack.NewProblem(http.StatusBadRequest, "CTX_INVALID", "invalid request context", err.Error()))
		return
	}
	if g.Blueprint != nil {
		env.Blueprint = g.Blueprint(r.Context(), env.Tenant)
	}
	ctx, cancel := context.WithTimeout(r.Context(), 10*time.Second)
	defer cancel()
	var resp bus.Response
	if rt.query {
		params := map[string]any{}
		if s, err := strconv.Atoi(r.URL.Query().Get("page[size]")); err == nil {
			params["size"] = s
		}
		if c := r.URL.Query().Get("page[cursor]"); c != "" {
			params["cursor"] = c
		}
		payload, _ := json.Marshal(params)
		resp, err = g.bus.Query(ctx, bus.Request{OperationID: rt.op, TargetID: id, Payload: payload, Envelope: env})
	} else {
		body, rerr := io.ReadAll(io.LimitReader(r.Body, g.maxBody+1))
		if rerr != nil || int64(len(body)) > g.maxBody {
			writeProblem(w, r, pack.NewProblem(http.StatusRequestEntityTooLarge, "PAYLOAD_TOO_LARGE", "request body too large", ""))
			return
		}
		if len(body) == 0 {
			body = []byte("{}")
		}
		if !json.Valid(body) {
			writeProblem(w, r, pack.NewProblem(http.StatusBadRequest, "INVALID_JSON", "request body is not valid JSON", ""))
			return
		}
		resp, err = g.bus.Execute(ctx, bus.Request{OperationID: rt.op, TargetID: id, Payload: body,
			IdempotencyKey: r.Header.Get("Idempotency-Key"), Envelope: env})
	}
	if err != nil {
		writeProblem(w, r, pack.NewProblem(http.StatusServiceUnavailable, "KERNEL_UNAVAILABLE", "temporarily unavailable, retry with the same Idempotency-Key", ""))
		return
	}
	if resp.Problem != nil {
		writeProblem(w, r, resp.Problem)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(resp.Status)
	_, _ = w.Write(resp.Body)
}

func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(v)
}

// writeProblem writes RFC 9457 problem details; ucos.code is the registry code.
func writeProblem(w http.ResponseWriter, r *http.Request, p *pack.Problem) {
	w.Header().Set("Content-Type", "application/problem+json")
	w.WriteHeader(p.Status)
	_ = json.NewEncoder(w).Encode(map[string]any{
		"type": "https://errors.ucos.io/" + strings.ToLower(strings.ReplaceAll(p.Code, "_", "-")), "title": p.Title,
		"status": p.Status, "detail": p.Detail, "instance": r.URL.Path, "ucos": map[string]string{"code": p.Code},
	})
}
