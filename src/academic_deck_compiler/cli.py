from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
import json
from pathlib import Path
import re
import subprocess
from typing import Any

from PIL import Image, ImageDraw
import yaml

from .assets import resolve_assets_dir
from .design_directions import (
    DESIGN_DIRECTIONS,
    DesignDirection,
    direction_for_grammar,
    directions_for_grammar,
)
from .judge import judge_route, write_report
from .evidence_audit import write_evidence_report
from .html_export import (
    STRICT_WARNING_TYPES,
    audit_html_layout,
    cadence_issues,
    export_html_image_pptx,
    strict_warning_count,
    write_layout_audit_report,
)
from .ir import Deck, dump_default_deck, dump_portfolio_deck, load_deck
from .package import package_build
from .paths import OUTPUT_DIR, ROOT
from .preview import contact_sheet, render_pdf_pages
from .quality import check_deck, write_quality_report
from .render_beamer import render_beamer
from .render_html import VISUAL_GRAMMARS, render_html
from .render_pptx import render_pptx
from .source_manifest import write_source_manifest


DEFAULT_COMPARE_GRAMMARS = (
    "academic-homepage-grid",
    "prism-dossier",
    "prism-clean-room",
    "prism-publication-stack",
    "prism-newsroom-index",
    "prism-workbench-index",
    "ia-research-archive",
    "broadsheet-data-room",
    "mono-ink-ledger",
    "forest-editorial-brief",
    "takram-research-system",
    "atlas-marginalia",
    "vellum-research-note",
    "evidence-atelier",
    "stamen-data-map",
    "cobalt-research-grid",
    "systems-field-manual",
    "pentagram-gridnote",
    "neo-grid-lab",
    "object-study-wall",
    "lab-trace-ledger",
    "monograph-review",
    "fathom-research-brief",
    "catalog-atelier",
    "swiss-systems",
    "paper-atlas",
    "keynote-evidence-wall",
    "broadside-lab",
    "jetset-theory-grid",
    "couture-exhibition",
    "js-editorial-cascade",
    "sumi-research-scroll",
    "huashu-editorial-lab",
    "huashu-build-board",
    "huashu-issue-broadsheet",
    "gallery-proof-room",
    "signal-intelligence-brief",
    "raw-grid-research",
    "stencil-field-tablet",
    "maison-research-catalog",
    "folio-swiss-noir",
    "chromatic-research-map",
)

HIGHSENSE_20_GRAMMARS = (
    "prism-workbench-index",
    "prism-clean-room",
    "prism-publication-stack",
    "ia-research-archive",
    "broadsheet-data-room",
    "fathom-research-brief",
    "takram-research-system",
    "pentagram-gridnote",
    "signal-intelligence-brief",
    "huashu-issue-broadsheet",
    "gallery-proof-room",
    "js-editorial-cascade",
    "couture-exhibition",
    "object-study-wall",
    "evidence-atelier",
    "maison-research-catalog",
    "folio-swiss-noir",
    "chromatic-research-map",
    "raw-grid-research",
    "stencil-field-tablet",
)

GRAMMAR_PRESETS = {
    "default": DEFAULT_COMPARE_GRAMMARS,
    "highsense-20": HIGHSENSE_20_GRAMMARS,
    "reference-20": HIGHSENSE_20_GRAMMARS,
}

BEAUTIFUL_TEMPLATE_INDEX = ROOT / "vendor" / "beautiful-html-templates" / "index.json"

ACADEMIC_TEMPLATE_BOOSTS: dict[str, tuple[str, ...]] = {
    "signal": ("academic", "research", "source", "evidence", "institutional", "quiet", "严肃", "学术", "研究", "证据", "克制"),
    "vellum": ("academic", "paper", "thesis", "seminar", "quiet", "scholarly", "论文", "答辩", "学术", "克制"),
    "monochrome": ("source", "dossier", "review", "handout", "formal", "文献", "综述", "档案"),
    "editorial-forest": ("profile", "researcher", "warm", "tasteful", "个人", "主页", "简历", "品味"),
    "blue-professional": ("professional", "technical", "review", "clean", "工程", "技术", "专业"),
    "cobalt-grid": ("technical", "systems", "benchmark", "architecture", "工程", "系统", "基准"),
    "raw-grid": ("benchmark", "demo", "bold", "method", "systems", "硬核", "方法", "基准"),
    "stencil-tablet": ("survey", "map", "field", "taxonomy", "技术地图", "调研", "分类"),
    "broadside": ("bold", "manifesto", "bilingual", "cn", "dramatic", "中文", "英文", "强表达"),
    "cartesian": ("quiet", "tasteful", "classical", "warm", "克制", "高级", "干净"),
}

BEAUTIFUL_TEMPLATE_FALLBACKS: tuple[dict[str, object], ...] = (
    {
        "slug": "signal",
        "name": "Signal",
        "tagline": "Institutional source-led briefing with disciplined contrast.",
        "best_for": "research dossiers, evidence-led profile decks, serious technical briefings",
        "avoid_for": "playful launch pages or image-only visual essays",
        "formality": "high",
        "density": "high",
        "scheme": "mixed",
        "mood": ["quiet", "institutional", "source"],
        "tone": ["academic", "research", "evidence"],
        "occasion": ["briefing", "seminar"],
    },
    {
        "slug": "vellum",
        "name": "Vellum",
        "tagline": "Formal paper-note rhythm for scholarly talks.",
        "best_for": "paper talks, seminars, thesis defenses, careful literature review",
        "avoid_for": "demo-heavy product talks",
        "formality": "high",
        "density": "medium-high",
        "scheme": "light",
        "mood": ["quiet", "scholarly"],
        "tone": ["academic", "paper"],
        "occasion": ["seminar", "defense"],
    },
    {
        "slug": "raw-grid",
        "name": "Raw Grid",
        "tagline": "Hard-edged technical board for methods and benchmarks.",
        "best_for": "systems talks, benchmark stories, demos with source artifacts",
        "avoid_for": "soft personal portfolios",
        "formality": "medium-high",
        "density": "high",
        "scheme": "mixed",
        "mood": ["bold", "technical"],
        "tone": ["systems", "benchmark", "method"],
        "occasion": ["technical review", "demo"],
    },
    {
        "slug": "stencil-tablet",
        "name": "Stencil Tablet",
        "tagline": "Archival field-manual structure for maps and taxonomies.",
        "best_for": "surveys, technical maps, taxonomy decks, artifact inspection",
        "avoid_for": "minimal one-claim pitch decks",
        "formality": "medium-high",
        "density": "high",
        "scheme": "mixed",
        "mood": ["field", "archive"],
        "tone": ["survey", "taxonomy", "technical"],
        "occasion": ["research review"],
    },
    {
        "slug": "cobalt-grid",
        "name": "Cobalt Grid",
        "tagline": "Precise technical grid with enough pressure for engineering reviews.",
        "best_for": "architecture reviews, evaluation decks, benchmark comparisons",
        "avoid_for": "warm editorial portfolios",
        "formality": "medium-high",
        "density": "high",
        "scheme": "dark",
        "mood": ["technical", "clean"],
        "tone": ["systems", "benchmark"],
        "occasion": ["review"],
    },
    {
        "slug": "monochrome",
        "name": "Monochrome",
        "tagline": "Plain source ledger for formal handouts.",
        "best_for": "source-linked reviews, dossiers, technical notes",
        "avoid_for": "talks that need strong image cadence",
        "formality": "high",
        "density": "medium-high",
        "scheme": "light",
        "mood": ["formal", "dossier"],
        "tone": ["source", "review"],
        "occasion": ["handout"],
    },
    {
        "slug": "editorial-forest",
        "name": "Editorial Forest",
        "tagline": "Warm editorial structure for researcher and project profiles.",
        "best_for": "public profiles, selected works, project storytelling",
        "avoid_for": "dense benchmark tables",
        "formality": "medium-high",
        "density": "medium",
        "scheme": "light",
        "mood": ["warm", "tasteful"],
        "tone": ["profile", "researcher"],
        "occasion": ["portfolio"],
    },
    {
        "slug": "cartesian",
        "name": "Cartesian",
        "tagline": "Quiet classical layout with restrained academic polish.",
        "best_for": "clean research talks, calm profile decks, method explanations",
        "avoid_for": "high-energy launches",
        "formality": "medium-high",
        "density": "medium",
        "scheme": "light",
        "mood": ["quiet", "classical"],
        "tone": ["tasteful", "clean"],
        "occasion": ["talk"],
    },
)


@dataclass(frozen=True)
class BeautifulTemplateCandidate:
    slug: str
    name: str
    score: int
    tagline: str
    formality: str
    density: str
    scheme: str
    best_for: str
    avoid_for: str
    rationale: str


def _brief_terms(brief: str) -> set[str]:
    normalized = brief.lower().replace("_", "-")
    terms = set(re.findall(r"[a-z0-9][a-z0-9-]{2,}", normalized))
    for phrase in (
        "学术",
        "研究",
        "论文",
        "技术",
        "工程",
        "系统",
        "基准",
        "证据",
        "主页",
        "个人",
        "简历",
        "克制",
        "高级",
        "干净",
        "中文",
        "英文",
        "调研",
        "方法",
        "严肃",
    ):
        if phrase in brief:
            terms.add(phrase)
    return terms


def beautiful_template_candidates(
    brief: str,
    *,
    limit: int = 5,
    index_path: Path = BEAUTIFUL_TEMPLATE_INDEX,
) -> list[BeautifulTemplateCandidate]:
    data = (
        json.loads(index_path.read_text(encoding="utf-8"))
        if index_path.exists()
        else {"templates": list(BEAUTIFUL_TEMPLATE_FALLBACKS)}
    )
    terms = _brief_terms(brief)
    candidates: list[BeautifulTemplateCandidate] = []
    for template in data.get("templates", []):
        slug_value = str(template.get("slug", ""))
        fields = [
            slug_value,
            str(template.get("name", "")),
            str(template.get("tagline", "")),
            str(template.get("best_for", "")),
            str(template.get("avoid_for", "")),
            str(template.get("formality", "")),
            str(template.get("density", "")),
            str(template.get("scheme", "")),
            " ".join(template.get("mood", [])),
            " ".join(template.get("tone", [])),
            " ".join(template.get("occasion", [])),
        ]
        searchable = " ".join(fields).lower()
        score = sum(2 for term in terms if term in searchable)
        score += sum(3 for term in ACADEMIC_TEMPLATE_BOOSTS.get(slug_value, ()) if term in terms)
        if template.get("density") in {"high", "medium-high"} and {"academic", "research", "学术", "研究", "证据"} & terms:
            score += 2
        if template.get("formality") in {"high", "medium-high"} and {"academic", "research", "严肃", "学术"} & terms:
            score += 2
        if "playful" in searchable and {"academic", "严肃", "学术"} & terms:
            score -= 2
        matched = sorted(term for term in terms if term in searchable or term in ACADEMIC_TEMPLATE_BOOSTS.get(slug_value, ()))
        rationale = ", ".join(matched[:6]) if matched else "tone-distance wildcard"
        candidates.append(
            BeautifulTemplateCandidate(
                slug=slug_value,
                name=str(template.get("name", slug_value)),
                score=score,
                tagline=str(template.get("tagline", "")),
                formality=str(template.get("formality", "")),
                density=str(template.get("density", "")),
                scheme=str(template.get("scheme", "")),
                best_for=str(template.get("best_for", "")),
                avoid_for=str(template.get("avoid_for", "")),
                rationale=rationale,
            )
        )
    ranked = sorted(candidates, key=lambda item: (-item.score, item.slug))
    return ranked[: max(1, limit)]

