# BASELINE-001 · Succession and Addressability

Every row below is DISCOVERED from the located register named in the register row.
No baseline is recorded, advanced or certified by this measurement.

| Register | Owner | Resolves |
|---|---|---|
| `BLN-REG-01` | `00-MASTER/BASELINE-001/BASELINE-REGISTRY.md` | YES |

## Recorded baselines

| Row | Baseline | Ordinal | Scheme | Commit | Branch | Date | State | Current |
|---|---|---|---|---|---|---|---|---|
| 1 | `UCOS-BASELINE-001` | 1 | YES | YES | YES | YES | CERTIFIED · superseded as *current* by row 2, not invalidated | no |
| 2 | `UCOS-BASELINE-002` | 2 | YES | YES | YES | YES | CERTIFIED — CURRENT CONSTITUTIONAL BASELINE | **YES** |

## Succession

The meta-constitution requires inheritance to be EXPLICIT and prohibits implicit
inheritance from a containing programme, phase or directory. Row order alone is
therefore insufficient: a non-origin baseline must RECORD its predecessor. Both the
explicit claim and the structural order are measured, and a disagreement between them
is a failure rather than a resolution in favour of either.

| Baseline | Origin | Explicit predecessor | Structurally preceding | Evidence block | Pointers | Unresolved |
|---|---|---|---|---|---|---|
| `UCOS-BASELINE-001` | YES | — | — | `00-MASTER/BASELINE-001/CERTIFIED-BASELINE-RECORD.md` | 0 | 0 |
| `UCOS-BASELINE-002` | no | `UCOS-BASELINE-001` | `UCOS-BASELINE-001` | `00-MASTER/BASELINE-001/BASELINE-REGISTRY.md` | 20 | 0 |

## Chain shape

| Property | Value |
|---|---|
| Origins | `UCOS-BASELINE-001` |
| Heads | `UCOS-BASELINE-002` |
| Acyclic | YES |
| Edges | `UCOS-BASELINE-002` → `UCOS-BASELINE-001` |

## Protected records

These are the append-only records this measurement may never write. The write set is
proved disjoint from them, and every record present in the home is proved to be a
member of the protected set.

| Record | Role | Owner | Located | Pointers | Unresolved |
|---|---|---|---|---|---|
| `BLN-RC-01` | register | `00-MASTER/BASELINE-001/BASELINE-REGISTRY.md` | YES | 21 | 0 |
| `BLN-RC-02` | origin-record | `00-MASTER/BASELINE-001/CERTIFIED-BASELINE-RECORD.md` | YES | 0 | 0 |
| `BLN-RC-03` | certificate | `00-MASTER/BASELINE-001/FINAL-BASELINE-CERTIFICATE.md` | YES | 27 | 0 |
| `BLN-RC-04` | continuation | `00-MASTER/BASELINE-001/REMAINING-ROADMAP-CLASSIFICATION.md` | YES | 0 | 0 |

| Immutability | Value |
|---|---|
| Write set | `00-MASTER/BASELINE-001/00-BASELINE-INHERITANCE-DASHBOARD.md`, `00-MASTER/BASELINE-001/01-SUCCESSION-AND-ADDRESSABILITY-REGISTER.md`, `00-MASTER/BASELINE-001/02-INHERITANCE-AND-NON-INHERITANCE-REGISTER.md`, `00-MASTER/BASELINE-001/03-CURRENCY-AND-CITATION-REGISTER.md`, `00-MASTER/BASELINE-001/04-VERSION-LINEAGE-AND-EVOLUTION-REGISTER.md`, `00-MASTER/BASELINE-001/05-VALIDATION-REPORT.md`, `00-MASTER/BASELINE-001/06-CERTIFICATION-REPORT.md`, `00-MASTER/BASELINE-001/baseline.json` |
| Protected set | `00-MASTER/BASELINE-001/BASELINE-REGISTRY.md`, `00-MASTER/BASELINE-001/CERTIFIED-BASELINE-RECORD.md`, `00-MASTER/BASELINE-001/FINAL-BASELINE-CERTIFICATE.md`, `00-MASTER/BASELINE-001/REMAINING-ROADMAP-CLASSIFICATION.md` |
| Intersection | **empty** |
| Records in the home outside the protected set | **none** |
| Disjoint | YES |
