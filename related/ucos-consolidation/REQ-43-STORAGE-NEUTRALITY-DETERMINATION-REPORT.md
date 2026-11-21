# REQ-43 — STORAGE NEUTRALITY DETERMINATION REPORT

**Checkpoint:** `03179308` (integration/recovery-001)
**Compiled:** 2026-08-22
**Phase:** 7A — discovery and determination only. **No implementation performed. No certification claimed.**
**Question:** Should `KnowledgeStore` (UKDA) be placed behind a common persistence abstraction shared with `engine/uckp`'s `PersistenceAdapter`?

---

## 1 — Inventory: `PersistenceAdapter` (`engine/uckp/persistence.py`, 716 lines)

### 1.1 Interface / contract

| Member | Signature | Kind |
|---|---|---|
| `kind` | `str` class attribute | declared |
| `locator` | `-> str` | abstract property |
| `write` | `(objects: Sequence[UCKO]) -> PersistenceReceipt` | **abstract** |
| `read` | `() -> tuple[UCKO, ...]` | **abstract** |
| `capabilities` | `() -> frozenset[str]` | concrete, advisory — "never consulted by the law" |
| `describe` | `() -> dict[str, object]` | concrete |
| `round_trip` | `(objects) -> tuple[UCKO, ...]` | concrete |
| `verify_contract` | `(objects) -> None`, raises `PersistenceContractError` | concrete, fail-closed |

The contract is **two abstract methods over one homogeneous collection**, verified by
`universe_digest()` equality plus per-object `require_integrity()` and `==` identity.
The module's own docstring states the design intent verbatim: *"The contract is
deliberately tiny, because a large contract is one that only some technologies can
honour… Nothing about files, transactions, schemas, regions, indexes or query languages
appears in it."*

### 1.2 Implementations — 10, all in the same module

`MemoryPersistence`, `FilesystemPersistence`, `GitPersistence`, `DatabasePersistence`
(sqlite3), `ObjectStoragePersistence`, `KnowledgeGraphPersistence`,
`DistributedLedgerPersistence`, `CloudPersistence`, `OfflineArchivePersistence`,
`FutureStoragePersistence`. `KNOWN_PERSISTENCE_KINDS` is an open tuple (Article 17).

### 1.3 Ownership and dependencies

- **Owner:** UCKP Layer Zero, Article 9. Constitutional basis is stated in-module.
- **Imports:** `engine.uckp.canonical`, `engine.uckp.errors`, `engine.uckp.ucko`, plus
  stdlib only (`base64`, `io`, `json`, `sqlite3`, `tarfile`, `abc`, `pathlib`).
- **Production consumers — measured, not assumed** (`grep` over the repo, excluding tests):

  | Call site | Use |
  |---|---|
  | `engine/uckp/universe.py:357` | `build_persistence_suite(base)` → `universe.persistence` (all 10) |
  | `engine/uckp/universe.py:86` | `persistence: tuple[PersistenceAdapter, ...]` field |
  | `engine/uckp/cli.py:152` | `verify_interchangeable(universe.persistence, …)` |
  | `engine/uckp/validation.py:672` | `verify_interchangeable(adapters, objects)` |

  **Every production consumer is inside `engine/uckp`.** There is no consumer of
  `PersistenceAdapter` anywhere else in the repository.

- **Tests:** `engine/tests/uckp/test_projection_persistence_execution.py` — **52 passing**,
  re-executed this pass, including
  `test_every_persistence_technology_round_trips_the_universe_identically` and an
  assertion that `build_persistence_suite` returns exactly 10 adapters.

### 1.4 The property the plurality actually serves

`build_persistence_suite()` instantiates **all ten adapters at once** and
`verify_interchangeable()` runs the identical contract across them and compares digests.
The plurality is not a deployment choice — it is the **evidence**. UCKP's universe is a
portable artifact whose constitutional claim is that it survives transfer between
mechanisms, and the suite is how that claim is measured.

---

## 2 — Inventory: `KnowledgeStore` (`engine/knowledge/store.py`, 421 lines)

### 2.1 Persistence surface — four streams, three types

