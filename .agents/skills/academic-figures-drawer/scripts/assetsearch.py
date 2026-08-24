#!/usr/bin/env python3
"""Search the curated template and scientific-asset catalog.

The catalog stores links and usage policy, not third-party asset files. Search it
before composing a non-trivial figure, then prefer tier 0 results. Tier 1 and 2
results require source/terms review and an asset-ledger entry.

Usage:
  python3 assetsearch.py "robot navigation block diagram" --json
  python3 assetsearch.py --list --tier 0
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


CATALOG = Path(__file__).resolve().parent.parent / "data" / "asset-catalog.json"
TOKEN_RE = re.compile(r"[\w.+-]+", re.UNICODE)


def load_catalog(path: Path = CATALOG) -> dict[str, Any]:
    """Load and minimally validate the catalog."""
    with path.open(encoding="utf-8") as handle:
        catalog = json.load(handle)
    if catalog.get("schema_version") != 1 or not isinstance(catalog.get("entries"), list):
        raise ValueError(f"unsupported asset catalog schema in {path}")
    return catalog


def tokens(text: str) -> list[str]:
    """Return deterministic, case-folded search tokens."""
    result: list[str] = []
    for token in TOKEN_RE.findall(text.casefold()):
        if len(token) <= 1:
            continue
        result.append(token)
        if re.fullmatch(r"[\u3400-\u9fff]+", token) and len(token) > 2:
            result.extend(token[index : index + 2] for index in range(len(token) - 1))
    return list(dict.fromkeys(result))


def searchable_text(entry: dict[str, Any]) -> dict[str, str]:
    """Build weighted text fields used by the ranker."""
    return {
        "title": str(entry.get("title", "")).casefold(),
        "keywords": " ".join(str(item) for item in entry.get("keywords", [])).casefold(),
        "kind": str(entry.get("kind", "")).casefold(),
        "description": " ".join(
            str(entry.get(field, ""))
            for field in ("default_action", "compatibility", "license")
        ).casefold(),
    }


def score_entry(entry: dict[str, Any], query: str) -> float:
    """Score an entry for exact phrases and token matches."""
    fields = searchable_text(entry)
    query_folded = query.casefold().strip()
    query_tokens = tokens(query)
    if not query_folded:
        return 1.0

    score = 0.0
    if query_folded in fields["title"]:
        score += 12.0
    if query_folded in fields["keywords"]:
        score += 8.0

    weights = {"title": 5.0, "keywords": 3.0, "kind": 2.0, "description": 1.0}
    matched_tokens = 0
    for token in query_tokens:
        token_score = max(
            (weight if token in fields[name] else 0.0)
            for name, weight in weights.items()
        )
        if token_score:
            matched_tokens += 1
            score += token_score

    if query_tokens and matched_tokens == len(query_tokens):
        score += 4.0
    return score


def search_entries(
    entries: list[dict[str, Any]],
    query: str,
    tiers: set[int] | None = None,
    kinds: set[str] | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Filter and rank catalog entries."""
    ranked: list[tuple[float, dict[str, Any]]] = []
    for entry in entries:
        if tiers is not None and int(entry["tier"]) not in tiers:
            continue
        if kinds is not None and str(entry["kind"]) not in kinds:
            continue
        score = score_entry(entry, query)
        if score <= 0:
            continue
        ranked.append((score, entry))

    ranked.sort(key=lambda item: (int(item[1]["tier"]), -item[0], item[1]["title"].casefold()))
    return [entry for _, entry in ranked[:limit]]


def print_table(entries: list[dict[str, Any]]) -> None:
    """Print concise human-readable results."""
    for entry in entries:
        print(f"[{entry['id']}] {entry['title']}  (tier {entry['tier']}, {entry['kind']})")
        print(f"  formats: {', '.join(entry['formats'])}")
        print(f"  license: {entry['license']}")
        print(f"  use: {entry['default_action']}")
        for label, url in entry.get("urls", {}).items():
            print(f"  {label}: {url}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="?", default="", help="semantic need, figure type, or object")
    parser.add_argument("--list", action="store_true", help="list catalog entries without a query")
    parser.add_argument("--tier", type=int, action="append", choices=(0, 1, 2), help="filter tier; repeatable")
    parser.add_argument("--kind", action="append", help="filter exact kind; repeatable")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    if not args.list and not args.query.strip():
        parser.error("provide a query or pass --list")
    if args.limit < 1:
        parser.error("--limit must be positive")

    catalog = load_catalog()
    results = search_entries(
        catalog["entries"],
        "" if args.list else args.query,
        tiers=set(args.tier) if args.tier else None,
        kinds=set(args.kind) if args.kind else None,
        limit=args.limit,
    )
    if not results:
        parser.exit(1, f"no catalog entries matched {args.query!r}\n")

    if args.json:
        print(
            json.dumps(
                {
                    "catalog_last_verified": catalog["last_verified"],
                    "results": results,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        print_table(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
