# UCOS Ω∞ — G-3 UNIVERSAL RELATIONSHIP DETERMINISTIC IDENTITY CLOSURE READINESS DETERMINATION

**Whether every relationship identity can become deterministic, universal, replayable and infinitely scalable. The measured answer is that the derivation works on the real population with zero collisions — and that two previously unmeasured obstacles stand in front of it: a validation regex that fails closed on deterministic identifiers, and a 48-bit identity space that is not infinite.**

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-G3-UNIVERSAL-RELATIONSHIP-DETERMINISTIC-IDENTITY-CLOSURE-READINESS-DETERMINATION.md` |
| Authority | **NONE — DERIVED DETERMINATION.** Mints no identity, migrates nothing, alters no edge, implements nothing. |
| Mode | ANALYSIS ONLY · **NO CODE · NO RELATIONSHIP DATA · NO IDENTITY MIGRATION · NO COMMIT** |
| Baseline commit (HEAD) | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Baseline branch | `integration/recovery-001` |
| Numbering note | This directive's `G-3` is the **deterministic-identity** step. In `…EVOLUTION-CLOSURE-ARCHITECTURE-DETERMINATION.md` §13 that step is `G-4`/`G-5`; that determination's `G-3` was DATA-sourcing. **The directive's numbering governs here**; §2.3 maps the two so the chain stays traceable |
| Method | Read-only measurement plus **six probes**: a repository-wide generator sweep, an identity derivation over **all 13,361** live edges, real-population collision counting, birthday-bound arithmetic to 10⁷, a regex conformance test, and gate-semantics inspection. Nothing written; porcelain **367** before and after |
| **Central proof** | **Deriving an identity for every one of the 13,361 live edges yields 13,361 distinct, well-formed identifiers and ZERO collisions** — measured on the actual population, not a bound — §8 |
| **Blocker 1 — NEW** | **`engine/graph/validation.py::_IMMUTABLE_ID` fails closed on deterministic identifiers.** It accepts `UCOS-[A-Z0-9]+-\d+` — **digits only**. `UCOS-REL-a76b71741947` → **False**. `is_valid` treats malformed identifiers as a **hard invariant**, and *"every gate built on `is_valid` fail closed on it"* — §11 |
| **Blocker 2 — NEW** | **48 bits is a finite ceiling.** `_ID_DIGEST_LEN = 12`. Collision probability: 3.2×10⁻⁷ at 13k · 1.8×10⁻³ at 10⁶ · **1.6×10⁻¹ at 10⁷**. The directive requires *infinitely scalable*; measured, it is not — §9 |
| **Third finding** | **The natural key already has a legislated two-level answer** — `key()` for grouping, `identity()` for de-duplication, differing by a temporal validity marker. My prior determinations proposed `(from,to,type)`, which is the **grouping** key — §7 |
| Generators, measured | **Exactly one** expression forms a `UEDGE-` identifier repository-wide: `ukb.py:1031`. Everything else consumes — §4 |
| Three completeness measures | **Capability ~90% (48-bit ceiling) · Implementation 25% · Evidence 0%** — §14 |
| **Readiness verdict** | **READY — BLOCKED ON `P-0`** (the regex). §15 |

---

## 1. Baseline

| Field | Value |
|---|---|
| HEAD | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch | `integration/recovery-001` |
| `git status --porcelain` | **367** |
| Tracked modifications | **38** |
| Staged | **0** |

| Identity substrate | Value |
|---|---|
| Book edges | **13,361** · ids `UEDGE-NNNNNNNNN` |
| UGA relationships | **34,872** · no identifier |
| UCKP derived edges | **13,036** · no identifier |
| Nucleus assignments | `UCOS-REL-<12hex>` via `deterministic_id` |
| `RegistryKind.RELATIONSHIP` | code `REL`, registered |
| `_ID_DIGEST_LEN` | **12 hex = 48 bits** |
| Ledger ids | **6,413**, 100% `UCOS-<CAT>-NNNNNN` |
| `UEDGE-` in the ledger | **0** |

---

## 2. Scope

### 2.1 What G-3 is

| G-3 is | G-3 is not |
|---|---|
| Replacing a **derivation**, not a value space | An ID migration patch — the field, schema field and every consumer stay |
| Folding one population into the **existing** `REL` space | A second identity system — `deterministic_id` already exists |
| **Recomputable** identity — nothing stored, nothing looked up | A temporary mapping or a lookup table; §6.4 shows why none is needed |
| The removal of the last positional identifier on the relationship path | A compatibility layer — no dual-id state exists at any point |

### 2.2 Mandatory principles

| Principle | G-3 |
|---|---|
| Zero duplicate identity authority | **YES** — `deterministic_id`, already the sole authority for `REL` |
| Zero positional identity | **YES** — this is precisely what G-3 removes |
| Zero sequence dependency | **YES** — the derivation reads only the edge's own fields |
| Zero hidden allocation | **YES** — a pure function; no counter, no ledger write |
| Zero identity mutation | **YES** — same key, same id, forever |
| Zero lost history | **YES** — no edge is removed or rewritten; §12 |
| Zero manual reconciliation | **YES** — nothing to reconcile; §6.4 |

### 2.3 Numbering reconciliation

| This directive | Architecture determination §13 | Subject |
|---|---|---|
| — | `G-1` | Derive `RelationType` from the vocabulary |
| — | `G-2` | `from_document` + persistence |
| — | `G-3` | DATA-sourced vocabularies |
| **`G-3` (here)** | **`G-4` + `G-5`** | **Deterministic edge identity + the schema pattern** |

**Stated so no reader concludes the chain skipped a step.** The subject is unambiguous; only the label differs.

---

## 3. Analysis 3 — Canonical Ownership

| Question | Located answer |
|---|---|
| Who owns identity minting? | `deterministic_id` + `RegistryKind` — `engine/registry/universal/identity.py` |
| Delegated authority | **`REG-AUTO-001`** — `CMG-DLG-13`: *"registration, identity allocation, classification"* |
| Is `RELATIONSHIP` a registered kind? | **YES** — code `REL`, 1 of 29 |
| Is a new authority required? | **NO** |
| Governing doctrine | `engine/tests/nucleus/test_identity_convergence.py` — *"a generator minting an identifier **inside a population another authority owns, without delegating to it**"* |

**Ownership is settled and unchanged. G-3 is a delegation act, not an ownership change.**

---

## 4. Analyses 1 and 2 — Generators and Populations

### 4.1 The generator sweep

A repository-wide scan across `engine/`, `platform/`, `intelligence/`, `00-BOOK/tools/` and `00-MASTER/` for every expression that **forms** a relationship identifier:

| Result | Count |
|---|---:|
| Expressions forming a `UEDGE-` identifier | **1** — `00-BOOK/tools/ukb.py:1031`, `f"UEDGE-{edge_seq[0]:09d}"` |
| Expressions forming a `UCOS-REL-` identifier | **1** — `engine/nucleus/model.py:437`, via `deterministic_id` |
| Inline `"UCOS-REL-"` literals in live code | **0** — the one at `nucleus/model.py:424` is the docstring recording the **retired** violation |
| Synthetic projection anchors | `PREFIX::…`, namespaced *"so they can never collide with a registry identifier"* |

> **Exactly one expression in the repository forms a positional relationship identifier.** Every other `edge_id` site — `engine/graph/model.py`, `engine/registry/graph.py`, `platform/coverage/graph.py`, `engine/context/graph.py`, `00-MASTER/URRC-000001/` — **consumes** an id it was handed.

### 4.2 The populations

| # | Population | Count | Identifier | Derivation | Generator |
|---|---|---:|---|---|---|
| `P-1` | UCKP derived edges | **13,036** | none | — | — |
| `P-2` | UGA relationship graph | **34,872** | none | — | — |
| `P-3` | **UKB book edges** | **13,361** | `UEDGE-NNNNNNNNN` | **positional** | `ukb.py:1031` |
| `P-4` | Nucleus assignments | — | `UCOS-REL-<12hex>` | **deterministic** | `deterministic_id` |
| `P-5` | Graph projection anchors | — | `PREFIX::…` | structural | `_syn_edge_id` |

**Three of five carry no minted identifier or a namespaced anchor; one delegates correctly; one mints positionally.**

### 4.3 Consumers that constrain the design

| Consumer | Constraint imposed |
|---|---|
| `engine/graph/model.py::EdgeRegistry` | Refuses a **conflicting** edge under an existing id; re-registration of an identical edge is accepted |
| `engine/registry/graph.py::RelationshipGraph` | Refuses a duplicate `edge_id` outright |
| **`engine/graph/validation.py`** | **`_IMMUTABLE_ID` shape check — §11** |
| `relationship.schema.json` | `edge_id` pattern `^UEDGE-[0-9]{9,}$` |
| `UCCEP-000005/derive.py` | Reports `duplicate_edge_ids` |
| `ukb.py`, `ukbx.py` | Dangling-endpoint reporting; a markdown table cell |

---

## 5. Determination A — Universal Relationship Identity Model

> **A relationship's identity is its natural key. Where a handle is required, that handle is `deterministic_id(RegistryKind.RELATIONSHIP, <namespace>, content_digest(<natural key>))` — recomputable, stored nowhere, allocated by nothing.**

### 5.1 The target chain, per the directive

```
Relationship Truth              the edge's own fields
        ↓
