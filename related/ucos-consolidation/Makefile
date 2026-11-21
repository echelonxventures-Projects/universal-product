# UCOS Ω∞ — Canonical developer entry points.
#
# Every target delegates to the self-bootstrapping shell entry points so there is a
# single source of truth for environment behavior. None of these require a manually
# activated virtualenv.
#
#   make bootstrap     create/repair the canonical venv + pinned toolchain, validate it
#   make doctor        report + validate the environment (Python/pytest/pytest-cov/coverage/ruff)
#   make verify        THE canonical gate: lint + tests/coverage + governance enforcement
#   make verify-full   verify + read-only registration observation (register.sh --observe)
#   make repo-ops      complete repository operational verification (EPIC-PLAT-003, T5)
#   make lint          ruff only
#   make test          pytest + coverage gate only
#   make clean-venv    remove the disposable .ec1-venv (recreated on next bootstrap/verify)

.DEFAULT_GOAL := help
.PHONY: help bootstrap doctor env env-report verify verify-full lint test format format-check build clean clean-venv hooks repo-ops closure closure-gate closure-phase2 closure-phase2-gate closure-phase3 closure-phase3-gate

VENV := .ec1-venv
PY   := $(VENV)/bin/python

help:
	@echo "UCOS canonical targets:"
	@echo "  make bootstrap     set up + validate the canonical environment (fresh clone)"
	@echo "  make doctor        report + validate tool versions"
	@echo "  make env           UEG-000001 execution environment integrity gate"
	@echo "  make env-report    the full environment observation as JSON"
	@echo "  make verify        canonical verification (lint + tests/coverage + governance)"
	@echo "  make verify-full   verify + full registration/drift gate"
	@echo "  make repo-ops      complete repository operational verification (EPIC-PLAT-003)"
	@echo "  make rib           regenerate the UCOS-RIB-001 Repository Integration Blueprint (EPIC-001)"
	@echo "  make rib-gate      fail-closed Repository Integration Gate (twelve quality gates)"
	@echo "  make rib-self      UCOS-RIB-001 guards over its own surface"
	@echo "  make uakos-archive read-only integrity guard over the completed UAKOS/USIS phases"
	@echo "  make closure       regenerate UAKOS-CLOSURE-002 repository-closure artifacts"
	@echo "  make closure-gate  fail-closed closure gate (non-zero exit while gaps remain)"
	@echo "  make closure-phase2      regenerate PHASE-002 concept-graph reconciliation (outputs 20-35)"
	@echo "  make closure-phase2-gate fail-closed PHASE-002 gate (non-zero exit while concept gaps remain)"
	@echo "  make closure-phase3      regenerate PHASE-003 implementation planning (outputs 36-48)"
	@echo "  make closure-phase3-gate fail-closed PHASE-003 gate (non-zero exit while repository NOT-CLOSED)"
	@echo "  make selfaware     project every discovered capability into canonical knowledge"
	@echo "  make selfaware-gate     fail-closed when the capability register is behind the repo"
	@echo "  make rpi           re-run repository intelligence and persist every sealed artefact"
	@echo "  make rpi-report    read-only: the current cycle, its verdicts and validation rules"
	@echo "  make rpi-gate      fail-closed while intelligence is NOT-CERTIFIED or non-deterministic"
	@echo "  make homing        resolve each concept's canonical home from declared ownership"
	@echo "  make homing-gate   fail-closed while any canonical home is undeclared (RG-B01)"
	@echo "  make homing-recommend   the governance workload, reduced to its irreducible minimum"
	@echo "  make homing-draft  the NON-BINDING draft assignment document for governance review"
	@echo "  make constitution  measure every Foundation capability against UCOS-UFC-001"
	@echo "  make constitution-gate  fail-closed while any capability fails any article"
	@echo "  make maturity      the measured Foundation maturity, axis by axis"
	@echo "  make convergence   prove each constitutional model has exactly one implementation"
	@echo "  make convergence-gate   fail-closed while any surface is a competing authority"
	@echo "  make freeze        the Foundation freeze readiness determination (twelve criteria)"
	@echo "  make freeze-full   the same, executing the declared verification commands"
	@echo "  make freeze-gate   fail-closed unless every criterion is discharged by measurement"
	@echo "  make corpus        UKAP-001 D-1: discover exports, resolve the newest as canonical input"
	@echo "  make corpus-replay      re-derive corpus currency from corpus.json (no corpus root)"
	@echo "  make corpus-gate   fail-closed corpus-currency gate (non-zero while the corpus is stale)"
	@echo "  make assimilate    regenerate UAKOS-CLOSURE-008 assimilation registers (01-08)"
	@echo "  make assimilate-replay  re-render the registers from assimilation.json (no evidence tree)"
	@echo "  make assimilate-gate    fail-closed completion gate (non-zero while any object is unclassified)"
	@echo "  make roadmap       regenerate the UCOS-MXR-001 master execution roadmap (01-10)"
	@echo "  make roadmap-replay     re-render the roadmap from roadmap.json (recorded HEAD kept)"
	@echo "  make roadmap-gate  fail-closed execution-roadmap gate (deps resolved, order total)"
	@echo "  make lint          ruff lint only"
	@echo "  make format        ruff format (rewrite engine + platform)"
	@echo "  make format-check  ruff format --check (no writes; CI-style)"
	@echo "  make test          pytest + coverage gate only"
	@echo "  make build         build wheel + sdist via the canonical venv"
	@echo "  make hooks         install the git pre-commit hook (local automation)"
	@echo "  make cmg-gate      fail-closed meta-constitutional gate (CMG-000001)"
	@echo "  make uccep         observe the UCCEP-000000 constitutional determinations (emits only at or above the recorded tier)"
	@echo "  make uccep-gate    fail-closed AGGREGATE constitutional gate (all located gates)"
	@echo "  make uccep-boot    read-only aggregate gate (session/pre-commit tier)"
	@echo "  make uccep-full    aggregate gate including the heavy tier (suites + determinism); the emitting path"
	@echo "  make uccep-self    UCCEP guards over its own surface"
	@echo "  make aee           run the autonomous evolution loop to convergence"
	@echo "  make aee-observe   fast read-only pass; no located owner is invoked"
	@echo "  make aee-gate      fail-closed convergence gate over the observation vector"
	@echo "  make aee-closure   the loop including the heavy aggregate tier"
	@echo "  make aee-self      AEE guards over its own surface"
	@echo "  make lifecycle-closure   measure realization of the 45 UCL-000001 lifecycle stages"
	@echo "  make lifecycle-closure-fast   the same measurement without the coverage phase"
	@echo "  make lifecycle-closure-gate   fail-closed: exit 1 unless every closure claim is PROVEN"
	@echo "  make final-closure       Phase 8 fixed-point + Phase 9 pristine-clone measurement"
	@echo "  make final-closure-gate  fail-closed: exit 1 unless both phases meet their requirement"
	@echo "  make ucda          regenerate the UCDA-000001 decision-assimilation determinations"
	@echo "  make ucda-gate     fail-closed Implementation Evidence Gate (CEP-002 Art 28)"
	@echo "  make ucda-self     UCDA guards over its own surface"
	@echo "  make uer           regenerate the UER-000001 execution-resilience determinations (Ω∞-001A)"
	@echo "  make uer-gate      fail-closed Execution Resilience Gate (Ω∞-001A exit criteria)"
	@echo "  make uer-self      UER guards over its own surface"
	@echo "  make research      regenerate UCOS-URI-001 research intelligence (assimilation/registry/standards)"
	@echo "  make research-gate fail-closed Research Validation Gate (13 obligations)"
	@echo "  make publication   regenerate UCOS-UPI-001 publications (every registered format)"
	@echo "  make publication-gate fail-closed Publication Validation Gate (14 obligations)"
	@echo "  make publications  research + publication in dependency order"
	@echo "  make uei           regenerate the UEI-000001 evolution-intelligence determinations (Ω∞-001B)"
	@echo "  make uei-gate      fail-closed Evolution Intelligence Gate (Ω∞-001B exit criteria)"
	@echo "  make uei-self      UEI guards over its own surface"
	@echo "  make umk           regenerate the UMK-000001 Universal Meta-Kernel deliverables (PROGRAM-002)"
	@echo "  make umk-gate      fail-closed Universal Meta-Kernel constitutional gate"
	@echo "  make umk-self      UMK-000001 guards over its own surface"
	@echo "  make umk-certify   fail-closed UNCONDITIONAL certification (all 20 matrix dimensions = 100%)"
	@echo "  make uprf          regenerate the UPF-000001 Universal Provider Framework deliverables (PROGRAM-003)"
	@echo "  make uprf-gate     fail-closed Universal Provider Framework constitutional gate"
	@echo "  make uprf-self     UPF-000001 guards over its own surface"
	@echo "  make uprf-certify  fail-closed UNCONDITIONAL certification (all 20 matrix dimensions = 100%)"
	@echo "  make mcos          regenerate the MCOS-000001 Meta-Civilization Platform deliverables (PROGRAM-004)"
	@echo "  make mcos-gate     fail-closed Meta-Civilization Platform constitutional gate"
	@echo "  make mcos-self     MCOS-000001 guards over its own surface (incl. reuse-before-create)"
	@echo "  make mcos-certify  fail-closed UNCONDITIONAL certification (all 20 matrix dimensions = 100%)"
	@echo "  make ucef          regenerate the UCEF-000001 constitutional-evolution registers (CEP-009-AMD-001)"
	@echo "  make ucef-gate     fail-closed Constitutional Evolution Gate (CEP-009 ADDENDUM B exit criteria)"
	@echo "  make ucef-self     UCEF-000001 guards over its own surface (incl. open-world + reuse-before-create)"
	@echo "  make uar           regenerate the UCOS-UAR-001 Universal Analysis Registry"
	@echo "  make uar-gate      fail-closed Universal Analysis Registry gate"
	@echo "  make uar-self      UCOS-UAR-001 guards over its own surface (incl. zero-enumeration)"
	@echo "  make uapf          report the UAPF-000001 declared pipeline catalogue (derived plans)"
	@echo "  make uapf-gate     fail-closed Universal Autonomous Pipeline Framework gate"
	@echo "  make uapf-self     UAPF-000001 guards over its own surface (determinism + taxonomy)"
	@echo "  make uaep          regenerate the UAEP-000001 platform capability binding registers"
	@echo "  make uaep-gate     fail-closed Platform Binding Gate (every named capability resolves)"
	@echo "  make uaep-self     UAEP-000001 guards over its own surface (incl. open-world + reuse-before-create)"
	@echo "  make uaep-replay   prove the committed registers replay from the committed declaration"
	@echo "  make uaie          regenerate the UAIE-000001 architectural intelligence registers"
	@echo "  make uaie-gate     fail-closed Architectural Intelligence Gate (every faculty + register resolves)"
	@echo "  make uaie-self     UAIE-000001 guards (incl. register-plane, no-parallel-authority, evolution-contract)"
	@echo "  make uaie-replay   prove the committed architectural registers replay from the declaration"
	@echo "  make ucaf          regenerate the UCOS-UCAF-001 constitutional authority registers"
	@echo "  make ucaf-gate     fail-closed Constitutional Authority Gate (no authority undefined)"
	@echo "  make ucaf-self     UCOS-UCAF-001 guards (incl. knowledge-once + no-vacancy-promotion)"
	@echo "  make ucaf-replay   prove the committed authority registers replay from the declaration"
	@echo "  make baseline      regenerate the BASELINE-001 baseline-inheritance registers"
	@echo "  make baseline-gate fail-closed Baseline Inheritance Gate (chain resolves, succession explicit)"
	@echo "  make baseline-self BASELINE-001 guards (incl. record-immutability + no-elevation)"
	@echo "  make baseline-replay prove the committed baseline registers replay from the declaration"
	@echo "  make uis-gate      fail-closed Identity Conformance Gate (planes crosswalked, laws measured)"
	@echo "  make uis-self      UIS-001 guards (incl. no-identity-minting + bounds-tight)"
	@echo "  make uis-replay    prove the committed identity registers replay from the declaration"
	@echo "  make ucl           regenerate the UCL-000001 Universal Constitutional Lifecycle registers"
	@echo "  make ucl-gate      fail-closed Universal Constitutional Lifecycle Gate (graph discovered + executable)"
	@echo "  make ucl-self      UCL-000001 guards (incl. implementation-independence + open-world + cko-identity)"
	@echo "  make ucl-replay    prove the committed lifecycle registers replay from the declaration"
	@echo "  make ucl-execute   execute the discovered lifecycle for GOAL='...' (writes nothing)"
	@echo "  make acee          regenerate the ACEE-000001 Autonomous Constitutional Engineering registers"
	@echo "  make acee-gate     fail-closed Autonomous Constitutional Engineering Gate (goal plane bound + invariants measured)"
	@echo "  make acee-self     ACEE-000001 guards (incl. no-privileged-logic + reuse-before-create + reduction)"
	@echo "  make acee-replay   prove the committed engineering registers replay from the declaration"
	@echo "  make acee-engineer derive the engineering plan for GOAL='...' SUBJECT='...' (writes nothing)"
	@echo "  make urat          regenerate the UCOS-URAT-001 ratification registry (CEP-006 Art XVI)"
	@echo "  make urat-gate     fail-closed Ratification Registry Gate (every record located + verified)"
	@echo "  make urat-self     UCOS-URAT-001 guards (incl. discovery coverage + no-conferral)"
	@echo "  make urat-replay   prove the committed ratification registers replay from the declaration"
	@echo "  make utce          regenerate the UCOS-UTCE-001 traceability closure registers"
	@echo "  make utce-gate     fail-closed Constitutional Traceability Closure Gate (CEP-001 Art XVIII)"
	@echo "  make utce-self     UCOS-UTCE-001 guards (incl. read-only corpus + no-fabrication)"
	@echo "  make utce-replay   prove the committed traceability registers replay from the declaration"
	@echo "  make ufep          regenerate the UCOS-UFEP-001 freeze eligibility registers"
	@echo "  make ufep-gate     fail-closed Freeze Eligibility + Constitutional Completion Gate"
	@echo "  make ufep-self     UCOS-UFEP-001 guards (incl. no-freeze-performed + no-drift)"
	@echo "  make ufep-replay   prove the committed eligibility registers replay from the declaration"
	@echo "  make uaue          measure the autonomous evolution capability (every obligation, every run)"
	@echo "  make uaue-gate     fail-closed Autonomous Universal Evolution Gate (unknown subject traverses)"
	@echo "  make uaue-render   regenerate the evolution history + 18 registers (DERIVED TRUTH)"
	@echo "  make uaue-replay   prove the committed evolution surface replays from the declaration"
	@echo "  make completion    the full ordered convergence: authority -> ratification -> traceability -> certifier -> eligibility"
	@echo "  make clean         remove build/test caches (venv preserved)"
	@echo "  make clean-venv    remove the disposable .ec1-venv"

bootstrap:
	@./bootstrap.sh

doctor:
	@./doctor.sh

# UEG-000001 — the execution environment integrity gate, on its own. `make doctor` reports
# the version table; this reports IDENTITY: is this interpreter inside this repository, is
# sys.prefix the canonical venv, does pytest resolve here, do the required plugins import.
# It is what ./verify.sh Stage 0 runs, so a developer can ask the same question the gate
# asks without paying for a verification run.
env:
	@.ec1-venv/bin/python -m engine.execution_environment.gate --gate --command "make env"

# The full observation as JSON — every check, every finding, the fingerprint and the
# identity. `make env` elides long advisory lists; this never does.
env-report:
	@.ec1-venv/bin/python -m engine.execution_environment.gate --json --quiet --command "make env-report"

# UVI-000001 — one command per declared mode. The bare `make verify` is `./verify.sh`,
# whose default is now --change: impact-selected tests plus every governance gate, and
# NOT a certification. `make verify-full` is the certification contract and is what CI
# invokes. `make verify-explain` prints the plan the mode would execute and runs nothing.
verify:
	@./verify.sh

verify-fast:
	@./verify.sh --fast

verify-change:
	@./verify.sh --change

verify-integration:
	@./verify.sh --integration

verify-full:
	@./verify.sh --full

verify-explain:
	@./verify.sh --explain

# verify-cost-model: RE-MEASURE the shard cost table. It is a measurement, not a fact
# about the repository: a stale entry makes a plan slower and never wrong, so this is
# deliberately not wired into any gate. Run it after a change that moves test durations
# materially, then commit the regenerated table.
# zero-classes: STAGE every declared residue class. adr/0021 stated a principle and disclosed
# that nothing enforced it; the Zero-X programme reproduced that one level up, governing twelve
# classes with a plan document and no gate. This is that gate. It reports and refuses nothing —
# the refusals live in each class's own ratchet, where they can name the file.
.PHONY: zero-classes
zero-classes: bootstrap-quiet
	@$(PY) -c "import engine.omega_infinite.direct_callers, json; \
from engine.zero_class.measure import measure; \
print(json.dumps([r.to_dict() for r in measure()], indent=2))"

# conformance: MEASURE the agnosticism axes. adr/0021 (UAP-001) declares that nothing enforces
# the Universal Agnostic Architecture Principle; this is the measurement that changes it. It is
# deliberately not a gate — it reports dispositions and refuses nothing, and whether
# ENVELOPE_ONLY becomes a refusal is an operator decision this target does not take.
.PHONY: conformance
conformance: bootstrap-quiet
	@$(PY) -m engine.conformance.measure

verify-cost-model: bootstrap-quiet
	@$(PY) -m pytest -o addopts= --no-cov -q --durations=0 \
	  > .uvi-durations.txt 2>&1 || true
	@$(PY) -m engine.verification_intelligence.cost_model --from .uvi-durations.txt
	@rm -f .uvi-durations.txt

# merge-drivers: prove the ledger merge driver still does the two things it exists for.
#
# A merge driver runs ONLY during a merge, so nothing else would notice if it stopped working —
# and the failure is silent in the worst way: git falls back to a text merge and writes an
# identity ledger neither branch produced, which can resolve a collision by picking a side.
# ART-05 forbids that outright. This target is also what makes the driver REACHABLE: an artifact
# no import, plane or entry point reaches is code that cannot run, and Ω-4 refuses a rise in that
# population. Invoking it here is a real check, not a reachability formality.
merge-drivers: bootstrap-quiet
	@$(PY) 00-BOOK/tools/merge-union-ledger.py --selftest

# repo-ops: EPIC-PLAT-003 (Terminal T5) — one command performs complete repository
# operational verification by orchestrating the canonical engines/scripts. Delegates to
# repo-ops.sh, which self-heals the venv first (no parallel tooling).
repo-ops:
	@./repo-ops.sh

# P0-FINAL-CONVERGENCE-001 — the two producers no target named. `.gitignore` excludes
# /knowledge/ and determinism-evidence/ on the STATED grounds that they are "regenerated
# each run", but neither had a Makefile target, so nothing named them and nothing re-ran
# them: the exclusion asserted a regeneration no entry point performed. Both wrap an
# ALREADY-DECLARED console script (ucos-knowledge / ec1-determinism in pyproject.toml) —
# no new capability, only reachability, which is the same discharge REG-AUTO-001 P7
# requires of every other engine (a target, a workflow and a test must name it).
.PHONY: knowledge determinism-evidence determinism-init-gate
knowledge: bootstrap-quiet
	@$(PY) -m engine.knowledge.cli init

determinism-evidence: bootstrap-quiet
	@$(PY) -m engine.determinism.reproduce

