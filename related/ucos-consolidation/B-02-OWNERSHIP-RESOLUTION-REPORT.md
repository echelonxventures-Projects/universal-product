# B-02 — UID Dictionary Persistence · Ownership Resolution Report

| Field | Value |
|---|---|
| ITEM | Scope B · B-02 — UID Dictionary Persistence (gap **G3**) |
| MODE | **OWNERSHIP RESOLUTION ONLY.** No code, no artifact, no registry mutation, no MCP-002 update, no completion claim. |
| PREDECESSOR | `B-02-UID-DICTIONARY-PERSISTENCE-DISCOVERY.md` |
| CONSTITUENT AUTHORITY | **NONE** |
| RULE OBSERVED | Ownership is **derived from existing declarations**, never invented. Every conclusion cites the instrument that already decides it. |

---

## 1. Existing ownership patterns — measured

`00-BOOK/DATA/generated-artifact-registry.json`: **344 entries**, uniform on three fields — `lifecycle: REGENERATED`, `canonical_identity_role: CANONICAL`, `registration_status: EXCLUDED_FROM_CORPUS_REGISTRATION` (344/344 each).

### Where derived artifacts live
| Host | Count |
|---|---|
| `00-MASTER/<PROGRAMME>/` | **333** |
| `intelligence/` | **11** |

### Who produces them
| Producer root | Count |
|---|---|
| `00-MASTER/<PROGRAMME>/<engine>.py` | 314 |
| **`engine/`** | **19** |
| `intelligence/` | 11 |

### The two patterns that settle this question

**Pattern A — engine-produced, programme-hosted (19 artifacts).**
`engine/uaue/gate.py` → `00-MASTER/UAUE-000001/…`, `owner: UAUE-000001`, `validation_owner: UAUE-000001`, `regeneration_command: make uaee-render`, `certification_role: REPLAY_PROVEN`.
**An engine module may produce an artifact owned by a programme.** The producer's location does not determine ownership.

**Pattern B — producer-adjacent, no programme home (11 artifacts).**
`intelligence/rie/engine.py` → `intelligence/UCOS-RIE-*.json`, `owner: UCOS-RIE-001` — an owner id with **no `00-MASTER/` home at all**, and **absent from `producer_homes`**.

**Conclusion: no operational home must be created. Both patterns already admit this artifact.**

> **CORRECTION, recorded during implementation (B-02).** This section originally concluded
> that *"neither an operational home nor a `producer_homes` row must be created"*. The second
> half was **wrong**, and an existing invariant caught it:
> `test_1_the_register_declares_a_home_for_every_producer_it_names` asserts
> `owners <= homed` over artifacts **whose `canonical_path` starts with `00-MASTER/`**.
> Pattern B is exempt only because RIE's artifacts live in `intelligence/`. Siting this
> artifact at `00-MASTER/UCOS-NUCLEUS-001/` invokes **Pattern A**, which *requires* a
> `producer_homes` row. One was therefore declared — `owner: UCOS-NUCLEUS-001`,
> `home: 00-MASTER/UCOS-NUCLEUS-001`, `producer: engine/nucleus/cli.py`, with the nine
> pre-existing documents declared as `authored_inputs` so that
> `test_1_live_every_tracked_file_in_a_declared_home_is_declared` holds. **No operational
> home was created** — the directory already existed with 9 registered objects; what was
> added is a declaration that brings all ten files under governance.

---

## 2. Artifact Classification

Determined against the rules that already exist, not chosen:

| Candidate | Verdict |
|---|---|
| canonical artifact | **NO** — it asserts nothing; `authority: NONE — DERIVED TRUTH` |
| **generated artifact** | **YES** — emitted by a declared producer from declared inputs |
| **derived projection** | **YES** — `dictionary_for(registry)` projects a population it does not own |
| runtime cache | **NO** — `lifecycle: REGENERATED`, not ephemeral; it is replay-proven, not memoised |
| verification artifact | **NO** — it is not evidence of a verification run |
| registry projection | **YES**, and this is the precise term — a projection **of** a registry, never a registry |

**CLASSIFICATION: `GENERATED_ARTIFACT` / `DERIVED PROJECTION` of a registry.**

Consequences that follow automatically, with no new rule:

* `lifecycle: REGENERATED` · `canonical_identity_role: CANONICAL` · `registration_status: EXCLUDED_FROM_CORPUS_REGISTRATION` — the value all 344 existing entries carry.
* Under **`UOBC-BSP-001`** (certified) it matches kind `GENERATED_ARTIFACT` first, so `birth_required: false`, `enforcement: MANDATORY_ABSENCE`. **`BSP-L-03` fails closed if it is ever given a birth record.** B-01 already governs B-02.

---

## 3. Ownership Authority

### 3.1 The rule that decides it

`00-MASTER/UCOS-UGA-001/uga-declaration.json` `ownership_rules`, first row:

> `00-MASTER/<PROGRAM>/...` → owner `<PROGRAM>` — *"Operational Memory is organised by programme; the programme directory IS the owner."*

Ownership follows **path**, not producer and not population. Pattern A confirms it empirically: `engine/uaue/gate.py` produces, `UAUE-000001` owns.

### 3.2 Resolution

| Field | Value | Existing basis |
|---|---|---|
| **Owner** | `UCOS-NUCLEUS-001` | Existing UGA owner — **9 objects already carry it**; existing home `00-MASTER/UCOS-NUCLEUS-001/`. Nothing created. |
| **Namespace** | `ucos-repository` (repository plane, derived) · identifier plane **P4 logical** | `constitutional-authority-alignment.json` `derivation.namespace`; `UIS-001` `MECH-EPIC001` |
| **Registry** | `00-BOOK/DATA/generated-artifact-registry.json` | The one registry for generated artifacts; 344 entries |
| **Lifecycle** | `REGENERATED` under `UCIC-001` (owner) · `UCL-000001` (derived) | 344/344 precedent |
| **Identifier authority** | `UCKP-ART-05`, unchanged; `deterministic_id` reused as-is | No counter opened |

