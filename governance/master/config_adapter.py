"""Configuration adapter (CONTRACT.md §4, type configuration; LXM-REQ-000074, LXM-REQ-000198, LXM-REQ-000202).
Usage: python3 -I config_adapter.py <code root> [--config config_adapter.json] [--baseline <file>] [--write-baseline <file>] [--json <out>] [--md <out> [--label <text>]]
                                    [--runtime-trace <file> [--runtime-declaration <id>]]

Checks a code tree against its declared configuration, and knows nothing about any particular repository: the declaration
files, code roots, exclusions and matching rules all come from the configuration file.

Declarations are trees (the leaves of a JSON document below a pointer) or names (listed in documents, such as environment
variables, and read through a configured pattern; a name code reads but no document declares is reported as undeclared).
Every file under the configured source folders must be declared or listed as not declared, with a reason; any other
is reported as unaccounted, so no configuration source is silently left out.

For every declared setting, it reports:
  reader   explicit  code names the setting's path (parent.key, or parent["key"])
           plausible code accesses the key as a property of something (an alias such as t.key, ["key"], or a
                     destructured { key }), or iterates or dynamically indexes a group above it; not proven
           none      the key is never accessed in code, by any name: strong evidence that nothing reads it
  copies   the setting's configured value written as a literal in code (comments ignored), classified as
           branch (=== !== case), fallback (|| ?? or a default), literal, or embedded (inside longer text). A copy is hard-coding: changing the
           setting would not change that behaviour.

Static evidence never proves that an engine applies a value (LXM-REQ-000198). With --runtime-trace (paths read by running code,
recorded by the settings engine under LX_SETTINGS_TRACE), each traced setting becomes runtime (read by running code) or
serialized (only sent out, e.g. to a browser); a traced setting never read at runtime is reported as runtime-unread. With --baseline, the run fails if any finding count rises above the baseline
(the ratchet: findings only go down). Exit 0 pass, 1 ratchet failure, 2 usage or configuration error."""
import json, os, re, sys

sys.dont_write_bytecode = True  # a check never changes the Master directory (no __pycache__)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from ids import X  # identifier formats and file names come from the registries (LXM-REQ-000240)

HERE = os.path.dirname(os.path.abspath(__file__))


def strip_comments(src):
    """Blank out // and /* */ comments in JavaScript, keeping strings, template literals and line numbers intact."""
    out, i, n, state = [], 0, len(src), None
    while i < n:
        c = src[i]
        if state is None:
            if c in '\'"`':
                state = c
            elif src.startswith('//', i):
                j = src.find('\n', i)
                j = n if j < 0 else j
                out.append(' ' * (j - i)); i = j; continue
            elif src.startswith('/*', i):
                j = src.find('*/', i + 2)
                j = n if j < 0 else j + 2
                out.append(re.sub(r'[^\n]', ' ', src[i:j])); i = j; continue
        elif c == '\\':
            out.append(src[i:i + 2]); i += 2; continue
        elif c == state or (c == '\n' and state != '`'):
            state = None
        out.append(c); i += 1
    return ''.join(out)


def leaves(obj, prefix=()):
    if isinstance(obj, dict) and obj:
        for k, v in obj.items():
            yield from leaves(v, prefix + (k,))
    else:
        yield prefix, obj


def pointer(doc, ptr):
    for part in [p for p in ptr.split('/') if p]:
        doc = doc[part]
    return doc


def code_files(root, cfg):
    c = cfg['code']
    for base in c['roots']:
        p = os.path.join(root, base)
        found = [p] if os.path.isfile(p) else sorted(os.path.join(a, f) for a, _, fs in os.walk(p) for f in fs)
        for f in found:
            rel = os.path.relpath(f, root)
            if f.endswith(tuple(c['extensions'])) and not any(rel.startswith(x) for x in c['exclude']):
                yield rel


def distinctive(v, rules, as_word=False):
    """A value specific enough that finding it in code means it was copied, not a common word. A value configured to be
    matched as a word (e.g. a brand name) only needs the minimum length."""
    if not isinstance(v, str) or len(v.strip()) < rules['min_length'] or v.strip() != v:
        return False
    if as_word:
        return True
    if rules.get('skip_single_lowercase_word') and re.fullmatch(r'[a-z][a-z0-9_-]*', v):
        return False
    return not any(re.fullmatch(p, v) for p in rules.get('skip_patterns', []))


def classify_use(line, start, end):
    """How code uses a literal at line[start:end] (quotes included): logic decides on it, falls back to it, or just names it."""
    before, after = line[:start].rstrip(), line[end:].lstrip()
    if re.search(r'(===|!==|==|!=|\bcase)$', before) or re.match(r'(===|!==|==|!=)', after):
        return 'branch'
    if re.search(r'(\|\||\?\?|\bDEFAULT|[(,{]\s*[\w$]+\s*=)$', before, re.I):  # a default parameter or destructuring default, not an assignment
        return 'fallback'
    return 'literal'


