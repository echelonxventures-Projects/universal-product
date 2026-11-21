# 06 — Origin Uniqueness Register

> PROGRAM **UAKOS PHASE-001A-R1** — Constitutional Baseline Re-Certification · closure baseline `8444c995` (branch `integration/recovery-001`) · corrected Authoritative-Origin model (Phase-001B) · AUTHORITY = **NONE (DERIVED / CERTIFIED TRUTH)** · **READ-ONLY** · derived from provenance baseline `8444c995` by `cert_engine.py`.
>
> Proof that every object has exactly one valid origin.
>
> Reproduce: `python3 00-MASTER/UAKOS-PHASE-001A-R1/cert_engine.py`.

| Uniqueness invariant | Count | Status |
|---|---|---|
| Objects with MULTIPLE authoritative origins | 0 | PASS |
| Objects with UNKNOWN origin | 0 | PASS |
| Objects with NO origin | 0 | PASS |
| Objects with CONFLICTING origins | 0 | PASS |
| Objects with CIRCULAR origins | 0 | PASS |
| Objects with INVALID origins | 0 | PASS |
| Objects with EXACTLY ONE valid origin | 550 | PASS |

**Origin Integrity = 100.0%** (550/550 objects with exactly one valid authoritative origin).
