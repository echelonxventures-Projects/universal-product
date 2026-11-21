# UCOS Ω∞ — CONSTITUTIONAL RATIFICATION CONSTITUTION

| Field | Value |
|-------|-------|
| ARTIFACT ID | CEP-006 |
| ARTIFACT | UCOS Ω∞ Constitutional Ratification Constitution |
| CLASSIFICATION | Constitutional Engineering Program (CEP) — Ratification Constitution |
| STATUS | RATIFIED (program-governance level) · NORMATIVE · LIVING-UNTIL-FROZEN |
| STAGE | Stage 01 · Prompt 08 |
| VERSION | 1.0 |
| DERIVES AUTHORITY FROM | CEP-000, CEP-001, CEP-002, CEP-003, CEP-004, CEP-005 |
| AUTHORITY | Supreme over all ratification operation of the Program; subordinate to CEP-000, CEP-001, CEP-002, CEP-003, CEP-004, and CEP-005 |
| SCOPE OF GOVERNANCE | HOW ratification operates — ratification only |
| CANONICAL FORM | This Markdown file |
| CONFLICT RULE | This instrument governs all ratification operation. Where it conflicts with CEP-005, CEP-004, CEP-003, CEP-002, CEP-001, or CEP-000, the higher instrument governs in that order. |

> This document is normative constitutional law legislating ratification only. It inherits and references CEP-000 through CEP-005 and SHALL NOT rewrite, duplicate, or restate them. It SHALL NOT legislate governance, execution, validation, certification, freeze, evidence content, repository content, or implementation; those are reserved to their respective constitutions.

---

## PREAMBLE

P.1 This instrument IS the permanent constitutional ratification instrument of the UCOS Ω∞ Constitutional Engineering Program.

P.2 Ratification SHALL be the single constitutional act through which a validated and certified artifact becomes an officially accepted member of the constitutional corpus.

P.3 Ratification SHALL determine constitutional acceptance only; it SHALL never perform validation, never perform certification, and never modify any artifact.

P.4 This instrument refines the general Ratification Model of CEP-001 Article XIII and the ratification principles of CEP-000 §28, and SHALL remain consistent with both.

P.5 This instrument SHALL bind every ratification act of the Program until amended or frozen under its own rules.

---

## ARTICLE I — RATIFICATION AUTHORITY

I.1 Ratification Authority SHALL be the authority to determine the constitutional acceptance of a validated and certified artifact and to record that determination.

I.2 Ratification Authority SHALL determine acceptance only; it SHALL introduce no content, perform no validation or certification, and modify no artifact.

I.3 Ratification Authority SHALL be single per artifact; two authorities SHALL NOT ratify the same artifact. A contested ratification authority SHALL be resolved under CEP-002 Article 23.

I.4 Where final constitutional finality requires an authority residing outside the corpus, that out-of-corpus authority SHALL be recognized as superior for finality, and Ratification Authority within the corpus SHALL confer only PROVISIONAL acceptance pending that finality (per CEP-000 §28, CEP-001 Article XIII).

I.5 Ratification Authority SHALL NEVER be self-conferred by Execution Authority and SHALL act only upon an authorization granted under Article XIV.

---

## ARTICLE II — RATIFICATION SCOPE

II.1 This instrument SHALL legislate ratification authority, jurisdiction, eligibility, preconditions, lifecycle, state machine, decision model, criteria, evidence requirements, dependencies, sequencing, authorization, permissions, registry, records, acceptance, rejection, deferral, appeals, finality, traceability, audit, enforcement, and closure.

II.2 This instrument SHALL NOT legislate governance, execution, validation, certification, freeze, evidence content, repository content, or implementation.

II.3 Ratification SHALL be non-mutating; it SHALL read the certified artifact and its bound evidence and SHALL write only ratification records.

II.4 A ratification act outside a defined ratification authorization IS PROHIBITED and SHALL be void.

II.5 Ratification jurisdiction SHALL be bounded to ratification alone and SHALL NOT overlap the jurisdiction of any other constitution.

---

