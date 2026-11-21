"""UCOS-EPIC-014 — Commercial Validation (Terminal T5).

The fourteen domain analyzers and the engine that runs them. Every analyzer is a **pure
function of the target's declared commercial facts**: it assimilates those facts through
the domain module that owns them and records a finding for each invariant it can — or
cannot — prove. An analyzer never raises for a commercial defect; it raises only if it is
itself malformed. Facts that will not assimilate produce a blocking FAIL naming the exact
assimilation error, so an unprovable commercial claim can never read as a pass.

The engine adds nothing to the verdict: it orders the analyzers canonically, collects the
findings, and lets :class:`~platform.commercial_intelligence.contracts.DomainReport` and
:class:`~platform.commercial_intelligence.contracts.CommercialIntelligenceReport` aggregate
them fail-closed. Certification is then a projection of that report
(:mod:`platform.commercial_intelligence.certification`), never a second opinion.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from platform.commercial_intelligence.approval import ApprovalChain, parse_records
from platform.commercial_intelligence.certification import Determination
from platform.commercial_intelligence.contracts import (
    BASIS_POINTS_SCALE,
    COMMERCIAL_AUTHORITY,
    CommercialDomain,
    CommercialIntelligenceReport,
    CommercialTarget,
    DomainReport,
    Finding,
    Severity,
    failed,
    passed,
)
from platform.commercial_intelligence.customer import CustomerBase
from platform.commercial_intelligence.documentation import DocumentationSet
from platform.commercial_intelligence.errors import (
    AnalyzerDefinitionError,
    CommercialIntelligenceError,
)
from platform.commercial_intelligence.evidence import EvidenceIndex
from platform.commercial_intelligence.investment import InvestmentCase
from platform.commercial_intelligence.licensing import (
    EntitlementRequest,
    LicenseGrant,
    LicenseRegister,
)
from platform.commercial_intelligence.marketplace import MarketplaceRegistry
from platform.commercial_intelligence.packages import CommercialPackage, assemble_package
from platform.commercial_intelligence.policy import (
    PolicyEffect,
    PolicyRegister,
    PolicyRequest,
)
from platform.commercial_intelligence.portfolio import Portfolio
from platform.commercial_intelligence.pricing import (
    PriceBook,
    QuoteLineRequest,
    build_quote,
)
from platform.commercial_intelligence.product import Product, ProductCatalog, ProductState
from typing import Any, Protocol, runtime_checkable

#: The action name probed to prove that an action no policy governs is refused. It is
#: deliberately un-declarable as a real action (a policy declaring it would be a defect).
UNGOVERNED_PROBE_ACTION = "__ungoverned_probe__"


@runtime_checkable
class DomainAnalyzer(Protocol):
    """A pure analyzer over one commercial domain's declared facts."""

    domain: CommercialDomain

    def analyze(self, target: CommercialTarget) -> tuple[Finding, ...]:
        """Return the ordered findings this analyzer can prove from ``target``."""


def _bound(facts: Mapping[str, Any], key: str) -> int:
    """Read an integer basis-point bound, defaulting to the unbounded 10000."""
    value = facts.get(key, BASIS_POINTS_SCALE)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return BASIS_POINTS_SCALE
    return value


def _sequence(facts: Mapping[str, Any], key: str) -> Sequence[Any]:
    value = facts.get(key, ())
    if isinstance(value, str | bytes) or not isinstance(value, Sequence):
        return ()
    return value


@dataclass(frozen=True, slots=True)
class MarketplaceAnalyzer:
    """Marketplace Intelligence: listings resolve to catalog products and never phantom."""

    domain: CommercialDomain = CommercialDomain.MARKETPLACE_INTELLIGENCE

    def analyze(self, target: CommercialTarget) -> tuple[Finding, ...]:
        facts = target.domain_facts(self.domain)
        try:
            catalog = ProductCatalog.from_sequence(facts.get("products", ()))
            registry = MarketplaceRegistry.from_sequence(facts.get("listings", ()))
        except CommercialIntelligenceError as exc:
            return (
                failed(
                    "CMI-MKT-001",
                    self.domain,
                    f"marketplace facts are not assimilable: {exc}",
                ),
            )
        findings = [
            passed(
                "CMI-MKT-001",
                self.domain,
                f"{len(registry.listings)} listing(s) and {len(catalog.products)} "
                "catalog product(s) assimilated",
                state_counts=registry.state_counts(),
            )
        ]
        unsound = [v for v in registry.integrity(catalog) if not v.sound]
        findings.append(
            passed("CMI-MKT-002", self.domain, "every listing resolves against the catalog")
            if not unsound
            else failed(
                "CMI-MKT-002",
                self.domain,
                f"{len(unsound)} listing(s) are unsound against the catalog",
                unsound=[v.to_dict() for v in unsound],
            )
        )
        findings.append(
            passed(
                "CMI-MKT-003",
                self.domain,
                f"{len(registry.visible())} listing(s) are commercially visible",
            )
            if registry.visible()
            else failed(
                "CMI-MKT-003",
                self.domain,
                "no listing is published — the marketplace offers nothing",
            )
        )
        return tuple(findings)


