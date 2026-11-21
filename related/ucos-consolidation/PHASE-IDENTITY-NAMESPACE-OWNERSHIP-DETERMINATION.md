# PHASE — IDENTITY NAMESPACE OWNERSHIP DETERMINATION

> **Mission:** Identifier Namespace Ambiguity — Namespace Ownership Determination
> **Mode:** Discovery only. Repository evidence only. No renaming, no migration, no code changes, no registry changes.
> **Date:** 2026-08-13
> **HEAD:** `844c5056`

---

## 1. Identifier Landscape

Direct reads show the bare token **"UCKO"** is used in three structurally distinct namespaces that never share a keyspace, a parser, or a lookup path:

| # | Usage | Home | Shape | Namespace kind |
|---|---|---|---|---|
| 1 | **Python symbol / class alias** | `engine/uckp/ucko.py:621` (`UCKO = UniversalConstitutionalKnowledgeObject`, in `__all__`); `engine/uckp/__init__.py:95` (`"UCKO": "engine.uckp.ucko"`, lazy-import table); `engine/uckp/intelligence.py:600` | Bare identifier `UCKO`, resolved by Python's own module/attribute namespace | Code-symbol namespace |
| 2 | **UCKO URN identity** | `engine/uckp/identity.py` | `urn:ucos:ucko:<namespace>:<local_name>` — "ucko" is a **fixed literal segment of the URN scheme prefix** (`UCKO_URN_PREFIX = "urn:ucos:ucko"`), never a user-suppliable value | URN scheme-identifier (structural constant, not assignable) |
| 3 | **Knowledge-object ID prefix (`cko_id`)** | `engine/knowledge/seed.py`, `engine/knowledge/capability.py:61` (`CAPABILITY_ID_PREFIX = "UCKO-CAP"`) | Free-form string `UCKO-<KIND>-<NNNN>`, e.g. `UCKO-PRIN-0001`, `UCKO-DEC-0001` | Flat, hyphenated text-content identifier — **zero regex or validation found anywhere in `engine/knowledge/`** |
| 4 | **Cross-repository text-reference family tag** | `00-MASTER/UAKOS-PHASE-{002,003,003R,004,005,006}/*.py`, `00-MASTER/UAKOS-CLOSURE-002/{phase3_engine,closure_engine}.py`, `00-MASTER/UAKOS-PHASE-001B/{provenance_engine,emit_registers}.py`, `00-MASTER/UCOS-MXR-001/roadmap_engine.py` — at least 12 independent scripts | `re.compile(r"\bUCKO-[A-Z]+-\d{3,4}\b")`, one of ~15 recognized "FAMILIES" alongside `UKDA-DEC`, `ARCH`, `MEP`, `MCP`, `MCS`, `CEP`, `DATA`, `SERVICE`, `RUNTIME`, `UCOS-COMP`, etc. | Text-scanning pattern recognition, read-only |

Usage 4 is a downstream **consumer** of usage 3's convention (it recognizes `UCKO-`-prefixed strings wherever they occur in prose/JSON, for completeness auditing — e.g. `"UCKO": "Missing Decision Record"` in `phase3_engine.py:139`, `"UCKO": "00-BOOK/MASTER-BOOK"` in `roadmap_engine.py:325`) — not an independent authority. It neither mints nor admits identifiers; it tallies occurrences of an already-existing convention.

**Key structural fact:** usage 1 (Python symbol) is resolved entirely inside Python's import machinery and never touches a string value. Usages 2–4 are string-content conventions that never touch Python's symbol table. No code path anywhere converts between them — confirmed by the prior determination's finding that `engine/knowledge/` has zero `ucko_objects()`/`UCKO_OBJECTS` provider-hook usage and zero import of `engine.uckp.registry`.

---

## 2. Namespace Ownership Matrix

