# 00-CMG — CONSTITUTIONAL META GOVERNANCE

| Field | Value |
|-------|-------|
| ARTIFACT ID | CMG-000000 |
| ARTIFACT | UCOS Ω∞ Constitutional Meta Governance Zone Index |
| CLASSIFICATION | Constitutional Meta Governance (CMG) — Zone Index |
| PHASE | PHASE-000 |
| PROGRAM | CMG |
| CATEGORY | CMG |
| VOLUME | VOL-002 |
| STATUS | UNDER REVIEW · DERIVED · NON-NORMATIVE |
| VERSION | 1.0 |
| AUTHORITY | NONE (DERIVED TRUTH) |
| GOVERNED-BY | CMG-000001 |
| CANONICAL FORM | This Markdown file |

This zone holds the **meta-constitutional layer** of UCOS Ω∞: the law that defines what a Constitution *is*, which artifacts *are* constitutions, and how constitutional authority is allocated and ranked across the whole corpus.

It governs **recognition**, never **substance** and never **process**. Substance belongs to each domain constitution; process belongs supremely to the Constitutional Engineering Program. The meta layer's only operations on other instruments are **recognize, record, rank, and refer**.

---

## Contents

| Artifact | Purpose | Normative? |
|---|---|---|
| [`CMG-000001`](CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md) | **The Constitutional Meta Governance Constitution.** 86 articles covering all 80 mandated sections plus closing law | **Yes**, upon ratification |
| [`CMG-000002`](CMG-000002-CONSTITUTIONAL-REPOSITORY-IMPACT-ANALYSIS.md) | What admission does and does not do to the repository | No |
| [`CMG-000003`](CMG-000003-CONSTITUTIONAL-GAP-ANALYSIS.md) | The nine gaps, their evidence, and their dispositions | No |
| [`CMG-000004`](CMG-000004-CONSTITUTIONAL-DEPENDENCY-ANALYSIS.md) | The two acyclic graphs, dependency chains, and standing propagation | No |
| [`CMG-000005`](CMG-000005-CONSTITUTIONAL-GOVERNANCE-ANALYSIS.md) | Authority allocation; Zero Parallel Authority and Zero Orphan Governance demonstrations | No |
| [`CMG-000006`](CMG-000006-CONSTITUTIONAL-VALIDATION-STRATEGY.md) | The 16 check groups, fail-closed semantics, determinism, and limits | No |
| [`CMG-000007`](CMG-000007-CONSTITUTIONAL-CERTIFICATION-STRATEGY.md) | The Constitutional Readiness subject, 14 preconditions, path to `READY` | No |
| [`CMG-000008`](CMG-000008-CONSTITUTIONAL-MIGRATION-STRATEGY.md) | Why no migration is required, and what would require one | No |
| [`CMG-000009`](CMG-000009-CONSTITUTIONAL-INTEGRATION-STRATEGY.md) | Binding to every located surface without creating a parallel one | No |
| [`CMG-000010`](CMG-000010-CONSTITUTIONAL-FUTURE-EVOLUTION-STRATEGY.md) | The Zero-Finite test, four structural devices, admission of the unknown | No |
| [`CMG-000011`](CMG-000011-CONSTITUTIONAL-ZERO-MISSING-VERIFICATION.md) | Coverage of every mandated definition, section, quality and repository requirement | No |
| [`CMG-000012`](CMG-000012-CONSTITUTIONAL-IMPLEMENTATION-READINESS-ASSESSMENT.md) | What was executed, what was observed, defects found and fixed | No |
| [`CMG-000013`](CMG-000013-CONSTITUTIONAL-RECOMMENDATIONS.md) | Ten recommendations, each naming the owner competent to act | No |
| [`CMG-000014`](CMG-000014-CONSTITUTIONAL-OPEN-QUESTIONS-FOR-RATIFICATION.md) | The seven recorded open questions (six open; `CMG-OQ-04` closed by Wave-2 Mission E-3) | No |
| [`CMG-REGISTRY.json`](CMG-REGISTRY.json) | Machine-readable projection: artifacts, concerns, tiers, states, gaps, vacancies | No — derived truth |
| [`tools/cmg_validate.py`](tools/cmg_validate.py) | The validator: 16 check groups over the 12 invariants | No — derived truth |
| [`tools/cmg-gate.sh`](tools/cmg-gate.sh) | The single permitted gate entry point | No |

---

## Running the gate

```
make cmg-gate                              # or
./00-CMG/tools/cmg-gate.sh                 # or
python3 00-CMG/tools/cmg_validate.py [--emit path/to/evidence.json]
```

Exit status: `0` zero findings · `1` findings · `2` fail-closed abort.
Standard library only; no network, no third-party package, byte-identical output across runs.

Current result: **0 findings**, readiness **`READY-PROVISIONAL`**.

---

## Where to start

- **To understand the design:** CMG-000001 Articles VI, VII (why a meta layer at all), XVI (the precedence lattice), and LXXXII (the delegation register — the whole Zero-Parallel-Authority mechanism in one table).
- **To understand what is unfinished:** CMG-000014. Two questions dominate everything else.
- **To understand what this changes in the repository:** CMG-000002. The answer is: one new zone, eight appended `Makefile` lines, and the derived registry/portal regeneration that the repository's own registration hook performed automatically — with zero existing identifiers renumbered and zero existing content hashes changed.

---

## The one thing to know

CMG-000001 recorded itself PROVISIONAL while its ratifying authority was unidentified, and said so; UCOS-RAT-002 records that authority's act and the instrument stands RATIFIED. Tier T1 — the substantive constitutional authority presupposed by CEP-000 §5.5 — was recorded **vacant** and is now **occupied** by the ratified constitution of substance. The validator computes readiness from the Registry, and the outcome for this state is READY; the ceiling rule of LXXX.4 stands against any future reopening.
