# UCOS Ω∞ — CONSTITUTIONAL CERTIFICATION CONSTITUTION

| Field | Value |
|-------|-------|
| ARTIFACT ID | CEP-005 |
| ARTIFACT | UCOS Ω∞ Constitutional Certification Constitution |
| CLASSIFICATION | Constitutional Engineering Program (CEP) — Certification Constitution |
| STATUS | RATIFIED (program-governance level) · NORMATIVE · LIVING-UNTIL-FROZEN |
| STAGE | Stage 01 · Prompt 07 |
| VERSION | 1.0 |
| DERIVES AUTHORITY FROM | CEP-000, CEP-001, CEP-002, CEP-003, CEP-004 |
| AUTHORITY | Supreme over all certification operation of the Program; subordinate to CEP-000, CEP-001, CEP-002, CEP-003, and CEP-004 |
| SCOPE OF GOVERNANCE | HOW certification operates — certification only |
| CANONICAL FORM | This Markdown file |
| CONFLICT RULE | This instrument governs all certification operation. Where it conflicts with CEP-004, CEP-003, CEP-002, CEP-001, or CEP-000, the higher instrument governs in that order. |

> This document is normative constitutional law legislating certification only. It inherits and references CEP-000, CEP-001, CEP-002, CEP-003, and CEP-004 and SHALL NOT rewrite, duplicate, or restate them. It SHALL NOT legislate governance, execution, validation, ratification, evidence content, repository content, or implementation; those are reserved to their respective constitutions.

---

## PREAMBLE

P.1 This instrument IS the permanent constitutional certification instrument of the UCOS Ω∞ Constitutional Engineering Program.

P.2 Certification SHALL be the reproducible attestation that a validated subject satisfies its certification preconditions; certification SHALL attest and SHALL confer no authority.

P.3 Certification SHALL occur only after successful validation, SHALL never replace validation, and SHALL never imply ratification.

P.4 This instrument refines the general Certification Model of CEP-001 Article XII and the certification principles of CEP-000 §27, and SHALL remain consistent with both.

P.5 This instrument SHALL bind every certification act of the Program until amended or frozen under its own rules.

---

## ARTICLE I — CERTIFICATION AUTHORITY

I.1 Certification Authority SHALL be the authority to attest that a validated subject satisfies its certification preconditions and to issue, suspend, revoke, renew, and expire a certification.

I.2 Certification Authority SHALL introduce no content and SHALL confer no status beyond an attestation.

I.3 Certification Authority SHALL NOT govern, execute, validate, ratify, or legislate evidence content.

I.4 Certification Authority SHALL be single per subject; two authorities SHALL NOT certify the same subject. A contested certification authority SHALL be resolved under CEP-002 Article 23.

I.5 Certification Authority SHALL NEVER self-authorize a certification and SHALL act only upon an authorization granted under Article XII.

---

## ARTICLE II — CERTIFICATION SCOPE

II.1 This instrument SHALL legislate certification authority, jurisdiction, eligibility, lifecycle, preconditions, evidence requirements, completeness, decision rules, state machine, dependencies, sequencing, authorization, permissions, records, registry, expiration, renewal, revocation, suspension, traceability, audit, enforcement, and closure.

II.2 This instrument SHALL NOT legislate governance, execution, validation, ratification, evidence content, repository content, or implementation.

II.3 Certification SHALL be non-mutating; it SHALL read the validated subject and its bound evidence and SHALL write only certification records.

II.4 A certification act outside a defined certification authorization IS PROHIBITED and SHALL be void.

II.5 Certification jurisdiction SHALL be bounded to certification alone and SHALL NOT overlap the jurisdiction of any other constitution.

---

## ARTICLE III — CERTIFICATION LIFECYCLE

III.1 The certification lifecycle SHALL be: determine eligibility, attest by decision, record, and thereafter maintain the certification through suspension, revocation, expiration, and renewal until closure.

III.2 A subject SHALL NOT enter the certification lifecycle until its validation is CLOSED under CEP-004 Article XIX.

III.3 Certification of a subject SHALL close upon issuance of a certification record or upon a terminal revocation.

III.4 Certification closure SHALL be distinct from validation closure, ratification, and completion, which are reserved to their respective constitutions.

III.5 A closed certification SHALL be reopened only by renewal or by a new certification cycle triggered by amendment under CEP-001 Article XV.

---

## ARTICLE IV — CERTIFICATION ELIGIBILITY

IV.1 A subject SHALL be eligible for certification only when its validation is CLOSED with a PASS verdict under CEP-004.

