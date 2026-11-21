# ADR-0039: Fourteen agnosticism axes, each proven, abstracted, bypassed or declared absent

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-09-04 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | `UCKP-ART-09`, `UCKP-ART-10`, `UCKP-ART-20` |
| Supersedes | none |

## Context

Agnosticism is declared across the corpus and was never measured. Measured this session against
one bar — *an abstraction with one implementation is an assumption; an abstraction its own
callers bypass is decoration* — fourteen axes score: 2 proven, 4 abstracted, 4 bypassed,
4 hardcoded.

Concrete findings: 1,732 direct `sha256` call sites against a crypto-agility registry that
governs almost none of them; `DeploymentDescriptor.kubernetes` is a typed field rather than a
provider; and there is no numeric-system reference domain.

On version control the first measurement was 20 non-test modules invoking `git` as a subprocess
against 2 that use `engine/omega_infinite/git_provider.py`, and that ratio was read as evidence
that the provider is bypassed. **It is not evidence of that, and the re-measurement below is why.**
`DiscoveryProvider` answers exactly one question — enumerate the artifacts a selector admits —
and the provider says so itself: *"One question only."* Splitting the 20 by the question they
actually ask gives 15 modules invoking `git ls-files`, which *is* that question and therefore *is*
a bypass. The remaining invocations — `status` (19 sites), `archive` (8), `rev-parse` (5),
`log` (4), `diff` (3), `check-ignore` (2) — ask questions no provider protocol covers, so there
is nothing there for them to bypass. A ratio that counts both populations together measures the
provider's *scope*, not anyone's compliance with it.

## Decision

Each axis carries a disposition, and four become `DECLARED_ABSENT` under `ADR-0030` rather than
remaining unproven claims:

- **human language** — no message catalogue exists and determinism forces `LC_ALL=C`;
- **infrastructure** — Kubernetes is in the data model;
- **numerics** — no numeric-system domain is registered;
- **OS/shell** — POSIX is assumed by every entry point.

**Version control** is declared git-bound, and the reason is constitutional rather than
numerical: `git ls-files` *is* the eligibility boundary that decides which paths are governed at
all, and `git archive` *defines* pristine-clone certification. Substituting a VCS is therefore
three constitutional redefinitions rather than an adapter swap. The call-site ratio is expressly
**not** part of this reasoning — 15 enumeration bypasses are a closable gap that would leave the
disposition exactly where it stands, because the binding is in what those two commands *mean* to
the constitution, not in how many modules happen to call them.

The remaining axes keep their measured status and close by acquiring a second implementation.

## Alternatives rejected

**Claim the axes and defer proof.** Rejected — an unproven claim is what generates the next
audit, and this ADR exists because one did.

**Drop the agnosticism goal.** Rejected: the axes that are proven — time and measurement — are
genuinely proven, and the property is the architecture's point.

## Revisit conditions

- A second implementation lands on any axis, which moves it from abstracted to proven and
  should be recorded as a movement rather than a silent upgrade.
- The 15 `git ls-files` call sites route through `DiscoveryProvider`, or the provider protocol
  grows a second question (working-tree state, or archive export) and the split above is
  re-measured against the widened scope. Neither moves the disposition on its own; both change
  what the axis costs to revisit.
- The interpreter moves to a version where `sys.monitoring` can measure branches, which would
  reopen the coverage-provider axis that is currently blocked.

## Consequences

Four axes stop being claimed and start being citable. `CoverageProvider` becomes a concrete
declared absence rather than a theoretical gap: `COVERAGE_CORE=sysmon` is silently ignored at
the current pins because `sys.monitoring` cannot measure branches before Python 3.14, which is
one implementation's constraint presenting as the system's ceiling.

## Compliance

`ART-09` (persistence abstraction) and `ART-10` (execution abstraction) require one contract
per mechanism; this decision records which of them currently have one implementation and says
so rather than implying otherwise. `ART-20` (perpetual validity) is served by declaring the
absences, since an undeclared assumption is what fails first when the environment moves.

## Validation evidence

Counts measured at this commit by direct search over `engine`, `platform`, `intelligence`,
`infrastructure` and `service`, excluding tests. The version-control split is measured twice: 20
modules that both name `git` and invoke a subprocess, then the 15 of those that pass `ls-files`,
with subcommand frequencies counted over the same population. The provider's declared scope is
read from its own module docstring rather than inferred from its callers. The `sysmon` constraint is read directly from
`coverage/core.py`: `branch_right_left = pep669 and (PYVERSION > (3, 14, 0, "alpha", 5, 0))`.
