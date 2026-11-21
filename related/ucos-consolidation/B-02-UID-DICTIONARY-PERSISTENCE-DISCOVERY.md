# B-02 — UID Dictionary Persistence · Discovery and Gap Determination

| Field | Value |
|---|---|
| ITEM | Scope B · B-02 — UID Dictionary Persistence (gap **G3**) |
| MODE | **DISCOVERY ONLY.** No code written, no file modified, no identifier minted, no registry mutated, no tracker updated. |
| CONSTITUENT AUTHORITY | **NONE** |
| PRIOR BASELINE | `UOBC-BSP-001` — CERTIFIED. **Not modified.** No constitutional dependency was discovered that requires touching it. |
| BINDING PRIORS | `UNIVERSAL-IDENTITY-UNIVERSE-DETERMINATION.md` §6 · `UNIVERSAL-IDENTITY-DICTIONARY-DETERMINATION.md` · `SCOPE-B-IDENTITY-CONTAINMENT-DETERMINATION.md` §5 |

---

## 1. Existing UID Dictionary Architecture

### 1.1 What exists

| Component | Path | Role |
|---|---|---|
| Dictionary | `engine/registry/universal/dictionary.py` (346 lines) | `IdentifierEntry`, `IdentifierDictionary`, `dictionary_for` |
| Identifier derivation | `engine/registry/universal/identity.py` (327 lines) | `deterministic_id`, `RegistryKind`, `register_kind`, grammar |
| Population source | `engine/nucleus/registry.py` | `NucleusRegistry`, `build_seed_registry` |
| Second projector | `engine/ceu/possessions.py` | `dictionary_for_existence` over `ExistenceRegistry` |
| Production entry point | `engine/nucleus/cli.py` `_cmd_dictionary` | `python -m engine.nucleus.cli dictionary` |

### 1.2 Current purpose

An **assigned-identifier** dictionary: it enumerates the identifiers actually minted by `deterministic_id`, so *"every minted id appears exactly once"* becomes a checkable statement. It is distinct from `engine/uckp/vocabulary.py`, which is a **term** dictionary governing which words may be used.

### 1.3 Current UID derivation flow

```
identity tuple (kind, namespace, natural_key)
        ↓  normalise → resolve_kind_code
        ↓  SHA-256 over the canonical tuple
UCOS-<CODE>-<12 hex>          e.g. UCOS-CAP-cef1ed1bb7c7
```

**Measured:** the same tuple yields the same identifier twice; a changed key yields a different one. Pure, total, counter-free.

### 1.4 Current persistence state — the gap in one line

`IdentifierDictionary.__slots__ = ("_entries",)`. **In-memory only.** `_cmd_dictionary` emits to stdout and writes nothing.

Serialisation is nonetheless **already complete**: `to_document()`, `to_json()`, `digest()`, `from_document()`.

### 1.5 Current missing capability

Not derivation, not verification, not serialisation, not replay — all four exist and pass. What is missing is **a written artifact, a producer that writes it, and a gate that measures it.**

---

## 2. Authority Validation

Required chain: **Canonical Identity Authority → Identity Registry → UID Dictionary Projection.**

| Property | Result | Evidence (executed) |
|---|---|---|
| Dictionary does **not** mint | **HOLDS** | No `category_seq`, `_seq`, `counter`, `itertools.count`, `next(` or `+= 1` in `dictionary.py` + `identity.py`. `deterministic_id` is a pure SHA-256 over the identity tuple. |
| Dictionary is **not** authoritative | **HOLDS** | Population arrives via `dictionary_for(registry)` / `dictionary_for_existence(registry)`. The dictionary holds only `_entries`; it declares no population of its own. |
| Dictionary is **derived truth** | **HOLDS** | `verify()` **re-mints every entry** from its recorded `(kind, namespace, natural_key)` and fails closed on any that does not reproduce. Measured over the production population: `count=212, status=PASS, parse_coverage=1.0, unreproducible=[], duplicated_natural_keys=[]`. |
| Identifier immutability | **HOLDS** | `add()` refuses re-binding an identifier to a different identity (`RegistrationValidationError`), and is idempotent for an identical entry. |

**VERDICT: NO VIOLATION. The chain is intact. Implementation may proceed to determination.**

### 2.1 One apparent conflict, resolved — recorded because it looked like a violation

`deterministic_id` emits `UCOS-<CODE>-<12 hex>`. `00-BOOK/DATA/constitutional-authority-alignment.json` declares only two planes and pins `id_shape: ^UCOS-[A-Z0-9]+-[0-9]{6}$` — which this shape does **not** match. That file never mentions `deterministic_id`.

