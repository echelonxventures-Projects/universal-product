"""Fixtures for the knowledge-system tools: gate_impact.py, gate_accuracy.py, states.py, knowledge_status.py.
Each runs on a throwaway copy of the candidate. Usage: python3 -I -B test_knowledge.py <root>"""
import json, os, shutil, sys, tempfile
sys.dont_write_bytecode = True
ROOT = os.path.abspath(sys.argv[1]); sys.path.insert(0, ROOT)
import gate_impact as GI, gate_accuracy as GA, states as ST, knowledge_status as KS, revalidate as RV, assimilate as A, capture as CP, shard as SH
results = []


def copy():
    d = tempfile.mkdtemp(prefix='kfx-'); shutil.copytree(ROOT, d, dirs_exist_ok=True); return d


def scenario(name, fn):
    try:
        ok, detail = fn()
    except Exception as e:
        ok, detail = False, 'exception: %r' % e
    results.append((name, ok, detail))


def s_impact():
    d = copy()
    try:
        same = GI.impact(d, os.path.join(d, 'assimilate.py'))[1]
        lex = os.path.join(d, 'lexicon-proposed.txt')
        open(lex, 'w').write(open(os.path.join(d, 'lexicon.txt')).read() + '\n@stop: technology, governance\n')
        changed = GI.impact(d, os.path.join(d, 'assimilate.py'), lex)[1]
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return not same and len(changed) > 0, 'unchanged gate: %d differences; a proposed vocabulary change: %d clause classifications change (shown before adoption)' % (len(same), len(changed))


def s_accuracy():
    d = copy()
    try:
        ref = os.path.join(d, 'ref.txt')
        open(ref, 'w').write('duplicate | LXM-REQ-000192 | Never invent owner approvals, financial policies, test evidence, external access, capability support or production readiness.\n'
                             'new | * | Each warehouse dock schedules forklift charging between delivery waves.\n'
                             'new | LXM-REQ-000192 | Never invent owner approvals, financial policies or production readiness.\n')
        res = GA.run(d, ref)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return [r['ok'] for r in res] == [True, True, False], 'a right duplicate, a right new case, and a mislabelled case caught as an error: %s' % [r['ok'] for r in res]


def s_states():
    d = copy(); code = tempfile.mkdtemp(prefix='kfx-code-')
    try:
        os.makedirs(code + '/lib'); os.makedirs(code + '/test')
        open(code + '/lib/x.js', 'w').write('x\n'); open(code + '/test/x.js', 'w').write('x\n')
        json.dump({'scripts': {'test': 'node test/x.js'}}, open(code + '/package.json', 'w'))
        open(d + '/trace.txt', 'a').write('\n@LXM-REQ-000192\nimpl: lib/x.js\nconfig: settings\ntest: test/x.js\nbasis: fixture\n')
        tests = os.path.join(d, 't.json'); json.dump({'sha': 'a' * 40, 'exit': 0, 'failed': 0, 'tree_clean_after': True}, open(tests, 'w'))
        tr = os.path.join(d, 'rt.jsonl'); open(tr, 'w').write('{"path": "brand.name", "how": "read"}\n')
        r = ST.compute(code, 'a' * 40, tests, tr, master=d)['LXM-REQ-000192']
        bad = ST.compute(code, 'b' * 40, tests, tr, master=d)['LXM-REQ-000192']
    finally:
        shutil.rmtree(d, ignore_errors=True); shutil.rmtree(code, ignore_errors=True)
    ok = r['state'] == 'Specified' and set(r['evidenced_beyond_a_gap']) == {'Implemented', 'Configured', 'Enforced at runtime', 'Verified'} and 'Verified' not in bad['evidence']
    return ok, 'all later evidence present but Designed missing -> state %s, evidenced beyond the gap %s; tests from another SHA -> Verified %s' % (
        r['state'], r['evidenced_beyond_a_gap'], 'Verified' in bad['evidence'])


def s_status():
    d = copy()
    try:
        early = KS.status(d, '2026-10-31'); late = KS.status(d, '2026-12-31')
    finally:
        shutil.rmtree(d, ignore_errors=True)
    over = lambda r: sum(h['overdue'] for h in r['held'])
    return over(early) == 0 and over(late) == len(late['held']) > 0 and late['review_lapsed'] and early['chain'][0], \
        'held items overdue today %d, in two months %d of %d; review lapses in two months: %d; log intact: %s' % (over(early), over(late), len(late['held']), len(late['review_lapsed']), early['chain'][0])


