#!/usr/bin/env python3
"""gen_contracts — derive API and event contracts from capability manifests (U63 §3, U61).

Outputs (deterministic):
  spec/api/openapi/capabilities/<capability>.yaml   OpenAPI 3.1 per capability with commands or queries
  spec/events/payloads/<event-type>.schema.json     payload schema for every declared event
  spec/api/asyncapi/ucos-events.yaml                AsyncAPI 3.0 catalogue of topics, messages and producers

Hand-written sources that are never overwritten:
  spec/api/openapi/kernel/*.yaml                    kernel and control-plane APIs (API-L1 exception)
  spec/events/payloads/hand/<event>.schema.json     payloads for core events; copied over the generated skeleton

Path rule (U63 §3, master §15.2): command C on primary object T ->
  POST /v1/{slug}/{collection}            when C = <create-verb>T and no earlier command already creates T
  POST /v1/{slug}/{collection}/{id}:{verb}  otherwise (verb = C without T, lowerCamel)
Queries: Get<T> -> GET /{collection}/{id}; List<T>s or <T>s -> GET /{collection}; <T>s<Rest> -> GET /{collection}/{rest-kebab};
other -> GET /{slug}/{query-kebab}. A path that would still collide is emitted with '#<operationId>' and fails the checker.
Request bodies are untyped objects until per-command payload schemas exist; object schemas point to spec/object-types/.

Usage: python3 tools/gen_contracts.py [--check]
"""
import glob, json, os, re, sys
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKS = os.path.join(ROOT, 'spec', 'capabilities', 'packs')
OA_DIR = 'spec/api/openapi/capabilities'
PL_DIR = 'spec/events/payloads'
ASYNC = 'spec/api/asyncapi/ucos-events.yaml'
VT = 'https://schemas.ucos.io/meta/value-types.schema.json#/$defs/'
CREATE_VERBS = ('Create', 'Register', 'Define', 'Place', 'Open', 'Start', 'Capture', 'Apply', 'Submit', 'Issue', 'Add', 'Raise', 'Request', 'Schedule', 'Enrol', 'Subscribe', 'Onboard', 'Hire', 'Book', 'Log', 'Record', 'Import')

def kebab(s):
    return re.sub(r'(?<!^)(?=[A-Z])', '-', s).lower()

def lower_camel(s):
    return s[:1].lower() + s[1:] if s else s

def plural(word):
    if re.search(r'(s|x|z|ch|sh)$', word):
        return word + 'es'
    if re.search(r'[^aeiou]y$', word):
        return word[:-1] + 'ies'
    return word + 's'

def collection(type_short):
    parts = kebab(type_short).split('-')
    parts[-1] = plural(parts[-1])
    return '-'.join(parts)

def load_manifests():
    out = []
    for f in sorted(glob.glob(os.path.join(PACKS, '*.yaml'))):
        out.append(yaml.safe_load(open(f)))
    return out

def error_codes_by_owner():
    p = os.path.join(ROOT, 'spec', 'registries', 'errors.yaml')
    if not os.path.exists(p):
        return {}
    by = {}
    for e in yaml.safe_load(open(p))['errors']:
        by.setdefault(e['owner'], []).append(e['code'])
    return by

# ---------------------------------------------------------------- OpenAPI
def match_type(name, shorts):
    best = None
    for s in shorts:
        if s in name and (best is None or len(s) > len(best)):
            best = s
    return best

