package metrics

import (
	"net/http/httptest"
	"strings"
	"testing"
)

func TestExposition(t *testing.T) {
	c := NewCounter("test_requests_total", "Requests.", "code")
	c.Inc("200")
	c.Add(2, "200")
	c.Inc("500")
	h := NewHistogram("test_duration_seconds", "Durations.", []float64{0.1, 1}, "op")
	h.Observe(0.05, "a")
	h.Observe(0.5, "a")
	w := httptest.NewRecorder()
	Handler().ServeHTTP(w, httptest.NewRequest("GET", "/metrics", nil))
	body := w.Body.String()
	for _, want := range []string{
		"# TYPE test_requests_total counter",
		`test_requests_total{code="200"} 3`,
		`test_requests_total{code="500"} 1`,
		`test_duration_seconds_bucket{op="a",le="0.1"} 1`,
		`test_duration_seconds_bucket{op="a",le="1"} 2`,
		`test_duration_seconds_bucket{op="a",le="+Inf"} 2`,
		`test_duration_seconds_sum{op="a"} 0.55`,
		`test_duration_seconds_count{op="a"} 2`,
	} {
		if !strings.Contains(body, want) {
			t.Errorf("missing %q in\n%s", want, body)
		}
	}
}
