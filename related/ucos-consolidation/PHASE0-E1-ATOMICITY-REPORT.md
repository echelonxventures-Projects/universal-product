# PHASE0-E1 — VERIFICATION → WRITE ATOMICITY REPORT

| Field | Value |
|---|---|
| Work item | E-1 — Verification → Write Atomicity |
| Question answered | Can `commit()` observe one state, validate that state, and write a different state without detection? |
| Answer | **YES. Reproduced by execution.** |
| Subject of measurement | `00-BOOK/tools/ledger_authority.py :: commit()` and every caller reaching it |
| Repository state | working tree at `77798202` + uncommitted modifications to `ukb.py`, `uga_engine.py`, `register.sh`; `ledger_authority.py` is `AM` (never committed) |
| Governance content | NONE. No authority, permit rule, domain rule, threat model or temporal decision is asserted or assumed anywhere in this report. |

---

## 0. Scope discipline

Every finding below is stated as a property of the code under **every possible answer** to
who may authorize a write, what a permit means, when authorization expires, or which
authority owns the ledger. Each finding is written so that substituting any governance
answer whatsoever changes nothing about it. Where a defect's severity *would* depend on a
governance answer, it is classified **UNVERIFIABLE** and the dependency is named, not
resolved.

---

## 1. The write path, enumerated

### 1.1 Verification steps

`commit()` is `ledger_authority.py:546-593`. In execution order:

| # | Step | Source | Reads |
|---|---|---|---|
| V1 | `before = load_preimage(path)` | `ledger_authority.py:567` | ledger file, parsed as JSON |
| V2 | `assert_append_only(before, ledger)` | `ledger_authority.py:568` → `:121-170` | in-memory only |
| V3 | `report = build_manifest(before, ledger, actor, path)` | `ledger_authority.py:569` → `:402-414` | in-memory + **`git_head()` subprocess** |
| V3a | `preimage_digest(before)` | `ledger_authority.py:338-347` | in-memory |
| V3b | `git_head(path)` — `subprocess.run(..., timeout=15)` | `ledger_authority.py:349-368` | forks `git rev-parse HEAD` |
| V3c | `manifest_digest(manifest)` | `ledger_authority.py:316-336` | in-memory |
| V4 | `used = _verify_permit(permit, report, actor, path)` | `ledger_authority.py:573` → `:432-543` | **permit register file** |

`plan()` (`ledger_authority.py:416-430`) performs V1–V3 and returns. It is read-only and
shares `build_manifest`, so preview and execution measure through one implementation.

### 1.2 Write steps

| # | Step | Source |
|---|---|---|
| W0 | `raw_before = fh.read()` — **second, independent read of the same file** | `ledger_authority.py:577-581` |
| W1 | `writer(path, ledger)` | `ledger_authority.py:583` |
| W2 | `raw_after = fh.read()` | `ledger_authority.py:585-589` |
| W3 | `report["bytes_changed"] = raw_before != raw_after` | `ledger_authority.py:591` |

Concrete `writer` values in production:

| Caller | `writer` | Source |
|---|---|---|
| `ukb.py build --mint` | `_dump_json` | `ukb.py:1299-1303`; writer at `ukb.py:135-146` |
| `ukb.py exec declare` (idempotent) | `_dump_json` | `ukb.py:2380-2384` |
| `ukb.py exec declare` (new) | `_dump_json` | `ukb.py:2401-2405` |
| `uga_engine.py run` | `lambda p, o: _dump(p, o)` | `uga_engine.py:1999-2002`; writer at `uga_engine.py:143-160` |

### 1.3 Mutation windows

There are **three** distinct windows in which the on-disk ledger can change while
`commit()` holds a stale observation of it. No lock, file descriptor, `O_EXCL`,
compare-and-swap or atomic rename spans any of them:

```
$ grep -rn "fcntl|flock|LOCK_EX|O_EXCL|threading.Lock|filelock" --include=*.py \
      00-BOOK/tools/ 00-MASTER/UCOS-UGA-001/
  (no matches)
$ grep -rn "os.replace|os.rename|NamedTemporary|fsync" --include=*.py \
      00-BOOK/tools/ 00-MASTER/UCOS-UGA-001/
  00-BOOK/tools/governance_telemetry.py:210,217   # telemetry only — not the ledger
```

