"""Level 2 as a projection (design §1): rebuild the canonical registers from a checkpoint by applying the mutations the
gate's log recorded, in order, without judging any contribution again.
Usage: python3 -I project.py <checkpoint root> <log root> [--out <dir>]   (default --out: a fresh temporary directory)
Prints, for each canonical file, whether the projection equals the log root's current file. Exit 0 equal, 1 different."""
import json, os, shutil, sys, tempfile
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import assimilate as A


def project(checkpoint, log_root, out):
    shutil.copytree(checkpoint, out, dirs_exist_ok=True)
    start = A.state_digest(checkpoint)
    lines = [json.loads(l) for l in open(os.path.join(log_root, A.LEDGER), encoding='utf-8') if l.strip()]
    i = next((k for k, e in enumerate(lines) if e.get('digest_before') == start and e.get('mutation')), None)  # first change after the checkpoint
    applied = 0
    for e in lines[i:] if i is not None else []:
        m = e.get('mutation')
        if not m:
            continue
        reqs, stages = A.read(os.path.join(out, 'reqs.txt')), A.read(os.path.join(out, 'stages.txt'))
        if m.get('ops'):
            reqs, stages, _ = A.apply([tuple(x) for x in m['ops']], reqs, stages)
        for f, t in ((m.get('contents') or {}).items()):
            open(os.path.join(out, f), 'w', encoding='utf-8').write(t)
        open(os.path.join(out, 'reqs.txt'), 'w', encoding='utf-8').write(reqs)
        open(os.path.join(out, 'stages.txt'), 'w', encoding='utf-8').write(stages)
        for f, h in m['files'].items():
            if A.sha(open(os.path.join(out, f), 'rb').read()) != h:
                raise SystemExit('projection diverged at ledger seq %s on %s' % (e['seq'], f))
        applied += 1
    return applied


if __name__ == '__main__':
    cp, lr = sys.argv[1], sys.argv[2]
    out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else tempfile.mkdtemp(prefix='lxm-projection-')
    n = project(cp, lr, out)
    same = {f: A.sha(open(os.path.join(out, f), 'rb').read()) == A.sha(open(os.path.join(lr, f), 'rb').read()) for f in ('reqs.txt', 'stages.txt', 'decisions.txt', 'evidence.txt')}
    print('%d recorded mutations applied from the checkpoint; %s' % (n, ', '.join('%s %s' % (f, 'equal' if v else 'DIFFERENT') for f, v in same.items())))
    sys.exit(0 if all(same.values()) else 1)
