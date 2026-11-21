# PHASE0-E4A — PERMIT ISSUANCE EXISTENCE PATH REPORT

| Field | Value |
|---|---|
| Work item | E-4A — Permit Issuance Existence Path |
| Question | Does any production path exist that writes permit records? |
| **Answer** | **NO. No production code creates, appends to, updates or persists the permit register. Only consumption is implemented.** |
| Blocker status | **REPRODUCED** |
| Governance content | NONE. This report determines only whether code exists. It does not assess whether issuance is valid, who may issue, or what issuance means. |

---

## 1. What the register is, per the implementation

```python
# 00-BOOK/tools/ledger_authority.py:275
PERMIT_REGISTER_NAME = "allocation-permits.json"

# 00-BOOK/tools/ledger_authority.py:371-373
def permit_register_path(ledger_path: str) -> str:
    """The register sits beside the ledger it authorizes, so the pair moves together."""
    return os.path.join(os.path.dirname(os.path.abspath(ledger_path)), PERMIT_REGISTER_NAME)
```

Resolved for the production ledger:

```
00-BOOK/DATA/id-ledger.json  ->  00-BOOK/DATA/allocation-permits.json
```

Required shape, per `load_permit_register` (`ledger_authority.py:376-399`): a JSON object
carrying a `permits` list (a bare list is also accepted), each element a dict. Required
fields, per `_verify_permit` (`ledger_authority.py:432-543`): `permit_id`, `actor`,
`manifest_digest`, `preimage_digest`; optional `head`, `scope.maps`,
`scope.max_allocations`, `expires_at`, `single_use`.

---

## 2. Complete inventory of every reference to the register

Exhaustive search across `.py`, `.sh`, `.json`, `.yml` and `Makefile`:

```
$ grep -rn "allocation-permits|PERMIT_REGISTER_NAME|permit_register_path" \
      --include=*.py --include=*.sh --include=Makefile --include=*.yml --include=*.json .
```

| Location | Operation | Production? |
|---|---|---|
| `ledger_authority.py:275` | constant definition | authority module |
| `ledger_authority.py:371-373` | `permit_register_path` — path derivation | authority module |
| `ledger_authority.py:382` | `open(path)` — **read** | authority module |
| `ledger_authority.py:456` | error message naming the register | authority module |
| `ukb.py:2497-2498` | `--permit` argparse help text | production, string only |
| `ukb.py:2555-2556` | `--permit` argparse help text | production, string only |
| `uga_engine.py:2079-2080` | `--permit` argparse help text | production, string only |
| `platform/tests/test_ledger_authority.py:85-87` | `.write_text(json.dumps({"permits": [permit]}))` | **test fixture** |
| `platform/tests/test_ledger_authority.py:474` | writes `"{ not json"` — unreadable-register case | **test fixture** |
| `platform/tests/test_ledger_authority.py:503-505` | reads, mutates, rewrites | **test fixture** |
| `platform/tests/test_ledger_authority.py:524` | asserts non-existence | **test fixture** |

**Total write operations in production code: zero.** The only code in the repository that
writes the register is the test helper `_issue` at `platform/tests/test_ledger_authority.py:61-87`,
whose docstring describes itself as *"the real operator workflow"* — but it lives in a test
module and is not importable as an operator tool.

Confirmed absent from disk:

```
$ python3 -c "import sys; sys.path.insert(0,'00-BOOK/tools'); import ledger_authority as LA, os
p = LA.permit_register_path('00-BOOK/DATA/id-ledger.json'); print(p, os.path.exists(p))"
/Users/bipin/Desktop/UCOS-CONSOLIDATION/00-BOOK/DATA/allocation-permits.json  False
```

```
$ ls 00-BOOK/DATA/
artifacts.json  canonical-observation-audit.json  certification.json  change-ledger.json
connector-cursors.json  constitutional-authority-alignment.json  control-tower.json
evidence-universe.json  exclusion-register.json  generated-artifact-registry.json
id-ledger.json  mutation-governance-boundary.json  observation-universe.json
relationships.json  signals.json  twin.json  volumes.json
```

No `allocation-permits.json`.

---

## 3. Per-operation determination

