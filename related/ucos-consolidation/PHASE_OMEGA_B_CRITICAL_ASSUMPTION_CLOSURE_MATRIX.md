# UCOS Ω∞ — PHASE Ω∞-B, DELIVERABLE 2
## Critical Assumption Closure Matrix

> ## ⚠ EVIDENCE PROVENANCE AND CURRENT REPRODUCIBILITY — READ FIRST
>
> **The subject tree measured by this phase, `engine/omega_governance/`, is NO LONGER PRESENT in the
> working directory.** This note is recorded rather than the claims below being quietly left standing,
> because a claim that nothing checks is the precise defect class this phase was convened to document.
>
> **Timeline, from filesystem timestamps:**
>
> | Time (2026-08-29) | Event |
> |---|---|
> | 11:23–11:26 | `engine/omega_governance/**` last modified (predates this phase) |
> | 12:01–12:08 | probes `b01`, `b02_b05`, `b03_b04`, `b06` executed; outputs recorded |
> | 12:48:23 | probe `b07` executed; §H9 confirmed the tree present — `state.py`, `authority.py`, and the `reference/` and `temporal/` subpackages |
> | **12:50:02** | **`engine/` directory mtime changes — the subpackage is removed** |
> | 12:51:56 | absence detected during final verification |
>
> **What this does and does not affect.**
>
> - **The evidence artifacts survive.** All probe sources and their recorded outputs are preserved in
>   `00-MASTER/UCOS-OMEGA-B-001/probes/`. Every measurement cited in this document was taken against the
>   tree while it existed, and the recorded outputs are the evidence of record.
> - **The reproduction instructions in this document no longer execute.** They now fail with
>   `ModuleNotFoundError: No module named 'engine.omega_governance'`. Where this document says a probe
>   was "re-executed against current repository state" and found byte-identical, that was true when
>   written and is **not verifiable now**.
> - **The tree is not recoverable from version control.** It was never committed and never stashed
>   (`git status` reported it untracked; `git log --all --diff-filter=A` finds no such path).
> - **Nothing in this phase removed it.** Ω∞-B writes were confined to
>   `00-MASTER/UCOS-OMEGA-B-001/probes/` and the root `PHASE_OMEGA_B_*.md` deliverables. No Ω∞-B
>   operation targeted `engine/`.
>
> **Consequence for this document's standing.** Its classifications remain the honest record of what was
> measured. They are **no longer independently re-verifiable** until the tree is restored from a backup or
> another working copy. Restoring it is an owner decision and is not taken here.


**AUTHORITY = NONE (DERIVED TRUTH).** No certification, no seal, no ratchet advancement, no closure
declaration, no readiness claim. No active governance, validation or certification process is modified.

**WHAT THIS DOCUMENT ENFORCES.** Ω∞-B mandatory constraint 6: **no assumption may be marked resolved
without evidence.** This matrix is the register in which that constraint is discharged. It states, for
every assumption in the Ω∞-A register, exactly what evidence exists and exactly what the evidence
licenses.

**THE FOUR CLOSURE STATES, and the distinction the third one draws is the whole point of this
document:**

| State | Meaning | What it licenses |
|---|---|---|
| **CLOSED (MEASURED)** | The assumption is absent from the subject tree, and a probe observed its absence or a hostile case exercising it | The assumption may be treated as removed **from that tree** |
| **REMOVABILITY ESTABLISHED** | A prototype over shipped types demonstrated the resolution works. **The assumption is still present in the tree** | The assumption may be classified as implementation-induced. **It may NOT be treated as resolved** |
| **OPEN** | Present, and no resolution has been demonstrated | Nothing |
| **NOT CLOSABLE** | Fundamental. Removing it would require abandoning the idea of a governance record | It must be *stated*, not fixed |

