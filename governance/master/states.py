"""Level 3 computed state (design §1; lifecycle states of the architecture text §4). For every requirement, each kind of
evidence is checked independently, and its state is the highest state reached with every earlier state also evidenced.
A state is never declared: it is derived from traceability, code, configuration, runtime trace and test results.
Usage: python3 -I states.py <code root> --sha <tested sha> --tests <test-results.json> [--runtime-trace <file>] [--md <out>] [--json <out>]"""
import json, os, re, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from ids import X  # identifier formats and file names come from the registries (LXM-REQ-000240)
HERE_STATES = os.path.dirname(os.path.abspath(__file__))
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import assimilate as A


def compute(root, sha, tests_path, runtime_trace=None, master=HERE):
    cfg = json.load(open(os.path.join(master, X('{@knowledge_json}')), encoding='utf-8'))
    order = cfg['states']['order']
    build = A.load_build(master)
    recs = A.blocks(A.read(os.path.join(master, X('{@reqs_txt}'))))
    _, trace = build.parse_trace(A.read(os.path.join(master, X('{@trace_txt}'))))
    decl = {d['id'] for d in json.load(open(os.path.join(master, X('{@config_adapter_json}')), encoding='utf-8'))['declarations']}
    t = json.load(open(tests_path, encoding='utf-8')) if tests_path and os.path.isfile(tests_path) else {}
    passed_on_sha = t.get('sha') == sha and t.get('exit') == 0 and not t.get('failed') and t.get('tree_clean_after')
    pkg_file = json.load(open(os.path.join(HERE_STATES, X('{@code_adapter_json}')), encoding='utf-8'))['commands']['package']  # the repository's manifest, as its configuration names it
    pkg = json.load(open(os.path.join(root, pkg_file), encoding='utf-8')).get('scripts', {}).get('test', '')
    runtime_decls = set(cfg['states'].get('runtime_traced_declarations', []))
    read_paths = set()
    if runtime_trace and os.path.isfile(runtime_trace):
        read_paths = {json.loads(l)['path'] for l in open(runtime_trace, encoding='utf-8') if l.strip() and json.loads(l)['how'] == 'read'}
    acfg = json.load(open(os.path.join(master, X('{@code_adapter_json}')), encoding='utf-8')).get('domains')
    owner_of = {}
    if acfg and os.path.isfile(os.path.join(root, acfg['registry'])):
        for dom in json.load(open(os.path.join(root, acfg['registry']), encoding='utf-8'))[acfg['list']]:
            files = dom
            for part in acfg['files'].split('.'):
                files = files.get(part, {}) if isinstance(files, dict) else {}
            for f in files or []:
                owner_of[f] = dom[acfg['key']]
    spec_dir = cfg['states'].get('domain_specs', 'docs/domains/{domain}.md')
    def designed(impl, explicit):
        if explicit:
            return all(os.path.isfile(os.path.join(root, p)) for p in explicit), 'explicit'
        docs = [spec_dir.format(domain=owner_of[m]) if m in owner_of else None for m in impl]
        return bool(impl) and all(d and os.path.isfile(os.path.join(root, d)) for d in docs), 'derived from the owning domain'
    out = {}
    for rid in recs:
        tr = trace.get(rid, {})
        impl = [p for p in tr.get('impl', '').split(', ') if p]
        conf = [c for c in tr.get('config', '').split(', ') if c]
        tests = [p for p in tr.get('test', '').split(', ') if p]
        dsg, dbasis = designed(impl, [p for p in tr.get('spec', '').split(', ') if p])
        ev = {'Specified': True,
              'Designed': dsg,  # a specification exists: named in trace.txt, or derived (module -> owning domain -> its specification)
              'Implemented': bool(impl) and all(os.path.exists(os.path.join(root, p)) for p in impl),
              'Configured': (set(conf) <= decl) if conf else None,  # None: not applicable (the requirement governs no configuration)
              'Enforced at runtime': (bool(read_paths) and any(c in runtime_decls for c in conf)) if conf else None,
              'Verified': bool(tests) and passed_on_sha and all(os.path.exists(os.path.join(root, p)) and (p in pkg or p.startswith('scripts/')) for p in tests),
              'Certified': False}  # release evidence and owner approval (LXM-DEC-000013) do not exist
        state = 'Specified'
        for s in order[1:]:
            if ev.get(s) is None and s in ('Configured', 'Enforced at runtime'):
                continue  # not applicable is not a gap
            if not ev.get(s):
                break
            state = s
        later = [s for s in order[order.index(state) + 1:] if ev.get(s)]
        out[rid] = {'state': state, 'evidence': {k: v for k, v in ev.items() if v}, 'not_applicable': [k for k, v in ev.items() if v is None], 'evidenced_beyond_a_gap': later,
                    'kind': 'product' if rid in trace else 'procedural (traced by stage actions, H.2)', 'design_basis': dbasis if dsg else None}
    return out


def markdown(res, sha):
    order = list(dict.fromkeys(['Specified', 'Designed', 'Implemented', 'Configured', 'Enforced at runtime', 'Verified', 'Certified']))
    cnt = {s: sum(1 for r in res.values() if r['state'] == s) for s in order}
    ev = {s: sum(1 for r in res.values() if s in r['evidence']) for s in order}
    lines = ['# Level 3: computed state of every requirement (candidate `%s`)' % sha, '',
             'Generated by `states.py` from traceability, code, configuration, runtime trace and test results. Nothing here is declared.', '',
             '| State | Requirements whose state it is | Requirements with this evidence |', '|---|---|---|']
    lines += ['| %s | %d | %d |' % (s, cnt[s], ev[s]) for s in order]
    gap = sum(1 for r in res.values() if r['evidenced_beyond_a_gap'])
    lines += ['', '%d requirements have later evidence but stay at an earlier state, because an earlier state is not evidenced.' % gap, '',
              '| Requirement | State | Evidence | Evidenced beyond a gap | Kind |', '|---|---|---|---|---|']
    lines += ['| %s | %s | %s | %s | %s |' % (rid, r['state'], ', '.join(r['evidence']) + (' (n/a: %s)' % ', '.join(r['not_applicable']) if r.get('not_applicable') else ''), ', '.join(r['evidenced_beyond_a_gap']) or '—', r['kind']) for rid, r in res.items()]
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    opt = lambda k: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else None
    res = compute(sys.argv[1], opt('--sha'), opt('--tests'), opt('--runtime-trace'))
    if opt('--json'):
        json.dump(res, open(opt('--json'), 'w', encoding='utf-8'), indent=1)
    if opt('--md'):
        open(opt('--md'), 'w', encoding='utf-8').write(markdown(res, opt('--sha')))
    print(markdown(res, opt('--sha')).split('\n\n| Requirement')[0].split('\n', 4)[4])
