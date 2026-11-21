"""Git repository connector (UMB-012 / UMB-018 §3) — a LIVE, credential-free source.

UMB-REMED-002 (F-2 runtime authenticity closure). Unlike the five external
reference connectors (github-actions / kubernetes / prometheus / sonarqube /
trivy), which replay static ``fixtures/*.json`` files, this connector queries the
REAL local Git repository at runtime via the ``git`` CLI. It is therefore a
genuine live authoritative source: the signal it emits is derived from actual
version-control state, not a canned fixture. It reads only public repository
facts (working-tree presence, HEAD, tracked-file counts) and NEVER reads, stores,
or logs a secret (RR-07): Git needs no credentials for local inspection.

It observes the live fact that UMB-REMED-001 established — the Master Book
machinery is under durable version control — and rolls it up to the book root's
``implementation`` dimension of the twin (UMB-018 §3: repository/commit facts
enter the twin as append-only Signals; UMB-012 §2 State-synchronization surface).

Idempotency / drift-safety (UKB-ADV-INV-07; F-1 drift gate): the event carries a
CONSTANT ``source_event_id`` so replay is de-duplicated by the append-only ledger
(the signal is committed exactly once and its idempotency key persists in the
ledger's ``seen_keys``), and ``high_water`` returns None so no connector cursor is
written. Consequently a re-run — at any cadence, on a shallow CI checkout, or after
any number of new commits — appends nothing and mutates no DATA file, exactly like
an unchanged fixture replay. Standard library only.
"""

from __future__ import annotations

import os
import subprocess

from . import register
from .base import Connector, make_signal

# Stable event identity — the connector reports ONE idempotent observation:
# "the Master Book corpus is under version control". Replay de-duplicates on this
# key, so the live signal is written exactly once and can never drift.
_EVENT_ID = "master-book-under-version-control"
_REPO_HINT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
# The Master Book subject the repository fact rolls up to (the book root artifact).
_BOOK_ROOT_UID = "UCOS-BOOK-000000"


def _git(args, cwd):
    """Run a git command read-only; return stripped stdout or None on any error.
    Never raises — a missing git binary or non-repo directory yields None so the
    connector degrades to 'no live event' rather than failing the run."""
    try:
        out = subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return out.stdout.strip()


@register
class GitRepositoryConnector(Connector):
    name = "git-repository"
    sources = ["GIT"]
    dimensions = ["implementation"]
    mode = "POLL_INCREMENTAL"

    def _repo_root(self):
        root = _git(["rev-parse", "--show-toplevel"], _REPO_HINT)
        return root or None

    def fetch(self, since):
        """Emit ONE live event describing the version-controlled Master Book, or
        nothing if this is not a Git work tree / git is unavailable. `since` is
        ignored: idempotency is enforced by append() on the constant event id, so
        replay is a true no-op regardless of cadence or clone depth."""
        root = self._repo_root()
        if not root:
            return []                                   # not a git work tree — no live source
        head = _git(["rev-parse", "--short", "HEAD"], root)
        if not head:
            return []
        committed_at = _git(["log", "-1", "--format=%cI"], root)
        tracked = _git(["ls-files", "00-BOOK/tools", "00-BOOK/MASTER-BOOK"], root)
        tracked_files = len([ln for ln in (tracked or "").splitlines() if ln.strip()])
        if tracked_files == 0:
            return []                                   # machinery not yet version-controlled
        return [{
            "source_event_id": _EVENT_ID,
            "subject_universal_id": _BOOK_ROOT_UID,
            "as_of": committed_at or None,
            "head": head,
            "tracked_book_files": tracked_files,
        }]

    def high_water(self, events):
        # No cursor is persisted: the single observation is idempotent by
        # construction, so the connector-cursor store stays byte-stable (F-1).
        return None

    def normalize(self, ev, ctx):
        subj = self.resolve(ev, ctx)                    # resolves to the book root (explicit)
        yield make_signal(
            ctx["next_signal_id"](), subj, "implementation", "IMPLEMENTED", "GIT",
            evidence=f"git:{ev.get('head')}",
            metrics={"head": ev.get("head"),
                     "tracked_book_files": ev.get("tracked_book_files"),
                     "version_controlled": True},
            connector=self.name, ingest_run=ctx["ingest_run"], as_of=ev.get("as_of"))