@dataclass(frozen=True, slots=True)
class LicensingAnalyzer:
    """Licensing Intelligence: every declared entitlement decides as the register requires."""

    domain: CommercialDomain = CommercialDomain.LICENSING_INTELLIGENCE

    def analyze(self, target: CommercialTarget) -> tuple[Finding, ...]:
        facts = target.domain_facts(self.domain)
        try:
            register = LicenseRegister.from_sequence(facts.get("grants", ()))
        except CommercialIntelligenceError as exc:
            return (
                failed("CMI-LIC-001", self.domain, f"licence facts are not assimilable: {exc}"),
            )
        findings = [
            passed(
                "CMI-LIC-001",
                self.domain,
                f"{len(register.grants)} licence grant(s) assimilated",
                model_counts=register.model_counts(),
            )
        ]
        findings.append(
            passed("CMI-LIC-002", self.domain, "the licence register is populated")
            if register.grants
            else failed(
                "CMI-LIC-002",
                self.domain,
                "no licence grant exists — no right to use can be proven",
            )
        )
        mismatches: list[dict[str, Any]] = []
        evaluated = 0
        for item in _sequence(facts, "entitlement_requests"):
            try:
                request = EntitlementRequest.from_mapping(item)
            except CommercialIntelligenceError as exc:
                mismatches.append({"request": repr(item), "reason": str(exc)})
                continue
            expected = bool(item.get("expect_granted", True)) if isinstance(item, Mapping) else True
            decision = register.evaluate(request)
            evaluated += 1
            if decision.granted is not expected:
                mismatches.append(
                    {
                        "request": request.to_dict(),
                        "expected_granted": expected,
                        "decided_granted": decision.granted,
                        "reasons": list(decision.reasons),
                    }
                )
        findings.append(
            passed(
                "CMI-LIC-003",
                self.domain,
                f"{evaluated} declared entitlement request(s) decided as required",
            )
            if not mismatches
            else failed(
                "CMI-LIC-003",
                self.domain,
                f"{len(mismatches)} entitlement request(s) did not decide as declared",
                mismatches=mismatches,
            )
        )
        return tuple(findings)


@dataclass(frozen=True, slots=True)
class ProductAnalyzer:
    """Product Intelligence: the catalog is well-formed and its transitions are legal."""

    domain: CommercialDomain = CommercialDomain.PRODUCT_INTELLIGENCE

    def analyze(self, target: CommercialTarget) -> tuple[Finding, ...]:
        facts = target.domain_facts(self.domain)
        try:
            catalog = ProductCatalog.from_sequence(facts.get("products", ()))
        except CommercialIntelligenceError as exc:
            return (
                failed("CMI-PRD-001", self.domain, f"product facts are not assimilable: {exc}"),
            )
        findings = [
            passed(
                "CMI-PRD-001",
                self.domain,
                f"{len(catalog.products)} product(s) assimilated with unique identity and SKU",
                state_counts=catalog.state_counts(),
            )
        ]
        findings.append(
            passed(
                "CMI-PRD-002",
                self.domain,
                f"{len(catalog.offerable())} product(s) are offerable",
            )
            if catalog.offerable()
            else failed(
                "CMI-PRD-002",
                self.domain,
                "no product is offerable — nothing may be commercialized",
            )
        )
        illegal: list[dict[str, Any]] = []
        checked = 0
        for item in _sequence(facts, "transitions"):
            if not isinstance(item, Mapping):
                illegal.append({"transition": repr(item), "reason": "not a mapping"})
                continue
            product = catalog.get(str(item.get("product_id") or ""))
            if product is None:
                illegal.append(
                    {
                        "transition": dict(item),
                        "reason": "names a product that is not in the catalog",
                    }
                )
                continue
            try:
                product.transition_to(ProductState.parse(item.get("to")))
                checked += 1
            except CommercialIntelligenceError as exc:
                illegal.append({"transition": dict(item), "reason": str(exc)})
        findings.append(
            passed(
                "CMI-PRD-003",
                self.domain,
                f"{checked} declared lifecycle transition(s) are legal",
            )
            if not illegal
            else failed(
                "CMI-PRD-003",
                self.domain,
                f"{len(illegal)} declared lifecycle transition(s) are not legal",
                illegal=illegal,
            )
        )
        return tuple(findings)


