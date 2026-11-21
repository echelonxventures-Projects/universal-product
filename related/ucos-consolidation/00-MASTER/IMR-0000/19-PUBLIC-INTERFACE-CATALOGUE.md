# IMR-0000/19 — PUBLIC INTERFACE CATALOGUE

| Field | Value |
|---|---|
| MISSION | `IMR-0000` — CIOS Platform Foundation |
| ARTIFACT | `19` — Public Interface Catalogue (**deliverable 29**) · directive capability 25 |
| ARTIFACT KIND | Interface catalogue (`CMG-K-05`) |
| NUMERIC CONTRACT | **8 platform ports** `IF-01 … IF-08` (identical to `CIOS-05` §2's public surface) · **12 located interfaces** `IFL-01 … IFL-12` a programme binds **directly** |
| CENTRAL CLAIM | **The platform's total consumable surface is 20 entries: 8 platform ports and 12 located interfaces. Zero ports were created.** A programme binding anything else has bound something the platform does not guarantee. |
| AUTHORITY OF ITS OWN | **NONE.** A port is a declared contract, never an authority; traversing one confers no right (`PR-6`). |
| CONFLICT RULE | `CIOS-05` governs the ports; each located owner governs its own interface; then this artifact. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. WHY THE CATALOGUE EXISTS

`CIOS-05` §2 declares the 8 public ports. `CIOS-05` §5 lists, in prose, the surfaces CIOS does **not** expose and directs a consumer to *"bind the located owner directly"*. Between those two statements there is a gap: nothing says **which** located owner, for **which** question. A programme therefore had to reconstruct that mapping — and the cheapest wrong reconstruction is to route a located mechanism through CIOS, which creates a second interface to a mechanism that already has one (`CIOS-L-09` breach, `CIOS-05` §5).

This catalogue closes the gap by stating both halves in one table: the 8 ports, and the 12 direct bindings. Nothing is added to either.

| ID | Rule | Basis |
|---|---|---|
| `IC-1` | The platform's public surface is **exactly** `IF-01 … IF-08`. It is not extended by this catalogue. | `CIOS-05` §2 |
| `IC-2` | An **internal** port may not be bound by a programme, and may not be promoted. | `CIOS-05` §2; `SR-5` |
| `IC-3` | A capability not on the 8-port surface is bound **directly** from its located owner (`IFL-*`). Routing it through the platform is a `CIOS-L-09` breach. | `CIOS-05` §5 |
| `IC-4` | Every entry declares a **payload class**, never a format, protocol, language, vendor or transport. | `PR-2`; `CIOS-L-22` |
| `IC-5` | Every entry is **fail-closed**. A port that cannot resolve its counterparty fails closed and emits a finding; it never degrades to a partial transfer. | `PR-3`, `PR-8`; `CIOS-L-07` |
| `IC-6` | No entry confers authority. | `PR-6`; `CIOS-INV-12` |
| `IC-7` | Entries change by the stability contract's route (`CEP-009` III.1), never by in-place edit. | `PR-7`; `22` |

---

## 2. THE PLATFORM SURFACE — 8 PORTS

| ID | Port | Subsystem | Engine | Direction | Role | Payload class | Failure mode |
|---|---|---|---|---|---|---|---|
| `IF-01` | **`CIOS-P-01`** | `SS-04` `CIOS-MRS` | `E-01` | **INGRESS** | the **sole** entry point for work | *submission descriptor* — subject, declared scope, declared dependencies, provenance, submitter authority | not accepted |
| `IF-02` | **`CIOS-P-35`** | `SS-14` `CIOS-GI` | `E-18` | **INGRESS** | the **sole** reach into protected or sealed work | *override request* — authority identifier (`CIOS-OR-01` \| `CIOS-OR-02`), target, evidence set, protocol record reference | reject; **an unrecorded override is void** |
| `IF-03` | **`CIOS-P-30`** | `SS-07` `CIOS-ORCH` | `E-15` | EGRESS | handoff to the located Execution Queue | *handoff record* — identity record reference, bound plan epoch, derived priority position | item stays in `CIOS-Q-04`; **never forced** |
| `IF-04` | **`CIOS-P-40`** | `SS-13` `CIOS-EI` | `E-20` | EGRESS | append to Repository Truth | *truth append record* — sealed item reference, terminal state, evidence set | no seal — prefers unsealed truth to false truth |
| `IF-05` | **`CIOS-P-42`** | `SS-13` `CIOS-EI` | `E-21` | EGRESS | traceability emission | *traceability edge* — `id → artifact` binding, canonical home reference | finding + item marked traceability-incomplete; **does not block the seal** (`UCCEP-F-002` bound) |
| `IF-06` | **`CIOS-P-44`** | `SS-12` `CIOS-OBS` | `E-22` | EGRESS | invariant findings | *finding* — invariant identifier, breach description, observed state reference | inability to observe is **itself a finding**; never reports a pass |
| `IF-07` | **`CIOS-P-46`** | `SS-12` `CIOS-OBS` | `E-23` | EGRESS | monotonicity findings | *finding* — epoch pair, certified-set cardinalities, direction | a decrease ⇒ maximum-severity finding |
| `IF-08` | **`CIOS-P-48`** | `SS-12` `CIOS-OBS` | `E-24` | EGRESS | determinism findings | *finding* — replay pair, divergent field set | divergence ⇒ finding; witnessed ordinal **excluded** from comparison |

### 2.1 Surface properties

| Property | Value |
|---|---|
| Public ports | **8** — unchanged from `CIOS-05` §2 |
| Ingress | **2** (`IF-01`, `IF-02`) |
| Egress | **6** (`IF-03 … IF-08`) |
| Egress ports that **mutate** a located artifact | **0** — one hands off, two append, three advise |
| Ports created by this catalogue | **0** |
| Internal ports promoted | **0** |
| Ports conferring authority | **0** |
| Ports naming a format, protocol, language or vendor | **0** |
| Ports with a declared fail-closed mode | **8 / 8** |
| Subsystems exposing a public port | **5 of 17** — `SS-04`, `SS-07`, `SS-12`, `SS-13`, `SS-14` |
| Subsystems exposing **none** | **12 of 17** |

**The asymmetry is deliberate and worth stating plainly:** two ways in, six ways to observe what happened. The platform is designed to be hard to inject into and easy to audit (`CIOS-05` §2.1).

---

## 3. THE LOCATED SURFACE — 12 DIRECT BINDINGS

Every capability a programme needs that is **not** on the 8-port surface. Bind the owner **directly**; do not route it through the platform.

| ID | Capability needed | Bind directly to | Platform subsystem that *declares* the binding | Why not through the platform |
|---|---|---|---|---|
| `IFL-01` | register or discover a **programme** | `uccep.json` `programs[]`; `UCCEP-000006` §1 P-5 home convention | `SS-03` (BINDING-ONLY) | the platform owns no programme register (`REG-01`) |
| `IFL-02` | register an **artifact**; allocate identity | `REG-AUTO-001` transaction `T`; `artifacts.json`; `id-ledger.json`; `00-BOOK/tools/` | `SS-02` | the platform **mints nothing** (`CIOS-L-14`) |
| `IFL-03` | read **portfolio / programme roll-up** | `control-tower.json`; `STATUS-001` | `SS-03`, `SS-10` | derived view, located owner (`REG-03`) |
| `IFL-04` | resolve **canonical home / owner**; read closure truth | `UAKOS-CLOSURE-002` `closure.json` + home register | `SS-09` | the platform resolves at admission but owns no register (`RC-04`, `RC-05`) |
| `IFL-05` | **dispatch**; evaluate READY; form batches; item states; quality gates | `IEC-001` `03`, `04`, `05`, `06`, `08`; C5, C7, C11 (EC-3 lane) | `SS-07` | the platform relinquishes control at `IF-03` (`CIOS-01` I.4) |
| `IFL-06` | **backlog, waves, order, critical path, readiness matrix** | `IMG-001` `03`–`09` | `SS-05`, `SS-06` | `IMG-001` is the sole authority (`CIOS-01` VII.2) |
| `IFL-07` | **twin / signals** | `twin.json`, `signals.json`; `UMB-002`; `ukbx.py twin` | `SS-10` (BINDING-ONLY) | derived state, no new persistence (`DT-1`, `DT-2`) |
| `IFL-08` | **checkpoint / session recovery** | `MCP-007` §01, §03, §04.B; `00-MASTER/CHECKPOINTS/`; `MCP-002`; `MCS-000` | `SS-11` (BINDING-ONLY) | one checkpoint store, located (`CF-2`) |
| `IFL-09` | **validation execution** | `CEP-004`; `engine/validation`; `verify.sh`; `uccep.json` `checks`; `G-10` | `SS-15` | a self-check is not a validation (`VR-04`) |
| `IFL-10` | **certification** | `CEP-005`; `certification.json`; EC-3 gate; `G-11`; `engine/certification` | `SS-16` (BINDING-ONLY) | **CIOS certifies nothing** (`CIOS-16` §1) |
| `IFL-11` | **change / evolution / amendment** | `CEP-009` Art III, III.1, IV.3, VI, XVI, XXIV; `UCI-001`; `change-ledger.json` | `SS-17` (BINDING-ONLY) | the platform owns no evolution model (`CIOS-01` VIII.1) |
| `IFL-12` | **constitutional gate verdicts** | `UCCEP-000000` `G-01 … G-14`; `uccep-bindings.json`; `CK-*` | `SS-14`, `SS-15` | the platform holds no gate authority (`CIOS-01` I.6) |

| Property | Value |
|---|---|
| Located interfaces catalogued | **12** |
| Located interfaces re-exposed through a platform port | **0** |
| Located interfaces the platform re-implements | **0** |
| Capabilities in `CIOS-05` §5's non-exposure list left uncatalogued | **0** |
| Freeze / seal interface | **not catalogued** — `CEP-007` freeze is **unavailable** (`GD-10`, `CIOS-GAP-13`); a programme cannot bind it |

---

## 4. THE TOTAL CONSUMABLE SURFACE

| Class | Count |
|---|---|
| Platform ports (`IF-*`) | **8** |
| Located interfaces (`IFL-*`) | **12** |
| **Total binding entries** | **20** |
| Entries created by `IMR-0000` | **0** — 8 pre-exist in `CIOS-05`; 12 pre-exist in their located owners |
| Entries a programme may not bind | all **40** internal ports (`CIOS-05` §4) |
| Unavailable capability recorded | **1** — freeze/seal |

### 4.1 The consumption rule

A future programme's obligation, in one sentence: **bind an `IF-*` for work entering or leaving the platform, and an `IFL-*` for everything else — and never construct a third path.** A third path is, by construction, either a bypass of a located gate (`CEP-001` LAW-5) or a second interface to a mechanism that has one (`CIOS-L-09`).

---

## 5. WHAT THIS CATALOGUE DOES NOT DO

| Not done | Located owner / reason |
|---|---|
| Create, alter, promote or deprecate a port | `CIOS-05`; `IC-1`, `IC-2`; `PG-02` |
| Specify a wire format, protocol, transport, schema language or serialization | `PR-2`; `CIOS-L-22` |
| Confer authority on any entry | `PR-6` |
| Re-expose a located interface through the platform | `IC-3`; `CIOS-05` §5 |
| Guarantee an internal port to any consumer | `CIOS-05` §2 |
| Catalogue a freeze or seal interface | `CEP-007` — unavailable |
| Change an entry in place | `IC-7`; `PR-7`; route is `CEP-009` III.1 |

---

## AUTHORITY BOUNDARY (MANDATORY)

This catalogue enumerates a surface it does not own. **It creates no port, alters none, promotes none and confers authority on none.** Eight entries are `CIOS-05`'s public ports, unchanged; twelve are located interfaces bound directly from their own owners. No format, protocol or transport is named. Freeze and seal are recorded as unavailable and are not catalogued. Every owner named is located in an instrument existing independently at `b26c5bb`. Where this catalogue and a located canonical instrument disagree, **the located instrument governs and this catalogue SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `IMR-0000/19` · PROVISIONAL · ADDITIVE · DESIGN-ONLY · AUTHORITY-NEUTRAL**
