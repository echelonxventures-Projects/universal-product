# CERTIFICATION READINESS MODEL

**Artifact ID**: UCOS-CERT-READINESS-001  
**Date**: 2026-09-01  
**Authority**: PHASE E6 — CERTIFICATION READINESS MODEL  
**Scope**: MB7-MB24 state transition requirements

---

## OBJECTIVE

Define exact, measurable requirements for each state transition:
- OPEN → IMPLEMENTED
- IMPLEMENTED → VERIFIED
- VERIFIED → CERTIFIED

For each threat: MB7, MB14, MB15, MB16, MB17, MB18, MB22, MB23, MB24

**No ambiguity. No inference. Only measurable criteria.**

---

## STATE DEFINITIONS

### OPEN
- No independent validator exists
- Self-validation only (validation_owner == owner)
- Threat is active and exploitable

### IMPLEMENTED
- Code exists (validator, test, or detector)
- Code may not be tested or proven to work
- No CI enforcement

### VERIFIED
- Code proven to work through attack tests or verification runs
- Evidence exists (attack results, test output)
- Still not CI-enforced (can be bypassed)

### CERTIFIED
- Code proven to work
- CI-enforced (integrated into verify.sh or equivalent)
- Cannot be bypassed
- Evidence documented and preserved

---

## MB7: GENERATOR AUTHORITY INDEPENDENCE

### Threat Definition
A uniformly wrong generator passes all validation because validators are derived from the same generator authority.

---

### OPEN → IMPLEMENTED

**Requirements**:
1. ✓ Authority corpus identified and documented
2. ✓ Independent validator code written
3. ✓ Validator does NOT import generator
4. ✓ Validator does NOT execute generator
5. ✓ Validator reads authority corpus directly

**Evidence Required**:
- `{producer}-authority.json` file exists
- `{producer}_verify.py` file exists (or equivalent)
- Code review confirms no `import {producer}_engine` in validator
- Code review confirms no `subprocess.run(producer_engine)` in validator

**Measurement**:
```bash
# Check validator exists
test -f 00-BOOK/tools/{producer}_verify.py

# Check validator does not import generator
! grep "import.*{producer}_engine" 00-BOOK/tools/{producer}_verify.py

# Check validator reads authority
grep "{producer}-authority.json" 00-BOOK/tools/{producer}_verify.py
```

**Blocking Failures**:
- Validator imports generator → NOT IMPLEMENTED
- Validator does not read authority → NOT IMPLEMENTED
- No authority corpus documented → NOT IMPLEMENTED

---

### IMPLEMENTED → VERIFIED

**Requirements**:
1. ✓ Attack reproducers created (minimum 3 variants)
2. ✓ Attacks executed in sandbox
3. ✓ Self-validation measured (gate_exit=0 expected)
4. ✓ Independent validator measured (verifier_exit=1 expected)
5. ✓ Results documented

**Evidence Required**:
- Attack scripts exist: `{producer}_attack_{1,2,3}.sh`
- Attack results file: `{producer}-attack-results.json`
- Results show: `gate_exit=0` (self-validation passes)
- Results show: `verifier_exit=1` (independent validator catches)

**Attack Variants** (minimum):
1. **Invented Content**: Add fabricated sentence/data not in authority
2. **Permutation**: Swap two values declared in authority
3. **Truncation**: Delete final line/section of output

**Measurement**:
```bash
# Run attack 1
./attacks/{producer}_attack_invented.sh
gate_exit=$?  # Should be 0 (self-validation passes wrong output)

# Run independent validator on attack output
python3 00-BOOK/tools/{producer}_verify.py --input {attack_output}
verifier_exit=$?  # Should be 1 (catches wrong output)

# Document
echo "{\"attack\": \"invented\", \"gate_exit\": $gate_exit, \"verifier_exit\": $verifier_exit}" \
  >> {producer}-attack-results.json
```

**Blocking Failures**:
- gate_exit=1 (self-validation catches attack) → Attacks too weak, strengthen
- verifier_exit=0 (independent validator passes attack) → Validator broken, fix
- <3 attack variants → Insufficient coverage

