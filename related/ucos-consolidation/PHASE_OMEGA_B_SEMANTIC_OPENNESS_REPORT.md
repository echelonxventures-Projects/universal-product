# UCOS Ω∞ — PHASE Ω∞-B, DELIVERABLE 6
## Semantic Openness Report (B-03)

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


**AUTHORITY = NONE (DERIVED TRUTH).** Analysis and classification only. No certification, no seal, no
ratchet advancement, no closure declaration, no readiness claim, and no modification to any active
governance, validation or certification process.

**INPUT.** Ω∞-A findings A-14 (BLOCKING, recorded as the highest-severity open item), A-18 (HIDDEN),
A-20 (REPLACEABLE), G-10, X-05, X-12, C-04 (FUNDAMENTAL). Treated as authoritative.

**EVIDENCE ARTIFACTS.**

| Artifact | Purpose |
|---|---|
| `probes/b03_b04_semantic_transformation.py` + `b03-b04-output.txt` | measures registry identity, reproduces divergent validation, attempts federation |
| `probes/b07_removability_validation.py` §H3 + `b07-output.txt` | tests whether divergence is detectable, and whether identity is sufficient for consensus |

```
cd /Users/bipin/Desktop/UCOS-CONSOLIDATION
.ec1-venv/bin/python 00-MASTER/UCOS-OMEGA-B-001/probes/b03_b04_semantic_transformation.py
.ec1-venv/bin/python 00-MASTER/UCOS-OMEGA-B-001/probes/b07_removability_validation.py
```

`b03_b04` re-executed against current repository state is **byte-identical** to its stored output.

**THE STRUCTURAL FINDING OF THIS REPORT, stated first because it changes the shape of A-14.** Ω∞-A
recorded vocabulary consensus as one BLOCKING finding. It is **two findings with different
classifications**, and conflating them would produce a resolution that closes the cheap half and
claims the expensive half:

| | Finding | Classification | Verdict |
|---|---|---|---|
| **B-03a** | Divergence cannot be **detected** | IMPLEMENTATION-INDUCED | **REMOVABLE** — measured |
| **B-03b** | Agreement cannot be **established** | ONTOLOGY-INDUCED | **FUNDAMENTAL** — measured, and Ω∞-A falsification criterion 5 is *confirmed* rather than falsified |

---

## 1. FINDING B-03a — no registry can state what it contains

### Observation

All seven registries in the Phase 2 tree, measured by attribute inspection:

| Registry | `digest()` | `declared_by()` | `diverges_from()` | Public API |
|---|---|---|---|---|
| `DomainRegistry` | **NO** | **NO** | **NO** | assert_authority_total, capable, declare, declare_domain, known, report, resolve, unexecutable_invariants, validate |
| `StateRegistry` | **NO** | **NO** | **NO** | axes, declare, declare_name, initial, known, on_axis, resolve |
| `TransitionGraph` | **NO** | **NO** | **NO** | edge, incoming, known, on_axis, outgoing, register, rule |
| `TransformationRegistry` | **NO** | **NO** | **NO** | apply, between, computable, declare, declared, path, register, report, resolve, uncomputable |
| `CapabilityRegistry` | **NO** | **NO** | **NO** | declare, declare_name, known, resolve |
| `CodecRegistry` | **NO** | **NO** | **NO** | known, register, resolve, supporting |
| `IdentityRegistry` | **NO** | **NO** | **NO** | known, register, resolve |

`grep -rn 'def digest' engine/omega_governance/` returns nothing. `declared_by` exists **only** on
`Provenance` (`domain.py:240`), which is per-**domain**, not per-**registry**.

**Zero of seven registries can state what they contain.**

### The failure mode, reproduced

Two `DomainRegistry` instances, each declaring `MASS` with a different schema and a different
authority. One value, one fingerprint:

```
value fingerprint 428a2df3b3994c77f591a9085c0bc264fda76887d2ecf8ff8d107bd4b67bbb4b
  node A findings : ("missing required field 'owner'",)      -> INVALID
  node B findings : ()                                        -> VALID
  node A domain authority: NODE-A-AUTHORITY
  node B domain authority: NODE-B-AUTHORITY
```

**Divergent verdict on one record: A = INVALID, B = VALID. Neither registry can detect the other.**
There is no comparison operator, no digest, and no contradiction class for vocabulary divergence.

And the registry's own conflict check does **not** help across nodes:

