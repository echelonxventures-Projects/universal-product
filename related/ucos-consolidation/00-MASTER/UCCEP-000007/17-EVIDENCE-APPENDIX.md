# Output 17 — Evidence Appendix

> **STATUS DOMAIN:** GOVERNANCE (measurement) · **STATUS BASIS:** this appendix is itself the evidence record; every command below was executed against HEAD `9de85ad` with the working tree CLEAN

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000007` · OUTPUT 17 |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| SUBJECT | Every command, output file and digest behind Outputs 1–16. No interpretation. |
| REPRODUCTION | Check out `9de85adb7e26211d07bd99b3bed356280c936a93` with a clean tree and re-run the commands in §2. Read-only commands reproduce byte-identically; transaction commands are idempotent at this baseline (§4). |

---

## 1. Why the commands are recorded inline

`.gitignore` line 72 excludes **`00-MASTER/**/evidence/`** from version control (→ OBS-8). The 24 raw outputs written by this programme therefore exist on disk but not in committed history. To keep the baseline reproducible from committed content alone, every command and every material value is recorded **in the committed Markdown**, and the raw files are treated as convenience artifacts rather than the record of truth.

## 2. Commands executed

### E-01 · Baseline identity (Output 1 §1)
```bash
git rev-parse HEAD; git rev-parse --short HEAD; git rev-parse --abbrev-ref HEAD
git log -1 --format=%s; git log -1 --format=%cI
git status --porcelain | wc -l
git ls-files | wc -l
git rev-list --count HEAD
git merge-base --is-ancestor 1c6e750e53efdbcba5fc501d58fc99781b03a966 HEAD
git remote -v; git rev-parse --abbrev-ref --symbolic-full-name @{u}
```
→ `9de85adb7e26211d07bd99b3bed356280c936a93` · `programme/evo-usis-005` · dirty **0** · tracked **4,499** · commits **183** · anchor is an ancestor (exit 0) · upstream: **fatal: no upstream configured**

### E-02 · Zone and extension census (Output 1 §2–§3)
```bash
git -c core.quotePath=false ls-files | awk -F/ '{if (NF==1) print "(root)"; else print $1}' | sort | uniq -c | sort -rn
git -c core.quotePath=false ls-files | awk -F. 'NF>1{print $NF} NF==1{print "(none)"}' | sort | uniq -c | sort -rn
```
→ `.md` 2,496 · `.py` 1,412 · `.json` 548 · `.docx` 24 · `.sh` 8 · `.yml` 4 · `.txt` 4 · `.toml` 1 · `.gitignore` 1 · none 1. The `core.quotePath=false` flag is required (→ OBS-1).

### E-03 · Code volume (Outputs 1 §4, 6 §1)
```bash
for t in engine platform data service application infrastructure intelligence \
         00-BOOK/tools 00-CMG/tools scripts; do
  git ls-files "$t" | grep '\.py$' | xargs wc -l | tail -1
done
for t in engine platform data service application infrastructure; do
  git ls-files "$t" | grep -c 'test_.*\.py$'
