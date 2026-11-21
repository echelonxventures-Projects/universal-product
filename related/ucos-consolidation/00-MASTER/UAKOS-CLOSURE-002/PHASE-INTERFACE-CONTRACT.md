# UAKOS-CLOSURE-002 — Inter-Phase Handoff Contract (Phase-001 ⇄ Phase-002)

| Field | Value |
|-------|-------|
| STATUS | CONTRACT — documents existing interfaces. **No code changed.** |
| AUTHORITY | NONE — DERIVED TRUTH. |
| BASELINE | branch `governance-reconciliation` · HEAD `b67a720` |
| PURPOSE | Formalize what Phase-001 produces and Phase-002 consumes, so Phase-001 can be maintained without breaking Phase-002. |
| GOLDEN RULE | Phase-001 MUST NOT rename, remove, retype, or reorder the interface fields below without a **schema version bump** and Phase-002 sign-off. |

---

## 1. Interface surface

The **only** machine interface between phases is the file:

```
00-MASTER/UAKOS-CLOSURE-002/closure.json     (produced by closure_engine.py; consumed by phase2_engine.py)
```

Phase-002 also independently reads `00-BOOK/DATA/relationships.json` (owned by ukb — **not** a Phase-001 artifact; out of scope for this contract). The `01`–`14` Markdown files are **human-facing only** and have **no** machine consumer; Phase-002 does not parse them.

---

## 2. `closure.json` schema (contract v1)

Producer: `closure_engine.py` · Consumer: `phase2_engine.py` · Format: UTF-8 JSON, `sort_keys=True`, `indent=2` (deterministic) · Schema id (proposed): `ucos-uakos-closure-001` · Version: **1.0.0** (implicit; see §5).

### 2.1 Top-level object

| Key | Type | Consumed by P2? | Contract note |
|-----|------|:---------------:|---------------|
| `program` | string | no | constant `"UAKOS-CLOSURE-002"` |
| `baseline_commit` | string | **yes** (`model.get("baseline_commit")`) | short git SHA; P2 stamps it |
| `branch` | string | no | informational |
| `determination` | string | yes (informational) | `"CLOSED"` \| `"NOT-CLOSED"` |
| `gap_total` | int | yes (informational) | blocking gap count |
| `gaps` | object | yes | keys are stable invariants (see §2.2) |
| `concept_total` | int | yes | count of `concepts[]` |
| `dispositions` | object{str:int} | yes | disposition histogram |
| `families` | object{str:int} | yes | family histogram |
| `sources` | object | no | source counts (see §2.3) |
| `detail` | object | no | gap-detail lists (human/debug) |
| `concepts` | array<object> | **yes (primary)** | the concept ledger (see §2.4) |

### 2.2 `gaps` object (stable keys — do not rename)

`not_homed_concepts`, `upload_only`, `conversation_only`, `in_repo_unhomed`, `orphan_concepts`, `duplicate_canonical_homes`, `ukda_content_hash_duplicates` — all `int`.

### 2.3 `sources` object

`tracked_total`, `markdown`, `docx_uploads`, `corpus_present` (bool), `corpus_files` (int), `tracked_by_top` (object{str:int}).

### 2.4 `concepts[]` element — **the fields Phase-002 depends on**

Phase-002 reads these per concept (confirmed in `phase2_engine.py`): **`id`**, **`family`**, **`disposition`**, **`homed`**, **`in_repo_unhomed`**, **`in_code`/`in_constitution`/`in_book`/`in_spec`** (for canonical-home selection), **`exact_homes`**, **`def_homes`**, **`files`**. Full element (all MUST remain present, same names/types):

