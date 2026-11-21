# UCOS Ω∞ — Temporal Binding Matrix

| Field | Value |
|---|---|
| Document ID | `UCOS-TEMPORAL-MATRIX` |
| Version | 1.0.0 |
| Authority | Normative companion to U13 Temporal (TMP-L1…L7, Appendix E) and master §9 |
| Purpose | For **every universe (U01–U109)**: which time needs it has (calendar, scheduling, appointments, triggers, ranges, expiry, SLAs, reminders, waitlists, sync) and **which Temporal mechanism** must be used. No universe may implement these any other way. |

## Legend

**Mechanisms**

| Code | Mechanism (U13) |
|---|---|
| `TP` | TimePoint (instant) |
| `TR` | TimeRange (validity, period, term, range) |
| `D` / `BD` | Duration / BusinessDuration (business time on a named calendar) |
| `R` | Recurrence or Schedule (backed by recurrence Triggers) |
| `POL` | TemporalPolicy: a reusable window, e.g. opening hours, campaign windows, quiet hours, freezes |
| `CAL` | Calendar: holiday, business-hours, fiscal, settlement, trading-session or resource calendar |
| `AV` | AvailabilityWindow, Slot or Reservation (appointments, bookings, delivery slots, rentals, seats) |
| `FCA` | FindCommonAvailability (multi-party or multi-resource scheduling) |
| `SLA` | SLADefinition or SLAClock |
| `TRG` | Trigger (at, relative, inactivity, deadline, condition, geo-temporal, hybrid) |
| `REM` | Reminder (a relative Trigger plus a Communication template) |
| `WL` | Waitlist or QueueToken |
| `FEED` | CalendarFeed (ICS), ExternalCalendarLink (Google, Microsoft, CalDAV), Invitation |
| `ASOF` | asOf / time-travel evaluation, bitemporal history |
| `TS` | Frame time scale or calendar system (U77, for non-Earth, virtual or simulation clocks) |

**Dependency kind** (U13 Appendix E.4)

| Code | Meaning |
|---|---|
| **V** | Value types only. Kernel SDK library, no service dependency, safe for layers below U13. |
| **E** | Pure evaluation through the SDK (policy and calendar evaluation, business-time math). Library, no cycle. |
| **S** | Uses Temporal services (triggers, reservations, SLA clocks, feeds, waitlists). Must list `U13 Temporal` in *Depends on*. |

Rows marked ⬜ are planned universes. Their specs MUST implement the bindings listed here.

---

## 1. Constitution, meta, knowledge (L0–L3)
| Universe | Time needs | Mechanisms | Kind |
|---|---|---|---|
| U01 Authority | authority validity; approval timeouts; emergency decisions confirmed within 24 h; renewal reminders | TR, D, TRG(deadline), REM | S |
| U02 Governance | change windows and freezes; approval timeouts; waiver validity and expiry; release-wave holds; change calendar | POL, D, TRG, TR, CAL(view) | S |
| U03 Policy | time-bound access ("only during business hours", "until …"); bundle staleness; asOf reads | E-eval of POL/TR in conditions, D, ASOF | S |
| U04 Meta | bitemporal envelope (valid / transaction time); definition sunset | TP, TR, ASOF | V |
| U05 Ontology | concept validity | TR | V |
| U06 Taxonomy | node validity; seasonal nodes | TR | V |
| U07 Knowledge Graph | assertion validity; trust decay; scheduled rebuilds | TR, D, R | S |
| U08 Reference Data | code validity; deprecation; release checks (scheduled by U73 ops triggers) | TR, TP | V |
| U77 Existence & Reality Frame | defines time scales and calendar systems (source of truth for TS) | TS (owner) | V |

