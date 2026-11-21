# 03 — CANONICAL OWNERSHIP

> **Mission:** IAC-001B · **Mode:** READ-ONLY · **Baseline:** HEAD `836475c`
> Every CKO must have: an Owner, a Repository Home, and a Canonical Source.

---

## 1. Ownership convention (self-declared per artifact)

Each CKO declares ownership intrinsically — no external (derived) registry required:

| Property | Declared by | Example |
|---|---|---|
| **Owner** | `UCOS-PROGRAM` / `UCOS-FAMILY` | USIS-001 → `UCOS-PROGRAM: USIS`, `UCOS-FAMILY: UNIVERSAL-SCIENCE-INTELLIGENCE` |
| **Repository Home** | Tracked path + `CANONICAL FORM` | USIS-001 → `15-UNIVERSAL-SCIENCE-INTELLIGENCE/00-CONSTITUTION/…`; CEP-005 → `00-CEP/…`, `CANONICAL FORM: This Markdown file` |
| **Canonical Source** | The artifact itself (authored, tracked, un-ignored) | CEP-005 `CANONICAL FORM: This Markdown file` |

## 2. Owner coverage by family

| Family / Program | Owner (program) | Home |
|---|---|---|
| CEP-000..010 | Constitutional Engineering Program (CEP) | `00-CEP/` |
| UCOS-GOV-001..006 | Repository Governance | `02-MASTER/` |
| UCOS-COMP-000000 (CIOA), 000001 (CCE) | Constitutional Orchestration / Completeness | `02-MASTER/` |
| 7 canonical catalogs | Catalog constitution | `03-CATALOGS/` |
| 7 reference architectures | Reference architecture | `04-REFERENCE/` |
| RUNTIME/PLATFORM/DATA/SERVICE/APPLICATION/INFRASTRUCTURE/SECURITY-NNN | respective band program | `08-…`/`09-…`/`10-…`/`11-…`/`12-…`/`13-…`/`14-…` |
| USIS-001..004, USIS-GOV-000 | USIS program | `15-…/` (canonical) · `00-MASTER/UCOS-USIS-001/` (blueprint) |
| engine packages | engineering | `engine/**` |

## 3. Single-owner / single-home confirmation

- Each canonical `.md` occupies exactly one tracked path → single home (structural).
- Each declares exactly one `UCOS-PROGRAM`/`UCOS-FAMILY` → single owner.
- The only multi-home ID family (USIS) has an **explicitly designated canonical home** (`15-…`, "registered corpus instantiation") with the second file declared a provenance blueprint — single canonical ownership preserved (see `02` §2).
- Program-internal / derived docs without an identity block (375) are owned by their enclosing program (declared in-doc, e.g. `PROGRAM UAKOS-CLOSURE-006`) and homed at their path → owned, not ownerless.

## 4. Determination

> **VERIFY 3 (Canonical Ownership): PASS.**
> Every CKO has a declared Owner, a single Repository Home, and a Canonical Source, established from the artifacts themselves under `UNIVERSAL-LAW-CANONICAL-HOMING` + `REG-AUTO-001`.

---
*End of 03-CANONICAL-OWNERSHIP.md*
