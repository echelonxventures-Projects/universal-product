# PHASE 1 — GOVERNANCE-INDEPENDENT REMEDIATION IMPLEMENTATION REPORT

| Field | Value |
|---|---|
| Phase | 1 — Implementation of the eleven change units approved in Phase 0.5 |
| Authority for scope, ordering, verification | `PHASE05-GOVERNANCE-INDEPENDENT-REMEDIATION.md` |
| Units implemented | R-1 … R-11 — **all eleven, complete** |
| Defects closed | E1-F1, E1-F2, E1-F4, E1-F5, E1-F6, E1-F7, E2-F1, E2-F2, E2-F3, E2-F4, E2-F5, E2-F6 — **12 of 12** |
| Files modified | 3 |
| Test outcome | `platform/tests/test_ledger_authority.py` **77 passed** (was 40); regression batch **331 passed, 1 pre-existing failure** |
| Ruff | no new violations (3 pre-existing in `uga_engine.py` unchanged) |
| Live ledger | **byte-identical** — `sha256 8471e709…c20b`, `git status --porcelain 00-BOOK/DATA/` empty |
| E-4A | **still blocks every production write** — verified by execution against the live ledger |
| Governance content | **NONE.** FD-1, FD-2, FD-3′, FD-4, FD-5 not answered, not assumed, not approached. `_verify_permit`'s permit path unmodified. No permit issuance mechanism, no audit-event definition, no mutation definition, no new authority. |
| Excluded and untouched | E1-F3, E-3, E-4A, RES-1, RES-2 |

---

## 1. Implementation summary

### 1.1 What was applied

| Unit | Defect | Change | Wave |
|---|---|---|---|
| R-1 | E1-F7 | `read_preimage_bytes` — one read returned as both raw bytes and parsed document | 0 |
| R-3 | E1-F2 | `_ledger_lock` — exclusive `flock` on the ledger's directory, spanning all of `commit()` | 0 |
| R-4 | E1-F4 | record-body refusal in `assert_append_only`, via new `_record_index` | 0 |
| R-6 | E1-F6 | duplicate-identifier refusal, within and across all four identity maps | 0 |
| R-9 | E2-F4 | `NO_ALLOCATION` requires the proposed document to equal the pre-image | 0 |
| R-10ₐ | E2-F5 | `indirect_ledger_writes` — AST measurement of ledger references handed to a writing parameter | 0 |
| R-11 | E2-F6 | serializer round-trip equivalence test (test-only; no production code) | 0 |
| R-2 | E1-F1 | pre-write byte re-check between authorization and `writer` | 1 |
| R-5 | E1-F5 | (a) `history` classified into `NON_ALLOCATION_KEYS`; (b) `history` prefix-preservation refusal | 1 |
| R-7 | E2-F1, E2-F2 | post-write parse; persisted document must equal the authorized one; pre-image restored on divergence | 1 |
| R-8 | E2-F3 | `bytes_changed` rendered in `format_report`; `_refuse_unmoved_allocation` assertion | 2 |
| R-10ₜ | E2-F5 | `LEDGER-INV-01` `why` text corrected to state its true scope | 2 |

### 1.2 Files modified

| File | Added | Removed | Before | After |
|---|---|---|---|---|
| `00-BOOK/tools/ledger_authority.py` | 381 | 41 | 593 | 933 |
| `00-MASTER/UCOS-UGA-001/uga_engine.py` | 101 | 2 | 2092 | 2191 |
| `platform/tests/test_ledger_authority.py` | 1091 | 12 | 301 | 1380 |
| **Total** | **1573** | **55** | | |

No other file was touched. `register.sh`, `ukb.py`, `uga-declaration.json`,
`mutation-governance-boundary.json` and every file under `00-BOOK/DATA/` are unchanged.

### 1.3 A note on the baseline, because it is not the obvious one

`00-BOOK/tools/ledger_authority.py` is `AM` — added to the index but never committed — and
its **index blob is a stale 285-line draft**, not the 593-line working-tree file Phase 0
measured. `00-MASTER/UCOS-UGA-001/uga_engine.py` is ` M`, so its `HEAD` blob predates the
uncommitted work that introduced `LEDGER-INV-01` entirely (`grep -c LEDGER-INV-01`: 0 in
`HEAD`, 5 in the working tree). **Neither git reference is a valid pre-Phase-1 baseline**,
and using one would have produced false metrics and a false regression finding — the first
invariant comparison run for this report did exactly that, reporting `LEDGER-INV-01` as
"newly added by Phase 1" when it had simply been absent from `HEAD`.

Both baselines were therefore reconstructed by inverting this phase's edits, and each
reconstruction was **verified faithful before being used**:

- `uga_engine.py`: the reconstruction yields 30 invariants with `LEDGER-INV-01 PASS,
  measured=2208, violations=0` — see §4.3.
- `ledger_authority.py`: the reconstruction reproduces **all twelve Phase-0 defects
  byte-for-byte identically to the E1/E2 reports**, including
  `E2-F1 -> PERMIT … disk ['EXTRA.py','a.py','b.py']`,
  `E1-F5a -> live ledger: allocating True unmeasured ['history']`, and
  `E1-F6 -> duplicate accepted: {'a.py':…001,'b.py':…002,'c.py':…002}`. A reconstruction
  that reproduces every recorded defect at the recorded value is the pre-image of the code
  those defects were recorded against.

Metrics in §1.2 are measured against those verified reconstructions.

### 1.4 Two deviations from the literal Phase 0.5 text

Both are recorded rather than absorbed, because Phase 0.5 is authoritative and a departure
from it needs to be visible.