## 2. Foundation (L4)
| Universe | Time needs | Mechanisms | Kind |
|---|---|---|---|
| U09 Identity | credential and token expiry; idle and absolute session timeouts; lockout cool-down; delegation validity; just-in-time elevation expiry; quarterly access reviews; key rotation | TP, D, TR, TRG, R | S |
| U10 Org & Tenant | store opening hours; workspace expiry; tier-migration cutover window; offboarding notice; link validity; org fiscal calendar | POL, TP+TRG, D, TR, CAL(fiscal) | S |
| U11 Person & Party | birth date (age and minor computation); role and relationship validity; consent timestamps | LocalDate, TR, TP, E | E |
| U12 Geography | place, jurisdiction and boundary validity; timezone of place; service-area hours (evaluated); geofence dwell; location retention | TR, E(POL), D | E |
| U13 Temporal | owner | — | — |
| U14 Currency & Unit | FX rate validity; rate refresh schedules; staleness; daily-close timing on calendars | TR, R, D, CAL | S |
| U15 Localization | calendar-system display; translation turnaround | E, D | E |
| U16 Context | `now`, `asOf`; envelope expiry; re-resolve at timer steps | TP, ASOF, D | E |
| U17 Resource ⬜ | resource calendars; shifts; time off; capacity per slot | CAL, AV, TimeOff, R | S |

## 3. Products, services, catalogue, commerce
| Universe | Time needs | Mechanisms | Kind |
|---|---|---|---|
| U18 Product Intelligence | lifecycle facts (announced, launched, end-of-sale, end-of-support); recall dates; fact freshness; end-of-life triggers to Catalog | TP, TR, D, TRG | S |
| U19 Service Intelligence | typical duration; SLA templates; scheduling mode; credential renewal; cancellation-notice norms | D, SLA, AV, D | S |
| U20 Industry | template validity; benchmark periods | TR | V |
| U21 Catalog | listing availability (e.g. breakfast menu); seasonal collections; scheduled publish; experience slots | POL, TRG, AV | S |
| U22 Offer | every offer, coupon and campaign window; flash sales; countdowns (nextChange); budget pacing windows | POL (TMP-001 pattern), TRG, D | S |
| U23 Pricing | price validity; scheduled price changes; quote expiry; 30-day lowest-price history; B2B quote validity | TR/POL, TRG, TP, ASOF | S |
| U24 Cart & Checkout | cart lifetime; abandonment (inactivity); checkout hold expiry; delivery-slot selection | D, TRG(inactivity), TP+TRG, AV | S |
| U25 Marketplace ⬜ | seller onboarding windows; settlement periods (T+N); payout schedules; commission periods; dispatch SLAs | POL, CAL(settlement), R, TR, SLA | S |
| U26 Order | placed-at; cancellation windows; return windows; completion after the return window; timeline | TP, D, TRG, Timeline | S |
| U27 Subscription ⬜ | trials; billing cycles; renewals; grace; dunning schedules; proration; usage periods | TR, R, TRG, D, BD | S |
| U28 Entitlement ⬜ | entitlement validity; quota resets | TR, R | S |
| U29 Payment | intent and authorisation expiry; capture deadlines; reconciliation on settlement calendars; mandate validity; dispute deadlines; payout schedules | TP+TRG, CAL, R, TR, SLA | S |
| U30 Ledger ⬜ | fiscal periods; period close; accruals (day-count); revenue schedules; ageing buckets; settlement T+N | CAL(fiscal), R, D, BD | S |
| U31 Tax | rate validity; filing calendars; invoice cancellation windows; e-invoice deadlines; fiscal-year numbering series | TR, CAL, D, TRG | S |
| U32 Loyalty ⬜ | points expiry; tier qualification periods; earn windows | TP+TRG, TR, POL | S |
| U33 Advertising ⬜ | flight dates; dayparting; budget pacing | POL, D | S |
| U78 Product Configuration | seasonal options; lead-time computation | POL, D | S |
| U79 Installed Base | lifecycle dates; maintenance intervals by time or meter; custody timestamps | TP, R, TRG(condition), D | S |
| U80 Warranty & After-sales | coverage anchored to delivery or registration; expiry reminders; claim turnaround SLA; maintenance-contract visits | TR, REM, SLA, R | S |
| U81 Ticketing & Events | session start and end; on-sale and off-sale; seat-hold expiry; virtual waiting room; waitlist; reminders; ICS calendar invites | TR, POL, D+TRG, WL, REM, FEED | S |
| U82 Field Service | appointment windows; multi-party scheduling; technician calendars and time off; SLAs; "on my way" reminders; time logs; invites | AV, FCA, CAL, TimeOff, SLA, REM, TR, FEED | S |
| U83 Rental & Leasing | rental periods; late-return deadlines; extensions; buffers between rentals; deposit pre-authorisation expiry; waitlist; lease schedules | AV, TRG, D, WL, R | S |
| U84 Stored Value | instrument expiry (statutory minimum); breakage schedules; activation windows | POL, R, TRG | S |
| U91 Auction & Negotiation | auction windows; soft-close extensions; tender deadlines; mandate expiry; server-time ordering | POL, D, TRG, TR, TP | S |
| U100 Financial Products | repayment schedules (day-count); interest accrual; days-past-due buckets; policy terms; premium schedules; market sessions; T+N settlement | R, D, BD, TR, CAL(trading, settlement) | S |

