"""Close the feedback loop (design §1; LXM-REQ-000234): outcomes in Level 3 become inputs to Level 1, never edits of Level 2.
Reads the computed states (states.py), the readiness report (readiness.py) and the held queue, and writes:
  - proposals: one file per finding in intake/proposals/, with an id derived from its subject, so a rerun never duplicates one;
    the index marks a proposal resolved when its condition no longer holds (nothing is deleted);
  - an evidence contribution with the computed-state snapshot (intake/proposals/EVD-states.ctb), to be submitted through the gate.
Usage: python3 -I proposals.py <root> --states <states.json> --readiness <readiness.json> --today YYYY-MM-DD --observer NAME"""
import hashlib, json, os, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from ids import X  # identifier formats come from ids.json (LXM-REQ-000240)
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import assimilate as A


def findings(states, readiness):
    out = []
    stuck = sorted(r for r, v in states.items() if v['evidenced_beyond_a_gap'])
    if stuck:
        out.append(('state-gap', 'Requirements with later evidence held at an earlier state', ', '.join(stuck),
                    'Supply the missing earlier evidence (usually a specification for the owning domain) so their state advances.'))
    cfg = sorted(r for r, v in states.items() if v['state'] == 'Configured')
    if cfg:
        out.append(('runtime-unproven', 'Configured requirements not proven at runtime', ', '.join(cfg),
                    'Extend the runtime read trace to their configuration declarations, or show by test that the engine applies them.'))
    for b in readiness.get('blockers', []):
        if b['kind'] in ('configuration', 'code', 'trace', 'tests', 'ci'):
            out.append(('blocker:' + b['what'].split(':')[0] + ':' + b['what'], b['what'], b['requirement'], 'Resolve: %s (%s).' % (b['rule'], b['resolves'])))
    for w in readiness.get('warnings', []):
        out.append(('warning:' + w['what'], w['what'], w['requirement'], 'Review: %s.' % w['rule']))
    return out


def write(root, states, readiness, today, observer):
    d = os.path.join(root, X('{@intake_dir}'), 'proposals'); os.makedirs(d, exist_ok=True)
    idx_p = os.path.join(d, X('{@proposals_index_json}'))
    idx = json.load(open(idx_p, encoding='utf-8')) if os.path.exists(idx_p) else {}
    seen = set(); new = 0
    for subject, title, about, action in findings(states, readiness):
        pid = 'PROP-' + hashlib.sha256(subject.encode()).hexdigest()[:10]
        seen.add(pid)
        p = os.path.join(d, pid + '.md')
        if not os.path.exists(p):  # write-once
            open(p, 'w', encoding='utf-8').write('# %s: %s\n\n- Raised: %s, by %s, from the Level 3 outcomes\n- About: %s\n- Proposed action: %s\n- Status: computed in index.json (open while the condition holds)\n' % (
                pid, title, today, observer, about, action))
            new += 1
        e = idx.setdefault(pid, {'title': title, 'raised': today})
        e.update(status='open', last_seen=today)
    for pid, e in idx.items():
        if pid not in seen and e['status'] == 'open':
            e.update(status='resolved', resolved=today)
    json.dump(dict(sorted(idx.items())), open(idx_p, 'w', encoding='utf-8'), indent=1)
    verified = sorted(r for r, v in states.items() if v['state'] == 'Verified')
    counts = {}
    for v in states.values():
        counts[v['state']] = counts.get(v['state'], 0) + 1
    evs = A.load_build(root).parse_evidence(A.read(os.path.join(root, X('{@evidence_txt}'))))[1]
    fact = 'Computed states of the %d requirements: %s' % (len(states), ', '.join('%s %d' % kv for kv in sorted(counts.items(), key=lambda kv: -kv[1])))
    if not any(e.get('fact') == fact for e in evs) and verified:
        open(os.path.join(d, X('{@states_evidence_ctb}')), 'w', encoding='utf-8').write(
            X('id: CTB-EVD-STATES-%s\nkind: evidence\nevidence: {evd%}\naction: add\nfact: %s\nsource: states.py over traceability, code, configuration, runtime trace and test results\n'
            'method: computed, deterministic\nobserved: %s\nobserver: %s\nverifies: %s\n') % (today, len(evs) + 1, fact, today, observer, ', '.join(verified)))
    return new, sum(1 for e in idx.values() if e['status'] == 'open'), sum(1 for e in idx.values() if e['status'] == 'resolved')


if __name__ == '__main__':
    opt = lambda k: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else None
    states = json.load(open(opt('--states'), encoding='utf-8')); readiness = json.load(open(opt('--readiness'), encoding='utf-8'))
    n, o, r = write(sys.argv[1], states, readiness, opt('--today'), opt('--observer'))
    print('%d new proposals; %d open, %d resolved; evidence contribution %s' % (n, o, r, 'written' if os.path.exists(os.path.join(sys.argv[1], X('{@intake_dir}'), 'proposals', X('{@states_evidence_ctb}'))) else 'not needed'))