| Window | Span | Duration character |
|---|---|---|
| **MW-1** | V1 → W1 (`load_preimage` → `writer`) | Contains a `subprocess.run` fork with a **15 s** timeout (V3b) plus a second file open (V4). Unbounded in practice. |
| **MW-2** | W0 → W1 (`raw_before` read → `writer`) | Short but non-zero; `raw_before` is the only value `bytes_changed` is derived from. |
| **MW-3** | caller's own ledger read → V1 | For `uga_engine.py run`: `ledger = _load(LEDGER_PATH)` at `uga_engine.py:1700`, then the entire `build(mint=True)` discovery pass (measured at ~60 s on this repository), then V1 at `ledger_authority.py:567`. |

`before` (V1, JSON-parsed) and `raw_before` (W0, raw bytes) are **two independent reads of
the same file that are never reconciled with each other**. `raw_before` is used only at
`ledger_authority.py:591` to compute `bytes_changed`. A single available comparison —
`json.loads(raw_before) == before` — would have collapsed MW-1 into MW-2. It is not
performed.

---

## 2. Findings

### E1-F1 — TOCTOU: the file can be replaced inside `commit()`'s own verification window

**Classification: PROVEN UNSAFE.** Blocker status: **REPRODUCED.**

`assert_append_only` (V2) and the manifest (V3) are both computed against `before` read at
V1. `writer` at W1 receives `ledger` — the caller's whole proposed document — and
overwrites the file unconditionally. Nothing between V1 and W1 re-establishes that the
file still holds `before`.

Source references:
- `ledger_authority.py:567` — the only read that verification uses.
- `ledger_authority.py:568-569` — verification bound to that read.
- `ledger_authority.py:583` — the write, with no re-check.
- `ledger_authority.py:349-368` — `git_head`, the `subprocess.run(timeout=15)` inside the
  window, executed at `:411` via `build_manifest`.

Reproduction (executed; temp-dir ledger, repository untouched). A concurrent allocation is
injected at exactly the point where `commit()` yields the CPU to a subprocess:

```python
import sys, json, os, tempfile
sys.path.insert(0, "00-BOOK/tools"); import ledger_authority as LA
BASE = {"version":1,"category_seq":{"OBJ":1},
        "by_object":{"a.py":{"universal_id":"UCOS-OBJ-000001",
                             "object_class":"TOOLING_OBJECT","first_seen":"commit:aaaa"}}}
tmp = tempfile.mkdtemp(); path = os.path.join(tmp,"id-ledger.json")
w = lambda p,o: open(p,"w").write(json.dumps(o, indent=2))
w(path, BASE)
after = json.loads(json.dumps(BASE)); after["category_seq"]["OBJ"] = 2
after["by_object"]["b.py"] = {"universal_id":"UCOS-OBJ-000002",
                              "object_class":"TOOLING_OBJECT","first_seen":"commit:bbbb"}
m = LA.plan(path, after, actor="probe")
json.dump({"permits":[{"permit_id":"P-1","actor":"probe",
    "manifest_digest":m["digest"],"preimage_digest":m["preimage_digest"],"head":None}]},
    open(LA.permit_register_path(path),"w"))
real, fired = LA.git_head, []
def hijack(near):                       # the concurrent actor, inside MW-1
    if not fired:
        fired.append(1)
        c = json.loads(json.dumps(BASE)); c["category_seq"]["OBJ"] = 2
        c["by_object"]["z.py"] = {"universal_id":"UCOS-OBJ-000002",
                                  "object_class":"TOOLING_OBJECT","first_seen":"commit:zzzz"}
        w(path, c)
    return real(near)
LA.git_head = hijack
r = LA.commit(path, after, actor="probe", writer=w, permit="P-1")
LA.git_head = real
print(r["allocating"], r["allocated"], r["bytes_changed"])
print(sorted(json.load(open(path))["by_object"]))
```

Observed output:

```
True {'by_object': ['UCOS-OBJ-000002']} True
['a.py', 'b.py']
```

`z.py` — a permanent identifier already persisted to disk — is gone. No refusal was
raised. `UCOS-OBJ-000002` is now bound to two different paths across time, which is the
exact property `assert_append_only` exists to make impossible. The chokepoint reports
success.