WARNING_WEIGHTS = {
    "proof-image-small": 8,
    "proof-image-rendered-small": 8,
    "proof-small": 6,
    "artifact-small": 7,
    "artifact-image-small": 7,
    "artifact-image-rendered-small": 7,
    "proof-image-letterboxed": 7,
    "artifact-image-letterboxed": 7,
    "decorative-image-too-small": 2,
    "cover-image-letterboxed": 4,
    "proof-caption-missing": 6,
    "proof-caption-generic": 6,
    "artifact-caption-generic": 6,
    "caption-text-too-small": 5,
    "caption-contrast-low": 5,
    "label-contrast-low": 5,
    "content-underfilled": 4,
    "useful-fill-low": 6,
    "artifact-role-underfeatured": 8,
    "cadence-no-proof-surface": 10,
    "cadence-low-variety": 8,
    "cadence-repetition": 6,
    "title-wrap-deep": 6,
    "subtitle-wrap-deep": 5,
}
AUDIT_INFRA_WARNINGS = {
    "audit-missing",
    "audit-unavailable",
    "audit-timeout",
    "audit-json",
    "screenshot-timeout",
    "screenshot-failed",
}

GRAMMAR_USE_CASES = {
    "academic-homepage-grid": "restrained profile default",
    "prism-dossier": "academic homepage / profile dossier",
    "prism-clean-room": "high-density academic homepage deck",
    "prism-publication-stack": "publication-list / academic homepage stack",
    "prism-newsroom-index": "PRISM-inspired news/publication index deck",
    "prism-workbench-index": "PRISM-inspired researcher workbench / selected-works index",
    "ia-research-archive": "source-linked research archive / paper dossier",
    "broadsheet-data-room": "dense broadsheet data room / source archive",
    "mono-ink-ledger": "formal black-and-white handout",
    "forest-editorial-brief": "editorial research profile default",
    "takram-research-system": "calm research systems memo",
    "atlas-marginalia": "annotated paper reading",
    "vellum-research-note": "formal dark research note",
    "evidence-atelier": "evidence-heavy visual profile",
    "stamen-data-map": "cartographic data/project evidence deck",
    "cobalt-research-grid": "systems / method-heavy deck",
    "systems-field-manual": "technical architecture deck",
    "pentagram-gridnote": "bold typographic methods deck",
    "neo-grid-lab": "loud lab/demo deck",
    "object-study-wall": "artifact and proof showcase default",
    "lab-trace-ledger": "experimental workflow ledger",
    "monograph-review": "long-form academic review",
    "fathom-research-brief": "structured research brief",
    "catalog-atelier": "portfolio catalog / project survey",
    "swiss-systems": "clean technical systems talk",
    "paper-atlas": "paper close-reading / figure atlas",
    "keynote-evidence-wall": "large keynote proof wall",
    "broadside-lab": "poster-like lab statement",
    "jetset-theory-grid": "high-contrast theory / method talk",
    "couture-exhibition": "editorial exhibition / high-end web proof wall",
    "js-editorial-cascade": "high-sense web editorial cascade / asymmetrical proof deck",
    "sumi-research-scroll": "ink-and-paper academic scroll / source-index profile",
    "huashu-editorial-lab": "Huashu-style typographic lab deck",
    "huashu-build-board": "Huashu Build-style hard benchmark board",
    "huashu-issue-broadsheet": "Huashu-style issue broadsheet / bold technical handout",
    "gallery-proof-room": "gallery proof plates / exhibition labels",
    "signal-intelligence-brief": "Signal-inspired institutional briefing / source dossier",
    "raw-grid-research": "Raw Grid-inspired graphic research demo / benchmark board",
    "stencil-field-tablet": "Stencil & Tablet-inspired field manual / poster survey",
    "maison-research-catalog": "luxury editorial catalog / artifact-rich profile",
    "folio-swiss-noir": "black-and-white exhibition folio / hard technical board",
    "chromatic-research-map": "colored research map / project landscape deck",
}

GRAMMAR_TASTE_BONUS = {
    "object-study-wall": 7,
    "forest-editorial-brief": 6,
    "evidence-atelier": 5,
    "prism-clean-room": 5,
    "prism-publication-stack": 5,
    "prism-newsroom-index": 5,
    "prism-workbench-index": 5,
    "takram-research-system": 5,
    "gallery-proof-room": 5,
    "js-editorial-cascade": 5,
    "sumi-research-scroll": 5,
    "couture-exhibition": 4,
    "huashu-editorial-lab": 4,
    "huashu-build-board": 4,
    "huashu-issue-broadsheet": 4,
    "signal-intelligence-brief": 4,
    "cobalt-research-grid": 4,
    "stamen-data-map": 4,
    "broadsheet-data-room": 4,
    "raw-grid-research": 3,
    "maison-research-catalog": 5,
    "folio-swiss-noir": 4,
    "chromatic-research-map": 4,
    "stencil-field-tablet": 2,
    "academic-homepage-grid": 3,
    "prism-dossier": 3,
    "ia-research-archive": 3,
    "atlas-marginalia": 2,
    "monograph-review": 2,
    "systems-field-manual": 1,
    "lab-trace-ledger": 1,
    "vellum-research-note": 1,
    "jetset-theory-grid": 1,
    "pentagram-gridnote": 1,
}

GRAMMAR_STYLE_FAMILY = {
    "academic-homepage-grid": "academic-homepage",
    "prism-dossier": "academic-homepage",
    "prism-clean-room": "academic-homepage",
    "prism-publication-stack": "academic-homepage",
    "prism-newsroom-index": "academic-homepage",
    "prism-workbench-index": "academic-workbench",
    "editorial-profile": "editorial-profile",
    "forest-editorial-brief": "editorial-profile",
    "catalog-atelier": "editorial-profile",
    "evidence-atelier": "proof-gallery",
    "object-study-wall": "proof-gallery",
    "gallery-proof-room": "proof-gallery",
    "couture-exhibition": "proof-gallery",
    "js-editorial-cascade": "web-editorial",
    "sumi-research-scroll": "ink-scroll",
    "paper-atlas": "formal-dossier",
    "atlas-marginalia": "formal-dossier",
    "ia-research-archive": "formal-dossier",
    "broadsheet-data-room": "formal-dossier",
    "monograph-review": "formal-dossier",
    "mono-ink-ledger": "formal-dossier",
    "vellum-research-note": "formal-dossier",
    "fathom-research-brief": "research-brief",
    "takram-research-system": "research-brief",
    "stamen-data-map": "research-brief",
    "swiss-systems": "systems-grid",
    "systems-field-manual": "systems-grid",
    "cobalt-research-grid": "systems-grid",
    "lab-trace-ledger": "systems-grid",
    "dark-lab-notebook": "dark-lab",
    "broadside-lab": "bold-reset",
    "jetset-theory-grid": "bold-reset",
    "pentagram-gridnote": "bold-reset",
    "neo-grid-lab": "bold-reset",
    "keynote-evidence-wall": "stage-proof",
    "highsense-gallery": "stage-proof",
    "huashu-editorial-lab": "huashu",
    "huashu-build-board": "huashu",
    "huashu-issue-broadsheet": "huashu",
    "signal-intelligence-brief": "institutional-editorial",
    "raw-grid-research": "raw-grid",
    "stencil-field-tablet": "field-tablet",
    "maison-research-catalog": "luxury-editorial",
    "folio-swiss-noir": "hard-folio",
    "chromatic-research-map": "chromatic-map",
}


@dataclass(frozen=True)
class LayoutReportSummary:
    blocking_errors: int = 0
    warnings: int = 0
    average_fill: str = "n/a"
    average_useful_fill: str = "n/a"
    sequence: str = "n/a"
    distinct_cadences: int = 0
    warning_counts: tuple[tuple[str, int], ...] = ()


@dataclass(frozen=True)
class GrammarComparisonRow:
    grammar: str
    variant_dir: Path
    errors: int
    warnings: int
    warning_counts: tuple[tuple[str, int], ...]
    average_fill: str
    average_useful_fill: str
    sequence: str
    distinct_cadences: int
    score: int
    recommendation: str
    use_case: str
    repair_hints: tuple[str, ...] = ()
    repair_actions: tuple["RepairAction", ...] = ()


@dataclass(frozen=True)
class LayoutIssue:
    slide: int | None
    level: str
    kind: str
    target: str
    detail: str


@dataclass(frozen=True)
class RepairAction:
    slide: int | None
    slide_title: str
    issue_kind: str
    level: str
    target: str
    detail: str
    current_layout: str
    current_image: str
    current_crop: dict[str, float] | None
    suggested_action: str
    suggested_layout: str
    crop_strategy: str
    content_strategy: str
    hint: str


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "academic-deck"


def with_visual_grammar(deck, visual_grammar: str | None):
    if not visual_grammar:
        return deck
    grammar = visual_grammar.strip().lower().replace("_", "-")
    if grammar not in VISUAL_GRAMMARS:
        known = ", ".join(sorted(VISUAL_GRAMMARS))
        raise SystemExit(f"Unsupported visual grammar `{visual_grammar}`. Use one of: {known}.")
    return replace(deck, visual_grammar=grammar)


def export_pptx_to_pdf(pptx_path: Path, pdf_path: Path) -> Path | None:
    script = f'''
set pptxPath to POSIX file "{pptx_path}" as alias
set outPath to POSIX file "{pdf_path}"
tell application "Microsoft PowerPoint"
    open pptxPath
    delay 1
    set thePres to active presentation
    save thePres in outPath as save as PDF
    close thePres saving no
end tell
'''
    try:
        subprocess.run(["osascript", "-e", script], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except Exception:
        return None
    return pdf_path if pdf_path.exists() else None


def mark_delivery_blocked(output_dir: Path, reason: str, artifacts: tuple[Path | None, ...]) -> Path:
    """Mark strict-mode artifacts as review-only when a delivery gate fails."""
    output_dir.mkdir(parents=True, exist_ok=True)
    moved: list[tuple[Path, Path]] = []
    for artifact in artifacts:
        if not artifact or not artifact.exists() or not artifact.is_file():
            continue
        blocked = artifact.with_name(f"{artifact.stem}.blocked{artifact.suffix}")
        if blocked.exists():
            blocked.unlink()
        artifact.replace(blocked)
        moved.append((artifact, blocked))
    marker = output_dir / "DELIVERY_BLOCKED.md"
    lines = [
        "# Delivery Blocked",
        "",
        reason,
        "",
        "This run failed a strict layout, image, density, or source-contract gate. Files in this directory are review artifacts, not deliverables.",
        "",
        "## Renamed Artifacts",
        "",
    ]
    if moved:
        lines.extend(f"- `{original}` -> `{blocked}`" for original, blocked in moved)
    else:
        lines.append("- No deliverable artifact was present to rename.")
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            "Read `quality-report.md`, `layout-audit-report.md`, and `GRAMMAR_REPAIR_HINTS.json` if present, then rerun with `--fail-on-layout`.",
        ]
    )
    marker.write_text("\n".join(lines), encoding="utf-8")
    return marker


