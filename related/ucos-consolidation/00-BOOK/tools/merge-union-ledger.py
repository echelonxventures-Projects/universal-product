#!/usr/bin/env python3
"""UCOS Ω∞ — merge driver for the IRREVERSIBLE identity ledger.  argv: %O %A %B %P

WHY UNION AND NEVER REGENERATE. `id-ledger.json` holds permanent allocations. Re-deriving
it would reissue identity, which UCKP-ART-05 forbids outright, so the regenerate driver is
wrong here for a constitutional reason rather than a practical one.

WHY IT REFUSES RATHER THAN RESOLVES. Two branches that allocated the SAME identifier to
DIFFERENT paths is an identity collision. Silently keeping one side would destroy an
allocation that some commit already treats as permanent. A collision must stop the merge
loudly and be resolved by a person under a permit — never by a driver.

COUNTERS ARE RECONCILED, NOT UNIONED. `page_cursor` and each `category_seq` are monotonic,
so the maximum is taken — but only after the collision check passes, because a max over a
colliding ledger would hide the collision behind a plausible number.
"""

import json
import os
import sys


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def merge_map(name, ours, theirs, conflicts):
    out = dict(ours)
    for key, value in theirs.items():
        if key in out and out[key] != value:
            conflicts.append(f"{name}[{key!r}]: ours={out[key]!r} theirs={value!r}")
        else:
            out[key] = value
    return out


def main(argv):
    _base, ours_path, theirs_path = argv[1], argv[2], argv[3]
    ours, theirs = load(ours_path), load(theirs_path)
    conflicts: list[str] = []
    merged = dict(ours)
    for name in ("by_path", "by_object", "by_observation"):
        merged[name] = merge_map(name, ours.get(name, {}), theirs.get(name, {}), conflicts)
    if conflicts:
        sys.stderr.write(
            "ucos-union-ledger: REFUSED — identity collision, which ART-05 forbids "
            "resolving automatically:\n  " + "\n  ".join(conflicts) + "\n"
            "Resolve under an operator permit; do not choose a side.\n"
        )
        return 1
    merged["history"] = list(ours.get("history", [])) + [
        e for e in theirs.get("history", []) if e not in ours.get("history", [])
    ]
    merged["page_cursor"] = max(ours.get("page_cursor", 0), theirs.get("page_cursor", 0))
    seq = dict(ours.get("category_seq", {}))
    for cat, n in theirs.get("category_seq", {}).items():
        seq[cat] = max(seq.get(cat, 0), n)
    merged["category_seq"] = seq
    with open(ours_path, "w", encoding="utf-8") as fh:
        json.dump(merged, fh, indent=1, sort_keys=True, ensure_ascii=False)
        fh.write("\n")
    return 0


def selftest() -> int:
    """Prove the two behaviours this driver exists for, on demand.

    A merge driver runs only during a merge, so nothing else in the repository would notice if
    it stopped working — and the failure would be silent in the worst way: git would fall back
    to a text merge and produce an identity ledger neither branch wrote. This exercises both
    directions against temporary files so `make merge-drivers` is a real check rather than a
    reachability formality.
    """
    import tempfile

    base = {"by_path": {}, "by_object": {}, "page_cursor": 1, "category_seq": {}}
    ours = {
        "by_path": {"a": {"uid": "A"}},
        "by_object": {},
        "page_cursor": 5,
        "category_seq": {"A": 5},
    }
    theirs = {
        "by_path": {"b": {"uid": "B"}},
        "by_object": {},
        "page_cursor": 7,
        "category_seq": {"A": 7},
    }
    collide = {
        "by_path": {"a": {"uid": "DIFFERENT"}},
        "by_object": {},
        "page_cursor": 6,
        "category_seq": {},
    }

    def run(left, right):
        d = tempfile.mkdtemp()
        paths = []
        for name, doc in (("O", base), ("A", left), ("B", right)):
            path = os.path.join(d, name)
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(doc, fh)
            paths.append(path)
        return main(["", *paths]), paths[1]

    code, merged_path = run(ours, theirs)
    if code != 0:
        sys.stderr.write("selftest FAILED: disjoint allocations were refused\n")
        return 1
    with open(merged_path, encoding="utf-8") as fh:
        merged = json.load(fh)
    if sorted(merged["by_path"]) != ["a", "b"]:
        sys.stderr.write(f"selftest FAILED: union lost an allocation: {merged['by_path']}\n")
        return 1
    if merged["page_cursor"] != 7 or merged["category_seq"].get("A") != 7:
        sys.stderr.write("selftest FAILED: monotonic counters were not reconciled to the max\n")
        return 1

    code, _ = run(ours, collide)
    if code == 0:
        sys.stderr.write(
            "selftest FAILED: an identity collision was resolved automatically, which ART-05 "
            "forbids. One key carried two values and the driver picked a side.\n"
        )
        return 1

    sys.stdout.write("merge-union-ledger selftest: union holds, collision refused\n")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(selftest())
    raise SystemExit(main(sys.argv))
