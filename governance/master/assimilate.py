"""Master assimilation gate (LXM-ACP-001; LXM-REQ-000220 to LXM-REQ-000226).
Usage: python3 -I assimilate.py <root> <contribution> [--dry-run]

Receive -> discover -> classify -> resolve -> validate -> assimilate -> propagate.
Canonical state is CANON plus the generated DERIVED files under <root>. A mutation is applied to a staging copy,
regenerated with build.py and accepted only if validate.py and the gate's own checks pass; it is then committed
atomically through a roll-forward journal. A rejected or quarantined contribution changes none of the canonical state;
it is recorded as an LXM-EXC entry in <root>/intake/exceptions.txt with its reason, impact and required resolution."""
import hashlib, importlib.util, json, os, re, shutil, subprocess, sys, tempfile, time

sys.dont_write_bytecode = True  # a check never changes the Master directory (no __pycache__)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from ids import X, ID_LEN, PREFIX_LEN, DIGITS  # identifier formats come from ids.json (LXM-REQ-000240)

_HERE = os.path.dirname(os.path.abspath(__file__))
LAYOUT = json.load(open(os.path.join(_HERE, X('{@layout_json}')), encoding='utf-8'))  # where the Master keeps what (LXM-REQ-000240)
_N = LAYOUT['names']
CANON, DERIVED, TOOLS = [_N[k] for k in LAYOUT['canon']], [_N[k] for k in LAYOUT['derived']], [_N[k] for k in LAYOUT['tools']]  # TOOLS: everything build, validate and the staged checks read
MATCH = json.load(open(os.path.join(_HERE, X('{@gate_json}')), encoding='utf-8'))['matching']  # the gate's matching rules, versioned with the gate
T_COVER, T_RELATED, T_CONFLICT = MATCH['cover'], MATCH['related'], MATCH['conflict']  # a contradiction needs the same shared meaning for negations and for numbers
COL = {c: i for i, c in enumerate(LAYOUT['sources_columns'])}  # the columns of the sources register, by name
REPORT = json.load(open(os.path.join(_HERE, _N['reporting_json']), encoding='utf-8'))  # how much the reports show
KINDS = json.load(open(os.path.join(_HERE, X('{@kinds_json}')), encoding='utf-8'))  # the entry contract: kinds, their targets and fields (LXM-REQ-000253)
KIND_FIELDS = {k: set(v['fields']) | set(KINDS['common']) for k, v in KINDS['kinds'].items()}
FIELDS = KIND_FIELDS['requirement']
FORMATS = json.load(open(os.path.join(_HERE, X('{@contribution_formats_json}')), encoding='utf-8'))['formats']  # how a contribution may be written
REGISTRIES = [_N[k] for k in LAYOUT['registries']]  # registries are knowledge: they change only through the gate (kind: registry)
ITEMS = {_N[k]: dict(v, start=re.compile(X(v['start']), re.M)) for k, v in LAYOUT['items'].items()}  # how a canonical file splits into versioned items
REQ = re.compile(X(r'{req}'))


# ---------- canonical model ----------

def read(p): return open(p, encoding='utf-8').read()
def sha(b): return hashlib.sha256(b if isinstance(b, bytes) else b.encode('utf-8')).hexdigest()


def blocks(reqs_text):
    """Record blocks with their span, so an edit rewrites only the records it touches."""
    out = {}
    for m in re.finditer(X(r'^@({req}) \|[^\n]*\n(?:[a-z]: [^\n]*\n?)*'), reqs_text, re.M):
        rid = m.group(1)
        head = m.group(0).split('\n', 1)[0]
        _, scope, cls, disp = [x.strip() for x in head[1:].split('|')]
        rec = {'id': rid, 'scope': scope, 'cls': cls, 'disp': disp, 'fields': [], 'span': m.span()}
        for line in m.group(0).split('\n')[1:]:
            if line:
                k, _, v = line.partition(': ')
                rec['fields'].append([k, v])
        out[rid] = rec
    return out


def field(rec, k):
    return next((v for kk, v in rec['fields'] if kk == k), '')


def set_field(rec, k, v, before='x'):
    for f in rec['fields']:
        if f[0] == k:
            f[1] = v
            return
    i = next(i for i, f in enumerate(rec['fields']) if f[0] == before)
    rec['fields'].insert(i, [k, v])


def render(rec):
    return '@%s | %s | %s | %s\n' % (rec['id'], rec['scope'], rec['cls'], rec['disp']) + \
        ''.join('%s: %s\n' % (k, v) for k, v in rec['fields'])


def sources(root):
    return {c[COL['id']]: {'authority': c[COL['authority']], 'text_status': c[COL['text_status']] if len(c) > COL['text_status'] else 'unknown'} for c in
            ([x.strip() for x in l.split(' | ')] for l in read(os.path.join(root, X('{@sources_txt}'))).split('\n') if l.startswith(X('{src-}')))}


ACTION = re.compile(X(r'^({stg})(?:\.A-| #)(\d+)$'))  # STG-NN.A-k; the legacy "STG-NN #k" names the same stable ID, never a position


def stage_actions(stages_text):
    """Stage actions by stable ID: {stage: {k: line index}} for each "- A-k" line."""
    out, cur = {}, None
    for i, line in enumerate(stages_text.split('\n')):
        if line.startswith(X('#{stg~}')):
            cur = line[1:1 + ID_LEN['stg']]  # after the heading marker: the stage ID
            out[cur] = {}
        elif cur and line.startswith('- '):
            out[cur][int(re.match(r'- A-(\d+) ', line).group(1))] = i
    return out


# ---------- matching ----------

class Lexicon:
    def __init__(self, path):
        self.phrases, self.words, self.stop, self.neg, self.frames = [], {}, set(), set(), []
        for line in read(path).split('\n'):
            if not line.strip() or line.startswith('#'):
                continue
            key, _, vals = line.partition(':')
            items = [v.strip().lower() for v in vals.split(',') if v.strip()]
            if key == '@stop':
                self.stop = set(items)
            elif key == '@neg':
                self.neg = {self.stem(w) for w in items}
            elif key == '@frame':
                self.frames = sorted(items, key=len, reverse=True)
            else:
                canon = key if ' ' in key else self.stem(key)
                for v in items:
                    (self.phrases.append((v, key)) if (' ' in v or '-' in v) else self.words.__setitem__(self.stem(v), canon))
        self.phrases.sort(key=lambda p: -len(p[0]))

    @staticmethod
    def stem(w):
        """The stem of a word, by the stemming rules in gate.json (matching.stemming)."""
        rules = MATCH['stemming']
        for r in rules['first_of']:
            if len(w) > r['longer_than'] and w.endswith(r['suffix']) and not (r.get('unless_suffix') and w.endswith(r['unless_suffix'])):
                w = w[:-len(r['suffix'])] + r['replace']
                break
        for r in rules['then']:
            if len(w) > r['longer_than'] and w.endswith(r['suffix']):
                w = w[:-len(r['suffix'])] + r['replace']
        u = rules['undouble']
        if len(w) > u['longer_than'] and w[-1] == w[-2] and w[-1] not in u['keep']:
            w = w[:-1]
        return w

    def norm(self, text):
        text = re.sub(r'\b\d{4}-\d{2}-\d{2}(?:t[\d:.]+z?)?\b', ' ', text.lower())  # a calendar date is a time reference, not a quantity
        text = re.sub(r'[\w.-]*/[\w./-]+|\b[\w-]+\.(?:md|json|txt|js|py|yml|yaml)\b', lambda m: re.sub(r'\d', '', m.group(0)), text)  # a path is an identifier
        t = ' ' + re.sub(r'(?<![a-z0-9])([a-z]+)-(\d+)(?![a-z0-9])', r'\1\2', text) + ' '  # writer-62, PR-053: identifiers, not quantities
        for f in self.frames:  # a list lead-in scopes the item; the item carries the meaning
            t = re.sub(r'(?<![a-z0-9])' + re.escape(f) + r'(?![a-z0-9])', ' ', t)
        for p, c in self.phrases:
            t = re.sub(r'(?<![a-z0-9])' + re.escape(p) + r'(?![a-z0-9])', ' ' + c + ' ', t)
        out = []
        for w in re.findall(r'[a-z0-9]+', t):
            if w in self.stop:
                continue
            s = self.stem(w)
            out.append(self.words.get(s, self.words.get(w, s)))
        return out

    def profile(self, text):
        toks, negated = self.norm(text), set()
        parts = re.split(r'([,;:.()])', text)
        carry = False  # "No configuration, valid or invalid, may bypass ...": a short negated subject carries its negation
        for seg, delim in zip(parts[0::2], parts[1::2] + ['']):  # through the commas of its sentence, to the next ; : . or (
            if carry:
                negated |= {t for t in self.norm(seg) if t not in self.neg}
                carry = delim == ','
                continue
            if re.match(r'\s*(if|unless|when|where|until|whether)\b', seg, re.I):
                continue  # a negation inside a condition states a case, not a prohibition
            st = self.norm(seg)
            if re.search(r'\b(?:no|not|never|nothing)\b.*\b(?:without|unless|except)\b', seg, re.I):
                continue  # "no X without Y", "never X unless Y": a double negation states an obligation, not a prohibition
                          # ("no X and not Y" is two negations, not a double negation)
            i = next((i for i, t in enumerate(st) if t in self.neg), None)
            if i is not None:
                negated |= {t for t in st[i + 1:] if t not in self.neg}
                carry = delim == ',' and i == 0 and len(st) <= 3
        content = {t for t in toks if t not in self.neg and not t.isdigit()}
        return {'seq': ' '.join(toks), 'negated': negated, 'asserted': content - negated,
                'num': {t for t in toks if t.isdigit()}, 'set': content}


def sentences(text):
    return [s.strip() for s in re.split(r'(?<=[.;])\s+(?=[A-Z(])', text.strip()) if s.strip()]


def containment(a, b):
    return len(a & b) / len(a) if a else 0.0


