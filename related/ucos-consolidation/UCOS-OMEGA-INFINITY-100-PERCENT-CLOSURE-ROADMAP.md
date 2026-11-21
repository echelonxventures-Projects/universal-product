# UCOS Ω∞ 100% CLOSURE ROADMAP

**Checkpoint:** `03179308` (integration/recovery-001)
**Compiled:** 2026-08-21, companion to the Master Index and Gap Register
**Posture:** Roadmap only. **Nothing in this document has been implemented.** Sequencing and risk assessment for the 13 non-certified items, plus the exact conditions under which 100% closure may honestly be claimed.

---

## Execution order

Ordered by dependency and risk, not by discovery order. Independent items may run in parallel; items sharing an owner/file are grouped and sequenced together.

| Order | Requirement | Owner | Current state | Approach | Dependencies | Risk | Validation | Certification criteria |
|---|---|---|---|---|---|---|---|---|
| 1 | `REQ-50` — UIEP-001 document | Constitutional Authority | Never created | Same treatment as `UAP-001`: declared design principle, explicitly non-certified, not a `CEP-002` decision | none | **none** — pure documentation | document review only | document exists, boundary statement present |
| 2 | `REQ-02` — CEU supersession history | CEU-001 | `_supersessions` mutated in place | Widen `dict[str,dict]` → `dict[str, list[dict]]`, append-only | none | **low** | existing 2 resurrection tests pass unchanged; new `supersession_history()` test | field-level reconstruction proven by test |
| 3 | `REQ-35` — UCDA append-only decision history | `UCDA-000001` | No mutation API; edits are raw JSON overwrites | `decision_history` ledger (`AuditEntry`-shaped) **or** git-commit-discipline policy — choice not yet made | none, but should land before further decisions accumulate un-audited | **medium** — touches the schema every governance record in this repo depends on | `ucda_engine.py --gate` computes the same verdict before/after; a decision mutated twice yields two recoverable states | `verify_audit()`-equivalent passes |
| 4 | `REQ-14` — `KnowledgeStore` destructive replace | UKDA | `replace_object()`/`save()` discard prior version | Route through existing `supersedes`/`superseded_by` fields | none | **low** | old + new coexist in `_objects` after "replace" | round-trip test |
| 5 | `REQ-34` — Provenance chains never persisted | UKIP | `ProvenanceChain` never written to disk | Extend `KnowledgeStore`'s existing JSON write to include `ProvenanceChain.to_dict()` | `REQ-14` (same file, sequence after to avoid two overlapping changes to `store.py`) | **low** | persist → simulated restart → recover byte-identical | round-trip test |
| 6 | `REQ-06` remainder — UCXI per-kind context binding | UCXI-000001 | Only `KNOWLEDGE` kind wired | Replicate `confidence.py`'s pattern per additional kind, one at a time | `ADR-0016` (pattern source) | **low per kind**; scope risk only if attempted as one large change | same test shape as `test_confidence.py`, per kind | passing tests per kind added |
| 7 | `REQ-39` — Mutation classification for authored documents | `platform.repository_intelligence.mutation_classification` | No `AUTHORED_DOCUMENT`-equivalent rule | First: run `classify()` against a real ADR to confirm current fall-through behavior. Then, if genuinely needed: one new rule + predicate | `REQ-38`'s existing mechanism (already certified — reused, not rebuilt) | **low**, contingent on the measurement step above possibly showing this is already acceptable | `validate_rule_coverage()` passes; sample ADR classifies correctly | new rule declared, predicate implemented, coverage check passes |
| 8 | `REQ-43` — `KnowledgeStore` storage-technology abstraction | UKDA | Direct JSON I/O, no interface | Generalize `engine/uckp/persistence.py`'s `PersistenceAdapter` to a `Protocol` both `UCKO` and `CanonicalKnowledgeObject` satisfy | `REQ-14`/`REQ-34` (settle `KnowledgeStore`'s write path first) | **medium** — must not regress `engine/uckp`'s existing 52 tests while generalizing | `engine/uckp`'s existing contract test suite still passes; a new contract test exists for `KnowledgeStore`'s adapter | round-trip identical across ≥2 technologies for `CanonicalKnowledgeObject` |
| 9 | `REQ-28` — 192-document corpus registration | `REG-AUTO-001`/`UMB-IMP-001` | Unregistered, non-blocking, unowned by any decision | Dedicated `CEP-002 Article 28` decision enumerating the population (or its deterministic enumeration mechanism), explicit irreversibility disclosure, at 7-8x `ADR-0017`'s scale | Best attempted last, after the smaller-scope pattern (`ADR-0017`/`0018`, this session) has been exercised and is trusted | **highest** — `register.sh --guard`'s full transaction is implicated, not just identity minting; this repo's own `test_verification_purity.py` module docstring names the exact prior incident this risk profile matches (140 identities minted, ~140 pages emitted, left uncommitted) | `ukb.py enforce --pre` reports 0 unregistered eligible; `UGA-INV`/`CAA-INV` unaffected; full-suite survives per `DEC-ADR-0020`'s fixed fixture | decision registered → minted → survives 2 consecutive full-suite runs (same bar `ADR-0017` met) |

