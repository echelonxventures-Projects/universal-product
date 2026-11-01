"""Regression fixtures for assimilate.py. Each scenario runs in its own throwaway copy of the canonical state with two
synthetic sources (SRC-9001 owner, SRC-9002 historical) registered only in that copy; nothing touches <root>.
Usage: python3 -I test_assimilate.py <root>"""
import os, re, shutil, subprocess, sys, tempfile

sys.dont_write_bytecode = True  # a check never changes the Master directory (no __pycache__)

ROOT = os.path.abspath(sys.argv[1])
sys.path.insert(0, ROOT)
import assimilate as A

SYN = ('\nSRC-9001 | Synthetic owner fixture source | test only | — | Fixture | owner | conversation-only\n'
       'SRC-9002 | Synthetic historical fixture source | test only | — | Fixture | historical | conversation-only\n')
R192 = 'Never invent owner approvals, financial policies, test evidence, external access, capability support or production readiness.'
results = []
NEXT = 'LXM-REQ-%06d' % (max(int(r[-6:]) for r in A.blocks(open(os.path.join(ROOT, 'reqs.txt'), encoding='utf-8').read())) + 1)  # the ID a new record receives


def fixture():
    d = tempfile.mkdtemp(prefix='lxm-fixture-')
    for f in A.CANON + A.TOOLS + A.DERIVED + ['assimilate.py']:
        os.makedirs(os.path.dirname(os.path.join(d, f)), exist_ok=True)
        shutil.copyfile(os.path.join(ROOT, f), os.path.join(d, f))
    shutil.copytree(os.path.join(ROOT, 'sources'), os.path.join(d, 'sources'))
    if os.path.exists(os.path.join(ROOT, 'intake', 'exceptions.txt')):  # open holds are part of what the validator sees
        os.makedirs(os.path.join(d, 'intake')); shutil.copyfile(os.path.join(ROOT, 'intake', 'exceptions.txt'), os.path.join(d, 'intake', 'exceptions.txt'))
    with open(os.path.join(d, 'sources.txt'), 'a', encoding='utf-8') as fh:
        fh.write(SYN)
    A.json.dump(A.gate_config(ROOT), open(os.path.join(d, 'gate.json'), 'w'), indent=1)  # the external sources stay in the Master, not the fixture copy
    rebuild(d, d + '/out')  # the synthetic sources appear in the register before any scenario runs
    return d


def rebuild(d, out):
    g = A.json.load(open(os.path.join(d, 'gate.json')))
    os.makedirs(out, exist_ok=True)
    subprocess.run([sys.executable, '-I', os.path.join(d, 'build.py'), g['src2'], g['src3'], out], check=True, capture_output=True)


def validate(d):
    g = A.json.load(open(os.path.join(d, 'gate.json')))
    v = subprocess.run([sys.executable, '-I', os.path.join(d, 'validate.py'), d + '/out/LXM-MASTER.md', d + '/out/LXM-RECONCILIATION.md',
                        g['src2'], g['src3'], g['prev_matrix'], g['src2_sha'], g['src3_sha']], capture_output=True, text=True)
    return v.returncode == 0, v.stdout.strip().split('\n')[-1]


def ctb(d, name, **kv):
    p = os.path.join(d, name + '.ctb')
    kv.setdefault('id', 'CTB-' + name); kv.setdefault('source', 'SRC-9001'); kv.setdefault('section', '§1'); kv.setdefault('kind', 'requirement')
    open(p, 'w', encoding='utf-8').write(''.join('%s: %s\n' % (k.replace('_', '-'), v) for k, v in kv.items() if v is not None))
    return p


def rec(d, rid):
    return A.blocks(open(os.path.join(d, 'reqs.txt'), encoding='utf-8').read()).get(rid)


def reproducible(d):
    t = tempfile.mkdtemp(); rebuild(d, t)
    same = all(open(os.path.join(t, os.path.basename(f)), 'rb').read() == open(os.path.join(d, f), 'rb').read() for f in A.DERIVED)
    shutil.rmtree(t)
    return same


CALLS = []
_assimilate = A.assimilate
def counted(*a, **k):
    CALLS.append(1)
    return _assimilate(*a, **k)
A.assimilate = counted


def ledger_ok(d, calls):
    """Every gate run leaves exactly one ledger line; refusals and errors never change canonical knowledge (the generated view may show a new hold)."""
    p = os.path.join(d, A.LEDGER)
    rows = [A.json.loads(l) for l in open(p, encoding='utf-8')] if os.path.exists(p) else []
    good = len(rows) == calls and [r['seq'] for r in rows] == list(range(1, calls + 1)) and all(
        r['outcome'] and ((r.get('knowledge_before', r['digest_before']) == r.get('knowledge_after', r['digest_after'])) if r['outcome'] in ('REJECTED', 'QUARANTINED', 'ERROR')
                          else r['digest_before'] == r['digest_after'] if r['outcome'] == 'NOOP' else r['digest_before'] != r['digest_after'])
        for r in rows)
    return good, '%d run(s), %d ledger line(s)' % (calls, len(rows))


_KNOW = {}


def snap(d):
    """The state digest now, remembering the canonical knowledge it stood for."""
    s = A.state_digest(d); _KNOW[s] = A.knowledge_digest(d); return s


def unchanged(d, ref):
    """A refusal leaves canonical knowledge as it was at ref (the generated view may show a new hold)."""
    return _KNOW.get(ref) == A.knowledge_digest(d)


def scenario(name, prevents, fn):
    d = fixture()
    CALLS.clear()
    try:
        before = snap(d)
        ok, detail = fn(d, before)
        lok, ldet = ledger_ok(d, len(CALLS))
        ok, detail = ok and lok, detail + ' | ledger: ' + ldet + ('' if lok else ' MISMATCH')
    except Exception as e:  # a crash is a failed scenario, not a pass
        ok, detail = False, 'exception: %r' % e
    finally:
        shutil.rmtree(d, ignore_errors=True)
    results.append((name, prevents, ok, detail))


def accepted(d, r, outcome):
    """A success must commit, still validate, and leave the derived files reproducible from canonical sources."""
    v, line = validate(d)
    return r['outcome'] == outcome and v and reproducible(d), '%s; %s; validator: %s' % (r['outcome'], r['stages'].get('resolve', ''), line)


def refused(d, r, before, outcome, words):
    exc = open(os.path.join(d, 'intake', 'exceptions.txt'), encoding='utf-8').read() if os.path.exists(os.path.join(d, 'intake', 'exceptions.txt')) else ''
    ok = r['outcome'] == outcome and unchanged(d, before) and r.get('exception') and r['exception'] in exc and re.search(words, r['reason'], re.I)
    return bool(ok), '%s %s: %s | resolution: %s | canonical state unchanged: %s' % (r['outcome'], r.get('exception'), r['reason'][:110], r['resolution'][:80], unchanged(d, before))


def s_exact(d, b):
    r = A.assimilate(d, ctb(d, 'exact', text=R192))
    x = rec(d, 'LXM-REQ-000192')
    ok, det = accepted(d, r, 'RECOGNIZE-EXACT')
    return ok and 'SRC-9001 §1' in A.field(x, 's') and A.field(x, 'x') == R192 and NEXT not in open(d + '/reqs.txt').read(), det


def s_semantic(d, b):
    r = A.assimilate(d, ctb(d, 'semantic', text='Do not fabricate owner sign-offs, monetary policies, testing evidence, outside access, capability support or launch readiness.'))
    ok, det = accepted(d, r, 'RECOGNIZE-SEMANTIC')
    return ok and r['clauses'][0]['rids'] == ['LXM-REQ-000192'] and A.field(rec(d, 'LXM-REQ-000192'), 'x') == R192, det


def s_partial(d, b):
    novel = 'Every synthetic fixture source is purged from the register once its fixture run finishes.'
    r = A.assimilate(d, ctb(d, 'partial', text=R192 + ' ' + novel, scope='ARC', title='Fixture source hygiene', applied_in='STG-12 #1'))
    n = rec(d, NEXT)
    ok, det = accepted(d, r, 'PARTIAL→NEW')
    return ok and n and A.field(n, 'x') == novel and 'SRC-9001 §1' in A.field(rec(d, 'LXM-REQ-000192'), 's'), det + ' | new record holds only the novel clause'