def tree_settings(root, decl):
    """Leaves of a declaration document, below its pointer, without commentary keys."""
    doc = pointer(json.load(open(os.path.join(root, decl['file']), encoding='utf-8')), decl.get('pointer', ''))
    by = decl.get('index_lists_by')
    if by:  # a list of records, each named by one of its fields, is read as a mapping from that name to the record
        def index(o):
            if isinstance(o, list) and o and all(isinstance(x, dict) and isinstance(x.get(by), str) for x in o):
                return {x[by]: index({k: v for k, v in x.items() if k != by}) for x in o}
            return {k: index(v) for k, v in o.items()} if isinstance(o, dict) else o
        doc = index(doc)
    skip = set(decl.get('skip_keys', []))
    return [(p, v) for p, v in leaves(doc) if not skip & set(p)]


ID = r'[A-Za-z_$][\w$]*'


class Index:
    """Each code file read once: member pairs (.parent.key, parent["key"]), keys accessed in any way, names iterated or
    indexed dynamically (from the configured generic_consumers patterns), and every text between two quote characters."""
    def __init__(self, files, cfg):
        self.files, self.pairs, self.access, self.iterated, self.quoted = files, {}, {}, {}, {}
        pair_res = [re.compile(r'(?=\.\s*(%s)\s*\??\.\s*(%s))' % (ID, ID)), re.compile(r'(%s)\s*\[\s*["\'`]([^"\'`\n]+)["\'`]\s*\]' % ID)]
        access_res = [re.compile(r'\.\s*(%s)' % ID), re.compile(r'\[\s*["\'`]([^"\'`\n]+)["\'`]\s*\]')]
        gen_res = [re.compile(g.replace('\\b{name}', '\\b(%s)' % ID).replace('{name}', '(%s)' % ID)) for g in cfg['generic_consumers']]
        quote_re = re.compile(r'(?=(["\'`])([^"\'`\n]+)(["\'`]))')
        for f, src in files.items():
            for r in pair_res:
                for m in r.finditer(src):
                    self.pairs.setdefault((m.group(1), m.group(2)), set()).add(f)
            for r in access_res:
                for m in r.finditer(src):
                    self.access.setdefault(m.group(1), set()).add(f)
            for m in re.finditer(r'\{([^{}]*)\}\s*=', src):  # destructuring
                for k in re.findall(ID, m.group(1)):
                    self.access.setdefault(k, set()).add(f)
            for r in gen_res:
                for m in r.finditer(src):
                    self.iterated.setdefault(m.group(1), set()).add(f)
            for ln, line in enumerate(src.split('\n'), 1):
                for m in quote_re.finditer(line):
                    self.quoted.setdefault(m.group(2), []).append((f, ln, line, m.start(), m.start() + len(m.group(2)) + 2))


def tree_reader(path, idx):
    parent, key = (path[-2] if len(path) > 1 else None), path[-1]
    explicit = idx.pairs.get((parent, key), set()) if parent else set()
    plausible = set(idx.access.get(key, ())) | {f for anc in path[:-1] for f in idx.iterated.get(anc, ())} | \
        {q[0] for anc in path[:-1] for q in idx.quoted.get(anc, ())}  # a group fetched by its name, e.g. listOf("group")
    return ('explicit' if explicit else 'plausible' if plausible else 'none'), sorted(explicit or plausible)[:5]


def copies_of(value, as_word, idx):
    """Every place code writes the value. As a word (case-insensitive) it also counts inside identifiers, text and hosts
    (NAME_KEY, "NAME Support", name.example)."""
    if not as_word:
        return [{'file': f, 'line': ln, 'use': classify_use(line, a, b)} for f, ln, line, a, b in idx.quoted.get(value, [])]
    pat, out = re.compile(r'(?<![A-Za-z0-9])%s(?![A-Za-z0-9])' % re.escape(value), re.I), []
    for f, src in idx.files.items():
        for ln, line in enumerate(src.split('\n'), 1):
            for m in pat.finditer(line):
                a, b = m.start(), m.end()
                if a and b < len(line) and line[a - 1] in '"\'`' and line[b] == line[a - 1]:  # the whole string literal is the value
                    out.append({'file': f, 'line': ln, 'use': classify_use(line, a - 1, b + 1)})
                else:
                    out.append({'file': f, 'line': ln, 'use': 'embedded'})
    return out


