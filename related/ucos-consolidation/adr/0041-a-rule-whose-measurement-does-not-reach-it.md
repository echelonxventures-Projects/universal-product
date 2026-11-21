# ADR-0041: A rule is not enforced by being right — six instances of a measurement that did not reach

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-09-04 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | `UCKP-ART-15`, `UCKP-ART-16`, `adr/0021`, `adr/0030` |
| Supersedes | none |

## Context

Six defects found in one session shared a shape that none of them announced. In every case a rule
was correct, an instrument existed, and a verdict was being reported — and the measurement behind
the verdict did not reach where the rule applied. None of the six was a wrong rule. None was a
broken engine. Each was a gap between what an instrument *said* and what it had actually looked at.

**One — `adr/0039`'s version-control inference.** The ADR read "20 non-test modules invoke `git`
directly against 2 that use the git provider" as evidence the provider is bypassed, and leaned on
that ratio to declare the axis git-bound. `DiscoveryProvider` answers one question. Split by the
question each module asks: 15 invoke `ls-files` and are genuine bypasses; the rest ask `status`,
`archive`, `rev-parse`, `log`, `diff`, `check-ignore` — questions no provider protocol covers. The
ratio measured the provider's scope, not anyone's compliance. The disposition survived on other
grounds; the stated reason did not.

**Two — the impact selector's escalation reason.** It reported "no dependency edges exist for this
file type" about a file registered as `UCOS-ENG-000023` with an explicitly empty dependency list,
among 172 registered `.json` objects. The claim was asserted before the registry was consulted at
all. The verdict — escalate to FULL — was right; the mechanism named was fictional.

**Three — `CAA-INV-05`'s scope.** CAA rules that a projection *"may never declare a relationship
KIND that names no class in the model above it"*. `engine/graph` emitted 26 kinds, CAA bound six,
the overlap was zero, and the invariant passed — because it read the kinds of one graph, the UGA
relationship projection, and never reached the other surface the rule plainly covers.

**Four — the split table's silent fallback.** Shard splitting is hash-gated and correctly falls back
to whole-file placement when an object's content moves. Nothing reported the fallback. The
second-most-expensive object in the suite was placed whole for four commits, and it surfaced because
a wave felt slow and someone asked why.

**Five — `adr/0021` itself.** UAP-001 states the agnosticism principle and discloses that nothing
enforces it. Honest, and unenforced for fourteen days.

**Six — the execution axis.** `verify_execution_interchangeable` passes over ten technologies that
share one body, behind a contract demanding only a serialisation. A conformance test that cannot
fail.

## Decision

The class is named: **a rule whose measurement does not reach it**. It is distinct from silent
drift (`INV-SIL-01…03`), which concerns a *change* nobody observed. This concerns a *scope* nobody
stated: an instrument that reports on a population narrower than the rule it enforces, while
reading as though it covered the rule.

Three obligations follow, and they are stated as obligations on future instruments rather than as a
new gate, because a gate for this would itself need a scope and would inherit the same defect.

**An instrument states the population it measured.** `CAA-INV-05` reported `measured=6` while the
rule covered 32. A count is not the population; naming what was counted is what makes a scope
auditable. Where a rule names a class of subjects, the instrument reports which subjects it reached.

**A verdict names the mechanism it rests on, and only a measured one.** The selector's escalation
and `adr/0039`'s inference were both right by accident and wrong by mechanism. A reason nobody
measured is worse than no reason, because a later reader spends the reason as evidence.

**A silent fallback is reported.** Not gated — the split table's fallback makes a plan slower and
never wrong, and refusing it would contradict its own authority text. But an instrument that
quietly degrades and reads identically is indistinguishable from one that did not degrade.

## Alternatives rejected

**Add a fourth `INV-SIL` invariant.** Rejected: silent drift is a change nobody observed, and this
is a scope nobody stated. Collapsing them would merge two questions into one answer — the
meaning-collapse the architecture determination forbids (P-2) — and the merged invariant would
answer neither well.

**Build a meta-gate that measures whether measurements reach their rules.** Rejected as currently
unbuildable and probably unbuildable in principle: it would need to know each rule's intended
population independently of the instrument that implements it, which is a second declaration of the
rule and therefore a rival authority (`UCKP-ART-03`).

**Treat the six as unrelated bugs.** Rejected on the evidence. Six instances in one session, found
by six different routes, none by the instrument responsible. The recurrence is the finding.

## Revisit conditions

- A seventh instance is found, which would argue the obligations above are insufficient and that a
  mechanical check is worth attempting after all.
- An instrument is built whose scope is derived from the rule's own declaration rather than written
  beside it, which would make the class structurally impossible for that instrument and worth
  generalising.

## Consequences

Positive: the class has a name and six worked examples, so the next instance is recognisable rather
than surprising. Every one of the six cost a separate discovery.

Negative, and disclosed: this ADR creates no gate and nothing checks conformance to it — which is
precisely the disclosure `adr/0021` made about itself, and which took fourteen days and a purpose-
built harness to close. Recording that symmetry is deliberate: this document is subject to its own
finding, and saying so is the only honest form it can take.

## Compliance

- `UCKP-ART-15` requires every finding to be derived from the declared universe rather than a
  hardcoded assumption; the six instances are each a case where a derivation ran over the wrong
  universe.
- `UCKP-ART-16` requires governance decisions to be auditable and traceable; an instrument reporting
  a scope it did not measure is traceable to the wrong thing.
- No authority is created and no existing invariant is amended.

## Validation evidence

Instances one, two and four are recorded in commits `5fa9afb4` and the cost-model commit; instance
three in `3dd92566`, where `CAA-INV-05` moved from `measured=6` to `measured=32`; instances five and
six in `bb0012d8`, where `engine/conformance` first reported `ENVELOPE_ONLY` for an axis that had
been passing an interchangeability test over ten technologies sharing one body.
