# ENFORCEMENT CLOSURE MATRIX

**Artifact id:** ENFORCEMENT-CLOSURE-MATRIX  
**Authority:** NONE — DERIVED TRUTH. This document legislates nothing, owns no gate, creates no identifier and changes no production logic. It is a measurement of repository state.  
**Measured at:** HEAD `446f8a0f6d95c42ab85ba70c83c6122ccfab107a` on `integration/recovery-001`  
**Method:** read-only. The enforcement plane is enumerated by importing UEC-000001 (`engine/enforcement_closure`) in-process and reading its discovery rules over `git ls-files`; the requirement plane from `00-MASTER/UAKOS-CLOSURE-009/requirements.json`; the law plane by parsing every `laws` array under `00-MASTER/`; the certification plane by enumerating persisted certification artifacts and Markdown assertions. No file in the repository was modified.

## 1. Predicates

Each column is a separate falsifiable question. They are deliberately not collapsed: an artifact can be declared and unreachable, reachable and unexecuted, executed and uncertified. Collapsing any two would hide exactly the defect class this matrix exists to expose.

| Column | Question | YES requires |
|---|---|---|
| **Declared** | Is the artifact named in a machine-readable governed register? | Presence in `governed_enforcement`, a `laws` array, `requirements.json`, or an equivalent parseable record. A mention in prose is `PARTIAL`, never `YES`. |
| **Reachable** | Could anything load or run it? | For an engine or gate: at least one invoker naming it in a form that could execute it (dotted module path or file path — a bare package name in prose does not count). For a declaration: at least one module that loads it. For a law: a `check` resolving to an implemented predicate. For a requirement: a populated implementation tier. |
| **Executed** | Does something run it automatically? | A CI workflow that fires on push/pull_request, or a `verify.sh` stage that is not elided. A target reachable only by a human typing `make X` is `NO`. A stage that may be served from cache is `PARTIAL`. |
| **Measured** | Does anything observe its state and record it? | A test that names it, or a persisted evidence/digest record. Naming is the necessary condition only; it does not prove a mutant would be killed. |
| **Certified** | Is it covered by a certification identity a gate validates? | A minted digest AND an executed gate that re-derives and compares it. Identity that exists but is never re-verified is `PARTIAL`. |

## 2. Population

| § | Population | Artifacts | Declared | Reachable | Executed | Measured | Certified |
|---|---|---|---|---|---|---|---|
| §A | REQUIREMENT — derived registry (RR-*) | 549 | 549 | 314 | 0 | 216 | 241 |
| §B | REQUIREMENT — prose universe (REQ-NN) | 49 | 0 | 0 | 0 | 0 | 0 |
| §C | LAW | 204 | 204 | 108 | 94 | 118 | 121 |
| §D | ENGINE — gate engines | 39 | 39 | 33 | 24 | 21 | 12 |
| §E | GATE — module gates | 9 | 9 | 9 | 8 | 9 | 8 |
| §F | GATE — Makefile gate targets | 54 | 54 | 53 | 39 | 9 | 34 |
| §G | GATE — verify.sh stages | 18 | 18 | 18 | 18 | 2 | 0 |
| §H | WORKFLOW | 32 | 32 | 32 | 32 | 12 | 12 |
| §I | CERTIFICATION OBJECT — governed declarations | 20 | 20 | 17 | 16 | 15 | 17 |
| §J | CERTIFICATION OBJECT — persisted JSON | 146 | 146 | 145 | 2 | 144 | 1 |
| §K | CERTIFICATION OBJECT — Markdown assertions | 141 | 0 | 47 | 0 | 0 | 0 |
|  | **TOTAL** | 1261 | 1071 | 776 | 233 | 546 | 446 |

Counts are `YES` only; `PARTIAL` is excluded from every column, which is why the certification columns are far below the artifact totals rather than near them.

### Independent cross-check against the live gate

`python -m engine.enforcement_closure.gate --json` at this HEAD reports verdict **OPEN**, 13 laws measured, 13 holding, 0 refused, over 172 enforcement artifacts and 6751 tracked paths, declaration digest `cffb41b32c9eba5b`. This matrix reproduces that population exactly (172 artifacts across §D–§I) and extends it with the requirement, law and certification-object planes UEC does not enumerate.

The gate reporting **OPEN** is not a claim that the enforcement set is closed. Every UEC law holds because each ratcheted class is *at* its declared ceiling, not at zero — the ceilings record standing findings rather than their absence:

| Ratchet | Declared ceiling | Measured |
|---|---|---|
| artifacts_with_one_invocation_plane | 16 | 16 |
| declarations_no_code_consumes | 3 | 3 |
| declarations_with_uniform_identity | 5 | — |
| declarations_without_a_certification_identity | 0 | 0 |
| discovery_floor_total | 127 | — |
| engines_with_no_invoker | 6 | 6 |
| engines_without_a_test | 18 | 18 |
| governed_artifacts | 172 | — |

### Two qualifications on the cross-check above

**The measured tree is not HEAD.** A large body of uncommitted work is present, including the whole of `engine/construct/`, `engine/enforcement_closure/` and `engine/recursive_knowledge/` staged but not committed. Every verdict quoted in this matrix is a property of this working tree. See gap X-16.

**A live mutant that disables UEC-L-08 is present in the working tree, and it survives.** `engine/enforcement_closure/contract.py` currently has `certification_identity_exists` replaced by `return []  # MUTANT`. The gate still reports OPEN and UEC-L-08 still reports HOLDS, because the class it measures is empty at this state — 0 offenders against a ceiling of 0. A working UEC-L-08 and a deleted UEC-L-08 are therefore observationally identical here. This was not introduced by this measurement and is absent from HEAD; it is reported rather than reverted. See gap X-15.

## §A — REQUIREMENT — derived registry (RR-*)

549 artifacts.