**Ω∞-A's own warning, which this matrix takes as binding.** Ω∞-A Deliverable 1 opens by recording that
the audit's first target was code written in the same session *specifically to eliminate hardcoded
assumptions*, and that it found five — none an enum, none catchable by review. It concludes: *"assumption
discovery by inspection has a demonstrated false-negative rate above zero, so every CLOSED entry below
should be read as 'closed against the tests that exist', not 'closed'."*

**Ω∞-B confirms that warning empirically.** Six assumptions Ω∞-A did not record were found by probing
(B-N-03 through B-N-08 and B-N-11 in the Blocker Resolution Matrix), including one **silent corruption**
in a module Ω∞-A had assessed as closed. Every CLOSED row below therefore carries the same qualifier.

**EVIDENCE BASE.** `00-MASTER/UCOS-OMEGA-B-001/probes/` — five probes, all re-executed against current
repository state; four byte-identical to their stored output, one (`b01`) identical in every structural
count with 6 timing lines differing.

---

## 1. SUMMARY

| Closure state | Count | IDs |
|---|---|---|
| **CLOSED (MEASURED)** in the Phase 2 tree, legacy untouched | 9 | A-01, A-02, A-03, A-04, A-05, A-07, A-08, A-12, A-13 |
| **REMOVABILITY ESTABLISHED, still present** | 8 | A-09, A-10, A-11, A-15, A-16(tractability), A-20, A-21, A-24 |
| **PARTIALLY: removability established for one half, fundamental for the other** | 3 | A-14, A-18, A-22 |
| **OPEN, removability not demonstrated in Ω∞-B** | 3 | A-19, A-23, A-27 |
| **NOT CLOSABLE (FUNDAMENTAL)** | 2 | A-06, A-17 |
| **ACCEPTED (correctly closed by design)** | 1 | A-26 |
| **OUT OF SCOPE BY DIRECTIVE** | 1 | A-25 |

**Total: 27 assumptions.** Zero are marked resolved. **Eight are marked removability-established, and
that is deliberately not the same claim.**

---

## 2. THE MATRIX

### 2.1 Temporal assumptions

| ID | Assumption | Ω∞-A class | Ω∞-B evidence | Closure state |
|---|---|---|---|---|
| **A-01** | Wall-clock time is available and authoritative | CRITICAL (legacy) / CLOSED in Phase 2 tree | **MEASURED:** 0 `datetime`/`time` imports in `engine/omega_governance/**`. A clock with **no ordering at all** registered and passed `assert_provider`; a non-numeric clock registered; a **reversed-arrow** clock registered. **AND a time-bounded governance guard was written with no wall clock** — it takes a `TemporalCoordinate` and refuses (rule Ω²-C-04) when the coordinate is not comparable with the window | **CLOSED (MEASURED)** in the Phase 2 tree. 11 legacy files remain, out of scope |
| **A-02** | Every pair of events has an agreed order | CRITICAL / CLOSED in Phase 2 tree | **MEASURED:** two `VectorClock` coordinates compare `CONCURRENT`; branch 0 vs branch 1 compares `INCOMPARABLE`, never `CONCURRENT`; `TemporalCoordinate` has **no `<` operator**. **A-02 RE-ENTERED ONCE DURING Ω∞-B AND WAS CAUGHT:** the first draft of the time-bounded guard tested `relation.ordered`, which is true for both `BEFORE` and `AFTER`, and therefore accepted an out-of-window coordinate. The repair resolves the precedence relation **by declared name** through the registry | **CLOSED (MEASURED)**, with a recorded warning: **the assumption re-enters through convenience, not through design.** Any guard, reporter or projection that tests "is it ordered" rather than "is it *this* relation" reinstates it |
| **A-03** | Gregorian rendering is identity | REPLACEABLE / CLOSED | **MEASURED:** `assert_presentation_only` holds under both encodings — rendering leaves equality and fingerprint unchanged. Gregorian arithmetic confined to one deletable class implemented without `datetime` | **CLOSED (MEASURED)** |

### 2.2 Measurement, identity and representation

