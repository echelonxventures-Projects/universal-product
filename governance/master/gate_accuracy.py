"""Gate accuracy (gap 6): classify every case of the reference set against the current Master and report what the gate gets
wrong, by kind of case. Run it on every gate change; the error count may only go down.
Usage: python3 -I gate_accuracy.py <root> [--reference gate_reference.txt] [--max-errors N]   Exit 0 when errors <= N (default 0)."""
import os, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from ids import X  # identifier formats and file names come from the registries (LXM-REQ-000240)
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import assimilate as A


def run(root, ref):
    lex = A.Lexicon(os.path.join(root, X('{@lexicon_txt}'))); recs = A.blocks(A.read(os.path.join(root, X('{@reqs_txt}')))); A.index(recs, lex)
    out = []
    for line in open(ref, encoding='utf-8'):
        if not line.strip() or line.startswith('#'):
            continue
        exp, rid, text = [x.strip() for x in line.split('|', 2)]
        c = A.classify(text, recs, lex, set())
        hit = rid == '*' or rid in c['rids']
        ok = {'duplicate': c['kind'] in ('EXACT', 'COVERED') and hit, 'new': c['kind'] == 'NOVEL',
              'conflict': c['kind'] == 'CONFLICT' and hit, 'agree': c['kind'] != 'CONFLICT'}[exp]
        out.append({'expected': exp, 'record': rid, 'got': c['kind'], 'rids': c['rids'], 'ok': ok, 'text': text})
    return out


if __name__ == '__main__':
    root = sys.argv[1]
    ref = sys.argv[sys.argv.index('--reference') + 1] if '--reference' in sys.argv else os.path.join(root, X('{@gate_reference_txt}'))
    res = run(root, ref)
    by = {}
    for r in res:
        b = by.setdefault(r['expected'], [0, 0]); b[0] += r['ok']; b[1] += 1
    print('gate accuracy: %d of %d cases correct; %s' % (sum(r['ok'] for r in res), len(res), ', '.join('%s %d/%d' % (k, v[0], v[1]) for k, v in sorted(by.items()))))
    for r in res:
        if not r['ok']:
            print('  WRONG  expected %s %s, got %s %s: %s' % (r['expected'], r['record'], r['got'], ','.join(x[-3:] for x in r['rids']), r['text'][:90]))
    errors = sum(not r['ok'] for r in res)
    limit = int(sys.argv[sys.argv.index('--max-errors') + 1]) if '--max-errors' in sys.argv else 0  # the ratchet: errors only go down
    print('errors %d, allowed %d: %s' % (errors, limit, 'pass' if errors <= limit else 'FAIL'))
    sys.exit(0 if errors <= limit else 1)
