# 06 — Universal Object Catalog

**Anchor** `c6c20fb` · **Canonical owner** `00-BOOK/DATA/artifacts.json` (Universal Artifact Registry)
**Authority** NONE — this output **binds by pointer** to the canonical owner and creates no second registry.

---

## 1 · Registration state

| Measure | Value |
|---|---|
| Registered objects | **1,204** |
| Unique `universal_id` | **1,204 / 1,204 — no duplicates** |
| Objects whose `path` resolves on disk | **1,204 / 1,204** |
| Eligible on-disk artifacts unregistered | **0 (GATED)** |
| Unclassified (`OTHER`/`MISC`) | **0 (GATED)** |
| Invalid (unreadable / empty) | **0** |
| Page range allocated | 9,618 pages |
| Volumes | 25 declared · **23 populated** |
| Categories | 94 in use · 95 sequences allocated |
| Programmes | 88 |
| Owner | `UCOS-PROGRAM-CUSTODIAN` — 1,204 / 1,204 (single owner) |

## 2 · Per-object attribute schema (as registered)

Each object carries 19 fields. Wave-1 measured population of every one:

| Field | Populated | Assessment |
|---|---|---|
| `universal_id` | 1,204 (100%) | unique, immutable, sequential per category |
| `native_id` | **379 (31.5%)** | **825 null** — see §5 |
| `name` | 1,204 (100%) | — |
| `description` | **0 (0.0%)** | **empty for every object** — see §5 |
| `category` | 1,204 (100%) | 94 distinct |
| `volume` | 1,204 (100%) | 62.0% concentrated in `VOL-000` — see §5 |
| `page_start` / `page_end` | 1,204 (100%) | contiguous allocation, cursor 9,618 |
| `status` | 1,204 (100%) | 6 distinct values |
| `version` | 1,204 (100%) | **`1.0.0` for all 1,204** — non-differentiating |
| `parent` | 1,203 (99.9%) | 1 null (the book root — correct) |
| `dependencies` | **190 (15.8%)** | **1,014 empty** — see §5 |
| `program` | 1,204 (100%) | 88 distinct |
| `owner` | 1,204 (100%) | single custodian |
| `tags` | 1,204 (100%) | — |
| `path` / `return_link` | 1,204 (100%) | all resolve |
| `content_hash` | 1,204 (100%) | **10 stale — see §5 / blocker B-1** |
| `traceability` | 1,204 present · **mean 2.2% populated** | 13 sub-dimensions — see output 13 |

## 3 · Object type distribution — by category (top 40 of 94)

| Category | Objects | | Category | Objects |
|---|---|---|---|---|
| SERVICE | 149 | | DAT | 19 |
| DATA | 134 | | SVC | 19 |
| INFRASTRUCTU* | 132 | | RUN | 18 |
| APPLICATION | 121 | | IMPLEMENTATI* | 12 |
| CON | 62 | | INTELLIGENCE | 11 |
| PLT | 56 | | IAC001C · IAC001E | 9 each |
| USIS | 36 | | EVOUSIS014/015/016 | 9 each |
| CEP | 35 | | IAC001B · IAC001D | 8 each |
| UMB | 31 | | CAT · GEN · IAC001A | 7 each |
| ARCH | 25 | | GOV | 6 |
| IMP · APP · MASTER | 24 each | | SEC | 5 |
| REF · ENG | 21 each | | EXEC | 4 |
| ADV · INF | 20 each | | VSN · FRZ · ADR · ARCHITECTURA* | 3 each |
| REG | 19 | | remaining 54 categories | 1–2 each |

`*` Four category labels are **truncated at 12 characters** (`INFRASTRUCTU`, `IMPLEMENTATI`,
`ARCHITECTURA`, and the abbreviations `CON`/`PLT`/`DAT`/`SVC`). This is a category-derivation
truncation in the registration engine, not a data-entry error — it makes category strings
non-round-trippable to their source names.

## 4 · Lifecycle distribution

| Status | Objects | Share |
|---|---|---|
| ACTIVE | 1,103 | 91.6% |
| COMPLETE | 43 | 3.6% |
| FROZEN | 27 | 2.2% |
| UNDER_REVIEW | 15 | 1.2% |
| FINAL | 9 | 0.7% |
| CERTIFIED | 7 | 0.6% |

Only **1.3%** of registered objects have reached FINAL or CERTIFIED lifecycle. 91.6% remain ACTIVE.