## ARTICLE III — RATIFICATION LIFECYCLE

III.1 The ratification lifecycle SHALL be: determine eligibility, deliberate, decide a single outcome, record the decision, and thereafter maintain the determination through appeal and finality until closure.

III.2 An artifact SHALL NOT enter the ratification lifecycle until it is CERTIFIED under CEP-005 and its certification is neither SUSPENDED, EXPIRED, nor REVOKED.

III.3 Ratification of an artifact SHALL close upon FINALIZED acceptance or upon a rejection that is not under appeal.

III.4 Ratification closure SHALL be distinct from validation closure, certification closure, freeze, and completion, which are reserved to their respective constitutions.

III.5 A closed ratification SHALL be reopened only by appeal under Article XI or by a new ratification cycle triggered by amendment under CEP-001 Article XV.

---

## ARTICLE IV — RATIFICATION ELIGIBILITY

IV.1 An artifact SHALL be eligible for ratification only when it is VALIDATED (validation CLOSED, PASS, under CEP-004) and CERTIFIED (an active certification under CEP-005).

IV.2 Eligibility SHALL be decidable: an artifact is either eligible or not eligible, with no intermediate condition.

IV.3 Eligibility SHALL require that every ratification precondition (Article V) is satisfiable and that the artifact is within a bounded ratification jurisdiction.

IV.4 An ineligible artifact SHALL NOT be ratified; an attempted ratification of an ineligible artifact SHALL be void.

IV.5 Eligibility SHALL be re-determined after any amendment or after any lapse of the artifact's certification.

---

## ARTICLE V — RATIFICATION PRECONDITIONS

V.1 Ratification SHALL require, as preconditions: closed validation (CEP-004), active certification (CEP-005), rooted-and-closed traceability (CEP-001 Article XVIII), and preservation of frozen work (CEP-000 §14).

V.2 Every precondition SHALL be machine-verifiable and SHALL resolve to a decidable satisfied-or-unsatisfied result.

V.3 Preconditions SHALL NOT conflict; two preconditions SHALL NOT require mutually exclusive conditions. A discovered conflict SHALL place the Program in HALTED until resolved under CEP-002 Article 23.

V.4 A precondition that cannot be verified SHALL be treated as unsatisfied until it is made verifiable.

V.5 Ratification SHALL NOT proceed while any precondition is unsatisfied.

---

## ARTICLE VI — RATIFICATION STATE MACHINE

VI.1 The ratification states SHALL be: NOT_ELIGIBLE, ELIGIBLE, DELIBERATING, ACCEPTED, PROVISIONAL, DEFERRED, REJECTED, APPEALING, FINALIZED.

VI.2 The initial state SHALL be NOT_ELIGIBLE; the terminal state SHALL be FINALIZED.

VI.3 The legal ratification transitions SHALL be exactly:
- NOT_ELIGIBLE → ELIGIBLE.
- ELIGIBLE → DELIBERATING.
- DELIBERATING → ACCEPTED.
- DELIBERATING → PROVISIONAL.
- DELIBERATING → DEFERRED.
- DELIBERATING → REJECTED.
- ACCEPTED → FINALIZED.
- PROVISIONAL → FINALIZED.
- PROVISIONAL → REJECTED.
- DEFERRED → ELIGIBLE.
- REJECTED → APPEALING.
- APPEALING → DELIBERATING.
- APPEALING → REJECTED.

VI.4 Any transition not enumerated in VI.3 IS PROHIBITED and SHALL be treated as an illegal transition that places the Program in HALTED.

VI.5 Every ratification state SHALL be defined; an undefined ratification state IS PROHIBITED. Every non-terminal state SHALL have at least one defined outgoing transition, and every state SHALL be reachable from NOT_ELIGIBLE.

VI.6 A single deliberation SHALL yield exactly one outcome among ACCEPTED, PROVISIONAL, DEFERRED, and REJECTED.

VI.7 Amendment of a ratified artifact under CEP-001 Article XV SHALL begin a new ratification cycle from NOT_ELIGIBLE and SHALL NOT mutate the prior ratification record.

