# IMR-003A — CONTINUOUS IMPLEMENTATION OPERATING SYSTEM (CIOS) · MISSION INDEX

| Field | Value |
|---|---|
| MISSION | `IMR-003A` — CIOS Constitution & Architecture |
| WORK PACKAGE | `WP-IMR-003A` |
| SUBJECT TOKEN | `CIOS` |
| BASELINE | `b26c5bb66c37717fe4eb96552bad4b9d8b74d890` · branch `programme/evo-usis-005` |
| STANDING | **PROVISIONAL** (`CMG-L-12`) · Tier T1 **VACANT** (`VAC-01`) · **not** ratified · **not** frozen |
| AUTHORITY | **NONE of its own.** Composition instrument. Every mechanism is a pointer to a located owner. |
| SUPREMACY | **NOT CONFERRED** — deferred behind `CIOS-G-01` and `CIOS-G-02` |
| EXECUTION | **NOT AUTHORIZED** — gated on `GG-3`, `GG-4`, `GG-6`, `IAC-001 B+C`, `CIOS-G-01 … G-07` |
| RECOVERED AND COMPLETED BY | `IMR-003A-R1` — see `00-MASTER/IMR-003A-R1/` |

> **What CIOS is.** A composition instrument that constitutes implementation as a **perpetual operating system** rather than a finite project. It adds exactly one thing the repository lacks: a **law of continuity** — a formal separation between the plane on which future work is prepared and the plane on which present work executes, such that neither can block the other.
>
> **What CIOS is not.** It is not an authority. It legislates no mechanism, owns no registry, no gate, no identifier space and no concern. It subordinates nothing and supersedes nothing. Where CIOS and a located canonical instrument conflict, **the located instrument governs and CIOS SHALL be corrected**.

---

## Mission history

| Event | Record |
|---|---|
| Registered and admitted | `00-CIOS-MISSION-REGISTRATION-RECORD.md` — 22-artifact output register declared |
| **Terminated after 2 of 22 outputs** | `CIOS-01` delivered; outputs 2–20 + bindings + index absent; 12 dangling forward references |
| Recovered and completed | `IMR-003A-R1` (Phases 1–6). Additive only: the two recovered artifacts are **byte-identical**, verified by digest (`r1_verify.py` `V-01`) |

---

## Artifact index

| # | Artifact | Subject |
|---|---|---|
| — | [`00-CIOS-MISSION-REGISTRATION-RECORD.md`](00-CIOS-MISSION-REGISTRATION-RECORD.md) | registration, work package, `AC-1…AC-12`, namespace allocation, canonical bindings |
| 1 | [`01-CIOS-CONSTITUTION.md`](01-CIOS-CONSTITUTION.md) | 24 laws · 12 invariants · 4 planes · 4 partitions · epoch model · Art X.1 closure test |
| 2 | [`02-CIOS-OPERATING-MODEL.md`](02-CIOS-OPERATING-MODEL.md) | plane detail · **write scopes** (`WS-1…WS-9`) · non-blocking proof · degradation semantics |
| 3 | [`03-CIOS-ENGINE-ARCHITECTURE.md`](03-CIOS-ENGINE-ARCHITECTURE.md) | the **24 engines** `CIOS-E-01…E-24` · binding classes · Art VII.3 mapping |
| 4 | [`04-CIOS-ENGINE-RESPONSIBILITIES.md`](04-CIOS-ENGINE-RESPONSIBILITIES.md) | per-engine OWNS / CONSUMES / PRODUCES / **EXCLUDES** / FAIL |
| 5 | [`05-CIOS-ENGINE-INTERFACES.md`](05-CIOS-ENGINE-INTERFACES.md) | **48 ports** · the **8-port public surface** — *the artifact downstream missions consume* |
| 6 | [`06-CIOS-ENGINE-DEPENDENCIES.md`](06-CIOS-ENGINE-DEPENDENCIES.md) | 25 `DERIVES` edges · acyclicity proof · the absent back-edge |
| 7 | [`07-CIOS-LIFECYCLE-MODEL.md`](07-CIOS-LIFECYCLE-MODEL.md) | the **24 admission stages** `CIOS-S-01…S-24` · all 14 located gates bound |
| 8 | [`08-CIOS-IDENTITY-MODEL.md`](08-CIOS-IDENTITY-MODEL.md) | the **Canonical Submission Object** — 22 fields `CIOS-ID-01…ID-22` |
| 9 | [`09-CIOS-QUEUE-MODEL.md`](09-CIOS-QUEUE-MODEL.md) | 4 queues `CIOS-Q-01…Q-04`, strictly upstream of the located Execution Queue |
| 10 | [`10-CIOS-SCHEDULING-MODEL.md`](10-CIOS-SCHEDULING-MODEL.md) | priority key vector `CIOS-K-01…K-08` · wave successor function · independent clocks |
| 11 | [`11-CIOS-IMPLEMENTATION-PROTECTION-MODEL.md`](11-CIOS-IMPLEMENTATION-PROTECTION-MODEL.md) | 10 interruption classes · quiesce protocol · `CIOS-OR-01`, `CIOS-OR-02` |
| 12 | [`12-CIOS-CONTINUOUS-EVOLUTION-MODEL.md`](12-CIOS-CONTINUOUS-EVOLUTION-MODEL.md) | future-only realignment · epoch discipline · monotone progress |
| 13 | [`13-CIOS-REPOSITORY-INTEGRATION-MODEL.md`](13-CIOS-REPOSITORY-INTEGRATION-MODEL.md) | registry contracts (read-only) · write confinement · zone matrix |
| 14 | [`14-CIOS-GOVERNANCE-INTEGRATION-MODEL.md`](14-CIOS-GOVERNANCE-INTEGRATION-MODEL.md) | **33 governance rules** `GR-01…GR-33` · inherited findings as bounds |
| 15 | [`15-CIOS-VALIDATION-INTEGRATION-MODEL.md`](15-CIOS-VALIDATION-INTEGRATION-MODEL.md) | 14 validation rules · three validation surfaces · 4 self-checks |
| 16 | [`16-CIOS-CERTIFICATION-INTEGRATION-MODEL.md`](16-CIOS-CERTIFICATION-INTEGRATION-MODEL.md) | 12 certification rules · the certification ceiling |
| 17 | [`17-CIOS-TRACEABILITY-MODEL.md`](17-CIOS-TRACEABILITY-MODEL.md) | 9 traceability rules · the **`UCCEP-F-002` bound** (§5) |
| 18 | [`18-CIOS-REPOSITORY-IMPACT-ASSESSMENT.md`](18-CIOS-REPOSITORY-IMPACT-ASSESSMENT.md) | `CEP-009` III.1 impact assessment · 10 risks |
| 19 | [`19-CIOS-GAP-ANALYSIS.md`](19-CIOS-GAP-ANALYSIS.md) | `CIOS-G-01…G-07` · `CIOS-GAP-01…GAP-14` · overlap deferral record |
| 20 | [`20-CIOS-CONSTITUTIONAL-VERIFICATION.md`](20-CIOS-CONSTITUTIONAL-VERIFICATION.md) | Art X.1 closure verification · `AC-1…AC-12` · what is **not** verified |
| — | [`cios-bindings.json`](cios-bindings.json) | machine binding declaration — **DATA ONLY, AUTHORITY NONE**; the sole lawful extension surface |
| — | `README.md` | this index |