| Artifact | Type | Declared | Reachable | Executed | Measured | Certified | Evidence |
|---|---|---|---|---|---|---|---|
| RR-AF-3 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-AMC-01 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 8/9 |
| RR-AMC-02 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-AMC-03 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-AMC-04 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-AMC-05 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-AMC-06 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-AMC-07 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-AMC-08 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-AMC-09 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-AMC-10 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-AMC-11 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 4/9 |
| RR-AMR-01 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 8/9 |
| RR-AMR-02 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-AMR-03 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-AMR-04 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-AMR-05 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-AMR-06 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-AMR-07 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-AMR-08 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-AMR-09 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-AMR-10 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-AMR-11 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-AMR-12 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-AMR-13 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-AMR-14 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-APPLICATION-000 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-APPLICATION-001 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 8/9 |
| RR-APPLICATION-002 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-APPLICATION-003 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 7/9 |
| RR-APPLICATION-004 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 4/9 |
| RR-APPLICATION-005 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 8/9 |
| RR-APPLICATION-006 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-APPLICATION-007 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-APPLICATION-008 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-APPLICATION-009 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-APPLICATION-010 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-APPLICATION-011 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 4/9 |
| RR-APPLICATION-012 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-APPLICATION-013 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 8/9 |
| RR-APPLICATION-014 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-APPLICATION-015 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-APPLICATION-016 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 5/9 |
| RR-APPLICATION-017 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-APPLICATION-018 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 5/9 |
| RR-APPLICATION-019 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-APPLICATION-020 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-ARCH-AI-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-ARCH-API-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-ARCH-APPLICATION-001 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-ARCH-BCDR-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-ARCH-CERT-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-ARCH-DATA-001 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-ARCH-DEPLOYMENT-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M2 · tiers 3/9 |
| RR-ARCH-EVENT-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-ARCH-GAP-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · REJECTED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M0 · tiers 1/9 |
| RR-ARCH-GOV-001 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 4/9 |
| RR-ARCH-INFRA-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-ARCH-INFRASTRUCTURE-001 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-ARCH-INTEGRATION-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-ARCH-MASTER-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-ARCH-OBS-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-ARCH-OPS-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-ARCH-PLATFORM-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M2 · tiers 3/9 |
| RR-ARCH-PRODUCTION-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M2 · tiers 3/9 |
| RR-ARCH-QUALITY-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-ARCH-RUNTIME-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-ARCH-SECURITY-001 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 6/9 |
| RR-ARCH-SERVICE-001 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-ARCH-TEST-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-ARCH-WORKFLOW-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-ARCH-XXX-000 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-CEP-000 | requirement | YES | NO | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M2 · tiers 6/9 |
| RR-CEP-001 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 7/9 |
| RR-CEP-002 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 8/9 |
| RR-CEP-003 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M5 · tiers 7/9 |
| RR-CEP-004 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · REJECTED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M0 · tiers 4/9 |
| RR-CEP-005 | requirement | YES | NO | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M2 · tiers 5/9 |
| RR-CEP-006 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M5 · tiers 7/9 |
| RR-CEP-007 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M5 · tiers 7/9 |
| RR-CEP-008 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · REJECTED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M0 · tiers 5/9 |
| RR-CEP-009 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M5 · tiers 7/9 |
| RR-CEP-010 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 5/9 |
| RR-CEP-011 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-DATA-000 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-DATA-001 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 8/9 |
| RR-DATA-002 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-DATA-003 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 5/9 |
| RR-DATA-004 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 5/9 |
| RR-DATA-005 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 8/9 |
| RR-DATA-006 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-DATA-007 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-DATA-008 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-DATA-009 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 4/9 |
| RR-DATA-010 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-DATA-011 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-DATA-012 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-DATA-013 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-DATA-014 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 8/9 |
| RR-DATA-015 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 4/9 |
| RR-DATA-016 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-DATA-017 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-DATA-018 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 5/9 |
| RR-DATA-027 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-DF-2 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-DMC-01 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 6/9 |
| RR-DMC-02 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-DMC-03 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-DMC-04 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-DMC-05 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-DMC-06 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-DMC-07 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-DMC-08 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-DMC-09 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-DMC-10 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-DMR-01 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-DMR-02 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-DMR-03 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-DMR-04 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-DMR-05 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-DMR-06 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-DMR-07 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-DMR-08 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-DMR-09 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-DMR-10 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M5 · tiers 4/9 |
| RR-DMR-11 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-DMR-12 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M5 · tiers 4/9 |
| RR-EC-3-AP-1 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-EC-3-AP-2 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-EC-3-AP-3 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 7/9 |
| RR-EC-3-AP-4 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 7/9 |
| RR-EC-3-AP-5 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 7/9 |
| RR-EC3-B10-U01 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 6/9 |
| RR-EC3-B10-U02 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B10-U03 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B10-U04 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B10-U05 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B10-U06 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B10-U07 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B10-U08 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B10-U09 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B10-U10 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B10-U11 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B10-U12 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-EC3-B11-U01 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 8/9 |
| RR-EC3-B11-U02 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B11-U03 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B11-U04 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B11-U05 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B11-U06 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B11-U07 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B11-U08 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B11-U09 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B11-U10 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B11-U11 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B11-U12 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B11-U13 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-EC3-B12-U01 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 8/9 |
| RR-EC3-B12-U02 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B12-U03 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B12-U04 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B12-U05 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B12-U06 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B12-U07 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B12-U08 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B12-U09 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-EC3-B12-U10 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B12-U11 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-EC3-B12-U12 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 4/9 |
| RR-EC3-B12-U13 | requirement | YES | NO | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M2 · tiers 4/9 |
| RR-EC3-B13-G01 | requirement | YES | NO | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M2 · tiers 4/9 |
| RR-EC3-B13-P01 | requirement | YES | NO | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M2 · tiers 4/9 |
| RR-EC3-B13-P02 | requirement | YES | NO | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M2 · tiers 4/9 |
| RR-EC3-B13-U01 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 8/9 |
| RR-EC3-B13-U02 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-EC3-B13-U03 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-EC3-B13-U04 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-EC3-B13-U05 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-EC3-B13-U06 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-EC3-B13-U07 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-EC3-B13-U08 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-EC3-B13-U09 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-EC3-B13-U10 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-EC3-B13-U11 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-EC3-B13-U12 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-EL-1 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-EPIC-DOC-002 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 3/9 |
| RR-EPIC-DOC-003 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 3/9 |
| RR-EPIC-GOV-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-EPIC-OBS-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-EPIC-PLAT-002 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · REJECTED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M0 · tiers 1/9 |
| RR-EPIC-PLAT-003 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 4/9 |
| RR-EPIC-RTE-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-EPIC-RTE-002 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 4/9 |
| RR-EPIC-RTE-003 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 4/9 |
| RR-EPIC-UKDA-002 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 4/9 |
| RR-EPIC-UKDA-003 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 4/9 |
| RR-EPIC-UKDA-004 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 3/9 |
| RR-EPIC-VAL-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-EPIC-VAL-002 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M5 · tiers 5/9 |
| RR-EPIC-VAL-003 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 4/9 |
| RR-EPIC-XXX-000 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-GOV-000 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 5/9 |
| RR-GOV-001 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-GOV-002 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M5 · tiers 7/9 |
| RR-GOV-003 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 5/9 |
| RR-GOV-004 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M5 · tiers 6/9 |
| RR-GOV-005 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M5 · tiers 6/9 |
| RR-GOV-006 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M5 · tiers 6/9 |
| RR-GOV-007 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · REJECTED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M0 · tiers 1/9 |
| RR-GOV-008 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-GOV-009 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-GOV-010 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · REJECTED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M0 · tiers 1/9 |
| RR-ICAP-01 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 6/9 |
| RR-ICAP-02 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 2/9 |
| RR-ICAP-03 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 6/9 |
| RR-ICAP-04 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M4 · tiers 4/9 |
| RR-ICAP-05 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 2/9 |
| RR-ICMP-01 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-ICMP-02 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-ICMP-03 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M4 · tiers 4/9 |
| RR-ICMP-04 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-ICMP-05 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M5 · tiers 4/9 |
| RR-ICNW-01 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-ICNW-02 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-ICNW-03 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-ICNW-04 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-ICNW-05 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M5 · tiers 4/9 |
| RR-INFRASTRUCTURE-000 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-INFRASTRUCTURE-001 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 8/9 |
| RR-INFRASTRUCTURE-002 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-INFRASTRUCTURE-003 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-INFRASTRUCTURE-004 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-INFRASTRUCTURE-005 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 8/9 |
| RR-INFRASTRUCTURE-006 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 8/9 |
| RR-INFRASTRUCTURE-007 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-INFRASTRUCTURE-008 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-INFRASTRUCTURE-009 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-INFRASTRUCTURE-010 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-INFRASTRUCTURE-011 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-INFRASTRUCTURE-012 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-INFRASTRUCTURE-013 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 8/9 |
| RR-INFRASTRUCTURE-014 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 7/9 |
| RR-INFRASTRUCTURE-015 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 4/9 |
| RR-INFRASTRUCTURE-016 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-INFRASTRUCTURE-017 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 4/9 |
| RR-INFRASTRUCTURE-018 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 5/9 |
| RR-ISTO-01 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-ISTO-02 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-ISTO-03 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-ISTO-04 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-ISTO-05 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M5 · tiers 4/9 |
| RR-MCP-000 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-MCP-001 | requirement | YES | NO | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M2 · tiers 4/9 |
| RR-MCP-002 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 7/9 |
| RR-MCP-003 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 7/9 |
| RR-MCP-004 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · REJECTED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M0 · tiers 3/9 |
| RR-MCP-005 | requirement | YES | NO | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M2 · tiers 4/9 |
| RR-MCP-006 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-MCP-007 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-MCP-008 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-MCS-000 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · REJECTED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M0 · tiers 3/9 |
| RR-MEP-00 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-MEP-01 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-MEP-02 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 7/9 |
| RR-MEP-03 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 7/9 |
| RR-MEP-04 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 7/9 |
| RR-MEP-05 | requirement | YES | NO | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M2 · tiers 4/9 |
| RR-MEP-06 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-MEP-07 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-MEP-08 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-MEP-09 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-MEP-10 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-MEP-11 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-PL-F2 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-PLATFORM-000 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-PLATFORM-001 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 4/9 |
| RR-PLATFORM-002 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-PLATFORM-003 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-PLATFORM-004 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-PLATFORM-005 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-PLATFORM-006 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 7/9 |
| RR-PLATFORM-007 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-PLATFORM-008 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 5/9 |
| RR-PLATFORM-009 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-PLATFORM-010 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-PLATFORM-011 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 3/9 |
| RR-PLATFORM-012 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-PLATFORM-013 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-PLATFORM-014 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-PLATFORM-015 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-PLATFORM-016 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-PLATFORM-017 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-PLATFORM-018 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-Phase-000 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-Phase-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-Phase-002 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · REJECTED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M0 · tiers 2/9 |
| RR-Phase-003 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-Phase-004 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-Phase-005 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-Phase-006 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-Phase-020 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-Phase-021 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-Phase-024 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-Phase-025 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-Phase-040 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-RL-F2 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-RUNTIME-000 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-RUNTIME-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-RUNTIME-002 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-RUNTIME-003 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-RUNTIME-004 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-RUNTIME-005 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · REJECTED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M0 · tiers 1/9 |
| RR-RUNTIME-006 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-RUNTIME-007 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-RUNTIME-008 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-RUNTIME-009 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-RUNTIME-010 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-RUNTIME-011 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · REJECTED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M0 · tiers 3/9 |
| RR-RUNTIME-012 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 4/9 |
| RR-RUNTIME-013 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M5 · tiers 7/9 |
| RR-RUNTIME-014 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · REJECTED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M0 · tiers 3/9 |
| RR-RUNTIME-015 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M2 · tiers 1/9 |
| RR-RUNTIME-020 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-SERVICE-000 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-SERVICE-001 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 8/9 |
| RR-SERVICE-002 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 2/9 |
| RR-SERVICE-003 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 7/9 |
| RR-SERVICE-004 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 4/9 |
| RR-SERVICE-005 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 8/9 |
| RR-SERVICE-006 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 4/9 |
| RR-SERVICE-007 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 4/9 |
| RR-SERVICE-008 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 4/9 |
| RR-SERVICE-009 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 4/9 |
| RR-SERVICE-010 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 4/9 |
| RR-SERVICE-011 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 4/9 |
| RR-SERVICE-012 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 4/9 |
| RR-SERVICE-013 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-SERVICE-014 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 8/9 |
| RR-SERVICE-015 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-SERVICE-016 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 5/9 |
| RR-SERVICE-017 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-SERVICE-018 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 5/9 |
| RR-SF-2 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 8/9 |
| RR-SMC-01 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 8/9 |
| RR-SMC-02 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-SMC-03 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-SMC-04 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-SMC-05 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-SMC-06 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-SMC-07 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-SMC-08 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-SMC-09 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-SMC-10 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-SMC-11 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 4/9 |
| RR-SMR-01 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 8/9 |
| RR-SMR-02 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-SMR-03 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-SMR-04 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-SMR-05 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-SMR-06 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 4/9 |
| RR-SMR-07 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 4/9 |
| RR-SMR-08 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-SMR-09 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-SMR-10 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-SMR-11 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-SMR-12 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 5/9 |
| RR-SMR-13 | requirement | YES | YES | NO | YES | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M6 · tiers 7/9 |
| RR-UCKO-ALIAS-0001 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 3/9 |
| RR-UCKO-ANTI-0001 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 3/9 |
| RR-UCKO-CONV-0001 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 3/9 |
| RR-UCKO-DEC-0001 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 4/9 |
| RR-UCKO-EXPLICIT-0001 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 3/9 |
| RR-UCKO-NOBODY-0001 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 3/9 |
| RR-UCKO-OTHER-0001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M2 · tiers 1/9 |
| RR-UCKO-PAT-0001 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 3/9 |
| RR-UCKO-PEER-0001 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 3/9 |
| RR-UCKO-PRIN-0001 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 6/9 |
| RR-UCKO-PRIN-0002 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 5/9 |
| RR-UCKO-PRIN-0003 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 3/9 |
| RR-UCKO-PRIN-0004 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 3/9 |
| RR-UCKO-PRIN-0005 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 3/9 |
| RR-UCKO-RULE-0001 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 4/9 |
| RR-UCKO-STD-0001 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 4/9 |
| RR-UCKO-T-0001 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 3/9 |
| RR-UCKO-T-0002 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 3/9 |
| RR-UCKO-T-0003 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 3/9 |
| RR-UCKO-T-0004 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 3/9 |
| RR-UCKO-T-0005 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 3/9 |
| RR-UCKO-T-0006 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 3/9 |
| RR-UCKO-T-0007 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 3/9 |
| RR-UCKO-T-0008 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 3/9 |
| RR-UCKO-T-0009 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 3/9 |
| RR-UCKO-T-0010 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 3/9 |
| RR-UCKO-T-0011 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 3/9 |
| RR-UCKO-T-0012 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 3/9 |
| RR-UCKO-TARGET-0001 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 3/9 |
| RR-UCKO-TEST-0001 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 3/9 |
| RR-UCKO-WRONG-0001 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 3/9 |
| RR-UCKO-X-0001 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 3/9 |
| RR-UCKO-XXX-000 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-UCOS-COMP-000000 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 6/9 |
| RR-UCOS-COMP-000001 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 7/9 |
| RR-UCOS-COMP-000002 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 3/9 |
| RR-UCOS-COMP-001000 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-001001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-UCOS-COMP-001002 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-001003 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-001004 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-001005 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-001006 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-001007 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-001008 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-001009 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-001010 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-002000 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-002001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-002002 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-002003 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-002004 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-002005 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-002006 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-002007 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-002008 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-002009 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-003000 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-003001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-003002 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-003003 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-003004 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-003005 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-003006 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-003007 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-003008 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-003009 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-004000 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-004001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-004002 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-004003 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-004004 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-004005 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-004006 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-004007 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-004008 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-004009 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-005000 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-005001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-005002 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-005003 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-005004 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-005005 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-005006 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-005007 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-005008 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-005009 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-005010 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-006000 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-006001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-006002 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-006003 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-006004 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-006005 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-006006 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-006007 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-006008 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-006009 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-006010 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-007000 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-007001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-007002 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-007003 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-007004 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-007005 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-007006 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-007007 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-007008 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-007009 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-008000 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-008001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-008002 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-008003 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-008004 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-008005 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-008006 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-008007 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-008008 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-008009 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-009000 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-009001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-009002 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-009003 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-009004 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-009005 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-009006 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-009007 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-009008 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-009009 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-COMP-009010 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 2/9 |
| RR-UCOS-EXEC-000 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-UCOS-EXEC-001 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 5/9 |
| RR-UCOS-EXEC-002 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 5/9 |
| RR-UCOS-EXEC-003 | requirement | YES | YES | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M3 · tiers 6/9 |
| RR-UCOS-EXEC-004 | requirement | YES | NO | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M2 · tiers 2/9 |
| RR-UCOS-EXEC-005 | requirement | YES | NO | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M2 · tiers 2/9 |
| RR-UCOS-EXEC-006 | requirement | YES | NO | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M2 · tiers 2/9 |
| RR-UCOS-EXEC-007 | requirement | YES | NO | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M2 · tiers 2/9 |
| RR-UCOS-EXEC-008 | requirement | YES | NO | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M2 · tiers 2/9 |
| RR-UCOS-EXEC-009 | requirement | YES | NO | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M2 · tiers 2/9 |
| RR-UCOS-EXEC-010 | requirement | YES | NO | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M2 · tiers 2/9 |
| RR-UCOS-EXEC-011 | requirement | YES | NO | NO | NO | YES | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · CERTIFIED-PROVISIONAL · M=M2 · tiers 4/9 |
| RR-UCOS-GOV-000 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-UCOS-GOV-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-UCOS-GOV-002 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 4/9 |
| RR-UCOS-GOV-003 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-UCOS-GOV-004 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 5/9 |
| RR-UCOS-GOV-005 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · REJECTED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M0 · tiers 3/9 |
| RR-UCOS-GOV-006 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 4/9 |
| RR-UCOS-RAT-000 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-UCOS-RAT-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 3/9 |
| RR-UCOS-RECON-0000 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-UCOS-RECON-0001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · REJECTED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M0 · tiers 1/9 |
| RR-UCOS-RECON-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · REJECTED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M0 · tiers 3/9 |
| RR-UCOS-RECON-C1 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 3/9 |
| RR-UCOS-RECON-C2 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · REJECTED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M0 · tiers 1/9 |
| RR-UKDA-DEC-000 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · DEFERRED · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M1 · tiers 1/9 |
| RR-UKDA-DEC-0001 | requirement | YES | YES | NO | YES | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M4 · tiers 3/9 |
| RR-UKDA-DEC-0002 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 2/9 |
| RR-UKDA-DEC-0003 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 2/9 |
| RR-Ω∞-000 | requirement | YES | YES | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · PRESENT-IN-CODE · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M3 · tiers 5/9 |
| RR-Ω∞-001 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M2 · tiers 5/9 |
| RR-Ω∞-002 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M2 · tiers 4/9 |
| RR-Ω∞-003 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M2 · tiers 4/9 |
| RR-Ω∞-004 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M2 · tiers 4/9 |
| RR-Ω∞-005 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M2 · tiers 4/9 |
| RR-Ω∞-006 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M2 · tiers 4/9 |
| RR-Ω∞-007 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M2 · tiers 4/9 |
| RR-Ω∞-008 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M2 · tiers 4/9 |
| RR-Ω∞-009 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M2 · tiers 4/9 |
| RR-Ω∞-010 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M2 · tiers 4/9 |
| RR-Ω∞-011 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M2 · tiers 4/9 |
| RR-Ω∞-012 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M2 · tiers 4/9 |
| RR-Ω∞-013 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M2 · tiers 4/9 |
| RR-Ω∞-014 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M2 · tiers 4/9 |
| RR-Ω∞-015 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M2 · tiers 4/9 |
| RR-Ω∞-016 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M2 · tiers 4/9 |
| RR-Ω∞-017 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M2 · tiers 4/9 |
| RR-Ω∞-018 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M2 · tiers 4/9 |
| RR-Ω∞-019 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M2 · tiers 4/9 |
| RR-Ω∞-020 | requirement | YES | NO | NO | NO | NO | 00-MASTER/UAKOS-CLOSURE-009/requirements.json · ABSENT · NO-RUNTIME-EVIDENCE · UNCERTIFIED · M=M2 · tiers 4/9 |

## §B — REQUIREMENT — prose universe (REQ-NN)

49 artifacts.

| Artifact | Type | Declared | Reachable | Executed | Measured | Certified | Evidence |
|---|---|---|---|---|---|---|---|
| REQ-01 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-02 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-03 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-04 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-05 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-06 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-08 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-09 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-10 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-11 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-12 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-13 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-14 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-15 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-16 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-17 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-18 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-19 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-20 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-21 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-22 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-23 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: True |
| REQ-24 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-25 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-26 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-27 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-28 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: True |
| REQ-29 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-30 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-31 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-32 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-33 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-34 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-35 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-36 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-37 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row present in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: True |
| REQ-38 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row ABSENT in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-39 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row ABSENT in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-40 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row ABSENT in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-41 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row ABSENT in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-42 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row ABSENT in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-43 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row ABSENT in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: True |
| REQ-44 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row ABSENT in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-45 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row ABSENT in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-46 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row ABSENT in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-47 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row ABSENT in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-48 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row ABSENT in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-49 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row ABSENT in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: False |
| REQ-50 | requirement | PARTIAL | NO | NO | NO | NO | UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md (prose table); traceability row ABSENT in UCOS-OMEGA-INFINITY-UNIVERSAL-REQUIREMENT-TRACEABILITY-MATRIX.md; named in code: True |

## §C — LAW

204 artifacts.

