# B-01 — Implementation Plan

**Predecessors:** `B-01-BIRTH-SCOPE-GOVERNANCE-DETERMINATION.md` · `00-MASTER/UOBC-000001/birth-scope-policy.json` (specification, empirically validated)
**Posture:** PLAN. Read back as the change contract before implementation.

---

## 1. Files

### Created
| Path | Role |
|---|---|
| `engine/object_birth/scope.py` | Policy model, ordered classification, six law checks, public evaluation API |
| `engine/tests/unit/test_birth_scope.py` | Tests — positive, negative, refusal, determinism |

### Modified
| Path | Change | Constraint |
|---|---|---|
| `engine/object_birth/gate.py` | Measure the six BSP laws alongside the eight UOBC laws; one report, one exit code | **No new stage.** The existing UOBC stage in `verify.sh` gains coverage; `verify.sh` and the UVI stage registry are untouched |
| `engine/object_birth/__init__.py` | Export the new public surface | additive |
| `pyproject.toml` | none required | `engine.object_birth` is already in both coverage enumerations |

### Not modified — stated so the boundary is explicit
`verify.sh` · `uvi-declaration.json` · `birth-ledger.json` · `uobc-birth-contract.json` · UGA surfaces · `id-ledger.json`. **No registry mutation, no identifier minted, no birth record generated.**

---

## 2. Public capability (mandate Step 2)

```
evaluate(path) -> Verdict(path, object_kind, birth_required, verdict, reason, authority)
```

| Question | Answer |
|---|---|
| Does this object require birth? | `object_kind` → `birth_required` |
| If yes, does valid birth exist? | ledger lookup via `subject_resolution` |
| If no, is absence correct? | `enforcement` = `MANDATORY_ABSENCE` / `NOT_REQUIRED` / `GOVERNED_ELSEWHERE` |

**Verdicts:**
- `PASS` — born where required; absent where forbidden; not required
- `FAIL` — a derived object is born · a birth names a missing subject · an unknown kind
- `EXCEPTION` — birth required, not present, and adoption is `DEFERRED` naming a gap. **The authorized reason is the gap id.** This is what keeps G11 disclosed instead of silently tolerated.

---

## 3. No hard-coded reality

- No `object_kind`, path, selector, floor or gap id appears in `scope.py`.
- Selector *operators* are generic (`path_prefix`, `basename`, `uga_object_class`, `catch_all`); the *values* live in the policy.
- Kind order comes from the file, not from code.
- A new kind is a JSON row. A new selector operator is the only change that would touch code, and `BSP-L-01` refuses a selector naming an operator that is not implemented.

---

## 4. Risks

| # | Risk | Control |
|---|---|---|
| R-1 | Gate closes on the deferred population | `EXCEPTION` verdict + `adoption: DEFERRED` + gap id; `BSP-L-05` refuses only *undisclosed* gaps. Validated: 0 unresolved, all floors hold |
| R-2 | Reading three registries slows the UOBC stage | All three are already parsed by gates in the same run; stage stays `READ_ONLY` |
| R-3 | Floors drift from reality | `BSP-L-06` fails closed on decrease; floors measured, zero slack |
| R-4 | Extending `gate.py` breaks the existing 8-law report | Additive section; existing `measure()` keys preserved; existing UOBC tests must still pass unchanged |

---

## 5. Validation

`ruff check` · `ruff format --check` · new tests · existing `test_object_birth` unchanged · `./verify.sh --change` · `--integration` · `--full`.

**Determinism:** no clock, no network, no subprocess, no write. Two runs over one tree produce identical bytes.

---

## 6. Order

1. `scope.py` (model → classification → checks → public API)
2. Tests
3. Gate integration
4. Isolated gate run must be green before verification sequence
5. Four verification modes
6. Evidence report → certification → tracker

No step begins before the one above passes.

---

*End of B-01-IMPLEMENTATION-PLAN.md*