---

## Reading order

| If you want to | Read |
|---|---|
| understand why CIOS exists | `01` PREAMBLE P.1–P.6 |
| **implement against CIOS** | **`05`** (public surface), then `03`, `04`, `07`, `08` |
| know what CIOS may and may not do | `01` Art I, VII, VIII; every artifact's Authority Boundary |
| know what is still blocked | `19` §1, §4 |
| know what CIOS does **not** claim | `20` §5; `16` §5 |
| extend CIOS | `cios-bindings.json` + `01` VIII.2 + `12` §6.1 |

---

## The numbers

Fixed by `CIOS-01` Art X.1 and Art II–V; machine-verified by `r1_verify.py`.

| Element | Count | Element | Count |
|---|---|---|---|
| Planes `CIOS-PL-*` | 4 | Stages `CIOS-S-*` | 24 |
| Partitions `CIOS-PT-*` | 4 | Identity fields `CIOS-ID-*` | 22 |
| Laws `CIOS-L-*` | 24 | Queues `CIOS-Q-*` | 4 |
| Invariants `CIOS-INV-*` | 12 | Key elements `CIOS-K-*` | 8 |
| Engines `CIOS-E-*` | 24 | Override authorities `CIOS-OR-*` | 2 |
| Ports `CIOS-P-*` | 48 (8 public) | Interruption classes `CIOS-IC-*` | 10 |
| Undischarged gates `CIOS-G-*` | 7 | Gaps `CIOS-GAP-*` | 14 |

---

## Standing limits — read before relying on anything here

| Limit | Basis |
|---|---|
| Every determination is **PROVISIONAL** | `CMG-L-12`; T1 VACANT (`VAC-01`, `CMG-OQ-02`, `UCCEP-F-004`) |
| CIOS is **not validated** under `CEP-004` | a self-check is not a validation (`15` `VR-04`) |
| CIOS is **not certified** active under `CEP-005` | ceiling `CERTIFIED-PROVISIONAL` (`16` §1) |
| CIOS is **not ratified** under `CEP-006` | no competent authority exists; no programme may self-ratify |
| CIOS is **not frozen** under `CEP-007`, and **cannot be** | ineligible on three limbs; an attempt would be **void** (`GD-10`; `19` `CIOS-GAP-13`) |
| `CIOS-PT-01` SEALED is **not** a `CEP-007` freeze state | `11` §2.1 |
| CIOS **claims no traceability closure** | `UCCEP-F-002` (`17` §5) |
| `CIOS-INV-05` is **not** machine-enforced corpus-wide | `UCCEP-F-003` (`06` §4.3) |
| CIOS registration is **unwitnessed by any commit** | `R1-F-001` — this mission home is untracked at `b26c5bb` (`19` `CIOS-GAP-14`) |
| CIOS **discharges no gate and no finding** | `01` IX.4; `19` §1 |
| CIOS **authorizes no execution** | every artifact's Authority Boundary |

---

## Verification

```
python3 ../IMR-003A-R1/r1_verify.py          # 162 checks over CIOS's own declaration
python3 ../IMR-003A-R1/r1_verify.py --json   # machine-readable result
```

Scope: CIOS's own declaration only — an `AC-4` self-check. **Not** a `CEP-004` validation; confers no status; discharges no located gate or finding.

---

**Every authority named in this mission is located in an instrument that exists independently at `b26c5bb`. This mission confers no authority on itself and authorizes no execution.**
