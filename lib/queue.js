/* LUXORA Platform - Job queue (sync in dev, async with Redis in prod) */
"use strict";

const isProd = process.env.NODE_ENV === "production";
let jobQueue = null;

// Dev/Test mode: synchronous execution (no Redis needed)
if (!isProd) {
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
// Production mode: async execution with Bull/Redis
else {
  try {
    const Bull = require("bull");
    const Redis = require("ioredis");
    const redis = new Redis(process.env.REDIS_URL || "redis://localhost:6379");
    jobQueue = new Bull("luxora-jobs", { redis });
    jobQueue.on("error", (err) => console.error("Queue error:", err));
  } catch (e) {
    console.error("Redis not configured. Run in dev mode or install Redis.");
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
