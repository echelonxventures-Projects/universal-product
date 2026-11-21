# UCOS Ω∞ CONSTITUTIONAL REMEDIATION PACKAGE

Phase 6 — Remediation Analysis (analytical only; nothing implemented)

Inputs (read-only):
- `00-SOURCE/` (frozen corpus; not modified)
- `99-FREEZE/` (source freeze; not modified)
- `01-WORKING/AUTHORITY-REGISTER.md`
- `01-WORKING/SUPERSESSION-REGISTER.md`
- `01-WORKING/LAW-REGISTER.md`
- `02-MASTER/UCOS-Ω∞-CONSTITUTIONAL-RATIFICATION-REPORT.md` (Phase 2)
- `02-MASTER/UCOS-Ω∞-CONSTITUTIONAL-ADJUDICATION-RECORD.md` (Phase 3)
- `02-MASTER/UCOS-Ω∞-CONSTITUTIONAL-DECISION-REGISTER.md` (Phase 4)
- `02-MASTER/UCOS-Ω∞-CONSTITUTIONAL-GOVERNANCE-GAP-REPORT.md` (Phase 5)

Output (this file only): `02-MASTER/UCOS-Ω∞-CONSTITUTIONAL-REMEDIATION-PACKAGE.md`

## SCOPE DISCIPLINE (READ FIRST)

- This package is **analytical only.** It determines the **minimum constitutional capabilities** that would have to exist to eliminate the governance deadlock — it does **not** implement, author, or instantiate any of them.
- For every gap it identifies **what must exist**, **why it must exist**, and **which constitutional functions depend on it** — as capability *requirements*, never as designs, text, procedures, or bodies.
- **"Candidate Constitutional Amendment Type"** names the *category* of change that would be needed. It is a classification label, not an amendment. No amendment is drafted, proposed, or enacted here.
- Explicit prohibitions honored throughout: no constitution, no amendments, no governance bodies, no voting mechanisms, no ratification authority, no sovereign body, no procedures are generated. `00-SOURCE/` and `99-FREEZE/` are untouched.
- Identifiers (`SRC-*`, `AUTH-*`, `GOV-*`, `SUP-*`, `DUP-*`, `LAW-*`, `CM-*`, `INV*`, `CONF-*`, `RAT-*`, `DR-RAT-*`, `GAP-*`) are used exactly as defined in the cited registers and reports.

---

## AMENDMENT-TYPE TAXONOMY (labels used below; none are authored)

| Type code | Type name | Meaning (classification only) |
|-----------|-----------|-------------------------------|
| AT-CONST | Constitutive (organ/seat-establishing) | Would bring a currently-absent constitutional organ or seat into existence. Requires an originating (constituent) act. |
| AT-PROC | Procedural | Would supply an operative procedure/decision-rule for an already-named function. |
| AT-META | Meta-procedural (self-amendment) | Would supply the rules by which the corpus is itself amended. |
| AT-PREC | Interpretive / precedence | Would supply a conflict-resolution or seniority rule reconciling co-equal claims. |
| AT-DEF | Definitional | Would supply the operative definition of a term the corpus uses but leaves undefined. |
| AT-ENTR | Entrenchment reconciliation | Would reconcile a self-declared-immutable clause with the (absent) authority competent to entrench it. |

> These labels identify the *kind* of remediation each gap needs so the required capability can be scoped. They do not constitute drafting.

---

## SECTION 1 — REMEDIATION SCOPE

**In scope.** Identifying, per gap GAP-01…GAP-08, the minimal capability whose *existence* (not implementation) would lift the corresponding block; the amendment *type* that capability implies; the dependency ordering among capabilities; and the residual conditions for constitutional synthesis.

**Out of scope (by mandate).** Designing, drafting, staffing, or enacting any body, seat, procedure, decision-rule, definition, or amendment; resolving the substantive RAT adjudications (already fixed in Phase 3); modifying any source.

