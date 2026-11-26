# The LUXORA API, from any language

Every route the platform serves is described in [`openapi.json`](openapi.json), an OpenAPI 3.1
description generated from the code (`node scripts/openapi.js --write`; a test fails if the two
differ). A running platform serves the same file at `/api/openapi.json`.

## Who can call what

| Routes | Caller | How it identifies itself |
|---|---|---|
| `/api/admin/…`, `/api/tenant/…` | a store's own systems (ERP, CRM, warehouse, reports) | a **store API key** as `Authorization: Bearer lxm_…` |
| `/api/platform/…` | the platform's administrators | their console session |
| everything else | shoppers and guests | none, or the shopper's session |

A store owner issues keys in **Store console → AI → API & MCP keys**. A key:

- acts as **one staff role** of that store (owner, catalog, orders, finance, support…) and can do
  exactly what that role can, in that store only;
- is shown once, stored only as a hash, and stops working the moment it is revoked;
- is recorded by name in the store's audit trail for everything it does;
- works for MCP clients (AI agents, Claude Desktop) at `/api/mcp` too.

A request with a key carries no cookie, so it needs no CSRF token.

## A client library in your language

Generate one from the description with any standard OpenAPI tool, for example
[OpenAPI Generator](https://openapi-generator.tech) (Java required):

```sh
openapi-generator-cli generate -i https://your-store.example/api/openapi.json -g python     -o luxora-python
openapi-generator-cli generate -i https://your-store.example/api/openapi.json -g java       -o luxora-java
openapi-generator-cli generate -i https://your-store.example/api/openapi.json -g typescript-fetch -o luxora-ts
openapi-generator-cli generate -i https://your-store.example/api/openapi.json -g csharp     -o luxora-dotnet
openapi-generator-cli generate -i https://your-store.example/api/openapi.json -g go         -o luxora-go
```

To check the description with a validator first: `npx @redocly/cli lint docs/api/openapi.json`.

## Without a library

Any HTTP client works. Python, with nothing installed:

```python
import json, urllib.request
KEY = "lxm_…"  # Store console → AI → API & MCP keys
req = urllib.request.Request("https://your-store.example/api/admin/orders",
                             headers={"Authorization": "Bearer " + KEY})
orders = json.load(urllib.request.urlopen(req))
```

JavaScript:

```js
const r = await fetch("https://your-store.example/api/admin/orders", { headers: { Authorization: "Bearer lxm_…" } });
const orders = await r.json();
```

## What the description does not say yet

- Request and response bodies are described as JSON objects, without their fields.
- Many routes have no written description yet; for those the summary is the handler's name.

Both are filled in as each domain's documentation is written.
