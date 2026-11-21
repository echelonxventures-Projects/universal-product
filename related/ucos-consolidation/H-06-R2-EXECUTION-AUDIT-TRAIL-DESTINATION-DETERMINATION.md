# H-06 R-2 EXECUTION AUDIT TRAIL DESTINATION DETERMINATION

## 1. Authority

NONE — DETERMINATION ONLY. No policy selected. No implementation authorized.
Baseline: HEAD `1f869865` · branch `integration/recovery-001`

---

## 2. Question

Where must EXECUTION-mode gate invocation audit records be stored, using existing
UCOS ownership surfaces, consistent with the Knowledge Once Principle?

---

## 3. Existing Candidate Surfaces

| Surface | Owner | Purpose | Suitable for EXECUTION audit? |
|---|---|---|---|
| `.runtime/governance/enforcement-audit.json` | `governance_telemetry.py` (`append_audit`) | Enforcement gate invocation telemetry | YES — existing pattern |
| `.runtime/governance/sync-audit.json` | `governance_telemetry.py` | Registration sync telemetry | PARTIAL — sync-specific |
| `.runtime/governance/certification-audit.json` | `governance_telemetry.py` | Certification invocation telemetry | PARTIAL — cert-specific |
| `00-BOOK/DATA/` (historical location) | FORBIDDEN — `TelemetryPathError` raised on write attempt | Previously hosted audit logs | NO — structurally forbidden |
| Per-programme `evidence/` dirs | gitignored, per programme | Programme-level evidence bundles | PARTIAL — programme-scoped only |
| `generated-artifact-registry.json` | UCOS-GENERATED-ARTIFACT-REGISTRY-001 | Artifact registration | NO — registration, not invocation audit |
| `mutation-governance-boundary.json` | UCOS-MUTATION-GOVERNANCE-BOUNDARY-001 | Class governance declaration | NO — declaration, not invocation audit |

---

## 4. Ownership Analysis

`00-BOOK/tools/governance_telemetry.py` is the canonical single writer for all runtime
governance telemetry. Its architecture is explicit:

- **ONE location:** `.runtime/governance/` — git-ignored, per-clone, never tracked
- **ONE writer:** `append_audit()` — the only function that persists an audit run
- **ONE sequence:** monotonic `seq` assigned only here
- **FROZEN path:** `forbid_data_telemetry()` + `TelemetryPathError` make the repository
  structurally incapable of writing audit records into `00-BOOK/DATA`

The module was created precisely to consolidate what were three separate per-engine audit
appenders into one. It already handles: enforcement invocations (`ukb.py`), sync
invocations (`ukbx.py`), and certification invocations (`ukbx.py`). The pattern is:
one log file per invocation class, all under `.runtime/governance/`.

An EXECUTION-mode audit requirement maps directly onto this existing pattern. A new log
filename (e.g. `execution-audit.json`) under `.runtime/governance/` written by
`append_audit()` would be consistent with the existing architecture, require no new
module, no new location, and no new sequence authority.

---

## 5. Canonical Destination Determination

**EXISTING SURFACE IDENTIFIED**

Canonical destination: `.runtime/governance/` via `governance_telemetry.append_audit()`

Owner: `00-BOOK/tools/governance_telemetry.py`
Location: `.runtime/governance/<execution-class>-audit.json`
Append authority: `append_audit()` — sole writer, already enforced
Validation authority: `forbid_data_telemetry()` — prevents writes to `00-BOOK/DATA`
Gitignore status: `.runtime/` is gitignored — audit records are per-clone operational
state, not Repository Truth. This is the documented and correct lifecycle.

This determination requires no new registry, no new authority surface, and no new module.
It is an additive invocation of the existing telemetry writer for a new audit class.

Note: adding a new audit class (`execution-audit.json`) to `governance_telemetry.py`
is a code change and requires implementation authorization. This determination only
identifies the canonical owner and destination. It does not authorize implementation.

---

## 6. Governance Impact

**Does not affect freeze.**

R-2 was identified as non-blocking for the H-06 Option A/B decision. It is required
before any programme declares EXECUTION mode. No programme currently holds an EXECUTION
mode declaration. The canonical destination is now identified; R-2 is resolved.

Updated R-2 status: **RESOLVED — existing surface identified.**

---

## 7. Remaining Unknowns

None arising from R-2.

Remaining H-06 ratification sub-decisions:

| ID | Item | Status |
|---|---|---|
| R-1 | GP-6 collision verification | RESOLVED — no collision |
| R-2 | EXECUTION audit trail destination | RESOLVED — `.runtime/governance/` via `governance_telemetry.append_audit()` |
| R-3 | `gate_mode` field name confirmation | OPEN |
| R-4 | Grandfathering policy for migration window | OPEN |

Sequence advances to R-3.

---

No implementation authorized.
No governance option selected.
R-2 evidence determination complete.
