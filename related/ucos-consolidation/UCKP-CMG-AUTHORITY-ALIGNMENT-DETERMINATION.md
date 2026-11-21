# UCKP-CMG AUTHORITY ALIGNMENT DETERMINATION

> **Mission:** UCOS Ω∞ Universal Evolution Foundation, Phase 0.5 — Constitutional Authority Alignment Determination
> **Mode:** READ-ONLY. No CMG modification, no UCKP modification, no new constitution, no new registry, no new engine.
> **Date:** 2026-08-13
> **Placement note:** Requested location was `00-BOOK/DATA/UCKP-CMG-AUTHORITY-ALIGNMENT-DETERMINATION.md`. That directory is listed verbatim in `00-BOOK/tools/config.py`'s `EXCLUDE_DIR_PREFIXES` (confirmed by direct read, line 890: `"00-BOOK/DATA/"`), which means any file placed there is **excluded from document-corpus registration** by the indexer that governs artifact identity in this repository. A determination placed there would never acquire an identity, would never appear in the corpus registries, and would be invisible to `ukb.py validate`/`enforce` — the opposite of what this mission requires ("zero anonymous objects"). This document is therefore placed at the repository root instead, following the repository's own established convention for cross-cutting determinations (`P0-ASSIMILATION-001-UNIVERSAL-CONSTITUTIONAL-ASSIMILATION-DETERMINATION.md`, `UCOS-P0-CONVERGENCE-001-CONSTITUTIONAL-CONVERGENCE-DETERMINATION.md`, and 13 further siblings, all root-level `*-DETERMINATION.md` files). Confirmed post-write: `ukb.py enforce --pre` and `00-CMG/tools/cmg-gate.sh` both still pass — see closing note.

---

## 1. Executive Determination

**Question:** Is UCKP deliberately excluded from CMG recognition?

**Answer: NO — evidenced as omission, not exclusion. But the investigation surfaced a second, more material finding that the question as posed does not capture: a scope ambiguity in UCKP's own self-declared supremacy clause that has never been tested against CMG's framework, because the two have never been brought into contact.**

Evidence for "omission, not exclusion":

- CMG-000001 Article LXXXII (Delegation Register) lists 49 delegated concerns (`CMG-DLG-01`..`CMG-DLG-49`) plus 11 retained concerns (`CMG-RET-01`..`CMG-RET-11`). `engine/uckp/` appears in **neither list**, and no clause of CMG-000001 mentions `UCKP`, `engine/uckp`, or `ROOT_LAW` by name (verified by full-text grep across all 2,024 lines).
- CMG-000001 does not claim its register is exhaustive: **LXXXII.6** states outright, *"This register IS not exhaustive of the corpus and does not claim to be... A concern absent from both LXXXII.2 and LXXXII.3 IS outside this instrument's engagement, and if it is also unowned it IS a gap under Article LXXVIII."* UCKP is not unowned — it has an active, tested, gate-enforced owner (`engine/uckp/`, consumed by `uga_engine.py` and bundled into the `verify.sh` gate chain). So by CMG's own test, this is not even a "gap" in its formal sense — it is a located, functioning owner that the meta layer's own register simply has not yet enumerated.
- `00-CMG/CMG-REGISTRY.json`'s `namespaces` array recognizes 14 legacy markdown-constitution namespaces (`DATA`, `PLATFORM`, `SECURITY`, `SERVICE`, `APPLICATION`, `INFRASTRUCTURE`, `RUNTIME`, `CONST`, `CEP`, `CAT`, `REF`, `AUTH-INF`, `UCI`, `GOV-INT`) and its `kinds` array includes a `CMG-K-14 Engine — Executable` kind that a code-level authority like UCKP could plausibly be classified under — but no `UCKP` token exists in either array. This is consistent with a register that was populated by walking the pre-existing markdown corpus and has not yet been extended to the newer, code-native `engine/uckp/` layer (UCKP's docstrings reference "Layer Zero" and read as a distinct, more recent architectural generation than the ~100 markdown `*-CONSTITUTION.md` files CMG was built to reconcile).
- Nothing in CMG-000001 argues against recognizing an executable authority in principle — Articles LXII (Implementation Integration) and LXIII (Runtime Integration) exist specifically to state the meta-requirements such a layer must satisfy, and UCKP's supporting modules already satisfy them (see §3).

**The second finding — the actual material risk:** `engine/uckp/law.py` declares an unconditional `SUPREMACY_CLAUSE`:

> *"Every constitutional entity shall exist exactly once as a canonical Universal Constitutional Knowledge Object. Every representation, execution environment and persistence mechanism of that entity is a view of it and holds no independent architectural authority. No architectural authority exists outside this principle."*

