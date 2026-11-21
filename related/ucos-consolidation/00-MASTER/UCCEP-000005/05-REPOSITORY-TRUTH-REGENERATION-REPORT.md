# Output 5 — Repository Truth Regeneration Report

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000005` · PHASES 3 and 5 |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| REGENERATION OWNER | `REG-AUTO-001` — `00-BOOK/tools/register.sh` + `ukb.py` + `ukbx.py` |
| GOVERNING LAW APPLIED | *Artifact Creation = Artifact Registration*; source is never split from projections |

---

## 1. Regeneration was performed by the located owner only

No parallel regeneration path, no second generator, no hand-edited register. The single
idempotent transaction `00-BOOK/tools/register.sh` was invoked; all ten phases succeeded
and the transaction sealed. Log: `evidence/post/register-transaction.log`.

## 2. Repository Truth after regeneration

| Register | Content | sha256 |
|---|---|---|
| `00-BOOK/DATA/artifacts.json` | 1199 artifacts | `aeb65199ae9059f2a78b56c4c06b3df64344f7108af6943ed26719c0cb3a4411` |
| `00-BOOK/DATA/relationships.json` | 12841 edges | `533c757006b81457aac360c24aecb35d66de84aeba2ec1a943e420bf2271253d` |
| `00-BOOK/DATA/volumes.json` | 25 volumes | `ea949948c5a079f72dfd9654ab38819166662f4c68e314c2251b8d895c6cc567` |
| `00-BOOK/DATA/id-ledger.json` | identity authority | `be97eb9f0e7152578d85a29f433a2cc284b3d9217231085052ec7efc5c057590` **(unchanged)** |
| `00-BOOK/DATA/control-tower.json` | computed dimensions | `a824c6fd435799ac03c6d2595b01df0f22026d435ba846145910718c41c53a5d` |
| `00-BOOK/DATA/change-ledger.json` | 1353 change events | `53119ddb53bef5d3dae39a3c337cabb110bea1a4e4053e82f05eb56cc7a16601` |
| `00-BOOK/DATA/certification.json` | 10/10 domain evidence | `636ba235a425eaab0e47ca87b5a9c766cf23f3fd097b79175975c5966dd48151` |

## 3. Registries and indexes refreshed

| Register | Owner | State |
|---|---|---|
| `UNIVERSAL-ARTIFACT-REGISTRY.md` | `ukb build` | refreshed · 1199 artifacts |
| `UNIVERSAL-PAGE-REGISTRY.md` | `ukb build` | refreshed |
| `VOLUME-REGISTRY.md` | `ukb build` | refreshed · 25 volumes |
| `KNOWLEDGE-GRAPH-REGISTRY.md` | `ukb build` | refreshed · 12841 edges |
| `CERTIFICATION-REGISTRY.md` | `ukbx certify` | CERTIFIED 10/10 |
| `CHANGE-VERSION-LINEAGE-REGISTRY.md` | `ukb build` | refreshed |
| `PROGRAM-CONTROL-TOWER.md` | `ukbx twin` | refreshed |
| `PORTAL/index.md` + portal pages | `ukbx portal` | refreshed · 4 ENG pages changed |

## 4. Identity and sticky-identifier preservation

| Guarantee | Proof |
|---|---|
| No identifier allocated | `id-ledger.json` byte-identical before and after regeneration |
| No identifier renumbered | `UCOS-ENG-000001…000009` all bound to the same paths as at baseline |
| No identifier released | append-only ledger unchanged |
| No page reallocated | `UNIVERSAL-PAGE-REGISTRY` regenerated from the same ledger |
| Artifact count stable | 1199 → 1199 |
| Native ids stable | `ENG-000/001/002/003/004/005`, `ENG-GOV-001/002/003` |

**A dependency-ordering correction changed edges only. It changed no identity.**

## 5. Enforcement after regeneration

`ukb enforce` (post-registration, audit run #513):

| Measure | Value |
|---|---|
| Eligible on-disk artifacts | 1199 |
| Registered in registers | 1199 |
| Unregistered eligible | **0** |
| Unclassified (OTHER/MISC) | **0** (GATED) |
| Reconciled sets declared | 1 (`CMG`) |
| Reconciled-set drift | **0** (GATED) |
| Invalid (unreadable/empty) | **0** |

**ENFORCEMENT PASSED.**

## 6. Regeneration determinism

A second `ukb build` over the already-regenerated repository produced **byte-identical**
`artifacts.json`, `relationships.json`, `volumes.json` and `id-ledger.json`. The
regeneration is a fixed point, so Repository Truth is reproducible rather than
incidental. Evidence: `evidence/post/T-3-regeneration-determinism.txt`.

## 7. Derived-intelligence re-derivation (T-3)

| Derived register | Owner | Result |
|---|---|---|
| `UCOS-RIE-DEPENDENCY-GRAPH.json` | `intelligence.rie` | derives identically on repeated derivation |
| `UCOS-RIE-EXECUTION-FRONTIER.json` (critical path) | `intelligence.rie` | derives identically |
| `UCOS-RIE-MODEL/PROGRESS/HEALTH/SNAPSHOT/DIGITAL-TWIN/CAPABILITY-CATALOG/AEOS-READINESS` | `intelligence.rie` | derive identically |
| `UCOS-IMP-BASELINE-001.rib.json` | `intelligence.rie` | derives identically |

`intelligence.rie verify` → `{"deterministic": true, "mismatches": []}` over all 10
outputs, on every run.

**What this proves, precisely.** `RepositoryIntelligenceEngine.verify_determinism()`
derives the full output set **twice in memory** and compares the canonical JSON
byte-for-byte (`intelligence/rie/engine.py`). It therefore proves *identical repository
state ⇒ identical outputs*. It does **not** compare against the committed files on disk,
and this programme did not run `rie build`, so the ten `intelligence/*.json` files are
unchanged by UCCEP-000005 — their working-tree modifications are pre-existing drift
present in `evidence/baseline/worktree.txt`.

The report also emits `model_content_hash`, which is a content hash of the *current*
repository model. It was `6b2748c40f6c4e01b70d98bbc4870cc37765ccf3e920b44c53d347810723be01`
when `evidence/post/T-3-rie-determinism.json` was captured and moves whenever repository
content changes — including when this programme wrote its own outputs under
`00-MASTER/UCCEP-000005/`. **It is a content fingerprint, not a stability claim**; the
stability claim is `deterministic: true`, which holds on every run. Consecutive runs
during final verification returned an identical hash to each other, confirming
within-state stability.

**Global Implementation Graph and Implementation State Registry.** Both
`02-MASTER/UCOS-COMP-000000-GLOBAL-IMPLEMENTATION-GRAPH-DETERMINATION.md` and
`02-MASTER/UCOS-COMP-000000-IMPLEMENTATION-STATE-REGISTRY.md` contain **zero**
`ENG-00N` references. Their statements do not depend on the corrected ordering, so
re-derivation confirms them unchanged, and neither was modified — the honest result, and
the one DP-03 requires.

## 8. Outstanding registration act (not this programme's to perform)

The regenerated Repository Truth is **not yet committed**. `CK-REG-DRIFT` therefore
reports exit 3 — *"uncommitted-registration drift — source split from projections"*.
This condition **pre-dates** UCCEP-000005 (recorded at baseline as `UCCEP-F-007`,
evidenced by `register.sh --guard` exit 3 before this programme began) and is owned by
`WP-UCCEP-005` (repository operator). Committing is an operator decision that this
programme does not take unilaterally.

---

**REPOSITORY TRUTH REGENERATED · CERTIFIED 10/10 · DETERMINISTIC · IDENTITY PRESERVED**