| ID | Assumption | Ω∞-A class | Ω∞-B evidence | Closure state |
|---|---|---|---|---|
| **A-04** | Measurement is numeric | CRITICAL / CLOSED | **MEASURED:** a symbolic coordinate `('EPOCH-ALPHA',)` compares, encodes and fingerprints; `_shape_of` gives symbols their own shape class so totality is not demanded against integers; cross-shape comparison answers `INCOMPARABLE`. **NEW RESIDUAL FOUND:** a bare `str` position is silently exploded into per-character components — `'EPOCH'` → `('E','P','O','C','H')` — accepted **without refusal**, and it **fingerprints**, entering a governance record as a legitimate position. The neighbouring case (empty position) is correctly refused | **CLOSED (MEASURED) for the assumption; a NEW OPEN defect inside the closure.** B-N-06. Removable by one `isinstance` refusal |
| **A-05** | JSON is the representation; SHA-256 is the identity | CRITICAL (legacy) / CLOSED | **MEASURED:** in `engine/omega_governance/**` both are confined to `reference/encoding.py` as 2 of 4 shipped providers; the full pipeline ran under `TagLengthValueCodec` + `PolynomialIdentity`. `Encoding` is a required argument with **no default**, so there is nothing to fall back to | **CLOSED (MEASURED)** in the Phase 2 tree. 404 `json` + 56 `hashlib` legacy sites remain, out of scope. **The no-default discipline is the mechanism that makes this a measurement rather than an intention, and it should be treated as a standard rather than a detail** |
| **A-06** | Everything governed is reducible to bytes | **FUNDAMENTAL** | **MEASURED, and the open action is now shown AVAILABLE:** the proxy relationship for a non-encodable artifact **is declarable** as a lossy, authority-bearing, non-computable `Transformation`. **Ω∞-A falsification criterion 3 — the one it ranked MOST LIKELY to fire — does NOT fire.** No sixth mechanism is needed for physical reference | **NOT CLOSABLE (FUNDAMENTAL)**, and its mitigation is now measured as **mechanically available and UNTAKEN** — no shipped declaration uses it. **Residual: `lossy: bool` states *that* fidelity is lost, never *how much*** |

### 2.3 Governance and certification

| ID | Assumption | Ω∞-A class | Ω∞-B evidence | Closure state |
|---|---|---|---|---|
| **A-07** | A governance state is a scalar | CRITICAL / CLOSED (legacy untouched) | **MEASURED:** six orthogonal axes; `GovernanceStatus` enforces one position per axis; `separation_report` discharges all five required combinations by execution. A 7th axis registered at runtime with zero source edits | **CLOSED (MEASURED)** in the Phase 2 tree. Legacy `DISPOSITIONS` at 8 sites untouched, as required |
| **A-08** | Authority may resolve to nothing | CRITICAL / CLOSED | **MEASURED:** an 8th authority tier (`INTERCIVILIZATION`, rank 8) resolved `CIV-COUNCIL` by rule `Ω²-A-08` — the exact case that raised `KeyError` before Ω∞-A's fix. The fallback tier is constructed from a constant, unregisterable and unremovable | **CLOSED (MEASURED)** |
| **A-09** | A justification is any non-empty string | **BLOCKING**, open | **MEASURED:** `Ω²-S-12` accepted `'x'`, `'.'`, `'0'`, `'no'`, `'TODO'`, `'  see ticket  '`. `Ω²-S-22` accepted a reason naming one approver where three were required. **REMOVABILITY MEASURED BY PROTOTYPE:** all four strings refused by a `JustificationGuard` validating a declared 3-field schema; a complete justification permitted | **REMOVABILITY ESTABLISHED, STILL PRESENT.** The tree still accepts `'x'` |
| **A-10** | Two guard kinds suffice | **BLOCKING**, open | **MEASURED:** exactly 2 guard-bearing fields; 7 of 8 governance capabilities REFUSED, 8th PARTIAL; `set()` destroys vote multiplicity. **REMOVABILITY MEASURED BY PROTOTYPE:** 10 of 10 capabilities expressed as registered guards, each refusing for its own stated reason, zero edits to `engine/`. **Ω∞-A falsification criterion 1 did not fire** | **REMOVABILITY ESTABLISHED, STILL PRESENT** |
| **A-11** | Certification has a fixed input set | **UNKNOWN (unbuilt)**, designated BLOCKING | **RECLASSIFIED BY MEASUREMENT.** Not unbuilt: the precondition set **exists today** as the frozen `blocked_by` tuple of four on `Ω²-S-22`/`Ω²-S-26` in `INITIAL_TRANSITIONS`. Three extension attempts refused; a 7th axis leaves the new concern **registrable and non-binding** — the artifact still certifies. **REMOVABILITY MEASURED BY PROTOTYPE:** the same registration bound immediately against a registry-driven decision and named itself in the explanation | **REMOVABILITY ESTABLISHED, STILL PRESENT. Ω∞-A's UNKNOWN classification is superseded by measurement** |

