"""Code adapter (CONTRACT.md §4, type implementation-artifact; LXM-REQ-000204, LXM-REQ-000229).
Usage: python3 -I code_adapter.py <code root> [--config code_adapter.json] [--baseline <file>] [--write-baseline <file>]
                                  [--json <out>] [--md <out> [--label <text>]] [--git-clean] [--trace <trace.txt>]

Checks that code is executed, tested, owned and not duplicated, using the repository's own registries and gates rather
than replacing them. It knows nothing about a particular repository: every path, file pattern and exemption comes from
the configuration file.

  executed   Every package script is reached from a CI workflow (directly, or through other scripts), or is listed as not a
             gate with a reason. Every test file is run by a command CI reaches.
  tested     Every module under the configured roots is reachable through require() from at least one test CI runs.
             Static reachability: a module a test loads is exercised in some way, not proven correct.
  owned      Every module is listed exactly once in the ownership registry, and every listed path exists.
  duplicate  No function body (at least the configured size) appears in two places (Knowledge Once, in code).
  clean      With --git-clean: the working tree has no uncommitted or untracked change after the run.
  traced     With --trace: every implementation and test path the Master's trace.txt names exists in the code, and every module is
             traced to at least one requirement (LXM-REQ-000204). Coverage is also shown per business domain, read from the
             repository's own domain registry.

With --baseline, the run fails if any finding count rises above the baseline (findings only go down).
Exit 0 pass, 1 ratchet failure, 2 usage error."""
import hashlib, json, os, re, subprocess, sys

sys.dont_write_bytecode = True  # a check never changes the Master directory (no __pycache__)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from ids import X  # identifier formats come from ids.json (LXM-REQ-000240)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from config_adapter import strip_comments, ratchet  # one comment stripper and one ratchet for every adapter


def read(root, rel):
    return open(os.path.join(root, rel), encoding='utf-8', errors='replace').read()


def walk(root, base, exts):
    p = os.path.join(root, base)
    if os.path.isfile(p):
        return [base]
    return sorted(os.path.relpath(os.path.join(a, f), root) for a, _, fs in os.walk(p) for f in fs if f.endswith(tuple(exts)))


# ---------- executed: the command graph from CI to scripts and files ----------

def command_graph(root, cfg):
    """What CI runs: workflow run lines -> package scripts (npm test / npm run x) -> node files, transitively."""
    c = cfg['commands']
    scripts = json.load(open(os.path.join(root, c['package']), encoding='utf-8')).get('scripts', {})
    ci_text = '\n'.join(read(root, f) for f in c['ci_workflows'])
    run_re = re.compile(c['script_call'])           # e.g. npm test / npm run <name>
    file_re = re.compile(c['file_call'])            # e.g. node <file>
    reached_scripts, files, todo = set(), set(), [ci_text]
    while todo:
        text = todo.pop()
        files |= set(file_re.findall(text))
        for name in run_re.findall(text):
            name = name or 'test'
            if name in scripts and name not in reached_scripts:
                reached_scripts.add(name); todo.append(scripts[name])
    return scripts, reached_scripts, files


# ---------- tested: require() reachability ----------

def requires(root, rel, src, cfg):
    """Modules a file loads through any configured loader (require, new Worker, ...): a relative path ("./x"), a path
    built with path.join (from __dirname, or from the repository root), or a directory prefix plus a variable
    ("./routes/" + f). A prefix load counts as loading the whole directory only when the configuration names that
    directory in dynamic_dirs; any other is unresolved and proves nothing."""
    here, loaders = os.path.dirname(rel), '|'.join(cfg['modules'].get('loaders', ['require\\(']))
    out, dirs = set(), set()
    for m in re.finditer(r'(?:%s)\s*["\'](\.{1,2}/[^"\']*)["\']\s*(\+)?' % loaders, src):
        (dirs if m.group(2) else out).add(os.path.normpath(os.path.join(here, m.group(1))))
    for m in re.finditer(r'(?:%s)\s*[\w$]+\.join\(([^)]*)\)' % loaders, src):  # path.join, or path imported under another name
        args = m.group(1)
        parts = re.findall(r'["\']([^"\']+)["\']', args)
        if parts:
            out.add(os.path.normpath(os.path.join(here if '__dirname' in args else '', *parts)))
    res = set()
    for p in out:
        for cand in (p, p + '.js', os.path.join(p, 'index.js')):
            if os.path.isfile(os.path.join(root, cand)):
                res.add(cand); break
    for d in dirs:
        if d.rstrip('/') + '/' in cfg['modules'].get('dynamic_dirs', []) and os.path.isdir(os.path.join(root, d)):
            res |= {os.path.join(d, f) for f in os.listdir(os.path.join(root, d)) if f.endswith('.js')}
        else:
            UNRESOLVED.add((rel, d.rstrip('/') + '/'))
    return res