@dataclass(frozen=True, slots=True)
class PortfolioAnalyzer:
    """Portfolio Intelligence: the offer covers the mandate and is not over-concentrated."""

    domain: CommercialDomain = CommercialDomain.PORTFOLIO_INTELLIGENCE

    def analyze(self, target: CommercialTarget) -> tuple[Finding, ...]:
        facts = target.domain_facts(self.domain)
        try:
            portfolio = Portfolio.from_mapping(facts)
        except CommercialIntelligenceError as exc:
            return (
                failed("CMI-PTF-001", self.domain, f"portfolio facts are not assimilable: {exc}"),
            )
        coverage = portfolio.coverage()
        findings = [
            passed(
                "CMI-PTF-001",
                self.domain,
                f"portfolio {portfolio.portfolio_id} assimilated over "
                f"{len(portfolio.catalog.products)} product(s)",
            ),
            (
                passed(
                    "CMI-PTF-002",
                    self.domain,
                    f"the offer covers the mandate ({coverage.coverage_basis_points} bp)",
                    coverage=coverage.to_dict(),
                )
                if coverage.complete
                else failed(
                    "CMI-PTF-002",
                    self.domain,
                    f"{len(coverage.gaps)} mandated capability(ies) are not offered",
                    coverage=coverage.to_dict(),
                )
            ),
        ]
        bound = _bound(facts, "max_concentration_basis_points")
        concentration = portfolio.concentration_basis_points()
        findings.append(
            passed(
                "CMI-PTF-003",
                self.domain,
                f"offer concentration {concentration} bp is within the declared bound {bound} bp",
            )
            if concentration <= bound
            else failed(
                "CMI-PTF-003",
                self.domain,
                f"offer concentration {concentration} bp exceeds the declared bound {bound} bp",
                severity=Severity.ADVISORY,
                concentration_basis_points=concentration,
                max_concentration_basis_points=bound,
            )
        )
        return tuple(findings)


@dataclass(frozen=True, slots=True)
class DocumentationAnalyzer:
    """Business Documentation: every declared documentation set is complete and addressed."""

    domain: CommercialDomain = CommercialDomain.BUSINESS_DOCUMENTATION

    def analyze(self, target: CommercialTarget) -> tuple[Finding, ...]:
        facts = target.domain_facts(self.domain)
        declared = _sequence(facts, "sets")
        if not declared:
            return (
                failed(
                    "CMI-DOC-001",
                    self.domain,
                    "no documentation set is declared — an undocumented offer is unbounded",
                ),
            )
        sets: list[DocumentationSet] = []
        malformed: list[dict[str, Any]] = []
        for item in declared:
            try:
                sets.append(DocumentationSet.from_mapping(item))
            except CommercialIntelligenceError as exc:
                malformed.append({"set": repr(item), "reason": str(exc)})
        findings = [
            passed(
                "CMI-DOC-001",
                self.domain,
                f"{len(sets)} documentation set(s) assimilated",
                subjects=[s.subject_id for s in sets],
            )
            if not malformed
            else failed(
                "CMI-DOC-001",
                self.domain,
                f"{len(malformed)} documentation set(s) are not assimilable",
                malformed=malformed,
            )
        ]
        incomplete = [
            {"subject_id": s.subject_id, "missing": list(s.completeness().missing)}
            for s in sets
            if not s.completeness().complete
        ]
        findings.append(
            passed(
                "CMI-DOC-002",
                self.domain,
                "every documentation set carries every required document kind",
            )
            if not incomplete
            else failed(
                "CMI-DOC-002",
                self.domain,
                f"{len(incomplete)} documentation set(s) are incomplete",
                incomplete=incomplete,
            )
        )
        findings.append(
            passed(
                "CMI-DOC-003",
                self.domain,
                "every documentation set is content-addressed",
                manifests={s.subject_id: s.digest() for s in sets},
            )
            if sets
            else failed(
                "CMI-DOC-003",
                self.domain,
                "no documentation set could be content-addressed",
            )
        )
        return tuple(findings)


def _assemble_declared_package(spec: Mapping[str, Any]) -> CommercialPackage:
    """Assemble one declared commercial package from its fact bundle (raises on defect)."""
    product = Product.from_mapping(spec.get("product"))
    book = PriceBook.from_mapping(spec.get("price_book"))
    lines = [QuoteLineRequest.from_mapping(line) for line in _sequence(spec, "lines")]
    quote = build_quote(book, lines, quote_id=str(spec.get("quote_id") or ""))
    grant = LicenseGrant.from_mapping(spec.get("grant"))
    documentation = DocumentationSet.from_mapping(spec.get("documentation"))
    register = PolicyRegister.from_sequence(spec.get("policies", ()))
    decision = register.decide(PolicyRequest.from_mapping(spec.get("policy_request")))
    approval = None
    if spec.get("approval_chain") is not None:
        chain = ApprovalChain.from_mapping(spec.get("approval_chain"))
        approval = chain.evaluate(parse_records(spec.get("approval_records", ())))
    return assemble_package(
        package_id=str(spec.get("package_id") or ""),
        product=product,
        quote=quote,
        grant=grant,
        documentation=documentation,
        policy_decision=decision,
        approval=approval,
    )


