# PHASE — KNOWLEDGE IDENTITY RELATIONSHIP DETERMINATION

> **Mission:** Knowledge Identity Relationship Determination
> **Mode:** Discovery only. Repository evidence only. No code changes, no registry changes, no identity migration, no renaming.
> **Date:** 2026-08-13
> **HEAD:** `844c5056`

---

## 1. Identity Landscape

The scoping question named two identity domains (UCKP Registry / UCKO URN identity vs. Knowledge System / content-hash identity). Direct reads of the actual identity code show a **third layer beneath both**: a single, shared, actively-enforced canonical hashing primitive that both constructions are built on.

| Layer | Home | What it produces | Derivation |
|---|---|---|---|
| **L0 — Canonical hashing primitive** | `engine/uckp/canonical.py` (UCKP Layer Zero, Article 13) | `canonical_json`, `content_hash` — the one digest function "every content digest anywhere in UCOS Ω∞ is derived through" | Pure function over canonicalized bytes; stdlib-only, bottom of the dependency order |
| **L1a — UCKO URN identity** | `engine/uckp/identity.py` (Article 5) | `urn:ucos:ucko:<namespace>:<local_name>`, plus a name-derived UUIDv5 | `uuid.uuid5(namespace_uuid, urn)` — **not** content-hash-derived; a *minted*, namespace-qualified identity |
| **L1b — UCKO content/semantic digest** | `engine/uckp/ucko.py:39,321,323` | `content_sha256` (`content_hash(self._facet_core())`), `semantic_digest()` | Calls `content_hash` imported directly from `engine.uckp.canonical` (L0) |
| **L1c — Knowledge (CKO) identity** | `engine/knowledge/cko.py` + `engine/knowledge/model.py:37` | `cko_id` (free-form, author-assigned string) + `content_sha256`/`semantic_hash` | `model.py` line 37: `from engine.uckp.canonical import canonical_json, content_hash` — **the identical L0 function**, re-exported, not reimplemented |
| **L1d — UKIP knowledge identity** | `engine/knowledge/ukip/contracts.py:339-347` | `knowledge_id()` = `f"UKID-{digest[:12]}"`, `knowledge_sha256()` | Calls `content_hash` — UKIP's own docstring: `knowledge_sha256` "reproduces `CanonicalKnowledgeObject.semantic_hash` field-for-field ... so UKIP's notion of 'the same knowledge' is structurally identical to UKDA's and cannot drift from it" |

**The determining fact:** `engine/knowledge/model.py` does not reimplement content hashing — it imports `content_hash` from `engine.uckp.canonical` verbatim (confirmed at line 37), exactly as `engine/uckp/ucko.py` does (line 39). Both the URN-identity side and the knowledge-identity side compute their content digests with the **same function object**. This is not incidental: `engine/uckp/canonical.py`'s own docstring names nine modules — including `engine.knowledge.model` and `engine.registry.universal.identity` — that used to reimplement this primitive byte-for-byte before Layer Zero existed, and states "Nine byte-identical definitions are nine competing authorities over the same knowledge, which UCKP Article 3 (Zero Duplication) forbids. Each of those modules now re-exports from here." This non-duplication is not aspirational — it is mechanically enforced: `UCKP-INV-03` / `ConstitutionalValidator._probe_zero_duplication` (`engine/uckp/validation.py:395`) "parses every module in `engine` and `platform` and reports any module-level `canonical_json`, `canonical_bytes` or `content_hash` that implements the digest itself rather than forwarding to this module," and runs on every live gate.

A fourth, adjacent identity scheme was found and is named for completeness but is **out of scope for this determination**: `engine/registry/universal/identity.py` (UCOS-EPIC-001, `(kind, namespace, natural_key) → universal_id`). It is cited only in prose by `capability.py`, `ukip/contracts.py`, and `canonical.py` ("matches the discipline of...") — never imported by either domain under review — so it is evidence of a third convergent digest discipline, not a code coupling this determination needs to resolve.

---

## 2. Identity Authority Matrix

