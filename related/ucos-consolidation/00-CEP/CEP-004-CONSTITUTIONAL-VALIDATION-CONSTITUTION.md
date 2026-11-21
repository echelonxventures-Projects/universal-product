# UCOS Ω∞ — CONSTITUTIONAL VALIDATION CONSTITUTION

| Field | Value |
|-------|-------|
| ARTIFACT ID | CEP-004 |
| ARTIFACT | UCOS Ω∞ Constitutional Validation Constitution |
| CLASSIFICATION | Constitutional Engineering Program (CEP) — Validation Constitution |
| STATUS | RATIFIED (program-governance level) · NORMATIVE · LIVING-UNTIL-FROZEN |
| STAGE | Stage 01 · Prompt 06 |
| VERSION | 1.0 |
| DERIVES AUTHORITY FROM | CEP-000 (Charter), CEP-001 (Constitution), CEP-002 (Governance), CEP-003 (Execution) |
| AUTHORITY | Supreme over all validation operation of the Program; subordinate to CEP-000, CEP-001, CEP-002, and CEP-003 |
| SCOPE OF GOVERNANCE | HOW validation operates — validation only |
| CANONICAL FORM | This Markdown file |
| CONFLICT RULE | This instrument governs all validation operation. Where it conflicts with CEP-003, CEP-002, CEP-001, or CEP-000, the higher instrument governs in that order. |

> This document is normative constitutional law legislating validation only. It inherits and references CEP-000, CEP-001, CEP-002, and CEP-003 and SHALL NOT rewrite, duplicate, or restate them. It SHALL NOT legislate governance, execution, certification, ratification, evidence content, implementation, or repository content; those are reserved to their respective constitutions.

---

## PREAMBLE

P.1 This instrument IS the permanent constitutional validation instrument of the UCOS Ω∞ Constitutional Engineering Program.

P.2 Validation SHALL be the act of verifying that an artifact or stage satisfies its defined criteria; validation SHALL verify and SHALL confer nothing.

P.3 This instrument refines the general Validation Model of CEP-001 Article XI and the validation principles of CEP-000 §26, and SHALL remain consistent with both.

P.4 This instrument SHALL bind every validation act of the Program until amended or frozen under its own rules.

---

## ARTICLE I — VALIDATION AUTHORITY

I.1 Validation Authority SHALL be the authority to verify that criteria hold at a gate and to declare a gate PASS or BLOCKED.

I.2 Validation Authority SHALL introduce no content, confer no status beyond a verification verdict, and decide no constitutional content.

I.3 Validation Authority SHALL NOT govern, execute, certify, ratify, or legislate evidence content.

I.4 Validation Authority SHALL NEVER convert a BLOCKED verdict to PASS other than through remediation and revalidation under this instrument.

---

## ARTICLE II — VALIDATION SCOPE

II.1 This instrument SHALL legislate validation authority, responsibilities, lifecycle, gates, criteria, completeness, correctness, consistency, integrity, determinism, dependencies, sequencing, authorization, permissions, checkpoints, failure, remediation, revalidation, closure, enforcement, and the audit interface.

II.2 This instrument SHALL NOT legislate governance, execution, certification, ratification, evidence content, implementation, or repository content.

II.3 Validation SHALL be non-mutating; it SHALL read the subject and its bound evidence and SHALL write only validation records.

II.4 A verdict issued outside a defined gate IS PROHIBITED and SHALL be void.

---

## ARTICLE III — VALIDATION LIFECYCLE

III.1 The validation states SHALL be: PENDING, EVALUATING, PASS, BLOCKED, REMEDIATING, REVALIDATING, CLOSED.

III.2 The initial validation state SHALL be PENDING; the terminal validation state SHALL be CLOSED.

III.3 The legal validation transitions SHALL be exactly:
- PENDING → EVALUATING.
- EVALUATING → PASS.
- EVALUATING → BLOCKED.
- PASS → CLOSED.
- BLOCKED → REMEDIATING.
- REMEDIATING → REVALIDATING.
- REVALIDATING → PASS.
- REVALIDATING → BLOCKED.

