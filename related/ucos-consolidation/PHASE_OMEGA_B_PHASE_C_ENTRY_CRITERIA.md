# UCOS Ω∞ — PHASE Ω∞-B, DELIVERABLE 11
## Recommended Phase Ω∞-C Entry Criteria

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
declaration, no readiness claim. **Nothing here authorises Phase Ω∞-C, and nothing here declares Phase
Ω∞-B complete.** These are recommended criteria, offered so they can be refused or tightened.

**WHAT AN ENTRY CRITERION IS FOR.** Not a checklist of work done. A criterion is a **question with a
mechanical answer**, such that entering Ω∞-C before the answer is available would mean building on a
claim nobody has checked. Each criterion below therefore states its **verification method** and the
**evidence artifact** that would satisfy it.

**THE PRINCIPLE THESE CRITERIA ENCODE, drawn from what Ω∞-B measured.** The most dangerous condition
found in this phase was not a blocker. It was a **claim in the tree that nothing checks** — a module
docstring presenting nine absent modules in the present tense, and a source comment asserting a proof
that has never run. Every criterion below is shaped to prevent Ω∞-C from inheriting or creating another
one.

---

## 1. HARD ENTRY CRITERIA — Ω∞-C should not begin until all six hold

### E-1 · No claim in the tree describes a module, proof or mechanism that does not exist

| Field | Content |
|---|---|
| **Why** | Measured (`b07` §H9): **9 of the 11 modules listed in `engine/omega_governance/__init__.py`'s own table are ABSENT** — 2 are present. `state.py:58` asserts `invariants.unknown_never_certifies` enumerates all 900 vectors; that module does not exist. The table is also stale the other way, omitting the 11 modules of `reference/` and `temporal/` that do exist. Ω∞-B could measure the exhaustive proof only by reconstructing it inside a probe |
| **Verification** | A mechanical check that every module named in the package's own documentation table exists, failing loudly if not. **The pattern already exists in the same file** — `REQUIRED_STATE_NAMES` at `state.py:340` holds thirteen names so that an edit renaming one is refused by a test rather than a reviewer. The false claim is at `state.py:58`, 282 lines above it |
| **Evidence artifact** | A passing check, plus the corrected docstrings |
| **Cost** | ~30 lines including the test |
| **Why it is a HARD criterion** | Its cost of delay is **epistemic**. Until it holds, no statement about the proof, the register, certification or self-verification distinguishes what is built from what is designed, and **no Ω∞-C assessment of any of them is trustworthy** |
| **Residual after it holds** | The check verifies existence, not correctness — a stub returning `True` satisfies it. That is C-04 in a new location, and the mitigation is C-04's: count what is unexecutable |

### E-2 · The register's shape is decided and recorded before `registry.py` is written

| Field | Content |
|---|---|
| **Why** | A hash chain requires each entry to name exactly one predecessor, imposing a total order on records whose coordinates the same architecture declares `CONCURRENT` (A-24, "the deepest internal contradiction found"). **Cost now: zero. Cost after: a rewrite plus a record migration.** `registry.py` is absent |
| **Verification** | A recorded design decision naming DAG or chain **and its argument**. If DAG: two independent writers append concurrently, the DAG verifies, tampering is detected, and a requested total-order projection is **labelled as a projection in the record it produces** |
| **Evidence artifact** | `b07` §H5 already demonstrates the criterion is satisfiable: concurrent sibling pair, third entry naming both predecessors, `verify()` ok, tampering detected, `kind=PROJECTION`, `asserted_by_register=False` |
| **Cost** | Zero relative to writing it as a chain |
| **Why it is a HARD criterion** | It is the **only** item in the whole programme whose cost is genuinely zero today and genuinely rises. Entering Ω∞-C without the decision recorded risks the decision being made implicitly by whoever writes the file first |
| **Residual** | C-03 is untouched: a total order over distributed events remains **chosen, not recovered**. The DAG makes the choice visible; it does not remove it. A DAG also grows heads without bound absent merges |

