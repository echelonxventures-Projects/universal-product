# PHASE 3 — IMPLEMENTATION READINESS DETERMINATION

| Field | Value |
|---|---|
| Question | After governance selection, what exact implementation work is required, and does any path exist to **UNCONDITIONAL READY FOR IMPLEMENTATION** without introducing a new blocker? |
| Answer | **NO.** Unconditional readiness is unreachable. The maximal reachable state is **READY, CONDITIONAL ON GOVERNANCE SELECTION**, attainable under all 12 admissible models, at a cost of **17–20 implementation tasks** (24 distinct across the set), **0 migration tasks**, leaving **0 blockers**, **3 residuals** and **2 unknowns**. |
| Inputs | `PHASE0-GOVERNANCE-INDEPENDENT-DETERMINATION.md`, `PHASE05-GOVERNANCE-INDEPENDENT-REMEDIATION.md`, `PHASE1-GOVERNANCE-INDEPENDENT-IMPLEMENTATION-REPORT.md`, `PHASE2-GOVERNANCE-CLOSURE-DETERMINATION.md` |
| Code changed | **NONE.** No repository file was modified. This document is the only file written. |
| Governance selected | **NONE.** No axis assigned, no model recommended, ranked or preferred. FD-1…FD-5 treated as UNKNOWN throughout. |
| Live ledger | unchanged — `sha256 8471e709b178a9a09909bca55f2e8eccb78161db8423026d1d26e4f35c41c20b`, `git status --porcelain 00-BOOK/DATA/` empty before and after |
| Baseline | working tree at `77798202`; `00-BOOK/tools/ledger_authority.py` 933 lines, `AM` (never committed); `platform/tests/test_ledger_authority.py` **77 passed** (re-run this phase) |

### Compliance with the stated rules

| Rule | Compliance |
|---|---|
| 1. No code changes | No source file modified. Every probe in §H is read-only or operates on in-memory copies. Verified: ledger sha256 identical before and after; `git status --porcelain 00-BOOK/DATA/` empty. |
| 2. No repository mutations | This document is the only addition attributable to this phase. |
| 3. No governance selection | No axis is assigned. §B and §C quantify over all 12 admissible models; §D reports what is invariant across them. |
| 4. All 12 zero-new-blocker models admissible | §A enumerates them exactly, from `PHASE2:§D.3`'s product form, and every subsequent section is evaluated over all 12. |
| 5. Every claim backed by source references or executable evidence | §H maps each load-bearing claim to a `file:line` verified this phase, or to a probe **P3-1 … P3-8** executed this phase. Where a claim is a derivation it is labelled DERIVED. |
| 6. Distinguish blocker / residual / unknown / implementation task | Four-way classification defined in §E.0 and applied in §E.1–§E.4. One reclassification against `PHASE2:§G.5` is flagged explicitly in §E.5. |
| 7. No governance model recommended | None. §F answers the five questions as counts and YES/NO. Every ordering that appears is a dependency ordering derived from source. |

---

## 0. What the inputs establish, and the state this phase measured

Three facts fix the frame, all re-verified by execution this phase rather than carried forward on trust.

**Fact 1 — governance writes no code, so governance closure does not move the artifact.** `PHASE2:§G.5` reports that after a full-closure zero-new-blocker model, *"0 of the 5 residual blockers remain."* That is a statement about **decision closure**, not about the repository. Measured today (probe **P3-1**), against a real allocating manifest derived from the live ledger:

```
register exists: False
REAL ALLOCATING MANIFEST: allocating=True total=1
  permit=None             -> REFUSED [PermitRefused] permit must be a permit_id string or NO_ALLOCATION; got None
  permit='P-ANY'          -> REFUSED [PermitRefused] permit 'P-ANY' is not in .../00-BOOK/DATA/allocation-permits.json
  permit=NO_ALLOCATION    -> REFUSED [PermitRefused] NO_ALLOCATION was asserted, but this write ALLOCATES: ...
```

All three admissible `permit` values are still refused. E-4A is a **total block on every identity-ledger write today**, and it remains one for as long as no code lands, whatever governance decides. This distinction is load-bearing for §G's two blocker counts and is stated once here rather than repeated.

**Fact 2 — the Phase-1 baseline is intact and green.** `platform/tests/test_ledger_authority.py` → **77 passed** (probe **P3-8**), matching `PHASE1:§4`'s terminal row exactly. The twelve governance-independent closures are in the tree and hold.

**Fact 3 — the governance-dependent five are all still open**, each re-verified by execution or by source read this phase:

| Blocker | Re-verification this phase | Method |
|---|---|---|
| **E-4A** | register absent; all three permit values refused on a real allocating manifest | **P3-1**, executed |
| **E1-F3** | `single_use` occurs **0** times in `ledger_authority.py`; no consumption record exists; `preimage_digest :570-577` unmodified and still derives spent-ness from mutable state | **P3-2**, executed |
| **E-3** | `audited == set(by_object.keys())` → **True (5374 ≡ 5374)**; `UGA-INV-01` and `UGA-INV-10` both FAIL at **violations=27** with identical violation sets | **P3-5**, **P3-6**, executed |
| **RES-1** | two materially different `history` appends produce the **same** `manifest_digest` `a7371a31a586a56c…` | **P3-3**, executed live read-only |
| **RES-2** | that digest is **also** the byte-identical no-op digest — one universal value per `(actor, pre-image)`; `_verify_permit`'s permit path reads neither `manifest["allocating"]` nor `manifest["total_allocations"]` | **P3-3**, **P3-4** |

---

## A. Closure-model inventory

`PHASE2:§D.3` gives the zero-new-blocker set in product form:

> `ZERO-NEW-BLOCKER FULL-CLOSURE MODELS ...... 12 = I-R × A3 × {B1,B2} × {D1,D2} × {Aud1,Aud2,Aud3}`
> — with modifier `R = R1` (since `R2` creates NB-2), and modifier `T` free (no closure effect).

Expanded. Labels `Z-01…Z-12` are identifiers for this document only; they are not rankings and the order carries no preference.

| Model | I | A | B | D | Aud | Equivalent to a `PHASE2:§D.2` column? |
|---|---|---|---|---|---|---|
| **Z-01** | I-R | A3 | B1 | D1 | Aud1 | — |
| **Z-02** | I-R | A3 | B1 | D1 | Aud2 | **= G-4** (document-binding, reusable) |
| **Z-03** | I-R | A3 | B1 | D1 | Aud3 | — |
| **Z-04** | I-R | A3 | B1 | D2 | Aud1 | — |
| **Z-05** | I-R | A3 | B1 | D2 | Aud2 | — |
| **Z-06** | I-R | A3 | B1 | D2 | Aud3 | — |
| **Z-07** | I-R | A3 | B2 | D1 | Aud1 | — |
| **Z-08** | I-R | A3 | B2 | D1 | Aud2 | — |
| **Z-09** | I-R | A3 | B2 | D1 | Aud3 | — |
| **Z-10** | I-R | A3 | B2 | D2 | Aud1 | **= G-5** (document-binding, consumed) |
| **Z-11** | I-R | A3 | B2 | D2 | Aud2 | — |
| **Z-12** | I-R | A3 | B2 | D2 | Aud3 | **= G-6** (document-binding, consumed, retire) |

Arithmetic check: `1 × 1 × 2 × 2 × 3 = 12`. ✓

**Axis values fixed across all 12 — and why.** These are not choices this phase makes; they are the consequence of the zero-new-blocker constraint applied to `PHASE2:§D.1`'s sub-matrices.

| Axis | Fixed value | Every alternative, and why it is excluded |
|---|---|---|
| **I** | `I-R` | `I-0` → E-4A UNRESOLVED. `I-D` → **NB-6** (dead authorization interface). Verified: the three `--permit` flags exist at `ukb.py:2497`, `ukb.py:2555`, `uga_engine.py:2177`, and `load_permit_register :608-631` is the single register access — all lose their referents under `I-D`. |
| **A** | `A3` | `A-0` → UNRESOLVED. `A1`, `A2` → PARTIALLY CLOSED. `A4` → CONTRADICTED (CX-6) + **NB-4**. `A3` is therefore the **unique** value of axis A admitting full closure — `PHASE2:§E.2`'s one conditionally-forced decision. |
| **B** | `B1` or `B2` | `B-0` → UNRESOLVED. `B2c` → PARTIAL + **NB-5** (clone-dependent, CX-5). |
| **D** | `D1` or `D2` | `D-0` → UNRESOLVED. `D3` → CLOSED but **NB-1** (a write class reachable on the production ledger with no authorization path). |
| **Aud** | `Aud1`, `Aud2` or `Aud3` | `Aud-0` → UNRESOLVED. `Aud4` → **NB-3** (unauditable `NO_ALLOCATION` act class). `Aud5` → PARTIAL + **NB-5**. |
| **R** (modifier) | `R1` | `R2` → **NB-2** (no trust anchor exists). |
| **T** (modifier) | free | Neither `T-state` nor `T-instant` opens or closes any blocker. `T-instant` needs a clock authority; `expires_at` is **read** at `:785-797` and has no producer anywhere — verified. |

**The 12-versus-24 question is left where Phase 2 left it.** `PHASE2:§D.3` reports 24 *"if `I-D`'s NB-6 is judged not to be a blocker"* and declines that judgment because it is itself a governance question. This phase inherits the decline. The task's Rule 4 names 12 as admissible, and 12 is used throughout. **Consequence recorded for completeness, not acted on:** were the 24-model reading taken, the forced set in §D would **shrink by one** (`F-4` register.sh plumbing survives, but `F-1`'s register producer is replaced by an admission-predicate rewrite of `:714-721`) and gain **NB-6**. It is therefore not a superset relation, and the 12-model results below do not transfer to the 24-model reading unchanged.

---

## B. Required implementation inventory

