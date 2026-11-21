package controlplane

import (
	"crypto/subtle"
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"strings"

	"go.yaml.in/yaml/v3"

	"ucos.io/kernel/internal/composer"
)

// Handler serves the control-plane API (A-78) on a separate, operator-only listener. Every request needs
// "Authorization: Bearer <token>". Routes (POST, JSON bodies, RFC 9457 problems):
//
//	/control/v1/snapshots       {"gitCommit"}                                         -> {"id"}
//	/control/v1/blueprints      {"tenant","snapshot","pd": <PlatformDefinition YAML>} -> {"id","gaps"}
//	/control/v1/certifications  {"blueprint","profile","evidence":[…],"waivers":[…]}  -> Certification
//	/control/v1/decisions       DecisionRecord                                        -> {"id"}
//	/control/v1/activations     {"tenant","cell","blueprint","decision","certification"} -> {"previous"}
//	/control/v1/rollbacks       {"tenant"}                                            -> {}
func (p *Plane) Handler(token string) http.Handler {
	type route func(r *http.Request, body []byte) (int, any, error)
	routes := map[string]route{
		"/control/v1/snapshots": func(r *http.Request, b []byte) (int, any, error) {
			var in struct{ GitCommit string }
			if err := json.Unmarshal(b, &in); err != nil {
				return 0, nil, errBadInput
			}
			id, err := p.Snapshot(r.Context(), in.GitCommit)
			return http.StatusCreated, map[string]string{"id": id}, err
		},
		"/control/v1/blueprints": func(r *http.Request, b []byte) (int, any, error) {
			var in struct{ Tenant, Snapshot, PD string }
			var pd composer.PD
			if json.Unmarshal(b, &in) != nil || yaml.Unmarshal([]byte(in.PD), &pd) != nil || in.Tenant == "" || in.Snapshot == "" {
				return 0, nil, errBadInput
			}
			res, err := p.Compose(r.Context(), in.Tenant, in.Snapshot, &pd)
			if err != nil {
				return 0, nil, err
			}
			return http.StatusCreated, map[string]any{"id": res.ID, "gaps": res.Gaps}, nil
		},
		"/control/v1/certifications": func(r *http.Request, b []byte) (int, any, error) {
			var in struct {
				Blueprint, Profile string
				Evidence           []Evidence
				Waivers            []Waiver
			}
			if json.Unmarshal(b, &in) != nil || in.Blueprint == "" {
				return 0, nil, errBadInput
			}
			if in.Profile == "" {
				in.Profile = "blueprint"
			}
			c, err := p.Certify(r.Context(), in.Blueprint, in.Profile, in.Evidence, in.Waivers)
			return http.StatusCreated, c, err
		},
		"/control/v1/decisions": func(r *http.Request, b []byte) (int, any, error) {
			var d DecisionRecord
			if json.Unmarshal(b, &d) != nil || d.ID == "" || d.Subject == "" || len(d.ApprovedBy) == 0 {
				return 0, nil, errBadInput
			}
			for _, a := range d.ApprovedBy {
				if a == d.RequestedBy {
					return 0, nil, errSelfApproval
				}
			}
			return http.StatusCreated, map[string]string{"id": d.ID}, p.Decide(r.Context(), d)
		},
		"/control/v1/activations": func(r *http.Request, b []byte) (int, any, error) {
			var in struct{ Tenant, Cell, Blueprint, Decision, Certification string }
			if json.Unmarshal(b, &in) != nil || in.Tenant == "" || in.Blueprint == "" {
				return 0, nil, errBadInput
			}
			prev, err := p.Activate(r.Context(), in.Tenant, in.Cell, in.Blueprint, in.Decision, in.Certification, p.Signer.Public())
			return http.StatusOK, map[string]string{"previous": prev}, err
		},
		"/control/v1/rollbacks": func(r *http.Request, b []byte) (int, any, error) {
			var in struct{ Tenant string }
			if json.Unmarshal(b, &in) != nil || in.Tenant == "" {
				return 0, nil, errBadInput
			}
			return http.StatusOK, map[string]string{}, p.Rollback(r.Context(), in.Tenant)
		},
	}
	want := []byte("Bearer " + token)
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if token == "" || subtle.ConstantTimeCompare([]byte(r.Header.Get("Authorization")), want) != 1 {
			problem(w, http.StatusUnauthorized, "CONTROL_UNAUTHENTICATED", "operator token required")
			return
		}
		h, ok := routes[r.URL.Path]
		if !ok {
			problem(w, http.StatusNotFound, "OPERATION_UNKNOWN", "unknown control-plane route "+r.URL.Path)
			return
		}
		if r.Method != http.MethodPost {
			problem(w, http.StatusMethodNotAllowed, "METHOD_NOT_ALLOWED", "use POST")
			return
		}
		body, err := io.ReadAll(io.LimitReader(r.Body, 1<<20))
		if err != nil {
			problem(w, http.StatusBadRequest, "INVALID_JSON", err.Error())
			return
		}
		status, out, err := h(r, body)
		switch {
		case errors.Is(err, errBadInput):
			problem(w, http.StatusBadRequest, "INVALID_JSON", "missing or malformed fields")
		case errors.Is(err, errSelfApproval):
			problem(w, http.StatusForbidden, "CONTROL_SOD_VIOLATION", "the requester cannot approve their own request")
		case errors.Is(err, ErrNotCertified):
			problem(w, http.StatusUnprocessableEntity, "CONTROL_CERT_GATE_FAILED", err.Error())
		case errors.Is(err, ErrNoApproval):
			problem(w, http.StatusUnprocessableEntity, "CONTROL_APPROVAL_MISSING", err.Error())
		case err != nil:
			problem(w, http.StatusUnprocessableEntity, "CONTROL_PRECONDITION_NOT_MET", strings.TrimPrefix(err.Error(), "controlplane: "))
		default:
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(status)
			_ = json.NewEncoder(w).Encode(out)
		}
	})
}

var (
	errBadInput     = errors.New("bad input")
	errSelfApproval = errors.New("self approval")
)

func problem(w http.ResponseWriter, status int, code, detail string) {
	w.Header().Set("Content-Type", "application/problem+json")
	w.WriteHeader(status)
	// Same RFC 9457 shape as the gateway (ucos.code is the registry code).
	_ = json.NewEncoder(w).Encode(map[string]any{"type": "https://errors.ucos.io/" + strings.ToLower(strings.ReplaceAll(code, "_", "-")),
		"title": code, "status": status, "detail": detail, "ucos": map[string]string{"code": code}})
}
