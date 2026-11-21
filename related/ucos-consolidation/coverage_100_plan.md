# Coverage 100 Plan

Every uncovered line inside the measured denominator, classified. The remedy column is
the disposition the mandate assigns to each class, not a suggestion.

**Total uncovered lines measured:** 1,777

| class | lines | share | remedy |
|---|---:|---:|---|
| `executable` | 1,762 | 99.2% | write tests |
| `generated` | 15 | 0.8% | govern |

## Why `executable` is the default

A line is executable until a stated rule says otherwise, so the cheap classification is
the one that costs work. The alternative — a permissive default — turns classification
into the mechanism by which coverage debt is retired without any test being written.

`dead_code` is never assigned automatically. Deciding code is dead requires knowing that
nothing calls it, including callers outside this repository, and a classifier that
guessed would be proposing deletions on the strength of a regex.

## Files inside the denominator that the coverage document does not describe

**742 files, 77,882 statements
by AST count.** They are declared in scope and appear nowhere in `coverage.xml`.

Their covered fraction is **unknown from this artifact and is not assumed to be
zero.** Two different causes produce identical evidence here — no test imported the
file, or `coverage xml` dropped it because its relative name collided across source
roots — and this document refuses to guess between them. `coverage report` shows
1,259 files against the 644 the XML body describes, which makes the rendering defect
the larger contributor.

Counting these as uncovered executable lines is what produced a first draft of this
plan claiming 79,008 lines owing tests against a coverage report showing 3,654
missing — a 21x overstatement caused entirely by treating absence as zero.

- `application/__init__.py`
- `application/capability.py`
- `application/capability_certification.py`
- `application/capability_meta.py`
- `application/capability_realize.py`
- `application/capability_traceability.py`
- `application/capability_validation.py`
- `application/composition.py`
- `application/composition_certification.py`
- `application/composition_meta.py`
- `application/composition_realize.py`
- `application/composition_traceability.py`
- `application/composition_validation.py`
- `application/governance.py`
- `application/governance_certification.py`
- `application/governance_meta.py`
- `application/governance_realize.py`
- `application/governance_traceability.py`
- `application/governance_validation.py`
- `application/model.py`
- `application/model_certification.py`
- `application/model_meta.py`
- `application/model_realize.py`
- `application/model_traceability.py`
- `application/model_validation.py`
- `application/security.py`
- `application/security_certification.py`
- `application/security_meta.py`
- `application/security_realize.py`
- `application/security_traceability.py`
- `application/security_validation.py`
- `application/state.py`
- `application/state_certification.py`
- `application/workflow.py`
- `data/__init__.py`
- `data/certification.py`
- `data/governance.py`
- `data/governance_certification.py`
- `data/governance_meta.py`
- `data/governance_realize.py`
- … and 702 more

## Heaviest owners

| file | uncovered lines |
|---|---:|
| `engine/certification_integrity/equivalence.py` | 104 |
| `engine/certification_integrity/immutable.py` | 72 |
| `intelligence/publication/__main__.py` | 72 |
| `engine/verification_intelligence/cost_model.py` | 62 |
| `intelligence/rie/__main__.py` | 56 |
| `intelligence/research/__main__.py` | 54 |
| `engine/certification_integrity/suite.py` | 40 |
| `engine/certification_integrity/classify.py` | 36 |
| `engine/knowledge/ukip/graph.py` | 33 |
| `infrastructure/integration_validation.py` | 32 |
| `platform/repository_intelligence/substrate.py` | 32 |
| `engine/ceu/existence.py` | 30 |
| `engine/knowledge/ukip/discovery.py` | 30 |
| `platform/commercial_intelligence/licensing.py` | 28 |
| `platform/commercial_intelligence/pricing.py` | 28 |
| `data/attribute_validation.py` | 26 |
| `data/schema_validation.py` | 26 |
| `infrastructure/resilience_validation.py` | 26 |
| `engine/lineage/memory.py` | 25 |
| `infrastructure/topology_validation.py` | 25 |
| `intelligence/realization/implementation.py` | 25 |
| `data/entity_validation.py` | 24 |
| `platform/commercial_intelligence/customer.py` | 23 |
| `platform/commercial_intelligence/marketplace.py` | 23 |
| `platform/commercial_intelligence/packages.py` | 22 |

## The executable remainder — what actually owes tests

1,762 lines carry no exemption. Sample of 40:

