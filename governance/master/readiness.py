"""Computed release readiness (step 5; LXM-REQ-000204, LXM-REQ-000214). Readiness is derived from evidence, never declared.
Usage: python3 -I readiness.py <code root> --candidate <sha> --ci <ci-runs.json> --tests <test-results.json> [--runtime-trace <file>] [--config readiness.json] [--json <out>] [--md <out>]

Inputs, all read at run time so that no stale evidence is reused:
  - the Master's decision register (decisions.txt) and implementation traceability (trace.txt), beside this file;
  - the release register in the code tree (its gate table);
  - the CI runs recorded for the candidate commit (a JSON file fetched read-only from the CI provider);
  - the results of the test suite run on the candidate commit (test_results.py);
  - the configuration and code adapters, run here on the same code tree.
Each rule in the configuration says what blocks release, which requirement it serves, and who resolves it.
A missing or unreadable input is itself a blocker: the verdict fails closed. GO only when nothing blocks.
Exit 0 GO, 1 NO-GO, 2 usage error."""
import hashlib, importlib.util, json, os, re, sys

sys.dont_write_bytecode = True  # a check never changes the Master directory (no __pycache__)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from ids import X, registry  # identifier formats and file names come from the registries (LXM-REQ-000240)
REPORT = registry('reporting_json')  # how much the reports show

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from actors import resolve as resolve_roles
sys.path.insert(0, HERE)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def digest(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest() if os.path.isfile(path) else None


def compute(root, candidate, ci_path, cfg, master=HERE, tests_path=None, runtime_trace=None):
    cfg = resolve_roles(cfg, HERE)  # who resolves a blocker is a role, held by whichever actor the registry names (LXM-REQ-000239)
    blockers, warnings, inputs = [], [], {}
    block = lambda kind, what, rule, who, ref: blockers.append({'kind': kind, 'what': what, 'rule': rule, 'resolves': who, 'requirement': ref})
    build = load('lxm_build', os.path.join(master, X('{@build_py}')))
    # 1. owner decisions
    p = os.path.join(master, X('{@decisions_txt}')); inputs[X('{@decisions_txt}')] = digest(p)
    r = cfg['rules']['decisions']
    try:
        for d in build.parse_decisions(open(p, encoding='utf-8').read())[1]:
            if d['status'] == 'open' and d['id'] not in r.get('not_blocking', {}):
                block('decision', '%s open: %s' % (d['id'], d.get('q', '')), r['rule'], r['resolves'], r['requirement'])
    except OSError as e:
        block('input', 'decision register unreadable: %s' % e, 'fail closed', cfg['input_owner'], '')
    # 2. release gates from the register
    rg = cfg['register']; p = os.path.join(root, rg['file']); inputs[rg['file']] = digest(p)
    gates = []
    try:
        text = open(p, encoding='utf-8').read()
        section = text.split(rg['section'], 1)[1] if rg['section'] in text else ''
        hdr = None
        for line in section.split('\n'):
            if not line.startswith('|'):
                if hdr and gates:
                    break
                continue
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if hdr is None:
                hdr = cells; continue
            if set(cells[0]) <= set('-: '):
                continue
            row = dict(zip(hdr, cells))
            gates.append(row)
        if len(gates) != rg['expected_gates']:
            block('input', 'register gate table: %d rows found, %d expected' % (len(gates), rg['expected_gates']), 'fail closed', cfg['input_owner'], '')
        for g in gates:
            st = g.get(rg['status_column'], '')
            ok = re.match(rg['pass_pattern'], st) and not any(w in st for w in rg['blocking_words'])
            if not ok:
                owner = g.get(rg['owner_column'], '').strip()
                block('gate', 'gate %s %s: %s' % (g.get(rg['id_column']), g.get(rg['name_column']), st), rg['rule'],
                      owner if owner and owner != '—' else 'unassigned: the owner must name who closes it', rg['requirement'])
    except OSError as e:
        block('input', 'release register unreadable: %s' % e, 'fail closed', cfg['input_owner'], '')
    # 3. CI on the candidate commit
    rc = cfg['rules']['ci']; inputs[os.path.basename(ci_path)] = digest(ci_path)
    try:
        ci = json.load(open(ci_path, encoding='utf-8'))
        runs = {x['id'] for x in ci.get('runs', []) if x.get('conclusion') == 'success'}
        if ci.get('head_sha') != candidate:
            block('ci', 'CI evidence is for %s, not the candidate %s' % (str(ci.get('head_sha'))[:12], candidate[:12]), rc['rule'], rc['resolves'], rc['requirement'])
        elif len(runs) < rc['distinct_successful_runs']:
            block('ci', '%d distinct successful CI run(s) on %s; %d required (attempts of one run count once)' % (
                len(runs), candidate[:12], rc['distinct_successful_runs']), rc['rule'], rc['resolves'], rc['requirement'])
    except (OSError, ValueError) as e:
        block('input', 'CI evidence unreadable: %s' % e, 'fail closed', rc['resolves'], rc['requirement'])
    # 3b. test results on the candidate commit
    rt = cfg['tests']
    if not tests_path or not os.path.isfile(tests_path):
        block('input', 'no test results for the candidate', 'fail closed: ' + rt['rule'], rt['resolves'], rt['requirement'])
    else:
        inputs[os.path.basename(tests_path)] = digest(tests_path)
        t = json.load(open(tests_path, encoding='utf-8'))
        problems = (['results are for %s, not the candidate' % str(t.get('sha'))[:12]] if t.get('sha') != candidate else []) + \
            (['exit %s' % t.get('exit')] if t.get('exit') != 0 else []) + (['%d failing checks' % t['failed']] if t.get('failed') else []) + \
            (['%d crash lines' % len(t['crashes'])] if t.get('crashes') else []) + (['the tree changed during the run'] if not t.get('tree_clean_after') else [])
        if problems:
            block('tests', '%s on %s (%s): %s; first: %s' % (t.get('command'), t.get('runtime'), str(t.get('sha'))[:12], ', '.join(problems),
                                                            (t.get('failures') or t.get('crashes') or ['—'])[0]), rt['rule'], rt['resolves'], rt['requirement'])
    # 4. adapters, run now on the same tree
    findings = {}
    for name, a in cfg['adapters'].items():
        mod = load(name, os.path.join(master, a['module']))
        acfg = json.load(open(os.path.join(master, a['config']), encoding='utf-8'))
        inputs[a['config']] = digest(os.path.join(master, a['config']))
        if a.get('trace'):
            acfg['_trace'] = os.path.join(master, a['trace'])
        if runtime_trace and a.get('runtime_declaration'):
            acfg['_runtime'] = {'file': runtime_trace, 'declaration': a['runtime_declaration']}
            inputs[os.path.basename(runtime_trace)] = digest(runtime_trace)
        rep = mod.analyse(master if a.get('scans') == 'master' else root, acfg)  # an adapter scans the code, or the Master's own tooling
        for key, n in rep['counts'].items():
            kind = key.split(' · ')[0]
            rule = a['findings'].get(kind)
            if rule is None:
                block('input', '%s reports an unclassified finding kind "%s"' % (name, kind), 'fail closed: every finding kind needs a rule', cfg['input_owner'], '')
                continue
            findings.setdefault((name, kind), [0, rule, rep['summary'].get('distinct_sites', {}).get(kind)])[0] += n
    for (name, kind), (n, rule, sites) in sorted(findings.items()):
        item = {'kind': name, 'what': '%s: %d × %s%s' % (name, n, kind, '' if sites in (None, n) else ' (%d distinct code sites; settings sharing a value count each)' % sites), 'rule': rule['rule'], 'resolves': rule['resolves'], 'requirement': rule['requirement']}
        (blockers if rule['severity'] == 'block' else warnings).append(item)
    # 5. known traceability gaps
    p = os.path.join(master, X('{@trace_txt}')); inputs[X('{@trace_txt}')] = digest(p)
    rt = cfg['rules']['trace_gaps']
    for rid, t in build.parse_trace(open(p, encoding='utf-8').read())[1].items():
        if not t.get('impl'):
            block('trace', '%s has no implementation (%s)' % (rid, t.get('basis', '')), rt['rule'], rt['resolves'], rid)
    computed = 'GO' if not blockers else 'NO-GO'
    declared = None
    if rg.get('declared_pattern') and gates:
        m = re.search(rg['declared_pattern'], text, re.M)
        declared = m.group(1) if m else None
        if declared and declared != computed:
            block('register', 'the register declares %s but the evidence computes %s' % (declared, computed), 'a declared verdict must equal the computed one',
                  cfg['rules']['decisions']['resolves'], rg['requirement'])
    verdict = 'GO' if not blockers else 'NO-GO'
    by_who = {}
    for b in blockers:
        by_who[b['resolves']] = by_who.get(b['resolves'], 0) + 1
    return {'verdict': verdict, 'candidate': candidate, 'blockers': blockers, 'warnings': warnings, 'by_resolver': dict(sorted(by_who.items())),
            'gates': len(gates), 'register_declares': declared, 'inputs': dict(sorted(inputs.items()))}


def markdown(r):
    out = ['# Computed release readiness: **%s**' % r['verdict'], '',
           'Candidate `%s`. Derived from evidence by `readiness.py`; nothing here is declared by hand. %d blockers, %d warnings. '
           'The release register declares %s.' % (r['candidate'], len(r['blockers']), len(r['warnings']), r['register_declares'] or 'no verdict'), '', '## Who resolves what', '', '| Resolves | Blockers |', '|---|---|']
    out += ['| %s | %d |' % kv for kv in r['by_resolver'].items()]
    out += ['', '## Blockers', '', '| Kind | What | Rule | Requirement | Resolves |', '|---|---|---|---|---|']
    out += ['| %s | %s | %s | %s | %s |' % (b['kind'], b['what'].replace('|', '\\|')[:REPORT['excerpt']['blocker']], b['rule'], b['requirement'] or '—', b['resolves']) for b in r['blockers']]
    out += ['', '## Warnings (do not block)', '', '| What | Rule | Requirement |', '|---|---|---|']
    out += ['| %s | %s | %s |' % (w['what'], w['rule'], w['requirement'] or '—') for w in r['warnings']] or ['None.']
    out += ['', '## Inputs (SHA-256)', ''] + ['- `%s` %s' % (k, v or '**missing**') for k, v in r['inputs'].items()]
    return '\n'.join(out) + '\n'


def main(argv):
    opt = lambda k: argv[argv.index(k) + 1] if k in argv else None
    if len(argv) < 2 or not opt('--candidate') or not opt('--ci'):
        print(__doc__); return 2
    cfg = json.load(open(opt('--config') or os.path.join(HERE, X('{@readiness_json}')), encoding='utf-8'))
    r = compute(argv[1], opt('--candidate'), opt('--ci'), cfg, tests_path=opt('--tests'), runtime_trace=opt('--runtime-trace'))
    if opt('--json'):
        json.dump(r, open(opt('--json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    if opt('--md'):
        open(opt('--md'), 'w', encoding='utf-8').write(markdown(r))
    print('%s: %d blockers (%s), %d warnings' % (r['verdict'], len(r['blockers']), ', '.join('%s %d' % kv for kv in r['by_resolver'].items()), len(r['warnings'])))
    return 0 if r['verdict'] == 'GO' else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
