# UICM — Universal Implementation Closure Matrix · Population Discovery Report

**Artifact:** `UICM-POPULATION-DISCOVERY-REPORT`
**Programme:** UCOS-UICM-000001
**Authority:** NONE — DERIVED TRUTH. This report legislates nothing, mints no identifier, opens no registry and certifies nothing.
**Producer:** UICM discovery pass over the confirmed canonical owners.
**Determinism:** no wall clock, no commit identity, no working-tree status. Every value is a pure function of tracked repository content.
**Disposition:** DISCOVERY ONLY. No gap in this report is fixed here.

---

## 1. What this report settles

UICM is a **measurement and certification layer only**. It consumes canonical owners and never replaces them. This report exists to make that consumption auditable *before* any UICM code exists, so the engine can be written against a measured population rather than an assumed one.

Three prohibitions are discharged by construction, and the discharge is stated here so it can be checked rather than trusted:

| Prohibition | How this report discharges it |
|---|---|
| No duplicate registry | Every column below is a **reference** into an existing register. UICM opens none. |
| No duplicate identity | Capability identity is read from `UCKO-CAP-*`; artifact identity is read from UCOS-UGA-001. UICM mints neither. |
| No duplicate governance | Mutation boundaries, lifecycle and certification status are read from their located owners. UICM asserts none. |

## 2. Confirmed canonical owners (the only sources consumed)

| Concern | Canonical owner | Consumed as |
|---|---|---|
| Capability identity | `knowledge/canonical-knowledge.json` | `UCKO-CAP-*` id, `owner`, `lifecycle`, `authority` for every capability row (universe `CAPABILITY`) |
| Artifact identity | `00-MASTER/UCOS-UGA-001/01-EXECUTABLE-OBJECT-REGISTRY.json` (UCOS-UGA-001) | `universal_id`, `owner`, `content_hash`, `evidence_class`, `validation_contract`, `certification_status` per tracked artifact |
| Implementation intelligence | `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json` | `canonical_location`, `implementation_status`, `reuse`, `replacement_prohibited` |

Four supporting sources are read as **located repository truth**, not as registries UICM owns: `pyproject.toml` (registration + coverage denominator + entrypoints), `.github/workflows/*.yml` (gate binding), `verify.sh` (verification binding), and the version-control boundary (`git ls-files`, the artifact universe).

## 3. Population discovery rule (no enumeration)

The population is **derived**, never listed. A capability is a Python package at depth 0 or 1 under a declared capability root that carries a `UCKO-CAP-*` row:

```
capability_roots      = engine, platform
capability_depth      = 0..1        (the namespace root is itself a capability)
excluded_namespaces   = tests       (test suites are evidence, not capabilities)
admission_requirement = a Capability row in knowledge/canonical-knowledge.json
```

Applying the rule to the tracked boundary yields **62 capabilities**. The knowledge register carries 122 `UCKO-CAP-*` rows in all (the remainder are nested sub-packages and non-`engine`/`platform` locations, each owned by its depth-1 parent); the RIE catalogue carries 122 rows; UCOS-UGA-001 carries 4603 artifact identities.

**Orphan artifacts: 0.** Every tracked `.py` file under a declared capability root resolves to exactly one capability in the population. The namespace roots `engine` and `platform` are admitted as capabilities precisely because `knowledge/canonical-knowledge.json` carries rows for them (`UCKO-CAP-40E9845BB521`, `UCKO-CAP-05A2A1854366`); excluding them would have orphaned `engine/__init__.py` and `platform/__init__.py`.

**Duplicate ownership: 0.** No capability name carries more than one `UCKO-CAP-*` row and no `canonical_location` carries more than one RIE row (`cko_duplicates` = {}).

## 4. Population register — identity and ownership

`UGA Identity Coverage` is *artifacts carrying a UCOS-UGA-001 `universal_id` / artifacts tracked*. `Knowledge Reference` is the exact `UCKO-CAP-*` anchor.

