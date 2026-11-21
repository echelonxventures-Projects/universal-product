// Command ucos-kernel runs the Phase 0 kernel in one process: the REST gateway, the command bus with registered
// packs, and the background workers (outbox relay, audit appender, trigger engine).
//
// "ucos-kernel migrate" applies db/migrations (UCOS_MIGRATIONS_DIR, default $UCOS_REPO_ROOT/db/migrations) and exits.
//
// Configuration (environment):
//
//	UCOS_DATABASE_URL   PostgreSQL DSN (migrations in db/migrations already applied)
//	UCOS_REPO_ROOT      repository root, for the generated OpenAPI routes (default ".")
//	UCOS_CELL           cell id used in event topics (default "dev-1")
//	UCOS_HTTP_ADDR      listen address (default ":8080")
//	UCOS_TENANTS        JSON array of auth.TenantConfig (issuer, jwksUrl, tenant, locale, currency, tz, reality)
//	UCOS_KAFKA_BROKERS  comma-separated brokers; empty means events are logged instead of published
//	UCOS_SIGNING_SEED   hex Ed25519 seed (32 bytes) for snapshots and attestations; enables the control plane
//	UCOS_ADMIN_ADDR     control-plane listen address (default "127.0.0.1:8081"); operator-only
//	UCOS_ADMIN_TOKEN    bearer token for the control plane (required with UCOS_SIGNING_SEED)
//	UCOS_METRICS_ADDR   Prometheus-format metrics listener (default ":9090"; empty disables)
//	UCOS_ENFORCE_POLICY "true": every operation is authorized with spec/policies/*.cedar (default "true")
//	UCOS_ENFORCE_ACTIVATION  "true": tenants may run only capabilities in their active blueprint (default "true")
package main

import (
	"context"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"path/filepath"
	"strings"
	"syscall"
	"time"

	_ "time/tzdata"

	"ucos.io/kernel/internal/audit"
	"ucos.io/kernel/internal/auth"
	"ucos.io/kernel/internal/bus"
	"ucos.io/kernel/internal/controlplane"
	"ucos.io/kernel/internal/gateway"
	"ucos.io/kernel/internal/metrics"
	"ucos.io/kernel/internal/migrate"
	"ucos.io/kernel/internal/policy"
	"ucos.io/kernel/internal/relay"
	"ucos.io/kernel/internal/store"
	"ucos.io/kernel/internal/triggers"
	"ucos.io/kernel/internal/trust"
	"ucos.io/kernel/packs/sample"
)

var (
	httpTotal = metrics.NewCounter("ucos_http_requests_total", "HTTP requests by method and status code.", "method", "code")
	httpDur   = metrics.NewHistogram("ucos_http_request_duration_seconds", "HTTP request latency.", metrics.DurationBuckets, "method")
	workTotal = metrics.NewCounter("ucos_worker_processed_total", "Items processed by background workers.", "worker")
	workErrs  = metrics.NewCounter("ucos_worker_errors_total", "Background worker cycles that failed.", "worker")
)

type statusRecorder struct {
	http.ResponseWriter
	code int
}

func (s *statusRecorder) WriteHeader(code int) { s.code = code; s.ResponseWriter.WriteHeader(code) }

func instrument(h http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		rec := &statusRecorder{ResponseWriter: w, code: http.StatusOK}
		h.ServeHTTP(rec, r)
		method := r.Method
		switch method {
		case http.MethodGet, http.MethodPost, http.MethodPut, http.MethodPatch, http.MethodDelete:
		default:
			method = "other"
		}
		httpTotal.Inc(method, fmt.Sprint(rec.code))
		httpDur.Since(start, method)
	})
}

type logPublisher struct{ log *slog.Logger }

func (l logPublisher) Publish(_ context.Context, topic, key string, value []byte) error {
	l.log.Info("event", "topic", topic, "key", key, "bytes", len(value))
	return nil
}

func env(k, def string) string {
	if v := os.Getenv(k); v != "" {
		return v
	}
	return def
}

func main() {
	log := slog.New(slog.NewJSONHandler(os.Stdout, nil))
	if err := run(log); err != nil {
		log.Error("ucos-kernel stopped", "error", err)
		os.Exit(1)
	}
}

