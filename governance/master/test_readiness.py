"""Fixtures for readiness.py: a synthetic Master and a synthetic code tree in throwaway directories; nothing else is read.
A fully evidenced candidate must compute GO; each kind of missing evidence must compute NO-GO for the right reason.
Usage: python3 -I -B test_readiness.py"""
import json, os, shutil, sys, tempfile

sys.dont_write_bytecode = True  # a check never changes the Master directory (no __pycache__)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import readiness as R

SHA = 'a' * 40
GATES = '## Decision: GO\n\n## Release gates\n\n| # | Gate | Status | Owner |\n|---|---|---|---|\n| 1 | CI | PASS | ops |\n| 2 | Backups | PASS (verified) | ops |\n\n## After\n'
CODE = {'REG.md': GATES, 'package.json': json.dumps({'scripts': {'test': 'node t/a.js'}}), 'ci.yml': 'run: npm test\n',
        't/a.js': 'require("../src/x.js");\n', 'src/x.js': 'module.exports = (S) => S.look.title;\n',
        'conf/d.json': json.dumps({'look': {'title': 'Acmeco Platform'}}), 'owners.json': json.dumps({'modules': [{'path': 'src/x.js'}]})}
DECISIONS = '%C.1 | ID=id | Outcome=o | Effect=e | Authorizes=a\n\n@LXM-DEC-000001 | adopted | C.1\no: synthetic\ne: x\na: None\n'
TRACE = '# basis-default: fixture\n@LXM-REQ-000001\nimpl: src/x.js\ntest: t/a.js\n'
CFG_CONF = {'declarations': [{'id': 'd', 'file': 'conf/d.json'}], 'code': {'roots': ['src'], 'exclude': [], 'extensions': ['.js']},
            'distinct': {'min_length': 5, 'skip_single_lowercase_word': True}, 'generic_consumers': []}
CFG_CODE = {'commands': {'package': 'package.json', 'ci_workflows': ['ci.yml'], 'script_call': 'npm (?:run\\s+([\\w:.-]+)|test\\b)',
                         'file_call': 'node\\s+([\\w./-]+\\.js)', 'not_gates': {}},
            'tests': {'roots': ['t'], 'extensions': ['.js']}, 'modules': {'roots': ['src'], 'extensions': ['.js'], 'loaders': ['require\\(']},
            'ownership': {'registry': 'owners.json', 'list': 'modules', 'path_field': 'path'}, 'duplicates': {'min_lines': 3, 'min_chars': 60}}
TESTS = {'sha': SHA, 'runtime': 'node 22', 'command': 'npm test', 'exit': 0, 'passed': 10, 'failed': 0, 'failures': [], 'crashes': [], 'tree_clean_after': True}
results = []


def config():
    c = json.load(open(os.path.join(HERE, 'readiness.json'), encoding='utf-8'))
    c['register'].update(file='REG.md', expected_gates=2)
    c['adapters'].pop('tooling', None)  # the synthetic Master has no tooling of its own; tooling_literals.py has its ratchet in CI
    return c


def world(code=None, decisions=DECISIONS, trace=TRACE, runs=(1, 2), sha=SHA, tests=None):
    m, d = tempfile.mkdtemp(prefix='rdfx-master-'), tempfile.mkdtemp(prefix='rdfx-code-')
    for f in ('build.py', 'config_adapter.py', 'code_adapter.py', 'ids.py', 'ids.json'):
        shutil.copyfile(os.path.join(HERE, f), os.path.join(m, f))
    open(os.path.join(m, 'decisions.txt'), 'w').write(decisions); open(os.path.join(m, 'trace.txt'), 'w').write(trace)
    json.dump(CFG_CONF, open(os.path.join(m, 'config_adapter.json'), 'w')); json.dump(CFG_CODE, open(os.path.join(m, 'code_adapter.json'), 'w'))
    for p, t in (code or CODE).items():
        os.makedirs(os.path.dirname(os.path.join(d, p)) or d, exist_ok=True)
        open(os.path.join(d, p), 'w').write(t)
    ci = os.path.join(m, 'ci.json')
    json.dump({'head_sha': sha, 'runs': [{'id': i, 'conclusion': 'success', 'run_attempt': 1} for i in runs]}, open(ci, 'w'))
    json.dump(tests or TESTS, open(os.path.join(m, 'tests.json'), 'w'))
    return m, d, ci


def verdict(**kw):
    m, d, ci = world(**kw)
    try:
        return R.compute(d, SHA, ci, config(), master=m, tests_path=os.path.join(m, 'tests.json'))
    finally:
        shutil.rmtree(m, ignore_errors=True); shutil.rmtree(d, ignore_errors=True)


def kinds(r):
    return sorted({b['kind'] for b in r['blockers']})


def scenario(name, fn):
    try:
        ok, detail = fn()
    except Exception as e:
        ok, detail = False, 'exception: %r' % e
    results.append((name, ok, detail))


def s_go():
    r = verdict()
    return r['verdict'] == 'GO' and not r['blockers'], 'fully evidenced candidate -> %s, blockers %s, warnings %d' % (r['verdict'], kinds(r), len(r['warnings']))


def s_open_decision():
    r = verdict(decisions=DECISIONS + '\n@LXM-DEC-000002 | open | C.1\nq: synthetic open question\n')
    return r['verdict'] == 'NO-GO' and 'decision' in kinds(r) and 'register' in kinds(r), \
        'open owner decision -> %s %s (the register declaring GO now disagrees too)' % (r['verdict'], kinds(r))