---

## ARTICLE VII — RATIFICATION DECISION MODEL

VII.1 A ratification decision SHALL be made only from DELIBERATING and SHALL yield exactly one constitutional outcome.

VII.2 The decision SHALL be ACCEPTED when every precondition is satisfied and in-corpus finality authority is available; PROVISIONAL when every precondition is satisfied but finality authority is out-of-corpus or unavailable; DEFERRED when a precondition is temporarily indeterminate; and REJECTED when a precondition is unmet.

VII.3 A ratification decision SHALL be deterministic; identical artifacts with identical evidence and identical finality-authority availability SHALL yield an identical decision.

VII.4 A ratification decision SHALL introduce no content and SHALL modify no artifact.

VII.5 A ratification decision SHALL be permanently recorded before any subsequent transition.

---

## ARTICLE VIII — RATIFICATION ACCEPTANCE

VIII.1 An ACCEPTED or PROVISIONAL determination SHALL admit the artifact as a member of the constitutional corpus, subject to finality (Article XII).

VIII.2 Every accepted artifact SHALL receive exactly one canonical ratification record.

VIII.3 Acceptance SHALL NOT alter the accepted artifact and SHALL NOT confer freeze, which is reserved to its own constitution.

VIII.4 A PROVISIONAL acceptance SHALL be non-blocking to engineering progression and SHALL be blocking only to declared constitutional finality (per CEP-000 §28, CEP-001 Article XIII).

---

## ARTICLE IX — RATIFICATION REJECTION

IX.1 A REJECTED determination SHALL deny constitutional acceptance and SHALL emit a finding.

IX.2 A rejection SHALL route the artifact to remediation and revalidation under CEP-004 and re-certification under CEP-005 before any new ratification cycle.

IX.3 A rejection SHALL NOT alter the rejected artifact.

IX.4 A rejection under appeal SHALL transition to APPEALING; a rejection not under appeal SHALL close the ratification cycle.

---

## ARTICLE X — RATIFICATION DEFERRAL

X.1 A DEFERRED determination SHALL suspend the ratification decision when a precondition is temporarily indeterminate.

X.2 A deferral SHALL be recorded and SHALL state the condition whose resolution is awaited.

X.3 A DEFERRED artifact SHALL transition to ELIGIBLE for re-deliberation once the awaited condition is resolved.

X.4 A deferral SHALL NOT alter the artifact and SHALL NOT be treated as acceptance or rejection.

---

## ARTICLE XI — RATIFICATION APPEALS

XI.1 An appeal SHALL be the governed re-examination of a REJECTED determination.

XI.2 An appeal SHALL transition a REJECTED determination to APPEALING and SHALL be recorded with its grounds.

XI.3 An appeal SHALL resolve to DELIBERATING when admitted or to REJECTED when denied.

XI.4 Appeals SHALL be finite; an appeal SHALL NOT be re-raised on identical grounds, and repeated appeals on identical grounds IS PROHIBITED, ensuring deterministic termination.

XI.5 An appeal SHALL NOT alter the artifact and SHALL NOT bypass any precondition.

---

## ARTICLE XII — RATIFICATION FINALITY

XII.1 FINALITY SHALL be the conferral of final constitutional acceptance, represented by the terminal state FINALIZED.

XII.2 An ACCEPTED determination MAY reach FINALIZED upon in-corpus finality authority; a PROVISIONAL determination SHALL reach FINALIZED only upon the act of the out-of-corpus finality authority.

XII.3 Where the finality authority is out-of-corpus or unavailable, the artifact SHALL rest at PROVISIONAL, which is non-blocking to engineering progression and blocking only to declared constitutional finality.

XII.4 A PROVISIONAL determination MAY transition to REJECTED if finality is denied; it SHALL NOT be treated as FINALIZED until the finality act occurs.

XII.5 FINALIZED SHALL be terminal; a finalized ratification SHALL be changed only by amendment under CEP-001 Article XV, which begins a new cycle.

---

## ARTICLE XIII — RATIFICATION DEPENDENCIES