## 4. Operations
| Universe | Time needs | Mechanisms | Kind |
|---|---|---|---|
| U34 Inventory | reservation TTL; lot expiry and "expiring soon"; low-stock condition; cycle-count schedules; inbound ETAs; allocation windows | D+TRG, TP+TRG, TRG(condition), R, POL | S |
| U35 Fulfillment | cut-offs on node calendars; processing time; transit time; delivery slots; pickup-hold expiry; dispatch SLA; re-attempt scheduling; delivery promise | CAL, BD, D, AV, TRG, SLA, TR | S |
| U36 Logistics ⬜ | carrier pickup schedules; transit matrices; route schedules; driver shifts; carrier calendars | R, D, AV, CAL | S |
| U37 Mobility ⬜ | surge windows; driver shifts; ETAs; trip timestamps | POL, AV, D, TP | S |
| U45 Procurement ⬜ | RFQ deadlines; promised delivery dates; payment terms (net-30 on a business calendar); supplier lead times | TRG, TP, BD, D | S |
| U46 Workforce ⬜ | shifts; attendance; leave (time off); payroll cycles; overtime; holiday calendars | AV, TP, TimeOff, R, D, CAL | S |
| U47 Manufacturing ⬜ | production schedules; work-centre calendars; cycle times; planning buckets | AV, CAL, D, R | S |
| U90 Global Trade | landed-cost quote validity; classification validity; declaration deadlines; sanctions-list refresh | TP, TR, TRG, R | S |
| U92 IoT & Devices | telemetry time; firmware rollout holds; firmware-update maintenance windows; command expiry; heartbeats | TP, D, POL, TRG | S |

## 5. Customer, growth, content
| Universe | Time needs | Mechanisms | Kind |
|---|---|---|---|
| U38 CRM ⬜ | follow-ups; scheduled activities; stage ageing; meetings (multi-party scheduling, invites, Google/Outlook sync) | REM, AV, D, FCA, FEED | S |
| U39 Support ⬜ | response and resolution SLAs on business hours; escalations; snooze; auto-close | SLA, CAL, TRG, TP, D | S |
| U40 Communication | quiet hours; scheduled sends; fallback windows; frequency-cap windows; OTP expiry; proxy-number validity; reminder delivery | POL, TRG, D, POL | S |
| U41 Content & Media ⬜ | publish and unpublish schedules; rights windows per territory; live schedules; embargo | TRG, POL, TR | S |
| U42 Document ⬜ | document validity; signing deadlines | TR, TRG | S |
| U43 Asset | rights validity and expiry; signed-URL TTL | TR+TRG, D | S |
| U44 Search | time-boxed result pins and boosts; query-rule validity; index freshness; reindex schedules | POL, TR, D, R | S |
| U52 Recommendation ⬜ | time-decay; seasonal strategies | D, POL | S |
| U70 Trust & Reputation ⬜ | review prompt after delivery; rating decay | TRG(relative), D | S |
| U85 CDP | trait refresh; segment windows ("last 90 days"); real-time entry and exit | R, D, TRG | S |
| U86 Marketing Automation | campaign schedules; journey waits (duration or until event); send time inside quiet hours; holdout periods | POL, D, TRG, TR | S |
| U87 Web Presence & SEO | sitemap regeneration; lastmod; temporary-redirect expiry; embargoed publish | R, TP, TRG | S |
| U88 Social & Community | scheduled posts; expiring stories; moderation and takedown SLAs (legal timelines); live sessions | TRG, D, SLA, TR | S |
| U89 Contract & Agreement | contract term; renewal notice period; obligations due; signing deadlines | TR, D+TRG, TRG | S |
| U96 Work & Collaboration | task due dates; sprints; milestones; reminders; meetings (multi-party scheduling, invites, sync); timesheets | TP, TR, REM, FCA, FEED | S |
| U97 Forms & Surveys | open and close windows; distribution schedules; "survey 3 days after delivery" | POL, R, TRG(relative) | S |

