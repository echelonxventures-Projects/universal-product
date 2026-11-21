# UCOS-UCAF-001 · Authority Realization

An authority is declared by an instrument and EXERCISED by code. Every token below
is DISCOVERED from the executable plane; none is declared by this programme. Two
properties are measured independently, and the second cannot waive the first.

1. **No collision.** No token minted in the executable plane may be a registered
   constitutional authority. This is the machine form of the prohibition on
   governance asserting, simulating or substituting for constitutional authority.
2. **Classified.** Every discovered token must belong to a declared class recording
   what it is and why it is not a constitutional authority. An undisclosed token
   closes the gate whatever it says.

## Declared token classes

| Class | Token | Class | Constitutional | Basis |
|---|---|---|---|---|
| `UCAF-TC-01` | `ENGINEERING-EXECUTION-ONLY` | ENGINEERING-EXECUTION | no | 00-CEP/CEP-003-CONSTITUTIONAL-EXECUTION-CONSTITUTION.md ARTICLE I.3 — execution authority SHALL NOT govern, ratify, decide constitutional content, or exercise a power reserved to a higher tier. A module minting this token discloses that it acts and holds nothing. |
| `UCAF-TC-02` | `NONE (DERIVED TRUTH)` | DERIVED-TRUTH | no | 00-CMG/CMG-000001 ARTICLE XVI.2 — the derived-truth tier records and asserts nothing. A module minting this token discloses that it computes and refuses rather than legislating. |
| `UCAF-TC-03` | `authority` | DELTA-REGISTER-KEY | no | engine/uckp/state.py — one of the five delta registers a UCKP transition is required to carry. The constant is a register key in a state record, not a claim to hold authority; it is disclosed here rather than filtered in code so that the discovered population is never quietly narrowed. |
| `UCAF-TC-04` | `Universal Foundation Constitutional Authority` | IMPLEMENTATION-CONFORMANCE | no | platform/universal_foundation/constitution.py — the declared owner of UCOS-UFC-001, the law governing whether a Foundation CAPABILITY conforms across the thirteen domains it names (contracts, services, providers, policies, registries, runtimes, lifecycle, compatibility, evolution, governance, certification, composition, specialization). Its subject is implementation conformance, never constitutional content: it cannot ratify, cannot legislate, cannot vest or revoke a tier, and cannot override a located canonical owner. Its standing is AUTHORITY = NONE (DERIVED TRUTH) under 00-CMG/CMG-000001 ARTICLE XVI.2 — it measures and refuses. Disclosed here rather than filtered in code so the discovered population is never quietly narrowed. |
| `UCAF-TC-05` | `FG-15-NO-PARALLEL-AUTHORITY` | CONSTITUTIONAL-GATE-IDENTITY | no | platform/universal_foundation/convergence.py — the identity of the executable gate that proves UCOS-UFC-001 UFC-15, the article FORBIDDING a parallel constitutional authority. The symbol name ends in AUTHORITY because the article it proves is about authority; the constant is the name of a measurement, not a claim to hold anything. Classified for the same reason as UCAF-TC-03: the discovered population is disclosed in full and narrowed by declaration, never by a filter in code. |
| `UCAF-TC-06` | `accountable_authority` | RESOLUTION-LEDGER-FIELD | no | engine/uckp/intelligence.py — the field name under which an entry of the constitutional `category_ownership_resolution` declares the party accountable for a category's population, read by the declared-versus-measured category integrity join (PHASE-UCF-013). The constant is a JSON key in a resolution record, not a claim to hold authority. What the key names is held distinct from constitutional authority in three separate ways, each already determined: the value is a governance entity accountable for a category's population POLICY, severed by PHASE-UCF-012 D4 from the Ownership.owner value space (Facet 7) precisely so it cannot be aggregated into one; what a category IS remains GOVERNED_CATEGORIES under Article 17, which the ledger cites and never re-declares (PHASE-UCF-012 § 8.2, 'there is no vacancy here'); and the reasoner that reads the key reports at OBSERVATION severity and can move no certification verdict. The resolution sections it belongs to are recognitive, never constitutive — each records a standing that measurement already shows to hold and grants no right (PHASE-UCF-012 § 6.3). Disclosed here rather than renamed in code, for the same reason as UCAF-TC-03 and UCAF-TC-05: the discovered population is narrowed by declaration, never by a filter — and a symbol chosen to fall outside the discovery pattern would be that filter under another name. |
| `UCAF-TC-07` | `AUTHORITY` | PROJECTION-ROLE-NAME | no | engine/root_ontology/model.py — the name of one of the four ROLES a site may hold in UCPA-000001's classification of artifacts that state the root ontology (AUTHORITY, RATIFICATION_RECORD, PROJECTION, SUPERSEDED). The constant is a role LABEL compared against declared data, not a claim to hold authority: the programme's own standing is AUTHORITY = NONE (DERIVED TRUTH), it legislates no ontology, and UCPA-L-06 requires the single site bearing this role to be the canonical owner that 00-MASTER/URRC-000001/urrc-bindings.json D-24 already binds — so the label can only ever point at an owner determined elsewhere, and can never vest one. Disclosed here rather than renamed in code for the reason UCAF-TC-06 records: a symbol chosen to fall outside the discovery pattern would be a filter under another name, and the discovered population must be narrowed by declaration only. |
| `UCAF-TC-08` | `UCOS-REPOSITORY-ROOT` | DERIVED-OWNERSHIP-OF-LAST-RESORT | no | 00-MASTER/UCOS-UGA-001 declares the repository's ownership function TOTAL: its last rule is unconditional, so every path resolves to exactly one owner and 'unowned' is structurally unreachable. UCOS-OMEGA-001's Ω-A-07 is that last rule in executable form, and this token is the owner it names -- the repository owning what nothing more specific claims. It legislates nothing and asserts nothing about the artifact beyond the fact that no declaration, programme home, invocation plane or importer claimed it. MEASURED PROPERTY OF THIS TOKEN IN THE CURRENT TREE: Ω-A-07 fires zero times, so the token is minted as a definition and reached by no artifact. That is the intended state -- the rule exists to make the function total, and the rule being UNUSED is what makes the derivation informative rather than vacuous. The authority_of_last_resort ratchet is CONVERGENT at 0 and refuses the first artifact that reaches it. |
| `UCAF-TC-09` | `UCOS-UNIVERSAL-AUTHORITY` | DERIVED-AUTHORITY-OF-LAST-RESORT | no | engine/omega_governance/authority.py — the owner UCOS-OMEGA-001's authority resolver names when all seven of its tiers have been consulted and every one abstained. It is the terminal rung of a resolution walk and its purpose is TOTALITY: a resolver returning nothing for an unclaimed artifact hands every caller the same decision to make separately, and they do not make it the same way. THE TOKEN LEGISLATES NOTHING AND VESTS NOTHING, and the module is built so it cannot be read as though it did: every arrival is recorded as a FallbackEvent carrying the tiers consulted and the tiers that actually had sources, counted by the scale-free `fallback_density` and named subject-by-subject by `unattributed`, precisely so 'nobody owns this' can never be mistaken for 'the universal authority owns this'. It marks an unowned artifact; it does not claim one. This is the omega_governance analogue of UCAF-TC-08's UCOS-REPOSITORY-ROOT, and it is disclosed here rather than renamed in code for the reason UCAF-TC-06 records: the discovered population is narrowed by declaration only, and a symbol chosen to fall outside the discovery pattern would be a filter under another name. |

