# Sub-processor register (template)

> **Template for legal review.** Provider names are placeholders until contracts are signed. The register is maintained as data (U67) and this page is generated from it once the platform runs.

Customer-selected providers (the Customer's own PSP, carrier, messaging or tax-engine accounts) are the Customer's processors, not UCOS sub-processors. They are listed in the Customer's admin console under integrations.

| Sub-processor | Purpose | Data | Location | Applies to |
|---|---|---|---|---|
| `[Cloud provider]` | Hosting of cells, storage, backups | All tenant data | Region of the Customer's cells (e.g. India: Mumbai; UAE: `[region]`) | All customers |
| `[CDN / edge provider]` | Content delivery, DDoS protection, TLS termination | Request metadata, cached public content | Global edge | All customers |
| `[Email delivery provider]` | Transactional email sent by UCOS on the Customer's behalf | Recipient address, message content | `[region]` | Customers using platform email |
| `[Observability provider]` (if not self-hosted) | Logs and metrics with personal data redacted | Pseudonymous identifiers only | `[region]` | All customers |
| `[AI model provider]` | AI features the Customer enables (U49 gateway) | Prompts and context permitted for the use case; no training on Customer data | Per routing policy (residency-constrained) | Customers who enable AI features |
| `[Support tooling provider]` | Customer support tickets with UCOS | Contact details, ticket content | `[region]` | All customers |

Changes: notified at least 30 days in advance (DPA §3).
