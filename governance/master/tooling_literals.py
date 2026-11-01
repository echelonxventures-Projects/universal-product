"""Hard-coding in the Master's own tooling (LXM-REQ-000240): count the literals in tool code that look like configuration
(files and paths, identifier formats, hashes, dates, numbers), per file and kind, and ratchet them down.
Usage: python3 -I tooling_literals.py <master root> [--baseline <file>] [--write-baseline <file>]
Exit 0 pass, 1 a count rose above the baseline. Kinds and their patterns come from tooling-literals.json."""
import ast, json, os, re, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from ids import X  # identifier formats and file names come from the registries (LXM-REQ-000240)


def scan(root):
    cfg = json.load(open(os.path.join(root, X('{@tooling_literals_json}')), encoding='utf-8'))
    f_cfg, counts, examples = cfg['files'], {}, {}
    for rule in cfg['kinds'].values():  # a kind may take its pattern from the identifier registry instead of repeating it
        if rule.get('from_ids'):
            reg = json.load(open(os.path.join(root, rule['from_ids']), encoding='utf-8'))
            marks = [ns['prefix'] for ns in reg['namespaces'].values()] + [ns['label'] for ns in reg['namespaces'].values()] + [reg['clause']['marker']]
            rule['pattern'] = '|'.join(re.escape(m) for m in sorted(set(marks), key=len, reverse=True))
    files = sorted(os.path.join(b, f) for b in f_cfg['roots'] if os.path.isdir(os.path.join(root, b)) for f in os.listdir(os.path.join(root, b))
                   if f.endswith(f_cfg['extension']) and not f.startswith(tuple(f_cfg['exclude_prefixes'])))
    for rel in files:
        tree = ast.parse(open(os.path.join(root, rel), encoding='utf-8').read())
        docs = {id(n.body[0].value) for n in ast.walk(tree) if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef))
                and n.body and isinstance(n.body[0], ast.Expr) and isinstance(getattr(n.body[0], 'value', None), ast.Constant)}
        for n in ast.walk(tree):
            if not isinstance(n, ast.Constant) or id(n) in docs:
                continue
            v, kind = n.value, None
            if isinstance(v, (int, float)) and not isinstance(v, bool) and v not in cfg['small_numbers']:
                kind = 'number'
            elif isinstance(v, str):
                for k, rule in cfg['kinds'].items():
                    if len(v) <= rule.get('max_length', len(v)) and (('pattern' in rule and re.search(rule['pattern'], v)) or any(re.fullmatch(p, v) for p in rule.get('fullmatch', []))):
                        kind = k
                        break
            if kind:
                key = '%s · %s' % (os.path.normpath(rel), kind)
                counts[key] = counts.get(key, 0) + 1
                examples.setdefault(key, []).append('%d: %r' % (n.lineno, v if not isinstance(v, str) else v[:60]))
    for key, d in cfg.get('declared', {}).items():  # a literal declared with its reason is not a finding
        if key in counts:
            counts[key] -= min(d['count'], counts[key])
            if not counts[key]:
                del counts[key]
    return counts, examples


def analyse(root, cfg=None):
    """The readiness adapter interface: every remaining literal is a finding (kind tooling-literal)."""
    counts, _ = scan(root)
    return {'counts': {'tooling-literal · ' + k: n for k, n in counts.items()}, 'summary': {'tooling_literals': sum(counts.values())}}


def main(argv):
    opt = lambda k: argv[argv.index(k) + 1] if k in argv else None
    counts, _ = scan(argv[1])
    total = sum(counts.values())
    if opt('--write-baseline'):
        json.dump(dict(sorted(counts.items())), open(opt('--write-baseline'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    if opt('--baseline'):
        base = json.load(open(opt('--baseline'), encoding='utf-8'))
        worse = sorted((k, base.get(k, 0), n) for k, n in counts.items() if n > base.get(k, 0))
        better = sum(base.values()) - total
        for k, a, b in worse:
            print('  worse  %s: %d -> %d' % (k, a, b))
        print('%d literals that look like configuration in the tooling (baseline %d); ratchet: %s' % (total, sum(base.values()), 'FAIL' if worse else 'pass'))
        return 1 if worse else 0
    print('%d literals that look like configuration in the tooling' % total)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
