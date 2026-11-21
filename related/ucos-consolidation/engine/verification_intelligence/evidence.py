"""UVI-000001 Part 05 — the Verification Evidence Registry.

A CACHE, and the docstring says so first because everything else follows from it. An
entry records that one declared stage was executed over one exactly-identified input
and passed. It is not a record of truth, it is not evidence of certification, and
deleting the whole store changes no verdict — it only makes the next run pay again.

The key is computed, never asserted. For a stage declaring ``reuse_inputs``, the digest
is taken over the ``content_hash`` values that ``00-MASTER/UCOS-UGA-001/01-EXECUTABLE-
OBJECT-REGISTRY.json`` already publishes for every object under those prefixes, plus the
stage's own identity, the engine version, and THE EXECUTION CONTRACT — the argv
``./verify.sh`` runs under that stage's label. So the question "has this exact stage
already passed over this exact input" is answered from hashes the repository already
owns rather than from a second measurement of the tree.

The execution contract is in the key because without it the question above was answered
for a stage identified only by name. A stage is what it RUNS as much as what it READS:
under EVIDENCE_VERSION 1.0 the label ``universal object birth contract (…)`` keyed the
same entry whether the script ran ``--gate --quiet`` or ``--gate``, so an edit to the
command was answered by a result the edited command had never produced. The argv is
taken from the script's own source text rather than from an expanded process argument
list, which keeps ``"$PY"`` a literal and therefore keeps this machine's absolute venv
path — and any other host detail — out of every key.

Three refusals are structural rather than configurable:

* **A certification-eligible mode never reaches a reuse decision.** ``integration`` and
  ``full`` declare ``evidence_reuse: false``, and :func:`decide` refuses before it looks
  at the store. A certification that reuses a result certifies a cache.
* **An unhashed input is never a hit.** If any object under a declared prefix carries no
  content hash, or the prefix matches no object at all, the digest is refused and the
  stage runs. A cache key that silently covers nothing is a permanent false hit.
* **An unresolvable command is never a hit.** If the script declares the stage's label
  no times or more than once, the contract is unknown, the digest is refused and the
  stage runs. Unknown widens; it never narrows.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from typing import Any

from engine.verification_intelligence.constitution import execution_contract, repo_root
from engine.verification_intelligence.model import Mode, StageSpec
from engine.verification_intelligence.registry import Substrates

#: Bumping this invalidates every stored entry. It is part of every key, so a change to
#: how a stage is executed can never be answered by a result produced under the old way.
#:
#: 2.0 — the key gained the EXECUTION CONTRACT. Under 1.0 the key covered the stage's
#: identity, its label and its declared inputs, but not the argv ``./verify.sh`` runs
#: under that label, so editing a stage's command while leaving its label alone produced
#: a HIT on a result the new command had never produced. Every 1.0 entry is unreachable
#: from this version, which is the correct migration: those entries record what an
#: unidentified command did.
EVIDENCE_VERSION = "2.0"

SCHEMA = "ucos-verification-evidence"

#: The declared read-set token for a stage whose subject IS the version-controlled
#: boundary. ``universal-object-governance`` asserts the ten invariants over every
#: tracked object and ``pytest`` runs the whole suite; enumerating roots for them would
#: be a list that silently fails to cover a root added later. The token cannot be a
#: prefix that happens to match everything, because it must remain TRUE when the tree
#: grows — which is the same openness UISD-000001 requires everywhere else.
WHOLE_BOUNDARY = "**"


@dataclass(frozen=True, slots=True)
class EvidenceEntry:
    """One recorded stage result."""

    stage_id: str
    input_digest: str
    result: str
    engine_version: str

    @property
    def passed(self) -> bool:
        return self.result == "PASS"


def store_home(root: str | None = None, home: str = ".ucos-verification-evidence/") -> str:
    return os.path.join(root or repo_root(), home)


def resolve_prefix(substrates: Substrates, prefix: str) -> list[str]:
    """Every registered object under ``prefix``, sorted — resolved against the UNIVERSAL registry.

    A6 — THE PROJECTION MATTERS. This used to resolve against ``substrates.objects``,
    which is the EXECUTABLE projection: a strict subset that omits every
    ``DOCUMENT_ARTIFACT``. Three stages declare read-sets that are wholly or partly
    documents, and two of their prefixes — ``00-SOURCE/`` and ``00-BOOK/SCHEMAS/`` —
    matched nothing at all, while 32 tracked, hashed objects sat in the universal
    registry. The prefixes were never wrong; they were being asked of the wrong register.

    An empty result is now a genuine authoring error: the declaration names a path the
    repository does not carry. ``input_digest`` still refuses the key rather than
    raising — a plan must never crash — but the condition is measured and refused by
    ``UVI-L-11`` so it cannot sit silent again.
    """
    if prefix == WHOLE_BOUNDARY:
        return sorted(substrates.universal)
    stem = prefix.rstrip("/")
    return sorted(
        path
        for path in substrates.universal
        if path == stem or path.startswith(stem + "/") or path == prefix
    )


def input_digest(
    stage: StageSpec, substrates: Substrates, *, contract: tuple[str, ...] | None
) -> str | None:
    """The digest of everything ``stage`` reads AND runs, or None when it cannot be taken.

    ``contract`` is the argv ``./verify.sh`` executes under this stage's label, as
    :func:`engine.verification_intelligence.constitution.execution_contract` derives it.
    It is keyword-only and has NO DEFAULT, deliberately. A default would let a caller
    compute a key that omits the command without saying so, which is precisely the
    condition this parameter exists to make impossible: under EVIDENCE_VERSION 1.0 the
    key covered the stage's label but not its command, so changing ``--gate --quiet`` to
    ``--gate`` while leaving the label alone HIT a result the new command had never
    produced. An optional key component is a false hit waiting for a forgetful caller.

    Returns None — never a placeholder — when the stage declares no reuse inputs, when
    the execution contract could not be resolved, when a declared prefix matches no
    registered object, or when a matched object carries no content hash. Each is a key
    that would cover less than the stage reads or runs, and such a key is a false hit
    waiting to happen.

    Order is significant in ``contract`` and insignificant in ``reuse_inputs``. The argv
    is hashed in the order the script writes it, because a shell passes it in that order
    and nothing here may assume a flag parser is order-insensitive; the prefixes are
    sorted, because a set of declared inputs has no order to preserve.
    """
    if not stage.reusable or not stage.reads:
        return None
    if contract is None:
        return None
    digest = hashlib.sha256()
    digest.update(f"{EVIDENCE_VERSION}\n{stage.stage_id}\n{stage.label}\n".encode())
    digest.update(f"argc:{len(contract)}\n".encode())
    for index, token in enumerate(contract):
        digest.update(f"argv:{index}:{token}\n".encode())
    for prefix in sorted(stage.reads):
        matched = resolve_prefix(substrates, prefix)
        if not matched:
            return None
        digest.update(f"prefix:{prefix}\n".encode())
        for path in matched:
            entry = substrates.universal[path]
            content_hash = entry.get("content_hash")
            if content_hash:
                digest.update(f"{path}:{content_hash}\n".encode())
                continue
            withheld = entry.get("content_hash_withheld")
            if withheld:
                # A5 — WITHHELD IS KNOWN, AND KNOWN IS NOT MISSING. Eleven surfaces
                # carry no hash because they are SELF_REFERENTIAL: the object is the
                # engine's own output and a file cannot contain its own hash. That is a
                # declared, permanent property of the object, not an absence of
                # measurement, so it contributes the declared reason as a constant. It
                # is a constant on purpose: it can never distinguish two revisions of
                # that file, so any stage whose read-set is ONLY such objects still
                # keys on nothing that moves — which is why the prefix's other members
                # carry the discrimination, and why UGA and infinite-scope, whose
                # subject IS the whole tree, remain declared non-reusable.
                digest.update(f"{path}:withheld:{withheld}\n".encode())
                continue
            # No hash and no declared reason. Unmeasured is unknown, and unknown
            # refuses the key rather than keying on an absence.
            return None
    return digest.hexdigest()


def _entry_path(home: str, stage_id: str, digest: str) -> str:
    return os.path.join(home, stage_id, f"{digest}.json")


def lookup(home: str, stage_id: str, digest: str) -> EvidenceEntry | None:
    """The recorded entry for this exact stage and input, if one exists and is usable."""
    target = _entry_path(home, stage_id, digest)
    try:
        with open(target, encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None
    if document.get("schema") != SCHEMA:
        return None
    if document.get("engine_version") != EVIDENCE_VERSION:
        return None
    if document.get("input_digest") != digest or document.get("stage_id") != stage_id:
        return None
    return EvidenceEntry(
        stage_id=stage_id,
        input_digest=digest,
        result=str(document.get("result") or ""),
        engine_version=EVIDENCE_VERSION,
    )


def record(home: str, stage_id: str, digest: str, result: str) -> None:
    """Store a stage result, atomically.

    A half-written entry read by the next run would be a corrupt cache reporting a hit,
    so the write is a rename over a completed temporary file. Failure to write is
    swallowed on purpose: a cache that cannot be written must not fail a verification.
    """
    directory = os.path.join(home, stage_id)
    document: dict[str, Any] = {
        "schema": SCHEMA,
        "engine_version": EVIDENCE_VERSION,
        "stage_id": stage_id,
        "input_digest": digest,
        "result": result,
    }
    try:
        os.makedirs(directory, exist_ok=True)
        handle = tempfile.NamedTemporaryFile(  # noqa: SIM115 - renamed below, not closed early
            "w", encoding="utf-8", dir=directory, delete=False, suffix=".tmp"
        )
        with handle:
            json.dump(document, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(handle.name, _entry_path(home, stage_id, digest))
    except OSError:
        return


def decide(
    mode: Mode,
    stage: StageSpec,
    substrates: Substrates,
    *,
    home: str,
    root: str | None = None,
    verify: str | None = None,
) -> tuple[bool, str, str | None]:
    """Decide whether ``stage`` may be answered from evidence.

    Returns ``(reuse, reason, digest)``. The reason is carried into the plan either way,
    so a run always states why a stage was executed as well as why one was not.

    ``verify`` is the text of ``./verify.sh``. A caller deciding many stages should read
    it once and pass it, so one plan performs one read rather than one per stage; a
    caller that omits it gets a correct answer and pays a read. Either way the CERTIFICATION
    REFUSAL IS EVALUATED FIRST — a certification-eligible mode returns before this
    function touches the script, the store, or a digest, because a certification that can
    be made to depend on the contents of a cache directory is not a certification.
    """
    if not mode.evidence_reuse:
        return False, f"{mode.mode_id} is a certification-eligible mode; it never reuses", None
    if not stage.reusable:
        return False, "the stage is declared non-reusable", None
    contract = execution_contract(stage.label, root=root, source=verify)
    if contract is None:
        return False, "the execution contract for this stage could not be resolved", None
    digest = input_digest(stage, substrates, contract=contract)
    if digest is None:
        return False, "no input digest could be taken over the declared inputs", None
    entry = lookup(home, stage.stage_id, digest)
    if entry is None:
        return False, "no evidence exists for this input", digest
    if not entry.passed:
        return False, "the recorded result for this input is not PASS", digest
    return True, f"identical input already passed (digest {digest[:12]})", digest
