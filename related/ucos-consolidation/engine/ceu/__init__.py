"""UCOS-CEU-001 — the Constitutional Existence substrate.

The package marker for the existence substrate. Every sibling package under ``engine/``
carries one; this package was the sole exception, which made it a NAMESPACE package rather
than a declared one.

Why the marker is required rather than cosmetic (P0-FINAL-CONVERGENCE-001). The build
declares its distribution contents with ``[tool.setuptools.packages.find]`` over
``include = ["engine*"]``, and that resolver admits a directory only when it carries an
``__init__.py``. Without this file ``engine.ceu`` was absent from the wheel, while
``pyproject.toml`` simultaneously declared it measured (``--cov=engine.ceu``,
``source = [… "engine/ceu" …]``) and depended on it through the ``ucos-nucleus`` console
script: :mod:`engine.nucleus.authority` imports :mod:`engine.ceu.catalog` and
:mod:`engine.ceu.existence`, so the published entry point would have failed at import from
an installed distribution while passing from a source checkout, where the working directory
supplies the module instead. A capability that runs only from the tree it was written in is
not a shipped capability.

This module declares no names of its own. The substrate's surface is its modules —
:mod:`engine.ceu.existence`, :mod:`engine.ceu.catalog`, :mod:`engine.ceu.possessions`,
:mod:`engine.ceu.sufficiency` and :mod:`engine.ceu.errors` — which every consumer and every
test already imports directly. Re-exporting them here would create a second surface for the
same substrate, which is the duplication the convergence register exists to refuse.
"""

from __future__ import annotations