---

### VERIFIED → CERTIFIED

**Requirements**:
1. ✓ Validator integrated into verify.sh
2. ✓ Validator stage added to UVI registry
3. ✓ verify.sh --full runs validator
4. ✓ Validator cannot be skipped or bypassed
5. ✓ CI pipeline enforces validator

**Evidence Required**:
- `verify.sh` contains stage for {producer} validator
- `00-MASTER/UVI-000001/uvi-declaration.json` lists stage
- `./verify.sh --full` output shows validator stage passed
- `.github/workflows/*.yml` invokes `./verify.sh --full`

**Measurement**:
```bash
# Check verify.sh integration
grep "{producer}_verify" verify.sh

# Check UVI registry
jq '.stage_registry[] | select(.name == "{producer}-validation")' \
  00-MASTER/UVI-000001/uvi-declaration.json

# Run full verification
./verify.sh --full 2>&1 | grep "PASS.*{producer}-validation"

# Verify CI enforcement
grep "verify.sh --full" .github/workflows/*.yml
```

**Blocking Failures**:
- Validator not in verify.sh → NOT CERTIFIED
- Validator not in UVI registry → NOT CERTIFIED
- Validator can be bypassed (--skip flag, conditional) → NOT CERTIFIED
- CI does not run validator → NOT CERTIFIED

---

## MB14: FRESH-CLONE BOOTSTRAP DEPENDENCY

### Threat Definition
A fresh clone cannot regenerate canonical artifacts because the generator depends on operational state not in the repository.

---

### OPEN → IMPLEMENTED

**Requirements**:
1. ✓ Fresh-clone test script created
2. ✓ Test clones repository to temporary directory
3. ✓ Test runs generator with no operational state
4. ✓ Test verifies regeneration succeeds

**Evidence Required**:
- `test_fresh_clone_{producer}.py` exists
- Test clones to /tmp or equivalent
- Test does not copy operational state (.env, caches, etc.)

**Measurement**:
```bash
# Check test exists
test -f platform/tests/test_fresh_clone_{producer}.py

# Check test clones fresh
grep "git clone" platform/tests/test_fresh_clone_{producer}.py
grep "/tmp" platform/tests/test_fresh_clone_{producer}.py
```

---

### IMPLEMENTED → VERIFIED

**Requirements**:
1. ✓ Test executed in isolated environment
2. ✓ Test passes (generator succeeds from tracked inputs only)
3. ✓ Test output logged

**Evidence Required**:
- Test execution log: `{producer}-fresh-clone-test.log`
- Test result: PASS
- Generator output matches expected (byte-for-byte or semantic equivalence)

**Measurement**:
```bash
# Run test
pytest platform/tests/test_fresh_clone_{producer}.py -v \
  > {producer}-fresh-clone-test.log 2>&1
result=$?

# Verify pass
test $result -eq 0
grep "PASSED" {producer}-fresh-clone-test.log
```

**Blocking Failures**:
- Test fails → Generator has hidden dependencies, fix generator
- Test passes but output wrong → Test is incomplete, strengthen test

---

### VERIFIED → CERTIFIED

**Requirements**:
1. ✓ Test integrated into CI test suite
2. ✓ Test runs in --integration and --full modes
3. ✓ CI pipeline enforces test

**Evidence Required**:
- Test in pytest test suite
- `./verify.sh --integration` runs test
- CI runs test

**Measurement**:
```bash
# Check test in suite
pytest --collect-only | grep "test_fresh_clone_{producer}"

# Run integration mode
./verify.sh --integration 2>&1 | grep "test_fresh_clone_{producer}.*PASSED"
```

---

## MB15: TEMPLATE EXPLOSION RISK

### Threat Definition
Each new producer instance requires a new template, creating O(n²) maintenance burden.

---

### OPEN → IMPLEMENTED

**Requirements**:
1. ✓ Normalisation algorithm implemented
2. ✓ MIN_SLOT threshold defined (≥6 recommended)
3. ✓ Template manifest created
4. ✓ Manifest contains normalized templates

