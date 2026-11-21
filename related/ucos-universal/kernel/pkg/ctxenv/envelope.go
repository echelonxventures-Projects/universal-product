// Package ctxenv models the ContextEnvelope (U16; spec/context/context-envelope.schema.json).
// Envelopes are built by the resolver at the gateway and can only be narrowed afterwards (CTX-L2).
package ctxenv

import (
	"errors"
	"fmt"
	"slices"
	"strings"
	"time"
)

type Actor struct {
	Identity   string `json:"identity"`
	Kind       string `json:"kind"` // human | service | agent | device | anonymous
	OnBehalfOf string `json:"onBehalfOf,omitempty"`
}

type Time struct {
	Now  time.Time  `json:"now"`
	AsOf *time.Time `json:"asOf,omitempty"`
}

type Frame struct {
	Reality          string `json:"reality"`
	SideEffectPolicy string `json:"sideEffectPolicy,omitempty"` // none | bridged | full
}

type Risk struct {
	Score *float64 `json:"score"`
	Band  string   `json:"band"` // low | medium | high | unknown
}

type Envelope struct {
	V            int                 `json:"v"`
	Tenant       string              `json:"tenant"`
	Blueprint    string              `json:"blueprint,omitempty"`
	Actor        Actor               `json:"actor"`
	Roles        []string            `json:"roles,omitempty"`
	Jurisdiction map[string][]string `json:"jurisdiction"`
	Locale       string              `json:"locale"`
	Currency     string              `json:"currency"`
	TZ           string              `json:"tz"`
	Time         Time                `json:"time"`
	Frame        Frame               `json:"frame"`
	Channel      string              `json:"channel"`
	Risk         Risk                `json:"risk"`
	Purpose      string              `json:"purpose,omitempty"`
	Simulation   bool                `json:"simulation,omitempty"`
	Exp          int64               `json:"exp"`
	Parent       string              `json:"parent,omitempty"`
}

var (
	ErrInvalid = errors.New("ctxenv: invalid envelope")
	ErrWiden   = errors.New("ctxenv: narrowing may not widen the envelope")
)

var jurisdictionRoles = []string{"actor", "buyer-delivery", "seller", "data-storage", "store", "payment-acquirer"}

// Validate checks the rules the schema states, plus expiry against now.
func (e *Envelope) Validate(now time.Time) error {
	var p []string
	if e.V != 1 {
		p = append(p, "v must be 1")
	}
	if e.Tenant == "" || e.Locale == "" || e.Currency == "" || e.TZ == "" || e.Channel == "" {
		p = append(p, "tenant, locale, currency, tz and channel are required")
	}
	if !slices.Contains([]string{"human", "service", "agent", "device", "anonymous"}, e.Actor.Kind) || e.Actor.Identity == "" {
		p = append(p, "actor identity and a valid kind are required")
	}
	for role, js := range e.Jurisdiction {
		if !slices.Contains(jurisdictionRoles, role) {
			p = append(p, "unknown jurisdiction role "+role)
		}
		for _, j := range js {
			if !strings.HasPrefix(j, "ucos:jur:") {
				p = append(p, "jurisdiction "+j+" must be a ucos:jur: id")
			}
		}
	}
	if !slices.Contains([]string{"low", "medium", "high", "unknown"}, e.Risk.Band) {
		p = append(p, "risk band must be low, medium, high or unknown (RSK-L4: unavailable means unknown)")
	}
	if e.Frame.Reality == "" {
		p = append(p, "frame reality is required")
	}
	if e.Exp <= now.Unix() {
		p = append(p, "envelope expired")
	}
	if len(p) > 0 {
		return fmt.Errorf("%w: %s", ErrInvalid, strings.Join(p, "; "))
	}
	return nil
}

// Narrow derives a child envelope for a purpose, keeping only the listed roles (CTX-L2).
// It may set a purpose only if none is set (or the same one), and may only drop roles.
func (e *Envelope) Narrow(id, purpose string, keepRoles []string) (*Envelope, error) {
	if e.Purpose != "" && purpose != e.Purpose {
		return nil, fmt.Errorf("%w: purpose %q cannot change to %q", ErrWiden, e.Purpose, purpose)
	}
	for _, r := range keepRoles {
		if !slices.Contains(e.Roles, r) {
			return nil, fmt.Errorf("%w: role %q is not held by the parent", ErrWiden, r)
		}
	}
	child := *e
	child.Purpose = purpose
	child.Roles = slices.Clone(keepRoles)
	child.Jurisdiction = make(map[string][]string, len(e.Jurisdiction))
	for k, v := range e.Jurisdiction {
		child.Jurisdiction[k] = slices.Clone(v)
	}
	child.Parent = id
	return &child, nil
}
