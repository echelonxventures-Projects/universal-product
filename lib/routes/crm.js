/* LUXORA Platform — CRM domain routes (lib/crm.js; _registry/business-domains.json).
   Companies, contacts, the pipeline and its deals, activities and one view of a customer. Every
   route belongs to the store's crm section (the Growth role may change it; Support may read it). */
"use strict";

module.exports = { domain: "crm", routes(kit) {
  const { T, actor, bad, json, logAction, requireAdmin } = kit;
  const C = () => require("../crm.js");
  const answer = (s, res, fn) => { if (!requireAdmin(s, res)) return; try { fn(); } catch (e) { bad(res, e.message, e.status || 400); } };
  const q = (url, k) => url.searchParams.get(k) || "";
  const done = (s, res, what, ref, out, key) => { logAction(s, "crm." + what, key || what, ref, {}); json(res, 200, out); };

  /* The store's companies, by name, with how many contacts and deals each has; `q` searches name and domain. */
  function apiCrmCompanies(req, res, url, s) { answer(s, res, () => json(res, 200, { companies: C().companies(T(s), { q: q(url, "q") }) })); }
  /* Adds a company: `name`, `domain`, `industry`, `size`, `country`, `tax_id`, `owner_staff`, `note`. */
  function apiCrmCompanyAdd(req, res, url, s, body) { answer(s, res, () => { const c = C().saveCompany(T(s), { ...(body || {}), id: undefined }); done(s, res, "company", c.id, { company: c }); }); }
  /* One company with its contacts, its deals and everything done about it. */
  function apiCrmCompany(req, res, url, s, body, id) { answer(s, res, () => json(res, 200, { company: C().company(T(s), id) })); }
  /* Changes a company's details. */
  function apiCrmCompanySave(req, res, url, s, body, id) { answer(s, res, () => { const c = C().saveCompany(T(s), { ...(body || {}), id }); done(s, res, "company", c.id, { company: c }); }); }
  /* The store's contacts, by name, with their company; `q` searches name and email, `company_id` narrows. */
  function apiCrmContacts(req, res, url, s) { answer(s, res, () => json(res, 200, { contacts: C().contacts(T(s), { q: q(url, "q"), company_id: q(url, "company_id") }) })); }
  /* Adds a contact: `name`, `email` (once per store; linked to their shopper account when they have one), `phone`, `title`, `company_id`. */
  function apiCrmContactAdd(req, res, url, s, body) { answer(s, res, () => { const c = C().saveContact(T(s), { ...(body || {}), id: undefined }); done(s, res, "contact", c.id, { contact: c }); }); }
  /* Changes a contact's details. */
  function apiCrmContactSave(req, res, url, s, body, id) { answer(s, res, () => { const c = C().saveContact(T(s), { ...(body || {}), id }); done(s, res, "contact", c.id, { contact: c }); }); }
  /* The pipeline board: each stage with its open deals, then the deals won and lost. */
  function apiCrmPipeline(req, res, url, s) { answer(s, res, () => json(res, 200, C().pipeline(T(s)))); }
  /* The forecast per currency and month: the open pipeline, the same weighted by each stage's chance, and what was won. */
  function apiCrmForecast(req, res, url, s) { answer(s, res, () => json(res, 200, { forecast: C().forecast(T(s)) })); }
  /* The store's pipeline stages, each with its chance of winning. */
  function apiCrmStages(req, res, url, s) { answer(s, res, () => json(res, 200, { stages: C().stages(T(s)) })); }
  /* Sets the store's own pipeline: `stages` of `{ key, label, probability }`. A stage that still has open deals cannot be removed. */
  function apiCrmStagesSave(req, res, url, s, body) { answer(s, res, () => done(s, res, "stages", "pipeline", { stages: C().setStages(T(s), (body || {}).stages) }, "settings")); }
  /* Opens a deal: `title`, `company_id` or `contact_id`, or `case_id` to turn a shopper's enquiry into one; `amount`, `currency`, `stage`, `expected_close`, `owner_staff`. */
  function apiCrmDealOpen(req, res, url, s, body) { answer(s, res, () => { const d = C().openDeal(T(s), body || {}, actor(s)); done(s, res, "deal", d.ref, { deal: d }); }); }
  /* One deal with its company, contact, stage and timeline. */
  function apiCrmDeal(req, res, url, s, body, id) { answer(s, res, () => json(res, 200, { deal: C().deal(T(s), id) })); }
  /* Moves an open deal: its `stage` (and so its chance), `amount`, `expected_close`, `title` or `owner_staff`. */
  function apiCrmDealSave(req, res, url, s, body, id) { answer(s, res, () => { const d = C().updateDeal(T(s), id, body || {}); done(s, res, "deal", d.ref, { deal: d }); }); }
  /* Marks a deal won. */
  function apiCrmDealWon(req, res, url, s, body, id) { answer(s, res, () => { const d = C().closeDeal(T(s), id, true); done(s, res, "won", d.ref, { deal: d }, "deal"); }); }
  /* Marks a deal lost, with the `reason`. */
  function apiCrmDealLost(req, res, url, s, body, id) { answer(s, res, () => { const d = C().closeDeal(T(s), id, false, (body || {}).reason); done(s, res, "lost", d.ref, { deal: d }, "deal"); }); }
  /* Reopens a lost deal in the stage it was in. */
  function apiCrmDealReopen(req, res, url, s, body, id) { answer(s, res, () => { const d = C().reopen(T(s), id); done(s, res, "reopen", d.ref, { deal: d }, "deal"); }); }
  /* Records an activity: `kind` (call, meeting, email, task, note), `subject`, `body`, about a `deal_id`, `contact_id` or `company_id`; `due_at` for what is still to do, `done` for what happened. */
  function apiCrmActivityLog(req, res, url, s, body) { answer(s, res, () => { const a = C().logActivity(T(s), body || {}, actor(s)); done(s, res, "activity", a.id, { activity: a }); }); }
  /* Marks an activity done, with its `outcome`. */
  function apiCrmActivityDone(req, res, url, s, body, id) { answer(s, res, () => { const a = C().completeActivity(T(s), id, (body || {}).outcome); done(s, res, "activity", a.id, { activity: a }); }); }
  /* What is still to do, by due date; `staff` narrows it to one person's. */
  function apiCrmAgenda(req, res, url, s) { answer(s, res, () => json(res, 200, { agenda: C().agenda(T(s), q(url, "staff")) })); }
  /* One view of a shopper: their orders, what they spent, returns, support cases, wallet, segments, and their contacts, deals and activities. */
  function apiCrmPerson(req, res, url, s, body, id) { answer(s, res, () => json(res, 200, C().person(T(s), id))); }

  return [
    ["GET /api/admin/crm/companies", apiCrmCompanies],
    ["POST /api/admin/crm/companies", apiCrmCompanyAdd],
    ["GET /api/admin/crm/companies/:id", (r, re, u, s, b, p) => apiCrmCompany(r, re, u, s, b, p)],
    ["PUT /api/admin/crm/companies/:id", (r, re, u, s, b, p) => apiCrmCompanySave(r, re, u, s, b, p)],
    ["GET /api/admin/crm/contacts", apiCrmContacts],
    ["POST /api/admin/crm/contacts", apiCrmContactAdd],
    ["PUT /api/admin/crm/contacts/:id", (r, re, u, s, b, p) => apiCrmContactSave(r, re, u, s, b, p)],
    ["GET /api/admin/crm/pipeline", apiCrmPipeline],
    ["GET /api/admin/crm/forecast", apiCrmForecast],
    ["GET /api/admin/crm/stages", apiCrmStages],
    ["PUT /api/admin/crm/stages", apiCrmStagesSave],
    ["POST /api/admin/crm/deals", apiCrmDealOpen],
    ["GET /api/admin/crm/deals/:id", (r, re, u, s, b, p) => apiCrmDeal(r, re, u, s, b, p)],
    ["PUT /api/admin/crm/deals/:id", (r, re, u, s, b, p) => apiCrmDealSave(r, re, u, s, b, p)],
    ["POST /api/admin/crm/deals/:id/won", (r, re, u, s, b, p) => apiCrmDealWon(r, re, u, s, b, p)],
    ["POST /api/admin/crm/deals/:id/lost", (r, re, u, s, b, p) => apiCrmDealLost(r, re, u, s, b, p)],
    ["POST /api/admin/crm/deals/:id/reopen", (r, re, u, s, b, p) => apiCrmDealReopen(r, re, u, s, b, p)],
    ["POST /api/admin/crm/activities", apiCrmActivityLog],
    ["POST /api/admin/crm/activities/:id/done", (r, re, u, s, b, p) => apiCrmActivityDone(r, re, u, s, b, p)],
    ["GET /api/admin/crm/agenda", apiCrmAgenda],
    ["GET /api/admin/crm/people/:id", (r, re, u, s, b, p) => apiCrmPerson(r, re, u, s, b, p)]
  ];
} };