**D-1 — E.1's read-count assertion was unimplementable as written.** Phase 0.5 §C.1
specified `test_the_preimage_is_read_exactly_once` asserting "≤ 2 opens (one pre-write, one
post-write), where today it is 3." R-2, specified in the same document, deliberately adds a
**third** read — the pre-write re-check — so the count returns to 3 and the assertion is
self-contradicting across the two units. The property R-1 establishes is that *verification
and the change measurement share one observation*, not that a particular number of opens
occurs. Implemented as `test_commit_reaches_the_preimage_through_exactly_one_reader`, an AST
assertion that `commit()` calls `read_preimage_bytes` exactly once and never calls
`load_preimage` — the same species as the existing
`test_the_measurement_has_exactly_one_implementation`, and stable under R-2. The behavioural
half is `test_the_parsed_and_raw_preimages_come_from_one_read`.

**D-2 — R-3 needed one addition Phase 0.5 did not anticipate.** §C.3 listed "cannot open the
directory → refuse" as an accepted failure mode. Executed, that turned out to break E1-S4:
a first mint into a tree that does not exist yet was refused where it previously succeeded,
because the lock is taken on a directory the writer had not created yet. Measured:

```
first mint into a non-existent directory -> REFUSED: cannot open /var/folders/… to take the ledger lock
```

`_ledger_lock` now calls `os.makedirs(directory, exist_ok=True)` before opening. Creating a
directory is not writing the ledger, and every writer already does it
(`ukb._dump_json` → `os.makedirs`), so this restores prior behaviour rather than adding new
behaviour. Pinned by `test_a_first_mint_into_a_nonexistent_tree_still_works`.

### 1.5 One documented design property was changed, as Phase 0.5 §B.7 flagged it would be

The module header used to read *"It does not write bytes either."* R-7 restores the
pre-image on divergence, so that sentence is no longer strictly true. The header now states
the exception and its justification: a restore re-establishes exactly the state that every
pre-write refusal leaves the file in, so a divergent writer and a refused permit produce the
same fail-closed outcome. `commit()` still never *invents* bytes. The alternative — detect
and refuse without restoring — was retained as the specified fallback and **not** chosen,
because it leaves a document on disk that no permit authorized, which fails Section A's
fail-closed requirement.

---

## 2. Per-unit evidence

Symbol line ranges are in the post-change `ledger_authority.py`.

### R-1 — E1-F7 · one read underwrites verification and measurement

**Change summary**
- Files: `00-BOOK/tools/ledger_authority.py`
- Functions: **new** `_read_bytes_or_none` (`:165-181`, 17 lines), **new**
  `read_preimage_bytes` (`:184-206`, 23 lines); `commit` body rewritten
- Lines: +40 new helpers; `commit`'s two reads (old `:567`, `:577-581`) collapsed to one

**Verification**
- *Reproduction before:* `"json.loads(raw_before)" in inspect.getsource(LA.commit)` → `False`;
  `open(path` occurrences in `commit` → `2`. `test_commit_reaches_the_preimage_through_exactly_one_reader`
  and `test_the_parsed_and_raw_preimages_come_from_one_read` both FAILED.
- *Reproduction after:* both PASS. `commit()` calls `read_preimage_bytes` exactly once and
  `load_preimage` never.
- *Regression:* `test_an_unreadable_ledger_is_refused_not_treated_as_empty` (E1-S2) and
  `test_a_missing_ledger_is_a_legitimate_first_mint` (E1-S4) green; refusal message text kept
  identical to `load_preimage`'s so the `match="cannot be read"` assertion still holds.

**Authority analysis.** The added predicate is the identity of two views of one buffer. No
new authority: `load_preimage` retains its signature and both behaviours for `plan()`. No
governance rule: nothing is classified, permitted or forbidden. No permit rule:
`_verify_permit` receives bit-identical inputs for every input.

**Compatibility.** No data shape read or written changes. One behaviour narrows in the
fail-closed direction: a raw read that raises `OSError` (not `FileNotFoundError`) now refuses
instead of yielding `None`. Previously unreachable — `load_preimage` already refused first on
the same condition.

---

### R-2 — E1-F1 · the verified state is the overwritten state

**Change summary**
- Files: `00-BOOK/tools/ledger_authority.py`
- Functions: `commit` (`:841-933`)
- Lines: +8 (a re-read, a comparison, a refusal)

**Verification**
- *Reproduction before:* `test_a_concurrent_write_inside_the_verification_window_is_refused`
  FAILED — no exception raised, and `z.py` (a permanent identifier already on disk) absent
  afterwards. Matches `PHASE0-E1-ATOMICITY-REPORT.md` §2 exactly.
- *Reproduction after:* PASSES. `LedgerWriteRefused: … the ledger changed between
  verification and write …`, **and** `z.py` still on disk — both legs asserted, because a
  refusal that still clobbered the file would be no fix.
- *Regression:* `test_a_single_writer_is_unaffected_by_the_recheck` PASSES — the re-read does
  not refuse when nothing else touched the file. Both production `--plan` paths and the whole
  77-test suite green.

**Authority analysis.** Refusal predicate: `bytes(t₁) ≠ bytes(t₀)`. Monotonically
restrictive — every write accepted after R-2 was accepted before it. `_verify_permit` still
runs first and is unchanged. `PHASE0-E1-ATOMICITY-REPORT.md` §6 states the independence
directly: *"re-reading and comparing bytes before writing decides nothing about authority."*

