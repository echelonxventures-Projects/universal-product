# Autonomous Evolution Capability Matrix

> **Register:** `01-AUTONOMOUS-EVOLUTION-CAPABILITY-MATRIX.md` (ordinal 01)  
> **Programme:** UAUE-000001 v1.0.0  
> **Renderer:** `capability_matrix`  
> **AUTHORITY = NONE — DERIVED TRUTH**  
> **Declaration digest:** `eb31205bea13edee`  
> **Regenerate:** `make uaue-render` — this file is a projection and never a source.

*the deliverable of architecture discovery: every capability of the loop classified against repository truth*

Every position of the loop, the owner homes that discharge it, the gate that closes it, and the classification the declaration's own rule measures it into.

| Position | Name | Duty | Stages | Owner homes | Gate | Wired | Class |
|---|---|---|---|---|---|---|---|
| AUE-P-01 | Discover | turn a condition observed by a located owner into an evolution candidate with a reason and a subject | observe | intelligence/rie/discovery.py · intelligence/rie/analysis.py · platform/universal_control_plane/evolution.py | make rib-gate | PASS | IMPLEMENTED |
| AUE-P-02 | Understand | answer why to evolve, what changes, what depends on it, what can break, and what evidence supports it | learn, impact-analysis, dependency-analysis | engine/uckp/ucko.py · engine/knowledge/model.py · platform/validation_intelligence/analyzers.py | make ucl-gate | PASS | IMPLEMENTED |
| AUE-P-03 | Plan | produce objectives, steps, dependencies, risk, acceptance criteria and a rollback strategy under the governing authority | reason, authority-resolution | intelligence/realization/planning.py · platform/universal_assurance/planning.py · engine/constitution/planner.py | make uaep-gate | PASS | IMPLEMENTED |
| AUE-P-04 | Simulate | predict impact, validate dependencies and evaluate risk before anything is executed | simulate | platform/universal_assurance/determinism.py · engine/constitution/replay.py · engine/nucleus/lifecycle.py | make final-closure-gate | PASS | IMPLEMENTED |
| AUE-P-05 | Execute | carry the plan through the single authorised mutation path, under identity, authority, evidence and gates | implementation | engine/constitution/gateway.py · engine/constitution/state.py · engine/runtime/execution/__init__.py | ./verify.sh | PASS | IMPLEMENTED |
| AUE-P-06 | Measure | observe the result after execution and compare expected against actual, recording the deviation | replay | platform/universal_control_plane/evolution.py · platform/universal_assurance/measurement.py · engine/nucleus/lineage.py | make aee-gate | PASS | IMPLEMENTED |
| AUE-P-07 | Validate | establish correctness, completeness, consistency, compatibility, traceability and reproducibility of the change | validation | platform/universal_assurance/orchestrator.py · engine/uckp/validation.py · engine/validation/executor.py | ./verify.sh | PASS | IMPLEMENTED |
| AUE-P-08 | Verify | prove identity, dependency, evidence, governance and lifecycle integrity, and readiness to certify | verification | verify.sh · 00-CMG/tools/cmg_validate.py · 00-MASTER/UCOS-UGA-001/uga_engine.py · 00-MASTER/UCOS-RIB-001/rib_engine.py | ./verify.sh | PASS | IMPLEMENTED |
| AUE-P-09 | Certify | prove the evolution was authorised, understood, planned, executed, evidenced, validated, verified and recorded | certification | engine/universal_certification/pipeline.py · platform/universal_assurance/certification.py · platform/certification/ledger.py | make aee-gate | PASS | IMPLEMENTED |
| AUE-P-10 | Learn | assimilate the outcome so the next cycle starts from what this one established | knowledge-assimilation | engine/knowledge/store.py · intelligence/rie/knowledge.py · engine/constitution/assimilation.py | make assimilate-gate | PASS | IMPLEMENTED |
| AUE-P-11 | Evolve | transition state, append the history record, and continue — never terminate | state-transition, continuation | engine/uckp/evolution.py · engine/uckp/state.py · engine/nucleus/evolution.py | make uaue-gate | PASS | IMPLEMENTED |

## Classification vocabulary