Derived per axis value from `PHASE2:§F`, then re-grounded on source verified this phase, because `PHASE2:§F` states requirements at axis granularity while this section needs them at task granularity. Every line number below was re-read this phase against the 933-line `ledger_authority.py` and the 2191-line `uga_engine.py`.

### B.0 One axis-level correction, stated before the inventory

`PHASE2:§A.2` and `§C.9` cite the third `--permit` flag at `uga_engine.py:2079`. Verified this phase: **line 2079 is the `LA.plan` call inside `cmd_run`**; the flag is at **`uga_engine.py:2177`**. `cmd_gate` at `:2125` matches Phase 2 exactly, so the drift is confined to that one citation. The artifact Phase 2 relies on — three inert `--permit` flags whose help text names a file the repository never produces — is confirmed present. **Substance unaffected; citation corrected.**

### B.1 Axis I — issuance (`I-R`, all 12 models)

| Dimension | Requirement |
|---|---|
| **Code** | A producer for `00-BOOK/DATA/allocation-permits.json`. Its output shape is **already fully determined** by the consumption set, so this is a construction task with no design freedom: `_verify_permit :714-804` performs exactly **9** permit reads — `permit_id :715`, `actor :728`, `manifest_digest :735`, `preimage_digest :743`, `head :751`, `scope :767`, `scope.maps :769`, `scope.max_allocations :778`, `expires_at :785` (probe **P3-7**). `load_permit_register :608-631` accepts either a bare list or `{"permits": [...]}`. **No change to `_verify_permit` is required or permitted by `I-R`.** |
| | Second code item, **derived this phase**: `register.sh:216` is `"$PY" "$HERE/ukb.py" build --mint \|\| fail "ukb build failed" 1` — no `--permit`. Three of the four `LA.commit` call sites pass `permit=getattr(args, "permit", None)` (`ukb.py:1299`, `ukb.py:2401`, `uga_engine.py:2097`), which is `None` when the flag is unset, and `None` is refused at the permit-type check. A register producer alone therefore does **not** make `register.sh` Phase 1 complete; the permit must also reach the call site. |
| **Invariants** | None changed directly. **DERIVED consequence** (`PHASE2:§F.1`, CY-3): `UGA-INV-01`'s 27 violations clear only after a mint completes, at which point `cmd_gate` can go green. Measured today: `UGA-INV-01 FAIL violations=27 measured=6804`, 2 of 30 invariants FAIL. Not measurable before implementation. |
| **Tests** | Issuance → verification round trip. One refusal test per binding across the 9 read fields. `register.sh` Phase 1 end-to-end — **not achievable without a mutating run (UK-1)**. |
| **Migration** | **Zero.** Purely additive: one new file where none exists. Verified: `permit=NO_ALLOCATION` on a byte-identical no-op is already accepted against the live ledger (`PHASE1:§6.3`), and that path is unaffected. |
| **Compatibility risk** | The register is a **new tracked file**, which re-enters CY-1 — and the regress is already terminated at exactly one file by construction (`:499-506`). `I-R` consumes that single termination. Any further tracked governance artifact (`B2b`, `Aud1`) must terminate it again, which is the ordering edge in §C.4. |

### B.2 Axis A — binding (`A3`, all 12 models)

| Dimension | Requirement |
|---|---|
| **Code** | `manifest_digest :548-568` gains a whole-document digest input. Verified this phase: it is a pure function of exactly six named fields — `actor`, `allocated`, `counter_advances`, `cursor_advances`, `unmeasured_maps`, `total_allocations` — so all five free dimensions U1–U5 lie in its complement, and closing them requires changing its input set. `plan() :648-661` must emit the new digest so an issuer can transcribe it; `plan()`'s own docstring defines issuance as *"a transcription of this output rather than an independent act of measurement."* |
| **Invariants** | None. |
| **Tests** | Per-leg refusal for U1 (new-record body), U2 (wrong key), U3 (swapped assignment), U4 (`history` content), U5 (`version` / `discovered_volumes` / non-dict top-level keys). The current-behaviour counterparts are `PHASE2`'s probes P2-2, P2-7, P2-3, P2-4, P2-8; U4 was re-measured live this phase (**P3-3**). |
| **Migration** | **Zero data migration**, but **every `manifest_digest` changes**, invalidating every issued permit. Cost today: **nil** — the register does not exist and zero permits have ever been issued (**P3-1**). |
| **Ordering** | **`A3` must land before `I-R` issues its first permit.** Not advice: `PHASE1:§4.2` records the identical outbound constraint already discharged once for `R-5a`, and it is the same mechanism. This is the single hard ordering edge inside the forced set. |

### B.3 Axis B — replay (`B1` in Z-01…Z-06, `B2` in Z-07…Z-12)

| | `B1` reusable — 6 models | `B2` consumed, durable — 6 models |
|---|---|---|
| **Code** | **None.** Amend the claim at `:570-577`, which currently reads *"the same permit cannot be replayed. No spent-permit registry is required, and none is created."* | `commit :870-933` records use under the **existing** `_ledger_lock` (`:216-268`). `B2a` makes `load_permit_register :608-631` read-write; `B2b` adds a second tracked artifact. |
| **Invariants** | None. | None. `B2b` adds one discovered object that itself needs minting (CY-1). |
| **Tests** | One test pinning that replay-after-restore is permitted **by design** — the inverse of `PHASE2` probe P2-1. | Replay-after-restore refusal; a first-use / second-use pair; lock interaction against `_ledger_lock`. |
| **Migration** | Zero. | Zero for `B2a`. `B2b` adds a tracked file → CY-1 re-entry, terminable only after `I-R` lands. |
| **Cost recorded** | The claim at `:570-577` becomes false-then-amended rather than false-and-standing. | `B2a` makes the enforcer a writer of the artifact it enforces, against the stated separation at `:490-497` (*"`commit()` ENFORCES an authorization it does not DECIDE"*) — the same species of documented-property change `PHASE1:§1.5` recorded once already. |

### B.4 Axis D — empty manifest (`D1` in Z-01…Z-03, Z-07…Z-09; `D2` in Z-04…Z-06, Z-10…Z-12)

| | `D1` issuable — 6 models | `D2` not issuable + alternative — 6 models |
|---|---|---|
| **Code** | **None.** Amend `:519` (*"a permit for an empty manifest would authorize nothing and must not be issuable"*). | A distinct authorization path for the non-allocating class in `_verify_permit :714-804`: either a new branch or a widened sentinel, the latter **partially reversing `R-9`** (`:696-707`). |
| **Invariants** | None. | None. |
| **Tests** | Pin empty-manifest issuability; pin that `scope` is vacuous on it — verified vacuous this phase: `scope.maps` compares against an empty `allocated`, and `total_allocations > cap` is `0 > cap`, false for any non-negative cap. | Authorization tests for `history`-only appends and for `version` / `discovered_volumes` changes. |
| **Migration** | Zero. | Zero, **subject to one hard constraint**: `ukb.py:2380-2384` passes `permit=LA.NO_ALLOCATION` on the idempotent exec-declare path — dead code that `R-5a` revived (`PHASE1:§R-5`). `D2` must not re-kill it. |
| **Residual harm** | Eliminated **because** `A3` is fixed across all 12: the permit names one document, so the single universal empty-manifest digest no longer covers a class. Under any model with `A ≠ A3` this harm would persist — but no such model is admissible here. Verified live: append-A, append-B and the no-op all digest to `a7371a31a586a56c…` (**P3-3**). |

### B.5 Axis Aud — mutation and audit (`Aud1` ×4, `Aud2` ×4, `Aud3` ×4)

All three modify the **same four lines**, `uga_engine.py:1331-1335`, plus `uga-declaration.json`. Verified this phase — the invariant in full:

```python
# 10 — every mutation has an audit event
mutated = {e["path"] for e in entries if e["identity_authority"] == "UCOS-UGA-001"}
audited = {ev["object_path"] for ev in audit_events}
v = sorted(mutated - audited)
add("UGA-INV-10", "EVERY_MUTATION_HAS_AUDIT_EVENT", v, len(mutated))
```

and the source of `audited`, `uga_engine.py:1842-1858`, which appends one event per key of `by_object` unconditionally, with `action` always `IDENTITY_MINTED`. Hence `audited ≡ set(by_object.keys())` **by construction**, not merely by measurement — confirmed **True (5374 ≡ 5374)** (**P3-5**).

| | `Aud1` independent + tracked — 4 models | `Aud2` measurement authoritative — 4 models | `Aud3` retire — 4 models |
|---|---|---|---|
| **Code** | An event emitter at the write act (`commit`, or its four call sites) **plus** a persisted tracked log, then `:1332-1334` re-pointed at it. Two hard constraints: `*-audit.json` is forbidden under `00-BOOK/DATA` (`governance_telemetry.py:187-207`) and no wall clock may enter a tracked canonical artifact (`uga_engine.py:1911-1915`). | `:1334`'s name string; `uga-declaration.json`. Optionally split into two invariants. | Remove from `epoch5_invariants` and from the declaration. |
| **Invariants** | `UGA-INV-10` redefined; declared surface stays 30 unless split. | `UGA-INV-10` renamed; 30 unchanged. | **30 → 29.** `cmd_gate :2125-2161` is structurally unaffected. |
| **Tests** | Emitter coverage per mutation element; an **independence** test — the inverse of `audited ≡ set(by_object.keys())`; a determinism/drift test. | Pin the corrected name to the measured set; a duplication test against `UGA-INV-01`. | Assert the invariant is **absent**, so it cannot silently return. |
| **Migration** | Zero data migration. | Zero. | Zero. |
| **Compatibility** | Identical blast radius for all three: **58 files** reference `UGA-INV-10` excluding the two Phase-2 documents, **60** including them — measured this phase, exactly matching `PHASE2`'s 58/59 plus its own document. `PHASE0:§2.4` established that ≥6 historical determinations cite INV-01 and INV-10 as two independent signals, which is one finding double-counted. | same | same, **plus** every citation becomes a reference to a retired invariant. |
| **Ordering** | **`Aud1` must follow `I-R`.** A new tracked audit artifact is a discovered object → needs an identity → needs an allocation → needs a permit → needs the register (CY-1, terminated at one file at `:499-506`, and `I-R` consumes that termination). | No ordering constraint. | No ordering constraint. |