```
same-name/different-description in ONE registry: REFUSED
  ("domain 'MASS' is already declared with different content; one name with two schemas...")
-> the check is INTRA-process only. Across two registries it cannot fire.
```

### Reproduction

`b03_b04` §B-03.1, §B-03.2, §B-03.3.

### Architectural cause

**IMPLEMENTATION-INDUCED.** Every registry is a plain in-process object holding a `dict`. The
architecture's own governance model is never applied to the vocabulary that *implements* it: a
`ReferenceDomain` has an authority, a schema, invariants and provenance, and the `DomainRegistry`
holding it has none of those. Ω∞-A Deliverable 7 §4 states the consequence precisely — "a vocabulary
nobody answers for is exactly the silent governance state Phase 2 exists to eliminate, currently
present in the mechanism that eliminates it."

The cause is not a missing feature so much as a **missed application of the architecture to itself.**

### Consequence if unresolved

| Consequence | Concretely |
|---|---|
| **Federation is impossible, and its impossibility is invisible** | Two nodes validate the same record differently and **both report success**. Nothing anywhere reports a problem |
| **Ω∞ Rule 8 case 5 fails** | "Previously unknown civilizations register and operate" — all eleven registration kinds succeed locally, and agreement does not exist |
| **Compounds with A-20** | Identifiers are a flat namespace. Two deployments minting `Ω²-S-37` for different edges produces **silent semantic divergence**: same identifier, different rule, both valid locally |
| **A merge cannot report a population** | Measured: `declare()` returns the existing entry for an identical name and raises on the **first** differing content. So a hand-merge either succeeds silently or raises at the first conflict. It cannot enumerate divergences, which is the only form in which they could be governed |

### Resolution options

#### Minimal change — derive a digest without touching any registry

`b07` §H3 measures that a content digest is **already derivable** from shipped parts:

```
digest(registry, encoding) = encoding.fingerprint(registry.report())

node A vocabulary digest : 9d2ba2bf13af0d25e5a553c051d8e0b40d874bf8820bf0c1e948d4f2872e1cb3
node B vocabulary digest : 5bf0a5b045411ce38729955f17694f14d7b2f23ae3307b1f52a6866f2e3f49a6
digests differ           : True
```

- **Cost.** Very small. One free function. **Zero registry changes.**
- **Risk.** **Low, with one caveat that matters.** Only `DomainRegistry` and
  `TransformationRegistry` currently expose `report()`. The other five expose `known()`, so a digest
  over them must fix a canonical serialisation — and if that serialisation is chosen carelessly, two
  registries with identical content could digest differently (ordering) or two with different content
  identically (omission). The shipped types are `order=True` frozen dataclasses, which makes a
  canonical order available; it must be *used deliberately* rather than assumed.
- **Architectural impact.** **None.** Purely additive.

#### Moderate change — divergence as a reportable population

```
diverges_from(peer, encoding) -> tuple[Divergence, ...]
```

Measured working (`b07` §H3), reporting a **population** rather than raising at the first conflict:

```
{'domain': 'ALPHA', 'kind': 'ABSENT_RIGHT', 'left_authority': 'NODE-A-AUTHORITY'}
{'domain': 'BETA',  'kind': 'ABSENT_LEFT',  'right_authority': 'NODE-B-AUTHORITY'}
{'domain': 'MASS',  'kind': 'CONTENT_DIVERGENT',
                    'left_authority': 'NODE-A-AUTHORITY', 'right_authority': 'NODE-B-AUTHORITY',
                    'left_digest': '07b2ec66e40512df', 'right_digest': '7e562ebc77952106'}
```

Three divergence kinds, each naming the authorities that answer for the two sides. **Ω∞-A Step 5's
exit criterion — "two registries differing by one declaration report a divergence naming the divergent
declaration and both authorities" — is met by prototype.**

- **Cost.** Small. ~60 lines per registry family, or one generic function over `known()`.
- **Risk.** Low. Read-only; raises nothing.
- **Architectural impact.** **Positive.** It introduces the first mechanism in the package that
  compares two *vocabularies* rather than two values, and it does so in the shape the architecture
  already prefers — report a population, do not raise at the first instance.

#### Maximal correctness — the vocabulary becomes a governed artifact

1. `digest()`, `declared_by()`, `diverges_from()` on every registry.
2. The vocabulary carries a `GovernanceStatus` over the same six axes as any other artifact, and an
   authority chain.