def build_all(
    output_dir: Path,
    deck_path: str | None = None,
    visual_grammar: str | None = None,
    fail_on_layout: bool = False,
) -> None:
    deck = with_visual_grammar(load_deck(deck_path), visual_grammar)
    output_dir.mkdir(parents=True, exist_ok=True)
    preview_dir = output_dir / "preview"
    safe_name = slug(deck.deck_id or deck.title)
    quality_issues = check_deck(deck)
    quality_report = write_quality_report(output_dir / "quality-report.md", deck, quality_issues)
    quality_errors = sum(1 for issue in quality_issues if issue.level == "error")
    if quality_errors:
        raise SystemExit(f"Quality check failed with {quality_errors} blocking issue(s). See {quality_report}.")
    evidence_report = write_evidence_report(output_dir / "evidence-report.md", deck)
    pptx_path = render_pptx(output_dir / f"{safe_name}.pptx", deck)
    pptx_pdf = export_pptx_to_pdf(pptx_path, output_dir / f"{safe_name}-pptx-render.pdf")
    pptx_images = []
    if pptx_pdf:
        pptx_images = render_pdf_pages(pptx_pdf, preview_dir / "pptx", "pptx")
        contact_sheet(pptx_images, output_dir / "pptx-contact-sheet.png")

    tex_path, beamer_pdf = render_beamer(output_dir / "beamer", deck=deck)
    beamer_images = []
    if beamer_pdf:
        beamer_images = render_pdf_pages(beamer_pdf, preview_dir / "beamer", "beamer")
        contact_sheet(beamer_images, output_dir / "beamer-contact-sheet.png")

    reports = [judge_route("PPTX-native", pptx_images)]
    if beamer_images:
        reports.append(judge_route("LaTeX/Beamer", beamer_images))
    write_report(output_dir / "judge-report.md", reports)
    html_path = render_html(output_dir / "html", deck=deck)
    audits = audit_html_layout(html_path, len(deck.slides))
    layout_report, layout_errors = write_layout_audit_report(output_dir / "layout-audit-report.md", audits)
    strict_layout_warnings = strict_warning_count(audits, cadence_issues(audits))
    blocked_reason = ""
    if fail_on_layout and layout_errors:
        blocked_reason = f"Layout audit failed with {layout_errors} blocking issue(s)."
    elif fail_on_layout and strict_layout_warnings:
        blocked_reason = f"Strict layout audit failed with {strict_layout_warnings} image/density warning gate(s)."
    blocked_marker = (
        mark_delivery_blocked(output_dir, blocked_reason, (pptx_path, pptx_pdf, beamer_pdf))
        if blocked_reason
        else None
    )
    print(f"PPTX: {pptx_path}")
    if pptx_pdf:
        print(f"PPTX PDF render: {pptx_pdf}")
    else:
        print("PPTX PDF render: unavailable; open/grant PowerPoint access and rebuild for visual QA.")
    print(f"Beamer TeX: {tex_path}")
    if beamer_pdf:
        print(f"Beamer PDF: {beamer_pdf}")
    print(f"HTML preview: {html_path}")
    print(f"Layout audit: {layout_report}")
    print(f"Report: {output_dir / 'judge-report.md'}")
    print(f"Quality: {quality_report}")
    print(f"Evidence: {evidence_report}")
    if blocked_marker:
        print(f"Delivery blocked: {blocked_marker}")
        raise SystemExit(f"{blocked_reason} See {blocked_marker}.")


def check_only(deck_path: str | None, out: str) -> None:
    deck = load_deck(deck_path)
    target = Path(out).resolve()
    if target.suffix.lower() != ".md":
        target = target / "quality-report.md"
    report = write_quality_report(target, deck, check_deck(deck))
    print(f"Quality: {report}")


def evidence_only(deck_path: str | None, out: str) -> None:
    deck = load_deck(deck_path)
    target = Path(out).resolve()
    if target.suffix.lower() != ".md":
        target = target / "evidence-report.md"
    report = write_evidence_report(target, deck)
    print(f"Evidence: {report}")


def html_pptx_only(
    deck_path: str | None,
    out: str,
    width: int,
    height: int,
    chrome: str | None,
    visual_grammar: str | None = None,
    fail_on_layout: bool = False,
    skip_layout_audit: bool = False,
) -> None:
    if fail_on_layout and skip_layout_audit:
        raise SystemExit("`--fail-on-layout` cannot be combined with `--skip-layout-audit`; strict delivery needs the DOM layout audit.")
    deck = with_visual_grammar(load_deck(deck_path), visual_grammar)
    output_dir = Path(out).resolve()
    quality_issues = check_deck(deck)
    quality_report = write_quality_report(output_dir / "quality-report.md", deck, quality_issues)
    quality_errors = sum(1 for issue in quality_issues if issue.level == "error")
    if quality_errors:
        raise SystemExit(f"Quality check failed with {quality_errors} blocking issue(s). See {quality_report}.")
    evidence_report = write_evidence_report(output_dir / "evidence-report.md", deck)
    result = export_html_image_pptx(
        deck,
        output_dir,
        width=width,
        height=height,
        chrome_path=chrome,
        skip_layout_audit=skip_layout_audit,
    )
    reports = [judge_route("HTML-image PPTX", list(result.images))]
    write_report(output_dir / "judge-report.md", reports)
    blocked_reason = ""
    if fail_on_layout and result.layout_errors:
        blocked_reason = f"Layout audit failed with {result.layout_errors} blocking issue(s)."
    elif fail_on_layout and result.strict_layout_warnings:
        blocked_reason = f"Strict layout audit failed with {result.strict_layout_warnings} image/density warning gate(s)."
    blocked_marker = mark_delivery_blocked(output_dir, blocked_reason, (result.pptx_path,)) if blocked_reason else None
    print(f"HTML preview: {result.html_path}")
    print(f"HTML screenshots: {result.html_path.parent.parent / 'html-shots'}")
    print(f"HTML-image PPTX: {result.pptx_path}")
    print(f"HTML contact sheet: {result.contact_sheet_path}")
    print(f"Layout audit: {result.layout_report_path}")
    print(f"Report: {output_dir / 'judge-report.md'}")
    print(f"Quality: {quality_report}")
    print(f"Evidence: {evidence_report}")
    if blocked_marker:
        print(f"Delivery blocked: {blocked_marker}")
        raise SystemExit(f"{blocked_reason} See {blocked_marker}.")


def parse_grammar_list(value: str | None) -> tuple[str, ...]:
    if not value:
        return DEFAULT_COMPARE_GRAMMARS
    preset = value.strip().lower().replace("_", "-")
    if preset in GRAMMAR_PRESETS:
        return GRAMMAR_PRESETS[preset]
    grammars = tuple(item.strip().lower().replace("_", "-") for item in value.split(",") if item.strip())
    unknown = [grammar for grammar in grammars if grammar not in VISUAL_GRAMMARS]
    if unknown:
        known = ", ".join(sorted(VISUAL_GRAMMARS))
        raise SystemExit(f"Unsupported visual grammar(s): {', '.join(unknown)}. Use one of: {known}.")
    return grammars or DEFAULT_COMPARE_GRAMMARS


def first_report_line(report_path: Path, needle: str) -> str:
    if not report_path.exists():
        return ""
    for line in report_path.read_text(encoding="utf-8").splitlines():
        if needle in line:
            return line
    return ""


def _count_issue_kinds(text: str, level: str = "warn") -> tuple[tuple[str, int], ...]:
    counts: dict[str, int] = {}
    for match in re.finditer(rf"- `{re.escape(level)}` `([^`]+)`", text):
        kind = match.group(1)
        counts[kind] = counts.get(kind, 0) + 1
    return tuple(sorted(counts.items()))


def _strict_warning_total(warning_counts: tuple[tuple[str, int], ...]) -> int:
    return sum(count for kind, count in warning_counts if kind in STRICT_WARNING_TYPES)


def layout_report_issues(report_path: Path) -> tuple[LayoutIssue, ...]:
    if not report_path.exists():
        return (LayoutIssue(None, "warn", "audit-missing", "audit", "layout audit report was not written"),)
    issues: list[LayoutIssue] = []
    current_slide: int | None = None
    for line in report_path.read_text(encoding="utf-8").splitlines():
        slide_match = re.match(r"^### Slide (\d+)", line)
        if slide_match:
            current_slide = int(slide_match.group(1))
            continue
        issue_match = re.match(r"^- `(error|warn)` `([^`]+)` on `([^`]+)`: (.*)$", line)
        if issue_match:
            level, kind, target, detail = issue_match.groups()
            issues.append(LayoutIssue(current_slide, level, kind, target, detail))
    return tuple(issues)


def _parse_int_line(text: str, label: str) -> int:
    match = re.search(rf"^- {re.escape(label)}: (\d+)", text, flags=re.MULTILINE)
    return int(match.group(1)) if match else 0


def layout_report_summary(report_path: Path) -> LayoutReportSummary:
    if not report_path.exists():
        return LayoutReportSummary(warning_counts=(("audit-missing", 1),))
    text = report_path.read_text(encoding="utf-8")
    avg = re.search(r"^- Average content fill: ([^\n]+)", text, flags=re.MULTILINE)
    useful_avg = re.search(r"^- Average useful fill: ([^\n]+)", text, flags=re.MULTILINE)
    sequence = re.search(r"^- Composition sequence: `([^`]+)`", text, flags=re.MULTILINE)
    distinct = re.search(r"^- Distinct cadences: (\d+)", text, flags=re.MULTILINE)
    return LayoutReportSummary(
        blocking_errors=_parse_int_line(text, "Blocking errors"),
        warnings=_parse_int_line(text, "Warnings"),
        average_fill=avg.group(1).strip() if avg else "n/a",
        average_useful_fill=useful_avg.group(1).strip() if useful_avg else "n/a",
        sequence=sequence.group(1).strip() if sequence else "n/a",
        distinct_cadences=int(distinct.group(1)) if distinct else 0,
        warning_counts=_count_issue_kinds(text, "warn"),
    )


def format_warning_counts(warning_counts: tuple[tuple[str, int], ...], warnings: int) -> str:
    if warnings == 0:
        return "0"
    if not warning_counts:
        return str(warnings)
    detail = ", ".join(f"{kind} x{count}" for kind, count in warning_counts)
    return f"{warnings} ({detail})"


def score_grammar_variant(grammar: str, summary: LayoutReportSummary) -> int:
    score = 100
    score -= summary.blocking_errors * 100
    for kind, count in summary.warning_counts:
        score -= WARNING_WEIGHTS.get(kind, 3) * count
    if summary.distinct_cadences and summary.distinct_cadences < 3:
        score -= 8
    score += GRAMMAR_TASTE_BONUS.get(grammar, 0)
    if summary.warnings:
        score = min(score, 99)
    return max(0, min(100, score))


def grammar_style_family(grammar: str) -> str:
    return GRAMMAR_STYLE_FAMILY.get(grammar, "general")


def _composition_family(token: str) -> str:
    token = token.strip()
    if token.startswith("cover-"):
        if "poster" in token:
            return "cover-poster"
        if "source" in token:
            return "cover-source"
        if "wall" in token:
            return "cover-wall"
        return "cover-standard"
    if token.startswith("proof-"):
        if "gallery" in token:
            return "proof-gallery"
        if "atlas" in token or "marginalia" in token:
            return "proof-atlas"
        if "dossier" in token:
            return "proof-dossier"
        if "ledger" in token:
            return "proof-ledger"
        if "stage" in token:
            return "proof-stage"
        return "proof-general"
    if token.startswith("artifact-"):
        if "showcase" in token:
            return "artifact-showcase"
        if "marginalia" in token:
            return "artifact-marginalia"
        if "dossier" in token:
            return "artifact-dossier"
        if "ledger" in token:
            return "artifact-ledger"
        return "artifact-general"
    if token.startswith("matrix-"):
        return "matrix"
    if token.startswith("content-") or token.startswith("text-"):
        return "content"
    return token or "unknown"


