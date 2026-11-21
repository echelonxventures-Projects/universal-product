# MUTATION OWNERSHIP DISCOVERY DETERMINATION

> **Mission:** UCOS Ω∞ — verification/evolution plane separation, discovery phase
> **Baseline:** `5eb1a704` · **Branch:** `integration/recovery-001` · **Date:** 2026-08-17
> **Mode:** DISCOVERY ONLY. **No code was modified in producing this document.** Earlier `--check`/`--reconcile` edits to `register.sh`, `verify.sh`, `ucos-registration-gate.yml` and `Makefile` were reverted before this discovery began; `register.sh` and the workflow are byte-identical to HEAD.
> **Authority:** NONE (DERIVED TRUTH). Locates responsibility. Proposes; implements nothing.

---

## 1. The two framing questions, answered

### 1.1 Is `register.sh` an evolution transaction engine?

**Yes — it says so in its own first line, and it is not incorrect.**

> "REG-AUTO-001 **Atomic Artifact Registration Transaction** … the single, idempotent, **all-or-nothing operation** that brings the repository's synchronized state … into agreement with the physical artifacts on disk."

Ten phases. Phase 1 is `ukb build`. Phase 10 is "transaction sealed". It is a transaction engine by design and by name. **`register.sh` is the correct owner of registration mutation.**

### 1.2 Is `verify.sh` incorrectly invoking an evolution transaction?

**Yes. This is the entire defect.**

`verify.sh:329-330`:

```bash
run_stage "registration + drift gate (register.sh --guard)" \
  env PYTHON="$PY" bash 00-BOOK/tools/register.sh --guard
```

`--guard` does not mean "check". In `register.sh` it sets `GUARD=1`, which changes **nothing** about phases 0-10 — the full mutating transaction runs regardless — and then adds a post-transaction drift comparison. So the sequence is:

```
mint identifiers → rewrite registers → regenerate portal → THEN ask "is anything uncommitted?"
```

The gate therefore **reports the drift it just caused**. Measured live in this session: `verify.sh --full` over a corpus with 140 unregistered artifacts took `artifacts.json` from **1 233 → 1 373**, emitted **~140 new PORTAL pages**, and failed with `exit 3` on the resulting drift. A verification command performed the G11 migration as a side effect.

**The fault is ownership invocation, not `register.sh`.** `register.sh --guard` is an evolution transaction with a verification-sounding flag name, called from the verification plane.

---

## 2. Responsibility map

| Component | Purpose | Allowed mutation | Lifecycle owner |
|---|---|---|---|
| `verify.sh` | Observe repository truth across 11 stages | **NONE** (declared: "lint, test corpus, coverage gate, governance enforcement, registry schema validation, meta-constitutional conformance") | `mutation-governance-boundary.json` → SOURCE chain |
| `ukb.py cmd_build` | Allocate corpus identity + emit 6 registers | **MINT + REGISTER** — `allocate()` (line 945) and `_dump_json()` ×6 (lines 1242-1253) | UMB-IMP-001 |
| `ukb.py validate / enforce / eligibility` | Structural + schema + eligibility observation | **NONE** (verified empirically) | UMB-IMP-001 |
| `ukbx.py sync / twin / portal / certify` | Regenerate twin, portal, certification | **IDEMPOTENT REGENERATION** — writes identical bytes at a fixed point | UMB-IMP-004/006 |
| `ukbx.py validate / twin --check` | Signal-ledger + twin certification observation | **NONE** (verified empirically) | UMB-IMP-006 |
| `register.sh` (phases 0-10) | Atomic registration transaction | **FULL** — mint, registers, twin, portal, lineage projection | REG-AUTO-001 |
| `uga_engine.py run` | Mint UGA object identity, emit 9 surfaces | **MINT + PROJECT** — `epoch1_identity(mint=True)` (line 1626) | UCOS-UGA-001 |
| `uga_engine.py gate` | 29 invariants over the boundary | **NONE** (verified empirically) | UCOS-UGA-001 |
| `engine/uckp/identity.py` | Derive constitutional identity (URN + UUIDv5) | **NONE** — pure, clock-free, path-free | UCKP-ART-05 (**SUPREME**) |
| `engine/object_birth/` | Birth contract: identity before existence | **NONE** in gate; ledger append is explicit | UOBC-000001 |
| `engine/nucleus/lineage.py` | Hash-chained append-only lineage | **APPEND** via `record()` | UCOS-NUCLEUS-001 |
| `engine/universal_certification/` | Issue certificates + audit ledger | **APPEND** via `CertificationPipeline.run()` | UCOS-EPIC-006 |
| `engine/uaue/gate.py` | Evolution transaction over Article-14 | `--render` **WRITES 19 files**; `--gate`/`--replay` **NONE** | UAUE-000001 |
| `engine/verification_impact/` | Select minimal verification | **NONE** (verified empirically) | this cycle, DERIVED |

