"""SonarQube connector (UKB-001; UMB-IMP-004) — offline replay reference impl.

Demonstrates INFINITE CONNECTOR EXPANSION with ZERO core edit: this file was
added to the connectors package and is picked up automatically by
`connectors.discover()` (UMB-IMP-004 Live Source Discovery) — no import list,
no registry edit, no ceiling (AUTH-INF-001 CR-INF-003/010; UMB-012 §4/§6).

Reads a fixture analysis file and emits `quality` signals. A quality gate that
fails, or a maintainability rating worse than the target, -> BLOCKED; otherwise
APPROVED. A live implementation swaps `fetch` for the SonarQube Web API polled
since the stored cursor; `normalize` stays identical. Credentials would be an
external secret-manager handle only (RR-07). It declares its own polling cadence
to prove per-connector, cadence-driven scheduling (no connector is named in
config).
"""

from __future__ import annotations

import json
import os

from . import register
from .base import Connector, make_signal

_FIX = os.path.join(os.path.dirname(__file__), "fixtures", "sonarqube.json")


@register
class SonarQubeConnector(Connector):
    name = "sonarqube"
    sources = ["SONARQUBE"]
    dimensions = ["quality"]
    mode = "POLL_INCREMENTAL"
    cadence_seconds = 1800  # per-connector schedule override (30 min)

    def fetch(self, since):
        events = json.load(open(_FIX, encoding="utf-8")) if os.path.exists(_FIX) else []
        return [e for e in events if since is None or e.get("as_of", "") > since]

    def normalize(self, ev, ctx):
        subj = self.resolve(ev, ctx)
        gate = str(ev.get("quality_gate", "OK")).upper()
        rating = str(ev.get("maintainability", "A")).upper()
        state = "BLOCKED" if (gate == "ERROR" or rating not in ("A", "B")) else "APPROVED"
        metrics = {"quality_gate": gate, "maintainability": rating,
                   "coverage": ev.get("coverage"), "code_smells": ev.get("code_smells"),
                   "bugs": ev.get("bugs"), "duplication": ev.get("duplication")}
        yield make_signal(
            ctx["next_signal_id"](), subj, "quality", state, "SONARQUBE",
            subject_native_id=ev.get("native_id"),
            evidence=ev.get("dashboard"), metrics=metrics,
            connector=self.name, ingest_run=ctx["ingest_run"], as_of=ev.get("as_of"))
