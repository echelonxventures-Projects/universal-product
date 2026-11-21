# Self-Coverage Closure — Gap Register

| Field | Value |
|---|---|
| MISSION | Measure self-coverage closure. Enumerate every gap in the certification graph. |
| AUTHORITY | **NONE — DERIVED TRUTH.** This document certifies nothing, ratifies nothing, creates no authority and repairs nothing. |
| METHOD | Read-only measurement at HEAD, using the repository's own discovery rules. Every count below is reproducible by the commands in §9. |
| BASELINE | HEAD `446f8a0f`, branch `integration/recovery-001`, working tree **DIRTY (91 entries at start, 95 at end)** |
| GRAPH | `SELF-COVERAGE-GRAPH.md` |
| MEASUREMENT CONDITION | A concurrent per-law mutation campaign rewrote `engine/enforcement_closure/contract.py` during the measurement window. It restored the file with a digest check (`total killed 13 SURVIVED 0`), and **every figure below was re-executed on the restored tree and is byte-identical.** See `SC-G0`. |
| DISPOSITION | **MEASUREMENT ONLY. NO REPAIR PERFORMED.** No gap below was closed, narrowed, reclassified or referred. |

---

## 0 · Summary

Self-coverage closure is **NOT CLOSED**. Six gap classes are open. The one that matters most is
the last: the certification chain has no certified terminus anywhere, and by the repository's own
constitutional design it cannot acquire one from inside the corpus.

| ID | Gap class | Measured | Population | Status |
|---|---|---:|---|:-:|
| **SC-G1** | Unverified certifiers | **18 / 48** | gate engines no test names | OPEN |
| **SC-G2** | Self-certifying objects | **38 / 48** | certifiers writing the verdict into their own home | OPEN |
| **SC-G3** | Circular certification | **40 self-loops · 1 data cycle** | governance + data-dependency planes | OPEN |
| **SC-G4** | Missing certification paths | **549 / 549 · 103 / 103** | requirements with no gate edge; proofs with a vacant certifier slot | OPEN |
| **SC-G5** | Unreachable certification nodes | **6 engines · 51 gate targets · 3 declarations** | nodes no plane can enter | OPEN |
| **SC-G6** | Uncertified roots | **3** | `UEC-000001` (self) · `REG-AUTO-001` (unregistered) · `T1` (vacant) | OPEN |

Note the posture this produces. `UEC-000001` — the meta-gate that certifies the certifiers —
measured **OPEN, 13 of 13 laws holding** at this baseline. SC-G1, SC-G5 and part of SC-G3 are not
violations of it. They sit **exactly at their declared ratchet ceilings**, which is what the
ratchet is for: it caps the debt so it cannot grow silently, and it refuses if a repair fails to
tighten the ceiling. A passing meta-gate and 18 unverified certifiers are the same fact viewed
from two ends.

---

## SC-G0 · Withdrawn — recorded because it was measured, and was wrong

An earlier revision of this register carried a seventh, severe gap: a live mutant
(`return []  # MUTANT`) in `engine/enforcement_closure/contract.py` disabling a `UEC` law body,
with the gate reporting OPEN regardless. The observation was real; the interpretation was wrong.

**What was actually happening.** A concurrent per-law mutation campaign
(`mut_uec_local.py`, PID 47436, started 14:28) was running against the live repository. It
neutered one law body at a time, ran `engine/tests/unit/test_enforcement_closure.py`, and restored
the file after each mutant inside a `finally` block with a digest check. Two transient states were
caught: `certification_identity_is_complete` (UEC-L-13) at 14:38 and `every_declaration_is_consumed`
(UEC-L-07) at 14:42. The campaign's completed output:

```
total killed 13  SURVIVED 0
contract restored: True
$ git diff --stat engine/enforcement_closure/contract.py     # empty — restored
```

**No persistent mutant exists.** `SC-G0` is withdrawn. It is retained rather than deleted because
`ENFORCEMENT-CLOSURE-MATRIX.md` — an independent measurement present in the same working tree —
reached the same wrong conclusion from the same transient artefact, attributing it to `UEC-L-08`
and asserting it "survives." Two independent measurements misread one moving file. That is a fact
about measuring a live tree, and deleting it would leave the standing artifact uncorrected.

