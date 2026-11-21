# B-02 — UID Dictionary Persistence · Certification Evidence Report

| Field | Value |
|---|---|
| CAPABILITY | **B-02** — UID Dictionary Persistence (gap `G3`) |
| ARTIFACT | `00-MASTER/UCOS-NUCLEUS-001/UCOS-NUCLEUS-IDENTIFIER-DICTIONARY.json` |
| OWNER | `UCOS-NUCLEUS-001` |
| CONSTITUENT AUTHORITY | **NONE** |
| PREDECESSORS | `B-02-UID-DICTIONARY-PERSISTENCE-DISCOVERY.md` · `B-02-OWNERSHIP-RESOLUTION-REPORT.md` · `B-02-LIFECYCLE-LINKAGE-GAP-DETERMINATION.md` |
| PRIOR BASELINE | `UOBC-BSP-001` — CERTIFIED, **unmodified** |

---

## 1. Objective

Persist the already-derived UID Dictionary projection, closing `G3-A`…`G3-E`, while preserving single identity authority, derived truth, deterministic replay, append-only evolution, zero duplicate registry and zero duplicate authority.

Discovery established that derivation, projection, verification, serialisation and replay **already existed and passed**. What was missing was a written artifact, a producer contract, a registration and a gate. B-02 adds exactly those four.

---

## 2. Architecture

```
build_seed_registry()                      existing, unchanged
        ↓
dictionary_for(registry)                   existing, unchanged
        ↓
IdentifierDictionary.to_document()         existing, unchanged
        ↓
[NEW] _dictionary_document(...)            metadata envelope
        ↓
[NEW] dictionary --write                   the producer
        ↓
00-MASTER/UCOS-NUCLEUS-001/UCOS-NUCLEUS-IDENTIFIER-DICTIONARY.json
        ↓
00-BOOK/DATA/generated-artifact-registry.json   one entry + one producer home
```

**Population:** 212 entries — CAPABILITY 129 · NUCLEUS 43 · COMPOSITION 26 · LAYER 14, equal to `len(subjects) + len(capabilities)` of the seed registry, measured.

---

## 3. Ownership

| Field | Value | Existing basis |
|---|---|---|
| Owner | `UCOS-NUCLEUS-001` | UGA `ownership_rules` — *"the programme directory IS the owner"*; existing owner with 9 pre-existing objects |
| Classification | `GENERATED_ARTIFACT` / derived projection of a registry | 344/345 precedent |
| Lifecycle | `REGENERATED` | 345/345 |
| Registry | `00-BOOK/DATA/generated-artifact-registry.json` | the one generated-artifact registry |
| Mutation class | `GENERATED_ARTIFACT → UCOS-GENERATED-ARTIFACT-REGISTRY-001 → producer → Phase 8 → Phase 9` | `mutation-governance-boundary.json` |

**Frozen-path authority, checked before writing `00-BOOK/`:** `.github/workflows/ec1-ci.yml` runs `ec1-frozen-guard` on a list that explicitly filters `^00-BOOK/(DATA|REGISTRIES|CONTROL-TOWER|PORTAL|SCHEMAS|tools)/`, with the authority chain recorded inline (UCCEP-000006 X-4/X-5). The register edit is sanctioned, not tolerated.

---

## 4. Implementation

### Files added
| Path | Role |
|---|---|
| `00-MASTER/UCOS-NUCLEUS-001/UCOS-NUCLEUS-IDENTIFIER-DICTIONARY.json` | the artifact — 212 entries |
| `engine/tests/nucleus/test_identifier_dictionary_persistence.py` | 26 tests |
| `B-02-LIFECYCLE-LINKAGE-GAP-DETERMINATION.md` | the referred lifecycle vacancy |

### Files modified
| Path | Change |
|---|---|
| `engine/nucleus/cli.py` | `DICTIONARY_ARTIFACT`, `_dictionary_document()`, `--write`; module docstring amended |
| `00-BOOK/DATA/generated-artifact-registry.json` | +1 entry, +1 producer home, **0 deletions** |
| `B-02-OWNERSHIP-RESOLUTION-REPORT.md` | correction recorded (D-5) |