def s_extend(d, b):
    add = 'Never invent customer consent records.'
    r = A.assimilate(d, ctb(d, 'extend', text=add, extends='LXM-REQ-000192'))
    x = A.field(rec(d, 'LXM-REQ-000192'), 'x')
    ok, det = accepted(d, r, 'EXTEND')
    return ok and x == R192 + ' ' + add and rec(d, NEXT) is None, det


def s_compose(d, b):
    r = A.assimilate(d, ctb(d, 'compose', text='Never invent owner approvals, financial policies or production readiness. Owner-reserved actions include merging any pull request, deploying and mutating production data.'))
    ok, det = accepted(d, r, 'COMPOSE')
    rids = sorted({x for c in r.get('clauses', []) for x in c['rids']})
    return ok and rids == ['LXM-REQ-000192', 'LXM-REQ-000193'] and rec(d, NEXT) is None, det + ' | composed: ' + ', '.join(rids)


def s_contradiction(d, b):
    r = A.assimilate(d, ctb(d, 'contradiction', text='Agents may invent owner approvals and financial policies when the owner is unavailable.'))
    return refused(d, r, b, 'QUARANTINED', 'contradict')


def s_supersede(d, b):
    v2 = 'Never invent owner approvals, financial policies, test evidence, external access, capability support, production readiness or customer consent.'
    r = A.assimilate(d, ctb(d, 'supersede', text=v2, supersedes='LXM-REQ-000192', reason='Customer consent added by the owner.'))
    x = rec(d, 'LXM-REQ-000192')
    ok, det = accepted(d, r, 'SUPERSEDE')
    hist = [v for k, v in x['fields'] if k == 'h']
    again = A.assimilate(d, ctb(d, 'supersede', text=v2, supersedes='LXM-REQ-000192', reason='Customer consent added by the owner.'))
    return ok and A.field(x, 'v') == '2' and A.field(x, 'x') == v2 and len(hist) == 1 and R192 in hist[0] and again['outcome'] == 'NOOP', \
        det + ' | v2 live, v1 kept in history; replay: ' + again['outcome']


def s_supersede_unauthorised(d, b):
    r = A.assimilate(d, ctb(d, 'sup-hist', source='SRC-9002', text='Never invent anything.', supersedes='LXM-REQ-000192', reason='x'))
    return refused(d, r, b, 'REJECTED', 'historical authority')


def s_new(d, b):
    r = A.assimilate(d, ctb(d, 'new', text='Every synthetic fixture source is purged from the register once its fixture run finishes.', scope='ARC', title='Fixture source hygiene', applied_in='STG-12 #1'))
    ok, det = accepted(d, r, 'NEW')
    cited = NEXT in [l for l in open(d + '/stages.txt').read().split('\n') if l.startswith('- ')][0] or \
        NEXT in open(d + '/out/LXM-MASTER.md').read().split('### STG-12')[1].split('### STG-13')[0]
    return ok and rec(d, NEXT) and cited, det + ' | %s created and cited by STG-12 action 1' % NEXT


def s_new_needs_identity(d, b):
    r = A.assimilate(d, ctb(d, 'new-bare', text='Every synthetic fixture source is purged from the register once its fixture run finishes.'))
    return refused(d, r, b, 'REJECTED', 'new canonical identity needs')


def s_ambiguous(d, b):
    t = 'Never invent owner approvals for synthetic fixture runs.'
    r = A.assimilate(d, ctb(d, 'ambiguous', text=t, scope='ARC', title='Fixture approvals', applied_in='STG-12 #1'))
    ok1, det1 = refused(d, r, b, 'QUARANTINED', 'ambiguous')
    # the same contribution resubmitted with the resolution the exception asked for
    r2 = A.assimilate(d, ctb(d, 'ambiguous', text=t, scope='ARC', title='Fixture approvals', applied_in='STG-12 #1', distinct_from='LXM-REQ-000192, LXM-REQ-000017'))
    ok2, det2 = accepted(d, r2, 'NEW')
    closed = bool(re.search(r'^@%s \| RESOLVED \| CTB-ambiguous \|' % r['exception'], open(d + '/intake/exceptions.txt').read(), re.M))
    return ok1 and ok2 and closed, det1 + ' || resubmitted with distinct-from: ' + det2 + ' || exception closed: %s' % closed


def s_declared_recognition(d, b):
    t = 'Never invent owner approvals for synthetic fixture runs.'
    r = A.assimilate(d, ctb(d, 'recog', text=t, recognized_as='LXM-REQ-000192'))
    ok1, det1 = accepted(d, r, 'RECOGNIZE-SEMANTIC')
    r2 = A.assimilate(d, ctb(d, 'recog-bad', text='Every synthetic fixture source is purged from the register once its fixture run finishes.', recognized_as='LXM-REQ-000192'))
    b2 = snap(d)
    ok2 = r2['outcome'] == 'REJECTED' and 'not supported' in r2['reason'] and unchanged(d, b2)
    return ok1 and ok2, det1 + ' || unsupported claim: %s %s' % (r2['outcome'], r2['reason'][:70])


def s_whole_master_discovery(d, b):
    recs = A.blocks(open(d + '/reqs.txt').read())
    first, last = sorted(recs)[0], sorted(recs)[-1]
    out = []
    for rid in (first, last):  # both ends of the Master, from a contribution scoped elsewhere
        r = A.assimilate(d, ctb(d, 'disc-' + rid[-3:], text=A.field(recs[rid], 'x').split('. ')[0].rstrip('.') + '.', scope='RPT'))
        out.append((r['outcome'].startswith('RECOGNIZE') or r['outcome'] == 'COMPOSE') and rid in r['clauses'][0]['rids'] and
                   r['stages']['discover'] == '%d canonical records indexed' % len(recs))
    return all(out), 'first %s and last %s found among all %d records' % (first[-3:], last[-3:], len(recs))


def s_later_recognition_of_new_record(d, b):
    t = A.field(rec(d, 'LXM-REQ-000226'), 'x')
    r = A.assimilate(d, ctb(d, 'later-226', text=t))
    ok, det = accepted(d, r, 'RECOGNIZE-EXACT')
    return ok and A.field(rec(d, 'LXM-REQ-000226'), 's').startswith('SRC-0008 '), det


def s_infrastructure_error(d, b):
    g = A.json.load(open(d + '/gate.json')); g['src2'] = '/nonexistent/source'; A.json.dump(g, open(d + '/gate.json', 'w'))
    b = snap(d)
    exc_p = d + '/intake/exceptions.txt'
    exc_before = open(exc_p).read() if os.path.exists(exc_p) else None
    r = A.assimilate(d, ctb(d, 'error', text='Every synthetic fixture source is purged from the register once its fixture run finishes.', scope='ARC', title='t', applied_in='STG-12 #1'))
    no_exc = (open(exc_p).read() if os.path.exists(exc_p) else None) == exc_before
    return r['outcome'] == 'ERROR' and unchanged(d, b) and no_exc, '%s: %s; canonical state unchanged: %s; no LXM-EXC raised: %s' % (r['outcome'], r['reason'][:70], unchanged(d, b), no_exc)


def s_invalid(d, b):
    r = A.assimilate(d, ctb(d, 'invalid', kind='opinion', text='Some opinion about something important.'))
    return refused(d, r, b, 'REJECTED', 'unsupported kind')


def s_no_provenance(d, b):
    r = A.assimilate(d, ctb(d, 'noprov', source='', text='Every synthetic fixture source is purged from the register.'))
    r2 = A.assimilate(d, ctb(d, 'unregistered', source='SRC-9999', text='Every synthetic fixture source is purged from the register.'))
    ok1, det1 = refused(d, r, b, 'REJECTED', 'provenance')
    ok2, det2 = refused(d, r2, b, 'REJECTED', 'not in the source register')
    return ok1 and ok2, det1 + ' || ' + det2


def s_broken_dependency(d, b):
    r = A.assimilate(d, ctb(d, 'brokendep', text=R192, depends='LXM-REQ-999999'))
    r2 = A.assimilate(d, ctb(d, 'brokenstage', text='Every synthetic fixture source is purged.', scope='ARC', title='t', applied_in='STG-99 #1'))
    ok1, det1 = refused(d, r, b, 'REJECTED', 'broken relationship')
    ok2, det2 = refused(d, r2, b, 'REJECTED', 'broken relationship')
    return ok1 and ok2, det1 + ' || ' + det2


