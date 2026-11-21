# 04 — KNOWLEDGE CLASSIFICATION

> **Mission:** IAC-001B · **Mode:** READ-ONLY · **Baseline:** HEAD `836475c`
> Every CKO must belong to exactly one constitutional classification.

---

## 1. Classification is self-declared

Every identity-block CKO carries a `CLASSIFICATION` field. Classification is therefore established per-artifact from canonical sources, not inferred. Observed classification values map onto the mission's constitutional classes:

| Constitutional class | Declared-classification evidence | Home(s) |
|---|---|---|
| **Constitution** | "Constitutional … Constitution" (CEP-000..010); "Program Constitution — supreme instrument" (USIS-001) | `00-CEP`, `02-MASTER`, `15-…` |
| **Universe** | "Universe Catalog" (USIS-002) | `15-…/06-UNIVERSES` |
| **Foundation** | "Foundational Architecture-Governance Artifact" (UCOS-COMP-000000/000001); FOUNDATION family | `02-MASTER` |
| **Registry** | "…state registry" (UCOS-COMP-000000-ISR — derived); registry constitutions | `02-MASTER` (+ derived in `00-BOOK`) |
| **Catalog** | 7 `UNIVERSAL-CANONICAL-*-CATALOG` | `03-CATALOGS` |
| **Schema** | `*.schema.json` | `00-BOOK/SCHEMAS` |
| **Model / Meta-Model** | "Universal Capability Meta-Model" (USIS-004); "…META-MODEL" (INFRASTRUCTURE-005) | `15-…/05-META-MODEL`, band dirs |
| **Engine** | authored `engine/**` packages | `engine/**` |
| **Runtime** | "Universal Runtime Theory/Taxonomy" (RUNTIME-002/004) | `08-RUNTIME` |
| **Policy / Rule / Constraint** | "Permanent … Rules" (CIOA/CCE); LAW invariants | `02-MASTER`, laws |
| **Capability** | "Universal Capability …" (USIS-004; AEOS-001) | `15-…`, `02-MASTER` |
| **Service / Workflow** | SERVICE/WORKFLOW catalogs + band architectures | `03-CATALOGS`, `11-SERVICE` |
| **Validation / Certification** | CEP-004/005; band GOV certification determinations | `00-CEP`, band dirs |
| **Architecture** | "Universal … Architecture"; "Specialized Concern Architecture — Implementation-Independent" | `04-REFERENCE`, `08-…14-` |
| **Determination** | "Governance Determination Artifact — …" | `02-MASTER`, band dirs, `00-MASTER` |

## 2. Unclassified-object report

**No unclassified canonical knowledge object found.** Every identity-block CKO carries a `CLASSIFICATION` value that maps to exactly one constitutional class above. Artifacts without an identity block are derived determinations / program-step records / historical checkpoints — they are not canonical-establishing CKOs and inherit their program's classification.

## 3. Determination

> **VERIFY 4 (Classification): PASS.**
> Every CKO belongs to exactly one constitutional classification; zero unclassified canonical objects.

---
*End of 04-KNOWLEDGE-CLASSIFICATION.md*
