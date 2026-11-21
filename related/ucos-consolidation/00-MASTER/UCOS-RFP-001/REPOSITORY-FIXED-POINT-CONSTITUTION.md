# UCOS-RFP-001 — REPOSITORY FIXED-POINT CLOSURE CONSTITUTION

> GENERATED FROM `rfp-declaration.json` BY UCOS-RFP-001 — DO NOT EDIT BY HAND.
> Regenerate with `make rfp`. AUTHORITY = NONE (DERIVED TRUTH).
>
> This projection records the DECLARATION only. It carries no commit identity
> (RFP-2) and no observation of the working tree (RFP-3) — including the
> fixed-point verdict itself, which is carried by the gate's exit code and
> standard output. An artifact asserting "the repository is a fixed point"
> would falsify that sentence by being written.

| Field | Value |
|---|---|
| PROGRAMME | `UCOS-RFP-001` — Repository Fixed-Point Closure |
| AUTHORITY | NONE — DERIVED TRUTH. This programme legislates the closure CONDITION; it ratifies nothing, freezes nothing and owns no capability. |
| ORIGIN | CK-REG-DRIFT. A generated artifact carrying repository-derived state (HEAD, commit metadata, projection hashes) was admitted into the registration corpus, creating a registration relation with no fixed point. This declaration makes that class of topology constitutionally impossible rather than individually repaired. |
| DECLARATION | `00-MASTER/UCOS-RFP-001/rfp-declaration.json` |
| SEAL | `7b11aa44b2bd146d` |

## Vocabulary

| ID | Term | Definition |
|---|---|---|
| VOC-FIXED-POINT | **Repository Fixed Point** | A committed repository state R is a Repository Fixed Point of the declared pipeline P when P(R) = R byte-for-byte. Executing every declared producer over R rewrites no tracked byte and creates no untracked entry outside a constitutionally excluded location. |
| VOC-DETERMINISTIC | **Deterministic Repository** | A repository in which every producer's output is a pure function of tracked repository content. Two executions over the same tracked content, in any environment, yield identical bytes. |
| VOC-STABLE | **Stable Repository State** | A state that is a Repository Fixed Point under N consecutive pipeline executions, N being the declared convergence_passes. Stability is an observation over repetitions; a fixed point observed once may be coincidence. |
| VOC-CLOSURE | **Closure State** | The state in which a programme is permitted to declare itself closed: its implementation is complete, every gate binding it PASSES, and the repository containing it is a Stable Repository State. Closure is a property of the REPOSITORY, never a property of the programme's own report. |
| VOC-ACCEPTABLE | **Acceptable Repository State** | A state that is either a Repository Fixed Point, or one whose only divergence is a declared, dispositioned finding carried in this declaration. Any other divergence is unacceptable and fails closed. |
| VOC-NON-CONVERGENT | **Non-convergent Repository** | A repository for which no reachable state is a Repository Fixed Point, because at least one tracked artifact's required bytes are a function of the very act of committing or recording them. Non-convergence is a topological property: it cannot be cleared by regenerating, committing or reordering. |
| VOC-SELF-REFERENTIAL | **Self-referential Repository** | A repository containing at least one tracked artifact whose content depends, directly or transitively, on itself — on the identity of the commit that contains it, on an observation of the working tree that contains it, or on the hash of an artifact that depends on it. Every self-referential repository is non-convergent. |
| VOC-REPO-DRIFT | **Repository Drift** | The genus. Any divergence between the committed repository and the result of re-executing the declared pipeline over it. Registration, Projection and Evidence Drift are its species. |
| VOC-REG-DRIFT | **Registration Drift** | Divergence between the registered corpus and the artifacts on disk: an artifact's recorded identity, content hash or classification no longer matches the artifact. Owned and detected by REG-AUTO-001 (register.sh --guard / CK-REG-DRIFT). |
| VOC-PROJ-DRIFT | **Projection Drift** | Divergence between a derived projection and the canonical source it projects: the projection was not regenerated after its source changed, or was regenerated from a stale reading of it. |
| VOC-EV-DRIFT | **Evidence Drift** | Divergence between recorded evidence and the state it claims to evidence: a verdict, measurement or certification asserting a repository state that re-execution does not reproduce. An evidence artifact that records an observation invalidated by its own writing is permanently in Evidence Drift. |
| VOC-PRODUCER | **Producer** | An executable the repository itself can invoke that writes tracked repository content. Both halves are measured, never assumed: invocability is read from the repository's own Execution Surface, and writing is OBSERVED by executing the candidate and comparing tracked content. Neither half appeals to a filename, a directory, a naming convention or a list, so the definition admits producers that do not exist yet. |
| VOC-EXEC-SURFACE | **Execution Surface** | The set of invocations the repository declares it performs: the recipe lines of its build entry point and the steps of its continuous-integration workflows, plus the argv of every declared pipeline stage. It is the repository's own statement of what it executes, maintained for its own reasons, and is therefore a discovery authority that cannot fall out of date without the repository ceasing to build. |
| VOC-PRODUCER-COMPLETE | **Producer-Complete Repository** | A repository in which every Producer discovered from the Execution Surface is a declared pipeline stage, every path any Producer writes lies inside exactly one declared write zone, and no discovered candidate remains unprobed. Producer completeness is thus a MEASUREMENT over the repository rather than a list somebody maintains, and it is re-measured on every gate run. |

