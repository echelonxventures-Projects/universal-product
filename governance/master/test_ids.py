"""Fixtures for ids.py: expansion comes from the registry, in a throwaway copy with its own namespaces.
Usage: python3 -I -B test_ids.py <master root>"""
import importlib.util, json, os, re, shutil, sys, tempfile
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
results = []


def load(reg):
    d = tempfile.mkdtemp(prefix='idfx-')
    shutil.copyfile(os.path.join(HERE, 'ids.py'), os.path.join(d, 'ids.py'))
    json.dump(reg, open(os.path.join(d, 'ids.json'), 'w'))
    spec = importlib.util.spec_from_file_location('ids_fx', os.path.join(d, 'ids.py')); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    shutil.rmtree(d, ignore_errors=True)
    return m


REG = {'namespaces': {'req': {'prefix': 'Q-', 'digits': 3, 'label': 'Q'}, 'src': {'prefix': 'S/', 'digits': 2, 'label': 'Src'}}, 'clause': {'name': 'cl', 'marker': '#', 'pattern': '[0-9]+'}}
m = load(REG)
cases = [('regex', '^({req})$', '^(Q-\\d{3})$'), ('template', '{req%}', 'Q-%03d'), ('prefix and label', '{src-}x {src~}', 'S/x Src'),
         ('placeholder form', '{req#}', 'Q-NNN'), ('one specific ID', '{req=007}', 'Q-007'), ('clause', '{cl} {cl-}', '#[0-9]+ #'),
         ('quantifiers and unknown braces untouched', 'a{2,3} {zz} {}', 'a{2,3} {zz} {}')]
for name, s, want in cases:
    got = m.X(s); results.append((name, got == want, '%r -> %r' % (s, got)))
q = re.compile(m.X('^{req}$'))
results.append(('A registry change alone changes what matches', bool(q.match('Q-123')) and not q.match('LXM-REQ-000123'), 'Q-123 matches; the old format does not'))
fails = 0
for name, ok, detail in results:
    fails += not ok
    print('%s  %-48s %s' % ('PASS' if ok else 'FAIL', name, detail))
print('\n%d scenarios, %d failed' % (len(results), fails))
sys.exit(1 if fails else 0)
