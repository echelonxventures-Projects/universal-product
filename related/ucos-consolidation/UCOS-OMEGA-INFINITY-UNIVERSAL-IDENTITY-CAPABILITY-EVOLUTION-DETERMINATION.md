# UCOS Ω∞ — UNIVERSAL IDENTITY CAPABILITY EVOLUTION DETERMINATION

| Field | Value |
|---|---|
| **Classification** | EVIDENCE — DETERMINATION ONLY |
| **Authority** | **NONE — DERIVED TRUTH.** This document certifies nothing, ratifies nothing, creates no authority, and mints no identifier. |
| **Mode** | READ-ONLY. No code modified, no identifier format changed, no validator updated, no identity created or migrated, no registry mutated, no certification changed, no phase created. |
| **Measurement baseline** | `git HEAD = bae59755d7e2d3566c93b89c722b68847145269a`, branch `integration/recovery-001`, 329 uncommitted working-tree entries at time of measurement |
| **Reference system** | `logical:git-commit-order@ucos-consolidation` (CMG-000002). No wall clock read. |
| **Finding markers** | Labels such as `IDF-01` below are **local reading aids scoped to this document only**. They register nothing, mint nothing, advance no counter, and enter no namespace. Deleting this file changes no verdict. |

---

## 1. Objective

Reconcile and formalize the claimed transition:

```
Finite Identity Representation  →  Universal Identity Capability
```

Determine, from repository evidence alone, whether the current identity architecture (a) separates identity **semantics** from identity **representation**, and (b) supports infinite and unlimited evolution.

**Primary question:** Has UCOS Ω∞ evolved identity from a finite representation model into a universal identity capability model?

**Answer, stated up front: NO — not yet. The transition is genuinely underway on the semantic axis and has not begun on the representation axis.**

The architecture has built an unusually strong *semantic* core: identity minting is pure, total, clock-free, storage-free and path-free across the principal planes, and this is asserted by tests. That is real and it is the hard part. But three measured facts defeat the claim as stated:

1. **Representation is not separated from semantics — it is welded to it.** The rendered string is a *stored field* that `verify()` treats as an invariant (`engine/uckp/identity.py:130-133`), and the identity's UUID is `uuid5` computed over that rendered string (`:58-60`). Changing the rendering therefore makes every persisted identity fail verification, i.e. representation change is structurally indistinguishable from tampering.
2. **There is no single identity capability. There are at least 13 structurally distinct identifier shapes minted by at least 10 independent implementations, and 58 distinct identifier prefix values declared across 53 files.**
3. **A six-digit width is enforced as law in code while the constitution declares it a presentation choice.** `engine/uckp/alignment.py:307-308` raises on any identifier that is not exactly six digits; `00-CMG/CMG-000001...CONSTITUTION.md` XXXI.4 states the opposite in terms.

The repository has already diagnosed item 3 itself and elected **disclosure over remediation**. Items 1 and 2 are, on the evidence located, undiagnosed as identity-capability defects.

---

## 2. Identity Evolution Principle

The directive's principle, restated as the test applied throughout this document.

Identity is **not**: digit count · prefix format · namespace string · storage representation · current technology encoding.

Identity **is**: authority · uniqueness · resolution · context · lineage · relationship · evolution history · validity.

Representation is one evolving projection of identity.

Two instruments in the repository state this principle independently, and both are quoted here because the rest of the document measures the code against them.

`00-MASTER/CMG-000006/CMG-000006-UNIVERSAL-AUTHORITY-IDENTITY-MODEL.md:221`:

> **Encoding is representation, not identity.**

`00-CMG/CMG-000001-CONSTITUTIONAL-META-GOVERNANCE-CONSTITUTION.md`, Article XXXI (verified verbatim):

> **XXXI.2** Sequence width SHALL be **declared per namespace** and SHALL NOT be assumed globally. The corpus presently uses widths of two, three, four, and six digits across different namespaces; a single global width would be a finite assumption and is prohibited.
>
> **XXXI.3** … width extension by left-padding SHALL be permitted without renumbering, because `CMG-000001` and `CMG-0000001` denote the same ordinal under XXXI.4.
>
> **XXXI.4** Identifier comparison SHALL be by **namespace token and numeric ordinal**, never by string. This makes zero-padding a presentation choice and removes any ceiling created by a chosen width.
>
> **XXXI.5** An identifier SHALL NOT encode meaning beyond namespace and ordinal. Encoding phase, kind, status, owner, or version into an identifier couples identity to mutable fact and IS PROHIBITED.

**Measured status of Article XXXI: NOT IMPLEMENTED.** No code anywhere parses an ordinal out of an identifier, compares two identifiers by `(namespace, int(ordinal))`, or treats padding width as a variable. Searched `engine/`, `platform/`, `data/`, `service/`, `application/`, `infrastructure/`, `intelligence/`. The string comparison XXXI.4 prohibits is what is actually enforced.

---

## 3. Current Identity Architecture

### 3.1 The declared model — two planes, one authority

`00-BOOK/DATA/constitutional-authority-alignment.json` → `identity_authority_resolution`:

> `"one_authority": "UCKP-ART-05 — Universal Identity. Every other identity mechanism in the repository is a persistence or projection binding of it."`

| Plane | Home | Shape | Declared role |
|---|---|---|---|
| `CONSTITUTIONAL_OBJECT` | `engine/uckp/identity.py` | `urn:ucos:ucko:<namespace>:<local_name>` | **SUPREME — this IS UCKP-ART-05** |
| `REPOSITORY_OBJECT` | `00-BOOK/DATA/id-ledger.json` | `UCOS-<CATEGORY>-<NNNNNN>` | **PERSISTENCE — the ONE such binding** |

Bridge: `engine.uckp.alignment.repository_local_urn`, with `id_shape: ^UCOS-[A-Z0-9]+-[0-9]{6}$` and the rationale:

> `"why_verbatim": "Any derivation that reshaped the identifier would be a re-mint wearing a projection's clothes, and UCKP-ART-05 says an identity once minted never changes."`

### 3.2 The measured model — at least 13 shapes, at least 10 mints

| # | Shape | Home (path:line) | Derivation | Pure? | Declared in an identity instrument? |
|---|---|---|---|---|---|
| 1 | `urn:ucos:ucko:<ns>:<local>` + uuid5 | `engine/uckp/identity.py:73` | caller-supplied name | yes | **yes — SUPREME** |
| 2 | `UCOS-<CODE>-<12hex>` | `engine/registry/universal/identity.py:257` | SHA-256 of `(kind, ns, key)` | yes | as UIS `MECH-EPIC001` |
| 3 | `UCOS-<CATEGORY>-<NNNNNN>` | `00-BOOK/tools/ukb.py:903`, `:2228` | **sequence counter + wall clock + file IO** | **no** | yes — persistence plane |
| 4 | `UCOS-<CAT>-<NNNNNN>` (same counter) | `00-MASTER/UCOS-UGA-001/uga_engine.py:294` | shares `category_seq` | no | yes (legitimised by shared counter) |
| 5 | `UMK-<SLUG>-<12hex>` | `engine/kernel/identity.py:87` | tuple digest | yes | **no** |
| 6 | `UAPF-<KIND>-<20hex>` | `platform/universal_pipeline/identity.py:223` | digest of kind+parts | yes | **no** |
| 7 | `urn:ucos:p2:<authority>:<32hex>` | `platform/foundation/durable_identity.py:145` | digest of admission key | value pure; registry **stateful** | **no** |
| 8 | `UKID-<12HEX>` | `engine/knowledge/ukip/contracts.py:364` | content of the statement | yes | as UIS `MECH-UKIP` |
| 9 | `UCKO-CAP-<12HEX>` | `engine/knowledge/capability.py:126` | **a filesystem path** | yes | **no** |
| 10 | `UICM-OBL/OBS/GAP-<short>-<NN>` | `engine/uicm/obligation.py:59`, `observation.py:71`, `gap.py:132` | string composition over other ids | yes | **no** |
| 11 | `UCOS-EVT-<16hex>` | `platform/foundation/dag_ledger.py:170` | event hash prefix | yes | **no** |
| 12 | bare `<16hex>`, **no prefix** | `platform/universal_control_plane/ontology.py:21-28` | digest **including a logical tick** | tick-dependent | **no** |
| 13 | `UCOS-ENTITY-<name>-<16hex>` | `data/entity.py:260` | **embeds a mutable name** | yes | **no** |

