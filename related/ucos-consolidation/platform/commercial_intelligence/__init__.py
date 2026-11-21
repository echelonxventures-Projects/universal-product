"""UCOS-EPIC-014 — Commercial Intelligence (Terminal T5).

The platform-layer **commercial** intelligence: a deterministic, fail-closed,
evidence-producing engine that reasons across the fourteen mandated commercial domains —
**marketplace, licensing, product, portfolio, business documentation, commercial packages,
pricing, investment, customer, policy governance, approval, business evidence, commercial
validation and commercial certification** — from a single, configuration-driven command.

The engine is:

    * **universal** — one normalized :class:`CommercialTarget` and one open analyzer suite
      reason over any commercial surface; the fourteen domains are covered by the built-in
      :func:`default_analyzers`, and callers may supply their own analyzers;
    * **exact** — every monetary amount is an integer count of minor units in one currency
      (:class:`Money`) and every proportion is expressed in basis points, so no binary
      float ever touches a price, discount, quote, contract value or investment flow;
    * **governed** — a commercial action that no policy governs is DENIED
      (:data:`~platform.commercial_intelligence.policy.UNGOVERNED_EFFECT`), a package is
      releasable only when policy permits it and any policy-required approval chain is
      satisfied, and self-approval is structurally impossible;
    * **fail-closed** — an analyzer that cannot prove its invariant (absent or malformed
      commercial facts) records a FAIL, never a pass; the verdict is FAIL iff any
      *blocking* check failed;
    * **evidence-required** — every run yields a content-addressed
      :class:`CommercialIntelligenceReport`, a :class:`CommercialDashboard`, a derived
      :class:`CommercialCertificate` and a :class:`CommercialEvidence` record; and
    * **deterministic** — an identical commercial surface analyzed by an identical suite
      yields a byte-identical report, certificate and evidence hash (IMP-007 §5); no
      wall-clock, locale or ambient state enters any identity.

It is strictly additive and record-only over the certified EC-1 engine: it consumes the
EC-1 foundation (disclosure) and the platform foundation (content hashing) through their
published surfaces, invents no verdict (TP-01), mutates no target, and never writes to the
certified corpus (DP-03). It asserts ``ENGINEERING-EXECUTION-ONLY`` authority and carries
the EC-1 provisional-state disclosure (DE-05 / IP-01) — a commercial determination
ratifies nothing constitutionally.

Governance route: the programme ``UCMI-000001`` (directive Ω∞-001C) binds this package as
the executable expression of the Commercial Certification Gate; see
``00-MASTER/UCMI-000001/``.
"""

from __future__ import annotations

from platform.commercial_intelligence.approval import (
    ApprovalChain,
    ApprovalDecision,
    ApprovalOutcome,
    ApprovalRecord,
    ApprovalStage,
    StageOutcome,
    parse_records,
)
from platform.commercial_intelligence.certification import (
    CERTIFICATE_FORMAT,
    CommercialCertificate,
    Determination,
    certify,
)
from platform.commercial_intelligence.config import (
    CommercialConfig,
    load_config,
    parse_config,
)
from platform.commercial_intelligence.contracts import (
    BASIS_POINTS_SCALE,
    COMMERCIAL_AUTHORITY,
    COMMERCIAL_CONTRACT_VERSION,
    COMMERCIAL_DASHBOARD_FORMAT,
    COMMERCIAL_REPORT_FORMAT,
    CommercialDashboard,
    CommercialDomain,
    CommercialIntelligenceReport,
    CommercialTarget,
    DomainKind,
    DomainReport,
    Finding,
    FindingStatus,
    Money,
    Severity,
    Verdict,
    domains_of_kind,
    sum_money,
)
from platform.commercial_intelligence.customer import (
    ENTITLED_SEGMENTS,
    AccountIntegrity,
    CustomerAccount,
    CustomerBase,
    CustomerSegment,
)
from platform.commercial_intelligence.documentation import (
    REQUIRED_DOCUMENT_KINDS,
    BusinessDocument,
    DocumentationCompleteness,
    DocumentationSet,
    DocumentKind,
)
from platform.commercial_intelligence.errors import (
    AnalyzerDefinitionError,
    ApprovalError,
    CommercialConfigError,
    CommercialEngineError,
    CommercialIntelligenceError,
    CommercialTargetError,
    CustomerError,
    DocumentationError,
    InvestmentError,
    LicensingError,
    MarketplaceError,
    MoneyError,
    PackageError,
    PolicyError,
    PortfolioError,
    PricingError,
    ProductError,
)
from platform.commercial_intelligence.evidence import (
    EVIDENCE_FORMAT,
    EVIDENCE_INDEX_FORMAT,
    CommercialEvidence,
    EvidenceEntry,
    EvidenceIndex,
    build_commercial_evidence,
)
from platform.commercial_intelligence.investment import InvestmentCase, InvestmentMetrics
from platform.commercial_intelligence.licensing import (
    TERMED_MODELS,
    EntitlementDecision,
    EntitlementRequest,
    LicenseGrant,
    LicenseModel,
    LicenseRegister,
)
from platform.commercial_intelligence.marketplace import (
    LISTING_TRANSITIONS,
    VISIBLE_STATES,
    Listing,
    ListingIntegrity,
    ListingState,
    MarketplaceRegistry,
)
from platform.commercial_intelligence.packages import CommercialPackage, assemble_package
from platform.commercial_intelligence.policy import (
    UNGOVERNED_EFFECT,
    CommercialPolicy,
    PolicyDecision,
    PolicyEffect,
    PolicyRegister,
    PolicyRequest,
)
from platform.commercial_intelligence.portfolio import Portfolio, PortfolioCoverage
from platform.commercial_intelligence.pricing import (
    DiscountRule,
    PriceBook,
    Quote,
    QuoteLine,
    QuoteLineRequest,
    build_quote,
    price_line,
)
from platform.commercial_intelligence.product import (
    OFFERABLE_STATES,
    PRODUCT_TRANSITIONS,
    Product,
    ProductCatalog,
    ProductState,
)
from platform.commercial_intelligence.service import (
    CommercialAssessment,
    CommercialIntelligenceService,
    build_commercial_service,
)
from platform.commercial_intelligence.validation import (
    UNGOVERNED_PROBE_ACTION,
    ApprovalAnalyzer,
    BusinessEvidenceAnalyzer,
    CommercialCertificationAnalyzer,
    CommercialIntelligenceEngine,
    CommercialValidationAnalyzer,
    CustomerAnalyzer,
    DocumentationAnalyzer,
    DomainAnalyzer,
    InvestmentAnalyzer,
    LicensingAnalyzer,
    MarketplaceAnalyzer,
    PackagesAnalyzer,
    PolicyGovernanceAnalyzer,
    PortfolioAnalyzer,
    PricingAnalyzer,
    ProductAnalyzer,
    default_analyzers,
    select_analyzers,
)

