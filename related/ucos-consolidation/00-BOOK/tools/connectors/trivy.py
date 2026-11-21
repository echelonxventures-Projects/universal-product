"""Trivy connector (UKB-001/005) — offline replay reference implementation.

Reads a fixture scan file and emits `security` signals. Open CRITICAL/HIGH
without exception -> BLOCKED; otherwise APPROVED. Live impl polls the Trivy
API/report since the stored cursor; `normalize` stays identical.
"""

from __future__ import annotations

import json
import os

from . import register
from .base import Connector, make_signal

_FIX = os.path.join(os.path.dirname(__file__), "fixtures", "trivy.json")


@register
class TrivyConnector(Connector):
    name = "trivy"
    sources = ["TRIVY"]
    dimensions = ["security"]
    mode = "POLL_INCREMENTAL"

    def fetch(self, since):
        events = json.load(open(_FIX, encoding="utf-8")) if os.path.exists(_FIX) else []
        return [e for e in events if since is None or e.get("as_of", "") > since]

    def normalize(self, ev, ctx):
        subj = self.resolve(ev, ctx)
        crit = int(ev.get("critical", 0))
        high = int(ev.get("high", 0))
        med = int(ev.get("medium", 0))
        state = "BLOCKED" if (crit + high) > 0 else "APPROVED"
        yield make_signal(
            ctx["next_signal_id"](), subj, "security", state, "TRIVY",
            subject_native_id=ev.get("native_id"),
            evidence=ev.get("report"), metrics={"critical": crit, "high": high, "medium": med},
            connector=self.name, ingest_run=ctx["ingest_run"], as_of=ev.get("as_of"))
