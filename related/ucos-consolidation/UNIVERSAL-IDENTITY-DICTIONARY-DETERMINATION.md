# UNIVERSAL IDENTITY DICTIONARY DETERMINATION

> **Mission:** UCOS Ω∞ Universal Infinite Scope, Self-Evolving Constitutional Model Alignment — Workstreams 3 and 4
> **Baseline:** `bb9c27d2` · **Branch:** `integration/recovery-001` · **Date:** 2026-08-18
> **Temporal coordinate:** `logical:ucos-repository-history@1#485` (CMG-000002)
> **Mode:** Determination. No new identity universe, no second identity authority, no third dictionary, no new registry, no counter.
> **Authority:** NONE (DERIVED TRUTH). This determination locates the existing identity and dictionary owners and measures their expansion capacity. It mints nothing.
> **Governing prior determinations:** `UNIVERSAL-IDENTITY-UNIVERSE-DETERMINATION.md` · `UNIVERSAL-IDENTITY-MIGRATION-DETERMINATION.md` — where either and this determination disagree, they govern.

---

## 1. The standing decision is unchanged

`UNIVERSAL-IDENTITY-UNIVERSE-DETERMINATION.md` §6 refuses four things by name: **a new identity universe, a second identity authority, a third dictionary, and a 14-component identity stack**. All four refusals stand.

```
one_authority = "UCKP-ART-05 — Universal Identity. Every other identity mechanism in the
                 repository is a persistence or projection binding of it."
second_authority_test = "A second identity authority would be a second APPEND-ONLY MINT …
                 A mint is recognised by the counter it advances."
mint_markers = ["category_seq"]
```

**The operative rule for any extension: derive, never count.** Nothing in this cycle holds a counter, and the gate this cycle installs holds none either.

Two planes, unchanged:

| Plane | Home | Shape | Role |
|---|---|---|---|
| `CONSTITUTIONAL_OBJECT` | `engine/uckp/identity.py` | `urn:ucos:ucko:<namespace>:<local_name>` | **SUPREME — this IS UCKP-ART-05.** Pure, total, clock-free, storage-free, repository-free |
| `REPOSITORY_OBJECT` | `00-BOOK/DATA/id-ledger.json` | `UCOS-<CATEGORY>-<NNNNNN>` | **PERSISTENCE — the ONE such binding.** Append-only; `first_seen` frozen; never reissued |

---

## 2. Workstream 3 — the identity chain, measured

The mission requires that Universal Identity include nine things. Measured at `bb9c27d2`:

| # | Required | Located owner | Status |
|---|---|---|---|
| 1 | Universal Unique ID | `UCKP-ART-05` (constitutional) + `id-ledger.json` (repository) | **PRESENT** |
| 2 | Universal Unique ID Dictionary | `engine/registry/universal/dictionary.py` — `IdentifierDictionary`, schema `ucos-universal-identifier-dictionary` | **PRESENT, in-memory only** — §4 |
| 3 | Global search | `ukb.py search` over 1,233 artifacts (`--id --volume --status --program --owner --dependency` + substring); `IdentifierDictionary.lookup` / `entries` / `by_kind`; `engine/knowledge/store.py` `by_kind` / `by_authority` / `by_lifecycle` / `by_universe` / `by_owner` | **PRESENT, linear** |
| 4 | Global indexing | `by_path` (1,264) · `by_object` (4,810) · `by_observation` (7) · `by_execution` · `history` (1,264, keyed by identity) · `births` (25, keyed by identity) | **PRESENT — six indexes** |
| 5 | Infinite expansion | `IdentifierDictionary.to_document()` emits `closed_set: false`, `upper_limit: null`; `category_seq` holds 117 open counters; page cursor unbounded | **MEASURED** — §5 |
| 6 | Temporal identity | `engine/temporal/` — `ReferenceSystem`, `TemporalCoordinate`, 8 `TemporalFacet`s incl. `CREATION`; `UOBC-F-04` `creation_timestamp` | **PRESENT** (G1/G2 closed) |
| 7 | Certificate binding | CEP-005 channel; `engine/universal_certification/` | **PRESENT, not keyed on `universal_id`** — gap **G6**, pre-existing |
| 8 | Lineage | `UOBC-F-06` `parent_identity`; `engine/nucleus/lineage.py`; `change-ledger.json` `lineage` | **PRESENT** |
| 9 | Evolution history | `id-ledger.json` `history` (append-only snapshots keyed by identity); `Article-14` `EvolutionLedger` | **PRESENT, partially unpersisted** — gaps F-2/F-3, pre-existing |

**Nine of nine located. Three carry pre-existing gaps (G6, F-2, F-3) already owned and recorded elsewhere. None is created here.**

### Every object at birth receives eight things

