# Customer legal templates

**Status: templates for legal review.** These documents describe what UCOS commits to, in the terms the architecture can actually enforce. They are not legal advice and must not be signed or published before review by qualified counsel in each jurisdiction (ADR-035: in-house counsel owns interpretations, with external firms per jurisdiction).

| Document | Purpose | Backed by |
|---|---|---|
| [TERMS-OF-SERVICE.md](TERMS-OF-SERVICE.md) | Platform subscription terms between UCOS and a tenant | Commercial model, U27, U28 |
| [DATA-PROCESSING-AGREEMENT.md](DATA-PROCESSING-AGREEMENT.md) | UCOS as processor of tenant personal data (DPDP, UAE PDPL, GDPR) | U66, U65, U68, ADR-028, ADR-029 |
| [SUB-PROCESSORS.md](SUB-PROCESSORS.md) | Register of sub-processors with purpose and location | U67, U62 adapters |
| [SERVICE-LEVEL-AGREEMENT.md](SERVICE-LEVEL-AGREEMENT.md) | Uptime commitments and service credits per plan | `spec/slo/`, U72 |

Bracketed text such as `[Company legal name]` must be completed. Every commitment links to the capability or control that implements it, so legal and engineering can check them against each other.