| # | Capability ID | Capability Name | Canonical Owner | Knowledge Reference | UGA Identity Coverage | RIE Implementation Location |
|---:|---|---|---|---|---:|---|
| 1 | `UCKO-CAP-40E9845BB521` | `engine` | UCOS-ENGINE-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-40E9845BB521` | 1/1 | `engine` · CERTIFIED |
| 2 | `UCKO-CAP-2AD4A61A2037` | `engine.acceptance` | UCOS-ENGINE-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-2AD4A61A2037` | 7/7 | `engine/acceptance` · CERTIFIED |
| 3 | `UCKO-CAP-4D2433A12128` | `engine.certification` | UCOS-ENGINE-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-4D2433A12128` | 9/9 | `engine/certification` · CERTIFIED |
| 4 | `UCKO-CAP-283FA3E62AE2` | `engine.ceu` | UCOS-ENGINE-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-283FA3E62AE2` | 6/6 | `engine/ceu` · CERTIFIED |
| 5 | `UCKO-CAP-7D3AED04D20A` | `engine.civilization` | UCOS-ENGINE-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-7D3AED04D20A` | 10/10 | `engine/civilization` · CERTIFIED |
| 6 | `UCKO-CAP-C675BA404EC5` | `engine.compiler` | UCOS-ENGINE-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-C675BA404EC5` | 16/16 | `engine/compiler` · CERTIFIED |
| 7 | `UCKO-CAP-1A295DAD5F94` | `engine.constitution` | UCOS-ENGINE-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-1A295DAD5F94` | 17/17 | `engine/constitution` · CERTIFIED |
| 8 | `UCKO-CAP-390B8C26ABA5` | `engine.context` | UCOS-ENGINE-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-390B8C26ABA5` | 18/18 | `engine/context` · CERTIFIED |
| 9 | `UCKO-CAP-44FBD8DE2C65` | `engine.determinism` | UCOS-ENGINE-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-44FBD8DE2C65` | 4/4 | `engine/determinism` · CERTIFIED |
| 10 | `UCKO-CAP-1A0AED612798` | `engine.discovery` | UCOS-ENGINE-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-1A0AED612798` | 7/7 | `engine/discovery` · CERTIFIED |
| 11 | `UCKO-CAP-1D83775A177A` | `engine.factory` | UCOS-ENGINE-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-1D83775A177A` | 17/17 | `engine/factory` · CERTIFIED |
| 12 | `UCKO-CAP-02364C2ECF84` | `engine.foundation` | UCOS-ENGINE-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-02364C2ECF84` | 15/15 | `engine/foundation` · CERTIFIED |
| 13 | `UCKO-CAP-6E366AB02D68` | `engine.governance` | UCOS-ENGINE-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-6E366AB02D68` | 7/7 | `engine/governance` · CERTIFIED |
| 14 | `UCKO-CAP-F70C547ACF71` | `engine.graph` | UCOS-ENGINE-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-F70C547ACF71` | 24/24 | `engine/graph` · CERTIFIED |
| 15 | `UCKO-CAP-BCA430A56784` | `engine.kernel` | UCOS-ENGINE-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-BCA430A56784` | 10/10 | `engine/kernel` · CERTIFIED |
| 16 | `UCKO-CAP-A1B82399651E` | `engine.knowledge` | UCOS-ENGINE-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-A1B82399651E` | 47/47 | `engine/knowledge` · CERTIFIED |
| 17 | `UCKO-CAP-7035D33BA1E3` | `engine.nucleus` | UCOS-ENGINE-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-7035D33BA1E3` | 14/14 | `engine/nucleus` · CERTIFIED |
| 18 | `UCKO-CAP-E57853D00480` | `engine.provider` | UCOS-ENGINE-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-E57853D00480` | 7/7 | `engine/provider` · CERTIFIED |
| 19 | `UCKO-CAP-989F51BC08C3` | `engine.registry` | UCOS-ENGINE-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-989F51BC08C3` | 17/17 | `engine/registry` · CERTIFIED |
| 20 | `UCKO-CAP-4388A76F2EE9` | `engine.runtime` | UCOS-ENGINE-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-4388A76F2EE9` | 37/37 | `engine/runtime` · CERTIFIED |
| 21 | `UCKO-CAP-750EC4F94557` | `engine.uaue` | UCOS-ENGINE-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-750EC4F94557` | 19/19 | `engine/uaue` · CERTIFIED |
| 22 | `UCKO-CAP-8E3F86206048` | `engine.uckp` | UCOS-ENGINE-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-8E3F86206048` | 25/27 ⚠ | `engine/uckp` · CERTIFIED |
| 23 | `UCKO-CAP-D67CCB63DE64` | `engine.universal_certification` | UCOS-ENGINE-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-D67CCB63DE64` | 10/10 | `engine/universal_certification` · CERTIFIED |
| 24 | `UCKO-CAP-AD7E550FF98A` | `engine.validation` | UCOS-ENGINE-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-AD7E550FF98A` | 7/7 | `engine/validation` · CERTIFIED |
| 25 | `UCKO-CAP-05A2A1854366` | `platform` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-05A2A1854366` | 1/1 | `platform` · IMPLEMENTED |
| 26 | `UCKO-CAP-50AAC6BB4ACC` | `platform.administration` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-50AAC6BB4ACC` | 13/13 | `platform/administration` · IMPLEMENTED |
| 27 | `UCKO-CAP-70104F372C71` | `platform.artifact_explorer` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-70104F372C71` | 11/11 | `platform/artifact_explorer` · IMPLEMENTED |
| 28 | `UCKO-CAP-07F02ED82CA9` | `platform.blueprints` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-07F02ED82CA9` | 18/18 | `platform/blueprints` · IMPLEMENTED |
| 29 | `UCKO-CAP-504E2E918AF3` | `platform.certification` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-504E2E918AF3` | 13/13 | `platform/certification` · IMPLEMENTED |
| 30 | `UCKO-CAP-AE09DA1D7669` | `platform.commercial_intelligence` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-AE09DA1D7669` | 20/20 | `platform/commercial_intelligence` · IMPLEMENTED |
| 31 | `UCKO-CAP-2580EE27E040` | `platform.coverage` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-2580EE27E040` | 12/12 | `platform/coverage` · IMPLEMENTED |
| 32 | `UCKO-CAP-87151879CDF1` | `platform.execution_dashboard` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-87151879CDF1` | 9/9 | `platform/execution_dashboard` · IMPLEMENTED |
| 33 | `UCKO-CAP-233533DA412A` | `platform.foundation` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-233533DA412A` | 17/17 | `platform/foundation` · IMPLEMENTED |
| 34 | `UCKO-CAP-864E5FEC5366` | `platform.generation` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-864E5FEC5366` | 14/14 | `platform/generation` · IMPLEMENTED |
| 35 | `UCKO-CAP-A2D76745EF75` | `platform.identity` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-A2D76745EF75` | 9/9 | `platform/identity` · IMPLEMENTED |
| 36 | `UCKO-CAP-08634E62D494` | `platform.measurement` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-08634E62D494` | 14/14 | `platform/measurement` · IMPLEMENTED |
| 37 | `UCKO-CAP-7CEF421DBDF1` | `platform.observability` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-7CEF421DBDF1` | 10/10 | `platform/observability` · IMPLEMENTED |
| 38 | `UCKO-CAP-1FE75006C6B0` | `platform.portal` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-1FE75006C6B0` | 10/10 | `platform/portal` · IMPLEMENTED |
| 39 | `UCKO-CAP-25E0354BC6E0` | `platform.projects` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-25E0354BC6E0` | 13/13 | `platform/projects` · IMPLEMENTED |
| 40 | `UCKO-CAP-2562CA56C39A` | `platform.providers` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-2562CA56C39A` | 3/3 | `platform/providers` · IMPLEMENTED |
| 41 | `UCKO-CAP-489725D63124` | `platform.repository_intelligence` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-489725D63124` | 18/18 | `platform/repository_intelligence` · IMPLEMENTED |
| 42 | `UCKO-CAP-93B6C3D9CBC3` | `platform.repository_operations` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-93B6C3D9CBC3` | 12/12 | `platform/repository_operations` · IMPLEMENTED |
| 43 | `UCKO-CAP-64A13AE203C1` | `platform.runtime_operations` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-64A13AE203C1` | 15/15 | `platform/runtime_operations` · IMPLEMENTED |
| 44 | `UCKO-CAP-A464950347D8` | `platform.runtime_platform` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-A464950347D8` | 15/15 | `platform/runtime_platform` · IMPLEMENTED |
| 45 | `UCKO-CAP-18C0F0B85AF1` | `platform.security` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-18C0F0B85AF1` | 11/11 | `platform/security` · IMPLEMENTED |
| 46 | `UCKO-CAP-23C4064278ED` | `platform.universal_assimilation` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-23C4064278ED` | 7/7 | `platform/universal_assimilation` · IMPLEMENTED |
| 47 | `UCKO-CAP-BE6EBBF5526E` | `platform.universal_assurance` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-BE6EBBF5526E` | 15/15 | `platform/universal_assurance` · IMPLEMENTED |
| 48 | `UCKO-CAP-E8712C738745` | `platform.universal_control_plane` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-E8712C738745` | 22/22 | `platform/universal_control_plane` · IMPLEMENTED |
| 49 | `UCKO-CAP-734180D46CA0` | `platform.universal_foundation` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-734180D46CA0` | 12/12 | `platform/universal_foundation` · IMPLEMENTED |
| 50 | `UCKO-CAP-59F4B3149827` | `platform.universal_generator` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-59F4B3149827` | 8/8 | `platform/universal_generator` · IMPLEMENTED |
| 51 | `UCKO-CAP-F160E803C9C9` | `platform.universal_master_plan` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-F160E803C9C9` | 5/5 | `platform/universal_master_plan` · IMPLEMENTED |
| 52 | `UCKO-CAP-A32514FD972D` | `platform.universal_measurement` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-A32514FD972D` | 7/7 | `platform/universal_measurement` · IMPLEMENTED |
| 53 | `UCKO-CAP-11168A87DA39` | `platform.universal_ownership` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-11168A87DA39` | 8/8 | `platform/universal_ownership` · IMPLEMENTED |
| 54 | `UCKO-CAP-0F8D7A23C8E4` | `platform.universal_pipeline` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-0F8D7A23C8E4` | 21/21 | `platform/universal_pipeline` · IMPLEMENTED |
| 55 | `UCKO-CAP-93B9E3210145` | `platform.universal_portal` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-93B9E3210145` | 8/8 | `platform/universal_portal` · IMPLEMENTED |
| 56 | `UCKO-CAP-655138F6679D` | `platform.universal_project_state` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-655138F6679D` | 7/7 | `platform/universal_project_state` · IMPLEMENTED |
| 57 | `UCKO-CAP-8B4DEA734244` | `platform.universal_provider` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-8B4DEA734244` | 14/14 | `platform/universal_provider` · IMPLEMENTED |
| 58 | `UCKO-CAP-4651C8A39A3A` | `platform.universal_truth` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-4651C8A39A3A` | 8/8 | `platform/universal_truth` · IMPLEMENTED |
| 59 | `UCKO-CAP-26A231278F14` | `platform.universal_validation` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-26A231278F14` | 9/9 | `platform/universal_validation` · IMPLEMENTED |
| 60 | `UCKO-CAP-9F2395B01ADB` | `platform.validation` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-9F2395B01ADB` | 13/13 | `platform/validation` · IMPLEMENTED |
| 61 | `UCKO-CAP-1EC026BCDAC5` | `platform.validation_intelligence` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-1EC026BCDAC5` | 11/11 | `platform/validation_intelligence` · IMPLEMENTED |
| 62 | `UCKO-CAP-69991528866E` | `platform.workspace` | UCOS-PLATFORM-AUTHORITY | `knowledge/canonical-knowledge.json`#`UCKO-CAP-69991528866E` | 13/13 | `platform/workspace` · IMPLEMENTED |

## 5. Population register — located closure sources and status

Every cell names an **existing** mechanism. Where no mechanism is located the cell says so and names whatever weaker *reference* exists, because a reference recorded as a mechanism is precisely the unverified claim UICM exists to refuse.

Two predicates are deliberately strict, and the strictness changes the result:

- **Evidence Closure** requires a *producer* — an `evidence.py` module or a declared `ucos-*-evidence/*` format. RIE's `evidence_present` flag and UGA's per-artifact `evidence_class` are classifications *of* an artifact, not producers *of* evidence. Accepting them would have closed the dimension for all 62 capabilities; requiring a producer closes it for 23.
- **Certification Closure** requires an *instrument* that can reach a verdict — a `certification.py` module or a CI gate naming the capability. Being mentioned in a 00-MASTER certification document is not a decision procedure. Accepting mentions would have closed the dimension for all 62; requiring an instrument closes it for 27.

| Capability Name | Existing Validation Source | Existing Evidence Source | Existing Certification Source | Closure Status | Missing Dimensions |
|---|---|---|---|---|---|
| `engine` | 264 suite(s) · 4435 case(s) · verify.sh | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | CI gate acee-gate.yml | **OPEN** | contract, coverage, evidence, registry |
| `engine.acceptance` | 8 suite(s) · 105 case(s) | engine/acceptance/evidence.py; emits ucos-acceptance-evidence/1.0.0 | no certification instrument; mention-level reference: 00-MASTER/IMPLEMENT-001A/00-IMPLEMENT-001-COMPLETION-REPORT.md | **OPEN** | certification, determinism |
| `engine.certification` | 18 suite(s) · 204 case(s) | engine/certification/evidence.py; emits ucos-certification-evidence/1.0.0 | no certification instrument; mention-level reference: 00-MASTER/ACEE-000001/acee.json | **OPEN** | certification, determinism |
| `engine.ceu` | 5 suite(s) · 136 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | no certification instrument; mention-level reference: 00-MASTER/P0-FINAL-CLOSURE-002/UCOS-COVERAGE-CLOSURE.json | **OPEN** | certification, contract, determinism, evidence |
| `engine.civilization` | 9 suite(s) · 167 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | CI gate mcos-gate.yml | **OPEN** | determinism, evidence |
| `engine.compiler` | 17 suite(s) · 185 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | CI gate uei-gate.yml | **OPEN** | determinism, evidence |
| `engine.constitution` | 7 suite(s) · 102 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | CI gate uaue-gate.yml | **OPEN** | coverage, evidence, registry |
| `engine.context` | 12 suite(s) · 356 case(s) | engine/context/evidence.py; emits ucos-ucxi-context-evidence-index | engine/context/certification.py | **OPEN** | determinism |
| `engine.determinism` | 3 suite(s) · 36 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | CI gate determinism.yml | **OPEN** | evidence |
| `engine.discovery` | 6 suite(s) · 54 case(s) | engine/discovery/evidence.py; emits ucos-discovery-evidence/1.0.0 | no certification instrument; mention-level reference: 00-MASTER/BASELINE-001/FINAL-BASELINE-CERTIFICATE.md | **OPEN** | certification, determinism |
| `engine.factory` | 7 suite(s) · 76 case(s) | engine/factory/evidence.py; emits ucos-generation-evidence/1.0.0 | no certification instrument; mention-level reference: 00-MASTER/ACEE-000001/acee.json | **OPEN** | certification, determinism |
| `engine.foundation` | 32 suite(s) · 569 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | no certification instrument; mention-level reference: 00-MASTER/BASELINE-001/FINAL-BASELINE-CERTIFICATE.md | **OPEN** | certification, determinism, evidence |
| `engine.governance` | 5 suite(s) · 42 case(s) | engine/governance/evidence.py; emits ucos-governance-evidence/1.0.0 | no certification instrument; mention-level reference: 00-MASTER/MIP-W1-P001/07-UNIVERSAL-CAPABILITY-CATALOG.md | **OPEN** | certification, determinism |
| `engine.graph` | 23 suite(s) · 363 case(s) | engine/graph/evidence.py | CI gate uei-gate.yml | **OPEN** | determinism |
| `engine.kernel` | 17 suite(s) · 199 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | CI gate umk-gate.yml | **OPEN** | determinism, evidence |
| `engine.knowledge` | 36 suite(s) · 641 case(s) | engine/knowledge/evidence.py; emits ucos-ukda-repository-assimilation-evidence | engine/knowledge/certification.py; CI gate uei-gate.yml | **OPEN** | determinism |
| `engine.nucleus` | 11 suite(s) · 254 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | engine/nucleus/certification.py; CI gate uaue-gate.yml | **OPEN** | evidence |
| `engine.provider` | 5 suite(s) · 55 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | CI gate uprf-gate.yml | **OPEN** | determinism, evidence |
| `engine.registry` | 22 suite(s) · 464 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | no certification instrument; mention-level reference: 00-MASTER/ACEE-000001/acee.json | **OPEN** | certification, determinism, evidence |
| `engine.runtime` | 35 suite(s) · 353 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | CI gate uei-gate.yml | **OPEN** | determinism, evidence |
| `engine.uaue` | 6 suite(s) · 302 case(s) · verify.sh | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | engine/uaue/certification.py; CI gate uaue-gate.yml | **OPEN** | evidence |
| `engine.uckp` | 23 suite(s) · 943 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | CI gate uaue-gate.yml | **OPEN** | evidence, governance, identity |
| `engine.universal_certification` | 11 suite(s) · 237 case(s) | engine/universal_certification/evidence.py; emits ucos-universal-certification-evidence/1.0.0 | no certification instrument; mention-level reference: 00-MASTER/ACEE-000001/acee.json | **OPEN** | certification, determinism |
| `engine.validation` | 16 suite(s) · 169 case(s) | engine/validation/evidence.py; emits ucos-validation-evidence/1.0.0 | no certification instrument; mention-level reference: 00-MASTER/ACEE-000001/acee.json | **OPEN** | certification, determinism |
| `platform` | 319 suite(s) · 5503 case(s) · verify.sh | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | CI gate aee-gate.yml | **OPEN** | contract, coverage, evidence, registry |
| `platform.administration` | 12 suite(s) · 124 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | no certification instrument; mention-level reference: 00-MASTER/MCP-003-MASTER-EXECUTION.md | **OPEN** | certification, determinism, evidence |
| `platform.artifact_explorer` | 10 suite(s) · 90 case(s) | platform/artifact_explorer/evidence.py | no certification instrument; mention-level reference: 00-MASTER/MIP-W1-P001/07-UNIVERSAL-CAPABILITY-CATALOG.md | **OPEN** | certification, determinism |
| `platform.blueprints` | 46 suite(s) · 431 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | no certification instrument; mention-level reference: 00-MASTER/IMPLEMENT-001B/01-C2-EVIDENCE-AND-DISPOSITION.md | **OPEN** | certification, determinism, evidence |
| `platform.certification` | 14 suite(s) · 137 case(s) | platform/certification/evidence.py | no certification instrument; mention-level reference: 00-MASTER/BASELINE-001/FINAL-BASELINE-CERTIFICATE.md | **OPEN** | certification, determinism |
| `platform.commercial_intelligence` | 3 suite(s) · 53 case(s) | platform/commercial_intelligence/evidence.py; emits ucos-business-evidence-index/1.0.0 | platform/commercial_intelligence/certification.py | **OPEN** | determinism |
| `platform.coverage` | 14 suite(s) · 107 case(s) | platform/coverage/evidence.py | platform/coverage/certification.py; CI gate uei-gate.yml | **OPEN** | determinism |
| `platform.execution_dashboard` | 9 suite(s) · 77 case(s) | platform/execution_dashboard/evidence.py | no certification instrument; mention-level reference: 00-MASTER/MCP-003-MASTER-EXECUTION.md | **OPEN** | certification, determinism |
| `platform.foundation` | 137 suite(s) · 2109 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | no certification instrument; mention-level reference: 00-MASTER/BASELINE-001/FINAL-BASELINE-CERTIFICATE.md | **OPEN** | certification, determinism, evidence |
| `platform.generation` | 30 suite(s) · 296 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | no certification instrument; mention-level reference: 00-MASTER/CAEM-001/01-MANDATE-TO-CANONICAL-HOME-MAP.md | **OPEN** | certification, determinism, evidence |
| `platform.identity` | 86 suite(s) · 1075 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | no certification instrument; mention-level reference: 00-MASTER/IMPLEMENT-001/00-EXECUTABLE-BACKLOG.md | **OPEN** | certification, determinism, evidence |
| `platform.measurement` | 13 suite(s) · 84 case(s) | platform/measurement/evidence.py | CI gate uei-gate.yml | **OPEN** | determinism |
| `platform.observability` | 48 suite(s) · 607 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | CI gate uei-gate.yml | **OPEN** | determinism, evidence |
| `platform.portal` | 10 suite(s) · 120 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | no certification instrument; mention-level reference: 00-MASTER/MIP-W1-P001/07-UNIVERSAL-CAPABILITY-CATALOG.md | **OPEN** | certification, determinism, evidence |
| `platform.projects` | 14 suite(s) · 146 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | no certification instrument; mention-level reference: 00-MASTER/MCP-003-MASTER-EXECUTION.md | **OPEN** | certification, determinism, evidence |
| `platform.providers` | 1 suite(s) · 36 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | no certification instrument; mention-level reference: 00-MASTER/MIP-W1-P001/07-UNIVERSAL-CAPABILITY-CATALOG.md | **OPEN** | certification, determinism, evidence |
| `platform.repository_intelligence` | 7 suite(s) · 136 case(s) | platform/repository_intelligence/evidence.py; emits ucos-evidence-universe | platform/repository_intelligence/certification.py | **OPEN** | determinism |
| `platform.repository_operations` | 11 suite(s) · 83 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | CI gate uei-gate.yml | **OPEN** | determinism, evidence |
| `platform.runtime_operations` | 14 suite(s) · 142 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | no certification instrument; mention-level reference: 00-MASTER/ACEE-000001/acee.json | **OPEN** | certification, determinism, evidence |
| `platform.runtime_platform` | 14 suite(s) · 111 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | no certification instrument; mention-level reference: 00-MASTER/MIP-W1-P001/07-UNIVERSAL-CAPABILITY-CATALOG.md | **OPEN** | certification, determinism, evidence |
| `platform.security` | 12 suite(s) · 295 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | platform/security/certification.py | **OPEN** | determinism, evidence |
| `platform.universal_assimilation` | 3 suite(s) · 62 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | no certification instrument; mention-level reference: 00-MASTER/UCOS-RIB-001/02-REPOSITORY-CAPABILITY-GRAPH.md | **OPEN** | certification, determinism, evidence |
| `platform.universal_assurance` | 14 suite(s) · 544 case(s) | platform/universal_assurance/evidence.py; emits ucos-assurance-evidence-bundle/1.0.0 | platform/universal_assurance/certification.py | **OPEN** | contract, determinism |
| `platform.universal_control_plane` | 7 suite(s) · 693 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | platform/universal_control_plane/certification.py | **OPEN** | determinism, evidence |
| `platform.universal_foundation` | 11 suite(s) · 528 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | CI gate ufc-gate.yml | **OPEN** | determinism, evidence |
| `platform.universal_generator` | 5 suite(s) · 146 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | no certification instrument; mention-level reference: 00-MASTER/UCOS-RIB-001/02-REPOSITORY-CAPABILITY-GRAPH.md | **OPEN** | certification, determinism, evidence |
| `platform.universal_master_plan` | 1 suite(s) · 92 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | no certification instrument; mention-level reference: 00-MASTER/UCOS-RIB-001/02-REPOSITORY-CAPABILITY-GRAPH.md | **OPEN** | certification, determinism, evidence |
| `platform.universal_measurement` | 2 suite(s) · 35 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | no certification instrument; mention-level reference: 00-MASTER/UCOS-RIB-001/02-REPOSITORY-CAPABILITY-GRAPH.md | **OPEN** | certification, determinism, evidence |
| `platform.universal_ownership` | 5 suite(s) · 201 case(s) | platform/universal_ownership/evidence.py | no certification instrument; mention-level reference: 00-MASTER/P0-FINAL-CLOSURE-002/UCOS-COVERAGE-CLOSURE.json | **OPEN** | certification, determinism |
| `platform.universal_pipeline` | 7 suite(s) · 199 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | CI gate uaep-gate.yml | **OPEN** | evidence |
| `platform.universal_portal` | 9 suite(s) · 80 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | no certification instrument; mention-level reference: 00-MASTER/MIP-W1-P001/07-UNIVERSAL-CAPABILITY-CATALOG.md | **OPEN** | certification, determinism, evidence |
| `platform.universal_project_state` | 2 suite(s) · 146 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | no certification instrument; mention-level reference: 00-MASTER/UCOS-RIB-001/02-REPOSITORY-CAPABILITY-GRAPH.md | **OPEN** | certification, determinism, evidence |
| `platform.universal_provider` | 11 suite(s) · 273 case(s) | platform/universal_provider/evidence.py | platform/universal_provider/certification.py | **OPEN** | determinism |
| `platform.universal_truth` | 7 suite(s) · 257 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | no certification instrument; mention-level reference: 00-MASTER/UCOS-RIB-001/02-REPOSITORY-CAPABILITY-GRAPH.md | **OPEN** | certification, determinism, evidence |
| `platform.universal_validation` | 11 suite(s) · 181 case(s) | platform/universal_validation/evidence.py; emits ucos-universal-validation-evidence/1.0.0 | no certification instrument; mention-level reference: 00-MASTER/ACEE-000001/acee.json | **OPEN** | certification, determinism |
| `platform.validation` | 14 suite(s) · 117 case(s) | platform/validation/evidence.py | no certification instrument; mention-level reference: 00-MASTER/ACEE-000001/acee.json | **OPEN** | certification, determinism |
| `platform.validation_intelligence` | 12 suite(s) · 395 case(s) | platform/validation_intelligence/evidence.py; emits ucos-validation-intelligence-evidence/1.0.0 | no certification instrument; mention-level reference: 00-MASTER/ACEE-000001/acee.json | **OPEN** | certification, determinism |
| `platform.workspace` | 22 suite(s) · 290 case(s) | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION | no certification instrument; mention-level reference: 00-MASTER/MCP-003-MASTER-EXECUTION.md | **OPEN** | certification, determinism, evidence |

## 6. Closure dimension coverage across the population

Seventeen dimensions × 62 capabilities = 1054 closure cells measured.

| # | Closure dimension | Question | CLOSED | OPEN | BLOCKED | UNKNOWN |
|---:|---|---|---:|---:|---:|---:|
| 1 | Existence Closure | Does the capability exist? | 62 | 0 | 0 | 0 |
| 2 | Architecture Closure | Is architecture defined? | 62 | 0 | 0 | 0 |
| 3 | Ownership Closure | Does exactly one canonical owner exist? | 62 | 0 | 0 | 0 |
| 4 | Identity Closure | Does every artifact have deterministic identity? | 61 | 1 | 0 | 0 |
| 5 | Registry Closure | Is every artifact registered? | 59 | 3 | 0 | 0 |
| 6 | Dependency Closure | Are all dependencies resolved? | 62 | 0 | 0 | 0 |
| 7 | Implementation Closure | Does executable implementation exist? | 62 | 0 | 0 | 0 |
| 8 | Contract Closure | Are interfaces and contracts defined? | 58 | 4 | 0 | 0 |
| 9 | Validation Closure | Can correctness be measured? | 62 | 0 | 0 | 0 |
| 10 | Verification Closure | Can correctness be proven? | 62 | 0 | 0 | 0 |
| 11 | Testing Closure | Are behaviours tested? | 62 | 0 | 0 | 0 |
| 12 | Coverage Closure | Are executable paths measured? | 59 | 3 | 0 | 0 |
| 13 | Determinism Closure | Does replay produce identical results? | 8 | 54 | 0 | 0 |
| 14 | Governance Closure | Are mutation boundaries controlled? | 61 | 1 | 0 | 0 |
| 15 | Evidence Closure | Is proof evidence generated? | 23 | 39 | 0 | 0 |
| 16 | Certification Closure | Has closure been certified? | 27 | 35 | 0 | 0 |
| 17 | Evolution Closure | Can the capability evolve safely? | 62 | 0 | 0 | 0 |

| Capability closure status | Count |
|---|---:|
| CLOSED | 0 |
| OPEN | 62 |
| BLOCKED | 0 |
| UNKNOWN | 0 |

Fully closed on all seventeen dimensions: .

## 7. Gap register — identified, not fixed

**140 gap instances** across 62 capabilities. Each names the canonical owner that would discharge it. UICM discharges none of them: it is a measurement layer, and repairing another owner's record would be the parallel authority this programme exists to forbid.

| Gap dimension | Instances | Canonical owner that discharges it |
|---|---:|---|
| Determinism Closure | 54 | `engine/determinism` (double-build / `compare_builds`) and the per-programme `--replay` owners. No per-capability determinism obligation is located for the other 54 capabilities, so the dimension is OPEN by absence of an obligation, not by a failed one. |
| Evidence Closure | 39 | The capability itself — an `evidence.py` producer or a declared `ucos-*-evidence/*` format. 23 of 62 carry one; the rest carry only a RIE `evidence_present` flag and a UGA `evidence_class`, neither of which produces evidence. |
| Certification Closure | 35 | `engine/universal_certification` (the producer-agnostic certifier) or a CI gate in `.github/workflows/`. 27 of 62 have an instrument; the rest are named in a 00-MASTER certification document without a decision procedure. |
| Contract Closure | 4 | The capability's own `__init__.py` (interface publication is capability-local). |
| Coverage Closure | 3 | `pyproject.toml` coverage denominator (same edit as the registry gap). |
| Registry Closure | 3 | `pyproject.toml` — `[tool.pytest.ini_options].addopts` + `[tool.coverage.run].source`. |
| Governance Closure | 1 | `00-MASTER/UCOS-UGA-001/01-EXECUTABLE-OBJECT-REGISTRY.json` — governance follows identity; same discharge as the identity gap. |
| Identity Closure | 1 | `00-MASTER/UCOS-UGA-001/01-EXECUTABLE-OBJECT-REGISTRY.json` — UCOS-UGA-001 is the identity authority; re-render admits the artifacts. |

### 7.1 Gap instances

| Gap ID | Capability | Dimension | State | Measured finding |
|---|---|---|---|---|
| `UICM-GAP-001` | `engine.acceptance` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/IMPLEMENT-001A/00-IMPLEMENT-001-COMPLETION-REPORT.md |
| `UICM-GAP-002` | `engine.certification` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/ACEE-000001/acee.json |
| `UICM-GAP-003` | `engine.ceu` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/P0-FINAL-CLOSURE-002/UCOS-COVERAGE-CLOSURE.json |
| `UICM-GAP-004` | `engine.discovery` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/BASELINE-001/FINAL-BASELINE-CERTIFICATE.md |
| `UICM-GAP-005` | `engine.factory` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/ACEE-000001/acee.json |
| `UICM-GAP-006` | `engine.foundation` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/BASELINE-001/FINAL-BASELINE-CERTIFICATE.md |
| `UICM-GAP-007` | `engine.governance` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/MIP-W1-P001/07-UNIVERSAL-CAPABILITY-CATALOG.md |
| `UICM-GAP-008` | `engine.registry` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/ACEE-000001/acee.json |
| `UICM-GAP-009` | `engine.universal_certification` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/ACEE-000001/acee.json |
| `UICM-GAP-010` | `engine.validation` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/ACEE-000001/acee.json |
| `UICM-GAP-011` | `platform.administration` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/MCP-003-MASTER-EXECUTION.md |
| `UICM-GAP-012` | `platform.artifact_explorer` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/MIP-W1-P001/07-UNIVERSAL-CAPABILITY-CATALOG.md |
| `UICM-GAP-013` | `platform.blueprints` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/IMPLEMENT-001B/01-C2-EVIDENCE-AND-DISPOSITION.md |
| `UICM-GAP-014` | `platform.certification` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/BASELINE-001/FINAL-BASELINE-CERTIFICATE.md |
| `UICM-GAP-015` | `platform.execution_dashboard` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/MCP-003-MASTER-EXECUTION.md |
| `UICM-GAP-016` | `platform.foundation` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/BASELINE-001/FINAL-BASELINE-CERTIFICATE.md |
| `UICM-GAP-017` | `platform.generation` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/CAEM-001/01-MANDATE-TO-CANONICAL-HOME-MAP.md |
| `UICM-GAP-018` | `platform.identity` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/IMPLEMENT-001/00-EXECUTABLE-BACKLOG.md |
| `UICM-GAP-019` | `platform.portal` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/MIP-W1-P001/07-UNIVERSAL-CAPABILITY-CATALOG.md |
| `UICM-GAP-020` | `platform.projects` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/MCP-003-MASTER-EXECUTION.md |
| `UICM-GAP-021` | `platform.providers` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/MIP-W1-P001/07-UNIVERSAL-CAPABILITY-CATALOG.md |
| `UICM-GAP-022` | `platform.runtime_operations` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/ACEE-000001/acee.json |
| `UICM-GAP-023` | `platform.runtime_platform` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/MIP-W1-P001/07-UNIVERSAL-CAPABILITY-CATALOG.md |
| `UICM-GAP-024` | `platform.universal_assimilation` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/UCOS-RIB-001/02-REPOSITORY-CAPABILITY-GRAPH.md |
| `UICM-GAP-025` | `platform.universal_generator` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/UCOS-RIB-001/02-REPOSITORY-CAPABILITY-GRAPH.md |
| `UICM-GAP-026` | `platform.universal_master_plan` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/UCOS-RIB-001/02-REPOSITORY-CAPABILITY-GRAPH.md |
| `UICM-GAP-027` | `platform.universal_measurement` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/UCOS-RIB-001/02-REPOSITORY-CAPABILITY-GRAPH.md |
| `UICM-GAP-028` | `platform.universal_ownership` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/P0-FINAL-CLOSURE-002/UCOS-COVERAGE-CLOSURE.json |
| `UICM-GAP-029` | `platform.universal_portal` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/MIP-W1-P001/07-UNIVERSAL-CAPABILITY-CATALOG.md |
| `UICM-GAP-030` | `platform.universal_project_state` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/UCOS-RIB-001/02-REPOSITORY-CAPABILITY-GRAPH.md |
| `UICM-GAP-031` | `platform.universal_truth` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/UCOS-RIB-001/02-REPOSITORY-CAPABILITY-GRAPH.md |
| `UICM-GAP-032` | `platform.universal_validation` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/ACEE-000001/acee.json |
| `UICM-GAP-033` | `platform.validation` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/ACEE-000001/acee.json |
| `UICM-GAP-034` | `platform.validation_intelligence` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/ACEE-000001/acee.json |
| `UICM-GAP-035` | `platform.workspace` | certification | OPEN | no certification instrument; mention-level reference: 00-MASTER/MCP-003-MASTER-EXECUTION.md |
| `UICM-GAP-036` | `engine` | contract | OPEN | __init__ publishes no __all__ interface |
| `UICM-GAP-037` | `engine.ceu` | contract | OPEN | __init__ publishes no __all__ interface |
| `UICM-GAP-038` | `platform` | contract | OPEN | __init__ publishes no __all__ interface |
| `UICM-GAP-039` | `platform.universal_assurance` | contract | OPEN | __init__ publishes no __all__ interface |
| `UICM-GAP-040` | `engine` | coverage | OPEN | absent from coverage denominator |
| `UICM-GAP-041` | `engine.constitution` | coverage | OPEN | absent from coverage denominator |
| `UICM-GAP-042` | `platform` | coverage | OPEN | absent from coverage denominator |
| `UICM-GAP-043` | `engine.acceptance` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-044` | `engine.certification` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-045` | `engine.ceu` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-046` | `engine.civilization` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-047` | `engine.compiler` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-048` | `engine.context` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-049` | `engine.discovery` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-050` | `engine.factory` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-051` | `engine.foundation` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-052` | `engine.governance` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-053` | `engine.graph` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-054` | `engine.kernel` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-055` | `engine.knowledge` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-056` | `engine.provider` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-057` | `engine.registry` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-058` | `engine.runtime` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-059` | `engine.universal_certification` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-060` | `engine.validation` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-061` | `platform.administration` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-062` | `platform.artifact_explorer` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-063` | `platform.blueprints` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-064` | `platform.certification` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-065` | `platform.commercial_intelligence` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-066` | `platform.coverage` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-067` | `platform.execution_dashboard` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-068` | `platform.foundation` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-069` | `platform.generation` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-070` | `platform.identity` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-071` | `platform.measurement` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-072` | `platform.observability` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-073` | `platform.portal` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-074` | `platform.projects` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-075` | `platform.providers` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-076` | `platform.repository_intelligence` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-077` | `platform.repository_operations` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-078` | `platform.runtime_operations` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-079` | `platform.runtime_platform` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-080` | `platform.security` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-081` | `platform.universal_assimilation` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-082` | `platform.universal_assurance` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-083` | `platform.universal_control_plane` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-084` | `platform.universal_foundation` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-085` | `platform.universal_generator` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-086` | `platform.universal_master_plan` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-087` | `platform.universal_measurement` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-088` | `platform.universal_ownership` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-089` | `platform.universal_portal` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-090` | `platform.universal_project_state` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-091` | `platform.universal_provider` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-092` | `platform.universal_truth` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-093` | `platform.universal_validation` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-094` | `platform.validation` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-095` | `platform.validation_intelligence` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-096` | `platform.workspace` | determinism | OPEN | no located per-capability determinism/replay obligation |
| `UICM-GAP-097` | `engine` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-098` | `engine.ceu` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-099` | `engine.civilization` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-100` | `engine.compiler` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-101` | `engine.constitution` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-102` | `engine.determinism` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-103` | `engine.foundation` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-104` | `engine.kernel` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-105` | `engine.nucleus` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-106` | `engine.provider` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-107` | `engine.registry` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-108` | `engine.runtime` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-109` | `engine.uaue` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-110` | `engine.uckp` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-111` | `platform` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-112` | `platform.administration` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-113` | `platform.blueprints` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-114` | `platform.foundation` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-115` | `platform.generation` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-116` | `platform.identity` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-117` | `platform.observability` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-118` | `platform.portal` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-119` | `platform.projects` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-120` | `platform.providers` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-121` | `platform.repository_operations` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-122` | `platform.runtime_operations` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-123` | `platform.runtime_platform` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-124` | `platform.security` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-125` | `platform.universal_assimilation` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-126` | `platform.universal_control_plane` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-127` | `platform.universal_foundation` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-128` | `platform.universal_generator` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-129` | `platform.universal_master_plan` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-130` | `platform.universal_measurement` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-131` | `platform.universal_pipeline` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-132` | `platform.universal_portal` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-133` | `platform.universal_project_state` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-134` | `platform.universal_truth` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-135` | `platform.workspace` | evidence | OPEN | no evidence producer; references only: RIE evidence_present; UGA evidence_class VALIDATION |
| `UICM-GAP-136` | `engine.uckp` | governance | OPEN | UGA governance incomplete (2 unregistered) |
| `UICM-GAP-137` | `engine.uckp` | identity | OPEN | 2 artifact(s) without UGA identity |
| `UICM-GAP-138` | `engine` | registry | OPEN | absent from coverage.source, pytest --cov |
| `UICM-GAP-139` | `engine.constitution` | registry | OPEN | absent from coverage.source, pytest --cov |
| `UICM-GAP-140` | `platform` | registry | OPEN | absent from coverage.source, pytest --cov |

### 7.2 The dominant finding

**Determinism Closure is OPEN for 54 of 62 capabilities.** This is the systemic gap in the population, and it is an absence of an *obligation*, not a failed measurement: `engine/determinism` proves double-build reproducibility for compiler-produced artifacts, and five programmes prove byte replay of their own rendered registers, but no located instrument asks the replay question of a capability in general.

The next two findings are Evidence Closure (39 OPEN) and Certification Closure (35 OPEN). Together with determinism these three account for 128 of 140 gap instances — so closure is not blocked by many small omissions but by three dimensions that were never asked of a capability in general.

### 7.3 Gaps that are drift rather than absence

`UICM-GAP-137` (identity) and its governance twin record that `engine/uckp/resolution.py` and `engine/uckp/uga_projection.py` are tracked but carry no UCOS-UGA-001 `universal_id`. UGA-INV-01 requires every version-controlled object to carry one, so this is **registry drift against a live invariant**, not a modelling gap. The discharge is a re-render by the identity authority; UICM must report it and stop.

Likewise `engine.constitution` is absent from the coverage denominator while shipping `engine/tests/constitution/`. The repository's own admission rule in `pyproject.toml` states a package joins `--cov` once it ships a suite. It ships one. That is a registration gap against a stated rule.

## 8. Determination

| Question | Measured answer |
|---|---|
| Population discovered without enumeration? | YES — 62 capabilities derived from a rule over the tracked boundary |
| Orphan artifacts under the declared roots? | 0 |
| Duplicate capability ownership? | 0 |
| Duplicate identity minted by UICM? | 0 — identity is read, never minted |
| Duplicate registry opened by UICM? | 0 — every column is a reference |
| Capabilities at full 17-dimension closure? | 0 of 62 |
| Gap instances disclosed? | 140 |
| Gaps fixed by this report? | 0 — discovery only, by instruction |

**DISCOVERY COMPLETE.** The population, its canonical owners and its missing closure dimensions are measured. Closure implementation may now proceed against this population: UICM adapters over the three confirmed owners, then the measurement engine, then certification.
