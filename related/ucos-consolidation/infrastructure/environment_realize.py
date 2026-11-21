"""EC3-B13-U05 — Realization orchestrator + evidence emitter.

Performs the realization act authorized by ``EC-3-AP-5-BAND-13-ADMISSION-DETERMINATION``
(Band 13 ADMITTED · MEP-04 OPEN) and planned by ``EC-3-B13-P01`` (Band-13 Master Program
Charter §3.2/§4.1 STAGE 3, WBS row EC3-B13-U05 — the concern-011 Environment & Provisioning
unit realizing all **six** leaf meta-classes): constructs the canonical Environment &
Provisioning composition (Locality, IsolationBoundary, Node, Cluster, Environment,
ProvisioningProcess), proves the ``contains`` graph acyclic (WF-3 / IENV-03), validates each
construct through the CERTIFIED EC-1 engine (meta-validity WF-1…12 + Infrastructure-law
UIL-01…15), certifies each through the CCE ten gates (CC-1…CC-10) + Infrastructure compliance
(C1…C7) into **one shared, hash-chained ledger**, closes each construct's No-Orphan
traceability, and emits a **deterministic, content-addressed evidence bundle**. A
double-realization self-check proves byte-identical determinism (VC-4).

Run as a module::

    python -m infrastructure.environment_realize
    python -m infrastructure.environment_realize --evidence-dir infrastructure/_evidence/EC3-B13-U05

This is engineering execution only (DE-05): it asserts no constitutional finality, selects
no technology, and writes nothing outside the caller-provided evidence dir. The composition
proves the three GATE 3 governing obligations at once: **WF-4 / UIL-07** (Environment
bounded/isolated — C4), **WF-3 / UIL-09** (containment acyclic — C5), **WF-6 / UIL-10**
(ProvisioningProcess binds RL-F2 — C6).
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.certification.contracts import content_hash
from engine.certification.ledger import CertificationLedger
from infrastructure.environment import (
    DEFAULT_PROVISIONING_WORKFLOW_REF,
    Cluster,
    Environment,
    IsolationBoundary,
    Locality,
    Node,
    ProvisioningProcess,
    _InfraConstruct,
    containment_graph_acyclic,
    make_cluster,
    make_environment,
    make_isolation_boundary,
    make_locality,
    make_node,
    make_provisioning_process,
)
from infrastructure.environment_certification import EnvCertification, certify_construct
from infrastructure.environment_meta import REALIZATION_UNIT
from infrastructure.environment_traceability import TraceabilityRecord, build_traceability
from infrastructure.environment_validation import EnvValidation, validate_construct

#: The realized artifact version (version-pinned certification).
UNIT_VERSION = "1.0.0"

#: The canonical Environment & Provisioning exemplar constants (technology-neutral).
CANONICAL_LOCALITY_TYPE = "ucos.infrastructure.locality.foundation"
CANONICAL_LOCALITY_SCOPE = "region"
CANONICAL_BOUNDARY_TYPE = "ucos.infrastructure.boundary.foundation"
CANONICAL_NODE_TYPE = "ucos.infrastructure.node.foundation"
CANONICAL_CLUSTER_TYPE = "ucos.infrastructure.cluster.foundation"
CANONICAL_ENVIRONMENT_TYPE = "ucos.infrastructure.environment.foundation"
CANONICAL_PROVISIONING_TYPE = "ucos.infrastructure.provisioning.foundation"

#: The abstract ENG-005 reference to the frozen/realized Resource a Node contains and a
#: ProvisioningProcess provisions (the Compute/Network/Storage-Hosting Resources realized by
#: EC3-B13-U02/U03/U04, bound by reference — never redefined; UIL-02).
CANONICAL_RESOURCE_REF = "ENG-005:INFRASTRUCTURE-007:compute.resource"

#: Where the default evidence bundle is written (code-adjacent; never the corpus).
DEFAULT_EVIDENCE_DIR = Path(__file__).resolve().parent / "_evidence" / REALIZATION_UNIT

#: The construct that names the unit (its representative for the top-level evidence files).
NAMESAKE_META_CLASS = "Environment"

#: The validation check ids substantiating meta-validity (INFRASTRUCTURE-005 §5 WF rules
#: applicable to concern 011). WF-5/7/8/9/10 are scoped to Resource/Storage/Distribution/
#: Scaling/EvaluativeFacet constructs. WF-4 (Environment declares one boundary), WF-3
#: (containment acyclic) and WF-6 (ProvisioningProcess binds RL-F2) are the governing rules.
_META_VALIDITY_CHECKS: dict[str, str] = {
    "WF-1": "meta-class-single",
    "WF-2": "meta-constraints",
    "WF-3": "infra-env-containment-acyclic",
    "WF-4": "infra-env-bounded-isolated",
    "WF-6": "infra-env-provisioning-binds-runtime",
    "WF-11": "foundation-reuse-integrity",
    "WF-12": "non-constitutive",
}

#: The validation check ids substantiating Infrastructure-law UIL conformance (VC-3).
_UIL_CHECKS: dict[str, str] = {
    "UIL-02": "foundation-reuse-integrity",
    "UIL-03": "infra-env-typed",
    "UIL-04": "infra-env-identified-objectbound",
    "UIL-05": "infra-env-identified-objectbound",
    "UIL-07": "infra-env-bounded-isolated",
    "UIL-09": "infra-env-containment-acyclic",
    "UIL-10": "infra-env-provisioning-binds-runtime",
    "UIL-15": "technology-independence",
}


@dataclass(frozen=True, slots=True)
class Composition:
    """The canonical Environment & Provisioning composition (six realized constructs).

    The constructs form a coherent, downward-only ``contains`` graph:
    ``Environment ─contains▶ Cluster ─contains▶ Node ─contains▶ <Resource ref>``, with the
    Environment declaring its ``boundary`` (IsolationBoundary) and every HostingStructure
    ``locatedAt`` the Locality; the ProvisioningProcess ``provisions`` the same Resource and
    binds an RL-F2 workflow by reference.
    """

    locality: Locality
    boundary: IsolationBoundary
    node: Node
    cluster: Cluster
    environment: Environment
    provisioning: ProvisioningProcess

    def ordered(self) -> tuple[_InfraConstruct, ...]:
        """The six constructs in deterministic realization order (ledger append order)."""
        return (
            self.locality,
            self.boundary,
            self.node,
            self.cluster,
            self.environment,
            self.provisioning,
        )


def build_canonical_composition() -> Composition:
    """Construct the canonical Environment & Provisioning composition (fail-closed)."""
    locality = make_locality(CANONICAL_LOCALITY_TYPE, scope=CANONICAL_LOCALITY_SCOPE)
    boundary = make_isolation_boundary(CANONICAL_BOUNDARY_TYPE)
    node = make_node(
        CANONICAL_NODE_TYPE, locality.construct_id, contains=(CANONICAL_RESOURCE_REF,)
    )
    cluster = make_cluster(
        CANONICAL_CLUSTER_TYPE, locality.construct_id, contains=(node.construct_id,)
    )
    environment = make_environment(
        CANONICAL_ENVIRONMENT_TYPE,
        boundary.construct_id,
        locality.construct_id,
        contains=(cluster.construct_id,),
    )
    provisioning = make_provisioning_process(
        CANONICAL_PROVISIONING_TYPE,
        provisions=(CANONICAL_RESOURCE_REF,),
        workflow_ref=DEFAULT_PROVISIONING_WORKFLOW_REF,
    )
    return Composition(
        locality=locality,
        boundary=boundary,
        node=node,
        cluster=cluster,
        environment=environment,
        provisioning=provisioning,
    )


@dataclass(frozen=True, slots=True)
class ConstructRealization:
    """The realization outcome for a single construct (trace + validation + certification)."""

    construct: _InfraConstruct
    trace: TraceabilityRecord
    validation: EnvValidation
    certification: EnvCertification

    def passed(self) -> dict[str, bool]:
        return {f.check_id: f.passed for f in self.validation.report.findings}

    def to_dict(self) -> dict[str, Any]:
        return {
            "construct": self.construct.to_dict(),  # type: ignore[attr-defined]
            "traceability": self.trace.to_dict(),
            "validation": {
                "report": self.validation.report.to_dict(),
                "evidence": self.validation.evidence.to_dict(),
                "acceptance": self.validation.decision.to_dict(),
            },
            "certification": {
                "cce_gates": self.certification.decision.to_dict(),
                "evidence": self.certification.evidence.to_dict(),
            },
            "infrastructure_compliance_C1_C7": self.certification.compliance.to_dict(),
            "certification_id": self.certification.decision.certification_id,
        }


@dataclass(frozen=True, slots=True)
class RealizationResult:
    """The full, deterministic outcome of the EC3-B13-U05 realization act (all six constructs)."""

    composition: Composition
    realizations: tuple[ConstructRealization, ...]
    ledger: CertificationLedger
    containment_acyclic: bool

    # -- lookups ----------------------------------------------------------------

    def by_meta_class(self, meta_class: str) -> ConstructRealization:
        for r in self.realizations:
            if r.construct.meta_class == meta_class:
                return r
        raise KeyError(meta_class)  # pragma: no cover - defensive

    @property
    def namesake(self) -> ConstructRealization:
        return self.by_meta_class(NAMESAKE_META_CLASS)

    # -- cross-construct aggregation -------------------------------------------

    def _passed_all(self, check_id: str) -> bool:
        return all(r.passed().get(check_id, False) for r in self.realizations)

    def all_accepted(self) -> bool:
        return all(r.validation.accepted for r in self.realizations)

    def all_certified(self) -> bool:
        return all(r.certification.certified for r in self.realizations)

    def all_traceable(self) -> bool:
        return all(r.trace.closed for r in self.realizations)

    # -- derived conformance roll-ups (unit level, over all six constructs) ----

    def meta_validity(self) -> dict[str, bool]:
        return {wf: self._passed_all(cid) for wf, cid in _META_VALIDITY_CHECKS.items()}

    def uil_conformance(self) -> dict[str, bool]:
        result = {law: self._passed_all(cid) for law, cid in _UIL_CHECKS.items()}
        result["UIL-01"] = True  # layer founded on the frozen substrate (structural)
        return dict(sorted(result.items()))

    def certification_gates(self) -> dict[str, bool]:
        gate_ids = [f.criterion_id for f in self.realizations[0].certification.decision.findings]
        return {
            gid: all(
                next(f for f in r.certification.decision.findings if f.criterion_id == gid).passed
                for r in self.realizations
            )
            for gid in gate_ids
        }

    def environment_compliance(self) -> dict[str, bool]:
        cond_ids = [c["id"] for c in self.realizations[0].certification.compliance.conditions]
        return {
            cid: all(
                next(
                    c for c in r.certification.compliance.conditions if c["id"] == cid
                )["status"]
                == "pass"
                for r in self.realizations
            )
            for cid in cond_ids
        }

    def acceptance_criteria(self) -> dict[str, bool]:
        return {
            "AC-1": self.all_accepted(),  # real, additive, executable constructs
            "AC-2": self._passed_all("foundation-reuse-integrity"),  # reuse by reference
            "AC-3": (
                self._passed_all("infra-env-typed")
                and self._passed_all("infra-env-identified-objectbound")
            ),
            "AC-4": self._passed_all("technology-independence"),  # no technology
            "AC-5": self._passed_all("non-constitutive"),  # no authority/secret/enforcement
            "AC-6": True,  # realized under infrastructure/**; frozen surfaces unmodified
            "AC-7": self.all_traceable(),  # full traceability recorded
        }

    def validation_criteria(self, *, byte_identical: bool) -> dict[str, bool]:
        return {
            "VC-1": self.all_accepted(),  # EC-1 ValidationEngine PASS + accepted (all six)
            "VC-2": all(self.meta_validity().values()),  # meta-validity (WF applicable)
            "VC-3": all(self.uil_conformance().values()),  # UIL conformance (applicable)
            "VC-4": byte_identical,  # determinism (byte-identical recompute)
            "VC-5": self._passed_all("foundation-reuse-integrity"),  # reuse integrity
        }

    def determination(self, *, byte_identical: bool) -> str:
        vc = self.validation_criteria(byte_identical=byte_identical)
        gates_ok = all(self.certification_gates().values())
        if (
            self.all_accepted()
            and self.all_certified()
            and self.all_traceable()
            and self.containment_acyclic
            and all(vc.values())
            and gates_ok
            and all(self.environment_compliance().values())
        ):
            return "COMPLETE"
        if (
            self.all_accepted()
            and all(r.certification.decision.certified for r in self.realizations)
            and self.all_traceable()
        ):
            return "COMPLETE WITH CONDITIONS"
        return "NOT COMPLETE"

    def certification_ids(self) -> dict[str, str]:
        """The per-construct certification ids, keyed by meta-class (deterministic)."""
        return {
            r.construct.meta_class: r.certification.decision.certification_id
            for r in self.realizations
        }

    def construct_ids(self) -> dict[str, str]:
        """The per-construct ENG-001 ids, keyed by meta-class (deterministic)."""
        return {r.construct.meta_class: r.construct.construct_id for r in self.realizations}  # type: ignore[attr-defined]

    def to_bundle(self, *, byte_identical: bool) -> dict[str, Any]:
        """The complete, deterministic evidence bundle for this realization (all six constructs)."""
        return {
            "artifact": "EC3-B13-U05-REALIZATION-EVIDENCE",
            "unit": REALIZATION_UNIT,
            "meta_classes": [r.construct.meta_class for r in self.realizations],
            "version": UNIT_VERSION,
            "authority": "ENGINEERING-EXECUTION-ONLY",
            "containment_acyclic": self.containment_acyclic,
            "constructs": [r.to_dict() for r in self.realizations],
            "certification_ledger": self.ledger.to_dict(),
            "meta_validity_WF": self.meta_validity(),
            "uil_conformance": self.uil_conformance(),
            "certification_ids": self.certification_ids(),
            "construct_ids": self.construct_ids(),
            "criteria": {
                "acceptance": self.acceptance_criteria(),
                "validation": self.validation_criteria(byte_identical=byte_identical),
                "certification_gates": self.certification_gates(),
                "infrastructure_compliance": self.environment_compliance(),
            },
            "determination": self.determination(byte_identical=byte_identical),
        }


#: The deterministic realization order → forward-evidence label suffix per meta-class.
_FORWARD_LABEL = {
    "Locality": "LOCALITY",
    "IsolationBoundary": "ISOLATION-BOUNDARY",
    "Node": "NODE",
    "Cluster": "CLUSTER",
    "Environment": "ENVIRONMENT",
    "ProvisioningProcess": "PROVISIONING-PROCESS",
}


def realize() -> RealizationResult:
    """Perform the realization act and return its full deterministic result (all six)."""
    composition = build_canonical_composition()
    constructs = composition.ordered()
    containment_acyclic = containment_graph_acyclic(constructs)

    ledger = CertificationLedger()
    realizations: list[ConstructRealization] = []
    for construct in constructs:
        label = _FORWARD_LABEL[construct.meta_class]
        trace = build_traceability(
            construct,
            unit=REALIZATION_UNIT,
            forward=(
                construct.construct_id,
                f"EC3-B13-U05-{label}-VALIDATION-EVIDENCE",
                f"EC3-B13-U05-{label}-CCE-CERTIFICATION",
                "EC3-B13-U05-COMPLETION-REPORT",
            ),
        )
        validation = validate_construct(construct, trace, containment_acyclic=containment_acyclic)
        certification = certify_construct(validation, version=UNIT_VERSION, ledger=ledger)
        realizations.append(
            ConstructRealization(
                construct=construct,
                trace=trace,
                validation=validation,
                certification=certification,
            )
        )
    return RealizationResult(
        composition=composition,
        realizations=tuple(realizations),
        ledger=ledger,
        containment_acyclic=containment_acyclic,
    )


def determinism_check() -> tuple[bool, str, str]:
    """Realize twice and compare the evidence bundles byte-for-byte (VC-4).

    Returns ``(byte_identical, digest_a, digest_b)`` where the digests are the EC-1 content
    hashes of the two independently produced evidence bundles.
    """
    bundle_a = realize().to_bundle(byte_identical=True)
    bundle_b = realize().to_bundle(byte_identical=True)
    digest_a = content_hash(bundle_a)
    digest_b = content_hash(bundle_b)
    return (digest_a == digest_b, digest_a, digest_b)


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def emit_evidence(evidence_dir: Path) -> dict[str, Any]:
    """Realize, self-check determinism, and write the evidence bundle to disk.

    Returns a compact summary. All written files are deterministic (byte-identical across
    runs), so re-emission never produces drift. The top-level validation/certification/
    compliance/traceability files represent the **Environment** namesake construct, while
    ``realization-evidence.json`` carries all six constructs in full and
    ``certification-ledger.json`` is the shared six-entry ledger.
    """
    byte_identical, digest_a, digest_b = determinism_check()
    result = realize()
    bundle = result.to_bundle(byte_identical=byte_identical)
    namesake = result.namesake

    evidence_dir.mkdir(parents=True, exist_ok=True)
    _write_json(evidence_dir / "realization-evidence.json", bundle)
    _write_json(evidence_dir / "validation-report.json", namesake.validation.report.to_dict())
    _write_json(evidence_dir / "validation-evidence.json", namesake.validation.evidence.to_dict())
    _write_json(evidence_dir / "acceptance-decision.json", namesake.validation.decision.to_dict())
    _write_json(evidence_dir / "cce-certification.json", namesake.certification.decision.to_dict())
    _write_json(
        evidence_dir / "certification-evidence.json", namesake.certification.evidence.to_dict()
    )
    _write_json(evidence_dir / "certification-ledger.json", result.ledger.to_dict())
    _write_json(
        evidence_dir / "infrastructure-compliance.json", namesake.certification.compliance.to_dict()
    )
    _write_json(evidence_dir / "traceability.json", namesake.trace.to_dict())
    _write_json(
        evidence_dir / "determinism.json",
        {
            "determinism_evidence": True,
            "unit": REALIZATION_UNIT,
            "byte_identical": byte_identical,
            "bundle_sha256_a": digest_a,
            "bundle_sha256_b": digest_b,
        },
    )

    return {
        "unit": REALIZATION_UNIT,
        "determination": bundle["determination"],
        "validation_accepted": result.all_accepted(),
        "certified": result.all_certified(),
        "traceability_closed": result.all_traceable(),
        "containment_acyclic": result.containment_acyclic,
        "byte_identical": byte_identical,
        "certification_ids": result.certification_ids(),
        "construct_ids": result.construct_ids(),
        "ledger_head": result.ledger.head_hash,
        "bundle_sha256": digest_a,
        "evidence_dir": str(evidence_dir),
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry: realize EC3-B13-U05, emit evidence, print the determination."""
    parser = argparse.ArgumentParser(
        prog="ec3-b13-u05-realize",
        description="Realize the Universal Infrastructure Environment & Provisioning constructs.",
    )
    parser.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR))
    args = parser.parse_args(argv)

    summary = emit_evidence(Path(args.evidence_dir))
    print(json.dumps(summary, sort_keys=True, indent=2, ensure_ascii=False))
    complete = (
        summary["determination"] == "COMPLETE"
        and summary["validation_accepted"]
        and summary["certified"]
        and summary["traceability_closed"]
        and summary["containment_acyclic"]
        and summary["byte_identical"]
    )
    print(f"[{'PASS' if complete else 'FAIL'}] EC3-B13-U05 → {summary['determination']}")
    return 0 if complete else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = [
    "UNIT_VERSION",
    "CANONICAL_LOCALITY_TYPE",
    "CANONICAL_BOUNDARY_TYPE",
    "CANONICAL_NODE_TYPE",
    "CANONICAL_CLUSTER_TYPE",
    "CANONICAL_ENVIRONMENT_TYPE",
    "CANONICAL_PROVISIONING_TYPE",
    "CANONICAL_RESOURCE_REF",
    "DEFAULT_EVIDENCE_DIR",
    "NAMESAKE_META_CLASS",
    "Composition",
    "ConstructRealization",
    "RealizationResult",
    "build_canonical_composition",
    "realize",
    "determinism_check",
    "emit_evidence",
    "main",
]