| Operation | Status | Evidence |
|---|---|---|
| **register creation** | **MISSING** | No code in any non-test file opens the path for writing, creates it, or scaffolds it. No `Makefile` target, no shell script, no CLI subcommand. `load_permit_register` treats absence as an empty register (`ledger_authority.py:383-385`) rather than creating one. |
| **register append** | **MISSING** | No `issue()`, `mint_permit()`, `add_permit()`, `permit issue` subcommand or equivalent exists. Grep for any function whose name pairs a write verb with "permit" returns nothing outside tests. |
| **register update** | **MISSING** | No code mutates an existing permit record. No spent-marking, no revocation, no expiry stamping. `ledger_authority.py:338-347` states this is deliberate: *"No spent-permit registry is required, and none is created — spent-ness is DERIVED."* The absence is by design; the design's soundness is E-1's subject (E1-F3), not this report's. |
| **register consumption** | **IMPLEMENTED** | `load_permit_register` (`ledger_authority.py:376-399`) reads and shape-checks; `_verify_permit` (`:432-543`) resolves `permit_id`, rejects zero matches (`:455-456`) and ambiguous matches (`:457-461`), then verifies actor, `manifest_digest`, `preimage_digest`, `head`, `scope.maps`, `scope.max_allocations` and `expires_at`. Reached from `commit()` at `:573`. Covered by `platform/tests/test_ledger_authority.py`. |
| **register persistence** | **MISSING** | Nothing writes the file, so nothing persists it. It is also absent from every registration surface: not in `00-BOOK/DATA/`, not produced by `register.sh`, not emitted by `ukb.py`, not emitted by `uga_engine.py:emit()`. |

**Implemented: 1 of 5. Partially implemented: 0 of 5. Missing: 4 of 5.**

The one implemented operation is the consumer. The register it consumes has no producer.

---

## 4. Measured consequence: the production write path cannot execute

This is not an inference. All three possible values of the `permit` parameter were passed to
`_verify_permit` against a manifest measured from the live `00-BOOK/DATA/id-ledger.json`:

```
permit=None (no --permit flag)  -> PermitRefused: permit must be a permit_id string or
                                   NO_ALLOCATION; got None
permit='P-ANY'                  -> PermitRefused: permit 'P-ANY' is not in
                                   /…/00-BOOK/DATA/allocation-permits.json
permit=NO_ALLOCATION            -> PermitRefused: NO_ALLOCATION was asserted, but this
                                   write ALLOCATES: identity ledger MUTATED with no
                                   measured identifier allocation …
                                   UNMEASURED_MAPS=['history']
```

`permit` has no default (`ledger_authority.py:546`), so there is no fourth value. The
`NO_ALLOCATION` refusal is a separate defect documented as **E1-F5** — `history` is in
neither `IDENTITY_MAPS` (`:71-77`) nor `NON_ALLOCATION_KEYS` (`:83-85`), so on the real
ledger even a byte-identical no-op measures `allocating=True`.

### 4.1 The three production call sites, and what each passes

| Call site | `permit` argument | Reachable outcome |
|---|---|---|
| `ukb.py:1299-1303` — `build --mint` | `getattr(args, "permit", None)` | refused unless `--permit` names a permit in a register that does not exist |
| `ukb.py:2380-2384` — `exec declare` (idempotent) | `LA.NO_ALLOCATION` (hard-coded) | **always refused** on the production ledger — E1-F5 |
| `ukb.py:2401-2405` — `exec declare` (new) | `getattr(args, "permit", None)` | refused, as above |
| `uga_engine.py:1999-2002` — `run` | `getattr(args, "permit", None)` | refused, as above |

### 4.2 The registration transaction does not pass a permit at all

```bash
# 00-BOOK/tools/register.sh:211-216
# --- Phase 1 — Foundation registration …
# --mint is EXPLICIT here and nowhere else. This is the REG-AUTO-001 transaction, the
# declared authority for CORPUS_REGISTRATION mutation, so it is the one place permitted
# to allocate permanent Universal IDs and page ranges.
echo "-- Phase 1/10: ukb build --mint (allocate identity; registry, pages, graph, control tower)"
"$PY" "$HERE/ukb.py" build --mint     || fail "ukb build failed" 1
```