# ===========================================================================
# BC-2 — cross-process initialization independence.
#
# THE PROPERTY THE DOUBLE BUILD STRUCTURALLY CANNOT SEE. `determinism-evidence` above
# compiles one blueprint twice and compares the bytes, and both builds run inside ONE
# interpreter — so every module global the second build reads is already whatever the
# first left it. That measures PATH REPRODUCIBILITY, which this repository has genuinely
# proven, and it has never measured whether a verdict depends on WHEN, or IN WHICH ORDER,
# the process was initialized. TA-26 records that the two are distinct properties;
# conflating them is the evidential error blocker BC-2 names.
#
# WHAT IT DOES. Three child interpreters over one canonical subject set — uninitialized,
# bootstrapped, and bootstrapped by the reverse arrival order — each reporting a verdict
# digest. A core kind whose verdict moves is refused; an extension kind's is disclosed,
# because "unknown before registration, known after it" is UCKP-ART-17's open extension
# space working rather than hidden state. Two admissible orders that disagree are refused
# unconditionally. Its own positive control must be detected or the run refuses itself.
#
# TWO PLANES, ONE COMMAND. This target and the ./verify.sh initialization-independence
# stage run identical argv, so they measure one thing rather than two, which is what
# UEC-L-06 requires. READ_ONLY: three subprocesses, no clock, no network, no write
# anywhere — not even to a gitignored path.
# ===========================================================================
determinism-init-gate: bootstrap-quiet
	@$(PY) -m engine.determinism.reproduce --gate --quiet \
	  || { echo "INITIALIZATION INDEPENDENCE REFUSED — a verdict moved with initialization; run 'make determinism-init-gate' without --quiet for the localised authority" >&2; exit 1; }
	@echo "determinism-init-gate: no core verdict moves with initialization, and no arrival order decides one"

# closure: UAKOS-CLOSURE-002 — regenerate the Vision-to-Repository closure artifacts
# (source inventory, concept inventory, coverage/traceability matrices, gap register,
# closure certificates). Deterministic, stdlib-only; never mutates the frozen corpus.
# SCOPE DECLARATION. CLOSURE_SKIP_CORPUS=1 is set on every invocation below, and on every
# other invocation site of this engine, as a STANDING DECLARATION rather than a speed
# option. The external corpus at ../UCOS is not present in any clone, so an undeclared
# run records `repo-only (undeclared - corpus absent)` with population_complete=False:
# the same population, bounded by accident instead of by declaration. Declaring it makes
# the disclosure identical here and in CI, which is what lets a reader trust it.
closure:
	@CLOSURE_SKIP_CORPUS=1 python3 00-MASTER/UAKOS-CLOSURE-002/closure_engine.py

# closure-gate: fail-closed standing gate — exits non-zero while any constitutional
# gap remains (conversation-only / upload-only / unhomed / duplicate / orphan).
closure-gate:
	@CLOSURE_SKIP_CORPUS=1 python3 00-MASTER/UAKOS-CLOSURE-002/closure_engine.py --gate

# closure-phase2: UAKOS-CLOSURE-002 · PHASE-002 — regenerate the concept-graph
# reconciliation views (outputs 20-35 + phase2.json) by REUSING the Phase-001 model
# (closure.json) and the canonical typed graph (00-BOOK/DATA/relationships.json).
# Deterministic, stdlib-only; no re-extraction, no fabrication. Depends on `closure`.
closure-phase2: closure
	@python3 00-MASTER/UAKOS-CLOSURE-002/phase2_engine.py

# closure-phase2-gate: fail-closed standing gate for the concept layer — exits non-zero
# while any concept remains unhomed / duplicated / orphaned.
closure-phase2-gate: closure
	@python3 00-MASTER/UAKOS-CLOSURE-002/phase2_engine.py --gate

# closure-phase3: UAKOS-CLOSURE-002 · PHASE-003 — regenerate the canonical implementation
# PLANNING artifacts (outputs 36-48 + phase3.json). Consumes the frozen PHASE-002 baseline
# (closure.json) and produces constitutional plans only — classification, destination, owner,
# dependency DAG, waves, priority, contracts, enrichment execution plan, closure projection.
# Planning only: never modifies Repository Truth, never implements automatically.
closure-phase3: closure-phase2
	@python3 00-MASTER/UAKOS-CLOSURE-002/phase3_engine.py

# closure-phase3-gate: fail-closed — non-zero exit while the repository is NOT-CLOSED
# (planning delivered, authorized execution still pending).
closure-phase3-gate: closure-phase2
	@python3 00-MASTER/UAKOS-CLOSURE-002/phase3_engine.py --gate

# selfaware: REPOSITORY SELF-AWARENESS — project every discovered capability into the
# canonical knowledge layer so the reuse gate can see the repository's own implementation.
# Discovery is owned by intelligence/rie (git ls-files eligibility boundary, any depth);
# this only projects its catalogue into UCKO-CAP-* facts. Deterministic and idempotent:
# a second run reports every capability unchanged and rewrites nothing.
.PHONY: selfaware selfaware-report selfaware-gate
selfaware:
	@python3 -m intelligence.rie build
	@python3 -m engine.knowledge.cli capabilities --write
	@python3 -m engine.knowledge.cli validate >/dev/null && echo "canonical base: valid"

# selfaware-report: read-only — what the projection WOULD change, plus coverage before/after.
selfaware-report:
	@python3 -m engine.knowledge.cli capabilities

# selfaware-gate: fail-closed — non-zero exit while the canonical capability register has
# fallen behind the repository (a capability was added, changed or removed without its
# canonical knowledge). This is the guard that keeps the reuse engine from going blind again.
selfaware-gate:
	@python3 -m engine.knowledge.cli capabilities --gate >/dev/null \
	  || { echo "SELF-AWARENESS STALE — run 'make selfaware' (capability register is behind the repository)" >&2; exit 1; }
	@echo "self-awareness: canonical capability register is current"

# ---------------------------------------------------------------------------
# Ω-E06 M-04 / W1-4 — REPOSITORY INTELLIGENCE. The producer had no re-run target, so
# nothing re-ran it: its certificate went 142 commits and 500 files stale while still
# being read as current. A producer nobody re-runs does not measure the repository, it
# measures whenever somebody last remembered to. These targets bind the producer to an
# entry point and to a gate, which is the whole of the M-04 disposition (EXTEND).
#
# HONEST LIMIT: emit writes to .runtime/repository-intelligence/, and .gitignore:12
# excludes .runtime/. The artefacts are therefore OUTSIDE Repository Truth — re-running
# refreshes them locally but commits nothing a clone can reproduce. Staleness returns
# the moment this is not run. Making the certificate durable requires W0-1, the
# constitutional determination on .gitignore against the twelve Truth zones. These
# targets close the "nothing re-runs it" half of M-04 and cannot close the other half.
.PHONY: rpi rpi-report rpi-gate
rpi: bootstrap-quiet
	@$(PY) -m platform.repository_intelligence.cli emit

# rpi-report: read-only — the current cycle with its dimension verdicts and validation
# rules, persisting nothing. Non-zero while the repository is NOT-CERTIFIED.
rpi-report: bootstrap-quiet
	@$(PY) -m platform.repository_intelligence.cli scan

# rpi-gate: fail-closed on BOTH halves of the M-04 defect, in the order that reports the
# more actionable failure first.
#
# certify re-derives the certificate from the live repository, so a NOT-CERTIFIED verdict
# is a finding about the repository and never a stale file being re-read.
#
# verify then proves the producer is deterministic: two scans of one substrate must yield
# byte-identical artefacts. It is fail-closed on an INCONCLUSIVE proof too — a substrate
# that changed mid-proof reports deterministic=False — so a concurrent writer cannot be
# mistaken for a pass.
rpi-gate: bootstrap-quiet
	@$(PY) -m platform.repository_intelligence.cli certify >/dev/null \
	  || { echo "REPOSITORY INTELLIGENCE NOT-CERTIFIED — run 'make rpi-report' for the blocking dimension and rule" >&2; exit 1; }
	@$(PY) -m platform.repository_intelligence.cli verify >/dev/null \
	  || { echo "REPOSITORY INTELLIGENCE NON-DETERMINISTIC — one substrate produced two different artefact sets; run 'make rpi-report'" >&2; exit 1; }
	@echo "repository intelligence: certified, and one substrate reproduces one artefact set"

# homing: CANONICAL HOME RESOLUTION — report which registered artifact each concept's
# ownership is DECLARED by, and which concepts Repository Truth does not answer. Reads
# only; assigns nothing. Ownership must be assigned by governed determination and must
# never be implied (CEP-002 14.2), so an undeclared home is reported, never guessed.
#
# Ω-A07 CONVERGENCE: this target now invokes the ONE ownership determination — the Universal
# Ownership Framework, specialised by platform/universal_foundation/catalog/ucos-consolidation.json.
# The engine-side resolver it used to call (engine/knowledge/homing.py) is RETIRED: two
# determinations over one population reported different numbers, which UCOS-UFC-001 UFC-16
# forbids. The converged determination reproduces the retired measurement exactly (151 declared,
# 390 unresolved over 541 subjects) and settles by declared zone precedence the two contests the
# retired rule broke with a hardcoded realization special case. Supersession is enforced, not
# documented: `make convergence-gate` fails if the retired module reappears.
.PHONY: homing homing-gate homing-recommend homing-draft
homing: bootstrap-quiet
	@$(PY) -m platform.universal_ownership.cli homing

# homing-gate: fail-closed — non-zero exit while any concept's canonical home is
# undeclared. This is the standing measurement of RG-B01 / WP-UAKOS-CLOSURE-009-001; it
# goes green only when a Governance Authority determination has declared the residue.
homing-gate: bootstrap-quiet
	@$(PY) -m platform.universal_ownership.cli homing --gate >/dev/null 2>&1 \
	  || { echo "CANONICAL OWNERSHIP UNDECLARED — run 'make homing' for the per-concept residue (RG-B01)" >&2; exit 1; }
	@echo "canonical ownership: every concept carries a declared canonical home"

# homing-recommend: GOVERNANCE MINIMISATION. Every deterministic capability has already run, so
# what remains is measured and split three ways: the RATIFIABLE residue, where a deterministic
# provider can state the assignment an authority would ratify together with its located basis;
# the REMEDIABLE residue, where the determination diagnosed a named eligibility deficit at a named
# locator, so what is needed is an ACT (register the artifact, give it the declared form, move it
# out of derived residue) and not a decision; and the GOVERNANCE MINIMUM, which is neither. Only
# the third number is work an authority must originate — reporting the second as "irreducible"
# billed a mechanical omission as constitutional ambiguity. A recommendation is never ownership
# and no engine reads one as evidence.
homing-recommend: bootstrap-quiet
	@$(PY) -m platform.universal_ownership.cli recommend

# homing-draft: emit the NON-BINDING draft assignment document a governing authority would
# review. It carries ratified:false and is deliberately a separate document from the governed
# ownership catalogue, so ratification stays an explicit constituent act.
homing-draft: bootstrap-quiet
	@$(PY) -m platform.universal_ownership.cli recommend --draft --json


# --- Ω-A07: the Universal Foundation Constitution ------------------------------------------
# UCOS-UFC-001 — the ONE law every Foundation capability obeys: sixteen articles over thirteen
# governed domains, each bound to exactly one executable probe. The law names no capability; its
# population is platform/universal_foundation/catalog/foundation-capabilities.json, and UFC-09 is
# measured by proving no governing module contains any identity from it. Registering a Foundation
# capability is therefore an entry in that document and requires NO change to any engine.
#
# A probe that cannot execute reports FAULT, never a pass. Absence of evidence is never evidence.
.PHONY: constitution constitution-gate maturity convergence convergence-gate freeze freeze-gate freeze-full
constitution: bootstrap-quiet
	@$(PY) -m platform.universal_foundation.constitution_cli conform

# constitution-gate: fail-closed — non-zero while any capability fails or faults any article.
constitution-gate: bootstrap-quiet
	@$(PY) -m platform.universal_foundation.constitution_cli conform --gate >/dev/null \
	  || { echo "FOUNDATION NON-CONFORMANT — run 'make constitution' for the article and capability" >&2; exit 1; }
	@echo "universal foundation: every capability conforms to every constitutional article"

# maturity: the measured maturity of the platform, axis by axis. Each of the fourteen axes is
# reached only when every gate declared to prove it passed, so this is a measurement over
# executed probes and never a status anybody typed.
maturity: bootstrap-quiet
	@$(PY) -m platform.universal_foundation.constitution_cli maturity

# convergence: prove each constitutional model — Repository Truth, ownership, assimilation,
# measurement, dependency, implementation — has exactly ONE live implementation. Relations are
# verified, not asserted: a SUPERSEDED surface must be absent from the tree, a DELEGATES surface
# must really import the canonical owner (measured over its import graph), a GOVERNED narrower
# authority must restate none of the canonical law, and a PROJECTION must hold no executable
# determination.
convergence: bootstrap-quiet
	@$(PY) -m platform.universal_foundation.constitution_cli convergence

# convergence-gate: fail-closed — non-zero while any surface holds a competing constitutional
# definition. This is the gate that keeps a retired implementation from quietly returning.
convergence-gate: bootstrap-quiet
	@$(PY) -m platform.universal_foundation.constitution_cli convergence --gate >/dev/null \
	  || { echo "COMPETING CONSTITUTIONAL AUTHORITY — run 'make convergence' for the model and surface" >&2; exit 1; }
	@echo "constitutional convergence: every model has exactly one live implementation"

# freeze: the Foundation freeze readiness determination over the twelve declared criteria.
# UNMEASURED is not a pass: a criterion whose evidence was not gathered withholds readiness as
# firmly as a failure, because a freeze declared over unmeasured criteria is the failure a freeze
# exists to prevent. This target DETERMINES ELIGIBILITY and never performs a freeze.
freeze: bootstrap-quiet
	@$(PY) -m platform.universal_foundation.constitution_cli freeze

# freeze-full: the same determination including the declared verification commands, so the
# suite criterion is measured rather than reported UNMEASURED. This is the emitting path for a
# freeze decision.
freeze-full: bootstrap-quiet
	@$(PY) -m platform.universal_foundation.constitution_cli freeze --with-suites

# freeze-gate: fail-closed — non-zero unless every declared criterion is discharged by measured
# evidence.
freeze-gate: bootstrap-quiet
	@$(PY) -m platform.universal_foundation.constitution_cli freeze --with-suites --gate >/dev/null \
	  || { echo "FOUNDATION NOT FREEZE-READY — run 'make freeze' for the criterion and its blockers" >&2; exit 1; }
	@echo "universal foundation: every freeze criterion is discharged by measured evidence"


# corpus: UKAP-001 / D-1 — CORPUS CURRENCY RESTORATION. Discovers every available ChatGPT
# export (archive form under the corpus roots + in-repository conversation exports),
# identifies the NEWEST by content / git commit order (never by filename or filesystem
# mtime), resolves it as the canonical assimilation input, measures what the committed
# baselines actually consumed, and fails closed when a newer export exists but is ignored.
# Deterministic, stdlib-only; mutates nothing outside 00-MASTER/UKAP-001/. Corpus roots come
# from UKAP_CORPUS_ROOTS, else UAKOS_EVIDENCE_ROOT (the existing evidence-root contract).
.PHONY: corpus corpus-replay corpus-gate
corpus:
	@python3 00-MASTER/UKAP-001/corpus_engine.py

# corpus-replay: re-derive the determination from the committed corpus.json alone — proves
# the currency record is self-contained (no corpus root required). The in-repo export class
# and both consumption measurements are still re-measured live, so a replay is never vacuous.
corpus-replay:
	@python3 00-MASTER/UKAP-001/corpus_engine.py --render

# corpus-gate: fail-closed — non-zero exit while any corpus class is STALE: a newer export
# exists but is ignored, an assimilated conversation is absent from the canonical export, an
# in-repo export was never reconstructed, or assimilated export content has drifted.
corpus-gate:
	@python3 00-MASTER/UKAP-001/corpus_engine.py --render --gate

# assimilate: UAKOS-CLOSURE-008 — constitutional assimilation & repository completion.
# Consumes the FROZEN knowledge-assimilation base + tri-source verification determination
# (read-only, hashed) and drives every verified knowledge object into exactly one of six
# terminal states, homing every approved item with a destination, owner, constitutional
# authority, wave and dependency chain. Deterministic, stdlib-only; mutates nothing outside
# 00-MASTER/UAKOS-CLOSURE-008/. Set UAKOS_EVIDENCE_ROOT to relocate the evidence tree.
#
# CORPUS CURRENCY (UKAP-001 D-1): every assimilation target depends on `corpus-gate`, so no
# assimilation artifact can be produced or certified while the corpus is stale. This is the
# dependency-closure guarantee — currency is verified BEFORE knowledge is assimilated.
.PHONY: assimilate assimilate-replay assimilate-gate
assimilate: corpus-gate
	@python3 00-MASTER/UAKOS-CLOSURE-008/assimilation_engine.py

# assimilate-replay: re-render every register from the in-repo assimilation.json alone —
# proves the repository is self-contained (no external evidence tree required).
assimilate-replay: corpus-gate
	@python3 00-MASTER/UAKOS-CLOSURE-008/assimilation_engine.py --render

# assimilate-gate: fail-closed — non-zero exit while any verified knowledge object is
# unclassified, unhomed, unowned, untraceable, or any semantic mapping fails to resolve.
assimilate-gate: corpus-gate
	@python3 00-MASTER/UAKOS-CLOSURE-008/assimilation_engine.py --render --gate

# roadmap: UCOS-MXR-001 — master execution roadmap (post UAKOS-CLOSURE-008). Compiles the
# CURRENT REPOSITORY STATE (MCP-002/MCP-003 state of record, UCDA-000001 work packages, the RIE
# intelligence artifacts, closure.json, assimilation.json + HEAD band evidence) into a
# deterministic execution program: backlog, dependency graph, waves, critical path, parallel
# groups, validation/certification gates and the readiness determination. No discovery, no
# reconciliation; mutates nothing outside 00-MASTER/UCOS-MXR-001/.
.PHONY: roadmap roadmap-replay roadmap-gate
roadmap:
	@python3 00-MASTER/UCOS-MXR-001/roadmap_engine.py

# roadmap-replay: re-render 01..10 from the committed roadmap.json alone. A committed artifact
# can never contain the sha of the commit that carries it, so the DRIFT check must replay
# (preserving the recorded HEAD) while `roadmap-gate` proves the program is still derivable.
roadmap-replay:
	@python3 00-MASTER/UCOS-MXR-001/roadmap_engine.py --render

# roadmap-gate: fail-closed — non-zero exit unless the roadmap is executable (acyclic graph,
# every dependency resolved, every item located/named-owner/validatable/rollback-able, no READY
# item behind a non-executable prerequisite, total order).
roadmap-gate:
	@python3 00-MASTER/UCOS-MXR-001/roadmap_engine.py --gate

# lint/test self-heal the venv first so they never hit "command not found".
lint: bootstrap-quiet
	@$(PY) -m ruff check engine platform

# format/format-check reuse the same pinned ruff as lint (no new tooling).
format: bootstrap-quiet
	@$(PY) -m ruff format engine platform

format-check: bootstrap-quiet
	@$(PY) -m ruff format --check engine platform

test: bootstrap-quiet
	@$(PY) -m pytest

# build mirrors the EC-1 CI "Build (wheel + sdist)" step, run through the canonical
# venv (pinned build==1.2.2, installed on demand so it never pollutes the [dev] set).
build: bootstrap-quiet
	@$(PY) -m pip install --disable-pip-version-check --quiet build==1.2.2 && $(PY) -m build

