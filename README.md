# AppstoreSpy API

Google Play and App Store market intelligence over a REST API: app metadata, reviews,
rankings, download and revenue estimates, developer lookup, keyword suggestions and
LiveOps events, across 13 million apps and 100 countries.

This repository holds the things that are easier to read than to describe: runnable
examples, a Postman collection, and the ruleset the contract is linted against.

| | |
|---|---|
| Base URL | `https://api.appstorespy.com/v1` |
| Contract | [openapi.json](https://api.appstorespy.com/openapi.json) (OpenAPI 3.1) |
| Reference | [/docs](https://api.appstorespy.com/docs) |
| MCP server | `https://api.appstorespy.com/mcp` |
| Changelog | [/changelog](https://api.appstorespy.com/changelog) |
| Status | [/status](https://api.appstorespy.com/status) |
| Deprecation policy | [/deprecation-policy](https://api.appstorespy.com/deprecation-policy) |
| Keys | [appstorespy.com/account](https://appstorespy.com/account) |

## Authentication

Every call carries your key in the `API-KEY` header.

```bash
curl -H 'API-KEY: YOUR_KEY' \
     'https://api.appstorespy.com/v1/play/apps/com.twitter.android?fields=name,downloads'
```

## The one thing that catches people out

`fields` exists on two surfaces and they do not accept the same names.

| Surface | `fields` shape | Accepts |
|---|---|---|
| `POST /{store}/apps/query` | array of strings | everything, including the windowed aggregates |
| `GET /{store}/apps`, `GET /{store}/apps/{id}` | comma-separated string | everything **except** the windowed aggregates |

The windowed aggregates are `downloads_month`, `downloads_lifetime`, `downloads_daily`,
`downloads_exact`, `downloads_mark`, `revenue_month` and `revenue_lifetime`. On the GET
surface the equivalents are `downloads` and `revenue`, and asking for a windowed one
returns `400 {"detail": "Wrong field - downloads_month"}`.

A few names are Google Play only on the GET surface: `installs`, `installs_exact` and
`review_count`.

## Two more pairs worth knowing

- `rating_avg` is the mean rating across all storefronts; `rating_value` is the mean in
  the country you asked for.
- `downloads_mark` is the install bracket Google Play displays (100, 500, 1000, …);
  `downloads_exact` is a reported number.

## Sorting and paging

`sort` takes a comma-separated list, with a leading `-` for descending:
`sort=-downloads_month,name`. Paging is `page` (1-based) and `limit`. List responses
carry the full result count in the `total-count` response header.

## Agents

The API is also an MCP server at `https://api.appstorespy.com/mcp`, exposing 13
read-only tools over both stores. See [examples/mcp.json](examples/mcp.json).

## What is here

- [`examples/`](examples) — a curl walkthrough, a Python quickstart, an MCP client config
- [`postman/`](postman) — a collection covering all 37 operations, generated from the live contract
- [`spectral/`](spectral) — the ruleset the contract is linted against

## Support

[appstorespy.com/support](https://appstorespy.com/support) · support@appstorespy.com