### 2.4 Discovery, storage, execution, repository

| ID | Assumption | Ω∞-A class | Ω∞-B evidence | Closure state |
|---|---|---|---|---|
| **A-12** | Storage is a local filesystem | CRITICAL (legacy) / CLOSED **by absence** | **MEASURED:** 0 `os`/`pathlib`/`shutil`/`glob` imports in `engine/omega_governance/**`; every record reduces to primitives via `as_record()`. **NOT TESTED IN Ω∞-B:** no `StorageProvider` exists, so storage-*capability* could not be probed — only storage-*neutrality*, which is what "closed by absence" means | **CLOSED (MEASURED) as neutrality. G-05 (storage capability) remains OPEN and was not tested — recorded as ARGUED, not measured** |
| **A-13** | Discovery is `git ls-files`; the world is a repository | CRITICAL (legacy) / addressed in Phase 1 | **MEASURED:** Phase 1's `GitDiscoveryProvider` is one provider declaring `TRACKED_CONTENT`; the filesystem provider declares neither `TRACKED_CONTENT` nor `VERSIONED_CONTENT`. 42 legacy git-invoking files remain | **CLOSED (MEASURED) for the discovery layer.** Consumers out of scope by directive |
| **A-14** | The governance vocabulary is a single in-process object | **BLOCKING**, open — "highest-severity" | **MEASURED:** 0 of 7 registries expose `digest`/`declared_by`/`diverges_from`; divergent verdict on one record (A=INVALID, B=VALID, identical fingerprint) with neither able to detect the other; the conflict check is intra-process only; a merge raises on the first conflict. **DETECTION: REMOVABILITY MEASURED BY PROTOTYPE** — digest derived from `report()` + `Encoding`; 3 divergence kinds reported with both authorities. **AGREEMENT: MEASURED FUNDAMENTAL** — two registries with **byte-identical digests** attaching different meanings to `magnitude`, both VALID | **SPLIT. Detection: REMOVABILITY ESTABLISHED, STILL PRESENT. Agreement: NOT CLOSABLE (= C-04). Ω∞-A falsification criterion 5 FIRED, exactly as written** |

### 2.5 Scale, finiteness, proof method

