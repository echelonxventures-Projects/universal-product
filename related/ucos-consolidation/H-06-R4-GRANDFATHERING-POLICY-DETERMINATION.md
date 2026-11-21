# H-06 R-4 GRANDFATHERING POLICY DETERMINATION

## 1. Authority

NONE — DETERMINATION ONLY. No policy selected. No implementation authorized.
Baseline: HEAD `1f869865` · branch `integration/recovery-001`

---

## 2. Question

If H-06 is ratified and implementation authorized: how should existing undeclared
mutation-capable gate entry points be handled during the transition while declarations
and replay contracts are being established?

---

## 3. Existing Migration Controls

| Control | Location | Capability | Status |
|---|---|---|---|
| `DECLARED-OPEN` condition mechanism | Programme declarations (e.g. UAUE) | Tracks a known gap with an explicit owner and discharge condition | EXISTING — used in UAUE `bootstrap_gaps` |
| `--check-declaration` self-guard | Per-engine argparse | Validates declaration integrity at runtime; fails closed on missing required fields | EXISTING — enforces current declaration schema |
| `forbidden_write_prefixes` guard | Per-engine, reads declaration | Write-scope enforcement; fails closed on out-of-scope writes | EXISTING — active on all engines with declarations |
| `ASSESSMENT-CONFLICT-REGISTER.md` | Repository root | Tracks unresolved conflicts with explicit human decision assignment | EXISTING — CR-09 is the H-06 registration |
| UGA `gate` mode `mint=False` | `uga_engine.py` | Separation of observation from mutation at engine level | EXISTING — reference pattern |
| `FINAL-FREEZE-ELIGIBILITY-DETERMINATION.md` | Repository root | Records freeze blockers with explicit conditions | EXISTING — gate purity is a named blocker |

---

## 4. Current Repository Reality

**Undeclared mutation paths:** 24 confirmed (GP-1: 15 engines; GP-2: 3 engines;
GP-3: 6 additional replay targets beyond GP-1/GP-2 engines).

**Current enforcement behaviour:** `verify.sh` passes on baseline `1f869865`. The
10/10 stages pass. The undeclared mutations do not currently cause a verification
failure because no gate enforces mode declaration. The defect is structural but silent
in the current verification regime.

**Consequence:** If `--check-declaration` is extended to require and validate a
`gate_mode` field, all 24 engines immediately fail their self-guard on the next run.
This would break `verify.sh` for every engine lacking a declaration until their
`gate_mode` field is added.

**Freeze impact of current state:** Gate purity is already a named freeze blocker.
The grandfathering policy does not change the freeze status — it governs the transition
path after implementation authorization, not the pre-decision state.

---

## 5. Policy Evidence Analysis

### Option 1 — Temporary Compliance Window

**Definition:** Undeclared mutation paths receive an explicit, bounded migration period
during which they are tracked as `gate_mode: UNDECLARED-PENDING-MIGRATION` (or
equivalent) in their declarations. The window has a defined deadline and owner.
Permanent exemption is not permitted.

**Evidence — benefits:**
- `verify.sh` continues to pass during migration. No single engine breakage blocks all
  other work.
- Migration can be sequenced by programme owner, reducing coordination overhead.
- The `DECLARED-OPEN` mechanism already exists in UAUE and provides a precedent: a
  gap is tracked, owned, and discharged — not silently tolerated.
- Operators can run gates safely during migration (assuming GP-2 and GP-10 code fixes
  are prioritized, since write-before-verdict and observe-alias mutation are defects
  regardless of mode).

**Evidence — risks:**
- Without a hard deadline enforced by a gate, migration windows can drift indefinitely.
  The history of GP-11 (42/46 undeclared at baseline after years of development)
  demonstrates that passive non-enforcement does not produce compliance.
- A `UNDECLARED-PENDING-MIGRATION` value in a declaration is itself an unverified claim
  unless the enforcement gate validates it and enforces a deadline.
- Evidence trust for PENDING-MIGRATION engines remains uncertain during the window.

**Required controls for Option 1 to be meaningful:**
1. A deadline field in the declaration alongside the pending status.
2. The `--check-declaration` guard must reject `UNDECLARED-PENDING-MIGRATION` after
   the deadline.
3. Each pending engine must be registered in a migration tracking surface (the existing
   `ASSESSMENT-CONFLICT-REGISTER.md` pattern is a candidate).
4. GP-2 and GP-10 code fixes must be treated as P0 — they are defects under any mode
   and cannot be grandfathered.

---

### Option 2 — Immediate Non-Compliance

**Definition:** On the date implementation authorization is granted, any engine without
a declared `gate_mode` field immediately fails its `--check-declaration` self-guard.
`verify.sh` fails until all 24 engines are declared.

**Evidence — benefits:**
- Clean invariant from day one of implementation: "every gate has a declared mode"
  is immediately true or immediately failing.
- No migration debt. The structural finding GP-11 is closed the moment implementation
  authorization is exercised, not after a window.
- Evidence trust is immediately clear: any engine passing `--check-declaration`
  has a verified mode.

**Evidence — risks:**
- All 24 engines must be declared before implementation authorization is exercised,
  or `verify.sh` breaks immediately across the full gate surface.
- This effectively requires batch implementation: declaration changes for all 24
  engines must be prepared before the enforcement gate is activated.
- If implementation is authorized in phases (Option B replay contracts, for example,
  require per-engine work), the enforcement gate cannot be activated until the last
  engine is ready.
- Under Option A, code changes in ≥18 engines must be complete before declarations
  are truthful — immediate non-compliance would require all code changes to precede
  the enforcement gate.

**Required controls for Option 2 to be meaningful:**
1. All 24 mode declarations must be prepared as a batch before the `--check-declaration`
   enforcement is activated.
2. A clear activation date for the enforcement gate must be part of the implementation
   authorization.
3. GP-2 and GP-10 code fixes remain P0 regardless.

---

## 6. Freeze Impact

**Does not affect freeze.**

R-4 is a migration-phase sub-decision. It governs the transition after implementation
authorization, which itself follows the H-06 owner decision. Foundation Freeze requires
the three gate-purity conditions to be satisfied, not that the migration policy be
selected in advance. R-4 must be resolved before implementation authorization is
issued, not before the owner records their Option A/B selection.

Updated R-4 status: **EVIDENCE COMPLETE — policy choice ready for owner.**

---

## 7. Remaining Unknowns

None blocking the H-06 owner decision.

| ID | Item | Status |
|---|---|---|
| R-1 | GP-6 collision verification | RESOLVED |
| R-2 | EXECUTION audit trail destination | RESOLVED |
| R-3 | `gate_mode` field name confirmation | RESOLVED |
| R-4 | Grandfathering policy | EVIDENCE COMPLETE — owner selects Option 1 or Option 2 as part of ratification |

All four ratification sub-decisions are resolved or evidence-complete.
The H-06 owner decision package is now complete for all dimensions.

---

No implementation authorized.
No governance option selected.
R-4 evidence determination complete.