**Evidence Required**:
- `{producer}_verify.py` contains `normalise()` function
- `{producer}-template-manifest.json` exists
- Manifest has `allowed_lines` or `allowed_cells`

**Measurement**:
```bash
# Check normalise function
grep "def normalise" 00-BOOK/tools/{producer}_verify.py

# Check manifest
test -f 00-BOOK/DATA/{producer}-template-manifest.json
jq '.allowed_lines | length' 00-BOOK/DATA/{producer}-template-manifest.json
```

---

### IMPLEMENTED → VERIFIED

**Requirements**:
1. ✓ Template coverage measured (templates cover all outputs)
2. ✓ Single template proven to cover multiple instances
3. ✓ Template count is O(1) per pattern type

**Evidence Required**:
- Template manifest documents coverage
- Multiple artifacts map to same template (normalised)
- Template count < artifact count (compression achieved)

**Measurement**:
```bash
# Count templates
template_count=$(jq '.allowed_lines | length' {producer}-template-manifest.json)

# Count artifacts
artifact_count=$(jq '[.entries[] | select(.owner == "{producer}")] | length' \
  00-BOOK/DATA/generated-artifact-registry.json)

# Verify compression
test $template_count -lt $artifact_count
```

**Blocking Failures**:
- Template count ≥ artifact count → No compression, normalisation failed
- Templates do not cover outputs → Incomplete, strengthen normalisation

---

### VERIFIED → CERTIFIED

**Requirements**:
1. ✓ Template verification integrated into validator
2. ✓ Validator rejects lines not matching templates
3. ✓ CI enforces template verification

**Evidence Required**:
- Validator checks every output line against templates
- Validator exits 1 on unmatched lines
- CI runs validator

**Measurement**: Same as MB7 VERIFIED → CERTIFIED (validator CI integration)

---

## MB16: SHORT-WORD FALSE MATCH

### Threat Definition
Common words ("the", "is") trigger false template matches, accepting unprovenanced text.

---

### OPEN → IMPLEMENTED

**Requirements**:
1. ✓ MIN_SLOT constant defined in normalise()
2. ✓ MIN_SLOT ≥ 6
3. ✓ Short strings passed through as literals

**Evidence Required**:
- `MIN_SLOT = 6` (or higher) in code
- Normalisation logic skips strings < MIN_SLOT

**Measurement**:
```python
# Check MIN_SLOT in validator
grep "MIN_SLOT = [6-9]" 00-BOOK/tools/{producer}_verify.py
```

---

### IMPLEMENTED → VERIFIED

**Requirements**:
1. ✓ Attack test: Insert short common word
2. ✓ Validator rejects insertion
3. ✓ Result documented

**Evidence Required**:
- Attack script inserts "the", "is", "and" into output
- Validator exits 1 (rejects)
- Attack results logged

**Measurement**:
```bash
# Create attack output with short word insertion
echo "This is normal line." > /tmp/attack.txt
echo "the" >> /tmp/attack.txt  # Short word, not in authority
echo "Another normal line." >> /tmp/attack.txt

# Run validator
python3 00-BOOK/tools/{producer}_verify.py --input /tmp/attack.txt
result=$?

# Should fail (exit 1)
test $result -eq 1
```

---

### VERIFIED → CERTIFIED

**Requirements**: Same as MB7 (validator CI integration)

---

## MB17: AUTHORITY GOVERNANCE GAP

### Threat Definition
Generator authority files are mutable without review, allowing silent corruption of all derived outputs.

---

### OPEN → IMPLEMENTED

**Requirements**:
1. ✓ Authority files identified
2. ✓ CODEOWNERS entry added for authority files
3. ✓ Constitutional superior documented (if applicable)

**Evidence Required**:
- `{producer}-authority.json` declares authority sources
- `.github/CODEOWNERS` or `CODEOWNERS` file has entry for authority paths
- Authority manifest links to constitutional superior

**Measurement**:
```bash
# Check authority declaration
test -f 00-BOOK/DATA/{producer}-authority.json

# Check CODEOWNERS
grep "{producer}-authority" .github/CODEOWNERS
```

