# U40 — Communication Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U40-communication` |
| Layer | L5 Business Capability |
| Domain | 06 Experience |
| Steward | `ucos:org:experience-messaging` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P1 (transactional email/SMS/push/WhatsApp, templates, preferences), P3 (conversations, agent desktop, masked calling), P4 (campaign orchestration) |
| Depends on | U11 Party (ContactPoints, consents), U66 Privacy (purposes, consent), U15 Localization (templates), U13 Temporal (quiet hours, scheduling), U43 Asset (attachments), U57 adapters (messaging providers), U61 Event (triggers) |
| Depended on by | every universe that notifies (Order, Fulfillment, Payment, Identity OTP, Support, Governance approvals, Workflow tasks), U39 Support, U51 Agents (agent-to-agent/human messages) |
| Master references | §6.3 (notifications ruling), §17.1 (messaging connectors), §6.2 U40 |

> Communication owns **every message UCOS sends or receives with people (and between agents)**: channels, templates, notification rules (event → message), preference & consent enforcement, delivery orchestration (fallbacks, quiet hours, rate limits), conversations (two-way threads across channels), masked contact (proxy numbers/relay emails), delivery tracking, and campaigns (P4). Universes emit events and template ids; they never call messaging providers.

---

## 1. Laws

| ID | Law | Enforcement |
|---|---|---|
| COMM-L1 | Messages are sent only to verified contact points with valid consent for the message purpose (transactional purposes per lawful basis; marketing requires opt-in where law requires). | Send pipeline checks U11/U66; `COMM_NO_CONSENT`. |
| COMM-L2 | All content comes from versioned, localised templates (or approved AI drafts for conversations); no free-form system strings. | Template registry; L10N-L1. |
| COMM-L3 | Channel-specific regulation is enforced: DLT template registration (India SMS), WhatsApp template approval, CAN-SPAM/unsubscribe, quiet hours/DND registries. | Channel adapters + decision tables + gap rules. |
| COMM-L4 | Direct contact details are not exposed between parties who don't need them (buyer↔seller↔driver); masked relays are used. | Policy obligations + proxy services. |
| COMM-L5 | Every message has an idempotency key derived from the triggering event; duplicate sends are suppressed. | Send log unique key. |

## 2. Objects
- **`Channel`** `{ kind: email|sms|push|whatsapp|rcs|in-app|voice|webhook|agent, provider adapter, sender identities (domains with SPF/DKIM/DMARC, sender IDs, WABA numbers), region }`
- **`Template`** `{ id (e.g. order.confirmed), purpose (PurposeRef), category: transactional|service|marketing|security, channelVariants: {email: {subject, html, text}, sms: {body, dltTemplateId?}, whatsapp: {providerTemplateName, params}, push: {title, body, deeplink}}, locales (L10n bundles), variables schema, version, approvals per channel/provider }`
- **`NotificationRule`** `{ id, on: EventType + filter, recipient: path to PartyRef/role, template, channelsPreference: ordered, fallback: {after: Duration, to: channel}, quietHours: TemporalPolicyRef, priority: critical|high|normal|low, dedupWindow }`
- **`Message`** `{ id, rule?, template@version, recipient (party + contact point ref), channel, rendered (stored per retention; restricted content redacted), status: queued|sent|delivered|read|failed|bounced|suppressed, providerRef, cost, triggeredBy (event id), at: TimePoint }`
- **`Conversation`** (P3) `{ id, participants (parties/agents/support agents), channel threads, subject ref (order/case), messages, status, assignedQueue }`
- **`ProxyContact`** (P3) `{ between: [party, party], channel: voice|sms, proxy number/address, subject ref, validity: TemporalPolicyRef (e.g. until delivery + 24h) }`
- **`Campaign`** (P4) `{ audience segment, template, schedule (Temporal), throttle, experiment, budget }`

## 3. Send pipeline (normative)
```text
event → match NotificationRules → for each recipient:
  resolve contact via party.ContactFor(party, purpose, channelPreference)   # consented+verified only
  apply preference center (frequency caps, opted-out categories), DND/quiet hours (Temporal; critical may bypass per law, e.g. OTP)
  render template (locale from party preference → ctx), validate variables & lengths per channel
  dedupe (idempotency key = ruleId:eventId:recipient:channel)
  send via channel adapter (rate-limited per provider/sender) → status callbacks → Message status
  fallback if not delivered within window (e.g. push → SMS)
```

