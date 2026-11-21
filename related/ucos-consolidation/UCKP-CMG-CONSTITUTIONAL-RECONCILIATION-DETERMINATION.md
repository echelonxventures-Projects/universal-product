# UCKP-CMG CONSTITUTIONAL RECONCILIATION DETERMINATION

> **Mission:** UCOS Ω∞ Universal Evolution Foundation, Phase 0.6 — Constitutional Reconciliation
> **Mode:** READ-ONLY. No CMG modification, no UCKP modification, no new constitution, no new registry, no new engine.
> **Date:** 2026-08-13
> **Precondition:** Builds directly on `UCKP-CMG-AUTHORITY-ALIGNMENT-DETERMINATION.md` (Phase 0.5), which selected Option C (separate but linked authorities) and identified the `SUPREMACY_CLAUSE` scope as the open question. This document goes one level deeper: it locates the *exact mechanism* that would have to recognize CMG for Option C to be true in practice, and shows precisely, mechanically, why it currently doesn't.

---

## 1. Current Conflict

The conflict is not philosophical. It is a **mechanical blind spot in an already-working mechanism**, and it runs in both directions.

**The mechanism:** `engine/uckp/alignment.py` (`UCOS-CAA-001`) exists specifically to prevent exactly the failure this reconciliation is worried about. Its own docstring records the original incident: *"seven version-controlled instruments each declared itself 'AUTHORED REPOSITORY TRUTH … upstream of every engine that reads it', and not one of them named the authority it was upstream under. Seven instruments each standing at the top of its own chain is seven roots, and Article 1 admits exactly one."* It fixed that by requiring every authority-claiming instrument to be bound in `00-BOOK/DATA/constitutional-authority-alignment.json` under one of seven roles (`SUPREME` — exactly one, `UCKP-LAW-0001` — plus six non-authoritative roles: `PROJECTION`, `PERSISTENCE`, `EXECUTION`, `EVIDENCE`, `OBSERVATION`, `DERIVED`), each enforced by `CAA-INV-01`..`07` and measured by `00-MASTER/UCOS-UGA-001/uga_engine.py`'s `scan_authority_claims()`, inside the `verify.sh` gate chain. Eight instruments are currently bound this way (`UOS-UGA-001`, `UCOS-EVIDENCE-UNIVERSE-001`, `UCOS-OBSERVATION-UNIVERSE-001`, `UCOS-GENERATED-ARTIFACT-REGISTRY-001`, `UCOS-EXCLUSION-REGISTER-001`, `UCOS-MUTATION-GOVERNANCE-BOUNDARY-001`, `UAKOS-CLOSURE-008-VALIDATION-RECORD`, and `UCOS-CAA-001` itself, bound to its own `DERIVED` role).

**Why CMG is not among them — verified mechanically, not inferred:**

```python
# 00-MASTER/UCOS-UGA-001/uga_engine.py, scan_authority_claims()
scan = caa["authority_claim_scan"]
suffixes = tuple(scan["path_suffixes"])   # == (".json",)
key = scan["authority_key"]               # == "authority"
for rel in paths:
    if not rel.endswith(suffixes):
        continue                          # <-- CMG-000001.md never enters the loop body
    ...
    value = doc.get(key)                  # top-level JSON key "authority"
```

Two independent, structural reasons, confirmed by direct read:

1. `authority_claim_scan.path_suffixes` in the binding is `[".json"]` only. `00-CMG/CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md` is markdown. The scan's own `if not rel.endswith(suffixes): continue` skips it before any content is ever inspected.
2. Even hypothetically re-pointed at markdown, the scan reads a **top-level JSON key literally named `authority`**. CMG-000001 states its authority as a **markdown table row** (`| AUTHORITY | Supreme over META-CONSTITUTIONAL MATTER ONLY — ... |`), a different data shape entirely.

CMG-000001's own front matter, read directly:

> `AUTHORITY | Supreme over META-CONSTITUTIONAL MATTER ONLY — what a Constitution is, how constitutionality is recognized, and how constitutional authority is allocated across the whole corpus. Confers NO authority over constitutional content and NO authority over constitutional-engineering process.`

Tested against the binding's own three `disclaiming_prefixes` (`NONE` → `DERIVED-TRUTH`; `ENGINEERING-EXECUTION-ONLY` → `ENGINEERING-EXECUTION`; `GOVERNED OWNERSHIP AUTHORITY` → `DELEGATED-ASSIGNMENT`), CMG-000001's authority text **matches none of them** — it does not start with any disclaiming token. Under the scan's own rule (*"An instrument whose `authority` matches no disclaiming prefix MUST appear in `subordinate_instruments` with a declared role and at least one article of derivation. There is no third outcome."*), CMG-000001, if it were ever seen by the scan, would trip the rule and require a role.