---

## C. Intersection analysis

### C.0 The task register

Tasks are stated at the granularity `PHASE05:§C` used for its `R-1…R-11` units — one unit of change, one file region, one verification obligation. `F-*` are forced (§D); `O-*` are axis-value-conditional.

| ID | Task | Kind | Axis value | Models | Site |
|---|---|---|---|---|---|
| **F-1** | Register producer for `00-BOOK/DATA/allocation-permits.json`, emitting the 9 consumed fields | code (new) | `I-R` | **12** | new artifact beside `00-BOOK/DATA/id-ledger.json` |
| **F-2** | Whole-document digest into `manifest_digest` | code | `A3` | **12** | `ledger_authority.py:548-568` |
| **F-3** | `plan()` emits the document digest for transcription | code | `A3` | **12** | `ledger_authority.py:648-661` |
| **F-4** | A verified permit reaches `ukb build --mint` | code | `I-R` | **12** | `register.sh:216` → `ukb.py:1299` |
| **F-5** | Dispose of E-3 (re-point / rename / remove) | code | `Aud1\|2\|3` | **12** | `uga_engine.py:1331-1335` |
| **F-6** | Invariant-surface declaration update | config | `Aud1\|2\|3` | **12** | `uga-declaration.json` |
| **F-7** | Amend ≥1 false source claim | doc | every | **12** | ≥1 of `:490-497`, `:519`, `:570-577`, `:763-766` |
| **F-8** | Reconcile `UGA-INV-10` citations | doc | `Aud1\|2\|3` | **12** | 58 files (60 incl. Phase-2 docs) |
| **F-9** | Issuance → verification round-trip test | test | `I-R` | **12** | `platform/tests/test_ledger_authority.py` |
| **F-10** | Refusal test per binding, 9 read fields | test | `I-R` | **12** | same |
| **F-11** | Per-leg refusal tests U1–U5 | test | `A3` | **12** | same |
| **F-12** | Pin the chosen E-3 disposal | test | `Aud1\|2\|3` | **12** | UGA invariant tests |
| **F-13** | Re-measure the 30-invariant surface and `cmd_gate` | verification | every | **12** | `uga_engine.py:2125-2161` |
| **O-1** | Amend the no-replay claim | doc | `B1` | 6 | `ledger_authority.py:570-577` |
| **O-2** | Pin replay-after-restore as by-design | test | `B1` | 6 | test suite |
| **O-3** | Record permit consumption under the existing lock | code | `B2` | 6 | `ledger_authority.py:870-933` |
| **O-4** | Replay refusal + first/second use + lock interaction tests | test | `B2` | 6 | test suite |
| **O-5** | Amend the empty-manifest claim | doc | `D1` | 6 | `ledger_authority.py:519` |
| **O-6** | Pin empty-manifest issuability + `scope` vacuity | test | `D1` | 6 | test suite |
| **O-7** | Alternative authorization for the non-allocating class | code | `D2` | 6 | `ledger_authority.py:714-804` |
| **O-8** | Authorization tests for `history` / `version` / `discovered_volumes` | test | `D2` | 6 | test suite |
| **O-9** | Independently-sourced tracked audit emitter + log | code | `Aud1` | 4 | `commit` or call sites + new tracked artifact |
| **O-10** | Emitter coverage + independence + determinism tests | test | `Aud1` | 4 | test suite |
| **O-11** | Coordinate two concurrent edits to `_verify_permit` | code | `B2 ∧ D2` | **3** | `ledger_authority.py:714-804` |

**Total distinct tasks: 24.** By kind: **9 code**, **1 config**, **4 doc**, **9 test**, **1 verification**. **0 migration.**

### C.1 Required by all 12 models

**13 tasks: F-1 … F-13.** Derivations, since three of these are not stated as universal in `PHASE2:§F`:

- **F-1, F-2, F-3, F-9, F-10, F-11** follow directly, because `I-R` and `A3` are fixed across all 12 (§A).
- **F-4** is derived here, not carried from Phase 2. `PHASE2:§F.1` lists a register producer under `I-R` but does not name the call-site plumbing. Verified: `register.sh:216` passes no `--permit`; `ukb.py:1299` resolves `permit=getattr(args, "permit", None)`; `None` is refused. A register with no route to the call site closes E-4A's *existence* question and still leaves `register.sh` Phase 1 failing. Forced in all 12 because `I-R` is.
- **F-5, F-6, F-8, F-12** are forced at the **site** level even though their **content** varies. This is the sharpest result in this section: `Aud1`, `Aud2` and `Aud3` are three different dispositions of E-3, and *all three* edit `uga_engine.py:1331-1335`, *all three* touch `uga-declaration.json`, *all three* carry the identical 58-file citation blast radius, and *all three* require a test pinning the disposition. There is no admissible model in which `uga_engine.py:1331-1335` is left alone — because `Aud-0` (decline) leaves E-3 UNRESOLVED and is therefore not zero-blocker, and `Aud4`/`Aud5` carry NB-3/NB-5.
- **F-7** is `PHASE2:§F.6`'s *"At least one source-claim amendment — **yes**, every model."* Verified as an internal-contradiction argument: CX-1 (`:490-497` versus the measured indistinguishability of key→identifier assignments), CX-2 (`:519` versus `:714-804`) and CX-3 (`:570-577` versus measured replay) are conflicts **internal to the current source**. No model can claim closure while leaving all three standing.
- **F-13** is `PHASE2:§F.6`'s *"Re-running the invariant surface — yes."* `cmd_gate` blocks on every failing invariant (`:2128-2136`), measured FAIL on 2 of 30 today.

### C.2 Required by some models

**11 tasks: O-1 … O-11.** Multiplicities: `{O-1, O-2, O-3, O-4, O-5, O-6, O-7, O-8}` → **6 models each**; `{O-9, O-10}` → **4 models each**; `{O-11}` → **3 models**.

Mutual exclusions, so per-model cost never sums the whole column:

```
B1 ⊕ B2   ->  exactly one of {O-1,O-2} or {O-3,O-4}
D1 ⊕ D2   ->  exactly one of {O-5,O-6} or {O-7,O-8}
Aud1 ⊕ Aud2 ⊕ Aud3 -> {O-9,O-10} only under Aud1; Aud2 and Aud3 add nothing beyond F-5/F-6/F-12
B2 ∧ D2   ->  additionally O-11
```

**O-11 is derived this phase, not carried from Phase 2.** `PHASE2:§F` notes that axis `A` and axis `D` both touch `_verify_permit`/`manifest_digest`. Verified this phase, the picture is tighter: `O-3` (`B2` consumption recording) and `O-7` (`D2` alternative authorization) **both** modify `_verify_permit :714-804` — `O-3` on the register-resolution side at `:714-721`, `O-7` on the branch structure. Three models take both (Z-10, Z-11, Z-12). This is a coordination task, not a new defect, and it is the **only** task in the register whose trigger is a *combination* rather than a single axis value.

### C.3 Required by exactly one model

**ZERO.** This is an exact result, not an absence of investigation, and it follows from two verified structural facts:

1. **`PHASE2:§D.0`'s factorization theorem** — every closure value is a function of one axis. Carried into implementation: every task in §C.0 except `O-11` is triggered by one axis value.
2. **The admissible set is a full product** — `{B1,B2} × {D1,D2} × {Aud1,Aud2,Aud3}`, with no pairing excluded. So each axis value appears in a fixed number of models: `B1`/`B2`/`D1`/`D2` in **6** each (`1×2×3`), `Aud1`/`Aud2`/`Aud3` in **4** each (`2×2×1`).

Therefore the **minimum multiplicity of any single-axis task is 4**, and the one combination-triggered task `O-11` has multiplicity **3**. Both exceed 1.

```
MINIMUM TASK MULTIPLICITY OVER THE 12 ADMISSIBLE MODELS .... 3   (O-11, from B2 ∧ D2)
MINIMUM SINGLE-AXIS TASK MULTIPLICITY ..................... 4   (O-9, O-10, from Aud1)
TASKS REQUIRED BY EXACTLY ONE MODEL ....................... 0
```

**Why this matters and is not a curiosity.** No implementation work is stranded on a single governance outcome. The most expensive discovery an implementer could make — that some task is needed only if one specific model of twelve is selected — does not arise. Every task is either forced (13) or shared by at least a quarter of the admissible set.

### C.4 Per-model task counts

`13 forced + B-contribution (2) + D-contribution (2) + Aud-contribution (2 if Aud1, else 0) + 1 if B2 ∧ D2`:

| Model | Forced | B | D | Aud | O-11 | **Total** |
|---|---|---|---|---|---|---|
| Z-01 `B1 D1 Aud1` | 13 | 2 | 2 | 2 | — | **19** |
| Z-02 `B1 D1 Aud2` | 13 | 2 | 2 | 0 | — | **17** |
| Z-03 `B1 D1 Aud3` | 13 | 2 | 2 | 0 | — | **17** |
| Z-04 `B1 D2 Aud1` | 13 | 2 | 2 | 2 | — | **19** |
| Z-05 `B1 D2 Aud2` | 13 | 2 | 2 | 0 | — | **17** |
| Z-06 `B1 D2 Aud3` | 13 | 2 | 2 | 0 | — | **17** |
| Z-07 `B2 D1 Aud1` | 13 | 2 | 2 | 2 | — | **19** |
| Z-08 `B2 D1 Aud2` | 13 | 2 | 2 | 0 | — | **17** |
| Z-09 `B2 D1 Aud3` | 13 | 2 | 2 | 0 | — | **17** |
| Z-10 `B2 D2 Aud1` | 13 | 2 | 2 | 2 | 1 | **20** |
| Z-11 `B2 D2 Aud2` | 13 | 2 | 2 | 0 | 1 | **18** |
| Z-12 `B2 D2 Aud3` | 13 | 2 | 2 | 0 | 1 | **18** |

