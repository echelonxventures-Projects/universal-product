"""Fixtures for config_adapter.py: synthetic repositories, each built in a throwaway directory; nothing else is read.
Usage: python3 -I -B test_config_adapter.py"""
import json, os, shutil, sys, tempfile

sys.dont_write_bytecode = True  # a check never changes the Master directory (no __pycache__)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import config_adapter as C

CFG = {'declarations': [{'id': 'conf', 'file': 'conf/defaults.json', 'pointer': '/D'}],
       'code': {'roots': ['src', 'main.js'], 'exclude': ['src/vendor/'], 'extensions': ['.js']},
       'distinct': {'min_length': 5, 'skip_single_lowercase_word': True, 'skip_patterns': ['\\d+(\\.\\d+)?(px|%|ms|s)?']},
       'match_as_word': ['look\\.title'],
       'generic_consumers': ['Object\\.(?:entries|keys|values)\\(\\s*[\\w$.]*\\b{name}\\s*\\)']}
DEFAULTS = {'D': {'look': {'title': 'Acmeco', 'accent': '#ABCDEF', 'shade': '#123456', 'unused': '#FEDCBA', 'gap': '18px', 'mode': 'fixed'},
                  'flags': {'alpha': True, 'beta': False}}}
results = []


def repo(files, defaults=DEFAULTS):
    d = tempfile.mkdtemp(prefix='cfgfx-')
    os.makedirs(d + '/conf'); json.dump(defaults, open(d + '/conf/defaults.json', 'w'))
    for p, t in files.items():
        os.makedirs(os.path.dirname(os.path.join(d, p)) or d, exist_ok=True)
        open(os.path.join(d, p), 'w').write(t)
    return d


def run(files, cfg=CFG, defaults=DEFAULTS):
    d = repo(files, defaults)
    try:
        return C.analyse(d, cfg)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def by(rep):
    return {s['setting']: s for s in rep['settings']}


def scenario(name, fn):
    try:
        ok, detail = fn()
    except Exception as e:  # a crash is a failure
        ok, detail = False, 'exception: %r' % e
    results.append((name, ok, detail))


def s_readers():
    s = by(run({'src/a.js': 'const S = load(); paint(S.look.accent);\nfunction f(t) { return t.shade; }\nfor (const [k, v] of Object.entries(S.flags)) use(k, v);\n'}))
    got = {k: s[k]['reader'] for k in ('look.accent', 'look.shade', 'flags.alpha', 'look.unused')}
    return got == {'look.accent': 'explicit', 'look.shade': 'plausible', 'flags.alpha': 'plausible', 'look.unused': 'none'}, str(got)


def s_copies():
    src = ('const a = cfg.accent || "#ABCDEF";\nif (x === "#ABCDEF") go();\nconst list = ["#ABCDEF"];\n'
           'const iss = meta.issuer || "Acmeco";\nconst ua = "Acmeco-Hooks/1";\nfunction f(n = "#ABCDEF") {}\n')
    c = by(run({'src/a.js': src}))
    uses = sorted(x['use'] for k in ('look.accent', 'look.title') for x in c[k]['copies'])
    return uses == ['branch', 'embedded', 'fallback', 'fallback', 'fallback', 'literal'], str(uses)


def s_comments_and_strings():
    src = ('// "#ABCDEF" in a line comment\n/* "#ABCDEF"\n   still a comment */\nconst u = "http://host/x"; const k = "#ABCDEF";\n'
           "const q = 'it\\'s'; // \"#ABCDEF\"\nconst t = `multi\n\"#ABCDEF\"`;\n")
    cp = by(run({'src/a.js': src}))['look.accent']['copies']
    lines = sorted(x['line'] for x in cp)
    return lines == [4, 7], 'copies found on lines %s (expected 4: after a URL string; 7: inside a template literal)' % lines


def s_scope():
    rep = run({'src/vendor/lib.js': 'const k = "#ABCDEF";\n', 'src/a.txt': 'const k = "#ABCDEF";\n', 'other/b.js': 'const k = "#ABCDEF";\n',
               'main.js': 'const ok = 1;\n'})
    n = sum(len(s['copies']) for s in rep['settings'])
    return n == 0 and rep['summary']['files'] == 1, 'copies %d outside scope; files analysed %d (main.js only)' % (n, rep['summary']['files'])


def s_not_distinctive():
    c = by(run({'src/a.js': 'if (m === "fixed") a(); const g = "18px";\n'}))
    return not c['look.mode']['copies'] and not c['look.gap']['copies'], 'common words and plain measures are not counted as copies'


def s_ratchet():
    d = repo({'src/a.js': 'const a = cfg.accent || "#ABCDEF";\n'})
    try:
        base = C.analyse(d, CFG)['counts']
        same = C.ratchet(C.analyse(d, CFG)['counts'], base)
        open(d + '/src/b.js', 'w').write('const b = "#123456";\n')
        worse = C.ratchet(C.analyse(d, CFG)['counts'], base)
        os.remove(d + '/src/b.js'); open(d + '/src/a.js', 'w').write('const a = cfg.look.accent;\n')
        better = C.ratchet(C.analyse(d, CFG)['counts'], base)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    ok = same == ({}, {}) and list(worse[0]) == ['copy-literal · conf:look.shade · src/b.js'] and not better[0] and better[1]
    return ok, 'unchanged: pass; a new copy: %s; a copy removed: pass, better %s' % (list(worse[0]), list(better[1]))


def s_deterministic():
    files = {'src/a.js': 'paint(S.look.accent); const k = "#ABCDEF";\n', 'src/b.js': 'x(t.shade)\n'}
    a, b = run(files), run(files)
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True), 'two runs, identical reports'