XIII.1 Every ratification dependency SHALL be declared; an undeclared dependency IS PROHIBITED.

XIII.2 The ratification dependency graph SHALL be acyclic; a dependency that would form a cycle IS PROHIBITED and SHALL place the Program in HALTED.

XIII.3 An artifact SHALL NOT be ratified until every artifact it depends upon is ACCEPTED, PROVISIONAL, or FINALIZED, and none is REJECTED.

XIII.4 A ratification dependency SHALL be satisfied by reference and SHALL NEVER be satisfied by mutating a depended-upon artifact or its ratification.

---

## ARTICLE XIV — RATIFICATION AUTHORIZATION

XIV.1 A ratification SHALL be authorized only when its artifact is ELIGIBLE.

XIV.2 Authorization SHALL bind the ratification to exactly one artifact and one Ratification Authority.

XIV.3 Ratification SHALL NEVER be self-waived, and a due ratification SHALL NEVER be bypassed (per CEP-000 §22, CEP-001 LAW-5).

XIV.4 An unauthorized ratification determination SHALL be void.

---

## ARTICLE XV — RATIFICATION PERMISSIONS

XV.1 Ratification SHALL be permitted to read the certified artifact and its bound evidence and to write only ratification records and registry entries.

XV.2 Ratification SHALL NOT write to the artifact, to any constitutional corpus content, or to any area outside ratification records and registry.

XV.3 Ratification SHALL NOT mutate, delete, or supersede any artifact.

XV.4 A ratification act exceeding these permissions IS PROHIBITED and SHALL be void.

---

## ARTICLE XVI — RATIFICATION REGISTRY

XVI.1 The Ratification Registry SHALL be the single canonical record of all ratification determinations, their states, and their artifacts.

XVI.2 The Ratification Registry SHALL enforce uniqueness: every accepted artifact SHALL hold exactly one canonical ratification record, and no duplicate ratification authority SHALL be admitted.

XVI.3 The Ratification Registry SHALL be append-only in lineage, content-addressed, and reconciled against repository truth at boot.

XVI.4 A ratification absent from the Registry SHALL be deemed non-existent, and reliance upon it IS PROHIBITED.

XVI.5 The Ratification Registry SHALL be operational memory and SHALL hold no authority over constitutional content.

---

## ARTICLE XVII — RATIFICATION RECORDS

XVII.1 A ratification record SHALL record the artifact, the Ratification Authority, the preconditions satisfied, the evidence referenced, the outcome, the state, and the program-state hash.

XVII.2 Ratification records SHALL be append-only, content-addressed, and reproducible.

XVII.3 A ratification record SHALL assert nothing beyond the determination it carries.

XVII.4 A ratification record SHALL be sufficient, with the registry, to reconstruct the ratification history of any artifact deterministically.

---

## ARTICLE XVIII — RATIFICATION TRACEABILITY

XVIII.1 Every ratification SHALL trace to the certified artifact it determines and to the validation, certification, evidence, and preconditions it references, referencing CEP-001 Article XVIII.

XVIII.2 Ratification traceability SHALL be rooted and closed with zero orphans and SHALL be verified before any determination.

XVIII.3 Ratification traceability links SHALL be typed and addressable.

XVIII.4 A ratification whose traceability cannot be closed SHALL be void.

---

## ARTICLE XIX — RATIFICATION AUDIT

XIX.1 Every ratification determination, acceptance, rejection, deferral, appeal, and finality act SHALL be recorded through the general Audit Model of CEP-001 Article XVII.

XIX.2 Ratification audit records SHALL be sufficient to reconstruct the ratification history deterministically and to preserve deterministic constitutional history.

XIX.3 Ratification audit records SHALL be operational memory and SHALL NEVER enter the constitutional corpus.

XIX.4 A ratification act that cannot be audited SHALL be treated as if it did not lawfully occur.

---

## ARTICLE XX — RATIFICATION ENFORCEMENT

XX.1 Ratification law SHALL be enforced at ratification transitions through the general Enforcement Model of CEP-001 Article XXIII.

