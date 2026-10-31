"""Fixtures for agnostic.py: synthetic Master folders in throwaway directories; nothing else is read.
Usage: python3 -I -B test_agnostic.py <master root>"""
import json, os, shutil, sys, tempfile
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import agnostic as G
results = []


def fixture(files):
    d = tempfile.mkdtemp(prefix='agfx-')
    reg = {'actors.json': {'actors': {'a': {'label': 'agent-alpha', 'aliases': ['VendorBot']}}, 'roles': {}},
           'hosts.json': {'hosts': {'somehost': {'aliases': ['shcli']}}},
           'agnostic.json': {'registries': {'actors.json': ['actors.*.label', 'actors.*.aliases'], 'hosts.json': ['hosts.*', 'hosts.*.aliases']},
                             'scan': {'roots': ['.'], 'extensions': ['.py', '.json'], 'recursive_roots': []},
                             'registry_files': ['actors.json', 'hosts.json'], 'adapter_dirs': ['adapters/'], 'exempt': {'layout.json': 'a path the repository chose'}}}
    for p, c in list(reg.items()) + list(files.items()):
        os.makedirs(os.path.dirname(os.path.join(d, p)) or d, exist_ok=True)
        open(os.path.join(d, p), 'w').write(c if isinstance(c, str) else json.dumps(c))
    return d


def scenario(name, files, want):
    d = fixture(files)
    try:
        ns, hits = G.check(d)
        ok = sorted(h.split(' ')[0] for h in hits) == sorted(want)
        results.append((name, ok, 'names %s; hits %s' % (ns, hits)))
    finally:
        shutil.rmtree(d, ignore_errors=True)


scenario('Clean tooling passes', {'tool.py': 'print("role-based")\n'}, [])
scenario('A registered agent alias in code fails, any case', {'tool.py': 'x = 1\nuse("vendorbot")\n'}, ['tool.py:2'])
scenario('A registered host id or tool name in configuration fails', {'cfg.json': '{"cmd": ["shcli", "view"], "host": "somehost"}'}, ['cfg.json:1', 'cfg.json:1'])
scenario('Registries, adapters and declared exemptions are not findings', {'adapters/somehost/job.py': 'shcli()\n', 'layout.json': '{"p": "somehost/x"}'}, [])
scenario('Part of a longer identifier is not a name', {'tool.py': 'agent-alpha-2 = 0\nshclix = 1\n'}, [])
fails = 0
for name, ok, detail in results:
    fails += not ok
    print('%s  %-58s %s' % ('PASS' if ok else 'FAIL', name, detail))
print('\n%d scenarios, %d failed' % (len(results), fails))
sys.exit(1 if fails else 0)
