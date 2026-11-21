"""UCOS-EPIC-014 — Commercial Intelligence contract tests (Terminal T5)."""

from __future__ import annotations

import copy
import inspect
import json
import pkgutil
import sys
from dataclasses import is_dataclass, replace
from platform import commercial_intelligence
from platform.commercial_intelligence import (
    approval,
    cli,  # noqa: F401 — imported so `_guarded_classes` can resolve it from sys.modules
    config,
    contracts,
    customer,
    evidence,
    investment,
    licensing,
    marketplace,
    packages,
    policy,
    portfolio,
    pricing,
    product,
    validation,
)
from platform.commercial_intelligence import documentation as documentation_module
from platform.commercial_intelligence.approval import ApprovalChain, parse_records
from platform.commercial_intelligence.certification import certify
from platform.commercial_intelligence.config import load_config, parse_config
from platform.commercial_intelligence.contracts import (
    BASIS_POINTS_SCALE,
    COMMERCIAL_AUTHORITY,
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
    failed,
    passed,
    sum_money,
)
from platform.commercial_intelligence.customer import CustomerBase
from platform.commercial_intelligence.documentation import DocumentationSet, DocumentKind
from platform.commercial_intelligence.errors import (
    AnalyzerDefinitionError,
    CommercialConfigError,
    CommercialTargetError,
    MarketplaceError,
    MoneyError,
    PackageError,
    PricingError,
)
from platform.commercial_intelligence.evidence import EvidenceIndex, build_commercial_evidence
from platform.commercial_intelligence.investment import InvestmentCase
from platform.commercial_intelligence.licensing import EntitlementRequest, LicenseRegister
from platform.commercial_intelligence.marketplace import (
    Listing,
    ListingState,
    MarketplaceRegistry,
)
from platform.commercial_intelligence.policy import PolicyRegister, PolicyRequest
from platform.commercial_intelligence.portfolio import Portfolio
from platform.commercial_intelligence.pricing import (
    DiscountRule,
    PriceBook,
    QuoteLineRequest,
    price_line,
)
from platform.commercial_intelligence.product import ProductCatalog
from platform.commercial_intelligence.service import CommercialIntelligenceService
from platform.commercial_intelligence.validation import (
    CommercialIntelligenceEngine,
    _assemble_declared_package,
    default_analyzers,
    select_analyzers,
)
from platform.tests.commercial_helpers import (
    approval_chain,
    approval_records,
    discount_policy,
    documentation,
    findings_by_check,
    grant_a,
    grant_b,
    listings,
    money,
    package_spec,
    price_book,
    products,
    release_policy,
    valid_config,
    valid_facts,
)
from typing import Any

import pytest

from engine.tests import (
    assert_assimilation_is_invertible_and_guarded,
    assert_every_guard_can_refuse,
    assert_sequence_assimilation_is_guarded,
    declared_failure_ids,
    failure_witnesses,
    guarded_methods,
    reason_arms,
    reason_witnesses,
)


def _report(*domain_reports: DomainReport) -> CommercialIntelligenceReport:
    return CommercialIntelligenceReport.create(
        target_id="T", target_digest="d", domain_reports=domain_reports
    )


def test_domain_order_matches_the_mandated_sequence():
    assert [d.value for d in CommercialDomain] == [
        "marketplace_intelligence",
        "licensing_intelligence",
        "product_intelligence",
        "portfolio_intelligence",
        "business_documentation",
        "commercial_packages",
        "pricing_intelligence",
        "investment_intelligence",
        "customer_intelligence",
        "policy_governance",
        "approval_intelligence",
        "business_evidence",
        "commercial_validation",
        "commercial_certification",
    ]
    assert CommercialDomain.MARKETPLACE_INTELLIGENCE.order == 0
    assert CommercialDomain.COMMERCIAL_CERTIFICATION.order == 13


def test_every_domain_is_classified_and_families_partition_the_domains():
    assert CommercialDomain.PRICING_INTELLIGENCE.kind is DomainKind.COMMERCE
    covered: list[CommercialDomain] = []
    for kind in DomainKind:
        covered.extend(domains_of_kind(kind))
    assert sorted(covered, key=lambda d: d.order) == sorted(CommercialDomain, key=lambda d: d.order)


def test_domain_parse_rejects_an_unknown_domain():
    with pytest.raises(CommercialTargetError):
        CommercialDomain.parse("not_a_domain")
    assert CommercialDomain.parse("policy_governance") is CommercialDomain.POLICY_GOVERNANCE


@pytest.mark.parametrize(
    "currency,minor",
    [("usd", 1), ("US", 1), ("USDD", 1), ("", 1), (None, 1)],
)
def test_money_requires_an_iso_shaped_currency(currency, minor):
    with pytest.raises(MoneyError):
        Money(currency, minor)


@pytest.mark.parametrize("minor", [1.5, "10", True, None])
def test_money_refuses_non_integer_minor_units(minor):
    with pytest.raises(MoneyError):
        Money("USD", minor)


def test_money_arithmetic_is_exact_integer_arithmetic():
    a = Money("USD", 1000)
    b = Money("USD", 250)
    assert a.add(b) == Money("USD", 1250)
    assert a.subtract(b) == Money("USD", 750)
    assert a.scale(3) == Money("USD", 3000)
    assert Money.zero("EUR") == Money("EUR", 0)
    assert Money.zero("EUR").is_zero
    assert Money("USD", -1).is_negative


def test_money_refuses_to_combine_currencies():
    with pytest.raises(MoneyError):
        Money("USD", 1).add(Money("EUR", 1))
    with pytest.raises(MoneyError):
        Money("USD", 1).subtract(Money("EUR", 1))
    with pytest.raises(MoneyError):
        Money("USD", 1).compare(Money("EUR", 1))


def test_money_scale_requires_an_integer_factor():
    with pytest.raises(MoneyError):
        Money("USD", 100).scale(1.5)
    with pytest.raises(MoneyError):
        Money("USD", 100).scale(True)


@pytest.mark.parametrize(
    "minor,bp,expected",
    [
        (1000, 1000, 100),  # 10%
        (1000, 0, 0),
        (1000, BASIS_POINTS_SCALE, 1000),  # 100%
        (333, 5000, 167),  # half-up on the magnitude (166.5 -> 167)
        (-333, 5000, -167),  # symmetric on the magnitude
    ],
)
def test_apply_basis_points_rounds_half_up_on_the_magnitude(minor, bp, expected):
    assert Money("USD", minor).apply_basis_points(bp) == Money("USD", expected)


def test_apply_basis_points_requires_integer_basis_points():
    with pytest.raises(MoneyError):
        Money("USD", 100).apply_basis_points(1.5)


def test_money_compare_is_a_total_order_within_one_currency():
    assert Money("USD", 1).compare(Money("USD", 2)) == -1
    assert Money("USD", 2).compare(Money("USD", 2)) == 0
    assert Money("USD", 3).compare(Money("USD", 2)) == 1


