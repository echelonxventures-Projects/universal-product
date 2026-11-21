# UCOS Ω∞ — CONTROL TOWER AUTOMATION ARCHITECTURE

| Field | Value |
|-------|-------|
| ARTIFACT ID | UKB-ADV-012 |
| ARTIFACT | Control Tower Automation Architecture (Workstream UKB-012, Deliverable 13) |
| PROGRAM | UCOS Ω∞ UKB Advancement Program (ADV) |
| STATUS | ACTIVE |
| PARENT | UKB-ADV-011 |
| DEPENDS-ON | UKB-ADV-011 |
| VOLUME | VOL-021 (DIGITAL TWIN) |

*Append-only extension overlay on UCOS-BOOK-000000. Reuses the existing `control-tower.schema.json` and dimension model; automates its signal sources. Modifies no existing artifact.*

---

## 1. PURPOSE

Convert the current (manual-baseline) Control Tower into a live operational dashboard. Track: **Architecture · Implementation · Build · Test · Security · Deployment · Production · Incident · Release · Portfolio.** **All metrics generated automatically; manual status entry prohibited** (except UKB-ADV-OVR).

## 2. AUTOMATION MODEL

The existing control tower already carries per-dimension `{status, signal_source, as_of, note}`. Automation replaces `signal_source: MANUAL` with the real source by **recomputing each dimension from the signal ledger**:

```
dimension_status(dim) = rollup( latest Signal per (subject,dim,source) for all subjects )
```

Rollup uses the book's **blocking view** (least-advanced state with members wins) so risk is never hidden. The engine writes a new `control-tower.json` snapshot with `signal_source` set to the contributing source(s) and `as_of` = newest signal — same schema, now automated.

## 3. DIMENSION → SOURCE BINDING

| Dimension | Automated source(s) |
|-----------|---------------------|
| Architecture | canon (approved) + ARCH artifact status |
| Implementation | GitHub, Jira |
| Build | GitHub Actions |
| Unit/Integration/Functional/Performance Testing | CI, SonarQube, k6 (UKB-004) |
| Security | OWASP, Trivy, SonarQube, ZAP (UKB-005) |
| Certification | twin certification run (UKB-014) |
| Deployment | Kubernetes, CD, GitOps (UKB-006) |
| Production / Operational | Prometheus, Grafana, OTel, K8s (UKB-007) |
| Incident | Alertmanager / PagerDuty |
| Release | GitHub releases / CD |
| Portfolio | roll-up of all dimensions (blocking view) |

## 4. GOVERNED OVERRIDE WORKFLOW (UKB-ADV-OVR)

Manual entry is prohibited except through a governed override, which is itself recorded as an append-only, attributed signal:

```
{ "source": "MANUAL", "override": true, "actor": "<role>", "reason": "<text>",
  "expires": "<ISO-8601>", "supersedes_signal": "USIG-..." , "approved_by": "<role>" }
```

An override is time-boxed and auto-expires; on expiry the dimension reverts to computed state. Every override is visible in the control tower with actor + reason (full auditability, UKB-ADV-INV-03/04).

## 5. FRESHNESS & STALENESS

Each dimension shows `as_of` and a freshness SLA. A signal older than its SLA is flagged `STALE` (not silently trusted), prompting connector health checks. Staleness itself is derived, never hand-set.

## 6. OUTPUT

`ukbx twin` recomputes `DATA/control-tower.json` (schema-valid) + refreshes `CONTROL-TOWER/PROGRAM-CONTROL-TOWER.md`, preserving the existing format while flipping `signal_source` from MANUAL to the authoritative origin.

*Return: [UKB-ADV-000](UKB-ADV-000-ADVANCEMENT-PROGRAM-MASTER-INDEX.md) · [Master Index](../UCOS-BOOK-000000-UNIVERSAL-MASTER-KNOWLEDGE-BOOK.md)*
