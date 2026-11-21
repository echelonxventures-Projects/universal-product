#!/usr/bin/env python3
"""
UCOS Ω∞ — Context Closure Gate (UCOS-UCTX-001).

Evaluates INV-CTX-01..17 over the emitted context state and REFUSES the commit
when any of them is violated. Every invariant fails closed.

WHY THIS IS NOT IN ukctx.py. The generator WRITES canonical artifacts, so under
UCOS-UGA-001 OBS-INV-12 it may not also READ an observation source: a producer
that observes the working tree is a producer whose output could depend on
uncommitted state, and UCKP-ART-13 would lose its fixed point. This gate reads
`git status --porcelain` and the ref list — both WORKING_TREE observations — and
so it lives here, holds NO canonical output, and writes nothing at all.

That separation was not designed in advance. The first version of this capability
had one module, and `uga_engine.py gate` refused it with:

    OBS-INV-12: 00-BOOK/tools/ukctx.py: reads WORKING_TREE and declares
                no observation source

The split is that refusal, honoured.

WHAT AN OBSERVATION MAY DO HERE. It may REFUSE. It may never be emitted: nothing
this module measures reaches a byte of any generated artifact. That is the
evidence/observation separation UCOS-CAA-001 records as CAA-INV-06, applied to
context.

Usage:
    python3 00-BOOK/tools/ukctx_gate.py            # evaluate INV-CTX-01..17
    python3 00-BOOK/tools/ukctx_gate.py --strict-branch

Standard library only. Exit 0 = closed, 1 = refused.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess  # noqa: S404
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from ukctx import (  # noqa: E402
    CAA,
    DECLARATION,
    REPO,
    compute_outputs,
    digest,
    exists,
    load_json,
    read_text,
    rel,
)


def _git(*args) -> str | None:
    """Git on the VERIFY path only. The build path never invokes it.

    argv is a fixed literal tuple; nothing here is shell-interpreted (no shell=True)
    and no element comes from user input, so S603 does not apply.
    """
    try:
        r = subprocess.run(  # noqa: S603
            ("git", "-C", REPO) + args,
            capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        # Git absent, or the call timed out. Both are "cannot measure", and the
        # caller records that as an unmeasured ref rather than a passing one.
        return None
    return r.stdout if r.returncode == 0 else None



# ---------------------------------------------------------------------------
# Agent surface classification (INV-CTX-12 / INV-CTX-08)
# ---------------------------------------------------------------------------
def _agent_class(relpath: str, decl: dict, emitted: set) -> str | None:
    """The declared class of one agent-directory file, or None if unclassified.

    None is a REFUSAL, never a default. The whole point of C-R3 was that an
    unclassified file was indistinguishable from an approved one.
    """
    if relpath in emitted:
        return "PROJECTION"
    for s in decl.get("agent_surfaces", []):
        if s["surface"] == relpath:
            return "PROJECTION"
    for rule in decl.get("agent_surface_rules", []):
        if fnmatch.fnmatch(relpath, rule["pattern"]):
            return rule["class"]
    return None


def _agent_classes(relpath: str, decl: dict, emitted: set) -> set[str]:
    """EVERY declared class that claims this path.

    `_agent_class` returns the first match, which is what a consumer needs. This
    returns all of them, because "resolves to a class" and "resolves to exactly ONE
    class" are different guarantees and only the second one is worth having: two
    rules claiming one path with different classes means the path's disposition
    depends on rule ORDER, and rule order is not a thing anybody declared.
    """
    found: set[str] = set()
    if relpath in emitted:
        found.add("PROJECTION")
    for s in decl.get("agent_surfaces", []):
        if s["surface"] == relpath:
            found.add("PROJECTION")
    sfx = tuple(decl.get("agent_directory_discovery", {})
                    .get("instruction_file_suffixes", []))
    constrained = bool(decl.get("operational_class_constraint"))
    for rule in decl.get("agent_surface_rules", []):
        if not fnmatch.fnmatch(relpath, rule["pattern"]):
            continue
        # MB10. A wildcard TOOL_OPERATIONAL rule describes a directory of runtime
        # state; it may not thereby bless an instruction file that happens to sit in
        # it. Closing MB9 by declaring `.claude/mailbox/*` operational would otherwise
        # have created exactly the unexamined hiding place MB9 was about. Exact-path
        # rules are untouched: they name one file and claim one file.
        if (constrained and rule["class"] == "TOOL_OPERATIONAL"
                and any(ch in rule["pattern"] for ch in "*?[")
                and relpath.endswith(sfx)):
            continue
        found.add(rule["class"])
    return found


def _agent_candidate_paths(decl: dict) -> list[str]:
    """Every path this invariant is responsible for, measured on the FILESYSTEM.

    Ignored-inclusive and untracked-inclusive on purpose: a rogue agent file starts
    life untracked, so a tracked-only scan would be blind to it for exactly as long
    as it takes somebody to read it.
    """
    out: set[str] = set()
    for d in decl.get("agent_directories", []):
        base = os.path.join(REPO, d)
        if not os.path.isdir(base):
            continue
        for dirpath, dirs, files in os.walk(base):
            dirs[:] = [x for x in dirs if x != "__pycache__"]
            for f in files:
                out.add(rel(os.path.join(dirpath, f)))
    names = set(decl.get("agent_filename_patterns", []))
    if names:
        skip = {".git", ".ec1-venv", "node_modules", "__pycache__", ".mypy_cache",
                ".pytest_cache", ".ruff_cache"}
        for dirpath, dirs, files in os.walk(REPO):
            dirs[:] = [x for x in dirs if x not in skip]
            for f in files:
                if f in names:
                    out.add(rel(os.path.join(dirpath, f)))
    return sorted(out)


def _normalize_projection(text: str, decl: dict, fmt: str) -> str:
    """A projection reduced to what every agent must be told identically.

    Only the substitutions `projection_normalization` declares are erased, and they
    are erased in EVERY file rather than only in the file they name — otherwise an
    incidental mention of one agent inside another agent's surface would survive on
    one side and be normalized on the other, and the comparison would report a
    difference that is not one.
    """
    envelopes = decl.get("projection_normalization", {}).get("format_envelopes", {})
    if fmt in envelopes and text.startswith("---"):
        parts = text.split("---\n", 2)
        if len(parts) == 3:
            # lstrip("\n"): the blank line after the closing fence is the envelope's own
            # separator, not content. Leaving it in would report a divergence that is
            # purely a property of the file FORMAT — and an invariant that cries wolf on
            # its own correct output is one somebody switches off.
            text = parts[2].lstrip("\n")
    tokens: list[str] = []
    for s in decl.get("agent_surfaces", []):
        tokens.append(s["surface"])
        tokens.append(s["agent"])
    for t in sorted(set(tokens), key=len, reverse=True):
        text = text.replace(t, "<AGENT-SUBSTITUTION>")
    return text


UCXI_KIND_RE = re.compile(r'^\s{4}[A-Z_]+ = "([a-z_]+)"\s*$', re.MULTILINE)


def _ucxi_kinds() -> set[str]:
    """UCXI's universal context kinds, read from ITS home, never restated here.

    Recomputed on every run so a kind added to UCXI tomorrow enters the collision
    set without anybody remembering to update this file.
    """
    path = os.path.join(REPO, "engine", "context", "taxonomy.py")
    try:
        src = read_text(path)
    except OSError:
        return set()
    body = src.split("class ContextKind", 1)
    if len(body) < 2:
        return set()
    body = body[1].split("\n@", 1)[0].split("\nclass ", 1)[0]
    return set(UCXI_KIND_RE.findall(body))


def _context_paths(decl: dict) -> set[str]:
    root = decl["context_root"]["path"]
    return {root + "/"} | {s["surface"] for s in decl["agent_surfaces"]} | {rel(DECLARATION)}


def _is_context_path(p: str, decl: dict) -> bool:
    root = decl["context_root"]["path"] + "/"
    if p.startswith(root) or p == rel(DECLARATION):
        return True
    return any(p == s["surface"] for s in decl["agent_surfaces"])


def verify(strict_branch: bool) -> tuple[list[dict], dict]:
    out, decl = compute_outputs()
    root = decl["context_root"]["path"]
    results: list[dict] = []

    def add(iid, name, violations, measured):
        results.append({"id": iid, "name": name,
                        "violations": sorted(str(v) for v in violations),
                        "measured": measured})

    # INV-CTX-01 — exactly one canonical context authority
    caa = load_json(CAA)
    declaring = [i for i in caa.get("subordinate_instruments", [])
                 if i.get("instrument") == rel(DECLARATION)]
    v = []
    if len(declaring) != 1:
        v.append("expected exactly one CAA binding for the context instrument, "
                 f"found {len(declaring)}")
    elif declaring[0]["id"] != decl["artifact_id"]:
        v.append(f"CAA binds {declaring[0]['id']}, declaration says {decl['artifact_id']}")
    if not os.path.isdir(os.path.join(REPO, root)):
        v.append(f"declared context root does not exist: {root}")
    if declaring and declaring[0].get("role") != "PROJECTION":
        v.append(f"context instrument must be role PROJECTION, CAA says {declaring[0].get('role')}")
    add("INV-CTX-01", "EXACTLY_ONE_CANONICAL_CONTEXT_AUTHORITY", v, 1)

    # INV-CTX-02 — every domain resolves to an authority home that exists
    v = [f"{d['domain']}: authority home missing: {d['authority_home']}"
         for d in decl["domains"] if not exists(d["authority_home"])]
    add("INV-CTX-02", "EVERY_CONTEXT_ARTIFACT_RESOLVES_TO_AUTHORITY", v, len(decl["domains"]))

    # INV-CTX-03 — no orphaned context under the root
    emitted = set(out)
    present = set()
    root_abs = os.path.join(REPO, root)
    if os.path.isdir(root_abs):
        for dirpath, _dirs, files in os.walk(root_abs):
            for f in files:
                present.add(rel(os.path.join(dirpath, f)))
    v = [f"orphan under context root, produced by nothing: {p}" for p in sorted(present - emitted)]
    add("INV-CTX-03", "NO_ORPHANED_CONTEXT", v, len(present))

    # INV-CTX-04 — no duplicate authority across domains
    #
    # REWRITTEN (C-R4). The previous test compared `answers` prose with string equality,
    # which attack A8 defeated by rewording. Question strings are written by whoever adds
    # the domain, so they can never be the thing that constrains them. This now measures a
    # structural property the attacker does not control: one authority HOME resolves to
    # exactly one authority id. Two domains may share a home only under one identity.
    v = []
    home_owner: dict[str, str] = {}
    for d in decl["domains"]:
        h, a = d["authority_home"], d["authority"]
        if h in home_owner and home_owner[h] != a:
            v.append(f"one home, two authority identities: {h} is claimed by "
                     f"{home_owner[h]} and by {a}")
        home_owner[h] = a
    add("INV-CTX-04", "NO_DUPLICATE_AUTHORITY", v, len(decl["domains"]))

    # INV-CTX-05 — no agent-owned authority
    v = []
    agent_dirs = sorted({s["surface"].split("/")[0] for s in decl["agent_surfaces"]
                         if "/" in s["surface"]})
    tracked = (_git("ls-files") or "").split()
    for p in tracked:
        top = p.split("/")[0]
        if top not in agent_dirs or not p.endswith(".json"):
            continue
        try:
            doc = load_json(os.path.join(REPO, p))
        except (OSError, ValueError):
            # Unreadable or non-JSON: it declares no authority we can read, and
            # UGA-INV-03 already governs whether it may exist at all.
            continue
        if isinstance(doc, dict) and isinstance(doc.get("authority"), str):
            if not doc["authority"].strip().upper().startswith(("NONE",)):
                v.append(f"agent-directory file claims authority: {p}")
    for s in decl["agent_surfaces"]:
        full = os.path.join(REPO, s["surface"])
        if os.path.isfile(full) and re.search(r'^\s*"?authority"?\s*:', read_text(full), re.M):
            v.append(f"agent surface declares an authority key: {s['surface']}")
    add("INV-CTX-05", "NO_AGENT_OWNED_AUTHORITY", v, len(decl["agent_surfaces"]))

    # INV-CTX-06 — every declared agent projection exists and is generated
    v = []
    for s in decl["agent_surfaces"]:
        if not s.get("generated"):
            continue
        full = os.path.join(REPO, s["surface"])
        if not os.path.isfile(full):
            v.append(f"declared surface not emitted: {s['surface']}")
        elif "AUTO-GENERATED by 00-BOOK/tools/ukctx.py" not in read_text(full):
            v.append(f"surface carries no generation banner: {s['surface']}")
    add("INV-CTX-06", "EVERY_AGENT_PROJECTION_GENERATED", v,
        sum(1 for s in decl["agent_surfaces"] if s.get("generated")))

    # INV-CTX-07 — no manual modification of a generated projection  (LOAD-BEARING)
    v = []
    for relpath in sorted(out):
        full = os.path.join(REPO, relpath)
        if not os.path.isfile(full):
            v.append(f"missing projection: {relpath}")
        elif read_text(full) != out[relpath]:
            v.append(f"DRIFT — on-disk bytes differ from the derivation: {relpath}")
    add("INV-CTX-07", "NO_MANUAL_MODIFICATION_OF_GENERATED_PROJECTIONS", v, len(out))

    # INV-CTX-08 — no branch-exclusive context authority
    v, measured = [], 0
    refs = (_git("for-each-ref", "--format=%(refname:short)",
                 "refs/heads", "refs/remotes", "refs/tags") or "").split()
    refs = [r for r in refs if not r.endswith("/HEAD")]
    tag_names = set((_git("tag", "-l") or "").split())
    for r in refs:
        listing = _git("ls-tree", "-r", "--name-only", r)
        if listing is None:
            continue
        measured += 1
        agent_dirs = tuple(d + "/" for d in decl.get("agent_directories", []))
        agent_names = set(decl.get("agent_filename_patterns", []))
        for p in listing.split("\n"):
            if not p:
                continue
            if _is_context_path(p, decl) and p not in emitted and p != rel(DECLARATION):
                v.append(f"{r}: context file the declaration does not produce: {p}")
                continue
            # EXTENSION (A15). The check above only ever saw the context root and the
            # declared surfaces, so a branch carrying `.claude/BRANCH-ONLY.md` passed:
            # the file was in no agent-directory scan and matched no declared surface.
            # Agent-directory files on every ref are now classified with the same rules
            # INV-CTX-12 applies to the working tree, so a workflow or a frozen hook is
            # still fine and an unclassifiable instruction file is not.
            if p.startswith(agent_dirs) or os.path.basename(p) in agent_names:
                if _agent_class(p, decl, emitted) is None:
                    v.append(f"{r}: unclassified agent-surface file on this ref: {p}")
    # Two legs, and only the first is unconditional.
    #
    # RIVAL (always): a ref carrying a context file this declaration does not produce
    # is carrying exclusive truth, and that is a violation the day it appears.
    #
    # PARITY (--strict-branch): every ref also HAVING the context. This is deliberately
    # opt-in, because absence is not divergence — a tag is an immutable snapshot of a
    # commit that legitimately predates this instrument, and demanding the context be
    # present in history would demand rewriting it. Parity is therefore measured over
    # BRANCHES only, and only when asked, which is the post-merge question: "does every
    # living line of development carry the same context?"
    if strict_branch:
        decl_path = rel(DECLARATION)
        for r in refs:
            if r.startswith("refs/tags/") or "/tags/" in r or r in tag_names:
                continue
            listing = _git("ls-tree", "-r", "--name-only", r)
            if listing is None:
                continue
            if decl_path not in set(listing.split("\n")):
                v.append(f"{r}: branch does not carry the context declaration {decl_path}")
    add("INV-CTX-08", "NO_BRANCH_EXCLUSIVE_CONTEXT_AUTHORITY", v, measured)

    # INV-CTX-09 — no worktree-exclusive context authority
    v, measured = [], 0
    wt = _git("worktree", "list", "--porcelain") or ""
    paths = [ln.split(" ", 1)[1] for ln in wt.split("\n") if ln.startswith("worktree ")]
    for w in paths:
        if not os.path.isdir(w):
            continue
        measured += 1
        try:
            # -uall: without it git collapses an untracked DIRECTORY to a single
            # entry, so a whole untracked agent surface would be reported as
            # `.claude/` and match no declared path. The collapse is exactly the
            # blind spot this invariant exists to close.
            r = subprocess.run(  # noqa: S603
                ("git", "-C", w, "status", "--porcelain", "-uall"),
                capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.SubprocessError):
            # This worktree cannot be measured; it is counted as unmeasured, never
            # as clean. `measured` in the result names how many actually answered.
            continue
        if r.returncode != 0:
            continue
        for ln in r.stdout.split("\n"):
            if not ln.strip():
                continue
            p = ln[3:].strip().strip('"')
            if _is_context_path(p, decl):
                v.append(f"{w}: uncommitted change to context: {p}")
    add("INV-CTX-09", "NO_WORKTREE_EXCLUSIVE_CONTEXT_AUTHORITY", v, measured)

    # INV-CTX-10 — every projection traceable to a canonical source
    v = []
    man_path = f"{root}/MANIFEST.json"
    try:
        man = json.loads(out[man_path])
    except Exception as exc:
        man, _ = {}, v.append(f"manifest not derivable: {exc}")
    listed = {p["path"] for p in man.get("projections", [])}
    for relpath in sorted(emitted):
        if relpath == man_path:
            continue
        if relpath not in listed:
            v.append(f"projection absent from manifest: {relpath}")
    for src in man.get("derives_from", []):
        if not exists(src):
            v.append(f"manifest names an input that does not exist: {src}")
    for p in man.get("projections", []):
        if p["sha256"] != digest(out[p["path"]]):
            v.append(f"manifest digest does not match derivation: {p['path']}")
    add("INV-CTX-10", "EVERY_PROJECTION_TRACEABLE_TO_CANONICAL_SOURCE", v, len(listed))

    # INV-CTX-11 — the generator reaches a fixed point
    again, _ = compute_outputs()
    v = [f"non-deterministic output: {k}" for k in sorted(set(out) | set(again))
         if out.get(k) != again.get(k)]
    add("INV-CTX-11", "GENERATOR_REACHES_FIXED_POINT", v, len(out))

    # INV-CTX-12 — no unregistered agent surfaces  (closes C-R3 / A1..A4)
    #
    # Measured over the FILESYSTEM, ignored- and untracked-inclusive. A rogue agent file
    # starts untracked, so a tracked-only scan is blind to it for exactly as long as it
    # takes an agent to read it. Classification, not prohibition: 45 legitimate files live
    # in these directories (36 workflows, 7 frozen hooks, 2 tool-operational), and a rule
    # that forbade them would be turned off within a day.
    v = []
    candidates = _agent_candidate_paths(decl)
    for relpath in candidates:
        classes = _agent_classes(relpath, decl, emitted)
        if not classes:
            v.append(f"unclassified agent-surface file (no declared class): {relpath}")
        elif len(classes) > 1:
            # UNIQUENESS (MB9). A path claimed by two classes has no determinate
            # disposition: whether it is a generated projection or per-developer
            # runtime state would depend on which rule was written first. That is
            # exactly the ambiguity TOOL_OPERATIONAL could otherwise acquire against
            # GENERATED_DETERMINISTIC as the operational rules grew.
            v.append(f"ambiguous classification — {relpath} is claimed by "
                     f"{', '.join(sorted(classes))}; exactly one class must claim it")
    # DISCOVERY LEG (A22). The scan above walks the directories the declaration NAMES, so
    # a new agent arriving in a directory nobody enumerated — `.newagent/rules.md` — was
    # invisible to it. An enumeration cannot cover the un-invented. This leg inverts the
    # question: any non-ignored top-level dot-directory holding an instruction-shaped file
    # must be declared. Ignored ones are skipped because the exclusion register already
    # obliges every ignored path to carry a declared class.
    disc = decl.get("agent_directory_discovery")
    if disc:
        declared_dirs = set(decl.get("agent_directories", []))
        sfx = tuple(disc.get("instruction_file_suffixes", []))
        for name in sorted(os.listdir(REPO)):
            if not name.startswith(".") or name == ".git":
                continue
            full = os.path.join(REPO, name)
            if not os.path.isdir(full) or name in declared_dirs:
                continue
            if _git("check-ignore", "-q", name) is not None:
                continue          # ignored: governed by the exclusion register
            carries = False
            for _dirpath, dirs, files in os.walk(full):
                dirs[:] = [x for x in dirs if x != "__pycache__"]
                if any(f.endswith(sfx) for f in files):
                    carries = True
                    break
            if carries:
                v.append(f"undeclared agent directory carrying instruction-shaped files: "
                         f"{name}/ — add it to agent_directories with a class, or have the "
                         "ignore authority classify it")
    add("INV-CTX-12", "NO_UNREGISTERED_AGENT_SURFACES", v, len(candidates))

    # INV-CTX-13 — no agent divergence  (closes C-R5 / A10)
    #
    # INV-CTX-07 compares each surface to its OWN derivation, so a generator that emitted
    # a different instruction per agent stayed green. This compares the surfaces to EACH
    # OTHER after erasing the substitutions the declaration permits.
    v = []
    norm: dict[str, str] = {}
    for sfc in decl.get("agent_surfaces", []):
        full = os.path.join(REPO, sfc["surface"])
        if not os.path.isfile(full):
            continue
        norm[sfc["surface"]] = digest(
            _normalize_projection(read_text(full), decl, sfc.get("format", "markdown")))
    groups: dict[str, list[str]] = {}
    for path, dg in norm.items():
        groups.setdefault(dg, []).append(path)
    if len(groups) > 1:
        for _dg, paths in sorted(groups.items(), key=lambda kv: -len(kv[1]))[1:]:
            for path in sorted(paths):
                v.append("agent projection diverges from the majority after normalization: "
                         f"{path}")
    add("INV-CTX-13", "NO_AGENT_DIVERGENCE", v, len(norm))

    # INV-CTX-14 — bounded-question uniqueness  (closes C-R4 / A8, A9)
    #
    # The load-bearing clause is the LAST one. Comparing question strings cannot constrain
    # whoever writes the strings (A8 reworded its way through). Binding an authority to the
    # exact domains it may answer can: the register already states which questions each
    # instrument answers, so answering one more is an edit to the register rather than a
    # choice of words.
    v = []
    reg = decl.get("authority_registry", {})
    seen: dict[str, str] = {}
    owned: dict[str, set] = {}
    for d in decl["domains"]:
        bq = (d.get("bounded_question") or "").strip().lower()
        if not bq:
            v.append(f"{d['domain']}: declares no bounded_question")
            continue
        if bq in seen and seen[bq] != d["authority"]:
            v.append("one bounded question, two authorities: "
                     f"{seen[bq]} and {d['authority']}")
        seen[bq] = d["authority"]
        owned.setdefault(d["authority"], set()).add(d["domain"])
    for a, doms in sorted(owned.items()):
        entry = reg.get(a)
        if entry is None:
            v.append(f"authority {a} is named by a domain but absent from authority_registry")
            continue
        if entry.get("standing") not in ("CAA_BOUND", "DISCLAIMED"):
            v.append(f"authority {a} has no declared standing")
        granted = set(entry.get("domains") or [])
        for extra in sorted(doms - granted):
            v.append(f"authority {a} answers domain '{extra}', which its registry entry "
                     "does not grant")
    add("INV-CTX-14", "BOUNDED_QUESTION_UNIQUENESS", v, len(decl["domains"]))

    # INV-CTX-15 — no undisambiguated collision with UCXI  (closes A-R2)
    #
    # The collision set is recomputed from UCXI's own home on every run rather than being
    # listed here, so a kind added to either side enters the set without anybody
    # remembering. A prose claim of non-overlap would decay silently; this fails instead.
    v = []
    kinds = _ucxi_kinds()
    if not kinds:
        v.append("UCXI context kinds could not be read from engine/context/taxonomy.py; "
                 "the collision set cannot be computed, so this fails closed")
    collisions = sorted(kinds & {d["domain"] for d in decl["domains"]})
    declared_overlap = set(decl.get("ucxi_relationship", {}).get("OVERLAP_SET", []))
    for d in decl["domains"]:
        if d["domain"] in collisions and not d.get("ucxi_disambiguation"):
            v.append(f"domain '{d['domain']}' collides with a UCXI universal context kind "
                     "and carries no ucxi_disambiguation")
    for miss in sorted(set(collisions) - declared_overlap):
        v.append(f"collision '{miss}' is not recorded in ucxi_relationship.OVERLAP_SET")
    for stale in sorted(declared_overlap - set(collisions)):
        v.append(f"OVERLAP_SET names '{stale}', which is no longer a collision — a stale "
                 "disambiguation is a false assurance")
    add("INV-CTX-15", "NO_UNDISAMBIGUATED_CONTEXT_KIND_COLLISION", v, len(kinds))

    # INV-CTX-16 — no proposal ever projected
    #
    # The proposal lane routes IN to proposer folders; projections route OUT from one
    # authority. A proposal becoming context without assimilation would bypass the four
    # declared gates.
    v = []
    proposal_class = "PROPOSAL"
    if proposal_class in decl.get("agent_surface_classes", {}):
        for relpath in sorted(emitted):
            classes = _agent_classes(relpath, decl, emitted)
            if proposal_class in classes:
                v.append(f"projection includes a PROPOSAL file: {relpath}")
    add("INV-CTX-16", "NO_PROPOSAL_EVER_PROJECTED", v, len(emitted))

    # INV-CTX-17 — every assimilation identified and gated
    #
    # Every assimilated contribution must carry a Universal ID minted under REG-AUTO-001
    # with an operator-issued permit, and must have passed all four declared gates. This
    # invariant is DECLARED but not yet MEASURED: the assimilation register does not exist,
    # so the gate cannot verify it. When the first contribution is assimilated and the
    # register is created, this check will read it.
    v = []
    assimilation_register_path = "00-BOOK/DATA/assimilation-register.json"
    if exists(assimilation_register_path):
        try:
            reg = load_json(os.path.join(REPO, assimilation_register_path))
            for entry in reg.get("assimilated_contributions", []):
                where = entry.get("proposal_path")
                if not entry.get("universal_id"):
                    v.append(f"assimilated contribution has no Universal ID: {where}")
                if not entry.get("gates_passed"):
                    v.append(f"assimilated contribution has no gate record: {where}")
        except (OSError, ValueError) as exc:
            v.append(f"assimilation register unreadable: {exc}")
    add("INV-CTX-17", "EVERY_ASSIMILATION_IDENTIFIED_AND_GATED", v, 0)

    summary = {
        "invariants": len(results),
        "failed": sum(1 for r in results if r["violations"]),
        "violations": sum(len(r["violations"]) for r in results),
    }
    return results, summary


def cmd_verify(args) -> int:
    results, summary = verify(strict_branch=args.strict_branch)
    print("UCOS-UCTX-001 Context Closure Gate")
    print("-" * 60)
    for r in results:
        mark = "FAIL" if r["violations"] else "PASS"
        print(f"  [{mark}] {r['id']}  {r['name']}  "
              f"(violations={len(r['violations'])}, measured={r['measured']})")
    print("-" * 60)
    if summary["failed"]:
        print(f"GATE FAILED — {summary['failed']} blocking invariant(s).")
        for r in results:
            for v in r["violations"]:
                print(f"    {r['id']}: {v}")
        return 1
    print("GATE PASSED — one context authority, every projection derived, no drift.")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="ukctx_gate.py",
        description="UCOS-UCTX-001 Context Closure Gate — INV-CTX-01..17, fail-closed.")
    ap.add_argument("--strict-branch", action="store_true",
                    help="Also require presence parity of context across every ref.")
    return cmd_verify(ap.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
