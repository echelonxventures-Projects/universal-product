"""Generate LXM-MASTER.md and LXM-RECONCILIATION.md from reqs.txt, stages.txt, coverage.txt, sources.txt, decisions.txt and frame.md.
Usage: python3 -I build.py <SRC-0002 path> <SRC-0003 path> <out dir>"""
import hashlib, json, os, re, sys
sys.dont_write_bytecode = True  # a check never changes the Master directory (no __pycache__)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from ids import X, ID_LEN, registry  # identifier formats come from ids.json (LXM-REQ-000240)

HERE = os.path.dirname(os.path.abspath(__file__))
APPENDIX_FIRST_LINE = registry('gate_json')['src3_appendix_first_line']  # the source line where the mandate's own title begins
LAY = json.load(open(os.path.join(HERE, X('{@layout_json}')), encoding='utf-8')); COL = {c: i for i, c in enumerate(LAY['sources_columns'])}
VAL = registry('validate_json')


def read(p): return open(p, encoding='utf-8').read()
def sha(b): return hashlib.sha256(b).hexdigest()


def parse_reqs(text):
    recs, cur = [], None
    for line in text.split('\n'):
        if line.startswith('#') or not line.strip():
            continue
        if line.startswith('@'):
            rid, scope, cls, disp = [x.strip() for x in line[1:].split('|')]
            cur = {'id': rid, 'scope': scope, 'cls': cls, 'disp': disp, 't': '', 's': '', 'k': '', 'n': '', 'x': ''}
            recs.append(cur)
        else:
            key, _, val = line.partition(': ')
            if key == 'h':
                cur.setdefault('h', []).append(val.strip())
            else:
                cur[key] = val.strip()
    return recs


def parse_stages(text):
    stages, cur = [], None
    for line in text.split('\n'):
        if line.startswith('# ') or not line.strip():
            continue
        if line.startswith(X('#{stg~}')):
            sid, title = [x.strip() for x in line[1:].split('|')]
            cur = {'id': sid, 'title': title, 'o': '', 'e': '', 'aids': [], 'acts': [], 'x': ''}
            stages.append(cur)
        elif line.startswith('- '):
            aid, act = re.match(r'- (A-\d+) (.*)$', line).groups()  # every action carries its stable ID
            cur['aids'].append(aid); cur['acts'].append(act)
        else:
            key, _, val = line.partition(': ')
            cur[key] = val
    return stages


def parse_sources(text):
    return [[c.strip() for c in l.split(' | ')] for l in text.split('\n') if l.startswith(X('{src-}'))]


LINE_CODES = {'S': X('{src=0002}'), 'L': X('{src=0003}'), 'A': X('{src=0001}')}  # lineage line prefixes (see reqs.txt header)


def cited_sources(s):
    return set(re.findall(X(r'{src}'), s)) | {LINE_CODES[p] for p in re.findall(r'(?<![A-Za-z0-9-])([SLA])\d', s)}


def parse_scopes(text, stage_ids):
    """The registered scopes: (order, names). "@stages" expands to every stage of stages.txt, in order. Shared with assimilate.py."""
    order, names = [], {}
    for line in text.split('\n'):
        if not line.strip() or line.startswith('#'):
            continue
        if line.strip() == '@stages':
            order += list(stage_ids)
            continue
        sid, name = [x.strip() for x in line.split('|', 1)]
        order.append(sid); names[sid] = name
    return order, names


def parse_decisions(text):
    """The decision register: (table layouts by group, decisions in register order). Shared by assimilate.py and validate.py."""
    layouts, decs, cur = {}, [], None
    for line in text.split('\n'):
        if line.startswith('%'):
            g, *cols = [c.strip() for c in line[1:].split(' | ')]
            layouts[g] = [tuple(c.split('=', 1)) for c in cols]
        elif line.startswith('@'):
            did, status, group = [c.strip() for c in line[1:].split(' | ')]
            cur = {'id': did, 'status': status, 'group': group}
            decs.append(cur)
        elif cur is not None and ': ' in line and not line.startswith('#'):
            k, v = line.split(': ', 1)
            cur[k] = v
    return layouts, decs


TRACE_FIELDS = ('impl', 'spec', 'config', 'test', 'basis')
EVIDENCE_FIELDS = ('fact', 'source', 'method', 'observed', 'observer', 'verifies', 'basis', 'subject', 'status')


def parse_evidence(text):
    """The evidence register: (table layouts by group, entries in register order), in the shape decision_table renders."""
    layouts, out, cur = {}, [], None
    for line in text.split('\n'):
        if line.startswith('%'):
            g, *cols = [c.strip() for c in line[1:].split(' | ')]
            layouts[g] = [tuple(c.split('=', 1)) for c in cols]
        elif line.startswith('@'):
            eid, group = [c.strip() for c in line[1:].split(' | ')]
            cur = {'id': eid, 'group': group}; out.append(cur)
        elif cur is not None and ': ' in line and not line.startswith('#'):
            k, v = line.split(': ', 1); cur[k] = v
    return layouts, out


