"""INV-AGN-02 — the direct-caller ratchet for a substitutable facility.

WHY A RATCHET AND NOT A BAN. The repository declares version control git-bound with a
constitutional reason (adr/0039): `git ls-files` IS the eligibility boundary and `git archive`
DEFINES pristine-clone certification. So this does not forbid git — it forbids reaching PAST the
provider for a question the provider answers, which is a different claim and the only one the
evidence supports.

WHAT MADE THIS MEASURABLE. Until the capability dispatch landed, the provider declared five
capabilities and delivered one, so a caller needing a content hash or the working tree had no
choice but to invoke the tool directly. Counting those as bypasses would have been counting the
provider's own gap against its callers. Now every declared capability has a delivery, so a direct
invocation is a choice, and this number is the count of those choices.

THE NUMBER MAY ONLY FALL. A rise means a new module reached past a facility that could have
answered it, which is exactly how nine execution adapters accumulated behind a contract nothing
could fail.
"""

from __future__ import annotations

import ast
import json
import os
import pathlib

#: Modules permitted to invoke the tool directly, each for a stated reason.
DECLARED_DIRECT: dict[str, str] = {
    "engine/omega_infinite/git_provider.py": (
        "IS the provider. Its whole purpose is to be the one place the tool is invoked."
    ),
    "platform/repository_intelligence/contamination.py": (
        "ASKS QUESTIONS THAT ARE VERSION-CONTROL CONCEPTS, NOT DISCOVERY CONCEPTS. It needs "
        "ignored paths with their status codes (`status --porcelain --ignored=matching`) and "
        "WHICH IGNORE RULE matched each path (`check-ignore`). A discovery provider enumerates "
        "content; neither of these is content. Declaring capabilities for them would create "
        "abstractions with exactly one implementation on an axis adr/0039 declares git-bound for "
        "a constitutional reason, which is the bar adr/0039 itself sets — an abstraction with one "
        "implementation is an assumption — and the checklist-driven abstraction adr/0021 warns "
        "against. Making this count fall that way would corrupt the measurement it reports. Its "
        "one `ls-files` call site could migrate alone, and that was deliberately not done: a "
        "partial migration leaves the module a direct caller anyway, so it would buy no fall and "
        "cost a second way of asking the same question."
    ),
    "engine/execution_environment/discovery.py": (
        "LOCATES THE REPOSITORY ROOT, which is the step that makes a provider constructible. A "
        "provider is rooted at a path before it can answer anything about that path, so asking "
        "one where its own root is has no answer to give. This is a bootstrap and not a bypass: "
        "there is no abstraction to route through until this call has returned."
    ),
    "engine/omega_infinite/compat.py": (
        "Demonstrates that the provider reproduces the pre-provider population exactly. It must "
        "invoke both sides to compare them, and a comparison that used the provider for both "
        "would prove nothing."
    ),
}

#: Where the scan's roots come from. UCON-000001 already declares the source roots its own
#: closure audit walks, and a second tuple here would be a second answer to one question
#: (UCKP-ART-03) as well as a closed enumeration ISD-L-01 counts. Reading the declared list
#: removes both: the roots are DATA, so admitting a new source tree is an edit to the
#: declaration and never to this module.
#:
#: MEASURED BEFORE ADOPTING IT: the declared list is broader than the tuple it replaced — eight
#: roots against five — and the direct-caller count is 19 under both. Widening the scan changed
#: no verdict, which is what made the replacement safe rather than merely tidier.
#: The call names that actually start a process. A module that merely NAMES the tool — in a
#: declaration, a docstring or a persistence binding — spawns nothing, and counting it would put
#: entries in the ratchet that no migration could ever remove.
_SPAWNS = frozenset({"run", "Popen", "check_output", "call", "check_call", "getoutput"})

UCON_DECLARATION = "00-MASTER/UCON-000001/ucon-declaration.json"


def roots(base: pathlib.Path) -> tuple[str, ...]:
    """The source roots to scan, read from the declaration that already names them."""
    document = json.loads((base / UCON_DECLARATION).read_text(encoding="utf-8"))
    declared = document.get("audit", {}).get("roots")
    if not isinstance(declared, list) or not declared:
        raise RuntimeError(f"{UCON_DECLARATION} declares no audit roots to scan")
    return tuple(str(entry) for entry in declared)


