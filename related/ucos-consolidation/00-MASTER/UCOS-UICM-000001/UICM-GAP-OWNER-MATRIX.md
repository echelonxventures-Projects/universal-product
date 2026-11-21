# UICM — Gap Owner Matrix

> **Artifact:** `UICM-GAP-OWNER-MATRIX`
> **Programme:** UCOS-UICM-000001 — Phase 2 (discovery)
> **AUTHORITY = NONE — DERIVED TRUTH.** This matrix assigns no ownership. Every owner
> below is *read* from a located instrument; none is minted here.
> **Disposition:** DISCOVERY ONLY. No engine code, no registry, no declaration edit.
> **Source:** `04-CLOSURE-GAP-REGISTER.json` (gap_total 158), `uicm.json`, `03-CLOSURE-MEASUREMENT-REPORT.json`
> **Matrix digest measured against:** `8ce37cd19fe42adf26d8832d84bd7106`

---

## 1. The two ownership vocabularies must not be conflated

The gap register already carries two owner fields per gap, and they answer different
questions. Phase 2 keeps them separate rather than collapsing them:

| Field | Question it answers | Vocabulary | Count of distinct values |
|---|---|---|---:|
| `canonical_owner` | Who is *accountable* for the capability? | `UCOS-<CATEGORY>-AUTHORITY` | 2 |
| `discharging_owner` | Which *source* does the probe read? | `SRC-*` | 5 |
| **resolution owner** (derived here) | Which located artifact must *change* for the probe to read differently? | UGA path owner / programme id | 6 |

`canonical_owner` is **not** a resolution owner. It is synthesized at projection time
from the capability's `category` field by `engine/knowledge/capability.py:229-232`
(`f"UCOS-{stem}-AUTHORITY"`), so `UCOS-ENGINE-AUTHORITY` literally denotes "the
`engine/` tree". Neither string is declared in `00-CMG/CMG-REGISTRY.json` nor in any
constitutional instrument, and `02-CANONICAL-OWNERSHIP-MATRIX.md` §5 records that the
reuse engine "refuses to assert a single owner". Treating either as a *resolution*
authority would invent an authority, which principle 10 forbids.

## 2. Resolution-owner derivation rule

Exactly one resolution owner per gap, derived by a total function of the gap's
dimension. No gap is left unowned and none carries two owners:

```
resolution_owner(gap) =
    if gap.dimension in {contract, evidence}:
        UGA path owner of the capability's own package        # ownership rule 3/4
    else:
        canonical_sources[gap.discharging_owner] -> located owner
```

**Why the two-branch rule rather than one.** For fifteen dimensions the declared
`owner_reference` names the artifact that must change. For `contract` and `evidence` it
does not: `owner_reference` is `SRC-CAPABILITY-IDENTITY`
(`knowledge/canonical-knowledge.json`), but `probe_contract` reads the capability's own
`__init__.py` for an `__all__` assignment and `probe_evidence` reads the capability's own
module names for an evidence producer. **Editing `canonical-knowledge.json` cannot close
either dimension** — and that file is generated and gitignored besides. So for those two
dimensions the resolution owner is the capability's own package, resolved through the
UGA `ownership_rules` (TOTAL, so "unowned" is structurally unreachable). This is a
divergence between *declared discharging source* and *effective resolution owner*, and it
is recorded rather than papered over.

## 3. Resolution owner per dimension