**Compatibility.** No migration. Stated limit: the window is narrowed, not eliminated — the
interval between the re-read and `writer`'s own `open` remains, and R-3 is what empties it
for cooperating processes.

---

### R-3 — E1-F2 · exclusive exclusion across the whole chokepoint

**Change summary**
- Files: `00-BOOK/tools/ledger_authority.py`
- Functions: **new** `_ledger_lock` (`:216-268`, 53 lines), **new** constant
  `LEDGER_LOCK_TIMEOUT_SECONDS` (`:212`); `commit` body indented into the `with`
- Imports: `contextlib`, `time`, guarded `fcntl`
- Lines: +66

**Verification**
- *Reproduction before:* `test_two_commits_cannot_interleave` FAILED (interleaved order);
  `test_a_lock_timeout_refuses_rather_than_proceeding` FAILED (`AttributeError`).
- *Reproduction after:* both PASS. Two subprocesses serialize —
  `['A-enter','A-exit','B-enter','B-exit']` or its mirror. Contention refuses with
  `LedgerWriteRefused … holds the ledger lock … refusing rather than writing unserialized`
  and the file byte-unchanged.
- *Regression:* `test_a_first_mint_into_a_nonexistent_tree_still_works` PASSES (see D-2).

**Authority analysis.** Exclusion changes *when* a caller runs, never *whether* it is
authorized; both callers still present a permit to the unmodified `_verify_permit`. **No new
file is created**: the lock is taken on the existing directory descriptor, so there is no new
tracked object requiring an identity, no `.gitignore` rule, and no entry in
`00-BOOK/DATA/exclusion-register.json` — the three places a lock file would have created
downstream governance surface.

**Compatibility.** `register.sh:187-197`'s advisory lock is untouched; the two are independent
and non-conflicting. `flock` on a directory descriptor does not impede processes that do not
call `flock`, so `_dump_json`'s many other writes into `00-BOOK/DATA` are unaffected.
**Two stated residuals:** the lock is advisory (a non-cooperating writer is caught by R-2, not
excluded), and on a platform without `fcntl` every `commit()` refuses. The second is a
behaviour change on non-POSIX platforms, chosen because a chokepoint that cannot exclude has
not established its property and proceeding anyway is the silent direction.

---

### R-4 — E1-F4 · a permanent identity's record is append-only in full

**Change summary**
- Files: `00-BOOK/tools/ledger_authority.py`
- Functions: **new** `_record_index` (`:151-162`, 12 lines); `assert_append_only`
  (`:271-383`) gains one refusal branch and a docstring update
- Lines: +12 helper, +21 in `assert_append_only`

**Verification**
- *Reproduction before:* `test_a_record_body_rewrite_is_refused` FAILED. Recorded outcome:
  `allocating=False authorization=NO_ALLOCATION`, disk holding
  `{'universal_id':'UCOS-OBJ-000001','object_class':'GOVERNANCE_OBJECT','first_seen':'c:FORGED'}`.
- *Reproduction after:* PASSES. `LedgerWriteRefused: by_object: record body of 'a.py' would be
  REWRITTEN (field(s) ['first_seen','object_class'])`, file byte-unchanged.
- *Against the live ledger:* `by_object: record body of '.github/workflows/acee-gate.yml'
  would be REWRITTEN` — the refusal fires on the real 5374-record shape.
- *Regression:* `test_a_new_records_body_is_unconstrained` PASSES — only **existing** records
  are frozen; a fresh allocation may carry any body.

**Authority analysis.** `assert_append_only`'s own docstring already names the property
(*"a way a permanent identifier could stop being permanent"*), and the module header states
*"append-only, no identity reissue"*. The fix widens an existing refusal to the rest of the
record it already refuses to reissue. `manifest_digest` was deliberately **not** widened, so
every digest is byte-stable and no permit binding changes.

**Compatibility.** No migration, measured: `assert_append_only(live, live)` passes, all four
allocators return existing entries untouched (`ukb.allocate:892-894`,
`ukb.allocate_execution:2249-2251`, `uga_engine.epoch1_identity:284-299`, the observation
minter at `:500-504`), and every live record shape is homogeneous. **Stated consequence:** a
future intentional schema change to an existing record would be refused, which is correct
under the module's append-only claim and is a known future cost, not a surprise.

---

### R-5 — E1-F5 · `history` classified, and its declared append-only property enforced

**Change summary**
- Files: `00-BOOK/tools/ledger_authority.py`
- Symbols: `NON_ALLOCATION_KEYS` (`:103-116`) gains `"history"` plus the comment recording
  why that set and not the other; `assert_append_only` gains the prefix refusal
- Lines: +10 (R-5a) / +25 (R-5b)

**Verification**
- *Reproduction before:* four tests FAILED. `LA.plan` on a deep copy of the live ledger:
  `allocating=True total=0 unmeasured=['history']` — so `NO_ALLOCATION` was unconditionally
  refused against the real ledger and `ukb.py:2380-2384` was dead code. History erasure was
  ACCEPTED, disk `history == {}`.
- *Reproduction after:* all four PASS. Live ledger, byte-identical proposal:
  `allocating=False`, `unmeasured_maps=[]`, `total_allocations=0`. Erasure and truncation
  refuse: `history: 'UCOS-BOOK-000000' would be REMOVED (1 recorded snapshot(s))`,
  `history: … is not an extension of the recorded 1 snapshot(s)`.
- *E1-F5(a) closed end-to-end:* `_verify_permit(NO_ALLOCATION, …)` on a byte-identical
  proposal against the live ledger → **ACCEPTED**. The idempotent exec-declare branch is no
  longer dead.
