# U92 — IoT & Devices Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U92-iot` |
| Layer | L5 Business Capability / L9 Integration |
| Domain | 05 Operations |
| Steward | `ucos:org:iot-edge` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P5 (POS/kiosk/scanner/printer device management, warehouse sensors, telematics), P6 (industrial IoT, robots, edge AI, smart products with digital twins) |
| Depends on | U09 Identity (device identities, X.509/attestation), U79 Installed Base (device ↔ unit), U73 Infra (edge cells), U61 Event (telemetry streams), U13 Temporal (schedules, condition triggers), U12 Geography / U77 Frame (location; non-Earth/vehicle frames), U55 Twin, U65 Security |
| Depended on by | U35 Fulfillment (scanners, label printers), U64 POS/kiosk channels, U36 Logistics/U37 Mobility (telematics), U82 Field Service (condition-based work orders), U98 ESG (meters), robotics/autonomous packs |
| Master references | Master "IoT, Edge, Robotics" universes (A-43) |

> IoT owns **connected physical devices and their data/command channels**: device types and models, provisioning and identity (certificates, attestation), fleet management (groups, configuration, firmware/OTA updates), telemetry ingestion and normalisation, commands and responses (with safety interlocks), device shadows/state, edge deployments (local processing, offline store-and-forward), and protocol adapters (MQTT, CoAP, OPC UA, Modbus, BLE, LoRaWAN, CAN/OBD, ROS 2 bridge).

## 1. Laws
| ID | Law | Enforcement |
|---|---|---|
| IOT-L1 | Every device has a unique cryptographic identity; no shared credentials; attestation where hardware supports it. | Provisioning service; Identity kind=device. |
| IOT-L2 | Commands with physical effects (unlock, actuate, move) require authorisation, safety interlocks, and idempotent acknowledgements; safety-critical commands need confirmation/dual control per decision. | Command policy + `iot.safety-class` decision. |
| IOT-L3 | Firmware updates are signed, staged (canary cohorts), and reversible. | OTA pipeline + U02 release plans. |
| IOT-L4 | Telemetry is classified; personal/location telemetry follows purpose and retention (U66). | Stream classification. |

## 2. Objects
`DeviceType { id, model (GPID), capabilities (telemetry schemas, commands), protocols, safetyClass, firmware lineage }` · `Device { id, type, identity (cert), unit (U79)?, owner, location/frame, group(s), shadow {reported, desired}, status: provisioned|online|offline|quarantined|retired }` · `TelemetrySchema { metrics, units (U14), sampling }` · `Command { device|group, name, args, safetyClass, issuedBy, status: queued|sent|acked|executed|failed|expired }` · `FirmwareRelease { type, version, artifact (signed), rollout plan }` · `EdgeNode { site, hardware, workloads (packs subset), sync policy }`.

## 3. Commands, Queries, Events, APIs
Commands: `ProvisionDevice`, `AssignGroup`, `SetDesiredState`, `SendCommand`, `RolloutFirmware`, `QuarantineDevice`, `RetireDevice`, `DeployToEdge`.
Events: `iot.device.online|offline`, `iot.telemetry.*` (signal category topics), `iot.command.acked|failed`, `iot.firmware.updated`, `iot.alarm.raised`.
Ports: `iot.broker` (EMQX/HiveMQ/AWS IoT/Azure IoT), protocol adapters, `robot.bridge` (ROS 2).
```text
POST /v1/iot/devices:provision   PATCH /v1/iot/devices/{id}/shadow   POST /v1/iot/commands   POST /v1/iot/firmware/rollouts
```

## 4. Gaps, AI, Ops, UI, Scale
```prolog
gap(device_without_identity, D) :- device(D), not device_certificate(D).
gap(unsigned_firmware, F)       :- firmware_release(F), not signed(F).
gap(safety_command_without_interlock, C) :- command_type(C), safety_class(C, high), not interlock(C).
```
AI: anomaly detection & predictive maintenance on telemetry (U94), edge inference, robotics task planning (agents with physical authority strictly bounded, L17). Signals: `devices_online_ratio`, `telemetry_ingest_rate`, `command_ack_latency_ms`, `ota_success_ratio`. Views: device fleet console (map, groups, health), device detail (shadow, telemetry charts, commands with safety prompts), OTA rollout board, edge node manager. Scale: 10⁷–10⁸ devices; MQTT clusters per region; telemetry in time-series stores; T1 (safety commands T0).

## Appendix
- **C.** 0.1.0.