3. `VOCABULARY_CONTRADICTION` joins the designed contradiction classes.
4. Identifiers become `(authority, identifier)`, closing A-20 and X-12.

- **Cost.** High. Item 4 changes the identity of every rule reference in the tree — `Ω²-S-01`…`Ω²-S-36`,
  `Ω²-A-01`…`Ω²-A-08`, `Ω²-C-01`…`Ω²-C-05`, `Ω²-F-00`, `Ω∞-D-*`, `Ω∞-X-*` — and therefore the bytes of
  every record citing one.
- **Risk.** **Medium-high, and concentrated in item 4.** A qualified identifier is a **record-shape
  change**, so it is a C-02 record backfill: prior records cite unqualified ids and cannot be
  auto-qualified without inventing an authority for them. The honest response is the one the
  architecture already uses for axis widening — **report the population of unqualified citations**
  rather than fabricating an authority. Item 3 carries a second risk: a contradiction class that fires
  on *every* federation event is noise, so divergence must be classified by whether it affects a
  validation outcome, which requires knowing what each node validated.
- **Architectural impact.** **Highest available, and it is self-referential in a good way.** After item
  2 the mechanism that eliminates silent governance states is itself subject to that elimination. Item 4
  makes A-20's collision *detectable* rather than silent, which is the difference between two
  deployments disagreeing and two deployments not knowing they disagree.

### Residual risk

| # | Residual | Severity |
|---|---|---|
| R-1 | A digest over five registries requires a canonical serialisation that does not yet exist. Chosen carelessly it produces false agreement (omission) or false divergence (ordering) | MEDIUM |
| R-2 | `diverges_from` compares **declarations**, not **behaviour**. Two registries can hold identical declarations and different registered predicates, because `Invariant.predicate` is a `Callable` and a callable has no content digest | **HIGH, and not recorded in Ω∞-A.** An executable invariant is precisely the part that gives a `kind` mechanical meaning, and it is the part a digest cannot see |
| R-3 | Divergence detection requires the peers to **exchange** digests. No transport, protocol or storage exists (G-05) | MEDIUM — a dependency, not a defect |

---

## 2. FINDING B-03b — identity is not consensus, and this is where the world ends

### Observation

Two registries, **byte-identical digests**, declaring `LENGTH` with a `magnitude` field of kind
`NUMBER`, same authority, same description:

```
two registries, IDENTICAL digests: True
  A validate(LENGTH[magnitude=3]) -> ()   VALID
  B validate(LENGTH[magnitude=3]) -> ()   VALID
```

And nothing anywhere states whether `magnitude` means metres or feet.

Separately, the name-agreement case (`b03_b04` §B-03.3):

```
node A declares MASS = kilograms; node B declares MASS = pounds
  node A validate(MASS[70]) : ()  VALID
  node B validate(MASS[70]) : ()  VALID
```

Both valid. `Field.kind` is a free string this architecture **deliberately never interprets**, so
`'kilograms'` versus `'pounds'` lives only in prose.

### Reproduction

`b07` §H3 second half; `b03_b04` §B-03.3.

### Determination — a falsification criterion confirmed, not refuted

Ω∞-A Deliverable 7 §7 criterion 5: *"Two deployments that agree on every vocabulary digest and still
disagree about a record's validity — which would show vocabulary identity is insufficient for
consensus."*

> **The hypothesis "semantic consensus is achievable by vocabulary identity alone" is REFUTED.**
> Criterion 5 is **CONFIRMED**. Digests close divergence *detection*; they do not close *meaning*.

This is not a defect in the digest proposal. It is the boundary of what any digest can do, and it means
**A-14 is PARTIALLY REMOVABLE rather than removable** — the detection half closes, the agreement half
does not.

### Architectural cause

**ONTOLOGY-INDUCED, and the openness is required rather than accidental.** `Field.kind` is a free
string *on purpose*: interpreting kinds inside `domain.py` would make the set of expressible kinds a
closed list in one file, which is precisely Ω∞ Rule 4's target. The cost is unavoidable and is C-04:
two parties can agree on a name and disagree on what it means, with nothing able to detect it.

The regress argument, stated so it can be checked: grounding every term in another term is infinite
regress; grounding them in a fixed base vocabulary is a closed world. Executable invariants narrow the
gap — a `kind` bound to a domain with checkable invariants has *some* mechanical meaning — and cannot
close it, because an invariant is itself stated in terms that need grounding.