def parse_trace(text):
    """Implementation traceability: (default basis, {requirement: {field: value}}) in file order. Shared with validate.py and code_adapter.py."""
    default, out, cur = '', {}, None
    for line in text.split('\n'):
        if line.startswith('# basis-default: '):
            default = line[len('# basis-default: '):]
        elif line.startswith('#') or not line.strip():
            continue
        elif line.startswith('@'):
            cur = out.setdefault(line[1:].strip(), {'_dup': line[1:].strip() in out})
        elif cur is not None:
            k, _, v = line.partition(': ')
            cur[k] = v
    return default, out


def decision_table(layouts, decs, group):
    cols = layouts[group]
    rows = ['| %s |' % ' | '.join(h for h, _ in cols), '|' + '---|' * len(cols)]
    for d in (d for d in decs if d['group'] == group):
        cell = lambda k: d['id'] + (' (%s)' % d['label'] if d.get('label') else '') if k == 'id' else d.get(k, '')
        rows.append('| %s |' % ' | '.join(cell(k) for _, k in cols))
    return '\n'.join(rows)


def refs(s): return re.findall(X(r'{req}'), s)
def strip_refs(s): return re.sub(r'\s*\[[^\]]*\]\s*$', '', s)


def parse_cov(text):
    rows = []
    for line in text.split('\n'):
        if line.startswith('RE-'):
            eid, src, el, secs = [x.strip() for x in line.split('|')]
            rows.append((eid, src, el, [s.strip() for s in secs.split(',')]))
    return rows


def lineage(s, prefix):
    out = []
    for m in re.finditer(r'(?<![A-Za-z0-9-])' + prefix + r'(\d+)(?:-(\d+))?(?![0-9])', s):
        out.append(m.group(0))
    return ', '.join(out)