# hooks: opt-in local automation; reuses scripts/ucos-env.sh + pinned ruff.
hooks:
	@./scripts/install-hooks.sh

.PHONY: bootstrap-quiet
bootstrap-quiet:
	@./bootstrap.sh >/dev/null

# clean removes regenerable build/test caches only; the venv is preserved (use
# clean-venv for that). No source, generated register, or corpus path is touched.
clean:
	@rm -rf .pytest_cache .ruff_cache .mypy_cache build dist ./*.egg-info .coverage coverage.xml \
		&& echo "removed build/test caches (venv preserved — run 'make clean-venv' to reset it)"

clean-venv:
	@rm -rf $(VENV) && echo "removed $(VENV) (run 'make bootstrap' to recreate)"


# cmg-gate: fail-closed meta-constitutional gate (CMG-000001 Article L, LXVI.7).
# Additive only — no existing target, recipe, or dependency above is altered.
# Exit 0 zero findings · 1 findings · 2 fail-closed abort.
.PHONY: cmg-gate
cmg-gate:
	@./00-CMG/tools/cmg-gate.sh


# uccep: UCCEP-000000 — Universal Continuous Constitutional Evolution Programme.
# Additive only — no existing target, recipe, or dependency above is altered.
#
# The AGGREGATE constitutional gate. It executes the gates that already exist and are
# already owned (cmg-gate, ukb enforce/validate, the closure engines, repository health,
# graph invariants, intelligence determinism, verify.sh, the determinism double-build),
# then emits the fifteen programme determinations + the assimilation/findings register
# into 00-MASTER/UCCEP-000000/. AUTHORITY = NONE (DERIVED TRUTH). Stdlib only; writes
# nothing outside its own operational-memory directory (guarded, fail-closed).
#
# Adding a programme, gate, check, invariant or finding is an entry in
# 00-MASTER/UCCEP-000000/uccep-bindings.json and requires NO change to any engine.
#
# OBSERVATION IS NOT EMISSION. Every target below observes and reports its verdict.
# A target WRITES only when the tier it requests is at least as wide as the tier of the
# determination Repository Truth already records, so a narrower run leaves the tracked
# tree byte-identical instead of replacing a wider determination with a narrower one.
# `uccep-full` is therefore the emitting path whenever the recorded determination is at
# the full tier, and `uccep` / `uccep-boot` are observation. Narrowing the recorded
# determination is an explicit constituent act (`--authorize-emission`), never a side
# effect of running a gate. Enforced by `--check-observation` (CK-SELF-OBSERVATION,
# blocking, boot tier).
#
# Exit 0 every executed blocking check passed · 1 a blocking check failed ·
# 2 fail-closed abort (declaration unusable — no verdict may be asserted).
.PHONY: uccep uccep-gate uccep-boot uccep-full uccep-self
uccep:
	@python3 00-MASTER/UCCEP-000000/uccep_engine.py --tier standard

uccep-gate:
	@python3 00-MASTER/UCCEP-000000/uccep_engine.py --tier standard --gate

uccep-boot:
	@python3 00-MASTER/UCCEP-000000/uccep_engine.py --tier boot --gate

uccep-full: bootstrap-quiet
	@python3 00-MASTER/UCCEP-000000/uccep_engine.py --tier full --gate

# uccep-self: the programme's guards over its own surface — declaration integrity,
# zero-enumeration / data-driven proof, forbidden-write scope, self-determinism, and the
# separation of observation from emission.
uccep-self:
	@python3 00-MASTER/UCCEP-000000/uccep_engine.py --check-declaration
	@python3 00-MASTER/UCCEP-000000/uccep_engine.py --check-no-enumeration
	@python3 00-MASTER/UCCEP-000000/uccep_engine.py --check-write-scope
	@python3 00-MASTER/UCCEP-000000/uccep_engine.py --check-determinism
	@python3 00-MASTER/UCCEP-000000/uccep_engine.py --check-observation


# ucda: UCDA-000001 — Constitutional Decision Assimilation.
# Additive only — no existing target, recipe, or dependency above is altered.
#
# The executable expression of the Implementation Evidence Gate legislated by
# 00-CEP/CEP-002 Article 28 (CEP-002-AMD-002). It asserts that no constitutionally
# agreed decision remains only in conversation history: every decision declared in
# 00-MASTER/UCDA-000001/ucda-decisions.json must name the LOCATED register it was
# recorded in, occupy exactly one stage of the mandatory lifecycle, and carry exactly
# one disposition from the closed set, with the evidence that disposition requires
# resolving against the repository.
#
# AUTHORITY = NONE (DERIVED TRUTH). Stdlib only; writes nothing outside its own
# operational-memory directory (guarded, fail-closed). Adding a decision, a work
# package, a stage or a disposition is an entry in the declaration and requires NO
# change to the engine.
#
# The gate is also bound into the aggregate gate as G-14 / CK-DECISION-EVIDENCE, so
# `make uccep-gate` and the CI aggregate gate execute it too.
#
# Exit 0 gate OPEN · 1 gate CLOSED (a decision is undispositioned) ·
# 2 fail-closed abort (declaration unusable — no verdict may be asserted).
.PHONY: ucda ucda-gate ucda-self
ucda:
	@python3 00-MASTER/UCDA-000001/ucda_engine.py

ucda-gate:
	@python3 00-MASTER/UCDA-000001/ucda_engine.py --gate

# ucda-self: the programme's guards over its own surface — declaration integrity
# (lifecycle ordering/reachability/terminality, closed disposition set, per-disposition
# evidence obligations), zero-enumeration / data-driven proof, forbidden-write scope,
# self-determinism.
ucda-self:
	@python3 00-MASTER/UCDA-000001/ucda_engine.py --check-declaration
	@python3 00-MASTER/UCDA-000001/ucda_engine.py --check-no-enumeration
	@python3 00-MASTER/UCDA-000001/ucda_engine.py --check-write-scope
	@python3 00-MASTER/UCDA-000001/ucda_engine.py --check-determinism



# uer: UER-000001 — Universal Execution Resilience (UCOS Ω∞ Programme Ω∞-001A).
# Additive only — no existing target, recipe, or dependency above is altered.
#
# The executable expression of the Execution Resilience contract. It creates no
# checkpoint, journal, recovery, atomic-write, resume, ledger, continuation, replay,
# repository-safety or health engine: every one already exists and is certified
# (engine/runtime/execution — EPIC-RTE-002; platform/repository_operations;
# 00-BOOK/tools/governance_telemetry.py; the master recovery/execution instruments).
# It BINDS them into one contract that every future autonomous programme inherits, and
# verifies from Repository Truth that each binding resolves, then emits the fourteen
# constitutional deliverables — the last of which is the continuation package — into
# 00-MASTER/UER-000001/.
#
# AUTHORITY = NONE (DERIVED TRUTH). Stdlib only; writes nothing outside its own
# operational-memory directory (guarded, fail-closed). Binding a newly proven gap is an
# entry in 00-MASTER/UER-000001/uer-resilience.json and requires NO change to the engine.
#
# Exit 0 gate OPEN · 1 gate CLOSED (a capability/validation/exit criterion is unsatisfied)
# · 2 fail-closed abort (declaration unusable — no verdict may be asserted).
.PHONY: uer uer-gate uer-self
uer:
	@python3 00-MASTER/UER-000001/uer_engine.py

uer-gate:
	@python3 00-MASTER/UER-000001/uer_engine.py --gate

# uer-self: the programme's guards over its own surface — declaration integrity
# (every home/evidence/programme reference resolves; every pipeline step, validation and
# exit criterion is bound to a declared capability/validation), zero-enumeration /
# data-driven proof, forbidden-write scope, self-determinism.
uer-self:
	@python3 00-MASTER/UER-000001/uer_engine.py --check-declaration
	@python3 00-MASTER/UER-000001/uer_engine.py --check-no-enumeration
	@python3 00-MASTER/UER-000001/uer_engine.py --check-write-scope
	@python3 00-MASTER/UER-000001/uer_engine.py --check-determinism



# urrc: URRC-000001 — Repository Reality & Constitutional Completion.
# Additive only — no existing target, recipe, or dependency above is altered.
#
# The executable expression of the programme charter. It creates no catalogue, no
# registry, no roadmap, no graph, no sequence and no authority: where a canonical owner
# already exists it is bound by pointer and never restated; where none exists the fact is
# derived from declared machine-readable substrate; where honest derivation is impossible
# the absence is declared with a counted probe and the evidence class that would be
# required. Every write lands inside 00-MASTER/URRC-000001/ (guarded, fail-closed).
#
# AUTHORITY = NONE (DERIVED TRUTH). Stdlib only. Adding a deliverable, matrix, gate,
# substrate, derivation or binding mode is an edit to
# 00-MASTER/URRC-000001/urrc-bindings.json and requires NO change to the engine.
#
# Exit 0 every blocking gate passed · 1 a blocking gate failed · 2 fail-closed abort
# (the declaration or a required substrate is unusable, so no verdict may be asserted).
.PHONY: urrc urrc-gate urrc-self
urrc:
	@python3 00-MASTER/URRC-000001/urrc_engine.py

urrc-gate:
	@python3 00-MASTER/URRC-000001/urrc_engine.py --gate

# urrc-self: the eight guards over the programme's own surface — declaration integrity,
# zero-enumeration (data-driven proof), forbidden-write scope, self-determinism, substrate
# usability, no-fabrication, reuse-before-create (the zero-duplication invariant), and the
# law-namespace guard that proves no emitted byte reintroduces the ratified law token.
urrc-self:
	@python3 00-MASTER/URRC-000001/urrc_engine.py --check-declaration
	@python3 00-MASTER/URRC-000001/urrc_engine.py --check-no-enumeration
	@python3 00-MASTER/URRC-000001/urrc_engine.py --check-write-scope
	@python3 00-MASTER/URRC-000001/urrc_engine.py --check-determinism
	@python3 00-MASTER/URRC-000001/urrc_engine.py --check-substrate
	@python3 00-MASTER/URRC-000001/urrc_engine.py --check-no-fabrication
	@python3 00-MASTER/URRC-000001/urrc_engine.py --check-reuse-before-create
	@python3 00-MASTER/URRC-000001/urrc_engine.py --check-law-namespace



# uei: UEI-000001 — Universal Evolution Intelligence (UCOS Ω∞ Programme Ω∞-001B).
# Additive only — no existing target, recipe, or dependency above is altered.
#
# The executable expression of the Evolution Intelligence contract. It creates no
# observation, learning, optimization, recommendation, impact-analysis, simulation,
# discovery, planning, execution, measurement or evolution mechanism: every one already
# exists and is certified (platform/observability — EC2-EPIC-013; engine/knowledge — UKDA;
# engine/compiler/optimization.py — EPIC-003; engine/graph/architecture over the certified
# knowledge graph — EPIC-010 over EPIC-002; engine/determinism — EPIC-004;
# engine/runtime/execution — EPIC-005; platform/repository_operations;
# platform/runtime_operations — EC2-EPIC-012; platform/coverage; platform/measurement;
# intelligence/rie). It BINDS them into one contract that every future autonomous
# programme inherits, places each capability under a located governing instrument, and
# verifies from Repository Truth that each binding resolves — then emits the twenty-three
# deliverables, the last of which is the continuation package, into 00-MASTER/UEI-000001/.
#
# AUTHORITY = NONE (DERIVED TRUTH). Stdlib only; writes nothing outside its own
# operational-memory directory (guarded, fail-closed). Binding a newly proven capability is
# an entry in 00-MASTER/UEI-000001/uei-evolution.json and requires NO change to the engine.
#
# Exit 0 gate OPEN · 1 gate CLOSED (an uncovered, ungoverned or unsatisfied element is
# present) · 2 fail-closed abort (declaration unusable — no verdict may be asserted).
.PHONY: uei uei-gate uei-self
uei:
	@python3 00-MASTER/UEI-000001/uei_engine.py

uei-gate:
	@python3 00-MASTER/UEI-000001/uei_engine.py --gate

# uei-self: the six guards over the programme's own surface — declaration integrity (every
# home/evidence/instrument/programme reference resolves; every deliverable, lifecycle step,
# standing loop, validation, exit criterion and governance obligation is bound), zero-
# enumeration / data-driven proof, forbidden-write scope, self-determinism, the governance
# guard that proves no declared capability is left ungoverned, and the reuse-before-create
# guard that proves no bound home lies inside this programme's own home.
uei-self:
	@python3 00-MASTER/UEI-000001/uei_engine.py --check-declaration
	@python3 00-MASTER/UEI-000001/uei_engine.py --check-no-enumeration
	@python3 00-MASTER/UEI-000001/uei_engine.py --check-write-scope
	@python3 00-MASTER/UEI-000001/uei_engine.py --check-determinism
	@python3 00-MASTER/UEI-000001/uei_engine.py --check-governance
	@python3 00-MASTER/UEI-000001/uei_engine.py --check-reuse-before-create



# research / publication: UCOS-URI-001 Universal Research Intelligence and
# UCOS-UPI-001 Universal Publication Intelligence.
# Additive only — no existing target, recipe, or dependency above is altered.
#
# UCOS-URI-001 assimilates the repository's own canonical knowledge, decision record,
# concept closure and generated corpus measurements into a research corpus of claims,
# findings, contribution areas and standards records — then registers it append-only
# (Knowledge-Once + hash chain), analyses standards conformance, and validates thirteen
# fail-closed obligations. Every record stores a REFERENCE to canonical content; none
# stores a copy (UCKO-PRIN-0001; the anti-pattern UCKO-ANTI-0001).
#
# UCOS-UPI-001 generates every publication format from that corpus: research paper,
# journal article, conference paper (full/short/extended-abstract/poster), white paper,
# technical article, patent draft, standards proposal, technical report, preprint,
# review, thesis/book chapter, RFC-style memo, briefs, datasheet and tutorial — plus any
# format registered afterwards. A format is DATA (a descriptor), not code: adding one is
# an entry in intelligence/UCOS-UPI-001/publication-formats.json (or a runtime
# register_format call) and requires NO engine change. Fourteen fail-closed obligations
# are validated, including an executed proof that the format space is open.
#
# AUTHORITY = NONE (DERIVED TRUTH). Stdlib only. Every write lands inside
# intelligence/UCOS-URI-001/ or intelligence/UCOS-UPI-001/ (guarded, fail-closed).
#
# Exit 0 gate OPEN · 1 gate CLOSED (an obligation is unsatisfied or output is
# non-deterministic) · 2 fail-closed abort (required substrate unusable — no verdict
# may be asserted).
.PHONY: research research-gate research-self publication publication-gate publication-self \
        publications research-publication-gate
research:
	@python3 -m intelligence.research build

research-gate:
	@python3 -m intelligence.research gate

# research-self: the subsystem's guards over its own surface — deterministic
# regeneration and the full thirteen-obligation validation report.
research-self:
	@python3 -m intelligence.research verify >/dev/null
	@python3 -m intelligence.research validate >/dev/null
	@echo "UCOS-URI-001: self-guards PASS (determinism + research validation)"

publication:
	@python3 -m intelligence.publication build

publication-gate:
	@python3 -m intelligence.publication gate

# publication-self: deterministic regeneration plus the fourteen-obligation validation
# report (which itself executes the format-openness probe).
publication-self:
	@python3 -m intelligence.publication verify >/dev/null
	@python3 -m intelligence.publication validate >/dev/null
	@echo "UCOS-UPI-001: self-guards PASS (determinism + publication validation)"

# publications: regenerate research intelligence, then every publication format.
publications: research publication

# research-publication-gate: both gates in dependency order (publication consumes the
# research corpus, so a closed research gate closes the publication gate too).
research-publication-gate: research-gate publication-gate



# rib: UCOS-RIB-001 — Repository Integration Blueprint (EPIC-001 / WP-001).
# Additive only — no existing target, recipe, or dependency above is altered.
#
# The executable expression of EPIC-001. It creates no capability catalogue, no dependency
# graph, no registry, no execution queue, no priority register and no certification
# authority: every one already exists and is already owned (intelligence/UCOS-RIE-* — the
# Repository Intelligence Engine; 00-BOOK/tools/ukb.py — registration; 00-BOOK/DATA — the
# typed graph and the twin certification; 00-MASTER/URRC-000001 — the reality matrices;
# 00-MASTER/UAKOS-CLOSURE-002 — concept closure and the planning layer; 00-MASTER/UEI-000001
# and UER-000001 — the evolution and resilience capability bindings). It DISCOVERS the unit
# universe from Repository Truth with zero enumeration, MEASURES every unit, BINDS each of
# the sixteen chartered matrices to the owner that already holds it — emitting the pointer
# and no rows — or DERIVES it where no owner holds it machine-readably, computes exactly one
# disposition per unit through an ordered, total, data-declared rule set, and emits the
# fourteen mandatory outputs into 00-MASTER/UCOS-RIB-001/.
#
# AUTHORITY = NONE (DERIVED TRUTH). Stdlib only; writes nothing outside its own operational
# memory directory (guarded, fail-closed). Adding a discovery source, measure, plane,
# disposition, rule, matrix, gap class, duplicate class, gate or output is an entry in
# 00-MASTER/UCOS-RIB-001/rib-blueprint.json and requires NO change to the engine.
#
# Exit 0 every blocking gate passed · 1 a blocking gate failed · 2 fail-closed abort
# (the declaration or a required substrate is unusable, so no verdict may be asserted).
.PHONY: rib rib-gate rib-self
rib:
	@python3 00-MASTER/UCOS-RIB-001/rib_engine.py

rib-gate:
	@python3 00-MASTER/UCOS-RIB-001/rib_engine.py --gate

# rib-self: the eight guards over the programme's own surface — declaration integrity
# (every reference resolves; every obligation names a computed metric; the rule set is
# ordered, reachable and total), zero-enumeration (the blueprint is DATA and the engine
# names none of its subject matter), forbidden-write scope, self-determinism, substrate
# usability, no-fabrication (every row traces to a source, a measure or a counted probe),
# reuse-before-create (no bound owner lies inside this programme's own home), and totality
# (every unit carries exactly one disposition from the closed set).
rib-self:
	@python3 00-MASTER/UCOS-RIB-001/rib_engine.py --check-declaration
	@python3 00-MASTER/UCOS-RIB-001/rib_engine.py --check-no-enumeration
	@python3 00-MASTER/UCOS-RIB-001/rib_engine.py --check-write-scope
	@python3 00-MASTER/UCOS-RIB-001/rib_engine.py --check-determinism
	@python3 00-MASTER/UCOS-RIB-001/rib_engine.py --check-substrate
	@python3 00-MASTER/UCOS-RIB-001/rib_engine.py --check-no-fabrication
	@python3 00-MASTER/UCOS-RIB-001/rib_engine.py --check-reuse-before-create
	@python3 00-MASTER/UCOS-RIB-001/rib_engine.py --check-totality



# uakos-archive: the completed, superseded UAKOS/USIS operational-memory phases.
# Additive only — no existing target, recipe, or dependency above is altered.
#
# Four operational-memory programme phases are terminal historical determinations: their
# missions completed and their responsibility is held by their successor programmes. They
# are retained as constitutional evidence, and this guard proves each archived phase
# directory and its completion determination is still present.
#
# THEIR ENGINES ARE PIPELINE STAGES, not frozen artifacts. This comment previously stated
# that no regeneration target names them and that their one-shot engines are
# wall-clock-stamped and would dirty the tree. UCOS-RFP-001 producer discovery measured
# both claims and both were false: the engines are DETERMINISTIC over two runs at one
# commit, and their committed registers had drifted from what they re-derive. Under
# CLS-OPERATIONAL-MEMORY the convergence obligation is REQUIRED — a determination that
# re-execution does not reproduce evidences nothing — so they are declared stages of the
# fixed-point pipeline and re-derived like every other producer. Being historical is not
# an exemption from being reproducible.
#
# Exit 0 all four archived phases present · non-zero one is missing.
.PHONY: uakos-archive
uakos-archive:
	@ok=1 ; \
	for d in \
		00-MASTER/UAKOS-PHASE-001A-R1 \
		00-MASTER/UAKOS-PHASE-001B \
		00-MASTER/UAKOS-PHASE-003R \
		00-MASTER/UCOS-USIS-WAVE0 ; do \
		if [ ! -d "$$d" ]; then echo "MISSING archived phase: $$d" ; ok=0 ; fi ; \
	done ; \
	[ "$$ok" -eq 1 ] && echo "UAKOS/USIS archived operational-memory phases present (4)"



# umk: UMK-000001 — Universal Meta-Kernel Foundation (PROGRAM-002, WAVE-2).
# Additive only — no existing target, recipe, or dependency above is altered.
#
# The Universal Meta-Kernel itself lives under engine/kernel/: the smallest possible
# open, self-describing meta-type system. Everything the platform can ever represent is a
# MetaObject classified by a registered MetaType; the reflective root MetaType is
# classified by itself. Concept-categories are registered DATA, never enum members, so a
# previously unknown category (a civilization, language family, value-exchange system,
# taxation/audit/temporal/governance/scientific model, provider category, capability
# domain or execution model) is admitted by registration only — the kernel is never
# redesigned (Engineering Rule 7).
#
# This target runs the executable expression of PROGRAM-002 in
# 00-MASTER/UMK-000001/umk_engine.py, which BINDS every universal abstraction declared in
# umk-kernel.json to its home in engine/kernel/, runs the kernel's own executed
# constitutional proof (engine/kernel/compliance.py), and emits the seven deliverables +
# validation/certification evidence into 00-MASTER/UMK-000001/. It legislates nothing and
# freezes no architecture.
#
# AUTHORITY = NONE (DERIVED TRUTH). Stdlib only; writes nothing outside its own
# operational-memory directory (guarded, fail-closed). The kernel is also runnable
# directly via the `ucos-kernel` console script (prove / certify / describe / evidence).
#
# Exit 0 constitutionally compliant · 1 a quality gate failed · 2 fail-closed abort
# (declaration or substrate unusable — no verdict may be asserted).
.PHONY: umk umk-gate umk-self umk-certify
umk:
	@python3 00-MASTER/UMK-000001/umk_engine.py

umk-gate:
	@python3 00-MASTER/UMK-000001/umk_engine.py --gate

# umk-certify: fail-closed UNCONDITIONAL certification — exits non-zero unless every one
# of the twenty Universal Certification Matrix dimensions reports exactly 100%. The two
# coverage dimensions are read from coverage.xml, so run `make test` (or `make verify`)
# first so the measured statement/branch coverage is present.
umk-certify: test
	@python3 00-MASTER/UMK-000001/umk_engine.py --certify

# umk-self: the programme's guards over its own surface — declaration integrity (every
# abstraction resolves to a real home, every seeded meta-type exists, every architectural-
# proof category is proven), forbidden-write scope (every output lands inside
# 00-MASTER/UMK-000001/), and self-determinism (deliverables are byte-identical across runs).
umk-self:
	@python3 00-MASTER/UMK-000001/umk_engine.py --check-declaration
	@python3 00-MASTER/UMK-000001/umk_engine.py --check-write-scope
	@python3 00-MASTER/UMK-000001/umk_engine.py --check-determinism



# uprf: UPF-000001 — Universal Provider Framework (PROGRAM-003, WAVE-2).
# Additive only — no existing target, recipe, or dependency above is altered.
#
# The framework itself lives under engine/provider/: the constitutional realization layer
# over the immutable PROGRAM-002 kernel. A provider category is a registered kernel
# meta-type (open set); a provider is a kernel MetaObject classified by its category.
# Concrete providers are future registrations, never framework modifications. It imports
# and modifies neither the kernel nor the distinct platform/universal_provider (EC-2).
#
# This target runs the executable expression of PROGRAM-003 in
# 00-MASTER/UPF-000001/upf_engine.py, which BINDS every provider responsibility declared in
# upf-provider.json to its home under engine/provider/ (or a reused kernel primitive), runs
# the framework's own executed constitutional proof (engine/provider/compliance.py), and
# emits the nine deliverables + validation/certification evidence into 00-MASTER/UPF-000001/.
#
# AUTHORITY = NONE (DERIVED TRUTH). Stdlib only; writes nothing outside its own
# operational-memory directory (guarded, fail-closed). The framework is also runnable
# directly via the `ucos-uprf` console script (prove / certify / describe / evidence).
#
# Exit 0 compliant/certified · 1 a gate/dimension below 100% · 2 fail-closed abort.
.PHONY: uprf uprf-gate uprf-self uprf-certify
uprf:
	@python3 00-MASTER/UPF-000001/upf_engine.py

uprf-gate:
	@python3 00-MASTER/UPF-000001/upf_engine.py --gate

# uprf-self: declaration integrity (every responsibility resolves, every category is
# proven), forbidden-write scope (outputs land inside 00-MASTER/UPF-000001/), self-determinism.
uprf-self:
	@python3 00-MASTER/UPF-000001/upf_engine.py --check-declaration
	@python3 00-MASTER/UPF-000001/upf_engine.py --check-write-scope
	@python3 00-MASTER/UPF-000001/upf_engine.py --check-determinism

# uprf-certify: fail-closed UNCONDITIONAL certification — non-zero unless every one of the
# twenty Universal Certification Matrix dimensions reports exactly 100%. Coverage dimensions
# are read from coverage.xml, so `make test` runs first.
uprf-certify: test
	@python3 00-MASTER/UPF-000001/upf_engine.py --certify


# ---------------------------------------------------------------------------
# UCOS-RFP-001 — REPOSITORY FIXED-POINT CLOSURE (G-15).
#
# The permanent answer to the class of defect that produced CK-REG-DRIFT. It adds no
# validator, engine, registry or capability: it BINDS the producers the repository
# already owns into one declared pipeline and asserts a single property over them —
# executing that pipeline over the committed HEAD must leave the repository
# byte-identical, for each declared convergence pass. Every producer, cycle class,
# artifact class and closure criterion is an entry in
# 00-MASTER/UCOS-RFP-001/rfp-declaration.json; this Makefile and the engine never need
# to change to admit a new one, and nothing is enumerated in either.
#
# The gate is what makes closure conditional on REALITY rather than on assertion:
# certification says the state is lawful, the fixed point says the state is real.
#
# AUTHORITY = NONE (DERIVED TRUTH). Stdlib only; writes nothing outside
# 00-MASTER/UCOS-RFP-001/ (guarded, fail-closed). The gate itself PERSISTS NOTHING —
# its verdict is the exit code, because an artifact recording "the repository is a
# fixed point" would falsify that sentence by being written (RFP-3).
#
# Exit 0 fixed point (gate OPEN) · 1 not a fixed point (gate CLOSED) · 2 fail-closed abort.
.PHONY: rfp rfp-gate rfp-detect rfp-self
rfp:
	@python3 00-MASTER/UCOS-RFP-001/rfp_engine.py

# rfp-gate: G-15. Fail-closed. Requires a clean committed tree to begin (a fixed point
# is a property of a COMMITTED state), then runs the full declared pipeline three times.
rfp-gate:
	@python3 00-MASTER/UCOS-RFP-001/rfp_engine.py --gate

# rfp-detect: the same measurement, reported without asserting a verdict — for use while
# repairing a producer. Never fails, so it can never be mistaken for the gate.
rfp-detect:
	@python3 00-MASTER/UCOS-RFP-001/rfp_engine.py --detect

# rfp-self: declaration integrity, zero-enumeration proof (the engine names no producer,
# zone or cycle class), forbidden-write scope, self-determinism, and self-compliance —
# the programme that abolishes commit self-reference and working-tree self-observation
# proving it commits neither in its own emitted bytes.
rfp-self:
	@python3 00-MASTER/UCOS-RFP-001/rfp_engine.py --check-declaration
	@python3 00-MASTER/UCOS-RFP-001/rfp_engine.py --check-no-enumeration
	@python3 00-MASTER/UCOS-RFP-001/rfp_engine.py --check-write-scope
	@python3 00-MASTER/UCOS-RFP-001/rfp_engine.py --check-determinism
	@python3 00-MASTER/UCOS-RFP-001/rfp_engine.py --check-self-compliance



# ---------------------------------------------------------------------------
# mcos: MCOS-000001 — Universal Meta-Civilization Platform (PROGRAM-004, WAVE-2).
# Additive only — no existing target, recipe, or dependency above is altered.
#
# The layer that GENERATES constitutional operating systems lives under engine/civilization/:
# the third realization layer over the immutable PROGRAM-002 kernel, sibling to the PROGRAM-003
# provider framework. Three components over ONE kernel — an open dimension space (the Universal
# Dimension Model), a planner that derives execution from declarations rather than a pipeline
# (Dynamic Capability Composition), and an ordered chain of registered strata through which a
# constitutional operating system comes into being (the Constitutional Generation Model).
#
# Seven of the ten mandated constructs already had a canonical owner and were NOT
# re-implemented: the Universal Meta Kernel (engine/kernel, UMK-000001), the Universal Registry
# Architecture (the kernel registry — a second registry is prohibited), Universal Capability
# Discovery (engine/discovery), the Open-World Expansion certifications, Unlimited
# Constitutional Evolution (CEP-009, UEI-000001), the Universal Engineering Platform
# (PLATFORM-005/010, named not authored), and the MCOS name itself (resolved onto MCS-000, with
# authority NONE). Reuse is MEASURED by mcos-self, not asserted.
#
# This target runs the executable expression of PROGRAM-004 in
# 00-MASTER/MCOS-000001/mcos_engine.py, which BINDS every responsibility declared in
# mcos-civilization.json to its home under engine/civilization/ (or a REUSED owner elsewhere),
# runs the layer's own executed constitutional proof (engine/civilization/compliance.py), and
# emits the nine deliverables + validation/certification evidence into 00-MASTER/MCOS-000001/.
#
# AUTHORITY = NONE (DERIVED TRUTH). Stdlib only; writes nothing outside its own
# operational-memory directory (guarded, fail-closed). Admitting a dimension, capability,
# composition strategy, generation stratum or constitutional operating system is a REGISTRATION
# and requires NO change to the layer, to the engine, or to the kernel. The platform is also
# runnable directly via the `ucos-mcos` console script (describe / prove / certify / evidence).
#
# Exit 0 compliant/certified · 1 a gate/dimension below 100% · 2 fail-closed abort.
.PHONY: mcos mcos-gate mcos-self mcos-certify
mcos:
	@python3 00-MASTER/MCOS-000001/mcos_engine.py

mcos-gate:
	@python3 00-MASTER/MCOS-000001/mcos_engine.py --gate

# mcos-self: declaration integrity (every substrate, mechanism, gate, proof category, generated
# operating system and stratum resolves), reuse-before-create (a responsibility claiming REUSED
# must be homed OUTSIDE this layer, and one claiming NEW must be homed inside — the guard that
# stops a re-implementation wearing a reuse label), forbidden-write scope, and self-determinism.
mcos-self:
	@python3 00-MASTER/MCOS-000001/mcos_engine.py --check-declaration
	@python3 00-MASTER/MCOS-000001/mcos_engine.py --check-reuse-before-create
	@python3 00-MASTER/MCOS-000001/mcos_engine.py --check-write-scope
	@python3 00-MASTER/MCOS-000001/mcos_engine.py --check-determinism

# mcos-certify: fail-closed UNCONDITIONAL certification — non-zero unless every one of the
# twenty Universal Certification Matrix dimensions reports exactly 100%. Coverage dimensions are
# read from coverage.xml, so `make test` runs first.
mcos-certify: test
	@python3 00-MASTER/MCOS-000001/mcos_engine.py --certify




# ---------------------------------------------------------------------------
# ucef: UCEF-000001 — Universal Constitutional Evolution Framework (CEP-009-AMD-001).
# Additive only — no existing target, recipe, or dependency above is altered.
#
# This block adds NO new validator, engine, authority or capability. It runs the executable
# expression of the constitutional-evolution contract declared in
# 00-MASTER/UCEF-000001/ucef-framework.json, whose NORMATIVE home is
# 00-CEP/CEP-009-...-AMENDMENT-EVOLUTION-CONSTITUTION.md ADDENDUM B. Every law, lifecycle
# stage, acceptance property, expansion axis, construct class and governance obligation in
# that DATA file BINDS to an authority that already exists and is already located — the
# meta-governance admission procedure and construct taxonomy (00-CMG/CMG-000001 Art XIII,
# XIV, XV, XL, XLI, LXXVI, LXXVII), governance change control (00-CEP/CEP-002 Art 20/21/28),
# validation (00-CEP/CEP-004 + verify.sh), certification (00-CEP/CEP-005), traceability
# (00-CEP/CEP-008), registration (REG-AUTO-001 + 00-BOOK/tools/register.sh), the
# implementation contract (00-MASTER/UCIC-001) and the evolution registry
# (00-CEP/CEP-009 Art XVI + 00-MASTER/EVOLUTION-001).
#
# Admitting a further construct class, expansion axis, lifecycle stage, acceptance property,
# governance obligation or validation dimension is an entry in that DATA file and requires NO
# change to the engine, to this Makefile, or to the workflow. A self-guard proves it: the
# engine names none of them.
#
# Exit semantics of the gate:
#   0  every law is anchored, every stage is bound to a located owner outside the programme,
#      every acceptance property is discharged by a located mechanism, the construct register
#      is declared OPEN, no expansion axis declares a finite bound, the stage graph is acyclic
#      and closed, and every mandatory dimension and exit criterion is satisfied (gate OPEN)
#   1  a binding, dimension or exit criterion is unsatisfied (gate CLOSED)
#   2  fail-closed abort — the declaration is unusable, so no verdict may be asserted
.PHONY: ucef ucef-gate ucef-self
ucef:
	@python3 00-MASTER/UCEF-000001/ucef_engine.py

ucef-gate:
	@python3 00-MASTER/UCEF-000001/ucef_engine.py --gate

# ucef-self: the six guards over the programme's own surface — declaration integrity (every
# law basis, stage owner, acceptance mechanism, axis basis, construct admission route and
# governance instrument resolves against Repository Truth), zero-enumeration (the framework is
# DATA: the engine special-cases no declared member), write-scope (no write ever lands outside
# 00-MASTER/UCEF-000001/, and never in a frozen or certified zone), determinism (assessment and
# rendering are byte-identical across runs, no wall-clock is emitted), reuse-before-create (no
# bound authority lies inside this programme's own home, so nothing owned elsewhere is
# re-authored here), and open-world (no finite ceiling is declared anywhere — the construct
# register is open and non-exhaustive and every expansion axis is unbounded).
ucef-self:
	@python3 00-MASTER/UCEF-000001/ucef_engine.py --check-declaration
	@python3 00-MASTER/UCEF-000001/ucef_engine.py --check-no-enumeration
	@python3 00-MASTER/UCEF-000001/ucef_engine.py --check-write-scope
	@python3 00-MASTER/UCEF-000001/ucef_engine.py --check-determinism
	@python3 00-MASTER/UCEF-000001/ucef_engine.py --check-reuse-before-create
	@python3 00-MASTER/UCEF-000001/ucef_engine.py --check-open-world



# ---------------------------------------------------------------------------
# uar: UCOS-UAR-001 — Universal Analysis Registry.
#
# WHY THIS BLOCK EXISTS. The engine was already complete, already deterministic and already
# self-guarded, but no declared entry point named it — so the Repository Integration Blueprint
# measured it as a DEAD ENGINE (`GAP-DEAD-ENGINE`, `VER-11`) and, because `RCH-ENTRYPOINT` is one
# of its seven pre-declared reachability dimensions, simultaneously as an ORPHAN unit (`VER-09`,
# `GATE-11`). One cause, two findings, both blocking `GATE-03`.
#
# UCOS-RIB-001/WP-003 §008 names the discharge exactly: "name the programme engine from a declared
# entry point, or disposition the engine", and assigns the act to the `Makefile` / CI entry points
# — this file. Disposition was rejected on measurement, not preference: all five of the engine's
# own checks exit 0 (26 declared analyses, every home resolving), so the engine is live code that
# was merely unreachable, and retiring working, self-guarded code to satisfy a reachability metric
# would destroy capability to make a number look better.
#
# Additive only — no existing target, recipe or dependency above is altered. This introduces NO
# authority, NO registry and NO new mechanism: it exposes an EXISTING engine through the EXISTING
# entry-point convention every other programme here already uses.
#
# AUTHORITY = NONE (DERIVED TRUTH). Stdlib only; writes nothing outside
# 00-MASTER/UCOS-UAR-001/. Adding an analysis is an entry in uar-analyses.json and requires no
# change to the engine or to this Makefile.
#
# Exit 0 gate OPEN · 1 gate CLOSED · 2 fail-closed abort.
.PHONY: uar uar-gate uar-self
uar:
	@python3 00-MASTER/UCOS-UAR-001/uar_engine.py

uar-gate:
	@python3 00-MASTER/UCOS-UAR-001/uar_engine.py --gate

# uar-self: declaration integrity (every declared analysis has a unique id and a resolving home),
# zero-enumeration proof (no declared analysis id appears as a literal in the engine source, so
# the registry cannot be faked by hardcoding), write scope, and self-determinism.
uar-self:
	@python3 00-MASTER/UCOS-UAR-001/uar_engine.py --check-declaration
	@python3 00-MASTER/UCOS-UAR-001/uar_engine.py --check-no-enumeration
	@python3 00-MASTER/UCOS-UAR-001/uar_engine.py --check-write-scope
	@python3 00-MASTER/UCOS-UAR-001/uar_engine.py --check-determinism


# ---------------------------------------------------------------------------
# uapf: UAPF-000001 — the Universal Autonomous Pipeline Framework.
#
# WHY THIS BLOCK EXISTS. The framework is the constitutional execution foundation for every
# autonomous activity (Evolution Pipeline, Build Pipeline, and every future pipeline category),
# and its two canonical pipelines are DECLARED as data in
# platform/universal_pipeline/catalog/uapf-pipelines.json rather than written as code. Neither
# the framework nor the catalogue may be reachable only from a test: the Repository Integration
# Blueprint measures a capability that no declared entry point names as a DEAD ENGINE
# (`GAP-DEAD-ENGINE`, `VER-11`) and, because `RCH-ENTRYPOINT` is one of its reachability
# dimensions, simultaneously as an ORPHAN unit (`VER-09`). This block plus the `ucos-uapf`
# console script in pyproject.toml are the discharge, using the same entry-point convention
# every other programme here already uses.
#
# Additive only — no existing target, recipe or dependency above is altered. This introduces NO
# authority, NO registry and NO new mechanism: it exposes an EXISTING framework through the
# EXISTING entry-point convention.
#
# AUTHORITY = NONE (DERIVED TRUTH). Stdlib only; READ-ONLY — it opens the declared catalogue and
# writes nothing anywhere, not the certified corpus (DP-03), not the registries, not a cache.
# Adding a pipeline, a stage, a gate, a policy or a whole new pipeline CATEGORY is an entry in
# the catalogue and requires no change to the framework or to this Makefile.
#
# Exit 0 gate OPEN · 1 gate CLOSED · 2 fail-closed abort.
.PHONY: uapf uapf-gate uapf-self
uapf:
	@python3 -m platform.universal_pipeline.cli

uapf-gate:
	@python3 -m platform.universal_pipeline.cli --gate

# uapf-self: the framework's guards over its own surface — that the derived registry is
# byte-identical across two independent discovery passes of the same declarations
# (--check-determinism), and that the open vocabularies it governs are enumerable
# (--taxonomy: pipeline types, event categories, stage handlers, object kinds, readiness
# predicates). Both are read-only.
uapf-self:
	@python3 -m platform.universal_pipeline.cli --check-determinism
	@python3 -m platform.universal_pipeline.cli --taxonomy >/dev/null
	@python3 -m platform.universal_pipeline.cli --gate


# ---------------------------------------------------------------------------------------
# uaep: UAEP-000001 — the platform capability binding register.
#
# The platform agreement names sixteen capabilities. Fifteen already had a canonical home
# before this programme existed and one had none, so this programme binds each name to the
# home that already realises it and then proves the binding still resolves. It creates no
# engine, no registry, no catalogue, no identity, no graph and no pipeline: every binding is
# a pointer, and `uaep-self` refuses any binding that points inside this programme's own home.
#
# The declaration 00-MASTER/UAEP-000001/uaep-platform.json is the single source: capabilities,
# homes, symbols, vocabularies, pipeline categories and validation dimensions are all DATA,
# so adding one is an edit to that file and never to the engine (proven by --check-no-enumeration).
#
# A declared validation dimension the engine does not measure FAILS CLOSED rather than being
# reported satisfied — absence of evidence is never evidence.
.PHONY: uaep uaep-gate uaep-self uaep-replay
uaep:
	@python3 00-MASTER/UAEP-000001/uaep_engine.py --render

uaep-gate:
	@python3 00-MASTER/UAEP-000001/uaep_engine.py --gate

# uaep-self: the six guards over the programme's own surface — declaration integrity (no
# duplicate id, no empty mandatory field), zero-enumeration (no capability id or name appears
# in the engine source, including its docstring), write-scope (every rendered target resolves
# inside 00-MASTER/UAEP-000001/), determinism (two renders are byte-identical; no wall-clock
# is emitted), reuse-before-create (no capability is bound to an artifact this programme owns),
# and open-world (every declared vocabulary names a registrar that exists in its declared home,
# so the type, handler, event and object-kind spaces stay open).
uaep-self:
	@python3 00-MASTER/UAEP-000001/uaep_engine.py --check-declaration
	@python3 00-MASTER/UAEP-000001/uaep_engine.py --check-no-enumeration
	@python3 00-MASTER/UAEP-000001/uaep_engine.py --check-write-scope
	@python3 00-MASTER/UAEP-000001/uaep_engine.py --check-determinism
	@python3 00-MASTER/UAEP-000001/uaep_engine.py --check-reuse-before-create
	@python3 00-MASTER/UAEP-000001/uaep_engine.py --check-open-world

# uaep-replay: prove the committed registers are the deterministic product of the committed
# declaration. Re-render, then require a clean diff over this programme's home.
uaep-replay:
	@python3 00-MASTER/UAEP-000001/uaep_engine.py --render --quiet
	@git diff --exit-code -- 00-MASTER/UAEP-000001 \
	  || { echo "UAEP-000001 REPLAY DRIFT — committed registers are not the product of the declaration" >&2; exit 1; }
	@echo "UAEP-000001 replay: no drift"


# ---------------------------------------------------------------------------------------
# uaie: UAIE-000001 — the architectural intelligence faculty binding and register-plane
# reasoning register.
#
# WHY THIS BLOCK EXISTS. The mission this programme records names ten architectural faculties
# — semantic graph, architectural reasoning, dependency, ownership, duplication, gap, evolution,
# reuse, constitutional and completion intelligence — and twelve subjects the repository must be
# able to reason about. EVERY ONE of them already had a canonical owner and a located register
# before this programme existed, so nothing here is built: each faculty is bound by pointer to
# the owner that realises it, to the analysis already registered in 00-MASTER/UCOS-UAR-001, and
# to the registers it reasons over, and the binding is then MEASURED so a rename, a move or a
# deletion closes the gate instead of silently invalidating the claim.
#
# WHAT IS ADDED. Exactly three analyses, and they are entries in the LOCATED analysis registry
# rather than a registry of this programme's own: cross-register consistency, faculty binding
# resolution, and closure over the faculty relation. The first is the one measurement no located
# owner performed — each owner validates its own register, and none reads one register's
# references against what the repository still holds, so a register that drifts while its own
# owner stays green is visible only across them.
#
# WHAT IS NOT ADDED. No engine, no registry, no catalogue, no identity, no graph, no lifecycle,
# no authority and no namespace. The programme is classified SUBSTANTIVE under
# 00-CMG/CMG-000001 Article LXXVI.2(b), which forbids admitting a substantive concept into the
# meta-constitutional layer, so it is deliberately ABSENT from 00-CMG/CMG-REGISTRY.json — and
# `uaie-self` MEASURES that absence rather than asserting it (--check-no-parallel-authority).
#
# The declaration 00-MASTER/UAIE-000001/uaie-architecture.json is the single source: faculties,
# owners, homes, symbols, analyses, registers, probes, ontology anchors and validation dimensions
# are all DATA, so adding one is an edit to that file and never to the engine (proven by
# --check-no-enumeration, which fails if any declared id, name or path leaks into the source).
#
# A declared validation dimension the engine does not measure FAILS CLOSED rather than being
# reported satisfied — absence of evidence is never evidence.
#
# AUTHORITY = NONE (DERIVED TRUTH). Stdlib only; READ-ONLY outside its own home.
# Exit 0 gate OPEN · 1 gate CLOSED · 2 fail-closed abort.
.PHONY: uaie uaie-gate uaie-self uaie-replay
uaie:
	@python3 00-MASTER/UAIE-000001/uaie_engine.py --render

uaie-gate:
	@python3 00-MASTER/UAIE-000001/uaie_engine.py --gate

# uaie-self: the seven guards over the programme's own surface — declaration integrity (no
# duplicate id, no empty mandatory field, no CREATE disposition, every structural register role
# present), zero-enumeration (no faculty, owner, home, register, path or anchor appears in the
# engine source, including its docstring), write-scope (every rendered target resolves inside
# 00-MASTER/UAIE-000001/), determinism (two renders are byte-identical; no wall-clock is
# emitted), reuse-before-create (no faculty and no canonical owner points inside this
# programme's own home), register-plane (every declared register resolves, parses, and is
# claimed by at least one faculty), and no-parallel-authority (the programme holds no place and
# claims no namespace token in the meta-constitutional plane, and declares AUTHORITY = NONE),
# and evolution-contract (every one of the ten Constitutional Evolution Contract obligations
# binds to a located owner, a named gate and evidence that resolves, and the change class,
# release state and baseline are members of the located registers that own those vocabularies
# — the VERDICT of each obligation stays with its own gate and is never restated here).
uaie-self:
	@python3 00-MASTER/UAIE-000001/uaie_engine.py --check-declaration
	@python3 00-MASTER/UAIE-000001/uaie_engine.py --check-no-enumeration
	@python3 00-MASTER/UAIE-000001/uaie_engine.py --check-write-scope
	@python3 00-MASTER/UAIE-000001/uaie_engine.py --check-determinism
	@python3 00-MASTER/UAIE-000001/uaie_engine.py --check-reuse-before-create
	@python3 00-MASTER/UAIE-000001/uaie_engine.py --check-register-plane
	@python3 00-MASTER/UAIE-000001/uaie_engine.py --check-no-parallel-authority
	@python3 00-MASTER/UAIE-000001/uaie_engine.py --check-evolution-contract

# uaie-replay: prove the committed registers are the deterministic product of the committed
# declaration — the programme's fixed point. Re-render, then require a clean diff over its home.
uaie-replay:
	@python3 00-MASTER/UAIE-000001/uaie_engine.py --render --quiet
	@git diff --exit-code -- 00-MASTER/UAIE-000001 \
	  || { echo "UAIE-000001 REPLAY DRIFT — committed registers are not the product of the declaration" >&2; exit 1; }
	@echo "UAIE-000001 replay: no drift"


# ---------------------------------------------------------------------------------------
# UCOS-AEE-001 — AUTONOMOUS EVOLUTION ENGINE.
#
# The closed loop. Every phase of the evolution loop already has a located, certified
# owner in this repository, and this programme creates none of them — no validator, no
# gate, no registry, no schema, no measurement, no certification. What no located
# programme owned is the LOOP: every entry point here is a one-shot process, so nothing
# re-executed the located owners, re-read their sealed determinations, compared
# consecutive readings and asserted a fixed point over what they report.
#
# The loop's phases are not restated anywhere in this programme. They are READ at run
# time from the declarations that already own them — the pipeline catalogue's evolution
# and implementation pipelines, and the evolution-intelligence loop and its standing
# continuous obligations. A phase appended to any of those sources is discovered on the
# next run; a phase nothing discharges is reported as uncovered rather than assumed.
#
# Convergence here is over the OBSERVATION VECTOR — the tuple of every located owner's
# reported verdict — and requires consecutive iterations to agree. Byte-level repository
# closure is a different and stronger condition owned by UCOS-RFP-001 and measured by
# `make rfp-gate`; this programme never invokes it, which is what keeps the driver out of
# the fixed-point engine's own pipeline (RFP CYC-RECURSE).
#
# Adding an actuator, an observation, a classification rule, a decision value, a
# precondition or a convergence criterion is an append-only edit to
# 00-MASTER/UCOS-AEE-001/aee-declaration.json and requires NO change to the engine or to
# this Makefile.
#
# AUTHORITY = NONE (DERIVED TRUTH). Stdlib only; writes nothing outside
# 00-MASTER/UCOS-AEE-001/ (guarded, fail-closed).
#
# Exit 0 converged · 1 a blocking convergence criterion is unsatisfied · 2 fail-closed
# abort (an admission condition failed, or the declaration is unusable).
.PHONY: aee aee-observe aee-gate aee-closure aee-self
aee:
	@python3 00-MASTER/UCOS-AEE-001/aee_engine.py --tier standard

# aee-observe: the fast read-only pass. No located owner is invoked, so nothing is
# regenerated and no residue is produced. It cannot assert convergence — stability across
# iterations is not measurable without actuation — and says so rather than implying it.
aee-observe:
	@python3 00-MASTER/UCOS-AEE-001/aee_engine.py --tier observe

# aee-gate: actuate the located owners, iterate until the observation vector is stable,
# fail closed. Refuses to begin while any declared owner or competing driver is already
# executing: a reading taken during a race describes neither the state before it nor the
# state after (measured, see AEE-F-004).
aee-gate:
	@python3 00-MASTER/UCOS-AEE-001/aee_engine.py --tier standard --gate

# aee-closure: the same loop including the heavy tier, which runs the aggregate
# constitutional certifier at its own full tier — verification, the determinism
# double-build and the registration-drift gate included.
aee-closure: bootstrap-quiet
	@python3 00-MASTER/UCOS-AEE-001/aee_engine.py --tier closure --gate

# aee-self: the six guards over the programme's own surface — declaration integrity,
# zero-enumeration (the engine names no actuator, observation, mandate, class, decision
# or owner path, including in its docstring), write scope (every emitted target resolves
# inside 00-MASTER/UCOS-AEE-001/), determinism (two renders are byte-identical; no
# wall-clock, commit identity or absolute path is emitted), reuse-before-create (no bound
# owner lies inside this programme's own home, so it is not a second home for a located
# capability), and mandate coverage (every loop phase read from the located sources is
# discharged by something).
aee-self:
	@python3 00-MASTER/UCOS-AEE-001/aee_engine.py --check-declaration
	@python3 00-MASTER/UCOS-AEE-001/aee_engine.py --check-no-enumeration
	@python3 00-MASTER/UCOS-AEE-001/aee_engine.py --check-write-scope
	@python3 00-MASTER/UCOS-AEE-001/aee_engine.py --check-determinism
	@python3 00-MASTER/UCOS-AEE-001/aee_engine.py --check-reuse-before-create
	@python3 00-MASTER/UCOS-AEE-001/aee_engine.py --check-mandate-coverage


# ---------------------------------------------------------------------------
# P0-LIFECYCLE-CLOSURE-001 — UNIVERSAL CONSTITUTIONAL LIFECYCLE REALIZATION.
#
# AUTHORITY = NONE (DERIVED TRUTH). The engine legislates nothing and certifies nothing.
# It measures whether each of UCL-000001's 45 stages is actually realized, treating the
# stage manifest's declared owner and evidence as claims to be tested rather than as
# findings. A stage is IMPLEMENTED only where five executed probes agree.
#
# These targets exist because RIB VER-09 (no orphan capability) and VER-11 (no dead
# engine) measure reachability by scanning the declared entry-point surface — the
# Makefile among it. A programme engine no entry point names is a dead engine by
# measurement, whatever its quality, so declaring the target IS the remediation.
#
# Write scope: 00-MASTER/P0-LIFECYCLE-CLOSURE-001/ only.
# Exit 0 measured · 1 --gate requested and a closure claim is NOT_PROVEN · 2 fail-closed
# abort (a phase could not be measured, so no verdict may be asserted).
.PHONY: lifecycle-closure lifecycle-closure-fast lifecycle-closure-gate
lifecycle-closure:
	@python3 00-MASTER/P0-LIFECYCLE-CLOSURE-001/lifecycle_closure_engine.py --rounds 10

# lifecycle-closure-fast: skips the coverage phase, which runs the test suite as a
# subprocess. Use when the realization/graph/replay measurement is what is wanted and the
# several-minute instrumented test run is not.
lifecycle-closure-fast:
	@python3 00-MASTER/P0-LIFECYCLE-CLOSURE-001/lifecycle_closure_engine.py --rounds 10 --no-coverage

# lifecycle-closure-gate: the fail-closed form. Exits 1 while any of the twelve closure
# claims measures NOT_PROVEN, so CI cannot pass on a lifecycle that is only declared.
lifecycle-closure-gate:
	@python3 00-MASTER/P0-LIFECYCLE-CLOSURE-001/lifecycle_closure_engine.py --rounds 10 --gate


# ---------------------------------------------------------------------------
# P0-FINAL-CLOSURE-002 — FIXED-POINT AND PRISTINE-CLONE MEASUREMENT.
#
# AUTHORITY = NONE (DERIVED TRUTH). Runs the located regeneration chain repeatedly and
# measures whether the repository regenerates to itself (Phase 8), then clones the
# repository and measures whether independent copies regenerate to the same identities
# (Phase 9). It creates no authority and certifies nothing it did not measure.
#
# Phase 8 fails closed on a dirty tree or a concurrent writer: drift measured while
# another process is writing is not attributable to the regeneration pipeline, which is
# the defect that invalidated the previous attempt at this phase.
#
# Write scope: 00-MASTER/P0-FINAL-CLOSURE-002/ plus whatever the located chain regenerates
# under its own owners, which is the chain's own declared scope and not this engine's.
# Exit 0 measured · 1 --gate requested and a requirement unmet · 2 fail-closed abort.
.PHONY: final-closure final-closure-gate
final-closure:
	@python3 00-MASTER/P0-FINAL-CLOSURE-002/final_closure_engine.py --rounds 5 --clones 3 --cycles 5

final-closure-gate:
	@python3 00-MASTER/P0-FINAL-CLOSURE-002/final_closure_engine.py --rounds 5 --clones 3 --cycles 5 --gate


# ---------------------------------------------------------------------------
# CONSTITUTIONAL GOVERNANCE CONVERGENCE — four programmes, one ordered chain.
#
# WHY THIS BLOCK EXISTS. The aggregate certifier reported two standing ceilings, and neither was
# a missing capability: both were missing MACHINERY.
#
#   * The authority ceiling. Every authority in this repository existed only as prose — a table
#     in a located register, or ARTICLE I of a located instrument. The tier lattice alone was
#     machine-readable. So no gate could resolve which authority was competent for an act, no
#     gate could detect an authority referenced but defined nowhere, and no gate could detect
#     that a recorded claim of authority ABSENCE had been contradicted by later located evidence.
#     Separately, CEP-006 Article XVI mandates a Ratification Registry and XVI.4 deems any
#     ratification absent from it NON-EXISTENT — and no registry existed, so five located and
#     committed ratification acts could not lawfully be relied upon by anything.
#
#   * The traceability ceiling. Two different obligations had been conflated under one word. The
#     CONSTITUTIONAL obligation (CEP-001 XVIII.1 upward rooting and downward evidence, XVIII.2
#     and CEP-008 XI.2 closure with zero orphans) is the one CEP-006 V.1 and CEP-007 V.1 both
#     name, verbatim, as the ratification and freeze precondition. The thirteen-lane ENGINEERING
#     spine is a richer model owned by platform/measurement and 00-BOOK/tools. Only the first is
#     a constitutional precondition, and nothing measured it on its own terms.
#
# AUTHORITY = NONE (DERIVED TRUTH) for all four. Stdlib only. Each writes nothing outside its own
# operational-memory directory, proven by a fail-closed write-scope guard. None creates an
# authority, confers a ratification, populates a traceability lane, weakens a predicate or
# performs a freeze. Every identifier each one acts on is read from a located instrument or from
# its own declaration, and a zero-enumeration guard fails closed if any leaks into engine source.
#
# NOTHING HERE LIFTS THE FINALITY CEILING. CEP-006 I.4 caps every in-corpus determination at
# provisional acceptance pending an out-of-corpus finality authority. That ceiling is preserved,
# and UCCEP-F-004 is deliberately RETAINED as blocking so the aggregate verdict stays capped.
# What changed is that the ceiling is now the ONLY one standing, and CEP-007 III.2 admits an
# artifact to the freeze lifecycle at provisional acceptance — which the located foundation
# freeze authorization records in terms as "not a freeze blocker".
#
# Additive only — no existing target, recipe or dependency above is altered.
#
# Exit 0 gate OPEN · 1 gate CLOSED · 2 fail-closed abort (no verdict may be asserted).
# ---------------------------------------------------------------------------

# ucaf: UCOS-UCAF-001 — the Universal Constitutional Authority Framework. Registry, delegation,
# resolution, validation, succession, scope, verification, evidence, audit, revocation and
# certification over the authorities the repository has ALREADY located. It defines none of them:
# every authority is discovered at run time from the located register or instrument that defines
# it, which is what --check-knowledge-once proves. --check-no-promotion proves it never reports a
# vacant tier as occupied and never converts a measured reconciliation into a ratification.
.PHONY: ucaf ucaf-gate ucaf-self ucaf-replay
ucaf:
	@python3 00-MASTER/UCOS-UCAF-001/ucaf_engine.py

ucaf-gate:
	@python3 00-MASTER/UCOS-UCAF-001/ucaf_engine.py --gate

ucaf-self:
	@python3 00-MASTER/UCOS-UCAF-001/ucaf_engine.py --check-declaration
	@python3 00-MASTER/UCOS-UCAF-001/ucaf_engine.py --check-no-enumeration
	@python3 00-MASTER/UCOS-UCAF-001/ucaf_engine.py --check-write-scope
	@python3 00-MASTER/UCOS-UCAF-001/ucaf_engine.py --check-determinism
	@python3 00-MASTER/UCOS-UCAF-001/ucaf_engine.py --check-knowledge-once
	@python3 00-MASTER/UCOS-UCAF-001/ucaf_engine.py --check-no-promotion

ucaf-replay:
	@python3 00-MASTER/UCOS-UCAF-001/ucaf_engine.py --render --quiet
	@git diff --exit-code -- 00-MASTER/UCOS-UCAF-001 \
	  || { echo "UCOS-UCAF-001 REPLAY DRIFT — committed registers are not the product of the declaration" >&2; exit 1; }
	@echo "UCOS-UCAF-001 replay: no drift"


# baseline: BASELINE-001 — Universal Constitutional Baseline Inheritance. The canonical baseline
# register, its origin record, its certificate and its continuation classification are APPEND-ONLY
# records held by the already-located baseline authority, and until now they were prose: no gate
# could resolve a baseline, detect a missing or duplicated row, detect a break in succession,
# detect a second claimed current baseline, detect a baseline cited but never recorded, or detect
# that a recorded baseline had come to rest on evidence that no longer existed. This measurement
# DERIVES the chain from those records and creates no second baseline, register, namespace,
# identifier family or lifecycle — CMG-INV-02 requires the concern-to-owner map be injective and
# BASELINE-001 already owns certified baseline, so the measurement is held BY that owner inside
# that owner's home.
#
# It confers nothing. Advancement is measured against the located criteria and reported, never
# granted. Where the register that records currency and another register that claims it disagree,
# both are measured, both are cited, and a referred outcome is reported for the claim owner to
# dispose of under CEP-002 Article 23 — every claimant is named in the declaration's forbidden
# write prefixes, and --check-declaration fails closed if a claimant is ever left unprotected.
#
# --check-record-immutability is the mandatory mechanical proof that write set ∩ canonical record
# set = ∅, and additionally that every record present in the home is a member of the protected
# set, so the protected set cannot be quietly narrowed to make room for a generated page.
# --check-no-elevation proves no baseline is reported at a standing its located record does not
# carry and that no currency divergence is decided rather than referred.
#
# AUTHORITY = NONE (DERIVED TRUTH). Stdlib only; no version-control observation; writes nothing
# outside 00-MASTER/BASELINE-001/ (guarded, fail-closed).
#
# Exit 0 gate OPEN · 1 gate CLOSED · 2 fail-closed abort (no verdict may be asserted).
.PHONY: baseline baseline-gate baseline-self baseline-replay
baseline:
	@python3 00-MASTER/BASELINE-001/baseline_engine.py

baseline-gate:
	@python3 00-MASTER/BASELINE-001/baseline_engine.py --gate

baseline-self:
	@python3 00-MASTER/BASELINE-001/baseline_engine.py --check-declaration
	@python3 00-MASTER/BASELINE-001/baseline_engine.py --check-no-enumeration
	@python3 00-MASTER/BASELINE-001/baseline_engine.py --check-write-scope
	@python3 00-MASTER/BASELINE-001/baseline_engine.py --check-determinism
	@python3 00-MASTER/BASELINE-001/baseline_engine.py --check-knowledge-once
	@python3 00-MASTER/BASELINE-001/baseline_engine.py --check-record-immutability
	@python3 00-MASTER/BASELINE-001/baseline_engine.py --check-no-elevation

baseline-replay:
	@python3 00-MASTER/BASELINE-001/baseline_engine.py --render --quiet
	@git diff --exit-code -- 00-MASTER/BASELINE-001 \
	  || { echo "BASELINE-001 REPLAY DRIFT — committed registers are not the product of the declaration" >&2; exit 1; }
	@echo "BASELINE-001 replay: no drift"


# uis: UIS-001 — Universal Identity System Conformance. It makes the identity architecture the
# repository ALREADY legislated executable, and adds no identity capability of its own. AIF governs
# the law of identity, ENG-001 is the engineering architecture of record, and UMB-003/004/005/008/
# 009/010 realize them; this measurement reads all of them plus the append-only identity ledger and
# the derived artifact registry, and reports what they say. It mints no identity, declares no
# namespace, defines no grammar, opens no registry and legislates no lifecycle:
# --check-no-identity-minting fails closed if any emitted byte carries an identifier the ledger does
# not already record, which is what forbids this programme from becoming a fifth identifier scheme
# or a sixth registry. --check-bounds-tight forbids inflating a disclosed divergence to hide a
# regression inside the slack.
#
# AUTHORITY = NONE (DERIVED TRUTH). Stdlib only; no wall-clock, no version-control observation;
# writes nothing outside 00-MASTER/UIS-001/ (guarded, fail-closed).
#
# Exit 0 gate OPEN · 1 gate CLOSED · 2 fail-closed abort (no verdict may be asserted).
.PHONY: uis uis-gate uis-self uis-replay
uis:
	@python3 00-MASTER/UIS-001/uis_engine.py

uis-gate:
	@python3 00-MASTER/UIS-001/uis_engine.py --gate

uis-self:
	@python3 00-MASTER/UIS-001/uis_engine.py --check-declaration
	@python3 00-MASTER/UIS-001/uis_engine.py --check-no-enumeration
	@python3 00-MASTER/UIS-001/uis_engine.py --check-write-scope
	@python3 00-MASTER/UIS-001/uis_engine.py --check-determinism
	@python3 00-MASTER/UIS-001/uis_engine.py --check-knowledge-once
	@python3 00-MASTER/UIS-001/uis_engine.py --check-record-immutability
	@python3 00-MASTER/UIS-001/uis_engine.py --check-no-identity-minting
	@python3 00-MASTER/UIS-001/uis_engine.py --check-bounds-tight
	@python3 00-MASTER/UIS-001/uis_engine.py --check-no-authority

uis-replay:
	@python3 00-MASTER/UIS-001/uis_engine.py --render --quiet
	@git diff --exit-code -- 00-MASTER/UIS-001 \
	  || { echo "UIS-001 REPLAY DRIFT — committed registers are not the product of the declaration" >&2; exit 1; }
	@echo "UIS-001 replay: no drift"


# urat: UCOS-URAT-001 — the Ratification Registry CEP-006 Article XVI mandates. It confers
# nothing: every state it records is READ out of the located act that determined it and verified
# by an anchor that must be present in that act's own text, so no edit to the declaration alone
# can improve a state. The two transitions into the terminal finality state are declared to
# require the out-of-corpus authority, and --check-no-conferral fails closed if any record ever
# reaches one. --check-coverage proves the registry is complete over its own discovery surface:
# every located file whose name declares it a ratification instrument is either registered or
# excluded with a class and a reason.
.PHONY: urat urat-gate urat-self urat-replay
urat:
	@python3 00-MASTER/UCOS-URAT-001/urat_engine.py

urat-gate:
	@python3 00-MASTER/UCOS-URAT-001/urat_engine.py --gate

urat-self:
	@python3 00-MASTER/UCOS-URAT-001/urat_engine.py --check-declaration
	@python3 00-MASTER/UCOS-URAT-001/urat_engine.py --check-no-enumeration
	@python3 00-MASTER/UCOS-URAT-001/urat_engine.py --check-write-scope
	@python3 00-MASTER/UCOS-URAT-001/urat_engine.py --check-determinism
	@python3 00-MASTER/UCOS-URAT-001/urat_engine.py --check-coverage
	@python3 00-MASTER/UCOS-URAT-001/urat_engine.py --check-no-conferral

urat-replay:
	@python3 00-MASTER/UCOS-URAT-001/urat_engine.py --render --quiet
	@git diff --exit-code -- 00-MASTER/UCOS-URAT-001 \
	  || { echo "UCOS-URAT-001 REPLAY DRIFT — committed registers are not the product of the declaration" >&2; exit 1; }
	@echo "UCOS-URAT-001 replay: no drift"


# utce: UCOS-UTCE-001 — the Universal Traceability Closure Engine. READ-ONLY over the certified
# corpus, proven by --check-read-only, which requires every source it opens to sit under a path
# this programme is forbidden to write. It measures the CONSTITUTIONAL obligation as BLOCKING and
# reports the thirteen-lane engineering spine UNCHANGED against its own owner — no predicate is
# weakened and no lane is populated. Both vocabularies are read from their located owners by
# static analysis rather than by import, so a lane added to the schema or a label added to the
# vocabulary is discovered here automatically. --check-no-fabrication requires every entry it
# calls derivable to cite the located edge that would support it.
.PHONY: utce utce-gate utce-self utce-replay
utce:
	@python3 00-MASTER/UCOS-UTCE-001/utce_engine.py

utce-gate:
	@python3 00-MASTER/UCOS-UTCE-001/utce_engine.py --gate

utce-self:
	@python3 00-MASTER/UCOS-UTCE-001/utce_engine.py --check-declaration
	@python3 00-MASTER/UCOS-UTCE-001/utce_engine.py --check-no-enumeration
	@python3 00-MASTER/UCOS-UTCE-001/utce_engine.py --check-write-scope
	@python3 00-MASTER/UCOS-UTCE-001/utce_engine.py --check-determinism
	@python3 00-MASTER/UCOS-UTCE-001/utce_engine.py --check-read-only
	@python3 00-MASTER/UCOS-UTCE-001/utce_engine.py --check-no-fabrication

utce-replay:
	@python3 00-MASTER/UCOS-UTCE-001/utce_engine.py --render --quiet
	@git diff --exit-code -- 00-MASTER/UCOS-UTCE-001 \
	  || { echo "UCOS-UTCE-001 REPLAY DRIFT — committed registers are not the product of the declaration" >&2; exit 1; }
	@echo "UCOS-UTCE-001 replay: no drift"


# ufep: UCOS-UFEP-001 — the Universal Freeze Eligibility Programme. CEP-007 IV.2 requires
# eligibility to be DECIDABLE and V.2 requires every precondition to be machine-verifiable;
# nothing measured them together, and one of the five could not be measured at all until the
# ratification registry existed. This programme measures all five per subject, computes the
# content-addressed baseline a freeze WOULD seal (CEP-007 VIII.2), and runs the Article X no-drift
# guard over the located frozen baseline manifest — recomputing every recorded digest.
#
# IT PERFORMS NO FREEZE. CEP-007 VII.1 reserves the freeze decision to Freeze Authority and I.5
# forbids its self-conferral by Execution Authority. Every state past eligibility is declared
# unreachable by this programme and --check-no-freeze fails closed if any subject is reported in
# one. The located freeze authorization is recorded as evidence that the channel is occupied; it
# is not acted upon.
#
# Its determination reads the aggregate certifier's own sealed model, so it is deliberately NOT
# bound as a check inside that certifier — only its self-guards are (G-21). Criterion UFEP-CC-11
# measures that the model it read was a FULL-tier one, so a tier-limited run cannot silently
# produce a completion verdict. Run `make completion` for the correct ordering.
.PHONY: ufep ufep-gate ufep-self ufep-replay
ufep:
	@python3 00-MASTER/UCOS-UFEP-001/ufep_engine.py

ufep-gate:
	@python3 00-MASTER/UCOS-UFEP-001/ufep_engine.py --gate

ufep-self:
	@python3 00-MASTER/UCOS-UFEP-001/ufep_engine.py --check-declaration
	@python3 00-MASTER/UCOS-UFEP-001/ufep_engine.py --check-no-enumeration
	@python3 00-MASTER/UCOS-UFEP-001/ufep_engine.py --check-write-scope
	@python3 00-MASTER/UCOS-UFEP-001/ufep_engine.py --check-determinism
	@python3 00-MASTER/UCOS-UFEP-001/ufep_engine.py --check-no-freeze
	@python3 00-MASTER/UCOS-UFEP-001/ufep_engine.py --check-no-drift

ufep-replay:
	@python3 00-MASTER/UCOS-UFEP-001/ufep_engine.py --render --quiet
	@git diff --exit-code -- 00-MASTER/UCOS-UFEP-001 \
	  || { echo "UCOS-UFEP-001 REPLAY DRIFT — committed registers are not the product of the declaration" >&2; exit 1; }
	@echo "UCOS-UFEP-001 replay: no drift"


# completion: the ordered convergence. The order is not arbitrary and is not a preference — it is
# the constitutional dependency order.
#
#   1. authority      — nothing may be attributed to an authority that does not resolve.
#   2. ratification   — a record's authority must resolve in the authority registry (fail-closed).
#   3. traceability   — the precondition CEP-006 V.1 and CEP-007 V.1 name in those exact words.
#   4. certifier      — at FULL tier, because a tier-limited run excludes blocking checks and
#                       says so in its own ceiling; completion may not rest on such a run.
#   5. eligibility    — reads 1-4 and decides CEP-007 Article IV per subject.
#
# Each step is fail-closed, so the chain stops at the first unsatisfied condition rather than
# reporting a completion the repository has not reached.
.PHONY: completion
completion:
	@$(MAKE) --no-print-directory ucaf-gate
	@$(MAKE) --no-print-directory urat-gate
	@$(MAKE) --no-print-directory utce-gate
	@python3 00-MASTER/UCCEP-000000/uccep_engine.py --tier full --gate
	@$(MAKE) --no-print-directory ufep-gate



# ucl: UCL-000001 — the Universal Constitutional Lifecycle. It makes the constitutional stage graph
# the repository ALREADY legislated discoverable, orderable and EXECUTABLE, and creates no lifecycle
# of its own. UCIC-001 owns the single deterministic lifecycle every capability follows, CEP-009
# ADDENDUM B owns construct admission, ENG-001 D30 and UMB-003 §3 own the artifact lifecycle,
# UEI-000001 §17 owns the evolution lifecycle and 02-EXECUTION-LIFECYCLE.md owns the execution
# lifecycle; this programme crosswalks all of them and MERGES none, because a merge would amend
# every owner at once.
#
# The lifecycle is GRAPH-DRIVEN, not enumeration-driven. Constitutional metadata is reached through
# Metadata Providers, normalized by Metadata Adapters into Canonical Knowledge Objects, and the
# Discovery Engine operates on those objects alone — so it never sees a file, a format or a field
# name. Admitting a stage, a capability, an object kind, a relation type, a graph type, a provider,
# an adapter, a serialization, an obligation, a property or an expansion axis is an append to DATA:
# --check-no-enumeration fails closed if any discovered value could steer behaviour from inside the
# engine, scanning EXECUTABLE string constants only (comments and docstrings are excluded, because
# the objective is to prevent hardcoded constitutional behaviour, not constitutional terminology).
#
# --check-implementation-independence fails closed if any object or relation is traced to an
# evidence-class provider: implementation source may corroborate an obligation, never originate one.
# --check-cko-identity proves every governed entity holds exactly ONE Canonical Knowledge Object and
# that no derived register is ever read back as a source. --check-open-world fails closed on any
# architectural bound token, on an expansion axis with no resolving registrar, on a closed registry,
# and if fewer than two serialization readers exist. Obligations are NOT universally applicable:
# applicability is determined first, and a NOT_APPLICABLE obligation is reported rather than counted
# as unbound.
#
# Execution resolves and records; it never re-invokes the stages' own engines, which would create the
# self-observation topology RFP-3 forbids and stop the repository converging.
#
# AUTHORITY = NONE (DERIVED TRUTH). Stdlib only; no wall-clock, no version-control observation;
# writes nothing outside 00-MASTER/UCL-000001/ (guarded, fail-closed).
#
# Additive only — no existing target, recipe, or dependency above is altered.
#
# Exit 0 gate OPEN · 1 gate CLOSED · 2 fail-closed abort (no verdict may be asserted).
.PHONY: ucl ucl-gate ucl-self ucl-replay ucl-execute
ucl:
	@python3 00-MASTER/UCL-000001/ucl_engine.py

ucl-gate:
	@python3 00-MASTER/UCL-000001/ucl_engine.py --gate

ucl-self:
	@python3 00-MASTER/UCL-000001/ucl_engine.py --check-declaration
	@python3 00-MASTER/UCL-000001/ucl_engine.py --check-no-enumeration
	@python3 00-MASTER/UCL-000001/ucl_engine.py --check-write-scope
	@python3 00-MASTER/UCL-000001/ucl_engine.py --check-determinism
	@python3 00-MASTER/UCL-000001/ucl_engine.py --check-implementation-independence
	@python3 00-MASTER/UCL-000001/ucl_engine.py --check-open-world
	@python3 00-MASTER/UCL-000001/ucl_engine.py --check-no-parallel-authority
	@python3 00-MASTER/UCL-000001/ucl_engine.py --check-lifecycle-executable
	@python3 00-MASTER/UCL-000001/ucl_engine.py --check-cko-identity
	@python3 00-MASTER/UCL-000001/ucl_engine.py --check-semantic-identity
	@python3 00-MASTER/UCL-000001/ucl_engine.py --check-knowledge-once
	@python3 00-MASTER/UCL-000001/ucl_engine.py --check-record-immutability
	@python3 00-MASTER/UCL-000001/ucl_engine.py --check-bounds-tight

ucl-replay:
	@python3 00-MASTER/UCL-000001/ucl_engine.py --render --quiet
	@git diff --exit-code -- 00-MASTER/UCL-000001 \
	  || { echo "UCL-000001 REPLAY DRIFT — committed registers are not the product of the declaration" >&2; exit 1; }
	@echo "UCL-000001 replay: no drift"

# The substrate entry point Ω-E05 (ACEE) binds to. Deterministic and side-effect free: the run
# identity is a pure function of the goal text and the discovered graph, and nothing is written.
ucl-execute:
	@python3 00-MASTER/UCL-000001/ucl_engine.py --execute "$(GOAL)"

# acee: ACEE-000001 — Autonomous Constitutional Engineering. It binds an engineering GOAL to
# the constitutional lifecycle the repository already legislated, and creates nothing. The
# lifecycle is CONSUMED from 00-MASTER/UCL-000001/ucl-stage-manifest.json, never re-derived:
# a second derivation would be a second lifecycle, which CMG-000001 Art LXXVI.6 forbids.
# The repository-directed loop stays with 00-MASTER/UCOS-AEE-001 and the fixed point with
# 00-MASTER/UCOS-RFP-001; this engine invokes NO capability and re-runs NO owner, so it
# never observes a run of itself and opens no second execution surface.
#
# Goals and constitutional completion invariants are DISCOVERED from located manifest
# patterns in this lane, so admitting a further goal or invariant is an append to data and
# requires no engine change, no declaration change and no architectural redesign. Every
# invariant is measured against a located owner, a cited anchor that must actually be
# present in that owner, and a counter in ANOTHER owner's committed artifact — so an
# invariant can never be reported satisfied by this programme's own output.
#
# Disposition is DERIVED from measurement and resolves only to values the repository already
# legislates; CREATE is reachable only where Repository Truth locates no owner at all.
# This engine holds no privileged path: it appears in its own goal plane as a subject.
#
# AUTHORITY = NONE (DERIVED TRUTH). Stdlib only; no wall-clock, no version-control
# observation; writes nothing outside 00-MASTER/ACEE-000001/ (guarded, fail-closed).
#
# Additive only — no existing target, recipe, or dependency above is altered.
#
# Exit 0 gate OPEN · 1 gate CLOSED · 2 fail-closed abort (no verdict may be asserted).
.PHONY: acee acee-gate acee-self acee-replay acee-engineer
acee:
	@python3 00-MASTER/ACEE-000001/acee_engine.py

acee-gate:
	@python3 00-MASTER/ACEE-000001/acee_engine.py --gate

acee-self:
	@python3 00-MASTER/ACEE-000001/acee_engine.py --check-declaration
	@python3 00-MASTER/ACEE-000001/acee_engine.py --check-no-enumeration
	@python3 00-MASTER/ACEE-000001/acee_engine.py --check-no-privileged-logic
	@python3 00-MASTER/ACEE-000001/acee_engine.py --check-reuse-before-create
	@python3 00-MASTER/ACEE-000001/acee_engine.py --check-write-scope
	@python3 00-MASTER/ACEE-000001/acee_engine.py --check-determinism
	@python3 00-MASTER/ACEE-000001/acee_engine.py --check-implementation-independence
	@python3 00-MASTER/ACEE-000001/acee_engine.py --check-open-world
	@python3 00-MASTER/ACEE-000001/acee_engine.py --check-no-parallel-authority
	@python3 00-MASTER/ACEE-000001/acee_engine.py --check-goal-plane-executable
	@python3 00-MASTER/ACEE-000001/acee_engine.py --check-invariant-coverage
	@python3 00-MASTER/ACEE-000001/acee_engine.py --check-cko-identity
	@python3 00-MASTER/ACEE-000001/acee_engine.py --check-semantic-identity
	@python3 00-MASTER/ACEE-000001/acee_engine.py --check-knowledge-once
	@python3 00-MASTER/ACEE-000001/acee_engine.py --check-record-immutability
	@python3 00-MASTER/ACEE-000001/acee_engine.py --check-reduction-measured
	@python3 00-MASTER/ACEE-000001/acee_engine.py --check-bounds-tight

acee-replay:
	@python3 00-MASTER/ACEE-000001/acee_engine.py --render --quiet
	@git diff --exit-code -- 00-MASTER/ACEE-000001 \
	  || { echo "ACEE-000001 REPLAY DRIFT — committed registers are not the product of the declaration" >&2; exit 1; }
	@echo "ACEE-000001 replay: no drift"

# Goal-directed autonomous engineering for a goal nobody declared. Deterministic and
# side-effect free: the plan identity is a pure function of the goal text and the consumed
# stage graph, and nothing is written.
acee-engineer:
	@python3 00-MASTER/ACEE-000001/acee_engine.py --engineer "$(GOAL)" --subject "$(SUBJECT)"


# closure009: UAKOS-CLOSURE-009 — Universal Constitutional Assimilation Programme.
# It projects every constitutionally accepted concept already in Repository Truth into a
# governed Repository Requirement and MEASURES assimilation coverage, lifecycle maturity,
# readiness, traceability and gap. CREATE = 0 at the concept layer: requirement identity is
# a derived, injective function of the existing concept identity (RR-<CONCEPT-ID>).
#
# Why these targets exist. UCOS-RIB-001 measured this programme as BOTH a dead engine
# (VER-11 / GAP-DEAD-ENGINE) and an orphan capability (VER-09): its engine was named by no
# Makefile target, no workflow and no test, so REG-AUTO-001 P7 — enforceability by tooling
# gates rather than author discipline — was undischarged. The consequence was not cosmetic:
# because nothing re-ran it, its committed registers were left rendered against a stale
# HEAD and carried 89 inherited concept gaps that Repository Truth had already closed. An
# engine no target names is an engine nobody re-runs, and a register nobody re-runs is a
# register that silently stops being true.
#
# closure009 depends on closure-phase3 because the engine's required inputs are the
# PHASE-002/003 models; running it against an unregenerated predecessor would measure a
# superseded substrate (the engine itself fails closed with exit 2 if they are absent).
#
# AUTHORITY = NONE (DERIVED TRUTH). Stdlib only. Writes only inside
# 00-MASTER/UAKOS-CLOSURE-009/. No timestamp is emitted anywhere.
#
# Additive only — no existing target, recipe, or dependency above is altered.
#
# Exit 0 gate OPEN · 1 gate CLOSED · 2 fail-closed abort (required input absent).
.PHONY: closure009 closure009-gate closure009-baseline-gate closure009-replay
closure009: closure-phase3
	@python3 00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py

# Fail-closed standing gate: non-zero while constitutional assimilation is below 100%.
closure009-gate: closure-phase3
	@python3 00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py --gate

# Fail-closed: non-zero while any Phase-8 baseline precondition is unproven.
closure009-baseline-gate: closure-phase3
	@python3 00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py --baseline-gate

# The drift gate this programme could not previously have: --render replays the HEAD
# recorded in requirements.json instead of re-reading it, so the rendered surface is a pure
# function of the declared inputs plus that record and can be diffed byte-for-byte. Without
# the replayed head every register would drift by exactly one field on every commit, and the
# check would be permanently red for a reason that has nothing to do with truth.
# THE REPLAY GENERATES WHAT IT READS, BECAUSE OTHERWISE IT ANSWERS A DIFFERENT QUESTION
# THAN CI ASKS. `.github/workflows/closure009-gate.yml` runs generate-prerequisites.sh
# immediately before invoking this target, and the requirement engine counts the artifacts
# that script writes as evidence — so a bare `make closure009-replay` renders against
# whatever generated state the working tree happens to hold. Measured: RR-UCOS-RAT-002 at
# 25 evidence files locally against 26 in CI, from a STALE prerequisite set left by an
# earlier run. That reads as a drift in the registers and is a drift in the environment.
# The workflow comment one step above its own invocation states the rule this obeys —
# "a prerequisite generated after the gate that consumes it is not a prerequisite" — and
# the target now obeys it too, so local and CI agree by construction rather than by the
# operator remembering the ordering.
closure009-replay:
	@env PYTHON=python3 bash scripts/generate-prerequisites.sh >/dev/null
	@python3 00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py --render --quiet
	@git diff --exit-code -- 00-MASTER/UAKOS-CLOSURE-009 \
	  || { echo "UAKOS-CLOSURE-009 REPLAY DRIFT — committed registers are not the product of the declared inputs" >&2; exit 1; }
	@echo "UAKOS-CLOSURE-009 replay: no drift"


# --- Ω-A05: Universal Foundation capabilities -----------------------------------------
# The reusable Foundation is invoked as a capability, never re-derived per programme.
# Every target below EXECUTES FROM REPOSITORY TRUTH: the population comes from the declared
# specialisation (platform/universal_foundation/catalog/*.json), so none of them scans the
# repository. Swap the specialisation document and the same targets serve another project.
.PHONY: truth ownership-determination foundation foundation-gate

# truth: classify any locator population against declared Repository Truth zones.
truth: bootstrap-quiet
	@$(PY) -m platform.universal_truth.cli policy

# ownership-determination: the Ownership Declaration Contract and its evidence providers.
ownership-determination: bootstrap-quiet
	@$(PY) -m platform.universal_ownership.cli contract
	@$(PY) -m platform.universal_ownership.cli providers

# foundation: the composed determination — Truth classified, ownership determined from
# evidence only, and every measurement produced by a registered policy.
foundation: bootstrap-quiet
	@$(PY) -m platform.universal_foundation.cli determine

# foundation-gate: fail-closed — non-zero while any blocking measurement policy is
# unsatisfied. The blockers are named policies, so the gate says WHICH determination is
# incomplete rather than reporting one opaque number.
foundation-gate: bootstrap-quiet
	@$(PY) -m platform.universal_foundation.cli determine --gate >/dev/null \
	  || { echo "FOUNDATION DETERMINATION NOT CLOSED — run 'make foundation' for the named blockers" >&2; exit 1; }
	@echo "universal foundation: every blocking measurement policy is satisfied"



# --- UAUE-000001: Autonomous Universal Evolution ---------------------------------------
# The gate the register's own final position declares. Until it existed, one verification
# dimension of UAUE-000001 was bound to a target nothing ran, which is why the register
# reported itself PARTIALLY_IMPLEMENTED against repository truth: a gate that exists only
# as a string in a declaration discharges nothing.
#
# Every obligation is fail-closed and each is the negation of a way this capability could
# look present while being absent: the declaration rehydrates; every declared position of
# the loop resolves to an owner that exists, binds its symbols and names a wired gate;
# every canonical stage of the perpetual cycle is claimed by exactly one position; every
# dependency resolves and runs forward; conducting the same candidates twice produces
# byte-identical runs; the declared UNKNOWN subject — an object in no registry, of no
# declared class, owned by nobody — traverses every position to a settled, certified run
# without a new registry, authority, engine or schema; every declared mandatory invariant
# is measured against its expectation rather than presumed satisfied; every declared
# register renders bytes that reproduce on another process and another machine; the
# repository's own verification entry point invokes this gate fail-closed; and every
# declared exit criterion of every implementation phase is measured rather than asserted.
#
# The count is deliberately not written here. It grows as more of the declaration becomes
# measurable, and `make uaue` prints the whole set with its detail — a number in a comment
# is a claim that goes stale silently, which is the defect class this register exists to
# close.
#
# The gate mutates nothing. Execution in this register is AUTHORISATION ONLY: the
# constitutional mutation gateway remains the sole path to repository truth, and the
# controller records that an execution was authorised to travel it, never that a mutation
# happened.
.PHONY: uaue uaue-gate uaue-render uaue-replay

# uaue: the human-readable measurement — every obligation, every run, every refusal named.
uaue: bootstrap-quiet
	@$(PY) -m engine.uaue.gate

# uaue-gate: fail-closed — non-zero exit while any obligation is unsatisfied.
uaue-gate: bootstrap-quiet
	@$(PY) -m engine.uaue.gate --gate --quiet \
	  || { echo "UAUE GATE CLOSED — run 'make uaue' for the named obligations" >&2; exit 1; }
	@echo "uaue-gate: every obligation satisfied (unknown subject traversed, replay stable)"

# uaue-render: regenerate the declared surface — the history projection and the eighteen
# registers. DERIVED TRUTH: the history is the canonical document of the Article 14
# append-only ledger and the registers are projections of one measurement; none is ever
# authored by hand, and a hand edit is drift rather than a fact.
uaue-render: bootstrap-quiet
	@$(PY) -m engine.uaue.gate --render --quiet

# uaue-replay: fail-closed — the committed surface must be exactly what the declaration
# produces. Both halves are compared as bytes: a gate that proved the history replayed
# while eighteen registers drifted would be measuring the smaller half of its own output.
uaue-replay: bootstrap-quiet
	@$(PY) -m engine.uaue.gate --replay --quiet
	@echo "uaue-replay: the committed surface is the product of the declaration"


# ===========================================================================
# UOBC-000001 — Universal Object Birth Contract
#
# AUTHORITY = NONE (DERIVED TRUTH). This programme mints no repository serial,
# opens no registry, declares no lifecycle and consumes no counter. Identity is
# DERIVED by delegating to engine/uckp/identity.py, which the repository's own
# authority alignment declares `role: SUPREME — this IS UCKP-ART-05`. Under that
# file's second_authority_test — "a mint is recognised by the counter it advances",
# marker `category_seq` — a derived-identity ledger cannot be a second mint.
#
# Stdlib only; no wall clock, no network, no version-control observation; writes
# nothing outside 00-MASTER/UOBC-000001/ (the gate writes nothing at all).
# Additive only — no existing target, recipe or dependency above is altered.
# Exit semantics: 0 OPEN, 1 CLOSED (a law was refused), 2 FAULT (no verdict).
# ===========================================================================
.PHONY: birth birth-gate birth-json

# birth: the human-readable measurement — every law, every refusal named.
birth: bootstrap-quiet
	@$(PY) -m engine.object_birth.gate

# birth-gate: fail-closed. Wired into ./verify.sh as Stage 6e, so deleting the
# stage closes the gate rather than silently unbinding the eight laws.
birth-gate: bootstrap-quiet
	@$(PY) -m engine.object_birth.gate --gate --quiet
	@echo "birth-gate: no object exists without identity, and no identity was replaced"

# birth-json: the machine-readable report, for a consumer that needs the law table.
birth-json: bootstrap-quiet
	@$(PY) -m engine.object_birth.gate --json



# ===========================================================================
# UISD-000001 — Universal Infinite Scope and Direction
#
# AUTHORITY = NONE (DERIVED TRUTH). This programme is NOT superior to CMG-000001
# (law owner), UCIC-001 (lifecycle owner) or CEP-009 (evolution authority). It
# declares no lifecycle stage, opens no registry, consumes no counter and issues
# no identifier, so it cannot become a rival authority under CAA-INV-04 or
# CAA-INV-07. Its subject is a PROPERTY of instruments, never an instrument.
#
# The property was already certified in prose — 16 unbounded axes in
# 03-CONSTITUTIONAL-UNBOUNDEDNESS-CERTIFICATION.md, 23 finite-assumption axes in
# 04-HIDDEN-FINITE-ASSUMPTION-CERTIFICATION.md — but the latter records in §4 that
# no exhaustive proof of absence was performed and confines residual risk to the
# realization layers. These targets compute the property over that space.
#
# Ten laws, all held as DATA in 00-MASTER/UISD-000001/uisd-declaration.json; the
# engine holds no law text and no enumeration member.
#
# OBSERVE MODE — READ ONLY. Stdlib only; no wall clock, no network, no subprocess;
# writes NOTHING anywhere, including gitignored paths. There is deliberately no
# -render and no -replay target: a gate that writes nothing cannot drift, and a
# replay target over an empty write set would be a declared-and-unread flag (GP-4).
# Additive only — no existing target, recipe or dependency above is altered.
# Exit semantics: 0 OPEN, 1 CLOSED (a law was refused), 2 FAULT (no verdict).
# ===========================================================================
.PHONY: infinite-scope infinite-scope-gate infinite-scope-json

# infinite-scope: the human-readable measurement — every law, every refusal named.
infinite-scope: bootstrap-quiet
	@$(PY) -m engine.infinite_scope.gate

# infinite-scope-gate: fail-closed. Wired into ./verify.sh as Stage 6f, so deleting
# the stage closes the gate rather than silently unbinding the ten laws.
infinite-scope-gate: bootstrap-quiet
	@$(PY) -m engine.infinite_scope.gate --quiet \
	  || { echo "INFINITE SCOPE GATE CLOSED — run 'make infinite-scope' for the named refusals" >&2; exit 1; }
	@echo "infinite-scope-gate: scope, direction, relationship and evolution capacity unbounded; no closure undisclosed"

# infinite-scope-json: the machine-readable report, for a consumer that needs the law table.
infinite-scope-json: bootstrap-quiet
	@$(PY) -m engine.infinite_scope.gate --json


# ===========================================================================
# UVI-000001 — Universal Verification Intelligence.
#
# The layer that answers "which verification does this change require, and in what
# order may it be executed". It owns no gate and certifies nothing; what it owns is
# selection, scheduling and evidence reuse. These targets expose its own law gate,
# which measures that the intelligence did not quietly reduce what verification means.
# Additive only — no existing target, recipe or dependency above is altered.
# Exit semantics: 0 COHERENT, 1 INCOHERENT (a law was refused), 2 FAULT (no verdict).
# ===========================================================================
.PHONY: uvi uvi-gate uvi-json verify-fast verify-change verify-integration verify-explain verify-cost-model

# uvi: the human-readable measurement — every law, every refusal named.
uvi: bootstrap-quiet
	@$(PY) -m engine.verification_intelligence.gate

# uvi-gate: fail-closed. Wired into ./verify.sh as Stage 6g, so deleting the stage
# closes the gate rather than silently unbinding the ten laws.
uvi-gate: bootstrap-quiet
	@$(PY) -m engine.verification_intelligence.gate --gate --quiet \
	  || { echo "UVI GATE CLOSED — run 'make uvi' for the named refusals" >&2; exit 1; }
	@echo "uvi-gate: selection is derived, every baseline gate still certifies, and no mode claims more than it measures"

# uvi-json: the machine-readable report, for a consumer that needs the law table.
uvi-json: bootstrap-quiet
	@$(PY) -m engine.verification_intelligence.gate --json


# ===========================================================================
# UCON-000001 — the Universal Construct Foundation.
#
# The layer that answers "what happens to a construct nobody anticipated". It owns no
# ontology, mints no identity scheme and certifies nothing; what it owns is a total,
# traceable disposition for every presented construct, and a governed home for the
# unknown, the contradictory and the undecidable.
#
# The distinction these targets exist to keep measurable: a REFUSAL must never be
# indistinguishable from a DROP. Before this capability, a construct whose classifying
# kind was unregistered raised MetaTypeUnknownError and left no record, so "we governed a
# refusal" and "we never saw it" were the same observable state. The registry here has no
# refusal path at all — disposition decides what a construct may DO, never whether it
# exists in the record — and the arithmetic is measured: the population cannot exceed the
# presentations.
#
# `ucon-audit` is the extensibility inventory: every closure mechanism in the repository
# joined to its declared risk tier, owner, extensibility limitation and migration path. It
# MEASURES and migrates nothing. The ratchet enforces disclosure inside engine/construct/
# and a non-rising population everywhere else, because a gate demanding zero closures on
# the day it was written would have been closed on that day and deleted on the next.
#
# Additive only — no existing target, recipe or dependency above is altered.
# Exit semantics: 0 OPEN, 1 CLOSED (a law was measured and refused), 2 FAULT (no verdict).
# ===========================================================================
.PHONY: ucon ucon-gate ucon-json ucon-audit ucon-inventory ucon-discover

# ucon: the human-readable measurement — all sixteen laws, every refusal named.
ucon: bootstrap-quiet
	@$(PY) -m engine.construct.gate

# ucon-gate: fail-closed. Wired into ./verify.sh as Stage 6i, so deleting the stage closes
# the gate rather than silently unbinding the sixteen laws.
ucon-gate: bootstrap-quiet
	@$(PY) -m engine.construct.gate --gate --quiet \
	  || { echo "UCON GATE CLOSED — run 'make ucon' for the named refusals" >&2; exit 1; }
	@echo "ucon-gate: every construct disposed, nothing silently ignored, no framework closed against a future it has not met"

# ucon-json: the machine-readable report, for a consumer that needs the law table.
ucon-json: bootstrap-quiet
	@$(PY) -m engine.construct.gate --json --quiet

# ucon-audit: the extensibility audit, rendered for a reader — every closure form with its
# limitation and migration path, the risk-tier distribution, and the heaviest modules.
ucon-audit: bootstrap-quiet
	@$(PY) -m engine.construct.cli audit

# ucon-inventory: the same inventory as JSON, written where the caller asks. Used to
# materialise the audit deliverable outside the untracked evidence home.
ucon-inventory: bootstrap-quiet
	@$(PY) -m engine.construct.cli audit --json --out 00-MASTER/UCON-000001/closure-inventory.json

# ucon-discover: run recursive discovery over a seeded registry and report the fixed point.
ucon-discover: bootstrap-quiet
	@$(PY) -m engine.construct.cli discover


# ===========================================================================
# UEC-000001 — UNIVERSAL ENFORCEMENT CLOSURE. Closure over the ENFORCEMENT surface.
#
# THE DEFECT, MEASURED. In an isolated worktree at HEAD, seven workflow files were deleted —
# including ec1-ci.yml, the sole CI invoker of `./verify.sh --full` — together with six
# fail-closed Makefile gate targets. `uvi-gate` exited 0. `uaue-gate` exited 0. A control test
# run and the post-deletion run were byte-identical: 5 failed, 191 passed, 1 skipped, 3 errors
# both times. Thirteen enforcement artifacts vanished and the repository said nothing.
#
# THE ROOT CAUSE, and why it is not carelessness. The repository has exactly ONE closure
# mechanism over its objects: REG-AUTO-001 registration. Its boundary, in 00-BOOK/tools/config.py,
# is INCLUDE_EXTENSIONS = (.md, .txt, .docx, .json) minus EXCLUDE_DIR_PREFIXES, which contains
# `.github/`, `00-MASTER/` and `00-BOOK/tools/`. Measured over the 1597 entries of
# 00-BOOK/DATA/artifacts.json: 0 are .py, 0 are .yml, 0 are under .github/, 0 are under
# 00-MASTER/. Every gate engine, every workflow, every declaration, every test and verify.sh
# itself is OUTSIDE the only closure mechanism the repository possesses — and was outside it
# before the first gate was written. `00-BOOK/tools/` is excluded on the stated ground that "the
# registry must not list itself", which is precisely why discovery D-09 records the trust anchor
# as unregistered: a designed exclusion whose consequence was never governed.
#
# UEC does NOT extend REG-AUTO-001. That would break its stated invariant and is a registry
# modification H-06 §5.4 authorizes under no approval. UEC is the COMPLEMENTARY plane, and
# UEC-L-10 measures the disjointness of the two rather than asserting it.
#
# THE RATCHET IS TWO-SIDED. Each ratcheted law refuses when measured > ceiling, so a NEW
# violation fails immediately; UEC-L-11 refuses when measured < ceiling, so a REPAIRED violation
# must tighten the ceiling. measured == ceiling exactly. There is no slack for a future
# violation to hide in — the half `00-MASTER/BASELINE-001/baseline_engine.py:726` lacks, where
# vacuity is computed, rendered, and does not close the gate.
#
# Additive only — no existing target, recipe or dependency above is altered.
# Exit semantics: 0 OPEN, 1 CLOSED (a blocking law refused), 2 FAULT (no verdict reachable).
# ===========================================================================
.PHONY: uec uec-gate uec-json uec-inventory uec-self

# uec: the human-readable measurement — all twelve laws, the ratchet table, every refusal named.
uec: bootstrap-quiet
	@$(PY) -m engine.enforcement_closure.gate

# uec-gate: fail-closed. Wired into ./verify.sh, so removing the stage closes the gate rather
# than silently unbinding the twelve laws — and UEC-L-09 refuses if UEC's own Makefile target,
# workflow, declaration or stage is the thing that went missing.
uec-gate: bootstrap-quiet
	@$(PY) -m engine.enforcement_closure.gate --gate --quiet \
	  || { echo "UEC GATE CLOSED — run 'make uec' for the named refusals" >&2; exit 1; }
	@echo "uec-gate: every protection governed, invoked from two planes, covered, and inside its own closure"

# uec-json: the machine-readable report, for a consumer that needs the law and ratchet tables.
uec-json: bootstrap-quiet
	@$(PY) -m engine.enforcement_closure.gate --json --quiet

# uec-inventory: the DISCOVERED enforcement surface, printed for adoption into the governed
# declaration by hand. Deliberately not written by any target: if the observation could rewrite
# the expectation, deleting a workflow and re-running the generator would produce a green gate,
# which is the bypass this whole programme closes. The `git diff` is the governed record.
uec-inventory: bootstrap-quiet
	@$(PY) -m engine.enforcement_closure.gate --inventory

# uec-self: UEC's guard over its own surface — UEC-L-09 alone. A closure mechanism outside its
# own closure is discovery D-09, so this is the leg that must never be allowed to pass vacuously.
uec-self: bootstrap-quiet
	@$(PY) -m engine.enforcement_closure.gate --gate --quiet --law UEC-L-09 \
	  || { echo "UEC SELF-COVERAGE CLOSED — UEC is not inside its own closure" >&2; exit 1; }
	@echo "uec-self: the registry is registered, the detector is detected"

# ===========================================================================
# URKE-000001 — Universal Recursive Knowledge Foundation.
#
# THIS PROGRAMME WAS BUILT AND NEVER WIRED, WHICH IS THE FAILURE MODE IT IS ITSELF ABOUT.
# The declaration, the sixteen-module engine, thirty-two laws, a 249-subject governed ledger
# and a passing suite all existed, and NOTHING INVOKED ANY OF IT: no Makefile target, no
# workflow, no ./verify.sh stage, and no row in UEC-000001's governed enforcement inventory.
# It was untracked, so UEC's discovery — which quantifies over `git ls-files` — could not see
# it either. A detector nothing runs is indistinguishable, from every gate in this repository,
# from a detector that does not exist.
#
# The targets below are one of the two invocation planes UEC-L-06 requires; the other is
# `.github/workflows/urke-gate.yml`, and ./verify.sh carries the stage. Deleting any one of
# them now fails UEC-L-02 (a governed artifact went missing) rather than silently reducing
# assurance.
#
# Exit semantics: 0 OPEN, 1 CLOSED (a blocking law refused), 2 FAULT (no verdict reachable).
# ===========================================================================
.PHONY: urke urke-gate urke-json urke-metrics

# urke: the human-readable measurement — all thirty-two laws, every refusal named.
urke: bootstrap-quiet
	@$(PY) -m engine.recursive_knowledge.gate

# urke-gate: fail-closed. Wired into ./verify.sh, so removing the stage closes the gate rather
# than silently unbinding the thirty-two laws.
urke-gate: bootstrap-quiet
	@$(PY) -m engine.recursive_knowledge.gate --gate --quiet \
	  || { echo "URKE GATE CLOSED — run 'make urke' for the named refusals" >&2; exit 1; }
	@echo "urke-gate: every unknown governed, discovery converges, no mechanism closed against a future domain"

# urke-json: the machine-readable report, for a consumer that needs the law table.
urke-json: bootstrap-quiet
	@$(PY) -m engine.recursive_knowledge.gate --json --quiet

# urke-metrics: the complexity metrics alone, for a reader tracking the governed population.
urke-metrics: bootstrap-quiet
	@$(PY) -m engine.recursive_knowledge.gate --metrics --quiet

# ===========================================================================
# SINGLE-INVOCATION-PLANE REMOVAL (UEC-L-06).
#
# UEC-000001 measures how many enforcement artifacts are reachable from exactly ONE invocation
# plane, because one plane is one deletion away from silence: remove the single caller and the
# gate stops running while every report stays green. Two of the fourteen it counted were
# reachable only from ./verify.sh — `00-MASTER/UCOS-UGA-001/uga_engine.py`, which asserts the
# ten universal object invariants over the whole version-controlled boundary, and
# `engine/root_ontology/gate.py`, which measures the constitutional primitive alignment. Both
# are blocking stages of the canonical gate, and neither could be run by name.
#
# These targets are the second plane. They add no authority, no new gate and no second criteria
# set: each invokes the identical command ./verify.sh already invokes, so the two planes cannot
# disagree about what the gate is. After adopting them the measured population falls to twelve
# and the declared ceiling is tightened to match — UEC-L-11 refuses a ceiling left above its
# measurement, so a repair cannot leave slack for a future violation to occupy.
# ===========================================================================
.PHONY: uga uga-gate ucpa ucpa-gate uccfa uccfa-gate

# uga: the human-readable measurement — every universal object invariant, every violation named.
uga: bootstrap-quiet
	@$(PY) 00-MASTER/UCOS-UGA-001/uga_engine.py gate

# uga-gate: fail-closed. The same command ./verify.sh runs as its universal object governance
# stage, so this plane and that one measure one thing rather than two.
uga-gate: bootstrap-quiet
	@$(PY) 00-MASTER/UCOS-UGA-001/uga_engine.py gate >/dev/null \
	  || { echo "UGA GATE CLOSED — run 'make uga' for the named violations" >&2; exit 1; }
	@echo "uga-gate: no anonymous, unowned, unregistered or unaudited object"

# ucpa: the human-readable measurement — the eight constitutional primitive alignment laws.
ucpa: bootstrap-quiet
	@$(PY) -m engine.root_ontology.gate

# ucpa-gate: fail-closed. The same command ./verify.sh runs as its constitutional primitive
# alignment stage.
ucpa-gate: bootstrap-quiet
	@$(PY) -m engine.root_ontology.gate --quiet \
	  || { echo "UCPA GATE CLOSED — run 'make ucpa' for the named refusals" >&2; exit 1; }
	@echo "ucpa-gate: the root ontology is measured, reduced and singly authored"

# uccfa: the human-readable measurement — the six coordinate framework alignment laws. The
# layer beside UCPA: four root primitives there, five coordinates here, and UCCFA-L-06 proves
# the two together are exactly the nine dimensions LAW Ω∞-000 requires.
uccfa: bootstrap-quiet
	@$(PY) -m engine.coordinate_framework.gate

# uccfa-gate: fail-closed. The same command ./verify.sh runs as its coordinate framework
# alignment stage, so this plane and that one measure one thing rather than two.
uccfa-gate: bootstrap-quiet
	@$(PY) -m engine.coordinate_framework.gate >/dev/null \
	  || { echo "UCCFA GATE CLOSED — run 'make uccfa' for the named refusals" >&2; exit 1; }
	@echo "uccfa-gate: the five coordinates are measured against the register that owns them"

# ===========================================================================
# EX-018 — MUTATION GOVERNANCE BOUNDARY DECIDABILITY
#
# The mutation classes decide WHO MAY MUTATE each artifact. Until this target existed
# nothing in any plane ran the classifier: `mutation_classification` was imported by
# exactly one file outside its own module — its own test — and neither it nor its
# register was in UEC-000001's governed inventory. Both could have been deleted with
# every gate in the repository still green, and twice they were effectively broken
# while every gate stayed green: R-09 declared with no predicate (classify() returned
# ERROR for every subject in the corpus), then implemented but shadowed by R-08 (
# GOVERNED_ANALYSIS claimed 0 of 6751 tracked paths).
# ===========================================================================
.PHONY: mutation mutation-gate mutation-json

# mutation: the human-readable measurement — the class census and all three laws.
mutation: bootstrap-quiet
	@$(PY) -m platform.repository_intelligence.mutation_gate

# mutation-gate: fail-closed. The same command ./verify.sh runs as its mutation
# governance boundary stage, so this plane and that one measure one thing rather
# than two. Deleting either leaves the other still refusing.
mutation-gate: bootstrap-quiet
	@$(PY) -m platform.repository_intelligence.mutation_gate --gate --quiet \
	  || { echo "MUTATION GATE CLOSED — run 'make mutation' for the named refusals" >&2; exit 1; }
	@echo "mutation-gate: every classification rule implemented, reachable and claiming subjects"

# mutation-json: the machine-readable report, for a consumer that needs the census.
mutation-json: bootstrap-quiet
	@$(PY) -m platform.repository_intelligence.mutation_gate --json --quiet


# ===========================================================================
# CAEM-001 — Mandate disposition closure.
#
# THE MEASUREMENT THAT PROVED THE DISPOSITION INSTRUMENT WAS LYING, AND THEN RAN
# NOTHING. caem_engine.py is what found the thirty concepts the register reported as
# IMPLEMENTED while the conformance suites proved them absent — substring collisions
# made `vr` inside `srv` and `web` inside `webhook` read as owners. It discharges all
# 1,449 mandates across six source documents to one of seven dispositions, and it sat
# invoked by no plane: a protection outside UEC-000001's governed inventory is one
# nothing knows it depends on (UEC-L-03), and a protection nothing invokes is one that
# cannot have refused anything (UEC-L-04).
#
# TWO PLANES, ONE COMMAND. This target and the ./verify.sh stage run identical argv, so
# they measure one thing rather than two; deleting either leaves the other still
# refusing, which is what UEC-L-06 requires. The slow half — `make caem-measure`, ~5k
# repository greps that WRITE 07-MANDATE-DISPOSITION.json — is an explicit regeneration
# and never a gate, because a gate that writes the artifact it measures cannot drift
# from it.
# ===========================================================================
.PHONY: caem-gate caem-measure

# caem-gate: fail-closed over the committed register. The same command ./verify.sh runs
# as its mandate disposition closure stage.
caem-gate: bootstrap-quiet
	@$(PY) 00-MASTER/CAEM-001/caem_engine.py --gate --quiet \
	  || { echo "CAEM GATE CLOSED — every mandate must carry a disposition; run 'make caem-measure'" >&2; exit 1; }
	@echo "caem-gate: every mandate disposed and no disposition invented"

# caem-measure: regenerate 07-MANDATE-DISPOSITION.json from the corpus. Slow (~5k greps)
# and writes; run it when a mandate or an owner changes, then commit the register.
caem-measure: bootstrap-quiet
	@$(PY) 00-MASTER/CAEM-001/caem_engine.py --measure
	@$(PY) 00-MASTER/CAEM-001/caem_engine.py --render


# ===========================================================================
# UCI-000001 — Universal Certification Integrity.
#
# WHAT THIS PROGRAMME MEASURES, AND WHY IT DID NOT EXIST BEFORE.
#
# Every coverage gate in this repository governed a NUMERATOR. The denominator was
# declared twice (`addopts` and `[tool.coverage.run] source`), reconciled by
# UCOS-COV-SCOPE-001 against each other, and compared to the executable surface by
# nothing at all. Measured at b51f6f84: the denominator held 905 of 1,524 tracked
# non-test Python files, so a reported 97.9% was a true statement about 52% of the
# executable surface, and executable-surface coverage was 44.9%.
#
# Outside the denominator: all 39 00-MASTER/*/*_engine.py gate engines (20,359
# statements, every one an enforcement artifact UEC-000001 governs by name),
# 00-BOOK/tools including ukb.py (the registration enforcement the whole corpus
# plane depends on), intelligence/ (in pytest testpaths, in no --cov flag), and
# engine/recursive_knowledge (an implicit namespace package the scope control could
# not see because it enumerated by __init__.py).
#
# These targets are one of the two invocation planes UEC-L-06 requires; the other
# is .github/workflows/uci-gate.yml. Deleting either now fails UEC-L-02 (a governed
# artifact went missing) rather than silently unbinding the six laws.
#
# Exit semantics: 0 OPEN, 1 CLOSED (a blocking law refused), 2 FAULT (no verdict).
# ===========================================================================
.PHONY: uci uci-gate uci-json uci-inventory

# uci: the human-readable measurement — the denominator against the surface, the
# scope drift, all six laws and the ratchet table.
uci: bootstrap-quiet
	@$(PY) -m engine.certification_integrity.gate

# uci-gate: fail-closed. Every ratchet is two-sided, so this refuses both a new
# violation AND debt repaid without tightening the ceiling — the second being how a
# ratchet decays into decoration.
uci-gate: bootstrap-quiet
	@$(PY) -m engine.certification_integrity.gate --gate --quiet \
	  || { echo "UCI GATE CLOSED — run 'make uci' for the named refusals" >&2; exit 1; }
	@echo "uci-gate: the denominator is governed, the surface is claimed, every ceiling binds"

# uci-json: the machine-readable report, for a consumer that needs the law table.
uci-json: bootstrap-quiet
	@$(PY) -m engine.certification_integrity.gate --json --quiet

# uci-inventory: writes coverage_gap_inventory.json, the one artifact this programme
# emits. No law in the package reads it back, so regenerating it cannot turn a
# refusal into a pass — the same asymmetry `make uec-inventory` relies on.
uci-inventory: bootstrap-quiet
	@$(PY) -m engine.certification_integrity.gate --write-inventory coverage_gap_inventory.json



# ===========================================================================
# UCOS-OMEGA-001 — Universal Discovery. Governance derived from executable reality.
#
# WHAT THIS PROGRAMME REPLACED. Every governance control in this repository used to
# quantify over a list somebody wrote. The lists were correct when written and
# silently wrong afterwards, and the omissions were found by READING them rather
# than by any control firing: SOURCE_TREES = ("engine", "platform") while five other
# roots existed; engine/recursive_knowledge invisible to an __init__.py predicate;
# 3,995 passing tests in four layers that no testpaths entry collected; scripts/ in
# no list at all. One root cause — a list has no term for what it omits, so it cannot
# report its own incompleteness.
#
# The five phases, each measured on every run of `make omega`:
#   Ω-1  scope, test roots and the coverage denominator DERIVED from git ls-files
#   Ω-2  authority derived by a chain whose last rule is unconditional (NONE is unreachable)
#   Ω-3  reachability over the execution graph, proved location-independent by experiment
#   Ω-4  ratchets that are DIRECTIONS, not the 65/27/39/25/14/10 snapshots they replaced
#   Ω-5  exactly one disposition per tracked artifact — no orphan, unknown or unowned state
#
# These targets are one of the two invocation planes UEC-L-06 requires; the other is
# .github/workflows/omega-gate.yml. Deleting either now fails UEC-L-02.
#
# Exit semantics: 0 all five criteria hold, 1 a criterion refused, 2 FAULT (no verdict).
# ===========================================================================
.PHONY: omega omega-gate omega-json omega-scope omega-seal

# omega: the human-readable measurement — every phase, every ratchet, every note.
omega: bootstrap-quiet
	@$(PY) -m engine.universal_discovery

# omega-gate: fail-closed. Refuses an artifact with no disposition, an artifact with no
# authority, a relocation that changes a verdict, and any ratchet worse than this
# repository's own best with no written justification.
#
# INVOKED BY ITS OWN MODULE PATH, and that is UEC-L-04's requirement rather than a style
# choice: UEC-000001 locates every `engine/*/gate.py` as an enforcement artifact and
# requires each to be invoked by a Makefile target, a workflow or a verify.sh stage.
# Reaching it only as `-m engine.universal_discovery` left the module UEC names with no
# invoker under the name UEC uses.
omega-gate: bootstrap-quiet
	@$(PY) -m engine.universal_discovery.gate >/dev/null \
	  || { echo "OMEGA GATE CLOSED — run 'make omega' for the named refusals" >&2; exit 1; }
	@echo "omega-gate: scope derived, authority total, graph invariant, every ratchet holds"

# omega-json: the machine-readable surface, for a consumer that needs the artifact table.
omega-json: bootstrap-quiet
	@$(PY) -m engine.universal_discovery --json

# omega-scope: what replaced the 78 --cov= flags, the 78 source paths and the 7 testpaths.
# Printed rather than described, so a reader can check the denominator the suite runs under.
omega-scope: bootstrap-quiet
	@$(PY) -m engine.universal_discovery --scope

# omega-seal: advance the Ω-4 best-ever values and write the surface evidence. Sealing moves
# each bound only DOWNWARD and is refused if the sealed document is looser than the run that
# wrote it, so this cannot turn a refusal into a pass — it can only record an improvement.
omega-seal: bootstrap-quiet
	@$(PY) -m engine.universal_discovery --seal

# omega-uci-seal: the same, for the six UCI laws now held to directions rather than ceilings.
.PHONY: uci-seal
uci-seal: bootstrap-quiet
	@$(PY) -m engine.certification_integrity.gate --seal-ratchet --quiet

# UCOS-SUB-001 — UCOS measured by the substrate it consumes. Exit 2 (FAULT) when the
# substrate is not importable, because a gate that passes without examining its subject is
# the false green every instrument here exists to refuse.
#
# IT NAMED `$(PYTHON)`, WHICH THIS MAKEFILE DOES NOT DEFINE. The recipe expanded to
# ` -m engine.substrate` and could never have run: `make -n substrate` printed
# `m engine.substrate`. It also carried no `.PHONY` and no `bootstrap-quiet`, so it was the
# only gate target that neither guaranteed an interpreter nor guaranteed being rebuilt. A
# target that cannot execute is not an invocation plane, and UEC-L-04 counted it as none.
# IT WAS NAMED `substrate`, WHICH PUT IT OUTSIDE GOVERNANCE. UEC-R-04 discovers make gate
# targets by the pattern `.*-gate$`; all fifty-seven others match it and this one did not, so
# the only Makefile target that ran a gate was also the only one no inventory could see.
.PHONY: substrate-gate
substrate-gate: bootstrap-quiet
	@$(PY) -m engine.substrate.gate
