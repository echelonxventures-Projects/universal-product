# ADR-029: Format-preserving tokenisation covers national IDs and bank accounts only

| Field | Value |
|---|---|
| Status | Accepted |
| Deciders | Architecture Board (U01 root authority) |
| References | U65 Security; open decision U65 |

## Context
Card data never enters UCOS (PAY-L1). Other sensitive identifiers (Aadhaar-masked IDs, PAN, Emirates ID, bank account numbers) flow through non-PSP processes such as payouts and KYC.

## Decision
Apply **format-preserving tokenisation** to national ID numbers and bank account numbers stored by U09, U11, U25 and U46. The token vault lives in U65 with per-tenant keys. Other restricted fields use field-level envelope encryption.

## Alternatives considered
- Tokenise all PII: high cost and breaks search for little benefit.
- Encrypt only: format-dependent validations and partial display become harder.

## Consequences
**Positive**
- Downstream systems and logs only see tokens for the most sensitive identifiers.

**Negative / costs**
- The vault is a T0 dependency for those flows.

## Enforcement
Data-class lint: fields classified `national-id` or `bank-account` must use the tokenised type (`SEC-META-01`).
