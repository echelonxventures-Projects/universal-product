# PHASE 0.5 — GOVERNANCE-INDEPENDENT REMEDIATION SPECIFICATION

| Field | Value |
|---|---|
| Phase | 0.5 — Governance-Independent Remediation Authorization |
| Input | `PHASE0-E1-ATOMICITY-REPORT.md`, `PHASE0-E2-CORRESPONDENCE-REPORT.md`, `PHASE0-E3-CLAIM-INTEGRITY-REPORT.md`, `PHASE0-E4A-ISSUANCE-PATH-REPORT.md`, `PHASE0-GOVERNANCE-INDEPENDENT-DETERMINATION.md` |
| Scope | The 12 blockers classified GOVERNANCE-INDEPENDENT in `PHASE0-GOVERNANCE-INDEPENDENT-DETERMINATION.md` §6.2 |
| Deliverable | Remediation plan + implementation specification. **No code was changed by this phase.** |
| Repository | working tree at `77798202`; `00-BOOK/tools/ledger_authority.py` still `AM`; `ukb.py`, `uga_engine.py`, `register.sh` still ` M` — identical to the state Phase 0 measured |
| Governance content | **NONE.** FD-1, FD-2, FD-3′, FD-4, FD-5 are not answered, assumed, inferred, redesigned or approached. No authority, permit rule, ratification rule, temporal legitimacy rule, mutation definition or audit-event definition is introduced. |
| Out of scope | E1-F3, E-3, E-4A — referenced only where their existence constrains implementation |
| Verification status of this document | Every defect re-confirmed live by execution against the unmodified authority; every proposed mechanism prototyped outside the repository and shown to convert the reproduction from ACCEPTED to REFUSED. Probe transcripts summarised in §G. |

---

## 0. Reading order and naming

Twelve defects are remediated by **eleven change units**, `R-1` … `R-11`. The mapping is
one-to-one except that E2-F1 and E2-F2 are two symptoms of one missing comparison and are
closed by one unit (`R-7`). E1-F5 is one defect requiring two edits that must land
together (`R-5a` + `R-5b`); they are counted as one unit because either alone is unsafe.

| Unit | Defect | One-line change |
|---|---|---|
| R-1 | E1-F7 | Derive `before` and `raw_before` from ONE read |
| R-2 | E1-F1 | Re-read and compare the bytes immediately before `writer` |
| R-3 | E1-F2 | Hold an exclusive advisory lock across the whole of `commit()` |
| R-4 | E1-F4 | Refuse a rewrite of the record body of an existing identity |
| R-5 | E1-F5 | (a) classify `history` into `NON_ALLOCATION_KEYS`; (b) refuse non-prefix `history` change |
| R-6 | E1-F6 | Refuse a duplicate identifier within or across identity maps |
| R-7 | E2-F1, E2-F2 | Parse the persisted file and require it to equal the authorized document |
| R-8 | E2-F3 | Render `bytes_changed`; assert `allocating ⇒ bytes_changed` |
| R-9 | E2-F4 | `NO_ALLOCATION` requires the proposed document to equal the pre-image |
| R-10 | E2-F5 | Add an AST indirection measurement to `LEDGER-INV-01`; correct its `why` text |
| R-11 | E2-F6 | Serializer round-trip equivalence test |

Two facts govern every design below and are stated once:

1. **Every unit is monotonically restrictive except `R-5a`.** Ten of the eleven units only
   ever move a write from ACCEPTED to REFUSED. `R-5a` is the single unit that moves a write
   from REFUSED to ACCEPTED, and `R-9` bounds that movement back to exactly the
   byte-identical no-op. This is why `R-9` must land before `R-5a` (§D).
2. **`commit()`'s authorization step is untouched.** `_verify_permit`
   (`ledger_authority.py:432-543`) is not modified by any unit. No unit reads, writes,
   creates, or interprets the permit register beyond what `:376-399` already does.

---

# Section A — Defect Inventory

Line references are to the working-tree state at `77798202`. `LA` = `00-BOOK/tools/ledger_authority.py`.

For orientation, `commit()`'s eleven statements (`LA:567-593`):

```
567  before  = load_preimage(path)            # V1
568  assert_append_only(before, ledger)       # V2
569  report  = build_manifest(...)            # V3  (contains git_head subprocess, :349-368)
573  used    = _verify_permit(...)            # V4  (reads the permit register)
577  raw_before = open(path,'rb').read()      # W0  — SECOND independent read
583  writer(path, ledger)                     # W1  — unconstrained callable
585  raw_after  = open(path,'rb').read()      # W2
591  report['bytes_changed'] = raw_before != raw_after
593  return report
```

---

## A.1 — E1-F1 · TOCTOU inside `commit()`'s own verification window

| | |
|---|---|
| **Current behavior** | `assert_append_only` (V2) and the manifest (V3) are computed against `before`, read at V1. `writer` at W1 overwrites the file unconditionally. Nothing between V1 and W1 re-establishes that the file still holds `before`. The window spans a `subprocess.run(..., timeout=15)` fork (`LA:349-368`, reached from `LA:411`) and a second file open (V4 → `LA:382`). |
| **Violated property** | *The state that was verified is the state that is overwritten.* |
| **Minimal code locations** | `LA:567` (the only read verification uses), `LA:583` (the write), `LA:577-581` (the already-present second read that could have detected it) |
| **Dependency graph** | Enabled by E1-F7 (two unreconciled reads). Enabled by E1-F2 (no exclusion). Remedy consumes R-1. |
| **Activation conditions** | Two processes reaching `commit()` on the same ledger with overlapping V1→W1 spans. Requires no privilege and no unusual input; the 15 s subprocess timeout makes the window arbitrarily wide in practice. Latent today only because E-4A blocks every production write (E2-F7). |
| **Expected fail-closed behavior** | If the ledger's bytes differ at W1 from the bytes verification was computed against, refuse with `LedgerWriteRefused` naming the mutation, and do not call `writer`. |
| **Re-confirmed live** | Yes — E1 report §2 probe `E1-P1`; re-derived here as `[E1-F1] REFUSED (ledger changed between verification and write)` under the R-1+R-2 prototype, versus the report's recorded ACCEPTED under current code. |

## A.2 — E1-F2 · No concurrency control of any kind on the ledger

| | |
|---|---|
| **Current behavior** | `commit()` contains no mutual exclusion. Repository-wide search for `fcntl`, `flock`, `LOCK_EX`, `O_EXCL`, `threading.Lock`, `filelock`, `os.replace`, `os.rename`, `NamedTemporary`, `fsync` over `00-BOOK/tools/` and `00-MASTER/UCOS-UGA-001/` returns no ledger match; the only hits are `governance_telemetry.py:210,217` (`_atomic_write`, telemetry only). The one lock naming the ledger is `register.sh:187-197`, a non-atomic test-then-create that guards only `register.sh`; `uga_engine.py run` (`:1975`) and `ukb.py exec declare` (`:2343`) take no lock and are reachable independently. |
| **Violated property** | *Two writers cannot interleave inside the chokepoint.* |
| **Minimal code locations** | `LA:546-593` (no lock anywhere in the function); `register.sh:187-197` (the lock that exists and does not cover the chokepoint) |
| **Dependency graph** | Independent. Complementary to R-2: the lock makes MW-1/MW-2 empty for cooperating processes; R-2 catches a non-cooperating writer. |
| **Activation conditions** | Any concurrent invocation of the three entrypoints. `register.sh`'s lock removes only the `register.sh`↔`register.sh` pair. |
| **Expected fail-closed behavior** | `commit()` serializes: the V1→W2 span executes under an exclusive lock on the ledger's containing directory; a second process blocks rather than interleaving. Lock acquisition failure is a refusal, never a silent proceed. |
| **Re-confirmed live** | Yes — grep re-run; zero ledger matches. Directory-fd `flock` mutual exclusion verified on this platform (macOS/APFS): second process raised `BlockingIOError` under `LOCK_EX|LOCK_NB`. |

## A.3 — E1-F4 · Record bodies of permanent identities are outside every check

| | |
|---|---|
| **Current behavior** | `_identifier_index` (`LA:112-119`) projects each record to one field. `assert_append_only` (`LA:121-170`) and `allocation_report` (`LA:172-221`) consume only that projection, so every other field of an existing record — `object_class`, `category`, `first_seen`, `page_start`, `page_count` — can be rewritten with no refusal, `allocating=False`, `total_allocations=0`, and a `NO_ALLOCATION` claim accepted. |
| **Violated property** | *A record of a permanent identity is append-only in full, not only in its identifier field.* |
| **Minimal code locations** | `LA:112-119` (the projection), `LA:121-170` (the consumer that inherits its narrowness) |
| **Dependency graph** | Independent. Its `NO_ALLOCATION`-path reproduction is **masked by E1-F5** on any ledger carrying `history` (see A.4 and §D.4). Supplies the restore primitive E1-F3 (out of scope) requires. |
| **Activation conditions** | Any write that changes an existing record body while holding the identifier constant. Reachable through the `NO_ALLOCATION` path with no permit at all on a ledger without `history`; reachable through the permit path on any ledger. |
| **Expected fail-closed behavior** | Refuse with `LedgerWriteRefused` naming the map, the key and the changed fields. |
| **Re-confirmed live** | Yes — executed here against unmodified `LA.commit`: `allocating=False authorization=NO_ALLOCATION`, disk now holds `{'universal_id': 'UCOS-OBJ-000001', 'object_class': 'GOVERNANCE_OBJECT', 'first_seen': 'c:FORGED'}`. |

## A.4 — E1-F5 · `history` is in neither classification set

| | |
|---|---|
| **Current behavior** | The production ledger's top-level keys are `by_object, by_observation, by_path, category_seq, discovered_volumes, history, page_cursor, version, volume_seq` (measured; note `by_execution` is **absent on disk** and is materialised only by `ukb.load_ledger` (`ukb.py:868-874`) or `allocate_execution` (`ukb.py:2251`)). `history` is a dict of 1628 lists and appears in neither `IDENTITY_MAPS` (`LA:71-77`) nor `NON_ALLOCATION_KEYS` (`LA:83-85`), so `allocation_report`'s `unmeasured` term (`LA:207-211`) collects it and folds it into `allocating` (`LA:196-198`). Two consequences: **(a)** a byte-identical no-op measures `allocating=True, total_allocations=0, unmeasured_maps=['history']`, so `permit=NO_ALLOCATION` is unconditionally refused against the real ledger and the `ukb.py exec declare` idempotent branch (`ukb.py:2380-2384`) is dead code; **(b)** total erasure of `history` is not an append-only violation, despite `record_snapshots` (`ukb.py:314-330`) declaring the map APPEND-ONLY in its own docstring. |
| **Violated property** | (a) *A byte-identical write allocates nothing.* (b) *`history` is append-only, as its producer states.* |
| **Minimal code locations** | `LA:83-85` (the set that omits it), `LA:121-170` (the check that never sees it), `ukb.py:314-330` (the producer whose claim is unenforced) |
| **Dependency graph** | **Masks E1-F4's and E2-F4's `NO_ALLOCATION`-path reproductions on the production ledger** — both were reproduced in Phase 0 on `history`-free fixtures, and re-running E1-F4 with `history` present raises `PermitRefused: … UNMEASURED_MAPS=['history']` before the defect is reached. Remedy `R-5a` requires `R-9` (§D). `R-5a` changes every future `manifest_digest`, so it must precede any E-4A remediation. |
| **Activation conditions** | (a) Every invocation against the production ledger, unconditionally. (b) Any write proposing a shortened or missing `history` list. |
| **Expected fail-closed behavior** | (a) A byte-identical proposal measures `allocating=False, unmeasured_maps=[]`. (b) A proposal in which any existing `history[uid]` list is absent, shortened, or not prefixed by its recorded value is refused. |
| **Re-confirmed live** | Yes — `LA.plan` against `00-BOOK/DATA/id-ledger.json` with a deep copy of itself: `allocating=True total=0 unmeasured=['history']`. Erasure probe: `history` replaced by `{}`, accepted, disk now `{}`. |

## A.5 — E1-F6 · Minting arithmetic computed against a different read than verification

| | |
|---|---|
| **Current behavior** | `uga_engine.py:1700` reads the ledger (`ledger = _load(LEDGER_PATH)`); `epoch1_identity` (`uga_engine.py:271-321`) computes `n = seq.get(cat, 0) + 1` against that read (`:305`); `commit()` re-reads at `LA:567` after the whole discovery pass (MW-3, ~60 s on this repository). The observed refusal for a realistic interleaving comes from the key-removal check (`LA:135-139`), not from counter detection: `new_n < old_n` (`LA:157`) is false when both reads produce the same next value. |
| **Violated property** | *The arithmetic that produces an identifier is bound to the state that authorizes it.* |
| **Minimal code locations** | `uga_engine.py:1700` and `:305` (the read the arithmetic uses), `LA:567` (the read verification uses), `LA:121-170` (the check whose coverage is at issue) |
| **Dependency graph** | Independent. Not closable by `R-3`: the caller's read is **outside** `commit()`, so no lock held inside `commit()` can cover MW-3. Closed by compensation, not by elimination. |
| **Activation conditions** | A concurrent commit landing during another caller's discovery pass. |
| **Expected fail-closed behavior** | Two independent refusals must cover MW-3, so the property does not rest on one leg: (i) the existing key-removal refusal, and (ii) a **duplicate-identifier refusal** — the same permanent identifier bound to two different keys within a map, or reused across maps, must be refused. |
| **Re-confirmed live** | The gap is confirmed by execution here: a proposal binding `UCOS-OBJ-000002` to both `b.py` and `c.py` was **ACCEPTED** by unmodified `LA.commit` (`allocated={'by_object': ['UCOS-OBJ-000002']}`) and both bindings landed on disk. The live ledger has zero duplicates within any map and zero across all four maps (1628 + 5374 + 0 + 7 identifiers measured), so the refusal is backward-compatible. |

## A.6 — E1-F7 · `raw_before` is read but never reconciled with `before`

| | |
|---|---|
| **Current behavior** | `LA:577-581` opens and reads the ledger a second time. The value is used only at `LA:591` to compute `bytes_changed`. `json.loads(raw_before) == before` is available at zero additional I/O cost and is not performed. Confirmed by source inspection: `"json.loads(raw_before)" in inspect.getsource(LA.commit)` is `False`; `open(path` appears twice. |
| **Violated property** | *One observation of the file underwrites both verification and the change measurement.* |
| **Minimal code locations** | `LA:567`, `LA:577-581` |
| **Dependency graph** | Enabler for E1-F1. `R-1` is a strict prerequisite of `R-2`. |
| **Activation conditions** | Every invocation. The defect is structural, not conditional. |
| **Expected fail-closed behavior** | `before` and `raw_before` are two views of one read. An unreadable or unparseable file refuses exactly as `load_preimage` does today (`LA:100-110`). |
| **Re-confirmed live** | Yes — source inspection above. |

## A.7 — E2-F1 · Divergent writer: authorized object ≠ persisted object, undetected

