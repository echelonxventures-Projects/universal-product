# UCOS Ω∞ — REAL-TIME CONNECTOR LAYER ARCHITECTURE

| Field | Value |
|-------|-------|
| ARTIFACT ID | UKB-ADV-001 |
| ARTIFACT | Real-Time Connector Layer Architecture (Workstream UKB-001, Deliverable 2) |
| PROGRAM | UCOS Ω∞ UKB Advancement Program (ADV) |
| STATUS | ACTIVE |
| PARENT | UKB-ADV-000 |
| DEPENDS-ON | UKB-ADV-000 |
| VOLUME | VOL-021 (DIGITAL TWIN) |

*Append-only extension overlay on UCOS-BOOK-000000. Defines the connector architecture and the reference implementation contract that turns authoritative external systems into append-only Signals. Modifies no existing artifact; embeds no secret (RR-07).*

---

## 1. PURPOSE

Create an event-driven, incremental, append-only connector layer that ingests state from authoritative systems and normalizes it into the universal **Signal** record. **Status is generated from authoritative systems; there is no manual status entry** (UKB-ADV-INV-04).

Target sources: **GitHub · GitHub Actions · Jira · SonarQube · OWASP Dependency-Check · Trivy · Prometheus · Grafana · OpenTelemetry · Kubernetes · Cloud Providers.**

## 2. CONNECTOR REFERENCE MODEL

Every connector implements one interface (reference in `tools/connectors/base.py`):

```
Connector
  ├─ name            : stable connector id           (e.g. "github-actions")
  ├─ sources         : [SOURCE enum]                 (GITHUB_ACTIONS, ...)
  ├─ dimensions      : [dimension]                   (build, security, ...)
  ├─ mode            : EVENT | POLL_INCREMENTAL
  ├─ cursor()        : returns last high-water mark  (append-only cursor store)
  ├─ fetch(since)    : yields raw events > cursor     (incremental)
  ├─ normalize(ev)   : raw event → Signal(s)          (pure, deterministic)
  └─ resolve(ev)     : maps external entity → subject_universal_id
```

### 2.1 Design requirements (from mission)

| Requirement | Mechanism |
|-------------|-----------|
| Event driven | Webhook receiver (`ukbx ingest --serve`) + queue; each event → `normalize` |
| Incremental synchronization | Per-connector high-water cursor (`DATA/connector-cursors.json`, append-only updates); `fetch(since=cursor)` |
| Append-only updates | `normalize` emits Signals appended to `DATA/signals.json`; never edits prior signals |
| No manual status entry | Rollup consumes only connector-sourced signals; `MANUAL` is rejected outside UKB-ADV-OVR |

### 2.2 Two ingestion modes

- **EVENT (push):** GitHub/Jira/Kubernetes/cloud webhooks and alertmanager hooks POST to the receiver, which validates signature (secret via external secret-manager handle, never stored), enqueues, and normalizes.
- **POLL_INCREMENTAL (pull):** SonarQube/OWASP/Trivy/Prometheus/Grafana/OTel APIs polled since the stored cursor on a schedule; only records newer than the cursor become signals.

## 3. SOURCE → DIMENSION → SIGNAL MATRIX

| Source | Feeds dimension(s) | Subject resolution key | Example signal state / metrics |
|--------|--------------------|------------------------|--------------------------------|
| GitHub | implementation, release | repo/path → REPO/artifact | `IMPLEMENTED`; PR merged |
| GitHub Actions | build, unit_testing, release | workflow → BLD/artifact | `IMPLEMENTED`/`BLOCKED`; pass/fail, duration |
| Jira | implementation, portfolio | issue key → artifact | `IN_PROGRESS`→`IMPLEMENTED`; epic state |
| SonarQube | quality | project → REPO/artifact | quality-gate `APPROVED`/`BLOCKED`; coverage %, bugs |
| OWASP Dependency-Check | security | project → REPO | `APPROVED`/`BLOCKED`; CVE counts by severity |
| Trivy | security | image/repo → BLD/REPO | `APPROVED`/`BLOCKED`; critical/high/medium |
| Prometheus | production, operational | job/service → SVC | availability %, error rate |
| Grafana | production, operational | dashboard/alert → SVC | alert firing → `BLOCKED` |
| OpenTelemetry | operational | service → SVC | latency p50/p95/p99, SLI |
| Kubernetes | deployment, production | deployment/ns → DEP/ENV | rollout `DEPLOYED`/`BLOCKED`; replicas ready |
| Cloud providers | infrastructure, production | resource/region → ENV/SVC | resource state, region availability |

## 4. SUBJECT RESOLUTION (external → Universal ID)

A connector must map an external entity to a `subject_universal_id`. Resolution order:
1. **Explicit binding** — a `.ukb-bindings.yml` in a repo declares `native_id → UCOS-...`.
2. **Native-ID match** — external label/annotation carries a native id (`IMP-006`) resolved via the Universal Artifact Registry.
3. **Path/name match** — repository path or service name matched against artifact `path`/`name`.
4. **Unresolved** — emit a signal against the program root with `evidence` noting the unresolved external ref, and open a **binding gap** (never guess identity; UKB-ADV-INV-05).

## 5. NORMALIZATION & IDEMPOTENCY

`normalize` is a pure function `(raw_event, cursor) → [Signal]`. Idempotency key = `(connector, source_event_id)`; a replayed event with the same key produces the same signal content and is deduplicated at append time. Because signals are append-only, a *corrected* upstream value arrives as a **new** signal with a later `as_of`; rollup uses the latest (UKB-ADV-INV-02).

## 6. SECURITY & GOVERNANCE

- Secrets referenced only by external secret-manager handle (`env://`, `vault://`, `awssm://`); never persisted in code, config, signal, or log (RR-07 / SRC-08 defense).
- Every signal is attributed (`connector`, `source`, `as_of`, `evidence`) — full audit trail.
- Connectors are read-only against source systems and write-only-append against the signal ledger; they never mutate canon (UKB-ADV-INV-01).
- Webhook endpoints authenticate signatures; failed verification is dropped and logged (without payload secrets).

## 7. REFERENCE IMPLEMENTATION

`tools/connectors/` ships a `base.Connector`, a `SignalLedger` writer, and offline **replay connectors** (`github_actions`, `trivy`, `prometheus`, `kubernetes`) that read fixture event files and emit signals — proving the contract end-to-end without live credentials. Live connectors subclass the same base and swap `fetch` for a real API/webhook. See `tools/ukbx.py ingest`.

## 8. TRACEABILITY

Connector definitions are registered as `CONN` entities (append-only) linked `Uses → subject artifacts`. Each ingest run is a `URUN` record referenced by every signal it produced, giving reverse traceability from any status back to the exact run and evidence.

*Return: [UKB-ADV-000](UKB-ADV-000-ADVANCEMENT-PROGRAM-MASTER-INDEX.md) · [Master Index](../UCOS-BOOK-000000-UNIVERSAL-MASTER-KNOWLEDGE-BOOK.md)*
