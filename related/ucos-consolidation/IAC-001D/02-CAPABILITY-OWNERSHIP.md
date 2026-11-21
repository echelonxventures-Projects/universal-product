# 02 — CAPABILITY OWNERSHIP

> **Mission:** IAC-001D · **Mode:** READ-ONLY · **Baseline:** HEAD `836475c`
> Every capability: exactly one canonical owner; no duplicate ownership; no ambiguous ownership.

---

## 1. Ownership rule

Capability ownership follows the same canonical-homing law as knowledge (IAC-001B): `UNIVERSAL-LAW-CANONICAL-HOMING` + `GOV-001-T3` (No-Orphan) + `REG-AUTO-001`. Each capability has one program/engine owner and one canonical home.

## 2. Single-owner confirmation

| Capability | Single canonical owner | Ambiguity? |
|---|---|---|
| Foundation | `engine/foundation` (CEP-001) | none |
| Runtime / Execution / Orchestration | `08-RUNTIME` Runtime Program (RL-F2) · `engine/runtime` | none |
| Platform | `09-PLATFORM` (PLATFORM-GOV-000) | none |
| Data | `10-DATA` (DATA-GOV-000) | none |
| Service | `11-SERVICE` (SERVICE-GOV-000) | none |
| Application | `12-APPLICATION` (APPLICATION-GOV-000) | none |
| Infrastructure | `13-INFRASTRUCTURE` (INFRASTRUCTURE-GOV-000) | none |
| Security | `14-SECURITY` (SECURITY-GOV-000) | none |
| Science / Intelligence | `15-USIS` (USIS-GOV-000) | none |
| Validation | `engine/validation` (CEP-004) | none |
| Certification | `engine/certification` (EC-1) + `engine/universal_certification` (Terminal T6) | **layered, not duplicate** — distinct scopes (see `06`) |
| Governance | `engine/governance` + `02-MASTER/UCOS-GOV-*` (CEP-002) | none |
| Knowledge | `engine/knowledge` (CEP-008) | none |
| Registry | `engine/registry` + `REG-AUTO-001` | none |
| Determinism | `engine/determinism` (CEP-008) | none |

## 3. Duplicate / ambiguous ownership

- **No duplicate ownership.** Each capability resolves to one program/engine owner. The only two-package capability (Certification) is a governed **layering** (EC-1 per-artifact vs Universal terminal-T6 record-only), not two owners of the same capability.
- **No ambiguous ownership.** Every band capability has exactly one `*-GOV-000` program-establishment determination as owner; every engine capability is one subpackage.

## 4. Determination

> **VERIFY 2 (Capability Ownership): PASS.**
> Every capability has exactly one canonical owner; no duplicate ownership; no ambiguous ownership.

---
*End of 02-CAPABILITY-OWNERSHIP.md*
