# IMR-0000/14 — RECOVERY FRAMEWORK

| Field | Value |
|---|---|
| MISSION | `IMR-0000` — CIOS Platform Foundation |
| ARTIFACT | `14` — Recovery Framework (**deliverable 24**) · directive capability 16 |
| ARTIFACT KIND | Framework (`CMG-K-05`) — binding declaration |
| SUBSYSTEM | `SS-11` `CIOS-RCV` — **BINDING-ONLY** (zero engines, zero ports); the lawful reach into protected work is `SS-14`'s `CIOS-P-35`, **not** this subsystem |
| CENTRAL CLAIM | **All recovery is forward-only.** Nothing in this corpus reverses; a recovery is a new change that restores a prior condition. Five recovery classes exist, each with one located owner. |
| AUTHORITY OF ITS OWN | **NONE.** |
| CONFLICT RULE | Located instrument governs (`CEP-009` for migration, `CEP-010` for audit, `MCP-007` for session recovery, `IEC-001` `06` for retry); then `IMR-003A` (`CIOS-11`, `CIOS-12`); then this artifact. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. THE FIVE RECOVERY CLASSES

Five distinct failures require recovery, and each has exactly one located owner. Treating them as one mechanism is what would produce a rollback registry — expressly prohibited (`UCI-OPT-001`).

| Class | Failure | Located owner | Mechanism | Forward-only? |
|---|---|---|---|---|
| **RV-1 · Session** | a session stops, is interrupted, or crashes | `MCP-007` §01, §04.B | resume from `MCP-002` state + the last checkpoint; reconcile recorded vs actual position by **updating the record forward** | **yes** |
| **RV-2 · Work item** | a dispatched item fails | `IEC-001` `06` | the located `FAILED → READY` retry edge, bounded by `MAX_RETRY` — the **sole** exception to one-way partition transitions | **yes** — a retry is a new attempt, not a rewind |
| **RV-3 · Repository** | recorded state and actual repository state diverge | `UCOS-RECON-001`; `MCP-007` §04.B; `UCOS-RECON-C1` | reconciliation determination; the divergence is recorded, then the record is advanced | **yes** |
| **RV-4 · Mission** | a mission terminates before delivering its declared outputs | `CEP-009` route; precedent `IMR-003A-R1` | a **successor recovery mission** (`-R<n>`) that is **additive only**: recovered artifacts are byte-identical, verified by digest | **yes** |
| **RV-5 · Constitutional** | an instrument is wrong, void, or must be replaced | `CEP-009` Art III / Art IV.3 / Art XI / Art XX.2; `CEP-010` audit | change/migration route with impact assessment; **successor instrument**, never in-place edit of a frozen artifact | **yes** |

| ID | Rule | Located basis |
|---|---|---|
| `RF-R1` | **No reversal exists.** Every recovery is a forward change that restores a prior condition. A "rollback" is a **new change artifact**, and there is **no rollback registry**. | `AIF-L17` (forward-only compensation); `UCI-OPT-001` row 7; `LR-5` |
| `RF-R2` | **Sealed work is not recovered; it is succeeded.** `CIOS-PT-01` items are byte-identical across epochs; correction proceeds by successor. | `CIOS-INV-03`; `CIOS-L-18`; `UUP-08` |
| `RF-R3` | **In-flight work is not rewound.** An item retains its bound plan epoch until terminal state; the only lawful path is the located retry (`RV-2`). | `CIOS-INV-04`; `CIOS-01` V.3 |
| `RF-R4` | **Reaching protected or sealed work requires a located override authority.** Exactly two exist, both located, each acting by declared, evidenced, recorded protocol. **An unrecorded override is void.** | `CIOS-L-21`; `E-18`; `CIOS-P-35` |
| `RF-R5` | **Recovery preserves monotonicity.** The certified set never shrinks. No recovery may reduce it, and no repository regression is admissible. | `CEP-001` LAW-7; `CIOS-L-20`, `CIOS-INV-10`; `SS-12` `E-23` observes |
| `RF-R6` | **A recovery mission is additive.** It does not restart, does not regenerate verified artifacts, and does not modify what it recovers. | `IMR-003A-R1` precedent (recovered artifacts byte-identical, digest-verified) |
| `RF-R7` | **Recovery is evidenced, not asserted.** A recovery without an evidence set and a recorded determination is a non-recovery. | `CEP-008`; `G-12`; `CIOS-L-07` |

---

## 2. THE TWO OVERRIDE AUTHORITIES

The only mechanisms that may reach protected or sealed work. Both are located; the platform adds neither and may add no third.

| Authority | Identity | Reaches | Protocol |
|---|---|---|---|
| `CIOS-OR-01` | **Constitutional Migration Authority** | protected and sealed work, for a constitutional change or migration | `CEP-009` change/migration route with impact assessment (`CEP-009` III.1, Art III) |
| `CIOS-OR-02` | **Critical Repository Integrity Authority** | protected and sealed work, for a repository-integrity emergency | declared, evidenced, recorded protocol (`CEP-009` Art XX.2; `CIOS-11` §4) |

