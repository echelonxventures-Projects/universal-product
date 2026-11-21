# MCP-004 — MASTER DECISIONS (UCOS Ω∞)

| Field | Value |
|-------|-------|
| ARTIFACT ID | MCP-004 |
| ARTIFACT | Master Decisions — Architectural & Program Decision Index of UCOS Ω∞ |
| CLASSIFICATION | MCS COMPONENT 4 — decision register index; append-only |
| STATUS | ACTIVE · LIVING |
| AUTHORITY | **NONE — DERIVED TRUTH.** MCS **indexes** decisions held in their authoritative registers; it authors none. |
| ANSWERS | *Why is it this way — what was decided, why, and is it still in force?* |
| PART OF | Master Context System (`00-MASTER/`), governed by `MCS-000` |
| BASELINE | 2026-07-18 · branch `governance-reconciliation` · HEAD `5874ede` |
| CONFLICT RULE | Where any statement conflicts with a higher frozen or governing instrument, the higher instrument governs. |

> **Scope.** MCP-004 is an **index** of ratified/recorded decisions, each pointing to its authoritative register. *Never revisit a recorded decision unless a defect is proven* (the only backward transition is a defect-driven REOPEN — `MCS-000 §05`). New decisions are appended to their authoritative register **first**, then indexed here.

**Authoritative registers indexed by this component:**
- Constitutional: `02-MASTER/UCOS-Ω∞-CONSTITUTIONAL-DECISION-REGISTER.md`
- Implementation/technology: `adr/` (e.g. `adr/0001-foundation-technology-stack.md`)
- Program/governance/EC: `02-MASTER/UCOS-GOV-00N-*`, `02-MASTER/EC-3-*`, `02-MASTER/EC2-*`, Program Tracker §6

> **Disposition obligation (CEP-002 Article 28).** Every decision indexed here SHALL carry exactly one constitutional disposition — IMPLEMENTED, REPRESENTED BY AN EXISTING CANONICAL CAPABILITY, REGISTERED AS AN IMPLEMENTATION WORK PACKAGE, REJECTED WITH CONSTITUTIONAL JUSTIFICATION, or SUPERSEDED — supported by evidence that resolves in the repository. The machine-readable disposition overlay is `00-MASTER/UCDA-000001/ucda-decisions.json`; it is enforced by the **Implementation Evidence Gate** (`make ucda-gate`, and `G-14` of `00-MASTER/UCCEP-000000/uccep-bindings.json`). A decision that appears only in conversation is **not recorded** (Art 28.4, 28.5) and closes the gate.

---

## SECTION 01 — CONSTITUTIONAL DECISIONS (source: Constitutional Decision Register)

| ID | Title | Decision (summary) | Status | Supersedes |
|----|-------|--------------------|--------|-----------|
| DR-RAT-01 | Status of BEING | BEING is axiom-only (non-layer); layered ontology begins at EXISTENCE | ADJUDICATED (non-final) | — |
| DR-RAT-02 | Root ontology arity | 4-primitive root (EXISTENCE→RELATIONSHIP→TRANSFORMATION beneath BEING axiom) | ADJUDICATED (non-final) | 5-primitive variant (SUP-07) |
| DR-RAT-03 | SPACE-TIME placement | SPACE-TIME is a coordinate axis; root law Ω-LAW-02 retired-as-root | ADJUDICATED (non-final) | — |
| DR-RAT-04 | Canonical invariant set | Layered coexistence (INV02 ordering / INV01 concurring / INV03 integrity) | ADJUDICATED (non-final; residual ordering open) | — |
| DR-RAT-05 | Sovereignty origin | Two-level: invariants *constrain* sovereignty; sovereignty *sources* authority | ADJUDICATED (non-final) | — |
| DR-RAT-06 | Authority-stack model | Flow model (AUTH-08) canonical; SRC-08 layered stack advisory-subordinate | ADJUDICATED (non-final) | — |
| DR-RAT-07 | Evolution gate | Tiered: routine→governance; structural→ratification | ADJUDICATED (non-final) | — |
| DR-RAT-08 | Canonical law-ID scheme | `LAW Ω∞` canonical + concordance for legacy schemes | ADJUDICATED (non-final) | — |
| DR-RAT-09 | `LAW Ω∞` namespace collision | Renumber SRC-07 15-law set out of `LAW Ω∞` (alias) | ADJUDICATED (non-final) | — |
| DR-RAT-10 | Domain/family namespacing | DOMAIN-tag commerce (`LAW-COMM`); family prefixes as sub-namespaces | ADJUDICATED (non-final) | — |
| **DR-RAT-11** | **Document supremacy + ratification authority (KEYSTONE)** | SRC-02 senior *pro tempore*; ratification body must be constituted out-of-corpus | **BLOCKED** | — |