### 2.1 Empirical mutation probe

Each command run against the real tree, comparing `git status --porcelain` digests before and after:

```
READ-ONLY  ukb.py enforce --pre        READ-ONLY  uga_engine.py gate
READ-ONLY  ukb.py validate            READ-ONLY  engine.uaue.gate --gate
READ-ONLY  ukb.py eligibility         READ-ONLY  engine.object_birth.gate
READ-ONLY  ukbx.py validate           READ-ONLY  engine.verification_impact
READ-ONLY  ukbx.py twin --check
READ-ONLY  ukbx.py portal   ← idempotent regenerator at a fixed point
READ-ONLY  ukbx.py twin     ← idempotent regenerator at a fixed point
READ-ONLY  ukbx.py certify  ← idempotent regenerator at a fixed point
```

**Every stage `verify.sh` invokes is observationally pure except one: `register.sh --guard`.**

An important nuance: phases 2, 3, 4 and 8 are *idempotent regenerators*. They write, but at a fixed point they write identical bytes, so they are observationally read-only. They only appear to mutate **after** phase 1 has minted something for them to project. **Phase 1 is the sole source of mutation; everything downstream is a follower.**

---

## 3. Answers

### A. Where does identity get created?

Three planes, only two of which mint:

| Plane | Site | Form | Counter |
|---|---|---|---|
| **CONSTITUTIONAL_OBJECT** (SUPREME) | `engine/uckp/identity.py::UniversalIdentity.mint` | `urn:ucos:ucko:<ns>:<local>` + UUIDv5 | **none — derived** |
| **REPOSITORY_OBJECT** (PERSISTENCE) | `ukb.py::allocate` line 876, called at line **945** inside `cmd_build` | `UCOS-<CATEGORY>-<NNNNNN>` | `category_seq` |
| **UGA object** | `uga_engine.py::epoch1_identity` line 258, called at line **1626** inside `cmd_run` | same shape, shared `category_seq` | `category_seq` |

`00-BOOK/DATA/constitutional-authority-alignment.json` declares `one_authority = UCKP-ART-05`; the other two are persistence bindings of it. The declared `mint_markers` is `["category_seq"]`, and `second_authority_test` states "a mint is recognised by the counter it advances".

**So: identity is created in `ukb.py::cmd_build` and `uga_engine.py::cmd_run` — and nowhere else.**

### B. Where does registry mutation happen?

`ukb.py::cmd_build`, exclusively, in six calls:

```
1242  _dump_json(LEDGER_PATH)         id-ledger.json
1243  _dump_json(ARTIFACTS_PATH)      artifacts.json
1246  _dump_json(VOLUMES_PATH)        volumes.json
1248  _dump_json(RELS_PATH)           relationships.json
1250  _dump_json(CHANGE_LEDGER_PATH)  change-ledger.json   ← lineage projection
1253  _dump_json(CT_JSON_PATH)        control-tower.json
```

Plus `ukbx.py` for twin/portal/certification surfaces, and `_exec_save`/`_exec_declare` for the execution register.

**Lineage mutation is line 1250** — `build_change_ledger()` (line 467), which the code itself labels "regenerated deterministically each transaction; **NOT** an append-only source of truth". The append-only lineage is a *different* owner: `engine/nucleus/lineage.py`.

### C. Where does verification call mutation?

**Exactly one place.**

```
verify.sh:330  →  register.sh --guard  →  Phase 1  →  ukb.py build  →  allocate()  →  MINT
```