def s_validation_blocks(d, b):
    # passes intake, but the staged Master would break an invariant: a stage-scoped record applied by another stage
    r = A.assimilate(d, ctb(d, 'wrongstage', text='Every synthetic fixture source is purged from the register once its fixture run finishes.', scope='STG-05', title='Fixture source hygiene', applied_in='STG-12 #1'))
    return refused(d, r, b, 'REJECTED', 'cited by its own stage')


def s_owner_decided(d, b):
    r = A.assimilate(d, ctb(d, 'ownerdec', text='Escalate a synthetic fixture failure to the owner.', extends='LXM-REQ-000016'))
    return refused(d, r, b, 'QUARANTINED', 'owner-reserved')


def s_owner_hold_sticks(d, b):
    # an owner-reserved refusal holds its source clause; rephrasing it as a new record, or citing an unrecorded decision, must not bypass the hold
    first = A.assimilate(d, ctb(d, 'hold', section='§5', text='Escalate every synthetic fixture failure to the owner.', extends='LXM-REQ-000016'))
    held = first['outcome'] == 'QUARANTINED' and 'owner-reserved' in first['reason']
    b = snap(d)
    t = 'Synthetic fixture failures are always escalated to the owner in a separate packet.'
    r = A.assimilate(d, ctb(d, 'hold-bypass', section='§5', text=t, scope='ESC', title='Fixture escalation', applied_in='STG-00 #1', distinct_from='LXM-REQ-000016'))
    ok, det = refused(d, r, b, 'QUARANTINED', 'held for an owner decision')
    r2 = A.assimilate(d, ctb(d, 'hold-bypass2', section='§5', text=t, scope='ESC', title='Fixture escalation', applied_in='STG-00 #1',
                             distinct_from='LXM-REQ-000016', decision='LXM-DEC-000099'))
    still = re.search(r'^@%s \| QUARANTINED \|' % first['exception'], open(d + '/intake/exceptions.txt').read(), re.M)
    return held and ok and bool(still) and r2['outcome'] == 'QUARANTINED', 'hold %s; ' % first['exception'] + det + ' | unrecorded decision id also refused: %s' % r2['outcome']


def s_decision_authority(d, b):
    # negative: open, unrecorded, unscoped and out-of-scope decisions authorize nothing; every refusal leaves state unchanged
    t = 'Escalate a synthetic fixture failure to the owner.'
    po = os.path.join(ROOT, 'intake', 'decisions', 'LXM-DEC-000014-options')
    neg = [('open C.2 decision', dict(extends='LXM-REQ-000016', decision='LXM-DEC-000010')),
           ('unrecorded decision', dict(extends='LXM-REQ-000016', decision='LXM-DEC-000015')),
           ('adopted K2, empty scope', dict(extends='LXM-REQ-000016', decision='LXM-DEC-000002')),
           ('DEC-14 for a clause outside its scope', dict(extends='LXM-REQ-000016', decision='LXM-DEC-000014')),
           ('DEC-14, in-scope clause, other owner-decided record', dict(source='SRC-0008', section='§7.1', extends='LXM-REQ-000203', decision='LXM-DEC-000014')),
           ('DEC-14 changing its own record without citing it', dict(source='SRC-0009', section='§7.2', extends='LXM-REQ-000231'))]
    out, ok = [], True
    for i, (label, kv) in enumerate(neg):
        r = A.assimilate(d, ctb(d, 'auth-neg-%d' % i, text=t, **kv))
        good = r['outcome'] == 'QUARANTINED' and unchanged(d, b)
        ok &= good; out.append('%s -> %s' % (label, r['outcome']))
    for f in ('7-1-option3.ctb', '7-2-option3.ctb'):  # the option the owner did not choose, citing the adopted decision
        r = A.assimilate(d, os.path.join(po, f))
        good = r['outcome'] == 'QUARANTINED' and 'scope does not cover' in r['reason'] and unchanged(d, b)
        ok &= good; out.append('%s with DEC-14 -> %s' % (f, r['outcome']))
    # positive: the adopted decision authorizes a change to the supplementary criteria, inside its scope
    r = A.assimilate(d, ctb(d, 'auth-pos', source='SRC-0009', section='§7.2', text=t, extends='LXM-REQ-000231', decision='LXM-DEC-000014'))
    pos, det = accepted(d, r, 'EXTEND')
    k = A.field(rec(d, 'LXM-REQ-000231'), 'k')
    return ok and pos and k == 'LXM-DEC-000014', '; '.join(out) + ' || in scope -> %s, decision reference kept once: %s' % (r['outcome'], k)


def s_k_decisions(d, b):
    # K1-K8 stay adopted and binding with an empty mutation-authorization scope: citing one authorizes nothing, anywhere,
    # and the records expressing them still refuse change without an authorized decision
    scopes = A.adopted_decisions(d)
    ks = ['LXM-DEC-%06d' % n for n in range(1, 9)]
    empty = all(k in scopes and scopes[k] == {'clauses': set(), 'records': set()} for k in ks)
    carried = {k: [r for r, x in A.blocks(open(d + '/reqs.txt', encoding='utf-8').read()).items() if k in A.field(x, 'k').split(', ')] for k in ks}
    novel = 'Every synthetic fixture source is purged from the register once its fixture run finishes.'
    out, ok = [], empty and all(carried.values())
    for n, k in enumerate(ks, 1):
        own = carried[k][0]
        tries = [('new', 'REJECTED', dict(text=novel, scope='ARC', title='Fixture source hygiene', applied_in='STG-12 #1', decision=k)),
                 ('extend ordinary 192', 'REJECTED', dict(text='Synthetic fixture runs log their finishing time.', extends='LXM-REQ-000192', decision=k)),
                 ('recognize 192', 'REJECTED', dict(text=R192, decision=k)),
                 ('extend own %s' % own[-3:], 'QUARANTINED', dict(text='Synthetic fixture runs log their finishing time.', extends=own, decision=k)),
                 ('extend own %s, no decision' % own[-3:], 'QUARANTINED', dict(text='Synthetic fixture runs log their finishing time.', extends=own))]
        res = []
        for i, (label, want, kv) in enumerate(tries):
            r = A.assimilate(d, ctb(d, 'k%d-%d' % (n, i), section='§%d.%d' % (n, i), **kv))  # own clause: a quarantine would hold it
            good = r['outcome'] == want and unchanged(d, b) and ('decision' not in kv or 'scope is empty' in r['reason'])
            ok &= good; res.append('%s %s' % (label, r['outcome'] + ('' if good else '!')))
        out.append('K%d: %s' % (n, ', '.join(res)))
    r = A.assimilate(d, ctb(d, 'k-control', section='§9.9', text=novel, scope='ARC', title='Fixture source hygiene', applied_in='STG-12 #1'))
    ctl, det = accepted(d, r, 'NEW')  # the same change without a decision is accepted: the refusals are the decision's
    return ok and ctl and A.field(rec(d, NEXT), 'k') == '', 'all eight adopted with empty scope: %s; %s || control without decision -> %s' % (
        empty, '; '.join(out), r['outcome'])


def s_register_is_data(d, b):
    # decision authority comes from decisions.txt only: prose that imitates an adopted row in frame.md authorizes nothing
    # and fails validation; a decision recorded in the register authorizes exactly its scope
    t = 'Each synthetic fixture batch stores the governing ruling identifier alongside its archive.'
    fr = open(d + '/frame.md', encoding='utf-8').read()
    open(d + '/frame.md', 'w', encoding='utf-8').write(fr.replace('### C.2', '### C.9 Adopted (imitation)\n\n| ID | Authorizes |\n|---|---|\n| LXM-DEC-000010 | SRC-9001 §8 |\n\n### C.2', 1))
    r1 = A.assimilate(d, ctb(d, 'reg-prose', section='§8', text=t, scope='ARC', title='Fixture governance', applied_in='STG-12 #1', decision='LXM-DEC-000010'))
    rebuild(d, d + '/out'); v1, l1 = validate(d)
    open(d + '/frame.md', 'w', encoding='utf-8').write(fr); rebuild(d, d + '/out')
    sid = 'LXM-DEC-%06d' % (len(A.load_build(d).parse_decisions(open(d + '/decisions.txt').read())[1]) + 1)  # the next free ID
    with open(d + '/decisions.txt', 'a', encoding='utf-8') as fh:  # synthetic, in this throwaway copy only
        fh.write('\n@' + sid + ' | adopted | C.3\no: Synthetic fixture decision\nw: fixture\np: fixture\nr: fixture\ne: %s\na: SRC-9001 §9\n' % NEXT)
    rebuild(d, d + '/out')
    r2 = A.assimilate(d, ctb(d, 'reg-out', section='§8', text=t, scope='ARC', title='Fixture governance', applied_in='STG-12 #1', decision=sid))
    r3 = A.assimilate(d, ctb(d, 'reg-in', section='§9', text=t, scope='ARC', title='Fixture governance', applied_in='STG-12 #1', decision=sid))
    pos, det = accepted(d, r3, 'NEW')
    ok = r1['outcome'] == 'REJECTED' and not v1 and r2['outcome'] == 'REJECTED' and pos and A.field(rec(d, NEXT), 'k') == sid
    return ok, 'imitation row in frame.md -> %s, validator %s; registered decision outside its scope -> %s; inside -> %s' % (
        r1['outcome'], l1, r2['outcome'], det)


