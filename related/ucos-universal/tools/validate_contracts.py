#!/usr/bin/env python3
"""validate_contracts — checks for contracts, acceptance scenarios, SLOs and repository hygiene.

Complements tools/ucos_check.py (registry, composition, gates). Deterministic, offline, no AI calls.
  1. Repository hygiene: no sync-conflict duplicates ("name 2.ext"), no editor/OS litter tracked
  2. gRPC contracts compile (grpc_tools.protoc, pinned)
  3. OpenAPI 3.1 documents validate (kernel + generated); no colliding paths ('#')
  4. Event payload schemas are valid JSON Schema; AsyncAPI catalogue references only existing payloads
     and lists every event declared by a manifest
  5. Gherkin features parse; every step matches the vocabulary (spec/acceptance/steps.yaml);
     @platform, @gate, @universe and @phase tags resolve; quoted error codes exist in the registry
  6. Service levels validate against their schema; every alert's runbook file and section exist
  7. Cedar policies parse; policy tests (spec/policies/tests/*.yaml) give the expected decisions (SEC-POLICY-01)
  8. Composition rules (spec/rules/**/*.dl) parse; predicates are declared with consistent arity; negation is
     stratified; every head variable is bound in the body
  9. Every decision declared by a hand-authored manifest has a default table in spec/decisions/
Exit 0 = all pass. Usage: python3 tools/validate_contracts.py [--quick]   (--quick skips OpenAPI validation)
"""
import glob, json, os, re, subprocess, sys, tempfile
import yaml
from jsonschema import Draft202012Validator

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors = []
counts = {}
def err(m): errors.append(m)
def rel(p): return os.path.relpath(p, ROOT)

# ---------------------------------------------------------------- 1. hygiene
DUP = re.compile(r' \d+(\.[A-Za-z0-9]+)?$')
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in ('.git', 'node_modules', '.venv', 'generated')]
    for n in filenames + dirnames:
        stem = n.rsplit('.', 1)[0] if '.' in n else n
        if DUP.search(stem) or DUP.search(n):
            err(f'sync-conflict duplicate: {rel(os.path.join(dirpath, n))} (delete it; see CONTRIBUTING.md)')
        if n in ('.DS_Store', 'Thumbs.db'):
            pass  # ignored by .gitignore; harmless locally
counts['hygiene'] = 'ok'

# ---------------------------------------------------------------- 2. protos
proto_root = os.path.join(ROOT, 'spec', 'api', 'proto')
protos = sorted(glob.glob(os.path.join(proto_root, '**', '*.proto'), recursive=True))
if protos:
    with tempfile.TemporaryDirectory() as td:
        r = subprocess.run([sys.executable, '-m', 'grpc_tools.protoc', f'-I{proto_root}', f'--descriptor_set_out={td}/d.pb',
                            '--include_imports'] + [os.path.relpath(p, proto_root) for p in protos],
                           capture_output=True, text=True, cwd=proto_root)
        if r.returncode != 0:
            err('protoc failed:\n' + r.stderr.strip())
counts['protos'] = len(protos)

# ---------------------------------------------------------------- 3. OpenAPI
oa_files = sorted(glob.glob(os.path.join(ROOT, 'spec', 'api', 'openapi', '**', '*.yaml'), recursive=True))
op_ids = {}
for f in oa_files:
    d = yaml.safe_load(open(f))
    for path, ops in (d.get('paths') or {}).items():
        if '#' in path:
            err(f'{rel(f)}: colliding path {path!r} (fix the command/query naming or the path rule)')
        for method, op in ops.items():
            if isinstance(op, dict) and 'operationId' in op:
                if op['operationId'] in op_ids:
                    err(f'duplicate operationId {op["operationId"]} in {rel(f)} and {op_ids[op["operationId"]]}')
                op_ids[op['operationId']] = rel(f)
if '--quick' not in sys.argv:
    from openapi_spec_validator import validate
    from openapi_spec_validator.readers import read_from_filename
    for f in oa_files:
        try:
            spec_dict, base_uri = read_from_filename(f)
            validate(spec_dict, base_uri=base_uri)
        except Exception as e:
            err(f'OpenAPI invalid: {rel(f)}: {str(e).splitlines()[0]}')