**Fixed premises carried from prior phases.**
1. Every substantive constitutional conflict (RAT-01…RAT-10) already has a **governing position selected from existing source material** (Phase 3 / Phase 4). No new substantive content is required for synthesis — only the governance machinery to ratify it.
2. RAT-11 is **BLOCKED** — "No ratification authority exists within the frozen constitutional corpus" (`DR-RAT-11`).
3. Phase 5 established that of 9 capabilities required to ratify, **1 is PRESENT** (the *obligation* to ratify), **4 REFERENCED-ONLY**, **4 ABSENT**.
4. The corpus's own rules forbid self-authorizing the first ratifier: INVARIANT Ω-010 "Ratification Before Structural Change" (LAW-INV02), reinforced by **LAW CM-007 "Every Constitutional Change Must Be Ratifiable"**, and AUTH-06 "sovereignty cannot be assumed, fabricated, or bypassed."

**Consequence for scope.** Remediation is therefore **governance-capability remediation, not content remediation.** The deadlock is dissolved by supplying (out-of-corpus) a minimal set of governance capabilities, after which the already-adjudicated positions can be ratified.

---

## SECTION 2 — GOVERNANCE GAP CLOSURE MATRIX

| Gap | Missing capability (minimal) | Amendment type | Closure tier | Blocks (decisions) | Risk |
|-----|------------------------------|----------------|--------------|--------------------|------|
| GAP-01 | An empowered ratification organ (existence of) | AT-CONST | Tier-0 (foundational) | RAT-11 → all RAT-01..10 | CRITICAL |
| GAP-04 | A supremacy/conflict tie-break rule | AT-PREC | Tier-0 (foundational) | RAT-11, RAT-01/02/03 | CRITICAL |
| GAP-05 | An identified sovereign seat / ratifier eligibility | AT-CONST | Tier-0 (foundational) | RAT-11, RAT-05 | CRITICAL |
| GAP-02 | A ratification decision rule (quorum + threshold) | AT-PROC | Tier-1 (enabling) | all RAT (validity of any act) | HIGH |
| GAP-03 | A self-amendment procedure | AT-META | Tier-1 (enabling) | RAT-07, all future evolution | HIGH |
| GAP-07 | A ratification audit/evidence procedure | AT-PROC | Tier-2 (integrity) | all RAT (trust under LAW-INV02) | MEDIUM-HIGH |
| GAP-06 | A definition of "structural change" | AT-DEF | Tier-2 (integrity) | RAT-07 finalization | MEDIUM |
| GAP-08 | An entrenchment/immutability reconciliation | AT-ENTR | Tier-2 (integrity) | RAT-04 finalization | MEDIUM |

**Tiering.** Tier-0 capabilities are *foundational* — nothing ratifies without them and each requires an originating act external to the corpus. Tier-1 are *enabling* — they make a ratification act *valid and repeatable* once Tier-0 exists. Tier-2 are *integrity* — they make a ratification act *trustworthy, bounded, and coherent* with the corpus's own invariants.

---

## SECTION 3 — CONSTITUTIONAL AMENDMENT REQUIREMENT REGISTER

> For each gap: Gap ID · Root Cause · Blocking Effect · Constitutional Impact · Minimal Required Capability (with What must exist / Why it must exist / Dependent constitutional functions) · Candidate Constitutional Amendment Type · Dependency Analysis · Risk Assessment · Closure Condition. **Capabilities are identified, not created.**

### GAP-01 — No Ratification Authority / Body

- **Root Cause:** The corpus names ratification as a governance *function* (GOV-03) and a Meta-Constitution *scope heading* (AUTH-10) but never constitutes an organ to exercise it. Obligation without organ.
- **Blocking Effect:** No entity can convert any adjudicated position into a ratified one; the entire Decision Register is frozen at provisional status.
- **Constitutional Impact:** Total — RAT-11 keystone cannot resolve; RAT-01…RAT-10 remain non-final by dependency.
- **Minimal Required Capability:**
  - *What must exist:* a constitutional organ empowered to perform ratification (its existence and empowerment — not its composition, which this report does not design).
  - *Why it must exist:* every downstream obligation (Ω-010, CM-007, BOOK IV "ratifiable," BOOK IX "requires ratification") presupposes an actor competent to ratify; none is named.
  - *Dependent constitutional functions:* ratification (GOV-03), evolution gating (GOV-07/RAT-07), amendment (AUTH-10), supremacy determination (RAT-11), and the "ratifiable/auditable" qualities of governance (GOV-04, CM-005, CM-007).
