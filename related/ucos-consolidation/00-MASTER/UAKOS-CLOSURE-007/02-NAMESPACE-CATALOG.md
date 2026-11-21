# 02 — Namespace Catalog

> PROGRAM **UAKOS-CLOSURE-007** · PHASE-001 · BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED TRUTH)** · READ-ONLY.
> Namespaces enumerated from filename-prefix census of the governed repo (`git ls-files`) and the external corpus (`../UCOS`). Counts are filename-family tallies (evidence, not concept totals).

## 1. Governed-repo namespaces (observed)

| Namespace family | Files | Discoverable by engine? | Note |
|---|---:|:---:|---|
| UCOS-SERVICE / SERVICE | 149 / 18 | ✓ (tail `SERVICE-\d{3}`) | band |
| UCOS-DATA / DATA | 134 / 18 | ✓ (`DATA-\d{3}`) | band |
| UCOS-INFRASTRUCTURE / INFRASTRUCTURE | 132 / 18 | ✓ | band |
| UCOS-APPLICATION / APPLICATION | 121 / 18 | ✓ | band |
| UCOS (generic) | 104 | ◑ | only if matches a specific family |
| UCOS-PLT / PLATFORM | 49 / 18 | ✓ (`PLATFORM-\d{3}`) | band |
| EC3-B (band-unit) | 48 | ✓ (`EC3-B\d{2}-[A-Z]?\d{2}`) | band-unit |
| **UCOS-MISC** | 46 | **✗** | no family |
| **UCOS-CON** | 44 | **✗** | no family |
| STAGE | 36 | ✗ | no family |
| UCOS-CEP / CEP | 35 / 11 | ✓ (`CEP-\d{3}`) | |
| CKPT | 32 | ✗ (evidence artifact) | checkpoints |
| **UCOS-UMB / UMB** | 31 / 21 | **✗** | Universal Master Build — no family |
| UCOS-MASTER | 24 | ◑ | filename-home only |
| UCOS-IMP | 24 | ✗ | no family |
| UCOS-ARCH | 24 | ✗ | `ARCH-XXX-\d{3}` ≠ `UCOS-ARCH-\d{4}` |
| EC2-EPIC / EPIC | 21 / 7 | ◑ (`EPIC-[A-Z]+-\d{3}`) | |
| **UKB-ADV / UCOS-ADV** | 20 / 20 | **✗** | no family |
| UCOS-REG | 19 | ✗ | no family |
| UCOS-SVC / UCOS-DAT / UCOS-RUN / UCOS-ENG | 19/19/18/18 | ✗ (abbrev) | short-form variants |
| RUNTIME / RUNTIME-GOV | 14 / 3 | ✓ / ✗ | |
| UCOS-GOV | 12 | ✓ (`UCOS-GOV-\d{3}`) | |
| UCOS-INTELLIGENCE | 11 | ✗ | no family |
| MCP | 8 | ✓ (`MCP-\d{3}`) | |
| UCOS-EXEC | 8 | ✓ (`UCOS-EXEC-\d{3}`) | |
| UCOS-COMP | 6 | ✓ (`UCOS-COMP-\d{6}`) | |
| **UCOS-RIE-*** (8 distinct) | 8 | **✗** | Repository Intelligence Engine — no family |
| **UCOS-GEN / CAT / REF / VSN / FRZ / ADR / SRC / EES / BOOK / APP** | ~30 | **✗** | governed but undiscoverable |
| **ZG-P** | 1 | **✗** | no family |

## 2. External-corpus namespaces (observed, top families)

| Namespace family | Files | Discoverable? |
|---|---:|:---:|
| **WP-R** | 86 | **✗** |
| **PCAMG-RUNTIME** | 56 | **✗** |
| PHASE | 45 | ◑ (`Phase-\d{3}` content only; `PHASE-11.0` filenames ✗) |
| UCOS (generic) | 37 | ◑ |
| **PI** | 32 | **✗** |
| **UCOS-REALM** | 26 | **✗** |
| MCS | 23 | ◑ (`MCS-\d{3}`; corpus `MCS-1` ✗) |
| **REAL-C / REAL-M** | 21 | **✗** |
| **PROMPT** | 14 | **✗** |
| **AUTH / AUTH-REST** | 17 | **✗** |
| UCOS-IMP | 12 | ✗ |
| UCOS-ARCH | 11 | ✗ |
| **AD** | 10 | **✗** |
| **WP-PLT** | 9 | **✗** |
| **WI** | 8 | **✗** |
| UCOS-UC / UCOS-KB | 14 | ✗ |
| **RPF / NVF** | 9 | **✗** |
| **ONTO-*** | 11 | **✗** |
| **MEM-*** | ~20 | **✗** |
| **INT-AUTH / INT-REM** | 12 | **✗** |
| UCOS-RECON | 2 | ✓ (`UCOS-RECON-[A-Z0-9]+`) |
| single-letter programs (B,F,T,M,G,C) | ~18 | ✗ |

## 3. Mission-listed candidate namespaces — presence check (repo)

| Candidate | Present in repo? | Evidence |
|---|:---:|---|
| UNI, DATA, SERVICE, APPLICATION, INFRASTRUCTURE, PLATFORM, RUNTIME, CEP, MCP, GOV, ARCH, COMP | YES | filename census §1 |
| UCOS, UAKOS, UCIC | YES | `UCIC-001-…`, `UAKOS-CLOSURE-*` |
| UKB | YES (21) | `UKB-ADV-*` |
| UKDA | store only (git-ignored) | `knowledge/canonical-knowledge.json` |
| POL | YES (7, prose) | policy files |
| **CTRL, RULE, TIME, SPACE, EXISTENCE, REALITY** | **NO (0 filename hits)** | census probe returned 0 |
| **AEOS** | 1 (incidental) | not a governed ID family |
| SYN, GRP, MED, EDU, SOC, COM | corpus/catalog only | rehomed as `UNI-*`; no governed ID family |
| ENG, INT, TRACE | prefix-collision only | no distinct governed ID family confirmed |

## 4. Determination

**NAMESPACE COMPLETENESS: FAIL.** The repository contains **many more namespaces than the discovery engine can enumerate**, including namespaces *inside the governed repo itself* (UCOS-MISC, UMB, UKB-ADV, UCOS-ADV, UCOS-REG, UCOS-RIE-*, EC2-EPIC variants). Several mission-listed namespaces (CTRL, RULE, TIME, SPACE, EXISTENCE, REALITY) are **absent entirely** — their absence cannot be distinguished from "never introduced" vs "not yet named," which is itself a census gap. Evidence: filename census (this doc), `closure_engine.py:FAMILIES` (report 03/04).

*END — 02 · AUTHORITY = NONE · READ-ONLY.*