### E-3 · Ω∞ Rule 9 distinguishes code migration from record backfill

| Field | Content |
|---|---|
| **Why** | Rule 9's success chain reads *"New Domain Added → Registration Only → No Source Modification → **No Migration** → No Recompilation"*. Measured: for axis registration the first three links hold and **the fourth cannot**. Registering a 7th axis makes `assert_total` raise and name the gap — which is the **correct** behaviour, because the three alternatives each either close the world or fabricate a governance fact |
| **Verification** | The amended rule text, distinguishing **code migration** (avoidable, and this architecture avoids it — measured across eleven registration kinds) from **record backfill** (not avoidable for any architecture permitting its governed questions to grow) |
| **Evidence artifact** | The amended directive |
| **Cost** | A directive edit |
| **Why it is a HARD criterion** | **An unamendable criterion that cannot be met makes every readiness assessment against it dishonest.** Ω∞-C will be assessed against Rule 9. If Rule 9 contains a link no architecture can satisfy, Ω∞-C either fails for a reason that is not a defect or passes by quietly reinterpreting the rule — and the second is worse |
| **Residual** | Record backfill remains real work. The amendment makes it *nameable*, not free |

### E-4 · Every active correctness defect found in Ω∞-B is closed

These are not future barriers. They are producing wrong records now, and they cost the same to fix at any
time — so the only reason to defer them is that nobody has noticed.

| Defect | Observation | Fix | Verification |
|---|---|---|---|
| **Conjunction indistinguishable from alternative** | `path('SPACE','VELOCITY')` returns a **COMPLETE route** with two of three required inputs absent, so `apply()` would produce a `VELOCITY` value having consulted neither time nor frame **and report success** | source **set** keying; report a **shortfall population** when unsatisfiable | `SPACE` alone is UNSATISFIABLE and the missing domains are named — measured in `b07` §H4 |
| **Bare `str` position silently exploded and fingerprinted** | `position='EPOCH'` → `('E','P','O','C','H')`, accepted without refusal, and it **fingerprints** — entering a governance record as a legitimate position. The neighbouring case (empty position) is correctly refused | one `isinstance(position, str)` refusal | the bare `str` is refused with a message naming the intended shape |
| **`assert_provider` advances the clock it verifies** | `LogicalClock` position `(0,)` → `(3,)` | verify a copy, or declare the reading count in the record | verifying a counting clock leaves its position unchanged |
| **A refusal cites a relation the emitting registry cannot resolve** | `compare()` emits `INCOMPARABLE` from a module constant; a registry seeded without it cannot resolve the relation its own record names | resolve the refusal relation **through** the registry; refuse a registry declaring no undecided relation | a narrow registry either resolves the relation it cites or refuses at construction |

**Why HARD.** Every day these remain, more records may be written that nothing can distinguish from
correct ones. **The `str` explosion is the sharpest case: the corrupted coordinate fingerprints, so it is
indistinguishable from an intended one in every downstream record.**

**Residual.** The `str` refusal is **breaking** for any caller relying on the explosion. That population
is likely zero and must be **measured**, not assumed.

### E-5 · Guards and certification inputs are treated as one item, and `blocked_by` is retained

