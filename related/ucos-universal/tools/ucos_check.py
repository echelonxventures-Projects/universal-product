#!/usr/bin/env python3
"""ucos_check — reference consistency checker for the UCOS spec repository.

Not the production composer (see engineering/KERNEL-DESIGN.md §9). It implements the generic rules of
spec/rules/core/closure.dl over the facts in spec/ to prove the machine-readable spec is consistent:

  1. JSON Schema validity of all schemas, manifests and platform definitions
  2. Registry integrity: unique ids, sole ownership of object types/events (L4), resolvable requires/implements,
     consumed events have producers, controls exist, universes exist, phase ordering, temporal dependency (ARCH-TMP-05),
     agreement with TEMPORAL-BINDING-MATRIX.md, every referenced certification gate defined (gates.yaml),
     generated registries (errors.yaml, object-types/) in sync with the specs
  3. Reference composition of every golden PlatformDefinition → deterministic blueprint + gap report

Exit code 0 = no errors and no MANDATORY gaps; 1 otherwise.
Usage: python3 tools/ucos_check.py [--write]   (--write stores blueprints/gap reports under spec/composition/golden/expected/)
"""
import glob, hashlib, json, os, re, sys
import yaml
from jsonschema import Draft202012Validator

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = os.path.join(ROOT, 'spec')
errors, warnings = [], []

def err(msg): errors.append(msg)
def warn(msg): warnings.append(msg)
def load_yaml(p):
    with open(p) as f: return yaml.safe_load(f)

# ---------------------------------------------------------------- 1. schemas
schemas = {}
for p in sorted(glob.glob(os.path.join(SPEC, '**', '*.schema.json'), recursive=True)):
    s = json.load(open(p))
    try:
        Draft202012Validator.check_schema(s)
    except Exception as e:
        err(f'schema invalid: {os.path.relpath(p, ROOT)}: {e}')
    schemas[os.path.basename(p)] = s
cap_v = Draft202012Validator(schemas['capability-manifest.schema.json'])
pd_v = Draft202012Validator(schemas['platform-definition.schema.json'])

# ---------------------------------------------------------------- 2. registry
packs = {}
for p in sorted(glob.glob(os.path.join(SPEC, 'capabilities', 'packs', '*.yaml'))):
    m = load_yaml(p)
    for e in cap_v.iter_errors(m):
        err(f'manifest schema: {os.path.basename(p)}: {e.message} at {list(e.path)}')
    cid = m['metadata']['id']
    if cid in packs: err(f'duplicate capability id {cid}')
    if os.path.basename(p) != cid + '.yaml': err(f'file name must equal id: {os.path.basename(p)}')
    packs[cid] = m

facts_reg = load_yaml(os.path.join(SPEC, 'rules', 'facts', 'regulations.yaml'))['regulations']
facts_ctl = load_yaml(os.path.join(SPEC, 'rules', 'facts', 'controls.yaml'))['controls']
defaults = load_yaml(os.path.join(SPEC, 'rules', 'facts', 'defaults.yaml'))

universe_dirs = {os.path.basename(d) for d in glob.glob(os.path.join(ROOT, 'constitutions', 'U*'))}
def spec_of(m): return m['spec']
def kind(c): return packs[c]['metadata']['capabilityKind']
def phase(c): return packs[c]['metadata']['phase']
def scope(c): return packs[c]['metadata']['scope']
def reqs(c): return [r['capability'] for r in spec_of(packs[c]).get('requires', [])]
def opts(c): return [r['capability'] for r in spec_of(packs[c]).get('optional', [])]
def impls(c): return spec_of(packs[c]).get('implements', [])
def prov(c, k): return spec_of(packs[c]).get('provides', {}).get(k, [])