IV.2 Eligibility SHALL be decidable: a subject is either eligible or not eligible, with no intermediate condition.

IV.3 Eligibility SHALL require that every certification precondition (Article V) is satisfiable and that the subject is within a bounded certification jurisdiction.

IV.4 An ineligible subject SHALL NOT be certified; an attempted certification of an ineligible subject SHALL be void.

IV.5 Eligibility SHALL be re-determined after any amendment, suspension, or expiration.

---

## ARTICLE V — CERTIFICATION PRECONDITIONS

V.1 Certification SHALL require, as preconditions: closed validation (CEP-004), proven determinism (CEP-001 Article XX), rooted-and-closed traceability (CEP-001 Article XVIII), preservation of frozen work (CEP-000 §14), and bound evidence (Article VIII).

V.2 Every precondition SHALL be machine-verifiable and SHALL resolve to a decidable satisfied-or-unsatisfied result.

V.3 Preconditions SHALL NOT conflict; two preconditions SHALL NOT require mutually exclusive conditions. A discovered conflict SHALL place the Program in HALTED until resolved under CEP-002 Article 23.

V.4 A precondition that cannot be verified SHALL be treated as unsatisfied until it is made verifiable.

V.5 Certification SHALL NOT proceed while any precondition is unsatisfied.

---

## ARTICLE VI — CERTIFICATION STATE MACHINE

VI.1 The certification states SHALL be: NOT_ELIGIBLE, ELIGIBLE, CERTIFYING, CERTIFIED, SUSPENDED, EXPIRED, RENEWING, REVOKED.

VI.2 The initial state SHALL be NOT_ELIGIBLE; the terminal state SHALL be REVOKED.

VI.3 The legal certification transitions SHALL be exactly:
- NOT_ELIGIBLE → ELIGIBLE.
- ELIGIBLE → CERTIFYING.
- CERTIFYING → CERTIFIED.
- CERTIFYING → NOT_ELIGIBLE.
- CERTIFIED → SUSPENDED.
- CERTIFIED → EXPIRED.
- CERTIFIED → REVOKED.
- SUSPENDED → CERTIFIED.
- SUSPENDED → REVOKED.
- EXPIRED → RENEWING.
- RENEWING → CERTIFIED.
- RENEWING → REVOKED.

VI.4 Any transition not enumerated in VI.3 IS PROHIBITED and SHALL be treated as an illegal transition that places the Program in HALTED.

VI.5 Every certification state SHALL be defined; an undefined certification state IS PROHIBITED. Every non-terminal state SHALL have at least one defined outgoing transition, and every state SHALL be reachable from NOT_ELIGIBLE.

VI.6 Amendment of a certified subject under CEP-001 Article XV SHALL transition the certification to REVOKED, and re-certification SHALL begin a new cycle from NOT_ELIGIBLE.

---

## ARTICLE VII — CERTIFICATION DECISION MODEL

VII.1 A certification decision SHALL be made only from CERTIFYING and SHALL yield exactly one outcome: grant (transition to CERTIFIED) or deny (transition to NOT_ELIGIBLE).

VII.2 A grant SHALL require that every precondition is satisfied; a single unsatisfied precondition SHALL compel a deny.

VII.3 A deny SHALL emit a finding and SHALL route the subject to remediation and revalidation under CEP-004 before re-eligibility.

VII.4 A certification decision SHALL be deterministic; identical subjects with identical evidence SHALL yield an identical decision.

VII.5 A certification decision SHALL introduce no content and SHALL NEVER imply ratification or finality.

---

## ARTICLE VIII — CERTIFICATION EVIDENCE REQUIREMENTS

VIII.1 Certification SHALL require that every attested claim is bound to addressable, reproducible evidence, referencing CEP-000 §15 and CEP-001 Article XIX.

VIII.2 Certification SHALL reference the validation closure evidence of CEP-004 and SHALL NOT re-perform validation.

VIII.3 Certification SHALL reference evidence and SHALL NOT inline it; certification SHALL legislate no evidence content.

VIII.4 A certification lacking bound evidence for any attested claim SHALL be void.

---

## ARTICLE IX — CERTIFICATION COMPLETENESS

IX.1 Certification completeness SHALL require that every precondition is satisfied and every required certification record field is present.

IX.2 A certification SHALL NOT be issued while any required attestation is missing or any precondition is unsatisfied.

IX.3 Completeness SHALL be machine-verifiable and decidable.

IX.4 An incomplete certification SHALL be void.

---

## ARTICLE X — CERTIFICATION DEPENDENCIES

X.1 Every certification dependency SHALL be declared; an undeclared dependency IS PROHIBITED.

