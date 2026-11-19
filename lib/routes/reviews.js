/* LUXORA Platform — reviews domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the reviews domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "reviews", routes(kit) {
  const { CFG, T, actor, all, bad, entity, get, isAdmin, json, logAction, ownerFor, requireAdmin, run, states, ugc } = kit;

  /* ---------------- reviews / gifts / viewed ---------------- */
  function apiReviewAdd(req, res, url, s, body, id) {
    if (!CFG(s).features.reviews) return bad(res, "Reviews are disabled", 403);
    if (!get("SELECT id FROM products WHERE tenant_id=? AND id=?", T(s), id)) return bad(res, "Unknown product", 404);
    const r = Math.max(1, Math.min(5, Number(body.rating) || 5));
    const name = s.user_id ? get("SELECT name FROM users WHERE id=?", s.user_id).name : "A customer";
    const media = CFG(s).ugc.reviewMedia && Array.isArray(body.media) ? body.media.slice(0, 5) : [];
    const out = ugc.addReview(T(s), id, ownerFor(s), name, { rating: r, title: body.title, body: body.body, media }, !!CFG(s).ugc.moderation);
    logAction(s, "review.create", "review", out.id, { rating: r, state: out.state });
    json(res, 200, { ok: true, id: out.id, state: out.state, moderated: !!CFG(s).ugc.moderation });
  }
  function apiReviewVote(req, res, url, s, body, id) {
    if (!CFG(s).features.reviews) return bad(res, "Reviews are disabled", 403);
    try {
      const v = ugc.vote(T(s), "review", id, ownerFor(s), String(body.dir || "up") === "down" ? "down" : "up");
      json(res, 200, v);
    } catch (e) { bad(res, e.message, 404); }
  }
  function apiReviewReply(req, res, url, s, body, id) {
    if (!CFG(s).ugc.reviewReplies) return bad(res, "Review replies are disabled", 403);
    if (!requireAdmin(s, res)) return;
    const a = actor(s);
    try { json(res, 200, { reply: ugc.replyReview(T(s), id, a[2] || "Store", s.platform_admin ? "platform" : "admin", body.body) }); }
    catch (e) { bad(res, e.message, 404); }
  }
  function apiReviewModerate(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try {
      const rv = ugc.setReviewState(T(s), id, String(body.state || ""));
      logAction(s, "review.moderate", "review", id, { state: body.state });
      json(res, 200, { review: rv });
    } catch (e) { bad(res, e.message, 400); }
  }
  /* ---------------- Q&A ---------------- */
  function apiQnaAsk(req, res, url, s, body, id) {
    if (!CFG(s).features.qna) return bad(res, "Questions & Answers are disabled", 403);
    if (!get("SELECT id FROM products WHERE tenant_id=? AND id=?", T(s), id)) return bad(res, "Unknown product", 404);
    const name = s.user_id ? get("SELECT name FROM users WHERE id=?", s.user_id).name : "A customer";
    const q = ugc.askQuestion(T(s), id, ownerFor(s), name, body.body || body.question, !!CFG(s).ugc.moderation);
    logAction(s, "qna.ask", "question", q.id, { product: id });
    json(res, 200, { ok: true, ...q, moderated: !!CFG(s).ugc.moderation });
  }
  function apiQnaAnswer(req, res, url, s, body, id) {
    if (!CFG(s).features.qna) return bad(res, "Questions & Answers are disabled", 403);
    const a = actor(s);
    /* a guest's actor name is their session id — never publish it; and a guest is a customer,
       not a "seller" badge */
    const role = s.platform_admin ? "platform" : (isAdmin(s) ? "admin" : "customer");
    const author = a[0] === "guest" ? "A customer" : (a[2] || "A customer");
    try {
      const an = ugc.answerQuestion(T(s), id, ownerFor(s), author, role, body.body, !!CFG(s).ugc.moderation);
      logAction(s, "qna.answer", "answer", an.id, { question: id });
      json(res, 200, { ok: true, ...an, moderated: !!CFG(s).ugc.moderation });
    } catch (e) { bad(res, e.message, 404); }
  }
  function apiQnaVote(req, res, url, s, body, id) {
    if (!CFG(s).features.qna) return bad(res, "Questions & Answers are disabled", 403);
    const entity = String(url.searchParams.get("kind") || "question") === "answer" ? "answer" : "question";
    try { json(res, 200, ugc.vote(T(s), entity, id, ownerFor(s), String(body.dir || "up") === "down" ? "down" : "up")); }
    catch (e) { bad(res, e.message, 404); }
  }
  function apiQnaModerate(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    const kind = String(url.searchParams.get("kind") || "question") === "answer" ? "answer" : "question";
    try { json(res, 200, { row: ugc.setQnaState(T(s), kind, id, String(body.state || "")) }); }
    catch (e) { bad(res, e.message, 400); }
  }
  function apiAdminReviews(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { reviews: all(`SELECT rv.id, rv.product_id, rv.name, rv.rating, rv.title, rv.body, rv.verified, rv.state, rv.votes_helpful, rv.votes_total, rv.created_at, p.title product_title FROM reviews rv LEFT JOIN products p ON p.tenant_id=rv.tenant_id AND p.id=rv.product_id WHERE rv.tenant_id=? ORDER BY rv.created_at DESC LIMIT 100`, T(s)) });
  }
  function apiAdminUgcQueue(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const q = ugc.moderationQueue(T(s));
    json(res, 200, { ...q, pending: q.reviews.length + q.questions.length + q.answers.length, states: ugc.STATES });
  }
  function apiAdminReviewDelete(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    run("DELETE FROM reviews WHERE id=? AND tenant_id=?", Number(id), T(s));
    logAction(s, "review.delete", "review", id);
    json(res, 200, { ok: true });
  }

  return [
    ["POST /api/reviews/:id", (r, re, u, s, b, p) => apiReviewAdd(r, re, u, s, b, p)],
    ["POST /api/reviews/:id/vote", (r, re, u, s, b, p) => apiReviewVote(r, re, u, s, b, p)],
    ["POST /api/reviews/:id/reply", (r, re, u, s, b, p) => apiReviewReply(r, re, u, s, b, p)],
    ["PUT /api/admin/reviews/:id/moderate", (r, re, u, s, b, p) => apiReviewModerate(r, re, u, s, b, p)],
    ["GET /api/admin/ugc/queue", apiAdminUgcQueue],
    ["POST /api/qna/:id/question", (r, re, u, s, b, p) => apiQnaAsk(r, re, u, s, b, p)],
    ["POST /api/qna/question/:id/answer", (r, re, u, s, b, p) => apiQnaAnswer(r, re, u, s, b, p)],
    ["POST /api/qna/:id/vote", (r, re, u, s, b, p) => apiQnaVote(r, re, u, s, b, p)],
    ["PUT /api/admin/qna/:id/moderate", (r, re, u, s, b, p) => apiQnaModerate(r, re, u, s, b, p)],
    ["GET /api/admin/reviews", apiAdminReviews],
    ["DELETE /api/admin/reviews/:id", (r, re, u, s, b, p) => apiAdminReviewDelete(r, re, u, s, b, p)]
  ];
} };