| ID | Assumption | Ω∞-A class | Ω∞-B evidence | Closure state |
|---|---|---|---|---|
| **A-15** | The governed population is finite and materialisable | **CRITICAL**, open | **MEASURED:** all six reporters are single-pass full materialisations. **REMOVABILITY MEASURED BY PROTOTYPE:** three disjoint shard censuses merged **equal** the census of the union, in any merge order, identity `{}`; a one-artifact-at-a-time stream reproduces it exactly. **NEW RESIDUAL:** `fallback_density` is a **ratio**, and a ratio is not a monoid — it must be carried as `(numerator, denominator)`. `assert_total` and `separation_report` are likewise not additive in the same way | **REMOVABILITY ESTABLISHED for `census`, STILL PRESENT. B-N-08 is a new OPEN sub-finding** |
| **A-16** | Invariants can be proven by exhaustive enumeration | **CRITICAL**, open — "most important" | **MEASURED:** Θ(3ⁿ), all four Ω∞-A points reproduced; 13 axes = 13.5 s, 25 ≈ 55 days. **AND the measurement Ω∞-A did not take:** a registered axis adds **exactly zero** distinguishable cases, so redundancy reaches **9,565,938×** at 20 axes. **REMOVABILITY MEASURED BY PROTOTYPE:** structural proof holds at 40 axes (1.5 × 10¹⁹ vectors) in ~66 µs; exhaustive **DECLINES** with a stated reason. **AND: `invariants.py` is ABSENT — 9 of the 11 modules `__init__.py`'s own table lists do not exist** | **SPLIT. Tractability: REMOVABILITY ESTABLISHED. Existence: OPEN and larger — six of seven designed invariants have no proof of any kind. Ω∞-A's framing ("the proof expires") is superseded: the proof has never run** |
| **A-17** | Registration is free | **FUNDAMENTAL** — and a correction to Rule 9 | **MEASURED AGAIN, and its compounding effect measured for the first time:** registering a 7th axis makes `assert_total` raise and name the gap **while the same registration leaves certification unaffected**. So one act simultaneously (a) correctly reports every prior record as incomplete and (b) silently certifies new artifacts as if the concern did not exist | **NOT CLOSABLE (FUNDAMENTAL), correctly handled — and its pairing with A-11 is the sharpest available statement of the certification problem. The architecture is more rigorous about the past than the present** |

### 2.6 Human-centric, language, semantic

| ID | Assumption | Ω∞-A class | Ω∞-B evidence | Closure state |
|---|---|---|---|---|
| **A-18** | Meaning is carried by English prose | **HIDDEN**, open | **MEASURED:** `MASS` = kilograms on A, pounds on B — both VALID. Identical digests, different meaning for `magnitude` — both VALID. **NEW:** a digest **cannot see a registered predicate** (`Invariant.predicate` is a `Callable` with no content digest), so two registries can agree on every digest and execute different checks — and the predicate is precisely what gives a `kind` mechanical meaning | **PARTIALLY: the countability half is removable (ratchet `unexecutable_invariants()`); the meaning half is NOT CLOSABLE (= C-04). B-N-07 is a new OPEN sub-finding** |
| **A-19** | An unexecutable invariant is still an invariant | EXPANDABLE, open | **NOT TESTED FOR REMOVABILITY IN Ω∞-B.** Confirmed present and *exercised*: the prototype justification domain declared `Ω∞-B-J-02` deliberately unexecutable, and it was **counted** rather than hidden. The recommended CONVERGENT ratchet on `unexecutable_invariants()` is **still not done** | **OPEN.** Mitigation is a ratchet, not a fix — Ω∞-A says so, and Ω∞-B does not improve on it |
| **A-20** | Rule identifiers occupy one flat global namespace | REPLACEABLE, open | **MEASURED (structural):** `Ω²-S-01`…`Ω²-S-36`, `Ω²-A-01`…`Ω²-A-08`, `Ω²-C-01`…`Ω²-C-05`, `Ω²-F-00`, `Ω∞-D-*`, `Ω∞-X-*` all unqualified. `TransitionGraph.register` refuses a duplicate **within one graph**; nothing prevents two deployments minting `Ω²-S-37` for different edges. **A related instance measured:** an `OrderingRegistry` constructed with no strategies reserves five ordering **names** unconditionally | **REMOVABILITY ESTABLISHED by argument from A-14 maximal `(authority, identifier)`. NOT separately prototyped. Requires a record backfill: prior records cite unqualified ids and cannot be auto-qualified without inventing an authority** |

### 2.7 Relationship, causality, truth