def composition_family_signature(sequence: str) -> str:
    if not sequence or sequence == "n/a":
        return "unknown"
    families = [_composition_family(part) for part in sequence.split(" -> ")]
    compact: list[str] = []
    for family in families:
        if not compact or compact[-1] != family:
            compact.append(family)
    return " -> ".join(compact)


def recommendation_for_variant(summary: LayoutReportSummary, score: int) -> str:
    warning_map = dict(summary.warning_counts)
    if summary.blocking_errors:
        return "discard until fixed"
    if "audit-missing" in warning_map:
        return "rerun strict audit"
    if score >= 96 and not warning_map:
        return "shortlist"
    if score >= 92 and set(warning_map) <= {"decorative-image-too-small", "cover-image-letterboxed"}:
        return "revise cover crop"
    if (
        warning_map.get("proof-image-small")
        or warning_map.get("proof-image-rendered-small")
        or warning_map.get("proof-small")
        or warning_map.get("artifact-small")
        or warning_map.get("artifact-image-small")
        or warning_map.get("artifact-image-rendered-small")
        or warning_map.get("artifact-role-underfeatured")
    ):
        return "revise image scale/crop"
    if any("letterboxed" in kind for kind in warning_map):
        return "revise crop or slot"
    if warning_map.get("callout-overlap"):
        return "revise callout placement"
    if (
        warning_map.get("proof-caption-missing")
        or warning_map.get("proof-caption-generic")
        or warning_map.get("artifact-caption-generic")
        or warning_map.get("caption-text-too-small")
        or warning_map.get("caption-contrast-low")
        or warning_map.get("label-contrast-low")
    ):
        return "revise image caption/source"
    if warning_map.get("title-wrap-deep") or warning_map.get("subtitle-wrap-deep"):
        return "revise text density"
    if warning_map.get("content-underfilled") or warning_map.get("useful-fill-low"):
        return "revise density/layout"
    if score >= 90:
        return "candidate"
    return "special-use only"


def _crop_text(deck: Deck, slide_number: int) -> str:
    slide = deck.slides[slide_number - 1]
    if slide.evidence and slide.evidence.crop:
        crop = slide.evidence.crop
        return f"crop x={crop.x:.2f}, y={crop.y:.2f}, w={crop.w:.2f}, h={crop.h:.2f}"
    return "no explicit crop"


def _crop_dict(deck: Deck, slide_number: int) -> dict[str, float] | None:
    slide = deck.slides[slide_number - 1]
    if slide.evidence and slide.evidence.crop:
        crop = slide.evidence.crop
        return {"x": crop.x, "y": crop.y, "w": crop.w, "h": crop.h}
    return None


def _image_value(deck: Deck, slide_number: int) -> str:
    slide = deck.slides[slide_number - 1]
    image = slide.evidence.image if slide.evidence and slide.evidence.image else slide.image
    return str(image or "")


def _image_text(deck: Deck, slide_number: int) -> str:
    image = _image_value(deck, slide_number)
    return f"`{image}`" if image else "no image"


def _slide_label(deck: Deck | None, slide_number: int | None) -> str:
    if not deck or slide_number is None or slide_number < 1 or slide_number > len(deck.slides):
        return "Deck"
    slide = deck.slides[slide_number - 1]
    return f"Slide {slide_number} `{slide.title}`"


def _repair_action(
    deck: Deck | None,
    issue: LayoutIssue,
    suggested_action: str,
    suggested_layout: str,
    crop_strategy: str,
    content_strategy: str,
    hint: str,
) -> RepairAction:
    slide_title = ""
    current_layout = ""
    current_image = ""
    current_crop = None
    if deck and issue.slide and 1 <= issue.slide <= len(deck.slides):
        slide = deck.slides[issue.slide - 1]
        slide_title = slide.title
        current_layout = slide.layout
        current_image = _image_value(deck, issue.slide)
        current_crop = _crop_dict(deck, issue.slide)
    return RepairAction(
        slide=issue.slide,
        slide_title=slide_title,
        issue_kind=issue.kind,
        level=issue.level,
        target=issue.target,
        detail=issue.detail,
        current_layout=current_layout,
        current_image=current_image,
        current_crop=current_crop,
        suggested_action=suggested_action,
        suggested_layout=suggested_layout,
        crop_strategy=crop_strategy,
        content_strategy=content_strategy,
        hint=hint,
    )


def repair_action_for_issue(deck: Deck | None, issue: LayoutIssue) -> RepairAction | None:
    label = _slide_label(deck, issue.slide)
    slide = deck.slides[issue.slide - 1] if deck and issue.slide and 1 <= issue.slide <= len(deck.slides) else None
    image = _image_text(deck, issue.slide) if deck and issue.slide and 1 <= issue.slide <= len(deck.slides) else "the source image"
    crop = _crop_text(deck, issue.slide) if deck and issue.slide and 1 <= issue.slide <= len(deck.slides) else "unknown crop"

    if issue.kind in {"proof-image-small", "proof-image-too-small", "proof-image-rendered-small", "proof-image-rendered-too-small", "proof-image-upscaled-too-much"}:
        if slide and slide.layout == "proof-showcase":
            hint = (
                f"{label}: proof is underfeatured ({issue.detail}). It already requests `layout: proof-showcase`; "
                f"crop {image} tighter around one readable proof object ({crop}) or replace it with a higher-signal figure/screenshot."
            )
            return _repair_action(deck, issue, "tighten-crop", "proof-showcase", "tighten around one readable proof object", "replace weak source if crop still reads small", hint)
        hint = (
            f"{label}: proof is underfeatured ({issue.detail}). Set `layout: proof-showcase`, crop {image} tighter "
            f"around one readable proof object ({crop}), and shorten side notes/metrics if the proof still falls below target."
        )
        return _repair_action(deck, issue, "set-layout-and-tighten-crop", "proof-showcase", "tighten around one readable proof object", "shorten side notes/metrics if proof remains under target", hint)
    if issue.kind == "proof-small" or issue.kind == "proof-too-small":
        if slide and slide.layout == "proof-showcase":
            hint = (
                f"{label}: proof container is too small ({issue.detail}) even with `layout: proof-showcase`. "
                "Use a grammar with a larger proof slot, split the slide, or move side notes into speaker notes."
            )
            return _repair_action(deck, issue, "split-or-change-grammar", "proof-showcase", "keep or tighten crop after slot is enlarged", "split slide or choose a larger proof grammar", hint)
        hint = (
            f"{label}: proof container is too small ({issue.detail}). Set `layout: proof-showcase` first; "
            "if the proof still fails, split the slide or choose a larger proof grammar."
        )
        return _repair_action(deck, issue, "set-layout", "proof-showcase", "keep current crop until the proof slot is larger", "shorten side notes/metrics if proof remains under target", hint)
    if issue.kind in {
        "artifact-image-small",
        "artifact-image-too-small",
        "artifact-image-rendered-small",
        "artifact-image-rendered-too-small",
        "artifact-image-upscaled-too-much",
        "artifact-role-underfeatured",
    }:
        if slide and slide.kind not in {"cover", "map", "matrix", "evidence", "loop", "product"}:
            if slide.layout == "artifact-showcase":
                hint = (
                    f"{label}: artifact panel is too small ({issue.detail}). It already requests `layout: artifact-showcase`; "
                    f"crop {image} to the smallest readable source region ({crop}), replace the weak source, or split the artifact into its own slide."
                )
                return _repair_action(deck, issue, "tighten-crop-or-split", "artifact-showcase", "crop to smallest readable source region", "replace weak source or split the artifact into its own slide", hint)
            hint = (
                f"{label}: artifact panel is too small ({issue.detail}). Set `layout: artifact-showcase`, crop {image} "
                f"to the smallest readable source region ({crop}), or split the slide if bullets compete with the artifact."
            )
            return _repair_action(deck, issue, "set-layout-and-tighten-crop", "artifact-showcase", "crop to smallest readable source region", "split slide if bullets compete with artifact", hint)
        hint = (
            f"{label}: artifact/proof source is too small ({issue.detail}). Promote the source to a proof slide with "
            f"`layout: proof-showcase` or split the artifact into its own slide."
        )
        return _repair_action(deck, issue, "promote-to-proof-or-split", "proof-showcase", "use one readable proof crop", "split artifact into its own slide", hint)
    if issue.kind in {"artifact-small", "artifact-too-small"}:
        if slide and slide.kind not in {"cover", "map", "matrix", "evidence", "loop", "product"}:
            if slide.layout == "artifact-showcase":
                hint = (
                    f"{label}: artifact container is too small ({issue.detail}) even with `layout: artifact-showcase`. "
                    "Split the slide, remove competing bullets/labels, or choose a grammar with a larger source panel."
                )
                return _repair_action(deck, issue, "split-or-change-grammar", "artifact-showcase", "keep current crop until the artifact slot is larger", "split slide or choose a larger artifact grammar", hint)
            hint = (
                f"{label}: artifact container is too small ({issue.detail}). Set `layout: artifact-showcase` first; "
                "if the artifact still fails, split the slide or choose a larger artifact grammar."
            )
            return _repair_action(deck, issue, "set-layout", "artifact-showcase", "keep current crop until the artifact slot is larger", "split slide if bullets compete with artifact", hint)
        hint = (
            f"{label}: artifact/proof container is too small ({issue.detail}). Promote the source to a dedicated proof slide "
            "or split the artifact into its own slide."
        )
        return _repair_action(deck, issue, "promote-to-proof-or-split", "proof-showcase", "use one readable proof crop after the slide is split", "split artifact into its own slide", hint)
    if "letterboxed" in issue.kind:
        hint = (
            f"{label}: source pixels are letterboxed ({issue.detail}). Adjust `evidence.crop` for {image} so the crop "
            f"matches the active slot aspect ratio; avoid full-page screenshots with browser chrome or dead margins."
        )
        return _repair_action(deck, issue, "match-crop-to-slot", "", "change crop aspect ratio to match active slot", "avoid full-page screenshots with browser chrome/dead margins", hint)
    if issue.kind == "callout-overlap":
        hint = (
            f"{label}: callout pins collide ({issue.detail}). Keep at most two pins, move them to separated source regions, "
            "or convert one annotation into the caption."
        )
        return _repair_action(deck, issue, "separate-or-reduce-callouts", "", "keep crop stable while moving pins onto separated source regions", "drop low-value callouts or move one into caption", hint)
    if issue.kind in {"content-underfilled", "useful-fill-low"}:
        hint = (
            f"{label}: slide is underfilled ({issue.detail}). Enlarge the proof/artifact surface, use a fuller composition, "
            "or merge in one stronger evidence/metric module instead of leaving the canvas thin."
        )
        return _repair_action(deck, issue, "increase-slide-density", "", "enlarge source crop only if it remains readable", "add a stronger evidence/metric module or switch composition", hint)
    if issue.kind in {"decorative-image-too-small", "cover-image-letterboxed"}:
        hint = (
            f"{label}: cover image is not carrying a clean identity role ({issue.detail}). Enlarge, recrop, or replace {image}, "
            "or remove it and let the cover be typographic; do not count this image as evidence."
        )
        return _repair_action(deck, issue, "enlarge-or-remove-decoration", "", "enlarge identity crop only if it remains tasteful", "remove decorative image and use typographic cover if crop has no evidence role", hint)
    if issue.kind == "proof-caption-missing":
        hint = (
            f"{label}: primary evidence was inserted without enough caption/source context ({issue.detail}). Add a one-line "
            "caption naming the inspected claim and a compact source label; if you cannot name the claim, replace the image."
        )
        return _repair_action(deck, issue, "add-proof-caption-source", "", "keep crop only if caption names the inspected region", "add caption/source or replace the weak proof", hint)
    if issue.kind == "proof-caption-generic":
        hint = (
            f"{label}: primary evidence caption/source is too generic ({issue.detail}). Replace vague labels with the inspected "
            "claim, source title, or URL; if the image cannot support a specific caption, choose stronger evidence."
        )
        return _repair_action(deck, issue, "rewrite-proof-caption-source", "", "keep crop only if the rewritten caption names the visible evidence", "rewrite caption/source or replace weak proof", hint)
    if issue.kind == "artifact-caption-generic":
        hint = (
            f"{label}: artifact image is using a generic caption/source fallback ({issue.detail}). Add `evidence.caption` "
            "and `evidence.source` that explain the exact region shown, or remove the artifact panel."
        )
        return _repair_action(deck, issue, "add-artifact-caption-source", "", "keep crop only if the artifact region remains readable", "add caption/source or remove the image", hint)
    if issue.kind in {"caption-text-too-small", "caption-contrast-low", "label-contrast-low"}:
        hint = (
            f"{label}: small support text is not readable enough ({issue.detail}). Increase font/contrast "
            "in the active grammar or simplify the text so it remains legible at contact-sheet scale."
        )
        return _repair_action(deck, issue, "increase-support-text-readability", "", "keep crop stable while making support text readable", "increase support-text font/contrast or shorten the text", hint)
    if issue.kind in {"text-image-overlap", "text-image-clearance-tight", "proof-notes-image-overlap", "artifact-notes-image-overlap", "notes-image-clearance-tight", "figure-caption-overlap", "figure-caption-clearance-tight"}:
        hint = (
            f"{label}: text and image are fighting for space ({issue.kind}). Shorten the title/caption or switch to a "
            f"proof/artifact showcase composition before judging the visual style."
        )
        return _repair_action(deck, issue, "resolve-text-image-conflict", "", "preserve readable proof crop after text is shortened", "shorten title/caption or switch to showcase composition", hint)
    if issue.kind in {
        "element-overlap",
        "viewport-overflow",
        "text-line-overlap",
        "text-line-height-tight",
        "text-self-overlap",
        "title-wrap-too-deep",
        "subtitle-wrap-too-deep",
        "title-wrap-deep",
        "subtitle-wrap-deep",
        "text-clearance-tight",
        "text-clipped",
        "container-overflow",
        "text-overflow",
    }:
        hint = (
            f"{label}: text layout is unsafe ({issue.kind}). Cut copy, split the slide, or move dense details into notes before CSS or image polish."
        )
        return _repair_action(deck, issue, "reduce-text-density", "", "keep current crop only if proof remains readable", "cut copy, split slide, or move dense details into notes", hint)
    if issue.kind in {"missing-proof", "missing-proof-image", "image-not-loaded", "image-overflow", "image-object-fit-unsupported", "untyped-image"}:
        hint = (
            f"{label}: image insertion failed ({issue.kind}). Verify the image path, crop bounds, and layout intent before any taste review."
        )
        return _repair_action(deck, issue, "fix-image-insertion", "", "verify crop bounds after image loads", "verify path and layout intent", hint)
    if issue.kind in {"callout-outside-image", "callout-outside-source-image"}:
        hint = (
            f"{label}: callout pin is not on a safe rendered image region ({issue.kind}). Move the pin onto visible source pixels "
            "after the crop and slot aspect ratio are final, or remove the annotation."
        )
        return _repair_action(deck, issue, "separate-or-reduce-callouts", "", "move pins onto visible source pixels", "move/delete unsafe callout pins", hint)
    if issue.kind == "pseudo-overlay-front":
        hint = (
            f"{label}: a visual grammar pseudo layer is above content ({issue.detail}). Move the pseudo layer behind content "
            "with non-positive z-index, or replace it with a real audited background element."
        )
        return _repair_action(deck, issue, "lower-pseudo-overlay", "", "keep source crops stable", "lower/remove foreground pseudo overlay", hint)
    if issue.kind in {"cadence-low-variety", "cadence-no-proof-surface", "cadence-repetition"}:
        hint = (
            f"{label}: deck cadence is unsafe ({issue.kind}). Add a proof/artifact slide, change layout intents, or split repeated "
            "sections so the deck has at least three real composition cadences."
        )
        return _repair_action(deck, issue, "revise-deck-cadence", "", "select crops for the added proof/artifact slide", "add proof surface or diversify composition sequence", hint)
    if issue.kind.startswith("audit-") or issue.kind.startswith("screenshot-"):
        hint = f"{label}: browser preview infrastructure failed ({issue.kind}). Re-run strict export with Chrome/Edge available before judging the deck."
        return _repair_action(deck, issue, "rerun-layout-audit", "", "keep crops unchanged until audit succeeds", "rerun strict export with browser audit", hint)
    return None


