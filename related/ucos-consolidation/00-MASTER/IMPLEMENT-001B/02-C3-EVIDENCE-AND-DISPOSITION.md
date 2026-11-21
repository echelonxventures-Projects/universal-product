# IMPLEMENT-001B · DELIVERABLE 02 — C-3 EVIDENCE & DISPOSITION

| Field | Value |
|---|---|
| MISSION | `IMPLEMENT-001B` |
| AUTHORITY | `NONE — DERIVED TRUTH` |
| FINDING | **C-3** — *"`verify.sh` Stage 5 silently degrades"* (`IMPLEMENT-001A` D00 §5.3), classified **BLOCKING** |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT |

---

## 1. DETERMINATION

> ### C-3 is **VALID as to fact** and **ALREADY SATISFIED as to disposition**.
>
> It is a **pre-existing** condition, already registered as `UCCEP-F-006`, already assigned to
> `WP-UCCEP-004`, already tracked as operator action `OA-3`, and already dispositioned
> **`blocking: false`, priority P2**.
>
> `IMPLEMENT-001A` classified it **BLOCKING**, contradicting the repository's own register.
> That classification is **REJECTED**.

---

## 2. PHASE 1 — EVIDENCE RECONSTRUCTION

### 2.1 The degradation is real — reproduced by blocking the import

```
PYTHONPATH=<jsonschema-blocker> .ec1-venv/bin/python 00-BOOK/tools/ukb.py validate
  → "jsonschema not installed — ran structural checks only
     (pip install jsonschema for full schema validation)."
  → "VALIDATION PASSED — 1193 artifacts, append-only page ledger intact,
     referential integrity OK"
  → exit 0
```

**Reproduced. Stage 5 reports PASS having validated no schema.**

### 2.2 Exact mechanism

| Location | Fact |
|---|---|
| `00-BOOK/tools/ukb.py:1723` | `# schema validation (optional)` |
| `:1724-1725` | `try: import jsonschema  # type: ignore` |
| `:1729-1731` | `jsonschema.validate(a, schema)` / `except jsonschema.ValidationError` |
| `:1732` | `print("jsonschema validation: ran.")` |
| **`:1733-1735`** | `except ImportError:` → prints *"ran structural checks only"* → **continues, no non-zero exit** |
| `:21` | self-declared: *"Validate emitted DATA against the JSON schemas (**if jsonschema present**)"* |
| `:25` | self-declared: *"Standard library only (**jsonschema optional** for `validate`)"* |

### 2.3 The dependency is undeclared — confirmed, and structurally so

| Location | Fact |
|---|---|
| `pyproject.toml:27-32` | `dev = ["pytest==8.3.4", "pytest-cov==6.0.0", "coverage==7.15.2", "ruff==0.8.4"]`. `grep jsonschema pyproject.toml` → **0 matches** |
| `scripts/ucos-env.sh:104-120` | `ucos_expected_deps()` **derives** the expected set by parsing `[project.optional-dependencies].dev`. There is no hardcoded list, so it **structurally cannot** expect `jsonschema` until `pyproject.toml` declares it |
| `.github/workflows/ucos-registration-gate.yml:39-40` | `- name: Install optional validators` / `run: pip install jsonschema \|\| true` — install failure is swallowed |

It passes locally only because `jsonschema 4.26.0` is present in `.ec1-venv` from an earlier
ad-hoc install. **One edit fixes both** — adding a pin to `pyproject.toml` makes
`ucos_expected_deps()` pick it up automatically.

### 2.4 ⛔ The evidence C-3 did not gather — this is NOT this change set

```
git diff --stat HEAD -- 00-BOOK/tools/ukb.py
  → (empty)

diff <(git show HEAD:00-BOOK/tools/ukb.py | grep -n jsonschema) \
     <(grep -n jsonschema 00-BOOK/tools/ukb.py)
  → IDENTICAL
```

**`00-BOOK/tools/ukb.py` is byte-identical to committed `HEAD`.** The `ImportError` swallow
already existed at `df763bf9`, at the same line numbers. The change set did not introduce it,
did not touch it, and did not worsen it.

What the change set *did* do: wire `ukb.py validate` into `verify.sh` as Stage 5, where it had
run in **no** gate before. That is a strict improvement — it moved a validator from "run by
nobody" to "run by the canonical entry point", with a known, pre-registered limitation.

---

## 3. PHASE 2 — CONSTITUTIONAL REVIEW

