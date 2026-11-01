"""Continuous re-validation (design §1): every coverage relation in Level 2 is re-checked against the current Master, so that a
change anywhere (records growing, extensions, supersessions) cannot silently leave a source clause unexpressed.
For each source clause, the records that cover or extend it express it together: every sentence of its contribution text must be
word for word in one of them, or share at least the gate's related threshold with one of them or with all of them combined.
Usage: python3 -I revalidate.py <root> [--max-regressions N]   Exit 0 when regressions <= N (default 0)."""
import json, os, re, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from ids import X  # identifier formats come from ids.json (LXM-REQ-000240)
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import assimilate as A


def revalidate(root):
    lex = A.Lexicon(os.path.join(root, X('{@lexicon_txt}'))); recs = A.blocks(A.read(os.path.join(root, X('{@reqs_txt}')))); A.index(recs, lex)
    texts = {}  # only contributions the gate accepted, exactly as accepted (same SHA-256), later ones winning; refused or stray files never count
    led = os.path.join(root, A.LEDGER)
    for e in [json.loads(l) for l in open(led, encoding='utf-8') if l.strip()] if os.path.exists(led) else []:
        ok = e.get('outcome') in A.ACCEPTED or (e.get('outcome') in ('NOOP', 'CLOSE') and e.get('classified_as') in A.ACCEPTED)
        p = os.path.join(root, e.get('path') or '')
        if not ok or not e.get('path') or not os.path.isfile(p):
            continue
        c = A.receive(p)
        if c['_sha'] != e.get('contribution_sha256') or c.get('kind', 'requirement') != 'requirement' or not c.get('text'):
            continue
        for sec in c.get('section', '').split(','):
            texts[(c['source'], sec)] = c['text']
    homes = {}
    for rid, r in recs.items():
        for src, sec, rel in re.findall(X(r'({src}) ({cl}) (covers|extends)'), A.field(r, 'c')):
            homes.setdefault((src, sec), []).append(rid)
    checked, regressions = 0, []
    for (src, sec), rids in sorted(homes.items()):
        t = texts.get((src, sec))
        if not t:
            continue  # reconciled before the gate existed: no contribution text to re-check
        checked += 1
        union = set().union(*(recs[r]['_profile']['set'] for r in rids))
        xs = [A.field(recs[r], 'x') for r in rids]
        for n, sen in enumerate(A.sentences(t), 1):  # the records that cover a clause express it together (a composition)
            if any(sen.rstrip('.') in x for x in xs):
                continue
            prof = lex.profile(sen)
            if not prof['set']:
                continue
            best = max(A.containment(prof['set'], recs[r]['_profile']['set']) for r in rids)
            joint = A.containment(prof['set'], union)
            if max(best, joint) < A.T_RELATED:
                regressions.append('%s %s sentence %d no longer expressed by %s (best %.2f, together %.2f)' % (src, sec, n, ', '.join(rids), best, joint))
    return checked, regressions


if __name__ == '__main__':
    n, reg = revalidate(sys.argv[1])
    limit = int(sys.argv[sys.argv.index('--max-regressions') + 1]) if '--max-regressions' in sys.argv else 0
    print('%d coverage relations re-checked against the current Master; %d regressions (allowed %d): %s' % (n, len(reg), limit, 'pass' if len(reg) <= limit else 'FAIL'))
    for x in reg[:40]:
        print('  ' + x)
    sys.exit(0 if len(reg) <= limit else 1)
