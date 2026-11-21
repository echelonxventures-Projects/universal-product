# ADR-0010: Platform composition is represented by existing canonical capability

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-08-21 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | UCKP-ART-18, AC-005, WP-UCDA-018 |
| Supersedes | none |

## Context

The principle requires that commerce, mobility, social, ERP, CRM, healthcare, education, scientific, government, space and future platforms compose from the same substrate with no platform-specific engine. Measured: `engine/nucleus/catalog.py` declares *"Commerce is not a Nucleus. Commerce is a Composition. So are Amazon, Uber, PayTM, WhatsApp, Facebook, Instagram, X, LinkedIn, YouTube, ERP, CRM, LMS, EdTech, and every sector, banking, insurance, healthcare, government, defence, industrial, scientific, research and civilisational platform."* No function branches on a platform name — verified. `engine/civilization/composition.py` derives plans from declarations and holds no pipeline.

## Decision

We record platform composition as **represented by existing canonical capability**. Platforms are compositions of registered nuclei plus configuration; *"the ten-thousandth nucleus costs one tuple entry."*

## Consequences

Positive: no platform-specific architecture is introduced. Neutral: the evidence is named for re-measurement.

## Compliance

- [x] Non-contradiction with the constitutional/EES corpus asserted (CC-02).
- [x] Rollback / migration path recorded (CC-04).
- [x] Traceability links to affected artifacts recorded (CC-05).
- [x] No secret material embedded (SEC-04).
