from __future__ import annotations

import base64
import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

SCRIPTS = Path(__file__).parents[1] / "scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


figkit = _load("figkit")
qa = _load("qa_svg_figure")


def _browser_or_none() -> str | None:
    try:
        return qa.find_browser()
    except SystemExit:
        return None


class MathMarkupTests(unittest.TestCase):
    def test_unbraced_command_subscript_is_one_token(self) -> None:
        out = figkit.rich("$E_\\theta$", 12)
        self.assertIn("θ", out)
        self.assertIn(">E<", out)

    def test_relations_are_spaced_only_at_base_level(self) -> None:
        out = figkit.rich("$a=b_{c=d}$", 12)
        self.assertIn(" = ", out)
        self.assertEqual(out.count(" = "), 1)

    def test_hyphen_becomes_minus_sign(self) -> None:
        self.assertIn("−", figkit.rich("$a_{t-1}$", 12))

    def test_baseline_is_restored_after_scripts(self) -> None:
        out = figkit.rich("x $a_t^{2}$ y", 12)
        total = sum(float(v) for v in re.findall(r'dy="(-?[0-9.]+)"', out))
        self.assertAlmostEqual(total, 0.0, places=6)

    def test_prime_calligraphic_and_blackboard(self) -> None:
        out = figkit.rich("$a'_t\\in\\mathcal{L}\\times\\mathbb{R}$", 12)
        for glyph in ("′", "ℒ", "ℝ", "×"):
            self.assertIn(glyph, out)

    def test_set_and_mapping_notation(self) -> None:
        out = figkit.rich("$\\kappa: V\\to\\mathcal{C},\\ \\mathrm{pre}(c)\\subseteq F_t,\\ \\langle\\theta,\\ldots\\rangle,\\ \\mathcal{B}\\subseteq\\mathcal{C}\\times\\Pi$", 12)
        for glyph in ("κ", "𝒞", "⊆", "⟨", "…", "⟩", "ℬ", "Π"):
            self.assertIn(glyph, out)
        self.assertIn("\u2005⊆\u2005", out)

    def test_accent_attaches_combining_mark(self) -> None:
        atoms, _ = figkit._parse("\\hat{\\tau}")
        self.assertEqual(atoms[0]["t"], "τ̂")

    def test_plain_text_is_escaped(self) -> None:
        self.assertIn("&lt;b&gt;", figkit.rich("<b>", 12))


class AssetTests(unittest.TestCase):
    def test_solid_icon_without_paint_is_tinted_with_currentcolor(self) -> None:
        raw = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960">'
               '<path d="M0 0h10v10H0z"/></svg>')
        asset = figkit.parse_svg_asset(raw, "arm.svg")
        self.assertIn('fill="currentColor"', asset.body)
        self.assertEqual(asset.view_box, (0.0, -960.0, 960.0, 960.0))

    def test_literal_black_paint_becomes_currentcolor(self) -> None:
        raw = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="#000">'
               '<path d="M0 0h10v10H0z" stroke="black"/></svg>')
        body = figkit.parse_svg_asset(raw, "robot.svg").body
        self.assertIn('fill="currentColor"', body)
        self.assertIn('stroke="currentColor"', body)
        self.assertNotIn("#000", body)

    def test_real_colors_and_none_survive(self) -> None:
        raw = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
               'stroke="currentColor"><path d="M0 0h1v1H0z" fill="#615CED"/></svg>')
        body = figkit.parse_svg_asset(raw, "logo.svg").body
        self.assertIn('fill="none"', body)
        self.assertIn("#615CED", body)