def openapi_for(m, codes):
    md, sp = m['metadata'], m['spec']
    prov = sp.get('provides', {})
    cmds, qrys = prov.get('commands', []) or [], prov.get('queries', []) or []
    if not cmds and not qrys:
        return None
    cap = md['id']
    slug = cap.split('.')[0]
    types = prov.get('objectTypes', []) or []
    shorts = [t.split('.')[-1] for t in types]
    primary = shorts[0] if shorts else None
    common = '../kernel/common.yaml'
    paths = {}

    def add(path, method, op):
        if method in paths.get(path, {}):
            path = f'{path}#{op["operationId"]}'            # never silently overwrite; checker flags '#'
        paths.setdefault(path, {})[method] = op

    created = set()
    for c in cmds:
        t = match_type(c, shorts) or primary
        verb = c
        if t and c.endswith(t) and c != t:
            verb = c[:-len(t)]
        is_create = bool(t) and c.endswith(t) and verb in CREATE_VERBS and t not in created
        if is_create:
            created.add(t)                                    # first create claims the collection
        base = f'/{slug}/{collection(t)}' if t else f'/{slug}'
        params = [{'$ref': f'{common}#/components/parameters/IdempotencyKey'}, {'$ref': f'{common}#/components/parameters/Traceparent'}]
        if is_create:
            path, status = base, '201'
        else:
            path, status = (f'{base}/{{id}}:{lower_camel(verb)}' if t else f'{base}:{lower_camel(c)}'), '200'
            if t:
                params += [{'$ref': f'{common}#/components/parameters/Id'}, {'$ref': f'{common}#/components/parameters/IfMatch'}]
        add(path, 'post', {
            'operationId': f'{slug}:{c}',
            'summary': f'{c} ({cap})',
            'tags': [cap],
            'parameters': params,
            'requestBody': {'required': True, 'content': {'application/json': {'schema': {
                'type': 'object', 'additionalProperties': True,
                'description': f'Command payload for {c}; see the {md["universe"]} constitution.'}}}},
            'responses': {
                status: {'description': f'{c} accepted',
                         'headers': {'ETag': {'$ref': f'{common}#/components/headers/ETag'}},
                         'content': {'application/json': {'schema': {'$ref': f'{common}#/components/schemas/Object'}}}},
                'default': {'$ref': f'{common}#/components/responses/Problem'}},
            'x-ucos': {'kind': 'command', 'objectType': f'ucos.{types[shorts.index(t)].split(".", 1)[1]}' if t else None,
                       'idempotencyRequired': True},
        })
    for q in qrys:
        t = match_type(q, shorts)
        if t and q == f'Get{t}':
            path = f'/{slug}/{collection(t)}/{{id}}'
            params = [{'$ref': f'{common}#/components/parameters/Id'}, {'$ref': f'{common}#/components/parameters/AsOf'}]
            schema = {'$ref': f'{common}#/components/schemas/Object'}
        elif t and (q in (f'List{plural(t)}', plural(t)) or (q.startswith(plural(t)) and q[len(plural(t)):])):
            rest = q[len(plural(t)):] if q.startswith(plural(t)) else ''
            path = f'/{slug}/{collection(t)}' + (f'/{kebab(rest)}' if rest else '')
            params = [{'$ref': f'{common}#/components/parameters/{p}'} for p in ('Filter', 'Sort', 'PageSize', 'PageCursor', 'AsOf')]
            schema = {'$ref': f'{common}#/components/schemas/Page'}
        else:
            path = f'/{slug}/{kebab(q)}'
            params = [{'$ref': f'{common}#/components/parameters/AsOf'}]
            schema = {'type': 'object', 'additionalProperties': True}
        add(path, 'get', {
            'operationId': f'{slug}:{q}',
            'summary': f'{q} ({cap})',
            'tags': [cap],
            'parameters': params,
            'responses': {'200': {'description': f'{q} result', 'content': {'application/json': {'schema': schema}}},
                          'default': {'$ref': f'{common}#/components/responses/Problem'}},
            'x-ucos': {'kind': 'query'},
        })
    schemas = {t.split('.')[-1]: {'type': 'object', 'additionalProperties': True,
                                  'description': f'Canonical object {t}.',
                                  'x-ucos-schema': f'spec/object-types/{t}.schema.json'} for t in types}
    doc = {
        'openapi': '3.1.0',
        'info': {'title': f'{cap} API', 'version': md['version'],
                 'description': f'{md["purpose"]}\n\nGenerated by tools/gen_contracts.py from spec/capabilities/packs/{cap}.yaml '
                                f'(universe {md["universe"]}, phase {md["phase"]}, maturity {md["maturity"]}). Do not edit.'},
        'servers': [{'url': 'https://{tenantDomain}/api/v1', 'variables': {'tenantDomain': {'default': 'example.ucos.app'}}}],
        'security': [{'bearer': []}],
        'tags': [{'name': cap}],
        'paths': dict(sorted(paths.items())),
        'components': {'securitySchemes': {'bearer': {'type': 'http', 'scheme': 'bearer', 'bearerFormat': 'JWT'}},
                       'schemas': schemas},
        'x-ucos': {'capability': cap, 'universe': md['universe'],
                   'problemCodes': sorted(codes.get(md['universe'], []))},
    }
    return doc

