# 02 — IMPLEMENTATION DESTINATIONS

> **Mission:** IAC-001E · **Mode:** READ-ONLY · **Baseline:** HEAD `836475c`
> Every canonical capability must have: Implementation owner · Implementation location · Realization location · Runtime destination.

---

## 1. Destination matrix (per capability class)

| Capability | Implementation owner | Implementation location | Realization location | Runtime destination |
|---|---|---|---|---|
| Foundation | `engine/foundation` (CEP-001) | `engine/foundation` | `06-IMPLEMENTATION` | `08-RUNTIME` |
| Runtime / Execution / Orchestration | `08-RUNTIME` RL-F2 | `engine/runtime` | `08-RUNTIME` | `08-RUNTIME` kernel |
| Platform | `09-PLATFORM` (PLATFORM-GOV-000) | `platform/**` | `09-PLATFORM` | platform runtime |
| Data | `10-DATA` (DATA-GOV-000) | `data/**` | `10-DATA` | data runtime |
| Service | `11-SERVICE` (SERVICE-GOV-000) | `service/**` | `11-SERVICE` | service runtime |
| Application | `12-APPLICATION` (APPLICATION-GOV-000) | `application/**` | `12-APPLICATION` | app runtime |
| Infrastructure | `13-INFRASTRUCTURE` (INFRASTRUCTURE-GOV-000) | `infrastructure/**` | `13-INFRASTRUCTURE` | infra/deployment |
| Security | `14-SECURITY` (SECURITY-GOV-000) | (security architecture) | `14-SECURITY` | cross-cutting runtime |
| Intelligence / Science | `15-USIS` (USIS-GOV-000) | `intelligence/**` | `15-…` | intelligence runtime |
| Validation | `engine/validation` (CEP-004) | `engine/validation` | validation lane | gate at runtime |
| Certification | `engine/certification`+`universal_certification` (CEP-005) | those packages | `platform/certification` | certification gate |
| Knowledge | `engine/knowledge` (CEP-008) | `engine/knowledge` | knowledge store | runtime knowledge |
| Registry | `engine/registry` (REG-AUTO-001) | `engine/registry` | registration | runtime registry |

## 2. Completeness

Every canonical capability (IAC-001D `01`) resolves to all four destination coordinates — owner, implementation location, realization location, runtime destination. The band structure (`08-…15-`) + code trees (`engine/`,`platform/`,`service/`,`application/`,`infrastructure/`,`data/`,`intelligence/`) provide concrete homes; the `03-CATALOGS` catalogs define the API/APP/DATA/EVENT/RUNTIME/SERVICE/WORKFLOW surfaces.

## 3. Determination

> **VERIFY 2 (Implementation Destinations): PASS.**
> Every canonical capability has an implementation owner, implementation location, realization location, and runtime destination.

---
*End of 02-IMPLEMENTATION-DESTINATIONS.md*
