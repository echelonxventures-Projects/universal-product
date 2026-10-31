"""Independent checks on the generated LXM-MASTER.md against the original sources.
Usage: python3 -I validate.py <master> <reconciliation> <SRC-0002> <SRC-0003> <earlier matrix> <expected SRC-0002 sha> <expected SRC-0003 sha>"""
import hashlib, re, sys

sys.dont_write_bytecode = True  # a check never changes the Master directory (no __pycache__)

master_p, recon_p, s2_p, s3_p, prev_p, exp2, exp3 = sys.argv[1:8]
M = open(master_p, encoding='utf-8').read()
results = []
def check(name, ok, detail=''):
    results.append((name, ok, detail))

# 1. sources unchanged
b2, b3 = open(s2_p, 'rb').read(), open(s3_p, 'rb').read()
check('SRC-0002 unchanged (SHA-256)', hashlib.sha256(b2).hexdigest() == exp2)
check('SRC-0003 unchanged (SHA-256)', hashlib.sha256(b3).hexdigest() == exp3)

# 2. Appendix A verbatim
appx = b'\n'.join(b3.split(b'\n')[373:])
mb = open(master_p, 'rb').read()
check('Appendix A: SRC-0003 lines 374-end appear byte-identical in the master', appx in mb,
      'block %d bytes, sha %s' % (len(appx), hashlib.sha256(appx).hexdigest()[:16]))
check('Appendix A appears exactly once', mb.count(appx) == 1)
cat_part = M.split('## Part D — Requirement catalogue')[1].split('## Part E — Stage procedures')[0]
stg_part = M.split('## Part E — Stage procedures')[1].split('## Part F —')[0]

# 3. requirement records: unique, contiguous, one disposition each
heads = re.findall(r'^#### (LXM-REQ-(\d{6})) — (.+)$', cat_part, re.M)
ids = [h[0] for h in heads]
check('Requirement IDs unique', len(ids) == len(set(ids)), '%d records' % len(ids))
nums = sorted(int(h[1]) for h in heads)
check('Requirement IDs contiguous from 000001', nums == list(range(1, len(nums) + 1)))
blocks = re.split(r'^#### ', cat_part, flags=re.M)[1:]
ALLOWED = {'Retained', 'Strengthened', 'Expanded-from-mandate', 'Repaired', 'Restored', 'Historical', 'Owner-decision', 'New-owner-addition'}
disp, cls, lin, text = {}, {}, {}, {}
for b in blocks:
    rid = b.split(' — ')[0]
    d = re.findall(r'disposition \*\*([^*]+)\*\*', b)
    disp[rid] = d
    cls[rid] = re.search(r'· class (\S+) ·', b).group(1)
    lin[rid] = re.search(r'^Lineage: (.*)$', b, re.M).group(1).rstrip()
    text[rid] = b.split('\n\n', 2)[2].strip() if b.count('\n\n') >= 2 else ''
bad = [r for r, d in disp.items() if len(d) != 1 or d[0] not in ALLOWED]
check('Every record has exactly one disposition from the allowed set', not bad, ', '.join(bad))
empty = [r for r, t in text.items() if len(t) < 20]
check('Every record has normative text', not empty, ', '.join(empty))

# 4. the 128 reconciled rows match the earlier hand matrix (IDs and classes)
prev = {r: re.sub(r'\([^)]*\)', '', c.replace('*', '')).replace(' ', '') for r, c in re.findall(r'^\| (LXM-REQ-\d{6}) \|.*\| ([^|]+) \|$', open(prev_p, encoding='utf-8').read(), re.M)}
mism = [r for r, c in prev.items() if r not in cls or cls[r].replace(' ', '') != c]
check('128 reconciled rows: same IDs and classes as the earlier matrix', len(prev) == 128 and not mism,
      '%d rows in earlier matrix; mismatches: %s' % (len(prev), ', '.join(mism)))
first128 = ['LXM-REQ-%06d' % n for n in range(1, 129)]
cnt = {}
for r in first128:
    cnt[cls[r]] = cnt.get(cls[r], 0) + 1