counts['openapi'] = len(oa_files)
counts['operations'] = len(op_ids)

# ---------------------------------------------------------------- 4. events and AsyncAPI
payload_dir = os.path.join(ROOT, 'spec', 'events', 'payloads')
payloads = sorted(glob.glob(os.path.join(payload_dir, '*.schema.json')) + glob.glob(os.path.join(payload_dir, 'hand', '*.schema.json')))
for f in payloads:
    try:
        Draft202012Validator.check_schema(json.load(open(f)))
    except Exception as e:
        err(f'payload schema invalid: {rel(f)}: {str(e).splitlines()[0]}')
for f in glob.glob(os.path.join(payload_dir, 'hand', '*.schema.json')):
    if not os.path.exists(os.path.join(payload_dir, os.path.basename(f))):
        err(f'hand payload {rel(f)} has no declared event of that type in any manifest')
declared = set()
for f in glob.glob(os.path.join(ROOT, 'spec', 'capabilities', 'packs', '*.yaml')):
    declared |= set(yaml.safe_load(open(f))['spec'].get('provides', {}).get('events', []) or [])
aa_path = os.path.join(ROOT, 'spec', 'api', 'asyncapi', 'ucos-events.yaml')
aa = yaml.safe_load(open(aa_path))
if aa.get('asyncapi') != '3.0.0':
    err('asyncapi: version must be 3.0.0')
msgs = aa.get('components', {}).get('messages', {})
for name, m in msgs.items():
    ref = m.get('payload', {}).get('$ref', '')
    if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(aa_path), ref))):
        err(f'asyncapi: message {name} payload {ref} does not exist')
for ev in sorted(declared - set(msgs)):
    err(f'asyncapi: declared event {ev} missing from the catalogue (run tools/gen_contracts.py)')
for op, o in aa.get('operations', {}).items():
    ch = o['channel']['$ref'].split('/')[-1]
    if ch not in aa.get('channels', {}):
        err(f'asyncapi: operation {op} references unknown channel {ch}')
counts['events'] = len(declared)

# ---------------------------------------------------------------- 5. acceptance
from gherkin.parser import Parser
vocab = yaml.safe_load(open(os.path.join(ROOT, 'spec', 'acceptance', 'steps.yaml')))['steps']
vocab_re = [(s['id'], re.compile(s['pattern'])) for s in vocab]
used_ids = set()
gate_ids = {g['id'] for g in yaml.safe_load(open(os.path.join(ROOT, 'spec', 'certification', 'gates.yaml')))['gates']}
golden = {os.path.basename(p).replace('.pd.yaml', '') for p in glob.glob(os.path.join(ROOT, 'spec', 'composition', 'golden', '*.pd.yaml'))}
universes = {os.path.basename(p).split('-')[0] for p in glob.glob(os.path.join(ROOT, 'constitutions', 'U*')) if os.path.isdir(p)}
error_codes = {e['code'] for e in yaml.safe_load(open(os.path.join(ROOT, 'spec', 'registries', 'errors.yaml')))['errors']}
features = sorted(glob.glob(os.path.join(ROOT, 'spec', 'acceptance', '**', '*.feature'), recursive=True))
n_scen = 0
for f in features:
    try:
        doc = Parser().parse(open(f, encoding='utf-8').read())
    except Exception as e:
        err(f'gherkin parse error: {rel(f)}: {e}')
        continue
    feat = doc.get('feature')
    if not feat:
        err(f'{rel(f)}: no Feature')
        continue
    tags = [t['name'] for t in feat.get('tags', [])]
    if not any(t.startswith('@platform:') for t in tags):
        err(f'{rel(f)}: feature needs a @platform:<golden-pd|any> tag')
    if not any(t.startswith('@gate:') for t in tags):
        err(f'{rel(f)}: feature needs at least one @gate:<id> tag')
    for t in tags:
        k, _, v = t[1:].partition(':')
        if k == 'platform' and v != 'any' and v not in golden:
            err(f'{rel(f)}: @platform:{v} is not a golden platform definition')
        elif k == 'gate' and v not in gate_ids:
            err(f'{rel(f)}: @gate:{v} is not in spec/certification/gates.yaml')
        elif k == 'universe' and v not in universes:
            err(f'{rel(f)}: @universe:{v} has no constitution')
        elif k == 'phase' and not v.isdigit():
            err(f'{rel(f)}: @phase:{v} must be a number')
    for child in feat.get('children', []):
        block = child.get('background') or child.get('scenario')
        if not block:
            continue
        if child.get('scenario'):
            n_scen += 1
        for st in block.get('steps', []):
            text = st['text']
            hits = [i for i, rx in vocab_re if rx.match(text)]
            if not hits:
                err(f'{rel(f)}:{st["location"]["line"]}: step not in vocabulary: "{text}"')
            used_ids.update(hits)
            for code in re.findall(r'error "([A-Z][A-Z0-9_]+)"', text):
                if code not in error_codes:
                    err(f'{rel(f)}:{st["location"]["line"]}: error code {code} is not in spec/registries/errors.yaml')
