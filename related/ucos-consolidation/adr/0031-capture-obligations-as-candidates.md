# ADR-0031: A discussion is not captured until its obligations exist as `CANDIDATE` records

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-09-04 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | `UCKP-ART-16`, `ADR-0028` |
| Supersedes | none |

## Context

This programme produced roughly 470 obligations across a single working session. They existed
in a conversation and in published pages, neither of which is a repository trace — the same
condition `CEP-002` Article 28.5 already refuses for decisions: *"a decision whose trace is
only conversational is not recorded."*

Findings captured only in prose decay in two ways. They are never triaged, and they are
rediscovered later as new.

## Decision

An obligation is captured when it exists as a `CANDIDATE` record in the requirement authority,
**before** any judgement is made about it. Triage moves it to `ADMITTED`,
`REJECTED_DUPLICATE`, `DERIVED_CONSTRAINT` or `GOVERNANCE_ITEM` — the four states the admission
process already defines.

An untriaged candidate is a gate failure. Forgetting is thereby made structurally impossible
rather than discouraged.

## Alternatives rejected

**Capture in a tracking document.** Rejected — that document is a second requirement plane, and
producing one during triage is exactly how the existing planes came to exist.

**Capture only what survives triage.** Rejected: it makes the rejection invisible, so the same
idea returns and is re-analysed from scratch.

## Revisit conditions

- The candidate backlog grows faster than triage can process it, making the gate a permanent
  blocker. The remedy is a triage rate, not the removal of the rule.

## Consequences

Nothing discussed can be lost, because the build refuses while a candidate is untriaged. The
cost is that capture must happen in the register at the moment of discovery, not afterwards.

## Compliance

`UCKP-ART-16`: the obligation is enforced by a gate rather than by diligence. Article 28.5's
treatment of conversation-only decisions is the direct precedent.

## Validation evidence

The four admission states are declared in
`UNIVERSAL-REQUIREMENT-ADMISSION-PROCESS-DETERMINATION.md` §2.1.
