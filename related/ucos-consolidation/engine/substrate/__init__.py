"""UCOS as a CONSUMER of the UAKP substrate.

THE DIRECTION OF THIS DEPENDENCY IS THE WHOLE POINT. UAKP knows nothing about UCOS — no
path, no register, no declaration name appears anywhere in it, and a test in that repository
refuses their appearance. Everything UCOS-specific lives here, on the consumer side, which
is what makes the substrate reusable by anything else. An adapter in the substrate would
have been the extraction undone in one commit.

IT IS NOT A RUNTIME DEPENDENCY, AND COULD NOT BE. `pyproject.toml` declares
`dependencies = []` on constitutional grounds (TP-04, TP-05), ISD-L-09 refuses a pinned
runtime dependency, and `test_infinite_scope.py` asserts the list is empty. So consumption
happens in the GOVERNANCE plane, where declared tooling already lives. The runtime core
remains stdlib-only and untouched.

IT FAILS CLOSED WHEN THE SUBSTRATE IS ABSENT. The substrate has published no release, so it
is installed from a local path today. A gate that quietly passed when its subject could not
be loaded would be the silent false green this whole apparatus exists to prevent — so an
absent substrate is a FAULT (exit 2, no verdict), never a pass.
"""

from __future__ import annotations

SUBSTRATE_REQUIREMENT = "uakp>=0.0.1"

__all__ = ["SUBSTRATE_REQUIREMENT"]
