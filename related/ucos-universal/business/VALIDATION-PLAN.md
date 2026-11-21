# UCOS — Validating the Business Assumptions

| Field | Value |
|---|---|
| Author | Bipin Kumar |
| Version | 0.1 |
| Date | 2026-10-03 |
| Related | [COST-MODEL.md](COST-MODEL.md) (assumptions A1–A8), [COMMERCIAL-MODEL.md](COMMERCIAL-MODEL.md), [TEAM-AND-ROADMAP-PLAN.md](TEAM-AND-ROADMAP-PLAN.md) |

The cost model and commercial model rest on assumptions. This plan says how each one gets tested, by when, and what changes if the result is outside the tolerance. Results are recorded as U01 DecisionRecords at the phase gate where they are due.

## 1. Cost assumptions
| # | Assumption | Test | Due | Tolerance | If outside tolerance |
|---|---|---|---|---|---|
| A2 | Variable infra cost $0.004 per order | P1 load test (`PERF-SLO-01`) on a reference cell: replay the `d2c-in-ae` journey mix at 2k rps for 2 h; divide the cell's metered cost by orders | P1 exit (Jun 2027) | $0.003–0.006 | Above: profile the object service and event fan-out before launch pricing; re-run cost model §3 |
| A3 | $10 fixed per tenant per month | Measure storage, index and backup cost for 50 design-partner tenants | P1 exit | $6–15 | Adjust the Starter platform fee |
| A4 | Dedicated cell $9k per month | Price the cell bill of materials with two cloud providers' calculators, then measure the first dedicated cell | P4 | $7k–12k | Adjust the dedicated-cell line item (+₹8 L) |
| A5 | ₹45 L blended loaded cost per FTE | Compare offers for the first 10 hires with the model | Month 3 | ±15% | Re-plan Y1 headcount to keep burn |
| AI | AI cost within included credits for typical tenants | Meter AI usage per use case for design partners (U49 budgets) | P3 exit | Median tenant ≤ included credits | Adjust credits per tier or route more traffic to smaller models |

## 2. Commercial assumptions
| Assumption | Test | Due | Success signal |
|---|---|---|---|
| Merchants accept a platform fee plus a GMV take rate | Price interviews with 30 D2C brands and 10 B2B distributors (Van Westendorp + an A/B offer of a fixed-fee option) | P0 (Feb 2027) | ≥ 60% of interviewees consider the Growth price acceptable |
| Time to first order ≤ 3 days (Starter) | Measure design-partner onboarding from signup to first real order | P1 exit | Median ≤ 3 days |
| Design partners convert to paying | 5 design partners on free P1 terms with a paid conversion clause | P1 exit + 60 days | ≥ 3 of 5 convert |
| Marketplace operators pay Enterprise + marketplace fee | First operator contract signed | P2 exit | 1 signed contract |
| Net revenue retention ≥ 110% | Cohort analysis from billing data (U27/U72) | 12 months after first paying tenant | ≥ 100% at month 12, trending upwards |

## 3. Review cadence
- Monthly: A2 measurement once P1 load tests exist, burn against plan, hiring against plan.
- At every phase gate: all items due at that gate, recorded as DecisionRecords.
- Any result outside tolerance triggers a re-plan of the affected document within two weeks.
