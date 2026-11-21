# UCOS Ω∞ · UNIVERSAL IDENTITY CONVERGENCE CLOSURE DETERMINATION

| Field | Value |
|---|---|
| ARTIFACT | UCOS-OMEGA-INFINITY-UNIVERSAL-IDENTITY-CONVERGENCE-CLOSURE-DETERMINATION |
| CLASS | DETERMINATION — closure architecture of record |
| VERSION | 1.0 |
| SCOPE | Convergence of all identity populations onto the existing Universal Identity Architecture; closure of blockers J1…J8 |
| PREDECESSOR | `UCOS-OMEGA-INFINITY-UNIVERSAL-IDENTITY-EVOLUTION-ARCHITECTURE-DETERMINATION.md` (architecture determined, 8 blockers open) |
| AUTHORITY | **NONE.** This determination mints no identity, allocates no identifier, declares no namespace, defines no grammar, opens no registry, legislates no lifecycle and certifies nothing. |
| LAW OWNERS | `02-MASTER/UCOS-Ω∞-ABSOLUTE-IDENTITY-FEDERATION-AND-CONTINUITY-CONSTITUTION.md` (AIF-L01…L24, A/G1…A/G14) · `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-AUTH-INF-001-…-CONSTITUTION.md` (CR-INF-001…012, IL-INF-01…08) |
| ARCHITECTURE OWNER | `07-ENGINEERING/UCOS-Ω∞-UNIVERSAL-IDENTITY-SYSTEM-MASTER-ARCHITECTURE.md` (ENG-001, UIL-01…UIL-20) |
| CONFORMANCE OWNER | `00-MASTER/UIS-001/` (`uis-declaration.json` · `uis_engine.py`) |
| SEAL | NOT SEALED — hand-authored determination, not engine-generated. No digest is asserted. |
| IMPLEMENTATION | NONE. No code, data, ledger, schema, registry or relationship record was created or modified. |

> **DISCLOSURE.** This determination creates nothing. Every construct it names — Identity Cell, Mint Epoch, Convergence Protocol — is a **name for a composition of mechanisms that already exist at the paths cited**, not a new mechanism. It opens no ledger, no registry, no namespace, no resolver and no authority. It proposes no compatibility layer, no migration table and no special case. Where this determination and a located instrument differ, **the located instrument governs**.

---

# PART 0 — CLOSURE IN ONE PAGE

## 0.1 The convergence theorem

The eight blockers are not eight defects. They are **one defect in eight places**: a population whose identity is *rendered* was allowed to be treated as a population whose identity is *recorded*.

The law already forbids exactly this, twice, in two independent constitutions:

- **CR-INF-005.1** — "Sequence numbers are **aliases**. Sequence numbers are **not** identity."
- **IL-INF-03** — "Every reference to identity SHALL resolve to the stable Universal ID, never to a mutable sequence alias."
- **AIF-L04** — the ordinal is "recorded at mint; **rendered**, never recomputed."
- **AIF-L02** — durable identity is "never content/order/path-derived."

Therefore: **`UEDGE-000013361` was never an identity. `UCOS-PLT-000032` was never an identity.** Both are P3 admission-ordinal *renders* over a P2 durable identity that the corpus has not yet written down. Convergence does not change any identity, because there is no identity in those strings to change.

This is the whole closure. It is stated once and applied eight times.

## 0.2 The Convergence Protocol

A *name* for the call sequence the located mechanisms already implement. Five steps, in order, per population. No step writes to a recorded identity value — which is why AIF-L17 is preserved by construction rather than by discipline.

| # | Step | What it writes | Located mechanism |
|---|---|---|---|
| 1 | **DECLARE** the cell | declaration data only (`identity_mechanisms[]`) | `00-MASTER/UIS-001/uis-declaration.json`; `register_kind` (`engine/registry/universal/identity.py:162-199`) |
| 2 | **ADOPT** history | a *new* record pointing at the existing render; render frozen verbatim | `DurableIdentity.adopt` / `IdentityRegistry.adopt` (`platform/foundation/durable_identity.py:158-182, 440-469`) |
| 3 | **MINT FORWARD** | new members only | `IdentityRegistry.mint` (prepare→commit, idempotent, `_guard_opaque`, `retire`-aware) |
| 4 | **MEASURE** | derived measurement, no writes to sources | `uis_engine.py` + `uis-declaration.json` `laws[]` / `validations[]` |
| 5 | **CERTIFY** | immutable attestation + recomputed status, distinct stores | `engine/certification/{contracts,ledger,closure}.py`; `ukbx.py::cmd_certify` |

**Invariant CP-1 (write-disjointness).** Step 1 writes declarations. Step 2 writes adoption records. Step 3 writes new members. Steps 4-5 write derived views. **No step has write access to an existing recorded identity value.** No renumbering, deletion or mutation is reachable from the protocol.

## 0.3 Closure disposition of J1…J8

| # | Blocker | Disposition | Closing mechanism (existing) | Residual |
|---|---|---|---|---|
| **J1** | Positional relationship identity | **DISSOLVED** — `UEDGE-` is a P3 alias by CR-INF-005; adopt the render frozen, mint P2 from the admission key `(from,to,type)` | `REL` kind (already registered) + `AdmissionKey` + `adopt()` | edge-population declaration is owner action |
| **J2** | Algorithm-naked persisted digests | **CONVERGED** — digests become `DigestSet{profile_id, [algorithm:value]}`; history interpreted through its Mint Epoch, never re-hashed | `Multihash` · `DigestSet` · `AlgorithmRegistry` · `CanonicalDigest` | ~130 producer sites are owned by their packages |
| **J3** | Three canonicalization profiles | **CONVERGED** — each existing profile is *registered as a versioned CCF profile*, not corrected | `CanonicalProfile` + `ProfileRegistry` (append-only `register()`) + `_probe_zero_duplication` | probe scope is `engine`/`platform` |
| **J4** | Four unlocated minting authorities | **CONVERGED** — declare the cell; register the code space; delegate the digest | `identity_mechanisms[]` + `register_kind` + `content_hash` + `_FORBIDDEN_MINTS` probe | `engine/`, `intelligence/` are outside UIS write scope |
| **J5** | Enumerative artifact grammar (3 compiled-in limits) | **DISSOLVED** — the grammar constrains a *render*, not an identity; CR-INF-002.4 makes width extensible append-only with no renumbering | grammar-by-pointer (`uis_engine.py:256-262`) + `capacity_threshold_fraction: 0.5` trigger | schema owner (`00-BOOK/SCHEMAS/`) action |
| **J6** | Flat ledger vs ratified DAG | **CONVERGED** — a new **map inside the existing ledger**, exactly as `by_execution` was added; chain shape proven by `engine/certification/ledger.py` | `load_ledger()` additive-default precedent (`ukb.py:867-873`) | ledger owner (UMB-003) action |
| **J7** | No corpus-wide identity replay tier | **CONVERGED** — compose existing per-object primitives into one fingerprint; declare it as a `validations[]` dimension | `IdentityRegistry.fingerprint()` · `verify()` · `reproduces()` · non-vacuity rule | gate composition is owner action |
| **J8** | UIL-11 DECLARED-NOT-MEASURABLE | **CLOSED** — authorities are a declared population; an authority's identity is minted by its parent, rooted at Genesis (AIF-L10) | `laws[]` `measurable` flag flips on declaration | none |

**Two dissolved, five converged, one closed. Zero repaired.** No blocker is closed by fixing a value; every blocker is closed by declaring what the value always was.

## 0.4 What must change, and what must not