**And that is the second, deeper part of the conflict:** none of the six existing non-`SUPREME` roles correctly describes what CMG-000001 actually claims. `DERIVED` — *"an instrument that records or measures the standing of others and asserts nothing of its own"* — is the closest, and is wrong: CMG explicitly does assert something (LXXXI.1: *"This instrument IS supreme over meta-constitutional matter... It IS supreme over nothing else"*), it just asserts it over a bounded, non-overlapping matter-class. `PROJECTION`/`PERSISTENCE`/`EXECUTION`/`EVIDENCE`/`OBSERVATION` do not fit at all. And `SUPREME` cannot be used — `CAA-INV-01` fixes it to exactly one instrument, `UCKP-LAW-0001`. **The taxonomy has no slot for "genuinely holds bounded authority, but over a different axis than Article 1 governs."** This is a real gap in the role vocabulary, not a misapplication of an existing one.

This is symmetric with the Phase 0.5 finding (CMG's own Article LXXXII delegation register never enumerates UCKP either, for the parallel reason that its register was built by walking the markdown corpus and was never extended to the newer, code-native `engine/uckp/` layer). Neither framework refused the other. Each has a blind spot shaped exactly like its own scanning mechanism.

---

## 2. Constitutional Interpretation

The two instruments' texts are compatible once read as answering **different questions**, and both frameworks already contain the vocabulary to say so — they have simply never been pointed at each other.

- **UCKP's `SUPREMACY_CLAUSE` (Article 1)** is elaborated by **Article 4, "Non-Authority of Representations"**: *"Repositories, documents, files, schemas, source code, APIs, databases, graphs, interfaces and every future technology are views, projections, execution environments or persistence mechanisms. None holds independent authority."* Article 1's supremacy is a supremacy **over the object model** — what a canonical knowledge object is, and the rule that no representation, storage mechanism, or execution technology of one may claim independent authority over what it represents. It is never elaborated, anywhere in the 20 articles, as a claim to decide *which instruments in the repository count as constitutional* or *how they rank against each other* — that question is never posed inside `ROOT_LAW` at all.
- **CMG's Article LXXXI.1** states the mirror-image scope discipline: *"This instrument IS supreme over meta-constitutional matter... It IS supreme over nothing else."* CMG never claims authority over object identity, persistence, execution, or representation — those words do not appear in its 86 articles in a governing sense; Article LXII.5 explicitly disclaims introducing *"no engine, service, runtime component, or persistent store."*
- The two claims do not overlap. UCKP governs *what an object is and how its representations behave*; CMG governs *which instruments are recognized as constitutional and how they rank*. Neither text answers the other's question, so neither can contradict the other's answer.
- Critically, **both frameworks already have a name for exactly this relationship, independently**:
  - CMG's own **Article XVI.4** declares "orthogonalities" between tiers that have no relative rank and are not resolved by rank (`T1M ⟂ T2`, `T2I ⟂ T2`, `T2I ⟂ T1M`) — precisely the shape of relationship CMG and UCKP have to each other, simply never declared as a fourth instance.
  - UCKP's `UCKP-POLICY-ONE-AUTHORITY` (in `alignment.py`) voids an instrument that *"claims constitutional authority and names no superior"* and is a **competing** root. CMG's claim does not compete — it is scoped to a matter-class Article 1 never addresses. The policy was written to catch rivalry, and there is no rivalry here to catch.

**Interpretation:** CMG-000001 is not a rival to `UCKP-LAW-0001`'s supremacy. It is a second, independently-scoped, bounded-supreme instrument occupying an axis (`recognition of constitutionality`) that `ROOT_LAW` never claims and structurally cannot claim without contradicting its own Article 4 (an instrument that decided "what counts as constitutional" is not itself a representation, execution environment, or persistence mechanism of a UCKO — it is answering a category of question UCKP's object model doesn't model at all). The `CAA-INV-01` "exactly one `SUPREME`" invariant remains true and is not threatened: `UCKP-LAW-0001` remains the one and only supreme authority over the canonical-object axis. CMG needs a *different* role, not `UCKP-LAW-0001`'s role.

---

## 3. Canonical Relationship Model

```
   Axis 1 — Architectural / Canonical-Object Authority           Axis 2 — Meta-Constitutional Recognition Authority
   ────────────────────────────────────────────────────          ──────────────────────────────────────────────────
   UCKP-LAW-0001  (role: SUPREME, exactly one — CAA-INV-01)       CMG-000001  (role: ORTHOGONAL — new, §4 below)
   Governs: what a canonical knowledge object IS; identity;       Governs: what counts as a constitutional instrument;
   persistence/execution/projection non-authority; the             how instruments rank; vacancy tracking; the
   relationship graph model; state immutability.                  Constitutional Precedence Lattice (T0–T5).
                                                                    Explicitly: "no authority over constitutional
                                                                    content" (LXXXI.2) — cannot decide the object axis.
            │                                                                  │
            ▼                                                                  ▼
   engine/uckp/{identity,registry,state,graph,validation}.py       00-CMG/CMG-REGISTRY.json, cmg_validate.py
   — the T4 "engines acting within a gate" that enforce Axis 1     — recognizes/ranks instruments; records vacancies,
                                                                      gaps, open questions on Axis 2

   Neither axis derives from, is superior to, or is subordinate to the other.
   Where a question touches both (e.g. "should a newly-discovered instrument get
   an identity AND get ranked"), CMG's own Article XVII.5 (Orthogonality
   Resolution) already provides the procedure: decompose the question and route
   each component to its axis owner. No new resolution mechanism is required —
   only naming UCKP as the located owner of the object-identity component,
   which XVII.5 already presupposes exists somewhere.
```

This is the same model Phase 0.5 selected as Option C, now expressed as the precise mechanical relationship the two existing frameworks (`alignment.py`'s role taxonomy, and CMG's own precedence lattice) would need to state, rather than as an abstract structural diagram.

---

## 4. Required Minimal Changes

**None of these are executed in this pass.** All are recommendations, ranked by how minimal they are, per the instruction to prefer semantic clarification over structural change.

1. **(Semantic — smallest change) Add one `AuthorityRole` to `engine/uckp/alignment.py`'s `AUTHORITY_ROLES` tuple:** `role_id="ORTHOGONAL"`, definition along the lines of *"an instrument holding genuine, bounded authority over a matter-class Article 1 does not govern; may hold authority within its own declared axis and none other; does not compete with SUPREME because its axis is disjoint from the canonical-object axis"*, `article="UCKP-ART-01"` (paired with a reference to `UCKP-ART-04`), `may_hold_authority=True` (unlike the six existing non-`SUPREME` roles, all `False` — this is the one substantive addition, because CMG genuinely does hold authority, just not over this axis), `cardinality="FEW"` (deliberately not `MANY` — an orthogonal-axis claim should be individually justified each time, not routinely available the way `PROJECTION`/`EVIDENCE` are). This adds no new authority: it gives the existing bookkeeping a name for authority CMG already claims for itself in its own text.
2. **(Semantic) Add a new `AlignmentRule`** (next free id, e.g. `CAA-INV-08`) requiring every `ORTHOGONAL`-role instrument to declare the specific matter-class its authority is scoped to, and requiring that matter-class to have **zero overlap** with `GOVERNED_CATEGORIES` or with any article's `binds` tuple in `ROOT_LAW` — a checkable non-overlap proof, not an assertion. This is the safeguard against the new role becoming an escape hatch for a future instrument to dodge real subordination.
3. **(Data, not code) Add one entry to `00-BOOK/DATA/constitutional-authority-alignment.json`'s `subordinate_instruments`** for `CMG-000001`, role `ORTHOGONAL`, `derives_under: ["UCKP-ART-01", "UCKP-ART-04"]`, and a declared scope (e.g. `"scoped_to": "meta-constitutional recognition — CMG-000001 Article XII–XVII"`), quoting CMG's own `AUTHORITY` line as the basis field, in the same style the existing 8 entries already use. (The list's name, "subordinate," is a slight misnomer once a peer axis exists in it — noted, not treated as blocking; the `role` value carries the operative meaning, and renaming the field would be the kind of structural change this phase is told to avoid.)
4. **(Symmetric, on the CMG side — the paired half of the same fix, restated from Phase 0.5) Add one row to CMG-000001 Article LXXXII** (`CMG-DLG-50` or next free id): concern = "canonical-object identity, registry, validation, and root constitutional law," owner = `engine/uckp/` (`UCKP-LAW-0001`), disposition `REUSE`, basis = `UCKP-ART-01, -02, -05, -08`. This closes CMG's own admitted non-exhaustive register (LXXXII.6) from its side, using CMG's existing amendment mechanism (Article XLIII) — not a new authority, not a new register.
5. **(Lower priority, explicitly flagged as more invasive — not recommended for this reconciliation) Extending `authority_claim_scan.path_suffixes` to also read markdown front-matter `AUTHORITY` fields.** This would make the scan generally aware of markdown constitutions going forward, rather than requiring a one-off manual fix like (3) for each. It touches the scanning mechanism itself (`uga_engine.py`), which is a real structural change, and is noted here as a longer-term option rather than part of the minimal reconciliation this phase asks for.

Items 1–4 together are the minimal, symmetric fix: one new role definition, one new safeguard rule, one data row on each side. No engine is created (the existing `uga_engine.py` gate and `cmg_validate.py` already run these checks inside `verify.sh`). No registry is created (both files being edited already exist and already serve exactly this purpose). No new authority is created (both additions record authority each instrument already claims for itself in ratified/provisional text — nothing is granted that wasn't already asserted).

---

## 5. Authority Boundaries

| | UCKP-LAW-0001 | CMG-000001 |
|---|---|---|
| **Governs** | What a canonical knowledge object is; identity; the relationship graph model; non-authority of representations, persistence, and execution; state immutability | What counts as a constitutional instrument; how instruments rank; recognition of constitutionality across the corpus |
| **Does not govern** | Which instruments are recognized as constitutional, or how they rank against each other | The object model; identity minting; persistence, execution, or representation of any object |
| **Role under reconciliation** | `SUPREME`, exactly one (`CAA-INV-01`, unchanged) | `ORTHOGONAL` (new, §4.1) — bounded-supreme over its own disjoint axis |
| **Self-declared limitation** | Article 4: representations/environments/persistence "hold no independent authority" — a claim about the object axis only | LXXXI.2: "holds no substantive authority," LXXXI.8: any clause deciding a substantive matter "IS void" |
| **Enforced by** | `engine/uckp/validation.py`, `uga_engine.py` gate (`verify.sh`) | `00-CMG/tools/cmg_validate.py`, `cmg-gate.sh` (`verify.sh`) |
| **Currently** | `ACTIVE`, code-enforced | `READY-PROVISIONAL`, Tier T1 (substantive constitutional authority — a third, still-vacant axis neither UCKP nor CMG occupies) remains open, unaffected by this reconciliation |

Neither instrument's boundary changes as a result of this reconciliation. What changes is that both boundaries become **visible to the other's bookkeeping**, which is the entire content of "reconciliation without duplicate authority, competing supremacy, ambiguous ownership, or constitutional conflict."

---

## 6. Validation Requirements

For the reconciliation in §4 to be real rather than asserted (consistent with both frameworks' own "measured, not asserted" discipline — CMG's VII.7 "evidence-bound" principle and UCKP's `validation.py` "an unmeasured invariant is not a satisfied invariant"):

1. **`engine.uckp.alignment.verify_binding()`**, once `CMG-000001` is added to `subordinate_instruments`, must resolve it to a located, readable file and check its declared `AUTHORITY` text against what `CMG-000001` actually states — the same drift check `_role_findings`/`_rule_findings` already perform for the other 8 bound instruments. A stale or drifted quote should fail the gate, not pass silently.
2. **The new `CAA-INV-08` non-overlap rule (§4.2)** must be measured by `uga_engine.py`'s existing `scan_authority_claims`/`alignment_state` machinery — no new engine, an extension of the function already reading `caa["subordinate_instruments"]`.
3. **CMG's `cmg_validate.py`**, once the symmetric `CMG-DLG-50` row (§4.4) is added, already requires (per LXXXII.4) that *"Every delegation... SHALL be verified to resolve to a located owner"* — this is an existing check, not a new one; it simply needs to successfully resolve `engine/uckp/` once the row exists.
4. **Both `cmg-gate.sh` and `uga_engine.py gate` already run inside `verify.sh` on every commit.** Reconciliation adds rows to data these gates already read; it adds no new gate, no new stage, and no new script.
5. **Before either data change is committed**, `python3 00-BOOK/tools/ukb.py enforce --pre` and `validate` should be re-run (as was done for the two prior determinations in this mission) to confirm no drift or unregistered-artifact regression is introduced by the edit itself.

No validation requirement above needs new tooling. Every one of them is an existing check being pointed at one more row of existing data.

---

## Closing note

No file under `00-CMG/` or `engine/uckp/` was modified in the production of this determination. `00-BOOK/DATA/constitutional-authority-alignment.json` was read, not written. Per the stop condition: waiting for approval before any of §4's changes are made.