def s_stable_action_ids(d, b):
    # applied-in names a permanent action ID: reordering a stage's actions never changes which action a citation lands in
    st = open(d + '/stages.txt', encoding='utf-8').read()
    blk = st.split('#STG-12 |')[1].split('\n#STG-')[0]
    acts = [l for l in blk.split('\n') if l.startswith('- ')]
    open(d + '/stages.txt', 'w', encoding='utf-8').write(st.replace(blk, blk.replace('\n'.join(acts), '\n'.join(reversed(acts)))))
    rebuild(d, d + '/out'); b2 = snap(d)
    t = 'Each synthetic fixture batch stores the governing ruling identifier alongside its archive.'
    r1 = A.assimilate(d, ctb(d, 'aid-legacy', text=t, scope='ARC', title='Fixture governance', applied_in='STG-12 #1'))
    a1 = [l for l in open(d + '/stages.txt', encoding='utf-8').read().split('\n') if l.startswith('- A-1 ') and NEXT in l]
    r2 = A.assimilate(d, ctb(d, 'aid-missing', section='§2', text='Every synthetic fixture archive is compressed before it is stored.', scope='ARC', title='Fixture archive', applied_in='STG-12.A-99'))
    r3 = A.assimilate(d, ctb(d, 'aid-new', section='§3', text='Synthetic fixture operators rotate their signing keys quarterly.', scope='ARC', title='Fixture archive', applied_in='STG-12.A-%d' % len(acts)))
    last = [l for l in open(d + '/stages.txt', encoding='utf-8').read().split('\n') if l.startswith('- A-%d ' % len(acts)) and 'LXM-REQ-%06d' % (int(NEXT[-6:]) + 1) in l]
    ok = r1['outcome'] == 'NEW' and len(a1) == 1 and r2['outcome'] == 'REJECTED' and r3['outcome'] == 'NEW' and len(last) == 1 and validate(d)[0]
    return ok, 'actions reversed; legacy "STG-12 #1" -> %s, cited in A-1 (now last in order): %s; unknown STG-12.A-99 -> %s; STG-12.A-%d -> %s, cited there: %s' % (
        r1['outcome'], len(a1) == 1, r2['outcome'], len(acts), r3['outcome'], len(last) == 1)


def s_decision_adapter(d, b):
    # recording a decision is a gated contribution: open the next question; adopt only with the owner's approval on file;
    # an adopted decision is never edited; once adopted, its scope authorizes requirement changes
    nid = 'LXM-DEC-%06d' % (len(A.load_build(d).parse_decisions(open(d + '/decisions.txt').read())[1]) + 1)
    dec = lambda name, **kv: ctb(d, name, kind='decision', source=None, section=None, **kv)
    out, ok = [], True
    def expect(label, r, want, before=None):
        nonlocal ok
        good = r['outcome'] == want and (before is None or unchanged(d, before))
        ok &= good; out.append('%s -> %s%s' % (label, r['outcome'], '' if good else '!'))
    b0 = snap(d)
    expect('open a skipped ID', A.assimilate(d, dec('d-skip', decision='LXM-DEC-%06d' % (int(nid[-6:]) + 1), action='open', question='Synthetic question?')), 'REJECTED', b0)
    r = A.assimilate(d, dec('d-open', decision=nid, action='open', question='Synthetic fixture question: which archive format?'))
    o_ok, _ = accepted(d, r, 'NEW'); ok &= o_ok; out.append('open %s -> %s' % (nid[-3:], r['outcome']))
    expect('replay the open', A.assimilate(d, dec('d-open', decision=nid, action='open', question='Synthetic fixture question: which archive format?')), 'NOOP')
    ap_dir = d + '/intake/decisions'; os.makedirs(ap_dir, exist_ok=True)
    open(ap_dir + '/fx.approval.txt', 'w').write('Owner approval (fixture), selected options: %s: zstd for archives.\n' % nid[-6:])  # named by its number
    open(ap_dir + '/other.approval.txt', 'w').write('Owner approval (fixture) of some other decision.\n')
    open(d + '/loose.txt', 'w').write('approve %s\n' % nid)
    h = lambda f: A.sha(open(f, 'rb').read())
    base = dict(decision=nid, action='adopt', outcome='Use zstd for fixture archives', effect='LXM-REQ-000192', authorizes='SRC-9001 §8, LXM-REQ-000192',
                adopted='fixture owner', provenance='fixture', rationale='fixture', approval='intake/decisions/fx.approval.txt', approval_sha256=h(ap_dir + '/fx.approval.txt'))
    b1 = snap(d)
    for label, change in [('adopt without an approval', dict(approval=None, approval_sha256=None)),
                          ('approval not naming the decision', dict(approval='intake/decisions/other.approval.txt', approval_sha256=h(ap_dir + '/other.approval.txt'))),
                          ('approval hash mismatch', dict(approval_sha256='0' * 64)),
                          ('approval outside intake/decisions', dict(approval='loose.txt', approval_sha256=h(d + '/loose.txt'))),
                          ('malformed scope', dict(authorizes='whatever is needed'))]:
        kv = dict(base); kv.update(change)
        expect(label, A.assimilate(d, dec('d-bad-%d' % len(out), **kv)), 'REJECTED', b1)
    here = os.getcwd(); os.chdir(d)
    try:  # the gate is often run from inside the Master folder: the root is then '.'
        r = A.assimilate('.', os.path.join('.', os.path.basename(dec('d-adopt', **dict(base, approval='intake/decisions/fx.approval.txt')))))
    finally:
        os.chdir(here)
    a_ok, _ = accepted(d, r, 'ADOPT'); ok &= a_ok; out.append('adopt with approval, root given as "." -> %s' % r['outcome'])
    grp = {x['id']: (x['status'], x['group']) for x in A.load_build(d).parse_decisions(open(d + '/decisions.txt').read())[1]}[nid]
    ok &= grp == ('adopted', 'C.3'); out.append('now %s in %s' % grp)
    expect('replay the adoption', A.assimilate(d, dec('d-adopt', **base)), 'NOOP')
    expect('replay the open after adoption', A.assimilate(d, dec('d-open', decision=nid, action='open', question='Synthetic fixture question: which archive format?')), 'NOOP')
    kv = dict(base); kv['outcome'] = 'Use gzip instead'
    b2 = snap(d)
    expect('edit the adopted decision', A.assimilate(d, dec('d-edit', **kv)), 'QUARANTINED', b2)
    r = A.assimilate(d, ctb(d, 'd-use', section='§8', text='Synthetic fixture archives are compressed with zstd before upload.', extends='LXM-REQ-000192', decision=nid))
    u_ok, _ = accepted(d, r, 'EXTEND'); ok &= u_ok; out.append('requirement change inside its scope -> %s' % r['outcome'])
    return ok, '; '.join(out)


