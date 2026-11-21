// Spike S-04 (ADR-001): runtime interpretation performance. Target: 2,000 rps AddLine, p99 < 150 ms end to end.
// Run against a reference cell with the d2c-in-ae blueprint and seeded listings:
//   k6 run -e API=https://bazaar.sandbox.example/api/v1 -e TOKEN=... tools/spikes/k6/s04-addline.js
import http from 'k6/http';
import { check } from 'k6';

const API = __ENV.API;
const HEADERS = { Authorization: `Bearer ${__ENV.TOKEN}`, 'Content-Type': 'application/json' };

export const options = {
  scenarios: {
    addline: {
      executor: 'constant-arrival-rate', rate: 2000, timeUnit: '1s', duration: '15m',
      preAllocatedVUs: 1000, maxVUs: 4000,
    },
  },
  thresholds: {
    'http_req_duration{op:addLine}': ['p(99)<150'],
    http_req_failed: ['rate<0.001'],
  },
};

export function setup() {
  const carts = [];
  for (let i = 0; i < 500; i++) {
    const r = http.post(`${API}/commerce/carts`, JSON.stringify({}), {
      headers: { ...HEADERS, 'Idempotency-Key': `s04-cart-${i}-${Date.now()}` },
    });
    carts.push(r.json('id'));
  }
  return { carts };
}

export default function (data) {
  const cart = data.carts[Math.floor(Math.random() * data.carts.length)];
  const sku = `SKU-LOAD-${Math.floor(Math.random() * 10000)}`;
  const res = http.post(`${API}/commerce/carts/${cart}:addLine`, JSON.stringify({ unit: sku, qty: 1 }), {
    headers: { ...HEADERS, 'Idempotency-Key': `${cart}-${sku}-${__ITER}-${__VU}` },
    tags: { op: 'addLine' },
  });
  check(res, { 'line added': (r) => r.status === 200 });
}
