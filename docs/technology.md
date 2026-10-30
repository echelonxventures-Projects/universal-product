# Technology governance (PR-053)

LUXORA is not bound to any runtime, language, library, image, database engine, browser, CI
provider or tool, including ones that do not exist yet. Every technology it uses or may use is
governed by one open-ended lifecycle on the kernel. The code holds no list of technologies.

| Part | Where | What it is |
|---|---|---|
| Declaration | `lib/seed/technology.json` | kinds, states and transitions, trust levels, evaluation policy, categories, sources, items, requirements, uses, bootstrap, the baseline and its evidence, detectors, classes, the classified inventory |
| Discovery snapshots | `lib/seed/technology-discovered.json` | what each source returned, with its fetch time and payload digest |
| Core | `lib/technology.js` | registry, ingest, evaluation, governed changes, resolutions, proposals, lock |
| Adapters | `lib/technology-adapters.js` | one discovery adapter per protocol, all behind one contract |
| Repository gate | `lib/technology-scan.js` | detectors, the inventory gate, and the consumers validated against the lock |
| CLI | `scripts/technology.js` | `lock`, `inventory`, `check`, `status`, `proposals`, `discover`, `verify-runtime` |
| Generated | `technology.lock.json`, `TECHNOLOGY_INVENTORY.generated.md` | the resolution, and the inventory for people. Never edited by hand |

## The model

The registry is built on the kernel and adds nothing beside it. A **category**, an **item** (a
technology), a **release** and a **resolution** are kernel nodes of four kinds. Their facts are
versioned in `k_versions`. Every production-affecting move is a kernel change in `k_changes`,
using the same lifecycle as the money policy:

1. drafted
2. validated
3. approved by someone other than its author, holding `kernel.approve`
4. published
5. rolled back

A new category is a node of the existing category kind, not a new kind, table or code path. It
carries:

- a version scheme (`dotted` or `opaque` are registered; another is added with `registerScheme`)
- a metadata contract: the facts its releases must carry, typed and checked by the kernel's own
  value checks, and whether an artifact digest is required

Facts outside the contract are refused unless they are named `x-<name>`.

## The lifecycle

Release states are declared in `states`. Each move is one declared transition.

| State | How a release gets there | What it permits |
|---|---|---|
| discovered | a trusted source reported it | nothing |
| candidate | its identity and provenance check out | nothing |
| under-evaluation | evaluated, and something required is missing (a digest, a capability, a dependency) | nothing |
| compatible | meets every requirement of a use, but lacks that use's evidence | an evaluation lane in CI |
| verified | compatible, with the evidence the use requires | proposing approval |
| approved | a published kernel change | being resolved for a use |
| active | resolved for a use, by a published kernel change | being used |
| deprecated | a published kernel change, with a reason and usually a replacement | resolvable until replaced; proposed for replacement |
| rejected | failed a check that cannot be waived (identity, licence) | nothing |
| prohibited | a published kernel change with a reason | nothing |

Discovery never confers compatibility. Evaluation computes compatibility from:

- the requirements (the capabilities a use needs, with the release each arrived in)
- the engine ranges the locked libraries declare
- the dependencies
- the advisories
- the artifact digests
- the evidence

The report is recorded on the release. Only approval and activation say a release may be used,
and only a person approving someone else's change can grant them.

A resolution binds a use (`deploy.container`, `ci.test`, …) to its releases, with each release's
artifact identity, provenance and evidence. Resolving makes an approved release active in the
same change. There is no `latest`: the lock names exact releases, digests and commits.

## Discovery and its limits

An adapter is a pure function from what a source published to entries. Adapters exist for:

- a release index
- a checksum list
- a container image index
- git tags
- an npm lockfile
- a maintainer's declaration of an observation

A new protocol is a new adapter registered with `register(protocol, { discover, fetch? })`, and
a new source is declared with `registerSource`. Both use the same ingest, checks and lifecycle.

Ingest refuses an entry when:

- its source is undeclared, untrusted, or not allowed for the item
- its version is malformed for its scheme
- a digest is malformed
- a fact is outside the category's contract or of the wrong type
- it carries `__proto__`, `constructor` or `prototype`
- it is larger than the size limit
- it reports a different digest for an artifact already recorded (refused as tampering)

Each refusal is held with its reason in the kernel's hash-chained event log
(`technology.discovery.ingested`; `status` lists them). Fetching is bounded:

- only a source's declared `https` location, never a URL taken from metadata
- no redirects
- a timeout and a size cap
- a version substituted into a location is validated first
- nothing fetched is executed

