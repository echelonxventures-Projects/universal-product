#!/usr/bin/env python3
"""selftest — prove that the CI guards fail on known defects (ADR-036).

Each case copies the repository to a temporary directory, injects one defect, runs one guard and
expects a non-zero exit. A guard that passes on a broken repository is itself a CI failure.
Usage: python3 tools/selftest.py
"""
import glob, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
SKIP = shutil.ignore_patterns('.git', 'node_modules', '.venv', '.tools', 'generated', '__pycache__', '*.pdf')

def append(path, text):
    def f(r):
        with open(os.path.join(r, path), 'a', encoding='utf-8') as h:
            h.write(text)
    return f

def replace(path, old, new):
    def f(r):
        p = os.path.join(r, path)
        t = open(p, encoding='utf-8').read()
        assert old in t, f'selftest anchor missing in {path}: {old!r}'
        open(p, 'w', encoding='utf-8').write(t.replace(old, new, 1))
    return f

def touch(path):
    def f(r):
        shutil.copy(os.path.join(r, 'README.md'), os.path.join(r, path))
    return f

CHECK = [PY, 'tools/ucos_check.py']
VALIDATE = [PY, 'tools/validate_contracts.py', '--quick']
CASES = [
    ('undefined gate id in a document', append('docs/adr/README.md', '\nSee gate `ARCH-NOPE-99`.\n'), CHECK, 'ARCH-NOPE-99'),
    ('hand edit of a generated object schema',
     replace('spec/object-types/ucos.order.Order.schema.json', '"title": "ucos.order.Order"', '"title": "edited"'), CHECK, 'registry out of date'),
    ('event provided by two capabilities (Law L4)',
     replace('spec/capabilities/packs/ledger.core.yaml', '    - ledger.journal.posted', '    - ledger.journal.posted\n    - order.order.placed'), CHECK, 'ownership collision'),
    ('capability requires a later phase',
     replace('spec/capabilities/packs/order.core.yaml', '  - capability: workflow.core', '  - capability: ledger.core\n    version: \'>=1 <2\'\n  - capability: workflow.core'), CHECK, 'which is later'),
    ('step outside the vocabulary',
     replace('spec/acceptance/platform/idempotency.feature', 'Then both responses are identical', 'Then everything looks fine'), VALIDATE, 'step not in vocabulary'),
    ('unknown error code in a scenario',
     replace('spec/acceptance/d2c-in-ae/return-refund.feature', 'ORD_RETURN_WINDOW_CLOSED', 'ORD_MADE_UP_CODE'), VALIDATE, 'ORD_MADE_UP_CODE'),
    ('alert links to a missing runbook section',
     replace('docs/runbooks/payment.md', '## Latency breach', '## Slow things'), VALIDATE, 'no section #latency-breach'),
    ('sync-conflict duplicate file', touch('spec/README 2.md'), VALIDATE, 'sync-conflict duplicate'),
    ('broken proto', append('spec/api/proto/ucos/kernel/v1/common.proto', '\nmessage Broken { string x = 1 }\n'), VALIDATE, 'protoc failed'),
    ('Cedar policy does not parse',
     replace('spec/policies/platform-baseline.cedar', 'forbid (principal is Agent', 'forbid (principal is ActionGroup::"x"'), VALIDATE, 'Cedar does not parse'),
    ('policy test expects the wrong decision',
     replace('spec/policies/tests/platform-baseline.yaml', 'resource: \'Order::"o-t2"\', expect: Deny', 'resource: \'Order::"o-t2"\', expect: Allow'), VALIDATE, 'expected Allow, got Deny'),
    ('undeclared predicate in composition rules',
     append('spec/rules/core/closure.dl', '\ngap("X", c, "-") :- required(c), mystery(c).\n'), VALIDATE, 'mystery is used but not declared'),
    ('decision table test fails',
     replace('spec/decisions/risk.checkout-thresholds.yaml', "- ['*', '>=90', decline]", "- ['*', '>=90', allow]"), VALIDATE, 'expected [\'decline\']'),
    ('composition rules drift from the checker',
     replace('spec/rules/core/closure.dl', 'required(abs) :- required(a), adapter_kind(a), implements(a, abs).', ''), [PY, 'tools/datalog.py', 'oracle'], 'differs between closure.dl and the checker'),
    ('stale generated contract',
     replace('spec/api/asyncapi/ucos-events.yaml', "asyncapi: 3.0.0", "asyncapi: 3.0.0\n# edited"), [PY, 'tools/gen_contracts.py', '--check'], 'out of date'),
    ('stale generated manifest',
     replace('spec/capabilities/packs/order.core.yaml', 'maturity: beta', 'maturity: certified'), [PY, 'tools/gen_manifests.py', '--check'], 'out of date'),
]

def main():
    failures = 0
    for name, mutate, cmd, expect in CASES:
        with tempfile.TemporaryDirectory() as td:
            repo = os.path.join(td, 'repo')
            shutil.copytree(ROOT, repo, ignore=SKIP)
            mutate(repo)
            r = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
            ok = r.returncode != 0 and expect in (r.stdout + r.stderr)
            print(f'  {"PASS" if ok else "FAIL"}  {name}')
            if not ok:
                failures += 1
                print(f'        expected a failure mentioning {expect!r}; output tail:\n        ' + '\n        '.join((r.stdout + r.stderr).strip().splitlines()[-5:]))
    print(f'selftest: {len(CASES) - failures}/{len(CASES)} guards fail as expected')
    sys.exit(1 if failures else 0)

if __name__ == '__main__':
    main()