**`REQ-46`/`REQ-47`/`REQ-44`/`REQ-45`** are intentionally absent from this table: no action is recommended for any of them (see Gap Register) — building an abstraction or a test solely to move them off `SUPPORTED`/`NOT APPLICABLE` would manufacture evidence rather than discover it, and this roadmap does not schedule that.

---

## Aggregate risk view

- **3 items, no risk / documentation only:** `REQ-50`.
- **5 items, low risk:** `REQ-02`, `REQ-14`, `REQ-34`, `REQ-06` (per kind), `REQ-39`.
- **2 items, medium risk:** `REQ-35` (schema every decision depends on), `REQ-43` (generalizing a proven, tested pattern without regressing it).
- **1 item, highest risk:** `REQ-28` — the only item this roadmap recommends extra deliberation for beyond the standard `CEP-002 Article 28` discipline already used throughout this session.

Every item's approach reuses an existing pattern already proven this session (`ContextRegistry`'s replace-not-mutate discipline, `supersedes`/`superseded_by`, `PersistenceAdapter`, the `EX-015`/`EX-016` declarative classification mechanism, or `ADR-0017`'s mint-with-explicit-scope discipline) — none requires inventing a new architectural concept.

---

## Phase 9 — Exact conditions for 100% closure

100% closure may be claimed **only** when every condition below is independently true, not assumed:

| Condition | Current state |
|---|---|
| ✓ All requirements mapped | **Met** — 49 requirements in the Master Index; no requirement discussed this session is absent |
| ✓ All ownership resolved | **Met** — every requirement in the Master Index names a canonical owner; `CAA-INV-01..07` confirm no ownership ambiguity exists in the measured governance surface |
| ✓ All governance completed | **Not met** — `REQ-28` has no decision; `REQ-39`, `REQ-43`, `REQ-50` have no decision either (though 3 of those 4 are small/optional) |
| ✓ All implementations completed | **Not met** — 9 of 13 non-certified items require code or document changes not yet made |
| ✓ All validations passing | **Partially met** — everything currently implemented passes (12,133/0/3, 97.33% coverage, all 10 gates); the 9 pending items have no validation yet because they don't exist yet |
| ✓ All evidence generated | **Partially met** — evidence exists for everything certified; no evidence exists for what isn't built |
| ✓ All certifications reproducible | **Met, for what is certified** — this session's own discipline of re-running full suites and gates twice consecutively (`DEC-ADR-0020`'s validation) is the standing bar |
| ✓ No unknown gaps remaining | **Met in the sense of "no undiscovered gaps"** — every gap found this session is named, owned, and registered here or in `WP-UCDA-028`; **not** met in the sense of "no gaps," since 13 remain open or governed-pending |

**Honest summary: 5 of 8 conditions fully met, 2 partially met, 1 not met.** This is not 100% closure. It is a complete, evidence-backed map of exactly what stands between the current state and 100% closure, with every remaining item owned, sequenced, and risk-assessed — which is what this directive asked for, and no more than that.