def analyse(root, cfg):
    files = {f: strip_comments(open(os.path.join(root, f), encoding='utf-8', errors='replace').read()) for f in code_files(root, cfg)}
    idx = Index(files, cfg)
    rules = cfg['distinct']
    word_paths = [re.compile(p) for p in cfg.get('match_as_word', [])]
    settings, findings = [], []
    for decl in cfg['declarations']:
        if decl.get('kind', 'tree') == 'names':  # names declared in documents (e.g. environment variables), read by a pattern
            declared = set()
            for df in decl['files']:
                declared |= set(re.findall(decl['pattern'], open(os.path.join(root, df), encoding='utf-8').read(), re.M))
            read = {}
            for f, src in files.items():
                for n in re.findall(decl['discover'], src):
                    read.setdefault(n, set()).add(f)
            for n in sorted(declared | set(read)):
                by_name = sorted({q[0] for q in idx.quoted.get(n, ())} | idx.access.get(n, set()))  # e[cfg.urlEnv], or an alias: e.NAME
                st = ('explicit' if n in read else 'plausible' if by_name else 'none') if n in declared else 'undeclared'
                read.setdefault(n, set()).update(by_name if n in declared and n not in read else ())
                settings.append({'declaration': decl['id'], 'setting': n, 'reader': st, 'readers': sorted(read.get(n, ()))[:5], 'copies': []})
                if st == 'none':
                    findings.append(('unread', decl['id'] + ':' + n, ''))
                elif st == 'undeclared':
                    findings.append(('undeclared', decl['id'] + ':' + n, ''))
            continue
        for path, value in tree_settings(root, decl):
            name = '.'.join(path)
            reader, readers = tree_reader(path, idx)
            as_word = any(p.fullmatch(name) for p in word_paths)
            copies = copies_of(value, as_word, idx) if distinctive(value, rules, as_word) else []
            settings.append({'declaration': decl['id'], 'setting': name, 'reader': reader, 'readers': readers, 'copies': copies})
            if reader == 'none':
                findings.append(('unread', decl['id'] + ':' + name, ''))
            for cp in copies:
                findings.append(('copy-' + cp['use'], decl['id'] + ':' + name, cp['file']))
    rt = cfg.get('_runtime')  # a runtime read trace: {"path": ..., "how": "read" | "serialized"} per line, for one declaration
    if rt:
        seen = {}
        for line in open(rt['file'], encoding='utf-8'):
            if line.strip():
                e = json.loads(line); seen.setdefault(e['path'], set()).add(e['how'])
        for s in settings:
            if s['declaration'] != rt['declaration']:
                continue
            hows = seen.get(s['setting'], set())
            s['static_reader'] = s['reader']
            s['reader'] = 'runtime' if 'read' in hows else 'serialized' if 'serialized' in hows else s['reader']
            if 'read' not in hows:
                findings.append(('runtime-unread', s['declaration'] + ':' + s['setting'], ''))
    src_cfg = cfg.get('sources', {})
    declared_files = {d['file'] for d in cfg['declarations'] if 'file' in d}
    unaccounted = []
    for base in src_cfg.get('account_for', []):
        for f in sorted(os.listdir(os.path.join(root, base))):
            rel = os.path.join(base, f)
            if f.endswith(tuple(src_cfg.get('extensions', ['.json']))) and rel not in declared_files and rel not in src_cfg.get('not_declared', {}):
                unaccounted.append(rel); findings.append(('unaccounted', rel, ''))
    counts = {}
    for k in findings:
        key = ' · '.join(x for x in k if x)
        counts[key] = counts.get(key, 0) + 1
    summary = {'settings': len(settings), 'files': len(files), 'declarations': len(cfg['declarations']),
               'reader': {r: sum(s['reader'] == r for s in settings) for r in ('runtime', 'serialized', 'explicit', 'plausible', 'none', 'undeclared')},
               'runtime_trace': rt and {'declaration': rt['declaration'], 'settings': sum(s['declaration'] == rt['declaration'] for s in settings)},
               'copies': {u: sum(cp['use'] == u for s in settings for cp in s['copies']) for u in ('branch', 'fallback', 'literal', 'embedded')},
               'settings_with_copies': sum(bool(s['copies']) for s in settings),
               'distinct_sites': {'copy-' + u: len({(c['file'], c['line']) for s in settings for c in s['copies'] if c['use'] == u})
                                  for u in ('branch', 'fallback', 'literal', 'embedded')},
               'sources': {'declared': len(declared_files), 'not_declared': len(src_cfg.get('not_declared', {})), 'unaccounted': unaccounted}}
    return {'summary': summary, 'settings': settings, 'counts': dict(sorted(counts.items()))}


