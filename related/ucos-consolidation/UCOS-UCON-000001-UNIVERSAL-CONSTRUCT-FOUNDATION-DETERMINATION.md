# UCOS-UCON-000001 — UNIVERSAL CONSTRUCT FOUNDATION DETERMINATION

**Artifact:** `UCON-000001`
**Declaration:** `00-MASTER/UCON-000001/ucon-declaration.json` (digest `192c63afe7073691…`)
**Implementation:** `engine/construct/` (14 modules)
**Verification:** `engine/tests/unit/test_construct_foundation.py` (204 tests) · `./verify.sh` Stage 6i · `.github/workflows/ucon-gate.yml`
**Standing:** CERTIFIED-PROVISIONAL
**AUTHORITY = NONE (DERIVED TRUTH).** This determination legislates nothing, ratifies nothing, and certifies nothing. It records what was built and what was measured.

---

## 1. EXECUTIVE SUMMARY

### 1.1 What was actually wrong

The repository already declared, in many documents, that any presented construct could be represented, governed, traced and researched without constitutional redesign. That claim was true of the **declarations** and false of the **runtime**, and nothing measured the gap.

Three measured facts, from before this work:

| Concern | What the runtime actually did | Where |
|---|---|---|
| An unknown construct | `MetaTypeUnknownError` was raised and **no record was left** | `engine/kernel/errors.py:36`, `engine/kernel/governance.py:110-121` |
| A contradiction | a recomputed three-string finding with **no identity and no lifecycle** | `engine/knowledge/intelligence.py:84-93` (`ConflictFinding`) |
| A non-closed measurement | had identity but, by its own docstring, **deliberately no status** | `engine/uicm/gap.py:77-130` (`Gap`) |

The first is the load-bearing one. Because a refused construct left no record, **"we governed a refusal" and "we never saw it" were the same observable state.** Nothing downstream could distinguish a governed refusal from a silent drop, and neither produced a red build.

### 1.2 What was built

`UCON-000001` — the Universal Construct Foundation. One store, eleven parts, sixteen computed laws, one fail-closed gate.

The four decisions that carry it, each enforced structurally rather than by convention:

1. **The registry has no refusal path.** Read the public surface of `engine/construct/registry.py`: there is no `reject()`, no `refuse()`, and no branch in `present()` that returns without recording. Disposition decides what a construct may *do*; it never decides whether the construct *exists in the record*. A REJECT is a record naming the rule and rationale that produced it. Law UCON-L-05 compares the presentation count to the population, so a registry that could lose a construct fails its own arithmetic.

2. **The catch-all is ESCALATE, never REJECT.** A REJECT catch-all would discard precisely the constructs the rule set failed to anticipate — the unforeseen, the future-originated, the currently unrepresentable — *while reporting a clean, total, fully-covered run*. Law UCON-L-03 measures both that the catch-all assigns the declared disposition and, structurally, that it forecloses nothing.

3. **Admission and reality cannot see each other.** `reality.py` does not import `disposition.py`; `disposition.py` does not import `reality.py`; law UCON-L-11 parses both to confirm neither ever will. They meet only as a **conjunction**: an act is permitted iff the active disposition permits it AND the active reality state permits it. That single line is the operational form of *admission does not imply truth* — ADMIT permits `certify`, HYPOTHETICAL does not, and no amount of admission changes that.

4. **Nine kinds of self-extension travel one mechanism.** An ontology, a governance rule, a verifier, a location axis, a temporal system and an identity namespace are all *constructs*. There is one extension mechanism to verify rather than nine, and law UCON-L-09 performs all nine admissions in memory on every run.

### 1.3 Measured result

| Measurement | Value |
|---|---|
| Laws holding | **16 / 16** (`status: OPEN`) |
| Tests | **204 / 204** pass, `engine.construct` coverage **92%** (floor 90) |
| `./verify.sh --full` | **15 / 16** stages pass, including the new Stage 6i |
| Combined repository coverage | **97%** (82,933 statements) |
| Closure mechanisms inventoried | **1,451** across **493** modules |
| Constructs bootstrapped through the ordinary path | 32 seed kinds, `presented == held`, chain intact |
| Disposition × reality pairs representable | **64 / 64** |
| Gate runtime | ~5.9 s, read-only, clock-free |

### 1.4 What is NOT claimed

The declaration's `principle.refused_claims` names each refused claim explicitly and this document does not restate them — one list, one owner. Law UCON-L-13 scans this capability's own source for the vocabulary such a guarantee would require and refuses any undeclared occurrence, so the absence of the claim is a **ratchet, not a promise**.

Stated positively, and this is the whole of what is claimed: **any presented construct can be represented, governed, traced, researched and assigned exactly one traceable disposition, and adding a category the foundation has never seen is one governed registration rather than a code change.** That is measurable, and it is measured.

---

## 2. ARCHITECTURE DESIGN

### 2.1 Eleven parts, in dependency order

```
                        ┌──────────────────────────────────────────┐
                        │ 00-MASTER/UCON-000001/                   │
                        │   ucon-declaration.json                  │  ALL vocabulary
                        │   (kinds, dispositions, reality states,  │  lives here.
                        │    rules, operators, selectors,          │  No kind name,
                        │    admissions, closure forms, laws)      │  no disposition
                        └───────────────────┬──────────────────────┘  name, no rule
                                            │                          in any engine.
  Part 02 declaration.py  ◄─────────────────┘
      rehydrate · refuse when unusable · two-way bind FIVE registries
                    │
  Part 01 model.py  ◄┘   Presentation │ DispositionRecord │ RealityAssessment │ Construct
                         (no verdict)   (no truth)          (no admission)      (the three joined)
                    │
      ┌─────────────┼──────────────┐
      ▼             ▼              ▼
  Part 03       Part 04        (cannot see each other — UCON-L-11)
  reality.py    disposition.py
  assess        12 operators
  transition    total function
  permits ──────┐ catch-all = ESCALATE
                │
                ▼
        Part 05 registry.py ── ONE store. No refusal path.
                │              derived-open · hash-chained · append-only
      ┌─────────┼─────────┬──────────────┐
      ▼         ▼         ▼              ▼
  Part 06   Part 07   Part 08        Part 09
  views.py  extension audit.py       contract.py
  4 projec- 9 points  1,451 closures 16 laws
  tions by  1 mecha-  measure-only   computed, several PERFORMED
  facet     nism      ratchet ×2
                                     │
                          ┌──────────┴──────────┐
                          ▼                     ▼
                    Part 10 evidence.py   Part 11 gate.py
                    the only writer       0 OPEN / 1 CLOSED / 2 FAULT
                    (untracked home)      + cli.py (6 subcommands)
```

### 2.2 The four-type split, and why it is the design

`engine/construct/model.py` deliberately refuses to put admission and truth in one object:

```
Presentation       what was presented.        No admitted flag. No valid flag. No truth field.
DispositionRecord  what governance decided.   rule_id + rationale + inputs_digest. Supersedable.
RealityAssessment  what the evidence supports. No admission. No permission.
Construct          the three joined, with full history.
```

A single type carrying `kind, payload, admitted, verified` would make *admission implies truth* **structurally expressible**, and then no law could refuse it. Because a presentation carries no disposition and an assessment carries no admission, the sentence "this construct is admitted, therefore it is true" **cannot be written in this model at all**. That is stronger than a rule forbidding it.

