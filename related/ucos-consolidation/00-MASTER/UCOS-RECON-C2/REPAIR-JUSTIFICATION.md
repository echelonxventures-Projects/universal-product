# UCOS-RECON-C2 — REPAIR JUSTIFICATION

| Field | Value |
|-------|-------|
| AUTHORITY | **NONE — DERIVED TRUTH** |
| REPAIR | 2 data entries in `00-BOOK/tools/config.py::EXCLUDE_DIR_PREFIXES` + the declarative prose that mirrors them |
| ENGINE LOGIC CHANGED | **NONE** |
| GENERATED FILES HAND-EDITED | **NONE** |

---

## 1. The change

```python
EXCLUDE_DIR_PREFIXES = (
    ...
    "00-MASTER/",
    "MCP-001-MASTER-CONTEXT-AND-EXECUTION-SYSTEM.md",
    # Generated Projections (class 2) emitted OUTSIDE 00-BOOK — UCOS-RIE-001.
    "intelligence/UCOS-RIE-",
    "intelligence/UCOS-IMP-BASELINE-001.",
)
```

Plus one prose update to `NON_ARTIFACT_SCOPE["generated"]` so the declared
taxonomy states what the executable rule now does. Both are DATA.

## 2. Why the declaration is the correct instrument

`config.py` names three exclusion classes: (1) the generator's own machinery,
(2) **its GENERATED outputs**, (3) Operational Memory. The RIE family is class (2).
The block further declares the operation lawful in advance:

> Excluding a path is append-only-safe: any identifier already allocated to a
> now-excluded path is RETAINED-BUT-RETIRED in the id-ledger (never renumbered,
> never reused, never emitted) — see `ukb.allocate()` / `derive_change_events()`
> (UMB-017 C-05).

And `derive_change_events` implements precisely this case in code:

> the append-only snapshot history may retain the UID of a path that is no longer
> a registered repository artifact (e.g. a corrected false registration whose path
> the version-control eligibility boundary now excludes). Such UIDs are NOT
> emitted as change-event subjects … The history itself is preserved.

The repair is therefore not a workaround bolted onto the engine — it is the
engine's own designed remedy for exactly "a corrected false registration".
Precedent: **UCOS-RECON-C1** performed the identical operation for `00-MASTER/`
and describes it as *"Single change. One file. Six lines of data + rationale."*

## 3. Why the engine was NOT changed

The mission mandates repairing the engine if the engine is at fault. It is not.

| Property | Verdict |
|---|---|
| Eligibility computed from a declared authority, not the environment | ✔ correct (B-01c) |
| Exclusion applied identically in both enumeration modes | ✔ correct |
| Ledger append-only, path-keyed, monotonic | ✔ correct |
| Regeneration idempotent (stamp-neutralized no-op skip) | ✔ correct — proven byte-identical across runs |
| Retirement of newly-excluded paths | ✔ already implemented |
| Drift gate fail-closed and accurate | ✔ correct — it reported a real split |

The engine did the right thing with a wrong input. The wrong input was a missing
declaration. Changing engine logic to tolerate self-referential artifacts would
have been the actual defect.

## 4. Options considered and rejected

### Option A — run `register.sh` and commit (the symptom fix)
**Rejected.** Provably breaks on the next `rie build` (ROOT-CAUSE-REPORT §2). It
had already been applied three times (`1c6e750`, `898ef8d`, and the `b47f5b9`-era
"regenerate at the committed anchor" run) and failed three times. A repair known
in advance to fail again is a make-the-status-green patch, which the mission
forbids.

### Option B — strip the self-referential fields from RIE output
**Rejected.** It would require deleting `source_commit`, `repository_head`,
`generation_timestamp`, `input_hash`, `evidence_state.evidence_files` and the
whole coverage-derived health section. Those fields *are* the artifact's
evidentiary content — its declared basis is *"sha256 over the canonical evidence
fingerprint … and HEAD, which pins the whole tracked tree."* Removing the anchor
to make the artifact registrable would destroy the provenance that makes it
worth having, and would gut `UCOS-RIE-HEALTH` entirely. It also treats a
classification error as a content problem.

