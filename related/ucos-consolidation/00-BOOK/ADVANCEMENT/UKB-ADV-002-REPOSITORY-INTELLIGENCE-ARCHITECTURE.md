# UCOS Ω∞ — REPOSITORY INTELLIGENCE LAYER ARCHITECTURE

| Field | Value |
|-------|-------|
| ARTIFACT ID | UKB-ADV-002 |
| ARTIFACT | Repository Intelligence Layer Architecture (Workstream UKB-002, Deliverable 3) |
| PROGRAM | UCOS Ω∞ UKB Advancement Program (ADV) |
| STATUS | ACTIVE |
| PARENT | UKB-ADV-001 |
| DEPENDS-ON | UKB-ADV-001 |
| VOLUME | VOL-021 (DIGITAL TWIN) |

*Append-only extension overlay on UCOS-BOOK-000000. Every repository becomes a first-class Universal Artifact. Modifies no existing artifact.*

---

## 1. PURPOSE

Make every repository a first-class artifact and track its living structure: **Repository · Branch · Commit · Pull Request · Release · Tag · Contributor · Dependency · Build.**

## 2. ENTITY MODEL (append-only Universal Artifacts)

| Entity | Category | Key attributes | Schema |
|--------|----------|----------------|--------|
| Repository | `REPO` | url, default_branch, visibility, owner, languages, latest_commit | `repository.schema.json` |
| Branch | `REPO` (sub) | name, head_commit, protected | (embedded) |
| Commit | `CMT` | sha, author, message, parents, timestamp, files_changed | (embedded/entity) |
| Pull Request | `CMT` (sub) | number, state, source→target branch, reviews, checks | (embedded) |
| Release / Tag | `BLD` | tag, semver, artifacts, notes, published_at | `build.schema.json` |
| Contributor | `REPO` (ref) | handle, commits, roles | (embedded) |
| Dependency | `REPO` (ref) | name, version (pinned), ecosystem, advisory refs | (embedded) |
| Build | `BLD` | workflow, run_id, result, duration, coverage | `build.schema.json` |

Commits/PRs/branches may be stored embedded in the Repository entity for scale, and promoted to their own Universal ID when they are a traceability target (e.g. a commit that implements an architecture artifact).

## 3. TRACEABILITY (the mission's end-to-end chain)

```
Vision → Requirement → Architecture → Repository → Module → File → Commit → Build → Deployment
UCOS-VSN-* → ... → UCOS-ARCH-* → UCOS-REPO-* → (module/file) → UCOS-CMT-* → UCOS-BLD-* → UCOS-DEP-*
```

Edges (all bidirectional via reverse projections):
- `Repository —Implements→ Architecture/Component` (a repo realizes one or more architecture artifacts)
- `Commit —Implements→ Requirement/Component` (conventional-commit / PR body references native ids)
- `Build —References→ Commit`, `Build —Deploys→ Environment` (see UKB-006)
- `Repository —Uses→ Dependency`

## 4. SIGNALS

| Source | Produces | Effect |
|--------|----------|--------|
| GitHub | repo/branch/commit/PR/release facts | Repository entity refresh; `implementation` signals |
| GitHub Actions | build results | `BLD` status; `build` dimension |
| SonarQube | quality gate, coverage | Repository `quality` metrics |
| OWASP/Trivy | dependency vulnerabilities | Repository `security` metrics (feeds UKB-005) |

Repository `derived_status` = worst-of(build, quality, security) blocking view, recomputed from latest signals.

## 5. DENSITY & SCALE

Commit history is unbounded; the layer stores a rolling window of full commit entities plus aggregate counters, with older commits summarized (append-only summaries, never deleted). Repository membership links to modules/files by path so the existing artifact `path` field is the join key — no renaming.

## 6. TRACEABILITY GUARANTEE

No orphan repository: every `REPO` must `Implements` at least one architecture/implementation artifact or be flagged as an **unmapped repository gap** (UKB-ADV-INV-05). Reverse navigation (`Implemented-By`) lets any architecture artifact list the repositories realizing it.

*Return: [UKB-ADV-000](UKB-ADV-000-ADVANCEMENT-PROGRAM-MASTER-INDEX.md) · [Master Index](../UCOS-BOOK-000000-UNIVERSAL-MASTER-KNOWLEDGE-BOOK.md)*
