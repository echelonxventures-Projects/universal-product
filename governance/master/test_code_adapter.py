"""Fixtures for code_adapter.py: synthetic repositories in throwaway directories; nothing else is read.
Usage: python3 -I -B test_code_adapter.py"""
import json, os, shutil, subprocess, sys, tempfile

sys.dont_write_bytecode = True  # a check never changes the Master directory (no __pycache__)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import code_adapter as K

CFG = {'commands': {'package': 'package.json', 'ci_workflows': ['ci.yml'], 'script_call': 'npm (?:run\\s+([\\w:.-]+)|test\\b)',
                    'file_call': 'node\\s+(?:--[\\w=-]+\\s+)*([\\w./-]+\\.js)', 'not_gates': {'start': 'a tool'}},
       'tests': {'roots': ['t'], 'extensions': ['.js'], 'helpers': []},
       'modules': {'roots': ['src'], 'extensions': ['.js'], 'exclude': ['src/data/'], 'loaders': ['require\\(', 'new\\s+Worker\\('], 'dynamic_dirs': ['src/plug/']},
       'ownership': {'registry': 'owners.json', 'list': 'modules', 'path_field': 'path'},
       'duplicates': {'min_lines': 3, 'min_chars': 60}}
BODY = '\n  const total = items.reduce((a, b) => a + b.amount, 0);\n  const tax = Math.round(total * rate);\n  return { total, tax };\n'
BASE = {
    'package.json': json.dumps({'scripts': {'test': 'node t/a.js && node t/b.js', 'check:ui': 'node t/ui.js', 'gate2': 'node tools/g.js', 'start': 'node src/x.js'}}),
    'ci.yml': 'steps:\n  - run: npm ci\n  - run: npm test\n  - run: npm run check:ui\n',
    't/a.js': 'const x = require("../src/x.js");\n', 't/b.js': 'const p = require("path"); require(p.join(__dirname, "..", "src", "w.js"));\n',
    't/ui.js': '/* browser check */\n', 't/orphan.js': 'require("../src/z.js");\n',
    'src/x.js': 'const y = require("./y");\nfor (const f of fs.readdirSync(dir)) require("./plug/" + f);\nconst m = require("./other/" + name);\n'
                'function sum(items, rate) {' + BODY + '}\n',
    'src/y.js': 'const w = new Worker(path.join(__dirname, "worker.js"));\nconst f = (items, rate) => {' + BODY + '};\nconst s = "{ not a block }";\n',
    'src/w.js': 'module.exports = {};\n', 'src/worker.js': 'module.exports = {};\n', 'src/plug/one.js': 'exports.r = 1;\n',
    'src/other/two.js': 'exports.r = 2;\n', 'src/z.js': 'function tiny() { return 1; }\n', 'src/data/seed.js': 'module.exports = [];\n',
    'owners.json': json.dumps({'modules': [{'path': p} for p in ['src/x.js', 'src/y.js', 'src/w.js', 'src/worker.js', 'src/plug/one.js', 'src/z.js', 'src/z.js', 'src/gone.js']]})}
results = []


def repo(files):
    d = tempfile.mkdtemp(prefix='codefx-')
    for p, t in files.items():
        os.makedirs(os.path.dirname(os.path.join(d, p)) or d, exist_ok=True)
        open(os.path.join(d, p), 'w').write(t)
    return d


def run(files=BASE, cfg=CFG):
    d = repo(files)
    try:
        return K.analyse(d, json.loads(json.dumps(cfg)))
    finally:
        shutil.rmtree(d, ignore_errors=True)


def scenario(name, fn):
    try:
        ok, detail = fn()
    except Exception as e:
        ok, detail = False, 'exception: %r' % e
    results.append((name, ok, detail))


def s_executed():
    s = run()['summary']
    return s['unexecuted_scripts'] == ['gate2'] and s['unwired_tests'] == ['t/orphan.js'] and s['scripts_reached_from_ci'] == 2, \
        'unexecuted %s (start exempt); unwired %s; scripts reached from CI %d' % (s['unexecuted_scripts'], s['unwired_tests'], s['scripts_reached_from_ci'])


def s_tested():
    s = run()['summary']
    ok = s['untested_modules'] == ['src/other/two.js', 'src/z.js'] and s['unresolved_dynamic_loads'] == ['src/x.js loads src/other/<variable>']
    return ok, 'untested %s (z only from an unwired test; other/ only through an unresolved load); worker, path.join and the configured plug/ folder reached; unresolved %s' % (
        s['untested_modules'], s['unresolved_dynamic_loads'])


