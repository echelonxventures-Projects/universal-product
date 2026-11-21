#!/usr/bin/env python3
"""datalog — reference evaluator for spec/rules/**/*.dl, fact export for spike S-01, and the oracle cross-check.

The composer engine (ADR-022) must evaluate spec/rules/core/closure.dl. This module:
  * parses the Souffle subset the rules use (conjunction, negation, parenthesised disjunction, = and comparisons,
    string and number constants, the wildcard _);
  * evaluates it bottom-up by strata (naive fixpoint; small inputs only);
  * encodes a PlatformDefinition plus the registry (manifests, facts, defaults) as EDB facts;
  * exports those facts as Souffle .facts files (tab-separated) for candidate engines;
  * cross-checks the rules against the checked-in golden blueprints produced by tools/ucos_check.py.

The oracle composes every golden platform from the rules alone (with the choice() loop for adapters) and requires
the same blueprint, byte for byte (same id), and the same gaps as tools/ucos_check.py.

Usage:
  python3 tools/datalog.py oracle                       # exit 1 if rules and golden blueprints disagree
  python3 tools/datalog.py export <pd.yaml> <outdir>    # write .facts files for an engine spike
  python3 tools/datalog.py synth <n-caps> <outdir>      # deterministic synthetic registry (S-01: 125000 -> ~1M facts)
"""
import glob, json, os, re, sys
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ------------------------------------------------------------------ parsing
def split_top(s, sep):
    out, depth, cur, q = [], 0, '', False
    for ch in s:
        if ch == '"':
            q = not q
        if not q:
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
        if ch == sep and depth == 0 and not q:
            out.append(cur.strip()); cur = ''
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out

TERM = r'(?:"[^"]*"|-?\d+|[A-Za-z_][A-Za-z0-9_]*)'
def parse_term(t):
    t = t.strip()
    if t.startswith('"'):
        return ('const', t[1:-1])
    if re.fullmatch(r'-?\d+', t):
        return ('const', int(t))
    if t == '_':
        return ('any', None)
    return ('var', t)

def parse_literal(s):
    s = s.strip()
    if s.startswith('(') and s.endswith(')') and len(split_top(s[1:-1], ';')) > 1:
        return ('or', [parse_literal(x) for x in split_top(s[1:-1], ';')])
    m = re.fullmatch(rf'({TERM})\s*(<=|>=|!=|=|<|>)\s*({TERM})', s)
    if m:
        return ('cmp', m.group(2), parse_term(m.group(1)), parse_term(m.group(3)))
    neg = s.startswith('!')
    m = re.fullmatch(r'!?\s*([a-z_][a-z0-9_]*)\s*\((.*)\)', s, re.S)
    if not m:
        raise ValueError(f'cannot parse literal: {s}')
    return ('neg' if neg else 'pos', m.group(1), [parse_term(a) for a in split_top(m.group(2), ',')])

def parse_program(text):
    text = re.sub(r'//[^\n]*', '', text)
    decls = {}
    for m in re.finditer(r'\.decl\s+([a-z_][a-z0-9_]*)\s*\(([^)]*)\)', text):
        decls[m.group(1)] = len([a for a in m.group(2).split(',') if a.strip()])
    body = re.sub(r'\.decl[^\n]*', '', text)
    rules = []
    for stmt in [s.strip() for s in re.split(r'\.\s*(?:\n|$)', body) if s.strip()]:
        head, rhs = stmt.split(':-', 1)
        rules.append((parse_literal(head), [parse_literal(x) for x in split_top(rhs, ',')]))
    return decls, rules

# ------------------------------------------------------------------ evaluation
def term_value(t, env):
    kind, v = t
    if kind == 'const':
        return v
    if kind == 'var':
        return env.get(v, KeyError)
    return None

def literal_vars(lit):
    if lit[0] in ('pos', 'neg'):
        return {v for k, v in lit[2] if k == 'var'}
    if lit[0] == 'cmp':
        return {v for k, v in (lit[2], lit[3]) if k == 'var'}
    return set().union(*[literal_vars(x) for x in lit[1]])