## 4. Commands, Queries, Events, APIs
Commands: `DefineTemplate`/`PublishTemplate` (governed; legal/marketing templates need review), `DefineNotificationRule`, `SendDirect(template, recipient, purpose)` (for system flows like OTP), `StartConversation`, `PostMessage`, `CreateProxyContact`, `CreateCampaign` (P4), `Unsubscribe(token)`.
Queries: `MessagesFor(party|subject)`, `DeliveryStats(template, range)`, `Preview(template, locale, sampleData)`.
Events: `communication.message.sent|delivered|failed|bounced|opened|clicked` (privacy-aware tracking only with consent), `communication.conversation.message-received`, `communication.unsubscribed`.
Port: `messaging.provider@1` (`Send, Status, ParseWebhook, RegisterTemplate`) — adapters: SES/SendGrid/Postmark, Twilio/Gupshup/Kaleyra/MSG91, Meta WhatsApp Cloud API/BSPs, FCM/APNs, Exotel/Twilio Voice (proxy).
```text
POST /v1/comm/templates      POST /v1/comm/rules      POST /v1/comm/send
GET  /v1/comm/messages?party=&subject=      POST /v1/comm/conversations/{id}/messages
GET  /u/{token}  (unsubscribe landing; public)
```
Errors: `COMM_NO_CONSENT`, `COMM_NO_CONTACT`, `COMM_TEMPLATE_NOT_APPROVED`, `COMM_QUIET_HOURS` (deferred), `COMM_PROVIDER_REJECTED`.

## 5. Decision tables
`communication.channel-preference` (by purpose/priority/region), `communication.quiet-hours` (by jurisdiction; e.g. telemarketing hours), `communication.frequency-caps`, `communication.fallback-windows`, `communication.retention` (message content retention by category).

## 6. Security & Compliance
OTP/security messages: no sensitive data in body beyond code; links signed; email authentication (SPF/DKIM/DMARC/BIMI) gate; phishing-resistant patterns (no login links in marketing). Laws: TRAI TCCCPR (DLT, headers, scrubbing), GDPR/ePrivacy/PECR, CAN-SPAM, TCPA (US calls/SMS), UAE TDRA rules, WhatsApp Business Policy. Content retention minimal; masked calling recordings consent-based.

## 7. Gaps
```prolog
gap(template_missing_locale, T, L)  :- template(T), used_in_tenant(T, X), tenant_locale(X, L), not template_locale(T, L).
gap(dlt_unregistered, T)            :- template(T), channel_variant(T, sms), used_in_jur(T, jur:IN), not dlt_registered(T).
gap(no_unsubscribe, T)              :- template(T), category(T, marketing), not unsubscribe_link(T).
gap(email_auth_missing, D)          :- sender_domain(D), not (spf(D), dkim(D), dmarc(D)).
gap(event_without_notification, E)  :- customer_facing_event(E), expected_notification(E), not notification_rule_for(E).
```

## 8. AI
Reply drafting in conversations (support), tone/localisation of templates (proposals), send-time optimisation (P4, within quiet hours), intent detection on inbound messages (routing to Support/Order actions). Agents converse via in-app/WhatsApp with disclosure that the user is talking to an AI (policy obligation per jurisdiction).

## 9. Operations, UI, Scale
Signals: `messages_sent_total{channel,template}`, `delivery_ratio{channel,provider}`, `otp_delivery_latency_s` (SLO p95 < 10 s), `bounce_ratio`, `complaint_ratio`, `provider_errors`. Views: `comm.template.editor` (multi-channel preview, locale tabs, variable sample data, approval status per provider), `comm.rules.editor` (event → template mapping), `comm.message.log` (per party/order), `comm.preference.center` (end-user), `conversation.inbox` (P3 agent desktop). Scale: 10⁹ messages/month platform; queue-based; provider rate limits respected; T1 (OTP path T0).

## Appendix
- **C.** 0.1.0.

## Appendix E — Communication completeness (amendment A-64)

### E.1 Channel registry (all channels are data; providers are adapter packs)
| Channel kind | Methods (adapter selection keys) | Phase | Typical providers (adapters) | Notes |
|---|---|---|---|---|
| Email | `email` | P1 | SES, SendGrid, Postmark | SPF/DKIM/DMARC gate; inbound parse via E.3 |
| SMS | `sms` | P1 | DLT-registered India providers, UAE sender-ID providers, global CPaaS | OTP and transactional; country rules as data |
| WhatsApp | `whatsapp` | P1 | Meta Cloud API via a BSP | Template approval; 24-hour session window (Temporal policy) |
| Web push | `web-push` | P1 | VAPID (self-hosted) | Consent-gated in the browser |
| Mobile push | `push-android`, `push-ios` | P3 | FCM, APNs | Device tokens are `ContactPoint{channel: push-token}`, bound to a Device identity |
| In-app notification centre | `in-app` | P1 | internal (`communication.inapp`) | §E.2 |
| RCS | `rcs` | P4 | RCS Business Messaging via CPaaS | Falls back to SMS |
| Telegram, LINE, WeChat, Viber, Messenger, Instagram DM | `telegram`, `line`, `wechat`, `viber`, `messenger`, `instagram` | P4 | Platform APIs | Opt-in threads only; platform terms enforced by the connector |
| Voice (calls, IVR, masked calling) | `voice` | P3 | CPaaS (Twilio, Exotel, Plivo class) | Owned by **U109** for sessions; U40 sends voice notifications (TTS) |
| Video | `video` | P3 | WebRTC SFU or CPaaS | Sessions owned by **U109** |
| Live chat (web or app widget) | `live-chat` | P3 | internal real-time (`communication.realtime`) | Routing and agents in **U109** |
| Agent-to-agent | `agent-protocol` | P3 | internal | §E.6 |
| Broadcast and emergency | `broadcast`, `cell-broadcast` (via authority integrations) | P4 | CPaaS bulk; government alert gateways | §E.5 |
| Postal mail | `postal` | P4 | print-and-mail providers | Documents from U42 |

