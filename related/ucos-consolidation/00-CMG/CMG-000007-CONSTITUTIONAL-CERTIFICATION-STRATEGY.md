# UCOS Ω∞ — CMG CONSTITUTIONAL CERTIFICATION STRATEGY

| Field | Value |
|-------|-------|
| ARTIFACT ID | CMG-000007 |
| ARTIFACT | UCOS Ω∞ CMG Constitutional Certification Strategy |
| CLASSIFICATION | Constitutional Meta Governance (CMG) — Certification Strategy |
| PHASE | PHASE-000 |
| PROGRAM | CMG |
| CATEGORY | CMG |
| VOLUME | VOL-002 |
| STATUS | UNDER REVIEW · DERIVED · NON-NORMATIVE |
| VERSION | 1.0 |
| AUTHORITY | NONE (DERIVED TRUTH) |
| GOVERNED-BY | CMG-000001 |
| DEPENDS-ON | CMG-000001 |
| CANONICAL FORM | This Markdown file |

> Derived strategy under CMG-000001 Articles LI and LXXX. Certification **operation** — eligibility, attestation, issuance, suspension, revocation, renewal, expiry, and the certification registry — is owned by the located certification constitution (`CMG-DLG-05`). This document states the certification subject, its preconditions, and how it is attested without the meta layer attesting itself.

---

## 1 — THE SUBJECT

CMG-000001 defines exactly one certification subject: **Constitutional Readiness**.

It attests that the corpus's meta-constitutional layer is complete, internally consistent, and mechanically enforceable. It attests **nothing** about the substance of any constitution, about process compliance, about implementation, or about finality.

---

## 2 — SEPARATION OF POWERS IN CERTIFICATION

Four roles must remain distinct, and the strategy holds them apart deliberately:

| Role | Held by | Why not the meta layer |
|---|---|---|
| **Defines** the subject and preconditions | CMG-000001 (Articles LI.2, LXXX.2) | This is a meta act — within jurisdiction |
| **Computes** precondition satisfaction | `00-CMG/tools/cmg_validate.py` | Derived truth; asserts nothing on its own authority (CMG-000001 L.6) |
| **Attests** the result | The located certification owner | Self-attestation is prohibited (CMG-000001 LI.6) |
| **Accepts** into the corpus | The located ratification owner | Certification never implies ratification (CMG-000001 LI.3, XLIV.5) |

The meta layer therefore defines and computes; it does not attest and does not accept. This is the certification analogue of the recognition/substance separation that governs the whole instrument.

---

## 3 — PRECONDITIONS AND THEIR PRESENT STATE

The fourteen preconditions of CMG-000001 LXXX.2, evaluated in order, with the present computed result:

| # | Precondition | Verified by | Present |
|---|---|---|---|
| 1 | CMG-000001 present, parseable, conformant to its mandate | Check group 2 | **PASS** — 86 articles, 80 mandated sections resolved |
| 2 | Identifier families used only as declared | Check group 3 | **PASS** |
| 3 | Every registry entry resolves to a present canonical home | Check group 5 | **PASS** — 43 of 43 |
| 4 | `CMG-INV-02` no concern has two owners | Check group 7 | **PASS** — 59 concerns, 0 collisions |
| 5 | `CMG-INV-03` no orphan concern, no ownerless owner | Check group 7 | **PASS** (after correcting 8 over-aggregated concerns) |
| 6 | `CMG-INV-04` every superior resolves or is a recorded vacancy with closure procedure | Check group 8 | **PASS** — 1 vacancy, properly recorded |
| 7 | `CMG-INV-05` dependency graph and lattice acyclic | Check group 9 | **PASS** |
| 8 | `CMG-INV-06` every pair ranked or declared orthogonal | Check group 10 | **PASS** |
| 9 | `CMG-INV-07` every state and transition legal | Check group 11 | **PASS** |
| 10 | `CMG-INV-08` identifiers unique and non-reused | Check group 4 | **PASS** |
| 11 | `CMG-INV-11` every lineage predecessor present | Check group 12 | **PASS** |
| 12 | Every gap dispositioned; every open question recorded | Check group 13 | **PASS** — 9 gaps, 7 open questions |
| 13 | No undispositioned finding, unresolved conflict, expired exception, unclassified impact | Check groups 13, 16; CMG-000002 §5 | **PASS** — 0 findings, 0 persisted conflicts, 0 exceptions, 42 artifacts classified |
| 14 | Every delegation names a **located** owner | Check group 7 | **PASS** — 48 of 48 resolve |