> **Keystone note.** All ten ADJUDICATED decisions are **non-final** and cannot advance to ratification while DR-RAT-11 is BLOCKED. Closing RAT-11 requires an out-of-corpus stakeholder act (constitute a ratification body: membership, quorum, amendment procedure). This is the single largest gate to constitutional finality and is **outside** engineering/CIOA authority. Tracked as MEP-09 (MCP-003) and blocker B-RAT-11 (MCP-002).

---

## SECTION 02 — IMPLEMENTATION & PROGRAM DECISIONS (source: `adr/`, Program Tracker §6, EC/GOV determinations)

| ID | Title | Decision | Status |
|----|-------|----------|--------|
| ADR-0001 | Foundation technology stack | Baseline stack for EC-1/EC-2 realization (`adr/0001-foundation-technology-stack.md`) | ACTIVE |
| IMPDEC-001 | Governance-before-implementation | Establish IMP-000 foundation before any implementation artifact | RECORDED |
| IMPDEC-002 | Provisional encoding | Encode constitutional positions as provisional/versioned, never hard-coded | RECORDED |
| IMPDEC-003 | Dependency sequencing | Sequence per MIP §6 dependency model; IMP-009/010/011 parallel | RECORDED |
| IMPDEC-004 | Gates finality-only | Treat EC-1…EC-6 as finality-only, not build-blocking | RECORDED |
| IMPDEC-005 | Defer vendor choices | Defer specific vendor/framework selections to per-artifact ADRs | RECORDED |
| GOV-001…006 | Corpus authority, traceability, readiness, execution authorization, repository governance reconciliation/correction | Governance-reconciliation determinations | ACTIVE |
| EC-2 CLOSURE | EC-2 platform program closure | PROGRAM CLOSED WITH OBSERVATIONS (engineering-execution scope) | ACTIVE |
| EC-3 CHARTER / AUTH / AP-1 / AP-2 | Bands 10–13 realization lane | Lane CHARTERED → OPEN → executor designated → Band 10 ADMITTED | ACTIVE |
| MCS-DEC-001 | Master Context System establishment | Decompose monolithic MCP-001 into MCS (`00-MASTER/`, MCP-001…007); operational memory, AUTHORITY=NONE; entry path preserved | RECORDED (Mission MCP-002) |
| MCS-DEC-002 | Repository state reconciliation (UCOS-RECON-001) | Canonical repo truth = working-tree projection (436 artifacts/6,021 pages); validate+enforce PASS, 0 drift. **Decision: CANONICAL STATE ESTABLISHED WITH WARNINGS.** 4 conflicts registered (RECON-C1 `00-MASTER` mis-registered as corpus; RECON-C2 canonical projection uncommitted; RECON-C3 MCP-005 stale scale; RECON-C4 CI signals stale). See `00-MASTER/UCOS-RECON-001-REPOSITORY-STATE-RECONCILIATION.md` | RECORDED (Mission UCOS-RECON-001) |
| MCS-DEC-003 | Operational-Memory / Corpus separation (UCOS-RECON-C1) | Resolve RECON-C1: exclude `00-MASTER/` + root redirect from corpus discovery (`config.py EXCLUDE_DIR_PREFIXES`); 14 sticky IDs retained-but-retired (append-only preserved); 436→423 registered; validate+enforce PASS; idempotent. **RECON-C1 CLOSED; Repository Management FROZEN; Repository Management Foundation COMPLETE.** See `00-MASTER/UCOS-RECON-C1-OPERATIONAL-MEMORY-EXCLUSION.md` | RECORDED (Mission UCOS-RECON-C1) |
| MCS-DEC-004 | Universal Capability Implementation Contract (UCOS-EXEC-002) | Adopt `UCIC-001` as the single deterministic 15-stage lifecycle every future capability follows (gates READY_TO_IMPLEMENT→IMPLEMENTED→VALIDATED→CERTIFIED→READY_TO_COMMIT→READY_FOR_PRODUCTION); composes CIOA/CCE/GOV-002/TRACK-001; AUTHORITY=NONE. **Governance, Repository Management, and Execution Methodology FROZEN.** See `00-MASTER/UCIC-001-UNIVERSAL-CAPABILITY-IMPLEMENTATION-CONTRACT.md` | RECORDED (Mission UCOS-EXEC-002) |
| **CDAF-001** | **Constitutional Decision Assimilation Framework (CEP-002-AMD-002)** | Amend the located governance constitution — **no new instrument** — to add `CEP-002` **Article 28**: (i) **no constitutionally agreed decision may remain only in conversation history** (28.4–28.7); (ii) the mandatory nine-stage decision lifecycle DISCUSSION → CONSTITUTIONAL AGREEMENT → DECISION REGISTRATION → REPOSITORY MAPPING → IMPLEMENTATION → VALIDATION → CERTIFICATION → REPOSITORY TRUTH UPDATE → CLOSURE (28.8–28.12); (iii) the **closed five-member disposition set** — IMPLEMENTED · REPRESENTED BY AN EXISTING CANONICAL CAPABILITY · REGISTERED AS AN IMPLEMENTATION WORK PACKAGE · REJECTED WITH CONSTITUTIONAL JUSTIFICATION · SUPERSEDED (28.13–28.16); (iv) the **Implementation Evidence Gate** blocking any successor implementation programme or architectural work while any ratified decision is undispositioned (28.17–28.21). Machine-readable disposition overlay at `00-MASTER/UCDA-000001/ucda-decisions.json` + engine `ucda_engine.py`; gate bound in the located aggregate gate declaration as **G-14 / CK-DECISION-EVIDENCE** and as **PROGRAM-000016**. CEP-002 version 1.1 → 1.2. Trigger: **CF-01** (`00-MASTER/UAKOS-CLOSURE-006/13-CONSTITUTIONAL-FINDINGS-REGISTER.md`). Recorded in its authoritative register (CEP-002 Article 28 and its AMENDMENT RECORD) before this index entry. | RECORDED · **ENFORCED** (gate OPEN) |