def main(src2, src3, outdir):
    recs = parse_reqs(read(os.path.join(HERE, X('{@reqs_txt}'))))
    stages = parse_stages(read(os.path.join(HERE, X('{@stages_txt}'))))
    cov = parse_cov(read(os.path.join(HERE, X('{@coverage_txt}'))))
    frame = read(os.path.join(HERE, X('{@frame_md}')))
    by = {r['id']: r for r in recs}
    cited = {}
    for st in stages:
        for a in st['acts'] + [st['e'], st['x']]:
            for rid in refs(a):
                cited.setdefault(rid, []).append(st['id'])
    b2, b3 = open(src2, 'rb').read(), open(src3, 'rb').read()
    lines3 = b3.split(b'\n')
    appx = b'\n'.join(lines3[APPENDIX_FIRST_LINE - 1:])

    tok = {'APPX_FIRST': APPENDIX_FIRST_LINE, 'SRC3_LINES': len(lines3), 'APPX_SHA': sha(appx),
           'SRC2_BYTES': len(b2), 'SRC2_SHA': sha(b2), 'SRC3_BYTES': len(b3), 'SRC3_SHA': sha(b3)}
    def fill(c):
        c = re.sub(r'\{SHA:([^}]+)\}', lambda m: sha(open(os.path.join(HERE, m.group(1)), 'rb').read()), c)
        return re.sub(r'\{(\w+)\}', lambda m: str(tok[m.group(1)]), c)
    reg = parse_sources(read(os.path.join(HERE, X('{@sources_txt}'))))
    rows = ['| %s |' % ' | '.join(fill(row[COL[k]]) for k in LAY['sources_shown']) for row in reg]
    STATUS = [('owner-file', 'owner-supplied files pinned by SHA-256'), ('owner-confirmed', 'extracts the owner has confirmed'),
              ('provisional-extract', 'agent-captured and hashed, **not owner-confirmed**'), ('conversation-only', 'no captured text')]
    status = ['', '**Source text status** (separate from authority; generated from the register):', '']
    for st, desc in STATUS:
        ids = [r[COL['id']] for r in reg if r[COL['text_status']] == st]
        if ids:
            dep = [x['id'] for x in recs if cited_sources(x['s']) & set(ids)]
            status.append('- *%s* — %s: %s. Cited by %d record%s.' % (st, desc, ', '.join(ids), len(dep), '' if len(dep) == 1 else 's'))
    status += ['', 'Records resting on provisional-extract or conversation-only sources stay candidate content until the owner confirms or supplies the source text (Part G.4, item 10). Only the owner can mark a source owner-confirmed.']
    sources = '\n'.join(['| ID | Source | Location | SHA-256 | Role |', '|---|---|---|---|---|'] + rows + status)

    cat = []
    scope_order, scope_name = parse_scopes(read(os.path.join(HERE, X('{@scopes_txt}'))), [st['id'] for st in stages])
    for sc in scope_order:
        rs = [r for r in recs if r['scope'] == sc]
        if not rs:
            continue
        name = scope_name.get(sc) or next(s['title'] for s in stages if s['id'] == sc)
        cat.append('### CAT-%s — %s\n' % (sc, name))  # catalogue group; STG-NN alone names the Part E procedure
        for r in rs:
            meta = '`%s` · class %s · disposition **%s**' % (r['scope'], r['cls'], r['disp'])
            if r['k']:
                meta += ' · %s' % r['k']
            extra = ''.join('  \n%s: %s' % (lbl, r[key]) for key, lbl in (('c', 'Coverage'), ('d', 'Depends on'), ('v', 'Version')) if r.get(key))
            hist = ''.join('\n> Superseded %s\n' % h for h in r.get('h', []))
            cat.append('#### %s — %s\n\n%s  \nLineage: %s%s\n\n%s\n%s' % (r['id'], r['t'], meta, r['s'], extra, r['x'], hist))

    stg = []
    for st in stages:
        stg.append('### %s — %s\n\n**Objective:** %s  \n**Entry:** %s\n' % (st['id'], st['title'], st['o'], st['e']))
        for aid, a in zip(st['aids'], st['acts']):
            stg.append('- `%s.%s` %s — %s' % (st['id'], aid, strip_refs(a), ', '.join(refs(a))))
        stg.append('\n**Exit:** %s\n' % st['x'])

    secid = dict(zip(VAL['report_sections']['letters'], [X('{req%}') % (VAL['report_sections']['first_record'] + i) for i in range(len(VAL['report_sections']['letters']))]))
    covt = ['| Element | Source | Required content | Report sections |', '|---|---|---|---|']
    for eid, src, el, secs in cov:
        covt.append('| %s | %s | %s | %s |' % (eid, src, el, ', '.join('%s (%s)' % (s, secid[s]) for s in secs)))

    om = ['| Restoration | Requirement | Source | Restored as | Applied in |', '|---|---|---|---|---|']
    for r in recs:
        m = re.search(r'OMR-(\d)', r['k'])
        if m:
            om.append(X('| OMR-%s | %s | {src=0002} %s | %s | %s |') % (m.group(1), r['id'], lineage(r['s'], 'S'), r['t'],
                                                                 ', '.join(sorted(set(cited.get(r['id'], [])))) or r['scope']))

    si = ['| Stage | Title | Actions | Requirements cited |', '|---|---|---|---|']
    for st in stages:
        ids = sorted({x for a in st['acts'] + [st['e'], st['x']] for x in refs(a)})
        si.append('| %s | %s | %d | %s |' % (st['id'], st['title'], len(st['acts']), ', '.join(i[-3:] for i in ids)))
    si.append(X('\nRequirement IDs are abbreviated to their last three digits ({req-}000xxx).'))

    tr = [X('| Requirement | {src=0002} | {src=0003} procedure | {src=0001} (Appendix A) | Other sources | Cited by stages | Disposition |'), '|---|---|---|---|---|---|---|']
    for r in recs:
        other = '; '.join(x.strip() for x in r['s'].split(';') if re.match(X(r'\s*({src-}|PRODUCTION)'), x))
        tr.append('| %s | %s | %s | %s | %s | %s | %s |' % (r['id'], lineage(r['s'], 'S') or '—', lineage(r['s'], 'L') or '—',
                                                          lineage(r['s'], 'A') or '—', other or '—',
                                                          ', '.join(sorted(set(cited.get(r['id'], [])))) or '(%s section)' % r['scope'], r['disp']))

    clauses = []
    exc_p = os.path.join(HERE, X('{@intake_dir}'), X('{@exceptions_txt}'))
    holds = {}
    if os.path.exists(exc_p):
        for m in re.finditer(X(r'^@({exc}) \| (QUARANTINED|REJECTED) \| [^\n]*\nsource: ({src}) ([^\n]+)$'), read(exc_p), re.M):
            for s in m.group(4).split(','):
                holds[(m.group(3), s)] = m.group(1)
    for led in sorted(f for f in os.listdir(os.path.join(HERE, X('{@sources_dir}'))) if f.endswith('.clauses')) if os.path.isdir(os.path.join(HERE, X('{@sources_dir}'))) else []:
        src, text = led[:ID_LEN['src']], read(os.path.join(HERE, X('{@sources_dir}'), led))
        status = (re.search(r'^status: (\S+)', text, re.M) or [None, '?'])[1]
        clauses += ['**%s** — ledger status *%s*, %d clauses.' % (src, status, len(re.findall(X(r'^{cl-}'), text, re.M))), '',
                    '| Clause | Source lines | Covered by | Supported by | Open hold |', '|---|---|---|---|---|']
        for cid, lines in re.findall(X(r'^({cl}) \| ([\d-]+) \|'), text, re.M):
            rel = lambda *kinds: ', '.join(r['id'] + ('' if k == kinds[0] else ' (%s)' % k) for r in recs for k in kinds
                                           if '%s %s %s' % (src, cid, k) in [t.strip() for t in r.get('c', '').split(';')]) or '—'
            clauses.append('| %s | %s | %s | %s | %s |' % (cid, lines, rel('covers', 'extends'), rel('supports'), holds.get((src, cid), '—')))
        clauses.append('')
    if not clauses:
        clauses = ['No source has a clause ledger yet.']

    note = (X('The following is {src=0003} bytes from line %d to the end, copied mechanically and unaltered (SHA-256 `%s`). '
            'Its internal headings belong to the mandate and are not part of this master\'s numbering.')) % (APPENDIX_FIRST_LINE, sha(appx))
    default_basis, trace = parse_trace(read(os.path.join(HERE, X('{@trace_txt}'))))
    it = ['Product requirements traced to an implementation: %d. Known gaps (no implementation found): %d. '
          'A link says where a requirement is implemented, never that it is met. Basis, unless the row says otherwise: %s.' % (
              sum(1 for t in trace.values() if t.get('impl')), sum(1 for t in trace.values() if not t.get('impl')), default_basis), '',
          '| Requirement | Title | Implementation | Configuration | Tests | Basis |', '|---|---|---|---|---|---|']
    for rid, t in trace.items():
        it.append('| %s | %s | %s | %s | %s | %s |' % (rid, by[rid]['t'] if rid in by else '?', ', '.join('`%s`' % x for x in t.get('impl', '').split(', ') if x) or '**gap**',
                                                     t.get('config') or '—', ', '.join('`%s`' % x for x in t.get('test', '').split(', ') if x) or '—', t.get('basis') or 'default'))
    out = frame.replace('{{IMPL_TRACE}}', '\n'.join(it))
    layouts, decs = parse_decisions(read(os.path.join(HERE, X('{@decisions_txt}'))))
    out = re.sub(r'\{\{DECISIONS:([^}]+)\}\}', lambda m: decision_table(layouts, decs, m.group(1)), out)
    ev_layouts, evs = parse_evidence(read(os.path.join(HERE, X('{@evidence_txt}'))))
    out = re.sub(r'\{\{EVIDENCE:([^}]+)\}\}', lambda m: decision_table(ev_layouts, evs, m.group(1)), out)
    for k, v in {'SOURCES': sources, 'CATALOGUE': '\n'.join(cat), 'STAGES': '\n'.join(stg), 'COVERAGE': '\n'.join(covt),
                 'OMISSIONS': '\n'.join(om), 'STAGE_INDEX': '\n'.join(si), 'TRACE': '\n'.join(tr), 'CLAUSES': '\n'.join(clauses).rstrip(), 'APPENDIX_NOTE': note}.items():
        out = out.replace('{{%s}}' % k, v)
    head, tail = out.split('{{APPENDIX}}')
    with open(os.path.join(outdir, X('{@master_md}')), 'wb') as f:
        f.write(head.encode('utf-8') + appx + tail.encode('utf-8'))

    mx = ['# LXM reconciliation evidence: the 128 reconciled rows (Stages 0–10, header and directive)', '',
          'Generated from `reqs.txt`; requirement text is in LXM-MASTER Part D and is not repeated here. Classes: FP fully preserved, ST strengthened, MO mandate-only, PP partially preserved, OM omitted, CF conflicting or superseded.', '',
          X('| Requirement | Title | {src=0002} | {src=0003} | Appendix A | Class | Disposition | Decision | Resolution | Stages |'), '|---|---|---|---|---|---|---|---|---|---|']
    for r in recs[:VAL['matrix_rows']]:
        mx.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (r['id'], r['t'], lineage(r['s'], 'S') or '—', lineage(r['s'], 'L') or '—',
                                                                      lineage(r['s'], 'A') or '—', r['cls'], r['disp'], r['k'] or '—', r['n'] or '—',
                                                                      ', '.join(sorted(set(cited.get(r['id'], [])))) or r['scope']))
    with open(os.path.join(outdir, X('{@reconciliation_md}')), 'w', encoding='utf-8') as f:
        f.write('\n'.join(mx) + '\n')


if __name__ == '__main__':
    main(*sys.argv[1:4])