III.4 Any transition not enumerated in III.3 IS PROHIBITED and SHALL be treated as an illegal transition that places the Program in HALTED.

III.5 Every validation state SHALL be defined; an undefined validation state IS PROHIBITED. Every non-terminal state SHALL have at least one defined outgoing transition, and every state SHALL be reachable from PENDING.

III.6 A CLOSED verdict SHALL be reopened only by a new validation cycle triggered by amendment under CEP-001 Article XV.

---

## ARTICLE IV — VALIDATION GATES

IV.1 A validation gate SHALL be the control at which validation criteria are evaluated and a verdict is issued.

IV.2 Every gate SHALL have a defined, complete set of applicable criteria; a gate without defined criteria IS PROHIBITED.

IV.3 A gate SHALL yield exactly one verdict: PASS when all applicable blocking criteria are satisfied, otherwise BLOCKED.

IV.4 A non-blocking observation MAY be recorded separately and SHALL NEVER convert a BLOCKED verdict to PASS (per CEP-000 §26.5).

IV.5 No stage SHALL progress through a gate whose verdict is not PASS.

---

## ARTICLE V — VALIDATION CRITERIA

V.1 The validation criteria SHALL comprise completeness, correctness, consistency, integrity, determinism, traceability closure, evidence-binding, preservation, and scope conformance, as established by CEP-000 §26 and CEP-001 Article XI.

V.2 Every criterion SHALL be machine-verifiable and SHALL resolve to a decidable satisfied-or-unsatisfied result.

V.3 Criteria SHALL NOT conflict; two criteria SHALL NOT require mutually exclusive conditions. A discovered conflict SHALL place the Program in HALTED until resolved under CEP-002 Article 23.

V.4 A criterion that cannot be verified SHALL be treated as unsatisfied until it is made verifiable.

V.5 Criteria SHALL be applied uniformly; identical subjects SHALL yield identical verdicts.

---

## ARTICLE VI — VALIDATION COMPLETENESS

VI.1 Completeness validation SHALL verify that every required deliverable of the subject exists and is non-empty.

VI.2 Completeness validation SHALL verify that the subject contains no placeholder, no unresolved marker, and no deferred obligation disguised as complete.

VI.3 A subject failing completeness SHALL yield BLOCKED.

---

## ARTICLE VII — VALIDATION CORRECTNESS

VII.1 Correctness validation SHALL verify that the subject conforms to the definition and criteria that authorize it.

VII.2 Correctness validation SHALL verify that the subject asserts nothing not bound to evidence and contradicts no ratified definition.

VII.3 A subject failing correctness SHALL yield BLOCKED.

---

## ARTICLE VIII — VALIDATION CONSISTENCY

VIII.1 Consistency validation SHALL verify that the subject contains no internal contradiction.

VIII.2 Consistency validation SHALL verify conformance to registered terminology and the absence of duplicate concept or duplicate owner.

VIII.3 A subject failing consistency SHALL yield BLOCKED.

---

## ARTICLE IX — VALIDATION INTEGRITY

IX.1 Integrity validation SHALL verify that every claim is bound to addressable evidence and that the binding is intact.

IX.2 Integrity validation SHALL verify that no frozen subject has been mutated and that the subject is additive where additivity is required (per CEP-000 §14).

IX.3 Integrity validation SHALL verify traceability rooting and closure with zero orphans, referencing CEP-001 Article XVIII.

IX.4 A subject failing integrity SHALL yield BLOCKED.

---

## ARTICLE X — VALIDATION DETERMINISM

X.1 Determinism validation SHALL verify that reproducible outputs of the subject regenerate byte-identically, referencing CEP-001 Article XX.

X.2 Determinism validation SHALL verify that the subject is content-addressed and that its address matches its content.

X.3 Validation itself SHALL be deterministic; identical inputs SHALL yield an identical verdict.

X.4 A subject failing determinism SHALL yield BLOCKED.

---

## ARTICLE XI — VALIDATION DEPENDENCIES