| Namespace | Formally declared owner | Evidence of formal reservation | Actual governing mechanism today |
|---|---|---|---|
| Python symbol `UCKO` | `engine.uckp.ucko` (module-level) | Ordinary Python scoping — the module that defines a name owns it; no repo-specific rule needed or found | Python's own import system |
| URN scheme prefix `urn:ucos:ucko` | `engine/uckp/identity.py`, ratified in `identity_authority_resolution` (`00-BOOK/DATA/constitutional-authority-alignment.json`) — plane `CONSTITUTIONAL_OBJECT`, role `SUPREME` | Yes — the fixed prefix is declared as a module constant and the plane is constitutionally bound | `UniversalIdentity.mint()`, refuse-on-clash admission in `engine/uckp/registry.py` |
| `UCKO-<KIND>-<NNNN>` text ID prefix | **None found** | **No** — searched `engine/uckp/law.py` for "namespace"/"prefix" governance (zero results), searched for a `_ID_RE`/pattern constant on `cko_id` in `engine/knowledge/*.py` (zero results), searched `00-BOOK/tools/config.py` for a prefix-reservation table (none exists for this token) | Informal author convention (`seed.py`, `capability.py`) plus de facto recognition by the 12+ `UAKOS-PHASE-*` scripts' independently-defined but mutually-consistent regex |

`engine/uckp/vocabulary.py:510` defines `"namespace"` only as a **vocabulary term description** ("the namespaces the corpus defines," part of `DISCOVERY_DIMENSION_VOCABULARY`) — a label for a *discovery dimension*, not a registry of actual reserved namespace strings. No file in the repository enumerates "namespaces this repository reserves" as concrete values.

`00-BOOK/DATA/id-ledger.json` — the one append-only, mint-tracked identifier ledger this repository has (bound in `identity_authority_resolution`) — contains **zero** occurrences of "UCKO" as a category or identifier (confirmed by direct search). The `cko_id` convention was never registered there and never draws from its `category_seq` counters.

---

## 3. Collision Analysis

- **No mechanical collision exists.** Usage 1 (Python symbol) is resolved by import machinery; usages 2–4 are string content. A `cko_id` value such as `"UCKO-PRIN-0001"` is never passed to `UniversalIdentity.mint()`, never matched against `_NAMESPACE_RE`/`_LOCAL_RE` (which additionally requires the namespace component to be **lowercase** — `^[a-z0-9][a-z0-9._-]{0,62}$` — so `UCKO-PRIN-0001` could not satisfy that regex even if it were fed to it), and never looked up in `engine/uckp/registry.py`. No shared index, no shared parser, no shared keyspace.
- **No collision in the ledger.** `id-ledger.json`'s `UCOS-<CATEGORY>-<NNNNNN>` shape and mint-marker counters (`category_seq`) never contain or derive from "UCKO," confirmed by direct search — zero risk of a `cko_id` accidentally advancing or colliding with a ledger sequence.
- **A real but purely human/cognitive collision risk stands**, as already identified in the prior determination (`PHASE-KNOWLEDGE-IDENTITY-RELATIONSHIP-DETERMINATION.md §4`): a reader or an agent grepping the repository for "UCKO" encounters all four usages interleaved with no structural marker distinguishing them. The `UAKOS-PHASE-*` family's own regex (`\bUCKO-[A-Z]+-\d{3,4}\b`) is *itself* evidence this risk is already live in practice — twelve independently-authored scripts each had to encode the same disambiguating pattern by hand to avoid over-matching, which is exactly the kind of repeated, undeclared knowledge this repository's "Knowledge Once" principle exists to prevent.
- **No evidence of drift risk between the 12+ consumer scripts.** All twelve occurrences of the `UCKO` regex found are textually identical (`r"\bUCKO-[A-Z]+-\d{3,4}\b"`), suggesting they were copied from a common source rather than independently reinvented — which lowers (but does not eliminate) the risk that one of them silently diverges in a future edit, since nothing declares this pattern as a single source of truth today.

**Conclusion: zero actual (mechanical) identity collision. One real, already-materialized legibility/duplication-of-knowledge risk at the human/tooling level**, distinct from a data-integrity risk.

---

## 4. Authority Determination

Applying the four options directly:

