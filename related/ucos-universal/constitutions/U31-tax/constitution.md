# U31 — Tax Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U31-tax` |
| Layer | L5 Business Capability |
| Domain | 04 Commerce |
| Steward | `ucos:org:finance-tax` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P1 (determination, invoicing for first country), P2 (multi-country, marketplace facilitator, e-invoicing), P4+ (filings) |
| Depends on | U12 Geography (jurisdictions, tax regions), U14 Currency (rounding), U13 Temporal (rate validity, filing periods), U06 Taxonomy (tax categories), U10 Org (registrations), U11 Party (buyer tax status), U21 Catalog (unit tax category), U42 Document (invoice rendering, P2), U67 Compliance |
| Depended on by | U23 Pricing (waterfall), U24 Checkout, U26 Order, U30 Ledger (tax liabilities), U25 Marketplace (TCS/withholding) |
| Master references | §11.3 (adapter_for tax.determination), §6.2 U31 |

> Tax owns **indirect-tax determination and documentation**: tax regimes, tax categories, rules/rates with validity, determination (who taxes what, where, how much), tax documents (invoices/credit notes metadata and numbering, e-invoice registration), registrations/nexus, exemptions, and withholding/collection-at-source obligations for marketplaces. Rates and rules come from **data packs** (per regime) or **external engines** via the `tax.determination` port — never code.

---

## 1. Laws

| ID | Law | Enforcement |
|---|---|---|
| TAX-L1 | All tax amounts are produced by `Determine`; no other component computes tax. | Lint; pricing waterfall calls Tax. |
| TAX-L2 | Rules and rates are temporal facts (validity) owned by regime packs; determination records the rule versions used. | Schema + determination snapshot. |
| TAX-L3 | Determination uses explicit supply facts: seller location/registration, ship-from, ship-to, buyer status (B2B/B2C, exemption), item tax category, place-of-supply rules. Never just "country of the store". | Determination input contract. |
| TAX-L4 | Tax documents use legally compliant sequential numbering per series (gapless where required) and are immutable once issued; corrections via credit/debit notes. | Document numbering service with gapless allocation. |
| TAX-L5 | Rounding follows the regime's rule (line vs invoice level). | RoundingRule from regime pack. |

---

## 2. Ontology & Objects
- **`TaxRegime`** `{ id (e.g. in-gst, ae-vat, eu-vat-oss, us-sales-tax, uk-vat), jurisdictions, model: vat|gst|sales-tax|consumption, components (CGST/SGST/IGST/cess; state/county/city), roundingRule, invoiceRules, eInvoicing?: {authority, threshold, schema}, filingCalendar: CalendarRef, packVersion }`
- **`TaxCategory`** `{ id, regime, code (e.g. HSN/SAC for India, CN for EU, PTC for US engines), description, rateRefs }` — mapped from taxonomy `taxCategoryHint` and overridable per unit by tax admins.
- **`TaxRule`** `{ regime, category, conditions: CEL over supply facts (inter/intra-state, B2B/B2C, threshold, place of supply), components: [{name, rate: Percentage | amountPerUnit}], validity }`
- **`TaxRegistration`** `{ organization, regime, jurisdiction, number (GSTIN, TRN, VAT ID), type: regular|composition|oss|marketplace-facilitator, validity: TimeRange, verified }`
- **`Exemption`** `{ party, regime, certificate: AssetRef, scope, validity: TimeRange }`
- **`TaxDetermination`** (snapshot) `{ id, inputsHash, supplyFacts, lines: [{line, category, taxable: Money, components: [{name, rate, amount}], inclusiveExtracted?: bool}], totals, regimeVersions, engine: internal|adapter:<x> }`
- **`TaxDocument`** `{ id, kind: invoice|credit-note|debit-note|bill-of-supply|receipt, series, number, issuer: OrgRef(registration), recipient, order/adjustment refs, determination, issuedAt, eInvoice?: {irn, qr, ackNo, status}, renderedDoc: DocumentRef (P2), status: draft|issued|cancelled }`
- **`Withholding`** (marketplace) `{ kind: tcs|tds|facilitator-collection, regime, seller, base, rate, amount, period: TimeRange }`

---

## 3. Determination Algorithm (normative)

