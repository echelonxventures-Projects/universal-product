# U109 — Real-time Communications & Contact Centre Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U109-rtc` |
| Layer | L5 Business Capability / L9 Integration |
| Domain | 06 Experience |
| Steward | `ucos:org:experience-rtc` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P3 (live chat + bot hand-off, voice calls & IVR, masked calling, video sessions, queues & routing, agent desktop, recordings), P4 (workforce forecasting integration, quality management, speech analytics), P6 (telehealth/education/video-KYC packs reuse sessions) |
| Depends on | U40 Communication (channels, real-time gateway, templates), U62 Integration (CPaaS/SFU connectors), U09 Identity (agents, customers, video-KYC verification), U11 Party, U13 Temporal (business hours, queues SLAs, call-backs, schedules), U53 Decision (routing), U60 Workflow (wrap-up, call-back tasks), U66 Privacy (recording consent, retention), U43 Asset (recordings, transcripts), U51 Agent (AI bots), U72 Observability, U39 Support (cases), U46 Workforce (agent schedules, P4) |
| Depended on by | U39 Support, U38 CRM (sales calls), U82 Field Service (dispatch calls), U37 Mobility (rider↔driver masked calls), health/education/fin packs (telehealth, live classes, video KYC), U88 (live sessions), U81 (virtual events) |
| Master references | Communication completeness review (A-65) |

> Real-time Communications owns **synchronous conversations and the contact centre that manages them**: voice calls (inbound/outbound, PSTN/SIP/WebRTC), IVR flows, masked/proxy calling, video sessions (1:1 and group, recordings, screen share), live chat sessions, chatbot/AI-agent front-line with human hand-off, **routing** (queues, skills, priorities, business hours, overflow), agent desktop state (available/busy/wrap-up), call-backs, recordings and transcripts with consent, supervision (monitor/whisper/barge), and contact-centre analytics. Asynchronous messaging stays in U40; ticket/case lifecycle stays in U39.

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| RTC-L1 | Recording and transcription require jurisdiction-appropriate notice/consent (one-party/two-party consent, DPDP/PDPL purpose) captured before recording starts; recordings are encrypted and retention-bound. | IVR/session pre-roll + consent record (U66); recording guard. |
| RTC-L2 | Parties' real numbers/identities are masked by default between customers and workers (drivers, sellers, technicians); proxies expire with the subject (Temporal policy). | Proxy sessions via U40 `ProxyContact`; policy obligations. |
| RTC-L3 | Every bot (AI agent) conversation discloses that it is automated and offers human hand-off within declared limits. | Bot flow template requirement; U51 policy. |
| RTC-L4 | Routing decisions are explainable (queue, skills, priority, SLA) and fair (no routing on protected attributes). | Decision logs (U53). |
| RTC-L5 | Emergency numbers and lawful-intercept obligations are handled per jurisdiction via licensed CPaaS/telecom partners; UCOS never acts as a telecom operator. | Provider contracts + U67 controls. |

## 2. Objects
- `Queue { id, tenant, name, channels: [voice|chat|video|messaging], skillsRequired, priorityRule: DecisionRef, businessHours: CalendarRef, slaTarget: SLADefinitionRef (e.g. 80% answered in 20 s), overflow: [{after: Duration, to: queue|voicemail|callback|bot}], maxWait: Duration }`
- `AgentProfile { identity (human or AI agent), skills [{skill (ISCO/taxonomy), level}], languages (locales), channels, maxConcurrent: {chat: 3, voice: 1}, state: offline|available|busy|wrap-up|break, stateSince: TimePoint }`
- `Interaction { id, channel, direction: inbound|outbound, from/to (party refs; masked numbers), queue, assignedAgent, startedAt: TimePoint, answeredAt?: TimePoint, endedAt?: TimePoint, waitDuration: Duration, handleDuration: Duration, disposition (taxonomy), linked: {case (U39), order (U26), lead (U38), workOrder (U82)}, recording?: RecordingRef, transcript?: AssetRef, sentiment?, csat? (U97) }`
- `IvrFlow { id, nodes: [menu|collect-input|play|tts|lookup (query/command)|condition|transfer|voicemail|callback|bot], locales, businessHoursBranch: CalendarRef, version }` — compiled from a flow definition (U60-style DSL), voice-provider agnostic.
- `BotFlow { agent (U51) or scripted, intents, handoffRules: {confidence < x | user asks | sensitive intent}, disclosures }`
- `VideoSession { id, kind: consult|meeting|class|kyc|support|event, participants [{party, role: host|guest|observer}], schedule: ReservationRef (U13) or ad-hoc, roomPolicy (lobby, max participants, recording allowed), startedAt: TimePoint, endedAt?: TimePoint, recordingConsent }`
- `Callback { party, number (ContactPoint), queue, requestedAt: TimePoint, window: TemporalPolicyRef, status }`
- `Recording { interaction|session, media (U43 encrypted), consentRef, retention: RetentionRuleRef, redactions (PCI pause/resume, PII redaction in transcript) }`

