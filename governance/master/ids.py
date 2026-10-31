"""Identifier formats from the registry (LXM-REQ-000240): X() expands placeholders in a string from ids.json, so no tool
writes an identifier format itself. Placeholders: {ns} the regex of an ID, {ns%} its printf template, {ns-} its prefix,
{ns~} the namespace's registered label, {ns#} the placeholder form (NNNNNN), {ns=digits} one specific ID;
{cl} a clause regex and {cl-} the clause marker."""
import json, os, re, sys
sys.dont_write_bytecode = True

REG = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ids.json'), encoding='utf-8'))
NS, CL = REG['namespaces'], REG['clause']
_P = re.compile(r'\{(%s)([%%#=~-]?)(\d*)\}' % '|'.join(map(re.escape, list(NS) + [CL['name']])))


def _one(m):
    name, op, n = m.groups()
    if name == CL['name']:
        return {'': CL['marker'] + CL['pattern'], '-': CL['marker']}[op]
    ns = NS[name]
    return {'': ns['prefix'] + r'\d{%d}' % ns['digits'], '%': ns['prefix'] + '%%0%dd' % ns['digits'], '-': ns['prefix'],
            '~': ns['label'], '#': ns['prefix'] + 'N' * ns['digits'], '=': ns['prefix'] + n}[op]


def X(s):
    """The string with every identifier placeholder expanded."""
    return _P.sub(_one, s)