@dataclass(frozen=True, slots=True)
class PackagesAnalyzer:
    """Commercial Packages: every declared package assembles and releases only if governed."""

    domain: CommercialDomain = CommercialDomain.COMMERCIAL_PACKAGES

    def analyze(self, target: CommercialTarget) -> tuple[Finding, ...]:
        facts = target.domain_facts(self.domain)
        declared = _sequence(facts, "packages")
        if not declared:
            return (
                failed(
                    "CMI-PKG-001",
                    self.domain,
                    "no commercial package is declared — there is nothing releasable",
                ),
            )
        assembled: list[CommercialPackage] = []
        malformed: list[dict[str, Any]] = []
        mismatches: list[dict[str, Any]] = []
        for item in declared:
            if not isinstance(item, Mapping):
                malformed.append({"package": repr(item), "reason": "not a mapping"})
                continue
            try:
                package = _assemble_declared_package(item)
            except CommercialIntelligenceError as exc:
                malformed.append({"package_id": item.get("package_id"), "reason": str(exc)})
                continue
            assembled.append(package)
            expected = bool(item.get("expect_releasable", True))
            if package.releasable is not expected:
                mismatches.append(
                    {
                        "package_id": package.package_id,
                        "expected_releasable": expected,
                        "releasable": package.releasable,
                        "reasons": list(package.reasons),
                    }
                )
        findings = [
            passed(
                "CMI-PKG-001",
                self.domain,
                f"{len(assembled)} commercial package(s) assembled",
                seals={p.package_id: p.package_sha256 for p in assembled},
            )
            if not malformed
            else failed(
                "CMI-PKG-001",
                self.domain,
                f"{len(malformed)} declared package(s) could not be assembled",
                malformed=malformed,
            )
        ]
        findings.append(
            passed(
                "CMI-PKG-002",
                self.domain,
                "every package's releasability matches its declaration",
            )
            if not mismatches
            else failed(
                "CMI-PKG-002",
                self.domain,
                f"{len(mismatches)} package(s) did not resolve to the declared releasability",
                mismatches=mismatches,
            )
        )
        ungoverned = [
            p.package_id
            for p in assembled
            if p.releasable
            and not (p.policy_decision.allowed or p.policy_decision.requires_approval)
        ]
        findings.append(
            passed(
                "CMI-PKG-003",
                self.domain,
                "no package is releasable without a governing policy decision",
            )
            if not ungoverned
            else failed(
                "CMI-PKG-003",
                self.domain,
                "package(s) are releasable without a governing policy decision",
                packages=ungoverned,
            )
        )
        return tuple(findings)


@dataclass(frozen=True, slots=True)
class PricingAnalyzer:
    """Pricing Intelligence: quotes compute exactly and the discount authority is enforced."""

    domain: CommercialDomain = CommercialDomain.PRICING_INTELLIGENCE

    def analyze(self, target: CommercialTarget) -> tuple[Finding, ...]:
        facts = target.domain_facts(self.domain)
        try:
            book = PriceBook.from_mapping(facts.get("price_book"))
        except CommercialIntelligenceError as exc:
            return (
                failed("CMI-PRC-001", self.domain, f"pricing facts are not assimilable: {exc}"),
            )
        findings = [
            passed(
                "CMI-PRC-001",
                self.domain,
                f"price book {book.book_id} assimilated in {book.currency} with "
                f"{len(book.prices)} price(s) and {len(book.discounts)} discount(s)",
                max_discount_basis_points=book.max_discount_basis_points,
            )
        ]
        defects: list[dict[str, Any]] = []
        priced = 0
        for item in _sequence(facts, "quotes"):
            if not isinstance(item, Mapping):
                defects.append({"quote": repr(item), "reason": "not a mapping"})
                continue
            try:
                lines = [QuoteLineRequest.from_mapping(line) for line in _sequence(item, "lines")]
                quote = build_quote(book, lines, quote_id=str(item.get("quote_id") or ""))
            except CommercialIntelligenceError as exc:
                defects.append({"quote_id": item.get("quote_id"), "reason": str(exc)})
                continue
            priced += 1
            expected = item.get("expect_net_minor_units")
            if expected is not None and quote.net_total.minor_units != expected:
                defects.append(
                    {
                        "quote_id": quote.quote_id,
                        "expected_net_minor_units": expected,
                        "computed_net_minor_units": quote.net_total.minor_units,
                    }
                )
        findings.append(
            passed("CMI-PRC-002", self.domain, f"{priced} declared quote(s) priced exactly")
            if not defects
            else failed(
                "CMI-PRC-002",
                self.domain,
                f"{len(defects)} declared quote(s) did not price as required",
                defects=defects,
            )
        )
        admitted: list[dict[str, Any]] = []
        refusals = 0
        for item in _sequence(facts, "refusals"):
            if not isinstance(item, Mapping):
                continue
            try:
                lines = [QuoteLineRequest.from_mapping(line) for line in _sequence(item, "lines")]
                build_quote(book, lines, quote_id=str(item.get("quote_id") or "refusal"))
            except CommercialIntelligenceError:
                refusals += 1
                continue
            admitted.append({"quote_id": item.get("quote_id")})
        findings.append(
            passed(
                "CMI-PRC-003",
                self.domain,
                f"{refusals} unauthorised pricing request(s) were refused",
            )
            if not admitted
            else failed(
                "CMI-PRC-003",
                self.domain,
                f"{len(admitted)} pricing request(s) that must be refused were admitted",
                admitted=admitted,
            )
        )
        return tuple(findings)


