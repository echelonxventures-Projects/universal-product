# ADR-013: CEL as the single expression language

| Field | Value |
|---|---|
| Status | Accepted (A-22) |
| Deciders | Architecture Board (U01 root authority) |
| References | U04 Meta; U53 Decision; U03 Policy |

## Context
Constraints, decision-table cells, workflow guards, notification conditions and earn rules all need expressions. Several languages would split tooling and security review.

## Decision
**Common Expression Language (CEL)** is the only expression language in definitions: it is non-Turing-complete, has linear-time evaluation, is type-checked and has Go/Java/TS implementations. Cedar remains the authorisation language (ADR-005), and Datalog the composition language (ADR-006). These are distinct concerns, not general expression languages.

## Alternatives considered
- JavaScript snippets: Turing-complete and a security risk.
- JSONLogic: weak typing and tooling.
- FEEL (DMN): good for decision tables, but less common outside DMN tooling. A FEEL-to-CEL import is possible.

## Consequences
**Positive**
- Safe to evaluate tenant-authored expressions.
- One editor, linter and test harness.

**Negative / costs**
- DMN imports need FEEL translation.

## Enforcement
U04 lint rejects non-CEL expressions; evaluation cost limits.
