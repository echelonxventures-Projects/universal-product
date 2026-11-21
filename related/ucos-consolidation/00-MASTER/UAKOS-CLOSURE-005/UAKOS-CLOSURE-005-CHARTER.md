# UAKOS-CLOSURE-005 — Continuous Knowledge Ingestion (Program Charter · INITIALIZATION)

| Field | Value |
|-------|-------|
| STATUS | INITIALIZATION (planning only). If a canonical charter already exists, that one governs (Knowledge Once). |
| AUTHORITY | NONE — DERIVED TRUTH. |
| BASELINE | HEAD `b67a720` |
| PREDECESSOR | `UAKOS-CLOSURE-002` (FROZEN); operationalizes the External Knowledge Ingestion capability permanently. |
| STATUS | INITIALIZED — not started. |

## 1. Mission

Keep Repository Truth permanently synchronized with the evolving vision by continuously ingesting and reconciling **new** knowledge — so conversation-only and upload-only knowledge can never accumulate again.

## 2. Responsibilities

- **Monitor** new repository artifacts, uploaded documents, and shared conversations/external corpora.
- **Reconcile** each new item through the frozen pipeline (`closure_engine.py` S1–S7): extract → match → gap → route recommendation.
- **Prevent** future conversation-only / upload-only knowledge by flagging unreconciled items fail-closed (advisory gate, doc `50`).
- **Maintain** ongoing reconciliation: run on ingestion events + CI + SessionStart hook (already wired: `.kiro/hooks/uakos-closure-002.json`, `make closure`).

## 3. Hard constraints (inherited guarantees, doc `67`)

- Produces **evidence + recommendations only**; writes Repository Truth **only** via `ukb.py` (routes to -003/-004 for enrichment/certification).
- Reuse the one engine, graph, registries, traceability; introduce none.
- Deterministic + fail-closed; honor the `closure.json` interface contract v1 (pin scan-mode, AB-6).

## 4. Inputs / Outputs

- **Inputs:** new/changed sources (repo, `00-SOURCE`, root uploads, external corpus/chats).
- **Outputs:** refreshed `closure.json` (measurement), new-gap alerts, reconciliation recommendations → hand to -003/-004.

## 5. Boundary

Detection + reconciliation recommendation only. Implementation is -003; certification is -004. This program is the **standing gate** that keeps closure from regressing.

---

*END — UAKOS-CLOSURE-005 Charter · INITIALIZATION · AUTHORITY = NONE.*
