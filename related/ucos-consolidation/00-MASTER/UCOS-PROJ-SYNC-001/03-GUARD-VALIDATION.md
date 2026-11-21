# 03 — GUARD VALIDATION

All commands executed with `.ec1-venv/bin/python` (Python 3.12). Raw logs:
`00-MASTER/UCOS-PROJ-SYNC-001/evidence/`.

---

## 1. Mission validation sequence — results

| # | Command | Result | Key evidence |
|---|---|---|---|
| 1 | `ukb build` | OK | 1002 artifacts, 25 volumes, 11,839 edges, 9134 pages allocated |
| 2 | `ukb validate` | **PASSED** | append-only page ledger intact; referential integrity OK |
| 3 | `ukb enforce` | **PASSED** | 1002 eligible == 1002 registered; 0 unregistered; 0 unclassified; 0 invalid |
| 4 | `ukbx validate` | **PASSED** | 15 signals, append-only, every subject resolves, provenance present, no embedded secrets |
| 5 | `ukbx twin --check` | **CERTIFIED (7/7)** | C-07 acyclic · C-08 navigation reachable+return · C-09 control-tower automated · C-10 export non-empty · C-11 search |
| 6 | `ukbx certify` | **CERTIFIED (10/10)** | Identity, Registry, Traceability, Knowledge-Graph, Change, Version, Lineage, Synchronization, Twin-Intelligence, Execution |
| 7 | `register.sh` | **TRANSACTION COMPLETE** | all 10 phases pass (pre-enforce → build → sync → twin → portal → validate ×2 → twin-check → certify → post-enforce) |
| 8 | `register.sh --guard` | **Guard PASSED** | committed DATA/REGISTRIES/CONTROL-TOWER/PORTAL show zero drift |

## 2. Guard determination

```
-- Guard: checking committed synchronized state for drift
Guard PASSED — repository, registry, control tower, twin, and portal are in sync.
GUARD_EXIT=0
```

Post-commit guard-scope working-tree status is **empty**:

```
$ git status --porcelain -- 00-BOOK/DATA 00-BOOK/REGISTRIES 00-BOOK/CONTROL-TOWER 00-BOOK/PORTAL
<no output>
```

`register.sh --guard` (exit 3 on drift) returned **exit 0** → the committed
synchronized state matches deterministic regeneration exactly. Zero projection
drift.

## 3. Certification runtime detail (`ukbx certify`)

```
RESULT: CERTIFIED (integrity domains 10/10) — scope 1002 artifacts, 15 signals, 1095 change events
  evidence : 00-BOOK/DATA/certification.json
  report   : 00-BOOK/REGISTRIES/CERTIFICATION-REGISTRY.md
```

Representative hard checks (from `certification.json`): `no duplicate Universal
IDs → 1002 unique`; `no overlapping page ranges → PASS`; `ledger page cursor >=
max page → cursor=9134 max_end=9134`; `every artifact present in id-ledger →
1002 ledgered`; `no dangling edge endpoints → 11839 edges resolve`; `Depends-On
graph acyclic → PASS`; `snapshot history seq monotonic (append-only) → PASS`.

## 4. Caveats (full disclosure)

- **`ukb validate` schema layer:** `jsonschema` is not installed in the venv, so
  `ukb validate` ran **structural + referential** checks only (JSON-Schema
  validation skipped — the tool reports this as an optional enhancement, not a
  failure). All structural, append-only, and referential invariants passed. This
  does not affect projection determinism or the guard result.
- **Runtime telemetry** (enforcement/certification audit logs) is written to
  `.runtime/` which is `.gitignore`d by design (permanent remediation for
  telemetry-induced non-determinism); it is not part of the guard scope and
  cannot register as drift.