def repair_hint_for_issue(deck: Deck | None, issue: LayoutIssue) -> str | None:
    action = repair_action_for_issue(deck, issue)
    return action.hint if action else None


def repair_actions_for_report(deck: Deck | None, report_path: Path, limit: int = 12) -> tuple[RepairAction, ...]:
    actions: list[RepairAction] = []
    seen: set[tuple[int | None, str, str]] = set()
    for issue in layout_report_issues(report_path):
        action = repair_action_for_issue(deck, issue)
        if not action:
            continue
        key = (action.slide, action.issue_kind, action.hint)
        if key in seen:
            continue
        seen.add(key)
        actions.append(action)
        if len(actions) >= limit:
            break
    return tuple(actions)


def repair_hints_for_report(deck: Deck | None, report_path: Path, limit: int = 6) -> tuple[str, ...]:
    hints: list[str] = []
    seen: set[str] = set()
    for issue in layout_report_issues(report_path):
        hint = repair_hint_for_issue(deck, issue)
        if not hint or hint in seen:
            continue
        seen.add(hint)
        hints.append(hint)
        if len(hints) >= limit:
            break
    return tuple(hints)


def compare_row(grammar: str, variant_dir: Path, layout_errors: int, report_path: Path, deck: Deck | None = None) -> GrammarComparisonRow:
    summary = layout_report_summary(report_path)
    errors = max(layout_errors, summary.blocking_errors)
    if errors != summary.blocking_errors:
        summary = LayoutReportSummary(
            blocking_errors=errors,
            warnings=summary.warnings,
            average_fill=summary.average_fill,
            average_useful_fill=summary.average_useful_fill,
            sequence=summary.sequence,
            distinct_cadences=summary.distinct_cadences,
            warning_counts=summary.warning_counts,
        )
    score = score_grammar_variant(grammar, summary)
    repair_actions = repair_actions_for_report(deck, report_path)
    return GrammarComparisonRow(
        grammar=grammar,
        variant_dir=variant_dir,
        errors=errors,
        warnings=summary.warnings,
        warning_counts=summary.warning_counts,
        average_fill=summary.average_fill,
        average_useful_fill=summary.average_useful_fill,
        sequence=summary.sequence,
        distinct_cadences=summary.distinct_cadences,
        score=score,
        recommendation=recommendation_for_variant(summary, score),
        use_case=GRAMMAR_USE_CASES.get(grammar, "general exploration"),
        repair_hints=tuple(action.hint for action in repair_actions[:6]),
        repair_actions=repair_actions,
    )


def has_image_revision_warning(row: GrammarComparisonRow) -> bool:
    warning_map = dict(row.warning_counts)
    return bool(
        warning_map.get("proof-image-small")
        or warning_map.get("proof-image-rendered-small")
        or warning_map.get("proof-small")
        or warning_map.get("artifact-small")
        or warning_map.get("artifact-image-small")
        or warning_map.get("artifact-image-rendered-small")
        or warning_map.get("artifact-role-underfeatured")
        or any("letterboxed" in kind for kind in warning_map)
        or warning_map.get("callout-overlap")
        or warning_map.get("proof-caption-missing")
        or warning_map.get("proof-caption-generic")
        or warning_map.get("artifact-caption-generic")
        or warning_map.get("caption-text-too-small")
        or warning_map.get("caption-contrast-low")
        or warning_map.get("label-contrast-low")
        or warning_map.get("title-wrap-deep")
        or warning_map.get("subtitle-wrap-deep")
        or warning_map.get("content-underfilled")
        or warning_map.get("useful-fill-low")
        or warning_map.get("decorative-image-too-small")
    )


def ready_for_shortlist(row: GrammarComparisonRow) -> bool:
    warning_kinds = set(dict(row.warning_counts))
    return (
        row.errors == 0
        and row.score >= 92
        and not has_image_revision_warning(row)
        and not (warning_kinds & AUDIT_INFRA_WARNINGS)
    )


def recommended_rows(rows: list[GrammarComparisonRow], limit: int = 5) -> list[GrammarComparisonRow]:
    selected: list[GrammarComparisonRow] = []
    seen_sequences: set[str] = set()
    seen_style_families: set[str] = set()
    seen_composition_families: set[str] = set()
    candidates = sorted(
        [row for row in rows if ready_for_shortlist(row)],
        key=lambda row: (-row.score, -GRAMMAR_TASTE_BONUS.get(row.grammar, 0), row.warnings, row.grammar),
    )
    for row in candidates:
        if row.sequence in seen_sequences:
            continue
        style_family = grammar_style_family(row.grammar)
        composition_family = composition_family_signature(row.sequence)
        if style_family in seen_style_families or composition_family in seen_composition_families:
            continue
        selected.append(row)
        seen_sequences.add(row.sequence)
        seen_style_families.add(style_family)
        seen_composition_families.add(composition_family)
        if len(selected) >= limit:
            return selected
    for row in candidates:
        if row in selected:
            continue
        if row.sequence in seen_sequences:
            continue
        selected.append(row)
        seen_sequences.add(row.sequence)
        if len(selected) >= limit:
            return selected
    return selected


def _primary_direction_for_grammar(grammar: str) -> DesignDirection | None:
    normalized = grammar.strip().lower().replace("_", "-")
    directions = directions_for_grammar(normalized)
    if not directions:
        return None
    for direction in directions:
        if direction.key == normalized:
            return direction
    for direction in directions:
        if direction.grammars and direction.grammars[0] == normalized:
            return direction
    return directions[0]


def _direction_rows(rows: list[GrammarComparisonRow], limit: int = 3) -> list[tuple[GrammarComparisonRow, DesignDirection]]:
    selected: list[tuple[GrammarComparisonRow, DesignDirection]] = []
    seen_direction_keys: set[str] = set()
    seen_schools: set[str] = set()
    pools = [
        [row for row in recommended_rows(rows, limit=8)],
        sorted(
            [row for row in rows if row.errors == 0 and not has_image_revision_warning(row)],
            key=lambda row: (-row.score, row.warnings, row.grammar),
        ),
        sorted([row for row in rows if row.errors == 0], key=lambda row: (-row.score, row.warnings, row.grammar)),
    ]
    for pool in pools:
        for row in pool:
            direction = _primary_direction_for_grammar(row.grammar)
            if not direction or direction.key in seen_direction_keys:
                continue
            if direction.school in seen_schools and len(selected) < limit - 1:
                continue
            selected.append((row, direction))
            seen_direction_keys.add(direction.key)
            seen_schools.add(direction.school)
            if len(selected) >= limit:
                return selected
    return selected


