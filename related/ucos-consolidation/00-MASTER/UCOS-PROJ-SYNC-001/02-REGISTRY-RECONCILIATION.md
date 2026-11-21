# 02 — REGISTRY RECONCILIATION

**Authority:** append-only `00-BOOK/DATA/id-ledger.json` (the immutable
allocation record). Every registration below is evidenced by an `id-ledger`
entry with a `first_seen` timestamp that fixes its provenance.

---

## 1. Registration delta

The synchronization advanced the page cursor `9001 → 9134` and registered
**10 new artifacts** (0 renumbered, 0 removed, 0 duplicated). Provenance is
determined **solely** by the immutable `first_seen` timestamp — not inferred.

### 1.1 Wave 0 synchronization — 1 artifact

`first_seen = 2026-07-23T11:00:27+00:00` (matches Wave 0 commit `0bcea68`).

| Universal ID | Category | Source artifact | Pages |
|---|---|---|---|
| `UCOS-USIS-000001` | USIS | `15-UNIVERSAL-SCIENCE-INTELLIGENCE/USIS-GOV-000-UNIVERSAL-SCIENCE-INTELLIGENCE-PROGRAM-ESTABLISHMENT-DETERMINATION.md` | 9133–9134 |

This is the projection of the USIS program established by Wave 0. The source
`.md` was already committed in `0bcea68`; only its **projection** (registry
entry, page allocation, `USIS` program in the control tower, portal page
`UCOS-USIS-000001`, graph edges) was deferred and is realized here. The Wave 0
`config.py` change (+43 lines declaring USIS as a first-class program) is what
makes `USIS` a distinct program column in the control tower.

### 1.2 Pre-existing projection reconciliation — 9 artifacts

`first_seen = 2026-07-23T06:39:49+00:00` (**predates** Wave 0's 11:00:27
timestamp). These are relocated architectural/reference source documents that
were placed on disk but **never registered** — historical drift unrelated to
Wave 0.

| Universal ID | Category | Source artifact | Prior git state |
|---|---|---|---|
| `UCOS-REF-000007` | REF | `04-REFERENCE/ARCHITECTURAL-SOURCES/README.md` | tracked (commit `0a491c2`), unregistered |
| `UCOS-REF-000008` | REF | `04-REFERENCE/ARCHITECTURAL-SOURCES/UCOS Ω∞ MASTER END-TO-END PROGRAM.docx` | tracked (`0a491c2`), unregistered |
| `UCOS-REF-000009` | REF | `04-REFERENCE/ARCHITECTURAL-SOURCES/UCOS Ω∞ MASTER EVOLUTION PATH - Plan.docx` | tracked (`0a491c2`), unregistered |
| `UCOS-REF-000010` | REF | `04-REFERENCE/ARCHITECTURAL-SOURCES/UCOS-Consolidation Plan.docx` | tracked (`0a491c2`), unregistered |
| `UCOS-REF-000011` | REF | `04-REFERENCE/ChatGPT Chat.docx` | untracked source, unregistered |
| `UCOS-REF-000012` | REF | `04-REFERENCE/PHASE.docx` | untracked source, unregistered |
| `UCOS-REF-000013` | REF | `04-REFERENCE/UCOS Ω - references.docx` | untracked source, unregistered |
| `UCOS-REF-000014` | REF | `04-REFERENCE/UCOS Ω∞ MASTER IMPLEMENTATION PLAN v2.docx` | untracked source, unregistered |
| `UCOS-REF-000015` | REF | `04-REFERENCE/UNIVERSAL REALITY COMPILER CONSTITUTION.docx` | untracked source, unregistered |

The five previously-untracked `.docx` sources (`REF-000011`…`000015`) were
committed as part of the convergence commit so the committed registry never
references an uncommitted file (baseline coherence). Their content was not
altered.

## 2. Provenance separation (no fabrication)

The two provenance classes are distinguished **only** by the immutable
`first_seen` field of the append-only ledger:

- `…T06:39:49` → pre-existing reconciliation (9 REF artifacts)
- `…T11:00:27` → Wave 0 synchronization (1 USIS artifact)

No provenance was inferred or fabricated; each claim is a direct read of
`id-ledger.json`.

## 3. Ownership invariants (post-sync)

From `ukb enforce`, `ukb validate`, and `ukbx certify`:

- **Unique canonical ownership:** 1002 artifacts, **1002 unique Universal IDs**;
  no overlapping page ranges; `page_cursor (9134) == max_page_end (9134)`.
- **Zero duplicate registrations:** `no duplicate Universal IDs` check → PASS.
- **Zero orphan registrations:** eligible on-disk artifacts (1002) == registered
  (1002); every artifact present in id-ledger; all 11,839 graph edges resolve to
  real endpoints (`no dangling edge endpoints` → PASS).
- **Append-only integrity:** page ledger intact; snapshot history sequence
  monotonic; `repo-operations.json` already tracked and registered — unchanged.

Category totals of note: `REF = 15`, `USIS = 1`. Program count includes a new
first-class `USIS` program (PROVISIONAL tier per Wave 0).
