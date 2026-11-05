# Vouchers — the parts only a person can write

## Flows

**Authorise.** A registered issuer defines a voucher kind, value unit, validity and holder scope. The voucher travels through the coupon code writer but remains attributable to its issuing authority.

**Validate and spend.** At checkout the platform validates the issuer, state, dates, tenant and remaining value before applying the voucher. The redemption and funder are recorded for settlement and reconciliation.

**Failure states.** Unknown, expired, revoked, exhausted or out-of-scope vouchers are refused without changing the order or ledger.

## Manual: shopper

Enter an issuer-provided voucher code in the cart. Confirm the issuer, value and resulting discount before placing the order. Contact the issuer if the code is expired or outside its permitted store or audience.

## Manual: store_admin

Accept only voucher kinds and issuers enabled by platform policy. Reconcile voucher redemptions by issuer and funder, and investigate mismatches through the audit trail rather than editing ledger rows.

## Manual: platform_admin

Maintain voucher kinds and issuer permissions in the registry. Configure jurisdiction, unit, validity and settlement rules before granting a partner access to issue or fund vouchers.

## Manual: partner

Use the registered voucher contract to issue codes and reconcile redemptions. Keep issuer references stable so every redemption can be attributed and settled.