def classify(clause, recs, lex, distinct):
    """One clause against every record: EXACT, COVERED (one record or a composition of two), CONFLICT, RELATED or NOVEL."""
    c = lex.profile(clause)
    scored, conflicts = [], []
    for rid, r in recs.items():
        if rid in distinct:
            continue
        rp = r['_profile']
        if c['seq'] and c['seq'] in rp['seq']:
            return {'kind': 'EXACT', 'rids': [rid], 'score': 1.0}
        scored.append((containment(c['set'], rp['set']), rid))
        for s in r['_sent']:
            share = containment(c['set'], s['set'])
            if share < T_RELATED:
                continue
            for neg, pos in ((s['negated'], c['asserted']), (c['negated'], s['asserted'])):
                hit = neg & pos
                if share >= T_CONFLICT and len(hit) >= MATCH['conflict_min_shared_terms'] and len(hit) >= MATCH['conflict_min_share_of_negated'] * len(neg):
                    conflicts.append((share, rid))
            if share >= T_CONFLICT and c['num'] and s['num'] and c['num'] != s['num']:
                conflicts.append((share, rid))
    if conflicts:
        share, rid = max(conflicts)
        return {'kind': 'CONFLICT', 'rids': [rid], 'score': round(share, 2)}
    scored.sort(reverse=True)
    best, rid = scored[0]
    if best >= T_COVER:
        return {'kind': 'COVERED', 'rids': [rid], 'score': round(best, 2)}
    top = [r for _, r in scored[:MATCH['composition_candidates']]]
    pairs = [(containment(c['set'], recs[a]['_profile']['set'] | recs[b]['_profile']['set']), a, b) for i, a in enumerate(top) for b in top[i + 1:]]
    if pairs:
        pb, a, b = max(pairs)
        pa, pq = c['set'] & recs[a]['_profile']['set'], c['set'] & recs[b]['_profile']['set']
        if pb >= T_COVER and len(pa - pq) >= MATCH['composition_min_distinct_terms'] and len(pq - pa) >= MATCH['composition_min_distinct_terms']:
            return {'kind': 'COVERED', 'rids': sorted([a, b]), 'score': round(pb, 2)}
    kind = 'RELATED' if best >= T_RELATED else 'NOVEL'
    return {'kind': kind, 'rids': [r for s, r in scored[:MATCH['related_candidates_reported']] if s >= T_RELATED], 'score': round(best, 2)}


def index(recs, lex):
    for r in recs.values():
        x = field(r, 'x')
        r['_profile'] = lex.profile(x)
        r['_profile']['set'] |= lex.profile(field(r, 't'))['set']
        r['_sent'] = [lex.profile(s) for s in sentences(x)]


# ---------- the gate ----------

def receive(path):
    """The contribution's fields, read by the first registered format (contribution-formats.json) that detects it. _format is
    None when no registered format reads it; the gate then refuses it. The SHA-256 of the exact bytes is its identity."""
    raw = open(path, 'rb').read(); body = raw.decode('utf-8')
    first = next((l for l in body.split('\n') if l.strip()), '')
    fmt = next((f for f in FORMATS if re.search(f['detect'], first)), None)
    ctb = PARSERS[fmt['parser']](body, fmt) if fmt else {}
    ctb.update(_sha=sha(raw), _path=os.path.abspath(path), _format=fmt['name'] if fmt else None)
    return ctb


def _parse_fields(body, fmt):
    ctb, key = {}, None
    for line in body.split('\n'):
        m = re.match(fmt['key'], line)
        if m:
            key = m.group(1)
            ctb[key] = m.group(2).strip()
        elif line.strip() and key == fmt['continue_field']:
            ctb[key] += ' ' + line.strip()
    return ctb


def _parse_json(body, fmt):
    try:
        obj = json.loads(body)
    except ValueError:
        return {}
    if not isinstance(obj, dict) or not all(isinstance(v, str) for v in obj.values()):
        return {}
    return {k: ' '.join(v.split()) for k, v in obj.items()}  # whitespace as the line format reads it: one contribution, one judgement


PARSERS = {'fields': _parse_fields, 'json': _parse_json}  # reading mechanisms; which formats use them is registered data


class Refusal(Exception):
    def __init__(self, outcome, reason, impact, resolution, detail=None):
        super().__init__(reason)
        self.outcome, self.reason, self.impact, self.resolution, self.detail = outcome, reason, impact, resolution, detail


def reject(reason, resolution, impact='The contribution is not accepted; canonical state is unchanged.'):
    raise Refusal('REJECTED', reason, impact, resolution)


def check_contribution(ctb, recs, srcs, actions):
    unknown = sorted(set(k for k in ctb if not k.startswith('_')) - FIELDS)
    if unknown:
        reject('Unknown fields: %s' % ', '.join(unknown), 'Use only the requirement fields registered in %s.' % X('{@kinds_json}'))
    for k in ('id', 'kind', 'text'):
        if not ctb.get(k):
            reject('Missing required field "%s"' % k, 'Supply "%s".' % k)
    if ctb['kind'] != 'requirement':
        reject('Unsupported kind "%s"' % ctb['kind'], 'Registered kinds (%s): %s.' % (X('{@kinds_json}'), ', '.join(sorted(KINDS['kinds']))))
    if len(ctb['text']) < MATCH['min_contribution_text'] or not re.search(r'[a-z]{3}', ctb['text']):
        reject('Text is too short to carry a requirement', 'State the obligation as at least one complete sentence.')
    if not ctb.get('source') or not ctb.get('section'):
        reject('Missing source provenance (source and section)', 'Name a registered source ID from sources.txt and the section it comes from.')
    if ctb['source'] not in srcs:
        reject('Source %s is not in the source register' % ctb['source'], 'Register the source in sources.txt (with its authority) before contributing from it.')
    if ctb.get('scope') and ctb['scope'] not in actions.get('_scopes', set()):
        reject('Unknown scope "%s"' % ctb['scope'], 'Use a registered scope (scopes.txt or a stage of stages.txt): %s.' % ', '.join(sorted(actions.get('_scopes', set()))))
    for k in ('extends', 'supersedes', 'depends', 'distinct-from', 'relates', 'recognized-as'):
        for rid in REQ.findall(ctb.get(k, '')):
            if rid not in recs:
                reject('Broken relationship: %s refers to %s, which does not exist' % (k, rid), 'Correct the reference or assimilate %s first.' % rid)
        if ctb.get(k) and not REQ.findall(ctb[k]):
            reject('Field "%s" holds no requirement ID' % k, X('Give {req#} identifiers.'))
    if ctb.get('supersedes') and not ctb.get('reason'):
        reject('Supersession without a recorded reason', 'State why the earlier version is replaced (reason:).')
    if ctb.get('applied-in'):
        m = ACTION.match(ctb['applied-in'])
        if not m or int(m.group(2)) not in actions.get(m.group(1), {}):
            reject('Broken relationship: applied-in "%s" names no existing stage action' % ctb['applied-in'], X('Use "{stg#}.A-k", the stable ID of an existing action of stage {stg#}.'))
    if ctb.get('relates') and not re.fullmatch(X(r'({req} (supports|depends-on)(, )?)+'), ctb['relates']):
        reject('Malformed relates "%s"' % ctb['relates'], X('Use "{req#} supports" or "{req#} depends-on", comma separated.'))


def lineage_has(s, source, section):
    top = section.split('.')[0]
    for m in re.finditer(re.escape(source) + X(r' ((?:{cl-}[\d.\-]+,?)+)'), s):
        secs = m.group(1).split(',')
        if section in secs or top in secs:
            return True
    return False


def add_lineage(rec, source, sections):
    s, added = field(rec, 's'), False
    for section in sections.split(','):
        if lineage_has(s, source, section):
            continue
        m = re.search(re.escape(source) + X(r' ((?:{cl-}[\d.\-]+,?)+)'), s)
        s = (s[:m.end()] + ',' + section + s[m.end():]) if m else (s + '; %s %s' % (source, section))
        added = True
    if added:
        set_field(rec, 's', s)
    return added


def add_coverage(rec, source, clause, rel):
    tok = '%s %s %s' % (source, clause, rel)
    c = field(rec, 'c')
    have = [x.strip() for x in c.split(';')]
    if tok in have or (rel == 'covers' and '%s %s extends' % (source, clause) in have):  # text it added already covers it
        return False
    set_field(rec, 'c', (c + '; ' + tok) if c else tok)
    return True


def owner_decided(rec, srcs):
    """Content fixed by a recorded owner decision: a decision reference, or lineage to an owner-decision source."""
    s = field(rec, 's') + ' ' + field(rec, 'k')
    return bool(re.search(X(r'{dec}'), s)) or rec['disp'] == 'Owner-decision' or \
        any(src in s for src, v in srcs.items() if v['authority'] == 'owner-decision')


def guard_owner_decided(rid, recs, srcs, ctb, decisions):
    if owner_decided(recs[rid], srcs) and not authorized(ctb, decisions, rid, recs):
        raise Refusal('QUARANTINED', '%s carries content fixed by an owner decision; changing it is owner-reserved%s' % (rid, not_authorized(ctb, decisions)),
                      'Changing it without the owner would override a recorded owner decision.',
                      X('The owner decides; record the decision in decisions.txt (rendered as Part C) and resubmit with decision: {dec#}.'))


