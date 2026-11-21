# UNIVERSAL ASSIMILATION FEEDBACK LOOP DETERMINATION

| Field | Value |
|---|---|
| ARTIFACT | `UNIVERSAL-ASSIMILATION-FEEDBACK-LOOP-DETERMINATION.md` |
| CLASSIFICATION | `EVIDENCE` |
| AUTHORITY | **NONE — DERIVED TRUTH.** Builds nothing, registers nothing, changes no hook, mints no identifier. |
| DISPOSITION | **DETERMINATION ONLY.** No engine, hook or declaration modified. |
| SUBJECT | The Universal Assimilation Feedback Loop: Discovery → Comparison Against Existing Knowledge → Duplicate Detection → Conflict Detection → Authority Resolution → Canonical Update Proposal → Validation → Governed Adoption → Future Enforcement; and detection of repeated discussions, forgotten principles, contradictory implementations, duplicate concepts, obsolete assumptions and hardcoded limitations |
| BASELINE | HEAD `03179308f5cb` · branch `integration/recovery-001` · working tree unchanged |
| MODE | Read-only measurement. No registry mutation. No identity minting. No certification claim. |
| GOVERNING INSTRUMENTS | `.kiro/hooks/uakos-closure-002.json` · `00-MASTER/UAKOS-CLOSURE-002/closure_engine.py` · `PR-02` Knowledge Once · `UCOS-UFC-001` UFC-16 · `CMG-000001` LXXVII.2/.4 (exactly one disposition; no default routing) |
| REFUSES | Claiming the loop is complete. Treating `gap_total: 0` as "no gaps". Building a second assimilation engine. |

> **Headline.** The feedback loop is **not missing — it is installed, running on every session start, and operating with its single most relevant detector switched off.** `.kiro/hooks/uakos-closure-002.json` invokes `closure_engine.py` with `CLOSURE_SKIP_CORPUS=1`, so `scan_mode` is `repo-only (declared)` and the **`conversation_only` gap class — the one that detects knowledge which exists only in discussion and was never written into the repository — is out of scope by declaration.** That class is precisely the detector for "forgotten principles" and "repeated rediscovery", which is the defect this entire directive exists to fix. The engine is scrupulously honest about it; the headline surfaced at session start (`gaps=0`) is not. Six of nine lifecycle stages exist; three of six required detections exist; and the highest-value fix is a configuration and corpus-availability decision, not new code.

---

## 1. Evidence

| Question | Command / file | Result |
|---|---|---|
| Does a loop exist and run automatically? | `.kiro/hooks/uakos-closure-002.json` | `trigger: SessionStart`, *"Runs the repository closure workflow (fast repo-only pass) at session start so newly added knowledge is reconciled against Repository Truth"*; `timeout 120`; described as *"Deterministic and idempotent; non-blocking"* |
| Exact command | same | `CLOSURE_SKIP_CORPUS=1 python3 00-MASTER/UAKOS-CLOSURE-002/closure_engine.py 2>/dev/null \| grep UAKOS-CLOSURE-002 \|\| true` |
| Current output | session-start hook output | `UAKOS-CLOSURE-002: CLOSED \| concepts=549 \| gaps=0` |
| Gap classes measured | `00-MASTER/UAKOS-CLOSURE-002/closure.json` | 7: `conversation_only`, `duplicate_canonical_homes`, `in_repo_unhomed`, `not_homed_concepts`, `orphan_concepts`, `ukda_content_hash_duplicates`, `upload_only` — all **0** |
| Scan scope | same | **`scan_mode: "repo-only (declared)"`** · `corpus_present: false` · `corpus_files: 0` |
| Scope disclosure, verbatim | same, `population_disclosure` | *"`CLOSURE_SKIP_CORPUS=1` was declared by the caller, so the external corpus was deliberately not scanned. The `conversation_only` class is out of scope for this run by explicit declaration, not unmeasured by accident."* |
| Is that class corpus-only? | `closure_engine.py:21` | *"The `conversation_only` gap class is measurable ONLY from the external corpus"* |
| Was this a known prior defect? | `closure_engine.py:26` | *"…`corpus_present`, so an unscanned population returned CLOSED"* — the engine now discloses `scan_mode` because of it |
| Where is the corpus expected? | `closure_engine.py:74` | `CORPUS = REPO.parent / "UCOS"  # external corpus sibling (conversation/upload material)` — **absent** |
| Sources actually scanned | `closure.json` `sources` | `markdown: 3324` · `docx_uploads: 24` · `tracked_total: 6176` · `corpus_files: 0` |
| Concept dispositions | same | `IMPLEMENTED 335` · `DEFERRED 176` · `SPECIFIED 25` · `REJECTED 13` |
| Hardcoded-limitation detector | `python3 -m engine.infinite_scope.gate --quiet --json` | `verdict: OPEN`, 11/11 laws hold, read-only (tree verified unchanged) |
| Contradiction handling | `00-MASTER/UCOS-UCAF-001/ucaf-authority.json` | 3 `reconciliations`; *"Two located instruments may both stand and disagree… neither silences the earlier nor asserts the later"* |
| Other closure programmes | `00-MASTER/` | `UAKOS-CLOSURE-002` … `-009` plus `UAKOS-PHASE-001A-R1` … `-007` |

