# Threat models

The models below use **STRIDE**: Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege. They cover the Phase 0–1 surfaces plus a Phase 3 communication addendum. Every capability manifest's `security.threatModel` points to one of these files, and `tools/ucos_check.py` fails if the file is missing. That is the automatable part of gate `SEC-TM-001`; the review itself is evidence recorded by U74.

| Model | Covers | Capabilities |
|---|---|---|
| [TM-KERNEL](kernel-and-tenancy.md) | Gateway, command bus, object service, tenancy (RLS), outbox and events, control plane, composition and activation, pack supply chain | all packs (baseline) |
| [TM-IDENTITY](identity.md) | Authentication, sessions, MFA/passkeys, federation and social login, role grants, delegation, verification | identity.* |
| [TM-PARTY-PRIVACY](party-and-privacy.md) | Personal data, contact points, consent, DSR (export, erase), retention | party.core, privacy.* |
| [TM-COMMERCE](commerce-checkout-order.md) | Cart, checkout, pricing, offers and coupons, orders, returns | commerce.*, order.core, pricing.engine, offer.* |
| [TM-PAYMENT](payment.md) | Payment intents, PSP adapters and webhooks, COD, refunds, card data scope | payment.* |
| [TM-TAX-DOCS](tax-and-documents.md) | Tax determination, e-invoicing (IRN), document rendering and signing | tax.*, document.core |
| [TM-GEO-FULFIL](geo-and-fulfillment.md) | Addresses, geocoding, location data, carriers, tracking, pickup | geo.core, fulfillment.core, carrier.* |
| [TM-COMM](communication.md) | Templates, sending, OTP, inbound, in-app; P3: chat, voice, video, contact centre | communication.*, messaging.*, rtc.*, contactcenter.core |
| [TM-INTEGRATION](integration-webhooks.md) | Connectors, outbound and inbound webhooks, secrets for third parties, sync jobs | integration.core, adapters |
| [TM-WEB](storefront-and-admin-ui.md) | Storefront, tenant admin, SEO surfaces, uploads | ui.*, seo.core, asset.core |

**Rating.** Likelihood (L) and impact (I) are each scored 1–3; risk = L × I. A risk of 6 or more is high and must be mitigated before the gate passes. Residual risks of 3–4 need an owner and a due date in U67.

**Cadence.** Each model is reviewed before its phase's exit, on any material change (new entry point, new data class, new provider), and at least every 12 months.
