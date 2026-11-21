// Universe-default policies shipped by Phase 1 packs (layer: universe-default). Tenants extend in their own layer.

@id("commerce.cart.owner-only")
permit (principal, action in [Action::"commerce:GetCart", Action::"commerce:AddLine", Action::"commerce:UpdateLineQuantity", Action::"commerce:RemoveLine", Action::"commerce:ApplyCoupon", Action::"commerce:RemoveCoupon"], resource is Commerce::Cart)
when { resource.buyer == principal.party || (resource has sessionToken && resource.sessionToken == context.session) };

@id("commerce.checkout.agent-confirmation") @obligation("requireConfirmation:human")
permit (principal is Agent, action == Action::"commerce:ConfirmAndPay", resource is Commerce::Checkout)
when { principal.authority.actions.contains(action) && resource.buyer == principal.onBehalfOf };

@id("order.buyer-read")
permit (principal, action in [Action::"order:GetOrder", Action::"order:RequestReturn", Action::"order:CancelOrder"], resource is Order::Order)
when { resource.buyer == principal.party };

@id("order.support-read") @obligation("mask:contact,purpose:customer-support")
permit (principal in Role::"support-agent", action == Action::"order:GetOrder", resource is Order::Order)
when { context.purpose == "customer-support" };

@id("catalog.seller-own")
permit (principal in Role::"seller", action in [Action::"catalog:CreateListing", Action::"catalog:UpdateListing", Action::"catalog:SubmitForReview", Action::"catalog:PauseListing"], resource is Catalog::Listing)
when { resource.seller == principal.organization && principal.organization.standing == "good" };

@id("catalog.operator-moderation")
permit (principal in Role::"catalog-admin", action in [Action::"catalog:ApproveListing", Action::"catalog:RejectListing", Action::"catalog:SuppressListing", Action::"catalog:PublishListing"], resource is Catalog::Listing);

@id("payment.refund-approval") @obligation("stepUpAuth:AAL2,requireReason")
permit (principal in Role::"finance-operator", action == Action::"payment:Refund", resource is Payment::PaymentIntent)
when { context.refund.amountMinor <= principal.limits.refundMinor };

@id("pricing.bulk-change-governed")
forbid (principal, action == Action::"pricing:UpsertPriceEntries", resource)
when { context.batchSize > 1000 && !(context has proposal) };
