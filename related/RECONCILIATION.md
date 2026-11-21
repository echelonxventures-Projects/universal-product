# Reconciliation of related projects

Checked and moved here on 2026-11-06, at the owner's request. Nothing was merged or deleted, and no
commit was pushed. Each project stays a separate folder with its own git history and GitHub repository.

## Result

| Project | What it is | Git | Only on this machine |
|---|---|---|---|
| `../repo` (LUXORA) | The commerce platform being built | `universal-product`, 227 commits | `data/`, keys, the owner directive |
| `UCOS-UNIVERSAL` | Platform-factory specification and kernel: master architecture, universe constitutions, ADRs | `UCOS-UNIVERSAL`, 30 commits, on `main` | No commits. `UCOS-MKT-MASTER-SPECIFICATION.txt` is untracked here, but the identical file is on GitHub in `marketplace`. |
| `UCOS-CONSOLIDATION` | Governance and constitutional corpus | `ABSOLUTE-FOUNDATION`, 880 commits on the current branch | No commits since the backup below (36 commits and 3 stashes before it) |
| `marketplace` | Marketplace implementation in Python, built from the UCOS-MKT specification | `marketplace`, 10 commits | No commits since the backup below (`f9eb8a0` before it) |
| `UCOS-knowledge` | Copies of the two UCOS topics from `KNOWLEDGE-ASSIMILATION`. Not a git repository. | None | **Everything** |

`universal-product-context-review` was already moved to `../archive/context-review-worktree`.

## How they relate

Measured from file contents and references:

- **Shared vocabulary only.** LUXORA and the UCOS projects use the same UCOS terms and lineage: 114 tracked
  LUXORA files mention UCOS, and LUXORA keeps five `UCOS*` documents at its root.
- **No shared history.** Each repository has a different first commit, so none is a copy or fork of another.
- **No shared file contents with LUXORA.** Zero identical files between the current version of each of the
  three repositories and all of LUXORA's history.
- **No references between repositories.** LUXORA does not name any of these repositories. The two
  `universal-product` hits in `UCOS-CONSOLIDATION` are an unrelated record marked `NOT-UCOS`.
- **One real link.** `UCOS-MKT-MASTER-SPECIFICATION.txt` is byte-identical in `UCOS-UNIVERSAL` and `marketplace`.
- **`KNOWLEDGE-ASSIMILATION` is mixed, so it was kept outside this folder.** It sorts a ChatGPT export into 22
  project streams, some of them personal (immigration, career, personal finance). The owner chose to move it back
  to `~/Desktop/Folders Container/KNOWLEDGE-ASSIMILATION` and keep only the UCOS topics here: `PRJ-000003` (UCOS)
  and `PRJ-000004` (universal composable platform), copied to `UCOS-knowledge/`. `PRJ-000001` (an earlier commerce
  platform) may be related but was not checked or copied.

Merging is not recommended: the histories are unrelated and nothing would be gained. If LUXORA should adopt
something from these projects, that is a separate decision about specific content.

## Commits that were only on this machine (`UCOS-CONSOLIDATION`)

Counted against the live GitHub branches and tags on 2026-11-06, before the backup. Branches overlap; the total is 36 distinct commits.

| Branch | Commits | Last commit |
|---|---|---|
| `integration/consolidation-trunk` (current) | 21 | 2026-09-27 |
| `backup/pre-reattrib-20260926-082356` | 12 | 2026-09-24 |
| `impl/option3-rib-coverage` | 4 | 2026-07-31 |
| `impl/rib-gap-coverage` | 1 | 2026-07-31 |
| `main` | 1 | 2026-09-14 |
| `preserve/omega-nucleus-wip`, `programme/omega-nucleus` | 1 | 2026-08-06 |

Stashes, all made on `integration/recovery-001`:
`ProgB post-cbd7c51 partial: caps+pyproject+generator`, `A+B working tree at boundary`, `a07`.

## Backup on GitHub (2026-11-06)

All of the above, and `marketplace` commit `f9eb8a0`, are now on GitHub in new private branches under
`backup/2026-11-06/`: 10 in `ABSOLUTE-FOUNDATION` and 1 in `marketplace`. No existing GitHub branch changed,
and no local branch or stash changed. Afterwards, 0 commits remained that GitHub could not reach.

Each stash is a branch named `backup/2026-11-06/stash-*`. To read one, run `git show <branch>`.

These are backups, not an update of the original branches. `integration/consolidation-trunk`, `main` and others
on GitHub still point to older commits. The `pre-reattrib` branch suggests history was rewritten at some point,
so check for divergence before replacing any of them.

This backup was made before the second check below, so it does not cover the folders moved in that check.

Still not on GitHub: `KNOWLEDGE-ASSIMILATION` and `UCOS-knowledge`.

## After the move

- Python environments (`UCOS-UNIVERSAL/.venv`, `UCOS-CONSOLIDATION/.ec1-venv`) hold absolute paths and need rebuilding before use.
- `UCOS-CONSOLIDATION` lists a stale worktree at `~/Desktop/UCOS-CONSOLIDATION/.kilo/worktrees/ethereal-court`. That path no longer exists. It was left as it was.
- Open terminals still in an old path keep working until they change directory. Run `cd` to the new path.

## Second check (2026-11-06)

The owner asked to check eight more folders and move the related ones. Six moved, intact, and two did not.