Read narrowly, this is a domain-scoped rule about object *representation* (consistent with `UCKP-INV-02` "single-authority" and `UCKP-INV-05` "zero-projection-authority" elsewhere in the same file) — not a claim to override `DATA-001`, `SECURITY-001`, or any other domain constitution's substance. Read at face value, the closing sentence — *"No architectural authority exists outside this principle"* — is unconditional and unscoped, with no reference to CMG, no acknowledgment of Tier T1's vacancy, and no provisional framing. CMG imposes exactly this discipline on **itself** — LXXXI.5: *"This instrument does not occupy Tier T1... Any reading of this instrument as occupying T1 IS erroneous and IS void"*; LXXXI.6: *"This instrument SHALL NOT self-elevate... Its standing IS PROVISIONAL until conferred by a located competent authority"* — but UCKP's law.py contains no analogous clause. This is not evidence of a deliberate power grab (nothing in UCKP's code references CMG, T1, or claims to bind other domains — the surrounding modules are conspicuously deferential; see §3), but it is a real, literal-text ambiguity that has never been reconciled, because CMG and UCKP have evidently evolved on separate tracks. **This is the finding future work must actually resolve** — narrower than "is UCKP recognized," and not resolvable by simply adding a registry row.

---

## 2. CMG Authority Model

**Purpose** (Article VII): meta-governance is *"the governance of governance: the allocation, ordering, and recognition of authorities, as distinguished from the exercise of authority."* It exists to close the residue left when a corpus of domain constitutions is locally complete but globally incomplete (VII.2–VII.3).

**Scope:** CMG governs *recognition* of constitutional instruments — what counts as one, how they rank, where vacancies exist. It explicitly disclaims governing:
- **Substance** (LXXXI.2: *"This instrument holds no substantive authority and therefore SHALL NOT be read as superior to any domain constitution on any question of substance"*).
- **Process** (LXXXI.3: orthogonal to `CEP-000`, the Program Authority governing constitutional-engineering process).
- **Interpretation** (LXXXI.4: orthogonal to `AUTH-INF-001`, sole owner of constitutional interpretation).
- **Implementation mechanism** (LXII.5: *"This instrument's own implementation footprint SHALL be exactly the validator of Article L and the derived Registry of Article XV. It SHALL introduce no engine, service, runtime component, or persistent store."*)

**Authority boundary:** CMG occupies Tier **T1M** (Meta-Constitutional Authority) in its own precedence lattice (Article XVI) — orthogonal to, not superior to, Program Authority (T2) and Interpretive Authority (T2I); subordinate in substance to Domain Authority (T3) wherever substance is at stake. It explicitly, repeatedly disclaims occupying **T1** (Constitutional Authority — the ratified, substantive constitution), which the lattice records as **VACANT** (XVI.2, XVII.4, LXXXI.5, tracked as open question `CMG-OQ-02`).

**Ownership:** `00-CMG/` exactly, and only. LVIII.4: *"This instrument SHALL occupy exactly one repository zone, `00-CMG/`, and SHALL NOT write into any other zone."*

**Limitations, in CMG's own words:** *"This instrument holds no substantive authority"* (LXXXI.2); *"Its standing IS PROVISIONAL until conferred by a located competent authority"* (LXXXI.6); *"Where any clause of this instrument would decide a substantive matter, that clause IS void by operation of CMG-INV-12 without amendment"* (LXXXI.8). Current certification status, confirmed live: `READY-PROVISIONAL`, 0 findings, 1 vacancy (T1), 9 gaps, 7 open questions (per `00-CMG/tools/cmg-gate.sh` run at time of writing).

---

## 3. UCKP Authority Model

**ROOT_LAW authority** (`engine/uckp/law.py`): 20 articles, 17 invariants, 13 stop conditions, declared as immutable Python data rather than markdown — the module's own docstring states the reasoning explicitly: *"a law whose only home is a document is a law that a document edit can silently repeal. It lives here, as immutable Python values, and every document, JSON declaration, register and certificate that states the law is generated from these values."* This is a genuine, substantive claim to originate law, not merely implement someone else's — which is the crux of the ambiguity in §1.

**Runtime enforcement** (`engine/uckp/validation.py`): executes the 17 invariants as probes against the live registry/state/graph, fail-closed on any unmeasured (blocking) invariant. Its own docstring is explicit about scope discipline: *"An unmeasured invariant is not a satisfied invariant"*; probes read their statement from `ROOT_LAW`, never restate it. This matches CMG's Article LXIII (Runtime Integration) requirements for fail-closed resolution almost clause-for-clause, despite having been written with no reference to CMG.

