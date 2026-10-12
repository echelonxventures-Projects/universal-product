/* LUXORA Platform - Job queue (inline by default, Bull/Redis when configured) */
"use strict";

/* The driver is DATA, not a NODE_ENV branch. config.js resolves it env → stored
   platform_settings.runtime → default (inline), the same spine every other concern uses,
   and test/smoke asserts the default is inline. Keying this on NODE_ENV instead meant a
   production boot that never opted into redis still constructed Bull + ioredis against
   localhost:6379 and flooded the log with ECONNREFUSED forever — the queue is opted into
   with LX_QUEUE=redis (or Platform → Runtime), never by running in production. */
const driver = (() => { try { return require("./config.js").driverOf("queue"); } catch (e) { return "inline"; } })();
let jobQueue = null;

// Inline (the default): handlers run synchronously in-process — dev, test, and any
// production boot that has not opted into redis. webhook delivery is an adapters.js
// concern, so the local report pipeline stays inline rather than silently double-running.
if (driver !== "redis") {
  const jobs = [];
  const handlers = {};

  const MockQueue = {
    add: async function (name, data, opts = {}) {
      const id = Date.now() + Math.random();
      jobs.push({ id, name, data, opts });
      // Execute immediately in dev
      if (handlers[name]) {
        try {
          await handlers[name](data);
        } catch (e) {
          console.error(`Job ${name} failed:`, e.message);
        }
      }
      return { id };
    },
    process: function (name, concurrency, handler) {
      handlers[name] = handler;
    },
    // Helper for tests to clear pending jobs
    empty: async function () {
      const pending = [...jobs];
      jobs.length = 0;
      return pending;
    }
  };
  jobQueue = MockQueue;
}
// Redis (LX_QUEUE=redis): Bull over the url config.js resolved — LX_REDIS_URL or stored
// params, never a hard-coded localhost. require failure means a broken install (bull and
// ioredis are declared dependencies), so report it rather than degrading silently.
else {
  try {
    const Bull = require("bull");
    let url = null;
    try { const q = require("./config.js").get("queue"); url = q && q.params && q.params.url; } catch (e) { }
    url = url || process.env.REDIS_URL || "redis://localhost:6379";
    /* Bull opens its own connections (command + blocking reader) and builds each one from
       these options — passing it a live ioredis instance instead leaves Bull's internal
       clients on the localhost:6379 default, silently splitting the queue across two
       hosts. One parsed url, shared with the RESP client in adapters.js. */
    const conn = require("./adapters.js").parseRedisUrl(url) || { host: "127.0.0.1", port: 6379 };
    jobQueue = new Bull("luxora-jobs", {
      redis: { host: conn.host, port: conn.port, db: conn.db, ...(conn.password ? { password: conn.password } : {}) }
    });
    /* a dead redis reconnects on a timer and re-emits the same error every few seconds —
       log it once, with the url the queue is actually pointed at, and let Bull keep
       retrying instead of filling the log with identical lines. */
    let warned = false;
    jobQueue.on("error", (err) => {
      if (warned) return;
      warned = true;
      console.error(`Queue error (redis ${url} unreachable; Bull retries in the background):`, err.message);
    });
  } catch (e) {
    console.error("Redis driver selected (LX_QUEUE=redis) but bull is unavailable:", e.message);
    process.exit(1);
  }
}

async function addJob(name, data, opts = {}) {
  return jobQueue.add(name, data, opts);
}

function processJob(name, handler) {
  if (jobQueue) {
    jobQueue.process(name, 5, handler);
  }
}

// In dev mode, processors run synchronously, so startProcessors does nothing
function startProcessors() {}

module.exports = { addJob, processJob, startProcessors };
