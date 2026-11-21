# TM-PARTY-PRIVACY — Personal data, consent and data-subject rights

| Field | Value |
|---|---|
| Scope | U11 Party (persons, roles, contact points, preferences), U66 Privacy (purposes, notices, consent, DSR export/rectify/erase, retention, transfers, cookie consent) |
| Data classes | PII, SPI (sensitive personal), children's data |
| Owner | `ucos:org:privacy` (DPO function) |
| References | U11, U66; DPDP Act 2023 and Rules; UAE PDPL; GDPR; A-21 (`privacy.dsr-handler`) |

## STRIDE
| ID | Threat | L | I | Mitigations | Verification |
|---|---|---|---|---|---|
| PP-S1 | A DSR is submitted by an impostor (data exfiltration through "export my data") | 2 | 3 | Verify the requester against an existing authenticated session or verified contact points; step-up for exports; deliver exports only into the authenticated account with expiring links | DSR tests |
| PP-T1 | Consent records forged or altered | 1 | 3 | Consent is append-only with evidence (UI snapshot hash, method, notice version); records are hash-chained in U68 | Audit chain job |
| PP-R1 | Tenant denies having consent for marketing | 2 | 2 | Consent evidence is exportable for regulators; send-time checks are logged with the consent reference | U40 send logs |
| PP-I1 | Over-collection or purpose creep | 2 | 2 | Every attribute is linked to purposes; U04 lint requires a classification; processing-activity register | `SEC-META-01`; RoPA review |
| PP-I2 | Erased data persists in search, caches, analytics or backups | 2 | 3 | Every universe holding PII implements `privacy.dsr-handler`; erasure fans out by event; analytics uses pseudonymous ids; backups expire by retention with tombstone replay on restore | `CMP-PRV-01`, `CMP-021` |
| PP-I3 | Children's data processed without guardian consent | 1 | 3 | Age signals in context; guardian-consent purpose; behavioural advertising and profiling disabled for minors (DPDP §9) | Policy tests |
| PP-I4 | Cross-border transfer without a mechanism | 2 | 3 | Transfer records are required facts; residency placement (`CMP-RES-01`); global registries carry no personal data | Checker; placement review |
| PP-D1 | DSR flooding to overload operations | 2 | 1 | Rate limits per party; SLA clocks on the business calendar with statutory limits | Ops alerts |
| PP-E1 | Support agents browse personal data without a need | 2 | 2 | Purpose-bound access via Cedar obligations; masked views by default; access logging and anomaly review | Access review |

## Abuse cases to test
- Erase a party, then search by their email in storefront search, the admin, analytics and the CDP (P4): no hits expected.
- Withdraw marketing consent, then trigger a campaign send: the message must be blocked with `COM_CONSENT_MISSING`-class error.