This is **not** a second authority, on two independent grounds:

1. **The declared test is the counter.** `second_authority_test`: *"a mint is recognised by the counter it advances"*, `mint_markers = ["category_seq"]`. `deterministic_id` advances nothing.
2. **The plane is declared elsewhere.** `00-MASTER/UIS-001/uis-declaration.json` `identity_mechanisms` declares `MECH-EPIC001` — *"Universal Registry Platform identity"*, module `engine/registry/universal/identity.py` — as plane **P4 (logical)**: *"the logical, human- and program-facing name of a thing, independent of its durable identity."*

The AIF prohibition *"never content/order/path-derived"* binds **P2 durable** identity (`MECH-UKB`, the id-ledger). A P4 logical name derived from an identity tuple is what P4 is for. The two instruments answer different questions — *which mechanism is the authority* versus *which plane does each mechanism serve* — and they agree.

**Recorded as an observation, not a defect:** the alignment file's two-plane view is narrower than UIS-001's five-plane taxonomy, and a reader consulting only the former would not find `deterministic_id`. No change is proposed; both instruments are owned elsewhere.

---

## 3. B-02 Gap Determination

```json
{
  "capability": "B-02 UID Dictionary Persistence",
  "gap_id": "G3",
  "sanctioned_by": "UNIVERSAL-IDENTITY-DICTIONARY-DETERMINATION.md §4",
  "path_determined": "DERIVED TRUTH (SCOPE-B-IDENTITY-CONTAINMENT-DETERMINATION.md §5.4)",

  "required": {
    "persistent_derived_dictionary": true,
    "deterministic_replay": true,
    "reconstruction_capability": true,
    "validation": true,
    "evidence_generation": true
  },

  "current": {
    "derivation":            "PRESENT — deterministic_id, pure, counter-free",
    "population_projection": "PRESENT — dictionary_for (212 entries) and dictionary_for_existence",
    "serialisation":         "PRESENT — to_document / to_json / digest",
    "reconstruction":        "PRESENT — from_document; round-trip measured byte-identical",
    "validation":            "PRESENT — verify() re-mints every entry; status PASS over 212",
    "determinism":           "PRESENT BUT UNGATED — two CLI runs byte-identical, nothing measures it",
    "persisted_artifact":    "ABSENT — in-memory only; _cmd_dictionary writes nothing",
    "producer_registration": "ABSENT — no entry in 00-BOOK/DATA/generated-artifact-registry.json",
    "gate":                  "ABSENT — verify.sh contains ZERO references to nucleus",
    "evidence":              "ABSENT — no evidence artifact, no certification record"
  },

  "gap": [
    "G3-A  no written artifact — the dictionary exists only for the life of a process",
    "G3-B  no producer contract — nothing declares where it is written, by what, from which inputs",
    "G3-C  no gate — determinism, verification and replay all hold and none is measured",
    "G3-D  no generated-artifact registration — a written file would be an unregistered generated object",
    "G3-E  no evidence or certification record"
  ],

  "explicitly_out_of_scope": [
    "G4 temporal/lifecycle/evolution/certification state on IdentifierEntry",
    "G9 child index on the identifier plane",
    "GAP B-4 UCL-S-0320 evidence names the TERM vocabulary, not this dictionary — referred to UCL-000001's owner",
    "any change to UOBC-BSP-001"
  ]
}
```

---

## 4. Dependency Analysis

### Upstream (read; unchanged)
`engine/nucleus/registry.py` `build_seed_registry` · `engine/registry/universal/identity.py` · `engine/ceu/possessions.py` · `engine/uckp/identity.py` (UCKP-ART-05, supreme).

### Downstream consumers
**Measured: none in production.** `dictionary_for` is referenced only from `engine/tests/nucleus/*` and `engine/tests/ceu/*`, plus `engine/nucleus/cli.py`. A persisted artifact therefore breaks no existing reader — and *"deleting it changes no verdict, only the cost of reaching one."*

### Affected verification stages
| Stage | Impact |
|---|---|
| `pytest + coverage gate` | new tests join the suite |
| **UOBC-000001 birth contract** | the new artifact classifies under `UOBC-BSP-001`; as a producer output it must be `GENERATED_ARTIFACT` → `birth_required: false`, `MANDATORY_ABSENCE`. **`BSP-L-03` will FAIL CLOSED if it is given a birth record** — B-01 already guards B-02. |
| `registry validate` · `universal object governance` | the new file becomes a governed object (UGA count +1) |
| A new dictionary stage | **only if** the UVI stage registry and `verify.sh` are updated together (`UVI-L-03` is bidirectional), plus the `stages_digest` in `UAKOS-CLOSURE-008/validation-record.json` and its re-render |