class FigureTests(unittest.TestCase):
    def build(self) -> figkit.Fig:
        f = figkit.Fig(400, 200)
        top = f.panel(4, 4, 392, 192, "blue", "(a) Stage", sub="subtitle", title_size=15)
        self.assertEqual(top, 38)
        card = f.card(12, 60, 150, 120, "green", stack=1, topbar=True)
        f.text(20, 80, "Card $x_t$", box=card)
        f.chip(20, 90, 60, 20, "chip", "purple")
        f.badge(90, 90, "12%", "red")
        f.pill(120, 150, "loop", "gray")
        f.icon("spark", 20, 120, 18, "#000")
        f.icon("spark", 40, 120, 18, "#000")
        f.scene(200, 60, 80, 60, frame="#333")
        f.arrow("M170 100H190", "#123456")
        f.arrow("M170 110H190", "#123456", dashed=True)
        f.brace(290, 60, 180)
        f.bars(300, 60, 80, 40, [0.2, 0.8, 0.5], "#999")
        f.curves(300, 110, 80, 40, ["#111", "#222"])
        f.strip(300, 160, 80, 10, 10, 3, "#0A0")
        return f

    def test_svg_is_well_formed(self) -> None:
        root = ET.fromstring(self.build().svg())
        self.assertTrue(root.tag.endswith("svg"))

    def test_markers_and_symbols_are_deduplicated(self) -> None:
        svg = self.build().svg()
        self.assertEqual(svg.count('id="ah1234567"'), 1)
        self.assertEqual(svg.count('id="i-spark"'), 1)

    def test_text_is_linked_to_its_container(self) -> None:
        svg = self.build().svg()
        box_ids = set(re.findall(r'data-box="([^"]+)"', svg))
        linked = set(re.findall(r'data-in="([^"]+)"', svg))
        self.assertTrue(linked)
        self.assertTrue(linked <= box_ids)

    def test_headerless_panel(self) -> None:
        f = figkit.Fig(100, 60)
        self.assertEqual(f.panel(0, 0, 100, 60, "gray", None), 10)

    def test_subtitle_below_reserves_second_line(self) -> None:
        f = figkit.Fig(200, 100)
        self.assertEqual(f.panel(0, 0, 200, 100, "gray", "(a) Inputs", sub="narrow panel", sub_below=True, title_size=15), 48)

    def test_font_sizes_follow_the_print_width(self) -> None:
        wide, column = figkit.Fig(1400, 400), figkit.Fig(700, 400)
        self.assertEqual(wide.print_width_pt, figkit.TEXT_WIDTH_PT)
        self.assertEqual(column.print_width_pt, figkit.COLUMN_WIDTH_PT)
        self.assertAlmostEqual(wide.fs("min"), 16.3, places=1)
        self.assertAlmostEqual(column.fs("label"), 18.6, places=1)
        self.assertAlmostEqual(figkit.Fig(1400, 400, print_width_pt=252).fs("label"), 37.2, places=1)
        wide.text(10, 30, "label")
        svg = wide.svg()
        self.assertIn('font-size="18.2"', svg)
        self.assertEqual(ET.fromstring(svg).get("data-print-width-pt"), "516")

    def test_example_cards_and_bubbles_are_marked(self) -> None:
        f = figkit.Fig(400, 200)
        f.example(10, 10, 200, 60)
        f.bubble(10, 100, 200, 40, "Set the table")
        self.assertEqual(f.svg().count('data-kind="example"'), 2)

    def test_image_embeds_raster_bytes(self) -> None:
        png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg==")
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp) / "render.png"
            good.write_bytes(png)
            fake = Path(tmp) / "fake.png"
            fake.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
            f = figkit.Fig(400, 200)
            f.image(good, 10, 10, 120, 80)
            svg = f.svg()
            self.assertIn('href="data:image/png;base64,', svg)
            self.assertIn('data-kind="thumb"', svg)
            ET.fromstring(svg)
            with self.assertRaises(ValueError):
                f.image(fake, 10, 10, 120, 80)
            old = figkit.MAX_IMAGE_BYTES
            figkit.MAX_IMAGE_BYTES = 10
            try:
                with self.assertRaises(ValueError):
                    f.image(good, 10, 10, 120, 80)
            finally:
                figkit.MAX_IMAGE_BYTES = old

    def test_default_font_is_inherited_so_family_attributes_win(self) -> None:
        f = figkit.Fig(200, 60)
        f.text(10, 20, "obs", family="serif", italic=True)
        f.text(10, 40, "accept", family="mono")
        svg = f.svg()
        self.assertNotRegex(svg, r"text\{[^}]*font-family")
        root = ET.fromstring(svg)
        self.assertIn("Helvetica", root.get("font-family", ""))
        families = [el.get("font-family", "") for el in root.iter() if el.tag.endswith("text")]
        self.assertTrue(any("STIX" in fam for fam in families))
        self.assertTrue(any("Menlo" in fam for fam in families))

    def test_meaningful_shapes_are_well_formed(self) -> None:
        f = figkit.Fig(400, 200)
        f.tokens(10, 10, 6, "blue", lit=4, to_role="amber")
        f.trapezoid(10, 30, 80, 40, "blue", "$E_\\theta$")
        f.bracket(100, 30, 80, 40)
        f.cylinder(200, 30, 50, 40, "green", "$h_t$")
        f.bubble(270, 30, 100, 30, "“fold shirt”")
        f.step(20, 120, 3)
        f.block_arrow(40, 120, 120, 120, width=10)
        f.block_arrow(200, 100, 200, 180, width=10)
        f.card(250, 100, 100, 60, "amber", key=True)
        root = ET.fromstring(f.svg())
        self.assertTrue(root.tag.endswith("svg"))
        self.assertIn('stroke="#1F1F1F"', f.svg())

    def test_palette_aliases_share_roles(self) -> None:
        self.assertIs(figkit.PAL["teal"], figkit.PAL["blue"])
        self.assertIs(figkit.PAL["ochre"], figkit.PAL["amber"])
        for role in figkit.PAL.values():
            for color in (role.accent, role.tint, role.deep, role.mid):
                self.assertRegex(color, r"^#[0-9A-F]{6}$")


