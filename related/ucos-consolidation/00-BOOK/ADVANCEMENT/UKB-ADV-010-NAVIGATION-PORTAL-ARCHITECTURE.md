# UCOS Ω∞ — NAVIGATION PORTAL ARCHITECTURE

| Field | Value |
|-------|-------|
| ARTIFACT ID | UKB-ADV-010 |
| ARTIFACT | Navigation Portal Architecture (Workstream UKB-010, Deliverable 11) |
| PROGRAM | UCOS Ω∞ UKB Advancement Program (ADV) |
| STATUS | ACTIVE |
| PARENT | UKB-ADV-009 |
| DEPENDS-ON | UKB-ADV-009 |
| VOLUME | VOL-021 (DIGITAL TWIN) |

*Append-only extension overlay on UCOS-BOOK-000000. Renders the existing registries/graph; modifies no existing artifact.*

---

## 1. PURPOSE

A rendered navigation layer over the whole book. Support: **Master Index · Volume Index · Artifact Pages · Dependency Navigation · Backlinks · Breadcrumbs · Forward Navigation · Return Navigation.** Requirements: **every page reachable · every page supports reverse navigation · no dead ends.**

## 2. PAGE TYPES

| Page | Renders from | Content |
|------|--------------|---------|
| Master Index | `DATA/artifacts.json` | entry point; volumes, programs, portfolio status |
| Volume Index | `DATA/volumes.json` | per-volume membership + page ranges |
| Artifact Page | artifact + graph + signals | header/footer (D2 of book), body, live status, edges |
| Dependency View | `DATA/relationships.json` | Depends-On / Implements / Tests graph around a node |
| Search Page | UKB-011 | query surface + results as navigation targets |

## 3. NAVIGATION MODEL (reuses the book's header/footer spec)

Every rendered artifact page carries:
- **Breadcrumbs:** `Master Index › Volume › Program › Parent › This`.
- **Forward navigation:** children, dependents, `Implemented-By`, `Tested-By`, `Deployed-By`.
- **Return navigation:** parent, volume index, master index (reverse of every forward link).
- **Backlinks:** every inbound edge listed (reverse projection of the graph).
- **Prev/Next:** UPN sequence (total order).

## 4. NO-DEAD-END GUARANTEE

The portal builds from the graph, where Parent/Child and Supersedes/Superseded-By are materialized inverse pairs and all other edge types have reverse projections. The reachability checker (shared with UKB-014) proves: (a) every artifact is reachable from `UCOS-BOOK-000000`; (b) every artifact has ≥1 return path to the master index. A page failing either is a **navigation gap** and blocks certification.

## 5. RENDERING

- **Static:** `ukbx portal` renders Markdown/HTML pages per artifact + indices into `00-BOOK/PORTAL/` (generated; excluded from registration like other generated dirs) — fully navigable offline, zero runtime.
- **Dynamic:** the same intermediate model can back a live server; links are Universal IDs/UPNs (stable), never volatile paths, so no link breaks under growth (UKB-INV-03/05).

## 6. LIVE STATUS ON PAGES

Each artifact page shows its derived twin status (from signals) with provenance chips (`source`, `as_of`), so navigation and operational state are unified in one surface.

*Return: [UKB-ADV-000](UKB-ADV-000-ADVANCEMENT-PROGRAM-MASTER-INDEX.md) · [Master Index](../UCOS-BOOK-000000-UNIVERSAL-MASTER-KNOWLEDGE-BOOK.md)*