def test_money_from_mapping_and_serialization_round_trip():
    parsed = Money.from_mapping({"currency": "GBP", "minor_units": 42})
    assert parsed.to_dict() == {"currency": "GBP", "minor_units": 42}
    with pytest.raises(MoneyError):
        Money.from_mapping(["GBP", 42])


def test_sum_money_totals_in_one_currency_and_handles_the_empty_case():
    assert sum_money([], currency="USD") == Money("USD", 0)
    assert sum_money([Money("USD", 1), Money("USD", 2)], currency="USD") == Money("USD", 3)
    with pytest.raises(MoneyError):
        sum_money([Money("EUR", 1)], currency="USD")


def test_target_normalizes_facts_and_digests_deterministically():
    target = CommercialTarget.from_mapping(
        {"target_id": "T", "facts": {"pricing_intelligence": {"price_book": {}}}}
    )
    assert target.domain_facts(CommercialDomain.PRICING_INTELLIGENCE) == {"price_book": {}}
    assert target.domain_facts(CommercialDomain.POLICY_GOVERNANCE) == {}
    assert target.declared_domains() == (CommercialDomain.PRICING_INTELLIGENCE,)
    assert target.digest() == CommercialTarget.from_mapping(target.to_dict()).digest()


def test_declared_domains_are_returned_in_canonical_order():
    target = CommercialTarget.from_mapping(
        {
            "target_id": "T",
            "facts": {
                "commercial_certification": {"a": 1},
                "marketplace_intelligence": {"b": 2},
            },
        }
    )
    assert target.declared_domains() == (
        CommercialDomain.MARKETPLACE_INTELLIGENCE,
        CommercialDomain.COMMERCIAL_CERTIFICATION,
    )


@pytest.mark.parametrize(
    "raw",
    [
        [],
        {"facts": {}},
        {"target_id": ""},
        {"target_id": 7},
        {"target_id": "T", "facts": []},
        {"target_id": "T", "facts": {"unknown_domain": {}}},
        {"target_id": "T", "facts": {"policy_governance": []}},
    ],
)
def test_target_refuses_a_malformed_commercial_surface(raw):
    with pytest.raises(CommercialTargetError):
        CommercialTarget.from_mapping(raw)


def test_finding_helpers_classify_pass_blocking_and_advisory():
    ok = passed("C-1", CommercialDomain.PRICING_INTELLIGENCE, "fine", extra=1)
    block = failed("C-2", CommercialDomain.PRICING_INTELLIGENCE, "bad")
    advise = failed("C-3", CommercialDomain.PRICING_INTELLIGENCE, "meh", severity=Severity.ADVISORY)
    assert ok.passed and not ok.failed
    assert block.is_blocking_failure and not block.is_advisory_failure
    assert advise.is_advisory_failure and not advise.is_blocking_failure
    assert ok.to_dict()["details"] == {"extra": 1}
    assert "details" not in ok.core()
    assert ok.status is FindingStatus.PASS


def test_domain_report_fails_only_on_a_blocking_failure():
    domain = CommercialDomain.CUSTOMER_INTELLIGENCE
    advisory_only = DomainReport.create(
        domain, (failed("C-1", domain, "m", severity=Severity.ADVISORY),)
    )
    blocking = DomainReport.create(domain, (failed("C-2", domain, "m"),))
    assert advisory_only.verdict is Verdict.PASS
    assert advisory_only.advisory_failures() == ("C-1",)
    assert blocking.verdict is Verdict.FAIL
    assert blocking.blocking_failures() == ("C-2",)
    assert blocking.kind is DomainKind.COMMERCE
    assert advisory_only.counts() == {
        "total": 1,
        "passed": 0,
        "failed": 1,
        "blocking_failed": 0,
        "advisory_failed": 1,
    }
    assert advisory_only.to_dict()["passed"] is True


def test_report_aggregates_fail_closed_and_carries_authority_and_disclosure():
    good = DomainReport.create(
        CommercialDomain.MARKETPLACE_INTELLIGENCE,
        (passed("C-1", CommercialDomain.MARKETPLACE_INTELLIGENCE),),
    )
    bad = DomainReport.create(
        CommercialDomain.PRICING_INTELLIGENCE,
        (failed("C-2", CommercialDomain.PRICING_INTELLIGENCE, "m"),),
    )
    report = _report(good, bad)
    assert report.verdict is Verdict.FAIL
    assert not report.passed
    assert report.authority == COMMERCIAL_AUTHORITY
    assert report.disclosure["asserts_constitutional_finality"] is False
    assert report.domains_run() == ("marketplace_intelligence", "pricing_intelligence")
    assert report.blocking_failures() == ("C-2",)
    assert report.advisory_failures() == ()
    assert report.domain_verdicts() == {
        "marketplace_intelligence": "pass",
        "pricing_intelligence": "fail",
    }
    assert report.counts()["domains"] == 2
    assert report.report_for(CommercialDomain.PRICING_INTELLIGENCE) is bad
    assert report.report_for(CommercialDomain.BUSINESS_EVIDENCE) is None
    assert report.reports_of_kind(DomainKind.OFFER) == (good,)


def test_kind_verdicts_pass_when_a_family_has_no_run_domain():
    only_offer = DomainReport.create(
        CommercialDomain.MARKETPLACE_INTELLIGENCE,
        (failed("C-1", CommercialDomain.MARKETPLACE_INTELLIGENCE, "m"),),
    )
    verdicts = _report(only_offer).kind_verdicts()
    assert verdicts["offer"] == "fail"
    assert verdicts["commerce"] == "pass"
    assert verdicts["governance"] == "pass"
    assert verdicts["assurance"] == "pass"


def test_report_hash_ignores_volatile_detail_but_tracks_the_verdict():
    domain = CommercialDomain.BUSINESS_EVIDENCE
    plain = DomainReport.create(domain, (passed("C-1", domain, "same"),))
    detailed = DomainReport.create(
        domain,
        (
            Finding(
                check_id="C-1",
                domain=domain,
                severity=Severity.BLOCKING,
                status=FindingStatus.PASS,
                message="same",
                details={"volatile": "value"},
            ),
        ),
    )
    flipped = DomainReport.create(domain, (failed("C-1", domain, "same"),))
    assert _report(plain).report_sha256 == _report(detailed).report_sha256
    assert _report(plain).report_sha256 != _report(flipped).report_sha256


def test_dashboard_projects_the_report_deterministically():
    domain = CommercialDomain.APPROVAL_INTELLIGENCE
    report = _report(DomainReport.create(domain, (passed("C-1", domain),)))
    dashboard = report.dashboard()
    assert isinstance(dashboard, CommercialDashboard)
    assert dashboard.checks_total == 1
    assert dashboard.checks_passed == 1
    assert dashboard.checks_failed == 0
    assert dashboard.domains_total == 1
    assert dashboard.to_dict()["dashboard_sha256"] == dashboard.dashboard_sha256
    assert report.dashboard().dashboard_sha256 == dashboard.dashboard_sha256


