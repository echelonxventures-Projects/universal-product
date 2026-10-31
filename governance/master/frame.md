# LUXORA Ω∞ — Master Specification and Execution Mandate

## Part A — Governance

### A.1 Document control

| Field | Value |
|---|---|
| Document ID | LXM-MASTER |
| Version | 1.0.0-rc.1 |
| Status | **CANDIDATE FOR OWNER REVIEW.** Not adopted and not authoritative until the owner approves it (LXM-DEC-000010). |
| Date | 2026-10-30 |
| Accountable owner | Bipin Kumar |
| Prepared by | `amazon-44` (read-only); generated from `reqs.txt`, `stages.txt`, `coverage.txt` and this frame by `build.py` |
| Parent contract | SRC-0001, the owner mandate, reproduced verbatim in Appendix A |
| Authorized writer | `amazon-62` (LXM-REQ-000216) |
| Release status | NO-GO (status dimension D5) |
| Content digest | Recorded in the delivery report; a file cannot contain its own SHA-256 |

**Revision history**

| Version | Date | Change |
|---|---|---|
| 1.0.0-rc.1 | 2026-10-30 | First candidate. Consolidates SRC-0001 to SRC-0008, applies owner decisions K1–K8, restores the six omitted execution instructions, and assimilates principle LXM-ACP-001 (LXM-REQ-000220 to LXM-REQ-000226). |
| 1.0.0-rc.2 | 2026-10-30 | Assimilates directive SRC-0009 through the gate: LXM-REQ-000227 to LXM-REQ-000230 created, LXM-REQ-000220 and LXM-REQ-000225 extended, eleven existing records recognized; SRC-0009 §7.2 held with SRC-0008 §7.1 for one owner decision. |
| 1.0.0-rc.3 | 2026-10-30 | Owner adopts LXM-DEC-000014 (Part C.3): supplementary escalation criteria assimilated as one new record; intake exceptions LXM-EXC-000001 and LXM-EXC-000002 resolved against it; the E1–E5 escalation record unchanged. |
| 1.0.0-rc.4 | 2026-10-30 | Owner confirms that K1–K8 (Part C.1) have an empty mutation-authorization scope. They stay adopted and binding. Part C now separates each decision's status, normative effect and authorization scope. The gate refuses any change that cites a decision outside its scope. |
| 1.0.0-rc.5 | 2026-10-30 | The decision register moves to its own canonical file and Part C is generated from it, unchanged. Every stage action gets a permanent ID (`STG-NN.A-k`), shown in Part E; citations no longer depend on order. No requirement changed. |
| 1.0.0-rc.6 | 2026-10-30 | Implementation traceability: `trace.txt`, rendered as Part H.4, links product requirements to the code, configuration and tests that implement them, each link with its basis; 1 known gap recorded. No requirement changed. |
| 1.0.0-rc.7 | 2026-10-30 | The evidence register moves to its own canonical file (G.3 unchanged), and recording a decision or evidence becomes a gated contribution. LXM-EVD-000007, today's CI observation for `39ed4d6`, supersedes LXM-EVD-000002. No requirement changed. |
| 1.0.0-rc.8 | 2026-10-30 | Evidence recorded through the gate: LXM-EVD-000008 (the full test chain passes on `39ed4d6` locally under Node 22.23.4) and LXM-EVD-000009 (the runtime settings read trace). No requirement changed. |
| 1.0.0-rc.9 | 2026-10-31 | Owner sources SRC-0010 to SRC-0016 registered (provisional extracts). SRC-0011 to SRC-0016 assimilated clause by clause: 177 of 179 clauses recognized or extending existing records, no new record; 2 held as contradictions for owner review (LXM-EXC-000005, LXM-EXC-000006). SRC-0010 held for LXM-DEC-000015. The re-sent master mandate and Decisions 3–5 are SRC-0001 itself (LXM-EVD-000010). |
| 1.0.0-rc.10 | 2026-10-31 | Owner sources SRC-0017 to SRC-0020 assimilated as LXM-REQ-000232 to 000235 (kernel derivation; Master Registry after all validation; the feedback layer; close every gap). The gate log becomes a hash chain recording each mutation, so the registers can be rebuilt by projection. New tools: gate impact, gate accuracy, computed states, knowledge status. |
| 1.0.0-rc.11 | 2026-10-31 | Owner instructions SRC-0021 to SRC-0024 assimilated (extending LXM-REQ-000220, 000227 and 000230). Requirement scopes become registered data (`scopes.txt`). A governed gate rule: dates and file paths are identifiers, not quantities. Specifications link requirements to their designs, and computed states now reach Verified. A kernel-derivation check measures LXM-REQ-000232. |
| 1.0.0-rc.12 | 2026-10-31 | Every canonical kind goes through the gate (trace, scope, source, stage action and prose join requirement, decision and evidence), and CI requires the canonical state to equal the last gate outcome; enforcement starts from one recorded baseline. Changes are re-validated against every recorded source clause; capture is the one way in; Level 3 outcomes feed back as proposals and evidence (LXM-EVD-000011); the registers split into small files and rebuild identically. No requirement changed. |