for sid in sorted({i for i, _ in vocab_re} - used_ids):
    err(f'steps.yaml: step {sid} is not used by any feature (remove it or add a scenario)')
counts['features'] = len(features)
counts['scenarios'] = n_scen

# ---------------------------------------------------------------- 6. SLOs and runbooks
slo_schema = json.load(open(os.path.join(ROOT, 'spec', 'slo', 'service-level.schema.json')))
slo_v = Draft202012Validator(slo_schema)
def anchors(md):
    out = set()
    for line in open(md, encoding='utf-8'):
        m = re.match(r'^#{1,6} (.+)$', line)
        if m:
            out.add(re.sub(r'[^a-z0-9 -]', '', m.group(1).lower()).strip().replace(' ', '-'))
    return out
slo_files = sorted(glob.glob(os.path.join(ROOT, 'spec', 'slo', '*.yaml')))
for f in slo_files:
    d = yaml.safe_load(open(f))
    for e in slo_v.iter_errors(d):
        err(f'{rel(f)}: {e.message}')
    if d.get('universe') not in universes:
        err(f'{rel(f)}: universe {d.get("universe")} has no constitution')
    slo_ids = {s['id'] for s in d.get('slos', [])}
    for a in d.get('alerts', []):
        if a.get('slo') not in slo_ids:
            err(f'{rel(f)}: alert {a.get("id")} references unknown SLO {a.get("slo")}')
        path, _, anchor = a.get('runbook', '').partition('#')
        full = os.path.join(ROOT, path)
        if not os.path.exists(full):
            err(f'{rel(f)}: runbook {path} does not exist')
        elif anchor not in anchors(full):
            err(f'{rel(f)}: runbook {path} has no section #{anchor}')
counts['slo-files'] = len(slo_files)

# ---------------------------------------------------------------- 7. Cedar policies and tests
import cedarpy
ENT = re.compile(r'^([A-Za-z_][A-Za-z0-9_:]*)::"([^"]*)"$')
def to_cedar(v):
    """Turn 'Type::"id"' strings into Cedar entity references, recursively."""
    if isinstance(v, str):
        m = ENT.match(v)
        return {'__entity': {'type': m.group(1), 'id': m.group(2)}} if m else v
    if isinstance(v, list):
        return [to_cedar(x) for x in v]
    if isinstance(v, dict):
        return {k: to_cedar(x) for k, x in v.items()}
    return v
cedar_files = sorted(glob.glob(os.path.join(ROOT, 'spec', 'policies', '*.cedar')))
for f in cedar_files:
    try:
        cedarpy.format_policies(open(f).read())
    except Exception as e:
        err(f'Cedar does not parse: {rel(f)}: {e}')