---

## SECTION 03 — IMMUTABLE vs REVISABLE

| Class | Members | Rule |
|-------|---------|------|
| **Immutable (pending ratification)** | DR-RAT-01…10 once ratified | Become immutable only upon ratification (blocked by DR-RAT-11) |
| **Immutable (frozen)** | EC-2 CLOSURE scope; EC-1 certification | Frozen; changes are additive-only elsewhere |
| **Revisable by supersession** | IMPDEC-*, ADR-*, GOV-*, MCS-DEC-* | Never edited in place; superseded by a new appended entry citing the prior ID |
| **Blocked** | DR-RAT-11 | Requires out-of-corpus act; kept honestly BLOCKED |

---

## SECTION 04 — REVIEW HISTORY / SUPERSESSIONS

| Decision | Superseded / Reviewed | By | Note |
|----------|-----------------------|----|------|
| 5-primitive root variant (SUP-07) | Superseded | DR-RAT-02 | 4-primitive root adopted |
| Ω-LAW-02 as root | Retired-as-root | DR-RAT-03 | SPACE-TIME reclassified as coordinate axis |
| SRC-08 layered authority stack | Demoted to advisory-subordinate | DR-RAT-06 | AUTH-08 flow model canonical |
| SRC-07 15-law set in `LAW Ω∞` | Renumbered (alias) | DR-RAT-09 | namespace collision resolved |

*No MCS decision has yet been superseded. Append here whenever a decision is reviewed or replaced.*

---

## SECTION 05 — CHANGE LOG (MCP-004 only)

| Date | Change | Reason |
|------|--------|--------|
| 2026-07-18 | MCP-004 established as MCS component 4 (constitutional + implementation/program decision index); added MCS-DEC-001 | Mission MCP-002 decomposition (migrated from root §04) |
| 2026-07-20 | Indexed **EC3-B13-G01 = EC-3 AP-5 Band-13 (Infrastructure) admission determination** (`02-MASTER/EC-3-AP-5-BAND-13-ADMISSION-DETERMINATION.md`): governance-only (AUTHORITY = NONE) per-band admission decision — **BAND 13 ADMITTED · AP-5 SATISFIED · MEP-04 OPEN** (AP5-1…AP5-10 all PASS; the analog of AP-2/AP-3/AP-4). Recorded in its authoritative register (the determination artifact itself) + MCP-002/003/006. Non-blocking observations OBS-C (test-dir lint) + OBS-D (DR-RAT-11 finality) carried. Decision authorizes queue admission only; realization DEFERRED pending explicit authorization. | EC3-B13-G01 — MEP-04 admission (AP-5) |

