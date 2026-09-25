"""AppstoreSpy API quickstart.

    pip install httpx
    export API_KEY=...       # https://appstorespy.com/account
    python quickstart.py
"""

import os

import httpx

BASE = "https://api.appstorespy.com/v1"
KEY = os.environ["API_KEY"]

client = httpx.Client(base_url=BASE, headers={"API-KEY": KEY}, timeout=60)


def one_app(store: str, app_id: str) -> dict:
    """Fetch a single listing.

    `fields` here is a comma-separated string, and this surface does not accept the
    windowed aggregates: ask for `downloads`, not `downloads_month`.
    """
    r = client.get(f"/{store}/apps/{app_id}", params={"fields": "name,developer_name,downloads,rating_avg"})
    r.raise_for_status()
    return r.json()


def size_segment(store: str, app_filter: dict) -> dict:
    """Totals for everything matching a filter, in one call.

    Worth doing before paging through `query`, which costs a call per page.
    """
    r = client.post(f"/{store}/apps/summary", json={"filter": app_filter})
    r.raise_for_status()
    return r.json()


def top_by_revenue(store: str, app_filter: dict, limit: int = 5) -> list:
    """The filter surface: `fields` is a list, and the windowed aggregates are valid."""
    r = client.post(
        f"/{store}/apps/query",
        json={
            "filter": app_filter,
            "fields": ["name", "downloads_month", "revenue_month"],
            "sort": "-revenue_month",
            "limit": limit,
        },
    )
    r.raise_for_status()
    return r.json()["data"]


def listing(app_id: str, country: str, language: str, attempts: int = 6) -> dict:
    """The store listing in any Google Play Console locale, crawled on demand.

    A 202 means the crawl is still running; the same request answers 200 once it is
    done. Each call waits up to about 30 seconds first, so a few attempts are plenty.
    """
    for _ in range(attempts):
        r = client.get(f"/play/apps/{app_id}/listing", params={"country": country, "language": language})
        r.raise_for_status()
        if r.status_code == 200:
            return r.json()
    raise TimeoutError(f"listing {app_id} {country}/{language} is still being crawled")


def rankings(store: str, country: str, collection: str, limit: int = 5) -> tuple:
    """List endpoints return the full result count in the `total-count` header."""
    r = client.get(f"/{store}/rankings", params={"country": country, "collection": collection, "limit": limit})
    r.raise_for_status()
    return r.json(), r.headers.get("total-count")


if __name__ == "__main__":
    print(one_app("play", "com.twitter.android"))

    social = {"category": "SOCIAL"}
    print(size_segment("play", social))

    for app in top_by_revenue("play", social):
        print(f"{app['name']:40} {app.get('revenue_month', 0):>12,}")

    indonesian = listing("com.twitter.android", "ID", "id")
    print(indonesian["name"], "-", indonesian["short"], "(machine translated)" if indonesian["translated"] else "")

    charts, total = rankings("play", "US", "topselling_free")
    print(f"{total} chart rows available")
