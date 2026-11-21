# PHASE 2 — GOVERNANCE CLOSURE DETERMINATION

| Field | Value |
|---|---|
| Question | Does a governance specification exist that can simultaneously close `E-4A`, `E1-F3`, `E-3`, `RES-1`, `RES-2`, `FD-1`, `FD-2`, `FD-3′`, `FD-4`, `FD-5` **without introducing any new unresolved blocker**? |
| Answer | **YES — 42 consistent governance-complete models achieve full closure of the five residual blockers; 24 of those introduce no new blocker. Governance completion alone does NOT yield implementation readiness.** |
| Inputs | `PHASE0-GOVERNANCE-INDEPENDENT-DETERMINATION.md`, `PHASE05-GOVERNANCE-INDEPENDENT-REMEDIATION.md`, `PHASE1-GOVERNANCE-INDEPENDENT-IMPLEMENTATION-REPORT.md` |
| Corroborating established evidence | `PHASE2-GOVERNANCE-DEPENDENCY-MAP.md` probes **P2-1 … P2-12** (executed; transcripts recorded there), and the four Phase-0 subordinate reports cited by the inputs |
| Method | Enumeration over the governance axes the **current implementation can distinguish**, with equivalence merges proved from source, and closure evaluated per blocker against its own recorded defect statement |
| Code changed | **NONE.** No repository file was modified. The only file written is this document. |
| Governance content | **NONE CHOSEN.** No model is recommended, preferred, ranked by desirability or selected. Every governance root is treated as UNKNOWN throughout. |
| Live ledger | unchanged — `sha256 8471e709b178a9a09909bca55f2e8eccb78161db8423026d1d26e4f35c41c20b` |

### Compliance with the stated rules

| Rule | Compliance |
|---|---|
| 1. Do not implement code | No code written. §F states implementation *requirements* as consequences, never as instructions. |
| 2. Do not modify repository files | `git status --porcelain` shows this document as the only addition attributable to this phase. |
| 3. Do not propose preferred governance | Every model is presented with its closure profile and its new-blocker profile. No ordering by desirability appears; orderings that appear are dependency orderings derived from source. |
| 4. Do not recommend any answer | No recommendation. §G answers the five questions as counts and YES/NO. |
| 5. Enumerate all materially distinct models | §C enumerates the five closure-determining axes and the two modifier axes, proves each axis's admissible value set from source, and gives the exact product. |
| 6. Treat every governance root as unknown | FD-1…FD-5 are quantified over, never assigned. |
| 7. Every claim backed by established source references and executable evidence | §H maps every load-bearing claim to a `file:line` or to an established probe ID. No new probe was required; no claim rests on unexecuted reasoning without being labelled as derivation. |
| 8. Merge answers that collapse to the same implementation consequences | §C.1 proves **five** collapses (FD-1, FD-4, T1≡T4, T3≡B2, I1≡I2≡I3) and merges them. Without these merges the enumeration is **unbounded** — proved in §C.1. |
| 9. Record new blockers | §C.9 — six recorded: NB-1 … NB-6. |
| 10. Record unresolved blockers | §D — every `UNRESOLVED` and `PARTIALLY CLOSED` cell, with the axis value that produces it. |

---

## 0. The FD roots: what the inputs actually establish

The three input documents reference `FD-1`, `FD-2`, `FD-3′`, `FD-4`, `FD-5` **twelve times and define them nowhere**. Verified by exhaustive search across the repository: every occurrence of the label `FD-1` outside this phase's own documents is a *status assertion* (`"not answered"`), not a definition.

What the inputs **do** establish is the five roots' **ranges**, stated twice and consistently:

> *"a choice among mutually exclusive answers to **who may authorize**, **what an authorization means**, **when it expires**, **which authority owns the ledger**, or **what counts as a mutation or an audit event**"*
> — `PHASE05-GOVERNANCE-INDEPENDENT-REMEDIATION.md:224-226`

> *"Each of the five governance roots ranges over **who** / **what** / **when** / **which authority** / **which domain rule**"*
> — `PHASE05-GOVERNANCE-INDEPENDENT-REMEDIATION.md:247`

> *"who may authorize a write, what a permit means, when authorization expires, or which authority owns the ledger"*
> — `PHASE0-E1-ATOMICITY-REPORT.md:17`, restated at `:375`

The two enumerations are positionally identical and five-valued, which fixes the mapping:

| Root | Range, as established by the inputs | Source |
|---|---|---|
| **FD-1** | **WHO** may authorize a write — issuer identity | `PHASE05:224`, `:247`; `PHASE0-E1:17` |
| **FD-2** | **WHAT** an authorization means — permit semantics and binding | `PHASE05:224-225`, `:247` |
| **FD-3′** | **WHEN** an authorization expires — temporal legitimacy | `PHASE05:225`, `:247` |
| **FD-4** | **WHICH AUTHORITY** owns the ledger | `PHASE05:225`, `:247` |
| **FD-5** | **WHICH DOMAIN RULE** — what counts as a mutation, and what counts as an audit event | `PHASE05:225-226`, `:247` |

Corroborated by the inputs' own per-blocker root attribution: `PHASE0-GOVERNANCE-INDEPENDENT-DETERMINATION.md` §5 assigns `E1-F3 → issuance semantics`, `E-3 → domain rules`, `E-4A → issuance semantics, issuer identity, temporal legitimacy`.

**One qualification, stated because the determination rests on it.** The *label-to-range* assignment above is an **inference from positional correspondence**, not a quotation. It is load-bearing only for naming. Every closure result in §D is computed over the **ranges** — over *who*, *what*, *when*, *which authority*, *which domain rule* — so **the entire determination is invariant under any relabeling permutation of FD-1…FD-5.** If a superseding artifact assigns the labels differently, §D's values do not move; only §B's node captions do.

---

## A. Residual blocker inventory

### A.1 Exact blocker list

Five, exactly as `PHASE1-GOVERNANCE-INDEPENDENT-IMPLEMENTATION-REPORT.md` §6.2 records, each re-verified open against the post-Phase-1 tree by execution.

| ID | Defect, stated as the discrepancy it is | Root(s) its remedy touches |
|---|---|---|
| **E-4A** | No production path creates, appends to, updates or persists the permit register. Consumption is complete and reached; issuance does not exist in any form. Because `permit` is mandatory with no default, this is a **total block on every identity-ledger write**, not a permissive gap. | FD-1, FD-2, FD-3′ |
| **E1-F3** | Spent-ness is *derived* from mutable state, so restoring the ledger's pre-image re-validates a permit. The module states the opposite: *"the same permit cannot be replayed. No spent-permit registry is required, and none is created."* | FD-2, FD-3′ |
| **E-3** | `UGA-INV-10 EVERY_MUTATION_HAS_AUDIT_EVENT` is unfalsifiable in the leg it names (`audited ≡ set(by_object.keys())`) and a verbatim duplicate of `UGA-INV-01` in the leg that discriminates. | FD-5 |
| **RES-1** | A permit binds a **six-field projection**, not the document. For a fixed pre-image and actor, the permit cannot distinguish members of an equivalence class with **five** free dimensions. | FD-2 |
| **RES-2** | `_verify_permit` does not refuse a permit over an all-empty manifest, while the sentinel's docstring states such a permit *"must not be issuable."* The empty-manifest digest is **one universal value** per `(actor, pre-image)`. | FD-2 |

### A.2 Source references

Post-Phase-1 line numbers (`00-BOOK/tools/ledger_authority.py`, 933 lines; the Phase-0 references are stale — mapping in `PHASE2-GOVERNANCE-DEPENDENCY-MAP.md` §0.1).

