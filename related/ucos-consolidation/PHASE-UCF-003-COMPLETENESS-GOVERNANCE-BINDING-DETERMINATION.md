# PHASE-UCF-003 — COMPLETENESS GOVERNANCE BINDING DETERMINATION

> **Mission:** Universal Completeness Foundation — the constitutional relationship model required before implementation.
> **Mode:** Determination only. No code changes, no registries, no engines, no JSON write applied to `constitutional-authority-alignment.json`.
> **Date:** 2026-08-13
> **Builds on:** `PHASE-UCF-000/001-COMPLETENESS-DISCOVERY-DETERMINATION.md`, `PHASE-UCF-002-COMPLETENESS-ARCHITECTURE-DETERMINATION.md`

This document specifies the exact binding shape a future, separately-approved implementation phase would write. Nothing below has been applied to any file. It follows the same `*_resolution` pattern already used five times this session (`identity_authority_resolution`, `relationship_graph_resolution`, `certification_authority_resolution`, `identity_namespace_resolution`) because every prior binding of this shape reused, not invented, that mechanism, and this one does the same.

---

## 1. Existence Relationship Binding — UGA, UCKP, Repository Intelligence

### Relationship classification

| Pair | Classification | Basis |
|---|---|---|
| UCKP registry vs. UGA registry | **Governance Gap → Federation** (declaration closes it) | Disjoint populations, zero conflict, both real, neither aware of the other (`PHASE-UCF-002 §1`) |
| UCKP registry vs. Repository Intelligence | **Governance Gap → Federation** | Zero import relationship either direction; different bounded question (facet-completeness vs. reuse/gap/conflict/duplicate analysis) (`PHASE-UCF-002 §3`) |
| UGA registry vs. Repository Intelligence | **Governance Gap → Federation** | Neither references the other; `repository_intelligence` reads the substrate independently via its own `substrate.py` |
| UGA's `owner`/`object_class`/`lifecycle` fields vs. UCKP's `OWNERSHIP`/`IDENTITY`/`LIFECYCLE` facets | **Projection** (not yet built) | UGA's fields are a strict, already-computed subset of what those three facets need; a provider translating one into the other adds no new fact, only exposes an existing one |
| All three vs. `engine.uckp.canonical` (the digest primitive) | **Authority** (unchanged) | All three already, transitively or directly, compute digests through the one Layer Zero primitive — confirmed for `repository_intelligence` via `platform/foundation/contracts.py:35`'s re-export |

### Proposed binding shape

A new top-level section, `existence_resolution`, structurally a peer of `certification_authority_resolution` (same `MULTIPLE_INDEPENDENT_AUTHORITIES`-family model, since three genuinely bounded, non-competing existence-tracking authorities were found, not one authority with subordinates):

```
"existence_resolution": {
  "model": {
    "type": "MULTIPLE_INDEPENDENT_AUTHORITIES",
    "declares": "Existence-tracking in UCOS is plural by design. Each authority answers
                 a different bounded question about 'what exists'; holding undisputed
                 authority over one does not compete with another holding undisputed
                 authority over a different one."
  },
  "authorities": [
    { "id": "UCKP-COMPLETENESS-REGISTRY", "home": "engine/uckp/registry.py",
      "role": "AUTHORITY", "bounded_question": "Does this object answer all 33
      constitutional completeness facets (Article 6)?", "population": "193 objects
      (measured), scoped to providers under engine.uckp by default root" },
    { "id": "UGA-EXISTENCE-REGISTRY", "home": "00-MASTER/UCOS-UGA-001/uga_engine.py",
      "role": "AUTHORITY", "bounded_question": "Does this version-controlled artifact
      exist, and who owns it, at repository scale?", "population": "5,789 objects
      (measured)" },
    { "id": "REPOSITORY-INTELLIGENCE", "home": "platform/repository_intelligence/",
      "role": "AUTHORITY", "bounded_question": "What exists, what can be reused,
      what is missing, what conflicts, what is duplicated, and who owns it — across
      the whole repository substrate?" }
  ],
  "declared_projections": [
    { "from": "UGA-EXISTENCE-REGISTRY", "to": "UCKP-COMPLETENESS-REGISTRY",
      "facets_covered": ["OWNERSHIP", "IDENTITY", "LIFECYCLE"],
      "status": "DECLARED, NOT YET IMPLEMENTED",
      "mechanism": "a ucko_objects() provider reading UGA's existing classification;
      no new field is computed, only exposed" }
  ],
  "second_authority_test": "A second authority over the SAME bounded question would be
    a rival. None found: each of the three answers a structurally different question,
    confirmed by zero cross-imports in any direction and non-overlapping population
    definitions. Full analysis in PHASE-UCF-002-COMPLETENESS-ARCHITECTURE-DETERMINATION.md."
}
```