@dataclass(frozen=True, slots=True)
class InvestmentAnalyzer:
    """Investment Intelligence: every case computes, recovers and returns as declared."""

    domain: CommercialDomain = CommercialDomain.INVESTMENT_INTELLIGENCE

    def analyze(self, target: CommercialTarget) -> tuple[Finding, ...]:
        facts = target.domain_facts(self.domain)
        declared = _sequence(facts, "cases")
        if not declared:
            return (
                failed(
                    "CMI-INV-001",
                    self.domain,
                    "no investment case is declared — the commercial position is unjustified",
                ),
            )
        cases: list[InvestmentCase] = []
        malformed: list[dict[str, Any]] = []
        unrecovered: list[str] = []
        below: list[dict[str, Any]] = []
        for item in declared:
            if not isinstance(item, Mapping):
                malformed.append({"case": repr(item), "reason": "not a mapping"})
                continue
            try:
                case = InvestmentCase.from_mapping(item)
            except CommercialIntelligenceError as exc:
                malformed.append({"case_id": item.get("case_id"), "reason": str(exc)})
                continue
            cases.append(case)
            metrics = case.metrics()
            if bool(item.get("require_recovered", True)) and not metrics.recovered:
                unrecovered.append(case.case_id)
            floor = item.get("min_return_basis_points")
            if (
                isinstance(floor, int)
                and not isinstance(floor, bool)
                and metrics.return_basis_points < floor
            ):
                below.append(
                    {
                        "case_id": case.case_id,
                        "min_return_basis_points": floor,
                        "return_basis_points": metrics.return_basis_points,
                    }
                )
        findings = [
            passed(
                "CMI-INV-001",
                self.domain,
                f"{len(cases)} investment case(s) assimilated and computed",
                metrics={c.case_id: c.metrics().to_dict() for c in cases},
            )
            if not malformed
            else failed(
                "CMI-INV-001",
                self.domain,
                f"{len(malformed)} investment case(s) are not assimilable",
                malformed=malformed,
            )
        ]
        findings.append(
            passed(
                "CMI-INV-002",
                self.domain,
                "every case requiring recovery recovers within its horizon",
            )
            if not unrecovered
            else failed(
                "CMI-INV-002",
                self.domain,
                f"{len(unrecovered)} case(s) do not recover within the declared horizon",
                cases=unrecovered,
            )
        )
        findings.append(
            passed("CMI-INV-003", self.domain, "every case meets its declared return floor")
            if not below
            else failed(
                "CMI-INV-003",
                self.domain,
                f"{len(below)} case(s) fall below the declared return floor",
                severity=Severity.ADVISORY,
                cases=below,
            )
        )
        return tuple(findings)


@dataclass(frozen=True, slots=True)
class CustomerAnalyzer:
    """Customer Intelligence: the base is sound against the licence register and diversified."""

    domain: CommercialDomain = CommercialDomain.CUSTOMER_INTELLIGENCE

    def analyze(self, target: CommercialTarget) -> tuple[Finding, ...]:
        facts = target.domain_facts(self.domain)
        try:
            base = CustomerBase.from_mapping(facts)
            register = LicenseRegister.from_sequence(facts.get("grants", ()))
        except CommercialIntelligenceError as exc:
            return (
                failed("CMI-CUS-001", self.domain, f"customer facts are not assimilable: {exc}"),
            )
        findings = [
            passed(
                "CMI-CUS-001",
                self.domain,
                f"{len(base.accounts)} customer account(s) assimilated in {base.currency}",
                segment_counts=base.segment_counts(),
                contracted_total=base.contracted_total().to_dict(),
            )
        ]
        unsound = [v for v in base.integrity(register) if not v.sound]
        findings.append(
            passed(
                "CMI-CUS-002",
                self.domain,
                "every account's entitlements resolve against the licence register",
            )
            if not unsound
            else failed(
                "CMI-CUS-002",
                self.domain,
                f"{len(unsound)} account(s) are unsound against the licence register",
                unsound=[v.to_dict() for v in unsound],
            )
        )
        bound = _bound(facts, "max_concentration_basis_points")
        concentration = base.concentration_basis_points()
        findings.append(
            passed(
                "CMI-CUS-003",
                self.domain,
                f"revenue concentration {concentration} bp is within the bound {bound} bp",
            )
            if concentration <= bound
            else failed(
                "CMI-CUS-003",
                self.domain,
                f"revenue concentration {concentration} bp exceeds the bound {bound} bp",
                severity=Severity.ADVISORY,
                concentration_basis_points=concentration,
                max_concentration_basis_points=bound,
            )
        )
        return tuple(findings)


