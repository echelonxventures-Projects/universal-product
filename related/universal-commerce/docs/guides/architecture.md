# UCII Platform Architecture Reference

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                │
│   Web App │ Mobile SDK │ REST API │ GraphQL │ gRPC │ Webhooks       │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY                                 │
│   Authentication │ Rate Limiting │ Routing │ Load Balancing        │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│  COMMERCE SERVICE │ │  INCENTIVE SERVICE│ │ FINANCIAL SERVICE │
│                   │ │                   │ │                   │
│ • Products        │ │ • Offers          │ │ • Ledger          │
│ • Orders          │ │ • Coupons         │ │ • Transactions    │
│ • Catalog         │ │ • Loyalty         │ │ • Payouts         │
│ • Cart            │ │ • Promotions      │ │ • Billing         │
└───────────────────┘ └───────────────────┘ └───────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│   EVENT BUS       │ │   POLICY ENGINE   │ │ WORKFLOW ENGINE   │
│                   │ │                   │ │                   │
│ • Pub/Sub         │ │ • Rules           │ │ • State Machine   │
│ • Async Processing│ │ • RBAC/ABAC       │ │ • Workflows       │
│ • Integration     │ │ • Governance      │ │ • Automations     │
└───────────────────┘ └───────────────────┘ └───────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                   │
│   PostgreSQL │ Redis │ S3 │ Elasticsearch │ Graph DB (optional)   │
└─────────────────────────────────────────────────────────────────────┘
```

## Service Contracts

### Commerce Service
- CRUD operations for products
- Order lifecycle management
- Inventory tracking

### Incentive Service
- Offer creation and management
- Coupon validation and redemption
- Loyalty program administration

### Financial Service
- Double-entry ledger
- Transaction processing
- Settlement and payout management

## Event Sourcing

Events are the source of truth:
- `commerce.product.created`
- `commerce.order.completed`
- `incentive.coupon.redeemed`

## Caching Strategy

- Redis for session data
- Query caching at application layer
- CDN for static assets