---

## 2. Completeness Authority Binding — UCKP, Providers, Projections

### Relationship classification

| Relationship | Classification |
|---|---|
| UCKP over "what does completeness mean" (the 33-facet definition itself) | **Authority** — unconditional; Article 6 makes the facet set closed and mandatory, and no other module anywhere was found defining a rival completeness criterion |
| A package implementing `ucko_objects()`/`UCKO_OBJECTS` (e.g., `engine.uckp.alignment`, `capabilities`, `constitution` today) | **Provider** — contributes whole, already-facet-complete candidate objects; admitted or refused by the registry (Article 18), never bypasses it |
| UGA → UCKP (per §1) | **Projection** — contributes partial facet coverage (3 of 33) for objects UGA already tracks, not whole objects; distinguished from Provider precisely because it is incomplete by construction until more facets are sourced |
| `require_complete()`'s fail-closed guarantee | **Authority**, unconditional, unchanged by anything in this document |

The Provider/Projection distinction matters constitutionally: a **Provider** submits an object UCKP's registry can admit outright (all 33 facets already answered by the submitting module); a **Projection** submits partial facet data that leaves the object short of `require_complete()` until further providers or projections close the remaining facets. Neither may claim `require_complete()` has passed on the other's behalf — this prevents a partial projection from being silently treated as a complete admission, which would be exactly the "hidden incompleteness" the mission's own problem statement names.

### Proposed binding shape

Not a new section — an addition to the `existence_resolution` draft above (`declared_projections`, already shown), plus one clarifying entry establishing the Provider/Projection vocabulary itself as a recognized pair, analogous to how `AUTHORITY`/`PROJECTION` are already recognized `AUTHORITY_ROLES` members for the canonical-object model. No new top-level section is proposed for this item — it is scoped inside existence_resolution because it is definitionally about how objects enter existence-tracking, not a separate axis.

---

## 3. Lifecycle Binding — UCL-000001, Knowledge Lifecycle, Evolution History

### Relationship classification

| Pair | Classification |
|---|---|
| UCL-000001 vs. `engine.knowledge.model.Lifecycle` | **Governance Gap → Specialization** (declared as orthogonal axes: process vs. state, not competing) — see `PHASE-UCF-002 §2` |
| UCL-000001 vs. `engine.constitution.evolution` | **Specialization**, already declared in the code itself (not new — this binding only formalizes an existing, code-documented relationship) |
| UCL-000001 vs. Evolution History as a repository-wide concept | **Governance Gap, unresolved** — carried forward, not decided here; a unified cross-domain evolution view was not confirmed to exist or not exist by either UCF-001 or UCF-002 |

### Proposed binding shape

A new top-level section, `lifecycle_resolution`, using the same `ORTHOGONAL`-role pattern Phase 0.6 proved for CMG↔UCKP — because the same shape of problem (two real, non-competing things sharing enough surface-level similarity to be mistaken for rivals) has the same shape of fix:

```
"lifecycle_resolution": {
  "model": {
    "type": "ORTHOGONAL_AXES",
    "declares": "A process lifecycle (the stages a unit of work passes through) and
                 a state lifecycle (the standing an artifact currently holds) are
                 different axes. Neither is a projection or subordinate of the other;
                 running a process stage is plausibly how a state transition occurs,
                 but the two vocabularies are not the same vocabulary."
  },
  "axes": [
    { "id": "UCL-000001", "home": "engine/nucleus/lifecycle.py", "axis": "PROCESS",
      "scope": "the 45-stage universal work-cycle, declared to apply to nuclei,
      layers, compositions, capabilities, artifacts, knowledge, registries, policies,
      evidence, executions, contexts, universes, civilisations and realities alike",
      "role": "AUTHORITY over the process axis" },
    { "id": "KNOWLEDGE-LIFECYCLE", "home": "engine/knowledge/model.py", "axis": "STATE",
      "scope": "the 10-stage standing vocabulary for knowledge objects specifically",
      "role": "AUTHORITY over the state axis, bounded to knowledge objects" }
  ],
  "open_item": {
    "id": "EVOLUTION-HISTORY-UNIFIED-VIEW",
    "status": "NOT RESOLVED — existence not confirmed either way",
    "note": "Real components exist (CMG amendments, Lifecycle.SUPERSEDED/HISTORICAL,
    supersedes/superseded_by, evolves-from relation types, engine.constitution.evolution)
    but no single cross-domain read path was confirmed. A dedicated discovery pass is
    the correct next step, not a guess recorded here as fact."
  },
  "second_authority_test": "A second authority over the SAME axis (process or state)
    would be a rival. UCL-000001 and the Knowledge Lifecycle were checked against this
    test directly: UCL-000001 has no state named 'Draft' or 'Operational'; the Knowledge
    Lifecycle has no stage named 'Validate' or 'Certify' as a transition step. Full
    analysis in PHASE-UCF-002-COMPLETENESS-ARCHITECTURE-DETERMINATION.md §2."
}
```