mo = [r for r in first128 if cls[r] == 'MO']
pp = [r for r in first128 if cls[r].startswith('PP')]
om = [r for r in first128 if cls[r] == 'OM']
check('33 mandate-only rows, each disposed Expanded-from-mandate with an Appendix A line', len(mo) == 33 and all(disp[r] == ['Expanded-from-mandate'] and re.search(r'(?<![A-Za-z-])A\d', lin[r]) for r in mo), str(len(mo)))
check('15 partial rows, each disposed Repaired', len(pp) == 15 and all(disp[r] == ['Repaired'] for r in pp), str(len(pp)))
check('6 omitted rows, each disposed Restored and registered OMR-1..6', len(om) == 6 and all(disp[r] == ['Restored'] for r in om)
      and sorted(re.findall(r'\| (OMR-\d) \|', M)) == ['OMR-%d' % i for i in range(1, 7)], str(len(om)))
check('Class distribution of the 128 rows', True, ', '.join('%s %d' % kv for kv in sorted(cnt.items())))

# 5. references resolve
allrefs = set(re.findall(r'LXM-REQ-\d{6}', M.replace(appx.decode('utf-8'), '')))
check('Every LXM-REQ reference in the master resolves', allrefs <= set(ids), ', '.join(sorted(allrefs - set(ids))))
decs_def = set(re.findall(r'^\| (LXM-DEC-\d{6})', M, re.M))
decs_used = set(re.findall(r'LXM-DEC-\d{6}', M))
check('Every LXM-DEC reference resolves', decs_used <= decs_def, ', '.join(sorted(decs_used - decs_def)))
for kind in ('EVD', 'CHG'):
    d = set(re.findall(r'^\| (LXM-%s-\d{6})' % kind, M, re.M)); u = set(re.findall(r'LXM-%s-\d{6}' % kind, M))
    check('Every LXM-%s reference resolves' % kind, u <= d, ', '.join(sorted(u - d)))
stage_ids = re.findall(r'^### (STG-\d{2}) — ', stg_part, re.M)
check('Stages are numbered contiguously from STG-00, once each, in order (no fixed number of stages)', bool(stage_ids) and stage_ids == ['STG-%02d' % i for i in range(len(stage_ids))], ', '.join(stage_ids))
stage_refs = set(re.findall(r'STG-\d{2}', M))
check('Every STG reference resolves', stage_refs <= set(stage_ids), ', '.join(sorted(stage_refs - set(stage_ids))))

# 6. stage records are cited by a stage; stages do not restate requirement prose
cited = set(re.findall(r'LXM-REQ-\d{6}', stg_part))
stage_scoped = [r for b in blocks for r in [b.split(' — ')[0]] if re.search(r'`STG-\d{2}`', b)]
orph = [r for r in stage_scoped if r not in cited]
check('Every stage-scoped requirement is cited by a stage procedure', not orph, ', '.join(orph))
notcited = sorted(set(ids) - cited)
check('Requirements not cited by any stage (cross-cutting sections only)', all(re.search(r'`(EXE|ESC|OWN|ARC|RPT|FIN)`', next(b for b in blocks if b.startswith(r))) for r in notcited), ', '.join(n[-3:] for n in notcited))
dup = [r for r, t in text.items() for chunk in [t[:80]] if len(chunk) >= 60 and chunk in stg_part]
check('No requirement text duplicated in the stage procedures', not dup, ', '.join(dup))

# 6b. heading namespaces: catalogue groups are CAT-<scope>, procedures are bare STG-NN, and no heading is reused
body = M.replace(appx.decode('utf-8'), '')
all_heads = re.findall(r'^#{1,4} (.+)$', body, re.M)
reused = sorted({h for h in all_heads if all_heads.count(h) > 1})
check('Every heading outside Appendix A is unique', not reused, '; '.join(reused))
groups = re.findall(r'^### (\S+) — (.+)$', cat_part, re.M)
scope_of = {b.split(' — ')[0]: re.search(r'^`([A-Z]{3}(?:-\d{2})?)` · class', b, re.M).group(1) for b in blocks}
check('Every Part D group heading is CAT-<scope>, one per scope in use', [g for g, _ in groups if not g.startswith('CAT-')] == []
      and [g[4:] for g, _ in groups] == sorted(set(scope_of.values()), key=[g[4:] for g, _ in groups].index)
      and len(groups) == len(set(scope_of.values())), ', '.join(g for g, _ in groups))
check('No bare STG-NN heading in Part D and no CAT- heading in Part E',
      not re.search(r'^#{1,4} STG-\d{2}\b', cat_part, re.M) and not re.search(r'^#{1,4} CAT-', stg_part, re.M))
