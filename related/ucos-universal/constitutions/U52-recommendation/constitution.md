# U52 — Recommendation Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U52-recommendation` |
| Layer | L8 Intelligence |
| Domain | 07 Intelligence |
| Steward | `ucos:org:intelligence-recs` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P4 |
| Depends on | U94 ML Platform (models, features, training), U61 Event (behaviour), U21 Catalog (candidates), U20 Inventory (availability filter), U16 Context, U66 Privacy (consent for personalisation), U44 Search (shared embeddings), U13 Temporal (recency, seasonality), U33 (sponsored blending) |
| Depended on by | Storefront slots (home, PDP, cart, email), U86 Marketing (next-best-offer), U41 (content recs), U56 (learning paths), U38 (next-best-action) |
| Master references | §6.2 U52, DSA Art. 27/38 (recommender transparency and non-profiling option) |

> Recommendation owns **ranked suggestions for slots**: slot definitions, strategies (popular, similar, frequently-bought-together, personalised, trending, rules-curated), candidate generation, filtering (availability, eligibility, policy), ranking and blending (organic + sponsored with labels), explanations, and experiments. Model training lives in U94.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| REC-L1 | Personalisation requires a lawful basis/consent; a non-profiled option is always available (DSA VLOP rules, DPDP children). | Context consent flag → strategy fallback to non-personal. |
| REC-L2 | Recommendations never show unavailable, ineligible or policy-restricted items for the context. | Post-filter via U20/U28/U53. |
| REC-L3 | Main parameters of recommender systems are disclosed to users. | Public transparency page per tenant. |
| REC-L4 | Sponsored items are labelled and capped per slot. | Blending policy (ADV-L1). |

## 2. Objects
`Slot { id, surface, strategy chain, max items, sponsored cap, fallback }` · `Strategy { kind, model ref (U94), parameters, filters }` · `RecommendationResponse { slot, items [{ref, score, reason code, sponsored}], modelVersions, at: TimePoint }` · `Experiment` (U94/U72 experiment ref).

## 3. Commands, APIs
Queries: `Recommend(slot, ctx, subject?)` (p99 ≤ 80 ms). Commands: `DefineSlot`, `PinItems` (merchandising), `StartExperiment`.
```text
POST /v1/recs/recommend   POST /v1/recs/slots   POST /v1/recs/slots/{id}/pins
```
Events: `recommendation.served` (sampled, for training/attribution), `recommendation.clicked`.

## 4. Gaps, UI
```prolog
gap(personalisation_without_consent_rule, T, J) :- tenant(T), in_scope(T, J), capability(T, recs.personalised), not consent_purpose(T, personalisation).
```
Signals: `rec_ctr`, `rec_attributed_revenue`, `coverage`, `latency_ms`. Views: slot manager with live preview per persona, merchandising pins, experiment results, transparency page. T1 (fallback: popular/curated lists from cache).

## Appendix
- **C.** 0.1.0.