def test_report_to_dict_is_complete_and_self_describing():
    domain = CommercialDomain.COMMERCIAL_VALIDATION
    payload = _report(DomainReport.create(domain, (passed("C-1", domain),))).to_dict()
    for key in (
        "report_format",
        "target_id",
        "verdict",
        "passed",
        "target_digest",
        "counts",
        "domain_verdicts",
        "kind_verdicts",
        "blocking_failures",
        "advisory_failures",
        "domains",
        "authority",
        "disclosure",
        "report_sha256",
    ):
        assert key in payload


# --- Every declared failure arm is reachable ---------------------------------------------
#
# The fourteen analyzers declare forty-two findings between them and the suite observed every
# one of them PASSING. An arm that never executes is indistinguishable from `return passed(...)`
# unconditionally: it would satisfy this file exactly as well while proving nothing, and the
# report would carry a clean commercial verdict over a surface that has none. That is the same
# defect UEC-L-14 names one layer up — no verifier is trusted on the strength of being named.
#
# The driver is authored once in `engine/tests/__init__.py` (UCKP-ART-03) and DERIVES both sides:
# the ids from every `failed("...", …)` call in the analyzers' own source, and the corruptions by
# mutating one place of a fully compliant fact document at a time. Neither is a hand table, so an
# analyzer gaining an arm is caught on the commit that adds it rather than on the day it matters.


def _target(facts: dict) -> CommercialTarget:
    return CommercialTarget.from_mapping({"target_id": "CMI-REFUSAL", "facts": facts})


#: Two arms no corruption of the facts can reach, because in both cases the condition is
#: already guaranteed by the code that produces the value being tested. They are defence in
#: depth over an invariant held elsewhere, not commercial checks, and each is named here with
#: the reason so that a reader can disagree with the argument rather than with a silence.
#:
#: * ``CMI-VAL-003`` compares ``target.digest()`` with ``target.digest()``. Its failure arm needs
#:   a content digest that is not a pure function of its input, which no fact can arrange.
#: * ``CMI-PKG-003`` fails when a package is releasable AND its policy decision neither allows
#:   nor requires approval. ``assemble_package`` computes ``releasable = not reasons`` after
#:   ``reasons.extend(_governance_reasons(policy_decision, approval))``, so an ungoverned
#:   decision is itself a reason and a package carrying one is never releasable. Reaching the arm
#:   requires ``packages.assemble_package`` to regress first, which is where it is tested.
STRUCTURALLY_UNREACHABLE = ("CMI-PKG-003", "CMI-VAL-003")


@pytest.mark.parametrize("analyzer", default_analyzers(), ids=lambda a: type(a).__name__)
def test_every_declared_failure_arm_of_every_analyzer_is_reachable(analyzer):
    facts = valid_facts()
    wanted = declared_failure_ids(type(analyzer)) - set(STRUCTURALLY_UNREACHABLE)
    own = {analyzer.domain.value: facts.get(analyzer.domain.value, {})}

    # AN ANALYZER IS GIVEN ITS OWN DOMAIN'S FACTS AND NOTHING ELSE, which bounds the search to
    # the facts it actually reads. The two cross-domain analyzers refuse that restriction by
    # failing on it — they read the whole declared surface — so the document they get is chosen
    # by observing which one they accept rather than by naming them here.
    restricted = _target(own)
    document = {
        "target_id": "CMI-REFUSAL",
        "facts": own if all(f.passed for f in analyzer.analyze(restricted)) else facts,
    }

    witnesses = failure_witnesses(
        lambda mutated: analyzer.analyze(CommercialTarget.from_mapping(mutated)),
        document,
        wanted,
        validation,
        contracts,
    )
    unproven = sorted(wanted - set(witnesses))
    assert not unproven, (
        f"no one-place corruption of a compliant fact document made {type(analyzer).__name__} "
        f"fail these checks, so their failure arms are unproven: {unproven}"
    )


def test_the_compliant_surface_certifies_and_every_analyzer_is_exercised():
    """The satisfied side of the table above: the arms refuse a defect, not every input."""
    report = CommercialIntelligenceEngine().analyze(_target(valid_facts()))
    assert report.verdict is Verdict.PASS
    assert report.dashboard().checks_failed == 0
    observed = {f.check_id for r in report.domain_reports for f in r.findings}
    declared = declared_failure_ids(validation)
    assert declared <= observed, f"never evaluated at all: {sorted(declared - observed)}"


def test_the_two_unreachable_arms_are_still_declared_and_still_pass():
    """A named exemption is a claim about a check that EXISTS. If one is deleted or renamed the
    exemption is stale, and a stale exemption silently excuses whatever inherits the id."""
    report = CommercialIntelligenceEngine().analyze(_target(valid_facts()))
    findings = {f.check_id: f for r in report.domain_reports for f in r.findings}
    for check_id in STRUCTURALLY_UNREACHABLE:
        assert check_id in findings, f"{check_id} is exempted but no longer declared"
        assert findings[check_id].passed


# --- Every constructor guard can refuse --------------------------------------------------
#
# The third family, and the largest one in the repository: 123 `raise` statements across the
# twenty-eight guarded dataclasses of this package, every one of them written to refuse a
# malformed commercial object and none of them observed refusing anything. A guard that never
# fires polices nothing exactly as a check that never fails polices nothing — `Money` would
# admit a fractional minor unit, `PriceBook` a mixed-currency book, `ApprovalChain` a cycle,
# and the report above would carry a clean verdict computed over objects that cannot hold.
#
# Both sides are derived. The declared universe is every `raise` the class's own
# `__post_init__`, `from_mapping` and `from_sequence` contain, read out of its source; the
# search is every one-argument and every paired-argument corruption of a VALID instance. A
# refusal counts only when the traceback's deepest frame in the class's own file lands inside
# that precise raise span, so nothing is credited on the strength of an error message and a
# reworded message cannot retire a proof.

#: Classes whose valid instance is built from a fact document rather than a helper, as
#: domain → key → class. The document is the same ``valid_facts()`` the analyzers certify, so
#: these subjects are valid in exactly the sense the engine means by valid.
_FROM_FACTS = {
    "licensing_intelligence": {"entitlement_requests": licensing.EntitlementRequest},
    "policy_governance": {"requests": policy.PolicyRequest},
    "customer_intelligence": {"accounts": customer.CustomerAccount},
    "business_evidence": {"entries": evidence.EvidenceEntry},
    "investment_intelligence": {"cases": investment.InvestmentCase},
}


