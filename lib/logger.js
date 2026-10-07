/* LUXORA Platform - Structured logger (JSON in prod, plain in dev) */
"use strict";

const isProd = process.env.NODE_ENV === "production";

module.exports = {
  info: (msg, data) => {
    if (isProd) {
      console.log(JSON.stringify({ ts: new Date().toISOString(), level: "info", msg, ...(data || {}) }));
    } else {
      console.log(`[INFO] ${msg} ${JSON.stringify(data || {})}`);
    }
  },
  error: (msg, data) => {
    if (isProd) {
      console.error(JSON.stringify({ ts: new Date().toISOString(), level: "error", msg, ...(data || {}) }));
    } else {
      console.error(`[ERROR] ${msg} ${JSON.stringify(data || {})}`);
    }
  }
};