Plus a fully disjoint security identity: `platform/foundation/identity.py:51-81` `Principal.principal_id`. Grep for `UniversalIdentity`, `urn:ucos:ucko` or `deterministic_id` inside `platform/identity/` and `platform/foundation/identity.py` returns **zero matches**.

### 3.3 Prefix census — measured

| Measure | Count |
|---|---|
| Distinct identifier-prefix **values** declared in `engine/ platform/ application/ intelligence/ data/ service/ infrastructure/` | **58** |
| Distinct prefix **constant names** | **55** |
| Files declaring at least one | **53** |
| `:06d` zero-pad mint sites repo-wide (9 non-test) | **10** |

Excludes `00-BOOK/tools/` and `00-MASTER/*_engine.py`, so 58 is a **floor, not a ceiling**. `ENTITY_ID_PREFIX = "UCOS-ENTITY"` alone is redeclared as an independent literal in four `data/` modules (`entity.py:57`, `lifecycle.py:72`, `storage.py:69`, `schema.py:63`) with no shared constant.

### 3.4 Persistence surfaces — disjoint

| Store | On disk | Measured contents |
|---|---|---|
| `00-BOOK/DATA/id-ledger.json` | **yes**, 2,090,320 bytes | `by_path` 1,492 · `by_object` 4,914 · `category_seq` **200 open counters** |
| `00-MASTER/UCOS-NUCLEUS-001/UCOS-NUCLEUS-IDENTIFIER-DICTIONARY.json` | **yes**, 75,204 bytes | 212 entries (CAPABILITY 129 · NUCLEUS 43 · COMPOSITION 26 · LAYER 14) |
| `IdentityRegistry` (`platform/foundation/durable_identity.py`) | **no** | in-memory; `export()` exists, nothing writes |
| `_EXTENSION_KIND_CODES`, `_OBJECT_KINDS` | **no** | process-lifetime kind registries |
| Shapes 5–13 above | **no** | recomputed on demand; no register enumerates them |

**No repository-wide identity census exists. No cross-prefix parser or resolver exists.**

---

## 4. Identity Authority Analysis

### IDF-01 — Two contradictory identity models are declared in the same file, and both stand

- **Observation.** `00-BOOK/DATA/constitutional-authority-alignment.json` carries `identity_authority_resolution` (one SUPREME authority, everything else a projection or persistence binding) *and* `identity_namespace_resolution` (`"type": "MULTIPLE_INDEPENDENT_BOUNDED_NAMESPACES"` — "identity in UCOS is namespace-plural by design", siblings with `relationship_to_sibling_namespace: NONE`).
- **Evidence.** Both sections read directly. `PHASE-IDENTITY-NAMESPACE-GOVERNANCE-BINDING-DETERMINATION.md:63`: *"`identity_authority_resolution` was not amended — its `SUPREME`/`one_authority` claims stand exactly as before."* `:33`: *"**No universal identity authority created** … neither namespace is marked `SUPREME` over the other."*
- **Impact.** The repository has no single answer to "is identity singular or plural?". Every downstream determination inherits whichever section it happens to read. This is the root of findings IDF-02 through IDF-05.
- **Classification.** **NOT YET ASSIMILATED.**
- **Dependency.** Blocks any coherent identity capability model. Nothing downstream can be settled while both stand.
- **Closure condition.** A constituent act by the owner of `constitutional-authority-alignment.json` that either subordinates one section to the other or declares the two to govern disjoint, named populations. Not performable inside this determination.

### IDF-02 — The "no second authority" test detects only counters, so eight mints pass by construction

- **Observation.** The declared enforcement test recognises a rival authority *by the counter it advances*.
- **Evidence.** `identity_authority_resolution.second_authority_test`: *"A second identity authority would be a second APPEND-ONLY MINT — a file other than the ledger that issues repository identifiers. A mint is recognised by the counter it advances…"*, with `mint_markers = ["category_seq"]`. Implemented at `00-MASTER/UCOS-UGA-001/uga_engine.py:1008-1021` (`rival_mints`), which scans `.json` files for the literal key `category_seq`.
- **Impact.** Every content-derived mint — shapes 2, 5, 6, 7, 8, 9, 11, 12, 13 — advances no counter and therefore **cannot** trip the test regardless of how independent it is. The invariant is satisfiable while being false. `UMK-`, `UAPF-`, `urn:ucos:p2:`, `UCKO-CAP-`, `UICM-*`, the bare-hex control-plane id and `UCOS-ENTITY-<name>-` are declared in **no** identity instrument located.
- **Classification.** **PARTIALLY ASSIMILATED** — a real enforcement mechanism exists; its detection surface does not cover the actual population.
- **Dependency.** IDF-01.
- **Closure condition.** A detection rule whose subject is *the set of minting functions*, not the set of counters. Evidence that such a rule is absent: no gate enumerates prefixes in one place (searched `.github/workflows/`, `Makefile`, `verify.sh`).

### IDF-03 — Determinations disagree about which mint is the authority

- **Observation.** Two instruments name different functions as *the* identity authority.
- **Evidence.** `constitutional-authority-alignment.json` names `engine/uckp/identity.py` (UCKP-ART-05). `IDENTITY-ASSIMILATION-DETERMINATION.md:28` names a different one: *"'Every non-document object has a universal identity' minted by `deterministic_id()` through REG-AUTO-001."* `engine/ceu/existence.py` comments refer to `deterministic_id` as *"the one identifier authority"*. `B-02-UID-DICTIONARY-PERSISTENCE-DISCOVERY.md:67` records the shape conflict directly: *"`deterministic_id` emits `UCOS-<CODE>-<12 hex>`. … pins `id_shape: ^UCOS-[A-Z0-9]+-[0-9]{6}$` — which this shape does **not** match. That file never mentions `deterministic_id`."*
- **Impact.** The declared authority and the operative authority are different functions producing incompatible shapes. `:76` concedes the residual: *"the alignment file's two-plane view is narrower than UIS-001's five-plane taxonomy, and a reader consulting only the former would not find `deterministic_id`."* Closed as observation, not defect.
- **Classification.** **NOT YET ASSIMILATED.**
- **Dependency.** IDF-01, IDF-02.
- **Closure condition.** Reconciliation of the two-plane and five-plane taxonomies under one instrument. Both are owned elsewhere; no located authority is competent to perform it (see IDF-05).

### IDF-04 — Nine capability namespaces, no register

- **Observation.** Capability identity is spread across nine parallel namespaces with no single register.
- **Evidence.** `CANONICAL-AUTHORITY-RESOLUTION-DETERMINATION.md:33`: *"**9 namespaces** — UEI-CAP 185 refs · UIS-CAP 108 · UER-CAP 92 · BLN-CAP 40 · UAEP-CAP 32 · UCAF-CAP 28 · UICM-CAP 3 · EVO-CAP 1 · CTX-CAP 1"*. `:93-94`: *"**Authority hierarchy | None.** … `FG-18` asserts every capability resolves to exactly one owning Nucleus — but the nine namespaces are not registered in any surface that gate can read, so the invariant is measured over the nucleus registry's population, not over the capability population. **The two are not proven to be the same set.**"*
- **Impact.** The uniqueness property — a core identity obligation — is asserted over a population that is not proven to be the population it claims to cover.
- **Classification.** **NOT YET ASSIMILATED.**
- **Dependency.** IDF-01.
- **Closure condition.** A register that enumerates the nine namespaces in a surface `FG-18` reads. `:186` records the current state as *"unregistered, unproven."*

### IDF-05 — No located authority is competent to ratify an identity resolution

