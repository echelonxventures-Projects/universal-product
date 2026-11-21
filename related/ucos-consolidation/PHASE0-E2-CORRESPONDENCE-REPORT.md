# PHASE0-E2 — WRITER ↔ AUTHORIZATION CORRESPONDENCE REPORT

| Field | Value |
|---|---|
| Work item | E-2 — Writer / Authorization Correspondence |
| Question answered | Are the bytes authorized by `commit()` guaranteed to equal the bytes persisted by `writer`? |
| Answer | **NO. No such guarantee exists, and its absence is exploitable without concurrency.** |
| Subject | `00-BOOK/tools/ledger_authority.py :: commit()` and its four production writers |
| Governance content | NONE. |

---

## 1. The four objects, traced

`commit()` is `ledger_authority.py:546-593`.

### 1.1 Authorized object

The dict `ledger`, as passed by the caller at `ledger_authority.py:546`.

Authorization is not over `ledger` itself. It is over a **lossy projection** of it:

```python
# ledger_authority.py:316-336
def manifest_digest(manifest: dict) -> str:
    return _sha256(_canonical({
        "actor", "allocated", "counter_advances", "cursor_advances",
        "unmeasured_maps", "total_allocations",
    }))
```

`allocated` comes from `allocation_report` (`:172-221`), which reads each record through
`_identifier_index` (`:112-119`) — one field per record. So the authorized object is:

> the **set of newly-appearing identifier strings** per identity map, plus `category_seq`
> and cursor deltas, plus the names of unmeasured maps, plus a count.

It is **not** the document. It carries no record bodies, no `history`, no `version`, no
`discovered_volumes`, and no bytes.

### 1.2 Serialized object

Produced by the caller-supplied `writer`, invoked once at `ledger_authority.py:583`:

```python
writer(path, ledger)
```

`writer` is an unconstrained callable. `commit()` neither inspects it nor constrains it.
The design intent is recorded at `ledger_authority.py:560-564`: *"Keeping it with the
caller preserves each writer's existing idempotency and guard behaviour byte-for-byte;
this function adds measurement, refusal and authorization, never a new on-disk format."*

Two distinct serializations are in production, and they are not byte-compatible with each
other or with the digest's canonical form (`_canonical`, `:303-310`, `sort_keys=True`,
no whitespace):

| Writer | Serialization | Source |
|---|---|---|
| `ukb._dump_json` | `json.dump(obj, fh, ensure_ascii=False, indent=2)` + `"\n"`, **preceded by an early return** | `ukb.py:135-146` |
| `uga_engine._dump` | `json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=False) + "\n"` via `_write_text` | `uga_engine.py:143-160` |

### 1.3 Persisted object

Whatever is on disk after `writer` returns. **`commit()` never reads it as an object.** It
reads it as opaque bytes at `ledger_authority.py:585-589` and uses them for one purpose
only:

```python
# ledger_authority.py:591
report["bytes_changed"] = raw_before != raw_after
```

There is no `json.load` after the write, anywhere in `commit()`.

### 1.4 Post-write state

`report`, returned at `ledger_authority.py:593`. It is **entirely** a function of `before`
and `ledger` — the pre-write inputs — plus the two boolean-producing byte reads. No field
of `report` is derived from the persisted document.

---

## 2. Transformations, enumerated

| # | Transformation | Source | Lossy? | Checked against the next stage? |
|---|---|---|---|---|
| T1 | file bytes → `before` dict | `ledger_authority.py:92-110` | no | n/a |
| T2 | `before`, `ledger` → identifier projections | `:112-119` | **yes** — one field per record | no |
| T3 | projections → `allocation_report` | `:172-221` | **yes** — set difference only | no |
| T4 | report → `manifest_digest` | `:316-336` | **yes** — six fields | no |
| T5 | `ledger` → serialized text | `ukb.py:135-146` / `uga_engine.py:143-160` | **caller-defined; may be a no-op** | **no** |
| T6 | text → file bytes | same | no | **no** |
| T7 | file bytes → `raw_after` | `ledger_authority.py:585-589` | no | compared to `raw_before` only |

**T5 and T6 are the correspondence gap.** Authorization terminates at T4. Persistence
begins at T5. Nothing joins them.

