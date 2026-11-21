# Output 10 — Validation Evidence Register

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000005` |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| PRINCIPLE | Every claim in Outputs 1–9 and 11 resolves to a file in this register. Nothing rests on narration. |

---

## 1. Evidence artifacts (sha256)

### 1.1 Baseline — `00-MASTER/UCCEP-000005/evidence/baseline/`

| Artifact | Records | sha256 |
|---|---|---|
| `head.txt` | HEAD + branch at establishment | `d66ae791fd9bec80767fe128402e6654c7be407d31a7d1d20ae5740feadfe135` |
| `worktree.txt` | 120 dirty entries at establishment | `0f644de5ba0e6353cdfb6f54f3b25f8b8db1fa5a7a37eb7f6c10607740219354` |
| `worktree-count.txt` | dirty-entry count | `97b912eb4a61df5f806ca6239dde3e1a4f51ad20aced1642cbb83dc510a5fa6b` |
| `pre-hashes.txt` | pre-mutation content hashes | `d99a5040bee121227ea6aee29aeb8a8cf129278390eb74b278c7700eacdc168c` |
| `graph-validate.json` | fail-open gate output (cycle + `is_valid true` + exit 0) | `3c4e7907132802a1e19b93080144e72d69dd50e9ee0fb2c1c441d0ddd624e29d` |
| `dependency-derivation.json` | baseline SCC / ordering / critical path / parallel groups | `bbc358a943cd76ae7cdd88e9e80ce01a2fab72bacc1b5dcef88ef43b3c2e9513` |
| `certification-baseline.json` | NOT-CERTIFIED, `G-08` FAIL, `CK-GRAPH` assertions, seal | `557f5267263da88c69006af3f0fe72dcbbb352bd5b62e018dc0a443175e14005` |

### 1.2 Post-remediation — `00-MASTER/UCCEP-000005/evidence/post/`

| Artifact | Records | sha256 |
|---|---|---|
| `T-1-config-py.diff` | the T-1 mutation, verbatim | `0af3de8b96beea1d73fd6be812728dfa05021b17251479de99175e9e9ec3ceb8` |
| `T-1-eng-chain-edges.json` | every ENG-internal edge + ENG artifact identity after T-1 | `101b52a6d5407ae578e0ce88c40520b67f4f3ee62310bc96f0e739b410fde131` |
| `post-t1-hashes.txt` | content hashes immediately after T-1 + regeneration | `b9e0d71619e37bf8e3cca9a5699ab79558f599ffc6355f35290fcacb7ce735e4` |
| `register-transaction.log` | REG-AUTO-001 10-phase transaction, TRANSACTION COMPLETE | `fafd7cf153f4225dd66a0d8a2b8d6949174cdb18a85c83a75421296d5e5329d1` |
| `T-2-validation-gate.diff` | the T-2 mutation + test replacement, verbatim | `ad59db4c76b87a005628d97d0486265448e7f4516e11511e132875bacc624bf7` |
| `T-2-gate-paths.txt` | positive path (exit 0) · negative path (exit 1) · determinism digests | `3c3e400fb33f95eb883bb69a7955e520eab320cdc9abbec1febc9b72071fd671` |
| `T-2-ec1-verify.log` | EC-1 `verify.sh` all stages PASS, coverage 97% | `bfd0928e3ed84fab41189ee6e51a2dafa1d7ca0cef5ea7af92bcdc06f48e355b` |
| `dependency-derivation.json` | post SCC / ordering / critical path / parallel groups / consistency | `423de99f82fa0c97eee2619fb06ed5d25b29417c94c88b02eaced02ff0a175ed` |
| `T-3-graph-evidence.json` | `engine.graph.cli evidence` — `operational: true` | `26117be94b91ba69809ff30e48050aaff7542d72203bb6ac4223b3630e63670a` |
| `T-3-rie-determinism.json` | `intelligence.rie verify` — deterministic, 10 outputs | `0b9d76645291d263ff7584fc665a9e12bd1104db1b63e9b29756b1872393eaba` |
| `T-3-determinism-build.log` | `engine.determinism.reproduce` double-build byte-identical | `5495ec93513fac8e7c66b9d28e23a70a0963c6f246d6ff8984c8d638942c9b64` |
| `T-3-regeneration-determinism.txt` | second `ukb build` byte-identical | `2468ddc60fc64fb50d648015c0f5a8b956d1cb3ec2076e3ed3a91bb00f3df4ee` |
| `T-3-uccep-gate-standard.log` | standard-tier gate CERTIFIED-PROVISIONAL, exit 0 | `b5c814235b056c00f849e62a92115424211e93d99178cec601d2e475d7eb9993` |
| `T-3-uccep-certification.json` | standard-tier gate register + `CK-GRAPH` assertions | `3119b7ecf799ca439fcaddbd527d43997fd92fe8f3c8cb1a4aa9bf4bf23b0c82` |
| `T-3-uccep-gate-full.log` | full-tier gate 12/13, blocking `CK-REG-DRIFT` | `5c1cf975ba259023fdc0a91ca8b42e69e718537559b7be945f33b6e55e8362e0` |
| `T-3-uccep-full-tier.json` | full-tier gate + check register | `06a44a6aed9d5d88359bdbc984bbb23459b79b6e25ff5ec2ef1d130d1b0bab28` |
| `T-3-uccep-gate-standard-final.log` | register returned to canonical `standard` tier | `b5c814235b056c00f849e62a92115424211e93d99178cec601d2e475d7eb9993` |
| `post-hashes.txt` | final content hashes of every mutated file | `99e34e3cdb88badd24132524070f9c9f9f5b0cd3f7b94083d050781a575f5d3b` |
| `worktree.txt` | 127 dirty entries after remediation | `d259d8e8ab12ae6d1828a89ce7afaee925f8231bd04b0a6de5c31dde2d6395cc` |

The two standard-tier logs share a digest, which is itself the evidence that the
aggregate gate is deterministic: the same tier over the same repository produced a
byte-identical verdict before and after the full-tier run.

### 1.3 Final verification sweep — `00-MASTER/UCCEP-000005/evidence/final-verification/`

Independent re-execution of every gate after all remediation and reporting work was
complete. Adjudicated in `13-FINAL-VERIFICATION-AND-COMPLETION-REPORT.md`.

| Artifact | Records | sha256 |
|---|---|---|
| `exit-codes.txt` | the eight gate exit codes of the sweep | `d5feca297c439fd8e36e6acd60112f231ca7d7e9f98e8ee4d39e3165c7c4a42b` |
| `verify.log` | EC-1 `verify.sh` — all stages PASS, exit 0 | `d7171ad75271eebb2137104e956f215e50299a4154b12a53edec00a645625cd9` |
| `graph-validate.json` | dependency gate — `dependency_cycle []`, exit 0 | `00ca33637606a4e8c5d194a38f944e25dbd5e2e8be063a73a70304427bd34897` |
| `ukb-enforce.log` | 1199/1199 registered, 0 unregistered/unclassified/invalid | `c39c5c9544aa188f2af5b7a88efd8edd63bf403b95e1ae44fdbab294b65050e3` |
| `ukb-validate.log` | 1199 artifacts, page ledger intact, referential integrity OK | `60e2b6a90819610c6aad1c9ce8f153d81ba60d56af935aaaa65da204f8cf370c` |
| `rie-verify.json` | `deterministic: true`, `mismatches: []`, 10 outputs | `8ffeb2db75451918da75d099d2c50c2effec7de9eab0694c60188ffd3f8322f3` |
| `determinism.log` | `double_build byte_identical=True` | `5fa30833e0cdd8253926164e47d6a64e5a8e7a38a07088eab4c9d2367c936a56` |
| `uccep-standard.log` | CERTIFIED-PROVISIONAL, exit 0, `G-08` PASS | `b5c814235b056c00f849e62a92115424211e93d99178cec601d2e475d7eb9993` |
| `uccep-full.log` | 12/13 gates, blocking `CK-REG-DRIFT` only | `5c1cf975ba259023fdc0a91ca8b42e69e718537559b7be945f33b6e55e8362e0` |

`uccep-standard.log` and `uccep-full.log` hash to exactly the digests recorded in §1.2
(`T-3-uccep-gate-standard.log`, `T-3-uccep-gate-full.log`), and `graph-validate.json`
hashes to the positive-path digest recorded in `T-2-gate-paths.txt`. **Every constitutional
verdict in this programme reproduces byte-identically on independent re-execution.**

## 2. Executed commands, in order

| # | Command | Owner | Exit | Records |
|---|---|---|---|---|
| 1 | `git rev-parse HEAD` / `git status --porcelain` | git | 0 | baseline HEAD + tree |
| 2 | `python3 -m engine.graph.cli validate` | `engine/graph` | 0 | fail-open baseline |
| 3 | `python3 00-MASTER/UCCEP-000005/derive.py --stage baseline` | UCCEP-000005 | 0 | baseline derivation |
| 4 | *T-1 edit* `00-BOOK/tools/config.py` | UCCEP-000005 | — | data correction |
| 5 | `00-BOOK/tools/register.sh` | REG-AUTO-001 | 0 | full regeneration, 10/10 phases |
| 6 | `python3 -m engine.graph.cli validate` | `engine/graph` | 0 | `dependency_cycle = []` |
| 7 | *T-2 edit* `engine/graph/validation.py` + its test | UCCEP-000005 | — | gate correction |
| 8 | `.ec1-venv/bin/python -m pytest engine/tests/graph -q` | pytest | 0 | 85 passed |
| 9 | `./verify.sh` | EC-1 | 0 | lint + tests + coverage 97% + enforce |
| 10 | `engine.graph.cli validate` ×2 (positive) | `engine/graph` | 0 | exit 0, determinism |
| 11 | `engine.graph.cli --data-dir <temp> validate` ×4 (negative) | `engine/graph` | 1 | **fail-closed**, determinism |
| 12 | `./verify.sh` (repeat) | EC-1 | 0 | reproducibility |
| 13 | `python3 00-MASTER/UCCEP-000005/derive.py --stage post` ×3 | UCCEP-000005 | 0 | identical digests |
| 14 | `python3 -m intelligence.rie verify` | `intelligence/rie` | 0 | deterministic, 10 outputs |
| 15 | `python3 -m engine.graph.cli evidence` | `engine/graph` | 0 | `operational: true` |
| 16 | `python3 -m engine.determinism.reproduce` | `engine/determinism` | 0 | double-build byte-identical |
| 17 | `python3 00-BOOK/tools/ukb.py build` (second) | REG-AUTO-001 | 0 | byte-identical registers |
| 18 | `uccep_engine.py --tier standard --gate` | UCCEP-000000 | **0** | CERTIFIED-PROVISIONAL, `G-08` PASS |
| 19 | `uccep_engine.py --tier full --gate` | UCCEP-000000 | 1 | 12/13, blocking `CK-REG-DRIFT` |
| 20 | `uccep_engine.py --tier standard --gate` | UCCEP-000000 | **0** | register returned to canonical tier |
| 21 | `python3 00-MASTER/UCCEP-000005/emit_views.py` | UCCEP-000005 | 0 | Outputs 7, 8, 9 rendered |

## 3. Claim → evidence traceability

| Claim | Evidence |
|---|---|
| The cycle existed and the gate was fail-open | `baseline/graph-validate.json` · `baseline/certification-baseline.json` |
| The root cause was `CHAINS["ENG"]` ordering, not the corpus | `baseline/dependency-derivation.json` (`eng_depends_on_edges`) · `07-ENGINEERING/…ROADMAP-RECONCILIATION-DETERMINATION.md` Output 11 |
| T-1 applied exactly the constitutional ordering | `post/T-1-config-py.diff` · `post/T-1-eng-chain-edges.json` |
| No identifier was allocated, renumbered or released | `id-ledger.json` digest identical in `baseline/pre-hashes.txt` and `post/post-hashes.txt` |
| Repository Truth was regenerated by its own owner | `post/register-transaction.log` |
| The cycle is gone | `post/dependency-derivation.json` (`scc_gt1_count: 0`, `acyclic: true`) |
| The gate now fails closed | `post/T-2-gate-paths.txt` (negative path exit 1) |
| The gate still passes on clean truth | `post/T-2-gate-paths.txt` (positive path exit 0) |
| The gate is deterministic | identical digests, 3 runs negative / 2 runs positive |
| EC-1 validation passed | `post/T-2-ec1-verify.log` |
| Ordering, critical path and parallel groups are derivable | `post/dependency-derivation.json` |
| Re-derivation is deterministic | `post/T-3-rie-determinism.json` · `post/T-3-regeneration-determinism.txt` · `post/T-3-determinism-build.log` |
| `G-08` PASS | `post/T-3-uccep-certification.json` · `post/T-3-uccep-full-tier.json` |
| Repository integrity preserved | `register-transaction.log` (`ukbx certify` 10/10) |
| Blast radius was 4 portal projections | `baseline/worktree.txt` vs `post/worktree.txt` |
| `CK-REG-DRIFT` pre-dates this programme | `baseline/worktree.txt` (120 entries) · `UCCEP-F-007` evidence in UCCEP-000000 |

## 4. Reproduction

```bash
python3 00-MASTER/UCCEP-000005/derive.py --stage post     # re-derive the dependency views
python3 00-MASTER/UCCEP-000005/emit_views.py              # re-render Outputs 7, 8, 9
python3 -m engine.graph.cli validate                       # the dependency gate (exit 0)
./verify.sh                                                # EC-1
make uccep-gate                                            # aggregate constitutional gate
```

---

**EVIDENCE REGISTER COMPLETE · 35 ARTIFACTS · 21 COMMANDS + 8-GATE FINAL SWEEP · EVERY CLAIM TRACEABLE**
