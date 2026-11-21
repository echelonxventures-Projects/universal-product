package policy

import (
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"testing"

	"github.com/cedar-policy/cedar-go"
	"go.yaml.in/yaml/v3"
)

var entRef = regexp.MustCompile(`^([A-Za-z_][A-Za-z0-9_:]*)::"([^"]*)"$`)

func uid(s string) (cedar.EntityUID, bool) {
	m := entRef.FindStringSubmatch(s)
	if m == nil {
		return cedar.EntityUID{}, false
	}
	return cedar.NewEntityUID(cedar.EntityType(m[1]), cedar.String(m[2])), true
}

func value(v any) cedar.Value {
	switch x := v.(type) {
	case string:
		if u, ok := uid(x); ok {
			return u
		}
		return cedar.String(x)
	case bool:
		return cedar.Boolean(x)
	case int:
		return cedar.Long(x)
	case []any:
		vs := make([]cedar.Value, len(x))
		for i, e := range x {
			vs[i] = value(e)
		}
		return cedar.NewSet(vs...)
	case map[string]any:
		return record(x)
	}
	panic("unsupported value")
}

func record(m map[string]any) cedar.Record {
	r := cedar.RecordMap{}
	for k, v := range m {
		r[cedar.String(k)] = value(v)
	}
	return cedar.NewRecord(r)
}

// Every policy suite in spec/policies/tests (run by CI with the Rust engine through cedarpy) gives the same
// answers with cedar-go, the engine the kernel embeds.
func TestPolicySuitesMatchReferenceEngine(t *testing.T) {
	suites, _ := filepath.Glob("../../../spec/policies/tests/*.yaml")
	if len(suites) == 0 {
		t.Fatal("no policy suites")
	}
	for _, f := range suites {
		var s struct {
			Policies []string
			Fixtures string
			Entities []struct {
				UID     string
				Attrs   map[string]any
				Parents []string
			}
			DefaultContext map[string]any `yaml:"defaultContext"`
			Cases          []struct {
				Name, Principal, Action, Resource, Expect string
				Context                                   map[string]any
			}
		}
		b, _ := os.ReadFile(f)
		if err := yaml.Unmarshal(b, &s); err != nil {
			t.Fatal(err)
		}
		var src strings.Builder
		for _, p := range s.Policies {
			pb, err := os.ReadFile(filepath.Join("../../..", p))
			if err != nil {
				t.Fatal(err)
			}
			src.Write(pb)
			src.WriteString("\n")
		}
		src.WriteString(s.Fixtures)
		ps, err := cedar.NewPolicySetFromBytes(filepath.Base(f), []byte(src.String()))
		if err != nil {
			t.Fatalf("%s: %v", f, err)
		}
		ents := cedar.EntityMap{}
		for _, e := range s.Entities {
			u, _ := uid(e.UID)
			var parents []cedar.EntityUID
			for _, p := range e.Parents {
				pu, _ := uid(p)
				parents = append(parents, pu)
			}
			ents[u] = cedar.Entity{UID: u, Parents: cedar.NewEntityUIDSet(parents...), Attributes: record(e.Attrs)}
		}
		for _, c := range s.Cases {
			ctx := map[string]any{}
			for k, v := range s.DefaultContext {
				ctx[k] = v
			}
			for k, v := range c.Context {
				ctx[k] = v
			}
			p, _ := uid(c.Principal)
			a, _ := uid(c.Action)
			r, _ := uid(c.Resource)
			dec, _ := cedar.Authorize(ps, ents, cedar.Request{Principal: p, Action: a, Resource: r, Context: record(ctx)})
			got := "Deny"
			if dec == cedar.Allow {
				got = "Allow"
			}
			if got != c.Expect {
				t.Errorf("%s: %q: cedar-go says %s, suite expects %s", filepath.Base(f), c.Name, got, c.Expect)
			}
		}
	}
}