### 3.1 The finding is already registered — verbatim

`00-MASTER/UCCEP-000000/uccep-bindings.json`, `findings[]`:

```json
{
  "id": "UCCEP-F-006",
  "title": "ukb validate degrades to structural-only checks when jsonschema is absent",
  "class": "DEGRADED-VALIDATION",
  "evidence": "python3 00-BOOK/tools/ukb.py validate prints \"jsonschema not installed —
               ran structural checks only\" and still exits 0. The CI registration workflow
               installs jsonschema with `|| true`, so schema validation is silently optional
               there too.",
  "violates": ["PR-14 Universal Validation"],
  "owner": "00-BOOK/tools/ukb.py · .github/workflows/ucos-registration-gate.yml",
  "disposition": "REGISTERED",
  "work_package": "WP-UCCEP-004",
  "blocking": false,
  "note": "A validation gate that silently reduces its own scope reports PASS for a weaker
           proposition than the one claimed. Recorded so the reduction is visible rather
           than silent."
}
```

The registered `evidence` field is **the same evidence C-3 presents**, including the
`|| true` observation. C-3 rediscovered a finding the repository had already recorded, with the
same reasoning, and then assigned it a **more severe** classification than its owner had.

### 3.2 The work package exists

```
WP-UCCEP-004 | Make schema validation mandatory rather than silently optional
             | owner: 00-BOOK/tools/ukb.py · .github/workflows/ucos-registration-gate.yml
             | discharges: ['UCCEP-F-006']
```

### 3.3 The operator action exists, and is **non-blocking P2**

`00-MASTER/UCCEP-000006/07-OPERATOR-ACTION-REGISTER.md:22`, verbatim
(header at `:19` — `# | Action | Owner | Discharges | Priority | Blocking | Status`):

```
| OA-3 | Install `jsonschema` so `ukb validate` runs full schema validation
       | `00-BOOK/tools/ukb.py` · CI workflow | `UCCEP-F-006` · `WP-UCCEP-004`
       | P2 | No | OPEN |
```

Corroborated at `00-MASTER/UCCEP-000006/evidence/findings-dispositions.txt:6`:

```
UCCEP-F-006 | disposition=REGISTERED | blocking=False | wp=WP-UCCEP-004
```

And at `00-MASTER/UCCEP-000006/03-REPOSITORY-INTEGRITY-REPORT.md:46`:

> *"Schema validation scope | **DEGRADED** — structural-only (`jsonschema` absent;
> `UCCEP-F-006` / `WP-UCCEP-004`, **pre-existing, non-blocking**)"*

> **The located owner has already determined this is non-blocking.** `X-9` of the
> implementation boundary provides: *"No cross-programme edits"* — reclassifying another
> programme's finding from non-blocking to blocking is precisely such an edit.
> `IMPLEMENT-001A` had no authority to escalate it.

### 3.4 The real conflict — and it is genuine

Two located instruments disagree, and neither yields:

| Instrument | Position |
|---|---|
| `00-BOOK/tools/ukb.py:21, :25` | jsonschema is **optional** by declared design |
| `00-MASTER/RELEASE-001/RELEASE-LIFECYCLE.md` §4 | `\| Registry validate \| ukb.py validate / verify.sh Stage 5 \| **Schema** + referential integrity PASS \|` — schema PASS is a stated **release exit criterion** |

A structural-only run cannot evidence "Schema … PASS". This conflict is real and is recorded in
the Constitutional Conflict Matrix (Deliverable 04, `CF-03`). It does **not** make C-3 blocking —
`RELEASE-001` §4 governs *release*, and no release is being asserted — but it does mean
`WP-UCCEP-004` must close before any release claim.

Note also: `CAEM-001/05:53` (S-2) already required closing `OA-3` as part of the same act that
wired `ukb validate` into `verify.sh`. **Half of S-2 was performed** (the `verify.sh` wiring);
the `OA-3` half and the `ucos-registration-gate.yml` half were not.

### 3.5 Identifier collision noted

`00-MASTER/IMR-0000/12-ORCHESTRATION-ARCHITECTURE.md:24` defines an unrelated `OA-3`
(an epoch-binding rule). Two distinct `OA-3`s exist in the corpus. Recorded as `CF-05`.

---

## 4. PHASE 3 — CLASSIFICATION

> ## **TOOLING LIMITATION** + **ALREADY SATISFIED** (registered, dispositioned, work-packaged)