| | |
|---|---|
| **Current behavior** | `writer` is an unconstrained caller-supplied callable invoked once at `LA:583`. `commit()` never parses the persisted file: `raw_after` (`LA:585-589`) is compared only to `raw_before` (`LA:591`). No field of `report` is derived from the persisted document. |
| **Violated property** | *What is persisted is what was authorized.* |
| **Minimal code locations** | `LA:583` (unchecked invocation), `LA:585-591` (bytes read, never parsed) |
| **Dependency graph** | The correctness of a *document-level* comparison rests on E2-F6 (serializer round-trip equivalence) — hence `R-11 → R-7`. A rollback on mismatch requires `R-3`. |
| **Activation conditions** | Any writer whose serialization is not a faithful round-trip of its argument. No concurrency required. Latent today only because E-4A blocks every production write. |
| **Expected fail-closed behavior** | After `writer` returns, parse the file and require the parsed document to equal `ledger`. On inequality: restore the pre-image bytes (under the held lock) and raise `LedgerWriteRefused` naming the divergence. |
| **Re-confirmed live** | Yes — executed here: `authorization=PERMIT`, `allocated={'by_object': ['UCOS-OBJ-000002']}`, no error, and disk holds `['EXTRA.py', 'a.py', 'b.py']` with `b.py → UCOS-OBJ-999999`. |

## A.8 — E2-F2 · Silent writer: allocation reported, nothing persisted

| | |
|---|---|
| **Current behavior** | `ukb._dump_json` (`ukb.py:135-146`) begins with `T.forbid_data_telemetry(...)` then `if _stamp_eq_json(path, obj): return`. Either the early return or a raise from the guard can leave the file untouched after authorization has already been granted. With `writer=lambda p, o: None`, `commit()` returns `allocating=True, total_allocations=1, allocated={'by_object': [...]}, bytes_changed=False` and prints `identity ledger ALLOCATED 1 permanent identifier(s) [by_object+1] …` while the disk is unchanged. |
| **Violated property** | *A reported allocation actually happened.* This is the mirror of the D0.1 defect the module's header documents (`LA:1-45`); the original fix addressed only the *understating* direction. |
| **Minimal code locations** | `LA:583`, `LA:585-591`; `ukb.py:139-140` (the early return that has exactly this shape) |
| **Dependency graph** | Same missing comparison as E2-F1; one unit closes both. |
| **Activation conditions** | Any writer that returns without writing, for any reason. |
| **Expected fail-closed behavior** | A missing or unparseable file after `writer`, or a parsed document unequal to `ledger`, is a refusal. |
| **Re-confirmed live** | Yes — executed here: `allocating=True total=1 bytes_changed=False`, disk `['a.py']`. |

## A.9 — E2-F3 · `bytes_changed` is informational, never enforced, never rendered

| | |
|---|---|
| **Current behavior** | Assigned at `LA:591` as the final statement before `return`. `commit()` performs no comparison, assertion or refusal involving it. `format_report` (`LA:223-249`) — the sole operator-facing rendering, used by all four call sites (`ukb.py:1293`, `:1299`, `:2380`, `:2401`, `uga_engine.py:2003`) — never references it, so the value is computed and discarded unseen. Its only production consumer is `uga_engine.py:2004`, which uses it as a cache-invalidation hint. The contradiction `allocating=True ∧ bytes_changed=False` is fully representable and checked nowhere. |
| **Violated property** | *A measurement that exists is either enforced or shown.* |
| **Minimal code locations** | `LA:591` (assignment), `LA:223-249` (the rendering that omits it) |
| **Dependency graph** | The *enforcement* half becomes provably unreachable once `R-7` lands (§D.5), so `R-8`'s assertion is defence in depth rather than the load-bearing control. The *rendering* half is independent — and constrained by the fact that `format_report` is also called on manifests that have no `bytes_changed` key (`plan()` output at `ukb.py:1293`; `_verify_permit`'s refusal message at `LA:443`). |
| **Activation conditions** | Every invocation (rendering). The contradiction requires a silent or equal-output writer (E2-F2). |
| **Expected fail-closed behavior** | `allocating=True ∧ bytes_changed=False` is a refusal. `bytes_changed` appears in the operator line whenever the report carries it. |
| **Re-confirmed live** | Yes — executed here: `format_report` output contains no `bytes_changed` token; the contradiction was produced and returned without error. |

## A.10 — E2-F4 · `NO_ALLOCATION` authorizes arbitrary non-allocating mutation

