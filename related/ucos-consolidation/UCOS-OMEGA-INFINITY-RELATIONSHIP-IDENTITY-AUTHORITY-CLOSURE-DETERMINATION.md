# UCOS Ω∞ — RELATIONSHIP IDENTITY AUTHORITY CLOSURE DETERMINATION

**Whether relationship identity has one authority and whether every relationship identity obeys universal identity law. The measured answer is that the authority exists, the doctrine for coexisting identifier populations is already written and tested, the exact defect has already been remediated once for a relationship identity — and one population of 13,361 edges still fails identity law for a single, precisely locatable reason.**

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-RELATIONSHIP-IDENTITY-AUTHORITY-CLOSURE-DETERMINATION.md` |
| Authority | **NONE — DERIVED DETERMINATION.** Mints no identity, registers no kind, writes no ledger entry, alters no edge, implements nothing. It measures the identity populations that exist and the law they are held to. |
| Mode | ANALYSIS ONLY · **NO CODE · NO REGISTRY · NO RELATIONSHIP DATA · NO IDENTITY · NO OWNERSHIP · NO CERTIFICATION · NO COMMIT** |
| Baseline commit (HEAD) | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Baseline branch | `integration/recovery-001` |
| Subject | Relationship identity authority; `C1-F-1`; `C1-F-2` identity dimension |
| Method | Read-only measurement plus pure-function evaluation: classification of all **6,413** ledger ids, all **13,361** book edges and all **34,872** UGA edges; `is_well_formed` / `parse_kind_name` probes; one `deterministic_id` computation over an existing triple; birthday-bound arithmetic. Nothing written |
| **Central finding** | **The repository already has a written, implemented and tested doctrine of identity convergence, and it says several identifier formats legitimately coexist.** The violation it defines is narrow: *"a generator minting an identifier **inside a population another authority owns, without delegating to it**."* Under that doctrine, `UEDGE-` is a **lawful distinct population**, exactly as `UCOS-EVO-` is — §5.2 |
| **Second finding** | **The defect is therefore not authority. It is determinism.** `UCOS-EVO-` is lawful as a separate population **because it is content-derived**. `UEDGE-` is positional. It fails `ART-05` and `ART-13` on its own terms, independently of any authority question — §4, §8 |
| **Third finding** | **This exact defect — an inline-minted RELATIONSHIP identity — has already been diagnosed and retired once**, in `engine/nucleus`, and a live AST guard prevents its return. The remediation shape, including the natural-key doctrine, is written down — §5.3 |
| **Fourth finding** | **Three of four relationship populations carry no identity at all, and that is correct.** UCKP's 13,036 derived edges and UGA's 34,872 projected edges are identified by their triple. **Only UKB mints an identifier for a derived edge** — §3 |
| **Proof of feasibility** | **`(from, to, type)` is unique across all 13,361 edges** — measured. A deterministic id over the triple is collision-free by construction; **no consumer depends on ordinality** — §8.4 |
| Options evaluated | **A · B · C · D · E** — §6 |
| **Selected** | **B + D jointly — a derived identifier computed through the existing universal mint.** A, C, E rejected or absorbed — §6.6 |
| Corrections of record | **3** — §14.5 |
| **Verdict** | **CONDITIONALLY RESOLVED** — §14 |

---

## 1. Current Baseline

### 1.1 Captured before writing

| Field | Value |
|---|---|
| HEAD | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch | `integration/recovery-001` |
| `git status --porcelain` | **362** |
| Tracked modifications | **38** |
| Staged | **0** |
| Untracked | **324** |

### 1.2 Identity substrate

| Surface | Value |
|---|---|
| `00-BOOK/DATA/id-ledger.json` | **6,413** ids · planes `by_path` 1,492 · `by_object` 4,914 · `by_observation` 7 |
| Ledger `history` plane | **1,492** entries, keyed by `universal_id` |
| `RegistryKind` | **29** members · `RELATIONSHIP` → `REL` |
| Registered extension kinds | **0** — `_EXTENSION_KIND_CODES` empty at import |
| `deterministic_id` digest | **12 hex = 48 bits** |
| `00-BOOK/DATA/relationships.json` | **13,361** edges · 16 types · 5,069 with `inverse_of` |
| `00-MASTER/UCOS-UGA-001/04-RELATIONSHIP-GRAPH.json` | **34,872** relationships · 6 kinds |
| `build_universe()` derived edges | **13,036** |

---

## 2. Previous Determination Findings

### 2.1 What this chain established

| Determination | Established |
|---|---|
| `C-1` | Inter-vocabulary mappings live on the object plane; a term projected as a UCKO carries the mapping as a `Relationship` facet. Verdict `CONDITIONALLY RESOLVED` |
| `C-1` `C1-F-1` | *"The edge register advances its own counter… `CAA-INV-04` recognises a second identity authority by the counter it advances"* |
| `D-a`/`D-b` | Semantic authority for the object plane is `UCRD-001` Tier 3, sole and already legislated. Verdict `CONDITIONALLY RESOLVED` |
| `D-a`/`D-b` §4.3 | **First correction:** sequential allocation *is* the ledger's own method (`category_seq`); the defect is positional instability, missing keying, and no ledger plane |
| `D-a`/`D-b` §14.2 Q2 | *"Is there exactly one identity authority for relationships? **NO.**"* |

### 2.2 What this determination inherits

`E-c` from `D-a`/`D-b` §11.6: *"Derive `edge_id` or add a keyed `by_edge` plane — owner `REG-AUTO-001` — **identity authority** decision."*

### 2.3 A doctrine neither prior determination had read

`engine/tests/nucleus/test_identity_convergence.py` — **a module-level docstring that states the repository's identity-convergence doctrine in full, and eight tests that enforce it.** Neither `C-1` nor `D-a`/`D-b` cited it. It changes the diagnosis of `C1-F-1` materially (§5.2, §14.5) and supplies the remediation shape (§5.3).

---

## 3. Relationship Identity Inventory

### 3.1 The four relationship populations

| # | Population | Count | Identifier | Derivation | In ledger | Standing |
|---|---|---:|---|---|---|---|
| `R-1` | UCKP derived edges — `UniversalKnowledgeEdge` | **13,036** | **none** | — | n/a | Layer Zero; *"derived, never authored"* |
| `R-2` | UGA relationship graph | **34,872** | **none** — `{from, kind, to}` | — | n/a | `standing: "PROJECTION"` |
| `R-3` | UKB book edges | **13,361** | **`UEDGE-NNNNNNNNN`** | **positional** | **NO** | — |
| `R-4` | Nucleus ownership assignments | — | `UCOS-REL-<12hex>` | **deterministic** | NO (recomputable) | delegated to the authority |

**Three of four carry no identity, and that is correct.** `R-1` is derived from objects, so the object bears the identity; `R-2` declares itself a projection measuring a population. An edge in both is identified by its triple.

**`R-3` is the sole population that mints an identifier for a derived edge.**

### 3.2 `id-ledger` relationship entries

| Query | Result |
|---|---|
| Ledger planes | `by_path`, `by_object`, `by_observation`, `history`, `page_cursor`, `category_seq`, `volume_seq`, `discovered_volumes` |
| An edge / relationship plane | **NONE** |
| `UEDGE-` ids in the ledger | **0** |
| `UCOS-REL-` ids in the ledger | **0** |
| `UCOS-REL-` anywhere in `00-BOOK/DATA/*.json` | **0** |
| Ledger ids matching `UCOS-<CAT>-NNNNNN` | **6,413 (100%)** |
| Ledger ids matching `UCOS-<CODE>-<12hex>` | **0 (0%)** |

### 3.3 The two identifier grammars

| Grammar | Shape | Producer | `is_well_formed`? |
|---|---|---|---|
| Ledger allocation | `UCOS-<CAT>-NNNNNN` | `ukb.py::allocate`, keyed by `relpath` | **False** |
| Registration authority | `UCOS-<CODE>-<12hex>` | `deterministic_id` | **True** |

Probed directly:

```
UEDGE-000000001         well_formed=False   kind=<RegistrationValidationError>
UCOS-EVO-088bd1337123   well_formed=False   kind=<RegistrationValidationError>
UCOS-REL-99790c515fc3   well_formed=True    kind=RELATIONSHIP
UCOS-BOOK-000000        well_formed=False   kind=<RegistrationValidationError>
```

**`UCOS-BOOK-000000` — a real ledger id — is not well-formed under the registration authority's grammar.** Two grammars coexist, and neither validates the other's ids. §5.2 shows this is anticipated by the doctrine, not a defect.

### 3.4 `edge_id` generation

`00-BOOK/tools/ukb.py:1020-1033`:

```python
edge_seq = [0]
_seen_edges = set()

def add_edge(src, dst, etype, note="", inverse_of=None):
    if not src or not dst or src == dst:
        return None
    key = (src, dst, etype)
    if key in _seen_edges:
        return None
    _seen_edges.add(key)
    edge_seq[0] += 1
    eid = f"UEDGE-{edge_seq[0]:09d}"
```

| Property | Measured |
|---|---|
| Counter scope | **Build-local** — `edge_seq = [0]` inside the build function, not `ledger["category_seq"]` |
| Keyed by | **Nothing.** The dedup key `(src, dst, etype)` is computed and **discarded** for id purposes |
| Ordering | Traversal order over `C.CHAINS`; **no `edges.sort` or `sorted(edges)` exists in `ukb.py`** |
| Recorded | **Nowhere** |
| Recomputable | **No** |

### 3.5 Deterministic mechanisms present

| Mechanism | Formula | Content-derived |
|---|---|---|
| `deterministic_id` | `UCOS-<CODE>-` + `sha256(code, ns, key)[:12]` | **Yes** |
| `OwnershipAssignment.assignment_id` | `deterministic_id(RELATIONSHIP, "ucos.ownership", digest([cap, owner, authority, supersedes]))` | **Yes** |
| `Evolution.evolution_id` | `"UCOS-EVO-" + content_hash([subject_id, generation, change, authority])[:12]` | **Yes** |
| `ReferenceFrame.universal_id` | `deterministic_id(LOCATION, "ucos.context.frame", key)` | **Yes** |
| `urn_for` / `uuid_for` | URN concatenation; UUID5 over the URN | **Yes** |

### 3.6 Sequential mechanisms present

| Mechanism | Counter | Keyed | Recorded |
|---|---|---|---|
| `ukb.py::allocate` | `ledger["category_seq"]` | **`relpath`** | **Yes** |
| `ukb.py::allocate_execution` | `ledger["category_seq"]` | **`exec_key`** | **Yes** |
| Page allocation | `ledger["page_cursor"]` | path-derived | **Yes** |
| **`ukb.py::add_edge`** | **build-local `edge_seq`** | **none** | **No** |

**Every sequential mechanism in the repository is keyed and recorded — except `add_edge`.**

### 3.7 Identity history storage

`id-ledger.json` `history` — **1,492 entries**, keyed by `universal_id`, each a list of records:

```json
{"seq": 1, "at": "…", "content_hash": "…", "version": "1.0.0",
 "status": "ACTIVE", "path": "…", "name": "…"}
```

**History is keyed by identity.** An edge with no ledger identity has no history, so `R-3` has no supersession record and no audit trail of its own.

---

## 4. Identity Law Compliance

### 4.1 The eight required properties

| # | Property | `R-1` derived | `R-2` UGA | `R-3` UKB | `R-4` nucleus |
|---|---|:-:|:-:|:-:|:-:|
| 1 | **Immutable identity** | n/a — no id | n/a — no id | **FAIL** | **PASS** |
| 2 | **Minted once** | n/a | n/a | **FAIL** — re-minted each build | **PASS** — pure function |
| 3 | **Authority namespaced** | n/a | n/a | **FAIL** — no namespace | **PASS** — `ucos.ownership` |
| 4 | **Deterministic reproducibility** | **PASS** — `derive_edges` total & deterministic | **PASS** — declared *"No wall clock"* | **FAIL** | **PASS** |
| 5 | **Historical preservation** | **PASS** — `ART-12` on the object | **PASS** — epoch-stamped | **FAIL** — no history plane | **PASS** |
| 6 | **Supersession support** | **PASS** — `supersedes` + class `historical` | n/a — projection | **FAIL** — no identity to supersede | **PASS** — `supersedes` in the key |
| 7 | **Auditability** | **PASS** — `INV-17` | **PASS** — `03-AUDIT-UNIVERSE.json` | **FAIL** — `ISD-G-04`, ungated | **PASS** |
| 8 | **Collision resistance** | n/a | n/a | trivially unique (serial) | **PASS** — §4.3 |

**`R-3` fails six of eight. No other population fails any.**

### 4.2 Against named law

| Law | Text | `R-3` |
|---|---|---|
| `UCKP-ART-05` | *"An identity, once minted, **never changes**."* | **FAILS** — positional; insertion shifts every later id |
| `UCKP-ART-13` | *"Every digest, identity, proof and decision is computed through **one canonical form**."* | **FAILS** — position is not a canonical form |
| `UCKP-ART-14` | *"It appends; it never rewrites."* | **FAILS** — regenerated, not appended |
| `CAA-INV-04` | *"One append-only mint holds every repository identity, **every declared map resolves in it**."* | **FAILS** — 0 of 13,361 resolve |
| `ukb.py::allocate` | *"Allocating a permanent identifier is an **EVOLUTION** act… Identity is born by intent, **never discovered by a checker**."* | **FAILS** — minted as a side effect of regeneration |

**Five for five**, unchanged from `D-a`/`D-b` §8.2 and re-verified here.

### 4.3 Collision resistance, measured

| Measure | Value |
|---|---|
| Digest length | 12 hex = **48 bits** |
| Space | **281,474,976,710,656** |
| 50% birthday bound | **≈ 19,753,662** identifiers |
| Current edge population | **13,361** |
| Collision probability at 13,361 | **3.171 × 10⁻⁷** |

**Collision resistance is not a constraint at any plausible scale for this population.** Recorded so the choice in §7 is not later attributed to a risk that was never measured.

---

## 5. Existing Identity Authority Analysis

### 5.1 The located authorities

| Authority | Home | Owns |
|---|---|---|
| **The one mint** | `00-BOOK/DATA/id-ledger.json` via `category_seq` | *"the ONE identity authority"* (`allocate_execution` docstring) |
| **Registration authority** | `engine/registry/universal/identity.py` | `deterministic_id`, `RegistryKind`, `register_kind` |
| **Delegated registration** | `REG-AUTO-001` | `CMG-DLG-13` — *"registration, identity allocation, classification"* |
| **UCKO identity** | `engine/uckp/identity.py` | `urn_for`, `uuid_for`, `UniversalIdentity` |
| **Meta-type identity** | `engine/kernel/identity.py` | meta-objects |

### 5.2 The convergence doctrine — written, implemented, tested

`engine/tests/nucleus/test_identity_convergence.py`, module docstring, verbatim:

> *"Identity convergence is **not** the claim that one identifier format exists. **Several formats legitimately coexist, because several distinct populations exist**: meta-types are minted by `engine.kernel.identity`, knowledge objects by `engine.uckp.identity`, registered artifacts by `engine.registry.universal.identity`, and the engineering pipeline mints `ENGINEERING-EXECUTION-ONLY` runtime, execution and compilation ids that are explicitly non-authoritative. Formatting, rendering, hashing and UUID derivation are **implementation details, not authority**.*
>
> *Duplication is narrower and is what this file measures: **a generator minting an identifier inside a population another authority owns, without delegating to it.**"*

And the ownership test, `_owns_population`:

> *"This is the decision-ownership test, and it is why `"UCOS-EVO-"` is **not** flagged while `"UCOS-REL-"` is: `REL` is a registered kind code, so the authority owns that population and an inline mint there can disagree with it. `EVO` is registered nowhere, so **the authority owns nothing to disagree with**, and `evolution_id` is a **distinct population rather than an intrusion** into this one. Classifying by prefix alone would wrongly condemn it."*

Verified live: `_owns_population("UCOS-REL-")` → **True**; `_owns_population("UCOS-EVO-")` → **False**; `is_well_formed("UCOS-EVO-088bd1337123")` → **False**.

**Applying the doctrine to `UEDGE-`:** it does not carry the `UCOS-` prefix and `EDGE` is not a registered kind code. The registration authority owns nothing under it. **`UEDGE-` is a distinct population, exactly as `UCOS-EVO-` is — not an intrusion, and not a second authority over an owned population.**

> **This retires the "second identity authority" framing of `C1-F-1`.** The repository's own doctrine, implemented and tested, holds that coexisting formats over distinct populations are lawful. `C1-F-1` cannot rest on `CAA-INV-04`'s counter clause, and §14.5 records the correction.

### 5.3 The precedent — this exact defect, already retired

The same docstring, continuing:

> *"**Two such violations existed in this layer and were removed** — `OwnershipAssignment.assignment_id` (**`RELATIONSHIP`**) and `Certificate.certificate_id` (`CERTIFICATION`). Both assembled a `UCOS-` identifier inline, producing ids the registration authority *accepts* as its own — `is_well_formed` returned true and `parse_kind_name` named the kind — that it had nevertheless **never minted**."*

The retired form, preserved verbatim in the calibration test: `'"UCOS-REL-" + content_digest([a, b])[:12]'`.

The converged form, at `engine/nucleus/model.py:437`, with its own reasoning:

> *"Overlapping population plus an independent decision is authority duplication, so the decision is **delegated** and only the *natural key* is derived here.*
>
> *The natural key is the **canonical digest of the triple**, which is what a relationship's stable business key is: **two assignments expressing the same (capability, owner, authority, supersedes) collapse onto one identity**, and the digest is whitespace-free so the authority's key rule accepts it."*

```python
return deterministic_id(
    RegistryKind.RELATIONSHIP,
    ASSIGNMENT_NAMESPACE,                      # "ucos.ownership"
    content_digest([self.capability_id, self.owner_id, self.authority, self.supersedes or ""]),
)
```

**A relationship identity has already been converged onto the authority using a natural-key digest of its defining tuple.** The pattern `C1-F-1` needs is not designed here; it is copied.

### 5.4 The live guard and its reach

`test_no_module_mints_into_the_registry_namespace_inline` walks the AST of every `*.py` in `engine/nucleus` and fails if any module assembles a `UCOS-` identifier by concatenation or f-string instead of calling `deterministic_id`.

| Property | Measured |
|---|---|
| Detector shapes | `BinOp` concatenation **and** `JoinedStr` interpolation |
| Calibrated against | Both retired violations, verbatim |
| False-positive guards | Bare constants and prose excluded, tested |
| **Scope** | **`engine/nucleus` only** — `NUCLEUS_PACKAGE.glob("*.py")` |
| Reaches `00-BOOK/tools/ukb.py`? | **NO** |

**The guard that would have caught `add_edge` exists and does not reach it.** That is a reach gap of a working mechanism, not a missing mechanism.

### 5.5 The forward-looking rule this determination must honour

`test_the_evolution_population_stays_unclaimed_by_the_authority`:

> *"A guard, not a preference: this is what keeps `evolution_id` lawful. `engine.nucleus.evolution` mints `UCOS-EVO-<12hex>` itself. That is a separate population **today only because no kind is registered under the code `EVO`**. If one ever were, those identifiers would retroactively parse as registered ids of a population they do not own — the exact retroactive reinterpretation the authority's own `register_kind` refuses for codes. **Should this test fail, the fix is to make `evolution_id` delegate, not to relax the assertion.**"*

**Consequence for §7:** any resolution that registers a kind code colliding with an existing separate population would retroactively reinterpret it. §7.3 checks this explicitly.

---

## 6. Option Evaluation

Rejection criteria: second identity authority · duplicate ledger · parallel identifier system · migration-only workaround · temporary compatibility layer.

### 6.1 Option A — relationship identities become Universal Identity Ledger entities

A `by_edge` plane on the `allocate_execution` precedent, keyed by `(from, to, type)`.

| Test | Result |
|---|---|
| Second identity authority | **NONE** — the ledger *is* the one mint |
| Duplicate ledger | **NONE** — a plane, not a ledger |
| Parallel identifier system | **NONE** |
| Migration-only workaround | **NONE** — permanent |
| Temporary compatibility layer | **NONE** |
| Precedent | **`allocate_execution`** — keyed, idempotent, append-only |
| Immutable / minted once | **PASS** — keyed lookup returns the existing id |
| Deterministic reproducibility | **PARTIAL** — reproducible *from the ledger*, not from the edge |
| Historical preservation | **PASS** — the `history` plane becomes available |
| **Cost** | Ledger grows by **13,361** entries — a **208%** increase over 6,413 |

**VIABLE.** Its weakness is that reproducibility becomes ledger-dependent: losing the ledger loses the ids.

### 6.2 Option B — relationship identities remain derived identifiers from relationship objects

No identifier at all; the edge is identified by `(from, to, type)`.

| Test | Result |
|---|---|
| All five rejection criteria | **NONE** |
| Precedent | **`R-1` (13,036 edges) and `R-2` (34,872 edges)** — both carry no identity |
| Immutable / minted once | **PASS vacuously** — nothing is minted |
| Deterministic reproducibility | **PASS** — the triple is the identity |
| Historical preservation | **PASS** — on the objects (`ART-12`) |
| Supersession | **PASS** — relation `supersedes`, class `historical` |
| **Cost** | **`inverse_of` must change** — it references an `edge_id`; 5,069 edges use it |

**VIABLE, and it is what the majority of the repository already does.**

### 6.3 Option C — relationship objects receive deterministic content-addressed identity

`edge_id = deterministic_id(RegistryKind.RELATIONSHIP, <namespace>, content_digest([from, to, type]))`.

| Test | Result |
|---|---|
| Second identity authority | **NONE** — delegates to the registration authority |
| Duplicate ledger | **NONE** — needs no ledger; recomputable |
| Parallel identifier system | **NONE** — enters the `REL` population the authority owns |
| Migration-only workaround | **NONE** |
| Temporary compatibility layer | **NONE** |
| Immutable | **PASS** — a pure function of the triple |
| Minted once | **PASS** — idempotent by construction |
| Authority namespaced | **PASS** |
| Deterministic reproducibility | **PASS** |
| Historical preservation | **PASS** — the id is stable, so history can attach |
| Supersession | **PASS** |
| Auditability | **PASS** — recomputable by any auditor |
| Collision resistance | **PASS** — §4.3; and the triple is **unique across all 13,361** |
| Precedent | **`OwnershipAssignment.assignment_id`** — the identical act for a relationship |
| `inverse_of` | **Preserved** — still an `edge_id`, now stable |

**VIABLE, and precedented for exactly this entity class.**

### 6.4 Option D — reuse an existing universal identity mechanism

This is not a rival to C; it is the statement of *which* mechanism C uses. `deterministic_id` + `RegistryKind.RELATIONSHIP` + `register_kind` already exist, and `RELATIONSHIP` is already a registered kind.

**ABSORBED INTO OPTION C.** C is D applied to edges.

### 6.5 Option E — other existing constitutional mechanism discovered

Four located that no prior determination in this chain had cited:

| # | Mechanism | Bearing |
|---|---|---|
| `E-1` | **The convergence doctrine** (§5.2) | Retires `C1-F-1`'s authority framing |
| `E-2` | **The retired inline RELATIONSHIP mint** (§5.3) | Supplies the exact remediation shape |
| `E-3` | **The inline-mint AST guard** (§5.4) | Exists; does not reach `ukb.py` |
| `E-4` | **UGA `kind_bindings`** (§9.2) | An exemplar of `CAA-INV-05` clause-2 binding |

**None is a fifth identity model.** `E-1` and `E-2` decide between the four; `E-3` is enforcement; `E-4` bears on `C1-F-2`.

### 6.6 Result

| Option | Verdict | Basis |
|---|---|---|
| A — ledger entities | **VIABLE, NOT SELECTED** | Reproducibility becomes ledger-dependent; +208% ledger growth for a derived population |
| **B — derived, no identifier** | **SELECTED as the model** | What `R-1` and `R-2` already do; an edge's identity is its triple |
| **C — deterministic content-addressed** | **SELECTED as the form** | Where a handle is needed (`inverse_of`, dangling reports), it is computed from that same triple through the existing mint |
| D — reuse existing mechanism | **ABSORBED into C** | `deterministic_id` + `RELATIONSHIP` |
| E — other mechanism | 4 located, none a rival model | §6.5 |

**B and C are one answer, not two.** B states what an edge's identity *is* — its natural key. C states how that identity is *rendered* as a handle when one is required. `OwnershipAssignment` is precisely this pairing: the natural key is the digest of the triple; the rendering is `deterministic_id`.

---

## 7. Canonical Relationship Identity Model

### 7.1 The model

> **A relationship's identity is its natural key — the tuple that defines it. Where a handle is required, that handle is `deterministic_id(RegistryKind.RELATIONSHIP, <namespace>, content_digest(<natural key>))`, computed through the one registration authority and recorded nowhere, because it is recomputable.**
>
> **This is not designed here. It is `OwnershipAssignment.assignment_id`, already in the repository, already tested, already the retirement of an inline mint of exactly this kind.**

### 7.2 What each population does under the model

| Population | Identity | Change required |
|---|---|---|
| `R-1` UCKP derived | The claiming object's id + the triple | **None** |
| `R-2` UGA projection | `{from, kind, to}` | **None** — declares itself a projection |
| `R-4` Nucleus | `deterministic_id(REL, "ucos.ownership", digest(...))` | **None** — already converged |
| **`R-3` UKB book edges** | **`deterministic_id(REL, <ns>, digest([from, to, type]))`** | **The one act** |

### 7.3 The retroactive-reinterpretation check (§5.5)

`test_the_evolution_population_stays_unclaimed_by_the_authority` requires that no resolution cause existing identifiers to retroactively parse as ids of a population they do not own.

| Check | Result |
|---|---|
| Does the model register a **new** kind code? | **No** — `RELATIONSHIP`/`REL` is already registered |
| Would any existing id retroactively parse differently? | **No** — `UEDGE-` lacks the `UCOS-` prefix; `is_well_formed("UEDGE-000000001")` is **False** and stays False |
| Would `UCOS-EVO-` be affected? | **No** — `EVO` remains unregistered |
| Does it collide with `R-4`'s population? | **No** — distinct namespaces (`ucos.ownership` vs a book-edge namespace) |

**Clean on all four.** The namespace parameter is what keeps two relationship populations inside one kind code without collision — the mechanism's designed purpose.

### 7.4 Feasibility, measured

Computed read-only over an existing edge (`UCOS-CON-000021 → UCOS-IDX-000001`, `Depends-On`):

```
deterministic_id(RELATIONSHIP, "ucos.book.edge",
                 content_hash(["UCOS-CON-000021","UCOS-IDX-000001","Depends-On"]))
  →  UCOS-REL-a76b71741947
```

*(The namespace string above is illustrative for the computation only. Selecting it is an owner act — §11.4.)*

| Property | Measured |
|---|---|
| `(from, to, type)` unique across 13,361 edges | **TRUE** — 13,361 distinct triples |
| Therefore distinct ids produced | **13,361** |
| Collision probability | **3.171 × 10⁻⁷** |
| `is_well_formed` on the result | **True** |
| `parse_kind_name` on the result | `RELATIONSHIP` |

### 7.5 The eight identity properties under the model

| # | Property | Satisfied by |
|---|---|---|
| 1 | Immutable | Pure function of the triple |
| 2 | Minted once | Idempotent — same triple, same id, forever |
| 3 | Authority namespaced | `deterministic_id` normalises the namespace |
| 4 | Deterministic reproducibility | Recomputable by any party from public data |
| 5 | Historical preservation | The id is stable, so `history` can key on it |
| 6 | Supersession | The triple carries `type`; `Supersedes` is a type |
| 7 | Auditability | Any auditor recomputes and compares |
| 8 | Collision resistance | §4.3 · triple uniqueness proven |

**Eight of eight.**

---

## 8. edge_id Disposition

### 8.1 The determination

> **`UEDGE-NNNNNNNNN` is not an identity and must not be treated as one. Its permanent disposition is to be replaced by a value derived from the edge's natural key `(from, to, type)` through `deterministic_id(RegistryKind.RELATIONSHIP, …)`.**
>
> **The defect is determinism, not authority.** Under the repository's own convergence doctrine, `UEDGE-` is a lawful distinct population by prefix. It fails regardless, because `ART-05` and `ART-13` bind every identifier, not only those in an owned population. `UCOS-EVO-` is lawful as a separate population **because it is content-derived**; `UEDGE-` is positional and is therefore not.

### 8.2 The four `C1-F-1` sub-questions, re-answered

| # | Question | Answer |
|---|---|---|
| 1 | Is `edge_id` identity? | **NO.** Positional over unsorted traversal; fails `ART-05`, `ART-13`, `ART-14`, `CAA-INV-04` and `allocate`'s own rule |
| 2 | Is `UCOS-REL-…` identity? | **YES.** Pure function of `(code, namespace, natural_key)`; `is_well_formed` True; `parse_kind_name` recovers `RELATIONSHIP` |
| 3 | Are both required? | **NO.** One question, two answers. The nucleus precedent already collapsed a case of exactly this |
| 4 | Should one become derived? | **YES — `edge_id`**, as the one that is not an identity. §7 gives the form |

### 8.3 Why not simply delete `edge_id`

Pure Option B would require changing `inverse_of` (5,069 edges) and every consumer that treats `edge_id` as a handle. Option C keeps the field, the schema and every consumer, and changes only how the value is computed. **That is the smaller and more conservative act, and it is the one with a precedent.**

### 8.4 Consumer impact, measured

`edge_id` appears in **78** files. Consumers outside tests:

| Consumer | Use |
|---|---|
| `ukbx.py:515`, `:1064` | Dangling-endpoint reporting — opaque handle |
| `ukb.py:1531` | A markdown table cell — opaque handle |
| `ukb.py:1032` | Production |
| `UCCEP-000005/derive.py:78,163,178` | Duplicate-id detection — opaque handle |

| Test | Result |
|---|---|
| Any consumer depending on **ordinality** | **NONE FOUND** |
| Any consumer depending on the `UEDGE-` **prefix** | **NONE FOUND** |
| Any consumer depending on the **9-digit width** | **NONE FOUND** |
| `inverse_of` referential integrity today | **0 dangling** across 5,069 |
| Would determinism preserve it? | **Yes** — both edges of a pair are computed from their own triples |

**Every consumer treats `edge_id` as an opaque handle. Changing its derivation changes no consumer's behaviour.**

### 8.5 The duplicate-detection interaction

`UCCEP-000005/derive.py:178` reports `duplicate_edge_ids`. Under determinism, two identical triples would produce one id — the *"two assignments expressing the same … collapse onto one identity"* doctrine. `add_edge` already dedups on `(src, dst, etype)` before minting, so no duplicate triple can reach the register. **Measured: 13,361 edges, 13,361 distinct triples, 13,361 distinct ids — no collapse occurs at this baseline.**

### 8.6 The enforcement gap

The AST guard that catches inline mints exists and is calibrated against two retired violations, but its scope is `engine/nucleus/*.py`. It does not reach `00-BOOK/tools/`.

**Recorded as a finding.** Widening its reach is an owner act (§11.5) and is not authorised here. Note also that `add_edge` would **not** be caught even by a widened guard as currently written: the detector matches literals beginning `UCOS-`, and `UEDGE-` does not. **A guard widened in scope but not in shape would report clean.**

---

## 9. Relation Vocabulary Identity Model

### 9.1 The `C1-F-2` identity question

> Are **semantic identity**, **relation-type identity** and **relationship-instance identity** three identities or one?

**Three, and they are already three.** Collapsing them would be the category error `UCRD-001` §5.1 disposition 2 already rejected.

| Level | What it identifies | Bearer | Identity today |
|---|---|---|---|
| **L1 — semantic** | What "depends-on" *means* | `Term` in `uckp.relation-type` | The `term_id` within its vocabulary. **No universal id** |
| **L2 — relation type** | The type as a governed thing | A term projected as a UCKO | A URN — *available*, not yet done for relation terms |
| **L3 — instance** | This binding between these two entities | An edge | The natural key `(from, to, type)`; §7 |

### 9.2 A correction to `D-a`/`D-b` §5.2

`D-a`/`D-b` recorded that `CAA-INV-05` clause 2 — *"every relationship kind any projection emits binds to a class and an article"* — is unperformed.

**Measured here: one projection already performs it.** `00-MASTER/UCOS-UGA-001/04-RELATIONSHIP-GRAPH.json` carries `kind_bindings`, binding each of its 6 kinds to a `uckp_class`, a `uckp_relation`, a `direction` and an **`article`**:

```json
"owned_by":  {"uckp_class":"ownership",      "uckp_relation":"owns",       "direction":"inverse", "article":"UCKP-ART-06"},
"produced_by":{"uckp_class":"traceability",  "uckp_relation":"produces",   "direction":"inverse", "article":"UCKP-ART-19"},
"depends_on":{"uckp_class":"constitutional", "uckp_relation":"depends-on", "direction":"forward", "article":"UCKP-ART-07"}
```

and declares its own standing:

> *"**PROJECTION.** This surface measures the repository-object edge POPULATION. **It declares no relationship class: what a relationship IS lives in `engine/uckp/graph.py`.**"*

with `model_owner`: `{"authority": "UCKP-ART-07", "home": "engine/uckp/graph.py", "owns": "What a relationship is, what an edge is, what makes an edge resolvable…"}`.

> **The `D-a`/`D-b` finding narrows: the binding is unperformed for the P2 and P3 planes, and it is *performed, correctly and completely*, by UGA. An exemplar exists.** §14.5 records this.

### 9.3 The three-level model and its identity requirements

| Level | Needs a universal identity? | Why |
|---|---|---|
| **L1 semantic** | **NO** | A `Term` is a member of a vocabulary; the vocabulary is the UCKO and carries the identity (13 of 13 vocabularies are graph nodes) |
| **L2 type-as-object** | **ONLY IF PROJECTED** | If a relation term is projected as a UCKO — the `C-1` Option D act — it gets a URN like any object. Required for term supersession (`D-a`/`D-b` §9.4) |
| **L3 instance** | **ONLY AS A HANDLE** | §7 — derived, never allocated |

### 9.4 Determination

> **Semantic identity, relation-type identity and relationship-instance identity are three distinct identities over three distinct populations, and the repository already treats them so. `C1-F-2`'s identity dimension therefore requires no unification — attempting one would collapse three populations into a false single, which `ART-03` and `UCRD-001` both forbid.**
>
> **What `C1-F-2` still requires is the `CAA-INV-05` clause-2 binding for the P2 and P3 planes — and UGA `kind_bindings` is the located exemplar of exactly that act.**

---

## 10. Infinite Evolution Validation

### 10.1 The seven capabilities

For a future relationship nobody has yet conceived:

| # | Capability | Mechanism | Available? |
|---|---|---|---|
| 1 | **Appear** | A `RELATES <Type>` front-matter row · a `Relationship` facet on an object | **YES** |
| 2 | **Receive identity** | `deterministic_id(REL, ns, digest(natural key))` — no allocation, no ledger write, no manual step | **YES** under §7 |
| 3 | **Define semantics** | `Term.definition`; `type`+`inverse`+`labels` | **YES** |
| 4 | **Connect entities** | `Relationship` facet → `derive_edges` → `UniversalKnowledgeEdge` | **YES** |
| 5 | **Evolve** | Object-plane lifecycle facet (`C-1` Option D) | **YES via projection** |
| 6 | **Supersede** | relation `supersedes` + class `historical`; type `Supersedes`/`Superseded-By` | **YES** |
| 7 | **Remain auditable** | Recomputable id + `INV-17` + `history` keyed by identity | **YES under §7; NO today** — `ISD-G-04` |

### 10.2 The four prohibitions

| Prohibition | Under §7 | Today |
|---|---|---|
| **No source modification** | Identity needs none — a new triple yields a new id automatically | Same |
| **No enum modification** | `RELATIONSHIP` is already registered; `register_kind` is open | Same |
| **No schema rewrite** | `edge_id` stays a string; the schema's pattern is `^UEDGE-[0-9]{9,}$` — **would need one pattern change**, or `$comment` already permits an open type space | **One pattern edit** |
| **No manual identifier assignment** | **HONOURED** — a pure function, never assigned | **HONOURED** — a counter, never assigned |

**One qualification, stated plainly:** `relationship.schema.json` pins `edge_id` to `^UEDGE-[0-9]{9,}$`. Adopting §7 requires changing that pattern once. That is a **one-time schema change to remove a closure**, of the same class as the one-time code in `CEP-MOD-002` — not a recurring cost, and not a rewrite of the schema.

### 10.3 The identity dimension specifically

| Question | Answer |
|---|---|
| Can a future relationship obtain identity without code? | **YES** — `deterministic_id` is total over any `(kind, namespace, natural_key)` |
| Without a new kind? | **YES** — `RELATIONSHIP` exists |
| Without a ledger write? | **YES** — recomputable, so nothing must be recorded |
| Without manual assignment? | **YES** — a pure function |
| Without a namespace decision? | **NO** — a namespace must be chosen once per population (§11.4) |

### 10.4 Where infinite evolution still does not hold

Unchanged from `D-a`/`D-b` §10.3 and re-verified: on the **object plane**, admitting a *new relation type* remains a two-sided act — vocabulary term **plus** `RelationType` enum member (`RCL-01`). **That is a semantic constraint, not an identity one**, and §7 neither worsens nor repairs it.

---

## 11. Authority Ownership

**No authority is invented. Each row is a located owner or an explicit "not located."**

### 11.1 Identity minting

| Field | Located |
|---|---|
| The one mint | `id-ledger.json` via `category_seq` — *"the ONE identity authority"* |
| Registration authority | `engine/registry/universal/identity.py` — `deterministic_id`, `RegistryKind`, `register_kind` |
| Delegated authority | **`REG-AUTO-001`** — `CMG-DLG-13`: *"registration, identity allocation, classification"* |
| Convergence doctrine owner | `engine/tests/nucleus/test_identity_convergence.py` — enforcement, not declaration |
| Relationship kind | `RegistryKind.RELATIONSHIP` → `REL` — **already registered** |

### 11.2 Relationship admission

| Plane | Owner |
|---|---|
| Object | `RELATION_TYPE_VOCABULARY` + the `RelationType` projection (two-sided) |
| Book | `UMB-006 §3`, `UMB-IMP-002`, `AUTH-INF-001 CR-INF-007`; mechanism `RELATES` |
| Meta-constitutional | `CMG-000001` via `CMG-REGISTRY.json` |
| Repository-object population | `UCOS-UGA-001`, `standing: PROJECTION` |

### 11.3 Semantic vocabulary

| Field | Located |
|---|---|
| What a relationship **is** | `engine/uckp/graph.py` — named by UGA's own `model_owner`, authority `UCKP-ART-07` |
| Relation type / class | `UCRD-001` Tiers 3 and 2 — `RELATION_TYPE_VOCABULARY` (17), `RELATIONSHIP_CLASS_VOCABULARY` (12) |
| Admission **party** | **NOT LOCATED** — the register names a mechanism, not a role |

### 11.4 Supersession

| Subject | Owner |
|---|---|
| Object relationships | `ART-12`; `UAUE-000001` `AUE-P-11` |
| Relation terms | Object plane only — no in-vocabulary owner, by design |
| Instruments | `CEP-007` via `CMG-DLG-07` |
| **Edge supersession** | **UNAVAILABLE TODAY** — `R-3` has no stable identity to supersede |

### 11.5 Certification

| Subject | State |
|---|---|
| UCKP objects / edges | `UICM`, `verify.sh` stages |
| UGA | `07-CERTIFICATION.json`; `verify.sh` UGA-INV-01..10 stage |
| **The 13,361 book edges** | **NONE** — `ISD-G-04`, ungated |

### 11.6 Decisions that remain

| # | Decision | Owner | Kind |
|---|---|---|---|
| `RI-a` | Adopt §7 for `edge_id` — derived through the mint | **`REG-AUTO-001`** | **Identity authority** |
| `RI-b` | The namespace string for the book-edge population | `REG-AUTO-001` | **Identity authority** |
| `RI-c` | Change `relationship.schema.json`'s `edge_id` pattern | Schema owner | **Owner** |
| `RI-d` | Widen the AST guard's **scope and shape** (§8.6) | Identity authority | **Owner** |
| `RI-e` | Gate the 13,361 edges (`ISD-G-04`) | UKB / relationship owner | **Referral** |
| `RI-f` | Bind P2/P3 kinds to classes and articles, on UGA's exemplar | Relationship-model owner | **Referral** |

---

## 12. Migration / Evolution Sequence

**Sequence and dependency only. Nothing below is authorised by this determination.**

| Step | Act | Depends on | Disposition |
|---|---|---|---|
| `RI-1` | Choose the namespace for the book-edge population | `RI-b` | **DECISION** |
| `RI-2` | Change `edge_id` to `deterministic_id(REL, <ns>, content_digest([from, to, type]))` | `RI-1` | **REUSE** — precedent `assignment_id` |
| `RI-3` | Change the schema pattern from `^UEDGE-[0-9]{9,}$` to the registration grammar | `RI-2`, `RI-c` | **EXTEND** — one-time closure removal |
| `RI-4` | Regenerate; verify 13,361 distinct ids and 0 dangling `inverse_of` | `RI-2` | **VERIFY** |
| `RI-5` | Widen the AST guard in scope **and** shape | `RI-d` | **EXTEND** |
| `RI-6` | Optionally add a `by_edge` ledger plane for history | `RI-2` | **EXTEND** — `allocate_execution` precedent |
| `RI-7` | Gate the edges against the schema | `RI-e` | **REFERRAL** |

**`CREATE` count: 0. New authorities: 0. New ledgers: 0. New identifier systems: 0.**

### 12.1 Preservation

| Requirement | Mechanism |
|---|---|
| Historical relationships preserved | No edge removed; `from`, `to`, `type`, `note` unchanged; only `edge_id`'s derivation changes |
| Existing evidence preserved | `ART-19` invertibility; the triple is retained verbatim |
| Existing references preserved | `inverse_of` still holds an `edge_id`; both sides recompute consistently; **0 dangling today, 0 after** |
| Consumers preserved | All four treat `edge_id` as opaque — §8.4 |
| Rollback before acceptance | The change is confined to one function and one schema pattern |

### 12.2 The one-way property

Once ids are content-derived they are **stable forever**: the same triple yields the same id in every future build, on any machine, by any auditor. That is the property `UEDGE-` never had and cannot be given by any counter.

---

## 13. Remaining Constraints

| Id | Severity | Constraint | Owner |
|---|---|---|---|
| `RIC-1` | **HIGH** | **13,361 edge ids fail identity law today.** Six of eight identity properties, five named laws. Disposition determined (§8); execution is `RI-a` | `REG-AUTO-001` |
| `RIC-2` | **MEDIUM** | **The inline-mint guard reaches only `engine/nucleus`, and its detector matches only `UCOS-`-prefixed literals.** Widening scope without widening shape would report clean on `add_edge` | Identity authority |
| `RIC-3` | **MEDIUM** | **The 13,361 edges are ungated** against `relationship.schema.json` — `ISD-G-04`. Carried, count re-measured | UKB / relationship owner |
| `RIC-4` | **MEDIUM** | **Two identifier grammars coexist and neither validates the other.** `is_well_formed` rejects all 6,413 ledger ids. Lawful under the convergence doctrine (distinct populations), but no instrument states the boundary between them | Identity authority |
| `RIC-5` | LOW | **`RCL-01` persists** — a new *relation type* on the object plane is a two-sided act. Semantic, not identity; §7 neither worsens nor repairs it | Relation-type owner |
| `RIC-6` | LOW | **P2/P3 kinds still bind to no class or article.** Narrowed by §9.2 — UGA performs the binding and is the exemplar | Relationship-model owner |

### 13.1 What §7 does not fix

| Not fixed | Why |
|---|---|
| `ISD-G-04` enforcement | An identity is not a gate |
| `RCL-01` two-sided admission | A semantic constraint |
| Edge history | Requires `RI-6`, a ledger plane, which §7 makes *possible* but does not perform |
| The grammar boundary (`RIC-4`) | Pre-existing; disposing of it is `non_goals[5]` |

---

## 14. Final Determination

### 14.1 Verdict

> # CONDITIONALLY RESOLVED

### 14.2 The four required answers

**1 — Is there exactly one relationship identity authority?**

> **YES for the population the authority owns; and the coexistence of other populations is lawful under the repository's own written doctrine.**
>
> `RegistryKind.RELATIONSHIP` → `REL` with `deterministic_id` is the sole authority over the `REL` population, and `engine/nucleus` already delegates to it. The convergence doctrine states plainly that *"several formats legitimately coexist, because several distinct populations exist"*, and that the violation is only *"minting inside a population another authority owns, without delegating to it."* By that test — implemented in `_owns_population` and verified live — `UEDGE-` is a distinct population, not a rival authority.
>
> **This is a change from what `C-1` recorded**, and §14.5 states it as a correction.

**2 — Is every relationship identity governed by universal identity law?**

> **NO.** Of four populations, three carry no identifier (correctly — they are derived or projections) and one delegates correctly. **`R-3`'s 13,361 `UEDGE-` ids fail six of eight identity properties and five named laws**: `ART-05`, `ART-13`, `ART-14`, `CAA-INV-04`, and `allocate`'s own rule that *"identity is born by intent, never discovered by a checker."*
>
> The failure is **determinism, not authority**. `UCOS-EVO-` is a lawful separate population *because it is content-derived*; `UEDGE-` is positional and so fails on its own terms wherever it sits.

**3 — Can future relationships evolve without code modification?**

> **On the identity dimension — YES, under §7.** `deterministic_id` is total over any `(kind, namespace, natural_key)`; `RELATIONSHIP` is already registered; nothing is allocated, recorded or manually assigned. A future edge obtains its identity by existing.
>
> **On the semantic dimension — plane-dependent, and NO on the object plane.** `RCL-01` makes a new relation type a two-sided act (`RIC-5`). Unchanged by this determination.
>
> **One qualification:** adopting §7 requires a **single** change to `relationship.schema.json`'s `edge_id` pattern — a one-time removal of a closure, not a recurring cost.

**4 — Are `C1-F-1` and `C1-F-2` permanently closed?**

> **NO — neither. Both are now fully determined, and neither is closed.**
>
> **`C1-F-1`** — the disposition is settled (§8): `edge_id` is not an identity and must become derived through the existing mint, on the `OwnershipAssignment` precedent. Closure requires `RI-a`, an act of `REG-AUTO-001`. Its diagnosis has been corrected **twice** — first from *"sequential vs deterministic"* to *"positional and unkeyed"* (`D-a`/`D-b` §4.3), now from *"second identity authority"* to *"lawful population, unlawful derivation"* (§5.2).
>
> **`C1-F-2`** — its **identity dimension is answered** (§9.4): semantic, type and instance identity are three populations and correctly remain three. Its **binding dimension is narrowed** (§9.2): UGA already performs the `CAA-INV-05` clause-2 binding, so an exemplar exists and the gap is P2/P3 only. Closure requires `RI-f`, a referral.

### 14.3 Why `CONDITIONALLY RESOLVED`

**Not `PERMANENTLY RESOLVED`:** 13,361 identifiers fail identity law at this baseline, answers 2 and 4 are NO, and closure requires acts by `REG-AUTO-001` and the schema owner that this artifact holds no authority to take.

**Not `NOT RESOLVED`:** the canonical model is determined, **precedented three times** (`assignment_id`, `certificate_id`, `evolution_id`), **proven feasible by measurement** (triple uniqueness, consumer independence, collision bound), and requires **no new authority, no new ledger, no parallel identifier system, no workaround and no compatibility layer**. What remains is one decision and its execution.

### 14.4 Against the rejection criteria

| # | Thing | Created? | Basis |
|---|---|---|---|
| 1 | **Second identity authority** | **NO** | `deterministic_id` is the existing authority; `RELATIONSHIP` already registered |
| 2 | **Duplicate ledger** | **NO** | The model needs no ledger — ids are recomputable. `RI-6` is optional and is a *plane*, not a ledger |
| 3 | **Parallel identifier system** | **NO** | It *removes* one: `UEDGE-` folds into the `REL` population |
| 4 | **Migration-only workaround** | **NO** | Permanent; the one-way property (§12.2) |
| 5 | **Temporary compatibility layer** | **NO** | The field, schema field and every consumer are preserved; only the derivation changes |

**Five of five: NO.**

### 14.5 Corrections of record

| # | Correction |
|---|---|
| 1 | **`C1-F-1`'s authority framing is retired.** `C-1` recorded *"`CAA-INV-04` recognises a second identity authority by the counter it advances."* The repository's own convergence doctrine — written, implemented and tested in `test_identity_convergence.py` — holds that coexisting formats over **distinct populations** are lawful, and that the violation is minting *inside an owned population*. `UEDGE-` is not in an owned population. **The finding survives, on a different and narrower ground: non-determinism** — §5.2, §8.1 |
| 2 | **`D-a`/`D-b` §5.2 is narrowed.** I recorded that `CAA-INV-05` clause 2 is unperformed. Measured here: `UCOS-UGA-001/04-RELATIONSHIP-GRAPH.json` performs it completely for its 6 kinds — `uckp_class`, `uckp_relation`, `direction` and `article` each — and declares its own standing as PROJECTION with `engine/uckp/graph.py` as model owner. **The gap is P2/P3 only, and an exemplar exists** — §9.2 |
| 3 | **This chain had not read the convergence doctrine or the UGA relationship graph.** Both predate every artifact in it and both bear directly. `ART-18` requires locating the canonical object first; that step, performed here, retired one framing and narrowed another |

### 14.6 What this determination did not do

| Not done | Under |
|---|---|
| Mint, allocate or alter any identity | Directive |
| Modify code, registries or relationship data | Directive |
| Register a kind, namespace or vocabulary term | Directive |
| Select the namespace string for the book-edge population | `RI-b` — an owner act |
| Dispose of `RIC-1`…`RIC-6` | `non_goals[5]` |
| Execute or authorise `RI-1`…`RI-7` | No authority held |
| Disturb `UCRD-001` or the convergence doctrine | Both govern |

---

## 15. Verification Record

### 15.1 Before / after

| Field | Before | After | Delta |
|---|---|---|---|
| HEAD | `bae59755…5269a` | `bae59755…5269a` | **unchanged** |
| Branch | `integration/recovery-001` | `integration/recovery-001` | **unchanged** |
| `git status --porcelain` | **362** | **363** | **+1 — this artifact** |
| Tracked modifications | **38** | **38** | **unchanged** |
| Staged | **0** | **0** | **unchanged** |
| Untracked | **324** | **325** | +1 |
| Commits | **0** | **0** | **none** |

### 15.2 Required post-write assertions

| Assertion | Result |
|---|---|
| Only one new artifact | **VERIFIED** — porcelain +1 |
| HEAD unchanged | **VERIFIED** |
| Branch unchanged | **VERIFIED** |
| Code unchanged | **VERIFIED** — tracked mods 38, unchanged |
| Registry unchanged | **VERIFIED** — no `00-BOOK/DATA/*`, `00-CMG/*`, `00-BOOK/SCHEMAS/*`, `00-MASTER/*` in the delta |
| Identity unchanged | **VERIFIED** — `id-ledger.json` untouched; every `deterministic_id` call was a pure function evaluated in-process and discarded |
| Ownership unchanged | **VERIFIED** |
| Certification unchanged | **VERIFIED** |
| Relationship data unchanged | **VERIFIED** — `relationships.json` and UGA graph read only |
| No commits | **VERIFIED** |

### 15.3 Live measurements

| Measurement | Method | Result |
|---|---|---|
| Ledger ids by shape | Regex over 6,413 | **100%** `UCOS-<CAT>-NNNNNN` · **0%** `UCOS-<CODE>-<12hex>` |
| `UEDGE-` / `UCOS-REL-` in ledger | Membership | **0** / **0** |
| `UCOS-REL-` in `00-BOOK/DATA/*.json` | `grep -c` | **0** |
| Ledger planes | Key inspection | `by_path` 1,492 · `by_object` 4,914 · `by_observation` 7 · **no edge plane** |
| `history` plane | Key inspection | **1,492** entries, keyed by `universal_id` |
| `is_well_formed` probes | Direct call | `UEDGE-…` **False** · `UCOS-EVO-…` **False** · `UCOS-REL-…` **True** · `UCOS-BOOK-000000` **False** |
| `_owns_population` | Direct call | `UCOS-REL-` **True** · `UCOS-EVO-` **False** |
| Book edges | JSON parse | **13,361** · **13,361** distinct `edge_id` · **5,069** with `inverse_of` · **0** dangling |
| **Natural-key uniqueness** | Set over `(from,to,type)` | **13,361 distinct — unique** |
| UGA relationship graph | JSON parse | **34,872** relationships · **6** kinds · fields `{from, kind, to}` only · **no identity field** |
| UGA `kind_bindings` | JSON parse | **6 of 6** bind `uckp_class`, `uckp_relation`, `direction`, `article` |
| UCKP derived edges | `build_universe().graph()` | **13,036** |
| `edge_id` producer | Source read | `ukb.py:1020-1033` — build-local counter, key discarded |
| Edge sorting before write | `grep` | **none** |
| `edge_id` consumers | `grep` across 78 files | 4 non-test uses, **all opaque handles** |
| Digest length / space | `_ID_DIGEST_LEN` | 12 hex = 48 bits · space 2.81 × 10¹⁴ |
| Birthday bound | Arithmetic | 50% at **19,753,662**; P at 13,361 = **3.171 × 10⁻⁷** |
| Candidate edge id | `deterministic_id` (pure, discarded) | `UCOS-REL-a76b71741947` |
| `RegistryKind` / extensions | Import | **29** core · **0** registered extensions |
| Convergence guard scope | Source read | `engine/nucleus/*.py` only; detector matches `UCOS-`-prefixed literals |

### 15.4 What was not verified

| Not verified | Why |
|---|---|
| That regenerating the corpus renumbers `edge_id` | Would require running `ukb.py`, which writes. Established by **reading** the producer: unkeyed counter over unsorted traversal |
| That `RI-2` passes `verify.sh` | Would require implementing it. Out of mode |
| The namespace string for the book-edge population | `RI-b`, an owner act. The §7.4 string is illustrative for the computation only |
| Whether `RIC-4`'s grammar boundary is a live breach | Requires the identity authority's disposition; `non_goals[5]` |
| That four relationship populations are the complete set | Measured across `engine/uckp`, `engine/registry`, `engine/nucleus`, `00-BOOK/DATA`, `00-MASTER/UCOS-UGA-001`. A fifth elsewhere would not have been seen |
| Current `verify.sh` verdict | Not executed — `ISD-G-11`; this mode forbids surface mutation |

### 15.5 Artifact creation verified

| Check | Result |
|---|---|
| File exists | **Yes** |
| Required sections | **15 of 15, in the specified order** |
| Verdict | **Exactly one permitted value — `CONDITIONALLY RESOLVED`** |
| Four required questions | **All four answered explicitly — §14.2** |
| Git status | `??` untracked — the only delta from 362 |
| Other files changed | **0** |
| Commits | **0** |

---

**End of determination.**

| Field | Value |
|---|---|
| Baseline | `bae59755d7e2d3566c93b89c722b68847145269a` · `integration/recovery-001` |
| Sections | 15 |
| Relationship populations measured | **4** — 13,036 · 34,872 · 13,361 · nucleus |
| Populations carrying no identity | **2** (correctly) |
| Populations delegating to the authority | **1** |
| Populations minting positionally | **1** |
| Identity properties failed by `R-3` | **6 of 8** |
| Named laws failed by `R-3` | **5** |
| Natural-key uniqueness over 13,361 edges | **proven** |
| Collision probability at current scale | **3.171 × 10⁻⁷** |
| Options evaluated | **5** · selected **2 jointly** · absorbed **1** · rejected-as-model **2** |
| Precedents for the selected model | **3** |
| Corrections of record | **3** |
| New authorities · ledgers · identifier systems · workarounds · layers | **0 · 0 · 0 · 0 · 0** |
| `CREATE` acts | **0** |
| Code changed | **0 files** |
| Registries changed | **0** |
| **Verdict** | **CONDITIONALLY RESOLVED** |