| Folder | Result | Evidence | Only on this machine |
|---|---|---|---|
| `UCOS-COM` | Moved. Related. | UCOS commerce corpus. LUXORA's master architecture names `UCOS-COM Ω∞`. | Nothing in git |
| `UCOS-RI` | Moved. Related. | Reference implementation of `UCOS-COM`, which it vendors and pins. Linked to LUXORA through `UCOS-COM`. | **1 commit and 5 uncommitted changes** |
| `UCOS-architecture` (was `~/UCOS`) | Moved. Related. | UCOS master constitutional architecture, 2026-10-01 baseline. | **Everything**: not in git |
| `Product-Platform` | Moved. Related. | Working UCOS platform and specification. `Architecture1.txt` (74 changed lines of 92,582) and `Architecture2.txt` (1 changed line) are near-copies of LUXORA's. | **Everything**: not in git |
| `offer` | Moved. Related. | GOIP, Global Offer Infrastructure Platform. LUXORA ships a module of the same name and mentions GOIP in 55 files. | **28 uncommitted changes** after the move (33 on the first scan; difference not explained) |
| `UNIVERSAL COMMERCE` | Moved. **Weak link, judgement call.** | A commerce and incentive platform named UCII. LUXORA uses the label UCII in 10 files, but for its registry and catalog, so the same meaning is not proven. No other link. | **Everything**: 11 commits with no GitHub repository, 10 uncommitted changes |
| `solution` | **Not moved.** Unrelated. | An online consultancy platform. No mention of LUXORA, UCOS or GOIP, in either direction. | Not reviewed |
| `UCP-TRUST` | **Not moved.** No link found. | A trust and identity platform. LUXORA does not mention it, and its 32 architecture documents do not mention UCOS. | Not reviewed |

`UNIVERSAL COMMERCE/data/` includes `encryption.key` and `customers.json`. They are not in git. Treat them as sensitive.

Searches for `UCOS-CONSOLIDATION` and others earlier were case-insensitive text matches. This check used exact-text
searches, each with a known-positive control, because `\b` silently matches nothing in `git grep -E` on this Mac.
Full-text search of `Product-Platform` and `UCP-TRUST` timed out, so those results rest on their documents and file
names; for `UCP-TRUST`, on its READMEs and architecture documents only.

## Commit and push (2026-11-07)

The owner asked to organise, commit and push whatever is related. Nothing was forced. Commits went to new `wip/`
branches. Existing branches moved only by a normal fast-forward.

| Repository | Result | State of the work |
|---|---|---|
| `offer` | 3 commits on `wip/2026-11-07-migrations-scheduler` (`b1ad273`) | 494 of 495 tests pass. The TLS test fails with `ERR_OSSL_PEM_NO_START_LINE`, and there is one type error in `test/api.test.ts`. Not fixed. |
| `UCOS-RI` | `main` pushed (`75c9751`). 1 commit on `wip/2026-11-07-s4b-availability` (`902b043`) | The availability work does not compile (`avl/avl.go:1050`). Not fixed. |
| `marketplace` | `master` pushed (`f9eb8a0`) | Not tested in this step. `.DS_Store` excluded locally. |
| `universal-product` (LUXORA) | Release receipt on `wip/release-receipt-2026-11-07` (`34b2821`) | The candidate is still `39ed4d6`. |

Not pushed:

- `UCOS-architecture` and `Product-Platform`: not pushed in this step, because the automated safety check blocked creating new repositories. The owner uploaded both later on 2026-11-07 as new private repositories (`3922add`, `334c7f9` on `main`). A content scan beforehand found no keys, tokens, passwords or emails in what would upload. `.gitignore` keeps out `Product-Platform/platform/var` (database, credentials), `node_modules` and `generated`, so those remain only here and in iCloud.
- `UCOS-CONSOLIDATION`: `integration/consolidation-trunk` and `integration/recovery-001` could fast-forward, but each push would fire about 37 workflows and the commits are already on GitHub. `main` has diverged (1 local, 17 on GitHub). None was pushed.
- `UNIVERSAL COMMERCE`: weak link, and `data/` holds an encryption key and customer records.
- `UCOS-knowledge`: background notes taken from chat history, not project files.

Fixed later the same day, tested locally because GitHub CI was refused for billing:

- `offer` `9ad26f2`: the TLS test now uses a real certificate made by `openssl`, and the type error is gone. Typecheck, 495 of 495 tests, docs, vectors and demo pass.
- `UCOS-RI` `main` `007c503`: `75c9751` had broken the inventory migration (an index expression needed its own parentheses), so conformance could not start. Full `./ucos ci` now passes locally, including 141 of 141 conformance tests for each event-platform implementation.
- `UCOS-RI` `wip/2026-11-07-s4b-availability` `3d451f0`: now compiles and `go vet` is clean. DOM-AVL still has no tests.

The 2026-11-06 backup triggered 279 workflow runs on `ABSOLUTE-FOUNDATION`, of which 135 failed. The `UCOS-RI` push on
2026-11-07 was refused by GitHub for a billing or spending limit, so CI is not running on that account for now.

Correction: the first file comparison for `UCOS-UNIVERSAL` was cut short (251 of 1,912 files). Rerun on complete
listings of all six repositories, the result is the same: no file identical with LUXORA's history.

## Not checked

`freebuff`, `astro`, `satta` and other folders in `Folders Container` were not part of either list.