---

## 2. Current state — the loop, stage by stage

| # | Stage | State | Located owner / gap |
|---|---|---|---|
| 1 | Discovery | **EXISTS, scope-limited** | `closure_engine.py` over 3,324 markdown + 24 docx + 6,176 tracked files. External corpus **not scanned**. |
| 2 | Comparison Against Existing Knowledge | **EXISTS** | Concept homing: `exact_homes`, `def_homes`, `_is_def_home()`; classes `in_repo_unhomed`, `not_homed_concepts`. |
| 3 | Duplicate Detection | **EXISTS** | `duplicate_canonical_homes` (0) and `ukda_content_hash_duplicates` (0), the latter grounded in CKO `content_sha256` — the `PR-02` Knowledge Once mechanism. |
| 4 | Conflict Detection | **PARTIAL** | `UCAF` records 3 reconciliations where located instruments disagree. No general contradiction detector; `orphan_concepts` catches structural, not semantic, conflict. |
| 5 | Authority Resolution | **EXISTS** | `UCAF`: 34 authorities, 17 resolutions, 61 delegations — answers a competence question by reading a located instrument. |
| 6 | Canonical Update Proposal | **PARTIAL** | `09-REPOSITORY-ENRICHMENT-PLAN.md` and `10-CONSTITUTIONAL-GAP-REGISTER.md` are generated. They propose enrichment; they do not propose canonical *updates* to principles or laws. |
| 7 | Validation | **EXISTS** | `verify.sh` (14 stages); per-programme gates; closure `determination` field. |
| 8 | Governed Adoption | **EXISTS** | `UCDA-000001` 9-stage decision lifecycle with evidence gate; `EVOLUTION-001` 8-stage wave lifecycle. |
| 9 | Future Enforcement | **EXISTS for one class** | `UISD-000001` 11 laws enforce hardcoded-limitation openness in CI and `verify.sh` stage 6f. No enforcement derived from an assimilated principle. |

**Six exist · two partial · one enforcement class of several.**

---

## 3. Required detections — measured

| Required detection | State | Basis |
|---|---|---|
| **duplicate concepts** | **EXISTS** | `duplicate_canonical_homes` 0; `ukda_content_hash_duplicates` 0, by content-hash equality |
| **hardcoded limitations** | **EXISTS** | `UISD` 11 laws, 11 axes, 11 disclosed closures, 11 gaps; passes read-only |
| **contradictory implementations** | **PARTIAL** | `UCAF` reconciliations (3) capture *instrument* contradictions. Two live *code* contradictions found this session — nucleus-vs-CEU, and the civilization stratum chain — were found by hand, not by any detector. |
| **forgotten principles** | **CLASS EXISTS, UNMEASURED** | `conversation_only` is the detector; it is corpus-only, the corpus is absent, and the hook skips it by declaration |
| **repeated discussions** | **ABSENT** | No similarity, recurrence or discussion-identity mechanism anywhere |
| **obsolete assumptions** | **ABSENT** | No staleness or supersession-drift detector. `UCDA` records supersession when authored; nothing detects an assumption that has silently expired |

**Three of six exist · one partial · one present-but-unmeasured · two absent.**

---

## 4. Conflicts

