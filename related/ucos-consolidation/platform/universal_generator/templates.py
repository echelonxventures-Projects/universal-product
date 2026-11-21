"""UCOS-UNG-001 — Artifact templates: the pluggable rendering authority.

:class:`ArtifactTemplate` is the extension point through which the generator admits a new way
of rendering an obligation. Adding a template — a different language, a different documentation
format, a stricter test shape — is a **registration**, never an edit to the generator that
consumes it. That is the whole reason the generator can be said to be unbounded: nothing here
knows how many kinds of artifact will one day exist.

Every shipped template renders from the **declaration alone**. None of them reads a filesystem,
none imports the nucleus it renders for, and none carries a project name. A template that
needed to look at the thing it generates would be describing an implementation rather than
deriving one, and the derived artifact would then be able to disagree with its declaration —
which is exactly the drift the Foundation exists to make impossible.

The rendered Python is deliberately *complete and conformant* rather than a stub with holes.
A skeleton that cannot pass the Constitution's own gates would hand its author the job the
generator exists to remove.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.universal_foundation.conformance import CapabilityDeclaration, FacetStatus
from platform.universal_generator.contracts import ArtifactKind, GenerationTarget
from platform.universal_generator.errors import GenerationTemplateError
from typing import Any

#: The banner every generated artifact carries, so a reader always knows what they are holding.
GENERATED_BANNER = (
    "Generated from the Ω Nucleus declaration by UCOS-UNG-001. Do not edit by hand: this "
    "artifact is a projection of the declaration, and an edit here would be a fact with "
    "nowhere to live. Change the declaration and re-derive."
)


@dataclass(frozen=True, slots=True)
class TemplateDescriptor:
    """What a template is, and which obligation it discharges."""

    name: str
    kind: ArtifactKind
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this descriptor."""
        return {"name": self.name, "kind": self.kind.value, "description": self.description}


class ArtifactTemplate(ABC):
    """The one authority that renders one kind of artifact from a nucleus declaration."""

    @abstractmethod
    def descriptor(self) -> TemplateDescriptor:
        """What this template is and which obligation it discharges."""

    @abstractmethod
    def render(self, declaration: CapabilityDeclaration, target: GenerationTarget) -> str:
        """Render the artifact content from the declaration alone."""

    @property
    def name(self) -> str:
        """The declared name under which this template is registered."""
        return self.descriptor().name

    def apply(self, declaration: CapabilityDeclaration, target: GenerationTarget) -> str:
        """Render, containing any fault as a typed refusal rather than a partial artifact."""
        try:
            content = self.render(declaration, target)
        except GenerationTemplateError:
            raise
        except Exception as exc:  # noqa: BLE001 - contained by design (fail-closed)
            raise GenerationTemplateError(
                "template could not render this declaration",
                template=self.name,
                target_id=target.target_id,
                capability_id=declaration.capability_id,
                detail=str(exc),
            ) from exc
        if not isinstance(content, str) or not content.strip():
            raise GenerationTemplateError(
                "template rendered nothing",
                template=self.name,
                target_id=target.target_id,
                capability_id=declaration.capability_id,
            )
        return content if content.endswith("\n") else content + "\n"


# --------------------------------------------------------------------------- helpers


def _docstring(declaration: CapabilityDeclaration, purpose: str) -> str:
    """The module docstring every generated Python artifact opens with."""
    return (
        f'"""{declaration.capability_id} — {declaration.name}: {purpose}.\n'
        f"\n"
        f"{GENERATED_BANNER}\n"
        f'"""\n'
    )


def _slug(declaration: CapabilityDeclaration) -> str:
    """The last segment of the declared package — the nucleus's short name."""
    return declaration.package.rsplit(".", 1)[-1]


def _prefix(declaration: CapabilityDeclaration) -> str:
    """A stable, declaration-derived error-code prefix (upper-cased identity tail)."""
    tail = declaration.capability_id.rsplit("-", 2)
    return tail[1].upper() if len(tail) == 3 else declaration.capability_id.upper()


