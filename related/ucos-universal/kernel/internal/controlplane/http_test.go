package controlplane

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"ucos.io/kernel/internal/trust"
)

// The operator API refuses requests without the token and self-approvals before touching the database.
func TestHandlerRefusesBeforeDatabase(t *testing.T) {
	signer, _ := trust.NewSigner(make([]byte, 32))
	h := (&Plane{Signer: signer}).Handler("operator-token-123456")
	cases := []struct {
		auth, path, body string
		status           int
		code             string
	}{
		{"", "/control/v1/snapshots", `{}`, 401, "CONTROL_UNAUTHENTICATED"},
		{"Bearer wrong", "/control/v1/snapshots", `{}`, 401, "CONTROL_UNAUTHENTICATED"},
		{"Bearer operator-token-123456", "/control/v1/nope", `{}`, 404, "OPERATION_UNKNOWN"},
		{"Bearer operator-token-123456", "/control/v1/decisions",
			`{"id":"d1","subject":"bp","decision":"approve-activation","requestedBy":"a","approvedBy":["a"]}`, 403, "CONTROL_SOD_VIOLATION"},
		{"Bearer operator-token-123456", "/control/v1/activations", `not json`, 400, "INVALID_JSON"},
	}
	for _, c := range cases {
		req := httptest.NewRequest(http.MethodPost, c.path, strings.NewReader(c.body))
		if c.auth != "" {
			req.Header.Set("Authorization", c.auth)
		}
		w := httptest.NewRecorder()
		h.ServeHTTP(w, req)
		if w.Code != c.status || !strings.Contains(w.Body.String(), c.code) {
			t.Errorf("%s %s: got %d %s, want %d %s", c.auth, c.path, w.Code, w.Body.String(), c.status, c.code)
		}
	}
}