The Evolution History item is deliberately left as a recorded open question inside this binding, not resolved by assertion — matching this session's repeated discipline of not guessing at what a dedicated pass alone can confirm.

---

## 4. The Universal Completeness Governance Model

Synthesizing §1–3, the governance model this mission actually needs is **not a new authority, registry, or engine** — every prior epoch confirmed this, and this binding pass found nothing to contradict it. The model is:

1. **UCKP remains the sole authority on what "complete" means** (Article 6, the 33 facets, `require_complete()`) — unconditional, unchanged.
2. **Existence-tracking is a declared federation of three authorities** (UCKP's own registry, UGA, Repository Intelligence), each bounded to its own question, with one declared (not yet implemented) projection path from UGA into UCKP.
3. **Providers submit whole objects; projections submit partial facet coverage** — a recognized, distinct pair, so a partial contribution can never be silently mistaken for a complete admission.
4. **Lifecycle is two orthogonal axes** (process, state), not one vocabulary needing unification — the same `ORTHOGONAL` mechanism already proven for CMG↔UCKP reused here, not reinvented.
5. **Evolution History remains an open, honestly-recorded question** — not forced to a premature resolution.
6. **Certification stays exactly as already bound** (`certification_authority_resolution`, `MULTIPLE_INDEPENDENT_AUTHORITIES`) — with one gap this binding pass surfaces: `RepositoryCertificate` (`repository_intelligence/certification.py`) is not yet a registered surface there, though it clearly qualifies by the same criteria every other surface in that binding was admitted under.

**This closes the loop the mission opened**: "anything that exists, emerges, changes, or evolves" does not need one new universal mechanism to become discoverable, owned, related, evidenced, validated, certified, and governed — it needs the *existing*, already-built mechanisms (UCKP, UGA, Repository Intelligence, UCL-000001, the Knowledge Lifecycle, the certification federation) to have their real relationships **declared**, so the next new object, capability, or context has an unambiguous path into all of them rather than a choice between three unconnected systems.

---

## 5. What Epoch 4 (Implementation) Would Actually Do — Named, Not Performed

For scoping only, per instruction not to implement:

1. Write `existence_resolution` and `lifecycle_resolution` (§1, §3 drafts above) into `constitutional-authority-alignment.json`, following the exact insertion-point and validation discipline every prior binding this session used (`verify_binding()`, `CAA-INV` re-check, `ukb.py enforce`/`validate`).
2. Add `RepositoryCertificate` as a fourteenth surface in the existing `certification_authority_resolution.surfaces` array (one entry, matching the pattern already used for `UKIP-KNOWLEDGE-CERTIFICATION`).
3. **Not** implement the UGA→UCKP projection provider itself in this same pass — that is code (a new `ucko_objects()` function somewhere reading UGA's data), materially different from a JSON declaration, and should be its own, separately-scoped and separately-validated phase, consistent with every prior binding-then-code split this session has used.
4. **Not** attempt to resolve the Evolution History open item — schedule it as its own discovery phase.

---

## 6. Non-Goals

- No file was modified. `constitutional-authority-alignment.json` was not touched — every JSON block above is illustrative, not applied.
- No registry, engine, or authority was created.
- The Evolution History question is recorded as open, not answered.
- No resolved governance question from any prior determination this session was reopened.
- This document does not itself constitute Epoch 4; it is the specification Epoch 4 would implement, pending review.

---

Stopping after determination, as instructed. Waiting for review before Epoch 4 implementation.
