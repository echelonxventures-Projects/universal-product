#!/usr/bin/env node
/* LUXORA Platform — the whole platform on this machine, with demo credentials and no outside account.

   npm run demo            starts it (its own database, data/demo.db; your own is not touched)
   npm run demo -- --fresh starts again from nothing

   Payments, email, SMS and carriers are local stand-ins (scripts/sandbox.js). Refuses to run in production. */
"use strict";
const path = require("path"), fs = require("fs");
if (process.env.NODE_ENV === "production") { console.error("The demo never runs in production."); process.exit(1); }
if (typeof process.env.LX_TRUST_PROXY !== "undefined") delete process.env.LX_TRUST_PROXY;
const PORT = Number(process.env.DEMO_PORT || 8787), BOX = Number(process.env.DEMO_SANDBOX_PORT || 8790), SMTP = Number(process.env.DEMO_SMTP_PORT || 8791);
const DB = path.resolve(process.env.DEMO_DB || path.join(__dirname, "..", "data", "demo.db"));
if (process.argv.includes("--fresh")) for (const s of ["", "-wal", "-shm"]) fs.rmSync(DB + s, { force: true });
Object.assign(process.env, { LX_DB: DB, PORT: String(PORT), LUXORA_DEMO_BRANDS: "1" });
for (const k of ["LX_OFFLINE", "LX_DB_DRIVER", "LX_PG_URL", "LX_QUEUE", "LX_REDIS_URL"]) delete process.env[k];
const APP = "http://localhost:" + PORT;

(async () => {
  const accounts = [["Platform admin", "/console.html", "platform@luxora.shop", "platform123"], ["LUXORA store owner (US)", "/console.html?store=luxora", "admin@luxora.shop", "admin123"], ["AURUM store owner (India)", "/console.html?store=aurum", "admin@aurum.shop", "aurum123"], ["VELORA store owner (UAE)", "/console.html?store=velora", "admin@velora.shop", "velora123"],
    ["LUXORA orders staff", "/console.html?store=luxora", "orders@luxora.shop", "Demo-Staff-1"], ["LUXORA support staff", "/console.html?store=luxora", "support@luxora.shop", "Demo-Staff-1"], ["Shopper (LUXORA)", "/index.html?store=luxora", "shopper@luxora.shop", "Demo-Shop-1"], ["Shopper (AURUM)", "/index.html?store=aurum", "shopper@aurum.shop", "Demo-Shop-1"]];
  const home = `<div class="c"><h2>Sign in</h2><table cellpadding="6">${accounts.map(a => `<tr><td>${a[0]}</td><td><a href="${APP + a[1]}">open</a></td><td><code>${a[2]}</code></td><td><code>${a[3]}</code></td></tr>`).join("")}</table></div>
    <div class="c"><h2>Stores</h2><a href="${APP}/index.html?store=luxora">LUXORA</a> (Stripe, PayPal, cash) · <a href="${APP}/index.html?store=aurum">AURUM</a> (Razorpay, cash) · <a href="${APP}/index.html?store=velora">VELORA</a> (Stripe, cash)</div>`;
  const box = require("./sandbox.js").start({ port: BOX, smtpPort: SMTP, app: APP, home });
  try { await box.ready; } catch (e) { console.error("The demo needs ports " + BOX + " and " + SMTP + " free (" + e.message + ")"); process.exit(1); }
  const log = console.log; console.log = () => { };
  require("../server.js");
  const db = require("../lib/db.js"), sec = require("../lib/security.js");
  require("../lib/connect.js").__setTransport(box.transport);
  await require("./demo-data.js").prepare({ db, sec, creds: box.CREDS, smtpPort: SMTP });
  console.log = log;
  console.log("\n  LUXORA is running on this machine\n\n  Start here     " + box.base + "\n  Mailbox        " + box.base + "/mail\n  Payments       " + box.base + "/payments\n");
  const w = Math.max(...accounts.map(a => a[0].length));
  for (const a of accounts) console.log("  " + a[0].padEnd(w) + "  " + a[2].padEnd(22) + "  " + a[3]);
  console.log("\n  Ctrl+C to stop · npm run demo -- --fresh to start again from nothing\n");
})().catch(e => { console.error(e); process.exit(1); });