X.2 The certification dependency graph SHALL be acyclic; a dependency that would form a cycle IS PROHIBITED and SHALL place the Program in HALTED.

X.3 A subject SHALL NOT be certified until every subject it depends upon is CERTIFIED and not SUSPENDED, EXPIRED, or REVOKED.

X.4 A certification dependency SHALL be satisfied by reference and SHALL NEVER be satisfied by mutating a depended-upon certification.

---

## ARTICLE XI — CERTIFICATION SEQUENCING

XI.1 Certification SHALL follow successful validation and SHALL NEVER precede it.

XI.2 Certification SHALL be sequenced deterministically; where certifications are independent, they SHALL be ordered by a canonical, reproducible ordering.

XI.3 Certification SHALL NOT reorder a subject ahead of a subject it depends upon.

XI.4 Certification sequencing SHALL NEVER depend on wall-clock time, arrival order, or nondeterministic identifiers.

---

## ARTICLE XII — CERTIFICATION AUTHORIZATION

XII.1 A certification SHALL be authorized only when its subject is ELIGIBLE.

XII.2 Authorization SHALL bind the certification to exactly one subject and one Certification Authority.

XII.3 Certification SHALL NEVER be self-waived, and a due certification SHALL NEVER be bypassed (per CEP-000 §22, CEP-001 LAW-5).

XII.4 An unauthorized certification SHALL be void.

---

## ARTICLE XIII — CERTIFICATION PERMISSIONS

XIII.1 Certification SHALL be permitted to read the validated subject and its bound evidence and to write only certification records and registry entries.

XIII.2 Certification SHALL NOT write to the subject, to any constitutional corpus, or to any area outside certification records and registry.

XIII.3 Certification SHALL NOT mutate, delete, or supersede any artifact.

XIII.4 A certification act exceeding these permissions IS PROHIBITED and SHALL be void.

---

## ARTICLE XIV — CERTIFICATION REGISTRY

XIV.1 The Certification Registry SHALL be the single canonical record of all certifications, their states, and their subjects.

XIV.2 The Certification Registry SHALL enforce uniqueness: no subject SHALL hold two active certifications, and no duplicate certification authority SHALL be admitted.

XIV.3 The Certification Registry SHALL be append-only in lineage, content-addressed, and reconciled against repository truth at boot.

XIV.4 A certification absent from the Registry SHALL be deemed non-existent, and reliance upon it IS PROHIBITED.

XIV.5 The Certification Registry SHALL be operational memory and SHALL hold no authority over constitutional content.

---

## ARTICLE XV — CERTIFICATION RECORDS

XV.1 A certification record SHALL record the subject, the Certification Authority, the preconditions satisfied, the evidence referenced, the decision, the state, and the program-state hash.

XV.2 Certification records SHALL be append-only, content-addressed, and reproducible.

XV.3 A certification record SHALL assert nothing beyond the attestation it carries.

XV.4 A certification record SHALL be sufficient, with the registry, to reconstruct the certification history of any subject deterministically.

---

## ARTICLE XVI — CERTIFICATION SUSPENSION

XVI.1 A CERTIFIED certification MAY transition to SUSPENDED upon a finding that a precondition is temporarily unmet.

XVI.2 A SUSPENDED certification SHALL confer no attestation while suspended and SHALL NOT be relied upon.

XVI.3 A SUSPENDED certification SHALL transition to CERTIFIED only upon re-verification that the affected preconditions are satisfied, or to REVOKED otherwise.

XVI.4 Suspension SHALL be recorded and SHALL preserve the prior certification record in lineage.

---

## ARTICLE XVII — CERTIFICATION REVOCATION

XVII.1 A certification SHALL transition to REVOKED upon a finding that a precondition is permanently unmet or upon amendment of the certified subject (per Article VI.6).

XVII.2 REVOKED SHALL be terminal for that certification; a revoked certification SHALL NOT be reinstated and SHALL NOT be relied upon.

XVII.3 Revocation SHALL be recorded and SHALL preserve the prior certification record in lineage.

XVII.4 Re-certification of a revoked subject SHALL begin a new certification cycle from NOT_ELIGIBLE.

---

## ARTICLE XVIII — CERTIFICATION RENEWAL

XVIII.1 Renewal SHALL occur only from EXPIRED, by transition to RENEWING.

XVIII.2 Renewal SHALL re-verify every certification precondition against the subject as of renewal.

XVIII.3 Renewal SHALL NOT carry forward any prior attestation; every precondition SHALL be re-verified.

XVIII.4 Renewal SHALL transition to CERTIFIED upon full re-verification, or to REVOKED otherwise.