### E1-F2 — No concurrency control of any kind on the ledger

**Classification: PROVEN UNSAFE.** Blocker status: **REPRODUCED.**

`commit()` contains no mutual exclusion. The only lock in the repository that mentions the
ledger is in the *transaction wrapper*, not the chokepoint:

- `register.sh:187-197` — `if [ -f "$LOCK" ] … date +%s > "$LOCK"`. This is itself a
  non-atomic test-then-create, and it guards only `register.sh`. `uga_engine.py run`
  (`uga_engine.py:1975`) and `ukb.py exec declare` (`ukb.py:2343`) take no lock and are
  reachable independently.

Two commits derived from one shared pre-image were tested (`E1-P3`). When B runs strictly
**after** A's bytes land, `assert_append_only` refuses B (A's new key is missing from B's
proposal → `entry … would be REMOVED`). That refusal is a **side effect of ordering**, not
a serialization guarantee: E1-F1 is the same two writers interleaved differently, and it is
not refused. The `preimage_digest` binding (`ledger_authority.py:338-347`) narrows but does
not close the window, because it is evaluated at V3 — inside MW-1.

### E1-F3 — Restore/replay: `preimage_digest` un-spends on any ledger restore

**Classification: PROVEN UNSAFE.** Blocker status: **REPRODUCED.**

`ledger_authority.py:338-347` states the design intent explicitly: *"performing the
allocation changes the pre-image, so recomputing this value afterwards no longer matches
the permit and the same permit cannot be replayed. No spent-permit registry is required,
and none is created — spent-ness is DERIVED from two artifacts that are already
committed."*

Spent-ness derived from mutable state is not spent-ness. Restoring the ledger file to its
prior bytes — `git checkout`, `git revert`, a stash pop, a backup restore, or the
`assert_append_only`-permitted rewrite in E1-F4 — restores the pre-image digest and makes
every permit issued against that state valid again.

Reproduced (`E1-P2`):

```
first commit allocated {'by_object': ['UCOS-OBJ-000002']}
immediate replay                     -> refused
after restoring the pre-image bytes  -> the SAME permit 'P-1' ACCEPTED again
                                        -> {'by_object': ['UCOS-OBJ-000002']}
```

There is no spent-permit record anywhere in the repository to consult; the only permit
state is the register read at `ledger_authority.py:376-399`, which `commit()` never writes.

This finding is governance-independent: it holds whatever a permit means and whoever
issues it, because it concerns only whether *use* is recorded.

### E1-F4 — Stale-preimage class: record bodies of permanent identities are outside every check

**Classification: PROVEN UNSAFE.** Blocker status: **REPRODUCED.**

`_identifier_index` (`ledger_authority.py:112-119`) projects every ledger record to a
single field:

```python
out[key] = rec.get(field) if isinstance(rec, dict) else rec
```

`assert_append_only` (`:121-170`) and `allocation_report` (`:172-221`) both consume only
that projection. Therefore every other field of an existing record — `object_class`,
`category`, `first_seen`, `page_start`, `page_count`, and for `by_execution` the entire
`lifecycle_state` / `transitions` / `last_transition_seq` body written at
`ukb.py:2388-2400` — can be rewritten arbitrarily, and:

- `assert_append_only` raises nothing,
- `allocating` is `False` and `total_allocations` is `0`,
- the `manifest_digest` (`:316-336`) does not cover it,
- a `NO_ALLOCATION` claim is **accepted**.

Reproduced (`E1-P4`), rewriting `object_class` to `GOVERNANCE_OBJECT` and `first_seen` to
`commit:FORGED` while holding `universal_id` constant:

```
assert_append_only  PASSED (no refusal)
allocating=False  total_allocations=0
NO_ALLOCATION claim ACCEPTED
```

This also supplies the restore primitive E1-F3 requires without needing any VCS operation.

### E1-F5 — `history` is in neither classification set, which disables `NO_ALLOCATION` on the production ledger

**Classification: PROVEN UNSAFE.** Blocker status: **REPRODUCED.**

The production ledger `00-BOOK/DATA/id-ledger.json` has these top-level keys:

```
version, by_path, page_cursor, category_seq, discovered_volumes, volume_seq,
history, by_object, by_observation
```