`UOBC-000001` makes this structural rather than aspirational. The mission's eight required birth fields map onto nine declared mandatory fields, and `UOBC-L-04` refuses any record with an empty mandatory field:

| Mission requirement | `UOBC` field | Immutable | Enforced |
|---|---|---|---|
| Universal ID | `UOBC-F-01` `universal_id` | yes | derived from `(namespace, local_name)`; re-derived by `UOBC-L-03` |
| namespace | `UOBC-F-02` `namespace` | yes | `^[a-z0-9][a-z0-9._-]{0,62}$`; undeclared namespace refused |
| owner | `UOBC-F-03` `owner` | no — ownership transfers, identity does not | present |
| creation event | `UOBC-F-05` `creation_context` | yes | present |
| temporal coordinate | `UOBC-F-04` `creation_timestamp` | yes | caller-supplied, never a clock read; not an identity input |
| lineage parent | `UOBC-F-06` `parent_identity` | yes | `null` admitted only for a declared root |
| certification boundary | `UOBC-F-09` `certification_boundary` | no | present |
| lifecycle binding | `UOBC-F-07` `lifecycle_binding` | no | present — this is what makes §4 of the root determination structural |

**"No anonymous existence" and "no later identity discovery" are enforced by construction:** `identity_exists` flips exactly once, at `UOBC-S-04` (ordinal 40), and `UOBC-L-01` refuses any stage that instantiates an artifact at an ordinal at or below it. `UOBC-L-06` refuses registration before identity.

**Honest measurement of enforcement reach:** 25 birth records exist — 17 inherited from the prior cycle, 8 created by this one. `UNIVERSAL-IDENTITY-MIGRATION-DETERMINATION.md` measured 1,371 eligible artifacts, 1,233 registered in `artifacts.json`, **138 unregistered-but-not-anonymous** (all hold `by_object` UGA identity as `EXCLUDED_DOCUMENT`, so **0 anonymous**). The birth contract governs objects born under it, and corpus-wide adoption is gap **G11**, whose disposition is already determined: an explicit `register.sh` migration transaction, not a verification-time backfill.

**The determinations created by this cycle are born under the contract**, with birth records at `logical:ucos-repository-history@1#485`. They do not enter the corpus anonymously and then get discovered.

---

## 3. Workstream 4 — the dictionary is not a static table

**Determination: the Universal ID Dictionary is already declared an unbounded knowledge graph, not a table, and this is measurable rather than asserted.**

`IdentifierDictionary.to_document()` emits, in every serialization:

```
closed_set:   false
upper_limit:  null
```

Those two fields *are* the "no predefined maximum size, no category exhaustion" requirement, expressed as data a gate can read. Supporting measurements:

| Property | Measurement | Result |
|---|---|---|
| No predefined maximum size | `to_document()` `upper_limit` | `null` |
| No category exhaustion | `to_document()` `closed_set` | `false` |
| Category space | `id-ledger.json` `category_seq` | **117 counters**, opened by classification, not by an enum |
| Automatic expansion | `ukb.py classify()` is total in three ordered steps, ending in a `_derive_class_from_path()` catch-all | `unclassified == 0` **with no config edit** — a new category opens itself |
| Identity keying | `history` keyed by `universal_id`; `births` keyed by `universal_id` | A move rewrites a path key and cannot touch an identity key |

`IdentifierEntry` carries `universal_id, kind, namespace, natural_key, owner, lineage, attributes` — `lineage` is a tuple and `attributes` is an open mapping, so the entry shape does not need to change to carry a new dimension.

### The eight required search capabilities

| Capability | Located mechanism | Status |
|---|---|---|
| global search | `ukb.py search` (linear over 1,233); `IdentifierDictionary.lookup` (exact, by `kind`+`namespace`+`natural_key`) | **PRESENT** |
| relationship traversal | `UniversalKnowledgeGraph`; `engine/graph/queries.py` BFS / closure / ancestors / topo / cycles; `ukb.py trace` | **PRESENT** |
| lineage search | `IdentifierEntry.lineage`; `parent_identity` edges; `change-ledger.json` `lineage`; descendants by edge inversion | **PRESENT** |
| ownership search | `by_owner` (`engine/knowledge/store.py`); `ukb.py search --owner`; `owner` on every entry | **PRESENT** |
| dependency search | `ukb.py search --dependency`; `dependencies[]` referential integrity in `cmd_validate` | **PRESENT** |
| capability search | `by_kind` / `entries(kind=…)`; `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json` | **PRESENT** |
| semantic search | Lexical: `engine/uckp/registry.py`, `ukip/discovery.py`, `knowledge/intelligence.py`; IDF-cosine: `knowledge/integration/reuse.py` | **PRESENT (lexical/statistical), no vector index** — gap **G8** |
| temporal search | `engine/temporal/` `compare` / `validate_ordering` / `ValidityPeriod` exist; **no temporal index over the identity population** | **PARTIAL** — gap **G8** |