- **Observation.** The instruments that would resolve IDF-01–IDF-04 record that no competent authority exists.
- **Evidence.** `CANONICAL-AUTHORITY-RESOLUTION-DETERMINATION.md:16`: *"**three located instruments independently record that no authority in this repository is competent to ratify anything**, which makes 'reserved to a governing authority' a currently unsatisfiable disposition."* `:129-133`: `UCAF-RC-01/02/03`; `UCAF-F-002` = **`STANDING-CONSTITUTIONAL-CONFLICT`**. Verdict `:220`: **`DETERMINATION-COMPLETE · SEVEN CATEGORIES RECORDED · ZERO RESOLVED · IMPLEMENTATION-NOT-AUTHORIZED`**. `REPOSITORY-IDENTITY-ALLOCATION-OWNER-DECISION-RECORD.md:336`: **`AWAITING OWNER DECISION — NO FIELD RECORDED`**.
- **Impact.** Every identity closure condition in this document terminates in an act no in-repository authority can currently perform. This is the binding constraint on the whole transition, not a side note.
- **Classification.** **NOT YET ASSIMILATED.**
- **Dependency.** External to the repository.
- **Closure condition.** An out-of-corpus constituent act. Explicitly outside this determination's mode.

**Determination for §4: one universal identity authority does NOT exist.** It is declared, and simultaneously un-declared in the same file; the test that would enforce it cannot see nine of the thirteen shapes; and the body that would resolve the contradiction is recorded as non-existent.

---

## 5. Representation Constraint Analysis

### 5.1 The directive's decisive question: is `000001` representation or law?

**Measured answer: it is enforced as law in code, and declared to be representation in the constitution. Both are live.**

**Enforced as law.** `engine/uckp/alignment.py:87-89`:

```python
#: The shape of an identifier the one repository mint issues. Matching it is what makes
#: the derivation *total over the ledger* rather than total over anything at all.
REPOSITORY_ID_PATTERN = re.compile(r"^UCOS-[A-Z0-9]+-[0-9]{6}$")
```

The raising site, `alignment.py:306-309` (verified verbatim):

```python
    text = str(universal_id).strip()
    if not REPOSITORY_ID_PATTERN.match(text):
        raise AlignmentError(f"not a repository identifier: {universal_id!r}")
    return urn_for(REPOSITORY_NAMESPACE, text)
```

`AlignmentError` is documented at `:104-105` as *"Raised when a binding contradicts the law it claims to derive under."* A **width mismatch is classified as a law contradiction.**

Propagated to CI: `platform/tests/test_constitutional_authority_alignment.py:195-216` asserts `derivation_is_injective(identifiers) == ()` over the live ledger (`assert len(identifiers) > 5000`). A single non-six-digit identifier entering `id-ledger.json` fails CI. And `engine/tests/uckp/test_alignment.py:97-103` asserts that `"UCOS-ENGINE-496"` — valid namespace, valid ordinal, **wrong width** — must raise. **The test suite explicitly ratifies width as identity-bearing.**

**Declared to be representation.** CMG-000001 XXXI.2 prohibits a single global width as *"a finite assumption"*; XXXI.4 makes zero-padding *"a presentation choice"*. `REPOSITORY_ID_PATTERN` is a single global width applied across all category families and compares by string.

**The repository has already reached this conclusion.** `UCOS-OMEGA-INFINITY-IMPLEMENTATION-ADMISSION-READINESS-DETERMINATION.md:421-429`:

> | `:06d` at the mint | **IMPLEMENTATION DETAIL** | a zero-pad for lexical sortability; imposes no ceiling |
> | `[0-9]{6}$` at the validator | **CURRENT REPRESENTATION masquerading as UNIVERSAL RULE** | it is enforced as a rule (raises on mismatch) while being a formatting choice; **nothing constitutional requires six** |
> | Six as a count limit | **NOT a universal rule** | **the bound is an artifact of a regex quantifier** |

And its measured overflow, `:387-397`: the mint is unbounded (`:06d` is a minimum-width pad), the validator is capped. `UCOS-ENGINE-999999` matches; `UCOS-ENGINE-1000000` does **not**. Disposition chosen, `:445-449`: *"the correct disposition is **disclosure, not remediation** … the defect here is precisely that it is undisclosed."*

**Classification of the directive's four options, applied to the six-digit width:**

| Surface | Classification |
|---|---|
| `:06d` at the 9 non-test mint sites | **representation choice** |
| `[0-9]{6}` at `alignment.py:89` + its CI assertions | **implementation limitation enforced as constitutional invariant — a defect against CMG-000001 XXXI.2/XXXI.4** |
| Six as a population ceiling (10⁶ per category) | **implementation limitation.** No instrument declares 10⁶ as a bound. |

### 5.2 IDF-06 — The corpus cannot agree whether a 7-digit identifier is an identity

- **Observation.** Two independent regexes in unrelated modules give opposite answers.
- **Evidence.** `engine/uckp/alignment.py:89` — `[0-9]{6}$`, refuses. `engine/graph/validation.py:36-39` — `_IMMUTABLE_ID = re.compile(r"^(UCOS-[A-Z0-9]+-\d+|UEDGE-\d+|…)$")`, `\d+`, accepts. Nothing reconciles them; no shared constant, no cross-import, no conformance test.
- **Impact.** The graph layer will admit an identifier the alignment layer refuses. Four width-3 identifiers are **already live** (`UCOS-AEE-001`, `UCOS-RIB-001` and two others) per `…ADMISSION-READINESS-DETERMINATION.md:399-419`, which records the consequence: *"a **namespace collision between programme identifiers and minted object identifiers** — the ledger cannot distinguish them by shape, and any code that applies `REPOSITORY_ID_PATTERN` totally over ledger values will reject four live entries."*
- **Classification.** **NOT YET ASSIMILATED.**
- **Dependency.** IDF-01.
- **Closure condition.** One declared shape authority the two modules both read. Neither currently reads any.

### 5.3 IDF-07 — Representation change is structurally indistinguishable from tampering

**This is the central structural finding of this determination.**

- **Observation.** The rendered string is not a substitutable projection. It is a stored field, and an invariant.
- **Evidence.** `engine/uckp/identity.py:63-71` (verified verbatim):

  ```python
  @dataclass(frozen=True, slots=True)
  class UniversalIdentity:
      """The immutable, technology-independent identity of a UCKO."""

      namespace: str
      local_name: str
      urn: str
      uuid: str
  ```

  Two of four fields (`urn`, `uuid`) are **derived and stored**. `verify()` at `:130-133` re-derives and compares; `require_intact()` at `:135-138` raises `IdentityError("universal identity was mutated after minting")`. And `uuid_for` at `:58-60` computes `uuid5` **over the rendered URN string**:

  ```python
  def uuid_for(urn: str) -> str:
      """Return the deterministic name-based UUID of ``urn`` (pure)."""
      return str(uuid.uuid5(UCKP_NAMESPACE_UUID, urn))
  ```

  The same trap exists independently at `platform/universal_pipeline/identity.py:192-194` (`verify()` recomputes `_render_identity`).
- **Impact.** Because the cryptographic core of the identity is a function of its formatting, changing `urn_for` — i.e. evolving the representation — makes every persisted identity fail `verify()`. Representation evolution and tamper detection are the same signal. **This is the precise mechanism by which representation became law rather than projection.**
- **Classification.** **NOT YET ASSIMILATED.**
- **Dependency.** None. This is an intrinsic property of the current value object.
- **Closure condition.** A representation-independent identity core (e.g. digest over the `(namespace, local_name)` tuple rather than over the rendered string) with rendering as a derived, versioned projection. No such design is located in the repository.

### 5.4 IDF-08 — The abstraction that would separate the two is deliberately foreclosed

- **Observation.** No codec, renderer registry, scheme version, or format migration mapping exists — and the architecture argues that building one would violate identity immutability.
- **Evidence.** Searched `id_codec`, `IdentityCodec`, `render_identity`, `identity_scheme`, `scheme_version`, `id_format_version`, `format_id`. The only hit is `platform/universal_pipeline/identity.py:217-219`, a single hard-coded rule for a separate scheme. No identity carries a scheme version; `UCKO_URN_PREFIX` is a bare literal at `identity.py:39`. The foreclosure is explicit — `engine/uckp/alignment.py:33-36`: *"**It does not re-mint anything.** … **Any derivation that reshaped the identifier would be a re-mint wearing a projection's clothes**, and Article 5 says an identity never changes."*
- **Impact.** The absence is a reasoned decision, not an oversight — which raises the closure cost from "build a codec" to "resolve a constitutional conflict between Article 5 immutability and CMG-000001 XXXI.4 width-neutrality."
- **Note on architectural capacity.** The system demonstrably knows how to build an open extension point: `engine/registry/universal/identity.py:167-206` provides `register_kind(kind, code)`, documented as *"Admit a future identifier kind. This is the **only** extension mechanism."* There is deliberately no equivalent on the *format* axis. The **kind** axis is open; the **representation** axis is closed.
- **Classification.** **NOT YET ASSIMILATED.**
- **Dependency.** IDF-01, IDF-07.
- **Closure condition.** A determination reconciling Article 5 immutability with XXXI.4 width-neutrality. `GOVERNED-EVOLUTION-STATE-DETERMINATION.md:183` names exactly this as unbuilt: F-5 *"needs a representation-migration determination"*.