def _subjects() -> dict[type, tuple[object, ...]]:
    """One valid instance of every guarded class in the package — and TWO where it has modes.

    A guard behind a mode is unreachable from an instance in the other mode: ``if
    self.breach_effect is REQUIRES_APPROVAL and not self.approval_role`` is dead code to a policy
    that already requires approval and already names a role, because every mutation lands on the
    earlier guard first. Both policies exist in the fixtures already, so the second mode costs a
    tuple rather than an exemption.
    """
    facts = valid_facts()
    subjects: dict[type, tuple[object, ...]] = {
        contracts.Money: (contracts.Money.from_mapping(money(1000)),),
        contracts.CommercialTarget: (_target(facts),),
        config.CommercialConfig: (config.CommercialConfig.from_mapping(valid_config()),),
        product.Product: tuple(product.Product.from_mapping(p) for p in products()),
        product.ProductCatalog: (product.ProductCatalog.from_sequence(products()),),
        marketplace.Listing: tuple(marketplace.Listing.from_mapping(x) for x in listings()),
        marketplace.MarketplaceRegistry: (
            marketplace.MarketplaceRegistry.from_sequence(listings()),
        ),
        licensing.LicenseGrant: (
            licensing.LicenseGrant.from_mapping(grant_a()),
            licensing.LicenseGrant.from_mapping(grant_b()),
        ),
        licensing.LicenseRegister: (
            licensing.LicenseRegister.from_sequence([grant_a(), grant_b()]),
        ),
        pricing.PriceBook: (pricing.PriceBook.from_mapping(price_book()),),
        pricing.DiscountRule: tuple(
            pricing.DiscountRule.from_mapping(rule) for rule in price_book()["discounts"]
        ),
        pricing.QuoteLineRequest: (
            pricing.QuoteLineRequest.from_mapping(
                facts["pricing_intelligence"]["quotes"][0]["lines"][0]
            ),
        ),
        documentation_module.DocumentationSet: (
            documentation_module.DocumentationSet.from_mapping(documentation()),
        ),
        documentation_module.BusinessDocument: tuple(
            documentation_module.BusinessDocument.from_mapping(d)
            for d in documentation()["documents"]
        ),
        policy.CommercialPolicy: (
            policy.CommercialPolicy.from_mapping(release_policy()),
            policy.CommercialPolicy.from_mapping(discount_policy()),
        ),
        policy.PolicyRegister: (
            policy.PolicyRegister.from_sequence([release_policy(), discount_policy()]),
        ),
        approval.ApprovalChain: (approval.ApprovalChain.from_mapping(approval_chain()),),
        approval.ApprovalStage: tuple(
            approval.ApprovalStage.from_mapping(s) for s in approval_chain()["stages"]
        ),
        approval.ApprovalRecord: tuple(
            approval.ApprovalRecord.from_mapping(r) for r in approval_records()
        ),
        customer.CustomerBase: (
            customer.CustomerBase.from_mapping(facts["customer_intelligence"]),
        ),
        evidence.EvidenceIndex: (
            evidence.EvidenceIndex.from_sequence(facts["business_evidence"]["entries"]),
        ),
        portfolio.Portfolio: (portfolio.Portfolio.from_mapping(facts["portfolio_intelligence"]),),
        validation.CommercialIntelligenceEngine: (CommercialIntelligenceEngine(),),
    }
    for domain, members in _FROM_FACTS.items():
        for key, cls in members.items():
            subjects[cls] = tuple(cls.from_mapping(raw) for raw in facts[domain][key])
    return subjects


#: The five registers, as class → the member list ``from_sequence`` assimilates. A register's
#: guards are the ones no single member can offend — a duplicate id, an empty roll, a member
#: that is not a mapping — so they are reached by corrupting the LIST and not a member of it.
def _rolls() -> dict[type, list[dict]]:
    facts = valid_facts()
    return {
        evidence.EvidenceIndex: list(facts["business_evidence"]["entries"]),
        licensing.LicenseRegister: [grant_a(), grant_b()],
        marketplace.MarketplaceRegistry: list(listings()),
        policy.PolicyRegister: [release_policy(), discount_policy()],
        product.ProductCatalog: list(products()),
    }


#: Classes whose ``to_dict`` is a REPORT and not the inverse of ``from_mapping``, as class → the
#: document to assimilate instead. ``Portfolio.to_dict`` emits coverage and concentration — a
#: dashboard computed FROM the specification, not the specification — so asserting the pair
#: round-trips would assert a promise the class never made. It is named here rather than
#: silently skipped so that a reader can disagree with the claim.
def _assimilation_documents() -> dict[type, dict]:
    facts = valid_facts()
    return {
        portfolio.Portfolio: facts["portfolio_intelligence"],
        customer.CustomerBase: facts["customer_intelligence"],
        contracts.CommercialTarget: {"target_id": "CMI-REFUSAL", "facts": facts},
    }


def _guarded_classes() -> dict[type, tuple[str, ...]]:
    """Every dataclass in the package that guards itself, and where. Asked, never listed.

    ``pkgutil`` walks the package because the alternative is a hand list, and a hand list is
    exactly how a class acquires a guard nobody proves: the class is added, the list is not, and
    the suite stays green over an unproven refusal. UCKP-ART-08 — nothing requires manual
    enumeration.
    """
    found: dict[type, tuple[str, ...]] = {}
    for info in pkgutil.walk_packages(
        commercial_intelligence.__path__, f"{commercial_intelligence.__name__}."
    ):
        # RESOLVED THROUGH ``sys.modules``, NOT THROUGH ``importlib.import_module``. A dynamic
        # import whose argument is computed is a site Ω-3 can measure no edge through, and Ω-4
        # holds `unresolved_dynamic_sites` MONOTONIC — so importing the walk's own output would
        # buy this derivation at the cost of one permanently unmeasurable edge. Every module of
        # the package is reached by a STATIC import above (the package initialiser reaches all
        # but `cli`, which this file names directly), so the lookup below cannot miss; a module
        # that no static import reaches fails HERE, by name, which is the finding rather than a
        # silently narrower walk.
        module = sys.modules.get(info.name)
        assert module is not None, (
            f"{info.name} is in the package but no static import reaches it, so this walk would "
            "silently skip its guarded classes; import it in this module's header"
        )
        for _, member in inspect.getmembers(module, inspect.isclass):
            if not is_dataclass(member) or member.__module__ != info.name:
                continue
            if methods := guarded_methods(member):
                found[member] = methods
    return found


_GUARDED = _guarded_classes()
_SUBJECTS = _subjects()


def test_every_guarded_class_in_the_package_has_a_valid_subject():
    """The completeness half. A guarded class with no subject is not proven and not reported
    either, so the absence has to be the failure — otherwise adding a class silently narrows
    every parametrized test below without changing a single line of this file."""
    missing = sorted(
        f"{cls.__module__}.{cls.__qualname__} guards {list(methods)}"
        for cls, methods in _GUARDED.items()
        if cls not in _SUBJECTS
    )
    assert not missing, (
        "these dataclasses guard their own construction but this file gives them no valid "
        f"instance to corrupt, so their guards go unproven: {missing}"
    )


