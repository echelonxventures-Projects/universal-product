# ADR-0036: A determination survives by being regenerated or admitted; otherwise it is archived

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-09-04 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | `UCKP-ART-11`, `ADR-0028`, `ADR-0031` |
| Supersedes | none |

## Context

The repository root holds roughly 300 determination, assessment and closure documents. Several
are superseded, and at least one records a finding later work corrected — this programme found
`P4-F-008` describing as absent a capability that `engine/uaue/` had since implemented.

`UCKP-ART-11` already settles the principle: documents are generated views, and *"generated
output never owns truth."*

## Decision

Each root determination is dispositioned as exactly one of:

1. **Regenerated** — registered in `00-BOOK/DATA/generated-artifact-registry.json` with a
   producer and an input closure, after which a hand edit is a drift failure.
2. **Admitted** — its content enters the requirement authority as candidates under `ADR-0031`,
   and the document is then archived.
3. **Archived** — the default.

A document that is none of the three was describing a requirement nobody owns, which the
requirement gate will say out loud.

## Alternatives rejected

**Keep them all for provenance.** Rejected: they are in git history, which is the provenance
mechanism. Keeping them live means keeping documents that contradict each other.

**Delete them.** Rejected — archival preserves readability without conferring standing.

## Revisit conditions

- The sweep finds that a large fraction can be regenerated, which would mean the corpus is
  healthier than measured and the default should be regeneration rather than archive.

## Consequences

The root stops holding contradictory truth. Anything still readable is either a projection of
an instrument or explicitly archived.

The pages this programme itself produced fall under the same rule and are archived once their
content is in the register.

## Compliance

`UCKP-ART-11` (document abstraction). The generated-artifact registry already carries 369
entries under exactly this contract, so the mechanism exists and is being extended, not
invented.

## Validation evidence

The stale `P4-F-008` finding is recorded in
`UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md` under REQ-20, which notes the entry
*"predates the `engine/uaue/` build-out."*
