# U99 — Digital Assets & Distributed Ledger Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U99-digital-assets` |
| Layer | L5 Business Capability / L9 Integration |
| Domain | 04 Commerce (fintech) |
| Steward | `ucos:org:fintech-digital-assets` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P6 (optional pack family; jurisdiction-gated) |
| Depends on | U14 Currency + U77 MonetarySystem (crypto/stablecoin/CBDC/in-game currencies), U30 Ledger (off-chain books), U29 Payment (crypto acceptance via PSP), U84 Stored Value (custodial balances), U09 Identity (KYC, travel rule), U65 Security (key custody/MPC/HSM), U67 Compliance (VASP rules), U43 Asset (NFT media), U18 Product (tokenised product passports), U13 Temporal (see TEMPORAL-BINDING-MATRIX) |
| Depended on by | loyalty tokens, digital collectibles, tokenised assets, product digital passports (EU DPP), proof-of-authenticity, virtual-world economies (U77 realities) |
| Master references | Master Economic Universe "Tokenization, Digital Assets" (A-44) |

> Digital Assets owns **interaction with blockchains and tokenised value**: chain/network registry, token definitions (fungible, non-fungible, semi-fungible), wallets (custodial via licensed custodians/MPC, non-custodial connections), on-chain transactions and their confirmation tracking, smart-contract adapters (mint, transfer, burn, redeem), token-gated entitlements, product passports/authenticity certificates anchored on-chain, and reconciliation of on-chain state with the Ledger (U30). The off-chain Ledger remains the financial book of record for UCOS tenants.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| DA-L1 | Activities regulated as virtual-asset services (custody, exchange, transfer) run only via licensed partners or licensed tenants per jurisdiction. | Composer rules (like FIN-L1); gap blocks activation. |
| DA-L2 | Private keys are never held in application memory/storage; custody via MPC/HSM providers with policy-controlled signing. | Architecture; adapter contract. |
| DA-L3 | On-chain events are reconciled to Ledger entries; finality thresholds per chain decide when value is recognised. | Reconciliation workflow; `confirmationsRequired` per network. |
| DA-L4 | Personal data is never written on-chain; only hashes/commitments with off-chain storage (erasure compatibility). | Adapter lint + review. |

## 2. Objects
`Network { id (eth-mainnet, polygon, solana, bitcoin, hyperledger-x, cbdc-pilot), kind: public|permissioned, finality rule, fee model }` · `TokenDefinition { network, standard (ERC-20/721/1155, SPL…), contract address, monetarySystem/currency link (U77/U14) or asset link (U18/U79), issuer, supply rules }` · `Wallet { owner, kind: custodial|mpc|external-connected, network addresses, custodian, policies (limits, approvals) }` · `ChainTransaction { network, hash, kind, from/to, token, amount, status: pending|confirmed|final|failed|reorged, confirmations, ledgerEntry }` · `ProductPassport { gproduct/unit, data (off-chain JSON-LD), anchor (on-chain hash), issuer, versions }` · `TokenGate { entitlement (U28), condition (holds token X ≥ n) }`.

## 3. Commands, Queries, Events, APIs
Commands: `RegisterNetwork/Token`, `CreateWallet` (via custodian), `ConnectExternalWallet` (signature challenge), `Mint`, `Transfer`, `Burn`, `RedeemTokenForGoods` (RealityLink if virtual→physical), `AnchorPassport`, `Reconcile(network, range)`.
Events: `digital-asset.transaction.confirmed|finalized|failed`, `digital-asset.passport.anchored`.
Ports: `custody.provider` (Fireblocks, BitGo, Copper, Anchorage — examples), `chain.node` (RPC providers/self-hosted), `travel-rule.provider`.
```text
POST /v1/digital-assets/wallets   POST /v1/digital-assets/transfers   GET /v1/digital-assets/transactions/{hash}
POST /v1/digital-assets/passports
```

## 4. Gaps, AI, Ops, UI, Scale
```prolog
gap(vasp_licence_missing, T, J) :- tenant(T), digital_asset_service(T, S, J), regulated_vasp(S, J), not licence_or_partner(T, S, J).
gap(onchain_unreconciled, N)    :- network(N), unreconciled_tx_older_than_hours(N, 24, C), C > 0.
gap(pii_onchain_risk, A)        :- adapter(A), writes_onchain(A), not pii_lint_pass(A).
```
AI: transaction monitoring (AML), anomaly detection. Signals: `tx_finality_seconds{network}`, `reconciliation_breaks`, `custody_approval_latency`. Views: wallet view, token admin, passport viewer (QR on product → passport page), reconciliation console. Regulatory seed: FATF travel rule, EU MiCA, India (PMLA VDA reporting, tax), UAE VARA/ADGM. T2 (optional pack family).

## Appendix
- **C.** 0.1.0.