| | |
|---|---|
| **Current behavior** | `_NoAllocation`'s docstring (`LA:282-293`) claims the sentinel "can only ever permit less". It is checked only against `manifest["allocating"]` (`LA:435-442`), and `allocating` is blind to `version`, `discovered_volumes` (both in `NON_ALLOCATION_KEYS`, `LA:83-85`) and to every non-identifier field of every existing record (`LA:112-119`). |
| **Violated property** | *A verified no-allocation claim permits strictly less than a permit.* The claim is made in source and is false. |
| **Minimal code locations** | `LA:435-442` (the whole of the sentinel's verification) |
| **Dependency graph** | Independent. **`R-9` is a prerequisite of `R-5a`**: without it, classifying `history` would widen the set of writes `NO_ALLOCATION` accepts. Its reproduction is masked by E1-F5 on any ledger carrying `history`. |
| **Activation conditions** | Any invocation passing `NO_ALLOCATION` with a document that differs from the pre-image outside the identifier projection. Today that is only `ukb.py:2380-2384`, whose branch is dead on the production ledger for the separate reason in A.4. |
| **Expected fail-closed behavior** | `NO_ALLOCATION` is accepted only when the proposed document equals the pre-image. Any difference refuses, naming the differing top-level keys. |
| **Re-confirmed live** | Yes — executed here on a `history`-free fixture: `allocating=False authorization=NO_ALLOCATION bytes_changed=True`, disk now `version=99`, `discovered_volumes={'VOL-666': 1}`. |

## A.11 — E2-F5 · `LEDGER-INV-01` is lexically blind to parameter indirection

| | |
|---|---|
| **Current behavior** | `LEDGER-INV-01` (`uga_engine.py:1250-1272`, engine `_direct_ledger_writes` at `:1093-1120`, patterns at `:1079-1092`) requires the ledger to be **named on the same source line** as a write primitive. A function receiving the path as a parameter never names it. Re-tested here against the live compiled patterns: `uga_engine._write_text` body, `ukb._dump_json` body, and both `writer=` call sites all return `match=False`; only a naïve `_dump_json(LEDGER_PATH, ledger)` returns `True`. Both production writers are exactly the unmatched shape. |
| **Violated property** | *The invariant measures the claim it states* — `IDENTITY_LEDGER_HAS_ONE_WRITE_PATH`. |
| **Minimal code locations** | `uga_engine.py:1079-1092` (patterns), `:1093-1120` (engine), `:1250-1272` (declaration and `why` text); mirrored in `platform/tests/test_ledger_authority.py:98-104` |
| **Dependency graph** | The `why`-text correction depends on `R-7`: once writer divergence is refused at runtime, the invariant no longer needs to claim it constrains writer behaviour. The AST measurement is independent. |
| **Activation conditions** | Any future write reached through a helper that takes the path as a parameter — the shape the invariant's own comment says it exists to prevent. |
| **Expected fail-closed behavior** | Passing a ledger reference to a function that writes that parameter is a violation, regardless of whether the write primitive and the ledger name share a line. Unreadable or unparseable source remains a violation, never a pass (`uga_engine.py:1109-1112`). |
| **Re-confirmed live** | Yes — pattern test above. The proposed AST measurement was prototyped over all tracked `.py` files: **0 violations in current source** (backward-compatible) and a synthetic `helper(LEDGER_PATH, "{}")` where `helper` writes its parameter is **caught**. |

## A.12 — E2-F6 · Serializer equivalence between authorized and persisted form is unproven

| | |
|---|---|
| **Current behavior** | Three serializers exist over one document: `LA._canonical` (`LA:303-310`, `sort_keys=True`, compact), `ukb._dump_json` (`ukb.py:135-146`, `indent=2`, insertion order), `uga_engine._dump` (`uga_engine.py:143-146`, `indent=2`, `sort_keys=False`). No round-trip equivalence test exists and none is asserted in source. |
| **Violated property** | *The relationship between the three serializations of one document is measured.* |
| **Minimal code locations** | `LA:303-310`, `ukb.py:135-146`, `uga_engine.py:143-160` |
| **Dependency graph** | **`R-11` is a prerequisite of `R-7`'s correctness.** `R-7` compares *documents*, not bytes; that choice is sound only if every serializer round-trips faithfully. Measured here on the live ledger: `_canonical` differs from the other two at byte level (1 786 167 vs 2 274 511 bytes), `ukb` and `uga` are **byte-identical** to each other, and all three parse back to a document equal to the original. So a byte-level comparison would be wrong and a document-level comparison is correct — which is exactly the fact `R-11` must pin. |
| **Activation conditions** | Becomes load-bearing the moment any control binds bytes or documents rather than the projection — i.e. the moment `R-7` lands. |
| **Expected fail-closed behavior** | A test failure if any of the three serializers stops round-tripping, or if `ukb` and `uga` output diverge at byte level. |
| **Re-confirmed live** | Yes — measurement above. |


---

# Section B — Fix Independence Proof

## B.0 The proof obligation, stated once

For each defect three things must hold. They are proved once here in general form and then
discharged per defect in B.1–B.12 by pointing at which general form applies.

**(i) The fix does not require governance.** A fix requires governance iff writing it forces
a choice among mutually exclusive answers to *who may authorize*, *what an authorization
means*, *when it expires*, *which authority owns the ledger*, or *what counts as a mutation
or an audit event*. Three fix shapes provably force no such choice:

- **Shape RECONCILE** — the fix compares two values the code already computes, or replaces
  two reads of one file with one read. It introduces no predicate over authority.
  *(R-1, R-2, R-7, R-8-assert, R-11)*
- **Shape RESTRICT** — the fix refuses a state transition that existing source already
  declares impossible, in a docstring or comment written by the same authority that owns the
  code being changed. Making an existing claim true adds no claim. *(R-4, R-5b, R-6, R-9)*
- **Shape MEASURE** — the fix widens a measurement's coverage to the shape the measurement
  already names, or classifies an existing key into one of two sets that already exist.
  *(R-3, R-5a, R-10)*

**(ii) The fix does not alter authority.** `_verify_permit` (`LA:432-543`) is the sole
authorization decision procedure in the repository, and **no unit modifies it**. No unit
adds a caller, a role, a signer, an issuer, an expiry rule, a scope field, or a register
operation. Ten of eleven units are monotonically restrictive: for every `(before, ledger,
actor, permit)` tuple, if the unit changes the outcome it changes it from ACCEPTED to
REFUSED. A control that can only refuse more cannot grant authority to anyone. `R-5a` is
the exception and is discharged separately in B.4.

**(iii) The fix remains valid under every possible answer to FD-1…FD-5.** Each of the five
governance roots ranges over *who* / *what* / *when* / *which authority* / *which domain
rule*. Every unit's predicate is a function of `(before, ledger, persisted_bytes)` only —
three artifacts fixed independently of all five. Formally: if `Φ` is a unit's refusal
predicate and `g` any assignment to FD-1…FD-5, then `Φ` does not read `g`, so `Φ`'s truth
value is invariant under `g`. The units that touch `permit` at all (`R-9`) narrow the
`NO_ALLOCATION` *claim*, which is not a permit and is issued by nobody — it is an assertion
by the caller about `(before, ledger)`, checked against `(before, ledger)`.

## B.1 R-1 · E1-F7

- **No governance:** Shape RECONCILE. One read replacing two. The predicate added is
  `json.loads(raw_before) == before`, which is trivially true after the change because both
  derive from one buffer. No predicate over authority exists.
- **No authority altered:** `report`'s contents, the manifest, the digest and
  `_verify_permit`'s inputs are bit-identical to today for every input. The change is
  observationally neutral except that the two reads can no longer disagree.
- **Valid under every FD answer:** the identity of two reads of one file is not a function
  of who may write it.

## B.2 R-2 · E1-F1

- **No governance:** Shape RECONCILE. Compare `raw_before` to the bytes present immediately
  before `writer`; refuse on inequality. The E1 report states this as fact
  (`PHASE0-E1-ATOMICITY-REPORT.md` §6): *"re-reading and comparing bytes before writing
  decides nothing about authority."*
- **No authority altered:** monotonically restrictive. Every write accepted after `R-2` was
  accepted before it. `_verify_permit` is unchanged and still runs first.
- **Valid under every FD answer:** the refusal predicate is `bytes(t₁) ≠ bytes(t₀)`. No
  assignment to FD-1…FD-5 makes it desirable for `commit()` to overwrite a state it did not
  verify — under *any* authority, the write that lands is then not the write that was
  checked, which is a defect for that authority too.

## B.3 R-3 · E1-F2

- **No governance:** Shape MEASURE/RESTRICT with no policy content. An advisory
  `fcntl.flock(LOCK_EX)` on the ledger's containing directory serializes callers. Choosing
  a lock *mechanism* is an implementation choice among equivalents, not a governance choice;
  the repository already contains the precedent (`register.sh:187-197` for the transaction,
  `governance_telemetry._atomic_write` for telemetry) and neither is a governance artifact.
- **No authority altered:** exclusion changes *when* a caller runs, never *whether* it is
  authorized. Both callers still present a permit to the unchanged `_verify_permit`.
- **Valid under every FD answer:** mutual exclusion is required by every possible authority
  assignment, because no authority is served by two of its own writers interleaving. The
  design deliberately introduces **no new file**: the lock is taken on the existing
  directory file descriptor, so no new tracked object is created, no `.gitignore` rule is
  needed, and no entry in `00-BOOK/DATA/exclusion-register.json` is required — the three
  places where a new lock file would have created downstream governance surface.

## B.4 R-5 · E1-F5 — the one non-monotonic unit, proved in full

`R-5a` (classify `history` into `NON_ALLOCATION_KEYS`) is the only unit that moves any write
from REFUSED to ACCEPTED. Its independence therefore needs a stronger argument than "it can
only refuse more."

- **No governance:** Shape MEASURE. `PHASE0-GOVERNANCE-INDEPENDENT-DETERMINATION.md` §4
  classifies this remedy as *"classify an existing key into one of two existing sets"*. The
  choice between the two sets is **forced by the data, not decided**: `IDENTITY_MAPS` maps a
  key to *the field name holding a permanent identifier* (`LA:71-77`). Measured on the live
  ledger, `history` is `{uid: [snapshot, …]}` — 1628 lists, no records, no identifier field.
  It is not expressible in `IDENTITY_MAPS`' vocabulary at all. `NON_ALLOCATION_KEYS` is
  therefore the only admissible classification, and no alternative had to be weighed.
- **The permission expansion is exactly characterised.** Before `R-5a`, a write is refused
  under `NO_ALLOCATION` iff `allocating`, and `history`'s presence makes `allocating` true
  unconditionally. After `R-5a`, `allocating` is false when nothing outside `history` moves.
  The newly-accepted set is therefore `{writes whose only difference from the pre-image lies
  in history} ∪ {byte-identical no-ops}`.
- **`R-9` collapses that set to the byte-identical no-op.** With `R-9` in place,
  `NO_ALLOCATION` additionally requires `ledger == before`. The first disjunct is empty. The
  newly-accepted set is exactly `{ledger == before}` — a write that changes nothing. This is
  verified by execution (§G, rows `E1-F5a` and `idem`).
- **No operator workflow is widened.** A `history`-only append is refused under
  `NO_ALLOCATION` before `R-5` (because `allocating=True`) and after `R-5`+`R-9` (because
  the document differs). In both worlds it requires a permit. Nothing that needed a permit
  stops needing one.
- **`R-5b` adds no mutation definition.** `record_snapshots` (`ukb.py:314-330`) declares in
  its own docstring: *"APPEND-ONLY … Preserves every prior content_hash and version."*
  Verified structurally: the function only ever calls `lst.append` on a
  `hist.setdefault(uid, [])` list (`ukb.py:321,340`) and never mutates a prior element.
  `R-5b` refuses the transitions that docstring already forbids — list absent, shortened, or
  not prefixed by its recorded value. It does not classify writes into governed and
  ungoverned, requires no audit event, and names no authority. *Recorded honestly: if a
  reviewer judges any new refusal to be a definitional act, `R-5b` is separable from `R-5a`
  and can be deferred — but then `R-5a` must not ship either, because `R-5a` without `R-5b`
  makes `history` erasure a non-allocating change under a `NO_ALLOCATION`-adjacent path.
  The pair is atomic in either direction.*
- **Valid under every FD answer:** whether `history` is one of two existing measurement
  categories, and whether a list may lose its prefix, are both decided by the shape of the
  data on disk.

## B.5 R-4 · E1-F4

- **No governance:** Shape RESTRICT. `assert_append_only`'s own docstring (`LA:122-128`)
  states the property as *"a permanent identifier could stop being permanent"* and the module
  header (`LA:47-52`) as *"append-only, no identity reissue"*. A record whose `object_class`
  changes from `TOOLING_OBJECT` to `GOVERNANCE_OBJECT` while keeping its identifier is the
  same defect in the fields the projection cannot see. The fix widens an existing refusal to
  the rest of the record it already refuses to reissue.
- **No authority altered:** monotonically restrictive, and the manifest/digest are
  deliberately **not** widened, so `manifest_digest` (`LA:316-336`) is byte-stable and no
  permit binding changes. `_verify_permit` sees identical inputs.
- **Valid under every FD answer:** the fix is a predicate over `(before, ledger)`. No
  authority assignment makes silent rewriting of a permanent record's body correct.
- **Backward compatibility is measured, not assumed:** all four allocators return existing
  entries untouched — `ukb.allocate` (`ukb.py:892-894`), `ukb.allocate_execution`
  (`ukb.py:2249-2251`), `uga_engine.epoch1_identity` (`:284-292` for documents, `:296-299`
  for objects), `uga_engine`'s observation minter (`:500-504`). No production path proposes a
  changed record body.

## B.6 R-6 · E1-F6

- **No governance:** Shape RESTRICT. `assert_append_only` already refuses reissue in the
  key→identifier direction (`LA:140-144`). Identifier uniqueness is the same property in the
  identifier→key direction, and the module header states it as *"no identity reissue"*
  without direction. The E1-F1 damage is described in the source report as *"`UCOS-OBJ-000002`
  is now bound to two different paths across time"* — a duplicate identifier is that state
  reached without any concurrency at all.
- **No authority altered:** monotonically restrictive; measurement and digest unchanged.
- **Valid under every FD answer:** "one identifier names at most one thing" is prior to any
  question of who may allocate it.
- **Backward compatibility is measured:** zero duplicates within `by_path` (1628), `by_object`
  (5374), `by_execution` (0), `by_observation` (7), and zero duplicates across the union of
  all four. The live ledger already satisfies the new refusal.
- **Not a closure of MW-3, and said so:** `R-6` does not eliminate the window. It removes the
  window's dependence on a single refusal leg, which is what E1-F6's UNVERIFIABLE
  classification asked for (*"needs a test, not a decision"*). The test is `R-6`'s regression
  test; the refusal is what makes the test's PASS condition meaningful.

## B.7 R-7 · E2-F1, E2-F2

- **No governance:** Shape RECONCILE. `commit()` already reads the persisted bytes
  (`LA:585-589`); the fix parses them and compares to the object it was handed. The E-2 report
  states the gap as *"nothing is compared"* and the determination classifies the remedy as
  *"parse and compare after write"*.
- **No authority altered:** monotonically restrictive. The comparison is between two objects
  both already inside `commit()`'s scope; no third party is consulted. `_verify_permit` still
  decides authorization, unchanged, and still runs before the write.
- **Valid under every FD answer:** "the file holds what the function was asked to persist" is
  a property of the function, not of the authority that permitted the call.
- **The rollback is a revert, not a new format.** On mismatch, restoring `raw_before` writes
  back bytes that were on disk moments earlier under the held `R-3` lock. It introduces no
  serialization and no on-disk format, so the module's stated non-writer property (`LA:57-64`)
  is preserved in substance: `commit()` still never *invents* bytes. *Flagged, not assumed:
  this is the one place where a unit changes a documented design property of the module. The
  alternative — refuse loudly without restoring — is strictly better than today (detected
  rather than silent) but leaves the ledger in a state no permit authorized, which fails the
  fail-closed requirement in Section A. The rollback variant is specified as the default and
  the non-rollback variant is retained as an explicit fallback in C.7.*

## B.8 R-8 · E2-F3

- **No governance:** Shape RECONCILE (the assertion) plus a string change (the rendering).
  `allocating ⇒ bytes_changed` relates two fields of one report. Rendering a field that is
  already computed decides nothing.
- **No authority altered:** restrictive for the assertion, neutral for the rendering. The
  only production consumer of `bytes_changed` (`uga_engine.py:2004`) reads the same value.
- **Valid under every FD answer:** an internal contradiction in a report is a defect under
  every authority.
- **Subsumption recorded rather than hidden:** after `R-7`, `allocating ∧ ¬bytes_changed` is
  unreachable — proof in D.5. `R-8`'s assertion is therefore defence in depth. Its
  independent content is the rendering, which no other unit supplies.

## B.9 R-9 · E2-F4

- **No governance:** Shape RESTRICT, and uniquely well-supported: the sentinel's own
  docstring (`LA:282-293`) already asserts the property being implemented — *"Passing it is
  therefore strictly safer than passing a permit — it can only ever permit less."* The
  determination records the same argument: *"the sentinel's own docstring already claims this
  property; making the claim true adds no authority."*
- **No authority altered:** `NO_ALLOCATION` is not a permit. It is issued by nobody, appears
  in no register, and names no actor. It is a caller assertion about `(before, ledger)`,
  verified against `(before, ledger)`. Narrowing when the assertion is believed adds no
  permission to anyone and removes none from `_verify_permit`.
- **Valid under every FD answer:** the claim "this write allocates nothing" is checkable
  without knowing who may allocate.
- **Compatible with the one real production case:** `ukb.py:2380-2384`'s idempotent branch
  reaches `commit()` with `ledger` equal to the pre-image — `allocate_execution` early-returns
  on an existing key (`ukb.py:2249-2251`) and `_exec_declare` mutates the ledger nowhere else
  (`ukb.py:2343-2385`). Verified by execution (§G row `idem`).

## B.10 R-10 · E2-F5

- **No governance:** Shape MEASURE. The AST pass measures a syntactic fact — *is a ledger
  reference passed as an argument that the callee writes* — and reports it as a violation of
  an invariant that already exists and already fails closed
  (`uga-declaration.json`: `LEDGER-INV-01`). No allow-list, no exemption list, no owner, no
  new invariant identifier.
- **No authority altered:** `LEDGER-INV-01` remains blocking, remains owned by
  `UCOS-UGA-001`, and keeps its identifier and name. Its measurement widens; its authority
  does not move.
- **Valid under every FD answer:** whether a helper writes a path it was handed is a fact
  about source text.
- **Prototyped for both directions:** 0 violations over all tracked `.py` files at
  `77798202` (so it does not manufacture failures), and a synthetic indirect write is caught
  (so it is not vacuous).
- **The `why`-text correction is not a weakening:** it stops the declaration implying that
  the invariant constrains what `writer` does after `commit()` hands it the path, because
  after `R-7` that is constrained at runtime and named there. Depends on `R-7`.

## B.11 R-11 · E2-F6

- **No governance:** Shape RECONCILE, expressed as a test. It asserts a relation among three
  existing serializers and adds no production code.
- **No authority altered:** a test grants nothing.
- **Valid under every FD answer:** JSON round-trip fidelity is arithmetic.

## B.12 Defects that could NOT be proved governance-independent

**None. All twelve remain in the remediation set.**

The three defects excluded from this phase were excluded by
`PHASE0-GOVERNANCE-INDEPENDENT-DETERMINATION.md` §5, not by this analysis, and this analysis
confirms each exclusion rather than revisiting it:

| Excluded | Why no fix here can be written without governance |
|---|---|
| E1-F3 | Recording that an authorization was *used* requires deciding whether it is single-use. `single_use` appears in the register shape documented at `PHASE0-E4A-ISSUANCE-PATH-REPORT.md:35` and is written by the test fixture (`test_ledger_authority.py:82`), but the string does not occur anywhere in `ledger_authority.py` — `_verify_permit` neither reads it nor acts on it. Giving it an effect is a permit rule. Constraint 2/3. |
| E-3 | Replacing `UGA-INV-10` requires defining what counts as a mutation and what an audit event must contain. Constraint 3 forbids both. Note this phase does **not** improve E-3 even incidentally: no unit emits an audit event, so counterexample C6 of the E-3 report (*"every `ledger_authority.commit()` call"* is unaudited) is unchanged by all eleven units. |
| E-4A | Creating an issuance path requires issuer identity, issuance semantics and expiry. Constraint 3 forbids all three. |

One boundary case was examined and **excluded**, with justification, because it is not among
the twelve and would exceed this authorization:

> **Widening `manifest_digest` to cover the document rather than the projection.** This
> would close the residual identified in F.4 (`RES-1`). It is arguably Shape MEASURE and
> therefore arguably governance-independent — but it changes what an issuer must transcribe
> from `plan()` output, i.e. it changes what a permit *binds*. Constraint 3 forbids
> introducing permit semantics, and the safest reading is that changing the content of the
> permit binding is inside that prohibition. It is recorded in F.4 as a derived residual and
> is **not** specified, designed or ranked here.


---

# Section C — Minimal Remediation Design

**No implementation is performed.** Each unit below states the smallest change set that
eliminates the defect while preserving all existing governance behavior. Code fragments are
*specifications of intent*, not patches; they are shown because a prose description of a
comparison is less precise than the comparison.

## C.0 Facts that constrain every design

Established by measurement, and each one rules out an otherwise-plausible design:

| # | Constraining fact | Consequence |
|---|---|---|
| CF-1 | `format_report` is called on `plan()` output (`ukb.py:1293`) and inside `_verify_permit`'s refusal message (`LA:443`). Neither carries `bytes_changed`. | `R-8`'s rendering must use `report.get("bytes_changed")` and omit the token when absent, or `--plan` and every `NO_ALLOCATION` refusal raise `KeyError`. |
| CF-2 | `platform/tests/test_ledger_authority.py:555-572` asserts, by AST, that `plan()` and `commit()` reach the measurement **through `build_manifest`** and never call `allocation_report` directly, and that `def allocation_report(` and `def build_manifest(` each occur exactly once. | No unit may add a second `allocation_report` definition, and no unit may make `commit()` call `allocation_report` directly. Helper predicates must be new module-level functions. |
| CF-3 | `LEDGER-INV-01` and its test mirror both skip `00-BOOK/tools/ledger_authority.py` (`uga_engine.py:1105`, `test_ledger_authority.py:131`). | `fcntl`, `os.replace` and byte-restoring writes added *inside the authority* do not trip the invariant. The same code added anywhere else would. |
| CF-4 | `ukb._dump_json` and `uga_engine._dump` produce **byte-identical** output for the same document (measured on the live ledger: both 2 274 511 bytes); `LA._canonical` does not (1 786 167 bytes). All three round-trip to an equal document. | `R-7` must compare **documents**, not bytes. A byte comparison would be wrong for `_canonical` and would couple the authority to one writer's formatting. |
| CF-5 | `.runtime/` is git-ignored and is the declared home for per-clone operational state (`.gitignore`; `governance_telemetry` docstring). A **new** ignored path under `00-BOOK/DATA/` would require an entry in `00-BOOK/DATA/exclusion-register.json` (UCOS-RIB-001 measures every ignored path against it). | `R-3` uses a directory file descriptor and creates **no file**, avoiding both the exclusion register and the "a new tracked file is an anonymous object" regress the module header already reasons about (`LA:268-274`). |
| CF-6 | `00-BOOK/DATA/allocation-permits.json` does not exist; zero permits have ever been issued (E-4A). | `R-5a`, which changes every future `manifest_digest`, invalidates no issued permit **today**. It must land before any E-4A remediation. |

---

## C.1 R-1 — E1-F7 · one read underwrites verification and change measurement

**Files touched:** `00-BOOK/tools/ledger_authority.py`
**Functions touched:** `commit` (`:546-593`); new module-level helper `read_preimage_bytes`

```
# replaces LA:567 and LA:577-581
raw_before, before = read_preimage_bytes(path)   # (bytes|None, dict)
assert_append_only(before, ledger)
```

`read_preimage_bytes` performs one `open(path,'rb')`, returns `(None, {})` on
`FileNotFoundError` (preserving E1-S4), and raises `LedgerWriteRefused` on `OSError` or
`json.JSONDecodeError` with the identical message shape as `load_preimage` (`LA:100-110`,
preserving E1-S2). `load_preimage` is retained unchanged because `plan()` (`LA:417`) and
`preimage_digest` callers use it.

- **Invariants affected:** none. `before` is value-identical for every input.
- **Migration:** none.
- **Backward compatibility:** `commit()`'s return value is unchanged. `load_preimage` keeps
  its signature and its two exported behaviours.
- **Failure modes introduced:** one. A ledger that is readable as bytes but whose *bytes*
  differ from what `json.load` would have re-read is no longer possible — which is the point
  — but a ledger holding a valid JSON *non-object* (e.g. `[]`) now flows into
  `assert_append_only` identically to today, since `load_preimage` has the same behaviour. No
  new class of input is accepted.
- **Verification:** `test_plan_and_commit_measure_the_same_allocation` and all 40 existing
  tests must stay green; new test `test_the_preimage_is_read_exactly_once` counts `open`
  invocations on the ledger path during `commit()` via monkeypatched `builtins.open` and
  asserts ≤ 2 (one pre-write, one post-write) where today it is 3.

## C.2 R-2 — E1-F1 · re-read and compare immediately before the writer

**Files touched:** `00-BOOK/tools/ledger_authority.py`
**Functions touched:** `commit`

```
# inserted between LA:573 (_verify_permit) and LA:583 (writer)
raw_now = _read_bytes_or_none(path)
if raw_now != raw_before:
    raise LedgerWriteRefused(
        "identity ledger write refused — the ledger changed between verification and "
        "write; the state that was checked is no longer the state on disk. Re-run the "
        "measurement against the current pre-image."
    )
writer(path, ledger)
```

- **Invariants affected:** strengthens E1-S1 (a refused write leaves the file
  byte-identical) to cover MW-1 mutation, not only verification failure.
- **Migration:** none.
- **Backward compatibility:** total for single-writer operation. `raw_now == raw_before`
  holds trivially when nothing else touched the file.
- **Failure modes introduced:** two, both stated rather than discovered later.
  (i) A *legitimate* concurrent no-op rewrite that changes only whitespace would now refuse.
  No production writer produces one — both are byte-stable on identical documents (CF-4) —
  but a future writer that stamps a timestamp would make this a spurious refusal.
  (ii) The window is narrowed, not eliminated: the interval between the re-read and
  `writer`'s own `open` remains. `R-3` is what makes that interval empty for cooperating
  processes; `R-2` is what makes a *non*-cooperating writer detectable. Neither alone is
  sufficient and the specification does not claim otherwise.
- **Verification:** reproduction test `test_a_concurrent_write_inside_the_window_is_refused`
  (E.2), which injects the concurrent write at `git_head` exactly as the E1 report's probe
  does.

## C.3 R-3 — E1-F2 · exclusive advisory lock across the whole of `commit()`

**Files touched:** `00-BOOK/tools/ledger_authority.py`
**Functions touched:** `commit`; new module-level context manager `_ledger_lock`

```
import fcntl, contextlib

@contextlib.contextmanager
def _ledger_lock(path, *, timeout=60.0):
    """Serialize commit() against every other commit() on the same ledger.

    Locks the ledger's CONTAINING DIRECTORY, not a lock file: a new file under
    00-BOOK/DATA would be an anonymous tracked object requiring an allocation to
    name — the regress PERMIT_REGISTER_NAME's comment already terminates once —
    and it would need an entry in the tracked exclusion register. A directory fd
    needs neither and works for a first-ever mint, when no ledger file exists.
    """
```

Body: `os.open(dirname, os.O_RDONLY)`, then `fcntl.flock(fd, LOCK_EX | LOCK_NB)` in a
bounded retry loop; on timeout raise `LedgerWriteRefused` naming the timeout. `finally`:
`LOCK_UN` and `os.close`. `commit()`'s entire body from `read_preimage_bytes` through the
post-write comparison runs inside the `with`.

- **Invariants affected:** none measured; MW-1 and MW-2 become empty for cooperating
  processes.
- **Migration:** none. No file, no directory, no ignore rule, no exclusion-register entry
  (CF-5).
- **Backward compatibility:** `register.sh:187-197`'s advisory lock is left in place and
  untouched; the two locks are independent and non-conflicting (different objects, and
  `flock` does not interact with a timestamp file). `flock` on a directory fd does not
  impede ordinary reads or writes of files in that directory by processes that do not call
  `flock`, so `_dump_json`'s many other writes into `00-BOOK/DATA` are unaffected.
- **Failure modes introduced:** four, all named.
  (i) **Advisory only.** A process that never calls `flock` is not excluded. Since
  `commit()` is the sole write path (`LEDGER-INV-01`, strengthened by `R-10`), the only
  non-cooperating writer is an out-of-band edit — which `R-2` detects.
  (ii) **Filesystem dependence.** `flock` semantics are not guaranteed on NFS/SMB. Verified
  working on this platform (macOS/APFS): a second process raised `BlockingIOError` under
  `LOCK_EX|LOCK_NB`. On a filesystem that silently no-ops, `R-3` degrades to no protection
  and `R-2` remains the detector. The specification does not claim portability it has not
  measured.
  (iii) **New refusal on contention.** A blocked caller refuses after `timeout` instead of
  waiting forever. 60 s is chosen against the measured ~60 s discovery pass being *outside*
  the lock, so lock hold time is I/O-bounded, not discovery-bounded.
  (iv) **No coverage of MW-3.** The caller's own ledger read (`uga_engine.py:1700`) happens
  before `commit()` is entered and therefore before the lock exists. `R-3` cannot close it;
  `R-6` plus the existing key-removal check are what bound it.
- **Verification:** `test_two_commits_cannot_interleave` (E.3), using two subprocesses and a
  writer that sleeps inside the lock.

## C.4 R-4 — E1-F4 · refuse a rewrite of an existing record's body

**Files touched:** `00-BOOK/tools/ledger_authority.py`
**Functions touched:** `assert_append_only` (`:121-170`); new module-level helper
`_record_index`

```
# added inside assert_append_only's existing per-map loop, alongside the
# REMOVED / REISSUED refusals it already raises
old_rec, new_rec = _record_index(before, map_name), _record_index(after, map_name)
for key in old_rec:
    if key in new_rec and old_rec[key] != new_rec[key]:
        changed = sorted(
            f for f in set(old_rec[key]) | set(new_rec[key])
            if old_rec[key].get(f) != new_rec[key].get(f)
        ) if isinstance(old_rec[key], dict) and isinstance(new_rec[key], dict) else ["<record>"]
        problems.append(
            f"{map_name}: record body of {key!r} would be REWRITTEN "
            f"(fields {changed}); a permanent identity's record is append-only in full"
        )
```

- **Invariants affected:** extends E1-S8's scope from the identifier field to the whole
  record. `manifest_digest` is deliberately **not** widened, so digests are byte-stable.
- **Migration:** none — measured: no allocator mutates an existing record (B.5), and every
  live record shape is homogeneous (`by_path` 1628× `{category, first_seen, page_count,
  page_start, universal_id}`; `by_object` 5374× `{category, first_seen, object_class,
  universal_id}`; `by_observation` 7× `{first_seen, kind, observation_id, observer,
  subject}`).
- **Backward compatibility:** total for every production path. **The one real risk is a
  future intentional schema change** to a record — e.g. adding a field to every `by_object`
  record. That would be refused. This is correct behaviour under the module's own append-only
  claim, and the escape hatch is the same one the module already provides for a new identity
  map: an explicit, reviewed change to this module. Recorded so it is a known consequence
  rather than a surprise during the next schema evolution.
- **Failure modes introduced:** one — the schema-evolution refusal above.
- **Verification:** reproduction test `test_a_record_body_rewrite_is_refused` (E.4);
  regression test asserting a *new* key's record body is unconstrained (only *existing*
  records are frozen).