| file:line | object | source |
|---|---|---|
| `data/attribute.py:168` | `Attribute.__post_init__` | `raise AttributeError_("attribute kind must be a DXH-03 AttributeKind (DMR-09)")` |
| `data/attribute.py:171` | `Attribute.__post_init__` | `raise AttributeError_("attribute values exactly one Datum via DatumValueRef (DMR-02)")` |
| `data/attribute.py:173` | `Attribute.__post_init__` | `raise AttributeError_("value reference is not a CERTIFIED Datum identity (DMR-02)")` |
| `data/attribute.py:177` | `Attribute.__post_init__` | `raise AttributeError_("value reference carries no ENG-003 value digest (UDL-06)")` |
| `data/attribute.py:186` | `Attribute.__post_init__` | `raise AttributeError_("attribute state must be a DOS-01…05 state (UDL-12)")` |
| `data/attribute.py:298` | `Attribute.transition` | `raise AttributeError_("target state must be a DOS-01…05 state (UDL-12)")` |
| `data/attribute_realize.py:106` | `build_canonical_attribute` | `value_datum = build_canonical_value_datum()` |
| `data/attribute_realize.py:107` | `build_canonical_attribute` | `return make_attribute(` |
| `data/attribute_realize.py:202` | `RealizationResult.determination` | `if self.validation.accepted and self.certification.decision.certified and self.trace.closed:` |
| `data/attribute_realize.py:203` | `RealizationResult.determination` | `return "COMPLETE WITH CONDITIONS"` |
| `data/attribute_realize.py:204` | `RealizationResult.determination` | `return "NOT COMPLETE"` |
| `data/attribute_validation.py:137` | `AttributeTypedCheck.evaluate` | `return self._failed("attribute is untyped (DAA-01 / UDL-08)")` |
| `data/attribute_validation.py:150` | `AttributeNamedCheck.evaluate` | `return self._failed("attribute is unnamed (DAA-04 / UDL-08)")` |
| `data/attribute_validation.py:163` | `AttributeIdentifiedCheck.evaluate` | `return self._failed("attribute has no ENG-001 identity (UDL-04)", id=subject.target_id)` |
| `data/attribute_validation.py:177` | `AttributeValueFidelityCheck.evaluate` | `return self._failed("value is not ENG-003 value-faithful (UDL-06)", digest=digest)` |
| `data/attribute_validation.py:190` | `AttributeValuesDatumCheck.evaluate` | `return self._failed(` |
| `data/attribute_validation.py:195` | `AttributeValuesDatumCheck.evaluate` | `return self._failed("attribute absorbs its value's Datum model (DMX-02)")` |
| `data/attribute_validation.py:208` | `AttributeSingleBearingCheck.evaluate` | `return self._failed("attribute floats free — no bearing entity (DAA-02)")` |
| `data/attribute_validation.py:221` | `AttributeNullabilityDeclaredCheck.evaluate` | `return self._failed("attribute nullability is not declared explicitly (DAA-05)")` |
| `data/attribute_validation.py:234` | `AttributeClassifiedCheck.evaluate` | `return self._failed("attribute kind is outside DXH-03", kind=subject.kind)` |
| `data/attribute_validation.py:248` | `AttributeRelationalByReferenceCheck.evaluate` | `return self._failed("relational attribute has no ENG-005 reference (DAA-07)")` |
| `data/attribute_validation.py:252` | `AttributeRelationalByReferenceCheck.evaluate` | `return self._failed("non-relational attribute set a cross-entity reference (DAA-07)")` |
| `data/attribute_validation.py:266` | `AttributeDerivationProvenanceCheck.evaluate` | `return self._failed("derived attribute records no provenance (DAA-06)")` |
| `data/attribute_validation.py:269` | `AttributeDerivationProvenanceCheck.evaluate` | `return self._failed("non-derived attribute declared provenance (DAA-06)")` |
| `data/attribute_validation.py:282` | `MetaClassSingleCheck.evaluate` | `return self._failed("meta-class is not DMC-03 (V1)", meta_class=subject.meta_class)` |
| `data/attribute_validation.py:296` | `MetaRelationshipsClosedCheck.evaluate` | `return self._failed("relationships outside DMR-01…12 (V2)", outside=outside)` |
| `data/attribute_validation.py:316` | `MetaConstraintsCheck.evaluate` | `return self._failed("DAA-K1/K2 (DMK-01/02) not satisfied (V3)")` |
| `data/attribute_validation.py:329` | `FoundingAcyclicCheck.evaluate` | `return self._failed("founding graph is not acyclic (V4)")` |
| `data/attribute_validation.py:342` | `LifecycleValidCheck.evaluate` | `return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)` |
| `data/attribute_validation.py:355` | `FoundationReuseIntegrityCheck.evaluate` | `return self._failed("an EL-1/DMC-01 primitive was redefined (UDL-02 / DMI-05)")` |
| `data/attribute_validation.py:357` | `FoundationReuseIntegrityCheck.evaluate` | `return self._failed("no EL-1 substrate reference recorded (UDL-02)")` |
| `data/attribute_validation.py:359` | `FoundationReuseIntegrityCheck.evaluate` | `return self._failed("the certified Datum model was absorbed, not referenced (DMX-02)")` |
| `data/attribute_validation.py:372` | `StorageIndependenceCheck.evaluate` | `return self._failed("a storage technology was selected (UDL-11 / DAA-K5)")` |
| `data/attribute_validation.py:385` | `NonConstitutiveCheck.evaluate` | `return self._failed("attribute confers authority (UDL-15 / DAA-09)")` |
| `data/attribute_validation.py:400` | `ProvisionalDisclosureCheck.evaluate` | `return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")` |
| `data/attribute_validation.py:416` | `TraceabilityRootedCheck.evaluate` | `return self._failed("lineage not rooted at the meta-class", head=chain[0])` |
| `data/attribute_validation.py:418` | `TraceabilityRootedCheck.evaluate` | `return self._failed("lineage does not close to the 10-DATA anchor")` |
| `data/datum.py:113` | `Datum.__post_init__` | `raise DatumError("datum kind must be a DXH-01 DatumKind (DMR-09)")` |
| `data/datum.py:118` | `Datum.__post_init__` | `raise DatumError("datum state must be a DOS-01…05 DatumState (UDL-12)")` |
| `data/datum.py:200` | `Datum.transition` | `raise DatumError("target state must be a DOS-01…05 DatumState (UDL-12)")` |
