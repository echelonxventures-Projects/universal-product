# 01 — Universal Architectural Census

> PROGRAM **UAKOS-CLOSURE-007** · PHASE-001 · UNIVERSAL ARCHITECTURAL CENSUS · MEASUREMENT AUTHORITY
> BASELINE `b67a720` (branch `governance-reconciliation`) · AUTHORITY = **NONE (DERIVED TRUTH)**
> MODE = READ-ONLY · EVIDENCE-ONLY · FAIL-CLOSED. No enrichment, no migration, no reassignment, no fixes.

---

## 0. Purpose

Not to count concepts — to determine whether the **counting process itself is complete**. This census asks: *can the Repository prove that every architectural namespace is enumerated and every architectural concept is discoverable?*

Predecessor `UAKOS-CLOSURE-006` found Architectural Completeness = FAIL because *"discovery itself cannot prove that all architectural namespaces have been enumerated."* This program tests that discovery system directly.

## 1. The discovery universe (what the system can measure)

The complete measurement apparatus is three engines + the UKB/registry stores:

| Mechanism | Role | Discovery power |
|---|---|---|
| `closure_engine.py` | Phase-001 extraction | the **only** discoverer; 26 curated ID families over git-tracked+corpus text |
| `phase2_engine.py` | reconciliation | none (reuses `closure.json`) |
| `phase3_engine.py` | planning | none (reuses `closure.json`) |
| UKB / `00-BOOK/DATA/*` / `knowledge/*` | canonical stores | record homed knowledge; not discoverers |

**Discovery power of the whole system = discovery power of `closure_engine.py`.** (reports 03, 04)

## 2. The measured universe vs the actual universe

| Layer | Count | Evidence |
|---|---:|---|
| Discoverable identifier families | **26** (+1 cert token) | `FAMILIES` (report 03) |
| Namespace families observed in governed repo (filename census) | **60+** | report 02 §1 |
| Namespace families observed in external corpus (filename census) | **50+** | report 02 §2 |
| Namespace families **outside** the discoverable set | **majority** | reports 02, 08 |

The actual namespace universe is several times larger than the discoverable set — including namespaces **inside the governed repo** (e.g. `UCOS-MISC`, `UMB`, `UKB-ADV`, `UCOS-ADV`, `UCOS-REG`, `UCOS-RIE-*`).

## 3. Census answer to each mandated question (per namespace) — summary

For each namespace the census attempts: identifier format · generation authority · registry · lifecycle · canonical owner · repository location · machine representation · dependencies · status.

**Result:** these can be answered **only for the 26 discoverable families** (they have documented formats and a machine representation in `closure.json`). For the 50+ non-discoverable families, **generation authority, registry, and machine representation are UNKNOWN** — there is no governed mechanism that mints, registers, or measures them. That "UNKNOWN" is the census gap (report 11).

## 4. Can architectural knowledge exist without ever being counted?

**YES — proven, not estimated.** A document is uncounted if any of the following hold (each an actual, evidenced condition):
1. Its IDs use a namespace not in `FAMILIES` (e.g. `WP-R`, `PCAMG-RUNTIME`, `AD`, `MEM`, `ONTO`, `RPF`, `NVF`, `UMB`, `UCOS-RIE`). → reports 02, 03, 08.
2. It is not git-tracked (and not one of the two explicit `knowledge/*.json` files). → report 04.
3. It is a PDF, image/diagram, zip, or spreadsheet. → `TEXT_EXT` (report 04).
4. Its architectural content is **prose without any ID token**. → homing requires an ID.
5. It lives only in the corpus while `CLOSURE_SKIP_CORPUS=1`. → report 13.
6. Its ID sits beyond the 4 MB read cap of a large file. → `_read_text` limit.

Because at least conditions 1–5 are demonstrably satisfied by real material, uncounted architectural knowledge **provably exists**.

## 5. Determination

**UNIVERSAL CENSUS READINESS: FAIL.** The measurement universe (26 families, ID-anchored, git-tracked, text-only, corpus-optional) is strictly smaller than the actual architectural universe. The Repository cannot presently prove that all architectural knowledge is discoverable. See report 15 for the sealed determination and report 05 for the Measurement Authority that must govern this going forward.

*END — 01 · AUTHORITY = NONE (DERIVED TRUTH) · READ-ONLY.*