stage_title = dict(re.findall(r'^### (STG-\d{2}) — (.+)$', stg_part, re.M))
badgrp = [g for g, t in groups if g.startswith('CAT-STG-') and stage_title.get(g[4:]) != t]
check('Each CAT-STG-NN group names an existing procedure STG-NN with the same title', not badgrp, ', '.join(badgrp))
misplaced = []
for chunk in re.split(r'^### ', cat_part, flags=re.M)[1:]:
    g = chunk.split(' — ')[0]
    misplaced += [r for r in re.findall(r'^#### (LXM-REQ-\d{6}) — ', chunk, re.M) if 'CAT-' + scope_of[r] != g]
check('Every record sits under the group of its own scope', not misplaced, ', '.join(misplaced))

# 6c. citations resolve to the right record, and the generated indexes agree with Part E
cites_by_stage = {}
for chunk in re.split(r'^### (?=STG-\d{2} — )', stg_part, flags=re.M)[1:]:
    cites_by_stage[chunk[:6]] = set(re.findall(r'LXM-REQ-\d{6}', chunk))
cited_by = {}
for st, rs in cites_by_stage.items():
    for r in rs:
        cited_by.setdefault(r, set()).add(st)
wrong_stage = [r for r, sc in scope_of.items() if sc.startswith('STG-') and sc not in cited_by.get(r, set())]
check('Every stage-scoped record is cited by its own stage procedure', not wrong_stage, ', '.join(wrong_stage))
nonnorm = {r for r in ids if 'non-normative' in dict((h[0], h[2]) for h in heads)[r].lower() and text[r].startswith('Non-normative')}
check('Only non-normative records are left uncited by every stage (execution rules applied, not just listed)',
      set(ids) - set(cited_by) == nonnorm, 'uncited: %s; non-normative: %s' % (sorted(set(ids) - set(cited_by)), sorted(nonnorm)))
h1 = re.findall(r'^\| (STG-\d{2}) \| [^|]+ \| (\d+) \| ([^|]*) \|$', M.split('### H.1')[1].split('### H.2')[0], re.M)
bad_h1 = [st for st, n, rs in h1 if {'LXM-REQ-000' + x.strip() for x in rs.split(',') if x.strip()} != cites_by_stage.get(st)]
check('H.1 stage index matches the citations in Part E', len(h1) == 17 and not bad_h1, ', '.join(bad_h1))
h2 = re.findall(r'^\| (LXM-REQ-\d{6}) \| (?:[^|]+ \| ){4}([^|]+) \| [^|]+ \|$', M.split('### H.2')[1].split('# Appendix A')[0], re.M)
bad_h2 = [r for r, c in h2 if (set(re.findall(r'STG-\d{2}', c)) or set()) != cited_by.get(r, set())]
check('H.2 traceability rows match Part E for every record', sorted(r for r, _ in h2) == sorted(ids) and not bad_h2, '%d rows; bad: %s' % (len(h2), ', '.join(bad_h2)))

# 7. no source line silently dropped
def covered(prefix):
    s = set()
    for l in lin.values():
        for m in re.finditer(r'(?<![A-Za-z0-9-])' + prefix + r'(\d+)(?:-(\d+))?(?![0-9])', l):
            a = int(m.group(1)); b = int(m.group(2) or a)
            s.update(range(a, b + 1))
    return s
def content_lines(data, lo, hi):
    out = []
    for i, line in enumerate(data.decode('utf-8').split('\n')[lo - 1:hi], lo):
        t = line.strip()
        if not t or t == '---' or re.match(r'#{1,3} ', t):
            continue
        out.append((i, t))
    return out
c2 = covered('S'); c3 = covered('L')
u2 = [(i, t) for i, t in content_lines(b2, 1, 636) if i not in c2]
lead2 = [x for x in u2 if x[1].endswith(':')]
check('SRC-0002: every content line covered by a record (lead-in lines ending ":" are structural)', len(u2) == len(lead2),
      'uncovered non-lead-in: %s; structural lead-ins: %d (%s)' % ([i for i, t in u2 if not t.endswith(':')], len(lead2), ', '.join(str(i) for i, _ in lead2)))
u3 = [(i, t) for i, t in content_lines(b3, 1, 373) if i not in c3]
lead3 = [x for x in u3 if x[1].endswith(':')]
check('SRC-0003 procedure (lines 1-373): every content line covered (lead-ins structural)', len(u3) == len(lead3),
      'uncovered non-lead-in: %s; structural lead-ins: %d' % ([i for i, t in u3 if not t.endswith(':')], len(lead3)))
