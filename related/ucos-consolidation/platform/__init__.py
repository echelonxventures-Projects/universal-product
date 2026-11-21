"""UCOS EC-2 ``platform`` package root — stdlib-safe shim.

The EC-2 Platform Realization Program's authoritative deliverable path is
``platform/foundation/`` (per ``06-IMPLEMENTATION/UCOS-EC-2-PLATFORM-REALIZATION-PROGRAM.md``).
Because ``platform`` is also the name of a Python standard-library module, a naive
package here would *shadow* the stdlib module for the whole interpreter and break
tooling (pytest, coverage, setuptools all ``import platform``).

To honor the mandated deliverable path **without** breaking the toolchain, this
package is a **transparent shim**: it loads the genuine standard-library
``platform`` module by file location and re-exports its public API into this
package namespace. Therefore:

    * ``import platform``            → exposes the real stdlib API (``system()``,
      ``python_version()``, ``machine()``, …) — tooling is unaffected;
    * ``import platform.foundation`` → resolves the EC-2 Platform Foundation, because
      this remains a real package with a ``__path__``.

This shim is additive and reads nothing from the certified corpus. It is *not* an
EC-2 foundation module; it exists solely to reconcile the reserved package name.
"""

from __future__ import annotations

import importlib.util as _importlib_util
import os as _os
import sysconfig as _sysconfig

# Load the genuine standard-library ``platform`` module by its file location,
# bypassing this shadowing package, under a private module name.
_stdlib_platform_path = _os.path.join(_sysconfig.get_paths()["stdlib"], "platform.py")
_spec = _importlib_util.spec_from_file_location("_ucos_stdlib_platform", _stdlib_platform_path)
if _spec is None or _spec.loader is None:  # pragma: no cover - defensive
    raise ImportError(
        f"could not locate the standard-library 'platform' module at {_stdlib_platform_path!r}"
    )
_stdlib_platform = _importlib_util.module_from_spec(_spec)
_spec.loader.exec_module(_stdlib_platform)

# Re-export the stdlib public API so ``import platform`` behaves exactly as usual.
for _name in dir(_stdlib_platform):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_stdlib_platform, _name)

del _importlib_util, _os, _sysconfig, _spec, _stdlib_platform_path, _name
