# UCOS — Cost Model and Unit Economics

| Field | Value |
|---|---|
| Author | Bipin Kumar |
| Version | 0.1 (planning model) |
| Date | 2026-10-03 |
| Currency | INR (₹), with USD at the stated FX assumption. 1 Cr = ₹10,000,000; 1 L (lakh) = ₹100,000 |
| Status | **Planning estimates.** Every figure follows from the assumptions in §1. Replace them with vendor quotes and payroll data before using them for funding or pricing decisions. |
| Related | [COMMERCIAL-MODEL.md](COMMERCIAL-MODEL.md), [TEAM-AND-ROADMAP-PLAN.md](TEAM-AND-ROADMAP-PLAN.md), master §27 (topology), U72 (cost signals) |

## 1. Assumptions (change these first)
| # | Assumption | Value | Why / source to verify |
|---|---|---|---|
| A1 | FX rate | ₹88 per USD | Treasury rate at budget time |
| A2 | Variable infra cost per order (shared cell, ≥ 60% utilisation) | $0.004 | Compute, Postgres, events, search and CDN for about 5–10 API calls and 8–12 events per order. Validate with the P1 load test (`PERF-SLO-01`). |
| A3 | Fixed infra cost per tenant per month | $10 | Storage, search index, backups, monitoring |
| A4 | Dedicated cell (enterprise), per month | $9,000 | HA cell: 3 AZs, Postgres HA, Kafka-API, search, observability |
| A5 | Blended loaded cost per product and engineering FTE | ₹45 L/year | India-based team with a few senior hires at higher bands; loaded = salary, benefits, equipment, office |
| A6 | Customer success and support | 10% of revenue | Included in cost of revenue |
| A7 | Variable infra and third-party cost of revenue | 12% of revenue | Derived from A2 and A3 at the tier mix in §4 |
| A8 | Go-to-market and G&A | ₹3 Cr (Y1), ₹8 Cr (Y2), ₹14 Cr (Y3) | Sales, customer success leads, legal, finance, office |

Pass-through costs (PSP fees, SMS, WhatsApp, maps, carriers, AI usage above included credits) are **excluded** from margins. They are billed at cost plus a handling fee (see the commercial model).

## 2. Fixed platform costs (USD per year)
These cover baseline production capacity, non-production environments, tooling and compliance. Incremental production capacity for tenant growth is a variable cost (A2, A3) and is counted in cost of revenue.

| Item | Y1 (Nov 26–Oct 27) | Y2 | Y3 | Notes |
|---|---|---|---|---|
| Production shared cells, IN (Mumbai) + AE (UAE), baseline HA | $144k (8 months from P1) | $312k | $480k | Two regions for residency; grows with the number of cells |
| Non-production (dev, staging, performance, sandbox/simulation) | $108k | $144k | $180k | Ephemeral environments with scale-to-zero |
| Control plane (registry, composer, certification, GitOps) | $48k | $60k | $72k | Global, small |
| Observability (metrics, logs, traces, lakehouse) | $36k | $60k | $96k | Retention tiers keep this bounded |
| Engineering tooling (code hosting, CI, SAST/SCA, secrets, design) | $60k | $84k | $108k | |
| Compliance (pen tests; SOC 2 Type I then II; ISO 27001; PCI SAQ A) | $55k | $140k | $160k | SOC 2 Type I is the P5 exit criterion (master §32) |
| AI development and evaluation usage | $30k | $60k | $120k | Eval suites and red-teaming (U49) |
| Contingency | 15% | 10% | 15% | |
| **Total** | **≈ $0.55M (₹4.8 Cr)** | **≈ $0.95M (₹8.4 Cr)** | **≈ $1.40M (₹12.3 Cr)** | |

## 3. Variable cost per tenant
```text
infra_cost_month(tenant) = (A3 + orders_per_month × A2) × FX + included_AI_credits × FX
gross_margin(tenant)     = 1 − infra_cost_month / revenue_month          (before support, A6)
```

| Tier (from the commercial model) | Orders/month | AOV | GMV/month | Revenue/month | Infra + AI cost | Infra gross margin |
|---|---|---|---|---|---|---|
| Starter | 1,000 | ₹1,000 | ₹10 L | ₹7,999 | ₹1,408 | 82% |
| Growth | 10,000 | ₹1,200 | ₹1.2 Cr | ₹44,999 | ₹5,720 | 87% |
| Scale | 100,000 | ₹1,200 | ₹12 Cr | ₹2,39,999 | ₹46,640 | 81% |
| Enterprise (dedicated cell) | 1,000,000 | ₹1,500 | ₹150 Cr | ₹27 L | ₹10.6 L | 61% |

After support (A6), blended gross margin lands at about **75–78%** for the shared tiers. Dedicated cells carry a lower margin, which is why they are priced as a separate line item.

**Sensitivity.** If the real per-order cost is double A2 ($0.008), infra margins fall to 78% (Starter), 80% (Growth) and 66% (Scale). The P1 load test must measure A2 before any price list is published.

## 4. AI cost model
```text
cost_per_call = input_tokens × price_in(model) + output_tokens × price_out(model)   (provider price sheet)
monthly_ai_cost(use case) = calls × cost_per_call × (1 − cache_hit_rate)
```
Controls (U49): every use case has an `AIBudget` with a rolling window and an `onExceed` action (block, downgrade route or alert). Routing sends high-volume extraction and classification to `claude-haiku-4-5-20251001`, general assistance to `claude-sonnet-5-5`, and complex planning to `claude-opus-5-5`. Prompt caching and response caching apply where outputs are deterministic. Each tier includes AI credits ($2, $15 or $120 a month); usage above that is billed at cost plus 20%.

## 5. FinOps practices
- Tag everything by `cell`, `tenant`, `capability` and `environment`. U72 cost signals feed showback per tenant and per capability.
- Keep cell utilisation at 60–75%. Add cells rather than scaling one cell beyond its tested envelope.
- Commit to reserved capacity or savings plans after six months of stable baseline usage, which typically saves 30–40% on baseline compute.
- Non-production environments scale to zero outside working hours. Previews and sandboxes have TTLs set as U13 triggers.
- The cost per order (A2) is a tracked KPI with an alert at +25% month over month.

## 6. What this model does not include
Payment processing and fund flows (UCOS is not a payment aggregator; marketplace payouts use PSP split and route products), taxes on revenue (GST/VAT are charged on top), and capitalisation and depreciation policy. Finance owns those.