```
MINIMUM PER-MODEL TASK COUNT ...... 17   (Z-02, Z-03, Z-05, Z-06, Z-08, Z-09)
MAXIMUM PER-MODEL TASK COUNT ...... 20   (Z-10)
SPREAD ............................  3   tasks — 17.6% of the minimum
```

The spread is narrow because 13 of 17–20 tasks are forced. **65%–76% of the implementation work is invariant under governance choice** (`13/20` at the most expensive model, `13/17` at the cheapest).

### C.5 Dependency ordering, invariant across all 12

Two hard edges, both derived from source rather than from preference:

```
  F-2, F-3  (A3 binding)     ─────>  F-1  (register producer)
      because A3 changes every manifest_digest (:548-568) and changes what plan()
      emits (:648-661). Issuing permits first invalidates them. Free of cost today,
      and only today: zero permits exist (P3-1).

  F-1  (register producer)   ─────>  O-9  (Aud1 tracked audit log)
      because a new tracked artifact re-enters CY-1, whose termination at one file
      (:499-506) is consumed by the register itself.
```

The second edge binds only the 4 `Aud1` models. The first binds all 12 and is the single most consequential ordering fact in this document: **`A3` before `I-R`, or the first permits issued are dead on arrival.** `PHASE1:§4.2` records the identical constraint already honoured once, for `R-5a`.

Every other task pair is order-free. No cycle exists among the 24 tasks.


---

## D. Forced implementation set

The 13 tasks mandatory under every one of the 12 admissible models, with the fact that forces each. **No task below is contingent on any governance value that varies across the admissible set.**

| ID | Forced task | Forcing fact | Verified |
|---|---|---|---|
| **F-1** | Register producer | `permit` is mandatory with no default (`commit :841`); `_verify_permit` resolves `permit_id` against the register at `:714-721`; the register's only writer is the test fixture `_issue` in `platform/tests/test_ledger_authority.py`. `I-R` is fixed across all 12. | **P3-1** + source |
| **F-2** | Document digest into `manifest_digest` | `A3` is the unique axis-A value closing RES-1 (`PHASE2:§D.1`, `§E.2`); `manifest_digest :548-568` is a six-input pure function, so U1–U5 lie in its complement | source, read this phase |
| **F-3** | `plan()` emits it | `plan()`'s docstring defines issuance as transcription of its output; an unemitted digest cannot be transcribed | `:648-661` |
| **F-4** | Permit reaches `ukb build --mint` | `register.sh:216` passes no `--permit`; `ukb.py:1299` passes `getattr(args,"permit",None)`; `None` is refused | **P3-1** + source |
| **F-5** | Dispose of E-3 at `uga_engine.py:1331-1335` | `Aud-0` is not zero-blocker; `Aud4`→NB-3; `Aud5`→NB-5. All three admissible values edit these four lines | **P3-5**, **P3-6** |
| **F-6** | `uga-declaration.json` update | All three admissible `Aud` values change the declared invariant surface (redefine / rename / remove) | `PHASE2:§F.5` |
| **F-7** | ≥1 source-claim amendment | CX-1/CX-2/CX-3 are contradictions internal to the current source; no closure claim survives leaving all three standing | `:490-497`, `:519`, `:570-577` |
| **F-8** | `UGA-INV-10` citation reconciliation | 58 files reference it (60 incl. Phase-2 docs); identical blast radius under all three `Aud` values | measured this phase |
| **F-9** | Issuance round-trip test | `I-R` fixed; no such test can exist today because the register has no producer | derived |
| **F-10** | Per-binding refusal tests, 9 fields | `_verify_permit` performs exactly 9 permit reads; each is an unexercised refusal path in production | **P3-7** |
| **F-11** | U1–U5 leg refusal tests | `A3` fixed; U4 measured exploitable live this phase | **P3-3** |
| **F-12** | Pin the E-3 disposal | `Aud3` in particular needs an absence assertion or the invariant can silently return | `PHASE2:§F.5` |
| **F-13** | Re-measure the invariant surface | `cmd_gate` blocks on every failing invariant (`:2128-2136`); 2 of 30 FAIL today | **P3-6** |

### D.1 What the forced set does **not** include

Stated because omissions are as load-bearing as inclusions, and each omission is a positive verified finding rather than an oversight:

| Not forced | Why | Verified |
|---|---|---|
| **Any data migration** | The live ledger already satisfies every property Phase 1 added, and `I-R` is purely additive. `assert_append_only(live, live)` passes; all 7009 records satisfy R-4; all 1628 snapshot lists satisfy R-5b; zero duplicate identifiers; the ledger round-trips through all three serializers | `PHASE1:§5.2`; ledger sha unchanged this phase |
| **Any permit invalidation** | Zero permits have ever existed. `A3`'s digest churn is free — **today only** | **P3-1** |
| **Any change to `_verify_permit`** | `I-R` requires none (`PHASE2:§F.1`); only `D2` (`O-7`) and `B2` (`O-3`) touch it, and both are optional | source |
| **Any change to `LEDGER-INV-01`** | It measures write paths, not authorization; unaffected by every admissible axis value | `PHASE2:§F.1` |
| **Any change to the 12 Phase-1 closures** | 77/77 tests green this phase; no admissible axis value reverses any of `R-1…R-11`. `D2` *partially reverses* `R-9` — but `D2` is optional, and even then must preserve `ukb.py:2380-2384` | **P3-8** |
| **Any new authority, actor or allow-list** | FD-1 and FD-4 are provably vacuous: `_verify_permit` reads no `issuer`, no `signature`, no `revoked`, no `uses`, no `single_use`; `:728-732` is unconstrained string equality with no allow-list | **P3-2**, **P3-7** |

### D.2 The exact delta from governance-complete to implementation-ready

This is the first success criterion, and it needs a precise reading of both endpoints.

- **Governance-complete** = all 13 decisions in `PHASE2:§E.1` answered; one of the 12 admissible models selected. **Zero code exists.** The artifact is byte-identical to today's.
- **Implementation-ready** = the state Phase 0.5 achieved for the governance-independent twelve: a specification giving, **per unit**, the files, functions, line ranges, invariants, migration, backward compatibility, failure modes and an executable PASS/FAIL verification for each defect.

**The delta is one specification artifact and zero code changes.**

Grounds, by direct comparison of what exists:

| | Governance-independent set | Post-governance set |
|---|---|---|
| Specification granularity | `PHASE05:§C` gives **replacement code** with anchored line ranges — e.g. `§C.1`'s *"# replaces LA:567 and LA:577-581"* | `PHASE2:§F` gives **requirement prose** at axis granularity — e.g. *"a producer … emitting the nine fields `_verify_permit` reads"* |
| Dependency graph | `PHASE05:§D` — a three-wave DAG with five explicit edges, each discharged and evidenced in `PHASE1:§4.1` | §C.5 above — 2 edges, derived, never sequenced into waves |
| Verification spec | `PHASE05:§E` — 12 executable reproductions with a verified run command and PASS/FAIL conditions | none exists |
| Outcome | `PHASE1` — 12 units landed, 77/77 green | not started |

So governance-completeness delivers **decision-completeness**, and the gap to implementation-readiness is exactly the design layer that `PHASE05` supplied once and that no artifact currently supplies for the forced 13 plus the applicable optional 4–7.

```
DELTA: governance-complete  ->  implementation-ready
    code changes ........................ 0
    repository mutations ................ 0
    specification artifacts required .... 1   (a PHASE05-grade design for 17-20 tasks)
    ordering constraints to encode ...... 2   (A3 -> I-R for all 12; I-R -> Aud1 for 4)
    new blockers introduced ............. 0

DELTA: implementation-ready  ->  implemented
    tasks ........................... 17-20  (13 forced + 4-7 conditional)
    migration tasks ..................... 0
    blockers closed ..................... 5
    blockers introduced ................. 0
```

---

## E. Residual analysis

### E.0 Classification scheme

Rule 6 requires four distinct classes. Definitions, applied literally below:

| Class | Definition used here |
|---|---|
| **blocker** | Prevents a required operation from completing, or leaves a false claim standing in source. Must be closed. |
| **residual** | A bounded, known, accepted property. Not closable within the current architecture without a change nobody has authorized. Does not prevent any operation. |
| **unknown** | A question whose answer is not established and cannot be established by any non-mutating act. Neither closed nor accepted — **unmeasured**. |
| **implementation task / verification task** | Work with a determinate outcome, which will either succeed or produce a defect. Not itself a defect. |

### E.1 RES-3 — MW-3 is bounded, not closed

**Classification: RESIDUAL**, carrying one **VERIFICATION TASK**. Not a blocker.

| Aspect | Determination |
|---|---|
| **What it is** | The caller's own ledger read precedes `commit()`, therefore precedes `_ledger_lock`. Verified this phase: `uga_engine.py:2097` calls `LA.commit(LEDGER_PATH, st["ledger"], …)` where `st` was produced by the whole `build()` discovery pass; `commit :870` takes the lock only on entry. The read-to-lock window is real and outside the authority's reach. |
| **Why residual, not blocker** | After `R-6`, MW-3 is covered by **two independent refusals** — key removal (`assert_append_only`) and cross-map identifier uniqueness. `PHASE1:§R-6` records both legs tested: leg 1 fires on the realistic interleaving, leg 2 on the key-preserving one that previously passed. The window persists; the exploit does not. This is exactly what E1-F6's UNVERIFIABLE classification asked for — *"needs a test, not a decision."* |
| **Effect of governance** | **None, under all 12 models.** No admissible axis value relocates the caller's read. Closing MW-3 entirely requires running `uga_engine.build`'s discovery pass under exclusion — governance-independent, and an architecture and performance change beyond any authorization in the input chain. |
| **Activation change** | **LATENT → ACTIVE under all 12.** Today no production write reaches `writer`, so no write can land inside the window. `I-R` opens the path and makes MW-3 live for the first time. This changes exposure, not classification. |
| **Verification task** | Confirm both refusal legs still fire once a real mint runs through the window. Determinate; part of `F-13`'s scope. |
| **Evidence** | `PHASE05:§F.4`; `PHASE1:§R-6`; `uga_engine.py:2097`, `ledger_authority.py:870`, verified this phase |