| # | Dimension | Gaps | Declared `discharging_owner` | Resolution owner | Instrument that must change | Dependency |
|---:|---|---:|---|---|---|---|
| 1 | `identity` | 1 | `SRC-ARTIFACT-IDENTITY` | UCOS-UGA-001 | `00-MASTER/UCOS-UGA-001/uga_engine.py` | none — root of the dependency graph |
| 2 | `registry` | 3 | `SRC-REGISTRATION` | UCOS-REPOSITORY-ROOT | `pyproject.toml` | none |
| 3 | `governance` | 1 | `SRC-ARTIFACT-IDENTITY` | UCOS-UGA-001 | `00-MASTER/UCOS-UGA-001/uga_engine.py` | **identity** (same two artifacts; the probe returns OPEN because `unidentified_artifacts` is non-empty) |
| 4 | `contract` | 4 | `SRC-CAPABILITY-IDENTITY` | the capability's own package (per gap) | `its `__init__.py` / an evidence producer module` | none |
| 5 | `coverage` | 3 | `SRC-REGISTRATION` | UCOS-REPOSITORY-ROOT | `pyproject.toml` | **registry** (same two `pyproject.toml` keys) |
| 6 | `evidence` | 39 | `SRC-CAPABILITY-IDENTITY` | the capability's own package (per gap) | `its `__init__.py` / an evidence producer module` | none |
| 7 | `certification` | 35 | `SRC-GATE-BINDING` | CMG-DLG-40 / UCCEP-000000 | `00-MASTER/UCCEP-000000/uccep-bindings.json + .github/workflows` | none |
| 8 | `determinism` | 42 | `SRC-VERIFICATION-BINDING` | UCOS-REPOSITORY-ROOT | `verify.sh` | none |
| 9 | `evolution` | 30 | `SRC-GATE-BINDING` | CMG-DLG-40 / UCCEP-000000 | `00-MASTER/UCCEP-000000/uccep-bindings.json + .github/workflows` | **registry**, **coverage** and `testing` (needs denominator membership + regression cases + binding) |
| | **total** | **158** | 5 distinct | 43 distinct (3 central + 40 capability-local) | 6 instrument classes | |

**Why 43 owners but only 6 instruments.** Three resolution owners are central programmes or
authorities (`UCOS-UGA-001`, `UCOS-REPOSITORY-ROOT`, `CMG-DLG-40 / UCCEP-000000`) and cover
115 gaps. The remaining 43 gaps are `contract` (4) and `evidence` (39), which resolve to the
capability's **own** package — 40 distinct package owners, cross-checked against the 40
distinct capabilities carrying a `contract` or `evidence` gap. That concentration matters for
sequencing: 115 gaps sit behind three owners, while 43 gaps are distributed across 40 owners
and cannot be closed by any central edit.

## 4. Single-authority verification

| Property | Measure | Result |
|---|---|---|
| Every gap has a resolution owner | gaps with a derived owner / 158 | 158/158 |
| No gap has two resolution owners | dimension -> owner is a function | 0 multi-owner gaps |
| No owner was invented | every owner traced to a located instrument | 43/43 located (3 programme ids + 40 UGA path owners) |
| Capability vs resolution ownership separated | fields kept distinct | separated |

Certification authority is **not** among the six. `certification` gaps resolve to a gate
binding, and the verdict itself remains with `engine/universal_certification`
(UCOS-EPIC-006) exactly as `uicm.json` `certification_binding` declares. Lifecycle
ownership remains UCIC-001; the `ucic_stages` column below is a crosswalk, not a fork.

## 5. Complete gap enumeration — all 158 gaps, one resolution owner each

Ordered by the declared closure priority, then by capability. `UCIC` is the UCIC-001
lifecycle stage the dimension crosswalks to.

### 4. `identity` — Identity Closure · 1 gap(s)

**Question.** Does every artifact have deterministic identity?
**Requirement.** Every tracked artifact of the capability carries a universal identity minted by the identity authority.
**UCIC-001 stage(s).** 13
**Dependency.** none — root of the dependency graph

| Gap ID | Capability | Capability owner (accountable) | Resolution owner | Gap class | Finding |
|---|---|---|---|---|---|
| `UICM-GAP-8E3F86206048-04` | `engine.uckp` | UCOS-ENGINE-AUTHORITY | `UCOS-UGA-001` | REGISTRY-DRIFT | 2 artifact(s) carry no universal identity: engine/uckp/resolution.py, engine/uckp/uga_projection.py |

### 5. `registry` — Registry Closure · 3 gap(s)

**Question.** Is every artifact registered?
**Requirement.** The capability is registered in the capability register, the implementation catalogue and the coverage denominator.
**UCIC-001 stage(s).** 13
**Dependency.** none