### A.2 Authority and precedence

1. Explicit later owner instructions (SRC-0004 to SRC-0007) supersede earlier instructions only within the scope they explicitly change. Each change is recorded in Part G.2.
2. The owner mandate (SRC-0001, Appendix A) remains the governing business and architectural contract. Nothing in this master weakens it.
3. Once adopted, this master's Parts B–F govern the implementation sequence, execution rules and acceptance process. They replace SRC-0002 and SRC-0003 as the operative procedure; both remain historical inputs.
4. Owner-approved architectural additions (scope ARC) add or strengthen requirements and never silently weaken the mandate.
5. Repository records are evidence of current behavior, never permission to redefine required behavior.
6. Historical notes and assistant suggestions are not owner-approved requirements unless adopted in Part C.
7. Where two authoritative instructions conflict and this order cannot settle it, an indexed conflict record is created and escalated (LXM-REQ-000016, E4). Consequential decisions are never resolved by inference.

### A.3 Source register

{{SOURCES}}

### A.4 How this master applies Knowledge Once

- **Requirement text** lives only in Part D, as one record per requirement with a stable ID, source lineage, analysis class and exactly one disposition.
- **Headings have distinct namespaces.** A Part D group heading carries the `CAT-` prefix and the record scope, for example `CAT-EXE` or `CAT-STG-01`, the requirements scoped to Stage 1. A bare `STG-NN` always names the executable procedure in Part E. Stage numbers and titles are the same in both places.
- **Stage procedures** (Part E) prescribe executable actions and cite requirement IDs; they never restate requirement text.
- **Appendix A** is the immutable provenance copy of the mandate, kept for authority and audit. It is not a registry; where a Part D record restates one of its operational details, the record cites the Appendix A line it comes from.
- **Every register and index** in Parts F–H is generated from the same records, so none is maintained by hand.
- **This candidate applies LXM-ACP-001 to itself:** `build.py` regenerates every derived view from the records (LXM-REQ-000223), and `validate.py` is the acceptance gate (LXM-REQ-000222). The candidate is not delivered unless every check passes. Requirement contributions enter this candidate only through `assimilate.py`, which discovers, classifies and resolves each one, validates the staged result with `validate.py`, and commits records and derived views together or not at all; refusals are recorded in `intake/exceptions.txt`. Its regression fixtures are in `test_assimilate.py`. Sources with a clause ledger (`sources/<SRC>.clauses`) are checked clause by clause for semantic coverage. A repository implementation of the assimilation mechanism does not exist yet; building it is STG-02 and STG-13 work, and its maturity is D2 *defined*.

## Part B — Canonical status model (LXM-DEC-000003)

One extensible model with separate semantic dimensions. A fact is always stated as a dimension and a value, never as a bare word such as "done". Dimensions and values are registered data, implemented on the repository's existing kernel lifecycle (LXM-REQ-000073); new values are added only by governed change, and existing values are never renamed.

| Dimension | Applies to | Values (in order where ordered) | Transition rule |
|---|---|---|---|
| **D1 Conformance** | each requirement | satisfied · partially satisfied · unsatisfied · blocked · awaiting owner decision · awaiting external verification · not applicable (reason required) | "satisfied" only with D4 = current evidence at the exact SHA; reverts when its evidence becomes stale or fails |
| **D2 Maturity** (ordered) | each capability, business profile, provider, method and technology use | conceptualized → architecturally supported → defined → implemented → registered and discoverable → configurable → validated → integrated → tested → verified → certified → approved → enabled → operational → production ready | each value needs its own evidence; an earlier value never proves a later one; "externally verified" means D2 verified with an external evidence source |
| **D3 Observation** | each gap-inventory item | existing and working · implemented not configured · configured not applied · missing · partially implemented · untested · externally blocked · awaiting owner decision | set by source inspection; reset whenever the code changes |
| **D4 Evidence** | each evidence record | current · stale · historical failed · superseded | becomes stale when code, generated artifacts, dependencies or execution conditions change |
| **D5 Release authorization** | each release candidate | NO-GO (default) · GO authorized | GO only by Bipin Kumar's recorded authorization, naming the exact commit and target |
| **D6 Technology lifecycle** | each technology item or release | discovered · candidate · under evaluation · compatible · verified · approved · resolved for a use · active · deprecated · rejected · prohibited | promotion to approved or active requires distinct-person approval (LXM-REQ-000045) |
| **D7 Decision** | each owner decision | open · packet prepared · decided (owner, date, scope) · superseded | only the owner sets "decided" |