| Identity construction | Home | Answers | Derivation root | Registered in `identity_authority_resolution`? |
|---|---|---|---|---|
| UCKO URN identity | `engine/uckp/identity.py` + `engine/uckp/registry.py` | "Which constitutional object is this" — minted, namespace-qualified, admitted with refuse-on-clash | `uuid.uuid5` over namespace+name (not content_hash) | **Yes** — plane `CONSTITUTIONAL_OBJECT`, role `SUPREME — this IS UCKP-ART-05` |
| Repository object identity | `00-BOOK/DATA/id-ledger.json` | "Which version-controlled thing holds/produces/observes an object" | `UCOS-<CATEGORY>-<NNNNNN>`, append-only | **Yes** — plane `REPOSITORY_OBJECT`, role `PERSISTENCE` |
| CKO knowledge identity | `engine/knowledge/cko.py` (`cko_id`) + `engine/knowledge/model.py` (`content_hash`, imported from L0) | "Is this the same architectural-decision knowledge" | `content_hash` (L0, shared with UCKO) for the digest; `cko_id` is author-assigned, not derived | **No** — zero mentions of `content_hash`, `cko_id`, or `semantic_digest` anywhere in `00-BOOK/DATA/constitutional-authority-alignment.json` |
| UKIP knowledge identity | `engine/knowledge/ukip/contracts.py` (`knowledge_id`, `knowledge_sha256`) | "Do N independently-supplied units describe the same knowledge substance" | `content_hash` (L0, same function, explicitly reused from CKO's `semantic_hash`) | **No** — same absence |

The existing binding's own text is directly relevant here: `identity_authority_resolution.one_authority` states *"UCKP-ART-05 — Universal Identity. Every other identity mechanism in the repository is a persistence or projection binding of it."* This claim is **verified true** for the `REPOSITORY_OBJECT` plane (id-ledger.json derives its URN mapping from the ledger id verbatim, per the binding's own `derivation` block) but has **never been checked against, and does not currently hold for, knowledge identity** — CKO/UKIP identity is not a projection of the URN scheme (it does not derive from or reference any `urn:ucos:ucko:...` value anywhere; confirmed by grep — zero occurrences of `ucko_objects`/`UCKO_OBJECTS`/`UniversalKnowledgeRegistry` inside `engine/knowledge/`). It is a sibling construction that shares only the L0 hashing primitive, not the URN identity scheme itself.

---

## 3. Relationship Determination

Answering the four options directly, against the evidence above:

- **(A) Duplicate identity authorities — No.** A duplicate would mean two independently-implemented mechanisms answering the same question with no coordination and a real risk of drift. That is precisely what `engine/uckp/canonical.py` documents as the *pre-Layer-Zero* state (nine byte-identical reimplementations) and what `UCKP-INV-03` now actively forbids and verifies on every gate run. The digest primitive is unified, not duplicated.
- **(B) Independent bounded identity domains — Substantially yes, at the construction layer.** UCKO URN identity and knowledge content-identity answer genuinely different, non-overlapping questions (object admission vs. knowledge-substance equality), use different derivation logic at the top (`uuid5`-over-namespace vs. pure content digest), and are never cross-registered — no CKO/knowledge unit is ever minted a URN, no UCKO object is ever assigned a `cko_id`.
- **(C) Hierarchical identity models — No, not as currently declared.** The existing binding declares URN identity `SUPREME` with everything else as "a persistence or projection binding of it," but repository evidence shows this framing does not extend to knowledge identity: knowledge identity is not derived from, does not reference, and cannot be reconstructed from any UCKO URN. Calling it hierarchical would misstate what the code actually does.
- **(D) Missing federation relationship — Yes, this is the best fit, with one correction: the federation is not absent, it is undeclared.** A real, code-level, mechanically-enforced federation point already exists — the shared L0 `content_hash`/`canonical_json` primitive both constructions import verbatim — but nothing in `00-BOOK/DATA/constitutional-authority-alignment.json` records it. The gap is constitutional recognition, not missing engineering.

**Determination: primarily (D) — a real but undeclared federation, converging on (B) at the identity-construction layer.** Two independent, non-competing identity *constructions* (URN-minted object identity vs. content-derived knowledge identity) already share one governed, enforced *primitive* (Layer Zero canonical hashing) that the constitutional binding has simply never been extended to name. This is not (A) duplication and not (C) a clean, currently-accurate hierarchy.

---

## 4. Collision Risk Analysis