def resolve(ctb, recs, srcs, lex, decisions={}):
    """Classify every clause and derive the minimum correct mutation. Returns (outcome, plan, clauses)."""
    distinct = set(REQ.findall(ctb.get('distinct-from', '')))
    sup = (REQ.findall(ctb.get('supersedes', '')) or [None])[0]
    ext = (REQ.findall(ctb.get('extends', '')) or [None])[0]
    owner = srcs[ctb['source']]['authority'] in ('owner', 'owner-decision')
    clauses = [dict(text=t, n=i, **classify(t, recs, lex, distinct)) for i, t in enumerate(sentences(ctb['text']), 1)]
    for rid in REQ.findall(ctb.get('recognized-as', '')):  # a declared recognition must still be supported by the text
        for cl in clauses:
            if cl['kind'] == 'RELATED' and rid in cl['rids']:
                cl.update(kind='COVERED', rids=[rid], declared=True)
        if not any(rid in cl['rids'] and cl['kind'] in ('EXACT', 'COVERED') for cl in clauses):
            reject('recognized-as %s is not supported: no clause shares enough meaning with it' % rid,
                   'Recognize only records that express the clause; otherwise extend, create or withdraw.')
    src, sec = ctb['source'], ctb['section']
    cids = sec.split(',')  # coverage names each cited source clause itself, never an invented sub-clause
    plan = []

    if sup:
        if not owner:
            reject('Source %s has historical authority and cannot supersede %s' % (src, sup), 'Supersession needs an owner-authority source.')
        foreign = [cl for cl in clauses if cl['kind'] == 'CONFLICT' and cl['rids'] != [sup]]
        if foreign:
            raise Refusal('QUARANTINED', 'Contradiction with records other than the one superseded: %s' % ', '.join(cl['rids'][0] for cl in foreign),
                          'Accepting would leave the Master internally contradictory.', 'Supersede or reconcile those records too, or narrow the contribution.', clauses)
        target = recs[sup]
        if field(target, 'x') == ctb['text'] or any(k == 'h' and ' (by %s %s: %s): ' % (src, sec, ctb['reason']) in v for k, v in target['fields']):
            return 'NOOP', [], clauses  # already applied: checked before any guard, so a replay never re-judges (or reverts) an applied change
        guard_owner_decided(sup, recs, srcs, ctb, decisions)
        guard_decision_cited(ctb, decisions, sup, recs)
        plan.append(('supersede', sup, ctb['text'], '%s %s' % (src, sec), ctb['reason']))
        if ctb.get('decision'):
            plan.append(('decision', sup, ctb['decision']))
        plan += [('lineage', sup, src, sec)] + [('coverage', sup, src, s, 'covers') for s in sec.split(',')]
        return 'SUPERSEDE', plan, clauses

    conflicts = [cl for cl in clauses if cl['kind'] == 'CONFLICT']
    if conflicts:
        raise Refusal('QUARANTINED', 'Contradiction: ' + '; '.join('clause %d contradicts %s (shared meaning %.2f)' % (cl['n'], cl['rids'][0], cl['score']) for cl in conflicts),
                      'Accepting would create two competing authorities for the same obligation.',
                      X('An owner-authority source either supersedes the record (supersedes: + reason:) or the contribution is withdrawn; unresolvable conflicts go to the owner ({req=000016} E4).'), clauses)

    covered = [cl for cl in clauses if cl['kind'] in ('EXACT', 'COVERED')]
    rest = [cl for cl in clauses if cl not in covered]
    for cl in covered:
        for rid in cl['rids']:
            plan += [('lineage', rid, src, sec)] + [('coverage', rid, src, c, 'covers') for c in cids]
    for part in [p.strip() for p in ctb.get('relates', '').split(',') if p.strip()]:
        rid, rel = part.split()
        plan += [('coverage', rid, src, s, rel) for s in sec.split(',')]
    if rest and not owner:
        reject('Source %s has historical authority; only recognition is possible, but %d clause(s) are not yet canonical' % (src, len(rest)),
               'Obtain the requirement from an owner-authority source.')
    if rest and ext:
        guard_owner_decided(ext, recs, srcs, ctb, decisions)
        plan += [('append', ext, ' '.join(cl['text'] for cl in rest)), ('lineage', ext, src, sec)]
        plan += [('coverage', ext, src, c, 'extends') for c in cids]
        if ctb.get('decision'):
            plan.append(('decision', ext, ctb['decision']))
        outcome = 'PARTIAL→EXTEND' if covered else 'EXTEND'
    elif rest:
        amb = [cl for cl in rest if cl['kind'] == 'RELATED']
        if amb:
            raise Refusal('QUARANTINED', 'Ambiguous: ' + '; '.join('clause %d is partly expressed by %s (%.2f) but not covered' % (cl['n'], ', '.join(cl['rids']), cl['score']) for cl in amb),
                          'Creating a record could duplicate existing meaning; extending could attach it to the wrong record.',
                          'Declare extends: <record> to add it there, recognized-as: <record> if that record already expresses it, or distinct-from: <records> to confirm the meaning is new.', clauses)
        missing = [k for k in ('scope', 'title', 'applied-in') if not ctb.get(k)]
        if missing:
            reject('A new canonical identity needs %s' % ', '.join(missing), X('Supply scope, title and the stage action that applies it (applied-in: {stg#} #k).'))
        plan += [('new', ctb['scope'], ctb['title'], ' '.join(cl['text'] for cl in rest), '%s %s' % (src, sec), ctb.get('depends', ''), ctb['applied-in'], ctb.get('decision', ''))]
        outcome = 'PARTIAL→NEW' if covered else 'NEW'
    else:
        rids = {r for cl in covered for r in cl['rids']}
        outcome = 'COMPOSE' if len(rids) > 1 else ('RECOGNIZE-EXACT' if all(cl['kind'] == 'EXACT' for cl in covered) else 'RECOGNIZE-SEMANTIC')
    guard_decision_cited(ctb, decisions, ext if rest and ext else None, recs)
    if ctb.get('depends') and outcome not in ('NEW', 'PARTIAL→NEW'):
        target = ext or (covered[0]['rids'][0] if covered else None)
        if target:
            plan.append(('depends', target, ctb['depends']))
    return outcome, plan, clauses


def apply(plan, reqs_text, stages_text):
    """Apply a plan to texts in memory. Returns (reqs, stages, changed record IDs); no-op steps change nothing."""
    recs = blocks(reqs_text)
    changed, new_ids, stage_lines = set(), [], stages_text.split('\n')
    for step in plan:
        op = step[0]
        if op == 'lineage':
            if add_lineage(recs[step[1]], step[2], step[3]): changed.add(step[1])
        elif op == 'coverage':
            if add_coverage(recs[step[1]], step[2], step[3], step[4]): changed.add(step[1])
        elif op == 'append':
            r = recs[step[1]]
            set_field(r, 'x', field(r, 'x').rstrip() + ' ' + step[2])
            changed.add(step[1])
        elif op == 'depends':
            r = recs[step[1]]
            d = sorted(set(REQ.findall(field(r, 'd'))) | set(REQ.findall(step[2])))
            if ', '.join(d) != field(r, 'd'):
                set_field(r, 'd', ', '.join(d)); changed.add(step[1])
        elif op == 'decision':  # the authorizing decision is recorded on the record it changed, once
            r = recs[step[1]]
            ks = [k for k in field(r, 'k').split(', ') if k]
            if step[2] not in ks:
                set_field(r, 'k', ', '.join(ks + [step[2]]))
                r['fields'].sort(key=lambda f: 'tsknvcdxh'.index(f[0]))
                changed.add(step[1])
        elif op == 'supersede':
            _, rid, text, origin, reason = step
            r = recs[rid]
            ver = int(field(r, 'v') or '1')
            r['fields'].append(['h', 'v%d (by %s: %s): %s' % (ver, origin, reason, field(r, 'x'))])
            set_field(r, 'v', str(ver + 1))
            set_field(r, 'x', text)
            r['fields'].sort(key=lambda f: 'tsknvcdxh'.index(f[0]))
            changed.add(rid)
        elif op == 'new':
            _, scope, title, text, origin, deps, applied, dec = step
            nid = X('{req%}') % (max(int(r[-DIGITS['req']:]) for r in recs) + 1)
            src, sec = origin.split(' ', 1)
            fields = [['t', title], ['s', origin]] + ([['k', dec]] if dec else []) + [['c', '; '.join('%s %s covers' % (src, c) for c in sec.split(','))]]
            if deps:
                fields.append(['d', ', '.join(REQ.findall(deps))])
            fields.append(['x', text])
            recs[nid] = {'id': nid, 'scope': scope, 'cls': 'NEW', 'disp': 'New-owner-addition', 'fields': fields, 'span': None}
            new_ids.append(nid); changed.add(nid)
            stg, k = ACTION.match(applied).groups()
            li = stage_actions('\n'.join(stage_lines))[stg][int(k)]
            stage_lines[li] = re.sub(r'\]\s*$', ', %s]' % nid, stage_lines[li])
    out = reqs_text
    for rid in sorted((r for r in changed if recs[r]['span']), key=lambda r: -recs[r]['span'][0]):
        a, b = recs[rid]['span']
        out = out[:a] + render(recs[rid]) + out[b:]
    for nid in new_ids:
        out = out.rstrip('\n') + '\n\n' + render(recs[nid])
    return out, '\n'.join(stage_lines), sorted(changed)


def registries(root):
    """The registries present under root (a fixture may carry only some)."""
    return [f for f in REGISTRIES if os.path.exists(os.path.join(root, f))]


def knowledge_digest(root):
    """Canonical knowledge only: the canonical files, the registries and the clause ledgers, without the generated Master (a view of them)."""
    ledgers = sorted(X('{@sources_prefix}') + f for f in os.listdir(os.path.join(root, X('{@sources_dir}'))) if f.endswith('.clauses')) if os.path.isdir(os.path.join(root, X('{@sources_dir}'))) else []
    return sha(''.join(sha(open(os.path.join(root, f), 'rb').read()) for f in CANON + registries(root) + ledgers))


def state_digest(root):
    ledgers = sorted(X('{@sources_prefix}') + f for f in os.listdir(os.path.join(root, X('{@sources_dir}')))) if os.path.isdir(os.path.join(root, X('{@sources_dir}'))) else []
    return sha(''.join(sha(open(os.path.join(root, f), 'rb').read()) for f in CANON + registries(root) + DERIVED + ledgers))


# ---------- versions (LXM-REQ-000253) ----------

def items(root):
    """{item: SHA-256 of its text} for every knowledge item: each record, decision, evidence entry, source row, stage and trace
    entry (layout.json items), the rest of each canonical file, every registry and every file under sources/."""
    src = sorted(X('{@sources_prefix}') + f for f in os.listdir(os.path.join(root, X('{@sources_dir}')))) if os.path.isdir(os.path.join(root, X('{@sources_dir}'))) else []
    out = {}
    for f in CANON + registries(root) + src:
        data = open(os.path.join(root, f), 'rb').read()
        rule = ITEMS.get(f)
        if not rule:
            out[f] = sha(data); continue
        text = data.decode('utf-8'); starts = list(rule['start'].finditer(text))
        out[f] = sha(text[:starts[0].start()] if starts else text)
        for i, m in enumerate(starts):
            name = f + '#' + m.group(1) if rule.get('qualify') else m.group(1)
            out[name] = sha(out.get(name, '') + text[m.start():starts[i + 1].start() if i + 1 < len(starts) else len(text)].rstrip('\n'))
    return out


def version_map(root):
    """{item: (version, SHA-256)} as the log records it (SHA-256 None: removed), or None before the log records versions."""
    p, vm, seen = os.path.join(root, LEDGER), {}, False
    for line in (open(p, encoding='utf-8') if os.path.exists(p) else []):
        v = json.loads(line).get('versions') if line.strip() else None
        if v is not None:
            seen = True; vm.update({k: tuple(x) for k, x in v.items()})
    return vm if seen else None


def version_changes(root, vm):
    """{item: [next version, SHA-256 or None]} for every item whose text differs from the version the log records."""
    now, vm = items(root), vm or {}
    ch = {k: [vm.get(k, (0, None))[0] + 1, s] for k, s in now.items() if vm.get(k, (0, None))[1] != s}
    ch.update({k: [n + 1, None] for k, (n, s) in vm.items() if s is not None and k not in now})
    return ch


def outside_gate(root):
    """The items whose current text is no version the gate recorded: knowledge that entered some other way."""
    vm = version_map(root)
    return [] if vm is None else sorted(version_changes(root, vm))


def runtime(root):
    """{runtime: (version, supported)} for the runtimes the gate checks before it runs (runtimes.json)."""
    spec = importlib.util.spec_from_file_location('lxm_runtimes', os.path.join(_HERE, X('{@runtimes_py}')))
    RT = importlib.util.module_from_spec(spec); spec.loader.exec_module(RT)
    return RT.check(root, 'gate')


def recover(root):
    """Finish an interrupted commit: the journal is written only after every staged file is complete."""
    j = os.path.join(root, '.assimilate-journal')
    if os.path.exists(j):
        for f in json.load(open(j)):
            tmp = os.path.join(root, f + '.staged')
            if os.path.exists(tmp):
                os.replace(tmp, os.path.join(root, f))
        os.remove(j)


def commit(root, staging, files):
    for f in files:
        shutil.copyfile(os.path.join(staging, f), os.path.join(root, f + '.staged'))
    with open(os.path.join(root, '.assimilate-journal'), 'w') as fh:
        json.dump(files, fh); fh.flush(); os.fsync(fh.fileno())
    recover(root)