| Blocker | Primary source | Secondary source |
|---|---|---|
| **E-4A** | `PERMIT_REGISTER_NAME :507`; `permit_register_path :603-605`; `load_permit_register :608-631` — the **single** register access, read-only; register absent from `00-BOOK/DATA/` | `commit :841` (`permit` mandatory, no default); rationale `:851-855`; `register.sh:216` passes no `--permit`; three inert CLI flags (`ukb.py:2497`, `ukb.py:2555`, `uga_engine.py:2079`); the only writer is the test fixture `platform/tests/test_ledger_authority.py:61-87` |
| **E1-F3** | `preimage_digest :570-577` — the claim, verbatim: *"performing the allocation changes the pre-image … the same permit cannot be replayed. No spent-permit registry is required, and none is created — spent-ness is DERIVED from two artifacts that are already committed."* | the sole replay control `:742-749`; refusal text `:746-747` cannot distinguish *spent* from *moved*; `single_use` absent from the module (probe **P2-6**) |
| **E-3** | `uga_engine.py:1331-1335` — the four lines of the invariant | event construction `uga_engine.py:1841-1858` (unconditional, total over `by_object`, `action` always `IDENTITY_MINTED`); `uga-declaration.json` (`fails_closed: true`); `cmd_gate uga_engine.py:2125-2161` blocks on every failing invariant; `adr/0017-…:15` states the mechanism outright |
| **RES-1** | `manifest_digest :548-568` — a pure function of six named fields | `allocated` built at `:396-400` (identifier **values** only); `_identifier_index :142-149`; `NON_ALLOCATION_KEYS :103-116`; `unmeasured_maps :417-420` (`isinstance(v, dict)` only); `_record_index :151-162`; the anti-forgery rationale at `:490-497` |
| **RES-2** | `_NoAllocation` docstring `:519` — *"a permit for an empty manifest would authorize nothing and must not be issuable."* | `_verify_permit :714-804` reads neither `manifest["allocating"]` nor `manifest["total_allocations"]` on the permit path; the sentinel branch `:684-712` is the only reader; scope checks `:767-783` are **vacuous** on an empty manifest |

### A.3 Activation conditions

| Blocker | Latent or active today | Activation condition | Established evidence |
|---|---|---|---|
| **E-4A** | **ACTIVE** — it is the blocking condition | none; it blocks now. All three admissible `permit` values refused against a real allocating manifest measured from the live ledger | probe **P2-5** |
| **E1-F3** | **LATENT** | requires ≥1 permit to have existed **and** an out-of-band restore. Restoration *through* the chokepoint is refused after Phase 1's `R-4` (append-only removal check `:290-296`); only a plain file write, `git checkout`, `git revert`, a stash pop or a backup restore re-validates | probe **P2-1** — replay ACCEPTED after byte restore; restore via chokepoint REFUSED |
| **E-3** | **ACTIVE and INDEPENDENT of every permit decision** | none. Measured failing today with zero permits in existence: `UGA-INV-01 FAIL measured=6804 violations=27`, `UGA-INV-10 FAIL measured=5207 violations=27`, **identical violation sets**, `audited == set(by_object) True` (5374 ≡ 5374) | probe **P2-10** |
| **RES-1** | **LATENT** | requires one verifying permit. Then all five dimensions are exercisable: forged new-record body (**P2-2**), wrong key (**P2-7**), swapped assignment (**P2-3**), different `history` content (**P2-4**), non-dict rogue top-level keys under a **no-op** permit (**P2-8**) — each persisted with `authorization=PERMIT` and no error | probes P2-2, P2-3, P2-4, P2-7, P2-8 |
| **RES-2** | **LATENT** | requires one permit over an empty manifest. The write class it authorizes is reachable **on the production ledger**: a `history`-only append measures `allocating=False, total=0` with a digest **equal to the no-op digest** | probe **P2-5** (live, read-only), **P2-4** (end-to-end through `commit()`) |

**The activation fact that shapes every model.** `permit` is mandatory with no default (`:841`), so no production write reaches `writer` (`:895`). E1-F3, RES-1 and RES-2 are therefore latent-not-absent, and **any** value of the issuance axis that closes E-4A activates all three simultaneously. This is the same mechanism `PHASE0-E2-CORRESPONDENCE-REPORT.md` recorded as E2-F7 for the twelve now-closed defects, and `PHASE05:§F.4` restated: *"Supplying any issuance path activates … nine of the twelve … simultaneously."* It is a measured consequence, not sequencing advice.


---

## B. Governance decision graph

### B.1 The five roots as nodes, with the code each one binds

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ FD-1  WHO may authorize                                                          │
│   binds: nothing the verifier reads.                                             │
│   `_verify_permit` reads no `issuer`, no `signature`, no `issued_at` (P2-6).      │
│   OUT-DEGREE 0 into the implementation.                    → collapses (§C.1-M1)  │
└───────────────┬─────────────────────────────────────────────────────────────────┘
                │ constrains only WHO performs the (absent) issuance act
                ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ FD-2  WHAT an authorization means                                                │
│   binds: `manifest_digest :548-568`  (RES-1)                                     │
│          `_verify_permit :714-804`   (RES-2 · empty manifest)                    │
│          `preimage_digest :570-577`  (E1-F3 · consumption)                       │
│   THE LOAD-BEARING ROOT: three of five blockers resolve here.                    │
└───┬───────────────────────┬──────────────────────────┬──────────────────────────┘
    │ binding (axis A)      │ empty-manifest (axis D)  │ replay (axis B)
    ▼                       ▼                          ▼
  RES-1                   RES-2                     E1-F3
    │                       │                          │
    │  ┌────────────────────┘                          │
    │  │ interaction: under A3 the empty-manifest       │
    │  │ digest names ONE document, so D1's harm        │
    │  │ vanishes while D1's CLAIM stays false          │
    │  ▼                                               │
┌─────────────────────────────────────────────────────────────────────────────────┐
│ FD-3′  WHEN an authorization expires                                             │
│   binds: `expires_at :785-797`  (implemented, NO PRODUCER — C-14)                │
│          `preimage_digest :742-749` already implements state-bound expiry         │
│          `head :751-762` already implements repository-state expiry (elective)    │
│   Every value either collapses into FD-2's replay axis or into the status quo.    │
│                                                            → collapses (§C.1-M3/M4)│
└─────────────────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────────────────┐
│ FD-4  WHICH AUTHORITY owns the ledger                                            │
│   binds: `permit.get("actor") != actor` :728-732 — string equality, NO ALLOW-LIST │
│   Any authority name verifies identically. OUT-DEGREE 0.    → collapses (§C.1-M2) │
└─────────────────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────────────────┐
│ FD-5  WHICH DOMAIN RULE — what is a mutation, what is an audit event              │
│   binds: `uga_engine.py:1331-1335` (the invariant)                                │
│          `uga_engine.py:1841-1858` (the derived event source)                      │
│          `uga-declaration.json`, `cmd_gate :2125-2161`                             │
│   INDEPENDENT of FD-1…FD-4 — proved by P2-10 (E-3 fails with zero permits).       │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### B.2 Dependencies

Each edge is derived from source or from an established measurement. `X → Y` reads *"Y cannot be specified, or cannot be implemented without invalidating work, until X is answered."*

| Edge | Nature | Basis |
|---|---|---|
| **FD-2(binding) → FD-1/FD-2(issuance)** | Hard ordering. Widening the binding changes every `manifest_digest`, invalidating every issued permit, **and** changes what `plan()` emits — and `plan()`'s docstring defines issuance as *"a transcription of this output rather than an independent act of measurement"*. | `:548-568`; `:648-661`; the identical rule Phase 1 §4.2 recorded for `R-5a` |
| **FD-2(empty-manifest) → FD-2(non-allocating authorization)** | Hard co-decision. `D`=not-issuable removes the **only** authorization path for a reachable write class, because `R-9` (`:696-707`) already refuses that class under `NO_ALLOCATION`. | probes P2-4, P2-5; Phase 1 §R-9; `PHASE05:§F.4` recorded the coupling in advance |
| **FD-2(replay) → FD-2(register writability)** | Shared substrate. Recording use *in the register* makes the enforcer a writer of the artifact it enforces, against the stated separation *"commit() ENFORCES an authorization it does not DECIDE"*. | `:490-497`; `:608-631` |
| **FD-1/FD-2(issuance) → FD-5(tracked audit artifact)** | Ordering, via the identity regress. A new tracked audit artifact is a discovered object → needs an identity → needs an allocation → needs a permit → needs the register. The regress is documented and **terminated at one file**; a second tracked governance artifact re-opens it and is only resolvable once an issuance path exists. | `:499-506`; `uga_engine` discovery over `git ls-files --cached` (`ukb.py:722-733`) |
| **FD-5 ⊥ FD-1…FD-4** | **Independence**, not dependency. E-3 is measured failing with no permit in existence. | probe **P2-10** |
| **FD-3′ → nothing** | No edge. Every temporal value collapses (§C.1-M3/M4); `expires_at` bounds a replay window without closing it. | `PHASE2-GOVERNANCE-DEPENDENCY-MAP.md` §3.4 path A7 |

### B.3 Contradictions

Recorded, not resolved. Each is a pair of propositions that cannot both hold.