# ---------------------------------------------------------------- events
def payload_for(event, m):
    hand = os.path.join(ROOT, PL_DIR, 'hand', f'{event}.schema.json')
    if os.path.exists(hand):
        s = json.load(open(hand))
        s.setdefault('x-ucos', {})['producer'] = m['metadata']['id']
        return s
    obj = event.split('.')[1]
    types = m['spec'].get('provides', {}).get('objectTypes', []) or []
    match = [t for t in types if kebab(t.split('.')[-1]) == obj] or [t for t in types if kebab(t.split('.')[-1]).startswith(obj)]
    props = {
        'subject': {'$ref': VT + 'UGID'},
        'objectVersion': {'type': 'integer', 'minimum': 1},
        'occurredAt': {'$ref': VT + 'TimePoint'},
        'changes': {'type': 'object', 'description': 'Changed attributes (JSON Merge Patch semantics).', 'additionalProperties': True},
        'data': {'type': 'object', 'description': 'Event-specific facts; see the producing universe constitution.', 'additionalProperties': True},
    }
    if match:
        props['objectType'] = {'const': match[0]}
    return {'$schema': 'https://json-schema.org/draft/2020-12/schema',
            '$id': f'https://schemas.ucos.io/events/{event}/1.json',
            'title': event,
            'description': f'Generated skeleton for {event}. Replace by adding spec/events/payloads/hand/{event}.schema.json.',
            'x-ucos': {'category': 'domain', 'handAuthored': False, 'producer': m['metadata']['id']},
            'type': 'object', 'required': ['subject', 'occurredAt'], 'properties': props, 'additionalProperties': False}

def asyncapi(manifests):
    channels, operations, messages = {}, {}, {}
    for m in manifests:
        for ev in m['spec'].get('provides', {}).get('events', []) or []:
            uni, obj, _ = ev.split('.', 2)
            ch = f'{uni}.{obj}'
            channels.setdefault(ch, {'address': f'ucos.{{cell}}.{uni}.{obj}.v1',
                                     'parameters': {'cell': {'description': 'Cell id, e.g. in-mum-1'}},
                                     'messages': {}})
            channels[ch]['messages'][ev] = {'$ref': f'#/components/messages/{ev}'}
            messages[ev] = {'name': ev, 'contentType': 'application/cloudevents+json',
                            'payload': {'$ref': f'../../events/payloads/{ev}.schema.json'},
                            'x-ucos-producer': m['metadata']['id']}
            op = f'publish.{ch}'
            operations.setdefault(op, {'action': 'send', 'channel': {'$ref': f'#/channels/{ch}'}, 'messages': []})
            operations[op]['messages'].append({'$ref': f'#/channels/{ch}/messages/{ev}'})
    return {'asyncapi': '3.0.0',
            'info': {'title': 'UCOS event catalogue', 'version': '1.0.0',
                     'description': 'Generated by tools/gen_contracts.py from capability manifests. Events use the CloudEvents envelope '
                                    '(spec/events/cloudevent-envelope.schema.json); topics are partitioned by aggregate id.'},
            'defaultContentType': 'application/cloudevents+json',
            'channels': dict(sorted(channels.items())),
            'operations': dict(sorted(operations.items())),
            'components': {'messages': dict(sorted(messages.items()))}}

# ---------------------------------------------------------------- io
def render():
    manifests = load_manifests()
    codes = error_codes_by_owner()
    files = {}
    for m in manifests:
        doc = openapi_for(m, codes)
        if doc:
            files[f'{OA_DIR}/{m["metadata"]["id"]}.yaml'] = yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=200)
        for ev in m['spec'].get('provides', {}).get('events', []) or []:
            files[f'{PL_DIR}/{ev}.schema.json'] = json.dumps(payload_for(ev, m), indent=2, ensure_ascii=False) + '\n'
    files[ASYNC] = yaml.safe_dump(asyncapi(manifests), sort_keys=False, allow_unicode=True, width=200)
    return files

def owned_existing():
    found = set(glob.glob(os.path.join(ROOT, OA_DIR, '*.yaml')))
    found |= set(glob.glob(os.path.join(ROOT, PL_DIR, '*.schema.json')))
    return {os.path.relpath(p, ROOT) for p in found}

def stale(files):
    bad = [p for p, c in files.items()
           if not os.path.exists(os.path.join(ROOT, p)) or open(os.path.join(ROOT, p), encoding='utf-8').read() != c]
    extra = sorted(owned_existing() - set(files))
    return bad, extra

def main():
    files = render()
    bad, extra = stale(files)
    if '--check' in sys.argv:
        for p in bad + extra:
            print('out of date:', p)
        sys.exit(1 if bad or extra else 0)
    for p in extra:
        os.remove(os.path.join(ROOT, p))
    for p in bad:
        os.makedirs(os.path.dirname(os.path.join(ROOT, p)), exist_ok=True)
        open(os.path.join(ROOT, p), 'w', encoding='utf-8').write(files[p])
    n_oa = sum(1 for p in files if p.startswith(OA_DIR))
    n_ev = sum(1 for p in files if p.startswith(PL_DIR))
    print(f'openapi: {n_oa}  event payloads: {n_ev}  asyncapi: 1  (written {len(bad)}, removed {len(extra)})')

if __name__ == '__main__':
    main()
