# 03 — CANONICAL NUCLEI CATALOG · OWNERSHIP MAPPING · NEW STRUCTURE

> **Mission:** UCOS-NUCLEUS-001 · Deliverables **5** (Nuclei catalog) and **4** (new canonical structure).
> **Rule:** every Nucleus maps to exactly ONE existing owner (REUSE/EXTEND) or is flagged **NEW** only where grep of `02-MASTER/**` found no owner. Zero Duplication.

---

## 1. Ownership legend

- **REUSE** — owner exists and is sufficient; reference only.
- **EXTEND** — owner exists; attach Nucleus completeness/Zero-Finite profile + realization scope.
- **NEW*** — no owner found; candidate NEW **subject to Reuse-First** before authoring.

---

## 2. Foundational / cross-cutting Nuclei (all EXTEND — owners exist)

| Nucleus | Canonical owner (evidence) | Class |
|---|---|---|
| Identity | `UNI-010 Identity Universe` + `ENG-001` + `id-ledger.json` | EXTEND |
| Space / Location | `UNI-005 Space Universe` (abstract frame, RAT-03) + `UNI-053/054/055/056` Geography/Country/Territory/City | EXTEND |
| Time | `UNI-006 Time Universe` (`DOM-0020`, `CAP-0083..0087`, `CMP-0158..0165`) | EXTEND |
| Calendar | `DOM-0021 Calendars` (`CAP-0088..0091`, `CMP-0168..0173`) | EXTEND |
| Scale | `UNI-007 Scale Universe` | EXTEND |
| Observer / Perspective | `UNI-008 / UNI-009` | EXTEND |
| Reality | `UNI-011 Reality Universe` | EXTEND |
| Meaning / Values | `UNI-012 / UNI-013` | EXTEND |
| Language / Communication | `UNI-037/038/039` (`DOM-0170..0173`) | EXTEND |
| Value / Currency | `UNI-067 Currency` + `ENG-003 Value` | EXTEND |
| Knowledge / Memory / Intelligence | `UNI-027/028/029` + `engine/knowledge` + `intelligence/` | EXTEND |
| Organization | `UNI-075 Organization` | EXTEND |
| Policy / Rules | `CEP` policy layer + governance | EXTEND |
| Workflow | `RUNTIME` workflow + reference-universe `Workflow` layer | EXTEND |
| Event | reference-universe `Event` layer + RL-F2 `RUNTIME-008` | EXTEND |

## 3. Commerce-domain Nuclei (all owners exist per BUC-002 — EXTEND)

`BUC-002` already models commerce as a composition; each part is an existing owner.

| Nucleus | Canonical owner (BUC-002 evidence) | Class |
|---|---|---|
| Product | `UNI-064` (Product, Variant, Attribute-set, LifecycleState) | EXTEND |
| Catalog | frontier over `UNI-064` + Taxonomy `UNI-036` + SearchIndex | EXTEND |
| Pricing | `UNI-065` (PriceModel, PriceBook, DiscountRule, DynamicPricingPolicy) | EXTEND |
| Offer / Promotion | frontier over Product+Pricing (`DOM-0283 Discounts`, promotions net-new specialization) | EXTEND |
| Inventory | inventory concern (reference over Product + Location) | EXTEND |
| Order | order concern (reference composition) | EXTEND |
| Payment | payment concern over Currency `UNI-067` (`SPEC`) | EXTEND |
| Tax | tax concern over Value/Currency (`SPEC`) | EXTEND |
| Customer / Party | `UNI-010/105` Identity + `UNI-075` Org + `UNI-039` Comm (BUC-002 "reference composition") | EXTEND |
| Supplier | Party specialization (`DOM-0275/0276` roles) | EXTEND |
| Logistics / Fulfilment / Return / Refund | logistics/fulfilment concerns over Order + Location + Workflow (`SPEC`) | EXTEND |
| Contract | contract concern over Party + Policy (`SPEC`) | EXTEND |

## 4. Genuine candidate-NEW (Reuse-First required)

| Nucleus | Evidence of absence | Determination |
|---|---|---|
| **Commission** | grep of `02-MASTER/**` for "commission"/"Commission" → **no owner** | **NEW\*** — but first adjudicate vs Pricing `UNI-065` / Discounts `DOM-0283` / Dynamic Pricing `DOM-0284`. If Commission is a value-distribution model distinct from price formation → author as a new domain under a Value/Commerce universe; else EXTEND Pricing. |
| **Nucleus primitive** (formal) | `GAP-1` (`04-REPOSITORY-GAP-ANALYSIS.md`) | EXTEND S2-03 (per `02-…` adjudication), not standalone NEW. |

**No other NEW is warranted.** Every domain the mission enumerated (Time, Calendar, and all commerce parts) already has a canonical owner.

---

## 5. New canonical repository structure (deliverable 4)

The structure is **additive and profile-based** — it does NOT reorganize existing zones (Zero-Regression). It adds a Nucleus *view/index* over existing owners.

```
00-MASTER/UCOS-NUCLEUS-001/            ← this mission (scope)
00-CEP/CEP-0XX-NUCLEUS-CONSTITUTION    ← EXTEND (amendment, CEP-009 governed)   [to author]
02-MASTER/
  UCOS-Ω∞-NUCLEUS-REGISTER.md          ← NEW index: maps every UNI-*/ENG-*/DOM-* → Nucleus profile
  UCOS-Ω∞-UNIVERSE-COMPOSITION-CATALOG.md ← NEW index: Universe = {Nuclei}; commerce/retail/etc. as compositions
  (existing UNIVERSE/DOMAIN/CAPABILITY/COMPONENT catalogs EXTENDED with a "Nucleus profile" column)
09-PLATFORM/
  PLATFORM-005 / PLATFORM-010          ← EXTEND: Platform-as-configuration, Universe-as-composition, Config-First
00-BOOK/
  REGISTRIES/* + DATA/*.json           ← REGENERATE on registration
  SCHEMAS/artifact.schema.json         ← EXTEND (ZF-1..ZF-5) to lift finite ceilings [conditional]
engine/**                              ← UNCHANGED (registry-driven engines already generic)
```

The two NEW index files (`NUCLEUS-REGISTER`, `UNIVERSE-COMPOSITION-CATALOG`) are the only genuinely new canonical documents; both are *indices/views*, carrying no duplicated concept content — they reference owners. This preserves Knowledge Once.

---
*End of 03-CANONICAL-NUCLEI-CATALOG-AND-OWNERSHIP.md*