def s_owned():
    s = run()['summary']
    return s['unowned'] == ['src/other/two.js'] and s['owned_twice'] == ['src/z.js'] and s['owner_lists_missing_file'] == ['src/gone.js'], \
        'unowned %s, owned twice %s, listed but missing %s' % (s['unowned'], s['owned_twice'], s['owner_lists_missing_file'])


def s_duplicates():
    r = run()
    sites = [v for v in r['duplicates'].values()]
    return len(sites) == 1 and sorted(f for f, _ in sites[0]) == ['src/x.js', 'src/y.js'], \
        'one duplicated body found in %s; the tiny function and the braces inside a string are ignored' % (sites[0] if sites else None)


def s_clean_tree():
    d = repo({'a.txt': 'x\n', 'package.json': '{"scripts": {}}', 'ci.yml': '', 'owners.json': '{"modules": []}'})
    try:
        g = lambda *a: subprocess.run(['git', '-c', 'user.name=f', '-c', 'user.email=f@f', '-c', 'commit.gpgsign=false'] + list(a), cwd=d, capture_output=True, check=True)
        g('init', '-q'); g('add', '-A'); g('commit', '-qm', 'fixture')
        cfg = json.loads(json.dumps(CFG)); cfg['_git_clean'] = True
        clean = K.analyse(d, cfg)['summary']['dirty']
        open(os.path.join(d, 'new.txt'), 'w').write('y\n'); open(os.path.join(d, 'a.txt'), 'a').write('z\n')
        dirty = K.analyse(d, cfg)['summary']['dirty']
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return clean == [] and len(dirty) == 2, 'committed tree: clean; after an edit and a new file: %s' % dirty


def s_ratchet_and_determinism():
    d = repo(BASE)
    try:
        base = K.analyse(d, json.loads(json.dumps(CFG)))['counts']
        again = K.analyse(d, json.loads(json.dumps(CFG)))
        open(os.path.join(d, 'src/new.js'), 'w').write('module.exports = 1;\n')
        worse = K.ratchet(K.analyse(d, json.loads(json.dumps(CFG)))['counts'], base)[0]
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return again['counts'] == base and sorted(worse) == ['unowned · src/new.js', 'untested-module · src/new.js'], \
        'identical on rerun; a new untested, unowned module fails the ratchet with %s' % sorted(worse)


def s_trace():
    files = dict(BASE); files['doms.json'] = json.dumps({'domains': [{'key': 'core', 'owns': {'files': ['src/x.js', 'src/y.js']}}, {'key': 'extra', 'owns': {'files': ['src/z.js']}}]})
    d = repo(files); m = tempfile.mkdtemp(prefix='codefx-master-')
    try:
        for f in ('build.py', 'ids.py', 'ids.json', 'layout.json', 'gate.json', 'validate.json'):  # the Master's own parser, and the registries it reads, sit beside trace.txt
            shutil.copyfile(os.path.join(HERE, f), os.path.join(m, f))
        open(os.path.join(m, 'trace.txt'), 'w').write('# basis-default: fixture\n@LXM-REQ-000001\nimpl: src/x.js, src/gone.js\ntest: t/a.js\n\n@LXM-REQ-000002\nbasis: nothing implements it\n')
        cfg = json.loads(json.dumps(CFG)); cfg['_trace'] = os.path.join(m, 'trace.txt'); cfg['domains'] = {'registry': 'doms.json', 'list': 'domains', 'key': 'key', 'files': 'owns.files'}
        t = K.analyse(d, cfg)['summary']['trace']
    finally:
        shutil.rmtree(d, ignore_errors=True); shutil.rmtree(m, ignore_errors=True)
    ok = t['missing_paths'] == ['LXM-REQ-000001 impl src/gone.js'] and t['gaps'] == ['LXM-REQ-000002'] and 'src/y.js' in t['untraced_modules'] \
        and 'src/x.js' not in t['untraced_modules'] and t['per_domain'] == {'core': {'modules': 2, 'traced': 1}, 'extra': {'modules': 1, 'traced': 0}}
    return ok, 'missing %s; gaps %s; per domain %s' % (t['missing_paths'], t['gaps'], t['per_domain'])