### Consequence if unresolved

The consequence is **not** that federation fails. It is subtler and worse: after B-03a is resolved,
federation will appear to *work*. Two nodes will exchange digests, agree, and validate the same record
identically — while attaching different meanings to the fields they agreed on. **The successful digest
comparison becomes evidence for a consensus that was never established.**

That is why this finding must be stated in the same document as the resolution to B-03a, and why the
resolution must not be described as closing A-14.

### Resolution options

#### Minimal change — make the unchecked population countable

`DomainRegistry.unexecutable_invariants()` already exists and reports invariants that carry no
predicate. Ω∞-A recommends holding that count as a **CONVERGENT ratchet** — it may fall or hold, never
rise.

- **Cost.** Very small. The reporter exists; only the ratchet is missing.
- **Risk.** Low. It is a measurement, not an enforcement.
- **Architectural impact.** None structurally. It changes what is *reportable*, which is the only
  honest move available against a fundamental constraint. **This is a mitigation, not a fix**, and
  Ω∞-A says so.

#### Moderate change — bind kinds to domains with executable invariants

Require every `Field.kind` naming a domain to resolve to a **declared** domain, and count kinds that do
not.

- **Cost.** Moderate. A resolution pass plus a reporter.
- **Risk.** **Medium, and it is a design hazard rather than a defect.** Requiring resolution makes the
  kind vocabulary *less* open, which trades Rule 4 openness for Rule 8 checkability. The correct form
  is to **count** unresolved kinds rather than **refuse** them, so an unknown civilisation's kind is
  admitted and visible rather than rejected.
- **Architectural impact.** Medium. It creates a graded notion of semantic grounding: kinds that
  resolve to a domain with executable invariants, kinds that resolve to a domain without, and kinds
  that do not resolve. That gradation is the most a mechanical system can offer here.

#### Maximal correctness — meaning by behavioural agreement

Two nodes exchange not declarations but **test vectors**: an agreed set of values with agreed expected
verdicts. Consensus becomes "we agree on the outcomes", not "we agree on the names".

- **Cost.** High. It is a protocol, a corpus and a governance process for the corpus.
- **Risk.** **High, and the risk is that it still does not close the gap.** Agreement on a finite
  sample is not agreement on meaning — the classic induction limit. It narrows the gap sharply and
  cannot close it, so it must not be described as closing it.
- **Architectural impact.** Significant, and it would be the first mechanism in the architecture where
  agreement is *demonstrated* rather than *declared*.

### Residual risk

| # | Residual | Severity |
|---|---|---|
| R-4 | Two parties agreeing on a name and disagreeing on its meaning remains undetectable, under every option above | **FUNDAMENTAL.** C-04 |
| R-5 | A deployment could declare every invariant unexecutable and pass validation with zero real checking | **HIGH**, and mitigated only by the ratchet of the minimal option — **still not done** |
| R-6 | Behavioural agreement (maximal) is sample-bounded and cannot be extended to a proof | FUNDAMENTAL |

---

## 3. FEDERATION — attempted, and what the attempt showed

### Observation

```
node A holds: ['ALPHA']   node B holds: ['BETA']
  DomainRegistry.merge          present: False
  DomainRegistry.union          present: False
  DomainRegistry.diverges_from  present: False
  DomainRegistry.compare        present: False
  DomainRegistry.digest         present: False
  DomainRegistry.version        present: False
  DomainRegistry.as_of          present: False
```

Federation by merge is possible only by re-declaring B's domains into A **by hand**, and the merge is
**silent**: `declare()` returns the existing entry for an identical name and raises only on differing
content (`domain.py:409-421`).

### Determination

| Question the directive asks | Answer | Basis |
|---|---|---|
| **Where is consensus required?** | At every point where two nodes validate the same record: domain schemas, invariants, state names, axis sets, transition rules, relation semantics, ordering disciplines, codec identity, and **the meaning of every `kind` string** | §1, §2 |
| **Is consensus implicit or explicit?** | **Entirely implicit.** No registry declares what it contains, who answers for it, or how it differs from a peer's. Consensus is currently an assumption held by whoever configured both nodes | §1 |
| **Does interoperability survive divergent vocabularies?** | **No — and worse, it appears to.** Measured: divergent verdict on one record, both nodes reporting success, neither able to detect the other | §1 |
| **Is registry federation possible?** | **Structurally yes; semantically only partly.** Merge and divergence detection are derivable with no registry change (§1, measured). Agreement on *meaning* is not achievable by any mechanism here (§2, measured) | §1, §2 |

