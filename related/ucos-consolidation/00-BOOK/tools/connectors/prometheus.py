"""Prometheus connector (UKB-001/007) — offline replay reference implementation.

Reads a fixture metrics file and emits `production`/`operational` signals.
Availability below SLO target -> BLOCKED; otherwise PRODUCTION. Live impl polls
the Prometheus HTTP API since the stored cursor; `normalize` stays identical.
"""

from __future__ import annotations

import json
import os

from . import register
from .base import Connector, make_signal

_FIX = os.path.join(os.path.dirname(__file__), "fixtures", "prometheus.json")


@register
class PrometheusConnector(Connector):
    name = "prometheus"
    sources = ["PROMETHEUS"]
    dimensions = ["production", "operational"]
    mode = "POLL_INCREMENTAL"

    def fetch(self, since):
        events = json.load(open(_FIX, encoding="utf-8")) if os.path.exists(_FIX) else []
        return [e for e in events if since is None or e.get("as_of", "") > since]

    def normalize(self, ev, ctx):
        subj = self.resolve(ev, ctx)
        avail = float(ev.get("availability", 1.0))
        target = float(ev.get("slo_target", 0.99))
        err = float(ev.get("error_rate", 0.0))
        state = "BLOCKED" if avail < target else "PRODUCTION"
        metrics = {"availability": avail, "slo_target": target,
                   "error_rate": err, "latency_p99_ms": ev.get("latency_p99_ms")}
        yield make_signal(
            ctx["next_signal_id"](), subj, "production", state, "PROMETHEUS",
            subject_native_id=ev.get("native_id"),
            evidence=ev.get("dashboard"), metrics=metrics,
            connector=self.name, ingest_run=ctx["ingest_run"], as_of=ev.get("as_of"))
        ostate = "BLOCKED" if err > float(ev.get("error_budget", 0.01)) else "PRODUCTION"
        yield make_signal(
            ctx["next_signal_id"](), subj, "operational", ostate, "PROMETHEUS",
            subject_native_id=ev.get("native_id"),
            evidence=ev.get("dashboard"), metrics={"error_rate": err},
            connector=self.name, ingest_run=ctx["ingest_run"], as_of=ev.get("as_of"))