No `--permit`. `register.sh:216` is the single sanctioned minting invocation in the
repository — asserted and tested as such by
`platform/tests/test_verification_purity.py:122-134` and `:378` (*"register.sh must remain
the one minting caller"*). It reaches `commit()` with `permit=None` and is refused at
`ledger_authority.py:449-451`.

**Determination:** `register.sh` Phase 1 cannot complete. Because Phase 1 is followed by
nine further phases each gated on the previous (`|| fail`), the REG-AUTO-001 transaction
terminates at Phase 1 with exit code 1. No corpus registration, no object identity
allocation and no execution declaration can occur.

### 4.3 CLI plumbing exists; the tool it plumbs to does not

```
ukb.py:2497        bp.add_argument("--permit", default=None, help="permit_id from
                   00-BOOK/DATA/allocation-permits.json authorizing …")
ukb.py:2555        xp.add_argument("--permit", default=None, help="permit_id from …")
uga_engine.py:2079 run_p.add_argument("--permit", default=None, help="permit_id from …")
```

Three flags whose help text names a file the repository never produces. `plan()`
(`ledger_authority.py:416-430`) emits the three bindings a permit must quote — `digest`,
`preimage_digest`, `head` — and its docstring states *"issuing a permit is a transcription
of this output rather than an independent act of measurement."* The transcription step has
no implementation: no tool, no template, no documented command, no schema file.

---

## 5. Determination

> Does any production path exist that writes permit records?

**No.**

- Creation: **MISSING**
- Append: **MISSING**
- Update: **MISSING**
- Consumption: **IMPLEMENTED**
- Persistence: **MISSING**

The permit layer is a **half-implemented control**: the enforcement side is complete,
tested and reachable; the issuance side does not exist in any form. Because `permit` is
mandatory with no default (`ledger_authority.py:546`, deliberately — *"A default would
convert the loudest possible failure … into a silent bypass"*), a complete enforcer with no
issuer is not a permissive gap. It is a **total block on every identity-ledger write in the
repository**.

Classification per the Phase-0 scheme: **UNSAFE** — not because a write can occur wrongly,
but because the sole write chokepoint has no reachable success path, and the repository's
registration transaction, corpus identity allocation, object identity allocation and
execution declaration all route through it. This is the defect that currently masks
E1-F1…F7 and E2-F1…F4: those become active the moment an issuance path is supplied.

---

## 6. Residual governance dependency

**Sharply bounded, and stated without being resolved.**

- **Governance-independent and determined here:** that no issuance code exists; that all
  three permit values are refused; that `register.sh:216` passes no permit; that the
  register file is absent. These are existence facts, verified by execution.

- **Governance-dependent, and deliberately not addressed:** what an issuance path should
  do. Creating one requires deciding who may issue, what issuance attests, whether a permit
  is single-use, and how expiry is set. Constraint 4 of this phase forbids introducing
  permits, ratification rules or temporal legitimacy decisions, and every one of those
  questions is inside that prohibition.

Therefore E-4A is **REPRODUCED and fully characterized, but not closable in Phase 0.** It
is the one item in this phase whose *remedy* is governance-dependent even though its
*diagnosis* is not. Recorded as such in
`PHASE0-GOVERNANCE-INDEPENDENT-DETERMINATION.md` §4.

One sub-item is governance-independent and is noted for completeness, not acted on:
E1-F5 (`history` classified in neither set) blocks the `NO_ALLOCATION` path independently of
any issuance decision. Its remedy — classifying an existing top-level ledger key — decides
nothing about authority.

---

## 7. Reproduction integrity

Every measurement in this report is read-only: `grep`, `ls`, `os.path.exists`, `LA.plan`
(`ledger_authority.py:416-430`, writes nothing) and `LA._verify_permit`
(`:432-543`, writes nothing). No file was created, and `register.sh` was **not** executed —
its behaviour is determined from source (`register.sh:216`) plus the measured refusal of
`permit=None`, not from a run that would have mutated the repository.
`git status --porcelain 00-BOOK/DATA/` shows no change.