def s_evidence_adapter(d, b):
    # evidence is recorded through the gate, never edited, and replaced only by a newer observation
    evs = A.load_build(d).parse_evidence(open(d + '/evidence.txt').read())[1]
    nxt = 'LXM-EVD-%06d' % (len(evs) + 1); cur = evs[-1]['id']
    ev = lambda name, **kv: ctb(d, name, kind='evidence', section=None, **kv)
    obs = dict(fact='Synthetic fixture observation', source='fixture API', method='fixture', observed='2026-10-30T00:00Z', observer='fixture', verifies='LXM-REQ-000192')
    out, ok = [], True
    def expect(label, r, want, before=None):
        nonlocal ok
        good = r['outcome'] == want and (before is None or unchanged(d, before))
        ok &= good; out.append('%s -> %s%s' % (label, r['outcome'], '' if good else '!'))
    b0 = snap(d)
    expect('skipped ID', A.assimilate(d, ev('e1', evidence='LXM-EVD-%06d' % (len(evs) + 2), action='add', **obs)), 'REJECTED', b0)
    kv = dict(obs); del kv['observer']
    expect('no observer', A.assimilate(d, ev('e2', evidence=nxt, action='add', **kv)), 'REJECTED', b0)
    kv = dict(obs); kv['verifies'] = 'LXM-REQ-999999'
    expect('verifies an unknown record', A.assimilate(d, ev('e3', evidence=nxt, action='add', **kv)), 'REJECTED', b0)
    kv = dict(obs); kv['fact'] = 'An edited fact'
    expect('edit existing %s' % cur[-3:], A.assimilate(d, ev('e4', evidence=cur, action='add', **kv)), 'REJECTED', b0)
    r = A.assimilate(d, ev('e5', evidence=nxt, action='supersede', supersedes=cur, **obs))
    s_ok, _ = accepted(d, r, 'SUPERSEDE'); ok &= s_ok; out.append('supersede %s with %s -> %s' % (cur[-3:], nxt[-3:], r['outcome']))
    after = {e['id']: e['status'] for e in A.load_build(d).parse_evidence(open(d + '/evidence.txt').read())[1]}
    ok &= after[cur] == 'superseded by ' + nxt and after[nxt] == 'current'; out.append('%s now "%s"' % (cur[-3:], after[cur]))
    expect('replay', A.assimilate(d, ev('e5', evidence=nxt, action='supersede', supersedes=cur, **obs)), 'NOOP')
    nn = 'LXM-EVD-%06d' % (len(evs) + 2)
    expect('supersede an already superseded entry', A.assimilate(d, ev('e6', evidence=nn, action='supersede', supersedes=cur, **obs)), 'REJECTED', snap(d))
    return ok, '; '.join(out)


def s_adopted_decision_applied(d, b):
    # the real candidate after LXM-DEC-000014: one record, both holds resolved against it, LXM-REQ-000016 untouched, replay NOOP
    po = os.path.join(ROOT, 'intake', 'decisions', 'LXM-DEC-000014-options')
    x231, x16 = rec(d, 'LXM-REQ-000231'), rec(d, 'LXM-REQ-000016')
    reqs = open(d + '/reqs.txt', encoding='utf-8').read()
    exc = open(d + '/intake/exceptions.txt', encoding='utf-8').read()
    one = reqs.count('(S1)') == 1 and reqs.count('(S2)') == 1 and '(E6)' not in reqs
    held = all(re.search(r'^@%s \| RESOLVED \|[^\n]*\n(?:[a-z]+: [^\n]*\n)*resolved: [^\n]*LXM-REQ-000231; decision LXM-DEC-000014$' % e, exc, re.M)
               for e in ('LXM-EXC-000001', 'LXM-EXC-000002'))
    rel = A.field(x231, 'c') == 'SRC-0008 §7.1 covers; SRC-0009 §7.2 covers' and A.field(x231, 'k') == 'LXM-DEC-000014' and A.field(x231, 'd') == 'LXM-REQ-000016'
    h3 = open(d + '/out/LXM-MASTER.md', encoding='utf-8').read().split('### H.3')[1]
    shown = '| §7.1 | 67-67 | LXM-REQ-000231 | — | — |' in h3 and '| §7.2 | 71-71 | LXM-REQ-000231 | — | — |' in h3
    e16 = all('(E%d)' % i in A.field(x16, 'x') for i in range(1, 6)) and '(E6)' not in A.field(x16, 'x') and A.field(x16, 'v') == ''
    replay = [A.assimilate(d, os.path.join(po, f))['outcome'] for f in ('7-1-option2.ctb', '7-2-option2.ctb')]
    ok = one and held and rel and shown and e16 and replay == ['NOOP', 'NOOP'] and unchanged(d, b)
    return ok, 'criteria in one record: %s; both exceptions resolved against 231 under DEC-14: %s; relations exact: %s; H.3 covered, no hold: %s; 000016 E1-E5 unchanged: %s; replay %s' % (
        one, held, rel, shown, e16, ', '.join(replay))


def s_repeat(d, b):
    p = ctb(d, 'repeat', text='Every synthetic fixture source is purged from the register once its fixture run finishes.', scope='ARC', title='Fixture source hygiene', applied_in='STG-12 #1')
    r1 = A.assimilate(d, p); after1 = snap(d)
    r2 = A.assimilate(d, p); after2 = snap(d)
    bad = ctb(d, 'repeat-bad', text='Agents may invent owner approvals and financial policies when the owner is unavailable.')
    e1 = A.assimilate(d, bad)['exception']; e2 = A.assimilate(d, bad)['exception']
    ok = r1['outcome'] == 'NEW' and r2['outcome'] == 'NOOP' and after1 == after2 and after1 != b and e1 == e2 and \
        open(d + '/reqs.txt').read().count('@' + NEXT) == 1 and open(d + '/stages.txt').read().count(NEXT) == 1
    return ok, 'first %s, replay %s, state identical after replay: %s; repeated failure reuses %s' % (r1['outcome'], r2['outcome'], after1 == after2, e1)


def s_interrupted_commit(d, b):
    # stage a valid mutation, write the journal, "crash" before any replacement; the next gate run rolls forward
    reqs = open(d + '/reqs.txt').read()
    new_reqs, new_stages, _ = A.apply([('lineage', 'LXM-REQ-000192', 'SRC-9001', '§9')], reqs, open(d + '/stages.txt').read())
    stg = tempfile.mkdtemp()
    for f in A.CANON + A.TOOLS:
        shutil.copyfile(os.path.join(d, f), os.path.join(stg, f))
    shutil.copytree(d + '/sources', stg + '/sources')
    if os.path.isdir(d + '/intake'):
        shutil.copytree(d + '/intake', stg + '/intake')  # stage exactly as the gate does
    open(stg + '/reqs.txt', 'w').write(new_reqs); rebuild(stg, stg + '/out')
    for f in ['reqs.txt'] + A.DERIVED:
        shutil.copyfile(os.path.join(stg, f), os.path.join(d, f + '.staged'))
    open(d + '/.assimilate-journal', 'w').write(A.json.dumps(['reqs.txt'] + A.DERIVED))
    mid = unchanged(d, b)
    A.recover(d)
    v, line = validate(d)
    return mid and v and 'SRC-9001 §9' in open(d + '/reqs.txt').read() and not os.path.exists(d + '/.assimilate-journal'), \
        'before recovery state was the old one: %s; after roll-forward valid: %s (%s)' % (mid, v, line)


def s_replay_after_later_change(d, b):
    # an old supersession and an old extension, replayed after the record changed again, are NOOP and revert nothing
    v2 = 'Never invent owner approvals, financial policies, test evidence, external access, capability support, production readiness or customer consent.'
    sup = ctb(d, 'r-sup', text=v2, supersedes='LXM-REQ-000192', reason='Customer consent added by the owner.')
    ext = ctb(d, 'r-ext', section='§2', text='Never invent supplier certifications.', extends='LXM-REQ-000192')
    o = [A.assimilate(d, sup)['outcome'], A.assimilate(d, ext)['outcome']]
    after = snap(d)
    o += [A.assimilate(d, sup)['outcome'], A.assimilate(d, ext)['outcome']]
    x = rec(d, 'LXM-REQ-000192')
    ok = o == ['SUPERSEDE', 'EXTEND', 'NOOP', 'NOOP'] and unchanged(d, after) and A.field(x, 'x') == v2 + ' Never invent supplier certifications.' \
        and A.field(x, 'v') == '2' and len([1 for k, _ in x['fields'] if k == 'h']) == 1
    return ok, 'outcomes %s; extension kept, still v2 with one history entry: %s' % (', '.join(o), ok)