def _nest(declaration: CapabilityDeclaration) -> dict[str, Any]:
    """Re-nest the flattened nucleus profile into the shape a register document carries."""
    nested: dict[str, Any] = {}
    for entry in declaration.nucleus.entries:
        cursor = nested
        parts = entry.path.split(".")
        for part in parts[:-1]:
            cursor = cursor.setdefault(part, {})
        key = "evidence" if entry.status is FacetStatus.PRESENT else "rationale"
        cursor[parts[-1]] = {"status": entry.status.value, key: entry.detail}
    return nested


def _register_entry(declaration: CapabilityDeclaration) -> dict[str, Any]:
    """The declaration projected back into the register document's own shape."""
    entry = declaration.to_dict()
    entry["nucleus"] = _nest(declaration)
    entry["replay"] = {"writes_tracked_artifacts": declaration.replay.writes_tracked_artifacts}
    if declaration.replay.target is not None:
        entry["replay"]["target"] = str(declaration.replay.target)
    if not declaration.cli:
        entry.pop("cli", None)
    return entry


def _json(payload: Any) -> str:
    """Canonical JSON: sorted, two-space indented, newline-terminated. Never written to disk."""
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)


def _registry_symbol(declaration: CapabilityDeclaration) -> tuple[str, str, str]:
    """The declared registry class, and the two method names its determinism is proven by."""
    if declaration.registries:
        first = declaration.registries[0]
        return first.symbol.attribute, first.ordered, first.require
    return f"{_slug(declaration).title().replace('_', '')}Registry", "ordered", "require"


def _extension_symbol(declaration: CapabilityDeclaration) -> str:
    """The declared extension point class through which new authority is admitted."""
    if declaration.extension_points:
        return declaration.extension_points[0].symbol.attribute
    return f"{_slug(declaration).title().replace('_', '')}Provider"


# --------------------------------------------------------------------------- templates


class DeclarationTemplate(ArtifactTemplate):
    """Renders the register entry — the artifact through which the nucleus becomes governed."""

    def descriptor(self) -> TemplateDescriptor:
        """This template renders the constitutional entry."""
        return TemplateDescriptor(
            name="nucleus-declaration",
            kind=ArtifactKind.CONSTITUTIONAL,
            description=(
                "The register entry through which the nucleus enters constitutional authority, "
                "in the register document's own shape so it is directly registrable."
            ),
        )

    def render(self, declaration: CapabilityDeclaration, target: GenerationTarget) -> str:
        """Project the declaration back into the register document's shape."""
        del target
        return _json(_register_entry(declaration))


class ContractTemplate(ArtifactTemplate):
    """Renders the published contract surface a consumer binds to (UFC-01, UFC-08)."""

    def descriptor(self) -> TemplateDescriptor:
        """This template renders the contract surface."""
        return TemplateDescriptor(
            name="contract-surface",
            kind=ArtifactKind.CONTRACT,
            description=(
                "The named, semantically versioned contract surface, with the identity, version "
                "and contract-tuple attributes the declaration itself names."
            ),
        )

    def render(self, declaration: CapabilityDeclaration, target: GenerationTarget) -> str:
        """Render the contract module from the declared identity, version and contract symbols."""
        del target
        identity = declaration.identity.attribute
        version = declaration.version.attribute
        contracts = declaration.contracts.attribute
        service = declaration.service_name
        lines = [
            _docstring(declaration, "the published contract surface"),
            "\nfrom __future__ import annotations\n",
            "\nfrom platform.foundation.contracts import ContractRef\n",
            "\n#: The canonical identity of this nucleus. Self-declared, never assigned (UFC-09).",
            f'\n{identity} = "{declaration.capability_id}"\n',
            "\n#: The semantic version governing the whole of this published surface (UFC-08).",
            f'\n{version} = "1.0.0"\n',
            "\n#: One entry per operation this nucleus offers. A consumer binds to a name here",
            "\n#: and never to a module, so the implementation may move without breaking anyone.",
            "\n_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (\n",
            f'    ("{service}.determine", "Produce this nucleus\'s determination."),\n',
            f'    ("{service}.describe", "Describe this nucleus\'s declared population."),\n',
            ")\n",
            "\n#: The versioned published contract surface.",
            f"\n{contracts}: tuple[ContractRef, ...] = tuple(\n",
            f"    ContractRef(name, {version}) for name, _ in _CONTRACT_NAMES\n",
            ")\n",
            "\n\ndef contract_names() -> tuple[str, ...]:\n",
            '    """The published contract names, in declaration order."""\n',
            "    return tuple(name for name, _ in _CONTRACT_NAMES)\n",
            "\n\n__all__ = [\n",
            f'    "{identity}",\n    "{version}",\n    "{contracts}",\n',
            '    "contract_names",\n',
            "]\n",
        ]
        return "".join(lines)