owners = {}
for c in packs:
    u = packs[c]['metadata']['universe']
    if u not in universe_dirs: err(f'{c}: universe {u} has no constitution folder')
    for k in ('objectTypes', 'events'):
        for x in prov(c, k):
            if (k, x) in owners: err(f'ownership collision (L4): {k} {x} provided by {owners[(k, x)]} and {c}')
            owners[(k, x)] = c
    for d in reqs(c) + opts(c):
        if d not in packs: err(f'{c}: requires/optional unknown capability {d}')
        elif not opts(c).count(d) and phase(d) > phase(c):
            err(f'{c} (P{phase(c)}) requires {d} which is later (P{phase(d)})')
    for a in impls(c):
        if a not in packs: err(f'{c}: implements unknown abstract {a}')
        elif kind(a) != 'abstract': err(f'{c}: implements {a} which is not abstract')
    if kind(c) in ('adapter', 'simulator') and not impls(c): err(f'{c}: adapter/simulator without implements')
    for ctl in spec_of(packs[c]).get('compliance', {}).get('controls', []):
        if ctl not in facts_ctl: err(f'{c}: declares unknown control {ctl}')

event_producers = {x for (k, x) in owners if k == 'events'}
for c in packs:
    for e in spec_of(packs[c]).get('consumes', {}).get('events', []):
        if e not in event_producers: err(f'{c}: consumes {e} but no capability produces it')

for k, impl in facts_ctl.items():
    for c in impl:
        if c not in packs: err(f'control {k}: implementer {c} unknown')
for r in facts_reg:
    for k in r['controls']:
        if k not in facts_ctl: err(f'regulation {r["id"]}: control {k} not defined in controls.yaml')
    w = r['when']
    if 'capability' in w and w['capability'] not in packs: err(f'regulation {r["id"]}: when.capability {w["capability"]} unknown')

# requires-cycle detection (warning; deploy ordering must break cycles)
def closure(start):
    seen, stack = set(), list(start)
    while stack:
        x = stack.pop()
        if x in seen or x not in packs: continue
        seen.add(x); stack.extend(reqs(x))
    return seen
for c in packs:
    if c in closure(reqs(c)): warn(f'requires-cycle through {c}')

# temporal dependency rule (U13 App. E.4) and matrix agreement
matrix_kind = {}
mpath = os.path.join(ROOT, 'constitutions', 'TEMPORAL-BINDING-MATRIX.md')
for line in open(mpath):
    mm = re.match(r'^\| (U\d+) [^|]*\|[^|]*\|[^|]*\| ([VES]) \|', line)
    if mm: matrix_kind[mm.group(1)] = mm.group(2)
for c in packs:
    tk = spec_of(packs[c]).get('temporal', {}).get('kind')
    if tk == 'S' and c != 'temporal.core' and 'temporal.core' not in closure(reqs(c)):
        err(f'{c}: temporal kind S but temporal.core not in its requires-closure (ARCH-TMP-05)')
    uid = packs[c]['metadata']['universe'].split('-')[0]
    if tk == 'S' and matrix_kind.get(uid) in ('V', 'E'):
        err(f'{c}: temporal kind S but TEMPORAL-BINDING-MATRIX says {uid} is {matrix_kind[uid]}')
for uid, k in matrix_kind.items():
    ks = {spec_of(packs[c]).get('temporal', {}).get('kind') for c in packs if packs[c]['metadata']['universe'].startswith(uid + '-')}
    if k == 'S' and ks and 'S' not in ks:
        warn(f'{uid}: matrix says S but no pack of this universe declares temporal kind S')

# certification gates (spec/certification/gates.yaml): every referenced gate id and wildcard family is defined
gcat = load_yaml(os.path.join(SPEC, 'certification', 'gates.yaml'))
gate_ids = [g['id'] for g in gcat['gates']]
for d in {x for x in gate_ids if gate_ids.count(x) > 1}:
    err(f'gate catalogue: duplicate gate id {d}')
families = set(gcat['families'])
GATE_RE = re.compile(r'(?<![A-Za-z0-9-])((?:' + '|'.join(sorted(families)) + r')-(?:[A-Z0-9]+-)*\d{2,3})(?![A-Za-z0-9])')
refs = {}
for path in glob.glob(os.path.join(ROOT, '**', '*.md'), recursive=True) + glob.glob(os.path.join(SPEC, '**', '*.yaml'), recursive=True):
    if '/node_modules/' in path or path.endswith('gates.yaml'):
        continue
    for gid in GATE_RE.findall(open(path, encoding='utf-8').read()):
        refs.setdefault(gid, os.path.relpath(path, ROOT))
