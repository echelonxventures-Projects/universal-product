# 03 — Identifier Family Catalog

> PROGRAM **UAKOS-CLOSURE-007** · PHASE-001 · BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED TRUTH)** · READ-ONLY.
> The complete set of identifier families the discovery engine is capable of recognizing, verbatim from `00-MASTER/UAKOS-CLOSURE-002/closure_engine.py`.

## 1. Discoverable concept families (26) + 1 evidence token

| # | Family | Regex | Format constraint |
|---|---|---|---|
| 1 | UCKO | `\bUCKO-[A-Z]+-\d{3,4}\b` | UCKO-XXX-000[0] |
| 2 | UKDA-DEC | `\bUKDA-DEC-\d{3,4}\b` | UKDA-DEC-000 |
| 3 | ARCH | `\bARCH-[A-Z0-9]+-\d{3}\b` | ARCH-XXX-000 (two segments) |
| 4 | MEP | `\bMEP-\d{2}\b` | MEP-00 |
| 5 | MCP | `\bMCP-\d{3}\b` | MCP-000 |
| 6 | MCS | `\bMCS-\d{3}\b` | MCS-000 |
| 7 | CEP | `\bCEP-\d{3}\b` | CEP-000 |
| 8 | DATA | `\bDATA-\d{3}\b` | DATA-000 |
| 9 | SERVICE | `\bSERVICE-\d{3}\b` | SERVICE-000 |
| 10 | APPLICATION | `\bAPPLICATION-\d{3}\b` | APPLICATION-000 |
| 11 | INFRASTRUCTURE | `\bINFRASTRUCTURE-\d{3}\b` | INFRASTRUCTURE-000 |
| 12 | PLATFORM | `\bPLATFORM-\d{3}\b` | PLATFORM-000 |
| 13 | RUNTIME | `\bRUNTIME-\d{3}\b` | RUNTIME-000 |
| 14 | UCOS-COMP | `\bUCOS-COMP-\d{6}\b` | UCOS-COMP-000000 (6 digits) |
| 15 | UCOS-GOV | `\bUCOS-GOV-\d{3}\b` | UCOS-GOV-000 |
| 16 | UCOS-EXEC | `\bUCOS-EXEC-\d{3}\b` | UCOS-EXEC-000 |
| 17 | UCOS-RAT | `\bUCOS-RAT-\d{3}\b` | UCOS-RAT-000 |
| 18 | UCOS-RECON | `\bUCOS-RECON-[A-Z0-9]+\b` | UCOS-RECON-* |
| 19 | EPIC | `\bEPIC-[A-Z]+-\d{3}\b` | EPIC-XXX-000 |
| 20 | GOV | `\bGOV-\d{3}\b` | GOV-000 |
| 21 | METACLASS | `\b(?:AMC\|AMR\|DMC\|DMR\|SMC\|SMR\|ICMP\|ICNW\|ISTO\|ICAP)-\d{2}\b` | fixed enum-00 |
| 22 | BAND-UNIT | `\bEC3-B\d{2}-[A-Z]?\d{2}\b` | EC3-B13-U03 |
| 23 | EC3-GATE | `\bEC-3-AP-\d\b` | EC-3-AP-5 |
| 24 | FOUNDATION | `\b(?:EL-1\|RL-F2\|PL-F2\|DF-2\|SF-2\|AF-3)\b` | fixed enum |
| 25 | LAW | `Ω∞-\d{3}\b` | Ω∞-000 |
| 26 | PHASE | `\bPhase-\d{3}\b` | Phase-000 (case-sensitive) |
| — | CERT (token) | `\bUCOS-CERT-[A-Za-z0-9-]{6,}\b` | evidence, **not** a concept |

## 2. Structural properties of the family set

- **Curated, closed set.** New namespaces are recognized only by editing this list (source-code change), not by any registry-driven mechanism.
- **Rigid numeric widths.** e.g. `UCOS-COMP` requires **exactly 6** digits; `MCS`/`CEP`/etc. require **exactly 3**. IDs like `MCS-1`, `PHASE-11.0`, `AD-0016` (4 digits, wrong prefix) fall outside.
- **Case-sensitive PHASE.** `Phase-\d{3}` does not match uppercase `PHASE-` filenames.
- **Sentinel exclusion.** `_SENTINEL = -U?9{2,3}$` deliberately drops `…-99`, `…-999`, `…-U99` as example IDs.
- **Two families are enumerations** (METACLASS, FOUNDATION) — additions require code edits.

## 3. Identifier families PRESENT in corpus/repo but ABSENT from the catalog

`WP-R-###`, `WP-PLT-##`, `PCAMG-RUNTIME-####`, `PI#`, `PI##`, `AD-####`, `UCOS-REALM-*`, `REAL-C-##`/`REAL-M-##`, `PROMPT##`, `AUTH-###`, `UCOS-IMP-####`, `UCOS-ARCH-####`, `UCOS-UC-####`, `UCOS-KB-####`, `RPF-####`, `NVF-####`, `ONTO-*`, `MEM-*`, `INT-AUTH-*`, `UMB-*`, `UKB-ADV-*`, `UCOS-ADV-*`, `UCOS-REG-*`, `UCOS-RIE-*`, `UCOS-MISC-*`, `AEOS-*`, `UCIC-###` (as concept), single-letter program IDs (`B##`, `F##`, `T##`, `M##`, `G##`).

## 4. Determination

**IDENTIFIER COMPLETENESS: FAIL.** The identifier catalog is a closed, hand-curated set of 26 formats with rigid widths and one deliberate case bug (`PHASE`). Dozens of identifier families that actually occur in the corpus and the governed repo are unrepresented in the catalog and therefore unrecognizable. Evidence: `closure_engine.py:FAMILIES` (verbatim above); census in report 02.

*END — 03 · AUTHORITY = NONE · READ-ONLY.*