| ID | Contradiction | Evidence |
|---|---|---|
| **CX-1** | The permit layer's anti-forgery rationale — *"Forging a permit therefore requires knowing every identifier and counter advance the run will produce — which is the same work as reviewing the allocation"* (`:490-497`) — versus the measured fact that a permit does **not** name which key receives which identifier, nor any new record's body. A reviewer who approves `UCOS-OBJ-000002 → engine/legit.py` has approved `UCOS-OBJ-000002 → totally/other/path.py` equally. | probe **P2-7**, **P2-3**, **P2-2** |
| **CX-2** | `:519` (*"a permit for an empty manifest … must not be issuable"*) versus `:714-804` (no such refusal). **This is RES-2.** It is listed as a contradiction because it is a conflict *internal to the current source*, which every model must dispose of in one direction or the other. | probe **P2-4** |
| **CX-3** | `:570-577` (*"the same permit cannot be replayed … No spent-permit registry is required"*) versus the measured replay after restore. **This is E1-F3**, likewise an internal contradiction every model must dispose of. | probe **P2-1** |
| **CX-4** | A register-as-audit-log answer (`Aud4`) requires permit **records**; a rule-derived-admission answer (`I-D`) abolishes them, since `_verify_permit` resolves `permit_id` against the register at `:714-721`. The two cannot both be taken. | `:714-721` |
| **CX-5** | Runtime-only records (`Aud5`, `B2c`) versus the repository's own asserted invariant property `repository_evaluable` — *"Every predicate is decidable from tracked repository state alone"* — because `.runtime/` is gitignored and a fresh clone starts at `seq = 1`. | `00-BOOK/DATA/mutation-governance-boundary.json` `classification_rules.properties`; `.gitignore:12`; `governance_telemetry.py:44-52`, `:79` |
| **CX-6** | A bytes-level binding (`A4`) versus `commit()`'s document-level comparison, which exists **because** three serializers over one document are not byte-equivalent (`_canonical` 1 786 167 bytes vs both production writers at 2 274 511, byte-identical to each other). A bytes binding would refuse correct writes unless one canonical serializer is mandated — an additional decision. | `:920-927`; Phase 1 §R-11 measurements |

### B.4 Cycles

| ID | Cycle | Terminated? |
|---|---|---|
| **CY-1** | *Identity regress.* A new tracked governance artifact → is a discovered object → requires an identity → requires an allocation → requires a permit → requires the register → which is itself a tracked artifact. | **Terminated at one file by construction**, and the termination is documented in source: *"A SINGLE append-only file, never one file per permit: a new tracked file is an anonymous UCOS-UGA-001 object, and clearing that anonymity requires an allocation, which requires a permit, which would be another new file. One register terminates that regress at one object"* (`:499-506`). Any model adding a **second** tracked governance artifact (a spent-register, a tracked audit log) re-enters the cycle and must terminate it again — which is possible **only after** an issuance path exists. This is the ordering edge in §B.2. |
| **CY-2** | *Self-auditing register.* If audit events are permit records (`Aud4`) and the register must itself be audited (register-integrity answers), the register audits itself. | **Not terminated by the current implementation.** `load_permit_register` (`:608-631`) verifies readability and shape only — never provenance. Recorded as NB-3/NB-2 territory in §C.9. |
| **CY-3** | *Gate-green cycle.* `UGA-INV-01` reports 27 anonymous objects; clearing them requires minting identities; minting requires a permit; the permit register does not exist; and `cmd_gate` blocks on every failing invariant. The gate cannot go green without E-4A, and the gate's own message says so, naming the authorization flow rather than the verb. | **Not a governance cycle** — it is E-4A's activation condition observed from the gate. Terminated by any value of the issuance axis. `uga_engine.py:2143-2153`, `:2154-2159`; probe P2-10. |

**No cycle among FD-1…FD-5 themselves.** The decision graph over the five roots is a DAG: FD-1 and FD-4 have out-degree 0 into the implementation, FD-3′ collapses, FD-5 is independent, and FD-2's three sub-axes are pairwise independent except for the two recorded interactions (A×D on RES-2's harm, B×register-writability). Proof of acyclicity is by the collapses in §C.1 plus the independence measurement P2-10.

---

## C. Governance model enumeration

### C.1 Five proved collapses — without which the enumeration is unbounded

Rule 8 requires merging answers with identical implementation consequences. Applied first, because **the raw enumeration has no finite cardinality**: FD-4 ranges over authority names, and `_verify_permit` compares `permit["actor"]` to the caller's `actor` string with **no allow-list, no registry lookup and no format constraint** (`:728-732`), so the raw model space is as large as the set of strings. The merges below are what make the space finite and countable.