def record_exception(root, ctb, refusal):
    d = os.path.join(root, X('{@intake_dir}')); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, X('{@exceptions_txt}'))
    text = read(p) if os.path.exists(p) else X('# Intake exceptions ({req=000222}). Not canonical; each entry blocks one contribution until resolved.\n')
    m = re.search(X(r'^@({exc}) \| [A-Z]+ \| %s \| %s$') % (re.escape(ctb.get('id', '?')), ctb['_sha']), text, re.M)
    if m:
        return m.group(1)
    n = len(re.findall(X(r'^@{exc-}'), text, re.M)) + 1
    eid = X('{exc%}') % n
    text += '\n@%s | %s | %s | %s\nsource: %s %s\nreason: %s\nimpact: %s\nresolution: %s\n' % (eid, refusal.outcome, ctb.get('id', '?'), ctb['_sha'], ctb.get('source', '?'), ctb.get('section', '?'), refusal.reason, refusal.impact, refusal.resolution)
    open(p, 'w', encoding='utf-8').write(text)
    return eid


def load_build(root):
    """build.py of this root: the one parser for the register and the trace, shared with the generator and the validator."""
    spec = importlib.util.spec_from_file_location('lxm_build', os.path.join(root, X('{@build_py}')))
    build = importlib.util.module_from_spec(spec); spec.loader.exec_module(build)
    return build


DECISION_FIELDS = KIND_FIELDS['decision']
DECISION_KEYS = {'question': 'q', 'facts': 'f', 'options': 'opt', 'recommendation': 'rec', 'outcome': 'o', 'effect': 'e', 'authorizes': 'a',
                 'adopted': 'w', 'provenance': 'p', 'rationale': 'r', 'label': 'label'}
SCOPE_CELL = re.compile(X(r'(?:(?:{src} (?:{cl}(?:, )?)+|{req})(?:, )?)+'))


def resolve_decision(root, ctb):
    """The decision adapter (kind: decision). action: open records a new question (the next ID); action: adopt records the
    owner's adoption of an open decision, only with the owner's approval on file (intake/decisions/, matching SHA-256, naming the
    decision). An adopted decision is never edited. Returns (new decisions.txt text, outcome, changed IDs)."""
    unknown = sorted(set(k for k in ctb if not k.startswith('_')) - DECISION_FIELDS)
    if unknown:
        reject('Unknown fields for a decision: %s' % ', '.join(unknown), 'Use only the decision fields registered in %s.' % X('{@kinds_json}'))
    groups = gate_config(root)['decision_groups']
    build = load_build(root)
    text = read(os.path.join(root, X('{@decisions_txt}')))
    layouts, decs = build.parse_decisions(text)
    by = {d['id']: d for d in decs}
    did, action = ctb.get('decision', ''), ctb.get('action', '')
    if not re.fullmatch(X(r'{dec}'), did) or action not in ('open', 'adopt'):
        reject(X('A decision contribution needs decision: {dec#} and action: open or adopt'), 'Supersession is not implemented yet; it stays a direct, owner-approved edit.')
    fields = {DECISION_KEYS[k]: ctb[k] for k in DECISION_KEYS if ctb.get(k)}
    if action == 'open':
        if did in by:
            if by[did].get('q') == fields.get('q'):
                return text, 'NOOP', []  # this question was opened; replaying the open changes nothing, adopted since or not
            reject('%s already exists' % did, 'Open a new question with the next free ID, or adopt the existing one.')
        nxt = X('{dec%}') % (len(decs) + 1)
        if did != nxt:
            reject('%s is not the next free decision ID (%s)' % (did, nxt), 'Decision IDs are contiguous; use %s.' % nxt)
        if not fields.get('q'):
            reject('An open decision needs its question', 'State the question (question:).')
        block = '@%s | open | %s\n%s' % (did, groups['open'], ''.join('%s: %s\n' % (k, fields[k]) for _, k in layouts[groups['open']][1:] if k in fields))
        return text.rstrip('\n') + '\n\n' + block, 'NEW', [did]
    # adopt
    if did not in by:
        reject('%s is not in the decision register' % did, 'Open the question first (action: open), then record its adoption.')
    cur = by[did]
    if cur['status'] == 'adopted':
        same = all(cur.get(k) == v for k, v in fields.items())
        if same:
            return text, 'NOOP', []
        raise Refusal('QUARANTINED', '%s is adopted; an adopted decision is never edited; owner-reserved' % did,
                      'Changing it would rewrite an owner decision after the fact.', 'Only a later owner decision can supersede it.')
    missing = [k for k in ('outcome', 'effect', 'authorizes', 'adopted', 'provenance', 'rationale', 'approval', 'approval-sha256') if not ctb.get(k)]
    if missing:
        reject('Adoption of %s lacks %s' % (did, ', '.join(missing)), 'An adoption records the outcome, effect, scope, who adopted it, provenance, rationale and the approval on file.')
    ap = os.path.abspath(os.path.join(root, ctb['approval']))  # absolute on both sides, whether the root is given as '.' or a full path
    if not ap.startswith(os.path.abspath(os.path.join(root, X('{@intake_dir}'), 'decisions')) + os.sep) or not os.path.isfile(ap):
        reject('The approval %s is not a file under intake/decisions/' % ctb['approval'], 'Store the owner\'s approval verbatim under intake/decisions/ and cite it.')
    if sha(open(ap, 'rb').read()) != ctb['approval-sha256']:
        reject('The approval file does not match approval-sha256', 'Cite the SHA-256 of the approval exactly as stored.')
    if not re.search(X(r'(?<![\w-])(?:{dec-})?%s(?!\d)') % did[-DIGITS['dec']:], read(ap)):  # named in full, or by its number ("000009")
        reject('The approval does not name %s' % did, 'An approval applies only to the decision it names.')
    if not (fields['a'] == 'None' or SCOPE_CELL.fullmatch(fields['a'])):
        reject('authorizes must be None or source clauses and records, not "%s"' % fields['a'], X('Give "None" or e.g. "{src=0009} {cl-}7.2, {req=000231}".'))
    new = {'q': cur.get('q', '')}
    new.update(fields)
    block = '@%s | adopted | %s\n%s' % (did, groups['adopted'], ''.join('%s: %s\n' % (k, new[k]) for k in ['label', 'q'] + [k for _, k in layouts[groups['adopted']][1:]] if new.get(k)))
    blocks_ = re.split(X(r'\n(?=@{dec-})'), text)
    out = [block.rstrip('\n') + '\n' if b.startswith('@' + did + ' ') else b for b in blocks_]
    return '\n'.join(x.rstrip('\n') + '\n' for x in out).replace('\n\n\n', '\n\n'), 'ADOPT', [did]


EVIDENCE_CTB = KIND_FIELDS['evidence']


def resolve_evidence(root, ctb):
    """The evidence adapter (kind: evidence). action: add records a new observation under the next ID; action: supersede records
    a newer observation that replaces a current one, whose status becomes "superseded by". Evidence is never edited.
    Returns (new evidence.txt text, outcome, changed IDs)."""
    unknown = sorted(set(k for k in ctb if not k.startswith('_')) - EVIDENCE_CTB)
    if unknown:
        reject('Unknown fields for evidence: %s' % ', '.join(unknown), 'Use only the evidence fields registered in %s.' % X('{@kinds_json}'))
    build = load_build(root)
    text = read(os.path.join(root, X('{@evidence_txt}')))
    _, evs = build.parse_evidence(text)
    by = {e['id']: e for e in evs}
    eid, action = ctb.get('evidence', ''), ctb.get('action', '')
    if not re.fullmatch(X(r'{evd}'), eid) or action not in ('add', 'supersede'):
        reject(X('An evidence contribution needs evidence: {evd#} and action: add or supersede'), 'Evidence is never edited; supersede it with a newer observation.')
    keys = [k for k in build.EVIDENCE_FIELDS if k not in ('status',)]
    fields = {k: ctb[k] for k in keys if ctb.get(k)}
    if eid in by:
        if all(by[eid].get(k) == v for k, v in fields.items()):
            return text, 'NOOP', []
        reject('%s exists; evidence is never edited' % eid, 'Record the newer observation under the next ID with action: supersede.')
    nxt = X('{evd%}') % (len(evs) + 1)
    if eid != nxt:
        reject('%s is not the next free evidence ID (%s)' % (eid, nxt), 'Evidence IDs are contiguous; use %s.' % nxt)
    missing = [k for k in ('fact', 'source', 'method', 'observed', 'observer', 'verifies') if not ctb.get(k)]
    if missing:
        reject('Evidence lacks %s' % ', '.join(missing), 'Evidence states the observed fact, where and how it was observed, when, by whom, and what it is evidence for.')
    known = set(re.findall(X(r'^@({req})'), read(os.path.join(root, X('{@reqs_txt}'))), re.M)) | \
        {d['id'] for d in build.parse_decisions(read(os.path.join(root, X('{@decisions_txt}'))))[1]} | set(by)
    refs = re.findall(r'LXM-(?:REQ|DEC|EVD)-\d{6}', fields['verifies'])
    if not refs or set(refs) - known:
        reject('verifies must name existing requirements, decisions or evidence: %s' % (', '.join(sorted(set(refs) - known)) or 'none named'),
               'Name what this observation is evidence for.')
    group = evs[-1]['group'] if evs else 'G.3'
    changed = [eid]
    if action == 'supersede':
        old = ctb.get('supersedes', '')
        if old not in by or by[old].get('status', '').startswith('superseded'):
            reject('supersedes must name current evidence, not "%s"' % old, 'Name the current entry this observation replaces.')
        text = re.sub(r'(^@%s \|[^\n]*\n(?:[a-z]+: [^\n]*\n)*?)status: [^\n]*' % old, lambda m: m.group(1) + 'status: superseded by ' + eid, text, count=1, flags=re.M)
        changed.append(old)
    block = '@%s | %s\n%s' % (eid, group, ''.join('%s: %s\n' % (k, fields[k]) for k in keys if k in fields) + 'status: current\n')
    return text.rstrip('\n') + '\n\n' + block, 'SUPERSEDE' if action == 'supersede' else 'NEW', changed


def _fields(ctb, kind):
    unknown = sorted(set(k for k in ctb if not k.startswith('_')) - KIND_FIELDS[kind])
    if unknown:
        reject('Unknown fields for %s: %s' % (kind, ', '.join(unknown)), 'Use only the %s fields registered in %s.' % (kind, X('{@kinds_json}')))
    if not ctb.get('basis'):
        reject('A %s change states its basis (why it is right)' % kind, 'Add basis: with the evidence or review behind the change.')