def s_replay_after_owner_decision(d, b):
    # a supersession applied before its record became owner-decided is a NOOP on replay: an applied change is never re-judged
    v2 = 'Never invent owner approvals, financial policies, test evidence, external access, capability support, production readiness or customer consent.'
    sup = ctb(d, 'od-sup', text=v2, supersedes='LXM-REQ-000192', reason='Customer consent added by the owner.')
    o = [A.assimilate(d, sup)['outcome']]
    with open(os.path.join(d, 'sources.txt'), 'a', encoding='utf-8') as fh:
        fh.write('SRC-9003 | Synthetic owner-decision fixture source | test only | — | Fixture | owner-decision | conversation-only\n')
    rebuild(d, d + '/out')
    o.append(A.assimilate(d, ctb(d, 'od-ext', source='SRC-9003', text='Never invent supplier certifications.', extends='LXM-REQ-000192'))['outcome'])
    decided = A.owner_decided(rec(d, 'LXM-REQ-000192'), A.sources(d))
    o.append(A.assimilate(d, sup)['outcome'])
    return o == ['SUPERSEDE', 'EXTEND', 'NOOP'] and decided, 'outcomes %s; record owner-decided before the replay: %s' % (', '.join(o), decided)


def s_replay_by_identity(d, b):
    # an accepted contribution replays as NOOP even after later growth changes how its text matches; if its recorded
    # relation is removed, it is judged again
    p = ctb(d, 'idem', section='§4', text=R192)
    r1 = A.assimilate(d, p)
    for i in range(3):  # grow other records so that matching shifts
        A.assimilate(d, ctb(d, 'grow%d' % i, section='§5.%d' % i, extends='LXM-REQ-000193', text='Synthetic fixture growth sentence number %d about invented owner approvals and financial policies.' % i))
    st = snap(d); r2 = A.assimilate(d, p); same = unchanged(d, st)
    reqs = open(d + '/reqs.txt', encoding='utf-8').read()
    open(d + '/reqs.txt', 'w', encoding='utf-8').write(reqs.replace('; SRC-9001 §4 covers', '').replace('c: SRC-9001 §4 covers; ', 'c: '))
    r3 = A.assimilate(d, p)
    ok = r1['outcome'] == 'RECOGNIZE-EXACT' and r2['outcome'] == 'NOOP' and 'ledger seq' in r2.get('recognized_as', '') and same and r3['outcome'] != 'NOOP'
    return ok, 'first %s; replay after growth %s (%s), state identical %s; relation removed, then %s' % (r1['outcome'], r2['outcome'], r2.get('recognized_as'), same, r3['outcome'])


def s_chain_and_projection(d, b):
    # the log is a hash chain; Level 2 is rebuilt from a checkpoint by applying the recorded mutations; tampering is caught
    import project as PJ
    cp = tempfile.mkdtemp(prefix='lxm-cp-'); shutil.copytree(d, cp, dirs_exist_ok=True)
    r1 = A.assimilate(d, ctb(d, 'pj-new', section='§6.1', text='Synthetic fixture operators rotate their signing keys quarterly.', scope='ARC', title='Fixture keys', applied_in='STG-12 #1'))
    r2 = A.assimilate(d, ctb(d, 'pj-ext', section='§6.2', text='Synthetic fixture runs log their finishing time.', extends='LXM-REQ-000192'))
    nxt = 'LXM-EVD-%06d' % (len(A.load_build(d).parse_evidence(open(d + '/evidence.txt').read())[1]) + 1)
    r3 = A.assimilate(d, ctb(d, 'pj-evd', kind='evidence', section=None, evidence=nxt, action='add', fact='Synthetic fixture observation', source='fixture API',
                             method='fixture', observed='2026-10-31T00:00Z', observer='fixture', verifies='LXM-REQ-000192'))
    chain_ok, det = A.verify_chain(d)
    out = tempfile.mkdtemp(prefix='lxm-pj-')
    n = PJ.project(cp, d, out)
    same = all(A.sha(open(os.path.join(out, f), 'rb').read()) == A.sha(open(os.path.join(d, f), 'rb').read()) for f in ('reqs.txt', 'stages.txt', 'decisions.txt', 'evidence.txt'))
    orig = open(d + '/intake/ledger.jsonl').read(); lines = orig.split('\n')
    lines[0] = lines[0].replace('"outcome": "NEW"', '"outcome": "REJECTED"')
    open(d + '/intake/ledger.jsonl', 'w').write('\n'.join(lines))
    tampered = A.verify_chain(d)[0]
    v_ok, v_line = validate(d)
    open(d + '/intake/ledger.jsonl', 'w').write(orig)  # restored: the harness checks the ledger afterwards
    shutil.rmtree(cp, ignore_errors=True); shutil.rmtree(out, ignore_errors=True)
    ok = [r1['outcome'], r2['outcome'], r3['outcome']] == ['NEW', 'EXTEND', 'NEW'] and chain_ok and n == 3 and same and not tampered and not v_ok
    return ok, 'outcomes %s; chain %s (%s); projection applied %d mutations, equal: %s; one earlier line edited -> chain intact: %s, validator %s' % (
        [r1['outcome'], r2['outcome'], r3['outcome']], chain_ok, det, n, same, tampered, v_line)


def s_open_scopes(d, b):
    # scopes are registered data: an unregistered scope is refused; once registered, the same requirement is accepted, no code change
    kv = dict(section='§7.1', text='Synthetic tenant operators archive their fixture dashboards every month.', scope='OPS', title='Fixture archive', applied_in='STG-12 #1')
    r1 = A.assimilate(d, ctb(d, 'scope-unknown', **kv))
    sc = open(d + '/scopes.txt').read().replace('RPT | Final report', 'OPS | Operations knowledge\nRPT | Final report')
    open(d + '/scopes.txt', 'w').write(sc)
    kv['section'] = '§7.2'
    r2 = A.assimilate(d, ctb(d, 'scope-known', **kv))
    ok2, det = accepted(d, r2, 'NEW')
    return r1['outcome'] == 'REJECTED' and ok2 and '#### CAT-OPS' in open(d + '/out/LXM-MASTER.md').read() or ('CAT-OPS' in open(d + '/out/LXM-MASTER.md').read() and r1['outcome'] == 'REJECTED' and ok2), \
        'unregistered scope OPS -> %s; registered in scopes.txt -> %s, with its own catalogue group: %s' % (r1['outcome'], r2['outcome'], 'CAT-OPS' in open(d + '/out/LXM-MASTER.md').read())