**How the source vocabularies map onto the model**

| Source vocabulary | Maps to |
|---|---|
| SRC-0002/0003 Stage 2: satisfied, partial, unsatisfied, blocked, awaiting owner decision | D1 |
| SRC-0003 Stage 3, eight observation states | D3 |
| Stage 7: architecturally supported … operational (nine states) | D2 |
| Stage 13: implemented, configurable, integrated, tested, certified, externally verified, production ready, authorized for release | D2 (the first seven) and D5 (the last) |
| Mandate Decision 2: ten capability and profile states | D2 (states 1–9) and D5 (state 10) |
| Mandate §15: twelve per-provider checks | D2 evidence for each provider and method: adapter → implemented; schema → defined; registry → registered; credentials and merchant setup → enabled prerequisite (external dependency); sandbox available → external dependency; authentication, lifecycle, webhooks, refunds verified → tested/verified; live operation → operational; production configuration and monitoring → production ready; release authorized → D5 |
| Technology lifecycle in SRC-0004/0006 and PR-053 | D6 |
| SRC-0006 §16 (fifteen maturity states) and §17 (seven requirement statuses) | D2 and D1 |

## Part C — Decision register

Every decision has three separate properties:
- **Status (applicability):** adopted (C.1, C.3) or open (C.2). An adopted decision is binding wherever its outcome applies, until a later owner decision supersedes it. Only adoption gives a decision force; an open decision decides nothing.
- **Normative effect:** what the decision fixed in this master. The *Effect in this master* column names it, and every record expressing it carries the decision in `k:`. Changing such a record is owner-reserved.
- **Mutation-authorization scope:** the *Authorizes* column. It lists the source clauses (and any records) that a gated change citing the decision may touch. *None* means an empty scope: the decision authorizes no change to canonical records. An empty scope does not mean that the decision is inactive, rejected, expired or superseded, and it does not weaken its effect.

### C.1 Owner decisions K1–K8 (adopted 2026-10-30, SRC-0007)

The owner confirmed on 2026-10-30 that K1–K8 authorize no further gated mutations. They stay adopted and binding with their original outcomes, rationale and lineage, but their scope is empty. Any future amendment to a rule they established goes through normal assimilation and needs whatever further owner authorization its classification requires. Their scope is not broadened retrospectively. The confirmation is recorded in session `47abdf14`, transcript line 1384, entry `de092231-c546-4181-8542-4463d0cb3b96`, 2026-10-30T12:35:49.409Z. Its verbatim text is `intake/decisions/LXM-DEC-000001-000008.scope-confirmation.txt` (SHA-256 `a36caf2ae53bc178d17f42db6ba69bb738d24f0d7cdfa00d7e27e9e577d88d1f`).

{{DECISIONS:C.1}}

### C.3 Owner decisions adopted through the assimilation gate

Each row records what the decision authorizes. The gate accepts a change citing the decision only inside that scope. The decisions in C.1 have an empty scope.

{{DECISIONS:C.3}}

### C.2 Open owner-reserved decisions

{{DECISIONS:C.2}}

## Part D — Requirement catalogue

{{CATALOGUE}}

## Part E — Stage procedures

{{STAGES}}

## Part F — Final report structure and coverage (LXM-DEC-000001)

The final report has sections A–K, defined by LXM-REQ-000174 to LXM-REQ-000184. Every reporting element required by any source is mapped to at least one section:

{{COVERAGE}}

## Part G — Registers

### G.1 Restoration register for the six omitted instructions

{{OMISSIONS}}

### G.2 Supersession and change history