| Artifact | Type | Declared | Reachable | Executed | Measured | Certified | Evidence |
|---|---|---|---|---|---|---|---|
| CIOS-L-01 | law | YES | NO | NO | NO | NO | 00-MASTER/IMR-003A/cios-bindings.json · check=NONE · no blocking field |
| CIOS-L-02 | law | YES | NO | NO | NO | NO | 00-MASTER/IMR-003A/cios-bindings.json · check=NONE · no blocking field |
| CIOS-L-03 | law | YES | NO | NO | NO | NO | 00-MASTER/IMR-003A/cios-bindings.json · check=NONE · no blocking field |
| CIOS-L-04 | law | YES | NO | NO | NO | NO | 00-MASTER/IMR-003A/cios-bindings.json · check=NONE · no blocking field |
| CIOS-L-05 | law | YES | NO | NO | NO | NO | 00-MASTER/IMR-003A/cios-bindings.json · check=NONE · no blocking field |
| CIOS-L-06 | law | YES | NO | NO | NO | NO | 00-MASTER/IMR-003A/cios-bindings.json · check=NONE · no blocking field |
| CIOS-L-07 | law | YES | NO | NO | NO | NO | 00-MASTER/IMR-003A/cios-bindings.json · check=NONE · no blocking field |
| CIOS-L-08 | law | YES | NO | NO | NO | NO | 00-MASTER/IMR-003A/cios-bindings.json · check=NONE · no blocking field |
| CIOS-L-09 | law | YES | NO | NO | NO | NO | 00-MASTER/IMR-003A/cios-bindings.json · check=NONE · no blocking field |
| CIOS-L-10 | law | YES | NO | NO | NO | NO | 00-MASTER/IMR-003A/cios-bindings.json · check=NONE · no blocking field |
| CIOS-L-11 | law | YES | NO | NO | NO | NO | 00-MASTER/IMR-003A/cios-bindings.json · check=NONE · no blocking field |
| CIOS-L-12 | law | YES | NO | NO | NO | NO | 00-MASTER/IMR-003A/cios-bindings.json · check=NONE · no blocking field |
| CIOS-L-13 | law | YES | NO | NO | NO | NO | 00-MASTER/IMR-003A/cios-bindings.json · check=NONE · no blocking field |
| CIOS-L-14 | law | YES | NO | NO | NO | NO | 00-MASTER/IMR-003A/cios-bindings.json · check=NONE · no blocking field |
| CIOS-L-15 | law | YES | NO | NO | NO | NO | 00-MASTER/IMR-003A/cios-bindings.json · check=NONE · no blocking field |
| CIOS-L-16 | law | YES | NO | NO | NO | NO | 00-MASTER/IMR-003A/cios-bindings.json · check=NONE · no blocking field |
| CIOS-L-17 | law | YES | NO | NO | NO | NO | 00-MASTER/IMR-003A/cios-bindings.json · check=NONE · no blocking field |
| CIOS-L-18 | law | YES | NO | NO | NO | NO | 00-MASTER/IMR-003A/cios-bindings.json · check=NONE · no blocking field |
| CIOS-L-19 | law | YES | NO | NO | NO | NO | 00-MASTER/IMR-003A/cios-bindings.json · check=NONE · no blocking field |
| CIOS-L-20 | law | YES | NO | NO | NO | NO | 00-MASTER/IMR-003A/cios-bindings.json · check=NONE · no blocking field |
| CIOS-L-21 | law | YES | NO | NO | NO | NO | 00-MASTER/IMR-003A/cios-bindings.json · check=NONE · no blocking field |
| CIOS-L-22 | law | YES | NO | NO | NO | NO | 00-MASTER/IMR-003A/cios-bindings.json · check=NONE · no blocking field |
| CIOS-L-23 | law | YES | NO | NO | NO | NO | 00-MASTER/IMR-003A/cios-bindings.json · check=NONE · no blocking field |
| CIOS-L-24 | law | YES | NO | NO | NO | NO | 00-MASTER/IMR-003A/cios-bindings.json · check=NONE · no blocking field |
| UCEF-LAW-01 | law | YES | NO | NO | NO | NO | 00-MASTER/UCEF-000001/ucef-framework.json · check=NONE · no blocking field |
| UCEF-LAW-02 | law | YES | NO | NO | NO | NO | 00-MASTER/UCEF-000001/ucef-framework.json · check=NONE · no blocking field |
| UCEF-LAW-03 | law | YES | NO | NO | NO | NO | 00-MASTER/UCEF-000001/ucef-framework.json · check=NONE · no blocking field |
| UCEF-LAW-04 | law | YES | NO | NO | NO | NO | 00-MASTER/UCEF-000001/ucef-framework.json · check=NONE · no blocking field |
| UCEF-LAW-05 | law | YES | NO | NO | NO | NO | 00-MASTER/UCEF-000001/ucef-framework.json · check=NONE · no blocking field |
| UCEF-LAW-06 | law | YES | NO | NO | NO | NO | 00-MASTER/UCEF-000001/ucef-framework.json · check=NONE · no blocking field |
| UCEF-LAW-07 | law | YES | NO | NO | NO | NO | 00-MASTER/UCEF-000001/ucef-framework.json · check=NONE · no blocking field |
| UCEF-LAW-08 | law | YES | NO | NO | NO | NO | 00-MASTER/UCEF-000001/ucef-framework.json · check=NONE · no blocking field |
| UCEF-LAW-09 | law | YES | NO | NO | NO | NO | 00-MASTER/UCEF-000001/ucef-framework.json · check=NONE · no blocking field |
| UCEF-LAW-10 | law | YES | NO | NO | NO | NO | 00-MASTER/UCEF-000001/ucef-framework.json · check=NONE · no blocking field |
| UCEF-LAW-11 | law | YES | NO | NO | NO | NO | 00-MASTER/UCEF-000001/ucef-framework.json · check=NONE · no blocking field |
| UCEF-LAW-12 | law | YES | NO | NO | NO | NO | 00-MASTER/UCEF-000001/ucef-framework.json · check=NONE · no blocking field |
| UCON-L-01 | law | YES | YES | YES | YES | YES | 00-MASTER/UCON-000001/ucon-declaration.json · check=every_construct_is_disposed · blocking |
| UCON-L-02 | law | YES | YES | YES | NO | YES | 00-MASTER/UCON-000001/ucon-declaration.json · check=disposition_is_total · blocking |
| UCON-L-03 | law | YES | YES | YES | YES | YES | 00-MASTER/UCON-000001/ucon-declaration.json · check=catch_all_is_non_destructive · blocking |
| UCON-L-04 | law | YES | YES | YES | NO | YES | 00-MASTER/UCON-000001/ucon-declaration.json · check=operators_are_two_way_bound · blocking |
| UCON-L-05 | law | YES | YES | YES | NO | YES | 00-MASTER/UCON-000001/ucon-declaration.json · check=nothing_is_silently_ignored · blocking |
| UCON-L-06 | law | YES | YES | YES | NO | YES | 00-MASTER/UCON-000001/ucon-declaration.json · check=unknown_and_contradiction_are_first_class · blocking |
| UCON-L-07 | law | YES | YES | YES | NO | YES | 00-MASTER/UCON-000001/ucon-declaration.json · check=discovery_reaches_a_fixed_point · blocking |
| UCON-L-08 | law | YES | YES | YES | YES | YES | 00-MASTER/UCON-000001/ucon-declaration.json · check=future_kinds_need_no_redesign · blocking |
| UCON-L-09 | law | YES | YES | YES | NO | YES | 00-MASTER/UCON-000001/ucon-declaration.json · check=extension_points_are_exercisable · blocking |
| UCON-L-10 | law | YES | YES | YES | YES | YES | 00-MASTER/UCON-000001/ucon-declaration.json · check=no_state_is_terminal · blocking |
| UCON-L-11 | law | YES | YES | YES | NO | YES | 00-MASTER/UCON-000001/ucon-declaration.json · check=reality_is_independent_of_admission · blocking |
| UCON-L-12 | law | YES | YES | YES | YES | YES | 00-MASTER/UCON-000001/ucon-declaration.json · check=verification_is_itself_verifiable · blocking |
| UCON-L-13 | law | YES | YES | YES | NO | YES | 00-MASTER/UCON-000001/ucon-declaration.json · check=no_completeness_claim_is_declared · blocking |
| UCON-L-14 | law | YES | YES | YES | YES | YES | 00-MASTER/UCON-000001/ucon-declaration.json · check=vocabulary_is_not_duplicated · blocking |
| UCON-L-15 | law | YES | YES | YES | NO | YES | 00-MASTER/UCON-000001/ucon-declaration.json · check=closure_inventory_holds · blocking |
| UCON-L-16 | law | YES | YES | YES | YES | YES | 00-MASTER/UCON-000001/ucon-declaration.json · check=measurement_is_deterministic · blocking |
| CAA-INV-01 | law | YES | NO | NO | YES | YES | 00-MASTER/UCOS-UGA-001/uga-declaration.json#alignment_invariants · check=NONE · no blocking field |
| CAA-INV-02 | law | YES | NO | NO | YES | YES | 00-MASTER/UCOS-UGA-001/uga-declaration.json#alignment_invariants · check=NONE · no blocking field |
| CAA-INV-03 | law | YES | NO | NO | YES | YES | 00-MASTER/UCOS-UGA-001/uga-declaration.json#alignment_invariants · check=NONE · no blocking field |
| CAA-INV-04 | law | YES | NO | NO | YES | YES | 00-MASTER/UCOS-UGA-001/uga-declaration.json#alignment_invariants · check=NONE · no blocking field |
| CAA-INV-05 | law | YES | NO | NO | YES | YES | 00-MASTER/UCOS-UGA-001/uga-declaration.json#alignment_invariants · check=NONE · no blocking field |
| CAA-INV-06 | law | YES | NO | NO | YES | YES | 00-MASTER/UCOS-UGA-001/uga-declaration.json#alignment_invariants · check=NONE · no blocking field |
| CAA-INV-07 | law | YES | NO | NO | YES | YES | 00-MASTER/UCOS-UGA-001/uga-declaration.json#alignment_invariants · check=NONE · no blocking field |
| IL-01 | law | YES | NO | NO | YES | NO | 00-MASTER/UCOS-URR-001/urr-declaration.json#inference_laws · check=NONE · no blocking field |
| IL-02 | law | YES | NO | NO | YES | NO | 00-MASTER/UCOS-URR-001/urr-declaration.json#inference_laws · check=NONE · no blocking field |
| IL-03 | law | YES | NO | NO | YES | NO | 00-MASTER/UCOS-URR-001/urr-declaration.json#inference_laws · check=NONE · no blocking field |
| IL-04 | law | YES | NO | NO | YES | NO | 00-MASTER/UCOS-URR-001/urr-declaration.json#inference_laws · check=NONE · no blocking field |
| IL-05 | law | YES | NO | NO | YES | NO | 00-MASTER/UCOS-URR-001/urr-declaration.json#inference_laws · check=NONE · no blocking field |
| IL-06 | law | YES | NO | NO | YES | NO | 00-MASTER/UCOS-URR-001/urr-declaration.json#inference_laws · check=NONE · no blocking field |
| IL-07 | law | YES | NO | NO | YES | NO | 00-MASTER/UCOS-URR-001/urr-declaration.json#inference_laws · check=NONE · no blocking field |
| IL-08 | law | YES | NO | NO | YES | NO | 00-MASTER/UCOS-URR-001/urr-declaration.json#inference_laws · check=NONE · no blocking field |
| IL-09 | law | YES | NO | NO | YES | NO | 00-MASTER/UCOS-URR-001/urr-declaration.json#inference_laws · check=NONE · no blocking field |
| IL-10 | law | YES | NO | NO | YES | NO | 00-MASTER/UCOS-URR-001/urr-declaration.json#inference_laws · check=NONE · no blocking field |
| IL-11 | law | YES | NO | NO | YES | NO | 00-MASTER/UCOS-URR-001/urr-declaration.json#inference_laws · check=NONE · no blocking field |
| IL-12 | law | YES | NO | NO | YES | NO | 00-MASTER/UCOS-URR-001/urr-declaration.json#inference_laws · check=NONE · no blocking field |
| IL-13 | law | YES | NO | NO | YES | NO | 00-MASTER/UCOS-URR-001/urr-declaration.json#inference_laws · check=NONE · no blocking field |
| UCPA-L-01 | law | YES | YES | YES | YES | YES | 00-MASTER/UCPA-000001/ucpa-declaration.json · check=primitives_are_declared_by_the_register · no blocking field |
| UCPA-L-02 | law | YES | YES | YES | YES | YES | 00-MASTER/UCPA-000001/ucpa-declaration.json · check=standing_matches_the_ratification_record · no blocking field |
| UCPA-L-03 | law | YES | YES | YES | YES | YES | 00-MASTER/UCPA-000001/ucpa-declaration.json · check=facet_reduction_covers_the_facet_model · no blocking field |
| UCPA-L-04 | law | YES | YES | YES | YES | YES | 00-MASTER/UCPA-000001/ucpa-declaration.json · check=no_reduction_targets_the_axiom · no blocking field |
| UCPA-L-05 | law | YES | YES | YES | YES | YES | 00-MASTER/UCPA-000001/ucpa-declaration.json · check=projections_resolve_and_supersessions_are_real · no blocking field |
| UCPA-L-06 | law | YES | YES | YES | YES | YES | 00-MASTER/UCPA-000001/ucpa-declaration.json · check=authority_is_single_and_matches_the_owner_binding · no blocking field |
| UCPA-L-07 | law | YES | YES | YES | YES | YES | 00-MASTER/UCPA-000001/ucpa-declaration.json · check=the_primitive_set_admits_a_future_member · no blocking field |
| UCPA-L-08 | law | YES | YES | YES | YES | YES | 00-MASTER/UCPA-000001/ucpa-declaration.json · check=the_programme_reduces_to_a_declared_primitive · no blocking field |
| UEC-L-01 | law | YES | YES | YES | YES | YES | 00-MASTER/UEC-000001/uec-declaration.json · check=discovery_rules_are_non_vacuous · blocking |
| UEC-L-02 | law | YES | YES | YES | YES | YES | 00-MASTER/UEC-000001/uec-declaration.json · check=declared_enforcement_exists · blocking |
| UEC-L-03 | law | YES | YES | YES | YES | YES | 00-MASTER/UEC-000001/uec-declaration.json · check=discovered_enforcement_is_governed · blocking |
| UEC-L-04 | law | YES | YES | YES | YES | YES | 00-MASTER/UEC-000001/uec-declaration.json · check=every_engine_has_an_invoker · blocking |
| UEC-L-05 | law | YES | YES | YES | YES | YES | 00-MASTER/UEC-000001/uec-declaration.json · check=every_engine_has_a_test · blocking |
| UEC-L-06 | law | YES | YES | YES | NO | YES | 00-MASTER/UEC-000001/uec-declaration.json · check=no_single_invocation_plane · blocking |
| UEC-L-07 | law | YES | YES | YES | NO | YES | 00-MASTER/UEC-000001/uec-declaration.json · check=every_declaration_is_consumed · blocking |
| UEC-L-08 | law | YES | YES | YES | NO | YES | 00-MASTER/UEC-000001/uec-declaration.json · check=certification_identity_exists · blocking |
| UEC-L-09 | law | YES | YES | YES | YES | YES | 00-MASTER/UEC-000001/uec-declaration.json · check=self_coverage_is_a_fixed_point · blocking |
| UEC-L-10 | law | YES | YES | YES | YES | YES | 00-MASTER/UEC-000001/uec-declaration.json · check=planes_are_disjoint · blocking |
| UEC-L-11 | law | YES | YES | YES | YES | YES | 00-MASTER/UEC-000001/uec-declaration.json · check=no_assurance_reduction · blocking |
| UEC-L-12 | law | YES | YES | YES | YES | YES | 00-MASTER/UEC-000001/uec-declaration.json · check=withdrawals_are_reasoned_and_capped · blocking |
| UEC-L-13 | law | YES | YES | YES | YES | YES | 00-MASTER/UEC-000001/uec-declaration.json · check=certification_identity_is_complete · blocking |
| UIL-01 | law | YES | NO | NO | YES | YES | 00-MASTER/UIS-001/uis-declaration.json · check=NONE · blocking |
| UIL-02 | law | YES | NO | NO | YES | YES | 00-MASTER/UIS-001/uis-declaration.json · check=NONE · blocking |
| UIL-03 | law | YES | NO | NO | YES | YES | 00-MASTER/UIS-001/uis-declaration.json · check=NONE · blocking |
| UIL-04 | law | YES | NO | NO | YES | YES | 00-MASTER/UIS-001/uis-declaration.json · check=NONE · blocking |
| UIL-05 | law | YES | NO | NO | YES | YES | 00-MASTER/UIS-001/uis-declaration.json · check=NONE · blocking |
| UIL-06 | law | YES | NO | NO | YES | YES | 00-MASTER/UIS-001/uis-declaration.json · check=NONE · blocking |
| UIL-07 | law | YES | NO | NO | YES | YES | 00-MASTER/UIS-001/uis-declaration.json · check=NONE · blocking |
| UIL-08 | law | YES | NO | NO | YES | YES | 00-MASTER/UIS-001/uis-declaration.json · check=NONE · blocking |
| UIL-09 | law | YES | NO | NO | YES | YES | 00-MASTER/UIS-001/uis-declaration.json · check=NONE · blocking |
| UIL-10 | law | YES | NO | NO | YES | YES | 00-MASTER/UIS-001/uis-declaration.json · check=NONE · blocking |
| UIL-11 | law | YES | NO | NO | YES | YES | 00-MASTER/UIS-001/uis-declaration.json · check=NONE · NON-BLOCKING |
| UIL-12 | law | YES | NO | NO | YES | YES | 00-MASTER/UIS-001/uis-declaration.json · check=NONE · blocking |
| UIL-13 | law | YES | NO | NO | YES | YES | 00-MASTER/UIS-001/uis-declaration.json · check=NONE · blocking |
| UIL-14 | law | YES | NO | NO | YES | YES | 00-MASTER/UIS-001/uis-declaration.json · check=NONE · blocking |
| UIL-15 | law | YES | NO | NO | YES | YES | 00-MASTER/UIS-001/uis-declaration.json · check=NONE · blocking |
| UIL-16 | law | YES | NO | NO | NO | YES | 00-MASTER/UIS-001/uis-declaration.json · check=NONE · blocking |
| UIL-17 | law | YES | NO | NO | NO | YES | 00-MASTER/UIS-001/uis-declaration.json · check=NONE · blocking |
| UIL-18 | law | YES | NO | NO | NO | YES | 00-MASTER/UIS-001/uis-declaration.json · check=NONE · blocking |
| UIL-19 | law | YES | NO | NO | NO | YES | 00-MASTER/UIS-001/uis-declaration.json · check=NONE · blocking |
| UIL-20 | law | YES | NO | NO | NO | YES | 00-MASTER/UIS-001/uis-declaration.json · check=NONE · blocking |
| UIL-01 | law | YES | NO | NO | YES | NO | 00-MASTER/UIS-001/uis.json · check=NONE · blocking |
| UIL-02 | law | YES | NO | NO | YES | NO | 00-MASTER/UIS-001/uis.json · check=NONE · blocking |
| UIL-03 | law | YES | NO | NO | YES | NO | 00-MASTER/UIS-001/uis.json · check=NONE · blocking |
| UIL-04 | law | YES | NO | NO | YES | NO | 00-MASTER/UIS-001/uis.json · check=NONE · blocking |
| UIL-05 | law | YES | NO | NO | YES | NO | 00-MASTER/UIS-001/uis.json · check=NONE · blocking |
| UIL-06 | law | YES | NO | NO | YES | NO | 00-MASTER/UIS-001/uis.json · check=NONE · blocking |
| UIL-07 | law | YES | NO | NO | YES | NO | 00-MASTER/UIS-001/uis.json · check=NONE · blocking |
| UIL-08 | law | YES | NO | NO | YES | NO | 00-MASTER/UIS-001/uis.json · check=NONE · blocking |
| UIL-09 | law | YES | NO | NO | YES | NO | 00-MASTER/UIS-001/uis.json · check=NONE · blocking |
| UIL-10 | law | YES | NO | NO | YES | NO | 00-MASTER/UIS-001/uis.json · check=NONE · blocking |
| UIL-11 | law | YES | NO | NO | YES | NO | 00-MASTER/UIS-001/uis.json · check=NONE · NON-BLOCKING |
| UIL-12 | law | YES | NO | NO | YES | NO | 00-MASTER/UIS-001/uis.json · check=NONE · blocking |
| UIL-13 | law | YES | NO | NO | YES | NO | 00-MASTER/UIS-001/uis.json · check=NONE · blocking |
| UIL-14 | law | YES | NO | NO | YES | NO | 00-MASTER/UIS-001/uis.json · check=NONE · blocking |
| UIL-15 | law | YES | NO | NO | YES | NO | 00-MASTER/UIS-001/uis.json · check=NONE · blocking |
| UIL-16 | law | YES | NO | NO | NO | NO | 00-MASTER/UIS-001/uis.json · check=NONE · blocking |
| UIL-17 | law | YES | NO | NO | NO | NO | 00-MASTER/UIS-001/uis.json · check=NONE · blocking |
| UIL-18 | law | YES | NO | NO | NO | NO | 00-MASTER/UIS-001/uis.json · check=NONE · blocking |
| UIL-19 | law | YES | NO | NO | NO | NO | 00-MASTER/UIS-001/uis.json · check=NONE · blocking |
| UIL-20 | law | YES | NO | NO | NO | NO | 00-MASTER/UIS-001/uis.json · check=NONE · blocking |
| ISD-L-01 | law | YES | YES | YES | YES | YES | 00-MASTER/UISD-000001/uisd-declaration.json · check=scope_expansion_capacity · no blocking field |
| ISD-L-02 | law | YES | YES | YES | YES | YES | 00-MASTER/UISD-000001/uisd-declaration.json · check=direction_expansion_capacity · no blocking field |
| ISD-L-03 | law | YES | YES | YES | YES | YES | 00-MASTER/UISD-000001/uisd-declaration.json · check=principle_inherits_itself · no blocking field |
| ISD-L-04 | law | YES | YES | YES | YES | YES | 00-MASTER/UISD-000001/uisd-declaration.json · check=lifecycle_applies_to_itself · no blocking field |
| ISD-L-05 | law | YES | YES | YES | YES | YES | 00-MASTER/UISD-000001/uisd-declaration.json · check=evolution_applies_to_itself · no blocking field |
| ISD-L-06 | law | YES | YES | YES | YES | YES | 00-MASTER/UISD-000001/uisd-declaration.json · check=relationship_model_expands · no blocking field |
| ISD-L-07 | law | YES | YES | YES | YES | YES | 00-MASTER/UISD-000001/uisd-declaration.json · check=no_active_permanence_declaration · no blocking field |
| ISD-L-08 | law | YES | YES | YES | YES | YES | 00-MASTER/UISD-000001/uisd-declaration.json · check=baseline_temporal_qualification · no blocking field |
| ISD-L-09 | law | YES | YES | YES | YES | YES | 00-MASTER/UISD-000001/uisd-declaration.json · check=technology_is_evolutionary_state · no blocking field |
| ISD-L-10 | law | YES | YES | YES | YES | YES | 00-MASTER/UISD-000001/uisd-declaration.json · check=capability_seed_openness · no blocking field |
| ISD-L-11 | law | YES | YES | YES | YES | YES | 00-MASTER/UISD-000001/uisd-declaration.json · check=admission_path_exercisability · no blocking field |
| BSP-L-01 | law | YES | YES | NO | YES | NO | 00-MASTER/UOBC-000001/birth-scope-policy.json · check=policy_is_structurally_usable · no blocking field |
| BSP-L-02 | law | YES | YES | NO | YES | NO | 00-MASTER/UOBC-000001/birth-scope-policy.json · check=classification_is_total · no blocking field |
| BSP-L-03 | law | YES | YES | NO | YES | NO | 00-MASTER/UOBC-000001/birth-scope-policy.json · check=no_derived_object_is_born · no blocking field |
| BSP-L-04 | law | YES | YES | NO | YES | NO | 00-MASTER/UOBC-000001/birth-scope-policy.json · check=every_birth_subject_may_be_born · no blocking field |
| BSP-L-05 | law | YES | YES | NO | YES | NO | 00-MASTER/UOBC-000001/birth-scope-policy.json · check=adoption_is_disclosed · no blocking field |
| BSP-L-06 | law | YES | YES | NO | YES | NO | 00-MASTER/UOBC-000001/birth-scope-policy.json · check=coverage_does_not_regress · no blocking field |
| UOBC-L-01 | law | YES | YES | NO | NO | NO | 00-MASTER/UOBC-000001/uobc-birth-contract.json · check=identity_precedes_existence · no blocking field |
| UOBC-L-02 | law | YES | YES | NO | NO | NO | 00-MASTER/UOBC-000001/uobc-birth-contract.json · check=no_rival_counter · no blocking field |
| UOBC-L-03 | law | YES | YES | NO | YES | NO | 00-MASTER/UOBC-000001/uobc-birth-contract.json · check=identity_immutable · no blocking field |
| UOBC-L-04 | law | YES | YES | NO | NO | NO | 00-MASTER/UOBC-000001/uobc-birth-contract.json · check=no_anonymous_object · no blocking field |
| UOBC-L-05 | law | YES | YES | NO | NO | NO | 00-MASTER/UOBC-000001/uobc-birth-contract.json · check=no_temporary_identity · no blocking field |
| UOBC-L-06 | law | YES | YES | NO | NO | NO | 00-MASTER/UOBC-000001/uobc-birth-contract.json · check=no_post_creation_registration · no blocking field |
| UOBC-L-07 | law | YES | YES | NO | NO | NO | 00-MASTER/UOBC-000001/uobc-birth-contract.json · check=evolution_preserves_identity · no blocking field |
| UOBC-L-08 | law | YES | YES | NO | NO | NO | 00-MASTER/UOBC-000001/uobc-birth-contract.json · check=append_only_history · no blocking field |
| URKE-L-01 | law | YES | YES | YES | YES | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=every_identified_unknown_is_governed · blocking |
| URKE-L-02 | law | YES | YES | YES | NO | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=residual_is_representable · blocking |
| URKE-L-03 | law | YES | YES | YES | YES | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=profile_requirements_are_enforced · blocking |
| URKE-L-04 | law | YES | YES | YES | YES | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=histories_are_append_only · blocking |
| URKE-L-05 | law | YES | YES | YES | YES | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=gap_closure_and_review_are_governed · blocking |
| URKE-L-06 | law | YES | YES | YES | YES | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=vocabulary_is_declared_not_coded · blocking |
| URKE-L-07 | law | YES | YES | YES | YES | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=no_state_is_terminal · blocking |
| URKE-L-08 | law | YES | YES | YES | NO | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=data_extension_needs_no_redesign · blocking |
| URKE-L-09 | law | YES | YES | YES | NO | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=future_domain_is_admissible · blocking |
| URKE-L-10 | law | YES | YES | YES | YES | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=discovery_reaches_a_fixed_point · blocking |
| URKE-L-11 | law | YES | YES | YES | NO | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=discovery_never_mutates_constitutional_truth · blocking |
| URKE-L-12 | law | YES | YES | YES | NO | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=discovery_covers_every_declared_target · blocking |
| URKE-L-13 | law | YES | YES | YES | YES | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=evolution_is_one_traceable_mechanism · blocking |
| URKE-L-14 | law | YES | YES | YES | YES | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=worlds_are_data_driven · blocking |
| URKE-L-15 | law | YES | YES | YES | YES | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=nothing_admitted_can_silently_disappear · blocking |
| URKE-L-16 | law | YES | YES | YES | YES | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=no_subject_exists_outside_governance · blocking |
| URKE-L-17 | law | YES | YES | YES | NO | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=no_subject_exists_outside_context · blocking |
| URKE-L-18 | law | YES | YES | YES | YES | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=no_completeness_claim_is_declared · blocking |
| URKE-L-19 | law | YES | YES | YES | YES | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=measurement_is_deterministic · blocking |
| URKE-L-20 | law | YES | YES | YES | YES | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=bound_vocabulary_is_neither_copied_nor_narrowed · blocking |
| URKE-L-21 | law | YES | YES | YES | NO | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=disclosed_gaps_are_themselves_governed · blocking |
| URKE-L-22 | law | YES | YES | YES | NO | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=reality_parity_and_review_are_enforced · blocking |
| URKE-L-23 | law | YES | YES | YES | NO | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=expressiveness_is_preserved_within_bounds · blocking |
| URKE-L-24 | law | YES | YES | YES | YES | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=lifecycle_axes_are_independent · blocking |
| URKE-L-25 | law | YES | YES | YES | YES | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=relationships_carry_governance · blocking |
| URKE-L-26 | law | YES | YES | YES | YES | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=unresolved_generates_research · blocking |
| URKE-L-27 | law | YES | YES | YES | YES | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=learning_pipeline_cannot_be_bypassed · blocking |
| URKE-L-28 | law | YES | YES | YES | YES | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=declared_mechanisms_are_live_and_exercised · blocking |
| URKE-L-29 | law | YES | YES | YES | YES | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=architectural_change_requires_a_governed_proposal · blocking |
| URKE-L-30 | law | YES | YES | YES | YES | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=representation_requires_no_understanding · blocking |
| URKE-L-31 | law | YES | YES | YES | NO | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=unresolved_is_eligible_for_discovery · blocking |
| URKE-L-32 | law | YES | YES | YES | NO | YES | 00-MASTER/URKE-000001/urke-declaration.json · check=stability_is_measured_and_instability_is_governed · blocking |
| UVI-L-01 | law | YES | YES | YES | NO | YES | 00-MASTER/UVI-000001/uvi-declaration.json · check=mode_constitution_completeness · no blocking field |
| UVI-L-02 | law | YES | YES | YES | NO | YES | 00-MASTER/UVI-000001/uvi-declaration.json · check=exactly_one_default · no blocking field |
| UVI-L-03 | law | YES | YES | YES | NO | YES | 00-MASTER/UVI-000001/uvi-declaration.json · check=stage_registry_reconciliation · no blocking field |
| UVI-L-04 | law | YES | YES | YES | NO | YES | 00-MASTER/UVI-000001/uvi-declaration.json · check=no_assurance_reduction · no blocking field |
| UVI-L-05 | law | YES | YES | YES | NO | YES | 00-MASTER/UVI-000001/uvi-declaration.json · check=no_mode_claims_more_than_it_measures · no blocking field |
| UVI-L-06 | law | YES | YES | YES | YES | YES | 00-MASTER/UVI-000001/uvi-declaration.json · check=selection_is_derived · no blocking field |
| UVI-L-07 | law | YES | YES | YES | NO | YES | 00-MASTER/UVI-000001/uvi-declaration.json · check=fail_wide · no blocking field |
| UVI-L-08 | law | YES | YES | YES | NO | YES | 00-MASTER/UVI-000001/uvi-declaration.json · check=topology_neutrality · no blocking field |
| UVI-L-09 | law | YES | YES | YES | YES | YES | 00-MASTER/UVI-000001/uvi-declaration.json · check=evidence_reuse_integrity · no blocking field |
| UVI-L-10 | law | YES | YES | YES | YES | YES | 00-MASTER/UVI-000001/uvi-declaration.json · check=deterministic_planning · no blocking field |
| UVI-L-11 | law | YES | YES | YES | YES | YES | 00-MASTER/UVI-000001/uvi-declaration.json · check=every_declared_read_set_resolves · no blocking field |
| UVI-L-12 | law | YES | YES | YES | NO | YES | 00-MASTER/UVI-000001/uvi-declaration.json · check=every_stage_declares_a_read_set · no blocking field |
| UVI-L-13 | law | YES | YES | YES | NO | YES | 00-MASTER/UVI-000001/uvi-declaration.json · check=read_set_is_independent_of_reuse_policy · no blocking field |
| UVI-L-14 | law | YES | YES | YES | NO | YES | 00-MASTER/UVI-000001/uvi-declaration.json · check=evidence_identity_depends_on_the_read_set · no blocking field |

