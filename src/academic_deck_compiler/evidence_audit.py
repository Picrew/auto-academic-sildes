from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from .assets import resolve_asset, resolve_assets_dir
from .content import Slide
from .ir import Deck


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


@dataclass(frozen=True)
class AssetRecord:
    path: Path
    width: int
    height: int
    role: str
    recommendation: str
    used_on: tuple[int, ...]

    @property
    def aspect(self) -> float:
        return self.width / max(1, self.height)


def classify_asset(path: Path) -> tuple[str, str]:
    name = path.stem.lower()
    if any(token in name for token in ("logo", "avatar", "portrait", "headshot", "microsoft", "netease", "lab")):
        return "identity marker", "Use as a small badge only; do not let it carry a slide claim."
    if any(token in name for token in ("homepage", "profile", "personal")):
        return "identity homepage", "Use as an identity anchor; pair it with work artifacts for claims."
    if any(token in name for token in ("github", "repo", "readme", "code")):
        return "repository artifact", "Use when reproducibility, implementation, or artifact availability matters."
    if any(token in name for token in ("project", "demo", "gym", "website", "page")):
        return "project page", "Use when project scope, links, or public positioning proves the claim."
    if any(token in name for token in ("screenshot", "product", "writer", "ui")):
        return "product screenshot", "Crop to the workflow state where the user or system decision is visible."
    if any(token in name for token in ("heatmap", "chart", "curve", "leaderboard", "result", "two_stage", "gap_panel", "quote_gap")):
        return "result figure", "Crop to one readable panel or rebuild the chart natively in the deck grammar."
    if any(token in name for token in ("arch", "pipeline", "checker", "system", "diagram")):
        return "system diagram", "Redraw natively if labels will shrink below presentation readability."
    return "candidate image", "Attach it only after naming the exact claim it proves."


def classify_reference(image_name: str, slide: Slide, record: AssetRecord | None = None) -> tuple[str, str]:
    evidence = slide.evidence
    source = (evidence.source if evidence else "") or ""
    caption = (evidence.caption if evidence else "") or ""
    image_key = image_name.lower()
    if any(token in image_key for token in ("homepage", "profile", "personal")):
        return "identity homepage", "Good for identity and positioning; pair with work artifacts for research claims."
    if any(token in image_key for token in ("github", "repo", "readme")) or "github.com" in source.lower():
        return "repository artifact", "Good for implementation, artifact links, reproducibility, or public code evidence."
    if any(token in image_key for token in ("leaderboard", "benchmark", "score", "eval")):
        return "benchmark/result surface", "Good for evaluation claims; crop enough labels to make the comparison readable."
    if any(token in image_key for token in ("heatmap", "chart", "curve", "figure", "result", "radar", "table")):
        return "paper/result figure", "Good for method or result claims; keep one inspectable panel rather than the full paper page."
    if any(token in image_key for token in ("project", "demo", "gym", "website", "page")):
        return "project page", "Good for public project scope and artifact navigation."
    haystack = " ".join((image_name, source, caption, slide.title, slide.subtitle)).lower()
    if "github.com" in haystack or any(token in haystack for token in ("repo", "repository", "readme", "code link")):
        return "repository artifact", "Good for implementation, artifact links, reproducibility, or public code evidence."
    if any(token in haystack for token in ("leaderboard", "benchmark", "bfcl", "aime", "score", "accuracy", "eval", "evaluation")):
        return "benchmark/result surface", "Good for evaluation claims; crop enough labels to make the comparison readable."
    if any(token in haystack for token in ("figure", "chart", "heatmap", "curve", "table", "result", "radar")):
        return "paper/result figure", "Good for method or result claims; keep one inspectable panel rather than the full paper page."
    if any(token in haystack for token in ("arxiv", "paper", "pdf", "openreview", "semantic scholar", "dblp")):
        return "paper page", "Good for citation and provenance; prefer figures/tables when arguing results."
    if any(token in haystack for token in ("homepage", "personal site", "profile", "biography", "identity anchor")):
        return "identity homepage", "Good for identity and positioning; pair with work artifacts for research claims."
    if any(token in haystack for token in ("project", "demo", "dataset", "model", "real-time gym", "gorilla", "limo", "scope", "vcr", "clap")):
        return "project page", "Good for public project scope and artifact navigation."
    if any(token in haystack for token in ("ui", "product", "workflow", "interface", "screenshot")):
        return "product workflow", "Good when the visible state shows a user or system decision."
    if record and record.role != "candidate image":
        return record.role, record.recommendation
    return "untyped evidence", "Clarify whether this is identity, project, paper, repo, benchmark, or result evidence."


def referenced_images(deck: Deck) -> dict[str, list[int]]:
    refs: dict[str, list[int]] = {}
    for idx, slide in enumerate(deck.slides, start=1):
        image = slide.evidence.image if slide.evidence and slide.evidence.image else slide.image
        if image:
            refs.setdefault(image, []).append(idx)
    return refs


def scan_assets(deck: Deck) -> list[AssetRecord]:
    asset_root = resolve_assets_dir(deck)
    refs = referenced_images(deck)
    records: list[AssetRecord] = []
    if not asset_root.exists():
        return records
    for path in sorted(p for p in asset_root.rglob("*") if p.suffix.lower() in IMAGE_SUFFIXES):
        try:
            with Image.open(path) as im:
                width, height = im.size
        except OSError:
            continue
        role, recommendation = classify_asset(path)
        rel = path.relative_to(asset_root).as_posix()
        records.append(AssetRecord(path=path, width=width, height=height, role=role, recommendation=recommendation, used_on=tuple(refs.get(rel, ()))))
    return records


