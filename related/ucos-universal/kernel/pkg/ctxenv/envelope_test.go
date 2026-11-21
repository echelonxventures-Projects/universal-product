package ctxenv

import (
	"errors"
	"testing"
	"time"
)

func sample(now time.Time) *Envelope {
	return &Envelope{
		V: 1, Tenant: "ucos:tenant:bazaar", Actor: Actor{Identity: "ucos:identity:asha", Kind: "human"},
		Roles: []string{"buyer", "sample-editor"}, Jurisdiction: map[string][]string{"buyer-delivery": {"ucos:jur:IN-KA"}},
		Locale: "hi-IN", Currency: "INR", TZ: "Asia/Kolkata", Time: Time{Now: now},
		Frame: Frame{Reality: "physical", SideEffectPolicy: "full"}, Channel: "web", Risk: Risk{Band: "unknown"},
		Exp: now.Add(5 * time.Minute).Unix(),
	}
}

func TestValidate(t *testing.T) {
	now := time.Date(2027, 1, 10, 9, 0, 0, 0, time.UTC)
	e := sample(now)
	if err := e.Validate(now); err != nil {
		t.Fatal(err)
	}
	e.Risk.Band = ""
	if err := e.Validate(now); !errors.Is(err, ErrInvalid) {
		t.Fatal("empty risk band must be rejected (unknown is the explicit value)")
	}
	e = sample(now)
	if err := e.Validate(now.Add(10 * time.Minute)); err == nil {
		t.Fatal("expired envelope accepted")
	}
	e = sample(now)
	e.Jurisdiction["moon"] = []string{"IN"}
	if err := e.Validate(now); err == nil {
		t.Fatal("unknown jurisdiction role and non-UGID jurisdiction accepted")
	}
}

func TestNarrowOnlyNarrows(t *testing.T) {
	e := sample(time.Now())
	c, err := e.Narrow("ctx-1", "customer-support", []string{"buyer"})
	if err != nil {
		t.Fatal(err)
	}
	if c.Parent != "ctx-1" || len(c.Roles) != 1 || c.Purpose != "customer-support" {
		t.Fatalf("unexpected child %+v", c)
	}
	c.Jurisdiction["buyer-delivery"][0] = "changed"
	if e.Jurisdiction["buyer-delivery"][0] != "ucos:jur:IN-KA" {
		t.Fatal("child shares state with parent")
	}
	if _, err := c.Narrow("ctx-2", "marketing", nil); !errors.Is(err, ErrWiden) {
		t.Fatal("purpose change accepted")
	}
	if _, err := e.Narrow("ctx-3", "x", []string{"admin"}); !errors.Is(err, ErrWiden) {
		t.Fatal("role widening accepted")
	}
}
