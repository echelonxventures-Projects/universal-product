# UCOS Ω∞ · UNIVERSAL IDENTITY EVOLUTION ARCHITECTURE DETERMINATION

| Field | Value |
|---|---|
| ARTIFACT | UCOS-OMEGA-INFINITY-UNIVERSAL-IDENTITY-EVOLUTION-ARCHITECTURE-DETERMINATION |
| CLASS | DETERMINATION — analysis of record |
| VERSION | 1.0 |
| SCOPE | ALL identity populations, present and future, across every plane |
| AUTHORITY | **NONE.** This determination mints no identity, allocates no identifier, declares no namespace, defines no grammar, opens no registry, legislates no lifecycle and certifies nothing. It reads the identity law the repository has already ratified and the identity mechanisms the repository has already located, and determines the permanent architecture they compose into. |
| LAW OWNER | `02-MASTER/UCOS-Ω∞-ABSOLUTE-IDENTITY-FEDERATION-AND-CONTINUITY-CONSTITUTION.md` (AIF-L01…L24) |
| ARCHITECTURE OWNER | `07-ENGINEERING/UCOS-Ω∞-UNIVERSAL-IDENTITY-SYSTEM-MASTER-ARCHITECTURE.md` (ENG-001) |
| CONFORMANCE OWNER | `00-MASTER/UIS-001/` (UIL-01…UIL-20) |
| SEAL | NOT SEALED — hand-authored determination, not engine-generated. No digest is asserted. |
| IMPLEMENTATION | NONE. No code, data, ledger, registry, authority or framework was created or modified. |

> **DISCLOSURE.** This is not a new identity framework. It creates no ledger, no registry, no authority, no namespace and no parallel identity system. Every mechanism named below already exists in the repository at the path given. Where this determination and a located instrument differ, **the located instrument governs**. The determination's only product is the architecture: which existing mechanism holds which role, permanently, for every population that exists now and every population that does not exist yet.

---

# PART 0 — THE DETERMINATION IN ONE PAGE

The universal identity architecture is **already ratified and partially realized**. It does not need to be invented; it needs to be *closed*. The ratified law is AIF-L01…L24 (24 laws, six Books) with five orthogonal identity planes. The realization is fragmented across nine minting sites, three canonicalization profiles and six digest widths.

The permanent architecture is a single generative function, parameterized — never a table of populations.

```
UID  =  MINT( AuthorityID , PopulationCode , LocalKey )

        opaque   := DIGEST_SET( { authority_id, population_code, local_key, plane: P2 } )
        durable  := urn:ucos:p2:<AuthorityID>:<opaque>          ← IDENTIFIES  (AIF-L02)
        content  := DIGEST_SET( CCF(payload) )                  ← VERIFIES    (AIF-L05)
        ordinal  := recorded-at-mint render, never recomputed   ← RENDERS     (AIF-L04)
        logical  := f(kind, namespace, natural_key)             ← NAMES       (AIF-L03)
        runtime  := bound at execution, never substituted       ← BINDS       (AIF-L03)
```

Six determinations follow from this and nothing else is required:

1. **Populations are infinite because they are not enumerated.** `PopulationCode` is an open, append-only vocabulary (`register_kind`, `engine/registry/universal/identity.py:162-199`). A new population — including one nobody has conceived — is a *registration*, not a schema edit, an enum edit or a new engine.
2. **Namespaces are infinite because uniqueness is by construction, not by coordination.** `AuthorityID` namespaces the key (AIF-L07/L09). Two authorities can mint forever, offline, in parallel, across an org split, and never collide.
3. **Algorithms are infinite because the digest is self-describing.** `Multihash` (`algorithm:value`) and `DigestSet` with witnessed append-only rollover already exist at `platform/foundation/crypto_agility.py`. Identity survives algorithm breakage because identity is *opaque* and *recorded* — not recomputed from content.
4. **Strength is infinite because width is a pinned parameter, not a literal.** AIF-L24 pins CCF profile, algorithm, id-width and encoding as parameters that *widen append-only*. Historical values remain valid under the width in force at their epoch. There is no ceiling to raise because no ceiling is compiled in.
5. **Determinism is regeneration, never allocation.** Identity is RECORDED truth, replayed from the ledger; every view over it is DERIVED truth, a pure function. AIF-L20 forbids deriving identity determinism from generation determinism. This is why `mint` defaults to `False` (`00-BOOK/tools/ukb.py:894-895`): observation can never allocate.
6. **History is preserved by adoption, not migration.** `DurableIdentity.adopt()` (`platform/foundation/durable_identity.py:158-182`) plus Genesis-Adoption (AIF A/G7) grandfather every existing identifier with its ordinal frozen. There is no migration table, because nothing moves.

**Verdict: ARCHITECTURE DETERMINED — NOT YET CLOSED.** Eight blockers remain (Part J). All eight are convergence-onto-existing-mechanism, none requires a new mechanism.

---

# PART 1 — ANALYSIS

## 1.1 Existing identity populations

Populations are located in one recorded store (`00-BOOK/DATA/id-ledger.json`), one derived projection set (`00-BOOK/DATA/*.json`), and a set of program-local declaration registers under `00-MASTER/`.

**Recorded — `00-BOOK/DATA/id-ledger.json` (v1, ~2.09 MB), five maps behind one counter:**

| Map | Key | ID field | Render | Members |
|---|---|---|---|---|
| `by_path` | repo-relative path | `universal_id` | `UCOS-<CAT>-<6d>` | 1 492 |
| `by_object` | repo-relative path | `universal_id` | `UCOS-<CAT>-<6d>` | 4 914 |
| `by_observation` | `observer::subject::kind` | `observation_id` | `UCOS-OBS-<6d>` | 7 |
| `by_execution` | stable execution key | `execution_id` | `UCOS-<EXEC>-<6d>` | **0 — key absent from the committed file** |
| `history` | `universal_id` | append-only snapshots | `seq` 1..n | ~1 264 histories |
| `discovered_volumes` | `VOL-<3d>` | `volume_id` | `VOL-023` | 25 |
| `page_cursor` | — | `UPN-<9d>` | `UPN-000010840` | 10 840 pages |
| `category_seq` | category | counter | — | ~200 categories |

`by_object` splits as EXCLUDED_DOCUMENT 2 621 · EXECUTABLE_OBJECT 1 265 · TEST_OBJECT 831 · DATA_OBJECT 130 · TOOLING_OBJECT 36 · CONFIGURATION_OBJECT 31. The corpus and `by_object` are asserted disjoint (`engine/tests/unit/test_registry_coverage_matrix.py:117-121`) — no object is claimed by two authorities.

**Derived projections:** `artifacts.json` 1 461 · `relationships.json` 13 361 edges · `change-ledger.json` 1 587 events + 1 461 version records + 1 461 lineage records · `signals.json` 15 signals / 267 ingest runs · `volumes.json` 25 · `generated-artifact-registry.json` 345.

**Content-derived populations (no ledger, pure function):** `00-MASTER/UCOS-NUCLEUS-001/…IDENTIFIER-DICTIONARY.json` 212 entries of shape `UCOS-CAP-001c4bf390b8`; `intelligence` research/publication classes (10 codes); UAPF pipeline objects (24 seed kinds); control-plane `MET-`/`PRG-`/`PRM-`.

**Program-local declaration spaces (~247 distinct prefixes observed across `00-BOOK/DATA/`):** `UEDGE-` 18 430 references · `UCHG-` 3 174 · `UEI-` 318 · `ACEE-` 264 · `URRC-` 256 · `UCL-` 212 · `UER-` 202 · `UAUE-` 178 · `MCOS-` 163 · `UCEF-` 161 · `UPF-` 145 · `UMK-` 144 · `CMG-` 142 · plus ~30 more families, and 109 live `UCOS-<CATEGORY>` namespaces of which 35 are governed by a declared classification rule and 74 are not.

**Finding P-1.** The population set is *large, open and already growing without schema edits* in the content-derived spaces, and *closed against schema edits* in the artifact plane. Nine schema-declared prefixes (`DEP`, `ENV`, `TST`, `FND`, `UI`, `UX`, `FLOW`, `CONN`, `EXP`) have zero members — grammar was declared ahead of population, which proves the artifact-plane grammar is currently *enumerative*, and enumeration is the mechanism that fails at "future unknown populations".