## C.5 R-5 — E1-F5 · classify `history`, and enforce its declared append-only property

**Files touched:** `00-BOOK/tools/ledger_authority.py`
**Functions touched:** module constant `NON_ALLOCATION_KEYS` (`:83-85`);
`assert_append_only`; new module-level helper `_history_problems`

**R-5a** — one line, plus the comment that makes the classification reviewable:

```
NON_ALLOCATION_KEYS: frozenset[str] = frozenset({
    "version", "category_seq", "discovered_volumes", *MONOTONIC_COUNTERS,
    # `history` is {universal_id: [snapshot, ...]} — snapshot lists, not records
    # carrying a permanent identifier, so it is not expressible in IDENTITY_MAPS'
    # vocabulary (map -> identifier FIELD NAME). It is append-only derived
    # observation of content, written by ukb.record_snapshots; its append-only
    # property is enforced below rather than by allocation measurement.
    "history",
})
```

**R-5b** — prefix preservation, refused inside `assert_append_only`:

```
for uid, old_list in (before.get("history") or {}).items():
    new_list = (after.get("history") or {}).get(uid)
    if new_list is None:
        problems.append(f"history: {uid!r} would be REMOVED (snapshots are append-only)")
    elif not isinstance(new_list, list) or new_list[:len(old_list)] != old_list:
        problems.append(
            f"history: {uid!r} snapshot list is not an extension of the recorded "
            f"{len(old_list)} entries (append-only; ukb.record_snapshots)"
        )
```

- **Invariants affected:** `allocation_report`'s `unmeasured` term (`:207-211`) stops
  reporting `history`, so `allocating` (`:196-198`) stops being unconditionally `True` on the
  production ledger. This **revives** the `ukb.py exec declare` idempotent branch
  (`:2380-2384`), which is dead today.
- **Migration:** none for data. **`manifest_digest` changes for every manifest**, because
  `unmeasured_maps` moves from `['history']` to `[]`. Harmless today (CF-6: zero permits
  exist) and a hard ordering constraint against E-4A (D.3).
- **Backward compatibility:** the accepted set widens by exactly `{ledger == before}` once
  `R-9` is in place (B.4, verified in §G). A `history`-only append requires a permit before
  and after.
- **Failure modes introduced:** two.
  (i) A future writer that legitimately rewrites a snapshot (e.g. backfilling a corrected
  `content_hash`) is refused. `record_snapshots` never does this.
  (ii) `R-5a` shipped without `R-5b` would make `history` erasure a non-allocating,
  refusal-free change. The pair is atomic; D.2 encodes it.
- **Verification:** `test_a_byte_identical_write_allocates_nothing` against a ledger carrying
  `history` (E.5a); `test_history_erasure_is_refused` and
  `test_a_shortened_history_list_is_refused` (E.5b).

## C.6 R-6 — E1-F6 · refuse a duplicate permanent identifier

**Files touched:** `00-BOOK/tools/ledger_authority.py`; `platform/tests/test_ledger_authority.py`
**Functions touched:** `assert_append_only`

```
# after the per-map loop, before the category_seq checks
seen: dict[object, str] = {}
for map_name in IDENTITY_MAPS:
    for key, ident in _identifier_index(after, map_name).items():
        if ident is None:
            continue
        where = f"{map_name}[{key!r}]"
        if ident in seen:
            problems.append(
                f"identifier {ident!r} would be bound to BOTH {seen[ident]} and {where} "
                f"(a permanent identifier names at most one thing)"
            )
        else:
            seen[ident] = where
```

Scope note: the check spans **all four maps**, not one, because the four share one
`category_seq` counter (`LA:71-77` comments; `ukb.allocate_execution` and
`uga_engine.epoch1_identity` both draw from it), so a cross-map collision is exactly as
constructible as an intra-map one.

- **Invariants affected:** adds the identifier→key direction of the reissue property that
  `:140-144` enforces in the key→identifier direction.
- **Migration:** none — measured zero duplicates within each map and zero across the union
  (1628 + 5374 + 0 + 7).
- **Backward compatibility:** total.
- **Failure modes introduced:** one. If any future design intentionally binds one identifier
  to two keys (an alias), it is refused. No such design exists; `_identifier_index`'s
  one-field-per-record model has no place to express an alias.
- **Verification:** reproduction test `test_a_duplicate_identifier_is_refused` — which
  **currently fails**, because the duplicate is accepted today and lands on disk (§G).
  Regression test `test_the_mw3_interleaving_is_refused_by_two_independent_legs` (E.6).

## C.7 R-7 — E2-F1, E2-F2 · the persisted document must equal the authorized document

**Files touched:** `00-BOOK/tools/ledger_authority.py`
**Functions touched:** `commit`

```
writer(path, ledger)

raw_after = _read_bytes_or_none(path)
report["bytes_changed"] = raw_before != raw_after
if raw_after is None:
    _restore(path, raw_before)
    raise LedgerWriteRefused(
        "writer persisted nothing: the file is absent after the write, while the "
        "authorized manifest reports " + format_report(report)
    )
try:
    persisted = json.loads(raw_after.decode("utf-8"))
except (UnicodeDecodeError, ValueError) as exc:
    _restore(path, raw_before)
    raise LedgerWriteRefused(f"writer persisted unparseable content ({exc})") from exc
if persisted != ledger:
    _restore(path, raw_before)
    raise LedgerWriteRefused(
        "persisted document is not the authorized document — the writer did not "
        "serialize what commit() measured and authorized"
    )
```

`_restore(path, raw_before)` writes `raw_before` back, or removes the file when
`raw_before is None` (the first-mint case). It runs under the `R-3` lock.

- **Invariants affected:** establishes, for the first time, that `report` describes the
  persisted document and not only the pre-write inputs. `bytes_changed` is assigned *before*
  the refusals so the report is complete even in the refusal message.
- **Migration:** none.
- **Backward compatibility:** both production writers satisfy `persisted == ledger` — `_dump`
  round-trips by CF-4, and `_dump_json`'s early return (`ukb.py:141-142`) fires only when the
  file already equals `obj` under stamp neutralization, which on this ledger (no top-level
  `generated_at`) reduces to plain equality.
- **Failure modes introduced:** three.
  (i) **Detection is post-hoc.** The divergent bytes reach disk before the check runs. The
  rollback re-establishes the pre-image, but a crash between `writer` and `_restore` leaves
  the divergent document on disk. The window is bounded by two file operations under a held
  lock; it cannot be eliminated without moving serialization inside the authority, which
  changes the on-disk format ownership the module explicitly reserves to callers
  (`LA:560-564`). *This tradeoff is flagged, not resolved: moving the writer inside the
  authority is a larger change than this authorization covers.*
  (ii) **`_restore` makes the authority a byte-writer.** Justified in B.7; the bytes written
  are bytes that were on disk seconds earlier. **Fallback variant, retained explicitly:** omit
  `_restore` and raise only. This is strictly better than today (loud instead of silent) but
  leaves an unauthorized document on disk, failing A.7's fail-closed requirement. Choose the
  rollback variant unless an implementer identifies a concrete hazard in it.
  (iii) **`json` round-trip strictness.** A writer emitting NaN/Infinity, or non-string dict
  keys, would produce `persisted != ledger`. The ledger holds only strings and ints
  (measured), so no production case is affected; a future writer would be refused loudly.
- **Verification:** reproduction tests `test_a_divergent_writer_is_refused` and
  `test_a_silent_writer_is_refused` (E.7, E.8), both of which currently pass silently and
  must become refusals; regression test asserting the pre-image is restored byte-for-byte.

## C.8 R-8 — E2-F3 · enforce and render `bytes_changed`

**Files touched:** `00-BOOK/tools/ledger_authority.py`
**Functions touched:** `format_report` (`:223-249`); `commit`

Rendering — note `report.get`, forced by CF-1:

```
changed = report.get("bytes_changed")
if changed is not None:
    line += f" bytes_changed={changed}"
```

placed on both branches of `format_report`, i.e. also on the `no allocation` line, so an
operator can distinguish a verified no-op from an unnoticed non-write.

Enforcement, after `R-7`'s comparisons:

```
if report["allocating"] and not report["bytes_changed"]:
    _restore(path, raw_before)
    raise LedgerWriteRefused(
        "the report claims an allocation but the file did not move: "
        + format_report(report)
    )
```

- **Invariants affected:** removes a representable contradiction from the report type.
- **Migration:** none.
- **Backward compatibility:** the four `print(LA.format_report(...))` call sites
  (`ukb.py:1293`, `:1299`, `:2380`, `:2401`, `uga_engine.py:2003`) are the only consumers of
  the line; nothing parses it — grep for `identity ledger ALLOCATED` /
  `identity ledger: no allocation` finds only the producer, the Phase-0 reports, and
  substring assertions in `test_ledger_authority.py:207,219,256-257`, all of which remain
  satisfied by an appended token. `uga_engine.py:2004`'s `if report["bytes_changed"]` reads
  the same value.
- **Failure modes introduced:** one, and it is why CF-1 is called out: forgetting `.get`
  breaks `ukb build --plan` and every `NO_ALLOCATION` refusal message with `KeyError`.
- **Verification:** `test_the_operator_line_shows_whether_the_file_moved`;
  `test_plan_output_still_renders` (the CF-1 guard);
  `test_an_allocation_that_did_not_move_the_file_is_refused` (E.9).

## C.9 R-9 — E2-F4 · `NO_ALLOCATION` requires the document to equal the pre-image

**Files touched:** `00-BOOK/tools/ledger_authority.py`
**Functions touched:** `_verify_permit` — **the sentinel branch only** (`:435-442`)

```
if permit_ref is NO_ALLOCATION:
    if manifest["allocating"]:
        raise PermitRefused(...)                      # unchanged, LA:436-442
    if before_doc != after_doc:                       # new
        differing = sorted(
            k for k in set(before_doc) | set(after_doc)
            if before_doc.get(k) != after_doc.get(k)
        )
        raise PermitRefused(
            f"NO_ALLOCATION was asserted, but this write MUTATES the ledger: top-level "
            f"key(s) {differing} differ from the pre-image. The sentinel asserts that "
            f"nothing changes, not merely that nothing is allocated. Obtain a permit for "
            f"the manifest above, or do not perform this write."
        )
    return None
```

The two documents must be passed in. Minimal signature change: `_verify_permit(permit_ref,
manifest, actor, ledger_path, *, before=None, after=None)`, with `commit()` (`:573`) and
nothing else supplying them — `_verify_permit` has exactly one caller.

