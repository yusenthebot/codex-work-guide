#!/usr/bin/env python3
"""Validate external SVG icons before embedding them in academic figures."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any


UNSAFE_TAGS = {"script", "foreignObject", "image", "iframe", "object", "embed"}
URL_ATTRS = {"href", "xlink:href"}
FAMILY_ATTRS = ("stroke-width", "stroke-linecap", "stroke-linejoin", "fill", "stroke")


def local_name(name: str) -> str:
    return name.rsplit("}", 1)[-1]


def parse_number(value: str | None) -> float | None:
    if value is None:
        return None
    match = re.fullmatch(r"\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))(?:px)?\s*", value)
    return float(match.group(1)) if match else None


def collect_paths(inputs: list[Path]) -> list[Path]:
    paths: list[Path] = []
    for item in inputs:
        if item.is_dir():
            paths.extend(sorted(item.rglob("*.svg")))
        elif item.suffix.lower() == ".svg":
            paths.append(item)
    return sorted(dict.fromkeys(path.resolve() for path in paths))


def finding(severity: str, rule: str, path: Path, message: str) -> dict[str, str]:
    return {"severity": severity, "rule": rule, "file": str(path), "message": message}


def inspect_svg(path: Path) -> tuple[dict[str, Any], list[dict[str, str]]]:
    findings: list[dict[str, str]] = []
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        return {}, [finding("FAIL", "xml-parse", path, str(exc))]

    if local_name(root.tag) != "svg":
        findings.append(finding("FAIL", "root-element", path, "root element is not <svg>"))

    viewbox_raw = root.get("viewBox")
    viewbox: tuple[float, float, float, float] | None = None
    if viewbox_raw:
        try:
            values = tuple(float(part) for part in re.split(r"[\s,]+", viewbox_raw.strip()))
            if len(values) == 4 and values[2] > 0 and values[3] > 0:
                viewbox = values  # type: ignore[assignment]
            else:
                raise ValueError
        except ValueError:
            findings.append(finding("FAIL", "viewbox-invalid", path, f"invalid viewBox: {viewbox_raw!r}"))
    else:
        findings.append(finding("FAIL", "viewbox-missing", path, "missing viewBox; aspect cannot be preserved"))

    width = parse_number(root.get("width"))
    height = parse_number(root.get("height"))
    if width is not None and height is not None and viewbox is not None:
        declared_ratio = width / height
        viewbox_ratio = viewbox[2] / viewbox[3]
        if not math.isclose(declared_ratio, viewbox_ratio, rel_tol=0.01, abs_tol=0.01):
            findings.append(
                finding(
                    "FAIL",
                    "aspect-mismatch",
                    path,
                    f"declared ratio {declared_ratio:.3f} differs from viewBox ratio {viewbox_ratio:.3f}",
                )
            )

    for element in root.iter():
        tag = local_name(element.tag)
        if tag in UNSAFE_TAGS:
            findings.append(finding("FAIL", "unsafe-tag", path, f"forbidden <{tag}> element"))
        for raw_name, value in element.attrib.items():
            name = local_name(raw_name)
            if name.lower().startswith("on"):
                findings.append(finding("FAIL", "event-handler", path, f"forbidden attribute {name}"))
            if name in URL_ATTRS or raw_name.endswith("}href"):
                findings.append(finding("FAIL", "linked-resource", path, f"linked resource in {name}={value!r}"))
            if isinstance(value, str) and re.search(r"url\s*\(", value, flags=re.IGNORECASE):
                findings.append(finding("FAIL", "css-url", path, f"CSS url() reference in {name}"))

    family = {key: root.get(key, "") for key in FAMILY_ATTRS}
    ratio = viewbox[2] / viewbox[3] if viewbox is not None else None
    return {
        "file": str(path),
        "viewBox": viewbox_raw,
        "ratio": ratio,
        "width": width,
        "height": height,
        "family": family,
    }, findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path, help="SVG files or directories")
    parser.add_argument("--strict", action="store_true", help="treat family warnings as failures")
    parser.add_argument(
        "--max-aspect-factor",
        type=float,
        default=1.35,
        help="maximum widest/narrowest intrinsic aspect-ratio factor for one family (default: 1.35)",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--output", type=Path, help="write JSON report")
    args = parser.parse_args()

    paths = collect_paths(args.inputs)
    if not paths:
        print("ERROR: no SVG files found", file=sys.stderr)
        return 1

    assets: list[dict[str, Any]] = []
    findings: list[dict[str, str]] = []
    for path in paths:
        asset, asset_findings = inspect_svg(path)
        if asset:
            assets.append(asset)
        findings.extend(asset_findings)

    for attribute in FAMILY_ATTRS:
        values = Counter(asset["family"].get(attribute, "") for asset in assets)
        nonempty = {value: count for value, count in values.items() if value}
        if len(nonempty) > 1:
            severity = "FAIL" if args.strict else "WARN"
            findings.append(
                finding(
                    severity,
                    "family-style-mismatch",
                    Path("*"),
                    f"mixed {attribute} values: {nonempty}",
                )
            )

    ratios = [round(asset["ratio"], 4) for asset in assets if asset.get("ratio") is not None]
    aspect_factor = max(ratios) / min(ratios) if ratios and min(ratios) > 0 else None
    if aspect_factor is not None and aspect_factor > args.max_aspect_factor:
        severity = "FAIL" if args.strict else "WARN"
        findings.append(
            finding(
                severity,
                "family-aspect-mismatch",
                Path("*"),
                (
                    f"intrinsic aspect factor {aspect_factor:.3f} exceeds "
                    f"limit {args.max_aspect_factor:.3f} "
                    f"(min={min(ratios):.3f}, max={max(ratios):.3f})"
                ),
            )
        )

    fail_count = sum(item["severity"] == "FAIL" for item in findings)
    warn_count = sum(item["severity"] == "WARN" for item in findings)
    report = {
        "summary": {
            "files": len(paths),
            "fail": fail_count,
            "warn": warn_count,
            "passed": fail_count == 0,
            "aspect_factor": aspect_factor,
            "max_aspect_factor": args.max_aspect_factor,
        },
        "assets": assets,
        "findings": findings,
    }
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    if args.json or not args.output:
        print(payload)
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