## 1.2 Existing identity authorities

Nine minting sites exist. They are not nine competing schemes — five are plane-distinct and legitimate; four are unlocated.

| # | Site | Plane | Keyed by | Status |
|---|---|---|---|---|
| 1 | `00-BOOK/tools/ukb.py::allocate` / `allocate_execution` / `upn` | P2 + P3 | ledger counter `category_seq`, admission order | LOCATED (MECH-UKB) |
| 2 | `00-MASTER/UCOS-UGA-001/uga_engine.py::epoch1_identity` | P2 | same `category_seq`, `by_object` / `by_observation` | LOCATED — shares the one counter, so no second scheme |
| 3 | `engine/registry/universal/identity.py::deterministic_id` | P4 | `(kind, namespace, natural_key)` | LOCATED (MECH-EPIC001) |
| 4 | `engine/uckp/identity.py::UniversalIdentity.mint` | P4 | URN `(namespace, local_name)` + UUIDv5 | LOCATED (MECH-UCKP) |
| 5 | `engine/knowledge/ukip/contracts.py` | P1 | digest of substance | LOCATED (MECH-UKIP) |
| 6 | `platform/foundation/durable_identity.py::IdentityMint` | P2 | `AdmissionKey(authority_id, local_key)` | LOCATED — the *only* AIF-L02-conformant minter in the repository |
| 7 | `engine/kernel/identity.py::mint` | P4 | `(metatype, namespace, natural_key)` | **UNLOCATED** — not in the plane crosswalk |
| 8 | `platform/universal_pipeline/identity.py::mint` | P4 | `{kind, ordered parts}` | **UNLOCATED** |
| 9 | `intelligence/kernel/ids.py::artifact_id`; `platform/foundation/identity.py::Principal.create`; `platform/universal_control_plane/{intelligence,prompt,ontology}.py` | P4 | tuple digests | **UNLOCATED** — and #9's first three squat the `UCOS-` prefix with code spaces (`PRIN`, `RSRC`…`CITE`, `MET`, `PRG`, `PRM`) that the single `_KIND_CODES` authority cannot parse |

**Finding A-1.** `parse_kind_name("UCOS-PRIN-<16hex>")` raises `RegistrationValidationError`, and `is_well_formed` returns `False`. Identifiers exist in the `UCOS-` namespace that the `UCOS-` namespace authority rejects. This is the concrete form of "duplicate identity authority" the objective requires eliminating.

**Finding A-2.** `intelligence/kernel/ids.py:119` spells out `hashlib.sha256(canonical_json(...).encode("utf-8")).hexdigest()` inline instead of calling `content_hash`. Byte-identical today; a latent fork the moment the canonical profile versions.

**Finding A-3.** The repository already knows how to prohibit hidden minting: `engine/uicm/validation.py:57` AST-scans its own package for `_FORBIDDEN_MINTS = ("deterministic_id", "mint", "uuid4", "uuid5", "identity_tuple")` and fails closed if an exemption disappears. The probe exists; its scope is one package.

## 1.3 Existing identity grammars

Grammar is declared *by pointer*, not by literal, and this is already enforced. `00-MASTER/UIS-001/uis_engine.py:256-262` resolves `properties.universal_id.pattern` out of `00-BOOK/SCHEMAS/artifact.schema.json` and raises `FailClosed("the declared identity grammar does not resolve in its owner")` if the pointer misses; line ~1621 fails the engine if the grammar *literal* appears in the engine's own source.

| Plane | Grammar | Owner |
|---|---|---|
| P2 artifact | `^UCOS-[A-Z][A-Z0-9]{1,11}-[0-9]{6}$` | `00-BOOK/SCHEMAS/artifact.schema.json:20` |
| P2 durable | `urn:ucos:p2:<authority>:<32 hex>` | `platform/foundation/durable_identity.py:57-64` |
| P3 pages | `^UPN-[0-9]{9,}$` | `00-BOOK/SCHEMAS/page.schema.json:11` |
| P3 edges | `^UEDGE-[0-9]{9,}$` | `00-BOOK/SCHEMAS/relationship.schema.json:11` |
| P3 signals | `^USIG-[0-9]{9,}$`, runs `^URUN-[0-9]{9,}$` | `00-BOOK/SCHEMAS/signal.schema.json:8,29` |
| P4 registry | `UCOS-<CODE>-<12 hex>`; ns `^[a-z0-9]+(?:-[a-z0-9]+)*(?:\.…)*$`; key `^\S+$`; ext code `[A-Z][A-Z0-9]{1,7}` | `engine/registry/universal/identity.py:32-45,178` |
| P4 UCKO | `urn:ucos:ucko:<ns>:<local>` + UUIDv5; ns `^[a-z0-9][a-z0-9._-]{0,62}$`; local `^[A-Za-z0-9][A-Za-z0-9._-]{0,190}$` | `engine/uckp/identity.py:39-50` |
| P4 UMK | `UMK-<SLUG>-<12 hex>` | `engine/kernel/identity.py:31-37` |
| P4 UAPF | `UAPF-<KIND>-<20 hex>` | `platform/universal_pipeline/identity.py:50-55` |
| Types | `^[A-Z][A-Za-z0-9]*(-[A-Z][A-Za-z0-9]*)*$` — explicitly OPEN, append-only | `00-BOOK/SCHEMAS/relationship.schema.json:26` |

**Finding G-1.** The relationship *type* vocabulary is already correctly architected: open, append-only, "a new relationship type is a new value, never a rewrite." The relationship *identity* is not. The same file gets both right and wrong in adjacent fields.

**Finding G-2.** The artifact-plane grammar's `[A-Z0-9]{1,11}` category segment is load-bearing and already saturated: namespaces are derived from path stems truncated to `DERIVED_CATEGORY_MAXLEN = 6` (`00-BOOK/tools/config.py:494`), producing nine colliding truncation windows (`ARCHIT`, `CANONI`, `DEPEND`, `EVOUSI`, `EXECUT`, `IAC001`, `READIN`, `REPOSI`, `WAVE01`) and the pinned `UIL-16 ≤ 17` partition-ambiguity bound. A width baked into a regex is a ceiling.

## 1.4 Existing validation mechanisms

Three independent, already-wired layers.

- **Structural / schema** — `00-BOOK/tools/ukb.py::cmd_validate` (1815-1919): duplicate `universal_id` (UIL-03), page-range overlap and inversion, referential integrity of `parent` and every `dependencies[]` (UIL-09), lineage-projection consistency, relationship-type correctness, then `jsonschema.validate` of every artifact against `artifact.schema.json` — the point at which the grammar is enforced per record. Exit 1 on any defect.
- **Admission / registration** — `cmd_enforce` (1987-2118), `--pre` (every eligible-unregistered file must be valid and classifiable *before* minting) and post (parity). Buckets: `invalid`, `unclassified`, `unreconciled`, `unregistered`. Writes an append-only audit record and exits 1.
- **Conformance measurement** — `00-MASTER/UIS-001/uis_engine.py`, reading grammar by pointer and accumulating `grammar_failures`, `attribute_coupled`, `renumbered`, `collisions`, `unresolvable`, `history_breaks`. Proves a mechanism exists by *source text* (`symbol_present`), never by import. Self-guards: `--check-no-identity-minting`, `--check-no-enumeration`, `--check-determinism`, `--check-record-immutability`, `--check-bounds-tight`, `--check-no-authority`.
- **CI** — `.github/workflows/ucos-registration-gate.yml` (eligibility → `enforce --pre` → `register.sh --observe`) and `.github/workflows/uis-gate.yml` (all self-checks → identity-conformance gate).

**Finding V-1.** Validation is single-grammar where the architecture is five-plane. A P4 identifier (`UCOS-SVC-a1b2c3d4e5f6`) does not satisfy the P2 artifact regex — correctly, by design — but any validator that applies the artifact grammar universally will report a false failure. Validation must be *plane-resolved*: which grammar applies is a function of the identifier's declaring authority, not a global constant.