- **Invariants affected:** makes `_NoAllocation`'s docstring claim (`:291-292`) true. The
  permit branch of `_verify_permit` is untouched.
- **Migration:** none.
- **Backward compatibility:** the sole production `NO_ALLOCATION` call site
  (`ukb.py:2380-2384`) passes a document equal to the pre-image (B.9), verified by execution.
- **Failure modes introduced:** one. Any future caller that uses `NO_ALLOCATION` for a
  non-allocating *mutation* is refused and must obtain a permit. That is the intended effect;
  it is listed because it changes what a future caller may do, not what any current caller
  does.
- **Verification:** reproduction test
  `test_no_allocation_does_not_authorize_a_non_allocating_mutation` (E.10); regression test
  `test_an_idempotent_no_op_is_still_accepted_under_no_allocation`.

## C.10 R-10 — E2-F5 · measure indirection, and correct the invariant's stated scope

**Files touched:** `00-MASTER/UCOS-UGA-001/uga_engine.py`;
`platform/tests/test_ledger_authority.py`
**Functions touched:** `_direct_ledger_writes` (`:1093-1120`); the `LEDGER-INV-01`
declaration text (`:1264-1272`); new module-level helper `_param_writing_functions`

Two additions to `_direct_ledger_writes`, both per-file and both AST-based:

1. `_param_writing_functions(tree)` → `{function_name: {(arg_index, sink), …}}` for every
   function whose body passes one of its **own formal parameters** to `open(…, 'w'|'a'|'x')`,
   `json.dump`, or `os.replace`.
2. For every `Call` in the module whose callee name is in that set, if the argument at
   `arg_index` renders (via `ast.unparse`) to a string matching the existing `_LEDGER_REF`
   pattern, report a violation naming file, line, callee and sink.

Prototype result at `77798202`: **0 violations across all tracked `.py` files**; a synthetic
`helper(LEDGER_PATH, "{}")` where `helper` writes its parameter is caught. `_param_writing_functions`
identifies `_dump_json` and `_write` in `ukb.py` and `_write_text` in `uga_engine.py`, and
neither is *called* with a ledger reference outside the authority — which is precisely why
current source is clean.

`why`-text correction at `:1264-1272`: state that the invariant measures *source-visible
write paths to the ledger, direct or one call deep*, and that what a `writer` does after
`commit()` hands it the path is enforced at runtime by the post-write comparison (`R-7`) —
so the declaration no longer implies a guarantee it does not provide.

Duplication decision: `platform/tests/test_ledger_authority.py:98-104` currently re-declares
the patterns. Rather than adding a second copy of the AST measurement, the test should
`sys.path.insert` `00-MASTER/UCOS-UGA-001` and import `_param_writing_functions` from
`uga_engine` — verified importable in 0.00 s with existing precedent at
`test_observation_universe.py:130`. *Alternative, if the cross-tree import is judged
undesirable: keep the duplication and add a test asserting the two implementations agree on a
fixture corpus. The single-implementation option is preferred because "a second implementation
of the measurement is a second scope" is the module's own stated principle (`LA:402-408`).*

- **Invariants affected:** `LEDGER-INV-01`'s violation set widens; its identifier, name,
  ownership and `fails_closed` status are unchanged.
- **Migration:** none.
- **Backward compatibility:** measured — zero new violations, so no gate flips.
- **Failure modes introduced:** two. (i) A `SyntaxError` in a scanned file must be a
  violation, not a skip, matching `:1112`'s existing treatment of unreadable source.
  (ii) The measurement is one call deep. A two-hop indirection (`a(p)` → `b(p)` → write) is
  not caught. Stated rather than papered over: the depth limit is a known bound, and the
  runtime control (`R-7`) is what does not have one.
- **Verification:** `test_the_guard_catches_an_indirect_ledger_write` (non-vacuity) and
  `test_the_guard_reports_no_violation_on_current_source` (non-regression), E.11.

## C.11 R-11 — E2-F6 · serializer round-trip equivalence

**Files touched:** `platform/tests/test_ledger_authority.py` only. **No production code.**
**Functions touched:** none

One test parametrised over three documents — `{}`, a synthetic ledger exercising all four
identity maps plus `history`, and the live `00-BOOK/DATA/id-ledger.json` (read-only) —
asserting:

```
assert json.loads(LA._canonical(doc)) == doc
assert json.loads(ukb_serialization(doc)) == doc
assert json.loads(uga_serialization(doc)) == doc
assert ukb_serialization(doc) == uga_serialization(doc)     # measured byte-identical
assert LA._canonical(doc) != ukb_serialization(doc) or doc == {}   # and _canonical is NOT
```

`ukb_serialization` / `uga_serialization` are obtained by importing `ukb` and `uga_engine`
(both verified importable) and writing to `tmp_path` via `_dump_json` / `_dump`, so the test
measures the real writers rather than a restatement of their arguments.

- **Invariants affected:** none. It pins the fact `R-7` depends on.
- **Migration / backward compatibility / failure modes:** none; test-only.
- **Verification:** the test is the verification. It must fail if any writer's `json.dumps`
  keyword arguments change in a way that breaks round-tripping — which is the regression it
  exists to catch, since `R-7` would then start refusing production writes.


---

# Section D — Dependency Ordering

## D.1 Edge derivation

Only edges that are *true implementation dependencies* are recorded. An edge exists iff
landing the successor before the predecessor either (a) cannot be written, (b) produces a
control whose correctness is unestablished, or (c) transiently widens what is accepted.

| Edge | Type | Derivation |
|---|---|---|
| `R-1 → R-2` | **(a) cannot be written correctly** | `R-2` refuses when the bytes at write time differ from the bytes verification used. Before `R-1`, `raw_before` (`LA:577-581`) is a *different read* than the one verification used (`LA:567`), so comparing against it closes MW-2 and leaves MW-1 — the window that contains the 15 s `git_head` fork and the permit-register open — wide open. `R-2` on top of `R-1` closes MW-1. **Hard.** |
| `R-9 → R-5a` | **(c) transient widening** | `R-5a` moves `{history-only change}` ∪ `{byte-identical no-op}` from REFUSED to ACCEPTED under `NO_ALLOCATION`. `R-9` removes the first disjunct. Landing `R-5a` first leaves a window in which a `history`-only mutation is accepted with no permit — a regression, however brief. **Hard.** |
| `R-5a ↔ R-5b` | **(c) atomic pair** | `R-5a` alone makes `history` erasure a non-allocating change; `R-5b` alone leaves the byte-identical no-op refused. Neither is safe alone. **Hard, bidirectional — one commit.** |
| `R-11 → R-7` | **(b) correctness unestablished** | `R-7` compares *documents*. That choice is correct only because all three serializers round-trip and the two production writers are byte-identical (CF-4). `R-11` is the measurement that pins it. Without `R-11`, `R-7` is a control whose soundness rests on an unmeasured assumption — exactly E2-F6's stated concern (*"if any future control binds bytes rather than the projection, three non-equivalent serializers become a correctness requirement with no test behind it"*). **Hard for correctness; soft for compilation.** |
| `R-3 → R-7ᵣ` | **(b) correctness unestablished** | `R-7`'s rollback (`_restore`) is safe only under exclusion; without the lock, a concurrent commit could land between `writer` and `_restore` and be silently reverted. The non-rollback fallback variant `R-7ₙ` has no such edge. **Hard for the rollback variant only.** |
| `R-7 → R-8ₑ` | **(b) subsumption** | `R-8`'s *enforcement* assertion is unreachable after `R-7` (proof in D.5), so landing it first would add an assertion whose non-vacuity cannot be demonstrated. `R-8`'s *rendering* half (`R-8ᵣ`) has no dependency. **Soft — ordering for demonstrability, not correctness.** |
| `R-7 → R-10ₜ` | **(b) the text asserts the successor** | `R-10`'s corrected `why` text states that writer behaviour is enforced at runtime. That statement is false until `R-7` lands. `R-10`'s AST measurement (`R-10ₐ`) has no dependency. **Hard for the text; none for the measurement.** |

**Edges deliberately NOT drawn**, with reasons, so absence is a finding rather than an
omission:

- `R-2 ↮ R-3` — complementary, not ordered. `R-3` empties the window for cooperating
  processes; `R-2` detects a non-cooperating writer. Either can land first.
- `R-4 ↮ R-9` — `R-4` covers the permit path, `R-9` the sentinel path. Disjoint.
- `R-6 ↮ anything` — the duplicate-identifier refusal reads only `after`.
- `R-5 ↮ R-4` — E1-F5 *masks* E1-F4's `NO_ALLOCATION`-path reproduction, but masking is a
  test-fixture concern (D.4), not an implementation dependency: `R-4`'s refusal fires on the
  permit path with or without `R-5`.
- **Nothing depends on E1-F3, E-3 or E-4A.** Checked exhaustively: no unit reads the permit
  register beyond `load_permit_register`'s existing call, no unit emits or consumes an audit
  event, and no unit requires a permit to exist. The twelve are implementable against a
  repository in which `00-BOOK/DATA/allocation-permits.json` never appears.

## D.2 The DAG

```
                        WAVE 0  (no predecessors — all six start in parallel)
   ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌───────┐  ┌───────┐  ┌───────┐
   │ R-1  │  │ R-3  │  │ R-4  │  │ R-6  │  │  R-9  │  │ R-10ₐ │  │ R-11  │
   │E1-F7 │  │E1-F2 │  │E1-F4 │  │E1-F6 │  │ E2-F4 │  │ E2-F5 │  │ E2-F6 │
   └──┬───┘  └──┬───┘  └──────┘  └──────┘  └───┬───┘  └───────┘  └───┬───┘
      │         │                              │                     │
      │         │        ┌─────────────────────┘                     │
      ▼         │        ▼                                           │
   ┌──────┐     │   ┌─────────────────┐                              │
   │ R-2  │     │   │ R-5a + R-5b     │   (one commit; atomic pair)   │
   │E1-F1 │     │   │     E1-F5       │                              │
   └──────┘     │   └─────────────────┘                              │
                │                                                    │
                └──────────────┬─────────────────────────────────────┘
                               ▼
                        ┌─────────────┐         WAVE 1
                        │  R-7        │
                        │ E2-F1,E2-F2 │
                        └──────┬──────┘
                               │
                    ┌──────────┴──────────┐        WAVE 2
                    ▼                     ▼
              ┌───────────┐         ┌───────────┐
              │  R-8ₑ     │         │  R-10ₜ    │
              │  E2-F3    │         │  E2-F5    │
              └───────────┘         └───────────┘

  R-8ᵣ (render bytes_changed) is Wave-0-eligible; grouped with R-8ₑ for one commit.
```

Acyclic by inspection: every edge points from a lower wave to a higher one, and the only
bidirectional relation (`R-5a ↔ R-5b`) is inside a single node.

## D.3 The three mandated determinations

**1. Which fixes can be applied independently?**

Seven nodes have no predecessor and may be applied in any order, individually, each
shippable and verifiable alone:

```
R-1 (E1-F7)   R-3 (E1-F2)   R-4 (E1-F4)   R-6 (E1-F6)
R-9 (E2-F4)   R-10ₐ (E2-F5 measurement)   R-11 (E2-F6)
```

Six of the twelve defects — E1-F2, E1-F4, E1-F6, E2-F4, E2-F6, and E1-F7 — are therefore
closable with no coordination whatsoever.

**2. Which fixes require prior fixes?**

| Successor | Requires | Strength |
|---|---|---|
| `R-2` (E1-F1) | `R-1` | hard |
| `R-5` (E1-F5) | `R-9` | hard |
| `R-7` (E2-F1, E2-F2) | `R-11`; `R-3` for the rollback variant | hard |
| `R-8ₑ` (E2-F3 enforcement) | `R-7` | soft (demonstrability) |
| `R-10ₜ` (E2-F5 text) | `R-7` | hard (the text asserts it) |

**3. Is any governance-independent fix blocked by another governance-independent fix?**

**Yes — five edges, four of them hard.** This is the answer the mandate asks for, stated
plainly: the twelve are *not* twelve independent work items. `R-2`, `R-5`, `R-7`, `R-8ₑ` and
`R-10ₜ` each wait on a governance-independent predecessor. No fix waits on a
governance-dependent one.

**One outbound constraint, recorded because it is the phase's most consequential sequencing
fact:**

> `R-5a` changes `unmeasured_maps` from `['history']` to `[]`, and therefore changes
> `manifest_digest` (`LA:316-336`) for **every** manifest measured against the production
> ledger. Today this invalidates nothing, because zero permits exist (CF-6, E-4A). If an
> issuance path is ever created before `R-5a` lands, every permit issued in between is
> invalidated the moment `R-5a` lands. **`R-5a` must precede any E-4A remediation.** This is
> a statement about digest arithmetic, not a recommendation about issuance.

## D.4 Test-fixture dependency, distinct from implementation dependency

E1-F5 **masks** the `NO_ALLOCATION`-path reproductions of E1-F4 and E2-F4 on any ledger
carrying `history` — including the production ledger. Executed here: E1-F4's reproduction on a
fixture *with* `history` raises `PermitRefused: … UNMEASURED_MAPS=['history']` before the
record-body rewrite is ever evaluated; on a `history`-free fixture it reproduces exactly as the
E1 report records. Consequence for Section E: the reproduction fixtures for E1-F4 and E2-F4
must either omit `history` or use the permit path. This is a fixture constraint, not a DAG
edge — `R-4` and `R-9` implement and verify correctly in either order relative to `R-5`.

## D.5 Derived result — `R-8`'s enforcement leg is unreachable after `R-7`

Not a design choice; a consequence, recorded so the assertion is understood as defence in
depth rather than as the control:

After `R-7`, `commit()` returns only if `json.loads(raw_after) == ledger`. Suppose
`bytes_changed` is `False`, i.e. `raw_after == raw_before`. Then
`json.loads(raw_before) == ledger`. After `R-1`, `before == json.loads(raw_before)`, so
`before == ledger`. `allocation_report(before, ledger, …)` over two equal documents yields
`allocated = {}`, `counter_advances = {}`, `cursor_advances = {}`, and — after `R-5a` —
`unmeasured_maps = []`, hence `allocating = False` (`LA:196-198`). Therefore
`allocating ∧ ¬bytes_changed` is unsatisfiable on any path that returns. The `raw_before is
None` case is excluded separately by `R-7`'s absent-file refusal.

The assertion is still specified, for two reasons: it fails loudly if `R-7` is ever weakened,
and its refusal message is the one an operator can act on.


---

# Section E — Verification Specification

## E.0 Harness, command, and the meaning of PASS / FAIL

**Home:** all tests extend `platform/tests/test_ledger_authority.py`. It is the existing home
of the chokepoint's tests, it already provides `_write`, `_writer` and `_issue`
(`:46-88`), and keeping one home is the module's own stated principle. Every test writes to
`tmp_path`; none can reach `00-BOOK/DATA/id-ledger.json`. The one test that reads the
production ledger (`E.12`) opens it read-only.

**Executable command** — verified working at `77798202` (40 tests, 0.80 s):

```bash
cd /Users/bipin/Desktop/UCOS-CONSOLIDATION
PYTHONPATH=. .ec1-venv/bin/pytest platform/tests/test_ledger_authority.py \
    -q -p no:cacheprovider --no-cov
```

