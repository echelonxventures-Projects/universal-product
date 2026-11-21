# CAEM-001 · OUTPUT 04 — VERIFICATION EVIDENCE

> **AUTHORITY = NONE — DERIVED TRUTH.** · **`CERTIFIED-PROVISIONAL`; Tier T1 VACANT** (`VAC-01` · `CMG-OQ-02` · `UCCEP-F-004`).

Every command below was executed in this working copy at HEAD `df763bf917943321886c3fc973eac4a1569b6183` on branch `integration/recovery-001`. Output is verbatim. All are read-only or deterministic-regenerating; **no command mutated a tracked file** (confirmed: the only tracked modifications in the tree, `.gitignore` and `scripts/ucos-env.sh`, were present before this session began and were not touched).

---

## §1 — BASELINE

```
$ git rev-parse HEAD
df763bf917943321886c3fc973eac4a1569b6183

$ git branch --show-current
integration/recovery-001

$ git log -1 --format='%h %ad %s' --date=short
df763bf 2026-07-28 UCOS-RIB-001: commit the blueprint as measured from a CLEAN tree

$ git status --porcelain
 M .gitignore
 M scripts/ucos-env.sh
?? 00-MASTER/CAEM-001/

$ git rev-parse --abbrev-ref @{u}
fatal: no upstream configured for branch 'integration/recovery-001'

$ git merge-base --is-ancestor 1c6e750 HEAD && echo ANCESTOR-YES
ANCESTOR-YES                       # UCCEP-000006 rollback anchor RB-1

$ git merge-base --is-ancestor 527485a HEAD && echo ANCESTOR-YES
ANCESTOR-YES                       # UCOS-ACFV-000001 baseline

$ git rev-list --count 1c6e750..HEAD
44

$ git ls-files | wc -l
4981
```

## §2 — GATES THAT PASS

```
$ python3 -m engine.graph.cli validate
{
  "dangling_edge_endpoints": [],
  "dependency_cycle": [],
  "duplicate_node_ids": [],
  "edge_count": 12829,
  "is_valid": true,
  "malformed_edge_ids": [],
  "malformed_node_ids": [],
  "node_count": 1218,
  "unversioned_artifacts": []
}
```
→ **No circular dependencies. No orphan/dangling edges. 1,218 nodes, 12,829 edges.**

```
$ python3 00-BOOK/tools/ukb.py enforce --pre
UMB-IMP-001 Enforcement Gate [PRE-REGISTRATION]  (audit run #534)
  eligible on-disk artifacts : 1193
  registered (in registers)  : 1193
  unregistered eligible      : 0
  unclassified (OTHER/MISC)  : 0 (GATED)
  reconciled sets declared   : 1 (CMG)
  reconciled-set drift       : 0 (GATED)
  invalid (unreadable/empty) : 0
  awaiting VCS binding       : 0 (REPORTED)
ENFORCEMENT PASSED
```
→ **Registration parity 1,193 = 1,193; zero drift.** (Note: `MCP-002` records 1,199 — that figure predates the 44 intervening commits.)

```
$ python3 00-MASTER/UAKOS-CLOSURE-002/closure_engine.py --gate
UAKOS-CLOSURE-002: CLOSED | concepts=440 | gaps=0
  {"conversation_only": 0, "duplicate_canonical_homes": 0, "in_repo_unhomed": 0,
   "not_homed_concepts": 0, "orphan_concepts": 0, "ukda_content_hash_duplicates": 0,
   "upload_only": 0}                                                        [exit 0]

$ python3 00-MASTER/UAKOS-CLOSURE-002/phase2_engine.py --gate
UAKOS-CLOSURE-002 · PHASE-002: CLOSED | concepts=440 homed=440 unhomed=0 | gaps=0
  {… all seven invariants 0 …}                                              [exit 0]
```
→ **All seven closure invariants are zero. No duplicate canonical homes. No orphan concepts.**

## §3 — GATES THAT FAIL

### 3.1 `ukb validate` — FAILS, exit 1, 539 problems (finding RG-09-A)

```
$ python3 00-BOOK/tools/ukb.py validate
jsonschema validation: ran.

VALIDATION FAILED — 539 problem(s):
  - UCOS-ENVIRONMENTS-000001 schema: 'UCOS-ENVIRONMENTS-000001' does not match '^UCOS-[A-Z]{2,6}-[0-9]{6}$'
  - UCOS-VERIFICATION-000001 schema: … does not match '^UCOS-[A-Z]{2,6}-[0-9]{6}$'
  - UCOS-SERVICE-000001    schema: … does not match '^UCOS-[A-Z]{2,6}-[0-9]{6}$'
  … (display capped at 50 by ukb.py:1745; 539 total)

$ python3 00-BOOK/tools/ukb.py validate >/dev/null 2>&1; echo exit=$?
exit=1
```

