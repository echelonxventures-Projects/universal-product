// Package metrics exposes counters and histograms in the Prometheus text format (version 0.0.4), which every
// common monitoring stack and the OpenTelemetry Collector scrape. No client library: the kernel stays
// dependency-light and backend-agnostic (ADR-037).
package metrics

import (
	"fmt"
	"io"
	"math"
	"net/http"
	"sort"
	"strings"
	"sync"
	"time"
)

type metric interface{ write(io.Writer) }

var (
	mu       sync.Mutex
	registry = map[string]metric{}
)

func register(name string, m metric) {
	mu.Lock()
	defer mu.Unlock()
	if _, dup := registry[name]; dup {
		panic("metrics: duplicate " + name)
	}
	registry[name] = m
}

// Counter is a monotonically increasing value per label set.
type Counter struct {
	name, help string
	labels     []string
	mu         sync.Mutex
	vals       map[string]float64
}

func NewCounter(name, help string, labels ...string) *Counter {
	c := &Counter{name: name, help: help, labels: labels, vals: map[string]float64{}}
	register(name, c)
	return c
}

func (c *Counter) Inc(labelValues ...string) { c.Add(1, labelValues...) }

func (c *Counter) Add(v float64, labelValues ...string) {
	k := key(c.labels, labelValues)
	c.mu.Lock()
	c.vals[k] += v
	c.mu.Unlock()
}

func (c *Counter) write(w io.Writer) {
	c.mu.Lock()
	defer c.mu.Unlock()
	fmt.Fprintf(w, "# HELP %s %s\n# TYPE %s counter\n", c.name, c.help, c.name)
	for _, k := range sorted(c.vals) {
		fmt.Fprintf(w, "%s%s %s\n", c.name, k, num(c.vals[k]))
	}
}

// Histogram counts observations into cumulative buckets (seconds for durations).
type Histogram struct {
	name, help string
	labels     []string
	buckets    []float64
	mu         sync.Mutex
	series     map[string]*hseries
}

type hseries struct {
	counts []uint64
	sum    float64
	n      uint64
}

// DurationBuckets suit request latencies from 1 ms to 10 s.
var DurationBuckets = []float64{.001, .0025, .005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5, 10}

func NewHistogram(name, help string, buckets []float64, labels ...string) *Histogram {
	h := &Histogram{name: name, help: help, labels: labels, buckets: buckets, series: map[string]*hseries{}}
	register(name, h)
	return h
}

func (h *Histogram) Observe(v float64, labelValues ...string) {
	k := key(h.labels, labelValues)
	h.mu.Lock()
	defer h.mu.Unlock()
	s := h.series[k]
	if s == nil {
		s = &hseries{counts: make([]uint64, len(h.buckets))}
		h.series[k] = s
	}
	for i, b := range h.buckets {
		if v <= b {
			s.counts[i]++
		}
	}
	s.sum += v
	s.n++
}

// Since observes the seconds elapsed since start.
func (h *Histogram) Since(start time.Time, labelValues ...string) {
	h.Observe(time.Since(start).Seconds(), labelValues...)
}

func (h *Histogram) write(w io.Writer) {
	h.mu.Lock()
	defer h.mu.Unlock()
	fmt.Fprintf(w, "# HELP %s %s\n# TYPE %s histogram\n", h.name, h.help, h.name)
	keys := make([]string, 0, len(h.series))
	for k := range h.series {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	for _, k := range keys {
		s := h.series[k]
		inner := strings.TrimSuffix(strings.TrimPrefix(k, "{"), "}")
		sep := ""
		if inner != "" {
			sep = ","
		}
		for i, b := range h.buckets {
			fmt.Fprintf(w, "%s_bucket{%s%sle=\"%s\"} %d\n", h.name, inner, sep, num(b), s.counts[i])
		}
		fmt.Fprintf(w, "%s_bucket{%s%sle=\"+Inf\"} %d\n", h.name, inner, sep, s.n)
		fmt.Fprintf(w, "%s_sum%s %s\n%s_count%s %d\n", h.name, k, num(s.sum), h.name, k, s.n)
	}
}

// Handler serves every registered metric.
func Handler() http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
		mu.Lock()
		names := make([]string, 0, len(registry))
		for n := range registry {
			names = append(names, n)
		}
		ms := make([]metric, len(names))
		sort.Strings(names)
		for i, n := range names {
			ms[i] = registry[n]
		}
		mu.Unlock()
		for _, m := range ms {
			m.write(w)
		}
	})
}

func key(names, values []string) string {
	if len(names) == 0 {
		return ""
	}
	var b strings.Builder
	b.WriteByte('{')
	for i, n := range names {
		v := ""
		if i < len(values) {
			v = values[i]
		}
		if i > 0 {
			b.WriteByte(',')
		}
		fmt.Fprintf(&b, "%s=%q", n, v)
	}
	b.WriteByte('}')
	return b.String()
}

func sorted(m map[string]float64) []string {
	out := make([]string, 0, len(m))
	for k := range m {
		out = append(out, k)
	}
	sort.Strings(out)
	return out
}

func num(f float64) string {
	if f == math.Trunc(f) && math.Abs(f) < 1e15 {
		return fmt.Sprintf("%d", int64(f))
	}
	return fmt.Sprintf("%g", f)
}
