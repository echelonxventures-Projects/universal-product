# Scope B · Workstream 3 — Universal Lineage Projection · Implementation Report

| Field | Value |
|---|---|
| CAPABILITY | Universal Lineage Projection (ULP) |
| MODE | Implementation + verification closure. **No certification claimed here.** |
| CONSTITUENT AUTHORITY | **NONE** |
| PREDECESSORS | Lineage Discovery · `F-1` Disposition · `F-1` Correction (CERTIFIED) · Architecture Determination |
| PRIOR BASELINE | `B-01` · `B-02` CERTIFIED — **unmodified** |

---

## 1. Objective

Answer **"how did this become this?"** by composing governed records that already answer parts of it, under the law that lineage is derived:

> `UCL-S-0350` / **`UCI-001 XVI.5` — "lineage and evolution are DERIVED projections over recorded history; no new store is created."**

---

## 2. Implementation Summary

| Path | Role |
|---|---|
| `engine/lineage/families.json` | The family classification — **data**, checked against the vocabulary owner |
| `engine/lineage/model.py` | Shapes: `Classification`, `Family`, `RelationRule`, `LineageEdge`, `LineageEvent`, `LineageProjection` |
| `engine/lineage/sources.py` | Reads the six governed sources and the owner's vocabulary. **Read-only** |
| `engine/lineage/projection.py` | Composition, serialisation, validation, `verify()` |
| `engine/lineage/query.py` | The six-question surface; every answer cites its source |
| `engine/tests/unit/test_lineage_projection.py` | **34 tests** |
| `00-BOOK/tools/ukb.py` | **Extended** — relation-type correctness (no new stage) |
| `pyproject.toml` | `engine/lineage` added to **both** coverage enumerations |

**Nothing persisted. No artifact created, no producer home added, no registry entry.**

---

## 3. Architecture Realization

Realized exactly as determined: **one projection, typed relations, four families, transformation kept as events.**

```
artifacts.json · relationships.json · change-ledger.json ·
generated-artifact-registry.json · birth-ledger.json · id-ledger.json
                        │  (read-only)
                        ▼
        UNIVERSAL LINEAGE PROJECTION   (derived · typed · in-memory)
                        │
          ┌─────────────┴─────────────┐
          ▼                           ▼
   six-question query          validation (ukb validate + engine)
```

Sources composed: artifacts 1,233 · typed edges 12,899 · change events 1,358 · change lineage 1,233 · generated 345 · births 38 · identity history 1,264.

---

## 4. Projection Model

| Family | Question | Edges | Source that owns the meaning |
|---|---|---|---|
| `structure` | What contains this? | **1,232** | `artifacts.json parent` |
| `dependency` | What requires this? | **5,009** | declared metadata rows |
| `derivation` | What produced this? | **1,932** | `generated-artifact-registry` producer + `input_closure` |
| `supersession` | What replaced this? | **10** | `change-ledger.lineage` + typed graph |
| *transformation* | What happened to this? | **1,358 EVENTS — never edges** | `change_events` |

**`structure` equals the declared containment facts exactly (1,232).** An earlier build reported 2,464 because `Parent` and its inverse `Child` express one fact twice; each fact is now carried once, under the **owner's** forward relation name — read from `RELATIONSHIP_TYPES`, not chosen here. Measured before adopting: `Parent` and inverted `Child` are exactly equal, and every `Required-By` has a forward `Depends-On`, so nothing is lost.

**Transformation is not a family.** `change_events` answer a different question from "what other object did this come from", and collapsing them would merge two questions into one answer.

---

## 5. Relationship Ontology Integration

**No vocabulary was created.** `families.json` classifies relations the owner already declares, and refuses to do anything else:

* every classified relation must exist in `00-BOOK/tools/config.py` `RELATIONSHIP_TYPES` — **44 directed names, 44 classified, 0 invented, 0 unclassified**;
* a relation classified into two families is refused;
* a relation both lineage and non-lineage is refused;
* a declared relation accounted for by neither list is refused, so a new type cannot be silently ignored.

**20 declared relations are classified `non_lineage`** — listed rather than omitted, so the classification is total.

**Multi-source attestation is preserved, not collapsed.** The change ledger records `UCOS-UMB-000024` as `Supersedes` `…000023`; the typed graph records the same pair as `Evolves-From`. Two governed sources describing one ancestry in their own vocabulary is not duplication, and dropping either would discard an attestation the repository holds. Each edge names its source, so a caller can tell them apart. *(An earlier test of mine asserted the opposite and was corrected — §9, D-2.)*

---

## 6. Canonical Primitive Reuse Evidence

Verified **structurally and by object identity**, not by reading import lines:

| Check | Result |
|---|---|
| Canonical primitives defined in `engine/lineage/` | **NONE** (AST scan of module-level functions) |
| `projection.canonical_json is uckp.canonical.canonical_json` | **True** |
| `projection.content_hash is uckp.canonical.content_hash` | **True** |
| `import hashlib` present | **False** — removed |
| `UCKP-INV-03 zero-duplication` | **PASS** — `verdict: CERTIFIED (17/17)` |

A rename or a shadowing local would fail the identity comparison, which is why it is used in preference to inspecting the source text.

---

## 7. Verification Coverage

| Mode | Exit | Stages | Tests | Failed | Coverage |
|---|---|---|---|---|---|
| `--fast` | **0** | 4/4 | 11,957 | 0 | 97% |
| `--change` | **0** | 9/9 | 11,957 | 0 | 97% |
| `--integration` | **0** | 14/14 | 11,957 | 0 | 97% |
| `--full` | **0** | **15/15** | 11,957 | 0 | 97% |

Module coverage: `__init__` 100% · `query` 100% · `model` 97% · `projection` 94% · `sources` 83%.