`PYTHONPATH=.` is required — without it the repository's `engine.universal_discovery.pytest_scope`
plugin fails to import. `--no-cov` is required for a single-file run, since the project-wide
90 % coverage gate (`pyproject.toml`) otherwise reports failure on an unrelated denominator.

**Convention, stated once:**

- A **reproduction test** asserts the *fixed* behaviour. It therefore **FAILS before its unit
  lands and PASSES after**. Its pre-fix failure is the proof that the defect is live; its
  post-fix pass is the proof that the unit closed it.
- A **regression test** asserts behaviour that is correct **both** before and after, and must
  be green at every point. It is the guard that the unit did not overreach.

Two additional fixtures are needed beyond the existing ones:

```python
_HIST = {"UCOS-OBJ-000001": [{"seq": 1, "at": "t0", "content_hash": "h0"}]}

def _base(history: bool = True) -> dict:
    """A minimal ledger of the shape the production ledger actually has.

    `history` is a parameter, not a constant, because E1-F5 MASKS the
    NO_ALLOCATION-path reproductions of E1-F4 and E2-F4 on any ledger that
    carries it (see PHASE05 §D.4): the write is refused for UNMEASURED_MAPS
    before the defect under test is ever evaluated.
    """
    doc = {
        "version": 1,
        "category_seq": {"OBJ": 1},
        "by_object": {"a.py": {"universal_id": "UCOS-OBJ-000001",
                               "object_class": "TOOLING_OBJECT",
                               "first_seen": "commit:aaaa"}},
    }
    if history:
        doc["history"] = json.loads(json.dumps(_HIST))
    return doc

def _plus_one(base: dict) -> dict:
    after = json.loads(json.dumps(base))
    after["category_seq"]["OBJ"] = 2
    after["by_object"]["b.py"] = {"universal_id": "UCOS-OBJ-000002",
                                  "object_class": "TOOLING_OBJECT",
                                  "first_seen": "commit:bbbb"}
    return after
```

---

## E.1 R-1 · E1-F7 — the pre-image is read once

```python
def test_the_preimage_is_read_exactly_once_before_the_write(tmp_path, monkeypatch):
    """REGRESSION-shaped reproduction: today commit() opens the ledger three times."""
    base = _base(); path = _write(tmp_path, base); after = _plus_one(base)
    permit_id = _issue(path, after)
    opens: list[str] = []
    real_open = builtins.open

    def counting_open(file, *a, **kw):
        if str(file) == str(path):
            opens.append(kw.get("mode") or (a[0] if a else "r"))
        return real_open(file, *a, **kw)

    monkeypatch.setattr(builtins, "open", counting_open)
    LA.commit(path, after, actor="test", writer=_writer, permit=permit_id)
    reads = [m for m in opens if "r" in m and "+" not in m]
    assert len(reads) == 2, f"expected one pre-write and one post-write read, got {opens}"
```

- **Expected FAIL condition (pre-fix):** `len(reads) == 3` — `load_preimage` (`LA:567`),
  `raw_before` (`LA:577`), `raw_after` (`LA:585`).
- **Expected PASS condition (post-fix):** exactly two reads, and every existing test green.
- **Regression test:** the existing `test_an_unreadable_ledger_is_refused_not_treated_as_empty`
  and `test_a_missing_ledger_is_a_legitimate_first_mint` must stay green — they pin E1-S2 and
  E1-S4, the two behaviours `read_preimage_bytes` must preserve.

## E.2 R-2 · E1-F1 — a concurrent write inside the window is refused

```python
def test_a_concurrent_write_inside_the_verification_window_is_refused(tmp_path, monkeypatch):
    """The E1-F1 probe, verbatim in shape: inject at the git_head subprocess."""
    base = _base(); path = _write(tmp_path, base); after = _plus_one(base)
    permit_id = _issue(path, after)
    real_git_head, fired = LA.git_head, []

    def hijack(near):
        if not fired:                                   # the concurrent actor, inside MW-1
            fired.append(1)
            rival = json.loads(json.dumps(base))
            rival["category_seq"]["OBJ"] = 2
            rival["by_object"]["z.py"] = {"universal_id": "UCOS-OBJ-000002",
                                          "object_class": "TOOLING_OBJECT",
                                          "first_seen": "commit:zzzz"}
            _writer(path, rival)
        return real_git_head(near)

    monkeypatch.setattr(LA, "git_head", hijack)
    with pytest.raises(LA.LedgerWriteRefused, match="changed between verification and write"):
        LA.commit(path, after, actor="test", writer=_writer, permit=permit_id)
    on_disk = json.loads(Path(path).read_text(encoding="utf-8"))
    assert "z.py" in on_disk["by_object"], "the rival's permanent identifier was destroyed"
```

- **Expected FAIL condition (pre-fix):** no exception; `z.py` absent from disk. Reproduced in
  `PHASE0-E1-ATOMICITY-REPORT.md` §2 (`['a.py', 'b.py']`).
- **Expected PASS condition (post-fix):** `LedgerWriteRefused` raised **and** `z.py` still on
  disk — both legs required, because a refusal that still clobbered the file would be no fix.
- **Regression test:** `test_a_single_writer_is_unaffected_by_the_recheck` — the ordinary
  happy path (`test_an_allocation_can_never_be_reported_as_nothing`) must stay green, proving
  the re-read does not refuse when nothing else touched the file.

## E.3 R-3 · E1-F2 — two commits cannot interleave

```python
def test_two_commits_cannot_interleave(tmp_path):
    """Real mutual exclusion, measured across processes rather than argued."""
    base = _base(); path = _write(tmp_path, base)
    marker = tmp_path / "order.log"
    script = textwrap.dedent(f"""
        import sys, json, time, pathlib
        sys.path.insert(0, {str(TOOLS)!r})
        import ledger_authority as LA
        path, marker, tag = {str(path)!r}, {str(marker)!r}, sys.argv[1]
        def writer(p, o):
            pathlib.Path(marker).open("a").write(tag + "-enter\\n")
            time.sleep(0.5)
            pathlib.Path(p).write_text(json.dumps(o, indent=2) + "\\n", encoding="utf-8")
            pathlib.Path(marker).open("a").write(tag + "-exit\\n")
        LA.commit(path, json.load(open(path)), actor="test",
                  writer=writer, permit=LA.NO_ALLOCATION)
    """)
    procs = [subprocess.Popen([sys.executable, "-c", script, tag]) for tag in ("A", "B")]
    for p in procs:
        p.wait(timeout=60)
    order = marker.read_text().split()
    assert order in (["A-enter", "A-exit", "B-enter", "B-exit"],
                     ["B-enter", "B-exit", "A-enter", "A-exit"]), \
        f"the two commits interleaved: {order}"
```

- **Expected FAIL condition (pre-fix):** `['A-enter', 'B-enter', …]` — interleaved.
- **Expected PASS condition (post-fix):** one commit's `enter`/`exit` pair completes before
  the other's `enter`.
- **Prerequisite:** this test needs `R-5a` + `R-9` for its `NO_ALLOCATION` no-op to be
  accepted on a `history`-bearing fixture, **or** it uses `_base(history=False)`. Use the
  latter so `R-3` remains independently verifiable (D.3).
- **Regression test:** `test_a_lock_timeout_refuses_rather_than_proceeding` — hold the
  directory lock in the test process, call `commit()` with a short timeout, assert
  `LedgerWriteRefused` naming the timeout and the file byte-unchanged.

## E.4 R-4 · E1-F4 — a record body rewrite is refused

```python
def test_a_record_body_rewrite_is_refused(tmp_path):
    base = _base(history=False)                    # §D.4: E1-F5 masks this on the real shape
    path = _write(tmp_path, base)
    forged = json.loads(json.dumps(base))
    forged["by_object"]["a.py"]["object_class"] = "GOVERNANCE_OBJECT"
    forged["by_object"]["a.py"]["first_seen"] = "commit:FORGED"
    with pytest.raises(LA.LedgerWriteRefused, match="REWRITTEN"):
        LA.commit(path, forged, actor="test", writer=_writer, permit=LA.NO_ALLOCATION)
    assert json.loads(Path(path).read_text())["by_object"]["a.py"]["object_class"] \
        == "TOOLING_OBJECT"
```

- **Expected FAIL condition (pre-fix):** accepted with `allocating=False
  authorization=NO_ALLOCATION`; disk holds `GOVERNANCE_OBJECT` / `commit:FORGED`. Confirmed by
  execution here.
- **Expected PASS condition (post-fix):** `LedgerWriteRefused` matching `REWRITTEN`, naming
  the changed fields, and the file byte-unchanged.
- **Regression test:** `test_a_new_records_body_is_unconstrained` — allocating a *new* key
  with any record body is accepted, so the refusal is scoped to *existing* records only.

## E.5 R-5 · E1-F5 — classification and prefix preservation

```python
def test_a_byte_identical_write_allocates_nothing_on_a_ledger_with_history(tmp_path):
    """(a) The production shape. Today this reports allocating=True for UNMEASURED_MAPS."""
    base = _base()                                       # carries `history`
    path = _write(tmp_path, base)
    report = LA.commit(path, json.loads(json.dumps(base)), actor="test",
                       writer=_writer, permit=LA.NO_ALLOCATION)
    assert report["unmeasured_maps"] == []
    assert report["allocating"] is False
    assert report["bytes_changed"] is False


def test_history_erasure_is_refused(tmp_path):
    """(b) The append-only property ukb.record_snapshots claims and nothing enforced."""
    base = _base(); path = _write(tmp_path, base)
    erased = json.loads(json.dumps(base)); erased["history"] = {}
    with pytest.raises(LA.LedgerWriteRefused, match="history"):
        LA.commit(path, erased, actor="test", writer=_writer, permit=_issue(path, erased))
    assert json.loads(Path(path).read_text())["history"] == _HIST


def test_a_shortened_history_list_is_refused(tmp_path):
    base = _base()
    base["history"]["UCOS-OBJ-000001"].append({"seq": 2, "at": "t1", "content_hash": "h1"})
    path = _write(tmp_path, base)
    truncated = json.loads(json.dumps(base))
    truncated["history"]["UCOS-OBJ-000001"] = truncated["history"]["UCOS-OBJ-000001"][:1]
    with pytest.raises(LA.LedgerWriteRefused, match="not an extension"):
        LA.commit(path, truncated, actor="test", writer=_writer, permit=LA.NO_ALLOCATION)
```

- **Expected FAIL conditions (pre-fix):** (a) `unmeasured_maps == ['history']`,
  `allocating is True`, and the call raises `PermitRefused` before reaching the assertions —
  confirmed by execution against the live ledger. (b) accepted; disk `history == {}`.
- **Expected PASS conditions (post-fix):** as asserted. For `test_history_erasure_is_refused`,
  note the permit path is used deliberately — the refusal must fire regardless of
  authorization mode.
- **Regression tests:** `test_a_history_append_is_accepted_under_a_permit` (the real
  `ukb build --mint` shape: `history` grows, nothing else moves, a permit authorizes it) and
  `test_an_idempotent_no_op_is_still_accepted_under_no_allocation` (shared with E.10).

## E.6 R-6 · E1-F6 — duplicate identifiers, and the MW-3 legs

```python
@pytest.mark.parametrize("second_map", ["by_object", "by_observation"])
def test_a_duplicate_identifier_is_refused(tmp_path, second_map):
    """Within a map and across maps: the four share one category_seq counter."""
    base = _base(history=False); path = _write(tmp_path, base)
    collide = json.loads(json.dumps(base))
    if second_map == "by_object":
        collide["by_object"]["c.py"] = {"universal_id": "UCOS-OBJ-000001",
                                        "object_class": "TOOLING_OBJECT",
                                        "first_seen": "commit:ccc"}
    else:
        collide["by_observation"] = {"k": {"observation_id": "UCOS-OBJ-000001",
                                           "observer": "o", "subject": "s",
                                           "kind": "K", "first_seen": "t"}}
    with pytest.raises(LA.LedgerWriteRefused, match="bound to BOTH"):
        LA.commit(path, collide, actor="test", writer=_writer,
                  permit=_issue(path, collide))


def test_the_mw3_interleaving_is_refused_by_two_independent_legs(tmp_path):
    """E1-F6's UNVERIFIABLE window, made verifiable: name which leg refuses.

    Leg 1 — key removal: the rival's key is missing from the late proposal.
    Leg 2 — duplicate identifier: the same identifier bound to two keys.
    Asserting BOTH is the point; today only leg 1 fires, so the property rests
    on a single check.
    """
    base = _base(history=False); path = _write(tmp_path, base)
    late = _plus_one(base)                          # computed against base: b.py -> …002
    rival = _plus_one(base)                         # the rival allocated …002 to z.py
    rival["by_object"]["z.py"] = rival["by_object"].pop("b.py")
    _writer(path, rival)                            # the rival's bytes land first
    with pytest.raises(LA.LedgerWriteRefused) as exc:
        LA.commit(path, late, actor="test", writer=_writer, permit=LA.NO_ALLOCATION)
    assert "REMOVED" in str(exc.value)              # leg 1, present today

    merged = json.loads(json.dumps(rival))          # a proposal that preserves the key
    merged["by_object"]["b.py"] = {"universal_id": "UCOS-OBJ-000002",
                                   "object_class": "TOOLING_OBJECT",
                                   "first_seen": "commit:bbbb"}
    with pytest.raises(LA.LedgerWriteRefused, match="bound to BOTH"):
        LA.commit(path, merged, actor="test", writer=_writer,
                  permit=_issue(path, merged))      # leg 2, absent today
```

- **Expected FAIL condition (pre-fix):** the collision is **accepted**. Confirmed by
  execution: `allocated={'by_object': ['UCOS-OBJ-000002']}` and disk holds
  `{'a.py': …001, 'b.py': …002, 'c.py': …002}`.
- **Expected PASS condition (post-fix):** both parametrisations refuse with
  `bound to BOTH`, and the second half of the MW-3 test refuses on leg 2 rather than leg 1.
- **Regression test:** `test_the_live_ledger_has_no_duplicate_identifiers` — reads
  `00-BOOK/DATA/id-ledger.json` read-only and asserts uniqueness within each map and across
  the union. This is the backward-compatibility guard: it is green today (measured: 1628 +
  5374 + 0 + 7 identifiers, zero duplicates) and must stay green.

## E.7 R-7 · E2-F1 — a divergent writer is refused

```python
def test_a_divergent_writer_is_refused(tmp_path):
    base = _base(); path = _write(tmp_path, base); after = _plus_one(base)
    permit_id = _issue(path, after)
    original = Path(path).read_bytes()

    def divergent(p, obj):
        forged = json.loads(json.dumps(obj))
        forged["by_object"]["b.py"]["universal_id"] = "UCOS-OBJ-999999"
        forged["by_object"]["EXTRA.py"] = {"universal_id": "UCOS-OBJ-000003",
                                           "object_class": "TOOLING_OBJECT",
                                           "first_seen": "commit:xxx"}
        forged["category_seq"]["OBJ"] = 3
        _writer(p, forged)

    with pytest.raises(LA.LedgerWriteRefused, match="not the authorized document"):
        LA.commit(path, after, actor="test", writer=divergent, permit=permit_id)
    assert Path(path).read_bytes() == original, "the pre-image was not restored"
```

- **Expected FAIL condition (pre-fix):** accepted with `authorization='PERMIT'` and
  `allocated={'by_object': ['UCOS-OBJ-000002']}`, while disk holds three identifiers
  (`['EXTRA.py', 'a.py', 'b.py']`, with `b.py → UCOS-OBJ-999999`). Confirmed by execution.
