# USIS-016 — Evidence Architecture

| Field | Value |
|-------|-------|
| ARTIFACT ID | USIS-016 (Evidence Architecture — registered corpus instantiation) |
| UCOS-PROGRAM | USIS |
| UCOS-CATEGORY | USIS |
| UCOS-VOLUME | VOL-024 |
| UCOS-FAMILY | UNIVERSAL-SCIENCE-INTELLIGENCE |
| UCOS-DOMAIN | science-intelligence |
| UNIVERSAL ID | Allocated append-only at registration (`ukb build`) from the immutable ledger — expected `UCOS-USIS-000019` (next free after `UCOS-USIS-000018` = USIS-015). Repository Truth (the ledger) is authoritative; no identifier is reused. |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| MISSION | Wave 2 · Evidence Architecture (EVO-USIS-016) — establish the constitutional Evidence-tier architecture of USIS |
| CLASSIFICATION | Constitutional Architecture — the canonical architecture of the Evidence tier (governed evidence & traceability model) owned by the substrate (subordinate to USIS-001…015, USIS-017, USIS-INT-001, and to LAW Ω∞-000 / MIP Parts 19/20/21) |
| STATUS | RATIFIED (PROVISIONAL / engineering-authority tier) · Wave 2 · registered |
| OWNING SCOPE | Substrate Evidence tier (USIS-004 tier **22 — Evidence**; parent tier Certification/21) — the evidence & traceability model (content-addressed records, provenance, lineage, retention, closed traceability) that discharges the meta-model's **evidence closure** obligation (TRACK-001 fail-closed) |
| DEPENDS-ON | USIS-015 · USIS-014 · USIS-INT-001 · USIS-017 · USIS-013 · USIS-012 · USIS-011 · USIS-010 · USIS-009 · USIS-008 · USIS-006 · USIS-007 · USIS-004 · CEP-008 (referenced) · TRACK-001 (referenced) |
| PARENT | (program family USIS — parents structurally to the USIS program root USIS-GOV-000; non-chained) |
| IMPLEMENTS | USIS-004 Universal Capability Meta-Model tier **22 (Evidence)** — discharges the tier's **evidence closure** obligation (TRACK-001 fail-closed) (LAW USIS-08) |
| REALIZES | LAW Ω∞-000 · CEP-008 (Constitutional Evidence & Traceability Constitution) · UCIC-001 Output-5 (evidence bundle) · GOV-002 (constitution-to-implementation traceability); the append-only evidence/audit substrate produced by the Digital-Twin runtime (`ukbx certify` / `ukbx twin`) |
| GOVERNED BY | USIS-001 (LAW USIS-02/04/05/07/08/09) · USIS-004 (24-tier meta-model) · CEP-008 (Constitutional Evidence & Traceability Constitution) · UCIC-001 (Output-5; TRACK-001) · GOV-001-T3 (No-Orphan) · GOV-002 (traceability) · REG-AUTO-001 (registration / registers) · FREEZE C4 (7-stream execution model) |
| AUTHORITY | **NONE — DERIVED.** Operationalizes the evidence & traceability mandate conferred by USIS-001, CEP-008, and the USIS-004 Evidence tier. It **records, identifies, preserves, and traces** only (CEP-008 I.2); it decides no validation, certification, ratification, or freeze outcome and introduces no constitutional content. It references the executable evidence substrate (`ukbx certify`/`ukbx twin` outputs, the `00-BOOK/DATA` registers, the `.runtime/governance` audit) and authorizes no code. Absolute FINALIZED standing remains pending the out-of-corpus External Constituent Act (DR-RAT-11 — external, non-blocking). |
| PROVENANCE | Authored under EVO-USIS-016 (parent programme EVO-USIS-015) as the Wave-2 Evidence-tier architecture named "pending" by USIS-INT-001 (Part G — "Evidence (→ USIS-016, pending)"), USIS-015 (Part P — "USIS-016 (Evidence, tier 22) Depends-On this tier — Certification founds Evidence"; Part R evidence model), and USIS-014. No new constitutional knowledge is introduced: evidence & traceability law is inherited from CEP-008 and the meta-model; the executable evidence substrate is **referenced** as-is. Canonical home `15-…/17-EVIDENCE/` per USIS-005 §2 (area 17 = EVIDENCE — "evidence model (traces, provenance)") and §3 (USIS-006…017 per-layer architectures, areas 08–18) — no variance; no structure invented; no `config.py` edit (`^15-…/` already classifies to USIS/VOL-024). |
| CONFLICT RULE | Higher frozen/governing instruments prevail; this instrument is void to the extent of any conflict. The executable evidence substrate (`ukbx certify`/`ukbx twin`, the `00-BOOK/DATA` registers, `.runtime/governance` audit) and CEP-008 are **referenced**; the canonical home governs and this architecture holds only a reference (LAW USIS-02). |

