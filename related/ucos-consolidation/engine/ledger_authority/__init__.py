"""UCOS-LEDGER-AUTHORITY-001 — the ONE write chokepoint for the identity ledger.

WHERE THIS LIVES, AND WHY IT MOVED. The module was `00-BOOK/tools/ledger_authority.py`, beside
the ledger it guards. That placement cost it three measurements at once, and none of them was a
matter of taste: `00-BOOK` is not a Python identifier, so no coverage source could name the file
(UCI-L-01), no authority claimed it (UCI-L-02), and the two importers reached it through
`sys.path.insert` — an edge Ω-3's import graph cannot resolve, so the one chokepoint every
irreversible allocation passes through was measured as UNREACHABLE, "code that cannot run".
Living beside its data bought proximity and paid for it in three blind spots.

The ledger's LOCATION is unchanged and is not what this module's authority rests on: `commit`
takes the ledger path as an argument and `permit_register_path` derives the permit register from
that argument, so the pair still moves together wherever the caller points it. What changed is
that the code is now importable by name, which is the condition Ω-4's `unnameable_exemptions`
states for a governance engine and the condition UCI-L-01 measures.

WHY THIS EXISTS
---------------
`00-BOOK/DATA/id-ledger.json` is GOVERNED EVOLUTION STATE: append-only, irreducible,
not reproducible from the tree (see `ukb.py::cmd_build` and
`GOVERNED-EVOLUTION-STATE-DETERMINATION.md`). Before this module it had FOUR
independent writers reached through FOUR different entrypoints:

    ukb.py:cmd_build      `--mint`                -> by_path,        category_seq, page_cursor
    ukb.py:_exec_declare  `exec declare`          -> by_execution,   category_seq
    uga_engine.py:cmd_run `run`                   -> by_object,      category_seq
    uga_engine.py:cmd_run `run` (same write)      -> by_observation, category_seq

Each writer reported only the counter IT understood. `uga_engine.py::cmd_run` derived
its whole mint report from `epoch1_identity`, which counts `by_object` only, while the
SAME `_dump` persisted observation identities minted by `epoch_observation_universe`.
A run could therefore print `minted=0` while permanently allocating `UCOS-OBS-NNNNNN`
and advancing the shared `category_seq` — a silent irreversible allocation whose only
operator-visible signal said nothing happened.

The defect was never the arithmetic. It was that ALLOCATION and REPORTING were computed
from different scopes. A counter maintained by the caller can only ever measure the
allocations that caller knows about, so every future writer reintroduces the same blind
spot by default.

WHAT THIS FIXES STRUCTURALLY
---------------------------
`commit()` derives the allocation report from the DIFFERENCE between the on-disk
pre-image and the ledger about to be written. The report is therefore a property of the
bytes, not of the caller's bookkeeping: a write that allocates cannot report zero,
because nobody is asked how much they allocated. A writer that invents a fifth identity
map is measured on its first run without touching this module — `IDENTITY_MAPS` is the
only place the vocabulary lives, and an unknown top-level map is reported as
`unmeasured_maps` rather than passing silently.

WHAT THIS DELIBERATELY DOES NOT DO
----------------------------------
It does not decide WHETHER a mint is permitted. Authorization is the caller's declared
governance boundary (`CORPUS_REGISTRATION` in `mutation-governance-boundary.json`,
REG-AUTO-001 for the corpus, UCOS-UGA-001 for objects) and moving that decision here
would create a second governance authority. This module enforces only the properties
that are true of the ledger under EVERY authority: append-only, no identity reissue, no
counter regression, and total allocation disclosure.

It does not write the ledger's bytes either. The caller supplies its own `writer`, so each
writer keeps its exact existing serialization and idempotency semantics (`ukb._dump_json`
with stamp-equality and the frozen-path telemetry guard; `uga_engine._dump` with byte
comparison). This module adds measurement, refusal and authorization around that write
without introducing an on-disk format of its own.

The one exception is stated rather than hidden: when the persisted document turns out NOT
to be the authorized one, `commit()` restores the pre-image bytes it read moments earlier,
under the lock it still holds. That is a revert, not a format — it re-establishes exactly
the state every pre-write refusal leaves the file in, so a divergent writer and a refused
permit have the same fail-closed outcome. Without it, detection would be an improvement
over silence that still left an unauthorized document permanently on disk.

INVARIANT
---------
`LEDGER-INV-01` (measured by `uga_engine.py`): no source file outside this module may
name the ledger in a write call, or hand a ledger reference to a function that writes its
parameter. That makes a future fifth writer a GATE FAILURE rather than a discovery made
after the identifiers are already permanent. What the invariant cannot see — what a
`writer` does once this module hands it the path — is checked here at runtime instead, by
comparing the persisted document against the authorized one.
"""

from __future__ import annotations

import contextlib
import datetime as _dt
import hashlib
import json
import os
import time

try:
    import fcntl