| Gap ID | Capability | Capability owner (accountable) | Resolution owner | Gap class | Finding |
|---|---|---|---|---|---|
| `UICM-GAP-40E9845BB521-05` | `engine` | UCOS-ENGINE-AUTHORITY | `UCOS-REPOSITORY-ROOT` | REGISTRY-DRIFT | absent from coverage source, coverage addopts |
| `UICM-GAP-1A295DAD5F94-05` | `engine.constitution` | UCOS-ENGINE-AUTHORITY | `UCOS-REPOSITORY-ROOT` | REGISTRY-DRIFT | absent from coverage source, coverage addopts |
| `UICM-GAP-05A2A1854366-05` | `platform` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | REGISTRY-DRIFT | absent from coverage source, coverage addopts |

### 14. `governance` — Governance Closure · 1 gap(s)

**Question.** Are mutation boundaries controlled?
**Requirement.** Every artifact of the capability is under the object-governance boundary with a named validation contract.
**UCIC-001 stage(s).** 3, 13
**Dependency.** **identity** (same two artifacts; the probe returns OPEN because `unidentified_artifacts` is non-empty)

| Gap ID | Capability | Capability owner (accountable) | Resolution owner | Gap class | Finding |
|---|---|---|---|---|---|
| `UICM-GAP-8E3F86206048-14` | `engine.uckp` | UCOS-ENGINE-AUTHORITY | `UCOS-UGA-001` | REGISTRY-DRIFT | 2 artifact(s) are outside the object-governance boundary |

### 8. `contract` — Contract Closure · 4 gap(s)

**Question.** Are interfaces and contracts defined?
**Requirement.** The capability publishes an explicit interface surface from its package root.
**UCIC-001 stage(s).** 4, 5
**Dependency.** none

| Gap ID | Capability | Capability owner (accountable) | Resolution owner | Gap class | Finding |
|---|---|---|---|---|---|
| `UICM-GAP-40E9845BB521-08` | `engine` | UCOS-ENGINE-AUTHORITY | `engine` | UNSATISFIED-REQUIREMENT | the package root publishes no __all__ interface surface |
| `UICM-GAP-283FA3E62AE2-08` | `engine.ceu` | UCOS-ENGINE-AUTHORITY | `engine/ceu` | UNSATISFIED-REQUIREMENT | the package root publishes no __all__ interface surface |
| `UICM-GAP-05A2A1854366-08` | `platform` | UCOS-PLATFORM-AUTHORITY | `platform` | UNSATISFIED-REQUIREMENT | the package root publishes no __all__ interface surface |
| `UICM-GAP-BE6EBBF5526E-08` | `platform.universal_assurance` | UCOS-PLATFORM-AUTHORITY | `platform/universal_assurance` | UNSATISFIED-REQUIREMENT | the package root publishes no __all__ interface surface |

### 12. `coverage` — Coverage Closure · 3 gap(s)

**Question.** Are executable paths measured?
**Requirement.** The capability is inside the branch-coverage denominator, so its executable paths are measured.
**UCIC-001 stage(s).** 8
**Dependency.** **registry** (same two `pyproject.toml` keys)

| Gap ID | Capability | Capability owner (accountable) | Resolution owner | Gap class | Finding |
|---|---|---|---|---|---|
| `UICM-GAP-40E9845BB521-12` | `engine` | UCOS-ENGINE-AUTHORITY | `UCOS-REPOSITORY-ROOT` | REGISTRY-DRIFT | outside the branch-coverage denominator, so executable paths are unmeasured |
| `UICM-GAP-1A295DAD5F94-12` | `engine.constitution` | UCOS-ENGINE-AUTHORITY | `UCOS-REPOSITORY-ROOT` | REGISTRY-DRIFT | outside the branch-coverage denominator, so executable paths are unmeasured |
| `UICM-GAP-05A2A1854366-12` | `platform` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | REGISTRY-DRIFT | outside the branch-coverage denominator, so executable paths are unmeasured |

### 15. `evidence` — Evidence Closure · 39 gap(s)