def s_kernel_derivation():
    files = dict(BASE); files['schema.sql'] = 'CREATE TABLE k_nodes (id);\nCREATE TABLE IF NOT EXISTS orders (id);\nCREATE TABLE sessions (id);\n'
    cfg = json.loads(json.dumps(CFG)); cfg['kernel'] = {'schema_files': ['schema.sql'], 'table_pattern': 'CREATE TABLE (?:IF NOT EXISTS )?"?(\\w+)', 'kernel_prefix': 'k_', 'exempt': {'sessions': 'transport state'}}
    k = run(files, cfg)['summary']['kernel']
    return k['kernel'] == ['k_nodes'] and k['outside'] == ['orders'] and k['exempt'] == ['sessions'], 'kernel %s, outside %s, exempted with a reason %s' % (k['kernel'], k['outside'], k['exempt'])


def s_no_repository_knowledge():
    src = open(os.path.join(HERE, 'code_adapter.py'), encoding='utf-8').read()
    real = json.load(open(os.path.join(HERE, 'code_adapter.json')))
    words = set(real['commands']['not_gates']) | set(real['commands']['ci_workflows']) | {real['ownership']['registry']} | set(real['modules']['dynamic_dirs'])
    leaked = sorted(w for w in words if w in src and any(c in w for c in '/.:'))  # paths and script names, not plain words like 'start'
    return not leaked, 'repository names in the adapter source: %s' % (leaked or 'none')


def s_named_values():
    # environments are configuration: a comparison with an environment selector, or a written environment name, is found
    # by the rules the real configuration declares; flags compared with "1" and names inside comments are not
    files = dict(BASE)
    files['src/env.js'] = ('if (process.env.NODE_ENV === "production") a();\nif ("live" !== process.env.APP_ENVIRONMENT) b();\n'
                           'if (process.env.LX_OFFLINE === "1") c();\nconst mode = "staging";\n// "production" in a comment\n')
    cfg = json.loads(json.dumps(CFG)); cfg['named_values'] = [r for r in json.load(open(os.path.join(HERE, 'code_adapter.json')))['named_values'] if r['finding'].startswith('environment-')]
    for r in cfg['named_values']:
        r['roots'], r['exclude'] = ['src'], []
    nv = run(files, cfg)['summary']['named_values']
    br, nm = nv['environment-branch']['list'], nv['environment-name']['list']
    ok = len(br) == 2 and all(h.startswith('src/env.js:') for h in br) and sorted(h.split(' ')[0] for h in nm) == ['src/env.js:1', 'src/env.js:4']
    return ok, 'environment-branch %s; environment-name %s' % (br, nm)


def s_names_from_registries():
    # agent and vendor names come from registries, not from the rule: a registered name in code is found, in any case and as a
    # whole word only; the registry itself (excluded data) and longer identifiers are not findings
    files = dict(BASE)
    files['src/data/providers.json'] = json.dumps({'P': [{'name': 'VendorX'}, {'name': 'Acme Vision'}]})
    files['src/ai.js'] = 'const a = "vendorx";\nconst b = "Acme Vision model";\nconst c = "VendorXtra";\n'
    cfg = json.loads(json.dumps(CFG))
    cfg['named_values'] = [{'finding': 'agent-or-vendor-name', 'roots': ['src'], 'extensions': ['.js', '.json'], 'exclude': ['src/data/'],
                            'names_from': [{'in': 'code', 'file': 'src/data/providers.json', 'paths': ['P.*.name']}]}]
    hits = run(files, cfg)['summary']['named_values']['agent-or-vendor-name']['list']
    return sorted(h.split(' ')[0] for h in hits) == ['src/ai.js:1', 'src/ai.js:2'], 'findings %s' % hits


for args in [('Executed: CI command graph, exemptions, unwired tests', s_executed),
             ('Tested: require, path.join, Worker, configured dynamic dirs', s_tested),
             ('Owned: unowned, owned twice, listed but missing', s_owned),
             ('Duplicates: same body twice; small and string braces ignored', s_duplicates),
             ('Clean tree: committed clean, edits and new files reported', s_clean_tree),
             ('Ratchet and determinism', s_ratchet_and_determinism),
             ('Traceability: missing paths, gaps, untraced modules, per domain', s_trace),
             ('Kernel derivation: tables outside the kernel, exemptions', s_kernel_derivation),
             ('Named values: environment selectors and names, from configuration', s_named_values),
             ('Names from registries: agents and vendors in code', s_names_from_registries),
             ('Configuration-driven; no repository knowledge in the adapter', s_no_repository_knowledge)]:
    scenario(*args)
fails = 0
for name, ok, detail in results:
    fails += not ok
    print('%s  %-62s %s' % ('PASS' if ok else 'FAIL', name, detail))
print('\n%d scenarios, %d failed' % (len(results), fails))
sys.exit(1 if fails else 0)