- **Expected PASS condition (post-fix):** refusal **and** byte-for-byte restoration. If the
  non-rollback fallback variant `R-7ₙ` is chosen instead, drop the second assertion and
  replace it with `assert Path(path).read_bytes() != original` plus an explicit comment that
  detection without restoration is the accepted tradeoff — so the choice is visible in the
  test rather than only in this document.
- **Regression test:** `test_both_production_writers_satisfy_the_post_write_check` —
  parametrised over `ukb._dump_json` and `uga_engine._dump`, asserting a real allocation lands
  and is accepted. This is the guard that `R-7` did not break production.

## E.8 R-7 · E2-F2 — a silent writer is refused

```python
def test_a_silent_writer_is_refused(tmp_path):
    base = _base(); path = _write(tmp_path, base); after = _plus_one(base)
    permit_id = _issue(path, after)
    original = Path(path).read_bytes()
    with pytest.raises(LA.LedgerWriteRefused):
        LA.commit(path, after, actor="test", writer=lambda p, o: None, permit=permit_id)
    assert Path(path).read_bytes() == original


def test_a_writer_that_removes_the_file_is_refused(tmp_path):
    base = _base(); path = _write(tmp_path, base); after = _plus_one(base)
    permit_id = _issue(path, after)
    with pytest.raises(LA.LedgerWriteRefused, match="persisted nothing"):
        LA.commit(path, after, actor="test", writer=lambda p, o: os.remove(p),
                  permit=permit_id)
    assert Path(path).exists(), "the pre-image was not restored"
```

- **Expected FAIL condition (pre-fix):** `report` returns
  `allocating=True total_allocations=1 bytes_changed=False` and the operator line reads
  `identity ledger ALLOCATED 1 permanent identifier(s) [by_object+1] …` while disk is
  unchanged. Confirmed by execution.
- **Expected PASS condition (post-fix):** both refuse; the file exists and equals the
  pre-image.

## E.9 R-8 · E2-F3 — enforce and render `bytes_changed`

```python
def test_the_operator_line_shows_whether_the_file_moved(tmp_path):
    base = _base(); path = _write(tmp_path, base); after = _plus_one(base)
    report = LA.commit(path, after, actor="test", writer=_writer,
                       permit=_issue(path, after))
    assert "bytes_changed=True" in LA.format_report(report)


def test_plan_output_still_renders_without_a_bytes_changed_field(tmp_path):
    """CF-1: format_report is also called on plan() output and inside a refusal message."""
    base = _base(); path = _write(tmp_path, base); after = _plus_one(base)
    manifest = LA.plan(path, after, actor="test")
    assert "bytes_changed" not in manifest
    line = LA.format_report(manifest)               # must not raise KeyError
    assert "ALLOCATED 1" in line and "bytes_changed" not in line


def test_an_allocation_that_did_not_move_the_file_is_refused(tmp_path):
    """Defence in depth: after R-7 this state is unreachable (PHASE05 §D.5).

    Constructed by monkeypatching the post-write read so the two byte reads agree
    while the persisted document still equals `ledger` — i.e. by defeating R-7's
    comparison specifically, which is what makes the assertion non-vacuous.
    """
```

- **Expected FAIL condition (pre-fix):** `format_report` output contains no `bytes_changed`
  token (confirmed by execution), and the contradiction is returned without error.
- **Expected PASS condition (post-fix):** the token appears whenever the field exists, never
  when it does not, and the contradiction refuses.
- **Regression test:** existing `test_a_genuine_no_op_is_still_reported_as_no_allocation`
  (`:212-219`), `test_an_allocation_can_never_be_reported_as_nothing` (`:183-210`) and
  `test_an_unknown_identity_map_is_surfaced_rather_than_counted_as_zero` (`:242-257`) must all
  stay green — they assert substrings of the line that an appended token cannot break.

## E.10 R-9 · E2-F4 — `NO_ALLOCATION` permits nothing, not merely no allocation

```python
@pytest.mark.parametrize(("key", "value"), [("version", 99),
                                            ("discovered_volumes", {"VOL-666": 1})])
def test_no_allocation_does_not_authorize_a_non_allocating_mutation(tmp_path, key, value):
    base = _base(history=False)                     # §D.4
    path = _write(tmp_path, base)
    mutated = json.loads(json.dumps(base)); mutated[key] = value
    with pytest.raises(LA.PermitRefused, match="MUTATES"):
        LA.commit(path, mutated, actor="test", writer=_writer, permit=LA.NO_ALLOCATION)
    assert json.loads(Path(path).read_text()).get(key) != value


def test_an_idempotent_no_op_is_still_accepted_under_no_allocation(tmp_path):
    """The one real production case: ukb.py:2380-2384's idempotent exec re-declare.

    allocate_execution early-returns on an existing key (ukb.py:2249-2251) and
    _exec_declare mutates the ledger nowhere else, so `ledger` equals the pre-image.
    """
    base = _base(history=False)
    base["by_execution"] = {"k": {"execution_id": "UCOS-EXE-000001", "first_seen": "t"}}
    path = _write(tmp_path, base)
    report = LA.commit(path, json.loads(json.dumps(base)), actor="test",
                       writer=_writer, permit=LA.NO_ALLOCATION)
    assert report["allocating"] is False
    assert report["authorization"] == "NO_ALLOCATION"
    assert report["bytes_changed"] is False
```

- **Expected FAIL condition (pre-fix):** accepted with `allocating=False
  authorization=NO_ALLOCATION bytes_changed=True`; disk holds `version=99` /
  `discovered_volumes={'VOL-666': 1}`. Confirmed by execution.
- **Expected PASS condition (post-fix):** `PermitRefused` naming the differing top-level keys,
  file byte-unchanged, and the idempotent no-op still accepted.
- **Regression test:** the existing `test_a_false_no_allocation_claim_is_refused`
  (`:382-392`) must stay green — `R-9` adds a second refusal to that branch without removing
  the first.

## E.11 R-10 · E2-F5 — the invariant sees indirection

```python
def test_the_guard_catches_an_indirect_ledger_write(tmp_path):
    """Non-vacuity for the AST leg. The lexical patterns miss this shape entirely."""
    src = textwrap.dedent('''
        LEDGER_PATH = "00-BOOK/DATA/id-ledger.json"
        def helper(p, obj):
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(obj)
        def go():
            helper(LEDGER_PATH, "{}")
    ''')
    assert U.indirect_ledger_writes_in_source(src), "the AST guard is blind to indirection"
    assert not any(U._PY_LEDGER_WRITE.search(l) or U._PY_LEDGER_OPEN.search(l)
                   for l in src.splitlines()), "the lexical guard already covered this"


def test_the_guard_reports_no_violation_on_current_source():
    """Non-regression. Measured at 77798202: 0 indirect writes in tracked .py source."""
    st = U.build(mint=False)
    inv = {i["id"]: i for i in st["invariants"]}["LEDGER-INV-01"]
    indirect = [v for v in inv["violations"] if "writes param" in v]
    assert indirect == [], f"new indirection violations: {indirect}"
```

- **Expected FAIL condition (pre-fix):** `U.indirect_ledger_writes_in_source` does not exist
  (`AttributeError`) — the measurement is absent.
- **Expected PASS condition (post-fix):** the synthetic indirection is caught, the lexical
  patterns are confirmed blind to it (so the new leg is doing real work), and current source
  reports zero indirect violations.
- **Cost note:** `U.build(mint=False)` performs the full discovery pass (~60 s measured). Mark
  the non-regression test `@pytest.mark.slow` or call `_direct_ledger_writes` directly on a
  `git ls-files`-derived entry list, which the prototype did in under a second.
- **Regression test:** existing `test_the_authority_is_the_only_ledger_writer` (`:118-146`),
  `test_the_structural_guard_actually_matches_a_direct_write` (`:161-172`) and
  `test_the_guard_does_not_confuse_the_change_ledger_for_the_identity_ledger` (`:174-177`)
  must stay green. The third is the important one: broadening the measurement must not start
  matching `CHANGE_LEDGER_PATH`.

## E.12 R-11 · E2-F6 — serializer round-trip equivalence

```python
@pytest.mark.parametrize("doc_name", ["empty", "synthetic", "production"])
def test_the_three_serializers_round_trip_to_the_same_document(tmp_path, doc_name):
    doc = {"empty": {},
           "synthetic": _full_shape_fixture(),      # all four maps + history + counters
           "production": json.loads(
               (REPO / "00-BOOK" / "DATA" / "id-ledger.json").read_text(encoding="utf-8"))
           }[doc_name]

    assert json.loads(LA._canonical(doc)) == doc

    ukb_path, uga_path = tmp_path / "u.json", tmp_path / "g.json"
    ukb._dump_json(str(ukb_path), doc)
    uga_engine._dump(str(uga_path), doc)
    ukb_bytes, uga_bytes = ukb_path.read_bytes(), uga_path.read_bytes()

    assert json.loads(ukb_bytes) == doc, "ukb._dump_json does not round-trip"
    assert json.loads(uga_bytes) == doc, "uga_engine._dump does not round-trip"
    assert ukb_bytes == uga_bytes, "the two production writers diverged at byte level"
    if doc:
        assert LA._canonical(doc).encode() != ukb_bytes, \
            "_canonical is expected to differ at byte level; a byte-level post-write " \
            "comparison would therefore be wrong (see PHASE05 §C.0 CF-4)"
```

- **Expected FAIL condition:** any serializer stops round-tripping, or the two production
  writers diverge at byte level. Neither holds today — measured on the live ledger:
  `ukb` and `uga` both 2 274 511 bytes and byte-identical; `_canonical` 1 786 167 bytes; all
  three parse back equal.
- **Expected PASS condition:** all four assertions, for all three documents.
- **Read-only guarantee:** the production ledger is opened with `read_text`; the two writes go
  to `tmp_path`.
- **This test is `R-7`'s premise.** If it ever fails, `R-7` will begin refusing production
  writes, and this test is what will say why.

## E.13 Verification matrix

| Defect | Unit | Reproduction test | Currently | Regression guard |
|---|---|---|---|---|
| E1-F1 | R-2 | `E.2` concurrent write in window | FAILS (accepted, rival destroyed) | happy path unaffected by the re-check |
| E1-F2 | R-3 | `E.3` two commits interleave | FAILS (interleaved) | lock timeout refuses, file unchanged |
| E1-F4 | R-4 | `E.4` record body rewrite | FAILS (accepted under NO_ALLOCATION) | new record's body unconstrained |
| E1-F5 | R-5 | `E.5` ×3 | FAILS (allocating=True; erasure accepted) | history append under a permit accepted |
| E1-F6 | R-6 | `E.6` ×3 | FAILS (collision accepted, lands on disk) | live ledger has zero duplicates |
| E1-F7 | R-1 | `E.1` read count | FAILS (3 reads) | E1-S2 and E1-S4 preserved |
| E2-F1 | R-7 | `E.7` divergent writer | FAILS (accepted, 3 ids on disk) | both production writers accepted |
| E2-F2 | R-7 | `E.8` ×2 silent writer | FAILS (reports 1 allocation, disk unchanged) | shared with E.7 |
| E2-F3 | R-8 | `E.9` ×3 | FAILS (no token, contradiction returned) | 3 existing line-substring tests green |
| E2-F4 | R-9 | `E.10` ×2 | FAILS (version/volumes rewritten) | idempotent no-op still accepted |
| E2-F5 | R-10 | `E.11` ×2 | FAILS (`AttributeError` — no measurement) | change-ledger not confused for identity ledger |
| E2-F6 | R-11 | `E.12` ×3 | FAILS (test does not exist) | is itself the guard |

Every row's "Currently" column was established by execution against the unmodified authority
at `77798202`, not by reading. Transcripts in §G.


---

# Section F — Closure Determination

Every number below is derived from `PHASE0-GOVERNANCE-INDEPENDENT-DETERMINATION.md` §6 plus
the executed measurements in this document. Nothing is estimated.

## F.1 Current blocker count

Carried forward unchanged from `PHASE0-GOVERNANCE-INDEPENDENT-DETERMINATION.md` §6.1, and
re-verified here in the sense that all twelve in-scope defects were re-confirmed live by
execution (§G) — none dissolved on re-examination:

| Work item | Blockers | Composition |
|---|---|---|
| E-1 | 7 | E1-F1…F7 — 6 UNSAFE + 1 UNVERIFIABLE |
| E-2 | 7 | E2-F1…F7 — 6 UNSAFE + 1 UNPROVEN; E2-F7 is a dependency statement about E-4A, carried inside E-2's seven for traceability |
| E-3 | 1 | TAUTOLOGY |
| E-4A | 1 | 4 of 5 operations MISSING; counted once |
| **Total** | **15** | |

```
CURRENT BLOCKER COUNT ............................... 15
```

## F.2 Blocker count after applying all governance-independent fixes

The twelve in scope, each mapped to the unit that closes it and to the executed evidence that
the unit converts the reproduction from ACCEPTED to REFUSED:

| # | Defect | Unit | Closed by | Prototype outcome (§G) |
|---|---|---|---|---|
| 1 | E1-F1 | R-2 | pre-write byte comparison | REFUSED — *ledger changed between verification and write* |
| 2 | E1-F2 | R-3 | directory-fd `flock` | second process BLOCKED under `LOCK_EX\|LOCK_NB` |
| 3 | E1-F4 | R-4 | record-body refusal | REFUSED — *record body of 'a.py' would be REWRITTEN* |
| 4 | E1-F5 | R-5a+R-5b | classify + prefix refusal | (a) no-op ACCEPTED with `unmeasured_maps=[]`; (b) erasure REFUSED |
| 5 | E1-F6 | R-6 | duplicate-identifier refusal | collision ACCEPTED today; refusal prototyped and live ledger clean |
| 6 | E1-F7 | R-1 | single read | read count 3 → 2 |
| 7 | E2-F1 | R-7 | post-write document compare | REFUSED — *persisted document != authorized document* |
| 8 | E2-F2 | R-7 | same | REFUSED — same predicate |
| 9 | E2-F3 | R-8 | render + assert | contradiction becomes unreachable (D.5); token rendered |
| 10 | E2-F4 | R-9 | `NO_ALLOCATION` ⇒ document unchanged | REFUSED — *document differs from the pre-image* |
| 11 | E2-F5 | R-10 | AST indirection measurement | synthetic indirection CAUGHT; 0 false positives on current source |
| 12 | E2-F6 | R-11 | round-trip test | all three serializers round-trip; two writers byte-identical |

```
BLOCKER COUNT AFTER ALL GOVERNANCE-INDEPENDENT FIXES ... 3
    15 current  −  12 closed  =  3
```

Every one of the twelve is closable with no answer to FD-1…FD-5, no new authority, no mutation
definition, no audit definition and no permit issuance semantics — proved per defect in
Section B and demonstrated mechanically in §G.

## F.3 Remaining governance-dependent blockers

```
REMAINING BLOCKERS ................................... 3
    E1-F3   permit replay after ledger restore
    E-3     UGA-INV-10 tautology
    E-4A    no permit issuance path
```

Each was excluded by Phase 0 and each exclusion is re-confirmed rather than re-litigated:

