# TM-COMM — Communication (P1) and real-time / contact centre (P3 addendum)

| Field | Value |
|---|---|
| Scope | P1: U40 templates, notification rules, sending (email, SMS with TRAI DLT, WhatsApp, web push), OTP delivery, inbound intake, in-app notifications. P3: real-time chat, voice/IVR, video sessions, contact centre (U109) |
| Data classes | PII; recordings may contain BIOMETRIC data and payment data (P3) |
| Owner | `ucos:org:engagement-comm` |
| References | U40, U109; TRAI TCCCPR 2018; WhatsApp Business policy; CAN-SPAM, GDPR/ePrivacy |

## STRIDE (P1)
| ID | Threat | L | I | Mitigations | Verification |
|---|---|---|---|---|---|
| CM-S1 | Email spoofing of the tenant's domain | 2 | 3 | SPF, DKIM and DMARC (p=quarantine or stricter) are required before sending; BIMI optional | Domain onboarding check |
| CM-T1 | Template injection (user data rendered as markup or script) | 2 | 3 | Logic-less templates; contextual escaping per channel; tenant templates reviewed; no remote content in transactional mail | Template tests |
| CM-I1 | Messages sent to the wrong recipient (stale contact point) | 2 | 2 | Only verified contact points; bounce and number-reassignment handling (reassigned-number checks where available) | Delivery stats |
| CM-I2 | Message content kept longer than needed | 2 | 2 | Retention rules per purpose; restricted content (OTPs) redacted after send | Retention job |
| CM-D1 | SMS pumping / toll fraud through the OTP endpoint | 3 | 3 | Per-country caps, CAPTCHA after threshold, anomaly alerts on spend, allow-list of countries per tenant | Spend alerts |
| CM-E1 | Marketing sent without consent | 2 | 3 | Send-time consent check by purpose and channel (COMM-L1); DLT template and header IDs in India; quiet hours | Policy tests; `CMP-MAP-01` |
| CM-S2 | Inbound spoofing (fake replies impersonating customers) | 2 | 2 | Inbound is linked to a party only through a verified contact point; sensitive actions from inbound require authentication | Inbound tests |

## Addendum (P3: real-time, voice, video, contact centre)
| ID | Threat | L | I | Mitigations |
|---|---|---|---|---|
| RT-I1 | Call recordings capture card numbers | 2 | 3 | Pause recording during payment (DTMF masking) or use a hosted IVR payment flow (`ucos.ctrl.pci-hosted-fields`) |
| RT-I2 | Recording without consent | 2 | 3 | Consent announcement and recording consent control (`ucos.ctrl.recording-consent`); per-jurisdiction rules |
| RT-S1 | Bot impersonates a human | 2 | 2 | Bot disclosure control (`ucos.ctrl.bot-disclosure`) and a "talk to a human" option at all times |
| RT-D1 | Toll fraud on outbound calling | 2 | 3 | Destination allow-lists, spend caps, anomaly detection |
| RT-T1 | Video-room hijack | 2 | 3 | Short-lived participant tokens bound to identity and room, lobby, host controls |
| RT-I3 | Masked-number leakage after the trip or order ends | 2 | 2 | Proxy-number bindings expire with the transaction |
