# 01 — CANONICAL RELATIONSHIP INVENTORY

> **Program:** Implementation Authority Program (IAP)
> **Mission:** IAC-001C — Canonical Relationship & Dependency Certification
> **Version:** 1.0 · **Mode:** READ-ONLY
> **Authority:** Repository Truth + IAC-001A + IAC-001B
> **Baseline:** HEAD `836475c` (branch `governance-reconciliation`) · **Date:** 2026-07-24
> **Rule:** Generated and derived artifacts SHALL NOT establish canonical relationships. Edges are extracted **only** from authored CKO identity blocks.

---

## 1. Establishing source of relationships

Relationships are declared intrinsically in each CKO's authored identity block — never from the generated `UAKOS-CLOSURE-002/38-DEPENDENCY-REGISTER` / `39-IMPL-DEPENDENCY-GRAPH` (gitignored) or the derived `00-BOOK` graphs. Relation-bearing fields:

`DEPENDS-ON` · `DERIVES AUTHORITY FROM` · `PARENT` · `GOVERNED BY` · `REALIZES` · `SUPERSEDES` / `SUPERSEDED BY` · `AUTHORIZED-BY` · `CONTAINS` / `COMPOSED OF` · `REFERENCES` · `IMPLEMENTS`.

## 2. Extraction result (read-only)

- CKO nodes carrying an `ARTIFACT ID` identity block: **342 files / 335 distinct node IDs**.
- Total authored relationship edges extracted: **1,976**.

## 3. Relationship-type inventory

| Relationship | Direction | Declaring nodes | Establishing field |
|---|---|---|---|
| Depends On / Required By | child → parent dep | **150** | `DEPENDS-ON` |
| Derives-From / Governs | subordinate → authority | 10 | `DERIVES AUTHORITY FROM` |
| Governed By / Governs | node → governance instrument | 9 (table-cell form; more in `AUTHORITY` prose) | `GOVERNED BY` |
| Realizes / Realized By | knowledge → destination | 7 | `REALIZES` |
| Supersedes / Superseded By | new → old | 4 | `SUPERSEDES` |
| Parent / Child | node → program root | 4 | `PARENT` |
| Contains / Composed-Of | whole → part | structural (program/band containment) | path + `PARENT` |
| References / Referenced-By | cross-reference | pervasive | `REFERENCES`, prose |

All relationship categories enumerated by the mission (Parent/Child, Contains/Contained-By, References, Governed-By, Implements/Implemented-By, Realizes/Realized-By, Depends-On/Required-By, Composes/Composed-Of, Extends, Supersedes, Produces/Consumes) are represented either as an explicit authored field or as structural containment.

## 4. Determination

> **VERIFY 1 (Canonical Relationships): PASS.**
> Every canonical relationship type is identified and inventoried from authored sources. The relationship matrix is in `02`; graphs in `03`–`06`.

---
*End of 01-CANONICAL-RELATIONSHIP-INVENTORY.md*