class ErrorsTemplate(ArtifactTemplate):
    """Renders the typed error taxonomy through which the nucleus refuses (UFC-10)."""

    def descriptor(self) -> TemplateDescriptor:
        """This template renders the error taxonomy."""
        return TemplateDescriptor(
            name="error-taxonomy",
            kind=ArtifactKind.ERRORS,
            description=(
                "The typed errors, each carrying a distinct stable code, that make every "
                "absence a refusal rather than an inference."
            ),
        )

    def render(self, declaration: CapabilityDeclaration, target: GenerationTarget) -> str:
        """Render the error module from the declared error base and identity."""
        del target
        base = declaration.errors_base.attribute
        prefix = _prefix(declaration)
        stem = base.removesuffix("Error") or base
        lines = [
            _docstring(declaration, "the error taxonomy"),
            "\nfrom __future__ import annotations\n",
            "\nfrom platform.foundation.errors import PlatformError\n",
            f"\n\nclass {base}(PlatformError):\n",
            f'    """Base class for all {declaration.capability_id} errors."""\n',
            f'\n    code = "EC2-{prefix}-000"\n',
            f"\n\nclass {stem}ContractError({base}):\n",
            '    """A value crossing this nucleus\'s contract boundary is malformed."""\n',
            f'\n    code = "EC2-{prefix}-CONTRACT-001"\n',
            f"\n\nclass {stem}RegistryError({base}):\n",
            '    """A population member is unknown, or is redefined in conflict with itself."""\n',
            f'\n    code = "EC2-{prefix}-REGISTRY-001"\n',
            f"\n\nclass {stem}DeterminationError({base}):\n",
            '    """A determination could not be made from the evidence supplied '
            '(fail-closed)."""\n',
            f'\n    code = "EC2-{prefix}-DETERMINATION-001"\n',
            "\n\n__all__ = [\n",
            f'    "{base}",\n',
            f'    "{stem}ContractError",\n',
            f'    "{stem}RegistryError",\n',
            f'    "{stem}DeterminationError",\n',
            "]\n",
        ]
        return "".join(lines)