## 1.5 Existing deterministic identity mechanisms

- **Pure minting.** All seven content-derived generators are pure: no wall clock, no RNG, no network, no global allocator. Re-minting is idempotent. Each has a self-check (`verify` / `reproduces` / `is_well_formed` / `require_intact`) that fails closed on a hand-built identifier.
- **Mint is opt-in.** `allocate(..., mint=False)` returns `None` rather than consuming a sequence number (`ukb.py:894-895`); the caller records the path in `unminted[]`. Identity is born by intent, never discovered by a checker.
- **Idempotent re-declaration.** `allocate_execution` keys by a stable execution key; `record_snapshots` (313-341) appends only when the 5-tuple `(content_hash, version, status, path, name)` differs from `history[uid][-1]`, so an unchanged rebuild appends nothing.
- **Stamp-neutral write suppression.** `_stamp_eq_json` (`ukb.py:74-105`) neutralizes generation stamps across the union of both documents' stamps before comparing, so a no-op rebuild does not rewrite files. This is `UKB-ADV-INV-07`.
- **Prepare/Commit/Abort.** `IdentityRegistry` (`platform/foundation/durable_identity.py:257-561`) realizes AIF-L13: mints provisional until seal, abort discards with no orphan identity, commit is idempotent, `retire()` guarantees a retired key is never re-minted, `_guard_opaque` rejects an opaque already bound to a different admission key.

**Finding D-1.** Two determinisms exist and are correctly separated in the P2/P4 code: *recorded* determinism (an identity is replayable because it was written down) and *derived* determinism (a value is reproducible because it is a pure function). AIF-L20 forbids mixing them. The mixing violation is not in the identity modules — it is in relationship identity (§1.11).

## 1.6 Existing digest algorithms

**One algorithm in every production path.** Across ~130 non-vendored `hashlib` call sites there is no MD5, no SHA-1 (outside RFC-4122 UUIDv5), no BLAKE2. `sha3_256` and `sha512` appear only as *registered* algorithms in the agility layer.

**Three competing canonicalization profiles:**

1. **Layer Zero** — `engine/uckp/canonical.py`: `DIGEST_ALGORITHM = "sha256"`, `CANONICAL_PROFILE = "ucos-uckp-canonical-json/1.0.0"`, `json.dumps(payload, sort_keys=True, separators=(",",":"), ensure_ascii=False)`, untruncated 64 hex. Declared as the single primitive; non-duplication enforced by AST probe (`engine.uckp.validation.ConstitutionalValidator._probe_zero_duplication`).
2. **Engine-local pretty** — every `00-MASTER/*/…_engine.py` redefines `canonical_json = json.dumps(..., indent=2, sort_keys=True, ensure_ascii=False) + "\n"` and digests *that* (`rib_engine.py:264`, `uccep_engine.py:176`, `ucda_engine.py:164`, `ucef_engine.py:253`, `aee_engine.py:143`, `uei_engine.py:165`, `uer_engine.py:145`, `urrc_engine.py:192`, `rfp_engine.py:88`).
3. **Ad-hoc `sort_keys` only** — the UAKOS phase engines: `sha256(json.dumps({...}, sort_keys=True).encode())`, default separators, `ensure_ascii=True` (`phase2_recon.py:465`, `phase3_engine.py:570`, `phase4_plan.py:608`, `phase5_gov.py:502`, `cert_engine.py:448`, `final_closure_engine.py:465`, and ~7 more). Of 77 `sort_keys=True` occurrences in `00-MASTER`, only 41 also set `ensure_ascii`.

**Six truncation widths in force:** 8 hex (ACEE/UCL `semantic_id` suffixes) · 12 hex (all identity digests: registry, kernel, intelligence, control-plane, `UGA-AUD`, `UICM-OBS`, `UCKO-CAP`) · 16 hex (`UCOS-PRIN`, `uar_engine seal`, control-plane ontology) · 20 hex (UAPF) · 32 hex (P2 opaque) · 64 hex (everything else).

**Algorithm agility exists in code and is absent from data.** `platform/foundation/crypto_agility.py` implements exactly the required mechanism: self-describing `Multihash` (`algorithm:value`, separator `:`) representable even for an algorithm this runtime cannot compute; `DigestSet` carrying several multihashes over the *same* canonical bytes, sorted, tagged with the CCF `profile_id`, widening append-only via `rolled_over()`; `AlgorithmRegistry` with strength-ranked deterministic `negotiate()`, `rollover()` requiring a named witness, and `deprecate()` refusing to leave zero active algorithms. `platform/foundation/canonical.py:200-256` defines `CanonicalDigest{profile_id, algorithm, value, byte_length}` whose `verify()` compares all three.

**Finding H-1 (the fixed digest ceiling, precisely).** No `content_hash`, `digest`, `entry_hash`, `previous_hash`, `seal_sha256` or `content_sha256` value in any data file carries an algorithm tag. Census: `content_hash` ×3 905, `previous_hash` ×467, `entry_hash` ×467, `content_hash_withheld` ×400, `digest` ×241, `evidence_digest` ×200, `content_sha256` ×84, `sha256` ×65, `seal_sha256` ×32 — all bare 64-hex. Exactly two files record an explicit algorithm (`acee-declaration.json:785`, `ucl-declaration.json:634`, both `"algorithm": "sha256"`). The only `sha256:`-prefixed strings in the tree are OCI image references. Agility therefore survives only as *field-naming convention* (`content_sha256`), so a rollover today would require renaming fields at every one of ~130 sites. `DigestSet.to_dict()` is written by no production path.

**Finding H-2.** The field name `content_hash` means *raw file bytes* in `ukb.py`/`uga_engine.py` and *canonical JSON text* in the `00-MASTER` engines. A digest read from the corpus can name neither its algorithm nor its canonicalization profile, so replay requires knowing which engine produced it. This is an undocumented identity/verification rule.

## 1.7 Existing ledger model

`00-BOOK/DATA/id-ledger.json` is RECORDED truth with exactly two writers — `ukb.py::_dump_json` (lines 1279, 2344, 2361) and `uga_engine.py:1869` — and fail-closed readers (`aee_engine.py:1602-1613`, `rib_engine.py:3554-3567`, `ukbx.py:1009`, `engine/lineage/query.py:82-86`) that resolve their own key and return `None` rather than mint.

Invariants, enforced live by `ukbx.py::_certify_domains` (1005-1035) and projected into `00-BOOK/DATA/certification.json`: no duplicate universal ID (1 233 unique) · no overlapping page ranges · `page_cursor >= max(page_end)` (9 826 = 9 826) · every artifact present in `by_path` · snapshot `seq` monotonic and append-only (1 264 histories).

There is **no JSON Schema for the ledger**; its schema is defined solely by `load_ledger()` defaults and the allocator. `first_seen` is non-uniform: ISO-8601 UTC in `by_path`/`discovered_volumes`, `commit:<12-hex>` in `by_object`/`by_observation`.

A second, structurally different ledger exists for certification: `engine/certification/ledger.py`, Merkle-style hash-chained with `GENESIS_HASH = "0"*64`, `entry_hash = content_hash({sequence, certification_id, record_sha256, prev_hash})`, `verify()` walking sequence/prev/recomputed-hash, append-only with no update or delete, in-memory only (DP-03).

**Finding L-1.** The identity ledger is a *flat append-only map*; AIF-L08 ratifies a *Merkle-linked, mergeable event DAG* where branches and merges are first-class. The DAG-ledger shape already exists and is proven in `engine/certification/ledger.py`. The gap is that the identity ledger has not adopted the chain the certification ledger demonstrates — not that the mechanism is missing.

## 1.8 Existing replay model