- *Regression:* `test_a_history_append_is_accepted_under_a_permit` PASSES — the real
  `ukb build --mint` shape (history grows, nothing else moves) still authorizes under a
  permit. `test_history_is_classified_exactly_once` pins the classification.

**Authority analysis.** The choice between the two existing sets was **forced by the data,
not decided**: `IDENTITY_MAPS` maps a key to *the field name holding a permanent identifier*,
and `history` is `{uid: [snapshot, …]}` — 1628 lists, no records, no identifier field. It is
not expressible in that vocabulary, so `NON_ALLOCATION_KEYS` is the only admissible
classification. R-5b refuses exactly the transitions `record_snapshots`' own docstring
(`ukb.py:315-320`, *"Preserves every prior content_hash and version"*) already declares
impossible; it classifies no write as governed and requires no audit event.

**The one permission expansion in this phase, bounded and measured.** R-5a is the only
change that moves a write from REFUSED to ACCEPTED. The newly-accepted set is
`{history-only change} ∪ {byte-identical no-op}`; **R-9, landed first, removes the first
disjunct**, leaving exactly `{ledger == before}` — a write that changes nothing. Verified by
execution: a `history`-only append still requires a permit both before and after, so nothing
that needed authorization stopped needing it.

**Compatibility.** No data migration. **One consequence of record: R-5a changes
`manifest_digest` for every manifest**, because `unmeasured_maps` moves from `['history']` to
`[]`. This invalidates nothing today — `00-BOOK/DATA/allocation-permits.json` does not exist
and zero permits have ever been issued — and it is why Phase 0.5 §D.3 required R-5a to
precede any E-4A remediation. Visible in production output: `ukb build --mint --plan` no
longer prints `UNMEASURED_MAPS=['history']`.

---

### R-6 — E1-F6 · a permanent identifier names at most one thing

**Change summary**
- Files: `00-BOOK/tools/ledger_authority.py`
- Functions: `assert_append_only` gains the cross-map uniqueness block
- Lines: +25

**Verification**
- *Reproduction before:* the collision was **ACCEPTED** and landed on disk —
  `{'a.py':'UCOS-OBJ-000001','b.py':'UCOS-OBJ-000002','c.py':'UCOS-OBJ-000002'}` with
  `allocated={'by_object':['UCOS-OBJ-000002']}`. This enabler was **not named in the Phase-0
  reports**; it was derived in Phase 0.5 §F.2 and is confirmed here by execution.
- *Reproduction after:* `test_a_duplicate_identifier_is_refused` PASSES for both
  parametrisations (within `by_object`, and across `by_object`/`by_observation`).
  `test_the_mw3_interleaving_is_refused_by_two_independent_legs` PASSES: leg 1 (key removal)
  fires on the realistic interleaving, leg 2 (`bound to BOTH`) fires on the key-preserving
  one that previously passed.
- *Against the live ledger:* `identifier 'UCOS-CONFIG-000001' would be bound to BOTH
  by_object[…] and …` — the refusal fires on the real shape.
- *Regression:* `test_the_live_ledger_has_no_duplicate_identifiers` PASSES — 7009 identifiers
  scanned across all four maps, zero duplicates within any map and zero across the union.

**Authority analysis.** `assert_append_only` already refuses reissue in the
key→identifier direction (`:305-310`); this is the same property in the identifier→key
direction. Spans all four maps because all four draw from the one shared `category_seq`.
Monotonically restrictive; measurement and digest unchanged.

**Compatibility.** No migration — the live ledger already satisfies the refusal, measured.
**Stated limit:** this does not eliminate MW-3, whose read precedes `commit()` and therefore
precedes the lock. It removes MW-3's dependence on a single refusal leg, which is what
E1-F6's UNVERIFIABLE classification asked for.

---

### R-7 — E2-F1, E2-F2 · the persisted document must be the authorized document

**Change summary**
- Files: `00-BOOK/tools/ledger_authority.py`
- Functions: **new** `_restore` (`:807-822`, 16 lines); `commit` gains the absent-file,
  unparseable and inequality refusals
- Lines: +16 helper, +34 in `commit`

**Verification**
- *Reproduction before:* five tests FAILED. E2-F1: `authorization=PERMIT`,
  `allocated={'by_object':['UCOS-OBJ-000002']}`, no error, disk holding
  `['EXTRA.py','a.py','b.py']` with `b.py → UCOS-OBJ-999999` — three permanent identifiers,
  one authorized. E2-F2: `allocating=True total=1 bytes_changed=False`, disk `['a.py']`.
- *Reproduction after:* all five PASS.
  `LedgerWriteRefused: … the persisted document is not the authorized document …`,
  `… the writer persisted nothing …`, `… persisted unparseable content …`, and in every case
  `Path(path).read_bytes() == original` — the pre-image restored byte-for-byte.
- *Regression:* `test_both_production_writers_satisfy_the_post_write_check` PASSES against
  the **real** serializers, `ukb._dump_json` and `uga_engine._dump`.
  `test_a_first_mint_that_the_writer_drops_leaves_no_file` PASSES — an absent pre-image
  restores to absent, never to a phantom `{}` that would report every future identity as
  freshly minted.

**Authority analysis.** The comparison is between two objects already inside `commit()`'s
scope; no third party is consulted. `_verify_permit` still decides authorization, unchanged,
and still runs before the write. Monotonically restrictive.

