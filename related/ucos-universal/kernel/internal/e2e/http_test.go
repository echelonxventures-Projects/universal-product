package e2e

import (
	"context"
	"crypto"
	"crypto/rand"
	"crypto/rsa"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"math/big"
	"net/http"
	"net/http/httptest"
	"os"
	"strings"
	"testing"
	"time"

	"ucos.io/kernel/internal/auth"
	"ucos.io/kernel/internal/bus"
	"ucos.io/kernel/internal/gateway"
	"ucos.io/kernel/internal/store"
	"ucos.io/kernel/packs/sample"
)

type issuer struct {
	key *rsa.PrivateKey
	srv *httptest.Server
}

func newIssuer(t *testing.T) *issuer {
	k, _ := rsa.GenerateKey(rand.Reader, 2048)
	i := &issuer{key: k}
	i.srv = httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		e := base64.RawURLEncoding
		_ = json.NewEncoder(w).Encode(map[string]any{"keys": []map[string]string{{"kty": "RSA", "kid": "k1", "use": "sig",
			"n": e.EncodeToString(k.N.Bytes()), "e": e.EncodeToString(big.NewInt(int64(k.E)).Bytes())}}})
	}))
	t.Cleanup(i.srv.Close)
	return i
}

func (i *issuer) token(iss, sub string, roles []string) string {
	e := base64.RawURLEncoding
	h, _ := json.Marshal(map[string]string{"alg": "RS256", "kid": "k1"})
	p, _ := json.Marshal(map[string]any{"iss": iss, "sub": sub, "exp": time.Now().Add(10 * time.Minute).Unix(), "realm_access": map[string]any{"roles": roles}})
	in := e.EncodeToString(h) + "." + e.EncodeToString(p)
	d := sha256.Sum256([]byte(in))
	s, _ := rsa.SignPKCS1v15(rand.Reader, i.key, crypto.SHA256, d[:])
	return in + "." + e.EncodeToString(s)
}

// The Phase 0 flow through HTTP: generated routes, tokens, envelopes, problems.
func TestGatewayHTTP(t *testing.T) {
	dsn := os.Getenv("UCOS_TEST_DATABASE_URL")
	if dsn == "" {
		t.Skip("UCOS_TEST_DATABASE_URL not set")
	}
	ctx := context.Background()
	db, err := store.Open(ctx, dsn)
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close()
	idp := newIssuer(t)
	stamp := time.Now().UnixNano()
	tA := auth.TenantConfig{Issuer: "https://idp.test/realms/a", JWKSURL: idp.srv.URL, Tenant: fmt.Sprintf("ucos:tenant:http-a-%d", stamp), Locale: "en", Currency: "INR", TZ: "Asia/Kolkata", Reality: "simulated"}
	tB := auth.TenantConfig{Issuer: "https://idp.test/realms/b", JWKSURL: idp.srv.URL, Tenant: fmt.Sprintf("ucos:tenant:http-b-%d", stamp), Locale: "en", Currency: "INR", TZ: "Asia/Kolkata", Reality: "simulated"}
	b := bus.New(db, "sandbox-1", nil)
	b.Register(sample.Pack{})
	b.PEP = pep(t)
	gw, err := gateway.New("../../..", b, auth.NewVerifier([]auth.TenantConfig{tA, tB}, nil, nil), nil)
	if err != nil {
		t.Fatal(err)
	}
	srv := httptest.NewServer(gw)
	defer srv.Close()
	asha := idp.token(tA.Issuer, "asha", []string{"sample-editor"})
	bob := idp.token(tB.Issuer, "bob", []string{"sample-editor"})

	call := func(method, path, tok, key, body string) (int, map[string]any) {
		t.Helper()
		req, _ := http.NewRequest(method, srv.URL+"/api/v1"+path, strings.NewReader(body))
		if tok != "" {
			req.Header.Set("Authorization", "Bearer "+tok)
		}
		if key != "" {
			req.Header.Set("Idempotency-Key", key)
		}
		res, err := http.DefaultClient.Do(req)
		if err != nil {
			t.Fatal(err)
		}
		defer res.Body.Close()
		raw, _ := io.ReadAll(res.Body)
		var out map[string]any
		_ = json.Unmarshal(raw, &out)
		return res.StatusCode, out
	}

	if s, _ := call("GET", "/health", "", "", ""); s != 200 {
		t.Fatalf("health %d", s)
	}
	if s, p := call("POST", "/sample/notes", "", "k-http-0001", `{"title":{"en":"x"}}`); s != 401 || p["ucos"].(map[string]any)["code"] != "AUTH_REQUIRED" {
		t.Fatalf("no token: %d %v", s, p)
	}
	if s, p := call("POST", "/sample/notes", asha, "", `{"title":{"en":"x"}}`); s != 400 || p["ucos"].(map[string]any)["code"] != "IDEMPOTENCY_KEY_REQUIRED" {
		t.Fatalf("no key: %d %v", s, p)
	}
	s, created := call("POST", "/sample/notes", asha, "k-http-create-1", `{"title":{"en":"Kernel works over HTTP"}}`)
	if s != 201 {
		t.Fatalf("create: %d %v", s, created)
	}
	id := created["id"].(string)
	if s2, again := call("POST", "/sample/notes", asha, "k-http-create-1", `{"title":{"en":"Kernel works over HTTP"}}`); s2 != 201 || again["id"] != id {
		t.Fatalf("replay: %d %v", s2, again)
	}
	if s, p := call("POST", "/sample/notes/"+id+":publish", bob, "k-http-pub-b", `{}`); s != 404 {
		t.Fatalf("other tenant's token must not reach the note: %d %v", s, p)
	}
	if s, p := call("POST", "/sample/notes/"+id+":remind", asha, "k-http-remind", `{}`); s != 403 {
		t.Fatalf("users must not fire reminders: %d %v", s, p)
	}
	if s, p := call("POST", "/sample/notes/"+id+":publish", asha, "k-http-pub-a", `{}`); s != 200 || p["status"] != "published" {
		t.Fatalf("publish: %d %v", s, p)
	}
	if s, p := call("GET", "/sample/notes/"+id, asha, "", ""); s != 200 || p["status"] != "published" || p["version"].(float64) != 2 {
		t.Fatalf("get: %d %v", s, p)
	}
	if s, p := call("GET", "/sample/notes?page[size]=10", asha, "", ""); s != 200 || len(p["items"].([]any)) != 1 {
		t.Fatalf("list: %d %v", s, p)
	}
	if s, p := call("GET", "/sample/notes?page[size]=10", bob, "", ""); s != 200 || len(p["items"].([]any)) != 0 {
		t.Fatalf("other tenant's list must be empty: %d %v", s, p)
	}
	if s, _ := call("DELETE", "/sample/notes/"+id, asha, "", ""); s != 405 && s != 404 {
		t.Fatalf("unknown method: %d", s)
	}
}