@dataclass(frozen=True, slots=True)
class PolicyGovernanceAnalyzer:
    """Policy Governance: declared actions decide as required and silence always refuses."""

    domain: CommercialDomain = CommercialDomain.POLICY_GOVERNANCE

    def analyze(self, target: CommercialTarget) -> tuple[Finding, ...]:
        facts = target.domain_facts(self.domain)
        try:
            register = PolicyRegister.from_sequence(facts.get("policies", ()))
        except CommercialIntelligenceError as exc:
            return (failed("CMI-POL-001", self.domain, f"policy facts are not assimilable: {exc}"),)
        if not register.policies:
            return (
                failed(
                    "CMI-POL-001",
                    self.domain,
                    "no commercial policy is declared — every commercial action would be refused",
                ),
            )
        findings = [
            passed(
                "CMI-POL-001",
                self.domain,
                f"{len(register.policies)} commercial policy(ies) assimilated",
                domains=sorted({p.domain.value for p in register.policies}),
            )
        ]
        mismatches: list[dict[str, Any]] = []
        decided = 0
        for item in _sequence(facts, "requests"):
            if not isinstance(item, Mapping):
                mismatches.append({"request": repr(item), "reason": "not a mapping"})
                continue
            try:
                request = PolicyRequest.from_mapping(item)
                expected = PolicyEffect.parse(item.get("expect_effect"))
            except CommercialIntelligenceError as exc:
                mismatches.append({"request": dict(item), "reason": str(exc)})
                continue
            decision = register.decide(request)
            decided += 1
            if decision.effect is not expected:
                mismatches.append(
                    {
                        "request": request.to_dict(),
                        "expected_effect": expected.value,
                        "decided_effect": decision.effect.value,
                        "reasons": list(decision.reasons),
                    }
                )
        findings.append(
            passed(
                "CMI-POL-002",
                self.domain,
                f"{decided} declared commercial action(s) decided as required",
            )
            if not mismatches
            else failed(
                "CMI-POL-002",
                self.domain,
                f"{len(mismatches)} commercial action(s) did not decide as declared",
                mismatches=mismatches,
            )
        )
        probe = register.decide(
            PolicyRequest(
                domain=register.policies[0].domain,
                action=UNGOVERNED_PROBE_ACTION,
                magnitude=0,
            )
        )
        findings.append(
            passed(
                "CMI-POL-003",
                self.domain,
                "an action no policy governs is refused (fail-closed governance proven)",
            )
            if probe.denied
            else failed(
                "CMI-POL-003",
                self.domain,
                f"an ungoverned action resolved to {probe.effect.value} — governance is not "
                "fail-closed",
            )
        )
        return tuple(findings)


@dataclass(frozen=True, slots=True)
class ApprovalAnalyzer:
    """Approval Intelligence: chains evaluate as declared and irregularities never count."""

    domain: CommercialDomain = CommercialDomain.APPROVAL_INTELLIGENCE

    def analyze(self, target: CommercialTarget) -> tuple[Finding, ...]:
        facts = target.domain_facts(self.domain)
        declared = _sequence(facts, "chains")
        if not declared:
            return (
                failed(
                    "CMI-APR-001",
                    self.domain,
                    "no approval chain is declared — policy-required approval cannot be discharged",
                ),
            )
        malformed: list[dict[str, Any]] = []
        mismatches: list[dict[str, Any]] = []
        irregular: list[dict[str, Any]] = []
        evaluated = 0
        for item in declared:
            if not isinstance(item, Mapping):
                malformed.append({"chain": repr(item), "reason": "not a mapping"})
                continue
            try:
                chain = ApprovalChain.from_mapping(item)
                outcome = chain.evaluate(parse_records(item.get("records", ())))
            except CommercialIntelligenceError as exc:
                malformed.append({"chain_id": item.get("chain_id"), "reason": str(exc)})
                continue
            evaluated += 1
            expected = bool(item.get("expect_satisfied", True))
            if outcome.satisfied is not expected:
                mismatches.append(
                    {
                        "chain_id": outcome.chain_id,
                        "expected_satisfied": expected,
                        "satisfied": outcome.satisfied,
                        "pending_stages": list(outcome.pending_stages),
                    }
                )
            allowed = item.get("expect_irregularities", 0)
            allowed = allowed if isinstance(allowed, int) and not isinstance(allowed, bool) else 0
            if len(outcome.irregularities) != allowed:
                irregular.append(
                    {
                        "chain_id": outcome.chain_id,
                        "expected_irregularities": allowed,
                        "irregularities": list(outcome.irregularities),
                    }
                )
        findings = [
            passed("CMI-APR-001", self.domain, f"{evaluated} approval chain(s) evaluated")
            if not malformed
            else failed(
                "CMI-APR-001",
                self.domain,
                f"{len(malformed)} approval chain(s) are not assimilable",
                malformed=malformed,
            ),
            passed("CMI-APR-002", self.domain, "every chain resolved as declared")
            if not mismatches
            else failed(
                "CMI-APR-002",
                self.domain,
                f"{len(mismatches)} approval chain(s) did not resolve as declared",
                mismatches=mismatches,
            ),
            passed("CMI-APR-003", self.domain, "every chain's irregularity count is as declared")
            if not irregular
            else failed(
                "CMI-APR-003",
                self.domain,
                f"{len(irregular)} approval chain(s) carry undeclared irregularities",
                irregular=irregular,
            ),
        ]
        return tuple(findings)