---

## 4. SEMANTIC OPENNESS REGISTER

| ID | Finding | Observation | Architectural cause | Classification | Verdict |
|---|---|---|---|---|---|
| S-01 | No registry exposes a content digest | 0 of 7; `grep 'def digest'` empty | IMPLEMENTATION-INDUCED | **REMOVABLE** — derivable from `report()` + `Encoding`, measured |
| S-02 | No registry names an authority | `declared_by` exists only on `Provenance`, per-domain | IMPLEMENTATION-INDUCED | **REMOVABLE** — the architecture applied to itself |
| S-03 | No registry can compare with a peer | no `diverges_from`/`compare`/`merge` | IMPLEMENTATION-INDUCED | **REMOVABLE** — measured, reporting 3 divergence kinds with both authorities |
| S-04 | Divergent verdict on one record, both nodes succeed | A=INVALID, B=VALID, fingerprint identical | IMPLEMENTATION-INDUCED | **REMOVABLE** — S-01+S-03 convert it to a finding |
| S-05 | The conflict check is intra-process only | one registry REFUSES; two cannot fire | IMPLEMENTATION-INDUCED | **REMOVABLE** |
| S-06 | A merge cannot report a population | `declare()` raises on first conflict | IMPLEMENTATION-INDUCED | **REMOVABLE** |
| S-07 | Identical digests, divergent meaning | `magnitude` = metres or feet; both VALID | **ONTOLOGY-INDUCED** | **FUNDAMENTAL** (C-04). Ω∞-A criterion 5 **confirmed** |
| S-08 | Name agreement without meaning agreement | MASS = kilograms vs pounds; both VALID | **ONTOLOGY-INDUCED** | **FUNDAMENTAL** (C-04) |
| S-09 | A digest cannot see a registered predicate | `Invariant.predicate` is a `Callable`; no content digest | **IMPLEMENTATION-INDUCED with an ontology-induced residue** | **PARTIALLY REMOVABLE.** **New in Ω∞-B** |
| S-10 | Flat identifier namespace admits cross-deployment collision | `Ω²-S-37` mintable twice | IMPLEMENTATION-INDUCED | **REMOVABLE** by `(authority, identifier)`; record backfill required |
| S-11 | Every invariant could be declared unexecutable and pass | `unexecutable_invariants()` reports, nothing ratchets | GOVERNANCE-INDUCED | **PARTIALLY REMOVABLE** — ratchet, not fix |

**Nine removable or partially removable. Two fundamental. One (S-09) is new and is the sharpest
limit on the digest proposal.**

---

## 5. DETERMINATION

**No closure is declared.** Established mechanically:

| Question | Determination | Basis |
|---|---|---|
| Is B-03 removable? | **PARTIALLY REMOVABLE** | Detection removable (§1, measured). Agreement fundamental (§2, measured) |
| Classification | **IMPLEMENTATION-INDUCED** for detection; **ONTOLOGY-INDUCED** for agreement | §1, §2 |
| Is any part mathematically unavoidable? | **Yes.** The regress in §2 is not a software limit | §2 |
| Does Ω∞-A falsification criterion 5 fire? | **Yes — it is CONFIRMED** | §2 |
| Cost of delay | **Moderate and flat.** Independent of build order, per Ω∞-A — **except S-10**, whose cost rises with every record citing an unqualified identifier | §1 |

**Two corrections to Ω∞-A.**

1. **A-14 is one finding in the register and two in reality.** Ω∞-A called it "the highest-severity
   open finding" and proposed digests as the resolution. The digest resolution is sound and closes
   *detection*; it does not close *agreement*, and the report must not be read as closing A-14.
   Ω∞-A's own falsification criterion 5 anticipated exactly this, and it fires.

2. **S-09 is a limit on the digest proposal that Ω∞-A did not record.** A digest covers declarations.
   `Invariant.predicate` is a `Callable` with no content digest, so two registries can agree on every
   digest while executing different checks — and the predicate is precisely the part that gives a
   `kind` mechanical meaning. Any Step 5 implementation should either declare predicates out of scope
   of the digest **and say so in the record**, or carry a predicate identity the declaring authority
   asserts (which is C-04 again, one level down).
