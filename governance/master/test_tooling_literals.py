"""Fixtures for tooling_literals.py: synthetic tool folders in throwaway directories.
Usage: python3 -I -B test_tooling_literals.py <master root>"""
import json, os, shutil, sys, tempfile
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import tooling_literals as T
results = []


def folder(files):
    d = tempfile.mkdtemp(prefix='tlfx-')
    shutil.copyfile(os.path.join(HERE, 'tooling-literals.json'), os.path.join(d, 'tooling-literals.json'))
    for p, c in files.items():
        open(os.path.join(d, p), 'w').write(c)
    return d


def run(name, files, check):
    d = folder(files)
    try:
        counts, _ = T.scan(d)
        b = os.path.join(d, 'b.json'); json.dump(counts, open(b, 'w'))
        ok, detail = check(d, counts, b)
        results.append((name, ok, detail))
    finally:
        shutil.rmtree(d, ignore_errors=True)


def grow(d, counts, b):
    open(os.path.join(d, 'tool.py'), 'a').write('Y = "reqs.txt"\n')
    return T.main(['x', d, '--baseline', b]) == 1, 'a new file literal raises the count -> ratchet fails'


def shrink(d, counts, b):
    open(os.path.join(d, 'tool.py'), 'w').write('import json\nX = json.load(open(CFG))["file"]\n')
    return T.main(['x', d, '--baseline', b]) == 0, 'moving the literal into configuration lowers the count -> ratchet passes'


run('Kinds are found: file, identifier format, number, hash, date', {'tool.py': 'A = "intake/x.json"\nB = r"LXM-REQ-\\d{6}"\nC = 0.75\nD = "0123456789abcdef"\nE = "2026-10-31"\n"""a docstring is not a literal"""\n'},
    lambda d, c, b: (sorted(k.split(' · ')[1] for k in c) == ['date', 'file or path', 'hash', 'identifier format', 'number'], str(c)))
run('Small numbers and plain messages are not findings', {'tool.py': 'n = 0\nm = 1\nprint("nothing configured here")\n'}, lambda d, c, b: (c == {}, str(c)))
run('A new literal fails the ratchet', {'tool.py': 'A = "intake/x.json"\n'}, grow)
run('Moving a literal out passes the ratchet', {'tool.py': 'A = "intake/x.json"\n'}, shrink)
fails = 0
for name, ok, detail in results:
    fails += not ok
    print('%s  %-62s %s' % ('PASS' if ok else 'FAIL', name, detail))
print('\n%d scenarios, %d failed' % (len(results), fails))
sys.exit(1 if fails else 0)
