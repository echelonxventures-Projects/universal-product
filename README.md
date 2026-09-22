# UCII Ω∞ — Universal Commerce & Incentive Infrastructure

A constitutional, composable, graph-native, AI-native, multi-tenant, federated commerce infrastructure platform.

## Quick Start

```bash
# Install dependencies
npm install

# Run platform
npm run dev

# Open web UI: http://localhost:3001
```

## Web Portals

| Portal | URL | Purpose |
|--------|-----|---------|
| **Admin** | `/admin` | Full platform management |
| **Merchant** | `/merchant` | Seller earnings and orders |
| **Seller** | `/seller` | Inventory management |

## Features

- **Products** - Create, manage, track inventory
- **Orders** - Full lifecycle management
- **Offers** - Promotions, coupons, cashback
- **Analytics** - Dashboard for all portals
- **Multi-tenant** - Isolated tenant data

## Docker

```bash
docker-compose up
```

## Testing

```bash
npm test              # Unit tests
npx playwright test   # E2E tests
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Testing](docs/TESTING.md)
- [Status](docs/STATUS.md)

## License

Proprietary - EchelonX Ventures