- **Canonical equality test** — `digests_match` (`engine/uckp/canonical.py:69-71`).
- **Byte-for-byte double build** — `engine/determinism/reproduce.py`: `double_build` compiles the same blueprint twice into `env-a`/`env-b` under `hermetic_env()` with `verify_toolchain()`, compares five categories (`generated_source`, `manifests`, `sbom`, `signatures`, `publication_payloads`), asserts `artifact_id_a == artifact_id_b`, and **forces a category with no files to `False`** so an empty build cannot pass by vacuity. Signing determinism via a fixed fixture key; production uses `env://` refs. Gate: `.github/workflows/determinism.yml`, evidence uploaded `if: always()`.
- **Replay obligation with non-vacuity** — `engine/uaue/gate.py`: `UAUE-GATE-05` runs every candidate twice and requires identical `digest()`, identical `run_id` and the same settlement round count; **an empty candidate set is a FAIL**. `replay_drift` compares committed files as *bytes* against `canonical_json(projection) + "\n"` — "a projection that only matches after normalisation is a projection nobody is holding to."
- **Multi-dimensional lifecycle replay** — `lifecycle_closure_engine.py::phase5_replay` measures 8 identity dimensions per round (`output_identity`, `registry_identity`, `dictionary_identity`, `knowledge_identity`, `bookkeeping_identity`, `lineage_identity`, `chain_head`, `chain_intact`) and emits `REPLAYABLE | NOT_REPLAYABLE`.
- **State round-trip replay** — `platform/universal_master_plan/master_plan_replay.py` reconstructs plans from a hash-chained fsync-appended `DurableJournal` and proves `reconstruct(journal).plan_id == plan.plan_id`.
- **Replay tiering** — AIF-L19 / A/G3 ratify eight classes: Historical, Bit, Generator, Registration, Certification, Repository, Execution, Semantic/Civilization.

**Finding R-1.** Replay verification is mature and fail-closed-on-vacuity. What it does not yet cover is *identity replay as a first-class tier*: re-deriving every recorded identifier from its recorded admission key and asserting equality. The primitives (`DurableIdentity.verify`, `IdentifierEntry.reproduces`, `IdentityRegistry.fingerprint`) all exist per-object; no gate composes them corpus-wide.

## 1.9 Existing certification model

Three stacks, all append-only and content-addressed.

- **Corpus / digital twin** — `00-BOOK/tools/ukbx.py::cmd_certify` → `00-BOOK/DATA/certification.json`: 10 domains (`identity`, `registry`, `traceability`, `knowledge_graph`, `change_intelligence`, `version`, `lineage`, `synchronization`, +2), `verdict = CERTIFIED` iff all pass, exit 1 on failure, append-only audit run with fingerprint dedup. Explicitly non-terminal: "certification closes scope, never evolution."
- **EC-1 engineering** — `engine/certification/`: `CertificationRecord` frozen and self-verifying (`_core()` excludes the id and the hash; `create()` derives both, so identical determinations produce an identical id); hash-chained ledger; `build_program_closure` refuses to build over a tampered ledger and computes A10 live (FAIL on empty ledger, failed verify, or any non-`CERTIFIED` entry); `closure_sha256` over a report core containing no wall clock, so the same ledger yields a byte-identical closure. `integrity.py` adds seven check families with a fail-closed severity split.
- **Certification duality** — AIF-L21: immutable Historical Attestation (RECORDED) vs recomputed Current Status (DERIVED), in distinct stores.

**Finding C-1.** Certification capability is present and does not need extension — it needs an *identity domain that certifies the identity architecture itself*, not only the artifact-plane invariants the `identity` domain currently checks (uniqueness + page ranges).

## 1.10 Existing identity laws

**Constitutional (AIF-L01…L24, six Books, ratified, authority-neutral).** Book I truth & identity: L01 bifurcation of truth · **L02 opaque durable identity (P2): minted-once, immutable, opaque, authority-namespaced; never content/order/path-derived; never reused** · L03 five orthogonal planes · **L04 witnessed non-recomputable ordinal (P3): recorded at mint, rendered, never recomputed from the file set, never globally monotonic** · **L05 content digest over CCF (P1): verifies, never identifies** · L06 path-independent admission key · **L07 authority-namespaced uniqueness: global uniqueness by construction, no global coordination** · L08 Merkle-linked mergeable event DAG ledger · L09 authority = serialization domain · L10 genesis & trust · L11 signed events & custody · L12 machine-computed recorded ACT boundaries · **L13 prepare/commit/abort atomicity: no orphan identity** · L14 atomic admission · L15 declared-intent transitions · L16 deterministic identity decision, ambiguity fails closed · **L17 forward-only compensation: no deletion or edit of Recorded Truth; retired identities never reissued** · L18 derivation purity & version stamp · L19 replay tiering · **L20 non-mixing of determinisms** · L21 certification duality · **L22 crypto-agility: algorithm-tagged multihash digest sets, witnessed rollover, deprecation only post-rollover, identity opaque and survives algorithm breakage** · L23 privacy via crypto-erasure · **L24 substrate neutrality: CCF / algorithm / id-width / encoding are pinned parameters that widen append-only**.

Gap-resolution appendices A/G1…A/G14 + A/G-AUTH are ratified, including **A/G7 Genesis-Adoption: a one-time event that imports and grandfathers the existing corpus with frozen ordinals.**

**Conformance (UIL-01…UIL-20, `00-MASTER/UIS-001/02-IDENTITY-LAW-BINDING-REGISTER.md`),** each bound to a measurable counter: UIL-01 `identities_absent`=0 · UIL-02 `identities_multiple`=0 · UIL-03 `identity_collisions`=0 · UIL-04 `identities_altered`=0 · UIL-05 `identities_reused`=0 · UIL-06 `identities_renumbered`=0 · UIL-07 `identities_attribute_coupled`=0 · **UIL-08 `identities_unresolvable` ≤ 6 (measured 6)** · UIL-09 `references_unresolvable`=0 · UIL-10 `identities_untraceable`=0 · **UIL-11 DECLARED-NOT-MEASURABLE** · UIL-12 `lifecycle_states_undeclared`=0 · UIL-13 `history_not_append_only`=0 · UIL-14 `identities_unverifiable`=0 · UIL-15 `identity_records_with_secret_field`=0 · **UIL-16 `namespace_partition_ambiguities` ≤ 17 (measured 17)** · UIL-17 `identity_records_claiming_authority`=0 · UIL-18 `identities_renumbered`=0 · **UIL-19 `identities_failing_declared_grammar`=0** · UIL-20 `capabilities_created`=0.

**Finding X-1.** The two non-zero bounds are not debt. UIL-05/06/13 and AIF-L17 forbid deleting or renumbering recorded identity, so 6 unresolvable and 17 ambiguous partitions are *preserved history* and must remain in the architecture permanently as bounded, declared, non-repairable readings.

**Finding X-2.** The law already says everything the objective requires. Every mandatory requirement in the objective maps to a ratified law (Part 3). The architecture question is therefore not *what* but *where the law is not yet the mechanism*.

## 1.11 Relationship identity — the acute case

`00-BOOK/DATA/relationships.json` holds 13 361 edges of shape `{edge_id, from, to, type, inverse_of, note}`. Identity is minted at `00-BOOK/tools/ukb.py:1020-1032`:

```python
edges = []
edge_seq = [0]
...
def add_edge(src, dst, etype, note="", inverse_of=None):
    ...
    edge_seq[0] += 1
    eid = f"UEDGE-{edge_seq[0]:09d}"
```

`edge_seq` is a **per-build, in-memory counter initialized to zero on every run**. An edge's identifier is therefore a function of the order in which the builder happened to emit it — structural chains first, then cross-program, then program-root parenting, then metadata edges. Edge identity is:

- **sequential** — `n+1`, the exact dependency the objective forbids;
- **positional** — determined by traversal position, not by the edge;
- **not recorded** — `id-ledger.json` has no `by_edge` map; nothing in the ledger binds `UEDGE-000013361` to a triple;
- **derived-but-treated-as-recorded** — the ID is regenerated each build, yet `inverse_of: "UEDGE-000013360"` is a *persisted cross-reference to a positional value*, and 18 430 `UEDGE-` references exist across the data files.

**Finding I-1 (severity: architectural).** This is a direct AIF-L20 violation: identity determinism (recorded) is being produced by generation determinism (derived). It holds today only because the traversal is deterministic. Insert one edge in the middle of `C.CHAINS`, and every subsequent edge silently re-identifies while every persisted `inverse_of` and every external `UEDGE-` reference silently re-points. The same file's relationship *type* field is correctly architected as an open append-only vocabulary; its *identity* field is the single worst-architected identifier in the repository.

