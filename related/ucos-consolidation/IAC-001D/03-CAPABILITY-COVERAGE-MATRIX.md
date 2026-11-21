# 03 — CAPABILITY COVERAGE MATRIX

> **Mission:** IAC-001D · **Mode:** READ-ONLY · **Baseline:** HEAD `836475c`
> Responsibility → Owning Capability → Owning Constitution → Owning Registry → Owning Implementation.

---

## 1. Constitutional-responsibility coverage matrix

| Constitutional responsibility | Owning capability | Owning constitution | Owning registry | Owning implementation |
|---|---|---|---|---|
| Engineering | Foundation/Core engines | CEP-001 | UNIVERSAL-ARTIFACT-REGISTRY | `engine/foundation`,`compiler`,`factory` |
| Governance | Governance capability | CEP-002 · UCOS-GOV-001..006 | ARCH-GOV-001 | `engine/governance`, `platform` |
| Execution | Runtime/Execution capability | CEP-003 · `08-RUNTIME` | control-tower | `engine/runtime` |
| Validation | Validation capability | CEP-004 | validation ledger | `engine/validation` |
| Certification | Certification capability (EC-1 + Universal) | CEP-005 | CERTIFICATION-REGISTRY | `engine/certification`,`engine/universal_certification`,`platform/certification` |
| Ratification | Acceptance/Ratification capability | CEP-006 | acceptance ledger | `engine/acceptance` |
| Freeze | Freeze capability | CEP-007 | `99-FREEZE` | `99-FREEZE` notices/hashes |
| Evidence & Traceability | Determinism/Evidence capability | CEP-008 | `data/_evidence` (registered) | `engine/determinism` |
| Amendment / Evolution | Amendment capability (definitional) | CEP-009 | VOLUME/lineage registry | governance process |
| Audit / Compliance / Assurance | Audit capability (definitional) | CEP-010 | audit records | governance process |
| Knowledge | Knowledge capability | CEP-008 · USIS U24 | KNOWLEDGE-GRAPH-REGISTRY | `engine/knowledge` |
| Science / Intelligence | Intelligence capability | `15-USIS` (USIS-001..004) | USIS registry | `intelligence/**` |
| Universe | Universe capability | USIS-002 | universe catalog | `15-…/06-UNIVERSES` |
| Capability (meta) | Capability Meta-Model | USIS-004 | capability registry | 24-tier spine |
| Registry | Registry capability | REG-AUTO-001 | registration authority | `engine/registry` |
| Data / Service / Application / Infrastructure / Security / Platform | Domain capabilities | band `*-GOV-000` | band registries | `data/`,`service/`,`application/`,`infrastructure/`,`platform/` |

## 2. Coverage result

Every constitutional responsibility resolves through the full five-link chain (**responsibility → capability → constitution → registry → implementation**). No responsibility terminates without an owning capability + constitution + implementation home. The registry link is present (canonical process `REG-AUTO-001` + registered projections; the projections themselves are derived per IAC-001A but the registration *authority/process* is canonical).

## 3. Determination

> **VERIFY 3 (Capability Coverage): PASS.**
> Every constitutional responsibility has a complete coverage chain to an owning capability, constitution, registry, and implementation home.

---
*End of 03-CAPABILITY-COVERAGE-MATRIX.md*