| Field | Content |
|---|---|
| **Why** | Ω∞-A Deliverable 7 §3.3 argued guards "make A-11 impossible". Ω∞-B supplies the evidence: the eighth certification input was bound by a **guard** in a registry. Building the input registry alone would produce inputs that cannot express N-of-M, a window or a peer state — **7 of 8 governance capabilities** |
| **And the constraint Ω∞-A did not record** | **The structural proof of `UNKNOWN never certifies` reads `blocked_by` on the edges inbound to `CERTIFIED`.** A migration that moves the four preconditions *out* of that field into a registry silently destroys the proof's input. **B-01 and B-05 pull in opposite directions on one field** |
| **Verification** | (a) a `QuorumGuard` registered at runtime refuses a transition, naming the shortfall, with zero source edits; (b) an eighth certification input registered at runtime **binds** a decision and appears in its explanation, with zero source edits; (c) **the structural proof still holds** after the change |
| **Evidence artifact** | `b07` §H1 (10 of 10 capabilities), §H2 (8th input bound), §H7 (structural proof at 40 axes) — all three satisfiable, demonstrated separately |
| **Cost** | Small for guards, zero for the decision function, non-zero for re-expressing the four graph preconditions |
| **Why HARD** | Criterion (c) is the reason. Without it, a plausible-looking migration trades one BLOCKING finding for a CRITICAL one and nothing reports the trade |
| **Residual** | A guard can be written that is wrong or always permits (C-04). The maximal option's removal of `set()` from `AuthorityLink` is **the only non-backward-compatible change in the programme** and should not be bundled into this criterion |

### E-6 · No vocabulary-identity work is described as closing A-14

| Field | Content |
|---|---|
| **Why** | Measured: two registries with **byte-identical digests**, same authority, same description, attaching different meanings to one field — **both validated the record as VALID**. **Ω∞-A's own falsification criterion 5 fires, exactly as written.** Digests close divergence *detection*; they do not close *meaning* |
| **The specific danger, and it is a timing danger** | **After the detection half is resolved, federation will appear to work.** Two nodes will exchange digests, agree, and validate identically — while attaching different meanings to the fields they agreed on. **The successful digest comparison becomes evidence for a consensus that was never established** |
| **And a limit Ω∞-A did not record** | **A digest cannot see a registered predicate.** `Invariant.predicate` is a `Callable` with no content digest, so two registries can agree on every digest and **execute different checks** — and the predicate is precisely what gives a `kind` its mechanical meaning |
| **Verification** | Any document, record or report emitted by vocabulary-identity work states that it establishes **divergence detection** and **not semantic agreement**, and states whether predicates are within the digest's scope |
| **Evidence artifact** | The wording of the divergence report itself |
| **Cost** | None. It is a constraint on claims |
| **Why HARD** | It is the only criterion here that guards against a *false assurance* rather than a missing capability, and false assurance is the failure mode Ω∞-A identified as the worst available (G-09) |
| **Residual** | C-04 stands under every option. Behavioural agreement narrows the gap and cannot close it — agreement on a finite sample is not agreement on meaning |

---

## 2. SOFT ENTRY CRITERIA — recommended, and Ω∞-C could reasonably proceed without them

| # | Criterion | Why it is soft | Verification |
|---|---|---|---|
| **S-1** | The structural proof is **incremental**: registering an edge re-checks that edge | The proof holds today against the declared edge set; the risk arrives only when edges are registered at runtime, which nothing yet does | an edge registered targeting `CERTIFIED` without naming `UNKNOWN` is refused or reported at registration |
| **S-2** | `census` merge is available and `fallback_density` carries `(numerator, denominator)` | No unbounded population exists yet | a census over three disjoint shards merged equals the census of the union — measured in `b07` §H6 |
| **S-3** | A **sampled** transitivity check exists and is **labelled as sampled** | `assert_consistent` verifies 3 of the properties an ordering can have; the gap admits an inconsistent model, but no such model ships | 6 violations found in a cyclic ordering, 0 in the shipped strategy, **and the sample size and shape coverage reported in the same record as the verdict** |
| **S-4** | `Comparison` carries `coincident` | A record consumer must currently string-match the relation name to tell coincidence from concurrency — the reasoning `assert_consistent` exists to avoid | the field is present; a C-02 record backfill is reported rather than auto-converted |
| **S-5** | The C-04 ratchet on `unexecutable_invariants()` is CONVERGENT | A mitigation, not a fix, and Ω∞-A already recommends it | the count may fall or hold and never rise |
| **S-6** | At least one **lossy proxy transformation** is declared for a non-encodable artifact class | Measured mechanically available and **untaken**. It converts C-01's mitigation from a recommendation into a recorded governance fact | a declared `lossy=True`, non-computable, authority-bearing transformation in the shipped set |
| **S-7** | Ordering and relation vocabularies are seeded **from a parameter** rather than a module constant | `OrderingRegistry(())` reserves five ordering names unconditionally; `StateRegistry` already takes its seed as a parameter, so the pattern exists in the same package | a registry constructed with an explicit seed holds only that seed |
| **S-8** | Frame reflexivity is **declarable** | `comparable(EARTH, EARTH)` returns a fabricated rule `Ω²-F-00`. Defensible for a reference frame; **not defensible for a frame representing an unrepeatable observation**, which is not comparable with itself across two observations | reflexivity declarable, defaulting to declared-identity for the shipped frames |