XI.1 Every validation dependency SHALL be declared; an undeclared dependency IS PROHIBITED.

XI.2 The validation dependency graph SHALL be acyclic; a dependency that would form a cycle IS PROHIBITED and SHALL place the Program in HALTED.

XI.3 A criterion that depends upon another SHALL NOT be evaluated until its dependency has been verified.

XI.4 A validation dependency SHALL be satisfied by reference to a verified result and SHALL NEVER be satisfied by mutating the subject.

---

## ARTICLE XII — VALIDATION SEQUENCING

XII.1 Validation SHALL be sequenced deterministically; where criteria are independent, they SHALL be ordered by a canonical, reproducible ordering.

XII.2 Validation SHALL NOT reorder a criterion ahead of a criterion it depends upon.

XII.3 Validation of a subject SHALL complete before the subject progresses through its gate.

XII.4 Validation sequencing SHALL NEVER depend on wall-clock time, arrival order, or nondeterministic identifiers.

---

## ARTICLE XIII — VALIDATION AUTHORIZATION

XIII.1 A validation SHALL be authorized only when its subject has reached the state at which validation is due under CEP-003.

XIII.2 Authorization SHALL bind the validation to exactly one subject and one gate.

XIII.3 Validation SHALL NEVER be self-waived, and a due validation SHALL NEVER be bypassed (per CEP-000 §22, CEP-001 LAW-5).

XIII.4 An unauthorized validation verdict SHALL be void.

---

## ARTICLE XIV — VALIDATION PERMISSIONS

XIV.1 Validation SHALL be permitted to read the subject and its bound evidence and to write only validation records.

XIV.2 Validation SHALL NOT write to the subject, to any constitutional corpus, or to any area outside validation records.

XIV.3 Validation SHALL NOT mutate, delete, or supersede any artifact.

XIV.4 A validation act exceeding these permissions IS PROHIBITED and SHALL be void.

---

## ARTICLE XV — VALIDATION CHECKPOINTS

XV.1 A validation checkpoint SHALL be written upon every verdict and upon entry to and exit from remediation and revalidation.

XV.2 A validation checkpoint SHALL record the subject, the gate, the applicable criteria, the verdict, and the program-state hash.

XV.3 Validation checkpoints SHALL be append-only and content-addressed and SHALL be reconciled against repository truth at boot.

XV.4 A validation checkpoint SHALL assert nothing beyond the recorded verdict.

---

## ARTICLE XVI — VALIDATION FAILURE

XVI.1 A validation SHALL fail by yielding BLOCKED when any applicable blocking criterion is unsatisfied.

XVI.2 A BLOCKED verdict SHALL place the affected progression in HALTED and SHALL emit a finding.

XVI.3 A BLOCKED subject SHALL transition only to REMEDIATING; it SHALL NOT progress through its gate.

XVI.4 A validation failure SHALL never be silently absorbed; it SHALL be recorded and routed.

---

## ARTICLE XVII — VALIDATION REMEDIATION

XVII.1 Remediation SHALL be the correction of the conditions that caused a BLOCKED verdict.

XVII.2 Remediation of non-frozen subjects SHALL correct the subject; remediation affecting frozen subjects SHALL proceed only by supersession under CEP-001 Article XV.

XVII.3 Remediation SHALL NOT alter the validation criteria to obtain a PASS.

XVII.4 Remediation SHALL transition to REVALIDATING upon completion.

---

## ARTICLE XVIII — VALIDATION REVALIDATION

XVIII.1 Revalidation SHALL re-evaluate the full set of applicable criteria against the remediated subject.

XVIII.2 Revalidation SHALL NOT carry forward any prior PASS; every criterion SHALL be re-verified.

XVIII.3 Revalidation SHALL yield PASS or BLOCKED under the same rules as initial validation.

XVIII.4 A subject amended under CEP-001 Article XV SHALL be revalidated in full before any subsequent progression.

---

## ARTICLE XIX — VALIDATION CLOSURE

XIX.1 Validation of a subject SHALL close only upon a PASS verdict.

