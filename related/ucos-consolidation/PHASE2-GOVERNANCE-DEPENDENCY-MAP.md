# PHASE 2 — GOVERNANCE DEPENDENCY MAP

| Field | Value |
|---|---|
| Phase | 2 — Governance Dependency Isolation |
| Scope | E1-F3, E-3, E-4A, RES-1, RES-2 — the five blockers Phase 1 left open |
| Objective | Determine the **minimum governance decisions** required to close them, **without making any** |
| Deliverable type | **Decision-space map. Not a design.** |
| Inputs | `PHASE0-E1-ATOMICITY-REPORT.md`, `PHASE0-E2-CORRESPONDENCE-REPORT.md`, `PHASE0-E3-CLAIM-INTEGRITY-REPORT.md`, `PHASE0-E4A-ISSUANCE-PATH-REPORT.md`, `PHASE0-GOVERNANCE-INDEPENDENT-DETERMINATION.md`, `PHASE05-GOVERNANCE-INDEPENDENT-REMEDIATION.md`, `PHASE1-GOVERNANCE-INDEPENDENT-IMPLEMENTATION-REPORT.md` |
| Phase 1 standing | Treated as **authoritative** — all twelve governance-independent defects are remediated |
| Method | Source reading against the **post-Phase-1** working tree + executed probes; every characterization carries a `file:line` reference or a probe transcript |
| Live ledger | **byte-identical throughout** — `sha256 8471e709…c20b`, `git status --porcelain 00-BOOK/DATA/` empty |
| Governance content | **NONE.** No permit issuer, permit record, audit event, audit schema, mutation semantics, issuance semantics, ratification semantics, temporal legitimacy semantics or authority structure is created, defined or recommended. No governance outcome is selected, ranked or preferred. |
| FD-1 / FD-2 / FD-3′ / FD-4 / FD-5 | **Not answered. Not approached.** |

---

## 0. Scope discipline and prohibition compliance

Every section below is written so that it states **what is true of the code** and **what the
admissible answer space is**, and never which answer to take. Where enumeration of an option
could be mistaken for advocacy, the option is stated together with the answers under which it
becomes *impossible*, so that the enumeration is symmetric and carries no direction.

| Prohibition | Compliance |
|---|---|
| create a permit issuer | No file writes the register. `00-BOOK/DATA/allocation-permits.json` still does not exist (probe P2-5). |
| create permit records | The three register files written during probing were `tempfile.mkdtemp()` fixtures, deleted with their temp dirs. |
| create audit events | No event was emitted, defined or persisted. `audit_event` / `emit_event` token count in `ledger_authority.py`: **0** (probe P2-6). |
| create audit schemas | §5 enumerates candidate event-content dimensions as *questions*, never as a schema. No field list is proposed as required. |
| define mutation semantics | §5 enumerates seven candidate mutation universes and refuses to select. The repository's existing declared classes are *quoted*, not extended. |
| define issuance semantics | §4 states what the code consumes and what it cannot consume. It defines no issuance act. |
| define ratification semantics | Not addressed anywhere. Where a decision would be a ratification, it is named as such and left open (GQ-21, GQ-25). |
| define temporal legitimacy semantics | `expires_at` is characterized as *implemented and unpopulated*; no expiry policy, duration or clock authority is proposed. |
| define authority structures | No actor, issuer, role, signer or separation-of-duty arrangement is proposed. Existing actor strings are quoted from call sites. |
| recommend governance outcomes | No section contains a recommendation, preference, ranking by desirability, or "should". Orderings that appear are **dependency** orderings derived from code, and are labelled as such. |

### 0.1 What changed under this phase's feet, and why the baseline is restated

Phase 1 modified `ledger_authority.py` from 593 to 933 lines. **Every line reference in the
Phase 0 reports is therefore stale.** All references in this document are to the post-Phase-1
working tree. The mapping for the symbols this phase depends on:

| Symbol | Phase 0 reference | Post-Phase-1 reference |
|---|---|---|
| `IDENTITY_MAPS` | `:71-77` | `:91-97` |
| `NON_ALLOCATION_KEYS` | `:83-85` | `:103-116` (now includes `history`) |
| `_identifier_index` | `:112-119` | `:142-149` |
| `assert_append_only` | `:121-170` | `:271-383` |
| `allocation_report` | `:172-221` | `:386-434` |
| `format_report` | `:223-249` | `:437-473` |
| `_NoAllocation` docstring | `:287`, `:293-296` | `:514-529`; the *"must not be issuable"* claim is at **`:519`** |
| `manifest_digest` | `:316-336` | `:548-568` |
| `preimage_digest` | `:338-347` | `:570-577` |
| `load_permit_register` | `:376-399` | `:608-631` |
| `plan` | `:416-430` | `:648-661` |
| `_verify_permit` | `:432-543` | `:664-804` |
| `commit` | `:546-593` | `:841-933` |

---

## 1. Remaining blocker inventory

*(Required deliverable 1.)*

Phase 1 §6.2 records five. All five were re-verified open against the post-Phase-1 tree by
execution. **No blocker dissolved; two acquired newly-measured legs** (§1.2).

| ID | Blocker | Class | Re-verified how | Status |
|---|---|---|---|---|
| **E1-F3** | A permit re-validates after the ledger is restored to its pre-image. Spent-ness is derived from mutable state (`:570-577`), so restoring the bytes un-spends the authorization. | GOVERNANCE-DEPENDENT (remedy) | Probe **P2-1**: commit → immediate replay REFUSED → out-of-band byte restore → **the same permit `P-1` ACCEPTED again** | **OPEN** |
| **E-3** | `UGA-INV-10 EVERY_MUTATION_HAS_AUDIT_EVENT` is a tautology in the leg it names (`audited ≡ set(by_object.keys())`) and a verbatim duplicate of `UGA-INV-01` in the leg that discriminates. | GOVERNANCE-DEPENDENT (remedy) | Probe **P2-10**: `UGA-INV-01 FAIL measured=6804 violations=27`; `UGA-INV-10 FAIL measured=5207 violations=27`; **identical violation sets `True`**; `audited == set(by_object) True` (5374 ≡ 5374) | **OPEN** |
| **E-4A** | No production path creates, appends to, updates or persists the permit register. Consumption is complete; issuance does not exist. | GOVERNANCE-DEPENDENT (remedy) | Probe **P2-5**: register absent; against a real allocating manifest measured from the live ledger, all three admissible `permit` values REFUSED | **OPEN** |
| **RES-1** | A permit binds a **six-field projection**, not the document. Distinct documents against one pre-image share one `manifest_digest`, so a permit issued for one authorizes the others. | GOVERNANCE-DEPENDENT (remedy) | Probes **P2-2, P2-3, P2-4, P2-7, P2-8** — five distinct unbound dimensions, each with a forged document persisted under a valid permit | **OPEN, WIDER THAN RECORDED** |
| **RES-2** | `_verify_permit` does not refuse a permit over an all-empty manifest, while `_NoAllocation`'s docstring (`:519`) states such a permit *"must not be issuable"*. | GOVERNANCE-DEPENDENT (remedy) | Probe **P2-4**: the empty-manifest digest is **one value** shared by every non-allocating mutation; a permit for a `history` append authorized a different append **and** a `version`/`discovered_volumes` rewrite | **OPEN, WIDER THAN RECORDED** |

```
TOTAL REMAINING BLOCKERS ............................. 5
  requiring a governance answer before remedy ........ 5
  closable by implementation alone ................... 0
  dissolved under Phase 2 examination ................ 0
  newly measured legs added to existing blockers ..... 4   (RES-1 ×3, RES-2 ×1)
  new independent blockers discovered ................ 0
```

### 1.1 Blockers whose *diagnosis* required no governance answer, restated

All five are defects under **every** assignment to FD-1…FD-5, exactly as Phase 0 §5 recorded.
Phase 2 changes nothing about that: it characterizes their **remedy** space. The distinction
Phase 0 drew — governance-independent *diagnosis*, governance-dependent *remedy* — is the axis
this entire document sits on.

### 1.2 The four newly-measured legs

These are not new blockers. They are dimensions of RES-1 and RES-2 that the Phase 0.5
derivation named in summary form or not at all, and which this phase measured individually
because the decision surface depends on the exact list.

| Leg | Statement | Probe | Previously recorded? |
|---|---|---|---|
| **RES-1-L3** | The **key** that receives a newly allocated identifier is outside the digest. `allocated` is a sorted list of identifier *values* (`:398-400`), never key→identifier pairs. A permit to allocate `UCOS-OBJ-000002` to `engine/legit.py` authorizes allocating it to `totally/other/path.py`. | **P2-7** | **No.** Phase 0.5 §F.4 named record bodies, `history` content and `version`/`discovered_volumes`; not the key set. |
| **RES-1-L4** | The **identifier↔key assignment** among several new allocations is outside the digest. Swapping two new identifiers between two new keys leaves the digest identical. | **P2-3** | No. |
| **RES-1-L5** | A **new top-level key whose value is not a dict** escapes `unmeasured_maps` entirely — the scan is `isinstance(v, dict)` (`:419`). A list- or scalar-valued rogue key is invisible to `allocating` and to the digest. Dict-valued keys *are* caught. | **P2-8** | No. |
| **RES-2-L2** | The empty-manifest digest is a **single universal value** for a fixed `(actor, pre-image)`. `history`-only appends, `version` rewrites and `discovered_volumes` rewrites all produce it, verified equal on both a fixture and the **live** ledger. One such permit authorizes the entire class. | **P2-4, P2-5** | Recorded for `history` pairs only (*"two different `history`-only appends … produce the same `manifest_digest`"*); not as a cross-key universal. |

### 1.3 One narrowing Phase 1 produced that changes E1-F3's precondition

Phase 0 listed the in-band restore primitive: E1-F4's record-body rewrite could restore a
pre-image without any VCS operation. **R-4 closed that.** Measured (probe P2-1 continuation):

```
restore via the chokepoint : REFUSED — by_object: entry 'b.py' would be REMOVED
                                      (identity 'UCOS-OBJ-000002' is permanent …)
out-of-band restore        : ACCEPTED (a plain file write; commit() is not involved)
  -> preimage_digest matches the permit again : True
  -> manifest_digest  matches the permit again : True
```

E1-F3's precondition is therefore now **exclusively out-of-band**: `git checkout`, `git
revert`, a stash pop, a backup restore, or any direct write. `R-2` (pre-write byte re-check)
and `R-3` (`flock`) do not address it, because both operate *inside* `commit()`'s own window
and a restore happens between two invocations. This is a factual narrowing of the attack
surface, not a reduction of the blocker.


---

## 2. Dependency graph

*(Required deliverable 2.)*

Three graphs are distinct and are kept distinct, because conflating them is what produces
false sequencing claims: **(a)** what activates what, **(b)** what decision gates what
remedy, **(c)** what remedy invalidates what artifact.

### 2.1 Activation graph — what becomes exercisable when

```
                          ┌──────────────────────────────────────────┐
                          │  E-4A  no issuance path                  │
                          │  permit is mandatory, no default (:841)  │
                          │  register absent  →  EVERY permit value  │
                          │  refused  →  no production write reaches │
                          │  `writer` at all                         │
                          └───────────────┬──────────────────────────┘
                                          │ resolving E-4A activates,
                                          │ simultaneously and only then:
                    ┌─────────────────────┼─────────────────────┐
                    ▼                     ▼                     ▼
         ┌──────────────────┐  ┌────────────────────┐  ┌──────────────────┐
         │ E1-F3            │  │ RES-1              │  │ RES-2            │
         │ replay-after-    │  │ 5 unbound          │  │ empty-manifest   │
         │ restore          │  │ dimensions of the  │  │ permit authorizes │
         │ (needs ≥1 permit │  │ authorized object  │  │ a whole class     │
         │  to have existed)│  │ (needs a permit)   │  │ (needs a permit)  │
         └──────────────────┘  └────────────────────┘  └──────────────────┘

         ┌──────────────────────────────────────────────────────────────┐
         │ E-3   INDEPENDENT of E-4A. Measured today, fails today,      │
         │       27 violations, identical set to UGA-INV-01. Neither    │
         │       activated nor suppressed by any permit decision.       │
         └──────────────────────────────────────────────────────────────┘
```

Evidence for the activation edge: `permit` is a required parameter with no default
(`:841`), and probe **P2-5** shows all three admissible values refused against a real
allocating manifest measured from the live ledger. Nothing reaches `writer` (`:895`), so
E1-F3, RES-1 and RES-2 are **latent-not-absent** — exactly as `PHASE0-E2-CORRESPONDENCE-REPORT.md`
E2-F7 recorded for the twelve now-closed defects.

E-3's independence is measured, not argued: probe **P2-10** ran
`uga_engine.build(mint=False)`, which never calls `LA.commit`, and both invariants failed
with 27 violations. No permit exists, and the defect is live.

### 2.2 Decision graph — which governance answer gates which remedy

```
GQ-1  is authorization consumed by use? ───────────────┬──────► E1-F3 remedy
GQ-3  is ledger restoration legitimate? ───────────────┤
GQ-4  is the use-record itself governed state? ────────┘
                     │
                     └── shares a regress-termination question with ──┐
                                                                       │
