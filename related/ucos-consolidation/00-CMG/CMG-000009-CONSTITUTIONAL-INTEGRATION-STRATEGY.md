# UCOS Ω∞ — CMG CONSTITUTIONAL INTEGRATION STRATEGY

| Field | Value |
|-------|-------|
| ARTIFACT ID | CMG-000009 |
| ARTIFACT | UCOS Ω∞ CMG Constitutional Integration Strategy |
| CLASSIFICATION | Constitutional Meta Governance (CMG) — Integration Strategy |
| PHASE | PHASE-000 |
| PROGRAM | CMG |
| CATEGORY | CMG |
| VOLUME | VOL-002 |
| STATUS | UNDER REVIEW · DERIVED · NON-NORMATIVE |
| VERSION | 1.0 |
| AUTHORITY | NONE (DERIVED TRUTH) |
| GOVERNED-BY | CMG-000001 |
| DEPENDS-ON | CMG-000001 |
| CANONICAL FORM | This Markdown file |

> Derived strategy under CMG-000001 Articles LVIII–LXVI. It states how the meta layer binds to every existing surface of the corpus without creating a parallel one.

---

## 1 — INTEGRATION PRINCIPLE

Every integration in this strategy follows one rule: **bind to the located surface; create none.** Where the corpus already has a store, a registry, a gate, a vocabulary, or a discovery surface, the meta layer uses it. Where it does not, the meta layer holds the fact in its own derived projection and nowhere else.

The measurable consequence: admission creates **zero** new stores, **zero** new registries, **zero** new lifecycles, **zero** new pipelines, and **one** new gate (CMG-000001 CMG-L-14, LXVI.7).

---

## 2 — REPOSITORY INTEGRATION

| Aspect | Binding |
|---|---|
| Zone | Exactly one: `00-CMG/`. The meta layer writes nowhere else (CMG-000001 LVIII.4) |
| Canonical homes | One per artifact, recorded in the projection; verified to exist by the gate |
| Repository Truth | Consumed, never redefined. Owned by the knowledge authority (`CMG-DLG-17`) |
| Frozen paths | Read-only by law. Untouched (LVIII.8) |
| Repository boundary | Not assumed. Namespace qualification and federation-scoped reach are declared in advance (LVIII.7) |

---

## 3 — CLASSIFICATION AND REGISTRATION INTEGRATION

This is the integration that most easily goes wrong, because the naive approach is to edit shared configuration.

**The naive approach, rejected.** Adding a path rule for `^00-CMG/` to the repository's classification configuration would work, but it is a change to machinery owned elsewhere, it must be repeated for every future zone, and it makes admission of a new constitutional zone a code change — a hard-coded enumeration in exactly the sense CMG-000001 CMG-L-08 prohibits.

**The approach taken.** Every CMG artifact self-declares its classification in its own front-matter table:

```
| PROGRAM  | CMG     |
| CATEGORY | CMG     |
| VOLUME   | VOL-002 |
```

The repository's classifier consults an artifact's self-declared metadata for any artifact not matched by an existing rule, so a new program participates with **zero configuration edits**. Independently, the CMG filenames all contain the token `CONSTITUTIONAL-`, which an existing classification rule already resolves to a real class — so classification succeeds by two independent paths, and neither requires editing shared machinery (CMG-000001 LVIII.6).

**Volume choice.** `VOL-002` (Constitution) is an existing volume. No volume is added, and nothing is renumbered.

**Status declaration.** CMG-000001 declares a status containing a token the repository's status parser recognizes, so its lifecycle state is machine-readable rather than inferred from a filename or directory (CMG-000001 XXVII.5).

**Identity.** Registration allocates universal identifiers from the located append-only ledger. Allocation is path-keyed, so no existing identifier is renumbered. The meta layer creates no second identity authority (`CMG-DLG-13`).

---

## 4 — TRACEABILITY AND RELATIONSHIP INTEGRATION

The corpus carries a typed relationship vocabulary in which an artifact declares outbound edges through front-matter row labels, and unknown relationship types may be self-declared without configuration change.

The CMG artifacts therefore declare their relationships through that vocabulary — `GOVERNED-BY`, `DEPENDS-ON`, `REFERENCES` — so the meta layer's edges appear in the located knowledge graph and traceability spine automatically. No second edge store, no second spine, and no hand-maintained traceability matrix is created (CMG-000001 XXXVII.2, XXXVII.4).

The sixteen CMG relationship types (`CMG-R-01` … `CMG-R-16`) are the **meta vocabulary** used for reasoning about constitutional relationships; where a located equivalent exists, the mapping is recorded in the projection and the located type is canonical (CMG-000001 XXXIV.5).