def s_all_kinds(d, b):
    # trace, scope, source, stage-action and prose go through the gate; bad changes are refused; replays are NOOP; and the
    # canonical state then equals the last gate outcome, so a direct edit afterwards is detected
    out, ok = [], True
    def run(cname, want, **kv):
        nonlocal ok
        path = os.path.join(d, cname + '.ctb')
        open(path, 'w', encoding='utf-8').write('id: CTB-%s\n' % cname + ''.join('%s: %s\n' % (k.replace('_', '-'), v) for k, v in kv.items()))
        r = A.assimilate(d, path)
        good = r['outcome'] == want; ok &= good; out.append('%s %s%s' % (cname, r['outcome'], '' if good else '!'))
        return r
    run('tr-bad', 'REJECTED', kind='trace', requirement='LXM-REQ-999999', action='add', impl='lib/x.js', basis='fixture')
    run('tr-add', 'NEW', kind='trace', requirement='LXM-REQ-000192', action='add', impl='lib/x.js', test='test/x.js', basis='fixture review')
    run('tr-add', 'NOOP', kind='trace', requirement='LXM-REQ-000192', action='add', impl='lib/x.js', test='test/x.js', basis='fixture review')
    run('tr-rep', 'SUPERSEDE', kind='trace', requirement='LXM-REQ-000192', action='replace', impl='lib/y.js', basis='fixture re-review')
    run('sc-stg', 'REJECTED', kind='scope', scope='STG-99', action='add', name='No', after='ARC', basis='fixture')
    run('sc-add', 'NEW', kind='scope', scope='OPS', action='add', name='Operations knowledge', after='ARC', basis='fixture')
    nid = 'SRC-%04d' % (max(int(l[4:8]) for l in open(d + '/sources.txt') if l.startswith('SRC-')) + 1)
    run('src-missing', 'REJECTED', kind='source', source=nid, action='register', title='T', location='L', sha='S', role='R', authority='owner', text_status='provisional-extract', basis='fixture')
    run('src-confirm', 'QUARANTINED', kind='source', source=nid, action='register', title='T', location='L', sha='S', role='R', authority='owner', text_status='owner-confirmed', basis='fixture')
    run('src-conv', 'NEW', kind='source', source=nid, action='register', title='Fixture conversation', location='Conversation only', sha='—', role='Fixture', authority='owner', text_status='conversation-only', basis='fixture')
    run('sa-bad', 'REJECTED', kind='stage-action', stage='STG-12', action='add', text='Do something without citing anything at all.', basis='fixture')
    run('sa-add', 'NEW', kind='stage-action', stage='STG-12', action='add', text='Archive every synthetic fixture run and its evidence.', refs='LXM-REQ-000192', basis='fixture')
    run('sa-add', 'NOOP', kind='stage-action', stage='STG-12', action='add', text='Archive every synthetic fixture run and its evidence.', refs='LXM-REQ-000192', basis='fixture')
    run('pr-owner', 'QUARANTINED', kind='prose', heading='### G.4 Remaining genuinely owner-reserved decisions', action='replace', text='Nothing.', basis='fixture')
    anchor = [l for l in open(d + '/frame.md', encoding='utf-8').read().split('\n') if l.startswith('| 1.0.0-rc.')][-1]
    run('pr-ins', 'EXTEND', kind='prose', anchor=anchor, action='insert', text='| 9.9.9-fixture | 2026-10-31 | Fixture revision row. |', basis='fixture')
    run('pr-ins', 'NOOP', kind='prose', anchor=anchor, action='insert', text='| 9.9.9-fixture | 2026-10-31 | Fixture revision row. |', basis='fixture')
    run('pr-edit', 'SUPERSEDE', kind='prose', line='| 9.9.9-fixture | 2026-10-31 | Fixture revision row. |', occurrence='1', action='edit-line', text='| 9.9.9-fixture | 2026-10-31 | Fixture revision row, corrected. |', basis='fixture')
    run('pr-edit', 'NOOP', kind='prose', line='| 9.9.9-fixture | 2026-10-31 | Fixture revision row. |', occurrence='1', action='edit-line', text='| 9.9.9-fixture | 2026-10-31 | Fixture revision row, corrected. |', basis='fixture')
    v, line = validate(d)
    m1 = A.state_matches_log(d)[0]
    open(d + '/trace.txt', 'a').write('\n')  # a direct edit
    m2 = A.state_matches_log(d)[0]
    return ok and v and m1 and not m2, '; '.join(out) + ' || validator %s; state equals the last gate outcome: %s; after one direct edit: %s' % (line, m1, m2)


def s_multi_clause(d, b):
    # one contribution citing several source clauses records one coverage relation per clause
    r = A.assimilate(d, ctb(d, 'multi', section='§3.1,§3.2', text='Every synthetic fixture source is purged from the register once its fixture run finishes.',
                            scope='ARC', title='Fixture source hygiene', applied_in='STG-12 #1'))
    ok, det = accepted(d, r, 'NEW')
    c = A.field(rec(d, NEXT), 'c')
    return ok and c == 'SRC-9001 §3.1 covers; SRC-9001 §3.2 covers', det + ' | coverage: ' + c


def s_matching_rules(d, b):
    # governed matching rules: double negation is an obligation; hyphenated identifiers are not quantities; list lead-ins do not dilute meaning
    lex = A.Lexicon(d + '/lexicon.txt')
    recs = A.blocks(open(d + '/reqs.txt', encoding='utf-8').read()); A.index(recs, lex)
    dn = lex.profile('No contribution becomes canonical without validation.')
    ident = lex.profile('writer-62 is the sole writer of PR-053.')
    frame = A.classify('All capabilities must conform to the Knowledge Once Principle.', recs, lex, set())
    ok = not dn['negated'] and not ident['num'] and frame['kind'] in ('RELATED', 'COVERED') and 'LXM-REQ-000203' in frame['rids']
    return ok, 'double negation negates nothing: %s; quantities in "writer-62 ... PR-053": %s; framed list item -> %s %s' % (
        not dn['negated'], sorted(ident['num']) or 'none', frame['kind'], ','.join(frame['rids']))


def s_ledger_in_progress(d, b):
    # a clause ledger blocks nothing while in progress; once declared complete, every clause must be covered or held
    open(d + '/sources/SRC-9001.extract.md', 'w').write('a\nb\n')
    sha = A.hashlib.sha256(open(d + '/sources/SRC-9001.extract.md', 'rb').read()).hexdigest()
    led = lambda st: open(d + '/sources/SRC-9001.clauses', 'w').write('status: %s\nextract: sources/SRC-9001.extract.md sha256 %s\n§1 | 1-1 | x\n§2 | 2-2 | y\n' % (st, sha))
    led('in-progress')
    r = A.assimilate(d, ctb(d, 'led', text=R192))
    ok1, det = accepted(d, r, 'RECOGNIZE-EXACT')
    led('complete'); rebuild(d, d + '/out'); v_bad, l_bad = validate(d)
    r2 = A.assimilate(d, ctb(d, 'led2', section='§2', text='Never invent owner approvals, financial policies or production readiness.'))
    v_ok, l_ok = validate(d)
    return ok1 and not v_bad and r2['outcome'] in ('RECOGNIZE-SEMANTIC', 'RECOGNIZE-EXACT') and v_ok, \
        'in progress: %s; declared complete with §2 open -> validator %s; after §2 is recognized -> %s' % (r['outcome'], l_bad, l_ok)


def s_resolved_without_clause(d, b):
    # a resolved exception of a contribution with no clause (recorded as '?') has no clause to cover; one with a real clause must
    ep = d + '/intake/exceptions.txt'
    base = open(ep, encoding='utf-8').read() if os.path.exists(ep) else ''
    entry = lambda n, cl: '\n@LXM-EXC-9%05d | RESOLVED | CTB-FIX-%d | 0\nsource: SRC-9001 %s\nreason: r\nimpact: i\nresolution: x\nresolved: 2026-10-31; NOOP by CTB-FIX-%d\n' % (n, n, cl, n)
    open(ep, 'w', encoding='utf-8').write(base + entry(1, '?'))
    v_ok, l_ok = validate(d)
    open(ep, 'w', encoding='utf-8').write(base + entry(1, '?') + entry(2, '§9.9'))
    v_bad, l_bad = validate(d)
    open(ep, 'w', encoding='utf-8').write(base)
    return v_ok and not v_bad, 'no clause -> validator %s; uncovered real clause -> %s' % (l_ok, l_bad)


def row91(d):
    m = open(d + '/out/LXM-MASTER.md', encoding='utf-8').read().split('**SRC-9001**')[1]
    return [l for l in m.split('\n') if l.startswith('| §1 | 1-1 |')][0]


def s_noop_closes_hold(d, b):
    # a resubmission with nothing to change that closes a held item regenerates the Master (outcome CLOSE), so it no longer shows the item as held
    open(d + '/sources/SRC-9001.extract.md', 'w').write('a\n')
    sha = A.hashlib.sha256(open(d + '/sources/SRC-9001.extract.md', 'rb').read()).hexdigest()
    open(d + '/sources/SRC-9001.clauses', 'w').write('status: in-progress\nextract: sources/SRC-9001.extract.md sha256 %s\n§1 | 1-1 | x\n' % sha)
    A.assimilate(d, ctb(d, 'rec', text=R192))
    r1 = A.assimilate(d, ctb(d, 'held', text='Every synthetic fixture shopper receives a printed receipt in a sealed envelope.'))
    shown_now = 'LXM-EXC-' in row91(d) and reproducible(d)  # the hold shows at once, not at the next accepted change
    open(d + '/tr.ctb', 'w').write('id: CTB-tr\nkind: trace\nrequirement: LXM-REQ-000192\naction: add\nimpl: lib/x.js\nbasis: fixture\n')
    r0 = A.assimilate(d, d + '/tr.ctb')  # an accepted change regenerates the Master while the item is held
    shown = 'LXM-EXC-' in row91(d)
    r2 = A.assimilate(d, ctb(d, 'held', text=R192))
    held = 'LXM-EXC-' in row91(d)
    return shown_now and shown and r0['outcome'] == 'NEW' and r1['outcome'] == 'REJECTED' and r2['outcome'] == 'CLOSE' and reproducible(d) and not held and A.state_matches_log(d)[0], \
        'refused: %s (shown held at once: %s); later change %s, shown held after it: %s; resubmitted: %s; Master equals a fresh generation: %s; still shown held: %s' % (r1['outcome'], shown_now, r0['outcome'] + ' ' + str(r0.get('reason'))[:120], shown, r2['outcome'], reproducible(d), held)