def match_atom(args, row, env):
    env = dict(env)
    for (kind, v), val in zip(args, row):
        if kind == 'const' and v != val:
            return None
        if kind == 'var':
            if v in env and env[v] != val:
                return None
            env[v] = val
    return env

def compare(op, a, b):
    try:
        return {'=': a == b, '!=': a != b, '<': a < b, '<=': a <= b, '>': a > b, '>=': a >= b}[op]
    except TypeError:
        return False

def solve(body, env, db):
    if not body:
        yield env
        return
    # evaluate the first literal whose variables are bound enough; positive atoms bind, others must wait
    for i, lit in enumerate(body):
        ready = lit[0] == 'pos' or literal_vars(lit) <= set(env) or lit[0] == 'or'
        if ready:
            break
    rest = body[:i] + body[i + 1:]
    if lit[0] == 'pos':
        for row in db.get(lit[1], ()):
            e = match_atom(lit[2], row, env)
            if e is not None:
                yield from solve(rest, e, db)
    elif lit[0] == 'neg':
        if not any(match_atom(lit[2], row, env) is not None for row in db.get(lit[1], ())):
            yield from solve(rest, env, db)
    elif lit[0] == 'cmp':
        a, b = term_value(lit[2], env), term_value(lit[3], env)
        if compare(lit[1], a, b):
            yield from solve(rest, env, db)
    else:  # disjunction: each branch may bind
        seen = set()
        for alt in lit[1]:
            for e in solve([alt], env, db):
                key = tuple(sorted(e.items(), key=lambda kv: kv[0]))
                if key not in seen:
                    seen.add(key)
                    yield from solve(rest, e, db)

def strata(rules):
    preds = {h[1] for h, _ in rules}
    level = {p: 0 for p in preds}
    for _ in range(len(preds) + 1):
        changed = False
        for h, body in rules:
            for lit in body:
                for sub in (lit[1] if lit[0] == 'or' else [lit]):
                    if sub[0] in ('pos', 'neg') and sub[1] in level:
                        need = level[sub[1]] + (1 if sub[0] == 'neg' else 0)
                        if level[h[1]] < need:
                            level[h[1]] = need; changed = True
        if not changed:
            return level
    raise ValueError('rules are not stratifiable')

def evaluate(rules, edb):
    db = {k: set(v) for k, v in edb.items()}
    level = strata(rules)
    for s in sorted(set(level.values())):
        layer = [r for r in rules if level[r[0][1]] == s]
        while True:
            added = 0
            for head, body in layer:
                for env in list(solve(body, {}, db)):
                    row = tuple(term_value(t, env) for t in head[2])
                    if row not in db.setdefault(head[1], set()):
                        db[head[1]].add(row); added += 1
            if not added:
                break
    return db

# ------------------------------------------------------------------ EDB encoding
def load_registry():
    packs = {}
    for f in glob.glob(os.path.join(ROOT, 'spec', 'capabilities', 'packs', '*.yaml')):
        m = yaml.safe_load(open(f))
        packs[m['metadata']['id']] = m
    facts = os.path.join(ROOT, 'spec', 'rules', 'facts')
    return (packs, yaml.safe_load(open(os.path.join(facts, 'regulations.yaml')))['regulations'],
            yaml.safe_load(open(os.path.join(facts, 'controls.yaml')))['controls'],
            yaml.safe_load(open(os.path.join(facts, 'defaults.yaml'))))

