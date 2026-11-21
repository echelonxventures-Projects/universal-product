"""Universal Assurance — the platform's evidence-bearing validation surface.

Turns an assurance *subject* into a planned, generated, executed and certified
assurance run whose result is a sealed, self-verifying evidence bundle. Subjects,
policies and checks are **declared as data** (``data/ucos-assurance-policy.json``,
``data/ucos-assurance-selfcheck.json``), so admitting one more subject, policy,
check or gate is a data entry and never a change to this package.

Module map
----------
=========================  ====================================================
Module                     Concern
=========================  ====================================================
:mod:`~.contracts`         ``AssuranceSubject`` and the wire value types
:mod:`~.config`            Subject/policy resolution from declared data
:mod:`~.policy`            Declared assurance policy and its binding rules
:mod:`~.planning`          Derives the assurance plan for a subject
:mod:`~.generation`        ``GeneratedCheck`` / ``GeneratedSuite`` derivation
:mod:`~.execution`         Executes a generated suite over a subject
:mod:`~.measurement`       Quantifies the outcome
:mod:`~.determinism`       Proves a run is a pure function of its inputs
:mod:`~.evidence`          ``ucos-assurance-evidence-{bundle,manifest}/1.0.0``
:mod:`~.certification`     Turns measured outcome into a certification verdict
:mod:`~.intelligence`      Read-only analytical projection over runs
:mod:`~.orchestrator`      Composes the phases into one assurance run
:mod:`~.registry`          Registration of subjects and suites
:mod:`~.errors`            ``AssuranceError`` taxonomy (fail-closed)
=========================  ====================================================

Reuse posture (Reuse First / No Parallel Authority)
---------------------------------------------------
This package owns the *generic, versioned* manifest and bundle format
(:mod:`~.evidence`) that programme-local manifests should generalise to rather than
re-implement. It creates no second hashing primitive, no second error taxonomy and
no second contract mechanism; those are reused from ``platform.foundation`` and
``engine.foundation``.

Determinism
-----------
Every module is pure over its inputs: no wall-clock, no RNG, no network and no
ambient state, so an identical subject and policy yield a byte-identical evidence
bundle (IMP-007 §5).

Authored to close a capability-discovery defect: this package carried fourteen
tracked modules and used absolute ``platform.universal_assurance.*`` imports, but
had no ``__init__.py``. It was therefore not a package by the repository's own
eligibility rule (a tracked ``__init__.py``) and was invisible to
:func:`intelligence.rie.discovery.discover` — an implemented capability that
Repository Truth could not see.
"""

from __future__ import annotations