## 6. Intelligence
| Universe | Time needs | Mechanisms | Kind |
|---|---|---|---|
| U49 AI/Model ⬜ | model and price validity; evaluation cadence | TR, R | S |
| U50 Prompt ⬜ | version validity | TR | V |
| U51 Agent ⬜ | authority validity; daily budgets; scheduled autonomous runs; memory retention | TR, D, R | S |
| U53 Decision | tenant-version validity; scheduled activation; asOf evaluation | POL/TR, TRG, ASOF | S |
| U54 Simulation ⬜ | simulation clock; scenario ranges | TS, TR | S |
| U55 Digital Twin ⬜ | snapshots; history replay | TP, ASOF | S |
| U56 Learning ⬜ | learning windows | D | E |
| U94 ML Platform | training schedules; point-in-time correct features; feature freshness; drift-triggered retraining | R, ASOF, D, TRG(condition) | S |

## 7. Platform, trust, operations
| Universe | Time needs | Mechanisms | Kind |
|---|---|---|---|
| U57 Capability | deprecation sunsets; revocation SLA; re-certification cadence | TP+TRG, SLA, R | S |
| U58 Composition | hourly registry snapshots; recompose ageing | R, D | S |
| U59 Generation ⬜ | scheduled generation | R | S |
| U60 Workflow | timers; human-task SLAs; escalations on business time; waits | TRG, SLA, BD | S |
| U61 Event | event time; retention; replay ranges; dead-letter queue ageing; schema sunsets | TP, D, TR, TRG | S |
| U62 Integration ⬜ | sync schedules; polling intervals; reconciliation schedules; external calendar connectors (Google, Microsoft, CalDAV) | R, D, FEED adapters | S |
| U63 API | deprecation and sunset; rate-limit windows; token lifetimes; quota periods | TP+TRG, D, R | S |
| U64 UI/App/Channel | calendar, slot-picker, timeline, countdown and date-range components; journey timeouts; "preview as of" | component bindings to AV/POL/Timeline, D, ASOF | S |
| U65 Security | key rotation; finding remediation deadlines; session limits; breach-notification clocks; threat-model review cadence; certificate expiry | R, TRG, D, SLA | S |
| U66 Privacy & Consent | data-subject request deadlines; retention (duration from an anchor event); consent validity; notice effective dates; nightly retention engine | SLA, D, TR, TP, R | S |
| U67 Compliance | regulation effective dates and "effective soon"; control-test schedules; evidence freshness; assessment periods | TP+TRG, R, D, TR | S |
| U68 Audit & Evidence | daily chain anchoring; retention; legal-hold periods; evidence freshness; auditor access validity | R, D, TR | S |
| U69 Risk ⬜ | velocity windows; score decay | D | S |
| U71 Dispute ⬜ | chargeback and appeal response deadlines | SLA, TRG | S |
| U72 Observability & Analytics | rolling SLO windows; alert `for` durations; maintenance windows (alert suppression); report schedules; flag expiry; experiment start and stop | D, POL, R, TP, TRG | S |
| U73 Infrastructure | backups; restore tests; disaster-recovery drills; cutover windows; rollout holds; certificate expiry | R, POL, D, TRG | S |
| U74 Certification | validity; re-certification; invalidation grace | TP, TRG, D | S |
| U75 Discovery & Gap | gap due dates; scan schedules | TP+TRG, R | S |
| U76 Evolution ⬜ | deprecation timelines; migration windows | TR, POL | S |
| U93 Data Governance | freshness SLOs; quality-check schedules; share-agreement expiry | D, R, TR | S |
| U95 Software Delivery (Git) | release trains; dev-environment TTL; pipeline timeouts; merge freezes (from U02) | R, D, POL | S |
| U98 Sustainability & ESG | reporting periods; emission-factor validity; packaging-responsibility (EPR) filing deadlines | TR, TRG | S |
| U99 Digital Assets | chain time; finality; custody-approval timeouts | TS, D | S |

