/* LUXORA Platform — campaigns domain routes (lib/campaigns.js; _registry/business-domains.json).
   A store's campaigns under its campaigns section (the Growth role holds it), and the one public
   route every message links to: the unsubscribe link, which needs no sign-in. */
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

  return [
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