`verify.sh` invokes 11 stage commands. Ten are observationally pure. The eleventh is a ten-phase mutating transaction. `generate-prerequisites.sh` (stage 1b) also writes, but only gitignored generated inputs, so it is pure with respect to version control.

### D. Which existing capability already owns evolution?

**Mutation ownership is already declared, per class**, in `00-BOOK/DATA/mutation-governance-boundary.json` (CAA role `EXECUTION`):

| Mutation class | Governed by |
|---|---|
| `CONSTITUTIONAL_TRUTH` | `UCOS-CMG-EXEC-000001` |
| `SOURCE` | pre-commit → **verify.sh** → `UCOS-RIB-001` → `UCOS-AEE-001` → Phase 8 → Phase 9 |
| `GENERATED_ARTIFACT` | `UCOS-GENERATED-ARTIFACT-REGISTRY-001` → producer → Phase 8 → Phase 9 |
| `EXCLUSION` | `UCOS-EXCLUSION-REGISTER-001` → RIB GATE-12 |
| `REPOSITORY_STATE` | `UCOS-RIB-001` GATE-02 / GATE-12 |

Its invariants read: *"Every mutation class names exactly one governing authority chain. No mutation class is claimed by two authorities as primary. **No mutation class is ungoverned.**"*

Evolution *transactions* are owned by **UAUE-000001** (`engine/uaue/`), whose `plan_contract.rollback_strategy` names "the **constitutional mutation gateway** … the only producer of a clean state seal", and whose position `AUE-P-05 Execute` binds its gate to `./verify.sh` — i.e. UAUE already treats verification as the gate that *validates* an execution, never as the executor.

### E. **The root cause, and the smallest architectural change**

**Corpus registration is an ungoverned mutation class.** Measured against the boundary register:

```
id-ledger        present in boundary register: False
artifacts.json   present in boundary register: False
category_seq     present in boundary register: False
mint             present in boundary register: False
REGISTRATION     present in boundary register: False
by_path          present in boundary register: False
```

And they are not generated artifacts either — `00-BOOK/DATA/id-ledger.json` **never appears as a `canonical_path`** in `generated-artifact-registry.json`; it appears only inside the `input_closure` of 10 *other* artifacts. UGA classifies it `TOOLING_OBJECT`, owner `UCOS-UKB-TOOLING`, lifecycle `AUTHORED`.

So identity allocation sits in a blind spot: it is not `CONSTITUTIONAL_TRUTH`, not `SOURCE`, not `GENERATED_ARTIFACT`, not `EXCLUSION`, not `REPOSITORY_STATE`. The register's invariant "no mutation class is ungoverned" is **vacuously satisfied** because corpus registration is not a *class at all*.

**That is why `verify.sh` could invoke a mint and no gate objected: no authority claims that mutation, so no authority forbids anyone from performing it.**

**Smallest architectural change — three edits, no new capability:**

| # | Change | Why it is minimal |
|---|---|---|
| **1** | Declare a `CORPUS_REGISTRATION` mutation class in `mutation-governance-boundary.json`, `governed_by: REG-AUTO-001 → register.sh`, with `does_not_govern` naming `verify.sh` explicitly | Uses the existing boundary register and its existing invariants. No new file, no new authority. Makes the violation *detectable by machinery that already runs*. |
| **2** | Give `register.sh` a read-only entry that runs only phases 0, 5, 6, 7 and reports gaps with remediation; keep phases 0-10 as the transaction, requiring an explicit determination + evolution cycle id | `register.sh` stays the transaction engine — it gains an observation mode, it is not renamed or split into a new tool. |
| **3** | Point `verify.sh:330` and `ucos-registration-gate.yml:60` at the read-only entry | One line each. The verification plane stops invoking the evolution plane. |

Plus one guardrail test asserting `./verify.sh` leaves `git status`, the registry digest and the lineage digest unchanged — which is the invariant that would have caught this on day one.

**What must NOT be done:** no second registry, no second identity system, no rename of `register.sh`, no new dictionary, no new certificate authority. Reuse UCKP-ART-05, UIS-001, UOBC-000001, UCL-000001, UAUE-000001, `engine/nucleus/lineage.py`, `engine/universal_certification/`.

