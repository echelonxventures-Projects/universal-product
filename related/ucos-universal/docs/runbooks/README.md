# Runbooks

Ceremonies: [genesis](genesis.md) (root authority and trust anchors, end of Phase 0).

One runbook per service with an SLO in `spec/slo/`. Every alert links to a section here; the checker fails on a missing link.

| Service | Tier | Universe |
|---|---|---|
| [gateway](gateway.md) | T0 | U63 |
| [context-resolver](context-resolver.md) | T0 | U16 |
| [command-bus](command-bus.md) | T0 | U61 |
| [object-service](object-service.md) | T0 | U04 |
| [outbox-relay](outbox-relay.md) | T0 | U61 |
| [pdp](pdp.md) | T0 | U03 |
| [temporal-triggers](temporal-triggers.md) | T0 | U13 |
| [audit-appender](audit-appender.md) | T0 | U68 |
| [composer](composer.md) | T1 | U58 |
| [activation-agent](activation-agent.md) | T1 | U73 |
| [checkout](checkout.md) | T0 | U24 |
| [order](order.md) | T0 | U26 |
| [payment](payment.md) | T0 | U29 |
| [inventory](inventory.md) | T0 | U34 |
| [fulfillment](fulfillment.md) | T1 | U35 |
| [tax](tax.md) | T0 | U31 |
| [messaging](messaging.md) | T1 | U40 |