Explicitly **not**: introduced by this change set (the file is byte-identical to HEAD), a new
finding (`UCCEP-F-006` predates it), or blocking (its owner determined `blocking: false`, P2).

---

## 5. PHASE 4 — DISPOSITION

> # **REJECT** as a new blocking finding
> # **DEFER** the substance to the existing `WP-UCCEP-004` / `OA-3`

| Dimension | Determination |
|---|---|
| **Evidence** | Degradation reproduced (exit 0, "structural checks only") · `git diff --stat HEAD -- 00-BOOK/tools/ukb.py` **empty** · jsonschema line numbers identical at HEAD and working tree · `UCCEP-F-006` `disposition=REGISTERED, blocking=false, wp=WP-UCCEP-004` · `OA-3` P2, Blocking **No**, OPEN · `03-REPOSITORY-INTEGRITY-REPORT.md:46` *"pre-existing, non-blocking"* |
| **Constitutional justification** | The finding is owned by `00-BOOK/tools/ukb.py` and `.github/workflows/ucos-registration-gate.yml` and was dispositioned non-blocking by `UCCEP-000000`. `X-9` forbids cross-programme edits to another programme's findings; escalating a `blocking: false` finding to BLOCKING is such an edit. `PR-14 Universal Validation` is the violated principle and is already recorded as violated. |
| **Implementation impact** | **2 lines**, when `WP-UCCEP-004` executes: (1) add `jsonschema==<pin>` to `pyproject.toml:27-32` — `ucos_expected_deps()` then requires it automatically; (2) drop `\|\| true` from `ucos-registration-gate.yml:40`. Optionally make the `ImportError` branch fail-closed, which is the work package's actual title. |
| **Repository impact** | None pending. Locally `jsonschema 4.26.0` is installed, so Stage 5 runs in full today (`"jsonschema validation: ran."` observed in all three `verify.sh` runs this mission). |
| **Dependency impact** | Adds one declared, pinned dev dependency. `ucos_expected_deps()` requires no change. |
| **Certification impact** | **NONE as a blocker.** `verify.sh` PASSES 5/5 with schema validation actually running. C-3 is removed from the blocking set. It **does** bar an unqualified *release* claim under `RELEASE-001` §4 until `WP-UCCEP-004` closes — recorded, not blocking. |

### 5.1 Why this is DEFER and not FIX

The mission mandate is explicit: *"Only evidence-backed findings proceed to remediation"* and
*"No finding shall be accepted solely because it appears in a report."* The substance here is
sound but it is **not this mission's finding and not this mission's to fix** — it has a located
owner, a work package, and a priority already assigned by that owner. Re-opening it under a new
identifier would create the duplicate-finding condition `X-9` exists to prevent.

The fix is genuinely 2 lines and genuinely worth doing. It is sequenced in Deliverable 06 as
`RB-03` under its **existing** identifier `WP-UCCEP-004` / `OA-3`, not a new one.

---

## 6. SUMMARY

| Claim in `IMPLEMENT-001A` C-3 | Verdict |
|---|---|
| `cmd_validate` swallows `ImportError` and exits 0 | ✓ **REPRODUCED** at `ukb.py:1733-1735` |
| `jsonschema` absent from `pyproject.toml` dev extras | ✓ **CONFIRMED** — 0 matches |
| `ucos_expected_deps()` will never install it | ✓ **CONFIRMED** — it parses only `dev` |
| `ucos-registration-gate.yml:40` still `\|\| true` | ✓ **CONFIRMED** |
| *"a clean bootstrap validates no schema"* | ✓ **REPRODUCED** by blocking the import |
| Introduced / worsened by this change set | ⛔ **DISPROVED** — `ukb.py` byte-identical to HEAD |
| A **new** finding | ⛔ **DISPROVED** — `UCCEP-F-006`, registered, with evidence text matching C-3's |
| **BLOCKING** | ⛔ **DISPROVED** — owner determined `blocking: false`, `OA-3` P2 "No" |
| *"`OA-3` is not closed"* | ✓ **CORRECT** — `OA-3` is OPEN, and that is the accurate framing |

> **What survives C-3:** nothing new. A correct restatement of `UCCEP-F-006` / `OA-3` /
> `WP-UCCEP-004`, mis-escalated to BLOCKING. The 2-line fix proceeds under its existing
> identifier.

---

*END — `IMPLEMENT-001B` Deliverable 02 · AUTHORITY = NONE · `CERTIFIED-PROVISIONAL` · Tier T1 VACANT*