1. **String-level naming collision (the concrete, present risk).** Every seed and generated CKO identifier is conventionally prefixed with the literal string `UCKO-` — e.g. `UCKO-PRIN-0001`, `UCKO-CAP-02364C2ECF84`, `UCKO-DEC-0001` (confirmed in `engine/knowledge/seed.py`, `engine/knowledge/capability.py:61` — `CAPABILITY_ID_PREFIX = "UCKO-CAP"` — and live in `knowledge/canonical-knowledge.json`). This is the exact same four-letter acronym as `UniversalConstitutionalKnowledgeObject` (UCKP Layer Zero's object type), despite the two having **zero code relationship** — a `cko_id` of `UCKO-PRIN-0001` is never a valid `urn:ucos:ucko:...` value and is never looked up in `engine/uckp/registry.py`. A human or an agent grepping the repository for `UCKO-` will find both populations intermixed with no way to distinguish "a minted constitutional object identity" from "an author-assigned knowledge-object label" without reading the surrounding code. This is a real, present confusability risk, not a hypothetical one.
2. **Verb collision, lower risk.** "Knowledge identity" is used to mean two different things depending on which module is speaking — UCKP's Article 5 identity (any constitutional object) vs. UKDA/UKIP's knowledge-substance identity (architectural decisions specifically). `engine/uckp/law.py` itself uses "knowledge" at the general-object grain (`"Universal Constitutional Knowledge Object. Nothing exists constitutionally..."`, `binds=("knowledge", "identity")`), while UKDA's docstrings use it at the curated-decision grain. This mirrors the finding already recorded in `PHASE-KNOWLEDGE-REGISTRY-OWNERSHIP-RECONCILIATION-DETERMINATION.md §6` for the registry layer; the identity layer inherits the same ambiguity.
3. **No collision found at the primitive layer.** Because both constructions import the same `content_hash`, there is no risk of two different hash values existing for what should be one digest — `UCKP-INV-03` actively guards against exactly this failure mode, repository-wide, not just within these two domains.
4. **No collision found in storage.** `cko_id` values live only in `knowledge/canonical-knowledge.json`; UCKO URNs live only through `engine/uckp/registry.py`'s in-memory/discovery admission and `00-BOOK/DATA/id-ledger.json`. No shared keyspace, no observed overwrite risk.

---

## 5. Governance Gap Classification

- **Primary gap (D→declaration gap):** the real, existing Layer Zero federation between UCKO's and knowledge's digest primitives has no constitutional record. `identity_authority_resolution`'s `one_authority` claim ("every other identity mechanism ... is a persistence or projection binding of it") is unverified — and, as written, inaccurate — for knowledge identity specifically.
- **Secondary gap (collision, not duplication):** the `UCKO-` string prefix convention inside `engine/knowledge/seed.py`/`capability.py` collides, at the naming level only, with UCKP's own object-type acronym. Nothing malfunctions today because the two are never looked up against each other, but the collision is a standing readability/audit risk that grows with every new seeded knowledge object.
- **Not a gap:** the digest primitive itself. `UCKP-INV-03` already provides continuous, gate-enforced protection against this specific class of problem (re-implemented canonical hashing) — this is the one part of the landscape that is fully governed today.

This matches the dominant shape found throughout this session's reconciliation work: a real technical relationship already exists and is sound, but was never declared as constitutional fact — the same pattern Phase 0.6 (CMG↔UCKP) and the Certification and Knowledge-Registry-Ownership determinations each found and closed by declaration alone, with no code change required.

---

## 6. Recommended Constitutional Recognition

Not implemented in this determination, per scope. For a future, separately-approved binding pass, using the same reusable `*_resolution` mechanism already used four times this session:

1. **Extend `identity_authority_resolution`** with a new plane (or a sibling section, `knowledge_identity_resolution`, if the existing binding's `one_authority`/`SUPREME` framing is judged not to fit — that is a drafting decision for the implementing phase, not this determination) that:
   - Names `engine/uckp/canonical.py` (`content_hash`/`canonical_json`) as the one shared digest primitive both UCKO and knowledge identity are built on — citing `UCKP-INV-03` as the existing, already-adequate enforcement mechanism.
   - Records that CKO/UKIP knowledge identity is a **sibling construction**, not a projection, of UCKO URN identity: same root primitive, different top-level derivation, different bounded question, never cross-registered.
   - Corrects or scopes `identity_authority_resolution.one_authority`'s totalizing claim so it accurately describes what is and is not a projection of UCKP-ART-05.
2. **Record the `UCKO-` prefix collision** as a documented, accepted naming convention (not a defect) if the seed/capability ID scheme is to be kept as-is, so a future reader has a citable reason it is safe rather than having to re-derive it from source, as this determination had to.

Both are single, additive declarations following existing, already-proven precedent — no code, hashing, or identifier is required to change for either.

---

## 7. Non-Goals

- No file was modified. No registry, identifier, or hash was changed, migrated, or renamed.
- No code was tested or reviewed for correctness beyond reading its identity/hashing logic to determine ownership and relationship.
- No decision was made on which binding shape (extend `identity_authority_resolution` vs. a new sibling section) is correct — that is deferred to the implementing phase named in §6.
- No determination was made on `engine/registry/universal/identity.py` (UCOS-EPIC-001) beyond naming it as an adjacent, prose-only-cited, currently out-of-scope third convergent discipline.
- No verdict was reached on whether the `UCKO-` naming convention inside `engine/knowledge/seed.py`/`capability.py` should be changed — only that it exists and is a collision risk worth a recorded decision.
- Phase-8/9, `verify.sh`, and all live gates were **not run** — this determination required only static reads of identity/hashing source files and the existing CAA binding.

---

Stopping after determination, as instructed.
