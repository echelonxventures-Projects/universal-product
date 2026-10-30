/* LUXORA Platform — technology discovery adapters (PR-053).
   A discovery adapter reads what one kind of source publishes and turns it into entries the
   registry ingests (lib/technology.js ingest). It is keyed by protocol, and a source in
   lib/seed/technology.json names the protocol it speaks; a new kind of feed is a new adapter
   registered here (or by any module through register), not a change to the governance core.

   The contract: discover(payload, source) → [{ item, version, channel?, artifacts?, metadata?,
   dependencies?, advisories?, newItem? }]. An adapter is a pure function of its payload — it never
   fetches, never writes and never says a release is compatible or approved; the registry checks
   every entry it returns against the source's trust and the category's metadata contract.
   fetch(source, o) is optional: it returns { payload, location, fetchedAt, payloadSha256 } for
   scripts/technology.js discover --fetch, and is the only place a network is touched. */
"use strict";

const crypto = require("crypto");
const ADAPTERS = new Map();
const fail = m => Object.assign(new Error(m), { status: 400, code: "technology_untrusted" });

function register(protocol, impl) {
  if (typeof protocol !== "string" || !/^[a-z][a-z0-9-]{0,63}$/.test(protocol)) throw fail("An adapter's protocol is a lower-case key: " + protocol);
  if (!impl || typeof impl.discover !== "function") throw fail("An adapter has a discover(payload, source) function");
  ADAPTERS.set(protocol, impl);
  return protocol;
}
const adapter = protocol => ADAPTERS.get(protocol) || null;
const protocols = () => [...ADAPTERS.keys()].sort();
const list = (v, what) => { if (!Array.isArray(v)) throw fail(what + " is a list"); return v; };
const sha256 = s => crypto.createHash("sha256").update(s).digest("hex");

/* numeric parts of a dotted version, for the adapters that order releases within a line */
const parts = v => String(v).replace(/^v/, "").split(/[.+-]/).map(x => /^\d+$/.test(x) ? Number(x) : 0);
const newer = (a, b) => { const x = parts(a), y = parts(b); for (let i = 0; i < Math.max(x.length, y.length); i++) { if ((x[i] || 0) !== (y[i] || 0)) return (x[i] || 0) > (y[i] || 0); } return false; };

/* bounded discovery: only a source's declared https location (never a URL found in metadata), no
   redirect off that host, a timeout and a size cap; nothing fetched is ever executed */
const LIMITS = { timeoutMs: 20000, maxBytes: 8 * 1024 * 1024 };
async function fetchText(url) {
  let u; try { u = new URL(url); } catch (e) { throw fail("Not a URL: " + url); }
  if (u.protocol !== "https:") throw fail("Discovery reads https sources only: " + url);
  const r = await fetch(u, { redirect: "manual", signal: AbortSignal.timeout(LIMITS.timeoutMs) });
  if (r.status >= 300 && r.status < 400) throw fail(`${url} redirects; a source is read where it is declared`);
  if (!r.ok) throw fail(`${url} answered ${r.status}`);
  const len = Number(r.headers.get("content-length") || 0);
  if (len > LIMITS.maxBytes) throw fail(`${url} is larger than ${LIMITS.maxBytes} bytes`);
  const buf = Buffer.from(await r.arrayBuffer());
  if (buf.length > LIMITS.maxBytes) throw fail(`${url} is larger than ${LIMITS.maxBytes} bytes`);
  return buf.toString("utf8");
}

/* ---------- release-index: a runtime supplier's index of releases (one record per release) ----------
   Facts kept: the release date, whether it is a long-term-support release, whether it is a security
   release, the package manager it bundles and the platforms it is built for. A release that a later
   security release of the same line supersedes carries an advisory saying so. The item the bundled
   package manager is registered as is the source's `bundles` (none declared: not reported). */
register("release-index", {
  discover(payload, source) {
    const rows = list(payload, "A release index");
    const clean = rows.map(r => {
      if (!r || typeof r.version !== "string") throw fail("An index record names its version");
      return { ...r, version: r.version.replace(/^v/, "") };
    });
    const line = v => String(v).split(".")[0];
    const out = [];
    for (const r of clean) {
      const later = clean.filter(x => line(x.version) === line(r.version) && x.security === true && newer(x.version, r.version));
      out.push({
        item: source.item, version: r.version, channel: r.lts ? "lts" : "current",
        metadata: { date: String(r.date || ""), support: r.lts ? "lts" : "current", securityRelease: r.security === true, ...(r.npm ? { npm: String(r.npm) } : {}),
          ...(r.modules ? { modules: String(r.modules) } : {}), platforms: Array.isArray(r.files) ? r.files.map(String) : [] },
        dependencies: r.npm && source.bundles ? [{ item: source.bundles, version: String(r.npm) }] : [],
        advisories: later.length ? [{ key: "superseded-by-security-release", severity: "security-release", source: source.key,
          note: "later security releases in the line: " + later.map(x => x.version).sort((a, b) => newer(a, b) ? 1 : -1).join(", ") }] : []
      });
      /* the package manager the release bundles is itself a release, reported by the same source */
      if (r.npm && source.bundles) out.push({ item: source.bundles, version: String(r.npm), metadata: { bundledWith: source.item + "@" + r.version } });
    }
    return out;
  },
  async fetch(source) {
    const text = await fetchText(source.location);
    return { payload: JSON.parse(text), location: source.location, fetchedAt: new Date().toISOString(), payloadSha256: sha256(text) };
  }
});

