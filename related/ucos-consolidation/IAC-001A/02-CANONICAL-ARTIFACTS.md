# 02 — CANONICAL ARTIFACTS

> **Mission:** IAC-001A · **Mode:** READ-ONLY · **Baseline:** HEAD `836475c`
> Canonical Authority = the authored source of truth that implementation must conform to. **Test:** git-tracked, un-ignored, and the originating (not derived) source.

---

## 1. Constitutions — `00-CEP/` (Canonical)

| ID | Artifact | Canonical Owner | Impl. Authority |
|---|---|---|---|
| CEP-000 | Constitutional Engineering Charter | 00-CEP | Yes |
| CEP-001 | Engineering Constitution | 00-CEP | Yes |
| CEP-002 | Governance Constitution | 00-CEP | Yes |
| CEP-003 | Execution Constitution | 00-CEP | Yes |
| CEP-004 | Validation Constitution | 00-CEP | Yes |
| CEP-005 | Certification Constitution | 00-CEP | Yes |
| CEP-006 | Ratification Constitution (finality authority) | 00-CEP | Yes |
| CEP-007 | Freeze Constitution | 00-CEP | Yes |
| CEP-008 | Evidence & Traceability Constitution | 00-CEP | Yes |
| CEP-009 | Amendment/Evolution Constitution | 00-CEP | Yes |
| CEP-010 | Audit/Compliance/Assurance Constitution | 00-CEP | Yes |

All 11 tracked and un-ignored. **Source of truth = themselves** (authored constitutions). These are the apex canonical authority.

## 2. Universes & USIS — canonical homes (Canonical)

| Location | Artifact | Role |
|---|---|---|
| `15-UNIVERSAL-SCIENCE-INTELLIGENCE/00-CONSTITUTION/USIS-001-…` | USIS Constitution | Canonical home |
| `15-…/06-UNIVERSES/USIS-002-UNIVERSE-CATALOG.md` | Universe catalog | Canonical home |
| `15-…/07-SCIENCES/USIS-003-UNIVERSAL-SCIENCE-CATALOG.md` | Science catalog | Canonical home |
| `15-…/05-META-MODEL/USIS-004-UNIVERSAL-CAPABILITY-META-MODEL.md` | Capability meta-model | Canonical home |
| `15-…/USIS-GOV-000-…-PROGRAM-ESTABLISHMENT-DETERMINATION.md` | USIS governance program | Canonical home |
| `00-MASTER/UCOS-USIS-001/00..07-*` | USIS program authoring lane | Canonical (program) |

USIS is registered (Wave-0, PROVISIONAL tier) and homed under `15-…`. Both the homed constitution and the `00-MASTER/UCOS-USIS-001` authoring lane are tracked/canonical.

## 3. Catalogs — `03-CATALOGS/` (Canonical)

Seven `UCOS-Ω∞-UNIVERSAL-CANONICAL-*-CATALOG` documents (API, APPLICATION, DATA, EVENT, RUNTIME-CATALOG-CONSTITUTION, SERVICE, WORKFLOW). All tracked/un-ignored. **Source of truth = themselves.**

## 4. Reference architecture constitutions — `04-REFERENCE/` (Canonical subset)

Seven `UCOS-Ω∞-UNIVERSAL-REFERENCE-*-ARCHITECTURE(.md)` constitutions (ARCHITECTURE-CONSTITUTION, API, APPLICATION, DATA, EVENT, SERVICE, WORKFLOW). Tracked. These are the authored REF family (per RTR-001/05, "committed, registered … none is lost"). *(The `.docx` sources in the same directory are Reference Evidence — see `05`.)*

## 5. Schemas — `00-BOOK/SCHEMAS/*.schema.json` (Canonical)

Authored JSON schemas (artifact, build, connector, control-tower, deployment, environment, export-job, finding, flow, journey, …). Tracked/un-ignored; they are authored contracts, not generated output.

## 6. Engines & engineering code — `engine/**/*.py` (Canonical)

372 tracked Python files across `engine/` (acceptance, certification, knowledge, …) plus the authored program engines that generate the non-artifacts:

- `00-MASTER/UAKOS-CLOSURE-002/closure_engine.py`, `phase2_engine.py`, `phase3_engine.py` — the **authored source of truth** for the gitignored `closure.json`/`phase*.json`/numbered reports.
- `engine/knowledge/seed.py` — the authored source of truth for the gitignored `/knowledge/` store.

These carry implementation authority as **code**; their outputs do not (see `04`/`05`).

## 7. Constitutional/program authored determinations — `00-MASTER/**` (Canonical, program-authored)

Authored program artifacts admitted by EAC-001 (F1–F9): root determinations, `00-MASTER` program registers, and authored engines. Examples: `UCOS-CRAT-001/05-FOUNDATION-SEAL.md`, `UCOS-USIS-001/*`, `RA-003/03-KNOWLEDGE-ONCE-CERTIFICATION.md`.

## 8. Canonical completeness check (no missing canonical artifact)

| Canonical set | Expected | Present |
|---|---|---|
| CEP constitutions | CEP-000..010 | 11/11 ✓ |
| Canonical catalogs | 7 | 7/7 ✓ |
| Reference architecture constitutions | 7 | 7/7 ✓ |
| USIS canonical home | USIS-001/002/003/004 + GOV-000 | present ✓ |
| Foundation binding stack (S2-01..S2-11) | present (per `07-ARCHITECTURE-FREEZE-EVIDENCE.md`) | ✓ |

**No missing canonical artifact identified.** (The absent CLOSURE-002 registers 39/43 are **generated** family members, not canonical — see `04`/`07`.)

---
*End of 02-CANONICAL-ARTIFACTS.md*