class RegistryTemplate(ArtifactTemplate):
    """Renders the deterministic, fail-closed registry and its extension point (UFC-03, UFC-05)."""

    def descriptor(self) -> TemplateDescriptor:
        """This template renders the population registry."""
        return TemplateDescriptor(
            name="population-registry",
            kind=ArtifactKind.REGISTRY,
            description=(
                "The registry that orders by declared identity rather than insertion, refuses a "
                "conflicting redefinition, and reports an unknown member instead of defaulting."
            ),
        )

    def render(self, declaration: CapabilityDeclaration, target: GenerationTarget) -> str:
        """Render the registry module from the declared registry and extension-point symbols."""
        del target
        registry, ordered, require = _registry_symbol(declaration)
        provider = _extension_symbol(declaration)
        base = declaration.errors_base.attribute
        stem = base.removesuffix("Error") or base
        errors_module = declaration.errors_module
        lines = [
            _docstring(declaration, "the population registry and its extension point"),
            "\nfrom __future__ import annotations\n",
            "\nfrom abc import ABC, abstractmethod\n",
            "from collections.abc import Iterable\n",
            "from dataclasses import dataclass\n",
            f"from {errors_module} import {stem}RegistryError\n",
            "from typing import Any\n",
            "\n\n@dataclass(frozen=True, slots=True)\n",
            "class MemberDescriptor:\n",
            '    """What one member of this nucleus\'s population is."""\n',
            '\n    name: str\n    description: str = ""\n',
            "\n    def to_dict(self) -> dict[str, Any]:\n",
            '        """A JSON-serialisable projection."""\n',
            '        return {"name": self.name, "description": self.description}\n',
            f"\n\nclass {provider}(ABC):\n",
            '    """The extension point through which new authority enters (UFC-03).\n',
            "\n    Admitting an authority is a registration. It is never an edit to the nucleus\n",
            '    that consumes it, which is what keeps this population unbounded.\n    """\n',
            "\n    @abstractmethod\n",
            "    def descriptor(self) -> MemberDescriptor:\n",
            '        """What this member is."""\n',
            "\n    @abstractmethod\n",
            "    def provide(self) -> tuple[Any, ...]:\n",
            '        """What this member contributes."""\n',
            "\n    @property\n",
            "    def name(self) -> str:\n",
            '        """The declared name under which this member is registered."""\n',
            "        return self.descriptor().name\n",
            f"\n\nclass {registry}:\n",
            '    """The deterministic, fail-closed registry of this nucleus\'s population."""\n',
            '\n    __slots__ = ("_members",)\n',
            f"\n    def __init__(self, members: Iterable[{provider}] = ()) -> None:\n",
            f"        self._members: dict[str, {provider}] = {{}}\n",
            "        for member in members:\n",
            "            self.add(member)\n",
            f"\n    def add(self, member: {provider}) -> {provider}:\n",
            '        """Register a member, refusing a conflicting redefinition."""\n',
            f"        if not isinstance(member, {provider}):\n",
            f'            raise {stem}RegistryError("only a declared member may be registered")\n',
            "        existing = self._members.get(member.name)\n",
            "        if existing is not None and existing is not member:\n",
            f"            raise {stem}RegistryError(\n",
            '                "member is already registered with a different definition",\n',
            "                name=member.name,\n",
            "            )\n",
            "        self._members[member.name] = member\n",
            "        return member\n",
            f"\n    def get(self, name: str) -> {provider} | None:\n",
            '        """The member ``name``, or ``None`` when it is not registered."""\n',
            "        return self._members.get(name)\n",
            f"\n    def {require}(self, name: str) -> {provider}:\n",
            '        """The member ``name``; raises when unknown (fail-closed)."""\n',
            "        member = self._members.get(name)\n",
            "        if member is None:\n",
            f'            raise {stem}RegistryError("unknown member", name=name)\n',
            "        return member\n",
            f"\n    def {ordered}(self) -> tuple[{provider}, ...]:\n",
            '        """Every member, ordered by declared name — never by insertion."""\n',
            "        return tuple(self._members[key] for key in sorted(self._members))\n",
            "\n    @property\n",
            "    def count(self) -> int:\n",
            '        """How many members are registered."""\n',
            "        return len(self._members)\n",
            "\n    def to_dict(self) -> dict[str, Any]:\n",
            '        """A JSON-serialisable projection of this registry."""\n',
            "        return {\n",
            '            "count": self.count,\n',
            f'            "members": [member.descriptor().to_dict() '
            f"for member in self.{ordered}()],\n",
            "        }\n",
            "\n\n__all__ = [\n",
            f'    "MemberDescriptor",\n    "{provider}",\n    "{registry}",\n',
            "]\n",
        ]
        return "".join(lines)