__all__ = [
    # contracts
    "COMMERCIAL_CONTRACT_VERSION",
    "COMMERCIAL_REPORT_FORMAT",
    "COMMERCIAL_DASHBOARD_FORMAT",
    "COMMERCIAL_AUTHORITY",
    "BASIS_POINTS_SCALE",
    "DomainKind",
    "CommercialDomain",
    "domains_of_kind",
    "Severity",
    "FindingStatus",
    "Verdict",
    "Money",
    "sum_money",
    "CommercialTarget",
    "Finding",
    "DomainReport",
    "CommercialIntelligenceReport",
    "CommercialDashboard",
    # product / marketplace / portfolio
    "ProductState",
    "PRODUCT_TRANSITIONS",
    "OFFERABLE_STATES",
    "Product",
    "ProductCatalog",
    "ListingState",
    "LISTING_TRANSITIONS",
    "VISIBLE_STATES",
    "Listing",
    "ListingIntegrity",
    "MarketplaceRegistry",
    "Portfolio",
    "PortfolioCoverage",
    # licensing / pricing / investment / customer
    "LicenseModel",
    "TERMED_MODELS",
    "LicenseGrant",
    "EntitlementRequest",
    "EntitlementDecision",
    "LicenseRegister",
    "DiscountRule",
    "PriceBook",
    "QuoteLineRequest",
    "QuoteLine",
    "Quote",
    "price_line",
    "build_quote",
    "InvestmentCase",
    "InvestmentMetrics",
    "CustomerSegment",
    "ENTITLED_SEGMENTS",
    "CustomerAccount",
    "AccountIntegrity",
    "CustomerBase",
    # governance
    "PolicyEffect",
    "UNGOVERNED_EFFECT",
    "CommercialPolicy",
    "PolicyRequest",
    "PolicyDecision",
    "PolicyRegister",
    "ApprovalDecision",
    "ApprovalStage",
    "ApprovalRecord",
    "StageOutcome",
    "ApprovalOutcome",
    "ApprovalChain",
    "parse_records",
    "DocumentKind",
    "REQUIRED_DOCUMENT_KINDS",
    "BusinessDocument",
    "DocumentationCompleteness",
    "DocumentationSet",
    # packages
    "CommercialPackage",
    "assemble_package",
    # assurance
    "CERTIFICATE_FORMAT",
    "Determination",
    "CommercialCertificate",
    "certify",
    "EVIDENCE_FORMAT",
    "EVIDENCE_INDEX_FORMAT",
    "EvidenceEntry",
    "EvidenceIndex",
    "CommercialEvidence",
    "build_commercial_evidence",
    # validation engine
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
    # config / service
    "CommercialConfig",
    "parse_config",
    "load_config",
    "CommercialAssessment",
    "CommercialIntelligenceService",
    "build_commercial_service",
    # errors
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