def markdown(rep, root, label):
    """The findings as a work list: what to fix first, then what to declare, then what is unproven."""
    s, esc = rep['summary'], lambda t: t.replace('|', '\\|')
    line = lambda f, n: esc(open(os.path.join(root, f), encoding='utf-8', errors='replace').read().split('\n')[n - 1].strip()[:140])
    out = ['# Configuration findings: %s' % label, '',
           '- %d settings from %d declarations, %d code files. Sources: %d declared, %d classified as not configuration, %d unaccounted.' % (
               s['settings'], s['declarations'], s['files'], s['sources']['declared'], s['sources']['not_declared'], len(s['sources']['unaccounted'])),
           '- Readers: %d explicit, %d plausible (alias, iteration or by name; **not proven**), %d never accessed, %d read but undeclared.' % (
               s['reader']['explicit'], s['reader']['plausible'], s['reader']['none'], s['reader']['undeclared']),
           ]
    sites = {}
    for st in rep['settings']:
        for c in st['copies']:
            sites.setdefault((c['file'], c['line'], c['use']), []).append('%s:%s' % (st['declaration'], st['setting']))
    n_use = lambda u: sum(1 for k in sites if k[2] == u)
    out += ['- Values also written in code: %d settings, at %d distinct sites: %d fallback, %d literal, %d embedded. A site shared by settings '
            'with the same value is counted and listed once.' % (s['settings_with_copies'], len(sites), n_use('fallback'), n_use('literal'), n_use('embedded')), '']
    out += ['## 1. Fallbacks and literals: behaviour that ignores its setting', '', '| Setting | Use | Location | Code |', '|---|---|---|---|']
    out += ['| %s | %s | `%s:%d` | `%s` |' % (', '.join(v), u, f, n, line(f, n)) for (f, n, u), v in sorted(sites.items()) if u != 'embedded']
    emb = {}
    for (f, n, u) in sites:
        if u == 'embedded':
            emb[f] = emb.get(f, 0) + 1
    out += ['', '## 2. Embedded in text, identifiers and hosts', '', '| File | Sites |', '|---|---|'] + ['| `%s` | %d |' % kv for kv in sorted(emb.items())]
    und = [x['setting'] for x in rep['settings'] if x['reader'] == 'undeclared']
    out += ['', '## 3. Read by code but declared nowhere (%d)' % len(und), '', ', '.join('`%s`' % x for x in und) or 'None.']
    none = ['%s:%s' % (x['declaration'], x['setting']) for x in rep['settings'] if x['reader'] == 'none']
    out += ['', '## 4. Declared but never accessed (%d)' % len(none), '', ', '.join('`%s`' % x for x in none) or 'None.']
    if s['sources']['unaccounted']:
        out += ['', '## 5. Configuration sources not accounted for', ''] + ['- `%s`' % x for x in s['sources']['unaccounted']]
    return '\n'.join(out) + '\n'


def ratchet(counts, baseline):
    """Findings only go down: a key that is new, or whose count rose, fails."""
    worse = {k: (baseline.get(k, 0), v) for k, v in counts.items() if v > baseline.get(k, 0)}
    better = {k: (v, counts.get(k, 0)) for k, v in baseline.items() if counts.get(k, 0) < v}
    return worse, better


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    opt = lambda k: argv[argv.index(k) + 1] if k in argv else None
    root = argv[1]
    cfg = json.load(open(opt('--config') or os.path.join(HERE, X('{@config_adapter_json}')), encoding='utf-8'))
    if opt('--runtime-trace'):
        cfg['_runtime'] = {'file': opt('--runtime-trace'), 'declaration': opt('--runtime-declaration') or cfg['declarations'][0]['id']}
    rep = analyse(root, cfg)
    if opt('--json'):
        json.dump(rep, open(opt('--json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    if opt('--md'):
        open(opt('--md'), 'w', encoding='utf-8').write(markdown(rep, root, opt('--label') or root))
    if opt('--write-baseline'):
        json.dump(rep['counts'], open(opt('--write-baseline'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False, sort_keys=True)
    s = rep['summary']
    if s['runtime_trace']:
        print('runtime trace (%s): %d of %d settings read by running code, %d only serialized' % (
            s['runtime_trace']['declaration'], s['reader']['runtime'], s['runtime_trace']['settings'], s['reader']['serialized']))
    print('%d settings from %d declarations in %d code files: reader explicit %d, plausible %d, none %d, read but undeclared %d; '
          '%d settings copied into code (%d branch, %d fallback, %d literal, %d embedded); sources declared %d, catalogues %d, unaccounted %d' % (
        s['settings'], s['declarations'], s['files'], s['reader']['explicit'], s['reader']['plausible'], s['reader']['none'], s['reader']['undeclared'], s['settings_with_copies'],
        s['copies']['branch'], s['copies']['fallback'], s['copies']['literal'], s['copies']['embedded'],
        s['sources']['declared'], s['sources']['not_declared'], len(s['sources']['unaccounted'])))
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