class BootstrapTemplate(ArtifactTemplate):
    """Renders the declared bootstrap and service registration (UFC-02, UFC-07)."""

    def descriptor(self) -> TemplateDescriptor:
        """This template renders the runtime wiring."""
        return TemplateDescriptor(
            name="service-bootstrap",
            kind=ArtifactKind.BOOTSTRAP,
            description=(
                "The one declared path into existence: a bootstrap that performs no import-time "
                "side effect, and the service descriptor that makes the nucleus resolvable."
            ),
        )

    def render(self, declaration: CapabilityDeclaration, target: GenerationTarget) -> str:
        """Render the bootstrap module from the declared service and lifecycle symbols."""
        del target
        registry, _, _ = _registry_symbol(declaration)
        registry_module = (
            declaration.registries[0].symbol.module
            if declaration.registries
            else f"{declaration.package}.registry"
        )
        lines = [
            _docstring(declaration, "the declared bootstrap and service registration"),
            "\nfrom __future__ import annotations\n",
            "\nfrom platform.foundation.contracts import platform_contract\n",
            "from platform.foundation.services import ServiceDescriptor, ServiceRegistry\n",
            f"from {declaration.contracts.module} import (\n",
            f"    {declaration.identity.attribute},\n",
            f"    {declaration.version.attribute},\n",
            ")\n",
            f"from {registry_module} import {registry}\n",
            "\n#: The service name under which this nucleus is published.\n",
            f"{declaration.service_name.upper().replace('.', '_')}_SERVICE_NAME = "
            f'"{declaration.service_name}"\n',
            f"\n\ndef {declaration.bootstrap.attribute}() -> {registry}:\n",
            '    """Compose this nucleus from its declaration. The only path into existence.\n',
            "\n    Performs no filesystem read, no network call and no registration "
            "side effect at\n",
            "    import time (UFC-07): a module that acted on import could never be "
            "composed twice\n",
            '    and therefore could never be proven replay-identical.\n    """\n',
            f"    return {registry}()\n",
            f"\n\ndef {declaration.service_descriptor.attribute}() -> ServiceDescriptor:\n",
            '    """The published service descriptor for this nucleus."""\n',
            "    return ServiceDescriptor(\n",
            f'        name="{declaration.service_name}",\n',
            "        contract=platform_contract(\n",
            f'            "{declaration.service_name}.determine",\n',
            f"            {declaration.version.attribute},\n",
            f'            "{declaration.description or declaration.name}",\n',
            "        ),\n",
            f"        capabilities=({declaration.identity.attribute},),\n",
            f'        description="{declaration.name}",\n',
            "    )\n",
            f"\n\ndef {declaration.service_register.attribute}(registry: ServiceRegistry)"
            " -> ServiceDescriptor:\n",
            '    """Register this nucleus into ``registry`` (lazy, memoised)."""\n',
            "    return registry.register(\n",
            f"        {declaration.service_descriptor.attribute}(),"
            f" {declaration.bootstrap.attribute}\n",
            "    )\n",
            "\n\n__all__ = [\n",
            f'    "{declaration.bootstrap.attribute}",\n',
            f'    "{declaration.service_descriptor.attribute}",\n',
            f'    "{declaration.service_register.attribute}",\n',
            "]\n",
        ]
        return "".join(lines)