| ID | Assumption | Ω∞-A class | Ω∞-B evidence | Closure state |
|---|---|---|---|---|
| **A-21** | Transformations are binary and directed | **BLOCKING**, open | **MEASURED:** all four assumptions present and structural; n-ary declaration refused with `AttributeError`; the composite workaround is a schema modification **and is opaque**. **AND the consequence is worse than Ω∞-A recorded:** `path('SPACE','VELOCITY')` returns a **COMPLETE route** with two of three inputs absent, so `apply()` would succeed on insufficient inputs — conjunction is indistinguishable from alternative. **AND: exactly one authority may relate any two domains.** **REMOVABILITY MEASURED BY PROTOTYPE:** hyperedge keyed on a source set reports `SPACE` alone UNSATISFIABLE with a named shortfall, and admits two authorities for one source set | **REMOVABILITY ESTABLISHED, STILL PRESENT. Reclassified from an expressiveness gap to a CORRECTNESS DEFECT producing wrong answers today** |
| **A-22** | A relation has exactly three semantic properties | EXPANDABLE, open | **MEASURED:** a degree lives only in the relation **name** (bucketing works, does not scale) or in free text; a genuinely stochastic strategy is refused by antisymmetry. **A-22 CONFIRMED: the `QuantumOrdering` pass was a FIT, not generality.** **NEW:** `Comparison` carries `decided` and `ordered` but **not `coincident`**, so a record consumer must string-match the relation name — the name-based reasoning `assert_consistent` exists to avoid | **PARTIALLY: `Relation.properties` and `Comparison.coincident` are removable; a degree any consumer can interpret without prior agreement is NOT CLOSABLE (= C-04)** |
| **A-23** | Truth is binary at the record level | EXPANDABLE, open | **NOT TESTED FOR REMOVABILITY IN Ω∞-B.** Confirmed present: `Invariant.check() -> bool \| None`; `Schema.validate() -> tuple[str, ...]`. Its resolution **depends on A-22's** `properties` mapping, so it cannot be assessed independently | **OPEN, and dependent on A-22** |
| **A-24** | An append-only register imposes a total order | **BLOCKING**, open | **MEASURED:** `registry.py` **absent**. **REMOVABILITY MEASURED BY PROTOTYPE:** a Merkle DAG admitted a concurrent sibling pair, a third entry naming both predecessors, `verify()` ok, **tampering detected after mutation** (so tamper evidence is unchanged by the DAG shape), and total order emitted as a record with `kind=PROJECTION`, `asserted_by_register=False` | **REMOVABILITY ESTABLISHED AT ZERO COST, STILL UNBUILT — which is the whole opportunity. Ω∞-A's cost-of-delay claim is confirmed: nothing was rewritten to obtain this result** |
| **A-27** | Totality is a property of a comparison, not of a value domain | HIDDEN, **partially closed** | **MEASURED:** the applied half holds — `_shape_of` enforces totality within a shape class and antisymmetry everywhere. **The unapplied half is confirmed still open:** `Ordering.total` remains a **bare boolean naming no precondition**, so a consumer requiring a total order trusts a label that holds only within a shape class. **AND a second instance of the same class of defect was found: `assert_consistent` verifies 3 of the properties an ordering can have — relation membership, within-shape totality, antisymmetry — and NEVER CHECKS TRANSITIVITY.** A repaired cyclic ordering violating transitivity **passes**. A written check finds 6 violations in it and 0 in the shipped strategy | **OPEN (partially closed). B-N-05 is a new OPEN sub-finding of the same class. The removable check is SAMPLED (O(n³) in the sample), so it must be labelled as sampled or it becomes G-09's silent-expiry failure in a new location** |

### 2.8 Closed-world inventory

