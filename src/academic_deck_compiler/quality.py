from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from math import hypot, isfinite
import re

from PIL import Image

from .content import Callout, Crop, KNOWN_LAYOUT_INTENTS, Slide, normalize_layout_intent
from .assets import resolve_asset, resolve_assets_dir
from .ir import Deck
from .render_html import VISUAL_GRAMMARS


KNOWN_KINDS = {
    "cover",
    "thesis",
    "map",
    "split",
    "process",
    "evidence",
    "matrix",
    "system",
    "loop",
    "product",
    "stack",
    "close",
}


@dataclass(frozen=True)
class Issue:
    level: str
    slide: int | None
    message: str


_SOURCE_HEAVY_CONTEXT_RE = re.compile(
    r"(github|repo|repository|code|demo|dataset|benchmark|leaderboard|paper|arxiv|table|chart|figure|"
    r"dashboard|ui|workflow|project page|homepage|screenshot|screen|interface|web|site|html|pdf)"
)


def _source_heavy_image_context(*values: str) -> bool:
    text = " ".join(value.lower() for value in values if value)
    return bool(_SOURCE_HEAVY_CONTEXT_RE.search(text))


def _validate_crop(crop: Crop, idx: int, image_path: Path | None, source_heavy: bool = False) -> list[Issue]:
    issues: list[Issue] = []
    if not all(isfinite(value) for value in (crop.x, crop.y, crop.w, crop.h)):
        issues.append(Issue("error", idx, "Evidence crop values must be finite numbers; NaN or infinity cannot be rendered safely."))
        return issues
    if crop.w <= 0 or crop.h <= 0:
        issues.append(Issue("error", idx, "Evidence crop width and height must be positive."))
        return issues
    if crop.x < 0 or crop.y < 0 or crop.x > 1 or crop.y > 1:
        issues.append(Issue("error", idx, "Evidence crop x/y must stay within [0, 1]."))
    if crop.x + crop.w > 1.0001 or crop.y + crop.h > 1.0001:
        issues.append(Issue("error", idx, "Evidence crop extends outside the source image; choose an in-bounds crop instead of relying on clamping."))
    area = crop.w * crop.h
    if area < 0.04:
        issues.append(Issue("warn", idx, "Evidence crop is extremely small; verify text remains readable after rendering."))
    elif area > 0.92:
        issues.append(Issue("warn", idx, "Evidence crop uses almost the full image; crop tighter if the page has browser chrome or dead margins."))
    if image_path and image_path.exists() and crop.x >= 0 and crop.y >= 0 and crop.x + crop.w <= 1.0001 and crop.y + crop.h <= 1.0001:
        try:
            with Image.open(image_path) as im:
                crop_w = round(crop.w * im.size[0])
                crop_h = round(crop.h * im.size[1])
            if crop_w < 420 or crop_h < 260:
                issues.append(Issue("warn", idx, f"Evidence crop is only {crop_w}x{crop_h}px; screenshots need enough pixels for slide-scale readability."))
            crop_ratio = crop_w / max(1, crop_h)
            if source_heavy and area > 0.92 and (crop_ratio < 1.25 or crop_ratio > 2.25):
                issues.append(
                    Issue(
                        "error",
                        idx,
                        f"Source-heavy evidence uses an almost full-frame {crop_ratio:.1f}:1 crop; crop to the readable figure, table, UI, or project region before insertion.",
                    )
                )
            if crop_ratio < 0.45 or crop_ratio > 3.2:
                issues.append(Issue("warn", idx, f"Evidence crop aspect ratio is {crop_ratio:.1f}:1; expect letterboxing unless the proof slot is redesigned."))
        except OSError:
            issues.append(Issue("warn", idx, f"Could not inspect image dimensions for {image_path}."))
    return issues