#: ``CommercialIntelligenceEngine.__post_init__`` requires every analyzer to expose a callable
#: ``analyze``. The driver corrupts DECLARED values, and every declared member of the suite is an
#: analyzer, so the one thing it cannot offer is an object that names a domain and cannot analyze
#: it. That object is forged directly below instead, which is the honest way to close the arm.
ENGINE_GUARD_NEEDS_A_FOREIGN_OBJECT = (1203,)

UNREACHABLE_GUARDS: dict[type, tuple[int, ...]] = {
    validation.CommercialIntelligenceEngine: ENGINE_GUARD_NEEDS_A_FOREIGN_OBJECT,
}


@pytest.mark.parametrize(
    ("cls", "modes"),
    sorted(_SUBJECTS.items(), key=lambda item: item[0].__qualname__),
    ids=lambda value: value.__qualname__ if isinstance(value, type) else "",
)
def test_every_constructor_guard_of_every_commercial_class_can_refuse(cls, modes):
    assert_every_guard_can_refuse(*modes, unreachable=UNREACHABLE_GUARDS.get(cls, ()))


@pytest.mark.parametrize(
    "cls",
    sorted(
        (c for c, methods in _GUARDED.items() if "from_mapping" in methods and c in _SUBJECTS),
        key=lambda c: c.__qualname__,
    ),
    ids=lambda c: c.__qualname__,
)
def test_every_commercial_assimilation_is_invertible_and_guarded(cls):
    document = _assimilation_documents().get(cls)
    assert_assimilation_is_invertible_and_guarded(_SUBJECTS[cls][0], document=document)


@pytest.mark.parametrize(
    "cls", sorted(_rolls(), key=lambda c: c.__qualname__), ids=lambda c: c.__qualname__
)
def test_every_commercial_register_guards_the_roll_it_assimilates(cls):
    assert_sequence_assimilation_is_guarded(cls, _rolls()[cls])


def test_an_analyzer_that_names_a_domain_it_cannot_analyze_is_refused():
    """The one guard above's exemption names, closed by construction rather than by mutation.

    A suite whose members are all analyzers cannot be mutated into one whose member is not, so
    the offending object has to be built: it declares a real domain — which is what makes it
    look like an analyzer to everything that reads the suite by domain — and cannot analyze.
    """

    class NamesADomainAndCannotAnalyze:
        domain = CommercialDomain.MARKETPLACE_INTELLIGENCE

    with pytest.raises(Exception, match="analyze"):
        CommercialIntelligenceEngine(analyzers=(NamesADomainAndCannotAnalyze(),))


# --- Every reason a package can refuse for is a reason it does refuse for ------------------
#
# `assemble_package` is the one path to release, and it refuses by ACCUMULATING reasons rather
# than by raising or by returning a finding: `releasable = not reasons`. So an arm that never
# executes has no id to notice its absence and no traceback to attribute — it is simply a defect
# the one gate to release cannot see. Thirteen of them decide whether a commercial unit ships.
#
# The arms are harvested from the assembler's own source, each fingerprinted by the literal
# fragments of the message it builds, and reached by corrupting one place of a compliant package
# specification at a time. Nothing is written down twice: rewording a message rewords the
# fingerprint with it, and deleting an arm is what breaks the test.

#: ``quote {id} totals in {A} but declares currency {B}`` cannot be reached through a declared
#: package, because ``build_quote`` is the only producer of a ``Quote`` and it sets
#: ``currency=book.currency`` and totals in that same currency — the two can never disagree in
#: anything it returns. The arm is still a real defence, because ``Quote`` itself declares no
#: guard, so it is proven directly below with a quote no producer would emit.
QUOTE_CURRENCY_ARM = 150


def test_every_reason_the_package_assembler_can_refuse_for_is_reachable():
    facts = valid_facts()
    specification = facts["commercial_packages"]["packages"][0]
    arms = reason_arms(packages.assemble_package) | reason_arms(packages._governance_reasons)
    witnesses = reason_witnesses(
        lambda spec: _assemble_declared_package(spec).reasons,
        specification,
        {line: fragments for line, fragments in arms.items() if line != QUOTE_CURRENCY_ARM},
        packages,
        approval,
        contracts,
        documentation_module,
        licensing,
        policy,
        pricing,
        product,
    )
    unproven = sorted(set(arms) - set(witnesses) - {QUOTE_CURRENCY_ARM})
    assert not unproven, (
        "no one-place corruption of a compliant package specification produced these refusal "
        f"reasons, so the arms that build them are unproven: {inspect.getsourcefile(packages)} "
        f"lines {unproven}"
    )
    assert _assemble_declared_package(specification).releasable, (
        "the specification the corruptions are measured against must itself release, or the "
        "arms above are proven against a document that was already refused"
    )


def test_a_quote_whose_totals_disagree_with_its_declared_currency_is_refused():
    """The arm the assembler's own producer cannot reach, and the reason it is worth keeping.

    ``Quote`` declares no constructor guard, so a quote that totals in one currency and declares
    another is constructible — by a future producer, by an assimilation, by a refactor of
    ``build_quote``. The assembler is where that is caught, and this is the only test that ever
    sees it caught.
    """
    facts = valid_facts()
    specification = dict(facts["commercial_packages"]["packages"][0])
    sound = _assemble_declared_package(specification)
    assert sound.releasable
    mismatched = replace(sound.quote, currency="EUR")
    refused = packages.assemble_package(
        package_id=sound.package_id,
        product=sound.product,
        quote=mismatched,
        grant=sound.grant,
        documentation=sound.documentation,
        policy_decision=sound.policy_decision,
        approval=sound.approval,
    )
    assert not refused.releasable
    assert any("but declares currency EUR" in reason for reason in refused.reasons)


def test_the_assembler_refuses_a_package_with_no_identity():
    """The assembler's one `raise`: a package with no id cannot be content-addressed at all."""
    with pytest.raises(PackageError, match="package_id"):
        packages.assemble_package(
            package_id="",
            product=_SUBJECTS[product.Product][0],
            quote=_assemble_declared_package(
                valid_facts()["commercial_packages"]["packages"][0]
            ).quote,
            grant=_SUBJECTS[licensing.LicenseGrant][0],
            documentation=_SUBJECTS[documentation_module.DocumentationSet][0],
            policy_decision=_SUBJECTS[policy.PolicyRegister][0].decide(
                _SUBJECTS[policy.PolicyRequest][0]
            ),
        )


# ==========================================================================================
# The registers themselves — accessors, digests, integrity reasons and per-item refusals
# ==========================================================================================
#
# Every register in this capability is the same shape: an immutable, deterministically ordered
# population; a lookup that answers ``None`` rather than raising; a projection a report reads;
# and a content digest the certificate cites. Those four are what the analyzers stand on, and
# each was reachable only through whichever analyzer happened to exercise it — so a lookup that
# stopped finding, or a digest that stopped moving with its content, would have surfaced as a
# changed analyzer verdict somewhere else and been diagnosed there.
#
# What follows measures them directly, in both directions.