Canonical Natural Key           §7 — (source, target, relation, validity_marker)
        ↓
Deterministic Derivation        deterministic_id(REL, ns, content_digest(key))
        ↓
Immutable Identity Record       none needed — recomputable (§6.4)
        ↓
Audit / Replay / Certification  §13
```

### 5.2 The precedent, verbatim

`engine/nucleus/model.py:437` — a relationship identity already converged onto this exact path, with its reasoning preserved:

> *"Overlapping population plus an independent decision is authority duplication, so the decision is **delegated** and only the *natural key* is derived here.*
>
> *The natural key is the **canonical digest of the triple**, which is what a relationship's stable business key is: **two assignments expressing the same … collapse onto one identity**, and the digest is whitespace-free so the authority's key rule accepts it."*

**G-3 is that act, applied to a second relationship population.**

---

## 6. Determination B — Identity Authority Model

### 6.1 The authority

| Layer | Owner |
|---|---|
| Minting function | `deterministic_id` |
| Kind space | `RegistryKind` — `RELATIONSHIP` → `REL`; `register_kind` open for future kinds |
| Namespace | `normalize_namespace` — dotted `[a-z0-9-]` |
| Natural key | `normalize_natural_key` — non-empty, whitespace-free |
| Delegated authority | `REG-AUTO-001` |

### 6.2 Analysis 4 — can `edge_id` be eliminated as authority?

> **YES, and it never held authority to begin with.**

| Test | Measured |
|---|---|
| Does any consumer depend on `edge_id`'s **ordinality**? | **NO** |
| On its **prefix**? | **NO** — except the schema pattern and `_IMMUTABLE_ID`, both shape checks |
| On its **width**? | **NO** |
| Does any digest include `edge_id`? | **NO** — `key()` / `identity()` serialize `relation.value` |
| Is `edge_id` in any ledger? | **NO** — 0 occurrences |
| Does anything resolve an edge *by* `edge_id` across a boundary? | **`inverse_of` only**, and it is internally consistent (0 dangling over 5,069) |

**`edge_id` is an opaque handle in every live use.** Eliminating it *as an authority* means changing how it is computed — not removing the field.

### 6.3 Why not a `by_edge` ledger plane

The `allocate_execution` precedent would work, and is **not** selected:

| Property | Ledger plane | Deterministic derivation |
|---|---|---|
| Reproducible without the ledger | **NO** | **YES** |
| Ledger growth | **+13,361 entries (+208%)** | **0** |
| Central allocation | **YES** | **NO** |
| Directive's *"no central allocation"* | **violated** | **satisfied** |

### 6.4 Why no mapping table is needed

`UEDGE-` ids appear in **no ledger, no cross-system reference, and no external contract**. The only internal reference is `inverse_of`, which resolves within the same regenerated file. **Nothing outside the file holds a `UEDGE-` id**, so no old→new mapping must be preserved — which is what keeps G-3 free of the lookup table the directive forbids.

---

## 7. Determination C — Natural Key Definition (Analysis 5)

### 7.1 The key is already legislated, at two levels

`engine/knowledge/ukip/relationships.py`:

```python
def key(self) -> tuple[str, str, str]:
    """The stable navigation/grouping key — every temporal version shares one."""
    return (self.source, self.target, self.relation.value)