**Question.** Is proof evidence generated?
**Requirement.** The capability itself produces evidence: an evidence producer module or a declared evidence format. A classification of an artifact is not a producer of evidence.
**UCIC-001 stage(s).** 9
**Dependency.** none

| Gap ID | Capability | Capability owner (accountable) | Resolution owner | Gap class | Finding |
|---|---|---|---|---|---|
| `UICM-GAP-40E9845BB521-15` | `engine` | UCOS-ENGINE-AUTHORITY | `engine` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-283FA3E62AE2-15` | `engine.ceu` | UCOS-ENGINE-AUTHORITY | `engine/ceu` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-7D3AED04D20A-15` | `engine.civilization` | UCOS-ENGINE-AUTHORITY | `engine/civilization` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-C675BA404EC5-15` | `engine.compiler` | UCOS-ENGINE-AUTHORITY | `engine/compiler` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-1A295DAD5F94-15` | `engine.constitution` | UCOS-ENGINE-AUTHORITY | `engine/constitution` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-44FBD8DE2C65-15` | `engine.determinism` | UCOS-ENGINE-AUTHORITY | `engine/determinism` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-02364C2ECF84-15` | `engine.foundation` | UCOS-ENGINE-AUTHORITY | `engine/foundation` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-BCA430A56784-15` | `engine.kernel` | UCOS-ENGINE-AUTHORITY | `engine/kernel` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-7035D33BA1E3-15` | `engine.nucleus` | UCOS-ENGINE-AUTHORITY | `engine/nucleus` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-E57853D00480-15` | `engine.provider` | UCOS-ENGINE-AUTHORITY | `engine/provider` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-989F51BC08C3-15` | `engine.registry` | UCOS-ENGINE-AUTHORITY | `engine/registry` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-4388A76F2EE9-15` | `engine.runtime` | UCOS-ENGINE-AUTHORITY | `engine/runtime` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-750EC4F94557-15` | `engine.uaue` | UCOS-ENGINE-AUTHORITY | `engine/uaue` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-8E3F86206048-15` | `engine.uckp` | UCOS-ENGINE-AUTHORITY | `engine/uckp` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-05A2A1854366-15` | `platform` | UCOS-PLATFORM-AUTHORITY | `platform` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-50AAC6BB4ACC-15` | `platform.administration` | UCOS-PLATFORM-AUTHORITY | `platform/administration` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-07F02ED82CA9-15` | `platform.blueprints` | UCOS-PLATFORM-AUTHORITY | `platform/blueprints` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-233533DA412A-15` | `platform.foundation` | UCOS-PLATFORM-AUTHORITY | `platform/foundation` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-864E5FEC5366-15` | `platform.generation` | UCOS-PLATFORM-AUTHORITY | `platform/generation` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-A2D76745EF75-15` | `platform.identity` | UCOS-PLATFORM-AUTHORITY | `platform/identity` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-7CEF421DBDF1-15` | `platform.observability` | UCOS-PLATFORM-AUTHORITY | `platform/observability` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-1FE75006C6B0-15` | `platform.portal` | UCOS-PLATFORM-AUTHORITY | `platform/portal` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-25E0354BC6E0-15` | `platform.projects` | UCOS-PLATFORM-AUTHORITY | `platform/projects` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-2562CA56C39A-15` | `platform.providers` | UCOS-PLATFORM-AUTHORITY | `platform/providers` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-93B6C3D9CBC3-15` | `platform.repository_operations` | UCOS-PLATFORM-AUTHORITY | `platform/repository_operations` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-64A13AE203C1-15` | `platform.runtime_operations` | UCOS-PLATFORM-AUTHORITY | `platform/runtime_operations` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-A464950347D8-15` | `platform.runtime_platform` | UCOS-PLATFORM-AUTHORITY | `platform/runtime_platform` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-18C0F0B85AF1-15` | `platform.security` | UCOS-PLATFORM-AUTHORITY | `platform/security` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-23C4064278ED-15` | `platform.universal_assimilation` | UCOS-PLATFORM-AUTHORITY | `platform/universal_assimilation` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-E8712C738745-15` | `platform.universal_control_plane` | UCOS-PLATFORM-AUTHORITY | `platform/universal_control_plane` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-734180D46CA0-15` | `platform.universal_foundation` | UCOS-PLATFORM-AUTHORITY | `platform/universal_foundation` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-59F4B3149827-15` | `platform.universal_generator` | UCOS-PLATFORM-AUTHORITY | `platform/universal_generator` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-F160E803C9C9-15` | `platform.universal_master_plan` | UCOS-PLATFORM-AUTHORITY | `platform/universal_master_plan` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-A32514FD972D-15` | `platform.universal_measurement` | UCOS-PLATFORM-AUTHORITY | `platform/universal_measurement` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-0F8D7A23C8E4-15` | `platform.universal_pipeline` | UCOS-PLATFORM-AUTHORITY | `platform/universal_pipeline` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-93B9E3210145-15` | `platform.universal_portal` | UCOS-PLATFORM-AUTHORITY | `platform/universal_portal` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-655138F6679D-15` | `platform.universal_project_state` | UCOS-PLATFORM-AUTHORITY | `platform/universal_project_state` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-4651C8A39A3A-15` | `platform.universal_truth` | UCOS-PLATFORM-AUTHORITY | `platform/universal_truth` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |
| `UICM-GAP-69991528866E-15` | `platform.workspace` | UCOS-PLATFORM-AUTHORITY | `platform/workspace` | UNSATISFIED-REQUIREMENT | no evidence producer; classification-level references only: catalogue evidence_present; artifact evidence_class VALIDATION |

### 16. `certification` — Certification Closure · 35 gap(s)

**Question.** Has closure been certified?
**Requirement.** A certification instrument that can reach a verdict names the capability. A mention in a certification document is not a decision procedure.
**UCIC-001 stage(s).** 10
**Dependency.** none

| Gap ID | Capability | Capability owner (accountable) | Resolution owner | Gap class | Finding |
|---|---|---|---|---|---|
| `UICM-GAP-2AD4A61A2037-16` | `engine.acceptance` | UCOS-ENGINE-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-4D2433A12128-16` | `engine.certification` | UCOS-ENGINE-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-283FA3E62AE2-16` | `engine.ceu` | UCOS-ENGINE-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-1A0AED612798-16` | `engine.discovery` | UCOS-ENGINE-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-1D83775A177A-16` | `engine.factory` | UCOS-ENGINE-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-02364C2ECF84-16` | `engine.foundation` | UCOS-ENGINE-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-6E366AB02D68-16` | `engine.governance` | UCOS-ENGINE-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-989F51BC08C3-16` | `engine.registry` | UCOS-ENGINE-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-D67CCB63DE64-16` | `engine.universal_certification` | UCOS-ENGINE-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-AD7E550FF98A-16` | `engine.validation` | UCOS-ENGINE-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-50AAC6BB4ACC-16` | `platform.administration` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-70104F372C71-16` | `platform.artifact_explorer` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-07F02ED82CA9-16` | `platform.blueprints` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-504E2E918AF3-16` | `platform.certification` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-87151879CDF1-16` | `platform.execution_dashboard` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-233533DA412A-16` | `platform.foundation` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-864E5FEC5366-16` | `platform.generation` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-A2D76745EF75-16` | `platform.identity` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-1FE75006C6B0-16` | `platform.portal` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-25E0354BC6E0-16` | `platform.projects` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-2562CA56C39A-16` | `platform.providers` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-64A13AE203C1-16` | `platform.runtime_operations` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-A464950347D8-16` | `platform.runtime_platform` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-23C4064278ED-16` | `platform.universal_assimilation` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-59F4B3149827-16` | `platform.universal_generator` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-F160E803C9C9-16` | `platform.universal_master_plan` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-A32514FD972D-16` | `platform.universal_measurement` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-11168A87DA39-16` | `platform.universal_ownership` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-93B9E3210145-16` | `platform.universal_portal` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-655138F6679D-16` | `platform.universal_project_state` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-4651C8A39A3A-16` | `platform.universal_truth` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-26A231278F14-16` | `platform.universal_validation` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-9F2395B01ADB-16` | `platform.validation` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-1EC026BCDAC5-16` | `platform.validation_intelligence` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |
| `UICM-GAP-69991528866E-16` | `platform.workspace` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | no certification instrument names this capability |

