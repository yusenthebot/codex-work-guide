from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_figure_contract.py"
SPEC = importlib.util.spec_from_file_location("validate_figure_contract", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


DRAWIO = """<mxfile><diagram><mxGraphModel pageWidth="400" pageHeight="200"><root>
<mxCell id="0"/><mxCell id="1" parent="0"/>
<mxCell id="a" value="A" style="rounded=1;shape=card;" vertex="1" parent="1"><mxGeometry x="10" y="20" width="80" height="40" as="geometry"/></mxCell>
<mxCell id="b" value="B" style="rounded=1;shape=card;" vertex="1" parent="1"><mxGeometry x="110" y="20" width="80" height="40" as="geometry"/></mxCell>
<mxCell id="obstacle" value="X" style="rounded=1;" vertex="1" parent="1"><mxGeometry x="95" y="80" width="20" height="20" as="geometry"/></mxCell>
<mxCell id="edge" style="edgeStyle=orthogonalEdgeStyle;exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="a" target="b"><mxGeometry relative="1" as="geometry"><Array as="points"><mxPoint x="100" y="40"/></Array></mxGeometry></mxCell>
</root></mxGraphModel></diagram></mxfile>"""


def component(cell_id: str) -> dict:
    return {
        "id": cell_id,
        "intended_noun": "test card",
        "selected_candidate": "card primitive",
        "match_grade": "exact",
        "visual_family": "line",
        "scores": {
            "semantic_specificity": 5,
            "silhouette_match": 5,
            "style_coherence": 5,
            "paper_scale_legibility": 5,
            "aspect_fit": 5,
        },
        "alternatives": [
            {"name": "x", "rejected_because": "wrong noun"},
            {"name": "y", "rejected_because": "wrong family"},
        ],
        "expected_aspect": [1.9, 2.1],
        "allowed_style_tokens": ["shape=card"],
    }


class FigureContractTests(unittest.TestCase):
    def write_case(self, contract: dict) -> tuple[Path, Path, tempfile.TemporaryDirectory]:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        drawio = root / "figure.drawio"
        contract_path = root / "figure-contract.json"
        drawio.write_text(DRAWIO, encoding="utf-8")
        contract_path.write_text(json.dumps(contract), encoding="utf-8")
        return drawio, contract_path, tmp

    def test_valid_contract_passes(self) -> None:
        contract = {
            "version": 1,
            "components": [component("a"), component("b")],
            "component_groups": [{"ids": ["a", "b"], "visual_family": "line"}],
            "dimension_groups": [{
                "name": "row",
                "ids": ["a", "b"],
                "checks": ["equal_width", "equal_height", "align_top", "equal_horizontal_gap"],
                "tolerance": 1,
            }],
            "non_overlap_groups": [{"name": "row", "ids": ["a", "b"], "clearance": 10}],
            "routes": [{
                "name": "main",
                "edge_ids": ["edge"],
                "obstacle_ids": ["obstacle"],
                "require_explicit_waypoints": True,
            }],
        }
        drawio, contract_path, tmp = self.write_case(contract)
        self.addCleanup(tmp.cleanup)
        self.assertEqual(MODULE.run(drawio, contract_path), [])

    def test_rejects_bad_match_and_penetration(self) -> None:
        bad = component("a")
        bad["match_grade"] = "reject"
        bad["scores"]["silhouette_match"] = 2
        contract = {
            "version": 1,
            "components": [bad],
            "routes": [{
                "name": "bad-route",
                "edge_ids": ["edge"],
                "obstacle_ids": ["obstacle"],
                "clearance": 80,
                "require_explicit_waypoints": True,
            }],
        }
        drawio, contract_path, tmp = self.write_case(contract)
        self.addCleanup(tmp.cleanup)
        rules = {item.rule for item in MODULE.run(drawio, contract_path)}
        self.assertIn("component-grade", rules)
        self.assertIn("component-score", rules)
        self.assertIn("route-penetration", rules)

    def test_global_routing_rejects_undeclared_component_collision(self) -> None:
        contract = {
            "version": 1,
            "components": [component("a"), component("b"), component("obstacle")],
            "global_routing": {
                "enabled": True,
                "edge_ids": ["edge"],
                "obstacle_clearance": 41,
            },
        }
        contract["components"][2]["expected_aspect"] = [0.9, 1.1]
        contract["components"][2]["allowed_style_tokens"] = ["rounded=1"]
        drawio, contract_path, tmp = self.write_case(contract)
        self.addCleanup(tmp.cleanup)
        rules = {item.rule for item in MODULE.run(drawio, contract_path)}
        self.assertIn("global-route-penetration", rules)

    def test_nontrivial_figure_cannot_disable_global_routing(self) -> None:
        third = component("obstacle")
        third["expected_aspect"] = [0.9, 1.1]
        third["allowed_style_tokens"] = ["rounded=1"]
        contract = {
            "version": 1,
            "components": [component("a"), component("b"), third],
        }
        drawio, contract_path, tmp = self.write_case(contract)
        self.addCleanup(tmp.cleanup)
        rules = {item.rule for item in MODULE.run(drawio, contract_path)}
        self.assertIn("global-routing-required", rules)

    def test_global_routing_rejects_border_following_port(self) -> None:
        bad_drawio = DRAWIO.replace(
            '<mxPoint x="100" y="40"/>',
            '<mxPoint x="90" y="60"/><mxPoint x="100" y="60"/><mxPoint x="100" y="40"/>',
        )
        contract = {
            "version": 1,
            "components": [component("a"), component("b")],
            "global_routing": {"enabled": True, "edge_ids": ["edge"]},
        }
        drawio, contract_path, tmp = self.write_case(contract)
        self.addCleanup(tmp.cleanup)
        drawio.write_text(bad_drawio, encoding="utf-8")
        rules = {item.rule for item in MODULE.run(drawio, contract_path)}
        self.assertIn("global-route-port", rules)

    def test_global_routing_rejects_crossing_semantic_edges(self) -> None:
        extra_edge = (
            '<mxCell id="cross" style="edgeStyle=orthogonalEdgeStyle;" edge="1" parent="1">'
            '<mxGeometry relative="1" as="geometry">'
            '<mxPoint x="100" y="10" as="sourcePoint"/>'
            '<mxPoint x="100" y="70" as="targetPoint"/>'
            '<Array as="points"><mxPoint x="100" y="30"/></Array>'
            '</mxGeometry></mxCell>'
        )
        crossing_drawio = DRAWIO.replace('</root>', extra_edge + '</root>')
        contract = {
            "version": 1,
            "components": [],
            "global_routing": {"enabled": True, "edge_ids": ["edge", "cross"]},
        }
        drawio, contract_path, tmp = self.write_case(contract)
        self.addCleanup(tmp.cleanup)
        drawio.write_text(crossing_drawio, encoding="utf-8")
        rules = {item.rule for item in MODULE.run(drawio, contract_path)}
        self.assertIn("global-route-crossing", rules)

    def test_global_routing_discovers_unlisted_freestanding_obstacles(self) -> None:
        moved_obstacle = DRAWIO.replace(
            'x="95" y="80" width="20" height="20"',
            'x="95" y="34" width="20" height="12"',
        )
        contract = {
            "version": 1,
            "components": [component("a"), component("b")],
            "global_routing": {"enabled": True, "edge_ids": ["edge"]},
        }
        drawio, contract_path, tmp = self.write_case(contract)
        self.addCleanup(tmp.cleanup)
        drawio.write_text(moved_obstacle, encoding="utf-8")
        rules = {item.rule for item in MODULE.run(drawio, contract_path)}
        self.assertIn("global-route-penetration", rules)

    def test_global_routing_rejects_container_border_crossing(self) -> None:
        boundary = (
            '<mxCell id="boundary" style="container=1;" vertex="1" parent="1">'
            '<mxGeometry x="95" y="10" width="50" height="60" as="geometry"/>'
            '</mxCell>'
        )
        bounded_drawio = DRAWIO.replace('</root>', boundary + '</root>')
        contract = {
            "version": 1,
            "components": [component("a"), component("b")],
            "global_routing": {
                "enabled": True,
                "edge_ids": ["edge"],
                "boundary_ids": ["boundary"],
            },
        }
        drawio, contract_path, tmp = self.write_case(contract)
        self.addCleanup(tmp.cleanup)
        drawio.write_text(bounded_drawio, encoding="utf-8")
        rules = {item.rule for item in MODULE.run(drawio, contract_path)}
        self.assertIn("global-route-boundary", rules)


if __name__ == "__main__":
    unittest.main()
