# 05 — PLATFORM-AS-CONFIGURATION · UNIVERSE-AS-COMPOSITION · CONFIGURATION-FIRST

> **Mission:** UCOS-NUCLEUS-001. **Owners:** composition → `09-PLATFORM/PLATFORM-010`; blueprint → `EC2-EPIC-006`; commerce exemplar → `BUC-002`.
> **Mode:** EXTEND scope; no new composition engine (the engine exists: `engine/runtime/composition.py`, `engine/factory`, `engine/compiler`).

---

## 1. Universe = governed composition of Nuclei

**Model:** a Universe is NOT a canonical concept; it is a *governed composition* of complete Nuclei plus configuration. This is REUSE of the existing `BUC-002` "reference composition" pattern (Offer = Product×Pricing×eligibility; Party = Identity×Org×Communication) and `PLATFORM-010` composition.

Canonical exemplar to record (from `BUC-002`, no new content):
```
Commerce Universe := compose(
    Product(UNI-064), Catalog(frontier), Pricing(UNI-065), Offer(frontier),
    Inventory, Order, Payment(→Currency UNI-067), Tax, Customer/Party(UNI-010/075/039),
    Supplier, Logistics/Fulfilment/Return/Refund, Contract, Workflow, Policy(CEP)
) + configuration
```
Rule (from `MCP-001`): *no universe owns another; exactly one canonical instance per concern* → compositions REFERENCE Nuclei, never copy them (Knowledge Once).

**New index to author:** `02-MASTER/UCOS-Ω∞-UNIVERSE-COMPOSITION-CATALOG.md` — for each Universe (Commerce, Retail, Healthcare, …), the Nuclei set + configuration profile. Pure references; zero duplicated concept content.

---

## 2. Platform = configuration (not implementation)

**Model:** a Platform is realizable **entirely by configuring complete Nuclei/Universes** — no bespoke platform code. This EXTENDS `PLATFORM-005` (meta-model) + `PLATFORM-010` (composition) + blueprint catalog (`EC2-EPIC-006`), already scoped as E1/E3 in `05-CANONICAL-INTEGRATION-PLAN.md`.

Configurable platform targets (all as configuration profiles, no redesign):
Marketplace · Retail · B2B · B2C · Healthcare · Government · Manufacturing · Education · Finance · ERP · CRM · Supply Chain · Defense · Space · Research · **future unknown / unlimited**.

Each target = `blueprint(selected Universes) + configuration(Nuclei parameters)`. New platform = new blueprint + config, **not** new architecture.

---

## 3. Configuration-First invariant (to formalize — resolves G-CFG)

**Invariant CFG-1:** *No source-code modification shall be required because of business behaviour. All business behaviour is expressed as declarative constitutional configuration, and configuration supports unlimited future evolution.*

Owner: EXTEND `PLATFORM-010`. Backing mechanisms that already exist:
- Declarative composition + universal compiler (`06-IMPLEMENTATION/UCOS-Ω∞-UNIVERSAL-COMPILER`).
- Blueprint catalog (`EC2-EPIC-006`).
- Registry-driven, pattern-free engines (`engine/discovery` "no hard-coded patterns").

**Scope to implement:** a per-Nucleus `configuration_schema` (NUC-META §2) + a Universe/Platform composition-config schema, validated by `engine/validation`, so behaviour (pricing rules, commission structures, calendars, tax rules, workflows) is data.

**Honesty caveat:** Configuration-First for *business behaviour* is achievable on the current substrate. It does **not** by itself remove the engine-level closed enums (LifecycleStatus/TRACE_STAGES/DiscoveryKind) or schema ID/volume ceilings — those are *architectural* vocabularies, tracked separately as ZF-1…ZF-5 (`06-…`). Configuration-First ≠ Zero-Finite; both are required for the full mission claim.

---

## 4. Backward compatibility

- Existing `UNI-*`/`DOM-*`/`ENG-*` owners are unchanged on disk; they gain a Nucleus profile (annotation) only.
- Existing compositions (`BUC-002`, PLATFORM-010) are referenced, not rewritten.
- The 314+ IMPLEMENTED concepts and frozen corpus are untouched (`Zero Regression`).

---
*End of 05-PLATFORM-CONFIG-AND-UNIVERSE-COMPOSITION.md*