n_cases = 0
for f in sorted(glob.glob(os.path.join(ROOT, 'spec', 'policies', 'tests', '*.yaml'))):
    suite = yaml.safe_load(open(f))
    src = '\n'.join(open(os.path.join(ROOT, p)).read() for p in suite['policies']) + '\n' + suite.get('fixtures', '')
    entities = []
    for e in suite.get('entities', []):
        m = ENT.match(e['uid'])
        entities.append({'uid': {'__entity': {'type': m.group(1), 'id': m.group(2)}},
                         'attrs': to_cedar(e.get('attrs', {})),
                         'parents': [to_cedar(x)['__entity'] for x in e.get('parents', [])]})
    for c in suite['cases']:
        n_cases += 1
        ctx = json.loads(json.dumps(suite.get('defaultContext', {})))
        ctx.update(c.get('context', {}))
        r = cedarpy.is_authorized({'principal': c['principal'], 'action': c['action'], 'resource': c['resource'],
                                   'context': to_cedar(ctx)}, src, entities)
        got = 'Allow' if r.decision == cedarpy.Decision.Allow else 'Deny'
        if got != c['expect']:
            err(f'{rel(f)}: "{c["name"]}" expected {c["expect"]}, got {got} (errors: {r.diagnostics.errors[:1]})')
counts['policy-tests'] = n_cases

# ---------------------------------------------------------------- 8. Datalog rules
def parse_datalog(text):
    """Small parser for the Souffle subset used by spec/rules: .decl lines and rules with conjunction, negation (!),
    parenthesised disjunction (;), comparisons and string/number constants."""
    text = re.sub(r'//[^\n]*', '', text)
    decls, rules = {}, []
    for m in re.finditer(r'\.decl\s+([a-z_][a-z0-9_]*)\s*\(([^)]*)\)', text):
        args = [a for a in m.group(2).split(',') if a.strip()]
        decls[m.group(1)] = len(args)
    body_text = re.sub(r'\.decl[^\n]*', '', text)
    for stmt in [s.strip() for s in re.split(r'\.\s*(?:\n|$)', body_text) if s.strip()]:
        if ':-' not in stmt:
            raise ValueError(f'not a rule: {stmt[:60]}')
        head, body = stmt.split(':-', 1)
        rules.append((head.strip(), body.strip()))
    return decls, rules
ATOM = re.compile(r'(!?)\s*([a-z_][a-z0-9_]*)\s*\(([^()]*)\)')
def atoms(s):
    return [(neg == '!', name, [a.strip() for a in args.split(',')]) for neg, name, args in ATOM.findall(s)]
def variables(args):
    return {a for a in args if re.fullmatch(r'[a-z][a-z0-9_]*', a)}
dl_files = sorted(glob.glob(os.path.join(ROOT, 'spec', 'rules', '**', '*.dl'), recursive=True))
n_rules = 0
for f in dl_files:
    try:
        decls, rules = parse_datalog(open(f).read())
    except ValueError as e:
        err(f'{rel(f)}: {e}')
        continue
    edges = []   # (head, body_pred, negated)
    for head, body in rules:
        n_rules += 1
        h = atoms(head)
        if len(h) != 1:
            err(f'{rel(f)}: rule head must be one atom: {head}')
            continue
        _, hname, hargs = h[0]
        bound = set()
        for neg, name, args in [(False, hname, hargs)] + atoms(body):
            if name not in decls:
                err(f'{rel(f)}: predicate {name} is used but not declared')
            elif decls[name] != len(args):
                err(f'{rel(f)}: {name} has arity {decls[name]} but is used with {len(args)} arguments')
        for neg, name, args in atoms(body):
            if not neg:
                bound |= variables(args)
            edges.append((hname, name, neg))
        for v in variables(hargs) - bound:
            err(f'{rel(f)}: head variable {v} of {hname} is not bound by a positive body atom (unsafe rule)')
    # stratification: no cycle through a negated edge
    graph = {}
    for h, b, neg in edges:
        graph.setdefault(h, set()).add(b)
    def reaches(a, b, seen=None):
        seen = seen or set()
        if a == b:
            return True
        seen.add(a)
        return any(reaches(n, b, seen) for n in graph.get(a, ()) if n not in seen)
    for h, b, neg in edges:
        if neg and reaches(b, h):
            err(f'{rel(f)}: negation of {b} inside the recursion of {h} is not stratifiable')
counts['datalog-rules'] = n_rules

