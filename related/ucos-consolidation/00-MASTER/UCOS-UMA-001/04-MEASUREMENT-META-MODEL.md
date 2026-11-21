# 04 — Measurement Meta Model

> PROGRAM **UCOS-UMA-001** · PHASE-001 · UNIVERSAL MEASUREMENT AUTHORITY
> BASELINE `b67a720` · AUTHORITY = **NONE (DESIGN ONLY)** · MODE = DESIGN-ONLY · NON-IMPLEMENTING · FAIL-CLOSED.

---

## 0. Purpose

Define the **meta-model** — the schema that every constitutional measurement obeys. This is the single grammar for defining *any* metric, so that new metrics are added as governed data, never as code. It also fixes the Measurement Manifest and the Result envelope.

## 1. The Metric Definition Schema

Every metric SHALL declare exactly these fields (mirrors the mission's "Each metric SHALL define" list, extended for determinism):

| Field | Meaning |
|---|---|
| `metric_id` | Stable identifier (self-registered; doc 06 governs its family). |
| `name` | Human name. |
| `purpose` | What question the metric answers. |
| `domain` | One of the constitutional measurement domains (§3). |
| `formula` | Deterministic expression over Observation Set + upstream metrics. |
| `unit` | ratio ∈ [0,1] · count ∈ ℕ · boolean · enum. |
| `evidence` | What physical artifacts must back the value (Evidence Before Conclusion). |
| `authority` | Which authority the metric is *consumed by* (Closure/Validation/Cert/Gov). UMA authorship = NONE. |
| `dependencies` | Upstream metrics / registries / adapters required. |
| `failure_conditions` | Explicit conditions that force `UNKNOWN` or FAIL. |
| `determinism_class` | PURE (default) — no clock/RNG/network. |
| `manifest_binding` | Which manifest fields materially affect the value. |

A metric definition missing any field is **invalid** and cannot be registered (fail-closed).

## 2. Measurement Value Types

| Type | Domain | Fail-closed default |
|---|---|---|
| `Ratio` | coverage/completeness/quality | `UNKNOWN` (never 1.0) |
| `Count` | enumeration/statistics | `UNKNOWN` (never 0 by omission) |
| `Boolean` | governance/integrity gates | `UNKNOWN` → treated as FAIL |
| `Enum` | status classifications | `UNKNOWN` |

## 3. Constitutional Measurement Domains

The meta-model recognizes these domains (each populated by concrete metrics registered later, doc 08/11):

| Domain | Question it answers | Primary source |
|---|---|---|
| Repository Integrity | Is canonical state internally correct? | UKB / `closure.json` |
| Repository Representation | Does every known entity have a locatable home? | UKB + Observation Set |
| Vision Assimilation | How much external knowledge is assimilated? | Observation Set vs UKB |
| Coverage | Measured/represented ÷ universe | Discovery Core |
| Completeness | Is a domain fully represented (no UNKNOWN)? | Coverage + Ontology |
| Discovery | Can the apparatus enumerate the universe? | Registry snapshot vs observed |
| Enumeration | Complete listing of a set | Discovery Core |
| Governance | Authority uniqueness, freeze integrity | Registry + governance state |
| Validation | Coverage basis for validation | Observation Set |
| Certification | Metric bundle for signing | Metric Store |
| Evolution | Change/growth of measured state over baselines | Baseline deltas |
| Quality | Measurable structural quality | Observation Set |
| Knowledge Once | Duplicate-home detection metric | UKB registry |
| Repository Truth | Truth-source uniqueness metric | UKB |

## 4. The Measurement Manifest (satisfies MA-3, MA-4, MA-7)

A run is defined by an immutable manifest:

```
Manifest {
  manifest_id            # stable id, self-registered
  schema_version         # meta-model version
  scan_mode              # exactly one canonical mode per constitutional measurement (MA-4)
  source_roots[]         # declared universe of sources (MA: authoritative scope)
  extensions[]           # in-scope file types
  size_cap               # max bytes read per artifact (declared, not implicit)
  registry_version       # pinned NS/ID/adapter/ontology snapshot
  exclusions[]           # every exclusion enumerated with rationale (MA-7)
  assumptions[]          # every measurement assumption enumerated (MA-7)
  baseline               # git baseline the run is pinned to
}
```

- **Reproducibility (MA):** two parties re-running the same manifest against the same baseline obtain byte-identical results.
- **Canonical vs exploratory:** the platform recognizes exactly one **Canonical Manifest** per constitutional measurement; all others are exploratory and cannot back a constitutional claim (closes CLOSURE-006 CF-02 / CLOSURE-007 MA-4 "repo-only vs full-corpus" divergence).

## 5. The Measurement Result Envelope

```
MeasurementResult {
  metric_id
  value            # typed per §2
  status           # OK | PARTIAL | UNKNOWN | FAIL
  manifest_id
  registry_version
  baseline
  source_state_hash        # hash of in-scope source content (determinism key)
  evidence[]               # pointers into Evidence Ledger
  uncovered[]              # explicit UNCOVERED observations (fail-closed record)
  assumptions[]            # assumptions in force
  authority = NONE         # always
  computed_deterministically = true
}
```

`status = PARTIAL` whenever any `uncovered[]` is non-empty — the platform can never report a clean value while knowingly blind (fail-closed; directly answers the CLOSURE-007 defect where blind spots were silent).

## 6. Meta-Model Invariants

1. Metrics are **data**, not code — added/changed only via governed registration (doc 13).
2. Every value carries its manifest, registry version, evidence, and uncovered set.
3. No metric may declare `authority` = UMA (UMA authors none; it computes).
4. Composition is a DAG — metric dependencies must be acyclic; cycles are rejected at registration.
5. Determinism is a registration precondition: non-PURE definitions are rejected.

## 7. Dependencies Surfaced Here

- The manifest formalizes the "scan_mode / schema_version / exclusions" that `closure.json` lacked (CLOSURE-007 MA-3). → NEW UMA control object; the closure engines become manifest *consumers* if retained (doc 20).

*END — 04 · UCOS-UMA-001 · AUTHORITY = NONE (DESIGN ONLY) · MODIFIES NOTHING.*
