# U56 — Learning Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U56-learning` |
| Layer | L5 Business Capability |
| Domain | 06 Engagement |
| Steward | `ucos:org:engagement-learning` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P5 |
| Depends on | U41 Content (lessons, video), U28 Entitlement (enrolment access), U27 Subscription / U26 Order (paid courses), U13 Temporal (cohorts, schedules, deadlines, certificate validity), U109 (live classes via RTC), U09 (verifiable credentials), U49/U51 (AI tutor), U66 Privacy (minors), U46 (employee training) |
| Depended on by | Education/EdTech packs, corporate LMS, U46 (compliance training), U17 (skills/credentials evidence), U107 partner certification |
| Master references | §6.2 U56 |

> Learning owns **structured learning**: courses, modules, lessons, learning paths, cohorts and live sessions, enrolments, progress tracking (xAPI/cmi5, SCORM import), assessments and grading, certificates (verifiable credentials, W3C VC), and skills taxonomy mapping. Content assets are U41/U43; access is U28.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| LRN-L1 | Learner records (progress, grades) are personal data; minors' data follows guardian consent (DPDP §9, COPPA) and no behavioural ads. | U66 checks; ADV-L2. |
| LRN-L2 | Assessments are versioned; a grade is reproducible from responses and rubric version. | Immutable attempt records. |
| LRN-L3 | Certificates are signed, verifiable and carry validity ranges; revocation is public. | VC issuance via U09; revocation list. |
| LRN-L4 | AI tutoring discloses AI, stays within course scope and escalates integrity concerns; AI does not grade high-stakes exams without human review. | U51 autonomy ≤ L2 for grading. |

## 2. Objects
`Course { modules, lessons (U41 refs), path prerequisites, skills, duration: Duration }` · `Cohort { course, schedule (U13 sessions), seats, enrolmentWindow: TimeRange }` · `Enrolment { learner, course/cohort, entitlement, status, progress %, due?: TimePoint }` · `Assessment { items, rubric version, attempts allowed, timeLimit: Duration, proctoring }` · `Attempt { assessment, responses, score, gradedBy, at: TimePoint }` · `Certificate { learner, course, issuedAt: TimePoint, validity: TimeRange, credential (VC) }` · `LearningRecord` (xAPI statement store).

## 3. Commands, Events, APIs
Commands: `PublishCourse`, `Enrol`, `RecordProgress` (xAPI), `StartAttempt`, `SubmitAttempt`, `Grade`, `IssueCertificate`, `RevokeCertificate`.
Events: `learning.enrolment.created|completed`, `learning.certificate.issued|revoked`.
```text
POST /v1/learning/courses   POST /v1/learning/enrolments   POST /v1/learning/xapi/statements   POST /v1/learning/attempts
GET /v1/learning/certificates/{id}/verify
```

## 4. Gaps, UI
```prolog
gap(minors_without_guardian_consent, T) :- tenant(T), serves_minors(T), capability(T, learning.core), not consent_purpose(T, guardian).
```
Views: course catalogue, course player, learner dashboard, instructor gradebook, cohort scheduler, certificate verify page. T2.

## Appendix
- **C.** 0.1.0.