Discovery writes only to a scratch registry, and to the snapshot file when asked with `--write`.
It never changes a resolution.

## The repository's own toolchain

The baseline in the declaration is the toolchain CI ran at `2ff2b4a`. It is imported as the
registry's first state, as the money policy's first version was seeded. Each baseline release
must still evaluate as verified, with the CI evidence recorded, or the import fails. No
individual approval is claimed for the baseline. Later changes are recorded kernel changes,
replayed in order (`changes`).

`node scripts/technology.js lock` builds the registry on a throwaway database and writes
`technology.lock.json`. The lock is a function of three committed files: the declaration, the
snapshots and `package-lock.json`. It carries no timestamps, so the same inputs give the same
bytes.

**CI consumes the lock.** The `resolve` job is the bootstrap: before any runtime is installed, the
runner image's `jq` reads the lock. From it come:

- the test lanes
- the runtime of the browser and postgres jobs: the runtime the production image carries,
  derived rather than declared
- the PostgreSQL service image, by digest

Each test lane checks that its runtime is the resolved release (`verify-runtime`). Evaluation
lanes are newer eligible releases earning their evidence; they report but do not hold the
commit back. The audit and Docker steps run on the primary lane.

**What cannot read the lock is validated against it**, by `node scripts/technology.js check`:

- `uses:` lines must be the resolved action commits
- `runs-on:` must be the resolved runner
- no literal `node-version:` or service `image:` may appear in the workflow
- the Dockerfile's `FROM` must be the `deploy.container` digest
- `package.json`'s `engines.node` must be the floor derived from the capabilities
  `platform.runtime` needs

The derived floor is `node:sqlite` unflagged since 22.13.0. The boot guard in `server.js` probes
for that module instead of comparing version numbers.

**Every technology assumption in the code is declared.** Detectors (data) find:

- runtime versions, runners, actions and images in workflows
- `FROM` lines
- engine ranges and dependencies
- required modules
- runtime introspection and runtime flags
- URL schemes
- host binaries
- browser binaries

Each finding must be covered by an inventory entry with a class. The gate fails on:

- an undeclared finding
- an entry whose class is a violation (unjustified hardcoding or duplicated configuration: fix
  it, do not declare it)
- an exception without a recorded approval
- a stale entry

Unverified assumptions pass but are reported as gaps.

## Commands

| Command | What it does |
|---|---|
| `npm run technology:check` | the gate; also in `npm test` |
| `npm run technology:lock`, `npm run technology:inventory` | regenerate the two generated files after changing the declaration |
| `npm run technology:status` | declared, discovered, evaluated, compatible, verified, approved, resolved and refused, kept apart |
| `node scripts/technology.js discover node-release-index --fetch` | what the source publishes now, and what that proposes (`--write` keeps it as the new snapshot) |
| `node scripts/technology.js proposals` | evaluation lanes, upgrades, security, replacement, end of life |

## Library integrity

`package-lock.json` is npm's generated resolution. The `npm-lockfile` adapter ingests every
locked package as a library release. Evaluation fails a release that has no integrity hash, or a
licence outside `policy.licences`.

Until 2026-10-30, the 35 packages of jsdom's development tree had neither `resolved` nor
`integrity`. The owner authorized a controlled re-resolution of that subtree only.

The first attempt let npm pick the newest versions the ranges allow. It moved ten development
versions, including undici 8.12.3, which does not load on Node 22.13.1, and CI's 22.13.1 lane
failed. It was replaced by an integrity-only re-resolution:

- npm re-resolved the 35 entries, each held to the version it already had;
- the entries gained exactly `resolved` and `integrity`, every value checked against the
  registry;
- no version, no other entry and no `package.json` changed;
- npm 10 and npm 11 leave the result byte-identical.

The lock's `developmentUnfit` is empty.

What this leaves open:

- The kept undici 8.11.2 carries a high-severity advisory. It is development-only and was already
  present before the fix.
- Its fixed releases need Node ≥ 22.19. The owner chooses between keeping the 22.13.1 full-suite
  lane and taking the tooling's fixes.
- The registry does not yet ingest `npm audit` advisories.
- `prom-client` 15.1.3, a production dependency, is deprecated upstream.

## Not automatic

- **New executable behaviour.** A new protocol needs an adapter. A new kind of consumer file
  needs a validator. A new capability needs code that uses it.
- **Another CI provider.** The consumer validators and the lock's `ci` section are written for
  this repository's workflow and Dockerfile. Another CI provider or build format needs its own
  validator.
- **Approval.** Approval and production resolutions are always a person's decision.
  `autoPropose` drafts the ready upgrades; it never approves or publishes them.