**Compatibility.** Compared as a **document**, not as bytes — required, because
`LA._canonical` differs from the production writers at byte level (1 786 167 vs 2 274 511
bytes on the live ledger) while all three round-trip to an equal document. A byte comparison
would have refused correct writes. **Stated limits:** detection is post-hoc — divergent bytes
reach disk before the check runs, and a crash between `writer` and `_restore` would leave them
there; that window is two file operations under a held lock and cannot be closed without
moving serialization inside the authority, which is a larger change than this phase covers.

---

### R-8 — E2-F3 · `bytes_changed` enforced and, for the first time, shown

**Change summary**
- Files: `00-BOOK/tools/ledger_authority.py`
- Functions: `format_report` (`:437-473`) restructured; **new** `_moved_suffix` (`:476-481`);
  **new** `_refuse_unmoved_allocation` (`:825-838`), called from `commit`
- Lines: +21 in `format_report` / `_moved_suffix`, +14 helper, +5 in `commit`

**Verification**
- *Reproduction before:* `format_report` output contained no `bytes_changed` token, and the
  contradiction `allocating=True ∧ bytes_changed=False` was returned without error.
- *Reproduction after:* `test_the_operator_line_shows_whether_the_file_moved` PASSES for both
  branches. `test_an_allocation_that_did_not_move_the_file_is_refused` PASSES against
  `_refuse_unmoved_allocation` directly — called at unit level because after R-7 the state is
  **unreachable through `commit()`** (Phase 0.5 §D.5: equal bytes plus an equal document imply
  an equal pre-image, hence nothing allocated). A test routed through `commit()` would have
  asserted against R-7's refusal and proved nothing about this check.
- *Regression, end-to-end:* both production `format_report(plan_output)` call sites execute
  without `KeyError`:
  ```
  ukb build --mint --plan   -> identity ledger ALLOCATED 9 permanent identifier(s) [by_path+9] … page_cursor:12507->12612
  uga_engine run --plan     -> identity ledger ALLOCATED 27 permanent identifier(s) [by_object+27] …
  ```
  Neither renders a `bytes_changed` token, because a plan has performed no write. This is
  Phase 0.5's CF-1, and it is **wider than CF-1 recorded**: there are two `plan()` render
  sites (`ukb.py:1293` and `uga_engine.py:1982`), plus `_verify_permit`'s refusal message —
  three places a bare subscript would have broken. `test_plan_output_still_renders_without_a_bytes_changed_field`
  pins it. The three existing line-substring assertions
  (`test_ledger_authority.py:207,219,256`) remain green.

**Authority analysis.** One relates two fields of one report; the other renders a field
already computed. Neither decides anything.

**Compatibility.** Nothing parses the operator line — grep confirms the only consumers are
five `print()` calls and three substring assertions. `uga_engine.py:2004`'s
`if report["bytes_changed"]` reads the same value.

---

### R-9 — E2-F4 · `NO_ALLOCATION` permits nothing, not merely no allocation

**Change summary**
- Files: `00-BOOK/tools/ledger_authority.py`
- Functions: `_verify_permit` (`:664-804`) — **the sentinel branch only**; signature gains
  keyword-only `before` / `after`; `commit` supplies them
- Lines: +9 signature/docstring, +16 in the sentinel branch, +1 at the call site

**Verification**
- *Reproduction before:* ACCEPTED with `allocating=False authorization=NO_ALLOCATION
  bytes_changed=True`; disk holding `version=99` and `discovered_volumes={'VOL-666':1}`.
- *Reproduction after:* both parametrisations PASS —
  `PermitRefused: … this write MUTATES the ledger: top-level key(s) ['version'] differ from
  the pre-image …`, file unchanged.
- *Against the live ledger:* a `version` bump measures `allocating=False` and is REFUSED with
  the same message. The defect is closed on the real shape, not only on a fixture.
- *Regression:* `test_an_idempotent_no_op_is_still_accepted_under_no_allocation` PASSES — the
  one real production case (`ukb.py:2380-2384`). Existing
  `test_a_false_no_allocation_claim_is_refused` green: R-9 adds a second refusal to that
  branch without removing the first.

**Authority analysis.** `NO_ALLOCATION` is **not a permit**. It is issued by nobody, appears
in no register, names no actor and has no expiry: it is a caller assertion about
`(before, ledger)`, verified against `(before, ledger)`. Narrowing when that assertion is
believed grants no permission to anyone. The property implemented is quoted verbatim from the
sentinel's own docstring (`:509-529`): *"strictly safer than passing a permit — it can only
ever permit less."* **The permit path of `_verify_permit` is byte-for-byte unchanged**;
`before`/`after` are not consulted on it.

**Compatibility.** `_verify_permit` has exactly one caller, so the signature change is
contained. No migration.

---

### R-10 — E2-F5 · `LEDGER-INV-01` sees a write reached through a path parameter

**Change summary**
- Files: `00-MASTER/UCOS-UGA-001/uga_engine.py`
- Symbols: **new** `_LEDGER_REF_RE`, `_PARAM_WRITE_SINKS`, `_param_writing_functions`,
  `indirect_ledger_writes`; `_direct_ledger_writes` calls the new measurement;
  `LEDGER-INV-01`'s `why` text corrected
- Lines: +101 / −2

**Verification**
- *Reproduction before:* `test_the_guard_catches_an_indirect_ledger_write` FAILED
  (`AttributeError` — no measurement existed). Live compiled patterns confirmed blind:
  `uga _write_text body False | ukb _dump_json body False | uga call site False | ukb call
  site False | naive direct write True`.
