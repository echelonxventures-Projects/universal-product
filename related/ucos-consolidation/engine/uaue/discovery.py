"""UAUE — AUE-P-01, the evolution discovery engine (UAUE-000001, Epoch 3).

Discovery turns a condition another owner already measured into an evolution candidate. It
does **not** inspect the working tree, and it does not decide what is worth evolving. It reads
the sealed derived-truth artifacts that located owners publish — repository intelligence,
integration blueprint, convergence findings, progress measurement — plus the two internal
sources the declaration selects from itself. A candidate is therefore always attributable to
an owner that measured it, and a candidate this engine invented would have no source to name.

**The engine does not know what a subject is.** Nothing here branches on a subject's class,
domain, technology or vendor. A source declares a form, a selector and a field map; discovery
walks it. That is why the declared unknown probe — an object of no known class, in no registry,
with no owner — traverses this phase on exactly the same code path as a capability gap, and why
a source added to the declaration tomorrow needs no code here.

**No candidate without evidence.** A candidate whose declared artifact does not resolve is
dropped and recorded as a finding, never emitted with an empty evidence set. An absent artifact
is a finding rather than a refusal, because the declaration carries disclosed absences.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.uaue.model import DiscoverySource, EvolutionAuthority, SourceCondition
from engine.uaue.objects import EvolutionCandidate, as_context, derive_identity
from engine.uaue.resolution import DECLARATION_PATH, DeclarationReader, Substrate
from engine.uckp.canonical import content_hash

#: The phase this module realises, and the object kind it produces. Both are looked up in the
#: authority by ordinal rather than named here, so this module carries no phase identifier.
_DISCOVERY_ORDINAL = 1


@dataclass(frozen=True, slots=True)
class DiscoveryReport:
    """Everything discovery found, everything it could not read, and duty coverage.

    ``findings`` is not an error channel: an artifact a located owner has not published yet is
    a disclosed absence, and a report that hid it would make discovery look complete when it
    was merely quiet.

    A duty is discharged when at least one of its sources was *read*, not when that source
    produced candidates. A source that resolves and reports nothing has answered the duty —
    treating "no gap found" as an unmet duty would make a closed gap indistinguishable from an
    unread artifact, which is the distinction the whole register exists to keep.
    """

    candidates: tuple[EvolutionCandidate, ...]
    findings: tuple[str, ...]
    unresolved_sources: tuple[str, ...]
    per_source: tuple[tuple[str, int], ...]
    unsatisfied_duties: tuple[str, ...]

    @property
    def duties_satisfied(self) -> bool:
        return not self.unsatisfied_duties

    def for_source(self, source: str) -> tuple[EvolutionCandidate, ...]:
        return tuple(entry for entry in self.candidates if entry.source == source)

    def subjects(self) -> tuple[str, ...]:
        return tuple(sorted({entry.subject_identity for entry in self.candidates}))

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidates": [entry.to_dict() for entry in self.candidates],
            "findings": list(self.findings),
            "unresolved_sources": list(self.unresolved_sources),
            "per_source": [list(pair) for pair in self.per_source],
            "unsatisfied_duties": list(self.unsatisfied_duties),
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


def _load_artifact(path: Path) -> tuple[object | None, str]:
    """One sealed artifact, or the reason it could not be read. Never raises."""
    try:
        return json.loads(path.read_text(encoding="utf-8")), ""
    except OSError as error:
        return None, f"{type(error).__name__}: {error}"
    except ValueError as error:
        return None, f"not valid JSON: {error}"


def _select(document: object, selector: Sequence[str]) -> object | None:
    """Walk a declared selector. Returns None when any segment is not present."""
    current = document
    for segment in selector:
        if not isinstance(current, Mapping) or segment not in current:
            return None
        current = current[segment]
    return current


def _compare(left: object, op: str, right: object) -> bool:
    """One include_when comparison.

    Numeric comparisons require both sides to be real numbers — a string that looks like a
    number is not silently coerced, because a source whose field changed type would then be
    filtered under a comparison nobody declared. A non-comparable pair fails the condition,
    which excludes the entry rather than including it on a technicality.
    """
    if op in {"eq", "ne"}:
        equal = left == right
        return equal if op == "eq" else not equal
    numeric = (int, float)
    if isinstance(left, bool) or isinstance(right, bool):
        return False
    if not isinstance(left, numeric) or not isinstance(right, numeric):
        return False
    if op == "gt":
        return left > right
    if op == "lt":
        return left < right
    if op == "ge":
        return left >= right
    return left <= right


def _included(entry: Mapping[str, object], conditions: Sequence[SourceCondition]) -> bool:
    return all(_compare(entry.get(c.field_name), c.op, c.value) for c in conditions)


def _text_of(value: object) -> str:
    """A source value as text, without inventing content for an absent one."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, bool | int | float):
        return str(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _candidate(
    *,
    authority: EvolutionAuthority,
    source: DiscoverySource,
    subject: str,
    reason: str,
    severity: str,
    location: str,
    selector_text: str,
    evidence: Sequence[str],
    dependencies: Sequence[str],
    phase_authority: str,
    object_kind: str,
    substrate: Substrate,
) -> EvolutionCandidate | None:
    """One candidate, or None when it cannot be identified or has no *resolving* evidence.

    Evidence is filtered to the declared paths that exist, which is what the field mandate says
    it is. A candidate left with nothing that resolves is dropped: an evolution object with no
    resolving evidence is refused, so emitting one here would only defer the refusal.

    Returning None rather than raising is what keeps one malformed entry in a large artifact from
    suppressing every other candidate in it; the caller records the drop as a finding.
    """
    resolving = tuple(path for path in evidence if substrate.resolves(path))
    if not subject or not reason or not resolving:
        return None
    evidence = resolving
    context = as_context(
        {
            "source": source.identifier,
            "source_name": source.name,
            "owner": source.owner,
            "artifact": location,
            "selector": selector_text,
            "candidate_class": source.candidate_class,
        }
    )
    identity_inputs = {
        "candidate_class": source.candidate_class,
        "subject_identity": subject,
        "reason": reason,
        "authority": phase_authority,
        "object_kind": object_kind,
    }
    return EvolutionCandidate(
        evolution_id=derive_identity(authority.identity, identity_inputs),
        subject_identity=subject,
        candidate_class=source.candidate_class,
        source=source.identifier,
        owner=source.owner,
        reason=reason,
        previous_state=f"{source.owner} measures, in {location}: {subject}",
        target_state=source.target_template,
        context=context,
        evidence=tuple(evidence),
        dependencies=tuple(dependencies),
        severity=severity,
    )


def discover_evolution_candidates(
    authority: EvolutionAuthority,
    substrate: Substrate | None = None,
    reader: DeclarationReader | None = None,
) -> DiscoveryReport:
    """Discover every evolution candidate the declared sources yield.

    Args:
        authority: the rehydrated authority. Its ``discovery_sources`` drive this function
            entirely; there is no source list here.
        substrate: the tree to resolve artifact and home paths against.
        reader: the declaration, needed only by the two internal sources that select from it.

    Returns:
        A :class:`DiscoveryReport`. Deterministic: candidates are emitted in declared source
        order and, within a source, in the artifact's own order.
    """
    substrate = substrate if substrate is not None else Substrate()
    reader = reader if reader is not None else DeclarationReader.canonical()
    phase = next(entry for entry in authority.phases if entry.ordinal == _DISCOVERY_ORDINAL)
    object_kind = authority.object_kind_of(phase.identifier).identifier
    dependencies = phase.homes

    candidates: list[EvolutionCandidate] = []
    findings: list[str] = []
    unresolved: list[str] = []
    per_source: list[tuple[str, int]] = []

    for source in authority.discovery_sources:
        before = len(candidates)
        if source.internal:
            candidates.extend(
                _internal_candidates(
                    authority=authority,
                    source=source,
                    reader=reader,
                    substrate=substrate,
                    dependencies=dependencies,
                    phase_authority=phase.authority,
                    object_kind=object_kind,
                    findings=findings,
                )
            )
        else:
            if not substrate.resolves(source.path):
                unresolved.append(source.identifier)
                findings.append(
                    f"{source.identifier}: declared artifact does not resolve: {source.path}"
                )
                per_source.append((source.identifier, 0))
                continue
            document, problem = _load_artifact(substrate.root / source.path)
            if document is None:
                unresolved.append(source.identifier)
                findings.append(f"{source.identifier}: artifact unreadable: {problem}")
                per_source.append((source.identifier, 0))
                continue
            selected = _select(document, source.selector)
            if selected is None:
                unresolved.append(source.identifier)
                findings.append(
                    f"{source.identifier}: selector {'.'.join(source.selector)} "
                    f"is absent from {source.path}"
                )
                per_source.append((source.identifier, 0))
                continue
            candidates.extend(
                _artifact_candidates(
                    authority=authority,
                    source=source,
                    selected=selected,
                    dependencies=dependencies,
                    phase_authority=phase.authority,
                    object_kind=object_kind,
                    findings=findings,
                    substrate=substrate,
                )
            )
        per_source.append((source.identifier, len(candidates) - before))

    readable = {
        source.identifier
        for source in authority.discovery_sources
        if source.identifier not in unresolved
    }
    unsatisfied = tuple(
        duty.identifier
        for duty in authority.discovery_duties
        if not (set(duty.satisfied_by) & readable)
    )
    return DiscoveryReport(
        candidates=tuple(candidates),
        findings=tuple(findings),
        unresolved_sources=tuple(unresolved),
        per_source=tuple(per_source),
        unsatisfied_duties=unsatisfied,
    )


def _artifact_candidates(
    *,
    authority: EvolutionAuthority,
    source: DiscoverySource,
    selected: object,
    dependencies: Sequence[str],
    phase_authority: str,
    object_kind: str,
    findings: list[str],
    substrate: Substrate,
) -> list[EvolutionCandidate]:
    """Candidates from one resolved artifact, by the form the source declares."""
    selector_text = ".".join(source.selector)
    found: list[EvolutionCandidate] = []
    entries: list[tuple[str, Mapping[str, object] | str]] = []

    if source.form == "list_of_objects":
        if not isinstance(selected, list):
            findings.append(f"{source.identifier}: {selector_text} is not a list")
            return found
        entries = [("", entry) for entry in selected if isinstance(entry, Mapping)]
    elif source.form == "list_of_strings":
        if not isinstance(selected, list):
            findings.append(f"{source.identifier}: {selector_text} is not a list")
            return found
        entries = [("", entry) for entry in selected if isinstance(entry, str)]
    elif source.form == "mapping_of_objects":
        if not isinstance(selected, Mapping):
            findings.append(f"{source.identifier}: {selector_text} is not a mapping")
            return found
        entries = [
            (str(key), value)
            for key, value in sorted(selected.items())
            if isinstance(value, Mapping)
        ]
    else:
        findings.append(f"{source.identifier}: form {source.form} is not read from an artifact")
        return found

    subject_field = source.field_for("subject")
    reason_field = source.field_for("reason")
    severity_field = source.field_for("severity")

    for key, entry in entries:
        if isinstance(entry, str):
            subject, reason, severity = entry.strip(), source.reason_template, ""
        else:
            if not _included(entry, source.include_when):
                continue
            subject = _text_of(entry.get(subject_field)) if subject_field else key
            subject = subject or key
            reason = (
                _text_of(entry.get(reason_field)) if reason_field else ""
            ) or source.reason_template
            severity = _text_of(entry.get(severity_field)) if severity_field else ""
        candidate = _candidate(
            authority=authority,
            source=source,
            subject=subject,
            reason=reason,
            severity=severity,
            location=source.path,
            selector_text=selector_text,
            evidence=(source.path,),
            dependencies=dependencies,
            phase_authority=phase_authority,
            object_kind=object_kind,
            substrate=substrate,
        )
        if candidate is None:
            findings.append(
                f"{source.identifier}: an entry of {selector_text} named no subject "
                "or no reason and was not carried as a candidate"
            )
            continue
        found.append(candidate)
    return found


def _internal_candidates(
    *,
    authority: EvolutionAuthority,
    source: DiscoverySource,
    reader: DeclarationReader,
    substrate: Substrate,
    dependencies: Sequence[str],
    phase_authority: str,
    object_kind: str,
    findings: list[str],
) -> list[EvolutionCandidate]:
    """Candidates from a source that selects from the declaration rather than an artifact.

    Two exist. ``symbol_obligation`` yields a candidate for every declared authority surface
    that is *not* bound in its declared home — this is how the platform detects a gap in
    itself, and why the self-evolution finding closes automatically when the surface appears.
    ``unknown_probe`` yields the declared unknown subject, so an object of no known class
    enters the loop through the same door as everything else.
    """
    found: list[EvolutionCandidate] = []
    selector_text = ".".join(source.selector)
    location = DECLARATION_PATH

    if source.form == "symbol_obligation":
        for entry in reader.entries(source.selector[0]):
            home = _text_of(entry.get(source.field_for("subject")))
            symbol = _text_of(entry.get("symbol"))
            reason = _text_of(entry.get(source.field_for("reason"))) or source.reason_template
            if not home or not symbol:
                findings.append(
                    f"{source.identifier}: an authority obligation named no home or no symbol"
                )
                continue
            if symbol in substrate.symbols(home):
                # The obligation is discharged: the surface exists. Emitting a candidate here
                # would keep a closed gap open for ever, which is the opposite of measuring it.
                continue
            candidate = _candidate(
                authority=authority,
                source=source,
                subject=home,
                reason=reason,
                severity=symbol,
                location=location,
                selector_text=selector_text,
                evidence=(location,),
                dependencies=dependencies,
                phase_authority=phase_authority,
                object_kind=object_kind,
                substrate=substrate,
            )
            if candidate is not None:
                found.append(candidate)
        return found

    if source.form == "unknown_probe":
        probe = authority.unknown_probe
        candidate = _candidate(
            authority=authority,
            source=source,
            subject=probe.subject,
            reason=source.reason_template,
            severity=probe.subject_class,
            location=location,
            selector_text=selector_text,
            evidence=(location,),
            dependencies=dependencies,
            phase_authority=phase_authority,
            object_kind=object_kind,
            substrate=substrate,
        )
        if candidate is None:
            findings.append(f"{source.identifier}: the unknown probe could not be identified")
        else:
            found.append(candidate)
        return found

    findings.append(f"{source.identifier}: internal form {source.form} has no reader")
    return found


def declaration_evidence() -> str:
    """The declaration's own path, which the internal sources cite as their evidence."""
    return DECLARATION_PATH


__all__ = ["DiscoveryReport", "declaration_evidence", "discover_evolution_candidates"]
