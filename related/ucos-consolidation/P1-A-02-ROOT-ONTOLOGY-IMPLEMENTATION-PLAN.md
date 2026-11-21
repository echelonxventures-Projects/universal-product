# P1-A-02 — Constitutional Primitive Alignment Implementation Plan

**Phase:** PHASE 1 — FOUNDATION COMPLETION · Scope A
**Predecessor:** `P1-A-01-ROOT-ONTOLOGY-DISCOVERY-REPORT.md` (discovery complete; GAP A-1…A-4; SC-A-01…03)
**Posture:** PLAN ONLY. Nothing in this document is executed until it is read back as the change contract.

---

## 1. Decision

**Programme:** `UCPA-000001` — Universal Constitutional Primitive Alignment.
**Verified free:** zero occurrences of `UCPA-` across all `.md`/`.json`/`.py`.

**Standing:** `authority: NONE — DERIVED TRUTH.` UCPA legislates no ontology. It measures the
register that already owns one. It mints no primitive, opens no counter, and admits no element the
canonical register does not already declare. It cannot become a second ontology authority because
every element it names must first be found in `01-WORKING/ONTOLOGY-REGISTER.md`, and `UCPA-L-01`
fails closed when one is not.

**Why a programme and not an extension:**

| Alternative | Rejected because |
|---|---|
| Extend `engine/uckp/` | UCKP is Layer Zero. `test_importing_layer_zero_does_not_drag_in_the_upper_layers` is an existing invariant; register parsing and file I/O would violate it. UCKP must be *imported by* the mapping, never made to carry it. |
| Extend `engine/context/ontology.py` | Owns the context universe (UCXI-000001), not the constitutional root. Would transfer authority to a programme that disclaims it. |
| Extend `00-MASTER/UAIE-000001` | An architectural-intelligence programme; its anchors bind *itself* to `ONT-25/27/29`. Making it own the root ontology inverts the anchor relation. |
| Edit `01-WORKING/ONTOLOGY-REGISTER.md` | It is the canonical owner and its Part A is **ratified**. Editing ratified content is amendment, which Scope A forbids ("Do not replace existing models"). UCPA reads it; it never writes it. |

---

## 2. Files

### 2.1 Created

| Path | Role |
|---|---|
| `00-MASTER/UCPA-000001/ucpa-declaration.json` | The declaration. All primitives, bindings, facet reduction, projection classification, laws — **as data**. |
| `engine/root_ontology/__init__.py` | Public surface. |
| `engine/root_ontology/model.py` | Rehydrates the declaration; contains no primitive name, no facet name, no path, no law text. Bidirectional `validate()`: a law naming an absent check *and* a check no law claims are both refusals. |
| `engine/root_ontology/contract.py` | The measurements. One function per declared check; `LAW_CHECKS` dispatch. |
| `engine/root_ontology/gate.py` | OBSERVE MODE, read-only. Exit `0` OPEN / `1` CLOSED / `2` FAULT. No `--render`, no `--replay` (writes nothing → declaring an unread flag is the `GP-4` defect). |
| `engine/tests/unit/test_root_ontology.py` | Tests. |
| `UCPA-001-CONSTITUTIONAL-PRIMITIVE-ALIGNMENT-DETERMINATION.md` | The reconciliation determination Scope A requires. Dispositions SC-A-01/02/03. |

### 2.2 Modified

| Path | Change | Constraint |
|---|---|---|
| `verify.sh` | One `run_stage` for the UCPA gate, in MAIN, after the UISD stage | The literal is the declared contract; `UAKOS-CLOSURE-008/validation-record.json` digests it |
| `00-MASTER/UVI-000001/uvi-declaration.json` | One `stage_registry.stages[]` entry | `UVI-L-03` requires label set and `verify.sh` `run_stage` literals to be **equal and identically ordered** |
| `00-MASTER/UOBC-000001/birth-ledger.json` | Birth records for the new governed objects | Identity before existence (`UOBC-000001`) |

### 2.3 Not modified — stated so the boundary is explicit

`01-WORKING/ONTOLOGY-REGISTER.md`, `01-WORKING/SUPERSESSION-REGISTER.md`,
`02-MASTER/UCOS-RAT-001-…md`, `engine/uckp/facets.py`, `UCOS-OMEGA-INFINITY-MASTER-IMPLEMENTATION-PLAN-V2.md`,
`UMN-001-…md`. The last two carry the superseded form (GAP A-4); they are **classified**, not edited.
Supersession is the forward channel (`CEP-007 XIII`), and a determination that supersedes a statement
does not require rewriting the artifact that made it.

---

## 3. Capabilities

| Capability | Status | Action |
|---|---|---|
| `engine.root_ontology` | NEW | CREATE — no ontology capability exists in the 128-entry catalogue |
| `engine.uckp.facets.Facet` | EXISTING | REUSE — imported as the sole source of the facet set |
| Register anchor verification | EXISTING (pattern) | REUSE — `UAIE` idiom, applied to the root register |
| Programme gate contract | EXISTING (pattern) | REUSE — `UISD` idiom |
| Object birth identity | EXISTING | REUSE — `UOBC-000001` |