- *Reproduction after:* PASSES. A synthetic `helper(LEDGER_PATH, "{}")` whose callee writes
  its parameter is caught, and the test **also asserts the lexical patterns miss it**, so the
  new leg is proven to be doing work the old one could not.
  `test_the_indirection_guard_is_wired_into_the_invariant` (AST) proves the measurement is
  *reached*, not merely defined — a measurement that exists and is never called would pass a
  naive check.
- *Regression:* `test_the_guard_reports_no_indirect_write_in_current_source` PASSES — zero
  indirect writes across all tracked `.py` files. Existing
  `test_the_guard_does_not_confuse_the_change_ledger_for_the_identity_ledger` green:
  broadening the measurement did not start matching `CHANGE_LEDGER_PATH`.

**Authority analysis.** A syntactic measurement with no allow-list, no exemption list and no
owner. `LEDGER-INV-01` keeps its identifier, name, `fails_closed: true` status and
`UCOS-UGA-001` ownership; its coverage widens, its authority does not move. The `why`-text
correction is not a weakening: it stops the declaration implying it constrains what a
`writer` does after the chokepoint hands it the path, because R-7 now constrains that at
runtime and the text says so.

**Compatibility — the decisive measurement.** The full invariant table was computed before
and after, against the verified pre-Phase-1 engine:

| | invariants | passing | `LEDGER-INV-01` | `UGA-INV-01` | `UGA-INV-10` |
|---|---|---|---|---|---|
| before | 30 | 28 | PASS, measured 2208, 0 violations | FAIL, 25 | FAIL, 25 |
| after | 30 | 28 | PASS, measured 2208, 0 violations | FAIL, 25 | FAIL, 25 |

`invariants whose result/measured/violations changed: NONE`. The widened measurement produces
zero new violations on the real repository. **Stated limits:** the measurement is one call
deep — a two-hop indirection is not caught — and a `SyntaxError` is reported as a violation
rather than skipped, matching `_direct_ledger_writes`' existing treatment of unreadable
source.

---

### R-11 — E2-F6 · serializer round-trip equivalence

**Change summary**
- Files: `platform/tests/test_ledger_authority.py` only. **No production code.**
- Lines: +60 (fixture + parametrised test)

**Verification**
- *Reproduction before:* no such test existed; the relation was unmeasured, which is exactly
  E2-F6's UNPROVEN classification.
- *Reproduction after:* PASSES for three documents — `{}`, a synthetic fixture carrying all
  four identity maps plus `history` and a non-ASCII name, and the live
  `00-BOOK/DATA/id-ledger.json` (read-only). Measured on the live ledger: `ukb._dump_json`
  and `uga_engine._dump` are **byte-identical** (both 2 274 511 bytes), `LA._canonical`
  differs (1 786 167), and all three parse back to a document equal to the original. The test
  asserts the `_canonical` byte inequality too, so the reason R-7 compares documents rather
  than bytes is pinned rather than remembered.

**Authority analysis.** A test grants nothing.

**Compatibility.** Test-only. **This test is R-7's premise**: if any writer's `json.dumps`
keyword arguments ever change so that round-tripping breaks, R-7 begins refusing production
writes, and this is the test that says why.

---

## 3. Test evidence

### 3.1 The ledger authority suite

```
BEFORE Phase 1 : 40 passed
AFTER  Phase 1 : 77 passed in 6.68s
```

Command, verified:

```bash
cd /Users/bipin/Desktop/UCOS-CONSOLIDATION
PYTHONPATH=. .ec1-venv/bin/pytest platform/tests/test_ledger_authority.py \
    -q -p no:cacheprovider --no-cov
```

**No existing test was removed or weakened.** All 40 originals are present and green; 37 were
added.

### 3.2 Regression batch

```
platform/tests/test_ledger_authority.py            test_mutation_governance_boundary.py
platform/tests/test_verification_purity.py         test_mutation_classification.py
platform/tests/test_observation_universe.py        test_durable_identity.py
platform/tests/test_dag_ledger.py                  test_certification_ledger.py
platform/tests/test_runtime_operations_ledger.py   test_identity.py
platform/tests/test_universal_truth.py

-> 331 passed, 1 failed in 115.71s
```

### 3.3 The one failure, proven pre-existing

`test_observation_universe.py::test_the_governance_gate_enforces_every_invariant` fails
because `UGA-INV-01` and `UGA-INV-10` each report 25 violations — anonymous objects in the
working tree, the state `PHASE0-E3-CLAIM-INTEGRITY-REPORT.md` documented (27 at the time of
that report; 25 now, as the tree has moved).

Not asserted — **measured**. The identical test was run against the unmodified engine by
temporarily swapping the file, with SHA-256 verification of restoration:

```
--- running the test against the UNMODIFIED engine (pre-Phase-1) ---
FAILED platform/tests/test_observation_universe.py::test_the_governance_gate_enforces_every_invariant
1 failed in 5.53s
restored correctly: YES
```

It fails identically without any Phase-1 change. Closing it requires E-3, explicitly out of
scope.

### 3.4 Lint

```
$ ruff check 00-BOOK/tools/ledger_authority.py platform/tests/test_ledger_authority.py
All checks passed!

$ ruff check 00-MASTER/UCOS-UGA-001/uga_engine.py
uga_engine.py:655:32: B023 …   uga_engine.py:657:25: B023 …   uga_engine.py:1979:101: E501 …
Found 3 errors.
```

All three are pre-existing and present in the reconstructed pre-Phase-1 baseline. Three
violations introduced during implementation (`UP038`, `F401`, `E501`) were found and fixed
before completion.

---

## 4. Dependency-order evidence

Phase 0.5 §D.2 specifies a three-wave DAG with five edges. Implementation followed it, and
the failure count after each wave is the evidence that the ordering was real rather than
nominal.