# ---------------------------------------------------------------- 9. decision defaults
MONEY = re.compile(r'^\{\s*(-?\d+(?:\.\d+)?)\s+([A-Z]{3})\s*\}$')
CMP = re.compile(r'^(>=|<=|>|<|=)\s*(.+)$')
def cell_matches(cell, value):
    """Cell grammar of UCOS decision tables: '*', exact text, path glob 'a/*', and comparisons
    (>=, >, <=, <, =) against a number or a Money literal '{12.00 INR}' (currencies must match)."""
    cell = str(cell).strip()
    if cell == '*':
        return True
    m = CMP.match(cell)
    if m:
        op, rhs = m.groups()
        a_m, b_m = MONEY.match(value.strip()), MONEY.match(rhs.strip())
        if b_m:
            if not a_m or a_m.group(2) != b_m.group(2):
                return False
            a, b = float(a_m.group(1)), float(b_m.group(1))
        else:
            try:
                a, b = float(value), float(rhs)
            except ValueError:
                return False
        return {'>=': a >= b, '>': a > b, '<=': a <= b, '<': a < b, '=': a == b}[op]
    if cell.endswith('/*'):
        return value == cell[:-2] or value.startswith(cell[:-1])
    return cell == value
def evaluate_decision(dt, inputs):
    if dt.get('hitPolicy', 'FIRST') != 'FIRST':
        raise ValueError('only hitPolicy FIRST is supported by the reference evaluator')
    n = len(dt['inputs'])
    for row in dt['rules']:
        if all(cell_matches(c, v) for c, v in zip(row[:n], inputs)):
            return [str(x) for x in row[n:]]
    return None
n_dec_tests = 0
decision_files = {os.path.basename(p)[:-5] for p in glob.glob(os.path.join(ROOT, 'spec', 'decisions', '*.yaml'))}
for f in sorted(glob.glob(os.path.join(ROOT, 'spec', 'capabilities', 'packs', '*.yaml'))):
    m = yaml.safe_load(open(f))
    if m['metadata'].get('maturity') == 'experimental':
        continue
    for d in m['spec'].get('provides', {}).get('decisions', []) or []:
        if d not in decision_files:
            err(f'{m["metadata"]["id"]}: decision {d} has no default table spec/decisions/{d}.yaml')
for f in sorted(glob.glob(os.path.join(ROOT, 'spec', 'decisions', '*.yaml'))):
    dt = yaml.safe_load(open(f))
    width = len(dt.get('inputs', [])) + len(dt.get('outputs', []))
    for i, row in enumerate(dt.get('rules', [])):
        if len(row) != width:
            err(f'{rel(f)}: rule {i + 1} has {len(row)} cells, expected {width} (inputs + outputs)')
    if os.path.basename(f)[:-5] != dt.get('id'):
        err(f'{rel(f)}: id {dt.get("id")} does not match the file name')
    n_in = len(dt.get('inputs', []))
    for tc in dt.get('tests', []):
        got = evaluate_decision(dt, [str(x) for x in tc['input']])
        want = [str(x) for x in tc['expect']]
        n_dec_tests += 1
        if got != want:
            err(f'{rel(f)}: test input {tc["input"]} expected {want}, got {got}')
counts['decision-tables'] = len(decision_files)
counts['decision-tests'] = n_dec_tests

# ---------------------------------------------------------------- 10. genesis record
g_schema = json.load(open(os.path.join(ROOT, 'spec', 'genesis', 'genesis-record.schema.json')))
for f in sorted(glob.glob(os.path.join(ROOT, 'spec', 'genesis', '*.json'))):
    if f.endswith('.schema.json'):
        continue
    for e in Draft202012Validator(g_schema).iter_errors(json.load(open(f))):
        err(f'{rel(f)}: {e.message}')