- **(A) Harmless display naming overlap — Incomplete, not the best fit.** "Display naming" undersells usage 3: `cko_id` values are **functional identifiers** inside UKDA — referenced by other CKOs via `dependencies=("UCKO-PRIN-0001",)` and `knowledge_links=(...)` (confirmed in `engine/knowledge/seed.py`), and are the basis for the `UAKOS-PHASE-*` family's cross-repository completeness auditing. It is accurate to say the overlap is **harmless with respect to UCKP's identity mechanism specifically** (§3 confirms zero mechanical collision), but calling the whole situation "harmless" would understate that it is a real, load-bearing convention operating with no governing declaration.
- **(B) Namespace ownership violation — No.** A violation requires a formally owned thing to be encroached upon. §2 found no Article, vocabulary entry, ledger record, or CAA binding that reserves the bare token "UCKO" (or the `UCKO-<KIND>-<NNNN>` shape) for UCKP's exclusive use. `identity_authority_resolution` reserves the **URN scheme prefix** `urn:ucos:ucko`, which `cko_id` values never use or resemble structurally (no colons, no namespace/local-name pair). Nothing has been violated because nothing was ever declared reserved in the space `cko_id` actually occupies.
- **(C) Missing identifier namespace governance — Yes, best fit.** No article of UCKP root law governs human-readable ID-prefix ownership generally (confirmed: zero "namespace"/"prefix" governance in `engine/uckp/law.py`). The `UAKOS-PHASE-*` family's independently-but-consistently reimplemented regex is a de facto, unratified governance layer already operating in practice — this is a gap of *never having been declared*, not a gap of active malfunction.
- **(D) Actual identity collision — No.** §3 found zero mechanical collision: different parsers, different keyspaces, different regexes, and (critically) `_NAMESPACE_RE`'s lowercase-only constraint makes it structurally impossible for the URN namespace component to ever equal a `cko_id`-shaped string in the first place.

**Determination: (C) missing identifier namespace governance.** Not (B), because nothing formally owned exists to violate. Not (D), because no code path can produce a genuine collision. Not fully (A), because the overlap is functional and already load-bearing across 12+ independent scripts, not merely cosmetic — "harmless" is true only at the mechanical level, not at the governance-completeness level.

---

## 5. Governance Gap Classification

This is the same shape of finding as every reconciliation performed this session: a real, already-functioning relationship (here: a consistent, widely-adopted text-ID convention with a de facto consumer ecosystem) that has never been promoted to a constitutional declaration. Specifically:

- **Gap 1 — no declared owner for the `UCKO-<KIND>-<NNNN>` text-ID shape.** `engine/knowledge/seed.py` and `capability.py` originate it; nothing declares them the canonical source, and nothing prevents a future author from choosing a colliding or divergent convention.
- **Gap 2 — no declared relationship between the Python symbol `UCKO`, the URN scheme prefix, and the text-ID prefix**, despite all three sharing four letters purely by acronym coincidence (`UCKO` = `UniversalConstitutionalKnowledgeObject`; the text-ID prefix's origin is not documented anywhere as intentional or coincidental).
- **Gap 3 — the `UAKOS-PHASE-*` family's regex is not sourced from a single shared constant.** Twelve textually-identical copies exist; nothing declares one of them canonical, so a future edit to one could silently diverge from the other eleven with no test to catch it (unlike `engine.uckp.canonical`'s hashing primitive, which is guarded by `UCKP-INV-03`).

None of these is a defect today — all twelve regex copies currently agree, and no mechanical collision exists. They are latent maintenance and legibility risks stemming from the same root cause: an organically-grown, never-declared naming convention.

---

## 6. Recommended Recognition

Not implemented in this determination, per scope. For a future, separately-approved recognition pass, using the same reusable declaration mechanism this session has used repeatedly (a `*_resolution` section or an extension of the existing `identity_authority_resolution`):

1. **Declare `engine/knowledge/seed.py`/`capability.py` as the canonical origin of the `UCKO-<KIND>-<NNNN>` text-ID shape**, explicitly recorded as a *separate, coincidentally-acronym-sharing convention* from the URN scheme prefix — closing Gap 1 and Gap 2 by declaration, matching how Phase 0.6 resolved CMG↔UCKP's naming overlap with an `ORTHOGONAL` role rather than a rename.
2. **Record the `UAKOS-PHASE-*` family's `FAMILIES` regex list as a recognized, existing artifact-reference taxonomy** (not a new one — it already exists and is already consistent across 12+ files), so a future change to the `UCKO` pattern in one file is understood to require the same change everywhere it is duplicated — closing Gap 3 without consolidating the files themselves.
3. **Optionally extend `identity_authority_resolution`'s `second_authority_test`** (currently scoped to append-only *mint* authorities) with an explicit statement that text-content ID-prefix conventions are a different governance question from identity *minting*, so a future reader does not conflate the two the way this determination's scoping prompt initially did.

No renaming, migration, or code change is implied by any of the above — each is a declaration of what repository evidence already shows to be true.

---

Stopping after determination, as instructed.
