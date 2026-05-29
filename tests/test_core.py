from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from PIL import Image
import yaml

from academic_deck_compiler.cli import (
    DEFAULT_COMPARE_GRAMMARS,
    HIGHSENSE_20_GRAMMARS,
    beautiful_template_candidates,
    compare_row,
    composition_family_signature,
    grammar_style_family,
    html_pptx_only,
    layout_report_summary,
    mark_delivery_blocked,
    parse_grammar_list,
    recommended_rows,
    repair_hints_for_report,
    repair_actions_for_report,
    revision_rows,
    score_grammar_variant,
    write_deck_repair_plan,
    write_design_direction_report,
    write_repair_draft,
    write_repair_manifest,
)
from academic_deck_compiler.content import Crop, KNOWN_LAYOUT_INTENTS
from academic_deck_compiler.design_directions import (
    DESIGN_DIRECTIONS,
    direction_for_grammar,
    direction_count,
    directions_for_grammar,
)
from academic_deck_compiler.assets import crop_asset
from academic_deck_compiler.evidence_audit import classify_reference, evidence_mix, scan_assets, write_evidence_report
from academic_deck_compiler.html_export import (
    audit_html_layout,
    cadence_issues,
    create_image_pptx,
    find_chrome,
    strict_warning_count,
    write_layout_audit_report,
)
from academic_deck_compiler.ir import dump_default_deck, load_deck
from academic_deck_compiler.judge import edge_pressure
from academic_deck_compiler.package import package_build
from academic_deck_compiler.paths import ROOT
from academic_deck_compiler.quality import check_deck
from academic_deck_compiler.render_html import VISUAL_GRAMMARS, composition_for, render_html
from academic_deck_compiler.render_pptx import render_pptx
from academic_deck_compiler.source_manifest import write_source_manifest