### 2.3 What it binds to rather than owns

| Concern | Owner | How UCON binds |
|---|---|---|
| Open-by-registration classification | UMK-000001 (`engine/kernel/`) | mirrors the `metatype_exists` invariant; derives openness from the record, consults no table |
| Existence / epistemic vocabularies | UCOS-CEU-001 (`engine/ceu/catalog.py`) | every reality state **names** the CEU row it derives from; UCON-L-14 *imports* `SEED_POPULATIONS` and refuses a binding CEU does not carry |
| Identity | UCKP-ART-05 (`engine/uckp/identity.py`) via `engine/kernel/identity.py::mint` | mints no scheme of its own; holds no counter |
| Canonical digest | UCKP-LAW-0001 §Art-13 (`engine/uckp/canonical.py`) | forwards; never reimplements (an AST probe in `engine/uckp/validation.py` detects duplication) |
| Context / location axes | UCXI-000001 | a `location-axis` construct is a *governed representation referred to the owner*, not a resolvable axis |
| Temporal coordinates | CMG-000002 | same: `temporal-system` is representation, not conversion |
| Birth | UOBC-000001 | gap **UCON-G-02** disclosed: `ucos.construct` is not a declared namespace, so no birth record is claimed |

**This is not a second kernel, registry or existence vocabulary.** The declaration's `$not_a_second_authority` states it and UCON-L-14 enforces the vocabulary half of it.

---

## 3. RUNTIME DESIGN

### 3.1 The one path a construct travels

```
Presentation
    │
    ├─► reality.assess(declaration, presentation)          ── the claimed state, or the DECLARED
    │        │                                                initial state when none was claimed.
    │        │                                                A claim above its floor is RECORDED
    │        │                                                with floor_met=false, never downgraded.
    │        ▼
    │   RealityAssessment
    │        │
    ├─► disposition.dispose(declaration, presentation,      ── ordered, first-match-wins.
    │        context=registry.context(resolved_status))        The LAST rule is the catch-all,
    │        │                                                 checked at LOAD, so a rule set
    │        ▼                                                 that could miss cannot load.
    │   DispositionRecord (rule_id, rationale, inputs_digest)
    │
    └─► Construct(presentation, dispositions, assessments, kind_registered, facet_violations)
             │
             ├─► stored — ALWAYS. There is no branch that declines.
             └─► JournalEntry appended, hash-chained from GENESIS = "0"*64
```

Re-presenting an identity **supersedes** its disposition and assessment and keeps both histories: presentation is idempotent in identity and cumulative in history.

### 3.2 The disposition context — five facts, deliberately tiny

`registered_kinds`, `registered_identities`, `contradicted`, `research_states`, `reality_status`. A context that could reach the whole registry would let a rule depend on anything, and "why did this construct get this disposition" would be answerable only by re-running the engine against the exact same world.

It is **rebuilt per presentation**, not cached: a contradiction registered a moment ago must affect the next presentation. A cached context is how a governance decision comes to be made against a world that no longer exists.

Note the permitted direction: a declared rule **may** consult reality to decide a disposition, because operational behaviour is *required* to depend on status. What is forbidden is the reverse — deriving reality from admission — and UCON-L-11 measures exactly that asymmetry.

### 3.3 Openness is derived, never tabulated

`ConstructRegistry.registered_kinds` scans the constructs of the reflective kind and consults no list. The declared seed kinds are **not** a privileged table: `bootstrap()` presents each one through the same `present()` an unknown category travels, with the declaration as its evidence. There is therefore **no code path that admits a founding kind and no separate path for any other** — which is what makes "a future category is one registration" mechanically true rather than documented.

Measured: registering 11 invented categories and their instances leaves the package's own source fingerprint byte-identical (UCON-L-08).

### 3.4 Observed behaviour (reproducible)

```
$ ucos-construct dispose --kind hyper-causal-lattice --key HCL-1
  → TRANSFORM  (UCON-DR-04: the classifying kind is not registered)
    …recorded, not dropped, not refused

$ (register the kind — one governed act, no code change)
$ ucos-construct dispose --kind hyper-causal-lattice --key HCL-1 --evidence obs-1 --reality HYPOTHETICAL
  → ADMIT      (UCON-DR-10: evidence is offered and no prior rule objected)
    permitted_acts: [derive_from, reference]
    refusals:      certify → "reality state HYPOTHETICAL does not permit it"
```

Admitted, and still not certifiable. That is the requirement, executing.

---

## 4. DATA MODEL

### 4.1 Entities (`engine/construct/model.py`, all `@dataclass(frozen=True, slots=True)`)

| Type | Fields | Notes |
|---|---|---|
| `Evidence` | `source`, `statement`, `independent`, `evidence_id` | `independent` separates "observed twice by one instrument" from "reproduced" |
| `Lineage` | `derived_from`, `supersedes`, `presented_by` | never invented; every entry supplied or derived-and-recorded |
| `Presentation` | `kind`, `natural_key`, `title`, `payload`, `evidence`, `dependencies`, `lineage`, `reality_status`, `escalation_requested`, `declared_undecidable`, `identity` | **no verdict field of any kind** |
| `DispositionRecord` | `identity`, `disposition`, `rule_id`, `rationale`, `sequence`, `inputs_digest`, `active`, `superseded_by`, `record_id` | `rule_id`+`rationale` read from the matched rule, so "why" needs no replay |
| `RealityAssessment` | `identity`, `status`, `evidence_count`, `independent_sources`, `assessed_from`, `sequence`, `floor_met`, `active`, `superseded_by`, `record_id` | carries no admission and no permission |
| `Construct` | `presentation`, `dispositions`, `assessments`, `kind_registered`, `facet_violations` | `__post_init__` refuses 0 or ≠1 active disposition — UCON-L-01 is a *type* invariant |
| `JournalEntry` | `sequence`, `identity`, `event`, `disposition`, `reality_status`, `content_digest`, `prev_hash`, `entry_hash` | `prev_hash` is inside the hashed body — that is what chains it |

### 4.2 Identity — total, derived, and not a new grammar

```python
construct_id(kind, natural_key) = mint(kind, "ucos.construct", content_hash([KEY_DOMAIN, natural_key]))
                                  └─ engine.kernel.identity.mint → "UMK-<SLUG>-<12 hex>"
```

The natural key is folded through the canonical digest **before** minting, because `normalize_segment` refuses whitespace. That makes identity **total**: a key containing whitespace, punctuation or a non-Latin script yields an identifier rather than a refusal. Verified over 7 hostile key shapes.

Why totality matters: a construct that could not be named is one that could not be recorded, and an unrecordable construct is indistinguishable from one that was silently ignored.

### 4.3 Declared vocabularies (all DATA; counts measured)

