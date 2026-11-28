/* LUXORA Platform — campaigns domain routes (lib/campaigns.js; _registry/business-domains.json).
   A store's campaigns under its campaigns section (the Growth role holds it), and the public routes
   every message links to, which need no sign-in: the unsubscribe link and the tracked links. Journeys
   (lib/journeys.js) under the same section. */
"use strict";

module.exports = { domain: "campaigns", routes(kit) {
  const { T, actor, bad, json, logAction, requireAdmin, publicLink } = kit;
  const CA = () => require("../campaigns.js");
  const answer = async (s, res, fn) => { if (!requireAdmin(s, res)) return; try { await fn(); } catch (e) { bad(res, e.message, e.status || 400); } };

  /* The store's campaigns, newest first, each with how many were sent, skipped and failed, and what may be done next; and the audiences, channels and segments a campaign can use. */
  function apiCampaigns(req, res, url, s) { return answer(s, res, () => json(res, 200, { campaigns: CA().list(T(s)), audiences: CA().SEED.audiences, channels: Object.keys(CA().SEED.channels), segments: CA().segments(T(s)) })); }
  /* Drafts a campaign: `name`, `channel` (email, sms, in_app), `subject`, `body` ({name} and {store} are filled in), and `audience` `{ kind: customers | segment | contacts | company, segment?, company_id? }`. */
  function apiCampaignCreate(req, res, url, s, body) {
    return answer(s, res, () => {
      const base = publicLink ? publicLink(req, s, "api/campaigns/unsubscribe", {}) : null;
      const c = CA().create(T(s), { ...(body || {}), link_base: base ? base + (base.includes("?") ? "&" : "?") + "t=" : "" }, actor(s));
      logAction(s, "campaigns.create", "campaign", c.ref, { channel: c.channel }); json(res, 200, { campaign: c });
    });
  }
  /* One campaign: its counts, why people were skipped, how many are still to go, and how many unsubscribed. */
  function apiCampaign(req, res, url, s, body, id) { return answer(s, res, () => json(res, 200, { campaign: CA().status(T(s), id) })); }
  /* How many it would reach now, and how many it would skip and why — before it is sent. */
  function apiCampaignPreview(req, res, url, s, body, id) { return answer(s, res, () => json(res, 200, CA().preview(T(s), id))); }
  /* Sends a draft or scheduled campaign now — the list is built and the first batch goes — or sends the next batch of one already sending. */
  function apiCampaignSend(req, res, url, s, body, id) { return answer(s, res, async () => { const c = await CA().send(T(s), id); logAction(s, "campaigns.send", "campaign", c.ref, { sent: c.sent }); json(res, 200, { campaign: c }); }); }
  /* Schedules a draft for `at`; the platform sends it when the time comes. */
  function apiCampaignSchedule(req, res, url, s, body, id) { return answer(s, res, () => { const c = CA().schedule(T(s), id, (body || {}).at); logAction(s, "campaigns.schedule", "campaign", c.ref, { at: c.scheduled_at }); json(res, 200, { campaign: CA().get(T(s), id) }); }); }
  /* Cancels a campaign: whoever has not been sent to yet is not. */
  function apiCampaignCancel(req, res, url, s, body, id) { return answer(s, res, () => { const c = CA().cancel(T(s), id); logAction(s, "campaigns.cancel", "campaign", c.ref, {}); json(res, 200, { campaign: CA().get(T(s), id) }); }); }
  /* The link in every campaign message (`t`, the recipient's own token): withdraws their consent for the campaign's purpose and says so. Needs no sign-in. */
  function apiCampaignUnsubscribe(req, res, url) {
    const r = CA().unsubscribe(url.searchParams.get("t"));
    const esc = v => String(v).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
    res.writeHead(r.ok ? 200 : 404, { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" });
    res.end(`<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Unsubscribed</title></head><body style="font-family:system-ui,sans-serif;max-width:32rem;margin:4rem auto;padding:0 1rem">` +
      (r.ok ? `<h1>You are unsubscribed</h1><p>${esc(r.store)} will not send you marketing messages any more. You can change this in your account's privacy settings.</p>` : `<h1>This link is not valid</h1><p>It may have been copied incompletely.</p>`) + `</body></html>`);
  }

  /* ---------- journeys (lib/journeys.js) ---------- */
  const JR = () => require("../journeys.js");
  const base = (req, s) => { const b = publicLink ? publicLink(req, s, "api/campaigns/unsubscribe", {}) : null; return b ? b + (b.includes("?") ? "&" : "?") + "t=" : ""; };
  /* The store's journeys, newest first, each with who entered, is in it, finished or left, and each step's sends, opens, clicks and unsubscribes; and the triggers, exits and channels a journey can use. */
  function apiJourneys(req, res, url, s) { return answer(s, res, () => json(res, 200, { journeys: JR().list(T(s)), ...JR().vocabulary(), segments: CA().segments(T(s)), audiences: CA().SEED.audiences })); }
  /* Drafts a journey: `name`, `trigger` (what starts it), `steps` `[{ wait_minutes, channel, subject?, body }]`, `exit_on` (events that take a person out), `reenter` (each time, not once), `segment` (only its members). */
  function apiJourneyCreate(req, res, url, s, body) { return answer(s, res, () => { const j = JR().create(T(s), { ...(body || {}), link_base: base(req, s) }, actor(s)); logAction(s, "journeys.create", "journey", j.ref, { trigger: j.trigger_on }); json(res, 200, { journey: j }); }); }
  /* One journey with its steps and their numbers, and the people in it (`status` narrows them). */
  function apiJourney(req, res, url, s, body, id) { return answer(s, res, () => json(res, 200, { journey: JR().get(T(s), id), people: JR().people(T(s), id, { status: url.searchParams.get("status") || "" }) })); }
  /* Changes a draft or paused journey: any of `name`, `trigger`, `steps`, `exit_on`, `reenter`, `segment`. */
  function apiJourneyUpdate(req, res, url, s, body, id) { return answer(s, res, () => { const j = JR().update(T(s), id, body || {}); logAction(s, "journeys.update", "journey", j.ref, {}); json(res, 200, { journey: j }); }); }
  /* Starts (or resumes) a journey: from now, the people it names enter it. */
  function apiJourneyStart(req, res, url, s, body, id) { return answer(s, res, () => { const j = JR().start(T(s), id); logAction(s, "journeys.start", "journey", j.ref, {}); json(res, 200, { journey: j }); }); }
  /* Pauses a journey: nobody enters and nothing is sent until it is started again. */
  function apiJourneyPause(req, res, url, s, body, id) { return answer(s, res, () => { const j = JR().pause(T(s), id); logAction(s, "journeys.pause", "journey", j.ref, {}); json(res, 200, { journey: j }); }); }
  /* Ends a journey for good: whoever is in it gets nothing more. */
  function apiJourneyEnd(req, res, url, s, body, id) { return answer(s, res, () => { const j = JR().end(T(s), id); logAction(s, "journeys.end", "journey", j.ref, {}); json(res, 200, { journey: j }); }); }
  /* Enrols an `audience` (as campaigns name them) in a live journey that people enter by hand; those without marketing consent are skipped. */
  function apiJourneyEnrol(req, res, url, s, body, id) { return answer(s, res, () => { const r = JR().enrolAudience(T(s), id, (body || {}).audience); logAction(s, "journeys.enrol", "journey", r.journey.ref, { entered: r.entered }); json(res, 200, r); }); }
  /* Sends the journey steps that are due now, and enters people who left their carts. */
  function apiJourneysRun(req, res, url, s) { return answer(s, res, async () => json(res, 200, await JR().sweep(T(s)))); }
  /* A tracked link in a message (`t`, the message's own token): `o=1` counts an open and answers a one-pixel image; `n` counts a click on the message's n-th link and sends the reader on to it. Needs no sign-in. */
  function apiTrack(req, res, url) {
    const t = url.searchParams.get("t"), open = url.searchParams.get("o") === "1";
    const r = CA().track(t, url.searchParams.get("n"), open);
    if (open) { res.writeHead(200, { "Content-Type": "image/gif", "Cache-Control": "no-store, private" }); return res.end(Buffer.from("R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7", "base64")); }
    if (!r.ok) return bad(res, "This link is not valid", 404);
    res.writeHead(302, { Location: r.to, "Cache-Control": "no-store, private", "Referrer-Policy": "no-referrer" }); res.end();
  }

  return [
    ["GET /api/admin/journeys", apiJourneys],
    ["POST /api/admin/journeys", apiJourneyCreate],
    ["POST /api/admin/journeys/run", apiJourneysRun],
    ["GET /api/admin/journeys/:id", (r, re, u, s, b, p) => apiJourney(r, re, u, s, b, p)],
    ["PUT /api/admin/journeys/:id", (r, re, u, s, b, p) => apiJourneyUpdate(r, re, u, s, b, p)],
    ["POST /api/admin/journeys/:id/start", (r, re, u, s, b, p) => apiJourneyStart(r, re, u, s, b, p)],
    ["POST /api/admin/journeys/:id/pause", (r, re, u, s, b, p) => apiJourneyPause(r, re, u, s, b, p)],
    ["POST /api/admin/journeys/:id/end", (r, re, u, s, b, p) => apiJourneyEnd(r, re, u, s, b, p)],
    ["POST /api/admin/journeys/:id/enrol", (r, re, u, s, b, p) => apiJourneyEnrol(r, re, u, s, b, p)],
    ["GET /api/m", apiTrack],
    ["GET /api/admin/campaigns", apiCampaigns],
    ["POST /api/admin/campaigns", apiCampaignCreate],
    ["GET /api/admin/campaigns/:id", (r, re, u, s, b, p) => apiCampaign(r, re, u, s, b, p)],
    ["GET /api/admin/campaigns/:id/preview", (r, re, u, s, b, p) => apiCampaignPreview(r, re, u, s, b, p)],
    ["POST /api/admin/campaigns/:id/send", (r, re, u, s, b, p) => apiCampaignSend(r, re, u, s, b, p)],
    ["POST /api/admin/campaigns/:id/schedule", (r, re, u, s, b, p) => apiCampaignSchedule(r, re, u, s, b, p)],
    ["POST /api/admin/campaigns/:id/cancel", (r, re, u, s, b, p) => apiCampaignCancel(r, re, u, s, b, p)],
    ["GET /api/campaigns/unsubscribe", apiCampaignUnsubscribe]
  ];
} };