multi = {}
for r, l in lin.items():
    for m in re.finditer(r'(?<![A-Za-z0-9-])S(\d+)(?:-(\d+))?(?![0-9])', l):
        for n in range(int(m.group(1)), int(m.group(2) or m.group(1)) + 1):
            multi.setdefault(n, set()).add(r)
split = {n: sorted(v) for n, v in multi.items() if len(v) > 1}
check('SRC-0002 lines carried by more than one record (one bullet holding several requirements; each record has one disposition)', True,
      '; '.join('S%d→%s' % (n, '/'.join(x[-3:] for x in v)) for n, v in sorted(split.items())))

# 8. final report coverage
cov = re.findall(r'^\| (RE-\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$', M, re.M)
secs_used = set()
badcov = []
for eid, src, el, secs in cov:
    ss = re.findall(r'\b([A-K]) \(LXM-REQ-(\d{6})\)', secs)
    if not ss:
        badcov.append(eid)
    for s, n in ss:
        secs_used.add(s)
        if 'LXM-REQ-' + n not in ids:
            badcov.append(eid)
check('Every mandated reporting element maps to a defined A–K section', cov and not badcov, '%d elements; bad: %s' % (len(cov), badcov))
check('Every section A–K carries at least one mandated element', secs_used == set('ABCDEFGHIJK'), ''.join(sorted(secs_used)))
rpt_titles = [t for h in heads for t in [h[2]] if re.match(r'^[A-K]\. ', t)]
check('Final report records A–K exist in order', [t[0] for t in rpt_titles] == list('ABCDEFGHIJK'))

# 9. owner decisions and reconciliation file
for k in range(1, 9):
    dk = 'LXM-DEC-%06d' % k
    check('K%d (%s) applied by at least one record' % (k, dk), any(dk in b for b in blocks))

# 10. SRC-0008 assimilation (LXM-ACP-001): extended records keep their identity; new records trace only to SRC-0008
check('SRC-0008 is in the source register', bool(re.search(r'^\| SRC-0008 \|', M, re.M)))
EXTENDED = {  # record: (scope, class, disposition, lineage before SRC-0008, SRC-0008 sections added)
    'LXM-REQ-000016': ('ESC', 'OM', 'Restored', 'S37,S39; L20,L363; A1082; SRC-0007 §2', '§7'),
    'LXM-REQ-000201': ('ARC', 'NEW', 'New-owner-addition', 'SRC-0004 §1; SRC-0005; SRC-0006 §12', '§2'),
    'LXM-REQ-000203': ('ARC', 'NEW', 'New-owner-addition', 'SRC-0004 §1; SRC-0005; SRC-0006 §12; SRC-0007 §5', '§3,§5'),
    'LXM-REQ-000215': ('ARC', 'NEW', 'New-owner-addition', 'SRC-0006 §8-9,§22', '§4,§6')}
def sec_list(l, src):
    m = re.search(re.escape(src) + r' ((?:§[\d.\-]+,?)+)', l)
    return m.group(1).split(',') if m else []
bad_ext = [r for r, (sc, c, d, old, add) in EXTENDED.items()
           if (scope_of.get(r), cls.get(r), disp.get(r)) != (sc, c, [d]) or not lin.get(r, '').startswith(old + '; SRC-0008 §')
           or not set(add.split(',')) <= set(sec_list(lin[r], 'SRC-0008'))]
check('Four extended records keep scope, class, disposition and prior lineage, and still cite their SRC-0008 sections', not bad_ext, ', '.join(bad_ext))
only_8 = sorted(r for r, l in lin.items() if l.split(';')[0].startswith('SRC-0008'))  # originated by SRC-0008; later sources may recognize them
sec8 = sorted({s.split('.')[0] for r in only_8 for s in sec_list(lin[r], 'SRC-0008')}, key=lambda s: int(s[1:]))
base_8 = ['LXM-REQ-%06d' % n for n in range(220, 227)]  # the first SRC-0008 assimilation; later decided additions may join
check('New SRC-0008 records 220–226: ARC, class NEW, New-owner-addition, cited by a stage, covering §1–§8',
      set(base_8) <= set(only_8) and sec8 == ['§%d' % i for i in range(1, 9)]
      and all(scope_of[r] == 'ARC' and cls[r] == 'NEW' and disp[r] == ['New-owner-addition'] and r in cited_by for r in base_8),
      '%s; sections %s' % (', '.join(x[-3:] for x in only_8), ','.join(sec8)))