def crop_summary(deck: Deck, slide_idx: int) -> str:
    slide = deck.slides[slide_idx - 1]
    if not slide.evidence or not slide.evidence.image:
        return "no evidence block"
    path = resolve_asset(deck, slide.evidence.image)
    if not path.exists():
        return "missing asset"
    try:
        with Image.open(path) as im:
            width, height = im.size
    except OSError:
        return "unreadable asset"
    if not slide.evidence.crop:
        return f"uncropped source ({width}x{height})"
    crop = slide.evidence.crop
    crop_w = round(width * crop.w)
    crop_h = round(height * crop.h)
    crop_area = crop.w * crop.h
    return f"crop {crop_w}x{crop_h} ({crop_area:.0%} of source)"


def evidence_mix(deck: Deck, record_by_rel: dict[str, AssetRecord]) -> tuple[dict[str, int], list[str]]:
    counts: dict[str, int] = {}
    warnings: list[str] = []
    refs = referenced_images(deck)
    for image, slide_numbers in refs.items():
        record = record_by_rel.get(image)
        for slide_idx in slide_numbers:
            role, _ = classify_reference(image, deck.slides[slide_idx - 1], record)
            counts[role] = counts.get(role, 0) + 1
            slide = deck.slides[slide_idx - 1]
            if slide.kind in {"evidence", "loop", "product"} and role in {"identity marker", "identity homepage"}:
                warnings.append(
                    f"`{image}` is used as {role} on evidence slide {slide_idx}; use it only for identity unless the slide claim is explicitly about the public profile."
                )
        if len(slide_numbers) > 2:
            slides = ", ".join(str(number) for number in slide_numbers)
            warnings.append(f"`{image}` appears on slides {slides}; after two uses, change the crop/purpose or replace it with new evidence.")
    distinct = {role for role in counts if role != "untyped evidence"}
    if len(refs) >= 3 and len(distinct) < 2:
        warnings.append("Evidence mix is too narrow; add a different proof type such as a project page, paper/result figure, benchmark surface, or repository artifact.")
    identity_count = counts.get("identity homepage", 0) + counts.get("identity marker", 0)
    work_count = sum(count for role, count in counts.items() if role not in {"identity homepage", "identity marker", "untyped evidence"})
    if identity_count and not work_count:
        warnings.append("The deck uses identity imagery but no work artifact; public profiles need source evidence for research or project claims.")
    if counts.get("untyped evidence"):
        warnings.append("Some referenced images are untyped; improve filenames, captions, or evidence.source so future agents know why the image is present.")
    return counts, warnings


def write_evidence_report(path: Path, deck: Deck) -> Path:
    refs = referenced_images(deck)
    records = scan_assets(deck)
    record_by_rel = {}
    asset_root = resolve_assets_dir(deck)
    for record in records:
        record_by_rel[record.path.relative_to(asset_root).as_posix()] = record
    mix_counts, mix_warnings = evidence_mix(deck, record_by_rel)

    lines = [
        "# Evidence Report",
        "",
        f"- Deck: `{deck.deck_id}`",
        f"- Asset root: `{asset_root}`",
        f"- Images found: {len(records)}",
        f"- Images referenced: {len(refs)}",
        "",
        "## Evidence Mix",
        "",
    ]
    if mix_counts:
        for role, count in sorted(mix_counts.items()):
            lines.append(f"- {role}: {count}")
    else:
        lines.append("No referenced images to classify.")
    if mix_warnings:
        lines.extend(["", "### Mix Warnings"])
        for warning in mix_warnings:
            lines.append(f"- {warning}")
    lines.extend(
        [
            "",
        "## Referenced Proof Objects",
        "",
        ]
    )
    if not refs:
        lines.append("No images are referenced by the deck yet.")
    for image, slide_numbers in sorted(refs.items(), key=lambda item: item[1][0]):
        record = record_by_rel.get(image)
        if record:
            role, role_advice = classify_reference(image, deck.slides[slide_numbers[0] - 1], record)
            shape = f"{record.width}x{record.height}, aspect {record.aspect:.2f}"
            advice = role_advice
        else:
            role = "missing"
            shape = "not found"
            advice = "Fix the asset path before layout work."
        slides = ", ".join(str(i) for i in slide_numbers)
        crop = "; ".join(crop_summary(deck, i) for i in slide_numbers)
        lines.append(f"- `{image}` -> slides {slides}: {role}; {shape}; {crop}. {advice}")

    lines.extend(["", "## Asset Catalog", ""])
    for record in records:
        rel = record.path.relative_to(asset_root).as_posix()
        status = f"used on {', '.join(str(i) for i in record.used_on)}" if record.used_on else "unused"
        lines.append(f"- `{rel}`: {record.role}; {record.width}x{record.height}; {status}. {record.recommendation}")

    lines.extend(
        [
            "",
            "## Selection Protocol",
            "",
            "1. Start from the slide claim, then choose the smallest image region that proves it.",
            "2. Prefer result figures, system diagrams, and real product workflow state over logos or decorative screenshots.",
            "3. Use one primary proof object per slide; add at most three pins, and make every pin explain a judgment.",
            "4. Rebuild charts natively when axes or labels are unreadable after cropping.",
            "5. Keep asset provenance in `evidence.source` so academic audiences can inspect the claim.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
