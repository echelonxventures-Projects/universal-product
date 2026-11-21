package auth

import (
	"net/http"
	"testing"
	"time"
)

func TestActorKindFromClaims(t *testing.T) {
	tc := TenantConfig{Tenant: "ucos:tenant:t1", Locale: "en", Currency: "INR", TZ: "Asia/Kolkata", Reality: "simulated"}
	now := time.Now()
	if e := Envelope(&Claims{Sub: "u1"}, tc, "api", now); e.Actor.Kind != "human" || e.Actor.Identity != "ucos:identity:u1" {
		t.Fatalf("user token: %+v", e.Actor)
	}
	if e := Envelope(&Claims{Sub: "x", Azp: "billing", PreferredUsername: "service-account-billing"}, tc, "api", now); e.Actor.Kind != "service" || e.Actor.Identity != "ucos:service:billing" {
		t.Fatalf("service account: %+v", e.Actor)
	}
	c := &Claims{Sub: "u1"}
	c.Act = &struct {
		Sub string `json:"sub"`
	}{Sub: "enrich-bot"}
	if e := Envelope(c, tc, "api", now); e.Actor.Kind != "agent" || e.Actor.OnBehalfOf != "ucos:identity:u1" || e.Actor.Identity != "ucos:agent:enrich-bot" {
		t.Fatalf("delegated token: %+v", e.Actor)
	}
}

func TestNarrow(t *testing.T) {
	tc := TenantConfig{Tenant: "ucos:tenant:t1", Locale: "en-IN", Locales: []string{"hi-IN", "ar-AE"}, Currency: "INR", TZ: "Asia/Kolkata"}
	cases := []struct{ accept, want string }{
		{"hi-IN,en;q=0.5", "hi-IN"},
		{"fr-FR, ar;q=0.8, en;q=0.9", "en-IN"}, // en (q 0.9) beats ar (q 0.8); fr is not enabled
		{"de-DE", "en-IN"},                     // nothing enabled matches: keep the tenant default
		{"ar-SA;q=0.7", "ar-AE"},               // primary-language match
	}
	for _, c := range cases {
		e := Envelope(&Claims{Sub: "u"}, tc, "api", time.Now())
		h := http.Header{}
		h.Set("Accept-Language", c.accept)
		if err := Narrow(e, tc, h); err != nil || e.Locale != c.want {
			t.Errorf("Accept-Language %q: got %q (%v), want %q", c.accept, e.Locale, err, c.want)
		}
	}
	e := Envelope(&Claims{Sub: "u"}, tc, "api", time.Now())
	h := http.Header{}
	h.Set("UCOS-Purpose", "customer-support")
	if err := Narrow(e, tc, h); err != nil || e.Purpose != "customer-support" {
		t.Fatalf("purpose: %q %v", e.Purpose, err)
	}
	h.Set("UCOS-Purpose", "Bad Purpose!")
	if err := Narrow(e, tc, h); err == nil {
		t.Fatal("malformed purpose must be refused")
	}
}