## Tokens minted in the executable plane

| Module | Constant | Token | Class | Classified | Collides |
|---|---|---|---|---|---|
| `engine/acceptance/contracts.py` | `ACCEPTANCE_AUTHORITY` | `ENGINEERING-EXECUTION-ONLY` | ENGINEERING-EXECUTION | YES | no |
| `engine/certification/contracts.py` | `CERTIFICATION_AUTHORITY` | `ENGINEERING-EXECUTION-ONLY` | ENGINEERING-EXECUTION | YES | no |
| `engine/context/__init__.py` | `AUTHORITY` | `NONE (DERIVED TRUTH)` | DERIVED-TRUTH | YES | no |
| `engine/context/certification.py` | `AUTHORITY` | `NONE (DERIVED TRUTH)` | DERIVED-TRUTH | YES | no |
| `engine/governance/contracts.py` | `GOVERNANCE_AUTHORITY` | `ENGINEERING-EXECUTION-ONLY` | ENGINEERING-EXECUTION | YES | no |
| `engine/knowledge/certification.py` | `KNOWLEDGE_CERTIFICATION_AUTHORITY` | `ENGINEERING-EXECUTION-ONLY` | ENGINEERING-EXECUTION | YES | no |
| `engine/knowledge/ukip/certification.py` | `KNOWLEDGE_INTELLIGENCE_AUTHORITY` | `ENGINEERING-EXECUTION-ONLY` | ENGINEERING-EXECUTION | YES | no |
| `engine/omega_governance/__init__.py` | `AUTHORITY` | `NONE (DERIVED TRUTH)` | DERIVED-TRUTH | YES | no |
| `engine/omega_governance/authority.py` | `UNIVERSAL_FALLBACK_AUTHORITY` | `UCOS-UNIVERSAL-AUTHORITY` | DERIVED-AUTHORITY-OF-LAST-RESORT | YES | no |
| `engine/omega_governance/reference/__init__.py` | `AUTHORITY` | `NONE (DERIVED TRUTH)` | DERIVED-TRUTH | YES | no |
| `engine/omega_governance/temporal/__init__.py` | `AUTHORITY` | `NONE (DERIVED TRUTH)` | DERIVED-TRUTH | YES | no |
| `engine/root_ontology/model.py` | `ROLE_AUTHORITY` | `AUTHORITY` | PROJECTION-ROLE-NAME | YES | no |
| `engine/runtime/bridge/contracts.py` | `BRIDGE_AUTHORITY` | `ENGINEERING-EXECUTION-ONLY` | ENGINEERING-EXECUTION | YES | no |
| `engine/runtime/execution/authorization.py` | `EXECUTION_AUTHORITY` | `ENGINEERING-EXECUTION-ONLY` | ENGINEERING-EXECUTION | YES | no |
| `engine/uckp/intelligence.py` | `ACCOUNTABLE_AUTHORITY` | `accountable_authority` | RESOLUTION-LEDGER-FIELD | YES | no |
| `engine/uckp/state.py` | `AUTHORITY` | `authority` | DELTA-REGISTER-KEY | YES | no |
| `engine/universal_certification/contracts.py` | `UCERT_AUTHORITY` | `ENGINEERING-EXECUTION-ONLY` | ENGINEERING-EXECUTION | YES | no |
| `engine/universal_discovery/authority.py` | `REPOSITORY_AUTHORITY` | `UCOS-REPOSITORY-ROOT` | DERIVED-OWNERSHIP-OF-LAST-RESORT | YES | no |
| `platform/commercial_intelligence/contracts.py` | `COMMERCIAL_AUTHORITY` | `ENGINEERING-EXECUTION-ONLY` | ENGINEERING-EXECUTION | YES | no |
| `platform/repository_intelligence/contracts.py` | `REPOSITORY_INTELLIGENCE_AUTHORITY` | `ENGINEERING-EXECUTION-ONLY` | ENGINEERING-EXECUTION | YES | no |
| `platform/repository_operations/contracts.py` | `OPERATIONS_AUTHORITY` | `ENGINEERING-EXECUTION-ONLY` | ENGINEERING-EXECUTION | YES | no |
| `platform/universal_assurance/contracts.py` | `ASSURANCE_AUTHORITY` | `ENGINEERING-EXECUTION-ONLY` | ENGINEERING-EXECUTION | YES | no |
| `platform/universal_foundation/constitution.py` | `FOUNDATION_CONSTITUTION_AUTHORITY` | `Universal Foundation Constitutional Authority` | IMPLEMENTATION-CONFORMANCE | YES | no |
| `platform/universal_foundation/convergence.py` | `GATE_NO_PARALLEL_AUTHORITY` | `FG-15-NO-PARALLEL-AUTHORITY` | CONSTITUTIONAL-GATE-IDENTITY | YES | no |
| `platform/universal_pipeline/governance.py` | `GOVERNANCE_AUTHORITY` | `NONE (DERIVED TRUTH)` | DERIVED-TRUTH | YES | no |
| `platform/universal_validation/contracts.py` | `VALIDATION_AUTHORITY` | `ENGINEERING-EXECUTION-ONLY` | ENGINEERING-EXECUTION | YES | no |
| `platform/validation_intelligence/contracts.py` | `INTELLIGENCE_AUTHORITY` | `ENGINEERING-EXECUTION-ONLY` | ENGINEERING-EXECUTION | YES | no |

## Realization bindings (located authority ↔ the code that exercises it)

| Binding | Authority | Resolves to | Tier | Tier located | Module | Token | Enforced by | Vesting located | Defined by the vesting instrument | Bound |
|---|---|---|---|---|---|---|---|---|---|---|
| `UCAF-RB-01` | Execution Authority | `CEP-003::EXECUTION` | Execution Authority | YES | `engine/runtime/execution/authorization.py` | `ENGINEERING-EXECUTION-ONLY` | `require_authorization` | YES | YES | YES |