except ImportError:  # pragma: no cover - non-POSIX platform
    # Absence is handled in `_ledger_lock` by REFUSING, never by writing unserialized.
    # A chokepoint that cannot exclude a second writer has not established the property
    # it exists for, and proceeding anyway would be the silent direction.
    fcntl = None  # type: ignore[assignment]

#: The append-only identity maps carried by the ledger, each mapping a stable key to a
#: record whose named field holds the PERMANENT identifier. Adding a map here is what
#: brings it under measurement; nothing else needs to change.
IDENTITY_MAPS: dict[str, str] = {
    "by_path": "universal_id",  # corpus documents    — UMB-IMP-001
    "by_object": "universal_id",  # executable objects  — UCOS-UGA-001
    "by_execution": "execution_id",  # execution instances — EXEC-REG-001
    "by_observation": "observation_id",  # observations        — UCOS-UGA-001
}

#: Scalar allocation cursors that may only ever increase.
MONOTONIC_COUNTERS: tuple[str, ...] = ("page_cursor", "volume_seq")

#: Top-level keys that are not identity allocation state, so their movement is not an
#: allocation. Anything else unknown is surfaced as `unmeasured_maps`.
NON_ALLOCATION_KEYS: frozenset[str] = frozenset(
    {
        "version",
        "category_seq",
        "discovered_volumes",
        *MONOTONIC_COUNTERS,
        # `history` is {universal_id: [snapshot, ...]} — snapshot LISTS, not records carrying
        # a permanent identifier, so it is not expressible in IDENTITY_MAPS' vocabulary at
        # all (that maps a key to the FIELD NAME holding an identifier). It is append-only
        # derived observation of content, written by `ukb.record_snapshots`. Leaving it
        # unclassified made every write against the real ledger measure `allocating=True`
        # for UNMEASURED_MAPS — including a byte-identical no-op — which made NO_ALLOCATION
        # unusable and `ukb.py exec declare`'s idempotent branch dead code. Its append-only
        # property is enforced by `assert_append_only` rather than by allocation counting,
        # because a snapshot append allocates no identifier.
        "history",
    }
)


class LedgerWriteRefused(RuntimeError):
    """A proposed ledger write violates an append-only property. Fails closed."""