class RuntimeTemplate(ArtifactTemplate):
    """Renders the one-command runtime surface (UFC-06)."""

    def descriptor(self) -> TemplateDescriptor:
        """This template renders the runtime CLI."""
        return TemplateDescriptor(
            name="runtime-cli",
            kind=ArtifactKind.RUNTIME,
            description=(
                "The one-command surface. A nucleus that can only be exercised from a test or an "
                "interactive session is not a runtime and cannot be operated."
            ),
        )

    def render(self, declaration: CapabilityDeclaration, target: GenerationTarget) -> str:
        """Render the CLI module from the declared entry point and bootstrap."""
        del target
        entry = declaration.entry_point or f"ucos-{_slug(declaration).replace('_', '-')}"
        function = declaration.cli.attribute if declaration.cli else "main"
        lines = [
            _docstring(declaration, "the one-command runtime surface"),
            "\nfrom __future__ import annotations\n",
            "\nimport argparse\nimport json\nimport sys\n",
            "from collections.abc import Sequence\n",
            f"from {declaration.bootstrap.module} import {declaration.bootstrap.attribute}\n",
            "\nfrom engine.foundation.obs.errors import FoundationError\n",
            "\n\ndef _build_parser() -> argparse.ArgumentParser:\n",
            "    parser = argparse.ArgumentParser(\n",
            f'        prog="{entry}",\n',
            f'        description="{declaration.name} ({declaration.capability_id}).",\n',
            "    )\n",
            "    parser.add_argument(\n",
            '        "command", choices=("describe", "determine"), '
            'help="the operation to perform"\n',
            "    )\n",
            "    parser.add_argument(\n",
            '        "--json", action="store_true", dest="as_json", help="emit JSON on stdout"\n',
            "    )\n",
            "    return parser\n",
            f"\n\ndef {function}(argv: Sequence[str] | None = None) -> int:\n",
            '    """CLI entry point. Returns 0 on success and 2 on a fault (fail-closed)."""\n',
            "    args = _build_parser().parse_args(argv)\n",
            "    try:\n",
            f"        composed = {declaration.bootstrap.attribute}()\n",
            "        payload = composed.to_dict()\n",
            "    except (FoundationError, OSError) as exc:\n",
            f'        print(f"{declaration.capability_id} error: {{exc}}", file=sys.stderr)\n',
            "        return 2\n",
            f'    print("======== {declaration.capability_id} '
            f'{declaration.name} ========", file=sys.stderr)\n',
            '    print(f"  command: {args.command}", file=sys.stderr)\n',
            "    print(f\"  members: {payload.get('count', 0)}\", file=sys.stderr)\n",
            "    if args.as_json:\n",
            "        print(json.dumps(payload, indent=2, sort_keys=True))\n",
            "    return 0\n",
            '\n\nif __name__ == "__main__":  # pragma: no cover\n',
            f"    raise SystemExit({function}())\n",
            f'\n\n__all__ = ["{function}"]\n',
        ]
        return "".join(lines)


class PolicyTemplate(ArtifactTemplate):
    """Renders the declared policy document that configures the nucleus (UFC-04)."""

    def descriptor(self) -> TemplateDescriptor:
        """This template renders the policy catalogue."""
        return TemplateDescriptor(
            name="policy-catalogue",
            kind=ArtifactKind.POLICY,
            description=(
                "The declared document behaviour is configured by. Configuration that lives in "
                "code is not configuration, because it cannot be changed without a release."
            ),
        )

    def render(self, declaration: CapabilityDeclaration, target: GenerationTarget) -> str:
        """Render an empty but well-formed policy catalogue the nucleus can be specialised by."""
        del target
        return _json(
            {
                "register_id": f"ucos.{_slug(declaration).replace('_', '.')}.policy",
                "$comment": (
                    f"The declared population {declaration.capability_id} governs. Registering a "
                    "member is an entry here and requires no change to any module. "
                    + GENERATED_BANNER
                ),
                "members": [],
            }
        )


