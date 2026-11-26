# Consoles

> Generated from `_registry/business-domains.json`, the code and `docs/source/consoles.md` — edit those, then run `node scripts/domain-docs.js`.

## Overview

The frames every domain's screens sit in: the store console and the platform console — signing in, navigation, layout, the shared table, form and chart parts — and nothing of any domain's own.

**Foundation domain:** Experience · **Used by:** Store staff, Store administrator, Platform administrator

## Architecture

| Module | What it is |
|---|---|
| `lib/consoles.js` | the consoles' menus, from the database (owner Experience). |

## Data model

### `console_screens`

| Column | Type |
|---|---|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT |
| `console` | TEXT NOT NULL |
| `key` | TEXT NOT NULL |
| `section` | TEXT |
| `grp` | TEXT NOT NULL |
| `label` | TEXT NOT NULL |
| `position` | REAL NOT NULL DEFAULT 0 |
| `shows` | TEXT |
| `access` | TEXT NOT NULL |
| `fit` | TEXT |
| `edited` | INTEGER DEFAULT 0 |

## Data flow

```mermaid
flowchart LR
  U([Store staff / Store administrator / Platform administrator]) --> UI[admin.html, platform.html]
  UI --> API[0 API routes]
  API --> ENG[consoles.js]
  ENG --> DB[(console_screens)]

```

## User interface

**Pages:** `admin.html`, `platform.html`

## User flows

_Not yet written — `docs/source/consoles.md`, section `## Flows`._

## Manuals

### Store staff

_Not yet written — `docs/source/consoles.md`, section `## Manual: store_staff`._

### Store administrator

_Not yet written — `docs/source/consoles.md`, section `## Manual: store_admin`._

### Platform administrator

_Not yet written — `docs/source/consoles.md`, section `## Manual: platform_admin`._

