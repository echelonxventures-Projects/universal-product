# U70 — Trust & Reputation Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U70-trust` |
| Layer | Trust Plane |
| Domain | 08 Governance |
| Steward | `ucos:org:trust-reviews` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P2 |
| Depends on | U26 Order (verified purchase), U11 Party, U88 Social (moderation pipeline), U69 Risk (fake-review detection), U13 Temporal (review prompts after delivery, decay), U18 Product (aggregate per GPID), U25 Marketplace (seller ratings), U66 Privacy, U67 Compliance (consumer review laws) |
| Depended on by | U21 Catalog/PDP, U44 Search (ranking signals), U25 Marketplace (seller performance), U37 Mobility (driver/rider ratings), U83 Rental, hospitality and services packs, U57 (pack marketplace ratings), U09/U10 (verified badges) |
| Master references | §6.3 (Review/rating owned by Trust), W4 (marketplace ratings) |

> Trust owns **reputation signals**: reviews and ratings (products, sellers, services, providers, drivers/riders, hosts/guests, packs), verified-purchase/experience badges, review moderation and authenticity, aggregate scores, trust scores for parties/organisations, verification badges (from U09 VerificationRecords), and responses/disputes on reviews.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| TRU-L1 | Reviews are authentic: verified-experience flags derived from real orders/bookings; incentivised reviews disclosed; fake/paid reviews detected and removed. | Verification link to U26/U13; U69 detection; consumer law (EU Omnibus, India BIS IS 19000:2022, FTC rule on fake reviews). |
| TRU-L2 | Negative reviews are not suppressed for commercial reasons; moderation removes only policy violations, with notice to the author and appeal. | Moderation reasons taxonomy; U71 appeals. |
| TRU-L3 | Aggregates disclose method (e.g. weighted, recency) and are computed identically for all subjects. | Published aggregation spec; reproducible job. |
| TRU-L4 | Two-sided ratings (mobility, rentals) are revealed simultaneously or after a window to avoid retaliation. | Temporal reveal policy. |

## 2. Objects
`Review { subject (GPID/listing/seller/service/provider/party/pack), author (party, may display pseudonym), rating (1–5 or dimensions), text, media (U43), verified: {kind: purchase|booking|trip, ref}, incentivised: bool, locale, status: pending|published|rejected|removed, moderation, createdAt: TimePoint }` · `Rating` (lightweight, two-sided) · `ReviewResponse { review, responder (seller/brand), text }` · `Aggregate { subject, average, count, distribution, method version, computedAt: TimePoint }` · `TrustScore { party/org, score, components (verifications, history, disputes, risk), computedAt: TimePoint }` · `Badge { subject, kind: verified-seller|top-rated|verified-identity|certified-pack, validity: TimeRange }`.

## 3. Commands, Queries, Events, APIs
Commands: `RequestReview` (Temporal trigger after delivery/experience), `SubmitReview`, `ModerateReview`, `RespondToReview`, `ReportReview`, `RecomputeAggregates`, `AwardBadge`, `RevokeBadge`.
Events: `trust.review.published|removed`, `trust.aggregate.updated`, `trust.badge.awarded|revoked`.
```text
POST /v1/trust/reviews   GET /v1/trust/aggregates/{subject}   POST /v1/trust/reviews/{id}:moderate|:respond|:report
```

## 4. Gaps, AI, Ops, UI
```prolog
gap(reviews_without_moderation, T) :- tenant(T), capability(T, trust.reviews), not capability(T, social.moderation).
gap(two_sided_without_reveal_policy, T) :- tenant(T), two_sided_ratings(T), not reveal_policy(T).
```
AI: fake-review detection (U69), review summarisation on PDP ("customers say…", labelled AI, citing reviews), sentiment and topic extraction for sellers/brands. Signals: `reviews_per_order`, `moderation_backlog`, `fake_review_removals`, `rating_avg_trend`. Views: PDP review widget (filters, verified badges, media), write-review flow (post-delivery), seller/brand response console, moderation queue, trust badges admin. T1.

## Appendix
- **C.** 0.1.0.