| Set | Contents | Changes under closure? |
|---|---|---|
| **Architecture** (code) | `engine/registry/universal/identity.py` · `engine/uckp/{identity,canonical}.py` · `platform/foundation/{durable_identity,crypto_agility,canonical}.py` · `uis_engine.py` | **NO** — zero enumeration is already probe-enforced (`check_no_enumeration`, `uis_engine.py:1600`) |
| **Declaration** (data) | `uis-declaration.json` `identity_mechanisms[]` · `laws[]` · `validations[]` · extension kind codes · CCF profile ids · algorithm registry entries | **YES — append-only** |
| **Recorded identity** | every `universal_id`, `edge_id`, `observation_id`, `page`, ordinal, digest already written | **NEVER** |

Closure is therefore an **append-only declaration event plus a one-time adoption event.** Nothing else.

---

# PART 1 — ANALYSIS

## 1.1 Relationship identity convergence (J1)

**Current mechanism.** `00-BOOK/tools/ukb.py:1020-1032`: `edge_seq = [0]` is a per-build, in-memory counter reset to zero on every run; `eid = f"UEDGE-{edge_seq[0]:09d}"` is assigned at the moment `add_edge` is called, so the value is a function of traversal position — structural chains, then cross-program, then program-root parenting, then metadata edges. 13 361 edges in `relationships.json`; 18 430 `UEDGE-` references across `00-BOOK/DATA/`; `inverse_of` persists a positional cross-reference (`UEDGE-000013361 → inverse_of: UEDGE-000013360`). No `by_edge` map exists in `id-ledger.json`.

**Why this is not a repair problem.** Repairing it would mean choosing new `UEDGE-` values — renumbering, prohibited by UIL-06, UIL-18, AIF-L17 and CR-INF-005.2. Leaving it means identity remains positional, prohibited by AIF-L02 and CR-INF-005.1.

**The convergence reading.** Both horns are false because `UEDGE-NNNNNNNNN` is not in the identity plane at all:

- It is **not P2**: P2 is opaque, minted-once, recorded, authority-namespaced, never order-derived. `UEDGE-` is transparent, regenerated, unrecorded and order-derived.
- It **is P3**: an authority-local admission ordinal, rendered, not globally meaningful. That is precisely AIF-L04's definition — except that AIF-L04 additionally requires it be *recorded at mint and never recomputed*, and the current mechanism recomputes it every build. **That single property is the whole of J1.**

**Convergence, step by step, using only located mechanisms:**

1. **Population** — `RegistryKind.RELATIONSHIP` with code `REL` already exists (`engine/registry/universal/identity.py:138`). No population is created.
2. **Admission key** — `local_key` = the canonical render of the ordered triple `(from, to, type)`. This is the *admission key*, not a content digest: for a relationship the endpoints-and-type **are** the thing, so keying on them is AIF-L06 path-independent keying, not AIF-L05 content identification. The distinction is load-bearing and already encoded: `compute_opaque` hashes `{authority_id, local_key, plane:"P2"}` and *never* content, order or path.
3. **Durable identity** — `urn:ucos:p2:<AuthorityID>:<32 hex>`. Order-independent, build-independent, insertion-stable. Inserting an edge in the middle of `C.CHAINS` changes no other edge's identity.
4. **Ordinal adoption** — all 13 361 existing `UEDGE-` renders are adopted **frozen**, becoming recorded rather than recomputed. Every one of the 18 430 references keeps resolving to the same edge.
5. **`inverse_of`** — resolves through `durable_reference()` rather than through a positional neighbour.
6. **Dedup already keys on the triple** — `_seen_edges.add((src, dst, etype))` at `ukb.py:1024`. The admission key the convergence needs is *already computed*; only the identifier fails to use it.

**Finding CV-1.** The relationship schema already gets the harder half right: `relationship.schema.json:26` declares the type vocabulary OPEN and append-only — "a new relationship type is a new value, never a rewrite." Convergence applies that same sentence to the `edge_id` field.

## 1.2 Digest algorithm and canonicalization convergence (J2/J3)

**Current state.** One algorithm in every production path (SHA-256; no MD5, no BLAKE2; SHA-1 only inside RFC-4122 UUIDv5). Three canonicalization profiles: Layer Zero compact (`engine/uckp/canonical.py:57`), engine-local pretty (`indent=2` + trailing newline, ~9 `00-MASTER` engines), UAKOS ad-hoc (`sort_keys` only, default separators, `ensure_ascii=True`, ~13 sites). Six truncation widths (8/12/16/20/32/64). ~5 900 persisted digest values carry no algorithm tag; exactly two files record `"algorithm": "sha256"`; the only `sha256:`-prefixed strings in the tree are OCI image references.

**The agility layer is complete and unused by data.** `platform/foundation/crypto_agility.py` provides: `Multihash` self-describing as `algorithm:value`, *representable for an algorithm this runtime cannot compute*; `DigestSet.compute/rolled_over/verify/verify_with` over the same canonical bytes, sorted by algorithm, tagged with `profile_id`; `AlgorithmRegistry` with `register` (never overwrites), `active_algorithms` (strongest first, deterministic tie-break), `negotiate` (fails closed), `rollover(name, strength, witness=…)` (refuses an unnamed witness, refuses a duplicate name), `deprecate` (refuses to leave zero active). `platform/foundation/canonical.py` provides `CanonicalProfile` (immutable, versioned, `__post_init__`-validated) and `ProfileRegistry.register` which **refuses to overwrite an existing `profile_id` with different parameters** — append-only by construction.

**The convergence reading — the three profiles are not a defect to unify; they are three profiles to register.** Unifying them would change historical digests, i.e. rewrite Recorded Truth. Registering them makes every historical digest permanently interpretable:

```
CCF-GENESIS-COMPACT  ← ucos-uckp-canonical-json/1.0.0   sort_keys, (",",":"),  ensure_ascii=False
CCF-GENESIS-PRETTY   ← indent=2, sort_keys, ensure_ascii=False, trailing "\n"
CCF-GENESIS-LOOSE    ← sort_keys only, default separators, ensure_ascii=True
```

Each is a `CanonicalProfile` with its own `profile_id`. `ProfileRegistry` already guarantees none can be mutated later. **Forward** minting uses the pinned default; **historical** digests are read under the profile their producing engine declares. Nothing is re-hashed. This is AIF-L24 ("CCF/algorithm/id-width/encoding are pinned parameters that widen append-only") applied literally.

**Finding CV-2.** The field name `content_hash` currently means raw file bytes in `ukb.py`/`uga_engine.py` and canonical-JSON text in the `00-MASTER` engines. Under convergence the *record* carries `profile_id`, so the ambiguity is resolved by declaration rather than by renaming ~3 905 fields. Field renaming would be a compatibility layer; declaration is not.

**Finding CV-3.** Because P2 identity is a *recorded opaque token* and not a live hash, a total break of SHA-256 invalidates zero identities. Only verification migrates, and `Multihash` can already represent the successor algorithm before this runtime can compute it. Infinite algorithm evolution is therefore a property of the located mechanism, not a future work item.

## 1.3 Identity minting authority discovery (J4)

**Nine minting sites; six located in `identity_mechanisms[]`, four not.**

