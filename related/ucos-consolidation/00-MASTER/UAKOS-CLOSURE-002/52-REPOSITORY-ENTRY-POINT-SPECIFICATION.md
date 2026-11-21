# 52 — Repository Entry Point Specification (Phase-004)

| Field | Value |
|-------|-------|
| PROGRAM | UAKOS-CLOSURE-002 · PHASE-004 |
| STATUS | PLANNING / GOVERNANCE — no implementation artifact modified |
| AUTHORITY | NONE — DERIVED TRUTH |
| BASELINE | HEAD `b67a720` |

> The official ways knowledge enters Repository Truth through the closure pipeline. Each entry point states Input → Processing → Validation → Repository destination → Closure requirement. In all cases the **destination writer is S0 (ukb)**; the pipeline produces reconciliation evidence only.

| Entry point | Input | Processing (stages) | Validation | Repository destination (canonical home) | Closure requirement |
|-------------|-------|---------------------|------------|------------------------------------------|---------------------|
| **New Constitution** | `.docx`/`.md` constitution | S1 ingest → S2 extract → S3 match → S6 gaps | `ukb validate` + `CEP-004`; No-Orphan | `02-MASTER/` (+ `00-CEP/` if constitutional-engineering) | homed once; `CEP-006` ratification; traceability to Vision |
| **New Architecture** | architecture doc | S1–S3 → S5 trace | `ukb validate`; `UCOS-GOV-002` | `02-MASTER/` `ARCH-*` / band spec | homed; linked to constitution; disposition SPECIFIED+ |
| **New Universe** | universe definition | S1–S3 → S4 graph | `AEOS-001` admission | `02-MASTER/…UNIVERSE-CATALOG` | admitted via AEOS-001; no duplicate universe |
| **New Capability** | capability spec | S1–S3 → S7 plan | `UCIC-001` contract + `EC-3 AP-N` | `02-MASTER/…CAPABILITY-CATALOG` + band | UCIC-001 satisfied; validated+certified for IMPLEMENTED |
| **New Registry** | registry proposal | S3 match (dedup vs existing registries) | Knowledge-Once check | `00-BOOK/REGISTRIES/*` (via ukb only) | **must reuse** existing registry unless proven distinct; no parallel registry |
| **New Uploaded Source** | root/`00-SOURCE` upload | S1 ingest → hash-pin (`SOURCE-HASHES.txt`) → S2/S3 | checksum + `ukb enforce` | `00-SOURCE/**` (frozen) + registered | file registered; **concepts extracted + matched** for closure (else upload-only gap) |
| **New Shared Conversation** | chat export / compilation | S1 ingest (external corpus scan) → S2/S3 → S6 | conversation reconciliation (doc 54 gate) | extract → decision record (`UKDA-DEC-*`) / spec; then ukb | 0 conversation-only concepts (else gap G-05 open) |
| **New External Knowledge** | any external anchor-bearing text | S1–S3 → S6/S7 | matching + gap proof | canonical home per family, or explicit REJECTED/DEFERRED | reconciled to exactly one disposition |

## Rules

1. Every entry point converges on **one** canonical home; duplicates become **links**, never copies (`UCKO-PRIN-0001`).
2. "Registered file" ≠ "closed knowledge": a source is closed only when its **concepts** are extracted, matched, and disposed (upload/conversation-only remain open gaps until then).
3. No entry point may create a competing registry, ID system, or graph; the destination is always written by S0 (ukb).

---

*END — 52 · Repository Entry Points · AUTHORITY = NONE.*
