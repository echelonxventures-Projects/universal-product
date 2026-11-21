"""``python -m engine.verification_intelligence`` — dispatch only.

A thin dispatcher rather than a copy of :mod:`engine.verification_intelligence.cli`:
two copies of an entry point are two things to keep in step, and the duplicate would be
measured as dead code.
"""

from __future__ import annotations

from engine.verification_intelligence.cli import main

raise SystemExit(main())
