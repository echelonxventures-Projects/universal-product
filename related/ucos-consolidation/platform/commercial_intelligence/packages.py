"""UCOS-EPIC-014 — Commercial Packages (Terminal T5).

A **commercial package** is the single releasable commercial unit: one product, the quote
that prices it, the licence grant that confers the right to use it, the documentation set
that bounds the promise, the policy decision that governs its release, and — when policy
demands it — the approval outcome that discharges that demand.

Assembly is the point at which governance becomes structural rather than procedural. A
package is ``releasable`` only when **every** constituent agrees:

    * the product is offerable;
    * the quote actually prices that product's SKU, in the package currency;
    * the licence grant licenses that same product;
    * the documentation set is complete for that product; and
    * the policy decision permits release — either outright, or through an approval chain
      that is satisfied and covers every role the policy required.

Anything short of that yields a package that carries its exact reasons and is refused.
There is no path to release that bypasses this function.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.commercial_intelligence.approval import ApprovalOutcome
from platform.commercial_intelligence.documentation import DocumentationSet
from platform.commercial_intelligence.errors import PackageError
from platform.commercial_intelligence.licensing import LicenseGrant
from platform.commercial_intelligence.policy import PolicyDecision
from platform.commercial_intelligence.pricing import Quote
from platform.commercial_intelligence.product import Product
from platform.foundation.contracts import content_hash
from typing import Any


@dataclass(frozen=True, slots=True)
class CommercialPackage:
    """An immutable, content-addressed, governed commercial package."""

    package_id: str
    product: Product
    quote: Quote
    grant: LicenseGrant
    documentation: DocumentationSet
    policy_decision: PolicyDecision
    approval: ApprovalOutcome | None
    releasable: bool
    reasons: tuple[str, ...]
    package_sha256: str

    @property
    def currency(self) -> str:
        return self.quote.currency

    def constituents(self) -> dict[str, str]:
        """The content digest of every constituent — the package's audit surface."""
        return {
            "product": self.product.digest(),
            "quote": self.quote.digest(),
            "grant": self.grant.digest(),
            "documentation": self.documentation.digest(),
            "policy_decision": self.policy_decision.digest(),
            "approval": self.approval.digest() if self.approval is not None else "",
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "package_id": self.package_id,
            "currency": self.currency,
            "product": self.product.to_dict(),
            "quote": self.quote.to_dict(),
            "grant": self.grant.to_dict(),
            "documentation": self.documentation.to_dict(),
            "policy_decision": self.policy_decision.to_dict(),
            "approval": self.approval.to_dict() if self.approval is not None else None,
            "constituents": self.constituents(),
            "releasable": self.releasable,
            "reasons": list(self.reasons),
            "package_sha256": self.package_sha256,
        }

    def digest(self) -> str:
        return self.package_sha256


def _governance_reasons(
    policy_decision: PolicyDecision, approval: ApprovalOutcome | None
) -> list[str]:
    """The reasons, if any, that governance refuses release."""
    reasons: list[str] = []
    if policy_decision.denied:
        detail = "; ".join(policy_decision.reasons) or "policy denies release"
        reasons.append(f"policy governance denies release: {detail}")
        return reasons
    if policy_decision.requires_approval:
        if approval is None:
            reasons.append("policy governance requires approval but no approval outcome is present")
            return reasons
        if approval.rejected:
            reasons.append(f"approval chain {approval.chain_id} was rejected")
        elif not approval.satisfied:
            pending = ", ".join(approval.pending_stages) or "unknown"
            reasons.append(
                f"approval chain {approval.chain_id} is not satisfied — pending: {pending}"
            )
        if approval.irregularities:
            reasons.append(
                f"approval chain {approval.chain_id} carries "
                f"{len(approval.irregularities)} irregularity(ies)"
            )
        satisfied_roles = {stage.role for stage in approval.stages if stage.satisfied}
        uncovered = sorted(set(policy_decision.required_roles) - satisfied_roles)
        if uncovered:
            reasons.append(
                "approval does not cover the role(s) policy required: " + ", ".join(uncovered)
            )
    return reasons


def assemble_package(
    *,
    package_id: str,
    product: Product,
    quote: Quote,
    grant: LicenseGrant,
    documentation: DocumentationSet,
    policy_decision: PolicyDecision,
    approval: ApprovalOutcome | None = None,
) -> CommercialPackage:
    """Assemble and seal a commercial package, computing its releasability fail-closed."""
    if not package_id:
        raise PackageError("a commercial package requires a non-empty package_id")

    reasons: list[str] = []

    if not product.offerable:
        reasons.append(
            f"product {product.product_id} is not offerable "
            f"(state {product.state.value}, {len(product.capabilities)} capabilities)"
        )
    if grant.product_id != product.product_id:
        reasons.append(
            f"licence grant {grant.grant_id} licenses product {grant.product_id}, "
            f"not {product.product_id}"
        )
    if not any(line.sku == product.sku for line in quote.lines):
        reasons.append(f"quote {quote.quote_id} carries no line for the product SKU {product.sku}")
    if quote.net_total.currency != quote.currency:
        reasons.append(
            f"quote {quote.quote_id} totals in {quote.net_total.currency} but declares "
            f"currency {quote.currency}"
        )
    if documentation.subject_id != product.product_id:
        reasons.append(
            f"documentation set documents {documentation.subject_id}, "
            f"not product {product.product_id}"
        )
    completeness = documentation.completeness()
    if not completeness.complete:
        reasons.append("documentation is incomplete — missing: " + ", ".join(completeness.missing))
    missing_capabilities = sorted(set(grant.capabilities) - set(product.capabilities))
    if missing_capabilities:
        reasons.append(
            "licence grant entitles capability the product does not offer: "
            + ", ".join(missing_capabilities)
        )

    reasons.extend(_governance_reasons(policy_decision, approval))

    releasable = not reasons
    core = {
        "package_id": package_id,
        "currency": quote.currency,
        "constituents": {
            "product": product.digest(),
            "quote": quote.digest(),
            "grant": grant.digest(),
            "documentation": documentation.digest(),
            "policy_decision": policy_decision.digest(),
            "approval": approval.digest() if approval is not None else "",
        },
        "releasable": releasable,
        "reasons": reasons,
    }
    return CommercialPackage(
        package_id=package_id,
        product=product,
        quote=quote,
        grant=grant,
        documentation=documentation,
        policy_decision=policy_decision,
        approval=approval,
        releasable=releasable,
        reasons=tuple(reasons),
        package_sha256=content_hash(core),
    )


__all__ = ["CommercialPackage", "assemble_package"]