UNRESOLVED = set()  # (file, directory prefix) of dynamic loads the configuration does not resolve


# ---------- duplicate: function bodies ----------

def bodies(src):
    """Bodies of named functions, methods and arrow functions with a block, found by brace matching outside strings."""
    out = []
    for m in re.finditer(r'(?:function\s*\*?\s*[\w$]*\s*\([^()]*\)|=>)\s*\{', src):
        i, depth, n, state = m.end(), 1, len(src), None
        while i < n and depth:
            ch = src[i]
            if state:
                if ch == '\\':
                    i += 1
                elif ch == state:
                    state = None
            elif ch in '"\'`':
                state = ch
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
            i += 1
        out.append((src.count('\n', 0, m.start()) + 1, src[m.end():i - 1]))
    return out


def analyse(root, cfg):
    findings, report = [], {}
    # executed
    scripts, reached, ran_files = command_graph(root, cfg)
    exempt = cfg['commands'].get('not_gates', {})
    unexecuted = sorted(s for s in scripts if s not in reached and s not in exempt)
    tests = [f for base in cfg['tests']['roots'] for f in walk(root, base, cfg['tests']['extensions'])
             if not any(re.fullmatch(p, os.path.basename(f)) for p in cfg['tests'].get('helpers', []))]
    unwired = sorted(f for f in tests if f not in ran_files)
    findings += [('unexecuted-script', s) for s in unexecuted] + [('unwired-test', f) for f in unwired]
    # tested
    mods = [f for base in cfg['modules']['roots'] for f in walk(root, base, cfg['modules']['extensions'])
            if not any(f.startswith(x) for x in cfg['modules'].get('exclude', []))]
    srcs = {f: strip_comments(read(root, f)) for f in set(mods) | {t for t in tests if t in ran_files}}
    seen, todo = set(), [t for t in tests if t in ran_files]
    while todo:
        f = todo.pop()
        if f in seen:
            continue
        seen.add(f)
        if f not in srcs and os.path.isfile(os.path.join(root, f)) and f.endswith('.js'):
            srcs[f] = strip_comments(read(root, f))
        todo += [r for r in requires(root, f, srcs.get(f, ''), cfg) if r not in seen]
    untested = sorted(m for m in mods if m not in seen)
    unresolved = sorted('%s loads %s<variable>' % u for u in UNRESOLVED); UNRESOLVED.clear()
    findings += [('untested-module', m) for m in untested]
    # owned
    o = cfg['ownership']
    reg = json.load(open(os.path.join(root, o['registry']), encoding='utf-8'))
    listed = [e[o['path_field']] for e in reg[o['list']]]
    counts = {p: listed.count(p) for p in set(listed)}
    unowned = sorted(m for m in mods if counts.get(m, 0) == 0)
    multiple = sorted(p for p, n in counts.items() if n > 1)
    missing = sorted(p for p in counts if not os.path.exists(os.path.join(root, p)))
    findings += [('unowned', m) for m in unowned] + [('owned-twice', p) for p in multiple] + [('owner-lists-missing-file', p) for p in missing]
    # duplicate
    d = cfg['duplicates']
    groups = {}
    for f in mods:
        for line, body in bodies(srcs[f]):
            norm = re.sub(r'\s+', ' ', body).strip()
            if len(norm) >= d['min_chars'] and body.count('\n') + 1 >= d['min_lines']:
                groups.setdefault(hashlib.sha256(norm.encode()).hexdigest()[:12], []).append((f, line))
    dups = {h: sorted(set(v)) for h, v in groups.items() if len({f for f, _ in v}) > 1 or len(v) > 1}
    findings += [('duplicate', h, f) for h, v in dups.items() for f, _ in v]
    # kernel derivation (LXM-REQ-000232): every stored entity type derived through the kernel, or exempted with a reason
    kd = None
    kc = cfg.get('kernel')
    if kc:
        tables = []
        for f in kc['schema_files']:
            tables += re.findall(kc['table_pattern'], read(root, f))
        kernel = sorted({t for t in tables if t.startswith(kc['kernel_prefix'])})
        k_exempt = kc.get('exempt', {})
        outside = sorted({t for t in tables if not t.startswith(kc['kernel_prefix']) and t not in k_exempt})
        kd = {'tables': len(set(tables)), 'kernel': kernel, 'exempt': sorted(set(k_exempt) & set(tables)), 'outside': outside}
        findings += [('outside-kernel', t) for t in outside]
    # named values (LXM-REQ-000238 and the like): literals the code must not carry, such as environment names; every rule,
    # root, pattern and exemption comes from the configuration
    nv = {}
    for rule in cfg.get('named_values', []):
        files = [f for base in rule['roots'] for f in walk(root, base, rule['extensions'])
                 if not any(f.startswith(x) for x in rule.get('exclude', []))]
        pats = list(rule.get('patterns', []))
        for nf in rule.get('names_from', []):  # names taken from registries, never listed in the rule (LXM-REQ-000239)
            reg = json.load(open(os.path.join(root if nf['in'] == 'code' else os.path.dirname(os.path.abspath(__file__)), nf['file']), encoding='utf-8'))
            for path in nf['paths']:
                nodes = [reg]
                for part in path.split('.'):
                    nodes = [v for n in nodes for v in ((n.values() if isinstance(n, dict) else n) if part == '*' else [n.get(part)] if isinstance(n, dict) else [])]
                for v in nodes:
                    for name in (v if isinstance(v, list) else [v]):
                        if isinstance(name, str) and name.strip():
                            pats.append('(?i)(?<![\\w])%s(?![\\w])' % re.escape(name))
        hits = []
        for f in files:
            src = strip_comments(read(root, f))
            for pat in pats:
                for m in re.finditer(pat, src):
                    hits.append('%s:%d %s' % (f, src.count('\n', 0, m.start()) + 1, re.sub(r'\s+', ' ', m.group(0))[:60]))
        hits = sorted(set(hits))
        nv[rule['finding']] = {'sites': len(hits), 'files': len({h.split(':')[0] for h in hits}), 'list': hits}
        findings += [(rule['finding'], h) for h in hits]
    # traced
    tr = None
    if cfg.get('_trace'):
        import importlib.util
        spec = importlib.util.spec_from_file_location('lxm_build', os.path.join(os.path.dirname(os.path.abspath(cfg['_trace'])), X('{@build_py}')))
        build = importlib.util.module_from_spec(spec); spec.loader.exec_module(build)  # the Master's own parser for trace.txt
        _, trace = build.parse_trace(open(cfg['_trace'], encoding='utf-8').read())
        by_mod, missing_paths = {}, []
        for rid, t in trace.items():
            for kind in ('impl', 'spec', 'test'):
                for p in [x for x in t.get(kind, '').split(', ') if x]:
                    if not os.path.exists(os.path.join(root, p)):
                        missing_paths.append('%s %s %s' % (rid, kind, p))
                    if kind == 'impl':
                        by_mod.setdefault(p, []).append(rid)
        untraced = sorted(m for m in mods if m not in by_mod)
        dc = cfg.get('domains')
        per_domain = {}
        if dc:
            for dom in json.load(open(os.path.join(root, dc['registry']), encoding='utf-8'))[dc['list']]:
                files = dom
                for part in dc['files'].split('.'):
                    files = files.get(part, {}) if isinstance(files, dict) else {}
                files = [f for f in (files or []) if f in mods]
                per_domain[dom[dc['key']]] = {'modules': len(files), 'traced': sum(f in by_mod for f in files)}
        tr = {'requirements': len(trace), 'gaps': sorted(r for r, t in trace.items() if not t.get('impl')), 'missing_paths': missing_paths,
              'traced_modules': len(mods) - len(untraced), 'untraced_modules': untraced, 'by_module': {m: sorted(set(v)) for m, v in sorted(by_mod.items())},
              'per_domain': per_domain}
        findings += [('trace-missing-path', p) for p in missing_paths] + [('untraced-module', m) for m in untraced]
    # clean
    dirty = None
    if cfg.get('_git_clean'):
        r = subprocess.run(['git', '--no-optional-locks', 'status', '--porcelain=v1', '--untracked-files=all'], cwd=root, capture_output=True, text=True)
        dirty = [l for l in r.stdout.split('\n') if l.strip()] if r.returncode == 0 else ['(not a git checkout: %s)' % r.stderr.strip()[:80]]
        findings += [('dirty', l) for l in dirty]
    out = {}
    for k in findings:
        key = ' · '.join(k)
        out[key] = out.get(key, 0) + 1
    report = {'summary': {'scripts': len(scripts), 'scripts_reached_from_ci': len(reached), 'not_gates': len(exempt), 'unexecuted_scripts': unexecuted,
                          'tests': len(tests), 'unwired_tests': unwired, 'modules': len(mods), 'tested_modules': len(mods) - len(untested),
                          'untested_modules': untested, 'unresolved_dynamic_loads': unresolved, 'unowned': unowned, 'owned_twice': multiple, 'owner_lists_missing_file': missing,
                          'duplicate_groups': len(dups), 'duplicate_sites': sum(len(v) for v in dups.values()), 'dirty': dirty, 'trace': tr, 'kernel': kd, 'named_values': nv},
              'duplicates': dups, 'counts': dict(sorted(out.items()))}
    return report