# 11. clause-level semantic coverage for every source with a clause ledger (sources/<SRC>.clauses)
import glob, os
root = os.path.dirname(os.path.dirname(os.path.abspath(master_p)))
srcreg = set(re.findall(r'^\| (SRC-\d{4}) \|', M, re.M))
cov_rel = {}
for b in blocks:
    m = re.search(r'^Coverage: (.*?)\s*$', b, re.M)
    for tok in (m.group(1).split('; ') if m else []):
        s, c, rel = tok.split(' ')
        cov_rel.setdefault((s, c), []).append((b.split(' — ')[0], rel))
RELS = {'covers', 'extends', 'supports', 'depends-on'}
bad_tok = sorted({'%s %s' % k for k, v in cov_rel.items() if k[0] not in srcreg or any(rel not in RELS for _, rel in v)})
check('Every coverage relation names a registered source and a known relation', not bad_tok, ', '.join(bad_tok))
exc_p = os.path.join(root, 'intake', 'exceptions.txt')
held = set(re.findall(r'^@LXM-EXC-\d{6} \| (?:QUARANTINED|REJECTED) \| [^\n]*\nsource: (SRC-\d{4} §[0-9A-Za-z.]+)$', open(exc_p, encoding='utf-8').read(), re.M)) if os.path.exists(exc_p) else set()
for led in sorted(glob.glob(os.path.join(root, 'sources', 'SRC-*.clauses'))):
    src = os.path.basename(led)[:8]
    L_ = open(led, encoding='utf-8').read()
    clauses = re.findall(r'^(§[0-9A-Za-z.]+) \|', L_, re.M)
    status = (re.search(r'^status: (\S+)', L_, re.M) or [None, 'in-progress'])[1]
    ext = re.search(r'^extract: (\S+) sha256 (\w+)', L_, re.M)
    check('%s ledger: extract unchanged since the clauses were taken' % src,
          bool(ext) and hashlib.sha256(open(os.path.join(root, ext.group(1)), 'rb').read()).hexdigest() == ext.group(2))
    unknown = sorted(c for (s, c) in cov_rel if s == src and c not in clauses)
    check('%s ledger: every coverage relation names a ledger clause' % src, not unknown, ', '.join(unknown))
    if status != 'complete':
        check('%s ledger: assimilation in progress, completeness not yet asserted' % src, True, status)
        continue
    open_cl = [c for c in clauses if not any(rel in ('covers', 'extends') for _, rel in cov_rel.get((src, c), [])) and '%s %s' % (src, c) not in held]
    check('%s ledger: every clause is covered by a record or held by an open intake exception' % src, not open_cl,
          '%d clauses; held: %s; uncovered: %s' % (len(clauses), ', '.join(sorted(h.split(' ')[1] for h in held if h.startswith(src))) or 'none', ', '.join(open_cl)))
    citing = sorted(r for r, l in lin.items() if sec_list(l, src))
    unsub = [r for r in citing if not any(r == rr for v in [x for (s, _), x in cov_rel.items() if s == src] for rr, _ in v)]
    check('%s ledger: every record citing the source has a clause-level relation to it' % src, not unsub, ', '.join(unsub))
# 12. source authority versus source text status (no invented confirmation)
reg = [[c.strip() for c in l.split(' | ')] for l in open(os.path.join(root, 'sources.txt'), encoding='utf-8').read().split('\n') if l.startswith('SRC-')]
TEXT_STATUS = {'owner-file', 'owner-confirmed', 'provisional-extract', 'conversation-only'}
check('Every source has an authority and a known text status', all(len(r) == 7 and r[5] in ('owner', 'owner-decision', 'historical') and r[6] in TEXT_STATUS for r in reg),
      ', '.join(r[0] for r in reg if len(r) != 7 or r[6] not in TEXT_STATUS))
row_md = dict(re.findall(r'^\| (SRC-\d{4}) \| (.*)$', M, re.M))
unpinned = [r[0] for r in reg if r[6] in ('owner-file', 'owner-confirmed', 'provisional-extract') and not re.search(r'`[0-9a-f]{64}`', row_md.get(r[0], ''))]
check('Every owner-file, owner-confirmed or provisional source shows a SHA-256 in the register', not unpinned, ', '.join(unpinned))
confirmed = [r[0] for r in reg if r[6] == 'owner-confirmed' and not re.search(r'LXM-DEC-\d{6}', r[2])]
check('No source is owner-confirmed without a recorded owner decision in its location', not confirmed, ', '.join(confirmed))
prov_ok = all(os.path.exists(os.path.join(root, 'sources', r[0] + '.extract.md')) and
              hashlib.sha256(open(os.path.join(root, 'sources', r[0] + '.extract.md'), 'rb').read()).hexdigest() in row_md.get(r[0], '')
              for r in reg if r[6] == 'provisional-extract')