---

## 4. Target architecture, expressed against located owners

```
INTENT
  │   determination artifact + evolution cycle id
  ▼
IDENTITY DERIVED            engine/uckp/identity.py        UCKP-ART-05 (SUPREME, no counter)
  ▼
BIRTH RECORD                engine/object_birth/           UOBC-000001 (9 fields, 8 laws)
  ▼
ARTIFACT MATERIALIZED       the author
  ▼
CORPUS REGISTRATION         register.sh (transaction)      REG-AUTO-001  ← currently ungoverned class
  ▼
LINEAGE APPENDED            engine/nucleus/lineage.py      hash-chained
  ▼
CERTIFICATION               engine/universal_certification/ CEP-005
  ▼
OBSERVATION                 verify.sh                      READ-ONLY, 11 stages
```

Identity is born at step 2, before the artifact exists at step 4. Verification enters only at the last step and never reaches back up the chain.

---

## 5. Proposal status

| Item | Status |
|---|---|
| Discovery | **COMPLETE** — evidence in §1-§3 |
| Responsibility map | **COMPLETE** — §2 |
| Root cause | **LOCATED** — corpus registration is an undeclared mutation class |
| Smallest change | **PROPOSED** — §3E, three edits + one guardrail test |
| Code modified | **NONE** — prior edits reverted; `register.sh` and the workflow are identical to HEAD |
| Implementation | **AWAITING APPROVAL** |

---

**END MUTATION OWNERSHIP DISCOVERY DETERMINATION**

**Status:** Evolution Baseline Established v1.0
**Authority:** NONE — DERIVED TRUTH
**Lifecycle Authority:** UCIC-001 (owner) · UCL-000001 (derived) · CMG-000001 (law)



---

# PART II — GOVERNED EVOLUTION STATE

> Added after the finding that `id-ledger.json` is neither an authored input nor a generated output. Part I stands unchanged. Still **discovery only** — no code, and no classification, has been modified.

---

## 6. Does UCOS require a third category?

**Yes. And the repository's own data already separates the two groups cleanly — the category exists in fact and is simply unnamed.**

### 6.1 The discriminating test: irreducibility

An artifact is a **derived view** if deleting it and re-running its producer reproduces it. It is **state** if that is impossible. Applied to every corpus register:

| Artifact | `generated_at` stamp | Recomputable from (tree + identity)? | Category |
|---|---|---|---|
| `00-BOOK/DATA/id-ledger.json` | **absent** | **NO** | **GOVERNED EVOLUTION STATE** |
| `00-BOOK/DATA/artifacts.json` | present | yes | derived view |
| `00-BOOK/DATA/change-ledger.json` | present | yes | derived view |
| `00-BOOK/DATA/relationships.json` | present | yes | derived view |
| `00-BOOK/DATA/volumes.json` | present | yes | derived view |
| `00-BOOK/DATA/control-tower.json` | present | yes | derived view |
| `00-BOOK/DATA/certification.json` | present | yes | derived view |

**`id-ledger.json` is the only one of the seven with no generation stamp.** That is not a formatting accident. `_stamp_eq_json(path, obj, stamp_keys=("generated_at",))` exists specifically so derived views can be rewritten idempotently by neutralising their own stamp. A document with no stamp is not participating in that mechanism, because it is not a regeneration.

`allocate()` (`ukb.py:876-899`) proves the irreducibility mechanically — three independent sources of unrecoverable information:

```python
seq = ledger["category_seq"].get(category, 0) + 1   # depends on ARRIVAL ORDER
page_start = ledger["page_cursor"] + 1              # MONOTONE CURSOR
"first_seen": _now(),                               # WALL CLOCK — unrecoverable
```

Delete `id-ledger.json`, re-run `ukb build`: different identifiers, different page spans, different timestamps. **The identity ledger is accumulated history, not a projection of the tree.**

### 6.2 Proposed category definition

> **GOVERNED EVOLUTION STATE** — an artifact that records the accumulated, append-only consequence of past evolution events, is not reproducible from present repository content, and therefore may be mutated only by an explicit governed evolution transaction. It is neither authored (no human wrote its content) nor generated (no producer can recompute it).

