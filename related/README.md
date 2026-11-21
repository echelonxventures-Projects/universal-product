# related/ — the owner's other projects, in this one repository

Merged on 2026-11-21 with `git subtree add`, so each project's full commit history is part of
this repository's history. Their old GitHub repositories still exist and are not updated any more.

| Folder | Was | Commits brought in | Branch taken |
|---|---|---|---|
| `marketplace/` | `echelonxventures-Projects/marketplace` | 10 | `master` |
| `offer/` | `echelonxventures-Projects/offer` | 13 | `wip/2026-11-07-migrations-scheduler` |
| `product-platform/` | `echelonxventures-Projects/Product-Platform` | 1 | `main` |
| `ucos-architecture/` | `echelonxventures-Projects/UCOS-architecture` | 1 | `main` |
| `ucos-com/` | `echelonxventures-Projects/UCOS-COM` | 18 | `main` |
| `ucos-consolidation/` | `echelonxventures-Projects/ABSOLUTE-FOUNDATION` | 880 | `integration/consolidation-trunk` |
| `ucos-ri/` | `echelonxventures-Projects/UCOS-RI` | 17 | `wip/2026-11-07-s4b-availability` |
| `ucos-universal/` | `echelonxventures-Projects/UCOS-UNIVERSAL` | 30 | `main` |
| `universal-commerce/` | `echelonxventures-Projects/universal-commerce` | 11 | `master` |
| `ucos-knowledge/` | not in git before (copied from the project folder) | — | — |

Only each project's current branch was merged; its other branches remain in its old GitHub
repository. Uncommitted changes and untracked files (dependencies, databases, local data) were
not merged and stay in the original folders.

Rules: the white-label guard (`scripts/white-label.js`) covers the LUXORA platform, not this
folder. The size guard (`scripts/size-guard.js`) covers everything: no file of 50 MB or more.
Start with `RECONCILIATION.md` for how the projects relate.