| Site | Render | Located? | Parseable by the `UCOS-` authority? |
|---|---|---|---|
| `ukb.py::allocate` / `allocate_execution` / `upn` | `UCOS-<CAT>-<6d>`, `UPN-<9d>` | MECH-UKB / MECH-NOMENCLATURE | n/a (P2/P3) |
| `uga_engine.py::epoch1_identity` | `UCOS-<CAT>-<6d>` | shares MECH-UKB's one counter | n/a |
| `engine/registry/universal/identity.py` | `UCOS-<CODE>-<12h>` | MECH-EPIC001 | YES |
| `engine/uckp/identity.py` | `urn:ucos:ucko:…` + UUIDv5 | MECH-UCKP | n/a |
| `engine/knowledge/ukip/contracts.py` | content digest | MECH-UKIP | n/a |
| `engine/context/constitution.py` | context tuple | MECH-UCXI | n/a |
| `engine/kernel/identity.py` | `UMK-<SLUG>-<12h>` | **NO** | n/a (own prefix) |
| `platform/universal_pipeline/identity.py` | `UAPF-<KIND>-<20h>` | **NO** | n/a (own prefix) |
| `intelligence/kernel/ids.py` | `UCOS-<10 codes>-<12h>` | **NO** | **NO** — codes unregistered |
| `platform/foundation/identity.py` | `UCOS-PRIN-<16h>` | **NO** | **NO** — `parse_kind_name` raises |
| `platform/universal_control_plane/{intelligence,prompt,ontology}.py` | `MET-`/`PRG-`/`PRM-<12h>` | **NO** | n/a (own prefixes) |

**Discovery is already mechanical; only its scope is narrow.** Three located probes exist:

- `engine/uicm/validation.py:57` — AST scan for `_FORBIDDEN_MINTS = ("deterministic_id","mint","uuid4","uuid5","identity_tuple")` with a *measured* exemption list (`_DERIVED_ID_MODULES`), failing closed if an exemption vanishes. Scope: one package.
- `engine.uckp.validation.ConstitutionalValidator._probe_zero_duplication` — parses every module in `engine` and `platform` for a module-level `canonical_json`/`canonical_bytes`/`content_hash` that implements rather than forwards. Scope: `engine` + `platform`.
- `uis_engine.py::symbol_present` — proves a declared module and symbol resolve **by source text, never by import**; `UIS-V-05` requires every mechanism classified into exactly one plane, `UIS-V-06` requires module and grammar symbol to resolve, `UIS-V-07` requires every declared plane to carry at least one mechanism.

**Finding CV-4.** Authority discovery needs no new instrument. `UIS-V-05/06/07` already turn "declared but unresolvable" and "claiming two planes or none" into detectable events. What is missing is the four declarations — and `register_kind` (append-only, refusing re-coding and code reuse) is the located admission path for `PRIN`, `RSRC`…`CITE`, `MET`, `PRG`, `PRM`. None is renamed; none is renumbered.

**Finding CV-5.** `intelligence/kernel/ids.py:119` inlines `hashlib.sha256(canonical_json(...).encode("utf-8")).hexdigest()`. Byte-identical to `content_hash` today. It is a latent fork of Layer Zero, and it is exactly the class of defect `_probe_zero_duplication` was written to catch — outside its current scope.

## 1.4 Artifact identity grammar evolution (J5)

`^UCOS-[A-Z][A-Z0-9]{1,11}-[0-9]{6}$` (`00-BOOK/SCHEMAS/artifact.schema.json:20`) compiles in three limits at once: category width ≤ 11, ordinal width = 6, and ordinal *form* = decimal (therefore sequential). Namespaces are derived from path stems truncated to `DERIVED_CATEGORY_MAXLEN = 6` (`00-BOOK/tools/config.py:494`), producing nine collision windows (`ARCHIT`, `CANONI`, `DEPEND`, `EVOUSI`, `EXECUT`, `IAC001`, `READIN`, `REPOSI`, `WAVE01`), 109 live namespaces of which 74 are ungoverned, and the pinned `UIL-16 ≤ 17` ambiguity bound.

**The evolution model is already legislated, verbatim.**

- **CR-INF-002.4** — "Zero-padding width (e.g. `NNNNNN` in `UCOS-<CATEGORY>-NNNNNN`) is a formatting convenience for sort-stability, **not** a ceiling; padding width MAY be extended append-only if a population approaches its current width, **without renumbering prior members**."
- **CR-INF-002.3** — no sequence number, count, index or cardinality anywhere in UCOS may be read as an upper bound.
- **CR-INF-003.2** — "All limits MUST be externally configurable. All capacities MUST be architecturally expandable."
- **IL-INF-02** — every number read as sequence, never as ceiling. **IL-INF-05** — every limit read as configuration, never hard-coded architecture. **IL-INF-06** — every construct admits a next member "without rewrite, renumber, or migration."

**The trigger is already declared and already measured.** `uis-declaration.json` `unboundedness.capacity_threshold_fraction = 0.5`, with the declared reading: "A namespace crossing the declared fraction is not a violation of the architecture — it is the declared trigger for the owner to widen the parameter, and this dimension is what makes that trigger observable instead of arriving as an exhaustion."

**Finding CV-6.** J5 therefore has no technical content. The grammar governs a P3 render whose width is declared formatting; widening it is a *parameter change with a measured trigger*, and the current pattern is preserved verbatim as the Genesis-epoch profile. The one substantive item is that the grammar must be *versioned by profile id* so "the pattern in force when this identifier was minted" is answerable — which `grammar_source.pointer` resolution (`uis_engine.py:256-262`) already supports and `ProfileRegistry` already models.

## 1.5 Identity storage architecture convergence (J6)

`00-BOOK/DATA/id-ledger.json` is RECORDED truth: `version`, `by_path`, `page_cursor`, `category_seq`, `discovered_volumes`, `volume_seq`, `history`, `by_object`, `by_observation`. Two writers only (`ukb.py::_dump_json` at 1279/2344/2361; `uga_engine.py:1869`); readers fail closed and never mint. It is a flat append-only map. AIF-L08 ratifies a **Merkle-linked, mergeable event DAG** with branches and merges first-class. It has no JSON Schema. `first_seen` is non-uniform (ISO-8601 in `by_path`, `commit:<12hex>` in `by_object`).

**Two located precedents make this a non-event.**

1. **Additive maps.** `load_ledger()` (`ukb.py:867-873`) documents `by_execution` as "an append-only map of execution KEY → {execution_id, first_seen} sharing the ONE identity authority (`category_seq`). **Additive to the ledger; a legacy ledger lacking it gets it on next load.**" A new map in the existing ledger is therefore the *established* way to admit a population — and it is the opposite of a parallel ledger, because it shares the one authority.
2. **Chain shape.** `engine/certification/ledger.py` already implements the DAG discipline in-repo: `GENESIS_HASH = "0"*64`, `entry_hash = content_hash({sequence, certification_id, record_sha256, prev_hash})`, `append` refusing a non-integral record, `verify()` walking sequence/prev/recomputed-hash, no update and no delete path, `"ledger_format": "ucos-certification-ledger/1.0.0"`.

**Finding CV-7.** Chaining the identity ledger is an append-only extension of an existing store using a chain algorithm already proven in the repository. `IdentityRegistry.export()` is already "deterministic, self-describing", exports **only sealed identities** ("provisional mints are not Recorded Truth and never persist"), and its `to_dict` is documented as "an alias kept parallel with the DAG ledger's `to_dict` surface" — the parallelism was anticipated.

**Finding CV-8 (the honest constraint).** `platform/foundation/durable_identity.py` is in-memory and never writes the certified corpus (DP-03). So persisted P2 truth requires the **ledger owner** (UMB-003) to admit the map. This is a governance dependency, not a missing mechanism, and it must be discharged inside `id-ledger.json` — never as a second file.

## 1.6 Universal replay architecture (J7)