def load_preimage(path: str) -> dict:
    """The ledger as it exists on disk right now, or {} when it does not yet exist.

    A missing file is a legitimate first-ever mint, not an error: every allocation in
    the proposed ledger is then correctly reported as new.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}
    except (OSError, ValueError) as exc:
        # Refuse rather than guess. Treating an unreadable ledger as empty would report
        # every existing identity as freshly minted and would hide a real regression.
        raise LedgerWriteRefused(
            f"identity ledger at {path} exists but cannot be read, so the append-only "
            f"properties of the proposed write cannot be checked ({exc})"
        ) from exc


def _identifier_index(ledger: dict, map_name: str) -> dict[str, object]:
    """{key: permanent identifier} for one identity map, tolerant of shape drift."""
    field = IDENTITY_MAPS[map_name]
    out: dict[str, object] = {}
    for key, rec in (ledger.get(map_name) or {}).items():
        out[key] = rec.get(field) if isinstance(rec, dict) else rec
    return out


def _record_index(ledger: dict, map_name: str) -> dict[str, object]:
    """{key: WHOLE record} for one identity map.

    The companion to `_identifier_index`, and the reason both exist: the identifier
    projection is what ALLOCATION is measured over (a new identifier is a new
    allocation), while the whole record is what APPEND-ONLY is checked over (a
    permanent identity's record may be extended by nothing at all). Measuring
    allocation over whole records would make every field edit an allocation; checking
    append-only over identifiers alone leaves `object_class`, `first_seen`,
    `page_start` and `page_count` rewritable while the identifier holds still.
    """
    return dict((ledger.get(map_name) or {}).items())


def _read_bytes_or_none(path: str) -> bytes | None:
    """The ledger's bytes as they are RIGHT NOW, or None when the file is absent.

    Absence is not an error (a first-ever mint has no pre-image); unreadability is,
    for the same reason `load_preimage` refuses — a file that cannot be read cannot be
    shown to satisfy anything.
    """
    try:
        with open(path, "rb") as fh:
            return fh.read()
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise LedgerWriteRefused(
            f"identity ledger at {path} exists but cannot be read, so the append-only "
            f"properties of the proposed write cannot be checked ({exc})"
        ) from exc


def read_preimage_bytes(path: str) -> tuple[bytes | None, dict]:
    """ONE read, returned as both views: the raw bytes and the parsed document.

    `commit()` used to read the ledger TWICE — once parsed, for verification, and once
    raw, for the byte comparison — and never reconciled the two. Two reads of one file
    that are never compared ARE the window: everything verified against the first read
    may already be stale by the second, and the second is the one the write is measured
    against. Returning both views of ONE buffer removes the possibility of disagreement
    instead of checking for it afterwards.

    Refusal messages deliberately match `load_preimage`'s, because the fail-closed
    behaviour they name is the same behaviour.
    """
    raw = _read_bytes_or_none(path)
    if raw is None:
        return None, {}
    try:
        return raw, json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise LedgerWriteRefused(
            f"identity ledger at {path} exists but cannot be read, so the append-only "
            f"properties of the proposed write cannot be checked ({exc})"
        ) from exc


#: How long `commit()` waits for the ledger lock before refusing. The discovery pass a
#: caller may run BEFORE reaching commit() is outside the lock, so hold time is bounded
#: by file I/O rather than by the caller's own work.
LEDGER_LOCK_TIMEOUT_SECONDS = 60.0


@contextlib.contextmanager
def _ledger_lock(path: str, *, timeout: float | None = None):
    """Serialize `commit()` against every other `commit()` on the same ledger.

    Locks the ledger's CONTAINING DIRECTORY rather than a lock file, and that choice is
    load-bearing rather than incidental: a new file under 00-BOOK/DATA would be an
    anonymous tracked object needing an allocation to name it — the regress
    `PERMIT_REGISTER_NAME` already terminates once — and it would additionally need a
    declared class in the tracked exclusion register. A directory descriptor needs
    neither, and it works for a first-ever mint, when no ledger file exists yet.

    Advisory, and therefore honest about its limits: a process that never asks for the
    lock is not excluded. That residual is what the pre-write byte re-check in
    `commit()` detects. Where `flock` is unavailable the write is REFUSED rather than
    performed unserialized.
    """
    if fcntl is None:  # pragma: no cover - non-POSIX platform
        raise LedgerWriteRefused(
            "identity ledger write refused — file locking is unavailable on this "
            "platform, so two writers cannot be shown not to interleave"
        )
    deadline = time.monotonic() + (LEDGER_LOCK_TIMEOUT_SECONDS if timeout is None else timeout)
    directory = os.path.dirname(os.path.abspath(path)) or "."
    # A first-ever mint may target a tree that does not exist yet, and every writer
    # already creates it (`ukb._dump_json` calls os.makedirs). Creating the DIRECTORY is
    # not writing the ledger, and doing it here keeps the lock from turning a legitimate
    # first mint into a refusal — E1-S4 must survive the addition of exclusion.
    try:
        os.makedirs(directory, exist_ok=True)
        fd = os.open(directory, os.O_RDONLY)
    except OSError as exc:
        raise LedgerWriteRefused(
            f"identity ledger write refused — cannot open {directory} to take the "
            f"ledger lock ({exc})"
        ) from exc
    try:
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise LedgerWriteRefused(
                        f"identity ledger write refused — another writer holds the "
                        f"ledger lock on {directory} and did not release it within the "
                        f"timeout; refusing rather than writing unserialized"
                    ) from None
                time.sleep(0.05)
        try:
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def assert_append_only(before: dict, after: dict) -> None:
    """Refuse any write that breaks a property the ledger holds under every authority.

    Five refusals, each naming a way a permanent identifier could stop being permanent:
    a key disappearing (identity forgotten), a key's identifier changing (identity
    reissued to different content), the record BODY of an existing identity changing
    (the identity's recorded facts rewritten under a constant identifier), the same
    identifier appearing under two keys (one identity naming two things), and a counter
    moving backward (a future allocation would collide with one already handed out).
    """
    problems: list[str] = []

    for map_name in IDENTITY_MAPS:
        old = _identifier_index(before, map_name)
        new = _identifier_index(after, map_name)
        old_rec = _record_index(before, map_name)
        new_rec = _record_index(after, map_name)
        for key in old:
            if key not in new:
                problems.append(
                    f"{map_name}: entry {key!r} would be REMOVED "
                    f"(identity {old[key]!r} is permanent and may not be forgotten)"
                )
            elif old[key] != new[key]:
                problems.append(
                    f"{map_name}: entry {key!r} would be REISSUED "
                    f"{old[key]!r} -> {new[key]!r} (identity is immutable)"
                )
            elif old_rec.get(key) != new_rec.get(key):
                # The identifier held still, so the projection above saw nothing. The
                # rest of the record — object_class, category, first_seen, page_start,
                # page_count — is equally permanent: it is what the identifier MEANS.
                was, now = old_rec.get(key), new_rec.get(key)
                if isinstance(was, dict) and isinstance(now, dict):
                    fields = sorted(f for f in set(was) | set(now) if was.get(f) != now.get(f))
                else:
                    fields = ["<record>"]
                problems.append(
                    f"{map_name}: record body of {key!r} would be REWRITTEN "
                    f"(field(s) {fields}); the record of a permanent identity is "
                    f"append-only in full, not only in its identifier"
                )

    # One identifier names at most one thing. `assert_append_only` already refuses a
    # reissue in the key -> identifier direction; this is the same property in the
    # identifier -> key direction, and it is what makes a counter collision detectable
    # on its own rather than only via the key-removal check. Spans all four maps
    # because all four draw from the ONE shared `category_seq`.
    bound: dict[object, str] = {}
    for map_name in IDENTITY_MAPS:
        for key, ident in sorted(_identifier_index(after, map_name).items()):
            if ident is None:
                continue
            where = f"{map_name}[{key!r}]"
            if ident in bound:
                problems.append(
                    f"identifier {ident!r} would be bound to BOTH {bound[ident]} and "
                    f"{where} (a permanent identifier names at most one thing)"
                )
            else:
                bound[ident] = where

    old_seq = before.get("category_seq") or {}
    new_seq = after.get("category_seq") or {}
    for cat, old_n in old_seq.items():
        new_n = new_seq.get(cat)
        if new_n is None:
            problems.append(
                f"category_seq: category {cat!r} would be REMOVED "
                f"(its allocated identifiers would become reissuable)"
            )
        elif isinstance(new_n, int) and isinstance(old_n, int) and new_n < old_n:
            problems.append(
                f"category_seq[{cat!r}] would REGRESS {old_n} -> {new_n} "
                f"(the next mint would collide with an issued identifier)"
            )

    for counter in MONOTONIC_COUNTERS:
        old_v, new_v = before.get(counter), after.get(counter)
        if isinstance(old_v, int) and isinstance(new_v, int) and new_v < old_v:
            problems.append(f"{counter} would REGRESS {old_v} -> {new_v}")

    # `history` is append-only, which `ukb.record_snapshots` states in its own docstring
    # ("Preserves every prior content_hash and version") and which nothing enforced. It
    # holds no permanent identifier, so allocation measurement cannot speak for it: the
    # only way a snapshot list can stop being append-only is to lose its prefix, and that
    # is what is refused here. This is not a definition of which writes are governed; it
    # is the property the producing code already claims.
    old_history = before.get("history") or {}
    new_history = after.get("history") or {}
    for uid, old_list in old_history.items():
        new_list = new_history.get(uid)
        if new_list is None:
            problems.append(
                f"history: {uid!r} would be REMOVED "
                f"({len(old_list) if isinstance(old_list, list) else '?'} recorded "
                f"snapshot(s); history is append-only)"
            )
        elif not isinstance(old_list, list) or not isinstance(new_list, list):
            if old_list != new_list:
                problems.append(f"history: {uid!r} would be REPLACED with a different shape")
        elif new_list[: len(old_list)] != old_list:
            problems.append(
                f"history: {uid!r} is not an extension of the recorded "
                f"{len(old_list)} snapshot(s) (history is append-only)"
            )

    if problems:
        raise LedgerWriteRefused(
            "identity ledger write refused — append-only violation:\n  - " + "\n  - ".join(problems)
        )


def allocation_report(before: dict, after: dict, actor: str = "UNDECLARED") -> dict:
    """TOTAL disclosure of what a proposed write allocates.

    Derived purely from the two ledger states, so it measures every identity map named
    in IDENTITY_MAPS whether or not the caller knows that map exists. `unmeasured_maps`
    names any top-level dict this module does not yet classify, so a genuinely new kind
    of allocation shows up as an unknown rather than as a zero.
    """
    allocated: dict[str, list[str]] = {}
    for map_name in IDENTITY_MAPS:
        old = _identifier_index(before, map_name)
        new = _identifier_index(after, map_name)
        fresh = sorted(str(new[k]) for k in new if k not in old)
        if fresh:
            allocated[map_name] = fresh

    old_seq = before.get("category_seq") or {}
    new_seq = after.get("category_seq") or {}
    advances = {
        cat: [old_seq.get(cat, 0), n]
        for cat, n in sorted(new_seq.items())
        if n != old_seq.get(cat, 0)
    }

    cursors = {
        c: [before.get(c), after.get(c)]
        for c in MONOTONIC_COUNTERS
        if before.get(c) != after.get(c)
    }

    unmeasured = sorted(
        k
        for k, v in after.items()
        if isinstance(v, dict) and k not in IDENTITY_MAPS and k not in NON_ALLOCATION_KEYS
    )

    total = sum(len(v) for v in allocated.values())
    return {
        "actor": actor,
        "total_allocations": total,
        # Fail closed: an unmeasured map is a kind of allocation this module cannot yet
        # count, so it may never be summarised as "nothing happened". Including it here
        # is what stops an unknown allocation from inheriting the no-op message.
        "allocating": bool(total or advances or cursors or unmeasured),
        "allocated": allocated,
        "counter_advances": advances,
        "cursor_advances": cursors,
        "unmeasured_maps": unmeasured,
    }


def format_report(report: dict) -> str:
    """One operator-facing line that can never understate an allocation.

    `bytes_changed` is rendered when present and omitted when absent, because this
    function is also called on `plan()` output (`ukb.py`, `uga_engine.py`) and inside
    `_verify_permit`'s own refusal message, none of which has performed a write. A bare
    subscript would turn `--plan` and every no-allocation refusal into a KeyError.
    """
    if not report["allocating"]:
        line = f"identity ledger: no allocation " f"(actor={report['actor']}, total_allocations=0)"
        return line + _moved_suffix(report)
    if report["total_allocations"]:
        parts = ", ".join(f"{name}+{len(ids)}" for name, ids in sorted(report["allocated"].items()))
        line = (
            f"identity ledger ALLOCATED {report['total_allocations']} permanent "
            f"identifier(s) [{parts}] actor={report['actor']}"
        )
    else:
        line = (
            f"identity ledger MUTATED with no measured identifier allocation "
            f"actor={report['actor']}"
        )
    if report["counter_advances"]:
        cats = ", ".join(f"{c}:{a}->{b}" for c, (a, b) in report["counter_advances"].items())
        line += f" category_seq({cats})"
    if report["cursor_advances"]:
        cur = ", ".join(f"{c}:{a}->{b}" for c, (a, b) in report["cursor_advances"].items())
        line += f" {cur}"
    if report["unmeasured_maps"]:
        line += (
            f" UNMEASURED_MAPS={report['unmeasured_maps']} "
            f"(add to IDENTITY_MAPS to bring under measurement)"
        )
    return line + _moved_suffix(report)


def _moved_suffix(report: dict) -> str:
    """Whether the file actually moved — computed since the first version of this module
    and, until now, never shown to anyone. An operator reading "ALLOCATED 1" had no way
    to distinguish a real allocation from a writer that persisted nothing."""
    changed = report.get("bytes_changed")
    return "" if changed is None else f" bytes_changed={changed}"


# ---------------------------------------------------------------------------------------
# AUTHORIZATION — the permit layer (Phase 2C)
#
# commit() ENFORCES an authorization it does not DECIDE. Who may issue a permit remains
# with the declared governance boundary (REG-AUTO-001 for the corpus, UCOS-UGA-001 for
# objects); this module only verifies mechanical properties of a permit that is presented
# to it. Moving the issuing decision here would create the second governance authority
# this module exists to avoid.
#
# The verification is content-bound rather than identity-bound. A permit names the digest
# of the allocation manifest it approves, and commit() RECOMPUTES that manifest from the
# on-disk pre-image before comparing. Forging a permit therefore requires knowing every
# identifier and counter advance the run will produce — which is the same work as
# reviewing the allocation. That is the property a signature alone would not buy in a
# single-operator repository, where the signer and the executor are the same person.
# ---------------------------------------------------------------------------------------

#: The ONE permit register, a sibling of the ledger it authorizes. A SINGLE append-only
#: file, never one file per permit: a new tracked file is an anonymous UCOS-UGA-001
#: object, and clearing that anonymity requires an allocation, which requires a permit,
#: which would be another new file. One register terminates that regress at one object.
#: The name must not end in `-audit.json` — governance_telemetry.forbid_data_telemetry
#: raises for any such path under 00-BOOK/DATA, and the obvious name is the forbidden one.
PERMIT_REGISTER_NAME = "allocation-permits.json"


class PermitRefused(RuntimeError):
    """A ledger write was attempted without an authorization that survives verification."""


class _NoAllocation:
    """Sentinel: the caller ASSERTS this write allocates nothing.

    Required because a write that allocates nothing still passes through the chokepoint
    (`ukb.py exec declare` re-declaring an existing execution is the real case), while a
    permit for an empty manifest would authorize nothing and must not be issuable.

    This is not a bypass and not a default. It is a CLAIM, and commit() checks it against
    the measured manifest: if the write turns out to allocate, the claim is false and the
    write is refused. Passing it is therefore strictly safer than passing a permit — it
    can only ever permit less.
    """

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return "NO_ALLOCATION"


#: The sentinel instance. `permit=NO_ALLOCATION` is an explicit, verified assertion.
NO_ALLOCATION = _NoAllocation()


def _canonical(obj) -> str:
    """Deterministic JSON: sorted keys, no whitespace drift, no wall clock.

    Determinism is what makes a digest usable as a permit binding at all — a manifest
    that serialises differently between two runs could never be pre-approved.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def manifest_digest(manifest: dict) -> str:
    """Digest over the ALLOCATION-BEARING fields only.

    Deliberately excludes `head`, `preimage_digest`, `issued_at` and any advisory field:
    those are separate bindings verified separately. Folding them in would make the digest
    change for reasons unrelated to what is being allocated, and an operator could no
    longer tell why a permit stopped matching.
    """
    return _sha256(
        _canonical(
            {
                "actor": manifest["actor"],
                "allocated": manifest["allocated"],
                "counter_advances": manifest["counter_advances"],
                "cursor_advances": manifest["cursor_advances"],
                "unmeasured_maps": manifest["unmeasured_maps"],
                "total_allocations": manifest["total_allocations"],
            }
        )
    )


def preimage_digest(before: dict) -> str:
    """Digest of the ledger state a manifest was measured against.

    This is what makes a permit SELF-INVALIDATING: performing the allocation changes the
    pre-image, so recomputing this value afterwards no longer matches the permit and the
    same permit cannot be replayed. No spent-permit registry is required, and none is
    created — spent-ness is DERIVED from two artifacts that are already committed.
    """
    return _sha256(_canonical(before))


def git_head(near_path: str) -> str | None:
    """Current HEAD of the repository containing `near_path`, or None outside a work tree.

    None is a legitimate answer (a VCS-less export, a temporary directory in a test), not
    an error. A permit that BINDS a head is refused when the head cannot be determined —
    the fail-closed direction — while a permit with `head: null` declines the binding.
    """
    directory = os.path.dirname(os.path.abspath(near_path)) or "."
    # THE PROVIDER, NOT THE TOOL. VERSIONED_CONTENT is the capability that names a revision, and
    # the provider supplies it.
    #
    # NONE IS PRESERVED DELIBERATELY, AND IT IS NOT COSMETIC. `revision()` returns "" where this
    # returned None, and the result of this function goes into `manifest["head"]` — which every
    # allocation permit is BOUND to. An empty string and a null are different JSON, so a silent
    # swap would move the manifest digest and invalidate permit binding for a repository with no
    # commits. The empty answer is mapped back to None so the contract is byte-identical.
    from engine.omega_infinite.capability import VERSIONED_CONTENT
    from engine.omega_infinite.git_provider import GitDiscoveryProvider

    try:
        head = str(GitDiscoveryProvider(root=directory).supply(VERSIONED_CONTENT) or "").strip()
    except Exception:  # noqa: BLE001 - any failure is "no head", exactly as before
        return None
    return head or None


def permit_register_path(ledger_path: str) -> str:
    """The register sits beside the ledger it authorizes, so the pair moves together."""
    return os.path.join(os.path.dirname(os.path.abspath(ledger_path)), PERMIT_REGISTER_NAME)


def load_permit_register(ledger_path: str) -> list[dict]:
    """Every permit ever issued. A missing register is an EMPTY register, never an open one.

    Fail-closed on unreadable content for the same reason `load_preimage` refuses: a
    register that cannot be parsed cannot be shown to contain the permit being claimed.
    """
    path = permit_register_path(ledger_path)
    try:
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except FileNotFoundError:
        return []
    except (OSError, ValueError) as exc:
        raise PermitRefused(
            f"permit register at {path} exists but cannot be read, so no permit can be "
            f"shown to authorize this write ({exc})"
        ) from exc
    permits = doc.get("permits") if isinstance(doc, dict) else doc
    if not isinstance(permits, list):
        raise PermitRefused(
            f"permit register at {path} does not carry a `permits` list; refusing to "
            f"guess its shape"
        )
    return permits


def build_manifest(before: dict, ledger: dict, actor: str, path: str) -> dict:
    """THE measurement. `plan()` and `commit()` both call this and nothing else.

    A second implementation of the allocation measurement would be a second SCOPE, and
    divergent scopes ARE the D0.1 defect: a run reported from one scope while allocating
    in another. Preview, authorization and execution read the same object here.
    """
    manifest = allocation_report(before, ledger, actor)
    manifest["preimage_digest"] = preimage_digest(before)
    manifest["head"] = git_head(path)
    manifest["digest"] = manifest_digest(manifest)
    return manifest


def plan(path: str, ledger: dict, *, actor: str) -> dict:
    """READ-ONLY preview. Everything commit() would do, stopped short of the writer.

    Writes nothing: not the ledger, not the permit register, not artifacts, not telemetry.
    The append-only check runs here too, so a write that WOULD be refused is refused at
    preview time rather than discovered after an operator has obtained authorization.

    The returned manifest carries `digest`, `preimage_digest` and `head` — exactly the
    three bindings a permit must quote — so issuing a permit is a transcription of this
    output rather than an independent act of measurement.
    """
    before = load_preimage(path)
    assert_append_only(before, ledger)
    return build_manifest(before, ledger, actor, path)


def _verify_permit(
    permit_ref,
    manifest: dict,
    actor: str,
    ledger_path: str,
    *,
    before: dict | None = None,
    after: dict | None = None,
) -> dict | None:
    """Resolve and verify. Returns the permit used, or None for a verified no-op claim.

    Every refusal names the binding that failed, because "permit rejected" with no reason
    is the message that gets worked around rather than understood.

    `before` / `after` are the pre-image and the proposed document, supplied only so the
    NO_ALLOCATION claim can be checked against the whole document rather than against the
    allocation projection alone. They are not consulted on the permit path: nothing about
    what a permit means, who may issue one, or when it expires is affected by them.
    """
    # ---- the explicit no-allocation claim, checked against the measurement -------------
    if permit_ref is NO_ALLOCATION:
        if manifest["allocating"]:
            raise PermitRefused(
                f"NO_ALLOCATION was asserted, but this write ALLOCATES: "
                f"{format_report(manifest)}. Obtain a permit for the manifest above, or "
                f"do not perform this write."
            )
        # The sentinel's claim is that this write allocates NOTHING, and its docstring
        # states the consequence: it "can only ever permit less" than a permit. That is
        # true of allocation and was not true of mutation — `version`,
        # `discovered_volumes` and every non-identifier record field sit outside the
        # allocation measurement, so a claim of "nothing allocated" was accepting a
        # rewrite of them. Checking the whole document is what makes the docstring true.
        if before is not None and after is not None and before != after:
            differing = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
            raise PermitRefused(
                f"NO_ALLOCATION was asserted, but this write MUTATES the ledger: "
                f"top-level key(s) {differing} differ from the pre-image. The sentinel "
                f"asserts that nothing changes, not merely that nothing is allocated. "
                f"Obtain a permit for the manifest above, or do not perform this write."
            )
        return None

    if not isinstance(permit_ref, str) or not permit_ref:
        raise PermitRefused(
            f"permit must be a permit_id string or NO_ALLOCATION; got {permit_ref!r}"
        )

    register = load_permit_register(ledger_path)
    matches = [p for p in register if isinstance(p, dict) and p.get("permit_id") == permit_ref]
    if not matches:
        raise PermitRefused(f"permit {permit_ref!r} is not in {permit_register_path(ledger_path)}")
    if len(matches) > 1:
        raise PermitRefused(
            f"permit {permit_ref!r} appears {len(matches)} times; an ambiguous "
            f"authorization is no authorization"
        )
    permit = matches[0]

    problems: list[str] = []

    # ---- actor binding ---------------------------------------------------------------
    if permit.get("actor") != actor:
        problems.append(
            f"actor: permit authorizes {permit.get('actor')!r}, this write is {actor!r}"
        )

    # ---- manifest binding — the D0.1 control -----------------------------------------
    if permit.get("manifest_digest") != manifest["digest"]:
        problems.append(
            f"manifest_digest: permit approves {permit.get('manifest_digest')!r}, this "
            f"write measures {manifest['digest']!r} — the allocation is not the one "
            f"authorized"
        )

    # ---- ledger pre-image binding — replay control -----------------------------------
    if permit.get("preimage_digest") != manifest["preimage_digest"]:
        problems.append(
            f"preimage_digest: permit was measured against a different ledger state "
            f"(permit {permit.get('preimage_digest')!r}, now "
            f"{manifest['preimage_digest']!r}) — it has already been spent, or the "
            f"ledger moved since issuance"
        )

    # ---- repository binding ----------------------------------------------------------
    bound_head = permit.get("head")
    if bound_head is not None:
        if manifest["head"] is None:
            problems.append(
                "head: permit binds a repository state but HEAD cannot be determined "
                "here; refusing rather than assuming a match"
            )
        elif bound_head != manifest["head"]:
            problems.append(
                f"head: permit binds {bound_head!r}, repository is at {manifest['head']!r}"
            )

    # ---- scope — redundant against the digest, and deliberately so -------------------
    # The digest binds exactly; a human cannot read a digest. `scope` is what a reviewer
    # actually approves, so it is verified independently: a permit whose stated scope
    # disagrees with what it digests is malformed, not merely redundant.
    scope = permit.get("scope")
    if isinstance(scope, dict):
        declared = scope.get("maps")
        if isinstance(declared, list):
            unauthorized = sorted(set(manifest["allocated"]) - set(declared))
            if unauthorized:
                problems.append(
                    f"scope: allocation touches {unauthorized} which the permit does not "
                    f"declare (declared: {sorted(declared)})"
                )
        cap = scope.get("max_allocations")
        if isinstance(cap, int) and manifest["total_allocations"] > cap:
            problems.append(
                f"scope: {manifest['total_allocations']} allocations exceed the declared "
                f"max_allocations={cap}"
            )

    # ---- expiry ----------------------------------------------------------------------
    expires_at = permit.get("expires_at")
    if expires_at:
        try:
            deadline = _dt.datetime.fromisoformat(str(expires_at).replace("Z", "+00:00"))
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=_dt.UTC)
        except ValueError:
            problems.append(f"expires_at: {expires_at!r} is not an ISO-8601 instant")
        else:
            if _dt.datetime.now(_dt.UTC) > deadline:
                problems.append(f"expires_at: permit expired at {expires_at}")

    if problems:
        raise PermitRefused(
            f"permit {permit_ref!r} refused — "
            + str(len(problems))
            + " binding(s) failed:\n  - "
            + "\n  - ".join(problems)
        )
    return permit


