#!/usr/bin/env bash
# A walk through the API with curl. Set your key first:
#   export API_KEY=...            # from https://appstorespy.com/account
set -euo pipefail

: "${API_KEY:?set API_KEY first, from https://appstorespy.com/account}"
BASE=https://api.appstorespy.com/v1
auth=(-H "API-KEY: ${API_KEY}" -H 'accept: application/json')

echo '# One app, a few fields'
curl -s "${auth[@]}" "${BASE}/play/apps/com.twitter.android?fields=name,developer_name,downloads,rating_avg"
echo

echo '# Size a segment before you page through it: one call instead of many'
curl -s "${auth[@]}" -H 'content-type: application/json' \
  -X POST "${BASE}/play/apps/summary" \
  -d '{"filter": {"category": "SOCIAL"}}'
echo

echo '# The top of that segment by monthly revenue'
curl -s "${auth[@]}" -H 'content-type: application/json' \
  -X POST "${BASE}/play/apps/query" \
  -d '{"filter": {"category": "SOCIAL", "downloads_month": {"gte": 1000}},
       "fields": ["name", "downloads_month", "revenue_month"],
       "sort": "-revenue_month", "limit": 5}'
echo

echo '# Who is competing for one app'"'"'s audience (apps that list it as similar)'
curl -s "${auth[@]}" -H 'content-type: application/json' \
  -X POST "${BASE}/play/apps/similar" \
  -d '{"id": "com.twitter.android", "link": "from", "filter": {}, "limit": 5}'
echo

echo '# The exact Indonesian listing, crawled on demand (202 while the crawl runs: repeat the call)'
curl -s "${auth[@]}" "${BASE}/play/apps/com.twitter.android/listing?country=ID&language=id"
echo

echo '# Today'"'"'s US top free chart, and the total in a response header'
curl -s -D- -o /dev/null "${auth[@]}" \
  "${BASE}/play/rankings?country=US&collection=topselling_free&limit=5" | grep -i total-count