for gid, where in sorted(refs.items()):
    if gid not in gate_ids:
        err(f'gate {gid} referenced in {where} is not defined in spec/certification/gates.yaml')
for c in packs:
    for g in spec_of(packs[c]).get('certification', {}).get('gates', []):
        fam = g.split('-')[0]
        if (g.endswith('-*') and fam not in families) or (not g.endswith('-*') and g not in gate_ids):
            err(f'{c}: certification gate {g} not in the gate catalogue')
for prof, gs in gcat.get('profiles', {}).items():
    for g in gs:
        if (g.endswith('-*') and g[:-2] not in families) or (not g.endswith('-*') and g not in gate_ids):
            err(f'gate profile {prof}: unknown gate {g}')

# threat models referenced by manifests exist (automatable part of SEC-TM-001)
for c in packs:
    tm = spec_of(packs[c]).get('security', {}).get('threatModel')
    if tm and not os.path.exists(os.path.join(ROOT, tm)):
        err(f'{c}: threat model {tm} does not exist (SEC-TM-001)')

# generated registries (errors.yaml, object-types/) must match the specs and manifests
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import gen_registries
bad, extra = gen_registries.stale(gen_registries.render())
for p_ in bad + extra:
    err(f'registry out of date: {p_} (run python3 tools/gen_registries.py)')

# ---------------------------------------------------------------- 3. composition
def adapters_for(abs_, jur, method, reality='physical'):
    cands = []
    for a in packs:
        if abs_ not in impls(a): continue
        sel = spec_of(packs[a]).get('selection', {})
        js, ms = sel.get('jurisdictions', ['*']), sel.get('methods')
        if reality not in sel.get('realities', ['physical']): continue   # simulators serve simulated realities only
        if jur not in js and '*' not in js: continue
        if method != '-' and ms is not None and method not in ms and '*' not in ms: continue
        specificity = 0 if jur in js else 1
        cands.append((specificity, a))
    return [a for _, a in sorted(cands)]