---

## ARTICLE XIX — CERTIFICATION EXPIRATION

XIX.1 A CERTIFIED certification MAY transition to EXPIRED when its declared validity condition lapses.

XIX.2 An EXPIRED certification SHALL confer no attestation and SHALL NOT be relied upon until renewed.

XIX.3 Expiration SHALL be deterministic and SHALL be recorded.

XIX.4 An EXPIRED certification SHALL transition only to RENEWING.

---

## ARTICLE XX — CERTIFICATION TRACEABILITY

XX.1 Every certification SHALL trace to the validated subject it attests and to the evidence and preconditions it references, referencing CEP-001 Article XVIII.

XX.2 Certification traceability SHALL be rooted and closed with zero orphans and SHALL be verified before issuance.

XX.3 Certification traceability links SHALL be typed and addressable.

XX.4 A certification whose traceability cannot be closed SHALL be void.

---

## ARTICLE XXI — CERTIFICATION AUDIT

XXI.1 Every certification decision, suspension, revocation, renewal, and expiration SHALL be recorded through the general Audit Model of CEP-001 Article XVII.

XXI.2 Certification audit records SHALL be sufficient to reconstruct the certification history deterministically.

XXI.3 Certification audit records SHALL be operational memory and SHALL NEVER enter the constitutional corpus.

XXI.4 A certification act that cannot be audited SHALL be treated as if it did not lawfully occur.

---

## ARTICLE XXII — CERTIFICATION ENFORCEMENT

XXII.1 Certification law SHALL be enforced at certification transitions through the general Enforcement Model of CEP-001 Article XXIII.

XXII.2 A certification violation — an illegal certification transition, an unauthorized certification, a permission breach, a precondition conflict, a certification of an ineligible subject, or a certification preceding validation — SHALL place the Program in HALTED, emit a finding, and require remediation or revocation before progression resumes.

XXII.3 A void certification act SHALL have no effect and SHALL be recorded as void.

XXII.4 Certification enforcement SHALL NEVER be waived, deferred, or overridden by any authority tier.

XXII.5 Certification enforcement records SHALL be append-only, content-addressed, and auditable.

---

## ARTICLE XXIII — CERTIFICATION SUPREMACY

XXIII.1 This instrument IS supreme over all certification operation and over every subordinate certification instrument.

XXIII.2 This instrument derives from CEP-000, CEP-001, CEP-002, CEP-003, and CEP-004 and IS subordinate to all five; conflicts resolve in favor of the higher instrument in that order.

XXIII.3 This instrument SHALL NOT govern, execute, validate, ratify, or legislate evidence content or repository content.

XXIII.4 Certification SHALL NEVER imply, substitute for, or confer ratification or finality.

XXIII.5 This instrument SHALL bind every remaining Stage of the Program until amended or frozen under its own rules.

---

## ARTICLE XXIV — NORMATIVE REFERENCES

XXIV.1 CEP-000 — Constitutional Engineering Charter, §14, §15, §22, §27 — the origin of the certification principles this instrument operationalizes.

XXIV.2 CEP-001 — Constitutional Engineering Constitution, Articles XII, XV, XVII, XVIII, XX, XXIII — the general certification, amendment, audit, traceability, determinism, and enforcement models this instrument refines and references.

XXIV.3 CEP-002 — Constitutional Governance Constitution, Article 23 — the conflict resolution invoked for authority and precondition conflicts.

XXIV.4 CEP-003 — Constitutional Execution Constitution — the execution states at which certification becomes due.

XXIV.5 CEP-004 — Constitutional Validation Constitution, Article XIX — the validation closure that is the eligibility precondition for certification.

XXIV.6 Where any normative reference conflicts with this instrument on certification, this instrument governs; on any other matter, the higher instrument governs.

---

## ARTICLE XXV — CONSTITUTIONAL CONCLUSION

XXV.1 This instrument IS the supreme certification law of the Constitutional Engineering Program.

XXV.2 Every certification act SHALL derive from, comply with, and remain consistent with this instrument and its superior instruments.

XXV.3 Certification SHALL occur only after successful validation, SHALL never replace validation, and SHALL never imply ratification.

XXV.4 This instrument SHALL govern until amended or frozen under its own rules, and is complete, normative, and binding.

---

*END OF ARTIFACT — CEP-005 · CONSTITUTIONAL CERTIFICATION CONSTITUTION · VERSION 1.0 · NORMATIVE · CERTIFICATION ONLY · DERIVES FROM CEP-000, CEP-001, CEP-002, CEP-003, CEP-004*