---

## 3. Findings

### E2-F1 — Divergent writer: authorized object ≠ persisted object, undetected

**Classification: UNSAFE.** Blocker status: **REPRODUCED.**

Reproduced (`E2-P6`, temp-dir ledger). A `writer` that persists a document different from
the one authorized:

```python
def divergent_writer(p, obj):
    forged = json.loads(json.dumps(obj))
    forged["by_object"]["b.py"]["universal_id"] = "UCOS-OBJ-999999"   # different identifier
    forged["by_object"]["EXTRA.py"] = {"universal_id": "UCOS-OBJ-000003", ...}  # extra identity
    forged["category_seq"]["OBJ"] = 3                                  # extra counter advance
    writer(p, forged)

report = LA.commit(path, after, actor="probe", writer=divergent_writer, permit=pid)
```

Observed:

```
commit() authorized : allocated={'by_object': ['UCOS-OBJ-000002']}
                      counter_advances={'OBJ': [1, 2]}
                      authorization=PERMIT   bytes_changed=True   (no error)
disk actually holds : {'a.py':'UCOS-OBJ-000001',
                       'b.py':'UCOS-OBJ-999999',
                       'EXTRA.py':'UCOS-OBJ-000003'}
                      category_seq={'OBJ': 3}
```

Three permanent identifiers on disk that no manifest measured and no permit named. The
report says one identifier, at a different value, and reports success.

Source: `ledger_authority.py:583` (unchecked invocation), `:585-591` (bytes read but not
parsed).

### E2-F2 — Silent writer: allocation reported, nothing persisted

**Classification: UNSAFE.** Blocker status: **REPRODUCED.**

`ukb._dump_json` begins:

```python
# ukb.py:135-146
def _dump_json(path, obj):
    T.forbid_data_telemetry(path, DATA_DIR)
    if _stamp_eq_json(path, obj):
        return                    # idempotent: only the stamp would change
    ...
```

Two ways this writer persists nothing while `commit()` reports allocation:

1. **Early return** — `_stamp_eq_json` (`ukb.py:75-107`) returns `True`. It neutralizes
   `generated_at` and, per its own docstring, *"any nested value equal to that same
   stamp"*, then compares. On the current ledger (no top-level `generated_at`) the stamp
   set is empty, so this reduces to plain equality — but the branch is reachable by
   construction and is not guarded by anything `commit()` checks.
2. **Raised exception** — `T.forbid_data_telemetry` can raise **after** authorization has
   already been granted. This is the safe direction (nothing lands) but confirms that
   authorization completing carries no implication about persistence.

Reproduced (`E2-P7`) with `writer=lambda p, o: None`:

```
report      : total_allocations=1  allocated={'by_object': ['UCOS-OBJ-000002']}
              bytes_changed=False
disk        : by_object=['a.py']            (unchanged)
operator line: "identity ledger ALLOCATED 1 permanent identifier(s) [by_object+1]
                actor=probe category_seq(OBJ:1->2)"
```

The operator is told one permanent identifier was allocated. Nothing was. This is the
**mirror image of the D0.1 defect** the module's header documents — D0.1 was *allocating
while reporting zero*; this is *reporting an allocation while allocating nothing*. The fix
addressed one direction.

### E2-F3 — `bytes_changed` is informational, never enforced

**Classification: UNSAFE.** Blocker status: **REPRODUCED.**

Every location `bytes_changed` appears:

| Location | Use |
|---|---|
| `ledger_authority.py:591` | assigned |
| `ledger_authority.py:564-565` (docstring) | *"records whether the file actually moved, which distinguishes a real allocation from an idempotent no-op rewrite"* |
| `uga_engine.py:2004` | `if report["bytes_changed"]: st = build(mint=False)` — triggers re-derivation for content-hash consistency |
| `platform/tests/test_ledger_authority.py:204, 332` | asserted `is True` |

Verdict, stated as E-2 requires:

- **Enforced: NO.** `commit()` performs no comparison, assertion or refusal involving
  `bytes_changed`. It is the final assignment before `return`.
- **Informational: YES.** Its only production consumer (`uga_engine.py:2004`) uses it as a
  cache-invalidation hint, not as a control.
