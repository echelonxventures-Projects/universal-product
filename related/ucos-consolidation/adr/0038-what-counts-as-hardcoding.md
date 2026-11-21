# ADR-0038: The three-part hardcoding test, and a closed five-item kernel residue

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-09-04 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | `UCKP-ART-08`, `UCKP-ART-17`, `UCPA-000001` |
| Supersedes | none |

## Context

"No hardcoding" is a direction everyone agrees with and nobody can enforce, because two
engineers will disagree about whether a given literal counts.

The repository already wrote the test down, in one module.
`engine/omega_governance/reference/domain.py` states: *"NOTHING IN THIS CLASS BRANCHES ON A
DOMAIN NAME. There is no `if name == \"TIME\"`"* — and of its fourteen shipped domains,
*"nothing quantifies over it, validates against it, or requires membership in it."*

Measured baseline at this commit: 346 behaviour-deciding string comparisons, 87 literal
membership sets, 85 repository paths in code, 32 numeric thresholds — roughly 550 candidates
before triage.

## Decision

A literal in code is **not** hardcoding when all three hold:

1. nothing branches on it;
2. it can be replaced by registration;
3. its presence is declared.

A literal passing all three is a shipped default. One failing any is hardcoding, and countable.

**The kernel residue is closed at five items**: the entry point, the canonical form, the
bootstrap reader, the law's own text, and the axiom. Adding to it requires a decision record.

## Alternatives rejected

**Target literal zero.** Rejected as unattainable: something must be typed, parsed and trusted
first. `UCPA-000001` already handles this shape by declaring `BEING` an axiom that is
deliberately *not an addressable layer*; the residue is the same treatment.

**Ban new literals without measuring existing ones.** Rejected: a rule with no baseline cannot
ratchet, and the 550 would stay invisible.

## Revisit conditions

- A sixth irreducible is discovered. The Python runtime was proposed as one during this
  session and withdrawn: `UEG-000001` declares the full runtime group with a named
  `series_authority` and `pin_authority`, so it is governed rather than residual.

## Consequences

"Zero hardcoding" becomes measurable: zero *undeclared* hardcoding over a residue that can only
shrink. Unproven claims convert into declared absences, which is progress rather than retreat.

## Compliance

`UCKP-ART-08` (automatic discovery) and `ART-17` (universal compatibility) both require that a
new category enter by registration; a literal that decides behaviour is what prevents that.

## Validation evidence

Baseline measured at this commit over `engine`, `platform`, `intelligence`, `infrastructure`
and `service`, excluding tests. The good pattern is `engine/omega_governance/reference/`; the
templates for each fix class are `DomainRegistry`, `engine/uckp/vocabulary.py` and the coverage
floor's existing declaration.