Located replay machinery: `digests_match` (the equality test); `engine/determinism/reproduce.py` `double_build`/`compare_builds` over five categories, forcing a file-less category to non-identical so an empty build cannot pass; `.github/workflows/determinism.yml` uploading evidence `if: always()`; `engine/uaue/gate.py` `UAUE-GATE-05` conducting twice and requiring identical digest, identical `run_id` and equal settlement rounds, with **an empty candidate set a FAIL**; `replay_drift` comparing committed files as *bytes* against `canonical_json(projection) + "\n"`; `phase5_replay` measuring 8 identity dimensions per round; `master_plan_replay.py` reconstructing from a hash-chained journal.

Per-object identity replay primitives all exist: `DurableIdentity.verify()`, `IdentityRegistry.verify()` / `require_intact()` / `fingerprint()` (= `content_hash(export())`), `IdentifierEntry.reproduces()`, `UniversalIdentity.require_intact()`, `Identity.require_intact()`, `DigestSet.verify()` / `verify_with()`.

**Finding CV-9.** The gap is composition, not capability. And the adoption model makes replay *two-class*, which the located code already encodes:

- **Minted records** — `verify()` recomputes `compute_opaque(recorded key)` and compares. This is Bit replay.
- **Adopted records** — `verify()` short-circuits `True` because "an adopted identity carries a frozen historical opaque that is preserved, not recomputed (AX-02)". This is Historical replay: the obligation is *preservation*, not re-derivation.

Conflating the two would either falsely fail history or falsely pass forward minting. `DurableIdentity.adopted` is the single flag that separates them, and it already exists.

## 1.7 Identity measurement closure (J8)

`uis-declaration.json` is the closure vehicle for the entire determination, and its own `$comment` states the property that makes it so:

> "This file is DATA and is the ONLY place the canonical owners, the identity planes, the located identity mechanisms, the laws, the bookkeeping obligations, the capability mapping, the protected records, the blocking dimensions and the exit criteria are stated. `uis_engine.py` contains no universal identifier, no category namespace, no ledger path and no discovered family name… **Adding a capability, a law, a plane, a mechanism or a dimension is an append-only edit to this file and requires NO engine change (PR-07 Zero Enumeration).**"

Enforced by `check_no_enumeration` (`uis_engine.py:1600`, wired at 1761) plus `--check-declaration`, `--check-write-scope`, `--check-determinism`, `--check-knowledge-once`, `--check-record-immutability`, `--check-no-identity-minting`, `--check-bounds-tight`, `--check-no-authority`. Currently declared: 5 planes · 6 mechanisms · 20 laws · 19 bookkeeping obligations · 54 capabilities · 8 exit criteria · a `validations[]` dimension set.

**UIL-11** is the only law with `measurable: false`, and its declared reason is precise: "The internal constructs are code-plane objects held by the located engines, not artifact-plane files; asserting reflexivity over them would require this measurement to mint or read an identity it has no authority over."

**Finding CV-10.** The reason is contingent, not permanent. It holds only while authorities and mechanisms are *undeclared as a population*. Once `AUTHORITY` is a declared population with a located authority (its parent, rooted at the AIF-L10 Genesis anchor), every UIS internal construct has an identity that UIS can **read** — and reading is precisely what UIS is permitted to do. `measurable` flips from `false` to `true` in declaration data, with no engine change, by the file's own PR-07 guarantee.

---

# PART 2 — DETERMINATIONS A…G

## A. Final identity convergence architecture

**DETERMINED.** Three append-only declaration registers, one protocol, one adoption event. All five are names for existing mechanisms.

```
REGISTER 1 — CELL REGISTER          ⟨plane, population, authority, grammar owner, keyed_by⟩
  located as: uis-declaration.json identity_mechanisms[]  +  register_kind() code space
  guarantee : exactly one authority per (plane × population); UIS-V-05/06/07 enforce
              exactly-one-plane, resolvable module+grammar, no unrealized plane

REGISTER 2 — EPOCH REGISTER         ⟨profile_id, ccf_profile, algorithm_set, id_width, encoding⟩
  located as: CanonicalProfile + ProfileRegistry (register() refuses overwrite)
            + AlgorithmRegistry + RolloverRecord(witness) + DigestSet.profile_id
  guarantee : parameters widen append-only (AIF-L24); an epoch is never mutated,
              only succeeded; every historical value stays interpretable

REGISTER 3 — LAW & MEASURE REGISTER ⟨law, invariant, measure, comparator, bound, blocking⟩
  located as: uis-declaration.json laws[] + validations[] + exit_criteria[]
  guarantee : PR-07 zero enumeration — adding a law, plane, mechanism or dimension
              requires NO engine change; check_no_enumeration fails closed otherwise

PROTOCOL   — DECLARE → ADOPT → MINT FORWARD → MEASURE → CERTIFY   (§0.2, invariant CP-1)
EVENT      — GENESIS ADOPTION (AIF A/G7), one-time, per population, ordinals frozen
```

**Determination A-1 — the architecture is closed at the plane level and open at every other level.** Five planes (closed by AIF-L03; a sixth is an amendment to AIF, never an edit). Authorities, populations, algorithms, profiles, widths, laws and measures are all open and append-only. This is the exact shape required by "infinite evolution with no new identity system."

**Determination A-2 — convergence is subtraction, not addition.** Nine minting sites do not become one site; they become **six located cells plus four declarations**. Three canonicalization profiles do not become one; they become **three registered epochs plus one pinned default**. The count of mechanisms after closure is the count before closure. Zero mechanisms are created; zero are deleted.

**Determination A-3 — no resolver, temporary or permanent.** Resolution is already total: `IdentityRegistry.resolve()` accepts an opaque or a full URN and fails closed; `lookup()` resolves by admission key and fails closed; `IdentifierEntry.lookup()` re-derives rather than searching. A temporary resolver would be a second authority over the same question.

## B. Migration philosophy preserving AIF-L17

**DETERMINED.** **There is no migration. Convergence is declaration plus adoption plus forward minting — three operations, none of which can write a recorded identity value.**

The philosophy in one sentence: **history is not converted, it is *dated*.**

| Prohibited operation | Why it never occurs |
|---|---|
| Renumber | The protocol has no write path to an existing render. Ordinals are adopted *frozen*; `DurableIdentity.adopt` validates and preserves the value verbatim and sets `adopted=True`. |
| Delete recorded truth | Every located store is append-only with no delete path: `history` appends only on change with `seq = last+1`; page space never reused; `retire()` marks and never removes; certification ledger has no update or delete. |
| Rewrite a digest | Rollover *widens* a digest set (`rolled_over` appends a multihash over the same bytes and refuses a duplicate algorithm). Historical values are read under their registered profile. Nothing is re-hashed. |
| Translate an identifier | No crosswalk table is introduced. The P3 render *is* the crosswalk, and UMB-004 §2 already declares the Nomenclature Engine maintains it — "renaming a native ID never changes the durable identity." |
| Special-case a population | Every clause of this determination is population-parametric. §1.1 is the general model with `population = REL`. |

**Determination B-1 — AIF-L17 is preserved structurally, not procedurally.** Forward-only compensation is not a rule the protocol obeys; it is a property the protocol cannot violate, because no step in §0.2 takes a recorded identity value as a write target. A correction is a new event (`history` append, a new certification entry, a widened digest set) — which is AIF-L17's own definition.

**Determination B-2 — the two non-zero bounds are permanent architecture.** `identities_unresolvable ≤ 6` (UIL-08 / UIS-F-002) and `namespace_partition_ambiguities ≤ 17` (UIL-16 / UIS-F-004) must **never** be repaired: repairing either requires deleting or renumbering recorded identity. They remain declared, bounded, measured and disclosed, with `--check-bounds-tight` preventing silent loosening. **A closure that reduced them would be a closure that violated the laws it claims to close.**

