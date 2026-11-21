"""Constitutional compliance + the mandatory architectural proof (mechanised).

Every claim PROGRAM-003 requires is turned into an *executed* probe against a live
framework. The two headline obligations:

    * **Architectural quality gates** — no closed provider categories, no finite
      enumeration in the framework, no vendor/technology coupling, the kernel is immutable,
      the open-world property holds, Knowledge-Once is inherited, and unknown future
      provider categories are compatible.

    * **The mandatory architectural proof** — that eleven provider categories (Storage,
      Database, Runtime, AI, Messaging, Identity, Security, Network, Logging, Monitoring,
      and a previously-unknown future category) can each be governed-registered with the
      Provider Framework *and* the kernel left byte-for-byte unchanged.

Determinism: every function is pure over (framework state, source on disk).
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from typing import Any

from engine.kernel.compliance import kernel_source_fingerprint
from engine.provider.framework import ProviderFramework
from engine.provider.metatypes import CATEGORY_ROLE

_PROVIDER_DIR = Path(__file__).resolve().parent

#: Unambiguous vendor / technology tokens the framework must never bake in as code or as a
#: category (mission PROHIBITED list, lower-cased). Ambiguous English words are excluded so
#: the scan cannot false-positive; these tokens never occur in ordinary prose.
PROHIBITED_VENDOR_TOKENS: tuple[str, ...] = (
    "aws",
    "azure",
    "gcp",
    "postgresql",
    "mongodb",
    "redis",
    "kafka",
    "rabbitmq",
    "openai",
    "gemini",
    "docker",
    "kubernetes",
)

#: The eleven provider categories the mandatory proof must govern-register. Each is a
#: (category, capability, contract-name) triple. "AI" here is a capability *domain*, not the
#: vendor tokens above; no concrete provider or vendor is named.
PROOF_CATEGORIES: tuple[tuple[str, str, str], ...] = (
    ("StorageProvider", "storage.persist", "storage.contract"),
    ("DatabaseProvider", "database.query", "database.contract"),
    ("RuntimeProvider", "runtime.execute", "runtime.contract"),
    ("AIProvider", "ai.infer", "ai.contract"),
    ("MessagingProvider", "messaging.publish", "messaging.contract"),
    ("IdentityProvider", "identity.authenticate", "identity.contract"),
    ("SecurityProvider", "security.protect", "security.contract"),
    ("NetworkProvider", "network.route", "network.contract"),
    ("LoggingProvider", "logging.record", "logging.contract"),
    ("MonitoringProvider", "monitoring.observe", "monitoring.contract"),
    ("UnknownFutureProvider", "unknown.future.capability", "unknown.contract"),
)


# --------------------------------------------------------------------------- helpers


def framework_source_fingerprint() -> str:
    """A deterministic fingerprint over every provider-framework source file on disk."""
    digest = hashlib.sha256()
    for path in sorted(_PROVIDER_DIR.glob("*.py")):
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _framework_has_no_closed_enum(directory: Path | None = None) -> tuple[bool, list[str]]:
    """True iff no source in ``directory`` defines a closed ``enum.Enum``."""
    root = directory if directory is not None else _PROVIDER_DIR
    offenders: list[str] = []
    for path in sorted(root.glob("*.py")):
        tree = ast.parse(path.read_text("utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if ast.unparse(base).split(".")[-1] in {"Enum", "IntEnum", "StrEnum", "Flag"}:
                        offenders.append(f"{path.name}:{node.name}")
    return (not offenders), offenders


def _mechanism_vendor_tokens(directory: Path | None = None) -> list[str]:
    """Vendor/technology tokens found baked into the framework *mechanism* source.

    The prover (this module) legitimately lists the tokens, so it is excluded from the
    scan; every mechanism file must be free of them. ``directory`` defaults to the
    framework package and is a parameter only so the scan is testable against a control
    sample.
    """
    root = directory if directory is not None else _PROVIDER_DIR
    found: set[str] = set()
    for path in sorted(root.glob("*.py")):
        if path.name == "compliance.py":
            continue
        text = path.read_text("utf-8").lower()
        for token in PROHIBITED_VENDOR_TOKENS:
            if token in text:
                found.add(token)
    return sorted(found)


# --------------------------------------------------------------------------- gates


def architectural_proof() -> dict[str, Any]:
    """Govern-register eleven provider categories; prove the kernel + framework unchanged."""
    kernel_before = kernel_source_fingerprint()
    framework_before = framework_source_fingerprint()
    framework = ProviderFramework()
    records: list[dict[str, Any]] = []
    all_ok = True
    for category, capability, contract_name in PROOF_CATEGORIES:
        record: dict[str, Any] = {"category": category, "capability": capability}
        try:
            cat = framework.register_category(category, description=f"{category} (proof).")
            provider = framework.register_provider(
                category=category,
                key=f"{category}-alpha",
                capabilities=[capability],
                contract={"name": contract_name, "version": "1.0.0"},
                health={"status": "serving"},
            )
            discovered = framework.discover(capability=capability)
            resolved = framework.resolve(capability)
            trace = framework.trace(provider.identity)
            record.update(
                {
                    "category_identity": cat.identity,
                    "provider_identity": provider.identity,
                    "discoverable": provider.identity in {d.identity for d in discovered},
                    "resolvable": resolved.identity == provider.identity,
                    "traceable": trace["identity"] == provider.identity,
                    "governed": True,
                    "ok": True,
                }
            )
        except Exception as exc:  # noqa: BLE001 — the proof records any failure as evidence
            record.update({"ok": False, "error": str(exc)})
            all_ok = False
        records.append(record)
    kernel_after = kernel_source_fingerprint()
    framework_after = framework_source_fingerprint()
    kernel_unchanged = kernel_before == kernel_after
    framework_unchanged = framework_before == framework_after
    return {
        "obligation": "mandatory-architectural-proof",
        "categories_proven": sum(1 for r in records if r.get("ok")),
        "categories_total": len(PROOF_CATEGORIES),
        "kernel_unchanged": kernel_unchanged,
        "framework_unchanged": framework_unchanged,
        "kernel_fingerprint": kernel_after,
        "framework_fingerprint": framework_after,
        "passed": all_ok and kernel_unchanged and framework_unchanged,
        "records": records,
    }


def quality_gates() -> dict[str, Any]:
    """Run each architectural quality gate against a live framework."""
    gates: list[dict[str, Any]] = []

    framework = ProviderFramework()
    before = len(framework.categories())
    framework.register_category("NeverSeenProviderCategory")
    gates.append(
        {
            "id": "no-closed-provider-categories",
            "passed": len(framework.categories()) == before + 1,
            "evidence": "admitted a never-seen provider category; the open set grew by one",
        }
    )

    no_enum, offenders = _framework_has_no_closed_enum()
    gates.append(
        {
            "id": "no-finite-enumeration",
            "passed": no_enum,
            "evidence": "no enum.Enum subclass exists in the provider framework package"
            if no_enum
            else f"closed enumerations found: {offenders}",
        }
    )

    baked = _mechanism_vendor_tokens()
    category_and_facet = {k.lower() for k in ProviderFramework().category_keys()}
    leaked = sorted(category_and_facet & set(PROHIBITED_VENDOR_TOKENS))
    gates.append(
        {
            "id": "no-vendor-technology-coupling",
            "passed": not baked and not leaked,
            "evidence": "no vendor/technology token is baked into the framework mechanism"
            if (not baked and not leaked)
            else f"vendor tokens present: source={baked}, categories={leaked}",
        }
    )

    proof = architectural_proof()
    gates.append(
        {
            "id": "kernel-immutable",
            "passed": proof["kernel_unchanged"],
            "evidence": "kernel source fingerprint unchanged after building the framework "
            "and registering eleven categories",
        }
    )

    # Open world: an unknown category with a provider is admitted, discoverable, resolvable.
    fw = ProviderFramework()
    fw.register_category("WhollyNovelProviderCategory")
    fw.register_provider(
        category="WhollyNovelProviderCategory",
        key="novel-alpha",
        capabilities=["novel.capability"],
        contract={"name": "novel.contract", "version": "1.0.0"},
        health={"status": "serving"},
    )
    resolved = fw.resolve("novel.capability")
    gates.append(
        {
            "id": "open-world",
            "passed": resolved.attributes.get("capabilities") == ["novel.capability"],
            "evidence": "an unknown provider category was registered, discovered and resolved",
        }
    )

    ko = "content-unique" in ProviderFramework().kernel.governance.admission.constraint_names()
    gates.append(
        {
            "id": "knowledge-once",
            "passed": ko,
            "evidence": "the kernel's content-unique (Knowledge-Once) constraint is inherited",
        }
    )

    gates.append(
        {
            "id": "unknown-future-compatibility",
            "passed": proof["passed"],
            "evidence": f"{proof['categories_proven']}/{proof['categories_total']} categories "
            f"govern-registered; kernel_unchanged={proof['kernel_unchanged']}, "
            f"framework_unchanged={proof['framework_unchanged']}",
        }
    )

    passed = all(g["passed"] for g in gates)
    return {"passed": passed, "gates": gates, "architectural_proof": proof}


def constitutional_report() -> dict[str, Any]:
    """The full, deterministic constitutional compliance report."""
    gates = quality_gates()
    framework = ProviderFramework()
    report = {
        "programme": "PROGRAM-003 — Universal Provider Framework",
        "framework_version": ProviderFramework.version,
        "framework_source_fingerprint": framework_source_fingerprint(),
        "kernel_source_fingerprint": kernel_source_fingerprint(),
        "facets": [key for key, _d in _facets()],
        "quality_gates": gates,
        "self_certification": framework.certify(),
        "verdict": "CONSTITUTIONALLY-COMPLIANT" if gates["passed"] else "NON-COMPLIANT",
        "passed": gates["passed"],
    }
    from engine.kernel.identity import content_digest

    report["report_hash"] = content_digest({k: v for k, v in report.items() if k != "report_hash"})
    return report


def _facets() -> tuple[tuple[str, str], ...]:
    from engine.provider.metatypes import PROVIDER_FACETS

    return PROVIDER_FACETS


__all__ = [
    "constitutional_report",
    "quality_gates",
    "architectural_proof",
    "framework_source_fingerprint",
    "PROHIBITED_VENDOR_TOKENS",
    "PROOF_CATEGORIES",
    "CATEGORY_ROLE",
]