| 2026-07-20 | Indexed **EC3-B13-P01 = Band-13 (Infrastructure) Master Program Charter & MEP-04 Implementation Roadmap** (`02-MASTER/EC-3-B13-P01-BAND-13-INFRASTRUCTURE-MASTER-PROGRAM-CHARTER.md`): program-governance / planning-only (AUTHORITY = NONE) decision fixing the complete MEP-04 realization execution contract — WBS over the frozen 16-leaf-meta-class inventory; recommended 12-unit concern-granularity spine (U01…U12) + construct-granularity alternative; implementation order + dependency gates; founding DAG; validation/certification(BRC-1…8+BCC-1…8)/freeze(FP-1…6+FE-1…5)/completion/transition strategies. **Key deferred decision: the exact intra-band unit granularity (concern vs construct) and the intra-band order are NOT fixed by the charter — they are CIOA-derived at UCIC-001 Stage 1–3 (CIOA-LAW-004 dependency-derived / LAW-010 sequence-not-authorization); the charter records the recommended default and the invariant construct-level founding DAG that governs correctness under any granularity.** Recorded in its authoritative register (the charter artifact itself) + MCP-002/003/006. Discharges the previously-deferred "Band-13 Program Charter" obligation. Decision plans realization only; EC3-B13-U01 realization DEFERRED pending explicit authorization. | EC3-B13-P01 — MEP-04 Master Program Charter (planning-only) |

*Append-only. Index a decision here only after it is recorded in its authoritative register.*

| 2026-07-26 | Indexed **CDAF-001 = Constitutional Decision Assimilation Framework** (`00-CEP/CEP-002` **Article 28**, added by **CEP-002-AMD-002** under Art 21; version 1.1 → 1.2). Establishes the assimilation prohibition (no agreed decision may remain only in conversation history), the mandatory nine-stage decision lifecycle, the closed five-member disposition set, and the **Implementation Evidence Gate** that blocks successor implementation and architectural work while any ratified decision is undispositioned. Machine-readable overlay + engine at `00-MASTER/UCDA-000001/`; bound as `G-14` / `CK-DECISION-EVIDENCE` / `PROGRAM-000016` / `PR-21` / `IV-17` in `00-MASTER/UCCEP-000000/uccep-bindings.json`; recorded as finding `UCCEP-F-008` with disposition IMPLEMENTED. First execution: **64 decisions, 0 undispositioned, 0 conversation-only, 205 located evidence references, gate OPEN**. Trigger: **CF-01/CF-03** (`00-MASTER/UAKOS-CLOSURE-006/13-CONSTITUTIONAL-FINDINGS-REGISTER.md`). No new register, authority, gate apparatus, pipeline, or scheduler was created. | CDAF-001 — decision assimilation made constitutional and executable |