XX.2 A ratification violation — an illegal ratification transition, an unauthorized ratification, a permission breach, a precondition conflict, a ratification of an ineligible artifact, a ratification preceding validation or certification, or a decision yielding other than exactly one outcome — SHALL place the Program in HALTED, emit a finding, and require remediation before progression resumes.

XX.3 A void ratification act SHALL have no effect and SHALL be recorded as void.

XX.4 Ratification enforcement SHALL NEVER be waived, deferred, or overridden by any authority tier.

XX.5 Ratification enforcement records SHALL be append-only, content-addressed, and auditable.

---

## ARTICLE XXI — RATIFICATION SUPREMACY

XXI.1 This instrument IS supreme over all ratification operation and over every subordinate ratification instrument.

XXI.2 This instrument derives from CEP-000, CEP-001, CEP-002, CEP-003, CEP-004, and CEP-005 and IS subordinate to all six; conflicts resolve in favor of the higher instrument in that order.

XXI.3 This instrument SHALL NOT govern, execute, validate, certify, freeze, or legislate evidence content or repository content.

XXI.4 This instrument SHALL bind every remaining Stage of the Program until amended or frozen under its own rules.

---

## ARTICLE XXII — NORMATIVE REFERENCES

XXII.1 CEP-000 — Constitutional Engineering Charter, §14, §22, §28 — the origin of the ratification principles this instrument operationalizes.

XXII.2 CEP-001 — Constitutional Engineering Constitution, Articles XIII, XV, XVII, XVIII, XXIII — the general ratification, amendment, audit, traceability, and enforcement models this instrument refines and references.

XXII.3 CEP-002 — Constitutional Governance Constitution, Article 23 — the conflict resolution invoked for authority and precondition conflicts.

XXII.4 CEP-003 — Constitutional Execution Constitution — the execution states at which ratification becomes due.

XXII.5 CEP-004 — Constitutional Validation Constitution, Article XIX — the validation closure precondition.

XXII.6 CEP-005 — Constitutional Certification Constitution — the active certification precondition.

XXII.7 Where any normative reference conflicts with this instrument on ratification, this instrument governs; on any other matter, the higher instrument governs.

---

## ARTICLE XXIII — CONSTITUTIONAL INTEGRITY

XXIII.1 A ratified artifact SHALL already be validated.

XXIII.2 A ratified artifact SHALL already be certified.

XXIII.3 Ratification SHALL NOT alter any artifact.

XXIII.4 A single ratification deliberation SHALL produce exactly one constitutional outcome.

XXIII.5 Every ratification decision SHALL be permanently recorded.

XXIII.6 Every accepted artifact SHALL receive exactly one canonical ratification record.

XXIII.7 Ratification SHALL preserve deterministic constitutional history.

---

## ARTICLE XXIV — VERSIONING

XXIV.1 This instrument carries an explicit version; the present version IS 1.0.

XXIV.2 Any change SHALL occur only through the Amendment Model of CEP-001 Article XV and SHALL increment the version.

XXIV.3 A superseded version SHALL be retained for lineage and marked superseded; a frozen version SHALL be immutable and content-addressed.

XXIV.4 Every subordinate ratification instrument SHALL cite the version of this instrument under which it was produced.

---

## ARTICLE XXV — CONSTITUTIONAL CONCLUSION

XXV.1 This instrument IS the supreme ratification law of the Constitutional Engineering Program.

XXV.2 Every ratification act SHALL derive from, comply with, and remain consistent with this instrument and its superior instruments.

XXV.3 Ratification SHALL determine constitutional acceptance only; it SHALL never validate, never certify, and never modify any artifact.

XXV.4 This instrument SHALL govern until amended or frozen under its own rules, and is complete, normative, and binding.

---

*END OF ARTIFACT — CEP-006 · CONSTITUTIONAL RATIFICATION CONSTITUTION · VERSION 1.0 · NORMATIVE · RATIFICATION ONLY · DERIVES FROM CEP-000, CEP-001, CEP-002, CEP-003, CEP-004, CEP-005*
