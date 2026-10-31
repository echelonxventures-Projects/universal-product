"""Monitoring of the knowledge system itself (gaps 5, 10, 12): backlog, the held queue with resolver and age, review lapses,
log integrity, gate accuracy and the computed-state summary, in one report. Policy (resolvers, deadlines, review periods)
comes from knowledge.json.
Usage: python3 -I knowledge_status.py <root> --today YYYY-MM-DD [--states <states.json>] [--md <out>]"""
import datetime, glob, json, os, re, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from ids import X  # identifier formats come from ids.json (LXM-REQ-000240)
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import assimilate as A
import gate_accuracy as GA


def status(root, today, states_path=None):
    cfg = json.load(open(os.path.join(root, 'knowledge.json'), encoding='utf-8'))
    day = datetime.date.fromisoformat(today)
    d = lambda s: datetime.date.fromisoformat(s[:10])
    # backlog: ledgers still in progress, and their clauses no record covers
    backlog = []
    reqs = A.read(os.path.join(root, 'reqs.txt'))
    for p in sorted(glob.glob(os.path.join(root, 'sources', X('{src-}*.clauses')))):
        t = A.read(p); src = os.path.basename(p)[:8]
        if re.search(r'^status: in-progress', t, re.M):
            cl = re.findall(X(r'^({cl-}\S+) \|'), t, re.M)
            backlog.append((src, len(cl), sum(1 for c in cl if '%s %s ' % (src, c) not in reqs)))
    # held queue
    held = []
    exc = A.read(os.path.join(root, 'intake', 'exceptions.txt')) if os.path.exists(os.path.join(root, 'intake', 'exceptions.txt')) else ''
    raised = {}
    for l in open(os.path.join(root, A.LEDGER), encoding='utf-8'):
        e = json.loads(l)
        if e.get('exception'):
            raised.setdefault(e['exception'], e['at'])
    for m in re.finditer(X(r'^@({exc}) \| (QUARANTINED|REJECTED) \| (\S+) \|[^\n]*\n((?:[a-z]+: [^\n]*\n?)*)'), exc, re.M):
        reason = (re.search(r'^reason: (.*)$', m.group(4), re.M) or [None, ''])[1]
        rule = next(r for r in cfg['held_queue']['resolvers'] if r['when'] in reason)
        at = raised.get(m.group(1), today)
        age = (day - d(at)).days
        held.append({'id': m.group(1), 'status': m.group(2), 'contribution': m.group(3), 'resolver': rule['resolver'], 'age_days': age,
                     'overdue': age > rule['due_days'], 'reason': reason[:120]})
    # review lapses
    rc = cfg['review_cycles']; lapsed = []
    for line in A.read(os.path.join(root, 'sources.txt')).split('\n'):
        if not line.startswith(X('{src-}')):
            continue
        c = [x.strip() for x in line.split(' | ')]
        prov = os.path.join(root, 'sources', c[0] + '.provenance.md')
        cap = re.search(r'Captured by \| [^,]*, (\d{4}-\d{2}-\d{2})', A.read(prov)) if os.path.exists(prov) else None
        when = cap.group(1) if cap else (re.search(r'\((\d{4}-\d{2}-\d{2})', c[1]) or [None, None])[1]
        if when and c[6] in rc and (day - d(when)).days > rc[c[6]]:
            lapsed.append('%s (%s since %s)' % (c[0], c[6], when))
    chain = A.verify_chain(root)
    matches = A.state_matches_log(root)
    baselines = [json.loads(l)['at'][:10] for l in open(os.path.join(root, A.LEDGER), encoding='utf-8') if '"outcome": "BASELINE"' in l]
    acc = GA.run(root, os.path.join(root, cfg['accuracy']['reference']))
    st = json.load(open(states_path, encoding='utf-8')) if states_path and os.path.isfile(states_path) else {}
    import revalidate as RV
    rv = RV.revalidate(root)
    pi = os.path.join(root, 'intake', 'proposals', 'index.json')
    props = json.load(open(pi, encoding='utf-8')) if os.path.exists(pi) else {}
    return {'revalidated': (rv[0], len(rv[1])), 'proposals': (sum(v['status'] == 'open' for v in props.values()), sum(v['status'] == 'resolved' for v in props.values())), 'matches': matches, 'baselines': baselines, 'backlog': backlog, 'held': held, 'review_lapsed': lapsed, 'chain': chain,
            'accuracy': (sum(r['ok'] for r in acc), len(acc)), 'states': {s: sum(1 for r in st.values() if r['state'] == s) for s in cfg['states']['order']} if st else None}


def markdown(r, today):
    out = ['# Knowledge system status (%s)' % today, '',
           '- **Log integrity:** %s (%s).' % ('intact' if r['chain'][0] else '**BROKEN**', r['chain'][1]),
           '- **No direct edits:** %s (%s). Baselines recorded: %s.' % ('the canonical state equals the last gate outcome' if r['matches'][0] else '**the canonical state differs from the last gate outcome**', r['matches'][1], ', '.join(r['baselines']) or 'none'),
           '- **Gate accuracy:** %d of %d reference cases correct.' % r['accuracy'],
           '- **Re-validation:** %d source-clause relations re-checked, %d regressions.' % r['revalidated'],
           '- **Feedback proposals:** %d open, %d resolved (intake/proposals/).' % r['proposals'],
           '- **Backlog:** %s.' % ('; '.join('%s: %d clauses, %d not yet in the Master' % b for b in r['backlog']) or 'none'),
           '- **Review lapsed:** %s.' % (', '.join(r['review_lapsed']) or 'none')]
    if r['states']:
        out.append('- **Computed states:** %s.' % ', '.join('%s %d' % kv for kv in r['states'].items() if kv[1]))
    out += ['', '## Held queue', '', '| Item | Contribution | Resolver | Age (days) | Overdue | Reason |', '|---|---|---|---|---|---|']
    out += ['| %s | %s | %s | %d | %s | %s |' % (h['id'], h['contribution'], h['resolver'], h['age_days'], 'yes' if h['overdue'] else 'no', h['reason'].replace('|', '\\|')) for h in r['held']] or ['| — | | | | | |']
    return '\n'.join(out) + '\n'


if __name__ == '__main__':
    opt = lambda k: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else None
    r = status(sys.argv[1], opt('--today'), opt('--states'))
    md = markdown(r, opt('--today'))
    if opt('--md'):
        open(opt('--md'), 'w', encoding='utf-8').write(md)
    print(md)
