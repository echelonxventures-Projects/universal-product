# 07 — Discovery Framework

> PROGRAM **UCOS-UMA-001** · PHASE-001 · UNIVERSAL MEASUREMENT AUTHORITY
> BASELINE `b67a720` · AUTHORITY = **NONE (DESIGN ONLY)** · MODE = DESIGN-ONLY · NON-IMPLEMENTING · FAIL-CLOSED.

---

## 0. Purpose

Define how UMA **discovers** architectural entities across all input sources, in a way that is **registry-driven, never regex-driven**, deterministic, replayable, and fail-closed. Discovery produces the **Observation Set** consumed by all L3 metric services.

## 1. The Discovery Contract

> Discovery enumerates every architectural entity that is *detectable under the registered adapters and registered families for the manifest scope*, and explicitly records every entity/source it **cannot** cover as an `UNCOVERED` observation.

Discovery never asserts completeness; it asserts *"this is what was observed, and this is precisely what could not be observed."* Completeness is a *metric* (doc 08), computed from the ratio of covered to universe — and it is `PARTIAL`/`UNKNOWN` whenever any `UNCOVERED` exists (fail-closed).

## 2. Three registered pillars (all self-registering — MA-1)

| Pillar | Registry | Answers |
|---|---|---|
| **Sources** | Source Adapter Registry | *What can be read?* (git, md, json, yaml, py, docx, pdf, img, graph, convo, future) |
| **Namespaces** | Namespace Registry (doc 05) | *What domains exist?* |
| **Identifiers** | Identifier Registry (doc 06) | *How are members named/matched?* |

Discovery = for each in-scope source → run its registered adapter → normalize → match against registered families + ontology → emit observations. Nothing is discovered that is not registered; nothing registered is silently skipped.

## 3. Source Adapter Registry (satisfies MA-5)

Each adapter self-declares:

```
SourceAdapter {
  adapter_id
  formats[]            # extensions / mime / source kind
  capability           # what it can extract (text, tokens, structure, relationships, metadata)
  disposition_on_fail  # DECLARE_UNCOVERED (never silent-drop)
  size_policy          # declared cap + behavior beyond cap (never implicit truncation)
  determinism_note     # must be deterministic for identical input
}
```

- **Non-text sources have declared dispositions (MA-5):** a PDF/diagram/image adapter either extracts (deterministically) or declares `UNCOVERED` with reason — never silently excluded as `TEXT_EXT` did.
- **Size caps are declared, not implicit (fixes 4 MB silent cap):** beyond `size_policy` cap, the adapter emits `UNCOVERED-OVER-CAP`, visible in the result.
- **Untracked/tracked scope is a manifest field**, not engine-internal (`CLOSURE_SKIP_CORPUS` becomes an explicit manifest `source_roots`/`scan_mode`, MA-4).

## 4. Discovery Modes

| Mode | Detects | Registry used |
|---|---|---|
| **Identifier discovery** | ID-shaped members | Identifier Registry (declarative rules, doc 06) |
| **Namespace discovery** | namespace presence + expected locations | Namespace Registry (doc 05) |
| **Structural discovery** | files, directories, artifacts, sizes | Source Adapters |
| **Relationship discovery** | edges (references, traceability, dependency) | Adapters + UKB graph |
| **Semantic discovery (MA-6)** | ID-less / prose concepts | Ontology Registry + Semantic Service |

Semantic discovery gives prose-only concepts a **declared measurement path** (MA-6): they are matched against a registered ontology (doc 08 Semantic/Ontology services), and where confidence is below a registered threshold they become `UNCOVERED-PROSE` — a declared, measurable gap rather than an invisible one.

## 5. Determinism & Replayability

- Discovery is a pure function of `(manifest scope, registry snapshot, source content)`.
- The `source_state_hash` over in-scope content is part of the result key; identical hash + identical snapshot ⇒ identical Observation Set (MA reproducibility).
- No wall-clock, RNG, ordering-by-filesystem, or network dependence (determinism class PURE).
- CLOSURE-007 already proved the *engine* was deterministic; UMA additionally makes *measurement* deterministic by pinning mode+registry in the manifest (fixes MA-4 "repo-only vs full-corpus" divergence).

## 6. The Exclusion & Assumption Register (satisfies MA-7)

Every exclusion — namespace, extension, directory, size cap, sentinel, corpus-skip — is a **first-class governed record** carried in the manifest and echoed in every result:

```
Exclusion { kind, target, rationale, authority, since_baseline }
Assumption { statement, rationale, impact_if_wrong, evidence }
```

No exclusion or assumption may be implicit. This makes report-09-style "Measurement Assumption Register" a permanent platform object rather than a one-off program artifact.

## 7. Fail-Closed Discovery Ledger

Discovery always emits, alongside observations, the complete negative space:

| Uncovered kind | Trigger |
|---|---|
| `UNCOVERED-NAMESPACE` | observed namespace token, no descriptor |
| `UNCOVERED-IDENTIFIER` | ID-shaped token, no matching family |
| `UNCOVERED-SOURCE` | source format with no registered adapter |
| `UNCOVERED-OVER-CAP` | artifact beyond declared size policy |
| `UNCOVERED-PROSE` | prose concept below ontology confidence threshold |

The presence of any entry forces downstream coverage/completeness metrics to `PARTIAL`. This is the structural guarantee that UMA can never repeat CLOSURE-007's silent blindness.

## 8. Dependency Determination

- The entire discovery role of `closure_engine.py` (sole discoverer, 26 regex families, text-only, corpus-optional, 4MB cap, hidden sentinels) is **TRANSFERRED** to this framework. Each of its embedded behaviors becomes an explicit registered record. The engine's *closure determination* role is untouched (RETAIN). Final in doc 20.

*END — 07 · UCOS-UMA-001 · AUTHORITY = NONE (DESIGN ONLY) · MODIFIES NOTHING.*
