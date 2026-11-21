# ADR-036: Continuous integration is deterministic and needs no person or AI to run

| Field | Value |
|---|---|
| Status | Accepted |
| Deciders | Architecture Board (U01 root authority) |
| References | tools/ci.sh; .github/workflows/; ADR-018 |

## Context
The specification is checked by tools, and generated files must stay in sync. If CI depends on someone running generators, an AI agent, or tools that change silently, the repository drifts.

## Decision
One entry point, **`tools/ci.sh`**, runs every check with **pinned tools** (hash-locked Python packages, pinned Node packages, GitHub Actions pinned by commit SHA). It makes **no network calls to AI services** and uses no secrets. Pull requests fail when generated files are stale. Pushes to `main` regenerate and commit generated files with the CI bot, then verify. A nightly run catches toolchain drift. Tagged releases build the site and PDF automatically. Dependabot proposes tool updates, which pass the same checks.

## Alternatives considered
- Run checks manually before release: depends on people.
- Let an AI agent fix CI failures: non-deterministic and unauditable.

## Consequences
**Positive**
- The same command gives the same result on a laptop and in CI.
- No hidden state: everything CI needs is in the repository.

**Negative / costs**
- Updating a pinned tool is a deliberate change.

## Enforcement
`.github/workflows/ci.yml` required on `main`; the CI self-test fixtures must fail as expected.
