# Output 2 — Outstanding Obligations Assessment

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000006` |
| PHASE | 2 — Outstanding Obligation Verification |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| SCOPE | The four obligations carried in `12-HANDOVER-TO-UCCEP-000006.md` §8.2 |
| CLASSIFICATION SET | Resolved · Pending · External · Not Blocking · Blocking |

> This phase classifies. It does not discharge O-01 or O-02: both are explicitly owned
> elsewhere (repository operator; UCCEP-000000 / `engine/graph`), and committing another
> owner's working tree is not an act this programme may take. O-03 is this programme's own
> act and is discharged in Output 5.

---

## 1. Classification summary

| # | Obligation | Owner | Verified state | **Classification** |
|---|---|---|---|---|
| **O-01** | Committed registration — `CK-REG-DRIFT` → PASS, `G-07` → PASS | repository operator · `WP-UCCEP-005` | **Not done.** 127 dirty entries measured; `00-CMG/`, `00-MASTER/UCCEP-000000/`, `00-MASTER/UCCEP-000005/` untracked; `MCP-002` §01 stale | **PENDING · BLOCKING** |
| **O-02** | `UCCEP-F-003` recorded as discharged | UCCEP-000000 / `engine/graph` | **Not done.** `uccep-bindings.json` still carries `UCCEP-F-003` as `disposition: GOVERNED`, `blocking: true`; the finding is still named in the live `certification_ceiling` | **PENDING · NOT BLOCKING** (record act; substance discharged and evidenced) |
| **O-03** | Explicit implementation authorization | **UCCEP-000006** | Discharged by this programme — see Output 5 | **RESOLVED (conditional)** |
| **O-04** | Ratified (non-provisional) certification | external constituent act | No competent authority exists in the corpus (`UCCEP-F-004`; Tier T1 VACANT, `CMG-000001` PROVISIONAL) | **EXTERNAL · NOT BLOCKING** (standing ceiling) |

---

## 2. O-01 — Registration Commit Readiness

**Classification: PENDING · BLOCKING.**

| Measure | Value |
|---|---|
| Working-tree entries | **127** (baseline 120 + 7 from UCCEP-000005) |
| Modified | 75 |
| Untracked | 52 |
| Untracked zones of constitutional significance | `00-CMG/` (entire meta-constitutional zone) · `00-MASTER/UCCEP-000000/` (the constitutional register) · `00-MASTER/UCCEP-000005/` (**the handover package itself**) · 37 `00-BOOK/PORTAL/*` projections · `.github/workflows/uccep-gate.yml` · `.kiro/hooks/uccep-000000.json` |
| Generator changes in the split | `00-BOOK/tools/config.py`, `00-BOOK/tools/ukb.py` (`RECONCILED_SETS`) |
| Gate consequence | `CK-REG-DRIFT` exit **3** — *uncommitted-registration drift, source split from projections*; `G-07` Registry **FAIL** at full tier |
| Aggregate consequence | full-tier aggregate gate **NOT-CERTIFIED**, exit 1, sole blocking failure |
| Owning finding / work package | `UCCEP-F-007` · `WP-UCCEP-005` |
| Provenance | **Pre-dates UCCEP-000005** (115–120 dirty entries at establishment/baseline) |

**Why blocking.** Not because it is a dependency defect — it is not — but because of what it
does to reproducibility of the authorization itself. Under PR-01 Repository Truth is what is
committed. Today the evidence package that justifies authorization, the register that records
it, and the meta-constitutional zone that frames it all exist only in an uncommitted working
tree. An implementation programme launched from that state cannot establish a pre-mutation
baseline it can roll back to, and cannot demonstrate from committed history what it was
authorized against. That is a precondition of controlled implementation, not a nicety.

**Note on `UCCEP-F-007.blocking = false`.** The binding declares this finding non-blocking,
and this programme does not re-open that determination. The classification here is about the
**execution-authorization obligation O-01**, whose measured gate consequence (`CK-REG-DRIFT`
exit 3 → `G-07` FAIL → full-tier aggregate exit 1) is blocking on its own terms. Both
statements are true and consistent: the finding is registered as non-blocking for
certification; the commit act is blocking for clean execution authorization.

**Required act (unchanged from `12` §8.2, restated for the operator).**
1. Review all 127 entries — in particular untracked `00-CMG/` and the `config.py` / `ukb.py` `RECONCILED_SETS` change.
2. Commit source **and** projections **atomically** (REG-AUTO-001: source is never split from projections).
3. Reconcile `MCP-002` §01 to the new HEAD (per MCP-007 §04.B).
4. Re-run the full-tier aggregate gate and confirm `CK-REG-DRIFT` PASS / `G-07` PASS.

## 3. O-02 — Binding Updates

**Classification: PENDING · NOT BLOCKING.**

| Measure | Value |
|---|---|
| Declaration state | `uccep-bindings.json` → `UCCEP-F-003`: `disposition: GOVERNED`, `blocking: true`, `work_package: WP-UCCEP-003` |
| Live ceiling | `uccep.json.certification_ceiling` still names `UCCEP-F-003` |
| Substantive state | **Discharged.** The located root cause (mutual `Depends-On` between `UCOS-ENG-000008` and `UCOS-ENG-000007`) is resolved in generator data; `dependency_cycle = []`; `CK-GRAPH` PASS; `G-08` PASS; the fail-open path now fails closed and was demonstrated failing closed (exit 1 on the negative path) |
| Why still open | UCCEP-000005 correctly declined to edit another programme's declaration |
| Owner | UCCEP-000000 / `engine/graph` (`WP-UCCEP-003`) |

**Why not blocking.** The obligation is a **record act**, not a repair. The condition the
finding describes is measurably absent from the repository; only the disposition field and
the derived ceiling text lag. Nothing in the execution model, the dependency graph or any
gate depends on that field. Left unrecorded, its only effect is a certification ceiling that
names a finding which is factually discharged — a traceability inaccuracy, addressed as
condition **C-2**.

## 4. O-03 — Implementation Authorization

**Classification: RESOLVED (conditional).**

This is the one obligation this programme owns. UCCEP-000005 granted no authorization and
said so. UCCEP-000006 issues it in Output 5 as **EXECUTION AUTHORIZED WITH CONDITIONS**,
with the boundary in Output 6 and the certificate in Output 10. It is *conditional*, not
unconditional, because O-01 remains outstanding and because R-04 caps every verdict in this
corpus at `CERTIFIED-PROVISIONAL`.

## 5. O-04 — Certification Authority Dependency

**Classification: EXTERNAL · NOT BLOCKING.**

| Measure | Value |
|---|---|
| Finding | `UCCEP-F-004` — `disposition: REGISTERED`, `blocking: true` |
| Facts | `CMG-000001` PROVISIONAL · constitutional Tier T1 **VACANT** · no located authority competent to ratify |
| Live effect | `certification_ceiling` caps every verdict at `CERTIFIED-PROVISIONAL`, **including this programme's** |
| Owner | external constituent act — CEP-006 names no existing authority |

**Why not blocking for execution.** It cannot be manufactured; treating it as blocking would
make controlled implementation permanently impossible, which no instrument requires. It is a
**standing ceiling on certification**, not a bar on execution. Its correct handling is
disclosure: the authorization in Output 5 is itself PROVISIONAL and says so on its face.

## 6. Completeness of classification

| Requirement | Result |
|---|---|
| Every obligation in `12` §8.2 classified | **4 / 4** |
| Classifications drawn from the mandated set | **YES** — Pending·Blocking · Pending·Not Blocking · Resolved · External·Not Blocking |
| Blocking obligations | **1** — O-01 |
| Obligations discharged by this programme | **1** — O-03 (conditionally) |
| Obligations this programme may not discharge | **3** — O-01 (operator), O-02 (UCCEP-000000 / `engine/graph`), O-04 (external) |
| New work packages created | **0** |
| Determinations re-opened | **0** |

**Phase 2 determination: ALL OUTSTANDING OBLIGATIONS CLASSIFIED · ONE BLOCKING (O-01).**