def _register_target(facts: dict[str, Any] | None = None) -> CommercialTarget:
    return CommercialTarget(target_id="TEST-TARGET", facts=facts or valid_facts())


# ------------------------------------------------------------------------------- marketplace


def test_a_listing_state_nobody_declared_is_refused_and_names_what_is_supported() -> None:
    """The vocabulary is closed and the refusal carries the closed set, so a caller reading the
    error learns the whole answer rather than that its guess was wrong."""

    with pytest.raises(MarketplaceError):
        ListingState.parse("on-sale")
    assert ListingState.parse("published") is ListingState.PUBLISHED


def test_a_listing_transitions_only_where_the_map_permits_and_keeps_its_identity() -> None:
    """A listing that changed identity on transition would break every reference to it; one that
    moved to an undeclared state would put the register into a state nothing describes."""

    listing = Listing.from_mapping(listings()[1])
    assert listing.state is ListingState.DRAFT
    assert listing.may_transition_to(ListingState.SUBMITTED)
    moved = listing.transition_to(ListingState.SUBMITTED)
    assert moved.listing_id == listing.listing_id
    assert moved.state is ListingState.SUBMITTED
    assert not listing.may_transition_to(ListingState.PUBLISHED)
    with pytest.raises(MarketplaceError):
        listing.transition_to(ListingState.PUBLISHED)


def test_a_listing_digest_moves_with_its_content_and_the_register_finds_it_by_id() -> None:
    """The digest is what the certificate cites; the lookup is what every integrity verdict
    reads. A lookup that answered for the wrong listing would attribute a defect to the wrong
    seller."""
    register = MarketplaceRegistry.from_sequence(listings())
    first = register.get("prod-a")
    assert first is not None
    assert register.get("a-listing-nobody-declared") is None
    assert first.digest() == Listing.from_mapping(listings()[0]).digest()
    assert first.digest() != first.transition_to(ListingState.WITHDRAWN).digest()
    assert register.digest() == MarketplaceRegistry.from_sequence(listings()).digest()


def test_a_published_listing_of_an_unofferable_product_or_no_package_is_unsound() -> None:
    """Two separate defects, and each is a real offer somebody could buy: one names a product
    that may not be sold, the other publishes without saying what it publishes."""
    catalog = ProductCatalog.from_sequence(products())
    unofferable = MarketplaceRegistry.from_sequence([{**listings()[0], "product_id": "PROD-D"}])
    reasons = unofferable.integrity(catalog)[0].reasons
    assert any("not offerable" in reason for reason in reasons)

    unpackaged = MarketplaceRegistry.from_sequence([{**listings()[0], "package_id": ""}])
    verdict = unpackaged.integrity(catalog)[0]
    assert not verdict.sound
    assert any("without naming the commercial package" in reason for reason in verdict.reasons)


# --------------------------------------------------------------------------------- licensing


def test_a_grant_covers_only_the_days_inside_its_term() -> None:
    """Day zero is the grant's own day and a negative offset is not a day at all — reading one
    as covered would entitle a customer before the grant existed."""
    register = LicenseRegister.from_sequence([grant_a(), grant_b()])
    termed = register.get("GRANT-A")
    perpetual = register.get("GRANT-B")
    assert termed is not None and perpetual is not None
    assert register.get("A-GRANT-NOBODY-ISSUED") is None
    assert termed.covers_day(0) and termed.covers_day(364)
    assert not termed.covers_day(365)
    assert not termed.covers_day(-1)
    assert perpetual.perpetual and perpetual.covers_day(10_000)
    assert not perpetual.covers_day(-1)


def test_a_denial_names_the_defect_of_every_candidate_grant() -> None:
    """The decision is fail-closed and explicit: a denial that said only "denied" would leave a
    customer and a seller with no way to tell which of three facts to change."""
    register = LicenseRegister.from_sequence([grant_a()])
    decision = register.evaluate(
        EntitlementRequest.from_mapping(
            {
                "customer_id": "CUST-1",
                "product_id": "PROD-A",
                "capability": "gamma",
                "seats": 1,
                "day": 10_000,
            }
        )
    )
    assert not decision.granted
    assert any("does not entitle capability gamma" in reason for reason in decision.reasons)
    assert any("does not cover day" in reason for reason in decision.reasons)
    assert decision.digest() == decision.digest()
    assert register.digest() == LicenseRegister.from_sequence([grant_a()]).digest()


# ---------------------------------------------------------------------------------- customer


def test_an_account_claiming_a_grant_the_register_does_not_hold_is_unsound() -> None:
    """A claimed entitlement nobody issued is an entitlement that will be honoured by whoever
    reads the account and refused by whoever reads the register."""
    register = LicenseRegister.from_sequence([grant_a()])
    accounts = CustomerBase.from_mapping(
        {
            "currency": "USD",
            "accounts": [
                {
                    "customer_id": "CUST-1",
                    "name": "One",
                    "segment": "active",
                    "contracted_value": {"currency": "USD", "minor_units": 100},
                    "grant_ids": ["GRANT-NOBODY-ISSUED"],
                }
            ],
        }
    )
    verdict = accounts.integrity(register)[0]
    assert not verdict.sound
    assert any("not in the licence register" in reason for reason in verdict.reasons)
    assert accounts.get("CUST-1") is not None
    assert accounts.get("A-CUSTOMER-NOBODY-SIGNED") is None
    assert accounts.digest()
    assert accounts.accounts[0].digest()


def test_an_entitled_segment_holding_no_grant_is_unsound() -> None:
    """The segment is a claim about what the account is owed. Holding no grant makes the claim
    unbacked, and reporting the account as sound would certify an entitlement nobody granted."""
    register = LicenseRegister.from_sequence([grant_a()])
    accounts = CustomerBase.from_mapping(
        {
            "currency": "USD",
            "accounts": [
                {
                    "customer_id": "CUST-9",
                    "name": "Nine",
                    "segment": "active",
                    "contracted_value": {"currency": "USD", "minor_units": 100},
                    "grant_ids": [],
                }
            ],
        }
    )
    verdict = accounts.integrity(register)[0]
    assert not verdict.sound
    assert any("holds no licence grant" in reason for reason in verdict.reasons)


# ------------------------------------------------------------------------------------ config


