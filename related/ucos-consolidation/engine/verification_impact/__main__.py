"""``python -m engine.verification_impact`` — dispatch only.

A thin dispatcher rather than a copy of :mod:`engine.verification_impact.cli`: two
copies of an entry point are two things to keep in step, and the duplicate would be
measured as dead code.
"""

from __future__ import annotations

from engine.verification_impact.cli import main

raise SystemExit(main())