def s_revalidate():
    d = copy()
    try:
        os.makedirs(d + '/intake/SRC-0009x', exist_ok=True)
        n0, r0 = RV.revalidate(d)
        p = d + '/intake/SRC-0009x/sup.ctb'  # supersede a record so that the clauses it expressed are gone
        open(p, 'w').write('id: CTB-FX-SUP\nsource: SRC-0009\nsection: §1.1\nkind: requirement\nsupersedes: LXM-REQ-000227\nreason: fixture\n'
                           'text: Synthetic fixture text about warehouse forklift charging windows between delivery waves.\n')
        r = A.assimilate(d, p)
        n1, r1 = RV.revalidate(d)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return not r0 and r['outcome'] == 'REJECTED' and 'unexpressed' in r.get('reason', '') and not r1, \
        'current Master: %d regressions over %d relations; a supersession that would lose other clauses -> %s at change time (%s); regressions afterwards: %d' % (
            len(r0), n0, r['outcome'], r.get('reason', '')[:70], len(r1))


def s_capture():
    d = copy()
    try:
        nid = 'SRC-%04d' % (max(int(l[4:8]) for l in open(d + '/sources.txt') if l.startswith('SRC-')) + 1)
        text = '# Fixture directive\n\n## 1. Rule\n\nEvery synthetic fixture warehouse logs its dock schedule.\n\nThe fixture keeps:\n- one log per dock;\n- one archive per week.\n'
        r1 = CP.capture(d, text, 'fixture', nid, 'Fixture directive', 'Fixture', 'owner', 'internal', 'fixture', '2026-10-31')
        m1 = A.state_matches_log(d)[0]
        r2 = CP.capture(d, text, 'fixture', nid, 'Fixture directive', 'Fixture', 'owner', 'internal', 'fixture', '2026-10-31')
        sec = 'SRC-%04d' % (int(nid[4:]) + 1)
        r3 = CP.capture(d, 'Use api_' + 'key = "abcd1234efgh5678" for the provider.\n', 'fixture', sec, 'Leaky', 'Fixture', 'owner')
        left = os.path.exists(d + '/sources/%s.extract.md' % sec)
        r4 = CP.capture(d, text + 'A changed line.\n', 'fixture', nid, 'Fixture directive', 'Fixture', 'owner')
        r5 = CP.capture(d, 'A synthetic sentence that registers under a skipped identifier.\n', 'fixture', 'SRC-%04d' % (int(nid[4:]) + 5), 'Skip', 'Fixture', 'owner')
        undone = not os.path.exists(d + '/sources/SRC-%04d.extract.md' % (int(nid[4:]) + 5)) and A.state_matches_log(d)[0] and A.verify_chain(d)[0]
        ledger = open(d + '/sources/%s.clauses' % nid).read().count('\n§')
    finally:
        shutil.rmtree(d, ignore_errors=True)
    ok = r1['outcome'] == 'NEW' and m1 and r2['outcome'] == 'NOOP' and r3['outcome'] == 'REJECTED' and not left and r4['outcome'] == 'REJECTED' and r5['outcome'] == 'REJECTED' and undone
    return ok, 'capture %s (%d clauses, state equals log %s); rerun %s; secret %s, nothing left %s; changed text %s; skipped id %s, files undone %s' % (
        r1['outcome'], r1.get('clauses', 0), m1, r2['outcome'], r3['outcome'], not left, r4['outcome'], r5['outcome'], undone)


def s_shard():
    same, master, files, mx, avg = SH.prove(ROOT)
    return all(same.values()) and master, '%d record files, largest %d bytes; registers rejoined identical %s; Master identical %s' % (files, mx, all(same.values()), master)


for a in [('Gate impact: a rule change is previewed before adoption', s_impact), ('Gate accuracy: wrong classifications are measured', s_accuracy),
          ('Computed states: evidence, gaps, exact SHA', s_states), ('Status: held queue ageing, review lapses, log integrity', s_status), ('Re-validation: a record change that loses clauses is caught', s_revalidate), ('Capture: one way in; secrets refused; nothing left behind', s_capture), ('Small files: shards rejoin and rebuild byte-identical', s_shard)]:
    scenario(*a)
fails = 0
for n, ok, det in results:
    fails += not ok; print('%s  %-58s %s' % ('PASS' if ok else 'FAIL', n, det))
print('\n%d scenarios, %d failed' % (len(results), fails))
sys.exit(1 if fails else 0)
