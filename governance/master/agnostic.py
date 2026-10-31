"""Agnostic tooling check (LXM-REQ-000239): no agent, tool, person or host is named in the tooling's code or configuration
outside its registry. The names come from the registries themselves, so a newly registered actor or host is covered at once.
Usage: python3 -I agnostic.py <master root>   Exit 0 clean, 1 a registered name appears outside its registry."""
import json, os, re, sys
sys.dont_write_bytecode = True


def names(root, cfg):
    out = set()
    for reg, paths in cfg['registries'].items():
        data = json.load(open(os.path.join(root, reg), encoding='utf-8'))
        for p in paths:
            parts = p.split('.')
            def walk(node, i):
                if i == len(parts):
                    out.update([node] if isinstance(node, str) else [x for x in node if isinstance(x, str)] if isinstance(node, list) else [])
                    return
                if parts[i] == '*':
                    if isinstance(node, dict):
                        if i == len(parts) - 1:
                            out.update(node.keys())
                        else:
                            for v in node.values():
                                walk(v, i + 1)
                elif isinstance(node, dict) and parts[i] in node:
                    walk(node[parts[i]], i + 1)
            walk(data, 0)
    return sorted(n for n in out if n.strip())


def files(root, cfg):
    s = cfg['scan']
    for base in s['roots']:
        d = os.path.join(root, base)
        walker = os.walk(d) if base in s.get('recursive_roots', []) else [(d, [], os.listdir(d))]
        for b, _, fs in walker:
            for f in sorted(fs):
                rel = os.path.relpath(os.path.join(b, f), root)
                if os.path.splitext(f)[1] in s['extensions'] and os.path.isfile(os.path.join(root, rel)) and rel not in cfg['registry_files'] \
                        and not any(rel.startswith(a) for a in cfg['adapter_dirs']) and rel not in cfg['exempt'] and '__pycache__' not in rel:
                    yield rel


def check(root):
    cfg = json.load(open(os.path.join(root, 'agnostic.json'), encoding='utf-8'))
    ns = names(root, cfg)
    pat = re.compile(r'(?<![\w-])(%s)(?![\w-])' % '|'.join(re.escape(n) for n in sorted(ns, key=len, reverse=True)), re.I)
    hits = []
    for rel in sorted(set(files(root, cfg))):
        for i, line in enumerate(open(os.path.join(root, rel), encoding='utf-8', errors='replace'), 1):
            for m in pat.finditer(line):
                hits.append('%s:%d %s' % (rel, i, m.group(1)))
    return ns, hits


if __name__ == '__main__':
    ns, hits = check(sys.argv[1])
    print('%d registered names; %d occurrence(s) outside the registries%s' % (len(ns), len(hits), ''.join('\n  ' + h for h in hits[:40])))
    sys.exit(1 if hits else 0)
