# 09 — Universal Identity Catalog

**Anchor** `c6c20fb` · **Canonical owners** `00-BOOK/DATA/id-ledger.json` (allocation) and
`00-BOOK/DATA/artifacts.json` (binding)

---

## 1 · The identity model as implemented

The corpus uses a **namespace-prefixed, category-sequenced surrogate identity**, not UUIDs:

```
<NAMESPACE>-<CATEGORY>-<SEQUENCE>     e.g.  UCOS-BOOK-000000
                                            UCOS-CON-000064
                                            UEDGE-000003640
```

| Identity system | Owner | Records | Uniqueness |
|---|---|---|---|
| `universal_id` (artifact identity) | `id-ledger.json` | 1,204 bound · 1,224 paths ledgered | **1,204 / 1,204 unique** |
| `native_id` (source-declared identity) | `artifacts.json` | 379 populated | **NOT unique** — 7 collision groups |
| `edge_id` (`UEDGE-*`) | `relationships.json` | 12,851 | 0 malformed, 0 duplicate |
| Page identity | `id-ledger.json` `page_cursor` | 9,618 | contiguous |
| Volume identity (`VOL-000`…`VOL-024`) | `volumes.json` | 25 declared | 23 populated |
| Category sequence | `id-ledger.json` `category_seq` | 95 sequences | 94 in use |
| Version / lineage identity | `change-ledger.json` | 1,204 version records · 1,204 lineage chains · 1,363 change events | append-only |
| History chains | `id-ledger.json` `history` | 1,224 | append-only, seq-numbered |
| Capability identity (`RC-*`, `SPEC-*`) | `UCOS-RIE-CAPABILITY-CATALOG.json` | 66 | unique |
| Unit identity (dotted key) | `rib.json` `units` | 236 | unique |
| Concept identity | `closure.json` | 437 repo-scope · 528 corpus-scope | unique |
| Finding identity (`UCCEP-F-*`) | `uccep-bindings.json` | 8 | unique |
| Gate / check identity (`G-*`, `CK-*`, `GATE-*`) | `uccep.json`, `rib.json` | 14 + 18 + 12 | unique |

## 2 · Identity integrity — measured

| Invariant | Result |
|---|---|
| Duplicate `universal_id` | **0** |
| Malformed node IDs | **0** |
| Malformed edge IDs | **0** |
| Duplicate node IDs in the typed graph (1,229 nodes) | **0** |
| Unversioned artifacts | **0** |
| Identifier immutability (append-only history) | **holds** — `CK-REG-VALIDATE` PASS (append-only ledger integrity) |
| Identity allocation determinism | **holds** — `CK-SELF-DETERMINISM` PASS |

**The surrogate identity system is sound.** Allocation is deterministic, append-only, collision-free,
and gated.

## 3 · UUID determination — the mandated question

> **For every discovered object determine: UUID (existing or missing).**

| Measure | Value |
|---|---|
| Objects examined | 1,204 |
| Objects carrying a UUID field | **0** |
| `universal_id` values matching RFC-4122 UUID shape | **0 of 1,204** |
| Objects **MISSING** a UUID | **1,204 (100%)** |

**Determination:** No object in this repository carries a UUID. This is a **deliberate design
choice**, not an oversight — the corpus uses human-readable, category-sequenced, page-bound
identifiers so that constitutional prose can cite an identifier directly. That choice is defensible
and internally consistent.

It nonetheless has three consequences that Wave-2 must decide on explicitly rather than inherit:

1. **Sequential IDs are allocation-ordered, so they are not globally mergeable.** Two branches that
   each register a new `UCOS-CON-*` artifact will both take the next sequence number and collide on
   merge. The `id-ledger.json` `category_seq` cursor is a single mutable integer per category — this
   is a merge hazard proportional to parallel development, and Wave-2 introduces exactly that.
2. **Identity is repository-scoped, not universe-scoped.** The architecture declares 28 universes and
   a federated identity constitution (`UCOS-Ω∞-ABSOLUTE-IDENTITY-FEDERATION-AND-CONTINUITY-CONSTITUTION`),
   but the implemented identity space cannot express federation without a globally unique component.
3. **No content-addressed identity path.** `content_hash` exists per artifact but is not an identity —
   and as blocker B-1 shows, it is not currently even a reliable *binding*.

Recommendation is recorded in output 16 (`G-ID-1`), not decided here.

## 4 · Native identity — the real defect

`native_id` is the identifier that constitutional prose, commit messages, and cross-references
actually cite. It is materially weaker than the surrogate:

| Measure | Value |
|---|---|
| Objects with `native_id` populated | **379 (31.5%)** |
| Objects with `native_id` = null | **825 (68.5%)** |
| Collision groups | **7** |
| Objects involved in a collision | **22** |

### Collisions

| `native_id` | Objects | Consequence |
|---|---|---|
| `EC2-CAP-SEC-001` | **7** | a prose citation of `EC2-CAP-SEC-001` is 7-way ambiguous |
| `UCOS-COMP-000000` | **4** | CIOA, Global Implementation Graph, and Implementation State Registry all share it |
| `EC2-EPIC-006` | **3** | blueprint catalog constitution + implementation + catalog |
| `EC2` | 2 | — |
| `UCOS-COMP-000001` | 2 | CCE constitution + implementation |
| `CEP-STAGE-02` | 2 | — |
| `CEP-STAGE-03` | 2 | — |

**Determination:** the corpus has **two identity spaces with different guarantees**, and the one used
in human discourse is the weaker one. 68.5% of objects cannot be cited natively at all, and 22 can
be cited ambiguously.

## 5 · Supporting identity-attribute gaps

| Attribute | State | Consequence |
|---|---|---|
| `version` | **`1.0.0` for all 1,204 objects** | version identity is non-differentiating in the registry; real lineage lives only in `change-ledger.json` (1,363 events), so version cannot be read from an artifact record |
| `description` | **empty for all 1,204** | no object is self-describing at the identity layer; identity resolves to a name and a path only |
| `dependencies` | **empty for 1,014 (84.2%)** | dependency identity is carried by the edge store, not the artifact record — the two are not cross-validated |
| `content_hash` | **10 of 1,204 stale** | identity-to-content binding is broken for the whole derived-intelligence plane (**B-1**) |
| `parent` | 1 null (book root) | correct |
| Volume identity | 62.0% of objects in `VOL-000`; `VOL-013`/`VOL-014` empty | volume identity is largely a default rather than a classification |

## 6 · Identity catalog verdict

| Criterion | Verdict |
|---|---|
| Every object carries a unique canonical identifier | **PASS** — 1,204/1,204 |
| Identifier allocation deterministic and append-only | **PASS** |
| Zero malformed / duplicate node or edge identifiers | **PASS** |
| Identity immutability enforced by gate | **PASS** — `CK-REG-VALIDATE` |
| Every object carries a UUID | **FAIL** — 0 of 1,204 (design choice; consequences unaddressed) |
| Native identifiers complete | **FAIL** — 68.5% null |
| Native identifiers unique | **FAIL** — 7 groups / 22 objects |
| Identity-to-content binding correct | **FAIL** — 10 stale hashes (**B-1**) |
| Version identity differentiating | **FAIL** — all `1.0.0` |
| Identity federated across declared universes | **FAIL** — repository-scoped only |
