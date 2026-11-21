# ADR-0001: EC-1 Foundation technology stack

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-07-16 |
| Deciders | EC-1 Platform Engineering |
| Technology Constitution refs | TP-04, TP-05, DE-01, DE-04, CD-01, CD-04, PL-02 |
| Supersedes | none |

## Context

EPIC-001 requires an executable foundation for the EC-1 engine (IMP-001). The
Technology Constitution mandates a vendor-neutral core (TP-04), the least
sufficient technology (TP-05), reproducible builds from pinned dependencies
(DE-01, DE-04), shared conventions and secure coding (CD-01, CD-04), and
observability by default (PL-02). The existing UKB/UMB runtime substrate
(`00-BOOK/tools/*.py`) is Python 3.12+, so a Python foundation reuses that
substrate rather than introducing a second toolchain.

## Decision

We will implement the Foundation layer in **Python (>= 3.12) using the standard
library only for runtime code**. Development tooling is pinned to exact versions:
`pytest==8.3.4`, `pytest-cov==6.0.0`, `ruff==0.8.4` (lint + `S` security rules),
and `build==1.2.2` for packaging. Coverage is gated at a 90% minimum. The
project is additive engineering code rooted at `/engine`; the certified corpus
(`00-BOOK`, `00-SOURCE`, `99-FREEZE`) remains read-only and is enforced by the
frozen-path guard (TASK-000003).

## Consequences

- Positive: zero runtime third-party dependencies (minimal supply-chain / attack
  surface, TP-05, SEC-01); reuses the existing Python substrate; fully
  reproducible (DE-01).
- Neutral: dev-only tools are pinned and vetted (DE-04); upgrades require an ADR.
- Reversibility: the foundation exposes versioned contracts (TASK-000008);
  swapping a dev tool is a config-only change with no runtime impact (CC-04).
- Exit path (TP-04): no proprietary core dependency is introduced; all runtime
  behavior rests on CPython stdlib.

## Compliance

- [x] Non-contradiction with the constitutional/EES corpus asserted (CC-02).
- [x] Rollback / migration path recorded (CC-04).
- [x] Traceability links to affected artifacts recorded (CC-05): IMP-001, IMP-000
      Technology Constitution.
- [x] No secret material embedded (SEC-04).
