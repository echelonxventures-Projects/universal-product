"""UCOS-EPIC-014 — shared builders for the Commercial Intelligence tests (Terminal T5).

Every builder returns a **fresh, deep-copied** structure so a test may mutate one domain's
facts without leaking into another test. The default surface is deliberately *fully
compliant*: each analyzer test then removes or corrupts exactly one fact and asserts the
corresponding fail-closed finding, which is what proves the check has evidentiary value in
both directions.
"""

from __future__ import annotations

import copy
import hashlib
from platform.commercial_intelligence.contracts import CommercialDomain, Money
from typing import Any


def digest_of(text: str) -> str:
    """A stable, honest content digest for a fixture document/evidence artefact."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def money(minor_units: int, currency: str = "USD") -> dict[str, Any]:
    return {"currency": currency, "minor_units": minor_units}


def usd(minor_units: int) -> Money:
    return Money("USD", minor_units)


def product_a() -> dict[str, Any]:
    return {
        "product_id": "PROD-A",
        "name": "Product A",
        "sku": "PROD-A",
        "version": "1.0.0",
        "state": "general_availability",
        "capabilities": ["alpha", "beta"],
    }


def product_b() -> dict[str, Any]:
    return {
        "product_id": "PROD-B",
        "name": "Product B",
        "sku": "PROD-B",
        "version": "2.1.0",
        "state": "general_availability",
        "capabilities": ["gamma"],
    }


def product_dev() -> dict[str, Any]:
    return {
        "product_id": "PROD-D",
        "name": "Product D",
        "sku": "PROD-D",
        "version": "0.1.0",
        "state": "development",
        "capabilities": ["delta"],
    }


def products() -> list[dict[str, Any]]:
    return [product_a(), product_b(), product_dev()]


def listings() -> list[dict[str, Any]]:
    return [
        {
            "listing_id": "prod-a",
            "product_id": "PROD-A",
            "seller_id": "SELLER-1",
            "state": "published",
            "package_id": "PKG-A",
        },
        {
            "listing_id": "prod-d",
            "product_id": "PROD-D",
            "seller_id": "SELLER-1",
            "state": "draft",
            "package_id": "",
        },
    ]


def grant_a() -> dict[str, Any]:
    return {
        "grant_id": "GRANT-A",
        "product_id": "PROD-A",
        "customer_id": "CUST-1",
        "model": "subscription",
        "seats": 10,
        "term_days": 365,
        "capabilities": ["alpha", "beta"],
    }


def grant_b() -> dict[str, Any]:
    return {
        "grant_id": "GRANT-B",
        "product_id": "PROD-B",
        "customer_id": "CUST-2",
        "model": "perpetual",
        "seats": 5,
        "term_days": 0,
        "capabilities": ["gamma"],
    }


def price_book() -> dict[str, Any]:
    return {
        "book_id": "PB-TEST",
        "currency": "USD",
        "max_discount_basis_points": 1500,
        "prices": {
            "PROD-A": money(100000),
            "PROD-B": money(50000),
            "PROD-D": money(20000),
        },
        "discounts": [
            {"rule_id": "DISC-05", "basis_points": 500, "min_quantity": 1},
            {"rule_id": "DISC-10", "basis_points": 1000, "min_quantity": 10},
            {"rule_id": "DISC-20", "basis_points": 2000, "min_quantity": 1},
        ],
    }


DOCUMENT_KINDS: tuple[tuple[str, str], ...] = (
    ("overview", "OVERVIEW"),
    ("pricing_sheet", "PRICING"),
    ("licence_terms", "LICENCE"),
    ("support_policy", "SUPPORT"),
    ("security_statement", "SECURITY"),
)


def documentation(subject_id: str = "PROD-A") -> dict[str, Any]:
    return {
        "subject_id": subject_id,
        "documents": [
            {
                "document_id": f"DOC-{subject_id}-{suffix}",
                "kind": kind,
                "title": f"{subject_id} {suffix.title()}",
                "version": "1.0.0",
                "content_sha256": digest_of(f"DOC-{subject_id}-{suffix}"),
            }
            for kind, suffix in DOCUMENT_KINDS
        ],
    }


def release_policy() -> dict[str, Any]:
    return {
        "policy_id": "POL-RELEASE",
        "domain": "commercial_packages",
        "action": "release",
        "effect": "requires_approval",
        "approval_role": "commercial-authority",
    }


def discount_policy() -> dict[str, Any]:
    return {
        "policy_id": "POL-DISCOUNT",
        "domain": "pricing_intelligence",
        "action": "discount",
        "effect": "allow",
        "max_magnitude": 1500,
        "breach_effect": "deny",
    }


def approval_chain(chain_id: str = "CHAIN-A", quorum: int = 1) -> dict[str, Any]:
    return {
        "chain_id": chain_id,
        "requested_by": "requester",
        "stages": [{"stage_id": "S1", "role": "commercial-authority", "quorum": quorum}],
    }


def approval_records() -> list[dict[str, Any]]:
    return [
        {
            "record_id": "R1",
            "stage_id": "S1",
            "approver_id": "approver-1",
            "role": "commercial-authority",
            "decision": "approved",
        }
    ]


def package_spec() -> dict[str, Any]:
    return {
        "package_id": "PKG-A",
        "expect_releasable": True,
        "quote_id": "Q-PKG-A",
        "product": product_a(),
        "price_book": price_book(),
        "lines": [{"sku": "PROD-A", "quantity": 10, "discount_ids": ["DISC-10"]}],
        "grant": grant_a(),
        "documentation": documentation("PROD-A"),
        "policies": [release_policy(), discount_policy()],
        "policy_request": {
            "domain": "commercial_packages",
            "action": "release",
            "magnitude": 0,
            "subject_id": "PKG-A",
        },
        "approval_chain": approval_chain(),
        "approval_records": approval_records(),
    }


def valid_facts() -> dict[str, dict[str, Any]]:
    """A fully compliant fourteen-domain commercial surface."""
    return copy.deepcopy(
        {
            CommercialDomain.MARKETPLACE_INTELLIGENCE.value: {
                "products": products(),
                "listings": listings(),
            },
            CommercialDomain.LICENSING_INTELLIGENCE.value: {
                "grants": [grant_a(), grant_b()],
                "entitlement_requests": [
                    {
                        "customer_id": "CUST-1",
                        "product_id": "PROD-A",
                        "capability": "alpha",
                        "seats": 5,
                        "day": 10,
                        "expect_granted": True,
                    },
                    {
                        "customer_id": "CUST-1",
                        "product_id": "PROD-A",
                        "capability": "alpha",
                        "seats": 500,
                        "day": 10,
                        "expect_granted": False,
                    },
                ],
            },
            CommercialDomain.PRODUCT_INTELLIGENCE.value: {
                "products": products(),
                "transitions": [{"product_id": "PROD-D", "to": "general_availability"}],
            },
            CommercialDomain.PORTFOLIO_INTELLIGENCE.value: {
                "portfolio_id": "PORT-1",
                "required_capabilities": ["alpha", "beta", "gamma"],
                "max_concentration_basis_points": 7000,
                "products": products(),
            },
            CommercialDomain.BUSINESS_DOCUMENTATION.value: {
                "sets": [documentation("PROD-A"), documentation("PROD-B")],
            },
            CommercialDomain.COMMERCIAL_PACKAGES.value: {"packages": [package_spec()]},
            CommercialDomain.PRICING_INTELLIGENCE.value: {
                "price_book": price_book(),
                "quotes": [
                    {
                        "quote_id": "Q-1",
                        "expect_net_minor_units": 900000,
                        "lines": [{"sku": "PROD-A", "quantity": 10, "discount_ids": ["DISC-10"]}],
                    }
                ],
                "refusals": [
                    {
                        "quote_id": "R-1",
                        "lines": [{"sku": "PROD-A", "quantity": 1, "discount_ids": ["DISC-10"]}],
                    },
                    {
                        "quote_id": "R-2",
                        "lines": [{"sku": "PROD-A", "quantity": 1, "discount_ids": ["DISC-20"]}],
                    },
                ],
            },
            CommercialDomain.INVESTMENT_INTELLIGENCE.value: {
                "cases": [
                    {
                        "case_id": "INV-1",
                        "currency": "USD",
                        "require_recovered": True,
                        "min_return_basis_points": 1000,
                        "costs": [money(1000000), money(100000)],
                        "returns": [money(200000), money(2000000)],
                    }
                ]
            },
            CommercialDomain.CUSTOMER_INTELLIGENCE.value: {
                "currency": "USD",
                "max_concentration_basis_points": 8000,
                "accounts": [
                    {
                        "customer_id": "CUST-1",
                        "name": "Customer One",
                        "segment": "active",
                        "contracted_value": money(600000),
                        "grant_ids": ["GRANT-A"],
                    },
                    {
                        "customer_id": "CUST-2",
                        "name": "Customer Two",
                        "segment": "renewal",
                        "contracted_value": money(400000),
                        "grant_ids": ["GRANT-B"],
                    },
                ],
                "grants": [grant_a(), grant_b()],
            },
            CommercialDomain.POLICY_GOVERNANCE.value: {
                "policies": [release_policy(), discount_policy()],
                "requests": [
                    {
                        "domain": "pricing_intelligence",
                        "action": "discount",
                        "magnitude": 1000,
                        "expect_effect": "allow",
                    },
                    {
                        "domain": "pricing_intelligence",
                        "action": "discount",
                        "magnitude": 9000,
                        "expect_effect": "deny",
                    },
                    {
                        "domain": "commercial_packages",
                        "action": "release",
                        "magnitude": 0,
                        "expect_effect": "requires_approval",
                    },
                ],
            },
            CommercialDomain.APPROVAL_INTELLIGENCE.value: {
                "chains": [
                    {
                        **approval_chain("CHAIN-A"),
                        "expect_satisfied": True,
                        "expect_irregularities": 0,
                        "records": approval_records(),
                    },
                    {
                        **approval_chain("CHAIN-Q", quorum=2),
                        "expect_satisfied": False,
                        "expect_irregularities": 0,
                        "records": approval_records(),
                    },
                ]
            },
            CommercialDomain.BUSINESS_EVIDENCE.value: {
                "required_subjects": ["PKG-A", "PROD-A"],
                "entries": [
                    {
                        "evidence_id": "EV-1",
                        "subject_id": "PROD-A",
                        "kind": "product-catalog",
                        "sha256": digest_of("EV-1"),
                    },
                    {
                        "evidence_id": "EV-2",
                        "subject_id": "PKG-A",
                        "kind": "package-seal",
                        "sha256": digest_of("EV-2"),
                    },
                ],
            },
            CommercialDomain.COMMERCIAL_VALIDATION.value: {
                "required_domains": [d.value for d in CommercialDomain]
            },
            CommercialDomain.COMMERCIAL_CERTIFICATION.value: {
                "subject_id": "TEST-SUBJECT",
                "authority": "ENGINEERING-EXECUTION-ONLY",
                "exemptions": [],
                "required_determination": "CERTIFIED",
            },
        }
    )


def valid_config() -> dict[str, Any]:
    """A fully compliant commercial-intelligence configuration mapping."""
    return {"target_id": "TEST-TARGET", "facts": valid_facts()}


def findings_by_check(findings: object) -> dict[str, Any]:
    """Index an iterable of findings by check id (for precise assertions)."""
    return {finding.check_id: finding for finding in findings}  # type: ignore[attr-defined]


__all__ = [
    "digest_of",
    "money",
    "usd",
    "product_a",
    "product_b",
    "product_dev",
    "products",
    "listings",
    "grant_a",
    "grant_b",
    "price_book",
    "documentation",
    "release_policy",
    "discount_policy",
    "approval_chain",
    "approval_records",
    "package_spec",
    "valid_facts",
    "valid_config",
    "findings_by_check",
]