TABLER_LIKE = """<!-- tags: [focus] -->
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
  stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon">
  <title>target</title>
  <path d="M3 12a9 9 0 1 0 18 0a9 9 0 1 0 -18 0" />
</svg>"""

GRADIENT_LOGO = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 24" height="1em" style="flex:none">
<defs><linearGradient id="a"><stop offset="0" stop-color="#000"/></linearGradient></defs>
<path fill="url(#a)" d="M0 0h48v24H0z"/><use href="#a"/></svg>"""


class SvgAssetTests(unittest.TestCase):
    def write(self, tmp: str, name: str, text: str) -> Path:
        path = Path(tmp) / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_symbol_is_shared_and_stroke_is_normalized_per_use(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            icon = self.write(tmp, "target.svg", TABLER_LIKE)
            f = figkit.Fig(200, 60)
            box = f.asset(icon, 10, 10, 16, color="#7A5506")
            f.asset(icon, 40, 10, 24)
            svg = f.svg()
        root = ET.fromstring(svg)
        symbols = [el for el in root.iter() if el.tag.endswith("symbol")]
        self.assertEqual(len(symbols), 1)
        group = symbols[0][0]
        self.assertEqual(group.get("stroke"), "currentColor")
        self.assertIsNone(group.get("stroke-width"))
        self.assertNotIn("<title>", svg)
        uses = [el for el in root.iter() if el.tag.endswith("use")]
        self.assertEqual([u.get("stroke-width") for u in uses], ["2.250", "1.500"])
        self.assertEqual(uses[0].get("color"), "#7A5506")
        self.assertIn(f'data-box="{box}" data-kind="icon"', svg)

    def test_ids_are_namespaced_and_aspect_is_kept(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            logo = self.write(tmp, "logo.svg", GRADIENT_LOGO)
            f = figkit.Fig(200, 60)
            f.asset(logo, 0, 0, 40)
            svg = f.svg()
        ids = re.findall(r'<linearGradient id="([^"]+)"', svg)
        self.assertEqual(len(ids), 1)
        self.assertTrue(ids[0].startswith("logo-") and ids[0].endswith("-a"))
        self.assertIn(f'fill="url(#{ids[0]})"', svg)
        self.assertIn(f'href="#{ids[0]}"', svg)
        self.assertIn('height="20.00"', svg)
        ET.fromstring(svg)

    def test_unsafe_or_invalid_svg_is_rejected(self) -> None:
        bad = {
            "script": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><script>alert(1)</script></svg>',
            "handler": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" onload="x()"/>',
            "remote": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><use href="https://e.com/a.svg#b"/></svg>',
            "css": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><style>text{fill:red}</style></svg>',
            "entity": '<!DOCTYPE svg [<!ENTITY a "b">]><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"/>',
            "no-viewbox": '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"/>',
            "not-svg": '<html xmlns="http://www.w3.org/1999/xhtml"/>',
        }
        for name, text in bad.items():
            with self.subTest(name=name), self.assertRaises(ValueError):
                figkit.parse_svg_asset(text, f"{name}.svg")


def label_markup(fig, s: str) -> str:
    """The <text> element whose content is `s` (figkit wraps label runs in tspans)."""
    return next(m for m in re.findall(r"<text[^>]*>.*?</text>", fig.svg()) if f">{s}<" in m)


class LayoutTests(unittest.TestCase):
    def test_columns_and_rows_are_exact_and_snapped(self) -> None:
        f = figkit.Fig(1400, 500)
        cols = f.cols(8, 1392, 4, 12)
        self.assertEqual([x for x, _ in cols], [8, 357, 706, 1055])
        self.assertEqual({w for _, w in cols}, {337})
        gaps = [cols[i + 1][0] - (cols[i][0] + cols[i][1]) for i in range(3)]
        self.assertEqual(set(gaps), {12})
        self.assertEqual(f.rows(0, 100, 2, 10), [(0, 45), (55, 45)])
        with self.assertRaises(ValueError):
            f.cols(0, 50, 5, 20)

    def test_place_centers_a_run_of_widths(self) -> None:
        f = figkit.Fig(1400, 500)
        self.assertEqual(f.place(0, 600, [100, 120, 80], gap=20), [130, 250, 390])

    def test_place_refuses_a_run_that_does_not_fit(self) -> None:
        f = figkit.Fig(1400, 500)
        with self.assertRaises(ValueError):
            f.place(8, 1392, (420, 500, 420), gap=40)

    def test_containers_register_their_rectangle(self) -> None:
        f = figkit.Fig(1400, 500)
        card = f.card(10, 20, 100, 40, "blue")
        chip = f.chip(200, 30, 60, 24, "x", "gray")
        self.assertEqual(f.rect(card), (10, 20, 100, 40))
        self.assertEqual(f.rect(chip), (200, 30, 60, 24))
        with self.assertRaises(KeyError):
            f.rect("nope")

    def test_ports_sit_on_the_edges(self) -> None:
        f = figkit.Fig(1400, 500)
        card = f.card(100, 100, 200, 60, "blue")
        self.assertEqual(f.port(card, "left"), (100, 130))
        self.assertEqual(f.port(card, "right", out=2), (302, 130))
        self.assertEqual(f.port(card, "top", t=0.25), (150, 100))
        self.assertEqual(f.port(card, "bottom"), (200, 160))
        with self.assertRaises(ValueError):
            f.port(card, "middle")

    def test_connect_anchors_on_edges_and_elbows_when_offset(self) -> None:
        f = figkit.Fig(1400, 500)
        a = f.card(40, 100, 200, 60, "blue")
        b = f.card(400, 100, 200, 60, "green")
        c = f.card(400, 300, 200, 60, "amber")
        self.assertEqual(f.connect(a, b), "M241.0 130.0H399.0")
        self.assertEqual(f.connect(a, c, mid=320), "M241.0 130.0H320.0V330.0H399.0")
        self.assertEqual(f.connect(b, c), "M500.0 161.0V299.0")
        f.connect(a, b, label="then")
        self.assertIn(">then<", f.svg())

    def test_bus_forks_through_one_trunk(self) -> None:
        f = figkit.Fig(1400, 500)
        src = f.card(40, 40, 200, 60, "blue")
        targets = [f.card(400, 200 + 80 * k, 160, 50, "purple") for k in range(3)]
        trunk = f.bus(src, targets, side="bottom")
        svg = f.svg()
        self.assertEqual(trunk, 150)
        for top in ("V199.0", "V279.0", "V359.0"):
            self.assertIn(top, svg)
        self.assertIn("H480.0", svg)  # one trunk spanning the targets

    def test_bus_face_overrides_the_entry_side(self) -> None:
        f = figkit.Fig(1400, 400)
        src = f.card(40, 120, 200, 60, "blue")
        targets = [f.card(400 + 300 * k, 120, 200, 60, "green") for k in range(2)]
        f.bus(src, targets, side="top", at=90, face="top", color=figkit.WIRE)
        svg = f.svg()
        self.assertIn("M140.0 119.0V90.0", svg)      # stem up from the source
        for stub in ("M500.0 90.0V119.0", "M800.0 90.0V119.0"):
            self.assertIn(stub, svg)                  # and back down into each target's top

    def test_arc_bends_to_one_side(self) -> None:
        f = figkit.Fig(1400, 500)
        a = f.card(40, 40, 120, 40, "blue")
        b = f.card(600, 40, 120, 40, "green")
        cx, cy = f.arc(a, b, bulge=50)
        self.assertAlmostEqual(cx, 380.0, places=1)
        self.assertAlmostEqual(cy, 110.0, places=1)
        self.assertIn("Q380.0 110.0", f.svg())

    def test_arc_label_sits_outside_the_bend(self) -> None:
        f = figkit.Fig(1400, 500)
        a = f.card(40, 40, 120, 40, "blue")
        b = f.card(600, 40, 120, 40, "green")
        f.arc(a, b, bulge=60, label="retry", label_size=16)
        apex_y = 90.0  # midpoint y 60, control y 120, so the curve peaks at 90
        y = float(re.search(r'y="([\d.]+)"', label_markup(f, "retry")).group(1))
        self.assertGreater(y, apex_y + 10)  # below the apex, never on the curve

    def test_arc_label_flips_inward_at_the_canvas_edge(self) -> None:
        f = figkit.Fig(600, 500)
        a = f.card(500, 400, 80, 40, "blue")
        b = f.card(500, 60, 80, 40, "green")
        f.arc(a, b, sides=("right", "right"), bulge=30, label="next", label_size=16)
        x = float(re.search(r'x="([\d.]+)"', label_markup(f, "next")).group(1))
        self.assertLess(x, 581)  # the outside would leave the canvas, so the label moves inward

    def test_curve_is_straight_when_ports_line_up_and_an_s_otherwise(self) -> None:
        f = figkit.Fig(600, 400)
        a = f.card(100, 40, 100, 40, "blue")
        b = f.card(100, 200, 100, 40, "green")
        c = f.card(300, 200, 100, 40, "green")
        self.assertEqual(f.curve(a, b), "M150.0 81.0V199.0")
        self.assertEqual(f.curve(a, c, ta=0.8, tb=0.2), "M180.0 81.0C180.0 140.0 320.0 140.0 320.0 199.0")
        self.assertEqual(f.curve(b, a, up=True), "M150.0 199.0V81.0")

    def test_route_wraps_through_its_lanes(self) -> None:
        f = figkit.Fig(1400, 600)
        a = f.card(100, 400, 200, 60, "blue")
        b = f.card(100, 60, 200, 60, "green")
        self.assertEqual(f.route(a, b, (520, 60), sides=("bottom", "left")),
                         "M200.0 461.0V520.0H60.0V90.0H99.0")
        self.assertEqual(f.route(a, b, (360,), sides=("right", "right")),
                         "M301.0 430.0H360.0V90.0H301.0")

    def test_route_labels_the_segment_asked_for(self) -> None:
        f = figkit.Fig(1400, 600)
        a = f.card(100, 400, 200, 60, "blue")
        b = f.card(100, 60, 200, 60, "green")
        f.route(a, b, (520, 60), sides=("bottom", "left"), label="back", label_seg=1, label_size=16)
        y = float(re.search(r'y="([\d.]+)"', label_markup(f, "back")).group(1))
        self.assertAlmostEqual(y, 513.0, places=1)  # above the lane at y 520

    def test_route_label_at_moves_the_label_along_its_segment(self) -> None:
        f = figkit.Fig(1400, 600)
        a = f.card(100, 400, 200, 60, "blue")
        b = f.card(100, 60, 200, 60, "green")
        f.route(a, b, (520, 60), sides=("bottom", "left"), label="back", label_seg=1, label_at=150, label_size=16)
        x = float(re.search(r'x="([\d.]+)"', label_markup(f, "back")).group(1))
        self.assertAlmostEqual(x, 150.0, places=1)
        with self.assertRaises(ValueError):  # the lane runs from x 200 to x 60
            f.route(a, b, (520, 60), sides=("bottom", "left"), label="off", label_seg=1, label_at=260)

    def test_trapezoid_narrows_toward_the_named_end(self) -> None:
        f = figkit.Fig(400, 200)
        f.trapezoid(10, 20, 60, 100, "blue", direction="right", inset=0.2, dashed=True)
        svg = f.svg()
        self.assertIn('points="10,20 70,40.0 70,100.0 10,120"', svg)  # tall on the left, short on the right
        self.assertIn('stroke-dasharray="4 3"', svg)
        with self.assertRaises(ValueError):
            f.trapezoid(0, 0, 10, 10, "blue", direction="sideways")

    def test_neural_network_visuals_register_their_boxes(self) -> None:
        f = figkit.Fig(900, 300)
        grid = f.patch_grid(10, 10, 88, 66, 3, 4, masked=((0, 1),), content=lambda x, y, w, h: None)
        vec = f.vector(120, 10, 5, "blue", cell=10, gap=2)
        toks = f.token_grid(150, 10, 2, 4, "amber", cell=12, gap=2, masked=((0, 0),), highlight=((1, 3),))
        heat = f.heatmap(220, 10, 4, 4, "red", cell=8)
        stack = f.layer_stack(280, 10, 60, 80, 3, "blue", s="$E$", depth=5, repeat="$\\times L$")
        maps = f.feature_maps(360, 60, ((8, 40), (12, 30)), "blue", gap=6)
        net = f.mlp(460, 10, 100, 80, (3, 4, 2), "purple")
        self.assertEqual(f.rect(vec), (120.0, 10.0, 10.0, 58.0))
        self.assertEqual(f.rect(toks), (150.0, 10.0, 54.0, 26.0))
        self.assertEqual(f.rect(heat), (220.0, 10.0, 32.0, 32.0))
        self.assertEqual(f.rect(stack), (280.0, 20.0, 60.0, 70.0))  # full width, front-face height
        self.assertEqual(f.rect(f.stack_front)[1:], (20, 50, 70))
        self.assertEqual(len(maps), 2)
        self.assertEqual(f.rect(net), (460.0, 10.0, 100.0, 80.0))
        svg = f.svg()
        ET.fromstring(svg)
        self.assertEqual(svg.count("<circle"), 9)  # one node per unit
        self.assertIn('stroke-dasharray="2 1.5"', svg)  # the masked token
        self.assertTrue(grid)

    def test_colour_assets_keep_their_paint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            icon = Path(tmp) / "cup.svg"
            icon.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="none">'
                            '<path d="M0 0h8v8H0z" fill="#000"/><path d="M8 8h8v8H8z" fill="#D3D3D3"/></svg>')
            f = figkit.Fig(200, 100)
            f.asset(icon, 10, 10, 32, color=None)
            f.asset(icon, 60, 10, 32)
            svg = f.svg()
        self.assertEqual(svg.count("<symbol"), 2)  # the coloured and the tinted copies are separate symbols
        self.assertIn('fill="#000"', svg)
        self.assertIn('fill="currentColor"', svg)

    def test_cells_give_patch_centres_and_sizes(self) -> None:
        cell = figkit.Fig.cells(10, 20, 104, 78, 3, 4)
        self.assertEqual(cell(0, 0), (23.0, 33.0, 26.0, 26.0))
        self.assertEqual(cell(2, 3), (101.0, 85.0, 26.0, 26.0))

    def test_token_row_is_registered_so_overhang_is_caught(self) -> None:
        f = figkit.Fig(400, 200)
        card = f.card(10, 10, 120, 40, "blue")
        width = f.tokens(20, 20, 8, "gray", w=16, h=10, gap=4)
        self.assertEqual(width, 8 * 16 + 7 * 4)
        row = f.rects[next(k for k in f.rects if k.startswith("tk"))]
        self.assertEqual(row, (20, 20, float(width), 10))
        self.assertGreater(row[0] + row[2], f.rect(card)[0] + f.rect(card)[2])  # the gate now sees the overhang

    def test_zone_anchors_connectors_without_drawing(self) -> None:
        f = figkit.Fig(1400, 500)
        z = f.zone(100, 100, 200, 60)
        card = f.card(500, 100, 200, 60, "blue")
        self.assertEqual(f.rect(z), (100, 100, 200, 60))
        self.assertEqual(f.connect(z, card), "M301.0 130.0H499.0")
        self.assertNotIn(z, f.svg())


class QaGateTests(unittest.TestCase):
    def report(self, **overrides) -> dict:
        base = {key: [] for key in qa.CHECKS}
        base["coverage"] = 0.7
        base.update(overrides)
        return base

    def test_clean_report_passes(self) -> None:
        self.assertEqual(qa.failures(self.report(), 0.55), [])

    def test_any_issue_or_low_coverage_fails(self) -> None:
        self.assertEqual(qa.failures(self.report(lineText=[["a", "M0 0"]]), 0.55), ["lineText=1"])
        self.assertEqual(qa.failures(self.report(coverage=0.3), 0.55), ["coverage=0.3 < 0.55"])

    def test_strict_tidy_turns_geometry_reports_into_failures(self) -> None:
        clean = self.report(tidy={key: [] for key in qa.TIDY_CHECKS})
        self.assertEqual(qa.failures(clean, 0.4, strict_tidy=True), [])
        sloppy = self.report(tidy={**{key: [] for key in qa.TIDY_CHECKS}, "edgeGap": [{"gap": 6}], "misalign": [{"spread": 3}]})
        self.assertEqual(qa.failures(sloppy, 0.4), [])
        self.assertEqual(qa.failures(sloppy, 0.4, strict_tidy=True), ["tidy.edgeGap=1", "tidy.misalign=1"])

    def test_word_budget_is_enforced(self) -> None:
        self.assertEqual(qa.failures(self.report(words=40, wordBudget=56), 0.4), [])
        self.assertEqual(qa.failures(self.report(words=90, wordBudget=56), 0.4), ["words=90 > budget 56"])

    @unittest.skipUnless(_browser_or_none(), "Chrome/Chromium/Edge not available")
    def test_browser_detects_overflow_and_line_through_label(self) -> None:
        f = figkit.Fig(300, 120)
        card = f.card(10, 10, 80, 40, "blue")
        f.text(20, 34, "this label is far too long for its card", size=12, box=card)
        f.text(150, 92, "label", size=14)
        f.line("M140 88H220", "#000", 1.5)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.svg"
            f.save(str(path))
            report = qa.measure(path, _browser_or_none())
        self.assertEqual(len(report["overflow"]), 1)
        self.assertEqual(len(report["lineText"]), 1)

    @unittest.skipUnless(_browser_or_none(), "Chrome/Chromium/Edge not available")
    def test_browser_flags_small_labels_but_not_math_scripts(self) -> None:
        f = figkit.Fig(1400, 120)
        f.text(20, 40, "tiny annotation", size=12.5)
        f.text(20, 80, "readable $a_t^{2}$ label", size=18)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "small.svg"
            f.save(str(path))
            report = qa.measure(path, _browser_or_none())
            relaxed = qa.measure(path, _browser_or_none(), min_font=9)
        self.assertEqual([item["s"] for item in report["smallText"]], ["tiny annotation"])
        self.assertEqual(relaxed["smallText"], [])

    @unittest.skipUnless(_browser_or_none(), "Chrome/Chromium/Edge not available")
    def test_browser_flags_sentences_outside_example_content(self) -> None:
        f = figkit.Fig(1400, 300)
        f.text(20, 40, "every navigate node uses the same contract")
        f.text(20, 80, "Skill graph")
        note = f.example(20, 120, 900, 60)
        f.text(30, 160, "Pick up the apple and place it on the table", box=note)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "words.svg"
            f.save(str(path))
            report = qa.measure(path, _browser_or_none())
            tight = qa.measure(path, _browser_or_none(), words_per_10k=0.02)
        self.assertEqual([item["words"] for item in report["longText"]], [7])
        self.assertEqual(report["words"], 9)
        self.assertEqual(report["wordBudget"], 42)
        self.assertIn("words=9 > budget 1", qa.failures(tight, 0.0))

    @unittest.skipUnless(_browser_or_none(), "Chrome/Chromium/Edge not available")
    def test_browser_reports_sloppy_geometry(self) -> None:
        f = figkit.Fig(1400, 300)
        a = f.card(40, 60, 200, 60, "blue")
        f.card(300, 63, 200, 60, "green")  # top off by 3 px
        c = f.card(560, 60, 200, 60, "amber")
        f.card(860, 60, 200, 60, "purple")  # uneven gap
        f.arrow("M245 90H292", "#333", 1.4)  # stops short of the next card
        tidy_arrow = f.connect(a, c, ta=0.5, tb=0.5)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sloppy.svg"
            f.save(str(path))
            report = qa.measure(path, _browser_or_none())
        tidy = report["tidy"]
        self.assertIn("M241.0 90.0H559.0", tidy_arrow)
        self.assertTrue(any(item["issue"] == "short of the edge" for item in tidy["edgeGap"]))
        self.assertTrue(any(item["axis"] == "top" and item["spread"] == 3 for item in tidy["misalign"]))
        self.assertTrue(any(item["kind"] == "row" for item in tidy["gapUneven"]))
        self.assertEqual(qa.failures(report, 0.0, strict_tidy=True) and True, True)

    @unittest.skipUnless(_browser_or_none(), "Chrome/Chromium/Edge not available")
    def test_browser_reports_a_label_hidden_under_a_later_card(self) -> None:
        f = figkit.Fig(600, 200)
        card = f.card(20, 20, 300, 60, "blue")
        f.text(30, 55, "Generalist policy", size=20, box=card)
        f.chip(150, 24, 120, 40, "ACT", "blue")  # drawn later, so it hides the tail of the label
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "covered.svg"
            f.save(str(path))
            report = qa.measure(path, _browser_or_none())
        self.assertTrue(any("Generalist" in item["s"] for item in report["textCovered"]))
        self.assertIn("textCovered=1", qa.failures(report, 0.0))

    @unittest.skipUnless(_browser_or_none(), "Chrome/Chromium/Edge not available")
    def test_browser_reports_a_label_pressed_against_a_drawing(self) -> None:
        f = figkit.Fig(600, 300)
        f.text(20, 40, "rank candidates", size=16)
        end = 20 + figkit.text_w("rank candidates", 16)
        f.add(f'<rect x="{end - 4:.0f}" y="28" width="60" height="8" fill="#C9A227"/>')  # butts into the word
        f.text(20, 120, "query graphs", size=16)
        f.add('<rect x="160" y="106" width="60" height="8" fill="#C9A227"/>')  # well clear of it
        card = f.chip(20, 180, 120, 34, "inside", "gray")
        top = f.card(300, 150, 80, 28, "gray")
        bottom = f.card(300, 204, 80, 28, "gray")
        f.connect(top, bottom, sides=("bottom", "top"), label="on", label_size=16)  # serif word in a 26 px gap
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "crowded.svg"
            f.save(str(path))
            report = qa.measure(path, _browser_or_none())
        crowded = [item["s"] for item in report["tidy"]["crowded"]]
        self.assertIn("rank candidates", crowded)
        self.assertNotIn("query graphs", crowded)
        self.assertNotIn("inside", crowded)
        self.assertNotIn("on", crowded)  # measured on the ink, not on the 1.5 em line box
        self.assertTrue(card)
        self.assertTrue(any(k.startswith("tidy.crowded") for k in qa.failures(report, 0.0, strict_tidy=True)))

    @unittest.skipUnless(_browser_or_none(), "Chrome/Chromium/Edge not available")
    def test_browser_reports_a_box_that_straddles_a_panel_edge(self) -> None:
        f = figkit.Fig(600, 300)
        f.panel(10, 10, 280, 280, "gray", "(a) Left")
        f.panel(300, 10, 290, 280, "blue", "(b) Right")
        f.card(40, 80, 120, 60, "purple")  # inside (a)
        f.pill(300, 250, "across", size=16)  # centred on (b)'s left edge
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "straddle.svg"
            f.save(str(path))
            report = qa.measure(path, _browser_or_none())
        found = report["tidy"]["straddle"]
        self.assertTrue(found and all(s["box"].startswith("chip:") for s in found))
        self.assertTrue(any(k.startswith("tidy.straddle") for k in qa.failures(report, 0.0, strict_tidy=True)))

    @unittest.skipUnless(_browser_or_none(), "Chrome/Chromium/Edge not available")
    def test_browser_reports_a_drawing_that_crosses_its_card(self) -> None:
        f = figkit.Fig(600, 300)
        f.card(40, 40, 120, 100, "purple")
        f.add('<path d="M28 120C60 120 80 70 100 70S140 120 172 120" fill="none" stroke="#6B5BA8"/>')  # tails out
        f.card(240, 40, 120, 100, "purple")
        f.add('<path d="M256 120C280 120 290 70 300 70S320 120 344 120" fill="none" stroke="#6B5BA8"/>')  # inside
        f.card(420, 60, 120, 80, "blue", stack=1)  # the offset sheets behind a stack are decoration, not overflow
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "overflow.svg"
            f.save(str(path))
            report = qa.measure(path, _browser_or_none())
        found = report["tidy"]["sketchOverflow"]
        self.assertEqual(len(found), 1)
        self.assertTrue(found[0]["what"].startswith("path:28,"))
        self.assertAlmostEqual(found[0]["by"], 12.0, delta=0.6)

    @unittest.skipUnless(_browser_or_none(), "Chrome/Chromium/Edge not available")
    def test_browser_treats_boxes_sharing_a_baseline_as_aligned(self) -> None:
        f = figkit.Fig(400, 240)
        f.card(20, 20, 300, 200, "gray")
        f.card(40, 60, 40, 30, "gray", kind="chip")  # rests on y = 90
        f.card(120, 52, 40, 38, "gray", kind="chip")  # taller, rests on the same line
        f.card(40, 140, 40, 30, "gray", kind="chip")
        f.card(120, 141, 40, 30, "gray", kind="chip")  # 1 px lower than its neighbour: a real near-miss
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "baseline.svg"
            f.save(str(path))
            report = qa.measure(path, _browser_or_none())
        groups = [set(item["which"]) for item in report["tidy"]["misalign"]]
        self.assertNotIn({"chip:40,60", "chip:120,52"}, groups)  # sharing a baseline is alignment
        self.assertIn({"chip:40,140", "chip:120,141"}, groups)

    @unittest.skipUnless(_browser_or_none(), "Chrome/Chromium/Edge not available")
    def test_browser_accepts_a_fork_off_a_trunk(self) -> None:
        f = figkit.Fig(900, 300)
        src = f.card(40, 200, 200, 60, "blue")
        targets = [f.card(400, 200, 160, 60, "green"), f.card(620, 200, 160, 60, "green")]
        f.bus(src, targets, side="top", at=140, face="top")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fork.svg"
            f.save(str(path))
            report = qa.measure(path, _browser_or_none())
        self.assertEqual(report["tidy"]["edgeGap"], [])  # stubs start on the trunk, not near a box

    @unittest.skipUnless(_browser_or_none(), "Chrome/Chromium/Edge not available")
    def test_browser_applies_monospace_family(self) -> None:
        # Narrow glyphs fit a 60 px box in sans; the same string only overflows if monospace really renders.
        f = figkit.Fig(300, 120)
        sans_box = f.card(10, 10, 60, 30, "gray")
        f.text(15, 30, "iiiiiiiiii", size=14, box=sans_box)
        mono_box = f.card(10, 60, 60, 30, "gray")
        f.text(15, 80, "iiiiiiiiii", size=14, box=mono_box, family="mono")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fonts.svg"
            f.save(str(path))
            report = qa.measure(path, _browser_or_none())
        self.assertEqual(len(report["overflow"]), 1)


class ScaffoldTests(unittest.TestCase):
    def test_scaffold_vendors_kit_and_writes_a_runnable_script(self) -> None:
        scaffold = _load("scaffold")
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "figures" / "src" / "fig_demo_pipeline.py"
            written = scaffold.scaffold(target, 1400, 400, 3, force=False, update_kit=False)
            self.assertIn(target, written)
            for name in ("figkit.py", "qa_svg_figure.py"):
                self.assertTrue((target.parent / name).exists())
            subprocess.run([sys.executable, str(target)], cwd=target.parent, check=True, capture_output=True)
            svg = target.parent.parent / "demo_pipeline-figure.svg"
            self.assertTrue(ET.parse(svg).getroot().tag.endswith("svg"))
            with self.assertRaises(SystemExit):
                scaffold.scaffold(target, 1400, 400, 3, force=False, update_kit=False)


if __name__ == "__main__":
    unittest.main()