| # | Merge | Proof | Effect on cardinality |
|---|---|---|---|
| **M1** | **Every FD-1 assignment collapses to one value.** All answers to *who may issue* have identical implementation consequences at verification time. | `_verify_permit` reads no `issuer`, `signature` or `issued_at` — probe **P2-6**, source-derived over `:664-804`. Validity is *presence in the register*, nothing more. Two permits identical in the nine read fields verify identically regardless of who wrote them. | FD-1: **unbounded → 1** |
| **M2** | **Every FD-4 assignment collapses to one value.** *Which authority owns the ledger* has no implementation consequence. | `:728-732` is string equality against the caller-supplied `actor`. No allow-list exists anywhere; the three production actor strings (`ukb.py:1287`, `:2382`, `:2403`, `uga_engine.py:2098`) are literals passed by the callers, not values validated against a register. | FD-4: **unbounded → 1** |
| **M3** | **FD-3′ = "expiry is repository-state-bound"** ≡ **"a permit never expires."** | With `expires_at` absent, a permit is valid exactly while the pre-image is unchanged, because `:742-749` refuses on pre-image movement. State-bound expiry is therefore already implemented and is what "no expiry" *means* operationally. `head` (`:751-762`) adds an elective second state binding. | FD-3′: 4 → 2 |
| **M4** | **FD-3′ = "expiry occurs on use"** ≡ **FD-2's replay axis value B2.** | Both are one mechanism: record consumption, then refuse. Expressing it as a temporal rule and as a consumption rule produces the same code. | FD-3′: 2 → 1 closure-relevant value + 1 modifier (`T-instant`, which requires a clock authority — C-14: `expires_at` has no producer) |
| **M5** | **Issuance by an in-repo tool ≡ by a hand-authored convention ≡ by CI** for every closure value. | Closure of every row depends on the register's *existence and content*; all three produce byte-identical registers, and M1 shows the verifier cannot distinguish their origin. They differ in FD-1's assignment, which M1 already collapsed. | issuance: 4 → **2** (`I-R` register-based with three recorded sub-variants; `I-D` rule-derived, which is **not** merged because it changes `_verify_permit`'s register lookup at `:714-721`) |

**Consequence.** FD-1 and FD-4 are **provably redundant with respect to every closure value in §D** — they must still be answered for a governance specification to be *complete*, but no assignment to either changes any cell. This is recorded again in §E.4.

### C.2 The five closure-determining axes

Each axis's admissible value set is derived from what the implementation can distinguish, not from imagination.

| Axis | Root | Values | Source of the value set |
|---|---|---|---|
| **I** — issuance path | FD-1 · FD-2 | `I-0` none · `I-R` register-based · `I-D` rule-derived admission | `load_permit_register :608-631`; `:714-721` (register match mandatory today) |
| **A** — authorization binding | FD-2 | `A-0` none · `A1` projection ratified · `A2` projection + named dimensions · `A3` whole document · **`A4` bytes (CONTRADICTED — CX-6)** | `manifest_digest :548-568` is a pure function of six named fields; the free dimensions U1–U5 partition its complement |
| **B** — replay semantics | FD-2 · FD-3′ | `B-0` none · `B1` reusable (claim corrected) · `B2` consumed, durable record · `B2c` consumed, runtime-only record | `preimage_digest :570-577`; `single_use` unread (P2-6); `governance_telemetry.append_audit :133-160`; `.gitignore:12` |
| **D** — empty-manifest semantics | FD-2 | `D-0` none · `D1` issuable (claim amended) · `D2` not issuable + alternative authorization for the non-allocating class · `D3` not issuable + class prohibited | `:519` vs `:714-804`; `:696-707` (`R-9`); scope vacuity `:767-783` |
| **Aud** — mutation + audit semantics | FD-5 | `Aud-0` none · `Aud1` act-level, independently sourced, tracked · `Aud2` measurement authoritative (rename/split) · `Aud3` retire the invariant · `Aud4` permit records **are** the audit log · `Aud5` act-level, independently sourced, runtime-only | `uga_engine.py:1331-1335`, `:1841-1858`; the nine candidate `(mutation, audit)` pairs P-0…P-9 established in `PHASE2-GOVERNANCE-DEPENDENCY-MAP.md` §5.4 |

**Sub-merge inside `Aud1`.** The established pairs `P-2, P-3, P-4, P-5, P-7, P-8` all pair an act-or-state mutation universe with an independently-sourced tracked event log. For **E-3's closure** they are equivalent: E-3's defect is that the measurement does not measure what its name claims and duplicates `UGA-INV-01`, and any independently-sourced event log removes both properties. They differ in *coverage breadth*, which is the model's own scope choice under FD-5 (GQ-16), not a residual blocker. Merged into `Aud1` with the six sub-variants recorded.

**Sub-merge inside `B2`.** `B2a` (mark the register) and `B2b` (a separate tracked record) both produce a clone-surviving, repository-evaluable use record and both close E1-F3. They differ in file count — which is a CY-1 modifier and a documented-property change (`B2a` makes the enforcer a writer of the register, against `:490-497`), not a closure value. Merged, sub-variants recorded. `B2c` is **not** merged: it is clone-scoped and contradicts `repository_evaluable` (CX-5).

### C.3 Two modifier axes

Answered for completeness of a governance specification; **provably no effect on any cell in §D**.

| Axis | Root | Values | Effect |
|---|---|---|---|
| **R** — register trust | FD-1 · FD-2 | `R1` presence in the register is sufficient · `R2` integrity/authenticity binding required | `R2` requires a trust anchor the repository does not have → **NB-2**. `R1` requires no code. `load_permit_register :608-631` checks readability and shape only. |
| **T** — temporal | FD-3′ | `T-state` (≡ no expiry, M3) · `T-instant` (populate `expires_at`) | `T-instant` requires a clock authority; `expires_at` has **no producer anywhere in the repository** (probe P2-6, `:785-797`). Neither closes nor opens any blocker. |

### C.4 Exact model counts

```
RAW ENUMERATION (before merges) ....................... UNBOUNDED
    proof: FD-4 ranges over authority-name strings and `:728-732` is unconstrained
           string equality with no allow-list.  Merges M1/M2 are what make counting
           possible at all.

AFTER MERGES M1–M5:

  GOVERNANCE-COMPLETE MODELS (every axis answered, no null value)
      I(2) × A(3) × B(3) × D(3) × Aud(5)  ............... 270
      of which internally contradictory (CX-4: I-D × Aud4) ...  27
      CONSISTENT GOVERNANCE-COMPLETE MODELS ............. 243

  WITH THE CONTRADICTED BINDING VALUE A4 INCLUDED
      I(2) × A(4) × B(3) × D(3) × Aud(5)  ............... 360   (90 of them A4-bearing,
                                                                 all CONTRADICTED by CX-6)

  INCLUDING MODELS THAT DECLINE AN AXIS (null values, for §D completeness)
      I(3) × A(4) × B(4) × D(4) × Aud(6)  ............. 1 152

  MODIFIER MULTIPLIER (R × T) — no closure effect ...... × 4
      consistent governance-complete specifications ..... 972
```

### C.5 Model attributes — axis `I` (issuance)

| | `I-0` no issuance path | `I-R` register-based issuance | `I-D` rule-derived admission |
|---|---|---|---|
| **Assumption** | authorization exists but is not producible | a permit is a record in one append-only sibling file | a permit is a *rule* admitting a class of manifests; no record is created |
| **Issuer identity** | undefined | any FD-1 answer — verifier cannot distinguish (M1). Sub-variants: in-repo tool · hand-authored convention · CI-issued | the rule's author; no per-act issuer |
| **Permit lifecycle** | none | created → verified → (consumed per axis B) | evaluated per write; nothing is created or consumed |
| **Code touched** | none | none in the verifier; the register acquires a producer | **`:714-721`** — the mandatory register match becomes optional or is replaced |
| **Closure of E-4A** | **UNRESOLVED** | **CLOSED** | **CLOSED by dissolution** — the blocker's subject ceases to exist |
| **New blocker** | — | none under `R1`; **NB-2** under `R2` | **NB-6** — `permit_id`, the register, and the three `--permit` CLI flags become dead interface; RES-1's equivalence-class problem becomes the rule's admission predicate |

### C.6 Model attributes — axis `A` (authorization binding)

| | `A1` projection ratified | `A2` named dimensions | `A3` whole document | `A4` bytes |
|---|---|---|---|---|
| **Assumption** | the six-field projection is what an authorization is *about* | the projection plus the dimensions a reviewer is assumed to be approving | the authorization names exactly one proposed document | the authorization names exactly one byte sequence |
| **Binding semantics** | `actor`, identifier **values** per map, counter/cursor transitions, unmeasured-map names, total | + key→identifier pairs, + new-record bodies | digest over the whole proposed document | digest over persisted bytes |
| **Legs closed** | none of U1–U5 | U1, U2, U3 | U1–U5 | U1–U5 |
| **Legs left open** | U1 new-record body · U2 key · U3 assignment · U4 `history` content · U5 `version`/`discovered_volumes` values and non-dict top-level keys | U4, U5 | none | none |
| **Requires amending a source claim** | **yes** — CX-1's rationale at `:490-497`, and the reviewability premise *"The digest binds exactly; a human cannot read a digest"* (`:763-766`) | partially | no | no |
| **Closure of RES-1** | **PARTIALLY CLOSED** | **PARTIALLY CLOSED** | **CLOSED** | **CONTRADICTED** (CX-6) |
| **Established evidence** | P2-2, P2-3, P2-4, P2-7, P2-8 | same | derivation from `:548-568` being a six-input pure function (P2-9) | Phase 1 §R-11 byte measurements; `:920-927` |

### C.7 Model attributes — axis `B` (replay) and axis `D` (empty manifest)

| | `B1` reusable | `B2` consumed (durable) | `B2c` consumed (runtime) |
|---|---|---|---|
| **Replay semantics** | an authorization is valid for **every** occurrence of its pre-image | first use exhausts it; use is recorded in tracked state | first use exhausts it; the record lives in `.runtime/governance` |
| **Disposition of CX-3** | the claim at `:570-577` is amended | the claim becomes true | the claim becomes true **per clone** |
| **Bounded-reuse variant** | — | merged: `n` uses is the same mechanism with a different constant (M4-adjacent) | merged likewise |
| **Interaction with A** | under `A3` replay is **idempotent by construction** (the permit names one document); under `A1` replay re-authorizes a class | none | none |
| **Closure of E1-F3** | **CLOSED** (by ratification + claim correction) | **CLOSED** | **PARTIALLY CLOSED** — clone-scoped; CX-5 |
| **New blocker** | none | none (`B2a` changes the documented enforcer/decider separation `:490-497`; `B2b` re-enters CY-1) | **NB-5** |

| | `D1` issuable | `D2` not issuable + alternative | `D3` not issuable + prohibited |
|---|---|---|---|
| **Empty-manifest semantics** | a permit may authorize a non-allocating mutation | such writes are authorized by a distinct mechanism | such writes do not occur |
| **Disposition of CX-2** | the claim at `:519` is amended | the claim becomes true | the claim becomes true |
| **Residual harm** | one digest per `(actor, pre-image)` covers `history` appends, `version` and `discovered_volumes` rewrites — **unless `A3`**, under which the permit names one document. Scope narrowing is unavailable either way: both scope checks are vacuous on an empty manifest (`:767-783`) | none | none |
| **Closure of RES-2** | **CLOSED** (ratified) | **CLOSED** | **CLOSED** |
| **New blocker** | none | none | **NB-1** — a write class reachable on the production ledger with no authorization path, given `permit` is mandatory (`:841`) |

### C.8 Model attributes — axis `Aud` (mutation and audit semantics)

| | `Aud1` independent + tracked | `Aud2` measurement authoritative | `Aud3` retire | `Aud4` register = audit log | `Aud5` independent + runtime |
|---|---|---|---|---|---|
| **Mutation semantics** | one of the established pairs P-2…P-8: an act, or a state transition, as the mutation element | unchanged; the **name** is corrected to what is measured (identity presence) | none required | each `commit()` act | as `Aud1` |
| **Audit semantics** | events sourced independently of the audited state, persisted in tracked state | the current derived projection is retained and re-labelled | no audit measurement | a permit record per authorized write | events in `.runtime/governance` |
| **Relation to declared classes** | **additional** to the six declared subject classes in `mutation-governance-boundary.json`, never a replacement — the declared universe is over *subjects*, this is over *acts* | consistent with the declared classes as-is | — | consistent, with `CORPUS_REGISTRATION` naming the ledger explicitly | as `Aud1` |
| **Constraints it must satisfy** | `*-audit.json` forbidden under `00-BOOK/DATA` (`governance_telemetry.py:187-207`); no wall clock in a tracked canonical artifact (`uga_engine.py:1911-1915`); CY-1 → requires `I ≠ I-0` first | none | none | — | violates `repository_evaluable` (CX-5) |
| **Closure of E-3** | **CLOSED** | **CLOSED** | **CLOSED by deletion** | **CLOSED** | **PARTIALLY CLOSED** |
| **Assumption it forces** | audit coverage of ledger mutation is required | the invariant's name may be corrected | audit coverage is **not** required | every authorized write has a permit record | audit memory need not survive a clone |
| **New blocker** | none, given the ordering edge is honoured | none | none | **NB-3** — writes under `NO_ALLOCATION` produce no permit record, so an act class is unauditable unless the sentinel is also abolished, which is a further decision | **NB-5** |

### C.9 New blockers created by governance answers

Rule 9. Each is a blocker that does not exist today and would exist under the stated answer.

| ID | New blocker | Created by | Basis |
|---|---|---|---|
| **NB-1** | A write class reachable on the production ledger with **no** authorization path — `history` appends, `version` and `discovered_volumes` changes. Structurally identical to E-4A. | `D3` | `permit` mandatory `:841`; `R-9` refuses the class under the sentinel `:696-707`; class reachability measured on the live ledger (**P2-5**) |
| **NB-2** | No trust anchor exists for register authenticity. Introducing one adds a tracked artifact (CY-1) and a key-management surface the repository has none of. | `R2` | `load_permit_register :608-631` verifies readability and shape only |
| **NB-3** | An unauditable act class: writes accepted under `NO_ALLOCATION` create no permit record, and the sentinel *"is issued by nobody, appears in no register, names no actor and has no expiry"*. | `Aud4` | `:514-529`, `:684-712`; Phase 1 §R-9 and §6.3 (the sentinel branch was revived from dead code by `R-5a`) |
| **NB-4** | A bytes binding cannot be satisfied without mandating one canonical serializer, and `commit()` compares documents precisely because the three are not byte-equivalent. | `A4` | CX-6; `:920-927`; Phase 1 §R-11 |
| **NB-5** | Clone-dependent authorization memory / clone-dependent invariant measurement, contradicting the asserted `repository_evaluable` property. | `B2c`, `Aud5` | CX-5; `.gitignore:12`; `governance_telemetry.py:44-52` |
| **NB-6** | Dead authorization interface: `permit_id`, the register, `load_permit_register`, and the three `--permit` CLI flags lose their referents; and RES-1's equivalence-class problem reappears as the admission rule's predicate. | `I-D` | `:714-721`; `ukb.py:2497`, `ukb.py:2555`, `uga_engine.py:2079`; `:648-661` |


---

## D. Closure matrix

### D.0 Value definitions and the factorization theorem

| Value | Definition |
|---|---|
| **CLOSED** | After the model's answers, the blocker's defect is gone **and** no source claim about it remains false. Ratification counts, provided the model also disposes of the contradicting source claim (CX-1/CX-2/CX-3) — that disposal is part of the axis value's definition, not an extra. |
| **PARTIALLY CLOSED** | The defect is removed on some measured legs but not all, or removed only within a scope narrower than the repository. |
| **UNRESOLVED** | The model's answers leave the defect intact. |
| **CONTRADICTED** | The model's answers make the blocker unclosable, or two answers inside the model conflict. |

**Factorization theorem.** Each row's value is a function of **one** axis, with two recorded interactions. Therefore the matrix over all 1 152 models is fully determined by the five sub-matrices below, and the explicit column table in §D.2 is a spanning sample rather than a truncation.

```
  value(E-4A)  = f(I)
  value(E1-F3) = f(B)                     [interaction: A3 makes B1's replay idempotent]
  value(E-3)   = f(Aud)                   [independent of I, A, B, D — probe P2-10]
  value(RES-1) = f(A)
  value(RES-2) = f(D)                     [interaction: A3 removes D1's residual harm]
```

Proof of single-axis dependence, per row: E-4A is an existence question about the register, and only axis `I` creates or dissolves it. E1-F3 is a question about whether use is recorded, and only axis `B` records it. E-3 is measured failing with zero permits in existence (**P2-10**), so no permit axis can move it; only `Aud` changes the measurement. RES-1 is the content of `manifest_digest`, which only axis `A` changes. RES-2 is the issuability of an empty-manifest permit, which only axis `D` decides. The two interactions are recorded and do not change any value from CLOSED to UNRESOLVED or vice versa — they change *residual harm*, noted in the cells.

### D.1 The five factored sub-matrices — complete for all models

**E-4A × axis I**

| `I-0` | `I-R` | `I-D` |
|---|---|---|
| UNRESOLVED | **CLOSED** | **CLOSED** (by dissolution; NB-6) |

**E1-F3 × axis B**

| `B-0` | `B1` | `B2` | `B2c` |
|---|---|---|---|
| UNRESOLVED | **CLOSED** (ratified; `:570-577` amended) | **CLOSED** | PARTIALLY CLOSED (clone-scoped; NB-5) |

**E-3 × axis Aud**

| `Aud-0` | `Aud1` | `Aud2` | `Aud3` | `Aud4` | `Aud5` |
|---|---|---|---|---|---|
| UNRESOLVED | **CLOSED** | **CLOSED** | **CLOSED** (by deletion) | **CLOSED** (NB-3; CONTRADICTED if paired with `I-D`) | PARTIALLY CLOSED (NB-5) |

**RES-1 × axis A**

| `A-0` | `A1` | `A2` | `A3` | `A4` |
|---|---|---|---|---|
| UNRESOLVED | PARTIALLY CLOSED — 5 legs persist as accepted behavior; CX-1 must be amended | PARTIALLY CLOSED — U4, U5 persist | **CLOSED** | CONTRADICTED (CX-6; NB-4) |

**RES-2 × axis D**

| `D-0` | `D1` | `D2` | `D3` |
|---|---|---|---|
| UNRESOLVED | **CLOSED** (ratified; `:519` amended). Residual harm eliminated only under `A3` | **CLOSED** | **CLOSED** (NB-1) |

### D.2 Explicit model columns — a spanning set

Twelve canonical models, chosen so that every value of every axis appears at least once, and so that every matrix value (CLOSED / PARTIALLY CLOSED / UNRESOLVED / CONTRADICTED) appears. Names are descriptive labels, not endorsements.

| Model | I | A | B | D | Aud |
|---|---|---|---|---|---|
| **G-1** ratify-all | I-R | A1 | B1 | D1 | Aud2 |
| **G-2** ratify-all + retire | I-R | A1 | B1 | D1 | Aud3 |
| **G-3** named-binding | I-R | A2 | B1 | D1 | Aud2 |
| **G-4** document-binding, reusable | I-R | A3 | B1 | D1 | Aud2 |
| **G-5** document-binding, consumed | I-R | A3 | B2 | D2 | Aud1 |
| **G-6** document-binding, consumed, retire | I-R | A3 | B2 | D2 | Aud3 |
| **G-7** register-as-audit | I-R | A3 | B2 | D2 | Aud4 |
| **G-8** prohibitionist | I-R | A3 | B2 | D3 | Aud1 |
| **G-9** runtime-scoped | I-R | A3 | B2c | D2 | Aud5 |
| **G-10** rule-derived admission | I-D | A3 | B2 | D2 | Aud1 |
| **G-11** issuance only, nothing else decided | I-R | A1 | B1 | D1 | Aud-0 |
| **G-12** bytes-binding | I-R | A4 | B2 | D2 | Aud1 |

| Blocker | G-1 | G-2 | G-3 | G-4 | G-5 | G-6 | G-7 | G-8 | G-9 | G-10 | G-11 | G-12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **E-4A** | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED |
| **E1-F3** | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED | **PARTIAL** | CLOSED | CLOSED | CLOSED |
| **E-3** | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED | **PARTIAL** | CLOSED | **UNRESOLVED** | CLOSED |
| **RES-1** | **PARTIAL** | **PARTIAL** | **PARTIAL** | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED | **PARTIAL** | **CONTRADICTED** |
| **RES-2** | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED | CLOSED |
| **full closure?** | no | no | no | **yes** | **yes** | **yes** | **yes** | **yes** | no | **yes** | no | no |
| **new blockers** | — | — | — | — | — | — | **NB-3** | **NB-1** | **NB-5** | **NB-6** | — | **NB-4** |
| **UNRESOLVED count** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **1** | 0 |
| **PARTIAL count** | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | **2** | 0 | 1 | 0 |
| **CONTRADICTED count** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **1** |

`G-7` is CONTRADICTED only when `Aud4` is paired with `I-D` (CX-4); with `I-R` as shown it is consistent and carries NB-3.

### D.3 Exact closure counts over the full space

```
CONSISTENT GOVERNANCE-COMPLETE MODELS ......................... 243

FULL-CLOSURE MODELS  (all five rows CLOSED)
    I ∈ {I-R, I-D}          2
    A  = A3                 1     ← the only value that closes RES-1
    B ∈ {B1, B2}            2
    D ∈ {D1, D2, D3}        3
    Aud ∈ {Aud1,2,3,4}      4
                        ───────
    raw                      48
    minus CX-4 contradictory (I-D × Aud4): 1×1×2×3×1 = 6
    FULL-CLOSURE CONSISTENT MODELS ............................  42

FULL CLOSURE WITH ZERO NEW BLOCKERS
    exclude D3 (NB-1) → D ∈ {D1, D2}          2
    exclude Aud4 (NB-3) → Aud ∈ {Aud1,2,3}    3
    exclude I-D (NB-6) → I = I-R              1
    modifier R = R1 (R2 → NB-2)
    A = A3 (1) · B ∈ {B1, B2} (2)
    ZERO-NEW-BLOCKER FULL-CLOSURE MODELS ......................  12
        = I-R × A3 × {B1,B2} × {D1,D2} × {Aud1,Aud2,Aud3}

MODELS LEAVING ≥1 BLOCKER UNRESOLVED OR PARTIAL ............... 201  (243 − 42)
MODELS CONTAINING A CONTRADICTED CELL ......................... every A4-bearing model
                                                                (90 of the 360-model space
                                                                 that includes A4)
```

Two counts are reported for zero-new-blocker closure because `I-D`'s NB-6 is a **dead-interface** blocker rather than an unauthorized-write blocker: **12** excluding `I-D`, **24** if `I-D`'s NB-6 is judged not to be a blocker. That judgment is itself a governance question and is therefore not made here; both numbers are given.

---

## E. Minimal-decision analysis

### E.1 Minimum number of governance decisions required

```
DECISIONS FOR A COMPLETE GOVERNANCE SPECIFICATION ............. 13
    (identical to PHASE2-GOVERNANCE-DEPENDENCY-MAP.md §11's D-1…D-13,
     re-derived here from the axes)

DECISIONS THAT DETERMINE ANY CLOSURE VALUE ....................  5
    axis I    (issuance path)                → E-4A
    axis A    (authorization binding)        → RES-1
    axis B    (replay semantics)             → E1-F3
    axis D    (empty-manifest semantics)     → RES-2
    axis Aud  (mutation + audit semantics)   → E-3

MINIMUM DECISIONS TO ACHIEVE FULL CLOSURE .....................  5
MINIMUM DECISIONS TO ACHIEVE FULL CLOSURE WITH NO NEW BLOCKER .  5
    (the same five; the difference is which values are taken, not how many
     decisions are needed)

DECISIONS WITH NO EFFECT ON ANY CLOSURE VALUE .................  8
    FD-1 issuer identity            — provably collapsed (M1)
    FD-4 ledger authority ownership — provably collapsed (M2)
    R    register trust             — modifier; R2 adds NB-2
    T    expiry instant             — modifier; C-14 no producer
    use-record location (B2a/B2b)   — sub-variant of B
    Aud1 pair selection (6 variants)— sub-variant of Aud
    I-R issuance mechanism (3 variants) — sub-variant of I (M5)
    bounded-reuse threshold n       — parameter of B2 (M4-adjacent)
```

### E.2 Are any decisions logically forced?

**One, and only conditionally.**

| Decision | Forced? | Proof |
|---|---|---|
| **A = A3** | **FORCED, conditional on full closure being required.** | `A3` is the unique value of axis A whose RES-1 cell is CLOSED. `A1` and `A2` are PARTIALLY CLOSED by measurement (P2-2/3/4/7/8 legs persist); `A4` is CONTRADICTED (CX-6); `A-0` is UNRESOLVED. Therefore *full closure ⇒ A = A3*. Unconditionally, A is free. |
| I, B, D, Aud | **NOT FORCED.** | Each has ≥2 values whose cell is CLOSED: `I ∈ {I-R, I-D}`, `B ∈ {B1, B2}`, `D ∈ {D1, D2, D3}`, `Aud ∈ {Aud1, Aud2, Aud3, Aud4}`. |
| **D3 ⇒ a further decision** | **FORCED consequence, not a forced choice.** | `D3` creates NB-1, so a model taking `D3` must additionally decide what becomes of the reachable non-allocating write class. Measured: `R-9` refuses it under the sentinel (`:696-707`), the class is reachable on the live ledger (**P2-5**). |
| **Aud1 after I** | **FORCED ordering, not a forced value.** | A tracked audit artifact re-enters CY-1, terminable only once an issuance path exists (`:499-506`). |
| **A before I** | **FORCED ordering.** | `A3` changes every `manifest_digest` (`:548-568`) and changes what `plan()` emits (`:648-661`); taking it after permits are issued invalidates live authorizations. Harmless only while zero permits exist — which is the case today (**P2-5**). |

### E.3 Are any decisions independent?

| Pair | Independent? | Basis |
|---|---|---|
| **Aud ⊥ {I, A, B, D}** | **YES — measured.** | E-3 fails today with **zero** permits in existence: `UGA-INV-01` 27 / `UGA-INV-10` 27, identical sets (**P2-10**). No permit answer can move E-3's cell. Sole exception: `Aud4` couples to `I` through CX-4. |
| **A ⊥ B** | **YES.** | The binding's content and whether use is recorded read disjoint state: `manifest_digest` (`:548-568`) versus a use record. The A3×B1 idempotence interaction changes residual harm, not either cell. |
| **A ⊥ I** | **YES for closure, NO for ordering.** | Both cells are independent; the ordering edge (C-7 digest churn) is real. |
| **B ⊥ D** | **YES.** | Consumption and empty-manifest issuability read disjoint state. |
| **A ↔ D** | **COUPLED in residual harm only.** | Under `A3`, `D1`'s residual harm vanishes because the permit names one document. Both cells remain CLOSED either way. |
| **I ↔ Aud4** | **COUPLED — contradictory.** | CX-4: `Aud4` needs permit records; `I-D` abolishes them. |
| **FD-1, FD-4 ⊥ everything** | **YES — provably vacuous.** | M1 (P2-6: no issuer field read), M2 (`:728-732`: unconstrained string equality). |

### E.4 Are any decisions redundant?

**Yes — six redundancies, each proved.**

| # | Redundant decision | Proof of redundancy |
|---|---|---|
| 1 | **FD-1 — who may issue** | The verifier reads no `issuer`, `signature` or `issued_at` (**P2-6**). Any two registers identical in the nine read fields verify identically. FD-1 must be answered for the specification to be complete; it changes no cell and no line of code. |
| 2 | **FD-4 — which authority owns the ledger** | `:728-732` is string equality with no allow-list. Any authority name behaves identically. |
| 3 | **FD-3′ = "expires on use"** | Identical mechanism to `B2` (M4). |
| 4 | **FD-3′ = "state-bound expiry"** | Already implemented by `preimage_digest` (`:742-749`); identical to "never expires" (M3). |
| 5 | **Issuance mechanism among tool / convention / CI** | Identical registers, and M1 shows origin is unreadable (M5). |
| 6 | **Bounded reuse (`n` uses) vs single use** | One mechanism, one constant (M4-adjacent). |

**Consequence for the decision count.** A governance specification must answer 13 questions to be *complete*; **5** of those answers determine the closure outcome; **8** are redundant with respect to closure, of which **2 (FD-1, FD-4) are redundant with respect to the implementation entirely**.


---

## F. Post-governance implementation requirement

Stated per axis value, because models are products of axis values and the requirements compose additively (no two axis values touch the same function except `A` and `D`, both of which touch `_verify_permit`/`manifest_digest` — noted where they do). **These are consequences, not instructions; nothing here is implemented.**

### F.1 Axis I — issuance

| | `I-0` | `I-R` | `I-D` |
|---|---|---|---|
| **Implementation changes** | none | a producer for `00-BOOK/DATA/allocation-permits.json` emitting the nine fields `_verify_permit` reads. **No change to `_verify_permit`** — the register's shape is already fixed by its consumption set | `_verify_permit :714-721` — the mandatory register match is replaced by an admission predicate; `permit_id` resolution, ambiguity refusal (`:718-722`) and `load_permit_register` become dead or repurposed |
| **Tests required** | none | issuance→verification round trip; refusal on each of the nine bindings; `register.sh` Phase 1 end-to-end (**UK-1**, unverifiable without a mutating run) | admission-predicate tests; removal or rewrite of the register-shape tests at `platform/tests/test_ledger_authority.py:61-87`, `:474`, `:503-505`, `:524` |
| **Invariants affected** | none | `UGA-INV-01` clears 27 anonymous objects once a mint completes → `cmd_gate` can go green (CY-3) | same, plus `LEDGER-INV-01`'s scope statement is unaffected (it measures write paths, not authorization) |
| **Backward compatibility** | n/a | additive — a new file. `permit=NO_ALLOCATION` on a byte-identical no-op keeps working (Phase 1 §6.3) | **breaking** for the three `--permit` CLI flags and their help text (`ukb.py:2497`, `:2555`, `uga_engine.py:2079`) |
| **Permit invalidation** | none | none — zero permits exist (**P2-5**) | n/a — permits cease to be records |

### F.2 Axis A — binding

| | `A1` | `A2` | `A3` | `A4` |
|---|---|---|---|---|
| **Implementation changes** | **none in code**; amend the claims at `:490-497` and `:763-766` | `allocation_report :386-434` emits key→identifier pairs and new-record bodies; `manifest_digest :548-568` gains those inputs; `plan()` output grows | `manifest_digest` gains a document digest; `plan()` emits it | a canonical serializer must be mandated first (CX-6) |
| **Tests required** | tests pinning the ratified equivalence class (the inverse of probes P2-2/3/4/7/8) | per-leg refusals for U1–U3; regression that U4/U5 remain accepted | per-leg refusals for U1–U5; the reviewability accompaniment if reviewability is required | serializer-equality tests replacing Phase 1's `R-11` round-trip test, which currently **asserts** the `_canonical` byte inequality |
| **Invariants affected** | none | none | none | none directly; `commit()`'s post-write comparison at `:920-927` changes from document to byte equality |
| **Backward compatibility** | full | `plan()` output shape changes → the three `format_report`/plan render sites (`ukb.py:1293`, `uga_engine.py:1982`, and `_verify_permit`'s refusal message) must tolerate it, exactly the surface Phase 1 §R-8 found wider than expected | same | **breaks** correct writes unless the serializer decision lands first (measured: 1 786 167 vs 2 274 511 bytes) |
| **Permit invalidation** | none | **every digest changes** → all permits invalidated | **every digest changes** → all permits invalidated | every digest changes |

`A2` and `A3` inherit Phase 1 §4.2's outbound constraint verbatim: the change is free **only while zero permits exist**, which is the present state (**P2-5**).

### F.3 Axis B — replay

| | `B1` | `B2` (durable) | `B2c` (runtime) |
|---|---|---|---|
| **Implementation changes** | amend `:570-577`; no code | `commit :841-933` records use under the existing lock; `B2a` makes `load_permit_register :608-631` read-write, `B2b` adds a tracked artifact (CY-1) | `commit` appends to `.runtime/governance` via `append_audit :133-160` |
| **Tests required** | a test pinning that replay after restore is permitted by design (the inverse of **P2-1**) | replay-after-restore refusal; a first-use/second-use pair; lock interaction (`_ledger_lock :216-268`) | as `B2`, plus a fresh-runtime test showing the record is absent |
| **Invariants affected** | none | none; `B2b` adds one discovered object that must be minted | none tracked |
| **Backward compatibility** | full | `B2a` changes a documented design property (`:490-497`), the same species of change Phase 1 §1.5 recorded for *"It does not write bytes either."* | full |
| **Permit invalidation** | none | none | none |

### F.4 Axis D — empty manifest

| | `D1` | `D2` | `D3` |
|---|---|---|---|
| **Implementation changes** | amend `:519`; no code | a distinct authorization mechanism for the non-allocating class — either a new `_verify_permit` branch or a widened sentinel, the latter partially reversing `R-9` | refuse empty-manifest permits at `:714-804`; **and** dispose of the reachable class (NB-1) |
| **Tests required** | a test pinning empty-manifest issuability, and pinning that `scope` is vacuous on it (`:767-783`) | authorization tests for `history`-only appends and `version`/`discovered_volumes` changes | the refusal test; plus tests proving the class cannot arise, which is the NB-1 problem |
| **Invariants affected** | none | none | none |
| **Backward compatibility** | full | must preserve Phase 1's revived idempotent branch (`ukb.py:2380-2384`), which `R-5a` brought back from dead code | **breaks** `ukb.record_snapshots`' ability to persist a snapshot append unaccompanied by an allocation (`ukb.py:314-330`) |
| **Permit invalidation** | none | none | none |

### F.5 Axis Aud — mutation and audit

| | `Aud1` | `Aud2` | `Aud3` | `Aud4` | `Aud5` |
|---|---|---|---|---|---|
| **Implementation changes** | an event emitter at the write act (`commit`, or the callers), a persisted tracked log honouring the `-audit.json` ban (`governance_telemetry.py:187-207`) and the no-wall-clock contract; `uga_engine.py:1331-1335` re-pointed at it | `uga_engine.py:1334` name; `uga-declaration.json`; optionally split into two invariants | remove the invariant from `epoch5_invariants` and the declaration | `commit` emits nothing new; `uga_engine.py:1331-1335` reads the register | as `Aud1`, persisting to `.runtime/governance` |
| **Tests required** | emitter coverage per mutation element; independence test (the inverse of `audited ≡ set(by_object.keys())`); determinism/drift test | a test pinning the corrected name to the measured set; a duplication test versus `UGA-INV-01` | a test asserting the invariant is absent, so it cannot silently return | register-completeness test; and an `NO_ALLOCATION` gap test, which is NB-3 | as `Aud1` minus the tracked-drift test |
| **Invariants affected** | `UGA-INV-10` redefined; count stays 30 unless split | `UGA-INV-10` renamed | 30 → 29 declared surface changes; `cmd_gate :2125-2161` unaffected structurally | `UGA-INV-10` redefined | `UGA-INV-10` redefined, clone-dependent (CX-5) |
| **Backward compatibility** | **58 files reference `UGA-INV-10`** (59 including `PHASE2-GOVERNANCE-DEPENDENCY-MAP.md`); ≥6 historical determinations cite INV-01/INV-10 as independent signals, which E-3 established is one finding double-counted | same blast radius | same blast radius, plus every citation becomes a reference to a retired invariant | same blast radius | same blast radius |
| **Permit invalidation** | none | none | none | none | none |

### F.6 What no model can avoid

| Requirement | Every model? | Basis |
|---|---|---|
| A producer for the register, or the abolition of registers | yes, for E-4A closure | `:841` mandatory `permit`; `:714-721` |
| At least one source-claim amendment | **yes** | Every axis value with a CLOSED cell either changes code or amends a claim; CX-1/CX-2/CX-3 are internal contradictions that no model can leave in place while claiming closure |
| Re-running the invariant surface | yes | `cmd_gate` blocks on every failing invariant (`:2128-2136`); 27 anonymous objects clear only after a mint |
| Post-decision verification that cannot be done today | **yes** | **UK-1** — whether `register.sh` Phase 1 and its nine dependent phases complete once a permit verifies requires an irreversible mutating run. Phase 0 declined for the same reason (`PHASE0-E4A-ISSUANCE-PATH-REPORT.md` §7) |

---

## G. Closure determination

### 1. Is there at least one governance model that closes all remaining blockers?

**YES.**

Existence is established constructively by the factorization theorem (§D.0) plus the five sub-matrices (§D.1): any model with `A = A3`, `B ∈ {B1, B2}`, `D ∈ {D1, D2, D3}`, `Aud ∈ {Aud1, Aud2, Aud3, Aud4}`, `I ∈ {I-R, I-D}`, excluding the CX-4 pairing, has all five rows CLOSED. `G-4`, `G-5`, `G-6`, `G-7`, `G-8` and `G-10` in §D.2 are explicit witnesses.

### 2. How many?

```
CONSISTENT GOVERNANCE-COMPLETE MODELS ......................... 243
FULL-CLOSURE MODELS ...........................................  42
FULL-CLOSURE MODELS INTRODUCING NO NEW BLOCKER ................  12
    (24 if I-D's NB-6 — a dead-interface blocker — is judged not to be a blocker;
     that judgment is itself a governance question and is not made here)
```

### 3. Do any produce new blockers?

**YES — 30 of the 42 full-closure models produce at least one new blocker**, from six distinct new blockers:

| New blocker | Produced by | Full-closure models affected |
|---|---|---|
| **NB-1** reachable write class with no authorization path | `D3` | 14 of 42 |
| **NB-2** no trust anchor for register authenticity | modifier `R2` | any model taking `R2` |
| **NB-3** unauditable `NO_ALLOCATION` act class | `Aud4` | 6 of 42 |
| **NB-4** bytes binding unsatisfiable without a serializer decision | `A4` | 0 of 42 — `A4` never achieves full closure (CONTRADICTED) |
| **NB-5** clone-dependent authorization / measurement | `B2c`, `Aud5` | 0 of 42 — both are PARTIAL, so they never achieve full closure |
| **NB-6** dead authorization interface | `I-D` | 18 of 42 |

### 4. Is governance sufficient for unconditional implementation readiness?

**NO.**

Four independent reasons, each measured or derived from source:

1. **Every full-closure model requires post-decision code.** `A = A3` is forced for full closure (§E.2) and is the one axis value that **cannot** be satisfied by ratification: it changes `manifest_digest`'s input set (`:548-568`) and `plan()`'s emitted output (`:648-661`). There is no full-closure model with zero implementation.
2. **E-4A's closure requires a producer that does not exist.** Every `I` value that closes it either adds a register producer or rewrites `_verify_permit :714-721`. Governance can specify it; only implementation can supply it.
3. **One precondition is unverifiable without an irreversible act.** **UK-1** — whether `register.sh` Phase 1 completes end-to-end, and whether the nine `|| fail`-gated phases then pass, cannot be established without executing a mutating registration run. What is established is the refusal at the call site (`register.sh:216` passes no `--permit`) and the gating structure (`register.sh:206-259`).
4. **Three documented bounds survive every model**, because none of them is a governance question: they were classified as bounds by `PHASE05:§F.4` and carried forward by Phase 1.

Therefore governance completion yields **decision-completeness, not implementation-readiness**. The precise status after a full-closure, zero-new-blocker model is: *0 of the 5 residual blockers remain; a bounded implementation backlog and 4 non-blocker residuals remain.*

### 5. Every remaining blocker after governance resolution

**Case A — a full-closure, zero-new-blocker model (12 of 243):**

```
RESIDUAL BLOCKERS FROM THE PHASE-1 SET ......................... 0   of 5
NEW BLOCKERS ................................................... 0
NON-BLOCKER RESIDUALS .......................................... 4
    RES-3   MW-3 remains a window — the caller's ledger read precedes commit(),
            hence precedes the lock; bounded by two independent refusals after R-6,
            not closed.                        [PHASE05 §F.4; Phase 1 §R-6]
    RES-4   flock is advisory and filesystem-dependent; where it is not honoured,
            R-2 is the sole detector.          [PHASE05 §F.4; Phase 1 §R-3]
    R-7w    R-7's detection is post-hoc: divergent bytes reach disk before the
            comparison at :920-927, and a crash between writer (:895) and
            _restore (:807-822) leaves them there — two file operations under a
            held lock.                          [Phase 1 §R-7]
    UK-1    register.sh end-to-end completion unverified; unverifiable without an
            irreversible mutating run.          [PHASE0-E4A §7]
IMPLEMENTATION BACKLOG (not blockers; enumerated per axis in §F) ... 3 axis values
            requiring code: A3, I (producer), and B2 where the model takes it
```

**Case B — full-closure models carrying a new blocker (30 of 42):** as Case A, plus the applicable member of {NB-1, NB-2, NB-3, NB-6}.

**Case C — the 201 consistent models that are not full-closure:** the UNRESOLVED and PARTIALLY CLOSED cells are given exactly by the five sub-matrices in §D.1. Specifically: `I-0` leaves E-4A unresolved (**1 blocker**); `A-0` leaves RES-1 unresolved and `A1`/`A2` leave it partial (**up to 1**); `B-0` leaves E1-F3 unresolved, `B2c` partial (**up to 1**); `D-0` leaves RES-2 unresolved (**up to 1**); `Aud-0` leaves E-3 unresolved, `Aud5` partial (**up to 1**). Maximum residual for a model that declines every axis: **5 unresolved**, which is the present state.

---

## H. Success criteria and evidence provenance

| Success criterion | Discharge |
|---|---|
| No recommendations | None present. Every axis value is stated with its closure profile and its new-blocker profile; no ordering by desirability appears. |
| No governance chosen | No axis is assigned. FD-1…FD-5 are quantified over throughout. |
| No code changes | No repository file modified; this document is the only file written. |
| **Exact count of governance decisions** | **13** total for a complete specification; **5** determine closure; **8** are closure-redundant, of which **2** are implementation-vacuous. |
| **Exact count of governance-complete models** | **270** governance-complete; **243** consistent after removing the 27 CX-4-contradictory pairings. |
| **Exact count of models achieving full closure** | **42**. Of these, **12** introduce no new blocker (**24** if NB-6 is not counted as a blocker). |
| **Exact count of blockers remaining after each model** | §D.2 per-column counts; §D.1 sub-matrices for all 1 152 models; §G.5 Cases A/B/C. |
| **Explicit YES/NO on governance sufficiency** | **NO** — §G.4, with four independent reasons. |

### H.1 Provenance of every load-bearing claim

| Claim | Backed by |
|---|---|
| FD ranges | `PHASE05:224-226`, `:247`; `PHASE0-E1:17`, `:375` |
| E-4A open, all three permit values refused on a real live manifest | probe **P2-5** (established, read-only) |
| E1-F3 open post-Phase-1; restore-via-chokepoint refused | probe **P2-1** |
| E-3 open, identical violation sets, `audited ≡ by_object` | probe **P2-10** |
| RES-1's five free dimensions | probes **P2-2, P2-3, P2-4, P2-7, P2-8**; exhaustiveness derived from `:548-568` being a six-input pure function (**P2-9**) |
| RES-2's universal empty-manifest digest | probes **P2-4** (fixture, end-to-end) and **P2-5** (live, read-only) |
| FD-1 collapse | probe **P2-6** — no `issuer`/`signature`/`issued_at`/`single_use`/`revoked`/`uses` read |
| FD-4 collapse | `:728-732` — unconstrained string equality, no allow-list |
| Serializer inequality forcing document comparison | Phase 1 §R-11 (1 786 167 vs 2 274 511 bytes); `:920-927` |
| Zero permits exist, so digest churn is free today | probe **P2-5**; Phase 1 §4.2 |
| 58/59 files reference `UGA-INV-10` | probe **P2-12** |
| `-audit.json` ban, `.runtime/` untracked, no-wall-clock contract | `governance_telemetry.py:187-207`, `:79`; `.gitignore:12`; `uga_engine.py:1911-1915` |
| Identity regress terminated at one file | `:499-506` |
| `cmd_gate` blocks on every invariant | `uga_engine.py:2128-2136` |
| Declared subject-level mutation classes already exist | `00-BOOK/DATA/mutation-governance-boundary.json` |

No claim in this document rests on a probe that was not already executed and recorded. No new probe was run against the repository for this determination.

---

## I. Stop condition

- Governance models enumerated: **270 complete / 243 consistent**, over **5** closure axes and **2** modifiers, after **5** proved equivalence merges without which the space is unbounded.
- Full closure: **exists**, **42** models, **12** of them free of new blockers.
- New blockers recorded: **6** (NB-1 … NB-6). Contradictions recorded: **6** (CX-1 … CX-6). Cycles recorded: **3** (CY-1 … CY-3).
- Governance sufficiency for unconditional implementation readiness: **NO**.
- Governance chosen: **none**. Decisions taken: **0**. Answers recommended: **0**.
- FD-1, FD-2, FD-3′, FD-4, FD-5: **treated as UNKNOWN throughout; not answered, not assumed, not preferred.**
- Repository files modified: **none**. Live ledger: byte-identical, `sha256 8471e709…c20b`.

The next act is a governance decision on the five closure axes. Nothing here prejudges which value any axis takes.
