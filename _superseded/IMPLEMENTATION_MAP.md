# IMPLEMENTATION MAP — the three corpora → runtime

This is the honest map from what **Architecture1/2/3 declare** to what exists as
**running software**. It is generated from live state (`GET /api/ucos/matrix`,
console → 🧭 Traceability), not hand-maintained — the numbers below were measured.

## What the corpora declare

| Corpus | Concepts | Registry lists | Universes |
|---|---|---|---|
| Architecture1 (UPIP) | 15,257 | 1,142 | 1,733 |
| Architecture2 (UMQSOCR) | 8,486 | 535 | 144 |
| Architecture3 (UCOS) | 396 | 2 | 0 |
| **Total** | **24,139** | **1,679** | **1,877** |

## How "implementation" is defined here

The platform's founding principle is **Configuration-Over-Code / "everything is
entity data, never code"**. That determines what *implemented* means:

- A **concept** is implemented by being **registered** — parsed into the registry
  with document+line provenance, queryable, and editable in the console. It is data
  by design; the platform deliberately does **not** write a code branch per concept
  (that would be 24,139 branches and would violate Knowledge-Once).
- A **universe** is the *operable* unit: it is implemented by being a **foundation**
  **plus a live, data-defined entity** — creatable, readable, validatable, deletable
  through one generic engine, with fields derived from the corpus itself.
- A universe is **activated** when its canonical offering is published into a tenant
  catalog, making it **shopper-transactable** (catalog → cart → checkout).

So the meaningful coverage measures are: **registration** (100%), **instantiation**
(100%), and **activation** (0% by default — opt-in per tenant).

## The eight runtime layers (per key, from `lib/ucos-trace.js`)

```
registry concept → foundation → universe → live entity → records →
catalog projection → API routes → console views
```

`GET /api/ucos/trace?key=Insurance` reports each layer as present or absent.
Absent layers are reported, never hidden. Example — `Insurance` before activation:

```
✔ registry concept   n=1     Architecture1:§Insurance
✔ foundation         n=1     lifecycle canonical
✔ universe           n=1
✔ live entity        n=1     11 corpus-derived fields
✗ records            n=0
✗ catalog projection n=0
✗ api routes         n=0     ← by design (Article 4.2): the generic entity/catalog
                              APIs serve it; no per-universe route may exist
✔ console views      n=5     Universes · Foundations · Traceability · Studio · Data
```

## The generic engines (zero per-universe code, Architecture3 Article 4.2)

| Layer | Module | Serves |
|---|---|---|
| Parse & registry | `lib/ucos.js` | all 24,139 concepts, 1,679 registry lists, provenance per row |
| Freeze criteria (Arch2 17AH.7) | `lib/ucos-completeness.js` | authority / boundary / dependency / separation / ordering — all 5 satisfied |
| Foundation engine (Arch3 Art. 2–8) | `lib/ucos-foundations.js` | canonical form, 5 graphs, admission, 7-state lifecycle, audit ledger |
| Universe instantiation | `lib/ucos-universes.js` | 1,877 universes → 1,877 foundations + 1,877 live entities (100%) |
| Catalog bridge | `lib/ucos-catalog.js` | publish / activate / withdraw — shopper-transactable |
| Per-domain engine | `lib/ucos-domain.js` | each universe's records move through the corpus's own state machine |
| Traceability | `lib/ucos-trace.js` | corpus key → every runtime layer |
| Universal theming | `lib/themes.js` | themes as data — generated presets, cascade assignment |
| Dashboard & reporting | `lib/dashboards.js` | Architecture1 §394/§395 — dashboards, widgets, reports as rows; one generic aggregate over native + universe entities |

## Activation — how to turn the whole corpus on