/* ---------- checksum-list: the supplier's published digests of each release's archives ---------- */
register("checksum-list", {
  discover(payload, source) {
    return list(payload, "A checksum list").map(r => {
      if (!r || typeof r.version !== "string" || !r.files || typeof r.files !== "object") throw fail("A checksum record is { version, files: { <archive>: <sha256> } }");
      const prefix = `${source.item}-v${r.version}-`;
      return { item: source.item, version: r.version, artifacts: Object.entries(r.files).sort().map(([name, sum]) => ({
        name, sha256: String(sum), platform: name.startsWith(prefix) ? name.slice(prefix.length).replace(/\.(tar\.(gz|xz)|zip|7z|msi|pkg)$/, "") : null })) };
    });
  },
  async fetch(source, o) {
    const versions = (o && o.versions) || [];
    const entries = [];
    let all = "";
    for (const v of versions) {
      if (!/^\d+\.\d+\.\d+$/.test(String(v))) throw fail("Not a release version: " + v);
      const text = await fetchText(source.location.replace("{version}", v));
      all += text;
      const files = {};
      for (const line of text.split("\n")) { const m = /^([0-9a-f]{64})\s+(\S+)$/.exec(line.trim()); if (m) files[m[2]] = m[1]; }
      entries.push({ version: v, files });
    }
    return { payload: entries, location: source.location, fetchedAt: new Date().toISOString(), payloadSha256: sha256(all) };
  }
});

/* ---------- image-index: a container registry's index digest for a tag ---------- */
register("image-index", {
  discover(payload, source) {
    return list(payload, "An image list").map(r => {
      if (!r || !r.repository || !r.tag || !r.digest) throw fail("An image record is { repository, tag, digest }");
      const item = (source.items || {})[r.repository];
      if (!item) throw fail(`The source ${source.key} reports no item for the repository ${r.repository}`);
      return { item, version: String(r.tag), artifacts: [{ name: `${r.repository}:${r.tag}`, digest: String(r.digest) }],
        metadata: { reference: `${r.repository}:${r.tag}@${r.digest}`, repository: String(r.repository), tag: String(r.tag) },
        dependencies: Object.entries(r.provides || {}).sort().map(([k, v]) => ({ item: k, version: String(v) })) };
    });
  }
});

/* ---------- git-tag: the commit a tag of a source repository points at ---------- */
register("git-tag", {
  discover(payload, source) {
    return list(payload, "A tag list").map(r => {
      if (!r || !r.repository || !r.tag || !r.commit) throw fail("A tag record is { repository, tag, commit }");
      const item = (source.items || {})[r.repository];
      if (!item) throw fail(`The source ${source.key} reports no item for the repository ${r.repository}`);
      return { item, version: String(r.tag), artifacts: [{ name: `${r.repository}@${r.tag}`, commit: String(r.commit) }], metadata: { repository: String(r.repository), tag: String(r.tag) } };
    });
  }
});

/* ---------- npm-lockfile: the resolution npm generated (package-lock.json, lockfileVersion 2 or 3) ----------
   Each locked package is a release of a library item named npm:<package>; the item is introduced by
   the lockfile when the registry does not know it yet. */
register("npm-lockfile", {
  discover(payload, source) {
    if (!payload || typeof payload !== "object" || !payload.packages || typeof payload.packages !== "object") throw fail("A lockfile has packages");
    const out = [];
    for (const [where, p] of Object.entries(payload.packages).sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0)) {
      if (!where) continue;
      const name = where.slice(where.lastIndexOf("node_modules/") + "node_modules/".length);
      if (!name || !p || typeof p.version !== "string") throw fail("A locked package names its version: " + where);
      out.push({
        item: "npm:" + name, version: p.version,
        newItem: { key: "npm:" + name, category: source.category, label: name, licence: p.license ? String(p.license) : null, sources: [source.key] },
        artifacts: p.integrity ? [{ name: p.resolved ? String(p.resolved) : name + "@" + p.version, integrity: String(p.integrity) }] : [],
        metadata: { scope: p.dev ? "development" : "runtime", ...(p.engines && typeof p.engines === "object" ? { engines: p.engines } : {}), ...(p.license ? { licence: String(p.license) } : {}), ...(p.resolved ? { resolved: String(p.resolved) } : {}) },
        dependencies: Object.entries(p.dependencies || {}).sort().map(([k, range]) => ({ item: "npm:" + k, range: String(range) }))
      });
    }
    return out;
  }
});

/* ---------- declaration: facts a maintainer declared from an observation ---------- */
register("declaration", {
  discover(payload) {
    return list(payload, "A declaration").map(r => {
      if (!r || !r.item || !r.version) throw fail("A declared release is { item, version }");
      return { item: String(r.item), version: String(r.version), ...(r.metadata ? { metadata: r.metadata } : {}), ...(r.artifacts ? { artifacts: r.artifacts } : {}), ...(r.dependencies ? { dependencies: r.dependencies } : {}) };
    });
  }
});

module.exports = { register, adapter, protocols, sha256, LIMITS };