All fourteen preconditions are satisfied.

---

## 4 — OUTCOME DETERMINATION

CMG-000001 LXXX.3 admits exactly three outcomes. The outcome is **computed** from repository state, never asserted:

```
if findings > 0                          -> NOT-READY
elif unclosed vacancies or blocking OQs   -> READY-PROVISIONAL
else                                      -> READY
```

**Present outcome: `READY-PROVISIONAL`.**

Reason: all preconditions pass, but `VAC-01` (Tier-1 Constitutional Authority) is unclosed and blocking open questions remain. CMG-000001 LXXX.4 independently declares a ceiling of `READY-PROVISIONAL` while `CMG-OQ-01` and `CMG-OQ-02` are open, and the validator enforces that ceiling even if the computation would otherwise yield `READY`. A declared ceiling that the tool enforces is the mechanism that prevents provisional readiness from silently becoming final readiness.

---

## 5 — PATH TO `READY`

`READY` is reachable by exactly two acts, both outside the meta layer's authority:

| Step | Act | Authority required | Effect |
|---|---|---|---|
| 1 | Identify and record the authority competent to ratify constitutional artifacts | The out-of-corpus finality authority, or an authority empowered to designate it | Closes `CMG-OQ-01` |
| 2 | Identify and record the artifact occupying Tier T1, or ratify that T1 remains permanently vacant with a declared consequence | The same authority | Closes `CMG-OQ-02` and `VAC-01` |

On completion of both, remove the ceiling by amendment of CMG-000001 LXXX.4, re-run the validator, and the computed outcome becomes `READY`. Standing across the entire dependency graph lifts from PROVISIONAL at the same moment (see CMG-000004 §7).

No other act shortens this path. In particular: freezing does not confer standing (CMG-000001 XXVI.4); certification does not imply ratification (LI.3); and promoting a located artifact into T1 would be self-elevation (XVII.4).

---

## 6 — CERTIFICATION LIFECYCLE

| Event | Effect on certification |
|---|---|
| Amendment to CMG-000001 | **Automatic revocation** (CMG-000001 LXXX.6, LI.5) |
| Amendment to the registry schema, Article LXXXII, or any invariant | **Automatic revocation** |
| Registry content change (a new artifact recognized) | Re-validation required; certification revoked until re-issued |
| A located owner amending its own constitution | Re-validation required if the amendment changes its authority, scope, or conflict rule |
| Closure of `VAC-01` | Re-validation; outcome may improve to `READY` |
| Freeze of CMG-000001 | Certification unchanged; freeze preserves standing and does not upgrade it |

Certification is therefore never a durable claim. It is a statement about a specific repository state, and CMG-000001 LXXX.8 requires the validator output that produced it to accompany the attestation, so that any party can reproduce the result from the repository alone.

---

## 7 — WHAT CERTIFICATION DOES NOT CONFER

Restated because the corpus's located certification constitution makes the same point and it is the most commonly violated boundary:

Certification confers **no** authority, **no** ratification, **no** finality, **no** effect, **no** freeze, and **no** standing. A `READY-PROVISIONAL` certification means: *the meta-constitutional layer is internally complete and mechanically consistent as of this repository state, and its standing is provisional because the authority above it is vacant.* It means nothing more.
