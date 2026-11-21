"""Execution-register connector (EXEC-REG-001 / RUNTIME-006) — a LIVE,
credential-free, DOMAIN-C runtime source.

Reads the append-only execution register (DATA/executions.json, written by
`ukb.py exec`) and rolls each execution instance's forward-only lifecycle state
up to its SUBJECT artifact's ``execution`` dimension in the Digital Twin +
Control Tower. This is DOMAIN-C evidence only (STATUS-001 §1); it is NEVER
projected onto DOMAIN-A/B/D/E (§2 non-projection law) — an execution's runtime
state says nothing about roadmap, architecture, certification, or operational
completion. It is read-only against the register and append-only against the
signal ledger, and embeds no secret (RR-07).

Idempotency / drift-safety (UKB-ADV-INV-07; F-1 drift gate): each signal's
idempotency key and ``as_of`` derive from the execution's own recorded
transition (execution_id | lifecycle_state | last_transition_seq / transition
timestamp) — NOT wall-clock — so a replay on unchanged state is de-duplicated by
the append-only ledger and appends nothing; a real lifecycle transition yields a
new key and a new signal, and roll-up uses the latest by ``as_of``.
``high_water`` returns None so no connector cursor is written. Standard library
only; no artifact, execution, or subject is hard-coded.
"""

from __future__ import annotations

import json
import os

import config as C

from . import register
from .base import Connector, make_signal

# The authoritative DATA directory (…/00-BOOK/DATA), resolved relative to this
# connector module so no path is hard-coded beyond the repository layout.
_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "DATA"))


@register
class ExecutionRegisterConnector(Connector):
    name = "execution-register"
    sources = ["EXECUTION"]
    dimensions = ["execution"]
    mode = "POLL_INCREMENTAL"

    def fetch(self, since):
        """Emit one live event per execution whose subject resolves to a
        registered artifact. `since` is ignored: idempotency is enforced by
        append() on a transition-derived event id, so replay is a true no-op."""
        path = os.path.join(_DATA_DIR, C.EXECUTION_STORE_FILE)
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as fh:
                doc = json.load(fh)
        except Exception:
            return []
        events = []
        for eid, r in sorted(doc.get("executions", {}).items()):
            subj = r.get("subject_universal_id")
            if not subj:
                continue                          # no registered subject → nothing to roll up
            events.append({
                "source_event_id": f"{eid}|{r.get('lifecycle_state')}|{r.get('last_transition_seq')}",
                "subject_universal_id": subj,
                "as_of": r.get("last_transition_at"),
                "execution_id": eid,
                "lifecycle_state": r.get("lifecycle_state"),
                "name": r.get("name"),
            })
        return events

    def high_water(self, events):
        # No cursor is persisted: every observation is idempotent by construction,
        # so the connector-cursor store stays byte-stable (F-1 drift gate).
        return None

    def normalize(self, ev, ctx):
        subj = self.resolve(ev, ctx)              # resolves to the declared subject (explicit)
        state = C.EXECUTION_STATE_TO_SIGNAL.get(ev.get("lifecycle_state"), "PLANNED")
        yield make_signal(
            ctx["next_signal_id"](), subj, "execution", state, "EXECUTION",
            evidence=f"exec:{ev.get('execution_id')}:{ev.get('lifecycle_state')}",
            metrics={"execution_id": ev.get("execution_id"),
                     "lifecycle_state": ev.get("lifecycle_state"),
                     "name": ev.get("name")},
            connector=self.name, ingest_run=ctx["ingest_run"], as_of=ev.get("as_of"))
