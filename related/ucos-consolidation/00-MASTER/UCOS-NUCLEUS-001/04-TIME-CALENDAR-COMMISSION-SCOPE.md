# 04 — TIME · CALENDAR · COMMISSION — COMPLETE IMPLEMENTATION SCOPE

> **Mission:** UCOS-NUCLEUS-001. **Mode:** Scope enumeration for future implementation. Each item is capability scope, not an engine.
> **Owners:** Time → `UNI-006` (EXTEND) · Calendar → `DOM-0021` (EXTEND) · Commission → candidate NEW (Reuse-First vs `UNI-065`/`DOM-0283/0284`).

Every capability below is tagged `[E]` (EXTEND existing owner — declared, mostly `SPEC`) or `[N]` (net-new realization scope). Nothing is assumed implemented; all are `SPEC/PLANNED` until certified.

---

## 1. TIME NUCLEUS (EXTEND `UNI-006` Time Universe / `DOM-0020` Temporal Modeling)

Existing anchor: `UNI-006` declared "Future evolution (∞): relativistic/multi-frame time, non-Earth calendars, simulation time, branching/temporal-version timelines, unknown temporal constructs" (`T02-UED-001`). This scope makes that explicit and enumerable.

| Scope item | Tag | Reuse anchor |
|---|---|---|
| Absolute Time | [E] | `CAP-0083` Time Modeling / `CAP-0085` Instant |
| Relative Time | [E] | multi-frame extension of `DOM-0020` |
| Relative Velocity / Acceleration / Motion | [N] | new temporal-kinematics scope over `UNI-006` + Physics `UNI-046` |
| Relative Frames (reference frames) | [E] | `UNI-008 Observer` + `engine/runtime/context.py` ReferenceFrame |
| Observer Time | [E] | `UNI-008 Observer` |
| Mission Time | [N] | over Scheduling `DOM-0022` |
| Simulation Time | [E] | declared future-evolution row |
| Logical Time (vector/Lamport clocks) | [E] | `DOM-0020` (logical clocks noted in historical models) |
| Event Time / Transaction Time | [E] | bitemporal over `DOM-0020` + Versioning `DOM-0023` |
| Historical Time / Future Time | [E] | History `DOM-0024` / Forecasting `DOM-0025` |
| Temporal Mathematics (interval/duration algebra) | [E] | `CAP-0086` Interval / `CAP-0087` Duration |
| Temporal Reference Systems | [N] | new TRS registry over `UNI-006` |
| Temporal Coordinate Systems | [E] | `DOM-0020` (coordinate frame, RAT-03) |
| Temporal Synchronization | [N] | new sync scope (clock reconciliation) |
| Temporal Precision / Drift / Uncertainty | [N] | new precision/uncertainty model |
| Temporal Intelligence | [E] | Intelligence `UNI-029` composed by reference |
| Planetary / Solar / Lunar Time | [N] | non-Earth frames over `UNI-005` Space + `UNI-050` Astronomy |
| Galactic / Interstellar / Interplanetary Time | [N] | relativistic multi-frame scope (Physics `UNI-046`) |
| Civilization Time | [N] | over Civilization models (parametric, `03-CONSTITUTIONAL-UNBOUNDEDNESS` axis 11) |
| Distributed Time / Virtual Time | [E] | logical/simulation time |
| Any future temporal model / unlimited | [E] | receptor `USIS-U-FUT`/`USIS-U-UNK` |

**Time Nucleus completeness (NUC-C):** ontology `DOM-0020`; taxonomy temporal-kinds; registry Time Registry `CMP-0159`; runtime `RUNTIME-007` RL-F2; certification via `engine/certification`. Gaps to realize: TRS registry, sync/precision/uncertainty, kinematics, non-Earth frames (all `[N]`).

---

## 2. CALENDAR NUCLEUS (EXTEND `DOM-0021` Calendars)

Existing anchor: `DOM-0021` (`CAP-0088` Calendar Management, `CAP-0089` Conversion, `CAP-0090` Date Arithmetic, `CAP-0091` Timezone; `CMP-0168..0173`).

| Scope item | Tag | Reuse anchor |
|---|---|---|
| Earth Calendars (Gregorian/Julian/lunar/fiscal) | [E] | `CAP-0088` + historical models |
| Planetary / Orbital Calendars | [N] | non-Earth calendar over `UNI-050` Astronomy + `UNI-005` Space |
| Lunar / Solar Calendars | [E] | `CAP-0088` (lunar/solar noted) |
| Galactic Calendars | [N] | future-evolution row |
| Mission / Organization / Fiscal Calendars | [E]/[N] | fiscal `[E]`; mission/org `[N]` over `UNI-075` Org |
| Academic / Manufacturing / Operational / Scientific Calendars | [N] | domain-specialized calendars (config profiles) |
| Simulation / Historical / Future Calendars | [E] | simulation time + History `DOM-0024` |
| Calendar Conversion | [E] | `CAP-0089` Conversion |
| Calendar Synchronization | [N] | new sync scope (shares Temporal Synchronization) |
| Unlimited Calendar Systems / future models | [E] | receptor `USIS-U-FUT` |

**Ownership boundary (from `T02-UED-001`):** temporal coordinate → `UNI-006`; calendar systems → `DOM-0021`; scheduling → `DOM-0022`. Preserve this boundary — do NOT re-home calendar logic into Time (Zero Duplication; duplicate-risk flagged LOW–MEDIUM).

---

## 3. COMMISSION NUCLEUS (candidate NEW — Reuse-First REQUIRED)

**Absence evidence:** grep of `02-MASTER/**` for "commission" → no owner. **Before authoring**, adjudicate against Pricing `UNI-065` (PriceModel/DiscountRule/DynamicPricingPolicy) and `DOM-0283 Discounts` / `DOM-0284 Dynamic Pricing`.

Adjudication guidance: Commission is **value distribution among parties after/according to a transaction**, distinct from **price formation** (Pricing). If confirmed distinct → author as a new domain (proposed `DOM-COMMISSION`) under a Value/Commerce universe, composing Party (`UNI-010/075`), Pricing (`UNI-065`), Currency (`UNI-067`), Policy (`CEP`), Workflow, Time (`UNI-006`).

| Commission model | Tag | Note |
|---|---|---|
| Percentage / Fixed / Tiered / Progressive / Regressive | [N] | rate structures |
| Revenue Share / Profit Share | [N] | base-of-calculation variants |
| Affiliate / Referral / Marketplace / Franchise | [N] | channel models over Party roles |
| Network / Hierarchical / Team | [N] | multi-level distribution over Org `UNI-075` |
| Subscription / Usage-Based / Performance-Based | [N] | metered over RL-F2 events + Metering |
| Policy-Driven / AI-Driven | [N] | over Policy (`CEP`) + Intelligence (`UNI-029`) |
| Future/unknown / unlimited structures | [N] | receptor `USIS-U-FUT` |

**Commission completeness (NUC-C) to author:** constitution (via CEP-009), ontology (commission-kinds), taxonomy, registry entry, config schema (rate/base/trigger/eligibility), validation (sum-to-whole, non-negative, policy-compliant), certification, runtime (event-triggered calculation), discovery.

**Configuration-First requirement:** all commission structures MUST be expressible as declarative configuration (rate table + base selector + trigger + eligibility rule) with **no source change** per new model (mission "Configuration First").

---
*End of 04-TIME-CALENDAR-COMMISSION-SCOPE.md*