def resolve_trace(root, ctb):
    """kind: trace. action add or replace: a requirement's implementation links (impl, spec, config, test) with their basis."""
    _fields(ctb, 'trace')
    rid, action = ctb.get('requirement', ''), ctb.get('action', '')
    if not REQ.fullmatch(rid) or rid not in blocks(read(os.path.join(root, X('{@reqs_txt}')))) or action not in ('add', 'replace'):
        reject('A trace change needs an existing requirement: and action: add or replace', 'Name the requirement whose links change.')
    text = read(os.path.join(root, X('{@trace_txt}')))
    block = '@%s\n%s' % (rid, ''.join('%s: %s\n' % (k, ctb[k]) for k in ('impl', 'spec', 'config', 'test', 'basis') if ctb.get(k)))
    m = re.search(r'^@%s\n(?:[a-z]+: [^\n]*\n)*' % rid, text, re.M)
    if m:
        if m.group(0) == block:
            return text, 'NOOP', []
        if action != 'replace':
            reject('%s is traced already' % rid, 'Use action: replace; the log keeps the earlier links.')
        return text[:m.start()] + block + text[m.end():], 'SUPERSEDE', [rid]
    if action != 'add':
        reject('%s has no trace to replace' % rid, 'Use action: add.')
    return text.rstrip('\n') + '\n\n' + block, 'NEW', [rid]


def resolve_scope(root, ctb):
    """kind: scope. action add: a new requirement scope, placed after an existing scope line (or @stages)."""
    _fields(ctb, 'scope')
    sid, name, after = ctb.get('scope', ''), ctb.get('name', ''), ctb.get('after', '')
    text = read(os.path.join(root, X('{@scopes_txt}')))
    lines = text.split('\n')
    ids = [l.split('|')[0].strip() for l in lines if l.strip() and not l.startswith('#')]
    if ctb.get('action') != 'add' or not re.fullmatch(r'[A-Z][A-Z0-9-]{1,15}', sid) or not name:
        reject('A scope change needs action: add, scope: an upper-case id and name:', 'For example scope: OPS, name: Operations knowledge.')
    if sid.startswith(X('{stg-}')):
        reject(X('{stg-} scopes come from stages.txt'), 'Add a stage instead.')
    if sid in ids:
        if '%s | %s' % (sid, name) in text:
            return text, 'NOOP', []
        reject('Scope %s exists with another name' % sid, 'A scope is never renamed silently.')
    if after not in ids:
        reject('after: must name an existing scope line or @stages', 'Say where the scope sits in the catalogue order.')
    i = next(k for k, l in enumerate(lines) if l.split('|')[0].strip() == after)
    return '\n'.join(lines[:i + 1] + ['%s | %s' % (sid, name)] + lines[i + 1:]), 'NEW', [sid]


def resolve_source(root, ctb):
    """kind: source. action register: the next source, with its extract, provenance and clause ledger already in sources/."""
    _fields(ctb, 'source')
    sid, status, auth = ctb.get('source', ''), ctb.get('text-status', ''), ctb.get('authority', '')
    text = read(os.path.join(root, X('{@sources_txt}')))
    rows = [l for l in text.split('\n') if l.startswith(X('{src-}'))]
    ids = [r.split(' | ')[0] for r in rows]
    row = ' | '.join([sid] + [ctb.get(k, '') for k in ('title', 'location', 'sha', 'role', 'authority', 'text-status')])
    if ctb.get('action') == 'add-clause':  # an in-progress ledger gains a clause capture missed: lines in the extract, in no other clause
        lp = os.path.join(root, X('{@sources_dir}'), sid + '.clauses')
        if sid not in ids or not os.path.isfile(lp):
            reject('%s has no clause ledger' % sid, 'Register and capture the source first.')
        lt = read(lp)
        sec, m = ctb.get('section', ''), re.fullmatch(r'(\d+)-(\d+)', ctb.get('lines', ''))
        if m and re.search(X(r'^%s \| %s-%s \|') % (re.escape(sec), m.group(1), m.group(2)), lt, re.M):
            return text, 'NOOP', []  # already added: checked first, so a replay after the ledger closed changes nothing
        if not re.search(r'^status: in-progress$', lt, re.M):
            reject('%s: only a ledger in progress gains clauses' % sid, 'A complete ledger is closed; a changed text is a new capture.')
        if not re.fullmatch(X('{cl}'), sec) or not m:
            reject('add-clause needs section: %sN.N and lines: A-B' % X('{cl-}'), 'Give the clause and its extract lines.')
        a, b = int(m.group(1)), int(m.group(2))
        have = [(c, int(x), int(y)) for c, x, y in re.findall(X(r'^({cl}) \| (\d+)-(\d+) \|'), lt, re.M)]
        for c, x, y in have:
            if c == sec:
                if (x, y) == (a, b):
                    return text, 'NOOP', []
                reject('%s %s already exists with lines %d-%d' % (sid, sec, x, y), 'Use a new clause number.')
            if a <= y and x <= b:
                reject('lines %d-%d overlap %s (lines %d-%d)' % (a, b, c, x, y), 'A source line belongs to one clause.')
        ex = re.search(r'^extract: (\S+) sha256 (\w+)$', lt, re.M)
        ext_lines = read(os.path.join(root, ex.group(1))).split('\n')
        if not (1 <= a <= b <= len(ext_lines)) or not any(l.strip() for l in ext_lines[a - 1:b]):
            reject('lines %d-%d are not text lines of the extract' % (a, b), 'Cite lines that hold the clause.')
        entry = '%s | %d-%d | %s' % (sec, a, b, sha('\n'.join(ext_lines[a - 1:b]).encode())[:16])
        rows_ = lt.rstrip('\n').split('\n')
        pos = max([k for k, l in enumerate(rows_) if re.match(X(r'^{cl} \| (\d+)-'), l) and int(re.match(X(r'^{cl} \| (\d+)-'), l).group(1)) < a], default=len(rows_) - 1)
        rows_.insert(pos + 1, entry)
        return text, 'EXTEND', [sid], {'sources/%s.clauses' % sid: '\n'.join(rows_) + '\n'}
    if ctb.get('action') == 'complete-ledger':  # a clause ledger declares itself complete: validate.py then requires every clause covered or held
        lp = os.path.join(root, X('{@sources_dir}'), sid + '.clauses')
        if sid not in ids or not os.path.isfile(lp):
            reject('%s has no clause ledger' % sid, 'Register and capture the source first.')
        lt = read(lp)
        if re.search(r'^status: complete$', lt, re.M):
            return text, 'NOOP', []
        return text, 'EXTEND', [sid], {'sources/%s.clauses' % sid: re.sub(r'^status: in-progress$', 'status: complete', lt, count=1, flags=re.M)}
    if row in rows:
        return text, 'NOOP', []
    if ctb.get('action') != 'register' or sid in ids:
        reject('A source change needs action: register and the next free source id', 'Sources are registered once; a new text version is a new capture.')
    nxt = X('{src%}') % (max(int(i[PREFIX_LEN['src']:]) for i in ids) + 1)
    if sid != nxt:
        reject('%s is not the next free source id (%s)' % (sid, nxt), 'Source ids are contiguous; use %s.' % nxt)
    if auth not in ('owner', 'owner-decision', 'historical') or status not in ('owner-file', 'owner-confirmed', 'provisional-extract', 'conversation-only'):
        reject('Unknown authority or text status', 'Authority: owner, owner-decision or historical; text status: owner-file, owner-confirmed, provisional-extract or conversation-only.')
    if status == 'owner-confirmed' and ctb.get('decision') not in adopted_decisions(root):
        raise Refusal('QUARANTINED', 'Only the owner confirms a source text; owner-reserved', 'Marking it confirmed would invent an owner act.', 'Record the owner\'s confirmation as an adopted decision and cite it.')
    more = {}
    if ctb.get('files-from'):  # the source files enter sources/ only through the gate, from the Level 1 intake area
        fd = os.path.abspath(os.path.join(root, ctb['files-from']))
        if not fd.startswith(os.path.abspath(os.path.join(root, X('{@intake_dir}'))) + os.sep) or not os.path.isdir(fd):
            reject('files-from must be a folder under intake/', 'Capture writes the source files under intake/<id>/files/.')
        for f in sorted(os.listdir(fd)):
            if not re.fullmatch(re.escape(sid) + r'\.(extract\.md|provenance\.md|clauses)', f) or os.path.exists(os.path.join(root, X('{@sources_dir}'), f)):
                reject('files-from holds %s, which is not a new file of %s' % (f, sid), 'Only the extract, provenance and clause ledger of the new source.')
            more[X('{@sources_prefix}') + f] = read(os.path.join(fd, f))
    if status == 'provisional-extract':
        need = ['%s.%s' % (sid, x) for x in (X('{@extract_md}'), X('{@provenance_md}'), 'clauses')]
        missing = [p for p in need if X('{@sources_prefix}') + p not in more and not os.path.isfile(os.path.join(root, X('{@sources_dir}'), p))]
        if missing:
            reject('A provisional extract needs %s' % ', '.join(missing), 'Capture the source first (capture.py).')
    if any(not ctb.get(k) for k in ('title', 'location', 'sha', 'role')):
        reject('A source states its title, location, sha and role', 'Use {SHA:sources/<id>.extract.md} for an extract.')
    return text.rstrip('\n') + '\n' + row + '\n', 'NEW', [sid], more


def resolve_stage_action(root, ctb):
    """kind: stage-action. action add: a new action of a stage, with the next permanent id, citing existing requirements."""
    _fields(ctb, 'stage-action')
    stg, txt, refs = ctb.get('stage', ''), ctb.get('text', ''), REQ.findall(ctb.get('refs', ''))
    text = read(os.path.join(root, X('{@stages_txt}')))
    acts = stage_actions(text)
    recs = blocks(read(os.path.join(root, X('{@reqs_txt}'))))
    if ctb.get('action') != 'add' or stg not in acts or len(txt) < MATCH['min_stage_action_text'] or not refs or set(refs) - set(recs):
        reject('A stage action needs action: add, an existing stage, text of a sentence and refs: existing requirements', 'Every action cites at least one requirement.')
    line = '- A-%d %s [%s]' % (max(acts[stg] or {0: 0}) + 1, txt, ', '.join(sorted(set(refs))))
    lines = text.split('\n')
    if any(l.split(' ', 2)[-1] == '%s [%s]' % (txt, ', '.join(sorted(set(refs)))) for l in (lines[i] for i in acts[stg].values())):
        return text, 'NOOP', []
    last = max(acts[stg].values()) if acts[stg] else next(i for i, l in enumerate(lines) if l.startswith('#' + stg))
    return '\n'.join(lines[:last + 1] + [line] + lines[last + 1:]), 'NEW', ['%s.A-%d' % (stg, max(acts[stg] or {0: 0}) + 1)]


