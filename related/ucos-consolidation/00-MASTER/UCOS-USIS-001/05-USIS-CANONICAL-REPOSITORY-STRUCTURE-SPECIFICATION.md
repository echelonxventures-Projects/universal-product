# USIS-005 — Canonical Repository Structure Specification

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-005 (Repository Structure Specification) |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| STATUS | PROPOSED · AWAITING RATIFICATION · PRE-WAVE-0 |
| DEPENDS-ON | USIS-GOV-000 · USIS-002 · USIS-004 · config.py (VOLUMES/CLASSIFY_RULES/CHAINS) |
| CONFORMS-TO | existing program pattern (09-PLATFORM…14-SECURITY); metadata-driven classification; No-Orphan |

> **Purpose.** Define the single registerable repository structure for USIS — one tree, conforming to UCOS conventions, hosting all 21 universes without duplication or isolated folders.

---

## 1 — Top-level home (one tree)

```
15-UNIVERSAL-SCIENCE-INTELLIGENCE/
```

- `15` = next free top-level number (existing `09-PLATFORM` … `14-SECURITY`).
- Program family **`USIS`**, thematic volume **`VOL-023 UNIVERSAL SCIENCE & INTELLIGENCE`** (append-only).
- One tree → satisfies "no isolated folders"; universes are sub-homes, not separate top-level trees.

## 2 — Internal canonical structure (21 areas)

Mirrors the program pattern and hosts the 21 universes under `06-UNIVERSES/`:

```
15-UNIVERSAL-SCIENCE-INTELLIGENCE/
├── 00-CONSTITUTION/     # USIS-001 constitution + LAW USIS-00 + Part 19/20/21 anchors
├── 01-THEORY/           # theory of universal science & intelligence
├── 02-ONTOLOGY/         # substrate ontology (concepts, relations) — Ontology Closure
├── 03-TAXONOMY/         # taxonomy of sciences/universes/domains/algorithms/models
├── 04-REGISTRIES/       # all USIS registries (Universe, Science, Domain, Capability, Algorithm, Model, Pattern, Insight, Reasoning-Trace, Dataset, Learned-Change, Self-Evolution)
├── 05-META-MODEL/       # USIS-004 Universal Capability Meta-Model
├── 06-UNIVERSES/        # the 21 universes — one canonical sub-home each (U-SCI, U-INT, …)
├── 07-SCIENCES/         # Universal Science discipline homes (USIS-SCI-*)
├── 08-DOMAINS/          # cross-universe domains + Human-Intelligence families
├── 09-ALGORITHMS/       # algorithm universe (registry-backed)
├── 10-MODELS/           # model universe (agnostic Model Registry)
├── 11-PATTERNS/         # reasoning/learning/analytics/science patterns
├── 12-ENGINES/          # engines (reference registries; zero hard coding)
├── 13-SERVICES/         # services (reason/learn/predict/analyze/simulate/…)
├── 14-RUNTIME/          # runtime model (on-demand + continuous; governed autonomy; self-*)
├── 15-VALIDATION/       # validation model (grounding, explanation coverage) — Validation Closure
├── 16-CERTIFICATION/    # certification model — Certification Closure
├── 17-EVIDENCE/         # evidence model (traces, provenance)
├── 18-APIS-SDK/         # API + SDK surfaces
├── 19-DOCUMENTATION/    # documentation + examples + reference implementations
└── 20-PROJECTS/         # implementation projects
```

> This supersedes the UIP `15-UNIVERSAL-INTELLIGENCE/` layout. The 21 mission areas are preserved and mapped: CONSTITUTION/THEORY/ONTOLOGY/TAXONOMY/REGISTRIES/CAPABILITIES(→05-META-MODEL+08-DOMAINS)/DOMAINS/ALGORITHMS/MODELS/PATTERNS/ENGINES/SERVICES/RUNTIME/VALIDATION/CERTIFICATION/EVIDENCE/DOCUMENTATION/APIS/SDK/TOOLS(→19)/PROJECTS. `06-UNIVERSES/` + `07-SCIENCES/` are the substrate additions that host the expanded scope.

## 3 — Artifact naming (conforms to program pattern)

Founding sequence, then per-area:

| Seq | Artifact | Area |
|----|----------|------|
| USIS-GOV-000 | Program establishment determination (chain head / root) | governance |
| USIS-001 | UNIVERSAL-SCIENCE-INTELLIGENCE-CONSTITUTION | 00 |
| USIS-002 | UNIVERSE-CATALOG | 06 |
| USIS-003 | UNIVERSAL-SCIENCE-CATALOG | 07 |
| USIS-004 | UNIVERSAL-CAPABILITY-META-MODEL | 05 |
| USIS-005 | …-THEORY / …-ONTOLOGY / …-TAXONOMY (foundation) | 01/02/03 |
| USIS-006…017 | per-universe & per-layer architectures (Capability/Domain/Algorithm/Model/Pattern/Engine/Service/Runtime/Validation/Certification/Evidence/API-SDK) | 08–18 |
| USIS-018 | UNIVERSAL-SCIENCE-INTELLIGENCE-FOUNDATION-FREEZE-DETERMINATION | governance |
| USIS-019 | READINESS-DETERMINATION | governance |
| USIS-020 | COMPLETION-DETERMINATION | governance |
| USIS-021 | MASTER-REGISTRY | 04 |

Per-universe artifacts: `USIS-U-<UNIV>-NNN` under `06-UNIVERSES/<UNIV>/`. Per-science: `USIS-SCI-<NAME>-NNN` under `07-SCIENCES/`. Per-domain/capability: `USIS-DOM-*` / `USIS-CAP-*`. Algorithm/model/self-evolution entries are registry rows (`USIS-ALG-*`, `USIS-MDL-*`, `USIS-EVO-*`), not architecture.

## 4 — Self-classification metadata (mandatory front-matter)

Every USIS corpus artifact SHALL carry:

```
| UCOS-PROGRAM  | USIS                              |
| UCOS-CATEGORY | USIS                              |
| UCOS-VOLUME   | VOL-023                           |
| UCOS-FAMILY   | UNIVERSAL-SCIENCE-INTELLIGENCE    |
| UCOS-DOMAIN   | science-intelligence              |
```

This classifies each artifact via `METADATA_CLASSIFY_KEYS` even before the curated `config.py` rule; the path-derived catch-all provides totality as a third net → `unclassified == 0`.

## 5 — Canonical ownership & No-Orphan homing

- Each area/universe/science has exactly one owning artifact and one canonical home.
- Every artifact declares `Parent` (USIS chain predecessor) + `Depends-On` edges → acyclic chain rooted at `USIS-GOV-000`, which `Depends-On` the terminal of the prior program (downward-only).
- **Reuse-First:** Data → `10-DATA`, Security → `14-SECURITY`, Runtime → `08-RUNTIME`/RIE, Simulation → U26 are **referenced**, never re-homed. USIS areas specialize the universal models for science/intelligence; they do not fork them.

## 6 — Intentionally NOT created here (pre-Wave-0)

No physical `15-…/` files, no `config.py` edit, no registration transaction are performed by this package. This spec is the authoritative blueprint the governed Wave-0 build follows.