`history` (1628 entries) appears in **neither** `IDENTITY_MAPS`
(`ledger_authority.py:71-77`) **nor** `NON_ALLOCATION_KEYS` (`:83-85`). It is written by
`record_snapshots` (`ukb.py:314-330`, `hist = ledger.setdefault("history", {})`) and is
described as append-only by comment at `ukb.py:1228-1232` — with no corresponding check
anywhere.

Two consequences, both measured against the live file:

**(a) A byte-identical no-op write is classified as allocating.** `allocation_report`
(`:207-211`) folds `unmeasured_maps` into `allocating` (`:196-198`, deliberately, to fail
closed):

```
$ python3 -c "...; m = LA.plan('00-BOOK/DATA/id-ledger.json', copy.deepcopy(before), actor='PHASE0-PROBE')"
allocating        : True
total_allocations : 0
unmeasured_maps   : ['history']
report line       : identity ledger MUTATED with no measured identifier allocation
                    actor=PHASE0-PROBE UNMEASURED_MAPS=['history']
```

Therefore `permit=NO_ALLOCATION` is **unconditionally refused** against the real ledger:

```
NO_ALLOCATION was asserted, but this write ALLOCATES: identity ledger MUTATED with
no measured identifier allocation … UNMEASURED_MAPS=['history']
```

The `ukb.py exec declare` idempotent branch at `ukb.py:2380-2384` passes exactly
`LA.NO_ALLOCATION`, with the in-source justification *"NO_ALLOCATION is correct HERE BY
CONSTRUCTION."* On the production ledger that branch cannot execute. Its comment predicts
the correct outcome — *"the write is refused rather than silently permitted"* — so the
control fails in the safe direction, but the code path is dead.

**(b) `history` erasure is not an append-only violation.** Reproduced (`E1-P5`): replacing
`history` with `{}` passes `assert_append_only` with no refusal. The append-only property
that `ukb.py:314-321` claims to establish is enforced nowhere.

### E1-F6 — Caller-side minting arithmetic is computed against a different read than verification

**Classification: UNVERIFIABLE.** Blocker status: **REPRODUCED as a window; no unsafe outcome demonstrated.**

`uga_engine.py:1700` reads the ledger. `epoch1_identity` (`uga_engine.py:271-321`) then
computes each new identifier as `n = seq.get(cat, 0) + 1` against **that** read. `commit()`
re-reads the file at `ledger_authority.py:567`, after the full discovery pass (MW-3).

If a concurrent writer advanced `category_seq[cat]` and added a key during MW-3,
`assert_append_only` detects the missing key (`ledger_authority.py:135-139`) and refuses —
so the *observed* behaviour is fail-closed. But the counter-collision leg is not
independently detected: `new_n < old_n` (`:157`) is false when both reads produce the same
next value, so the refusal depends entirely on the key-removal check. Whether a
key-preserving concurrent counter advance is constructible is not established here.

Classified UNVERIFIABLE rather than safe because no test in the repository covers MW-3 and
no argument in the source addresses it.

### E1-F7 — `raw_before` is read but never reconciled with `before`

**Classification: PROVEN UNSAFE (enabler for E1-F1).** Blocker status: **REPRODUCED.**

`ledger_authority.py:577-581` opens and reads the ledger a second time. The value is used
only at `:591`. The comparison that would detect a MW-1 mutation —
`json.loads(raw_before) == before` — is available at zero additional I/O cost and is not
made. This is recorded separately from E1-F1 because it is the single narrowest point at
which the window is observable.

---

## 3. Proven safe