### 13. `determinism` — Determinism Closure · 42 gap(s)

**Question.** Does replay produce identical results?
**Requirement.** A located instrument asks the replay question of this capability.
**UCIC-001 stage(s).** 6
**Dependency.** none

| Gap ID | Capability | Capability owner (accountable) | Resolution owner | Gap class | Finding |
|---|---|---|---|---|---|
| `UICM-GAP-2AD4A61A2037-13` | `engine.acceptance` | UCOS-ENGINE-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-4D2433A12128-13` | `engine.certification` | UCOS-ENGINE-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-283FA3E62AE2-13` | `engine.ceu` | UCOS-ENGINE-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-390B8C26ABA5-13` | `engine.context` | UCOS-ENGINE-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-1A0AED612798-13` | `engine.discovery` | UCOS-ENGINE-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-1D83775A177A-13` | `engine.factory` | UCOS-ENGINE-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-02364C2ECF84-13` | `engine.foundation` | UCOS-ENGINE-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-6E366AB02D68-13` | `engine.governance` | UCOS-ENGINE-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-989F51BC08C3-13` | `engine.registry` | UCOS-ENGINE-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-D67CCB63DE64-13` | `engine.universal_certification` | UCOS-ENGINE-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-AD7E550FF98A-13` | `engine.validation` | UCOS-ENGINE-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-50AAC6BB4ACC-13` | `platform.administration` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-70104F372C71-13` | `platform.artifact_explorer` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-07F02ED82CA9-13` | `platform.blueprints` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-504E2E918AF3-13` | `platform.certification` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-AE09DA1D7669-13` | `platform.commercial_intelligence` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-87151879CDF1-13` | `platform.execution_dashboard` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-233533DA412A-13` | `platform.foundation` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-864E5FEC5366-13` | `platform.generation` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-A2D76745EF75-13` | `platform.identity` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-1FE75006C6B0-13` | `platform.portal` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-25E0354BC6E0-13` | `platform.projects` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-2562CA56C39A-13` | `platform.providers` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-489725D63124-13` | `platform.repository_intelligence` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-64A13AE203C1-13` | `platform.runtime_operations` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-A464950347D8-13` | `platform.runtime_platform` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-18C0F0B85AF1-13` | `platform.security` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-23C4064278ED-13` | `platform.universal_assimilation` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-BE6EBBF5526E-13` | `platform.universal_assurance` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-E8712C738745-13` | `platform.universal_control_plane` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-59F4B3149827-13` | `platform.universal_generator` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-F160E803C9C9-13` | `platform.universal_master_plan` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-A32514FD972D-13` | `platform.universal_measurement` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-11168A87DA39-13` | `platform.universal_ownership` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-93B9E3210145-13` | `platform.universal_portal` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-655138F6679D-13` | `platform.universal_project_state` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-8B4DEA734244-13` | `platform.universal_provider` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-4651C8A39A3A-13` | `platform.universal_truth` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-26A231278F14-13` | `platform.universal_validation` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-9F2395B01ADB-13` | `platform.validation` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-1EC026BCDAC5-13` | `platform.validation_intelligence` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |
| `UICM-GAP-69991528866E-13` | `platform.workspace` | UCOS-PLATFORM-AUTHORITY | `UCOS-REPOSITORY-ROOT` | ABSENT-OBLIGATION | no located instrument asks the replay question of this capability |

