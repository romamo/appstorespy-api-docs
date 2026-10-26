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
| Keys | [appstorespy.com/profile/api](https://appstorespy.com/profile/api) |

## Authentication

Every call carries your key in the `API-KEY` header. The MCP server takes the same key, in `API-KEY` or as `Authorization: Bearer <key>`.

```bash
curl -H 'API-KEY: YOUR_KEY' \
     'https://api.appstorespy.com/v1/play/apps/com.twitter.android?fields=name,downloads'
```

### Your keys

Create, rename and revoke keys at [appstorespy.com/profile/api](https://appstorespy.com/profile/api).

- A key looks like `asp_live_` followed by 36 letters and digits. The page lists keys by that prefix and the first 8 characters after it; the full key is shown once, when you create it, so copy it then
- Older keys are 40 lowercase hex characters. The ones listed on the page as "Default key" keep working; an older key that is not listed there will stop working, so create a new key in its place
- You can hold up to 10 active keys, one per integration, so a key can be revoked without touching the others
- A key never expires unless you pick an expiry when creating it (30 days, 90 days or 1 year); an expiry cannot be extended later
- Revoking takes effect on the next call and cannot be undone
- The page shows when each key was last used, to the minute

### Rotating a key without downtime

1. Create a new key
2. Deploy it to your integration
3. Revoke the old key once the new one shows a recent "last used"

### When a key is refused

| Answer | Meaning |
|---|---|
| `401 Malformed API key.` | The value is not a well-formed key: usually a copy-paste error, a missing or extra character |
| `401 Wrong key` | No active key matches: unknown, revoked or expired |
| `401 Not authenticated` | The `API-KEY` header is missing |
| `402` | The credit balance does not cover the call, or the paid subscription is not active: the body says which |
| `403` | The endpoint is not in your plan; the body names the plan it needs |

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

## Daily installs and the website chart

`GET /play/apps/{id}/installs_daily` returns `ipd`, a per-day figure derived from the
cumulative install total: each increase is spread evenly over the days since the total
last changed, so a collection gap becomes a plateau rather than a one-day spike.

Those are raw values. The Daily Installs chart on the website smooths them for
readability, so a given day will not match. Pass `smooth=true` to get the chart's series
instead: a centered, triangular-weighted 9-day moving average, weights 1,2,3,4,5,4,3,2,1,
renormalised over the days that have data. The API pads the window with days either side
of `start`/`end`, while the chart smooths only the 30 days it draws, so the first and last
days of a range can still differ slightly.

`start` defaults to the 30 days ending at `end`, and `end` defaults to the newest data.

## Listings in any language

`GET /{store}/apps/{id}` serves the languages AppstoreSpy stores. For the exact store
listing in any other language, `GET /play/apps/{id}/listing?country=ID&language=id`
crawls Google Play on demand and returns the listing as Google Play serves it: title,
short and full description, what's new, icon, feature graphic, trailer and screenshots
in Google's order. `language` takes any Google Play Console locale (`id`, `th`, `hi_IN`,
`ur`, `fa`, `ms`, `pt_PT`, `es_ES`, `uk`, …).

`translated` is `true` when Google Play is showing a machine translation because the
developer has not supplied that language; `translated_from` then names the source
language the way Google Play spells it in the requested language.

The listing is kept once crawled. `freshness` (`1d`, `7d`, `30d`, default `1d`) says how
old a kept listing may be before it is crawled again. A call waits for a running crawl for
up to about 30 seconds, then answers `202` with the crawl state; repeat the same request to
get the listing. `wait=false` returns the `202` at once. A call that queues a crawl costs
the crawl price; a call served from a kept listing costs the read price; a `202` for a crawl
someone else queued costs nothing. The `X-Cost` response header carries what was charged.

## Sorting and paging

`sort` takes a comma-separated list, with a leading `-` for descending:
`sort=-downloads_month,name`. Paging is `page` (1-based) and `limit`. List responses
carry the full result count in the `total-count` response header.

## Agents

The API is also an MCP server at `https://api.appstorespy.com/mcp`, exposing
read-only tools over both stores (listed by `tools/list`). Tool calls take the same
API key and cost the same credits as the endpoint each one wraps. See
[examples/mcp.json](examples/mcp.json).

- [MCP server](https://api.appstorespy.com/mcp): Streamable HTTP endpoint
- [Agentic access](https://api.appstorespy.com/agentic-access): what each operation costs and whether it reads, queues or writes
- [Agent skills](https://api.appstorespy.com/skills/): one SKILL.md per capability
- [llms.txt](https://api.appstorespy.com/llms.txt): an index of every agent document

## What is here

- [`examples/`](examples) — a curl walkthrough, a Python quickstart, an MCP client config
- [`postman/`](postman) — a collection covering all 38 operations, generated from the live contract
- [`spectral/`](spectral) — the ruleset the contract is linted against
- [`tools/`](tools) — regenerates the collection from the live contract: `python tools/generate_postman.py`

## Support

[appstorespy.com/support](https://appstorespy.com/support) · support@appstorespy.com