### E.2 RES-4 — `flock` is advisory and filesystem-dependent

**Classification: RESIDUAL**, carrying one **VERIFICATION TASK**. Not a blocker.

| Aspect | Determination |
|---|---|
| **What it is** | `_ledger_lock :216-268` takes `fcntl.flock(fd, LOCK_EX\|LOCK_NB)` on the ledger's **containing directory**. Advisory: a process that never asks is not excluded. On a filesystem that does not honour `flock`, the control silently degrades. |
| **Why residual, not blocker** | Two verified mitigations. (i) On a platform without `fcntl`, the code **refuses rather than proceeding** — `if fcntl is None: raise LedgerWriteRefused(…)` at `:232-236`, the fail-closed direction. (ii) Where `flock` is present but unhonoured, `R-2`'s pre-write byte re-check at `commit :887-893` is the remaining detector, and it exists and is tested. The residual is a *degradation of defence depth from two layers to one*, not a hole. |
| **Effect of governance** | **None, under all 12 models.** `B2` records consumption *under the existing lock* and so inherits this residual without widening it. No axis value changes the locking primitive. |
| **Activation change** | **PARTIALLY ACTIVE today.** The lock is taken on entry to `commit()`, before `_verify_permit`, so it is already exercised on every production refusal. Its residual risk matters only when a write actually proceeds — which requires `I-R`. Verified working on this platform (macOS/APFS): two subprocesses serialize, contention refuses. |
| **Verification task** | Confirm `flock` is honoured on every filesystem the ledger will live on. Determinate, environmental, outside the repository. |
| **Evidence** | `PHASE05:§F.4`; `PHASE1:§R-3`; `ledger_authority.py:216-268`, read this phase |

### E.3 R-7 post-hoc window (`R-7w`)

**Classification: RESIDUAL.** Not a blocker. The most consequential of the three, and the one whose exposure changes most under governance.

| Aspect | Determination |
|---|---|
| **What it is** | `R-7`'s detection is **post-hoc, by construction**. Verified this phase, exact sequence inside `commit()` under the held lock: `writer(path, ledger)` at **`:893`** → `raw_after = _read_bytes_or_none(path)` at **`:895`** → `if persisted != ledger` at **`:920`** → `_restore(path, raw_before)` at **`:921`**. Divergent bytes therefore **reach disk** before the comparison runs, and a crash between `:893` and `:921` leaves them there. |
| **Why residual, not blocker** | The window is **two file operations wide, under a held exclusive lock**, and every exit path restores the pre-image byte-for-byte — `PHASE1:§R-7` records `Path(path).read_bytes() == original` on all five divergence tests, including the absent-pre-image case that restores to absent rather than to a phantom `{}`. Closing it requires moving serialization inside the authority, which `PHASE1:§R-7` explicitly declined as *"a larger change than this phase covers."* |
| **Why it cannot be closed by comparing bytes instead** | Verified as a hard constraint, not a preference: `commit()` compares **documents** because the three serializers over this one document are not byte-equivalent — `LA._canonical` produces 1 786 167 bytes against both production writers' 2 274 511 (byte-identical to each other). A byte comparison would refuse correct writes. This is `CX-6`, and it is why `A4` is CONTRADICTED and excluded from all 12 admissible models. |
| **Effect of governance** | **None, under all 12 models.** No admissible axis value moves `writer` inside the authority. |
| **Activation change** | **LATENT → ACTIVE under all 12, and this is the sharpest exposure change in this document.** `R-7`'s refusals have never fired in production, because no production write reaches `:893`. Under `I-R` they become live on the first mint. `PHASE05:§F.4` recorded the same mechanism for nine of the twelve Phase-1 defects: supplying any issuance path activates them simultaneously. |
| **Evidence** | `PHASE1:§R-7`; `ledger_authority.py:893`, `:895`, `:920`, `:921`, `:807-822`, `:920-927`, all read this phase |

### E.4 UK-1 — `register.sh` end-to-end completion

**Classification: UNKNOWN**, convertible to a **VERIFICATION TASK** only after implementation **and** an authorization to mutate. Not a blocker. Not a residual.

| Aspect | Determination |
|---|---|
| **What it is** | Whether `register.sh` Phase 1 completes once a permit verifies, and whether the nine dependent phases then pass. |
| **What is established** | The refusal at the call site and the gating structure, both verified this phase. `register.sh:216` is `"$PY" "$HERE/ukb.py" build --mint \|\| fail "ukb build failed" 1`. `fail()` at `:201` ends in `exit "${2:-1}"`. Phases 2/10 through 9/10 (`:221`–`:259`) are each `… \|\| fail …`. So Phase 1's failure terminates the transaction and **nine** subsequent phases never execute. |
| **What is not established** | Everything downstream of a successful Phase 1. |
| **Why unknown and not residual** | A residual is a property that has been *measured and accepted*. UK-1 has never been measured. Phase 0 declined for the recorded reason that `register.sh` *"was not executed — running it would mutate the repository"* (`PHASE0-E4A:§7`). Phase 1 did not execute it. Phase 2 did not. This phase does not. |
| **Why unknown and not blocker** | It blocks no implementation task. All 17–20 tasks in §C can be specified, written and unit-verified without discharging UK-1. It blocks only the *claim* that the transaction works end-to-end. |
| **Effect of governance** | **None.** `PHASE2:§F.6` lists it as required by every model: *"Post-decision verification that cannot be done today — **yes**."* No axis value converts it into something measurable without a mutating run. |
| **Discharge condition** | `F-1` and `F-4` land, then an authorized irreversible registration run. Not before. |
| **Evidence** | `PHASE0-E4A:§7`; `register.sh:201`, `:216`, `:221-259`, read this phase |

### E.5 UK-2 — post-mint gate greenness

**Classification: UNKNOWN.** Recorded here for the first time under its own label. **Not a blocker, and it changes no blocker count in §G.**

`PHASE2:§F.1` states that `UGA-INV-01` *"clears 27 anonymous objects once a mint completes → `cmd_gate` can go green (CY-3)."* Verified this phase that the premise holds: 27 violations, 2 of 30 invariants FAIL, `GATE FAILED — 2 blocking invariant(s)`. The **consequence** is a derivation, not a measurement, and it is unmeasurable for the same reason as UK-1.

Two verified facts make it worth naming separately rather than folding into UK-1:

1. **`00-BOOK/tools/ledger_authority.py` is itself among the 27 anonymous objects** (**P3-6**). Phase 1's own deliverable is an untracked-identity object requiring a mint that requires a permit that requires the register that does not exist. This is CY-1 observed in the live repository, not in the abstract.
2. The other 26 include six further Phase-1-era additions (`omega-gate.yml`, `uci-ratchet.json`, `OMEGA-CLOSURE-REPORT.md`, `omega-ratchet.json`, `omega-surface.json`, and four `engine/tests/universal_discovery/` files). The set is not static — it grows with every new tracked artifact, which is precisely what `B2b` and `Aud1` would add.

So the open question is narrower than "does the gate go green": it is **whether the 27 clear in one mint given the set can grow between measurement and mint.** Unmeasurable without the mutating run.

### E.6 One reclassification against Phase 2, flagged

`PHASE2:§G.5` groups **four** items as *"NON-BLOCKER RESIDUALS"*: RES-3, RES-4, R-7w and UK-1. Under Rule 6's four-way distinction, UK-1 does not satisfy the definition of a residual — it is unmeasured rather than measured-and-accepted, and it is discharged by an act rather than accepted as a property.

**This phase therefore reports 3 residuals and 2 unknowns where Phase 2 reported 4 residuals.** No item is added or dropped; UK-1 moves class and UK-2 is newly named. The total non-blocker count moves from 4 to 5, entirely because UK-2 is named. Stating this plainly: the change is in classification and labelling, not in the substance any input established, and **no blocker count moves**.

### E.7 Residual summary across all 12 models

| Item | Class | Blocker? | Closed by any of the 12? | Latent today? | Active after implementation? |
|---|---|---|---|---|---|
| **RES-3** MW-3 window | residual | no | **no — all 12 identical** | yes | **yes** |
| **RES-4** advisory `flock` | residual | no | **no — all 12 identical** | partially | **yes** |
| **R-7w** post-hoc detection | residual | no | **no — all 12 identical** | yes | **yes** |
| **UK-1** `register.sh` end-to-end | unknown | no | **no — all 12 identical** | n/a | resolvable only by a mutating run |
| **UK-2** post-mint gate greenness | unknown | no | **no — all 12 identical** | n/a | resolvable only by a mutating run |

**Every one of the five is invariant across all 12 admissible models.** None is a governance question; each was classified as a bound or a gap before governance entered, by `PHASE05:§F.4`, `PHASE1:§R-3`/`§R-6`/`§R-7` and `PHASE0-E4A:§7`. The single change governance produces is **exposure**: three latent residuals become active, because `I-R` opens a write path that has never been open.


---

## F. Readiness determination

### F.1 Is unconditional implementation readiness achievable?

**NO.**

"Unconditional" admits two readings. Both are answered, because conflating them is how this question gets answered wrongly.

**Reading 1 — unconditionally ready to *begin* implementation, with no unmet precondition.**

**NO.** Exactly one precondition is irreducible: **governance selection on the five closure axes.** Three independent grounds:

1. **`A = A3` is forced and cannot be satisfied by ratification.** It is the unique axis-A value closing RES-1 (`PHASE2:§D.1`, `§E.2`), and it changes `manifest_digest`'s input set (`:548-568`) and `plan()`'s emitted output (`:648-661`). Verified this phase: `manifest_digest` is a pure function of six named fields, so U1–U5 lie in its complement and cannot be closed without changing those inputs. **No full-closure model has zero implementation.**
2. **The remaining four axes are not forced** (`PHASE2:§E.2`): `I ∈ {I-R, I-D}`, `B ∈ {B1, B2}`, `D ∈ {D1, D2, D3}`, `Aud ∈ {Aud1…Aud4}` each have ≥2 CLOSED values. So implementation content genuinely varies, and 4–7 tasks per model (§C.4) cannot be written before the selection.
3. **This phase is forbidden to make that selection** (Rule 3), and would be wrong to: `PHASE2:§I` records the next act as a governance decision, and nothing here prejudges it.

**Reading 2 — unconditionally ready such that implementation completes with no unknown remaining.**

**NO**, and this reading fails permanently rather than pending a decision. Two grounds:

1. **UK-1 and UK-2 are undischargeable without an irreversible mutating run.** No governance answer changes this; `PHASE2:§F.6` lists it as required by every model. The input chain declined the run four consecutive times, each time for the same recorded reason.
2. **Three residuals survive every admissible model by construction** (§E.7), because none is a governance question. RES-3 needs `uga_engine.build`'s discovery pass under exclusion; R-7w needs serialization inside the authority; RES-4 needs a guarantee no filesystem provides. All three are governance-**independent** and were declined by authorization scope, not by governance uncertainty.

**The maximal reachable state, named precisely:**

```
    READY — CONDITIONAL ON GOVERNANCE SELECTION

    reachable under ................ 12 of 12 admissible models
    precondition ...................  1  (governance selection, 5 axis decisions)
    new blockers introduced ........  0
    blockers on reaching it ........  0
    residuals ......................  3   (RES-3, RES-4, R-7w)
    unknowns .......................  2   (UK-1, UK-2)
```

The condition is a **single, fully-specified, decidable** precondition — not an open-ended one. All twelve values that satisfy it are enumerated in §A, and the implementation consequence of each is enumerated in §B and §C. That is a materially different situation from a condition whose satisfaction set is unknown, and it is the honest ceiling.

### F.2 Under how many closure models?

```
CONSISTENT GOVERNANCE-COMPLETE MODELS (PHASE2 §D.3) ........ 243
    FULL-CLOSURE MODELS .....................................  42
        ZERO-NEW-BLOCKER FULL-CLOSURE MODELS ................  12   <- admissible here
            reaching READY-CONDITIONAL-ON-SELECTION .........  12   <- all of them
            reaching UNCONDITIONAL READY ....................   0   <- none of them
```

**All 12 reach conditional readiness. None reaches unconditional readiness.** The count is 12 and not fewer because the blocking factors (governance selection, UK-1, UK-2, three residuals) are **invariant across the admissible set** — no model is better or worse positioned, which is itself the reason no recommendation follows from this analysis.

The alternative 24-model reading is declined for the reason `PHASE2:§D.3` declined it, with the non-transferability consequence recorded in §A.

### F.3 What implementation work remains?

```
DISTINCT TASKS ACROSS ALL 12 MODELS ........................  24
    forced   (all 12 models) ...............................  13
    optional (4-6 models each, 3 for O-11) .................  11
    required by exactly one model ..........................   0

PER-MODEL TASK COUNT ................................... 17 - 20
    minimum 17 .... Z-02, Z-03, Z-05, Z-06, Z-08, Z-09
    maximum 20 .... Z-10
    forced share ......................................  65% - 76%

BY KIND (union over all 12)
    code ...................................................   9
    config .................................................   1
    documentation / claim amendment ........................   4
    test ...................................................   9
    verification ...........................................   1
    migration ..............................................   0

ORDERING CONSTRAINTS ......................................   2
    A3 -> I-R    binding before issuance ....... all 12 models
    I-R -> Aud1  register before tracked log ...  4 models
```

The four load-bearing code tasks required by every model: **a register producer** (`F-1`), **a whole-document binding in `manifest_digest`** (`F-2`, `F-3`), **permit plumbing to `register.sh`'s minting call** (`F-4`), and **a disposal of E-3 at `uga_engine.py:1331-1335`** (`F-5`).

### F.4 What risks remain?

Ordered by the size of the surface each touches, not by likelihood — likelihood is not established.

| # | Risk | Scope | Basis | Mitigation status |
|---|---|---|---|---|
| **1** | **Ordering violation: `I-R` before `A3`.** Every issued permit is invalidated, because `A3` changes every `manifest_digest`. | all 12 | `:548-568`; `PHASE1:§4.2` records the identical constraint honoured once for `R-5a` | **Free to avoid today, and only today.** Zero permits exist (**P3-1**). The cost of getting this wrong grows from zero the moment the first permit is issued. |
| **2** | **`UGA-INV-10` citation blast radius.** 58 files reference it (60 incl. Phase-2 docs); ≥6 historical determinations cite INV-01 and INV-10 as independent signals, which `PHASE0:§2.4` established is one finding double-counted. `Aud3` additionally turns every citation into a reference to a retired invariant. | all 12 | measured this phase | Not mitigated. Documentation-scale, mechanical, but unavoidable and easy to under-scope. |
| **3** | **Three residuals go live simultaneously.** RES-3, R-7w and RES-4's write-path leg activate on the **first** mint, having never executed in production. | all 12 | §E.7; `PHASE05:§F.4`'s recorded activation mechanism | Partially mitigated: R-7 and R-6 refusals are unit-tested (`PHASE1`). Never exercised end-to-end. |
| **4** | **`D2` partially reverses `R-9`.** A widened sentinel re-opens what `:696-707` closed, and must not re-kill `ukb.py:2380-2384` — the idempotent branch `R-5a` revived from dead code. | 6 | `PHASE2:§F.4`; `PHASE1:§R-5`, `§R-9` | Not mitigated. The one task in the register that touches a Phase-1 closure. |
| **5** | **`B2a` inverts a documented design property.** Making `load_permit_register` read-write turns the enforcer into a writer of the artifact it enforces, against `:490-497` (*"`commit()` ENFORCES an authorization it does not DECIDE"*). | ≤6 | `:490-497`, `:608-631` | Not mitigated. Same species as the change `PHASE1:§1.5` recorded once. `B2b` avoids it and re-enters CY-1 instead. |
| **6** | **CY-1 re-entry.** The identity regress is terminated at exactly one file (`:499-506`), and `I-R` consumes that termination. `B2b` and `Aud1` each add a second tracked governance artifact. | ≤10 | `:499-506`; §C.5's second ordering edge | Mitigated by ordering only — `I-R` must land first. |
| **7** | **Two concurrent edits to `_verify_permit`.** `O-3` and `O-7` both modify `:714-804`. | 3 | derived, §C.2 | Coordination, not a defect. Named so it is not discovered as a merge conflict. |
| **8** | **`Aud1`'s tracked log has two hard constraints that are easy to miss.** `*-audit.json` is forbidden under `00-BOOK/DATA` (`governance_telemetry.py:187-207`) and no wall clock may enter a tracked canonical artifact (`uga_engine.py:1911-1915`). | 4 | `PHASE2:§C.8` | Not mitigated. Both are enforced elsewhere in the codebase and will fail loudly. |

**One risk explicitly ruled out.** Data migration. Zero migration is required under all 12 models, verified: the live ledger already satisfies every property Phase 1 added, `I-R` is purely additive, and `A3`'s digest churn invalidates nothing because nothing exists to invalidate (`PHASE1:§5.2`; **P3-1**).

### F.5 What unknowns remain?

```
UNKNOWNS ................................................... 2

  UK-1  register.sh Phase 1 end-to-end completion, and the nine
        || fail-gated phases at register.sh:221-259.
        Established:   the refusal at :216 (no --permit) and the
                       gating structure (fail() exits at :201).
        Unknown:       everything downstream of a successful Phase 1.
        Discharge:     F-1 + F-4, then an authorized irreversible
                       registration run.  Not before.
        Governance:    irrelevant — identical under all 12 models.

  UK-2  Whether the 27 anonymous objects clear in one mint, and
        cmd_gate goes green.
        Established:   27 violations, 2 of 30 invariants FAIL,
                       GATE FAILED (P3-6, executed this phase).
                       ledger_authority.py -- Phase 1's own deliverable
                       -- is itself one of the 27.
        Unknown:       the consequence. PHASE2 §F.1 derives it; nobody
                       has measured it. The 27-set grows with every new
                       tracked artifact, which B2b and Aud1 add.
        Discharge:     same mutating run as UK-1.
        Governance:    irrelevant — identical under all 12 models.
```

**Neither is a blocker.** All 24 tasks can be specified, written and unit-verified without discharging either. What they block is the **claim** that the registration transaction works end-to-end — which is a certification question, not an implementation-readiness question.

**Both were declined four consecutive times for one consistent reason**, and that consistency is the reason they remain: `PHASE0-E4A:§7` (*"`register.sh` was **not** executed — its behaviour is determined from source … not from a run that would have mutated the repository"*), `PHASE1:§5.1` (*"`commit()` was **never** called against the production ledger"*), `PHASE2:§H.1` (*"No new probe was run against the repository"*), and this phase (**P3-1 … P3-8** all read-only or in-memory; ledger sha256 identical before and after).

---

## G. Exact counts

### G.1 The requested counts

