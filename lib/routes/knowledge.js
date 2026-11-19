/* LUXORA Platform — knowledge domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the knowledge domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "knowledge", routes(kit) {
  const { J, T, actor, all, bad, constitutionHeld, coverageReport, entity, events, get, governance, json, logAction, meta, policies, requirePlatform, requireStaff, run, stIn, ucos, ucosCat, ucosComp, ucosDomain, ucosFound, ucosMon, ucosStore, ucosTrace, ucosUniv } = kit;

  function apiUcosManifest(req, res, url, s) {
    json(res, 200, ucos.manifest());
  }
  function apiUcosCoverage(req, res, url, s) {
    json(res, 200, ucos.coverage());
  }
  function apiUcosDocs(req, res, url, s) {
    json(res, 200, { documents: ucosStore().docs() });
  }
  function apiUcosParts(req, res, url, s, body, docId) {
    if (!requireStaff(s, res)) return;
    const o = ucosStore().parts(docId, url.searchParams.get("limit"), url.searchParams.get("offset"));
    json(res, 200, { doc: docId, parts: o.rows, total: o.total, limit: o.limit, offset: o.offset });
  }
  function apiUcosSections(req, res, url, s, body, docId) {
    if (!requireStaff(s, res)) return;
    const st = ucosStore();
    const out = st.sections(docId, url.searchParams.get("part"), url.searchParams.get("limit"), url.searchParams.get("offset"));
    json(res, 200, { doc: docId, sections: out.rows.map(function (r) { return Object.assign({}, r, { meta: J(r.meta, {}), doc_block: r.doc_block ? J(r.doc_block, {}) : null }); }), total: out.total, limit: out.limit, offset: out.offset });
  }
  function apiUcosConcepts(req, res, url, s, body, docId) {
    const out = ucosStore().concepts(docId, url.searchParams.get("q"), url.searchParams.get("limit"), url.searchParams.get("offset"));
    json(res, 200, { doc: docId, concepts: out.rows, total: out.total, limit: out.limit, offset: out.offset });
  }
  function apiUcosRegistries(req, res, url, s, body, docId) {
    if (!requireStaff(s, res)) return;
    const o = ucosStore().registries(docId, url.searchParams.get("limit"), url.searchParams.get("offset"));
    json(res, 200, { doc: docId, registries: o.rows, total: o.total, limit: o.limit, offset: o.offset });
  }
  function apiUcosEdges(req, res, url, s, body, docId) {
    if (!requireStaff(s, res)) return;
    const o = ucosStore().edges(docId, url.searchParams.get("source_type"), url.searchParams.get("source_id"), url.searchParams.get("limit"), url.searchParams.get("offset"));
    json(res, 200, { doc: docId, edges: o.rows, total: o.total, limit: o.limit, offset: o.offset });
  }
  function apiUcosNeighbours(req, res, url, s, body, docId) {
    const type = url.searchParams.get("type"), id = url.searchParams.get("id");
    if (!type || !id) return bad(res, "type and id parameters required");
    json(res, 200, Object.assign({ doc: docId }, ucosStore().neighbours(docId, type, id, url.searchParams.get("limit"))));
  }
  function apiUcosSearch(req, res, url, s) {
    const q = url.searchParams.get("q");
    if (!q) return bad(res, "q parameter required");
    json(res, 200, { q, results: ucos.search(q, Number(url.searchParams.get("limit")) || 50) });
  }
  function apiUcosReparse(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    const out = ucos.seed({ get, run, all });
    logAction(s, "ucos.reparse", "ucos", "documents", out, req);
    json(res, 200, { ok: true, stats: out });
  }
  function apiUcosHealth(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    const h = ucosMon.health();
    const code = h.ok ? 200 : (h.status === "degraded" ? 200 : 503);
    json(res, code, h);
  }
  function apiUcosDrift(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    json(res, 200, Object.assign(ucosMon.driftStatus(), { log: ucosMon.driftLog() }));
  }
  /* ---------- foundation completeness ----------
     Executes the corpus's own FOUNDATION FREEZE CRITERIA (17AH.7) and exposes
     the master index, so "how much is left" is answered by data rather than by
     prose. The audit is read-only and derives every number from the registry. */
  function apiUcosCompleteness(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    const a = ucosComp.audit();
    /* re-auditing is also how an operator LIFTS a hold: storing the fresh verdict means a
       resolved constitution unblocks constitutional writes immediately, with no restart */
    try {
      run("INSERT INTO platform_settings(key,value) VALUES('ucos_freeze',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        JSON.stringify({ ok: a.ok, verdict: a.verdict, criticalCount: a.criticalCount, gapCount: a.gapCount, auditedAt: a.auditedAt }));
    } catch (e) { }
    json(res, a.ok ? 200 : 503, a);
  }
  function apiUcosIndex(req, res, url, s) {
    json(res, 200, ucosComp.masterIndex());
  }
  /* ---------- annotation CRUD (the write path) ----------
     Every mutation requires platform admin and is audit-logged; the canonical documents are never
     touched. Reads are open to store admins so a team can share context. */
  function apiUcosAnnotations(req, res, url, s, body, docId) {
    if (!requireStaff(s, res)) return;
    const kind = url.searchParams.get("kind"), key = url.searchParams.get("key");
    if (!kind || !key) return bad(res, "kind and key parameters required");
    json(res, 200, ucos.annotations({ get, run, all }, docId, kind, key, url.searchParams.get("limit"), url.searchParams.get("offset")));
  }
  function apiUcosAnnotationCreate(req, res, url, s, body, docId) {
    if (!requirePlatform(s, res)) return;
    const out = ucos.addAnnotation({ get, run, all }, s, docId, body.kind, body.key, body.note, body.pin);
    logAction(s, "ucos.annotate", "ucos", body.kind + ":" + body.key, out, req);
    json(res, out.ok ? 200 : 400, out);
  }
  function apiUcosAnnotationUpdate(req, res, url, s, body, rest) {
    if (!requirePlatform(s, res)) return;
    const id = (url.pathname.split("/").pop()) || (body && body.id);
    const out = ucos.updateAnnotation({ get, run, all }, s, id, body.note, body.pin);
    logAction(s, "ucos.annotate", "ucos", "annotation:" + id, out, req);
    json(res, out.ok ? 200 : 400, out);
  }
  function apiUcosAnnotationDelete(req, res, url, s, body, rest) {
    if (!requirePlatform(s, res)) return;
    const id = (url.pathname.split("/").pop()) || (body && body.id);
    const out = ucos.deleteAnnotation({ get, run, all }, s, id);
    logAction(s, "ucos.annotate", "ucos", "annotation:" + id, out, req);
    json(res, out.ok ? 200 : 404, out);
  }
  function apiUcosAnnotationOrphans(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    json(res, 200, { orphans: ucos.orphanedAnnotations({ get, run, all }) });
  }
  /* ---------- UCOS Ω∞ Foundation Registry (Architecture3 Articles 2-8) ----------
     The operational half of the constitution. Reads are open to administrators so the
     console can draw the five graphs; the register/certify/deprecate mutations are
     Foundation Authority actions and require platform admin (Article 6). Every mutation
     is recorded in the append-only ledger by the module itself. */
  function apiUcosFoundationsManifest(req, res, url, s) {
    json(res, 200, ucosFound.manifest());
  }
  function apiUcosFoundationsList(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    json(res, 200, { foundations: ucosFound.list({ universe: url.searchParams.get("universe"), lifecycle: url.searchParams.get("lifecycle") }) });
  }
  function apiUcosFoundationResolve(req, res, url, s, body, key) {
    if (!requireStaff(s, res)) return;
    const f = ucosFound.resolve(key);
    if (!f) return bad(res, "foundation not found", 404);
    json(res, 200, f);
  }
  function apiUcosFoundationTraverse(req, res, url, s, body, key) {
    if (!requireStaff(s, res)) return;
    const graph = url.searchParams.get("graph") || "dependency";
    if (!ucosFound.GRAPHS[graph]) return bad(res, "unknown graph: " + graph, 400);
    json(res, 200, ucosFound.traverse(key, graph, url.searchParams.get("depth")));
  }
  function apiUcosFoundationRegister(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    if (constitutionHeld(res)) return;
    const out = ucosFound.register(body.name, {
      parent: body.parent, dependencies: body.dependencies, universe: body.universe,
      lifecycle: body.lifecycle, governance: body.governance,
      sourceDoc: body.source_doc, sourceLine: body.source_line
    });
    logAction(s, "ucos.foundation.register", "ucos", out.key, out, req);
    json(res, out.ok ? 200 : 409, out);
  }
  function apiUcosFoundationCertify(req, res, url, s, body, key) {
    if (!requirePlatform(s, res)) return;
    if (constitutionHeld(res)) return;
    const out = ucosFound.certify(key);
    logAction(s, "ucos.foundation.certify", "ucos", key, out, req);
    json(res, out.ok ? 200 : 404, out);
  }
  function apiUcosFoundationDeprecate(req, res, url, s, body, key) {
    if (!requirePlatform(s, res)) return;
    if (constitutionHeld(res)) return;
    const out = ucosFound.deprecate(key, body && body.successor);
    logAction(s, "ucos.foundation.deprecate", "ucos", key, out, req);
    json(res, out.ok ? 200 : 409, out);
  }
  function apiUcosFoundationRetire(req, res, url, s, body, key) {
    if (!requirePlatform(s, res)) return;
    if (constitutionHeld(res)) return;
    const out = ucosFound.retire(key);
    logAction(s, "ucos.foundation.retire", "ucos", key, out, req);
    json(res, out.ok ? 200 : 409, out);
  }
  /* Article 3.2 / 8.2: the compliance rules are executable — this proves the registry
     is acyclic, fully resolved, unique and orphan-free at any moment */
  function apiUcosFoundationsVerify(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    const v = ucosFound.verify();
    json(res, v.ok ? 200 : 503, v);
  }
  function apiUcosFoundationsLedger(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    json(res, 200, { events: ucosFound.ledger(url.searchParams.get("limit")) });
  }
  /* ---------- instantiated universes ----------
     Each universe the corpus declares is registered as a foundation AND instantiated as a
     live, data-defined entity, so the constitution is operable rather than merely readable.
     The instantiation is derived from the corpus (never hand-listed) and idempotent. */
  function apiUcosUniverses(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    json(res, 200, { universes: ucosUniv.list(), stats: ucosUniv.stats() });
  }
  function apiUcosUniversesInstantiate(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    const out = ucosUniv.instantiateAll();
    logAction(s, "ucos.universes.instantiate", "ucos", "universes", out, req);
    json(res, 200, { ok: true, ...out, stats: ucosUniv.stats() });
  }
  function apiUcosCoverageReport(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    json(res, 200, coverageReport());
  }
  /* ---------- catalog bridge: universe entities become shopper-transactable ----------
     Publishing is a platform action (it changes a tenant's live catalog); withdrawal
     too. Reads are open to store admins so a merchant can see what is on their shelf. */
  function apiUcosCatalogStats(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    json(res, 200, ucosCat.catalogStats());
  }
  function apiUcosCatalogPublish(req, res, url, s, body, key) {
    if (!requirePlatform(s, res)) return;
    const tenantId = Number(url.searchParams.get("tenant_id") || (s.tenant && s.tenant.id));
    if (!tenantId) return bad(res, "tenant_id required", 400);
    const out = ucosCat.publishUniverse(tenantId, key);
    logAction(s, "ucos.catalog.publish", "ucos", key, out, req);
    json(res, out.ok ? 200 : 409, out);
  }
  function apiUcosCatalogWithdraw(req, res, url, s, body, key) {
    if (!requirePlatform(s, res)) return;
    const tenantId = Number(url.searchParams.get("tenant_id") || (s.tenant && s.tenant.id));
    if (!tenantId) return bad(res, "tenant_id required", 400);
    const out = ucosCat.withdrawUniverse(tenantId, key);
    logAction(s, "ucos.catalog.withdraw", "ucos", key, out, req);
    json(res, 200, out);
  }
  function apiUcosCatalogList(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    /* tenant_id= is honoured only for platform admins; a store admin sees their own store */
    const tenantId = s.platform_admin && url.searchParams.get("tenant_id") ? Number(url.searchParams.get("tenant_id")) : T(s);
    json(res, 200, { published: tenantId ? ucosCat.listPublished(tenantId) : [], stats: ucosCat.catalogStats() });
  }
  /* ---------- ACTIVATION: every declared universe becomes shopper-transactable ----------
     This is the "implement all" primitive: activation materializes a universe's
     canonical offering (from its own corpus-declared fields) and publishes it into a
     tenant catalog, so the whole constitution is on the shelf by default. It is a
     platform action (it writes a tenant's live catalog), bounded and idempotent. */
  function apiUcosCatalogActivate(req, res, url, s, body, key) {
    if (!requirePlatform(s, res)) return;
    const tenantId = Number(url.searchParams.get("tenant_id") || (s.tenant && s.tenant.id));
    if (!tenantId) return bad(res, "tenant_id required", 400);
    /* the target must be a real store — activation writes that tenant's live catalog,
       so an invented id must be refused rather than creating orphaned catalog rows */
    if (!get("SELECT 1 ok FROM tenants WHERE id=? AND status IN " + stIn("tenant", "operating").sql, tenantId, ...stIn("tenant", "operating").args))
      return bad(res, "unknown or inactive tenant", 404);
    /* the limit is capped: a corpus of thousands must never saturate one request */
    const limit = Math.min(Number(body && body.limit) || 250, 2000);
    const out = key ? ucosCat.activate(tenantId, key) : ucosCat.activateAll(tenantId, { limit });
    logAction(s, "ucos.catalog.activate", "ucos", key || "all", out, req);
    json(res, out.ok === false ? 409 : 200, out);
  }
  function apiUcosActivationStats(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    json(res, 200, ucosCat.activationStats());
  }
  function apiUcosTrace(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    const key = url.searchParams.get("key");
    if (!key) return json(res, 200, ucosTrace.matrix());
    json(res, 200, ucosTrace.trace(key));
  }
  function apiUcosMatrix(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    json(res, 200, ucosTrace.matrix());
  }
  function apiUcosDomain(req, res, url, s, body, key) {
    if (!requireStaff(s, res)) return;
    const d = ucosDomain.board(key, s.platform_admin ? null : T(s));
    if (!d) return bad(res, "unknown universe " + key, 404);
    json(res, 200, d);
  }
  function apiUcosDomainFire(req, res, url, s, body, key) {
    if (!requireStaff(s, res)) return;
    if (constitutionHeld(res)) return;
    const rid = Number((body && body.record_id) || url.searchParams.get("record_id"));
    if (!rid) return bad(res, "record_id required", 400);
    const out = ucosDomain.fire(key, rid, { tenantId: s.platform_admin ? null : T(s), actor: s.platform_admin ? ("platform:" + s.platform_admin.email) : ("admin:" + s.user_id), detail: body && body.detail });
    logAction(s, "ucos.domain.transition", "ucos", key + "#" + rid, out, req);
    json(res, out.ok === false ? 409 : 200, out);
  }
  function apiUcosDomains(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    json(res, 200, { domains: ucosDomain.domains() });
  }
  /* ========== UCII Ω∞ Registry API ========== */
  // Capability Registry
  function apiCapabilityList(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    const category = url.searchParams.get('category');
    const q = category ? 'WHERE category=?' : '';
    const p = category ? [category] : [];
    json(res, 200, { capabilities: all(`SELECT * FROM capabilities ${q} ORDER BY category, key`, ...p) });
  }
  function apiCapabilityCreate(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    if (!body.key || !body.name) return bad(res, 'key and name required', 400);
    run('INSERT INTO capabilities(key,name,description,category,version,schema,config,dependencies,status) VALUES(?,?,?,?,?,?,?,?,?)',
      body.key, body.name, body.description || '', body.category || '', body.version || '1.0.0', 
      JSON.stringify(body.schema || {}), JSON.stringify(body.config || {}), JSON.stringify(body.dependencies || []), body.status || 'active');
    logAction(s, 'capability.create', 'capability', body.key);
    json(res, 200, { ok: true });
  }
  function apiCapabilityUpdate(req, res, url, s, body, key) {
    if (!requirePlatform(s, res)) return;
    run('UPDATE capabilities SET name=?,description=?,category=?,version=?,schema=?,config=?,dependencies=?,status=? WHERE key=?',
      body.name, body.description, body.category, body.version, JSON.stringify(body.schema || {}), 
      JSON.stringify(body.config || {}), JSON.stringify(body.dependencies || []), body.status, key);
    logAction(s, 'capability.update', 'capability', key);
    json(res, 200, { ok: true });
  }
  // Domain Registry
  function apiDomainList(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    json(res, 200, { domains: all('SELECT * FROM domains ORDER BY key') });
  }
  function apiDomainCreate(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    if (!body.key || !body.name) return bad(res, 'key and name required', 400);
    run('INSERT INTO domains(key,name,description,parent,schema,policies,status) VALUES(?,?,?,?,?,?,?)',
      body.key, body.name, body.description || '', body.parent || '', JSON.stringify(body.schema || {}), JSON.stringify(body.policies || []), body.status || 'active');
    logAction(s, 'domain.create', 'domain', body.key);
    json(res, 200, { ok: true });
  }
  // Policy Registry
  function apiPolicyList(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    const domain = url.searchParams.get('domain');
    const q = domain ? 'WHERE domain=?' : '';
    const p = domain ? [domain] : [];
    json(res, 200, { policies: all(`SELECT * FROM policies ${q} ORDER BY priority`, ...p) });
  }
  function apiPolicyCreate(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    if (!body.key || !body.name || !body.rule) return bad(res, 'key, name, and rule required', 400);
    run('INSERT INTO policies(key,domain,name,description,type,priority,rule,context,status) VALUES(?,?,?,?,?,?,?,?,?)',
      body.key, body.domain, body.name, body.description || '', body.type || 'validation', body.priority || 0, body.rule, JSON.stringify(body.context || {}), body.status || 'active');
    logAction(s, 'policy.create', 'policy', body.key);
    json(res, 200, { ok: true });
  }
  // Workflow Registry
  function apiWorkflowList(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    const domain = url.searchParams.get('domain');
    const q = domain ? 'WHERE domain=?' : '';
    const p = domain ? [domain] : [];
    json(res, 200, { workflows: all(`SELECT * FROM workflows ${q} ORDER BY key`, ...p) });
  }
  function apiWorkflowCreate(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    if (!body.key || !body.domain || !body.trigger || !body.steps) return bad(res, 'key, domain, trigger, and steps required', 400);
    run('INSERT INTO workflows(key,domain,name,description,trigger,steps,config,status) VALUES(?,?,?,?,?,?,?,?)',
      body.key, body.domain, body.name || null, body.description || '', body.trigger, JSON.stringify(body.steps), JSON.stringify(body.config || {}), body.status || 'active');
    logAction(s, 'workflow.create', 'workflow', body.key);
    json(res, 200, { ok: true });
  }
  function apiWorkflowDelete(req, res, url, s, body, key) {
    if (!requirePlatform(s, res)) return;
    run('DELETE FROM workflows WHERE key=?', key);
    logAction(s, 'workflow.delete', 'workflow', key);
    json(res, 200, { ok: true });
  }
  // Config Store
  function apiConfigGet(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    const key = url.searchParams.get('key');
    const tenantId = url.searchParams.get('tenant_id');
    const scope = url.searchParams.get('scope') || 'platform';
    if (key) {
      const row = get('SELECT * FROM config_store WHERE key=? AND scope=? AND (tenant_id=? OR tenant_id IS NULL) ORDER BY version DESC LIMIT 1', key, scope, tenantId ? Number(tenantId) : null);
      json(res, 200, { config: row ? { ...row, value: JSON.parse(row.value || '{}') } : null });
    } else {
      const q = tenantId ? 'WHERE scope=? AND tenant_id=?' : 'WHERE scope=?';
      const p = tenantId ? [scope, Number(tenantId)] : [scope];
      const configs = all(`SELECT * FROM config_store ${q} AND active=1 ORDER BY key`, ...p);
      json(res, 200, { config: Object.fromEntries(configs.map(c => [c.key, JSON.parse(c.value || '{}')])) });
    }
  }
  function apiConfigSet(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    if (!body.key || !body.value) return bad(res, 'key and value required', 400);
    const scope = body.scope || 'platform';
    const tenantId = body.tenant_id || null;
    const existing = get('SELECT version FROM config_store WHERE key=? AND scope=? AND tenant_id=?', body.key, scope, tenantId);
    const version = (existing ? existing.version : 0) + 1;
    run('INSERT INTO config_store(key,value,scope,tenant_id,version,active,updated_at) VALUES(?,?,?,?,?,?,datetime(\'now\')) ON CONFLICT(key,scope,tenant_id) DO UPDATE SET value=excluded.value,version=excluded.version,updated_at=datetime(\'now\')',
      body.key, JSON.stringify(body.value), scope, tenantId, version, body.active !== false ? 1 : 0);
    logAction(s, 'config.set', 'config', body.key);
    json(res, 200, { ok: true });
  }
  // Knowledge Graph
  function apiKnowledgeGraphQuery(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    const source = url.searchParams.get('source_type');
    const sourceId = url.searchParams.get('source_id');
    const rel = url.searchParams.get('relationship');
    if (source && sourceId) {
      const q = 'WHERE source_type=? AND source_id=?' + (rel ? ' AND relationship=?' : '');
      const p = rel ? [source, Number(sourceId), rel] : [source, Number(sourceId)];
      json(res, 200, { edges: all(`SELECT * FROM knowledge_graph ${q} ORDER BY weight DESC LIMIT 100`, ...p) });
    } else {
      json(res, 200, { edges: all('SELECT * FROM knowledge_graph ORDER BY weight DESC LIMIT 100') });
    }
  }
  function apiKnowledgeGraphAdd(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    if (!body.source_type || !body.source_id || !body.relationship || !body.target_type || !body.target_id) return bad(res, 'source and target required', 400);
    run('INSERT INTO knowledge_graph(source_type,source_id,relationship,target_type,target_id,weight,metadata) VALUES(?,?,?,?,?,?,?)',
      body.source_type, Number(body.source_id), body.relationship, body.target_type, Number(body.target_id), body.weight || 1.0, JSON.stringify(body.metadata || {}));
    json(res, 200, { ok: true });
  }
  // Usage Metering
  /* S10: this had no auth gate and took the tenant from the request body, so
     anyone could inject metering rows for any store — the table usage reporting
     and billing read. The tenant is the session's store, always. A platform
     operator working a store records against it too, so the gate accepts the
     platform session as well as the store's own admin. */
  function apiUsageRecord(req, res, url, s, body) {
    if (!requireStaff(s, res)) return;
    const tenantId = T(s);
    run('INSERT INTO usage_events(tenant_id,entity,entity_id,event_type,quantity,unit,metadata) VALUES(?,?,?,?,?,?,?)',
      tenantId, body.entity, body.entity_id ? Number(body.entity_id) : null, body.event_type, body.quantity || 1, body.unit || 'count', JSON.stringify(body.metadata || {}));
    json(res, 200, { ok: true });
  }
  function apiUsageReport(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    const tenantId = url.searchParams.get('tenant_id');
    const entity = url.searchParams.get('entity');
    const period = url.searchParams.get('period');
    let q = 'SELECT entity,event_type,SUM(quantity) as total,unit FROM usage_events';
    const p = [];
    if (tenantId) { q += ' WHERE tenant_id=?'; p.push(Number(tenantId)); }
    if (entity) { q += (p.length ? ' AND ' : ' WHERE ') + 'entity=?'; p.push(entity); }
    if (period) { q += (p.length ? ' AND ' : ' WHERE ') + 'strftime(\'%Y-%m\',created_at)=?'; p.push(period); }
    q += ' GROUP BY entity,event_type,unit ORDER BY total DESC';
    json(res, 200, { usage: all(q, ...p) });
  }

  return [
    ["GET /api/ucii/capabilities", apiCapabilityList],
    ["POST /api/ucii/capabilities", apiCapabilityCreate],
    ["PUT /api/ucii/capabilities/:key", (r, re, u, s, b, p) => apiCapabilityUpdate(r, re, u, s, b, p)],
    ["GET /api/ucii/domains", apiDomainList],
    ["POST /api/ucii/domains", apiDomainCreate],
    ["GET /api/ucii/policies", apiPolicyList],
    ["POST /api/ucii/policies", apiPolicyCreate],
    ["GET /api/ucii/workflows", apiWorkflowList],
    ["POST /api/ucii/workflows", apiWorkflowCreate],
    ["DELETE /api/ucii/workflows/:key", (r, re, u, s, b, p) => apiWorkflowDelete(r, re, u, s, b, p)],
    ["GET /api/ucii/config", apiConfigGet],
    ["POST /api/ucii/config", apiConfigSet],
    ["GET /api/ucii/knowledge", apiKnowledgeGraphQuery],
    ["POST /api/ucii/knowledge", apiKnowledgeGraphAdd],
    ["POST /api/ucii/usage", apiUsageRecord],
    ["GET /api/ucii/usage", apiUsageReport],
    ["GET /api/ucos/manifest", apiUcosManifest],
    ["GET /api/ucos/coverage", apiUcosCoverage],
    ["GET /api/ucos/docs", apiUcosDocs],
    ["GET /api/ucos/:doc/parts", (r, re, u, s, b, p) => apiUcosParts(r, re, u, s, b, p)],
    ["GET /api/ucos/:doc/sections", (r, re, u, s, b, p) => apiUcosSections(r, re, u, s, b, p)],
    ["GET /api/ucos/:doc/concepts", (r, re, u, s, b, p) => apiUcosConcepts(r, re, u, s, b, p)],
    ["GET /api/ucos/:doc/registries", (r, re, u, s, b, p) => apiUcosRegistries(r, re, u, s, b, p)],
    ["GET /api/ucos/:doc/edges", (r, re, u, s, b, p) => apiUcosEdges(r, re, u, s, b, p)],
    ["GET /api/ucos/:doc/neighbours", (r, re, u, s, b, p) => apiUcosNeighbours(r, re, u, s, b, p)],
    ["GET /api/ucos/search", apiUcosSearch],
    ["POST /api/ucos/reparse", apiUcosReparse],
    ["GET /api/ucos/health", apiUcosHealth],
    ["GET /api/ucos/drift", apiUcosDrift],
    ["GET /api/ucos/completeness", apiUcosCompleteness],
    ["GET /api/ucos/index", apiUcosIndex],
    ["GET /api/ucos/:doc/annotations", (r, re, u, s, b, p) => apiUcosAnnotations(r, re, u, s, b, p)],
    ["POST /api/ucos/:doc/annotations", (r, re, u, s, b, p) => apiUcosAnnotationCreate(r, re, u, s, b, p)],
    ["PUT /api/ucos/annotations/:id", (r, re, u, s, b, p) => apiUcosAnnotationUpdate(r, re, u, s, b, p)],
    ["DELETE /api/ucos/annotations/:id", (r, re, u, s, b, p) => apiUcosAnnotationDelete(r, re, u, s, b, p)],
    ["GET /api/ucos/annotations/orphans", apiUcosAnnotationOrphans],
    ["GET /api/ucos/foundations/manifest", apiUcosFoundationsManifest],
    ["GET /api/ucos/foundations/verify", apiUcosFoundationsVerify],
    ["GET /api/ucos/foundations/ledger", apiUcosFoundationsLedger],
    ["GET /api/ucos/foundations", apiUcosFoundationsList],
    ["GET /api/ucos/foundations/:key", (r, re, u, s, b, p) => apiUcosFoundationResolve(r, re, u, s, b, p)],
    ["GET /api/ucos/foundations/:key/traverse", (r, re, u, s, b, p) => apiUcosFoundationTraverse(r, re, u, s, b, p)],
    ["POST /api/ucos/foundations", apiUcosFoundationRegister],
    ["POST /api/ucos/foundations/:key/certify", (r, re, u, s, b, p) => apiUcosFoundationCertify(r, re, u, s, b, p)],
    ["POST /api/ucos/foundations/:key/deprecate", (r, re, u, s, b, p) => apiUcosFoundationDeprecate(r, re, u, s, b, p)],
    ["POST /api/ucos/foundations/:key/retire", (r, re, u, s, b, p) => apiUcosFoundationRetire(r, re, u, s, b, p)],
    ["GET /api/ucos/universes", apiUcosUniverses],
    ["POST /api/ucos/universes/instantiate", apiUcosUniversesInstantiate],
    ["GET /api/ucos/coverage-report", apiUcosCoverageReport],
    ["GET /api/ucos/catalog", apiUcosCatalogList],
    ["GET /api/ucos/catalog/stats", apiUcosCatalogStats],
    ["POST /api/ucos/catalog/:key/publish", (r, re, u, s, b, p) => apiUcosCatalogPublish(r, re, u, s, b, p)],
    ["POST /api/ucos/catalog/:key/withdraw", (r, re, u, s, b, p) => apiUcosCatalogWithdraw(r, re, u, s, b, p)],
    ["POST /api/ucos/catalog/activate", apiUcosCatalogActivate],
    ["POST /api/ucos/catalog/:key/activate", (r, re, u, s, b, p) => apiUcosCatalogActivate(r, re, u, s, b, p)],
    ["GET /api/ucos/catalog/activation", apiUcosActivationStats],
    ["GET /api/ucos/trace", apiUcosTrace],
    ["GET /api/ucos/matrix", apiUcosMatrix],
    ["GET /api/ucos/domains", apiUcosDomains],
    ["GET /api/ucos/domain/:key", (r, re, u, s, b, p) => apiUcosDomain(r, re, u, s, b, p)],
    ["POST /api/ucos/domain/:key/fire", (r, re, u, s, b, p) => apiUcosDomainFire(r, re, u, s, b, p)]
  ];
} };