**Determination B-3 — the frozen corpus is the Genesis epoch, and that is a complete account of it.** The 6-digit ordinals, three canonicalization profiles, six digest widths, 74 ungoverned namespaces, nine truncation collisions, non-uniform `first_seen`, and untagged digests are all *parameters of one declared epoch*. They require no exception because the epoch register's purpose is to hold exactly this.

## C. Identity ownership resolution

**DETERMINED.** Ownership resolves by **cell**: exactly one authority per (plane × population). Two authorities in one cell is the definition of duplication; the same *function* used in two cells is not duplication.

Resolution rules, all already enforced or enforceable by located probes:

1. **One authority per cell.** `UIS-V-05` — every located mechanism classified into exactly one declared plane. A mechanism claiming two planes or none is a detectable event.
2. **The authority is named in the identifier.** `urn:ucos:p2:<AuthorityID>:<opaque>` — uniqueness by construction (AIF-L07), no coordination (AIF-L09), no registry lookup to prove non-collision.
3. **Shared counters are not shared authority.** `uga_engine.py` mints `by_object`/`by_observation` off the same `category_seq` as `ukb.py` and reads `by_path` rather than minting into it (`epoch1_identity` lines 271-279). One counter, distinct cells, no second scheme. This is the pattern the four unlocated sites adopt.
4. **Discovery is mechanical.** Generalize `_FORBIDDEN_MINTS` (`engine/uicm/validation.py:57`) repository-wide with a *measured* exemption list; keep `_probe_zero_duplication` for the canonical primitive; keep `symbol_present` source-text proof. Prose prohibition of hidden minting is the class of claim that quietly stops being true.
5. **Codes are admitted, never renamed.** `register_kind` is append-only, validates `[A-Z][A-Z0-9]{1,7}`, and refuses both re-coding an existing kind and reusing a code. `PRIN`, `RSRC`…`CITE`, `MET`, `PRG`, `PRM` are admitted as-is.
6. **Realization is verified, not asserted.** `realization_obligation` requires each obliged architecture to carry the `REALIZES AIF` / `AIF CONFORMANCE` token and the `exactly one identity authority` phrase; `UIS-V-04` fails closed if an owner drops it or a new architecture is named without one.

**Determination C-1 — J4 closes without deleting a single generator.** Four declarations plus three code-space registrations plus one digest delegation (`intelligence/kernel/ids.py:119` → `content_hash`). No identifier changes value. No module is removed.

**Determination C-2 — write scope is part of ownership.** `uis-declaration.json` `forbidden_write_prefixes` (`00-SOURCE/`, `99-FREEZE/`, `01-WORKING/`, `02-MASTER/`, `07-ENGINEERING/`, `00-CEP/`, `00-CMG/`, `00-BOOK/`, `engine/`, `intelligence/`) makes the measurement provably unable to alter what it measures, and `--check-write-scope` fails closed if its own home ever falls inside one. **A consequence: the conformance owner cannot close J5 or J6 itself** — the schema and ledger owners must act. That is correct separation, and it is recorded as a residual in §G.

## D. Deterministic identity adoption model

**DETERMINED.** Adoption is a **total, idempotent, collision-guarded, retirement-respecting** function that freezes a historical value. It is fully implemented; no new logic is required.

```
adopt(authority_id, local_key, opaque) → DurableIdentity{adopted=True}

  validate  local_key and authority_id as tokens; '/' forbidden in either
  validate  opaque is exactly P2_OPAQUE_HEX_LEN lowercase hex        (width-checked)
  refuse    if the admission key is retired          → IdentityMintError
  return    existing if already sealed to the same opaque            (idempotent)
  refuse    if already sealed to a different opaque   → IdentityCollisionError
  guard     _guard_opaque: reject an opaque bound to another key, committed OR pending
  seal      committed[ref] = identity ; _by_opaque[opaque] = ref ; _order.append(ref)
  log       foundation.durable_identity.adopted
```

Round-trip determinism is already asymmetric in exactly the right way (`DurableIdentity.from_dict`, `IdentityRegistry.from_dict`):

- `adopted: true` → re-adopted, value preserved verbatim (AX-02: Recorded Truth is never recomputed).
- `adopted: false` → re-minted and compared; a mismatch raises `IdentityCollisionError("imported opaque does not match its admission key (tamper detected)")`.

**Determination D-1 — adoption is a record, not a mapping.** This is why no migration table exists. A table maps old → new; adoption records "this value is the value" and marks it frozen. `adopted` is one boolean on one record.

**Determination D-2 — adoption is bounded and one-time per population.** AIF A/G7: a one-time `Genesis-Adoption` that imports and grandfathers the existing corpus with frozen ordinals. Adoption is not an ongoing mode; after the event, `mint()` is the only path, and `mint()` never adopts.

**Determination D-3 — adoption cannot manufacture uniqueness it does not have.** `_guard_opaque` runs on the adoption path too, over both committed and pending sets. If two historical records share an opaque, adoption **fails closed** rather than silently coalescing them. The count of adopted identities is therefore itself evidence.

**Determination D-4 — `verify()` must remain two-class.** Adopted → `True` by preservation. Minted → recompute and compare. Any change that made adopted records recomputable would renumber history; any change that made minted records trivially valid would disable tamper detection.

## E. Replay and audit model

**DETERMINED.** **Registration replay** as a declared tier of AIF-L19, two-class per §D-4, composed from located primitives, fail-closed on vacuity.

| Level | Obligation | Located mechanism |
|---|---|---|
| Record (minted) | `compute_opaque(recorded key) == recorded opaque` | `DurableIdentity.verify()` |
| Record (adopted) | recorded value byte-identical to what is recorded | `DurableIdentity.verify()` short-circuit (AX-02) |
| Index | `len(_by_opaque) == len(_committed)`; every key ↔ opaque bijective | `IdentityRegistry.verify()` |
| Population | one deterministic value replays the whole population | `IdentityRegistry.fingerprint()` = `content_hash(export())` |
| Digest | every carried multihash recomputes over the same CCF | `DigestSet.verify()` / `verify_with()` |
| Corpus | derived views byte-identical across two runs | `reproduce.py::compare_builds`; `replay_drift` byte comparison |

**Determination E-1 — non-vacuity is mandatory and already precedented.** An empty population, an unpopulated cell, an unmeasured law and a file-less comparison category all **FAIL**. Three located precedents: `compare_builds` forces a missing category to non-identical; `_replay_obligation` fails on zero candidates ("an empty candidate set is a FAIL, not a vacuous pass"); `certification_framework_status` fails on an empty ledger. The nine schema-declared prefixes with zero members must be declared **RESERVED**, not silently pass as satisfied.

**Determination E-2 — audit is the recorded event stream, not a report.** Every mint, commit, abort, retirement and adoption is a structured event (`foundation.durable_identity.{prepared,committed,aborted,retired,adopted}`), and the artifact plane already carries `03-AUDIT-UNIVERSE.json` (4 914 events, `UGA-AUD-<12h>`), `history` snapshots, and the change ledger (1 587 events). AIF-L11 signs events; AIF-L12 records ACT boundaries at seal and never recomputes them.

**Determination E-3 — replay is declared, not coded.** The new tier enters as a `validations[]` dimension with a measure, comparator, bound and `blocking: true`. By PR-07 this requires no engine change, and `check_no_enumeration` guarantees the engine cannot have hard-coded the population it measures.

## F. Certification model

**DETERMINED.** **AIF-L21 duality, unchanged. Two stores, two truth classes, no contradiction possible because neither is a claim about the other.**