### Possible regressions
| # | Risk | Control |
|---|---|---|
| R-1 | Written artifact not at a producer fixed point | Producer loop to fixed point, as Scope A and B-01 both required |
| R-2 | Artifact given a birth record | `BSP-L-03` fails closed — already certified |
| R-3 | Stage added in one reader only | `UVI-L-03` + `stages_digest` + `uisd-gate.yml` all reconcile or fail |
| R-4 | Non-determinism enters via the population | `verify()` re-mints; a determinism check must compare two independent builds |
| R-5 | The file read as authoritative | `authority: NONE — DERIVED TRUTH` in the document; `closed_set:false`, `upper_limit:null` already emitted |

### Confirmations
* **No duplicate authority** — §2, four properties measured.
* **No duplicate registry** — the artifact is a projection of a registry that already exists; it registers nothing.
* **No new identity mechanism** — `deterministic_id` is reused unchanged; no counter is opened.

---

## 5. Implementation Proposal *(proposal only — not authorized)*

### Architecture
```
build_seed_registry()            existing, unchanged
        ↓
dictionary_for(registry)         existing, unchanged
        ↓
IdentifierDictionary.to_document()   existing, unchanged
        ↓
[NEW] producer writes ONE artifact + [NEW] gate measures it
```

### Files affected
| Path | Change |
|---|---|
| `engine/nucleus/cli.py` | `--write` on the existing `dictionary` command — a producer, not a new CLI |
| `<owner>/…-IDENTIFIER-DICTIONARY.json` | **new** derived artifact. Home follows `producer_homes` convention; owner determination required (see below) |
| `00-BOOK/DATA/generated-artifact-registry.json` | one entry: all 18 declared fields |
| `engine/registry/universal/dictionary.py` | possibly none — serialisation is already complete |
| new gate module + `verify.sh` + `uvi-declaration.json` + `validation-record.json` | only if a stage is added; all four move together |

### Schema changes
**None required.** `to_document()` already emits `schema: ucos-universal-identifier-dictionary`, `version: 1.0.0`, `count`, `by_kind`, `entries`, `closed_set: false`, `upper_limit: null`.

### Tests required
Population projected exactly · round-trip `to_document → from_document → to_document` byte-identical · digest stable across rebuild · two independent builds byte-identical · `verify()` PASS with zero unreproducible · refusal paths (re-bind, malformed document, missing `entries`) · artifact holds **no** birth record (`BSP-L-03`) · openness fields present.

### Evidence requirements
Producer fixed point · determinism proof (two builds, one digest) · `verify()` report as evidence · generated-artifact registration · four-mode verification · evidence report · certification record.

### Verification impact
Stage cost is small — 212 entries, one registry build. If a stage is added it must be declared in the UVI registry **in the same change**, and the `stages_digest` re-rendered.

---

## 6. Open question requiring your decision

**Where does the artifact live, and who owns it?**

Repository Truth does not settle this: `producer_homes` binds each generated artifact to a programme home, and the two candidate owners each have a defect as a home —

* `00-MASTER/UCOS-NUCLEUS-001/` — the nucleus programme, but it is **documentation-only today** (9 `.md` files, no engine, no declaration), so it has no producer home pattern to follow.
* There is **no** `00-MASTER/UCOS-EPIC-001/` — the Universal Registry Platform that owns `deterministic_id` (`MECH-EPIC001`) has no Operational Memory home at all.

Choosing either would be creating a programme home by implication rather than by determination, which Scope B forbids. **This is the one item I cannot decide from Repository Truth, and it must be settled before implementation.**

---

## 7. Discovery validation

| Requirement | Status |
|---|---|
| No code written | **CONFIRMED** |
| No files modified | **CONFIRMED** — this report is the only new file |
| No identifiers minted | **CONFIRMED** — `category_seq` unchanged at 117 |
| No registries mutated | **CONFIRMED** |
| `UOBC-BSP-001` untouched | **CONFIRMED** — no constitutional dependency required it |
| MCP-002 not updated | **CONFIRMED** |
| No completion claimed | **CONFIRMED** — B-02 is DISCOVERY COMPLETE, IMPLEMENTATION NOT AUTHORIZED |

---

*End of B-02-UID-DICTIONARY-PERSISTENCE-DISCOVERY.md*
