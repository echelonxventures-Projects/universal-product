# ADR-0035: Four verification lanes, and which claim each may be cited for

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-09-04 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | `UVI-000001`, `UVI-L-04`, `UVI-L-05` |
| Supersedes | none |

## Context

`verify.sh` declares four modes and each states a different claim. `--fast` reports
`coverage: NOT_EVALUATED` and prints, in its own output, that it *"is not evidence of
certification."* Despite that, a `--change` run was pasted into this programme as evidence of
repository state, and this session ran `--integration` eight times while treating W0's
`--full` exit criterion as met.

## Decision

- **`--fast`** — inner loop, impact-selected. Never cited as evidence of anything but "the
  change I just made did not break what it reaches."
- **`--change`** — commit validation. What runs before a push.
- **`--integration`** — merge validation. Whole suite under the floor plus every gate.
- **`--full`** — release certification. The only lane whose result may be called certification,
  and the only one that runs the registration observation.

A claim may never exceed the lane that produced it.

## Alternatives rejected

**One lane for everything.** Rejected: an 18-minute inner loop is not used, and a lane nobody
runs verifies nothing.

**Let developers choose per change.** Rejected — that is the status quo, and it produced a
`--change` run being cited as repository truth.

## Revisit conditions

- The impact selector's escalation rules change such that `--change` and `--integration` no
  longer differ materially, at which point three lanes would be enough.

## Consequences

Every citation of a verification result carries the lane that produced it. `--full` becomes a
deliberate act rather than an assumed one.

## Compliance

`UVI-L-05` already refuses any mode that claims more than it measures; this decision states the
consumer-side obligation that matches it. `UVI-L-04` holds the pre-existing stage set as a
ratchet, so no lane may quietly drop a stage.

## Validation evidence

Measured this session: nine verification runs, of which one was `--full` and it failed; every
subsequent green was `--integration`. The exit criterion for W0 names `--full`, and treating
`--integration` as equivalent is exactly the substitution this decision forbids.