Three properties, all three required: **irreducible · append-only · consequence-of-events**.

### 6.3 Membership, measured

| Candidate | Irreducible | Append-only | Verdict |
|---|---|---|---|
| **Universal Identity Ledger** `00-BOOK/DATA/id-ledger.json` | yes | yes (`first_seen` frozen, never reissued, retired-but-retained) | **MEMBER — the canonical case** |
| **Object Birth Ledger** `00-MASTER/UOBC-000001/birth-ledger.json` | yes (records birth events) | yes (`append`/`supersede`, refuses overwrite) | **MEMBER** |
| **UKDA knowledge store** `knowledge/canonical-knowledge.json` | yes (authored + `supersedes`/`superseded_by` chains) | yes | **MEMBER** (authored-accumulated hybrid) |
| **Artifact Registry** `artifacts.json` | no | no (full rewrite each build) | derived view |
| **Lineage Ledger** `change-ledger.json` | no — self-declared "regenerated deterministically each transaction; **NOT** an append-only source of truth" | no | derived view |
| **Evolution Registry** | — | — | **DOES NOT EXIST.** UAUE refuses one by declaration: "no corpus serial is consumed and **no registry is written**" |
| `00-MASTER/UAUE-000001/UAUE-EVOLUTION-HISTORY.json` | no — carries `projection_of`, byte-replay-compared | n/a | derived projection |
| **Certification Ledger** `engine/universal_certification/audit.py` | yes (hash-chained) | yes | **MEMBER — but not persisted** (§6.4) |

### 6.4 A second, separate gap: append-only ledgers that are never persisted

Three engines implement hash-chained append-only ledgers with full `to_document()` / `from_document()` round-trips:

- `engine/nucleus/lineage.py::LineageLedger` — schema `ucos-universal-lineage-ledger`, `is_intact()` re-derives every digest and back-link
- `engine/uckp/evolution.py::EvolutionLedger` — Article-14 cycle numbering, `from_document` replays every record through `append`
- `engine/universal_certification/audit.py::CertificationAuditLedger` — hash-chained certification audit

**None is written to any tracked file.** A repository-wide search for their schema tokens across all `*.json` returns nothing. They are constructed in memory, per run, from other sources.

Consequence: the repository owns correct append-only ledger *machinery* and persists **no** append-only ledger except `id-ledger.json` — and `id-ledger.json` is the one nothing governs. The two gaps are mirror images.

---

## 7. Updated responsibility map — seven dimensions

| Artifact | 1 Authority owner | 2 Mutation authority | 3 Read authority | 4 Lifecycle phase | 5 Temporal behaviour | 6 Identity ownership | 7 Append-only |
|---|---|---|---|---|---|---|---|
| `id-ledger.json` | UMB-IMP-001 (declared by UMB-003 §2) | **UNGOVERNED** — no mutation class claims it | UGA, UIS-001, ukbx, 10 `input_closure`s | Registry Activation | wall-clock `first_seen`, frozen at mint | **owns the REPOSITORY_OBJECT plane** | **YES** |
| `artifacts.json` | UMB-IMP-005 (declared by UMB-005 §2) | `ukb.py cmd_build` | UGA, UIS-001, twin, portal | Registry Activation | `generated_at` stamp, neutralised | none — carries ids | no |
| `change-ledger.json` | UMB-IMP-003 | `ukb.py cmd_build` (`build_change_ledger`) | ukb evolve, intel | Observation | ISO-8601 **UTC hard-coded** (`_now()`) — contradicts CMG-000002 §3.1 | none | no |
| `relationships.json` / `volumes.json` / `control-tower.json` | UMB-IMP-002/005 | `ukb.py cmd_build` | twin, portal, graph | Observation | `generated_at` | none | no |
| `birth-ledger.json` | UOBC-000001 | `engine/object_birth/ledger.py` (`append`/`supersede`) | birth gate | **Identity Assignment** — before materialisation | caller-supplied temporal coordinate, clock-free engine | binds URN → birth facts | **YES** |
| `knowledge/canonical-knowledge.json` | UKDA (`engine/knowledge/`) | `engine/knowledge/store.py` copy-on-write | closure engine, intelligence | Lifecycle Binding | `created` / `updated` | `cko_id` (hand-assigned, unjoined to `deterministic_id`) | **YES** |
| `LineageLedger` (in memory) | UCOS-NUCLEUS-001 | `record()` | `lineage_of`, `orphans`, `unrecorded` | Lineage Update | **no clock** — insertion order only | subject_id reference | **YES** |
| `EvolutionLedger` (in memory) | UCKP Article 14 | `append()` | `from_document` replay | Evolution Cycle | integer `cycle`, non-terminal | none | **YES** |
| `CertificationAuditLedger` (in memory) | UCOS-EPIC-006 | `CertificationPipeline.run()` | outcome | Certification | audit event order | `UCOS-UCERT-…` | **YES** |
| `UAUE-EVOLUTION-HISTORY.json` | UAUE-000001 | `--render` only | `--replay` byte comparison | Evolution | derived from declaration | derived `UCOS-EVO-…`, no counter | projection |
| UGA 9 surfaces | UCOS-UGA-001 | `uga_engine.py cmd_run` | `cmd_gate`, impact engine | Observation | `commit:<sha12>` — **no wall clock** | mints UGA `by_object` plane | ledger append-only |

