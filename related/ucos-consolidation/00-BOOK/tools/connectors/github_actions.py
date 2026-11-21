"""GitHub Actions connector (UKB-001) — offline replay reference implementation.

Reads a fixture event file and emits `build`/`unit_testing` signals. A live
implementation swaps `fetch` for the GitHub Actions API/webhook; `normalize`
stays identical. Credentials would be an external secret-manager handle only.
"""

from __future__ import annotations

import json
import os

from . import register
from .base import Connector, make_signal

_FIX = os.path.join(os.path.dirname(__file__), "fixtures", "github_actions.json")


@register
class GitHubActionsConnector(Connector):
    name = "github-actions"
    sources = ["GITHUB_ACTIONS"]
    dimensions = ["build", "unit_testing", "release"]
    mode = "EVENT"

    def fetch(self, since):
        events = json.load(open(_FIX, encoding="utf-8")) if os.path.exists(_FIX) else []
        return [e for e in events if since is None or e.get("as_of", "") > since]

    def normalize(self, ev, ctx):
        subj = self.resolve(ev, ctx)
        result = ev.get("result", "UNKNOWN")
        state = {"pass": "IMPLEMENTED", "fail": "BLOCKED",
                 "running": "IN_PROGRESS"}.get(result, "IN_PROGRESS")
        metrics = {"result": result, "duration_seconds": ev.get("duration_seconds"),
                   "coverage": ev.get("coverage"), "workflow": ev.get("workflow")}
        yield make_signal(
            ctx["next_signal_id"](), subj, "build", state, "GITHUB_ACTIONS",
            subject_native_id=ev.get("native_id"),
            evidence=ev.get("run_url"), metrics=metrics,
            connector=self.name, ingest_run=ctx["ingest_run"], as_of=ev.get("as_of"))
        # a passing build with tests also asserts unit_testing progress
        if ev.get("coverage") is not None:
            tstate = "TESTED" if result == "pass" else "BLOCKED"
            yield make_signal(
                ctx["next_signal_id"](), subj, "unit_testing", tstate, "GITHUB_ACTIONS",
                subject_native_id=ev.get("native_id"),
                evidence=ev.get("run_url"), metrics={"coverage": ev.get("coverage")},
                connector=self.name, ingest_run=ctx["ingest_run"], as_of=ev.get("as_of"))
