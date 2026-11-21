# UCII API Documentation

## Overview

The UCII platform exposes REST and GraphQL APIs for commerce and incentive operations.

## Base URL

```
https://api.ucii.io/v1
```

## Authentication

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "X-Tenant-ID: tenant-123" \
     https://api.ucii.io/v1/products
```

## Endpoints

### Commerce

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /products | List products |
| POST | /products | Create product |
| GET | /orders | List orders |
| POST | /orders | Create order |

### Incentives

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /offers | List offers |
| POST | /offers | Create offer |
| POST | /coupons/validate | Validate coupon |

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Rate Limited |
| 500 | Server Error |
