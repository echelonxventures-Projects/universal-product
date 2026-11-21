"""Module entry point — ``python -m engine.construct`` runs the one-command surface."""

from __future__ import annotations

from engine.construct.cli import main

if __name__ == "__main__":  # pragma: no cover - module dispatch
    raise SystemExit(main())