---

## 4. The law set

Every law is measured against a **file the repository already owns**. No law is satisfied by a
constant in Python.

| Law | Statement | Measured against |
|---|---|---|
| `UCPA-L-01` | Every primitive the declaration binds is an element the canonical register already declares. | `01-WORKING/ONTOLOGY-REGISTER.md` — id **and** element name must both appear |
| `UCPA-L-02` | The standing the declaration gives each primitive is the standing the ratification record gives it. | `01-WORKING/SUPERSESSION-REGISTER.md` `SUP-01`/`SUP-07` rows, parsed — not restated |
| `UCPA-L-03` | The facet reduction is total and single-valued over the live facet enumeration. | `engine.uckp.facets.Facet`, imported. A 34th facet added without a mapping closes the gate. |
| `UCPA-L-04` | No facet reduces to the axiom. | `RAT-01` made executable: BEING is not an addressable node, so nothing may anchor to it |
| `UCPA-L-05` | Every declared projection site exists, and every site classified SUPERSEDED is named by a superseding instrument that exists. | The projection files themselves + the naming determination |
| `UCPA-L-06` | Exactly one claimant holds role AUTHORITY, and it is the owner the binding register names. | `00-MASTER/URRC-000001/urrc-bindings.json` `D-24.canonical_owner`, read at measurement time |
| `UCPA-L-07` | The primitive set is open. | Extension probe — a synthetic primitive is admitted into a copy of the binding; refusal is a violation (mirrors `UCKP-INV-14` `is_extensible()`) |
| `UCPA-L-08` | The programme reduces to a primitive and says which. | The declaration's own `self_application` section |

### 4.1 Hard-coding control

The Phase-1 rule "NO HARD CODED REALITY" is satisfied structurally, and it is checkable:

- No primitive name, facet name, `ONT-*` id, file path or law sentence appears in any `.py` file.
- `model.py` refuses a declaration missing a section rather than defaulting.
- `UCPA-L-07` proves the set is not a closed enumeration.
- The facet side of the mapping is **imported**, so the mapping cannot silently disagree with the
  facet model — it can only fail.

---

## 5. Dependencies

```
01-WORKING/ONTOLOGY-REGISTER.md      (canonical owner, read-only)
01-WORKING/SUPERSESSION-REGISTER.md  (ratification record, read-only)
00-MASTER/URRC-000001/urrc-bindings.json (owner binding, read-only)
engine/uckp/facets.py                (facet enumeration, imported)
        │
        ▼
00-MASTER/UCPA-000001/ucpa-declaration.json
        │
        ▼
engine/root_ontology/{model,contract,gate}.py
        │
        ├─► engine/tests/unit/test_root_ontology.py
        └─► verify.sh  ──►  00-MASTER/UVI-000001/uvi-declaration.json (UVI-L-03, bidirectional)
```

No dependency runs backwards. Nothing UCPA writes is read by anything it reads.

---

## 6. Risks

| # | Risk | Control |
|---|---|---|
| R-1 | `UVI-L-03` closes because the stage label and the registry entry disagree | Add both in the same change; the law is bidirectional and will prove it |
| R-2 | Register parsing is brittle against markdown edits | Match on the stable `ONT-*` id **and** the element name, both of which are ratified content; report the miss as a violation with the id, never a silent pass |
| R-3 | The gate is read as a second ontology authority | `authority: NONE`; every element must pre-exist in the register; `UCPA-L-01` is the structural proof |
| R-4 | Coverage floor (90%) not met by the new module | Tests cover every law check, both verdicts, and the FAULT path |
| R-5 | The facet→primitive mapping is contestable | Each mapping row carries a `basis` citing the facet's own declared question from `engine/uckp/facets.py`; the determination records the reasoning |
| R-6 | New stage slows `--fast`/`--change` | Gate is read-only, parses three files and imports one enum; declared `reusable: true` |

---

## 7. Validation

| Gate | Requirement |
|---|---|
| `python -m engine.root_ontology.gate` | exit `0` OPEN |
| `pytest engine/tests/unit/test_root_ontology.py` | all pass |
| `./verify.sh --fast` | pass |
| `./verify.sh --change` | pass — includes every governance gate |
| `./verify.sh --integration` | pass — whole suite under the 90% floor |
| `./verify.sh --full` | pass — certification |

**Determinism:** the gate takes no clock, no network, no subprocess, and writes nothing. Two runs
over the same tree produce the same report.

---

## 8. Order of execution

1. Declaration (`ucpa-declaration.json`) — data first, so the model has something to refuse.
2. `model.py` → `contract.py` → `gate.py`.
3. Tests.
4. Gate run in isolation → must be OPEN before wiring.
5. `verify.sh` stage + `uvi-declaration.json` registry entry — together.
6. Birth records.
7. Determination.
8. `./verify.sh --fast` → `--change` → `--integration` → `--full`.
9. Certification record + registry/baseline update.

No step begins before the one above it passes.

---

*End of P1-A-02-ROOT-ONTOLOGY-IMPLEMENTATION-PLAN.md*