---

### IMPLEMENTED → VERIFIED

**Requirements**:
1. ✓ Test commit to authority file
2. ✓ Verify review required (PR blocked without approval)
3. ✓ Governance enforced

**Evidence Required**:
- Branch protection rules require review for authority changes
- Test PR shows review requirement

**Measurement**:
```bash
# Create test branch
git checkout -b test-authority-governance
echo "# test change" >> 00-BOOK/DATA/{producer}-authority.json
git commit -am "Test: authority change"
git push origin test-authority-governance

# Create PR (requires GitHub CLI or API)
gh pr create --title "Test: Authority Governance" --body "Testing review requirement"

# Check PR status
gh pr view --json reviewDecision | jq '.reviewDecision'
# Should be null or "REVIEW_REQUIRED", not "APPROVED"
```

---

### VERIFIED → CERTIFIED

**Requirements**:
1. ✓ Governance documented
2. ✓ Authority changes require constitutional review
3. ✓ Process enforced in repository settings

**Evidence Required**:
- Branch protection rules saved
- CODEOWNERS file committed
- Governance policy documented

**Measurement**: Governance remains enforced (continuous requirement, not one-time)

---

## MB18: GENERATED_DETERMINISTIC INPUT CIRCULARITY

### Threat Definition
Deterministic artifacts depend on GENERATED_DETERMINISTIC inputs whose bootstrap paths form cycles or are incomplete.

---

### OPEN → IMPLEMENTED

**Requirements**:
1. ✓ Bootstrap graph builder implemented
2. ✓ Cycle detector implemented
3. ✓ Completeness verifier implemented

**Evidence Required**:
- `bootstrap_graph.py` exists
- Graph builder enumerates all GENERATED_DETERMINISTIC dependencies
- Cycle detection algorithm implemented (DFS or Tarjan)

**Measurement**:
```bash
# Check graph builder exists
test -f 00-BOOK/tools/bootstrap_graph.py

# Check has cycle detection
grep "def detect_cycles" 00-BOOK/tools/bootstrap_graph.py
```

---

### IMPLEMENTED → VERIFIED

**Requirements**:
1. ✓ Graph constructed for all 368 artifacts
2. ✓ Cycle detection run
3. ✓ No cycles found OR cycles documented for remediation
4. ✓ Bootstrap path completeness verified

**Evidence Required**:
- `bootstrap-graph.json` contains full dependency graph
- `bootstrap-cycle-report.json` shows cycle detection results
- Report shows: 0 cycles (or lists cycles to fix)

**Measurement**:
```bash
# Build graph
python3 00-BOOK/tools/bootstrap_graph.py \
  --input 00-BOOK/DATA/generated-artifact-registry.json \
  --output bootstrap-graph.json

# Detect cycles
python3 00-BOOK/tools/bootstrap_graph.py \
  --detect-cycles \
  --input bootstrap-graph.json \
  --output bootstrap-cycle-report.json

# Check result
jq '.cycles | length' bootstrap-cycle-report.json
# Should be 0
```

**Blocking Failures**:
- Cycles detected → Remediate generator dependencies, re-run
- Incomplete bootstrap paths → Document paths, re-run

---

### VERIFIED → CERTIFIED

**Requirements**:
1. ✓ Bootstrap graph verification integrated into CI
2. ✓ CI fails if cycles detected
3. ✓ CI fails if incomplete bootstrap paths

**Evidence Required**:
- verify.sh stage runs bootstrap graph verification
- Stage exits 1 on cycles or incomplete paths

**Measurement**:
```bash
# Check verify.sh integration
grep "bootstrap_graph" verify.sh

# Run verification
./verify.sh --full 2>&1 | grep "PASS.*bootstrap-integrity"
```

---

## MB22: REGENERATION_COMMAND UNVERIFIED

### Threat Definition
Regeneration commands declared but not verified to actually produce the declared output.

---

### OPEN → IMPLEMENTED

**Requirements**:
1. ✓ Regeneration test script created
2. ✓ Script runs declared regeneration_command
3. ✓ Script compares output to current artifact