check('Every provisional extract exists and the register shows its exact SHA-256', prov_ok)
cited_src = {s for l in lin.values() for s in re.findall(r'SRC-\d{4}', l)}
check('Every source cited in a lineage is registered', cited_src <= {r[0] for r in reg}, ', '.join(sorted(cited_src - {r[0] for r in reg})))
check('The Master states the text status of every source', all(r[0] in M.split('**Source text status**')[1].split('Records resting')[0] for r in reg) if '**Source text status**' in M else False)
h3 = M.split('### H.3')[1].split('# Appendix A')[0] if '### H.3' in M else ''
h3_rows, h3_bad = [], []
for part in re.split(r'^(?=\*\*SRC-\d{4}\*\* — ledger status)', h3, flags=re.M)[1:]:  # completeness is asserted only for complete ledgers
    rows_ = re.findall(r'^\| (§[0-9A-Za-z.]+) \| [\d-]+ \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$', part, re.M)
    h3_rows += rows_
    if '*complete*' in part.split('\n')[0]:
        h3_bad += [part[2:10] + ' ' + c for c, cov, sup, hold in rows_ if cov.strip() == '—' and hold.strip() == '—']
check('H.3 clause coverage index lists every ledger clause; in a complete ledger each is covered or held', len(h3_rows) == sum(
    len(re.findall(r'^§', open(p, encoding='utf-8').read(), re.M)) for p in glob.glob(os.path.join(root, 'sources', 'SRC-*.clauses'))) and not h3_bad,
    '%d rows; uncovered and unheld: %s' % (len(h3_rows), ', '.join(h3_bad)))
# 12b. every stage action carries a permanent ID, unique in its stage, shown in Part E
st_txt = open(os.path.join(root, 'stages.txt'), encoding='utf-8').read()
bad_a, seen_a = [], set()
for st in re.split(r'^#(?=STG-\d{2} \|)', st_txt, flags=re.M)[1:]:
    ids_a = []
    for l in st.split('\n'):
        if l.startswith('- '):
            m = re.match(r'- A-(\d+) \S', l)
            ids_a.append(int(m.group(1)) if m else None)
    if None in ids_a or len(ids_a) != len(set(ids_a)):
        bad_a.append(st[:6])
    seen_a |= {'%s.A-%d' % (st[:6], k) for k in ids_a if k}
shown_a = set(re.findall(r'^- `(STG-\d{2}\.A-\d+)` ', stg_part, re.M))
check('Every stage action has a stable ID (STG-NN.A-k), unique in its stage, and Part E shows each one', not bad_a and seen_a == shown_a,
      ', '.join(bad_a) or '%d actions' % len(seen_a))
# 13. decisions, decided records and exception resolutions agree (the register is decisions.txt; Part C is rendered from it)
import importlib.util
_spec = importlib.util.spec_from_file_location('lxm_build', os.path.join(root, 'build.py'))
_build = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_build)
layouts, decs = _build.parse_decisions(open(os.path.join(root, 'decisions.txt'), encoding='utf-8').read())
dids = [d['id'] for d in decs]
check('Decision register: IDs unique and contiguous from LXM-DEC-000001, each with status adopted or open and a known table',
      dids == ['LXM-DEC-%06d' % i for i in range(1, len(dids) + 1)] and all(d['status'] in ('adopted', 'open') and d['group'] in layouts for d in decs),
      '%d decisions' % len(dids))
grp_status = {}
for d in decs:
    grp_status.setdefault(d['group'], set()).add(d['status'])
check('Each Part C table holds one status only (adopted and open decisions never share a table)', all(len(v) == 1 for v in grp_status.values()),
      ', '.join('%s: %s' % (g, '/'.join(sorted(v))) for g, v in sorted(grp_status.items())))
part_c = M.split('## Part C')[1].split('\n## ')[0] if '## Part C' in M else ''
check('Part C is exactly the rendering of decisions.txt', all(_build.decision_table(layouts, decs, g) in part_c for g in layouts)
      and sorted(re.findall(r'^\| (LXM-DEC-\d{6})\b', part_c, re.M)) == sorted(dids))