def encode(pd, packs, regs, ctls, defaults):
    s = pd['spec']
    E = {}
    def fact(p, *row): E.setdefault(p, set()).add(tuple(row))
    countries = s['geography']['countries']
    jurs = [f'ucos:jur:{c}' for c in countries]
    channels = s.get('channels', [])
    msg = set(defaults['alwaysMessagingMethods']); rtc = set()
    for c in s.get('capabilities', {}).get('include', []):
        fact('requested', c)
    for ch in channels:
        cd = defaults['channels'].get(ch)
        if cd:
            for c in cd['capabilities']:
                fact('requested', c)
            msg |= set(cd['messagingMethods']); rtc |= set(cd.get('rtcMethods', []))
    cur = {s['geography'].get('primaryCurrency', {}).get(c, defaults['countryCurrency'].get(c)) for c in countries}
    if len(cur) > 1:
        fact('requested', 'fx.provider')
    for c in defaults['baseCapabilities']:
        fact('base_capability', c)
    fact('target_phase', s.get('targetPhase', 1))
    fact('pd_reality', s.get('reality', 'physical'))
    for c in s.get('capabilities', {}).get('exclude', []):
        fact('excluded', c)
    for j in jurs:
        fact('in_scope', j)
    for m in s.get('businessModel', []):
        fact('pd_business_model', m)
    for ch in channels:
        fact('pd_channel', ch)
    if 'sms' in msg:
        fact('pd_channel', 'sms')
    for f in s.get('compliance', {}).get('frameworks', []):
        fact('pd_framework', f)
    for r in regs:
        fact('regulation', r['id'], r['jurisdiction'])
        w = r['when']
        if w.get('always'): fact('reg_when_always', r['id'])
        if 'capability' in w: fact('reg_when_capability', r['id'], w['capability'])
        if 'businessModel' in w: fact('reg_when_business_model', r['id'], w['businessModel'])
        if 'channel' in w: fact('reg_when_channel', r['id'], w['channel'])
        if 'framework' in w: fact('reg_when_framework', r['id'], w['framework'])
        for k in r['controls']:
            fact('requires_control', r['id'], k)
    for k, cs in ctls.items():
        for c in cs:
            fact('control_implemented_by', k, c)
    pay = {c: s.get('paymentMethods', {}).get(c, defaults['defaultPaymentMethods'].get(c, [])) for c in countries}
    for cid, m in packs.items():
        md, sp = m['metadata'], m['spec']
        fact('provider_capability', cid)
        fact('phase_of', cid, md['phase'])
        for r in sp.get('requires', []):
            fact('requires', cid, r['capability'])
        if md['capabilityKind'] == 'abstract':
            fact('abstract', cid)
            src = defaults['abstractMethodSource'].get(cid, 'none')
            for i, j in enumerate(jurs):
                ms = pay.get(countries[i], []) if src == 'paymentMethods' else sorted(msg) if src == 'messagingMethods' \
                    else sorted(rtc) if src == 'rtcMethods' else ['-']
                for mth in ms:
                    fact('needed_method', cid, j, mth)
        sel = sp.get('selection', {})
        for e in sp.get('provides', {}).get('events', []) or []:
            fact('provides_event', cid, e)
        for e in (sp.get('consumes') or {}).get('events', []) or []:
            fact('consumes_event', cid, e)
        if md['capabilityKind'] in ('adapter', 'simulator'):
            fact('adapter_kind', cid)
        for a in sp.get('implements', []):
            fact('implements', cid, a)
            if md['capabilityKind'] == 'simulator':
                fact('simulator_for', cid, a)
        if sp.get('implements'):
            for j in sel.get('jurisdictions', ['*']):
                fact('adapter_jur', cid, j)
            for mth in sel.get('methods', []) or []:
                fact('adapter_method', cid, mth)
            for x in sel.get('realities', ['physical']):
                fact('adapter_reality', cid, x)
    for a in defaults['ioAbstracts']:
        fact('io_abstract', a)
    return E

# ------------------------------------------------------------------ commands
def rules_text():
    return '\n'.join(open(p).read() for p in sorted(glob.glob(os.path.join(ROOT, 'spec', 'rules', '**', '*.dl'), recursive=True)))

SEVERITY = {'MISSING_CAPABILITY': 'MANDATORY', 'CONFLICT_EXCLUDED': 'MANDATORY', 'PHASE_NOT_AVAILABLE': 'MANDATORY',
            'MISSING_ADAPTER': 'MANDATORY', 'CONTROL_NOT_IMPLEMENTED': 'MANDATORY',
            'MISSING_SIMULATOR': 'RECOMMENDED', 'EVENT_WITHOUT_PRODUCER_IN_BLUEPRINT': 'RECOMMENDED'}