- **Candidate Constitutional Amendment Type:** **AT-CONST** (constitutive; requires an originating constituent act external to the corpus).
- **Dependency Analysis:** Depends on GAP-05 (a sovereign seat must exist to *empower* the organ) and GAP-04 (the organ must know which document's rules it operates under). Gates GAP-02 (a decision rule is meaningless without a body to apply it).
- **Risk Assessment:** **CRITICAL.** Keystone-of-keystones; no internal workaround (see Section 5 deadlock).
- **Closure Condition:** An empowered ratification organ exists and is traceable to a legitimate sovereign source.

### GAP-04 — No Supremacy / Conflict-Resolution Tie-Break

- **Root Cause:** Two documents self-declare supremacy (DUP-07; AUTH-11 "⚠ dual-claimed"); SUP-14 is **UNRESOLVED**; AUTH-10 lists "Conflict Resolution" as a heading with no operative rule.
- **Blocking Effect:** The seniority underpinning the whole precedence order is unsettled; the working "SRC-02 senior *pro tempore*" is explicitly non-binding.
- **Constitutional Impact:** High and structural — if SRC-01 were senior, RAT-02/RAT-03 flip from 4-primitive to 5-primitive and the LAW Ω∞ numbering baseline changes (LAW-R04 vs LAW-R01/R05).
- **Minimal Required Capability:**
  - *What must exist:* an operative precedence/tie-break rule capable of resolving co-equal supremacy claims.
  - *Why it must exist:* no determination that names an "authoritative source" is binding while two sources hold mutually exclusive supremacy clauses; AUTH-11 cannot be closed without it.
  - *Dependent constitutional functions:* supremacy determination (RAT-11), ontology chain finalization (RAT-01/02/03), law-identifier baseline (RAT-08/09), and any rule invoking "the Constitution" (AUTHCLAIM-03).
- **Candidate Constitutional Amendment Type:** **AT-PREC** (interpretive/precedence).
- **Dependency Analysis:** Co-foundational with GAP-01/GAP-05; the tie-break must be issued *by* the empowered organ (GAP-01) under the sovereign seat (GAP-05), yet the organ must operate under *a* precedence to exist — a co-dependency addressed in Section 5.
- **Risk Assessment:** **CRITICAL.** A wrong or unmade call silently reclassifies the ontology and law canon.
- **Closure Condition:** A single, authorized precedence rule fixes document seniority (resolving SUP-14 / CONF-07).

### GAP-05 — No Identified Sovereign Seat / Ratifier Eligibility

- **Root Cause:** The corpus asserts sovereignty as the source of authority (AUTH-02; BOOK II) and forbids fabricating it (AUTH-06) but never identifies the holder of sovereignty. The only origin doctrine (AUTH-12/GOV-10, SRC-08) is advisory-superseded (SUP-05).
- **Blocking Effect:** No party may legitimately convene or empower a ratifier, because sovereignty "cannot be assumed, fabricated, or bypassed."
- **Constitutional Impact:** Total — the empowerment chain for GAP-01 has no root; RAT-05 (sovereignty origin) cannot be finalized.
- **Minimal Required Capability:**
  - *What must exist:* an identified, legitimate sovereign seat from which ratification authority can be derived, and criteria for ratifier eligibility.
  - *Why it must exist:* AUTH-03 makes all authority derive from sovereignty; without a named sovereign, every derived authority (including the ratifier) is ungrounded, and AUTH-06 blocks improvisation.
  - *Dependent constitutional functions:* sovereignty model (AUTH-02/06), authority derivation chain (AUTH-03), ratifier empowerment (GAP-01), sovereignty-origin decision (RAT-05).
- **Candidate Constitutional Amendment Type:** **AT-CONST** (constitutive; the originating/constituent act).
- **Dependency Analysis:** Root of the empowerment chain — GAP-01 and GAP-02 depend on it. Independent of the ontology/identifier gaps.
- **Risk Assessment:** **CRITICAL.** AUTH-06 actively forecloses an internal fix; this is the true origin of the deadlock.
- **Closure Condition:** A legitimate sovereign seat is identified and ratifier eligibility is derivable from it.

### GAP-02 — No Quorum / Voting Threshold

- **Root Cause:** GOV-03 lists "Voting"/"Deliberation" as functions but no decision rule (quorum, majority, supermajority, unanimity) is defined anywhere.
- **Blocking Effect:** Even with an organ (GAP-01), any determination would be of undefined validity.
- **Constitutional Impact:** Broad — every RAT ratification act would be procedurally ungrounded and contestable.
- **Minimal Required Capability:**
  - *What must exist:* an operative decision rule binding ratification outcomes to a defined threshold.
  - *Why it must exist:* GOV-04 requires governance be "enforceable" and CM-005 "auditable"; an outcome with no threshold is neither.
  - *Dependent constitutional functions:* all ratification acts (RAT-01…RAT-11), enforceability (GOV-04), auditability (CM-005).
- **Candidate Constitutional Amendment Type:** **AT-PROC** (procedural).
- **Dependency Analysis:** Depends on GAP-01 (a body to which the rule applies) and GAP-05 (legitimacy of the body). Enables GAP-07 (an audit needs a defined outcome to record).
- **Risk Assessment:** **HIGH.** Not foundational but renders any act binding vs. contestable.
- **Closure Condition:** A defined quorum + threshold governs ratification outcomes.

### GAP-03 — No Amendment Procedure

- **Root Cause:** AUTH-10 names "Amendment Rules"; CM-007 requires "Every Constitutional Change Must Be Ratifiable"; but no operative amendment pathway exists.
- **Blocking Effect:** The corpus cannot lawfully change after (or in order to enable) ratification; the tiered evolution model (RAT-07) has no structural pathway.
- **Constitutional Impact:** Permanent-freeze risk — even a successful first ratification could not be lawfully revised.
- **Minimal Required Capability:**
  - *What must exist:* a self-amendment procedure (the rules by which the corpus is changed).
  - *Why it must exist:* CM-007 and BOOK IX make ratifiability of change constitutional; without an amendment path the requirement is unsatisfiable, and RAT-07's structural branch is inert.
  - *Dependent constitutional functions:* evolution gate (RAT-07/GOV-07), constitutional-change ratifiability (CM-007), BOOK IX evolution law.
- **Candidate Constitutional Amendment Type:** **AT-META** (meta-procedural / self-amendment).
- **Dependency Analysis:** Depends on GAP-01/GAP-02 (a body + decision rule to run the procedure). Interlocks with GAP-08 (entrenchment limits what may be amended).
- **Risk Assessment:** **HIGH.** Non-blocking for the *first* act but blocks all lawful evolution thereafter.
- **Closure Condition:** A ratifiable amendment procedure exists and bounds future constitutional change.

### GAP-07 — No Ratification Audit / Evidence Procedure

- **Root Cause:** GOV-03/GOV-04 require governance be "auditable"; LAW-INV02 mandates "Audit Before Trust"; CM-005 "Every Governance Action Must Be Auditable" — but no procedure records/evidences a ratification act.
- **Blocking Effect:** A ratification produced without an audit trail fails the corpus's own trust invariant, rendering it untrusted even if procedurally attempted.
- **Constitutional Impact:** Converts nominal ratification into constitutionally-untrusted ratification (LAW-INV02 "Audit Before Trust"; LAW-AX03 "Verification Produces Trust → Trust Enables Governance").
- **Minimal Required Capability:**
  - *What must exist:* a ratification audit/evidence capability recording each act and its basis.
  - *Why it must exist:* "Audit Before Trust" (LAW-INV02) and the AX03 trust chain make an unauditable act non-trustworthy and therefore constitutionally inert.
  - *Dependent constitutional functions:* trust/verification (LAW-AX03), auditability (GOV-04, CM-005), evidentiary basis of every RAT act.
- **Candidate Constitutional Amendment Type:** **AT-PROC** (procedural).
- **Dependency Analysis:** Depends on GAP-01/GAP-02 (there must be an act, with a defined outcome, to audit). Enables trust for all RAT items.
- **Risk Assessment:** **MEDIUM-HIGH.** Determines whether ratification is *trusted*, not merely *made*.
- **Closure Condition:** Every ratification act is recorded and auditable, satisfying "Audit Before Trust."

### GAP-06 — No Definition of "Structural Change"

- **Root Cause:** INVARIANT Ω-010 gates "Structural Change" on ratification, and LAW Ω∞-018 gates evolution on governance, but "structural" vs "routine" is never enumerated.
- **Blocking Effect:** The tiered evolution gate (RAT-07) cannot be applied — any change is classifiable either way.
- **Constitutional Impact:** RAT-07 cannot be finalized; the routine/structural boundary that makes SRC-02 self-consistent stays undefined.
- **Minimal Required Capability:**
  - *What must exist:* an operative definition distinguishing structural from routine change.
  - *Why it must exist:* the two gate-laws (Ω-010 ratification vs Ω∞-018 governance) are only reconcilable if the boundary between them is defined; otherwise the tier is meaningless.
  - *Dependent constitutional functions:* evolution gate (RAT-07), which pathway (governance vs ratification) applies, and thus when GAP-01/02 machinery must engage.
- **Candidate Constitutional Amendment Type:** **AT-DEF** (definitional).
- **Dependency Analysis:** Depends on GAP-01 (only an empowered body may fix the definition authoritatively). Downstream of the foundational tier.
- **Risk Assessment:** **MEDIUM.** Definitional; resolvable quickly once a ratifier exists.
- **Closure Condition:** "Structural change" is authoritatively defined and the RAT-07 tier is operable.

### GAP-08 — No Entrenchment / Immutability Reconciliation

- **Root Cause:** LAW-INV02 declares itself "immutable / non-amendable" (SUP-06) yet was never ratified — a set claiming entrenchment without an entrenching authority.
- **Blocking Effect:** The invariant base cannot be finalized: if binding, it pre-empts ratification; if not, its immutability is void (the RAT-04 paradox).
- **Constitutional Impact:** RAT-04 cannot be finalized, including the residual LAW-INV01↔INV02 ordering divergence.
- **Minimal Required Capability:**
  - *What must exist:* an entrenchment-reconciliation capability able to rule on the status of a self-declared-immutable, unratified set.
  - *Why it must exist:* only an authority competent to entrench (or decline to entrench) can dissolve the "immutable-but-unratified" paradox; the corpus supplies none.
  - *Dependent constitutional functions:* invariant-set finalization (RAT-04), amendment scope (GAP-03), and the standing of LAW-INV02 as a constraint on everything below it.
- **Candidate Constitutional Amendment Type:** **AT-ENTR** (entrenchment reconciliation).
- **Dependency Analysis:** Depends on GAP-01 (ruling authority) and interlocks with GAP-03 (entrenchment bounds amendment scope).
- **Risk Assessment:** **MEDIUM.** Isolated to the invariant layer but logically paradoxical until ruled.
- **Closure Condition:** The immutable-but-unratified paradox is authoritatively reconciled and RAT-04's residual ordering is selectable.

---

## SECTION 4 — DEPENDENCY RESOLUTION MODEL

Resolution order is dictated by the tiering in Section 2. Capabilities cannot be supplied in arbitrary order.

```
        [ EXOGENOUS CONSTITUENT ACT ]   ← out-of-corpus; not created here
                     │
   TIER-0  ──────────┼───────────────────────────────
   (foundational)    ▼
              GAP-05 sovereign seat  ──────┐
                     │                     │ (empowers)
                     ▼                     ▼
              GAP-01 ratification organ ── GAP-04 precedence/tie-break
                     │        (co-dependent: organ needs a precedence to
                     │         operate; precedence is issued by the organ —
                     │         resolved only by the exogenous act, §5)
   TIER-1  ──────────┼───────────────────────────────
   (enabling)        ▼
              GAP-02 decision rule ──► GAP-03 amendment procedure
   TIER-2  ──────────┼───────────────────────────────
   (integrity)       ▼
              GAP-07 audit  │  GAP-06 "structural" def  │  GAP-08 entrenchment
                     │              │                        │
                     ▼              ▼                        ▼
              trust for      RAT-07 finalizable        RAT-04 finalizable
              all RAT acts
                     │
                     ▼
              RAT-11 ratifiable ──► RAT-01/02/03 ──► RAT-05/06 ──► RAT-08/09/10
                     │
                     ▼
              CONSTITUTIONAL SYNTHESIS POSSIBLE (positions already selected in Phase 3)
```

**Reading.** Everything is rooted in a single exogenous constituent act (Section 5). Tier-0 must exist before Tier-1 can be valid; Tier-1 before Tier-2 can operate; only then does RAT-11 become ratifiable, unblocking the already-adjudicated substantive decisions. Note the Tier-0 **co-dependency** between GAP-01 and GAP-04 (the organ needs a precedence to know its own charter; the precedence is normally issued by the organ) — this circularity is the deadlock's second face and is only breakable exogenously.

---

## SECTION 5 — GOVERNANCE BOOTSTRAPPING ANALYSIS

The deadlock is a **constituent-power problem**, not a content problem.

1. **The self-reference.** INVARIANT Ω-010 (immutable) requires "Ratification Before Structural Change." **LAW CM-007** requires "Every Constitutional Change Must Be Ratifiable." Constituting the ratifier (GAP-01) and naming the sovereign (GAP-05) are themselves structural constitutional changes. Therefore the corpus demands that its own founding governance act be ratified by a governance actor that the same act is supposed to create. The rule that would authorize the first step presupposes the step already taken.

2. **The empowerment vacuum.** AUTH-03 makes all authority derive from sovereignty; AUTH-06 forbids sovereignty being "assumed, fabricated, or bypassed." So the derivation chain that would empower a ratifier has **no legitimate root inside the corpus**, and the corpus prohibits inventing one.

3. **The trust chain cannot start.** LAW-AX03: "Verification Produces Trust → Trust Enables Governance → Governance Enables Civilization." LAW-INV02: "Audit Before Trust." With no ratification act to verify/audit (GAP-07), the trust chain has no first link, so governance legitimacy cannot accrue internally.

4. **The precedence circularity.** The organ (GAP-01) needs a supremacy rule (GAP-04) to know which document charters it; the supremacy rule is the kind of determination an organ issues. Neither can go first from inside the corpus.

**Bootstrapping conclusion.** These are the classic marks of a system that possesses **constituted power** (rules for operating) but lacks **constituent power** (the originating authority that brings the rule-appliers into being). Constituent power, by definition, sits *outside* the constituted order. The remediation therefore cannot be internal: it requires a **single exogenous constituent act** that (a) identifies the sovereign seat, (b) empowers a ratification organ, and (c) fixes the operating precedence — simultaneously, so none of the three has to pre-exist the others. This report **identifies** the necessity of that act; it does **not** perform it, design it, or name its actors.

---

## SECTION 6 — CONSTITUTIONAL CLOSURE PATH

The minimal ordered path from the current deadlock to a synthesizable foundation (capabilities only; each step is an out-of-corpus prerequisite, not an action taken here):

- **Step 0 — Exogenous constituent act (precondition).** A legitimate originating act external to the corpus supplies the Tier-0 triad together (GAP-05 sovereign seat + GAP-01 ratification organ + GAP-04 precedence rule), breaking the circularity of Section 5.
- **Step 1 — Enable valid acts (Tier-1).** A decision rule (GAP-02) makes ratification outcomes binding; a self-amendment procedure (GAP-03) makes future change lawful (satisfying CM-007).
- **Step 2 — Make acts trustworthy and coherent (Tier-2).** An audit/evidence capability (GAP-07) satisfies "Audit Before Trust"; a "structural change" definition (GAP-06) operationalizes RAT-07; an entrenchment reconciliation (GAP-08) resolves the LAW-INV02 paradox for RAT-04.
- **Step 3 — Ratify the keystone.** With Tier-0/1/2 present, RAT-11 becomes ratifiable: document supremacy is fixed (resolving SUP-14/CONF-07) and the ratifier is legitimate.
- **Step 4 — Ratify the adjudicated substance.** RAT-01/02/03 (ontology), RAT-05/06 (sovereignty/authority stack), RAT-08/09/10 (identifiers), and RAT-04/07 move from ADJUDICATED to ratified — using the positions **already selected in Phase 3**; no new substantive content is introduced.
- **Step 5 — Synthesis becomes possible.** Only after Steps 0–4 may a consolidated constitutional artifact be produced (a later phase, not this one), carrying the ratifier's identity and supremacy determination as its precondition header.

**Residual conditions surviving the path.** (i) RAT-04's INV01↔INV02 ordering divergence still needs a ratifier's selection — resolvable once a ratifier exists. (ii) Corpus-completeness caveats persist: SRC-11 extracted empty (Ratification Report N-1) and SRC-08 carries excluded credentials (N-2); neither is fixable under the freeze and both must be acknowledged in any synthesis precondition.

---

## SECTION 7 — MINIMAL VIABLE RATIFICATION ARCHITECTURE (capabilities only)

The smallest set of *capabilities* whose co-existence would make ratification possible. This is a **capability requirement stack**, not a design; nothing here is instantiated.

| Layer | Capability that must exist | Satisfies gap | Corpus hook it discharges |
|-------|----------------------------|---------------|---------------------------|
| L0 — Constituent root | An identified legitimate sovereign seat | GAP-05 | AUTH-02/03/06 |
| L0 — Constituent root | An empowered ratification organ | GAP-01 | GOV-03, AUTH-10, Ω-010 |
| L0 — Constituent root | An authoritative document-precedence rule | GAP-04 | SUP-14, AUTH-11, CONF-07 |
| L1 — Decision validity | A binding decision rule (quorum + threshold) | GAP-02 | GOV-04, CM-005 |
| L1 — Change lawfulness | A ratifiable self-amendment procedure | GAP-03 | CM-007, BOOK IX |
| L2 — Trust | A ratification audit/evidence capability | GAP-07 | LAW-INV02 "Audit Before Trust", AX03 |
| L2 — Boundary | A definition of "structural change" | GAP-06 | Ω-010, LAW Ω∞-018 |
| L2 — Coherence | An entrenchment reconciliation capability | GAP-08 | LAW-INV02 immutability, SUP-06 |

**Minimality argument.** Remove any L0 capability and the deadlock persists (no legitimate ratifier). Remove any L1 capability and ratification is non-binding or non-repeatable. Remove any L2 capability and a specific decision (RAT-04, RAT-07) or the trust basis of all decisions remains open. Nothing in the stack is substantive constitutional content — all substantive positions already exist (Phase 3). Hence this is the *minimum viable* set: eight capabilities across three layers, all governance, none of which this report supplies.

---

## SECTION 8 — READINESS REASSESSMENT

### A. Current Corpus Readiness

**NOT READY.** Of the 9 capabilities required to ratify, only the *obligation* to ratify is present; the ratification organ, sovereign seat, precedence rule, decision rule, amendment procedure, audit procedure, "structural" definition, and entrenchment reconciliation are ABSENT or REFERENCED-ONLY (Phase 5 matrix). `DR-RAT-11` is BLOCKED; all RAT-01…RAT-10 are non-final. The corpus cannot self-remediate (Section 5 deadlock). Readiness score: **0 of 8 remediation capabilities present; keystone blocked.**

### B. Readiness After Gap Closure

**READY (conditional).** If — and only if — the eight capabilities of Section 7 are supplied by the exogenous constituent act (Section 5) and Tier-1/Tier-2 capabilities, then: RAT-11 becomes ratifiable; SUP-14/CONF-07 resolves; and RAT-01…RAT-10 can be ratified using positions **already selected in Phase 3**. No further substantive adjudication is required. Readiness after closure: **all blocking dependencies satisfied; keystone ratifiable; substance pre-adjudicated.**

### C. Conditions Required For Constitutional Synthesis

1. **C-1:** An exogenous constituent act supplies the Tier-0 triad (sovereign seat + ratification organ + precedence rule) — breaking the Section 5 circularity.
2. **C-2:** Tier-1 capabilities exist (binding decision rule; ratifiable amendment procedure) satisfying GOV-04 and CM-007.
3. **C-3:** Tier-2 capabilities exist (audit/evidence; "structural" definition; entrenchment reconciliation) satisfying "Audit Before Trust", RAT-07, and the RAT-04 paradox.
4. **C-4:** RAT-11 is ratified (document supremacy fixed; SUP-14/CONF-07 closed), then RAT-01…RAT-10 ratified from their Phase-3 positions.
5. **C-5:** RAT-04's residual INV01↔INV02 ordering is selected by the now-existing ratifier.
6. **C-6:** Corpus-completeness caveats (SRC-11 empty; SRC-08 excluded credentials) are formally acknowledged as freeze-bound limitations in the synthesis precondition.

### Determination

**Question:** Can a Constitutional Foundation be synthesized after all identified gaps are closed?

## ANSWER: **YES** (conditional on out-of-corpus closure)

**Evidence:**

1. **The remaining blockers are exclusively governance-capability absences, not substantive conflicts.** Phase 3 already selected a governing position for every substantive item (RAT-01…RAT-10) from existing source material, and Phase 4 recorded each as ADJUDICATED. Once GAP-01…GAP-08 are closed, nothing substantive remains to invent.
2. **Every gap has an identified minimal capability and a defined closure condition** (Section 3); collectively they form a finite, minimal, layered set (Section 7) with a determinate resolution order (Section 4).
3. **The keystone unblocks by construction.** Closing GAP-05/GAP-01/GAP-04 makes a legitimate ratifier exist and fixes supremacy — the exact two conditions on which `DR-RAT-11` was BLOCKED — so RAT-11 becomes ratifiable, and its dependents follow.
4. **No corpus rule prevents synthesis *after* closure.** The only rules that currently block (Ω-010, CM-007, AUTH-06) are *satisfied*, not violated, once the exogenous constituent act and the capability stack exist.

**Qualification (why the YES is conditional, not unconditional).** The closure itself is **not achievable from within the frozen corpus** (Phase 5 = NO; Section 5 deadlock). The affirmative answer holds *only after* an exogenous constituent act supplies the Tier-0 capabilities. This report **identifies** that act as the necessary and sufficient precondition; consistent with its mandate, it does **not** perform, design, or populate it. Residual conditions C-5 and C-6 remain, but both are resolvable once a ratifier exists and neither reintroduces a deadlock.

---

## CLOSING ATTESTATION

- Minimum constitutional changes to eliminate the deadlock were **determined, not implemented**: for each gap GAP-01…GAP-08 the report states Root Cause, Blocking Effect, Constitutional Impact, Minimal Required Capability (What must exist / Why / dependent functions), Candidate Amendment Type, Dependency Analysis, Risk Assessment, and Closure Condition.
- All eight required sections produced: Remediation Scope (1), Governance Gap Closure Matrix (2), Constitutional Amendment Requirement Register (3), Dependency Resolution Model (4), Governance Bootstrapping Analysis (5), Constitutional Closure Path (6), Minimal Viable Ratification Architecture (7), Readiness Reassessment (8).
- Readiness Reassessment answered: **A. NOT READY · B. READY (conditional) · C. six conditions C-1…C-6**; synthesis after closure = **YES**, conditional on an out-of-corpus constituent act, with evidence.
- **No constitution generated. No amendments generated or drafted. No governance body, voting mechanism, ratification authority, sovereign body, or procedure was created. Only minimum required capabilities were identified.** `00-SOURCE/` and `99-FREEZE/` untouched.
- This remediation package is the sole Phase-6 output. Processing stops here.