func run(log *slog.Logger) error {
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()
	// Dependencies may start after the kernel (any orchestrator): wait for the database instead of crash-looping.
	var db *store.DB
	deadline := time.Now().Add(2 * time.Minute)
	for {
		var err error
		if db, err = store.Open(ctx, os.Getenv("UCOS_DATABASE_URL")); err == nil {
			break
		}
		if time.Now().After(deadline) || ctx.Err() != nil {
			return err
		}
		log.Info("waiting for the database", "error", err)
		select {
		case <-ctx.Done():
		case <-time.After(2 * time.Second):
		}
	}
	defer db.Close()
	if len(os.Args) > 1 && os.Args[1] == "migrate" {
		done, err := migrate.Apply(ctx, db.Pool, env("UCOS_MIGRATIONS_DIR", filepath.Join(env("UCOS_REPO_ROOT", "."), "db", "migrations")))
		log.Info("migrations applied", "count", len(done), "names", done)
		return err
	}
	var tenants []auth.TenantConfig
	if err := json.Unmarshal([]byte(env("UCOS_TENANTS", "[]")), &tenants); err != nil {
		return errors.New("UCOS_TENANTS must be a JSON array of tenant configs")
	}
	b := bus.New(db, env("UCOS_CELL", "dev-1"), nil)
	b.Register(sample.Pack{})
	if env("UCOS_ENFORCE_POLICY", "true") == "true" {
		pe, err := policy.Load(env("UCOS_REPO_ROOT", "."))
		if err != nil {
			return err
		}
		b.PEP = pe.PEP
		log.Info("policy enforcement on", "files", pe.Files)
	}
	active := &controlplane.Active{DB: db, TTL: 2 * time.Second}
	if env("UCOS_ENFORCE_ACTIVATION", "true") == "true" {
		b.Active = active.Check
	}
	if seed := os.Getenv("UCOS_SIGNING_SEED"); seed != "" {
		raw, err := hex.DecodeString(seed)
		if err != nil {
			return errors.New("UCOS_SIGNING_SEED must be hex")
		}
		signer, err := trust.NewSigner(raw)
		if err != nil {
			return err
		}
		token := os.Getenv("UCOS_ADMIN_TOKEN")
		if len(token) < 16 {
			return errors.New("UCOS_ADMIN_TOKEN must be at least 16 characters when the control plane is enabled")
		}
		cp, err := controlplane.New(db, env("UCOS_REPO_ROOT", "."), signer)
		if err != nil {
			return err
		}
		admin := &http.Server{Addr: env("UCOS_ADMIN_ADDR", "127.0.0.1:8081"), Handler: cp.Handler(token), ReadHeaderTimeout: 5 * time.Second}
		go func() {
			<-ctx.Done()
			_ = admin.Close()
		}()
		go func() {
			log.Info("control plane listening", "addr", admin.Addr, "key", signer.KeyID)
			if err := admin.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
				log.Error("control plane stopped", "error", err)
				stop()
			}
		}()
	}
	gw, err := gateway.New(env("UCOS_REPO_ROOT", "."), b, auth.NewVerifier(tenants, nil, nil), nil)
	if err != nil {
		return err
	}
	gw.Blueprint = active.Blueprint
	migrations := env("UCOS_MIGRATIONS_DIR", filepath.Join(env("UCOS_REPO_ROOT", "."), "db", "migrations"))
	gw.Ready = func(c context.Context) error {
		n, err := migrate.Pending(c, db.Pool, migrations)
		if err == nil && n > 0 {
			err = fmt.Errorf("%d migrations pending", n)
		}
		return err
	}
	for _, r := range gw.Routes() {
		log.Info("route", "route", r)
	}
	var pub relay.Publisher = logPublisher{log}
	if brokers := os.Getenv("UCOS_KAFKA_BROKERS"); brokers != "" {
		k, err := relay.NewKafka(strings.Split(brokers, ","))
		if err != nil {
			return err
		}
		defer k.Close()
		pub = k
	}
	workers := []struct {
		name string
		fn   func(context.Context) (int, error)
	}{
		{"relay", func(c context.Context) (int, error) { return (&relay.Relay{DB: db, Pub: pub}).Drain(c, 500) }},
		{"audit", func(c context.Context) (int, error) { return (&audit.Appender{DB: db}).Seal(c, 1000) }},
		{"triggers", func(c context.Context) (int, error) { return (&triggers.Engine{DB: db, Bus: b}).FireDue(c, time.Now()) }},
	}
	for _, w := range workers {
		go func() {
			t := time.NewTicker(time.Second)
			defer t.Stop()
			for {
				select {
				case <-ctx.Done():
					return
				case <-t.C:
					if n, err := w.fn(ctx); err != nil {
						workErrs.Inc(w.name)
						log.Error("worker", "worker", w.name, "error", err)
					} else if n > 0 {
						workTotal.Add(float64(n), w.name)
						log.Info("worker", "worker", w.name, "processed", n)
					}
				}
			}
		}()
	}
	if addr := env("UCOS_METRICS_ADDR", ":9090"); addr != "" {
		ms := &http.Server{Addr: addr, Handler: metrics.Handler(), ReadHeaderTimeout: 5 * time.Second}
		go func() {
			<-ctx.Done()
			_ = ms.Close()
		}()
		go func() {
			if err := ms.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
				log.Error("metrics listener stopped", "error", err)
			}
		}()
	}
	srv := &http.Server{Addr: env("UCOS_HTTP_ADDR", ":8080"), Handler: instrument(gw), ReadHeaderTimeout: 5 * time.Second}
	go func() {
		<-ctx.Done()
		shut, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		_ = srv.Shutdown(shut)
	}()
	log.Info("ucos-kernel listening", "addr", srv.Addr)
	if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
		return err
	}
	return nil
}
