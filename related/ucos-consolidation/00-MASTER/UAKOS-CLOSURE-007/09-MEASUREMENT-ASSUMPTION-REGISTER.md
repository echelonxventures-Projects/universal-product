# 09 — Measurement Assumption Register

> PROGRAM **UAKOS-CLOSURE-007** · PHASE-001 · BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED TRUTH)** · READ-ONLY.
> Every hidden assumption the measurement makes. Making these explicit is a prerequisite for the Measurement Authority (report 05, MA-7).

| ID | Assumption (implicit in code) | If false, then… | Evidence |
|---|---|---|---|
| MA-A01 | "Every architectural concept carries an ID from one of 26 families." | prose/other-namespace concepts are unmeasured | `FAMILIES` |
| MA-A02 | "An ID appearing under a truth-root = a canonical home." | mere mention counts as homing; weak-home risk | `_scan` (`top in TRUTH_ROOTS ⇒ homed`) |
| MA-A03 | "git-tracked ∪ two `knowledge/*.json` = the whole repository." | untracked generated truth invisible | `discover_sources()` |
| MA-A04 | "Architectural knowledge lives only in the listed text extensions." | PDF/diagram/zip knowledge invisible | `TEXT_EXT` |
| MA-A05 | "docx `word/document.xml` body = the document's knowledge." | non-body docx content invisible | `_read_text` |
| MA-A06 | "4 MB per file is enough." | tail of large files invisible | `limit` |
| MA-A07 | "`…-99/-999/-U99` are always examples." | real terminal IDs dropped | `_SENTINEL` |
| MA-A08 | "The corpus is optional to a valid measurement." | corpus-only knowledge silently zeroed | `CLOSURE_SKIP_CORPUS` |
| MA-A09 | "Whatever mode last wrote `closure.json` is 'the' measurement." | determination depends on run history | `PHASE-INTERFACE-CONTRACT.md §5` |
| MA-A10 | "Absence of a namespace = it does not exist." | reserved/future namespaces indistinguishable from missing | report 02 §3 |
| MA-A11 | "Homed set having no duplicates/orphans ⇒ nothing is wrong." | says nothing about unmeasured set | CLOSURE-006 reports 08/09 |

## Note

None of these assumptions is documented **inside** the engine as a declared limitation; they are inferred from behavior. This register is the first explicit enumeration.

## Determination

**MEASUREMENT ASSUMPTIONS: 11 UNDECLARED assumptions identified.** Until each is either eliminated or ratified by the Measurement Authority, measurement cannot be called complete or authoritative. Evidence: cited inline.

*END — 09 · AUTHORITY = NONE · READ-ONLY.*
