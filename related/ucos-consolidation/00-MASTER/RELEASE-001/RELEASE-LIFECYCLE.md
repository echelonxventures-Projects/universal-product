# RELEASE-001 — CANONICAL RELEASE LIFECYCLE

| Field | Value |
|---|---|
| PROGRAMME | `RELEASE-001` — Continuous Release & Evolution Lifecycle |
| AUTHORITY | `NONE — DERIVED TRUTH` |
| BASELINE | `UCOS-BASELINE-001` · SHA `df763bf917943321886c3fc973eac4a1569b6183` |
| GOVERNS | Every future repository change from UCOS-BASELINE-001 onward |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT |

---

## 1. CANONICAL RELEASE LIFECYCLE

Every repository change passes through these states in order:

```
PROPOSED → CLASSIFIED → IMPACT-ANALYZED → APPROVED → IMPLEMENTED → VALIDATED → CERTIFIED → RELEASED
```

| State | Gate | Evidence required |
|---|---|---|
| **PROPOSED** | Entry | Description + justification |
| **CLASSIFIED** | Classification | Exactly one of: new-capability / extension / enhancement / infrastructure / documentation / refactoring / defect / amendment |
| **IMPACT-ANALYZED** | Impact gate | Baseline impact + dependency impact + registry impact confirmed non-destabilizing |
| **APPROVED** | Approval | Operator authorization (or automatic for LOW-risk classified items) |
| **IMPLEMENTED** | Implementation | Code/artifact changes + updated registries + updated traceability |
| **VALIDATED** | Validation gate | verify.sh GREEN + programme gates PASS + tests PASS |
| **CERTIFIED** | Certification gate | UCCEP blocking=none + evidence recorded |
| **RELEASED** | Release gate | Baseline updated (if major) OR evolution version incremented |

---

## 2. RELEASE GOVERNANCE RULES

### 2.1 Every change requires

| Requirement | Enforcement |
|---|---|
| Classification | Must be exactly one type from §1 |
| Dependency analysis | No unresolved dependencies introduced |
| Implementation plan | Follows CAEM-001 mandated form (declaration + engine + gate + self-guards) |
| Validation plan | verify.sh + relevant programme gates |
| Certification evidence | UCCEP gate_exit=0 after change |
| Rollback strategy | Git revert (append-only history, no force-push) |
| Traceability | Source → decision → implementation → validation → certification chain |

### 2.2 Prohibited actions

| Action | Reason |
|---|---|
| Force-push | Destroys baseline immutability |
| Modify frozen corpus | DP-03 violation |
| Duplicate existing capability | Knowledge Once violation |
| Skip verify.sh | Constitutional violation (AC-5) |
| Self-authorize beyond scope | Governance violation |
| Remove committed artifacts | Append-only violation |

---

## 3. VERSIONING POLICY

### 3.1 Version scheme

```
UCOS-BASELINE-NNN    Certified baselines (major milestones)
UCOS-EVO-NNN-WNN     Evolution releases (wave completions)
```

### 3.2 Version history

| Version | SHA | Date | Content |
|---|---|---|---|
| `UCOS-BASELINE-001` | `df763bf9` | 2026-07-30 | First certified baseline (68/68 capabilities) |
| `UCOS-EVO-001-W01` | `91a8b1d`…`ac44985` | 2026-07-30 | Wave-001 completion — the `IMPLEMENT-001` programme. 8 commits · 89 modified · 45 added · 0 removed, plus the evolution record and the producer-convergence regeneration. Registered by `IMPLEMENT-001D` per §5.1 step 5; full record at `EVOLUTION-001` §6.1, post-record findings at §6.2. Lifecycle state **`RELEASED`**. |
| `UCOS-EVO-001-W02` | *(future)* | *(tbd)* | Wave-002 completion |

**`UCOS-EVO-001-W01` against the §4 continuous-validation policy — 7 of 7:**

