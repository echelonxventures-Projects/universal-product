"""Level 1 capture: the one way any source enters the Master Context (design §1, gap 14 of the Level 1 checklist).
Usage:
  python3 -I capture.py <root> --file <path> --id SRC-NNNN --title T --role R --authority owner|owner-decision|historical [--sensitivity S] [--by NAME]
  python3 -I capture.py <root> --transcript <session.jsonl> --line N [--block K] --id ... (same options)

It reads the bytes exactly; refuses anything that looks like a secret (secrets never enter the Master); writes the extract,
provenance (with sensitivity), a clause ledger in progress and one contribution per clause (intake/<id>/); then registers the
source through the gate (kind: source). Clause resolutions are reviewed before submission. A rerun on the same input is a NOOP.
Exit 0 captured or already captured, 2 refused."""
import hashlib, json, os, re, subprocess, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import assimilate as A

SECRETS = [r'-----BEGIN [A-Z ]*PRIVATE KEY-----', r'\bAKIA[0-9A-Z]{16}\b', r'\bgh[pousr]_[A-Za-z0-9]{30,}\b', r'\bsk-[A-Za-z0-9]{20,}\b',
           r'\bxox[abposr]-[A-Za-z0-9-]{10,}\b', r'(?i)\b(?:password|passwd|secret|api[_-]?key|token)\s*[:=]\s*["\']?[^\s"\'<>]{8,}']
SENSITIVITY = ('public', 'internal', 'confidential')


def segment(lines):
    """Clauses: a list with its lead-in is one clause; every other sentence paragraph is one; headings and metadata are none."""
    heading = lambda x: x.startswith('#') or re.match(r'^(Decision|DECISION) \d+ —', x)
    item = lambda x: re.match(r'^\s*(?:[-*]|\d+\.)\s+', x)
    spec, sec, k, i, n = [], '0', 0, 0, len(lines)
    while i < n:
        x = lines[i]
        if not x.strip() or heading(x) or (x.startswith('**') and ':**' in x and not item(x)):
            m = re.match(r'^#+\s*(\d+)\.', x) or re.match(r'^(?:Decision|DECISION) (\d+)', x)
            if m:
                sec, k = m.group(1), 0
            i += 1
            continue
        a = i
        if x.rstrip().endswith(':') and not item(x):
            j = i + 1
            while j < n and (not lines[j].strip() or item(lines[j])):
                j += 1
            i = j - 1
            while not lines[i].strip():
                i -= 1
        k += 1
        spec.append(('§%s.%d' % (sec, k) if sec != '0' or k > 0 else '§%d' % k, a + 1, i + 1))
        i += 1
    return spec


def clean(t):
    return re.sub(r'^\s*(?:[-*]|\d+\.)\s+', '', re.sub(r'\*\*|`', '', t)).strip()