done
```
→ 1,395 `.py` files · 292,599 LOC · 564 test modules

### E-04 · Programme directories and engines (Output 2)
```bash
for d in 00-MASTER/*/; do echo "$(basename $d) $(git ls-files "$d" | wc -l)"; done
git ls-files '00-MASTER/**/*.py'
```
→ 45 directories · 646 tracked files · 17 programme engines

### E-05 · Register contents (Output 4)
```bash
git -c core.quotePath=false ls-files 00-BOOK/DATA 00-BOOK/REGISTRIES
python3 - <<'PY'
import json
a=json.load(open('00-BOOK/DATA/artifacts.json'));  print(len(a['artifacts']))
r=json.load(open('00-BOOK/DATA/relationships.json'));print(len(r['relationships']))
i=json.load(open('00-BOOK/DATA/id-ledger.json'));   print(len(i['by_path']), i['page_cursor'])
PY
```
→ artifacts **1,199** · edges **12,841** · `by_path` **1,219** · `page_cursor` **9,587** · volumes **25** · signals **15**

### E-06 · Constitution registry (Output 3)
```bash
python3 -c "import json;d=json.load(open('00-CMG/CMG-REGISTRY.json'));print({k:len(v) for k,v in d.items() if isinstance(v,list)})"
./00-CMG/tools/cmg-gate.sh
for f in 00-CEP/CEP-0*.md; do grep -m1 '^| VERSION' "$f"; done
```
→ 43 artifacts · 60 concerns · 24 kinds · 9 gaps · 7 open questions · 1 vacancy · **findings 0** · READY-PROVISIONAL · `CEP-001` **1.1** · `CEP-002` **1.2**

### E-07 · Capability catalogue (Output 5)
```bash
python3 -c "import json;d=json.load(open('intelligence/UCOS-RIE-CAPABILITY-CATALOG.json'));print(d['count'],d['content_hash'])"
```
→ **42** capabilities · hash `2c740651608f8e7e…` · 14 CERTIFIED / 26 IMPLEMENTED / 2 PLANNED

### E-08 · Dependency DAG, independently recomputed (Output 8 §2)
Kahn layering over the `Depends-On` projection, from `relationships.json` + `artifacts.json` only:
```
Depends-On edges          : 4774
registered artifacts      : 1199
nodes in ordering         : 1199
parallel groups (layers)  : 164
placed / unorderable      : 1199 / 0
critical path length      : 164
single-member groups      : 112
largest group size        : 908
cycle present             : NO
artifacts with >=1 dependency declared : 190
artifacts with non-empty traceability  : 1199
```

### E-09 · Graph validator (Output 8 §3)
```bash
python3 -m engine.graph.cli validate
```
→ `is_valid true` · `dependency_cycle []` · nodes **1,224** · edges **12,841** · exit 0

### E-10 · Corpus enforcement and validation (Output 10 §6)
```bash
python3 00-BOOK/tools/ukb.py validate
python3 00-BOOK/tools/ukb.py enforce --pre
```
→ VALIDATION PASSED, 1,199 artifacts, append-only ledger intact · eligible 1,199 = registered 1,199 · unregistered 0 · unclassified 0 · reconciled sets 1 (CMG) · reconciled-set drift 0 · invalid 0 · *jsonschema not installed — structural checks only* (→ DG-3)

### E-11 · Full verification (Output 6 §2)
```bash
./verify.sh
```
→ exit 0 · ruff PASS · pytest+coverage PASS · coverage report PASS · enforce --pre PASS · TOTAL coverage **97%** over 31,884 statements / 6,162 branches

### E-12 · Registration transaction and drift guard (Outputs 7 §5, 11 §2)
```bash
./00-BOOK/tools/register.sh --guard
```
→ exit **0** · 10 phases · *RESULT: CERTIFIED (hard checks 7/7)* · *RESULT: CERTIFIED (integrity domains 10/10) — scope 1199 artifacts, 15 signals, 1358 change events* · 1,199 = 1,199 · zero drift

### E-13 · Aggregate constitutional gate (Outputs 10, 11)
```bash
python3 00-MASTER/UCCEP-000000/uccep_engine.py --tier full --gate
```
→ exit **0** · `CERTIFIED-PROVISIONAL` · gates **14/14 PASS** · programmes **16/16 PASS** · blocking **none** · seal `a6082ab6c6a61b86…`
Pre-OA-1 comparison run: exit **1** · 13/14 · sole blocking `CK-REG-DRIFT` · seal `12a33bff8c2d1778…`

### E-14 · Self-guards (Output 7 §5)
```bash
for f in --check-declaration --check-no-enumeration --check-write-scope --check-determinism; do
  python3 00-MASTER/UCCEP-000000/uccep_engine.py $f
  python3 00-MASTER/UCDA-000001/ucda_engine.py  $f