## Principle

### RFP-1 — Fixed-Point Closure Condition

**Rule.** No programme may close, and no repository may be certified, unless the repository is a Stable Repository State: executing the declared pipeline over the committed HEAD leaves the repository byte-identical, for each of the declared convergence passes.

**Why.** Certification asserts a property of the repository. An assertion that re-execution does not reproduce is not evidence.

*Cycle class:* — · *Enforced by:* `CK-FIXED-POINT`

### RFP-2 — No Commit Self-Reference

**Rule.** No tracked artifact's bytes may depend on the identity of the commit that contains it — its hash, abbreviation, committer date, author date, tag or ref.

**Why.** The commit's identity is a function of the tracked bytes it contains. An artifact that names its own commit demands a commit whose hash appears inside its own tree, which is not reachable. Committing changes HEAD, which changes the artifact, without limit. Version control already records the containing commit, so restating it inside the artifact also duplicates state the repository already owns.

*Cycle class:* CYC-COMMIT · *Enforced by:* `CK-FIXED-POINT`

### RFP-3 — No Working-Tree Self-Observation

**Rule.** No tracked artifact's bytes may record an observation of the working tree that the act of recording invalidates. An observation whose scope EXCLUDES the recorder's own declared write zone does not invalidate itself and is therefore permitted; an unscoped observation is not. In every case the observation is a legitimate input to a GATE VERDICT and legitimate content of a gate's exit code and standard output.

**Why.** Writing an unscoped observation falsifies it: an artifact recording 'working tree CLEAN, 0 entries' makes the tree dirty by being written, so the recorded value is never the value that holds once it is recorded. The defect is not the measurement, it is the self-inclusion of the recorder in what it measures. Scoping the observation to exclude the recorder's own write zone removes the self-inclusion and makes the record stable, which is why a repository-cleanliness gate may persist a verdict measured outside its own zone.

*Cycle class:* CYC-OBSERVE · *Enforced by:* `CK-FIXED-POINT`

### RFP-4 — No Hash Cycle

**Rule.** No tracked artifact may embed a content hash of any artifact that depends, directly or transitively, upon it.

**Why.** This is the CK-REG-DRIFT topology exactly: the registry recorded the hash of an artifact that embedded the hash of the registry. Mutual hash embedding admits no simultaneous solution.

*Cycle class:* CYC-HASH · *Enforced by:* `CK-FIXED-POINT`

### RFP-5 — Registration Admits Canonical Source Only

**Rule.** Only artifacts of class CANONICAL-SOURCE are eligible for registration. Every other class is a non-artifact, excluded by a declared authority, and may never consume a permanent corpus identity.

**Why.** Registration records a content hash. A class whose content is derived cannot hold a stable hash relative to the register that records it. This restates GOV-005 §5.3 as a closure obligation and is the rule whose absence produced CK-REG-DRIFT.

*Cycle class:* CYC-REGISTER · *Enforced by:* `CK-REG-ENFORCE`, `CK-REG-DRIFT`, `CK-FIXED-POINT`

### RFP-6 — Producers Are Declared, Never Discovered Ad Hoc