> **Purpose.** Establish the **canonical architecture of the Evidence tier** — the tier that makes every constitutional action, decision, and state transition of the science-intelligence substrate **substantiated, addressable, reproducible, provenance-bearing, and closed-traceable**, so that *nothing exists without evidence, nothing changes without traceability, nothing is accepted without provenance, and nothing evolves without historical continuity* (CEP-008 P.3). This instrument creates the `15-UNIVERSAL-SCIENCE-INTELLIGENCE/17-EVIDENCE/` home and defines the Evidence node shape, its ontology/taxonomy placement, evidence lifecycle, evidence model, generation, collection, lineage, integrity, traceability, retention, governance, dependency model, validation/certification integration, and the Digital-Twin / runtime / registry / knowledge / cross-layer evidence contracts — while remaining technology-/implementation-/infrastructure-/platform-agnostic and vendor-neutral, and **never duplicating** CEP-008 or the executable evidence substrate. **This instrument establishes only the Evidence-tier architecture.** It authors **no** individual evidence record or capability instance — those are produced by the referenced substrate at the time of the action they substantiate, not by this architecture.

---

## PART A — Constitutional scope

This architecture is the registered instantiation of the evidence & traceability mandate of USIS-001, CEP-008, and the Evidence tier (22) of the USIS-004 meta-model:

- **USIS-004 Part C tier 22** — Evidence (parent = Certification, tier 21). USIS-016 is the constitutional architecture and rule-set for this tier; its closure obligation is **evidence closure** — *TRACK-001 fail-closed* (absence of required evidence ⇒ NOT-DONE).
- **CEP-008 (Constitutional Evidence & Traceability Constitution)** — the frozen constitutional source of evidence & traceability law (Articles I–XXV); USIS-016 **references** it and specializes it for the science-intelligence substrate, never rewriting, duplicating, or restating it (CEP-008 preamble; LAW USIS-02).
- **USIS-001 LAW USIS-07 (explainability & grounding)** — evidence is the grounding of every verdict; a claim, decision, or state transition without preserved evidence is unsubstantiated and not a valid state (CEP-008 V.5 / VIII.4).
- **USIS-001 LAW USIS-04** — evidence is architecture, not technology: it names no storage vendor/hash library/CI system; the executable evidence substrate (`ukbx certify`/`ukbx twin`, the `00-BOOK/DATA` registers, `.runtime/governance`) is referenced.
- **The validated + certified spine is the evidence subject:** USIS-006…013/017 + USIS-INT-001 (adjudicated `VALID` by USIS-014, `CERTIFIED` by USIS-015) are the surfaces evidenced, reached **by reference**; USIS-016 `Depends-On` USIS-015/USIS-014 and re-homes nothing (LAW USIS-02).

**Scope of this instrument (Wave 2 · EVO-USIS-016).** This architecture:
- creates the `15-…/17-EVIDENCE/` home and this single registered architecture artifact;
- defines the Evidence **node shape, ontology/taxonomy placement, evidence lifecycle, evidence model, generation, collection, lineage, integrity, traceability, retention, governance, dependency model, validation-integration, certification-integration**, and the **Digital-Twin / runtime / registry / knowledge / cross-layer** evidence contracts (Parts B–W);
- founds downward-only on `USIS-015/014/INT-001/017/013/012/011/010/009/008/006/007/004` and references `CEP-008`/`TRACK-001` (Depends-On; parents to the USIS program root), introducing no upstream change and no cycle;
- authors **no** evidence record, collector, verifier, or capability instance, and begins **no** Wave-3/5 realization;
- reuses, without duplication, the executable evidence substrate (`ukbx certify`, `ukbx twin`, the `00-BOOK/DATA` registers, `.runtime/governance` audit), CEP-008, UCIC-001 (Output-5), GOV-002, TRACK-001, REG-AUTO-001, and the governance instruments — and performs **no** `config.py` edit.

