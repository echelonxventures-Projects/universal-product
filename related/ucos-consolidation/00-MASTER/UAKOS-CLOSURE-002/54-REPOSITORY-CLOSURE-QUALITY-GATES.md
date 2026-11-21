# 54 — Repository Closure Quality Gates (Phase-004)

| Field | Value |
|-------|-------|
| PROGRAM | UAKOS-CLOSURE-002 · PHASE-004 |
| STATUS | PLANNING / GOVERNANCE — no implementation artifact modified |
| AUTHORITY | NONE — DERIVED TRUTH |
| BASELINE | HEAD `b67a720` |
| RULE | ALL gates PASS ⇒ closure certificate may be green. ANY gate FAIL ⇒ fail-closed. |

## Mandatory gates

| Gate | Pass criterion | Evidence source | Enforced by | Current status @ `b67a720` |
|------|----------------|-----------------|-------------|:--------------------------:|
| **G-KX** Knowledge extraction complete | every in-scope source scanned; anchors extracted | `closure.json` (S2) | `closure_engine` | PASS (extraction runs) |
| **G-CM** Canonical matching complete | every anchor matched or flagged | `closure.json` (S3) | `closure_engine` | PASS |
| **G-DUP** No unresolved duplicates | 0 duplicate canonical homes; 0 UKDA hash dups (`UCKO-RULE-0001`) | `closure.json`.gaps + ukb | `closure_engine` + `ukb validate` | PASS (0 dup) |
| **G-TR** Traceability valid | no broken chain; No-Orphan | `MCP-006` + `ukb` traceability | `ukb` / `UCOS-GOV-002` | **FAIL** (21% any-trace; 10/13 dims empty — see `19`) |
| **G-EV** Evidence complete | all determinations cite present evidence | `15`, `19`, twin | `CEP-008` | PARTIAL |
| **G-VAL** Validation complete | `ukb validate` PASS; `verify.sh` PASS | validate runs | `CEP-004` | PARTIAL (`jsonschema` absent; structural only) |
| **G-CERT** Certification complete | CCE ten-gate PASS for in-scope units | CCE records | `CEP-005` / `UCOS-COMP-000001` | PARTIAL |
| **G-CONV** Conversation reconciliation complete | 0 conversation-only concepts | `closure.json`.gaps.conversation_only | `closure_engine` (S6) | **FAIL** (108 conversation-only) |
| **G-UPL** Upload reconciliation complete | 0 upload-only concepts; each upload's concepts matched | `closure.json`.gaps.upload_only | `closure_engine` (S6) | OPEN (files registered; concepts partial) |
| **G-HOME** Every concept homed with one disposition | 0 not-homed; 0 UNCLASSIFIED | `closure.json`.gaps.not_homed_concepts | `closure_engine` (S3/S5) | **FAIL** (2 unhomed laws Ω∞-008/009) |
| **G-DRIFT** Zero repository drift | `register.sh --guard` clean | guard run | `register.sh` | PASS (guard clean in evidence) |
| **G-DET** Determinism | byte-identical re-run at HEAD | two runs diff | `determinism.yml` | PASS |

## Aggregate gate

**Repository Closure = green iff every gate above = PASS.** At `b67a720`, G-TR / G-CONV / G-HOME are FAIL and G-EV/G-VAL/G-CERT/G-UPL are PARTIAL ⇒ **fail-closed / NOT-CLOSED** (consistent with `19` and `35`). No green certificate may be issued.

## Gate ownership (no duplication)

Gates reuse existing enforcers: `ukb validate`/`enforce` (G-DUP/G-TR/G-DRIFT), `CEP-004` (G-VAL), `CEP-005`/CCE (G-CERT), `CEP-008` (G-EV), `closure_engine` (G-KX/G-CM/G-CONV/G-UPL/G-HOME), `determinism.yml` (G-DET). No new gate engine is introduced; the closure gate is an **aggregator** over existing verdicts.

---

*END — 54 · Quality Gates · AUTHORITY = NONE.*