---

# PART 2 — DETERMINATIONS A…J

## A. Universal identity ontology

**DETERMINED.** The ontology is **generative over an open population space**, never enumerative. It has exactly four levels and no fifth is permitted.

```
LEVEL 0  PLANE          — closed at five (AIF-L03). P1 verifies · P2 identifies ·
                          P3 renders · P4 names · P5 binds. Orthogonal,
                          non-substitutable, crosswalked, never merged.

LEVEL 1  AUTHORITY      — open, append-only. AuthorityID namespaces every key.
                          One authority per (plane × population). Uniqueness by
                          construction (AIF-L07); no global coordination (AIF-L09).

LEVEL 2  POPULATION     — open, append-only. A PopulationCode admitted through
                          register_kind(). NOT an enum edit, NOT a schema edit,
                          NOT a new engine, NOT a new registry.

LEVEL 3  MEMBER         — one durable identity per member, keyed by
                          AdmissionKey(AuthorityID, local-key). Minted once.
                          Opaque. Never reused, never renumbered, never released
                          by retirement.
```

The nine populations named in the objective — entities, relationships, knowledge objects, capabilities, authorities, laws, artifacts, executions, observations — are **Level 2 instances, not Level 0 or 1 concepts**. They receive no special treatment whatsoever. "Future unknown populations" is satisfied by construction: the ontology never names a population, so it can never fail to name one.

Mechanism reused: `RegistryKind` + `register_kind` / `_EXTENSION_KIND_CODES` (`engine/registry/universal/identity.py:45-199`) for Level 2; `AdmissionKey` (`platform/foundation/durable_identity.py:67-99`) for Level 3; the UIS-001 plane crosswalk for Level 0; `AuthorityID` for Level 1.

**Corollary A-i.** Authorities and laws are populations *and* Level-1 concepts simultaneously. The recursion terminates because an authority's own identity is minted by its *parent* authority, rooted at the Genesis self-signed anchor (AIF-L10). This closes UIL-11 ("UIS internal constructs also possess UIDs"), currently the only DECLARED-NOT-MEASURABLE law.

**Corollary A-ii.** Nothing is a special case. Relationships are a population. Observations are a population. Executions are a population. Certifications are a population. The objective's prohibition on special-case identity is satisfied by the ontology having no place to put one.

## B. Identity authority model

**DETERMINED.** **Federated, single-authority-per-cell, with the authority named in the identifier.**

- One **cell** = (plane, population). Exactly one authority mints into a cell. Two authorities in one cell is the definition of duplicate authority.
- The AuthorityID is **carried in the identifier** (`urn:ucos:p2:<AuthorityID>:<opaque>`), so uniqueness needs no registry lookup and no global lock. Branch, merge, offline operation, org split and org merge preserve uniqueness with zero coordination (AIF A/G1).
- An authority is a **serialization domain** (AIF-L09): it totally orders its own events. Under partition it blocks minting or delegates a sub-namespace — it never guesses.
- **Prepare/Commit/Abort** is the only admission protocol (AIF-L13). Provisional until seal; abort discards with no orphan or burned identity; commit is idempotent; retirement is permanent and never releases the value.

Mechanism reused: `IdentityRegistry.prepare/commit/abort/mint/retire/adopt/verify/fingerprint` and `_guard_opaque` (`platform/foundation/durable_identity.py:257-561`) — already the complete authority implementation. `ukb.py`, `uga_engine.py`, `register_kind` and the UIS-001 crosswalk supply the located cells.

**Determination B-1 — the nine minting sites resolve without deletion.** Sites 1-6 are plane-located and remain. Sites 7-9 are the same *function* applied in unlocated cells: each converges by (a) declaring its plane and authority in the UIS-001 crosswalk, (b) registering its code space through `register_kind`, and (c) delegating its digest to `content_hash`. `UCOS-PRIN`, `RSRC`…`CITE`, `MET`, `PRG`, `PRM` become registered codes; none is renamed, none is renumbered, no compatibility layer is introduced.

**Determination B-2 — hidden generators are eliminated mechanically, not by policy.** Generalize the existing probe: `engine/uicm/validation.py:57` `_FORBIDDEN_MINTS` with its measured exemption list is the pattern. Scope it repository-wide. Any module that constructs an identifier without delegating to a located authority fails the gate. A prose prohibition on hidden minting is exactly the kind of claim that quietly stops being true.

## C. Identity grammar model

**DETERMINED.** **Grammar is data, resolved by pointer, versioned by profile, one per cell — never a literal in code.**

```
GRAMMAR := ⟨ plane , authority_id , population_code , profile_id , pattern ⟩
```

- The **pattern is owned by exactly one file** and read by pointer. Already enforced: `uis_engine.py:256-262` resolves `properties.universal_id.pattern` from its owner and fails closed on a missing pointer; line ~1621 fails the engine if the literal appears in its own source.
- Grammar evolution is a **new `profile_id`**, never a rewrite. `profile_id` widens append-only (AIF-L24). Existing identifiers remain valid under the profile in force at their mint epoch — which is precisely what UIL-19 measures (`identities_failing_declared_grammar` = 0) and what makes "scheme evolution never changes a UID" (UIL-06) mechanically true.
- **Validation resolves the grammar set, not a grammar.** An identifier is well-formed iff it satisfies the pattern of *its declaring cell's active profile*. Applying one plane's grammar to another plane's identifier is a validator defect, not an identifier defect.

Mechanism reused: `artifact.schema.json` (P2 grammar owner) · `config.py` (P3 nomenclature owner) · `engine/registry/universal/identity.py` and `engine/uckp/identity.py` (P4 owners) · `engine/context/taxonomy.py` (P5 owner) · `uis_engine.py` pointer resolution · `CANONICAL_PROFILE` / `CCF_DEFAULT_PROFILE` as the profile-version precedent.

**Determination C-1 — the enumerative artifact grammar is the ceiling to remove.** `^UCOS-[A-Z][A-Z0-9]{1,11}-[0-9]{6}$` hard-codes three limits at once: category width 11, ordinal width 6, and ordinal *form* (decimal, therefore sequential). Under this determination all three become pinned parameters of the P2/P3 profile. The pattern is not rewritten to be looser; it is **superseded by a versioned profile whose parameters are declared**, with the current pattern preserved verbatim as the frozen profile of the Genesis epoch. This is why no migration table is required: the old grammar is not replaced, it is *dated*.

## D. Identity validation architecture

**DETERMINED.** **Four tiers, each already implemented, composed and made plane-aware. Fail-closed at every tier. Non-vacuity mandatory.**

| Tier | Question | Mechanism (existing) |
|---|---|---|
| T1 Form | Does the identifier satisfy its cell's active grammar profile? | `jsonschema` in `ukb.py::cmd_validate`; `is_well_formed`; `parse_kind_name`; `Multihash.parse` |
| T2 Admission | Is the identifier bound to exactly one admission key, and that key to exactly one identifier? | `IdentityRegistry._guard_opaque`; `cmd_enforce --pre`; duplicate-UID check in `_certify_domains` |
| T3 Integrity | Does the identifier still equal the re-mint of its recorded key? | `DurableIdentity.verify`; `IdentifierEntry.reproduces`; `UniversalIdentity.require_intact`; `Identity.require_intact` |
| T4 Conformance | Do all twenty identity laws hold over the whole corpus, at declared bounds? | `uis_engine.py` measures + `uis-gate.yml` + `ucos-registration-gate.yml` |

**Determination D-1 — no vacuous pass.** The repository already refuses vacuity in three places: `compare_builds` forces a file-less category to non-identical (`reproduce.py:234-237`); `_replay_obligation` fails on zero candidates (`uaue/gate.py:331-334`); `certification_framework_status` fails on an empty ledger. Identity validation inherits this rule: an empty population, an unpopulated cell and an unmeasured law all FAIL. A grammar declared ahead of population (the nine zero-member prefixes) must be declared as *reserved*, not silently pass as satisfied.

**Determination D-2 — validation never mints.** `--check-no-identity-minting` and the `_FORBIDDEN_MINTS` probe are permanent architectural components, not test scaffolding. Identity is born by intent; a checker that can allocate is a second authority.

