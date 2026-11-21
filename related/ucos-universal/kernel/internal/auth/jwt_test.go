package auth

import (
	"context"
	"crypto"
	"crypto/rand"
	"crypto/rsa"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"errors"
	"math/big"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

// TestIssuer is a tiny OIDC issuer for tests: it signs RS256 tokens and serves its JWKS.
type TestIssuer struct {
	Key    *rsa.PrivateKey
	Server *httptest.Server
	Kid    string
}

func NewTestIssuer(t testing.TB) *TestIssuer {
	k, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		t.Fatal(err)
	}
	ti := &TestIssuer{Key: k, Kid: "test-key-1"}
	ti.Server = httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		enc := base64.RawURLEncoding
		_ = json.NewEncoder(w).Encode(map[string]any{"keys": []map[string]string{{
			"kty": "RSA", "kid": ti.Kid, "use": "sig", "alg": "RS256",
			"n": enc.EncodeToString(k.N.Bytes()), "e": enc.EncodeToString(big.NewInt(int64(k.E)).Bytes())}}})
	}))
	t.Cleanup(ti.Server.Close)
	return ti
}

func (ti *TestIssuer) Sign(t testing.TB, alg string, claims map[string]any) string {
	enc := base64.RawURLEncoding
	h, _ := json.Marshal(map[string]string{"alg": alg, "kid": ti.Kid, "typ": "JWT"})
	p, _ := json.Marshal(claims)
	in := enc.EncodeToString(h) + "." + enc.EncodeToString(p)
	d := sha256.Sum256([]byte(in))
	sig, err := rsa.SignPKCS1v15(rand.Reader, ti.Key, crypto.SHA256, d[:])
	if err != nil {
		t.Fatal(err)
	}
	return in + "." + enc.EncodeToString(sig)
}

func TestVerify(t *testing.T) {
	ti := NewTestIssuer(t)
	now := time.Date(2027, 1, 10, 9, 0, 0, 0, time.UTC)
	tc := TenantConfig{Issuer: "https://idp.test/realms/sample", JWKSURL: ti.Server.URL, Tenant: "ucos:tenant:sample", Locale: "en", Currency: "INR", TZ: "Asia/Kolkata"}
	v := NewVerifier([]TenantConfig{tc}, nil, func() time.Time { return now })
	good := map[string]any{"iss": tc.Issuer, "sub": "asha", "exp": now.Add(5 * time.Minute).Unix(), "realm_access": map[string]any{"roles": []string{"sample-editor"}}}
	c, got, err := v.Verify(context.Background(), ti.Sign(t, "RS256", good))
	if err != nil || got.Tenant != "ucos:tenant:sample" || c.Sub != "asha" {
		t.Fatalf("valid token rejected: %v", err)
	}
	if e := Envelope(c, got, "api", now); e.Validate(now) != nil || e.Actor.Identity != "ucos:identity:asha" || e.Roles[0] != "sample-editor" {
		t.Fatalf("envelope: %+v", e)
	}

	// alg=none and other algorithms are refused.
	enc := base64.RawURLEncoding
	h, _ := json.Marshal(map[string]string{"alg": "none"})
	p, _ := json.Marshal(good)
	if _, _, err := v.Verify(context.Background(), enc.EncodeToString(h)+"."+enc.EncodeToString(p)+"."); !errors.Is(err, ErrToken) {
		t.Fatal("alg=none accepted")
	}
	// Tampered payload fails the signature.
	tok := ti.Sign(t, "RS256", good)
	evil := map[string]any{"iss": tc.Issuer, "sub": "admin", "exp": good["exp"]}
	ep, _ := json.Marshal(evil)
	parts := splitDots(tok)
	if _, _, err := v.Verify(context.Background(), parts[0]+"."+enc.EncodeToString(ep)+"."+parts[2]); !errors.Is(err, ErrToken) {
		t.Fatal("tampered token accepted")
	}
	// Untrusted issuer.
	other := map[string]any{"iss": "https://idp.test/realms/other", "sub": "x", "exp": good["exp"]}
	if _, _, err := v.Verify(context.Background(), ti.Sign(t, "RS256", other)); !errors.Is(err, ErrIssuer) {
		t.Fatal("untrusted issuer accepted")
	}
	// Expired.
	old := map[string]any{"iss": tc.Issuer, "sub": "asha", "exp": now.Add(-time.Hour).Unix()}
	if _, _, err := v.Verify(context.Background(), ti.Sign(t, "RS256", old)); !errors.Is(err, ErrToken) {
		t.Fatal("expired token accepted")
	}
}

func splitDots(s string) []string {
	var out []string
	start := 0
	for i := 0; i < len(s); i++ {
		if s[i] == '.' {
			out = append(out, s[start:i])
			start = i + 1
		}
	}
	return append(out, s[start:])
}
