# ADR-0028: Plane B is the requirement authority; every other requirement surface projects from it

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-09-04 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | `UCKP-ART-03`, `UCKP-ART-18`, `UCOS-UFC-001` UFC-16, `CEP-002` §14.2 |
| Supersedes | none |

## Context

This ADR supersedes nothing. It takes a decision `CEP-002` §14.2 expressly reserved
and every derived engine declined to make.

`REQUIREMENT-UNIVERSE-INTEGRATION-DESIGN-ANALYSIS.md` measured two requirement planes and
stated the defect in terms: *"two requirement planes exist with different populations,
different identifier schemes and no join key. Nothing in the repository states whether these
are the same population."*

Plane A is `UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md` — 49 rows, scheme
`REQ-NN`, hand-tallied markdown. Plane B is `00-MASTER/UAKOS-CLOSURE-009/requirements.json` —
549 records, scheme `RR-<concept_id>`, engine-generated, carrying `authority:
NONE-DERIVED-TRUTH` and `determination: ASSIMILATION-INCOMPLETE`.

A third plane was proposed and refused: `00-MASTER/UCOS-URR-001` stands `PROPOSED — NOT
ADMITTED` because *"a second register plane over the requirements already registered would be
the competing measurement UFC-16 forbids."* The determination declined to choose between A and
B, correctly: choosing is not a derived engine's act, and CEP-002 §14.2 reserves it.

## Decision

**Plane B is the requirement authority.** `00-MASTER/UAKOS-CLOSURE-009/requirements.json` is
the single population; every other requirement surface — including the master index and any
conformance report — becomes a projection of it and holds no independent standing.

Plane B is chosen because it is already data, already engine-produced, and already carries
`authority: NONE-DERIVED-TRUTH`, so promoting it is a governed act rather than a rewrite. Its
`ASSIMILATION-INCOMPLETE` determination becomes the work item rather than a standing defect.

## Alternatives rejected

**Promote Plane A.** It carries 49 curated requirements with owners and acceptance criteria
already written, which is real value. Rejected because it is hand-maintained markdown — the
exact failure mode this decision exists to end — and would need re-homing into data before any
gate could read it. The curation survives as admitted content, not as the authority.

**Keep both and declare a join key.** Rejected: UFC-16 admits one measurement per subject
population. Two registers with a mapping is still two registers, and the mapping is a third
thing to keep correct.

**Create a purpose-built third register.** Rejected under `UCKP-ART-03` — a second authoring of
an existing population is void — and already refused once as `UCOS-URR-001`.

## Revisit conditions

- Plane B's population is shown to be a strict subset of the requirements in force, so
  promoting it would lose obligations Plane A carries.
- A join key is discovered that makes the two planes provably one population, in which case
  the choice was between spellings and not between registers.

## Consequences

Every requirement surface in the repository becomes derivable. The master index and the
traceability matrix stop being authored and become generated projections registered in
`00-BOOK/DATA/generated-artifact-registry.json`, so a hand edit to either is a drift failure.

Plane A's 49 requirements must be admitted into Plane B before Plane A is archived, or the
decision loses content. That admission is the work this decision authorizes, not a consequence
it assumes.

## Compliance

`UCKP-ART-03` (zero duplication) and `UCKP-ART-18` (reuse before create) are satisfied by
promoting an existing register rather than authoring a new one. `UFC-16` is satisfied because
exactly one surface will write a requirement count and every other derives it. This ADR is
itself the CEP-002 §14.2 constituent act the integration determination reserved.

## Validation evidence

Measured, not asserted: `REQUIREMENT-UNIVERSE-INTEGRATION-DESIGN-ANALYSIS.md` §1.1 records the
two planes, their populations (49 and 549), their schemes and the absence of a join key.
`00-MASTER/UCOS-URR-001/00-URR-DISPOSITION-DETERMINATION.md` records the refusal of a third
plane and the reason. `00-MASTER/UAKOS-CLOSURE-009/requirements.json` carries
`requirement_total: 549` and `authority: NONE-DERIVED-TRUTH` at this commit.