**Not modified:** `engine/registry/universal/dictionary.py` (serialisation was already complete) · `identity.py` · `id-ledger.json` · `birth-ledger.json` · `ucl-stage-manifest.json` · `UOBC-BSP-001` · any authority declaration.

### The one declared-property change, stated rather than left as drift
`engine/nucleus/cli.py` declared *"The CLI writes no file — a determination is materialised by the authority that owns the truth it would enter."* B-02 narrows this and says so in the docstring: `dictionary --write` materialises **exactly one** artifact, into the Operational Memory home of the programme that **owns** it — the same pattern `engine/uaue/gate.py` already uses for 19 artifacts owned by `UAUE-000001`. The original ground is preserved, not abandoned. No other subcommand writes, and nothing writes without the flag.

---

## 5. Validation

| Property | Result |
|---|---|
| **Authority** — dictionary cannot mint | `deterministic_id` is pure; same tuple → same id; no counter in either module |
| **Persistence** — artifact exists | present at the declared path, tracked |
| **Determinism** — two generations identical | byte-identical, measured |
| **Replay** — delete → regenerate → identical | performed; regeneration compared byte-for-byte |
| **Integrity** — digest matches regenerated projection | equal; every one of the 212 entries re-mints from its own tuple |
| **Negative — mutation detected** | a forged `universal_id` → `verify()` `FAIL`, listed `unreproducible` |
| **Negative — duplicate rejected** | second differing assignment → `RegistrationValidationError`; identical re-assignment idempotent |
| **Negative — invalid identity rejected** | bad namespace, spaced key, empty key → `RegistrationError` |
| **Write scope** | producer run leaves `git status` byte-unchanged apart from the declared artifact |
| **No wall clock** | zero timestamp matches in the document |
| **Openness** | `closed_set: false`, `upper_limit: null` |

### Birth-scope compatibility (`UOBC-BSP-001`, certified, unmodified)
The artifact classifies `GENERATED_ARTIFACT` → `birth_required: false`, `MANDATORY_ABSENCE`. **`BSP-L-03` refuses a birth record for it** — exercised with a URN that genuinely resolves to its path. B-01 governs B-02, as predicted at discovery.

---

## 6. Deterministic proof

```
write #1                     → 18967349ca539ed7
write #2                     → 18967349ca539ed7      identical
delete + regenerate          → 18967349ca539ed7      identical
committed bytes == fresh projection                  identical
registry_digest (source)     == build_seed_registry().digest()
```

Producer **fixed point at pass 1** across the full chain (`dictionary --write` · `rie build` · `uga run` · `uaie --render` · `ucaf --render` · `uakos --render`).

---

## 7. Defects discovered

All five were introduced by this implementation; none was a pre-existing architectural defect.

### D-1 — JSON splice corrupted the register
* **Detection** — `json.load` raised at line 11627 immediately after the edit.
* **Root cause** — a regex-located splice offset by one brace.
* **Fix** — reverted, then discovered the register uses **hand-authored inline arrays**, so re-serialising would reformat ~11k lines. Redone as an exact-anchor text insert.
* **Regression prevention** — every subsequent edit validated by `json.load` plus `git diff --numstat` showing **0 deletions**.

### D-2 — artifact written but untracked
* **Detection** — `test_11_every_canonical_artifact_is_tracked` failed.
* **Root cause** — a canonical artifact must be tracked; a new file is not.
* **Fix** — `git add`.
* **Regression prevention** — the existing invariant, unchanged.

