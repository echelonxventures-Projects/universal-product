# PHASE — CAA-INV-08 ENFORCEMENT COMPLETENESS DETERMINATION

> **Mission:** Determine whether CAA-INV-08's absence from `uga_engine.py`'s own gate output requires production-gate integration, is intentionally validation-only, is already protected through another mechanism, or something else.
> **Mode:** Discovery only. Repository evidence only. No code changes, no remediation.
> **Date:** 2026-08-13
> **HEAD:** `844c5056` (plus three uncommitted governance-binding/discovery phases from this session, unaffected)

---

## 1. CAA-INV-08 Intent

`engine/uckp/alignment.py:282-290`: `CAA-INV-08` / `ORTHOGONAL_ROLE_IS_SCOPE_BOUNDED_AND_NON_SUPREME` requires that *"every instrument bound under role ORTHOGONAL declares an explicit, non-unrestricted scope naming the axis its authority is bounded to, and role ORTHOGONAL never resolves as a supreme role."* Its implementation (`verify_binding()`, lines 745-755) checks each `subordinate_instruments` entry with `role: "ORTHOGONAL"`: it must carry a non-empty `owns` string, and that string must not contain any of five unrestricted-scope marker phrases (`_UNRESTRICTED_SCOPE_MARKERS`, lines 94-100: `"every constitutional matter"`, `"all constitutional authority"`, `"universal supremacy"`, `"unrestricted"`, `"everything in ucos"`). Today exactly one instrument holds this role: `CMG-000001` (added Phase 0.6).

The defining structural fact: an `ORTHOGONAL`-role instrument, by the role's own definition, **does not derive under `UCKP-LAW-0001`** and therefore carries no `constitutional_superior` block — and `CMG-000001` itself is a Markdown constitutional document, not a JSON instrument.

---

## 2. `uga_engine.py`'s Live Enforcement Architecture

`uga_engine.py`'s CAA measurement is built around `scan_authority_claims()` (line 914), which scans every **tracked JSON file** matching declared path suffixes for a top-level `authority` string key, and classifies each as a claim or a disclaimed-non-claim. This is a **JSON-instrument scanner by construction** — it has no code path that reads a Markdown document's prose for a role or a scope declaration.

The omission of CAA-INV-08 from `uga_engine.py`'s own invariant list is not silent. `alignment_state()` (line 947) contains an explicit, first-person comment (lines 959-964):

> *"Role ORTHOGONAL is exempt: it names an instrument that does NOT derive under UCKP-LAW-0001 (that is the whole content of 'orthogonal'), so it carries no constitutional_superior block to re-read and is not expected to be JSON at all — **CAA-INV-08 is what measures it instead (engine/uckp/alignment.py)**."*

A second, corroborating comment appears at the `CAA-INV-02` check itself (line 1371-1372): the `ORTHOGONAL`-role instrument is described as *"exempt from this sweep for the same reason it is exempt from CAA-INV-03: it names no superior to claim, by definition of the role (CAA-INV-08)."*

This is a **documented architectural decision**, not an oversight: `uga_engine.py`'s scanner is structurally scoped to JSON instruments with a `constitutional_superior`/`authority` shape, `CMG-000001` structurally falls outside that shape by the very definition of the `ORTHOGONAL` role, and the comment names the intended alternative measurement point by file.

---

## 3. Is CAA-INV-08 Actually Enforced in Production?

The named alternative — `engine.uckp.alignment.verify_binding()` — is not merely "importable." It is exercised by a real pytest test against the **live, on-disk binding**, not a stub:

- `engine/tests/uckp/test_alignment.py:47-49` — fixture `binding()` loads `(REPO / ALIGNMENT_BINDING_PATH).read_text(...)` and parses it: the actual `00-BOOK/DATA/constitutional-authority-alignment.json`, not a hand-built mock. The file's own docstring is explicit about why: *"each negative below is a mutation of the real binding, because a rejection test written against a hand-made stub proves only that the stub is wrong."*
- Line 161: `assert verify_binding(binding) == ()` — a test named for asserting the real binding is aligned, requiring **zero findings**, which necessarily includes every `CAA-INV-08` finding `verify_binding()` could produce.
- `pyproject.toml:200` — `testpaths = ["engine/tests", "platform/tests", "intelligence/tests"]` — `engine/tests/uckp/test_alignment.py` is unconditionally within pytest's collection scope; nothing excludes it.
- `verify.sh:114` — `run_stage "pytest + coverage gate (--cov-fail-under=90)" "$PY" -m pytest` is **Stage 2** of the repository's mandatory verification pipeline, and `verify.sh:16` opens with `set -euo pipefail`, making every stage fail-closed.
- `uga_engine.py gate` — the mechanism CAA-INV-01 through 07 run through — is invoked from exactly **one** place in the entire repository: `verify.sh:173` (Stage 6b). No Makefile target, shell script, or CI configuration was found invoking it standalone. Confirmed by repository-wide search (`grep -rln "uga_engine.py.*gate" --include="*.sh" --include="Makefile" --include="*.yml" --include="*.yaml" .` → `verify.sh` only).