def _validate_callouts(callouts: tuple[Callout, ...], idx: int) -> list[Issue]:
    issues: list[Issue] = []
    if len(callouts) > 3:
        issues.append(Issue("error", idx, "More than three callouts would be silently truncated; keep only the three most important pins."))
    for callout in callouts:
        if not (isfinite(callout.x) and isfinite(callout.y)):
            issues.append(Issue("error", idx, "Callout pin coordinates must be finite numbers; NaN or infinity cannot be positioned safely."))
            continue
        if callout.x < 0.03 or callout.x > 0.97 or callout.y < 0.03 or callout.y > 0.97:
            issues.append(Issue("error", idx, "Callout pin is outside the safe image area; keep x/y between 0.03 and 0.97."))
        if len(callout.text) > 42:
            issues.append(Issue("warn", idx, "Callout text is long; shorten it so the annotation does not dominate the crop."))
    for left_index, left in enumerate(callouts):
        for right in callouts[left_index + 1 :]:
            if hypot(left.x - right.x, left.y - right.y) < 0.09:
                issues.append(Issue("warn", idx, "Two callout pins are very close; separate them or remove one to avoid visual overlap."))
    return issues


_DENSE_SCRIPT_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uf900-\ufaff\uac00-\ud7af]")
_LATIN_TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:[._:/%+#-][A-Za-z0-9]+)*")


def _text_len(value: str) -> int:
    """Approximate slide-layout burden across English and dense CJK scripts."""
    text = " ".join(value.split())
    if not text:
        return 0
    dense_units = len(_DENSE_SCRIPT_RE.findall(text))
    latin_text = _DENSE_SCRIPT_RE.sub(" ", text)
    latin_units = len(_LATIN_TOKEN_RE.findall(latin_text))
    char_units = len(text)
    dense_penalty = dense_units // 2
    return max(char_units + dense_penalty, dense_units + latin_units)


def _generic_image_context(value: str) -> bool:
    text = " ".join(value.lower().split())
    if not text:
        return True
    if text.startswith(("http://", "https://", "doi:", "arxiv:")):
        return False
    if " " not in text and text.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif", ".pdf", ".html")):
        return True
    return text in {
        "image",
        "screenshot",
        "figure",
        "chart",
        "proof",
        "source",
        "source artifact",
        "source surface",
        "homepage",
        "project page",
        "artifact",
        "fixture",
    }


def _validate_text_budget(slide: Slide, idx: int, normalized_layout: str) -> list[Issue]:
    issues: list[Issue] = []
    title_len = _text_len(slide.title)
    subtitle_len = _text_len(slide.subtitle)
    has_inserted_image = bool(slide.evidence or slide.image)
    is_proof_slide = slide.kind in {"evidence", "loop", "product"}
    is_image_backed_content = has_inserted_image and slide.kind not in {"cover", "map", "matrix", "evidence", "loop", "product"}
    title_error_limit = 104 if has_inserted_image and slide.kind != "cover" else 128
    title_warn_limit = 78 if has_inserted_image and slide.kind != "cover" else 92
    if title_len > title_error_limit:
        issues.append(Issue("error", idx, "Title is too long to lay out safely; split the idea across slides or move detail into subtitle/notes."))
    elif title_len > title_warn_limit:
        issues.append(Issue("warn", idx, "Title is long; action titles work best when they can be read in one breath."))
    subtitle_error_limit = 190 if is_proof_slide and has_inserted_image else 220 if is_image_backed_content else 260
    subtitle_warn_limit = 140 if is_proof_slide and has_inserted_image else 160 if is_image_backed_content else 180
    if subtitle_len > subtitle_error_limit:
        issues.append(Issue("error", idx, "Subtitle is too long for a fixed slide canvas; shorten it or move it into speaker notes."))
    elif subtitle_len > subtitle_warn_limit:
        issues.append(Issue("warn", idx, "Subtitle is dense; shorten it if the layout audit reports tight spacing."))

    bullet_limit = 4
    if normalized_layout in {"proof-showcase", "artifact-showcase"} or (is_proof_slide and has_inserted_image) or is_image_backed_content:
        bullet_limit = 3
    if slide.kind == "matrix":
        bullet_limit = 8
    if len(slide.bullets) > bullet_limit and slide.kind != "matrix":
        issues.append(Issue("error", idx, f"Too many bullets for `{normalized_layout or slide.kind}`; renderer shows at most {bullet_limit}, so split the slide or change the layout instead of silently dropping content."))

    for item in slide.bullets:
        if not item.strip():
            issues.append(Issue("error", idx, "Empty bullet creates an empty visual module; remove it or replace it with a real claim."))

    total_bullet_chars = sum(_text_len(item) for item in slide.bullets)
    total_error_limit = 360 if (is_proof_slide and has_inserted_image) or is_image_backed_content else 620
    total_warn_limit = 260 if (is_proof_slide and has_inserted_image) or is_image_backed_content else 420
    if slide.kind != "matrix" and total_bullet_chars > total_error_limit:
        issues.append(Issue("error", idx, "Bullet text exceeds the safe content budget for one slide."))
    elif slide.kind != "matrix" and total_bullet_chars > total_warn_limit:
        issues.append(Issue("warn", idx, "Bullet text is dense; expect a cramped slide unless the layout is redesigned."))
    for item in slide.bullets:
        item_len = _text_len(item)
        bullet_error_limit = 150 if (is_proof_slide and has_inserted_image) or is_image_backed_content else 220
        bullet_warn_limit = 110 if (is_proof_slide and has_inserted_image) or is_image_backed_content else 150
        if item_len > bullet_error_limit:
            issues.append(Issue("error", idx, "A bullet is too long to render safely; split it or move detail to notes."))
        elif item_len > bullet_warn_limit:
            issues.append(Issue("warn", idx, "A bullet is long; shorten it to prevent wrapping collisions."))

    if is_proof_slide and has_inserted_image and len(slide.metrics) > 2:
        issues.append(Issue("error", idx, "Proof slides with images must use at most two metrics; extra metrics squeeze the evidence surface and increase overlap risk."))
    if is_image_backed_content and len(slide.metrics) > 2:
        issues.append(Issue("error", idx, "Image-backed content slides should not combine an artifact panel with more than two metrics; split the slide or remove the image."))

    if len(slide.metrics) > 4:
        issues.append(Issue("error", idx, "Too many metrics for one slide; renderer shows at most four, so use a matrix or split the evidence."))
    for value, label in slide.metrics:
        if not value.strip() or not label.strip():
            issues.append(Issue("error", idx, "Metric cells need both a value and a label; empty metric boxes read as AI filler."))
            continue
        if _text_len(value) > 28:
            issues.append(Issue("error", idx, "Metric value is too long; metric cells need short numeric or named anchors."))
        elif _text_len(value) > 18:
            issues.append(Issue("warn", idx, "Metric value is long and may wrap awkwardly."))
        if _text_len(label) > 60:
            issues.append(Issue("error", idx, "Metric label is too long; shorten it or convert it to a bullet."))
        elif _text_len(label) > 42:
            issues.append(Issue("warn", idx, "Metric label is long and may collide with neighboring cells."))

    label_limit = 4 if is_image_backed_content else 5
    if len(slide.labels) > label_limit and slide.kind not in {"matrix", "map"}:
        word = "four" if label_limit == 4 else "five"
        issues.append(Issue("error", idx, f"Too many labels for this slide; renderer shows at most {word}, so use fewer labels or a matrix layout."))
    for label in slide.labels:
        if not label.strip():
            issues.append(Issue("error", idx, "Empty labels create blank boxes; remove them instead of using them as spacing devices."))
            continue
        if _text_len(label) > 96:
            issues.append(Issue("error", idx, "A label is too long for the label-board layouts."))
        elif _text_len(label) > 68:
            issues.append(Issue("warn", idx, "A label is long; shorten it to avoid wrapping collisions."))

    if has_inserted_image and slide.kind != "cover":
        callout_count = len(slide.evidence.callouts) if slide.evidence else 0
        module_count = len(slide.bullets) + len(slide.metrics) + len(slide.labels) + callout_count
        if is_proof_slide:
            if module_count > 5:
                issues.append(
                    Issue(
                        "error",
                        idx,
                        "Image-backed proof slide combines too many text modules; keep the proof surface dominant by using at most five total bullets, metrics, labels, and callouts.",
                    )
                )
            elif module_count > 4 and normalized_layout not in {"proof-showcase", "proof-stage"}:
                issues.append(
                    Issue(
                        "warn",
                        idx,
                        "Dense proof slide should request `layout: proof-showcase` or `proof-stage` so text cannot crowd the inserted image.",
                    )
                )
            if callout_count and (len(slide.bullets) > 2 or len(slide.metrics) > 1):
                issues.append(Issue("warn", idx, "Callout notes compete with side bullets and metrics; remove one module family if the DOM audit reports tight clearance."))
        elif is_image_backed_content:
            if module_count > 6:
                issues.append(
                    Issue(
                        "error",
                        idx,
                        "Image-backed content slide combines too many modules around the artifact; split the slide or remove labels/metrics before inserting the image.",
                    )
                )
            elif module_count > 5 and normalized_layout != "artifact-showcase":
                issues.append(
                    Issue(
                        "warn",
                        idx,
                        "Dense artifact slide should request `layout: artifact-showcase` so the image and text receive stable separate zones.",
                    )
                )

    if slide.evidence:
        caption_error_limit = 125 if is_proof_slide or is_image_backed_content else 170
        caption_warn_limit = 90 if is_proof_slide or is_image_backed_content else 120
        if _text_len(slide.evidence.caption) > caption_error_limit:
            issues.append(Issue("error", idx, "Evidence caption is too long; keep it to the inspected claim and source cue."))
        elif _text_len(slide.evidence.caption) > caption_warn_limit:
            issues.append(Issue("warn", idx, "Evidence caption is long and may crowd the proof surface."))
        if _text_len(slide.evidence.source) > 150:
            issues.append(Issue("warn", idx, "Evidence source line is long; use a compact source label or URL note."))
    return issues


def _effective_image_size(path: Path, crop: Crop | None = None) -> tuple[int, int, float] | None:
    try:
        with Image.open(path) as im:
            width, height = im.size
    except OSError:
        return None
    if crop:
        width = round(width * crop.w)
        height = round(height * crop.h)
    ratio = width / max(1, height)
    return width, height, ratio


def _source_image_size(path: Path) -> tuple[int, int, float] | None:
    try:
        with Image.open(path) as im:
            width, height = im.size
    except OSError:
        return None
    return width, height, width / max(1, height)


def _validate_image_role(path: Path, idx: int, role: str, crop: Crop | None = None, source_heavy: bool = False) -> list[Issue]:
    issues: list[Issue] = []
    inspected = _effective_image_size(path, crop)
    if inspected is None:
        return [Issue("warn", idx, f"Could not inspect image dimensions for {path}.")]
    width, height, ratio = inspected
    label = "crop" if crop else "image"
    if role == "proof":
        if source_heavy and (width < 900 or height < 500):
            issues.append(Issue("error", idx, f"Source-heavy evidence {label} is only {width}x{height}px; use a tighter or higher-resolution figure, table, UI, or project crop before insertion."))
        elif source_heavy and (width < 1100 or height < 620):
            issues.append(Issue("warn", idx, f"Source-heavy evidence {label} is {width}x{height}px; verify it remains readable as the main proof surface."))
        if width < 640 or height < 360:
            issues.append(Issue("error", idx, f"Evidence {label} is only {width}x{height}px; proof surfaces need enough pixels to remain readable."))
        elif width < 1000 or height < 560:
            issues.append(Issue("warn", idx, f"Evidence {label} is {width}x{height}px; use a tighter or higher-resolution crop if text matters."))
        if ratio < 0.38 or ratio > 4.2:
            issues.append(Issue("error", idx, f"Evidence {label} aspect ratio is {ratio:.1f}:1; choose a different crop or a grammar with a matching slot."))
        elif ratio < 0.55 or ratio > 3.2:
            issues.append(Issue("warn", idx, f"Evidence {label} aspect ratio is {ratio:.1f}:1; expect letterboxing unless the proof slot is redesigned."))
    elif role == "artifact":
        if source_heavy and (width < 820 or height < 460):
            issues.append(Issue("error", idx, f"Source-heavy artifact {label} is only {width}x{height}px; source panels should be readable evidence, not thumbnails."))
        elif source_heavy and (width < 980 or height < 540):
            issues.append(Issue("warn", idx, f"Source-heavy artifact {label} is {width}x{height}px; verify it at full-slide scale before delivery."))
        if width < 520 or height < 300:
            issues.append(Issue("error", idx, f"Artifact {label} is only {width}x{height}px; source panels should be readable or removed."))
        elif width < 800 or height < 450:
            issues.append(Issue("warn", idx, f"Artifact {label} is {width}x{height}px; verify it at full-slide scale."))
        if ratio < 0.28 or ratio > 5.8:
            issues.append(Issue("error", idx, f"Artifact {label} aspect ratio is {ratio:.1f}:1; choose a crop that can occupy a stable slide slot."))
        elif ratio < 0.36 or ratio > 4.6:
            issues.append(Issue("warn", idx, f"Artifact {label} aspect ratio is {ratio:.1f}:1; consider cropping before insertion."))
    elif role == "cover":
        if width < 260 or height < 260:
            issues.append(Issue("warn", idx, f"Cover image is only {width}x{height}px; use it as a small identity anchor, not a large proof surface."))
    return issues


def _image_name(slide: Slide) -> str | None:
    if slide.evidence and slide.evidence.image:
        return slide.evidence.image
    return slide.image


def check_deck(deck: Deck) -> list[Issue]:
    issues: list[Issue] = []
    grammar = deck.visual_grammar.strip().lower().replace("_", "-")
    if grammar and grammar not in VISUAL_GRAMMARS:
        known = ", ".join(sorted(VISUAL_GRAMMARS))
        issues.append(Issue("error", None, f"Unsupported visual_grammar `{deck.visual_grammar}`. Use one of: {known}."))
    if len(deck.slides) < 4:
        issues.append(Issue("warn", None, "Deck has fewer than four slides; most talks need a cover, thesis, evidence, and close."))
    asset_root = resolve_assets_dir(deck)
    image_refs: dict[str, list[int]] = {}
    proof_refs: dict[str, list[int]] = {}
    for idx, slide in enumerate(deck.slides, start=1):
        evidence_image = _image_name(slide)
        if evidence_image:
            image_refs.setdefault(evidence_image, []).append(idx)
            if slide.kind in {"evidence", "loop", "product"}:
                proof_refs.setdefault(evidence_image, []).append(idx)
        if slide.kind not in KNOWN_KINDS:
            issues.append(Issue("error", idx, f"Unsupported slide kind: {slide.kind}."))
        normalized_layout = normalize_layout_intent(slide.layout)
        if slide.layout and not normalized_layout:
            known = ", ".join(sorted(KNOWN_LAYOUT_INTENTS))
            issues.append(Issue("error", idx, f"Unsupported layout intent: {slide.layout}. Use one of: {known}."))
        if normalized_layout.startswith("proof-") and slide.kind not in {"evidence", "loop", "product"}:
            issues.append(Issue("error", idx, f"Layout `{normalized_layout}` is only valid for evidence, loop, or product slides."))
        if normalized_layout.startswith("artifact-") and slide.kind in {"cover", "map", "matrix", "evidence", "loop", "product"}:
            issues.append(Issue("error", idx, f"Layout `{normalized_layout}` is only valid for image-backed content slides."))
        if normalized_layout.startswith("proof-") and not evidence_image:
            issues.append(Issue("error", idx, f"Layout `{normalized_layout}` needs an evidence image; otherwise the slide will render a placeholder."))
        if normalized_layout.startswith("artifact-") and not evidence_image:
            issues.append(Issue("error", idx, f"Layout `{normalized_layout}` needs an image or evidence object."))
        issues.extend(_validate_text_budget(slide, idx, normalized_layout))
        if slide.kind in {"evidence", "loop", "product"} and not (evidence_image or slide.metrics):
            issues.append(Issue("warn", idx, "Evidence-oriented slide has no image or metrics."))
        if evidence_image and slide.kind in {"evidence", "loop", "product"} and not slide.evidence:
            issues.append(Issue("error", idx, "Proof/evidence images must use an `evidence:` block with image, crop, caption, and source; bare images skip the insertion contract."))
        elif evidence_image and slide.kind != "cover" and not slide.evidence:
            issues.append(Issue("error", idx, "Image-backed content must use an `evidence:` block with crop, caption, and source; bare images skip the artifact insertion contract."))
        if slide.kind != "cover" and slide.image and (not slide.evidence or not slide.evidence.image):
            issues.append(Issue("error", idx, "Non-cover images must be declared as `evidence.image`; top-level `image` is only a cover identity fallback."))
        if slide.kind != "cover" and slide.image and slide.evidence and slide.evidence.image and slide.image != slide.evidence.image:
            issues.append(Issue("error", idx, "`image` and `evidence.image` point to different files; use one evidence source so crop, caption, and audit checks target the rendered image."))
        if slide.kind == "cover" and slide.image and slide.evidence and slide.evidence.image and slide.image != slide.evidence.image:
            issues.append(Issue("error", idx, "Cover `image` and `evidence.image` point to different files; use one cover source so crop, caption, and audit checks target the rendered image."))
        if slide.kind == "cover" and evidence_image and not slide.evidence:
            issues.append(Issue("warn", idx, "Cover image is treated as identity-only; move proof screenshots, figures, and project evidence to an evidence or artifact slide with crop, caption, and source."))
        if slide.kind == "cover" and slide.evidence and evidence_image:
            if not slide.evidence.crop:
                issues.append(Issue("error", idx, "Cover evidence images must declare `evidence.crop`; use top-level `image` only for simple identity art."))
            if not slide.evidence.caption.strip() or not slide.evidence.source.strip():
                issues.append(Issue("error", idx, "Cover evidence images need both caption and source; otherwise the cover image must remain identity-only."))
        image_path = resolve_asset(deck, evidence_image) if evidence_image else None
        source_heavy = _source_heavy_image_context(
            evidence_image or "",
            slide.title,
            slide.subtitle,
            slide.evidence.caption if slide.evidence else "",
            slide.evidence.source if slide.evidence else "",
        )
        if evidence_image and image_path and not image_path.exists():
            issues.append(Issue("error", idx, f"Missing image asset: {image_path}."))
        if evidence_image and image_path and image_path.exists():
            image_role = "proof" if slide.kind in {"evidence", "loop", "product"} else "cover" if slide.kind == "cover" else "artifact"
            image_crop = slide.evidence.crop if slide.evidence else None
            issues.extend(_validate_image_role(image_path, idx, image_role, image_crop, source_heavy=source_heavy))
            if slide.kind == "cover" and slide.image and not slide.evidence:
                source_size = _source_image_size(image_path)
                if source_size:
                    width, height, ratio = source_size
                    if width >= 900 and height >= 500 and ratio > 1.45:
                        issues.append(Issue("error", idx, "Cover image looks like a screenshot or proof surface; declare it as `evidence:` with crop, caption, and source, or replace it with a compact identity image."))
        bare_image_evidence = bool(
            evidence_image
            and slide.evidence
            and not slide.evidence.crop
            and not slide.evidence.caption.strip()
            and not slide.evidence.source.strip()
            and not slide.evidence.callouts
        )
        if bare_image_evidence and slide.kind in {"evidence", "loop", "product"}:
            issues.append(Issue("error", idx, "Proof/evidence images must use an `evidence:` block with image, crop, caption, and source; bare images skip the insertion contract."))
        elif bare_image_evidence and slide.kind != "cover":
            issues.append(Issue("error", idx, "Image-backed content must use an `evidence:` block with crop, caption, and source; bare images skip the artifact insertion contract."))
        if slide.evidence and evidence_image and slide.kind != "cover" and not slide.evidence.crop:
            issues.append(Issue("error", idx, "Non-cover images must declare `evidence.crop`; use a full-frame crop only when the source file is already pre-cropped for slide use."))
        if slide.kind in {"evidence", "loop", "product"} and evidence_image and normalized_layout not in {"proof-showcase", "proof-stage"}:
            if len(slide.bullets) >= 4 or len(slide.metrics) >= 3:
                issues.append(Issue("warn", idx, "Dense evidence slide may squeeze the proof surface; use `layout: proof-showcase` or shorten the side notes if the audit reports small proof images."))
        if slide.evidence and evidence_image and slide.kind != "cover":
            has_caption = bool(slide.evidence.caption.strip())
            has_source = bool(slide.evidence.source.strip())
            if slide.kind in {"evidence", "loop", "product"} and not (has_caption and has_source):
                issues.append(Issue("error", idx, "Primary proof image needs both a caption and compact source line."))
            elif slide.kind in {"evidence", "loop", "product"} and (
                _generic_image_context(slide.evidence.caption) or _generic_image_context(slide.evidence.source)
            ):
                issues.append(Issue("warn", idx, "Primary proof caption/source is too generic; name the inspected claim and source."))
            if slide.kind not in {"evidence", "loop", "product"} and not (has_caption and has_source):
                issues.append(Issue("error", idx, "Image-backed content slide needs an explicit artifact caption and source; otherwise the screenshot reads as decoration."))
            elif slide.kind not in {"evidence", "loop", "product"} and (
                _generic_image_context(slide.evidence.caption) or _generic_image_context(slide.evidence.source)
            ):
                issues.append(Issue("warn", idx, "Artifact caption/source is too generic; describe the exact source region or remove the image."))
        if slide.evidence and slide.evidence.crop:
            issues.extend(_validate_crop(slide.evidence.crop, idx, image_path, source_heavy=source_heavy))
        if slide.evidence and slide.evidence.callouts:
            issues.extend(_validate_callouts(slide.evidence.callouts, idx))
        if slide.kind == "cover" and not slide.metrics:
            issues.append(Issue("warn", idx, "Cover has no metrics; add 2-3 credibility anchors."))
        if slide.kind == "close" and not (slide.note or deck.contact):
            issues.append(Issue("warn", idx, "Close slide has no contact, paper, repo, or next-step link."))
    for image, slide_numbers in sorted(image_refs.items(), key=lambda item: item[1][0]):
        if len(slide_numbers) > 2:
            slides = ", ".join(str(number) for number in slide_numbers)
            issues.append(Issue("warn", None, f"Image `{image}` appears on slides {slides}; after two uses, change the crop/purpose or replace it with fresh evidence."))
    for image, slide_numbers in sorted(proof_refs.items(), key=lambda item: item[1][0]):
        if len(slide_numbers) > 1:
            slides = ", ".join(str(number) for number in slide_numbers)
            issues.append(Issue("warn", None, f"Image `{image}` is reused as primary proof on slides {slides}; verify each crop proves a different claim or use another source surface."))
    if not asset_root.exists():
        issues.append(Issue("warn", None, f"Assets directory does not exist yet: {asset_root}."))
    return issues


def write_quality_report(path: Path, deck: Deck, issues: list[Issue]) -> Path:
    errors = [issue for issue in issues if issue.level == "error"]
    warnings = [issue for issue in issues if issue.level == "warn"]
    lines = [
        "# Quality Report",
        "",
        f"- Deck: `{deck.deck_id}`",
        f"- Slides: {len(deck.slides)}",
        f"- Errors: {len(errors)}",
        f"- Warnings: {len(warnings)}",
        "",
    ]
    if not issues:
        lines.append("No structural issues found. Manual visual review is still required.")
    else:
        lines.append("## Issues")
        for issue in issues:
            scope = f"slide {issue.slide}" if issue.slide else "deck"
            lines.append(f"- `{issue.level}` / {scope}: {issue.message}")
    lines.extend(
        [
            "",
            "## Manual Gates",
            "- Each slide should have one judgment, not a paragraph title.",
            "- Each evidence image should prove a claim and remain readable after rendering.",
            "- HTML-first is the design source of truth; PPTX is exported after the HTML pass is stable.",
            "- Run `html-pptx --fail-on-layout` and read `layout-audit-report.md`; hard overlap, overflow, small rendered-image, callout, or underfill gates must be fixed.",
            "- Pages may use whitespace, but they should not leave most of the canvas empty with tiny text.",
            "- Aesthetic review overrides the density heuristic when they disagree, but not hard overlap failures.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
