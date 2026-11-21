# UCOS Ω∞ IMPLEMENTATION GAP REGISTER

**Checkpoint:** `03179308` (integration/recovery-001)
**Compiled:** 2026-08-21, companion to `UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md`
**Scope:** Full detail on every requirement **not** classified `CERTIFIED` — 13 of 49 tracked requirements. No implementation performed in this pass.

---

## GOVERNED CLOSURE (5)

Approved decision exists (`DEC-ADR-0019`, `WP-UCDA-028`, except where noted); implementation intentionally pending.

### REQ-02 — Entity supersession history not field-level reconstructible
- **Owner:** CEU-001. **Authority:** `engine/ceu/existence.py`, `ExistenceRegistry`.
- **Current state:** `_supersessions: dict[str, dict]` — one mutable slot per subject. `resurrect()` mutates the same dict object in place (`:527-535`); the audit journal hashes only the post-mutation record, so pre-resurrection field values are unrecoverable.
- **Why deferred:** independent architectural change with its own test surface — the same rigor `ADR-0015` required for relationships.
- **Approach (from Phase 1 discovery):** widen `_supersessions` to `dict[str, list[dict]]`; `supersede()`/`resurrect()` append rather than mutate. Mirrors two patterns already proven this session: Task 2's non-overlapping-coexistence design, and `ContextRegistry`'s replace-not-mutate discipline.
- **Risk:** low — read paths (`is_superseded()`, `successors_of()`) need only read the list's last element; no behavior change for existing callers.
- **Validation:** existing `test_resurrection_keeps_the_supersession_in_the_journal` and `test_resurrection_does_not_erase_the_supersession` must still pass; a new `supersession_history(id)` accessor test proves reconstruction.