| ID | Assumption | Ω∞-A class | Ω∞-B evidence | Closure state |
|---|---|---|---|---|
| **A-25** | 264 enumerations, 1,372 members, 7 trees | CRITICAL (aggregate) | Not re-measured. Ω∞-A Deliverable 4 triages: **~60 are true invariants and should stay closed**; the recommendation is that **every closed list carry a written argument for its closedness**, and the absence of the argument is the finding | **OUT OF SCOPE BY DIRECTIVE.** Phase 2's constraint is adapters, not rewrites |
| **A-26** | The Phase 2 tree's own residual closed list (`REQUIRED_STATE_NAMES`, 13 items) | Accepted | Confirmed present and confirmed **not a vocabulary**: nothing resolves through it and nothing is validated against it. It is a directive-conformance assertion. **And Ω∞-B recommends generalising it** — the same discipline applied to module presence would have caught B-N-01 (9 of 11 documented modules absent) | **ACCEPTED (correctly closed by design), and proposed as a standard rather than an exception** |

---

## 3. WHAT THE EVIDENCE DOES NOT LICENSE

**Stated explicitly, because Ω∞-B constraint 6 is a constraint on claims, not only on findings.**

| Claim that could be mistakenly drawn | Why the evidence does not support it |
|---|---|
| "A-09, A-10, A-11, A-15, A-21, A-24 are resolved" | **No.** Each is REMOVABILITY ESTABLISHED. The tree still accepts `'x'` as a justification, still has two guard kinds, still enumerates four certification preconditions, still materialises every census, still returns a complete route from insufficient inputs, and still has no register at all |
| "The prototypes are the resolution" | **No.** They live in `probes/`, are imported by nothing, and are discarded on exit. They establish the *class* of each blocker. **Six of the twelve resolutions require a record backfill; one (A-10 maximal) is not backward compatible.** Those costs are stated in the Blocker Resolution Matrix rows |
| "A-14 is removable" | **No.** Half is. The agreement half is fundamental, and it was predicted by Ω∞-A's own falsification criterion 5 |
| "A-16 is removable" | **Only the tractability half.** Six of the seven designed invariants have **no proof of any kind**, because the module does not exist |
| "The Phase 2 tree is free of hardcoded assumptions" | **No.** Ω∞-B found six that Ω∞-A did not, including a **silent corruption** (bare `str` position exploded and fingerprinted) inside a closure Ω∞-A had assessed as complete |
| "The nine CLOSED rows are closed" | **Closed against the tests that exist.** Ω∞-A's own false-negative warning applies, and Ω∞-B's six new findings are direct evidence for it |
| "G-05 and G-06 are removable" | **ARGUED, not measured.** Both are *absences* rather than *limitations*; no probe tested either, and this matrix says so rather than borrowing A-11's reasoning silently |

---

## 4. DETERMINATION

**No assumption is marked resolved. No closure is declared. No readiness is claimed.**

| Question | Determination |
|---|---|
| How many assumptions are resolved? | **Zero.** Nine are CLOSED-as-measured in the Phase 2 tree with the legacy trees untouched; that is a scoped absence, not a resolution of the assumption in the repository |
| How many have removability established by evidence? | **Eight fully, three in half** |
| How many are not closable? | **Two outright (A-06, A-17), plus the fundamental halves of A-14, A-18 and A-22 — all of which are C-04 or C-01 surfacing inside an assumption** |
| How many remain open with no Ω∞-B evidence? | **Three (A-19, A-23, A-27)**, each recorded with the reason: A-19's mitigation is a ratchet Ω∞-B does not improve on; A-23 depends on A-22; A-27's unapplied half is a labelling problem that produced a **new** finding of the same class |
| Did Ω∞-A's false-negative warning prove justified? | **Yes, six times.** Which is grounds for treating **this** matrix as incomplete too |

**The most useful single observation in this matrix.** The pairing of **A-17** (registering an axis makes
prior records incomplete — correctly reported) with **A-11** (registering an axis leaves the new concern
non-binding — silently ignored) is the sharpest available statement of what remains wrong. Both behaviours
follow from the same registration. One is the architecture at its most honest; the other is the silent
governance state the architecture exists to eliminate, occurring in the certification path. **They are not
two findings about registration. They are one finding about where the architecture's rigour stops.**
