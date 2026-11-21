# 03 — Determinism Certification

| Field | Value |
|-------|-------|
| ARTIFACT ID | WAVE0-ACC-03 (Determinism Certification) |
| MISSION | Wave-0 Acceptance / Baseline Certification |
| STATUS | COMPLETE · AUTHORITY = NONE (DERIVED) · READ-ONLY |

---

## 1 — FREEZE C4 reproducibility

| Run | Command | FREEZE C4 seal |
|-----|---------|----------------|
| 1 | `python3 00-MASTER/UCOS-USIS-WAVE0/freeze_c4_engine.py` | `710769fca46d2655eb9e34a1229cf60f3ee35451dd4863551811500bea0309bf` |
| 2 | (re-run) | `710769fca46d2655eb9e34a1229cf60f3ee35451dd4863551811500bea0309bf` |

**Byte-identical.** Additionally, the engine independently **recomputed the FREEZE C2 object-distribution seal = `f966c8e0fd135cc5abf77012ced83a15f1b8135e59f18f1b6fd34e0e9794668f`** — identical to the repository-recorded FREEZE C2 seal — proving the C4 model is a faithful, deterministic extension of C2 (not fabricated). **PASS.**

## 2 — Registry / repository-generation reproducibility

| Run | Command | Output |
|-----|---------|--------|
| 1 | `ukb build` | 1002 artifacts, 25 volumes, 11839 edges, 9134 pages |
| 2 | `ukb build` | 1002 artifacts, 25 volumes, 11839 edges, 9134 pages |

**Identical.** Working-tree change count **52 before = 52 after** the re-run → the regeneration is **idempotent** (no growing drift; re-running produces the same outputs). `register.sh` transaction is likewise idempotent (append-only ledger; deterministic regeneration). **PASS.**

> Note: the "25 volumes" figure is deterministic but **reflects the blocking duplicate `VOL-023`** (B1). Determinism means the defect is *stably reproduced*, not that it is absent. Post-remediation the deterministic figure will be 25 distinct volumes with a single `VOL-023` and a single `VOL-024`.

## 3 — Determinism verdict

| Property | Result |
|----------|:------:|
| FREEZE C4 reproducible (byte-identical) | ✅ |
| FREEZE C2 seal faithfully recomputed | ✅ (`f966c8e0…`) |
| Registry/graph/page generation reproducible | ✅ |
| Idempotent (repeat run → same result, no new drift) | ✅ |
| Append-only identity preserved (no reuse/renumber) | ✅ (`ukb validate` referential integrity OK) |

**Determinism CERTIFIED.** Repeated execution produces identical results. (This certifies *reproducibility*; it does not by itself certify *correctness* — the reproduced state contains defect B1, addressed in 01/04.)

*END — 03 · DETERMINISM CERTIFICATION · REPRODUCIBLE · AUTHORITY = NONE (DERIVED).*
