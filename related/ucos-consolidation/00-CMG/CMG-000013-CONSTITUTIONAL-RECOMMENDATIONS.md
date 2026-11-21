# UCOS Ω∞ — CMG CONSTITUTIONAL RECOMMENDATIONS

| Field | Value |
|-------|-------|
| ARTIFACT ID | CMG-000013 |
| ARTIFACT | UCOS Ω∞ CMG Constitutional Recommendations |
| CLASSIFICATION | Constitutional Meta Governance (CMG) — Recommendations |
| PHASE | PHASE-000 |
| PROGRAM | CMG |
| CATEGORY | CMG |
| VOLUME | VOL-002 |
| STATUS | UNDER REVIEW · DERIVED · NON-NORMATIVE |
| VERSION | 1.0 |
| AUTHORITY | NONE (DERIVED TRUTH) — recommendations bind nobody; each names the owner competent to act |
| GOVERNED-BY | CMG-000001 |
| DEPENDS-ON | CMG-000001 |
| CANONICAL FORM | This Markdown file |

> Derived recommendations. Every recommendation names the **owner competent to act**, because a recommendation addressed to nobody is an opinion (CMG-000001 XXIII.5).

---

## 1 — PRIORITY 1: THE TWO ACTS THAT CHANGE EVERYTHING

### R-01 — Identify the authority competent to ratify constitutional artifacts
**Owner:** the out-of-corpus finality authority, or an authority empowered to designate it.
**Closes:** `CMG-OQ-01`.

The corpus records that no ratification authority exists within the frozen corpus and that the identity of any out-of-corpus finality authority is undetermined. Consequently **nothing in the corpus can be ratified** — not CMG-000001, not the CEP instruments, not the domain constitutions. Every artifact operates provisionally, which is legally correct but permanently incomplete.

This is the single highest-leverage act available. It is also the one act that no artifact in the corpus can perform for itself, because self-ratification is prohibited (CMG-000001 XLIV.7).

### R-02 — Resolve Tier-1 occupancy, or ratify that it is permanently vacant
**Owner:** the same authority as R-01.
**Closes:** `CMG-OQ-02`, `VAC-01`.

The located charter declares itself subordinate to a ratified constitution of substance and places it at the top of its authority tiers. That referent exists in the repository only as frozen source material in binary document form — not as ratified normative law. The reference has therefore been dangling since the charter was written, and CMG-000001 is the first instrument to record it.

Two acceptable outcomes, and one unacceptable one:

| Outcome | Effect | Acceptable? |
|---|---|---|
| Designate an artifact (existing or new) as the T1 occupant | Standing lifts from PROVISIONAL across all 43 recognized artifacts at once | Yes |
| Ratify that T1 is permanently vacant, with a declared consequence for dependent standing | Standing remains provisional but is *ratified as such* rather than provisional by accident | Yes |
| Leave it unrecorded | Every determination in the corpus stays silently provisional | **No** — this is the pre-existing condition being corrected |

**Cost of R-02 is low and stays low only while standing remains a recorded fact rather than embedded text.** No artifact body changes when the vacancy closes (CMG-000008 §3.2). Had standing been written into each artifact, this act would require amending 43 artifacts.

---

## 2 — PRIORITY 2: CONFIRMATIONS BY LOCATED OWNERS

### R-03 — Confirm or reject the orthogonality of the meta and process axes
**Owner:** an authority above both axes (presently vacant — depends on R-01/R-02).
**Closes:** `CMG-OQ-03`.

CMG-000001 declares the recognition axis (T1M) **orthogonal** to the process axis (T2) rather than superior or subordinate. Orthogonality was chosen because ranking the axes would require an authority above both, and because the located charter forbids its own self-elevation while claiming supremacy over its own program.

If this determination is wrong, the correction is a MAJOR amendment to CMG-000001 Article XVI, not a reinterpretation. Until it is ratified, the lattice is provisional in exactly this one respect.

### R-04 — Acknowledge the new zone through the registration authority
**Owner:** the registration authority.
**Closes:** `CMG-OQ-06`.

Recognition of `00-CMG/` was achieved without editing any shared classification or registration configuration: the constitution and analyses resolve through an existing filename rule, the tools resolve through the total path-derived classifier, and every artifact additionally self-declares its program, category and volume. Whether the registration authority nonetheless requires a formal acknowledgement of a new zone is that authority's determination, not the meta layer's.

### R-05 — Confirm the four REQUIRES-REVIEW assertions
**Owners:** the stewards of `CEP-000`, `CEP-002`, `AUTH-INF-001`, `CONST-07`.

CMG-000001 makes a claim *about* each of these instruments without changing any of them. Each owner should confirm the claim rather than have it stand unexamined:

| Instrument | Claim to confirm |
|---|---|
| `CEP-000` | That the meta axis is orthogonal to Program Authority and does not encroach on process supremacy |
| `CEP-002` | That the precedence lattice contains, rather than replaces, the governance conflict ladder |
| `AUTH-INF-001` | That interpretive authority remains orthogonal and undiminished, and that the meta layer refers rather than interprets |
| `CONST-07` | That admission satisfies the "no competing authority, registry, governance, canonical store, traceability, or lifecycle" separation invariant |

### R-06 — Allocate ownership of the Deferral Register lifecycle — **IMPLEMENTED**
**Owner:** the authority competent to allocate governance ownership.
**Closes:** `CMG-OQ-04`, fully closes `CMG-GAP-02`. **Status: DONE (Wave-2 · Mission E-3)** — allocated to `CEP-002` Article 27 by `CEP-002-AMD-001`, enabled by `CEP-001-AMD-001`, recognized at CMG-000001 CMG-DLG-49 / LXXVIII.8.

