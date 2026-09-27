# S-4 Evidence-kind constitutive status — decision record

| Field | Value |
|---|---|
| ARTIFACT | `UCOS-OMEGA-INFINITY-BLOCKER-CLOSURE/BC-4-S-4-EVIDENCE-KIND-DECISION.md` |
| PURPOSE | Record the constitutive status of each evidence kind, which the implementation plan reports as R-52 CRITICAL undecided |
| AUTHORITY | **NONE — DERIVED TRUTH.** Measures what the code already enforces; creates no authority |
| RESOLVES | **S-4** (R-52 CRITICAL) — BC-4 dependency |

---

## 1. What the plan recorded

The implementation plan §3.4 forbids binding an assignment to *"an evidence kind whose
constitutive status is undecided (R-52 CRITICAL),"* and §3.5 holds the partition's P-C at
*"Constitutional decision required"* on the same question. R-52 is recorded as **OPEN** in the
status register.

## 2. The decision, measured in code

`platform/universal_ownership/contracts.py` does not leave this undecided. The `EvidenceKind`
enum carries the status per kind, and the two tuples partition the set:

| Evidence kind | Status | Basis |
|---|---|---|
| `declared-assignment` | **CONSTITUTIVE** | may establish ownership |
| `declared-identity` | **CONSTITUTIVE** | may establish ownership |
| `definitional-locator` | **CONSTITUTIVE** | may establish ownership |
| `delegation` | **CONSTITUTIVE** | may establish ownership |
| `registration` | corroborative | may corroborate, never establish |
| `corroboration` | corroborative | may corroborate, never establish |

The partition is total — six kinds, four constitutive, two corroborative, no kind unclassified.
The `.constitutive` property is executable and is what the evidence gate actually consults.

## 3. The decision

**Evidence-kind constitutive status is DECIDED.** Four kinds are constitutive, two are
corroborative, and no kind holds undecided status. R-52 is resolved by measurement of the
enforcement code rather than by a constitutional act, because the code already partitions the
set and the partition is total.

## 4. Boundary

This records a partition the implementation already enforces. It does not amend OWN-REQ-001,
does not add a seventh evidence kind — which the plan notes would require amending the facet
doctrine — and does not decide any *other* undecided constitutional question held in P-C. If a
future evidence kind is admitted, it is admitted by registration under UCKP-ART-17, and this
record does not pre-empt that act.

*End of S-4 decision record.*