def compose(pd, target_phase=1):
    s = pd['spec']
    jurs = [f'ucos:jur:{c}' for c in s['geography']['countries']]
    countries = s['geography']['countries']
    channels = s.get('channels', [])
    excluded = set(s.get('capabilities', {}).get('exclude', []))
    reality = s.get('reality', 'physical')
    trace = {}
    def add(c, why):
        if c not in trace: trace[c] = why
    for c in defaults['baseCapabilities']:
        if c not in packs or phase(c) <= target_phase: add(c, 'base-capability')   # base set grows with phases (A-74)
    for c in s.get('capabilities', {}).get('include', []): add(c, 'requested')
    msg_methods = set(defaults['alwaysMessagingMethods'])
    rtc_methods = set()
    for ch in channels:
        cd = defaults['channels'].get(ch)
        if not cd: continue
        for c in cd['capabilities']: add(c, f'channel:{ch}')
        msg_methods |= set(cd['messagingMethods'])
        rtc_methods |= set(cd.get('rtcMethods', []))
    currencies = {s['geography'].get('primaryCurrency', {}).get(c, defaults['countryCurrency'].get(c)) for c in countries}
    if len(currencies) > 1: add('fx.provider', 'multi-currency')
    pay_methods = {c: s.get('paymentMethods', {}).get(c, defaults['defaultPaymentMethods'].get(c, [])) for c in countries}

    gaps, selected, controls = [], {}, {}
    for _ in range(20):  # fixpoint
        before = set(trace)
        for c in list(trace):
            if c in packs:
                for d in reqs(c): add(d, f'required-by:{c}')
        for r in facts_reg:
            if reality != 'physical': break                      # regulations protect real people (P-004)
            if r['jurisdiction'] != '*' and r['jurisdiction'] not in jurs: continue
            w = r['when']
            ok = (w.get('always') or (w.get('capability') in trace) or (w.get('businessModel') in s.get('businessModel', []))
                  or (w.get('channel') in channels or (w.get('channel') == 'sms' and 'sms' in msg_methods))
                  or (w.get('framework') in s.get('compliance', {}).get('frameworks', [])))
            if ok:
                for k in r['controls']:
                    controls.setdefault(k, set()).add(r['id'])
                    for c in facts_ctl[k]: add(c, f'control:{k}<-{r["id"]}')
        for c in [c for c in list(trace) if c in packs and kind(c) in ('adapter', 'simulator')]:
            for a in impls(c): add(a, f'abstract-of:{c}')
        for abs_ in [c for c in list(trace) if c in packs and kind(c) == 'abstract']:
            src = defaults['abstractMethodSource'].get(abs_, 'none')
            for i, j in enumerate(jurs):
                cc = countries[i]
                methods = (pay_methods.get(cc, []) if src == 'paymentMethods' else sorted(msg_methods) if src == 'messagingMethods' else sorted(rtc_methods) if src == 'rtcMethods' else ['-'])
                for mth in methods:
                    cands = adapters_for(abs_, j, mth, reality)
                    if cands:
                        selected[(abs_, j, mth)] = cands[0]
                        add(cands[0], f'adapter:{abs_}[{j},{mth}]')
        if set(trace) == before: break

    required = set(trace)
    for c in sorted(required):   # each condition is its own gap, as in spec/rules/core/closure.dl
        if c not in packs: gaps.append(('MANDATORY', 'MISSING_CAPABILITY', c, trace[c])); continue
        if c in excluded: gaps.append(('MANDATORY', 'CONFLICT_EXCLUDED', c, trace[c]))
        if phase(c) > target_phase: gaps.append(('MANDATORY', 'PHASE_NOT_AVAILABLE', c, f'P{phase(c)} > target P{target_phase}'))
    for abs_ in [c for c in required if c in packs and kind(c) == 'abstract']:
        src = defaults['abstractMethodSource'].get(abs_, 'none')
        for i, j in enumerate(jurs):
            methods = (pay_methods.get(countries[i], []) if src == 'paymentMethods' else sorted(msg_methods) if src == 'messagingMethods' else sorted(rtc_methods) if src == 'rtcMethods' else ['-'])
            for mth in methods:
                if (abs_, j, mth) not in selected:
                    gaps.append(('MANDATORY', 'MISSING_ADAPTER', abs_, f'{j} method={mth}'))
        if abs_ in defaults['ioAbstracts'] and not any(abs_ in impls(x) and kind(x) == 'simulator' for x in packs):
            gaps.append(('RECOMMENDED', 'MISSING_SIMULATOR', abs_, 'INT-L5/CTX-L4: needed for simulation and tests'))
    produced = {e for c in required if c in packs for e in prov(c, 'events')}
    for c in sorted(required):
        if c not in packs: continue
        for e in spec_of(packs[c]).get('consumes', {}).get('events', []):
            if e not in produced:
                gaps.append(('RECOMMENDED', 'EVENT_WITHOUT_PRODUCER_IN_BLUEPRINT', c, e))
    for k, regs in controls.items():
        missing = [c for c in facts_ctl[k] if c not in required]
        if missing: gaps.append(('MANDATORY', 'CONTROL_NOT_IMPLEMENTED', k, ','.join(missing)))

    bp = {
        'kind': 'Blueprint',
        'platformDefinition': f"{pd['metadata']['id']}@{pd['metadata']['version']}",
        'targetPhase': target_phase,
        **({'reality': reality} if reality != 'physical' else {}),
        'capabilities': [{'id': c, 'version': packs[c]['metadata']['version'], 'scope': scope(c)}
                         for c in sorted(required) if c in packs],
        'adapters': [{'abstract': a, 'jurisdiction': j, 'method': m, 'implementation': i} for (a, j, m), i in sorted(selected.items())],
        'controls': [{'control': k, 'regulations': sorted(v), 'implementedBy': facts_ctl[k]} for k, v in sorted(controls.items())],
        'objectTypes': sorted(x for c in required if c in packs for x in prov(c, 'objectTypes')),
        'events': sorted(produced),
    }
    canon = json.dumps(bp, sort_keys=True, separators=(',', ':')).encode()
    bp['id'] = 'ucos:blueprint:sha256:' + hashlib.sha256(canon).hexdigest()
    # Provenance is a separate ResolutionTrace (A-76): the blueprint id depends only on what is composed.
    bp_trace = {'kind': 'ResolutionTrace', 'blueprint': bp['id'], 'why': {c: trace[c] for c in sorted(required)}}
    report = {'kind': 'GapReport', 'blueprintCandidate': bp['id'],
              'summary': {sev: sum(1 for g in gaps if g[0] == sev) for sev in ('MANDATORY', 'RECOMMENDED', 'OPTIONAL')},
              'gaps': [{'severity': a, 'kind': b, 'subject': c, 'because': d} for a, b, c, d in sorted(gaps)]}
    return bp, report, bp_trace