## 7a. Completeness universes U101–U108
| Universe | Time needs | Mechanisms | Kind |
|---|---|---|---|
| U101 QHSE | inspection and audit schedules; CAPA and effectiveness due dates; controlled-document review cycles; permit-to-work validity; regulatory incident notification clocks; environmental monitoring schedules | R, TP+TRG, TR, SLA | S |
| U102 Strategy & Performance | planning cycles; objective and key-result periods; check-in reminders | R, TR, REM | S |
| U103 Corporate Governance & Equity | board calendars; statutory filing deadlines; vesting schedules; dividend record and payment dates; cap table as-of | AV/FCA (meetings), FEED, TRG, R, TP, ASOF | S |
| U104 Legal, Ethics & IP | hearings and court dates; limitation periods; IP renewal deadlines; legal-hold periods; investigation SLAs | TP+TRG, TR, SLA, FEED | S |
| U105 Workplace & Facilities | desk, room and parking booking; check-in and no-show release; visitor arrivals; building calendars | AV, TRG, FCA, FEED, CAL | S |
| U106 Travel & Expense | trip ranges; claim submission deadlines; per-diem days; card statement cycles | TR, TRG, D, R | S |
| U107 Partner, Channel & Franchise | program periods; deal-registration expiry; rebate periods; royalty and fee cycles | TR, TP+TRG, R | S |
| U108 Product Development & R&D | stage-gate milestones; engineering-change effectivity; launch dates; experiment timelines | TP, TemporalRef, TRG, TR | S |
| U109 Real-time Comms & Contact Centre | queue business hours; service-level SLAs; offer timeouts; overflow durations; call-backs in windows; video sessions booked as reservations; agent states and shifts; recording retention | CAL, SLA, D, TRG, POL, AV, TP, R | S |

## 8. Industry packs (U48 family)
| Pack | Calendar and scheduling needs | Mechanisms |
|---|---|---|
| Healthcare | practitioner calendars, appointments, tele-consult slots, no-show and waitlist, reminders, ICS invites, clinic queue tokens, prescription validity | AV, FCA, WL, REM, FEED, TR |
| Education | academic calendars, terms, timetables, exam windows, assignment deadlines, attendance | CAL(academic), R, POL, TRG, TP |
| Hospitality and stays | nightly inventory, check-in and check-out times, minimum stay, seasonal rate plans, blackout dates | AV(night granularity), D, POL |
| Travel | departure schedules, seat inventory per departure, connections, fare validity, check-in windows | R, AV/U81 seats, D, POL |
| Food delivery and restaurants | menu hours, prep times, delivery slots, kitchen capacity | POL, D, AV |
| Government | office hours, appointment booking, processing SLAs, permit validity, filing deadlines | POL, AV, SLA, TR, TRG |
| Utilities and telecom | billing cycles, meter-read schedules, outage windows, installation appointments | R, POL, AV |
| Brokerage | trading sessions, holidays per exchange, settlement T+N, corporate-action dates | CAL(trading), BD, TP |
| Space, metaverse and simulation | sols, world clocks, light-time SLA pauses | TS, D |

---

## 9. Guarantees
1. Every universe has an explicit binding row above. No time need is left to free-form fields.
2. Every universe of kind **S** lists `U13 Temporal` in its *Depends on* (fixed in all specs by amendment A-46). Gate `ARCH-TMP-05` checks this.
3. Field naming follows U13 Appendix E.3, so `expiresAt`, `validUntil`, `period`, `schedule` and similar names always mean the canonical Temporal types.
4. Gap rules (U13 §8, plus):
```prolog
gap(time_need_unbound, U, N)   :- universe(U), time_need(U, N), not binding(U, N, _).
gap(service_use_undeclared, U) :- uses_temporal_service(U), not depends_on(U, u13).
gap(private_scheduler, P)      :- pack(P), uses_library(P, cron_or_rrule_or_scheduler).
```