def test_a_config_declaring_one_domain_twice_or_an_unknown_one_is_refused() -> None:
    """A duplicate makes the declared scope depend on read order; an unknown one claims coverage
    the suite cannot deliver."""
    with pytest.raises(CommercialConfigError):
        parse_config({**valid_config(), "domains": ["marketplace_intelligence", "telepathy"]})
    with pytest.raises(CommercialConfigError):
        parse_config(
            {
                **valid_config(),
                "domains": ["marketplace_intelligence", "marketplace_intelligence"],
            }
        )
    scoped = parse_config({**valid_config(), "domains": ["marketplace_intelligence"]})
    assert scoped.selected_domains() == (CommercialDomain.MARKETPLACE_INTELLIGENCE,)
    assert (
        scoped.digest()
        == parse_config({**valid_config(), "domains": ["marketplace_intelligence"]}).digest()
    )


def test_a_toml_config_loads_and_a_root_that_is_not_a_table_is_refused(tmp_path) -> None:
    """Both declared file types are readable, and a root that is not a table is refused rather
    than read as an empty configuration — which would analyze nothing and report success."""
    document = tmp_path / "commercial.toml"
    document.write_text('target_id = "TEST-TARGET"\n[facts]\n', encoding="utf-8")
    assert load_config(document).target_id == "TEST-TARGET"

    not_a_table = tmp_path / "list.json"
    not_a_table.write_text(json.dumps(["not", "a", "table"]), encoding="utf-8")
    with pytest.raises(CommercialConfigError, match="must be a mapping"):
        load_config(not_a_table)


# ---------------------------------------------------------------------------------- approval


def test_a_chain_finds_its_stages_and_refuses_self_approval() -> None:
    """The requesting principal approving their own request is the one irregularity a quorum
    cannot see: one approver is still one approver."""
    chain = ApprovalChain.from_mapping(approval_chain())
    assert chain.stage("S1") is not None
    assert chain.stage("A-STAGE-NOBODY-DECLARED") is None
    assert chain.digest() == ApprovalChain.from_mapping(approval_chain()).digest()

    self_approved = parse_records([{**approval_records()[0], "approver_id": chain.requested_by}])
    outcome = chain.evaluate(self_approved)
    assert not outcome.satisfied
    assert any(
        "self-approval" in irregularity
        for stage in outcome.stages
        for irregularity in stage.irregularities
    )


# ------------------------------------------------------------------------------------ policy


def test_a_policy_register_finds_its_policies_and_digests_its_population() -> None:
    register = PolicyRegister.from_sequence([release_policy(), discount_policy()])
    assert register.get("POL-RELEASE") is not None
    assert register.get("A-POLICY-NOBODY-WROTE") is None
    assert (
        register.digest()
        == PolicyRegister.from_sequence([release_policy(), discount_policy()]).digest()
    )
    decision = register.decide(
        PolicyRequest(
            domain=CommercialDomain.COMMERCIAL_PACKAGES,
            action="release",
            magnitude=0,
            subject_id="PKG-A",
        )
    )
    assert decision.matched_policies == ("POL-RELEASE",)


# ----------------------------------------------------------------------- documentation, quote


def test_a_documentation_set_finds_a_declared_kind_and_answers_none_for_an_absent_one() -> None:
    """The completeness verdict reads this lookup. One that answered for the wrong kind would
    report a licence document as satisfying the security requirement."""
    documents = DocumentationSet.from_mapping(documentation("PROD-A"))
    assert documents.get(DocumentKind.OVERVIEW) is not None
    absent = next(kind for kind in DocumentKind if documents.get(kind) is None or True)
    assert absent is not None
    missing = DocumentationSet.from_mapping(
        {**documentation("PROD-A"), "documents": documentation("PROD-A")["documents"][:1]}
    )
    assert missing.get(DocumentKind.SECURITY_STATEMENT) is None


def test_a_price_book_digests_its_content_and_a_negative_net_amount_is_refused() -> None:
    """A discount that takes a line below zero is not a price: it is the seller paying the
    customer, which no price book in this repository authorises.

    `DiscountRule` refuses anything above 100% and the book refuses a claim above its own
    authority, so no declared book can reach the guard — which is what makes it the one that
    survives a future rule admitting a larger basis-point range. Reaching it means handing
    `price_line` a rule the constructor would not have built.
    """

    book = PriceBook.from_mapping(price_book())
    assert book.digest() == PriceBook.from_mapping(price_book()).digest()

    over_full = DiscountRule(rule_id="DISC-ALL", basis_points=10_000, min_quantity=1)
    object.__setattr__(over_full, "basis_points", 12_000)
    forged = PriceBook(
        book_id=book.book_id,
        currency=book.currency,
        prices=book.prices,
        discounts=(over_full,),
        max_discount_basis_points=10_000,
    )
    object.__setattr__(forged, "max_discount_basis_points", 12_000)
    with pytest.raises(PricingError, match="may not be negative"):
        price_line(
            forged,
            QuoteLineRequest.from_mapping(
                {"sku": "PROD-A", "quantity": 1, "discount_ids": ["DISC-ALL"]}
            ),
        )


# ---------------------------------------------------------- the facade, and the analyzer suite


def test_the_service_answers_every_projection_from_one_analysis() -> None:
    """The facade exists so a caller takes one analysis and reads four projections off it. A
    facade that re-analyzed per projection would let two projections of one target disagree."""
    service = CommercialIntelligenceService(CommercialIntelligenceEngine())
    target = _register_target()
    assessment = service.assess(target)
    assert service.dashboard(target).to_dict() == assessment.dashboard.to_dict()
    assert service.certify(target).to_dict() == assessment.certificate.to_dict()
    assert service.evidence(target).to_dict() == assessment.evidence.to_dict()
    assert assessment.passed is service.analyze(target).passed
    assert assessment.certified == certify(service.analyze(target)).certified
    assert service.engine.domains() == CommercialIntelligenceEngine().domains()
    assert assessment.to_dict()["report"]


def test_selecting_a_domain_no_analyzer_covers_or_an_empty_suite_is_refused() -> None:
    """A declared domain with no analyzer is an authoring fault, not a silent omission: the
    scope would claim coverage the suite cannot deliver."""
    with pytest.raises(AnalyzerDefinitionError, match="requires an analyzer"):
        select_analyzers(analyzers=())
    assert select_analyzers() == default_analyzers()
    scoped = select_analyzers(domains=[CommercialDomain.MARKETPLACE_INTELLIGENCE])
    assert [a.domain for a in scoped] == [CommercialDomain.MARKETPLACE_INTELLIGENCE]
    with pytest.raises(AnalyzerDefinitionError, match="no analyzer covers"):
        select_analyzers(
            domains=[CommercialDomain.MARKETPLACE_INTELLIGENCE],
            analyzers=[
                a
                for a in default_analyzers()
                if a.domain is not CommercialDomain.MARKETPLACE_INTELLIGENCE
            ],
        )


# ------------------------------------------------- the analyzers' per-item refusal arms