**No new owner, no new namespace, no new registry, no new lifecycle model.**

### 3.3 Why not the Registry Platform

`MECH-EPIC001` (`engine/registry/universal/identity.py`) owns the identifier **grammar**. The artifact's content changes when the **population** changes, not when the grammar does. Ownership by path assigns it to the programme whose population it enumerates. The grammar owner remains cited, never displaced.

---

## 4. Persistence Location

**`00-MASTER/UCOS-NUCLEUS-001/UCOS-NUCLEUS-IDENTIFIER-DICTIONARY.json`**

| Requirement | Satisfied by |
|---|---|
| deterministic | Two CLI runs already byte-identical (measured); `deterministic: true` in the registry entry |
| discoverable | Under an existing programme home that UGA already indexes |
| registry-backed | One entry in the generated-artifact registry, all 18 declared fields |
| evidence traceable | `verify()` report + digest; `certification_role: REPLAY_PROVEN` |
| rebuildable | `from_document()` exists; `regeneration_command` declared |

This uses an existing directory and an existing owner. **It does not create an operational home** — `00-MASTER/UCOS-NUCLEUS-001/` already exists with 9 registered objects.

---

## 5. Implementation Boundary *(proposal — NOT authorized)*

### Producer contract
| Field | Value |
|---|---|
| `producer` | `engine/nucleus/cli.py` (extend the existing `dictionary` command with `--write`) |
| `owner` / `validation_owner` | `UCOS-NUCLEUS-001` |
| `capability` | `nucleus-ownership` *(to be confirmed against the existing capability vocabulary)* |
| `input_closure` | `engine/nucleus/registry.py`, `engine/registry/universal/{identity,dictionary}.py` |
| `regeneration_command` | `python -m engine.nucleus.cli dictionary --write` |
| `deterministic` | `true` |
| `consumers` | `[]` — **measured: no production consumer exists today** |

### Verification integration point
The **existing** UOBC/UGA/registry stages already govern the file as a governed object. A dedicated determinism/replay stage is **optional**; if added, `verify.sh`, the UVI `stage_registry`, `UAKOS-CLOSURE-008/validation-record.json` `stages_digest` and its re-render **must move in one change** (`UVI-L-03` is bidirectional).

### Evidence requirements
Producer fixed point · two-build determinism proof · `verify()` PASS (currently 212/212, 0 unreproducible) · generated-artifact registration · four-mode verification · evidence report · certification record.

### Files expected to change
| Path | Change |
|---|---|
| `engine/nucleus/cli.py` | `--write` flag on the existing command |
| `00-MASTER/UCOS-NUCLEUS-001/UCOS-NUCLEUS-IDENTIFIER-DICTIONARY.json` | **new** derived artifact |
| `00-BOOK/DATA/generated-artifact-registry.json` | one entry |
| `engine/tests/nucleus/…` | persistence, replay, refusal, no-birth tests |
| *(optional)* `verify.sh` + `uvi-declaration.json` + `validation-record.json` | only together |

**Not changed:** `engine/registry/universal/dictionary.py` (serialisation already complete) · `UOBC-BSP-001` · `id-ledger.json` · `birth-ledger.json` · any authority declaration.

---

## 6. A vacancy discovered, referred — not resolved here

`00-MASTER/P0-LIFECYCLE-CLOSURE-001/UCOS-LIFECYCLE-REALIZATION.json` records stage **`UCL-S-0320` "Update Universal Constitutional Identifier Dictionary"** as:

```
realization : IMPLEMENTED        discharge.provider : engine.constitution.evolution
coverage    : engine/constitution/stages.py · engine/uckp/vocabulary.py
probes      : ownership_resolves = true
```

The coverage names **`engine/uckp/vocabulary.py`** — the **TERM** vocabulary. `engine/registry/universal/dictionary.py` — the **assigned-identifier** dictionary this item persists — appears nowhere in it.

**This independently confirms `GAP B-4`** (recorded in `SCOPE-B-IDENTITY-CONTAINMENT-DETERMINATION.md` §5.2) from a second machine-readable source: the lifecycle stage bearing the word *Identifier Dictionary* is already claimed and discharged against a different object.

**Consequence:** the assigned-identifier dictionary has **no lifecycle stage claiming it**. That is a genuine ownership vacancy on the *stage* plane — distinct from the *artifact* ownership resolved in §3, which stands on its own.

**Referred to `UCL-000001`'s owner. Not resolved here, and B-02 does not depend on it:** artifact ownership is settled by the UGA path rule regardless of which stage later claims the obligation.

---

## 7. Stop-condition validation

| Requirement | Status |
|---|---|
| Ownership resolved from existing declarations only | **CONFIRMED** — UGA path rule + two measured registry patterns |
| No `UCOS-EPIC-001` operational home created | **CONFIRMED** — not needed; Pattern B proves `producer_homes` is optional |
| No `UCOS-NUCLEUS-001` operational home created | **CONFIRMED** — it already exists with 9 registered objects |
| No new registry | **CONFIRMED** |
| No new authority | **CONFIRMED** |
| No persistence implemented | **CONFIRMED** |
| No code modified | **CONFIRMED** — this report is the only new file |
| No artifact created | **CONFIRMED** |
| MCP-002 not updated | **CONFIRMED** |
| B-02 completion not claimed | **CONFIRMED** — ownership resolved; implementation **NOT AUTHORIZED** |

---

*End of B-02-OWNERSHIP-RESOLUTION-REPORT.md*
