# 02 — USIS-001 VALIDATION SUMMARY (independent re-execution)

**Environment.** Canonical `.ec1-venv/bin/python` = **Python 3.12.13**. All gates re-run by the acceptance reviewer against the live regenerated repository state. Working tree unchanged by the runs (idempotent).

---

## 1 — Gate results (re-run, not copied)

| # | Gate | Command | Result | Key metrics |
|---|---|---|:--:|---|
| 0 | Pre-registration enforcement | `ukb.py enforce --pre` | **PASSED** | 1003 eligible == 1003 registered; 0 unregistered / 0 unclassified / 0 invalid (audit run #182) |
| 1 | Registration transaction | `register.sh` (10 phases) | **TRANSACTION COMPLETE** (exit 0) | build: 1003 artifacts · 25 volumes · 11 845 edges · 9 136 pages; 1096 change events; 15 signals |
| 2 | Structural validation | `ukb.py validate` | **PASSED** | 1003 artifacts; append-only page ledger intact; referential integrity OK; forward-only lifecycle intact |
| 3 | Post-registration enforcement | `ukb.py enforce` | **PASSED** | 1003 == 1003; 0 unregistered / 0 unclassified / 0 invalid (audit run #181) |
| 4 | Twin/signal validation | `ukbx.py validate` | **PASSED** | 15 signals; append-only; every subject resolves; provenance present; no embedded secrets |
| 5 | Digital-twin certification | `ukbx.py twin --check` | **CERTIFIED 7/7** | C-07 acyclic · C-08 navigation reachable+return · C-09 control-tower automated · C-10 export non-empty · C-11 search (167 hits) |
| 6 | Certification runtime | `ukbx.py certify` | **CERTIFIED 10/10** | Identity · Registry · Traceability · Knowledge-Graph · Change · Version · Lineage · Synchronization · Twin-Intelligence · Execution — scope 1003 artifacts, 15 signals, 1096 change events |
| 7 | Drift gate | `register.sh --guard` | **exit 3 — EXPECTED** | Drift == exactly the 16 regenerated guard-scope files + new `PORTAL/UCOS-USIS-000002.md` |

All gates that must pass, pass. The only non-zero exit (`--guard` = 3) is the **intended** signal that the completed registration is not yet committed (STOP condition).

## 2 — Guard-drift attribution (mission-critical confirmation)

`register.sh --guard` reported drift on exactly:

```
 M 00-BOOK/CONTROL-TOWER/PROGRAM-CONTROL-TOWER.md
 M 00-BOOK/DATA/{artifacts,certification,change-ledger,control-tower,id-ledger,relationships,volumes}.json
 M 00-BOOK/PORTAL/{index.md, UCOS-USIS-000001.md}
 M 00-BOOK/REGISTRIES/{CERTIFICATION, CHANGE-VERSION-LINEAGE, KNOWLEDGE-GRAPH, UNIVERSAL-ARTIFACT, UNIVERSAL-PAGE, VOLUME}-REGISTRY.md
 ?? 00-BOOK/PORTAL/UCOS-USIS-000002.md
```

Cross-checked against `git status`:
- Outside `00-MASTER/`, the **only** untracked items are the two USIS-001 realization artifacts: the corpus file `15-…/00-CONSTITUTION/…CONSTITUTION.md` and its portal page `UCOS-USIS-000002.md`.
- `config.py` and all frozen paths are clean.

**Conclusion:** the guard drift is **solely attributable to the intentionally uncommitted USIS-001 implementation.** No unrelated file appears in the guard's enforcement scope (`00-BOOK/{DATA,REGISTRIES,CONTROL-TOWER,PORTAL}`).

## 3 — Dependency / classification / registration correctness

- **Classification:** program USIS, category USIS, VOL-024, family UNIVERSAL-SCIENCE-INTELLIGENCE, domain science-intelligence — resolved from front-matter (`METADATA_CLASSIFY_KEYS`) and confirmed by the committed `config.py` path rule. `unclassified == 0`.
- **Dependency:** `Depends-On` + `Parent` + `Authorized-By` → `UCOS-USIS-000001`; downward-only; acyclic (C-07); no forward reference (target pre-registered in Wave-0); no `config.py` chain edit.
- **Registration:** present in every synchronized register (artifact/page/graph/volume/change-version-lineage/certification); id-ledger append-only (no reuse/renumber).

## 4 — Caveats (full disclosure — non-blocking)

1. **`jsonschema` not installed** in the local venv → `ukb validate` ran **structural checks only** (self-reported and independently reproduced). This matches the published-baseline environment; the CI workflow `ucos-registration-gate.yml` installs `jsonschema` and exercises full schema validation on push/PR. Recommended (non-blocking): `pip install jsonschema` for local parity.
2. Obligations 11/12 (ontology/taxonomy closure) and 13 (capability-chain) apply to later USIS-004/005 content and are correctly **out of scope** for the constitution.

## 5 — Determination

**USIS-001 is constitutionally validated, dependency-correct, and registration-correct. All applicable gates PASS on independent re-execution.** Detailed determinism evidence in `03-USIS001-DETERMINISM-REPORT.md`.