| Vocabulary | Count | Openness |
|---|---|---|
Construct kinds | 32 seed | open by registration (reflective root `construct-kind` classifies itself)
Facets | 8 | `none, kind, unknown, contradiction, research, discovery, verifier, extension`
Dispositions | 8 | open by registration (UCON-EP-02); none terminal
Reality states | 8 | open by registration (UCON-EP-03); none terminal
Operational acts | 6 | `reference, depend_on, derive_from, certify, publish, execute`
Disposition rules | 11 | ordered, catch-all last
Operators | 12 | code; two-way bound to rules
Unknown classes | 14 | includes `unknown-unclassified` — the second-order unknown has a declared home
Contradiction classes | 7 | + 6 resolution states, each flagged `contradicting` true/false
Research states | 9 | includes `refuted` (a finding, not a failure) and `undecidable`
Discovery sources | 6 | + 5 priorities, 5 impacts
Extension points | 9 | one mechanism; 5 admissions
Closure forms | 5 | + 4 risk tiers
Laws | 16 | two-way bound to `LAW_CHECKS`

### 4.4 The reality-state model

| State | evidence floor | independent floor | permits | CEU binding |
|---|---|---|---|---|
VERIFIED | 2 | 2 | all six | `existence-state/actual`
REPRODUCED | 2 | 2 | all six | `existence-state/actual`
OBSERVED | 1 | 1 | reference, depend_on, derive_from, publish | `existence-state/actual`
THEORETICAL | 0 | 0 | reference, depend_on, derive_from | `existence-state/predicted`
HYPOTHETICAL | 0 | 0 | reference, derive_from | `existence-state/hypothetical`
CONTRADICTED | 1 | 2 | reference | `epistemic-state/contradicted`
UNKNOWN | 0 | 0 | reference | `epistemic-state/unknown`
UNDECIDABLE | 0 | 0 | reference, derive_from | **none** — gap UCON-G-01 disclosed

**No state is terminal, including the strongest.** VERIFIED names CONTRADICTED among its successors, because falsification must stay reachable from every state. UCON-L-10 measures this precisely: *every state that permits `certify` must name a successor permitting strictly fewer acts.* A framework in which VERIFIED were terminal would be asserting that some verification can never be overturned.

**Gap UCON-G-01 (disclosed, not papered over).** UCOS-CEU-001 declares no epistemic row for "no decision procedure exists". Its nearest row, `impossible`, means *excluded by a stated constraint* — a different claim. So UNDECIDABLE binds to nothing and discloses why, referred to UCOS-CEU-001. Binding it to `impossible` would have been silently wrong.

---

## 5. API MODEL

### 5.1 Python surface

```python
# store
registry = ConstructRegistry(declaration)            # bootstraps the declared seed kinds
construct = registry.present(presentation)           # ALWAYS records. No refusal path.
registry.present_all(presentations)
registry.redispose(identity, disposition=…, rule_id=…, rationale=…)   # declared successors only
registry.reassess(identity, to_status, evidence=…)                     # declared transitions only
registry.adopt(extended_declaration)                 # refuses ANY narrowing
registry.get / has / all / of_kind / of_facet / with_disposition / with_reality
registry.registered_kinds / contradicted() / research_states() / facet_violations()
registry.undisposed() / chain_is_intact() / verify() / summary() / digest() / rendered()

# reality (cannot import disposition)
reality.assess / transition / reachable_from / permitted_acts / permits / refusal

# disposition (cannot import reality)
disposition.dispose / select_rule / matches / evaluate_clause / trace / available_operators

# the four registries — projections over ONE store
views.unknowns / contradictions / standing_contradictions / research_objects / discovery_objects
views.register_unknown / register_contradiction / register_research / register_discovery
views.promote_to_research(registry, identity)    # ANY construct → research object. Idempotent.
views.opportunities(registry)                    # read; mints nothing
views.discover(registry)                         # mints; converges to a fixed point

# self-extension — nine subjects, one mechanism
extension.register_kind / register_disposition / register_reality_state
extension.register_extension / register_verifier
extension.extended_with_kind / _disposition / _reality_state       # NON-MUTATING
extension.exercise(registry, point_id)                             # performs a declared admission

# audit — measures, migrates nothing
audit.scan / inventory / validate / verify / rendered / digest / unscannable

# laws
contract.measure(laws=…) / load_contract / available_checks
```

### 5.2 Command surface

```
ucos-construct laws      [--law ID] [--json]      measure every declared law
ucos-construct audit     [--json] [--out PATH]    the closure inventory
ucos-construct registry                          population, verification, extension points
ucos-construct dispose   --kind K --key N […]     present one construct + the FULL rule trace
ucos-construct discover                           recursive discovery + the fixed point
ucos-construct permits   --disposition D --reality R    what is permitted, and why not

python -m engine.construct.gate [--gate] [--quiet] [--json] [--inventory] [--law ID] [--evidence]
    exit 0 OPEN · 1 CLOSED · 2 FAULT
```

`dispose` and `permits` exist because the two questions this capability most needs to answer out loud are *why does this construct have this disposition* and *why may it not do that*. Both are answered from the declaration, so the answer cannot drift from the behaviour.

---

## 6. REGISTRY ARCHITECTURE

### 6.1 Four registries, one store

An unknown registry with its own table, a contradiction registry with its own table and a research registry with a third would be three more places a governed object can live, three more coverage questions, and three more owners for one concern — the defect the repository's own `DEC-MCOS-00R` precedent refuses.

So each of the four is a **projection** selected by the facet its kind declares:

| Registry | Selection | Registration |
|---|---|---|
Unknown | kinds carrying facet `unknown` | `register_unknown` — class checked against 14 declared, incl. `unknown-unclassified` |
Contradiction | facet `contradiction` | `register_contradiction` — neither side deleted, neither preferred |
Research | facet `research` | `register_research` / `promote_to_research` |
Discovery | facet `discovery` | `register_discovery` / `discover` |

Registering an unknown *is* presenting a construct. Querying the unknown registry *is* filtering the one store. Nothing is duplicated and nothing can drift.

### 6.2 A contradiction has an operational consequence

Which resolution states **contradict** is declared (`contradicting: true/false` per state), not decided in code. A contradiction in a contradicting state puts the constructs it names into `registry.contradicted()`, and rule UCON-DR-03 then quarantines them on their next presentation.

Measured:
```
register_contradiction(left=U, right=X, resolution_state="open")
re-present U  →  QUARANTINE  (UCON-DR-03)
                 history: [RESEARCH (superseded), QUARANTINE (active)]
resolution_state="resolved-by-evidence"  →  U is no longer in contradicted()
```

Quarantine, not rejection: **discarding a contradiction destroys the evidence that the contradiction exists.**

### 6.3 Integrity

Append-only. History is superseded and kept, never rewritten. The journal is hash-chained from `GENESIS = "0"*64`, so a retroactive edit or a reordering breaks `chain_is_intact()` — verified by forging an entry in the test suite. No clock is read: ordering is a registry-assigned sequence, because a wall-clock ordering would make two identical runs produce different bytes.

### 6.4 Registration in the repository's own planes

The 15 new artifacts were registered through the existing authority (`00-MASTER/UCOS-UGA-001/uga_engine.py run`), not a new one:

```
UCOS-ENGINE-001276 … 001289   engine/construct/*.py            EXECUTABLE_OBJECT
UCOS-DATAOBJ-000132           ucon-declaration.json            DATA_OBJECT
UCOS-TESTOBJ-000838           test_construct_foundation.py     TEST_OBJECT
```