**What the episode establishes instead**, and it is the strongest positive result in this register:

- **13 of 13 `UEC` law mutants were KILLED by the test suite. 0 survived.** This is the only
  programme in the repository with mutation-kill evidence for its full law set.
- **Running a gate does not detect a neutered law body; only a test suite does.** Observed
  directly while a mutant was live:
  `python -m engine.enforcement_closure.gate --law UEC-L-13 --gate` **exited 0 and reported
  HOLDS**. This is reproducible by anyone repeating the mutation.

That second point is not a defect in `UEC` — it is the reason `UEC-L-05` requires a test per
detector and the reason `uec-gate.yml` carries a separate `uec-mutation` job. It is, however, the
empirical anchor for **SC-G1**: for the 18 certifiers no test names, the identical mutation would
survive unobserved, because the gate that would run them cannot see it. SC-G1 was previously an
inference from `UEC-L-05`'s own phrasing; it is now a measured property.

**Every figure in this register was re-executed on the restored tree** and is byte-identical to
the pre-campaign run: 48 certifiers, 18 unverified, 6 unreachable, 16 single-plane, 3 inert
declarations, 322 nodes, 371 edges, 40 self-loops, 172 governed artifacts, declaration digest
`cffb41b32c9eba5b`. The ratcheted helpers this register calls are distinct from the law functions
the campaign neutered, so no count was taken through a mutant.

---

## SC-G1 · Unverified certifiers

**18 of 48 certifiers (37.5%) are named by no test.** UEC-L-05's own phrasing: "a detector with
no test is a detector nobody has shown can fail." Declared ceiling 18, measured 18 — at ceiling,
so UEC-L-05 holds.

| # | Unverified certifier | Also single-plane | Also unreachable |
|---:|---|:-:|:-:|
| 1 | `00-MASTER/ACEE-000001/acee_engine.py` | | |
| 2 | `00-MASTER/MCOS-000001/mcos_engine.py` | | |
| 3 | `00-MASTER/P0-FINAL-CLOSURE-002/final_closure_engine.py` | YES | |
| 4 | `00-MASTER/P0-LIFECYCLE-CLOSURE-001/lifecycle_closure_engine.py` | YES | |
| 5 | `00-MASTER/UAKOS-PHASE-001A-R1/cert_engine.py` | YES | **YES** |
| 6 | `00-MASTER/UAKOS-PHASE-003R/phase3r_engine.py` | YES | **YES** |
| 7 | `00-MASTER/UCCEP-000000/uccep_engine.py` | | |
| 8 | `00-MASTER/UCDA-000001/ucda_engine.py` | YES | |
| 9 | `00-MASTER/UCEF-000001/ucef_engine.py` | | |
| 10 | `00-MASTER/UCOS-MXR-001/roadmap_engine.py` | | |
| 11 | `00-MASTER/UCOS-RFP-001/rfp_engine.py` | | |
| 12 | `00-MASTER/UCOS-USIS-WAVE0/freeze_c4_engine.py` | YES | **YES** |
| 13 | `00-MASTER/UEI-000001/uei_engine.py` | | |
| 14 | `00-MASTER/UER-000001/uer_engine.py` | | |
| 15 | `00-MASTER/UIS-001/uis_engine.py` | | |
| 16 | `00-MASTER/UMK-000001/umk_engine.py` | | |
| 17 | `00-MASTER/UPF-000001/upf_engine.py` | | |
| 18 | `00-MASTER/URRC-000001/urrc_engine.py` | | |

Three entries deserve naming individually, because they are the certifiers of certification:

