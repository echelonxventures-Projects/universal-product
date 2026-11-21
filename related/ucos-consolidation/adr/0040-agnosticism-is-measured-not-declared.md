# ADR-0040: Agnosticism is measured, and a contract that cannot fail proves nothing

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-09-04 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | `UCKP-ART-09`, `UCKP-ART-10`, `UCKP-ART-17`, `adr/0021`, `adr/0039` |
| Supersedes | none |

## Context

`adr/0021` (UAP-001) states the Universal Agnostic Architecture Principle and then discloses, in
its own Consequences section: *"a principle with no enforcement mechanism can be ignored without
consequence. This is disclosed rather than hidden — no gate, invariant, or certification currently
checks conformance to this statement, and none is created by this document."*

That was written on 2026-08-21 and remained true until this decision. `adr/0039` later scored
fourteen axes by hand against a bar — *an abstraction with one implementation is an assumption; an
abstraction its own callers bypass is decoration* — which established the bar and left the scoring
unrepeatable, performed once by reading code.

Measured while building the mechanism: `engine/uckp/execution.py` declares ten execution
technologies and `verify_execution_interchangeable` passes over all ten. It cannot do otherwise.
Nine inherit one `transcribe()` returning identical canonical JSON with a different comment line,
and `ExecutionAdapter.execute()` discards the payload and calls `resolve_operation` in Python
regardless. Ten names, one implementation, and a green test that confirms a thing equals itself.

## Decision

Agnosticism is a measurement, taken by `UAC-000001` (`engine/conformance`), and an axis is scored
on **two** properties because one over-reports.

**Distinctness** — how many declared implementations define the contract's own abstract methods
rather than inheriting a sibling's body. Persistence scores 10 of 10; execution scores 2 of 11.

**Whether the contract can fail** — whether it demands an answer a placeholder could not give.
`PersistenceAdapter` requires `write()` then `read()` and compares universe digests, so a mechanism
that stores nothing is refused. `ExecutionAdapter` requires only `transcribe()`, a serialisation, so
a mechanism that computes nothing passes.

Four dispositions: `PROVEN`, `SINGLE`, `ENVELOPE_ONLY`, `DECLARED_ABSENT` (under `adr/0030`).

The harness names no technology, discovers implementations rather than reading a roster
(`UCKP-ART-08`), never reads a disposition, and admits a new axis by an appended register entry
(`UCKP-ART-17`). It resolves contracts from `sys.modules` and imports nothing, so the caller loads
what it asks about.

**It measures and refuses nothing.** Whether `ENVELOPE_ONLY` becomes a refusal is a separate
decision, deliberately not taken here.

## Alternatives rejected

**A conformance suite per axis.** Rejected: a suite per axis names a technology per suite, which is
the hardcoding the principle forbids. One harness over a declared register keeps the instrument
neutral and makes a new axis an appended entry rather than new code.

**Score on implementation count alone.** Rejected by measurement. Across the repository 42
abstraction boundaries exist and 20 carry two or more distinct implementations — but most are *rule
registries* (21 validation rules, 20 acceptance gates), where swapping an implementation changes
which rule runs, not which technology runs it. A first pass of this measurement made exactly that
error and scored the execution axis healthy.

**Let the register declare dispositions.** Rejected: a register that could declare an axis proven
would reproduce the defect this instrument exists to catch, and `adr/0039`'s hand scoring is the
evidence that a written verdict goes stale the moment it is written.

**Make it a gate immediately.** Rejected for now, and recorded as an open decision rather than a
preference. `adr/0021` refuses to *"retroactively certify any dimension"* and warns against
*"building an abstraction merely to satisfy a checklist"*; an instrument whose first act failed the
build would be doing the second thing. The gate is a real change to `ExecutionAdapter`'s contract,
not a setting.

## Revisit conditions

- `ExecutionAdapter` acquires a contract demanding a computed answer, at which point the execution
  axis becomes measurable and its disposition may move off `ENVELOPE_ONLY`.
- Any axis moves between dispositions, which should be recorded as a movement rather than a silent
  upgrade.
- A second interpreter passes the axes, which would move the runtime axis from assumed to proven —
  the environment already carries one, so this is nearer than `adr/0039` recorded.

## Consequences

The repository can state its agnosticism as a measurement rather than an intention, and the first
statement contradicts a surface that currently reports green. That is the instrument working.

Negative, and disclosed: `ENVELOPE_ONLY` is visible and still lawful. Nine adapters answering no
computation remain conformant, and a tenth costs nothing to add until the open decision is taken.

## Compliance

- `UCKP-ART-09` and `UCKP-ART-10` require one contract per mechanism; this measures which of them
  have more than one implementation of that contract and says so rather than implying it.
- `UCKP-ART-17` is served by the register: a new axis is admitted by registration, never amendment.
- `UCKP-ART-08` is served by discovery: implementations are found, not listed.
- No authority is created. `engine/conformance` declares `authority: NONE — DERIVED TRUTH` and
  changes no test's pass/fail state.

## Validation evidence

`make conformance` and `engine/tests/conformance/test_agnosticism_conformance.py`, six tests. Two
guard the design rather than the output: one asserts the harness names no technology in its body,
because an instrument measuring hardcoding may not hardcode what it measures; another asserts that
distinctness alone would have scored execution `PROVEN`, so the second property cannot be dropped
later without the suite noticing. Landed under `P-UCOS-UGA-005` and `P-UCOS-UGA-006` at commit
`bb0012d8`.