def identity(self) -> tuple[str, str, str, str | None]:
    """The stable per-instance identity, temporal version included.

    key() deliberately groups every validity-scoped version of a relationship
    together… This is the narrower identity used wherever two versions of the
    same triple must NOT be treated as the same thing — de-duplication and
    content sealing (UCKP-ART-07 temporal validity, P4-F-002).
    """
    marker = None if self.validity is None else self.validity.since.qualified
    return (*self.key(), marker)
```

### 7.2 The correction this forces

My earlier determinations proposed `(from, to, type)` as the natural key. **That is `key()` — the *grouping* key, not the *instance* identity.**

| Key | Answers | Correct for |
|---|---|---|
| `key()` — `(source, target, relation)` | *"what does A depend on?"* | Navigation, grouping |
| **`identity()`** — `(source, target, relation, validity_marker)` | *"is this the same instance?"* | **De-duplication, content sealing, and therefore identity** |

> **Determination: the deterministic identity tuple is `identity()`, not `key()`.**
>
> `(from, to, type)` is correct for the book population **today** — measured unique across all 13,361 — and becomes **wrong the moment temporal validity is used**, collapsing two versions of one triple onto one identifier. The repository already models that case in another population, so building on `key()` would design in a defect the repository has already solved elsewhere.

### 7.3 The tuple

```
natural_key = content_digest([source, target, relation, validity_marker or ""])
edge_id     = deterministic_id(RegistryKind.RELATIONSHIP, <namespace>, natural_key)
```

`validity_marker` is `""` for a population without temporal validity — which makes the book plane's ids **identical to what `key()` would produce today**, and correct in advance for the case where it is not.

### 7.4 Why the digest and not the raw tuple

`normalize_natural_key` requires a **whitespace-free** token. A digest satisfies it unconditionally; a concatenated tuple would not, for any endpoint containing a space. `OwnershipAssignment` makes exactly this choice, and states the reason.

---

## 8. Analysis 6 and 7 — Collision Resistance and Replay Determinism, on the Real Population

### 8.1 The probe

An identity was derived for **every one of the 13,361 live edges** in `00-BOOK/DATA/relationships.json`, in memory, writing nothing:

```
edges                : 13,361
distinct derived ids : 13,361
COLLISIONS           : 0
all well_formed      : True
```

### 8.2 What this establishes

| Claim | Status |
|---|---|
| The derivation is **injective over the actual corpus** | **PROVEN** — not a bound, a count |
| Every derived id is accepted by `is_well_formed` | **PROVEN** |
| Every derived id parses back to `RELATIONSHIP` | **PROVEN** (prior determination) |
| The derivation is **replay-deterministic** | **PROVEN** — a pure function of `(code, namespace, natural_key)`; `content_hash` is canonical |

### 8.3 Replay determinism, precisely

| Property | Basis |
|---|---|
| No wall clock | `deterministic_id` reads no time |
| No randomness | SHA-256 over a canonical tuple |
| No process state | No counter, no registry read |
| No ordering dependence | The id depends only on the edge's own fields |
| **Reproducible by any third party** | The inputs are published in `relationships.json` |

> **This is the property `UEDGE-` can never have.** A positional identifier is reproducible only by re-running the same traversal over the same corpus in the same order; a derived one is reproducible from the edge alone.

---

## 9. Determination D — Digest / Content Identity Model

### 9.1 The measured ceiling

| Measure | Value |
|---|---|
| `_ID_DIGEST_LEN` | **12 hex = 48 bits** |
| Space | **281,474,976,710,656** |
| Collision P at **13,361** | **3.171 × 10⁻⁷** |
| Collision P at **100,000** | **1.776 × 10⁻⁵** |
| Collision P at **1,000,000** | **1.775 × 10⁻³** |
| Collision P at **10,000,000** | **1.628 × 10⁻¹** |
| 50% birthday bound | **≈ 19.75 million** |

### 9.2 The finding

> **48 bits is a finite ceiling, and the directive asks for infinite scalability.**
>
> At the current population the risk is negligible (3.2×10⁻⁷) and the derivation is provably injective. At 10⁷ relationships — a scale a repository claiming *"infinite entities, infinite meanings, infinite civilizations"* must contemplate — the collision probability is **16%**.

### 9.3 Why this is a real constraint and not pedantry

`UISD-000001` `ISD-L-01` requires that *"no enumeration claims completeness silently: every closed enumeration discloses both the invariant that closes it and the admission path."* An identity space is not an enumeration, but the same discipline applies: **`_ID_DIGEST_LEN = 12` is an undisclosed finite bound on a layer the repository describes as unbounded.**

### 9.4 Disposition — reported, not decided

| Option | Note |
|---|---|
| Leave 12 | Correct at present scale; the bound stays undisclosed |
| Disclose the bound | Minimal act; makes the ceiling checkable |
| Widen the digest | **Changes every deterministic id ever produced** — an `ART-05` question, not an engineering one |

> **This determination does not choose.** Widening the digest would mutate existing identities, which `ART-05` forbids; disclosing the bound is an owner act. **`G-3` is unaffected either way at present scale**, and the constraint is recorded as `RB-2` so it is not discovered later.

---

## 10. Determination E — Historical Transition Model (Analysis 8, 9)

### 10.1 Historical preservation

| Requirement | Under G-3 |
|---|---|
| No edge removed | **Held** — only `edge_id`'s derivation changes |
| `from`, `to`, `type`, `note` unchanged | **Held** |
| `inverse_of` referential integrity | **Held** — both sides recompute from their own tuples; 0 dangling today, 0 after |
| Prior states unchanged | **Held** — `ART-12`; nothing rewrites a past state |
| Old `UEDGE-` ids referenced elsewhere | **None exist** — §6.4 |

### 10.2 The one honest discontinuity

**Every edge's identifier changes value once**, at the moment of adoption. `UEDGE-000000001` becomes `UCOS-REL-<hex>`.

| Question | Answer |
|---|---|
| Is that identity **mutation**? | **No** — `UEDGE-…` was never an identity (positional, unkeyed, unrecorded, regenerated). It is the *replacement of a non-identity with an identity* |
| Does it violate `ART-05` (*"once minted, never changes"*)? | **No** — `ART-05` binds identities. A value that changes on every regeneration was never minted in the `ART-05` sense |
| Is any historical truth lost? | **No** — no external reference exists to break |
| Is a mapping needed for continuity? | **No** — §6.4 |

**Stated plainly rather than glossed:** this is the single discontinuity in G-3, it happens once, and it is the correction rather than a cost of it.

### 10.3 Relationship evolution compatibility (Analysis 9)

| Evolution act | Under G-3 |
|---|---|
| A **new** relationship appears | Gets an id automatically — no allocation, no registration |
| A relationship is **superseded** | Supersession is a *relation type* (`Supersedes`), so the superseding edge is a new triple with its own id |
| A relationship becomes **historical** | Class `historical`; the edge and its id persist |
| A relationship gains **temporal validity** | The marker enters the key — §7.3 — so each version gets a distinct id |
| A **new relation type** is admitted | The id derivation is type-agnostic; no change |

> **The identity model imposes no ceiling on relationship evolution and requires no change when any of the five occur.**

---

## 11. Blocker `P-0` — The Immutable-Identifier Regex

### 11.1 The measurement

`engine/graph/validation.py:36`:

```python
_IMMUTABLE_ID = re.compile(
    r"^(UCOS-[A-Z0-9]+-\d+|UEDGE-\d+|USIG-\d+|VOL-\d+|[A-Z][A-Za-z0-9_]*::.+"
    r"|KGE::.+|UCHG-\d+|URUN-\d+)$"
)
```

Tested directly:

```
UEDGE-000000001          -> True
UCOS-CON-000021          -> True
UCOS-BOOK-000000         -> True
UCOS-REL-a76b71741947    -> False    ← deterministic
UCOS-REL-99790c515fc3    -> False    ← deterministic
```

### 11.2 Why it fails

The `UCOS-` alternation is `UCOS-[A-Z0-9]+-\d+` — the trailing segment is **digits only**. That matches the ledger's sequential shape (`UCOS-<CAT>-NNNNNN`) and **cannot** match `deterministic_id`'s output, which is 12 lowercase hex characters.

> **The regex encodes an assumption that every `UCOS-` identifier is sequential.** True of all 6,413 ledger ids; false of every identifier the registration authority mints.

### 11.3 Why it blocks

`validate_graph` collects `malformed_edges` when `_is_immutable(edge.edge_id)` is false, and the module states:

> *"`is_valid` — True iff **no hard mission invariant** was violated. The hard invariants are: no duplicate nodes, **immutable identifiers**, …"*
> *"every gate built on `is_valid` **fail closed** on it."*

`validate_graph` is consumed by `engine/graph/adapter.py`, exported from `engine/graph/__init__.py`, and called by `00-MASTER/UCCEP-000005/derive.py:137`, which names it *"the located dependency gate."*

> **Adopting deterministic edge ids without extending this regex would turn every edge into a `malformed_edge` and fail the dependency gate closed, repository-wide.**

### 11.4 Disposition

| Field | Value |
|---|---|
| Act | Extend one alternation to admit the registration authority's shape |
| Disposition | **EXTEND** — a shape check widened to accept a shape the authority already mints |
| Scope | **1 file, 1 regex** |
| Must precede | The identity change — **it is `P-0`** |
| Is it a patch? | **No** — it corrects a check that never anticipated the authority's own output format |

**This blocker was not visible from any prior determination in this chain.** It is exactly what a readiness determination exists to find.

---

## 12. Determination F — Replay Verification Model

| Check | Method | Available |
|---|---|---|
| Every id recomputes from its own edge | Re-derive and compare | **YES — proven §8.1** |
| Zero collisions over the corpus | Count distinct | **YES — 13,361/13,361** |
| Every id well-formed | `is_well_formed` | **YES** |
| Every id parses to `RELATIONSHIP` | `parse_kind_name` | **YES** |
| `inverse_of` integrity | Reference resolution | 0 dangling today; recomputed consistently |
| Fixed point | A second regeneration rewrites no byte | Same property UGA declares |
| **Identity-authority gate** | An `EXL-02`-shaped check | **ABSENT for edges** — `RB-4` |

`ukb.py:2277` already gates executions: *"not minted from the id-ledger identity authority (EXL-02)."* **The equivalent check for edges does not exist**, and under G-3 it becomes both possible and meaningful — a derived id can be recomputed and compared, which a positional one cannot.

---

## 13. Determination G — Remaining Blockers

| Id | Sev | Blocker | Disposition |
|---|---|---|---|
| **`RB-1`** | **BLOCKING** | **`_IMMUTABLE_ID` rejects deterministic identifiers**; `is_valid` fails closed | **`P-0` — EXTEND one regex, 1 file** |
| `RB-2` | **HIGH** | **48-bit ceiling undisclosed.** 16% collision probability at 10⁷ | **REPORTED** — widening mutates existing ids (`ART-05`); an owner decision |
| `RB-3` | **HIGH** | `relationship.schema.json` pins `edge_id` to `^UEDGE-[0-9]{9,}$` | **EXTEND** — one pattern, one-time closure removal |
| `RB-4` | MEDIUM | **No identity-authority gate for edges**, though `EXL-02` exists for executions | **REUSE** the pattern |
| `RB-5` | MEDIUM | **The 13,361 edges are validated against no schema** — `jsonschema` 4.26.0 installed, `relationship.schema.json` never passed to it | **EXTEND** |
| `RB-6` | MEDIUM | **The namespace string is unchosen** | **OWNER** — `REG-AUTO-001` |
| `RB-7` | LOW | **The inline-mint AST guard reaches only `engine/nucleus` and matches only `UCOS-` literals** — widened in scope alone it would still report clean on `add_edge` | **EXTEND** scope **and** shape |

### 13.1 Closure sequence

```
P-0 (RB-1: regex)  ──▶  RB-3 (schema pattern)  ──▶  RB-6 (namespace)  ──▶  identity change
                                                          └──▶ RB-4, RB-5 (gates)