- **`uccep_engine.py`** (#7) owns the aggregate constitutional certification cluster — 26 gates
  `G-01`…`G-26`, including `G-11` literally named *"Certification Gate"*. No test names it.
- **`acee_engine.py`** (#1) is the subject of the only recorded blocking failure in that cluster
  (`G-26`, `CK-ACEE`, `FAIL`). No test names it. The measured record in `uec-gate.yml`'s header
  is that a one-line `return True` inserted into `acee_engine.py`'s `compare()` flipped the gate
  from CLOSED to OPEN while all of its own `--check-*` self-guards still passed.
- **`cert_engine.py`** (#5) is a certification engine that is both untested **and** unreachable.

**Three certifiers are simultaneously unverified and unreachable** — nothing runs them and
nothing proves they could refuse:

```
00-MASTER/UAKOS-PHASE-001A-R1/cert_engine.py
00-MASTER/UAKOS-PHASE-003R/phase3r_engine.py
00-MASTER/UCOS-USIS-WAVE0/freeze_c4_engine.py
```

**SC-G1.1 — the consequence is measured, not inferred.** While a `UEC` law body was neutered by
the concurrent campaign described in `SC-G0`, this was observed directly:

```
$ python -m engine.enforcement_closure.gate --law UEC-L-13 --gate ; echo $?
0                                   # HOLDS · violations 0 — over a body replaced by `return []`
```

Running a gate does not detect a neutered detector. Only a test suite does, and for `UEC` that
suite killed 13 of 13 mutants. **For the 18 certifiers above, no such suite exists.** The identical
one-line neutering applied to any of them would leave its gate reporting OPEN and nothing else
would notice. The repository has already paid for this once: `uec-gate.yml`'s header records that
inserting `return True` into `compare()` in `uis_engine.py` and `acee_engine.py` flipped both gates
from CLOSED to OPEN while all nine of `UIS`'s own `--check-*` self-guards still passed, and that
zero test files reference either programme. Both engines remain on the list above.

---

## SC-G2 · Self-certifying objects

**38 of 48 certifiers write their verdict artifact into their own home directory. 31 have a
`CERTIFIC*`-named artifact in that same directory.**

| Certifier kind | Total | Self-certifying | Rate |
|---|---:|---:|---:|
| `GATE_ENGINE` (`00-MASTER/*/*_engine.py`) | 39 | **37** | 95% |
| `MODULE_GATE` (`engine/*/gate.py`) | 9 | **1** | 11% |

This violates `CF-C4` — *"Self-certification is void. A programme may not certify itself"*
(`00-MASTER/IMR-0000/20-VALIDATION-AND-CERTIFICATION-FRAMEWORK.md`) — and `CMG-000001` **LI.6**,
and `UUP-07` ("one certification chain", whose violation conditions explicitly include "a
self-certification"). The repository already records the contradiction:
`IMPLEMENTATION-REALITY-ASSESSMENT.md` measures 48 `00-MASTER/**` engines as "self-certifying
gates | **REQUIRES REMEDIATION**" and certification evidence as "self-issued".

Two sub-findings:

**SC-G2.1 — `CF-C4` is not executable.** No gate, workflow, Make target or verify stage
enforces it. There is no registration of `CF-C4` as a machine-checkable rule anywhere. The
prohibition exists only as prose in a corpus that the certification-architecture documents
(`CERTIFICATION-ARCHITECTURE-DETERMINATION-DRAFT.md`,
`CERTIFICATION-OWNERSHIP-RECONCILIATION-DETERMINATION.md`, `-FINDING.md`,
`PHASE-CERTIFICATION-GOVERNANCE-BINDING-DETERMINATION.md`) never cite.

**SC-G2.2 — the mechanism is write scope, not write mode.** The 37/39 vs 1/9 split is the same
defect `GATE-PURITY-DETERMINATION.md` records as D-3.0: an engine passes `--check-write-scope`
while rewriting the register its verdict compares against, because its home lies inside its own
permitted scope. The guard answers "did you write outside your boundary?" and never "were you
supposed to write at all?" D-3.1 is reproduced at this baseline: of 91 dirty working-tree
entries, tracked registers under `00-MASTER/UAIE-000001/`, `00-MASTER/UCOS-UGA-001/`,
`00-MASTER/UAKOS-CLOSURE-008/` and `00-BOOK/DATA/` are modified — gate runs mutated Repository
Truth. `GATE-PURITY-DETERMINATION.md` is classified `EVIDENCE` / `DETERMINATION ONLY` and no
workflow references it, so nothing enforces its findings.

**Not a defect, and distinguished deliberately:** `UEC-000001`'s self-coverage (§SC-G3.1) is
*declared*, *fail-closed* and *mutation-tested*. It is the one self-reference in the repository
that is an invariant rather than an omission.

---

## SC-G3 · Circular certification

| Cycle class | Count | Verdict |
|---|---:|---|
| Self-loops (certifier certifies its own home) | **40** | OPEN — 39 engines + UEC |
| Multi-node cycles in the governance graph | **0** | closed (Tarjan SCC over 322 nodes / 371 edges: all singletons) |
| Engine → engine invocation cycles | **0** | closed (17 naming edges, acyclic) |
| Cross-programme data-dependency cycles | **1** | OPEN |

**SC-G3.1 — the declared self-loop.** `UEC-000001` certifies itself. `self_coverage.artifacts`
names its own gate, declaration, workflow, Make target and verify stage; `UEC-L-09
self_coverage_is_a_fixed_point` refuses if any is missing, and the law is exercised by mutation
tests (`engine/tests/unit/test_enforcement_closure.py`) including "drop a self-coverage
artifact". Its own rationale: *"A closure mechanism outside its own closure is the defect, not
the exception to it."* This is recorded as a graph cycle because it is one — not as a defect.

**SC-G3.2 — the data-dependency cycle.**

```
00-MASTER/UAKOS-CLOSURE-008/assimilation_engine.py
   reads EVIDENCE-MANIFEST.json  (written under 00-MASTER/UKAP-001/)
00-MASTER/UKAP-001/corpus_engine.py
   reads assimilation.json       (written under 00-MASTER/UAKOS-CLOSURE-008/)
```

Each engine's input is the other's output. 52 cross-programme data-dependency edges were
measured; 51 form a DAG rooted at `closure.json`; this pair is the single cycle.

**SC-G3.3 — the historical ACEE↔UCCEP fixed point is mediated, and the residue is on disk.**
At this baseline `acee_engine.py` does not read `uccep.json` and `uccep_engine.py` does not name
ACEE, so no code cycle exists. The coupling now runs through `uccep-bindings.json` (which does
name ACEE) and is broken by an `independent_view` block keyed to 20+ constituent homes. But the
register still records the failing branch of that former fixed point:

```
00-MASTER/UCCEP-000000/uccep.json
  gate_exit: 1 · certification: "NOT-CERTIFIED" · blocking_failures: ["CK-ACEE"]
  G-26 "Autonomous Constitutional Engineering Gate" → FAIL (failed: CK-ACEE)
  G-11 "Certification Gate" (owner 00-CEP/CEP-005) → PASS-WITH-ADVISORY (advisory: CK-HEALTH)
```

Also recording a closed gate at HEAD: `00-MASTER/UCOS-RIB-001/rib.json`
(`BLUEPRINT NOT CERTIFIED — REPOSITORY MUST STOP`) and `00-MASTER/UCOS-UFEP-001/ufep.json`
(`blocking_failures: ["UFEP-VAL-14"]`).

**SC-G3.4 — circularity the repository has already named and left OPEN.**
`DISCOVERY-REGISTER.md` `DR-0377` / `GAP-R2-05`: *"`CMG-INV-10`'s verification condition is
circular — satisfied by the exit status of the validator that omits it. No located clause detects
a self-certifying verification condition."* Status OPEN. The named remedy,
`WP-001A-CONSTITUTIONAL-INTEGRATION-ANALYSIS.md` `CI-02` — *"No verification condition SHALL be
satisfiable by the exit status of the program that omits it"* — is recorded as
`RECORD AS CANDIDATE — HIGHEST LEVERAGE` and is **not implemented**. Related:
`CAA-INV-01` in `engine/uckp/alignment.py` is recorded as structurally unfalsifiable ("its
premise, subject and standard are one module; it would pass over an empty repository"), and
`UCOS-OMEGA-INFINITY-ABSOLUTE-END-STATE-DETERMINATION.md` records limit `U-02`:
"self-verification cannot establish its own soundness."

---

## SC-G4 · Missing certification paths

**SC-G4.1 — the requirement plane is disconnected from the gate plane.**

| Measurement | Result |
|---|---:|
| `RR-*` identifiers appearing in any workflow, `Makefile`, `verify.sh` or collected test | **0 / 549** |
| `REQ-nn` identifiers with a machine-checkable binding to a gate | **0 / 49** |
| requirements with `runtime_status: NO-RUNTIME-EVIDENCE` | **549 / 549** |
| requirements with no test tier, no validation evidence and no verification evidence | **254 / 549** |
| requirements at `certification_status: UNCERTIFIED` | **308 / 549** |
| full `constitution→requirement→implementation→test→evidence→certification` chain | **70 / 549** |

The 241 requirements marked `CERTIFIED-PROVISIONAL` are not uniformly evidenced:

- **78 of 241** carry no test tier at all
- **19 of 241** carry `verification_status: NOT-EVIDENCED`

`requirements.json` records `determination: ASSIMILATION-INCOMPLETE`, `baseline_permitted:
false`, and **all eight baseline conditions BC-01…BC-08 at `FAIL`** (BC-06: "0 of 314 implemented
requirements carry determinism evidence").

**SC-G4.2 — the `REQ-nn` identifier namespace is not injective.** `REQ-23` and `REQ-28` each
denote one subject in `UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md` and a different
subject in the test that names them. `test_req_28_extensibility.py` asserts
`Status: REQ-28 CERTIFIED` for context-kind extensibility, while the register's `REQ-28`
(192-document corpus registration) is an **OPEN GAP**. A reader following the identifier arrives
at a certification for a different requirement.

**SC-G4.3 — the certifier slot is vacant on every proof.** 103 certificate documents parsed
(77 programme + 26 root). **101 declare `AUTHORITY = NONE` or carry no authority line**; the 2
residual regex matches were inspected and name no certifier either. Measured: **103 of 103 have a
vacant certifier slot.** This is `CMG-000001` LI.7 operating as designed — a certification
issued against a vacant superior is `PROVISIONAL` — but it means no proof in the repository
names who certified it.

**SC-G4.4 — no gate re-verifies the proofs.**

| Population | Total | Referenced by any enforcement artifact |
|---|---:|---:|
| Programme certificates | 77 | **1** |
| Root certificates | 26 | **2** |

76 programme certificates and 24 root certificates — including
`10-FINAL-ARCHITECTURE-FREEZE-CERTIFICATE.md`, `03-FINAL-CERTIFICATION.md` and
`P0-ULTIMATE-CLOSURE-CERTIFICATION.md` — are certification claims that no gate can invalidate.

**SC-G4.5 — the certifier of all 549 requirements is enforced by a non-blocking gate.**
`requirement_engine.py` is governed, invoked from two planes and covered by a test. But
`closure009-gate.yml` carries the repository's only two `continue-on-error: true` steps, and both
sit on `--gate` and `--baseline-gate`. The requirement verdicts are measured in CI and not
enforced by it. Eleven of 32 workflows additionally contain a `|| true` construct.

**SC-G4.6 — the most affirmative certification verdict in the repository is covered by nothing.**
`00-BOOK/DATA/certification.json` records `verdict: "CERTIFIED"`, `domains_passed: 10 / 10`,
standard `UMB-017`. It is **not** registered in `artifacts.json` and **not** present in
`UEC-000001`'s governed inventory. It sits outside both closure mechanisms. `artifacts.json`
itself is likewise not registered in `artifacts.json`.

---

## SC-G5 · Unreachable certification nodes

**SC-G5.1 — 6 certifiers no plane invokes.** Declared ceiling 6, measured 6.

```
00-MASTER/UAKOS-CLOSURE-008/decision_engine.py
00-MASTER/UAKOS-CLOSURE-008/superiority_engine.py
00-MASTER/UAKOS-PHASE-001A-R1/cert_engine.py          ← also unverified
00-MASTER/UAKOS-PHASE-001B/provenance_engine.py
00-MASTER/UAKOS-PHASE-003R/phase3r_engine.py          ← also unverified
00-MASTER/UCOS-USIS-WAVE0/freeze_c4_engine.py         ← also unverified
```

All six are governed by `UEC-000001` — deleting one fails the build — but no workflow, Make
target or verify stage can cause any of them to run. Three of the six are still *depended upon*
in the data plane: `provenance_engine.py` writes `provenance.json`, which
`assimilation_engine.py`, `cert_engine.py`, `phase3r_engine.py` and `corpus_engine.py` all read.
An unreachable engine's stale output is live input elsewhere.

**SC-G5.2 — 51 of 54 governed gate targets are unreachable from CI.**

| Invocation source | `MAKE_GATE_TARGET` count |
|---|---:|
| invoked by a workflow | **3** (`constitution-gate`, `convergence-gate`, `freeze-gate` — all from `ufc-gate.yml`) |
| invoked by `verify.sh` | **0** |
| reachable only by a human typing `make` | **51** |

`UEC-L-06` requires two independent invocation planes so that deleting one leaves a signal. The
second plane exists and is governed; for 51 of 54 targets it is not exercised by any automated
run. 10 certifiers are reachable from exactly one plane and 6 from none:

| Planes reachable from | Certifiers |
|---:|---:|
| 3 | 5 |
| 2 | 27 |
| 1 | 10 |
| 0 | 6 |

**SC-G5.3 — 3 inert declarations.** Declared ceiling 3, measured 3. No module loads them, so
every field in them is unenforced:

```
00-MASTER/UCOS-CEU-001/ceu-declaration.json
00-MASTER/UCOS-URR-001/urr-declaration.json
00-MASTER/UCXI-000001/ucxi-declaration.json
```

**SC-G5.4 — dormant certification engines outside the enforcement plane.**
`engine/universal_certification` has no consumer outside its own tests, and
`platform/universal_assurance/certification.py` has no consumer anywhere in the repository
(recorded in `CERTIFICATION-OWNERSHIP-RECONCILIATION-DETERMINATION.md` §3 and
`PHASE-UNIVERSAL-ASSURANCE-RELATIONSHIP-DETERMINATION.md` §4). Of the 12 certification surfaces
registered in `00-BOOK/DATA/constitutional-authority-alignment.json`, the formal Certification
Layer is recorded as *"not referenced by `Makefile` or `verify.sh` anywhere"* — two populations
that, in the repository's own words, "have essentially never spoken to each other."

---

## SC-G6 · Uncertified roots

Every chain in the graph terminates. **No chain terminates in a certified authority.** Three
roots, each uncertified for a different reason:

| Root | Terminus kind | Measured evidence |
|---|---|---|
| `UEC-000001` | **self-loop** | Certifies itself via `self_coverage` + UEC-L-09. Declared, fail-closed, mutation-tested. The trust anchor of the enforcement plane is its own certifier. |
| `REG-AUTO-001` | **unregistered anchor** | **0 of 1,597** registered artifacts lie under `00-BOOK/tools/`. The registration mechanism is not registered under itself. Recorded as discovery `D-09`: *"trust anchor → REG-AUTO-001, itself unregistered."* |
| `T1` ratification authority | **VACANT** | `VAC-01` / `DR-RAT-11` / `UCCEP-F-004`. `00-MASTER/P0-FINAL-CLOSURE-002/UCOS-UNCONDITIONAL-CERTIFICATION.json`: `outcome_from_inside_the_corpus: "PROHIBITED"`, `maximum_attainable_in_corpus_state: "CERTIFIED-PROVISIONAL"`. Three located instruments independently record that no in-corpus authority is competent to ratify (`UCAF-RC-01/02/03`). |

The `T1` vacancy is not a defect in the same sense as SC-G1…SC-G5. The repository determines it
is unresolvable from inside the corpus: the exact closing condition on record is *"an
out-of-corpus constituent ratification act that identifies and ratifies the artifact occupying
Tier T1, followed by `CMG-000001` XVII.4(d) re-run of authority resolution."* Everything else in
this register is in-corpus and therefore in principle measurable to zero; SC-G6's third row is
not. `UCOS-OMEGA-INFINITY-ABSOLUTE-END-STATE-DETERMINATION.md` §15 states the resulting
position: the corpus **can** self-certify (compute an outcome) and **cannot** self-accept (confer
standing by it).

**Consequence for the graph.** Since `T1` is vacant and `CF-C4` is not executable, the practical
certifier of the 38 self-certifying objects is the object itself, and the practical certifier of
the certifiers is `UEC-000001`, whose own certifier is `UEC-000001`. The chain
`Requirement → Certifier → Certifier-of-Certifier → Closure Proof → Certification Gate`
closes on itself at the third position and terminates in a vacancy at the fourth.

---

## 7 · What is measured CLOSED

Recorded so the register is not read as uniformly negative. These are real, executed results,
not assertions:

| Property | Measured |
|---|---|
| `UEC-000001` meta-gate verdict | **OPEN** — exit 0, 13 of 13 laws hold, 0 blocking refusals |
| `UEC-000001` law falsifiability | **13 of 13 law mutants KILLED, 0 survived** (per-law neutering campaign, `SC-G0`). The only full-law-set mutation evidence in the repository. |
| Enforcement inventory drift | **0** — 172 governed = 172 located; UEC-L-02 and UEC-L-03 hold |
| Discovery vacuity | **0** — every rule meets its floor; no floor is zero (UEC-L-01) |
| Plane overlap | **0** — no enforcement artifact falls inside the registration boundary (UEC-L-10) |
| Ratchet slack | **0** — every ratcheted measurement equals its ceiling exactly (UEC-L-11) |
| Withdrawals | **0** used of a cap of 3, all reasoned (UEC-L-12) |
| Declarations with no certification identity | **0** (UEC-L-08) |
| Multi-node governance cycles | **0** across 322 nodes / 371 edges |
| Engine → engine invocation cycles | **0** across 17 edges |
| Verifiers referenced by workflows that are missing from disk | **0 of 32** |
| `UAKOS-CLOSURE-002` concept closure | 549 concepts, `gap_total: 0`, `determination: CLOSED` |

---

## 8 · Prior art — what already exists, and what does not

The mechanism required to close SC-G2 already exists and is proven, in a different domain.
`UEC-L-09` is a complete self-coverage law: a declaration block, a fail-closed fixed-point
predicate (`engine/enforcement_closure/contract.py`), a dedicated CI job
(`uec-gate.yml :: uec-self-coverage`), a Makefile guard, and mutation tests. It closes
self-coverage for **enforcement closure**.

For **certification** there is no equivalent. Measured absences:

- No file in the repository is named `*SELF-COVERAGE*` or `*SELF-CERTIFICATION*` prior to this
  measurement.
- No gate, workflow, Make target, verify stage or test enforces `CF-C4`.
- `CI-02` — the named highest-leverage candidate invariant that would detect a self-certifying
  verification condition — is recorded as a candidate only, explicitly not authorized.
- `R-6 Trust-Anchor Self-Coverage`, the generalization of `D-09`
  (`UCOS-OMEGA-INFINITY-BLOCKER-ERADICATION-AND-IMPLEMENTATION-READINESS-DETERMINATION.md` §485),
  is sequenced but recorded as **not authorized for implementation**.

None of the above was implemented, authorized or advanced by this measurement.

---

## 9 · Reproduction

```bash
git rev-parse --short HEAD                             # 446f8a0f
git status --porcelain | wc -l                          # 91 at start, 95 at end
python -m engine.enforcement_closure.gate --json        # exit 0 · OPEN · 13/13 laws
python -m engine.enforcement_closure.gate --inventory    # discovered surface; writes nothing

# SC-G0 / SC-G1.1 — a gate does not detect its own neutered detector
git diff --stat engine/enforcement_closure/contract.py   # empty at end of measurement (restored)
```

Counts derive from `00-MASTER/UEC-000001/uec-declaration.json`,
`00-MASTER/UAKOS-CLOSURE-009/requirements.json` (seal `b9d62642…`),
`00-MASTER/UCCEP-000000/uccep.json`, `00-BOOK/DATA/artifacts.json`,
`00-BOOK/DATA/certification.json`, `Makefile`, `verify.sh`, `.github/workflows/*.yml`, and the
six `UEC-R-0n` discovery rules. Populations were located with the repository's own discovery
module rather than a second inventory, so this register cannot disagree with `UEC-000001` about
what exists.

---

## 10 · Limits of this measurement

1. **The working tree was DIRTY (91 entries at start, 95 at end).** This register describes the
   working tree, not commit `446f8a0f`. Of the 4 new untracked files, 2 are this register and its
   graph; `ENFORCEMENT-CLOSURE-MATRIX.md` and `ENFORCEMENT-CLOSURE-GAPS.md` appeared during the
   session and were **not written by this mission**. Some dirty entries are registers that earlier
   gate runs mutated — the `GATE-PURITY` D-3.1 finding, reproduced rather than corrected.
2. **The tree mutated during measurement, and the first reading of that was wrong** (`SC-G0`).
   A concurrent campaign neutered `UEC` law bodies one at a time and restored the file with a
   digest check. Every figure here was re-executed on the restored tree and is byte-identical. The
   ratcheted helpers this register calls are distinct from the law functions that were neutered,
   verified by reading `git diff engine/enforcement_closure/contract.py` while a mutant was live.
3. **`proves-can-refuse` is name-binding, not falsifiability.** SC-G1 measures that no test names
   the engine, which is what UEC-L-05 measures. A certifier absent from that list has a test that
   *names* it. Mutation-kill evidence exists for exactly one programme — `UEC-000001`, 13 of 13 —
   so "covered" is weaker than "shown to be able to fail" for 47 of 48 certifiers. `SC-G1.1`
   records the direct observation that makes this concrete.
4. **SC-G2 is a structural test.** It measures that the engine writes into the directory whose
   artifacts it judges. It does not prove a specific verdict was satisfied by that write.
5. **SC-G4.4 is a reference test.** It measures that no enforcement artifact mentions the
   certificate by filename. A gate could in principle re-verify a claim without naming the
   document; none was found doing so.
6. **The `REQ-nn` layer was read from prose** and is internally inconsistent (the traceability
   matrix declares 37 requirements and tallies 40). The master index supersedes it. Neither is
   machine-readable.
7. **`gap_classes[*].members` in `requirements.json` is capped at 400.** Counts are
   authoritative; member lists are truncated for `RG-B01` (406), `RG-E01` (549), `RG-E02` (471),
   `RG-E03` (416).
8. **This register is outside the closure it measures.** It is a root-level `.md` inside the
   `REG-AUTO-001` registration boundary and is not registered. With its companion it adds 2 to
   the unregistered-eligible population `REQ-28` tracks. Registering it would mutate Repository
   Truth, which this mission does not authorize.

---

## 11 · No repair performed

No gap above was closed, narrowed, reclassified, referred or deferred. No declaration was edited.
No ratchet ceiling was moved. No withdrawal was added. No gate, test, workflow, Make target or
verify stage was created or modified. No register was re-rendered. No source file was reverted or
restored — the `contract.py` restoration recorded in `SC-G0` was performed by the concurrent
campaign's own `finally` block, not by this mission.

The only files written by this mission are `SELF-COVERAGE-GRAPH.md` and `SELF-COVERAGE-GAPS.md`.
`ENFORCEMENT-CLOSURE-MATRIX.md` and `ENFORCEMENT-CLOSURE-GAPS.md`, which appeared in the working
tree during the session, were not written by this mission; `SC-G0` records where this measurement
contradicts the former.

*END — SELF-COVERAGE-GAPS · AUTHORITY = NONE (DERIVED TRUTH) · MEASUREMENT ONLY · REPAIRS NOTHING.*