Purely additive: `id-ledger.json` `by_object` **+34 / −0 / ~0**; universal registry **+52 / −0** (6,662 → 6,714). UCON holds no counter and mints no repository serial.

---

## 7. DISCOVERY ARCHITECTURE

### 7.1 Six declared sources

| Source | Selects | Priority | Impact | Why |
|---|---|---|---|---|
UCON-DS-01 | facet `unknown` | P1 | architectural | this is what makes "unknowns automatically become research objects" a mechanism |
UCON-DS-02 | facet `contradiction` | **P0** | architectural | a contradiction nobody is investigating is the highest-value discovery in the system |
UCON-DS-03 | disposition `ESCALATE` | **P0** | **constitutional** | an escalation is evidence of a gap in the **rule set itself** |
UCON-DS-04 | disposition `UNDECIDABLE` | P2 | constitutional | a future framework may decide what this one cannot |
UCON-DS-05 | unresolved dependency | P2 | operational | future, misnamed, or belonging to an owner who has not presented it |
UCON-DS-06 | facet violation | P3 | local | the discovery is *what the presenter was unable to supply* |

UCON-DS-03's impact is `constitutional` deliberately: the question is not what to do with that construct but **why the governance had nothing to say about it.**

### 7.2 Termination without a counter

Derived constructs take a natural key that is a function of their subject (`discovery-of:<identity>`, prefix declared). The identifier is therefore determined by the subject rather than by when the walk happened, so `discover()` checks whether the derived identity already exists and mints nothing when it does.

Measured (UCON-L-07): run 1 mints, run 2 returns `()`, run 3 returns `()`, and the registry digest is unchanged after run 1 — a fixed point, not a loop with a bound.

`opportunities()` is separated from `discover()` so "what is discoverable" can be answered without minting: a read that changes the thing it reads is a read nobody can trust twice.

---

## 8. RESEARCH ARCHITECTURE

`promote_to_research(registry, identity)` transforms **any** construct into a research object about it — not only those the foundation anticipated. Lineage names the subject in both directions; the object starts in the declared first research state with the subject's own formulation as its hypothesis; and it is idempotent by identity, so research objects cannot multiply.

The research facet requires `hypothesis` and `research_state` and optionally carries `findings`, `open_questions`, `future_work`, `confidence`, `dependencies`.

**Confidence is a reference, never a number invented here.** UKIP already owns confidence as a UCXI `KNOWLEDGE` context keyed on `(knowledge_id, version)` (`engine/knowledge/ukip/confidence.py`). A float in this payload would be a second authority over the same quantity, so the field carries the context identifier and this capability computes no confidence of its own.

Nine research states, including `refuted` — *a refutation is a finding, not a failure, and the object is retained* — and `undecidable`, distinct from `inconclusive`.

---

## 9. GOVERNANCE ARCHITECTURE

### 9.1 Disposition as a lifecycle

Eight dispositions, each declaring what it `permits` and what it may become. **Nothing is terminal.** REJECT names 7 successors; a rejection is reconsiderable on new evidence. UNDECIDABLE is non-terminal on purpose: a terminal UNDECIDABLE would be a claim about all future frameworks.

`redispose` enforces the declared successor graph, so the lifecycle is a lifecycle rather than a suggestion, and the superseded record is retained.

### 9.2 The eleven rules

| Rule | → | Fires when | The reasoning |
|---|---|---|---|
DR-01 | ESCALATE | escalation requested | cheaper than discovering later that a rule decided something a human meant to decide |
DR-02 | UNDECIDABLE | declared undecidable | more useful than forcing a verdict the framework cannot support |
DR-03 | QUARANTINE | a contradiction names it | retained; discarding it destroys the evidence |
DR-04 | TRANSFORM | kind unregistered | the transformation is one registration — **which is why it is not REJECT** |
DR-05 | RESEARCH | kind ∈ {unknown, question} | an unknown is productive, not defective |
DR-06 | RESEARCH | research state unfinished | promoting on partial evidence is how an investigation becomes a claim |
DR-07 | DEFER | unresolved dependency | records **what** is being waited for, so a wait cannot become a drop |
DR-08 | QUARANTINE | `provenance == unattributed` | rejecting it would lose the record that it was presented |
DR-09 | RESEARCH | UNKNOWN/HYPOTHETICAL ∧ no evidence | that is a research subject, not a verdict |
DR-10 | ADMIT | evidence present | governed representation and nothing more |
DR-11 | **ESCALATE** | always (**catch-all**) | a gap in the rule set; an authority must decide |

Totality is structural: the catch-all's position is checked at **load**, so a rule set that could miss cannot be loaded. Measured by presenting a construct engineered to match no specific rule and requiring the catch-all to take it.

### 9.3 Governance is governable

A `governance-rule` is a construct (UCON-EP-05), registered through the same mechanism as everything else, with lineage, evidence and a disposition — and referred to the owner the declaration names for that point. UCON does **not** thereby make `engine/governance` behave differently; claiming otherwise would be this capability quietly becoming a second authority over a framework it does not own.

---

## 10. VERIFICATION ARCHITECTURE

### 10.1 Verification is itself verifiable

The `verifier` facet **requires** `assumptions` and `limitations`. A verifier declaring neither is **refused at registration**, not merely flagged:

- a verifier whose assumptions are unstated cannot be verified — there is no way to ask whether they hold;
- a verifier claiming no limitations is claiming to decide everything.

It is a refusal rather than a facet violation because admitting an unverifiable verifier would let it start certifying things immediately. Verifier **lineage** is expressible (`lineage_of`), so a verifier can verify a verifier — measured in UCON-L-12 and in the suite.

This closes a gap the pre-work audit found explicitly: *no verifier lineage, assumptions or limitations model existed anywhere* in `engine/verification_intelligence`, `engine/universal_certification`, `platform/universal_assurance` or `engine/uaue` (grep-confirmed empty).

### 10.2 The sixteen laws

| Law | Property | How it is measured |
|---|---|---|
L-01 | every construct carries exactly one active disposition | computed **and** forged: a construct with 0 or 2 is refused by the model |
L-02 | the rule set is total | catch-all position + a construct engineered to match nothing specific |
L-03 | the catch-all forecloses nothing | declared expectation **+** structural one-step reachability |
L-04 | operators are two-way bound | both directions, plus a forged rule naming an absent operator |
L-05 | nothing is silently ignored | arithmetic (population ≤ presentations) + a REJECT must stay referenceable |
L-06 | unknowns/contradictions/research/discovery are governed | registered, projected, promoted, traced |
L-07 | discovery converges | run twice; second mints nothing; digest unchanged |
L-08 | a future kind needs no redesign | **PERFORMED**: 11 invented categories; source fingerprint must not move |
L-09 | every extension point is exercisable | **PERFORMED**: all 9 admissions in memory; nothing narrows |
L-10 | nothing is terminal | + every certifying state must be able to fall to a weaker one |
L-11 | reality ⟂ admission | **PERFORMED** (64/64 pairs) **+ STRUCTURAL** (neither module imports the other) |
L-12 | a verifier declares its own limits | registration refuses the three degenerate forms |
L-13 | no unverifiable guarantee is declared | **RATCHET both ways**: undeclared occurrence *and* stale exemption |
L-14 | vocabulary is bound, not copied | **imports** CEU's seeds; refuses a binding CEU lacks |
L-15 | the closure inventory holds | **RATCHET both ways**: undisclosed in scope *and* stale disclosure *and* risen baseline |
L-16 | measurement is deterministic | byte comparison + no clock + no machine path |