## E. Deterministic identity model

**DETERMINED.** **Identity is RECORDED and replayed. Every view over identity is DERIVED and recomputed. The two are never mixed (AIF-L20).**

```
RECORDED (immutable, append-only, never recomputed):
    admission key  ·  durable opaque value  ·  admission ordinal render
    mint epoch (profile_id, algorithm set, id-width)  ·  lifecycle events
    snapshot history

DERIVED (pure f(Source, Recorded Truth, Generator-version); stamped; no hidden
state, no wall clock — AIF-L18):
    every registry, projection, index, graph, report, status and page render
```

**Deterministic regeneration** therefore means: given the recorded ledger and a generator version, every derived view is byte-reproducible — *and no identity is allocated in the process*. Both halves are load-bearing. `mint=False` by default (`ukb.py:894-895`) is the mechanism that makes the second half true.

**Determination E-1 — the four-step decision is the only admission logic.** AIF-L16 / A/G2+G11: author-declared intent (version / copy / clone / fork / split / merge / supersede / replace / restore / new), machine-validated, ambiguity fails closed. No heuristic ever decides whether something is new. Content similarity never decides identity — P1 verifies, it does not identify (AIF-L05).

**Determination E-2 — identity replay becomes a declared tier.** AIF-L19's eight replay classes gain nothing new; *Registration* replay is instantiated as: re-derive every recorded identifier from its recorded admission key under its recorded epoch parameters, and require equality for all of them. The per-object primitives already exist (`verify`, `reproduces`, `require_intact`, `fingerprint`); the gate composes them, exactly as `uaue/gate.py` composes double-conduct into `UAUE-GATE-05`.

## F. Identity algorithm evolution model

**DETERMINED.** **Algorithm-tagged multihash digest sets, witnessed append-only rollover, deprecation only post-rollover — AIF-L22, realized by `platform/foundation/crypto_agility.py`, extended from code into data.**

```
DIGEST := DigestSet{ profile_id , [ Multihash{algorithm, value} , … ] }
          rendered self-describingly as  "<algorithm>:<value>"
```

Four rules:

1. **Every persisted digest names its algorithm and its canonicalization profile.** A bare hex string is not a digest; it is a digest whose meaning depends on knowing which of three profiles produced it (Finding H-2). `CanonicalDigest{profile_id, algorithm, value, byte_length}` (`platform/foundation/canonical.py:200-256`) is the record shape; its `verify()` already compares all three.
2. **Rollover widens the set; it never rewrites history.** `DigestSet.rolled_over()` appends a multihash over the *same* canonical bytes. `AlgorithmRegistry.rollover()` requires a named witness. `deprecate()` refuses to leave zero active algorithms. Historical bare digests are interpreted through the epoch parameter record that states the algorithm and profile in force when they were written — no re-hashing, no migration table.
3. **One canonicalization primitive.** Layer Zero (`engine/uckp/canonical.py`) is already declared sole and already probe-enforced (`_probe_zero_duplication`). Profiles 2 and 3 (§1.6) are un-declared forks of the primitive; they converge by delegation, and where a legacy digest was computed over pretty-printed text, that fact is recorded as the epoch's `profile_id` rather than corrected.
4. **Identity survives algorithm breakage because identity is opaque.** A P2 durable value is a *recorded opaque token*, not a live hash of anything. If SHA-256 breaks tomorrow, every durable identity remains valid, every admission key binding remains valid, and only *verification* migrates. This is the single most important consequence of AIF-L02's "never content-derived": it is what makes infinite algorithm evolution possible without touching one identifier.

**Determination F-1.** `Multihash` can *represent* a digest for an algorithm the local runtime cannot compute. Forward compatibility with unknown future algorithms is therefore already a property of the located mechanism, not an aspiration.

## G. Identity strength evolution model

**DETERMINED.** **Identity strength is a pinned parameter that widens append-only (AIF-L24). There is no ceiling because there is no literal.**

```
EPOCH := ⟨ profile_id , ccf_profile , algorithm_set , id_width , encoding ⟩
         recorded at mint · immutable · widens append-only
```

Current widths in force — 8, 12, 16, 20, 32, 64 hex — are **not a defect to unify; they are six epochs to declare.** Unifying them would renumber history, which AIF-L17 and UIL-05/06 forbid. Declaring them makes every existing identifier permanently interpretable and every future identifier free to be wider.

Three consequences:

1. **Widening is minting-forward only.** A new epoch mints wider values. Every previously minted value stays valid, stays resolvable and stays unchanged. Strength evolution therefore *cannot* invalidate history — which is exactly why it can be unbounded.
2. **The collision-resistance floor is stated, not assumed.** The 12-hex identity digest is ~48 bits, mitigated today only by per-kind namespacing. Under this determination each epoch *declares* its width and therefore its resistance, and the 32-hex P2 opaque (128 bits, `P2_OPAQUE_HEX_LEN = 32`) is the pinned default for durable identity. An implicit floor is an undocumented identity rule.
3. **Grammar cannot re-impose the ceiling.** Because width is a parameter of the profile (Determination C-1) and the grammar is resolved by pointer from the profile, a wider epoch needs no regex edit, no schema redesign and no compatibility layer.

## H. Historical preservation model

**DETERMINED.** **Genesis-Adoption plus forward-only compensation. Nothing is migrated, corrected, renumbered or deleted — ever.**

- **Adoption, not migration.** AIF A/G7 ratifies a one-time `Genesis-Adoption` that imports and grandfathers the existing corpus **with frozen ordinals**. The mechanism exists: `DurableIdentity.adopt()` (`platform/foundation/durable_identity.py:158-182`) preserves a historical opaque verbatim, marks `adopted=True`, and `verify()` short-circuits `True` for adopted identities. Adopted values are trusted by fiat (AX-02) precisely because recomputing them would renumber history.
- **Forward-only compensation (AIF-L17).** No deletion, no edit of Recorded Truth. A correction is a *new event*. A retired identity is never reissued — already implemented (`retire()`; and `uga_engine.py:306-308` retires vanished paths while retaining identity).
- **Bounded historical readings are permanent.** `identities_unresolvable ≤ 6` (UIL-08) and `namespace_partition_ambiguities ≤ 17` (UIL-16) are not debt and must never be "fixed": repairing them would require deleting or renumbering recorded identity. They are declared, bounded, measured, and preserved. `--check-bounds-tight` keeps them from silently loosening.
- **Append-only history everywhere.** Snapshot `seq` contiguous 1..n (UIL-13, `history_not_append_only` = 0); page space never reused; certification ledger hash-chained from `GENESIS_HASH` with no update or delete path.
- **Immutable historical truth is separated from current status (AIF-L21).** Historical Attestation is recorded and immutable; Current Status is recomputed. They live in distinct stores and cannot contradict each other, because one is not a claim about the other.

**Determination H-1.** The existing corpus is not a compatibility problem. It is the Genesis epoch. Every legacy shape — the 6-digit ordinals, the bare digests, the three canonicalization profiles, the six widths, the 74 ungoverned namespaces, the nine truncation collisions — is preserved as *what the Genesis epoch's parameters were*. This is the whole reason no migration table, exception or compatibility layer appears anywhere in this determination.

## I. Relationship identity integration model

**DETERMINED.** **A relationship is a population like any other. It receives no special-case identity, and its current identity mechanism is the one place the architecture is actively violated.**

Current state (Finding I-1): `UEDGE-%09d` from a per-build in-memory counter (`ukb.py:1020-1032`), assigned in traversal order, unledgered, yet persisted as a cross-reference in `inverse_of` and referenced 18 430 times.

Integration under the universal model, using only existing mechanisms:

1. **Population.** `RELATIONSHIP` already exists as a `RegistryKind` with code `REL` (`engine/registry/universal/identity.py:138`). No new population is created.
2. **Admission key.** An edge's local key is its own canonical content — the ordered triple `(from, to, type)` — under the one canonical primitive. Note what this is *not*: it is not a content digest used as identity (which AIF-L05 forbids). The triple is the edge's **admission key**, exactly as `(authority_id, local_key)` is an artifact's, because for a relationship the endpoints-and-type *are* the identity, not the content. `DurableIdentity.compute_opaque` already hashes the admission key and never the content, order or path.
3. **Durable identity.** `urn:ucos:p2:<AuthorityID>:<opaque>` — order-independent, build-independent, machine-independent, stable under insertion anywhere in the traversal. Re-minting is idempotent; `_guard_opaque` refuses to bind one opaque to two triples.
4. **The `UEDGE-NNNNNNNNN` render is preserved as a P3 admission ordinal.** AIF-L04: recorded at mint, rendered, never recomputed, never globally monotonic. All 13 361 existing renders are Genesis-Adopted with frozen ordinals via `adopt()`. Every one of the 18 430 existing references stays valid and keeps pointing at the same edge.
5. **`inverse_of` becomes a durable reference,** not a positional one — `durable_reference()` already exists for this.
6. **Recorded, not derived.** Edge identity moves from "regenerated each build" to "recorded once, replayed." This is the AIF-L20 fix: identity determinism stops being a side effect of generation determinism.

**Determination I-1 — no relationship exception.** The objective's "not relationship-specific" is satisfied structurally: every clause above is the general model with `population_code = REL` substituted. If any clause needed a relationship-only rule, the ontology would be wrong.

**Determination I-2 — the type vocabulary is already correct and is the template.** `relationship.schema.json:26` declares an OPEN, append-only TitleCase type pattern with the reasoning "a new relationship type is a new value, never a rewrite." That is exactly the treatment `PopulationCode` receives at Level 2. The repository already contains the right pattern; this determination applies it to identity.

## J. Remaining blockers to 100%

Eight. Every one is convergence onto an existing located mechanism. **None requires a new ledger, registry, authority or framework.** Listed in dependency order; severity reflects blast radius if left unclosed.

| # | Blocker | Evidence | Violates | Existing mechanism that closes it | Severity |
|---|---|---|---|---|---|
| **J1** | **Positional relationship identity.** `UEDGE-` minted from a per-build in-memory counter in traversal order; unledgered; 18 430 persisted references depend on traversal position. | `ukb.py:1020-1032`; `relationships.json` `inverse_of` | AIF-L02, L04, **L20**; objective's *sequential* + *positional* prohibitions | `AdmissionKey` + `IdentityMint` + `adopt()`; `REL` kind already registered | **CRITICAL** |
| **J2** | **Digests are algorithm-naked in data.** ~3 905 `content_hash` + ~467 `entry_hash` + ~467 `previous_hash` + 241 `digest` + 84 `content_sha256`, all bare hex. Only 2 files record an algorithm. `DigestSet.to_dict()` written by no production path. | §1.6 Finding H-1 | AIF-L22, L24; objective's *fixed digest ceiling* | `Multihash` / `DigestSet` / `AlgorithmRegistry`; `CanonicalDigest{profile_id, algorithm, value, byte_length}` | **HIGH** |
| **J3** | **Three canonicalization profiles.** Layer Zero (compact) vs engine-local (indent 2 + trailing newline) vs UAKOS ad-hoc (`sort_keys` only, `ensure_ascii` default). Same payload → three digests. `content_hash` means file bytes in one place and canonical JSON text in another. | §1.6 profiles 1-3; Finding H-2 | AIF-L18; UCKP Art. 3 zero duplication; objective's *undocumented identity rules* | Layer Zero + `_probe_zero_duplication` (probe exists, scope is `engine`/`platform`) | **HIGH** |
| **J4** | **Four unlocated minting sites.** `engine/kernel/identity.py`, `platform/universal_pipeline/identity.py`, `intelligence/kernel/ids.py`, `platform/foundation/identity.py` (+ control-plane `MET`/`PRG`/`PRM`) are absent from the plane crosswalk. `UCOS-PRIN` and 10 intelligence codes are unparseable by the `UCOS-` authority. `intelligence/kernel/ids.py:119` inlines `hashlib.sha256`. | §1.2 Findings A-1, A-2 | AIF-L07; objective's *duplicate identity authorities* + *hidden identity generators* | UIS-001 crosswalk declaration + `register_kind` + `content_hash` delegation | **HIGH** |
| **J5** | **Enumerative artifact grammar with three compiled-in limits.** `^UCOS-[A-Z][A-Z0-9]{1,11}-[0-9]{6}$` fixes category width, ordinal width and ordinal *form* (decimal ⇒ sequential). Nine truncation collisions; 74 of 109 namespaces ungoverned; nine prefixes declared with zero members. | `artifact.schema.json:20`; `config.py:494`; §1.3 Finding G-2 | AIF-L24; objective's *fixed ceiling* + *positional identity* | Versioned grammar profile resolved by pointer (`uis_engine.py:256-262`), current pattern frozen as the Genesis profile | **MEDIUM** |
| **J6** | **Flat identity ledger where the law ratifies a Merkle-linked mergeable DAG.** `id-ledger.json` is an unchained map with no JSON Schema; `first_seen` is non-uniform (ISO-8601 vs `commit:<hex>`); `by_execution` is documented in `load_ledger()` but absent from the file (0 executions). | §1.7 Finding L-1 | AIF-L08 | `engine/certification/ledger.py` hash chain (`GENESIS_HASH`, `entry_hash`, `verify()`) — the shape is proven in-repo | **MEDIUM** |
| **J7** | **No corpus-wide identity replay tier.** Per-object `verify` / `reproduces` / `require_intact` / `fingerprint` all exist; no gate re-derives every recorded identifier from its recorded key under its recorded epoch. Determinism gates cover build outputs, not identity. | §1.8 Finding R-1 | AIF-L19; objective's *replay verification* | Compose existing primitives the way `uaue/gate.py` composes `UAUE-GATE-05` (with its non-vacuity rule) | **MEDIUM** |
| **J8** | **UIL-11 DECLARED-NOT-MEASURABLE.** Reflexivity: identity-system internal constructs are not shown to possess identity. This is the last unasserted identity law. | `02-IDENTITY-LAW-BINDING-REGISTER.md` UIL-11 | UIL-11 | Corollary A-i: authorities are a population whose members are minted by their parent authority, rooted at Genesis | **LOW** |

**Not blockers — permanent by law:** `identities_unresolvable = 6` (UIL-08) and `namespace_partition_ambiguities = 17` (UIL-16) are preserved history under AIF-L17 / UIL-05 / UIL-06 / UIL-13 and must remain bounded and declared, never repaired (Finding X-1, Determination H-1).

---

# PART 3 — CONFORMANCE MATRICES

## 3.1 Mandatory requirements → mechanism

| Requirement | How the architecture provides it | Located mechanism | Law |
|---|---|---|---|
| Infinite identity populations | `PopulationCode` is an open append-only vocabulary; the ontology never names a population | `register_kind` / `_EXTENSION_KIND_CODES`, `engine/registry/universal/identity.py:157-199` | AIF-L03 |
| Infinite identity namespaces | `AuthorityID` namespaces every key; uniqueness by construction, no coordination | `AdmissionKey`, `IdentityRegistry`, `platform/foundation/durable_identity.py` | AIF-L07, L09 |
| Infinite identity algorithms | Self-describing `algorithm:value` multihash sets; witnessed append-only rollover; representable for uncomputable algorithms | `platform/foundation/crypto_agility.py` | AIF-L22 |
| Infinite identity strength | `id_width` is a pinned parameter widening append-only; opaque recorded values never recomputed | epoch record + `P2_OPAQUE_HEX_LEN`; `CanonicalDigest.byte_length` | AIF-L24 |
| Deterministic regeneration | Identity RECORDED and replayed; all views DERIVED as pure stamped functions; `mint=False` default | Layer Zero, `ukb.py:894-895`, `_stamp_eq_json`, `reproduce.py` | AIF-L18, L20 |
| Immutable historical truth | Append-only; forward-only compensation; retired never reissued; adoption with frozen ordinals | `retire()`, `adopt()`, `record_snapshots`, hash-chained certification ledger | AIF-L17, A/G7 |
| Replay verification | Eight ratified tiers; byte-identity harness; non-vacuity enforced; per-object integrity primitives | `reproduce.py`, `uaue/gate.py`, `phase5_replay`, `master_plan_replay.py` | AIF-L19 |
| Auditability | Every mint is a signed recorded event with lifecycle transitions and an audit universe | `IdentityRegistry` logging, `03-AUDIT-UNIVERSE.json`, `history`, change ledger | AIF-L11, L12 |
| Certification capability | Historical Attestation (recorded, immutable) vs Current Status (recomputed), distinct stores; hash-chained closure | `engine/certification/*`, `ukbx.py::cmd_certify`, `certification.json` | AIF-L21 |

