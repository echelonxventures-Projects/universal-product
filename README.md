# UCII Ω∞ — Universal Commerce & Incentive Infrastructure

## Overview

UCII is a constitutional, composable, graph-native, AI-native, multi-tenant, federated commerce infrastructure platform.

### What Can UCII Do?

| Category | Capabilities |
|----------|---------------|
| **Commerce** | B2B, B2C, D2C, Marketplace, Retail Media |
| **Incentives** | Offers, Coupons, Cashback, Loyalty, Rewards, Affiliate |
| **Finance** | Payments, Settlement, Payouts, Billing |
| **AI** | AI Commerce, AI Offers, AI Pricing, Autonomous Agents |
| **Federation** | Multi-tenant, Cross-marketplace, Cross-country |

## Quick Start

```bash
npm install
npm run dev
```

## Project Structure

```
ucii-platform/
├── core/                    # Core infrastructure
│   ├── types/              # Shared type definitions
│   ├── event-bus/          # Async event system
│   ├── policy-engine/      # Policy evaluation
│   ├── workflow-engine/    # Workflow execution
│   └── config-manager/     # Configuration loading
├── domains/                 # Domain models
│   ├── types/
│   │   ├── commerce.ts
│   │   ├── incentive.ts
│   │   └── financial.ts
├── services/                # Domain services
│   ├── commerce/
│   ├── incentive/
│   ├── financial/
│   └── handlers/
├── infrastructure/          # Infrastructure as Code
│   ├── terraform/
│   ├── k8s/
│   └── ci-cd/
├── sdk/                     # Client SDKs
├── tests/                   # Test suite
├── docs/                    # Documentation
└── config/                  # Configuration files
```

## API Endpoints

### Products
```bash
POST /products     # Create product
GET  /products     # List products
GET  /products/:id # Get product
```

### Orders
```bash
POST /orders      # Create order
GET  /orders      # List orders
PUT  /orders/:id  # Update order
```

### Incentives
```bash
POST /offers            # Create offer
GET  /offers            # List offers
POST /coupons/validate  # Validate coupon
```

## Constitutional Principles

- **Registry over Hardcoding** — All configuration in registries
- **Configuration over Code** — Behavior controlled via config
- **Policies over Branching Logic** — Rules as first-class citizens
- **Events over Coupling** — Async, decoupled communication
- **Federation over Monolith** — Distributed, scalable architecture

## Documentation

- [Quick Start](./docs/guides/quick-start.md)
- [Architecture](./docs/guides/architecture.md)
- [API Reference](./docs/api/README.md)
- [Production Deployment](./docs/production-deployment.md)

## License

Proprietary - EchelonX Ventures