def _restore(path: str, raw_before: bytes | None) -> None:
    """Put the pre-image back. Not a new on-disk format — the same bytes, seconds later.

    Called only from `commit()`, only under the ledger lock, and only when the persisted
    document has already been shown NOT to be the authorized one. `commit()` still never
    invents bytes: it re-establishes the state that every refusal before the write leaves
    the file in, so a divergent writer produces the same fail-closed outcome as a refused
    permit. An absent pre-image restores to absent, never to an empty ledger — a phantom
    `{}` would report every future identity as freshly minted.
    """
    if raw_before is None:
        with contextlib.suppress(FileNotFoundError):
            os.remove(path)
        return
    with open(path, "wb") as fh:
        fh.write(raw_before)


def _refuse_unmoved_allocation(report: dict) -> None:
    """An allocation that did not move the file is a contradiction, not a report.

    Defence in depth: once the persisted document is compared against the authorized one,
    this state is unreachable through `commit()` — equal bytes plus an equal document
    imply an equal pre-image, hence nothing allocated. Kept as a named check because it
    fails loudly if that comparison is ever weakened, and because its message is the one
    an operator can act on.
    """
    if report.get("allocating") and report.get("bytes_changed") is False:
        raise LedgerWriteRefused(
            "identity ledger write refused — the report claims an allocation but the "
            f"file did not move: {format_report(report)}"
        )