Full categorisation, obtained by a read-only probe that reuses `ukb.py`'s own loaders and the same frozen schema (`ukb._load_artifacts()`, `jsonschema.validate`, `ukb.validate_executions()`):

```
artifacts                 : 1193
structural problems       :    0     # no duplicate UIDs, no page overlap, no dangling parent/dep
schema problems           :  539     # ALL are the identifier-pattern violation
execution-register probs  :    0
TOTAL                     :  539

schema-failing UIDs by namespace:
   149  UCOS-SERVICE            132  UCOS-INFRASTRUCTU       121  UCOS-APPLICATION
    12  UCOS-IMPLEMENTATI         9  UCOS-IAC001C              9  UCOS-IAC001E
     9  UCOS-EVOUSIS014           9  UCOS-EVOUSIS015           9  UCOS-EVOUSIS016
     8  UCOS-IAC001B              8  UCOS-IAC001D              7  UCOS-IAC001A
     3  UCOS-ARCHITECTURA         2  UCOS-FINALCERTIFI         2  UCOS-VALIDATIONRE
```
→ **539 / 1,193 = 45.2% of registered artifacts fail schema validation.** Corpus structural integrity is perfect; the **frozen schema's ceiling** is what fails.

The ceiling, in the frozen corpus:
```
$ grep -n 'pattern' 00-BOOK/SCHEMAS/artifact.schema.json
20:  "pattern": "^UCOS-[A-Z]{2,6}-[0-9]{6}$"      # namespace ≤ 6 chars; "SERVICE" is 7
39:  "pattern": "^[A-Z]{2,6}$"
44:  "pattern": "^VOL-[0-9]{3}$"                   # ceiling: 1,000 volumes
82:  "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
93:  "items": { "type": "string", "pattern": "^UCOS-[A-Z]{2,6}-[0-9]{6}$" }
```

**Why no gate caught it:**
```
$ grep -n 'ukb.py' verify.sh
105:run_stage "governance enforce --pre" "$PY" 00-BOOK/tools/ukb.py enforce --pre
      # ← `validate` is NOT a verify.sh stage

$ grep -n 'ukb.py\|register.sh' .github/workflows/ucos-registration-gate.yml
48:  run: python3 00-BOOK/tools/ukb.py eligibility --unbound
51:  run: python3 00-BOOK/tools/ukb.py enforce --pre
54:  run: bash 00-BOOK/tools/register.sh --guard
      # ← `validate` is NOT a CI step
```

### 3.2 `closure-phase3-gate` — FAILS, exit 1 (finding `UCCEP-F-001` / OA-5, confirmed live)

```
$ python3 00-MASTER/UAKOS-CLOSURE-002/phase3_engine.py --gate
GATE: repository NOT-CLOSED (fail-closed) — planning delivered, execution pending.
UAKOS-CLOSURE-002 · PHASE-003: PLANNING-COMPLETE · REPOSITORY NOT-CLOSED (fail-closed)
  | planned=0/0 | classes=0 waves=0 | repo=NOT-CLOSED                       [exit 1]
```
→ `planned=0/0`, `classes=0`, `waves=0`: the verdict is a **constant**, not a measurement.

### 3.3 No closure gate exists in CI (finding GG-05, confirmed live)

```
$ grep -rln closure verify.sh .github/workflows/
.github/workflows/uccep-gate.yml
.github/workflows/research-publication-gate.yml
.github/workflows/rfp-gate.yml
```
→ Three matches, **none of which is a closure gate**. `verify.sh` does not match at all.

## §4 — CLOSURE DETERMINATION IS ENVIRONMENT-DEPENDENT (refines ACFV RG-02)

```
$ ls -d ../UCOS
ls: ../UCOS: No such file or directory

$ grep -n 'CORPUS = ' 00-MASTER/UAKOS-CLOSURE-002/closure_engine.py
34:CORPUS = REPO.parent / "UCOS"   # external corpus sibling

$ grep -n 'CLOSURE_SKIP_CORPUS' 00-MASTER/UAKOS-CLOSURE-002/closure_engine.py \
                                 .kiro/hooks/uakos-closure-002.json
closure_engine.py:120:  if CORPUS.is_dir() and os.environ.get("CLOSURE_SKIP_CORPUS") != "1":
uakos-closure-002.json:10:  "command": "CLOSURE_SKIP_CORPUS=1 python3 …"

$ git check-ignore -v 00-MASTER/UAKOS-CLOSURE-002/closure.json
.gitignore:53:00-MASTER/UAKOS-CLOSURE-002/closure.json
```