## PART B — Evidence architecture (the Evidence node)

An evidence record is a typed node of the canonical form:

```
{ id: <content-addressed identity, deterministic from content (CEP-008 IV.1)>,
  home: 17-EVIDENCE/<subject>/ (architecture) | 00-BOOK/DATA + .runtime/governance (runtime records),
  tier: 22,
  subject: <action | decision | state-transition | claim it substantiates>,
  classification: action | decision | state-transition | claim (exactly one — CEP-008 VII.2),
  provenance: { action, actor, stage, program-state-hash } (immutable — CEP-008 X.2),
  referenced_inputs: <by identity, never inlined (CEP-008 II.3 / XIV.3)>,
  outcome: <recorded result>,
  state: PROPOSED | COLLECTED | VERIFIED | PRESERVED | SUPERSEDED | REJECTED (CEP-008 VI.1),
  lineage: { predecessor?, successors[] } (acyclic, append-only — CEP-008 XII),
  dependencies: <evidence depended-upon, by identity; acyclic (CEP-008 XIII)>,
  certification_ref: <USIS-015 verdict this evidence bundles (meta-model tier 21→22)>,
  traceability_links: <typed, addressable, append-only (CEP-008 XI.3)>,
  owner, status }
```

- The node is the meta-model **child of the Certification tier** (USIS-004 tier 22, parent 21): an evidence bundle substantiates a certification verdict (and, cross-layer, the validated/certified surfaces it spans).
- It is a **record + traceability contract** — it binds a substantiated matter to a content-addressed, provenance-bearing, immutable-on-preservation record and to closed traceability links. It embeds no store and names no vendor (LAW USIS-04).
- Produces **no** code and **no** collector/verifier; evidence is created, collected, verified, and preserved by the referenced substrate (evidence independence, Part N).

## PART C — Evidence ontology (reference to USIS-005)

Every evidence record is **placed** into the substrate ontology (USIS-005 `02-ONTOLOGY/`) by reference: it declares evidence concepts (record, identity, provenance, lineage, dependency, traceability-link, state, classification, defect) and their relations. Ontology Closure (USIS-011 obligation 11) governs. USIS-016 defines the *placement contract*; it does not duplicate the ontology (LAW USIS-02).

## PART D — Evidence taxonomy (reference to USIS-005)

Every evidence record occupies a taxon in the substrate taxonomy (USIS-005 `03-TAXONOMY/`) — the evidence taxonomy of **evidence kinds** (CEP-008 VII.1): action-evidence, decision-evidence, state-transition-evidence, and claim-evidence; and, cross-layer, the surface it evidences (architecture / implementation / runtime / registry / knowledge / validation / certification / Digital-Twin). Taxonomy Closure (USIS-011 obligation 12) governs. USIS-016 defines the *taxon-placement contract*; the taxonomy structure remains owned by USIS-005.

## PART E — Evidence lifecycle

An evidence node follows the CEP-008 evidence state machine (Article VI) under UCIC-001:

```
create → classify → verify → preserve → (thereafter immutable; evolve only via successor)
states:  PROPOSED → COLLECTED → VERIFIED → PRESERVED → SUPERSEDED
                 ↘ REJECTED   ↘ REJECTED  ↘ REJECTED
```

- **Legal transitions only** (CEP-008 VI.3): PROPOSED→COLLECTED|REJECTED; COLLECTED→VERIFIED|REJECTED; VERIFIED→PRESERVED|REJECTED; PRESERVED→SUPERSEDED. Any other transition is illegal ⇒ HALTED (CEP-008 VI.4).
- **Evidence closure** (CEP-008 III.4) is the point at which evidence is preserved and registered; it is **distinct** from validation, certification, ratification, and freeze closure — USIS-016 owns evidence closure only and defers those to USIS-014/USIS-015/CEP-006/CEP-007 (referenced).
- Evidence **discharges** the evidence obligation of the capability lifecycle (it substantiates the `VALIDATED`/`CERTIFIED` stages produced by USIS-014/USIS-015) — it does not redefine that lifecycle (UCIC-001 / USIS-006/008 own it; referenced). Certification (`CERTIFIED`, USIS-015) is the **parent tier**: evidence bundles a certification verdict (meta-model tier 21→22).