adopted = {d['id'] for d in decs if d['status'] == 'adopted'}
miss = ['%s %s' % (d['id'], k) for d in decs for k in (('o', 'e') if d['status'] == 'adopted' else ('q',)) if not d.get(k)]
check('Every adopted decision records its outcome and effect; every open decision its question', not miss, ', '.join(miss))
kd = {}
reqs_txt = open(os.path.join(root, 'reqs.txt'), encoding='utf-8').read()
for blk in re.split(r'\n(?=@LXM-REQ-)', reqs_txt):
    m = re.match(r'@(LXM-REQ-\d{6})', blk)
    k = re.search(r'^k: (.*)$', blk, re.M)
    if m and k:
        kd[m.group(1)] = set(re.findall(r'LXM-DEC-\d{6}', k.group(1)))
ids_all = set(re.findall(r'^@(LXM-REQ-\d{6})', reqs_txt, re.M))
bad_k = sorted(r for r, ds in kd.items() if ds - adopted)
check('Every decision a record cites is adopted (an open or unknown decision decides nothing)', not bad_k, ', '.join(bad_k))
scope_bad, effect_bad, k18, pending = [], [], {}, []
for d in decs:
    if d['status'] != 'adopted':
        continue
    cell = d.get('a')
    if cell is None or not (cell == 'None' or re.fullmatch(r'(?:(?:SRC-\d{4} (?:§[0-9A-Za-z.]+(?:, )?)+|LXM-REQ-\d{6})(?:, )?)+', cell)):
        scope_bad.append('%s (%s)' % (d['id'], 'no a: field' if cell is None else cell))
    if d.get('label', '') in ['K%d' % i for i in range(1, 9)]:
        k18[d['id']] = cell
    eff = d.get('e', '')
    carried = any(d['id'] in ds for ds in kd.values())
    if not eff or set(re.findall(r'LXM-REQ-\d{6}', eff)) - ids_all or (cell == 'None' and not carried):
        effect_bad.append(d['id'])  # an empty-scope decision can never be applied later, so it must already be carried
    elif not carried:
        pending.append(d['id'])     # a scoped decision is applied by gated changes inside its scope; until the first, it is pending
check('Every adopted decision records its mutation-authorization scope explicitly: None, or source clauses and records only', not scope_bad, ', '.join(scope_bad))
check('K1-K8 have an empty mutation-authorization scope, as the owner confirmed', len(k18) == 8 and all(v == 'None' for v in k18.values()),
      ', '.join('%s=%s' % kv for kv in sorted(k18.items()) if kv[1] != 'None') or '%d decisions' % len(k18))
check('Every adopted decision keeps its normative effect: an effect naming existing records; one with an empty scope is carried by a record', not effect_bad, ', '.join(effect_bad))
check('Adopted decisions whose scoped effect no gated change has applied yet (reported, not a failure)', True, ', '.join(pending) or 'none')
# 13b. evidence register (evidence.txt, rendered as G.3)
ev_layouts, evs = _build.parse_evidence(open(os.path.join(root, 'evidence.txt'), encoding='utf-8').read())
eids = [e['id'] for e in evs]
check('Evidence register: IDs unique and contiguous from LXM-EVD-000001', eids == ['LXM-EVD-%06d' % i for i in range(1, len(eids) + 1)], '%d entries' % len(eids))
known_refs = ids_all | set(dids) | set(eids)
bad_e = []
for e in evs:
    if any(not e.get(k) for k in ('fact', 'source', 'method', 'observed', 'observer', 'verifies', 'status')):
        bad_e.append(e['id'] + ' (missing field)')
    refs = re.findall(r'LXM-(?:REQ|DEC|EVD)-\d{6}', e.get('verifies', ''))
    if not refs or set(refs) - known_refs:
        bad_e.append(e['id'] + ' (verifies)')
    m = re.match(r'superseded by (LXM-EVD-\d{6})$', e.get('status', ''))
    if m and (m.group(1) not in eids or eids.index(m.group(1)) <= eids.index(e['id'])):
        bad_e.append(e['id'] + ' (superseded by an unknown or earlier entry)')
    if not m and e.get('status') not in ('current', 'current for that SHA', 'stale'):
        bad_e.append(e['id'] + ' (status "%s")' % e.get('status'))
