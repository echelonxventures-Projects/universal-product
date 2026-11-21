"""``python -m engine.enforcement_closure`` — dispatch to the gate."""

from __future__ import annotations

from engine.enforcement_closure.gate import main

if __name__ == "__main__":  # pragma: no cover - CLI dispatch
    raise SystemExit(main())
