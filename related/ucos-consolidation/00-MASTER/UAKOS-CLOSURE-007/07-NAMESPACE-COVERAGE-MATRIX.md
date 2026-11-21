# 07 — Namespace Coverage Matrix

> PROGRAM **UAKOS-CLOSURE-007** · PHASE-001 · BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED TRUTH)** · READ-ONLY.
> Per-namespace: is it discoverable by the engine? `✓` yes · `◑` partial (format edge cases) · `✗` no.

## 1. Discoverable (✓ / ◑)

| Namespace | Cov. | Reason |
|---|:---:|---|
| DATA, SERVICE, APPLICATION, INFRASTRUCTURE, PLATFORM, RUNTIME | ✓ | tail-anchored `\bX-\d{3}\b` matches inside `UCOS-X-###` |
| CEP, MCP, MEP, MCS, GOV | ◑ | need exact 2–3 digit width; `MCS-1`, `MEP` variants miss |
| ARCH | ◑ | needs `ARCH-XXX-\d{3}`; `UCOS-ARCH-\d{4}` misses |
| UCKO, UKDA-DEC | ✓ | store + decision families |
| UCOS-COMP | ✓ | 6-digit component block |
| UCOS-GOV, UCOS-EXEC, UCOS-RAT, UCOS-RECON | ✓ | explicit UCOS-* families |
| EPIC | ◑ | `EPIC-XXX-\d{3}` |
| METACLASS, BAND-UNIT, EC3-GATE, FOUNDATION | ✓ | fixed enums / band formats |
| LAW (`Ω∞-###`) | ✓ | |
| PHASE (`Phase-\d{3}`) | ◑ | case-sensitive; `PHASE-11.0` misses |

## 2. NOT discoverable (✗) — present in corpus and/or repo

| Namespace | Where | Files (census) |
|---|---|---:|
| WP-R | corpus | 86 |
| PCAMG-RUNTIME | corpus | 56 |
| PI | corpus | 32 |
| UCOS-REALM | corpus | 26 |
| REAL-C / REAL-M | corpus | 21 |
| AUTH / AUTH-REST | corpus | 17 |
| AD | corpus | 10 |
| WP-PLT, WI | corpus | 17 |
| UCOS-UC, UCOS-KB, UCOS-IMP, UCOS-ARCH | corpus | 34 |
| RPF, NVF | corpus | 9 |
| ONTO-* | corpus | 11 |
| MEM-* | corpus | ~20 |
| INT-AUTH, INT-REM | corpus | 12 |
| single-letter programs (B/F/T/M/G/C) | corpus | ~18 |
| **UCOS-MISC** | **repo** | 46 |
| **UCOS-CON** | **repo** | 44 |
| **UCOS-UMB / UMB** | **repo** | 52 |
| **UKB-ADV / UCOS-ADV** | **repo** | 40 |
| **UCOS-REG** | **repo** | 19 |
| **UCOS-RIE-*** | **repo** | 8+ |
| **UCOS-GEN/CAT/REF/VSN/FRZ/ADR/SRC/EES** | **repo** | ~30 |
| STAGE, CKPT | repo | 68 (evidence artifacts) |

## 3. Key observation

The `✗` list includes **governed-repo namespaces**, not just corpus ones. The engine cannot enumerate parts of its own Repository Truth as concepts (they are homed by filename-in-truth-root heuristics but never recognized as ID concepts). This means discovery incompleteness is intrinsic, not merely a corpus problem.

## 4. Determination

**NAMESPACE COVERAGE: FAIL.** The discoverable namespace set is a minority of the observed namespace universe, and the non-discoverable set includes governed-repo namespaces. Evidence: census (reports 02, this doc), `FAMILIES`.

*END — 07 · AUTHORITY = NONE · READ-ONLY.*
