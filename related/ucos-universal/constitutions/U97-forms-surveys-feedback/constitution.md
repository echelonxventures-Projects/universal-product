# U97 — Forms, Surveys & Feedback Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U97-forms` |
| Layer | L10 Experience / L5 |
| Domain | 06 Experience |
| Steward | `ucos:org:experience-forms` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P3 |
| Depends on | U64 UI (form rendering), U04 Meta (schemas), U66 Privacy (purpose/consent), U40 Communication (distribution), U85 CDP (targeting, traits), U72 Analytics, U60 Workflow, U13 Temporal (see TEMPORAL-BINDING-MATRIX) |
| Depended on by | U39 Support (CSAT), U26 Order (post-delivery survey), U86 Marketing (lead forms), U82 (checklists reuse), Government/education packs (applications) |
| Master references | A-38 |

> Forms owns **structured data collection from people**: standalone forms (lead capture, applications, registrations), surveys (NPS, CSAT, CES, research with branching), feedback widgets, quizzes, and their distribution, responses, scoring and analysis. Object create/edit forms for canonical objects are ViewDefinitions (U64); this universe covers forms whose responses are their own data.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| FRM2-L1 | Each form declares purpose, retention and whether responses link to identity; anonymous surveys never store identifiers. | Schema + validator. |
| FRM2-L2 | Survey sampling respects frequency caps and consent (marketing vs service feedback). | Communication + CDP caps. |
| FRM2-L3 | Responses that create business objects (e.g. lead, application) do so via commands of owning universes. | Response handlers = commands. |

## 2. Objects
`FormDefinition { id, kind: form|survey|quiz|feedback-widget, schema (questions: text/choice/rating/scale/matrix/file/date/address/signature), logic (branching CEL), scoring, purpose, retention: RetentionRuleRef, anonymity, locales }` · `Distribution { form, channels (link, embed, email, SMS, WhatsApp, in-app trigger), audience/trigger (event, segment), schedule: Recurrence }` · `Response { form@v, respondent? (party or anonymous token), answers, metadata, score, at: TimePoint }` · `Insight { form, metrics (NPS, CSAT avg), themes (AI) }`.

## 3. Commands, Queries, Events, APIs
Commands: `PublishForm`, `Distribute`, `SubmitResponse`, `CloseForm`.
Events: `forms.response.submitted`, `forms.nps.detractor` (→ support case workflow).
```text
POST /v1/forms   GET /f/{formId} (public render)   POST /v1/forms/{id}/responses   GET /v1/forms/{id}/insights
```

## 4. Gaps, AI, Ops, UI, Scale
```prolog
gap(form_without_purpose, F) :- form(F), collects_personal_data(F), not purpose(F, _).
```
AI: question drafting, open-text theme clustering and sentiment, survey fatigue prediction. Views: form builder (drag-drop, logic, preview per channel), response table, insights dashboard. T2.

## Appendix
- **C.** 0.1.0.
