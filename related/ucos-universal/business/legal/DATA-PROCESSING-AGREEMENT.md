# Data Processing Agreement (template)

> **Template for legal review.** Drafted to cover India's DPDP Act 2023 and Rules, UAE Federal Decree-Law 45/2021 (PDPL), and the GDPR where it applies. Counsel must confirm each clause per jurisdiction.

**Roles.** The Customer is the data fiduciary / controller. UCOS is the data processor and processes personal data only on the Customer's documented instructions, which are the Terms, this DPA, and the Customer's configuration of its Tenant Platform.

## 1. Processing details
| Item | Description |
|---|---|
| Subject matter | Operation of the Tenant Platform |
| Data subjects | The Customer's buyers, sellers, staff, partners and other parties it records |
| Categories | Identity and contact data, addresses, order and payment references (no card numbers, see §4), communications, device and session data, and any categories the Customer configures |
| Special categories | Only where the Customer configures them (for example health data in a clinic pack); such fields are classified `restricted` |
| Duration | The term of the Terms plus the export and deletion period |
| Location | The region(s) of the cells chosen for the Customer (ADR-002, ADR-028). Changes need the Customer's written approval. |

## 2. Processor obligations
2.1 Process only on documented instructions. Inform the Customer if an instruction appears to break the law.
2.2 Personnel are bound by confidentiality, and production access is just-in-time, approved and recorded (break-glass with dual approval).
2.3 Assist the Customer with data-subject requests. The platform provides access, correction, erasure and portability functions (U66 `privacy.dsr`), with erasure reaching search indexes, caches, analytics and backups (control `ucos.ctrl.dsr-erasure`, gate `CMP-021`).
2.4 Assist with impact assessments and consultations with authorities using the platform's processing register and control evidence (U67, U68).
2.5 Delete or return personal data at the end of the service (Terms §4.2).
2.6 Make available the information needed to demonstrate compliance, including certification reports (SOC 2, ISO 27001 when held) and evidence packs.

## 3. Sub-processors
UCOS uses the sub-processors listed in SUB-PROCESSORS.md. It gives at least 30 days' notice of a new sub-processor, and the Customer may object on reasonable data-protection grounds. Sub-processors are bound by terms at least as protective as this DPA.

## 4. Security measures (summary)
- Tenant isolation with database row-level security and tenant-scoped keys (ADR-020), tested continuously (`SEC-TENANT-01`).
- Encryption in transit (TLS 1.2+) and at rest; national IDs and bank account numbers are tokenised (ADR-029).
- Card data never enters UCOS: card entry uses payment-provider hosted fields (PAY-L1, `SEC-PAY-01`).
- Phishing-resistant MFA for all business users (`SEC-ID-01`).
- Tamper-evident audit trail of every action (U68).
- Signed, scanned software supply chain (ADR-009).
- Backups with tested restores for critical services (`DR-01`).

## 4a. Contact
Data-protection and security contact for UCOS: Bipin Kumar, bipin.kumar@aol.com (copy bipin1@gmail.com). A grievance officer for India (DPDP) and a UAE contact are named before the first customer contract.

## 5. Personal data breaches
UCOS notifies the Customer without undue delay and in any case within `[24]` hours of becoming aware of a breach affecting the Customer's personal data. The notice includes the nature of the breach, categories and approximate numbers affected, likely consequences and measures taken. This lets the Customer meet its own deadlines (for example, India's CERT-In 6-hour reporting and DPDP notification to the Board and affected people).

## 6. Cross-border transfers
Personal data is stored in the cells chosen for the Customer. Transfers outside those regions happen only for listed sub-processors or on the Customer's instruction, and with a transfer mechanism recorded in the platform (standard contractual clauses, adequacy, or a permitted transfer under DPDP and PDPL).

## 7. Audits
The Customer may audit once a year, or after a breach, primarily through reports and evidence packs. On-site audits need 30 days' notice and a confidentiality agreement.