| Stream | File constant | Payload type | Semantics |
|---|---|---|---|
| Canon | `CANON_FILE` | `CanonicalKnowledgeObject[]` | current state only, overwritten |
| Decisions | `DECISIONS_FILE` | `DecisionRecord[]` | current state only, overwritten; **optional on read** |
| History | `HISTORY_FILE` | archived CKO **records**, keyed by `cko_id` | **append-only**, written by `save()` before overwrite (`DEC-ADR-0025`, P4-F-004) |
| Provenance | `PROVENANCE_FILE` | `ProvenanceChain[]`, keyed by `subject` | sibling file, deliberately outside the CKO content-addressed core (`DEC-ADR-0025`, P4-F-006) |

### 2.2 Operations

| Operation | Method | Behaviour |
|---|---|---|
| load | `load()` | reads canon (required) + decisions (**fail-soft**, absent ⇒ `[]`) |
| save | `save(base) -> (Path, Path)` | `_guard_writable()` → `mkdir` → **`_archive_replaced_versions()`** → write canon → write decisions |
| archive | `_archive_replaced_versions()` | diffs on-disk `content_sha256` vs incoming; appends changed/disappearing records to history; **fail-soft** on unreadable prior state |
| history | `history(cko_id)` | prior versions, oldest first; `()` when never overwritten — never an error |
| provenance | `save_provenance()` / `load_provenance()` | keyed by `chain.subject`; `{}` when never saved |

### 2.3 Serialization boundary

Exactly two private methods touch the encoding:

- `_read_json(filename)` — `json.loads(path.read_text(encoding="utf-8"))`, wraps
  `JSONDecodeError` into `KnowledgeSourceError`.
- `_write_json(filename, document)` — `json.dumps(document, sort_keys=True, indent=2,
  ensure_ascii=False) + "\n"`.

Determinism is a **stated property** of the module docstring: *"serialization is stable
(records sorted by id, no wall-clock) so a round-trip is byte-identical."*

### 2.4 Two guards that are constitutional, not mechanical

| Guard | Location | What it enforces |
|---|---|---|
| `_guard_writable()` | `store.py:277-288` | **DP-03** — refuses to write canonical knowledge anywhere inside the frozen corpus, via `find_frozen_writes()` on the repo-relative path. Returns early (allowed) when the directory is outside the repository. |
| `_path()` | `store.py:237-243` | refuses a `filename` whose resolved path escapes the store directory |

Both are expressed **in terms of a filesystem path relative to the repository root**.

### 2.5 Ownership and consumers

- **Owner:** UKDA Part 04/13. Governing law: the **Knowledge Once Principle** — *"Knowledge
  is authored exactly once here; everything else in the repository is generated, derived,
  linked, validated, certified, or consumed from this source."*
- **Production consumers — measured (14 call sites, 5 modules):**
  `engine/knowledge/cli.py` (×5), `engine/knowledge/integration/cli.py`,
  `engine/knowledge/ukip/cli.py` (×2), `intelligence/kernel/knowledge.py:195`,
  `intelligence/realization/knowledge.py:99`. Three `intelligence/realization/generators/*`
  files emit `KnowledgeStore()` as **generated source text**, not as a live call.
- **Every one** constructs `KnowledgeStore(<directory>)` and reads/writes the repository's
  own on-disk canonical knowledge. `intelligence/kernel/knowledge.py:22` states it
  explicitly: *"owner, `engine.knowledge.store.KnowledgeStore`; no second reader exists."*
- **Tests:** `engine/tests/knowledge/test_store.py` — **21 passing**; whole
  `engine/tests/knowledge/` tree — **618 passing**. Both re-executed this pass.

---

## 3 — Determination

### **B — forced abstraction causing architectural damage.**

Not "no abstraction is possible." The pattern *is* reusable in shape. The determination is
that applying it **here** buys a capability nobody has asked for at the cost of dissolving
two guarantees that were certified four decisions ago.

The four findings below are stated against the directive's own five criteria.

### 3.1 Granularity and cardinality mismatch (the roadmap understated this)