---

## 5 — KNOWLEDGE INTEGRATION

| Requirement | Realization |
|---|---|
| Every introduced concept is homed | Every CMG concept's canonical home is a file in `00-CMG/`; the corpus's unhomed-concept count is not increased (CMG-000001 LXI.3) |
| Knowledge Once | Constitutional truth is stated once in CMG-000001 and referenced everywhere; the projection and analyses reference, never restate normatively |
| No second discovery surface | The located knowledge graph remains the discovery surface (LXI.5) |
| Authority declaration | CMG-000001 is `constitutional`; every other CMG artifact is derived and declares `AUTHORITY = NONE (DERIVED TRUTH)` (LXI.4, XII.6) |
| No authority from the knowledge base | Reference is bidirectional; authority flows one way only (LXI.6) |

---

## 6 — ENFORCEMENT INTEGRATION

| Existing gate | CMG interaction |
|---|---|
| Lint / format (`engine`, `platform`) | Out of scope for `00-CMG/`; the validator was nevertheless confirmed clean against the repository's own ruff configuration |
| Test / coverage floor | Out of scope; the validator lies outside the coverage source set and cannot depress the floor |
| Pre-registration enforcement | Satisfied: every new file is valid (has a title) and classifiable (resolves to a real class) |
| Registration transaction / drift guard | Satisfied: new files register normally; no existing registration changes |
| Frozen-path guard | Satisfied: no frozen path touched |
| Determinism gate | Independent; the CMG validator is separately verified byte-identical |
| Closure gates | Satisfied: no concept left unhomed |
| **`cmg-gate` (new)** | One additive `.PHONY` target invoking the validator. No existing target, recipe, or dependency altered |

CMG-000001 LXVI.7 permits the meta layer **exactly one** gate. That budget is now spent; any future meta check extends the existing validator rather than adding a second gate.

---

## 7 — GENERATOR, IMPLEMENTATION, RUNTIME INTEGRATION

| Surface | Binding |
|---|---|
| Generators | Consume constitutional artifacts by identity and version; must record consumed versions; must not embed constitutional content in code (CMG-000001 LX.3, LX.5) |
| Implementation | Must trace to the obligation it realizes; admission is owned by the engineering governance authority (`CMG-DLG-23`); the meta layer's own implementation footprint is the validator and the projection, nothing more (LXII.5) |
| Runtime | Must resolve governing law by identity and version, fail closed when it cannot, and never treat operational memory as corpus (LXIII.2–LXIII.5) |
| Security | Constitutional artifacts are integrity-critical, tamper-evident by content hash; authority is never conferred by write access (LXIV.2–LXIV.4); controls are owned by the security authority (`CMG-DLG-33`) |
| Automation | Deterministic obligations are checked mechanically, fail-closed, configuration-driven, emitting findings not determinations (LXVI.1–LXVI.6) |
| Intelligence | Any intelligence may author, review, steward, and implement; none may own, be accountable, ratify, or self-elevate (LXV.1–LXV.8) |

---

## 8 — INTEGRATION SEQUENCE

| Step | Action | Blocking? |
|---|---|---|
| 1 | Place `00-CMG/` with CMG-000001, the projection, the validator, and the analyses | Done |
| 2 | Run the validator; require zero findings | Done — 0 findings |
| 3 | Confirm the located pre-registration gate accepts the new files | Done |
| 4 | Add the additive `cmg-gate` target | Done; reversible in two lines |
| 5 | Register the new artifacts through the located registration transaction | **Done — automatically.** The repository's own registration hook fired on artifact creation and executed the located Atomic Registration Transaction. 16 CMG artifacts registered; identifiers `UCOS-CON-000050` … `UCOS-CON-000063`, `UCOS-CMG-000001`, `UCOS-CMG-000002`. 0 existing identifiers renumbered, 0 existing content hashes changed. See CMG-000002 §3.2 |
| 6 | Route the four REQUIRES-REVIEW confirmations (CMG-000002 §5) to their owners | Open — see CMG-000013 R-05 |
| 7 | Obtain certification from the located certification owner | Open — preconditions satisfied, attestation is not the meta layer's act |
| 8 | Obtain ratification | **Blocked** — no located ratification authority (`CMG-OQ-01`) |

Steps 1–4 are complete and verified. Step 5 completed automatically through the repository's own registration hook. Steps 6–7 are ordinary acts of other owners. Step 8 is blocked by a pre-existing condition of the corpus, not by anything in this change.
