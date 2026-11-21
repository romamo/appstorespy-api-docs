"""
Regenerate the Postman collection from the live contract.

    python tools/generate_postman.py
    python tools/generate_postman.py --check

The collection is a build artifact: regenerate it after any endpoint change rather than
editing it by hand. `--check` compares the committed collection with what the generator
would write and exits 1 on a difference; CI runs it on every pull request. Stdlib only,
so it needs no install.
"""
import argparse
import json
import sys
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "postman" / "appstorespy.postman_collection.json"
SPEC = "https://api.appstorespy.com/openapi.json"
BASE_URL = "https://api.appstorespy.com/v1"


def build(spec: dict) -> dict:
    groups: dict[str, list] = {}
    for path in sorted(spec["paths"]):
        ops = spec["paths"][path]
        for method, op in sorted(ops.items()):
            if method not in ("get", "post", "put", "patch", "delete"):
                continue
            tag = (op.get("tags") or ["Other"])[0]
            groups.setdefault(tag, []).append(item(path, method, op, spec))
    return {
        "info": {
            "name": "AppstoreSpy API",
            "description": (
                "Google Play and App Store market data.\n\n"
                "Set the `API_KEY` collection variable to the key from "
                "https://appstorespy.com/profile/api before sending anything.\n\n"
                f"Generated from AppstoreSpy API at {SPEC}."
            ),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "auth": {
            "type": "apikey",
            "apikey": [
                {"key": "key", "value": "API-KEY", "type": "string"},
                {"key": "value", "value": "{{API_KEY}}", "type": "string"},
                {"key": "in", "value": "header", "type": "string"},
            ],
        },
        "variable": [
            {"key": "baseUrl", "value": BASE_URL, "type": "string"},
            {"key": "API_KEY", "value": "", "type": "string"},
        ],
        "item": [{"name": tag, "item": items} for tag, items in sorted(groups.items())],
    }


def item(path: str, method: str, op: dict, spec: dict) -> dict:
    params = [resolve(p, spec) for p in op.get("parameters", [])]
    segments = [s for s in path.strip("/").split("/") if s]
    segments = [f":{s[1:-1]}" if s.startswith("{") else s for s in segments]

    query = [
        {
            "key": p["name"],
            "value": str(p.get("schema", {}).get("example", p.get("example", ""))),
            "description": p.get("description", ""),
            "disabled": not p.get("required", False),
        }
        for p in params
        if p["in"] == "query"
    ]
    # Postman repeats the enabled params in the raw URL; disabled ones live only in `query`.
    enabled = "&".join(f"{p['key']}={p['value']}" for p in query if not p["disabled"])
    raw = "{{baseUrl}}/" + "/".join(segments) + (f"?{enabled}" if enabled else "")

    headers = [{"key": "accept", "value": "application/json"}]
    request = {
        "method": method.upper(),
        "header": headers,
        "url": {
            "raw": raw,
            "host": ["{{baseUrl}}"],
            "path": segments,
            "query": query,
        },
        "description": op.get("description", ""),
    }
    variables = [
        {
            "key": p["name"],
            "value": str(p.get("schema", {}).get("example", p.get("example", ""))),
            "description": p.get("description", ""),
        }
        for p in params
        if p["in"] == "path"
    ]
    if variables:
        request["url"]["variable"] = variables
    if op.get("requestBody"):
        headers.append({"key": "content-type", "value": "application/json"})
        request["body"] = {
            "mode": "raw",
            "raw": '{\n  "filter": {}\n}',
            "options": {"raw": {"language": "json"}},
        }
    return {"name": op.get("summary", path), "request": request, "response": []}


def resolve(param: dict, spec: dict) -> dict:
    if "$ref" in param:
        node = spec
        for part in param["$ref"].lstrip("#/").split("/"):
            node = node[part]
        return node
    return param


def serialise(collection: dict) -> str:
    """The collection exactly as it is committed; the write and the check both use it."""
    return json.dumps(collection, indent=2, ensure_ascii=False) + "\n"


def fetch_spec() -> dict:
    with urllib.request.urlopen(SPEC, timeout=30) as response:
        return json.load(response)


def check(out: Path, expected: str) -> int:
    fix = "python tools/generate_postman.py"
    if not out.is_file():
        print(f"{out} is missing; run `{fix}` to generate it", file=sys.stderr)
        return 1
    if out.read_bytes() != expected.encode("utf-8"):
        print(
            f"{out} differs from what tools/generate_postman.py writes from {SPEC} "
            f"(a hand edit, or a contract change since it was generated); "
            f"run `{fix}` and commit the result",
            file=sys.stderr,
        )
        return 1
    print(f"{out} matches the generator's output")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Regenerate the Postman collection from the live contract.")
    parser.add_argument("out", nargs="?", type=Path, default=OUT, help=f"collection path (default: {OUT})")
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare the collection with the generator's output instead of writing it; exit 1 on a difference",
    )
    args = parser.parse_args(argv)
    expected = serialise(build(fetch_spec()))
    if args.check:
        return check(args.out, expected)
    with args.out.open("w", encoding="utf-8") as handle:
        handle.write(expected)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