```
HISTORICAL ATTESTATION  (RECORDED · immutable · hash-chained · never recomputed)
  the Genesis-Adoption event per population: what was adopted, under which epoch,
  with which frozen ordinals, witnessed by whom
  located: engine/certification/{contracts,ledger}.py — CertificationRecord.create()
           derives id and content_sha256 from a core excluding both, so identical
           determinations produce an identical id; ledger append-only from
           GENESIS_HASH with no update/delete path

CURRENT STATUS          (DERIVED · recomputed every run · never authored)
  do all twenty laws hold now, at their declared bounds, over the live corpus
  located: uis_engine.py + uis-declaration.json laws[]/validations[]/exit_criteria[]
           ukbx.py::cmd_certify → certification.json (10 domains, CERTIFIED iff all pass)
           build_program_closure: refuses a tampered ledger, computes A10 live,
           closure_sha256 over a core with no wall clock → byte-identical per ledger
```

**Determination F-1 — certification closes scope, never evolution.** CR-INF-001.2 and CR-INF-011 are explicit, and `ukbx.py` already stamps its standard "non-terminal". Certifying identity convergence therefore certifies *that the populations declared so far are converged* — it makes no claim about populations not yet declared, and it cannot close the architecture against them (IL-INF-01).

**Determination F-2 — no new certification domain is required.** The located 10-domain `identity` check (uniqueness, page ranges, cursor) plus the UIS-001 gate (20 laws, 8 exit criteria) plus the EC-1 chain already span the question. Adding an eleventh domain would be an addition; declaring the identity dimension in `validations[]` is not.

**Determination F-3 — the certification of a future population is automatic.** `CertificationRecord` is population-agnostic: `target_id`, `certification_class`, `standard`, `criteria`, `evidence_ref`. A population declared tomorrow is certified by the same record shape, the same ledger and the same closure computation, with no code change.

## G. Remaining blockers

After closure, **no technical blocker remains.** What remains is four **owner-action dependencies** and two **permanent architectural readings**. These are stated as residuals rather than closures because this determination holds no authority to discharge them.

| # | Residual | Class | Owner who must act | Why it cannot be closed here |
|---|---|---|---|---|
| **R1** | Declare the four unlocated cells (`UMK`, `UAPF`, `intelligence`, `PRIN`/control-plane) and register their code spaces | owner action | `engine/` · `platform/` · `intelligence/` package owners + UIS-001 declaration | `engine/` and `intelligence/` are inside UIS's `forbidden_write_prefixes` |
| **R2** | Admit a durable-identity map into `00-BOOK/DATA/id-ledger.json` (as `by_execution` was admitted) and chain it | owner action | UMB-003 identity-architecture owner | `00-BOOK/` is a forbidden write prefix; `durable_identity.py` is in-memory by DP-03 |
| **R3** | Version the artifact-plane grammar by profile id, preserving the current pattern verbatim as the Genesis profile | owner action | `00-BOOK/SCHEMAS/` + UMB-004 nomenclature owner | schema ownership; also the trigger for CR-INF-002.4 width extension |
| **R4** | Register the three canonicalization epochs and tag forward digests as multihashes | owner action | Layer Zero owner (`engine/uckp/`) + each `00-MASTER` engine owner | ~130 producer sites across packages this determination cannot write |
| **R5** | `identities_unresolvable ≤ 6` and `namespace_partition_ambiguities ≤ 17` | **permanent** | none — preserved by law | Repairing either requires deleting or renumbering recorded identity (AIF-L17, UIL-05/06/13). **Must never be closed.** |
| **R6** | Nine schema-declared prefixes with zero members (`DEP`, `ENV`, `TST`, `FND`, `UI`, `UX`, `FLOW`, `CONN`, `EXP`) | **permanent** | declaration | Must be declared RESERVED so they fail non-vacuity rather than passing silently (§E-1). Grammar declared ahead of population is legitimate; a vacuous pass is not. |

**Determination G-1 — R1…R4 require zero new mechanisms.** Each is an append-only edit by the instrument's own owner, using a mechanism already present in that instrument's package. The architecture set (code) does not change; the declaration set (data) does.

**Determination G-2 — the sequencing is forced.** R1 before R2 (a map cannot be admitted for undeclared cells), R2 before R7-class replay gating (nothing to replay until P2 is recorded), R3 and R4 independent. **J8 is already closed by R1**, because declaring authorities as a population is what makes UIL-11's `measurable: false` reason expire.

---

# PART 3 — PROOF: A FUTURE UNKNOWN POPULATION

**Claim.** Let Π be an identity population that does not exist today and whose nature is unknown — a population no artifact, schema, enum or engine in this repository names. Then Π can be admitted, receive identity, be validated, be replayed, be audited and be certified **without modifying identity architecture**.

## 3.1 Definitions

- **Architecture set 𝒜** — the code that implements identity: `engine/registry/universal/identity.py`, `engine/uckp/{identity,canonical}.py`, `engine/kernel/identity.py`, `platform/foundation/{durable_identity,crypto_agility,canonical}.py`, `platform/universal_pipeline/identity.py`, `00-MASTER/UIS-001/uis_engine.py`, `engine/certification/*`.
- **Declaration set 𝒟** — the data that parameterizes it: `uis-declaration.json` (`identity_mechanisms[]`, `laws[]`, `validations[]`, `exit_criteria[]`), the `register_kind` extension code space, `ProfileRegistry` profile ids, `AlgorithmRegistry` entries.
- **"Without modifying identity architecture"** — 𝒜 is unchanged; only 𝒟 is appended to.

## 3.2 Lemma 1 — 𝒜 contains no enumeration of populations

`uis_engine.py` "contains no universal identifier, no category namespace, no ledger path and no discovered family name: everything it measures is read from [the declaration] and everything it reports is DISCOVERED from the located sources." This is not a docstring claim: `check_no_enumeration` (`uis_engine.py:1600`, wired at 1761) fails the engine closed if it is false, and `--check-declaration` fails closed if a cited owner is unprotected. `symbol_present` proves mechanisms exist by *source text*, never by import, so a declared mechanism the engine has never heard of is still measurable.

Independently: `deterministic_id` accepts "a `RegistryKind` **or the name of a kind admitted through `register_kind`**, so a future entity kind is minted by this same authority" (its own docstring, `identity.py:257-270`); `normalize_segment` in `engine/kernel/identity.py:52-64` deliberately imposes **no alphabet restriction**; `platform/universal_pipeline/identity.py:89` makes the kind registry and the identity namespace *the same object* (`Vocabulary("object-kind")`); `Multihash` is representable for an algorithm the runtime cannot compute. ∎

## 3.3 Lemma 2 — 𝒟 is append-only and admits arbitrary members

`register_kind` validates `[A-Z][A-Z0-9]{1,7}`, appends, and refuses to re-code a kind or reuse a code. `ProfileRegistry.register` refuses to overwrite an existing `profile_id` with different parameters. `AlgorithmRegistry.register` refuses to overwrite a name with different parameters; `rollover` refuses an unnamed witness and a duplicate name; `deprecate` refuses to leave zero active. `uis-declaration.json` states its own append-only extension property (PR-07). Every register therefore grows without bound and cannot mutate an existing member. ∎

## 3.4 The six discharges

Let Π have an authority `A_Π`, a population code `C_Π` (≤ 8 chars, `[A-Z][A-Z0-9]*`), and per-member local keys.