## 5 · Mandatory anomaly determination

### 5.1 Missing identifiers

| Anomaly | Count | Determination |
|---|---|---|
| Missing `universal_id` | **0** | clean |
| **Missing UUID** | **1,204 (100%)** | **No object in the corpus carries a UUID.** Identity is namespace-prefixed sequential (`UCOS-BOOK-000000`, `UCOS-CON-000064`). 0 of 1,204 `universal_id` values are UUID-shaped. See output 09. |
| Missing `native_id` | **825 (68.5%)** | 825 objects have no canonical native identifier, so they are addressable only by the registry-assigned surrogate |

### 5.2 Duplicate identifiers

`universal_id` duplicates: **0**. `native_id` collisions: **7 groups / 22 objects**.

| `native_id` | Objects sharing it |
|---|---|
| `EC2-CAP-SEC-001` | **7** |
| `UCOS-COMP-000000` | **4** |
| `EC2-EPIC-006` | **3** |
| `EC2` | 2 |
| `UCOS-COMP-000001` | 2 |
| `CEP-STAGE-02` | 2 |
| `CEP-STAGE-03` | 2 |

The registry's uniqueness invariant holds on the surrogate key only. The **native** key — the one
humans and prose cite — is not unique.

### 5.3 Duplicate / conflicting / overlapping concepts

| Class | Count | Blocking | Detail |
|---|---|---|---|
| `DUP-CAPABILITY` | 0 | yes | — |
| `DUP-INTERFACE` | 0 | yes | — |
| `DUP-RUNTIME` | 0 | yes | — |
| `DUP-REGISTRY` | 0 | yes | — |
| `DUP-CONSTITUTION` | 0 | yes | — |
| `DUP-KNOWLEDGE` | 0 | yes | — |
| `DUP-NAME` cross-layer collision | 4 | no | `certification`, `foundation`, `validation`, `identity` under both `engine/` and `platform/` |
| `MULTI-ENGINE PROGRAMME` | 1 | no | `UAKOS-CLOSURE-002` runs 3 engines (`closure_engine.py`, `phase2_engine.py`, `phase3_engine.py`) |
| `FREEZE-BOUNDARY COPY` | 2 | no | `SOURCE-FILES.txt` and `SOURCE-HASHES.txt` each exist identically in `00-SOURCE-MANIFEST/` and `99-FREEZE/` |
| **Content-hash duplicate groups (measured)** | **2** | — | exactly the two freeze-boundary pairs above; no unintended content duplication anywhere in 1,204 objects |

**Conflicting concept — 1 material instance:** `closure.json` declares `determination: CLOSED`
while `phase3.json` in the same programme directory declares `repository_status: NOT-CLOSED`, both at
baseline `c6c20fb`. One programme, two contradictory determinations.

### 5.4 Orphan / dead / unreferenced objects

| Class | Count | Source |
|---|---|---|
| Orphan units (unreachable in every measured plane) | **0** | RIB GATE-11 PASS |
| Orphan concepts | **0** | `closure.json` (repo scope) |
| Dead engines (engine no declared entry point names) | **0** | RIB `GAP-DEAD-ENGINE` |
| Units with no canonical owner | **0** | RIB `GAP-OWNER` |
| Capability records resolving to no unit | **0** | RIB `GAP-CAPABILITY` |
| Units homing no artifact and publishing no interface | **0** | RIB `GAP-REGISTRY` |
| **Unreferenced concepts (co-occurrence isolated)** | **1** | `phase2.json.cooccurrence.isolated` |
| **Unpopulated volumes** | **2** | `VOL-013`, `VOL-014` declared in `volumes.json`, zero artifacts |
| **Residual empty directory** | **1** | `engine/identity/` contains only `__pycache__` — no source, untracked, absent from the capability catalog |

### 5.5 Broken references

| Class | Count |
|---|---|
| Dangling graph edge endpoints | **0** (declared by design under UMB-007 §5 where external trace markers exist) |
| Unresolved dependency edges | **0** — RIB GATE-06 PASS |
| Artifact paths not on disk | **0 / 1,204** |
| Malformed node / edge IDs | **0** |
| Broken symlinks | **0** |
| **Stale `content_hash` bindings** | **10 / 1,204** — see below |

**The one real broken reference class.** Ten objects record a `content_hash` that does not match
their own committed bytes at the anchor:

| Object path | HEAD-recorded | Actual bytes | Match |
|---|---|---|---|
| `intelligence/UCOS-IMP-BASELINE-001.rib.json` | `3b540156726e…` | `946e084f8781…` | ✗ |
| `intelligence/UCOS-RIE-AEOS-READINESS.json` | `909da0a1d581…` | `162e8ac4809b…` | ✗ |
| `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json` | `5fe102e883e0…` | `17e991937174…` | ✗ |
| `intelligence/UCOS-RIE-DEPENDENCY-GRAPH.json` | `bad77ec9e0d0…` | `464fabcd3b03…` | ✗ |
| `intelligence/UCOS-RIE-DIGITAL-TWIN.json` | `fe906caae8a6…` | `43b035e3eed1…` | ✗ |
| `intelligence/UCOS-RIE-EXECUTION-FRONTIER.json` | `61dba1590da3…` | `cc48790458f6…` | ✗ |
| `intelligence/UCOS-RIE-HEALTH.json` | `e17df8844999…` | `d45ee3f5d74b…` | ✗ |
| `intelligence/UCOS-RIE-MODEL.json` | `5afb11fb4867…` | `90e60fc81f10…` | ✗ |
| `intelligence/UCOS-RIE-PROGRESS.json` | `b83933610ad9…` | `cd056503cdc2…` | ✗ |
| `intelligence/UCOS-RIE-SNAPSHOT.json` | `e59857d8dcf5…` | `eac221100e06…` | ✗ |

**0 of 10 HEAD-recorded hashes are correct. 10 of 10 re-registered hashes are correct.** This is
blocker **B-1**; root cause and proof are in output 16 §B-1.

### 5.6 Circular dependencies

| Plane | Cycles | Class |
|---|---|---|
| Typed `Depends-On` graph (12,851 edges) | **0** | verified `dependency_cycle: []` |
| Python import plane, cross-unit | **0** | RIB GATE-10 PASS (`CYC-ARCHITECTURAL`) |
| Python import plane, intra-unit `__init__` re-export | present, **declared benign** | `CYC-INIT-REEXPORT` |
| **Programme-scope citation plane** | **2** | `ARCH↔CAT`, `CEP↔IMP` — mutual programme-level references, not `Depends-On` |

### 5.7 Hidden dependencies

| Hidden dependency | Nature |
|---|---|
| **External source corpus** at `<repo>/../UCOS` (6,332 files) | Closure determinations depend on a directory **outside the repository** that is neither tracked, versioned, nor hash-pinned. Its presence or absence silently changes the verdict (437/0-gap vs 528/91-gap). |
| **Connector-supplied dimension state** | 6 of 15 progress dimensions are fed by GitHub Actions / Kubernetes / Prometheus / Trivy / SonarQube cursors last advanced 2026-07-15 — all now `stale: true`. Four report `BLOCKED` purely from staleness. |
| **Optional `jsonschema`** | `ukb validate` silently degrades to structural-only checks when absent and still exits 0 (`UCCEP-F-006`); CI installs it with `\|\| true`. The strength of the validation claim depends on an unpinned import. |
| **`intelligence/` regeneration ↔ registry** | Regenerating any derived intelligence artifact invalidates its registry `content_hash`. The coupling is real but unenforced — exactly how B-1 arose. |
| **`engine` dependency isolation** | RIB `GAP-DEPENDENCY` = 1 (`engine`): the certified root has no measured edge in either direction, so its consumers are implicit rather than declared. |

## 6 · Catalog verdict

| Criterion | Verdict |
|---|---|
| Every object uniquely registered (surrogate key) | **PASS** — 1,204/1,204 unique |
| Every object type inventoried | **PASS** — 94 categories, 6 lifecycle states |
| Zero missing IDs, zero duplicate IDs (surrogate) | **PASS** |
| Zero orphan / dead / unowned objects | **PASS** |
| Zero circular dependencies in the typed plane | **PASS** |
| Zero broken path references | **PASS** |
| Every object carries a UUID | **FAIL** — 0/1,204 |
| Native identifiers unique | **FAIL** — 7 collision groups / 22 objects |
| Content-hash evidence binding correct | **FAIL** — 10/1,204 stale (**B-1**) |
| Objects self-describing (`description`, differentiated `version`) | **FAIL** — 0% described, 100% at `1.0.0` |
| Dependencies declared | **FAIL** — 84.2% empty |
