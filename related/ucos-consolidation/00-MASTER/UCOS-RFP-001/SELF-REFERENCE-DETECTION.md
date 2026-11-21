# UCOS-RFP-001 — SELF-REFERENCE DETECTION

> GENERATED FROM `rfp-declaration.json` BY UCOS-RFP-001 — DO NOT EDIT BY HAND.
> Regenerate with `make rfp`. AUTHORITY = NONE (DERIVED TRUTH).
>
> This projection records the DECLARATION only. It carries no commit identity
> (RFP-2) and no observation of the working tree (RFP-3) — including the
> fixed-point verdict itself, which is carried by the gate's exit code and
> standard output. An artifact asserting "the repository is a fixed point"
> would falsify that sentence by being written.

## Detection is architectural

No detector matches a path, a lane, a producer or a field name. Each observes either the BEHAVIOUR of a producer across executions or the BYTES a producer wrote in its own delta. Consequently an authored document that merely cites a commit is never flagged: a citation appears in no producer's delta.

## Topologies

| ID | Topology | Principle | Severity | Detector | Signature |
|---|---|---|---|---|---|
| CYC-OBSERVE | Self-observation cycle | RFP-3 | CRITICAL | `pass_instability` | The producer's output differs between two consecutive executions at ONE unchanged commit. Only an input the producer itself perturbs can do that; the working tree is the input it perturbs by writing. |
| CYC-COMMIT | Commit-identity cycle | RFP-2 | CRITICAL | `commit_token_in_delta` | The bytes a producer writes contain a hex token that this repository's object database resolves to a commit. Only `git rev-parse`-class input produces that, and the artifact is inside a commit it cannot name. |
| CYC-HASH | Hash cycle | RFP-4 | CRITICAL | `mutual_hash_in_delta` | Within one pipeline pass, artifact A's written bytes contain the content hash of artifact B while B's written bytes contain the content hash of A. |
| CYC-REGISTER | Registration cycle | RFP-5 | CRITICAL | `foreign_projection_write` | A producer that does not own the registration projections nevertheless causes them to change — so a non-canonical artifact is carrying a registered identity. |
| CYC-RECURSE | Recursive generator | RFP-6 | CRITICAL | `reentrancy` | A producer re-enters itself, directly or through an aggregate that invokes it. |
| CYC-UNDECLARED | Undeclared producer | RFP-6 | HIGH | `unattributed_residue` | Tracked content changed during a pipeline pass but no declared stage's write zone contains it. |
| CYC-PRODUCER | Undiscovered producer | RFP-6 | CRITICAL | `undeclared_producer` | An executable named by the repository's own Execution Surface writes tracked content when executed, yet is not a stage of the declared pipeline. The proof is behavioural: the candidate was run in isolation and its writes were measured, so the finding never rests on where the file lives or what it is called. |
| CYC-UNGOVERNED | Producer outside write governance | RFP-6 | CRITICAL | `producer_write_outside_zone` | A path a producer was OBSERVED to write lies inside no declared write zone. The artifact therefore has no constitutional owner and no pipeline coverage, whether or not the producer that wrote it is declared. |
| CYC-ZONE | Ambiguous write scope | RFP-6 | HIGH | `overlapping_write_zones` | Two stages declare write zones where one is a prefix of the other, so a path inside the overlap belongs to more than one write scope and 'exactly one owner' is not well-defined. Attribution would then depend on the order zones happen to be read. |
| CYC-UNPROBED | Unprobed producer candidate | RFP-6 | HIGH | `unprobed_producer` | A candidate the repository invokes ITSELF could not be executed and does not participate in the declared re-entrancy protocol, so whether it writes tracked content is unknown. Producer completeness may not be asserted over an executable the repository runs but cannot measure: an unprobed candidate is an undetermined verdict, and treating it as innocent would make the whole measurement fail open. A candidate that aborts BECAUSE the declared guard is armed is self-excluded, and one that nothing invokes and that cannot start unaided is unreachable; both are accounted for separately. |
| CYC-TRESPASS | Write-scope trespass | RFP-6 | CRITICAL | `cross_zone_write` | A declared stage wrote a path that a DIFFERENT declared stage's write zone owns. Attributing the residue to some declared zone is not enough: if the writer is not the owner, the artifact has two producers and belongs to no single write scope, so regenerating it from its declared owner cannot reproduce it. |

## Remediation

| ID | Remediation |
|---|---|
| CYC-OBSERVE | Stop persisting the observation. Keep it as an input to the gate verdict and to standard output. |
| CYC-COMMIT | Remove the commit identity from the emitted bytes. Version control already records it. |
| CYC-HASH | Break the mutual embedding: one side must derive from the other, never both. |
| CYC-REGISTER | Withdraw the class from registration through the declared admission authority. |
| CYC-RECURSE | Declare the stage non-reentrant; the aggregate must exclude itself from its own pipeline. |
| CYC-UNDECLARED | Declare the producer as a pipeline stage, or stop it from writing tracked content. |
| CYC-PRODUCER | Declare the producer as a pipeline stage with its write zone, positioned after the stages whose output it consumes; or stop it writing tracked content. |
| CYC-UNGOVERNED | Extend the owning stage's declared write zone to cover the path, or move the output inside the zone its producer already owns. |
| CYC-ZONE | Make the declared write zones pairwise disjoint: narrow the broader zone, or merge the stages that genuinely share an output surface. |
| CYC-UNPROBED | Make the candidate runnable from a clean checkout, declare it as a stage so the pipeline runs it, or give it the inputs its earlier stages owe it. |
| CYC-TRESPASS | Stop the trespassing stage writing outside its own zone, or move the path into the zone of the stage that actually produces it. One artifact, one producer. |

## Why behaviour, not inspection

A producer that reads repository state cannot be recognised from its source without enumerating the calls it might make; the set of such calls is open. What is closed is the OBSERVABLE consequence: an output that changes at an unchanged commit, or an output containing an identity only the object database can mint. Detecting the consequence catches every present and future mechanism that produces it.

---

*Regenerate with `make rfp`.*
