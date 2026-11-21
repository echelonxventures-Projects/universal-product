# Output 0 — Repository Discovery Baseline · Index

> **STATUS DOMAIN:** GOVERNANCE (measurement) · **STATUS BASIS:** direct measurement of the committed repository at HEAD `9de85ad`, plus the located owners' own generated outputs cited per finding (STATUS-001 §3)

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000007` — Repository Controlled Implementation Programme |
| OUTPUT | 0 — Discovery Index |
| PHASE | 0 — Repository Discovery Baseline |
| AUTHORITY | **NONE — DERIVED TRUTH.** This programme measures. It legislates nothing, decides nothing, owns no concern, and authorizes no step. |
| GOVERNING AUTHORITY | `00-CEP/CEP-008` (evidence & traceability operation, `CMG-DLG-08`) · `00-MASTER/MCS-000` (operational memory) · `00-MASTER/UCCEP-000006/06-IMPLEMENTATION-BOUNDARY-SPECIFICATION.md` §1 **P-5** (programme-owned outputs under `00-MASTER/<PROGRAMME-ID>/`) |
| ROLLBACK ANCHOR | `1c6e750e53efdbcba5fc501d58fc99781b03a966` (OA-1 atomic constitutional baseline commit) |
| BASELINE MEASURED | HEAD `9de85adb7e26211d07bd99b3bed356280c936a93` · branch `programme/evo-usis-005` · working tree **CLEAN** (0 entries) |
| MEASURED ON | 2026-07-26 |
| CERTIFICATION DISCLOSURE | `CERTIFIED-PROVISIONAL`. Constitutional Tier T1 is **VACANT** (`VAC-01` · `CMG-OQ-02` · `UCCEP-F-004`). Nothing recorded here is ratified or final. (condition **C-3**, constraint **K-09**) |

> **What this programme is.** The repository's canonical **discovery evidence** at the OA-1 baseline. Every statement is a measurement of committed repository state or a verbatim reproduction of a located owner's own output, with the command that produced it recorded in `17-EVIDENCE-APPENDIX.md`.
>
> **What this programme is not.** Not a determination. Not an implementation plan. Not a migration strategy. Not a governance decision. It assigns no disposition, allocates no identifier, recommends no action, and proposes no architecture. Where repository evidence cannot resolve a question, the question is recorded unresolved in `16-DECISION-DERIVED-INPUTS.md` and routed to its owning authority — never answered here.

---

## 1. Structure — one responsibility per artifact

Knowledge exists once. Each inventory owns exactly one subject and **cross-references** the others rather than restating them.

| Output | Artifact | Sole responsibility | Does **not** contain |
|---|---|---|---|
| 0 | `00-DISCOVERY-INDEX.md` | Scope, method, structure, reading order | Any measurement |
| 1 | `01-REPOSITORY-INVENTORY.md` | Physical repository: file counts, zones, extensions, git facts | Programme or artifact semantics |
| 2 | `02-PROGRAMME-INVENTORY.md` | Programmes and their operational-memory directories | Constitutions, registries |
| 3 | `03-CONSTITUTION-INVENTORY.md` | Recognized constitutional artifacts, kinds, tiers, standings | Concern ownership (→ 09) |
| 4 | `04-REGISTRY-INVENTORY.md` | The register set, its stores and measured contents | Registry gates (→ 10) |
| 5 | `05-CAPABILITY-INVENTORY.md` | Declared capability catalogue as measured | Realization state (→ 06) |
| 6 | `06-IMPLEMENTATION-INVENTORY.md` | Realized code trees, tests, coverage | Capability declarations (→ 05) |
| 7 | `07-GENERATED-ARTIFACT-INVENTORY.md` | Generated vs authored classification; the generators | Contents of generated files (→ 4) |
| 8 | `08-DEPENDENCY-INVENTORY.md` | Edge population, `Depends-On` DAG, ordering | Ownership (→ 09) |
| 9 | `09-OWNERSHIP-INVENTORY.md` | Concern → owner allocation as located | Constitution metadata (→ 03) |
| 10 | `10-VALIDATION-INVENTORY.md` | Checks, gates, enforcement chain, entry points | Certification verdicts (→ 11) |
| 11 | `11-CERTIFICATION-INVENTORY.md` | Certification verdicts, domains, ceiling | Gate composition (→ 10) |
| 12 | `12-DISCOVERY-OBSERVATIONS.md` | Measured observations that no single inventory owns | Judgements, recommendations |
| 13 | `13-KNOWN-GAPS.md` | Gaps recorded by located owners | Risk assessment (→ 14) |
| 14 | `14-KNOWN-RISKS.md` | Risks recorded by located owners | Treatments or decisions |
| 15 | `15-OPEN-CONSTITUTIONAL-QUESTIONS.md` | Open questions and vacancies as recorded | Answers |
| 16 | `16-DECISION-DERIVED-INPUTS.md` | Items repository evidence cannot resolve | Any resolution |
| 17 | `17-EVIDENCE-APPENDIX.md` | Every command, output file and digest | Interpretation |

## 2. Measurement method

Four admissible sources, and no fifth:

| # | Method | Meaning | Marker used |
|---|---|---|---|
| **M-1** | Direct git measurement | `git` interrogation of committed state at HEAD `9de85ad` | `M-1` |
| **M-2** | Direct file measurement | Enumeration/parsing of committed files by path | `M-2` |
| **M-3** | Located owner's own output | A value reproduced verbatim from a generated artifact or an engine's own run | `M-3` |
| **M-4** | Independent recomputation | A located owner's claim recomputed from primary data by this programme | `M-4` |

Nothing is inferred, summarized from conversation, or carried over from another session's narrative. A statement with no method marker is not a finding of this programme.

## 3. Reference convention

To keep cross-references unambiguous, and because several zones use two-digit filename prefixes:

| Form | Meaning |
|---|---|
| `NN-NAME.md` with no directory | a **sibling output of this programme**, i.e. `00-MASTER/UCCEP-000007/NN-NAME.md` |
| any path containing `/` | **repository-relative** from the repository root; a leading `/` marks a root-level artifact whose own name carries a two-digit prefix (e.g. `/02-CANONICAL-OWNERSHIP-MATRIX.md`) |
| a bare filename in prose (e.g. `artifacts.json`, `config.py`) | shorthand for the fully-qualified path introduced earlier in the same output |
| `OBS-n` · `DG-n` · `DR-n` · `DDI-n` | identifiers defined in Outputs 12 · 13 · 14 · 16 respectively |
| `CMG-*` · `UCCEP-F-*` · `WP-*` · `CK-*` · `G-*` · `VAC-01` · `C-n` · `K-n` · `RB-n` · `V-n` · `X-n` · `P-n` · `OA-n` | identifiers owned by located instruments, reproduced never coined |

Outputs of **other** UCCEP programmes are always written with their directory (e.g. `00-MASTER/UCCEP-000000/01-CANONICAL-ASSIMILATION-REGISTER.md`), never bare, so they cannot be mistaken for siblings.

## 4. Reading order

`01` → `02` → `03` → `04` establishes what exists. `05` → `06` → `07` → `08` establishes what is realized and how it is produced. `09` → `10` → `11` establishes who owns and what passes. `12` → `15` records what is open. `16` records what only an authority can answer. `17` proves all of it.

## 4. Baseline integrity

| Fact | Value | Method |
|---|---|---|
| Rollback anchor is an ancestor of HEAD | **true** (`git merge-base --is-ancestor` exit 0) | M-1 |
| Working tree at measurement | **CLEAN**, 0 entries | M-1 |
| Tracked files | **4,499** | M-1 |
| Commits in history | **183** | M-1 |
| Full-tier aggregate gate at the anchor | exit 0 · 14/14 gates · 16/16 programmes · blocking none | M-3 |

Because the tree is clean, every measurement in this programme is reproducible from committed history alone. Evidence files are written to `evidence/`, which the ignore authority excludes from version control (`.gitignore` → `00-MASTER/**/evidence/`); `17-EVIDENCE-APPENDIX.md` therefore carries the commands and the material values inline so the baseline survives independently of that directory.

---

*`UCCEP-000007` Output 0. AUTHORITY = NONE (DERIVED TRUTH). Creates no authority, allocates no identity, supersedes no instrument. Where this conflicts with a higher frozen or governing instrument, the higher instrument governs.*