def write_design_direction_report(rows: list[GrammarComparisonRow], output_path: Path, deck: Deck) -> Path:
    selected = _direction_rows(rows, limit=3)
    lines = [
        "# Design Directions",
        "",
        f"- Deck: `{deck.deck_id}`",
        f"- Direction library size: {len(DESIGN_DIRECTIONS)}",
        "- References: [JS Design high-sense cases](https://js.design/special/article/highsense-page-design.html), "
        "[PRISM academic homepage](https://github.com/xyjoey/PRISM), "
        "[Huashu Design](https://github.com/alchaincyf/huashu-design), "
        "[Beautiful HTML Templates](https://github.com/zarazhangrui/beautiful-html-templates)",
        "",
        "This report is the design-direction layer above raw grammar scores. It asks the agent to choose a school of layout, evidence treatment, density, and anti-AI discipline before generating or repairing slides.",
        "",
        "## Recommended Direction Set",
        "",
    ]
    if selected:
        lines.extend(
            [
                "| Role | Direction | Grammar | School | Related schools | Why it fits | Output |",
                "|---|---|---|---|---|---|---|",
            ]
        )
        roles = ("Safe academic base", "Proof-forward art direction", "Bold reset / alternate")
        for idx, (row, direction) in enumerate(selected):
            role = roles[idx] if idx < len(roles) else "Alternate"
            related_schools = ", ".join(
                dict.fromkeys(related.school for related in directions_for_grammar(row.grammar))
            )
            lines.append(
                f"| {role} | {direction.name} | `{row.grammar}` | {direction.school} | {related_schools} | "
                f"{direction.use_when} | `{row.variant_dir}` |"
            )
    else:
        lines.append("No clean direction was selected. Fix blocking layout errors and image-revision warnings first.")
    lines.extend(
        [
            "",
            "## Agent Selection Protocol",
            "",
            "1. Verify facts and collect assets before design. For public people or projects, prefer homepage, paper, repo, benchmark, product UI, or real figure crops over decorative portraits.",
            "2. Choose three directions, not three palettes: one safe academic base, one proof-forward editorial route, and one bold reset.",
            "3. Render a two-page showcase for each direction: cover plus the strongest evidence page. Do not build the full deck before the showcase passes.",
            "4. Run `compare-grammars --fail-on-layout`; reject any overlap, underfilled, image-scale, caption, or source-context warning before judging taste.",
            "5. Apply Huashu-style 5D critique: philosophy alignment, visual hierarchy, detail craft, function, and innovation. Passing DOM gates is necessary but not sufficient.",
            "",
            "## Anti-AI Surface Ban",
            "",
            "- No purple-blue gradient wallpaper, glass cards, floating blobs, fake dashboards, random 3D objects, or stock-like atmospheric images.",
            "- No palette-only variation. A new direction must change grid logic, proof scale, caption treatment, density rhythm, or slide cadence.",
            "- No empty half-page unless it creates reading hierarchy. If a slide feels empty, add source rows, a larger proof plate, a ledger, or split the story.",
            "- No screenshot as decoration. If the image cannot be captioned with the exact claim it proves, remove it.",
            "",
            "## 20+ Direction Library",
            "",
            "| Direction | School | Candidate grammars | Use when | Density rule | Evidence rule | Anti-AI rule |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for direction in DESIGN_DIRECTIONS:
        grammars = ", ".join(f"`{grammar}`" for grammar in direction.grammars)
        lines.append(
            f"| {direction.name} | {direction.school} | {grammars} | {direction.use_when} | "
            f"{direction.density_rule} | {direction.evidence_rule} | {direction.anti_ai_rule} |"
        )
    lines.extend(
        [
            "",
            "## 5D Critique Checklist",
            "",
            "- Philosophy alignment: the deck actually follows the chosen school, not just its colors.",
            "- Visual hierarchy: one slide has one visual protagonist and one judgment.",
            "- Detail craft: captions, source rails, rules, and crops look deliberately placed.",
            "- Function: proof remains readable at 1920x1080 and survives PPTX screenshot export.",
            "- Innovation: at least one slide type breaks the default text-plus-screenshot pattern without becoming decorative.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def revision_rows(rows: list[GrammarComparisonRow], limit: int = 5) -> list[GrammarComparisonRow]:
    candidates = [
        row
        for row in rows
        if row.errors == 0 and has_image_revision_warning(row)
    ]
    return sorted(candidates, key=lambda row: (-row.score, row.warnings, row.grammar))[:limit]


def comparison_overview(contact_sheets: tuple[tuple[str, Path], ...], output_path: Path) -> Path | None:
    panels: list[tuple[str, Image.Image]] = []
    for label, path in contact_sheets:
        if not path.exists():
            continue
        image = Image.open(path).convert("RGB")
        width = 1500
        height = round(image.height * width / image.width)
        panels.append((label, image.resize((width, height), Image.LANCZOS)))
    if not panels:
        return None
    pad = 36
    label_h = 38
    width = max(image.width for _, image in panels) + pad * 2
    height = pad + sum(label_h + image.height + pad for _, image in panels)
    overview = Image.new("RGB", (width, height), (244, 241, 234))
    draw = ImageDraw.Draw(overview)
    y = pad
    for label, image in panels:
        draw.text((pad, y), label, fill=(24, 32, 42))
        y += label_h
        overview.paste(image, (pad, y))
        y += image.height + pad
    output_path.parent.mkdir(parents=True, exist_ok=True)
    overview.save(output_path)
    return output_path


def write_repair_manifest(rows: list[GrammarComparisonRow], output_path: Path) -> Path:
    data = {
        "variants": [
            {
                "grammar": row.grammar,
                "score": row.score,
                "recommendation": row.recommendation,
                "blocking_errors": row.errors,
                "warnings": dict(row.warning_counts),
                "average_fill": row.average_fill,
                "average_useful_fill": row.average_useful_fill,
                "composition_sequence": row.sequence,
                "output": str(row.variant_dir),
                "repair_hints": list(row.repair_hints),
                "repair_actions": [asdict(action) for action in row.repair_actions],
            }
            for row in rows
        ]
    }
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


def write_deck_repair_plan(manifest_path: Path, output_path: Path) -> Path:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    variants = list(data.get("variants", []))
    ready = [item for item in variants if str(item.get("recommendation", "")).startswith("shortlist")]
    queued = [item for item in variants if item.get("repair_actions")]
    lines = [
        "# Deck Repair Plan",
        "",
        f"- Source manifest: `{manifest_path}`",
        f"- Variants: {len(variants)}",
        "",
        "## Repair Order",
        "",
        "1. Prefer a clean `shortlist` variant with no repair actions.",
        "2. If a variant has decorative cover warnings, adjust or remove the cover image before treating it as delivery-ready.",
        "3. Treat `Image Revision Queue` variants as repair candidates, not accepted designs.",
        "4. After edits, rerun `compare-grammars --fail-on-layout` and inspect the contact sheet.",
        "",
        "## Shortlist",
        "",
    ]
    if ready:
        for item in ready:
            warnings = item.get("warnings") or {}
            warn_text = ", ".join(f"{key} x{value}" for key, value in warnings.items()) or "none"
            lines.append(f"- `{item.get('grammar')}` score {item.get('score')}: {item.get('recommendation')} (warnings: {warn_text})")
    else:
        lines.append("- No ready shortlist variant. Fix blocking or image-revision issues first.")
    lines.extend(["", "## Action Queue", ""])
    if not queued:
        lines.append("- No repair actions found.")
    for item in queued:
        lines.append(f"### `{item.get('grammar')}`")
        for action in item.get("repair_actions", []):
            slide = action.get("slide")
            title = action.get("slide_title") or "untitled"
            layout = action.get("current_layout") or "grammar default"
            image = action.get("current_image") or "none"
            crop = action.get("current_crop")
            crop_text = json.dumps(crop, ensure_ascii=False) if crop else "none"
            lines.extend(
                [
                    f"- Slide {slide} `{title}`",
                    f"  - Issue: `{action.get('issue_kind')}` on `{action.get('target')}` ({action.get('detail')})",
                    f"  - Current: layout `{layout}`, image `{image}`, crop `{crop_text}`",
                    f"  - Action: `{action.get('suggested_action')}`",
                    f"  - Layout target: `{action.get('suggested_layout') or 'keep / grammar-specific'}`",
                    f"  - Crop strategy: {action.get('crop_strategy')}",
                    f"  - Content strategy: {action.get('content_strategy')}",
                ]
            )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def repair_plan_only(manifest: str | None, out: str) -> None:
    if not manifest:
        raise SystemExit("repair-plan requires --manifest <GRAMMAR_REPAIR_HINTS.json>.")
    manifest_path = Path(manifest).resolve()
    output_path = Path(out).resolve()
    if output_path.suffix.lower() != ".md":
        output_path = output_path / "DECK_REPAIR_PLAN.md"
    report = write_deck_repair_plan(manifest_path, output_path)
    print(f"Repair plan: {report}")


def _variant_score(item: dict[str, Any]) -> tuple[int, int, int, str]:
    warnings = item.get("warnings") or {}
    warning_total = sum(int(value) for value in warnings.values())
    zero_error = 1 if int(item.get("blocking_errors") or 0) == 0 else 0
    return (zero_error, int(item.get("score") or 0), -warning_total, str(item.get("grammar") or ""))


def _selected_repair_variant(data: dict[str, Any], visual_grammar: str | None) -> dict[str, Any]:
    variants = [item for item in data.get("variants", []) if isinstance(item, dict)]
    if not variants:
        raise SystemExit("repair-draft manifest has no variants.")
    if visual_grammar:
        wanted = visual_grammar.strip().lower().replace("_", "-")
        for item in variants:
            if str(item.get("grammar", "")).strip().lower() == wanted:
                return item
        raise SystemExit(f"repair-draft could not find grammar `{wanted}` in manifest.")
    clean_shortlist = [
        item
        for item in variants
        if str(item.get("recommendation", "")).startswith("shortlist")
        and int(item.get("blocking_errors") or 0) == 0
        and not item.get("repair_actions")
    ]
    if clean_shortlist:
        return sorted(clean_shortlist, key=_variant_score, reverse=True)[0]
    with_actions = [item for item in variants if item.get("repair_actions")]
    return sorted(with_actions or variants, key=_variant_score, reverse=True)[0]


def _slide_maps(data: dict[str, Any]) -> list[dict[str, Any]]:
    slides = data.get("slides")
    if not isinstance(slides, list):
        raise SystemExit("repair-draft requires a deck.yaml with a slides list.")
    return [slide for slide in slides if isinstance(slide, dict)]


def _can_apply_layout(slide: dict[str, Any], layout: str) -> bool:
    kind = str(slide.get("kind", ""))
    if layout.startswith("proof-"):
        return kind in {"evidence", "loop", "product"}
    if layout.startswith("artifact-"):
        return kind not in {"cover", "map", "matrix", "evidence", "loop", "product"}
    return bool(layout)


def _default_crop() -> dict[str, float]:
    return {"x": 0.06, "y": 0.06, "w": 0.88, "h": 0.88}


def _crop_from_mapping(value: Any) -> dict[str, float]:
    if not isinstance(value, dict):
        return _default_crop()
    return {
        "x": float(value.get("x", 0.0)),
        "y": float(value.get("y", 0.0)),
        "w": float(value.get("w", 1.0)),
        "h": float(value.get("h", 1.0)),
    }


def _tightened_crop(crop: dict[str, float], factor: float = 0.86) -> dict[str, float]:
    width = min(1.0, max(0.08, float(crop.get("w", 1.0))))
    height = min(1.0, max(0.08, float(crop.get("h", 1.0))))
    x = min(max(0.0, float(crop.get("x", 0.0))), max(0.0, 1.0 - width))
    y = min(max(0.0, float(crop.get("y", 0.0))), max(0.0, 1.0 - height))
    center_x = x + width / 2
    center_y = y + height / 2
    new_w = min(1.0, max(0.08, width * factor))
    new_h = min(1.0, max(0.08, height * factor))
    new_x = min(max(0.0, center_x - new_w / 2), 1.0 - new_w)
    new_y = min(max(0.0, center_y - new_h / 2), 1.0 - new_h)
    return {
        "x": round(new_x, 3),
        "y": round(new_y, 3),
        "w": round(new_w, 3),
        "h": round(new_h, 3),
    }


def _ensure_evidence(slide: dict[str, Any]) -> dict[str, Any]:
    evidence = slide.get("evidence")
    if not isinstance(evidence, dict):
        evidence = {}
        slide["evidence"] = evidence
    if not evidence.get("image") and slide.get("image"):
        evidence["image"] = slide.get("image")
    return evidence


def _apply_repair_action(slides: list[dict[str, Any]], action: dict[str, Any]) -> tuple[list[str], list[str]]:
    applied: list[str] = []
    deferred: list[str] = []
    slide_number = action.get("slide")
    if not isinstance(slide_number, int) or slide_number < 1 or slide_number > len(slides):
        deferred.append(f"Deck-level `{action.get('issue_kind')}` needs manual review.")
        return applied, deferred

    slide = slides[slide_number - 1]
    title = str(slide.get("title", "untitled"))
    issue_kind = str(action.get("issue_kind", "unknown"))
    suggested_action = str(action.get("suggested_action", ""))
    suggested_layout = str(action.get("suggested_layout", "") or "")

    if suggested_layout and suggested_action in {
        "set-layout",
        "set-layout-and-tighten-crop",
        "tighten-crop",
        "tighten-crop-or-split",
        "resolve-text-image-conflict",
    }:
        if _can_apply_layout(slide, suggested_layout):
            old_layout = str(slide.get("layout", "") or "grammar default")
            slide["layout"] = suggested_layout
            applied.append(f"Slide {slide_number} `{title}`: layout `{old_layout}` -> `{suggested_layout}`.")
        else:
            deferred.append(f"Slide {slide_number} `{title}`: `{suggested_layout}` is not valid for kind `{slide.get('kind')}`; split or rewrite manually.")

    if suggested_action in {"set-layout-and-tighten-crop", "tighten-crop", "tighten-crop-or-split"}:
        evidence = _ensure_evidence(slide)
        if evidence.get("image") or slide.get("image"):
            old_crop = _crop_from_mapping(evidence.get("crop"))
            new_crop = _tightened_crop(old_crop)
            evidence["crop"] = new_crop
            applied.append(f"Slide {slide_number} `{title}`: tightened evidence crop for `{issue_kind}` from {old_crop} to {new_crop}.")
        else:
            deferred.append(f"Slide {slide_number} `{title}`: `{issue_kind}` needs an image before crop repair can be applied.")
    elif suggested_action == "match-crop-to-slot":
        deferred.append(f"Slide {slide_number} `{title}`: `{issue_kind}` needs human crop/aspect selection; match crop to the selected grammar slot.")
    elif suggested_action == "enlarge-or-remove-decoration":
        deferred.append(f"Slide {slide_number} `{title}`: cover identity image is too small; enlarge/recrop or remove after visual review.")
    elif suggested_action == "promote-to-proof-or-split":
        deferred.append(f"Slide {slide_number} `{title}`: source should become a dedicated proof slide or be split; no automatic kind rewrite applied.")
    elif suggested_action == "split-or-change-grammar":
        deferred.append(f"Slide {slide_number} `{title}`: `{issue_kind}` needs a larger grammar slot, shorter side content, or a split slide; no crop-only repair applied.")
    elif suggested_action in {"resolve-text-image-conflict", "reduce-text-density"}:
        deferred.append(f"Slide {slide_number} `{title}`: shorten copy or split the slide; no automatic text deletion applied.")
    elif suggested_action == "fix-image-insertion":
        deferred.append(f"Slide {slide_number} `{title}`: verify image path, crop bounds, and source file before rerendering.")
    elif suggested_action == "separate-or-reduce-callouts":
        deferred.append(f"Slide {slide_number} `{title}`: move/delete overlapping callout pins by hand; no automatic pin rewrite applied.")
    elif suggested_action == "increase-slide-density":
        deferred.append(f"Slide {slide_number} `{title}`: slide is too empty; choose a fuller composition, larger proof/artifact slot, or stronger module.")
    elif suggested_action == "lower-pseudo-overlay":
        deferred.append(f"Slide {slide_number} `{title}`: lower or remove the foreground pseudo overlay in the active grammar CSS.")
    elif suggested_action == "revise-deck-cadence":
        deferred.append(f"Slide {slide_number} `{title}`: revise layout intents or add a proof/artifact slide to diversify the deck cadence.")
    elif suggested_action == "rerun-layout-audit":
        deferred.append(f"Slide {slide_number} `{title}`: rerun strict export with Chrome audit available before visual review.")

    return applied, deferred


def write_repair_draft(deck_path: Path, manifest_path: Path, output_dir: Path, visual_grammar: str | None = None) -> tuple[Path, Path]:
    data = yaml.safe_load(deck_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("repair-draft could not parse deck.yaml as a mapping.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise SystemExit("repair-draft could not parse GRAMMAR_REPAIR_HINTS.json.")
    variant = _selected_repair_variant(manifest, visual_grammar)
    grammar = str(variant.get("grammar") or visual_grammar or data.get("visual_grammar") or "editorial-profile")
    data["visual_grammar"] = grammar
    data["assets_dir"] = str(resolve_assets_dir(load_deck(deck_path)).resolve())
    slides = _slide_maps(data)
    actions = [action for action in variant.get("repair_actions", []) if isinstance(action, dict)]

    applied: list[str] = []
    deferred: list[str] = []
    for action in actions:
        action_applied, action_deferred = _apply_repair_action(slides, action)
        applied.extend(action_applied)
        deferred.extend(action_deferred)

    output_dir.mkdir(parents=True, exist_ok=True)
    draft_path = output_dir / "deck.repair.yaml"
    draft_path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    lines = [
        "# Deck Repair Draft",
        "",
        f"- Source deck: `{deck_path}`",
        f"- Source manifest: `{manifest_path}`",
        f"- Selected grammar: `{grammar}`",
        f"- Draft deck: `{draft_path}`",
        f"- Repair actions read: {len(actions)}",
        "",
        "## Applied Edits",
        "",
    ]
    lines.extend(f"- {item}" for item in applied) if applied else lines.append("- None. This draft only pins the selected grammar.")
    lines.extend(["", "## Deferred Manual Edits", ""])
    lines.extend(f"- {item}" for item in deferred) if deferred else lines.append("- None.")
    lines.extend(
        [
            "",
            "## Next Validation",
            "",
            "```bash",
            f"uv run academic-deck html-pptx --deck {draft_path} --out {output_dir / 'render'} --visual-grammar {grammar} --fail-on-layout",
            "```",
        ]
    )
    report_path = output_dir / "DECK_REPAIR_DRAFT.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return draft_path, report_path


def repair_draft_only(deck_path: str | None, manifest: str | None, out: str, visual_grammar: str | None) -> None:
    if not deck_path:
        raise SystemExit("repair-draft requires --deck <deck.yaml>.")
    if not manifest:
        raise SystemExit("repair-draft requires --manifest <GRAMMAR_REPAIR_HINTS.json>.")
    draft, report = write_repair_draft(Path(deck_path).resolve(), Path(manifest).resolve(), Path(out).resolve(), visual_grammar)
    print(f"Repair draft deck: {draft}")
    print(f"Repair draft report: {report}")


def compare_grammars(
    deck_path: str | None,
    out: str,
    width: int,
    height: int,
    chrome: str | None,
    grammars_value: str | None,
    fail_on_layout: bool = False,
) -> None:
    source_deck = load_deck(deck_path)
    output_dir = Path(out).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    source_quality_issues = check_deck(source_deck)
    source_quality_errors = sum(1 for issue in source_quality_issues if issue.level == "error")
    source_quality_report = write_quality_report(output_dir / "quality-report.md", source_deck, source_quality_issues)
    if source_quality_errors:
        raise SystemExit(f"Quality check failed with {source_quality_errors} blocking issue(s). See {source_quality_report}.")
    rows: list[GrammarComparisonRow] = []
    contact_sheets: list[tuple[str, Path]] = []
    for grammar in parse_grammar_list(grammars_value):
        deck = with_visual_grammar(source_deck, grammar)
        variant_dir = output_dir / grammar
        write_quality_report(variant_dir / "quality-report.md", deck, check_deck(deck))
        write_evidence_report(variant_dir / "evidence-report.md", deck)
        try:
            result = export_html_image_pptx(deck, variant_dir, width=width, height=height, chrome_path=chrome)
        except subprocess.TimeoutExpired as exc:
            report_path, layout_errors = write_layout_audit_report(
                variant_dir / "layout-audit-report.md",
                (
                    {
                        "slide": None,
                        "issues": [
                            {
                                "level": "error",
                                "type": "screenshot-timeout",
                                "target": "chrome",
                                "detail": f"Chrome screenshot command timed out after {exc.timeout}s.",
                            }
                        ],
                    },
                ),
            )
            write_report(variant_dir / "judge-report.md", [judge_route(f"HTML-image PPTX / {grammar}", [])])
            rows.append(compare_row(grammar, variant_dir, layout_errors, report_path, source_deck))
            continue
        except (subprocess.CalledProcessError, RuntimeError) as exc:
            detail = str(exc)
            report_path, layout_errors = write_layout_audit_report(
                variant_dir / "layout-audit-report.md",
                (
                    {
                        "slide": None,
                        "issues": [
                            {
                                "level": "error",
                                "type": "screenshot-failed",
                                "target": "chrome",
                                "detail": detail[:220],
                            }
                        ],
                    },
                ),
            )
            write_report(variant_dir / "judge-report.md", [judge_route(f"HTML-image PPTX / {grammar}", [])])
            rows.append(compare_row(grammar, variant_dir, layout_errors, report_path, source_deck))
            continue
        reports = [judge_route(f"HTML-image PPTX / {grammar}", list(result.images))]
        write_report(variant_dir / "judge-report.md", reports)
        rows.append(compare_row(grammar, variant_dir, result.layout_errors, result.layout_report_path, source_deck))
        contact_sheets.append((grammar, result.contact_sheet_path))
    overview = comparison_overview(tuple(contact_sheets), output_dir / "grammar-comparison-overview.png")
    shortlist = recommended_rows(rows)
    revisions = revision_rows(rows)
    design_direction_report = write_design_direction_report(rows, output_dir / "DESIGN_DIRECTIONS.md", source_deck)
    warning_totals: dict[str, int] = {}
    for row in rows:
        for kind, count in row.warning_counts:
            warning_totals[kind] = warning_totals.get(kind, 0) + count
    lines = [
        "# Grammar Comparison",
        "",
        f"- Deck: `{source_deck.deck_id}`",
        f"- Variants: {len(rows)}",
        f"- Overview: `{overview}`" if overview else "- Overview: unavailable",
        f"- Design directions: `{design_direction_report}`",
        "",
        "## Recommended Shortlist",
        "",
    ]
    if shortlist:
        lines.extend(
            [
                "| Rank | Grammar | Score | Recommendation | Best use | Warnings | Output |",
                "|---:|---|---:|---|---|---|---|",
            ]
        )
        for idx, row in enumerate(shortlist, start=1):
            lines.append(
                f"| {idx} | `{row.grammar}` | {row.score} | {row.recommendation} | {row.use_case} | "
                f"{format_warning_counts(row.warning_counts, row.warnings)} | `{row.variant_dir}` |"
            )
        lines.extend(
            [
                "",
                "## Shortlist Diversity",
                "",
                "| Grammar | Style family | Composition family |",
                "|---|---|---|",
            ]
        )
        for row in shortlist:
            lines.append(
                f"| `{row.grammar}` | `{grammar_style_family(row.grammar)}` | "
                f"`{composition_family_signature(row.sequence)}` |"
            )
    else:
        if any(row.errors == 0 for row in rows):
            lines.append("No ready grammar variant was found. Fix image revision warnings or audit infrastructure warnings first.")
        else:
            lines.append("No zero-error grammar variant was found. Fix blocking layout issues first.")
    if revisions:
        lines.extend(
            [
                "",
                "## Image Revision Queue",
                "",
                "| Grammar | Score | Issue | Best use | Warnings | Output |",
                "|---|---:|---|---|---|---|",
            ]
        )
        for row in revisions:
            lines.append(
                f"| `{row.grammar}` | {row.score} | {row.recommendation} | {row.use_case} | "
                f"{format_warning_counts(row.warning_counts, row.warnings)} | `{row.variant_dir}` |"
            )
    hint_rows = [row for row in rows if row.repair_hints]
    if hint_rows:
        lines.extend(
            [
                "",
                "## Repair Hints",
                "",
            ]
        )
        for row in sorted(hint_rows, key=lambda item: (item.errors, -item.score, item.grammar)):
            lines.append(f"### `{row.grammar}`")
            for hint in row.repair_hints:
                lines.append(f"- {hint}")
    lines.extend(
        [
            "",
            "## Warning Totals",
            "",
        ]
    )
    if warning_totals:
        for kind, count in sorted(warning_totals.items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"- `{kind}`: {count}")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## All Variants",
            "",
            "| Grammar | Score | Recommendation | Blocking errors | Warnings | Avg fill | Avg useful | Composition sequence | Output |",
            "|---|---:|---|---:|---|---:|---:|---|---|",
        ]
    )
    total_errors = 0
    total_strict_warnings = 0
    for row in sorted(rows, key=lambda item: (item.errors, -item.score, item.warnings, item.grammar)):
        total_errors += row.errors
        total_strict_warnings += _strict_warning_total(row.warning_counts)
        lines.append(
            f"| `{row.grammar}` | {row.score} | {row.recommendation} | {row.errors} | "
            f"{format_warning_counts(row.warning_counts, row.warnings)} | {row.average_fill} | {row.average_useful_fill} | "
            f"`{row.sequence}` | `{row.variant_dir}` |"
        )
    lines.extend(
        [
            "",
            "## Reading Order",
            "- Start with the recommended shortlist, then inspect the stacked overview and each variant's contact sheet.",
            "- Read `DESIGN_DIRECTIONS.md` before picking a winner; choose a direction family, not a color variant.",
            "- Keep grammars with distinct composition sequences, not merely different colors.",
            "- Treat any blocking error as a renderer/content issue before judging taste.",
            "- In strict export, proof/artifact scale, rendered source pixel size, callout overlap, underfilled-slide, useful-fill, and source-heavy artifact warnings are also delivery blockers.",
            "- `proof-image-small`, `artifact-small`, and letterbox warnings lower the score because the inserted image is not carrying enough proof.",
            "- `screenshot-timeout` or `screenshot-failed` rows are browser infrastructure failures; rerun those variants before judging taste.",
            "- `decorative-image-too-small` is a strict cover-crop warning in delivery mode; enlarge, crop, or remove the cover image before final export.",
            "- Prefer variants whose proof surfaces stay readable without making all slides use the same evidence layout.",
        ]
    )
    report = output_dir / "GRAMMAR_COMPARISON.md"
    report.write_text("\n".join(lines), encoding="utf-8")
    repair_manifest = write_repair_manifest(rows, output_dir / "GRAMMAR_REPAIR_HINTS.json")
    print(f"Grammar comparison: {report}")
    print(f"Design directions: {design_direction_report}")
    print(f"Repair hints: {repair_manifest}")
    if overview:
        print(f"Overview: {overview}")
    if fail_on_layout and not shortlist:
        if total_errors:
            raise SystemExit(f"No ready grammar variant found; comparison produced {total_errors} blocking layout issue(s).")
        if total_strict_warnings:
            raise SystemExit(f"No ready grammar variant found; comparison produced {total_strict_warnings} strict image/density warning gate(s).")


def package_only(deck_path: str | None, out: str) -> None:
    if deck_path is None:
        raise SystemExit("package requires --deck so the source deck.yaml can be copied.")
    deck = load_deck(deck_path)
    package_dir = package_build(Path(deck_path).resolve(), deck, Path(out).resolve())
    print(f"Package: {package_dir}")


def ingest_only(source: str | None, out: str) -> None:
    if not source:
        raise SystemExit("ingest requires --source <file-or-folder>.")
    manifest = write_source_manifest(Path(source), Path(out).resolve())
    print(f"Source manifest: {manifest}")


def template_shortlist_only(brief: str | None, out: str, limit: int = 5) -> None:
    brief_text = (brief or "").strip()
    if not brief_text:
        raise SystemExit("template-shortlist requires --brief <occasion / mood / content>.")
    output_dir = Path(out).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    candidates = beautiful_template_candidates(brief_text, limit=limit)
    template_source = (
        f"`{BEAUTIFUL_TEMPLATE_INDEX}`"
        if BEAUTIFUL_TEMPLATE_INDEX.exists()
        else "built-in shortlist fallback; clone zarazhangrui/beautiful-html-templates into `vendor/beautiful-html-templates` for the full index"
    )
    lines = [
        "# Beautiful HTML Template Shortlist",
        "",
        f"- Brief: {brief_text}",
        f"- Source index: {template_source}",
        "- Workflow: use this as a tone/source reference, then map it into an Academic Deck Compiler grammar or clone the template for a bespoke HTML route.",
        "",
        "| Rank | Template | Score | Formality | Density | Scheme | Why matched |",
        "|---:|---|---:|---|---|---|---|",
    ]
    for idx, candidate in enumerate(candidates, start=1):
        lines.append(
            f"| {idx} | `{candidate.slug}` / {candidate.name} | {candidate.score} | "
            f"{candidate.formality} | {candidate.density} | {candidate.scheme} | {candidate.rationale} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
        ]
    )
    for candidate in candidates:
        template_dir = BEAUTIFUL_TEMPLATE_INDEX.parent / "templates" / candidate.slug
        lines.extend(
            [
                f"### `{candidate.slug}`",
                f"- Tagline: {candidate.tagline}",
                f"- Best for: {candidate.best_for}",
                f"- Avoid for: {candidate.avoid_for}",
                f"- Local template: `{template_dir}`",
                "",
            ]
        )
    report = output_dir / "BEAUTIFUL_TEMPLATE_SHORTLIST.md"
    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"Beautiful template shortlist: {report}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and compare academic or technical slide decks.")
    parser.add_argument("command", choices=["build", "html-pptx", "compare-grammars", "template-shortlist", "repair-plan", "repair-draft", "init", "ingest", "check", "evidence", "package", "doctor"], nargs="?", default="build")
    parser.add_argument("--out", default=str(OUTPUT_DIR / "deck-build"))
    parser.add_argument("--deck", help="Path to deck.yaml. Defaults to the neutral starter deck.")
    parser.add_argument("--source", help="File or folder to scan into a source manifest for a future deck.")
    parser.add_argument("--brief", help="Occasion, mood, and content hints for template-shortlist.")
    parser.add_argument("--limit", type=int, default=5, help="Number of template candidates for template-shortlist.")
    parser.add_argument("--manifest", help="GRAMMAR_REPAIR_HINTS.json for repair-plan.")
    parser.add_argument("--example", choices=["starter", "portfolio"], default="starter", help="Deck to write for init.")
    parser.add_argument("--width", type=int, default=1920, help="Browser viewport width for html-pptx screenshots.")
    parser.add_argument("--height", type=int, default=1080, help="Browser viewport height for html-pptx screenshots.")
    parser.add_argument("--chrome", help="Path to Chrome/Chromium for html-pptx screenshots.")
    parser.add_argument("--visual-grammar", help="Override deck.yaml visual_grammar for build or html-pptx.")
    parser.add_argument("--grammars", help="Comma-separated visual grammars for compare-grammars, or a preset such as `highsense-20`.")
    parser.add_argument("--fail-on-layout", action="store_true", help="Exit non-zero when quality or HTML layout audit finds overlap, overflow, proof-scale, crop, or density gates.")
    parser.add_argument("--skip-layout-audit", action="store_true", help="Skip DOM layout audit for fast visual exploration; shortlisted variants should run the audit.")
    args = parser.parse_args()
    if args.command == "build":
        build_all(Path(args.out).resolve(), args.deck, args.visual_grammar, args.fail_on_layout)
    elif args.command == "html-pptx":
        html_pptx_only(args.deck, args.out, args.width, args.height, args.chrome, args.visual_grammar, args.fail_on_layout, args.skip_layout_audit)
    elif args.command == "compare-grammars":
        compare_grammars(args.deck, args.out, args.width, args.height, args.chrome, args.grammars, args.fail_on_layout)
    elif args.command == "template-shortlist":
        template_shortlist_only(args.brief, args.out, args.limit)
    elif args.command == "repair-plan":
        repair_plan_only(args.manifest, args.out)
    elif args.command == "repair-draft":
        repair_draft_only(args.deck, args.manifest, args.out, args.visual_grammar)
    elif args.command == "check":
        check_only(args.deck, args.out)
    elif args.command == "evidence":
        evidence_only(args.deck, args.out)
    elif args.command == "package":
        package_only(args.deck, args.out)
    elif args.command == "ingest":
        ingest_only(args.source, args.out)
    elif args.command == "init":
        path = Path(args.out).resolve()
        if path.suffix not in {".yaml", ".yml"}:
            path = path / "deck.yaml"
        result = dump_portfolio_deck(path) if args.example == "portfolio" else dump_default_deck(path)
        print(f"Wrote starter deck: {result}")
    elif args.command == "doctor":
        import shutil

        checks = {
            "xelatex": shutil.which("xelatex"),
            "pdftoppm": shutil.which("pdftoppm"),
            "osascript": shutil.which("osascript"),
            "python": shutil.which("python3"),
        }
        for name, value in checks.items():
            print(f"{name}: {value or 'missing'}")


if __name__ == "__main__":
    main()