## PART F — Evidence model

The evidence model is the deterministic set of properties a record must carry to be `PRESERVED` and to substantiate a claim (CEP-008 Articles IV/V/VIII/X/XVII):

| Model element | Contract (what "preserved evidence" requires) | Source (referenced) |
|---------------|------------------------------------------------|---------------------|
| **Content-addressed identity** | unique identity derived deterministically from content; stable, never reassigned | CEP-008 IV |
| **Creation binding** | created at the time of the action, recording action/actor/inputs-by-reference/outcome | CEP-008 V.2 |
| **Completeness** | records matter + actor + referenced inputs + outcome + identity; machine-verifiable | CEP-008 VIII |
| **Provenance** | origin (action, actor, stage, program-state) recorded at creation, immutable | CEP-008 X |
| **Reproducibility / determinism** | identical content ⇒ identical identity + verification result | CEP-008 IV.2 / XVIII.3 |
| **Immutability on preservation** | never modified after preservation; evolve only via successor | CEP-008 IX.2 / III.3 |
| **Record schema** | identity, classification, provenance, referenced inputs, outcome, state, lineage, program-state hash | CEP-008 XVII.1 |

**Fail-closed rule.** An action requiring evidence progresses **iff** its evidence is complete and preserved. Incomplete evidence is not preserved and substantiates nothing (CEP-008 VIII.2/VIII.4); an action that produces no evidence is treated as if it did not lawfully occur (CEP-008 V.5) — TRACK-001 NOT-DONE.

## PART G — Evidence generation

Evidence **generation** is the creation act (CEP-008 Article V): every constitutional action, decision, and state transition of the substrate **SHALL produce evidence** (V.1), created at the time of the action, deterministically and reproducibly (V.2/V.3). USIS-016 owns the *generation contract* — *what* must be generated (record + provenance at the substantiated moment) — never a generator. Fabricated, backdated, or fictitious-action evidence is prohibited and void (CEP-008 V.4). Generation is discharged by the referenced substrate (the certifier/twin runtime and the registration transaction emit records + append-only audit at the time of each action).

## PART H — Evidence collection

Evidence **collection** gathers the record of a matter deterministically and preserves it in a declared evidence area (CEP-008 Article XIV). Collection is **interpretation-free** — it records what occurred and does not interpret, judge, or decide (XIV.2; CEP-000 §15.5); it references inputs **by identity** and never inlines or copies constitutional content (XIV.3; II.3); it does not alter the matter it records (XIV.4). USIS-016 owns the *collection contract*; the declared evidence areas are the referenced registers (`00-BOOK/DATA/*.json`) and the append-only governance audit (`.runtime/governance/*`). USIS-016 stands up **no** collector of its own.

## PART I — Evidence lineage

Evidence **lineage** (CEP-008 Article XII) preserves each record's predecessor (where one exists) and successors as a **deterministic, acyclic, append-only** chain (XII.1/XII.2/XII.3). Evidence **evolution occurs only through successor evidence**, which supersedes its predecessor **without modifying it** (XII.4; III.3); the `PRESERVED → SUPERSEDED` transition records a lineage transition only and never mutates the preserved record (CEP-008 VI.6). Every version in a lineage remains individually reproducible and discoverable, enabling deterministic historical reconstruction (XII.5; XXIII.10). USIS-016 owns the *lineage contract*; lineage is materialized into the referenced Change/Version/Lineage register by the reused mechanism (`ukb build` → `00-BOOK/DATA/change-ledger.json` + `CHANGE-VERSION-LINEAGE-REGISTRY.md`).

## PART J — Evidence integrity

Evidence **integrity** (CEP-008 Article IX) requires that a record's content matches its content-addressed identity (IX.1) and that preserved evidence is **never modified** (IX.2). A **no-drift guard** verifies that every preserved record matches its identity and that every record is registered (IX.3); an integrity failure or detected drift places the Program in HALTED and emits a finding (IX.4; XX.2). An identity collision between two distinct records places the Program in HALTED (CEP-008 IV.4). USIS-016 owns the *integrity contract*; it is discharged by reference through `ukb validate` (append-only, no duplicate id/page, referential integrity) and `ukbx certify` (Registry/Identity/Change integrity domains) over the real corpus.

## PART K — Evidence traceability