# ---------------------------------------------------------------- 11. workflow definitions
wf_v = Draft202012Validator(json.load(open(os.path.join(ROOT, 'spec', 'workflows', 'workflow-definition.schema.json'))))
object_types = {os.path.basename(p)[:-len('.schema.json')] for p in glob.glob(os.path.join(ROOT, 'spec', 'object-types', '*.schema.json'))}
n_wf = 0
for f in sorted(glob.glob(os.path.join(ROOT, 'spec', 'workflows', '*.yaml'))):
    n_wf += 1
    wf = yaml.safe_load(open(f))
    def bool_keys(o, path=''):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(k, bool):
                    err(f'{rel(f)}: key at {path or "/"} parsed as boolean {k}: quote it (YAML 1.1 reads on/off/yes/no as booleans)')
                bool_keys(v, f'{path}/{k}')
        elif isinstance(o, list):
            for i, v in enumerate(o):
                bool_keys(v, f'{path}/{i}')
    bool_keys(wf)
    for e in wf_v.iter_errors(wf):
        err(f'{rel(f)}: {e.message}')
    states = wf.get('states', {})
    if wf.get('object') not in object_types:
        err(f'{rel(f)}: object {wf.get("object")} is not a registered object type')
    targets = {}
    for name, st in states.items():
        nxt = list((st.get('on') or {}).values()) + [t.get('then') for t in (st.get('timers') or {}).values()]
        if st.get('then'):
            nxt.append(st['then'])
        for n in nxt:
            if n not in states:
                err(f'{rel(f)}: state {name} goes to unknown state {n}')
        targets[name] = [n for n in nxt if n in states]
        if st.get('final') and (st.get('on') or st.get('timers') or st.get('then')):
            err(f'{rel(f)}: final state {name} has outgoing transitions')
        if not st.get('final') and not nxt:
            err(f'{rel(f)}: state {name} is a dead end (no transitions and not final)')
        for tm in (st.get('timers') or {}).values():
            if 'decision' in tm and tm['decision'] not in decision_files:
                err(f'{rel(f)}: timer uses unknown decision {tm["decision"]}')
            if 'decision' not in tm and 'duration' not in tm:
                err(f'{rel(f)}: timer in {name} needs a duration or a decision')
    seen, stack = set(), [wf.get('initial')]
    while stack:
        s_ = stack.pop()
        if s_ in seen or s_ not in states:
            continue
        seen.add(s_); stack.extend(targets.get(s_, []))
    for s_ in sorted(set(states) - seen):
        err(f'{rel(f)}: state {s_} is unreachable from {wf.get("initial")}')
    if not any(st.get('final') for st in states.values()):
        err(f'{rel(f)}: no final state')
    for g in (wf.get('guards') or {}):
        if not any(g in (st.get('on') or {}) for st in states.values()):
            err(f'{rel(f)}: guard {g} is not an event of any state')
counts['workflows'] = n_wf

# ---------------------------------------------------------------- 12. spike kits
cel = yaml.safe_load(open(os.path.join(ROOT, 'tools', 'spikes', 'cel-vectors.yaml')))
ids = [v.get('id') for v in cel['vectors']]
for v in cel['vectors']:
    if not v.get('expr') or (('expect' in v) == ('error' in v)):
        err(f'tools/spikes/cel-vectors.yaml: vector {v.get("id")} needs expr and exactly one of expect or error')
if len(ids) != len(set(ids)):
    err('tools/spikes/cel-vectors.yaml: duplicate vector ids')
counts['cel-vectors'] = len(ids)

# ---------------------------------------------------------------- 13. seed data
import datetime
seed = os.path.join(ROOT, 'spec', 'seed')
def load(p): return yaml.safe_load(open(os.path.join(seed, p)))
for f in sorted(glob.glob(os.path.join(seed, 'refdata', '*.yaml'))):
    d = yaml.safe_load(open(f))
    lic = d.get('licence') or {}
    if d.get('bundled') and lic.get('redistribution') != 'allowed':
        err(f'{rel(f)}: bundled code list without a licence that allows redistribution (ADR-027)')
    if d.get('count') != len(d.get('entries', [])):
        err(f'{rel(f)}: count {d.get("count")} does not match {len(d.get("entries", []))} entries')
    key = next(iter(d['entries'][0])) if d.get('entries') else None
    vals = [e[key] for e in d.get('entries', [])]
    if len(vals) != len(set(vals)):
        err(f'{rel(f)}: duplicate {key} values')