| Field | Type | P2-critical | Meaning |
|-------|------|:-----------:|---------|
| `id` | string | **yes** | canonical concept anchor (sort key) |
| `family` | string | **yes** | anchor family (UCKO/ARCH/DATA/…) |
| `disposition` | string | **yes** | IMPLEMENTED/SPECIFIED/PLANNED/DEFERRED/REJECTED/UNCLASSIFIED |
| `homed` | bool | **yes** | present in a canonical home |
| `in_repo_unhomed` | bool | **yes** | in repo but no home (gap) |
| `in_code`/`in_constitution`/`in_book`/`in_spec`/`in_filename`/`in_plan` | bool | **yes** | home-tier flags (P2 home selection) |
| `deferred`/`rejected`/`certified` | bool | yes | disposition inputs |
| `exact_homes` / `def_homes` | array<string> | **yes** | canonical home paths (P2 home count) |
| `files` | array<string> | **yes** | occurrence files (P2 co-occurrence graph) |
| `source_only_files`/`corpus_files` | array<string> | yes | gap-location subsets |
| `zones`/`tops` | array<string> | yes | provenance |
| `upload_only`/`conversation_only`/`orphan` | bool | yes | gap flags |
| `trace` | object{source,constitution,specification,implementation,certification:bool} | yes | traceability tiers |

---

## 3. Producer inventory (Phase-001 outputs) and their contracts

| Output | Producer | Consumer | Format | Schema | Version | Backward-compat requirement |
|--------|----------|----------|--------|--------|:-------:|-----------------------------|
| `closure.json` | `closure_engine.py` | `phase2_engine.py` | JSON | `ucos-uakos-closure-001` | 1.0.0 | **STRICT** — no field rename/remove/retype without version bump + P2 sign-off |
| `01`–`11`, `14` `*.md` | `closure_engine.py` | human | Markdown | none | n/a | may evolve freely (no machine consumer) |
| `12`,`13-VISION` certs | `closure_engine.py` | human | Markdown | none | n/a | may evolve freely |
| `closure_engine.py` | authored | invoked by `make closure`, hook, and (indirectly) P2 pipeline | Python 3, stdlib-only | — | — | **filename + `closure.json` path/name are load-bearing for P2** — do not rename |

---

## 4. Compatibility rules (binding on Phase-001)

1. **Do not rename** `closure_engine.py` or `closure.json`, or move them out of `00-MASTER/UAKOS-CLOSURE-002/`. Phase-002 hardcodes `HERE / "closure.json"`.
2. **Do not remove or rename** any `closure.json` field in §2. Adding **new** optional fields is backward-compatible and allowed.
3. **Preserve determinism** — `sort_keys=True`, sorted `concepts[]` by `id`, sets serialized as sorted lists. Phase-002 relies on stable ordering.
4. **Preserve the disposition vocabulary** (5 states + `UNCLASSIFIED`). New states require a version bump.
5. **Preserve `id` semantics** — `id` is the join key across phases; its format must not change silently.

---

## 5. Known compatibility risk (document, do not fix under freeze)

**Scan-mode variance.** `closure_engine.py` supports `CLOSURE_SKIP_CORPUS=1` (repo-only, `concept_total≈398`, `gaps≈2`) vs full-corpus (`concept_total≈506`, `gaps≈110`, incl. 108 conversation-only). Both are schema-identical, but **whichever mode last wrote `closure.json` changes the numbers Phase-002 reports** (observed live: `closure.json` moved 398→506 mid-session). 

- Risk: non-deterministic Phase-002 figures depending on who ran P1 last and in which mode.
- **Recommended resolution (post-freeze, needs authorization):** designate the **full-corpus** run as the canonical `closure.json`; write the fast repo-only pass to a separate `closure.repo-only.json`; add an explicit `scan_mode` + `schema_version` field to `closure.json`. **Not executed** — it is an interface change requiring P2 sign-off.

---

## 6. Handoff summary

```
External sources ─▶ closure_engine.py ─▶ closure.json (contract v1) ─▶ phase2_engine.py ─▶ 20..35 + phase2.json
                                            │                                                    │
                                   (human) 01..14 md                              (reconciliation recommendations)
                                            │                                                    │
                                            └──────────────▶ ukb.py (00-BOOK) ◀───────────────────┘
                                                   (only ukb updates Repository Truth; determination = 19)
```

**Contract status:** Phase-001 will maintain `closure.json` per §2/§4. Any change to the interface is gated on a version bump and Phase-002 sign-off. No interface change is made by this document.

---

*END — INTER-PHASE HANDOFF CONTRACT · DOCUMENTATION ONLY · NO CODE OR INTERFACE CHANGED · AUTHORITY = NONE.*
