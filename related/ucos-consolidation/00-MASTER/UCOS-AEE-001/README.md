# UCOS-AEE-001 — Autonomous Evolution Engine

| Field | Value |
|---|---|
| AUTHORITY | `NONE — DERIVED TRUTH` |
| DECLARATION | `aee-declaration.json` — the only place anything is stated |
| ENGINE | `aee_engine.py` — stdlib only, names no declared identifier |
| REGENERATE | `make aee` |
| ENFORCE | `make aee-gate` · `.github/workflows/aee-gate.yml` |
| SELF-GUARDS | `make aee-self` |

## What this programme is

The closed loop, and nothing else.

Every phase of the evolution loop already has a located, certified owner in this
repository. This programme creates none of them — no validator, no gate, no registry, no
schema, no measurement, no certification. What no located programme owned is the loop
itself: every entry point in this repository is a one-shot process, so nothing
re-executed the located owners, re-read their sealed determinations, compared consecutive
readings, and asserted a fixed point over what they report.

It **actuates** located owners so they regenerate their own determinations, **observes**
those determinations through declared pointers, **classifies** and **decides** every
divergence from declared rules, and **iterates** until consecutive readings agree.

## What it does not do

It does not assert byte-level repository closure. That condition belongs to
`UCOS-RFP-001`, requires a clean committed tree to begin, and runs the aggregate
certifier as one of its own pipeline stages — so a driver that emits artifacts cannot
assert it, and a driver that invoked the fixed-point engine would rebuild the recursion
topology that engine exists to forbid. Convergence here is over the **observation
vector**; closure remains `make rfp-gate`. Recorded as finding `AEE-F-002`.

It does not run as a resident process. No daemon, scheduler or armed session hook exists
anywhere in this repository, and the hooks that once did were deliberately disarmed.
Cadence is continuous integration on every push, plus operator invocation. Recorded as
finding `AEE-F-003`.

## Knowledge Once

The loop's phases are not restated here. They are READ at run time from the declarations
that already own them, and `--check-mandate-coverage` fails closed if a bound phase does
not resolve in its source or if any phase is discharged by nothing. A phase appended to a
source is discovered on the next run with no edit to this programme.

## Extension

Adding an actuator, an observation, a classification rule, a decision value, a
precondition or a convergence criterion is an append-only edit to
`aee-declaration.json`. The engine, the Makefile and the workflow never change —
`--check-no-enumeration` proves it by failing if any declared identifier or owner path
appears as a literal in the engine source.