**Validation authority:** same module; belongs, functionally, to CMG's **T4 — Execution Authority** tier (*"Agents and engines acting within a gate"*, XVI.2) and satisfies Article LXII's Implementation Integration requirements (LXII.2 traceability, LXII.3 no hard-coded content, LXII.6 replaceability without constitutional change) in substance, without ever citing them.

**Registry authority** (`engine/uckp/registry.py`): the admission model — *registered / reused / refused*, never "a clash resolved by picking a winner" — is functionally identical in spirit to CMG's own non-duplication discipline (VIII.1 "Knowledge Once", LIX.4 "A canonical object SHALL NOT be duplicated").

**Identity authority** (`engine/uckp/identity.py`): pure, clock-free URN/UUIDv5 minting, reconciled with the corpus's separate append-only serial ledger (`00-BOOK/DATA/id-ledger.json`) via the standing gate `CAA-INV-04` (see `00-BOOK/DATA/constitutional-authority-alignment.json`) — proof that this exact class of cross-authority reconciliation has already been done once in this repository, successfully, for identity. It is the template this determination recommends following for CMG/UCKP (§6).

**`engine/uckp/constitution.py`** (the projection of `ROOT_LAW` into canonical knowledge objects) is, by contrast, scrupulously deferential — its own docstring: *"These objects are derived, never restated... a projection of the law into object form rather than a rival declaration of it."* This is the one UCKP module that explicitly rules out being a competing source of truth, consistent with CMG's Article LX (Generator Integration: *"A generator SHALL NOT be a source of constitutional truth"*).

**Net characterization:** every UCKP module *except* `law.py`'s `SUPREMACY_CLAUSE` already behaves as a disciplined, CMG-compatible Execution/Implementation-tier authority. The `SUPREMACY_CLAUSE` is the one place UCKP's own text reaches further than its demonstrated behavior.

---

## 4. Relationship Analysis

### OPTION A — CMG superior; CMG recognizes UCKP as executable constitutional authority
**Against:** contradicted directly by CMG's own text. LXXXI.2 states CMG *"holds no substantive authority"* and LXXXI.8 voids any CMG clause that "would decide a substantive matter." CMG cannot be *superior* to UCKP's substantive law-declaring function (`ROOT_LAW`) — only to UCKP's *recognition status* (whether it appears in the registry at all). Superiority over substance is exactly the thing CMG disclaims holding over any domain constitution.

### OPTION B — UCKP superior; CMG becomes documentation classification only
**Against:** this would require accepting UCKP's `SUPREMACY_CLAUSE` at its broadest literal reading — a self-declared, unconditional claim with no external conferral. CMG's own principle **CMG-P-16** ("Non-self-elevation: No instrument is the sole source of its own superiority") and Article XVII.8 ("Resolution SHALL NEVER be resolved by the instrument seeking authority... An instrument SHALL NOT determine its own jurisdiction in a contested case") were written precisely to prevent this pattern — and CMG applies that discipline to *itself* (LXXXI.6). Accepting Option B would mean the corpus applies non-self-elevation to every instrument except the one that happens to be executable code, which has no principled basis in the evidence gathered.

### OPTION C — Separate but linked authorities: CMG governs constitutional recognition and classification; UCKP governs executable constitutional enforcement
**For:** this is the only option consistent with everything gathered in §§2–3 without requiring either instrument to be rewritten:
- CMG's own lattice already reserves a tier for exactly this role — **T4, "engines acting within a gate"** — and Articles LXII/LXIII already state the meta-requirements such a layer must meet, which UCKP's validation/registry/state/constitution modules already meet in substance.
- UCKP's disciplined modules (everything but the `SUPREMACY_CLAUSE`) are already living proof this relationship works in practice — `identity.py`'s reconciliation with the corpus ledger via `CAA-INV-04` is a running example of "separate but linked."
- CMG remains the sole recognizer (T1M); UCKP remains the sole executor of the canonical-object-identity domain specifically — neither needs to become superior to the other, because they answer different questions ("is this recognized as constitutional" vs. "does this object satisfy its constitutional invariants right now").
- The one open item Option C does **not** resolve automatically is the `SUPREMACY_CLAUSE`'s literal scope — that requires a follow-on action (§6), not a structural choice between A/B/C.

**Determination: OPTION C**, on repository evidence.

---

## 5. Recommended Canonical Model

**C — Separate but linked authorities.**

```
        Constitutional Recognition Layer  (CMG, Tier T1M)
        — ranks, recognizes, records vacancies —
                        |
                        | (recognition, not command; LXXXII.7:
                        |  "no entry confers, alters, limits, or
                        |  conditions the authority of the named owner")
                        |
        Executable Constitutional Enforcement Layer  (UCKP, functionally Tier T4)
        — mints identity, registers objects, validates invariants,
          projects law into canonical objects, records state —
```

