const express = require('express');
const path = require('path');

const app = express();
app.use(express.json());
const PORT = process.env.PORT || 5566;

// ============================================================================
// DEMO DATA (All Systems)
// ============================================================================

const products = [
  { id: 'prod-001', sku: 'WIDGET-PREMIUM', name: 'Premium Widget', status: 'active', price: 99.99, inventory: 150 },
  { id: 'prod-002', sku: 'WIDGET-BASIC', name: 'Basic Widget', status: 'active', price: 49.99, inventory: 300 },
  { id: 'prod-003', sku: 'WIDGET-DELUXE', name: 'Deluxe Widget', status: 'active', price: 149.99, inventory: 75 },
];

const orders = [
  { id: 'ord-001', orderNumber: 'ORD-100001', customerId: 'cust-001', status: 'delivered', total: 234.50, items: 2, createdAt: '2026-09-20' },
  { id: 'ord-002', orderNumber: 'ORD-100002', customerId: 'cust-002', status: 'shipped', total: 156.75, items: 1, createdAt: '2026-09-21' },
  { id: 'ord-003', orderNumber: 'ORD-100003', customerId: 'cust-003', status: 'processing', total: 89.00, items: 1, createdAt: '2026-09-22' },
];

const offers = [
  { id: 'off-001', code: 'SUMMER25', name: 'Summer 25% Off', type: 'discount', value: 25, currency: 'USD', status: 'active' },
  { id: 'off-002', code: 'WELCOME10', name: 'Welcome Cashback', type: 'cashback', value: 10, currency: 'USD', status: 'active' },
];

const tenants = {
  'tenant-123': { id: 'tenant-123', name: 'Demo Corp', status: 'active' },
};

// ============================================================================
// API ROUTES
// ============================================================================

// Products
app.get('/api/products', (req, res) => {
  res.json({ products });
});

app.post('/api/products', (req, res) => {
  const product = {
    id: `prod-${Date.now()}`,
    sku: req.body.sku,
    name: req.body.name,
    status: 'active',
    price: req.body.price || 0,
    inventory: req.body.inventory || 0,
  };
  products.push(product);
  res.json(product);
});

// Orders
app.get('/api/orders', (req, res) => {
  res.json({ orders });
});

app.post('/api/orders', (req, res) => {
  const order = {
    id: `ord-${Date.now()}`,
    orderNumber: `ORD-${100000 + orders.length}`,
    customerId: req.body.customerId || 'cust-001',
    status: 'pending',
    total: req.body.total || 0,
    items: req.body.items || 1,
    createdAt: new Date().toISOString().split('T')[0],
  };
  orders.push(order);
  res.json(order);
});

// Offers
app.get('/api/offers', (req, res) => {
  res.json({ offers });
});

app.post('/api/offers', (req, res) => {
  const offer = {
    id: `off-${Date.now()}`,
    code: req.body.code,
    name: req.body.name,
    type: req.body.type || 'discount',
    value: req.body.value || 0,
    currency: 'USD',
    status: 'active',
  };
  offers.push(offer);
  res.json(offer);
});

// Health & System Status
app.get('/api/system/health', (req, res) => {
  res.json({
    status: 'healthy',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
    domains_loaded: 195,
    layers_complete: 25,
  });
});

// ============================================================================
// FRONTEND (Served Directly)
// ============================================================================