def resolve_prose(root, ctb):
    """kind: prose. action replace (a section's body under its exact heading) or insert (a block after a unique anchor line).
    Sections the configuration marks owner-reserved need an adopted decision."""
    _fields(ctb, 'prose')
    text = read(os.path.join(root, X('{@frame_md}')))
    owner_sections = gate_config(root).get('owner_sections', [])
    action, body = ctb.get('action', ''), ctb.get('text', '').replace('\\n', '\n')
    if action == 'replace':
        h = ctb.get('heading', '')
        if text.count('\n' + h + '\n') != 1:
            reject('heading: must be one exact heading line of frame.md', 'Copy the heading line exactly.')
        if any(h.startswith(o) for o in owner_sections) and ctb.get('decision') not in adopted_decisions(root):
            raise Refusal('QUARANTINED', '%s is an owner-authored section; owner-reserved' % h, 'Changing it would rewrite the owner\'s text.', 'Cite the adopted decision that authorizes the change.')
        level = len(h) - len(h.lstrip('#'))
        a = text.index('\n' + h + '\n') + len(h) + 2
        nxt = re.search(r'^#{1,%d} ' % level, text[a:], re.M)
        b = a + nxt.start() if nxt else len(text)
        new = text[:a] + '\n' + body.strip('\n') + '\n\n' + text[b:]
    elif action == 'insert':
        anchor = ctb.get('anchor', '')
        if text.count(anchor + '\n') != 1 or not anchor:
            reject('anchor: must be one exact, unique line of frame.md', 'Copy the line after which the text goes.')
        i = text.index(anchor + '\n') + len(anchor) + 1
        if text[i:].startswith(body.strip('\n') + '\n'):
            return text, 'NOOP', []  # already inserted: a replay changes nothing
        new = text[:i] + body.strip('\n') + '\n' + text[i:]
    elif action == 'edit-line':  # replace (or, with an empty text, remove) the n-th occurrence of an exact line
        line, occ = ctb.get('line', ''), int(ctb.get('occurrence') or 0)
        starts = [m.start() for m in re.finditer(r'(?m)^' + re.escape(line) + r'\n', text)] if line else []
        if not 1 <= occ <= len(starts):
            if line and occ > len(starts) and len(starts) < occ:
                return text, 'NOOP', []  # that occurrence is already gone: a replay changes nothing
            reject('edit-line needs an exact line and an existing occurrence number', 'Give line: and occurrence: (1 for the first).')
        a = starts[occ - 1]
        new = text[:a] + (body.strip('\n') + '\n' if body.strip() else '') + text[a + len(line) + 1:]
    else:
        reject('A prose change needs action: replace, insert or edit-line', 'Prose is replaced by section, inserted after an anchor, or edited by exact line; nothing else.')
    return (text, 'NOOP', []) if new == text else (new, 'EXTEND' if action == 'insert' else 'SUPERSEDE', [(ctb.get('heading') or ctb.get('anchor') or ctb.get('line') or '')[:REPORT['excerpt']['heading']]])


def resolve_relation(root, ctb):
    """kind: relation. action retract: remove one coverage relation the gate recorded in error (a false match), and the lineage
    entry when no other relation of that source clause remains. A record fixed by an owner decision needs an authorizing decision."""
    _fields(ctb, 'relation')
    rid, src, sec, rel = ctb.get('record', ''), ctb.get('source', ''), ctb.get('section', ''), ctb.get('relation', '')
    text = read(os.path.join(root, X('{@reqs_txt}')))
    recs = blocks(text)
    if ctb.get('action') != 'retract' or rid not in recs or not re.fullmatch(X('{src}'), src) or not re.fullmatch(X('{cl}'), sec) or rel not in ('covers', 'extends', 'supports', 'depends-on'):
        reject('A relation change needs action: retract, an existing record:, a source:, a section: and a relation:', 'Name exactly the relation to remove.')
    guard_owner_decided(rid, recs, sources(root), ctb, adopted_decisions(root))
    rec = recs[rid]
    tok = '%s %s %s' % (src, sec, rel)
    have = [x.strip() for x in field(rec, 'c').split(';') if x.strip()]
    if tok not in have:
        return text, 'NOOP', []
    left = [x for x in have if x != tok]
    set_field(rec, 'c', '; '.join(left))
    if not left:
        rec['fields'] = [f for f in rec['fields'] if f[0] != 'c']
    if not any(x.startswith('%s %s ' % (src, sec)) for x in left):  # the clause no longer relates to this record: drop it from the lineage
        parts = []
        for part in [x.strip() for x in field(rec, 's').split(';')]:
            if part.startswith(src + ' '):
                secs = [s for s in part[len(src) + 1:].split(',') if s != sec]
                if secs:
                    parts.append('%s %s' % (src, ','.join(secs)))
            else:
                parts.append(part)
        set_field(rec, 's', '; '.join(p for p in parts if p))
    a, b = rec['span']
    return text[:a] + render(rec) + text[b:], 'RETRACT', [rid]


def resolve_registry(root, ctb):
    """kind: registry. A registry is knowledge and changes only here, one whole new version at a time. registry: its layout.json key;
    content: the new file, beside the contribution; content-sha256: its SHA-256 (part of the contribution's identity);
    base-version: the version it replaces (0 for a new registry). The same content again is a NOOP; a base that is no longer
    current is refused (no lost update); content that does not parse is refused. Returns (text, outcome, changed, files)."""
    _fields(ctb, 'registry')
    key = ctb.get('registry', '')
    if key not in LAYOUT['registries']:
        reject('"%s" is not a registered registry' % key, 'Name a registry key from %s (registries); a new registry is first added there.' % X('{@layout_json}'))
    f, rule = _N[key], KINDS['kinds']['registry']
    p = os.path.join(os.path.dirname(ctb['_path']), ctb.get('content', ''))
    if not ctb.get('content') or not os.path.isfile(p):
        reject('The new content is missing (content: %s)' % ctb.get('content'), 'Put the new registry file beside the contribution and name it in content:.')
    data = open(p, 'rb').read()
    if sha(data) != ctb.get('content-sha256'):
        reject('content-sha256 does not match the content', 'State the SHA-256 of exactly the content submitted.')
    cur = os.path.join(root, f)
    if os.path.exists(cur) and open(cur, 'rb').read() == data:
        return data.decode('utf-8'), 'NOOP', [], {}  # already this version (a replay)
    current = (version_map(root) or {}).get(f, (0, None))[0] if os.path.exists(cur) else 0
    if ctb.get('base-version') != str(current):
        reject('base-version %s is not the current version of %s (%d)' % (ctb.get('base-version'), f, current), 'Rebase the change on version %d and resubmit.' % current)
    parse = rule['parse'].get(os.path.splitext(f)[1])
    try:
        text = data.decode('utf-8')
        if parse:
            PARSE_CHECKS[parse](text)
    except ValueError as e:
        reject('The new %s does not parse: %s' % (f, e), 'Submit content that parses as %s.' % (parse or 'text'))
    return text, 'NEW' if current == 0 else 'SUPERSEDE', [f], {f: text}


PARSE_CHECKS = {'json': json.loads}  # parse mechanisms; which registries use them is registered data (kinds.json)


ADAPTERS = {k: (_N[v['target']] if v['target'] else None, 'resolve_' + k.replace('-', '_')) for k, v in KINDS['kinds'].items() if k != 'requirement'}  # every kind other than requirement: its canonical file (a registry contribution names its own) and its resolver


def adopted_decisions(root):
    """Adopted decisions and their mutation-authorization scope, read from the decision register (decisions.txt).
    Field a: lists the source clauses (SRC-NNNN §n) and records (LXM-REQ-NNNNNN) a gated change citing the decision may
    touch; 'None' is an empty scope (K1-K8, by owner confirmation). Scope is separate from status and effect: an adopted
    decision with an empty scope stays binding and authorizes nothing. A missing a: also authorizes nothing.
    Open decisions never authorize."""
    build = load_build(root)
    out = {}
    for d in build.parse_decisions(read(os.path.join(root, X('{@decisions_txt}'))))[1]:
        if d['status'] != 'adopted':
            continue
        cell = d.get('a')
        out[d['id']] = None if cell is None else {
            'clauses': {(a, b) for a, bs in re.findall(X(r'({src}) ((?:{cl}(?:, )?)+)'), cell) for b in re.findall(X(r'{cl}'), bs)},
            'records': set(REQ.findall(cell))}
    return out


def authorized(ctb, decisions, target=None, recs=None):
    """The contribution names an adopted decision whose recorded scope covers every cited clause, and the record it changes.
    A record created under the decision carries its reference and is inside its scope."""
    dec = ctb.get('decision')
    scope = decisions.get(dec) if dec else None
    if not scope:
        return False
    if not {(ctb['source'], c) for c in ctb['section'].split(',')} <= scope['clauses']:
        return False
    return target is None or target in scope['records'] or dec in field(recs[target], 'k').split(', ')


def not_authorized(ctb, decisions):
    dec = ctb.get('decision')
    if not dec:
        return ''
    if dec not in decisions:
        return '; %s is not an adopted decision' % dec
    if not decisions[dec] or not (decisions[dec]['clauses'] or decisions[dec]['records']):
        return '; %s is adopted and binding, but its mutation-authorization scope is empty' % dec
    return '; %s is adopted but its recorded scope does not cover this change' % dec


def guard_decision_cited(ctb, decisions, target, recs):
    """A cited decision must authorize the change itself; otherwise the gate would record it on content it never decided."""
    if ctb.get('decision') and not authorized(ctb, decisions, target, recs):
        reject('decision: %s does not authorize this change%s' % (ctb['decision'], not_authorized(ctb, decisions)),
               'Cite only an adopted decision whose recorded scope (decisions.txt, field a:) covers the clause and the record; otherwise submit without decision:.')


def owner_holds(root):
    """Open owner-reserved holds by source clause. A hold binds the clause itself, however a later contribution is phrased."""
    p = os.path.join(root, X('{@intake_dir}'), X('{@exceptions_txt}'))
    if not os.path.exists(p):
        return {}
    held = {}
    for m in re.finditer(X(r'^@({exc}) \| QUARANTINED \| [^\n]*\nsource: ({src}) ([^\n]+)\nreason: ([^\n]*owner-reserved[^\n]*)$'), read(p), re.M):
        for s in m.group(3).split(','):
            held[(m.group(2), s)] = m.group(1)
    return held


def guard_owner_holds(root, ctb, decisions):
    hits = sorted({e for s in ctb['section'].split(',') for e in [owner_holds(root).get((ctb['source'], s))] if e})
    if hits and not authorized(ctb, decisions):
        raise Refusal('QUARANTINED', '%s %s is held for an owner decision (%s); owner-reserved%s' % (ctb['source'], ctb['section'], ', '.join(hits), not_authorized(ctb, decisions)),
                      'Assimilating it in any form would implement an option the owner has not chosen.',
                      X('The owner decides; record the decision in decisions.txt (rendered as Part C) and resubmit with decision: {dec#}.'))