## 3. Commands, Queries, Events, APIs
Commands: `DefineQueue`, `SetAgentState`, `StartInteraction` (inbound arrives via U62 webhook/SIP), `RouteInteraction`, `AcceptInteraction`, `TransferInteraction` (warm/cold), `ConferenceIn`, `HoldResume`, `EndInteraction`, `WrapUp(disposition, notes)`, `RequestCallback`, `StartRecording`/`PauseRecording` (PCI pause during card entry), `PublishIvrFlow`, `PublishBotFlow`, `CreateVideoSession`, `JoinVideoSession`, `EndVideoSession`, `Monitor`/`Whisper`/`Barge` (supervisor, audited).
Queries: `QueueStats(realtime)`, `AgentBoard`, `InteractionHistory(party)`, `EstimatedWait(queue)`.
Events: `rtc.interaction.started|answered|transferred|ended`, `rtc.queue.sla-breached`, `rtc.callback.requested|completed`, `rtc.session.started|ended`, `rtc.recording.available`.
Ports: `rtc.provider@1` (voice: dial, answer, bridge, play/TTS, gather DTMF/speech, record, transfer, masked proxy; video: create room, tokens, recording, egress; webhooks), adapters for CPaaS voice (Twilio/Exotel/Plivo class), WebRTC SFU (LiveKit/Janus class self-hosted or Agora/Twilio class hosted), SIP trunks/BYOC.
```text
POST /v1/rtc/queues   POST /v1/rtc/agents/{id}:state   POST /v1/rtc/interactions/{id}:accept|:transfer|:end|:wrap-up
POST /v1/rtc/callbacks   POST /v1/rtc/ivr-flows   POST /v1/rtc/bot-flows   POST /v1/rtc/video-sessions   POST /v1/rtc/video-sessions/{id}/tokens
GET  /v1/rtc/queues/{id}/stats (SSE stream)
```

## 4. Routing algorithm (normative outline)
On arrival: classify (IVR/bot intent, channel, language, customer tier, linked case priority) → `rtc.routing` decision gives queue + priority + required skills → select longest-idle eligible agent with skill match and capacity (or best-skill-first per queue policy) → offer with timeout (Duration) → on reject/timeout re-queue → overflow per queue policy as wait exceeds thresholds (Temporal durations) → outside business hours (CalendarRef) → after-hours branch (voicemail/callback/bot). Fairness: routing inputs exclude protected attributes (policy lint).

## 5. Gaps, AI, Security, Ops, UI
```prolog
gap(queue_without_hours, Q)        :- queue(Q), not business_hours(Q, _).
gap(recording_without_consent_flow, T) :- tenant(T), recording_enabled(T), not consent_prompt(T).
gap(bot_without_handoff, B)        :- bot_flow(B), not handoff_rule(B, _).
gap(no_rtc_adapter, T, J)          :- tenant(T), capability(T, contactcenter.core), in_scope(T, J), not adapter_for(rtc.provider, J, voice, _).
```
AI: front-line AI agents (U51) with tool access bounded to the tenant's commands; real-time agent assist (knowledge suggestions from U07/U39, next best action), live transcription and translation (U15), summarisation and auto-disposition, sentiment and QA scoring (P4); all AI outputs labelled. Security: SRTP/DTLS for media, TLS SIP, PCI DSS pause/resume (no card audio recorded), PII redaction in transcripts, supervisor actions audited. Signals: `service_level{queue}` (answered within threshold), `abandon_rate`, `asa_seconds`, `aht_seconds`, `occupancy{agent}`, `fcr_rate`, `callback_completion`, `bot_containment_rate`, `video_session_quality` (MOS, packet loss). Views: agent desktop (multi-channel inbox, softphone, customer 360 from U11/U26/U39, scripts, wrap-up), supervisor wallboard (real-time queues and SLAs), IVR/bot flow designer (U60-style canvas), video room UI (web and mobile, accessible captions), call-back scheduler. T1 (media path via provider; signalling and routing T0 during business hours).

## Appendix
- **A.** Self-hosted SFU vs hosted video provider — cost/latency spike in P3; data residency of media (recordings stored in jurisdiction cells regardless of provider).
- **C.** 0.1.0.