results = []
for p in sorted(glob.glob(os.path.join(SPEC, 'composition', 'golden', '*.pd.yaml'))):
    pd = load_yaml(p)
    for e in pd_v.iter_errors(pd): err(f'PD schema: {os.path.basename(p)}: {e.message}')
    tp = pd['spec'].get('targetPhase', 1)
    bp1, gr1, tr1 = compose(pd, tp)
    bp2, _, _ = compose(pd, tp)
    if bp1['id'] != bp2['id']: err(f'{os.path.basename(p)}: composition not deterministic (L18)')
    results.append((os.path.basename(p), bp1, gr1))
    out = os.path.join(SPEC, 'composition', 'golden', 'expected')
    base = os.path.basename(p).replace('.pd.yaml', '')
    files = {base + '.blueprint.json': bp1, base + '.gaps.json': gr1, base + '.trace.json': tr1}
    if '--write' in sys.argv:
        os.makedirs(out, exist_ok=True)
        for name, doc in files.items():
            with open(os.path.join(out, name), 'w') as fh:
                json.dump(doc, fh, indent=2, sort_keys=True); fh.write('\n')
    else:   # golden regression: results may change only by a deliberate --write
        for name, doc in files.items():
            path = os.path.join(out, name)
            want = json.load(open(path)) if os.path.exists(path) else None
            if want != doc:
                err(f'golden {name} differs from the composed result (review, then run tools/ucos_check.py --write)')

# ---------------------------------------------------------------- report
print(f'packs: {len(packs)}  gates: {len(gate_ids)} ({len(refs)} referenced)  object types: {sum(1 for k in owners if k[0]=="objectTypes")}  events: {len(event_producers)}  controls: {len(facts_ctl)}  regulations: {len(facts_reg)}')
for name, bp, gr in results:
    tenant_caps = sum(1 for c in bp['capabilities'] if c['scope'] == 'tenant')
    print(f'\n== {name} → {bp["id"][:40]}…')
    print(f'   capabilities: {len(bp["capabilities"])} ({tenant_caps} tenant, {len(bp["capabilities"])-tenant_caps} platform)  adapters: {len(bp["adapters"])}  controls: {len(bp["controls"])}  object types: {len(bp["objectTypes"])}')
    for a in bp['adapters']:
        print(f'   adapter  {a["abstract"]:<20} {a["jurisdiction"]:<12} {a["method"]:<10} → {a["implementation"]}')
    print(f'   gaps: {gr["summary"]}')
    for g in gr['gaps']:
        print(f'   [{g["severity"]}] {g["kind"]}: {g["subject"]} ({g["because"]})')
print(f'\nerrors: {len(errors)}  warnings: {len(warnings)}')
for e in errors: print('  ERROR  ', e)
for w in warnings: print('  WARN   ', w)
mand = sum(gr['summary']['MANDATORY'] for _, _, gr in results)
sys.exit(1 if errors or mand else 0)