| Classification | Rank | Rule | Meaning |
|---|---|---|---|
| IMPLEMENTED | 4 | every_declared_home_resolves_with_its_symbols_and_the_gate_is_wired | every declared owner home resolves, every declared symbol is bound in it, and a gate is declared and resolves |
| PARTIALLY_IMPLEMENTED | 3 | at_least_one_declared_home_resolves | at least one declared owner home resolves with its symbols, but a declared home, symbol or gate does not |
| FUTURE_EVOLUTION | 2 | no_home_is_declared | the phase is declared with no owner home at all and is carried as a disclosed absence rather than closed by building a new engine |
| DUPLICATE | 1 | another_phase_declares_an_identical_home_set | two phases resolve to an identical owner home set, which would be two authorities over one home |
| MISSING | 0 | no_declared_home_resolves | no declared owner home resolves, so the phase has no realisation in repository truth |

## Exit criteria

Every criterion, and the violation count the declaration binds it to. A criterion is satisfied when its measure holds its declared expectation — measured on this run, not asserted by the declaration that states it.

| Criterion | Phase | Obligation | Measure | Expected | Measured | Verdict |
|---|---|---|---|---|---|---|
| AUE-EXIT-01 | AUE-001 | every capability of the loop is classified against repository truth and the classification matrix is rendered | unclassified_capability_surface | 0 | 0 | PASS |
| AUE-EXIT-02 | AUE-002 | every mandated evolution object kind exists and carries every mandated field | object_kinds_or_mandated_fields_unmet | 0 | 0 | PASS |
| AUE-EXIT-03 | AUE-003 | every declared discovery duty is satisfied by at least one resolving source, and discovery yields at least one candidate | discovery_duties_unsatisfied | 0 | 0 | PASS |
| AUE-EXIT-04 | AUE-004 | every candidate produces an understanding object answering all five understanding questions | understanding_questions_unanswered | 0 | 0 | PASS |
| AUE-EXIT-05 | AUE-005 | every candidate produces a plan object carrying objectives, steps, dependencies, risk, criteria and rollback | plan_components_missing | 0 | 0 | PASS |
| AUE-EXIT-06 | AUE-006 | no execution object exists without a preceding simulation object | executions_without_simulation | 0 | 0 | PASS |
| AUE-EXIT-07 | AUE-007 | every execution object binds the single authorised mutation path and no second mutation path is offered | executions_without_the_single_mutation_path | 0 | 0 | PASS |
| AUE-EXIT-08 | AUE-008 | every chain produces an observation object recording expected, actual and deviation | observations_without_expected_actual_deviation | 0 | 0 | PASS |
| AUE-EXIT-09 | AUE-009 | every declared validation dimension is measured and satisfied | validation_dimensions_unsatisfied | 0 | 0 | PASS |
| AUE-EXIT-10 | AUE-010 | every declared verification dimension is measured, satisfied and bound to a wired gate | verification_dimensions_unsatisfied_or_ungated | 0 | 0 | PASS |
| AUE-EXIT-11 | AUE-011 | every declared certification proof is measured and satisfied | certification_proofs_unsatisfied | 0 | 0 | PASS |
| AUE-EXIT-12 | AUE-012 | the controller traverses every phase for every candidate with no phase-specific or subject-specific branch | controller_subject_specific_branches | 0 | 0 | PASS |
| AUE-EXIT-13 | AUE-013 | the history projection contains every object, rehydrates through the canonical ledger and is queryable by every declared key | history_projection_gaps | 0 | 0 | PASS |
| AUE-EXIT-14 | AUE-014 | the self-evolution subject's gap is measured closed and its required symbols resolve | self_evolution_unclosed | 0 | 0 | PASS |
| AUE-EXIT-15 | AUE-015 | the unknown-object probe traverses every phase, and the stage vocabulary admits a stage term no stage declares | unknown_subject_or_vocabulary_unmet | 0 | 0 | PASS |

## Discovery duties and the sources that satisfy them

| Duty | Obligation | Satisfied by |
|---|---|---|
| AUE-DUTY-01 | repository changes | AUE-SRC-06, AUE-SRC-08 |
| AUE-DUTY-02 | capability gaps | AUE-SRC-01, AUE-SRC-02 |
| AUE-DUTY-03 | knowledge gaps | AUE-SRC-03 |
| AUE-DUTY-04 | validation failures | AUE-SRC-04, AUE-SRC-06 |
| AUE-DUTY-05 | optimization opportunities | AUE-SRC-05 |
| AUE-DUTY-06 | new relationships | AUE-SRC-07 |
| AUE-DUTY-07 | unknown objects | AUE-SRC-09 |
| AUE-DUTY-08 | authority surface gaps in this repository's own canonical owners | AUE-SRC-08 |