Evidence **traceability** (CEP-008 Article XI; GOV-002) requires that **every artifact is traceable to its evidence chain** and every evidence record is traceable to the matter it substantiates (XI.1). Traceability is **rooted and closed with zero orphans** — every link resolves to an existing endpoint (XI.2); links are **typed, addressable, and append-only** (XI.3); traceability is verifiable at every gate and never deferred to freeze (XI.4). A discovered traceability orphan places the Program in HALTED until rooted or closed (XI.5). USIS-016 owns the *traceability contract*; links are materialized into the referenced Knowledge-Graph register (`relationships.json` + `KNOWLEDGE-GRAPH-REGISTRY.md`) and verified by `ukb validate` (referential integrity, C-05) + `ukbx twin --check` (C-08 navigation) — GOV-002 owns the constitution-to-implementation traceability determination, referenced.

## PART L — Evidence retention

Evidence **retention** (CEP-008 Article XV — Preservation) requires that preserved evidence is **immutable, content-addressed, and reproducible** (XV.1) and **never deleted**; superseded evidence is **retained for lineage** and marked `SUPERSEDED` (XV.2). Preservation maintains the discoverability of every record and its lineage for the life of the Program (XV.3; III.5) and supports **unbounded** successive evidence evolution without destroying historical truth (XV.4). USIS-016 owns the *retention contract* — retain-forever, supersede-never-delete, discoverable-for-life; it is discharged by the append-only registers and governance audit (referenced). No retention window truncates history; retention is bounded below by "forever for lineage," never above (append-only).

## PART M — Evidence governance & authority

Evidence is **governed and separated**. Evidence Authority **records and preserves only** (CEP-008 I.2); it decides no validation, certification, ratification, or freeze outcome and introduces no constitutional content. It is **single per record** — two authorities never own the same evidence record (I.3), and is **never self-conferred by Execution Authority** (I.5). Evidence and traceability jurisdiction is **bounded to CEP-008 alone** and **does not overlap** validation (CEP-004/USIS-014), certification (CEP-005/USIS-015), ratification (CEP-006), or freeze (CEP-007); those consume evidence **by reference** and never produce or own it (CEP-008 II.5) — Zero-Overlap (USIS-011 obligation 3). Evidence and traceability records are **operational memory** and **never enter the constitutional corpus** (CEP-008 XIX.3; XVI.5). **AUTHORITY = NONE (DERIVED):** USIS-016 confers no new governance authority, ratifies no constitution, and authorizes no EC-series step or code; absolute FINALIZED standing remains subject to the out-of-corpus External Constituent Act (DR-RAT-11 — external, non-blocking).

## PART N — Dependency model & Evidence independence

- **Dependency model.** `Depends-On` runs downward to USIS-015 (Certification, the parent tier), USIS-014 (Validation), and the full Wave-2 spine (USIS-INT-001/017/013/012/011/010/009/008/006/007/004), and references `CEP-008`, `TRACK-001`, `UCIC-001`, `GOV-002`, and the executable substrate (`ukbx certify`/`ukbx twin`, `00-BOOK/DATA`); `Parent` is the program root (non-chained). No forward reference (USIS-011 obligation 14). Acyclic, downward-only (obligation 5). **Evidence dependencies** among records are themselves declared and acyclic (CEP-008 XIII.1/XIII.2) — a cycle is prohibited and HALTS; a dependency on `REJECTED` evidence renders the dependent unsubstantiated (XIII.4).
- **Evidence independence.** The Evidence tier is architecture: it defines evidence *records, identity, provenance, lineage, retention, traceability, and authority*, not a concrete storage/hashing/CI technology. Generation/collection/verification/preservation occur in the referenced substrate, never embedded. The evidence architecture is fully defined independent of technology, implementation, infrastructure, platform, or vendor (LAW USIS-04).

## PART O — Evidence ↔ Validation integration

Validation (USIS-014) is a **consumer of evidence by reference** (CEP-008 II.5): a validation verdict is grounded in, and traceable to, its evidence chain (LAW USIS-07). USIS-016 supplies the *evidence contract* validation relies upon — every validation obligation's outcome is a substantiated, preserved, provenance-bearing record — and owns **no** validation logic (USIS-014 owns the verdict). Verification of evidence (CEP-008 Article XVIII: identity integrity, completeness, provenance, traceability closure before preservation) is **non-mutating** and **decides no validation outcome** (XVIII.2) — it verifies the evidence, not the subject. No overlap: USIS-014 validates the subject; USIS-016 substantiates and traces the record.