`UCOS-ARCHITECTURAL-OPENNESS-ROADMAP.md` Phase 3 identified one obstacle: `PersistenceAdapter`
is hard-typed to `UCKO`, so a `Protocol`/`TypeVar` generalization would be needed. That is
true and it is the *smaller* half of the problem.

The larger half: `PersistenceAdapter` models **one homogeneous collection**
(`Sequence[UCKO]` in, `tuple[UCKO, ...]` out, one `universe_digest`). `KnowledgeStore`
persists **four streams of three different types** with **different write disciplines**
(canon and decisions overwrite; history appends; provenance is keyed and independent).

Neither mapping survives contact:

- **Four adapters, one per stream** — fractures `save()`'s ordering invariant. `save()` is
  *archive-then-write*: the history append must complete before canon is overwritten, or a
  prior version is lost. Four independent `write()` calls have no such ordering, and
  `PersistenceAdapter` has no transaction concept (deliberately — see §1.1).
- **One adapter over a composite document** — then `objects` is no longer a sequence of
  content-addressed objects, so `universe_digest()`, per-object `require_integrity()` and
  the `recovered == original` check in `verify_contract()` all stop applying. What remains
  is a bytes-in/bytes-out interface wearing `PersistenceAdapter`'s name — the contract's
  entire fail-closed value is gone.

### 3.2 DP-03 would stop being enforced without being repealed — **criterion 1 fails**

`_guard_writable()` enforces DP-03 by computing `self._dir.relative_to(_repository_root())`
and consulting `find_frozen_writes()`. It has a documented early return: *"outside the
repository (e.g. a test tmp dir) — allowed."*

Under a `MemoryPersistence`, `DatabasePersistence` or `CloudPersistence` backend there is
no repo-relative directory at all. The guard does not fail — **it silently succeeds**. The
frozen-corpus rule is not repealed; the surface it applies to is dissolved. That is a
duplicate/vacated persistence authority in the precise sense criterion 1 forbids: DP-03's
enforcement point would move from "the one place canonical knowledge is written" to
"whichever adapter happens to be configured."

### 3.3 REQ-14 and REQ-34 are at regression risk — **criterion 2 fails**

Both were certified **this session** by `DEC-ADR-0025`:

- REQ-14 — prior knowledge version retained on save (`_archive_replaced_versions`).
- REQ-34 — provenance chains persist (`save_provenance`/`load_provenance`).