**Validation extended, never added.** `ukb validate` gained relation-type correctness beside the F-1 rule — proven by injecting an undeclared type (**exit 1**, named finding) and restoring byte-identically. **No new `verify.sh` stage.**

Refusals exercised: F-1 pattern at the projection layer · a cycle in an acyclic family · an undeclared relation · an invented relation in the classification · an unclassified declared relation · a relation in two families · a relation both lineage and non-lineage · an unknown ancestor direction · a missing section · a missing file · unparseable JSON.

---

## 8. Determinism Evidence

| Property | Result |
|---|---|
| Two builds byte-identical | **True** |
| Replay equality (`rendered`) | **True** |
| Digest stable across builds | **True** |
| Digest | `9f7a4b87d827b986…` |
| Validation | `status: PASS`, **0 problems** |
| No wall clock in the document | **True** |
| Writes nothing | 2 `open()` calls, both read-only; **no write mode anywhere**, no `write(` |

---

## 9. Defects Found and Corrected

All four were introduced by this implementation. None was a pre-existing defect.

### D-1 — one containment fact counted twice
* **Detection** — `structure: 2464` against 1,232 declared parents.
* **Root cause** — `Parent` and inverse `Child` each produced an edge for one fact.
* **Fix** — collapse per fact, preferring the owner's forward relation; loss measured as zero first.
* **Prevention** — `test_structural_edges_equal_the_declared_containment_facts`.

### D-2 — an over-strong test of my own
* **Detection** — a test failed on `UCOS-UMB-000024 ← …000023`.
* **Root cause** — I asserted at most one primary relation per fact. Two *different governed sources* legitimately attest one ancestry under different names. The assertion, not the data, was wrong.
* **Fix** — assert the true contract: one relation per fact **per source**; multiple sources allowed, each citing itself.
* **Prevention** — two tests replacing one, covering both halves.

### D-3 — module outside the coverage floor
* **Detection** — `engine.lineage` absent from both enumerations in `pyproject.toml`.
* **Root cause** — the same gap that bit `B-01`; the enumerations are explicit lists.
* **Fix** — added to both, **before** verification rather than after.
* **Prevention** — the 90% floor now applies to the module.

### D-4 — redefinition of the canonical primitive *(constitutional)*
* **Detection** — `./verify.sh --fast` failed: **`UCKP-INV-03 zero-duplication`**, `verdict: REFUSED (16/17)`.
* **Root cause** — I defined a module-level `canonical_json` inlining `json.dumps`. UCKP Article 13 permits exactly one definition, at `engine/uckp/canonical.py`. **A second canonicaliser is a second authority over every hash it produces** — precisely what a derived projection must never become.
* **Fix** — deleted it and delegated to Layer Zero. **Renaming would have dodged the scan while leaving the defect**, so reuse was the only correct remedy; the public helper is now `rendered()`.
* **Prevention** — `UCKP-INV-03`, unchanged, in every verification mode.

---

## 10. Governance Compliance

| Constraint | Result |
|---|---|
| No lineage authority | **HELD** — `families.json` declares `authority: NONE — DERIVED TRUTH` |
| No lineage store / registry | **HELD** — nothing persisted; absent from the generated-artifact registry by design |
| No producer home added | **HELD** — `producer_homes` unchanged at **31** |
| No lifecycle owner created | **HELD** |
| No identity authority changed | **HELD** — `category_seq` **117**, births **38**, `id-ledger` untouched |
| No counter opened | **HELD** — `category_seq` absent from source; `snapshot_seq` is a field *read*, and "counter" occurs only in docstrings denying one |
| No duplicate relationship vocabulary | **HELD** — 44/44 classified, 0 invented |
| No new `verify.sh` stage | **HELD** — `ukb validate` extended |
| Registry integrity | **HELD** — `ukb validate` PASS, 1,233 artifacts |
| Fixed point | **HELD** — pass 1 |
| Tree drift | **NONE** — 0 unstaged |

---

## 11. Remaining Gaps

Preserved explicitly, not silently solved.

| Gap | State |
|---|---|
| **Lineage completeness** | **OPEN.** Nothing asserts every node reaches a root. `validate()` deliberately does not answer it — a check that quietly did would be a claim this projection has not earned. |
| **Root reachability** | **OPEN.** Same reason. |
| **Capability Reality integration** | **OPEN — not implemented.** The projection assumes nothing about it. Lineage over capabilities becomes available when capabilities become objects, by registration. |
| **Entity Evolution integration** | **OPEN.** Evolution records are read for supersession; deeper integration is unbuilt. |
| **Certification lineage ownership (`G6`)** | **OPEN**, owned elsewhere. `Evidence-Of` — the one relation of the nine that does not exist — is what would key certification onto lineage. Not registered here. |
| **`GAP B-4`** | **OPEN**, referred to `UCL-000001`: `UCL-S-0320` remains discharged against the term vocabulary. |
| **Cross-vocabulary mapping** | **OPEN.** Three relation-type spaces exist; the projection reads the corpus one. Mapping between them is unchecked. |

---

## 12. Certification Readiness

| Criterion | Status |
|---|---|
| Four-mode verification | **PASS** — 15/15 stages, 11,957 tests, 0 failures, 97% |
| Constitutional compliance | **PASS** — UCKP 17/17 |
| Canonical primitive reuse | **VERIFIED** by object identity |
| Determinism and replay | **PROVEN** |
| Authority preserved | **VERIFIED** |
| Identity invariants | **UNCHANGED** — 117 / 38 |
| Evidence report | **THIS DOCUMENT** |
| Open gaps recorded | **YES** — §11, seven items |

**Ready for certification. Certification is NOT claimed here** — it follows separately, and against the final closed state including this report.

---

# IMPLEMENTATION COMPLETE
