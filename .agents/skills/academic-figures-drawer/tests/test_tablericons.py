from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).parents[1] / "scripts" / "tablericons.py"
SPEC = importlib.util.spec_from_file_location("tablericons", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TablerIconsTests(unittest.TestCase):
    def test_search_prefers_exact_semantic_tokens(self) -> None:
        icons = [
            "robot",
            "robot-arm",
            "robot-face",
            "armchair",
            "a-b",
            "brand-robot-framework",
        ]
        results = MODULE.search_icons(icons, "robot arm", 3)
        self.assertEqual(results[0].slug, "robot-arm")
        self.assertNotIn("armchair", [result.slug for result in results])
        self.assertNotIn("a-b", [result.slug for result in results])

    def test_slug_rejects_traversal_and_urls(self) -> None:
        for slug in ("../robot", "robot.svg", "https://example.com/icon", "Robot"):
            with self.subTest(slug=slug), self.assertRaises(ValueError):
                MODULE.validate_slug(slug)

    def test_tree_parser_accepts_only_outline_svg_paths(self) -> None:
        tree = {
            "truncated": False,
            "tree": [
                {"path": f"icons/outline/icon-{index}.svg"} for index in range(1001)
            ]
            + [
                {"path": "icons/filled/robot.svg"},
                {"path": "icons/outline/../unsafe.svg"},
            ],
        }
        icons = MODULE.parse_tree(json.dumps(tree).encode())
        self.assertEqual(len(icons), 1001)
        self.assertNotIn("robot", icons)

    def test_vendor_writes_svg_and_license(self) -> None:
        svg = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"></svg>'
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "assets" / "robot.svg"
            with patch.object(MODULE, "request_bytes", return_value=svg):
                result = MODULE.vendor_icon("robot", output)
            self.assertEqual(output.read_bytes(), svg)
            self.assertEqual(result["license"], "MIT")
            self.assertTrue((output.parent / "LICENSE-Tabler.txt").exists())


if __name__ == "__main__":
    unittest.main()
