#!/usr/bin/env python3
"""Search and vendor selected Tabler outline SVG icons.

Tabler is the default external icon family for this skill.  The command keeps
the skill package small by caching the official GitHub tree index locally and
downloading only the SVG files selected for a figure.

Examples:
  python3 tablericons.py search "robot" --limit 8 --json
  python3 tablericons.py get robot --out assets/tabler/robot.svg
  python3 tablericons.py get tools --out assets/tabler/tools.svg --force
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

TREE_URL = "https://api.github.com/repos/tabler/tabler-icons/git/trees/main?recursive=1"
RAW_URL = "https://raw.githubusercontent.com/tabler/tabler-icons/main/icons/outline/{slug}.svg"
PAGE_URL = "https://tabler.io/icons/icon/{slug}"
LICENSE_FILE = (
    Path(__file__).resolve().parent.parent / "references" / "TABLER_ICONS_LICENSE.txt"
)
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TOKEN_RE = re.compile(r"[a-z0-9]+")
MAX_RESPONSE_BYTES = 12 * 1024 * 1024
DEFAULT_CACHE_SECONDS = 7 * 24 * 60 * 60
FORBIDDEN_SVG = (
    b"<script",
    b"<foreignobject",
    b" onload=",
    b" onclick=",
    b"xlink:",
    b"url(",
)


@dataclass(frozen=True)
class Match:
    slug: str
    score: int


def default_cache_dir() -> Path:
    """Return an XDG-compatible cache directory without a hardcoded user path."""
    base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    return base / "academic-figures-drawer"


def request_bytes(url: str, *, timeout: float = 20.0) -> bytes:
    """Fetch a bounded response from an allowlisted official Tabler URL."""
    if not url.startswith(
        (
            "https://api.github.com/repos/tabler/tabler-icons/",
            "https://raw.githubusercontent.com/tabler/tabler-icons/",
        )
    ):
        raise ValueError(f"refusing non-Tabler URL: {url}")
    request = urllib.request.Request(
        url, headers={"User-Agent": "academic-figures-drawer/1"}
    )
    # The prefix allowlist above excludes file:, custom schemes, and arbitrary hosts.
    with urllib.request.urlopen(request, timeout=timeout) as response:  # nosec B310
        payload = response.read(MAX_RESPONSE_BYTES + 1)
    if len(payload) > MAX_RESPONSE_BYTES:
        raise ValueError(f"response exceeds {MAX_RESPONSE_BYTES} bytes")
    return payload


def parse_tree(payload: bytes) -> list[str]:
    """Extract safe outline-icon slugs from a GitHub recursive tree response."""
    document = json.loads(payload)
    if document.get("truncated"):
        raise ValueError("GitHub tree response was truncated")
    slugs: list[str] = []
    for item in document.get("tree", []):
        path = str(item.get("path", ""))
        match = re.fullmatch(r"icons/outline/([a-z0-9]+(?:-[a-z0-9]+)*)\.svg", path)
        if match:
            slugs.append(match.group(1))
    if len(slugs) < 1000:
        raise ValueError(f"unexpectedly small Tabler index: {len(slugs)} icons")
    return sorted(set(slugs))


def load_index(cache_dir: Path, *, refresh: bool = False) -> list[str]:
    """Load the cached index or refresh it from the official GitHub tree."""
    cache_path = cache_dir / "tabler-outline-index.json"
    if cache_path.exists() and not refresh:
        age = time.time() - cache_path.stat().st_mtime
        if age <= DEFAULT_CACHE_SECONDS:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            icons = cached.get("icons", [])
            if isinstance(icons, list) and all(
                SLUG_RE.fullmatch(str(icon)) for icon in icons
            ):
                return [str(icon) for icon in icons]

    icons = parse_tree(request_bytes(TREE_URL))
    cache_dir.mkdir(parents=True, exist_ok=True)
    document = {"source": TREE_URL, "fetched_at": int(time.time()), "icons": icons}
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=cache_dir, delete=False
    ) as handle:
        json.dump(document, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        temp_path = Path(handle.name)
    temp_path.replace(cache_path)
    return icons


def query_tokens(query: str) -> list[str]:
    """Normalize English technical nouns into deterministic slug tokens."""
    aliases = {
        "ai": "brain",
        "artifact": "file",
        "certificate": "certificate",
        "experiment": "flask",
        "folder": "folder",
        "log": "logs",
        "model": "brain",
        "plugin": "plug",
        "robotics": "robot",
        "simulation": "cube",
        "skill": "tools",
    }
    tokens = TOKEN_RE.findall(query.casefold())
    expanded = [aliases.get(token, token) for token in tokens]
    return list(dict.fromkeys(expanded))


def score_slug(slug: str, tokens: list[str]) -> int:
    """Rank a slug by exact token, prefix, substring, and compact-phrase match."""
    if not tokens:
        return 0
    parts = slug.split("-")
    compact = "".join(tokens)
    score = 0
    for token in tokens:
        matched = False
        if token == slug:
            score += 100
            matched = True
        elif token in parts:
            score += 35
            matched = True
        elif any(
            (len(token) >= 2 and part.startswith(token))
            or (len(part) >= 3 and token.startswith(part))
            for part in parts
        ):
            score += 18
            matched = True
        elif token in slug:
            score += 10
            matched = True
        if not matched:
            score -= 20
    if compact == slug.replace("-", ""):
        score += 60
    if all(
        any(
            token == part
            or (len(token) >= 3 and len(part) >= 3 and (token in part or part in token))
            for part in parts
        )
        for token in tokens
    ):
        score += 25
    score -= max(0, len(parts) - len(tokens))
    return score


def search_icons(icons: list[str], query: str, limit: int) -> list[Match]:
    """Return the highest-scoring icon slugs."""
    tokens = query_tokens(query)
    matches = [Match(slug, score_slug(slug, tokens)) for slug in icons]
    matches = [match for match in matches if match.score > 0]
    matches.sort(key=lambda match: (-match.score, len(match.slug), match.slug))
    return matches[:limit]


def validate_slug(slug: str) -> str:
    """Reject traversal, URLs, and unsupported Tabler icon variants."""
    if not SLUG_RE.fullmatch(slug):
        raise ValueError(f"invalid Tabler icon slug: {slug!r}")
    return slug


def validate_svg(payload: bytes, slug: str) -> None:
    """Apply a small boundary check before writing a downloaded SVG."""
    lowered = payload.lower()
    if b"<svg" not in lowered or b"viewbox=" not in lowered:
        raise ValueError(f"{slug}: response is not a viewBox-based SVG")
    used = [token.decode("ascii") for token in FORBIDDEN_SVG if token in lowered]
    if used:
        raise ValueError(f"{slug}: unsafe SVG tokens: {used}")


def vendor_icon(slug: str, output: Path, *, force: bool = False) -> dict[str, Any]:
    """Download one official outline SVG and copy the MIT license beside it."""
    slug = validate_slug(slug)
    if output.exists() and not force:
        raise FileExistsError(f"refusing to overwrite {output}; pass --force")
    payload = request_bytes(RAW_URL.format(slug=slug))
    validate_svg(payload, slug)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", dir=output.parent, delete=False) as handle:
        handle.write(payload)
        temp_path = Path(handle.name)
    temp_path.replace(output)
    if LICENSE_FILE.exists():
        shutil.copyfile(LICENSE_FILE, output.parent / "LICENSE-Tabler.txt")
    return {
        "slug": slug,
        "output": str(output.resolve()),
        "source": RAW_URL.format(slug=slug),
        "page": PAGE_URL.format(slug=slug),
        "license": "MIT",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, default=default_cache_dir())
    subparsers = parser.add_subparsers(dest="command", required=True)

    search = subparsers.add_parser(
        "search", help="search official Tabler outline icon names"
    )
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=8)
    search.add_argument("--refresh", action="store_true")
    search.add_argument("--json", action="store_true")

    get = subparsers.add_parser("get", help="vendor one selected outline SVG")
    get.add_argument("slug")
    get.add_argument("--out", type=Path, required=True)
    get.add_argument("--force", action="store_true")
    get.add_argument("--json", action="store_true")

    args = parser.parse_args()
    try:
        if args.command == "search":
            if args.limit < 1:
                parser.error("--limit must be positive")
            matches = search_icons(
                load_index(args.cache_dir, refresh=args.refresh),
                args.query,
                args.limit,
            )
            if not matches:
                parser.exit(1, f"no Tabler icons matched {args.query!r}\n")
            results = [
                {
                    "slug": match.slug,
                    "score": match.score,
                    "page": PAGE_URL.format(slug=match.slug),
                }
                for match in matches
            ]
            if args.json:
                print(
                    json.dumps(
                        {
                            "family": "Tabler outline",
                            "license": "MIT",
                            "results": results,
                        },
                        indent=2,
                    )
                )
            else:
                for result in results:
                    print(
                        f"{result['slug']:<36} score={result['score']:>3}  {result['page']}"
                    )
            return 0

        result = vendor_icon(args.slug, args.out, force=args.force)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(result["output"])
        return 0
    except (
        FileExistsError,
        ValueError,
        urllib.error.HTTPError,
        urllib.error.URLError,
    ) as exc:
        parser.exit(1, f"error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
