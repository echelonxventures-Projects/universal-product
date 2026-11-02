"""The technologies the Master's tooling runs on, and their versions (LXM-REQ-000253). runtimes.json registers each one, how its
version is read and the versions it supports; nothing here names a technology.
Usage: python3 -I runtimes.py <master root> [--at gate|ci]   exit 0 every checked runtime is on a supported version, 1 otherwise."""
import json, os, re, subprocess, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from ids import X


def probe(spec):
    """The version of one runtime as a string, or None when it cannot be read."""
    if spec['probe'] == 'self':
        return '.'.join(map(str, sys.version_info[:3]))
    try:
        out = subprocess.run(spec['probe'], capture_output=True, text=True).stdout
    except OSError:
        return None
    m = re.search(spec['pattern'], out)
    return m.group(1) if m else None


def supported(version, prefixes):
    return version is not None and any(version == p or version.startswith(p + '.') for p in prefixes)


def check(root, at):
    """{name: (version, supported)} for every runtime checked at this point."""
    reg = json.load(open(os.path.join(root, X('{@runtimes_json}')), encoding='utf-8'))['runtimes']
    out = {}
    for name, spec in sorted(reg.items()):
        if at in spec['checked_at']:
            v = probe(spec); out[name] = (v, supported(v, spec['supported']))
    return out


if __name__ == '__main__':
    at = sys.argv[sys.argv.index('--at') + 1] if '--at' in sys.argv else 'ci'
    res = check(sys.argv[1], at)
    for name, (v, ok) in res.items():
        print('%s  %s %s' % ('ok  ' if ok else 'FAIL', name, v or 'not found'))
    bad = [n for n, (v, ok) in res.items() if not ok]
    print('%d runtime(s) checked at %s; %d outside their supported versions' % (len(res), at, len(bad)))
    sys.exit(1 if bad else 0)