### 10.3 Non-vacuity is itself measured

Sixteen laws that hold and cannot be made to fail would measure nothing. The suite forges a violating state for **each** law and asserts the refusal — e.g. setting `catch_all_disposition` to REJECT, making VERIFIED unfalsifiable, stranding a reality state, emptying the discovery sources, removing the verifier facet's required fields, lowering the baseline, binding a reality state to a CEU population that does not exist. CI gates the law table on the non-vacuity suite passing, because a green law table alone is not evidence.

---

## 11. EXTENSIBILITY AUDIT

**Deliverable:** `00-MASTER/UCON-000001/closure-inventory.json` (399 KB, digest `297a51e48a96cb17…`), regenerable by `make ucon-inventory`.

**MEASURE FIRST.** Nothing in `engine/construct/audit.py` edits, rewrites or migrates any closure it finds. A scanner that also fixed things would make the measurement unrepeatable, because the second run would be measuring the first run's edits.

### 11.1 The inventory

**1,451 closure mechanisms across 493 modules.** Each row carries module, symbol, form, line, member count, risk tier, declared owner, governed-scope flag and disclosure id.

| Form | Total | Outside governed scope | Baseline | Extensibility limitation | Proposed migration |
|---|---|---|---|---|---|
`ENUM_CLASS` | **246** | 246 | 246 | a member set fixed in source; a future member is a code edit, a release, and a migration of every persisted value | move the member set to a declaration and derive membership from a registry; keep the enum only where the vocabulary is a closed internal state machine the code branches on exhaustively |
`FIXED_VOCABULARY_TUPLE` | **477** | 477 | 477 | an ordered fixed vocabulary, frequently a seed table — benign when the runtime does not consult it after seeding, a closure when it is the authority | establish whether the runtime consults it after seeding; if it does, move it to a declaration; if it does not, disclose it as a seed |
`FIXED_DISPATCH_TABLE` | **452** | 446 | 446 | the set of behaviours the module can perform is decided in source | where it maps a declared name to an implementation, bind it two-way to the declaration; where it maps data to data, move it to a declaration |
`FROZEN_MEMBERSHIP_SET` | **240** | 239 | 239 | a membership test against a fixed population | read the population from the owner's declaration; keep the constant as a cache of what was read |
`POPULATION_ASSERTION` | **36** | 35 | 35 | asserts a population has exactly N members | assert a floor or a declared expectation, or derive N from the declaration |

### 11.2 Risk classification — declared, never inferred

| Tier | Count | Criterion |
|---|---|---|
R1-CONSTITUTIONAL | **46** | the module is named by a declared constitutional owner |
R2-ARCHITECTURAL | **177** | the closure is consulted by more than one package |
R3-LOCAL | **1,220** | internal to one module |
R4-DELIBERATE | **8** | disclosed with `intentional: true`, a closing invariant and an admission path |

Risk is mapped from module prefix to tier and owner, resolved by **longest prefix** so declaring a narrower owner never depends on list order. A prefix the declaration does not name takes the declared `undeclared_tier` (R3-LOCAL) and is counted in the backlog — the conservative answer rather than a flattering one. Inferring a tier from a keyword would manufacture exactly the classification the audit exists to measure, invisibly.

By owner (top): UNDECLARED 1,220 · EPIC-UKDA 50 · EC-2 security 32 · UCKP-LAW-0001 21 · UCXI-000001 21 · UCOS-CEU-001 20 · EC-2 platform foundation 15 · UAUE-000001 10.

### 11.3 Notable closures located (concrete migration targets)

| Closure | Where | Limitation | Migration |
|---|---|---|---|
`Facet` (33 members) | `engine/uckp/facets.py:25` | **deliberately** closed — "a thirty-fourth facet is a constitutional amendment"; live-imported by `engine/root_ontology/contract.py` so the reduction table cannot drift | none proposed; this is R1 and correctly closed |
`AXIS_DERIVATION` (19 axes) | `engine/context/location.py:93` | **the single highest-leverage finding.** `reference-frames.json` declares frames as data with `"closed_set": false`, but `ReferenceFrame.__post_init__` refuses any axis not in this **Python** tuple — so a new *frame* is a data edit while a new *axis* (`galaxy`, `star-system`, `planet`, `region`, `coordinate-frame`) is a code edit, contradicting the file's own openness claim | move `AXIS_DERIVATION` into the catalog (or a second `axes.json`) |
`Role` (9) · `Permission` (4) · `CapabilityGroup` (16) · `_MATRIX` (9×16) | `platform/foundation/identity.py`, `platform/identity/` | Earth-enterprise RBAC; adding a role requires editing the enum **and** every matrix row | registry-driven role and capability space |
`_ID_DIGEST_LEN = 12` | `engine/registry/universal/identity.py:31` | 48-bit truncated hash — the de-facto population ceiling (~50% collision at ~2²⁴ per kind); 16-hex platform ids are 64-bit | widening is one line but breaks every persisted identifier, and `parse_kind` requires exactly 3 dash-parts |
`ConversionRule.convert: Callable` | `engine/temporal/operations.py:33` | temporal conversions are Python callables, so a new calendar conversion cannot be a data edit; `TemporalRegistry` also seeds **zero** reference systems | declarable conversions + a `catalog/*.json` mirroring `reference-frames.json` |
`DiscoveryKind` (8) | `engine/discovery/contracts.py:42` | the discovery dimension set is closed; `coerce` raises | registry-backed dimensions |

### 11.4 The ratchet — two halves, both directions

```
INSIDE  governed_scope (= engine/construct/ only)
        every closure must be DISCLOSED with intentional flag, closing invariant, admission path.
        An undisclosed closure is a VIOLATION.
        A disclosure whose closure is GONE is ALSO a violation → disclosures cannot rot.

OUTSIDE governed_scope
        the population per form may not EXCEED the declared baseline. It may hold; it may fall.
```

Governed scope initially contains **exactly this capability**. A capability that ratcheted every other owner's code before its own would have inverted the obligation. Widening the scope is how backlog becomes enforcement, one named owner at a time.

A global gate demanding zero closures today would have been closed on the day it was written and deleted on the next — UISD-000001 §ISD-L-07 established that failure mode in this repository.

### 11.5 The audit is subject to itself

Eight closures inside governed scope, all disclosed:

| id | Symbol | Form | Closing invariant |
|---|---|---|---|
UCON-CL-01 | `disposition.OPERATORS` | dispatch | two-way bound to the rules (L-04) |
UCON-CL-02 | `views.SELECTORS` | dispatch | two-way bound to the discovery sources |
UCON-CL-03 | `extension.ADMISSIONS` | dispatch | two-way bound to the extension points; every entry exercised each run |
UCON-CL-04 | `audit.DETECTORS` | dispatch | two-way bound to the closure forms — **deliberately self-referential**: this table is one of the closures the audit reports |
UCON-CL-05 | `contract.LAW_CHECKS` | dispatch | two-way bound to the laws |
UCON-CL-06 | `audit._ENUM_BASES` | frozenset | closed because *Python* closes it — a fact about the stdlib, not a UCOS vocabulary |
UCON-CL-07 | `audit.len(node.targets)` | population assertion | a declared **false positive**, retained rather than suppressed: narrowing the detector would stop it finding real population pins, and rewriting the comparison to evade its own detector would be the audit gaming itself |
UCON-CL-08 | `evidence._PRODUCED` | dispatch | two-way bound to the declared evidence records |

