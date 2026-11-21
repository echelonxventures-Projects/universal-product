# ADR-0029: `RR-<concept_id>` survives the join; `REQ-NN` become recorded aliases

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-09-04 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | `UCKP-ART-05`, `ADR-0028` |
| Supersedes | none |

## Context

This ADR supersedes nothing. It is consequential to `ADR-0028`, which chose the authority
whose identifier scheme this decision settles.

`ADR-0028` makes Plane B the requirement authority. The two planes carry different identifier
schemes — `REQ-NN` (49 records) and `RR-<concept_id>` (549 records) — and admitting Plane A's
content into Plane B raises the question of what happens to the identifiers already cited in
determinations, reports and this programme's own traceability.

## Decision

`RR-<concept_id>` is the surviving scheme, because it is the authority's own. Every `REQ-NN`
identifier is retained as a recorded **alias** on the requirement it names.

No identifier is reissued and none is reused for a different subject. A citation of `REQ-28`
in any existing document continues to resolve, through the alias, to the requirement it always
meant.

## Alternatives rejected

**Renumber Plane B to `REQ-NN`.** Rejected: `RR-` identifiers were minted by an engine and are
cited in generated evidence; renumbering 549 records to match 49 would reissue identity, which
`UCKP-ART-05` forbids — *an identity, once minted, never changes.*

**Drop `REQ-NN` entirely.** Rejected: dozens of determinations cite `REQ-01`…`REQ-41`. Dropping
the scheme would silently break every one of those citations, which is a worse defect than
carrying an alias map.

## Revisit conditions

- An alias is found to be ambiguous — one `REQ-NN` resolving to two `RR-` records — which would
  mean the two planes were not the same population after all and `ADR-0028` needs revisiting
  before this one does.

## Consequences

Aliases are data on the requirement record, so resolution is a lookup rather than a convention.
Documents citing `REQ-NN` keep working without edit, which is what makes archiving Plane A safe.

## Compliance

`UCKP-ART-05` is satisfied: nothing is reissued, nothing is reused, and the historical
identifier remains resolvable rather than being deleted.

## Validation evidence

The 49 `REQ-NN` identifiers are enumerated in
`UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md`; the 549 `RR-` identifiers in
`00-MASTER/UAKOS-CLOSURE-009/requirements.json`. Both are readable at this commit.