```
TOTAL CLOSURE MODELS ........................................  12
    (zero-new-blocker full-closure, PHASE2 §D.3; admissible per Rule 4)
    context: 243 consistent governance-complete
              42 full-closure
              12 full-closure with zero new blockers   <- this set

TOTAL IMPLEMENTATION TASKS ..................................  24
    (distinct tasks across the union of all 12 models)

FORCED IMPLEMENTATION TASKS .................................  13
    F-1 register producer                          code
    F-2 manifest_digest document binding           code
    F-3 plan() emits the document digest            code
    F-4 permit reaches ukb build --mint             code
    F-5 dispose of E-3 at uga_engine.py:1331-1335   code
    F-6 uga-declaration.json surface update         config
    F-7 amend >=1 false source claim                doc
    F-8 reconcile UGA-INV-10 citations (58 files)   doc
    F-9 issuance -> verification round-trip test    test
    F-10 refusal test per binding (9 read fields)   test
    F-11 U1-U5 leg refusal tests                    test
    F-12 pin the chosen E-3 disposal                test
    F-13 re-measure the 30-invariant surface        verification

OPTIONAL IMPLEMENTATION TASKS ...............................  11
    O-1  B1  amend :570-577                    doc    6 models
    O-2  B1  pin replay-by-design              test   6 models
    O-3  B2  record consumption in commit      code   6 models
    O-4  B2  replay/use-pair/lock tests        test   6 models
    O-5  D1  amend :519                        doc    6 models
    O-6  D1  pin issuability + scope vacuity   test   6 models
    O-7  D2  alternative authorization branch  code   6 models
    O-8  D2  non-allocating-class auth tests   test   6 models
    O-9  Aud1 tracked audit emitter + log      code   4 models
    O-10 Aud1 emitter/independence/determinism test   4 models
    O-11 B2 & D2 _verify_permit coordination   code   3 models

    tasks required by exactly one model ......................   0
    minimum task multiplicity ................................   3   (O-11)
    minimum single-axis task multiplicity ....................   4   (O-9, O-10)
    per-model task count ................................. 17 - 20

MIGRATION TASKS .............................................   0
    verified: live ledger already satisfies every Phase-1 property;
    I-R is purely additive; zero permits exist to invalidate

REMAINING BLOCKERS
    today, measured .........................................   5   E-4A, E1-F3, E-3, RES-1, RES-2
    after governance closure - DECISION level ................   0
    after governance closure - ARTIFACT level ................   5   <- unchanged; governance writes no code
    after implementation completion ..........................   0

REMAINING RESIDUALS .........................................   3   RES-3, RES-4, R-7w
    closed by any of the 12 models ..........................   0
    activated (latent -> live) by all 12 .....................   3

REMAINING UNKNOWNS ..........................................   2   UK-1, UK-2
    closed by any of the 12 models ..........................   0
    dischargeable without an irreversible mutating run ......   0

NEW BLOCKERS INTRODUCED BY THIS PHASE .......................   0
```

### G.2 Blocker count at each state — the two-count distinction

The task asks for the blocker count *after governance closure* and *after implementation completion*. The first requires care, and reporting a single number for it would be wrong.

| State | Blockers | Basis |
|---|---|---|
| **Today** (post-Phase-1) | **5** | `PHASE1:§6.2`; all five re-verified open this phase — **P3-1** through **P3-6** |
| **Governance-complete**, no code — *decision level* | **0** | `PHASE2:§G.5`: all five rows CLOSED under any of the 12. A statement about **decisions**. |
| **Governance-complete**, no code — *artifact level* | **5** | Governance writes no code. Verified today: all three `permit` values still refused on a real allocating manifest (**P3-1**); `single_use` absent (**P3-2**); the empty-manifest digest still universal (**P3-3**); `audited ≡ set(by_object.keys())` still True (**P3-5**); `UGA-INV-01`/`UGA-INV-10` still FAIL at 27 with identical sets (**P3-6**). E-4A remains a **total block on every production write** until `F-1` and `F-4` land. |
| **Implementation complete** (17–20 tasks) | **0** | All 12 models are full-closure and zero-new-blocker by construction (`PHASE2:§D.1`, `§D.3`) |

**Both numbers are reported because both are true of different things.** `PHASE2:§G.5`'s zero is decision-closure and is correct as such. The artifact-level five is what an implementer starting work will find in the tree, and is equally correct. Reporting only the zero would imply the repository moves when a decision is made; reporting only the five would deny that governance closes anything. The delta between them — **5 blockers, 0 code** — is precisely the implementation work §C enumerates.

### G.3 Success criteria

| Criterion | Discharge |
|---|---|
| **Exact implementation delta from governance-complete to implementation-ready** | **0 code changes; 0 repository mutations; 1 specification artifact** (a `PHASE05`-grade design for 17–20 tasks); **2 ordering constraints** to encode. Then 17–20 tasks to implemented. §D.2, with the comparison to what `PHASE05:§C`/`§D`/`§E` supplied for the governance-independent twelve. |
| **Exact blocker count after governance closure** | **0 at decision level; 5 at artifact level.** Both reported, both grounded, distinction explained. §G.2. |
| **Exact blocker count after implementation completion** | **0**, under all 12 models. Plus **3 residuals** and **2 unknowns**, none of which is a blocker and none of which any model closes. §G.1. |
| **Explicit YES/NO on unconditional implementation readiness** | **NO.** §F.1 and §G.4. |
| No code changes | No source file modified. Ledger `sha256 8471e709…c20b` before and after; `git status --porcelain 00-BOOK/DATA/` empty. |
| No repository mutations | This document is the only file written. |
| No governance selection | No axis assigned. All results quantified over the 12 admissible models. |
| All 12 models admissible | §A enumerates them exactly; `1×1×2×2×3 = 12` verified against `PHASE2:§D.3`'s product form. |
| Every claim sourced or executed | §H. Every `file:line` re-read this phase against the current tree; 8 probes executed; three citation/count discrepancies in the inputs resolved by measurement. |
| Four-way classification applied | §E.0 defines; §E.1–§E.5 apply; §E.6 flags the one reclassification against `PHASE2:§G.5`. |
| No governance model recommended | None. Every ordering is a dependency ordering derived from source. |

### G.4 The answer

```
================================================================================
  UNCONDITIONAL READY FOR IMPLEMENTATION?                              N O
================================================================================

  Reachable state ....... READY, CONDITIONAL ON GOVERNANCE SELECTION
  Reachable under ....... 12 of 12 admissible closure models
  Irreducible condition .  1 -- governance selection on 5 closure axes
  New blockers .......... 0
  Implementation cost ... 17-20 tasks (13 forced, 4-7 conditional, 0 migration)

  Why not unconditional -- three independent reasons, none removable by
  any governance answer:

    1. A = A3 is forced for full closure and cannot be satisfied by
       ratification: it changes manifest_digest's input set (:548-568)
       and plan()'s emitted output (:648-661).  No full-closure model
       has zero implementation.

    2. UK-1 and UK-2 are undischargeable without an irreversible
       mutating run.  Identical under all 12 models.  Declined four
       consecutive times for the same recorded reason.

    3. RES-3, RES-4 and R-7w survive every admissible model by
       construction -- none is a governance question, and all three
       were bounded rather than closed by authorization scope.

  Governance completion yields DECISION-completeness.
  Implementation completion yields BLOCKER-completeness.
  Neither yields UNCONDITIONAL readiness, and no combination does.
================================================================================
```


---

## H. Evidence

### H.1 Probes executed this phase

All read-only or operating on in-memory `deepcopy` objects. No `commit()` call, no register creation, no repository mutation.

| ID | Claim established | Method | Outcome | Mutating? |
|---|---|---|---|---|
| **P3-1** | E-4A open: register absent; all three `permit` values refused against a **real allocating manifest** measured from the live ledger | `LA.plan` + `LA._verify_permit` on an in-memory copy with one injected `by_object` record | `register exists: False`; `allocating=True total=1`; `permit=None` → *permit must be a permit_id string or NO_ALLOCATION*; `permit='P-ANY'` → *not in …/allocation-permits.json*; `permit=NO_ALLOCATION` → *this write ALLOCATES* | **no** |
| **P3-2** | E1-F3 open: no consumption mechanism exists | string count over `ledger_authority.py` | `single_use` **0**, `issuer` **0**, `revoked` **0**, `"uses"` **0**; `signature` **1** — the prose comment at `:497`, not a read | no |
| **P3-3** | RES-1 (U4 leg) and RES-2 live on the production ledger | `LA.plan` on three in-memory variants of the live ledger | two materially different `history` appends **and** the byte-identical no-op all digest to `a7371a31a586a56c…`, `allocating=False total=0` — one universal value | **no** |
| **P3-4** | RES-2's mechanism: `_verify_permit`'s permit path reads neither `allocating` nor `total_allocations`; `scope` is vacuous on an empty manifest | source read `:714-804` | confirmed — `scope.maps` compares against empty `allocated`; `total_allocations > cap` is `0 > cap` | no |
| **P3-5** | E-3 tautology **by construction**, not merely by measurement | source read `uga_engine.py:1331-1335` + `:1842-1858`; set comparison on the live ledger | `audit_events` built unconditionally from `sorted(by_object)`, `action` always `IDENTITY_MINTED`; `audited == set(by_object.keys())` → **True (5374 ≡ 5374)** | no |
| **P3-6** | E-3 open and E-4A's gate consequence, measured | `uga_engine.py gate` and `U.build(mint=False)` | `UGA-INV-01 FAIL violations=27 measured=6804`; `UGA-INV-10 FAIL violations=27 measured=5207`; shown violation sets **identical**; **2 of 30** invariants FAIL; `GATE FAILED`; `00-BOOK/tools/ledger_authority.py` is itself among the 27 | **no** — `cmd_gate` docstring: *"Verify without mutating. Fails closed."* Ledger sha verified identical after |
| **P3-7** | `_verify_permit` performs exactly **9** permit reads — the register producer's complete output contract | `grep` of `permit.get` / `scope.get` / `p.get` over `:714-804` | `permit_id`, `actor`, `manifest_digest`, `preimage_digest`, `head`, `scope`, `scope.maps`, `scope.max_allocations`, `expires_at` = 9 | no |
| **P3-8** | Phase-1 baseline intact | `pytest platform/tests/test_ledger_authority.py` | **77 passed** — matches `PHASE1:§4`'s terminal row exactly | temp dirs only |

