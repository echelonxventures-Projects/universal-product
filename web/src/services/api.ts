// API Client for UCII Platform
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000/api';

interface RequestOptions {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, headers = {} } = options;

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || `HTTP ${response.status}`);
  }

  return response.json();
}

// Products
export const products = {
  list: (tenantId: string) => request(`/products?tenantId=${tenantId}`),
  get: (id: string) => request(`/products/${id}`),
  create: (data: unknown) => request('/products', { method: 'POST', body: data }),
  update: (id: string, data: unknown) => request(`/products/${id}`, { method: 'PUT', body: data }),
  delete: (id: string) => request(`/products/${id}`, { method: 'DELETE' }),
};

// Orders
export const orders = {
  list: (tenantId: string) => request(`/orders?tenantId=${tenantId}`),
  get: (id: string) => request(`/orders/${id}`),
  create: (data: unknown) => request('/orders', { method: 'POST', body: data }),
  updateStatus: (id: string, status: string) => request(`/orders/${id}/status`, { method: 'PUT', body: { status } }),
};

// Offers
export const offers = {
  list: (tenantId: string) => request(`/offers?tenantId=${tenantId}`),
  get: (id: string) => request(`/offers/${id}`),
  create: (data: unknown) => request('/offers', { method: 'POST', body: data }),
  activate: (id: string) => request(`/offers/${id}/activate`, { method: 'POST' }),
};

// Coupons
export const coupons = {
  validate: (code: string) => request(`/coupons/validate`, { method: 'POST', body: { code } }),
  redeem: (id: string, orderId: string) => request(`/coupons/${id}/redeem`, { method: 'POST', body: { orderId } }),
};

export default { request, products, orders, offers, coupons };