---

## 3. WHAT Ω∞-C MUST NOT INHERIT

Stated as prohibitions because each is a way the phase could go wrong while appearing to go right.

| # | Prohibition | Why |
|---|---|---|
| **P-1** | **Do not treat a prototype in `probes/` as a resolution** | Fourteen verdicts in the Blocker Resolution Matrix are MEASURED BY PROTOTYPE. Each establishes that a blocker is *implementation-induced*. **None establishes that the implementation will be correct, complete, or free of the record-shape consequences named in its risk column** |
| **P-2** | **Do not describe any Ω∞-B finding as closed** | Zero assumptions are marked resolved. Eight are REMOVABILITY ESTABLISHED — the tree still accepts `'x'` as a justification, still has two guard kinds, still enumerates four certification preconditions, still materialises every census, still returns a complete route from insufficient inputs, and still has no register at all |
| **P-3** | **Do not report a sampled property without its sampling caveat** | S-3's transitivity check is O(n³) in the sample. A sampled check reported as a proof is **exactly G-09's silent-expiry failure in a new location**, and G-09 is the worst failure mode Ω∞-A identified |
| **P-4** | **Do not auto-fill, auto-qualify or auto-convert any record affected by a widening** | Six of the twelve resolutions require a record backfill (C-02). Auto-filling fabricates a governance fact; the architecture's own precedent — `assert_total` raising and naming the population — is the correct response |
| **P-5** | **Do not bind a newly registered axis to certification automatically** | Not every concern is a certification precondition. Auto-binding fabricates an obligation; ignoring it silently is the current failure. **Report the population of axes no certification input reads** |
| **P-6** | **Do not test `relation.ordered` where a specific relation is meant** | A-02 re-entered once during Ω∞-B through exactly this route: the first draft of the time-bounded guard tested `ordered`, which is true for both `BEFORE` and `AFTER`, and therefore accepted an out-of-window coordinate. **The assumption re-enters through convenience, not through design** |
| **P-7** | **Do not wire any Phase 2 code into `verify.sh`, a gate stage, a seal or a ratchet** | Forbidden by the directive sequence, and Ω∞-B has not changed it. Cost of delay analysis shows this is also the state in which every fix becomes most expensive |
| **P-8** | **Do not treat the Ω∞-B finding lists as complete** | Ω∞-A warned that assumption discovery by inspection has a demonstrated false-negative rate above zero. **Ω∞-B found six assumptions Ω∞-A missed, including a silent corruption inside a closure Ω∞-A had assessed as complete.** That is direct evidence for treating this phase's lists as incomplete too. Two of Ω∞-A's five falsification criteria (2 and 4) remain untested |

---

## 4. WHAT Ω∞-C SHOULD TEST THAT Ω∞-B DID NOT

Recorded so the gaps in this phase's evidence are explicit rather than implied.