**Non-mutation, verified before and after every probe:**

```
$ shasum -a 256 00-BOOK/DATA/id-ledger.json
8471e709b178a9a09909bca55f2e8eccb78161db8423026d1d26e4f35c41c20b
$ git status --porcelain 00-BOOK/DATA/
(0 lines)
```

### H.2 Source references re-read this phase

Every line reference used in this document was re-read against the current tree — `ledger_authority.py` 933 lines, `uga_engine.py` 2191 lines, `ukb.py` 2579 lines, working tree at `77798202`.

| Reference | Content confirmed |
|---|---|
| `ledger_authority.py:507` | `PERMIT_REGISTER_NAME = "allocation-permits.json"` |
| `:514`, `:519` | `class _NoAllocation`; the empty-manifest claim (CX-2 / RES-2) |
| `:548-568` | `manifest_digest` — pure function of exactly six named fields (RES-1) |
| `:570-577` | `preimage_digest` — the no-replay claim (CX-3 / E1-F3) |
| `:603-605`, `:608-631` | `permit_register_path`, `load_permit_register` — the single register access, read-only; accepts a bare list or `{"permits": [...]}` |
| `:648-661` | `plan()` |
| `:664-804` | `_verify_permit` — signature, sentinel branch, and the 9-field permit path |
| `:696-707` | `R-9`'s sentinel document check |
| `:807-822` | `_restore` |
| `:825-838` | `_refuse_unmoved_allocation` |
| `:841`, `:870`, `:887-893`, `:893`, `:895`, `:920`, `:921` | `commit` — mandatory `permit`; lock entry; `R-2` pre-write re-check; `writer`; `raw_after`; document comparison; `_restore` (R-7w) |
| `:216-268` | `_ledger_lock` — directory `flock`, `fcntl is None` → refuse (RES-4) |
| `:142-149`, `:151-162` | `_identifier_index`, `_record_index` |
| `uga_engine.py:1231` | `UGA-INV-01 EVERY_OBJECT_HAS_UNIVERSAL_ID` |
| `uga_engine.py:1331-1335` | `UGA-INV-10` — all four lines (E-3) |
| `uga_engine.py:1842-1858` | `audit_events` construction — unconditional over `by_object` |
| `uga_engine.py:2097`, `:2102`, `:2125`, `:2177` | `LA.commit` call site (RES-3); `bytes_changed` consumer; `cmd_gate`; `--permit` flag |
| `ukb.py:1299`, `:2380-2384`, `:2401`, `:2497`, `:2555` | three `LA.commit` call sites; the `R-5a`-revived idempotent branch; two `--permit` flags |
| `register.sh:201`, `:216`, `:221-259` | `fail()` exits; Phase 1 passes no `--permit`; nine `\|\| fail`-gated phases (UK-1) |
| `platform/tests/test_ledger_authority.py` | `_issue` — the register's only writer; writes `{"permits":[…]}` with 9 fields incl. `single_use`, which the module never reads |

### H.3 Three input discrepancies resolved by measurement

Recorded because each was load-bearing somewhere in the input chain, and because Rule 5 requires claims to be backed rather than averaged.

| # | Discrepancy | Resolution | Consequence |
|---|---|---|---|
| **1** | `UGA-INV-10` violation count: `PHASE0:§2.4` and `PHASE2:§A.3` report **27**; `PHASE1:§6.2` reports **25** | **Both read a real field; the true count is 27.** Measured: `violation_count = 27`, `len(violations) = 25`, `violations_truncated = 2`. `add()` truncates the stored list at 25 (`sorted(violations)[:25]`). Phase 1 read the truncated list; Phase 0 and Phase 2 read the count. | None substantive. **27** is used throughout this document. |
| **2** | Third `--permit` flag: `PHASE2:§A.2`, `§C.9`, `§F.1` cite `uga_engine.py:2079` | **The flag is at `uga_engine.py:2177`.** Line 2079 is the `LA.plan` call inside `cmd_run`. `cmd_gate` at `:2125` matches Phase 2 exactly, so the drift is confined to this one citation. | Citation corrected in §B.0. The artifact — three inert `--permit` flags — is confirmed present. |
| **3** | `UGA-INV-10` file references: `PHASE2:§F.5` reports **58** (59 incl. `PHASE2-GOVERNANCE-DEPENDENCY-MAP.md`) | **Confirmed exactly.** 58 excluding every Phase-2 and Phase-3 document; 60 including the two Phase-2 documents; 61 including this one. | **58** used as the blast radius, matching Phase 2. The figure is stable under the addition of determination documents, which is why the exclusion is stated. |

### H.4 Provenance of every load-bearing claim

| Claim | Backed by |
|---|---|
| The 12 admissible models and their product form | `PHASE2:§D.3`; arithmetic re-verified `1×1×2×2×3 = 12` |
| `A3` forced for full closure | `PHASE2:§D.1` (RES-1 × axis A), `§E.2`; mechanism verified at `:548-568` |
| Each excluded axis value's new blocker | `PHASE2:§C.9` NB-1…NB-6; `I-D`'s dead-interface referents verified at `:714-721`, `ukb.py:2497`, `ukb.py:2555`, `uga_engine.py:2177` |
| Per-axis implementation requirements | `PHASE2:§F.1-F.5`, re-grounded on source re-read this phase |
| **F-4** register.sh plumbing is forced | **DERIVED this phase.** `register.sh:216` + `ukb.py:1299` + the `permit=None` refusal (**P3-1**). Not stated in `PHASE2:§F.1`. |
| **O-11** `B2 ∧ D2` coordination | **DERIVED this phase.** Both `O-3` and `O-7` modify `_verify_permit :714-804`. |
| Zero tasks required by exactly one model | **DERIVED this phase** from `PHASE2:§D.0`'s factorization theorem plus the full-product structure of the admissible set. Multiplicity floor 3. |
| Zero migration under all 12 | `PHASE1:§5.2`; **P3-1** (zero permits); `I-R` additive by construction |
| `A3 → I-R` ordering | `PHASE2:§E.2`; `PHASE1:§4.2`'s identical discharged constraint for `R-5a`; `:548-568`, `:648-661` |
| `I-R → Aud1` ordering (CY-1) | `PHASE2:§B.2`, `§E.2`; termination at one file stated in source at `:499-506` |
| RES-3 classification and invariance | `PHASE05:§F.4`; `PHASE1:§R-6`; `uga_engine.py:2097` + `ledger_authority.py:870` |
| RES-4 classification and fail-closed leg | `PHASE05:§F.4`; `PHASE1:§R-3`; `:216-268`, `:232-236` |
| R-7w classification and exact window | `PHASE1:§R-7`; `:893` → `:895` → `:920` → `:921`, read this phase |
| R-7's document-not-bytes comparison is forced | `PHASE1:§R-11` (1 786 167 vs 2 274 511 bytes); CX-6; `:920-927` |
| UK-1 structure | `PHASE0-E4A:§7`; `register.sh:201`, `:216`, `:221-259` |
| UK-2 premise | **P3-6**, executed. The consequence is a `PHASE2:§F.1` derivation, labelled as such. |
| 58/60 `UGA-INV-10` references | measured this phase; matches `PHASE2:§F.5` |
| `_verify_permit`'s 9-field contract | **P3-7**, executed |
| FD-1 / FD-4 vacuity | **P3-2**, **P3-7**; `:728-732` unconstrained string equality, no allow-list |
| Phase-1 baseline green | **P3-8** — 77 passed |

**No claim in this document rests on unexecuted reasoning without being labelled DERIVED.** Where a Phase-2 or Phase-0.5 result is carried forward, its source section is named and its mechanism re-verified against the current tree.

---

## I. Stop condition

Phase 3 ends here.

- **Closure models inventoried:** 12, exactly the zero-new-blocker full-closure set, expanded from `PHASE2:§D.3`'s product form and verified `1×1×2×2×3 = 12`.
- **Implementation inventory:** complete per model across code, invariants, tests and migration — §B.
- **Intersection:** 13 forced · 11 optional · **0 required by exactly one model** · multiplicity floor 3 · per-model 17–20 — §C.
- **Forced set:** 13 tasks, each with its forcing fact — §D. Delta from governance-complete to implementation-ready: **0 code, 1 specification artifact, 2 ordering constraints** — §D.2.
- **Residuals classified:** RES-3 residual · RES-4 residual · R-7w residual · UK-1 **unknown** (reclassified from `PHASE2:§G.5`, flagged in §E.6) · UK-2 unknown (newly named, not a blocker, changes no blocker count).
- **Blockers:** 5 today · 0 after governance at decision level · **5 after governance at artifact level** · 0 after implementation.
- **Residuals after implementation:** 3, none closable by any of the 12, all three activated latent→live by all 12.
- **Unknowns after implementation:** 2, neither dischargeable without an irreversible mutating run.
- **New blockers introduced by this phase:** **0.**
- **UNCONDITIONAL READY FOR IMPLEMENTATION:** **NO.** Maximal reachable state is READY-CONDITIONAL-ON-GOVERNANCE-SELECTION, under all 12 models.
- **Governance selected:** none. Decisions taken: **0.** Models recommended, ranked or preferred: **0.** FD-1, FD-2, FD-3′, FD-4, FD-5 — **treated as UNKNOWN throughout.**
- **Code changed:** none. **Repository files modified:** none. **Live ledger:** byte-identical, `sha256 8471e709…c20b`, verified before and after every probe.

The next act remains a governance decision on the five closure axes. Nothing here prejudges which value any axis takes; §C.3's result — that no implementation task is stranded on a single model — is stated precisely so that it cannot be read as an argument for any particular one.