class CompilerSmokeTests(unittest.TestCase):
    def test_default_deck_round_trip_has_no_errors(self) -> None:
        with TemporaryDirectory() as tmp:
            deck_path = Path(tmp) / "deck.yaml"
            dump_default_deck(deck_path)
            deck = load_deck(deck_path)
            issues = check_deck(deck)
        self.assertEqual(deck.deck_id, "technical-research-talk")
        self.assertEqual(deck.visual_grammar, "editorial-profile")
        self.assertFalse([issue for issue in issues if issue.level == "error"])

    def test_missing_asset_is_reported(self) -> None:
        deck = load_deck()
        slide = deck.slides[0]
        patched = type(deck)(
            deck_id=deck.deck_id,
            title=deck.title,
            subtitle=deck.subtitle,
            footer=deck.footer,
            contact=deck.contact,
            assets_dir=deck.assets_dir,
            slides=(type(slide)(**{**slide.__dict__, "image": "missing.png"}),),
        )
        issues = check_deck(patched)
        self.assertTrue(any(issue.level == "error" and "missing.png" in issue.message for issue in issues))

    def test_invalid_crop_and_callout_are_reported(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "assets"
            assets.mkdir()
            Image.new("RGB", (800, 500), color=(230, 230, 230)).save(assets / "proof.png")
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: crop-test",
                        "title: Crop Test",
                        f"assets_dir: {assets.as_posix()}",
                        "slides:",
                        "  - kind: evidence",
                        "    kicker: Proof",
                        "    title: Bad crops should fail before visual rendering",
                        "    image: proof.png",
                        "    evidence:",
                        "      image: proof.png",
                        "      crop:",
                        "        x: 0.9",
                        "        y: 0.1",
                        "        w: 0.3",
                        "        h: 0.4",
                        "      caption: bad crop",
                        "      source: fixture",
                        "      callouts:",
                        "        - x: 1.1",
                        "          y: 0.5",
                        "          text: outside",
                    ]
                ),
                encoding="utf-8",
            )
            deck = load_deck(deck_path)
            messages = [issue.message for issue in check_deck(deck) if issue.level == "error"]
            self.assertTrue(any("extends outside" in message for message in messages))
            self.assertTrue(any("Callout pin" in message for message in messages))

    def test_pptx_renderer_respects_assets_dir(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "custom-assets"
            assets.mkdir()
            Image.new("RGB", (64, 64), color=(20, 30, 40)).save(assets / "proof.png")

            deck_path = root / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: asset-test",
                        "title: Asset Test",
                        "subtitle: custom assets dir",
                        "footer: Asset Test",
                        f"assets_dir: {assets.as_posix()}",
                        "slides:",
                        "  - kind: product",
                        "    kicker: Proof",
                        "    title: Renderer should find a custom image",
                        "    subtitle: This verifies deck.assets_dir reaches PPTX rendering.",
                        "    image: proof.png",
                        "    bullets: []",
                        "    labels: []",
                        "    metrics: []",
                    ]
                ),
                encoding="utf-8",
            )
            deck = load_deck(deck_path)
            out = render_pptx(root / "asset-test.pptx", deck)
            self.assertTrue(out.exists())
            self.assertGreater(out.stat().st_size, 20_000)

    def test_evidence_crop_is_materialized(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "wide.png"
            Image.new("RGB", (100, 50), color=(240, 240, 240)).save(source)

            cropped = crop_asset(source, Crop(x=0.25, y=0.2, w=0.5, h=0.4), root / "cache", "wide-mid")

            self.assertTrue(cropped.exists())
            with Image.open(cropped) as im:
                self.assertEqual(im.size, (70, 40))

    def test_edge_pressure_detects_content_near_border(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            clean = root / "clean.png"
            crowded = root / "crowded.png"
            Image.new("RGB", (160, 90), color=(250, 250, 240)).save(clean)
            im = Image.new("RGB", (160, 90), color=(250, 250, 240))
            for x in range(160):
                for y in range(5):
                    im.putpixel((x, y), (10, 10, 10))
            im.save(crowded)

            self.assertLess(edge_pressure(clean), edge_pressure(crowded))

    def test_html_renderer_writes_preview(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            deck = load_deck()
            html = render_html(root / "html", deck)
            self.assertTrue(html.exists())
            text = html.read_text(encoding="utf-8")
            self.assertIn("<section", text)
            self.assertIn('data-visual-grammar="editorial-profile"', text)
            self.assertIn('params.get("slide")', text)
            self.assertIn('params.get("audit")', text)
            self.assertIn("element-overlap", text)
            self.assertIn("text-block-overlap", text)
            self.assertIn("text-block-clearance-tight", text)
            self.assertIn("text-line-overlap", text)
            self.assertIn("text-line-height-tight", text)
            self.assertIn("text-self-overlap", text)
            self.assertIn("title-wrap-too-deep", text)
            self.assertIn("subtitle-wrap-too-deep", text)
            self.assertIn("text-clearance-tight", text)
            self.assertIn("text-image-overlap", text)
            self.assertIn("text-image-clearance-tight", text)
            self.assertIn("proof-notes-image-overlap", text)
            self.assertIn("artifact-notes-image-overlap", text)
            self.assertIn("notes-image-clearance-tight", text)
            self.assertIn("IMAGE_TEXT_OVERLAP_MIN_AREA_PX", text)
            self.assertIn("IMAGE_SIDE_CLEARANCE_PX", text)
            self.assertIn("TEXT_BLOCK_CLEARANCE_PX", text)
            self.assertIn("horizontal clearance between text and image/proof slot", text)
            self.assertIn("text-clipped", text)
            self.assertIn("figure-caption-overlap", text)
            self.assertIn("figure-caption-clearance-tight", text)
            self.assertIn("TEXT_LINE_HEIGHT_SAFE_RATIO", text)
            self.assertIn("container-overflow", text)
            self.assertIn("content-underfilled", text)
            self.assertIn("useful-fill-low", text)
            self.assertIn("artifact-role-underfeatured", text)
            self.assertIn("missing-proof-image", text)
            self.assertIn("proof-image-rendered-too-small", text)
            self.assertIn("proof-image-upscaled-too-much", text)
            self.assertIn("proof-image-letterboxed-severe", text)
            self.assertIn("artifact-image-rendered-too-small", text)
            self.assertIn("artifact-image-upscaled-too-much", text)
            self.assertIn("artifact-image-letterboxed-severe", text)
            self.assertIn("image-object-fit-unsupported", text)
            self.assertIn("image-contract-missing", text)
            self.assertIn("image-crop-missing", text)
            self.assertIn("image-caption-source-missing", text)
            self.assertIn("rendered line-box overlap inside one text element", text)
            self.assertIn("untyped-image", text)
            self.assertIn("untyped-vector-image", text)
            self.assertIn("untyped-background-image", text)
            self.assertIn("proof-image-letterboxed", text)
            self.assertIn("cover-image-letterboxed", text)
            self.assertIn("decorative-image-too-small", text)
            self.assertIn("proof-caption-missing", text)
            self.assertIn("proof-caption-generic", text)
            self.assertIn("artifact-caption-generic", text)
            self.assertIn("caption-text-too-small", text)
            self.assertIn("caption-contrast-low", text)
            self.assertIn("label-contrast-low", text)
            self.assertIn("effectiveBackgroundColor", text)
            self.assertIn("callout-outside-source-image", text)
            self.assertIn("positionPins", text)
            self.assertIn("sourceBoxFor", text)
            self.assertIn("imageContracts", text)
            self.assertIn("visible_area", text)
            self.assertIn("data-composition", text)
            self.assertIn("data-layout-intent", text)
            self.assertIn("composition", text)
            self.assertIn('".slide > *"', text)
            self.assertIn('".proof-marginalia:not(.slide)"', text)
            self.assertIn('".artifact-showcase:not(.slide)"', text)
            self.assertIn('".content-bento:not(.slide)"', text)
            self.assertIn("pseudo-overlay-front", text)
            self.assertIn("body.grammar-gallery-proof-room .kicker", text)
            self.assertIn("body.grammar-fathom-research-brief .proof-atlas-spread .proof-notes", text)
            self.assertIn("body.grammar-ia-research-archive .proof-marginalia .proof-notes", text)
            self.assertIn("body.grammar-fathom-research-brief .artifact-dossier .artifact-visual", text)
            self.assertIn("body.grammar-fathom-research-brief .artifact-dossier .artifact-notes", text)

    @unittest.skipUnless(find_chrome(), "Chrome/Chromium is required for DOM layout integration tests.")
    def test_chrome_layout_audit_detects_forced_text_image_overlap(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "assets"
            assets.mkdir()
            Image.new("RGB", (1920, 1080), color=(235, 238, 242)).save(assets / "proof.png")
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: browser-overlap-fixture",
                        "title: Browser Overlap Fixture",
                        "visual_grammar: gallery-proof-room",
                        f"assets_dir: {assets.as_posix()}",
                        "slides:",
                        "  - kind: evidence",
                        "    title: The proof layer should not be allowed to cover text",
                        "    evidence:",
                        "      image: proof.png",
                        "      crop: {x: 0, y: 0, w: 1, h: 1}",
                        "      caption: A specific browser-overlap proof crop.",
                        "      source: fixture",
                    ]
                ),
                encoding="utf-8",
            )
            html = render_html(root / "html", load_deck(deck_path))
            text = html.read_text(encoding="utf-8")
            forced_overlap_css = """
.proof-visual {
  position: fixed !important;
  inset: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
}
"""
            html.write_text(text.replace("</style>", forced_overlap_css + "\n</style>", 1), encoding="utf-8")
            audits = audit_html_layout(html, 1, chrome_path=find_chrome())
            issue_kinds = {issue.get("type") for audit in audits for issue in audit.get("issues", [])}
            self.assertIn("text-image-overlap", issue_kinds)

    @unittest.skipUnless(find_chrome(), "Chrome/Chromium is required for DOM layout integration tests.")
    def test_chrome_layout_audit_requires_image_insertion_contract(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "assets"
            assets.mkdir()
            Image.new("RGB", (1920, 1080), color=(235, 238, 242)).save(assets / "proof.png")
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: browser-image-contract-fixture",
                        "title: Browser Image Contract Fixture",
                        "visual_grammar: gallery-proof-room",
                        f"assets_dir: {assets.as_posix()}",
                        "slides:",
                        "  - kind: evidence",
                        "    title: The proof image must carry crop, caption, and source metadata",
                        "    evidence:",
                        "      image: proof.png",
                        "      crop: {x: 0, y: 0, w: 1, h: 1}",
                        "      caption: A specific browser-contract proof crop.",
                        "      source: fixture",
                    ]
                ),
                encoding="utf-8",
            )
            html = render_html(root / "html", load_deck(deck_path))
            text = html.read_text(encoding="utf-8")
            html.write_text(text.replace("data-has-crop='true'", "data-has-crop='false'", 1), encoding="utf-8")
            audits = audit_html_layout(html, 1, chrome_path=find_chrome())
            issue_kinds = {issue.get("type") for audit in audits for issue in audit.get("issues", [])}
            self.assertIn("image-crop-missing", issue_kinds)

    @unittest.skipUnless(find_chrome(), "Chrome/Chromium is required for DOM layout integration tests.")
    def test_chrome_layout_audit_rejects_unaudited_svg_canvas_and_background_images(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "assets"
            assets.mkdir()
            Image.new("RGB", (1920, 1080), color=(235, 238, 242)).save(assets / "proof.png")
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: browser-untyped-visual-fixture",
                        "title: Browser Untyped Visual Fixture",
                        "visual_grammar: gallery-proof-room",
                        f"assets_dir: {assets.as_posix()}",
                        "slides:",
                        "  - kind: evidence",
                        "    title: Visual proof cannot be smuggled in outside audited image channels",
                        "    evidence:",
                        "      image: proof.png",
                        "      crop: {x: 0, y: 0, w: 1, h: 1}",
                        "      caption: A specific browser-contract proof crop.",
                        "      source: fixture",
                    ]
                ),
                encoding="utf-8",
            )
            html = render_html(root / "html", load_deck(deck_path))
            text = html.read_text(encoding="utf-8")
            injected = """
<div class="rogue-bg" style="position:absolute;left:4vw;top:4vh;width:12vw;height:12vh;background-image:url('proof.png')"></div>
<svg class="rogue-svg" style="position:absolute;left:18vw;top:4vh;width:8vw;height:8vh"><rect width="100%" height="100%"/></svg>
<canvas class="rogue-canvas" style="position:absolute;left:28vw;top:4vh;width:8vw;height:8vh"></canvas>
"""
            html.write_text(text.replace("</section>", injected + "\n</section>", 1), encoding="utf-8")
            audits = audit_html_layout(html, 1, chrome_path=find_chrome())
            issue_kinds = {issue.get("type") for audit in audits for issue in audit.get("issues", [])}
            self.assertIn("untyped-background-image", issue_kinds)
            self.assertIn("untyped-vector-image", issue_kinds)

    def test_visual_grammar_changes_composition_profile(self) -> None:
        deck = load_deck()
        cover = deck.slides[0]
        evidence_slide = deck.slides[3]
        self.assertEqual(composition_for(cover, "prism-dossier", 1), "cover-source-rail")
        self.assertEqual(composition_for(cover, "jetset-theory-grid", 1), "cover-poster-grid")
        self.assertEqual(composition_for(evidence_slide, "fathom-research-brief", 4), "proof-atlas-spread")
        self.assertEqual(composition_for(evidence_slide, "keynote-evidence-wall", 4), "proof-stage")
        self.assertEqual(composition_for(evidence_slide, "mono-ink-ledger", 4), "proof-atlas-spread")
        self.assertEqual(composition_for(evidence_slide, "forest-editorial-brief", 4), "proof-gallery-split")
        self.assertEqual(composition_for(evidence_slide, "cobalt-research-grid", 4), "proof-ledger")
        self.assertEqual(composition_for(cover, "prism-clean-room", 1), "cover-source-rail")
        self.assertEqual(composition_for(cover, "prism-publication-stack", 1), "cover-source-rail")
        self.assertEqual(composition_for(cover, "pentagram-gridnote", 1), "cover-poster-grid")
        self.assertEqual(composition_for(cover, "couture-exhibition", 1), "cover-title-wall")
        self.assertEqual(composition_for(cover, "huashu-editorial-lab", 1), "cover-poster-grid")
        self.assertEqual(composition_for(cover, "prism-newsroom-index", 1), "cover-source-rail")
        self.assertEqual(composition_for(cover, "huashu-build-board", 1), "cover-poster-grid")
        self.assertEqual(composition_for(cover, "gallery-proof-room", 1), "cover-title-wall")
        self.assertEqual(composition_for(cover, "broadsheet-data-room", 1), "cover-source-rail")
        self.assertEqual(composition_for(cover, "signal-intelligence-brief", 1), "cover-source-rail")
        self.assertEqual(composition_for(cover, "raw-grid-research", 1), "cover-poster-grid")
        self.assertEqual(composition_for(cover, "stencil-field-tablet", 1), "cover-poster-grid")
        self.assertEqual(composition_for(evidence_slide, "ia-research-archive", 4), "proof-marginalia")
        self.assertEqual(composition_for(evidence_slide, "takram-research-system", 4), "proof-atlas-spread")
        self.assertEqual(composition_for(evidence_slide, "stamen-data-map", 4), "proof-atlas-spread")
        self.assertEqual(composition_for(evidence_slide, "prism-publication-stack", 4), "proof-dossier")
        self.assertEqual(composition_for(evidence_slide, "couture-exhibition", 4), "proof-gallery-split")
        self.assertEqual(composition_for(evidence_slide, "huashu-editorial-lab", 4), "proof-gallery-split")
        self.assertEqual(composition_for(evidence_slide, "prism-newsroom-index", 4), "proof-dossier")
        self.assertEqual(composition_for(evidence_slide, "huashu-build-board", 4), "proof-ledger")
        self.assertEqual(composition_for(evidence_slide, "gallery-proof-room", 4), "proof-gallery-split")
        self.assertEqual(composition_for(evidence_slide, "broadsheet-data-room", 4), "proof-atlas-spread")
        self.assertEqual(composition_for(cover, "js-editorial-cascade", 1), "cover-title-wall")
        self.assertEqual(composition_for(evidence_slide, "js-editorial-cascade", 4), "proof-stage")
        self.assertEqual(composition_for(cover, "sumi-research-scroll", 1), "cover-source-rail")
        self.assertEqual(composition_for(evidence_slide, "sumi-research-scroll", 4), "proof-marginalia")
        self.assertEqual(composition_for(evidence_slide, "signal-intelligence-brief", 4), "proof-atlas-spread")
        self.assertEqual(composition_for(evidence_slide, "raw-grid-research", 4), "proof-ledger")
        self.assertEqual(composition_for(evidence_slide, "stencil-field-tablet", 4), "proof-ledger")
        explicit = type(evidence_slide)(**{**evidence_slide.__dict__, "layout": "proof-dominant"})
        self.assertEqual(composition_for(explicit, "fathom-research-brief", 4), "proof-atlas-spread")
        explicit_artifact = type(cover)(**{**cover.__dict__, "kind": "stack", "layout": "artifact-showcase"})
        self.assertEqual(composition_for(explicit_artifact, "atlas-marginalia", 2), "artifact-marginalia")
        self.assertEqual(composition_for(explicit_artifact, "forest-editorial-brief", 2), "artifact-showcase")

    def test_layout_intent_round_trips_and_quality_checks_invalid_values(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: layout-test",
                        "title: Layout Test",
                        "slides:",
                        "  - kind: evidence",
                        "    kicker: Proof",
                        "    title: A requested layout should survive parsing",
                        "    layout: proof-dominant",
                        "    image: proof.png",
                        "  - kind: stack",
                        "    kicker: Bad",
                        "    title: Invalid layout names should fail early",
                        "    layout: made-up-layout",
                    ]
                ),
                encoding="utf-8",
            )
            deck = load_deck(deck_path)
            self.assertEqual(deck.slides[0].layout, "proof-dominant")
            messages = [issue.message for issue in check_deck(deck) if issue.level == "error"]
            self.assertTrue(any("Unsupported layout intent" in message for message in messages))
            self.assertTrue(any("Missing image asset" in message for message in messages))

    def test_quality_enforces_text_and_image_safety_budgets(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "assets"
            assets.mkdir()
            Image.new("RGB", (500, 260), color=(240, 240, 240)).save(assets / "tiny-proof.png")
            Image.new("RGB", (900, 560), color=(230, 230, 230)).save(assets / "bare-proof.png")
            deck_path = root / "deck.yaml"
            long_title = " ".join(["This title keeps adding claims until it is no longer safe for a fixed slide canvas"] * 3)
            long_bullet = " ".join(["dense implementation detail"] * 80)
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: safety-budget-test",
                        "title: Safety Budget Test",
                        f"assets_dir: {assets.as_posix()}",
                        "slides:",
                        "  - kind: evidence",
                        "    kicker: Proof",
                        f"    title: {long_title}",
                        "    layout: proof-showcase",
                        "    image: tiny-proof.png",
                        "    bullets:",
                        f"      - {long_bullet}",
                        "    evidence:",
                        "      image: tiny-proof.png",
                        "      caption: tiny proof",
                        "      source: fixture",
                        "  - kind: evidence",
                        "    kicker: Proof",
                        "    title: Bare proof image should fail before render",
                        "    image: bare-proof.png",
                    ]
                ),
                encoding="utf-8",
            )
            deck = load_deck(deck_path)
            messages = [issue.message for issue in check_deck(deck) if issue.level == "error"]
            self.assertTrue(any("Title is too long" in message for message in messages))
            self.assertTrue(any("A bullet is too long" in message for message in messages))
            self.assertTrue(any("Evidence image is only 500x260px" in message for message in messages))
            self.assertTrue(any("Proof/evidence images must use an `evidence:` block" in message for message in messages))
            self.assertTrue(any("must declare `evidence.crop`" in message for message in messages))

    def test_quality_rejects_overloaded_image_slides(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "assets"
            assets.mkdir()
            Image.new("RGB", (1600, 1000), color=(240, 240, 240)).save(assets / "proof.png")
            Image.new("RGB", (1500, 900), color=(235, 235, 235)).save(assets / "artifact.png")
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                yaml.safe_dump(
                    {
                        "deck_id": "image-module-budget-test",
                        "title": "Image Module Budget Test",
                        "assets_dir": assets.as_posix(),
                        "slides": [
                            {
                                "kind": "evidence",
                                "title": "A proof slide cannot carry every supporting module at once",
                                "layout": "proof-showcase",
                                "image": "proof.png",
                                "bullets": ["claim one", "claim two", "claim three"],
                                "metrics": [
                                    {"value": "1", "label": "first anchor"},
                                    {"value": "2", "label": "second anchor"},
                                    {"value": "3", "label": "third anchor"},
                                ],
                                "evidence": {
                                    "image": "proof.png",
                                    "crop": {"x": 0, "y": 0, "w": 1, "h": 1},
                                    "caption": "Specific proof crop.",
                                    "source": "fixture source",
                                },
                            },
                            {
                                "kind": "split",
                                "title": "An artifact panel needs text budget too",
                                "layout": "artifact-showcase",
                                "bullets": ["point one", "point two", "point three"],
                                "metrics": [
                                    {"value": "A", "label": "first anchor"},
                                    {"value": "B", "label": "second anchor"},
                                ],
                                "labels": ["source", "method", "result"],
                                "image": "artifact.png",
                                "evidence": {
                                    "image": "artifact.png",
                                    "crop": {"x": 0, "y": 0, "w": 1, "h": 1},
                                    "caption": "Specific artifact crop.",
                                    "source": "fixture source",
                                },
                            },
                        ],
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            messages = [issue.message for issue in check_deck(load_deck(deck_path)) if issue.level == "error"]
            self.assertTrue(any("Proof slides with images must use at most two metrics" in message for message in messages))
            self.assertTrue(any("Image-backed proof slide combines too many text modules" in message for message in messages))
            self.assertTrue(any("Image-backed content slide combines too many modules" in message for message in messages))

    def test_quality_counts_cjk_text_without_spaces(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            deck_path = root / "deck.yaml"
            long_title = "这个研究结论说明模型行为需要证据约束和版面约束" * 12
            long_bullet = "训练过程中的奖励信号稀疏会让搜索行为被错误强化所以需要分阶段信号和严格证据闭环" * 14
            deck_path.write_text(
                yaml.safe_dump(
                    {
                        "deck_id": "cjk-budget-test",
                        "title": "CJK Budget Test",
                        "slides": [
                            {
                                "kind": "thesis",
                                "title": long_title,
                                "bullets": [long_bullet],
                            }
                        ],
                    },
                    sort_keys=False,
                    allow_unicode=True,
                ),
                encoding="utf-8",
            )
            messages = [issue.message for issue in check_deck(load_deck(deck_path)) if issue.level == "error"]
            self.assertTrue(any("Title is too long" in message for message in messages))
            self.assertTrue(any("A bullet is too long" in message for message in messages))

    def test_quality_rejects_bare_content_images(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "assets"
            assets.mkdir()
            Image.new("RGB", (1280, 720), color=(240, 240, 240)).save(assets / "artifact.png")
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: bare-content-image-test",
                        "title: Bare Content Image Test",
                        f"assets_dir: {assets.as_posix()}",
                        "slides:",
                        "  - kind: split",
                        "    title: A content screenshot needs a caption and source contract",
                        "    image: artifact.png",
                    ]
                ),
                encoding="utf-8",
            )
            messages = [issue.message for issue in check_deck(load_deck(deck_path)) if issue.level == "error"]
            self.assertTrue(any("Image-backed content must use an `evidence:` block" in message for message in messages))

    def test_quality_requires_non_cover_images_to_use_evidence_source(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "assets"
            assets.mkdir()
            Image.new("RGB", (1280, 720), color=(240, 240, 240)).save(assets / "artifact-a.png")
            Image.new("RGB", (1280, 720), color=(230, 230, 230)).save(assets / "artifact-b.png")
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: image-contract-test",
                        "title: Image Contract Test",
                        f"assets_dir: {assets.as_posix()}",
                        "slides:",
                        "  - kind: split",
                        "    title: A source panel cannot rely on the top-level image fallback",
                        "    image: artifact-a.png",
                        "    evidence:",
                        "      crop: {x: 0, y: 0, w: 1, h: 1}",
                        "      caption: A specific artifact crop.",
                        "      source: fixture",
                        "  - kind: evidence",
                        "    title: The crop contract must target the rendered source",
                        "    image: artifact-a.png",
                        "    evidence:",
                        "      image: artifact-b.png",
                        "      crop: {x: 0, y: 0, w: 1, h: 1}",
                        "      caption: A specific proof crop.",
                        "      source: fixture",
                    ]
                ),
                encoding="utf-8",
            )
            messages = [issue.message for issue in check_deck(load_deck(deck_path)) if issue.level == "error"]
            self.assertTrue(any("must be declared as `evidence.image`" in message for message in messages))
            self.assertTrue(any("point to different files" in message for message in messages))

    def test_quality_rejects_full_frame_source_heavy_crop_with_bad_slot_shape(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "assets"
            assets.mkdir()
            Image.new("RGB", (900, 1800), color=(240, 240, 240)).save(assets / "homepage-screenshot.png")
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: full-frame-source-heavy-crop-test",
                        "title: Full Frame Source Heavy Crop Test",
                        f"assets_dir: {assets.as_posix()}",
                        "slides:",
                        "  - kind: evidence",
                        "    title: A long homepage screenshot needs a real crop before insertion",
                        "    evidence:",
                        "      image: homepage-screenshot.png",
                        "      crop: {x: 0, y: 0, w: 1, h: 1}",
                        "      caption: Homepage screenshot showing project page and publication table.",
                        "      source: https://example.com/profile",
                    ]
                ),
                encoding="utf-8",
            )
            messages = [issue.message for issue in check_deck(load_deck(deck_path)) if issue.level == "error"]
            self.assertTrue(any("Source-heavy evidence uses an almost full-frame" in message for message in messages))

    def test_quality_rejects_tiny_source_heavy_crops_before_render(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "assets"
            assets.mkdir()
            Image.new("RGB", (760, 430), color=(240, 240, 240)).save(assets / "benchmark-table.png")
            Image.new("RGB", (780, 440), color=(235, 235, 235)).save(assets / "repo-screenshot.png")
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                yaml.safe_dump(
                    {
                        "deck_id": "source-heavy-size-test",
                        "title": "Source Heavy Size Test",
                        "assets_dir": assets.as_posix(),
                        "slides": [
                            {
                                "kind": "evidence",
                                "title": "A benchmark table crop must be readable before insertion",
                                "evidence": {
                                    "image": "benchmark-table.png",
                                    "crop": {"x": 0, "y": 0, "w": 1, "h": 1},
                                    "caption": "Benchmark table showing the reported accuracy.",
                                    "source": "paper table",
                                },
                            },
                            {
                                "kind": "split",
                                "title": "A repository screenshot must not become a tiny artifact",
                                "evidence": {
                                    "image": "repo-screenshot.png",
                                    "crop": {"x": 0, "y": 0, "w": 1, "h": 1},
                                    "caption": "GitHub repository screenshot showing implementation scope.",
                                    "source": "GitHub repo",
                                },
                            },
                        ],
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            messages = [issue.message for issue in check_deck(load_deck(deck_path)) if issue.level == "error"]
            self.assertTrue(any("Source-heavy evidence crop is only 760x430px" in message for message in messages))
            self.assertTrue(any("Source-heavy artifact crop is only 780x440px" in message for message in messages))

    def test_strict_html_export_cannot_skip_layout_audit(self) -> None:
        with TemporaryDirectory() as tmp:
            with self.assertRaises(SystemExit) as raised:
                html_pptx_only(
                    None,
                    tmp,
                    width=1920,
                    height=1080,
                    chrome=None,
                    fail_on_layout=True,
                    skip_layout_audit=True,
            )
            self.assertIn("cannot be combined", str(raised.exception))

    def test_delivery_blocker_renames_failed_strict_artifacts(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            pptx = root / "candidate.pptx"
            pdf = root / "candidate.pdf"
            pptx.write_bytes(b"pptx")
            pdf.write_bytes(b"pdf")
            marker = mark_delivery_blocked(root, "Layout audit failed with 2 blocking issue(s).", (pptx, pdf))
            text = marker.read_text(encoding="utf-8")
            self.assertTrue(marker.exists())
            self.assertFalse(pptx.exists())
            self.assertFalse(pdf.exists())
            self.assertTrue((root / "candidate.blocked.pptx").exists())
            self.assertTrue((root / "candidate.blocked.pdf").exists())
            self.assertIn("review artifacts, not deliverables", text)

    def test_quality_accepts_source_urls_for_image_context(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "assets"
            assets.mkdir()
            Image.new("RGB", (1280, 720), color=(240, 240, 240)).save(assets / "leaderboard.png")
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: source-url-test",
                        "title: Source URL Test",
                        f"assets_dir: {assets.as_posix()}",
                        "slides:",
                        "  - kind: evidence",
                        "    kicker: Proof",
                        "    title: A URL ending in HTML is still a specific source",
                        "    image: leaderboard.png",
                        "    evidence:",
                        "      image: leaderboard.png",
                        "      crop: {x: 0, y: 0, w: 1, h: 1}",
                        "      caption: BFCL leaderboard crop showing task categories and comparative scores.",
                        "      source: https://gorilla.cs.berkeley.edu/leaderboard.html",
                    ]
                ),
                encoding="utf-8",
            )
            messages = [issue.message for issue in check_deck(load_deck(deck_path))]
            self.assertFalse(any("caption/source is too generic" in message for message in messages))

    def test_quality_rejects_empty_visual_modules(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: empty-module-test",
                        "title: Empty Module Test",
                        "slides:",
                        "  - kind: thesis",
                        "    kicker: Empty",
                        "    title: Empty boxes should not survive quality checks",
                        "    bullets:",
                        "      - \"\"",
                        "    labels:",
                        "      - \"\"",
                        "    metrics:",
                        "      - [\"\", \"anchor\"]",
                    ]
                ),
                encoding="utf-8",
            )
            deck = load_deck(deck_path)
            messages = [issue.message for issue in check_deck(deck) if issue.level == "error"]
            self.assertTrue(any("Empty bullet" in message for message in messages))
            self.assertTrue(any("Metric cells need both" in message for message in messages))
            self.assertTrue(any("Empty labels" in message for message in messages))

    def test_quality_rejects_content_that_renderer_would_truncate(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: truncation-test",
                        "title: Truncation Test",
                        "slides:",
                        "  - kind: thesis",
                        "    title: Silent truncation should fail quality checks",
                        "    bullets: [one, two, three, four, five]",
                        "    metrics:",
                        "      - {value: '1', label: one}",
                        "      - {value: '2', label: two}",
                        "      - {value: '3', label: three}",
                        "      - {value: '4', label: four}",
                        "      - {value: '5', label: five}",
                        "    labels: [a, b, c, d, e, f]",
                    ]
                ),
                encoding="utf-8",
            )
            messages = [issue.message for issue in check_deck(load_deck(deck_path)) if issue.level == "error"]
            self.assertTrue(any("renderer shows at most 4" in message for message in messages))
            self.assertTrue(any("renderer shows at most four" in message for message in messages))
            self.assertTrue(any("renderer shows at most five" in message for message in messages))

    def test_compare_grammar_list_defaults_and_normalizes(self) -> None:
        self.assertEqual(parse_grammar_list(None), DEFAULT_COMPARE_GRAMMARS)
        self.assertEqual(len(DEFAULT_COMPARE_GRAMMARS), 42)
        self.assertEqual(parse_grammar_list("highsense-20"), HIGHSENSE_20_GRAMMARS)
        self.assertEqual(parse_grammar_list("reference_20"), HIGHSENSE_20_GRAMMARS)
        self.assertEqual(len(HIGHSENSE_20_GRAMMARS), 20)
        self.assertEqual(len(set(HIGHSENSE_20_GRAMMARS)), 20)
        self.assertTrue(set(HIGHSENSE_20_GRAMMARS).issubset(VISUAL_GRAMMARS))
        self.assertEqual(
            parse_grammar_list("Prism_Dossier, fathom-research-brief, "),
            ("prism-dossier", "fathom-research-brief"),
        )

    def test_beautiful_template_shortlist_prefers_research_safe_templates(self) -> None:
        candidates = beautiful_template_candidates(
            "academic research profile with evidence, source links, technical benchmark, quiet high taste",
            limit=5,
        )
        slugs = [candidate.slug for candidate in candidates]
        self.assertIn("signal", slugs[:3])
        self.assertTrue({"raw-grid", "cobalt-grid", "vellum"} & set(slugs))
        self.assertGreaterEqual(candidates[0].score, candidates[-1].score)

    def test_beautiful_template_shortlist_has_public_fallback(self) -> None:
        with TemporaryDirectory() as tmp:
            missing_index = Path(tmp) / "missing" / "index.json"
            candidates = beautiful_template_candidates(
                "formal academic evidence review",
                limit=3,
                index_path=missing_index,
            )
        self.assertEqual(len(candidates), 3)
        self.assertIn("signal", {candidate.slug for candidate in candidates})

    def test_schema_visual_grammar_enum_matches_renderer(self) -> None:
        schema = json.loads((ROOT / "schema" / "deck.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(set(schema["properties"]["visual_grammar"]["enum"]), VISUAL_GRAMMARS)
        slide_schema = schema["$defs"]["slide"]["properties"]
        self.assertEqual(set(slide_schema["layout"]["enum"]), KNOWN_LAYOUT_INTENTS)
        self.assertEqual(schema["$defs"]["evidence"]["required"], ["image", "crop", "caption", "source"])
        self.assertEqual(schema["$defs"]["evidence"]["properties"]["image"]["type"], "string")
        self.assertEqual(schema["$defs"]["evidence"]["properties"]["callouts"]["maxItems"], 3)

    def test_prism_workbench_index_renders_distinct_content_composition(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: workbench-fixture",
                        "title: Workbench Fixture",
                        "visual_grammar: prism-workbench-index",
                        "slides:",
                        "  - kind: cover",
                        "    title: Selected works as a research workbench",
                        "    labels: [identity, papers, systems]",
                        "    metrics:",
                        "      - {value: '3', label: threads}",
                        "  - kind: thesis",
                        "    kicker: Index",
                        "    title: The ordinary content page should not look like another card grid",
                        "    bullets:",
                        "      - Keep the claim column compact.",
                        "      - Use selected-work rows on the right.",
                        "    labels:",
                        "      - First selected paper",
                        "      - Tool-use benchmark",
                        "      - Public project artifact",
                    ]
                ),
                encoding="utf-8",
            )
            html = render_html(root / "html", load_deck(deck_path))
            text = html.read_text(encoding="utf-8")
            self.assertIn('data-visual-grammar="prism-workbench-index"', text)
            self.assertIn('data-composition="content-workbench-index"', text)
            self.assertIn(".content-workbench-index:not(.slide)", text)

    def test_renderer_rejects_unknown_visual_grammar_directly(self) -> None:
        deck = load_deck()
        bad = type(deck)(
            deck_id=deck.deck_id,
            title=deck.title,
            subtitle=deck.subtitle,
            slides=deck.slides,
            visual_grammar="typo-grammar",
            footer=deck.footer,
            contact=deck.contact,
            assets_dir=deck.assets_dir,
            base_dir=deck.base_dir,
        )
        with TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                render_html(Path(tmp), bad)

    def test_non_strict_html_export_stops_on_quality_errors(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "assets"
            assets.mkdir()
            Image.new("RGB", (1200, 760), color=(245, 245, 245)).save(assets / "artifact.png")
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: invalid-image-contract",
                        "title: Invalid Image Contract",
                        f"assets_dir: {assets.as_posix()}",
                        "slides:",
                        "  - kind: split",
                        "    title: Bare non-cover images stop before export",
                        "    image: artifact.png",
                    ]
                ),
                encoding="utf-8",
            )
            with self.assertRaises(SystemExit) as raised:
                html_pptx_only(
                    str(deck_path),
                    str(root / "out"),
                    width=1920,
                    height=1080,
                    chrome=None,
                    fail_on_layout=False,
                    skip_layout_audit=True,
                )
            self.assertIn("Quality check failed", str(raised.exception))

    def test_cover_evidence_contract_controls_rendered_cover_image(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "assets"
            assets.mkdir()
            Image.new("RGB", (900, 900), color=(10, 10, 10)).save(assets / "identity.png")
            Image.new("RGB", (1600, 900), color=(240, 240, 240)).save(assets / "proof.png")
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: cover-contract",
                        "title: Cover Contract",
                        f"assets_dir: {assets.as_posix()}",
                        "slides:",
                        "  - kind: cover",
                        "    title: Cover evidence must be one source",
                        "    image: identity.png",
                        "    evidence:",
                        "      image: proof.png",
                        "      crop: {x: 0, y: 0, w: 1, h: 1}",
                        "      caption: A cover proof crop.",
                        "      source: fixture",
                    ]
                ),
                encoding="utf-8",
            )
            deck = load_deck(deck_path)
            messages = [issue.message for issue in check_deck(deck) if issue.level == "error"]
            self.assertTrue(any("Cover `image` and `evidence.image` point to different files" in message for message in messages))

            fixed_path = root / "fixed.yaml"
            fixed_path.write_text(deck_path.read_text(encoding="utf-8").replace("image: identity.png", "image: proof.png"), encoding="utf-8")
            html = render_html(root / "html", load_deck(fixed_path)).read_text(encoding="utf-8")
            self.assertIn("A cover proof crop.", html)
            self.assertIn("fixture", html)

    def test_too_many_callouts_are_quality_errors(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "assets"
            assets.mkdir()
            Image.new("RGB", (1400, 900), color=(245, 245, 245)).save(assets / "proof.png")
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: callout-limit",
                        "title: Callout Limit",
                        f"assets_dir: {assets.as_posix()}",
                        "slides:",
                        "  - kind: evidence",
                        "    title: Extra pins cannot disappear silently",
                        "    evidence:",
                        "      image: proof.png",
                        "      crop: {x: 0, y: 0, w: 1, h: 1}",
                        "      caption: A specific proof crop.",
                        "      source: fixture",
                        "      callouts:",
                        "        - {x: 0.2, y: 0.2, text: one}",
                        "        - {x: 0.4, y: 0.2, text: two}",
                        "        - {x: 0.6, y: 0.2, text: three}",
                        "        - {x: 0.8, y: 0.2, text: four}",
                    ]
                ),
                encoding="utf-8",
            )
            messages = [issue.message for issue in check_deck(load_deck(deck_path)) if issue.level == "error"]
            self.assertTrue(any("More than three callouts" in message for message in messages))

    def test_layout_report_exposes_image_contracts_and_wrap_gates(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report_path, blocking = write_layout_audit_report(
                root / "layout-audit-report.md",
                (
                    {
                        "slide": 1,
                        "composition": "proof-ledger",
                        "metrics": {"content_fill": 0.52, "useful_fill": 0.36},
                        "images": [
                            {
                                "role": "proof",
                                "target": "img@.proof-visual",
                                "rendered_width": 1120,
                                "rendered_height": 640,
                                "visible_area": 0.34,
                                "slot_use": 0.72,
                                "has_crop": True,
                                "has_caption": True,
                                "has_source": True,
                            }
                        ],
                        "issues": [
                            {
                                "level": "warn",
                                "type": "title-wrap-deep",
                                "target": "h2",
                                "detail": "4 rendered title lines; shorten action title or split the slide",
                            }
                        ],
                    },
                    {
                        "slide": 2,
                        "composition": "content-label-board",
                        "metrics": {"content_fill": 0.48, "useful_fill": 0.31},
                        "issues": [
                            {
                                "level": "error",
                                "type": "subtitle-wrap-too-deep",
                                "target": "p.subtitle",
                                "detail": "8 rendered subtitle lines; maximum 7 before layout becomes unsafe",
                            }
                        ],
                    },
                ),
            )
            text = report_path.read_text(encoding="utf-8")
            self.assertEqual(blocking, 1)
            self.assertIn("## Image Contracts", text)
            self.assertIn("| 1 | `proof` | 1120x640 | 34.0% | 72.0% | yes | yes | yes | yes | `img@.proof-visual` |", text)
            self.assertIn("title-wrap-deep", text)
            self.assertIn("subtitle-wrap-too-deep", text)
            self.assertEqual(
                strict_warning_count(
                    (
                        {
                            "slide": 1,
                            "issues": [
                                {
                                    "level": "warn",
                                    "type": "title-wrap-deep",
                                    "target": "h2",
                                    "detail": "4 rendered title lines",
                                }
                            ],
                        },
                    )
                ),
                1,
            )

    def test_layout_report_summary_scores_image_warnings(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = root / "layout-audit-report.md"
            report.write_text(
                "\n".join(
                    [
                        "# HTML Layout Audit",
                        "",
                        "- Slides audited: 6",
                        "- Blocking errors: 0",
                        "- Warnings: 5",
                        "- Average content fill: 56.7%",
                        "- Average useful fill: 31.2%",
                        "",
                        "## Deck Cadence",
                        "- Composition sequence: `cover-title-card -> proof-atlas-spread`",
                        "- Distinct cadences: 4 (cover-title-card, proof-atlas-spread)",
                        "",
                        "## Issues",
                        "- `warn` `decorative-image-too-small` on `img@.cover-art`: 3% visible slide area",
                        "- `warn` `proof-image-small` on `img@.proof-visual`: 27% visible slide area",
                        "- `warn` `proof-image-rendered-small` on `img@.proof-visual`: 940x520 rendered source pixels",
                        "- `warn` `proof-image-small` on `img@.proof-visual`: 27% visible slide area",
                        "- `warn` `artifact-small` on `.artifact-panel`: 22% slide area",
                    ]
                ),
                encoding="utf-8",
            )
            summary = layout_report_summary(report)
            self.assertEqual(summary.warnings, 5)
            self.assertEqual(dict(summary.warning_counts)["proof-image-small"], 2)
            self.assertEqual(dict(summary.warning_counts)["proof-image-rendered-small"], 1)
            self.assertEqual(summary.average_fill, "56.7%")
            self.assertEqual(summary.average_useful_fill, "31.2%")
            self.assertEqual(summary.sequence, "cover-title-card -> proof-atlas-spread")
            self.assertLess(score_grammar_variant("paper-atlas", summary), 80)
            row = compare_row("paper-atlas", root, 0, report)
            self.assertEqual(row.recommendation, "revise image scale/crop")

            decorative_report = root / "decorative.md"
            decorative_report.write_text(
                "\n".join(
                    [
                        "- Blocking errors: 0",
                        "- Warnings: 1",
                        "- Average content fill: 65.0%",
                        "- Average useful fill: 44.0%",
                        "- Composition sequence: `cover-title-wall -> proof-gallery-split`",
                        "- Distinct cadences: 4",
                        "- `warn` `decorative-image-too-small` on `img@.cover-art`: 3% visible slide area",
                    ]
                ),
                encoding="utf-8",
            )
            decorative_summary = layout_report_summary(decorative_report)
            self.assertLess(score_grammar_variant("evidence-atelier", decorative_summary), 100)

    def test_recommended_rows_prefers_zero_error_distinct_sequences(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            clean_report = root / "clean.md"
            clean_report.write_text(
                "\n".join(
                    [
                        "- Blocking errors: 0",
                        "- Warnings: 0",
                        "- Average content fill: 64.0%",
                        "- Average useful fill: 41.0%",
                        "- Composition sequence: `cover-source-rail -> proof-gallery-split`",
                        "- Distinct cadences: 4",
                    ]
                ),
                encoding="utf-8",
            )
            repeat_report = root / "repeat.md"
            repeat_report.write_text(clean_report.read_text(encoding="utf-8"), encoding="utf-8")
            proof_small_report = root / "proof-small.md"
            proof_small_report.write_text(
                "\n".join(
                    [
                        "- Blocking errors: 0",
                        "- Warnings: 2",
                        "- Average content fill: 60.0%",
                        "- Average useful fill: 28.0%",
                        "- Composition sequence: `cover-title-card -> proof-atlas-spread`",
                        "- Distinct cadences: 4",
                        "- `warn` `proof-image-small` on `img@.proof-visual`: 27% visible slide area",
                        "- `warn` `proof-image-small` on `img@.proof-visual`: 27% visible slide area",
                    ]
                ),
                encoding="utf-8",
            )
            blocked_report = root / "blocked.md"
            blocked_report.write_text(
                "\n".join(
                    [
                        "- Blocking errors: 1",
                        "- Warnings: 0",
                        "- Average content fill: 60.0%",
                        "- Average useful fill: 39.0%",
                        "- Composition sequence: `cover-poster-grid -> proof-ledger`",
                        "- Distinct cadences: 4",
                    ]
                ),
                encoding="utf-8",
            )
            rows = [
                compare_row("object-study-wall", root / "object", 0, clean_report),
                compare_row("forest-editorial-brief", root / "forest", 0, repeat_report),
                compare_row("paper-atlas", root / "paper", 0, proof_small_report),
                compare_row("neo-grid-lab", root / "neo", 1, blocked_report),
            ]
            shortlist = recommended_rows(rows, limit=3)
            self.assertEqual(shortlist[0].grammar, "object-study-wall")
            self.assertNotIn("neo-grid-lab", [row.grammar for row in shortlist])
            self.assertNotIn("paper-atlas", [row.grammar for row in shortlist])
            revisions = revision_rows(rows, limit=3)
            self.assertEqual(revisions[0].grammar, "paper-atlas")

    def test_recommended_rows_diversifies_style_families(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            def report(name: str, sequence: str) -> Path:
                path = root / f"{name}.md"
                path.write_text(
                    "\n".join(
                        [
                            "- Blocking errors: 0",
                            "- Warnings: 0",
                            "- Average content fill: 62.0%",
                            f"- Composition sequence: `{sequence}`",
                            "- Distinct cadences: 4",
                        ]
                    ),
                    encoding="utf-8",
                )
                return path

            rows = [
                compare_row("prism-clean-room", root / "prism-clean", 0, report("prism-clean", "cover-source-rail -> proof-dossier")),
                compare_row("prism-newsroom-index", root / "prism-news", 0, report("prism-news", "cover-source-rail -> artifact-dossier -> proof-dossier")),
                compare_row("object-study-wall", root / "object", 0, report("object", "cover-title-wall -> proof-gallery-split")),
                compare_row("systems-field-manual", root / "systems", 0, report("systems", "cover-poster-grid -> proof-ledger")),
            ]
            shortlist = recommended_rows(rows, limit=3)
            families = [grammar_style_family(row.grammar) for row in shortlist]
            self.assertEqual(len(families), len(set(families)))
            self.assertLessEqual(sum(1 for family in families if family == "academic-homepage"), 1)
            self.assertIn("proof-gallery", composition_family_signature(rows[2].sequence))

    def test_design_direction_report_exposes_twenty_plus_schools(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            def report(name: str, sequence: str) -> Path:
                path = root / f"{name}.md"
                path.write_text(
                    "\n".join(
                        [
                            "- Blocking errors: 0",
                            "- Warnings: 0",
                            "- Average content fill: 64.0%",
                            f"- Composition sequence: `{sequence}`",
                            "- Distinct cadences: 4",
                        ]
                    ),
                    encoding="utf-8",
                )
                return path

            rows = [
                compare_row("prism-workbench-index", root / "prism", 0, report("prism", "cover-source-rail -> content-workbench-index -> proof-dossier")),
                compare_row("gallery-proof-room", root / "gallery", 0, report("gallery", "cover-title-wall -> proof-gallery-split -> artifact-showcase")),
                compare_row("huashu-issue-broadsheet", root / "huashu", 0, report("huashu", "cover-poster-grid -> proof-ledger -> matrix-ledger")),
            ]
            out = write_design_direction_report(rows, root / "DESIGN_DIRECTIONS.md", load_deck())
            text = out.read_text(encoding="utf-8")
            self.assertGreaterEqual(direction_count(), 20)
            self.assertGreaterEqual(len(DESIGN_DIRECTIONS), 20)
            self.assertIsNotNone(direction_for_grammar("prism-workbench-index"))
            self.assertIn("# Design Directions", text)
            self.assertIn("20+ Direction Library", text)
            self.assertIn("JS Design", text)
            self.assertIn("PRISM", text)
            self.assertIn("Huashu", text)
            self.assertIn("5D Critique", text)
            self.assertIn("prism-workbench-index", text)
            self.assertIn("gallery-proof-room", text)
            self.assertIn("huashu-issue-broadsheet", text)
            self.assertIn("Gallery Proof Room", text)
            self.assertIn("Huashu Issue Broadsheet", text)
            self.assertIn("Related schools", text)
            gallery_directions = directions_for_grammar("gallery-proof-room")
            self.assertGreaterEqual(len(gallery_directions), 2)
            self.assertIn("Exhibition editorial", {direction.school for direction in gallery_directions})

    def test_repair_hints_map_audit_warnings_to_source_slides(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "assets"
            assets.mkdir()
            Image.new("RGB", (1200, 700), color=(240, 240, 240)).save(assets / "proof.png")
            Image.new("RGB", (900, 600), color=(245, 245, 245)).save(assets / "cover.png")
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: repair-hint-test",
                        "title: Repair Hint Test",
                        f"assets_dir: {assets.as_posix()}",
                        "slides:",
                        "  - kind: cover",
                        "    title: Cover uses a tiny identity crop",
                        "    image: cover.png",
                        "  - kind: evidence",
                        "    title: Proof should dominate the slide",
                        "    layout: proof-showcase",
                        "    image: proof.png",
                        "    evidence:",
                        "      image: proof.png",
                        "      crop:",
                        "        x: 0.10",
                        "        y: 0.20",
                        "        w: 0.70",
                        "        h: 0.40",
                        "      caption: proof crop",
                        "      source: fixture",
                    ]
                ),
                encoding="utf-8",
            )
            report = root / "layout-audit-report.md"
            report.write_text(
                "\n".join(
                    [
                        "# HTML Layout Audit",
                        "",
                        "## Issues",
                        "### Slide 1 / fill 40%",
                        "- `warn` `decorative-image-too-small` on `img@.cover-art`: 3% visible slide area",
                        "### Slide 2 / fill 66%",
                        "- `warn` `proof-image-small` on `img@.proof-visual`: 27% visible slide area",
                    ]
                ),
                encoding="utf-8",
            )
            hints = repair_hints_for_report(load_deck(deck_path), report)
            joined = "\n".join(hints)
            self.assertIn("Slide 1 `Cover uses a tiny identity crop`", joined)
            self.assertIn("Slide 2 `Proof should dominate the slide`", joined)
            self.assertIn("already requests `layout: proof-showcase`", joined)
            self.assertIn("`proof.png`", joined)
            self.assertIn("crop x=0.10", joined)

    def test_repair_manifest_is_machine_readable(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = root / "layout-audit-report.md"
            report.write_text(
                "\n".join(
                    [
                        "- Blocking errors: 0",
                        "- Warnings: 1",
                        "- Average content fill: 62.0%",
                        "- Average useful fill: 37.0%",
                        "- Composition sequence: `cover -> proof`",
                        "- Distinct cadences: 2",
                        "- `warn` `proof-image-small` on `img@.proof-visual`: 27% visible slide area",
                    ]
                ),
                encoding="utf-8",
            )
            row = compare_row("paper-atlas", root / "paper-atlas", 0, report)
            manifest = write_repair_manifest([row], root / "GRAMMAR_REPAIR_HINTS.json")
            data = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(data["variants"][0]["grammar"], "paper-atlas")
            self.assertEqual(data["variants"][0]["warnings"]["proof-image-small"], 1)
            self.assertEqual(data["variants"][0]["average_useful_fill"], "37.0%")
            self.assertIn("repair_hints", data["variants"][0])
            self.assertIn("repair_actions", data["variants"][0])

            plan = write_deck_repair_plan(manifest, root / "DECK_REPAIR_PLAN.md")
            plan_text = plan.read_text(encoding="utf-8")
            self.assertIn("Deck Repair Plan", plan_text)
            self.assertIn("paper-atlas", plan_text)
            self.assertIn("proof-image-small", plan_text)

    def test_repair_draft_writes_non_destructive_candidate_deck(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "assets"
            assets.mkdir()
            Image.new("RGB", (1400, 900), color=(245, 245, 245)).save(assets / "proof.png")
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: repair-draft-test",
                        "title: Repair Draft Test",
                        "visual_grammar: paper-atlas",
                        "assets_dir: assets",
                        "slides:",
                        "  - kind: evidence",
                        "    title: Proof crop should be tightened without touching the source deck",
                        "    layout: proof-showcase",
                        "    image: proof.png",
                        "    evidence:",
                        "      image: proof.png",
                        "      crop:",
                        "        x: 0.10",
                        "        y: 0.10",
                        "        w: 0.80",
                        "        h: 0.70",
                        "      caption: proof crop",
                        "      source: fixture",
                    ]
                ),
                encoding="utf-8",
            )
            original = deck_path.read_text(encoding="utf-8")
            manifest = root / "GRAMMAR_REPAIR_HINTS.json"
            manifest.write_text(
                json.dumps(
                    {
                        "variants": [
                            {
                                "grammar": "academic-homepage-grid",
                                "score": 91,
                                "recommendation": "revise image scale/crop",
                                "blocking_errors": 0,
                                "warnings": {"proof-image-small": 1},
                                "repair_actions": [
                                    {
                                        "slide": 1,
                                        "slide_title": "Proof crop should be tightened without touching the source deck",
                                        "issue_kind": "proof-image-small",
                                        "level": "warn",
                                        "target": "img@.proof-visual",
                                        "detail": "27% visible slide area",
                                        "current_layout": "proof-showcase",
                                        "current_image": "proof.png",
                                        "current_crop": {"x": 0.1, "y": 0.1, "w": 0.8, "h": 0.7},
                                        "suggested_action": "tighten-crop",
                                        "suggested_layout": "proof-showcase",
                                        "crop_strategy": "tighten around one readable proof object",
                                        "content_strategy": "replace weak source if crop still reads small",
                                        "hint": "tighten crop",
                                    }
                                ],
                            }
                        ]
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            draft, report = write_repair_draft(deck_path, manifest, root / "draft", "academic-homepage-grid")
            draft_data = yaml.safe_load(draft.read_text(encoding="utf-8"))
            crop = draft_data["slides"][0]["evidence"]["crop"]
            self.assertEqual(deck_path.read_text(encoding="utf-8"), original)
            self.assertEqual(draft_data["visual_grammar"], "academic-homepage-grid")
            self.assertEqual(draft_data["assets_dir"], assets.resolve().as_posix())
            self.assertEqual(draft_data["slides"][0]["layout"], "proof-showcase")
            self.assertLess(crop["w"], 0.8)
            self.assertLess(crop["h"], 0.7)
            self.assertGreater(crop["x"], 0.1)
            self.assertIn("tightened evidence crop", report.read_text(encoding="utf-8"))

    def test_repair_draft_defaults_to_clean_shortlist(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: shortlist-draft-test",
                        "title: Shortlist Draft Test",
                        "visual_grammar: paper-atlas",
                        "slides:",
                        "  - kind: cover",
                        "    title: Clean shortlist should win by default",
                    ]
                ),
                encoding="utf-8",
            )
            manifest = root / "GRAMMAR_REPAIR_HINTS.json"
            manifest.write_text(
                json.dumps(
                    {
                        "variants": [
                            {
                                "grammar": "academic-homepage-grid",
                                "score": 91,
                                "recommendation": "revise image scale/crop",
                                "blocking_errors": 0,
                                "warnings": {"proof-image-small": 1},
                                "repair_actions": [{"slide": 1, "issue_kind": "proof-image-small", "suggested_action": "tighten-crop"}],
                            },
                            {
                                "grammar": "object-study-wall",
                                "score": 100,
                                "recommendation": "shortlist",
                                "blocking_errors": 0,
                                "warnings": {},
                                "repair_actions": [],
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )
            draft, report = write_repair_draft(deck_path, manifest, root / "draft")
            draft_data = yaml.safe_load(draft.read_text(encoding="utf-8"))
            self.assertEqual(draft_data["visual_grammar"], "object-study-wall")
            self.assertIn("Selected grammar: `object-study-wall`", report.read_text(encoding="utf-8"))

    def test_repair_draft_preserves_repo_root_asset_fallback(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = root / "nested"
            nested.mkdir()
            deck_path = nested / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: repo-root-asset-test",
                        "title: Repo Root Asset Test",
                        "assets_dir: assets/images",
                        "slides:",
                        "  - kind: cover",
                        "    title: Nested decks may use repo-root assets",
                        "    image: github_avatar.png",
                    ]
                ),
                encoding="utf-8",
            )
            manifest = root / "GRAMMAR_REPAIR_HINTS.json"
            manifest.write_text(
                json.dumps(
                    {
                        "variants": [
                            {
                                "grammar": "object-study-wall",
                                "score": 100,
                                "recommendation": "shortlist",
                                "blocking_errors": 0,
                                "warnings": {},
                                "repair_actions": [],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            draft, _ = write_repair_draft(deck_path, manifest, root / "draft")
            draft_data = yaml.safe_load(draft.read_text(encoding="utf-8"))
            self.assertEqual(draft_data["assets_dir"], (ROOT / "assets" / "images").as_posix())
            self.assertFalse([issue for issue in check_deck(load_deck(draft)) if issue.level == "error"])

    def test_hard_image_errors_map_to_repair_actions(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: hard-image-action-test",
                        "title: Hard Image Action Test",
                        "slides:",
                        "  - kind: evidence",
                        "    title: Proof needs a bigger slot and source pixels",
                        "    image: proof.png",
                        "    evidence:",
                        "      image: proof.png",
                        "      crop:",
                        "        x: 0.1",
                        "        y: 0.1",
                        "        w: 0.8",
                        "        h: 0.6",
                        "  - kind: stack",
                        "    title: Artifact needs a bigger source panel",
                        "    image: artifact.png",
                        "    evidence:",
                        "      image: artifact.png",
                        "      crop:",
                        "        x: 0.0",
                        "        y: 0.0",
                        "        w: 1.0",
                        "        h: 1.0",
                    ]
                ),
                encoding="utf-8",
            )
            report = root / "layout-audit-report.md"
            report.write_text(
                "\n".join(
                    [
                        "## Issues",
                        "### Slide 1 / fill 40%",
                        "- `error` `proof-image-too-small` on `img@.proof-visual`: 19% visible slide area",
                        "- `error` `proof-too-small` on `.proof`: 24% slide area",
                        "- `warn` `proof-small` on `.proof`: 32% slide area",
                        "### Slide 2 / fill 40%",
                        "- `error` `artifact-image-too-small` on `img@.artifact-visual`: 8% visible slide area",
                        "- `error` `artifact-too-small` on `.artifact-panel`: 12% slide area",
                        "- `warn` `artifact-small` on `.artifact-panel`: 18% slide area",
                    ]
                ),
                encoding="utf-8",
            )
            actions = repair_actions_for_report(load_deck(deck_path), report, limit=10)
            by_kind = {action.issue_kind: action for action in actions}
            self.assertEqual(by_kind["proof-image-too-small"].suggested_action, "set-layout-and-tighten-crop")
            self.assertEqual(by_kind["artifact-image-too-small"].suggested_action, "set-layout-and-tighten-crop")
            self.assertEqual(by_kind["proof-too-small"].suggested_action, "set-layout")
            self.assertEqual(by_kind["artifact-too-small"].suggested_action, "set-layout")
            self.assertEqual(by_kind["proof-small"].suggested_action, "set-layout")
            self.assertEqual(by_kind["artifact-small"].suggested_action, "set-layout")
            self.assertEqual(by_kind["proof-too-small"].crop_strategy, "keep current crop until the proof slot is larger")
            self.assertEqual(by_kind["artifact-too-small"].crop_strategy, "keep current crop until the artifact slot is larger")

    def test_html_renderer_applies_visual_grammar(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: grammar-test",
                        "title: Grammar Test",
                        "visual_grammar: keynote-evidence-wall",
                        "slides:",
                        "  - kind: cover",
                        "    title: Visual grammar should reach HTML",
                    ]
                ),
                encoding="utf-8",
            )
            deck = load_deck(deck_path)
            html = render_html(root / "html", deck)
            text = html.read_text(encoding="utf-8")
            self.assertIn('class="grammar-keynote-evidence-wall"', text)
            self.assertIn("body.grammar-highsense-gallery", text)
            self.assertIn("body.grammar-prism-dossier", text)
            self.assertIn("body.grammar-fathom-research-brief", text)
            self.assertIn("body.grammar-jetset-theory-grid", text)
            self.assertIn("body.grammar-monograph-review", text)
            self.assertIn("body.grammar-broadside-lab", text)
            self.assertIn("body.grammar-catalog-atelier", text)
            self.assertIn("body.grammar-evidence-atelier", text)
            self.assertIn("body.grammar-atlas-marginalia", text)
            self.assertIn("body.grammar-systems-field-manual", text)
            self.assertIn("body.grammar-lab-trace-ledger", text)
            self.assertIn("body.grammar-object-study-wall", text)
            self.assertIn("body.grammar-vellum-research-note", text)
            self.assertIn("body.grammar-cobalt-research-grid", text)
            self.assertIn("body.grammar-mono-ink-ledger", text)
            self.assertIn("body.grammar-forest-editorial-brief", text)
            self.assertIn("body.grammar-neo-grid-lab", text)
            self.assertIn("body.grammar-prism-clean-room", text)
            self.assertIn("body.grammar-prism-publication-stack", text)
            self.assertIn("body.grammar-prism-newsroom-index", text)
            self.assertIn("body.grammar-ia-research-archive", text)
            self.assertIn("body.grammar-broadsheet-data-room", text)
            self.assertIn("body.grammar-pentagram-gridnote", text)
            self.assertIn("body.grammar-takram-research-system", text)
            self.assertIn("body.grammar-stamen-data-map", text)
            self.assertIn("body.grammar-couture-exhibition", text)
            self.assertIn("body.grammar-huashu-editorial-lab", text)
            self.assertIn("body.grammar-huashu-build-board", text)
            self.assertIn("body.grammar-gallery-proof-room", text)
            self.assertIn("proof-gallery-split", text)
            self.assertIn("content-bento", text)

    def test_html_renderer_adds_artifact_panel_to_image_backed_content_slide(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "assets"
            assets.mkdir()
            Image.new("RGB", (1200, 760), color=(235, 238, 242)).save(assets / "artifact.png")
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: artifact-panel-test",
                        "title: Artifact Panel Test",
                        f"assets_dir: {assets.as_posix()}",
                        "slides:",
                        "  - kind: stack",
                        "    kicker: Source",
                        "    title: A normal content slide can still carry readable evidence",
                        "    subtitle: The renderer should not drop the image into abstract summary-card mode.",
                        "    image: artifact.png",
                        "    evidence:",
                        "      image: artifact.png",
                        "      crop: {x: 0, y: 0, w: 1, h: 1}",
                        "      caption: Source crop with visible workflow state.",
                        "      source: fixture",
                        "    bullets:",
                        "      - Keep the claim on the left.",
                        "      - Keep the source artifact on the right.",
                        "    labels: []",
                        "    metrics: []",
                    ]
                ),
                encoding="utf-8",
            )
            deck = load_deck(deck_path)
            html = render_html(root / "html", deck)
            text = html.read_text(encoding="utf-8")
            self.assertIn("artifact-panel", text)
            self.assertIn("Source crop with visible workflow state.", text)
            self.assertIn("fixture", text)

    def test_cadence_audit_detects_repeated_composition(self) -> None:
        audits = tuple({"slide": idx, "composition": "text-two-col", "issues": [], "metrics": {"content_fill": 0.42}} for idx in range(1, 6))
        issues = cadence_issues(audits)
        self.assertTrue(any(issue["type"] == "cadence-low-variety" for issue in issues))
        self.assertTrue(any(issue["type"] == "cadence-repetition" for issue in issues))

    def test_layout_report_counts_text_and_image_hard_gates(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            audits = (
                {
                    "slide": 1,
                    "composition": "proof-led",
                    "metrics": {"content_fill": 0.44, "useful_fill": 0.19},
                    "issues": [
                        {"level": "error", "type": "text-line-overlap", "target": "h2 x table", "detail": "line collision"},
                        {"level": "error", "type": "text-block-overlap", "target": "h2 x p", "detail": "block collision"},
                        {"level": "error", "type": "text-block-clearance-tight", "target": "p x li", "detail": "tight block clearance"},
                        {"level": "error", "type": "text-line-height-tight", "target": "h2", "detail": "unsafe line-height"},
                        {"level": "error", "type": "text-self-overlap", "target": "h2", "detail": "line-height collision"},
                        {"level": "error", "type": "text-image-overlap", "target": "h2 x .proof-visual", "detail": "image collision"},
                        {"level": "error", "type": "text-image-clearance-tight", "target": "caption x .proof-visual", "detail": "image clearance"},
                        {"level": "error", "type": "text-clipped", "target": "li", "detail": "hidden text"},
                        {"level": "error", "type": "figure-caption-overlap", "target": ".proof-visual x figcaption", "detail": "caption collision"},
                        {"level": "error", "type": "container-overflow", "target": ".two-col", "detail": "content clipped"},
                        {"level": "error", "type": "missing-proof-image", "target": ".proof", "detail": "placeholder"},
                        {"level": "error", "type": "proof-image-letterboxed-severe", "target": "img", "detail": "severe narrow crop"},
                        {"level": "error", "type": "artifact-image-rendered-too-small", "target": "img", "detail": "tiny rendered source"},
                        {"level": "error", "type": "untyped-image", "target": "img", "detail": "raw inserted image"},
                        {"level": "warn", "type": "untyped-vector-image", "target": "svg", "detail": "raw vector visual"},
                        {"level": "warn", "type": "untyped-background-image", "target": "div", "detail": "background image visual"},
                        {"level": "warn", "type": "image-not-loaded", "target": "img", "detail": "hard gate emitted as warn"},
                        {"level": "warn", "type": "proof-image-letterboxed", "target": "img", "detail": "narrow crop"},
                        {"level": "warn", "type": "content-underfilled", "target": ".slide", "detail": "24% occupied grid"},
                        {"level": "warn", "type": "proof-caption-missing", "target": ".proof", "detail": "missing caption"},
                        {"level": "warn", "type": "proof-caption-generic", "target": ".proof", "detail": "generic proof caption"},
                        {"level": "warn", "type": "artifact-caption-generic", "target": ".artifact-panel", "detail": "generic caption"},
                        {"level": "warn", "type": "caption-text-too-small", "target": "figcaption span", "detail": "9px caption"},
                        {"level": "warn", "type": "caption-contrast-low", "target": "figcaption span", "detail": "2.2:1 contrast"},
                        {"level": "warn", "type": "label-contrast-low", "target": ".label-board b", "detail": "2.1:1 contrast"},
                        {"level": "warn", "type": "useful-fill-low", "target": ".slide", "detail": "19% useful text/source fill"},
                        {"level": "warn", "type": "artifact-role-underfeatured", "target": "img", "detail": "14% visible slide area for source-heavy artifact"},
                    ],
                },
            )
            report, errors = write_layout_audit_report(root / "layout-audit-report.md", audits)
            text = report.read_text(encoding="utf-8")
            self.assertEqual(errors, 17)
            self.assertIn("text-line-overlap", text)
            self.assertIn("text-block-overlap", text)
            self.assertIn("text-block-clearance-tight", text)
            self.assertIn("text-line-height-tight", text)
            self.assertIn("text-self-overlap", text)
            self.assertIn("text-image-overlap", text)
            self.assertIn("text-image-clearance-tight", text)
            self.assertIn("text-clipped", text)
            self.assertIn("figure-caption-overlap", text)
            self.assertIn("container-overflow", text)
            self.assertIn("missing-proof-image", text)
            self.assertIn("proof-image-letterboxed-severe", text)
            self.assertIn("artifact-image-rendered-too-small", text)
            self.assertIn("untyped-image", text)
            self.assertIn("`error` `untyped-vector-image`", text)
            self.assertIn("`error` `untyped-background-image`", text)
            self.assertIn("`error` `image-not-loaded`", text)
            self.assertIn("proof-image-letterboxed", text)
            self.assertIn("proof-caption-missing", text)
            self.assertIn("proof-caption-generic", text)
            self.assertIn("artifact-caption-generic", text)
            self.assertIn("caption-text-too-small", text)
            self.assertIn("caption-contrast-low", text)
            self.assertIn("label-contrast-low", text)
            self.assertIn("useful-fill-low", text)
            self.assertIn("artifact-role-underfeatured", text)
            self.assertIn("Average useful fill: 19.0%", text)
            self.assertIn("## Slide Metrics", text)
            self.assertIn("| 1 | `proof-led` | 44.0% | 19.0% | 27 |", text)
            self.assertIn("### Slide 1 / fill 44% / useful 19%", text)
            self.assertIn("Strict quality warnings: 10", text)
            self.assertIn("Strict warning gates", text)
            self.assertEqual(strict_warning_count(audits), 10)

    def test_image_pptx_export_uses_rendered_slides(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            images = []
            for idx, color in enumerate(((20, 30, 40), (240, 238, 230)), start=1):
                image = root / f"slide-{idx}.png"
                Image.new("RGB", (1600, 900), color=color).save(image)
                images.append(image)
            pptx = create_image_pptx(tuple(images), root / "html-image.pptx")
            self.assertTrue(pptx.exists())
            self.assertGreater(pptx.stat().st_size, 20_000)

    def test_evidence_report_lists_asset_catalog(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "assets"
            assets.mkdir()
            Image.new("RGB", (120, 80), color=(230, 230, 230)).save(assets / "result-chart.png")
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: evidence-test",
                        "title: Evidence Test",
                        f"assets_dir: {assets.as_posix()}",
                        "slides:",
                        "  - kind: evidence",
                        "    kicker: Proof",
                        "    title: A chart should be audited",
                        "    image: result-chart.png",
                        "    evidence:",
                        "      image: result-chart.png",
                        "      caption: chart caption",
                        "      source: local fixture",
                    ]
                ),
                encoding="utf-8",
            )
            deck = load_deck(deck_path)
            report = write_evidence_report(root / "evidence-report.md", deck)
            text = report.read_text(encoding="utf-8")
            self.assertIn("result-chart.png", text)
            self.assertIn("result figure", text)

    def test_evidence_mix_distinguishes_identity_and_work_artifacts(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "assets"
            assets.mkdir()
            Image.new("RGB", (500, 320), color=(250, 250, 250)).save(assets / "homepage.png")
            Image.new("RGB", (500, 320), color=(245, 245, 245)).save(assets / "repo-github.png")
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: mix-test",
                        "title: Mix Test",
                        f"assets_dir: {assets.as_posix()}",
                        "slides:",
                        "  - kind: cover",
                        "    title: Identity anchor",
                        "    image: homepage.png",
                        "  - kind: evidence",
                        "    title: Repository proves artifact availability",
                        "    image: repo-github.png",
                        "    evidence:",
                        "      image: repo-github.png",
                        "      caption: GitHub repository links and README",
                        "      source: https://github.com/example/project",
                    ]
                ),
                encoding="utf-8",
            )
            deck = load_deck(deck_path)
            asset_root = assets
            records = {record.path.relative_to(asset_root).as_posix(): record for record in scan_assets(deck)}
            counts, warnings = evidence_mix(deck, records)
            self.assertEqual(counts.get("identity homepage"), 1)
            self.assertEqual(counts.get("repository artifact"), 1)
            self.assertFalse(warnings)

    def test_evidence_mix_warns_on_repeated_identity_evidence(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "assets"
            assets.mkdir()
            Image.new("RGB", (900, 600), color=(250, 250, 250)).save(assets / "homepage.png")
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: repeated-evidence-test",
                        "title: Repeated Evidence Test",
                        f"assets_dir: {assets.as_posix()}",
                        "slides:",
                        "  - kind: cover",
                        "    title: Identity anchor",
                        "    image: homepage.png",
                        "  - kind: evidence",
                        "    title: Homepage describes the public profile",
                        "    image: homepage.png",
                        "    evidence:",
                        "      image: homepage.png",
                        "      caption: profile text",
                        "      source: personal homepage",
                        "  - kind: product",
                        "    title: Reusing the same homepage should be called out",
                        "    image: homepage.png",
                        "    evidence:",
                        "      image: homepage.png",
                        "      caption: profile again",
                        "      source: personal homepage",
                    ]
                ),
                encoding="utf-8",
            )
            deck = load_deck(deck_path)
            records = {record.path.relative_to(assets).as_posix(): record for record in scan_assets(deck)}
            _, warnings = evidence_mix(deck, records)
            self.assertTrue(any("after two uses" in warning for warning in warnings))
            self.assertTrue(any("identity homepage on evidence slide" in warning for warning in warnings))
            quality_warnings = [issue.message for issue in check_deck(deck) if issue.level == "warn"]
            self.assertTrue(any("appears on slides 1, 2, 3" in warning for warning in quality_warnings))
            self.assertTrue(any("reused as primary proof on slides 2, 3" in warning for warning in quality_warnings))

    def test_reference_classification_prioritizes_homepage_filename(self) -> None:
        from academic_deck_compiler.content import Slide

        slide = Slide(
            kind="evidence",
            kicker="",
            title="A homepage can mention papers, evaluation, and benchmarks",
            subtitle="The page lists selected papers and benchmark news.",
            image="homepage.png",
        )
        role, _ = classify_reference("homepage.png", slide)
        self.assertEqual(role, "identity homepage")

    def test_package_build_copies_deck_and_used_assets(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "assets"
            assets.mkdir()
            Image.new("RGB", (64, 64), color=(20, 20, 20)).save(assets / "avatar.png")
            deck_path = root / "deck.yaml"
            deck_path.write_text(
                "\n".join(
                    [
                        "deck_id: package-test",
                        "title: Package Test",
                        f"assets_dir: {assets.as_posix()}",
                        "slides:",
                        "  - kind: cover",
                        "    title: Package copies assets",
                        "    image: avatar.png",
                    ]
                ),
                encoding="utf-8",
            )
            deck = load_deck(deck_path)
            package_dir = package_build(deck_path, deck, root / "outputs")
            self.assertTrue((package_dir / "deck.yaml").exists())
            self.assertTrue((package_dir / "assets" / "avatar.png").exists())
            self.assertTrue((package_dir / "PACKAGE.md").exists())

    def test_source_manifest_scans_images_and_documents(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            Image.new("RGB", (100, 60), color=(220, 220, 220)).save(root / "chart.png")
            (root / "notes.md").write_text("# Notes", encoding="utf-8")
            manifest = write_source_manifest(root, root / "out")
            text = manifest.read_text(encoding="utf-8")
            self.assertIn("chart.png", text)
            self.assertIn("notes.md", text)
            self.assertIn("result figure", text)


if __name__ == "__main__":
    unittest.main()
