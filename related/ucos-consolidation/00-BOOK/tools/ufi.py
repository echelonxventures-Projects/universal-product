#!/usr/bin/env python3
"""
UCOS Ω∞ — Universal Formal Independence framework (UFI).

WHAT THIS IS FOR. MB7: a producer validated only by its own programme cannot be shown
to be CORRECT, only CONSISTENT. Measured across this repository: `validation_owner`
equals `owner` for every entry of the generated-artifact registry, no producer has a
single test inside its own home, and 14 of 33 producers have no validator anywhere.
A producer that is uniformly wrong emits self-consistent output and every check derived
from that run agrees with it.

UCOS-UCTX-001 was closed against that defect by an independent verifier. This module is
that verifier with the capability taken out of it. It exists so the second producer to
adopt formal independence writes a DECLARATION rather than a second verifier — a
repository with 33 hand-written verifiers has 33 new things that can be uniformly wrong,
which is the defect again with more files.

WHAT IS SHARED AND WHAT MAY NEVER BE. The CODE is shared: one implementation of the
three checks, one place a bug is fixed, one place an attack is measured. The AUTHORITY
is never shared. Each adopter names its own authorities and its own template manifest,
and this module holds no list of either. A shared authority source would make every
adopter's truth a projection of one instrument, which is the rival-authority failure
UCKP-ART-03 voids — the opposite of what independence means.

THE THREE CHECKS, AND WHY THREE.

  CHECK 1 — PROVENANCE. Every emitted LINE traces to a declared source: a reviewed
    template in the adopter's manifest, or a string one of the adopter's declared
    authorities already holds. A sentence the generator invents is in neither.

  CHECK 2 — RECORD INTEGRITY. Every declared record is projected WHOLE. Provenance asks
    only whether a cell traces to SOME declared string, which admits keeping every cell
    and changing which record it sits with. Cells sharing a row must reconcile with one
    record; a page named after a record may not display another record's values.

  CHECK 3 — COMPLETENESS. Every declared obligation is CARRIED. Checks 1 and 2 both
    reason about what was emitted, so neither can see a producer that emits LESS.

Measured on the reference adopter: of ten uniformly wrong variants, five emit no text
that is not declared. CHECK 1 alone passed all five. That is why there are three.

WHAT AN ADOPTER DECLARES. An independence declaration names three things and nothing
else — its authorities, its surfaces, and its manifest. Each may be a literal list or a
POINTER of the form {"from": <path>, "json_path": "a.b[].c"} into an instrument that
already says it. The pointer form exists so adopting this framework never re-authors a
list that a declaration already holds, which UCKP-ART-03 would void.

This module reads. It writes nothing, imports no producer, and executes none.

Usage:
    python3 00-BOOK/tools/ufi.py <independence-declaration.json>
    python3 00-BOOK/tools/ufi.py <declaration> --report   # list findings, exit 0
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

#: Shortest declared string that may stand in for a template slot. Below this a corpus
#: hit is a coincidence ("the", "and") and normalising on it would erase the sentence
#: rather than its values — which would let injected text normalise onto a template.
MIN_SLOT = 6

CELL_CLEAN = re.compile(r"^[`*_\s]+|[`*_\s]+$")
STRUCTURAL = re.compile(r"^[\s|:\-]*$")


def read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# Declaration resolution
# ---------------------------------------------------------------------------
class UnsupportedPointer(Exception):
    """A json_path this resolver cannot answer.

    It is its own type so that an unreadable POINTER is reported as a refusal naming the
    adopter and the pointer, and never escapes as a traceback. A framework that dies with
    a KeyError has said nothing about the adopter it was asked to verify, and "said
    nothing" is indistinguishable from "found nothing" in a CI log — which is the
    vacuous pass this framework exists to prevent.
    """

    def __init__(self, path: str, at: str):
        super().__init__(f"unsupported json_path {path!r} at {at!r}")
        self.path, self.at = path, at


#: ONE step of a pointer: a key, optionally followed by `[]` (map over the list it names)
#: or by `[?key=='value']` (keep the records of that list whose field equals value).
#:
#: The filter form is resolved HERE rather than by rewriting the one declaration that used
#: it. Two adopters already point with `[]`, the registry groups its entries by owner, and
#: every future adopter that wants "my rows out of a shared register" wants exactly this
#: predicate — so the declaration was not wrong, the resolver was incomplete.
_STEP = re.compile(
    r"(?P<name>[^.\[\]]+)"
    r"(?:(?P<map>\[\])|\[\?(?P<key>[^.\[\]=]+)\s*==\s*'(?P<value>[^']*)'\])?"
)


def _walk_json_path(node, path: str):
    """Resolve "a.b[].c" or "entries[?owner=='X'].canonical_path" against a document.

    `[]` maps over a list; `[?key=='value']` selects from one. The path is tokenised
    whole before anything is walked, so an unsupported pointer refuses up front instead
    of half-resolving and failing later as a KeyError against a literal step.
    """
    steps, pos = [], 0
    while pos < len(path):
        step = _STEP.match(path, pos)
        if not step:
            raise UnsupportedPointer(path, path[pos:])
        steps.append(step)
        pos = step.end()
        if pos < len(path):
            if path[pos] != ".":
                raise UnsupportedPointer(path, path[pos:])
            pos += 1

    for step in steps:
        name = step.group("name")
        try:
            node = [x[name] for x in node] if isinstance(node, list) else node[name]
        except (KeyError, IndexError, TypeError) as exc:
            raise UnsupportedPointer(path, name) from exc
        if step.group("map"):
            node = list(node)
        elif step.group("key"):
            key, value = step.group("key"), step.group("value")
            node = [x for x in node if str(x.get(key)) == value]
    return node


def resolve(value, repo: str) -> list:
    """A declared list, or a POINTER into an instrument that already holds it.

    The pointer form is the whole reason this framework does not force an adopter to
    re-author what its own declaration already says.
    """
    if isinstance(value, list):
        out = []
        for v in value:
            out += resolve(v, repo) if isinstance(v, dict) else [v]
        return out
    if isinstance(value, dict):
        if "glob" in value:
            import glob as _g
            base = os.path.join(repo, value["glob"])
            return sorted(os.path.relpath(p, repo) for p in _g.glob(base))
        doc = json.loads(read(os.path.join(repo, value["from"])))
        got = _walk_json_path(doc, value["json_path"])
        got = list(got) if isinstance(got, list) else [got]
        # a declaration may name its registers by bare filename; the prefix is where
        # they live, which is the one thing the pointer cannot read out of the document
        out = [value.get("prefix", "") + str(g) for g in got]
        # `suffix` narrows by FORMAT, which is the other thing the pointed-at document
        # does not record. BASELINE-001's registry entries are identical in every field
        # for its dashboard and for baseline.json, so no filter expression can separate
        # a prose projection from a record file; the alternative is copying the list of
        # surfaces into the adoption, which is the second authoring UCKP-ART-03 voids.
        return [o for o in out if o.endswith(value["suffix"])] if "suffix" in value else out
    return [value]


# ---------------------------------------------------------------------------
# The declared corpus — every string the adopter's authorities hold
# ---------------------------------------------------------------------------
def strings_of(obj, out: set) -> set:
    if isinstance(obj, str):
        out.add(obj)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            out.add(str(k))
            strings_of(v, out)
    elif isinstance(obj, list):
        for v in obj:
            strings_of(v, out)
    return out


def declared_corpus(authorities: list, repo: str) -> set:
    corpus: set = set()
    for rel in sorted(set(authorities)):
        path = os.path.join(repo, rel)
        if not os.path.isfile(path):
            continue
        if rel.endswith(".json"):
            try:
                strings_of(json.loads(read(path)), corpus)
            except ValueError:
                pass
        else:
            # a source module: its identifiers and statements are string literals,
            # which is where they are authored
            for m in re.finditer(r'"((?:[^"\\]|\\.)*)"', read(path)):
                try:
                    corpus.add(json.loads('"' + m.group(1) + '"'))
                except ValueError:
                    corpus.add(m.group(1))
    return {c for c in corpus if c and c.strip()}


# ---------------------------------------------------------------------------
# CHECK 1 — provenance
# ---------------------------------------------------------------------------
def concatenation_of(cell: str, corpus: set, lengths: list) -> bool:
    """True if the cell tiles, left to right, out of declared pieces and nothing else.

    A long declared statement is often authored as adjacent string literals, so the
    emitted cell exists in no single string yet contains not one authored character.
    Copying such statements into a manifest to admit them would be the second authoring
    UCKP-ART-03 voids; this decides the question instead.
    """
    n = len(cell)
    reach = [False] * (n + 1)
    reach[0] = True
    for i in range(n):
        if not reach[i]:
            continue
        for ln in lengths:
            j = i + ln
            if j <= n and not reach[j] and cell[i:j] in corpus:
                reach[j] = True
        if reach[n]:
            return True
    return reach[n]


def cell_is_derived(cell: str, corpus: set, allowed_cells: set, lengths: list) -> bool:
    c = CELL_CLEAN.sub("", cell).strip()
    if not c or c in allowed_cells or c in corpus:
        return True
    if len(c) >= MIN_SLOT and any(c in s for s in corpus):
        return True
    return len(c) > 40 and concatenation_of(c, corpus, lengths)


def normalise(line: str, corpus_sorted: list) -> str:
    """The line with every DECLARED value replaced by a slot.

    This is what lets one template cover many surfaces: the parts that differ are
    declared values, and the part that must not differ is the sentence around them.
    Injected text contains no declared value, so it normalises to itself.
    """
    out = line
    for value in corpus_sorted:
        if len(value) < MIN_SLOT:
            break
        if value in out:
            out = out.replace(value, "{}")
    return re.sub(r"(\{\})+", "{}", out).strip()


def classify(line: str, manifest: dict, corpus: set) -> tuple:
    s = line.strip()
    if not s or STRUCTURAL.match(s):
        return "OK", "structural"
    allowed_lines = manifest["_allowed_lines"]
    allowed_cells = manifest["_allowed_cells"]
    if s in allowed_lines:
        return "OK", "declared template"
    if normalise(s, manifest["_corpus_sorted"]) in allowed_lines:
        return "OK", "declared template (normalised)"
    if s.startswith("|"):
        bad = [c.strip() for c in s.strip("|").split("|")
               if not cell_is_derived(c, corpus, allowed_cells, manifest["_lengths"])]
        if bad:
            return "UNPROVENANCED", "table cell(s): " + " ; ".join(bad[:3])
        return "OK", "derived table row"
    body = CELL_CLEAN.sub("", re.sub(r"^[-*]\s+|^\d+\.\s+", "", s))
    if body in corpus or any(body in c for c in corpus):
        return "OK", "derived prose"
    return "UNPROVENANCED", "free text in no manifest and no authority"


# ---------------------------------------------------------------------------
# CHECK 2 — record integrity
# ---------------------------------------------------------------------------
def record_values(rec) -> set:
    """The VALUES a declared record carries. Keys are not values: a key is a schema
    word the projection may legitimately reuse as a label."""
    out: set = set()
    if isinstance(rec, str):
        if len(rec) >= MIN_SLOT:
            out.add(rec)
    elif isinstance(rec, dict):
        for v in rec.values():
            out |= record_values(v)
    elif isinstance(rec, list):
        for v in rec:
            out |= record_values(v)
    return out


def collections_of(authorities: list, repo: str) -> dict:
    """Every declared collection of records: {name: (records, value -> record ids)}.

    Discovered, never listed — a list of dicts in a declared authority IS a collection.
    """
    colls: dict = {}
    for rel in sorted(set(authorities)):
        path = os.path.join(repo, rel)
        if not (os.path.isfile(path) and rel.endswith(".json")):
            continue
        try:
            doc = json.loads(read(path))
        except ValueError:
            continue
        for key, value in (doc.items() if isinstance(doc, dict) else []):
            if not (isinstance(value, list) and len(value) > 1
                    and all(isinstance(x, dict) for x in value)):
                continue
            index: dict = {}
            for i, rec in enumerate(value):
                for v in record_values(rec):
                    index.setdefault(v, set()).add(i)
            if index:
                colls[f"{rel}:{key}"] = (value, index)
    return colls


def row_cells(line: str) -> list:
    return [CELL_CLEAN.sub("", c).strip() for c in line.strip().strip("|").split("|")]


def row_integrity(cells: list, colls: dict):
    """A table row must reconcile, per collection, with ONE declared record.

    Three real shapes make the naive rule wrong. All three were measured on UNATTACKED
    output before this was written, which is the only reason they are known:

      * A RELATION row names two records of one collection by design — a state machine's
        transition holds a `from` and a `to`.
      * A row may mix a declared value with a computed one: a record id and a path from
        the declaration beside a status the engine derived. A lone hit is never evidence.
      * Two collections may hold the SAME string in different records by coincidence — one
        declaration listed a path under `records` and again under `findings`, so the row
        looked like it drew from two `findings` records when it drew from one `records`
        record and never mentioned findings at all.

    The third is what ATTRIBUTION below resolves: a cell that some record of ANOTHER
    collection holds together with a second cell of this row belongs to that record, not
    to this collection. The attack is deliberately not rescued by it — a permuted table
    draws from two records of the SAME collection, and a same-collection record never
    attributes a cell away from itself.
    """
    covers = [(name, record_values(rec) & set(cells))
              for name, (recs, _i) in colls.items() for rec in recs]
    strong = [(name, c) for name, c in covers if len(c) >= 2]
    for name, (recs, index) in colls.items():
        hits = {c for c in cells if c in index}
        hits -= {c for other, cov in strong if other != name for c in cov}
        if len(hits) < 2:
            continue
        if any(hits <= record_values(r) for r in recs):
            continue
        return sorted(hits)[:3]
    return None


def table_shape(block: list):
    """A markdown table has a header, then a separator, then its body.

    Measured need: rotating a file's table rows left every row internally consistent, every
    cell declared and every record present — provenance, record integrity and completeness
    all passed. What actually moved was the HEADER, to the bottom, with the separator behind
    it. No content check can see that, because no content changed; only the shape did.
    """
    seps = [i for i, ln in enumerate(block) if re.fullmatch(r"\|[\s|:-]+\|?", ln.strip())]
    if not seps:
        return None                      # not a header/body table; nothing is claimed
    if len(seps) > 1:
        return f"table carries {len(seps)} separator rows at {seps}"
    if seps[0] != 1:
        return (f"table separator is at row {seps[0] + 1}, not row 2 — the header is not "
                f"where a header goes")
    return None


def header_is_a_header(block: list, raw: list, colls: dict):
    """The row above the separator names COLUMNS. It must not be a declared RECORD.

    This is what finally catches a rotated table. Rotating a file's table rows by one
    leaves the separator where it was, every row internally consistent and every record
    still present — so shape, provenance, record integrity and completeness all pass. The
    single thing that moved is which row sits in the header position, and a header that
    reconciles to a declared record is not a header.
    """
    seps = [i for i, ln in enumerate(raw) if re.fullmatch(r"\|[\s|:-]+\|?", ln.strip())]
    if seps[:1] != [1] or len(raw) < 3:
        return None
    head = row_cells(raw[0])
    for name, (recs, _i) in colls.items():
        for rec in recs:
            if len({c for c in head if c} & record_values(rec)) >= 2:
                return (f"the header row of a table holds a declared record of {name} — "
                        f"the rows are not in their emitted positions")
    return None


def table_order(rows: list, colls: dict):
    """Rows that project a collection must arrive in a determinate ORDER.

    Checks 1-3 are all order-insensitive, and measured that is a real hole: rotating a
    table's rows intact leaves every row reconciling to its own record and the row SET
    unchanged, so provenance, record integrity and completeness all pass a table whose
    every row now sits against the wrong neighbour.

    A generator has no freedom about order — it emits either the order its declaration
    holds or a sort of some emitted column. Both are accepted; anything else is a
    permutation. Only runs of three or more are judged, because two rows are a coin toss
    and refusing them would refuse every two-row table in the repository.
    """
    for name, (recs, index) in colls.items():
        seq, keys = [], []
        for cells in rows:
            hit = None
            for i, rec in enumerate(recs):
                v = record_values(rec)
                if any(c in v for c in cells if c in index):
                    hit = i
                    break
            if hit is None:
                seq, keys = [], []
                continue
            seq.append(hit)
            keys.append(cells[0] if cells else "")
        if len(set(seq)) < 3 or len(seq) != len(set(seq)):
            continue
        if seq == sorted(seq) or keys == sorted(keys):
            continue
        return name, f"rows project {name} in neither declared nor sorted order: {seq[:6]}"
    return None


def page_binding(relpath: str, text: str, colls: dict):
    """A page named after a record must project THAT record, field by field.

    The row rule cannot see this one: a property table holds one label and one value per
    row and never two values to reconcile. The question that catches it is asked per
    FIELD — if the page shows some record's value for a field and not the value the
    record it is named after holds for that field, it is projecting the wrong record.
    """
    base = os.path.basename(relpath).rsplit(".", 1)[0]
    for name, (recs, _index) in colls.items():
        bound = [i for i, r in enumerate(recs)
                 if any(isinstance(v, str) and v == base for v in r.values())]
        if len(bound) != 1:
            continue
        mine = recs[bound[0]]
        for field in sorted(k for k, v in mine.items()
                            if isinstance(v, str) and len(v) >= MIN_SLOT):
            others = {r[field] for i, r in enumerate(recs)
                      if i != bound[0] and isinstance(r.get(field), str)
                      and len(r[field]) >= MIN_SLOT}
            intruder = sorted(v for v in others - {mine[field]} if v in text)
            if intruder and mine[field] not in text:
                return name, f"{field}={intruder[0]} (declared: {mine[field]})"
    return None


# ---------------------------------------------------------------------------
# CHECK 3 — declared completeness
# ---------------------------------------------------------------------------
def required_strings(entry: dict, repo: str) -> list:
    path = os.path.join(repo, entry["source"])
    if not os.path.isfile(path):
        return []
    if "regex" in entry:
        return sorted(set(re.findall(entry["regex"], read(path))))
    node = _walk_json_path(json.loads(read(path)), entry["collection"])
    if isinstance(node, dict):
        return sorted(node)
    return [rec[entry["field"]] if isinstance(rec, dict) else rec for rec in node]


def completeness(manifest: dict, surfaces: list, texts: dict, repo: str) -> list:
    gaps = []
    for entry in manifest.get("required_projections", []):
        targets = []
        for t in entry["surfaces"]:
            if t == "ALL_SURFACES":
                targets += surfaces
            elif isinstance(t, dict):
                targets += resolve(t, repo)      # a pointer, so the obligation names
            else:                                # no surface list this file re-authors
                targets.append(t)
        for value in required_strings(entry, repo):
            for relpath in targets:
                if relpath not in texts:
                    gaps.append((relpath, entry["source"], "surface absent"))
                elif value not in texts[relpath]:
                    gaps.append((relpath,
                                 f"{entry['source']}:{entry.get('collection', 'regex')}",
                                 value[:80]))
    return gaps


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------
def verify(decl_path: str, repo: str = REPO, report_only: bool = False) -> int:
    decl = json.loads(read(decl_path))
    owner = decl["owner"]
    try:
        authorities = resolve(decl["authorities"], repo)
        surfaces = sorted(set(resolve(decl["surfaces"], repo)))
    except UnsupportedPointer as bad:
        print(f"FAIL — {owner}: {bad}")
        print("       The declaration points at a surface list this resolver cannot read, so")
        print("       nothing about this adopter was measured. That fails closed.")
        return 1
    man_path = os.path.join(repo, decl["manifest"])
    if not os.path.isfile(man_path):
        print(f"FAIL — {owner}: the template manifest is absent: {decl['manifest']}")
        print("       Provenance cannot be established, so this fails closed.")
        return 1
    manifest = json.loads(read(man_path))
    corpus = declared_corpus(authorities, repo)
    colls = collections_of(authorities, repo)
    manifest["_corpus_sorted"] = sorted(corpus, key=len, reverse=True)
    manifest["_lengths"] = sorted({len(c) for c in corpus}, reverse=True)
    manifest["_allowed_lines"] = set(manifest.get("allowed_lines", []))
    manifest["_allowed_cells"] = set(manifest.get("allowed_cells", []))

    texts: dict = {}
    for relpath in surfaces:
        path = os.path.join(repo, relpath)
        if not os.path.isfile(path):
            print(f"FAIL — {owner}: declared surface absent: {relpath}")
            return 1
        text = read(path)
        if relpath.endswith(".mdc") and text.startswith("---"):
            parts = text.split("---\n", 2)
            text = parts[2] if len(parts) == 3 else text
        texts[relpath] = text

    gaps: list = []
    misbound: list = []
    checked = 0
    for relpath, text in texts.items():
        block: list = []
        raw: list = []
        for n, line in enumerate(text.split("\n"), 1):
            st = line.strip()
            if st.startswith("|"):
                raw.append(st)
                if not STRUCTURAL.match(st):
                    block.append(row_cells(st))
            elif raw:
                shape = table_shape(raw) or header_is_a_header(block, raw, colls)
                if shape:
                    misbound.append((relpath, n, shape))
                bad = table_order(block, colls)
                if bad:
                    misbound.append((relpath, n, bad[1]))
                block, raw = [], []
            checked += 1
            verdict, detail = classify(line, manifest, corpus)
            if verdict != "OK":
                gaps.append((relpath, n, line.strip()[:110], detail))
            s_line = line.strip()
            if not s_line.startswith("|") or STRUCTURAL.match(s_line):
                continue
            hit = row_integrity(row_cells(s_line), colls)
            if hit:
                misbound.append((relpath, n, "no declared record holds these together: "
                                 + " ; ".join(str(x)[:40] for x in hit)))
        if raw:
            shape = table_shape(raw) or header_is_a_header(block, raw, colls)
            if shape:
                misbound.append((relpath, 0, shape))
        if block:
            bad = table_order(block, colls)
            if bad:
                misbound.append((relpath, 0, bad[1]))
        bound = page_binding(relpath, text, colls)
        if bound:
            misbound.append((relpath, 0, f"page displays another record's value from "
                                         f"{bound[0]}: {str(bound[1])[:60]}"))
    missing = completeness(manifest, surfaces, texts, repo)

    print(f"{owner} — Universal Formal Independence (UFI) verification")
    print("-" * 66)
    print(f"  declared authorities    : {len(authorities)}")
    print(f"  surfaces checked        : {len(texts)}")
    print(f"  lines checked           : {checked}")
    print(f"  declared corpus strings : {len(corpus)}")
    print(f"  declared collections    : {len(colls)}")
    print(f"  manifest templates      : {len(manifest.get('allowed_lines', []))}")
    print(f"  [1] UNPROVENANCED lines : {len(gaps)}")
    print(f"  [2] MISBOUND records    : {len(misbound)}")
    print(f"  [3] MISSING projections : {len(missing)}")

    if gaps:
        print("-" * 66)
        print("  CHECK 1 — provenance: emitted text that traces to no declared source")
        seen = set()
        for relpath, n, line, detail in gaps:
            if line in seen and not report_only:
                continue
            seen.add(line)
            print(f"    {relpath}:{n}  [{detail}]")
            print(f"      {line}")
    if misbound:
        print("-" * 66)
        print("  CHECK 2 — record integrity: declared values against the wrong record")
        for relpath, n, detail in misbound[:20]:
            print(f"    {relpath}:{n}  {detail}")
        if len(misbound) > 20:
            print(f"    … and {len(misbound) - 20} more")
    if missing:
        print("-" * 66)
        print("  CHECK 3 — completeness: a declared obligation the surface does not carry")
        for relpath, source, value in missing[:20]:
            print(f"    {relpath}  missing from {source}: {value}")
        if len(missing) > 20:
            print(f"    … and {len(missing) - 20} more")

    if report_only:
        return 0
    if gaps or misbound or missing:
        print("-" * 66)
        print(f"VERIFIER FAILED — {owner}'s surfaces are not a faithful projection.")
        print("A generator may not mint normative text, re-pair declared values, or drop a")
        print("declared obligation. Either the output is wrong, or the change belongs in")
        print(f"{decl['manifest']} as a reviewed entry.")
        return 1
    print("-" * 66)
    print("VERIFIER PASSED — every line traces to a declared source, every declared")
    print("record is projected whole, and every declared obligation is carried.")
    return 0


#: Where adoptions live. A directory rather than a list in this file: adopting the
#: framework is adding a declaration, and a framework that must be edited to admit its
#: next adopter is not a framework.
ADOPTIONS = os.path.join(REPO, "00-BOOK", "DATA", "independence")


def verify_all(repo: str = REPO, report_only: bool = False) -> int:
    """Every declared adopter, fail-closed on the first that refuses.

    The count is deliberately not asserted anywhere. A number here would make adopting
    the framework a documentation edit in three files, and a stale number is a claim
    about coverage that nothing measured.
    """
    decls = sorted(f for f in os.listdir(ADOPTIONS)
                   if f.endswith(".json") and "template-manifest" not in f)
    if not decls:
        print("FAIL — no independence declaration is present. The framework would pass by")
        print("       verifying nothing, which is the failure it exists to prevent.")
        return 1
    worst = 0
    for f in decls:
        rc = verify(os.path.join(ADOPTIONS, f), repo, report_only)
        worst = worst or rc
        print()
    print(f"UFI — {len(decls)} declared adopter(s) verified.")
    return worst


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="ufi.py",
        description="Universal Formal Independence verification of a producer's surfaces.")
    ap.add_argument("declaration", nargs="?",
                    help="path to an independence declaration (omit with --all)")
    ap.add_argument("--all", action="store_true",
                    help="Verify every declared adopter under 00-BOOK/DATA/independence/.")
    ap.add_argument("--report", action="store_true",
                    help="List every finding and exit 0 (population aid).")
    a = ap.parse_args(argv)
    if a.all:
        return verify_all(REPO, a.report)
    if not a.declaration:
        ap.error("give a declaration, or --all")
    return verify(a.declaration if os.path.isabs(a.declaration)
                  else os.path.join(REPO, a.declaration), REPO, a.report)


if __name__ == "__main__":
    sys.exit(main())
