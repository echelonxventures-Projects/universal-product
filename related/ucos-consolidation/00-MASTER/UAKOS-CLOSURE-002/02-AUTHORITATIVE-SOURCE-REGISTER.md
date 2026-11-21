# Output 02 — AUTHORITATIVE SOURCE REGISTER (UAKOS-CLOSURE-002)

> AUTHORITY = NONE (derived). Sources authoritative via `00-SOURCE-MANIFEST/SOURCE-HASHES.txt` (SHA-256) and git. HEAD `b67a720`.
> Fields per mission Phase-0: Source ID · Name · Type · Authority · Origin · Version · Checksum · Owner · Repository Location · Repository Status · Ingestion Status · Coverage Status · Closure Status · Last Reconciled · Evidence · Certification State.

Common values unless noted — Owner: `UCOS-PROGRAM-CUSTODIAN` · Last Reconciled: `2026-07-22` · Certification State: see per-row.

## A. Frozen original sources (`00-SOURCE/**`) — checksummed, FROZEN

| Source ID | Name | Type | Authority | Version | SHA-256 (prefix) | Repo Status | Ingestion | Coverage | Closure |
|-----------|------|------|:---------:|:-------:|------------------|:-----------:|:---------:|:--------:|:-------:|
| SRC-VIS-01 | Missing 1.docx | Vision | HIGHEST(content) | frozen | `9c0c8519…` | FROZEN | REGISTERED | UNVERIFIED | UNDETERMINED |
| SRC-VIS-02 | Missing 2.docx | Vision | HIGHEST | frozen | `92cdece0…` | FROZEN | REGISTERED | UNVERIFIED | UNDETERMINED |
| SRC-VIS-03 | Missing 3.docx | Vision | HIGHEST | frozen | `cef7ab6f…` | FROZEN | REGISTERED | UNVERIFIED | UNDETERMINED |
| SRC-CON-01 | UCOS Ω.docx | Constitution | HIGHEST | frozen | `0fdfcde0…` | FROZEN | REGISTERED | UNVERIFIED | UNDETERMINED |
| SRC-CON-02 | UCOS Ω∞ ABSOLUTE ARCHITECTURAL CONSTITUTION.docx | Constitution | HIGHEST | frozen | `226fb0e0…` | FROZEN | REGISTERED | UNVERIFIED | UNDETERMINED |
| SRC-CON-03 | UCOS Ω∞ UNIVERSAL REALITY COMPILER CONSTITUTION.docx | Constitution | HIGHEST | frozen | `97b7db34…` | FROZEN | REGISTERED | UNVERIFIED | UNDETERMINED |
| SRC-CON-04 | Universal Commerce Compiler Constitution.docx | Constitution | HIGHEST | frozen | `47126cc9…` | FROZEN | REGISTERED | UNVERIFIED | UNDETERMINED |
| SRC-ARC-01 | UCOS Ω∞ - Universal Platform.docx | Architecture | HIGHEST | frozen | `719ba6fc…` | FROZEN | REGISTERED | UNVERIFIED | UNDETERMINED |
| SRC-ARC-02 | Final Architechture.docx | Architecture | HIGHEST | frozen | `687e576b…` | FROZEN | REGISTERED | UNVERIFIED | UNDETERMINED |
| SRC-PHS-01 | …Operating System_Part-001(Phase-000-019).docx | Phases | HIGHEST | frozen | `f2830c9a…` | FROZEN | REGISTERED | UNVERIFIED | UNDETERMINED |
| SRC-PHS-02 | …Part-001(Phase-020-050).docx | Phases | HIGHEST | frozen | `91f0602b…` | FROZEN | REGISTERED | UNVERIFIED | UNDETERMINED |
| SRC-PHS-03 | …Part-002(Phase-020-024-Time-001-160).docx | Phases | HIGHEST | frozen | `7a4f3d52…` | FROZEN | REGISTERED | UNVERIFIED | UNDETERMINED |
| SRC-PHS-04 | …Part-003(Phase-024-time-161-211 to 50).docx | Phases | HIGHEST | frozen | `1a439055…` | FROZEN | REGISTERED | UNVERIFIED | UNDETERMINED |

Origin for all A-rows: `00-SOURCE/{VISION,CONSTITUTIONS,ARCHITECTURE,PHASES}/`. Evidence: `00-SOURCE-MANIFEST/SOURCE-HASHES.txt` + `SOURCE-FILES.txt`.

**Ingestion note:** "REGISTERED" means the source file exists in Repository Truth and is corpus-tracked. It does **NOT** mean every concept inside it has been extracted and matched (Phases 2–4 not run) — hence Coverage = UNVERIFIED and Closure = UNDETERMINED for all rows. This is the honest, fail-closed state.

## B. Uploaded master plans (root) — REGISTERED, ACTIVE

| Source ID | Name | Type | Authority | Repo Location | Status | Ingestion | Coverage | Closure |
|-----------|------|------|:---------:|---------------|:------:|:---------:|:--------:|:-------:|
| SRC-UPL-01 | UCOS Ω∞ MASTER END-TO-END PROGRAM.docx | Uploaded plan | HIGH | `/` (root) | ACTIVE | REGISTERED | UNVERIFIED | UNDETERMINED |
| SRC-UPL-02 | UCOS Ω∞ MASTER EVOLUTION PATH - Plan.docx | Uploaded plan | HIGH | `/` | ACTIVE | REGISTERED | UNVERIFIED | UNDETERMINED |
| SRC-UPL-03 | UCOS-Consolidation Plan.docx | Uploaded plan | HIGH | `/` | ACTIVE | REGISTERED | UNVERIFIED | UNDETERMINED |
| SRC-UPL-04 | UCOS-OMEGA-INFINITY-MASTER-IMPLEMENTATION-PLAN-V2.md | Master plan | HIGH | `/` | ACTIVE | REGISTERED | UNVERIFIED | UNDETERMINED |

## C. Derived / generated knowledge stores — MACHINERY / PROJECTION

| Source ID | Name | Type | Authority | Location | Status |
|-----------|------|------|:---------:|----------|:------:|
| SRC-GEN-01 | Universal Artifact Registry (+ 5 registries) | Projection | NONE (derived) | `00-BOOK/REGISTRIES/*` | regenerable |
| SRC-GEN-02 | Digital Twin / Control Tower | Projection | NONE | `00-BOOK/DATA/control-tower.json` | regenerable |
| SRC-GEN-03 | id-ledger (append-only allocation) | Ledger | HIGH | `00-BOOK/DATA/id-ledger.json` | append-only |
| SRC-GEN-04 | Signals ledger + connector cursors | Evidence | HIGH | `00-BOOK/DATA/{signals,connector-cursors}.json` | append-only |
| SRC-GEN-05 | Generator machinery | Machinery | MACHINERY | `00-BOOK/tools/{ukb,ukbx,config}.py` | code |

## D. Unregistered / external sources (declared, not proven present)

| Source ID | Name | Type | Status | Gap |
|-----------|------|------|:------:|-----|
| SRC-EXT-01 | Shared chat exports / master chat compilations | Conversation | **UNREGISTERED** | G-05 — cannot prove "Zero Conversation-only Knowledge" |

**Register completeness:** every source discoverable **within Repository Truth** is registered above. Sources outside the repository (external chat exports, if any) are declared as SRC-EXT-01 and remain the mission's open ingestion gap.