| # | Property | Evidence |
|---|---|---|
| E1-S1 | A refused write leaves the ledger byte-identical. Every refusal (V2, V4) raises before `writer` is reached. | `ledger_authority.py:567-583` — `writer` is the last statement; `assert_append_only` and `_verify_permit` both raise. Ordering verified by reading; exercised by `platform/tests/test_ledger_authority.py`. |
| E1-S2 | An unreadable ledger refuses rather than being treated as empty. | `ledger_authority.py:100-110` — `OSError`/`ValueError` → `LedgerWriteRefused`. Without this, every existing identity would report as freshly minted. |
| E1-S3 | An unreadable or wrongly-shaped permit register refuses. | `ledger_authority.py:387-399`. |
| E1-S4 | A missing ledger is a legitimate first mint, not an error, and every identity is then correctly reported new. | `ledger_authority.py:97-99`. |
| E1-S5 | The permit is verified against the **recomputed** manifest, never against a caller-supplied description. | `ledger_authority.py:571-573` and the comment at `:571-572`. |
| E1-S6 | `plan()` and `commit()` measure through one implementation, so preview cannot diverge from execution. | Both call `build_manifest` and nothing else: `ledger_authority.py:429` and `:569`; rationale at `:402-408`. |
| E1-S7 | `permit` has no default, so omitting it is a `TypeError` at the call site rather than a silent bypass. | `ledger_authority.py:546` signature; rationale at `:555-559`. |
| E1-S8 | Within the identifier projection, removal / reissue / `category_seq` regression / monotonic-cursor regression are all refused. | `ledger_authority.py:130-165`. **Scope limit:** the projection is `_identifier_index`, so this is safe *only* for the identifier field — see E1-F4. |

---

## 4. Answer to the E-1 question

> Can `commit()` observe one state, validate that state, and write a different state
> without detection?

**Yes, by three independent mechanisms:**

1. **The observed state can change** between observation and write — E1-F1, executed, with
   a permanent identifier destroyed and success reported.
2. **The written state can differ from the validated state** even with no concurrency,
   because `writer` is an unconstrained caller-supplied callable and the persisted bytes
   are never compared to `ledger` — this is E-2's subject; see
   `PHASE0-E2-CORRESPONDENCE-REPORT.md`.
3. **Parts of the state are never observed at all** — record bodies (E1-F4) and `history`
   (E1-F5) are outside every check, so a write that changes only those is validated
   vacuously.

---

## 5. Classification summary

| ID | Finding | Classification | Blocker status |
|---|---|---|---|
| E1-F1 | TOCTOU in `commit()`'s verification window | PROVEN UNSAFE | REPRODUCED |
| E1-F2 | No concurrency control on the ledger | PROVEN UNSAFE | REPRODUCED |
| E1-F3 | Permit replay after ledger restore | PROVEN UNSAFE | REPRODUCED |
| E1-F4 | Record bodies outside every check | PROVEN UNSAFE | REPRODUCED |
| E1-F5 | `history` unclassified → `NO_ALLOCATION` dead + history erasure unrefused | PROVEN UNSAFE | REPRODUCED |
| E1-F6 | Minting arithmetic vs. verification read (MW-3) | UNVERIFIABLE | REPRODUCED as window |
| E1-F7 | `raw_before` never reconciled with `before` | PROVEN UNSAFE | REPRODUCED |
| E1-S1…S8 | Eight properties | PROVEN SAFE | n/a |

**Unsafe: 6. Unverifiable: 1. Safe: 8.**

No remediation was applied. Every finding above is a determination; each is
governance-independent, and none of the four work items in this phase authorized a code
change.

---

## 6. Residual governance dependency

**None for the findings.** Each unsafe finding is a defect under every possible answer to
who may authorize a write, what a permit means, when it expires, or which authority owns
the ledger:

- E1-F1/F2/F7 concern whether the verified state is the written state — undefined by any
  authority.
- E1-F3 concerns whether *use* of an authorization is recorded — independent of what the
  authorization means.
- E1-F4/F5 concern whether a mutation is observed at all — prior to any question of
  permission.

The **remedies** are the point at which governance re-enters, and this report proposes
none. Naming the choice without making it: closing E1-F3 requires deciding whether a
permit is single-use, which is an issuance-semantics question (FD-scope). Closing
E1-F1/F2/F7 does not — re-reading and comparing bytes before writing decides nothing about
authority. That distinction is recorded in
`PHASE0-GOVERNANCE-INDEPENDENT-DETERMINATION.md` §4 and is not acted on here.

---

## 7. Reproduction integrity

All probes ran against throwaway `tempfile.mkdtemp()` ledgers except the two read-only
measurements against `00-BOOK/DATA/id-ledger.json` (`LA.plan` and `LA._verify_permit`,
both of which write nothing — `ledger_authority.py:416-430` and `:432-543`).
`git status --porcelain 00-BOOK/DATA/id-ledger.json` is empty before and after. The probe
harness was deleted after execution; every probe is reproduced inline above or in
`PHASE0-E2-CORRESPONDENCE-REPORT.md`.
