"""Kubernetes connector (UKB-001/006) — offline replay reference implementation.

Reads a fixture rollout file and emits `deployment` signals. Rollout complete
-> DEPLOYED; failed -> BLOCKED; progressing -> IN_PROGRESS. Live impl watches the
Kubernetes API / GitOps controller; `normalize` stays identical.
"""

from __future__ import annotations

import json
import os

from . import register
from .base import Connector, make_signal

_FIX = os.path.join(os.path.dirname(__file__), "fixtures", "kubernetes.json")


@register
class KubernetesConnector(Connector):
    name = "kubernetes"
    sources = ["KUBERNETES"]
    dimensions = ["deployment", "production"]
    mode = "EVENT"

    def fetch(self, since):
        events = json.load(open(_FIX, encoding="utf-8")) if os.path.exists(_FIX) else []
        return [e for e in events if since is None or e.get("as_of", "") > since]

    def normalize(self, ev, ctx):
        subj = self.resolve(ev, ctx)
        rollout = ev.get("rollout", "unknown")
        state = {"complete": "DEPLOYED", "failed": "BLOCKED",
                 "progressing": "IN_PROGRESS"}.get(rollout, "IN_PROGRESS")
        metrics = {"rollout": rollout, "tier": ev.get("tier"),
                   "replicas_ready": ev.get("replicas_ready"),
                   "replicas_desired": ev.get("replicas_desired"),
                   "image": ev.get("image")}
        yield make_signal(
            ctx["next_signal_id"](), subj, "deployment", state, "KUBERNETES",
            subject_native_id=ev.get("native_id"),
            evidence=ev.get("namespace"), metrics=metrics,
            connector=self.name, ingest_run=ctx["ingest_run"], as_of=ev.get("as_of"))