@dataclass(frozen=True, slots=True)
class BusinessEvidenceAnalyzer:
    """Business Evidence: every commercial claim is content-addressed and non-duplicated."""

    domain: CommercialDomain = CommercialDomain.BUSINESS_EVIDENCE

    def analyze(self, target: CommercialTarget) -> tuple[Finding, ...]:
        facts = target.domain_facts(self.domain)
        try:
            index = EvidenceIndex.from_sequence(facts.get("entries", ()))
        except CommercialIntelligenceError as exc:
            return (
                failed("CMI-EVD-001", self.domain, f"evidence facts are not assimilable: {exc}"),
            )
        findings = [
            passed(
                "CMI-EVD-001",
                self.domain,
                f"{len(index.entries)} business-evidence entry(ies) assimilated and addressed",
                index_sha256=index.digest(),
                subjects=list(index.subjects()),
            )
            if index.entries
            else failed(
                "CMI-EVD-001",
                self.domain,
                "no business evidence is declared — no commercial claim is auditable",
            )
        ]
        collisions = index.collisions()
        findings.append(
            passed("CMI-EVD-002", self.domain, "no business-evidence entry is duplicated")
            if not collisions
            else failed(
                "CMI-EVD-002",
                self.domain,
                f"{len(collisions)} business-evidence entry(ies) are duplicated",
                collisions=list(collisions),
            )
        )
        required = sorted({str(s) for s in _sequence(facts, "required_subjects")})
        missing = [subject for subject in required if not index.for_subject(subject)]
        findings.append(
            passed(
                "CMI-EVD-003",
                self.domain,
                f"every one of {len(required)} required subject(s) carries evidence",
            )
            if not missing
            else failed(
                "CMI-EVD-003",
                self.domain,
                f"{len(missing)} required subject(s) carry no business evidence",
                missing=missing,
            )
        )
        return tuple(findings)


@dataclass(frozen=True, slots=True)
class CommercialValidationAnalyzer:
    """Commercial Validation: the commercial surface is fully declared and stably identified."""

    domain: CommercialDomain = CommercialDomain.COMMERCIAL_VALIDATION

    def analyze(self, target: CommercialTarget) -> tuple[Finding, ...]:
        facts = target.domain_facts(self.domain)
        required_raw = _sequence(facts, "required_domains")
        try:
            required = (
                tuple(
                    sorted((CommercialDomain.parse(d) for d in required_raw), key=lambda x: x.order)
                )
                if required_raw
                else tuple(sorted(CommercialDomain, key=lambda x: x.order))
            )
        except CommercialIntelligenceError as exc:
            return (
                failed(
                    "CMI-VAL-001",
                    self.domain,
                    f"the declared required-domain set is not assimilable: {exc}",
                ),
            )
        declared = set(target.declared_domains())
        missing = [d.value for d in required if d not in declared]
        findings = [
            passed(
                "CMI-VAL-001",
                self.domain,
                f"every one of {len(required)} mandated domain(s) declares commercial facts",
            )
            if not missing
            else failed(
                "CMI-VAL-001",
                self.domain,
                f"{len(missing)} mandated domain(s) declare no commercial facts",
                missing=missing,
            )
        ]
        empty = [
            domain.value for domain in target.declared_domains() if not target.domain_facts(domain)
        ]
        findings.append(
            passed("CMI-VAL-002", self.domain, "no declared domain carries an empty fact set")
            if not empty
            else failed(
                "CMI-VAL-002",
                self.domain,
                f"{len(empty)} declared domain(s) carry an empty fact set — an empty claim "
                "cannot be validated",
                domains=empty,
            )
        )
        first_digest = target.digest()
        second_digest = target.digest()
        findings.append(
            passed(
                "CMI-VAL-003",
                self.domain,
                "the commercial surface is stably content-addressed",
                target_digest=first_digest,
            )
            if first_digest == second_digest
            else failed(
                "CMI-VAL-003", self.domain, "the commercial surface is not stably addressed"
            )
        )
        return tuple(findings)


@dataclass(frozen=True, slots=True)
class CommercialCertificationAnalyzer:
    """Commercial Certification: the certification subject, authority and scope are lawful."""

    domain: CommercialDomain = CommercialDomain.COMMERCIAL_CERTIFICATION

    def analyze(self, target: CommercialTarget) -> tuple[Finding, ...]:
        facts = target.domain_facts(self.domain)
        subject = str(facts.get("subject_id") or "")
        findings = [
            passed("CMI-CRT-001", self.domain, f"the certification subject is {subject}")
            if subject
            else failed(
                "CMI-CRT-001",
                self.domain,
                "no certification subject is declared — a certificate must name its subject",
            )
        ]
        authority = str(facts.get("authority") or "")
        findings.append(
            passed(
                "CMI-CRT-002",
                self.domain,
                f"the certification claims only {COMMERCIAL_AUTHORITY} authority",
            )
            if authority == COMMERCIAL_AUTHORITY
            else failed(
                "CMI-CRT-002",
                self.domain,
                f"the declared authority {authority!r} is not {COMMERCIAL_AUTHORITY} — a "
                "commercial certificate may not claim constitutional authority",
            )
        )
        exemptions = [str(item) for item in _sequence(facts, "exemptions")]
        required = str(facts.get("required_determination") or Determination.CERTIFIED.value)
        valid = required in {d.value for d in Determination}
        if exemptions:
            findings.append(
                failed(
                    "CMI-CRT-003",
                    self.domain,
                    f"{len(exemptions)} domain(s) claim exemption from commercial certification",
                    exemptions=exemptions,
                )
            )
        elif not valid:
            findings.append(
                failed(
                    "CMI-CRT-003",
                    self.domain,
                    f"the required determination {required!r} is not in the closed set",
                    supported=[d.value for d in Determination],
                )
            )
        else:
            findings.append(
                passed(
                    "CMI-CRT-003",
                    self.domain,
                    f"no domain is exempt and the required determination is {required}",
                )
            )
        return tuple(findings)


