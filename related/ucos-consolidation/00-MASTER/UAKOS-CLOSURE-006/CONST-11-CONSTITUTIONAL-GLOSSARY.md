# CONST-11 — Constitutional Glossary

> PROGRAM UAKOS-CLOSURE-006 · PHASE-001 · Read-only · Baseline `b67a720`
> Permanent, frozen terminology. Where a term is defined at length elsewhere, the cross-reference is given.

| Term | Frozen meaning | Ref |
|------|----------------|-----|
| Repository Truth | The governed repository as the single source of truth; owned solely by UKB. | CONST-01 |
| Knowledge Once | Each concept has exactly one canonical home; no duplicate canonical stores. | CONST-01 |
| Single Canonical Authority | One authority (UKB) governs canonical representation. | CONST-01 |
| Single Repository Engine | One engine (UKB) owns truth; pipeline stages are derived. | CONST-08 |
| Single Governance Authority | One governance authority; no competing governance. | CONST-07/16 |
| Single Canonical Registry | One registry; no competing registries. | CONST-16 |
| Fail-Closed Governance | Absence of evidence never yields a positive closure claim. | CONST-01 |
| Deterministic Execution | Analyses are re-runnable and reproduce identical results. | CONST-06 |
| Evidence Before Conclusion | No speculation, inferred completeness, or fabricated closure. | CONST-01 |
| Repository Closure | All required concepts of a domain assimilated; per-domain, never global. | CONST-01 |
| Repository Integrity (Domain A) | Internal canonical correctness of governed artifacts. CLOSED at 398/0. | CONST-02 |
| Vision Assimilation (Domain B) | Assimilation of external knowledge into truth. NOT-CLOSED at 506/110. | CONST-03 |
| Repository Completeness | 100% of concepts hold a disposition; no UNKNOWN. | CONST-01 |
| Repository Representation | Every concept has a canonical location/identity. | CONST-01 |
| Knowledge Assimilation | Incorporation of a discovered unit into a canonical home with governance. | CONST-01 |
| Conversation Assimilation | Assimilation of conversation-only concepts (`conversation_only` gap). | CONST-01/03 |
| Upload Assimilation | Assimilation of upload-only concepts (`upload_only` gap). | CONST-01 |
| Canonical Representation | Single authoritative form/location of a concept. | CONST-01 |
| Architectural Completeness | Every concept has representation/governance/ownership/disposition/authority/destination. | CONST-04 |
| Governance Completeness | All concepts under one authority; no competing governance. | CONST-01/16 |
| Validation Completeness | All governed concepts pass structural + referential validation. | CONST-01 |
| Certification Completeness | Independent certification a domain meets criteria. | CONST-01 |
| Operational Completeness | Pipeline is operable, deterministic, re-runnable end-to-end. | CONST-01/08 |
| Disposition | One of IMPLEMENTED / SPECIFIED / DEFERRED / REJECTED per concept. | CONST-04/06 |
| Gap | An open closure deficiency (unhomed, orphan, duplicate, conversation/upload-only, enrichment). | CONST-06 |
| Homed | Concept has a canonical home (`homed=true`). | CONST-02 |
| Orphan | Concept with no governing reference. | CONST-02 |
| Enrichment Item | A planned unit of Domain-B assimilation (110 planned). | CONST-03 |
| Wave | An ordered batch of enrichment items (CLOSURE-003). | CONST-07/08 |
| UKB | Universal Knowledge Base — sole authority engine (`00-BOOK/tools/ukb.py`). | CONST-08/16 |
| Derived Pipeline | Non-authoritative analytical/operational engine stage. | CONST-08 |
| CLOSED / NOT-CLOSED | Per-domain determination: `determination==CLOSED` AND `gap_total==0`. | CONST-06 |
| REPOSITORY COMPLETE (D1) | Domain A CLOSED. | CONST-05 |
| VISION COMPLETE (D2) | Domain B CLOSED. | CONST-05 |
| FULLY CLOSED (D3) | D1 ∧ D2. Never one alone. | CONST-05 |
| Baseline | Fixed commit at which evidence is read (`b67a720`). | all |

**Rule:** These meanings are frozen. Amendments occur only through the evolution path (CONST-10).