| Stage | Units landed | Suite result |
|---|---|---|
| Tests added, no implementation | — | **27 failed, 49 passed** |
| **Wave 0** | R-1, R-3, R-4, R-6, R-9, R-10ₐ, R-11 | **13 failed, 63 passed** |
| **Wave 1** | R-2, R-5, R-7 | **1 failed, 75 passed** |
| **Wave 2** | R-8, R-10ₜ | **0 failed, 76 passed** |
| R-3 regression fix (D-2) | `_ledger_lock` makedirs + its test | **0 failed, 77 passed** |

The 13 failures remaining after Wave 0 were exactly the Wave 1/2 units — 1 for R-2, 5 for
R-5, 5 for R-7, 2 for R-8 — with no Wave 0 unit's test among them.

### 4.1 Each specified edge, discharged

| Edge | Honoured how |
|---|---|
| `R-1 → R-2` | `read_preimage_bytes` landed in Wave 0; R-2's comparison in Wave 1 is against the `raw_before` that verification itself used, so it closes MW-1 rather than only MW-2. |
| `R-9 → R-5a` | R-9 landed in Wave 0. When R-5a landed in Wave 1, the set it widened was already bounded to `{ledger == before}`. **At no point was a `history`-only mutation acceptable without a permit.** |
| `R-5a ↔ R-5b` | Both applied in one edit sequence with no test run between them; `history` was never classified while its prefix was unenforced. |
| `R-11 → R-7` | R-11's round-trip test was green in Wave 0, establishing that the two production writers are byte-identical and all three serializers round-trip — before R-7 relied on document comparison in Wave 1. |
| `R-3 → R-7ᵣ` | The lock landed in Wave 0, so `_restore` has never executed outside exclusion. |
| `R-7 → R-8ₑ`, `R-7 → R-10ₜ` | Both deferred to Wave 2. `_refuse_unmoved_allocation`'s unreachability-through-`commit()` was confirmed empirically, which is why its test is unit-level. `LEDGER-INV-01`'s corrected text asserts the runtime check, which existed by then. |

### 4.2 Outbound constraint, still satisfied

Phase 0.5 §D.3 records that **R-5a must precede any E-4A remediation**, because it changes
every `manifest_digest`. It landed with the permit register still absent and zero permits ever
issued, so no permit was invalidated. The constraint remains binding on any future phase.

### 4.3 Invariant-table comparison

See R-10 above: 30 invariants, 28 passing, `NONE` changed.

---

## 5. Backward-compatibility evidence

### 5.1 The live ledger

```
$ git status --porcelain 00-BOOK/DATA/
(0 lines)
$ shasum -a 256 00-BOOK/DATA/id-ledger.json
8471e709b178a9a09909bca55f2e8eccb78161db8423026d1d26e4f35c41c20b
```

Byte-identical before and after. No file under `00-BOOK/DATA/` was created, modified or
removed. `commit()` was **never** called against the production ledger; every live-ledger
measurement used `plan()`, `load_preimage`, `assert_append_only` and `_verify_permit`, all of
which write nothing.

### 5.2 No persisted data requires migration

Each new refusal was executed against the live ledger and against a self-copy of it:

| Check | Result |
|---|---|
| `assert_append_only(live, live)` | **PASSES** — no refusal |
| `plan(live, copy(live))` | `allocating=False`, `unmeasured_maps=[]`, `total_allocations=0` |
| R-4 — record-body immutability | satisfied by all 7009 live records; refusal fires only on an injected rewrite |
| R-5b — `history` prefix | satisfied by all 1628 live snapshot lists |
| R-6 — identifier uniqueness | satisfied: zero duplicates within any map, zero across the union of all four |
| R-11 — serializer round-trip | the live ledger round-trips through all three serializers |

The ledger already satisfied every property added. **Zero migration.**

### 5.3 The production call sites still work

Both read-only preview paths were executed end-to-end against the real repository, and the
working tree was verified unchanged afterwards:

```
$ python3 00-BOOK/tools/ukb.py build --mint --plan
identity ledger ALLOCATED 9 permanent identifier(s) [by_path+9] actor=UMB-IMP-001 :: ukb.py build --mint
  category_seq(COVERA:0->1, ENFORC:0->2, …, UCOSUC:1->2) page_cursor:12507->12612
  manifest_digest : a6827d8a…3fae5     preimage_digest : 3a2a2532…2bcf4
  head            : 77798202d2df43285760b3277f230ebde4b52bbc
PLAN ONLY — nothing written, no identity allocated.
working tree unchanged: YES

$ python3 00-MASTER/UCOS-UGA-001/uga_engine.py run --plan
identity ledger ALLOCATED 27 permanent identifier(s) [by_object+27] actor=UCOS-UGA-001 :: uga_engine.py run
  category_seq(CONFIG:36->37, DATAOBJ:136->139, ENGINE:1330->1342, …)
PLAN ONLY — nothing written, no identity allocated.
working tree unchanged: YES
```

### 5.4 Unchanged surfaces

`register.sh` (including its own advisory lock), `ukb.py`, `uga-declaration.json`,
`mutation-governance-boundary.json`, `exclusion-register.json`, `.gitignore` — **none
modified**. R-3 introduced no file, so no ignore rule and no exclusion-register entry was
required.

---

## 6. Remaining blocker inventory

### 6.1 Closed