Two of these were found by the ratchets **during** this work and fixed properly rather than exempted:

1. `registry.py` hardcoded `"REJECT"` → now `construct_kinds.registration_dispositions: ["ADMIT"]`, read from the declaration. (Found by the CI probe that forbids a vocabulary member appearing in an engine.)
2. `__init__.py` restated the refused-claims phrases verbatim → now points at the declaration. (Found by UCON-L-13.)
3. `evidence._PRODUCED` was an undisclosed dispatch table → disclosed as UCON-CL-08. (Found by UCON-L-15.)

Also fixed: the contradiction class `authority` collided with the JSON key `authority`, which made the strict "no vocabulary leak" probe unable to distinguish a real leak from a key read — renamed to `authority-conflict`, which is clearer anyway. Vocabulary leaks into the engines are now **0**.

---

## 12. REPOSITORY IMPACT ANALYSIS

### 12.1 New (17 files)

```
00-MASTER/UCON-000001/ucon-declaration.json      the declaration (all vocabulary)
00-MASTER/UCON-000001/closure-inventory.json     the audit deliverable
engine/construct/                                14 modules
engine/tests/unit/test_construct_foundation.py   204 tests
.github/workflows/ucon-gate.yml                  3-job CI gate
UCOS-UCON-000001-…-DETERMINATION.md              this document
```

### 12.2 Modified (existing owners)

| File | Change | Why required |
|---|---|---|
`pyproject.toml` | `ucos-construct` script; `--cov=engine.construct`; coverage source | RCH-ENTRYPOINT + the measured denominator |
`Makefile` | `ucon`, `ucon-gate`, `ucon-json`, `ucon-audit`, `ucon-inventory`, `ucon-discover` (additive) | one-command surfaces |
`verify.sh` | Stage 6i `run_stage` | the gate must run in the canonical path, not only in CI |
`00-MASTER/UVI-000001/uvi-declaration.json` | stage `universal-construct` at index 13 | UVI-L-03 requires exact set **and order** parity with `verify.sh`; UVI-L-11 requires the read-set to resolve |
`00-MASTER/UAKOS-CLOSURE-008/validation-record.json` | stage + `stages_digest` | the three-reader contract; a stage in `verify.sh` and not here makes the record a stale claim |
`00-MASTER/UAKOS-CLOSURE-008/04-…md`, `06-…md` | re-rendered | committed registers must be the rendered fixed point |
`00-BOOK/DATA/id-ledger.json` | +34 `by_object` | registration of the new artifacts |
`00-BOOK/DATA/canonical-observation-audit.json`, `00-MASTER/UCOS-UGA-001/*` (10 surfaces) | regenerated | UGA registration surfaces |

### 12.3 Zero behavioural change to existing capabilities

No existing module was edited. `engine/construct` is additive; every other change is a declaration, a registry surface, or wiring. All 29 UGA invariants pass; all 14 UVI laws pass; the 23 validation-record tests pass.

### 12.4 Registration side effect — disclosed

`uga_engine.py run` also registered **18 pre-existing unregistered `00-BOOK/PORTAL/*.md`** files, because the engine closes the whole ledger backlog in one pass. This was a pre-existing gap, not introduced by UCON, and it is bundled into the same diff. Reported rather than hidden.

---

## 13. MIGRATION STRATEGY

Nothing in this work migrates a closure. The strategy for the 1,443 closures outside governed scope is **owner-by-owner, measured, and ratcheted** — never a sweep.

**Phase M0 — hold (now, in force).** The baseline is declared and enforced. The population may fall; it may not rise. New code in `engine/construct/` may not add an undisclosed closure at all.

**Phase M1 — widen governed scope by one owner.** For a chosen owner (candidate order below), enumerate its closures from the inventory, disclose each with a closing invariant and an admission path or migrate it, then add its prefix to `governed_scope`. Each widening is a decision with a named owner.

Candidate order, by leverage rather than by count:

| Order | Owner / target | Why first | Cost |
|---|---|---|---|
1 | `engine/context/location.py::AXIS_DERIVATION` | the only closure that **contradicts its own file's declared openness**; blocks `galaxy`/`system`/`planet`/`region`/`coordinate-frame` | small: move a tuple to the catalog |
2 | `engine/temporal` conversions + a seeded catalog | non-Earth time is *representable* but **undeclared** — zero reference systems are seeded | medium |
3 | `platform/identity` role/capability space | 3 closed enums + a 9×16 hardcoded matrix; no principal kind; no temporal validity; no location binding | large |
4 | `_ID_DIGEST_LEN` (48-bit) | the only genuine population ceiling in the system | large + breaking: every persisted identifier |
5 | `engine/discovery::DiscoveryKind` | closed dimension set in a capability whose job is discovery | small |

**Phase M2 — lower the baseline.** Each migration reduces a form's population; the baseline is edited down to match. The ratchet makes the reduction permanent.

**Explicitly out of scope.** `engine/uckp/facets.py::Facet` (33) is correctly closed and live-bound to the root-ontology reduction table; migrating it would require a constitutional amendment and would weaken UCPA-L-03. `engine/kernel/` already contains zero enums and enforces it.

---

## 14. RISK ANALYSIS

| # | Risk | Severity | Mitigation in place | Residual |
|---|---|---|---|---|
R1 | The registry becomes a dumping ground: everything recorded, nothing decided | Medium | every construct carries exactly one **traceable** disposition with rule + rationale; ESCALATE and UNDECIDABLE are surfaced as P0/P2 **constitutional** discoveries | Real. Governance must work the escalation queue; UCON makes it visible, it cannot make anyone act |
R2 | The catch-all is quietly changed to REJECT | **High** | UCON-L-03 measures the declared expectation **and** structural non-foreclosure; CI gates it | Low |
R3 | Reality and admission are coupled by a future edit | High | UCON-L-11 parses both modules; the type split makes the coupling inexpressible | Low |
R4 | The audit becomes a document nobody runs | Medium | it is Stage 6i of `verify.sh`, a CI job, and law UCON-L-15; the inventory is regenerable and content-addressed | Low |
R5 | The baseline is raised to make the gate pass | Medium | the ratchet direction is declared and law-enforced; raising it is a visible diff to a declaration whose `$why_a_ratchet_and_not_a_gate` note explains the rule | **Real** — a determined editor can raise it. Detectable, not prevented |
R6 | Disclosures accumulate as excuses | Medium | a stale disclosure is a **violation**; each requires a closing invariant **and** an admission path | Low |
R7 | UCON drifts into a second existence vocabulary | High | UCON-L-14 imports CEU's seeds and refuses an unbacked binding; also refuses restating a whole CEU population | Low |
R8 | The detector cache serves a stale answer | Medium | keyed on **content digest**, so a changed byte is a changed key; a test proves it | Low |
R9 | Registration allocated permanent identifiers | Medium | additive only (+34/−0); no renumbering; snapshot retained; nothing committed | Accepted — allocation is append-only by design |
R10 | 18 unrelated PORTAL files registered in the same pass | Low | disclosed in §12.4 | Accepted |
R11 | Gate cost (~5.9 s) grows with the repository | Low | content-digest memoisation; the scan is the dominant term and is linear | Low |
R12 | `contract.py` at 81% coverage | Low | the uncovered arms are defensive violation branches inside checks whose main paths are exercised; aggregate 92% | Low |

