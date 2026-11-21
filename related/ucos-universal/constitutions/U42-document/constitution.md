# U42 — Document Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U42-document` |
| Layer | L5 Business Capability |
| Domain | 06 Experience |
| Steward | `ucos:org:experience-documents` |
| Version | 0.1.0 (Draft) |
| Delivery phase | **P1** (templates, rendering of tax invoices/credit notes/receipts/shipping labels & packing slips, immutable storage, numbering hand-off from U31), P2 (e-signature, contracts with U89, document versioning workflows), P4 (AI document understanding at scale) |
| Depends on | U43 Asset (storage, renditions), U15 Localization (multilingual templates, RTL), U14 Currency (money formatting), U13 Temporal (validity, retention, signing deadlines), U65 Security (signing keys, encryption), U68 Audit (evidence), U04 Meta (data binding schemas), U31 Tax (invoice data and numbering), U66 Privacy (retention) |
| Depended on by | U31 Tax (tax documents), U26 Order (invoices, receipts), U35 Fulfillment (labels, packing slips, delivery notes), U89 Contract, U101 QHSE (controlled documents), U103 (minutes), U68 (evidence packs), U40 Communication (attachments) |
| Master references | §6.2 U42; Phase 1 blocker (legal requirement: GST/VAT tax invoices) |

> Document owns **generated, versioned, legally meaningful documents**: document templates (layout + data binding + localisation), rendering to PDF/HTML/image/ZPL (thermal labels) and structured formats (UBL/PEPPOL, India e-invoice JSON is produced by U31 and embedded as IRN/QR), document instances that are **immutable once issued**, versions/amendments, digital signatures (PAdES) and seals, e-signature envelopes (P2), and document delivery. Binary storage is delegated to U43; legal numbering of tax documents remains in U31.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| DOC-L1 | Issued documents are immutable; corrections are new documents (credit note, amendment) referencing the original. | Status guard; content hash stored; storage object lock. |
| DOC-L2 | Every rendered document is reproducible: template version + data snapshot + locale + renderer version are recorded. | `RenderRecord`. |
| DOC-L3 | Legal documents carry jurisdiction-mandated fields; templates are validated against field requirements from compliance rules before publishing. | Template validator using U67/U31 rule outputs (e.g. India GST invoice: supplier GSTIN, place of supply, HSN/SAC, tax breakdown, IRN/QR when e-invoicing applies; UAE: TRN, "Tax Invoice" title in Arabic/English). |
| DOC-L4 | Documents with personal data follow retention and are encrypted; public links are short-lived and signed. | U43 + U66. |
| DOC-L5 | Organisation-issued PDFs requiring authenticity are digitally signed with the issuer's certificate (where law or tenant policy requires). | Signing step via U65 HSM-backed keys. |

## 2. Objects
- `DocumentTemplate { id, kind: tax-invoice|credit-note|debit-note|receipt|proforma|packing-slip|shipping-label|delivery-note|return-label|statement|contract|certificate|letter|report|custom, engine: html-pdf|label-zpl|docx|ubl-xml, version, locales: [..], dataSchema: ObjectTypeRef/JSON Schema, requiredFieldsRule: RuleRef, layout (HTML/CSS with tokens; Handlebars-safe subset), brandTheme: ThemeRef, paper: A4|Letter|4x6-label|80mm-receipt, status }`
- `Document { id, tenant, kind, template@version, subject: ObjectRef (order, tax document, shipment, agreement…), issuer: OrgRef, recipient: PartyRef?, locale, dataSnapshotRef (content-addressed), renditions: [AssetRef (pdf, html, png, zpl)], contentHash, number?: (from U31 for tax docs), issuedAt: TimePoint, status: draft|issued|superseded|voided, supersedes?: DocumentRef, signature?: {type: pades|xades|seal, certRef, signedAt: TimePoint}, retention: RetentionRuleRef }`
- `RenderRecord { document, templateVersion, rendererVersion, dataHash, locale, durationMs }`
- `SignatureEnvelope` (P2) `{ document, signers [{party, order, method: aadhaar-esign|dsc|otp|click|qualified}], deadline: TimePoint, status }`

## 3. Commands, Queries, Events, APIs
Commands: `PublishTemplate` (governed; legal kinds require compliance review), `RenderDocument(template, subject, locale)` (draft preview), `IssueDocument` (render + hash + store + optional sign; idempotent by subject+kind+version), `SupersedeDocument`, `VoidDocument` (only where law permits, e.g. within IRN cancellation window — coordinated with U31), `DeliverDocument(channel)` (via U40), P2 `SendForSignature`.
Queries: `DocumentsFor(subject)`, `Download(document, rendition)` (signed URL via U43), `VerifyDocument(hash|qr)` (public verification page for issued docs, optional).
Events: `document.document.issued|superseded|voided|delivered`.
```text
POST /v1/document/templates            POST /v1/document/templates/{id}:publish
POST /v1/document/documents:render     POST /v1/document/documents  (issue)
GET  /v1/document/documents?subject=   GET /v1/document/documents/{id}/download?rendition=pdf
```
Errors: `DOC_TEMPLATE_INVALID`, `DOC_REQUIRED_FIELD_MISSING` (with field list), `DOC_IMMUTABLE`, `DOC_VOID_NOT_ALLOWED`, `DOC_RENDER_FAILED`.

## 4. Rendering architecture
Stateless renderer service: HTML template + data → headless Chromium (PDF) or ZPL generator (labels) or XML serializer; fonts bundled for all supported scripts (Latin, Devanagari, Arabic with shaping, etc.); bidi correctness for Arabic; QR codes (e-invoice IRN QR, UPI pay QR, verification QR); deterministic output (fixed fonts, no network fetches during render); p95 < 800 ms for a 2-page invoice.

## 5. Phase 1 template set (seed)
India: GST tax invoice (B2C, B2B with e-invoice IRN/QR), bill of supply, credit note, payment receipt; UAE: tax invoice (simplified & full, EN/AR), credit note; shipping label 4×6 (carrier-provided label passthrough or generic), packing slip, return label, order confirmation PDF (optional). All in en / hi / ar where relevant.

## 6. Gaps, AI, Ops, UI
```prolog
gap(no_invoice_template, T, J) :- tenant(T), in_scope(T, J), invoice_required(J), not published_template(T, tax-invoice, J).
gap(template_missing_locale, Tpl, L) :- template(Tpl), used_in(Tpl, T), required_doc_language(T, L), not template_locale(Tpl, L).
```
AI (P4): document understanding (supplier invoices, KYC docs) produces structured proposals; template drafting from sample PDFs. Signals: `render_latency_ms`, `render_failures_total`, `documents_issued_total{kind}`. Views: `document.template.editor` (code + visual preview with sample data per locale), `document.viewer`, `document.list` (per order/customer). T1 (issue path on order confirmation; queued with retry, never blocks payment).

## Appendix
- **C.** 0.1.0.
