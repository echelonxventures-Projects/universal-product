# U48 — Industry Packs Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U48-industry-packs` |
| Layer | L6 Industry |
| Domain | 09 Platform |
| Steward | `ucos:org:platform-industries` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P6 (catalogue and certification of industry packs; individual packs ship from P4 onward) |
| Depends on | U57 Capability (pack manifests, `capabilityKind: industry-pack`), U58 Composition (pack facts, rules), U74 Certification, U67 Compliance (industry regulations), U08 Reference Data (ISIC/NAICS/NIC), all business universes being composed |
| Depended on by | Tenants choosing an industry, the coverage register (ISIC 88/88 mapping), the pack marketplace (U57) |
| Master references | §6.2 U48, `constitutions/INDUSTRY-PRODUCT-DOMAIN-CATALOGUE.md`, COVERAGE-REGISTER §Z |

> Industry Packs owns **the curation of industry compositions**, not industry logic. An industry pack is a capability of kind `industry-pack` that bundles: required/recommended capabilities, industry object-type extensions (via U04 extension points), decision-table defaults, regulations and controls facts, gap rules, UI packs, seed data, reference platform definitions, and certification scenarios. U48 owns the pack taxonomy (mapped to ISIC Rev.4 / NAICS / NIC), the pack standard, maturity levels and the pack certification profile.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| IND-L1 | Industry packs add composition, configuration and extensions only; they never fork or bypass a universe (Law L4). | Pack lint: no new universes, only extensions/decisions/rules. |
| IND-L2 | Each pack declares its industry codes, jurisdictions, regulations and maturity; claims are certified by scenario tests. | Manifest fields + U74 profile `industry-pack`. |
| IND-L3 | A pack includes at least one golden platform definition that composes with 0 MANDATORY gaps. | Checker golden test (like `spec/composition/golden/`). |

## 2. Objects
`IndustryPack` (= capability manifest with `capabilityKind: industry-pack`) `{ industryCodes [{scheme: isic|naics|nic, code}], jurisdictions, requires/recommends capabilities, extensions [object-type extension refs], decisions defaults, facts (regulations, controls), gapRules, uiPacks, seedData, goldenPlatforms, maturity: alpha|beta|ga }` · `IndustryTaxonomyNode { scheme code, name, packs }` · `PackCertification { pack@version, scenarios passed, at: TimePoint, validity: TimeRange }`.

## 3. Seed packs (roadmap)
| Pack | Industry (ISIC) | Core universes | Phase |
|---|---|---|---|
| `industry.retail-d2c` | G47 | U21–U31, U35, U40 | P1 (golden `d2c-in-ae`) |
| `industry.b2b-distribution` | G46 | + U38, U89, U45 | P2 (golden `b2b-in`) |
| `industry.marketplace` | G47/N82 | + U25, U70, U71 | P2 |
| `industry.food-delivery` | I56 | + U37, U36, U19 | P5 |
| `industry.hospitality` | I55 | + U13 reservations, U83, U19 | P4 |
| `industry.healthcare-clinic` | Q86 | + U19, U17, U97 | P5 |
| `industry.education` | P85 | + U56, U27 | P5 |
| `industry.ott-media` | J59/J60 | + U41, U27, U28 | P5 |
| `industry.manufacturing-discrete` | C25–C30 | + U47, U45, U99 | P6 |
| `industry.fintech-wallet` | K64 | + U84, U100, U69 | P6 |

## 4. Commands, APIs, Gaps
Commands: `RegisterIndustryPack`, `CertifyIndustryPack`, `MapIndustryCode`, `DeprecatePack`.
```text
GET /v1/industries   GET /v1/industries/{code}/packs   POST /v1/industry-packs (via U57 publish)
```
```prolog
gap(industry_without_pack, T, I) :- tenant(T), industry(T, I), not pack_for_industry(I, _).   % INSIGHT
gap(pack_without_golden, P) :- industry_pack(P), not golden_platform(P, _).
```
Views: industry chooser in onboarding (W1 genesis), pack detail (what it adds, maturity, certifications), coverage map by ISIC. T3.

## Appendix
- **C.** 0.1.0.