```
CLOSED BY PHASE 1 .................................. 12
    E1-F1  TOCTOU verification -> write            (R-2)
    E1-F2  no concurrency control                  (R-3)
    E1-F4  record bodies unchecked                 (R-4)
    E1-F5  history unclassified + erasure unrefused(R-5)
    E1-F6  minting arithmetic vs verification read  (R-6)
    E1-F7  raw_before unreconciled                  (R-1)
    E2-F1  divergent writer                         (R-7)
    E2-F2  silent writer                            (R-7)
    E2-F3  bytes_changed unenforced and unrendered  (R-8)
    E2-F4  NO_ALLOCATION permits mutation           (R-9)
    E2-F5  LEDGER-INV-01 lexically blind            (R-10)
    E2-F6  serializer equivalence unproven          (R-11)
```

Each has a reproduction test that failed before its unit and passes after, plus a regression
test that was green throughout.

### 6.2 Remaining — exactly the expected set

```
REMAINING BLOCKERS ................................... 5
    E1-F3   permit replay after ledger restore        GOVERNANCE-DEPENDENT
    E-3     UGA-INV-10 tautology                      GOVERNANCE-DEPENDENT
    E-4A    no permit issuance path                   GOVERNANCE-DEPENDENT
    RES-1   permit binds a projection, not the doc    GOVERNANCE-DEPENDENT
    RES-2   empty-manifest permits not refused        GOVERNANCE-DEPENDENT

ADDITIONAL BLOCKERS DISCOVERED ....................... 0
```

Each verified still open, and still untouched, by execution:

| Blocker | Executable evidence it is unchanged |
|---|---|
| **E1-F3** | The string `single_use` does not occur in `ledger_authority.py`. No unit records, marks or consumes permit use. `preimage_digest` remains derived from mutable state (`:565-575`, unmodified). |
| **E-3** | No unit emits an audit event. `UGA-INV-10` measured 25 violations before and after, with an identical violation set; `audited ≡ set(by_object.keys())` is untouched. E-3 counterexample C6 — *every `commit()` call passes `UGA-INV-10` unaudited* — holds verbatim. |
| **E-4A** | `00-BOOK/DATA/allocation-permits.json` still does not exist. Against a real allocating manifest measured from the live ledger: `permit=None → REFUSED (permit must be a permit_id string or NO_ALLOCATION)`; `permit='P-ANY' → REFUSED (not in …/allocation-permits.json)`; `permit=NO_ALLOCATION → REFUSED (this write ALLOCATES)`. `register.sh:216` still passes no `--permit`, so Phase 1 of REG-AUTO-001 still cannot complete. |
| **RES-1** | `manifest_digest` (`:543-564`) is unmodified: still six fields over `_identifier_index`. A new record's body, `history` content, and `version` / `discovered_volumes` values remain outside what a permit binds. |
| **RES-2** | `_verify_permit`'s permit path contains no test of `total_allocations` or `allocating`. Phase 1 **relies** on this: it is what keeps a `history`-only append authorizable after R-5a + R-9. |

### 6.3 One clarification, not a new blocker

`E-4A still blocks every production write.` The twelve fixes made the write path safe; they
did not open it, and were not intended to. The one thing that changed in the accept direction
is that a **byte-identical no-op** under `NO_ALLOCATION` is now accepted against the live
ledger where it was previously refused for `UNMEASURED_MAPS=['history']`. That is E1-F5(a)'s
closure, it writes nothing by construction (the proposed document *is* the pre-image), and it
revives `ukb.py:2380-2384` from dead code. It is not a production write path: every
allocating write still requires a permit from a register that does not exist.

---

## 7. Governance discipline

| Requirement | Status |
|---|---|
| FD-1 / FD-2 / FD-3′ / FD-4 / FD-5 | **Not answered, not assumed, not inferred, not approached.** |
| No new authority | **MET.** `_verify_permit`'s permit path is byte-for-byte unchanged; only the `NO_ALLOCATION` sentinel branch — a caller claim, issued by nobody, present in no register — was narrowed. No new caller, role, issuer, signer or decision procedure. |
| No governance rule | **MET.** No unit classifies writes as governed or ungoverned. Every refusal is a function of `(pre-image, proposed document, persisted bytes)`. |
| No permit rule | **MET.** No unit creates, appends to, updates or persists the permit register. `load_permit_register`'s single `open` (`:616`) remains the only register access. No expiry, scope, revocation or single-use semantics added. |
| No mutation-definition redesign | **MET.** R-4, R-5b and R-6 refuse state transitions that existing producer docstrings already declare impossible (`ukb.py:315-320`; `ledger_authority.py`'s own append-only docstring and module header). |
| No audit-event redesign | **MET.** No unit emits, reads, requires or names an audit event. |
| E1-F3, E-3, E-4A, RES-1, RES-2 | **Not modified, not resolved.** §6.2 gives executable evidence for each. |
| Existing fail-closed behavior preserved | **MET.** E1-S1…S8 all still hold; E1-S4 needed an explicit fix to survive R-3 (§1.4 D-2) and is now pinned by a test. Every added behaviour refuses rather than permits, except R-5a, bounded by R-9 and measured. |
| No test removed or weakened | **MET.** All 40 original tests present and green; 37 added. |

---

## 8. Stop condition

Phase 1 ends here.

- Twelve governance-independent defects: **closed**, each with a reproduction that failed
  before and passes after.
- `E-4A`: **still blocking**, verified against the live ledger.
- Live ledger: **byte-identical**.
- Remaining blockers: **exactly the five expected** — E1-F3, E-3, E-4A, RES-1, RES-2. None
  additional.
- Governance questions answered: **none**.

The next act would be governance-dependent by construction, and nothing in this phase
prejudges it.