def resolve_exceptions(root, ctb_id, note=''):
    """An accepted (or already-assimilated) resubmission closes the exceptions it was blocked by, recording what resolved them."""
    p = os.path.join(root, X('{@intake_dir}'), X('{@exceptions_txt}'))
    if not os.path.exists(p):
        return False
    t = read(p)
    pat = X(r'^(@{exc}) \| (?:QUARANTINED|REJECTED) \| (%s) \|([^\n]*)\n((?:[a-z]+: [^\n]*\n)*)') % re.escape(ctb_id)
    n = re.sub(pat, lambda m: '%s | RESOLVED | %s |%s\n%s%s' % (m.group(1), m.group(2), m.group(3), m.group(4), ('resolved: %s\n' % note) if note else ''), t, flags=re.M)
    if n != t:
        open(p, 'w', encoding='utf-8').write(n)
    return n != t


def gate_config(root):
    """gate.json, with the paths it lists under "root_relative" resolved against the Master folder, so the Master verifies
    itself wherever it is installed."""
    g = json.load(open(os.path.join(root, X('{@gate_json}'))))
    for k in g.get('root_relative', []):
        if not os.path.isabs(g[k]):
            g[k] = os.path.join(os.path.abspath(root), g[k])
    return g


def regenerate_view(root):
    """Regenerate the generated Master from canonical knowledge and the hold log; nothing canonical changes."""
    gate = gate_config(root)
    b = subprocess.run([sys.executable, '-I', os.path.join(root, X('{@build_py}')), gate['src2'], gate['src3'], os.path.join(root, X('{@out_dir}'))], capture_output=True, text=True)
    if b.returncode:
        raise RuntimeError('regenerating the Master failed: ' + (b.stderr or b.stdout)[-REPORT['excerpt']['build_error']:])


def close_on_noop(root, ctb_id, note):
    """A NOOP resubmission that closes held items regenerates the Master, which shows open holds; nothing canonical changes."""
    if resolve_exceptions(root, ctb_id, note):
        gate = gate_config(root)
        b = subprocess.run([sys.executable, '-I', os.path.join(root, X('{@build_py}')), gate['src2'], gate['src3'], os.path.join(root, X('{@out_dir}'))], capture_output=True, text=True)
        if b.returncode:
            raise RuntimeError('regenerating the Master after closing a hold failed: ' + (b.stderr or b.stdout)[-REPORT['excerpt']['build_error']:])
        return True
    return False


LEDGER = _N[LAYOUT['ledger']]
LEDGER_SCHEMA = 3  # 2: hash chain (prev) and the exact mutation an accepted run made (mutation); 3: item versions (versions) and runtime versions (runtime)


def state_matches_log(root):
    """(ok, detail): the canonical state is exactly the one the last gate run left. Any direct edit since then breaks this."""
    p = os.path.join(root, LEDGER)
    lines = [l for l in open(p, encoding='utf-8').read().split('\n') if l.strip()] if os.path.exists(p) else []
    if not lines:
        return False, 'no gate run recorded'
    last = json.loads(lines[-1]); now = state_digest(root)
    return now == last.get('digest_after'), 'state %s; last gate run (seq %s) left %s' % (now[:12], last.get('seq'), (last.get('digest_after') or '')[:12])


def baseline(root, reason):
    """Record the current canonical state as accepted, once, when it differs from the last gate outcome: only after a full
    build and validation pass, with a stated reason, as a chained ledger line. Monitoring reports every baseline."""
    ok, detail = state_matches_log(root)
    if ok:
        return {'outcome': 'NOOP', 'reason': 'state already equals the last gate outcome'}
    if len(reason) < MATCH['min_baseline_reason']:
        return {'outcome': 'REJECTED', 'reason': 'a baseline states why the state changed outside the gate'}
    gate = gate_config(root)
    b = subprocess.run([sys.executable, '-I', os.path.join(root, X('{@build_py}')), gate['src2'], gate['src3'], os.path.join(root, X('{@out_dir}'))], capture_output=True, text=True)
    v = subprocess.run([sys.executable, '-I', os.path.join(root, X('{@validate_py}')), os.path.join(root, DERIVED[0]), os.path.join(root, DERIVED[1]),
                        gate['src2'], gate['src3'], gate['prev_matrix'], gate['src2_sha'], gate['src3_sha']], capture_output=True, text=True)
    summary = v.stdout.strip().split('\n')[-1]
    if b.returncode or v.returncode:
        return {'outcome': 'REJECTED', 'reason': 'validation fails: ' + summary}
    report = {'contribution': 'BASELINE', 'stages': {'validate': summary}, 'outcome': 'BASELINE', 'reason': reason,
              '_mutation': {'ops': None, 'files': {f: sha(open(os.path.join(root, f), 'rb').read()) for f in CANON}, 'contents': None}}
    log_outcome(root, report, {'id': 'BASELINE', '_sha': state_digest(root)}, json.loads([l for l in open(os.path.join(root, LEDGER)) if l.strip()][-1])['digest_after'], {})
    return report


def verify_chain(root):
    """(ok, detail): every schema-2 line names the SHA-256 of the line before it; legacy lines before the first are accepted as the chain's start."""
    p = os.path.join(root, LEDGER)
    lines = [l for l in open(p, encoding='utf-8').read().split('\n') if l.strip()] if os.path.exists(p) else []
    started = False
    for i, l in enumerate(lines):
        e = json.loads(l)
        if e.get('schema', 1) >= 2:
            started = True
            if e.get('prev') != (sha(lines[i - 1].encode()) if i else None):
                return False, 'line %d (seq %s) does not chain to the line before it' % (i + 1, e.get('seq'))
            if e.get('seq') != i + 1:
                return False, 'line %d carries seq %s' % (i + 1, e.get('seq'))
        elif started:
            return False, 'line %d is a legacy line after the chain started' % (i + 1)
    return True, '%d lines, %d chained' % (len(lines), sum(1 for l in lines if json.loads(l).get('schema', 1) >= 2))


def gate_version(root):
    return sha(''.join(sha(open(os.path.join(root, f), 'rb').read()) for f in (X('{@assimilate_py}'), X('{@lexicon_txt}'), X('{@build_py}'), X('{@validate_py}'))))[:16]


ACCEPTED = {'RECOGNIZE-EXACT', 'RECOGNIZE-SEMANTIC', 'COMPOSE', 'EXTEND', 'PARTIAL→EXTEND', 'NEW', 'PARTIAL→NEW', 'SUPERSEDE', 'RETRACT'}


def already_assimilated(root, ctb, reqs_text):
    """Replay idempotency by identity: this exact contribution (ID and SHA-256) was accepted before, and every source clause
    it cites still has its recorded relation. Matching may have shifted since (records grow), so replay never re-judges it."""
    p = os.path.join(root, LEDGER)
    if not os.path.exists(p) or ctb.get('kind', 'requirement') != 'requirement' or not ctb.get('source'):
        return None
    for line in open(p, encoding='utf-8'):
        e = json.loads(line)
        accepted = e.get('outcome') in ACCEPTED or (e.get('outcome') in ('NOOP', 'CLOSE') and e.get('classified_as') in ACCEPTED)  # a NOOP that recognized it
        if e.get('contribution_sha256') == ctb['_sha'] and e.get('contribution') == ctb.get('id') and accepted:
            if all(re.search(r'%s %s (covers|extends|supports)\b' % (re.escape(ctb['source']), re.escape(c)), reqs_text) for c in ctb.get('section', '').split(',')):
                return e['seq']
    return None


def log_outcome(root, report, ctb, before, srcs):
    """Append one machine-readable line per gate run (every outcome, including NOOP and ERROR). Not canonical state."""
    p = os.path.join(root, LEDGER); os.makedirs(os.path.dirname(p), exist_ok=True)
    lines = open(p, encoding='utf-8').read().split('\n') if os.path.exists(p) else []
    lines = [l for l in lines if l.strip()]
    seq = len(lines) + 1
    prev = sha(lines[-1].encode()) if lines else None  # hash chain: each line names the line before it
    src = (srcs or {}).get((ctb or {}).get('source'), {})
    entry = {'seq': seq, 'at': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(timespec='seconds'),
             'gate': gate_version(root), 'contribution': (ctb or {}).get('id'), 'contribution_sha256': (ctb or {}).get('_sha'),
             'path': os.path.relpath(report['contribution'], root) if not os.path.relpath(report['contribution'], root).startswith('..') else report['contribution'],
             'source': (ctb or {}).get('source'), 'section': (ctb or {}).get('section'),
             'source_authority': src.get('authority'), 'source_text_status': src.get('text_status'),
             'outcome': report.get('outcome'), 'classified_as': report.get('recognized_as'), 'clauses': report.get('clauses', []),
             'changed': report.get('changed', []), 'exception': report.get('exception'), 'reason': report.get('reason'),
             'validation': report['stages'].get('validate'), 'digest_before': before, 'digest_after': state_digest(root),
             'knowledge_before': (report.get('_knowledge') or (None, None))[0], 'knowledge_after': (report.get('_knowledge') or (None, None))[1],
             'schema': LEDGER_SCHEMA, 'prev': prev, 'mutation': report.get('_mutation'),
             'runtime': {n: v for n, (v, ok) in (report.get('_runtime') or runtime(root)).items()}}
    vm = version_map(root)
    if vm is None or report.get('outcome') not in ('REJECTED', 'QUARANTINED', 'ERROR'):  # a refusal changes no knowledge; the first line records every item
        ch = version_changes(root, vm)
        if ch or vm is None:
            entry['versions'] = ch
    with open(p, 'a', encoding='utf-8') as fh:
        fh.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + '\n'); fh.flush(); os.fsync(fh.fileno())
    report['ledger_seq'] = seq


def assimilate(root, ctb_path, dry_run=False):
    """Run the gate once. Never raises for a bad contribution or a gate failure: the outcome is reported and logged."""
    recover(root)
    report, before, ctx = {'contribution': ctb_path, 'stages': {}}, state_digest(root), {}
    k_before, ep = knowledge_digest(root), os.path.join(root, X('{@intake_exceptions_txt}'))
    holds_before = read(ep) if os.path.exists(ep) else ''
    try:
        rt = report['_runtime'] = runtime(root)
        outside = outside_gate(root)
        if any(not ok for v, ok in rt.values()):
            report.update(outcome='ERROR', reason='runtime outside its supported versions: %s' % ', '.join('%s %s' % (n, v) for n, (v, ok) in rt.items() if not ok),
                          resolution='Run the gate on a version %s registers, or widen it there through the gate with the evidence of a passing run.' % X('{@runtimes_json}'))
        elif outside:
            report.update(outcome='ERROR', reason='knowledge changed outside the gate: %s' % ', '.join(outside[:REPORT['excerpt']['outside_items']]) + (' and %d more' % (len(outside) - REPORT['excerpt']['outside_items']) if len(outside) > REPORT['excerpt']['outside_items'] else ''),
                          resolution='Restore those items, then submit the change as a contribution; the gate is the one entry point for knowledge.')
        else:
            _run(root, ctb_path, dry_run, report, before, ctx)
    except Exception as e:  # infrastructure failure (unreadable input, build crash...): nothing is committed
        report.update(outcome='ERROR', reason='%s: %s' % (type(e).__name__, e), resolution='Fix the gate environment and resubmit; the contribution was not judged.')
    refused = report['outcome'] in ('REJECTED', 'QUARANTINED', 'ERROR')
    if refused and knowledge_digest(root) != k_before:
        raise SystemExit('INVARIANT BROKEN: a refused contribution changed canonical knowledge')
    if refused and not dry_run and (read(ep) if os.path.exists(ep) else '') != holds_before:
        regenerate_view(root)  # the refusal opened or changed a hold: the generated Master shows it now, not at the next accepted change
    report['digest_unchanged'] = state_digest(root) == before
    report['_knowledge'] = (k_before, knowledge_digest(root))
    if not dry_run:
        log_outcome(root, report, ctx.get('ctb'), before, ctx.get('srcs'))
    return report