## PART P — Evidence ↔ Certification integration

Certification (USIS-015) is the **parent tier and a consumer of evidence by reference** (meta-model tier 21→22): a certification verdict is `CERTIFIED` only if it carries an evidence reference (USIS-015 Part R; CEP-008 II.5). USIS-016 supplies the *evidence bundle* (UCIC-001 Output-5) that a certification records — subject reference, gate set evaluated, certifier run + result, grounding trace, explanation, verdict — written to the referenced registers (`certification.json` + `CERTIFICATION-REGISTRY.md`) and the append-only audit (`.runtime/governance/certification-audit.json`). Absence of the bundle ⇒ NOT-DONE (TRACK-001) ⇒ `NOT-CERTIFIED`. USIS-016 owns the *bundle contract*; USIS-015 owns the verdict; the certifier runtime produces both — referenced, never duplicated.

## PART Q — Digital Twin evidence

Digital-Twin evidence is the tier's canonical runtime evidence surface: the Digital-Twin runtime (`ukbx certify` — UMB-IMP-006 / UMB-017; `ukbx twin`) emits, at the time of each run, **content-addressed, append-only** evidence of the corpus state — the integrity-domain results, twin signals, and change events — to `00-BOOK/DATA/certification.json` + `twin.json` + `change-ledger.json` and the append-only audit `.runtime/governance/`. USIS-016 owns the *Digital-Twin-evidence contract* (what the twin must record and preserve immutably); the twin and its runtime are owned by UMB-002 / UMB-IMP-006 — referenced, never duplicated (LAW USIS-02). A twin action that records no evidence is treated as not lawfully occurring (CEP-008 V.5).

## PART R — Runtime evidence

Runtime evidence (the surface named by USIS-013) attests, by immutable record and reference, that every self-* runtime effect is **evidenced at the moment it occurs**: bounded-autonomy decisions, reversibility-or-justification of self-* effects, and gate outcomes each produce a provenance-bearing record (CEP-008 V.1/X). An ungated or unrecorded self-* pathway ⇒ unsubstantiated ⇒ NOT-DONE (TRACK-001). USIS-016 owns the *runtime-evidence contract*; USIS-013 owns the runtime; the platform runtime executes and emits records — referenced.

## PART S — Registry evidence

Registry evidence attests that the registers (REG-AUTO-001 §2) are themselves an evidence substrate: **append-only, content-addressed, and reconciled against repository truth at boot** (CEP-008 XVI.3; XXI.1). The Evidence Registry is the single canonical record of all evidence records (their identities, states, classifications, provenance, lineage) and the Traceability Registry the single canonical record of all links (XVI.1), enforcing **uniqueness** (one canonical identity + one canonical owner; no duplicate authority — XVI.2). A record or link absent from its registry is deemed non-existent (XVI.4). USIS-016 owns the *registry-evidence contract*; the registers are owned by the universal mechanism (`ukb build` → `00-BOOK/DATA` + `00-BOOK/REGISTRIES`) — referenced, with **no parallel registry** created (LAW USIS-02).

## PART T — Knowledge evidence

Knowledge evidence attests **Knowledge-Once** over the evidence substrate: no duplicated evidence record or authority; every record singly-owned and homed (No-Orphan, GOV-001-T3); every reference resolves; the knowledge/traceability graph navigable with **zero orphans** (CEP-008 XI.2). Discharged by reference through `ukbx certify` domain 4 (Knowledge Graph) + `ukbx twin --check` C-08 navigation. USIS-016 owns the *knowledge-evidence contract*; the knowledge graph is owned by UMB-006 — referenced. Evidence and traceability records remain operational memory and never enter the constitutional corpus (CEP-008 XIX.3).

## PART U — Cross-layer evidence