### 5.5 IDF-09 — Four incompatible namespace alphabets

- **Observation.** Four instruments declare four different, mutually contradictory character sets for an identity segment.
- **Evidence.**

  | Instrument | Rule | Verified at |
  |---|---|---|
  | `engine/kernel/identity.py` | **any Unicode**; only non-empty + no whitespace. *"The kernel deliberately does NOT constrain the alphabet to a finite script or language (Universal Language independence)"* | `:39-45`, `normalize_segment` `:53-64` |
  | `engine/registry/universal/identity.py` | lowercase ASCII, **no underscore** — `^[a-z0-9]+(?:-[a-z0-9]+)*(?:\.[a-z0-9]+…)*$` | `:38-40` |
  | `engine/uckp/identity.py` | lowercase **plus underscore**, capped at 63/191 chars — `^[a-z0-9][a-z0-9._-]{0,62}$` | `:46-47` |
  | CMG-000001 XXXII.6 | *"ASCII uppercase alphanumerics and hyphen only"* | constitution |
- **Impact.** `ucos_platform` is a valid UCKP namespace and an invalid registry namespace. The kernel's declared Unicode openness directly contradicts XXXII.6. Nothing reconciles them: the *hashing* primitive was consolidated (`kernel/identity.py:22-24` and `registry/universal/identity.py:28-30` both note *"one primitive, two names, so the rename never became a fork"*), the *alphabet* was not.
- **Classification.** **PARTIALLY ASSIMILATED** — one alphabet (the kernel's) correctly treats script as representation; three do not.
- **Dependency.** IDF-01.
- **Closure condition.** One declared alphabet authority, or an explicit declaration that the four govern disjoint populations.

### 5.6 The one place the separation is done correctly

`engine/kernel/identity.py:68-77`, `_slug`:

> *"The slug is purely cosmetic — uniqueness is guaranteed by the digest — so it may be **any data-derived rendering**. … a meta-type that renders empty (e.g. a purely symbolic script) falls back to `X` so the identifier shape stays uniform."*

Unicode semantics survive in the digest; ASCII survives only in the projection. **This is exactly the pattern the repository plane lacks** — and it proves the architecture is capable of the separation it has not generalised. In the repository plane the digits *are* the identity, because there is no digest and no value object beneath the string.

### 5.7 IDF-10 — A mutable fact is embedded in an identity, contra XXXI.5

- **Observation.** `data/entity.py:260` composes an identity from an entity's **name**.
- **Evidence.** `return f"{ENTITY_ID_PREFIX}-{self.name}-{self.structure_digest[:16]}"`. XXXI.5: *"Encoding phase, kind, status, owner, or version into an identifier couples identity to mutable fact and IS PROHIBITED."*
- **Impact.** Renaming the entity changes its identity — a direct loss of identity continuity, and the failure mode the principle exists to prevent. This shape also matches neither the six-digit pattern nor the registry's 12-hex pattern, so it is a fourteenth unreconciled surface. The same tension applies more broadly to the 58 prefixes, most of which encode *kind* (`UCOS-ENTITY`, `UCOS-WORKFLOW`, `UCOS-INFRA-NETWORK`, …); XXXI.1 permits a `<SUBSERIES>` token, so whether these violate XXXI.5 or are permitted subseries is **genuinely ambiguous and reserved to the owner**.
- **Classification.** **NOT YET ASSIMILATED** for the name-embedding case (unambiguous); **UNKNOWN** for the kind-encoding prefixes pending owner adjudication of XXXI.1 vs XXXI.5.
- **Dependency.** IDF-01.
- **Closure condition.** Owner adjudication of the XXXI.1/XXXI.5 boundary, then measurement of the 58-prefix population against it.

---

## 6. Universal Identity Capability Model

The directive's eight identity obligations, measured. This table is the core determination.

| Obligation | Located representation | Status | Evidence |
|---|---|---|---|
| **Authority** | `engine/uckp/identity.py` declared SUPREME | **NOT YET ASSIMILATED** | IDF-01…IDF-05: model self-contradictory, 9 of 13 shapes undeclared, no competent ratifier |
| **Uniqueness** | pure minting + registry refusal of duplicates (`engine/ceu/existence.py:340`); `DuplicateHomeError` both directions in UKIP | **PARTIALLY ASSIMILATED** | Real per store. No cross-store view; asserted over a population not proven to be the population (IDF-04) |
| **Resolution** | `ExistenceRegistry.resolve` (`existence.py:417-425`), `UniversalIdentity.parse` (`identity.py:95-107`) | **PARTIALLY ASSIMILATED** | Genuine mint↔parse inverse for shapes 1–2. **No resolver spans prefixes; no historical resolution (IDF-13)** |
| **Context** | none — identity is context-free **by design** | **NOT YET ASSIMILATED as a capability** | §8. Deliberate and defensible; the *gap* is the unwired facet, not the purity |
| **Lineage** | `engine/nucleus/lineage.py` `LineageLedger`; `master_plan.py:481-500` | **PARTIALLY ASSIMILATED** | In-memory only, never persisted (F-2). Silent truncation at depth 64. Completeness verification **ABSENT** |
| **Relationship** | `engine/nucleus/model.py:436-443` mints relationship identity through the one authority | **ASSIMILATED (within its plane)** | Tested at `engine/tests/nucleus/test_identity_convergence.py:151-168`. No cascade on identity change (IDF-15) |
| **Evolution history** | `ExistenceRegistry` supersession: list-based, appending, round-trippable | **ASSIMILATED (within the CEU plane)** | §9.1 — REQ-02 verified **STALE**; the fix is implemented |
| **Validity** | `verify()`/`require_intact()`/`require_unchanged()`; `is_well_formed` (`registry/universal/identity.py:303-309`) | **PARTIALLY ASSIMILATED** | Strong per shape. But validity is defined *as format conformance* (IDF-07), which is the defect |

**Determination for §6: the capability model exists in fragments with genuinely strong semantics inside each fragment, and no unifying capability across them.** Two obligations are met within a bounded plane, four are partial, two are unmet.

---

## 7. Infinite Expansion Compatibility

| Axis | Supported without redesign? | Evidence |
|---|---|---|
| **Unlimited entities** | **NO — bounded at 10⁶ per category** | `alignment.py:89` refuses the 1,000,000th identifier in any category; mint is unbounded. Headroom currently 99.74%; largest family `EXDOC` at 2,621. A **latent** bound, not an active one |
| **Unlimited kinds** | **YES** | `register_kind` (`registry/universal/identity.py:167-206`), *"the **only** extension mechanism"*, append-only |
| **Unlimited realities** | **N/A to identity** | Identity is reality-invariant by design (§8). `RegistryKind` includes `REALITY`, `UNIVERSE`, `CIVILIZATION` as *identifiable kinds*, so realities can be identified; identities do not vary by reality |
| **Unlimited dimensions** | **UNKNOWN** | No dimensional model exists anywhere in code (measured: `multiverse\|multi-reality\|multi_reality\|parallel possibilit` → **0 matches** across all `*.py`). The question is not yet answerable |
| **Unlimited temporal contexts** | **PARTIAL** | Identity is clock-free, which is the right property. But `id-ledger.json.first_seen` is hardcoded Earth UTC ISO-8601 — `00-MASTER/UISD-000001/uisd-declaration.json:287` records it as *"the original gap G1 … deliberately uncorrected"*; migration is F-5 |
| **Unlimited spatial contexts** | **YES for identity** | No mint takes a location. `engine/uckp/persistence.py:489` region default remediated to `None` (ADR-0012) |
| **Unknown future entities** | **YES** | `ExistenceRegistry.declare_form` admits a novel form as data; `engine/tests/ceu/test_existence.py:102-106` `test_a_future_form_needs_no_code_change` registers form `"dream"` and asserts the identity mints |
| **Unknown future existence models** | **PARTIAL** | Forms are open; the *identifier shape* they mint into is not (IDF-06, IDF-07) |
| **Unlimited representations** | **NO** | IDF-07, IDF-08. This is the directive's core claim and it fails |

### IDF-11 — The identifier space is bounded at 10⁶ per category by a regex quantifier

- **Observation.** A finite population ceiling exists, created by a formatting constraint rather than by any declared bound.
- **Evidence.** `alignment.py:89` + measured overflow at `…ADMISSION-READINESS-DETERMINATION.md:387-397`. No instrument declares 10⁶.
- **Impact.** Latent, not active. Current largest family occupies 0.26% of its space. But it is a genuine finite assumption inside a system whose CR-INF-009 declares *"architecturally expandable without predefined upper limits"* — and CR-INF-009 has **no gate and no test** (`adr/0022-uiep-001-universal-infinite-evolution-principle.md:61`: *"No gate currently checks conformance to this statement, and none is created by this document."*).
- **Classification.** **PARTIALLY ASSIMILATED** — the bound is now disclosed; it is not removed and not gated.
- **Dependency.** IDF-07, IDF-08.
- **Closure condition.** Either implement XXXI.4 ordinal comparison (which dissolves the bound), or declare the bound constitutionally with a width-per-namespace register per XXXI.2.

### IDF-12 — The openness that exists is on the kind axis, not the identity axis

- **Observation.** The system's proven extension mechanisms admit new *kinds of thing*, never new *ways of naming things*.
- **Evidence.** `register_kind` (kinds), `declare_form` (forms), `ContextTaxonomy.extend` (context kinds) — all open, all tested. No format extension point (IDF-08).
- **Impact.** Infinite expansion of *what exists* is supported. Infinite expansion of *how existence is denoted* is not. The directive's statement concerns the latter.
- **Classification.** **PARTIALLY ASSIMILATED.**
- **Dependency.** IDF-08.
- **Closure condition.** A representation extension point of equivalent rigour to `register_kind`.

---

## 8. Context-Aware Identity Analysis

**Determination: identity is context-free by deliberate design, and this is a defensible architectural choice — not the gap. The gap is that the context slots reserved on the identity record are wired to nothing.**

### 8.1 The purity is explicit, reasoned, and tested

`engine/uckp/identity.py` module docstring:

> *"**Time-independent** — no clock is read. Two processes on different planets in different centuries mint the same identity for the same name, which is what makes cross-era replay possible at all."*

`mint` (`:73-90`) takes exactly two inputs. Asserted at `engine/tests/uckp/test_layer_zero.py:136-139`:

```python
def test_identity_reads_no_clock_and_no_location():
    identity = UniversalIdentity.mint("ucos", "THING-1")
    record = identity.to_dict()
    assert set(record) == {"namespace", "local_name", "urn", "uuid"}
```

A test named *"reads no clock and no location"* that asserts the field set contains no context. And `:184` asserts two independent mints of the same name are equal — the test-level proof of frame-invariance.

**Correction to a premise in the directive's framing:** there is **no `identity` axis** in the context derivation chain. `AXIS_DERIVATION` (`engine/context/location.py:93-116`) holds 19 axes — existence, reality, observer, civilization, universe, location, spatial, temporal, jurisdiction, governance, calendar, time-standard, language, units, currency, regulation, tax, policy, execution-context. Verified: grep for `"identity"` within that block returns **0**.

### 8.2 What the Reality Context Principle actually governs

`engine/context/location.py:77-87`:

> *"The Universal Reality Context Principle: no value may be **interpreted** — measured, validated, governed, certified or executed against — until these five resolve."* (`existence`, `reality`, `observer`, `spatial`, `temporal`)

Minting an identity is **not** in that list. The principle gates *interpretation*, not *identification*. Its executable form `require_reality_context` (`:710-738`) takes a `LocationResolution`, never an identity, and has exactly **one non-test caller** in the repository: `engine/nucleus/context.py:121`.

### 8.3 The correct join point is the record, and it works

`engine/nucleus/context.py`, `context_stage_function` docstring:

> *"Every stage outcome carries the context fingerprint, which means the execution digest is a function of the reality the run happened in: the same subject run in two frames produces two different — and both honest — records."*

**One identity, many frame-qualified records.** This is a coherent and well-reasoned answer to the directive's Earth-only/Mars-only/single-reality concern: the architecture does not assume a single reality — it asserts that identity is the thing that must *not* vary across realities, and pushes reality-qualification into the record. The 14-frame catalog (`engine/context/catalog/reference-frames.json`, 2 realities, 2 civilizations, zero Earth/Mars literals) is the substrate proving the frames are expressible.

### IDF-13 — The six context facets on the identity record are hardcoded constants

- **Observation.** The UCKO reserves context facets and fills them with universal string literals.
- **Evidence.** `engine/uckp/facets.py:58` declares `Facet.EXISTENCE_CONTEXT`; `:122` asks *"From whose vantage point is it described?"*. `engine/uckp/ucko.py:90-96`:

  ```python
  _DEFAULT_OBSERVER = ContextBinding("observer", "constitutional-observer")
  _DEFAULT_EXISTENCE = ContextBinding("existence", "declared-and-registered")
  ```

  Identity is minted independently at `ucko.py:213`. **No code path connects these facets to `engine/context/location.py` resolutions.**
- **Impact.** The facet asks "from whose vantage point?" and **every object in the repository answers with the same constant**. The context capability and the identity record are adjacent and unwired. This is the single most concrete context gap.
- **Classification.** **NOT YET ASSIMILATED.**
- **Dependency.** None technical — both sides exist.
- **Closure condition.** A binding from `LocationResolution` into the six context facets, with a test that two frames yield two different facet populations for one identity. No such test exists (searched `engine/tests/`).

### IDF-14 — No gate or test asserts any context property of identity

- **Observation.** The one dedicated identity gate tests authority conformance, never context.
- **Evidence.** `.github/workflows/uis-gate.yml` ("UIS-001 Identity Conformance Gate (G-24)") steps are: zero-enumeration proof · self-determinism · Knowledge Once · `--check-no-identity-minting` · fail-closed gate. No step mentions reality, observer, frame or civilization. No test asserts an identity carries a frame, that one name in two frames yields two identities, or that an identity resolves differently per observer — **the tests assert the opposite** (§8.1).
- **Impact.** Whatever context posture is chosen, it is currently unguarded by measurement.
- **Classification.** **NOT YET ASSIMILATED.**
- **Dependency.** IDF-13.
- **Closure condition.** A gate asserting the chosen posture (invariance or qualification) so the property cannot drift silently.

---

## 9. Evolution and Lineage Analysis

### 9.1 Supersession — ASSIMILATED within the CEU plane; two cited gap-register entries are STALE

**Correction to the current gap register.** `UCOS-OMEGA-INFINITY-IMPLEMENTATION-GAP-REGISTER.md:13-19` (REQ-02) states supersession history is *"not field-level reconstructible"* — `"_supersessions: dict[str, dict]` — one mutable slot per subject"*. **The prescribed fix is implemented.** `engine/ceu/existence.py:258`:

```python
self._supersessions: dict[str, list[dict[str, Any]]] = {}
```

`supersede()` (`:458-517`) appends and refuses to rewrite an active supersession. `resurrect()` (`:521-546`) appends a snapshot with the comment *"A new snapshot, appended — not a mutation of `latest`, which stays exactly as supersede() left it, forever readable at its own position in the history."* The accessor REQ-02 requested exists at `:581-583` (`supersession_history`). `to_document()` (`:750-756`) emits the full per-subject history; `from_document()` (`:771-848`) reads it back with a lossless fallback for older single-row documents.

The semantics are strong — `supersede()` docstring `:461-476`:

> *"One call covers every construct and every shape of change: **split** … **merge** … **transform** … **deprecate**. Nothing is deleted — the unit stays registered and stays resolvable, because units already referring to it keep a readable lineage. What ends is its *admissibility* for new registrations."*

**REQ-14 is likewise stale**: `engine/knowledge/store.py:297-350` now archives prior versions to `HISTORY_FILE` before overwrite.

- **Classification: ASSIMILATED** (CEU plane). **Closure condition for the register:** correct REQ-02 and REQ-14 to reflect code. Reserved to their owner; not performed here.

### IDF-15 — Historical resolution does not exist; a rename mints a new identity with no back-pointer

- **Observation.** The persisted repository identity plane is keyed on filesystem path. A rename produces a **new** identity and no forward or backward link.
- **Evidence.** `00-BOOK/tools/ukb.py:876-914` — `allocate()` looks up `ledger["by_path"].get(relpath)` and, on miss, mints. The ledger schema (`by_path`, `page_cursor`, `category_seq`, `discovered_volumes`, `volume_seq`, `by_execution`) has **no field able to express "this old identity is now that one"**. Searched `engine/` and `platform/` for `_aliases|alias_of|redirect|former_id|previous_id|renamed_from` → no historical redirection anywhere. The only alias resolution located is *spatial, not temporal*: `engine/knowledge/ukip/registry.py:539-561` `reference_map()` maps alias→canonical for currently-existing records and **withdraws** the bare form on collision.
- **Aggravating evidence.** The system **drops** rather than redirects stale identity. `ukb.py:347-366`: *"the append-only snapshot history may retain the UID of a path that is no longer a registered repository artifact … Such UIDs are NOT emitted as change-event subjects, because a change event must bind to a real, currently-registered graph node — never a dangling endpoint."* The old identity's history is preserved but becomes unreachable from the current graph.
- **Impact.** Identity continuity across representation or location change is **not** preserved in the persisted plane. This directly negates the directive's requirement.
- **Classification.** **NOT YET ASSIMILATED.**
- **Dependency.** IDF-07, IDF-08.
- **Closure condition.** A resolution table mapping superseded identifiers forward. Blocked by the append-only constraint, which is why `GOVERNED-EVOLUTION-STATE-DETERMINATION.md:183` classes it as F-5 *"needs a representation-migration determination"*.

### IDF-16 — Lineage is derived, in-memory, silently truncated, and completeness-unverified

- **Observation.** Four independent limitations on the lineage obligation.
- **Evidence.**
  - Not persisted — `GOVERNED-EVOLUTION-STATE-DETERMINATION.md:180-182`: `F-2` *"Persist `engine/nucleus/lineage.py::LineageLedger`"*, `F-3` `EvolutionLedger`, `F-4` certification audit ledger. `SCOPE-B-WORKSTREAM-3-…-IMPLEMENTATION-REPORT.md:34`: *"**Nothing persisted. No artifact created, no producer home added, no registry entry.**"*
  - Silent truncation — `platform/universal_master_plan/master_plan.py:91-93` `MAX_LINEAGE_DEPTH = 64`; `lineage_of` (`:481-500`) `break`s at the cap and returns a plain tuple, so **a caller cannot distinguish a complete chain from a truncated one**. Contrast `ExistenceRegistry.ancestry()` (`existence.py:585-604`), which *raises* `"cycle in the specialization graph"` — the correct discipline, applied in the other module.
  - Completeness unverified — `SCOPE-B-WORKSTREAM-3-…-ARCHITECTURE-DETERMINATION.md:181`: *"Lineage completeness | **ABSENT** | Nothing asserts every node reaches a root … **New coverage required.**"*
  - A real divergence occurred — `F-1-LINEAGE-DIVERGENCE-DISPOSITION-DETERMINATION.md:12-16`: 2 of 1,234 `Parent` edges assert an ancestry `artifacts.json` does not declare; *"**The divergence is real, and it is not residue.** It is produced by a **live rule** in the current generator."* Now gated at `ukb.py:1841-1870`.
- **Impact.** Lineage is a best-effort projection, not a preserved property. Deliberate per `SCOPE-B-IDENTITY-CONTAINMENT-DETERMINATION.md:82`: *"**DETERMINED: lineage shall be composed as a derived projection. No lineage database, no lineage authority, no lineage store shall be created.**"*
- **Classification.** **PARTIALLY ASSIMILATED.**
- **Dependency.** IDF-05 (persistence would create new canonical state, requiring an authority).
- **Closure condition.** Either persist (F-2, needs an authority) or add completeness verification plus a truncation signal to the derived projection (needs neither). The second is available now.

### IDF-17 — No per-identity version; migration capability determined not to exist

- **Observation.** Document/scheme versions exist; identity versions do not. Migration is documented as absent.
- **Evidence.** `engine/uckp/evolution.py:107-110` `LEDGER_SCHEMA`; `existence.py:734-735` `"version": "1.0.0"` — both version the **document format**. No `ExistenceUnit` or ledger entry carries an identity version. `UNIVERSAL-IDENTITY-MIGRATION-DETERMINATION.md:6`: *"**Authority:** NONE (DERIVED TRUTH). Determines disposition; **performs no migration**."* `IDENTITY-CORRECTION-EXECUTION-REPORT.md:29-35` — the one executed "identity correction" was five filesystem renames that deliberately avoided the ledger: *"**Result:** No output — **confirmed no unauthorized IDs in ledger**. **Ledger entry count:** 6,178 entries (unchanged)"*. That is evidence migration was **avoided**, not that it is possible.
- **Nuance worth recording against F-3.** The `EvolutionLedger` is not persisted *as canonical governed state*, but a byte-deterministic projection **is** written and **is** read back into a live ledger: `engine/uaue/gate.py:676-687` writes `canonical_json(report.projection)`; `engine/uaue/history.py:191-204` `rehydrate_history` re-validates on read. Classified *"EXCLUDED — projection"* at `GOVERNED-EVOLUTION-STATE-DETERMINATION.md:161`. So evolution history is durable in practice and non-canonical by determination.
- **Classification.** **NOT YET ASSIMILATED.**
- **Dependency.** IDF-08.
- **Closure condition.** The F-5 representation-migration determination.

### IDF-18 — Referential integrity is enforced by refusal; there is no cascade on identity change

- **Observation.** Edges are validated against the current identity set; nothing rewrites them when an identity changes.
- **Evidence.** Enforcement exists — `00-BOOK/tools/ukb.py:1832-1839` (unknown parent/dep → problem), `:1841-1870` (F-1 lineage gate, also refusing multiple parents), `:1873+` (relation-type vocabulary). No cascade or edge-rewrite mechanism located anywhere. Continuity in the CEU plane is achieved by **non-deletion**, not pointer maintenance (`supersede()` docstring). One conservative projection-boundary rewrite exists: `engine/knowledge/ukip/registry.py:220-239` `resolved_relations(..., preserve=...)`, whose docstring explains that links into artifacts UKIP does not own *"survive the projection instead of being rewritten to a knowledge identifier that would no longer name the same thing."*
- **Impact.** Within CEU, relationships survive because the target is never removed — sound. Across the repository plane, a rename orphans every edge pointing at the old id, and the change-event deriver drops rather than redirects.
- **Classification.** **PARTIALLY ASSIMILATED.**
- **Dependency.** IDF-15.
- **Closure condition.** Either a resolution table (IDF-15) or an explicit determination that representation change is prohibited rather than unsupported. The two are currently conflated.

---

## 10. Contradiction Register

Every entry is a pair of **live, located, mutually inconsistent** claims. None is resolved by this document.

| # | Claim A | Claim B | Status |
|---|---|---|---|
| C-01 | `identity_authority_resolution`: one SUPREME authority; all else a projection | `identity_namespace_resolution`: `MULTIPLE_INDEPENDENT_BOUNDED_NAMESPACES`, siblings, `relationship_to_sibling_namespace: NONE` | **OPEN** — same file, neither amended |
| C-02 | CMG-000001 XXXI.4: zero-padding is *"a presentation choice"*; XXXI.2 prohibits a global width | `alignment.py:307-308` raises on ≠6 digits; `test_alignment.py:97-103` ratifies width-3 refusal | **OPEN** — disposition chosen as disclosure |
| C-03 | `alignment.py:89` refuses 7-digit ids | `engine/graph/validation.py:36-39` accepts `UCOS-[A-Z0-9]+-\d+` | **OPEN** — nothing reconciles |
| C-04 | Declared authority = `engine/uckp/identity.py` | `IDENTITY-ASSIMILATION-DETERMINATION.md:28` and `engine/ceu/existence.py` comments name `deterministic_id` | **OPEN** |
| C-05 | Declared `id_shape` = `^UCOS-[A-Z0-9]+-[0-9]{6}$` | `deterministic_id` emits `UCOS-<CODE>-<12hex>`, which does not match | **CLOSED AS OBSERVATION** (`B-02…DISCOVERY.md:71-76`), shape conflict unresolved |
| C-06 | Kernel: *"deliberately does NOT constrain the alphabet to a finite script or language"* | CMG-000001 XXXII.6: *"ASCII uppercase alphanumerics and hyphen only"*; registry: lowercase ASCII; UCKP: lowercase + `_`, capped | **OPEN** — four rules |
| C-07 | XXXI.5: encoding kind/version into an identifier *"IS PROHIBITED"* | 58 prefix values encode kind; `data/entity.py:260` embeds a mutable **name** | **OPEN** — XXXI.1 subseries allowance makes the boundary ambiguous |
| C-08 | Article 5 / `alignment.py:33-36`: an identity once minted never changes; reshaping would be *"a re-mint wearing a projection's clothes"* | XXXI.3: *"width extension by left-padding SHALL be permitted without renumbering"* | **OPEN** — the deepest conflict; blocks IDF-07/08/15/17 |
| C-09 | `FG-18`: every capability resolves to exactly one owning Nucleus | 9 capability namespaces unregistered in any surface `FG-18` reads | **OPEN** (`CANONICAL-AUTHORITY-RESOLUTION-DETERMINATION.md:93-94`) |
| C-10 | Facet question: *"From whose vantage point is it described?"* | Every object answers `"constitutional-observer"` (`ucko.py:95`) | **OPEN** |
| C-11 | CR-INF-009: expandable *"without predefined upper limits"* | 10⁶ per-category ceiling from a regex quantifier | **OPEN**; CR-INF-009 has no gate (`adr/0022:61`) |
| C-12 | `second_authority_test` enforces one authority | Test detects only `category_seq`; 9 shapes advance no counter | **OPEN** |

**C-08 is the load-bearing contradiction.** Until immutability and width-neutrality are reconciled by an authority, IDF-07, IDF-08, IDF-15 and IDF-17 cannot close, and the directive's final statement cannot become true.

---

## 11. Existing Capability Reuse Analysis

Per the repository's own governing rule — `UNIVERSAL-IDENTITY-DICTIONARY-DETERMINATION.md:24`: *"The operative rule for any extension: **derive, never count.**"* — this section records what **already exists** and must be reused rather than rebuilt.

| Required capability | Already exists | Reuse verdict |
|---|---|---|
| Pure, deterministic minting | `engine/uckp/identity.py:73`; `registry/universal/identity.py:257`; `engine/kernel/identity.py:87` | **REUSE.** Three sound implementations. The gap is unification, not capability |
| Canonical hashing primitive | `engine/uckp/canonical.py` — `canonical_json`/`content_hash`, imported by kernel and registry with matching comments (*"one primitive, two names, so the rename never became a fork"*) | **REUSE — already consolidated.** Precedent proving cross-module unification is achievable here |
| Open kind admission | `register_kind` (`registry/universal/identity.py:167-206`), *"the **only** extension mechanism"* | **REUSE as the template** for the missing representation extension point (IDF-08) |
| Representation-as-cosmetic pattern | `engine/kernel/identity.py:68-77` `_slug` — *"purely cosmetic — uniqueness is guaranteed by the digest — so it may be **any data-derived rendering**"* | **REUSE as the template** for IDF-07. The pattern is already in the codebase and simply not generalised |
| Supersession with split/merge/transform/deprecate | `engine/ceu/existence.py:458-546` + `supersession_history:581` | **REUSE.** Complete and round-trippable |
| Mint↔parse inverse | `urn_for`/`parse` (`identity.py:50-107`) | **REUSE.** Proves the inverse is buildable; needs generalising across shapes |
| Fail-closed re-derivation | `IdentifierDictionary.verify()` re-mints every entry; `from_dict` refuses a declared value contradicting the mint | **REUSE.** The correct validity discipline |
| Frame-qualified records | `engine/nucleus/context.py` `context_fingerprint` | **REUSE** to close IDF-13. Both sides exist; only the wire is missing |
| Bounded-open extension governance | `ContextTaxonomy.extend` + `ContextOntology.extend` (runtime, immutable, tested at `engine/tests/context/test_req_28_extensibility.py`) | **REUSE as the governance template** for representation openness |
| Cycle-refusing graph walk | `ExistenceRegistry.ancestry()` raises on cycle | **REUSE** to fix `master_plan.py`'s silent truncation (IDF-16) |
| Disclosure register for closed sets | `00-MASTER/UISD-000001/uisd-declaration.json` `closed_enumeration_disclosures` (ISD-CE-01…11) + gate | **REUSE.** The 58-prefix population and the 6-digit width are undisclosed closures that this mechanism already exists to hold |

**Determination for §11: no new engine is required to close the located gaps.** Every mechanism needed — pure minting, consolidated hashing, open admission, cosmetic rendering, supersession, parse inverses, frame fingerprints, closure disclosure — already exists and is tested. What is missing is (a) a binding layer across the thirteen shapes, and (b) an authority competent to declare it. This mirrors the conclusion of `UCOS-OMEGA-INFINITY-UNIVERSAL-ASSIMILATION-FABRIC-DETERMINATION.md`: *"BINDING LAYER MISSING, ENGINES SUFFICIENT."*

Four things are **refused** by standing determinations and must not be built: a new identity universe, a second identity authority, a third dictionary, and a 14-component identity stack (`UNIVERSAL-IDENTITY-UNIVERSE-DETERMINATION.md` §6, refusals restated as standing at `UNIVERSAL-IDENTITY-DICTIONARY-DETERMINATION.md:14-24`).

---

## 12. Remaining Gaps

Consolidated. Every closure condition is stated; none is executed.

| # | Gap | Class | Blocked by |
|---|---|---|---|
| IDF-01 | Two contradictory identity models live in one file | **NOT YET ASSIMILATED** | IDF-05 |
| IDF-02 | Second-authority test detects only counters | **PARTIALLY ASSIMILATED** | IDF-01 |
| IDF-03 | Declared vs operative authority differ | **NOT YET ASSIMILATED** | IDF-01 |
| IDF-04 | 9 capability namespaces, no register | **NOT YET ASSIMILATED** | IDF-01 |
| IDF-05 | No competent ratifying authority | **NOT YET ASSIMILATED** | external |
| IDF-06 | 6-digit vs `\d+` — corpus disagrees on 7 digits | **NOT YET ASSIMILATED** | IDF-01 |
| IDF-07 | Representation change ≡ tampering (uuid5 over rendered string) | **NOT YET ASSIMILATED** | — (intrinsic) |
| IDF-08 | No codec/renderer/scheme-version; foreclosed by Article 5 reading | **NOT YET ASSIMILATED** | C-08 |
| IDF-09 | Four incompatible namespace alphabets | **PARTIALLY ASSIMILATED** | IDF-01 |
| IDF-10 | Mutable name embedded in identity (`data/entity.py:260`) | **NOT YET ASSIMILATED** / kind-prefixes **UNKNOWN** | C-07 |
| IDF-11 | 10⁶ per-category ceiling from a regex quantifier | **PARTIALLY ASSIMILATED** (disclosed) | IDF-07/08 |
| IDF-12 | Openness on kind axis only, not representation axis | **PARTIALLY ASSIMILATED** | IDF-08 |
| IDF-13 | Six context facets hardcoded; unwired to context engine | **NOT YET ASSIMILATED** | — (both sides exist) |
| IDF-14 | No gate/test asserts any context property of identity | **NOT YET ASSIMILATED** | IDF-13 |
| IDF-15 | No historical resolution; rename mints a new id, no back-pointer | **NOT YET ASSIMILATED** | IDF-07/08 |
| IDF-16 | Lineage in-memory, silently truncated at 64, completeness ABSENT | **PARTIALLY ASSIMILATED** | IDF-05 (persist) / none (verify) |
| IDF-17 | No per-identity version; migration determined absent | **NOT YET ASSIMILATED** | IDF-08 |
| IDF-18 | No cascade on identity change | **PARTIALLY ASSIMILATED** | IDF-15 |
| IDF-19 | 58 prefixes + 6-digit width are undisclosed closed sets | **NOT YET ASSIMILATED** | — (UISD register exists) |
| IDF-20 | Security identity (`Principal`) fully disjoint from universal identity | **NOT YET ASSIMILATED** | IDF-01 |
| IDF-21 | Assimilation pipeline mints no identity (0 identity references) | **NOT YET ASSIMILATED** | IDF-01 |
| IDF-22 | REQ-02 / REQ-14 in the gap register are stale vs code | **ASSIMILATED in code**, register uncorrected | register owner |

**Gaps closable without a new authority (measurement-only, available now):** IDF-13, IDF-14, IDF-16 (verification half), IDF-19. Recorded for the owner; **not executed here.**

---

## 13. Implementation Dependency Impact

Dependency structure of the located gaps. No sequence, phase, wave or roadmap is created — this records what depends on what, as evidence.

```
IDF-05  no competent ratifier  (external — root constraint)
   └── IDF-01  contradictory identity models
         ├── IDF-02  counter-only detection
         ├── IDF-03  declared vs operative authority
         ├── IDF-04  nine capability namespaces
         ├── IDF-06  6-digit vs \d+
         ├── IDF-09  four alphabets
         ├── IDF-20  security identity disjoint
         └── IDF-21  assimilation mints nothing

C-08  Article 5 immutability  vs  XXXI.4 width-neutrality   (root conflict)
   └── IDF-08  no representation extension point
         ├── IDF-11  10^6 ceiling
         ├── IDF-12  kind-axis openness only
         ├── IDF-15  no historical resolution
         │     └── IDF-18  no cascade
         └── IDF-17  no per-identity version / no migration

IDF-07  uuid5 over rendered string   (intrinsic, no upstream blocker)
   └── makes IDF-08 a semantic change, not an additive one

Independent of both roots (no authority required):
   IDF-13  wire context facets        IDF-14  context gate
   IDF-16b lineage completeness       IDF-19  disclose closed sets
   IDF-22  correct stale register entries
```

**Impact statements:**

1. **IDF-07 is the highest-leverage finding.** It has no upstream blocker and it is what converts IDF-08 from "add a codec" into "change what an identity *is*". Any representation-evolution work that does not address it will reproduce the defect.
2. **C-08 gates five gaps.** Until immutability and width-neutrality are reconciled, representation evolution, historical resolution, migration and versioning are all structurally unavailable.
3. **IDF-05 gates eight gaps** and is external to the repository. This is the reason `CANONICAL-AUTHORITY-RESOLUTION-DETERMINATION.md` closes at `ZERO RESOLVED`.
4. **Five gaps require no authority at all** and are measurement work against mechanisms that already exist (§11).
5. **No new engine is implied by any gap.** Consistent with §11 and with the fabric determination's *"engines sufficient"* conclusion.

---

## 14. Final Determination

### 14.1 The primary question

> Has UCOS Ω∞ evolved identity from a finite representation model into a universal identity capability model?

**Determination: PARTIALLY — and not on the axis the question is about.**

| Axis | Determination |
|---|---|
| Identity **semantics** (purity, determinism, storage/clock/path independence, supersession) | **PARTIALLY ASSIMILATED, and strong.** Minting is pure and total across the principal planes and is asserted by tests. Supersession is complete and round-trippable within CEU. This is genuine and it is the hard part |
| Identity **representation** | **NOT YET ASSIMILATED.** 13 shapes, 58 prefixes, 4 alphabets, one CI-enforced 6-digit regex, no codec, no scheme version, no migration — and the abstraction is argued to be prohibited |
| **Separation** of the two | **NOT YET ASSIMILATED.** The rendered string is a stored invariant and the UUID is computed over it. Representation change is indistinguishable from tampering |
| **Infinite/unlimited evolution** | **PARTIALLY ASSIMILATED.** Open on the *kind* axis (`register_kind`, `declare_form`, `ContextTaxonomy.extend` — all tested). Closed on the *representation* axis. Population ceiling of 10⁶ per category from a regex quantifier |
| **One universal authority** | **NOT YET ASSIMILATED.** Declared and simultaneously un-declared in the same file; enforcement test blind to 9 of 13 shapes; no competent ratifier |

### 14.2 The final architectural test

> *"UCOS Ω∞ does not have an identity format. UCOS Ω∞ has an identity capability that can generate, resolve, evolve, and preserve identity across unlimited future representations."*

**DISPROVED on repository evidence.** Clause by clause:

| Clause | Verdict | Decisive evidence |
|---|---|---|
| "does not have an identity format" | **FALSE** | 13 distinct shapes; 58 prefix values across 53 files; `REPOSITORY_ID_PATTERN` raises on ≠6 digits at `alignment.py:307-308`; `test_alignment.py:97-103` asserts width-3 must raise. A format that raises is a format |
| "can **generate** identity" | **TRUE** | `UniversalIdentity.mint`, `deterministic_id`, `engine/kernel/identity.py:87` — pure, total, tested. The strongest clause |
| "can **resolve** identity" | **PARTIALLY TRUE** | `resolve()`/`parse()` work within shapes 1–2. No resolver spans prefixes; no historical resolution (IDF-15) |
| "can **evolve** identity" | **PARTIALLY TRUE** | Supersession is complete within CEU (split/merge/transform/deprecate, appending, round-trippable). No per-identity version; migration determined absent (IDF-17) |
| "can **preserve** identity" | **FALSE in the persisted plane** | Path-keyed `allocate()` mints a new id on rename with no back-pointer; `derive_change_events` **drops** stale subjects rather than redirecting (`ukb.py:347-366`). `data/entity.py:260` embeds a mutable name in the identity |
| "across **unlimited future representations**" | **FALSE** | No codec, no renderer registry, no scheme version, no migration mapping. `alignment.py:33-36` argues that building one would be *"a re-mint wearing a projection's clothes"*. `uuid5` over the rendered string makes representation change fail `verify()` |

**Two of six clauses hold; two hold partially; two fail — including both clauses the statement's novelty depends on.**

### 14.3 What the evidence does support

A narrower statement that the evidence **does** sustain, offered as a measurement rather than a claim:

> *UCOS Ω∞ has a strong, tested, technology-independent identity **semantics** — pure, deterministic, clock-free, path-free minting with complete supersession within its existence plane. It has not separated that semantics from its representations, does not have one authority over them, and cannot yet evolve, migrate, or historically resolve an identifier across a change of representation.*

### 14.4 Standing

| Item | State |
|---|---|
| Determination | **COMPLETE** |
| Gaps recorded | **22** (`IDF-01`…`IDF-22`) |
| Contradictions recorded | **12** (`C-01`…`C-12`) |
| Gaps resolved by this document | **ZERO** |
| New engines determined necessary | **ZERO** — binding layer missing, mechanisms sufficient (§11) |
| Code modified | **NONE** |
| Identifier formats changed | **NONE** |
| Validators updated | **NONE** |
| Identities created or migrated | **NONE** |
| Registries modified | **NONE** |
| Certification changed | **NONE** |
| Phases created | **NONE** |
| Closure claimed | **NONE.** Per IDF-05, no located authority is competent to ratify a resolution; every closure condition above terminates in an act outside this determination's mode |

**Two corrections this determination makes to standing repository records**, both recorded and neither executed:

1. `UCOS-OMEGA-INFINITY-IMPLEMENTATION-GAP-REGISTER.md` REQ-02 and REQ-14 are **stale**. The prescribed fixes are implemented at `engine/ceu/existence.py:258,458-546,581-583` and `engine/knowledge/store.py:297-350`. Correction reserved to the register's owner.
2. The framing premise that an `identity` axis exists in `engine/context/location.py`'s `AXIS_DERIVATION` is **incorrect** — verified 0 occurrences across the 19 declared axes. Identity is deliberately outside the context derivation chain, and §8 determines that this posture is defensible; the gap is the unwired facet (IDF-13), not the purity.

---

**END DETERMINATION — STOPPED AFTER DETERMINATION.**