def s_gates():
    out = []
    for status in ('NOT VERIFIED', 'PASS (procedure) / NOT VERIFIED (staging)', 'PARTIAL', 'BLOCKED (headers PASS)'):
        code = dict(CODE); code['REG.md'] = GATES.replace('| 2 | Backups | PASS (verified) |', '| 2 | Backups | %s |' % status)
        r = verdict(code=code)
        out.append((status, r['verdict'], 'gate' in kinds(r)))
    return all(v == 'NO-GO' and g for _, v, g in out), '; '.join('"%s" -> %s' % (s, v) for s, v, _ in out)


def s_ci():
    one = verdict(runs=(7,))
    wrong = verdict(sha='b' * 40)
    return one['verdict'] == wrong['verdict'] == 'NO-GO' and 'ci' in kinds(one) and 'ci' in kinds(wrong), \
        'one run ID (two attempts would still be one) -> %s; runs for another SHA -> %s' % (one['verdict'], wrong['verdict'])


def s_tests():
    bad = [('failing checks', dict(TESTS, exit=1, failed=2, failures=['x broke'])), ('another SHA', dict(TESTS, sha='b' * 40)),
           ('tree changed by the run', dict(TESTS, tree_clean_after=False)), ('crash', dict(TESTS, exit=1, crashes=['TypeError: x']))]
    out = [(label, verdict(tests=t)) for label, t in bad]
    m, d, ci = world()
    try:
        missing = R.compute(d, SHA, ci, config(), master=m)
    finally:
        shutil.rmtree(m, ignore_errors=True); shutil.rmtree(d, ignore_errors=True)
    ok = all(r['verdict'] == 'NO-GO' and 'tests' in kinds(r) for _, r in out) and missing['verdict'] == 'NO-GO' and 'input' in kinds(missing)
    return ok, '; '.join('%s -> %s' % (l, r['verdict']) for l, r in out) + '; no results at all -> %s (fail closed)' % missing['verdict']


def s_adapters():
    code = dict(CODE); code['src/y.js'] = 'const brand = name || "Acmeco Platform";\n'
    r = verdict(code=code)
    what = sorted(b['what'] for b in r['blockers'])
    return r['verdict'] == 'NO-GO' and any('copy-fallback' in w for w in what) and any('untested-module' in w for w in what) and any('unowned' in w for w in what), \
        'a new hard-coded fallback in an untested, unowned module -> %s: %s' % (r['verdict'], [w.split(': ', 1)[-1] for w in what])


def s_trace_gap():
    r = verdict(trace=TRACE + '\n@LXM-REQ-000002\nbasis: nothing implements it\n')
    return r['verdict'] == 'NO-GO' and kinds(r) == ['register', 'trace'], \
        'a requirement with no implementation -> %s %s (the register declaring GO now disagrees too)' % (r['verdict'], kinds(r))


def s_fail_closed():
    m, d, ci = world()
    try:
        os.remove(ci)
        a = R.compute(d, SHA, ci, config(), master=m)
        os.remove(os.path.join(d, 'REG.md'))
        b = R.compute(d, SHA, os.path.join(m, 'missing.json'), config(), master=m)
        c = config(); del c['adapters']['code']['findings']['untested-module']
        open(os.path.join(d, 'src/z.js'), 'w').write('module.exports = 1;\n')
        e = R.compute(d, SHA, os.path.join(m, 'missing.json'), c, master=m)
    finally:
        shutil.rmtree(m, ignore_errors=True); shutil.rmtree(d, ignore_errors=True)
    unclassified = any('unclassified finding kind "untested-module"' in x['what'] for x in e['blockers'])
    return a['verdict'] == b['verdict'] == e['verdict'] == 'NO-GO' and 'input' in kinds(a) and 'input' in kinds(b) and unclassified, \
        'missing CI evidence -> %s; missing register -> %s; a finding kind with no rule -> %s' % (a['verdict'], b['verdict'], e['verdict'])


def s_warning_only():
    code = dict(CODE); code['conf/d.json'] = json.dumps({'look': {'title': 'Acmeco Platform', 'unusedKey': 'x'}})
    r = verdict(code=code)
    return r['verdict'] == 'GO' and any('unread' in w['what'] for w in r['warnings']), 'a declared but unread setting -> %s with a warning' % r['verdict']


def s_deterministic():
    a, b = verdict(), verdict()
    strip = lambda r: json.dumps({k: v for k, v in r.items() if k != 'inputs'}, sort_keys=True)
    return strip(a) == strip(b), 'two runs on the same inputs give the same verdict and blockers'


for args in [('Fully evidenced candidate computes GO', s_go),
             ('Open owner decision blocks; declared verdict cross-checked', s_open_decision),
             ('Any gate status that is not a clean PASS blocks', s_gates),
             ('CI: one run ID, or runs for another SHA, block', s_ci),
             ('Test results: failures, another SHA, a changed tree, a crash, none', s_tests),
             ('Adapter findings block (hard-coding, untested, unowned)', s_adapters),
             ('A traceability gap blocks', s_trace_gap),
             ('Fails closed: missing inputs, unclassified findings', s_fail_closed),
             ('Warnings alone do not block', s_warning_only),
             ('Deterministic', s_deterministic)]:
    scenario(*args)
fails = 0
for name, ok, detail in results:
    fails += not ok
    print('%s  %-58s %s' % ('PASS' if ok else 'FAIL', name, detail))
print('\n%d scenarios, %d failed' % (len(results), fails))
sys.exit(1 if fails else 0)