#: THE BASELINE IS MEASURED, NOT ASPIRED TO. Setting this to 0 while nineteen modules invoke the
#: tool would be a ceiling nothing could satisfy, and a gate that always fails is as useless as one
#: that never can — the defect this session measured on the execution axis, inverted. The number is
#: what the repository actually holds, and it may only fall.
#:
#: WHY IT IS MEANINGFUL NOW AND WAS NOT BEFORE. Until the capability dispatch landed, a caller
#: needing a content hash, an owner or the working tree had no alternative: the provider declared
#: those capabilities and delivered none of them. Counting such a caller as a bypass would have
#: charged the provider's gap to its callers. Every declared capability now has a delivery, so a
#: direct invocation is a CHOICE, and this counts choices.
#:
#: MOVEMENTS
#:   5 -> 4     (-1)  platform/repository_intelligence/substrate.py. Its two wrappers took
#:                     arbitrary argv and returned "" on any failure, so every question went to
#:                     the tool directly and every failure looked exactly like an empty answer.
#:                     The three questions it actually asks are each a declared capability now.
#:                     THIS MODULE WAS LISTED AS "NEEDS CONFIG" AND NEVER DID. That came from
#:                     matching the string "config" in `"config": self.config.to_dict()` — a dict
#:                     key, not a subcommand. The module was fully covered before this commit and
#:                     the estimate said otherwise, which is the same text-matching error this log
#:                     has now recorded five times.
#:                     Population proven identical first: 7,133 paths both ways.
#:
#:   6 -> 5     (-1)  infrastructure/integration_realize.py, on REVISION_IDENTITY — the
#:                     capability the previous entry named as missing and predicted would unblock
#:                     four. It answers position rather than content: which line of development,
#:                     the abbreviated revision, whether this is a working copy, the upstream it
#:                     tracks, whether a reference resolves, and where two references diverged.
#:                     Every field answered or empty, never absent, so a caller can tell "no
#:                     revision" from "the provider declined to say".
#:                     One behaviour was restated rather than copied: `clean` was
#:                     `porcelain == ""`, true when the tool printed nothing. It is now the union
#:                     of untracked and modified being empty — the same condition expressed in
#:                     terms of what it means, and verified identical against the original.
#:
#:   7 -> 6     (-1)  platform/repository_operations/stages.py, and it took THREE NEW
#:                     CAPABILITIES to move one caller — CHANGE_SET, REVISION_HISTORY and
#:                     REVISION_METADATA, each answering one question the provider declared it
#:                     could not answer before.
#:                     THE ESTIMATE THAT PRECEDED THIS WAS WRONG, and the correction is the
#:                     useful record. "One history capability unblocks four" was measured from
#:                     the subcommands each module names, not from every call site each module
#:                     makes. Enumerating the call sites showed four of the five also ask
#:                     `rev-parse --abbrev-ref HEAD` for the current branch, three ask
#:                     `rev-parse --short`, and one each ask merge-base, @{u} and
#:                     --is-inside-work-tree. Those are a REVISION IDENTITY cluster, distinct
#:                     from history, and until it exists those four modules keep a call with no
#:                     home — so they stay direct callers however much else is migrated.
#:                     A module falls only when EVERY question it asks has somewhere to go.
#:
#:   10 -> 7    (-3)  The three that were migratable and had been left. All proven
#:                     population-identical before the swap, which is the bar every migration
#:                     here has met: engine/enforcement_closure/discovery.py at 7,133 tracked
#:                     paths, engine/universal_discovery/discovery.py at 2,292 Python paths, and
#:                     engine/ledger_authority's git_head against a live rev-parse.
#:                     THE LEDGER ONE NEARLY BROKE PERMIT BINDING. `revision()` returns "" where
#:                     git_head returned None, and git_head's result becomes `manifest["head"]` —
#:                     which every allocation permit is BOUND to. An empty string and a null are
#:                     different JSON, so a silent swap would have moved the manifest digest and
#:                     invalidated permit binding in a repository with no commits. The empty
#:                     answer is mapped back to None so the contract is byte-identical.
#:                     Each kept its refusal: all three raise rather than returning an empty
#:                     population, because an empty world satisfies every invariant and would
#:                     turn "ungoverned" into "fully governed".
#:
#:   12 -> 10   (-2)  A DETECTOR CORRECTION, NOT PROGRESS, and recorded apart from the
#:                     migrations for that reason. engine/uckp/assimilation.py and
#:                     engine/uckp/constitution.py were never callers: both name the tool in
#:                     `PersistenceBinding("git", ...)`, a persistence mechanism, and neither
#:                     spawns anything. The predicate counted a declaration as an invocation.
#:                     Narrowing it then opened the opposite hole — an argv assigned to a
#:                     variable escaped the check entirely — so the predicate is now a
#:                     conjunction of two module-level facts: it spawns a process, and it builds
#:                     a vector headed by the tool. Five cases pin both directions in the suite.
#:                     NO CODE MOVED for this fall. Two entries left the count because they
#:                     should never have been in it.
#:
#:   13 -> 12   (-1)  platform/repository_intelligence/contamination.py, and it was DECLARED
#:                     rather than migrated — so this fall is matched by a rise in
#:                     DECLARED_DIRECT_CEILING and buys no behaviour change at all. Recorded that
#:                     way on purpose: a fall by declaration and a fall by migration are different
#:                     facts and collapsing them would let the ratchet be satisfied by writing.
#:
#:   14 -> 13   (-1)  platform/repository_intelligence/mutation_classification.py, and this one
#:                     CHANGED A FAILURE MODE deliberately rather than incidentally. The call ran
#:                     with `check=False`, so a non-git tree produced an EMPTY tracked set — and
#:                     `_r01_repository_state` claims any existing path absent from that set, so
#:                     every subject in the repository would have been absorbed into
#:                     REPOSITORY_STATE before the rule that owns it was evaluated. The module's
#:                     own docstring calls precisely that outcome "a wrong authority, which is
#:                     strictly worse than the fail-closed terminal". It argued for fail-closed
#:                     and implemented fail-open; the provider raises, so it now does what it
#:                     said. Byte-safety is preserved and not re-argued: the provider's single
#:                     subprocess call site decodes with surrogateescape exactly as this did, so
#:                     a path that is not valid UTF-8 still round-trips. Populations proven
#:                     identical first: 7,126 both ways.
#:
#:   15 -> 14   (-1)  intelligence/rie/config.py, and it is recorded separately because the
#:                     migration was NOT mechanical. It asked `:(glob)*/__init__.py`, where git's
#:                     pathspec magic stops `*` at a separator; Selector matches with fnmatch,
#:                     where `*` crosses one. The same pattern through the provider returned an
#:                     EXTRA root — `00-BOOK`, from a nested package — which would have widened
#:                     RIE's capability catalogue silently. Measured: 7 roots the old way, 8 the
#:                     naive way, 7 again with depth-1 stated explicitly as `count("/") == 1`.
#:                     The filesystem fallback was RETAINED. It is what makes the function work in
#:                     a non-git checkout, and FilesystemProvider does not declare TRACKED_CONTENT
#:                     — correctly, since a filesystem cannot guarantee it — so resolving by
#:                     capability would find git alone and leave a non-git checkout with nothing.
#:                     Routing the fallback through a provider that cannot answer the question
#:                     would have been the appearance of abstraction, not the thing.
#:
#:   19 -> 15   (-4)  Tranche 1. THREE MIGRATED, ONE DECLARED, and the difference matters.
#:                     engine/certification_integrity/surface.py, engine/uicm/matrix.py and
#:                     platform/repository_intelligence/generated_artifacts.py each asked
#:                     TRACKED_CONTENT with the provider's own flags and each now calls
#:                     `enumerate`. PROVEN IDENTICAL BEFORE THE SWAP: the direct call and the
#:                     provider both return 7,126 paths and the sorted lists compare equal, so
#:                     no verdict any of them reaches can have moved. Failure semantics match
#:                     too — all three refused an empty world by raising, and the provider
#:                     raises rather than returning an empty tuple.
#:                     engine/execution_environment/discovery.py was DECLARED rather than
#:                     migrated: it runs `rev-parse --show-toplevel` to locate the repository
#:                     root, and a provider must be rooted at a path before it can answer
#:                     anything about that path. Asking one where its own root is has no answer
#:                     to give. That is a bootstrap, not a bypass.
#:                     ONE DEFECT CAUGHT IN THE MIGRATION ITSELF: `Artifact.location` renders as
#:                     `git:<path>`, carrying the provider identifier, and the bare path is
#:                     `location.locator`. The first draft used the rendered form and would have
#:                     silently failed every downstream path lookup while reporting a full
#:                     population — an absence indistinguishable from a clean result.
#:
#:   (established) 19  Baseline measured by AST over engine, platform, intelligence,
#:                     infrastructure and service, excluding tests and the two modules declared
#:                     above. Six of the nineteen were invisible to the flag-based scan that
#:                     preceded this one, which matched `ls-files` argument lists and therefore
#:                     missed every caller using another subcommand.
DIRECT_CALLER_CEILING = 4