def s_configurable():
    cfg = json.loads(json.dumps(CFG))
    cfg['declarations'].append({'id': 'more', 'file': 'conf/more.json'})
    d = repo({'src/a.js': 'use(S.limits.perPage);\n'})
    try:
        json.dump({'limits': {'perPage': 24}}, open(d + '/conf/more.json', 'w'))
        s = by(C.analyse(d, cfg))
    finally:
        shutil.rmtree(d, ignore_errors=True)
    src = open(os.path.join(HERE, 'config_adapter.py'), encoding='utf-8').read()
    real = json.load(open(os.path.join(HERE, 'config_adapter.json')))
    words = {w for dcl in real['declarations'] for w in [dcl.get('file'), dcl.get('pointer', '').strip('/')] + dcl.get('files', []) if w}
    words |= set(real.get('sources', {}).get('not_declared', {})) | set(real['code']['roots'])
    leaked = sorted(w for w in words if w in src)
    return s.get('limits.perPage', {}).get('reader') == 'explicit' and not leaked, \
        'a new declaration added by configuration alone is analysed: %s; repository names in the adapter source: %s' % ('limits.perPage' in s, leaked or 'none')


def s_names():
    cfg = json.loads(json.dumps(CFG))
    cfg['declarations'].append({'id': 'env', 'kind': 'names', 'files': ['RUN.md'], 'pattern': '^\\| `([A-Z][A-Z0-9_]+)', 'discover': 'process\\.env\\.([A-Z][A-Z0-9_]*)'})
    d = repo({'RUN.md': '| Variable | What |\n|---|---|\n| `APP_PORT` | port |\n| `APP_OLD` | gone |\n| `APP_MAIL` | via an alias |\n',
              'src/a.js': 'listen(process.env.APP_PORT); const k = process.env.APP_SECRET; // process.env.APP_COMMENTED\nfunction m(e) { return e.APP_MAIL; }\n'})
    try:
        s = {x['setting']: x['reader'] for x in C.analyse(d, cfg)['settings'] if x['declaration'] == 'env'}
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return s == {'APP_PORT': 'explicit', 'APP_OLD': 'none', 'APP_SECRET': 'undeclared', 'APP_MAIL': 'plausible'}, str(s)


def s_skip_keys_and_identifiers():
    cfg = json.loads(json.dumps(CFG)); cfg['declarations'][0]['skip_keys'] = ['$comment']
    defaults = {'D': {'$comment': 'Explains the look block in prose.', 'look': dict(DEFAULTS['D']['look'])}}
    c = by(run({'src/a.js': 'const k = process.env.ACMECO_MASTER_KEY; const w = "Acmeco";\n'}, cfg, defaults))
    uses = sorted(x['use'] for x in c['look.title']['copies'])
    return '$comment' not in c and uses == ['embedded', 'literal'], 'commentary skipped: %s; the value inside an identifier counts: %s' % ('$comment' not in c, uses)


def s_accounting():
    cfg = json.loads(json.dumps(CFG))
    cfg['sources'] = {'account_for': ['conf'], 'extensions': ['.json'], 'not_declared': {'conf/catalogue.json': 'catalogue of records'}}
    d = repo({'src/a.js': 'x\n', 'conf/catalogue.json': '[]', 'conf/forgotten.json': '{}'})
    try:
        rep = C.analyse(d, cfg)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    src = rep['summary']['sources']
    return src['unaccounted'] == ['conf/forgotten.json'] and 'unaccounted · conf/forgotten.json' in rep['counts'], \
        'declared %d, catalogues %d, unaccounted %s' % (src['declared'], src['not_declared'], src['unaccounted'])


def s_runtime_trace():
    d = repo({'src/a.js': 'paint(S.look.accent); function f(t) { return t.shade; }\n'})
    try:
        tf = os.path.join(d, 'trace.jsonl')
        open(tf, 'w').write('{"path": "look.accent", "how": "read"}\n{"path": "look.shade", "how": "serialized"}\n')
        cfg = json.loads(json.dumps(CFG)); cfg['_runtime'] = {'file': tf, 'declaration': 'conf'}
        rep = C.analyse(d, cfg)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    s = by(rep)
    got = {k: s[k]['reader'] for k in ('look.accent', 'look.shade', 'look.title')}
    ok = got == {'look.accent': 'runtime', 'look.shade': 'serialized', 'look.title': 'none'} and 'runtime-unread · conf:look.shade' in rep['counts'] \
        and 'runtime-unread · conf:look.accent' not in rep['counts']
    return ok, 'read -> runtime, only serialized -> serialized (reported), never seen -> keeps its static class: %s' % got


for args in [('Readers: explicit, plausible (alias, iteration), none', s_readers),
             ('Copies: branch, fallback, literal, embedded', s_copies),
             ('Comments ignored; strings, URLs and templates kept', s_comments_and_strings),
             ('Only configured roots and extensions; exclusions honoured', s_scope),
             ('Common words and measures are not copies', s_not_distinctive),
             ('Ratchet: unchanged passes, a new copy fails, a removal passes', s_ratchet),
             ('Deterministic report', s_deterministic),
             ('Configuration-driven; no repository knowledge in the adapter', s_configurable),
             ('Names: read, read via alias, unread, undeclared', s_names),
             ('Commentary keys skipped; a value inside an identifier counts', s_skip_keys_and_identifiers),
             ('Every source declared or classified; others unaccounted', s_accounting),
             ('Runtime trace: read, serialized only, unseen', s_runtime_trace)]:
    scenario(*args)
fails = 0
for name, ok, detail in results:
    fails += not ok
    print('%s  %-58s %s' % ('PASS' if ok else 'FAIL', name, detail))
print('\n%d scenarios, %d failed' % (len(results), fails))
sys.exit(1 if fails else 0)