| 2026-07-31 | Indexed **UCEF-000001 / CEP-009-AMD-001 = Universal Constitutional Evolution Framework** (`00-CEP/CEP-009-CONSTITUTIONAL-AMENDMENT-EVOLUTION-CONSTITUTION.md` **ADDENDUM B**, added under Art IV.2 (additive) as an extension under `00-CMG/CMG-000001` XLI; version 1.0 → 1.1, recorded in `AMENDMENT RECORD — CEP-009-AMD-001`). Institutionalizes: the **Primary Constitutional Law of Evolution** (the foundation never requires redesign to admit a future construct — B.2); the **open, non-exhaustive register of construct classes**, which shall never be assumed complete and whose absence is no ground of rejection (B.3); the **canonical fifteen-stage constitutional evolution lifecycle** Discovery → Context Assimilation → Repository Truth Discovery → Reuse Analysis → Dependency Analysis → Constitutional Registration → Ontology Integration → Taxonomy Integration → Registry Synchronization → Governance Validation → Implementation Planning → Implementation → Validation → Certification → Repository Evolution, **each stage bound to a located owner and none authored here** (B.4); **open-world expansion** with no finite architectural boundary, bounded only by evidence (B.5); and the **sixteen architectural acceptance properties** a new construct must satisfy, each discharged by a located mechanism (B.6). **Disposition EXTEND** under `CMG-000001` LXXVII.2(b) — the concern lay within `CEP-009`'s declared scope (Art II.1) and was unaddressed there. **CREATE was rejected**: `CMG-000001` LXXVI/LXXVII already own construct admission and `CMG-GAP-09` is recorded CLOSED by them, so a second mechanism would breach `CMG-INV-02` / `CMG-L-14`. **No authority, registry, lifecycle or namespace is created** (`CMG-000001` XLI.5); no `CEP-009` Article, clause or identifier is renumbered, reused or repurposed (XLII.4). Machine-readable overlay + engine at `00-MASTER/UCEF-000001/` (`AUTHORITY = NONE — DERIVED TRUTH`), gate `make ucef-gate` / `.github/workflows/ucef-gate.yml`. First execution: **18/18 validation dimensions PASS, 8/8 exit criteria PASS, 6/6 self-guards 0 findings, 15/15 stages bound externally, 16/16 properties discharged, 33 construct classes over an OPEN register, 17 axes unbounded, gate OPEN, CERTIFIED-PROVISIONAL**. Registry updated in the same change (`00-CMG/CMG-REGISTRY.json`, `cmg-gate` 0 findings) per `CMG-000001` XLIII.2(f). Deliberately **not** aggregated into `uccep-bindings.json` (`UCEF-K-01`) to preserve the aggregate seal protected by `EVOLUTION-001` §5. | UCEF-000001 — constitutional evolution made normative and executable |

| 2026-08-04 | Indexed **Ω-P-ADMISSION = admission of the Ω-P programme determinations to Repository Truth** (`00-MASTER/EVOLUTION-001/Ω-P1-UNIVERSAL-CONSTITUTIONAL-KERNEL-DETERMINATION.md`, `Ω-P2-CONSTITUTIONAL-RECONCILIATION.md`, `Ω-P2-E1-CERTIFIED-EVOLUTION-EPOCH.md`, `Ω-P2-R-CANONICAL-RECONCILIATION.md`). Four constitutional determinations existed as untracked CANDIDATES — *"reported, never registered, until it is bound by `git add`"* (`00-BOOK/tools/config.py`) — and each made its own admission conditional on acceptance of the canonical ownership it proved plus the located registration transaction. Both conditions are discharged. Canonical home `00-MASTER/EVOLUTION-001/` is **REUSED** (the located home of the tracked Ω-E03/Ω-E04/Ω-E05 completion certificates): no new home, namespace or identifier, **CREATE = 0**. `00-MASTER/` is excluded from corpus registration by `UCOS-RECON-C1`, so admission consumes no corpus identity and `register.sh --guard` reports no drift. Recorded as `DEC-OMEGA-P-01`…`-04` (disposition **IMPLEMENTED**, stage `REPOSITORY-TRUTH-UPDATE`) and `DEC-OMEGA-P-05` (disposition **REPRESENTED-BY-EXISTING-CANONICAL-CAPABILITY**, canonical owner `Ω-P2-R`) in `00-MASTER/UCDA-000001/ucda-decisions.json`. The fifteen Ω-P proposition outcomes are **not** re-recorded: Ω-P2-R §7 already carries exactly one certified outcome each — 7 FALSIFIED · 5 PROVEN · 1 UNKNOWN · 1 REUSE · 1 WITHDRAWN, with §9 certifying 0 contradictions and 0 outcomes outside the closed vocabulary — so the located owner is registered rather than copied, and no second disposition store is opened. Admission changes **standing only**: AUTHORITY remains NONE (DERIVED TRUTH) and no measurement, theorem, cardinality or verdict in any of the four was altered. Blocking condition discharged: `Ω-P1 §6` and `Ω-P2-E1 §8.7` both recorded that an untracked entry under `00-MASTER/EVOLUTION-001/` blocks re-assertion of the `UCOS-RFP-001` fixed point by `CLO-01`/`CLO-05`; `rfp_engine.py --gate` confirmed it, naming all four as `pre-existing untracked`. | Ω-P-ADMISSION — nothing constitutional remains a candidate outside Repository Truth |

---

*END OF ARTIFACT — MCP-004 · MASTER DECISIONS · ACTIVE · LIVING · AUTHORITY = NONE (DERIVED TRUTH)*