def _run(root, ctb_path, dry_run, report, before, ctx):
    lex = Lexicon(os.path.join(root, X('{@lexicon_txt}')))
    gate = gate_config(root)
    ctb = ctx['ctb'] = receive(ctb_path)                                                       # receive
    report['stages']['receive'] = '%s from %s %s, sha %s' % (ctb.get('id'), ctb.get('source'), ctb.get('section'), ctb['_sha'][:12])
    reqs_text, stages_text = read(os.path.join(root, X('{@reqs_txt}'))), read(os.path.join(root, X('{@stages_txt}')))
    recs, srcs = blocks(reqs_text), sources(root)
    ctx['srcs'] = srcs
    try:
        if not ctb['_format']:
            reject('No registered contribution format reads this contribution', 'Write it in a format registered in %s, or register its format there.' % X('{@contribution_formats_json}'))
        extra, plan = {}, []
        seq = already_assimilated(root, ctb, reqs_text)
        if seq:
            report.update(outcome='NOOP', recognized_as='already assimilated (ledger seq %d)' % seq, digest_unchanged=True)
            report['stages']['assimilate'] = 'nothing to change: this contribution was accepted at ledger seq %d and its relations still hold' % seq
            if not dry_run:
                if close_on_noop(root, ctb.get('id', ''), '%s; already assimilated (ledger seq %d)' % (time.strftime('%Y-%m-%d'), seq)) and state_digest(root) != before:
                    report.update(outcome='CLOSE', digest_unchanged=False)  # the held item is closed; the generated Master no longer shows it
            return report
        if ctb.get('kind') in ADAPTERS:                                                        # every non-requirement adapter
            target, fn = ADAPTERS[ctb['kind']]
            res = globals()[fn](root, ctb)
            new_text, outcome, changed = res[:3]
            if len(res) > 3 and changed:
                extra.update(res[3])  # further canonical files the change brings (a new source's extract, provenance, ledger)
            new_reqs, new_stages, clauses = reqs_text, stages_text, []
            if changed:
                if target == X('{@stages_txt}'):
                    new_stages = new_text
                elif target == X('{@reqs_txt}'):
                    new_reqs = new_text
                elif target:
                    extra[target] = new_text
        else:                                                                                  # requirement adapter
            acts = stage_actions(stages_text)
            acts['_scopes'] = set(load_build(root).parse_scopes(read(os.path.join(root, X('{@scopes_txt}'))), [k for k in acts if not k.startswith('_')])[0])
            check_contribution(ctb, recs, srcs, acts)
            index(recs, lex)                                                                   # discover
            report['stages']['discover'] = '%d canonical records indexed' % len(recs)
            decisions = adopted_decisions(root)
            guard_owner_holds(root, ctb, decisions)
            outcome, plan, clauses = resolve(ctb, recs, srcs, lex, decisions)                             # classify + resolve
            report['clauses'] = [{k: cl[k] for k in ('n', 'kind', 'rids', 'score')} for cl in clauses]
            report['stages']['classify'] = ', '.join('%d:%s%s' % (cl['n'], cl['kind'], '(' + '+'.join(r[-3:] for r in cl['rids']) + ')' if cl['rids'] else '') for cl in clauses)
            new_reqs, new_stages, changed = apply(plan, reqs_text, stages_text)
        report['stages']['resolve'] = '%s; mutation: %s' % (outcome, ', '.join(changed) or 'none')
        if not changed:
            report.update(outcome='NOOP' if outcome != 'NOOP' else outcome, recognized_as=outcome, digest_unchanged=True)
            report['stages']['assimilate'] = 'nothing to change: already assimilated'
            if not dry_run:
                if close_on_noop(root, ctb.get('id', ''), '%s; already assimilated (%s)' % (time.strftime('%Y-%m-%d'), outcome)) and state_digest(root) != before:
                    report.update(outcome='CLOSE', digest_unchanged=False)  # the held item is closed; the generated Master no longer shows it
            return report
        staging = tempfile.mkdtemp(prefix='lxm-stage-')                                        # validate
        try:
            for f in dict.fromkeys(CANON + TOOLS + registries(root)):
                os.makedirs(os.path.dirname(os.path.join(staging, f)), exist_ok=True)
                shutil.copyfile(os.path.join(root, f), os.path.join(staging, f))
            for d in (X('{@sources_dir}'), X('{@intake_dir}')):
                if os.path.isdir(os.path.join(root, d)):
                    shutil.copytree(os.path.join(root, d), os.path.join(staging, d), dirs_exist_ok=True)
            os.makedirs(os.path.join(staging, X('{@out_dir}')))
            open(os.path.join(staging, X('{@reqs_txt}')), 'w', encoding='utf-8').write(new_reqs)
            open(os.path.join(staging, X('{@stages_txt}')), 'w', encoding='utf-8').write(new_stages)
            for f, t in extra.items():
                open(os.path.join(staging, f), 'w', encoding='utf-8').write(t)
            closes = resolve_exceptions(staging, ctb.get('id', ''), '%s; %s by %s (sha %s); records %s%s' % (
                time.strftime('%Y-%m-%d'), outcome, ctb.get('id'), ctb['_sha'][:12], ', '.join(changed),
                '; decision %s' % ctb['decision'] if ctb.get('decision') else ''))  # closed in staging: the Master is generated with it closed
            b = subprocess.run([sys.executable, '-I', os.path.join(staging, X('{@build_py}')), gate['src2'], gate['src3'], os.path.join(staging, X('{@out_dir}'))], capture_output=True, text=True)
            if b.returncode:
                raise RuntimeError('staged build failed: ' + (b.stderr.strip().split('\n') or ['?'])[-1])
            v = subprocess.run([sys.executable, '-I', os.path.join(staging, X('{@validate_py}')), os.path.join(staging, DERIVED[0]), os.path.join(staging, DERIVED[1]),
                                gate['src2'], gate['src3'], gate['prev_matrix'], gate['src2_sha'], gate['src3_sha']], capture_output=True, text=True)
            fails = [l for l in v.stdout.split('\n') if l.startswith('FAIL')]
            post = blocks(new_reqs); index(post, lex)
            for cl in clauses:                                                                 # assimilated means expressed (LXM-REQ-000226)
                declared = cl.get('declared') and ('%s %s covers' % (ctb['source'], ctb['section'])) in field(post[cl['rids'][0]], 'c')
                if not declared and classify(cl['text'], post, lex, set())['kind'] not in ('EXACT', 'COVERED', 'CONFLICT') and outcome != 'SUPERSEDE':
                    fails.append('FAIL  clause %d is still not expressed by any record after the mutation' % cl['n'])
            try:                                                                               # re-validation of every dependent clause
                spec = importlib.util.spec_from_file_location('lxm_revalidate', os.path.join(staging, X('{@revalidate_py}')))
                RV = importlib.util.module_from_spec(spec); spec.loader.exec_module(RV)
                before_reg, after_reg = len(RV.revalidate(root)[1]), RV.revalidate(staging)[1]
                if len(after_reg) > before_reg:
                    fails.append('FAIL  the change leaves %d source clause sentence(s) unexpressed: %s' % (len(after_reg) - before_reg, '; '.join(after_reg[:3])))
            except FileNotFoundError:
                pass  # a root without revalidate.py (older checkpoints) is checked by validate.py alone
            for rid in (r for r in changed if r in post):                                      # uniqueness of what changed
                p = post[rid]['_profile']['set']
                twins = [o for o in post if o != rid and containment(p, post[o]['_profile']['set']) >= T_COVER and containment(post[o]['_profile']['set'], p) >= T_COVER]
                if twins:
                    fails.append('FAIL  %s would duplicate %s' % (rid, ', '.join(twins)))
            report['stages']['validate'] = 'validate.py: %s; gate checks: %d failure(s)' % (v.stdout.strip().split('\n')[-1], len(fails))
            if v.returncode or fails:
                raise Refusal('REJECTED', 'Validation failed: ' + ' | '.join(fails), 'Accepting would break a Master invariant.',
                              'Correct the contribution so that every listed check passes.', clauses)
            if dry_run:
                report.update(outcome=outcome, dry_run=True)
                return report
            report['_mutation'] = {'ops': [list(x) for x in plan] if ctb.get('kind', 'requirement') == 'requirement' else None,
                                   'files': {f: sha(t.encode()) for f, t in [(X('{@reqs_txt}'), new_reqs), (X('{@stages_txt}'), new_stages)] + sorted(extra.items())},
                                   'contents': dict(extra, **({X('{@stages_txt}'): new_stages} if ctb.get('kind') == 'stage-action' else {})) or None}  # small registers replay exactly
            commit(root, staging, [X('{@reqs_txt}'), X('{@stages_txt}')] + sorted(extra) + DERIVED + ([X('{@intake_exceptions_txt}')] if closes else []))  # assimilate + propagate
            report['stages']['assimilate'] = 'committed: ' + ', '.join([X('{@reqs_txt}'), X('{@stages_txt}')] + sorted(extra)) + (', intake/exceptions.txt (exception closed)' if closes else '')
            report['stages']['propagate'] = 'regenerated: %s' % ', '.join(DERIVED)
            report.update(outcome=outcome, changed=changed)
            return report
        finally:
            shutil.rmtree(staging, ignore_errors=True)
    except Refusal as r:
        assert state_digest(root) == before
        report.update(outcome=r.outcome, reason=r.reason, resolution=r.resolution, exception=None if dry_run else record_exception(root, ctb, r))
        if r.detail:
            report['clauses'] = [{k: cl[k] for k in ('n', 'kind', 'rids', 'score')} for cl in r.detail]
        return report


if __name__ == '__main__':
    if sys.argv[2] == '--baseline':
        print(json.dumps(baseline(sys.argv[1], ' '.join(sys.argv[3:])), indent=1, default=str)); sys.exit(0)
    rep = assimilate(sys.argv[1], sys.argv[2], '--dry-run' in sys.argv)
    print(json.dumps(rep, indent=1, ensure_ascii=False))
    sys.exit({'REJECTED': 2, 'QUARANTINED': 2, 'ERROR': 3}.get(rep['outcome'], 0))
