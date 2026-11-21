# ADR-0027: Mutation classification admits AUTHORED_DOCUMENT as its eighth class

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-08-21 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | `UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md` (REQ-39), UCOS-CL-016, UCKP-LAW-0001 |
| Supersedes | none — closes REQ-39, a gap discovered independently of `adr/0019`/`WP-UCDA-028`. **Correction, stated plainly:** this decision's first draft incorrectly described REQ-39 as one of `WP-UCDA-028`'s six sub-obligations; `adr/0019`'s own list (`P4-F-001, 004, 005, 006, 007-remainder, 008, 009-remainder`) names no mutation-classification finding. REQ-39 was found separately, during the requirement-index compilation pass, and is dispositioned here on its own governance basis — not as a discharge of `WP-UCDA-028` |

## Context

`00-BOOK/DATA/mutation-governance-boundary.json` (EX-015/EX-016) declares seven ordered
classification rules over repository mutation subjects, terminating fail-closed in
`UNRESOLVED` for anything none of them claims. Its own `$conformance_is_not_claimed_here`
note, written when the section was declared, names the expected `UNRESOLVED` population at
that commit: *"root-level `*.md` including the Master Implementation Plan artifacts."*

Measured directly this session: every constitution (`00-CEP/*.md`), every ADR this
programme has produced (`adr/*.md`), and every determination/assessment/report document
this session's own work has authored resolves to that terminal — `platform.
repository_intelligence.mutation_classification.classify()` confirms it (see Validation
evidence). These are tracked, authored, self-attributing governance documents, not
unclassified artifacts — the same shape of gap `GOVERNED_DECLARATION` (Class 6, `ADR-0011`
lineage) closed for JSON declarations, still open for prose.

## Decision

We **implement** a new class, `AUTHORED_DOCUMENT`, and its rule `R-08` (precedence 8, the
last rule before the terminal):

1. `00-BOOK/DATA/mutation-governance-boundary.json` — a new `mutation_classes` entry
   declaring five membership criteria (markdown, authored, repository-controlled,
   non-generated, self-declared-authority) and a new `classification_rules.rules` entry,
   `R-08`, evaluated in the same ordered-precedence, first-match scheme as `R-01`–`R-07`.
2. `platform/repository_intelligence/mutation_classification.py` — `_r08_authored_document`
   (registered in the two-sided `RULE_PREDICATES` map exactly like every other rule),
   `authored_document_checks()` (mirrors `governed_declaration_checks()`'s per-criterion
   shape — evidence generation), `authored_document_owner()` (canonical-owner resolution:
   reads the document's own self-declared `Authority` or `Deciders` field, checked in that
   priority order — both are real, observed conventions, `Authority` for constitutions and
   determination/assessment reports, `Deciders` for ADRs), and
   `authored_document_lifecycle()` (reads the document's own self-declared `Status` field,
   open vocabulary, never coerced into a closed set the class does not declare).

`governed_by` is owner-parameterised, the identical pattern `GOVERNED_DECLARATION` already
uses and for the identical reason: an ADR's `Deciders` and a constitution's `Authority` are
each self-declared by the artifact, not shared, and `CEP-009 I.3` keeps that authority
single per lineage. `AUTHORED_DOCUMENT` grants mutation ownership only — no certification,
ratification or freeze authority, the same `CEP-009 I.1` reservation Class 6 states.

**No new mutation authority, registry or governance model is created.** `R-06`
(`GOVERNED_DECLARATION`) precedes `R-08` and a JSON path never satisfies `R-08`'s markdown
criterion, so the two classes are structurally disjoint — confirmed by test, not merely
argued. Ownership resolution reuses the existing `Repository` view (`tracked`, `generated`,
`producer_homes`) unchanged; only one new accessor, `text_of()`, was added to read a
subject's own content, mirroring `declaration_document()`'s existing shape for JSON.

## Consequences

Positive: every constitution, ADR, decision document, determination report and assessment
report this programme produces now resolves to a named, evidenced mutation class instead of
the fail-closed terminal — including every ADR this session registered as a `DEC-ADR-*`
decision. Ownership and lifecycle are queryable per-document without inventing a second
prose-parsing subsystem elsewhere.

Neutral: a document that declares neither `Authority` nor `Deciders` in its opening metadata
(e.g. `adr/0002`, which states `AUTHORITY = NONE (derived truth)` as inline prose rather than
a self-declared field) correctly remains `UNRESOLVED` — this is fail-closed working as
declared, not a gap `R-08` was meant to close.

Negative: none identified for the implemented scope. The predicate reads only the first 40
lines of a document; a self-declaration placed later in a very long document would not be
found — an explicit, bounded design choice (every observed convention declares it
immediately after the title), not a silent limitation.

Reversible: one new class entry, one new rule entry, four new functions, all additive;
removing `R-08` from both the register and `RULE_PREDICATES` fully reverts affected
documents to `UNRESOLVED`, their prior state.

## Compliance

- [x] Non-contradiction with the constitutional/EES corpus asserted (CC-02) — no new
      authority; the mutation boundary remains "DATA ONLY", `UCKP-LAW-0001` subordinate,
      exactly as declared.
- [x] Rollback / migration path recorded (CC-04) — see Consequences.
- [x] Traceability links to affected artifacts recorded (CC-05) — `adr/0019`,
      `00-BOOK/DATA/mutation-governance-boundary.json`,
      `platform/repository_intelligence/mutation_classification.py`,
      `platform/tests/test_mutation_classification.py`.
- [x] No secret material embedded (SEC-04).

## Validation evidence

- `platform/tests/test_mutation_classification.py` — 53 tests (13 new for Class 7):
  authored-document classification via both self-declaration conventions (ADR `Deciders`,
  constitution `Authority`), ownership resolution, authority (governance-chain) resolution,
  lifecycle resolution, per-criterion evidence generation, fail-closed refusal for a document
  declaring neither field, structural exclusivity from `GOVERNED_DECLARATION` and `SOURCE`,
  untracked-document refusal, and no-duplicate-mutation-authority between Class 6 and Class
  7. All passing.
- `platform/tests/test_mutation_governance_boundary.py` — 9 tests, including
  `test_2_no_class_is_claimed_by_two_authorities_as_primary`, re-exercised against the
  now-eight-class register. All passing.
- Direct classification of real tracked files confirmed the two conventions and the
  fail-closed edge case: `adr/0003-constitutional-binding-of-ceu-and-ucxi.md` →
  `AUTHORED_DOCUMENT` via `Deciders`; `00-CEP/CEP-002-CONSTITUTIONAL-GOVERNANCE-CONSTITUTION.md`
  → `AUTHORED_DOCUMENT` via `AUTHORITY` (case-insensitive); `adr/0002-aeos-phase-1-architectural-determination.md`
  → `UNRESOLVED` (states `AUTHORITY = NONE` as prose, not a self-declared field).