**Honest limitations.** UCON measures what is *presented to it*. It does not discover constructs nobody presents, and the closure audit only detects the five declared syntactic forms within the declared roots — a closure expressed some other way, or outside those roots, is invisible to it. Neither limitation is hidden: both are properties of a declared scan configuration, and widening either is a data edit.

---

## 15. ENFORCEMENT ANALYSIS

The question this section answers: **which claims are operationally enforced, and which are only declared?**

| Claim | Enforcement | Grade |
|---|---|---|
Every construct receives exactly one active disposition | `Construct.__post_init__` **refuses** otherwise — a *type* invariant, not a check | **STRUCTURAL** |
No construct is silently ignored | no refusal path exists in the registry; L-05 verifies the arithmetic | **STRUCTURAL** |
Disposition is total | catch-all position checked at **load**; a rule set that could miss cannot load | **STRUCTURAL** |
Admission does not imply truth | the conjunction in `permitted_acts`; the two facts live in separate types | **STRUCTURAL** |
Reality is not derived from admission | the two modules cannot import each other; L-11 parses both | **STRUCTURAL** |
A future kind needs no redesign | L-08 fingerprints the package across an admission | **PERFORMED** |
Every extension point works | L-09 performs all nine in memory | **PERFORMED** |
Extensions never narrow | `adopt()` refuses narrowing; `extended_with_*` are non-mutating | **STRUCTURAL** |
Discovery converges | derived identity + existence check; L-07 measures the fixed point | **PERFORMED** |
A verifier declares its limits | registration refuses the degenerate forms | **STRUCTURAL** |
Vocabulary is bound, not copied | L-14 **imports** the owner's seeds | **PERFORMED** |
Nothing is terminal | L-10 walks the successor graphs and the permission lattice | **COMPUTED** |
No unverifiable guarantee is declared | L-13 scans this package's source; ratchet both ways | **COMPUTED (ratchet)** |
The closure inventory holds | L-15; ratchet both ways | **COMPUTED (ratchet)** |
Determinism, writes nothing | L-16 + CI double-run diff of report *and* `git status` | **PERFORMED** |
Operators/selectors/admissions/forms/checks are two-way bound | refused at **load** in both directions | **STRUCTURAL** |

**Declared but not enforced by UCON** (honestly stated):

- That an escalation is *acted upon*. UCON records and prioritises it; acting is governance's.
- That a registered `location-axis`, `temporal-system` or `identity-namespace` changes its owner's behaviour. It does not, and the code says so — these are governed representations *referred to* their owners.
- That the 1,443 closures outside governed scope will be migrated. Only non-increase is enforced.
- Birth. Gap UCON-G-02: `ucos.construct` is not a declared UOBC namespace, so no birth record is claimed and none appears in the birth ledger.

---

## 16. VERIFICATION PLAN

### 16.1 Mandatory verification — the twelve requested demonstrations

| # | Required demonstration | Evidence | Result |
|---|---|---|---|
1 | every construct receives a disposition | UCON-L-01 + `Construct.__post_init__` + `registry.undisposed()` | **HOLDS** (`undisposed: []`) |
2 | no construct is silently ignored | UCON-L-05: `presented ≥ held`, every hostile presentation retrievable, REJECT still referenceable | **HOLDS** |
3 | unknowns are representable | UCON-L-06; 14 declared classes incl. the second-order unknown | **HOLDS** |
4 | contradictions are representable | UCON-L-06; retained, standing-vs-resolved, operationally quarantining | **HOLDS** |
5 | research objects are representable | UCON-L-06; `promote_to_research` on **any** construct, idempotent | **HOLDS** |
6 | future domains are representable | UCON-L-08: 11 invented categories admitted, **source fingerprint unchanged** | **HOLDS** |
7 | ontologies can evolve | UCON-EP-04 exercised by UCON-L-09 | **HOLDS** |
8 | governance can evolve | UCON-EP-05 exercised by UCON-L-09 | **HOLDS** |
9 | verification can evolve | UCON-EP-06 + UCON-L-12 (assumptions, limitations, verifier-of-verifier lineage) | **HOLDS** |
10 | location frameworks can evolve | UCON-EP-07 exercised; the blocking closure in the *owner* is inventoried and given a migration path | **HOLDS** (representation) |
11 | temporal frameworks can evolve | UCON-EP-08 exercised; owner-side gaps inventoried | **HOLDS** (representation) |
12 | reality status is independent of admission | UCON-L-11: **64/64** pairs + structural non-import + the conjunction | **HOLDS** |

For 10 and 11 the honest scope is stated: UCON proves the *governed representation* of an axis or a temporal system is admissible and traced. Making `engine/context` resolve a new axis is the owner's change, and the audit names it as migration target #1 and #2.

### 16.2 Executable evidence

```bash
make ucon                 # 16 laws, every refusal named
make ucon-gate            # fail-closed  → exit 0
make ucon-audit           # the inventory, rendered
make ucon-inventory       # regenerate 00-MASTER/UCON-000001/closure-inventory.json
./verify.sh --full        # Stage 6i runs in the canonical path
.ec1-venv/bin/python -m pytest engine/tests/unit/test_construct_foundation.py   # 204 passed
```

### 16.3 Results

```
UNIVERSAL CONSTRUCT FOUNDATION — UCON-000001
  declaration           : UCON-000001 v1.0.0   digest 192c63afe7073691
  laws measured         : 16   holds 16   refused 0
  constructs registered : 32   (presented 32, undisposed 0)
  registered kinds      : 32  (open by registration)
  closures inventoried  : 1451   across 493 modules
  governed scope        : 8 closures, all disclosed
  verdict: OPEN
```

- `./verify.sh --full`: **15/16 stages PASS**, including Stage 6i. Combined coverage **97%**.
- Tests: **204/204**; `engine.construct` **92%**.
- UGA 29/29 · UVI 14/14 · validation-record 23/23.

### 16.4 The one outstanding failure — pre-existing, not UCON

`engine/tests/unit/test_verification_impact.py::test_cli_bounded_change_exits_zero` and `::test_cli_emits_json` fail. **Proven pre-existing**: both fail identically in a clean `git worktree add … HEAD --detach` with none of this work present. `engine/knowledge/ukip/errors.py` now escalates to an `integration` blast radius where the tests expect `changed`/bounded. Owner: `engine/verification_impact`. Deliberately **not** fixed here — changing that engine's thresholds or the tests' example paths is a separate governed decision under a different owner, and silently adjusting either would be exactly the kind of unrelated change that makes a diff untrustworthy.

---

## 17. IMPLEMENTATION ROADMAP