#: A SECOND CEILING, BECAUSE THE FIRST HAS A LOOPHOLE. Declaring a caller lowers the direct count
#: without changing one line of behaviour, so a ratchet on that count alone can always be
#: satisfied by writing a paragraph. That is the gaming the Omega-4 note refuses in its own terms,
#: available here by construction — and a ratchet that can be satisfied by explaining is not
#: measuring anything.
#:
#: So declarations are ratcheted too. This may only rise with a reason a reader can check, and
#: every rise is a claim that the provider CANNOT answer the question rather than that nobody
#: routed it yet. The two numbers together are the honest statement: how many callers reach past
#: the abstraction, and how many questions the abstraction admits it does not cover.
#:
#: MOVEMENTS
#:   2 -> 3   engine/execution_environment/discovery.py — locates the repository root, which must
#:            happen before a provider can be rooted at it. A bootstrap, not a bypass.
#:   3 -> 4   platform/repository_intelligence/contamination.py — needs ignored paths with status
#:            codes and ignore-rule attribution. Neither is content, so neither is a discovery
#:            question; capabilities for them would have one implementation each on an axis
#:            adr/0039 declares git-bound.
DECLARED_DIRECT_CEILING = 4


def _invokes_tool_directly(path: pathlib.Path) -> bool:
    """True when this module SPAWNS the tool, not merely when it names it.

    AST rather than text, for the reason UVI-L-06 gives about a selection engine naming a test
    file: a module discussing the tool in a docstring is not invoking it, and a comment cannot
    execute.

    TWO DEFECTS WERE FOUND IN THIS PREDICATE, IN OPPOSITE DIRECTIONS, AND BOTH ARE WHY IT LOOKS
    LIKE THIS.

    FALSE POSITIVES. The first version flagged any call whose argument list held the string, so a
    DECLARATION naming the tool was indistinguishable from an INVOCATION of it.
    `PersistenceBinding("git", path, False)` names a persistence mechanism and spawns nothing, yet
    two modules were counted as callers for it. A ratchet carrying false positives can never
    honestly reach its floor: the last entries are unremovable, and the only way to close it would
    be to declare modules that never had a bypass to declare.

    FALSE NEGATIVES. Narrowing to "the tool is the first argument of a spawn call" fixed that and
    opened a worse hole: `cmd = ["git", "status"]` followed by `run(cmd)` was no longer caught. A
    guard against new bypasses that anyone evades by assigning to a variable is not a guard.

    So the test is a CONJUNCTION of two module-level facts: the module spawns a process somewhere,
    and it builds an argument vector whose first element is the tool. A declaration fails the
    second (its "git" is a call argument, not the head of a vector); a docstring fails both; and
    an argv assigned to a name passes both, wherever the assignment sits.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except (SyntaxError, OSError):  # pragma: no cover - unparseable file
        return False
    spawns = False
    builds_argv = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            target = node.func
            name = target.attr if isinstance(target, ast.Attribute) else getattr(target, "id", "")
            if name in _SPAWNS:
                spawns = True
        elif isinstance(node, ast.List | ast.Tuple) and node.elts:
            head = node.elts[0]
            if isinstance(head, ast.Constant) and head.value == "git":
                builds_argv = True
        if spawns and builds_argv:
            return True
    return False


def direct_callers(root: str | None = None) -> tuple[str, ...]:
    """Every module invoking the tool directly, excluding those declared above."""
    base = pathlib.Path(root or os.getcwd())
    found = []
    for top in roots(base):
        for path in (base / top).rglob("*.py"):
            rel = path.relative_to(base).as_posix()
            if {"test", "tests"} & set(path.parts) or path.name.startswith(("test_", "conftest")):
                continue
            if "__pycache__" in rel or rel in DECLARED_DIRECT:
                continue
            if _invokes_tool_directly(path):
                found.append(rel)
    return tuple(sorted(found))


__all__ = [
    "DECLARED_DIRECT",
    "DECLARED_DIRECT_CEILING",
    "DIRECT_CALLER_CEILING",
    "direct_callers",
    "roots",
]