New channels are added as a registry entry plus an adapter pack implementing `messaging.provider@1` (or `rtc.provider@1` for sessions). Templates gain a channel variant. No change to U40 code.

### E.2 In-app notification centre
`Notification { id, recipient (party), category (taxonomy: order, payment, security, social, marketing, system), title/body (LocalizedText via template), deepLink, actions [{label, command}], priority, createdAt: TimePoint, readAt?: TimePoint, archivedAt?: TimePoint, expiresAt?: TimePoint }`.
- Commands: `MarkRead`, `MarkAllRead`, `Archive`, `PerformAction` (executes a command through the bus with the user's context).
- Live delivery over the real-time gateway (§E.4), with unread counts per category.
- Retention by category (U66).
- `communication.inapp` is a delivery method, so notification rules can target `in-app` like any other channel, and fallback chains can include it (for example in-app → push → email).

### E.3 Inbound messages and routing
- `InboundMessage { channel, from (resolved to party via ContactPoint or unknown), to (tenant address/number), threadKey, body, attachments (U43), receivedAt: TimePoint, intent?: classification, routedTo: { case | order | conversation | workflow signal | agent queue }, status }`.
- **Routing rules** are a decision table `communication.inbound-routing` with inputs: channel, address, sender known?, intent, keywords and business hours (Temporal). Outputs: conversation, case (U39), order action (e.g. "CANCEL" reply), opt-out (STOP/UNSUBSCRIBE handled by law, always first), or bot (U109).
- **Inbound email:** MX routing to the parse webhook, then DKIM/SPF verification, attachment scanning (U43), and thread matching via reply tokens.
- **Opt-out keywords** are processed before any other route, in every language configured for the tenant (`l10n` keys).

### E.4 Real-time messaging (conversations between people, and between people and agents)
- **`communication.realtime`:** a WebSocket gateway (per cell, horizontally scaled, tenant-isolated channels) offering presence, typing indicators, delivery and read receipts, and message ordering per conversation (server sequence numbers).
- **Conversation types:** buyer↔seller (marketplace, masked identities), rider↔driver (mobility), customer↔support agent (U109), patient↔practitioner (health pack, end-to-end encrypted option), team chat (U96), group chats (U88 communities).
- **Message types:** text, media (U43), location (U12, temporary), product card (U21), order card (U26), payment request (U29), form (U97), quick replies.
- **Laws:**
  - conversation content follows purpose and retention (U66);
  - moderation (U88 pipeline) applies to user-to-user chat;
  - contact details are masked between parties (COMM-L4);
  - end-to-end encrypted conversations disable server-side AI and moderation features, and say so in the UI.

### E.5 Broadcast and emergency alerts
- `Broadcast { audience (segment U85, geofence U12, role, all-tenants for platform notices), severity: info|warning|critical|emergency, channels (priority ordered), content, schedule (Temporal), approvals (U01 level by severity), throttle, acknowledgementRequired: bool }`.
- Emergency broadcasts may bypass quiet hours and marketing consent only when legally permitted, as a jurisdiction decision `communication.emergency-bypass`. They need dual approval and are fully audited.
- Delivery and acknowledgement tracking, with escalation to the next channel when not acknowledged within a duration.
- Government cell-broadcast systems are reached via authority connectors (U62) for public-sector tenants.

### E.6 Agent-to-agent protocol
- Agents (U51) exchange messages through `agent-protocol` conversations. The envelope carries `from agent, to agent, onBehalfOf, mandate ref (U91/U09 delegation), intent, payload schema ref, reply-to, expiresAt: TimePoint, signature`.
- Transports: internal event bus for UCOS agents; for external agents, HTTPS with signed messages, or MCP and A2A-style protocols via U62 connectors. Every exchange is audited (U68) and policy-checked (P-003).
- Language: U77 `LanguageSystem` kind `machine-protocol`. Schemas are registered in U61.

### E.7 New and extended gap rules
```prolog
gap(channel_without_adapter, T, Ch, J) :- tenant(T), pd_channel(T, Ch), channel_method(Ch, M), in_scope(T, J), not adapter_for(messaging.provider, J, M, _).
gap(push_without_device_binding, T)     :- tenant(T), uses_method(T, push-ios), not capability(T, identity.core).
gap(inbound_without_optout_routing, T)  :- tenant(T), receives_inbound(T), not decision_version(T, communication.inbound-routing).
gap(chat_without_moderation, T)         :- tenant(T), capability(T, communication.realtime), user_to_user_chat(T), not capability(T, social.moderation).
gap(emergency_broadcast_without_dual_approval, T) :- tenant(T), capability(T, communication.broadcast), not authority_quorum(T, broadcast-emergency, 2).
```