### 17. `evolution` — Evolution Closure · 30 gap(s)

**Question.** Can the capability evolve safely?
**Requirement.** A change to the capability is caught: it is in the coverage denominator, carries regression tests, and is bound to a gate or a published entrypoint.
**UCIC-001 stage(s).** 11, 14, 15
**Dependency.** **registry**, **coverage** and `testing` (needs denominator membership + regression cases + binding)

| Gap ID | Capability | Capability owner (accountable) | Resolution owner | Gap class | Finding |
|---|---|---|---|---|---|
| `UICM-GAP-40E9845BB521-17` | `engine` | UCOS-ENGINE-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: 5760 regression case(s), bound to acee-gate.yml |
| `UICM-GAP-2AD4A61A2037-17` | `engine.acceptance` | UCOS-ENGINE-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 105 regression case(s) |
| `UICM-GAP-4D2433A12128-17` | `engine.certification` | UCOS-ENGINE-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 639 regression case(s) |
| `UICM-GAP-283FA3E62AE2-17` | `engine.ceu` | UCOS-ENGINE-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 136 regression case(s) |
| `UICM-GAP-1A295DAD5F94-17` | `engine.constitution` | UCOS-ENGINE-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: 102 regression case(s), bound to uaue-gate.yml |
| `UICM-GAP-1D83775A177A-17` | `engine.factory` | UCOS-ENGINE-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 76 regression case(s) |
| `UICM-GAP-6E366AB02D68-17` | `engine.governance` | UCOS-ENGINE-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 42 regression case(s) |
| `UICM-GAP-D67CCB63DE64-17` | `engine.universal_certification` | UCOS-ENGINE-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 237 regression case(s) |
| `UICM-GAP-AD7E550FF98A-17` | `engine.validation` | UCOS-ENGINE-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 938 regression case(s) |
| `UICM-GAP-05A2A1854366-17` | `platform` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: 5503 regression case(s), bound to aee-gate.yml |
| `UICM-GAP-50AAC6BB4ACC-17` | `platform.administration` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 124 regression case(s) |
| `UICM-GAP-70104F372C71-17` | `platform.artifact_explorer` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 90 regression case(s) |
| `UICM-GAP-07F02ED82CA9-17` | `platform.blueprints` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 431 regression case(s) |
| `UICM-GAP-504E2E918AF3-17` | `platform.certification` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 137 regression case(s) |
| `UICM-GAP-87151879CDF1-17` | `platform.execution_dashboard` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 77 regression case(s) |
| `UICM-GAP-233533DA412A-17` | `platform.foundation` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 2109 regression case(s) |
| `UICM-GAP-864E5FEC5366-17` | `platform.generation` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 296 regression case(s) |
| `UICM-GAP-A2D76745EF75-17` | `platform.identity` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 1075 regression case(s) |
| `UICM-GAP-1FE75006C6B0-17` | `platform.portal` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 120 regression case(s) |
| `UICM-GAP-25E0354BC6E0-17` | `platform.projects` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 146 regression case(s) |
| `UICM-GAP-2562CA56C39A-17` | `platform.providers` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 36 regression case(s) |
| `UICM-GAP-64A13AE203C1-17` | `platform.runtime_operations` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 142 regression case(s) |
| `UICM-GAP-A464950347D8-17` | `platform.runtime_platform` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 111 regression case(s) |
| `UICM-GAP-18C0F0B85AF1-17` | `platform.security` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 295 regression case(s) |
| `UICM-GAP-BE6EBBF5526E-17` | `platform.universal_assurance` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 544 regression case(s) |
| `UICM-GAP-F160E803C9C9-17` | `platform.universal_master_plan` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 92 regression case(s) |
| `UICM-GAP-93B9E3210145-17` | `platform.universal_portal` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 80 regression case(s) |
| `UICM-GAP-655138F6679D-17` | `platform.universal_project_state` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 146 regression case(s) |
| `UICM-GAP-9F2395B01ADB-17` | `platform.validation` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 117 regression case(s) |
| `UICM-GAP-69991528866E-17` | `platform.workspace` | UCOS-PLATFORM-AUTHORITY | `CMG-DLG-40 / UCCEP-000000` | UNSATISFIED-REQUIREMENT | incomplete safety net: coverage denominator, 290 regression case(s) |

## 6. Determination

**ALL 158 GAPS ARE OWNED.** Every gap resolves to exactly one located resolution owner,
drawn from six instrument classes that already exist — 3 central owners covering 115 gaps and
40 capability-local package owners covering the remaining 43. No owner was created, no ownership was
modified, and capability accountability remains separate from resolution authority.