```text
determine(lines, supply, asOf):
  for each line:
    seller ← supply.sellerOf(line); regReg ← registrationsOf(seller) valid at asOf
    place  ← placeOfSupply(regime rules, shipFrom, shipTo, buyer, service-type)       # regime pack rule
    J      ← geo.resolveJurisdictions(place)
    regime ← regimeFor(J) ; if seller not registered and below threshold → exempt (rule)
    cat    ← unit.taxCategory (or taxonomy hint) mapped to regime category
    rules  ← match TaxRule(regime, cat, conditions(supply facts), validity ∋ asOf), highest specificity
    if priceList.taxMode = inclusive: taxable = gross / (1 + Σrates) (component-wise per regime method)
    else taxable = net
    components ← apply rates; round per regime (line or invoice level)
  marketplace facilitator rules may shift liability to operator (regime rule) → mark collector
  return TaxDetermination (with rule versions)
```
External engine mode: same input contract to adapter (`tax.determination` port: Avalara, Vertex, ClearTax, etc.); results normalised; internal regime packs remain the reference for simulation.

---

## 4. Commands, Queries, Events, APIs

Commands: `Determine` (stateless, called by Pricing), `CommitDetermination` (on order placement, stores snapshot), `IssueDocument(kind, refs)`, `CancelDocument` (within legal window), `RegisterEInvoice` (adapter to IRP/ZATCA/etc.), `RecordRegistration`, `RecordExemption`, `ImportRegimePack(version)` (governed).
Events: `tax.determination.committed`, `tax.document.issued|cancelled`, `tax.einvoice.registered|failed`, `tax.regime.updated`.

```text
POST /v1/tax/determine                 POST /v1/tax/documents   POST /v1/tax/documents/{id}:cancel|:register-einvoice
GET  /v1/tax/documents?order=          POST /v1/tax/registrations   POST /v1/tax/exemptions
GET  /v1/tax/categories?regime=&q=
```
Errors: `TAX_NO_RULE` (category/regime gap), `TAX_REGISTRATION_MISSING`, `TAX_DOCUMENT_IMMUTABLE`, `TAX_EINVOICE_REJECTED` (with authority code), `TAX_SERIES_EXHAUSTED`.

## 5. Decision tables
`tax.document-series` (by org, regime, doc kind, fiscal year), `tax.einvoice-applicability` (turnover thresholds), `tax.inclusive-display` (by jurisdiction/channel), `tax.category-override-approval`.

## 6. Security & Compliance
Tax IDs `confidential`; documents immutable with audit; e-invoice credentials in Vault. Regimes P1: India GST (incl. e-invoicing IRP, e-way bill hook for logistics in P2, TCS for marketplaces), UAE VAT (+ FTA e-invoicing when mandated); P2: KSA ZATCA Phase 2, EU VAT OSS/IOSS, UK VAT, US sales tax via engine adapter. Retention of tax documents per jurisdiction (e.g. 8 years India, 5–15 years elsewhere).

## 7. Reuse
Pricing waterfall → Tax; Order stores determination; Ledger (P2) posts tax liability from `tax.determination.committed`/documents; Document universe renders invoices from TaxDocument data.

## 8. Gaps
```prolog
gap(no_regime_pack, J)          :- in_scope(_, J), sells(_, J), not regime_pack_for(J).
gap(seller_unregistered, S, J)  :- seller(S), sells_in(S, J), registration_required(J, S), not tax_registration(S, J).
gap(uncategorised_units, T, N)  :- tenant(T), units_without_tax_category(T, N), N > 0.
gap(einvoice_required, T, J)    :- tenant(T), in_scope(T, J), einvoice_applicable(T, J), not capability(T, tax.einvoice(J)).
```

## 9. AI
HSN/SAC/tax-category suggestion from product data (proposal; tax admin approves), anomaly detection on effective tax rates, regulatory-change monitoring feeding regime-pack updates (proposals to steward).

## 10. Operations
Signals: `tax_determine_latency_ms` (p99 < 15 ms internal, < 300 ms adapter), `tax_no_rule_total`, `einvoice_failure_ratio`, `document_issue_lag_s`. Runbooks: e-invoice portal outage (queue + retry within legal window), rate change go-live (Temporal validity switch at midnight local).

## 11. UI
Views: `tax.category.mapper` (bulk assign with AI suggestions), `tax.registration.manage`, `tax.document.list/detail`, `tax.regime.browser` (rules & rates with validity timeline), `tax.determination.inspector` (debug a line), invoice templates (Document universe).

## 12. Scale
Determination on every quote (high QPS, in-memory rules per cell); documents ~ orders; gapless numbering via per-series allocator with short transactions (series sharded per store/GSTIN where law allows). T0 on checkout path.

## Appendix
- **A.** Build vs buy per regime: internal packs for IN/AE (P1); engine adapters for US/EU breadth.
- **C.** 0.1.0.

## Appendix P1 — Phase 1 behaviour without later-phase dependencies
- **U42 Document:** specified for Phase 1. `TaxDocument.renderedDoc` references the U42 Document. E-invoice IRN and QR are embedded at render time.