| Blocker | Governance root its remedy requires | Why no part of it is severable into this phase |
|---|---|---|
| E1-F3 | issuance semantics | Recording *use* of an authorization requires deciding whether an authorization is single-use. Nothing in this phase's twelve units records, marks or consumes a permit; `_verify_permit` is byte-for-byte unchanged. `single_use` is named in the register shape (`PHASE0-E4A-ISSUANCE-PATH-REPORT.md:35`) and written by the test fixture (`test_ledger_authority.py:82`), and the string appears nowhere in `ledger_authority.py`. |
| E-3 | domain rules — what a mutation is, what an audit event must contain | Confirmed unimproved by this phase: no unit emits an audit event, so E-3 counterexample **C6** (*"every `ledger_authority.commit()` call"* passes `UGA-INV-10` unaudited) holds identically after all twelve fixes. `audited ≡ set(by_object.keys())` is untouched. |
| E-4A | issuance semantics, issuer identity, temporal legitimacy | The register still has no producer after all twelve units. `permit=None` is still refused at `LA:448-451`, so `register.sh:216` still cannot complete Phase 1. |

**The irreducible governance-dependent core is 3, and this phase does not reduce it.** It is
also worth stating what the 12 → 0 reduction does *not* buy: because E-4A still blocks every
production write, applying all twelve units leaves the production write path exactly as
unreachable as it is today. The twelve fixes make a path safe; they do not open it.

## F.4 Newly exposed defects, and what becomes visible once E-4A is resolved

E2-F7 records the mechanism: `permit` is mandatory with no default (`LA:546`) and the register
is absent, so *no production write reaches `writer`*. Supplying any issuance path activates
E1-F1, E1-F2, E1-F4, E1-F5, E1-F7, E2-F1, E2-F2, E2-F3 and E2-F4 **simultaneously** — nine of
the twelve are latent-not-absent today. Applying the twelve units before any E-4A remediation
is therefore the ordering under which E-4A's resolution exposes nothing. That is a derived
consequence of `permit`'s mandatory status, not sequencing advice.

Four items were **derived in this phase and are not in the Phase-0 set**. Each is recorded with
its evidence and its class. None is remediated here.

### RES-1 — a permit binds a projection, not the document *(new; would survive all twelve fixes)*

After `R-7`, the persisted document equals the document `commit()` was handed. The document
`commit()` was handed still is not the object the permit approved: `manifest_digest`
(`LA:316-336`) covers six fields derived from `_identifier_index` (`LA:112-119`). After the
twelve fixes, the following remain unauthorized-but-permitted under a valid permit:

- the record **body** of a *newly* allocated identity (`R-4` freezes existing records only);
- the **content** of `history` appends (`R-5b` constrains the prefix, not the appended values);
- the **values** of `version` and `discovered_volumes` (in `NON_ALLOCATION_KEYS`).

Concretely: two different `history`-only appends against the same pre-image produce the same
`manifest_digest`, so a permit issued for one authorizes the other.

- **Evidence:** `manifest_digest`'s field list (`LA:322-331`); `_identifier_index` (`LA:112-119`);
  `NON_ALLOCATION_KEYS` (`LA:83-85`); E-2 report §5 reason 2 (*"no digest of the document, or of
  the intended file content, exists anywhere in the system"*).
- **Class:** the remedy — widening `manifest_digest` — changes what a permit **binds**, i.e.
  what an issuer must transcribe from `plan()`. Constraint 3 forbids introducing permit
  semantics, and changing the content of a permit binding is the safest reading of that
  prohibition. **GOVERNANCE-DEPENDENT for remedy; out of scope here.**
- **Visibility:** becomes exercisable the moment E-4A supplies an issuance path.

### RES-2 — `_verify_permit` does not refuse an empty-manifest permit *(new)*

`_NoAllocation`'s docstring (`LA:287`) states that *"a permit for an empty manifest would
authorize nothing and must not be issuable."* `_verify_permit` implements no such refusal: a
permit whose `manifest_digest` is the digest of an all-empty manifest verifies normally. This
is the mechanism by which `history`-only appends remain authorizable after `R-5a`+`R-9` (which
is why the specification relies on it — see B.4), and it is simultaneously a claim in source
that the code does not honour.

- **Evidence:** `LA:432-543` contains no test of `manifest["total_allocations"]` or
  `manifest["allocating"]` on the permit branch; the sentinel branch (`:435-442`) is the only
  place either is read.
- **Class:** refusing a class of permit is a permit rule. **GOVERNANCE-DEPENDENT.**
- **Note:** this phase *depends* on the current permissive behaviour. If a future phase makes
  empty-manifest permits unissuable, `history`-only appends lose their authorization path and
  `R-5`'s design must be revisited. Recorded here so that coupling is not discovered later.

### RES-3 — MW-3 is bounded, not closed *(scope clarification, not a new defect)*

The caller's own ledger read (`uga_engine.py:1700`) precedes `commit()`, so `R-3`'s lock cannot
span it. After `R-6`, MW-3 is covered by two independent refusals — key removal (`LA:135-139`)
and duplicate identifier — which is what E1-F6's UNVERIFIABLE classification asked for
(*"needs a test, not a decision"*). The window itself persists. **Not a blocker; a documented
bound.** Closing it entirely would require moving the caller's read inside the lock, i.e.
restructuring `uga_engine.build`'s 60-second discovery pass to run under exclusion — a
performance and architecture change well beyond this authorization, and governance-independent
if ever undertaken.

### RES-4 — `flock` is advisory and filesystem-dependent *(residual risk of R-3)*

Verified working on this platform (macOS/APFS). On a filesystem that does not honour `flock`,
`R-3` silently degrades to no protection and `R-2` is the sole remaining detector. **Not a
blocker; a stated environmental dependency**, recorded because a control that can silently
become a no-op should be documented as such rather than assumed.

## F.5 Closure ledger

```
TOTAL BLOCKERS IN SECTION E SCOPE ..................... 15

  Governance-INDEPENDENT, specified for implementation .. 12
      E1-F1  E1-F2  E1-F4  E1-F5  E1-F6  E1-F7
      E2-F1  E2-F2  E2-F3  E2-F4  E2-F5  E2-F6
      -> 11 change units, R-1 … R-11
      -> 7 units have no predecessor; 5 wait on another governance-independent unit
      -> 0 units wait on a governance-dependent blocker

  Governance-DEPENDENT, unchanged ........................ 3
      E1-F3   E-3   E-4A

  BLOCKERS AFTER APPLYING ALL 12 ......................... 3
  RESOLVED BY THIS PHASE ................................. 0   (specification only)

  DERIVED THIS PHASE, not in the Phase-0 set ............. 4
      RES-1  permit binds a projection, not the document   -> GOVERNANCE-DEPENDENT
      RES-2  empty-manifest permits are not refused        -> GOVERNANCE-DEPENDENT
      RES-3  MW-3 bounded by two refusals, not closed      -> bound, not a blocker
      RES-4  flock is advisory and fs-dependent            -> environmental, not a blocker

  IRREDUCIBLE GOVERNANCE-DEPENDENT CORE .................. 3, plus RES-1 and RES-2
                                                            once E-4A is resolved
```

**Answer to the closure question.** The remaining blocker set after the twelve
governance-independent fixes is `{E1-F3, E-3, E-4A}` — three blockers, each of whose remedy
requires an answer to a governance root that Constraint 2 forbids approaching. It is the
irreducible core **for the defect set Phase 0 enumerated**. It is *not* the whole irreducible
core of the system: `RES-1` and `RES-2` are governance-dependent residues that Phase 0 did not
enumerate and that this phase derived from the same evidence. Stating the count as exactly
three without them would be the more comfortable answer and the less accurate one.

## F.6 Success criteria, discharged

| Criterion | Status |
|---|---|
| Implementation may begin without answering any governance question | **MET** — every unit's refusal predicate is a function of `(before, ledger, persisted_bytes)`; B.0(iii) proves invariance under every assignment to FD-1…FD-5 |
| Without creating any new authority | **MET** — `_verify_permit` (`LA:432-543`) is unmodified by all eleven units; no new caller, role, issuer, register operation or decision procedure |
| Without defining mutation semantics | **MET** — no unit classifies writes into governed/ungoverned. `R-5b` and `R-4` refuse specific state transitions that existing producer docstrings already declare impossible (`ukb.py:315-320`, `LA:121-129`) |
| Without defining audit semantics | **MET** — no unit emits, reads, requires or names an audit event. E-3's C6 gap is unchanged |
| Without defining permit issuance semantics | **MET** — no unit creates, appends to, updates or persists the permit register; `load_permit_register`'s single `open` (`LA:382`) remains the only register access. `R-9` narrows the `NO_ALLOCATION` *claim*, which is issued by nobody and appears in no register |
| Complete implementation-ready specification for the 12 | **MET** — Section C gives files, functions, invariants, migration, backward compatibility, failure modes and verification strategy per unit; Section E gives an executable reproduction and regression test per defect with PASS/FAIL conditions and a verified run command |
| Proof that the remainder is the irreducible governance-dependent core | **MET with a correction** — `{E1-F3, E-3, E-4A}` is irreducible for the enumerated set, and F.4 records two governance-dependent residues (`RES-1`, `RES-2`) that the enumerated set omitted |

---

# Section G — Evidence and reproduction integrity

## G.1 What was executed

All probes ran against `tempfile.mkdtemp()` ledgers except four read-only measurements against
`00-BOOK/DATA/id-ledger.json` (`LA.plan`, `LA.load_preimage`, and two `json.load` reads — all
non-mutating; `LA:416-430`, `:92-110`). `uga_engine.build` was **not** run for the mint path.
`register.sh` was **not** executed. No repository file was created or modified by this phase
other than this document.

```
$ git status --porcelain 00-BOOK/DATA/ 00-BOOK/tools/ 00-MASTER/UCOS-UGA-001/
AM 00-BOOK/tools/ledger_authority.py
 M 00-BOOK/tools/register.sh
 M 00-BOOK/tools/ukb.py
 M 00-MASTER/UCOS-UGA-001/uga_engine.py
```

Identical to the state Phase 0 recorded. `00-BOOK/DATA/` shows no change.

## G.2 Defects re-confirmed live against the UNMODIFIED authority

```
E2-F1     -> PERMIT  allocated={'by_object': ['UCOS-OBJ-000002']}
             disk    ['EXTRA.py', 'a.py', 'b.py']            (3 ids; 1 authorized)
E2-F2     -> allocating True  total 1  bytes_changed False   disk ['a.py']  (unchanged)
E2-F3     -> format_report renders bytes_changed : False
             contradiction allocating ∧ ¬bytes_changed representable : True
E1-F4     -> allocating False  NO_ALLOCATION
             disk {'universal_id': 'UCOS-OBJ-000001',
                   'object_class': 'GOVERNANCE_OBJECT', 'first_seen': 'c:FORGED'}
E1-F5(a)  -> LA.plan on a deep copy of the LIVE ledger:
             allocating True  total 0  unmeasured ['history']
E1-F5(b)  -> history erased, accepted; disk history == {}
E1-F6     -> UCOS-OBJ-000002 bound to BOTH b.py and c.py — ACCEPTED
             disk {'a.py': …001, 'b.py': …002, 'c.py': …002}
E1-F7     -> "json.loads(raw_before)" in commit() source : False
             open(path…) occurrences in commit()          : 2
E2-F4     -> allocating False  NO_ALLOCATION  bytes_changed True
             disk version 99   discovered_volumes {'VOL-666': 1}
E2-F5     -> live compiled patterns:
             uga _write_text body  False | ukb _dump_json body False
             uga call site         False | ukb call site        False
             naive direct write    True
E2-F6     -> bytes equal canon/ukb : False   (1 786 167 vs 2 274 511)
             bytes equal ukb/uga   : True
             docs  equal all three : True
```

## G.3 Remediation mechanics prototyped outside the repository

A shim reimplementing `R-1, R-2, R-3, R-4, R-5, R-7, R-9` around the unmodified module,
executed against throwaway ledgers. Ten cases, ten expected outcomes:

```
[PASS] E2-F1 divergent writer                    -> REFUSED (persisted document != authorized)
[PASS] E2-F2 silent writer                       -> REFUSED (persisted document != authorized)
[PASS] E1-F1 TOCTOU inside verification window   -> REFUSED (ledger changed before write)
[PASS] E1-F4 record-body rewrite                 -> REFUSED (record body of 'a.py' REWRITTEN)
[PASS] E1-F5b history erasure                    -> REFUSED (history 'UCOS-OBJ-000001' REMOVED)
[PASS] E1-F5a no-op after classifying history    -> ACCEPTED  (allocating False, unmeasured [])
[PASS] E2-F4 version/volumes under NO_ALLOCATION -> REFUSED (document differs from pre-image)
[PASS] E2-F3 allocating with bytes_changed False -> REFUSED (permit binding failed first)
[PASS] happy path: authorized allocation lands   -> ACCEPTED  (total 1, bytes_changed True)
[PASS] idempotent exec-declare no-op             -> ACCEPTED  (allocating False, bytes False)
10/10 mechanics verified
```

One transcript line needs its caveat stated rather than left to be inferred. The `E2-F3` case
refused, but on the **`preimage_digest` binding**, not on the intended
`allocating ∧ ¬bytes_changed` assertion: pre-placing the target bytes to construct the
contradiction also moves the pre-image, which `_verify_permit` (`LA:481-488`) refuses first.
The probe therefore did **not** demonstrate `R-8`'s assertion firing. That is consistent with —
and is what prompted — the derivation in D.5: after `R-7`, the contradiction is unreachable on
any path that returns, so `R-8`'s assertion is defence in depth and its non-vacuity has to be
demonstrated by defeating `R-7`'s comparison deliberately, which is how `E.9`'s third test is
specified. Reported this way rather than as a clean pass, because a probe that refused for a
different reason than the one under test proves nothing about that reason.

Additional prototypes:

- **R-3:** directory-fd `fcntl.flock(LOCK_EX)` acquired on macOS/APFS; a second process raised
  `BlockingIOError` under `LOCK_EX|LOCK_NB`.
- **R-6:** live-ledger uniqueness measured — `by_path` 1628, `by_object` 5374, `by_execution` 0,
  `by_observation` 7; zero duplicates within each map and zero across the union.
- **R-10:** AST indirection pass over every tracked `.py` file — **0 violations**;
  `_param_writing_functions` identifies `_dump_json` and `_write` in `ukb.py` and `_write_text`
  in `uga_engine.py`, none called with a ledger reference outside the authority; a synthetic
  `helper(LEDGER_PATH, "{}")` is caught.
- **Baseline:** `PYTHONPATH=. .ec1-venv/bin/pytest platform/tests/test_ledger_authority.py -q
  -p no:cacheprovider --no-cov` → **40 passed in 0.80 s** at `77798202`. Every unit must leave
  this green.

## G.4 Governance discipline

- FD-1, FD-2, FD-3′, FD-4, FD-5 — **not answered, not assumed, not inferred, not approached.**
- New authorities — **none.** `_verify_permit` unmodified by every unit.
- Permit semantics, ratification semantics, temporal legitimacy rules — **none introduced.**
  `R-9` narrows a caller *claim*; it does not touch a permit.
- Mutation definitions, audit-event definitions — **none introduced.** No unit classifies
  writes as governed, and no unit emits or requires an audit event.
- E1-F3, E-3, E-4A — **not remediated, not designed for, not ranked.** Referenced only where
  their existence constrains implementation (D.1 confirms no unit depends on any of them; D.3
  records the one outbound digest-ordering constraint against E-4A).
- Code changed by this phase — **none.** The deliverable is this specification.

## G.5 Stop condition

Phase 0.5 ends here. The next act is implementation of `R-1` … `R-11` under the DAG in D.2,
each unit landing with its reproduction test failing before and passing after, and the 40
existing tests green throughout. No governance question is opened by any of it.