def choose(db, edb):
    """Engine choice() over selected_adapter: a jurisdiction-specific adapter beats '*', then the smallest id."""
    best = {}
    jur = edb.get('adapter_jur', set())
    for abs_, j, m, a in db.get('selected_adapter', set()):
        key = (0 if (a, j) in jur else 1, a)
        if (abs_, j, m) not in best or key < best[(abs_, j, m)]:
            best[(abs_, j, m)] = key
    return {(abs_, j, m, k[1]) for (abs_, j, m), k in best.items()}

def compose(pd, packs, regs, ctls, defaults, rules):
    """Evaluate the rules with the choice() loop and assemble the blueprint exactly as tools/ucos_check.py does."""
    import hashlib
    edb = encode(pd, packs, regs, ctls, defaults)
    chosen = set()
    for _ in range(50):
        edb['chosen_adapter'] = set(chosen)
        db = evaluate(rules, edb)
        nxt = choose(db, edb)
        if nxt == chosen:
            break
        chosen = nxt
    s = pd['spec']
    required = sorted(r[0] for r in db.get('required', set()) if r[0] in packs)
    applies = {r[0] for r in db.get('applies', set())}
    controls = {}
    for r_, k in edb.get('requires_control', set()):
        if r_ in applies:
            controls.setdefault(k, set()).add(r_)
    prov = lambda c, k: packs[c]['spec'].get('provides', {}).get(k, []) or []
    produced = sorted({e for c in required for e in prov(c, 'events')})
    reality = s.get('reality', 'physical')
    bp = {'kind': 'Blueprint', 'platformDefinition': f"{pd['metadata']['id']}@{pd['metadata']['version']}",
          'targetPhase': s.get('targetPhase', 1), **({'reality': reality} if reality != 'physical' else {}),
          'capabilities': [{'id': c, 'version': packs[c]['metadata']['version'], 'scope': packs[c]['metadata']['scope']} for c in required],
          'adapters': [{'abstract': a, 'jurisdiction': j, 'method': m, 'implementation': i} for a, j, m, i in sorted(chosen)],
          'controls': [{'control': k, 'regulations': sorted(v), 'implementedBy': ctls[k]} for k, v in sorted(controls.items())],
          'objectTypes': sorted(x for c in required for x in prov(c, 'objectTypes')),
          'events': produced}
    bp['id'] = 'ucos:blueprint:sha256:' + hashlib.sha256(json.dumps(bp, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    gaps = {(SEVERITY[k], k, a) for k, a, b in db.get('gap', set())}
    return bp, gaps

def oracle():
    decls, rules = parse_program(rules_text())
    packs, regs, ctls, defaults = load_registry()
    problems = []
    for pdf in sorted(glob.glob(os.path.join(ROOT, 'spec', 'composition', 'golden', '*.pd.yaml'))):
        name = os.path.basename(pdf).replace('.pd.yaml', '')
        pd = yaml.safe_load(open(pdf))
        edb = encode(pd, packs, regs, ctls, defaults)
        for p, rows in edb.items():
            if p not in decls:
                problems.append(f'{name}: encoder emits undeclared predicate {p}')
            elif any(len(r) != decls[p] for r in rows):
                problems.append(f'{name}: {p} facts do not have arity {decls[p]}')
        bp, gaps = compose(pd, packs, regs, ctls, defaults, rules)
        exp = json.load(open(os.path.join(ROOT, 'spec', 'composition', 'golden', 'expected', f'{name}.blueprint.json')))
        gr = json.load(open(os.path.join(ROOT, 'spec', 'composition', 'golden', 'expected', f'{name}.gaps.json')))
        exp_gaps = {(g['severity'], g['kind'], g['subject']) for g in gr['gaps']}
        same = bp == exp and gaps == exp_gaps
        if bp != exp:
            for k in sorted(set(bp) | set(exp)):
                if bp.get(k) != exp.get(k):
                    problems.append(f'{name}: blueprint field {k} differs between closure.dl and the checker')
        if gaps != exp_gaps:
            problems.append(f'{name}: gaps differ: rules-only {sorted(gaps - exp_gaps)}, checker-only {sorted(exp_gaps - gaps)}')
        print(f'  {name:<20} {bp["id"][22:38]}…  {"identical" if same else "DIFFER"}')
    for p in problems:
        print('  ERROR  ', p)
    return problems

def export(pd_path, outdir):
    packs, regs, ctls, defaults = load_registry()
    edb = encode(yaml.safe_load(open(pd_path)), packs, regs, ctls, defaults)
    os.makedirs(outdir, exist_ok=True)
    decls, _ = parse_program(rules_text())
    for p in decls:
        rows = sorted(edb.get(p, set()), key=lambda r: tuple(map(str, r)))
        with open(os.path.join(outdir, f'{p}.facts'), 'w') as f:
            for r in rows:
                f.write('\t'.join(map(str, r)) + '\n')
    print(f'wrote {sum(len(v) for v in edb.values())} facts for {len(decls)} predicates to {outdir}')

def synth(n_caps, outdir, seed=42):
    """Deterministic synthetic registry for engine performance tests (S-01: ~1M facts at n_caps=100000).
    Shapes follow the real registry: layered requires (no cycles), regulations on capabilities, controls, adapters."""
    import random
    rnd = random.Random(seed)
    E = {}
    def fact(p, *row): E.setdefault(p, []).append(row)
    caps = [f'cap{i}' for i in range(n_caps)]
    for i, c in enumerate(caps):
        fact('provider_capability', c); fact('phase_of', c, rnd.randint(0, 3))
        for _ in range(rnd.randint(1, 6)):
            if i > 10:
                fact('requires', c, caps[rnd.randrange(0, i)])           # only earlier caps: acyclic, layered
    for i in range(n_caps // 20):
        a = f'abs{i}'; fact('provider_capability', a); fact('phase_of', a, 0); fact('abstract', a); fact('io_abstract', a)
        for jx in range(3):
            fact('needed_method', a, f'ucos:jur:J{jx}', '-')
        for k in range(4):
            ad = f'adapter{i}_{k}'
            fact('provider_capability', ad); fact('phase_of', ad, 1); fact('adapter_kind', ad); fact('implements', ad, a)
            fact('adapter_jur', ad, f'ucos:jur:J{k % 3}' if k < 3 else '*'); fact('adapter_reality', ad, 'physical')
        sim = f'sim{i}'; fact('provider_capability', sim); fact('phase_of', sim, 0); fact('adapter_kind', sim)
        fact('implements', sim, a); fact('simulator_for', sim, a); fact('adapter_jur', sim, '*'); fact('adapter_reality', sim, 'simulated')
    for i in range(n_caps // 10):
        r = f'reg{i}'; fact('regulation', r, f'ucos:jur:J{i % 5}' if i % 7 else '*')
        fact('reg_when_capability', r, caps[rnd.randrange(n_caps)])
        for _ in range(2):
            k = f'ctl{rnd.randrange(n_caps // 5)}'
            fact('requires_control', r, k); fact('control_implemented_by', k, caps[rnd.randrange(n_caps)])
    for c in rnd.sample(caps, min(200, n_caps)):
        fact('requested', c)
    for j in range(3):
        fact('in_scope', f'ucos:jur:J{j}')
    fact('target_phase', 3); fact('pd_reality', 'physical')
    os.makedirs(outdir, exist_ok=True)
    decls, _ = parse_program(rules_text())
    for p in decls:
        with open(os.path.join(outdir, f'{p}.facts'), 'w') as f:
            for r in E.get(p, []):
                f.write('\t'.join(map(str, r)) + '\n')
    print(f'wrote {sum(len(v) for v in E.values())} synthetic facts to {outdir}')

if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == 'synth':
        synth(int(sys.argv[2]), sys.argv[3]); sys.exit(0)
    if len(sys.argv) >= 2 and sys.argv[1] == 'oracle':
        sys.exit(1 if oracle() else 0)
    if len(sys.argv) == 4 and sys.argv[1] == 'export':
        export(sys.argv[2], sys.argv[3]); sys.exit(0)
    print(__doc__); sys.exit(2)
