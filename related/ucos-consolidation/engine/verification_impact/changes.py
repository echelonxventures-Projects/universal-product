"""What changed — resolved fail-closed, the way CI already does it.

The diff-base resolution chain is copied in spirit from ``.github/workflows/ec1-ci.yml``
(lines 60-95), which resolves a base and **fails closed if none resolves**. That
refusal is the important part: an impact engine that silently treats "no base" as "no
changes" reports an empty affected set, and an empty affected set is indistinguishable
from a clean run. So :func:`changed_paths` raises rather than returning ``()``.

Order, most to least specific:

1. an explicit base the caller supplied
2. staged + unstaged changes against ``HEAD`` (the local pre-commit case)
3. ``merge-base`` against the upstream tracking branch
4. ``HEAD^`` — the single-commit case

Every candidate is validated with ``git rev-parse --verify`` before use, so a stale
branch name cannot silently widen or narrow the set.
"""

from __future__ import annotations

import subprocess

from engine.verification_impact.graph import ImpactError, repo_root


def _git(*args: str, root: str | None = None) -> tuple[int, str]:
    """Run git and return ``(returncode, stdout)``. Never raises on non-zero.

    For refs and object names only. Every command that emits *paths* must go through
    :func:`_git_paths` instead — see the note there.
    """
    result = subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607 - resolved from PATH by design, no shell
        cwd=root or repo_root(),
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, result.stdout.strip()


def _git_paths(*args: str, root: str | None = None) -> tuple[int, tuple[str, ...]]:
    """Run a path-emitting git command and return ``(returncode, paths)``.

    ``-z`` is the correctness condition, not an optimisation. Without it git C-quotes
    and octal-escapes any path holding a non-ASCII byte, so a changed ``UCOS-Ω∞-T.md``
    arrives as the literal string ``"UCOS-\\316\\251\\342\\210\\236-T.md"`` — quote
    characters included. That string is not a repository path: it matches no
    ``UNBOUNDED_PREFIXES`` entry (it starts with ``"``), no ``BOUNDED_SUFFIXES`` entry
    (it ends with ``.py"``), and no executable-object-registry record. The change is
    still *seen*, so the scope does not narrow — but every downstream statement about
    it is false: the escalation reason names a file that does not exist, and a
    registered module is reported as unregistered. An impact engine whose escalations
    are right by accident and wrong by reason is not tracking real coupling.

    ``-z`` disables quoting outright, so this carries no dependence on
    ``core.quotePath``. Decoding is byte-safe for the same reason: a path git carries
    need not be valid UTF-8, and ``surrogateescape`` round-trips those bytes rather
    than raising or substituting. Same construction as ``ukb._git_ls`` and
    ``mutation_classification.Repository.tracked``, the repository's other
    version-control path queries.

    Selection logic is untouched: this returns exactly the paths the previous parse
    intended to return, spelled correctly.
    """
    result = subprocess.run(  # noqa: S603
        ["git", *args, "-z"],  # noqa: S607 - resolved from PATH by design, no shell
        cwd=root or repo_root(),
        capture_output=True,
        check=False,
    )
    decoded = result.stdout.decode("utf-8", errors="surrogateescape")
    return result.returncode, tuple(path for path in decoded.split("\0") if path)


def _exists(ref: str, root: str | None = None) -> bool:
    code, _ = _git("rev-parse", "--verify", "--quiet", ref, root=root)
    return code == 0


def working_tree_changes(root: str | None = None) -> tuple[str, ...]:
    """Paths differing from ``HEAD``, staged or not.

    This is the local pre-commit reality: a developer's uncommitted work is the change
    set, and it is what ``--change`` should measure before a commit exists.
    """
    code, found = _git_paths("diff", "--name-only", "HEAD", root=root)
    if code != 0:
        return ()
    paths = set(found)
    code, found = _git_paths("diff", "--name-only", "--cached", "HEAD", root=root)
    if code == 0:
        paths |= set(found)
    code, found = _git_paths("ls-files", "--others", "--exclude-standard", root=root)
    if code == 0:
        paths |= set(found)
    return tuple(sorted(paths))


def changed_paths(base: str | None = None, root: str | None = None) -> tuple[str, ...]:
    """Resolve the change set, failing closed when no base can be established.

    Raises:
        ImpactError: no diff base resolved. Treating that as "nothing changed" would
            make an unverified run look verified.
    """
    if base:
        if not _exists(base, root):
            raise ImpactError(f"the supplied diff base does not resolve: {base}")
        code, found = _git_paths("diff", "--name-only", f"{base}...HEAD", root=root)
        if code != 0:
            raise ImpactError(f"could not diff against base: {base}")
        return tuple(sorted(found))

    local = working_tree_changes(root)
    if local:
        return local

    code, upstream = _git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}", root=root)
    if code == 0 and upstream and _exists(upstream, root):
        code, merge_base = _git("merge-base", upstream, "HEAD", root=root)
        if code == 0 and merge_base:
            code, found = _git_paths("diff", "--name-only", f"{merge_base}...HEAD", root=root)
            if code == 0:
                return tuple(sorted(found))

    if _exists("HEAD^", root):
        code, found = _git_paths("diff", "--name-only", "HEAD^...HEAD", root=root)
        if code == 0:
            return tuple(sorted(found))

    raise ImpactError(
        "no diff base could be resolved (no working-tree change, no upstream, no HEAD^); "
        "refusing to report an empty change set, which would look like a verified run"
    )