**(1) ADMITTED.** Append `⟨plane, C_Π, A_Π, grammar owner, keyed_by⟩` to `identity_mechanisms[]`; `register_kind(Π, C_Π)`. `UIS-V-05` verifies exactly one plane, `UIS-V-06` verifies the module and grammar symbol resolve, `UIS-V-07` verifies the plane is realized. Admission is *prepare/commit/abort* (AIF-L13), so a failed admission leaves no orphan identity. **𝒜 unchanged.**

**(2) RECEIVES IDENTITY.** `IdentityRegistry.mint(A_Π, local_key)` → `urn:ucos:p2:A_Π:<32 hex>`, the opaque being `content_hash({authority_id, local_key, plane:"P2"})[:32]`. Uniqueness holds by construction against every other population and every other authority, present and future, with no coordination (AIF-L07/L09) — because the authority and the key are both inside the hashed payload. `_guard_opaque` refuses a collision across committed and pending sets. **𝒜 unchanged.** Note `mint` is *never* called by a checker: `mint=False` is the default observation mode (`ukb.py:894-895`).

**(3) VALIDATED.** Four located tiers, all population-parametric: form (`is_well_formed` / `parse_kind_name` / `Multihash.parse` / declared grammar resolved by pointer), admission (`_guard_opaque` + duplicate-UID certification check), integrity (`verify` / `require_intact`), conformance (the 20 laws, whose measures are computed over *declared* sources, not enumerated ones). A law's `measurable` flag and bound are declaration data. **𝒜 unchanged.**

**(4) REPLAYED.** `fingerprint() = content_hash(export())` replays the whole of Π in one value; `verify()` is two-class per §D-4 (adopted preserved, minted recomputed); `DigestSet.verify` covers Π's content digests under Π's declared CCF profile; non-vacuity means an empty Π **fails** rather than passes. Registration replay enters as a `validations[]` dimension. **𝒜 unchanged.**

**(5) AUDITED.** Every mint/commit/abort/retire/adopt on Π emits a structured event through the located observability path; `history` is append-only with contiguous `seq`; retirement marks and never removes; the ledger map for Π is additive exactly as `by_execution` is ("a legacy ledger lacking it gets it on next load"). Traceability (UIL-10) is discharged by the 19 declared bookkeeping obligations, each bound to a located field and a member of the **closed** facet set — and `UIS-V-10` fails closed if an obligation does not bind. **𝒜 unchanged.**

**(6) CERTIFIED.** `CertificationRecord.create()` is population-agnostic (`target_id`, `certification_class`, `standard`, `criteria`, `evidence_ref`) and derives its own id and `content_sha256` from a core excluding both, so an identical determination over Π yields an identical record id. The ledger appends and hash-chains it; `build_program_closure` refuses to build over a tampered chain, computes framework status live, and emits a `closure_sha256` over a wall-clock-free core so the same ledger yields a byte-identical closure. Certification closes Π's scope and never Π's evolution (CR-INF-001.2, CR-INF-011, IL-INF-01). **𝒜 unchanged.** ∎

## 3.5 Corollaries

**C1 — Π needs no schema redesign.** Its grammar is a profile registered in 𝒟; its width is a pinned parameter widening append-only (CR-INF-002.4, AIF-L24); its ordinal render is optional, because identity is the opaque, not the render.

**C2 — Π cannot collide with anything, ever.** The opaque is a digest over a payload containing `A_Π`. Two authorities minting the same `local_key` produce different opaques. This holds across branches, merges, offline operation, organizational splits and organizational merges (AIF A/G1), with no lock and no lookup.

**C3 — Π survives algorithm death.** Π's identities are recorded opaque tokens, not live hashes. A total break of every algorithm in the current registry invalidates none of them; verification rolls over under a named witness while identity is untouched (AIF-L22, Finding CV-3).

**C4 — Π's admission cannot damage any existing population.** By invariant CP-1 no step in the protocol has write access to a recorded identity value. Adding Π is therefore non-destructive by construction — which is IL-INF-06 ("every construct SHALL be read as admitting a next member without rewrite, renumber, or migration") made mechanical.

**C5 — the proof is self-applying.** Π may itself be a population of *authorities*, of *laws*, or of *identity mechanisms*. That is the discharge of UIL-11 (J8): reflexivity is not a special case, it is the theorem applied to 𝒟's own members, terminating at the AIF-L10 Genesis self-signed anchor.

---

# PART 4 — CONFORMANCE

## 4.1 Mandatory principles

| Principle | Discharge | Enforcing mechanism |
|---|---|---|
| Preserve historical identities | Adoption freezes every existing value verbatim; `verify()` short-circuits for adopted records (AX-02) | `DurableIdentity.adopt` · `from_dict` adopted branch |
| Never renumber | The protocol has no write path to an existing render; renders are recorded, not recomputed | invariant CP-1 · AIF-L04 · CR-INF-005 · UIL-06/18 |
| Never delete recorded truth | Every store append-only, no delete path anywhere; `retire()` marks and never removes | `history` · page space · `retire` · certification ledger |
| Never create duplicate identity authorities | One authority per (plane × population); authority named in the identifier; realization token verified | `UIS-V-04/05/06/07` · `_FORBIDDEN_MINTS` probe |
| Never create parallel ledgers | Convergence uses an additive **map inside** `id-ledger.json`, precedent `by_execution`; certification ledger is in-memory (DP-03) | `load_ledger()` additive defaults |
| Never use positional identity | Identity is a digest of the admission key and *never* of content, order or path | `compute_opaque` docstring + payload |
| Never use finite identity assumptions | Planes closed at 5; authorities, populations, algorithms, profiles, widths, laws all open and append-only | AIF-L24 · CR-INF-002/003/007/009/010 · PR-07 |

## 4.2 Prohibitions

| Prohibition | Compliance |
|---|---|
| No new identity system | Zero mechanisms created. Every construct is a name for an existing composition, path-cited. |
| No new ledger | R2 admits a **map** in the existing ledger, exactly as `by_execution` was admitted. |
| No new namespace | Code spaces already in use (`PRIN`, `RSRC`…`CITE`, `MET`, `PRG`, `PRM`) are *registered*, not minted. |
| No compatibility layer | Legacy shapes are dated as Genesis-epoch parameters, never translated. No field is renamed. |
| No migration table | Adoption records "this value is the value"; it maps nothing (§D-1). |
| No temporary resolver | Resolution is already total and fails closed (`resolve`, `lookup`, `IdentifierEntry.lookup`). |
| No special-case identity authority | Every determination is population-parametric; §1.1 is the general model with `population = REL`. |
| Do not implement | No code, data, schema, ledger or relationship record written. This artifact is the only file created. |

## 4.3 Blocker closure summary

| Blocker | Before | After | Mechanisms created |
|---|---|---|---|
| J1 relationship identity | positional, unledgered, 18 430 dependent references | P3 render adopted frozen; P2 minted from the admission key | 0 |
| J2 algorithm-naked digests | ~5 900 untagged values | multihash-tagged forward; history read under its epoch | 0 |
| J3 three canonicalizations | undeclared forks | three registered CCF epochs, one pinned default | 0 |
| J4 unlocated authorities | 4 sites, 2 unparseable code spaces | 4 declared cells, code spaces registered | 0 |
| J5 enumerative grammar | 3 compiled-in limits | render governed by a versioned profile; width a triggered parameter | 0 |
| J6 flat ledger | unchained map, no schema | additive chained map in the same ledger | 0 |
| J7 no identity replay tier | primitives uncomposed | declared `validations[]` dimension over `fingerprint()` | 0 |
| J8 UIL-11 unmeasurable | reason contingent on undeclared authorities | `measurable: true` once authorities are a declared population | 0 |

---

# PART 5 — BOUNDARY, TRACEABILITY, DETERMINATION, CERTIFICATION

