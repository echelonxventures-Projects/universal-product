/* LUXORA Platform - Prometheus metrics (only in production) */
"use strict";

const isProd = process.env.NODE_ENV === "production";

let trackRequest = () => {};
let getMetrics = () => "";
let snapshot = () => ({});

if (isProd) {
  try {
    const client = require("prom-client");
    // Collect default Node.js metrics
    client.collectDefaultMetrics();

    // Custom counter for API requests
    const apiRequests = new client.Counter({
      name: "luxora_api_requests_total",
      help: "Total number of API requests",
      labelNames: ["endpoint", "status"]
    });

    // Custom gauge for active tenants
    const activeTenants = new client.Gauge({
      name: "luxora_active_tenants",
      help: "Number of active tenant sessions"
    });

    trackRequest = (tenant, method, pathname, status, latency) => {
      const endpoint = pathname.split("/").slice(0, 3).join("/");
      apiRequests.inc({ endpoint, status: status.toString() });
      // You could add latency histogram here if needed
    };

    snapshot = (tenantId) => {
      // Return current metrics snapshot
      return { activeTenants: activeTenants.getValue() };
    };

    getMetrics = () => {
      return client.register.metrics();
    };
  } catch (e) {
    console.error("Metrics init failed:", e.message);
  }
}

// Fallback for dev/test (no-op)
module.exports = { trackRequest, getMetrics, snapshot, record: trackRequest };