## §D — ENGINE — gate engines

39 artifacts.

| Artifact | Type | Declared | Reachable | Executed | Measured | Certified | Evidence |
|---|---|---|---|---|---|---|---|
| 00-MASTER/ACEE-000001/acee_engine.py | engine | YES | YES | YES | NO | NO | invocation planes=3 ['.github/workflows/acee-gate.yml', '.github/workflows/uec-gate.yml', 'Makefile']; tests naming it=0 |
| 00-MASTER/BASELINE-001/baseline_engine.py | engine | YES | YES | YES | YES | YES | invocation planes=2 ['.github/workflows/baseline-gate.yml', 'Makefile']; tests naming it=1 |
| 00-MASTER/MCOS-000001/mcos_engine.py | engine | YES | YES | YES | NO | NO | invocation planes=2 ['.github/workflows/mcos-gate.yml', 'Makefile']; tests naming it=0 |
| 00-MASTER/P0-FINAL-CLOSURE-002/final_closure_engine.py | engine | YES | YES | NO | NO | NO | invocation planes=1 ['Makefile']; tests naming it=0 |
| 00-MASTER/P0-LIFECYCLE-CLOSURE-001/lifecycle_closure_engine.py | engine | YES | YES | NO | NO | NO | invocation planes=1 ['Makefile']; tests naming it=0 |
| 00-MASTER/UAEP-000001/uaep_engine.py | engine | YES | YES | YES | YES | YES | invocation planes=2 ['.github/workflows/uaep-gate.yml', 'Makefile']; tests naming it=1 |
| 00-MASTER/UAIE-000001/uaie_engine.py | engine | YES | YES | YES | YES | YES | invocation planes=2 ['.github/workflows/uaie-gate.yml', 'Makefile']; tests naming it=2 |
| 00-MASTER/UAKOS-CLOSURE-002/closure_engine.py | engine | YES | YES | YES | YES | YES | invocation planes=2 ['.github/workflows/roadmap-gate.yml', 'Makefile']; tests naming it=3 |
| 00-MASTER/UAKOS-CLOSURE-002/phase2_engine.py | engine | YES | YES | NO | YES | NO | invocation planes=1 ['Makefile']; tests naming it=3 |
| 00-MASTER/UAKOS-CLOSURE-002/phase3_engine.py | engine | YES | YES | NO | YES | NO | invocation planes=1 ['Makefile']; tests naming it=3 |
| 00-MASTER/UAKOS-CLOSURE-008/assimilation_engine.py | engine | YES | YES | YES | YES | YES | invocation planes=2 ['.github/workflows/assimilation-gate.yml', 'Makefile']; tests naming it=4 |
| 00-MASTER/UAKOS-CLOSURE-008/decision_engine.py | engine | YES | NO | NO | YES | NO | invocation planes=0 []; tests naming it=4 |
| 00-MASTER/UAKOS-CLOSURE-008/superiority_engine.py | engine | YES | NO | NO | YES | NO | invocation planes=0 []; tests naming it=4 |
| 00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py | engine | YES | YES | YES | YES | YES | invocation planes=2 ['.github/workflows/closure009-gate.yml', 'Makefile']; tests naming it=1 |
| 00-MASTER/UAKOS-PHASE-001A-R1/cert_engine.py | engine | YES | NO | NO | NO | NO | invocation planes=0 []; tests naming it=0 |
| 00-MASTER/UAKOS-PHASE-001B/provenance_engine.py | engine | YES | NO | NO | YES | NO | invocation planes=0 []; tests naming it=1 |
| 00-MASTER/UAKOS-PHASE-003R/phase3r_engine.py | engine | YES | NO | NO | NO | NO | invocation planes=0 []; tests naming it=0 |
| 00-MASTER/UCCEP-000000/uccep_engine.py | engine | YES | YES | YES | NO | NO | invocation planes=2 ['.github/workflows/uccep-gate.yml', 'Makefile']; tests naming it=0 |
| 00-MASTER/UCDA-000001/ucda_engine.py | engine | YES | YES | NO | NO | NO | invocation planes=1 ['Makefile']; tests naming it=0 |
| 00-MASTER/UCEF-000001/ucef_engine.py | engine | YES | YES | YES | NO | NO | invocation planes=2 ['.github/workflows/ucef-gate.yml', 'Makefile']; tests naming it=0 |
| 00-MASTER/UCL-000001/ucl_engine.py | engine | YES | YES | YES | YES | YES | invocation planes=2 ['.github/workflows/ucl-gate.yml', 'Makefile']; tests naming it=2 |
| 00-MASTER/UCOS-AEE-001/aee_engine.py | engine | YES | YES | YES | YES | YES | invocation planes=2 ['.github/workflows/aee-gate.yml', 'Makefile']; tests naming it=3 |
| 00-MASTER/UCOS-MXR-001/roadmap_engine.py | engine | YES | YES | YES | NO | NO | invocation planes=2 ['.github/workflows/roadmap-gate.yml', 'Makefile']; tests naming it=0 |
| 00-MASTER/UCOS-RFP-001/rfp_engine.py | engine | YES | YES | YES | NO | NO | invocation planes=2 ['.github/workflows/rfp-gate.yml', 'Makefile']; tests naming it=0 |
| 00-MASTER/UCOS-RIB-001/rib_engine.py | engine | YES | YES | YES | YES | YES | invocation planes=2 ['.github/workflows/rib-gate.yml', 'Makefile']; tests naming it=5 |
| 00-MASTER/UCOS-UAR-001/uar_engine.py | engine | YES | YES | YES | YES | YES | invocation planes=2 ['.github/workflows/uar-gate.yml', 'Makefile']; tests naming it=1 |
| 00-MASTER/UCOS-UCAF-001/ucaf_engine.py | engine | YES | YES | NO | YES | NO | invocation planes=1 ['Makefile']; tests naming it=1 |
| 00-MASTER/UCOS-UFEP-001/ufep_engine.py | engine | YES | YES | NO | YES | NO | invocation planes=1 ['Makefile']; tests naming it=1 |
| 00-MASTER/UCOS-UGA-001/uga_engine.py | engine | YES | YES | YES | YES | YES | invocation planes=2 ['Makefile', 'verify.sh']; tests naming it=8 |
| 00-MASTER/UCOS-URAT-001/urat_engine.py | engine | YES | YES | NO | YES | NO | invocation planes=1 ['Makefile']; tests naming it=1 |
| 00-MASTER/UCOS-USIS-WAVE0/freeze_c4_engine.py | engine | YES | NO | NO | NO | NO | invocation planes=0 []; tests naming it=0 |
| 00-MASTER/UCOS-UTCE-001/utce_engine.py | engine | YES | YES | NO | YES | NO | invocation planes=1 ['Makefile']; tests naming it=1 |
| 00-MASTER/UEI-000001/uei_engine.py | engine | YES | YES | YES | NO | NO | invocation planes=2 ['.github/workflows/uei-gate.yml', 'Makefile']; tests naming it=0 |
| 00-MASTER/UER-000001/uer_engine.py | engine | YES | YES | YES | NO | NO | invocation planes=2 ['.github/workflows/uer-gate.yml', 'Makefile']; tests naming it=0 |
| 00-MASTER/UIS-001/uis_engine.py | engine | YES | YES | YES | NO | NO | invocation planes=3 ['.github/workflows/uec-gate.yml', '.github/workflows/uis-gate.yml', 'Makefile']; tests naming it=0 |
| 00-MASTER/UKAP-001/corpus_engine.py | engine | YES | YES | YES | YES | YES | invocation planes=2 ['.github/workflows/corpus-currency-gate.yml', 'Makefile']; tests naming it=1 |
| 00-MASTER/UMK-000001/umk_engine.py | engine | YES | YES | YES | NO | NO | invocation planes=2 ['.github/workflows/umk-gate.yml', 'Makefile']; tests naming it=0 |
| 00-MASTER/UPF-000001/upf_engine.py | engine | YES | YES | YES | NO | NO | invocation planes=2 ['.github/workflows/uprf-gate.yml', 'Makefile']; tests naming it=0 |
| 00-MASTER/URRC-000001/urrc_engine.py | engine | YES | YES | YES | NO | NO | invocation planes=2 ['.github/workflows/urrc-gate.yml', 'Makefile']; tests naming it=0 |

