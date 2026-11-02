"""Knowledge versions and the single entry point (LXM-REQ-000253).
Usage:
  python3 -I versions.py <master root>          check: every file is classified, every item's text is a version the gate recorded
  python3 -I versions.py <master root> <item>   the item's versions: ledger line, time, contribution, outcome, runtimes, SHA-256

An item is a record, decision, evidence entry, source row, stage or trace entry, the rest of a canonical file, a registry or a
file under sources/ (layout.json items). Each accepted gate run records the new version of every item it changed, found by
comparing texts, not by trusting what a contribution claims; the first line that records versions gives every item version 1.
Exit 0 pass, 1 fail."""
import json, os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import assimilate as A
from ids import X


def unclassified(root):
    """Files and folders in the Master that are neither canonical, a registry, code, a document nor an area: knowledge with no entry rule."""
    c = A.LAYOUT['classify']
    known = set(A.CANON) | set(A.REGISTRIES) | {A._N[k] for k in c['documents']} | {A._N[k] for k in c['areas']} | set(c['ignored'])
    return sorted(f for f in os.listdir(root) if f not in known and not (os.path.isfile(os.path.join(root, f)) and os.path.splitext(f)[1] in c['code_suffixes']))


def history(root, item):
    rows = []
    for line in open(os.path.join(root, A.LEDGER), encoding='utf-8'):
        e = json.loads(line) if line.strip() else {}
        if item in (e.get('versions') or {}):
            n, s = e['versions'][item]
            rows.append((n, e['seq'], e['at'], e.get('contribution'), e.get('outcome'), e.get('runtime'), s))
    return rows


if __name__ == '__main__':
    root = sys.argv[1]
    if len(sys.argv) > 2:
        rows = history(root, sys.argv[2])
        for n, seq, at, ctb, outcome, rt, s in rows:
            print('v%d  ledger %s  %s  %s %s  %s  %s' % (n, seq, at, ctb, outcome, ' '.join('%s %s' % kv for kv in sorted((rt or {}).items())), (s or 'removed')[:12]))
        print('%s: %d version(s)' % (sys.argv[2], len(rows)))
        sys.exit(0 if rows else 1)
    vm, loose, outside = A.version_map(root), unclassified(root), A.outside_gate(root)
    if vm is None:
        print('FAIL  the log records no versions yet'); sys.exit(1)
    live = {k: v for k, v in vm.items() if v[1] is not None}
    for f in loose:
        print('FAIL  %s is not classified in %s (classify)' % (f, X('{@layout_json}')))
    for i in outside:
        print('FAIL  %s: its text is no version the gate recorded (changed outside the gate)' % i)
    print('%d knowledge items, %d versions recorded; %d unclassified, %d changed outside the gate' % (
        len(live), sum(n for n, s in live.values()), len(loose), len(outside)))
    sys.exit(1 if loose or outside else 0)
