# U88 — Social & Community Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U88-social` |
| Layer | L5 Business Capability |
| Domain | 06 Experience |
| Steward | `ucos:org:experience-social` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P5 (community & UGC, social login/sharing), P6 (social commerce, social-network platforms as compositions) |
| Depends on | U11 Party (profiles), U09 Identity (social login federation), U43 Asset (media), U40 Communication (notifications, DMs), U70 Trust & Reputation (ratings, karma), U69 Risk (abuse), U66 Privacy, U03 Policy (ReBAC — OpenFGA option), U44 Search, U52 Recommendation (feeds), U62 Integration (external social networks), U13 Temporal (see TEMPORAL-BINDING-MATRIX) |
| Depended on by | marketplaces (seller follow, Q&A), media/OTT (comments), education (forums), social-network-class platforms (Instagram/Reddit-like compositions), U86 (social publishing) |
| Master references | User requirement "social media" (A-33); master Communication "Social" channel; Mobility/Marketplace "Community" |

> Social owns **relationships and user-generated interaction between people (and agents) on tenant platforms, and integration with external social networks**: social graph (follow, friend, block, mute), profiles (public persona over Party), posts/threads/comments/reactions, product Q&A, groups/communities, feeds (ranking via U52), mentions/hashtags, moderation (automated + human, appeals), creator/affiliate features, social commerce (shoppable posts, live shopping with U41), and **external social integration** (social login, share, publish/schedule to external networks, listen/ingest mentions, social ads via U33).

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| SOC-L1 | All UGC passes moderation pipelines appropriate to risk (pre/post moderation), with transparent notice-and-action and appeals. | Moderation workflow mandatory for UGC capabilities. |
| SOC-L2 | Graph edges respect privacy settings and blocks globally (search, feeds, DMs, mentions). | ReBAC policies; block list checked in all read paths. |
| SOC-L3 | Minors' safety rules (no DMs from unknown adults, default private profiles, no targeted ads) apply by default. | Policy + `isMinor` context. |
| SOC-L4 | Platform obligations (illegal content takedown timelines, transparency reporting, grievance officers, traceability where mandated) are implemented as controls. | U67 packs: EU DSA, India IT Rules 2021, UK Online Safety Act, etc. |
| SOC-L5 | External social network actions occur only with the user's/brand's connected account authorisation and network API terms. | Connector scopes (U62). |

## 2. Objects
`SocialProfile { party, handle (unique per tenant), bio, avatar, visibility, verified badge (U70) }` · `Edge { from, to, kind: follow|friend|block|mute|member-of, state }` · `Post { author, kind: text|image|video|link|product|poll|live, body, media, mentions, tags, productRefs (shoppable), visibility, status: published|pending-review|removed|hidden }` · `Comment`, `Reaction` · `Question/Answer` (product Q&A; links to Listing/GPID) · `Group { name, rules, moderators, visibility, membership policy }` · `ModerationCase { content, signals (AI scores, reports), decision, policy violated, action, appeal }` · `ConnectedSocialAccount { owner (brand/user), network (Instagram, X, Facebook, LinkedIn, YouTube, TikTok, WhatsApp channels…), scopes, token (vault) }` · `ScheduledPost` (external publish) · `Mention` (listening).

## 3. Commands, Queries, Events, APIs
Commands: `Follow/Unfollow/Block/Mute`, `CreatePost`, `Comment`, `React`, `AskQuestion`, `Answer`, `Report`, `Moderate(decision)`, `Appeal`, `CreateGroup/Join`, `ConnectSocialAccount`, `SchedulePublish`, `IngestMentions`.
Queries: `Feed(party, kind: following|for-you|group)`, `Thread(post)`, `QandA(listing)`, `GraphNeighbours(party)`.
Events: `social.post.created|removed`, `social.edge.created`, `social.moderation.decided`, `social.question.answered`.
```text
POST /v1/social/posts   GET /v1/social/feed?kind=   POST /v1/social/edges   POST /v1/social/reports
POST /v1/social/moderation/{case}:decide   POST /v1/social/connected-accounts   POST /v1/social/scheduled-posts
```

## 4. Gaps
```prolog
gap(ugc_without_moderation, T)  :- tenant(T), capability(T, social.posts), not capability(T, social.moderation).
gap(platform_obligation_missing, T, J) :- tenant(T), intermediary(T), in_scope(T, J), obligation(J, intermediary, C), not implemented(T, C).
gap(no_csam_detection, T)       :- tenant(T), accepts_ugc_images(T), not control_implemented(T, ctrl:csam-detection).
```

## 5. AI, Ops, UI, Scale
AI: moderation classifiers (text/image/video), spam/bot detection, feed ranking, Q&A answer suggestion from product facts (cited, labelled AI), social listening sentiment. Signals: `posts_total`, `moderation_backlog`, `takedown_time_hours`, `appeal_overturn_rate`, `feed_latency_ms`. Views: `feed`, `post.composer`, `profile`, `group`, `qa.widget` (PDP), `moderation.console`, `social.publishing.calendar` (external networks), `social.listening.dashboard`. Scale: social-network class → graph store (sharded), fan-out-on-write/read hybrid feeds, media CDN; T1.

## Appendix
- **C.** 0.1.0.