**Rule.** Every producer that writes tracked repository content must appear as a stage of the declared pipeline. A producer absent from the pipeline is unverifiable and its output is therefore not an Acceptable Repository State. Completeness of the pipeline is itself a measured property: the repository DISCOVERS its own producers from its Execution Surface and proves, by execution, that each one is declared. Declaration is never satisfied by a list somebody remembered to update.

**Why.** A fixed point can only be asserted over a known pipeline. Undeclared regeneration is precisely how the CK-REG-DRIFT split reached four sealed commits unnoticed. Discovery closes the residual hole in the original enforcement: attributing residue can only convict a producer that RAN inside the declared pipeline, so a producer omitted from the pipeline never ran and was never observed. Measuring the Execution Surface instead makes omission itself the detectable event.

*Cycle class:* — · *Enforced by:* `CK-FIXED-POINT`, `CK-PRODUCER-COMPLETE`

### RFP-7 — Universal Inheritance, No Opt-Out

**Rule.** RFP-1..RFP-6 bind every PROGRAM, EPIC, EIP, Universe, Framework, Capability and Module, present and future, with no opt-out and no per-programme exemption. Inheritance is structural: the condition is evaluated over the REPOSITORY, so anything the repository contains is bound without needing to declare itself bound.

**Why.** A rule a programme must opt into is a rule the next programme forgets. Evaluating the condition over the repository rather than over a programme register makes exemption impossible and enrolment unnecessary.

*Cycle class:* — · *Enforced by:* `CK-FIXED-POINT`, `G-15`

## Admission classes

| ID | Class | Registrable | Tracked | Convergence obligation |
|---|---|---|---|---|
| CLS-CANONICAL-SOURCE | Canonical Source | **YES** | yes | INVARIANT — authored; no producer rewrites it, so it is trivially a fixed point. |
| CLS-GENERATED-PROJECTION | Generated Projection | no | yes | REQUIRED — must be byte-reproducible from canonical source by its owner. |
| CLS-OPERATIONAL-MEMORY | Operational Memory | no | yes | REQUIRED — a programme determination is evidence, and evidence that re-execution does not reproduce is Evidence Drift. |
| CLS-DERIVED-INTELLIGENCE | Derived Intelligence | no | yes | REQUIRED — derived truth must be re-derivable, or it is not truth. |
| CLS-EVIDENCE | Evidence | no | no | REQUIRED-WHEN-TRACKED — per-run evidence is not tracked; where a family is tracked it carries the full obligation. |
| CLS-CERTIFICATION | Certification | no | yes | REQUIRED — a certification whose re-execution differs certifies nothing. |
| CLS-TRANSIENT | Transient Output | no | no | EXEMPT — never tracked, so outside the fixed point by construction. |

### Placing a future family

1. Is it absent from version control (ignored or untracked)? → CLS-TRANSIENT if environment output, else CLS-EVIDENCE.
2. Does a located producer rewrite it? → NO: CLS-CANONICAL-SOURCE.
3. Is it emitted into the corpus-internal projection zone? → CLS-GENERATED-PROJECTION.
4. Is it a verdict of a certification runtime? → CLS-CERTIFICATION.
5. Is it programme execution or coordination state? → CLS-OPERATIONAL-MEMORY.
6. Otherwise it is producer output declaring AUTHORITY = NONE → CLS-DERIVED-INTELLIGENCE.

**Invariant.** Exactly one class admits registration (CLS-CANONICAL-SOURCE). Every class that is tracked and has a producer carries the convergence obligation. There is no class that is both derived and registrable — which is the state that produced CK-REG-DRIFT.

## Governing instruments

- `00-CEP/CEP-005-CONSTITUTIONAL-CERTIFICATION-CONSTITUTION.md`
- `00-CEP/CEP-008-CONSTITUTIONAL-EVIDENCE-TRACEABILITY-CONSTITUTION.md`
- `00-CEP/CEP-009-CONSTITUTIONAL-AMENDMENT-EVOLUTION-CONSTITUTION.md`
- `00-BOOK/tools/config.py (GOV-005 §5.3 admission boundary)`
- `00-MASTER/UCOS-RECON-C1-OPERATIONAL-MEMORY-EXCLUSION.md`
- `00-MASTER/UCOS-RECON-C2/ROOT-CAUSE-REPORT.md`

---

*Regenerate with `make rfp`. Enforce with `make rfp-gate`.*