done
```
→ **8/8 PASS**

### E-15 · Decision assimilation (Outputs 9 §6, 11 §7)
```bash
python3 -c "import json;u=json.load(open('00-MASTER/UCDA-000001/ucda.json'));print(u['determination'],u['gate'],u['decision_total'],u['evidence_references'],u['seal_sha256'][:16])"
```
→ ASSIMILATED · OPEN · 64 · 205 · `8d34d196a80a05b8`

### E-16 · Absence searches (Output 16 §1)
```bash
grep -rn "M-1\b" --include="*.md" --include="*.json" . | grep -i "migrat\|consolidat\|step"
grep -rln "no new generators\|single execution owner\|consolidated execution generator\|MIGRATION SEQUENCE\|reference-only policy\|freeze policy" --include="*.md" --include="*.json" .
```
→ first: **0 hits**. second: 2 hits, both `07-ENGINEERING/`, both unrelated to UCCEP/UCDA consolidation.

### E-17 · Ignore-authority verification (OBS-8, DG-8)
```bash
git check-ignore -v 00-MASTER/UCCEP-000000/evidence/CK-CMG.log
sed -n '68,72p' .gitignore
for p in .coverage .mypy_cache .ruff_cache .pytest_cache .ec1-venv; do git check-ignore -q "$p" && echo "$p IGNORED"; done
```
→ `.gitignore:72:00-MASTER/**/evidence/` · all caches IGNORED

## 3. Raw evidence files and digests

24 files under `00-MASTER/UCCEP-000007/evidence/` (uncommitted by policy). Verify with `shasum -a 256 -c`.

| File | sha256 |
|---|---|
| `head.txt` | `d14810a99d32fac64003b9de6dcf1c0a7e56f7444ac522bbaace72d8046a3705` |
| `zone-counts.txt` | `3ebf0bb10256b47baa79f2d2e66a649984648c354a3a3702ae26b6267edbb182` |
| `ext-counts.txt` | `bdf33c8feb2fc1f6eaf7373a83e909d53e194c7b2d6485f756c53f8f2536770d` |
| `code-loc.txt` | `61ffc60d1f0ba2187e96800cb83adc64eea1fe833e25e6aad094ffd21aff9e5a` |
| `test-counts.txt` | `d1ecf5f551ee3bf4619e6e11e6fef228ea93ea5cfa854387a6fae37765dc2035` |
| `programme-dirs.txt` | `c81205f7cb965ca033fdd38ceb26b80eaf34b3754cd819e331035b8433b9a499` |
| `programme-engines.txt` | `4b8bee2218f5327e88ec19e71cb5d4e445fc3e76651b488e2cb13e57d139ae64` |
| `registry-files.txt` | `a41e751bce13ffaa735d66b78717bd3c1359c51e664e2a7998e96001510c219e` |
| `registry-metrics.txt` | `c0b06c94f8ea41708fd85d27483a5c3ba1f4fb0dfd5be260b6ed23538aa0be4d` |
| `cep-inventory.txt` | `658c8929dfff1cb450e303b1375ce32080415f143955252d2363319fc3d4dd88` |
| `cmg-ucda-rie.txt` | `b9ada81918473003141b8b3d5975fc31e170505b9cf725451c09af67fcff27f1` |
| `capabilities.txt` | `4a5df6b52113e426f59a761c143a8a33897a826f68aa1058882cb05923066dee` |
| `rie-metrics.txt` | `e3ec7174d6b3708763916d7d4bc2ec8be6f2c374fabaafbd7de16644beec5b3e` |
| `dag-computed.txt` | `4d980e1916c7e21cc7764a8a9090e8102145d7a6f03a2dbfa1b43b850c1a110c` |
| `dag-metrics.txt` | `30a5860b463fb4f9ec0fff00746134649fdc21b539c98bc3c1bf5114b3d47852` |
| `dag-metrics2.txt` | `ed8aacf70ecc0b5d3bb9409f5b7a5beeb19c72b480bfe151c3917383056031dc` |
| `verdicts.txt` | `178d89deb3518d2428f469d350b328987a1b2e156f3b58509a04d2479012e0be` |
| `checks-programs-findings.txt` | `25f3f2f74db2213d2cd3fe1cb4b36f9a58bf7d08f07892b07eae81d36574c154` |
| `gate-and-cert-metrics.txt` | `a0f538c6743f0dcf7762eeb71061efe7f1e662916874405159e7a91e37dad967` |
| `uccep-model.txt` | `e9cf4e41b8f0f5d156f4ede9fdf32358b3f913ef9dc2f788fb042a93605ac422` |
| `uccep-shape.txt` | `b420b9790936040e4ecfb0c2a719d7ceb815c27d0532941f6b92248d239b9d4a` |
| `cert-ct-metrics.txt` | `604dda6fde47fd048f46ec6c56bfd16115c319c43e468925e37c9dc56b10c66e` |
| `enforcement-gates.txt` | `2f675b3e61928b99e126d5f9e813364bd31ea80dd9724281d64aa920ca76fb70` |
| `make-targets.txt` | `37f27f3b44bc86259c3df4756aaf0868a5b456dc64476f0d74d257eb19910bd8` |

## 4. Repository state before and after this programme

| Fact | Before | After |
|---|---|---|
| HEAD | `9de85ad` | `9de85ad` — unchanged |
| Anchor | `1c6e750` | `1c6e750` — unchanged, still an ancestor |
| Registered artifacts | 1,199 | 1,199 |
| `id-ledger.json` digest | `1b7434ec…` | `1b7434ec…` — unchanged |
| Registration drift | zero | zero (`register.sh --guard` exit 0) |
| Registers mutated | — | **none** — `00-MASTER/` is registration-excluded |

The commands of E-10, E-12 and E-13 write governance telemetry and re-emit their own programmes' outputs; both were verified idempotent at this baseline (no digest movement in `00-BOOK/DATA/`, no registration drift).

## 5. Sources cited across Outputs 1–16

Constitutional and governing: `00-CEP/CEP-000`…`CEP-010` · `00-CMG/CMG-000001` + `CMG-REGISTRY.json` · `STATUS-001` · `STATUS-REG-001` · `REG-AUTO-001` · `UCI-001` · `GOV-INT-001` · `MCS-000` · `UCIC-001` · `UCOS-RECON-C1`.
Programme records: `UCCEP-000000` (bindings, engine, `uccep.json`) · `UCCEP-000005` Outputs 1–13 · `UCCEP-000006` Outputs 1–10 · `UCDA-000001` (`ucda-decisions.json`, `ucda.json`) · `MCP-002` · `MCP-007`.
Machine stores: `00-BOOK/DATA/*.json` (10 files) · `intelligence/*.json` (10 files) · `00-BOOK/tools/config.py` · `ukb.py` · `register.sh` · `engine/graph/validation.py` · `Makefile` · `verify.sh` · `.gitignore`.

---

*`UCCEP-000007` Output 17. AUTHORITY = NONE (DERIVED TRUTH). Evidence only, no interpretation. `CERTIFIED-PROVISIONAL`; Tier T1 VACANT.*