| Property | Value |
|---|---|
| Override authorities | **2** — fixed by `CIOS-L-21` |
| Override authorities the platform may add | **0** |
| Override entry points | **1** — `CIOS-P-35` (`SS-14` `E-18`), public ingress |
| Default posture on any other reach | **deny**, with a finding (`SS-07` `E-17`) |
| Unrecorded override | **void** |
| Silent override | **impossible by declaration** — the record is a precondition of the adjudication, not a consequence of it |

---

## 3. THE RECOVERY PRECEDENT, MEASURED

`IMR-003A-R1` is the corpus's worked example of `RV-4`, and it is the reason `RF-R6` is stated as law rather than as guidance.

| Property of the located precedent | Value |
|---|---|
| Trigger | `IMR-003A` terminated after **2 of 22** declared outputs; 12 dangling forward references |
| Recovery mode | **additive only** |
| Recovered artifacts modified | **0** — byte-identical, verified by digest |
| Artifacts restarted | **0** |
| New subject token allocated | **0** — `UAES`/`UAMR` refused |
| Architectural gaps remaining after closure | **0** |
| Terminal act | a **declaration-scoped** stability contract — **not** a `CEP-007` freeze |

**This mission is itself operating under the same discipline.** The Context Assimilation Directive was handled as an `RV-4`-class event without a restart: 0 artifacts regenerated, 0 discarded, scope amended additively (`00A` Outputs 1 and 9).

---

## 4. WHAT CANNOT BE RECOVERED AT `b26c5bb`

Stated plainly, because a recovery framework that implied capabilities the corpus lacks would be worse than none.

| Capability | Status | Owner | Gate |
|---|---|---|---|
| Register-backed rollback | **UNAVAILABLE** — `changes.json`, `knowledge.json`, `regeneration.json`, `rollback.json` are absent | `UCI-001`; `WP-GDR-001` | `GG-3` / `CIOS-GAP-12` |
| Off-machine recovery anchor | **UNAVAILABLE** — the anchor lacks off-machine existence; no upstream configured | repository operator; `WP-GDR-002` | `GG-4` |
| Unfreeze / freeze reversal | **NOT APPLICABLE** — freeze itself is unavailable (`CEP-007` ineligible while `VAC-01` is open) | `CEP-007` authority | `CIOS-GAP-13` |
| Ratification-backed restoration of standing | **UNAVAILABLE** — no authority competent to ratify | `CEP-006`; `VAC-01` | `CIOS-G-03` |
| Recovery of this mission's own home from a commit | **UNAVAILABLE** — `00-MASTER/IMR-0000/` is **untracked** at `b26c5bb`, as `00-MASTER/IMR-003A/` was | repository operator / T4 | `CIOS-G-07` (same condition, this mission's instance recorded as `PF-03` in `23`) |

**Five recovery capabilities a reader might reasonably assume exist do not.** None is this mission's to supply, and none is claimed.

---

## 5. PROPERTIES

| Property | Value |
|---|---|
| Recovery classes declared | **5** |
| Recovery mechanisms created | **0** |
| Rollback registries created | **0** — prohibited (`UCI-OPT-001`) |
| Reversal operations defined | **0** (`RF-R1`) |
| Override authorities added | **0** |
| Sealed items reachable by the platform | **0** |
| Monotonicity guarantees weakened | **0** (`RF-R5`) |
| Public ports on `SS-11` | **0** — programmes bind `MCP-007`, `CEP-009`, `IEC-001` **directly** (`IFL-08`, `IFL-11`) |
| Unavailable capabilities recorded | **5** (§4) |

---

## 6. WHAT THIS FRAMEWORK DOES NOT DO

| Not done | Located owner |
|---|---|
| Perform, authorize or schedule any recovery | `MCP-007`; `IEC-001`; `CEP-009`; `UCOS-RECON-001` |
| Create a rollback, snapshot, restore or reversal mechanism | prohibited (`UCI-OPT-001`); `GG-3` |
| Add or alter an override authority, or reach protected work | `CIOS-L-21`; only `CIOS-P-35` reaches |
| Restate the interruption classes or the quiesce protocol | `CIOS-11` — bound by pointer |
| Reduce, restate or reinterpret the certified set | `CEP-001` LAW-7; `SS-12` observes |
| Discharge `GG-3`, `GG-4`, `CIOS-G-03`, `CIOS-G-07` or `CIOS-GAP-13` | each owner-held |

---

## AUTHORITY BOUNDARY (MANDATORY)

This framework binds five recovery classes to located owners. **It performs no recovery, creates no rollback or restore mechanism, defines no reversal, adds no override authority and reaches no protected or sealed work.** All recovery is forward-only; sealed work is succeeded, never rewritten. Five recovery capabilities are recorded as unavailable at `b26c5bb`, each with a named owner and an open gate; none is claimed. Every owner named is located in an instrument existing independently at `b26c5bb`. Where this framework and a located canonical instrument disagree, **the located instrument governs and this framework SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `IMR-0000/14` · PROVISIONAL · ADDITIVE · DESIGN-ONLY · AUTHORITY-NEUTRAL**