---

## 8. The key question: where is the single mutation authority for identity state?

**There is none. That is the governance gap, stated exactly.**

| Question | Answer |
|---|---|
| Who *reads* identity state? | UGA, UIS-001, ukbx twin/portal, 10 generated `input_closure`s, the impact engine |
| Who *writes* identity state? | `ukb.py::cmd_build` — line 945 `allocate()`, line 1242 `_dump_json(LEDGER_PATH)` |
| Which authority *governs* that write? | **NONE.** `mutation-governance-boundary.json` contains no `id-ledger`, no `artifacts.json`, no `category_seq`, no `by_path`, no `mint`, no `REGISTRATION` |
| Is it a generated artifact instead? | **No.** `id-ledger.json` never appears as a `canonical_path` in `generated-artifact-registry.json` — only inside the `input_closure` of 10 *other* artifacts |
| How does UGA classify it? | `TOOLING_OBJECT`, owner `UCOS-UKB-TOOLING`, lifecycle `AUTHORED` — i.e. *mistaken for an authored input* |

The boundary register's own invariant reads **"No mutation class is ungoverned — there is no class whose `governed_by` is empty."** It holds only because corpus registration **is not a class at all**. The invariant is vacuously true for the one mutation that matters most.

**Expected answer, per the steering: an explicit governed evolution transaction.** The transaction already exists and is correctly named — `register.sh`, "REG-AUTO-001 Atomic Artifact Registration Transaction". What is missing is the *declaration* that it is the sole authority for that class, which is why anything at all — including a verification command — can invoke the mint without contradicting any declared boundary.

---

## 9. Why does `ukb build` write corpus registers? — A, B, or C

**It does all three in one function, and that conflation is the mechanical root cause.**

| `cmd_build` write | Classification |
|---|---|
| line 945 `allocate()` → `category_seq`, `page_cursor`, `by_path`, `first_seen` | **B — mutation of canonical state** (irreducible, append-only, identity-bearing) |
| line 1242 `_dump_json(LEDGER_PATH)` | **B/C — persistence of that canonical state** |
| lines 1243, 1246, 1248, 1253 → artifacts, volumes, relationships, control-tower | **A — generation of derived views** |
| line 1250 `_dump_json(CHANGE_LEDGER_PATH)` | **A — derived**, self-declared not a source of truth |

So `cmd_build` is **one command performing one canonical-state mutation and six derived-view regenerations**, with no way to request the second without also performing the first. There is no `mint=False`. That is why "regenerate the registers to check for drift" and "allocate permanent identity" are the same operation — and why a drift *check* necessarily mints.

### 9.1 The precedent: UGA already solved this

The sibling engine separates exactly these concerns, at the parameter level:

```python
# 00-MASTER/UCOS-UGA-001/uga_engine.py
def epoch1_identity(objects, ledger, mint: bool, now: str)   # line 258
def mint_observation(ledger, observer, subject, kind, mint: bool, now)  # line 464
def build(mint: bool)                                         # line 1587

def cmd_run(args):   st = build(mint=True)    # line 1865  — EVOLUTION
def cmd_gate(args):  st = build(mint=False)   # line 1891  — VERIFICATION
```

| Engine | Mint separated from projection? | Read-only path |
|---|---|---|
| `uga_engine.py` | **YES** — `build(mint: bool)` threaded through three functions | `cmd_gate` → `build(mint=False)` |
| `ukb.py` | **NO** — `cmd_build` allocates unconditionally | **none exists** |

The asymmetry is the whole defect. `verify.sh` can safely call `uga_engine.py gate` — and does, purely — precisely because UGA has `mint=False`. It cannot safely call anything in `ukb.py` that regenerates, because `ukb.py` has no such mode.

### 9.2 The repository already identified this hazard once

`ukb.py:758-768` and `:1978` record a prior correction against the *same* failure mode:

> "the append-only identity ledger can no longer **mint PERMANENT identities** for files the repository does not contain" · "every such file is named on every gate run instead of being **silently minted a permanent identity**"

That correction narrowed *which files* may be minted. It did not separate *when* minting may occur. The second half of the same fix was never applied.

---

## 10. Minimal correction proposal

Four changes. No new registry, no new identity system, no second dictionary or certificate authority, no rename of `register.sh`, no new capability.

| # | Change | Scope | Why minimal |
|---|---|---|---|
| **1** | Add `mint: bool` to `ukb.py::cmd_build` (default `True`), threaded to `allocate()`; when `False`, reuse existing ids, refuse to allocate, and regenerate derived views only | `ukb.py` | **Applies a pattern that already exists in this repository**, in the sibling engine, for this exact purpose. Not a new design. |
| **2** | Declare `CORPUS_REGISTRATION` as a mutation class in `mutation-governance-boundary.json`: `governed_by: REG-AUTO-001 → register.sh`, with `does_not_govern` naming `verify.sh` | 1 data entry | Uses the existing boundary register and its existing invariants. Converts an ungoverned mutation into a *declared* one, so the existing CAA/RIB machinery can detect a violation. |
| **3** | Give `register.sh` an observation entry that runs the read-only phases and reports gaps with remediation; keep phases 0-10 as the transaction, requiring a determination + evolution cycle id | `register.sh` | `register.sh` remains the transaction engine. It gains a mode; it is not split, renamed, or replaced. |
| **4** | Point `verify.sh:330` and `ucos-registration-gate.yml:60` at the observation entry; add a purity test asserting `./verify.sh` leaves `git status`, the identity-ledger digest and the lineage digest unchanged | 2 lines + 1 test | The verification plane stops invoking the evolution plane, and the invariant that would have caught this becomes enforced. |

**Ordering matters:** change 1 must land before change 4, because until `ukb.py` can regenerate without minting there is no read-only operation for `verify.sh` to call.

**Deliberately excluded from this proposal:** reclassifying `id-ledger.json` in UGA (`TOOLING_OBJECT` → a new class) and persisting the three in-memory ledgers. Both are real findings (§6.4, §8) but each changes object classification for existing entries and re-renders generated surfaces, so each belongs to its own determined cycle.

---

## 11. Status

| Item | Status |
|---|---|
| Third category required | **YES — GOVERNED EVOLUTION STATE**, defined §6.2, membership measured §6.3 |
| Responsibility map, 7 dimensions | **COMPLETE** — §7 |
| Single mutation authority for identity state | **NONE EXISTS** — §8. Should be `register.sh` under REG-AUTO-001, undeclared |
| `ukb build` classification | **A + B + C conflated in one function** — §9 |
| Root cause | `cmd_build` has no `mint=False`; corpus registration is an undeclared mutation class |
| Minimal correction | **PROPOSED** — §10, four changes, ordered |
| Code modified | **NONE.** `register.sh`, `ucos-registration-gate.yml` byte-identical to HEAD; `verify.sh`/`Makefile` retain only previously-approved mode work |
| Classification modified | **NONE** |
| Implementation | **AWAITING APPROVAL** |