| ID | Conflict | Grade |
|---|---|---|
| **FL-C-01** | **`gaps=0` is scope-qualified and the qualification does not travel with it.** The engine discloses `scan_mode` and `population_disclosure` in `closure.json`, but the hook pipes output through `grep UAKOS-CLOSURE-002`, so the line surfaced at session start carries `concepts=549 \| gaps=0` **without** the scope caveat. A reader could reasonably conclude the repository has no assimilation gaps. | **CONFIRMED** |
| **FL-C-02** | **The detector for the directive's core defect is the one that is off.** `conversation_only` detects knowledge existing only in discussion — exactly "forgotten principles" and the substrate of "repeated rediscovery". It is measurable only from the external corpus, which is absent (`corpus_present: false`) *and* skipped (`CLOSURE_SKIP_CORPUS=1`). | **CONFIRMED** |
| **FL-C-03** | **Two failure modes are conflated into one skip.** "Corpus deliberately skipped for speed" and "corpus does not exist at `REPO.parent/UCOS`" are different conditions with different remedies. The current configuration produces the same output for both. | **CONFIRMED** |
| **FL-C-04** | **Code contradictions are undetected.** Both live contradictions found this session were found by reading. No engine compares two executing surfaces for contradictory assertions. | **CONFIRMED** |
| **FL-C-05** | **The loop has no principle subject.** It assimilates *concepts*. Nothing closes the loop from an assimilated principle to a generated enforcement obligation — which is the "Future Enforcement" stage for principle-class knowledge. | **CONFIRMED** |
| **FL-C-06** | **Prior identical defect, same class.** `closure_engine.py:26` records that an unscanned population once *"returned CLOSED"*. The fix was disclosure, not measurement — so the same condition can recur, disclosed, indefinitely. | **CONFIRMED** |
| **FL-C-07** | **Nine closure programmes and seven closure phases** (`UAKOS-CLOSURE-002..009`, `UAKOS-PHASE-*`). Whether these are one loop iterated or several loops over different subjects is not declared — a `UFC-16`-shaped ambiguity. | **APPARENT** — directory names enumerated; contents of `-003..-009` not read. |

---

## 5. Design — closing the loop

### 5.1 The three-line fix that yields the most

None of these is new code:

1. **Make the scope qualification travel with the verdict.** The hook greps one line; that line should carry `scan_mode`. A verdict whose scope is invisible is the defect `closure_engine.py:26` already recorded once. Cheapest possible change, highest honesty return.
2. **Distinguish corpus-absent from corpus-skipped.** Two conditions, two dispositions. `CMG-000001` LXXVII.2 requires *exactly one disposition for every concept reached*; the same discipline should apply to the scan's own state.
3. **Decide the corpus.** Either the external corpus at `REPO.parent/UCOS` is available and scanned periodically, or its absence is recorded as a standing disclosed gap with an owner. Currently it is neither — it is absent and unremarked outside the JSON.

### 5.2 The two genuinely absent detectors

| Detector | Feasible mechanism | Determinism risk |
|---|---|---|
| **Repeated discussions** | Content-hash and normalized-form equality over discussion artifacts, reusing the `ukda_content_hash_duplicates` mechanism rather than inventing similarity scoring | **LOW if exact-match only.** Semantic similarity would be non-deterministic and unreplayable — it must not be built that way. |
| **Obsolete assumptions** | An assumption record carrying its basis; the detector reports assumptions whose basis no longer resolves — the same shape as `UCAF`'s *"A rule whose anchor is absent is a binding failure, not a silent pass"* | **LOW.** Anchor resolution is deterministic. |

Both are expressible as **two-way reconciliations**, the pattern `ISD-L-11` already implements: an undeclared occurrence fails, and a stale declaration whose subject no longer exists also fails. Applied here: a discussion recurring without a corresponding canonical object fails, and a recorded assumption whose basis has vanished fails.

### 5.3 The contradiction detector

Narrowly scoped so it is decidable. Not "find all contradictions" — that is unbounded — but: **for each pair of surfaces where one declares itself a projection of the other, verify the projection does not assert what the source withdrew.** This is decidable, and it would have caught the nucleus/CEU contradiction mechanically, since `engine/nucleus/law.py` *already declares itself a projection of CEU*. The declaration is present; nothing reads it.

### 5.4 Where it belongs

`UAKOS-CLOSURE-002` is the located owner. It already runs at session start, is deterministic and idempotent, and has the seven-class gap register the loop needs. New detections should enter as **additional gap classes** in that engine, with any openness law entering `UISD`'s declaration. **No new engine, no new programme, no new identifier** — the same conclusion the principle-assimilation determination reached about UPAE, for the same reason.

---

## 6. Decision options