**Evidence Required**:
- `test_regeneration_{producer}.py` exists
- Test extracts regeneration_command from registry
- Test diffs output against current

**Measurement**:
```bash
# Check test exists
test -f platform/tests/test_regeneration_{producer}.py

# Check test uses regeneration_command
grep "regeneration_command" platform/tests/test_regeneration_{producer}.py
```

---

### IMPLEMENTED → VERIFIED

**Requirements**:
1. ✓ Test executed
2. ✓ Regeneration succeeds
3. ✓ Output matches current (byte-for-byte or semantic)
4. ✓ Results logged

**Evidence Required**:
- Test execution log: `{producer}-regeneration-test.log`
- Test result: PASS
- Output diff: empty or acceptable variance

**Measurement**:
```bash
# Run test
pytest platform/tests/test_regeneration_{producer}.py -v \
  > {producer}-regeneration-test.log 2>&1
result=$?

# Verify pass
test $result -eq 0
```

**Blocking Failures**:
- Command fails → Update command or fix generator
- Output differs → Update command or accept new output as canonical

---

### VERIFIED → CERTIFIED

**Requirements**: Same as MB14 (CI test integration)

---

## MB23: DETERMINISTIC CLAIM WITHOUT EVIDENCE

### Threat Definition
Artifacts claim deterministic:true but no test verifies byte-for-byte reproducibility.

---

### OPEN → IMPLEMENTED

**Requirements**:
1. ✓ Determinism test script created
2. ✓ Script runs generator twice
3. ✓ Script compares outputs byte-for-byte

**Evidence Required**:
- `test_determinism_{producer}.py` exists
- Test runs generator multiple times
- Test compares with `diff` or hash comparison

**Measurement**:
```bash
# Check test exists
test -f platform/tests/test_determinism_{producer}.py

# Check test runs twice
grep -c "run_generator" platform/tests/test_determinism_{producer}.py | test $(cat) -ge 2
```

---

### IMPLEMENTED → VERIFIED

**Requirements**:
1. ✓ Test executed
2. ✓ Two runs produce identical bytes
3. ✓ Results logged

**Evidence Required**:
- Test execution log: `{producer}-determinism-test.log`
- Test result: PASS (outputs identical)

**Measurement**:
```bash
# Run test
pytest platform/tests/test_determinism_{producer}.py -v \
  > {producer}-determinism-test.log 2>&1
result=$?

# Verify pass
test $result -eq 0
grep "outputs identical" {producer}-determinism-test.log
```

**Blocking Failures**:
- Outputs differ → Fix non-determinism (timestamps, ordering, randomness) OR downgrade deterministic:true to false

---

### VERIFIED → CERTIFIED

**Requirements**: Same as MB14 (CI test integration)

---

## MB24: CONSTITUTIONAL_SUPERIOR UNENFORCED

### Threat Definition
Artifacts declare constitutional_superior but no validator verifies alignment with superior's authority.

---

### OPEN → IMPLEMENTED

**Requirements**:
1. ✓ Constitutional superior identified
2. ✓ Alignment verifier implemented
3. ✓ Verifier checks artifact claims against superior

**Evidence Required**:
- `{producer}-authority.json` declares `constitutional_superior`
- `{producer}_constitutional_verify.py` exists
- Verifier reads superior authority file
- Verifier validates alignment

**Measurement**:
```bash
# Check superior declared
jq '.constitutional_superior' 00-BOOK/DATA/{producer}-authority.json

# Check verifier exists
test -f 00-BOOK/tools/{producer}_constitutional_verify.py

# Check verifier reads superior
grep "constitutional_superior" 00-BOOK/tools/{producer}_constitutional_verify.py
```

---

### IMPLEMENTED → VERIFIED

**Requirements**:
1. ✓ Attack test: Modify artifact to misalign with superior
2. ✓ Verifier detects misalignment
3. ✓ Results logged

**Evidence Required**:
- Attack script creates misaligned output
- Verifier exits 1 (rejects misalignment)
- Attack results logged

