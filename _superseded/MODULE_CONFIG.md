# Module Configuration Guide

## Quick Start

```bash
# Run database migration
node migrate.js

# Start server on port 8787
PORT=8787 npm start
# or: PORT=8787 node server.js

# Visit admin panel
open http://localhost:8787/admin.html
```

---

## 1. Affiliate Network

### Features
- Multi-network affiliate tracking
- Click & conversion tracking
- Flexible commission rules (flat, percentage, tiered)
- Automated payouts
- Performance reports

### Configuration

#### Create a Network
```javascript
POST /affiliate/networks
{
  "name": "Default Network",
  "default_commission_pct": 5.0,
  "cookie_days": 30,
  "attribution_model": "last_touch"
}
```

#### Add Affiliate
```javascript
POST /affiliate/affiliates
{
  "name": "John Doe",
  "email": "john@example.com",
  "tier": "standard"
}
```

#### Record a Conversion
```javascript
POST /affiliate/conversion
{
  "affiliate_id": 1,
  "order_id": 123,
  "commission_pct": 5.0
}
```

#### Commission Rules
```javascript
POST /affiliate/rules
{
  "network_id": 1,
  "name": "Premium Partners",
  "commission_value": 10.0,
  "tier": "gold",
  "applies_to": "products"
}
```

---

## 2. Sitemap & SEO

### Features
- Auto-generated XML sitemaps
- Multi-tenant support
- Dynamic product/category indexing
- Scheduled regeneration

### Configuration

```javascript
PUT /sitemap/config
{
  "hostname": "https://yourstore.com",
  "max_per_file": 50000,
  "enabled": true
}
```

### Generate Sitemap
```bash
curl -X POST http://localhost:3000/sitemap/generate
```

### Access Sitemap
```
GET /sitemap.xml
```

---

## 3. Shipping & Tracking

### Features
- Multi-carrier integration (FedEx, UPS, DHL)
- Real-time tracking
- Rate quotes
- Label generation

### Configure Carrier APIs

```javascript
POST /shipping/providers/config
{
  "provider_id": "fedex",
  "config": {
    "apiKey": "YOUR_FEDEx_API_KEY",
    "accountId": "YOUR_ACCOUNT_ID"
  }
}
```

### Track Shipment
```javascript
POST /shipping/track
{
  "tracking_number": "1234567890",
  "order_id": 123,
  "origin": {"city": "NYC", "country": "US"},
  "destination": {"city": "LA", "country": "US"}
}
```

### Get Rate Quote
```javascript
POST /shipping/quote
{
  "origin": {"zip": "10001", "country": "US"},
  "destination": {"zip": "90001", "country": "US"},
  "weight": 2.5
}
```

### Carrier API Credentials

#### FedEx
- Account ID
- API Key
- Secret Key

#### UPS
- API Key
- Account Number

#### DHL
- Site ID
- Password

---

## 4. Enhanced Helpdesk

### Features
- Live chat integration
- SMS support
- Agent availability status
- Multi-channel tickets

### Configure Chat

```javascript
POST /helpdesk/chat
{
  "name": "Customer Name",
  "email": "customer@example.com",
  "message": "Hello, I need help with..."
}
```

### Send SMS
```javascript
POST /helpdesk/sms
{
  "phone": "+1234567890",
  "message": "Your order has shipped!"
}
```

### Update Agent Status
```javascript
POST /helpdesk/agents/status
{
  "agent_id": "agent-123",
  "status": "online"
}
```

---

## Integration Points

### Affiliate → Orders
Automatically track when customers use affiliate links.

### Shipping → Orders
```javascript
POST /orders/ship
{
  "order_id": 123,
  "tracking_number": "1234567890",
  "provider_id": "fedex"
}
```

### Helpdesk → Tickets
Automatically create tickets from:
- Customer emails
- Live chat sessions
- SMS messages
- Social media

---

## Registry Configuration

All modules use the platform's registry system:

```javascript
// View available registries
GET /api/goip/registry/goipDistribution

// Add new affiliate channel
POST /api/meta/lists
{
  "name": "affiliateChannels",
  "items": [{"key": "blog", "name": "Blog"}, {"key": "social", "name": "Social"}]
}
```

---

## Webhooks

### Affiliate Events
```
POST /webhooks/affiliate/click
POST /webhooks/affiliate/conversion
POST /webhooks/affiliate/payout
```

### Shipping Events
```
POST /webhooks/shipping/tracking_update
POST /webhooks/shipping/label_created
```

### Helpdesk Events
```
POST /webhooks/helpdesk/ticket_created
POST /webhooks/helpdesk/ticket_reply
```

---

## Example Use Cases

### Affiliate Marketing Campaign
1. Create affiliate network
2. Add affiliates with unique codes
3. Share tracking links
4. Track clicks → conversions
5. Approve commissions
6. Process payouts

### Multi-Carrier Shipping
1. Configure FedEx/UPS/DHL credentials
2. Get real-time quotes
3. Create shipment with tracking
4. Monitor delivery status
5. Generate labels automatically

### Live Customer Support
1. Add agents and set status
2. Start live chat sessions
3. Convert chats to tickets
4. Track resolution times
5. Monitor CSAT scores

---

## Monitoring

### Affiliate Health
```javascript
GET /affiliate/reports
// Returns: affiliates, sales, commissions
```

### Shipping Status
```javascript
GET /shipping/providers
// Returns: configured carriers, status
```

### Helpdesk Performance
```javascript
GET /helpdesk/tickets?status=open
// Returns: active tickets by priority
```

---

## Troubleshooting

### Affiliate tracking not working
- Check `affiliate_clicks` table for recorded clicks
- Verify affiliate codes are active
- Confirm conversion tracking URL is set

### Sitemap not generating
- Check `sitemap_config.enabled` is true
- Verify hostname is set correctly
- Check file permissions

### Shipping API errors
- Verify API credentials
- Check provider status in `shipping_providers`
- Review carrier API documentation

### Helpdesk chat not connecting
- Check agent availability status
- Verify websocket connection
- Check browser console for errors

---

## Support

For advanced configuration:
- See `lib/affiliate.js` for commission logic
- See `lib/shipping.js` for carrier integrations
- See `lib/helpdesk.js` for ticket workflows
