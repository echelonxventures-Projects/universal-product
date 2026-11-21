"""UCOS-EPIC-014 — Commercial Intelligence error taxonomy (Terminal T5).

Commercial Intelligence reasons over the fourteen commercial domains — marketplace,
licensing, product, portfolio, business documentation, commercial packages, pricing,
investment, customer, policy governance, approval, business evidence, commercial
validation and commercial certification — and must never *invent* a commercial fact. It
reuses the EC-1 / Platform Foundation error discipline additively: every error is rooted
in :class:`~platform.foundation.errors.PlatformError` (itself rooted in the certified
EC-1 :class:`~engine.foundation.obs.errors.FoundationError`), carries a stable,
category-prefixed ``code`` (``EC2-CMI-*``) and structured, non-secret ``context`` so a
commercial failure is auditable (PL-02, IP-12) and machine-consumable.

Fail-closed discipline: an analyzer that cannot *prove* a commercial invariant holds —
because the declared commercial fact is absent or malformed — records a **FAIL** finding,
never a pass and never a swallowed exception. An exception is raised **only** for a
malformed *authoring* input (a programming or declaration fault: an unknown domain, a
mixed-currency arithmetic attempt, an unreadable configuration), never for a legitimate
fail-closed commercial verdict, which is always reported as data.
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class CommercialIntelligenceError(PlatformError):
    """Base class for all Commercial Intelligence errors (UCOS-EPIC-014)."""

    code = "EC2-CMI-000"


class CommercialConfigError(CommercialIntelligenceError):
    """The commercial-intelligence configuration is missing, unreadable, or malformed."""

    code = "EC2-CMI-CONFIG-001"


class CommercialTargetError(CommercialIntelligenceError):
    """A commercial target could not be assimilated from the supplied facts."""

    code = "EC2-CMI-TARGET-001"


class MoneyError(CommercialIntelligenceError):
    """A monetary amount is malformed, or two currencies were combined."""

    code = "EC2-CMI-MONEY-001"


class MarketplaceError(CommercialIntelligenceError):
    """A marketplace listing or listing-lifecycle transition is invalid."""

    code = "EC2-CMI-MARKET-001"


class LicensingError(CommercialIntelligenceError):
    """A licence grant, term or entitlement is malformed."""

    code = "EC2-CMI-LICENCE-001"


class ProductError(CommercialIntelligenceError):
    """A product, product version or lifecycle transition is invalid."""

    code = "EC2-CMI-PRODUCT-001"


class PortfolioError(CommercialIntelligenceError):
    """A portfolio could not be composed from the supplied products."""

    code = "EC2-CMI-PORTFOLIO-001"


class PricingError(CommercialIntelligenceError):
    """A price book, price rule, discount or quote request is malformed."""

    code = "EC2-CMI-PRICING-001"


class InvestmentError(CommercialIntelligenceError):
    """An investment case is malformed (no horizon, or a mixed-currency flow)."""

    code = "EC2-CMI-INVEST-001"


class CustomerError(CommercialIntelligenceError):
    """A customer account or customer entitlement is malformed."""

    code = "EC2-CMI-CUSTOMER-001"


class PolicyError(CommercialIntelligenceError):
    """A commercial policy or policy request is malformed."""

    code = "EC2-CMI-POLICY-001"


class ApprovalError(CommercialIntelligenceError):
    """An approval chain, stage or decision record is malformed."""

    code = "EC2-CMI-APPROVAL-001"


class DocumentationError(CommercialIntelligenceError):
    """A business document or documentation set is malformed."""

    code = "EC2-CMI-DOC-001"


class PackageError(CommercialIntelligenceError):
    """A commercial package could not be assembled from the supplied constituents."""

    code = "EC2-CMI-PACKAGE-001"


class AnalyzerDefinitionError(CommercialIntelligenceError):
    """An analyzer (or analyzer set) is malformed or names an unknown domain."""

    code = "EC2-CMI-ANALYZER-001"


class CommercialEngineError(CommercialIntelligenceError):
    """The commercial-intelligence engine/service could not be composed or run."""

    code = "EC2-CMI-ENGINE-001"


__all__ = [
    "CommercialIntelligenceError",
    "CommercialConfigError",
    "CommercialTargetError",
    "MoneyError",
    "MarketplaceError",
    "LicensingError",
    "ProductError",
    "PortfolioError",
    "PricingError",
    "InvestmentError",
    "CustomerError",
    "PolicyError",
    "ApprovalError",
    "DocumentationError",
    "PackageError",
    "AnalyzerDefinitionError",
    "CommercialEngineError",
]