| Gate | Result |
|---|---|
| Lint + format (`verify.sh` Stage 1) | exit 0 |
| Tests + coverage (Stage 2) | exit 0 · **94.28%** ≥ 90% · 0 failures |
| Coverage report (Stage 3) | exit 0 |
| Governance enforce (Stage 4) | exit 0 · 1193 ≡ 1193 · 0 unregistered · 0 drift |
| Registry validate (Stage 5) | exit 0 · schema + referential integrity PASS |
| `make uccep-gate` | exit 0 · `blocking=none` · `unproven=none` |
| `make closure-gate` | exit 0 · `CLOSED` · `gaps=0` |

All seven are the gates §4 names. Two further gates are **not** in §4's list and do **not** pass:
`rib-gate` (exit 1, single cause) and `rfp-gate` (exit 1, now evaluable rather than aborting).
Both are recorded at `EVOLUTION-001` §6.2 as `W01-F-01` and `W01-F-02` rather than waived; §4 is
unamended.

Baseline advancement (§3.3) is **NOT** claimed: this wave is remediation and finalization, not a
capability milestone. `UCOS-BASELINE-001` stands as the certified baseline.

### 3.3 Baseline advancement criteria

A new baseline (`UCOS-BASELINE-NNN`) is certified when:
- A significant capability milestone is reached
- All blocking gates pass
- verify.sh GREEN
- UCCEP CERTIFIED-PROVISIONAL (or higher) with blocking=none
- Evolution version history records the complete chain from prior baseline

---

## 4. CONTINUOUS VALIDATION POLICY

Every release requires ALL of the following to pass:

| Gate | Command | Exit criteria |
|---|---|---|
| Lint + format | `make lint` / verify.sh Stage 1 | Exit 0 |
| Tests + coverage | `make test` / verify.sh Stage 2 | ≥90% coverage, 0 failures |
| Coverage report | verify.sh Stage 3 | Exit 0 |
| Governance enforce | `ukb.py enforce --pre` / verify.sh Stage 4 | 0 unregistered, 0 drift |
| Registry validate | `ukb.py validate` / verify.sh Stage 5 | Schema + referential integrity PASS |
| UCCEP gate | `make uccep-gate` | blocking=none |
| Closure gate | `make closure-gate` | CLOSED, gaps=0 |

**Continuous integration** (when CI is configured):
- `.github/workflows/ec1-ci.yml` — lint + test + coverage
- `.github/workflows/uccep-gate.yml` — aggregate constitutional gate
- Per-programme gates (rib, uer, uei, umk, uprf, urrc, rfp, etc.)

---

## 5. REPOSITORY OPERATIONAL GUIDE

### 5.1 For any future change

```bash
# 1. Verify baseline is green before starting
./verify.sh

# 2. Implement the change (additive only)

# 3. Verify after implementation
./verify.sh

# 4. Run relevant programme gates
make uccep-gate
make closure-gate

# 5. Record the evolution version
# (append to 00-MASTER/EVOLUTION-001/EVOLUTION-GOVERNANCE-MODEL.md §6)
```

### 5.2 For Wave execution

```bash
# Load the evolution roadmap
cat 00-MASTER/EVOLUTION-001/EVOLUTION-GOVERNANCE-MODEL.md

# Implement wave items following dependency order
# Each item follows: declare → implement → test → validate → certify

# After wave completion
./verify.sh
make uccep-gate
# Update evolution version history
```

### 5.3 For baseline advancement

```bash
# All gates green
./verify.sh
make uccep-gate
make closure-gate

# Create baseline record
# (follow BASELINE-001 pattern in 00-MASTER/BASELINE-NNN/)

# Tag (when upstream configured)
git tag UCOS-BASELINE-NNN
```

---

## 6. DETERMINATION

> **Permanent operational lifecycle ESTABLISHED.**

Every future repository change follows one governed, repeatable lifecycle from proposal through certification. UCOS-BASELINE-001 is the immutable origin. All evolution is additive, traceable, validated, and certified.

This is the last governance meta-program. The governance framework is complete.

---

*END — `RELEASE-001` Canonical Release Lifecycle · `CERTIFIED-PROVISIONAL` · Tier T1 VACANT*