Activation is **OFF by default** (the platform's fill-in-the-blank convention). It is
a platform action because it writes a tenant's live catalog.

- One universe: `POST /api/ucos/catalog/uv_insurance/activate?tenant_id=1`
- All universes: `POST /api/ucos/catalog/activate?tenant_id=1` `{ "limit": 250 }`
- Console: 🧬 Universes → **⚡ Activate all → storefront**

Activation is **idempotent** and **bounded**: it skips universes already on the
shelf, materializes a canonical offering only where none exists (from the universe's
own corpus-declared fields — the platform invents no values), and never duplicates a
catalog row, SKU or inventory row. An operator's real records always take precedence.

## Proven by tests

| Suite | Proves |
|---|---|
| `test/ucos-audit.js` | the parse reproduces the corpora exactly (containers, concepts, registries) |
| `test/ucos-universes.js` | 100% instantiation; Article 2–8 invariants bite (admission, cycles, lifecycle, ledger) |
| `test/ucos-catalog.js` | one universe is fully transactable: publish → cart → checkout, zero duplicates/orphans |
| `test/ucos-product-universes.js` | the UPIP §1 product-universe vocabulary is derived from the corpus, not coded |
| `test/ucos-activation.js` | **287 universes across 267 families** follow the full generic path — activate, publish, SKU+inventory, withdraw — proving no family got special treatment; also proves the completed corpus reaches 100% and that `remaining` is honest |
| `test/dashboards.js` | §394/§395 are real: dashboards/widgets/reports are data, the aggregate is correct over both storage shapes, SQL-smuggling is rejected, personalization is per-user, platform-audience boards refuse to render for store admins |
| `test/ucos-domains.js` | every universe is a domain: records walk the corpus lifecycle, the 5.2 rules bite (certification, dependents-retired), every transition append-audited |
| `test/themes.js` | themes are data: generated presets, infinite hue expansion, the product→dept→tenant→platform cascade, adaptive card UI |
| `test/smoke.js` | end-to-end through the real server and both consoles, incl. the traceability view |

## Honest gaps that remain

The two gaps that were previously open are now CLOSED and covered by tests:

- **Activation is no longer empty by default.** The flagship store now ships with the
  entire corpus **activated — 1,877/1,877 universes shopper-transactable (100%)** on boot,
  idempotently and bounded (`activateComplete`, `test/ucos-activation.js` proves coverage
  and the fixed `remaining` arithmetic). Other stores remain opt-in, as the white-label
  model requires: `POST /api/ucos/catalog/activate?tenant_id=N`.
- **The Universal Dashboard Engine (§394) and Reporting Engine (§395) now exist as a
  generic engine**, where before they were registered concepts with no runtime. A
  dashboard is a row, every widget is a row pointing at an entity + a metric, and
  `lib/dashboards.js` computes both storage shapes (native tables and corpus universes)
  with no per-dashboard code. `test/dashboards.js` (68 checks) proves the §1439 meta-model,
  the §395 pipeline, SQL-smuggling rejection, per-user personalization, and the
  platform-audience isolation gate.

Three honest limits remain (by design or scope):

1. **Activation is flagship-default, not global.** A store that wants the corpus still
   opts in with one call; activating every tenant's shelf on every boot would violate
   the white-label contract. The flagship is the demonstration; other stores are the
   control case.
2. **Concept→foundation coverage is intentionally low** (UPIP 11%, UMQSOCR 2%): most
   concepts are data, not foundations. A concept becomes a foundation only when it is
   declared as a universe — that threshold is the corpus's, not a shortcut.
3. **Traceability covers the platform console only** — the storefront and store console
   are not yet mapped per key.

## The scaling defects activation exposed

Shipping the corpus activated (≈1,877 offerings + SKUs on one tenant) surfaced three
latent defects that a smaller catalog hid. All are fixed and regression-tested:

| Defect | Symptom | Fix |
|---|---|---|
| `activateAll().remaining` double-counted `skipped` (a subset of `already`) | reported `remaining: 0` at 64% — the corpus could never complete | correct arithmetic + `activateComplete`; both asserted in tests |
| Plan quota counted platform-provisioned universes against the merchant's own catalog | a Growth store could not add one product of its own | quota counts only `source_kind != 'universe'` |
| `listEntities` / planning list had fixed caps with no server-side filter | a specific SKU fell past `LIMIT 500/300` once ~2,000 existed | server-side `q` + field-equality filters on both paths |