def capture(root, raw, origin, sid, title, role, authority, sensitivity='internal', by='amazon-44', today=None):
    if sensitivity not in SENSITIVITY:
        return {'outcome': 'REJECTED', 'reason': 'sensitivity must be one of %s' % ', '.join(SENSITIVITY)}
    hits = [p for p in SECRETS if re.search(p, raw)]
    if hits:
        return {'outcome': 'REJECTED', 'reason': 'the text looks like it contains a secret (%d pattern(s)); secrets never enter the Master. Redact it, or store it in the write-once archive outside git.' % len(hits)}
    text = raw.rstrip('\n') + '\n'
    xsha = hashlib.sha256(text.encode()).hexdigest()
    ext = os.path.join(root, 'sources', sid + '.extract.md')
    if os.path.exists(ext) and A.read(ext) != text:
        return {'outcome': 'REJECTED', 'reason': '%s exists with different text; a changed text is a new capture under a new id' % sid}
    lines = text.split('\n')
    fdir = os.path.join(root, 'intake', sid, 'files')  # Level 1: the files reach sources/ only through the gate
    os.makedirs(fdir, exist_ok=True)
    def new_file(path, content):
        open(path, 'w', encoding='utf-8').write(content)
    spec = segment(lines)
    if not spec:
        return {'outcome': 'REJECTED', 'reason': 'no clause found (only headings or metadata)'}
    os.makedirs(os.path.join(root, 'intake', sid), exist_ok=True)
    new_file(os.path.join(fdir, sid + '.extract.md'), text)
    led = ['# %s clause ledger: clause | extract lines | text digest (first 16 hex of SHA-256 of the lines joined by newlines). Captured by capture.py from %s.' % (sid, origin),
           '# A list is one clause together with its lead-in; every other sentence paragraph is a clause; headings and metadata are none.',
           'status: in-progress', 'extract: sources/%s.extract.md sha256 %s' % (sid, xsha)]
    for sec, a, b in spec:
        led.append('%s | %d-%d | %s' % (sec, a, b, hashlib.sha256('\n'.join(lines[a - 1:b]).encode()).hexdigest()[:16]))
        parts = [clean(y) for y in lines[a - 1:b] if y.strip()]
        t = ' '.join(p if p.endswith(('.', ':', '?')) else p + ';' for p in parts).rstrip(';')
        t = t if t.endswith(('.', ':', '?')) else t + '.'
        p = os.path.join(root, 'intake', sid, sec[1:].replace('.', '-') + '.ctb')
        if not os.path.exists(p):
            new_file(p, 'id: CTB-%s-%s\nsource: %s\nsection: %s\nkind: requirement\ntext: %s\n' % (sid.replace('-', ''), sec[1:].replace('.', '-'), sid, sec, t))
    new_file(os.path.join(fdir, sid + '.clauses'), '\n'.join(led) + '\n')
    pp = os.path.join(fdir, sid + '.provenance.md')
    if True:
        new_file(pp, '# %s provenance — provisional working extract\n\n| Field | Value |\n|---|---|\n| Source | %s, %s |\n| Authority | %s (as registered in `sources.txt`) |\n'
                                              '| Text status | **provisional-extract**: not owner-confirmed |\n| Sensitivity | %s |\n| Extract | `sources/%s.extract.md`, SHA-256 `%s` |\n'
                                              '| Captured from | %s |\n| Method | capture.py: the bytes, unchanged, one trailing newline; secret scan passed |\n| Captured by | `%s`, %s |\n'
                                              '| Clause ledger | `sources/%s.clauses` (%d clauses) |\n\nOnly the owner can confirm this text (Part G.4, item 10).\n' % (
                                                  sid, sid, title, authority, sensitivity, sid, xsha, origin, by, today or 'today', sid, len(spec)))
    reg = os.path.join(root, 'intake', sid, 'register.source-ctb')
    open(reg, 'w', encoding='utf-8').write('id: CTB-REGISTER-%s\nkind: source\nsource: %s\naction: register\ntitle: %s\nlocation: %s; provisional working extract `sources/%s.extract.md`\n'
                                           'sha: `{SHA:sources/%s.extract.md}` (extract, not owner-confirmed)\nrole: %s\nauthority: %s\ntext-status: provisional-extract\nfiles-from: intake/%s/files\nbasis: captured by capture.py (secret scan passed, sensitivity %s)\n' % (
                                               sid, sid, title, origin, sid, sid, role, authority, sid, sensitivity))
    r = A.assimilate(root, reg)  # a refusal touches nothing canonical: the files stay in Level 1 with the refusal on record
    return {'outcome': r['outcome'], 'reason': r.get('reason'), 'clauses': len(spec), 'ledger_seq': r.get('ledger_seq')}


def from_transcript(path, line, block=None):
    e = json.loads(open(path, encoding='utf-8').read().split('\n')[line - 1])
    c = e.get('message', {}).get('content')
    t = c if isinstance(c, str) else ''.join(x.get('text', '') for x in (c or []) if isinstance(x, dict) and x.get('type') == 'text')
    blocks = re.findall(r'<pasted_content id="[^"]+">\n(.*?)\n</pasted_content', t, re.S)
    return (blocks[block] if block is not None else t.strip()), 'session transcript %s line %d%s' % (os.path.basename(path), line, '' if block is None else ' paste block %d' % block)


if __name__ == '__main__':
    opt = lambda k: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else None
    root = sys.argv[1]
    if opt('--file'):
        raw, origin = open(opt('--file'), encoding='utf-8').read(), 'file %s' % opt('--file')
    else:
        raw, origin = from_transcript(opt('--transcript'), int(opt('--line')), int(opt('--block')) if opt('--block') else None)
    r = capture(root, raw, origin, opt('--id'), opt('--title'), opt('--role'), opt('--authority'), opt('--sensitivity') or 'internal', opt('--by') or 'amazon-44', opt('--today'))
    print(json.dumps(r))
    sys.exit(0 if r['outcome'] in ('NEW', 'NOOP') else 2)
