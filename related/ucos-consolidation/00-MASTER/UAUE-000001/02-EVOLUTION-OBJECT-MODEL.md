# Universal Evolution Object Model

> **Register:** `02-EVOLUTION-OBJECT-MODEL.md` (ordinal 02)  
> **Programme:** UAUE-000001 v1.0.0  
> **Renderer:** `object_model`  
> **AUTHORITY = NONE — DERIVED TRUTH**  
> **Declaration digest:** `eb31205bea13edee`  
> **Regenerate:** `make uaue-render` — this file is a projection and never a source.

*the object kinds, the mandated fields, and the proof that every kind carries every field*

## Object kinds

| Kind | Name | Position | Mandated | Purpose |
|---|---|---|---|---|
| AUE-OBJ-01 | Evolution Intent Object | AUE-P-01 | PASS | the recorded intention to evolve one subject for one reason, derived from an owner's measurement rather than from a human feature request |
| AUE-OBJ-02 | Evolution Understanding Object | AUE-P-02 | PASS | why the evolution matters, what it changes, what depends on it, what it can break, and what evidence supports each of those answers |
| AUE-OBJ-03 | Evolution Plan Object | AUE-P-03 | PASS | objectives, steps, dependencies, risk, the criteria each later phase will be judged against, and the rollback strategy |
| AUE-OBJ-04 | Evolution Simulation Object | AUE-P-04 | FAIL | the predicted impact, dependency resolution and risk evaluation obtained before execution. Additional to the mandated set: without it, execution would be permitted with no prior evaluation, which the controlled-execution rule forbids |
| AUE-OBJ-05 | Evolution Execution Object | AUE-P-05 | PASS | the record that the plan was carried through the single authorised mutation path under identity, authority, evidence and gates |
| AUE-OBJ-06 | Evolution Observation Object | AUE-P-06 | PASS | the post-execution measurement — expected result, actual result, deviation — attributed to the owner that measured it |
| AUE-OBJ-07 | Evolution Validation Object | AUE-P-07 | PASS | the verdict of each declared validation dimension over this evolution, with the failures that produced it |
| AUE-OBJ-08 | Evolution Verification Object | AUE-P-08 | PASS | the integrity verdicts and the gate that discharges each of them |
| AUE-OBJ-09 | Evolution Certification Object | AUE-P-09 | PASS | the proofs that make this evolution certifiable, and the located owner that would issue the certificate |
| AUE-OBJ-10 | Evolution Learning Object | AUE-P-10 | FAIL | what the outcome established and which assimilator holds it. Additional to the mandated set: a loop that cannot record what it learned repeats itself |
| AUE-OBJ-11 | Evolution History Object | AUE-P-11 | PASS | the append-only record of the whole transaction — who, what, why, when in logical time, where, context, evidence, decision, impact, validation, certification |

## Mandated fields

Every mandated field, and the measurement of whether every object of every conducted run carries it. A field declared non-empty and measured empty is a refusal, which is why the count is rendered rather than a checkmark.

| Field | Name | Non-empty required | Carried | Empty | Verdict |
|---|---|---|---|---|---|
| AUE-FLD-01 | evolution_id | PASS | 572 | 0 | PASS |
| AUE-FLD-02 | subject_identity | PASS | 572 | 0 | PASS |
| AUE-FLD-03 | previous_state | PASS | 572 | 0 | PASS |
| AUE-FLD-04 | target_state | PASS | 572 | 0 | PASS |
| AUE-FLD-05 | reason | PASS | 572 | 0 | PASS |
| AUE-FLD-06 | context | PASS | 572 | 0 | PASS |
| AUE-FLD-07 | dependencies | FAIL | 572 | 0 | PASS |
| AUE-FLD-08 | evidence | PASS | 572 | 0 | PASS |
| AUE-FLD-09 | plan | PASS | 572 | 0 | PASS |
| AUE-FLD-10 | execution_record | PASS | 572 | 0 | PASS |
| AUE-FLD-11 | validation_result | PASS | 572 | 0 | PASS |
| AUE-FLD-12 | verification_result | PASS | 572 | 0 | PASS |
| AUE-FLD-13 | certification_result | PASS | 572 | 0 | PASS |
| AUE-FLD-14 | lifecycle_state | PASS | 572 | 0 | PASS |

## Identity rule

Identity is derived, never minted: no corpus serial is consumed and no registry is written, so this register cannot become a second identity authority.

| Property | Value |
|---|---|
| prefix | UCOS-EVO- |
| width | 12 |
| derivation | engine/nucleus/evolution.py::Evolution |
| digest | engine/uckp/canonical.py::content_hash |
| inputs | candidate_class, subject_identity, reason, authority, object_kind |
| anonymity rule | An evolution object whose identity does not match the digest of its own declared inputs, or whose subject identity is empty, is anonymous. Anonymous evolution is refused, not reported. |
