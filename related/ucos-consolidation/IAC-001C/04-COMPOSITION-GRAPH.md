# 04 — COMPOSITION GRAPH

> **Mission:** IAC-001C · **Mode:** READ-ONLY · **Baseline:** HEAD `836475c`
> Whole→part composition, established from authored `PARENT`/containment + program/band structure.

---

## 1. Composition mechanism

Composition (Contains / Composed-Of) is established canonically by (a) `PARENT` declarations and (b) program/band structural containment (each CKO's home lane is its compositional parent). No generated/derived graph is used.

## 2. Composition layers

| Composition | Whole | Parts (composed of) | Evidence |
|---|---|---|---|
| **Foundation composition** | FOUNDATION family / `USIS-GOV-000` program root | foundation CKOs (METACLASS/FOUNDATION/UCKO families), CEP binding stack S2-01..S2-11 | `PARENT` → program root; `07-ARCHITECTURE-FREEZE-EVIDENCE` foundation-realization table |
| **Universe composition** | `USIS-002 Universe Catalog` | universes U16/U24/U25/U26/U28 (declared in USIS-001 `REALIZES`) | `15-…/06-UNIVERSES` |
| **Capability composition** | `USIS-004 Capability Meta-Model` | capability entries; AEOS-001 discovery/admission | `15-…/05-META-MODEL`, `02-MASTER/AEOS-001` |
| **Platform composition** | `09-PLATFORM` program | PLATFORM-NNN architectures + `platform/**` code | band containment |
| **Blueprint composition** | `EC2-EPIC-006 Blueprint Catalog Constitution` | blueprint entries | `02-MASTER/EC2-EPIC-006-BLUEPRINT-CATALOG-CONSTITUTION` |

## 3. Consistency

Composition is a strict tree over program/band containment (each CKO has exactly one home lane → one compositional parent). No CKO is contained by two disjoint wholes. Composition is consistent with the dependency DAG (`03`) — no composition edge introduces a cycle.

## 4. Determination

> **VERIFY 3 (Composition Graph): PASS.**
> Foundation, Universe, Capability, Platform, and Blueprint composition are established and consistent; no compositional cycle or dual-containment.

---
*End of 04-COMPOSITION-GRAPH.md*