| ID | Change | From | To | Authority |
|---|---|---|---|---|
| LXM-CHG-000001 | Candidate head | `ed634ad`, run 40922556022 (SRC-0002/0003 Stage 0) | `39ed4d6`, run 40990327443 | Repository evidence; LXM-REQ-000027 |
| LXM-CHG-000002 | Re-resolution fact | "35 development dependencies, ten version changes, jsdom/dom-selector 9→10" (S68) | Integrity-only re-resolution, 0 version changes (`39ed4d6`); `9e22917` and failed run 40931760311 kept as historical | Repository evidence; LXM-REQ-000029 |
| LXM-CHG-000003 | Approval qualifier | "distinct-person approval where required" (L50) | Unconditional independent approval (S101) | SRC-0002; LXM-REQ-000045 |
| LXM-CHG-000004 | CI acceptance | "two independent, fully green CI runs" | Two distinct successful run IDs; attempts count once | K2; LXM-REQ-000153 |
| LXM-CHG-000005 | Final report | A–K beside the mandate's §29 A–I | A–K with every §29 element merged | K1; LXM-REQ-000173 to LXM-REQ-000184 |
| LXM-CHG-000006 | Delivery form | "Single-file edition, supply unsplit" (L3) | This master; sources are immutable historical inputs | K8; LXM-REQ-000191 |
| LXM-CHG-000007 | Naming in the procedure | "Amazon-like", "Uber-like" and similar in Stage 7 (S302–307, L111) | Neutral descriptions registered as data; Appendix A keeps its own wording | K7; LXM-REQ-000106 |
| LXM-CHG-000008 | Waiting on CI | Unspecified (L18) versus no concurrent work (S125) | Candidate frozen; only non-mutating, pre-scoped analysis | K4; LXM-REQ-000054 |
| LXM-CHG-000009 | Workspace retirement | Retire after proof (S552) | Never the original iCloud workspace, Phase 1 or preservation copies without separate authorization | K6; LXM-REQ-000167 |

### G.3 Evidence register (facts verified read-only by `amazon-44`, 2026-10-30)

{{EVIDENCE:G.3}}

### G.4 Remaining genuinely owner-reserved decisions

1. **LXM-DEC-000009:** how to obtain the second distinct CI run ID.
2. **LXM-DEC-000010:** adopting this master, and its repository location.
3. **Lifting amazon-62's own instruction "After PR-053, stop"**, typed in its own session. Its session boundary means only the owner can lift it there.
4. **LXM-DEC-000011:** PR-053 (a), the 22.13.1 lane versus the undici fixes. Related register choices: (b) the `prom-client` replacement; (g) who approves promoting the evaluation lanes; whether Redis is supported.
5. **LXM-DEC-000012:** MD-1–MD-5.
6. **The release policy** for critical and high findings (mandate §27).
7. **External resources only the owner can supply:** hosting target and region, secret store, domain and certificate, payment-provider accounts and sandbox credentials, notification provider, expected traffic, backup destination and retention, on-call contacts, rounding policy per currency and jurisdiction, and the refund-handling decision (PR-029).
8. **Any retirement, move or cleaning** of the original iCloud workspace, the Phase 1 work, `~/LUXORA-preservation/` or a stale `index.lock` outside the canonical workspace.
9. **LXM-DEC-000013:** production release authorization.
10. **Capturing SRC-0004 to SRC-0009 as files**, so they can be hashed (Part A.3).
11. *Decided 2026-10-30 (LXM-DEC-000014, Part C.3):* SRC-0008 §7.1 and SRC-0009 §7.2 versus LXM-REQ-000016. The owner chose option 2: supplementary criteria in a separate record; E1–E5 unchanged.

## Part H — Indexes

### H.1 Stage index

{{STAGE_INDEX}}

### H.2 Source → requirement → stage traceability

{{TRACE}}

### H.4 Requirement → implementation traceability

Generated from `trace.txt` (LXM-REQ-000204). Procedural requirements are traced by the stage actions that apply them (H.2). Each implementation path is checked against the code by `code_adapter.py --trace`.

{{IMPL_TRACE}}

### H.3 Source clause → canonical record coverage

Generated from each source's clause ledger (`sources/<SRC>.clauses`), the records' coverage relations and the open intake holds. *covers* means the record expresses the clause; *supports* means the record provides something the clause relies on.

{{CLAUSES}}

---

# Appendix A — Owner mandate (SRC-0001), verbatim

{{APPENDIX_NOTE}}

{{APPENDIX}}