class DocumentationTemplate(ArtifactTemplate):
    """Renders the documentation of record, derived from the declaration."""

    def descriptor(self) -> TemplateDescriptor:
        """This template renders documentation."""
        return TemplateDescriptor(
            name="nucleus-documentation",
            kind=ArtifactKind.DOCUMENTATION,
            description=(
                "Documentation derived from the declaration cannot drift from it. Documentation "
                "authored beside the declaration always can."
            ),
        )

    def render(self, declaration: CapabilityDeclaration, target: GenerationTarget) -> str:
        """Render the nucleus README from the declaration alone."""
        del target
        rows = [
            f"# {declaration.capability_id} — {declaration.name}",
            "",
            f"> {GENERATED_BANNER}",
            "",
            declaration.description or "",
            "",
            "## Identity",
            "",
            f"* **Universal identifier** — `{declaration.capability_id}`",
            f"* **Constitutional domain** — `{declaration.domain.value}`",
            f"* **Package** — `{declaration.package}`",
            f"* **Identity symbol** — `{declaration.identity}`",
            f"* **Contract surface** — `{declaration.contracts}`",
            f"* **Version symbol** — `{declaration.version}`",
            "",
            "## Runtime",
            "",
            f"* **Service** — `{declaration.service_name}`",
            f"* **Bootstrap** — `{declaration.bootstrap}`",
            f"* **One command** — `{declaration.entry_point or '(none declared)'}`",
            "",
            "## Composition",
            "",
        ]
        if declaration.dependencies:
            rows.extend(f"* depends on `{item}`" for item in declaration.dependencies)
        else:
            rows.append("* depends on nothing; available for composition by reference")
        rows.extend(["", "## Extension points", ""])
        if declaration.extension_points:
            rows.extend(
                f"* `{point.symbol}` — admits new authority by registration"
                for point in declaration.extension_points
            )
        else:
            rows.append("* none declared")
        rows.extend(
            ["", "## Ω Nucleus profile", "", "| Facet | Status | Reason |", "| --- | --- | --- |"]
        )
        rows.extend(
            f"| `{entry.path}` | {entry.status.value} | {entry.detail} |"
            for entry in declaration.nucleus.entries
        )
        rows.append("")
        return "\n".join(rows)


class TestTemplate(ArtifactTemplate):
    """Renders the executable obligations that ship with the nucleus."""

    def descriptor(self) -> TemplateDescriptor:
        """This template renders the test module."""
        return TemplateDescriptor(
            name="conformance-tests",
            kind=ArtifactKind.TESTS,
            description=(
                "The obligations that arrive with the artifact. A generated artifact with no "
                "executable obligation attached is a claim, not a capability."
            ),
        )

    def render(self, declaration: CapabilityDeclaration, target: GenerationTarget) -> str:
        """Render tests that hold the declaration and the implementation to each other."""
        del target
        registry, ordered, require = _registry_symbol(declaration)
        registry_module = (
            declaration.registries[0].symbol.module
            if declaration.registries
            else f"{declaration.package}.registry"
        )
        base = declaration.errors_base.attribute
        stem = base.removesuffix("Error") or base
        lines = [
            _docstring(
                declaration,
                "the obligations its declaration places on it",
            ),
            "\nfrom __future__ import annotations\n",
            "\nimport pytest\n",
            f"from {declaration.contracts.module} import (\n",
            f"    {declaration.identity.attribute},\n",
            f"    {declaration.contracts.attribute},\n",
            f"    {declaration.version.attribute},\n",
            ")\n",
            f"from {declaration.errors_module} import {stem}RegistryError\n",
            f"from {registry_module} import {registry}\n",
            f"from {declaration.bootstrap.module} import (\n",
            f"    {declaration.bootstrap.attribute},\n",
            f"    {declaration.service_descriptor.attribute},\n",
            ")\n",
            "\nfrom platform.foundation.services import ServiceRegistry\n",
            "\n\ndef test_identity_is_self_declared() -> None:\n",
            '    """UFC-09: the identity lives with the nucleus, not in a governing module."""\n',
            f'    assert {declaration.identity.attribute} == "{declaration.capability_id}"\n',
            "\n\ndef test_contract_surface_is_published_at_one_version() -> None:\n",
            '    """UFC-01/UFC-08: one declared version governs the whole published surface."""\n',
            f"    assert {declaration.contracts.attribute}\n",
            f"    versions = {{ref.version for ref in {declaration.contracts.attribute}}}\n",
            f"    assert versions == {{{declaration.version.attribute}}}\n",
            "\n\ndef test_bootstrap_is_deterministic() -> None:\n",
            '    """UFC-11: two independent builds agree, or nothing built is certifiable."""\n',
            f"    first = {declaration.bootstrap.attribute}()\n",
            f"    second = {declaration.bootstrap.attribute}()\n",
            "    assert first.to_dict() == second.to_dict()\n",
            "\n\ndef test_registry_refuses_an_unknown_member() -> None:\n",
            '    """UFC-05: an unknown member is reported, never substituted with a default."""\n',
            f"    with pytest.raises({stem}RegistryError):\n",
            f'        {registry}().{require}("member-that-was-never-registered")\n',
            "\n\ndef test_registry_orders_by_identity_not_insertion() -> None:\n",
            '    """UFC-05: order is a property of the declaration, not of who arrived first."""\n',
            f"    registry = {registry}()\n",
            f"    assert list(registry.{ordered}()) == sorted(\n",
            f"        registry.{ordered}(), key=lambda member: member.name\n",
            "    )\n",
            "\n\ndef test_service_registers_validates_and_resolves() -> None:\n",
            '    """UFC-02: reachable only by importing its module is not integrated."""\n',
            "    services = ServiceRegistry()\n",
            f"    descriptor = {declaration.service_descriptor.attribute}()\n",
            f'    assert descriptor.name == "{declaration.service_name}"\n',
            f"    services.register(descriptor, {declaration.bootstrap.attribute})\n",
            "    services.validate()\n",
            f'    assert services.resolve("{declaration.service_name}") is not None\n',
        ]
        return "".join(lines)