### D-3 — a vacuous test of my own
* **Detection** — `test_giving_the_artifact_a_birth_record_is_refused` failed, and the reason mattered: the forged URN used `ucos.determination`, which resolves to `<name>.md` and **can never name a `.json` artifact**. Had it passed, it would have proved nothing.
* **Root cause** — the test asserted a refusal on an input the resolver cannot produce.
* **Fix** — forged a `ucos.master` URN, verified to resolve to exactly the artifact path.
* **Regression prevention** — the test now fails if `BSP-L-03` stops refusing, which is what it is for.

### D-4 — wrong exception class asserted
* **Detection** — `test_an_invalid_identity_is_rejected` failed: the call *was* refused, with `NamespaceError`, not `RegistrationValidationError`.
* **Root cause** — the test asserted an implementation detail rather than the contract.
* **Fix** — assert the shared base `RegistrationError`, parametrised over three malformed identities.
* **Regression prevention** — the contract, not one subclass, is now the assertion.

### D-5 — a claim in my own ownership report was false
* **Detection** — `test_1_the_register_declares_a_home_for_every_producer_it_names` failed under `--fast`.
* **Root cause** — the report concluded *"neither an operational home nor a `producer_homes` row must be created"*, generalising the RIE precedent past its boundary. The invariant is `owners <= homed` **only for artifacts whose path starts with `00-MASTER/`**; RIE is exempt because its artifacts live in `intelligence/`. Siting this artifact in `00-MASTER/` invokes the pattern that *requires* a home.
* **Fix** — declared the producer home with the nine pre-existing documents as `authored_inputs`, so `test_1_live_every_tracked_file_in_a_declared_home_is_declared` also holds. This brings **all ten** files in the directory under declaration — more governance, not a bypass. **No operational home was created**; the directory already existed with 9 registered objects.
* **Regression prevention** — both invariants now cover the directory; and the false sentence was **corrected in the ownership report itself** rather than left standing.

---

## 8. Regression controls

| Control | Guards |
|---|---|
| `test_the_committed_bytes_equal_a_freshly_computed_projection` | any hand-edit of the artifact |
| `test_every_committed_entry_re_mints_from_its_own_tuple` | any entry that stopped being derived |
| `test_the_producer_writes_the_artifact_and_nothing_else` | producer write-scope creep |
| `test_write_refuses_the_context_projection` | a different document overwriting the declared one |
| `BSP-L-03` | the artifact acquiring an independent birth identity |
| `test_1_*` (canonical governance) | an undeclared file in the declared home |
| `test_11_every_canonical_artifact_is_tracked` | an untracked canonical artifact |

---

## 9. Certification evidence

| Mode | Exit | Stages | Tests | Failed | Coverage |
|---|---|---|---|---|---|
| `--fast` | **0** | 3/3 | 11,914 | 0 | 97% |
| `--change` | **0** | 9/9 | 11,914 | 0 | 97% |
| `--integration` | **0** | 14/14 | 11,914 | 0 | 97% |
| `--full` | **0** | **15/15** | 11,914 | 0 | 97% |

**Gates:** UVI 10/10 · UCPA 8/8 · UISD 10/10 · UGA 29/29 · UOBC+BSP 14/14 · nucleus dictionary exit 0.
**Derived state:** fixed point at pass 1 · `ruff check`/`format --check` clean · **0 unstaged modifications**.
**Identity invariants:** `category_seq` **117 (unchanged — no counter opened)** · births **38 (unchanged — no birth minted)**.

---

## 10. Certification Decision

# CERTIFIED

`B-02 UID Dictionary Persistence` is certified. `G3-A`…`G3-E` are closed: the artifact is written, the producer contract is declared, the registration exists with a producer home, verification covers authority, determinism, replay, integrity and three refusals, and evidence is generated.

The lifecycle vacancy (`GAP B-4`) is **determined and referred**, not claimed — recorded in `B-02-LIFECYCLE-LINKAGE-GAP-DETERMINATION.md`. It does not block certification: the artifact is governed on the ownership, mutation-class and birth-scope planes, all three occupied and measured.

---

*End of B-02-UID-DICTIONARY-PERSISTENCE-EVIDENCE-REPORT.md*