check('Every evidence entry states fact, source, method, time, observer and status, and verifies existing records', not bad_e, ', '.join(bad_e))
g3 = M.split('### G.3')[1].split('\n### ')[0] if '### G.3' in M else ''
check('G.3 is exactly the rendering of evidence.txt', all(_build.decision_table(ev_layouts, evs, g) in g3 for g in ev_layouts))
evd_used = set(re.findall(r'LXM-EVD-\d{6}', M))
check('Every LXM-EVD reference resolves', evd_used <= set(eids), ', '.join(sorted(evd_used - set(eids))))
# 13d. the gate's log is tamper-evident (hash chain from the first schema-2 line)
def _chain(path):
    ls_ = [x for x in open(path, encoding='utf-8').read().split('\n') if x.strip()] if os.path.exists(path) else []
    started = False
    for i, x in enumerate(ls_):
        e = _json.loads(x)
        if e.get('schema', 1) >= 2:
            started = True
            if e.get('prev') != (hashlib.sha256(ls_[i - 1].encode()).hexdigest() if i else None) or e.get('seq') != i + 1:
                return False, 'line %d breaks the chain' % (i + 1)
        elif started:
            return False, 'legacy line %d after the chain started' % (i + 1)
    return True, '%d lines, %d chained' % (len(ls_), sum(1 for x in ls_ if _json.loads(x).get('schema', 1) >= 2))
import json as _json
_ok, _det = _chain(os.path.join(root, 'intake', 'ledger.jsonl'))
check('The gate log is an unbroken hash chain from its first chained line (tamper-evident)', _ok, _det)
# 13c. implementation traceability (trace.txt, rendered as H.4)
import json as _json
default_basis, trace = _build.parse_trace(open(os.path.join(root, 'trace.txt'), encoding='utf-8').read())
bad_t = sorted(r for r, t in trace.items() if r not in ids_all or t['_dup'] or set(t) - {'_dup'} - set(_build.TRACE_FIELDS))
check('Implementation traceability: each block names an existing requirement once, with known fields only', not bad_t and bool(default_basis), ', '.join(bad_t) or '%d blocks' % len(trace))
decl_ids = {d['id'] for d in _json.load(open(os.path.join(root, 'config_adapter.json'), encoding='utf-8'))['declarations']}
bad_c = sorted('%s:%s' % (r, c) for r, t in trace.items() for c in t.get('config', '').split(', ') if c and c not in decl_ids)
check('Every configuration a requirement traces to is a declaration of the configuration adapter', not bad_c, ', '.join(bad_c))
gap_nb = sorted(r for r, t in trace.items() if not t.get('impl') and not t.get('basis'))
check('Every known gap (a block without impl) states its basis', not gap_nb, ', '.join(gap_nb))
h4 = M.split('### H.4')[1].split('\n### ')[0] if '### H.4' in M else ''
check('H.4 lists every traced requirement exactly once', sorted(re.findall(r'^\| (LXM-REQ-\d{6}) \|', h4, re.M)) == sorted(trace), '%d rows' % len(re.findall(r'^\| (LXM-REQ-\d{6}) \|', h4, re.M)))
exc_t = open(exc_p, encoding='utf-8').read() if os.path.exists(exc_p) else ''
bad_res = []
for m in re.finditer(r'^@(LXM-EXC-\d{6}) \| RESOLVED \|[^\n]*\n((?:[a-z]+: [^\n]*\n?)*)', exc_t, re.M):
    res = re.search(r'^resolved: (.*)$', m.group(2), re.M)
    if res and (set(re.findall(r'LXM-REQ-\d{6}', res.group(1))) - ids_all or set(re.findall(r'LXM-DEC-\d{6}', res.group(1))) - adopted):
        bad_res.append(m.group(1))
    src_cl = re.search(r'^source: (SRC-\d{4}) (§\S+)$', m.group(2), re.M)  # a contribution with no clause (e.g. complete-ledger) is recorded as '?' and has none to cover
    if res and src_cl and not any('%s %s covers' % (src_cl.group(1), c) in reqs_txt or '%s %s extends' % (src_cl.group(1), c) in reqs_txt for c in src_cl.group(2).split(',')):
        bad_res.append(m.group(1) + ' (clause not covered)')
check('Every resolved exception names existing records and adopted decisions, and its clause is covered', not bad_res, ', '.join(bad_res))
R = open(recon_p, encoding='utf-8').read()
rows = re.findall(r'^\| (LXM-REQ-\d{6}) \|', R, re.M)
check('Reconciliation file has exactly the 128 rows', rows == first128, str(len(rows)))

w = max(len(n) for n, _, _ in results)
fails = 0
for n, ok, d in results:
    fails += not ok
    print('%s  %s%s' % ('PASS' if ok else 'FAIL', n, ('  — ' + d) if d else ''))
print('\n%d checks, %d failed' % (len(results), fails))
sys.exit(1 if fails else 0)
