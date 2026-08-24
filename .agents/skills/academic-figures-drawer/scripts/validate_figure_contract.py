#!/usr/bin/env python3
"""Validate semantic component choices and exact figure geometry.

The companion JSON contract records judgments that XML alone cannot infer and
declares dimension/alignment/routing facts that can be checked deterministically.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


SCORE_KEYS = (
    "semantic_specificity",
    "silhouette_match",
    "style_coherence",
    "paper_scale_legibility",
    "aspect_fit",
)
VALID_GRADES = {"exact", "strong", "approximate", "reject"}


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    w: float
    h: float

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def bottom(self) -> float:
        return self.y + self.h

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2

    def expanded(self, clearance: float) -> Rect:
        return Rect(
            self.x - clearance,
            self.y - clearance,
            self.w + 2 * clearance,
            self.h + 2 * clearance,
        )


@dataclass(frozen=True)
class Finding:
    severity: str
    rule: str
    element_id: str
    message: str


@dataclass
class Cell:
    id: str
    parent: str
    style: str
    vertex: bool
    edge: bool
    source: str
    target: str
    geometry: ET.Element | None


def finding(severity: str, rule: str, element_id: str, message: str) -> Finding:
    return Finding(severity, rule, element_id, message)


def parse_cells(path: Path) -> tuple[dict[str, Cell], dict[str, Rect]]:
    tree = ET.parse(path)
    cells: dict[str, Cell] = {}
    for cell_el in tree.findall(".//mxCell"):
        cell_id = cell_el.get("id", "")
        cells[cell_id] = Cell(
            id=cell_id,
            parent=cell_el.get("parent", ""),
            style=cell_el.get("style", ""),
            vertex=cell_el.get("vertex") == "1",
            edge=cell_el.get("edge") == "1",
            source=cell_el.get("source", ""),
            target=cell_el.get("target", ""),
            geometry=cell_el.find("mxGeometry"),
        )

    rect_cache: dict[str, Rect] = {}

    def absolute_rect(cell_id: str, stack: set[str] | None = None) -> Rect | None:
        if cell_id in rect_cache:
            return rect_cache[cell_id]
        cell = cells.get(cell_id)
        if not cell or not cell.vertex or cell.geometry is None:
            return None
        stack = set() if stack is None else stack
        if cell_id in stack:
            raise ValueError(f"cyclic parent relation at {cell_id}")
        stack.add(cell_id)
        x = float(cell.geometry.get("x", 0))
        y = float(cell.geometry.get("y", 0))
        w = float(cell.geometry.get("width", 0))
        h = float(cell.geometry.get("height", 0))
        parent_rect = absolute_rect(cell.parent, stack)
        if parent_rect is not None:
            x += parent_rect.x
            y += parent_rect.y
        result = Rect(x, y, w, h)
        rect_cache[cell_id] = result
        stack.remove(cell_id)
        return result

    for cell_id in cells:
        absolute_rect(cell_id)
    return cells, rect_cache


def style_number(style: str, key: str, default: float) -> float:
    match = re.search(rf"(?:^|;){re.escape(key)}=([^;]+)", style)
    if not match:
        return default
    try:
        return float(match.group(1))
    except ValueError:
        return default


def point_for_endpoint(
    cell: Cell,
    endpoint: Cell | None,
    endpoint_rect: Rect | None,
    source: bool,
) -> tuple[float, float] | None:
    if cell.geometry is not None:
        key = "sourcePoint" if source else "targetPoint"
        point = cell.geometry.find(f"mxPoint[@as='{key}']")
        if point is not None:
            return float(point.get("x", 0)), float(point.get("y", 0))
    if endpoint is None or endpoint_rect is None:
        return None
    x_key = "exitX" if source else "entryX"
    y_key = "exitY" if source else "entryY"
    x_frac = style_number(cell.style, x_key, 0.5)
    y_frac = style_number(cell.style, y_key, 0.5)
    return endpoint_rect.x + endpoint_rect.w * x_frac, endpoint_rect.y + endpoint_rect.h * y_frac


def edge_points(cell: Cell, cells: dict[str, Cell], rects: dict[str, Rect]) -> list[tuple[float, float]]:
    if not cell.edge or cell.geometry is None:
        return []
    source = cells.get(cell.source)
    target = cells.get(cell.target)
    start = point_for_endpoint(cell, source, rects.get(cell.source), True)
    end = point_for_endpoint(cell, target, rects.get(cell.target), False)
    points: list[tuple[float, float]] = []
    if start:
        points.append(start)
    waypoints = cell.geometry.find("Array[@as='points']")
    if waypoints is not None:
        points.extend(
            (float(point.get("x", 0)), float(point.get("y", 0)))
            for point in waypoints.findall("mxPoint")
        )
    if end:
        points.append(end)
    return points


def has_explicit_route(cell: Cell) -> bool:
    if cell.geometry is None:
        return False
    return (
        cell.geometry.find("Array[@as='points']") is not None
        or cell.geometry.find("mxPoint[@as='sourcePoint']") is not None
        or cell.geometry.find("mxPoint[@as='targetPoint']") is not None
    )


def orientation(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def on_segment(a: tuple[float, float], b: tuple[float, float], p: tuple[float, float]) -> bool:
    epsilon = 1e-9
    return (
        min(a[0], b[0]) - epsilon <= p[0] <= max(a[0], b[0]) + epsilon
        and min(a[1], b[1]) - epsilon <= p[1] <= max(a[1], b[1]) + epsilon
        and abs(orientation(a, b, p)) <= epsilon
    )


def segments_intersect(
    a: tuple[float, float],
    b: tuple[float, float],
    c: tuple[float, float],
    d: tuple[float, float],
) -> bool:
    o1 = orientation(a, b, c)
    o2 = orientation(a, b, d)
    o3 = orientation(c, d, a)
    o4 = orientation(c, d, b)
    if (o1 > 0 > o2 or o1 < 0 < o2) and (o3 > 0 > o4 or o3 < 0 < o4):
        return True
    return any(
        (
            abs(value) <= 1e-9
            and on_segment(segment_a, segment_b, point)
        )
        for value, segment_a, segment_b, point in (
            (o1, a, b, c),
            (o2, a, b, d),
            (o3, c, d, a),
            (o4, c, d, b),
        )
    )


def segment_hits_rect(a: tuple[float, float], b: tuple[float, float], rect: Rect) -> bool:
    if rect.x <= a[0] <= rect.right and rect.y <= a[1] <= rect.bottom:
        return True
    if rect.x <= b[0] <= rect.right and rect.y <= b[1] <= rect.bottom:
        return True
    corners = (
        (rect.x, rect.y),
        (rect.right, rect.y),
        (rect.right, rect.bottom),
        (rect.x, rect.bottom),
    )
    sides = zip(corners, corners[1:] + corners[:1], strict=True)
    return any(segments_intersect(a, b, c, d) for c, d in sides)


def validate_components(
    contract: dict[str, Any], cells: dict[str, Cell], rects: dict[str, Rect]
) -> list[Finding]:
    findings: list[Finding] = []
    component_by_id: dict[str, dict[str, Any]] = {}
    for component in contract.get("components", []):
        cell_id = str(component.get("id", ""))
        component_by_id[cell_id] = component
        cell = cells.get(cell_id)
        rect = rects.get(cell_id)
        if cell is None or rect is None:
            findings.append(finding("FAIL", "component-exists", cell_id, "component id is missing or is not a vertex"))
            continue
        grade = str(component.get("match_grade", ""))
        if grade not in VALID_GRADES:
            findings.append(finding("FAIL", "component-grade", cell_id, f"invalid match_grade {grade!r}"))
        elif grade == "reject":
            findings.append(finding("FAIL", "component-grade", cell_id, "selected component is explicitly rejected"))
        elif grade == "approximate":
            note = str(component.get("approximation_note", "")).strip()
            severity = "WARN" if note else "FAIL"
            message = "approximate component requires a visible label and documented limitation"
            findings.append(finding(severity, "component-grade", cell_id, message))

        scores = component.get("scores", {})
        missing_scores = [key for key in SCORE_KEYS if key not in scores]
        if missing_scores:
            findings.append(finding("FAIL", "component-score", cell_id, f"missing score fields: {', '.join(missing_scores)}"))
        else:
            values = [scores[key] for key in SCORE_KEYS]
            if any(not isinstance(value, (int, float)) or not 1 <= value <= 5 for value in values):
                findings.append(finding("FAIL", "component-score", cell_id, "all component scores must be numeric values from 1 to 5"))
            else:
                total = float(sum(values))
                if total < float(component.get("minimum_score", 21)) or min(values) < 4:
                    findings.append(finding("FAIL", "component-score", cell_id, f"match score {total:g}/25 does not meet 21/25 with every criterion >= 4"))

        alternatives = component.get("alternatives", [])
        if len(alternatives) < 2 or any(not item.get("rejected_because") for item in alternatives):
            findings.append(finding("FAIL", "component-shortlist", cell_id, "record at least two rejected alternatives with reasons"))

        allowed = component.get("allowed_style_tokens", [])
        if allowed and not any(str(token) in cell.style for token in allowed):
            findings.append(finding("FAIL", "component-style", cell_id, f"style does not contain any allowed token: {allowed}"))
        forbidden = component.get("forbidden_style_tokens", [])
        used_forbidden = [token for token in forbidden if str(token) in cell.style]
        if used_forbidden:
            findings.append(finding("FAIL", "component-style", cell_id, f"style contains forbidden tokens: {used_forbidden}"))

        aspect = rect.w / rect.h if rect.h else math.inf
        expected = component.get("expected_aspect")
        if expected and len(expected) == 2 and not float(expected[0]) <= aspect <= float(expected[1]):
            findings.append(finding("FAIL", "component-aspect", cell_id, f"aspect {aspect:.3f} is outside [{expected[0]}, {expected[1]}]"))

    for group in contract.get("component_groups", []):
        ids = group.get("ids", [])
        expected_family = group.get("visual_family")
        for cell_id in ids:
            component = component_by_id.get(cell_id)
            if component is None:
                findings.append(finding("FAIL", "component-family", str(cell_id), "component group references an undeclared component"))
            elif expected_family and component.get("visual_family") != expected_family:
                findings.append(finding("FAIL", "component-family", str(cell_id), f"visual family must be {expected_family!r}"))
    return findings


def spread(values: list[float]) -> float:
    return max(values) - min(values) if values else 0.0


def validate_dimensions(contract: dict[str, Any], rects: dict[str, Rect]) -> list[Finding]:
    findings: list[Finding] = []
    for group in contract.get("dimension_groups", []):
        name = str(group.get("name", "unnamed dimension group"))
        ids = [str(cell_id) for cell_id in group.get("ids", [])]
        missing = [cell_id for cell_id in ids if cell_id not in rects]
        if missing:
            findings.append(finding("FAIL", "dimension-ids", name, f"missing vertices: {missing}"))
            continue
        boxes = [rects[cell_id] for cell_id in ids]
        tolerance = float(group.get("tolerance", 1))
        value_map = {
            "equal_width": [box.w for box in boxes],
            "equal_height": [box.h for box in boxes],
            "align_left": [box.x for box in boxes],
            "align_right": [box.right for box in boxes],
            "align_top": [box.y for box in boxes],
            "align_bottom": [box.bottom for box in boxes],
            "align_center_x": [box.cx for box in boxes],
            "align_center_y": [box.cy for box in boxes],
        }
        for check in group.get("checks", []):
            if check in value_map:
                delta = spread(value_map[check])
                if delta > tolerance:
                    findings.append(finding("FAIL", check, name, f"spread {delta:.3f}px exceeds tolerance {tolerance:g}px"))
            elif check == "equal_horizontal_gap":
                ordered = sorted(boxes, key=lambda box: box.x)
                gaps = [b.x - a.right for a, b in zip(ordered, ordered[1:], strict=False)]
                if gaps and (min(gaps) < 0 or spread(gaps) > tolerance):
                    findings.append(finding("FAIL", check, name, f"horizontal gaps {gaps} are not equal within {tolerance:g}px"))
            elif check == "equal_vertical_gap":
                ordered = sorted(boxes, key=lambda box: box.y)
                gaps = [b.y - a.bottom for a, b in zip(ordered, ordered[1:], strict=False)]
                if gaps and (min(gaps) < 0 or spread(gaps) > tolerance):
                    findings.append(finding("FAIL", check, name, f"vertical gaps {gaps} are not equal within {tolerance:g}px"))
            elif check == "snap_to_grid":
                grid = float(group.get("grid", 8))
                off_grid = [
                    cell_id
                    for cell_id, box in zip(ids, boxes, strict=True)
                    if any(abs(value / grid - round(value / grid)) > tolerance / grid for value in (box.x, box.y, box.w, box.h))
                ]
                if off_grid:
                    findings.append(finding("FAIL", check, name, f"off-grid vertices: {off_grid}"))
            else:
                findings.append(finding("FAIL", "dimension-check", name, f"unknown check {check!r}"))
    return findings


def rectangles_too_close(a: Rect, b: Rect, clearance: float) -> bool:
    return not (
        a.right + clearance <= b.x
        or b.right + clearance <= a.x
        or a.bottom + clearance <= b.y
        or b.bottom + clearance <= a.y
    )


def validate_non_overlap(contract: dict[str, Any], rects: dict[str, Rect]) -> list[Finding]:
    findings: list[Finding] = []
    for group in contract.get("non_overlap_groups", []):
        name = str(group.get("name", "unnamed non-overlap group"))
        ids = [str(cell_id) for cell_id in group.get("ids", [])]
        clearance = float(group.get("clearance", 0))
        for index, left_id in enumerate(ids):
            for right_id in ids[index + 1 :]:
                left, right = rects.get(left_id), rects.get(right_id)
                if left is None or right is None:
                    findings.append(finding("FAIL", "non-overlap-ids", name, f"missing vertex in pair {left_id}, {right_id}"))
                elif rectangles_too_close(left, right, clearance):
                    findings.append(finding("FAIL", "non-overlap", name, f"{left_id} and {right_id} violate {clearance:g}px clearance"))
    return findings


def validate_containment(contract: dict[str, Any], rects: dict[str, Rect]) -> list[Finding]:
    findings: list[Finding] = []
    for group in contract.get("containment", []):
        parent_id = str(group.get("container_id", ""))
        parent = rects.get(parent_id)
        inset = float(group.get("inset", 0))
        if parent is None:
            findings.append(finding("FAIL", "containment-container", parent_id, "container is missing"))
            continue
        for cell_id in group.get("ids", []):
            child = rects.get(str(cell_id))
            if child is None:
                findings.append(finding("FAIL", "containment-id", str(cell_id), "contained vertex is missing"))
                continue
            if not (
                child.x >= parent.x + inset
                and child.y >= parent.y + inset
                and child.right <= parent.right - inset
                and child.bottom <= parent.bottom - inset
            ):
                findings.append(finding("FAIL", "containment", str(cell_id), f"not contained in {parent_id} with {inset:g}px inset"))
    return findings


def validate_routes(
    contract: dict[str, Any], cells: dict[str, Cell], rects: dict[str, Rect]
) -> list[Finding]:
    findings: list[Finding] = []
    for route in contract.get("routes", []):
        name = str(route.get("name", "unnamed route group"))
        obstacle_ids = [str(cell_id) for cell_id in route.get("obstacle_ids", [])]
        clearance = float(route.get("clearance", 0))
        require_explicit = bool(route.get("require_explicit_waypoints", False))
        for edge_id in route.get("edge_ids", []):
            edge_id = str(edge_id)
            edge = cells.get(edge_id)
            if edge is None or not edge.edge:
                findings.append(finding("FAIL", "route-edge", edge_id, f"edge is missing in route group {name}"))
                continue
            if require_explicit and not has_explicit_route(edge):
                findings.append(finding("FAIL", "route-explicit", edge_id, "high-risk edge has no explicit points or waypoints"))
                continue
            points = edge_points(edge, cells, rects)
            if len(points) < 2:
                findings.append(finding("FAIL", "route-geometry", edge_id, "edge path cannot be reconstructed"))
                continue
            ignored = {edge.source, edge.target, *map(str, route.get("ignore_ids", []))}
            for obstacle_id in obstacle_ids:
                if obstacle_id in ignored:
                    continue
                obstacle = rects.get(obstacle_id)
                if obstacle is None:
                    findings.append(finding("FAIL", "route-obstacle", edge_id, f"declared obstacle {obstacle_id!r} is missing"))
                    continue
                expanded = obstacle.expanded(clearance)
                if any(segment_hits_rect(a, b, expanded) for a, b in zip(points, points[1:], strict=False)):
                    findings.append(finding("FAIL", "route-penetration", edge_id, f"route penetrates {obstacle_id} with {clearance:g}px clearance"))
    return findings


def run(drawio: Path, contract_path: Path) -> list[Finding]:
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    if contract.get("version") != 1:
        return [finding("FAIL", "contract-version", str(contract_path), "contract version must be 1")]
    cells, rects = parse_cells(drawio)
    return [
        *validate_components(contract, cells, rects),
        *validate_dimensions(contract, rects),
        *validate_non_overlap(contract, rects),
        *validate_containment(contract, rects),
        *validate_routes(contract, cells, rects),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("drawio", type=Path)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        findings = run(args.drawio, args.contract)
    except (OSError, ET.ParseError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.strict:
        findings = [
            Finding("FAIL", item.rule, item.element_id, item.message)
            if item.severity == "WARN"
            else item
            for item in findings
        ]
    failures = [item for item in findings if item.severity == "FAIL"]
    warnings = [item for item in findings if item.severity == "WARN"]
    report = {
        "drawio": str(args.drawio),
        "contract": str(args.contract),
        "summary": {
            "fail": len(failures),
            "warn": len(warnings),
            "passed": not failures,
        },
        "findings": [asdict(item) for item in findings],
    }
    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
    if args.json:
        print(output)
    else:
        for item in findings:
            print(f"{item.severity}: {item.rule}: {item.element_id}: {item.message}")
        print(f"{len(failures)} failure(s), {len(warnings)} warning(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