| # | Untested | Why it was not tested | Recommended method |
|---|---|---|---|
| **U-1** | **G-05 — storage as a provider** | No `StorageProvider` exists to probe. Ω∞-B could only confirm the absence, which `b01` §B-01.7 does. The removability verdict is **ARGUED, not measured** | Write a `StorageProvider` protocol and an in-memory reference implementation in a probe; verify a register **refuses** a provider declaring `MUTABLE` by name, using the shipped `CapabilitySet.refuse` |
| **U-2** | **G-06 — schema emission** | `schema.py` absent. Verdict **ARGUED, not measured** | Emit contracts in a probe and have someone who has not read the Python source attempt to implement one |
| **U-3** | **Ω∞-A falsification criterion 2** — a governance concept needing a **sixth mechanism** | Not attempted | Enumerate governance concepts from an unrelated domain (regulatory, scientific, legal) and attempt each as a composition of the five |
| **U-4** | **Ω∞-A falsification criterion 4** — a relation between values that is neither a `Relation` nor a `Transformation` | Not attempted | Attempt containment, provenance, aggregation and substitution relations |
| **U-5** | **The six invariants that do not exist** | `invariants.py` absent, so five of the seven designed invariants could not be examined at all — only `unknown_never_certifies` was reconstructible | Once written, each invariant's proof method and complexity should be established the way B-01 established this one |
| **U-6** | **Whether a hyperedge's callable reads all its declared sources** | A callable's behaviour is not inspectable | Declare three sources and a computation reading one; determine whether anything can detect it |
| **U-7** | **Predicate identity within a vocabulary digest** | Found late in Ω∞-B (B-N-07) and not pursued | Two registries with identical digests and different predicates; determine whether the difference is expressible at all |

---

## 5. THE ONE CRITERION THAT MATTERS MOST

If only one criterion is adopted, it should be **E-1**.

Not because absent modules are the most severe finding — they are not; A-14's agreement half is
fundamental and A-21's route defect is producing wrong answers. **E-1 matters most because it is the
criterion that makes the others checkable.**

Ω∞-B's evidence base rests on probes that measure the tree as it is. Where the tree makes a claim about
something that does not exist, a probe can only report the absence — which is what happened with the
exhaustive proof, the register, certification, contradiction handling, self-verification, the adapters,
the evidence document and the schema emitter. **Nine of the eleven modules the package's own table presents were
unmeasurable because they were absent, and the tree said otherwise in the present tense.**

The discipline that would have caught it is 282 lines below the claim, in the same file (`state.py:340`
versus `state.py:58`):

> `REQUIRED_STATE_NAMES` — *"Held here so 'every required state is a declared first-class entity' is
> checked by execution, and so an edit renaming one is refused by a test rather than by a reviewer."*

**The finding is not that eight modules are missing. That is a schedule.** The finding is that the tree
makes a present-tense claim nothing checks, in a file that demonstrates the checking pattern for a
different claim in the same file. Generalising that one pattern from states to modules — and then to
proofs, to guards, and to certification inputs — is the cheapest structural improvement available
anywhere in this programme, and it is the one that keeps every later assessment honest.

---

## 6. DETERMINATION

**Phase Ω∞-B is not declared complete by this document. Phase Ω∞-C is not authorised by this document.
No readiness is claimed, no certification is issued, no seal is generated, no ratchet is advanced, and no
closure is declared.**

| Question | Determination |
|---|---|
| Are entry criteria recommended? | **Yes: 6 hard, 8 soft, 8 prohibitions, 7 untested areas** |
| Does each hard criterion have a mechanical verification? | **Yes**, with a named evidence artifact; five of six are already demonstrated satisfiable by the Ω∞-B probes |
| Are any criteria mutually constraining? | **Yes, and it must be respected: E-5 requires `blocked_by` to be RETAINED, because the structural proof E-1's correction makes honest is the proof that reads it.** B-01 and B-05 pull opposite ways on one field |
| Is the criterion list complete? | **No, and P-8 says so.** Ω∞-B found six assumptions Ω∞-A missed; two of Ω∞-A's five falsification criteria remain untested; seven areas are listed as untested in §4 |