**The consequence of stage ordering:** Stage 2 (pytest, which enforces CAA-INV-08 via the real-binding test) runs and must pass **before** Stage 6b (`uga_engine.py gate`, which enforces CAA-INV-01–07) is ever reached, in the one script that is the sole invocation site for both. A CAA-INV-08 violation would fail `test_alignment.py`'s real-binding assertion, which fails Stage 2, which halts `verify.sh` under `set -euo pipefail` — Stage 6b never runs at all in that scenario. There is no path through this repository's actual verification architecture in which CAA-INV-01–07 are checked while CAA-INV-08 is silently skipped.

---

## 4. Determination

Evaluating the four options against this evidence:

- **(A) Production gate integration required — Not supported.** This would mean building a Markdown-prose scanner inside `uga_engine.py`'s JSON-instrument-scanning architecture to re-check something `pytest` + `verify_binding()` already checks, in the same fail-closed pipeline, on the same real binding. That would be a second implementation of an already-enforced check — the kind of duplication this repository's own "Zero Duplication" discipline (UCKP Article 3, and this session's own `UCKP-INV-03` finding in the identity-relationship determination) argues against, not for.
- **(B) Intentionally validation-only — Not accurate as stated.** "Validation-only" implies CAA-INV-08 is checked but never blocks anything in production. That is false: `test_the_real_binding_is_aligned`'s assertion is a hard pytest failure on the live binding, gating Stage 2 of `verify.sh` — exactly as blocking as any `uga_engine.py gate` failure at Stage 6b. It is not "validation only" in the sense of being advisory or offline.
- **(C) Duplicate protection through another mechanism — Best fit, confirmed by evidence.** CAA-INV-08 is enforced, in production, fail-closed, on the real binding — by pytest (Stage 2), which is a mandatory, earlier stage of the same `verify.sh` pipeline `uga_engine.py gate` (Stage 6b) belongs to, and which `uga_engine.py gate` has no invocation path independent of. This is not a coincidental redundancy; the comment in `uga_engine.py:959-964` shows it was a deliberate design choice to measure ORTHOGONAL-role scope-boundedness at the one place structurally equipped to read it (the binding object itself, via `verify_binding()`), rather than force a JSON-scanner to parse Markdown prose.
- **(D) Other — Not needed.** (C) accounts fully for the evidence.

**Determination: (C).** CAA-INV-08 is not an enforcement gap. It is measured at a different, already-mandatory point in the same fail-closed pipeline, for a structural reason (JSON-scanner vs. Markdown-authored, non-deriving instrument) documented in `uga_engine.py`'s own source. Every real invocation path enforces it exactly once, before the JSON-instrument invariants ever run.

**This corrects a characterization carried in this session's own prior context** (noted in the working summary as "the discovered-but-unfixed gap that `uga_engine.py`'s live gate never checks CAA-INV-08"). That framing was accurate about the narrow fact — `uga_engine.py`'s own gate output does not list `CAA-INV-08` — but, absent this deeper investigation, implied an enforcement hole that direct evidence does not support. The pytest-mediated check is real, blocking, and unconditionally precedes the only script that runs `uga_engine.py gate` at all.

---

## 5. Non-Goals

- No file was modified. No remediation was implemented — none is recommended, since none is needed.
- No claim is made that `uga_engine.py`'s own output list should be edited to mention CAA-INV-08 for legibility (e.g., a comment noting "see pytest for this one") — that would be a documentation nicety, not a governance or enforcement question, and is left to the user's judgment rather than proposed here.
- No test was run beyond static reads of `alignment.py`, `uga_engine.py`, `test_alignment.py`, `verify.sh`, and `pyproject.toml` — sufficient to trace the enforcement path without executing the pipeline.
- No determination is made about whether other invariants might have a similar split-enforcement shape; this discovery was scoped to CAA-INV-08 specifically, as requested.

---

Stopping after discovery, as instructed.
