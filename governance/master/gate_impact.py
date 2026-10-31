"""Gate governance (gap 1): before a gate change is adopted, classify every contribution under the current gate and under the
proposed one, on the same canonical state, and report every clause whose classification changes.
Usage: python3 -I gate_impact.py <root> <proposed assimilate.py> [<proposed lexicon.txt>]   Exit 0 no change, 1 changes reported."""
import glob, importlib.util, os, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from ids import X  # identifier formats come from ids.json (LXM-REQ-000240)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def classify_all(gate, root, lexicon):
    lex = gate.Lexicon(lexicon); recs = gate.blocks(gate.read(os.path.join(root, 'reqs.txt'))); gate.index(recs, lex)
    out = {}
    for p in sorted(glob.glob(os.path.join(root, 'intake', X('{src-}*'), '*.ctb'))):
        c = gate.receive(p)
        if c.get('kind', 'requirement') != 'requirement' or not c.get('text'):
            continue
        for n, t in enumerate(gate.sentences(c['text']), 1):
            k = gate.classify(t, recs, lex, set())
            out['%s#%d' % (os.path.relpath(p, root), n)] = (k['kind'], tuple(k['rids']))
    return out


def impact(root, proposed, lexicon=None):
    cur = load(os.path.join(root, 'assimilate.py'), 'gate_current')
    new = load(proposed, 'gate_proposed')
    a = classify_all(cur, root, os.path.join(root, 'lexicon.txt'))
    b = classify_all(new, root, lexicon or os.path.join(root, 'lexicon.txt'))
    return a, {k: (a[k], b.get(k)) for k in a if a[k] != b.get(k)}


if __name__ == '__main__':
    a, ch = impact(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    print('%d clause sentences classified; %d would change under the proposed gate' % (len(a), len(ch)))
    for k, (x, y) in sorted(ch.items()):
        print('  %s: %s %s -> %s %s' % (k, x[0], ','.join(r[-3:] for r in x[1]), y[0] if y else '-', ','.join(r[-3:] for r in (y[1] if y else ()))))
    sys.exit(1 if ch else 0)
