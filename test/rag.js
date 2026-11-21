/* LUXORA Platform — the knowledge base (lib/rag.js): collections any app keeps, the four ways a
   collection grows (expert, AI-assisted, self-learning, auto-evolving), experts by store role,
   versions and rollback, proposals, feedback, and retrieval by words and tags. */
"use strict";
const path = require("path"), fs = require("fs");
const DB = path.join(__dirname, "rag.db");
for (const x of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + x, { force: true }); } catch (e) { } }
process.env.LX_DB = DB;
const quiet = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = quiet;
const rag = require("../lib/rag.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x) : ""))); };
const throws = (fn, re) => { try { fn(); return false; } catch (e) { return re.test(e.message); } };
const T = db.masterTenant().id;
const astrologer = { name: "Asha (astrologer)", roleKey: "astrologer" }, support = { name: "Sam (support)", roleKey: "support" };
const roles = ["owner", "manager", "support", "astrologer"];

try {
  console.log("▸ A COLLECTION, ITS MODE AND ITS EXPERTS ARE SETTINGS");
  ok(throws(() => rag.saveCollection(T, "astro", { mode: "wild" }, roles), /Unknown mode/), "an unknown mode is refused");
  ok(throws(() => rag.saveCollection(T, "astro", { expertRoles: ["wizard"] }, roles), /Unknown role/), "an expert role must be one of the store's roles");
  const c = rag.saveCollection(T, "astro", { label: "Astrology", mode: "expert", expertRoles: ["astrologer"] }, roles);
  ok(c.mode === "expert" && c.expertRoles[0] === "astrologer", "the astrology collection is created in Expert mode, owned by the astrologer role", c);

  console.log("▸ EXPERT MODE");
  const e1 = rag.addEntry(T, "astro", { title: "Mars in the 7th house", body: "Mars in the seventh house brings energy and friction to partnerships.", tags: ["planet:mars", "house:7", "topic:placement"] }, astrologer);
  ok(e1.status === "approved" && e1.source === "expert", "an expert's entry is approved on save", e1);
  const e2 = rag.addEntry(T, "astro", { title: "Moon in Rohini", body: "Rohini Moon is said to favour beauty and stability.", tags: ["planet:moon", "nakshatra:rohini"] }, support);
  ok(e2.status === "review", "a non-expert's entry waits for review", e2.status);
  ok(throws(() => rag.addEntry(T, "astro", { title: "x", body: "y", source: "ai" }, support), /does not draft/), "the AI may not draft in Expert mode");
  ok(throws(() => rag.review(T, e2.id, "approve", support), /Only the collection's experts/), "a non-expert cannot approve");
  const ap = rag.review(T, e2.id, "approve", astrologer);
  ok(ap.status === "approved" && ap.approved_by === astrologer.name, "the astrologer approves it", ap);

  console.log("▸ RETRIEVAL — ONLY APPROVED ENTRIES, BY WORDS AND TAGS");
  rag.addEntry(T, "astro", { title: "Saturn return", body: "Draft notes not yet reviewed about Saturn.", tags: ["planet:saturn"] }, support);
  const byWord = rag.search(T, "astro", { q: "partnerships seventh" });
  ok(byWord.length >= 1 && byWord[0].id === e1.id, "a question finds the entry that answers it", byWord.map(x => x.title));
  ok(!rag.search(T, "astro", { q: "Saturn" }).length, "an entry awaiting review is never retrieved");
  const byTag = rag.search(T, "astro", { tags: ["nakshatra:rohini"] });
  ok(byTag.length === 1 && byTag[0].id === e2.id, "tags from a chart find their entries", byTag.map(x => x.title));
  ok(rag.search(T, "astro", { q: "Mars", tags: ["house:7"] })[0].id === e1.id, "words and tags together narrow the answer");

  console.log("▸ VERSIONS AND ROLLBACK");
  const rv = rag.revise(T, e1.id, { body: "Mars in the 7th: assertive partners; channel the energy into shared goals." }, astrologer, "clearer");
  ok(!rv.proposed && rv.entry.version > e1.version, "an expert's revision lands at once as a new version", rv.entry && rv.entry.version);
  const pr = rag.revise(T, e1.id, { body: "Mars in 7th is always bad." }, support, "my view");
  ok(pr.proposed && !pr.applied, "a non-expert's revision becomes a proposal", pr);
  const h = rag.history(T, e1.id);
  ok(h.length >= 2 && h.some(v => v.reason === "clearer"), "every version is kept with who changed it and why", h.map(v => v.reason));
  const back = rag.rollback(T, e1.id, 1, astrologer);
  ok(/energy and friction/.test(back.body), "an expert restores the first version", back.body);
  ok(throws(() => rag.rollback(T, e1.id, 1, support), /experts roll/), "a non-expert cannot roll back");
  ok(rag.decideProposal(T, pr.proposal.id, "reject", astrologer).rejected === pr.proposal.id, "the expert rejects the proposal");

  console.log("▸ AI-ASSISTED MODE");
  rag.saveCollection(T, "astro", { mode: "ai_assisted" }, roles);
  const ai = rag.addEntry(T, "astro", { title: "Jupiter in the 9th", body: "AI draft: Jupiter in the ninth house favours learning.", tags: ["planet:jupiter", "house:9"], source: "ai", confidence: 0.7 }, support);
  ok(ai.status === "review" && ai.source === "ai", "an AI draft waits for an expert", ai);
  const plain = rag.feedback(T, { entry_id: e1.id, rating: 5 }, { name: "a customer" });
  ok(plain.ok && !plain.proposed, "a rating is recorded; in AI-assisted mode it proposes nothing", plain);
  ok(throws(() => rag.feedback(T, { entry_id: e1.id, rating: 9 }, support), /rating is 1 to 5/), "a rating outside 1–5 is refused");

  console.log("▸ SELF-LEARNING MODE");
  rag.saveCollection(T, "astro", { mode: "self_learning" }, roles);
  const fb = rag.feedback(T, { entry_id: e1.id, rating: 3, correction: "Mention the 7th house also covers business partners." }, { name: "a customer" });
  ok(fb.proposed && !fb.applied, "a correction becomes a proposed revision, not a change", fb);
  ok(rag.proposals(T, "astro").some(p => p.id === fb.proposed && p.source === "learned"), "the proposal waits in the expert's queue, marked as learned");
  ok(!/business partners/.test(rag.search(T, "astro", { tags: ["house:7"] })[0].body), "the live entry is unchanged until an expert approves");

  console.log("▸ AUTO-EVOLVING MODE");
  rag.saveCollection(T, "astro", { mode: "auto_evolving", thresholds: { minConfidence: 0.8, minConfirmations: 2, minVotes: 3, minRating: 4 } }, roles);
  const low = rag.revise(T, e1.id, { body: "Low-confidence idea.", source: "learned", confidence: 0.4 }, { name: "learner" }, "weak");
  ok(low.proposed && !low.applied, "a proposal below the confidence threshold does not go live", low.applied);
  const strong = rag.revise(T, e1.id, { body: "Mars in the 7th: energetic partnerships, in marriage and in business.", source: "learned", confidence: 0.9 }, { name: "learner" }, "strong");
  ok(strong.proposed && !strong.applied, "a confident proposal waits for confirmations", strong.applied);
  rag.confirmProposal(T, strong.proposal.id);
  const done = rag.confirmProposal(T, strong.proposal.id);
  ok(done.applied && /business/.test(done.applied.body), "two confirmations carry it over the threshold and it goes live by itself", done);
  const hh = rag.history(T, e1.id);
  ok(hh[0].changed_by === "auto-evolving" && /auto-applied/.test(hh[0].reason), "the automatic change is recorded as the engine's, with its reasons", hh[0]);
  const restored = rag.rollback(T, e1.id, hh[1].version, astrologer);
  ok(!/in marriage and in business/.test(restored.body) && restored.version > hh[0].version, "an expert can still roll an automatic change back", restored.body);

  console.log("▸ COLLECTIONS ARE PER STORE AND PER APP");
  rag.saveCollection(T, "legal_help", { label: "Legal help", mode: "expert", expertRoles: ["owner"] }, roles);
  ok(rag.collections(T).map(x => x.key).join(",") === "astro,legal_help", "any app keeps its own collection", rag.collections(T).map(x => x.key));
  ok(!rag.search(T, "legal_help", { q: "Mars" }).length, "one collection's knowledge never answers another's");
} catch (e) { failed++; console.log("  ✗ harness error: " + (e && e.stack || e)); }
for (const x of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + x, { force: true }); } catch (e) { } }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