Both report to the same underlying fact — Repository Truth — neither derives authority from the other, and disagreements about *recognition* (does UCKP appear correctly in the registry) are CMG's to resolve, while disagreements about *whether an object satisfies the law* (do the 17 invariants hold) are UCKP's to resolve. This mirrors the already-working Identity precedent (`CAA-INV-04`) almost exactly.

---

## 6. Required Future Impact

Where future work should belong, given Option C:

- **Universal Evolution Law** (the substantive rule that anything existing/emerging/evolving must become discoverable, identified, owned, related, evidenced, validated, certified): this is **already substantially satisfied** by the existing `ROOT_LAW`. `GOVERNED_CATEGORIES` in `engine/uckp/law.py` is explicitly declared an **open set**, extensible "by registration, never by editing this module" (per the module's own docstring, referencing Article 17), and already includes non-software categories (`planetary-infrastructure` is already present alongside `repository`, `schema`, `programming-language`, etc.) — evidence UCKP's object model was already built with an eye toward being domain-agnostic. New object families the Universal Evolution Foundation cares about ("Intelligence Objects", "Evolution Objects", etc., per the original mission brief) most likely belong as **new entries in `GOVERNED_CATEGORIES`**, extending the existing law, rather than as new supreme law text in a new document. This is a strong instance of "extend before create."
- Anything that is genuinely **new substantive law** beyond what category-registration can express belongs at **T1 or T3** in CMG's own lattice — not at T1M (CMG has no substantive authority to hold it) and not unilaterally inside `law.py` either without first resolving the `SUPREMACY_CLAUSE` ambiguity, since T1 is formally vacant and CMG's own Article XVII.4 forbids silently promoting a lower instrument into a vacant tier.
- **Universal Context Expansion**: has a located, mature owner already — `engine/context/` (UCXI-000001) — extend there, not in a new constitution.
- **Universal Intelligence Universe / Universal Capability Expansion**: no located owner was found in Phase 0 discovery (`UNIVERSAL-EVOLUTION-FOUNDATION-GAP-ANALYSIS.md`, Section D). Per CMG's own gap procedure (Article LXXVIII) and this mission's own rules, these remain **open questions to record**, not capabilities to build yet — building either now would mean legislating before the CMG/UCKP recognition gap (§1) is closed, risking a third parallel authority.

---

## 7. Governance Rules

Before any new constitutional capability is added under the Universal Evolution Foundation mission, it must have, consistent with both CMG's Article XVIII (Authority Delegation) and this mission's own constitutional principle:

1. **Identity** — minted through the existing, single identity authority (`engine/uckp/identity.py` reconciled with `00-BOOK/DATA/id-ledger.json` per `CAA-INV-04`). No second minting mechanism.
2. **Owner** — a located, named owner recorded per CMG's delegation-record shape (LXXXII.2 columns: concern, owner, basis, disposition, revocation condition). "Unowned" is not a valid end state (CMG-INV-03).
3. **Authority** — explicit tier placement in CMG's lattice (Article XVI) if it is a recognition question, or explicit category registration in `GOVERNED_CATEGORIES` (Article 17) if it is an object-modeling question. Not both by default, and not neither.
4. **Relationships** — recorded in the existing relationship graph (`engine/uckp/graph.py` + UGA population), never a new graph.
5. **Dependencies** — declared and resolvable to a located artifact; a dangling dependency is void (XVIII.6 analog).
6. **Evidence** — recorded under the existing Evidence Universe (`00-BOOK/DATA/evidence-universe.json`), reproducible from repository state alone (CMG's VII.7 evidence-bound principle).
7. **Validation** — proved, not asserted, by an executable probe bound to an invariant id (per `engine/uckp/validation.py`'s own discipline: *"An unmeasured invariant is not a satisfied invariant"*).
8. **Certification** — recorded honestly, including PROVISIONAL status where standing has not been conferred by a competent authority (CMG's VIII.5 "honesty over completeness"; LXXXI.6 non-self-elevation). A capability that cannot yet prove Tier T1 backing should say so, not omit the question.

Any new capability failing any of the eight SHALL be recorded as an open question (per CMG Article LVII) rather than built provisionally as if resolved.

---

## Closing note — governance checks run against this document

- `python3 00-BOOK/tools/ukb.py enforce --pre` — passed (this file reported as "awaiting VCS binding", the expected pre-`git add` state; 0 unregistered, 0 unclassified, 0 drift).
- `bash 00-CMG/tools/cmg-gate.sh` — passed, `READY-PROVISIONAL`, 0 findings (this document does not modify `00-CMG/` and makes no claim of ratified authority for itself).

No CMG file, no UCKP file, and no registry was modified in the production of this determination, per the stop condition.