## §E — GATE — module gates

9 artifacts.

| Artifact | Type | Declared | Reachable | Executed | Measured | Certified | Evidence |
|---|---|---|---|---|---|---|---|
| engine/construct/gate.py | gate | YES | YES | YES | YES | YES | invocation planes=3 ['.github/workflows/ucon-gate.yml', 'Makefile', 'verify.sh']; tests naming it=2 |
| engine/enforcement_closure/gate.py | gate | YES | YES | YES | YES | YES | invocation planes=3 ['.github/workflows/uec-gate.yml', 'Makefile', 'verify.sh']; tests naming it=1 |
| engine/execution_environment/gate.py | gate | YES | YES | NO | YES | NO | invocation planes=1 ['Makefile']; tests naming it=1 |
| engine/infinite_scope/gate.py | gate | YES | YES | YES | YES | YES | invocation planes=3 ['.github/workflows/uisd-gate.yml', 'Makefile', 'verify.sh']; tests naming it=1 |
| engine/object_birth/gate.py | gate | YES | YES | YES | YES | YES | invocation planes=2 ['Makefile', 'verify.sh']; tests naming it=4 |
| engine/recursive_knowledge/gate.py | gate | YES | YES | YES | YES | YES | invocation planes=3 ['.github/workflows/urke-gate.yml', 'Makefile', 'verify.sh']; tests naming it=2 |
| engine/root_ontology/gate.py | gate | YES | YES | YES | YES | YES | invocation planes=2 ['Makefile', 'verify.sh']; tests naming it=2 |
| engine/uaue/gate.py | gate | YES | YES | YES | YES | YES | invocation planes=3 ['.github/workflows/uaue-gate.yml', 'Makefile', 'verify.sh']; tests naming it=8 |
| engine/verification_intelligence/gate.py | gate | YES | YES | YES | YES | YES | invocation planes=2 ['Makefile', 'verify.sh']; tests naming it=2 |

## §F — GATE — Makefile gate targets

54 artifacts.