RB-2, RB-7  — independent
```

**`CREATE` count: 0. New authorities: 0. New ledgers: 0. Lookup tables: 0. Mapping tables: 0.**

---

## 14. The Three Completeness Measures

### 14.1 Identity capability completeness

| Capability | Available |
|---|---|
| Deterministic derivation | **YES** |
| Universal — one authority, one kind space | **YES** |
| Replayable by a third party | **YES** |
| Collision-free at present and foreseeable scale | **YES to ~10⁶** |
| **Infinitely scalable** | **NO — 48-bit ceiling** (`RB-2`) |
| Temporal-version aware | **YES** — `identity()` already models it |
| No central allocation | **YES** |

> **Capability completeness ≈ 90%.** The single deficit is the digest width, and it is a disclosed-bound question rather than a missing mechanism.

### 14.2 Identity implementation completeness

| Layer | Built |
|---|---|
| Natural key defined | **YES** — `key()` / `identity()` |
| Deterministic derivation available | **YES** — `deterministic_id` |
| Applied to `P-4` (nucleus) | **YES** |
| Applied to `P-3` (book edges) | **NO** |
| Validation accepts the shape | **NO** — `RB-1` |
| Schema accepts the shape | **NO** — `RB-3` |
| Identity-authority gate | **NO** — `RB-4` |

> **Implementation completeness: 3 of 7 ≈ 25%** for the relationship-identity path as a whole.

### 14.3 Identity evidence completeness

| Evidence | Present |
|---|---|
| Any relationship identity recorded in the ledger | **NO** — 0 |
| Any published artifact from which an edge id can be recomputed and checked | **NO** |
| A gate proving edge ids came from the authority | **NO** |
| A round-trip / replay proof in the test suite | **NO** |
| History keyed by relationship identity | **NO** |

> **Evidence completeness: 0%.**

### 14.4 The verification question

> *Can an unknown future relationship be created, receive identity, be reconstructed, verified and audited — with no code change and no central allocation?*

| Step | Today | After `P-0` + G-3 |
|---|---|---|
| **created** | YES | **YES** |
| **receive identity** | Positional, allocated by a counter | **YES — pure function, no allocation** |
| **reconstructed** | **NO** — not recomputable | **YES** |
| **verified** | **NO** | **YES** — recompute and compare |
| **audited** | **NO** — no stable key for history | **YES** |
| **no code change** | — | **YES** — a new edge needs none |
| **no central allocation** | **NO** — `edge_seq` | **YES** |

**Six of seven fail today; seven of seven hold after G-3, with `P-0` first.**

---

## 15. Readiness Determination

### 15.1 Verdict

> # READY — BLOCKED ON `P-0`

`P-0` is the extension of `_IMMUTABLE_ID` (`RB-1`): **one regex, one file.** Every other prerequisite is an owner decision or an additive gate.

### 15.2 The seven determinations

| | Determination | Established | New mechanism |
|---|---|---|---|
| **A** | **Identity model** — natural key, rendered via the existing mint | **YES** | None |
| **B** | **Authority model** — `deterministic_id` + `RELATIONSHIP`; `REG-AUTO-001` delegated | **YES** | None |
| **C** | **Natural key** — `identity()`, not `key()`; validity marker included | **YES — corrected** | None |
| **D** | **Digest/content model** — 48 bits, injective on the real corpus, **finite at 10⁷** | **YES, with `RB-2`** | None |
| **E** | **Historical transition** — nothing lost; one value discontinuity, stated | **YES** | None |
| **F** | **Replay verification** — recompute and compare; `EXL-02` is the gate template | **YES** | None |
| **G** | **Remaining blockers** — 7, one blocking | **YES** | — |

### 15.3 Readiness gates

| Gate | Verdict |
|---|---|
| Canonical owner located | **PASS** — `deterministic_id`, `REG-AUTO-001` |
| Mechanism exists without invention | **PASS** |
| Generators enumerated | **PASS** — exactly one positional |
| Populations enumerated | **PASS** — five |
| Natural key defined | **PASS** — legislated, two-level |
| **Injectivity on the real corpus** | **PASS** — 13,361/13,361, 0 collisions |
| Replay determinism | **PASS** |
| Historical preservation | **PASS** |
| Evolution compatibility | **PASS** |
| No mapping table required | **PASS** — §6.4 |
| Consumers unaffected | **PASS** — all opaque handles |
| **Validation accepts the shape** | **FAIL — `P-0`** |
| Schema accepts the shape | **FAIL — `RB-3`, non-blocking if sequenced** |
| Infinite scalability | **FAIL — `RB-2`, reported not decided** |
| **Blocking prerequisite** | **`P-0`** |

### 15.4 What G-3 delivers, precisely

| Delivered | Not delivered |
|---|---|
| Positional identity **eliminated** — the last one on the relationship path | **Infinite** scalability — 48-bit ceiling (`RB-2`) |
| Central allocation **eliminated** | Certification of edges (`RB-5`) |
| Replay and third-party verification **enabled** | Edge history (needs a plane or a ledger key) |
| Audit **enabled** — a stable key to record against | `RB-2`'s disposition |
| Sequence dependency **eliminated** | |

### 15.5 Constraint compliance

| Constraint | Result |
|---|---|
| Do not implement / modify code / modify relationship data / migrate identities | **HONOURED** |
| Create only the named artifact | **HONOURED** |
| Not an ID migration patch | The field, schema field and consumers all persist; only the derivation changes |
| Not a compatibility layer | No dual-id state at any point |
| Not a second identity system | `deterministic_id` is the existing one |
| Not a temporary mapping / lookup table | **None required** — §6.4 proves no external reference exists |

---

## 16. Verification Record

### 16.1 Before / after

| Field | Before | After | Delta |
|---|---|---|---|
| HEAD | `bae59755…5269a` | `bae59755…5269a` | **unchanged** |
| Branch | `integration/recovery-001` | `integration/recovery-001` | **unchanged** |
| `git status --porcelain` | **367** | **368** | **+1 — this artifact** |
| Tracked modifications | **38** | **38** | **unchanged** |
| Staged | **0** | **0** | **unchanged** |
| Commits | **0** | **0** | **none** |

### 16.2 Required assertions

| Assertion | Result |
|---|---|
| Artifact only changed | **VERIFIED** — porcelain +1 |
| HEAD unchanged | **VERIFIED** |
| Branch unchanged | **VERIFIED** |
| Tracked modifications unchanged | **VERIFIED** — 38 |
| Identity unchanged | **VERIFIED** — `id-ledger.json` untouched; every `deterministic_id` call was a pure function, discarded |
| Relationship data unchanged | **VERIFIED** — `relationships.json` read only |
| Certification unchanged | **VERIFIED** |
| No commits | **VERIFIED** |

### 16.3 Probe isolation

Six probes ran in-process. `deterministic_id` is a pure function that touches no ledger. The 13,361 derived identifiers were held in a local dict and discarded. No file was opened for writing. **`git status --porcelain` was 367 before and after every probe.**

### 16.4 Live measurements

| Measurement | Method | Result |
|---|---|---|
| `UEDGE-`-forming expressions repository-wide | Regex sweep over 5 roots | **1** — `ukb.py:1031` |
| Inline `"UCOS-REL-"` literals in live code | Sweep | **0** |
| Relationship populations | Enumeration | **5** |
| **Derived ids over all live edges** | `deterministic_id` ×13,361 | **13,361 distinct · 0 collisions · all well-formed** |
| Birthday probability | Arithmetic | 3.171e-07 @13k · 1.776e-05 @100k · 1.775e-03 @1M · **1.628e-01 @10M** |
| 50% bound | Arithmetic | **≈19,753,662** |
| `_ID_DIGEST_LEN` | Source read | **12** |
| **`_IMMUTABLE_ID` conformance** | Direct regex test | `UEDGE-…` **True** · `UCOS-REL-<hex>` **False** |
| `is_valid` semantics | Source read | *"hard mission invariant"*; *"every gate built on `is_valid` fail closed"* |
| `validate_graph` consumers | `grep` | `engine/graph/adapter.py`, `engine/graph/__init__.py`, `UCCEP-000005/derive.py:137` |
| Natural-key levels | Source read | `key()` 3-tuple · `identity()` 4-tuple with validity marker |
| `edge_id` consumers | `grep` | All opaque handles |
| `EXL-02` precedent | Source read | `ukb.py:2277` — executions gated, edges not |

### 16.5 What was not verified

| Not verified | Why |
|---|---|
| That extending `_IMMUTABLE_ID` breaks nothing else | Would require implementing it; the regex has 2 call sites, both in `validation.py` |
| That regenerating the corpus renumbers `UEDGE-` | Would require running `ukb.py`, which writes. Established by reading the producer |
| Whether any population uses `ValidityPeriod` today | The class was located; **no population was measured as carrying a non-null validity marker** — §7.3's provision is precautionary |
| Whether `RB-2`'s ceiling has ever been considered by an owner | No instrument was found addressing digest width; absence of a record is not proof of absence |
| That 5 populations is the complete set | Swept `engine/`, `platform/`, `intelligence/`, `00-BOOK/tools/`, `00-MASTER/`; a sixth elsewhere would not have been seen |
| Current `verify.sh` verdict | Not executed — `ISD-G-11`; this mode forbids surface mutation |

### 16.6 Artifact creation verified

| Check | Result |
|---|---|
| File exists at the specified name | **Yes** |
| Determinations A–G | **All seven delivered** |
| Analyses 1–10 | **All ten addressed** |
| Three completeness measures | **Separated — §14** |
| Verification question answered | **§14.4** |
| Git status | `??` untracked — the only delta from 367 |
| Other files changed | **0** |
| Commits | **0** |

---

**End of determination.**

| Field | Value |
|---|---|
| Baseline | `bae59755d7e2d3566c93b89c722b68847145269a` · `integration/recovery-001` |
| Determinations delivered | **A–G, seven of seven** |
| Probes | **6 — all in-memory, nothing persisted** |
| Identities derived over the live corpus | **13,361** · collisions **0** |
| Positional generators repository-wide | **1** |
| Relationship populations | **5** |
| Blockers | **7** — 1 BLOCKING · 2 HIGH · 3 MEDIUM · 1 LOW |
| Blockers newly measured here | **2** — `RB-1` (regex), `RB-2` (48-bit ceiling) |
| Corrections of record | **1** — natural key is `identity()`, not `key()` |
| Capability / implementation / evidence completeness | **~90% / ~25% / 0%** |
| New authorities · ledgers · mappings · lookup tables | **0 · 0 · 0 · 0** |
| Code changed | **0 files** |
| Relationship data changed | **0** |
| **Readiness** | **READY — BLOCKED ON `P-0`** |