def commit(path: str, ledger: dict, *, actor: str, writer, permit) -> dict:
    """THE chokepoint. Every identity-ledger write in this repository routes here.

    Order is deliberate and is the fix for the second half of the defect: the pre-image
    is read, the append-only properties are checked, and the AUTHORIZATION is verified
    BEFORE `writer` is allowed to touch the file, so a refused write leaves the ledger
    exactly as it was. The manifest is computed from the pre-image too, so it survives
    any re-derivation the caller performs afterwards.

    `permit` is REQUIRED and has no default. A default would convert the loudest possible
    failure — TypeError at the call site, before anything runs — into a silent bypass, and
    that is the single likeliest way this control could be lost. Pass a `permit_id` from
    the register, or `NO_ALLOCATION` to assert (and have verified) that nothing allocates.

    `writer(path, ledger)` performs the actual serialization. Keeping it with the caller
    preserves each writer's existing idempotency and guard behaviour byte-for-byte;
    this function adds measurement, refusal and authorization, never a new on-disk format.

    The whole body runs under an exclusive lock on the ledger's directory, and the bytes
    verification measured are re-read immediately before the writer runs, so the state
    that was checked is the state that gets overwritten. After the writer returns, the
    file is parsed and required to equal the document that was authorized; on any
    divergence the pre-image is restored and the write is refused. Those three additions
    are what make "verified" and "written" the same state rather than two states nothing
    compared.

    Returns the allocation report. `bytes_changed` records whether the file actually
    moved, which distinguishes a real allocation from an idempotent no-op rewrite.
    """
    with _ledger_lock(path):
        raw_before, before = read_preimage_bytes(path)
        assert_append_only(before, ledger)
        report = build_manifest(before, ledger, actor, path)

        # Authorization is verified against the RECOMPUTED manifest, never against
        # anything the caller supplied. A caller cannot describe its own write into
        # acceptability.
        used = _verify_permit(permit, report, actor, path, before=before, after=ledger)
        report["permit_id"] = None if used is None else used.get("permit_id")
        report["authorization"] = "NO_ALLOCATION" if used is None else "PERMIT"

        # Everything above was verified against `raw_before`. Confirm the file still
        # holds it. The lock makes this impossible for a cooperating writer, so what is
        # caught here is an out-of-band edit — and the whole point of the chokepoint is
        # that the state which was checked is the state that gets overwritten.
        if _read_bytes_or_none(path) != raw_before:
            raise LedgerWriteRefused(
                "identity ledger write refused — the ledger changed between "
                "verification and write, so the state that was checked is no longer the "
                "state on disk. Re-measure against the current pre-image."
            )

        writer(path, ledger)

        raw_after = _read_bytes_or_none(path)
        report["bytes_changed"] = raw_before != raw_after
        report["path"] = os.path.relpath(path) if os.path.isabs(path) else path

        # The writer is outside this module by design, so its OUTPUT is what gets
        # checked. Authorization measured `ledger`; only the file can say what was
        # persisted. Compared as a DOCUMENT rather than as bytes: three serializers
        # exist over this one document and they are not byte-equivalent, so byte
        # equality would refuse correct writes. Document equality is what authorization
        # actually covers.
        if raw_after is None:
            _restore(path, raw_before)
            raise LedgerWriteRefused(
                "identity ledger write refused — the writer persisted nothing: the file "
                f"is absent after the write, while the authorized manifest reports "
                f"{format_report(report)}"
            )
        try:
            persisted = json.loads(raw_after.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as exc:
            _restore(path, raw_before)
            raise LedgerWriteRefused(
                f"identity ledger write refused — the writer persisted unparseable "
                f"content, which cannot be the authorized document ({exc})"
            ) from exc
        if persisted != ledger:
            _restore(path, raw_before)
            raise LedgerWriteRefused(
                "identity ledger write refused — the persisted document is not the "
                "authorized document: the writer did not serialize what commit() "
                f"measured and authorized ({format_report(report)})"
            )
        try:
            _refuse_unmoved_allocation(report)
        except LedgerWriteRefused:
            _restore(path, raw_before)
            raise

        return report