| Option | Description | Assessment |
|---|---|---|
| **A — Fix scope honesty, then add the two absent detectors** *(recommended)* | §5.1 first (config and reporting), then repeated-discussion and obsolete-assumption classes, then the projection-contradiction check. | Cheapest first, highest-value first. Nothing requires new authority. Reversible. |
| **B — Build a new feedback-loop engine** | Charter an assimilation-loop programme. | **Rejected.** Duplicates `UAKOS-CLOSURE-002`, breaches Zero Parallel Authority, and mints an identifier the directive forbids. |
| **C — Enable corpus scanning in the session hook** | Drop `CLOSURE_SKIP_CORPUS=1`. | **Rejected as a first step.** The corpus is absent, so this changes nothing except runtime; and the hook has a 120s timeout that a full corpus scan may exceed. Decide the corpus (§5.1.3) first. |
| **D — Semantic similarity for repeated discussions** | Model or heuristic similarity. | **Rejected.** Non-deterministic, unreplayable, and would make the loop's verdict irreproducible — disqualifying under the engine's own determinism guarantee. |
| **E — Accept the loop as sufficient** | `gaps=0`, done. | **Rejected.** That reading is exactly FL-C-01. |

**Recommended direction: A.** Note the ordering is deliberate: making the scope visible is worth more than adding detectors, because an invisible scope makes every future detector's verdict equally misreadable.

---

## 7. Validation approach

| Obligation | Measurement |
|---|---|
| Scope travels with the verdict | The session-start line includes `scan_mode`; a check fails if a verdict is emitted without it |
| Skip and absence are distinct | `corpus_present` and `corpus_skip_declared` yield distinct dispositions; a check fails if both map to one output |
| Determinism preserved | Two consecutive runs on an unchanged tree produce byte-identical `closure.json` (the engine already claims *"deterministic and idempotent"* — assert it) |
| Read-only preserved | Tree byte-identical before and after; the loop must never mutate what it observes |
| Duplicate detection reuses the existing mechanism | Content-hash equality only; no similarity scoring |
| Obsolete-assumption detection is anchor-based | Every assumption's basis resolves, or the assumption is reported; absence is a finding, never a silent pass |
| Contradiction detection is decidable | Only surfaces that declare themselves projections are compared; the pair set is derived from those declarations, not enumerated by hand |
| New gap classes are two-way | An undisclosed occurrence fails **and** a stale disclosure whose subject no longer exists fails |
| No cardinality assertion | No test asserts 549 concepts or 7 gap classes unless cardinality is itself the invariant |
| The loop detects its own gap | After the fix, a principle discussed and never written must appear as a non-zero `conversation_only` count. **This is the acceptance test for the whole determination.** |

---

## 8. Risk assessment

| ID | Risk | Severity | Mitigation |
|---|---|---|---|
| FL-R-01 | `gaps=0` continues to be read as "no assimilation gaps", and the loop provides false assurance about the exact defect it was built to catch | **HIGH** | §5.1.1 — scope travels with the verdict. Highest priority in this determination. |
| FL-R-02 | Repeated-discussion detection is built on semantic similarity, making the loop non-deterministic and its verdicts unreplayable | **HIGH** | Exact content-hash equality only. If exact matching is insufficient, do not build it. |
| FL-R-03 | Enabling corpus scanning exceeds the hook's 120s timeout and the loop silently stops running (`|| true` swallows failure) | **MEDIUM** | Measure runtime before enabling; consider a separate non-session-start trigger. Note the hook already suppresses stderr and cannot fail loudly. |
| FL-R-04 | The absent corpus is treated as an engine defect rather than a missing input | **MEDIUM** | FL-C-03: distinguish the two conditions explicitly. |
| FL-R-05 | Contradiction detection is scoped broadly, becomes unbounded, and is abandoned | **HIGH** | Restrict to declared projection pairs (§5.3). |
| FL-R-06 | New gap classes land blocking and turn a passing loop red on known items, prompting the classes to be disabled rather than the gaps closed | **HIGH** | Observe-and-disclose first, as with UISD laws. |
| FL-R-07 | A "canonical update proposal" is auto-adopted, letting a machine amend canonical truth | **HIGH** | Proposal ≠ adoption. Adoption stays in `UCDA`'s 9-stage lifecycle with its evidence gate and human ratification (`LAW P32-003`). |
| FL-R-08 | Nine closure programmes drift, each measuring an overlapping population | **MEDIUM** | Declare each programme's subject; FL-C-07 is currently **APPARENT** and should be measured before extending any of them. |
| FL-R-09 | The loop is credited with preventing rediscovery when it has never measured the class that would prove it | **HIGH** | The §7 acceptance test: a discussed-but-unwritten principle must produce a non-zero count. |