**Six of eight complete; two partial, both under pre-existing gap G8.**

### What is deliberately NOT determined here

**The dictionary is not persisted.** `IdentifierDictionary` has `__slots__ = ("_entries",)` and no `identity-dictionary.json` exists. This is gap **G3**, with **G4** (temporal/lifecycle/evolution/certification state on `IdentifierEntry`) and **G9** (a child index on the identifier plane) stacked on it.

**Determination: G3/G4/G9 are the sanctioned extension points and are NOT exercised by this cycle.**

Reason, stated plainly: persisting the dictionary creates a new file that is either derived truth (and must then be replay-gated, byte-stable and owned by a producer) or governed evolution state (and must then be declared in `mutation-governance-boundary.json` with a named transaction owner). Either path is a capability addition requiring its own determination and its own mutation-class registration. Writing it inside a cycle declared "no new capability, no new registry" would be exactly the undeclared-mutation defect that `GOVERNED-EVOLUTION-STATE-DETERMINATION.md` and the `CORPUS_REGISTRATION` correction exist to prevent.

**Infinite expansion does not depend on persistence.** `closed_set: false` / `upper_limit: null` are properties of the model; they hold whether or not a snapshot is on disk.

---

## 4. Infinite expansion, measured (ISD-L-01 applied to identity)

| Axis | Bound? | Evidence |
|---|---|---|
| Identifier count | **NO** | `category_seq` counters are integers with no declared ceiling; `page_cursor` 9,826 and monotonic |
| Category count | **NO** | 117 open counters; a new category is opened by a total classifier, not admitted by an enum |
| Namespace count | **NO** | `namespace_policy.pattern` admits `[a-z0-9][a-z0-9._-]{0,62}`; the declared list is *"open through declaration, never through invention at a call site"* |
| Dictionary size | **NO** | `upper_limit: null` |
| Kind space | **DISCLOSED-CLOSED** | `RegistryKind` — 29 members with a fail-closed coercer; admission is an enum edit under `UCKP-ART-17` registration |
| Lineage depth | **NO** | `lineage: tuple[str, ...]`; graph traversal is depth-agnostic |
| Evolution history length | **NO** | `history` append-only per identity; `supersessions` an unbounded list |
| Temporal reference systems | **NO** | `ReferenceSystem` is constructed, not enumerated; `SystemType.UNKNOWN` is *"not a failure value"* but the open slot for future time |

**One disclosed closure (`RegistryKind`), seven unbounded axes.** No identity axis is closed without a declared admission path.

---

## 5. Determination summary

| Item | Determination |
|---|---|
| New identity universe / second authority / third dictionary | **REFUSED** — standing refusals of `UNIVERSAL-IDENTITY-UNIVERSE-DETERMINATION.md` §6 reaffirmed |
| Any counter created by this cycle | **NONE** — `mint_markers = ["category_seq"]` remains held by exactly one file |
| Nine-element identity chain | **9/9 LOCATED**; 3 carry pre-existing gaps (G6, F-2, F-3) |
| Eight birth fields | **STRUCTURALLY ENFORCED** by `UOBC-F-01…F-09` + `UOBC-L-01/L-04/L-06` |
| No anonymous existence | **HOLDS** — 0 anonymous artifacts measured; 138 unregistered-but-identified is gap G11, already determined |
| Dictionary as infinite knowledge graph | **MEASURED** — `closed_set: false`, `upper_limit: null`, 117 self-opening categories, total classifier |
| Eight search capabilities | **6 PRESENT, 2 PARTIAL** (semantic index, temporal index) under pre-existing gap G8 |
| Dictionary persistence (G3/G4/G9) | **NOT EXERCISED** — sanctioned extension points, each requiring its own determination and mutation-class registration |
| Identity axes bounded | **NONE**, except `RegistryKind`, which is disclosed with an admission path |

---

**END UNIVERSAL IDENTITY DICTIONARY DETERMINATION**

**Status:** Evolution Baseline Established v1.0
**Certified Temporal Baseline:** `bb9c27d2` · `logical:ucos-repository-history@1#485` (CMG-000002 coordinate; CEP-005 certification channel)
**Identity Authority:** UCKP-ART-05 (`engine/uckp/identity.py`, SUPREME) · `id-ledger.json` (PERSISTENCE, the one repository mint)
**Lifecycle Authority:** UCIC-001 (owner) · UCL-000001 (derived truth, not supreme) · CMG-000001 (law)
**Governed Evolution:** ENABLED — CEP-009 amendment · Article-14 perpetual cycle
