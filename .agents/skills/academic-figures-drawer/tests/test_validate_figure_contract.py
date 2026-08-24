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


if __name__ == "__main__":
    unittest.main()
