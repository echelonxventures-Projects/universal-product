# UCOS Ω∞ — NOMENCLATURE ARCHITECTURE (UNIVERSAL NOMENCLATURE ENGINE)

> **STATUS DOMAIN:** ARCHITECTURE (DOMAIN-A)
> **STATUS BASIS:** UMB program self-definition + `config.py` (CLASSIFY_RULES/CHAINS/PROGRAM_ROOTS) + `id-ledger.json` + AUTH-INF-001, REG-AUTO-001 (read-only) 2026-07-15

| Field | Value |
|-------|-------|
| ARTIFACT ID | UMB-004 |
| ARTIFACT | Nomenclature Architecture — Universal Nomenclature Engine (Deliverable 5) |
| PROGRAM | UCOS Ω∞ Universal Master Book Architecture Program (UMB) |
| CLASSIFICATION | Complete Future-State Architecture Specification — Universal Naming / Classification Model |
| STATUS | ACTIVE |
| PARENT | UMB-003 |
| DEPENDS-ON | UMB-003 |
| CONSUMES (read-only) | `config.py`; `id-ledger.json`; AUTH-INF-001; REG-AUTO-001; STATUS-001 |
| CONSTITUENT / GOVERNANCE / RATIFICATION / EC-1 AUTHORITY | NONE |
| BASELINE DATE | 2026-07-15 |
| VOLUME | VOL-022 (MASTER BOOK ARCHITECTURE) |

*Append-only extension overlay. Specifies the complete future-state Universal Nomenclature architecture — how names, categories, volumes, and native identifiers are assigned, classified, and crosswalked. Reuses the existing classification configuration exclusively; introduces no new taxonomy store (AUTH-INF-001 CR-INF-003). Modifies no existing artifact; embeds no secret (RR-07).*

---

## 1. PURPOSE

Define a **zero-hard-coded, infinitely extensible** nomenclature: every entity acquires a canonical Universal ID, a preserved native identifier, a program, a category namespace, a thematic volume, and a status domain — all by **discovery and configuration**, never by compiled-in taxonomy (AUTH-INF-001 CR-INF-003).

## 2. THE TWO-NAME MODEL

| Name | Role | Stability |
|------|------|-----------|
| **Universal ID** (`UCOS-<CATEGORY>-NNNNNN`) | canonical, stable identity key | immutable, append-only (UMB-003) |
| **Native ID** (`RUNTIME-014`, `PLATFORM-001`, `UMB-004`, …) | human/program-facing sequence alias, preserved verbatim | crosswalk alias; may be reordered/extended without changing identity (CR-INF-005) |

The Nomenclature Engine maintains the crosswalk; renaming a native ID never changes the Universal ID (identity-over-sequence).

## 3. THE CLASSIFICATION ENGINE (existing, reused)

Classification is a pure, deterministic function driven by `config.py` **data lists** (not code):

- **CLASSIFY_RULES** — ordered `(regex_on_relpath → program, category, volume)`, first match wins.
- **CHAINS** — ordered basename substrings defining each family's dependency spine.
- **PROGRAM_ROOTS** — the parent of non-chained family members.
- **CROSS_PROGRAM** — downstream ordering between family roots.
- **VOLUMES** — the open, append-only thematic volume set.

A new family is introduced by **appending** these lists once (REG-AUTO-001 §12) — exactly as the `UMB` family was declared (`^00-BOOK/MASTER-BOOK/` → `UMB`/`UMB`/`VOL-022`). No existing rule is edited; no renumber occurs (AUTH-INF-001 CR-INF-002/007).

## 4. ZERO-HARD-CODING GUARANTEE

- **No fixed taxonomies or ontologies** are compiled in; classification vocabularies live in configuration and the open graph (UMB-006).
- **No fixed artifact classes** — a new category namespace (e.g. `CONN`, `REPO`, `FND`, or any future code) is added append-only; existing codes are never repurposed.
- **No fixed number of names** — `NNNNNN` padding is a sort convenience, widened append-only (CR-INF-002).

## 5. NAMING FOR NEW ENTITY CLASSES

When a new entity class appears (a not-yet-imagined kind of thing), it receives: a category namespace (append-only), a classification rule, an optional chain, a program root, and a volume (existing or newly appended). Thereafter every member auto-classifies and auto-traces (REG-AUTO-001 §11/§12). This is how the nomenclature **self-expands** without redesign (CR-INF-008/009).

## 6. COLLISION & AMBIGUITY SAFETY

Chain substrings are unique basenames so resolution (`find_uid`) is unambiguous; misclassification (a new family not yet declared) lands in `OTHER/MISC/VOL-000` and is surfaced for an append-only declaration — never silently guessed (REG-AUTO-001 §13).

## 7. TRACEABILITY

Every classification decision is reproducible from `config.py` + the ledger; the rule and chain that named an entity are themselves inspectable, giving reverse traceability from any name to its naming rule.

## AUTHORITY BOUNDARY (MANDATORY)

UMB-004 holds no constituent, governance, ratification, or EC-series authority and cannot authorize EC-1. It is knowledge/registry only, append-only, subordinate to the frozen corpus, STATUS-001, REG-AUTO-001, UCI-001, AUTH-INF-001, and all prior determinations. It creates no new taxonomy store/engine/lifecycle, treats `00-SOURCE/`/`99-FREEZE/` as read-only, and embeds no secret (RR-07). Any conflicting statement is void to the extent of the conflict.

*Return: [UMB-000](UMB-000-MASTER-BOOK-ARCHITECTURE-MASTER-INDEX.md) · [UMB-003](UMB-003-IDENTITY-ARCHITECTURE.md)*

**END OF ARTIFACT — UMB-004 · ACTIVE · APPEND-ONLY · AUTHORITY-NEUTRAL**


---

## AIF CONFORMANCE (Owner Amendment — ACT-C1 · append-only)

This architecture **REALIZES** the *Absolute Identity, Federation & Continuity Constitution (AIF)* — `UCOS-IMP-000024` (`02-MASTER/UCOS-Ω∞-ABSOLUTE-IDENTITY-FEDERATION-AND-CONTINUITY-CONSTITUTION.md`).

- **Single authority (X-DUP resolution):** exactly **one identity authority**. The AIF **governs**; this Nomenclature Architecture **realizes** it and asserts no parallel or duplicate naming/identity authority.
- **Realized laws:** AIF-L04 (witnessed non-recomputable admission ordinal P3; the human render `UCOS-<AUTH>-<CAT>-<n>` is authority-local, never globally monotonic), AIF-L07 (authority-namespaced uniqueness).
- **Subordination:** append-only; adds no authority; rewrites no existing content; renumbers no section; modifies no frozen artifact; subordinate to the AIF and all superior constitutional authority.
- **Traceability:** owner-side realization record referenced by AIF Part III (A/G-AUTH) and the AIF Traceability Register.

*Owner amendment only — realizes AIF; creates no authority.*