iso2 = {e['alpha2'] for e in load('refdata/iso3166-1.yaml')['entries']}
cur = {e['alpha3']: e['minorUnit'] for e in load('refdata/iso4217.yaml')['entries']}
zones = {e['zone'] for e in load('refdata/iana-tz.yaml')['entries']}
subs = {e['code'] for cc in ('IN', 'AE') for e in load(f'refdata/iso3166-2-{cc}.yaml')['entries']}
for j in load('geo/jurisdictions.yaml')['jurisdictions']:
    if j['id'].split(':')[-1] not in iso2: err(f'jurisdictions: {j["id"]} is not an ISO 3166-1 code')
    if j['currency'] not in cur: err(f'jurisdictions: unknown currency {j["currency"]}')
    for z in j['timezones']:
        if z not in zones: err(f'jurisdictions: unknown time zone {z}')
    for c in j['children']:
        if c['id'].split(':')[-1] not in subs: err(f'jurisdictions: {c["id"]} is not an ISO 3166-2 code')
for c in load('calendars/holidays-2026-2027.yaml')['calendars']:
    for h in c['fixed']:
        try: datetime.date.fromisoformat(h['date'])
        except ValueError: err(f'holidays: invalid date {h["date"]} in {c["id"]}')
for b in load('calendars/holidays-2026-2027.yaml')['businessHours']:
    if b['timezone'] not in zones: err(f'business hours {b["id"]}: unknown time zone {b["timezone"]}')
for p_ in load('plans/platform-plans.yaml')['plans']:
    for c_, amt in p_['price']['platformFee'].items():
        if c_ not in cur: err(f'plans: {p_["id"]} price in unknown currency {c_}')
        elif not amt.startswith('from ') and len(amt.split('.')[-1]) != cur[c_]:
            err(f'plans: {p_["id"]} {c_} amount {amt} does not use {cur[c_]} decimals')
tmpl = {yaml.safe_load(open(f))['id'] for f in glob.glob(os.path.join(seed, 'industry-templates', '*.yaml'))}
for pdf in glob.glob(os.path.join(ROOT, 'spec', 'composition', 'golden', '*.pd.yaml')):
    t_ = yaml.safe_load(open(pdf))['spec'].get('template', '').split('@')[0]
    if t_ and t_ not in tmpl: err(f'{rel(pdf)}: template {t_} has no seed in spec/seed/industry-templates/')
PH = re.compile(r'\{([a-zA-Z]+)\}')
for m in load('l10n/messages-core.yaml')['messages']:
    want = set(PH.findall(m['values']['en']['text']))
    for loc, v in m['values'].items():
        if set(PH.findall(v['text'])) != want:
            err(f'messages: {m["key"]} [{loc}] placeholders {sorted(set(PH.findall(v["text"])))} differ from en {sorted(want)}')
    if m['category'] == 'legal' and not m.get('requiresHumanReview'):
        err(f'messages: legal key {m["key"]} must require human review (U15)')
for f in sorted(glob.glob(os.path.join(seed, 'tax', '*.yaml'))):
    d = yaml.safe_load(open(f))
    for c in d.get('categories', []):
        if c.get('status') not in ('proposed', 'verified'):
            err(f'{rel(f)}: category {c.get("id")} needs status proposed or verified')
for f in sorted(glob.glob(os.path.join(seed, 'documents', '*.yaml'))):
    d = yaml.safe_load(open(f))
    if not d.get('legalBasis') or not d.get('requiredFields'):
        err(f'{rel(f)}: document template needs legalBasis and requiredFields')
counts['seed-files'] = len(glob.glob(os.path.join(seed, '**', '*.yaml'), recursive=True))

# ---------------------------------------------------------------- 14. error codes used by code are registered
CODE_LIT = re.compile(r'(?:NewProblem|problem)\([^,]+,\s*"([A-Z][A-Z0-9_]+)"')
for f in sorted(glob.glob(os.path.join(ROOT, 'kernel', '**', '*.go'), recursive=True)):
    if f.endswith('_test.go') or '/gen/' in f:
        continue
    for code in CODE_LIT.findall(open(f).read()):
        if code not in error_codes:
            err(f'{rel(f)}: error code {code} is not in spec/registries/errors.yaml (name it in the owning spec)')

# ---------------------------------------------------------------- report
print('  '.join(f'{k}: {v}' for k, v in counts.items()))
print(f'errors: {len(errors)}')
for e in errors:
    print('  ERROR  ', e)
sys.exit(1 if errors else 0)