## 3.2 Eliminations → mechanism

| Must eliminate | Elimination | Residual |
|---|---|---|
| Sequential identity dependency | Durable identity is a function of the admission key alone. No `n+1` anywhere. Sequential renders survive only as recorded P3 ordinals — rendered at mint, never recomputed, never globally monotonic (AIF-L04). | **J1** (edges), **J5** (decimal-form grammar) |
| Positional identity | No identifier is a function of emission order, traversal position, file-set membership or path. `compute_opaque` hashes the admission key and *never* content, order or path. | **J1** |
| Fixed digest ceiling | Width and algorithm are epoch parameters that widen append-only; digests are self-describing; old values interpreted through their epoch record, never re-hashed. | **J2**, **J5** |
| Duplicate identity authorities | One authority per (plane × population); AuthorityID carried in the identifier; plane crosswalk is the located register. | **J4** |
| Hidden identity generators | Repository-wide AST probe on forbidden mint symbols with a *measured* exemption list, plus `--check-no-identity-minting`. Mechanical, not prose. | **J4** |
| Undocumented identity rules | Grammar, algorithm, profile, width and authority are all declared data resolved by pointer; the conformance engine fails closed if a declaration does not resolve, and fails if it hard-codes a grammar literal. | **J2**, **J3**, **J6** |

## 3.3 Prohibitions honoured by this determination

| Prohibition | Compliance |
|---|---|
| No patch / exception / special case | Every determination is the general model. §I is the general model with `population_code = REL`. |
| No migration table | Genesis-Adoption freezes existing values in place; nothing moves, so nothing needs mapping. |
| No compatibility layer | Legacy shapes are dated as the Genesis epoch's declared parameters, not translated. |
| No new identity ledger | `id-ledger.json` remains the sole recorded identity store; J6 chains it, does not replace it. |
| No new registry | No registry proposed. `register_kind` extends the existing code space. |
| No new authority | Authorities are *located*, not created. J4 declares four existing sites; it mints none. |
| No parallel identity framework | Every mechanism cited exists at a stated path. The determination adds zero mechanisms. |
| Do not implement | No code, data or configuration was written. This artifact is the only file created. |

---

# PART 4 — BOUNDARY, TRACEABILITY, DETERMINATION

## TRACEABILITY REGISTER
All links are navigational and analytical. No referenced determination, frozen artifact, ledger, registry or data file was altered.

| Link | Target | Relationship |
|---|---|---|
| Identity law | `02-MASTER/UCOS-Ω∞-ABSOLUTE-IDENTITY-FEDERATION-AND-CONTINUITY-CONSTITUTION.md` | Governed-By (AIF-L01…L24, A/G1…A/G14) |
| Identity architecture of record | `07-ENGINEERING/UCOS-Ω∞-UNIVERSAL-IDENTITY-SYSTEM-MASTER-ARCHITECTURE.md` (ENG-001) | Depends-On |
| Identity conformance | `00-MASTER/UIS-001/` (02 law-binding · 03 plane-and-grammar · 04 ledger-measurement) | Reads |
| Artifact-plane grammar owner | `00-BOOK/SCHEMAS/artifact.schema.json` | References (read-only, by pointer) |
| Recorded identity store | `00-BOOK/DATA/id-ledger.json` | References (read-only) |
| P2 durable identity mechanism | `platform/foundation/durable_identity.py` | References |
| Crypto agility mechanism | `platform/foundation/crypto_agility.py` | References |
| Canonical primitive (Layer Zero) | `engine/uckp/canonical.py` | References |
| Registration transaction | `00-BOOK/tools/register.sh` (REG-AUTO-001 / UMB-IMP-001) | References |
| Realization architecture | UMB-003 / 004 / 005 / 008 / 009 / 010 | References |
| Superior frozen authority | STATUS-001, REG-AUTO-001, UCI-001, AUTH-INF-001 | Read-only superior authority; never altered |

## AUTHORITY BOUNDARY (MANDATORY)
This artifact holds no constituent, governance, ratification, certification or execution authority. It creates no engine, no registry, no ledger, no identifier namespace, no volume and no lifecycle. It allocates no identifier and mints no identity. It amends no constitution and supersedes no determination. It treats `00-SOURCE/`, `99-FREEZE/`, `00-BOOK/DATA/`, `engine/`, `platform/` and all program registers as read-only. It embeds no secret, credential or key material. It is subordinate to the frozen constitutional corpus, to AIF, to ENG-001, and to every superior determination. Where it conflicts with a located instrument, it is void to the extent of the conflict.

## DETERMINATION

- **A. Is a permanent universal identity architecture determinable from existing mechanisms?** **YES.** Four ontology levels, five closed planes, one generative mint function, three pinned-parameter registers (grammar profile · algorithm set · id width). Every component is located at a stated path. No mechanism was invented.
- **B. Does it support infinite evolution across all named populations and future unknown ones?** **YES** — because populations are never enumerated. Entities, relationships, knowledge objects, capabilities, authorities, laws, artifacts, executions and observations are Level-2 instances of one model; an unknown future population is a registration.
- **C. Does it satisfy all nine mandatory requirements?** **YES in architecture** (§3.1), with eight convergence blockers open in realization (§J).
- **D. Does it eliminate all six prohibited properties?** **YES in architecture** (§3.2). Residual realization defects: sequential/positional identity survives in relationship edges (J1) and in the decimal-form artifact grammar (J5); the digest ceiling survives in algorithm-naked persisted digests (J2, J5); duplicate authorities and hidden generators survive in four unlocated minting sites (J4); undocumented rules survive in three canonicalization profiles and the unschematized ledger (J2, J3, J6).
- **E. Does it require a new ledger, registry, authority or parallel framework?** **NO.** All eight blockers close by converging onto mechanisms that already exist in the repository.
- **F. Does it require a migration, patch, exception or compatibility layer?** **NO.** Genesis-Adoption with frozen ordinals preserves every existing identifier in place. Legacy shapes are dated, not translated.
- **G. Is the architecture closed at 100% today?** **NO.** Blockers J1…J8. J1 is critical: relationship identity is currently positional, unledgered and cross-referenced 18 430 times, and is the one active AIF-L20 violation.

## CERTIFICATION

| Attribute | Value |
|---|---|
| Artifact status | ACTIVE — determination of record |
| Verdict | ARCHITECTURE DETERMINED · NOT YET CLOSED (8 blockers) |
| Populations analysed | 5 ledger maps · 17 declared schema populations · ~247 observed prefix families · 109 live categories |
| Authorities analysed | 9 minting sites (6 located, 4 unlocated) |
| Grammars analysed | 10 across 5 planes |
| Laws read | 24 constitutional (AIF-L01…L24) + 20 conformance (UIL-01…UIL-20) |
| Mechanisms created | **0** |
| Files created | **1** (this artifact) |
| Files modified | **0** |
| Authority | **NONE** |

*Return: [Absolute Identity, Federation & Continuity Constitution](02-MASTER/UCOS-Ω∞-ABSOLUTE-IDENTITY-FEDERATION-AND-CONTINUITY-CONSTITUTION.md) · [Master Index](02-MASTER/UCOS-Ω∞-CONSOLIDATION-PROGRAM-MASTER-INDEX.md) · [Master Knowledge Book](00-BOOK/UCOS-BOOK-000000-UNIVERSAL-MASTER-KNOWLEDGE-BOOK.md)*

**END OF ARTIFACT — UNIVERSAL IDENTITY EVOLUTION ARCHITECTURE DETERMINATION · ANALYSIS ONLY · NO IMPLEMENTATION · AUTHORITY-NEUTRAL**
