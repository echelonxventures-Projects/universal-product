"""UCOS-OMEGA-001 — Universal Discovery: governance derived from executable reality.

AUTHORITY = NONE (DERIVED TRUTH). This package legislates nothing and owns no lifecycle. It
measures, and the measurement's only input is ``git ls-files '*.py'``.

THE ONE CLAIM. No governance verdict in this package quantifies over a list a human wrote. Scope,
authority, reachability, disposition and every threshold are functions of the discovered
population, so a top-level tree that does not exist yet is already governed: the commit that
creates ``quantum/`` puts it inside every measurement here, with no edit to any file.

Read ``model.py`` first — it states the five dispositions and the four ratchet kinds, and why
each is a measurement rather than a preference.

THE PACKAGE ROOT IMPORTS NOTHING, AND THE REASON IS A MEASUREMENT. This file used to import
``model`` eagerly, and pytest loads the package before coverage starts because
``engine.universal_discovery.pytest_scope`` is registered with ``-p``. Every line of ``model.py``
that runs at import — the dispositions, the ratchet kinds, the frozen dataclasses — executed
outside the collector and reported as a miss no test could reach: 62 statements, measured in the
combined shard report while the same suite run with an explicit ``--cov`` (which takes the
plugin's early return and imports nothing here) reported them covered. The root now forwards on
first use (PEP 562), and it forwards by ACCESSING the model rather than by restating a list of
its names: the first attempt held a 16-member literal and ISD-L-01 counted it as the 889th closed
enumeration against a ceiling of 888 — the law this package exists to honour refusing the fix
that hid the measurement. What the root owns is therefore nothing but the route: names are
``model``'s, membership of ``__all__`` is derived at first read, and a future constant needs no
edit here because there is no list here to edit.
"""

#: The one module the root forwards to. A single name, not a set of what it exports.
_FORWARD = "engine.universal_discovery.model"


def _model() -> object:
    from importlib import import_module

    return import_module(_FORWARD)


def __getattr__(name: str) -> object:
    """Resolve a package attribute by importing ``model``, once, on first use.

    ``__all__`` answers from the model's public surface rather than a list kept here, so the
    star-import form cannot go stale against a constant added upstream. Private and dunder
    names are refused without consulting the target: a forwarding root that answered
    ``__wrapped__`` or ``__reduce__`` by accident would make the package pretend to be the
    protocol it was asked about.
    """
    if name == "__all__":
        return sorted(key for key in vars(_model()) if not key.startswith("_"))
    if name.startswith("_"):
        msg = f"module {__name__!r} has no attribute {name!r}"
        raise AttributeError(msg)
    try:
        return getattr(_model(), name)
    except AttributeError:
        msg = f"module {__name__!r} has no attribute {name!r}"
        raise AttributeError(msg) from None


def __dir__() -> list[str]:
    """The public names come from the module they live in, never from a copy made here."""
    return sorted({key for key in vars(_model()) if not key.startswith("_")} | {"__all__"})