| Artifact | Type | Declared | Reachable | Executed | Measured | Certified | Evidence |
|---|---|---|---|---|---|---|---|
| acee-gate | gate | YES | YES | YES | NO | YES | Makefile:1878 → @python3 00-MASTER/ACEE-000001/acee_engine.py --gate; target named in CI=0; enforcement in CI=1; in verify.sh=False |
| aee-gate | gate | YES | YES | YES | NO | YES | Makefile:1421 → @python3 00-MASTER/UCOS-AEE-001/aee_engine.py --tier standard --gate; target named in CI=0; enforcement in CI=1; in verify.sh=False |
| assimilate-gate | gate | YES | YES | YES | YES | YES | Makefile:492 → @python3 00-MASTER/UAKOS-CLOSURE-008/assimilation_engine.py --render --gate; target named in CI=0; enforcement in CI=1; in verify.sh=False |
| baseline-gate | gate | YES | YES | YES | YES | YES | Makefile:1601 → @python3 00-MASTER/BASELINE-001/baseline_engine.py --gate; target named in CI=0; enforcement in CI=1; in verify.sh=False |
| birth-gate | gate | YES | YES | YES | NO | NO | Makefile:2071 → @$(PY) -m engine.object_birth.gate --gate --quiet @echo "birth-gate: no object e; target named in CI=0; enforcement in CI=0; in verify.sh=True |
| closure-gate | gate | YES | YES | YES | NO | YES | Makefile:253 → @python3 00-MASTER/UAKOS-CLOSURE-002/closure_engine.py --gate; target named in CI=0; enforcement in CI=1; in verify.sh=False |
| closure-phase2-gate | gate | YES | YES | NO | NO | NO | Makefile:265 → @python3 00-MASTER/UAKOS-CLOSURE-002/phase2_engine.py --gate; target named in CI=0; enforcement in CI=0; in verify.sh=False |
| closure-phase3-gate | gate | YES | YES | NO | NO | NO | Makefile:278 → @python3 00-MASTER/UAKOS-CLOSURE-002/phase3_engine.py --gate; target named in CI=0; enforcement in CI=0; in verify.sh=False |
| closure009-baseline-gate | gate | YES | YES | YES | YES | YES | Makefile:1947 → @python3 00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py --baseline-gate; target named in CI=0; enforcement in CI=1; in verify.sh=False |
| closure009-gate | gate | YES | YES | YES | YES | YES | Makefile:1943 → @python3 00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py --gate; target named in CI=0; enforcement in CI=1; in verify.sh=False |
| cmg-gate | gate | YES | YES | YES | NO | NO | Makefile:558 → @./00-CMG/tools/cmg-gate.sh; target named in CI=0; enforcement in CI=0; in verify.sh=True |
| constitution-gate | gate | YES | YES | YES | NO | YES | Makefile:400 → @$(PY) -m platform.universal_foundation.constitution_cli conform --gate >/dev/nu; target named in CI=1; enforcement in CI=1; in verify.sh=False |
| convergence-gate | gate | YES | YES | YES | NO | YES | Makefile:422 → @$(PY) -m platform.universal_foundation.constitution_cli convergence --gate >/de; target named in CI=1; enforcement in CI=1; in verify.sh=False |
| corpus-gate | gate | YES | YES | YES | YES | YES | Makefile:468 → @python3 00-MASTER/UKAP-001/corpus_engine.py --render --gate; target named in CI=0; enforcement in CI=1; in verify.sh=False |
| final-closure-gate | gate | YES | YES | NO | NO | NO | Makefile:1498 → @python3 00-MASTER/P0-FINAL-CLOSURE-002/final_closure_engine.py --rounds 5 --clo; target named in CI=0; enforcement in CI=0; in verify.sh=False |
| foundation-gate | gate | YES | YES | NO | NO | NO | Makefile:1986 → @$(PY) -m platform.universal_foundation.cli determine --gate >/dev/null \ \|\| { e; target named in CI=0; enforcement in CI=0; in verify.sh=False |
| freeze-gate | gate | YES | YES | YES | NO | YES | Makefile:442 → @$(PY) -m platform.universal_foundation.constitution_cli freeze --with-suites --; target named in CI=1; enforcement in CI=1; in verify.sh=False |
| homing-gate | gate | YES | YES | NO | NO | NO | Makefile:363 → @$(PY) -m platform.universal_ownership.cli homing --gate >/dev/null 2>&1 \ \|\| { ; target named in CI=0; enforcement in CI=0; in verify.sh=False |
| infinite-scope-gate | gate | YES | YES | YES | NO | YES | Makefile:2114 → @$(PY) -m engine.infinite_scope.gate --quiet \ \|\| { echo "INFINITE SCOPE GATE CL; target named in CI=0; enforcement in CI=1; in verify.sh=True |
| lifecycle-closure-gate | gate | YES | YES | NO | NO | NO | Makefile:1475 → @python3 00-MASTER/P0-LIFECYCLE-CLOSURE-001/lifecycle_closure_engine.py --rounds; target named in CI=0; enforcement in CI=0; in verify.sh=False |
| mcos-gate | gate | YES | YES | YES | NO | YES | Makefile:1093 → @python3 00-MASTER/MCOS-000001/mcos_engine.py --gate; target named in CI=0; enforcement in CI=1; in verify.sh=False |
| publication-gate | gate | YES | YES | YES | NO | YES | Makefile:817 → @python3 -m intelligence.publication gate; target named in CI=0; enforcement in CI=1; in verify.sh=False |
| research-gate | gate | YES | YES | YES | NO | YES | Makefile:804 → @python3 -m intelligence.research gate; target named in CI=0; enforcement in CI=1; in verify.sh=False |
| research-publication-gate | gate | YES | NO | NO | NO | NO | Makefile:832 → EMPTY RECIPE; target named in CI=0; enforcement in CI=0; in verify.sh=False |
| rfp-gate | gate | YES | YES | YES | NO | YES | Makefile:1036 → @python3 00-MASTER/UCOS-RFP-001/rfp_engine.py --gate; target named in CI=0; enforcement in CI=1; in verify.sh=False |
| rib-gate | gate | YES | YES | YES | YES | YES | Makefile:863 → @python3 00-MASTER/UCOS-RIB-001/rib_engine.py --gate; target named in CI=0; enforcement in CI=1; in verify.sh=False |
| roadmap-gate | gate | YES | YES | YES | NO | YES | Makefile:514 → @python3 00-MASTER/UCOS-MXR-001/roadmap_engine.py --gate; target named in CI=0; enforcement in CI=1; in verify.sh=False |
| rpi-gate | gate | YES | YES | NO | YES | NO | Makefile:336 → @$(PY) -m platform.repository_intelligence.cli certify >/dev/null \ \|\| { echo "R; target named in CI=0; enforcement in CI=0; in verify.sh=False |
| selfaware-gate | gate | YES | YES | NO | NO | NO | Makefile:299 → @python3 -m engine.knowledge.cli capabilities --gate >/dev/null \ \|\| { echo "SEL; target named in CI=0; enforcement in CI=0; in verify.sh=False |
| uaep-gate | gate | YES | YES | YES | NO | YES | Makefile:1273 → @python3 00-MASTER/UAEP-000001/uaep_engine.py --gate; target named in CI=0; enforcement in CI=1; in verify.sh=False |
| uaie-gate | gate | YES | YES | YES | NO | YES | Makefile:1340 → @python3 00-MASTER/UAIE-000001/uaie_engine.py --gate; target named in CI=0; enforcement in CI=1; in verify.sh=False |
| uapf-gate | gate | YES | YES | NO | NO | NO | Makefile:1240 → @python3 -m platform.universal_pipeline.cli --gate; target named in CI=0; enforcement in CI=0; in verify.sh=False |
| uar-gate | gate | YES | YES | YES | NO | YES | Makefile:1199 → @python3 00-MASTER/UCOS-UAR-001/uar_engine.py --gate; target named in CI=0; enforcement in CI=1; in verify.sh=False |
| uaue-gate | gate | YES | YES | YES | YES | YES | Makefile:2028 → @$(PY) -m engine.uaue.gate --gate --quiet \ \|\| { echo "UAUE GATE CLOSED — run 'm; target named in CI=0; enforcement in CI=1; in verify.sh=True |
| ucaf-gate | gate | YES | YES | NO | NO | NO | Makefile:1552 → @python3 00-MASTER/UCOS-UCAF-001/ucaf_engine.py --gate; target named in CI=0; enforcement in CI=0; in verify.sh=False |
| uccep-gate | gate | YES | YES | YES | NO | YES | Makefile:591 → @python3 00-MASTER/UCCEP-000000/uccep_engine.py --tier standard --gate; target named in CI=0; enforcement in CI=1; in verify.sh=False |
| ucda-gate | gate | YES | YES | NO | NO | NO | Makefile:636 → @python3 00-MASTER/UCDA-000001/ucda_engine.py --gate; target named in CI=0; enforcement in CI=0; in verify.sh=False |
| ucef-gate | gate | YES | YES | YES | NO | YES | Makefile:1148 → @python3 00-MASTER/UCEF-000001/ucef_engine.py --gate; target named in CI=0; enforcement in CI=1; in verify.sh=False |
| ucl-gate | gate | YES | YES | YES | NO | YES | Makefile:1820 → @python3 00-MASTER/UCL-000001/ucl_engine.py --gate; target named in CI=0; enforcement in CI=1; in verify.sh=False |
| ucon-gate | gate | YES | YES | YES | NO | YES | Makefile:2185 → @$(PY) -m engine.construct.gate --gate --quiet \ \|\| { echo "UCON GATE CLOSED — r; target named in CI=0; enforcement in CI=1; in verify.sh=True |
| ucpa-gate | gate | YES | YES | YES | NO | NO | Makefile:2349 → @$(PY) -m engine.root_ontology.gate --quiet \ \|\| { echo "UCPA GATE CLOSED — run ; target named in CI=0; enforcement in CI=0; in verify.sh=True |
| uec-gate | gate | YES | YES | YES | YES | YES | Makefile:2251 → @$(PY) -m engine.enforcement_closure.gate --gate --quiet \ \|\| { echo "UEC GATE C; target named in CI=0; enforcement in CI=1; in verify.sh=True |
| uei-gate | gate | YES | YES | YES | NO | YES | Makefile:754 → @python3 00-MASTER/UEI-000001/uei_engine.py --gate; target named in CI=0; enforcement in CI=1; in verify.sh=False |
| uer-gate | gate | YES | YES | YES | NO | YES | Makefile:674 → @python3 00-MASTER/UER-000001/uer_engine.py --gate; target named in CI=0; enforcement in CI=1; in verify.sh=False |
| ufep-gate | gate | YES | YES | NO | NO | NO | Makefile:1741 → @python3 00-MASTER/UCOS-UFEP-001/ufep_engine.py --gate; target named in CI=0; enforcement in CI=0; in verify.sh=False |
| uga-gate | gate | YES | YES | YES | NO | NO | Makefile:2338 → @$(PY) 00-MASTER/UCOS-UGA-001/uga_engine.py gate >/dev/null \ \|\| { echo "UGA GAT; target named in CI=0; enforcement in CI=0; in verify.sh=True |
| uis-gate | gate | YES | YES | YES | NO | YES | Makefile:1639 → @python3 00-MASTER/UIS-001/uis_engine.py --gate; target named in CI=0; enforcement in CI=1; in verify.sh=False |
| umk-gate | gate | YES | YES | YES | NO | YES | Makefile:947 → @python3 00-MASTER/UMK-000001/umk_engine.py --gate; target named in CI=0; enforcement in CI=1; in verify.sh=False |
| uprf-gate | gate | YES | YES | YES | NO | YES | Makefile:992 → @python3 00-MASTER/UPF-000001/upf_engine.py --gate; target named in CI=0; enforcement in CI=1; in verify.sh=False |
| urat-gate | gate | YES | YES | NO | NO | NO | Makefile:1672 → @python3 00-MASTER/UCOS-URAT-001/urat_engine.py --gate; target named in CI=0; enforcement in CI=0; in verify.sh=False |
| urke-gate | gate | YES | YES | YES | NO | YES | Makefile:2300 → @$(PY) -m engine.recursive_knowledge.gate --gate --quiet \ \|\| { echo "URKE GATE ; target named in CI=0; enforcement in CI=1; in verify.sh=True |
| urrc-gate | gate | YES | YES | YES | NO | YES | Makefile:709 → @python3 00-MASTER/URRC-000001/urrc_engine.py --gate; target named in CI=0; enforcement in CI=1; in verify.sh=False |
| utce-gate | gate | YES | YES | NO | NO | NO | Makefile:1702 → @python3 00-MASTER/UCOS-UTCE-001/utce_engine.py --gate; target named in CI=0; enforcement in CI=0; in verify.sh=False |
| uvi-gate | gate | YES | YES | YES | NO | NO | Makefile:2142 → @$(PY) -m engine.verification_intelligence.gate --gate --quiet \ \|\| { echo "UVI ; target named in CI=0; enforcement in CI=0; in verify.sh=True |

## §G — GATE — verify.sh stages

18 artifacts.

| Artifact | Type | Declared | Reachable | Executed | Measured | Certified | Evidence |
|---|---|---|---|---|---|---|---|
| autonomous universal evolution (UAUE gate, every declared obligation) | gate | YES | YES | YES | NO | PARTIAL | verify.sh run_stage "autonomous universal evolution (UAUE gate, every declared obligation)" (order 8); UVI stage_registry reusable=None; tests naming it=0 |
| constitutional primitive alignment (UCPA-000001, root ontology measured and reduced) | gate | YES | YES | YES | NO | PARTIAL | verify.sh run_stage "constitutional primitive alignment (UCPA-000001, root ontology measured and reduced)" (order 12); UVI stage_registry reusable=None; tests naming it=0 |
| coverage report | gate | YES | YES | YES | YES | PARTIAL | verify.sh run_stage "coverage report" (order 17); UVI stage_registry reusable=None; tests naming it=1 |
| evolution surface replay (history + 18 registers) | gate | YES | YES | YES | NO | PARTIAL | verify.sh run_stage "evolution surface replay (history + 18 registers)" (order 9); UVI stage_registry reusable=None; tests naming it=0 |
| governance enforce --pre | gate | YES | YES | YES | NO | PARTIAL | verify.sh run_stage "governance enforce --pre" (order 4); UVI stage_registry reusable=None; tests naming it=0 |
| meta-constitutional conformance (CMG-INV-01..12) | gate | YES | YES | YES | NO | PARTIAL | verify.sh run_stage "meta-constitutional conformance (CMG-INV-01..12)" (order 6); UVI stage_registry reusable=None; tests naming it=0 |
| prerequisite generation (knowledge · determinism · closure 1-3) | gate | YES | YES | YES | NO | PARTIAL | verify.sh run_stage "prerequisite generation (knowledge · determinism · closure 1-3)" (order 2); UVI stage_registry reusable=None; tests naming it=0 |
| pytest + coverage gate (--cov-fail-under=90) | gate | YES | YES | YES | YES | PARTIAL | verify.sh run_stage "pytest + coverage gate (--cov-fail-under=90)" (order 3); UVI stage_registry reusable=None; tests naming it=1 |
| registration observation (register.sh --observe, read-only) | gate | YES | YES | YES | NO | PARTIAL | verify.sh run_stage "registration observation (register.sh --observe, read-only)" (order 18); UVI stage_registry reusable=None; tests naming it=0 |
| registry validate (schema + integrity) | gate | YES | YES | YES | NO | PARTIAL | verify.sh run_stage "registry validate (schema + integrity)" (order 5); UVI stage_registry reusable=None; tests naming it=0 |
| ruff lint + format-check (engine + platform) | gate | YES | YES | YES | NO | PARTIAL | verify.sh run_stage "ruff lint + format-check (engine + platform)" (order 1); UVI stage_registry reusable=None; tests naming it=0 |
| universal construct foundation (UCON-000001, every construct disposed and nothing silently ignored) | gate | YES | YES | YES | NO | PARTIAL | verify.sh run_stage "universal construct foundation (UCON-000001, every construct disposed and nothing silently ignored)" (order 14); UVI stage_registry reusable=None; tests naming it=0 |
| universal enforcement closure (UEC-000001, every protection governed, invoked twice and covered) | gate | YES | YES | YES | NO | PARTIAL | verify.sh run_stage "universal enforcement closure (UEC-000001, every protection governed, invoked twice and covered)" (order 15); UVI stage_registry reusable=None; tests naming it=0 |
| universal infinite scope and direction (UISD-000001, unbounded and self-applied) | gate | YES | YES | YES | NO | PARTIAL | verify.sh run_stage "universal infinite scope and direction (UISD-000001, unbounded and self-applied)" (order 11); UVI stage_registry reusable=None; tests naming it=0 |
| universal object birth contract (UOBC-000001, identity before existence) | gate | YES | YES | YES | NO | PARTIAL | verify.sh run_stage "universal object birth contract (UOBC-000001, identity before existence)" (order 10); UVI stage_registry reusable=None; tests naming it=0 |
| universal object governance (UGA-INV-01..10) | gate | YES | YES | YES | NO | PARTIAL | verify.sh run_stage "universal object governance (UGA-INV-01..10)" (order 7); UVI stage_registry reusable=None; tests naming it=0 |
| universal recursive knowledge foundation (URKE-000001, every unknown governed and no mechanism closed against a future domain) | gate | YES | YES | YES | NO | PARTIAL | verify.sh run_stage "universal recursive knowledge foundation (URKE-000001, every unknown governed and no mechanism closed against a future domain)" (order 16); UVI stage_registry reusable=None; tests naming it=0 |
| universal verification intelligence (UVI-000001, selection derived and assurance preserved) | gate | YES | YES | YES | NO | PARTIAL | verify.sh run_stage "universal verification intelligence (UVI-000001, selection derived and assurance preserved)" (order 13); UVI stage_registry reusable=None; tests naming it=0 |

## §H — WORKFLOW

32 artifacts.

| Artifact | Type | Declared | Reachable | Executed | Measured | Certified | Evidence |
|---|---|---|---|---|---|---|---|
| .github/workflows/acee-gate.yml | workflow | YES | YES | YES | YES | YES | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=True |
| .github/workflows/aee-gate.yml | workflow | YES | YES | YES | NO | NO | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=False |
| .github/workflows/assimilation-gate.yml | workflow | YES | YES | YES | YES | YES | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=True |
| .github/workflows/baseline-gate.yml | workflow | YES | YES | YES | YES | YES | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=True |
| .github/workflows/closure009-gate.yml | workflow | YES | YES | YES | NO | NO | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=2; render+diff currency=False |
| .github/workflows/corpus-currency-gate.yml | workflow | YES | YES | YES | YES | YES | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=True |
| .github/workflows/determinism.yml | workflow | YES | YES | YES | NO | NO | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=False |
| .github/workflows/ec1-ci.yml | workflow | YES | YES | YES | NO | NO | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=False |
| .github/workflows/mcos-gate.yml | workflow | YES | YES | YES | NO | NO | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=False |
| .github/workflows/research-publication-gate.yml | workflow | YES | YES | YES | NO | NO | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=False |
| .github/workflows/rfp-gate.yml | workflow | YES | YES | YES | NO | NO | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=False |
| .github/workflows/rib-gate.yml | workflow | YES | YES | YES | NO | NO | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=False |
| .github/workflows/roadmap-gate.yml | workflow | YES | YES | YES | YES | YES | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=True |
| .github/workflows/uaep-gate.yml | workflow | YES | YES | YES | YES | YES | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=True |
| .github/workflows/uaie-gate.yml | workflow | YES | YES | YES | YES | YES | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=True |
| .github/workflows/uar-gate.yml | workflow | YES | YES | YES | YES | YES | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=True |
| .github/workflows/uaue-gate.yml | workflow | YES | YES | YES | YES | YES | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=True |
| .github/workflows/uccep-gate.yml | workflow | YES | YES | YES | NO | NO | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=False |
| .github/workflows/ucef-gate.yml | workflow | YES | YES | YES | YES | YES | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=True |
| .github/workflows/ucl-gate.yml | workflow | YES | YES | YES | YES | YES | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=True |
| .github/workflows/ucon-gate.yml | workflow | YES | YES | YES | NO | NO | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=False |
| .github/workflows/ucos-registration-gate.yml | workflow | YES | YES | YES | NO | NO | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=False |
| .github/workflows/uec-gate.yml | workflow | YES | YES | YES | NO | NO | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=False |
| .github/workflows/uei-gate.yml | workflow | YES | YES | YES | NO | NO | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=False |
| .github/workflows/uer-gate.yml | workflow | YES | YES | YES | NO | NO | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=False |
| .github/workflows/ufc-gate.yml | workflow | YES | YES | YES | NO | NO | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=False |
| .github/workflows/uis-gate.yml | workflow | YES | YES | YES | YES | YES | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=True |
| .github/workflows/uisd-gate.yml | workflow | YES | YES | YES | NO | NO | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=False |
| .github/workflows/umk-gate.yml | workflow | YES | YES | YES | NO | NO | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=False |
| .github/workflows/uprf-gate.yml | workflow | YES | YES | YES | NO | NO | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=False |
| .github/workflows/urke-gate.yml | workflow | YES | YES | YES | NO | NO | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=False |
| .github/workflows/urrc-gate.yml | workflow | YES | YES | YES | NO | NO | on: push=True pull_request=True dispatch=False schedule=False; continue-on-error=0; render+diff currency=False |

## §I — CERTIFICATION OBJECT — governed declarations

20 artifacts.

| Artifact | Type | Declared | Reachable | Executed | Measured | Certified | Evidence |
|---|---|---|---|---|---|---|---|
| 00-MASTER/ACEE-000001/acee-declaration.json | certification object | YES | YES | YES | NO | YES | code consumers=1; invocation planes=2 ['.github/workflows/acee-gate.yml', 'Makefile']; tests naming it=0 |
| 00-MASTER/BASELINE-001/baseline-declaration.json | certification object | YES | YES | YES | YES | YES | code consumers=1; invocation planes=2 ['.github/workflows/baseline-gate.yml', 'Makefile']; tests naming it=1 |
| 00-MASTER/UCL-000001/ucl-declaration.json | certification object | YES | YES | YES | YES | YES | code consumers=1; invocation planes=4 ['.github/workflows/acee-gate.yml', '.github/workflows/ucl-gate.yml', '.github/workflows/uisd-gate.yml', 'Makefile']; tests naming it=2 |
| 00-MASTER/UCON-000001/ucon-declaration.json | certification object | YES | YES | YES | YES | YES | code consumers=3; invocation planes=3 ['.github/workflows/ucon-gate.yml', 'Makefile', 'verify.sh']; tests naming it=2 |
| 00-MASTER/UCOS-AEE-001/aee-declaration.json | certification object | YES | YES | YES | YES | YES | code consumers=1; invocation planes=3 ['.github/workflows/acee-gate.yml', '.github/workflows/aee-gate.yml', 'Makefile']; tests naming it=3 |
| 00-MASTER/UCOS-CEU-001/ceu-declaration.json | certification object | YES | NO | YES | NO | NO | code consumers=0; invocation planes=2 ['.github/workflows/ucon-gate.yml', 'verify.sh']; tests naming it=0 |
| 00-MASTER/UCOS-RFP-001/rfp-declaration.json | certification object | YES | YES | YES | NO | YES | code consumers=1; invocation planes=3 ['.github/workflows/aee-gate.yml', '.github/workflows/rfp-gate.yml', 'Makefile']; tests naming it=0 |
| 00-MASTER/UCOS-UFEP-001/ufep-declaration.json | certification object | YES | YES | NO | YES | YES | code consumers=1; invocation planes=1 ['Makefile']; tests naming it=1 |
| 00-MASTER/UCOS-UGA-001/uga-declaration.json | certification object | YES | YES | YES | YES | YES | code consumers=1; invocation planes=2 ['Makefile', 'verify.sh']; tests naming it=8 |
| 00-MASTER/UCOS-URAT-001/urat-declaration.json | certification object | YES | YES | NO | YES | YES | code consumers=1; invocation planes=1 ['Makefile']; tests naming it=1 |
| 00-MASTER/UCOS-URR-001/urr-declaration.json | certification object | YES | NO | NO | NO | NO | code consumers=0; invocation planes=0 []; tests naming it=0 |
| 00-MASTER/UCOS-UTCE-001/utce-declaration.json | certification object | YES | YES | NO | YES | YES | code consumers=1; invocation planes=1 ['Makefile']; tests naming it=1 |
| 00-MASTER/UCPA-000001/ucpa-declaration.json | certification object | YES | YES | YES | YES | YES | code consumers=2; invocation planes=2 ['.github/workflows/ucon-gate.yml', 'verify.sh']; tests naming it=1 |
| 00-MASTER/UCXI-000001/ucxi-declaration.json | certification object | YES | NO | YES | YES | NO | code consumers=0; invocation planes=1 ['.github/workflows/ucon-gate.yml']; tests naming it=3 |
| 00-MASTER/UEC-000001/uec-declaration.json | certification object | YES | YES | YES | YES | YES | code consumers=2; invocation planes=4 ['.github/workflows/uec-gate.yml', '.github/workflows/urke-gate.yml', 'Makefile', 'verify.sh']; tests naming it=1 |
| 00-MASTER/UEG-000001/ueg-declaration.json | certification object | YES | YES | YES | YES | YES | code consumers=3; invocation planes=2 ['Makefile', 'verify.sh']; tests naming it=1 |
| 00-MASTER/UIS-001/uis-declaration.json | certification object | YES | YES | YES | NO | YES | code consumers=1; invocation planes=2 ['.github/workflows/uis-gate.yml', 'Makefile']; tests naming it=0 |
| 00-MASTER/UISD-000001/uisd-declaration.json | certification object | YES | YES | YES | YES | YES | code consumers=1; invocation planes=3 ['.github/workflows/uisd-gate.yml', 'Makefile', 'verify.sh']; tests naming it=2 |
| 00-MASTER/URKE-000001/urke-declaration.json | certification object | YES | YES | YES | YES | YES | code consumers=3; invocation planes=3 ['.github/workflows/urke-gate.yml', 'Makefile', 'verify.sh']; tests naming it=1 |
| 00-MASTER/UVI-000001/uvi-declaration.json | certification object | YES | YES | YES | YES | YES | code consumers=1; invocation planes=3 ['.github/workflows/ec1-ci.yml', 'Makefile', 'verify.sh']; tests naming it=1 |

## §J — CERTIFICATION OBJECT — persisted JSON

146 artifacts.

| Artifact | Type | Declared | Reachable | Executed | Measured | Certified | Evidence |
|---|---|---|---|---|---|---|---|
| 00-BOOK/DATA/certification.json | certification object | YES | YES | YES | NO | NO | producer=none declared; producing modules=3 by full path + 0 in an ancestor directory; digest field=NONE; verdict=CERTIFIED |
| 00-MASTER/P0-FINAL-CLOSURE-002/UCOS-FIXED-POINT-CERTIFICATION.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 1 in an ancestor directory; digest field=digest; verdict=FIXED POINT CERTIFIED |
| 00-MASTER/P0-FINAL-CLOSURE-002/UCOS-PRISTINE-CLONE-CERTIFICATION.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 1 in an ancestor directory; digest field=digest; verdict=REPRODUCIBILITY CERTIFIED |
| 00-MASTER/P0-FINAL-CLOSURE-002/UCOS-UNCONDITIONAL-CERTIFICATION.json | certification object | YES | NO | NO | NO | NO | producer=none declared; producing modules=0 by full path + 0 in an ancestor directory; digest field=NONE; verdict=none |
| 00-MASTER/UCOS-UGA-001/07-CERTIFICATION.json | certification object | YES | YES | YES | YES | YES | producer=00-MASTER/UCOS-UGA-001/uga_engine.py; producing modules=0 by full path + 1 in an ancestor directory; digest field=existence_digest; verdict=CERTIFIED |
| application/_evidence/EC3-B12-U01/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| application/_evidence/EC3-B12-U01/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| application/_evidence/EC3-B12-U01/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=entry_hash; verdict=certified |
| application/_evidence/EC3-B12-U02/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| application/_evidence/EC3-B12-U02/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| application/_evidence/EC3-B12-U02/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=entry_hash; verdict=certified |
| application/_evidence/EC3-B12-U03/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| application/_evidence/EC3-B12-U03/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| application/_evidence/EC3-B12-U03/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=entry_hash; verdict=certified |
| application/_evidence/EC3-B12-U04/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| application/_evidence/EC3-B12-U04/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| application/_evidence/EC3-B12-U04/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=entry_hash; verdict=certified |
| application/_evidence/EC3-B12-U05/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| application/_evidence/EC3-B12-U05/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| application/_evidence/EC3-B12-U05/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=entry_hash; verdict=certified |
| application/_evidence/EC3-B12-U06/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| application/_evidence/EC3-B12-U06/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| application/_evidence/EC3-B12-U06/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=entry_hash; verdict=certified |
| application/_evidence/EC3-B12-U07/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| application/_evidence/EC3-B12-U07/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| application/_evidence/EC3-B12-U07/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=entry_hash; verdict=certified |
| application/_evidence/EC3-B12-U08/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| application/_evidence/EC3-B12-U08/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| application/_evidence/EC3-B12-U08/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=entry_hash; verdict=certified |
| application/_evidence/EC3-B12-U09/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| application/_evidence/EC3-B12-U09/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| application/_evidence/EC3-B12-U09/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=entry_hash; verdict=certified |
| application/_evidence/EC3-B12-U10/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| application/_evidence/EC3-B12-U10/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| application/_evidence/EC3-B12-U10/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=entry_hash; verdict=certified |
| application/_evidence/EC3-B12-U11/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| application/_evidence/EC3-B12-U11/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| application/_evidence/EC3-B12-U11/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=entry_hash; verdict=certified |
| data/_evidence/EC3-B10-U01/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| data/_evidence/EC3-B10-U01/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| data/_evidence/EC3-B10-U01/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=entry_hash; verdict=certified |
| data/_evidence/EC3-B10-U02/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| data/_evidence/EC3-B10-U02/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| data/_evidence/EC3-B10-U02/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=entry_hash; verdict=certified |
| data/_evidence/EC3-B10-U03/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| data/_evidence/EC3-B10-U03/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| data/_evidence/EC3-B10-U03/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=entry_hash; verdict=certified |
| data/_evidence/EC3-B10-U04/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| data/_evidence/EC3-B10-U04/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| data/_evidence/EC3-B10-U04/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=entry_hash; verdict=certified |
| data/_evidence/EC3-B10-U05/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| data/_evidence/EC3-B10-U05/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| data/_evidence/EC3-B10-U05/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=entry_hash; verdict=certified |
| data/_evidence/EC3-B10-U06/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| data/_evidence/EC3-B10-U06/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| data/_evidence/EC3-B10-U06/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=entry_hash; verdict=certified |
| data/_evidence/EC3-B10-U07/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| data/_evidence/EC3-B10-U07/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| data/_evidence/EC3-B10-U07/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=entry_hash; verdict=certified |
| data/_evidence/EC3-B10-U08/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| data/_evidence/EC3-B10-U08/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| data/_evidence/EC3-B10-U08/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=entry_hash; verdict=certified |
| data/_evidence/EC3-B10-U09/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| data/_evidence/EC3-B10-U09/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| data/_evidence/EC3-B10-U09/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=entry_hash; verdict=certified |
| data/_evidence/EC3-B10-U10/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| data/_evidence/EC3-B10-U10/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| data/_evidence/EC3-B10-U10/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=entry_hash; verdict=certified |
| data/_evidence/EC3-B10-U11/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| data/_evidence/EC3-B10-U11/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| data/_evidence/EC3-B10-U11/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=entry_hash; verdict=certified |
| data/_evidence/EC3-B10-U12/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| data/_evidence/EC3-B10-U12/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| data/_evidence/EC3-B10-U12/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 12 in an ancestor directory; digest field=entry_hash; verdict=certified |
| infrastructure/_evidence/EC3-B13-U01/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| infrastructure/_evidence/EC3-B13-U01/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| infrastructure/_evidence/EC3-B13-U01/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=entry_hash; verdict=certified |
| infrastructure/_evidence/EC3-B13-U02/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| infrastructure/_evidence/EC3-B13-U02/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| infrastructure/_evidence/EC3-B13-U02/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=entry_hash; verdict=certified |
| infrastructure/_evidence/EC3-B13-U03/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| infrastructure/_evidence/EC3-B13-U03/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| infrastructure/_evidence/EC3-B13-U03/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=entry_hash; verdict=certified |
| infrastructure/_evidence/EC3-B13-U04/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| infrastructure/_evidence/EC3-B13-U04/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| infrastructure/_evidence/EC3-B13-U04/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=entry_hash; verdict=certified |
| infrastructure/_evidence/EC3-B13-U05/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| infrastructure/_evidence/EC3-B13-U05/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| infrastructure/_evidence/EC3-B13-U05/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=entry_hash; verdict=certified |
| infrastructure/_evidence/EC3-B13-U06/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| infrastructure/_evidence/EC3-B13-U06/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| infrastructure/_evidence/EC3-B13-U06/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=entry_hash; verdict=certified |
| infrastructure/_evidence/EC3-B13-U07/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| infrastructure/_evidence/EC3-B13-U07/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| infrastructure/_evidence/EC3-B13-U07/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=entry_hash; verdict=certified |
| infrastructure/_evidence/EC3-B13-U08/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| infrastructure/_evidence/EC3-B13-U08/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| infrastructure/_evidence/EC3-B13-U08/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=entry_hash; verdict=certified |
| infrastructure/_evidence/EC3-B13-U09/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| infrastructure/_evidence/EC3-B13-U09/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| infrastructure/_evidence/EC3-B13-U09/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=entry_hash; verdict=certified |
| infrastructure/_evidence/EC3-B13-U10/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| infrastructure/_evidence/EC3-B13-U10/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| infrastructure/_evidence/EC3-B13-U10/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=entry_hash; verdict=certified |
| infrastructure/_evidence/EC3-B13-U11/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| infrastructure/_evidence/EC3-B13-U11/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| infrastructure/_evidence/EC3-B13-U11/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 11 in an ancestor directory; digest field=entry_hash; verdict=certified |
| service/_evidence/EC3-B11-U01/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| service/_evidence/EC3-B11-U01/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| service/_evidence/EC3-B11-U01/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=entry_hash; verdict=certified |
| service/_evidence/EC3-B11-U02/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| service/_evidence/EC3-B11-U02/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| service/_evidence/EC3-B11-U02/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=entry_hash; verdict=certified |
| service/_evidence/EC3-B11-U03/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| service/_evidence/EC3-B11-U03/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| service/_evidence/EC3-B11-U03/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=entry_hash; verdict=certified |
| service/_evidence/EC3-B11-U04/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| service/_evidence/EC3-B11-U04/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| service/_evidence/EC3-B11-U04/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=entry_hash; verdict=certified |
| service/_evidence/EC3-B11-U05/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| service/_evidence/EC3-B11-U05/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| service/_evidence/EC3-B11-U05/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=entry_hash; verdict=certified |
| service/_evidence/EC3-B11-U06/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| service/_evidence/EC3-B11-U06/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| service/_evidence/EC3-B11-U06/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=entry_hash; verdict=certified |
| service/_evidence/EC3-B11-U07/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| service/_evidence/EC3-B11-U07/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| service/_evidence/EC3-B11-U07/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=entry_hash; verdict=certified |
| service/_evidence/EC3-B11-U08/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| service/_evidence/EC3-B11-U08/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| service/_evidence/EC3-B11-U08/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=entry_hash; verdict=certified |
| service/_evidence/EC3-B11-U09/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| service/_evidence/EC3-B11-U09/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| service/_evidence/EC3-B11-U09/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=entry_hash; verdict=certified |
| service/_evidence/EC3-B11-U10/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| service/_evidence/EC3-B11-U10/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| service/_evidence/EC3-B11-U10/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=entry_hash; verdict=certified |
| service/_evidence/EC3-B11-U11/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| service/_evidence/EC3-B11-U11/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| service/_evidence/EC3-B11-U11/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=entry_hash; verdict=certified |
| service/_evidence/EC3-B11-U12/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| service/_evidence/EC3-B11-U12/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| service/_evidence/EC3-B11-U12/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=entry_hash; verdict=certified |
| service/_evidence/EC3-B11-U13/cce-certification.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| service/_evidence/EC3-B11-U13/certification-evidence.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=evidence_sha256; verdict=pass |
| service/_evidence/EC3-B11-U13/certification-ledger.json | certification object | YES | YES | NO | YES | PARTIAL | producer=none declared; producing modules=0 by full path + 13 in an ancestor directory; digest field=entry_hash; verdict=certified |

## §K — CERTIFICATION OBJECT — Markdown assertions

141 artifacts.

| Artifact | Type | Declared | Reachable | Executed | Measured | Certified | Evidence |
|---|---|---|---|---|---|---|---|
| 00-BOOK/ADVANCEMENT/UKB-ADV-014-DIGITAL-TWIN-CERTIFICATION-ARCHITECTURE.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-BOOK/MASTER-BOOK/UMB-017-CERTIFICATION-ARCHITECTURE.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-BOOK/MASTER-BOOK/UMB-CERT-001-MASTER-BOOK-DIGITAL-TWIN-PROGRAM-CERTIFICATION-DETERMINATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-BOOK/MASTER-BOOK/UMB-IMP-006-DIGITAL-TWIN-CERTIFICATION-RUNTIME-REALIZATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-BOOK/MASTER-BOOK/UMB-REMED-001-CRITICAL-CERTIFICATION-FINDINGS-REMEDIATION-AND-CLOSURE.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-BOOK/REGISTRIES/CERTIFICATION-REGISTRY.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-CEP/CEP-005-CONSTITUTIONAL-CERTIFICATION-CONSTITUTION.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-CEP/STAGE-04-S4-05-SECURITY-VALIDATION-CERTIFICATION-FREEZE-READINESS.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-CEP/STAGE-04-S4-10-INFRASTRUCTURE-014-GOVERNANCE-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-CMG/CMG-000007-CONSTITUTIONAL-CERTIFICATION-STRATEGY.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/ACEE-000001/13-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/ACEE-000001/15-OMEGA-E05-EXIT-CERTIFICATION.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/BASELINE-001/06-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/CMG-FOUNDATION-PERMANENT-FREEZE-CERTIFICATION-AUDIT.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/IMPLEMENT-001A/03-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/IMPLEMENT-001B/08-CERTIFICATION-STATUS.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/IMPLEMENT-001C/05-CERTIFICATION-REPORT.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/IMPLEMENT-001E/01-CERTIFICATION-REPORT.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/IMR-0000/20-VALIDATION-AND-CERTIFICATION-FRAMEWORK.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/IMR-003A/16-CIOS-CERTIFICATION-INTEGRATION-MODEL.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/MCOS-000001/07-UNIVERSAL-CERTIFICATION-MATRIX.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/MCOS-000001/08-FINAL-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/MCOS-000001/MISSION-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/RA-003/03-KNOWLEDGE-ONCE-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UAEP-000001/03-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UAIE-000001/06-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UAKOS-CLOSURE-003/08-CERTIFICATION-READINESS-REPORT.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UAKOS-CLOSURE-006/CONST-15-ARCHITECTURAL-COMPLETENESS-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UAKOS-CLOSURE-008/07-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UAKOS-PHASE-001A-R1/00-FINAL-CONSTITUTIONAL-BASELINE-CERTIFICATION.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UAKOS-PHASE-001A-R1/09-CERTIFICATION-REGISTER.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UAKOS-PHASE-003A-R2/08-FREEZE-C3-CERTIFICATION-REPORT.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UAKOS-PHASE-004/06-CERTIFICATION-PLANNING-REGISTER.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UAKOS-PHASE-005/04-CERTIFICATION-GOVERNANCE-REGISTER.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UAUE-000001/11-EVOLUTION-CERTIFICATION-REPORT.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCCEP-000000/03-META-MODEL-GOVERNANCE-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCCEP-000000/04-UNIVERSAL-REGISTRY-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCCEP-000000/05-REPOSITORY-GOVERNANCE-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCCEP-000000/12-CERTIFICATION-INTELLIGENCE.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCCEP-000000/15-CONTINUOUS-CONSTITUTIONAL-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCCEP-000000/18-DECISION-ASSIMILATION-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCCEP-000007/11-CERTIFICATION-INVENTORY.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCEF-000001/10-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UCL-000001/10-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UCL-000001/13-SELF-EVOLUTION-AND-OMEGA-E05-READINESS-CERTIFICATION.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-AB-001/15-ARCHITECTURE-BASELINE-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-AEE-001/07-CONVERGENCE-CERTIFICATION.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-AEE-001/11-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-CVER-001/02-CONTEXT-ASSIMILATION-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-CVER-001/03-REFERENCE-CORPUS-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-CVER-001/04-DIGITAL-TWIN-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-CVER-001/05-GRAPH-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-CVER-001/06-TRACEABILITY-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-CVER-001/07-GOVERNANCE-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-EG-001/15-CERTIFICATION-COMPLIANCE-RULES.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-MXR-001/08-CERTIFICATION-GATES.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-NUCLEUS-001/07-TRACEABILITY-VALIDATION-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-RIB-001/13-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-UCAF-001/06-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-UICM-000001/05-CLOSURE-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-URAT-001/03-COVERAGE-AND-CERTIFICATION.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-USIS-001/10-USIS-ARCHITECTURAL-PROPERTIES-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-USIS-WAVE0/ACCEPTANCE/03-DETERMINISM-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-USIS-WAVE0/ACCEPTANCE/05-BASELINE-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-USIS-WAVE0/FREEZE-C4/03-FREEZE-C4-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-USIS-WAVE1/MISSION-001-USIS-001/03-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-USIS-WAVE1/MISSION-002-USIS-002/03-USIS002-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-USIS-WAVE1/MISSION-003-USIS-003/03-USIS003-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-USIS-WAVE1/MISSION-004-USIS-004/03-USIS004-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-USIS-WAVE2/BLUEPRINTS/USIS-015-CERTIFICATION-ARCHITECTURE.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-USIS-WAVE2/INTEGRATION/08-CERTIFICATION-REPORT.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-USIS-WAVE2/MISSION-006-USIS-006/04-CERTIFICATION-REPORT.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-USIS-WAVE2/MISSION-007-USIS-007/04-CERTIFICATION-REPORT.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-USIS-WAVE2/MISSION-008-USIS-008/05-CERTIFICATION-REPORT.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-USIS-WAVE2/MISSION-009-USIS-009/04-CERTIFICATION-REPORT.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-USIS-WAVE2/MISSION-010-USIS-010/06-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-USIS-WAVE2/MISSION-011-USIS-011/06-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-USIS-WAVE2/MISSION-012-USIS-012/06-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-USIS-WAVE2/MISSION-013-USIS-013/06-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-USIS-WAVE2/MISSION-017-USIS-017/06-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-USIS-WAVE3-REGISTRY/06-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-USIS-WAVE3-REGISTRY/08-WHOLE-CORPUS-CERTIFICATION-REPORT.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UCOS-UTCE-001/03-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UEI-000001/20-CERTIFICATION-REPORT.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UER-000001/11-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UIS-001/07-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UKAP-001/07-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UKAP-001/MISSION-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 00-MASTER/UMK-000001/07-UNIVERSAL-CERTIFICATION-MATRIX.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UMK-000001/08-FINAL-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UPF-000001/07-UNIVERSAL-CERTIFICATION-MATRIX.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/UPF-000001/08-FINAL-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 00-MASTER/URRC-000001/14-VALIDATION-CERTIFICATION-COMPLIANCE-BINDING.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 01-CONSTITUTIONAL-COMPLETENESS-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 02-ARCHITECTURAL-STABILITY-CERTIFICATION.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 02-MASTER/EC2-PROGRAM-CLOSURE-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 02-MASTER/UCOS-Ω∞-CONSTITUTIONAL-READINESS-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 02-MASTER/UCOS-Ω∞-UNIVERSAL-CERTIFICATION-ARCHITECTURE-CONSTITUTION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 02-MASTER/UCOS-Ω∞-ZG-CERT-001-ZERO-GAP-PROGRAM-CERTIFICATION-RECORD.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 03-CONSTITUTIONAL-UNBOUNDEDNESS-CERTIFICATION.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 03-FINAL-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 04-HIDDEN-FINITE-ASSUMPTION-CERTIFICATION.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| 05-CONSTITUTIONAL-CLOSURE-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 07-CERTIFICATION-READINESS.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 07-CERTIFICATION-RECONCILIATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 08-RUNTIME/RUNTIME-GOV-002-RUNTIME-PROGRAM-CERTIFICATION-DETERMINATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 09-WAVE-01-READINESS-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 10-FINAL-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 100-PERCENT-IMPLEMENTATION-READINESS-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 12-APPLICATION/APPLICATION-GOV-999-UNIVERSAL-APPLICATION-PROGRAM-FINAL-CERTIFICATION-DETERMINATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| 15-UNIVERSAL-SCIENCE-INTELLIGENCE/16-CERTIFICATION/USIS-015-CERTIFICATION-ARCHITECTURE.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| CERTIFICATION-ARCHITECTURE-DETERMINATION-DRAFT.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| CERTIFICATION-OWNERSHIP-RECONCILIATION-DETERMINATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| CERTIFICATION-OWNERSHIP-RECONCILIATION-FINDING.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| EVO-USIS-014/06-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| EVO-USIS-015/06-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| EVO-USIS-015/08-WHOLE-CORPUS-CERTIFICATION-REPORT.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| EVO-USIS-016/06-CERTIFICATION-REPORT.md | certification object | PARTIAL | YES | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: True; digest field: NONE; producer: NONE |
| EVO-USIS-016/08-WHOLE-CORPUS-CERTIFICATION-REPORT.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| FINAL-UNIVERSAL-INFINITE-EXPANSION-FOUNDATION-CERTIFICATION-REPORT.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| H-06-TASK-010-GATE-PURITY-CERTIFICATION-PLAN.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| IAC-001B/02-KNOWLEDGE-ONCE-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| IAC-001B/09-FINAL-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| IAC-001C/09-FINAL-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| IAC-001D/09-FINAL-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| IAC-001E/09-FINAL-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| P0-FREEZE-CERTIFICATION-001-FINAL-FOUNDATION-FREEZE-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| P0-ULTIMATE-CLOSURE-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| PHASE-4-VALIDATION-AND-CERTIFICATION-EVIDENCE.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| PHASE-CERTIFICATION-GOVERNANCE-BINDING-DETERMINATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| PHASE-CERTIFICATION-GOVERNANCE-RELATIONSHIP-DETERMINATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| PHASE-CERTIFICATION-TAXONOMY-READINESS-DETERMINATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| UAUE-EPOCH-6-CERTIFICATION-DETERMINATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| UCOS-EXECUTION-GOVERNANCE-CERTIFICATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| UNIVERSAL-BASELINE-TEMPORAL-CERTIFICATION-DETERMINATION.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| platform/security/EC2-CAP-SEC-001-SEC-CERT-CERTIFICATION-REPORT.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| platform/security/EC2-CAP-SEC-001-SEC-CLASS-CERTIFICATION-REPORT.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| platform/security/EC2-CAP-SEC-001-SEC-INTEL-CERTIFICATION-REPORT.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| platform/security/EC2-CAP-SEC-001-SEC-OBS-CERTIFICATION-REPORT.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| platform/security/EC2-CAP-SEC-001-SEC-REG-CERTIFICATION-REPORT.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |
| platform/security/EC2-CAP-SEC-001-SEC-ZONE-CERTIFICATION-REPORT.md | certification object | PARTIAL | NO | NO | NO | NO | referenced by code/Makefile/verify.sh/workflow: False; digest field: NONE; producer: NONE |

## 3. Closure arithmetic

| Measure | Value |
|---|---|
| Enforcement artifacts enumerated | 1261 |
| Declared (machine-readable register) | 1071 |
| Reachable | 776 |
| Executed automatically | 233 |
| Measured | 546 |
| Certified | 446 |
| Distinct gap findings | 1547 |

**The enforcement set is NOT closed.** Closure would require every declared artifact to be reachable, every reachable artifact executed, every executed artifact measured, and every measured artifact certified. Each of those four implications fails at this HEAD, with the specific counterexamples enumerated in `ENFORCEMENT-CLOSURE-GAPS.md`.

## 4. Reproduction

```
python -m engine.enforcement_closure.gate --json      # enforcement plane, 172 artifacts
python -m engine.enforcement_closure.gate --inventory # discovered surface
python3 00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py --render --quiet  # requirement plane
git ls-files | wc -l                                  # tracked-path boundary
```

## 5. Stated limits of this measurement

- **Naming is not killing.** `Measured` counts a test that *names* the artifact. It does not prove the test would fail if the artifact broke. The sufficient condition is proven by mutation for 5 of 20 governed declarations only (UEC ratchet `declarations_with_uniform_identity = 5`); for the remaining 15 it is recorded as UNPROVEN, not as passing.
- **Branch protection is not visible in the repository.** Whether the blocking workflows are enforced as required merge checks cannot be determined from files alone, so `Executed=YES` for a workflow means 'fires automatically', not 'can block a merge'.
- **Requirement runtime evidence is uniformly absent.** All 549 records carry `runtime_status=NO-RUNTIME-EVIDENCE`, so `Executed=NO` for the whole requirement plane is a property of the register, not a per-requirement discrimination.
- **The prose requirement universe is not cross-linked** to the derived registry: no `REQ-NN` appears in `requirements.json` and no `RR-*` in the prose index, so the two populations are reported separately and cannot be reconciled from repository content.
