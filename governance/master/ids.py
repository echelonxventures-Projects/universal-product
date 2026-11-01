"""Registry placeholders (LXM-REQ-000240): X() expands identifier placeholders from ids.json and file placeholders from
layout.json, so no tool writes an identifier format or a file name itself. {@key} is the file or folder layout.json names for key. Placeholders: {ns} the regex of an ID, {ns%} its printf template, {ns-} its prefix,
{ns~} the namespace's registered label, {ns#} the placeholder form (NNNNNN), {ns=digits} one specific ID;
{cl} a clause regex and {cl-} the clause marker."""
import json, os, re, sys
sys.dont_write_bytecode = True

REG = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ids.json'), encoding='utf-8'))
NAMES = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'layout.json'), encoding='utf-8'))['names']
_F = re.compile(r'\{@([\w]+)\}')
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
    """The string with every identifier and file placeholder expanded; an unknown file key fails loudly."""
    return _F.sub(lambda m: NAMES[m.group(1)], _P.sub(_one, s))