A Deferral Register is referenced across multiple located instruments as the destination for out-of-scope discoveries and undecided matters, but no instrument defines its states, entry and exit conditions, review cadence, or owner. CMG-000001 recognizes it as a constitutional Kind and binds exceptions and deferrals to it, which is the limit of what recognition can do. Selecting the owner is an allocation and requires the allocating authority.

The natural candidates are the located governance constitution (which owns deferral *disposition*) and the located evolution constitution (which owns the change lifecycle). **Recommendation: extend the governance constitution**, on the ground that deferral disposition is already its concern and extension is preferred to creation (CMG-000001 XLI.7).

### R-07 — Allocate ownership of program-completion ceremony
**Owner:** the process owner.
**Closes:** `CMG-OQ-05`, `CMG-GAP-06`.

The located operational constitution defines a program COMPLETE state with an entry predicate but no instrument performs, records, or attests completion. This is a process concern and therefore outside the meta layer's jurisdiction entirely.

---

## 3 — PRIORITY 3: DETECTION AND HYGIENE

### R-08 — Run a latent-constitution detection pass
**Owner:** the audit owner.

CMG-000001 XII.5 now makes it a defect for an artifact to function as constitutional law without recognition, and LII.2 makes latency an audit condition. The *rule* is in force; the *enumeration* of artifacts currently latent requires a detection run across every artifact in the repository against the six conditions of IV.1.

**Expected findings, based on the discovery pass:** several artifacts declaring `AUTHORITY = NONE (DERIVED TRUTH)` while in practice being cited as governing constraints. Each will resolve either to recognition (it really is a constitution) or to explicit reclassification as DECLARATIVE (it really asserts nothing). Both outcomes are improvements; the present ambiguity is the defect.

### R-09 — Add the meta gate to the canonical verification chain
**Owner:** the enforcement-machinery owner.

The `cmg-gate` target exists and passes, but it is not yet part of the repository's canonical `verify` chain, so nothing forces it to run. Two options:

| Option | Effect | Recommendation |
|---|---|---|
| Add `cmg-gate` as a stage of the canonical verification entry point | The meta layer is enforced on every verification | Preferred |
| Add `cmg-gate` to the CI workflow only | Enforced on CI but skippable locally | Acceptable fallback |

This change was deliberately **not** made here: modifying the canonical verification chain alters the behaviour of an existing gate owned by another party, which exceeds what admission may do unilaterally (CMG-000001 LVIII.5). The additive `cmg-gate` target was added; wiring it into `verify` is the machinery owner's call.

### R-10 — Do not extend the meta invariants corpus-wide without a migration plan
**Owner:** whoever decides `CMG-OQ-07`.

Adopting `CMG-INV-01` … `CMG-INV-12` as corpus-wide obligations is attractive and would make every constitutional artifact mechanically checkable. It is also a MAJOR change that imposes new obligations on artifacts owned elsewhere and could invalidate conforming artifacts. If pursued, follow the plan in CMG-000008 §3.1: enumerate non-conformances first, sequence remediation shallowest-dependency-first, and remediate each artifact through its own amendment path — never by editing another owner's artifact.

**Recommendation: do not pursue this until R-01 and R-02 are closed.** Imposing corpus-wide invariants while every artifact's standing is provisional would enforce obligations derived from an unratified instrument.

---

## 4 — STANDING GUIDANCE

Four practices that should outlive this document:

| # | Practice | Rationale |
|---|---|---|
| G-1 | Before creating any constitutional artifact, record the reuse discovery: which existing owners were examined and why each was insufficient | CMG-000001 XL.5. Creation without a recorded discovery is how parallel authority arrives |
| G-2 | Keep the meta layer's retained-concern count low; treat growth in the ratio as a warning | CMG-P-15. Eleven of fifty-nine today. A meta layer that absorbs the domains it allocates becomes the parallel authority it was built to prevent |
| G-3 | Never resolve a constitutional conflict by rank before testing for jurisdiction error | CMG-000001 LIV.3. Resolving an overreach by precedence *ratifies the overreach* |
| G-4 | Re-run the meta gate on every change to any constitutional artifact, registry, delegation, or namespace, and treat its output as the completeness evidence | CMG-000001 LXXIX.5. A completeness claim is valid only for the repository state that produced it |

---

## 5 — WHAT NOT TO DO

| Do not | Why |
|---|---|
| Promote a located artifact into Tier T1 to close the vacancy conveniently | Self-elevation by proxy (CMG-000001 XVII.4, CMG-L-04). The vacancy must be closed by an authority, not by a nomination |
| Treat `READY-PROVISIONAL` as `READY` | The ceiling is declared in law and enforced by the tool precisely to prevent this drift |
| Freeze CMG-000001 to make it feel settled | Freezing preserves standing; it does not confer it (CMG-000001 XXVI.4, `CMG-T-09`). A frozen provisional artifact is still provisional |
| Expand CMG-000001's jurisdiction by amendment to cover a new concern | Prohibited (XLIII.4, XIX.4). A new meta concern becomes a new artifact in the `CMG` namespace |
| Edit shared classification or enforcement configuration to accommodate future zones | A hard-coded enumeration in the sense CMG-L-08 prohibits. Metadata self-declaration and the total classifier already handle it |
| Maintain a hand-written traceability matrix for constitutional relationships | A second source of truth that will drift (CMG-000001 XXXVII.2) |
