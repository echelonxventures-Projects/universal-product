"""
UCOS Ω∞ UKB Advancement — Connector Framework (UKB-001).

Append-only, authority-neutral connector layer that ingests authoritative
external state into append-only Signal records keyed by Universal Artifact ID.
Standard library only. Embeds no secret (RR-07): credentials are external
secret-manager handles only. Modifies no existing artifact and does not import
or alter the foundation engine (00-BOOK/tools/ukb.py).
"""

from .base import (  # noqa: F401
    SOURCES,
    DIMENSIONS,
    STATE_ORDER,
    Connector,
    SignalLedger,
    rollup_dimensions,
    make_signal,
)

REGISTRY = {}


def register(cls):
    """Class decorator: register a connector implementation by its name."""
    inst = cls()
    REGISTRY[inst.name] = cls
    return cls


# ---------------------------------------------------------------------------
# UMB-IMP-004 — LIVE SOURCE DISCOVERY (dynamic connector discovery).
#
# Auto-discover every connector module in this package and import it so its
# @register decorator runs, populating REGISTRY. This REPLACES the previous
# hard-coded import list (`from connectors import github_actions, trivy, …`),
# which pinned the connector set at four and violated the mission constraint
# "No hard-coded connector lists / Infinite connector expansion" (AUTH-INF-001
# CR-INF-003/010; UMB-012 §4/§6). Dropping a new `*.py` connector into this
# package is now sufficient for it to participate — zero core edit, no ceiling.
#
# Discovery is metadata-free and list-free: it enumerates the package's own
# modules (skipping the framework module `base` and dunder/private modules),
# so participation is configuration-driven (the presence of the file) rather
# than enumerated in code. Idempotent and import-safe (already-imported modules
# are a no-op; a module that fails to import is isolated and reported, never
# aborting discovery — Synchronization Recovery at the discovery boundary).
# ---------------------------------------------------------------------------
_SKIP_MODULES = {"base"}


def discover(verbose: bool = False):
    """Import every connector module in this package so @register runs.
    Returns (registered_names, failures) where failures is a list of
    (module_name, error_str). Never raises for a single bad module."""
    import importlib
    import pkgutil

    failures = []
    for modinfo in pkgutil.iter_modules(__path__):
        name = modinfo.name
        if name in _SKIP_MODULES or name.startswith("_"):
            continue
        try:
            importlib.import_module(f"{__name__}.{name}")
        except Exception as exc:  # isolate a broken connector; keep discovering
            failures.append((name, f"{type(exc).__name__}: {exc}"))
            if verbose:
                print(f"  connector discovery: SKIPPED {name} ({exc})")
    return sorted(REGISTRY.keys()), failures