**Measurement**:
```bash
# Create misaligned output (modify constitutional claim)
sed 's/UCKP-ART-01/FAKE-ART-01/' {artifact} > /tmp/misaligned.txt

# Run constitutional verifier
python3 00-BOOK/tools/{producer}_constitutional_verify.py \
  --input /tmp/misaligned.txt
result=$?

# Should fail
test $result -eq 1
```

---

### VERIFIED → CERTIFIED

**Requirements**: Same as MB7 (validator CI integration)

---

## CROSS-THREAT CERTIFICATION MATRIX

| Threat | IMPLEMENTED Requirements | VERIFIED Requirements | CERTIFIED Requirements |
|--------|-------------------------|----------------------|------------------------|
| MB7 | Authority corpus + independent validator code | 3 attacks, gate_exit=0, verifier_exit=1 | CI integration, UVI registry, enforced |
| MB14 | Fresh-clone test script | Test passes in isolation | CI test integration |
| MB15 | Normalisation + template manifest | Template coverage verified, compression achieved | Validator CI integration |
| MB16 | MIN_SLOT ≥ 6 in normalise() | Short-word attack rejected | Validator CI integration |
| MB17 | CODEOWNERS + authority manifest | Review requirement tested | Governance enforced |
| MB18 | Bootstrap graph + cycle detector | Graph complete, 0 cycles | CI graph verification |
| MB22 | Regeneration test script | Command verified, output matches | CI test integration |
| MB23 | Determinism test script | Two runs identical | CI test integration |
| MB24 | Constitutional verifier | Misalignment attack rejected | Validator CI integration |

---

## UNIVERSAL CERTIFICATION CRITERIA

**All threats must meet these requirements to be CERTIFIED**:

### 1. Evidence Preservation
- All attack results, test logs, and verification outputs stored
- Evidence linked in generated-artifact-registry.json
- Evidence survives repository clones (tracked or reproducible)

### 2. CI Non-Bypassability
- No `--skip-{validator}` flags
- No conditional execution based on branch/environment
- Failure blocks merge

### 3. Documentation
- Threat closure documented in registry
- independent_validation field populated
- Closure certificate generated

### 4. Reproducibility
- Any operator can re-run verification
- Verification produces identical results
- No hidden dependencies

---

## CERTIFICATION READINESS CHECKLIST

### Per Producer, Per Threat

```
Producer: {producer_id}
Threat: MB{X}

[ ] IMPLEMENTED
    [ ] Code exists
    [ ] Code reviewed
    [ ] No import/execution of generator (if MB7)
    [ ] Reads authority directly (if MB7)

[ ] VERIFIED
    [ ] Attacks executed (if applicable)
    [ ] Tests passed
    [ ] Results logged
    [ ] Evidence stored

[ ] CERTIFIED
    [ ] CI integration complete
    [ ] UVI registry updated
    [ ] verify.sh --full includes stage
    [ ] Cannot be bypassed
    [ ] Documentation updated
    [ ] Closure certificate generated

Final Status: [ ] OPEN [ ] IMPLEMENTED [ ] VERIFIED [ ] CERTIFIED
```

---

## CERTIFICATION AUTHORITY

**Certification Decisions**: Operator (human) or CI (automated, for clear pass/fail)

**Operator Certification**: Required for
- MB17 (governance review requirement test)
- MB24 (constitutional alignment interpretation)
- First-time validator architecture approval

**Automated Certification**: Sufficient for
- MB7 (attack results are pass/fail)
- MB14, MB22, MB23 (tests are pass/fail)
- MB15, MB16 (validation is deterministic)
- MB18 (cycle detection is algorithmic)

---

## CERTIFICATION

**Model Author**: Kiro (Claude Opus 5)  
**Model Date**: 2026-09-01  
**Method**: State transition decomposition per threat

**Key Principle**: No ambiguity. Every requirement is measurable. Every state transition has evidence.

**Verification**: All requirements map to concrete commands or code checks. No subjective criteria.

---

**Status**: PHASE E6 COMPLETE ✓  
**Next Phase**: E7 — EXECUTION BACKLOG
