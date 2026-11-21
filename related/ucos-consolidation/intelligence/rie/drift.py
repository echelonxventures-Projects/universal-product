"""Drift detection — what changed vs the previously persisted snapshot.

Drift is inherently temporal: it compares the freshly derived model against the
last persisted snapshot (if any). Duplicate and stale-evidence detection are
computed from the *current* evidence alone. When no prior snapshot exists, drift
reports ``baseline`` (nothing to compare) rather than inventing change.

Note on determinism: the DERIVED intelligence is a pure function of evidence and
is byte-identical across runs on identical state. Drift additionally depends on
the persisted prior snapshot; given the same evidence AND the same prior, drift
is likewise deterministic.
"""

from __future__ import annotations

from typing import Any


def detect(current: dict[str, Any], prior: dict[str, Any] | None) -> dict[str, Any]:
    duplicates = _duplicates(current)
    stale = _stale(current)
    if prior is None:
        return {
            "baseline": True,
            "note": "No prior snapshot; drift baseline established.",
            "implementation_drift": [],
            "certification_drift": [],
            "dependency_drift": [],
            "duplicate_findings": duplicates,
            "stale_evidence": stale,
        }
    return {
        "baseline": False,
        "implementation_drift": _impl_drift(current, prior),
        "certification_drift": _cert_drift(current, prior),
        "dependency_drift": _dep_drift(current, prior),
        "duplicate_findings": duplicates,
        "stale_evidence": stale,
    }


def _cap_index(model: dict[str, Any]) -> dict[str, str]:
    """Capability status by canonical name.

    Keyed on the canonical name, not on ``unique_id``: the id is an ordinal over
    the discovered catalogue, so inserting a capability shifts every later id and
    a drift report keyed on it would attribute changes to the wrong capability.
    The canonical name is the capability's identity.
    """
    caps = model.get("capabilities", [])
    return {c["canonical_name"]: c.get("implementation_status", "?") for c in caps}


def _impl_drift(cur: dict[str, Any], prior: dict[str, Any]) -> list[dict[str, str]]:
    now, was = _cap_index(cur), _cap_index(prior)
    drift: list[dict[str, str]] = []
    for name, status in sorted(now.items()):
        if name not in was:
            drift.append({"capability": name, "change": "ADDED", "status": status})
        elif was[name] != status:
            drift.append({"capability": name, "change": "STATUS", "from": was[name], "to": status})
    for name in sorted(set(was) - set(now)):
        drift.append({"capability": name, "change": "REMOVED", "was": was[name]})
    return drift


def _cert_drift(cur: dict[str, Any], prior: dict[str, Any]) -> list[dict[str, Any]]:
    cnow = cur.get("health", {}).get("certification", {}) or {}
    cwas = prior.get("health", {}).get("certification", {}) or {}
    drift = []
    for key in ("digital_twin_verdict", "domains"):
        if cnow.get(key) != cwas.get(key):
            drift.append({"field": key, "from": cwas.get(key), "to": cnow.get(key)})
    return drift


def _dep_drift(cur: dict[str, Any], prior: dict[str, Any]) -> list[dict[str, Any]]:
    now_edges = cur.get("health", {}).get("corpus", {}).get("edges")
    was_edges = prior.get("health", {}).get("corpus", {}).get("edges")
    if now_edges != was_edges:
        return [{"metric": "corpus_edges", "from": was_edges, "to": now_edges}]
    return []


def _duplicates(model: dict[str, Any]) -> list[dict[str, Any]]:
    """Heuristic duplicate detection: same short name across engine & platform."""
    caps = model.get("capabilities", [])
    by_name: dict[str, list[str]] = {}
    for c in caps:
        short = c["canonical_name"].split(".")[-1].split("/")[-1]
        by_name.setdefault(short, []).append(c["canonical_name"])
    findings = []
    for short, names in sorted(by_name.items()):
        if len(names) > 1:
            findings.append(
                {
                    "name": short,
                    "locations": sorted(names),
                    "assessment": "INTENTIONAL (layered engine/platform pair) — KEEP/COMPOSE",
                }
            )
    return findings


def _stale(model: dict[str, Any]) -> list[dict[str, Any]]:
    per_dim = model.get("progress", {}).get("per_dimension", {})
    return [
        {"dimension": name, "status": d["status"], "as_of": d["as_of"], "source": d["source"]}
        for name, d in sorted(per_dim.items())
        if d.get("stale")
    ]