- **Not even surfaced.** `format_report` (`ledger_authority.py:223-249`) — the sole
  operator-facing rendering, and what all four call sites print — **never references
  `bytes_changed`**. `ukb.py:1299`, `ukb.py:2380`, `ukb.py:2401` wrap `LA.commit` directly
  in `LA.format_report`, so the value is computed and discarded unseen.

The contradiction `allocating=True ∧ bytes_changed=False` is exactly the state E2-F2
produces, is fully representable in the returned report, and is checked nowhere.

### E2-F4 — `NO_ALLOCATION` authorizes arbitrary non-allocating mutation of the file

**Classification: UNSAFE.** Blocker status: **REPRODUCED.**

`NO_ALLOCATION` is documented as *"strictly safer than passing a permit — it can only ever
permit less"* (`ledger_authority.py:293-296`). It permits less **allocation**. It does not
permit less **mutation**, because the sentinel is checked only against `manifest`
`["allocating"]` (`:435-442`), and `allocating` is blind to:

- `version` and `discovered_volumes` — in `NON_ALLOCATION_KEYS` (`:83-85`)
- every non-identifier field of every existing record — `_identifier_index` (`:112-119`)

Reproduced (`E2-P8`), mutating both under a `NO_ALLOCATION` claim:

```
authorization=NO_ALLOCATION  allocating=False  bytes_changed=True
disk now carries: version=99  discovered_volumes=['VOL-666']
```

For `by_execution` this is material: the entire execution lifecycle body written at
`ukb.py:2388-2400` — `lifecycle_state`, `transitions`, `last_transition_seq` — is
rewritable under a claim that nothing is being allocated.

### E2-F5 — `LEDGER-INV-01` is lexically blind to the shape both sanctioned writers use

**Classification: UNSAFE.** Blocker status: **REPRODUCED.**

`LEDGER-INV-01` (`IDENTITY_LEDGER_HAS_ONE_WRITE_PATH`, `uga_engine.py:1249-1272`, engine at
`:1094-1120`) is the structural guarantee that `commit()` is the only write path. Its
patterns (`uga_engine.py:1079-1092`) require the ledger to be **named on the same source
line** as a write primitive:

```python
_LEDGER_REF = r"(?:(?<![A-Z_])LEDGER_PATH\b|id-ledger\.json)"
```

A function that receives the path as a **parameter** never names it. Tested directly
against the live compiled patterns:

```
uga_engine _write_text body   `with open(path, "w", ...) as fh:`   matched = False
ukb _dump_json body           `with open(path, "w", ...) as fh:`   matched = False
uga_engine call site          `writer=lambda p, o: _dump(p, o),`   matched = False
ukb call site                 `writer=_dump_json,`                 matched = False
hypothetical direct write     `_dump_json(LEDGER_PATH, ledger)`    matched = True
```

