# U93 — Data Governance & Data Products Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U93-data` |
| Layer | L2 Data Fabric |
| Domain | 02 Knowledge |
| Steward | `ucos:org:data-governance` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P2 (data catalog, contracts registry ownership, lineage, quality checks), P4 (data products marketplace, MDM workflows, data sharing/clean rooms) |
| Depends on | U04 Meta, U61 Event (data contracts for events), U72 Analytics (lakehouse), U65 Security (classification), U66 Privacy (purposes), U07 Knowledge Graph (lineage graph), U68 Evidence, U13 Temporal (see TEMPORAL-BINDING-MATRIX) |
| Depended on by | U72, U85 CDP, U94 ML Platform, U98 ESG reports, U67 Compliance (records), all producers/consumers of data |
| Master references | §14.4 (data contracts, lineage, quality), §5.2 L2 Data Fabric, master chat "Universal Data Universe … first-class" (A-41) |

> Data Governance owns **data as a managed product**: the data catalog (every dataset/table/topic/stream/feature with owner, classification, purpose, quality, lineage), data contracts (schema + semantics + SLAs between producers and consumers, incl. event contracts), data products (curated, documented, versioned datasets with SLAs), data quality rules and scores, end-to-end lineage, master-data management workflows for shared reference/master entities across tenants' systems (golden records with U11/U18 as hubs), and governed data sharing (exports, partner sharing, clean rooms).

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| DATA-L1 | Every persistent dataset (table, topic, lake table, feature, export) is registered in the catalog with owner, classification and purpose before use. | Pipeline/storage provisioning requires catalog id; scanners flag unregistered datasets (gap). |
| DATA-L2 | Cross-team/cross-universe data consumption is via data contracts or data products with declared SLAs and breaking-change policy. | Consumer registration required; contract checks in CI. |
| DATA-L3 | Lineage is captured automatically (OpenLineage) for all pipelines; reports and ML features must have complete lineage to sources. | Pipeline SDK emits lineage; certification gate for reports/models. |
| DATA-L4 | Data leaving the tenant boundary (exports, sharing, clean rooms) requires purpose, legal basis, and approval; outputs are watermarked/logged. | Sharing workflow + U68 audit. |

## 2. Objects
`Dataset { id, kind: table|topic|lake-table|view|feature|file-set|export, location, schema ref, owner, steward, classification, purposes, retention: RetentionRuleRef, freshness SLO, qualityScore, tags }` · `DataContract` (master §14.4 + `consumers`, `version`, `compatibility`) · `DataProduct { id, datasets, interface (SQL view, API, file drop, Delta/Iceberg share), docs, SLAs, version, consumers, price? (internal/external marketplace) }` · `QualityRule { dataset, kind: completeness|validity|uniqueness|freshness|consistency|distribution-drift, expression, threshold, severity }` · `QualityResult { rule, run, value, pass }` · `LineageEdge { from (dataset/column), to, job, transformation }` · `MasterEntity { domain (customer, supplier, product, location), golden record ref, sources, match/merge rules, stewardship queue }` · `ShareAgreement { from tenant, to party, data product, purpose, legal basis (U89 contract), expiry: TimePoint, controls (clean room, aggregation thresholds) }`.

## 3. Commands, Queries, Events, APIs
Commands: `RegisterDataset`, `PublishDataContract`, `PublishDataProduct`, `DefineQualityRule`, `RunQualityChecks`, `ApproveShare`, `ResolveMasterRecord`.
Queries: `Catalog(search)`, `Lineage(dataset|column, direction, depth)`, `Impact(schemaChange)`, `QualityScore(dataset)`, `WhoUses(dataset)`.
Events: `data.quality.failed`, `data.contract.breaking-change-proposed`, `data.share.approved|revoked`.
```text
GET /v1/data/catalog?q=   GET /v1/data/lineage?dataset=&dir=   POST /v1/data/products   POST /v1/data/quality-rules
```

## 4. Gaps, AI, Ops, UI, Scale
```prolog
gap(unregistered_dataset, D) :- discovered_dataset(D), not catalog_entry(D).
gap(report_lineage_incomplete, R) :- certified_report(R), not lineage_to_sources(R).
gap(dataset_without_owner, D) :- catalog_entry(D), not owner(D, _).
gap(quality_failing, D) :- dataset(D), critical_rule_failing(D).
```
AI: auto-classification of columns (PII detection), documentation drafting, anomaly-based quality rules, natural-language catalog search. Views: data catalog (search, schema, lineage graph, quality, owners, consumers), contract editor with compatibility check, data product pages, stewardship queue (MDM), sharing approvals. Tools: OpenLineage/Marquez-compatible, Great-Expectations-style checks, Iceberg REST catalog. T2.

## Appendix
- **C.** 0.1.0.