function sendPage(req, res, title, content) {
  const html = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>${title} - UCII Platform</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f3f4f6; }
    .sidebar { width: 260px; background: #1e40af; color: white; position: fixed; height: 100vh; padding: 20px; }
    .sidebar h1 { font-size: 20px; margin-bottom: 30px; }
    .sidebar a { display: block; color: #bfdbfe; text-decoration: none; padding: 10px 15px; margin: 5px 0; border-radius: 4px; }
    .sidebar a:hover, .sidebar a.active { background: #1e3a8a; }
    .main { margin-left: 260px; padding: 30px; }
    .header { background: white; padding: 15px 30px; margin: -30px -30px 30px; border-bottom: 1px solid #e5e7eb; }
    .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .stat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px; }
    .stat-card { background: white; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .stat-value { font-size: 32px; font-weight: bold; color: #1e40af; }
    .stat-label { color: #6b7280; font-size: 14px; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }
    th { background: #f9fafb; font-weight: 600; color: #374151; }
    .btn { background: #1e40af; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
    .btn:hover { background: #1e3a8a; }
    input, select { width: 100%; padding: 10px; border: 1px solid #d1d5db; border-radius: 4px; margin: 5px 0; }
    .badge { padding: 4px 8px; border-radius: 12px; font-size: 12px; }
    .badge-success { background: #dcfce7; color: #166534; }
    .badge-processing { background: #fef3c7; color: #92400e; }
    .badge-blue { background: #dbeafe; color: #1e40af; }
  </style>
</head>
<body>
  <div class="sidebar">
    <h1>UCII ${title}</h1>
    <a href="/admin">Dashboard</a>
    <a href="/admin/products">Products</a>
    <a href="/admin/orders">Orders</a>
    <a href="/admin/offers">Offers</a>
  </div>
  <div class="main">
    <div class="header">
      <h2>${title} Portal</h2>
    </div>
    ${content}
  </div>
</body>
</html>`;
  res.send(html);
}

// Admin Dashboard
app.get('/admin', (req, res) => {
  const content = `
    <h1>Admin Dashboard</h1>
    <div class="stat-grid">
      <div class="stat-card">
        <div class="stat-value">${products.length}</div>
        <div class="stat-label">Total Products</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${orders.length}</div>
        <div class="stat-label">Total Orders</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${offers.length}</div>
        <div class="stat-label">Active Offers</div>
      </div>
    </div>
    <div class="card">
      <h3>Recent Orders</h3>
      <table>
        <thead><tr><th>Order #</th><th>Status</th><th>Total</th><th>Customer</th></tr></thead>
        <tbody>
          ${orders.map(o => `
            <tr>
              <td>${o.orderNumber}</td>
              <td><span class="badge badge-${o.status === 'delivered' ? 'success' : 'processing'}">${o.status}</span></td>
              <td>$${o.total.toFixed(2)}</td>
              <td>${o.customerId}</td>
            </tr>`).join('')}
        </tbody>
      </table>
    </div>
    <div class="card">
      <h3>System Health</h3>
      <div id="system-status">Loading...</div>
    </div>
    <script>
      fetch('/api/system/health').then(r => r.json()).then(d => {
        document.getElementById('system-status').innerHTML = 
          'Status: ' + d.status + ' | Domains: ' + d.domains_loaded + ' | Layers: ' + d.layers_complete;
      });
    </script>
  `;
  sendPage(req, res, 'Admin', content);
});

// Products Page
app.get('/admin/products', (req, res) => {
  const content = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
      <h1>Products</h1>
      <button class="btn" onclick="addProduct()">+ New Product</button>
    </div>
    <div class="card">
      <table>
        <thead><tr><th>SKU</th><th>Name</th><th>Price</th><th>Inventory</th><th>Status</th><th>Actions</th></tr></thead>
        <tbody id="products-table">
          ${products.map(p => `
            <tr>
              <td>${p.sku}</td>
              <td>${p.name}</td>
              <td>$${p.price}</td>
              <td>${p.inventory}</td>
              <td><span class="badge badge-success">${p.status}</span></td>
              <td><a style="color:#1e40af">Edit</a></td>
            </tr>`).join('')}
        </tbody>
      </table>
    </div>
    <script>
      function addProduct() {
        fetch('/api/products', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({sku: 'NEW-' + Date.now(), name: 'New Product', price: 29.99, inventory: 100})
        }).then(() => location.reload());
      }
    </script>
  `;
  sendPage(req, res, 'Admin', content);
});

// Orders Page
app.get('/admin/orders', (req, res) => {
  const content = `
    <h1>Orders</h1>
    <div class="card">
      <table>
        <thead><tr><th>Order #</th><th>Status</th><th>Total</th><th>Items</th><th>Date</th></tr></thead>
        <tbody>
          ${orders.map(o => `
            <tr>
              <td>${o.orderNumber}</td>
              <td><span class="badge badge-${o.status === 'delivered' ? 'success' : 'processing'}">${o.status}</span></td>
              <td>$${o.total.toFixed(2)}</td>
              <td>${o.items}</td>
              <td>${o.createdAt}</td>
            </tr>`).join('')}
        </tbody>
      </table>
    </div>
  `;
  sendPage(req, res, 'Admin', content);
});

// Offers Page
app.get('/admin/offers', (req, res) => {
  const content = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
      <h1>Offers & Promotions</h1>
      <button class="btn" onclick="createOffer()">+ New Offer</button>
    </div>
    <div class="card">
      <table>
        <thead><tr><th>Code</th><th>Name</th><th>Type</th><th>Value</th><th>Status</th></tr></thead>
        <tbody>
          ${offers.map(o => `
            <tr>
              <td><code>${o.code}</code></td>
              <td>${o.name}</td>
              <td>${o.type}</td>
              <td>${o.value} ${o.currency}</td>
              <td><span class="badge badge-success">${o.status}</span></td>
            </tr>`).join('')}
        </tbody>
      </table>
    </div>
    <script>
      function createOffer() {
        fetch('/api/offers', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({code: 'PROMO-' + Date.now(), name: 'Promotion', type: 'discount', value: 10})
        }).then(() => location.reload());
      }
    </script>
  `;
  sendPage(req, res, 'Admin', content);
});

// Merchant Portal
app.get('/merchant', (req, res) => {
  const content = `
    <h1>Merchant Dashboard</h1>
    <div class="stat-grid">
      <div class="stat-card">
        <div class="stat-value">${products.length}</div>
        <div class="stat-label">My Products</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${orders.length}</div>
        <div class="stat-label">Orders</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">$${(orders.reduce((a,b) => a + b.total, 0)).toFixed(2)}</div>
        <div class="stat-label">Earnings</div>
      </div>
    </div>
    <div class="card">
      <h3>Recent Activity</h3>
      <p>Orders received in the last 30 days: <strong>${orders.length}</strong></p>
    </div>
  `;
  sendPage(req, res, 'Merchant', content);
});

// Seller Portal
app.get('/seller', (req, res) => {
  const content = `
    <h1>Seller Dashboard</h1>
    <div class="stat-grid">
      <div class="stat-card">
        <div class="stat-value">${products.reduce((a,p) => a + p.inventory, 0)}</div>
        <div class="stat-label">Total Inventory</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${products.length}</div>
        <div class="stat-label">SKUs</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">$${(products.reduce((a,p) => a + (p.price * p.inventory), 0)).toFixed(2)}</div>
        <div class="stat-label">Inventory Value</div>
      </div>
    </div>
    <div class="card">
      <h3>Inventory Alert</h3>
      <p>All items are currently in stock.</p>
    </div>
  `;
  sendPage(req, res, 'Seller', content);
});

// Start Server
app.listen(PORT, () => {
  console.log(`✅ UCII Platform running on http://localhost:${PORT}`);
  console.log(`\n📍 URLs:`);
  console.log(`   Admin:    http://localhost:${PORT}/admin`);
  console.log(`   Merchant: http://localhost:${PORT}/merchant`);
  console.log(`   Seller:   http://localhost:${PORT}/seller`);
  console.log(`\n🔑 Demo Credentials (Simulated):`);
  console.log(`   Admin:    admin@echelonx.com`);
  console.log(`   Merchant: merchant@example.com`);
  console.log(`   Seller:   seller@example.com`);
});