def default_analyzers() -> tuple[DomainAnalyzer, ...]:
    """The built-in suite: exactly one analyzer per mandated domain, canonical order."""
    return (
        MarketplaceAnalyzer(),
        LicensingAnalyzer(),
        ProductAnalyzer(),
        PortfolioAnalyzer(),
        DocumentationAnalyzer(),
        PackagesAnalyzer(),
        PricingAnalyzer(),
        InvestmentAnalyzer(),
        CustomerAnalyzer(),
        PolicyGovernanceAnalyzer(),
        ApprovalAnalyzer(),
        BusinessEvidenceAnalyzer(),
        CommercialValidationAnalyzer(),
        CommercialCertificationAnalyzer(),
    )


def select_analyzers(
    domains: Sequence[CommercialDomain] | None = None,
    analyzers: Sequence[DomainAnalyzer] | None = None,
) -> tuple[DomainAnalyzer, ...]:
    """Scope an analyzer suite to ``domains``, defaulting to the full built-in suite.

    A declared domain with no analyzer is an authoring fault, not a silent omission: the
    scope would claim coverage the suite cannot deliver.
    """
    suite = tuple(analyzers) if analyzers is not None else default_analyzers()
    if not suite:
        raise AnalyzerDefinitionError("a commercial-intelligence suite requires an analyzer")
    if domains is None:
        return suite
    available = {analyzer.domain for analyzer in suite}
    unmatched = [d.value for d in domains if d not in available]
    if unmatched:
        raise AnalyzerDefinitionError(
            "no analyzer covers the declared commercial domain(s)",
            domains=sorted(unmatched),
        )
    wanted = set(domains)
    return tuple(analyzer for analyzer in suite if analyzer.domain in wanted)


@dataclass(frozen=True, slots=True)
class CommercialIntelligenceEngine:
    """Runs an analyzer suite over a commercial target and aggregates it fail-closed."""

    analyzers: tuple[DomainAnalyzer, ...] = field(default_factory=default_analyzers)

    def __post_init__(self) -> None:
        if not self.analyzers:
            raise AnalyzerDefinitionError("a commercial-intelligence suite requires an analyzer")
        seen: set[CommercialDomain] = set()
        for analyzer in self.analyzers:
            domain = getattr(analyzer, "domain", None)
            if not isinstance(domain, CommercialDomain):
                raise AnalyzerDefinitionError(
                    "every analyzer must declare the commercial domain it analyzes",
                    analyzer=type(analyzer).__name__,
                )
            if not callable(getattr(analyzer, "analyze", None)):
                raise AnalyzerDefinitionError(
                    "every analyzer must expose analyze(target)",
                    analyzer=type(analyzer).__name__,
                )
            if domain in seen:
                raise AnalyzerDefinitionError(
                    "exactly one analyzer per domain — a second would make the verdict "
                    "order-dependent",
                    domain=domain.value,
                )
            seen.add(domain)

    def domains(self) -> tuple[CommercialDomain, ...]:
        return tuple(sorted((a.domain for a in self.analyzers), key=lambda d: d.order))

    def ordered_analyzers(self) -> tuple[DomainAnalyzer, ...]:
        return tuple(sorted(self.analyzers, key=lambda a: a.domain.order))

    def analyze(self, target: CommercialTarget) -> CommercialIntelligenceReport:
        """Analyze ``target`` and aggregate the ordered domain reports into one report."""
        reports = tuple(
            DomainReport.create(analyzer.domain, tuple(analyzer.analyze(target)))
            for analyzer in self.ordered_analyzers()
        )
        return CommercialIntelligenceReport.create(
            target_id=target.target_id,
            target_digest=target.digest(),
            domain_reports=reports,
        )


__all__ = [
    "UNGOVERNED_PROBE_ACTION",
    "DomainAnalyzer",
    "MarketplaceAnalyzer",
    "LicensingAnalyzer",
    "ProductAnalyzer",
    "PortfolioAnalyzer",
    "DocumentationAnalyzer",
    "PackagesAnalyzer",
    "PricingAnalyzer",
    "InvestmentAnalyzer",
    "CustomerAnalyzer",
    "PolicyGovernanceAnalyzer",
    "ApprovalAnalyzer",
    "BusinessEvidenceAnalyzer",
    "CommercialValidationAnalyzer",
    "CommercialCertificationAnalyzer",
    "default_analyzers",
    "select_analyzers",
    "CommercialIntelligenceEngine",
]