class BuildTemplate(ArtifactTemplate):
    """Renders the build wiring that publishes the runtime surface (UFC-06)."""

    def descriptor(self) -> TemplateDescriptor:
        """This template renders the build entry point."""
        return TemplateDescriptor(
            name="build-entry-point",
            kind=ArtifactKind.BUILD,
            description=(
                "The console-script and coverage wiring. A declared entry point the build does "
                "not publish is a runtime surface nobody can reach."
            ),
        )

    def render(self, declaration: CapabilityDeclaration, target: GenerationTarget) -> str:
        """Render the build manifest fragment the declared entry point requires."""
        del target
        entry = declaration.entry_point or f"ucos-{_slug(declaration).replace('_', '-')}"
        cli = str(declaration.cli) if declaration.cli else f"{declaration.package}.cli:main"
        return "\n".join(
            [
                f"# {declaration.capability_id} — {declaration.name}",
                f"# {GENERATED_BANNER}",
                "#",
                "# Merge into [project.scripts]:",
                f'{entry} = "{cli}"',
                "#",
                "# Merge into [tool.pytest.ini_options] addopts and [tool.coverage.run] source,",
                "# so the nucleus is measured by the same gate as every other:",
                f"#   --cov={declaration.package}",
                f'#   "{declaration.package.replace(".", "/")}"',
                "",
            ]
        )


#: The templates shipped with the generator — one per declared obligation. Registering a
#: different renderer for the same obligation is a registration, never an edit here.
SHIPPED_TEMPLATES: tuple[type[ArtifactTemplate], ...] = (
    DeclarationTemplate,
    ContractTemplate,
    ErrorsTemplate,
    RegistryTemplate,
    BootstrapTemplate,
    RuntimeTemplate,
    PolicyTemplate,
    DocumentationTemplate,
    TestTemplate,
    BuildTemplate,
)


def shipped_templates() -> tuple[ArtifactTemplate, ...]:
    """One instance of every shipped template, in declaration order."""
    return tuple(template() for template in SHIPPED_TEMPLATES)


def template_fingerprint(templates: Iterable[ArtifactTemplate]) -> str:
    """The deterministic content fingerprint of a template population."""
    payload: list[Mapping[str, Any]] = [item.descriptor().to_dict() for item in templates]
    return content_hash({"templates": sorted(payload, key=lambda item: str(item["name"]))})


__all__ = [
    "GENERATED_BANNER",
    "SHIPPED_TEMPLATES",
    "ArtifactTemplate",
    "BootstrapTemplate",
    "BuildTemplate",
    "ContractTemplate",
    "DeclarationTemplate",
    "DocumentationTemplate",
    "ErrorsTemplate",
    "PolicyTemplate",
    "RegistryTemplate",
    "RuntimeTemplate",
    "TemplateDescriptor",
    "TestTemplate",
    "shipped_templates",
    "template_fingerprint",
]
