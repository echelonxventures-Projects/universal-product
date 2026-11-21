# Seed content (engineering/PHASE1-READINESS.md §1, S1–S15)

Data the platform needs on day one. Every file names its owner. Bundled code lists record their source and licence (ADR-027), and `tools/validate_contracts.py` checks structure, cross-references and licences on every CI run.

| Seed | Content | Files | Coverage |
|---|---|---|---|
| S1 | ISO 3166-1, ISO 4217 (with CLDR minor units), ISO 639-1, IANA tz 2026d (pinned), units | `refdata/*.yaml` | **Complete** for codes. Units: core subset; full Rec 20 / UCUM import by the U14 steward before P2 |
| S2 | ISIC, NIC, CPC, HS, SAC, GS1 GPC, UNSPSC | — | **Open.** Licences differ (ADR-027); spike S-06 records the outcome per source |
| S3 | Address formats IN and AE; subdivisions | `geo/address-formats.yaml`, `refdata/iso3166-2-*.yaml` | **Complete** for formats and subdivisions. PIN directory imported as a data pack (India Post open data) |
| S4 | Jurisdictions IN (36 states and UTs) and AE (7 emirates) | `geo/jurisdictions.yaml` | **Complete**. GST state codes filled for the 10 states used in tests; full table from GSTN by the tax steward |
| S5 | Holiday calendars 2026–2027; business-hours templates | `calendars/holidays-2026-2027.yaml` | Fixed national holidays and templates **complete**. Lunar and state holidays are imported yearly from official announcements (listed as rules, not guessed) |
| S6 | Product taxonomy | `taxonomy/product-category-v1-top.yaml` | **Top level only** (28 nodes). The ~6k-node tree and mappings are the taxonomy workstream |
| S7 | Tax regime packs GST India, VAT UAE | `tax/*.yaml` | Structure, slabs, components and the categories used in tests. Every line is `proposed` until the tax steward verifies it against current notifications |
| S8 | Compliance library | `../rules/facts/{regulations,controls}.yaml` | 26 regulations, 35 controls (Phases 0–2) |
| S9 | Message bundles en, hi, ar | `l10n/messages-core.yaml` | 25 core keys. Hindi and Arabic are machine drafts; legal keys need human review |
| S10 | Document templates | `documents/*.yaml` | GST tax invoice (Rule 46), GST credit note, UAE VAT tax invoice: required fields and legal basis |
| S11 | Default decision tables | `../decisions/*.yaml` | 16 tables with 44 executable tests |
| S12 | Platform plans | `plans/platform-plans.yaml` | **Complete** (Starter, Growth, Scale, Enterprise) |
| S13 | Industry templates | `industry-templates/*.yaml` | **Complete** for the templates the golden platforms use |
| S14 | FX sources and rate policies | `fx/rate-policies.yaml` | **Complete** (FBIL, CBUAE, ECB; display, settlement, accounting) |
| S15 | Golden test datasets | `tools/gen_golden_data.py` → `generated/golden-data/`; digest in `golden-data.sha256` | **Complete**: 5 tenants, 10,000 listings, 2,000 buyers, 5,000 orders, simulator scripts; byte-reproducible |