Cross-layer evidence attests integrity of the evidence + traceability chain **across** the surfaces the mission enumerates — architecture (USIS-006…013/017), implementation (USIS-INT-001), runtime (USIS-013), registry (REG-AUTO-001), knowledge (UMB-006), governance (UCIC-001 / GOV instruments / CEP-008), validation (USIS-014), certification (USIS-015), Digital Twin (UMB-002), and **future UCOS universes** (USIS-002 reserved slots `USIS-U-FUT`/`USIS-U-UNK`). A subject is cross-layer-evidenced iff every artifact traces to its evidence chain, every evidence/traceability link resolves (zero orphans), the composite lineage + dependency graph remains acyclic, and no record contradicts another. Discharged by `ukbx certify` (10 domains, whole-corpus) + `ukb validate` (referential integrity + acyclicity).

## PART V — Evidence (constitutional) invariants & Failure model

**Invariants (fail-closed; verified in USIS-011 obligations; CEP-008 Article XXIII).**
1. Duplicate evidence store / competing evidence or traceability registry created by USIS-016: **0** (LAW USIS-02; CEP-008 XVI.2).
2. Hard-coded present-day technology/store/hash/vendor in this architecture: **0** (LAW USIS-04, obligation 1).
3. Orphan (unowned/unhomed) evidence layers or traceability orphans: **0** (No-Orphan; CEP-008 XI.2/XI.5).
4. Constitutional action/decision/state-transition of the substrate lacking evidence: **0** (CEP-008 V.1/V.5).
5. Modification of preserved evidence, or evidence identity reuse/reassignment: **0** (CEP-008 IX.2/IV.3).
6. Fabricated, backdated, or fictitious-action evidence: **0** (CEP-008 V.4).
7. Evidence lineage cycle or evidence dependency cycle: **0** (CEP-008 XII.2/XIII.2).
8. Inlined constitutional content in an evidence record (not referenced by identity): **0** (CEP-008 II.3/XIV.3).
9. Evidence/traceability jurisdiction overlapping validation/certification/ratification/freeze: **0** (CEP-008 II.5; Zero-Overlap).
10. USIS-016 edits to any frozen instrument or the executable substrate: **0** (obligation 19; `engine/**`,`platform/**`,`00-CEP/**` untouched — referenced).

Any nonzero ⇒ NOT CONSTITUTIONALLY CONFORMANT ⇒ HALTED (CEP-008 XX.2).

**Failure model (per UCIC-001 Output-4; CEP-008 Article XX).**
- An action lacking evidence, a fabricated/backdated record, an identity collision, a modification of preserved evidence, an illegal state transition, a traceability orphan, or a lineage/dependency cycle ⇒ **HALTED**, emit a finding, remediate before progression resumes (CEP-008 XX.2).
- Evidence failing verification ⇒ `REJECTED`; the action remains unsubstantiated until valid evidence is preserved (CEP-008 XVIII.4 / VI.7).
- A void evidence act has no effect and is recorded as void (CEP-008 XX.3).
- On boot, evidence/traceability state is reconciled against repository truth; repository truth prevails on divergence (CEP-008 XXI.1). Preserved evidence is **never** rolled back or deleted; correction is forward-only through successor evidence (XXI.3/XXI.5). Recovery is non-destructive and reproduces byte-identical evidence for an interrupted-then-resumed collection of an unchanged matter (XXI.4).

## PART W — Non-goals

- Authors **no** evidence record, collector, verifier, preservation store, audit log, or capability instance (Wave-3/5, per-member); those are produced by the referenced substrate at the time of the action.
- Is **not** `ukbx certify`/`ukbx twin`, the `00-BOOK/DATA` registers, or the `.runtime/governance` audit — all referenced.
- Does **not** govern, execute, validate, certify, ratify, freeze, or implement (CEP-008 II.2/XXII.3); it legislates no such outcome and defers each to its owning constitution (CEP-004/005/006/007) and tier (USIS-014/015).
- Confers **no** new governance authority and **no** FINALIZED standing (Part M); names **no** technology/store/hash/vendor (LAW USIS-04); creates **no** competing evidence or traceability registry (LAW USIS-02; CEP-008 XVI.2); produces **no** code; admits **no** unsubstantiated, un-provenanced, or mutable-after-preservation evidence (CEP-008 IX/X; Part F).
- Re-registers **no** repository structure specification and duplicates **no** CEP-008 content (reference-only; Knowledge-Once).

---

*END — USIS-016 · EVIDENCE ARCHITECTURE · registered corpus instantiation · RATIFIED (PROVISIONAL) · Wave 2 · AUTHORITY = NONE (DERIVED). Higher frozen/governing instruments prevail.*