Both runs — with and without the flag — produced **byte-identical** `CLOSED | concepts=440 | gaps=0`, because `../UCOS` is absent so the guard short-circuits either way. The determination is a function of the environment, not of the commit; and `closure.json` is gitignored, so it is per-clone runtime state rather than Repository Truth.

## §5 — HARD-CODING, VERIFIED VERBATIM

```
$ grep -n 'CURRENCY_PATTERN' platform/commercial_intelligence/contracts.py
53:_CURRENCY_PATTERN = re.compile(r"^[A-Z]{3}$")
165:  if not isinstance(self.currency, str) or not _CURRENCY_PATTERN.match(self.currency):
                                                                          # RG-10

$ grep -n 'app.kubernetes.io' engine/runtime/deploy.py
228: "app.kubernetes.io/name": k8s_name(unit.blueprint_id)
229: "app.kubernetes.io/version": unit.version
230: "app.kubernetes.io/managed-by": "ucos-runtime-assembly"
288: "selector": {"matchLabels": {"app.kubernetes.io/name": name}}
327: "selector": {"app.kubernetes.io/name": name}                          # IG-08

$ grep -n '"language"\|"locale"' engine/context/catalog.py
182: "language": "en"
192: "locale": "engineering culture of the UCOS programme"                  # IG-06

$ grep -n 'SOURCE_DATE_EPOCH\|NORMALIZED_LOCALE\|NORMALIZED_TIMEZONE' \
       engine/determinism/hermetic.py
66: SOURCE_DATE_EPOCH = 0          # 1970-01-01, Gregorian
70: NORMALIZED_LOCALE = "C"
71: NORMALIZED_TIMEZONE = "UTC"
75-81: injected as LC_ALL / LANG / LC_CTYPE / TZ / SOURCE_DATE_EPOCH        # IG-07

$ grep -n 'class RegistryKind' engine/registry/universal/identity.py
42:class RegistryKind(str, Enum)   # 13 closed members                      # IG-01
```

## §6 — VOCABULARY

```
$ git grep -icE 'Fabric' -- '*.md' '*.py' | wc -l
0                     # the token "Fabric" occurs in zero tracked md/py files

$ git grep -l 'MCOS' | wc -l
0                     # "MCOS" occurs in zero tracked files

$ git grep -inE '\bCAEM\b' | wc -l
0                     # zero prior occurrence of this programme's label
```

## §7 — MISSION FINAL-VERIFICATION CHECKLIST, HONESTLY SCORED

The mission requires twelve verifications before completion. Scored against evidence above:

| # | Mission verification | Result | Basis |
|---|---|---|---|
| 1 | No duplicated concepts | **PASS** | `duplicate_canonical_homes = 0` over 440 concepts; plus the manual name-level check in Output `01` |
| 2 | No architectural regression | **PASS (by construction)** | Nothing outside `00-MASTER/CAEM-001/` was written |
| 3 | No hard-coded domains | **PASS** | No ERP/CRM/commerce/healthcare/government schema exists in any realized tree |
| 4 | No hard-coded technology | **FAIL** | IG-08 (Kubernetes in `engine/runtime/deploy.py`) |
| 5 | No hard-coded operational ecosystems | **PASS** | Verified: zero hard-coded verticals; `LAW P43-001` holds |
| 6 | No hard-coded realities | **NOT VERIFIABLE** | Certified at document layer only; no executable probe exists (Output `03` §1 #19–20) |
| 7 | No orphan artefacts | **PASS** | `orphan_concepts = 0`; `dangling_edge_endpoints = []`; 0 unregistered eligible |
| 8 | No circular dependencies | **PASS** | `dependency_cycle = []` |
| 9 | Complete constitutional traceability | **FAIL** | ACFV `RG-06`/OA-4: traceability completeness ≈22.7%; `WP-UCCEP-002` open |
| 10 | Complete registry synchronisation | **PASS** | 1,193 = 1,193, zero drift, 0 unclassified |
| 11 | Complete Digital Twin synchronisation | **PARTIAL** | 10/10 integrity domains certified, but `UMB-CERT-001`: *"fixture data, not live systems"*; 1 live connector |
| 12 | Repository internally consistent | **FAIL** | `ukb validate` exit 1, 539 problems (RG-09-A); `closure-phase3-gate` exit 1 |

**Score: 7 PASS · 3 FAIL · 1 PARTIAL · 1 NOT VERIFIABLE.**

Per the mission's own rule — *"Only declare completion after all verification passes successfully"* — **completion of the mission MUST NOT be declared.** Three verifications fail on measured evidence, and none of the three is remediable within this programme's permitted write scope.

---

*END — `CAEM-001` OUTPUT 04 · AUTHORITY = NONE · `CERTIFIED-PROVISIONAL` · Tier T1 VACANT*