XIX.2 Closure SHALL record the final verdict, the criteria satisfied, and the evidence referenced.

XIX.3 Closure SHALL be distinct from certification, ratification, and completion, which are reserved to their respective constitutions.

XIX.4 A closed validation SHALL be reopened only by a new validation cycle under Article III.6.

---

## ARTICLE XX — VALIDATION ENFORCEMENT

XX.1 Validation law SHALL be enforced at validation gates through the general Enforcement Model of CEP-001 Article XXIII.

XX.2 A validation violation — an illegal validation transition, an unauthorized verdict, a permission breach, a criteria conflict, or a bypassed validation — SHALL place the Program in HALTED, emit a finding, and require remediation before progression resumes.

XX.3 A void validation act SHALL have no effect and SHALL be recorded as void.

XX.4 Validation enforcement SHALL NEVER be waived, deferred, or overridden by any authority tier.

XX.5 Validation enforcement records SHALL be append-only, content-addressed, and auditable.

---

## ARTICLE XXI — VALIDATION AUDIT INTERFACE

XXI.1 Every verdict, remediation, and revalidation SHALL be recorded through the general Audit Model of CEP-001 Article XVII.

XXI.2 Validation records SHALL be sufficient to reconstruct the validation history of any subject deterministically.

XXI.3 Validation records SHALL be operational memory and SHALL NEVER enter the constitutional corpus.

XXI.4 A validation act that cannot be audited SHALL be treated as if it did not lawfully occur.

---

## ARTICLE XXII — VALIDATION SUPREMACY

XXII.1 This instrument IS supreme over all validation operation and over every subordinate validation instrument.

XXII.2 This instrument derives from CEP-000, CEP-001, CEP-002, and CEP-003 and IS subordinate to all four; conflicts resolve in favor of the higher instrument in that order.

XXII.3 This instrument SHALL NOT govern, execute, certify, ratify, or legislate evidence content or repository content.

XXII.4 This instrument SHALL bind every remaining Stage of the Program until amended or frozen under its own rules.

---

## ARTICLE XXIII — VALIDATION VERSIONING

XXIII.1 This instrument carries an explicit version; the present version IS 1.0.

XXIII.2 Any change SHALL occur only through the Amendment Model of CEP-001 Article XV and SHALL increment the version.

XXIII.3 A superseded version SHALL be retained for lineage and marked superseded; a frozen version SHALL be immutable and content-addressed.

XXIII.4 Every subordinate validation instrument SHALL cite the version of this instrument under which it was produced.

---

## ARTICLE XXIV — NORMATIVE REFERENCES

XXIV.1 CEP-000 — Constitutional Engineering Charter, §14, §15, §16, §22, §26 — the origin of the validation principles this instrument operationalizes.

XXIV.2 CEP-001 — Constitutional Engineering Constitution, Articles XI, XV, XVII, XVIII, XX, XXIII — the general validation, amendment, audit, traceability, determinism, and enforcement models this instrument refines and references.

XXIV.3 CEP-002 — Constitutional Governance Constitution, Article 23 — the conflict resolution invoked for criteria conflicts.

XXIV.4 CEP-003 — Constitutional Execution Constitution — the execution states at which validation becomes due.

XXIV.5 Where any normative reference conflicts with this instrument on validation, this instrument governs; on any other matter, the higher instrument governs.

---

## ARTICLE XXV — CONSTITUTIONAL CONCLUSION

XXV.1 This instrument IS the supreme validation law of the Constitutional Engineering Program.

XXV.2 Every validation act SHALL derive from, comply with, and remain consistent with this instrument and its superior instruments.

XXV.3 This instrument SHALL govern until amended or frozen under its own rules.

XXV.4 This instrument is complete, normative, and binding.

---

*END OF ARTIFACT — CEP-004 · CONSTITUTIONAL VALIDATION CONSTITUTION · VERSION 1.0 · NORMATIVE · VALIDATION ONLY · DERIVES FROM CEP-000, CEP-001, CEP-002, CEP-003*