Both are implemented **as ordering and sibling-file semantics at the filesystem boundary** —
exactly the layer an adapter would replace. `PersistenceAdapter`'s contract carries no
notion of "archive the prior value first" or "this sibling stream is keyed independently."
Any adapter-based `KnowledgeStore` must re-implement both **above** the adapter (in which
case the adapter is only handling raw bytes and §3.1's second horn applies) or **inside each
of ten adapters** (in which case ten implementations now each own a constitutional
guarantee — the opposite of one owner per obligation).

### 3.4 No second consumer exists, and the store is singular by law — **criterion 4 fails**

All 14 production call sites point at the repository's own canonical knowledge directory.
The Knowledge Once Principle makes that home **singular by design**. "Run the canonical
knowledge store on two storage technologies simultaneously" is not a scenario this
repository has; it is a scenario the checklist has.

This is precisely the case `UCOS-ARCHITECTURAL-OPENNESS-ROADMAP.md` Phase 2 already made
against four of the five persistence-shaped gaps. The same reasoning applies to the fifth —
the roadmap classified `KnowledgeStore` as the one "genuine candidate" on the strength of
type-shape similarity, before the four-stream structure and the DP-03 coupling had been
read.

### 3.5 Criterion 3 — existing UCKP tests

Would be **satisfiable but only by accident of scope**: a `Protocol` generalization that
leaves `write`/`read` signatures variance-compatible would keep all 52 tests green. This
criterion does not discriminate, and is noted as passing rather than presented as support.

### 3.6 Criterion 5 — technology independence of the result

**Fails.** Any abstraction faithful enough to preserve §3.2 and §3.3 must carry
repo-relative path semantics, archive-before-write ordering, and keyed sibling streams.
Those are filesystem-and-git shaped. An abstraction that drops them is technology-independent
and **wrong**; one that keeps them is correct and **not technology-independent**.

### 3.7 Scorecard

| Required criterion | Verdict |
|---|---|
| No duplicate persistence authority | **FAIL** (§3.2 — DP-03's enforcement point vacates) |
| No behavior regression | **FAIL** (§3.3 — REQ-14/REQ-34 ordering and sibling-stream semantics) |
| Existing UCKP persistence tests unchanged | pass (§3.5 — non-discriminating) |
| KnowledgeStore gains real capability | **FAIL** (§3.4 — nominal only; no second consumer) |
| Abstraction remains technology independent | **FAIL** (§3.6 — mutually exclusive with fidelity) |

**Proceed condition is not met. The directive's own instruction applies: do not create an
abstraction for a single consumer.**

---

## 4 — Impact analysis

### 4.1 If determination B is accepted (recommended)

| Dimension | Impact |
|---|---|
| Code | **None.** No file changes. |
| Tests | **None.** 21 / 618 / 52 baselines stand unchanged. |
| Gates | **None.** No gate consults `KnowledgeStore`'s storage technology. |
| Requirement matrix | REQ-43 moves `OPEN GAP` → `GOVERNED CLOSURE`, pending a `CEP-002 Article 28` decision that records the decline and its reasoning. It does **not** become `CERTIFIED` — nothing was built. |
| Precedent | Consistent with REQ-15 (`disclosed non-openness by design`) and REQ-48 (`correctly closed, not a gap`), both already adjudicated in this repository. |
| Residual risk | If a genuine second storage target ever appears, this determination must be re-opened. It is a determination about the *present* consumer set, not a permanent prohibition. That boundary is stated so it cannot be read as a stronger claim than it is. |

### 4.2 If determination B is overridden and the abstraction is built anyway

| Dimension | Impact |
|---|---|
| Files changed | `engine/uckp/persistence.py` (generalize to `Protocol`), `engine/knowledge/store.py` (delegate), + a guard-relocation module |
| Regression surface | 618 `engine/tests/knowledge/` tests, 52 uckp persistence tests, plus `intelligence/kernel/knowledge.py` and `intelligence/realization/knowledge.py` |
| New obligations created | DP-03 enforcement must be re-sited and re-tested; REQ-14 archive ordering and REQ-34 provenance keying must be re-proven above the adapter |
| Decisions that must be re-validated | `DEC-ADR-0025` (REQ-14 + REQ-34) — its implementation moves |
| Honest cost | Three certified obligations re-opened to add zero capability any current consumer uses |

---

## 5 — Migration design

Recorded as the directive requires — for the path **actually recommended**, plus the
conditional design if B is overridden.

### 5.1 Recommended — governed decline (no migration)

1. Author `adr/0028-req-43-knowledgestore-storage-neutrality-decline.md`, registered as a
   `CEP-002 Article 28` decision, citing §3.1–§3.6 of this report as its evidence.
2. Amend `UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md` REQ-43: status
   `OPEN GAP` → `GOVERNED CLOSURE`; `Required action` → "none — declined by decision";
   `Gap` → "not a gap — adjudicated closure, re-openable on a real second storage target."
3. Amend `UCOS-ARCHITECTURAL-OPENNESS-ROADMAP.md` Phase 2/3 to record that the
   "genuine candidate" classification was made on type-shape similarity alone and is
   **superseded** by this report's four-stream and DP-03 findings.

No code, no tests, no gates.

### 5.2 Conditional — the narrower seam that *is* legitimate, if any change is wanted

If the intent is "reduce coupling to JSON" rather than "swap storage technology," there is a
real, small, single-purpose seam that does **not** trip any of §3.2–§3.6:

**Extract the serialization boundary only.** `_read_json` / `_write_json` are the *only* two
methods that name an encoding. A `KnowledgeCodec` protocol (`encode(Mapping) -> str`,
`decode(str) -> Any`) injected into `KnowledgeStore.__init__` would:

- leave `_guard_writable()` and `_path()` **inside `KnowledgeStore`**, so DP-03 keeps its
  single enforcement point (§3.2 satisfied);
- leave `save()`'s archive-then-write ordering and the four-stream layout **untouched**, so
  REQ-14/REQ-34 are not re-opened (§3.3 satisfied);
- stay technology-independent in the only sense that applies here — canonical encoding,
  not storage mechanism (§3.6 satisfied).

It still has **no second consumer today** (§3.4 unsatisfied), so this report does **not**
recommend building it either. It is recorded so the option is on the table with an honest
label rather than rediscovered later.

### 5.3 Conditional — full abstraction, if B is overridden

Sequenced so each step is independently reversible:

1. Add `PersistedObject` `Protocol` in a new `engine/uckp/contracts.py`:
   `to_dict()`, `from_dict()` (classmethod), `require_integrity()`, and a **uniform identity
   accessor**. Note the real friction: `UCKO.ucko_id` is a *property*, `CanonicalKnowledgeObject.cko_id`
   is a *field* — the protocol needs one agreed name, which means touching one of the two
   object models or introducing an extractor callable.
2. Re-type `PersistenceAdapter` generic over that protocol. Run the 52 uckp tests — must be
   green with **zero test edits** (criterion 3).
3. Relocate DP-03 into an explicit `WriteAuthority` collaborator that every adapter must be
   constructed with, with a fail-closed default. Add a test proving a memory-backed store
   still refuses a frozen-corpus target.
4. Re-prove REQ-14 ordering and REQ-34 keying **above** the adapter, with the
   `DEC-ADR-0025` tests re-pointed and passing.
5. Only then delegate `KnowledgeStore`'s four streams.
6. Introduce a real second consumer, or stop at step 5 and record that the abstraction has
   one.

---

## 6 — Acceptance criteria

### 6.1 For the recommended governed decline

| # | Criterion | How verified |
|---|---|---|
| A1 | A `CEP-002 Article 28` decision exists recording the decline, its five-criterion scorecard, and its re-open condition | decision registered in `00-MASTER/UCDA-000001/01-CONSTITUTIONAL-DECISION-REGISTER.md` |
| A2 | REQ-43 reads `GOVERNED CLOSURE`, never `CERTIFIED` | matrix diff |
| A3 | Zero source files changed | `git diff --stat` over `engine/` is empty for this change |
| A4 | Baselines unchanged | `engine/tests/knowledge/` = 618 pass; `engine/tests/uckp/test_projection_persistence_execution.py` = 52 pass |
| A5 | The roadmap's superseded "genuine candidate" line is corrected, not silently left standing | `UCOS-ARCHITECTURAL-OPENNESS-ROADMAP.md` diff |

### 6.2 For the full abstraction, were it built (binding if B is overridden)

| # | Criterion |
|---|---|
| B1 | All 52 `engine/tests/uckp/test_projection_persistence_execution.py` tests pass with **zero edits to the test file** |
| B2 | All 618 `engine/tests/knowledge/` tests pass; any edit to a `test_store.py` assertion is a **regression**, not an update |
| B3 | A new test proves a **non-filesystem** backend still refuses a frozen-corpus write target (DP-03 preserved) |
| B4 | A new test proves archive-before-overwrite ordering holds through **every** adapter (REQ-14 preserved) |
| B5 | A new test proves provenance round-trips keyed by `subject` through **every** adapter (REQ-34 preserved) |
| B6 | `verify_interchangeable` runs the identical contract over **both** `UCKO` and `CanonicalKnowledgeObject` universes and compares digests |
| B7 | Exactly one owner for DP-03 enforcement after the change, named in the decision |
| B8 | A **real** second consumer exists, or the decision states in its own text that the abstraction currently has one |

---

## 7 — Boundary statement

This report determines that a shared storage abstraction is **not warranted for the present
consumer set**, on evidence read from the code at checkpoint `03179308`. It does not claim
that `KnowledgeStore` is technology-independent, that storage neutrality has been achieved,
or that a future second storage target could not change the answer. REQ-43 is not closed by
this report — this report is the evidence a closing decision would be built on.

**Stopped before implementation, as directed.**