GQ-6  who may issue? ──────────────────────────┬──────► E-4A remedy ◄──┘
GQ-7  what does issuance attest? ──────────────┤
GQ-8  is the register itself governed state? ──┤
GQ-10 what ends a permit's validity? ──────────┤
GQ-13 must the register be authenticated? ─────┘
                     │
                     ├── GQ-22 what must a permit BIND? ─────► RES-1 remedy
                     │        (projection | document | bytes)
                     │        ▲
                     │        └── GQ-23 must the approval object be human-reviewable?
                     │
                     └── GQ-25 is an empty-manifest permit issuable? ──► RES-2 remedy
                              ▲
                              └── GQ-26 what authorizes a non-allocating mutation?

GQ-15 what is a mutation (subject-class | act)? ──┬──► E-3 remedy
GQ-17 what must an audit event contain? ──────────┤
GQ-18 must an event be independently sourced? ────┤
GQ-19 must events be durable and tracked? ────────┤
GQ-20 is the invariant NAME authoritative? ───────┘
```

**Four edges are hard, in the sense that the dependent remedy cannot be specified at all
until the antecedent is answered.** Each is derived from code, not from judgment:

| Edge | Why it is hard |
|---|---|
| `GQ-22 → RES-1` | `manifest_digest`'s input set (`:548-568`) *is* what a permit binds. Changing the remedy without answering GQ-22 means choosing the binding by implementation accident. |
| `GQ-25 → RES-2` | Both admissible answers are self-consistent and produce **opposite** code (add a refusal, or delete the docstring claim at `:519`). No implementation is derivable from the current source, because the source contains both positions. |
| `GQ-1 → E1-F3` | If authorization is not consumed by use, E1-F3 is not a defect but a property, and its "remedy" is a documentation correction. If it is consumed, a use-record is required and GQ-4 opens. |
| `GQ-15 → E-3` | The measurable set is a pure function of the mutation universe chosen (§5). Seven candidate universes produce seven different measurements with no common refinement. |

### 2.3 Invalidation graph — what a remedy breaks

Derived from Phase 1 §4.2's outbound constraint and from this phase's measurements.

```
RES-1 remedy (widen what a permit binds)
    ├─► invalidates EVERY manifest_digest  ──► every issued permit becomes unverifiable
    │                                          (harmless TODAY: zero permits exist — P2-5)
    ├─► changes what plan() must emit      ──► changes what an issuer transcribes (:648-661)
    └─► must therefore precede or accompany E-4A, never follow it
                                               (same shape as Phase 0.5 §D.3's R-5a rule)

RES-2 remedy (refuse empty-manifest permits)
    └─► removes the ONLY authorization path for the non-allocating-mutation class
        {history append, version change, discovered_volumes change}
        because R-9 (:696-707) already refuses those under NO_ALLOCATION
        ──► produces a second total block of the same shape as E-4A, unless GQ-26 is
            answered in the same act

E-3 remedy (replace or re-name UGA-INV-10)
    ├─► 58 files reference `UGA-INV-10` (measured before this report; 59 with it)
    ├─► `uga-declaration.json` declares it `fails_closed: true` among 10 declared invariants
    ├─► `cmd_gate` (:2125-2161) blocks on EVERY failing invariant, with no carve-out
    └─► ≥6 historical determinations cite INV-01/INV-10 counts as independent signals;
        E-3 established they are one finding double-counted

E1-F3 remedy (record use)
    └─► if the use-record is a new tracked file, it is an anonymous UCOS-UGA-001 object
        requiring an identity, requiring an allocation, requiring a permit, requiring a
        file — the regress `ledger_authority.py:499-506` already documents for the
        register itself and terminates at ONE file
```

---

## 3. Work Item P2-A — E1-F3 decision surface

> Determine exactly which governance questions must be answered before permit replay can be
> closed.

### 3.1 Current behavior, exactly

| Aspect | Behavior | Source |
|---|---|---|
| Where spent-ness lives | Nowhere. It is **derived** from the comparison `permit["preimage_digest"] != manifest["preimage_digest"]`. | `:742-749` |
| The design intent, stated in source | *"performing the allocation changes the pre-image, so recomputing this value afterwards no longer matches the permit and the same permit cannot be replayed. No spent-permit registry is required, and none is created — spent-ness is DERIVED from two artifacts that are already committed."* | `:570-577` |
| The refusal message's own claim | *"it has already been spent, or the ledger moved since issuance"* — the message cannot distinguish the two cases, because one comparison produces both. | `:746-747` |
| Any use record | **None.** No code marks, counts or consumes a permit. `single_use` does not occur in the module (probe P2-6). | whole file |
| Whether `single_use` is honoured | **No.** It appears in the register shape documented by `PHASE0-E4A-ISSUANCE-PATH-REPORT.md:35` and is written by the test fixture `platform/tests/test_ledger_authority.py:82`; `_verify_permit` never reads it. | probe P2-6 |
| Effect of restoring the pre-image | The permit becomes valid again. Both digests match. | probe **P2-1** |

Probe P2-1 transcript:

```
commit #1            : PERMIT {'by_object': ['UCOS-OBJ-000002']} bytes_changed True
immediate replay     : REFUSED  -> permit 'P-1' refused — 2 binding(s) failed
preimage restored    : True
REPLAY AFTER RESTORE : ACCEPTED PERMIT {'by_object': ['UCOS-OBJ-000002']}
single_use in ledger_authority.py: False
```

Two bindings fail on the immediate replay — `manifest_digest` **and** `preimage_digest` —
because after the first commit the proposed document equals the on-disk document, so the
measured manifest is empty and its digest differs too. Both recover together on restore.
This matters for the decision surface: **there is exactly one state variable behind both
bindings**, and it is the file the permit authorizes writing.

### 3.2 The source locations that depend on the answer

| # | Location | What it does today | What an answer determines |
|---|---|---|---|
| L1 | `:570-577` `preimage_digest` + its docstring | Defines spent-ness as a derived property and states that no registry is required | Whether the docstring is a correct design statement or a false claim |
| L2 | `:742-749` the pre-image binding in `_verify_permit` | The only replay control | Whether this check is sufficient, or one leg of two |
| L3 | `:664-804` `_verify_permit`'s return contract | Returns the permit dict; the caller records `permit_id` in the report and nothing else | Whether verification must have a side effect (recording use), which changes it from a pure function to a writer |
| L4 | `:841-933` `commit()`'s body, under the lock | Records `report["permit_id"]` in the returned report, which no caller persists | Whether the report must become durable |
| L5 | `:608-631` `load_permit_register` — the register's single access point, read-only | Reads | Whether the register acquires a write path (this is E-4A's surface too — the two blockers share this line) |
| L6 | `00-BOOK/DATA/id-ledger.json` as a **tracked** artifact | `git ls-files` confirms tracked; listed at X-4 in the protected-area register (`.github/workflows/ec1-ci.yml:109-111`) | Whether VCS restoration of this path is a legitimate operation |

### 3.3 Every technically-valid implementation path

Enumerated by mechanism, with no ordering and no preference. "Valid" means: implementable
against the current code, and it closes the replay property. Each carries the governance
answer it presupposes.

| Path | Mechanism | Presupposes | Consequence measured or derived |
|---|---|---|---|
| **A1 — spent-register** | A second file recording consumed `permit_id`s, appended by `commit()` under the existing lock | GQ-1 = *consumed*; GQ-4 answered (the record is or is not governed state) | A new tracked file is an anonymous object → identity → permit → file. The regress is documented at `:499-506` and terminated there at one file; a second file re-opens it. |
| **A2 — mark in the register** | `commit()` mutates the permit record in place (`spent_at`, `uses`) | GQ-1 = *consumed*; GQ-8 = the register is writable by the enforcer | Makes `commit()` a writer of the authorization artifact it enforces. `load_permit_register` (`:608-631`) becomes read-write; the enforcer/issuer separation stated at `:490-497` (*"commit() ENFORCES an authorization it does not DECIDE"*) is materially affected. |
| **A3 — use-record inside the ledger** | A `permits_used` key in `id-ledger.json` | GQ-1 = *consumed* | **Does not close the property.** A restore restores the ledger *including* the use-record, so both digests and the use-record revert together. Derived from `preimage_digest` covering the whole document (`:577`). Listed because it is the intuitive path and it is provably insufficient. |
| **A4 — monotone external counter** | A per-clone monotone sequence (the mechanism `governance_telemetry.append_audit` already implements, `:133-160`) consulted as a nonce | GQ-1 = *consumed*; GQ-19 = the record need not be tracked | `GOVERNANCE_DIR = .runtime/governance` and `.runtime/` is gitignored (`.gitignore:12`). The record is per-clone: a fresh clone has no memory, so replay is closed locally and open globally. |
| **A5 — bind to an unrepeatable external state** | Require `head` (already implemented, `:751-762`) and treat HEAD as non-recurring | GQ-3 = restoration does not restore history; GQ-12 = the head binding is mandatory rather than optional | Narrows but does not close: `git revert` produces a *new* head, but a restore *plus* re-issuance at the new head replays the same allocation. Also couples every permit to a commit, so any commit between issuance and use invalidates it. |
| **A6 — forbid restoration** | Treat out-of-band restoration of the ledger as prohibited and detect it (e.g. a monotone marker checked at `commit()` entry) | GQ-3 = restoration is illegitimate | Requires a monotone artifact, which is A1/A4 again. The prohibition alone is unenforceable in code because the restore happens outside every code path this repository controls. |
| **A7 — expiry only** | Populate `expires_at` (already implemented, `:785-797`) so the replay window is bounded in time | GQ-10 answered; GQ-1 = *not consumed*, only time-bounded | Bounds the window; does not close the property. Replay inside the window is unaffected. Requires a clock authority — which is the temporal-legitimacy question this phase may not touch. |
| **A8 — no change; correct the claim** | Delete or qualify the "cannot be replayed" statement at `:570-577` | GQ-1 = *not consumed* | E1-F3 stops being a defect and becomes a documented property. This is a **source change with no control change**, and it is a technically valid closure of the *discrepancy* — which is what E1-F3 records. |

### 3.4 Which paths become impossible under each answer

The load-bearing table. Read as: given the answer in the row, the paths in *impossible* cannot
be built, for the reason given.

| Question | Answer | Paths that survive | Paths that become **impossible** | Reason (source) |
|---|---|---|---|---|
| **GQ-1** is authorization consumed by use? | **NO — reusable** | A7, A8 | A1, A2, A3, A4, A6 | Each exists only to record consumption. With no consumption, a use-record has nothing to record. |
| | **YES — single-use** | A1, A2, A4, A6 | **A8** (the claim would then be a false claim, not a design), **A3** (provably insufficient), **A7** alone (time-bounding is not consumption) | A3's insufficiency is derived from `preimage_digest` covering the whole document (`:577`). |
| | **YES, bounded reuse (n uses / a window)** | A1, A2, A4, A7 | A8, A3, A6 | Requires a count, hence a record. |
| **GQ-3** is restoring the ledger legitimate? | **YES, freely** | A1, A2, A4 | **A5, A6** | A5 and A6 both assume the pre-image is not reachable twice. |
| | **NO — prohibited** | A6, A5, A1, A2, A4 | none *additional*, but A8 becomes inconsistent with the prohibition | A prohibition with no detector is a policy, not a control; detection requires A1/A4/A6. |
| | **YES, but only by a named authority** | A1, A2, A4 | A5, A6 as *sufficient* controls | The restore is legitimate, so the control must be use-recording, not restore-prevention. |
| **GQ-4** is the use-record itself governed state? | **YES — it needs authorization** | A2 (uses the existing single register), A4 (untracked, hence arguably outside), A3 (inside the already-governed ledger) | **A1** | A1's new tracked file needs an identity → a permit → a file. `:499-506` terminates that regress at one file; A1 restarts it. |
| | **NO — it is operational telemetry** | A1, A4 | none | The `.runtime/` precedent (`.gitignore:12`) exists for exactly this classification. |
| **GQ-5** must authorization memory survive a fresh clone? | **YES** | A1, A2, A3 | **A4** | `.runtime/` is gitignored; a fresh clone starts at `seq = 1` (`governance_telemetry.py:44-52`). |
| | **NO — per-clone is sufficient** | A1, A2, A4 | none | — |

### 3.5 The minimum decision set for E1-F3

**Two answers are strictly necessary; a third becomes necessary only under one branch.**

```
NECESSARY  GQ-1  is an authorization consumed by use?
                 (without it, no path is selectable — A8 and A1 are opposite answers to one question)
NECESSARY  GQ-3  is restoring the identity ledger to a prior state a legitimate operation?
                 (determines whether the control belongs at use-recording or at restore-detection)
CONDITIONAL GQ-4 is the record of use itself governed state?
                 — required only if GQ-1 ≠ NO. Under GQ-1 = NO there is no record.
CONDITIONAL GQ-5 must authorization memory survive a fresh clone?
                 — required only if GQ-1 ≠ NO and A4 is admissible.
```

No answer is given. The size of the decision is: **2 mandatory questions, 2 conditional, 8
enumerated paths, 0 selected.**


---

## 4. Work Item P2-B — E-4A decision surface

> Determine what information an issuer would need, what a permit currently binds, what is not
> currently bound. Construct a complete issuance dependency graph.

No issuer is created. No permit is created. Who may issue is not defined.

### 4.1 What information an issuance act would need — derived from what the verifier consumes

`_verify_permit` (`:664-804`) is the complete specification of what a permit must carry to
survive verification. Every field below is derived from a line that reads it, so this list is
**exhaustive and non-speculative**: a permit carrying exactly these fields verifies; one
missing a mandatory field is refused.

| Field | Mandatory? | Consumed at | Where the value must come from | Producible today? |
|---|---|---|---|---|
| `permit_id` | **yes** | `:715-721` (resolution; zero matches and >1 match both refuse) | Invented by the issuance act. Must be unique *within the register* — ambiguity is refused, not resolved. | Yes — any unique string. No format is enforced. |
| `actor` | **yes** | `:728-732` | Must equal the `actor=` string the calling tool passes. Three exist in production: `"UMB-IMP-001 :: ukb.py build --mint"` (`ukb.py:1287`), `"EXEC-REG-001 :: ukb.py exec declare"` (`ukb.py:2403`) and its idempotent variant (`:2382`), `"UCOS-UGA-001 :: uga_engine.py run"` (`uga_engine.py:2098`). | Yes — transcribed from `plan()`'s report line. |
| `manifest_digest` | **yes** | `:734-740` | `plan()["digest"]` | Yes — `ukb build --mint --plan` and `uga_engine run --plan` print it. |
| `preimage_digest` | **yes** | `:742-749` | `plan()["preimage_digest"]` | Yes — printed. |
| `head` | optional; **binding when non-null** | `:751-762` | `plan()["head"]`; `null` declines the binding; a bound head with an undeterminable HEAD refuses | Yes — printed. |
| `scope.maps` | optional | `:767-776` | The map names in `plan()["allocated"]` | Yes — derivable from the report line (`[by_path+9]`). |
| `scope.max_allocations` | optional | `:777-783` | `plan()["total_allocations"]` | Yes — printed in the report line. |
| `expires_at` | optional | `:785-797` | **Nothing in the repository produces this value.** No default, no policy, no clock authority. | **No** — it is the one field with no producible source. |
| `single_use` | **never read** | — | — | Field is inert. |
| `issuer`, `signature`, `issued_at`, `revoked`, `uses` | **never read** | — | — | Fields do not exist in the verifier's vocabulary. |

Probe **P2-6**, source-derived, confirming consumption:

```
permit.get('permit_id')       consumed: True     permit.get('single_use')  consumed: False
permit.get('actor')           consumed: True     permit.get('issuer')      consumed: False
permit.get('manifest_digest') consumed: True     permit.get('signature')   consumed: False
permit.get('preimage_digest') consumed: True     permit.get('issued_at')   consumed: False
permit.get('head')            consumed: True     permit.get('revoked')     consumed: False
permit.get('scope')           consumed: True     permit.get('uses')        consumed: False
permit.get('maps')            consumed: True
permit.get('max_allocations') consumed: True
permit.get('expires_at')      consumed: True
```

### 4.2 What a permit currently binds

Exactly the six inputs to `manifest_digest` (`:548-568`), plus four independently-verified
bindings. Stated as the equivalence relation, because that is what a digest is:

> For a fixed pre-image `B` and actor `A`, two proposed documents `D` and `D′` are
> **indistinguishable to a permit** iff their six manifest fields agree:
> `actor`, `allocated`, `counter_advances`, `cursor_advances`, `unmeasured_maps`,
> `total_allocations`.

| Bound | Binding | Strength |
|---|---|---|
| the actor string | `:728-732` | exact equality |
| the **set of new identifier values** per map | `allocated`, built at `:396-400` | exact, but value-only — no keys |
| `category_seq` transitions | `counter_advances`, `:403-408` | exact `[old, new]` pairs |
| `page_cursor` / `volume_seq` transitions | `cursor_advances`, `:410-414` | exact `[old, new]` pairs |
| the names of unclassified **dict-valued** top-level keys | `unmeasured_maps`, `:417-420` | names only |
| the total allocation count | `:422` | exact integer |
| the whole pre-image, as a digest | `preimage_digest`, `:570-577` | exact — of the entire `before` document |
| repository HEAD | `:751-762` | exact, when the permit elects it |
| declared maps / allocation cap | `:767-783` | superset / upper bound |
| an expiry instant | `:785-797` | deadline, when populated |

Note the asymmetry, because it is the whole of RES-1: **the pre-image is bound in full; the
post-image is bound only through the six-field projection.**

### 4.3 What is not currently bound — exhaustive, by construction

Because `manifest_digest` is a pure function of six named fields, the unbound space is
*everything not determined by those six given the pre-image*. Enumerating it is therefore a
derivation, not a search. Five dimensions, each measured:

| # | Unbound dimension | Probe | Observed |
|---|---|---|---|
| **U1** | The **record body** of a newly allocated identity | **P2-2** | `digest(honest) == digest(forged)` → `True`. Permit issued for `object_class: TOOLING_OBJECT, first_seen: commit:HONEST`; the document persisted was `object_class: GOVERNANCE_OBJECT, first_seen: commit:FORGED, extra_field: "anything at all"`. `authorization=PERMIT`. |
| **U2** | The **key** a new identifier is bound to | **P2-7** | Permit for `UCOS-OBJ-000002 → engine/legit.py`; committed `UCOS-OBJ-000002 → totally/other/path.py`. Same digest, `authorization=PERMIT`, disk shows the second key. |
| **U3** | The **assignment** of identifiers among several new keys | **P2-3** | Two new keys, two new identifiers, swapped. `allocated` identical (`['UCOS-OBJ-000002','UCOS-OBJ-000003']`), digest identical, swap persisted. |
| **U4** | The **content** of `history` appends (prefix-preserving) | **P2-4** | Permit for append `APPEND-A`; committed `APPEND-B-DIFFERENT`. Accepted; disk holds `APPEND-B-DIFFERENT`. |
| **U5** | New top-level keys whose value is **not a dict**, and the **values** of `version` / `discovered_volumes` | **P2-8, P2-4** | `digest(no-op) == digest(list+scalar rogue keys)` → `True`; a permit measured for a **no-op** authorized adding `rogue_list` and `rogue_scalar`. Dict-valued rogue keys *are* caught (`unmeasured_maps=['rogue_map']`, different digest). |

`R-4` (record-body immutability) does **not** cover U1: it freezes records that already exist,
and a permit authorizes the creation of *new* ones. Verified — `test_a_new_records_body_is_unconstrained`
is a Phase 1 regression test asserting exactly this (Phase 1 §R-4).

### 4.4 Complete issuance dependency graph

```
                     ┌───────────────────────────────────────────────┐
                     │ WORKING TREE at a fixed state                 │
                     │  (discovered documents / objects / executions) │
                     └───────────────┬───────────────────────────────┘
                                     │ the producing tool's own discovery pass
                                     │ ukb.cmd_build  |  uga_engine.build(mint=True)
                                     ▼
                     ┌───────────────────────────────────────────────┐
                     │ PROPOSED DOCUMENT `ledger`                     │
                     │  produced ONLY by the tool that will write it  │
                     └───────────────┬───────────────────────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │ ON-DISK PRE-IMAGE          │                            │
        │ 00-BOOK/DATA/id-ledger.json│                            │
        └────────────┬───────────────┘                            │
                     ▼                                            ▼
              ┌──────────────────────────────────────────────────────────┐
              │ plan(path, ledger, actor)   :648-661   READ-ONLY         │
              │ emits: digest · preimage_digest · head · report line     │
              │ docstring: "issuing a permit is a TRANSCRIPTION of this  │
              │             output rather than an independent act of     │
              │             measurement"                                │
              └──────────────┬───────────────────────────────────────────┘
                             │  ── THE MISSING EDGE ──
                             │  no tool, no template, no schema, no CLI
                             ▼
              ┌──────────────────────────────────────────────────────────┐
              │ 00-BOOK/DATA/allocation-permits.json   DOES NOT EXIST    │
              │ writers in production: 0   (only test fixture :61-87)    │
              └──────────────┬───────────────────────────────────────────┘
                             ▼
              ┌──────────────────────────────────────────────────────────┐
              │ load_permit_register :608-631  →  _verify_permit :664-804│
              │ COMPLETE, TESTED, REACHED at :884                        │
              └──────────────┬───────────────────────────────────────────┘
                             ▼
                        writer(path, ledger)  :895
```

**Four dependency properties of the graph, each measured:**

| # | Property | Evidence |
|---|---|---|
| **D-a** | The approval object is **produced by the thing being approved**. `plan()` takes the fully-built proposed document as an argument (`ukb.py:1292` passes `ledger`; `uga_engine.py:2079` passes `st["ledger"]`), so no independent party can compute a manifest without running the producing tool's discovery pass. | source |
| **D-b** | Transcription is **deterministic while the tree is still**. Two consecutive `ukb build --mint --plan` runs produced byte-identical digests: `manifest a6827d8a…fae5`, `preimage 3a2a2532…2bcf4`, `head 77798202…`. | executed, read-only |
| **D-c** | Transcription is **invalidated by a change to the discovered set, which is the git index — not the working tree**. Discovery reads `git ls-files --cached --exclude-standard` (`ukb.py:722-733, 750`), so an untracked file is not discovered. Measured: creating this report file left the digest **unchanged** (`a6827d8a…fae5` before and after, `PHASE2-GOVERNANCE-DEPENDENCY-MAP.md` shown as `??` by `git status`). `git add` of an eligible artifact is what moves the digest. | executed — see §12.3 |
| **D-d** | One `register.sh` transaction needs **one** ledger permit. Only Phase 1/10 reaches `commit()` (`register.sh:216`); Phases 0 and 2–10 are `ukb enforce`, `ukbx sync/twin/portal/validate/certify` and `ukb validate`, none of which write the ledger. The other two write paths — `uga_engine run` and `ukb exec declare` — are separate invocations with different `actor` strings, so each needs its own permit. | `register.sh:206-259` |

### 4.5 Which issuance properties are already enforced

| Property | Enforced | Where |
|---|---|---|
| A permit names one resolvable identity | **yes** — zero matches refuse (`:716-717`), duplicates refuse (`:718-722`) with *"an ambiguous authorization is no authorization"* | `:715-722` |
| The write's actor is the permit's actor | **yes**, exact string equality | `:728-732` |
| The allocation performed is the allocation approved, *within the projection* | **yes**, digest equality against a **recomputed** manifest — a caller cannot describe its own write into acceptability (`:878-880`) | `:734-740`, `:884` |
| The permit was measured against the current ledger state | **yes** | `:742-749` |
| The repository state is the one bound, when bound | **yes**, and fail-closed when HEAD is undeterminable | `:751-762` |
| The allocation touches no map outside the declared scope | **yes** | `:767-776` |
| The allocation count does not exceed the declared cap | **yes** | `:777-783` |
| A permit past its expiry is refused | **yes**, when `expires_at` is populated; a malformed instant is also refused | `:785-797` |
| An unreadable or wrongly-shaped register refuses | **yes** | `:608-631` |
| A missing register is empty, never open | **yes** | `:614-615` |
| Refusal precedes the writer | **yes** — `_verify_permit` at `:884`, `writer` at `:895` | `:841-933` |

### 4.6 Which issuance properties are impossible to enforce with the current manifest

"Impossible" means: the manifest does not carry the information the property quantifies over,
so no check written against `manifest` can decide it.

| Property | Why impossible | Missing term |
|---|---|---|
| **Single use** | The manifest is a function of `(before, after, actor, path)`. It contains no history of authorization use. | a use record — E1-F3 |
| **The permit was issued by anyone in particular** | No `issuer` field is read; no signature is verified; presence in the register *is* validity. | an issuer identity and an authentication mechanism |
| **The register itself is authentic** | `load_permit_register` (`:608-631`) checks readability and shape, never provenance or integrity. Any process that can write the file can grant authorization. | a register integrity binding |
| **Which key receives which identifier** | `allocated` holds identifier values only (`:398`). | key→identifier pairs — RES-1/U2, U3 |
| **What a new record asserts** | Record bodies are not in the digest's inputs. | a record-body binding — RES-1/U1 |
| **What a `history` append records** | `history` is in `NON_ALLOCATION_KEYS` (`:103-116`); only its prefix is checked (`:355-383`). | an append-content binding — RES-1/U4 |
| **The values of `version` / `discovered_volumes`** | In `NON_ALLOCATION_KEYS`; changes are invisible to the manifest. | RES-1/U5 |
| **That a new non-dict top-level key was not added** | `unmeasured_maps` scans `isinstance(v, dict)` only (`:419`). | RES-1/U5 |
| **That an authorization is not for "nothing"** | `_verify_permit`'s permit path never reads `total_allocations` or `allocating`. | RES-2 |
| **Revocation** | No `revoked` field is read; removing a permit from the register is the only revocation, and nothing writes the register. | a revocation mechanism |
| **Ordering between permits** | Permits carry no sequence and the register is a list whose order is never consulted. | a sequence |
| **Separation of issuer and executor** | Nothing distinguishes them. The module states the intent — *"commit() ENFORCES an authorization it does not DECIDE"* (`:490-497`) — and the enforcement of that separation is entirely social today. | an issuer identity |


---

## 5. Work Item P2-C — E-3 decision surface

> Determine every mutation universe and every audit-event universe that could reasonably
> satisfy the current claim name. For each candidate pair: measurable set, expected set,
> counterexample space, implementation impact.

No definition is selected. The invariant is not replaced.

### 5.1 The claim name, and what constrains its admissible readings

```python
# 00-MASTER/UCOS-UGA-001/uga_engine.py:1331-1335  (post-Phase-1 line numbers)
mutated = {e["path"] for e in entries if e["identity_authority"] == "UCOS-UGA-001"}
audited = {ev["object_path"] for ev in audit_events}
v = sorted(mutated - audited)
add("UGA-INV-10", "EVERY_MUTATION_HAS_AUDIT_EVENT", v, len(mutated))
```

Declared `fails_closed: true` among **10** declared invariants in
`00-MASTER/UCOS-UGA-001/uga-declaration.json`; the engine computes **30** invariants in total,
28 passing (probe P2-10). `cmd_gate` (`uga_engine.py:2125-2161`) blocks on **every** failing
invariant, with the carve-out removed and the removal justified in-source.

Three artifacts already in the repository constrain which readings are available. They are
quoted, not extended:

| Artifact | What it already fixes | Relevance |
|---|---|---|
| `00-BOOK/DATA/mutation-governance-boundary.json` | Six declared `mutation_classes` — `CONSTITUTIONAL_TRUTH`, `SOURCE`, `GENERATED_ARTIFACT`, `EXCLUSION`, `REPOSITORY_STATE`, `CORPUS_REGISTRATION` — plus a `classification_rules` section asserting resolution is **deterministic, total, unique, repository-evaluable**, over a subject domain of *"MUTATION SUBJECTS, not only paths"*. `CORPUS_REGISTRATION`'s examples name `00-BOOK/DATA/id-ledger.json (by_path allocation, category_seq, page_cursor)` explicitly. | A mutation universe over **subjects** is already declared. What is *not* declared is a universe over **acts**. |
| `00-BOOK/tools/governance_telemetry.py` | An append-only audit-log mechanism with a monotone `seq` assigned in one place (`:133-160`), three log names (`:83-86`), atomic writes (`:209-217`), and a **frozen-path guard**: `forbid_data_telemetry` (`:187-207`) makes any `*-audit.json` under `00-BOOK/DATA` a hard `TelemetryPathError`. `GOVERNANCE_DIR = .runtime/governance` (`:79`), and `.runtime/` is gitignored (`.gitignore:12`). | Audit machinery exists; its persistence location is structurally constrained and **untracked**. |
| `00-MASTER/UCOS-UGA-001/03-AUDIT-UNIVERSE.json` | A tracked 2.7 MB artifact regenerated every run, carrying the derived events with header `"authority": "NONE — DERIVED TRUTH"` and `"determinism": "No wall clock. Timestamps are ledger first_seen values."` | The current "audit universe" is a **projection**, and the determinism contract forbids a wall clock in it. |

### 5.2 Candidate mutation universes

Enumerated by what could be *measured*, each with the code that would have to supply it. `|·|`
values are measured on the current tree where computable.

| ID | Mutation universe | Element | Measurable today? | Size today |
|---|---|---|---|---|
| **M1** | Byte change to `id-ledger.json` | one write event | No — requires an occurrence record; `bytes_changed` exists per-call (`:898`) but is never persisted | unmeasurable |
| **M2** | Document-level inequality of the ledger across a write | one write event | No — same reason | unmeasurable |
| **M3** | Newly allocated permanent identifier | one identifier | **Yes** — `allocation_report["allocated"]` (`:396-400`) | 0 for a no-op; 9 (`by_path`) / 27 (`by_object`) for the currently pending plans |
| **M4** | Any change within the four `IDENTITY_MAPS` — keys *or* record bodies | one key | Partly — `assert_append_only` (`:271-383`) sees it and refuses most of it, but nothing records it | 7009 live records |
| **M5** | Each successful `commit()` invocation (act-level) | one act | No — `commit()` returns a report no caller persists (`:930`) | unmeasurable |
| **M6** | Any change to any artifact under `00-BOOK/DATA/` | one artifact write | Partly — `change-ledger.json` carries 1724 `change_events` over 1597 versioned artifacts | 1724 recorded events |
| **M7** | Content change of any governed object in the tree (content-hash drift) | one object | **Yes** — `history` in the ledger holds `{uid: [snapshot…]}`, 1628 lists, written by `ukb.record_snapshots` | 1628 |
| **M8** | `by_execution` lifecycle transitions | one transition | Partly — `lifecycle_state`, `transitions`, `last_transition_seq` are written at `ukb.py:2388-2400` but no invariant reads them | present, uncounted |

**Note on M-current.** What `UGA-INV-10` measures today is none of these. Its `mutated` set is
*live non-document discovered objects* — a static file census (5207 elements). `E-3`'s finding
stands unchanged: the measured universe contains no mutation-valued element.

### 5.3 Candidate audit-event universes

| ID | Audit-event universe | Source of events | Independently sourced from the audited state? | Durable across clones? |
|---|---|---|---|---|
| **A-current** | Derived events built from `ledger["by_object"]` (`uga_engine.py:1843-1860`) | the audited state itself | **No** — `audited ≡ set(by_object.keys())`, measured `True` | tracked, but regenerated |
| **A1** | An append-only log written by `commit()` through `governance_telemetry.append_audit` | the write act | **Yes** | **No** — `.runtime/` gitignored |
| **A2** | A new tracked append-only log under `00-BOOK/DATA/` | the write act | Yes | Yes — but `forbid_data_telemetry` (`:187-207`) forbids the `-audit.json` name there, and a new tracked file re-opens the identity regress (`ledger_authority.py:499-506`) |
| **A3** | `history` inside the ledger, treated as the audit record | content observation | **No** — it is inside the state being audited; a ledger restore reverts it | tracked |
| **A4** | Git commits as the audit record | VCS | Yes | Yes — but `first_seen` already carries `commit:…`, and `git_head` (`:581-601`) can return `None` legitimately |
| **A5** | The permit register as the audit record | issuance | Yes | Yes — **but the register does not exist** (E-4A); this pair makes E-3 depend on E-4A |
| **A6** | `change-ledger.json` `change_events` (1724 today, shape `{change_id, subject, kind, at, snapshot_seq, from, to, commit}`) | change detection | Partly — derived from artifact versions, `commit: null` on the sample | tracked |
| **A7** | `03-AUDIT-UNIVERSE.json` extended to carry non-derived events | the write act | Only if a non-derived source feeds it | tracked; bound by the `"No wall clock"` determinism contract |

### 5.4 Candidate pairs — measurable set, expected set, counterexample space, implementation impact

Each row is a *candidate*, not a proposal. Pairs are listed where the pairing is coherent; the
table is the decision space, and its rows are mutually exclusive readings of one claim name.

| Pair | Measurable set (what the check would compute) | Expected set (what the claim would require) | Counterexample space (what still passes) | Implementation impact |
|---|---|---|---|---|
| **P-0 = M-current × A-current** *(today)* | `{live non-document objects} ∖ set(by_object.keys())` — 27 violations | mutations | **10 classes**, per `PHASE0-E3-CLAIM-INTEGRITY-REPORT.md` C1–C10: every content change to a registered object; every `by_path` write (1628 docs); every `by_execution` write; every `history` append; every counter advance; **every `commit()` call**; record-body rewrites; `history` erasure; deletions; wrong event content | none — this is the status quo. Its non-zero count is `UGA-INV-01`'s finding reported twice (identical sets, measured). |
| **P-1 = M5 × A1** | `{commit() acts} ∖ {logged acts}`, both from the runtime log | one durable record per write act | Acts performed in a clone whose `.runtime/` was cleared; any write that bypasses `commit()` (bounded by `LEDGER-INV-01`, whose scope R-10 widened to one-hop indirection) | `commit()` becomes an audit writer → `ledger_authority.py` acquires a second output; the log is per-clone, so the invariant's measurement becomes **clone-dependent**, which conflicts with a repository-evaluable invariant (`classification_rules.properties.repository_evaluable`) |
| **P-2 = M5 × A2** | as P-1, from a tracked log | as P-1, repository-evaluable | Same bypass space; plus the log's own mutations | A new tracked file: (i) must not be named `*-audit.json` under `00-BOOK/DATA` (`:187-207`); (ii) is an anonymous `UCOS-UGA-001` object → identity → permit → file, the regress `:499-506` terminates at one file; (iii) becomes a drift surface for the determinism gate unless it carries no wall clock |
| **P-3 = M3 × A1/A2** | `{newly allocated identifiers} ∖ {identifiers named in log entries}` | one event per identifier allocated | Every non-allocating mutation: `history`, `version`, `discovered_volumes`, counter-only advances, record bodies of new records (RES-1/U1) | Narrowest change; leaves the name *"EVERY MUTATION"* still wider than the measurement, so GQ-20 (is the name authoritative?) must be answered in the same act |
| **P-4 = M4 × A2** | `{changed identity-map keys} ∖ {audited keys}` | one event per identity-map change | `history`, counters, `version`, `discovered_volumes`; non-ledger state | Requires a per-key before/after record, i.e. a diff, i.e. the pre-image must be retained or digested per record. Interacts directly with RES-1/GQ-22. |
| **P-5 = M6 × A6** | `{changed 00-BOOK/DATA artifacts} ∖ {change_events subjects}` | one change event per artifact write | Ledger-internal changes that do not alter an artifact's registered identity; `commit: null` events carry no VCS anchor | Reuses an existing 1724-event artifact. Widens the invariant's subject from objects to artifacts, which crosses into `UMB-IMP-001`'s and the generated-artifact registry's territory — an ownership question, not a measurement question |
| **P-6 = M7 × A3** | `{objects whose content hash moved} ∖ {objects with a history snapshot}` | one snapshot per content change | Anything not content-hashed; and the audit source lives **inside** the audited state, so a restore reverts both | Nearly free — both sets already exist and are measured (1628 lists). Fails a non-derivability requirement if GQ-18 answers *yes*, for the same structural reason `A-current` does. |
| **P-7 = M1/M2 × A1/A2** | `{writes where bytes/document changed} ∖ {logged writes}` | one record per byte-level change | Out-of-band writes that never reach `commit()`; a crash between `writer` and the log append | `bytes_changed` is already computed (`:898`) and now rendered (`:476-481`); persisting it is small. But byte-level equality of *authorized* vs *persisted* is document-level only (Phase 1 §R-7: three serializers, `_canonical` differs at 1 786 167 vs 2 274 511 bytes), so an audit over *bytes* would need a serializer decision |
| **P-8 = M8 × A1/A2** | `{lifecycle transitions} ∖ {logged transitions}` | one record per transition | Everything outside `by_execution` | `last_transition_seq` already exists at `ukb.py:2388-2400`; smallest scope; least coverage of the claim name |
| **P-9 = M5 × A5** | `{commit() acts} ∖ {permit records}` | every write traceable to an authorization | Writes under `NO_ALLOCATION` (which is issued by nobody and appears in no register, `:514-529`) | Makes the register the audit log. **Creates a hard dependency E-3 → E-4A**, and requires the register to record *use*, which is E1-F3's GQ-1. Three blockers collapse into one decision under this pair, and only under this pair. |

### 5.5 What every pair has in common — the one fact governance design needs

For **all nine** candidate pairs, the audit source must be **something other than the state
being audited**. That is the single structural property `A-current` lacks, and it is why the
current invariant is a tautology rather than a weak invariant:

```
audited ≡ set(ledger["by_object"].keys())      measured True, 5374 ≡ 5374  (probe P2-10)
```

Whether non-derivability is *required* is GQ-18, and it is not answered here. What is
established is that the choice of audit universe is **not free**: A1 is untracked, A2 is
name-constrained and regress-bearing, A3 and A6 are derived, A4 is optional-valued, A5 does
not exist. Every option carries a measured constraint, and §10 tabulates them.


---

## 6. Work Item P2-D — RES-1 analysis

> Determine whether RES-1 is a governance problem, an implementation problem, an invariant
> problem, or a permit-model problem. Support the classification with executable evidence.
> Determine every defect that remains even if E-4A is fully implemented.

### 6.1 Classification

**RES-1 is a permit-model problem.** It is not primarily any of the other three, and the
evidence separates the four cleanly.

| Candidate class | Verdict | Executable evidence |
|---|---|---|
| **Implementation problem** | **REJECTED** | No code is wrong. `manifest_digest` (`:548-568`) computes exactly what its docstring says it computes — *"Digest over the ALLOCATION-BEARING fields only … Deliberately excludes …"* — and does it correctly. Probes P2-2/3/4/7/8 show digest **equality** where the code says equality should hold. Nothing malfunctions. A bug is a divergence between code and its stated contract; here they agree. |
| **Invariant problem** | **REJECTED** | No invariant asserts document-level binding, so none is violated. `assert_append_only` (`:271-383`) does its full job — it refused the restore in P2-1's continuation and refuses record-body rewrites of existing records. `LEDGER-INV-01` measures write paths, not bindings. There is no false invariant claim to correct. |
| **Governance problem** *(pure)* | **REJECTED as the primary class** | A pure governance problem would be resolvable by a decision alone. Answering GQ-22 does not close RES-1: every answer other than *"the projection is the correct binding"* requires `manifest_digest`'s input set to change, i.e. code. |
| **Permit-model problem** | **ACCEPTED** | The defect is located in **what the authorization object is a statement about**. Measured: for a fixed pre-image, the permit's identity of the write is an equivalence class with **at least five orthogonal free dimensions** (U1–U5, §4.3), and a member of that class other than the reviewed one was persisted in five separate probes with `authorization=PERMIT` and no error. The model says *"a permit approves an allocation"*; the code makes a permit approve *a set of allocations plus an unbounded set of accompanying changes*. |

Consolidated probe evidence for the classification:

```
P2-2  digest(honest body) == digest(forged body)            True   -> forged body persisted
P2-3  digest(assignment X) == digest(assignment swapped)     True   -> swap persisted
P2-7  digest(id→legit key) == digest(id→other key)           True   -> other key persisted
P2-8  digest(no-op) == digest(no-op + rogue non-dict keys)   True   -> rogue keys persisted
P2-4  digest(history A) == digest(history B) == digest(version+volumes bump)   True
      -> a permit for one authorized the others; all three ACCEPTED as PERMIT
```

**Secondary classification, stated because it determines who can act.** RES-1's *remedy* is
governance-dependent for one measured reason: widening `manifest_digest` changes what `plan()`
must emit, and `plan()`'s docstring (`:648-661`) defines issuance as *"a transcription of this
output"*. Changing the transcription content changes what an issuer attests to — which is
issuance semantics. This is the same reasoning `PHASE05-GOVERNANCE-INDEPENDENT-REMEDIATION.md`
§B.7 and §F.4 recorded, and it survives re-examination.

### 6.2 Every defect that remains even if E-4A is fully implemented

Assume, purely as an analytical premise and without designing it, that **some** issuance path
exists and produces permits that verify. The following remain. Each is stated with the reason
an issuance path does not touch it.

| # | Remaining defect | Why E-4A's resolution does not close it |
|---|---|---|
| **R-a** | **U1** — a new record's body is unbound | `manifest_digest`'s inputs (`:548-568`) do not include record bodies. Any correctly-issued permit has this hole. |
| **R-b** | **U2** — the key receiving a new identifier is unbound | `allocated` is built from identifier *values* (`:398`). |
| **R-c** | **U3** — identifier↔key assignment among new keys is unbound | Same line. |
| **R-d** | **U4** — `history` append content is unbound | `history ∈ NON_ALLOCATION_KEYS` (`:103-116`); prefix-only check (`:355-383`). |
| **R-e** | **U5** — `version` / `discovered_volumes` values, and new non-dict top-level keys, are unbound | `NON_ALLOCATION_KEYS`; `unmeasured_maps` scans `isinstance(v, dict)` only (`:419`). |
| **R-f** | **RES-2** — an empty-manifest permit authorizes the whole non-allocating-mutation class | `_verify_permit`'s permit path reads neither `total_allocations` nor `allocating`. Worsens with issuance, because then such a permit can exist. |
| **R-g** | **E1-F3** — replay after out-of-band restore | Requires a use record; issuance alone creates permits, it does not consume them. |
| **R-h** | **E-3** — the audit tautology | Independent of permits entirely (probe P2-10: measured and failing today with no permit in existence). |
| **R-i** | **Register authenticity** | `load_permit_register` (`:608-631`) verifies readability and shape only. Whatever process writes the register grants authorization; an issuance path *creates* this surface rather than closing it. |
| **R-j** | **No revocation** | `revoked` is not read (P2-6). Removal from the register is the only mechanism, and it is retroactive rather than recorded. |
| **R-k** | **`expires_at` has no producer** | Implemented at `:785-797`, populated by nothing. An issuance path that omits it produces permits that never expire; one that sets it requires a temporal decision. |
| **R-l** | **RES-3 — MW-3 remains a window** | The caller's own ledger read (`uga_engine.py:1700`-equivalent) precedes `commit()`, hence precedes the lock. Bounded by two independent refusals after R-6; not closed. Phase 0.5 §F.4 classifies it as a bound, not a blocker; it is listed here for completeness of the post-E-4A picture. |
| **R-m** | **RES-4 — `flock` is advisory** | Verified working on macOS/APFS; on a filesystem that does not honour it, `R-3` degrades to nothing and `R-2` is the sole detector. Environmental, not a blocker. |
| **R-n** | **R-7's post-hoc window** | Divergent bytes reach disk before the comparison at `:920-927`; a crash between `writer` (`:895`) and `_restore` (`:807-822`) leaves them there. Two file operations under a held lock. Phase 1 §R-7 states this limit; it is unchanged. |

```
DEFECTS REMAINING AFTER A FULLY IMPLEMENTED E-4A ......... 14
  RES-1 legs (U1–U5) ..................................... 5   R-a … R-e
  other open blockers .................................... 3   R-f (RES-2), R-g (E1-F3), R-h (E-3)
  surfaces E-4A CREATES rather than closes ............... 3   R-i, R-j, R-k
  documented bounds carried forward ...................... 3   R-l, R-m, R-n
```

The three in the middle row are the ones worth naming precisely: **an issuance path is not
purely additive.** It creates a register whose authenticity is unverified (R-i), a revocation
gap that only matters once permits exist (R-j), and a mandatory-in-practice decision about
`expires_at` (R-k). None of these is a reason to do or not do anything — they are the measured
consequences of the existence question E-4A poses.

---

## 7. Work Item P2-E — RES-2 analysis

> Determine whether the empty-manifest permissiveness is required, accidental, contradictory or
> unreachable behavior. Determine all consequences of changing it. Do not change it.

### 7.1 The behavior, exactly

`_NoAllocation`'s docstring, `00-BOOK/tools/ledger_authority.py:519`:

> *"a permit for an empty manifest would authorize nothing and must not be issuable."*

`_verify_permit`'s permit path (`:714-804`) reads `permit_id`, `actor`, `manifest_digest`,
`preimage_digest`, `head`, `scope.maps`, `scope.max_allocations`, `expires_at`. It reads
**neither** `manifest["allocating"]` **nor** `manifest["total_allocations"]`. Those are read
only in the sentinel branch (`:684-690`). So a permit whose `manifest_digest` is the digest of
an all-empty manifest verifies like any other.

Measured, probe **P2-4** (fixture) and **P2-5** (live ledger, read-only):

```
fixture, one pre-image, three different proposed documents:
  history append A     allocating=False total=0 allocated={} counters={} unmeasured=[]
  history append B     allocating=False total=0 allocated={} counters={} unmeasured=[]
  version+volumes bump allocating=False total=0 allocated={} counters={} unmeasured=[]
  digest(A) == digest(B) == digest(version bump)               : True
  permit issued for A, committed B                             : ACCEPTED (PERMIT)
  same digest, committed the version+discovered_volumes bump   : ACCEPTED (PERMIT) -> version 99
  the SAME write under NO_ALLOCATION                           : REFUSED (R-9)

LIVE 00-BOOK/DATA/id-ledger.json, read-only:
  byte-identical no-op        : allocating=False unmeasured=[]
  history-only append         : allocating=False total=0 allocated={} counters={} cursors={} unmeasured=[]
  digest(history append) == digest(no-op)                      : True
  history append under NO_ALLOCATION                           : REFUSED
```

The last two lines are the sharp form of RES-2: **on the production ledger, the digest of a
real `history` append is the digest of doing nothing.** One permit value covers both, and
covers `version` and `discovered_volumes` rewrites as well.

### 7.2 The four-way determination

The question admits a single answer per label only if the labels are read as mutually
exclusive. They are not, and forcing one would misreport the evidence. Each is therefore
determined separately, and the composite verdict is stated last.

| Label | Determination | Evidence |
|---|---|---|
| **Required behavior** | **TRUE, as of Phase 1.** It is the **only** authorization path for a real class of write. After `R-9` (`:696-707`), `NO_ALLOCATION` refuses any write where `before != after`; after `R-5a`, `history` is classified so a `history` append measures `allocating=False, total=0`. A `history`-only append therefore has exactly one admissible `permit` value: a permit over the empty manifest. Measured on the live ledger above. Phase 0.5 §F.4 recorded this coupling in advance: *"this phase depends on the current permissive behaviour."* | P2-4, P2-5 |
| **Accidental behavior** | **TRUE of the implementation, FALSE of the design intent.** The intent is recorded — the docstring places the control at **issuance** (*"must not be issuable"*), not at verification. Under that reading the verifier's silence is by design and the missing control is the issuer's, which does not exist (E-4A). What is accidental is that the claim ended up enforced **nowhere**: not at issuance (no issuer) and not at verification (no check). | `:519` vs `:714-804` |
| **Contradictory behavior** | **TRUE.** The module states a property it does not hold. This is the same species of defect as `E2-F4` — which Phase 1 closed by *making the docstring true* (`R-9`, quoting `:527-529` verbatim as the property to implement). RES-2 is the residue of that pattern: one docstring claim in the same class, in the same file, left unimplemented. | `:519`; Phase 1 §R-9 |
| **Unreachable behavior** | **FALSE.** Reachable in two senses, both measured: (i) a permit over an empty manifest verifies (P2-4, executed end-to-end through `commit()`); (ii) the write class it authorizes exists on the production ledger (P2-5, `history`-only append measured `allocating=False`). It is currently *unexercised* only because no register exists — the same E-4A latency that covers RES-1 and E1-F3. | P2-4, P2-5 |

**Composite:** RES-2 is a **contradictory** behavior that is **currently required** by Phase
1's design and **accidental** in the sense that its intended control point was never built. It
is not unreachable. The three true labels are not in tension: the contradiction is between
source claim and source behavior; the requirement is a downstream consequence of R-5a + R-9;
the accident is the absent issuer.

### 7.3 All consequences of changing it

Not changed. Enumerated for both directions, because "changing it" is ambiguous between two
opposite acts.

#### Direction 1 — make the docstring true (add a refusal for empty-manifest permits)

| # | Consequence | Certainty |
|---|---|---|
| C1 | The non-allocating-mutation class `{history append, version change, discovered_volumes change}` loses its **only** authorization path. `NO_ALLOCATION` already refuses it (R-9); a permit would then also refuse it. | **Measured** — P2-4 shows `NO_ALLOCATION` refusing the exact write that the empty-manifest permit accepts |
| C2 | This produces a **second total block**, structurally identical to E-4A: a write class reachable in production with no admissible `permit` value. | Derived from C1 plus `permit`'s mandatory status (`:841`) |
| C3 | `ukb.record_snapshots` (`ukb.py:314-330`) becomes unable to persist a snapshot append unless it accompanies an allocation. Whether `ukb build --mint` ever produces a `history`-only change is a production-frequency question this phase did not measure; the *class* is reachable, which is what matters for the decision. | Class reachability measured; frequency **not measured** |
| C4 | Phase 1's `R-5` design must be revisited, exactly as Phase 0.5 §F.4 warned: *"If a future phase makes empty-manifest permits unissuable, `history`-only appends lose their authorization path and R-5's design must be revisited."* | Recorded in advance; confirmed by C1 |
| C5 | RES-1/U5 is **partially** closed as a side effect: `version` and `discovered_volumes` rewrites lose their permit path along with `history`. The unbound *values* remain unbound wherever an accompanying allocation supplies a non-empty manifest. | Derived from `allocation_report` (`:386-434`) |
| C6 | GQ-26 must be answered in the same act — *what authorizes a non-allocating mutation?* — or C2 stands. | Derived |
| C7 | No existing permit is invalidated, because none exists. | **Measured** — register absent (P2-5) |

#### Direction 2 — make the code's behavior the stated design (delete or qualify the claim at `:519`)

| # | Consequence | Certainty |
|---|---|---|
| C8 | The contradiction closes with **no control change**. The permissive behavior Phase 1 depends on is preserved. | Derived |
| C9 | The statement *"strictly safer than passing a permit — it can only ever permit less"* (`:527-529`) requires re-examination, because it is now **false in one direction**: `NO_ALLOCATION` refuses a `history` append (R-9) that an empty-manifest permit accepts. Measured in P2-4. After R-9, the sentinel permits **less** than a permit in the mutation dimension — which is the intended direction — but the docstring's framing of the empty-manifest permit as non-existent is what makes the sentence read as exhaustive. | **Measured** |
| C10 | An issuance path (E-4A) would then be free to issue empty-manifest permits, each authorizing the entire non-allocating class for a given pre-image. The scope fields cannot narrow this: `scope.maps` is checked against `manifest["allocated"]`, which is `{}` here, so the subset test is vacuous (`:767-776`); `scope.max_allocations` compares against `total_allocations = 0`, so any cap passes (`:777-783`). | **Derived from source, verified by reading the two checks** |
| C11 | RES-1's U4 and U5 remain, and become the operative holes for this write class. | Derived |

**C10 is the load-bearing consequence of Direction 2 and is stated without preference:** the
two existing scope-narrowing mechanisms are both **inoperative on an empty manifest**. Any
narrowing of an empty-manifest permit would have to come from a binding that does not exist
today, which is GQ-22 — i.e. RES-2's Direction 2 hands the problem to RES-1.


---

## 8. Governance-question inventory

*(Required deliverable 3.)*

Twenty-seven questions. Each is stated as a question, with the blockers it gates, the source
location whose behavior depends on it, and its admissible answer space. **No answer is given,
implied or preferred.** "Minimum" means: removing any question from the mandatory set leaves at
least one blocker with no derivable remedy.

| ID | Question | Gates | Source dependency | Admissible answers (enumerated, unranked) | Mandatory? |
|---|---|---|---|---|---|
| **GQ-1** | Is an authorization consumed by its use? | E1-F3 | `:570-577`, `:742-749` | reusable · single-use · bounded reuse (n / window) | **MANDATORY** |
| GQ-2 | Is authorization bound to a *state* or to an *occasion*? | E1-F3 | `:742-749` (state today) | state · occasion · both | conditional on GQ-1 ≠ reusable |
| **GQ-3** | Is restoring `id-ledger.json` to a prior state a legitimate operation? | E1-F3 | tracked path; X-4 in the protected-area register (`ec1-ci.yml:109-111`) | freely legitimate · prohibited · legitimate only by a named authority | **MANDATORY** |
| GQ-4 | Is the record of authorization-use itself governed state requiring authorization? | E1-F3 | the regress terminated at one file, `:499-506` | yes · no · it is operational telemetry | conditional on GQ-1 ≠ reusable |
| GQ-5 | Must authorization memory survive a fresh clone? | E1-F3 | `.gitignore:12`; `governance_telemetry.py:44-52` | yes · no | conditional |
| **GQ-6** | Who may issue? | E-4A | `:490-497` (*"ENFORCES an authorization it does not DECIDE"*) | — (not enumerated; enumerating candidate issuers would be defining an authority structure) | **MANDATORY** |
| **GQ-7** | What does issuance attest? | E-4A, RES-1 | `plan()` docstring `:648-661` (*"a transcription of this output"*) | that the manifest was reviewed · that the actor is authorized · that the resulting state is intended · a combination | **MANDATORY** |
| GQ-8 | Is the permit register itself governed state, and who may write it? | E-4A, E1-F3 (path A2) | `:608-631`; `:499-506` | governed · ungoverned · governed by the same authority as the ledger | **MANDATORY** |
| GQ-9 | Must the issuer be distinct from the executor? | E-4A | `:490-497` states the intent; nothing enforces it | required · not required · required above a threshold | conditional on GQ-6 |
| GQ-10 | What event ends a permit's validity? | E-4A, E1-F3 | `:785-797` (`expires_at` implemented, unpopulated) | use · an instant · a repository state change · never · a combination | **MANDATORY** |
| GQ-11 | Is issuance revocable, and is revocation recorded or retroactive? | E-4A | `revoked` unread (P2-6) | recorded revocation · removal from the register · not revocable | conditional |
| GQ-12 | Is the `head` binding mandatory or elective? | E-4A, E1-F3 (path A5) | `:751-762` (elective today) | mandatory · elective · mandatory for some actors | conditional |
| GQ-13 | Must the register be authenticated, or is presence sufficient? | E-4A | `:608-631` — shape only | presence is sufficient · integrity binding required · signature required | **MANDATORY** |
| GQ-14 | Is a permit per-act or per-campaign? | E-4A | `scope.max_allocations` `:777-783` suggests campaign; `preimage_digest` `:742-749` forces per-act | per-act · per-campaign · per-actor-session | conditional |
| **GQ-15** | What is a *mutation* for audit purposes — a subject class or an act? | E-3 | `uga_engine.py:1331-1335`; `mutation-governance-boundary.json` `mutation_classes` | subject-class (declared already) · act/occurrence · both | **MANDATORY** |
| GQ-16 | Which state's mutations must be audited? | E-3 | `IDENTITY_MAPS` `:91-97`; `00-BOOK/DATA/` (17 artifacts) | the identity ledger · all `00-BOOK/DATA` · all tracked state · constitutional truth only | **MANDATORY** |
| **GQ-17** | What must an audit event contain to count as one? | E-3 | current event shape `uga_engine.py:1846-1858` (11 fields, `action` always `IDENTITY_MINTED`) | — (dimensions listed in §5.3/§5.4 as questions; no field set proposed) | **MANDATORY** |
| GQ-18 | Must an audit event be independently sourced from the state it audits? | E-3 | `audited ≡ set(by_object.keys())`, measured | yes · no | **MANDATORY** |
| GQ-19 | Must audit events be durable and tracked? | E-3 | `forbid_data_telemetry` `:187-207`; `.gitignore:12`; determinism contract `"No wall clock"` | tracked · runtime-only · both, with different retention | **MANDATORY** |
| GQ-20 | Is the invariant's *name* authoritative, or may the name be changed to match the measurement? | E-3 | `uga-declaration.json` (`fails_closed: true`); 58 referencing files | name is authoritative · measurement is authoritative · both change | **MANDATORY** |
| GQ-21 | Do historical determinations that cited `UGA-INV-01` and `UGA-INV-10` as independent signals require re-issuance? | E-3 | ≥6 records, `PHASE0-E3-CLAIM-INTEGRITY-REPORT.md` §4.3 | yes · no · only those whose conclusion depended on the count | conditional on GQ-20 |
| **GQ-22** | What must a permit bind — the allocation projection, the whole proposed document, or the persisted bytes? | RES-1, RES-2 (C10) | `manifest_digest` `:548-568` | projection (today) · whole document · bytes · projection + named additional dimensions | **MANDATORY** |
| GQ-23 | Must the approval object be human-reviewable? | RES-1 | `:763-766` (*"The digest binds exactly; a human cannot read a digest"*) | yes · no · reviewable summary plus exact digest | conditional on GQ-22 ≠ projection |
| GQ-24 | Is the key↔identifier assignment a governed property? | RES-1 (U2, U3) | `:396-400` | yes · no | conditional on GQ-22 |
| **GQ-25** | Is a permit over an empty manifest issuable? | RES-2 | `:519` claims not; `:714-804` permits it | issuable · not issuable | **MANDATORY** |
| GQ-26 | What authorizes a non-allocating mutation? | RES-2 (C2, C6) | `NO_ALLOCATION` `:684-712` refuses it after R-9; empty-manifest permit accepts it | an empty-manifest permit · a widened sentinel · a distinct authorization kind · nothing (the class is prohibited) | **MANDATORY if GQ-25 = not issuable** |
| GQ-27 | Is the unit of authorization "nothing allocated" or "the document changed"? | RES-2, RES-1 | `allocating` `:386-434` vs `before != after` `:702` | allocation-unit · document-unit · both | conditional on GQ-22, GQ-25 |

```
GOVERNANCE QUESTIONS IN THE MINIMUM SET .................. 14   (marked MANDATORY)
  E1-F3 ................................................... 2   GQ-1, GQ-3
  E-4A .................................................... 5   GQ-6, GQ-7, GQ-8, GQ-10, GQ-13
  E-3 ..................................................... 6   GQ-15, GQ-16, GQ-17, GQ-18, GQ-19, GQ-20
  RES-1 ................................................... 1   GQ-22
  RES-2 ................................................... 1 (+1 conditional)  GQ-25 (+GQ-26)
  shared across blockers .................................. GQ-7 (E-4A + RES-1), GQ-8 (E-4A + E1-F3),
                                                            GQ-22 (RES-1 + RES-2), GQ-10 (E-4A + E1-F3)
CONDITIONAL QUESTIONS .................................... 13
TOTAL .................................................... 27
ANSWERED IN THIS DOCUMENT ................................  0
```

The four shared questions are why the count of *questions* (14) is lower than the sum of
per-blocker minimums (15): `GQ-7`, `GQ-8`, `GQ-10` and `GQ-22` each gate two blockers.

---

## 9. Implementation-option inventory

*(Required deliverable 4.)*

Options are labelled `⟨blocker⟩-P⟨n⟩`. Each row states the mechanism, the code it touches, and
the governance answers under which it is **impossible**. No option is recommended, and the
ordering within each block is arbitrary (alphabetical by mechanism where not otherwise fixed).

### 9.1 E1-F3

Enumerated in §3.3 as A1–A8. Restated with code locations:

| Option | Touches | Impossible when |
|---|---|---|
| A1 spent-register (new file) | `commit()` `:841-933`; a new tracked artifact | GQ-1 = reusable; GQ-4 = the record is governed state (regress) |
| A2 mark in the register | `load_permit_register` `:608-631` becomes read-write; `commit()` | GQ-1 = reusable; GQ-8 = the enforcer may not write the register |
| A3 use-record inside the ledger | `IDENTITY_MAPS` / `NON_ALLOCATION_KEYS` `:91-116` | always insufficient — restore reverts it with the pre-image (`:577`) |
| A4 monotone runtime nonce | `governance_telemetry.append_audit` `:133-160` | GQ-1 = reusable; GQ-5 = memory must survive a clone |
| A5 mandatory `head` binding | `:751-762` (already implemented; make it required) | GQ-3 = restoration freely legitimate; GQ-12 = elective |
| A6 restore prohibition + detector | requires A1 or A4 as substrate | GQ-3 = restoration freely legitimate |
| A7 populate `expires_at` | `:785-797` (already implemented) | GQ-1 = single-use (time-bounding is not consumption); GQ-10 = never |
| A8 correct the claim at `:570-577` | docstring only | GQ-1 ≠ reusable |

### 9.2 E-4A

| Option | Mechanism | Touches | Impossible when |
|---|---|---|---|
| **E4A-P1** | A CLI subcommand that transcribes `plan()` output into the register | a new subcommand on an existing tool | GQ-9 = issuer must be distinct from executor **and** the tool is the executor |
| **E4A-P2** | A standalone tool separate from `ukb`/`uga_engine` | a new tracked tool object | GQ-6 answers to an issuer outside the repository |
| **E4A-P3** | A CI/workflow-issued permit (issuance as an automated gate) | `.github/workflows/*` | GQ-6 = issuance requires human judgment; GQ-13 = signature required and CI cannot hold the key |
| **E4A-P4** | An out-of-band, hand-authored register file (issuance as an editing convention, no tool) | nothing — the register is already consumed | GQ-13 = integrity binding required; GQ-7 = issuance must be a recorded act |
| **E4A-P5** | Issuance folded into `plan()` (plan emits a permit) | `plan()` `:648-661` | GQ-9 = separation required; GQ-7 = issuance attests review (a tool cannot review) |
| **E4A-P6** | Permits derived rather than issued (a rule that admits a class of manifests without a register entry) | `_verify_permit` `:664-804` | GQ-7 = issuance attests a per-act decision; GQ-14 = per-act |

Each option is **independent of** the register's *shape*, which is already fixed by
`_verify_permit`'s consumption set (§4.1). That is the one part of E-4A that requires no
decision: any issuance path must emit those fields, because those are the fields verified.

### 9.3 E-3

| Option | Mechanism | Touches | Impossible when |
|---|---|---|---|
| **E3-P1** | Re-name the invariant to what it measures; the identity claim stands alone | `uga_engine.py:1334`; `uga-declaration.json`; 58 referencing files | GQ-20 = the name is authoritative |
| **E3-P2** | Keep the name; replace the measurement with pair P-1…P-9 (§5.4) | `uga_engine.py:1331-1335` + the chosen event source | GQ-20 = measurement is authoritative and the name must change; the pair's own constraint column |
| **E3-P3** | Split into two invariants — one for identity presence, one for audit coverage | `epoch5_invariants` `uga_engine.py:1209+`; declaration | GQ-20 = neither name may change |
| **E3-P4** | Retire `UGA-INV-10` entirely as a duplicate of `UGA-INV-01` | declaration; `cmd_gate` `:2125-2161` | GQ-16/GQ-17 require audit coverage to be measured at all |
| **E3-P5** | Keep both, and record the duplication as a declared property | declaration text | GQ-18 = independence required |

### 9.4 RES-1

| Option | Mechanism | Touches | Impossible when |
|---|---|---|---|
| **RES1-P1** | Add a document digest as a **seventh** manifest field | `manifest_digest` `:548-568`; `plan()` output; every permit binding | GQ-23 = the approval object must be human-reviewable and a document digest is not |
| **RES1-P2** | Add named dimensions only (key→identifier pairs; new record bodies) | `allocation_report` `:386-434`; `manifest_digest` | GQ-22 = whole document or bytes |
| **RES1-P3** | Widen `allocated` from identifier values to key→identifier pairs | `:396-400` | GQ-24 = assignment is not a governed property |
| **RES1-P4** | Bind persisted **bytes** | requires a serializer decision — three exist, `_canonical` differs from the two production writers (1 786 167 vs 2 274 511 bytes, Phase 1 §R-11) | GQ-22 ≠ bytes; also blocked by the measured serializer inequality unless one canonical form is chosen |
| **RES1-P5** | Extend `scope` with reviewable declarations instead of widening the digest | `:767-783` | GQ-22 = the binding itself must widen (scope is checked as superset/cap, not equality) |
| **RES1-P6** | No change; record the projection as the intended binding | docstring `:548-568` (already states it) | GQ-22 ≠ projection |

### 9.5 RES-2

| Option | Mechanism | Touches | Impossible when |
|---|---|---|---|
| **RES2-P1** | Refuse a permit whose manifest is all-empty | `_verify_permit` permit path `:714-804` | GQ-25 = issuable; blocked in practice by C2 unless GQ-26 is answered together |
| **RES2-P2** | Refuse at issuance only (the docstring's stated control point) | whichever E-4A option is built | GQ-25 = issuable; requires E-4A to exist first |
| **RES2-P3** | Delete or qualify the claim at `:519` | docstring only | GQ-25 = not issuable |
| **RES2-P4** | Introduce a distinct authorization kind for non-allocating mutation | `_verify_permit`; `NO_ALLOCATION` `:514-529` | GQ-26 = an empty-manifest permit is the answer; GQ-27 = allocation-unit |
| **RES2-P5** | Widen the sentinel to cover the non-allocating-mutation class under stated conditions | `:684-712` (R-9's branch) | GQ-26 ≠ a widened sentinel; note this reverses part of R-9 and Phase 1 §7 records R-9 as the closure of E2-F4 |

```
IMPLEMENTATION OPTIONS ENUMERATED ........................ 30
  E1-F3 ....  8      E-4A ....  6      E-3 ....  5      RES-1 ....  6      RES-2 ....  5
OPTIONS SELECTED .........................................  0
OPTIONS PROVEN INSUFFICIENT ON THEIR OWN .................  3   A3 (restore reverts it),
                                                                A5 and A7 (bound, do not close)
```


---

## 10. Constraint matrix

*(Required deliverable 5.)*

Constraints are properties of the existing repository that **any** answer must live with. Each
was verified in this phase or is quoted from a verified Phase 1 measurement. They are not
policies; they are measured facts that bound the option space.

| ID | Constraint | Source / evidence | Binds |
|---|---|---|---|
| **C-1** | `permit` is mandatory with no default, so a missing authorization is a `TypeError` at the call site, never a bypass | `:841`; rationale `:851-855` | every option: no option may make authorization optional without removing this property |
| **C-2** | Every added control must fail closed. Phase 1 preserved E1-S1…S8 and every new refusal is monotonically restrictive | Phase 1 §7 | all |
| **C-3** | A new tracked file is an anonymous `UCOS-UGA-001` object → needs identity → needs allocation → needs a permit → needs a file. The regress is terminated at **one** register file, deliberately | `:499-506` | A1, A2, E4A-P2, P-2, E3-P2 |
| **C-4** | `*-audit.json` may **never** be written under `00-BOOK/DATA` — hard `TelemetryPathError` | `governance_telemetry.py:187-207` | every audit-event option persisting to `00-BOOK/DATA` |
| **C-5** | `.runtime/` is gitignored, so runtime audit logs are **per-clone** and start at `seq = 1` in a fresh clone | `.gitignore:12`; `governance_telemetry.py:44-52` | A1, A4, P-1 |
| **C-6** | Canonical UGA artifacts carry `"determinism": "No wall clock. Timestamps are ledger first_seen values."` | `uga_engine.py:1911-1915` | any tracked audit artifact carrying event times |
| **C-7** | Widening `manifest_digest` changes **every** digest, invalidating every issued permit. Harmless today (zero permits exist); binding the moment one does | `:548-568`; P2-5; Phase 1 §4.2's identical rule for R-5a | RES1-P1…P3, and the ordering RES-1 before E-4A |
| **C-8** | `plan()` is defined as the transcription source: *"issuing a permit is a transcription of this output rather than an independent act of measurement"* | `:648-661` | E4A-P1…P6; GQ-7 |
| **C-9** | The proposed document is produced only by the tool that will write it, so no fully independent measurement of a manifest is available | `ukb.py:1292`, `uga_engine.py:2079` | GQ-9, E4A-P3, E4A-P5 |
| **C-10** | Manifest transcription is deterministic while the **git index** is still. The discovered set is `git ls-files --cached`, so an untracked working-tree file does not move the digest; staging an eligible artifact does | executed (§4.4 D-b, D-c; §12.3) | any issuance workflow spanning a `git add` |
| **C-11** | `register.sh` is asserted by test to be the one minting caller | `platform/tests/test_verification_purity.py:122-134`, `:378` | any option adding a second minting invocation |
| **C-12** | `register.sh` Phase 1 passes no `--permit`; the remaining nine phases are gated on it (`|| fail`) | `register.sh:206-259` | every E-4A option must reach this call site or the transaction stays blocked |
| **C-13** | One `register.sh` transaction needs exactly **one** ledger permit; the other two write paths are separate invocations with different actor strings | `register.sh:206-259`; `ukb.py:1287,2382,2403`; `uga_engine.py:2098` | GQ-14, E4A-P1…P6 |
| **C-14** | `expires_at` has no producer anywhere in the repository | probe P2-6; `:785-797` | every E-4A option: either omit it (permits never expire) or answer GQ-10 |
| **C-15** | `cmd_gate` blocks on **every** failing invariant, with the previous carve-out removed and the removal justified in-source | `uga_engine.py:2128-2136` | E3-P1…P5: any option leaving a failing invariant leaves the gate red |
| **C-16** | **58 files** reference `UGA-INV-10` — measured before this report existed; 59 including it | measured (`grep -rl`, excluding `.git` and `.ec1-venv`) | E3-P1…P5 blast radius |
| **C-17** | `UGA-INV-10` is declared `fails_closed: true` among 10 declared invariants; the engine computes 30 | `uga-declaration.json`; probe P2-10 | E3-P3, E3-P4 |
| **C-18** | `NO_ALLOCATION` is issued by nobody, appears in no register, names no actor and has no expiry — it is a caller claim verified against `(before, after)` | `:514-529`, `:684-712`; Phase 1 §R-9 | RES2-P4, RES2-P5, P-9 |
| **C-19** | `scope.maps` and `scope.max_allocations` are **inoperative on an empty manifest** — the subset test is vacuous against `{}` and any cap passes against `0` | `:767-783`; §7.3 C10 | RES2-P1…P5, RES1-P5 |
| **C-20** | The document, not the bytes, is what `commit()` compares after the write, because three serializers exist and `_canonical` is not byte-equal to the two production writers | `:920-927`; Phase 1 §R-11 (1 786 167 vs 2 274 511 bytes; both production writers byte-identical) | RES1-P4 |
| **C-21** | `flock` is advisory and filesystem-dependent; `R-2` is the sole detector where it is not honoured | Phase 0.5 §F.4 RES-4; Phase 1 §R-3 | any concurrency assumption |
| **C-22** | MW-3 persists: the caller's ledger read precedes `commit()`, hence precedes the lock; bounded by two independent refusals, not closed | Phase 0.5 §F.4 RES-3; Phase 1 §R-6 | any assumption that the lock covers the whole act |
| **C-23** | Restoration through the chokepoint is refused; only out-of-band restoration re-validates a permit | probe P2-1 continuation | A5, A6, GQ-3 |
| **C-24** | `00-BOOK/DATA/id-ledger.json` is tracked and is listed at X-4 in the protected-area register | `git ls-files`; `.github/workflows/ec1-ci.yml:109-111` | GQ-3 |
| **C-25** | The mutation-class universe over **subjects** is already declared, with resolution asserted deterministic / total / unique / repository-evaluable; `CORPUS_REGISTRATION` names the ledger explicitly | `00-BOOK/DATA/mutation-governance-boundary.json` | GQ-15, GQ-16: an act-level universe would be **additional** to an existing subject-level one, not a replacement |
| **C-26** | `commit()` emits no audit event; `audit_event`/`emit_event` token count in `ledger_authority.py` is **0** | probe P2-6 | E-3 pairs P-1, P-2, P-5, P-7, P-9 |

### 10.1 Option × constraint matrix

`✗` = the constraint makes the option impossible or self-defeating as stated. `!` = the option
is available but the constraint imposes a named cost. Blank = no interaction.

| Option | C-3 new-file regress | C-4 audit path | C-5 per-clone | C-6 determinism | C-7 digest churn | C-9 no independent measurement | C-12 register.sh | C-14 no expiry producer | C-16 58 refs | C-19 empty-scope vacuity | C-20 serializers |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 spent-register | **✗** if GQ-4=governed | | | ! | | | | | | | |
| A2 mark register | | | | ! | | | | | | | |
| A3 ledger use-record | | | | | **✗** always insufficient | | | | | | |
| A4 runtime nonce | | | **✗** if GQ-5=survive | | | | | | | | |
| A5 mandatory head | | | | | | | ! | | | | |
| A7 populate expiry | | | | | | | | **✗** must answer GQ-10 | | | |
| E4A-P1 CLI subcommand | | | | | ! | ! | ✓ reaches it | ! | | | |
| E4A-P3 CI issuance | | | | | ! | **✗** if GQ-13=signature | ! | ! | | | |
| E4A-P4 hand-authored | | | | | ! | | ! | ! | | | |
| E4A-P5 plan emits permit | | | | | ! | **✗** if GQ-9=separation | ✓ | ! | | | |
| E3-P1 rename | | | | | | | | | **!** 58 files | | |
| E3-P2 replace measurement | ! | **✗** for a `-audit.json` under DATA | ! | ! | | | | | ! | | |
| E3-P4 retire INV-10 | | | | | | | | | **!** | | |
| RES1-P1 document digest | | | | | **!** invalidates all permits | | | | | | |
| RES1-P4 bind bytes | | | | | ! | | | | | | **✗** three serializers |
| RES2-P1 refuse empty | | | | | | | | | | ✓ removes the vacuity | |
| RES2-P3 delete claim | | | | | | | | | | **!** vacuity persists | |
| P-1 (M5 × A1) | | | **✗** for a repository-evaluable invariant | | | | | | | | |
| P-2 (M5 × A2) | **!** one new tracked file | **✗** if named `*-audit.json` | | **!** no wall clock | | | | | | | |
| P-9 (M5 × A5) | | | | | | | | | | | |

`P-9` has no `✗` in this matrix and one property worth stating factually: it makes E-3 depend on
E-4A and E1-F3, collapsing three decisions into one. That is a structural observation about the
option, not a reason to take or avoid it.

---

## 11. Unresolved decision table

*(Required deliverable 6.)*

Every decision required, in one table, with nothing decided. `Blocks` names what stays open
until the decision is made. `Governance root` uses the existing FD labels where the mapping is
determined by the prior phases; where it is not, the cell reads `unmapped` rather than guessing.

| # | Decision | Question(s) | Blocks | Options | Governance root | Status |
|---|---|---|---|---|---|---|
| **D-1** | Whether an authorization is consumed by use | GQ-1, GQ-2 | E1-F3 | A1, A2, A4, A6, A7, A8 (8 paths, 3 exclusive families) | issuance semantics | **UNRESOLVED** |
| **D-2** | Whether restoring the identity ledger is a legitimate operation, and by whom | GQ-3 | E1-F3 | 3 answers | unmapped — it is an operational-legitimacy question the prior phases did not label | **UNRESOLVED** |
| **D-3** | Whether the record of authorization-use is itself governed state | GQ-4, GQ-5 | E1-F3 (conditional on D-1) | 3 answers | issuance semantics + the C-3 regress | **UNRESOLVED** |
| **D-4** | Who may issue | GQ-6, GQ-9 | E-4A | not enumerated (enumerating would define an authority structure) | issuer identity | **UNRESOLVED** |
| **D-5** | What issuance attests | GQ-7 | E-4A, RES-1 | 4 answers | issuance semantics | **UNRESOLVED** |
| **D-6** | Whether the register is governed state, and who may write it | GQ-8, GQ-13 | E-4A, E1-F3 path A2 | 3 × 3 | issuance semantics + authority | **UNRESOLVED** |
| **D-7** | What ends a permit's validity | GQ-10, GQ-11, GQ-12, GQ-14 | E-4A, E1-F3 | 5 answers for GQ-10 | temporal legitimacy | **UNRESOLVED** |
| **D-8** | What a mutation is, for audit purposes | GQ-15, GQ-16 | E-3 | 8 candidate universes M1–M8 (§5.2) | domain rules | **UNRESOLVED** |
| **D-9** | What an audit event must be and where it lives | GQ-17, GQ-18, GQ-19 | E-3 | 7 candidate universes A-current, A1–A7 (§5.3) | domain rules | **UNRESOLVED** |
| **D-10** | Whether an invariant's name or its measurement is authoritative | GQ-20, GQ-21 | E-3 | 3 answers; 5 options E3-P1…P5 | unmapped — a naming/ratification question | **UNRESOLVED** |
| **D-11** | What a permit binds | GQ-22, GQ-23, GQ-24 | RES-1, RES-2 (via C-19) | 4 answers; 6 options RES1-P1…P6 | issuance semantics | **UNRESOLVED** |
| **D-12** | Whether an empty-manifest permit is issuable | GQ-25 | RES-2 | 2 answers; 5 options RES2-P1…P5 | permit rules | **UNRESOLVED** |
| **D-13** | What authorizes a non-allocating mutation | GQ-26, GQ-27 | RES-2 (mandatory if D-12 = not issuable) | 4 answers | permit rules | **UNRESOLVED** |

```
DECISIONS REQUIRED ....................................... 13
  unconditional .......................................... 11   D-1, D-2, D-4 … D-12
  conditional on another decision ........................  2   D-3 (on D-1), D-13 (on D-12)
DECISIONS MADE IN THIS DOCUMENT ..........................  0
DECISIONS PARTIALLY CONSTRAINED BY MEASURED FACTS ........  6   D-1 (A3 excluded), D-7 (C-14),
                                                                D-9 (C-4, C-5, C-6), D-11 (C-7, C-20),
                                                                D-12 (C-19), D-13 (C-2, C-18)
```

"Partially constrained" means the option space is narrowed by a measured constraint, not that
an answer is implied. In each case at least two answers remain admissible.

### 11.1 Cross-decision couplings, stated as facts

| Coupling | Nature | Evidence |
|---|---|---|
| D-11 must be settled **before or with** D-4…D-7 | Widening the binding invalidates every issued permit (C-7). Ordering after issuance means invalidating live authorizations. | `:548-568`; Phase 1 §4.2's identical rule for R-5a |
| D-12 and D-13 must be settled **together** | D-12 = *not issuable* removes the only authorization path for a reachable write class (§7.3 C1–C2). | probes P2-4, P2-5 |
| D-1 and D-6 share one substrate | A2 records use *in the register*, so consumption and register-writability are one mechanism. | `:608-631` |
| D-8/D-9 are **independent** of D-4…D-7 | E-3 fails today with no permit in existence. | probe P2-10 |
| D-8/D-9 **become** coupled to D-4…D-7 under exactly one candidate pair | P-9 (M5 × A5) makes the register the audit log. | §5.4 |


---

## 12. Required final output

### 12.1 Calculation

```
TOTAL REMAINING BLOCKERS ................................. 5
    E1-F3   permit replay after out-of-band ledger restore
    E-3     UGA-INV-10 tautology + duplicate discriminating leg
    E-4A    no permit issuance path
    RES-1   a permit binds a six-field projection, not the document
    RES-2   an empty-manifest permit is not refused

BLOCKERS REQUIRING GOVERNANCE DECISIONS .................. 5   (100%)
    every one of the five has a remedy that is underdetermined by the source.
    For each, at least two admissible answers produce opposite code:
      E1-F3  A8 (correct the claim)        vs  A1/A2/A4 (record use)
      E-3    E3-P1 (rename)                vs  E3-P2 (replace the measurement)
      E-4A   E4A-P4 (a convention)         vs  E4A-P1/P2 (a tool)
      RES-1  RES1-P6 (record the projection) vs RES1-P1/P2/P3 (widen the binding)
      RES-2  RES2-P3 (delete the claim)    vs  RES2-P1 (add the refusal)

BLOCKERS REQUIRING IMPLEMENTATION AFTER THE DECISION ..... 5 under at least one
                                                             admissible answer;
                                                           0 under all answers
    Answer-dependent, measured per blocker:
      E1-F3  code under GQ-1 ∈ {single-use, bounded};  docstring-only under GQ-1 = reusable
      E-3    code under GQ-20 = measurement-authoritative;  declaration text otherwise
      E-4A   code under every answer except E4A-P4, which is a convention plus a file
      RES-1  code under every answer except RES1-P6, which is docstring-only
      RES-2  code under GQ-25 = not issuable;  docstring-only under GQ-25 = issuable
    Minimum total implementation if every decision takes its smallest-code answer: 0 lines
      of control logic and 5 documentation corrections.
    Maximum: changes to manifest_digest, _verify_permit, commit(), the register's write
      path, epoch5_invariants, one audit source, and 58 referencing artifacts.

BLOCKERS ALREADY FULLY CHARACTERIZED ..................... 5   (100%)
    "Fully characterized" is defined and tested in §12.2. All five meet all six criteria.

BLOCKERS DISSOLVED BY PHASE 2 EXAMINATION ................ 0
NEW INDEPENDENT BLOCKERS DISCOVERED ...................... 0
NEW LEGS ADDED TO EXISTING BLOCKERS ...................... 4   RES-1/U2, U3, U5; RES-2/L2

GOVERNANCE QUESTIONS IN THE MINIMUM SET .................. 14
DECISIONS REQUIRED ....................................... 13   (11 unconditional, 2 conditional)
IMPLEMENTATION OPTIONS ENUMERATED ........................ 30
CONSTRAINTS MEASURED ..................................... 26
DECISIONS MADE ...........................................  0
GOVERNANCE OUTCOMES RECOMMENDED ..........................  0
```

### 12.2 Does the repository possess enough information to conduct governance design without further technical investigation?

**Determination: YES for all five blockers, against the criterion below, with four named
technical unknowns that are not inputs to any of the thirteen decisions.**

The claim is only meaningful with a testable criterion, so one is stated and applied rather
than asserted. A blocker is **fully characterized** when all six hold:

| # | Criterion | E1-F3 | E-3 | E-4A | RES-1 | RES-2 |
|---|---|---|---|---|---|---|
| 1 | Current behavior established by execution, not by reading | ✓ P2-1 | ✓ P2-10 | ✓ P2-5 | ✓ P2-2/3/4/7/8 | ✓ P2-4/P2-5 |
| 2 | Every dependent source location identified by `file:line` | ✓ L1–L6 | ✓ §5.1 | ✓ §4.1–4.6 | ✓ §4.2–4.3 | ✓ §7.1 |
| 3 | The option space enumerated **exhaustively or by derivation**, not sampled | ✓ 8 by mechanism | ✓ 8 × 7 universes; 9 coherent pairs | ✓ 6; the register *shape* is fixed by the verifier and needs no decision | ✓ 5 unbound dimensions derived from a 6-input function — exhaustive by construction | ✓ 2 directions, 5 options |
| 4 | The governance questions isolated, and each one shown to be **necessary** (removing it leaves a remedy underdetermined) | ✓ GQ-1, GQ-3 | ✓ GQ-15…GQ-20 | ✓ GQ-6, 7, 8, 10, 13 | ✓ GQ-22 | ✓ GQ-25 (+GQ-26) |
| 5 | The consequences of each answer stated, including which options become impossible | ✓ §3.4 | ✓ §5.4 impact column | ✓ §4.6, §9.2 | ✓ §6.2, §9.4 | ✓ §7.3 C1–C11 |
| 6 | Constraints that bound every answer measured, not assumed | ✓ C-3, C-5, C-23, C-24 | ✓ C-4, C-5, C-6, C-15, C-16, C-17, C-25, C-26 | ✓ C-8…C-14 | ✓ C-7, C-19, C-20 | ✓ C-18, C-19 |

**Criterion 3 is the one that would most easily be claimed falsely, so its basis is stated
explicitly.** For RES-1 the enumeration is exhaustive *by derivation*, not by probing:
`manifest_digest` is a pure function of six named fields (`:548-568`, reproduced by probe
P2-9), so for a fixed pre-image and actor the set of documents a permit cannot distinguish is
exactly the set that agrees on those six. U1–U5 are that complement, partitioned by where the
free variation lives. A sixth unbound dimension could exist only if a document dimension exists
that is neither an identity-map key, an identifier value, a record body, a `category_seq` /
cursor value, a `NON_ALLOCATION_KEYS` value, `history` content, nor a new top-level key — and
the top-level key space is closed by the ledger's shape.

#### The four technical unknowns, and why none is a decision input

| # | Unknown | Why it could not be closed | Which decision it would inform |
|---|---|---|---|
| **UK-1** | Whether `register.sh` Phase 1 completes end-to-end once a verifying permit exists, and whether the nine dependent phases then pass | Closing it requires **executing** `register.sh --mint`, which allocates permanent identifiers and mutates the repository irreversibly. Phase 0 declined for the same reason (`PHASE0-E4A-ISSUANCE-PATH-REPORT.md` §7). What *is* measured is the refusal at the call site and the `|| fail` gating (`register.sh:206-259`). | **None.** It is a post-decision verification step, not an input: no answer to D-4…D-7 depends on it. |
| **UK-2** | How often production runs produce a `history`-only change (the empty-manifest write class) | Requires executing a mutating `ukb build --mint`. The class's **reachability** on the live ledger is measured (P2-5), which is what §7.3 C1–C2 rest on. | Informs the *cost* of D-12/D-13, not their admissible answers. Recorded in §7.3 C3 as explicitly not measured. |
| **UK-3** | Whether a two-hop indirect ledger write escapes `LEDGER-INV-01` after R-10 | Phase 1 §R-10 states the measurement is one call deep. Not re-measured here — it bounds the twelve *closed* defects, not the five open ones. | None. It is a Phase-1 residual, and Phase 1 is authoritative. |
| **UK-4** | Whether any candidate audit design can simultaneously satisfy tracked persistence (C-4 name ban), determinism (C-6 no wall clock), and the identity regress (C-3) | This is a **design** question, not an investigation question: the three constraints are measured, and whether their conjunction is satisfiable is discovered by attempting a design. | Informs D-9's feasibility. The constraints themselves are measured and supplied; the conjunction is for the designer. |

**One qualification on the YES, stated because it is the honest bound.** This phase added four
previously-unenumerated legs to two blockers (§1.2), which is direct evidence that
characterization was *incomplete* before it. The claim above is therefore not "characterization
can never deepen"; it is the narrower, testable claim that **all thirteen decisions can now be
taken from the artifacts in this repository, with every option's consequences and every binding
constraint supplied, and none of the four residual unknowns is an input to any of them.**

### 12.3 Live-ledger integrity and the D-c measurement

```
$ shasum -a 256 00-BOOK/DATA/id-ledger.json
8471e709b178a9a09909bca55f2e8eccb78161db8423026d1d26e4f35c41c20b     (before and after)
$ git status --porcelain 00-BOOK/DATA/
(0 lines)
```

Identical to the value Phase 1 §5.1 recorded. No file under `00-BOOK/DATA/` was created,
modified or removed. `commit()` was never invoked against the production ledger; every
live-ledger measurement used `load_preimage`, `build_manifest`, `plan` and `_verify_permit`,
all of which write nothing.

The D-c measurement, run **before and after** creating this report:

```
before : manifest a6827d8a…fae5  preimage 3a2a2532…2bcf4  head 77798202…  [by_path+9]
after  : manifest a6827d8a…fae5  preimage 3a2a2532…2bcf4  head 77798202…  [by_path+9]
git status PHASE2-GOVERNANCE-DEPENDENCY-MAP.md -> ?? (untracked)
```

Unchanged, because discovery reads the **git index** (`ukb.py:722-733`, `:750` —
`git ls-files --cached --exclude-standard`), and an untracked file is not a discovered
artifact. This is the precise form of C-10: an issuance transcription is stable across
working-tree edits and is invalidated by `git add` of an eligible artifact, not by editing.

---

## 13. Evidence index

Every probe. All fixture probes used `tempfile.mkdtemp()` ledgers; live-ledger measurements are
marked and are read-only.

| Probe | Establishes | Target | Mutating? |
|---|---|---|---|
| **P2-1** | E1-F3 still reproduces post-Phase-1: replay ACCEPTED after out-of-band restore; restore *through* the chokepoint REFUSED; `single_use` absent from the module | temp dir | temp only |
| **P2-2** | RES-1/U1 — a new record's body is unbound; forged body persisted under a permit issued for a different body | temp dir | temp only |
| **P2-3** | RES-1/U3 — identifier↔key assignment unbound; swap persisted | temp dir | temp only |
| **P2-4** | RES-2 + RES-1/U4 — one empty-manifest digest for `history` A, `history` B and a `version`+`discovered_volumes` bump; cross-authorization ACCEPTED; the same write REFUSED under `NO_ALLOCATION` | temp dir | temp only |
| **P2-5** | E-4A unchanged — register absent; all three `permit` values refused against a real allocating manifest; `history`-only append on the **live** ledger measures `allocating=False` with a digest equal to the no-op digest | **live ledger, read-only** | **no** |
| **P2-6** | Which permit fields `_verify_permit` consumes (9 read, 6 inert); `audit_event`/`emit_event` token count 0 | source | no |
| **P2-7** | RES-1/U2 — the key receiving a new identifier is unbound | temp dir | temp only |
| **P2-8** | RES-1/U5 — non-dict top-level keys escape `unmeasured_maps`; dict-valued keys do not | temp dir | temp only |
| **P2-9** | `manifest_digest`'s six inputs, printed from source — the basis of the exhaustiveness derivation | source | no |
| **P2-10** | E-3 unchanged — `UGA-INV-01` 27 / `UGA-INV-10` 27, identical sets, `audited == set(by_object)` `True`, 30 invariants / 28 passing | `uga_engine.build(mint=False)` | **no** |
| **P2-11** | C-10 / D-b / D-c — `ukb build --mint --plan` deterministic across runs and unchanged by an untracked file | **live repo, read-only** | **no** |
| **P2-12** | C-16 — 58 files reference `UGA-INV-10` before this report; 59 after, this document being the 59th | `grep -rl` | no |

Reproduction integrity: `build(mint=False)` allocates nothing and never calls `LA.commit`
(`uga_engine.py:2127` in `cmd_gate`; the same call in `build` is guarded by `mint`).
`ukb build --mint --plan` returns before every write (`ukb.py:1288-1298`). `register.sh` was
**not** executed. The two probe harnesses were written to `/tmp` and deleted after execution;
every probe transcript is reproduced inline above.

---

## 14. Stop condition

Phase 2 ends here.

- Five blockers: **characterized, not closed.**
- Thirteen decisions: **stated, not taken.**
- Thirty implementation options: **enumerated, none selected.**
- Twenty-six constraints: **measured, none imposed as policy.**
- No permit issuer, permit record, audit event, audit schema, mutation definition, issuance
  definition, ratification rule, temporal rule or authority structure was created.
- No governance outcome was recommended, ranked or preferred.
- FD-1, FD-2, FD-3′, FD-4, FD-5: **not answered, not assumed, not approached.**
- Live ledger: **byte-identical**, `sha256 8471e709…c20b`.

The next act is a governance decision. Nothing in this document prejudges which.