## TRACEABILITY REGISTER
All links are navigational and analytical. No referenced determination, constitution, schema, ledger, registry, engine or data file was altered.

| Link | Target | Relationship |
|---|---|---|
| Identity law | `02-MASTER/UCOS-Ω∞-ABSOLUTE-IDENTITY-FEDERATION-AND-CONTINUITY-CONSTITUTION.md` | Governed-By (AIF-L01…L24; A/G1, A/G4, A/G5, A/G7, A/G8, A/G9) |
| Infinite-evolution law | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-AUTH-INF-001-…-CONSTITUTION.md` | Governed-By (CR-INF-001…012; IL-INF-01…08) |
| Identity architecture of record | `07-ENGINEERING/UCOS-Ω∞-UNIVERSAL-IDENTITY-SYSTEM-MASTER-ARCHITECTURE.md` | Depends-On (UIL-01…UIL-20) |
| Conformance declaration | `00-MASTER/UIS-001/uis-declaration.json` | Reads — the closure vehicle (PR-07 zero enumeration) |
| Conformance engine | `00-MASTER/UIS-001/uis_engine.py` | Reads (`check_no_enumeration`, `symbol_present`, grammar-by-pointer) |
| Durable identity mechanism | `platform/foundation/durable_identity.py` | References (mint · adopt · retire · fingerprint · `_guard_opaque`) |
| Crypto agility mechanism | `platform/foundation/crypto_agility.py` | References (`Multihash` · `DigestSet` · `AlgorithmRegistry`) |
| Canonical content form | `platform/foundation/canonical.py` | References (`CanonicalProfile` · `ProfileRegistry`) |
| Canonical primitive (Layer Zero) | `engine/uckp/canonical.py` | References |
| Population code authority | `engine/registry/universal/identity.py` | References (`register_kind`, `REL`) |
| Recorded identity store | `00-BOOK/DATA/id-ledger.json` | References (read-only; `by_execution` additive precedent) |
| Relationship projection | `00-BOOK/DATA/relationships.json` · `00-BOOK/SCHEMAS/relationship.schema.json` | References (read-only) |
| Artifact grammar owner | `00-BOOK/SCHEMAS/artifact.schema.json` | References (read-only, by pointer) |
| Chain-shape precedent | `engine/certification/ledger.py` | References |
| Certification duality | `engine/certification/{contracts,closure,integrity}.py` · `00-BOOK/tools/ukbx.py` | References |
| Predecessor determination | `UCOS-OMEGA-INFINITY-UNIVERSAL-IDENTITY-EVOLUTION-ARCHITECTURE-DETERMINATION.md` | Depends-On (J1…J8 origin) |
| Superior frozen authority | STATUS-001, REG-AUTO-001, UCI-001, AUTH-INF-001, GOV-INT-001 | Read-only superior authority; never altered |

## AUTHORITY BOUNDARY (MANDATORY)
This artifact holds no constituent, governance, ratification, certification or execution authority. It creates no engine, registry, ledger, identifier namespace, resolver, volume or lifecycle. It allocates no identifier and mints no identity. It amends no constitution, supersedes no determination and authorizes no EC-series step. It treats `00-SOURCE/`, `99-FREEZE/`, `01-WORKING/`, `02-MASTER/`, `07-ENGINEERING/`, `00-CEP/`, `00-CMG/`, `00-BOOK/`, `engine/`, `intelligence/` and all program registers as read-only. It embeds no secret, credential or key material. It is subordinate to the frozen constitutional corpus, to AIF, to AUTH-INF-001, to ENG-001 and to every superior determination. Where it conflicts with a located instrument, it is void to the extent of the conflict.

## DETERMINATION

- **A. Is a permanent closure architecture determinable for J1…J8 from existing mechanisms?** **YES.** Three append-only declaration registers, one five-step protocol, one adoption event. Mechanisms created: **zero**.
- **B. Are the blockers repaired or converged?** **CONVERGED.** Two dissolved (J1, J5 — the values in question were never identities, by CR-INF-005 and AIF-L04), five converged onto located mechanisms (J2, J3, J4, J6, J7), one closed by declaration (J8). **None repaired**, because repair would mean renumbering.
- **C. Is AIF-L17 preserved?** **YES, structurally.** By invariant CP-1 no step in the protocol has write access to a recorded identity value; renumbering, deletion and mutation are unreachable rather than merely prohibited.
- **D. Is any prohibited construct introduced?** **NO.** No new identity system, ledger, namespace, compatibility layer, migration table, temporary resolver or special-case authority. R2 is an additive map inside the one existing ledger, on the `by_execution` precedent.
- **E. Can a future unknown identity population be admitted, identified, validated, replayed, audited and certified without modifying identity architecture?** **YES — proved in Part 3.** Lemma 1: the architecture set contains no enumeration of populations, and this is probe-enforced (`check_no_enumeration`). Lemma 2: every declaration register is append-only and unbounded. Six discharges, each citing the located function that performs it, each leaving the architecture set unchanged.
- **F. Are all seven mandatory principles satisfied?** **YES** (§4.1), each bound to an enforcing mechanism rather than to an assertion.
- **G. Does any technical blocker remain?** **NO.** Four owner-action dependencies remain (R1…R4), each an append-only edit by the owning instrument's own owner using a mechanism already in that instrument's package. Two residuals are **permanent by law** (R5 bounded historical divergences, R6 reserved-but-unpopulated prefixes) and must never be closed.
- **H. Is the identity architecture closed against future evolution by this determination?** **NO** — and it must not be. Certification closes scope, never evolution (CR-INF-001.2, CR-INF-011, IL-INF-01). This determination closes the *convergence* of the populations declared to date and makes no claim about populations not yet declared.

## CERTIFICATION

| Attribute | Value |
|---|---|
| Artifact status | ACTIVE — closure determination of record |
| Verdict | **CONVERGENCE ARCHITECTURE DETERMINED · TECHNICALLY CLOSED · 4 OWNER-ACTION DEPENDENCIES · 2 PERMANENT RESIDUALS** |
| Blockers dispositioned | 8 of 8 (2 dissolved · 5 converged · 1 closed) |
| Mechanisms created | **0** |
| Ledgers created | **0** |
| Namespaces created | **0** |
| Authorities created | **0** |
| Migration tables created | **0** |
| Identities altered | **0** |
| Universality proof | Part 3 — 2 lemmas, 6 discharges, 5 corollaries |
| Laws relied upon | AIF-L01…L24 · CR-INF-001…012 · IL-INF-01…08 · UIL-01…UIL-20 |
| Files created | **1** (this artifact) |
| Files modified | **0** |
| Authority | **NONE** |

*Return: [Universal Identity Evolution Architecture Determination](UCOS-OMEGA-INFINITY-UNIVERSAL-IDENTITY-EVOLUTION-ARCHITECTURE-DETERMINATION.md) · [Absolute Identity, Federation & Continuity Constitution](02-MASTER/UCOS-Ω∞-ABSOLUTE-IDENTITY-FEDERATION-AND-CONTINUITY-CONSTITUTION.md) · [Master Index](02-MASTER/UCOS-Ω∞-CONSOLIDATION-PROGRAM-MASTER-INDEX.md) · [Master Knowledge Book](00-BOOK/UCOS-BOOK-000000-UNIVERSAL-MASTER-KNOWLEDGE-BOOK.md)*

**END OF ARTIFACT — UNIVERSAL IDENTITY CONVERGENCE CLOSURE DETERMINATION · ANALYSIS ONLY · NO IMPLEMENTATION · AUTHORITY-NEUTRAL**
