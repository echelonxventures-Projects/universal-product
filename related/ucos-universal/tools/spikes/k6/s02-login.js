// Spike S-02 (ADR-021): identity provider load. Target: 5,000 logins/s per cell, p99 < 800 ms, 0% cross-tenant tokens.
// Run: k6 run -e IDP=https://idp.sandbox.example -e TENANTS=100 tools/spikes/k6/s02-login.js
import http from 'k6/http';
import { check } from 'k6';
import encoding from 'k6/encoding';

const IDP = __ENV.IDP;
const TENANTS = parseInt(__ENV.TENANTS || '100', 10);

export const options = {
  scenarios: {
    logins: {
      executor: 'ramping-arrival-rate',
      startRate: 100, timeUnit: '1s', preAllocatedVUs: 2000, maxVUs: 8000,
      stages: [
        { target: 1000, duration: '2m' },
        { target: 5000, duration: '5m' },
        { target: 5000, duration: '10m' },
        { target: 0, duration: '1m' },
      ],
    },
  },
  thresholds: {
    'http_req_duration{kind:token}': ['p(99)<800'],
    'checks{check:issuer-matches-tenant}': ['rate==1'],
    http_req_failed: ['rate<0.001'],
  },
};

export default function () {
  const tenant = `t${Math.floor(Math.random() * TENANTS)}`;
  const user = `load-${Math.floor(Math.random() * 1000)}`;
  const res = http.post(`${IDP}/realms/${tenant}/protocol/openid-connect/token`, {
    grant_type: 'password', client_id: 'load-test', username: user, password: __ENV.PASSWORD || 'load-test-password',
  }, { tags: { kind: 'token' } });
  check(res, { 'token issued': (r) => r.status === 200 });
  if (res.status === 200) {
    const payload = JSON.parse(encoding.b64decode(res.json('access_token').split('.')[1], 'rawurl', 's'));
    check(payload, { 'issuer-matches-tenant': (p) => p.iss.endsWith(`/realms/${tenant}`) }, { check: 'issuer-matches-tenant' });
  }
}
