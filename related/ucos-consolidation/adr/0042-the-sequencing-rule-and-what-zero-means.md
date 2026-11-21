# ADR-0042: The sequencing rule, and how a count reaches zero honestly

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-09-05 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | `CEP-002 Art 28.5`, `UCKP-ART-16`, `adr/0030`, `adr/0041` |
| Supersedes | none |

## Context

Two rules governed a long working session and existed only in conversation. `CEP-002 Article 28.5`
holds that a decision whose trace is only conversational is not recorded, so neither rule bound
anything: a later session, or a different agent, would inherit no obligation at all.

The first rule is sequencing: **implement → test to a full pass → commit; on a failure, fix →
test to a full pass → commit → only then the next item.** Thirteen commits were produced under it,
each through a full verification lane, none forced.

The second rule is what "zero" means. It was never stated, and the session produced the evidence
for why it needs to be: a residue count fell twice without any work happening, and both falls were
lawful. Without a stated meaning, a falling number reads as progress it did not represent.

## Decision

**Sequencing.** No item begins while another is unresolved. A failing verification is not a
finding to be logged and passed over — it is the current item until it is green. Preflight (lint,
format, the governance gates the lane will run) is executed locally BEFORE the lane, because a
lane spent discovering a formatting error is a lane that measured nothing.

**Zero is reached by declaring, not by pretending.** A residue class reaches zero when every
remaining instance carries a recorded, checkable disposition — not when the instances are gone.
`adr/0030` already established the principle for requirements: a deliberate gap is a record, not a
defect. This extends it to counts.

Three consequences, each learned from a defect this session:

**A count and its declarations are ratcheted separately.** Declaring an instance lowers a count
without changing one line of behaviour, so a single ratchet can always be satisfied by writing a
paragraph. Both numbers carry ceilings; a fall in one matched by a rise in the other is recorded
as buying nothing.

**MOVEMENTS distinguishes three kinds of fall.** A *migration* changes behaviour and must be
proven population-identical first. A *declaration* changes none and records a question the
abstraction cannot answer. A *correction* is a detector fix where no code moved at all. Collapsing
them lets a number imply work that did not happen.

**A detector is trusted only with failing cases in both directions.** One that cannot catch is
useless; one that cannot spare is worse, because false positives make a floor unreachable — the
last entries resist every migration, and the only way to close the count is to declare instances
that were never defects.

## Alternatives rejected

**Leave both rules as working practice.** Rejected: that is precisely the condition `adr/0021`
disclosed about itself and kept for fourteen days, and the condition `adr/0041` names as a
recurrence class. A rule nothing records is a rule the next session does not inherit.

**Define zero as "no instances remain".** Rejected by measurement. Four instances this session are
complete without being migrated: a bootstrap that locates the repository root before a provider can
be rooted at it, and a module needing ignore-rule attribution, which is not a discovery question.
Forcing either would mean inventing a single-implementation abstraction to make a counter fall —
the decoration `adr/0021` warns against and `adr/0040` measures.

**Make this a gate.** Rejected for the reason `adr/0041` gives about its own class: a gate for a
sequencing rule would need a scope, and would inherit the defect it exists to prevent. What is
gateable is already gated — each class's own ratchet refuses, by name, at the file.

## Revisit conditions

- A fourth kind of movement is found that is neither migration, declaration nor correction.
- A residue class reaches a floor composed entirely of declarations, which would test whether the
  declaration ceiling is doing its work or merely absorbing the remainder.
- A detector is admitted that cannot express a must-not-catch case, which would mean the
  both-directions requirement is unsatisfiable for some class of defect and needs qualifying.

## Consequences

A later session inherits the rules rather than rediscovering them. `UZX-000001` already enforces
the detector requirement mechanically; the sequencing rule and the meaning of zero are recorded
here because neither is mechanically checkable without a scope that would itself be a gap.

Negative, and disclosed in the manner `adr/0021` established: nothing checks conformance to the
sequencing rule. It is a discipline, recorded so it can be cited and so a departure from it is
visible as a departure rather than as an ordinary way of working.

## Compliance

- `CEP-002 Article 28.5` — the trace is no longer only conversational, which is the whole purpose.
- `UCKP-ART-16` — governance decisions are discoverable, replayable and auditable; two rules that
  governed thirteen commits were none of those.
- `adr/0030` is extended, not contested: a declared absence is lawful, and this states how a
  declared absence counts toward a residue total.

## Validation evidence

Thirteen commits between `3b577c86` and `7e1a817a`, each landed on a green `./verify.sh --change`.
The `INV-AGN-02` MOVEMENTS log carries all three movement kinds with the reasoning for each: a
migration proven identical at 7,126 paths, a declaration matched by a rise in the declaration
ceiling, and a correction where two entries left a count because they were never callers.