def s_add_clause(d, b):
    # an in-progress ledger gains a clause capture missed; overlaps, closed ledgers and replays are handled
    open(d + '/sources/SRC-9001.extract.md', 'w').write('first line\nsecond line\n')
    sha = A.hashlib.sha256(open(d + '/sources/SRC-9001.extract.md', 'rb').read()).hexdigest()
    open(d + '/sources/SRC-9001.clauses', 'w').write('status: in-progress\nextract: sources/SRC-9001.extract.md sha256 %s\n%s1 | 1-1 | x\n' % (sha, A.X('{cl-}')))
    def add(name, sec, lines):
        p = d + '/' + name + '.ctb'
        open(p, 'w').write('id: CTB-%s\nkind: source\nsource: SRC-9001\naction: add-clause\nsection: %s\nlines: %s\nbasis: fixture\n' % (name, sec, lines))
        return A.assimilate(d, p)['outcome']
    r1 = add('ac1', A.X('{cl-}2'), '2-2'); r2 = add('ac1', A.X('{cl-}2'), '2-2'); r3 = add('ac2', A.X('{cl-}3'), '1-2')
    led = open(d + '/sources/SRC-9001.clauses').read()
    open(d + '/sources/SRC-9001.clauses', 'w').write(led.replace('status: in-progress', 'status: complete'))
    r4 = add('ac3', A.X('{cl-}4'), '2-2')
    r5 = add('ac1', A.X('{cl-}2'), '2-2')  # replaying the earlier addition after the ledger closed
    open(d + '/sources/SRC-9001.clauses', 'w').write(led)
    ok = (r1, r2, r3, r4, r5) == ('EXTEND', 'NOOP', 'REJECTED', 'REJECTED', 'NOOP') and A.X('{cl-}2 | 2-2 |') in led
    return ok, 'new clause %s; replay %s; overlapping lines %s; closed ledger %s; replay after closing %s' % (r1, r2, r3, r4, r5)


def s_retract_relation(d, b):
    # a coverage relation recorded by a false match is retracted through the gate; the record's text is untouched; a replay
    # is a NOOP; a malformed retraction is refused
    rec = 'LXM-REQ-000192'
    r1 = A.assimilate(d, ctb(d, 'rel-add', text=R192))  # a real recognition gives SRC-9001 §1 a relation to the record
    before = A.field(A.blocks(open(d + '/reqs.txt').read())[rec], 'x')
    def retract(name, **kv):
        p = d + '/' + name + '.ctb'
        fields = dict(kind='relation', action='retract', record=rec, source='SRC-9001', section=A.X('{cl-}1'), relation='covers', basis='fixture: a false match')
        fields.update(kv)
        open(p, 'w').write('id: CTB-%s\n' % name + ''.join('%s: %s\n' % (k, v) for k, v in fields.items()))
        return A.assimilate(d, p)['outcome']
    r2 = retract('rt1'); r3 = retract('rt1'); r4 = retract('rt2', relation='resembles')
    after = A.blocks(open(d + '/reqs.txt').read())[rec]
    gone = 'SRC-9001' not in A.field(after, 'c') and 'SRC-9001' not in A.field(after, 's')
    v, line = validate(d)
    ok = r1['outcome'] in ('RECOGNIZE-EXACT', 'RECOGNIZE-SEMANTIC') and (r2, r3, r4) == ('RETRACT', 'NOOP', 'REJECTED') and gone and A.field(after, 'x') == before and v
    return ok, 'recognized %s; retract %s; replay %s; malformed %s; relation and lineage gone %s; text unchanged %s; validator %s' % (r1['outcome'], r2, r3, r4, gone, A.field(after, 'x') == before, line)


for args in [
    ('Exact duplicate', 'a second copy of an existing record', s_exact),
    ('Semantic duplicate, different terminology', 'a reworded duplicate', s_semantic),
    ('Partial overlap', 're-authoring the covered half', s_partial),
    ('Extension of an existing requirement', 'a parallel near-copy record', s_extend),
    ('Composition of complementary requirements', 'a new record restating two existing ones', s_compose),
    ('Contradictory requirement', 'competing authorities', s_contradiction),
    ('Superseding a previous version', 'losing version history', s_supersede),
    ('Supersession without authority', 'replacement by a historical source', s_supersede_unauthorised),
    ('Genuinely new requirement', 'an orphan record no stage applies', s_new),
    ('New requirement without identity data', 'an unplaced record', s_new_needs_identity),
    ('Ambiguous overlap, then resolved', 'silent acceptance of ambiguity', s_ambiguous),
    ('Declared recognition (supported / unsupported)', 'recognition by assertion alone', s_declared_recognition),
    ('Whole-Master candidate discovery', 'matching only a subset of records', s_whole_master_discovery),
    ('Later source recognizes an SRC-0008 record', 'snapshot checks blocking valid growth', s_later_recognition_of_new_record),
    ('Gate infrastructure failure', 'a crash leaving state or log inconsistent', s_infrastructure_error),
    ('Invalid contribution', 'malformed input', s_invalid),
    ('Missing source provenance', 'unsourced knowledge', s_no_provenance),
    ('Broken dependency or relationship', 'dangling references', s_broken_dependency),
    ('Invariant failure found in staged validation', 'a Master that fails validate.py', s_validation_blocks),
    ('Owner-decided content', 'overriding an owner decision', s_owner_decided),
    ('Owner hold survives rephrasing', 'bypassing an owner decision as a new record', s_owner_hold_sticks),
    ('Decision authority: negative and positive', 'any decision authorizing a change outside its adopted scope', s_decision_authority),
    ('K1-K8: binding, empty authorization scope', 'an adopted decision\'s existence authorizing changes', s_k_decisions),
    ('Decision register is data', 'authority granted by prose instead of the register', s_register_is_data),
    ('Stable stage-action IDs', 'a citation landing in the wrong action after reordering', s_stable_action_ids),
    ('Decision adapter: open, adopt with approval, immutable', 'decisions recorded or edited without the owner\'s approval', s_decision_adapter),
    ('Evidence adapter: add, never edit, supersede', 'evidence edited in place or recorded without provenance', s_evidence_adapter),
    ('Adopted decision LXM-DEC-000014 applied', 'duplicate criteria, open holds or a changed E1-E5 record', s_adopted_decision_applied),
    ('Repeated assimilation', 'non-idempotent replay', s_repeat),
    ('Replay after a later change', 'an old supersession reverting later versions', s_replay_after_later_change),
    ('Replay after the record became owner-decided', 'an applied change re-judged and refused on replay', s_replay_after_owner_decision),
    ('Replay by identity after the Master grows', 'replays re-judged once records change', s_replay_by_identity),
    ('Tamper-evident log; Level 2 rebuilt from recorded mutations', 'an altered log, or a registry that cannot be rebuilt', s_chain_and_projection),
    ('Scopes are registered data, not a fixed list', 'a closed list of scopes in code', s_open_scopes),
    ('Every kind through the gate; direct edits detected', 'canonical files changed outside the gate', s_all_kinds),
    ('One contribution, several source clauses', 'malformed multi-clause coverage', s_multi_clause),
    ('Governed matching rules', 'false contradictions and diluted list items', s_matching_rules),
    ('Clause ledger in progress, then complete', 'incremental assimilation blocked, or completeness unchecked', s_ledger_in_progress),
    ('Resolved exception without a clause', 'a clause-less contribution failing a coverage check', s_resolved_without_clause),
    ('NOOP resubmission closes a hold', 'a generated Master showing a closed item as held', s_noop_closes_hold),
    ('A missed clause joins an in-progress ledger', 'a source sentence silently left out of its ledger', s_add_clause),
    ('A relation recorded by a false match is retracted', 'a wrong coverage link that can never be corrected', s_retract_relation),
    ('Interrupted commit', 'a half-applied mutation', s_interrupted_commit)]:
    scenario(*args)

fails = 0
for name, prevents, ok, detail in results:
    fails += not ok
    print('%s  %-46s prevents %-42s %s' % ('PASS' if ok else 'FAIL', name, prevents, detail))
print('\n%d scenarios, %d failed' % (len(results), fails))
sys.exit(1 if fails else 0)