def markdown(rep, label):
    s = rep['summary']
    li = lambda xs: ', '.join('`%s`' % x for x in xs) or 'None.'
    out = ['# Code findings: %s' % label, '',
           '- Package scripts: %d, of which %d are reached from CI and %d are listed as not gates; **not executed by CI:** %s' % (
               s['scripts'], s['scripts_reached_from_ci'], s['not_gates'], li(s['unexecuted_scripts'])),
           '- Test files: %d; **not run by any command CI reaches:** %s' % (s['tests'], li(s['unwired_tests'])),
           '- Modules: %d; reachable from a test CI runs: %d. Static reachability shows a module is loaded by a test, not that it is correct.' % (
               s['modules'], s['tested_modules']),
           '- Ownership registry: %d modules unowned, %d owned twice, %d listed paths missing.' % (
               len(s['unowned']), len(s['owned_twice']), len(s['owner_lists_missing_file'])),
           '- Duplicated function bodies: %d groups, %d sites.' % (s['duplicate_groups'], s['duplicate_sites'])]
    if s['dirty'] is not None:
        out.append('- Working tree: %s' % ('clean' if not s['dirty'] else '%d uncommitted or untracked paths' % len(s['dirty'])))
    k = s.get('kernel')
    if k:
        out.append(X('- Kernel derivation ({req=000232}): %d tables; %d are the kernel, %d exempted with a reason, **%d hold entity types outside the kernel**.') % (
            k['tables'], len(k['kernel']), len(k['exempt']), len(k['outside'])))
    t = s.get('trace')
    if t:
        out.append('- Traceability: %d requirements traced, %d known gaps; modules traced to a requirement: %d of %d; traced paths missing in the code: %d.' % (
            t['requirements'] - len(t['gaps']), len(t['gaps']), t['traced_modules'], s['modules'], len(t['missing_paths'])))
    out += ['', '## Modules no test reaches (%d)' % len(s['untested_modules']), '', li(s['untested_modules']),
            '', 'Dynamic loads the configuration does not resolve (the modules they load are not counted as tested): %s' % li(s['unresolved_dynamic_loads']),
            '', '## Modules missing from the ownership registry (%d)' % len(s['unowned']), '', li(s['unowned']),
            '', '## Listed in the ownership registry but missing on disk (%d)' % len(s['owner_lists_missing_file']), '', li(s['owner_lists_missing_file']),
            '', '## Duplicated function bodies', '', '| Group | Sites |', '|---|---|']
    out += ['| `%s` | %s |' % (h, ', '.join('`%s:%d`' % fl for fl in v)) for h, v in sorted(rep['duplicates'].items(), key=lambda kv: -len(kv[1]))]
    for name, v in sorted((s.get('named_values') or {}).items()):
        out += ['', '## Named values: %s (%d sites in %d files)' % (name, v['sites'], v['files']), ''] + ['- `%s`' % h for h in v['list']]
    if t:
        out += ['', '## Traceability by business domain', '', '| Domain | Modules | Traced to a requirement |', '|---|---|---|']
        out += ['| %s | %d | %d |' % (k, v['modules'], v['traced']) for k, v in sorted(t['per_domain'].items(), key=lambda kv: (kv[1]['traced'] - kv[1]['modules'], kv[0]))]
        out += ['', '## Traced paths missing in the code (%d)' % len(t['missing_paths']), '', li(t['missing_paths']),
                '', '## Modules no requirement traces (%d)' % len(t['untraced_modules']), '', li(t['untraced_modules'])]
    return '\n'.join(out) + '\n'


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    opt = lambda k: argv[argv.index(k) + 1] if k in argv else None
    root = argv[1]
    cfg = json.load(open(opt('--config') or os.path.join(HERE, X('{@code_adapter_json}')), encoding='utf-8'))
    cfg['_git_clean'] = '--git-clean' in argv
    cfg['_trace'] = opt('--trace')
    rep = analyse(root, cfg)
    if opt('--json'):
        json.dump(rep, open(opt('--json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    if opt('--md'):
        open(opt('--md'), 'w', encoding='utf-8').write(markdown(rep, opt('--label') or root))
    if opt('--write-baseline'):
        json.dump(rep['counts'], open(opt('--write-baseline'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False, sort_keys=True)
    s = rep['summary']
    print('scripts %d (CI reaches %d, not gates %d, unexecuted %d); tests %d (unwired %d); modules %d (tested %d, unowned %d); '
          'duplicate bodies %d groups / %d sites%s' % (
              s['scripts'], s['scripts_reached_from_ci'], s['not_gates'], len(s['unexecuted_scripts']), s['tests'], len(s['unwired_tests']),
              s['modules'], s['tested_modules'], len(s['unowned']), s['duplicate_groups'], s['duplicate_sites'],
              '' if s['dirty'] is None else '; working tree %s' % ('clean' if not s['dirty'] else '%d dirty paths' % len(s['dirty'])))
          + ('' if not s.get('kernel') else '; tables outside the kernel %d of %d' % (len(s['kernel']['outside']), s['kernel']['tables']))
          + ('' if not s['trace'] else '; traced modules %d of %d, missing traced paths %d, known gaps %d' % (
              s['trace']['traced_modules'], s['modules'], len(s['trace']['missing_paths']), len(s['trace']['gaps']))))
    if opt('--baseline'):
        worse, better = ratchet(rep['counts'], json.load(open(opt('--baseline'), encoding='utf-8')))
        for k, (a, b) in sorted(better.items()):
            print('  better  %s: %d -> %d (record it with --write-baseline)' % (k, a, b))
        for k, (a, b) in sorted(worse.items()):
            print('  WORSE   %s: %d -> %d' % (k, a, b))
        print('ratchet: %s' % ('FAIL, %d finding(s) rose' % len(worse) if worse else 'pass'))
        return 1 if worse else 0
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