### Option C — hand the family to the ignore authority (`.gitignore`)
**Rejected on evidence.** This is the mechanism used for eight other generated
families, and it was the first candidate. It fails here: `rib-blueprint.json`
declares four RIE outputs as `required: true` substrate, and
`rib_engine.py::Substrate.findings()` emits *"required substrate absent"*
unconditionally when the file is missing. Untracking them would make the file
absent in a fresh CI checkout. **Measured:** a clean detached worktree at
`a6ccdc0` already fail-closes (`exit 2`) on the two *existing* gitignored
substrates `closure.json` / `phase3.json`. Option C would have widened that
pre-existing fragility from two substrates to six. Option A′ below avoids it.

### Option A′ — corpus-internal exclude, files stay tracked  ← **ADOPTED**
Withdraws *registration* without withdrawing *version control*. This is the
distinction the config block draws for `00-BOOK/DATA/`, `REGISTRIES/`,
`CONTROL-TOWER/`, `PORTAL/` — all tracked, none registered, because "the registry
must not list itself".

## 5. Constraint compliance

| Constraint | Evidence |
|---|---|
| Preserve PROGRAM-002 (frozen kernel) | 0 writes under `engine/`. `engine/kernel` untouched. `verify.sh` PASS. |
| Preserve PROGRAM-003 | 0 writes under `engine/`, `platform/`. `engine/provider` untouched. Both are now *catalogued* (RIB GATE-07 closed) where before they were not. |
| Zero duplication | No new list, registry, engine, validator or config file. Two entries appended to the one list that already governs this. |
| Zero hardcoding | Family **prefixes**, not artifact names — every present *and future* output of this producer is covered with no further edit. Mirrors the existing `MCP-001-…md` prefix entry. |
| Zero manual synchronization | Nothing to keep in sync: the prefix is evaluated on every enumeration. |
| Zero technical debt | The declared taxonomy (`NON_ARTIFACT_SCOPE`) was updated so no stale declaration is left behind. |
| Repair the engine, not the outputs | Engine logic unchanged; every projection regenerated by `register.sh`. No generated byte was typed by hand. |
| Generated outputs reproducible | Two consecutive transactions byte-identical (digest `8b483a13…`). |

## 6. No overreach

`intelligence/UCOS-` would have been shorter and was deliberately **not** used: it
would also match `intelligence/UCOS-UPI-001/publication-formats.json`, the authored
format descriptor that `.gitignore` explicitly re-admits *"so a future authored
format remains a registerable artifact."* Verified mechanically:

```
newly excluded (11): the exact RIE family, nothing else
still eligible under intelligence/ (0)
'intelligence/UCOS-UPI-001/publication-formats.json'.startswith(EXCLUDE) → False
```

## 7. Consumers verified unaffected

| Consumer | Requirement | Status |
|---|---|---|
| `rib-blueprint.json` SUB-RIE-{CAPS,BASELINE,DEPS,FRONTIER} | present + parses + tracked + pointers resolve | ✔ `--check-substrate` PASS |
| `platform/repository_intelligence/substrate.py` | live producer first, artifact second | ✔ unchanged; artifact still present |
| `intelligence/tests/test_rie.py`, `test_portal.py` | in-memory `eng.outputs()` | ✔ never read the tracked files |
| `CK-RIE-DETERMINISM` (`rie verify`) | read-only, in-memory double render | ✔ `deterministic: true` |
| Hardcoded corpus counts (`1204`, `12851`) in any gate or test | must not exist | ✔ none found |

## 8. Scope discipline

Implemented: the root-cause repair only.

One adjacent action is recorded separately in `4141647`: regenerating the
UCOS-RIE-001 capability catalogue. This is not part of the repair — it is the
blueprint's own named remediation for the **pre-existing** GATE-07 failure
(*"extend the canonical capability catalogue — the catalogue is the owner, so the
entry is added there, not here"*), performed by the owner from evidence, and it
became safe to do only because the repair removed the registration coupling. It
is reported as a distinct commit with its own justification, not folded into the
repair.

`00-MASTER/MIP-W1-P001/` was bound to version control, not registered and not
ignored: it is authored operational memory in the permanently non-registrable
`00-MASTER/` lane, and it was proven non-causal (ROOT-CAUSE-REPORT §6).

---

*END — UCOS-RECON-C2 REPAIR JUSTIFICATION · AUTHORITY = NONE (DERIVED TRUTH)*