**Wave 0 — COMPLETE (this work).** Declaration; 11 parts; 16 laws; 204 tests; gate; CLI; `verify.sh` Stage 6i; UVI + validation-record parity; CI workflow; registration; the closure inventory.

| Wave | Deliverable | Depends on | Owner |
|---|---|---|---|
W1 | Close UCON-G-02: declare `ucos.construct` in UOBC `namespace_policy`; constructs then carry birth records | UOBC-000001 | UOBC |
W2 | Close UCON-G-01: CEU registers an `undecidable` epistemic row; UNDECIDABLE binds; the gap closes | UCOS-CEU-001 | CEU |
W3 | Migration target #1: `AXIS_DERIVATION` → catalog; then register `galaxy`/`system`/`planet`/`region`/`coordinate-frame` as data; widen `governed_scope` to `engine/context/` | W0 | UCXI-000001 |
W4 | Migration target #2: seed `engine/temporal` reference systems in a catalog; make conversions declarable; join the context `calendar`/`time-standard` axes to `ReferenceSystem` | W3 | CMG-000002 |
W5 | Persist the construct registry (today it is in-memory per process) behind a declared storage binding | W0 | UCON-000001 |
W6 | Escalation workflow: route ESCALATE and UNDECIDABLE discovery objects to a governance queue with an owner and an SLA | W0 | governance |
W7 | Migration target #3: registry-driven identity roles/capabilities; principal kind; temporal validity; reference-frame binding | W3, W4 | EC-2 identity |
W8 | Digest-width determination for `_ID_DIGEST_LEN` (48-bit ceiling) | W7 | UCKP-ART-05 |

**Deliberately not scheduled:** migrating `Facet` (correctly closed, constitutionally bound); a second registry for any of the four projections; any claim that the remaining 1,443 closures will be migrated on a timetable.

---

## 18. PRIORITIZED EXECUTION SEQUENCE

Ordered by *what unblocks the most* per unit of risk, not by size.

| Seq | Action | Effort | Risk | Unblocks | Gate |
|---|---|---|---|---|---|
**1** | **Review and commit Wave 0.** Nothing is committed; everything is staged. Registration allocated permanent identifiers additively (+34/−0) | — | Low | everything | `./verify.sh --full`, `register.sh --observe` |
2 | Triage the 2 pre-existing `test_verification_impact` failures with their owner | S | Low | a green `verify.sh` | pytest stage |
3 | W3 · `AXIS_DERIVATION` → catalog | S | Low | universe/galaxy/system/planet/region/coordinate-frame **as data**; resolves the one self-contradicting closure | UCXI tests + UCON-L-15 |
4 | W2 · CEU `undecidable` epistemic row | S | Low | closes UCON-G-01 | UCON-L-14 |
5 | W1 · UOBC declares `ucos.construct` | S | Low | closes UCON-G-02; birth records | UOBC gate |
6 | W6 · escalation workflow | M | Low | makes the escalation queue actionable rather than merely visible | — |
7 | W4 · temporal catalog + declarable conversions | M | Medium | Mars/lunar/mission-elapsed/logical time **declared**, not merely representable | CMG-000002 |
8 | W5 · persist the construct registry | M | Medium | cross-process construct truth | UCON-L-16 |
9 | Widen `governed_scope` to `engine/context/`, then `engine/temporal/` | S each | Low | converts backlog into enforcement, per owner | UCON-L-15 |
10 | W7 · identity model | L | High | non-human, non-Earth, federated principals | EC-2 identity |
11 | W8 · digest width | L | **High — breaking** | removes the only real population ceiling | full replay |

**Sequence 1 is the only action requiring a decision now.** Everything else is scheduled work with a named owner.

---

## APPENDIX A — REQUIREMENT TRACEABILITY

| Req | Subject | Where realised | Verified by |
|---|---|---|---|
1 | Universal Construct model | `model.py`; 32 seed kinds incl. every category the requirement lists + `future-unknown-model` | UCON-L-08 |
2 | Universal Disposition engine | `disposition.py`; all 8 required dispositions; total; traceable | L-01, L-02, L-03, L-04, L-05 |
3 | Unknown registry | `views.py` unknown projection; 14 classes; no enum expansion needed | L-06 |
4 | Contradiction registry | `views.py` contradiction projection; retained; queryable; operational | L-06 |
5 | Research object framework | `views.py` research projection; `promote_to_research`; confidence by reference | L-06 |
6 | Reality status framework | `reality.py`; all 8 required states; transitions; floors; the conjunction | L-10, L-11, L-14 |
7 | Extensibility audit | `audit.py`; `closure-inventory.json`; 1,451 closures, tiers, owners, migrations | L-15 |
8 | Recursive discovery engine | `views.py` 6 sources; unknowns → research automatically; fixed point | L-07 |
9 | Self-extending ontology | kind `ontology` (facet `extension`); UCON-EP-04 | L-09 |
10 | Self-extending governance | kinds `governance-model`, `governance-rule`; UCON-EP-05 | L-09 |
11 | Self-extending verification | kind `verifier`; assumptions+limitations required; lineage; UCON-EP-06 | L-12 |
12 | Universal location framework | kinds `location-model`, `location-axis`; UCON-EP-07; owner closure inventoried as migration #1 | L-09, L-15 |
13 | Universal temporal framework | kinds `temporal-model`, `temporal-system`; UCON-EP-08; owner gaps inventoried as migration #2 | L-09, L-15 |
14 | Universal identity framework | kinds `identity-model`, `identity-namespace`; UCON-EP-09; ceilings inventoried (48-bit) | L-09, L-15 |
15 | Universal Discovery Council | discovery projection; priority, impact, dependencies, evidence gaps, research/governance/verification status | L-06, L-07 |

## APPENDIX B — NON-NEGOTIABLE CONSTRAINTS, AUDITED

| Constraint | Compliance |
|---|---|
No unverifiable guarantees | L-13 scans this package's source; ratchet both ways |
No claim of complete future knowledge / first discovery / supremacy / completeness | declared in `principle.refused_claims`; L-13 enforces absence |
No silent assumptions | the initial reality state, the seed reality state, the contradicting resolution states, the registration dispositions, the undeclared tier and the deliberate tier are **all declared** — each was a literal in code at some point during this work and each was moved out |
No silent closure mechanisms | L-15; 8 in scope, all disclosed; 1,443 outside, all inventoried and baselined |
No hardcoded future limits | `closed_set: false`, `upper_limit: null` in every emitted document; existing ceilings (48-bit digest) inventoried rather than introduced |
Registries over enumerations | 4 projections over one store; `registered_kinds` derived from the record, consulting no table |
Representation over prediction | the model represents; it predicts nothing |
Governance over assumption | 11 declared rules; catch-all ESCALATE; nothing defaults |
Discovery over static completeness | 6 sources; recursive; converges |
Enforceable runtime over declarations | §15: 9 STRUCTURAL, 5 PERFORMED, 2 COMPUTED-ratchet; declared-but-unenforced items listed explicitly |

---

**AUTHORITY = NONE (DERIVED TRUTH).** UCON-000001 owns no ontology, mints no identity, holds no counter, and certifies nothing. What it adds is a total, traceable disposition for every presented construct, and a governed home for the unknown, the contradictory and the undecidable.

**Closed set:** false. **Upper limit:** null.
