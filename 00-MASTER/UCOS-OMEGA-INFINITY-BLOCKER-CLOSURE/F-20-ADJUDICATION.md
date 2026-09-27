# F-20 Adjudication — the UREE admission contradiction

| Field | Value |
|---|---|
| ARTIFACT | `UCOS-OMEGA-INFINITY-BLOCKER-CLOSURE/F-20-ADJUDICATION.md` |
| PURPOSE | Resolve the F-20 contradiction on evidence |
| AUTHORITY | **NONE — DERIVED TRUTH.** Reads existing instruments; creates no authority, no programme, no identifier |
| RESOLVES | **S-5 / F-20** — BC-4 dependency, R-55 |
| METHOD | Evidence adjudication, not constitutional conferral |

---

## 1. The contradiction, as stated

Two determinations disagree on whether the Article 28 block exists, in the specific form of
**UREE admission**:

| Side | Determination | Claim |
|---|---|---|
| **A** | `CAPABILITY-REUSE-ANALYSIS-DETERMINATION.md` §5.2 | **New capability required.** UREE is a distinct concern — *requirement evolution* (discovery → admission → certification) — with distinct scope vs. existing programmes |
| **B** | `UKAP-UREE-CAPABILITY-ADMISSION-REASSESSMENT-DETERMINATION.md` | **Already operational.** Requirement evolution is live within ACEE-000001, UCKP vocabularies and UCDA. *"Phase 3 blocked status was a misdiagnosis."* |

R-55 forbids proceeding under *"already operational"* while the contradiction is live. So the
contradiction must be resolved, not chosen between.

---

## 2. The evidence, measured

Each of Side B's three cited hosts was tested for whether it actually evolves requirements.

| Claimed host | Test | Result |
|---|---|---|
| `ACEE-000001` | does it mention requirements? | **0 occurrences of "requirement"** in `acee.json`. It tracks mandates (7 mentions), not requirements. Side B's first cited host does not do the work claimed of it |
| `UCKP vocabularies` | does `engine/uckp/vocabulary.py` handle requirements? | **No requirement vocabulary.** The module defines vocabularies for terms; "requirement" appears once, as a *rule* gloss for a term kind, not a requirements capability |
| `UCDA decision tracking` | does `ucda-decisions.json` track requirements? | It tracks **decisions** — the disposition overlay mandated by CEP-002 Article 28. 18 mentions of "requirement" are requirements *upon decisions*, not requirement evolution |

Does UREE exist as a programme?

| Test | Result |
|---|---|
| UREE programme directory or engine | **None.** The only UREE-named path in the repository is the Side B determination document itself |
| UREE identifiers in the id ledger | **One object** — `UCOS-UKAPUR-000001`, which is the Side B *document*, not a programme |

---

## 3. Adjudication

**Both sides are right about a different thing, and the contradiction dissolves once they are
read as answers to two different questions.**

Side B is right that **no new programme admission is required**. UREE should not be built as a
new programme: the discovery and disposition machinery already exists in `CAEM-001`, which
runs the 1,449-mandate corpus through discovery → disposition → certification and is a passing
stage of `./verify.sh --full` (28/28 green, 2026-09-26). That IS requirement evolution, by
another name.

Side A is right that **requirement evolution is a distinct concern from what ACEE, UCKP and
UCDA do** — and Side B's evidence for "already operational" named three hosts, none of which
perform it. The capability is real; the hosts were wrong.

The reconciliation, on evidence:

> **Requirement evolution is operational, and it lives in CAEM-001 — not in the three hosts
> Side B named.** UREE is therefore `ALREADY-REPRESENTED` as a capability under an existing
> programme, and Side A's "new capability required" is satisfied by *composition*, not by new
> programme admission. Neither side's host claim survives intact: Side A's new programme is
> not needed, and Side B's three hosts are not the ones doing the work.

This is the same disposition the capability catalogue already records for Amendment Authority
(`ALREADY-REPRESENTED`, `R2`): the capability exists, under an existing home, and the apparent
gap was a registration question rather than a construction one.

---

## 4. What this discharges

| Item | Effect |
|---|---|
| **F-20 / S-5** | **RESOLVED.** The contradiction is adjudicated on evidence, not by choosing a side or proceeding under "already operational" while it was live |
| **BC-4 P-B** | The partition's P-B (requires external authority) population is unaffected — 0 subjects, unchanged |
| **R-55** | Satisfied. The resolution is recorded rather than assumed |

**What this does NOT discharge:** S-3 (the machine-readable authority key) and S-4 (evidence-kind
constitutive status) remain separate dependencies of BC-4, and BC-4's ratification remains an
owner act. Adjudicating F-20 does not ratify anything.

---

## 5. Boundary

This adjudication resolves a *factual disagreement between two determinations* by measuring the
repository. It does not confer authority, does not amend a constitution, and does not ratify an
owner. If the owner of either determination disagrees with the reading, that disagreement is
recorded here rather than overridden — but the measurements above are reproducible.

*End of F-20 adjudication.*