### REQ-06 (remainder) — UCXI per-subject binding wired only for `KNOWLEDGE`
- **Owner:** UCXI-000001. **Authority:** `engine/context/registry.py`, `ContextRegistry`.
- **Current state:** `ADR-0016` wired a real per-subject binding for the `KNOWLEDGE` context kind (`engine/knowledge/ukip/confidence.py`). The other 15 universal context kinds have no equivalent — `bind-context` remains a CEU journal action with no corpus record (`P4-F-009`'s original, broader claim).
- **Why deferred:** each kind's binding would need its own integration point analogous to `confidence.py`, and no second consumer has been designed yet.
- **Approach:** replicate `confidence.py`'s pattern (project the subject's existing owned data into the target `ContextKind`'s required dimensions, register through `ContextRegistry`) for whichever kind is needed next, one at a time — not all 15 at once.
- **Risk:** low per-kind; scope risk if attempted as one large change instead of one-kind-at-a-time.
- **Validation:** same test shape as `test_confidence.py`.

### REQ-14 — `KnowledgeStore` discards prior version on replace/save
- **Owner:** UKDA. **Authority:** `engine/knowledge/store.py`.
- **Current state:** `replace_object()` (`:175-180`) removes the old CKO from `_objects`; `save()` (`:287-293`) fully overwrites the JSON file. Confirmed by direct investigation: no recovery path exists elsewhere (id-ledger.json indexes file *paths*, not `cko_id`; the memory-layers.json knowledge layer reads the *same* file `save()` overwrites).
- **Why deferred:** genuine data-loss defect, but the object model already has the field pair (`supersedes`/`superseded_by`) a fix would route through — this is "needs implementation" but small and well-precedented, not "needs design."
- **Approach:** `replace_object` deprecated in favor of `with_object(new_obj)` where `new_obj.supersedes` names the old `cko_id`; a companion transition sets the old object's `superseded_by`. `save()`'s mechanics are unchanged — it already writes the full `_objects` tuple; the fix is entirely upstream of it.
- **Risk:** low — additive field usage already defined on `CanonicalKnowledgeObject`.
- **Validation:** round-trip test proving both old and new versions coexist in `_objects` after a "replace."

### REQ-34 — Provenance chains never persisted
- **Owner:** UKIP, certification owners. **Authority:** `engine/knowledge/ukip/provenance.py`.
- **Current state:** `ProvenanceChain.to_dict()`/`.from_dict()` already round-trip fully and hash-verify (`require_intact()`). Zero write call sites exist anywhere in the codebase — `RegisteredKnowledge` (which carries `.provenance`) is a pure runtime construct, never serialized.
- **Why deferred:** shares an owner and a file (`KnowledgeStore`) with `REQ-14`; sequencing them together is more efficient than two separate passes over the same file.
- **Approach:** extend `KnowledgeStore`'s existing persisted JSON to also write `ProvenanceChain.to_dict()` keyed by subject — same store, same guard, same pattern already governing CKO/DecisionRecord. Not a new store.
- **Note, explicitly not a gap:** `KnowledgeCertificate` non-persistence is by design (derived truth, deterministically re-derivable) — only the step-by-step audit chain is the real gap.
- **Risk:** low — pure additive write/read path.
- **Validation:** persist → simulate restart → recover byte-identical chain.

### REQ-35 — UCDA decision register mutated in place, no append-only history
- **Owner:** `UCDA-000001`. **Authority:** `ucda_engine.py`, `ucda-decisions.json`.
- **Current state:** `ucda_engine.py` is a pure reader (`AUTHORITY = NONE, DERIVED TRUTH`) — no mutation API exists at all. Every decision edit, **including this session's own** `DEC-ADR-0017`/`DEC-ADR-0018` stage/disposition updates, is raw external JSON editing with zero transition validation (backward transitions or skipped stages would be silently accepted).
- **Why deferred:** unlike the others, this is genuinely **"needs implementation," no existing mechanism to integrate with directly** — `UCDA-000001` is its own distinct owner; `ContextRegistry`'s audit-journal shape is a pattern to *copy*, not a thing to *call*.
- **Approach — two options found, not yet chosen between:**
  1. A `decision_history` array added to `ucda-decisions.json`'s schema, hash-chained (`AuditEntry`-shaped: `sequence, decision_id, action, previous_snapshot_hash, new_snapshot_hash, entry_hash`), appended by whatever tool mutates a decision.
  2. A lighter policy: require every `ucda-decisions.json` mutation to be its own commit, never amended — treats git itself as the ledger. Cheaper, but weaker (no `verify_audit()`-style tamper evidence; append-only only if commit discipline is actually followed).
- **Risk:** medium — touches the schema every other decision in this repository's governance depends on; must not break `ucda_engine.py`'s existing `--gate` computation.
- **Validation:** a decision mutated twice produces two recoverable historical states; `ucda_engine.py --gate` still computes the same verdict as before the schema addition.

---

## OPEN GAP (4)

No approved decision exists. No implementation exists.

### REQ-28 — 192-document corpus-registration population unregistered
- **Owner:** `REG-AUTO-001` acting as `UMB-IMP-001`. **Authority:** `00-BOOK/tools/register.sh (ukb.py build --mint)`.
- **Current state:** `ukb.py enforce --pre` reports 192 unregistered-eligible documents, non-blocking at the PRE stage. This is a **different identity authority** than `UGA-001` (which `DEC-ADR-0017`/`0018` already closed, for 26 non-document objects, this session).
- **Why open, not governed:** explicitly named and excluded from `ADR-0017`'s scope (*"a different registration authority... over a different, larger, unenumerated population"*) — but nothing has since given it its own decision. It exists in a document's prose, not a decision register.
- **Required governance action before any implementation:** a dedicated `CEP-002 Article 28` decision that enumerates the 192 documents (or the deterministic mechanism by which they're enumerated), names `REG-AUTO-001`/`UMB-IMP-001` as owner, and states the irreversibility characteristics precisely — the same discipline `ADR-0017` applied to the 26-object UGA mint, at 7-8x the scale.
- **Risk:** higher than `ADR-0017`'s — larger population, and `register.sh --guard`'s full transaction (not just identity minting) is implicated, per this session's own reading of `test_verification_purity.py`'s module docstring (*"minted 140 permanent identities and emitted ~140 PORTAL pages... the result was uncommitted"* — the exact prior incident this repository's purity tests exist to prevent).

### REQ-39 — No mutation-classification rule for authored governance documents
- **Owner:** `platform.repository_intelligence.mutation_classification`.
- **Current state:** 7 classes declared (`CONSTITUTIONAL_TRUTH`, `SOURCE`, `GENERATED_ARTIFACT`, `EXCLUSION`, `REPOSITORY_STATE`, `CORPUS_REGISTRATION`, `GOVERNED_DECLARATION`) — checked directly, none literally named `AUTHORED_DOCUMENT`. ADRs, decision records, and determination artifacts (the kind of document this entire session has produced) presumably classify under `GOVERNED_DECLARATION` or `SOURCE` today; not confirmed by an actual `classify()` run this pass.
- **Why open:** this is a real, unaddressed absence, but a small one — the classification system is already data-declared and fail-closed (`EX-015`/`EX-016`), so closing it is additive, not a redesign.
- **Approach if pursued:** one new rule in `mutation-governance-boundary.json` + one new predicate in `RULE_PREDICATES`, reusing the exact mechanism `REQ-38` already certifies. No new authority, no new classifier module.
- **Risk:** low, contingent on first confirming (by actually running `classify()`) whether the current fall-through behavior is already acceptable — this may turn out to be a documentation gap, not a functional one, once measured directly.

### REQ-43 — `KnowledgeStore` has no swappable storage-technology interface
- **Owner:** UKDA. **Authority:** `engine/knowledge/store.py`.
- **Current state:** direct JSON file I/O; no interface a second storage technology could implement against. `engine/uckp/persistence.py`'s `PersistenceAdapter` is the proven pattern to copy, but is hard-typed to `UCKO` (`write(objects: Sequence[UCKO])`, direct `.ucko_id`/`.require_integrity()` calls) — not reusable as literally written.
- **Why open, not governed:** explicitly assessed and **not recommended for implementation** in `UCOS-ARCHITECTURAL-OPENNESS-ROADMAP.md` Phase 3 — design-only conclusion reached, no decision registered to build it.
- **Approach if pursued:** generalize `PersistenceAdapter` to a `Protocol` (or a `TypeVar` bound) both `UCKO` and `CanonicalKnowledgeObject` satisfy — both already expose `to_dict()`/`from_dict()`/`require_integrity()`/an id field structurally.
- **Risk:** medium — touches a proven, working, tested pattern; must not regress `engine/uckp`'s own 52 passing tests while generalizing.

### REQ-50 — UIEP-001 (Universal Infinite Expansion Principle) never created
- **Owner:** Constitutional Authority.
- **Current state:** requested in an earlier directive in this session before the track pivoted to evidence-first, grounded assessment. Never written under any name.
- **Why open:** superseded by the pivot — `UAP-001` was created instead, in the corrected, explicitly-non-certified form. `UIEP-001` was never revisited under the same discipline.
- **Approach if still wanted:** identical treatment to `UAP-001` — a declared design-direction document, explicitly labeled `DESIGN PRINCIPLE`, with the same non-certification boundary statement, not registered as a `CEP-002` decision.
- **Risk:** low — pure documentation, no code implication either way.

---

## SUPPORTED (2) — architectural direction exists, no executable proof

### REQ-46 — Infrastructure neutrality
No hardcoded paths/OS branches found in `engine/`'s core domain; dynamic `repo_root()`-style resolution used consistently. No test proves the codebase runs identically under a genuinely different infrastructure target (no second target exists to test against). Not recommended for closure by inventing one — nothing indicates this is currently a live constraint.

### REQ-47 — Tool neutrality
`git` dependency confirmed confined to governance/tooling layers, not core domain classes (verified by direct reading of `CanonicalKnowledgeObject`, `ExistenceRegistry`, `ContextRegistry` — none import `subprocess`/`git`). No test proves any tool is actually swappable. Same reasoning as `REQ-46` — no action recommended absent a real second target.

---

## NOT APPLICABLE (2) — no implementation surface exists

### REQ-44 — API/Communication neutrality
No communication-contract, interaction-capability, or exchange-relationship abstraction exists anywhere in the codebase (`platform/universal_control_plane/ontology.py`'s `Capability` class is a catalog record, not an interaction contract — checked directly). Documented per instruction, not designed, not invented.

### REQ-45 — UI/Experience neutrality
No UI layer of any kind exists. "No UI coupling detected; no UI architecture exists." UI agnosticism is not claimed as certified because there is nothing to be agnostic *about*.

---

**Total gap-register items:** 13 (5 governed closure + 4 open gap + 2 supported + 2 not applicable), against 36 fully `CERTIFIED` items tracked in the master index. Every item above cites the specific evidence (or absence of evidence) it rests on — nothing in this register is asserted from memory of an earlier claim without having been directly re-checked this session.