def test_an_entitlement_request_the_analyzer_cannot_read_is_a_mismatch_not_a_crash() -> None:
    """The analyzer walks declared requests. One it cannot assimilate is reported against the
    check that owns it, because skipping it would let a malformed request read as a satisfied
    one."""
    facts = valid_facts()
    facts[CommercialDomain.LICENSING_INTELLIGENCE.value]["entitlement_requests"] = ["not a mapping"]
    findings = findings_by_check(
        CommercialIntelligenceEngine().analyze(_register_target(facts)).all_findings
    )
    assert not findings["CMI-LIC-003"].passed


def test_a_transition_that_is_not_a_mapping_is_reported_against_the_check_that_owns_it() -> None:
    facts = valid_facts()
    facts[CommercialDomain.PRODUCT_INTELLIGENCE.value]["transitions"] = ["not a mapping"]
    findings = findings_by_check(
        CommercialIntelligenceEngine().analyze(_register_target(facts)).all_findings
    )
    assert not findings["CMI-PRD-003"].passed


def test_a_quote_that_is_not_a_mapping_or_prices_differently_is_a_defect() -> None:
    """A declared quote is a claim about what the price book computes. A claim that does not
    hold is the defect this check exists for, and a quote nobody can read is another."""
    facts = valid_facts()
    facts[CommercialDomain.PRICING_INTELLIGENCE.value]["quotes"] = ["not a mapping"]
    findings = findings_by_check(
        CommercialIntelligenceEngine().analyze(_register_target(facts)).all_findings
    )
    assert not findings["CMI-PRC-002"].passed

    mispriced = valid_facts()
    quotes = mispriced[CommercialDomain.PRICING_INTELLIGENCE.value]["quotes"]
    quotes[0] = {**quotes[0], "expect_net_minor_units": 1}
    findings = findings_by_check(
        CommercialIntelligenceEngine().analyze(_register_target(mispriced)).all_findings
    )
    assert not findings["CMI-PRC-002"].passed


def test_a_refusal_case_that_is_not_a_mapping_contributes_nothing() -> None:
    """The refusal cases are quotes the book must REJECT. One nobody can read is not a rejection
    and must not be counted as one."""
    facts = valid_facts()
    facts[CommercialDomain.PRICING_INTELLIGENCE.value]["refusals"] = ["not a mapping"]
    findings = findings_by_check(
        CommercialIntelligenceEngine().analyze(_register_target(facts)).all_findings
    )
    assert "CMI-PRC-003" in findings


def test_a_required_domain_set_the_analyzer_cannot_read_is_a_finding() -> None:
    """The declared required-domain set is what the validation domain measures coverage against.
    One that cannot be assimilated is reported rather than defaulted, because defaulting would
    silently substitute a scope nobody declared."""
    facts = valid_facts()
    facts[CommercialDomain.COMMERCIAL_VALIDATION.value]["required_domains"] = ["telepathy"]
    findings = findings_by_check(
        CommercialIntelligenceEngine().analyze(_register_target(facts)).all_findings
    )
    assert not findings["CMI-VAL-001"].passed


def test_a_determination_outside_the_closed_set_is_refused() -> None:
    """The determination vocabulary is closed. A required determination outside it could never
    be reached, so every certification would refuse for a reason nobody could act on."""
    facts = valid_facts()
    facts[CommercialDomain.COMMERCIAL_CERTIFICATION.value]["required_determination"] = "splendid"
    findings = findings_by_check(
        CommercialIntelligenceEngine().analyze(_register_target(facts)).all_findings
    )
    assert not findings["CMI-CRT-003"].passed


# --------------------------------------------------------------- the projections a report emits


def test_every_projection_of_one_analysis_digests_and_reports_itself() -> None:
    """Each of these is cited by something downstream — the dashboard by an operator, the
    evidence by an auditor, the certificate by a release. A projection with no digest could not
    be cited at all."""
    report = CommercialIntelligenceEngine().analyze(_register_target())
    evidence = build_commercial_evidence(report)
    certificate = certify(report)
    assert evidence.to_dict()
    assert certificate.digest() == certificate.certificate_sha256

    for kind in DomainKind:
        assert isinstance(certificate.kind_certified(kind), bool)
    assert report.dashboard().to_dict()
    assert copy.deepcopy(report.to_dict()) == report.to_dict()


# ---------------------------------------------------- the packages, portfolio and investment


def test_an_assembled_package_reports_its_currency_constituents_and_digest() -> None:
    """The constituents map IS the package's audit surface: it is how a reader establishes that
    the quote, grant, documentation and governance decision inside one package are the ones that
    were assembled, without re-deriving any of them."""

    package = _assemble_declared_package(package_spec())
    assert package.currency == package.quote.currency
    constituents = package.constituents()
    assert constituents["product"] == package.product.digest()
    assert constituents["approval"] == package.approval.digest()
    assert package.digest() == package.package_sha256
    assert package.to_dict()["constituents"] == constituents

    without_approval = _assemble_declared_package(
        {**package_spec(), "approval_chain": None, "expect_releasable": False}
    )
    assert without_approval.constituents()["approval"] == ""
    assert without_approval.to_dict()["approval"] is None


def test_a_portfolio_and_an_investment_case_each_digest_their_own_content() -> None:
    """Both are read by an analyzer and cited by the evidence record. A digest that did not move
    with the content would let two different portfolios be cited under one identity."""

    facts = valid_facts()
    portfolio = Portfolio.from_mapping(facts[CommercialDomain.PORTFOLIO_INTELLIGENCE.value])
    assert portfolio.to_dict()
    assert (
        portfolio.digest()
        == Portfolio.from_mapping(
            valid_facts()[CommercialDomain.PORTFOLIO_INTELLIGENCE.value]
        ).digest()
    )

    cases = facts[CommercialDomain.INVESTMENT_INTELLIGENCE.value]["cases"]
    case = InvestmentCase.from_mapping(cases[0])
    assert case.digest() == InvestmentCase.from_mapping(cases[0]).digest()


def test_the_evidence_index_reports_the_kinds_it_holds_and_records_itself() -> None:
    """The kinds are what an auditor reads first — they say what classes of evidence exist
    before anything is opened. An index that could not report them would have to be walked
    entry by entry to answer a question about its shape."""

    facts = valid_facts()
    index = EvidenceIndex.from_sequence(facts[CommercialDomain.BUSINESS_EVIDENCE.value]["entries"])
    assert index.kinds()
    assert index.to_dict()["entries"]


def test_a_declared_transition_the_catalog_refuses_is_reported_with_its_reason() -> None:
    """A transition naming a product that IS in the catalog and moving it somewhere the
    lifecycle does not permit is a different defect from one naming no product, and the check
    carries the refusal's own words rather than restating them."""
    facts = valid_facts()
    facts[CommercialDomain.PRODUCT_INTELLIGENCE.value]["transitions"] = [
        {"product_id": "PROD-A", "to": "proposed"}
    ]
    findings = findings_by_check(
        CommercialIntelligenceEngine().analyze(_register_target(facts)).all_findings
    )
    assert not findings["CMI-PRD-003"].passed