Both production writers are **exactly** the unmatched shape. `LEDGER-INV-01` therefore
constrains only the *naïve* second write path. It does not, and cannot, constrain what a
`writer` does once `commit()` hands it the path — which is precisely the surface E2-F1
exploits. The invariant is sound for the failure mode named in its own comment (*"a NEW
direct write … is visible in the source text"*); it does not establish the property E-2
asks about.

### E2-F6 — Serialization equality between authorized and persisted form is unproven

**Classification: UNPROVEN.** Blocker status: **NOT REPRODUCIBLE as a defect.**

Three serializers exist over the same document: `_canonical` (`ledger_authority.py:303-310`,
`sort_keys=True`, compact), `ukb._dump_json` (`indent=2`, insertion order),
`uga_engine._dump` (`indent=2`, `sort_keys=False`). No round-trip equivalence test exists,
and none is asserted in source.

No divergence was demonstrated: the digest is over a projection, not over bytes, so key
order does not currently affect authorization. Recorded as UNPROVEN rather than SAFE
because if any future control binds *bytes* rather than the projection, three
non-equivalent serializers become a correctness requirement with no test behind it.

### E2-F7 — The production correspondence question is presently unreachable

**Classification: UNSAFE (higher-order).** Blocker status: **REPRODUCED.**

Measured against `00-BOOK/DATA/id-ledger.json`, all three possible values of `permit` are
refused, so no production write reaches `writer` at all:

```
permit=None (no --permit flag)  -> PermitRefused: permit must be a permit_id string or NO_ALLOCATION
permit='P-ANY'                  -> PermitRefused: permit 'P-ANY' is not in
                                   00-BOOK/DATA/allocation-permits.json
permit=NO_ALLOCATION            -> PermitRefused: NO_ALLOCATION was asserted, but this
                                   write ALLOCATES … UNMEASURED_MAPS=['history']
```

`register.sh:216` invokes `ukb.py build --mint` with **no** `--permit`. See
`PHASE0-E4A-ISSUANCE-PATH-REPORT.md`. Consequence for E-2: the correspondence defects
E2-F1…F4 are **latent, not active** — they are properties of code that currently cannot
execute in production. They are still classified UNSAFE, because the blocking condition is
a separate defect (E-4A) whose removal activates them all simultaneously.

---

## 4. Per-path determination

| Path | Determination |
|---|---|
| authorized object → serialized object | **UNSAFE** — `writer` unconstrained (`ledger_authority.py:583`); E2-F1 |
| serialized object → persisted object | **UNSAFE** — writer may persist nothing (`ukb.py:139-140`); E2-F2 |
| persisted object → post-write state | **UNSAFE** — persisted object never parsed; `report` derived wholly from pre-write inputs (`ledger_authority.py:567-593`) |
| `bytes_changed` recording | **SAFE** — correctly computed at `:591` from two real byte reads |
| `bytes_changed` enforcement | **UNSAFE** — informational only; absent from `format_report` (`:223-249`); no refusal anywhere |
| `NO_ALLOCATION` → persisted mutation | **UNSAFE** — E2-F4 |
| `LEDGER-INV-01` → writer behaviour | **UNSAFE** — lexically blind to parameter indirection; E2-F5 |
| serializer equivalence | **UNPROVEN** — E2-F6 |
| pre-write authorization ordering | **SAFE** — `_verify_permit` precedes `writer` (`:573` before `:583`); a refused write persists nothing |
| manifest recomputation from disk | **SAFE** — `commit()` recomputes rather than trusting the caller (`:569-573`) |
| `plan()` / `commit()` scope identity | **SAFE** — one `build_manifest` (`:402-414`), called at `:429` and `:569` |

---

## 5. Answer to the E-2 question

> Are the bytes authorized by `commit()` guaranteed to equal the bytes persisted by
> `writer`?

**No.** Three independent reasons, in increasing order of generality:

1. **Nothing is compared.** No code path reads the persisted document back as an object.
   `raw_after` (`ledger_authority.py:585-589`) is compared only to `raw_before`.
2. **Bytes are never authorized.** The permit binds `manifest_digest`
   (`ledger_authority.py:316-336`) — a six-field projection of an identifier-only view. No
   digest of the document, or of the intended file content, exists anywhere in the system.
   The question "do the authorized bytes equal the persisted bytes" has no authorized-bytes
   term to compare against.
3. **The writer is outside the boundary by design.** `ledger_authority.py:560-564` states
   this as an intentional trade to preserve caller idempotency. The trade is real; what is
   missing is any compensating post-write check.

**Classification: UNSAFE — 7 paths. UNPROVEN — 1 path. SAFE — 4 paths.**

No remediation was applied.

---

## 6. Residual governance dependency

**None.** Whether persisted bytes match authorized bytes is undefined by every governance
answer: no authority, permit rule, ratification rule or temporal decision speaks to it.
E2-F7 records a dependency on E-4A (whether an issuance path exists), which is an
existence question, not a governance question — see `PHASE0-E4A-ISSUANCE-PATH-REPORT.md`.

---

## 7. Reproduction integrity

E2-P6, E2-P7, E2-P8 ran against `tempfile.mkdtemp()` ledgers. The E2-F7 measurement used
`LA.plan` and `LA._verify_permit` against the production ledger; both are read-only
(`ledger_authority.py:416-430`, `:432-543`).
`git status --porcelain 00-BOOK/DATA/id-ledger.json` is empty. The probe harness was
deleted after execution.
