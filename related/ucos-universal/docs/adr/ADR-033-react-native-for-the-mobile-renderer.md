# ADR-033: React Native for the mobile renderer

| Field | Value |
|---|---|
| Status | Accepted |
| Deciders | Architecture Board (U01 root authority) |
| References | U64 UI; open decision U64 |

## Context
Generated white-label mobile apps need a cross-platform renderer for the UI meta-model.

## Decision
Use **React Native (Expo)**, sharing the TypeScript UI meta-model renderer and design tokens with the web renderer. Flutter is considered only if POS or kiosk performance tests fail on target hardware.

## Alternatives considered
- Flutter: excellent rendering performance, but a second renderer implementation in Dart.

## Consequences
**Positive**
- One renderer language across web and mobile.

**Negative / costs**
- Native modules are needed for some device features (printers, scanners).

## Enforcement
Renderer conformance suite; `A11Y-AUTO-01` on mobile builds.
