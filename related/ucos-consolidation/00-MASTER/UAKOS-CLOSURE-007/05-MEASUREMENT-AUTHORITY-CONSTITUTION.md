# 05 — Measurement Authority Constitution

> PROGRAM **UAKOS-CLOSURE-007** · PHASE-001 · BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED TRUTH)** · READ-ONLY.
> Defines (documents, does not implement) the constitutional Measurement Authority for UCOS Ω∞. This is a proposed constitutional charter; it creates no canonical concept and modifies no artifact.

## 1. Mandate

The **Measurement Authority (MA)** is the sole constitutional authority that defines *what it means to have measured all architectural knowledge*. No claim of Repository Closure, Architectural Completeness, or Universal Knowledge Assimilation is valid unless it is produced under an MA-governed census.

## 2. Constitutional definitions the MA owns

| Term | MA definition |
|---|---|
| **Authoritative discovery** | The complete, versioned set of discovery mechanisms + their inputs. Today: `closure_engine.py` (sole discoverer). |
| **Authoritative measurement** | A determination produced by a discovery run whose **scan mode and inputs are pinned and recorded**. |
| **Authoritative census** | An enumeration of every architectural namespace with format, authority, registry, owner, location, machine representation, and status. |
| **Authoritative scope** | The declared universe of sources (repo roots, `00-SOURCE`, corpus, stores) and file types in scope for a run. |
| **Authoritative exclusions** | Every exclusion — regex, namespace, directory, extension, size cap, sentinel, corpus-skip — declared **explicitly and by intent**, never implicit. |
| **Authoritative evidence** | The physical artifacts (files, line numbers, `closure.json`) that back a determination. |
| **Measurement reproducibility** | Any party re-running the pinned run obtains byte-identical results. |
| **Measurement determinism** | One input state ⇒ exactly one determination; no mode-dependent divergence. |

## 3. Constitutional requirements the MA SHALL enforce (currently UNMET — see evidence)

| # | Requirement | Current state | Evidence |
|---|---|:---:|---|
| MA-1 | Discovery families are **registry-driven**, not hard-coded | UNMET (closed regex list) | `FAMILIES` |
| MA-2 | Every namespace present in repo/corpus is **either discoverable or explicitly reserved/excluded with rationale** | UNMET (50+ silent) | report 02 |
| MA-3 | Scan mode + schema version stamped into every `closure.json` | UNMET (no `scan_mode` field) | `PHASE-INTERFACE-CONTRACT.md §5` |
| MA-4 | Canonical measurement uses **one** deterministic mode | UNMET (repo-only vs full-corpus) | CLOSURE-006 CF-02 |
| MA-5 | Non-text sources (PDF/diagram/zip) have a declared disposition | UNMET (silently excluded) | `TEXT_EXT` |
| MA-6 | Prose-only (ID-less) concepts have a declared measurement path | UNMET (requires ID) | report 04 |
| MA-7 | Every exclusion is enumerated in a Measurement Assumption Register | UNMET until now | report 09 |

## 4. MA governance interfaces (proposed, not built)

- **Namespace Registry** (would satisfy MA-1/MA-2): a governed list of every namespace → {format, authority, owner, status ∈ Implemented/Specified/Reserved/Historical/Deprecated/Experimental/Unknown}. The discovery engine would read families from this registry.
- **Measurement Manifest** (MA-3/MA-4): pinned `{scan_mode, schema_version, source_roots, extensions, size_cap, exclusions[]}` recorded in `closure.json`.
- **Assumption Register** (MA-7): report 09 of this program is the first materialization.

## 5. Authority relationship

The MA is **subordinate to Repository Truth** (it measures; it does not create knowledge) and **superior to any closure/completeness claim** (no closure may be certified except through an MA census). It does not override the enrichment authority (-003), validation/cert authority (-004), or ingestion gate (-005); it governs the **measurement basis** all of them rely upon.

## 6. Determination

**MEASUREMENT AUTHORITY: DEFINED (documentary), NOT YET SATISFIED.** The constitution above is establishable, but 7/7 of its core requirements are currently UNMET by the existing discovery apparatus. Establishing the MA is necessary before any future completeness claim can be constitutionally valid. Evidence: `closure_engine.py`, `PHASE-INTERFACE-CONTRACT.md §5`, reports 02–04, 08, 09.

*END — 05 · AUTHORITY = NONE (DERIVED TRUTH) · READ-ONLY.*