---

## 9. Acceptance criteria

1. Every verdict the loop emits carries its scan scope. A verdict without `scan_mode` is a failure. **Currently: the session-start line omits it.**
2. `corpus_present: false` and `corpus_skip_declared: true` produce distinct, individually identifiable dispositions.
3. The external corpus is either scanned on a declared cadence, or its absence is a standing disclosed gap with a named owner. **Currently neither.**
4. `conversation_only` is measured at least once against a real corpus, and the result — zero or non-zero — is recorded with its scope. Until then, no claim that forgotten principles are absent.
5. **The loop detects the defect this directive describes:** a principle discussed and never written to the repository appears as a non-zero `conversation_only` count. This is the single acceptance test that matters.
6. Repeated-discussion detection, if built, is deterministic and replay-verified — byte-identical output across runs on an unchanged tree.
7. Obsolete-assumption detection reports every assumption whose basis no longer resolves; absence of an anchor is a finding, never a pass.
8. Contradiction detection covers every surface that declares itself a projection of another, and would have flagged `engine/nucleus/law.py` against `engine/ceu/catalog.py` before that contradiction was closed.
9. Every new gap class is two-way reconciled.
10. No canonical object is updated by the loop. Proposals only; adoption stays in `UCDA` with human ratification.
11. No second assimilation engine, programme or identifier is created.
12. The loop remains read-only and deterministic; tree byte-identical before and after every run.
13. Working tree unchanged by this determination; no engine, hook or declaration written. **Verified at close.**

---

## 10. Refusals

- Modifying `.kiro/hooks/uakos-closure-002.json`, `closure_engine.py`, or any gap class. Not performed.
- Running `closure_engine.py` in any mode. Refused: it writes 15 tracked artifacts to `00-MASTER/UAKOS-CLOSURE-002/`, which would breach the no-registry-mutation constraint. **All figures here are read from the committed `closure.json` produced by the session-start hook, not re-measured.**
- Enabling corpus scanning or clearing `CLOSURE_SKIP_CORPUS`.
- Reading `closure_engine.py` in full. Lines 21–26, 74, 177–231, 352–390 and 423–473 were read via targeted inspection; the full 700+ line body was not. Claims about stages not cited above are therefore not supported.
- Reading `UAKOS-CLOSURE-003..009` or the `UAKOS-PHASE-*` programmes. **FL-C-07 is APPARENT** — directory names only.
- Asserting that `gap_total: 0` is wrong. It is correct *for the classes measured*. The finding is about the scope qualification, not the arithmetic.
- Building any detector.
- Asserting the external corpus exists or does not exist beyond `corpus_present: false` at this baseline. Its content, if any, is unknown.

---

## 11. Determination

**INSTALLED, HONEST, AND RUNNING WITH THE WRONG DETECTOR OFF.**

The mechanism the directive asks for is largely present and better engineered than the request assumes. It runs on every session start without being asked, it is deterministic and idempotent, it homes 549 concepts against Repository Truth, it detects duplicates by content-hash equality rather than by guesswork, and it feeds a governed adoption lifecycle that requires human ratification. Six of nine stages exist; authority resolution is handled by a framework that answers competence questions by reading located instruments rather than deciding.

The finding that matters is narrow and uncomfortable. The class that detects knowledge existing only in discussion — the mechanical form of "forgotten principle", and the substrate of the repeated rediscovery this whole directive exists to stop — is measurable only from an external corpus that is absent, and is additionally skipped by declaration in the session-start hook. The engine says so plainly in its own JSON. The one-line verdict surfaced at session start does not. So the system that exists to prevent forgetting currently reports `gaps=0` while never having measured the class of forgetting.

That is not a code defect. It is a configuration and input-availability decision, and it is the cheapest high-value fix identified anywhere in this session: make the scope travel with the verdict, separate *skipped* from *absent*, and decide the corpus. Two detectors are genuinely absent — repeated discussions and obsolete assumptions — and both are buildable deterministically if similarity scoring is refused. A third, contradiction detection, becomes decidable if scoped to surfaces that already declare themselves projections; that scoping would have caught mechanically the contradiction this session found by hand.

**VERDICT: `DETERMINATION-COMPLETE · LOOP PARTIALLY OPERATIONAL · CORE DETECTOR UNMEASURED · IMPLEMENTATION-NOT-AUTHORIZED`**

No engine, hook, declaration or gap class modified. No identifier minted. Working tree unchanged.
