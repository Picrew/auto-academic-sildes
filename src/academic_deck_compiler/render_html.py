from __future__ import annotations

from hashlib import sha1
from html import escape
from pathlib import Path

from .assets import crop_asset, resolve_asset
from .content import Slide, normalize_layout_intent
from .ir import Deck, DEFAULT_DECK
from .patterns import parse_matrix_rows
from .style import THEME

VISUAL_GRAMMARS = {
    "editorial-profile",
    "swiss-systems",
    "dark-lab-notebook",
    "paper-atlas",
    "keynote-evidence-wall",
    "highsense-gallery",
    "academic-homepage-grid",
    "prism-dossier",
    "fathom-research-brief",
    "jetset-theory-grid",
    "monograph-review",
    "broadside-lab",
    "catalog-atelier",
    "evidence-atelier",
    "atlas-marginalia",
    "systems-field-manual",
    "lab-trace-ledger",
    "object-study-wall",
    "vellum-research-note",
    "cobalt-research-grid",
    "mono-ink-ledger",
    "forest-editorial-brief",
    "neo-grid-lab",
    "prism-clean-room",
    "prism-publication-stack",
    "ia-research-archive",
    "pentagram-gridnote",
    "takram-research-system",
    "stamen-data-map",
    "couture-exhibition",
    "huashu-editorial-lab",
    "prism-newsroom-index",
    "prism-workbench-index",
    "huashu-build-board",
    "huashu-issue-broadsheet",
    "gallery-proof-room",
    "broadsheet-data-room",
    "js-editorial-cascade",
    "sumi-research-scroll",
    "signal-intelligence-brief",
    "raw-grid-research",
    "stencil-field-tablet",
    "maison-research-catalog",
    "folio-swiss-noir",
    "chromatic-research-map",
}


def slug(text: str) -> str:
    return "".join(ch if ch.isalnum() else "-" for ch in text.lower()).strip("-") or "academic-deck"


def normalize_grammar(value: str | None) -> str:
    grammar = (value or "editorial-profile").strip().lower().replace("_", "-")
    if grammar not in VISUAL_GRAMMARS:
        known = ", ".join(sorted(VISUAL_GRAMMARS))
        raise ValueError(f"Unsupported visual grammar `{value}`. Use one of: {known}.")
    return grammar


def evidence_path(slide: Slide, deck: Deck, cache_dir: Path) -> Path | None:
    evidence = slide.evidence
    if evidence and evidence.image:
        image_name = evidence.image
    elif slide.kind == "cover":
        image_name = slide.image
    else:
        return None
    if not image_name:
        return None
    source = resolve_asset(deck, image_name)
    if not source.exists():
        return None
    if evidence and evidence.crop:
        key = sha1(f"{source}|{evidence.crop}".encode("utf-8")).hexdigest()[:16]
        return crop_asset(source, evidence.crop, cache_dir, key)
    return source


def metrics(items: tuple[tuple[str, str], ...]) -> str:
    if not items:
        return ""
    cells = []
    for value, label in items[:4]:
        cells.append(f"<div class='metric'><strong>{escape(value)}</strong><span>{escape(label)}</span></div>")
    return "<div class='metrics'>" + "".join(cells) + "</div>"


def bullets(items: tuple[str, ...]) -> str:
    return "<ul>" + "".join(f"<li>{escape(item)}</li>" for item in items[:4]) + "</ul>" if items else ""


def labels_panel(items: tuple[str, ...]) -> str:
    if not items:
        return ""
    rows = "".join(f"<div><span>{i + 1:02d}</span><b>{escape(item)}</b></div>" for i, item in enumerate(items[:5]))
    return f"<div class='label-board'>{rows}</div>"


def proof_composition_for(grammar: str) -> str:
    if grammar in {"paper-atlas", "fathom-research-brief", "catalog-atelier", "takram-research-system", "stamen-data-map", "broadsheet-data-room", "signal-intelligence-brief"}:
        return "proof-atlas-spread"
    if grammar in {"atlas-marginalia", "ia-research-archive", "sumi-research-scroll"}:
        return "proof-marginalia"
    if grammar == "js-editorial-cascade":
        return "proof-stage"
    if grammar in {"evidence-atelier", "object-study-wall", "couture-exhibition", "huashu-editorial-lab", "gallery-proof-room", "maison-research-catalog"}:
        return "proof-gallery-split"
    if grammar in {"systems-field-manual", "lab-trace-ledger", "jetset-theory-grid", "swiss-systems", "cobalt-research-grid", "neo-grid-lab", "pentagram-gridnote", "huashu-build-board", "huashu-issue-broadsheet", "raw-grid-research", "stencil-field-tablet"}:
        return "proof-ledger"
    if grammar == "mono-ink-ledger":
        return "proof-atlas-spread"
    if grammar == "forest-editorial-brief":
        return "proof-gallery-split"
    if grammar == "folio-swiss-noir":
        return "proof-ledger"
    if grammar == "chromatic-research-map":
        return "proof-atlas-spread"
    if grammar in {"keynote-evidence-wall", "highsense-gallery", "broadside-lab"}:
        return "proof-stage"
    if grammar in {"academic-homepage-grid", "prism-dossier", "monograph-review", "vellum-research-note", "prism-clean-room", "prism-publication-stack", "prism-newsroom-index", "prism-workbench-index"}:
        return "proof-dossier"
    return "proof-led"


def artifact_composition_for(grammar: str, idx: int) -> str:
    if grammar in {"object-study-wall", "evidence-atelier", "forest-editorial-brief", "stamen-data-map", "couture-exhibition", "gallery-proof-room", "js-editorial-cascade", "stencil-field-tablet", "maison-research-catalog"}:
        return "artifact-showcase"
    if grammar in {"atlas-marginalia", "ia-research-archive", "broadsheet-data-room", "sumi-research-scroll", "signal-intelligence-brief"}:
        return "artifact-marginalia"
    if grammar == "mono-ink-ledger":
        return "artifact-marginalia"
    if grammar in {"systems-field-manual", "lab-trace-ledger", "cobalt-research-grid", "neo-grid-lab", "pentagram-gridnote", "huashu-editorial-lab", "huashu-build-board", "huashu-issue-broadsheet", "raw-grid-research", "folio-swiss-noir"}:
        return "artifact-ledger"
    if grammar == "chromatic-research-map":
        return "artifact-marginalia"
    if grammar in {"prism-clean-room", "prism-publication-stack", "takram-research-system", "prism-newsroom-index", "prism-workbench-index"}:
        return "artifact-dossier"
    return "artifact-dossier" if idx % 2 == 0 else "artifact-rail"


def composition_for(slide: Slide, grammar: str, idx: int) -> str:
    """Name the layout relationship, not just the slide kind."""
    requested = normalize_layout_intent(slide.layout)
    if requested:
        if requested.startswith("cover-") and slide.kind == "cover":
            return requested
        if requested.startswith("proof-") and slide.kind in {"evidence", "loop", "product"}:
            if requested == "proof-showcase":
                return proof_composition_for(grammar)
            return requested
        if requested.startswith("matrix-") and slide.kind == "matrix":
            return requested
        if requested == "spine-map" and slide.kind == "map":
            return requested
        if requested.startswith("artifact-") and slide.kind not in {"cover", "map", "matrix", "evidence", "loop", "product"}:
            if requested == "artifact-showcase":
                return artifact_composition_for(grammar, idx)
            return requested
        if requested in {"metrics-led", "content-label-board", "content-workbench-index", "text-two-col"} and slide.kind not in {
            "cover",
            "map",
            "matrix",
            "evidence",
            "loop",
            "product",
        }:
            return requested
    if slide.kind == "cover":
        if grammar in {"academic-homepage-grid", "prism-dossier", "monograph-review", "prism-clean-room", "prism-publication-stack", "ia-research-archive", "takram-research-system", "prism-newsroom-index", "prism-workbench-index", "broadsheet-data-room", "sumi-research-scroll", "signal-intelligence-brief"}:
            return "cover-source-rail"
        if grammar in {"atlas-marginalia", "object-study-wall", "mono-ink-ledger", "forest-editorial-brief"}:
            return "cover-source-rail"
        if grammar in {"keynote-evidence-wall", "highsense-gallery", "broadside-lab", "vellum-research-note", "stamen-data-map", "couture-exhibition", "gallery-proof-room", "js-editorial-cascade", "maison-research-catalog", "chromatic-research-map"}:
            return "cover-title-wall"
        if grammar in {"evidence-atelier", "systems-field-manual", "lab-trace-ledger"}:
            return "cover-title-wall"
        if grammar in {"jetset-theory-grid", "cobalt-research-grid", "neo-grid-lab", "pentagram-gridnote", "huashu-editorial-lab", "huashu-build-board", "huashu-issue-broadsheet", "raw-grid-research", "stencil-field-tablet", "folio-swiss-noir"}:
            return "cover-poster-grid"
        return "cover-title-card"
    if slide.kind in {"evidence", "loop", "product"}:
        return proof_composition_for(grammar)
    if slide.kind == "matrix":
        if grammar in {
            "swiss-systems",
            "fathom-research-brief",
            "jetset-theory-grid",
            "monograph-review",
            "broadside-lab",
            "systems-field-manual",
            "lab-trace-ledger",
            "atlas-marginalia",
            "vellum-research-note",
            "cobalt-research-grid",
            "mono-ink-ledger",
            "neo-grid-lab",
            "ia-research-archive",
            "pentagram-gridnote",
            "takram-research-system",
            "huashu-editorial-lab",
            "huashu-build-board",
            "huashu-issue-broadsheet",
            "broadsheet-data-room",
            "prism-newsroom-index",
            "prism-workbench-index",
            "sumi-research-scroll",
            "signal-intelligence-brief",
            "raw-grid-research",
            "stencil-field-tablet",
            "folio-swiss-noir",
            "chromatic-research-map",
        }:
            return "matrix-ledger"
        return "matrix-map"
    if slide.kind == "map":
        return "spine-map"
    if slide.evidence or slide.image:
        return artifact_composition_for(grammar, idx)
    if slide.metrics:
        if grammar in {"systems-field-manual", "lab-trace-ledger", "pentagram-gridnote", "takram-research-system", "huashu-editorial-lab", "huashu-issue-broadsheet"}:
            return "metrics-ledger"
        return "metrics-led"
    if slide.labels:
        if grammar in {"evidence-atelier", "object-study-wall", "forest-editorial-brief", "couture-exhibition", "js-editorial-cascade", "maison-research-catalog"}:
            return "content-bento"
        if grammar in {"atlas-marginalia", "mono-ink-ledger", "ia-research-archive", "sumi-research-scroll", "signal-intelligence-brief"}:
            return "content-marginalia"
        if grammar == "prism-workbench-index":
            return "content-workbench-index"
        if grammar in {"systems-field-manual", "lab-trace-ledger", "cobalt-research-grid", "neo-grid-lab", "pentagram-gridnote", "huashu-editorial-lab", "huashu-issue-broadsheet", "raw-grid-research", "stencil-field-tablet", "folio-swiss-noir"}:
            return "content-field-manual"
        if grammar in {"stamen-data-map", "chromatic-research-map"}:
            return "content-bento"
        return "content-label-board"
    return "text-two-col"


def image_block(s: Slide, deck: Deck, cache_dir: Path) -> str:
    path = evidence_path(s, deck, cache_dir)
    if not path:
        return "<div class='proof empty'>add one proof artifact</div>"
    evidence = s.evidence
    caption = evidence.caption if evidence else ""
    source = evidence.source if evidence else ""
    has_crop = "true" if evidence and evidence.crop else "false"
    has_caption = "true" if caption.strip() else "false"
    has_source = "true" if source.strip() else "false"
    pins = ""
    notes = ""
    if evidence and evidence.callouts:
        pins = "".join(
            f"<span class='pin' data-x='{callout.x:.4f}' data-y='{callout.y:.4f}' style='left:{callout.x * 100:.1f}%;top:{callout.y * 100:.1f}%'>{i + 1}</span>"
            for i, callout in enumerate(evidence.callouts[:3])
        )
        notes = "<ol class='proof-notes'>" + "".join(
            f"<li><span>{i + 1:02d}</span>{escape(callout.text)}</li>" for i, callout in enumerate(evidence.callouts[:3])
        ) + "</ol>"
    return (
        f"<figure class='proof' data-image-role='proof' data-has-crop='{has_crop}' data-has-caption='{has_caption}' data-has-source='{has_source}'>"
        f"<div class='proof-visual'><img src='{path.resolve().as_uri()}' alt='Evidence for {escape(s.title)}'>{pins}</div>"
        f"<figcaption><b>{escape(caption)}</b><span>{escape(source)}</span></figcaption>"
        f"{notes}"
        "</figure>"
    )


def artifact_panel(s: Slide, deck: Deck, cache_dir: Path) -> str:
    """Render a source artifact for non-evidence slides that still need proof texture."""
    path = evidence_path(s, deck, cache_dir)
    if not path:
        return ""
    evidence = s.evidence
    caption = evidence.caption if evidence and evidence.caption else "source artifact"
    source = evidence.source if evidence and evidence.source else path.name
    has_crop = "true" if evidence and evidence.crop else "false"
    has_caption = "true" if evidence and evidence.caption.strip() else "false"
    has_source = "true" if evidence and evidence.source.strip() else "false"
    pins = ""
    notes = ""
    if evidence and evidence.callouts:
        pins = "".join(
            f"<span class='pin' data-x='{callout.x:.4f}' data-y='{callout.y:.4f}' style='left:{callout.x * 100:.1f}%;top:{callout.y * 100:.1f}%'>{i + 1}</span>"
            for i, callout in enumerate(evidence.callouts[:3])
        )
        notes = "<ol class='artifact-notes'>" + "".join(
            f"<li><span>{i + 1:02d}</span>{escape(callout.text)}</li>" for i, callout in enumerate(evidence.callouts[:3])
        ) + "</ol>"
    return (
        f"<figure class='artifact-panel' data-image-role='artifact' data-has-crop='{has_crop}' data-has-caption='{has_caption}' data-has-source='{has_source}'>"
        f"<div class='artifact-visual'><img src='{path.resolve().as_uri()}' alt='Source artifact for {escape(s.title)}'>{pins}</div>"
        f"<figcaption><b>{escape(caption)}</b><span>{escape(source)}</span></figcaption>"
        f"{notes}"
        "</figure>"
    )


def render_slide(s: Slide, deck: Deck, idx: int, total: int, cache_dir: Path, grammar: str) -> str:
    dark = s.kind in {"cover", "map", "matrix", "product", "close"}
    composition = composition_for(s, grammar, idx)
    classes = f"slide {s.kind} {composition} {'dark' if dark else 'light'}"
    layout_attr = normalize_layout_intent(s.layout)
    section_open = f'<section class="{classes}" data-composition="{composition}" data-layout-intent="{layout_attr}">'
    kicker = f"<div class='kicker'>{escape(s.kicker)}</div>" if s.kicker else ""
    footer = f"<footer><span>{escape(deck.footer or deck.title)}</span><span>{idx}/{total}</span></footer>"
    if s.kind == "cover":
        cover_art = ""
        cover_path = evidence_path(s, deck, cache_dir)
        if cover_path:
            caption = s.evidence.caption if s.evidence and s.evidence.caption else "identity anchor"
            source = s.evidence.source if s.evidence and s.evidence.source else "cover source"
            has_evidence = "true" if s.evidence else "false"
            has_crop = "true" if s.evidence and s.evidence.crop else "false"
            has_caption = "true" if s.evidence and s.evidence.caption.strip() else "false"
            has_source = "true" if s.evidence and s.evidence.source.strip() else "false"
            cover_art = (
                f"<figure class='cover-art' data-image-role='cover' data-has-evidence='{has_evidence}' data-has-crop='{has_crop}' data-has-caption='{has_caption}' data-has-source='{has_source}'>"
                f"<img src='{cover_path.resolve().as_uri()}' alt='Source surface for {escape(deck.title)}'>"
                f"<figcaption><b>{escape(caption)}</b><span>{escape(source)}</span></figcaption>"
                "</figure>"
            )
        return f"""
{section_open}
  <div class="rule"></div>
  {kicker}
  <h1>{escape(deck.title)}</h1>
  <h2>{escape(s.title)}</h2>
  <p class="lead">{escape(deck.subtitle)}</p>
  <p>{escape(s.subtitle)}</p>
  <div class="tags">{''.join(f'<span>{escape(label)}</span>' for label in s.labels)}</div>
  {metrics(s.metrics)}
  {cover_art}
</section>
"""
    if s.kind in {"evidence", "loop", "product"}:
        return f"""
{section_open}
  {kicker}
  <h2>{escape(s.title)}</h2>
  <p class="subtitle">{escape(s.subtitle)}</p>
  <div class="evidence-grid">
    <aside>{bullets(s.bullets)}{metrics(s.metrics)}</aside>
    {image_block(s, deck, cache_dir)}
  </div>
  {footer}
</section>
"""
    if s.kind == "map":
        nodes = "".join(
            f"<div><span>{i+1:02d}</span><b>{escape(label)}</b></div>" for i, label in enumerate(s.labels[:5])
        )
        return f"""
{section_open}
  {kicker}
  <h2>{escape(s.title)}</h2>
  <p class="subtitle">{escape(s.subtitle)}</p>
  <div class="spine">{nodes}</div>
  <div class="case-row">{''.join(f'<p>{escape(item)}</p>' for item in s.bullets[:4])}</div>
  {footer}
</section>
"""
    if s.kind == "matrix":
        matrix_rows = parse_matrix_rows(s.labels[:8], s.bullets)
        rows = "".join(
            f"<tr><td>{i+1:02d}</td><th>{escape(label)}</th><td>{escape(failure)}</td><td>{escape(artifact)}</td></tr>"
            for i, (label, failure, artifact) in enumerate(matrix_rows)
        )
        return f"""
{section_open}
  {kicker}
  <h2>{escape(s.title)}</h2>
  <p class="subtitle">{escape(s.subtitle)}</p>
  <div class="matrix-grid">{metrics(s.metrics)}<table>{rows}</table></div>
  {footer}
</section>
"""
    side = artifact_panel(s, deck, cache_dir) or metrics(s.metrics) or labels_panel(s.labels)
    return f"""
{section_open}
  {kicker}
  <h2>{escape(s.title)}</h2>
  <p class="subtitle">{escape(s.subtitle)}</p>
  <div class="two-col">{bullets(s.bullets)}{side}</div>
  {footer}
</section>
"""


def build_html(deck: Deck, cache_dir: Path) -> str:
    total = len(deck.slides)
    grammar = normalize_grammar(deck.visual_grammar)
    slides = "\n".join(render_slide(s, deck, i, total, cache_dir, grammar) for i, s in enumerate(deck.slides, start=1))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(deck.title)}</title>
<style>
:root {{
  --paper: #{THEME.paper};
  --ink: #{THEME.ink};
  --muted: #{THEME.muted};
  --hair: #{THEME.hair};
  --navy: #{THEME.graphite};
  --gold: #{THEME.copper};
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--paper); color: var(--ink); font-family: "Helvetica Neue", Arial, sans-serif; }}
body.grammar-editorial-profile {{ --paper: #f5f1e8; --ink: #1c2430; --muted: #756f66; --hair: #d5cdc0; --navy: #172132; --gold: #bb7a36; }}
body.grammar-swiss-systems {{ --paper: #f7f8f5; --ink: #111417; --muted: #626a72; --hair: #d9dee2; --navy: #101214; --gold: #2457ff; }}
body.grammar-dark-lab-notebook {{ --paper: #11171c; --ink: #e8eef2; --muted: #98a8b3; --hair: #2b3840; --navy: #0c1014; --gold: #85d4bc; }}
body.grammar-paper-atlas {{ --paper: #fbf7ef; --ink: #2a241e; --muted: #746b61; --hair: #ded3c2; --navy: #352a22; --gold: #8c3e2d; }}
body.grammar-keynote-evidence-wall {{ --paper: #f3f0e8; --ink: #121417; --muted: #686d70; --hair: #d4cec1; --navy: #111214; --gold: #ff5a3c; }}
body.grammar-highsense-gallery {{ --paper: #eafcff; --ink: #151827; --muted: #68728a; --hair: #c9dbe6; --navy: #17203a; --gold: #2e74ff; }}
body.grammar-academic-homepage-grid {{ --paper: #fefffe; --ink: #0f172a; --muted: #64748b; --hair: #dbe3ed; --navy: #1e293b; --gold: #c9924f; }}
body.grammar-prism-dossier {{ --paper: #fbfcfa; --ink: #202838; --muted: #677084; --hair: #e2e7ef; --navy: #f4f6f8; --gold: #c8954f; }}
body.grammar-fathom-research-brief {{ --paper: #f4f7f8; --ink: #16232d; --muted: #60717d; --hair: #cad6dd; --navy: #10202c; --gold: #2f7c8c; }}
body.grammar-jetset-theory-grid {{ --paper: #f8f4e8; --ink: #0a0a0a; --muted: #4e4a42; --hair: #191919; --navy: #111111; --gold: #0057ff; }}
body.grammar-monograph-review {{ --paper: #fbfaf4; --ink: #17212b; --muted: #5f6872; --hair: #d8d4c8; --navy: #f1eee5; --gold: #846f47; }}
body.grammar-broadside-lab {{ --paper: #161410; --ink: #f5efe5; --muted: #b9ad9d; --hair: #3c342b; --navy: #100f0c; --gold: #ff5b31; }}
body.grammar-catalog-atelier {{ --paper: #f7f0e5; --ink: #20251f; --muted: #6b7166; --hair: #d7cbb8; --navy: #28362d; --gold: #9b673b; }}
body.grammar-evidence-atelier {{ --paper: #faf3e8; --ink: #17120f; --muted: #6e665d; --hair: #d8c8b3; --navy: #243a35; --gold: #b44d31; }}
body.grammar-atlas-marginalia {{ --paper: #fffdfa; --ink: #171717; --muted: #5b5b5b; --hair: #d7d7d2; --navy: #f2f2ed; --gold: #0645ad; }}
body.grammar-systems-field-manual {{ --paper: #f6f7f1; --ink: #101411; --muted: #59635c; --hair: #cfd6cc; --navy: #111a16; --gold: #d05a2a; }}
body.grammar-lab-trace-ledger {{ --paper: #111512; --ink: #e9efe7; --muted: #9aa79c; --hair: #2a352e; --navy: #0b0e0c; --gold: #b8f266; }}
body.grammar-object-study-wall {{ --paper: #f6efe5; --ink: #171717; --muted: #6b625a; --hair: #d7c7b5; --navy: #1f2528; --gold: #2c63c7; }}
body.grammar-vellum-research-note {{ --paper: #10182a; --ink: #f3ead7; --muted: #c2b7a2; --hair: #314057; --navy: #0b1020; --gold: #d7ad62; }}
body.grammar-cobalt-research-grid {{ --paper: #fbf8ec; --ink: #11131a; --muted: #5d6470; --hair: #c8d5ef; --navy: #111827; --gold: #0047ff; }}
body.grammar-mono-ink-ledger {{ --paper: #fbfaf2; --ink: #0d0d0d; --muted: #55524c; --hair: #d4d0c6; --navy: #0d0d0d; --gold: #0d0d0d; }}
body.grammar-forest-editorial-brief {{ --paper: #f7f1e7; --ink: #143322; --muted: #667265; --hair: #d8cebf; --navy: #133024; --gold: #bd6f78; }}
body.grammar-neo-grid-lab {{ --paper: #fbf7e6; --ink: #080808; --muted: #3f3f38; --hair: #080808; --navy: #080808; --gold: #d7ff2f; }}
body.grammar-prism-clean-room {{ --paper: #fcfdfb; --ink: #172033; --muted: #596579; --hair: #e4e8ef; --navy: #f6f8fb; --gold: #b38b4d; }}
body.grammar-prism-publication-stack {{ --paper: #fefffe; --ink: #0f172a; --muted: #64748b; --hair: #e2e8f0; --navy: #f8fafc; --gold: #d4a562; }}
body.grammar-ia-research-archive {{ --paper: #ffffff; --ink: #111111; --muted: #5b5b5b; --hair: #d6d6d6; --navy: #f4f4f2; --gold: #0b55c7; }}
body.grammar-pentagram-gridnote {{ --paper: #f7f5ee; --ink: #111111; --muted: #57534a; --hair: #111111; --navy: #111111; --gold: #e22b1a; }}
body.grammar-takram-research-system {{ --paper: #f8f8f4; --ink: #18201d; --muted: #68726c; --hair: #d9ddd5; --navy: #eef2ee; --gold: #2f786b; }}
body.grammar-stamen-data-map {{ --paper: #f7f0df; --ink: #1e2925; --muted: #677067; --hair: #d9cdb5; --navy: #23362f; --gold: #c36b2f; }}
body.grammar-couture-exhibition {{ --paper: #f7f1e4; --ink: #12110f; --muted: #6d665c; --hair: #d8cbb8; --navy: #f0e6d6; --gold: #8a6f45; }}
body.grammar-huashu-editorial-lab {{ --paper: #f8f3e8; --ink: #0c0c0c; --muted: #5f5b52; --hair: #111111; --navy: #111111; --gold: #d74a2f; }}
body.grammar-prism-newsroom-index {{ --paper: #fcfdfb; --ink: #111827; --muted: #667085; --hair: #e2e7df; --navy: #f5f6f1; --gold: #b18446; }}
body.grammar-prism-workbench-index {{ --paper: #fbfcf8; --ink: #101827; --muted: #647083; --hair: #dbe3d6; --navy: #f1f4ec; --gold: #a67c3f; }}
body.grammar-huashu-build-board {{ --paper: #f6f3e9; --ink: #090909; --muted: #56524a; --hair: #090909; --navy: #090909; --gold: #ef2f24; }}
body.grammar-huashu-issue-broadsheet {{ --paper: #f4f0e6; --ink: #090909; --muted: #514d45; --hair: #090909; --navy: #090909; --gold: #d6261f; }}
body.grammar-gallery-proof-room {{ --paper: #f1ede4; --ink: #171412; --muted: #736b61; --hair: #d6c9bb; --navy: #24211d; --gold: #6f8061; }}
body.grammar-broadsheet-data-room {{ --paper: #fbfaf3; --ink: #101010; --muted: #595959; --hair: #d8d3c7; --navy: #efede3; --gold: #0b55c7; }}
body.grammar-js-editorial-cascade {{ --paper: #f6f7ef; --ink: #111316; --muted: #5f655d; --hair: #d9ded1; --navy: #151618; --gold: #ff5a2d; }}
body.grammar-sumi-research-scroll {{ --paper: #fbf7ee; --ink: #17120e; --muted: #70665b; --hair: #d9cec0; --navy: #17120e; --gold: #b82f24; }}
body.grammar-signal-intelligence-brief {{ --paper: #f0ece3; --ink: #1a2030; --muted: #5a6270; --hair: #cac4b4; --navy: #1c2644; --gold: #c8a870; }}
body.grammar-raw-grid-research {{ --paper: #ffffff; --ink: #0a0a0a; --muted: #333333; --hair: #0a0a0a; --navy: #f5f5f5; --gold: #e5edd6; }}
body.grammar-stencil-field-tablet {{ --paper: #f4efe0; --ink: #0a0a0a; --muted: #4c4940; --hair: #0a0a0a; --navy: #e2dcc9; --gold: #ee7a2e; }}
body.grammar-maison-research-catalog {{ --paper: #f7f4ec; --ink: #15120e; --muted: #625b50; --hair: #d5c9b8; --navy: #15120e; --gold: #9f2a25; }}
body.grammar-folio-swiss-noir {{ --paper: #f7f5ed; --ink: #0b0b0b; --muted: #4b4740; --hair: #0b0b0b; --navy: #0b0b0b; --gold: #e2b84b; }}
body.grammar-chromatic-research-map {{ --paper: #eef7f1; --ink: #14231c; --muted: #4d665a; --hair: #b9d4c4; --navy: #10251d; --gold: #e0442e; }}
.slide {{ width: 100vw; height: 100vh; padding: 5.8vh 6.2vw 9vh; position: relative; page-break-after: always; overflow: hidden; isolation: isolate; --proof-visual-height: 48vh; --artifact-visual-height: 36vh; --cover-art-height: 17vh; }}
.slide > * {{ position: relative; z-index: 1; }}
.slide h1, .slide h2, .slide p, .slide li, .slide figcaption, .slide footer, .label-board b, .metric span {{ overflow-wrap: anywhere; hyphens: auto; }}
.slide h1, .slide h2, .slide .subtitle, .slide .lead {{ text-wrap: balance; }}
.slide .kicker + h1,
.slide .kicker + h2 {{ margin-top: clamp(.72rem, 1.35vh, 1.12rem); }}
.slide h1 + h2 {{ margin-top: clamp(1rem, 1.75vh, 1.45rem); }}
.slide h2 + .subtitle,
.slide h2 + .lead,
.cover h2 + .lead {{ margin-top: clamp(1.2rem, 2vh, 1.6rem); }}
.slide h1, .slide h2 {{ text-wrap: balance; }}
.two-col > *, .evidence-grid > *, .matrix-grid > *, .case-row > *, .spine > * {{ min-width: 0; }}
.dark {{ background: var(--navy); color: #e2dcd0; }}
.dark::before {{ content: ""; position: absolute; inset: 0; opacity: .32; background-image: linear-gradient(rgba(255,255,255,.07) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.07) 1px, transparent 1px); background-size: 8.33vw 12vh; }}
.light {{ background: var(--paper); color: var(--ink); }}
.kicker {{ color: var(--gold); font-family: Menlo, monospace; text-transform: uppercase; font-size: 0.72rem; font-weight: 700; letter-spacing: .08em; }}
h1, h2 {{ margin: .35em 0 .25em; font-family: Georgia, serif; font-weight: 500; line-height: 1.06; }}
h1 {{ font-size: clamp(3.2rem, 8vw, 7.5rem); }}
h2 {{ font-size: clamp(2.1rem, 3.8vw, 4.5rem); max-width: 74vw; }}
.cover h1 {{ max-width: 62vw; margin-bottom: .42em; }}
.cover h2 {{ max-width: 62vw; margin-top: 0; font-size: clamp(1.85rem, 3vw, 3.25rem); line-height: 1.08; }}
.cover .lead,
.cover p {{ max-width: 58vw; }}
.evidence h2, .loop h2, .product h2, .process h2, .system h2 {{ font-size: clamp(1.85rem, 3vw, 3.55rem); max-width: 84vw; line-height: 1.05; }}
p {{ color: inherit; max-width: 56rem; line-height: 1.45; }}
.subtitle, .lead {{ color: color-mix(in srgb, currentColor 72%, transparent); font-size: 1.2rem; }}
.rule {{ height: 1px; background: var(--gold); margin-bottom: 6vh; opacity: .8; }}
.tags span {{ display: inline-block; margin: 2rem 1.2rem 0 0; color: var(--gold); font-family: Menlo, monospace; font-size: .72rem; }}
.cover-art {{ position: absolute; right: 6.2vw; top: auto; bottom: 14vh; width: min(18vw, 21rem); margin: 0; padding: .6rem; border: 1px solid #53606b; background: rgba(255,255,255,.06); }}
.cover-art img {{ display: block; width: 100%; height: var(--cover-art-height); object-fit: contain; background: #fff; }}
.cover-art figcaption {{ margin-top: .85rem; color: color-mix(in srgb, currentColor 48%, transparent); font-family: Menlo, monospace; font-size: .68rem; text-transform: uppercase; line-height: 1.25; }}
.cover-source-rail {{ display: grid; grid-template-columns: minmax(16rem, 30vw) minmax(0, 1fr); column-gap: 5vw; align-items: center; }}
.cover-source-rail .rule {{ position: absolute; left: 6.2vw; right: 6.2vw; top: 5.8vh; width: auto; }}
.cover-source-rail h1,
.cover-source-rail h2,
.cover-source-rail .lead,
.cover-source-rail p,
.cover-source-rail .tags,
.cover-source-rail .metrics,
.cover-source-rail .kicker {{ grid-column: 2; max-width: none; }}
.cover-source-rail .cover-art {{ position: static; grid-column: 1; grid-row: 1 / span 8; width: 100%; bottom: auto; right: auto; }}
.cover-title-wall .cover-art {{ width: min(18vw, 21rem); bottom: 8vh; opacity: .86; }}
.cover-title-wall .cover-art img {{ height: 20vh; }}
.cover-poster-grid h1 {{ max-width: 76vw; }}
.cover-poster-grid .cover-art {{ width: min(13vw, 15rem); bottom: 9vh; }}
.metrics {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 2rem; margin-top: 5.5vh; max-width: 68vw; border-top: 1px solid color-mix(in srgb, currentColor 20%, transparent); padding-top: 1.25rem; }}
.metric {{ min-width: 0; display: grid; align-content: start; row-gap: .66rem; }}
.metric strong {{ display: block; color: var(--gold); font-family: Georgia, serif; font-size: clamp(1.8rem, 3vw, 3.2rem); font-weight: 500; line-height: 1.12; }}
.metric span {{ display: block; color: color-mix(in srgb, currentColor 64%, transparent); font-size: .8rem; line-height: 1.3; }}
ul {{ list-style: none; padding: 0; margin: 0; }}
li {{ margin: .95rem 0; line-height: 1.45; max-width: 34rem; }}
li::before {{ content: "—"; color: var(--gold); margin-right: .65rem; }}
.two-col {{ display: grid; grid-template-columns: minmax(26rem, 1.05fr) .95fr; gap: 6vw; margin-top: 5vh; align-items: start; max-height: 61vh; overflow: hidden; }}
.artifact-rail .two-col {{ grid-template-columns: minmax(22rem, .76fr) 1.24fr; gap: 4.4vw; }}
.artifact-rail .artifact-panel {{ align-self: start; }}
.artifact-rail .artifact-visual {{ height: min(43vh, var(--artifact-visual-height)); }}
.artifact-dossier .two-col {{ grid-template-columns: minmax(28rem, 1fr) minmax(0, 1fr); gap: 4.8vw; }}
.artifact-showcase .two-col {{ grid-template-columns: minmax(17rem, 24vw) minmax(0, 1fr); gap: 3vw; margin-top: 2.4vh; max-height: 67vh; }}
.artifact-showcase .two-col > ul {{ max-height: 66vh; overflow: hidden; }}
.artifact-showcase .artifact-panel {{ padding: .65rem; }}
.artifact-showcase .artifact-visual {{ height: 50vh; min-height: 20rem; max-height: 50vh; }}
.artifact-showcase .artifact-notes {{ grid-template-columns: repeat(2, minmax(0, 1fr)); font-size: .72rem; }}
.content-label-board .two-col {{ grid-template-columns: minmax(30rem, 1.02fr) .98fr; gap: 4.8vw; }}
.two-col .metrics {{ margin-top: 0; max-width: none; }}
.label-board {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .9rem; align-self: stretch; }}
.label-board div {{ min-height: 5.8rem; border: 1px solid var(--hair); background: color-mix(in srgb, var(--paper) 88%, white); padding: .9rem 1rem; display: grid; align-content: space-between; row-gap: .62rem; box-shadow: 0 10px 34px rgba(15,23,42,.05); }}
.label-board span {{ color: var(--gold); font-family: Menlo, monospace; font-size: .68rem; font-weight: 800; }}
.label-board b {{ color: currentColor; font-size: 1.12rem; line-height: 1.15; }}
.dark .label-board div {{ background: rgba(255,255,255,.045); border-color: color-mix(in srgb, currentColor 16%, transparent); box-shadow: none; }}
.evidence-grid {{ display: grid; grid-template-columns: minmax(19rem, 26vw) minmax(0, 1fr); gap: 3.6vw; align-items: start; margin-top: 2.6vh; max-height: 64vh; overflow: hidden; }}
.proof-atlas-spread .evidence-grid {{ grid-template-columns: minmax(0, 1fr) minmax(18rem, 23vw); gap: 3.2vw; }}
.proof-atlas-spread .proof {{ order: -1; }}
.proof-atlas-spread aside {{ border-left: 1px solid color-mix(in srgb, currentColor 18%, transparent); padding-left: 1.2rem; }}
.proof-stage .evidence-grid {{ grid-template-columns: minmax(16rem, 20vw) minmax(0, 1fr); gap: 3vw; }}
.proof-stage .proof-visual {{ height: 51vh; }}
.proof-dossier .evidence-grid {{ grid-template-columns: minmax(17rem, 22vw) minmax(0, 1fr); gap: 3.4vw; }}
.proof-ledger .evidence-grid {{ grid-template-columns: minmax(15rem, 19vw) minmax(0, 1fr); gap: 2.5vw; }}
.proof-showcase h2 {{ font-size: clamp(1.75rem, 2.7vw, 3.25rem); max-width: 86vw; line-height: 1.04; }}
.proof-showcase .subtitle {{ max-width: 72vw; font-size: 1.02rem; margin: .15rem 0 0; }}
.proof-showcase .evidence-grid {{ grid-template-columns: minmax(12rem, 16vw) minmax(0, 1fr); gap: 2.3vw; margin-top: 1.7vh; max-height: 70vh; }}
.proof-showcase .evidence-grid aside {{ gap: .85rem; max-height: 67vh; }}
.proof-showcase li {{ margin: .52rem 0; line-height: 1.32; max-width: 22rem; font-size: .94rem; }}
.proof-showcase .proof {{ padding: .65rem; }}
.proof-showcase .proof-visual {{ height: 58vh; min-height: 23rem; max-height: 58vh; }}
.proof-showcase .proof figcaption {{ margin-top: .55rem; font-size: .72rem; line-height: 1.2; }}
.proof-showcase .proof-notes {{ grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .42rem .8rem; margin-top: .55rem; font-size: .72rem; }}
.proof-showcase .proof-notes li {{ padding-top: .38rem; }}
.evidence-grid aside {{ display: grid; align-content: start; gap: 1.6rem; max-height: 64vh; overflow: hidden; }}
.evidence-grid aside .metrics {{ display: grid; grid-template-columns: 1fr; gap: .75rem; margin-top: .4rem; max-width: 100%; padding-top: 1rem; }}
.evidence-grid aside .metric {{ row-gap: .7rem; }}
.evidence-grid aside .metric strong {{ font-size: clamp(1.15rem, 1.9vw, 2.05rem); line-height: 1.12; }}
.evidence-grid aside .metric span {{ font-size: .68rem; line-height: 1.26; }}
.proof {{ margin: 0; border: 1px solid var(--hair); background: #fff; padding: 1rem; }}
.dark .proof {{ border-color: #2e3d5c; background: #10192e; }}
.proof-visual {{ position: relative; overflow: hidden; height: var(--proof-visual-height); min-height: 19rem; max-height: 54vh; }}
.proof img {{ display: block; position: absolute; inset: 0; width: 100%; height: 100%; max-height: none; object-fit: contain; }}
.pin {{ position: absolute; z-index: 4; transform: translate(-50%, -50%); width: 1.45rem; height: 1.45rem; border-radius: 50%; display: grid; place-items: center; background: var(--gold); color: var(--navy); font-family: Menlo, monospace; font-size: .72rem; font-weight: 800; }}
.proof figcaption {{ margin-top: .9rem; display: grid; grid-template-columns: minmax(0, .82fr) minmax(0, 1fr); align-items: start; gap: .75rem; font-size: .78rem; line-height: 1.3; color: var(--muted); }}
.proof figcaption b {{ color: var(--ink); }}
.proof figcaption b,
.proof figcaption span,
.artifact-panel figcaption b,
.artifact-panel figcaption span,
.cover-art figcaption {{ min-width: 0; overflow-wrap: anywhere; }}
.dark .proof figcaption b {{ color: #e2dcd0; }}
.proof.empty {{ min-height: 44vh; display: grid; place-items: center; font-family: Georgia, serif; font-size: 1.7rem; color: var(--muted); }}
.proof-notes {{ list-style: none; padding: 0; margin: 1rem 0 0; display: grid; gap: .55rem; color: color-mix(in srgb, currentColor 76%, transparent); font-size: .82rem; }}
.proof-notes li {{ margin: 0; max-width: none; border-top: 1px solid color-mix(in srgb, currentColor 14%, transparent); padding-top: .55rem; }}
.proof-notes li::before {{ content: none; }}
.proof-notes span {{ color: var(--gold); font-family: Menlo, monospace; margin-right: .75rem; font-size: .72rem; font-weight: 700; }}
.artifact-panel {{ margin: 0; align-self: stretch; border: 1px solid var(--hair); background: #fff; padding: .85rem; box-shadow: 0 14px 42px rgba(15,23,42,.07); overflow: hidden; }}
.dark .artifact-panel {{ border-color: color-mix(in srgb, currentColor 16%, transparent); background: rgba(255,255,255,.045); box-shadow: none; }}
.artifact-visual {{ position: relative; overflow: hidden; background: #fff; height: var(--artifact-visual-height); min-height: 13rem; max-height: 44vh; }}
.artifact-panel img {{ display: block; position: absolute; inset: 0; width: 100%; height: 100%; max-height: none; object-fit: contain; }}
.artifact-panel figcaption {{ margin-top: .75rem; display: grid; gap: .25rem; color: var(--muted); font-size: .76rem; line-height: 1.25; }}
.artifact-panel figcaption b {{ color: var(--ink); font-size: .8rem; }}
.dark .artifact-panel figcaption b {{ color: #e2dcd0; }}
.artifact-notes {{ list-style: none; padding: 0; margin: 1rem 0 0; display: grid; gap: .45rem; font-size: .78rem; color: color-mix(in srgb, currentColor 76%, transparent); }}
.artifact-notes li {{ margin: 0; max-width: none; border-top: 1px solid color-mix(in srgb, currentColor 14%, transparent); padding-top: .45rem; }}
.artifact-notes li::before {{ content: none; }}
.artifact-notes span {{ color: var(--gold); font-family: Menlo, monospace; margin-right: .65rem; font-size: .68rem; font-weight: 700; }}
.spine {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 2vw; margin-top: 10vh; }}
.spine div {{ border-top: 1px solid color-mix(in srgb, currentColor 18%, transparent); padding-top: 1.2rem; }}
.spine span {{ color: var(--gold); font-family: Menlo, monospace; font-size: .75rem; }}
.spine b {{ display: block; margin-top: 1.4rem; font-family: Georgia, serif; font-size: 2.2rem; font-weight: 500; }}
.case-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 2rem; margin-top: 9vh; color: color-mix(in srgb, currentColor 70%, transparent); }}
.matrix-grid {{ display: grid; grid-template-columns: 24vw 1fr; gap: 4vw; margin-top: 4vh; max-height: 63vh; overflow: hidden; }}
.matrix-ledger .matrix-grid {{ grid-template-columns: minmax(14rem, 20vw) minmax(0, 1fr); gap: 2.8vw; }}
.matrix-map .matrix-grid {{ grid-template-columns: minmax(18rem, 24vw) minmax(0, 1fr); }}
.matrix-grid .metrics {{ display: block; margin-top: 2vh; max-width: 16rem; border-top: 1px solid color-mix(in srgb, currentColor 18%, transparent); }}
.matrix-grid .metric {{ margin-bottom: 1.25rem; }}
.matrix-grid .metric strong {{ font-size: clamp(1.6rem, 2.5vw, 2.5rem); }}
table {{ border-collapse: collapse; width: 100%; font-size: .92rem; }}
td, th {{ border-top: 1px solid color-mix(in srgb, currentColor 16%, transparent); padding: .85rem 0; text-align: left; }}
td:first-child {{ color: var(--gold); font-family: Menlo, monospace; width: 4rem; }}
.slide > footer {{ position: absolute; bottom: .35vh; left: 6.2vw; right: 6.2vw; display: flex; justify-content: space-between; color: color-mix(in srgb, currentColor 45%, transparent); font-size: .66rem; }}
body.grammar-swiss-systems .slide {{ padding: 5.8vh 5.4vw; }}
body.grammar-swiss-systems h1,
body.grammar-swiss-systems h2 {{ font-family: "Helvetica Neue", Arial, sans-serif; font-weight: 720; line-height: 1.02; }}
body.grammar-swiss-systems .rule {{ height: 2px; margin-bottom: 7vh; }}
body.grammar-swiss-systems .metrics {{ border-top: 2px solid color-mix(in srgb, currentColor 72%, transparent); gap: 1.6rem; }}
body.grammar-swiss-systems .metric strong {{ font-family: "Helvetica Neue", Arial, sans-serif; font-weight: 760; }}
body.grammar-swiss-systems .evidence-grid {{ grid-template-columns: 24vw 1fr; gap: 3.4vw; }}
body.grammar-swiss-systems .proof {{ padding: .65rem; border-width: 2px; box-shadow: none; }}
body.grammar-swiss-systems table {{ font-size: .86rem; }}

body.grammar-dark-lab-notebook .slide {{ background: radial-gradient(circle at 78% 18%, rgba(133,212,188,.13), transparent 30%), var(--paper); color: var(--ink); }}
body.grammar-dark-lab-notebook .slide {{ --cover-art-height: 13vh; }}
body.grammar-dark-lab-notebook .dark {{ background: radial-gradient(circle at 70% 10%, rgba(133,212,188,.18), transparent 28%), var(--navy); }}
body.grammar-dark-lab-notebook h1,
body.grammar-dark-lab-notebook h2 {{ font-family: Georgia, "Times New Roman", serif; color: #f3f7f8; }}
body.grammar-dark-lab-notebook .light h2 {{ color: #f3f7f8; }}
body.grammar-dark-lab-notebook .proof {{ background: #0d1419; border-color: #31434c; box-shadow: 0 20px 70px rgba(0,0,0,.28); }}
body.grammar-dark-lab-notebook .artifact-panel {{ background: #0d1419; border-color: #31434c; box-shadow: 0 20px 70px rgba(0,0,0,.24); }}
body.grammar-dark-lab-notebook .proof figcaption b {{ color: #e8eef2; }}
body.grammar-dark-lab-notebook .artifact-panel figcaption b {{ color: #e8eef2; }}
body.grammar-dark-lab-notebook .cover-art {{ width: min(14vw, 16rem); bottom: 8vh; right: 5.4vw; }}
body.grammar-dark-lab-notebook td,
body.grammar-dark-lab-notebook th {{ border-top-color: #31434c; }}
body.grammar-dark-lab-notebook .case-row,
body.grammar-dark-lab-notebook .subtitle,
body.grammar-dark-lab-notebook .lead {{ color: #b9c6cc; }}

body.grammar-paper-atlas .slide {{ padding: 6.8vh 7vw; background: linear-gradient(90deg, rgba(140,62,45,.055) 0 1px, transparent 1px 100%), var(--paper); background-size: 6.66vw 100%; }}
body.grammar-paper-atlas .dark {{ background: linear-gradient(90deg, rgba(251,247,239,.05) 0 1px, transparent 1px 100%), #352a22; background-size: 6.66vw 100%; color: #f7efe4; }}
body.grammar-paper-atlas .dark h1,
body.grammar-paper-atlas .dark h2 {{ color: #f7efe4; }}
body.grammar-paper-atlas h1,
body.grammar-paper-atlas h2,
body.grammar-paper-atlas .spine b,
body.grammar-paper-atlas .metric strong {{ font-family: "Iowan Old Style", Georgia, serif; }}
body.grammar-paper-atlas .cover h2 {{ margin-top: .82em; }}
body.grammar-paper-atlas .kicker {{ color: #8c3e2d; }}
body.grammar-paper-atlas .proof {{ padding: 1.15rem; border-color: #cbb9a2; box-shadow: 0 18px 50px rgba(72,48,28,.12); }}
body.grammar-paper-atlas .artifact-panel {{ border-color: #cbb9a2; box-shadow: 0 18px 50px rgba(72,48,28,.10); }}
body.grammar-paper-atlas .evidence-grid {{ grid-template-columns: 30vw 1fr; }}
body.grammar-paper-atlas .matrix-grid {{ grid-template-columns: 28vw 1fr; }}
body.grammar-paper-atlas footer {{ left: 7vw; right: 7vw; }}

body.grammar-keynote-evidence-wall .slide {{ padding: 5.4vh 5vw; }}
body.grammar-keynote-evidence-wall .slide {{ --proof-visual-height: 50vh; --artifact-visual-height: 36vh; }}
body.grammar-keynote-evidence-wall h1 {{ max-width: 62vw; font-size: clamp(3rem, 7vw, 6.8rem); }}
body.grammar-keynote-evidence-wall .cover h2 {{ max-width: 62vw; font-size: clamp(1.9rem, 3.2vw, 3.4rem); }}
body.grammar-keynote-evidence-wall h2 {{ max-width: 72vw; font-size: clamp(2.2rem, 4.1vw, 4.8rem); }}
body.grammar-keynote-evidence-wall .evidence h2,
body.grammar-keynote-evidence-wall .loop h2,
body.grammar-keynote-evidence-wall .product h2 {{ max-width: 64vw; font-size: clamp(2rem, 3.2vw, 3.8rem); }}
body.grammar-keynote-evidence-wall .evidence-grid {{ grid-template-columns: 20vw 1fr; gap: 3vw; margin-top: 2.4vh; }}
body.grammar-keynote-evidence-wall .proof {{ padding: .45rem; border: 0; box-shadow: 0 24px 70px rgba(17,18,20,.24); }}
body.grammar-keynote-evidence-wall .artifact-panel {{ padding: .55rem; border: 0; box-shadow: 0 24px 70px rgba(17,18,20,.18); }}
body.grammar-keynote-evidence-wall .proof figcaption {{ padding: 0 .45rem .2rem; }}
body.grammar-keynote-evidence-wall .dark .proof figcaption,
body.grammar-keynote-evidence-wall .dark .artifact-panel figcaption {{ color: #686d70; }}
body.grammar-keynote-evidence-wall .dark .proof figcaption b,
body.grammar-keynote-evidence-wall .dark .artifact-panel figcaption b {{ color: #121417; }}
body.grammar-keynote-evidence-wall .metrics {{ max-width: 54vw; margin-top: 6vh; grid-template-columns: repeat(3, minmax(0, 1fr)); }}
body.grammar-keynote-evidence-wall footer {{ left: 5vw; right: 5vw; }}

body.grammar-highsense-gallery .light {{ background: linear-gradient(135deg, #eafcff 0%, #f6f0ff 42%, #fff7e1 100%); }}
body.grammar-highsense-gallery .dark {{ background: linear-gradient(135deg, #111a34 0%, #163443 48%, #34233a 100%); }}
body.grammar-highsense-gallery .slide::after {{ content: ""; position: absolute; inset: 5.4vh 4.8vw; border: 1px solid rgba(255,255,255,.38); box-shadow: 0 24px 90px rgba(35,74,115,.12); pointer-events: none; z-index: 0; }}
body.grammar-highsense-gallery .dark::after {{ border-color: rgba(255,255,255,.12); box-shadow: 0 24px 90px rgba(0,0,0,.24); }}
body.grammar-highsense-gallery .rule {{ width: 18vw; height: 3px; background: linear-gradient(90deg, #2e74ff, #f2b25e); }}
body.grammar-highsense-gallery h1,
body.grammar-highsense-gallery h2 {{ font-family: "Avenir Next", "Helvetica Neue", Arial, sans-serif; font-weight: 760; }}
body.grammar-highsense-gallery .proof {{ border: 0; box-shadow: 0 22px 80px rgba(43,83,126,.18); background: rgba(255,255,255,.82); }}
body.grammar-highsense-gallery .artifact-panel {{ border: 0; box-shadow: 0 22px 80px rgba(43,83,126,.16); background: rgba(255,255,255,.82); }}
body.grammar-highsense-gallery .dark .proof {{ background: rgba(12,18,34,.78); }}
body.grammar-highsense-gallery .dark .artifact-panel {{ background: rgba(12,18,34,.78); }}
body.grammar-highsense-gallery .evidence-grid {{ grid-template-columns: 24vw 1fr; }}
body.grammar-keynote-evidence-wall .evidence-grid aside .metrics,
body.grammar-highsense-gallery .evidence-grid aside .metrics {{ grid-template-columns: 1fr; margin-top: .4rem; max-width: 100%; gap: .75rem; }}
body.grammar-keynote-evidence-wall .evidence-grid aside .metric strong,
body.grammar-highsense-gallery .evidence-grid aside .metric strong {{ font-size: clamp(1.05rem, 1.7vw, 1.85rem); line-height: 1; }}

body.grammar-academic-homepage-grid .slide {{ padding: 5.6vh 6vw 8vh; background: var(--paper); color: var(--ink); }}
body.grammar-academic-homepage-grid .slide {{ --cover-art-height: 36vh; --proof-visual-height: 50vh; --artifact-visual-height: 40vh; }}
body.grammar-academic-homepage-grid .dark {{ background: #f8fafc; color: var(--ink); }}
body.grammar-academic-homepage-grid .dark::before {{ opacity: .14; background-image: linear-gradient(rgba(15,23,42,.045) 1px, transparent 1px), linear-gradient(90deg, rgba(15,23,42,.045) 1px, transparent 1px); }}
body.grammar-academic-homepage-grid h1,
body.grammar-academic-homepage-grid h2,
body.grammar-academic-homepage-grid .metric strong,
body.grammar-academic-homepage-grid .spine b {{ font-family: "Georgia CDN", Georgia, serif; font-weight: 700; color: #1e293b; }}
body.grammar-academic-homepage-grid .kicker {{ color: #c9924f; }}
body.grammar-academic-homepage-grid .cover {{ display: grid; grid-template-columns: 30vw 1fr; column-gap: 5vw; align-items: center; }}
body.grammar-academic-homepage-grid .cover .rule {{ position: absolute; top: 5.6vh; left: 6vw; right: 6vw; width: auto; }}
body.grammar-academic-homepage-grid .cover h1,
body.grammar-academic-homepage-grid .cover h2,
body.grammar-academic-homepage-grid .cover .lead,
body.grammar-academic-homepage-grid .cover p,
body.grammar-academic-homepage-grid .cover .tags,
body.grammar-academic-homepage-grid .cover .metrics {{ grid-column: 2; max-width: none; }}
body.grammar-academic-homepage-grid .cover h1 {{ font-size: clamp(3rem, 5.4vw, 5.8rem); }}
body.grammar-academic-homepage-grid .cover h2 {{ font-size: clamp(1.8rem, 2.9vw, 3.05rem); }}
body.grammar-academic-homepage-grid .cover-art {{ position: static; grid-column: 1; grid-row: 1 / span 8; width: 100%; padding: .9rem; border-color: #dbe3ed; background: #f8fafc; box-shadow: 0 18px 48px rgba(15,23,42,.11); }}
body.grammar-academic-homepage-grid .cover .metrics {{ max-width: none; grid-template-columns: repeat(3, minmax(0, 1fr)); margin-top: 4vh; }}
body.grammar-academic-homepage-grid .tags span {{ color: #64748b; margin-top: 1.4rem; }}
body.grammar-academic-homepage-grid .two-col {{ grid-template-columns: minmax(30rem, .95fr) 1.05fr; gap: 4vw; margin-top: 4vh; }}
body.grammar-academic-homepage-grid .label-board div,
body.grammar-academic-homepage-grid .proof,
body.grammar-academic-homepage-grid .artifact-panel {{ background: #f8fafc; border-color: #dbe3ed; border-radius: 8px; box-shadow: 0 10px 30px rgba(15,23,42,.06); }}
body.grammar-academic-homepage-grid .dark .proof figcaption,
body.grammar-academic-homepage-grid .dark .artifact-panel figcaption {{ color: #64748b; }}
body.grammar-academic-homepage-grid .dark .proof figcaption b,
body.grammar-academic-homepage-grid .dark .artifact-panel figcaption b {{ color: #1e293b; }}
body.grammar-academic-homepage-grid .evidence-grid {{ grid-template-columns: 23vw 1fr; gap: 3.4vw; }}
body.grammar-academic-homepage-grid .matrix-grid {{ grid-template-columns: 21vw 1fr; }}
body.grammar-academic-homepage-grid td,
body.grammar-academic-homepage-grid th {{ border-top-color: #dbe3ed; }}

body.grammar-prism-dossier .slide {{ padding: 4.8vh 5vw 7vh; background: var(--paper); color: var(--ink); }}
body.grammar-prism-dossier .slide {{ --cover-art-height: 39vh; --proof-visual-height: 52vh; --artifact-visual-height: 41vh; }}
body.grammar-prism-dossier .dark {{ background: #f6f8fb; color: var(--ink); }}
body.grammar-prism-dossier .dark::before {{ opacity: .08; background-size: 7.5vw 10vh; }}
body.grammar-prism-dossier h1,
body.grammar-prism-dossier h2,
body.grammar-prism-dossier .metric strong,
body.grammar-prism-dossier .spine b {{ font-family: "Georgia CDN", Georgia, serif; font-weight: 700; color: #202838; }}
body.grammar-prism-dossier .kicker {{ color: #c8954f; }}
body.grammar-prism-dossier .cover {{ display: grid; grid-template-columns: 31vw 1fr; grid-template-rows: auto auto auto auto 1fr auto; column-gap: 5.5vw; align-items: center; }}
body.grammar-prism-dossier .cover .rule {{ position: absolute; left: 5vw; right: 5vw; top: 4.8vh; width: auto; background: #e2e7ef; }}
body.grammar-prism-dossier .cover h1,
body.grammar-prism-dossier .cover h2,
body.grammar-prism-dossier .cover .lead,
body.grammar-prism-dossier .cover p,
body.grammar-prism-dossier .cover .tags,
body.grammar-prism-dossier .cover .metrics {{ grid-column: 2; max-width: 58vw; }}
body.grammar-prism-dossier .cover h1 {{ font-size: clamp(3.1rem, 5.8vw, 6.3rem); }}
body.grammar-prism-dossier .cover h2 {{ font-size: clamp(1.55rem, 2.4vw, 2.75rem); line-height: 1.08; color: #202838; }}
body.grammar-prism-dossier .cover-art {{ position: static; grid-column: 1; grid-row: 1 / span 6; width: 100%; padding: .95rem; background: #fff; border-color: #e2e7ef; border-radius: 8px; box-shadow: 0 22px 56px rgba(32,40,56,.12); }}
body.grammar-prism-dossier .cover-art img {{ border-radius: 6px; }}
body.grammar-prism-dossier .cover .metrics {{ grid-template-columns: repeat(3, minmax(0, 1fr)); margin-top: 3.6vh; border-top-color: #e2e7ef; }}
body.grammar-prism-dossier .two-col {{ grid-template-columns: minmax(27rem, .86fr) 1.14fr; gap: 4.3vw; margin-top: 4.2vh; }}
body.grammar-prism-dossier .label-board {{ grid-template-columns: 1fr; }}
body.grammar-prism-dossier .label-board div,
body.grammar-prism-dossier .proof,
body.grammar-prism-dossier .artifact-panel {{ background: #fff; border-color: #e2e7ef; border-radius: 8px; box-shadow: 0 14px 38px rgba(32,40,56,.07); }}
body.grammar-prism-dossier .dark .proof figcaption,
body.grammar-prism-dossier .dark .artifact-panel figcaption {{ color: #677084; }}
body.grammar-prism-dossier .dark .proof figcaption b,
body.grammar-prism-dossier .dark .artifact-panel figcaption b {{ color: #202838; }}
body.grammar-prism-dossier .artifact-panel img,
body.grammar-prism-dossier .proof img {{ border-radius: 6px; }}
body.grammar-prism-dossier .evidence-grid {{ grid-template-columns: 22vw 1fr; gap: 3.5vw; }}
body.grammar-prism-dossier .matrix-grid {{ grid-template-columns: 19vw 1fr; gap: 3.4vw; }}
body.grammar-prism-dossier table {{ font-size: .86rem; }}
body.grammar-prism-dossier td,
body.grammar-prism-dossier th {{ border-top-color: #e2e7ef; }}

body.grammar-fathom-research-brief .slide {{ padding: 5.2vh 5.2vw 7.4vh; background: var(--paper); color: var(--ink); }}
body.grammar-fathom-research-brief .slide {{ --proof-visual-height: 53vh; --artifact-visual-height: 42vh; }}
body.grammar-fathom-research-brief .slide::after {{ content: ""; position: absolute; inset: 4.6vh 5.2vw auto; height: 1px; background: var(--hair); pointer-events: none; }}
body.grammar-fathom-research-brief .dark {{ background: #10202c; color: #eef5f7; }}
body.grammar-fathom-research-brief .dark::before {{ opacity: .18; background-size: 6vw 8vh; }}
body.grammar-fathom-research-brief h1,
body.grammar-fathom-research-brief h2 {{ font-family: "Helvetica Neue", Arial, sans-serif; font-weight: 760; line-height: 1; color: currentColor; }}
body.grammar-fathom-research-brief h1 {{ font-size: clamp(3rem, 6.9vw, 7rem); }}
body.grammar-fathom-research-brief h2 {{ max-width: 78vw; font-size: clamp(2rem, 3.6vw, 4.15rem); line-height: 1.04; }}
body.grammar-fathom-research-brief .kicker {{ color: var(--gold); letter-spacing: 0; }}
body.grammar-fathom-research-brief .metrics {{ grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1.1rem; max-width: 74vw; }}
body.grammar-fathom-research-brief .metric {{ border-left: 2px solid color-mix(in srgb, var(--gold) 45%, transparent); padding-left: .8rem; }}
body.grammar-fathom-research-brief .metric strong {{ font-family: "Helvetica Neue", Arial, sans-serif; font-size: clamp(1.35rem, 2.4vw, 2.65rem); color: var(--gold); }}
body.grammar-fathom-research-brief .two-col {{ grid-template-columns: minmax(28rem, .92fr) 1.08fr; gap: 4vw; margin-top: 3.8vh; }}
body.grammar-fathom-research-brief li {{ max-width: 39rem; }}
body.grammar-fathom-research-brief .label-board {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
body.grammar-fathom-research-brief .label-board div,
body.grammar-fathom-research-brief .proof,
body.grammar-fathom-research-brief .artifact-panel {{ background: rgba(255,255,255,.74); border-color: #cad6dd; box-shadow: none; }}
body.grammar-fathom-research-brief .evidence-grid {{ grid-template-columns: 25vw 1fr; gap: 3.2vw; margin-top: 2.2vh; }}
body.grammar-fathom-research-brief .evidence-grid aside .metrics {{ grid-template-columns: 1fr; gap: .72rem; max-width: 100%; border-top: 1px solid color-mix(in srgb, currentColor 18%, transparent); padding-top: .9rem; }}
body.grammar-fathom-research-brief .evidence-grid aside .metric strong {{ font-size: clamp(1.05rem, 1.65vw, 1.85rem); line-height: 1; }}
body.grammar-fathom-research-brief .matrix-grid {{ grid-template-columns: 23vw 1fr; gap: 3vw; }}
body.grammar-fathom-research-brief table {{ font-size: .84rem; background: rgba(255,255,255,.46); }}
body.grammar-fathom-research-brief td,
body.grammar-fathom-research-brief th {{ border-top-color: #cad6dd; padding: .72rem 0; }}
body.grammar-fathom-research-brief .cover .tags {{ max-width: 50vw; }}
body.grammar-fathom-research-brief .cover-art {{ right: 5.2vw; bottom: 11vh; width: min(15vw, 17rem); border-color: #cad6dd; background: #fff; }}

body.grammar-jetset-theory-grid .slide {{ padding: 4.7vh 4.8vw 7.2vh; background: linear-gradient(90deg, rgba(10,10,10,.12) 0 1px, transparent 1px 100%), var(--paper); background-size: 8.333vw 100%; color: var(--ink); }}
body.grammar-jetset-theory-grid .slide {{ --proof-visual-height: 51vh; --artifact-visual-height: 39vh; }}
body.grammar-jetset-theory-grid .dark {{ background: linear-gradient(90deg, rgba(248,244,232,.12) 0 1px, transparent 1px 100%), #111; color: #f8f4e8; }}
body.grammar-jetset-theory-grid .dark::before {{ display: none; }}
body.grammar-jetset-theory-grid h1,
body.grammar-jetset-theory-grid h2,
body.grammar-jetset-theory-grid .metric strong,
body.grammar-jetset-theory-grid .spine b {{ font-family: "Helvetica Neue", Arial, sans-serif; font-weight: 820; line-height: 1.02; color: currentColor; }}
body.grammar-jetset-theory-grid h1 {{ max-width: 72vw; font-size: clamp(3.2rem, 7.8vw, 8.2rem); }}
body.grammar-jetset-theory-grid h2 {{ max-width: 82vw; font-size: clamp(2.15rem, 4.2vw, 5rem); }}
body.grammar-jetset-theory-grid .cover h2 {{ max-width: 70vw; }}
body.grammar-jetset-theory-grid .kicker {{ display: inline-block; background: #0057ff; color: #fff; padding: .22rem .5rem; letter-spacing: 0; }}
body.grammar-jetset-theory-grid .rule {{ height: 4px; width: 24vw; background: #e3262f; margin-bottom: 4vh; }}
body.grammar-jetset-theory-grid .subtitle,
body.grammar-jetset-theory-grid .lead {{ color: color-mix(in srgb, currentColor 74%, transparent); }}
body.grammar-jetset-theory-grid .metrics {{ grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0; border: 3px solid currentColor; padding: 0; max-width: 68vw; }}
body.grammar-jetset-theory-grid .metric {{ padding: 1rem; border-right: 3px solid currentColor; }}
body.grammar-jetset-theory-grid .metric:last-child {{ border-right: 0; }}
body.grammar-jetset-theory-grid .metric strong {{ color: #e3262f; }}
body.grammar-jetset-theory-grid .two-col {{ grid-template-columns: minmax(28rem, .9fr) 1.1fr; gap: 3vw; margin-top: 4vh; }}
body.grammar-jetset-theory-grid li::before {{ content: "■"; color: #0057ff; }}
body.grammar-jetset-theory-grid .label-board div,
body.grammar-jetset-theory-grid .proof,
body.grammar-jetset-theory-grid .artifact-panel {{ background: #fffdf5; border: 3px solid currentColor; border-radius: 0; box-shadow: none; }}
body.grammar-jetset-theory-grid .evidence-grid {{ grid-template-columns: 20vw 1fr; gap: 2.8vw; }}
body.grammar-jetset-theory-grid .evidence-grid aside .metrics {{ grid-template-columns: 1fr; gap: 0; max-width: 100%; border: 3px solid currentColor; }}
body.grammar-jetset-theory-grid .evidence-grid aside .metric {{ padding: .55rem .7rem; border-right: 0; border-bottom: 3px solid currentColor; }}
body.grammar-jetset-theory-grid .evidence-grid aside .metric:last-child {{ border-bottom: 0; }}
body.grammar-jetset-theory-grid .evidence-grid aside .metric strong {{ font-size: clamp(.95rem, 1.45vw, 1.62rem); line-height: 1; }}
body.grammar-jetset-theory-grid .evidence-grid aside .metric span {{ font-size: .64rem; }}
body.grammar-jetset-theory-grid .matrix-grid {{ grid-template-columns: 18vw 1fr; gap: 2.5vw; }}
body.grammar-jetset-theory-grid table {{ font-size: .82rem; background: #fffdf5; border: 3px solid currentColor; }}
body.grammar-jetset-theory-grid td,
body.grammar-jetset-theory-grid th {{ border-top: 3px solid currentColor; padding: .58rem .45rem; }}
body.grammar-jetset-theory-grid .cover .tags {{ max-width: 52vw; }}
body.grammar-jetset-theory-grid .cover-art {{ right: 4.8vw; bottom: 10vh; width: min(15vw, 17rem); border: 3px solid currentColor; background: #fffdf5; box-shadow: none; }}
body.grammar-jetset-theory-grid footer {{ color: color-mix(in srgb, currentColor 60%, transparent); }}

body.grammar-monograph-review .slide {{ padding: 5.1vh 6vw 7.6vh; background: var(--paper); color: var(--ink); }}
body.grammar-monograph-review .slide {{ --cover-art-height: 34vh; --proof-visual-height: 52vh; --artifact-visual-height: 43vh; }}
body.grammar-monograph-review .dark {{ background: var(--paper); color: var(--ink); }}
body.grammar-monograph-review .dark::before {{ opacity: .16; background-image: linear-gradient(rgba(23,33,43,.045) 1px, transparent 1px); background-size: 100% 7.2vh; }}
body.grammar-monograph-review h1,
body.grammar-monograph-review h2,
body.grammar-monograph-review .metric strong,
body.grammar-monograph-review .spine b {{ font-family: "Georgia CDN", Georgia, serif; font-weight: 700; color: #17212b; letter-spacing: 0; }}
body.grammar-monograph-review h1 {{ font-size: clamp(3.4rem, 6.5vw, 7.1rem); line-height: .98; }}
body.grammar-monograph-review h2 {{ font-size: clamp(2rem, 3.35vw, 4.05rem); max-width: 80vw; line-height: 1.04; }}
body.grammar-monograph-review .kicker {{ color: #846f47; letter-spacing: .02em; }}
body.grammar-monograph-review .rule {{ background: #d8d4c8; margin-bottom: 4.6vh; }}
body.grammar-monograph-review .subtitle,
body.grammar-monograph-review .lead {{ color: #4f5b66; }}
body.grammar-monograph-review .cover {{ display: grid; grid-template-columns: 28vw 1fr; column-gap: 5.2vw; align-items: center; }}
body.grammar-monograph-review .cover .rule {{ position: absolute; left: 6vw; right: 6vw; top: 5.1vh; width: auto; }}
body.grammar-monograph-review .cover h1,
body.grammar-monograph-review .cover h2,
body.grammar-monograph-review .cover .lead,
body.grammar-monograph-review .cover p,
body.grammar-monograph-review .cover .tags,
body.grammar-monograph-review .cover .metrics,
body.grammar-monograph-review .cover .kicker {{ grid-column: 2; max-width: none; }}
body.grammar-monograph-review .cover-art {{ position: static; grid-column: 1; grid-row: 1 / span 8; width: 100%; padding: 0; border: 0; border-bottom: 1px solid #d8d4c8; background: transparent; box-shadow: none; }}
body.grammar-monograph-review .cover-art img {{ object-fit: contain; border: 1px solid #d8d4c8; background: #fff; }}
body.grammar-monograph-review .metrics {{ max-width: none; gap: 1rem; border-top-color: #d8d4c8; }}
body.grammar-monograph-review .metric strong {{ font-size: clamp(1.45rem, 2.4vw, 2.65rem); }}
body.grammar-monograph-review .two-col {{ grid-template-columns: minmax(30rem, .9fr) 1.1fr; gap: 3.8vw; margin-top: 3.6vh; }}
body.grammar-monograph-review .label-board {{ grid-template-columns: 1fr; gap: .55rem; }}
body.grammar-monograph-review .label-board div,
body.grammar-monograph-review .proof,
body.grammar-monograph-review .artifact-panel {{ background: #fffef9; border-color: #d8d4c8; border-radius: 0; box-shadow: none; }}
body.grammar-monograph-review .label-board div {{ min-height: 4.4rem; padding: .75rem .9rem; }}
body.grammar-monograph-review .evidence-grid {{ grid-template-columns: minmax(17rem, 22vw) minmax(0, 1fr); gap: 3vw; }}
body.grammar-monograph-review .matrix-grid {{ grid-template-columns: minmax(16rem, 20vw) minmax(0, 1fr); gap: 3vw; }}
body.grammar-monograph-review table {{ font-size: .86rem; }}
body.grammar-monograph-review td,
body.grammar-monograph-review th {{ border-top-color: #d8d4c8; padding: .68rem 0; }}

body.grammar-broadside-lab .slide {{ padding: 4.9vh 5vw 7vh; background: #161410; color: #f5efe5; }}
body.grammar-broadside-lab .slide {{ --cover-art-height: 22vh; --proof-visual-height: 54vh; --artifact-visual-height: 43vh; }}
body.grammar-broadside-lab .light,
body.grammar-broadside-lab .dark {{ background: #161410; color: #f5efe5; }}
body.grammar-broadside-lab .dark::before,
body.grammar-broadside-lab .light::before {{ opacity: .12; background-image: linear-gradient(90deg, rgba(245,239,229,.12) 0 1px, transparent 1px 100%); background-size: 8.333vw 100%; }}
body.grammar-broadside-lab h1,
body.grammar-broadside-lab h2,
body.grammar-broadside-lab .metric strong,
body.grammar-broadside-lab .spine b {{ font-family: "Helvetica Neue", Arial, sans-serif; font-weight: 830; color: #f5efe5; letter-spacing: 0; line-height: 1.02; }}
body.grammar-broadside-lab h1 {{ font-size: clamp(3.6rem, 8vw, 8.5rem); max-width: 74vw; }}
body.grammar-broadside-lab h2 {{ font-size: clamp(2rem, 4.15vw, 5rem); max-width: 78vw; }}
body.grammar-broadside-lab .kicker {{ display: inline-block; color: #ff5b31; letter-spacing: 0; border-bottom: 2px solid #ff5b31; padding-bottom: .18rem; }}
body.grammar-broadside-lab .rule {{ height: 3px; width: 22vw; background: #ff5b31; margin-bottom: 4.2vh; }}
body.grammar-broadside-lab .subtitle,
body.grammar-broadside-lab .lead,
body.grammar-broadside-lab p {{ color: color-mix(in srgb, currentColor 76%, transparent); }}
body.grammar-broadside-lab .tags span,
body.grammar-broadside-lab .metric strong,
body.grammar-broadside-lab td:first-child {{ color: #ff5b31; }}
body.grammar-broadside-lab .metrics {{ border-top-color: rgba(245,239,229,.22); max-width: 78vw; }}
body.grammar-broadside-lab .cover .metrics {{ max-width: 68vw; }}
body.grammar-broadside-lab .metric strong {{ display: block; line-height: 1.04; }}
body.grammar-broadside-lab .metric span {{ display: block; line-height: 1.28; color: #b9ad9d; }}
body.grammar-broadside-lab .two-col {{ grid-template-columns: minmax(25rem, .72fr) 1.28fr; gap: 3vw; margin-top: 4.2vh; }}
body.grammar-broadside-lab .label-board div,
body.grammar-broadside-lab .proof,
body.grammar-broadside-lab .artifact-panel {{ background: #1d1a15; border-color: #3c342b; border-radius: 0; box-shadow: none; }}
body.grammar-broadside-lab .label-board div {{ min-height: 4.9rem; }}
body.grammar-broadside-lab .label-board span,
body.grammar-broadside-lab .proof-notes span,
body.grammar-broadside-lab .artifact-notes span {{ color: #ff5b31; }}
body.grammar-broadside-lab .proof figcaption,
body.grammar-broadside-lab .artifact-panel figcaption {{ color: #b9ad9d; }}
body.grammar-broadside-lab .proof figcaption b,
body.grammar-broadside-lab .artifact-panel figcaption b {{ color: #f5efe5; }}
body.grammar-broadside-lab .evidence-grid {{ grid-template-columns: minmax(13rem, 18vw) minmax(0, 1fr); gap: 2.8vw; }}
body.grammar-broadside-lab .matrix-grid {{ grid-template-columns: minmax(14rem, 18vw) minmax(0, 1fr); gap: 2.6vw; }}
body.grammar-broadside-lab table {{ font-size: .82rem; background: #1d1a15; }}
body.grammar-broadside-lab td,
body.grammar-broadside-lab th {{ border-top-color: #3c342b; padding: .62rem .2rem; color: #f5efe5; }}
body.grammar-broadside-lab .cover-art {{ width: min(14vw, 17rem); bottom: 8vh; right: 5vw; border-color: #3c342b; background: #1d1a15; }}
body.grammar-broadside-lab footer {{ left: 5vw; right: 5vw; color: rgba(245,239,229,.45); }}

body.grammar-catalog-atelier .slide {{ padding: 5.5vh 6vw 7.8vh; background: var(--paper); color: var(--ink); }}
body.grammar-catalog-atelier .slide {{ --cover-art-height: 28vh; --proof-visual-height: 52vh; --artifact-visual-height: 42vh; }}
body.grammar-catalog-atelier .dark {{ background: #28362d; color: #f7f0e5; }}
body.grammar-catalog-atelier .dark::before {{ opacity: .16; background-size: 7vw 9vh; }}
body.grammar-catalog-atelier h1,
body.grammar-catalog-atelier h2,
body.grammar-catalog-atelier .metric strong,
body.grammar-catalog-atelier .spine b {{ font-family: "Iowan Old Style", Georgia, serif; font-weight: 700; letter-spacing: 0; }}
body.grammar-catalog-atelier h1 {{ font-size: clamp(3.2rem, 6.8vw, 7.4rem); line-height: .98; }}
body.grammar-catalog-atelier h2 {{ font-size: clamp(2rem, 3.65vw, 4.45rem); max-width: 80vw; }}
body.grammar-catalog-atelier .kicker {{ color: #9b673b; letter-spacing: .04em; }}
body.grammar-catalog-atelier .rule {{ width: 16vw; height: 2px; background: #9b673b; }}
body.grammar-catalog-atelier .cover .tags {{ max-width: 50vw; }}
body.grammar-catalog-atelier .cover-art {{ width: min(15vw, 17rem); bottom: 8vh; right: 6vw; border-color: #d7cbb8; background: #fffaf1; box-shadow: 0 18px 45px rgba(55,42,26,.12); }}
body.grammar-catalog-atelier .metrics {{ border-top-color: #d7cbb8; max-width: 72vw; }}
body.grammar-catalog-atelier .metric strong {{ color: #9b673b; }}
body.grammar-catalog-atelier .two-col {{ grid-template-columns: minmax(25rem, .8fr) 1.2fr; gap: 4.6vw; margin-top: 4vh; }}
body.grammar-catalog-atelier .label-board {{ grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .75rem; }}
body.grammar-catalog-atelier .label-board div,
body.grammar-catalog-atelier .proof,
body.grammar-catalog-atelier .artifact-panel {{ background: #fffaf1; border-color: #d7cbb8; border-radius: 2px; box-shadow: 0 12px 34px rgba(55,42,26,.08); }}
body.grammar-catalog-atelier .evidence-grid {{ grid-template-columns: minmax(0, 1fr) minmax(17rem, 23vw); gap: 3vw; }}
body.grammar-catalog-atelier .proof-atlas-spread .proof {{ order: -1; }}
body.grammar-catalog-atelier .matrix-grid {{ grid-template-columns: minmax(18rem, 24vw) minmax(0, 1fr); }}
body.grammar-catalog-atelier table {{ font-size: .86rem; background: rgba(255,250,241,.54); }}
body.grammar-catalog-atelier td,
body.grammar-catalog-atelier th {{ border-top-color: #d7cbb8; }}

body.grammar-evidence-atelier .slide {{ padding: 5.2vh 5.6vw 7.2vh; background: linear-gradient(90deg, rgba(180,77,49,.08) 0 1px, transparent 1px 100%), var(--paper); background-size: 12.5vw 100%; color: var(--ink); }}
body.grammar-evidence-atelier .slide {{ --proof-visual-height: 57vh; --artifact-visual-height: 48vh; --cover-art-height: 22vh; }}
body.grammar-evidence-atelier .dark {{ background: #243a35; color: #faf3e8; }}
body.grammar-evidence-atelier .dark::before {{ opacity: .12; background-size: 12.5vw 10vh; }}
body.grammar-evidence-atelier h1,
body.grammar-evidence-atelier h2,
body.grammar-evidence-atelier .metric strong,
body.grammar-evidence-atelier .spine b {{ font-family: "Iowan Old Style", Georgia, serif; font-weight: 700; letter-spacing: 0; }}
body.grammar-evidence-atelier h1 {{ font-size: clamp(3.2rem, 7.5vw, 8.1rem); line-height: .99; max-width: 70vw; }}
body.grammar-evidence-atelier h2 {{ font-size: clamp(2rem, 3.95vw, 4.7rem); max-width: 78vw; line-height: 1.03; }}
body.grammar-evidence-atelier .kicker {{ color: #b44d31; letter-spacing: .03em; }}
body.grammar-evidence-atelier .rule {{ width: 18vw; height: 2px; background: #b44d31; margin-bottom: 4.6vh; }}
body.grammar-evidence-atelier .metrics {{ max-width: 74vw; border-top-color: #d8c8b3; gap: 1.2rem; }}
body.grammar-evidence-atelier .metric strong {{ color: #b44d31; }}
body.grammar-evidence-atelier .cover-art {{ right: 5.6vw; bottom: 8vh; width: min(16vw, 18rem); border-color: #d8c8b3; background: #fffaf2; box-shadow: 0 18px 44px rgba(60,38,20,.12); }}
body.grammar-evidence-atelier .two-col {{ grid-template-columns: minmax(24rem, .78fr) 1.22fr; gap: 4vw; margin-top: 4vh; }}
body.grammar-evidence-atelier .label-board {{ grid-template-columns: 1.18fr .82fr; gap: .75rem; }}
body.grammar-evidence-atelier .label-board div:nth-child(1) {{ grid-row: span 2; }}
body.grammar-evidence-atelier .label-board div,
body.grammar-evidence-atelier .proof,
body.grammar-evidence-atelier .artifact-panel {{ background: #fff9ef; border-color: #d8c8b3; border-radius: 0; box-shadow: none; }}
body.grammar-evidence-atelier .proof {{ padding: .5rem; }}
body.grammar-evidence-atelier .evidence-grid {{ grid-template-columns: minmax(13rem, 17vw) minmax(0, 1fr); gap: 2.4vw; }}
body.grammar-evidence-atelier table {{ font-size: .86rem; background: rgba(255,249,239,.55); }}
body.grammar-evidence-atelier td,
body.grammar-evidence-atelier th {{ border-top-color: #d8c8b3; }}

body.grammar-atlas-marginalia .slide {{ padding: 5.4vh 6.6vw 7.4vh; background: var(--paper); color: var(--ink); }}
body.grammar-atlas-marginalia .slide {{ --cover-art-height: 35vh; --proof-visual-height: 56vh; --artifact-visual-height: 45vh; }}
body.grammar-atlas-marginalia .dark {{ background: #fffdfa; color: #171717; }}
body.grammar-atlas-marginalia .dark::before {{ opacity: .10; background-image: linear-gradient(rgba(6,69,173,.12) 1px, transparent 1px); background-size: 100% 7.5vh; }}
body.grammar-atlas-marginalia .dark .proof figcaption,
body.grammar-atlas-marginalia .dark .artifact-panel figcaption {{ color: #5b5b5b; }}
body.grammar-atlas-marginalia .dark .proof figcaption b,
body.grammar-atlas-marginalia .dark .artifact-panel figcaption b {{ color: #171717; }}
body.grammar-atlas-marginalia h1,
body.grammar-atlas-marginalia h2,
body.grammar-atlas-marginalia .spine b {{ font-family: Georgia, "Times New Roman", serif; font-weight: 700; color: #171717; }}
body.grammar-atlas-marginalia h1 {{ font-size: clamp(3.4rem, 6.3vw, 6.9rem); line-height: 1.02; }}
body.grammar-atlas-marginalia h2 {{ font-size: clamp(2rem, 3.35vw, 3.95rem); max-width: 74vw; line-height: 1.08; }}
body.grammar-atlas-marginalia .kicker,
body.grammar-atlas-marginalia .tags span,
body.grammar-atlas-marginalia td:first-child {{ color: #0645ad; }}
body.grammar-atlas-marginalia .rule {{ background: #d7d7d2; margin-bottom: 4.2vh; }}
body.grammar-atlas-marginalia .cover {{ grid-template-columns: 26vw 1fr; }}
body.grammar-atlas-marginalia .cover-art {{ padding: .5rem; border-color: #d7d7d2; background: #fff; box-shadow: none; }}
body.grammar-atlas-marginalia .two-col {{ grid-template-columns: minmax(27rem, 1.05fr) minmax(13rem, .95fr); gap: 4.5vw; margin-top: 4vh; }}
body.grammar-atlas-marginalia .label-board {{ grid-template-columns: 1fr; border-left: 2px solid #0645ad; padding-left: 1rem; }}
body.grammar-atlas-marginalia .label-board div,
body.grammar-atlas-marginalia .proof,
body.grammar-atlas-marginalia .artifact-panel {{ background: #fff; border-color: #d7d7d2; border-radius: 0; box-shadow: none; }}
body.grammar-atlas-marginalia .evidence-grid {{ grid-template-columns: minmax(0, 1fr) minmax(14rem, 18vw); gap: 2.8vw; }}
body.grammar-atlas-marginalia .proof {{ order: -1; padding: .8rem; }}
body.grammar-atlas-marginalia .proof-notes,
body.grammar-atlas-marginalia .artifact-notes {{ border-left: 2px solid #0645ad; padding-left: .75rem; }}
body.grammar-atlas-marginalia table {{ font-size: .84rem; }}
body.grammar-atlas-marginalia td,
body.grammar-atlas-marginalia th {{ border-top-color: #d7d7d2; padding: .68rem 0; }}

body.grammar-systems-field-manual .slide {{ padding: 4.8vh 4.8vw 7.2vh; background: linear-gradient(90deg, rgba(16,20,17,.10) 0 1px, transparent 1px 100%), var(--paper); background-size: 8.333vw 100%; color: var(--ink); }}
body.grammar-systems-field-manual .slide {{ --proof-visual-height: 53vh; --artifact-visual-height: 42vh; --cover-art-height: 17vh; }}
body.grammar-systems-field-manual .dark {{ background: #111a16; color: #f6f7f1; }}
body.grammar-systems-field-manual .dark::before {{ opacity: .15; background-size: 8.333vw 9vh; }}
body.grammar-systems-field-manual h1,
body.grammar-systems-field-manual h2,
body.grammar-systems-field-manual .metric strong {{ font-family: "Helvetica Neue", Arial, sans-serif; font-weight: 820; line-height: 1.02; color: currentColor; }}
body.grammar-systems-field-manual h1 {{ font-size: clamp(3.4rem, 7.2vw, 7.6rem); max-width: 74vw; }}
body.grammar-systems-field-manual h2 {{ font-size: clamp(2rem, 3.75vw, 4.45rem); max-width: 80vw; }}
body.grammar-systems-field-manual .kicker {{ display: inline-block; color: #d05a2a; border-bottom: 2px solid #d05a2a; letter-spacing: 0; padding-bottom: .18rem; }}
body.grammar-systems-field-manual .rule {{ height: 3px; width: 22vw; background: #101411; }}
body.grammar-systems-field-manual .dark .rule {{ background: #d05a2a; }}
body.grammar-systems-field-manual .metrics {{ border-top: 2px solid currentColor; gap: 1rem; }}
body.grammar-systems-field-manual .metric strong {{ color: #d05a2a; }}
body.grammar-systems-field-manual .two-col {{ grid-template-columns: minmax(25rem, .85fr) 1.15fr; gap: 3.2vw; margin-top: 4vh; }}
body.grammar-systems-field-manual .label-board {{ grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .55rem; }}
body.grammar-systems-field-manual .label-board div,
body.grammar-systems-field-manual .proof,
body.grammar-systems-field-manual .artifact-panel {{ background: rgba(255,255,255,.66); border: 2px solid currentColor; border-radius: 0; box-shadow: none; }}
body.grammar-systems-field-manual .dark .label-board div,
body.grammar-systems-field-manual .dark .proof,
body.grammar-systems-field-manual .dark .artifact-panel {{ background: #15211b; }}
body.grammar-systems-field-manual .evidence-grid {{ grid-template-columns: minmax(14rem, 18vw) minmax(0, 1fr); gap: 2.6vw; }}
body.grammar-systems-field-manual .matrix-grid {{ grid-template-columns: minmax(15rem, 20vw) minmax(0, 1fr); gap: 2.5vw; }}
body.grammar-systems-field-manual table {{ font-size: .82rem; border: 2px solid currentColor; background: rgba(255,255,255,.5); }}
body.grammar-systems-field-manual td,
body.grammar-systems-field-manual th {{ border-top: 2px solid currentColor; padding: .58rem .45rem; }}

body.grammar-lab-trace-ledger .slide {{ padding: 4.8vh 5vw 7.2vh; background: #111512; color: #e9efe7; }}
body.grammar-lab-trace-ledger .slide {{ --proof-visual-height: 53vh; --artifact-visual-height: 42vh; --cover-art-height: 16vh; }}
body.grammar-lab-trace-ledger .light,
body.grammar-lab-trace-ledger .dark {{ background: #111512; color: #e9efe7; }}
body.grammar-lab-trace-ledger .light::before,
body.grammar-lab-trace-ledger .dark::before {{ opacity: .14; background-image: linear-gradient(rgba(184,242,102,.13) 1px, transparent 1px), linear-gradient(90deg, rgba(184,242,102,.10) 1px, transparent 1px); background-size: 8.333vw 9vh; }}
body.grammar-lab-trace-ledger h1,
body.grammar-lab-trace-ledger h2,
body.grammar-lab-trace-ledger .metric strong {{ font-family: "Helvetica Neue", Arial, sans-serif; font-weight: 800; line-height: 1.02; color: #e9efe7; }}
body.grammar-lab-trace-ledger h1 {{ font-size: clamp(3.4rem, 7.5vw, 8.2rem); max-width: 74vw; }}
body.grammar-lab-trace-ledger h2 {{ font-size: clamp(2rem, 3.9vw, 4.8rem); max-width: 78vw; }}
body.grammar-lab-trace-ledger .kicker,
body.grammar-lab-trace-ledger .metric strong,
body.grammar-lab-trace-ledger td:first-child,
body.grammar-lab-trace-ledger .label-board span {{ color: #b8f266; }}
body.grammar-lab-trace-ledger .rule {{ width: 20vw; height: 2px; background: #b8f266; }}
body.grammar-lab-trace-ledger .subtitle,
body.grammar-lab-trace-ledger .lead,
body.grammar-lab-trace-ledger p {{ color: #c9d4ca; }}
body.grammar-lab-trace-ledger .metrics {{ border-top-color: #2a352e; }}
body.grammar-lab-trace-ledger .two-col {{ grid-template-columns: minmax(24rem, .8fr) 1.2fr; gap: 3vw; margin-top: 4vh; }}
body.grammar-lab-trace-ledger .label-board {{ grid-template-columns: 1fr; gap: .45rem; }}
body.grammar-lab-trace-ledger .label-board div,
body.grammar-lab-trace-ledger .proof,
body.grammar-lab-trace-ledger .artifact-panel {{ background: #151d17; border-color: #2a352e; border-radius: 0; box-shadow: none; }}
body.grammar-lab-trace-ledger .proof figcaption b,
body.grammar-lab-trace-ledger .artifact-panel figcaption b {{ color: #e9efe7; }}
body.grammar-lab-trace-ledger .proof figcaption,
body.grammar-lab-trace-ledger .artifact-panel figcaption {{ color: #9aa79c; }}
body.grammar-lab-trace-ledger .evidence-grid {{ grid-template-columns: minmax(13rem, 17vw) minmax(0, 1fr); gap: 2.4vw; }}
body.grammar-lab-trace-ledger .matrix-grid {{ grid-template-columns: minmax(14rem, 18vw) minmax(0, 1fr); gap: 2.4vw; }}
body.grammar-lab-trace-ledger table {{ font-size: .82rem; background: #151d17; }}
body.grammar-lab-trace-ledger td,
body.grammar-lab-trace-ledger th {{ border-top-color: #2a352e; color: #e9efe7; padding: .6rem .25rem; }}
body.grammar-lab-trace-ledger footer {{ color: rgba(233,239,231,.45); }}

body.grammar-object-study-wall .slide {{ padding: 5.4vh 5.8vw 7.4vh; background: var(--paper); color: var(--ink); }}
body.grammar-object-study-wall .slide {{ --cover-art-height: 40vh; --proof-visual-height: 58vh; --artifact-visual-height: 50vh; }}
body.grammar-object-study-wall .dark {{ background: #1f2528; color: #f6efe5; }}
body.grammar-object-study-wall .dark::before {{ opacity: .10; background-size: 9vw 10vh; }}
body.grammar-object-study-wall h1,
body.grammar-object-study-wall h2,
body.grammar-object-study-wall .metric strong {{ font-family: "Avenir Next", "Helvetica Neue", Arial, sans-serif; font-weight: 760; line-height: 1.04; color: currentColor; }}
body.grammar-object-study-wall h1 {{ font-size: clamp(3.3rem, 6.8vw, 7.4rem); max-width: 68vw; }}
body.grammar-object-study-wall h2 {{ font-size: clamp(2rem, 3.75vw, 4.4rem); max-width: 78vw; }}
body.grammar-object-study-wall .kicker {{ color: #2c63c7; letter-spacing: 0; }}
body.grammar-object-study-wall .rule {{ width: 12vw; height: 3px; background: #2c63c7; }}
body.grammar-object-study-wall .cover {{ grid-template-columns: 33vw 1fr; }}
body.grammar-object-study-wall .cover-art {{ padding: .7rem; border-color: #d7c7b5; background: #fffaf2; box-shadow: 0 22px 58px rgba(44,36,28,.14); }}
body.grammar-object-study-wall .cover .metrics {{ max-width: 54vw; }}
body.grammar-object-study-wall .metric {{ row-gap: .7rem; }}
body.grammar-object-study-wall .metric strong {{ line-height: 1.16; }}
body.grammar-object-study-wall .metric span {{ line-height: 1.34; }}
body.grammar-object-study-wall .two-col {{ grid-template-columns: minmax(23rem, .7fr) 1.3fr; gap: 3.2vw; margin-top: 4vh; }}
body.grammar-object-study-wall .label-board {{ grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .85rem; }}
body.grammar-object-study-wall .label-board div:nth-child(1) {{ grid-column: span 2; min-height: 7rem; }}
body.grammar-object-study-wall .label-board div,
body.grammar-object-study-wall .proof,
body.grammar-object-study-wall .artifact-panel {{ background: #fffaf2; border-color: #d7c7b5; border-radius: 0; box-shadow: 0 14px 36px rgba(44,36,28,.08); }}
body.grammar-object-study-wall .dark .proof figcaption,
body.grammar-object-study-wall .dark .artifact-panel figcaption {{ color: #6b625a; }}
body.grammar-object-study-wall .dark .proof figcaption b,
body.grammar-object-study-wall .dark .artifact-panel figcaption b {{ color: #171717; }}
body.grammar-object-study-wall .evidence-grid {{ grid-template-columns: minmax(12rem, 16vw) minmax(0, 1fr); gap: 2.2vw; }}
body.grammar-object-study-wall .proof {{ padding: .55rem; }}
body.grammar-object-study-wall .matrix-grid {{ grid-template-columns: minmax(17rem, 22vw) minmax(0, 1fr); }}
body.grammar-object-study-wall table {{ font-size: .86rem; background: rgba(255,250,242,.55); }}
body.grammar-object-study-wall td,
body.grammar-object-study-wall th {{ border-top-color: #d7c7b5; }}

body.grammar-vellum-research-note .light,
body.grammar-vellum-research-note .dark {{ background: #10182a; color: #f3ead7; }}
body.grammar-vellum-research-note .light::before,
body.grammar-vellum-research-note .dark::before {{ opacity: .13; background-image: linear-gradient(rgba(215,173,98,.12) 1px, transparent 1px); background-size: 100% 8.6vh; }}
body.grammar-vellum-research-note h1,
body.grammar-vellum-research-note h2,
body.grammar-vellum-research-note .spine b {{ font-family: "Cormorant Garamond", Georgia, serif; font-weight: 650; line-height: 1.02; color: #f3ead7; }}
body.grammar-vellum-research-note h1 {{ max-width: 70vw; font-size: clamp(3.3rem, 7.2vw, 7.7rem); }}
body.grammar-vellum-research-note h2 {{ max-width: 76vw; font-size: clamp(2rem, 3.7vw, 4.4rem); }}
body.grammar-vellum-research-note .kicker,
body.grammar-vellum-research-note .tags span,
body.grammar-vellum-research-note .metric strong,
body.grammar-vellum-research-note td:first-child {{ color: #d7ad62; }}
body.grammar-vellum-research-note .rule {{ width: 14vw; height: 1px; background: #d7ad62; margin-bottom: 4.8vh; }}
body.grammar-vellum-research-note .subtitle,
body.grammar-vellum-research-note .lead,
body.grammar-vellum-research-note p {{ color: #c2b7a2; }}
body.grammar-vellum-research-note .metrics {{ border-top-color: #314057; max-width: 72vw; }}
body.grammar-vellum-research-note .two-col {{ grid-template-columns: minmax(25rem, .84fr) 1.16fr; gap: 3.6vw; margin-top: 4vh; }}
body.grammar-vellum-research-note .label-board div,
body.grammar-vellum-research-note .proof,
body.grammar-vellum-research-note .artifact-panel {{ background: #141e33; border-color: #314057; border-radius: 0; box-shadow: none; }}
body.grammar-vellum-research-note .proof figcaption b,
body.grammar-vellum-research-note .artifact-panel figcaption b {{ color: #f3ead7; }}
body.grammar-vellum-research-note .proof figcaption,
body.grammar-vellum-research-note .artifact-panel figcaption {{ color: #aeb6ad; }}
body.grammar-vellum-research-note .evidence-grid {{ grid-template-columns: minmax(15rem, 20vw) minmax(0, 1fr); gap: 3vw; }}
body.grammar-vellum-research-note .matrix-grid {{ grid-template-columns: minmax(14rem, 19vw) minmax(0, 1fr); gap: 2.8vw; }}
body.grammar-vellum-research-note table {{ font-size: .84rem; background: #141e33; }}
body.grammar-vellum-research-note td,
body.grammar-vellum-research-note th {{ border-top-color: #314057; color: #f3ead7; }}

body.grammar-cobalt-research-grid .slide {{ padding: 4.8vh 5vw 7.2vh; background: linear-gradient(rgba(0,71,255,.075) 1px, transparent 1px), linear-gradient(90deg, rgba(0,71,255,.06) 1px, transparent 1px), var(--paper); background-size: 8.333vw 9vh; }}
body.grammar-cobalt-research-grid .dark {{ background: linear-gradient(rgba(255,255,255,.08) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.065) 1px, transparent 1px), #111827; background-size: 8.333vw 9vh; color: #f4f7ff; }}
body.grammar-cobalt-research-grid h1,
body.grammar-cobalt-research-grid h2,
body.grammar-cobalt-research-grid .metric strong {{ font-family: "Helvetica Neue", Arial, sans-serif; font-weight: 820; line-height: 1.01; color: currentColor; }}
body.grammar-cobalt-research-grid h1 {{ max-width: 76vw; font-size: clamp(3.4rem, 7.4vw, 8rem); }}
body.grammar-cobalt-research-grid h2 {{ max-width: 80vw; font-size: clamp(2.05rem, 3.8vw, 4.65rem); }}
body.grammar-cobalt-research-grid .kicker {{ display: inline-block; color: #0047ff; border-bottom: 2px solid #0047ff; padding-bottom: .18rem; letter-spacing: 0; }}
body.grammar-cobalt-research-grid .rule {{ width: 18vw; height: 3px; background: #0047ff; }}
body.grammar-cobalt-research-grid .metric strong,
body.grammar-cobalt-research-grid td:first-child,
body.grammar-cobalt-research-grid .label-board span {{ color: #0047ff; }}
body.grammar-cobalt-research-grid .metrics {{ border-top: 2px solid currentColor; gap: 1rem; }}
body.grammar-cobalt-research-grid .label-board div,
body.grammar-cobalt-research-grid .proof,
body.grammar-cobalt-research-grid .artifact-panel {{ background: rgba(255,255,255,.72); border: 2px solid currentColor; border-radius: 0; box-shadow: none; }}
body.grammar-cobalt-research-grid .dark .label-board div,
body.grammar-cobalt-research-grid .dark .proof,
body.grammar-cobalt-research-grid .dark .artifact-panel {{ background: #141b2a; }}
body.grammar-cobalt-research-grid .two-col {{ grid-template-columns: minmax(24rem, .82fr) 1.18fr; gap: 3vw; margin-top: 3.6vh; }}
body.grammar-cobalt-research-grid .evidence-grid {{ grid-template-columns: minmax(13rem, 17vw) minmax(0, 1fr); gap: 2.2vw; }}
body.grammar-cobalt-research-grid .matrix-grid {{ grid-template-columns: minmax(14rem, 18vw) minmax(0, 1fr); gap: 2.4vw; }}
body.grammar-cobalt-research-grid table {{ font-size: .82rem; border: 2px solid currentColor; background: rgba(255,255,255,.55); }}
body.grammar-cobalt-research-grid td,
body.grammar-cobalt-research-grid th {{ border-top: 2px solid currentColor; padding: .58rem .45rem; }}

body.grammar-mono-ink-ledger .slide {{ padding: 5.4vh 6.6vw 7.4vh; background: var(--paper); color: var(--ink); --cover-art-height: 34vh; }}
body.grammar-mono-ink-ledger .dark {{ background: var(--paper); color: var(--ink); }}
body.grammar-mono-ink-ledger .dark::before {{ opacity: .18; background-image: linear-gradient(rgba(13,13,13,.045) 1px, transparent 1px); background-size: 100% 7.5vh; }}
body.grammar-mono-ink-ledger h1,
body.grammar-mono-ink-ledger h2,
body.grammar-mono-ink-ledger .spine b {{ font-family: "Iowan Old Style", Georgia, serif; font-weight: 700; color: #0d0d0d; }}
body.grammar-mono-ink-ledger h1 {{ max-width: 70vw; font-size: clamp(3.2rem, 6.4vw, 7rem); line-height: 1.01; }}
body.grammar-mono-ink-ledger h2 {{ max-width: 78vw; font-size: clamp(2rem, 3.35vw, 4.05rem); line-height: 1.06; }}
body.grammar-mono-ink-ledger h2 {{ margin-bottom: .42em; }}
body.grammar-mono-ink-ledger .kicker,
body.grammar-mono-ink-ledger .tags span,
body.grammar-mono-ink-ledger .metric strong,
body.grammar-mono-ink-ledger td:first-child,
body.grammar-mono-ink-ledger .label-board span {{ color: #0d0d0d; }}
body.grammar-mono-ink-ledger .rule {{ background: #0d0d0d; margin-bottom: 4.6vh; }}
body.grammar-mono-ink-ledger .metrics {{ border-top-color: #0d0d0d; max-width: none; }}
body.grammar-mono-ink-ledger .two-col {{ grid-template-columns: minmax(28rem, 1fr) minmax(13rem, .92fr); gap: 4vw; margin-top: 3.7vh; }}
body.grammar-mono-ink-ledger .label-board {{ grid-template-columns: 1fr; border-left: 2px solid #0d0d0d; padding-left: 1rem; }}
body.grammar-mono-ink-ledger .label-board div,
body.grammar-mono-ink-ledger .proof,
body.grammar-mono-ink-ledger .artifact-panel {{ background: #fffef8; border-color: #0d0d0d; border-radius: 0; box-shadow: none; }}
body.grammar-mono-ink-ledger .evidence-grid {{ grid-template-columns: minmax(0, 1fr) minmax(13rem, 17vw); gap: 2.6vw; }}
body.grammar-mono-ink-ledger .proof {{ order: -1; padding: .7rem; }}
body.grammar-mono-ink-ledger .matrix-grid {{ grid-template-columns: minmax(14rem, 19vw) minmax(0, 1fr); }}
body.grammar-mono-ink-ledger table {{ font-size: .84rem; background: #fffef8; }}
body.grammar-mono-ink-ledger td,
body.grammar-mono-ink-ledger th {{ border-top-color: #0d0d0d; padding: .62rem 0; }}

body.grammar-forest-editorial-brief .slide {{ padding: 5.3vh 5.8vw 7.3vh; background: var(--paper); color: var(--ink); }}
body.grammar-forest-editorial-brief .slide {{ --cover-art-height: 34vh; }}
body.grammar-forest-editorial-brief .dark {{ background: #133024; color: #f7f1e7; }}
body.grammar-forest-editorial-brief .dark::before {{ opacity: .11; background-size: 8vw 9vh; }}
body.grammar-forest-editorial-brief h1,
body.grammar-forest-editorial-brief h2,
body.grammar-forest-editorial-brief .spine b {{ font-family: "Source Serif 4", Georgia, serif; font-weight: 720; color: currentColor; }}
body.grammar-forest-editorial-brief h1 {{ max-width: 68vw; font-size: clamp(3.2rem, 6.4vw, 7rem); line-height: 1.03; }}
body.grammar-forest-editorial-brief h2 {{ max-width: 76vw; font-size: clamp(2rem, 3.45vw, 4.2rem); line-height: 1.06; }}
body.grammar-forest-editorial-brief .kicker,
body.grammar-forest-editorial-brief .metric strong,
body.grammar-forest-editorial-brief td:first-child,
body.grammar-forest-editorial-brief .label-board span {{ color: #bd6f78; }}
body.grammar-forest-editorial-brief .rule {{ width: 13vw; height: 2px; background: #bd6f78; margin-bottom: 4.8vh; }}
body.grammar-forest-editorial-brief .cover {{ grid-template-columns: 31vw 1fr; }}
body.grammar-forest-editorial-brief .cover-art {{ background: #fffaf1; border-color: #d8cebf; box-shadow: 0 18px 44px rgba(20,51,34,.12); }}
body.grammar-forest-editorial-brief .metrics {{ border-top-color: #d8cebf; max-width: 70vw; }}
body.grammar-forest-editorial-brief .two-col {{ grid-template-columns: minmax(23rem, .72fr) 1.28fr; gap: 3.7vw; margin-top: 4vh; }}
body.grammar-forest-editorial-brief .label-board {{ grid-template-columns: 1.18fr .82fr; gap: .8rem; }}
body.grammar-forest-editorial-brief .label-board div:nth-child(1) {{ grid-row: span 2; }}
body.grammar-forest-editorial-brief .label-board div,
body.grammar-forest-editorial-brief .proof,
body.grammar-forest-editorial-brief .artifact-panel {{ background: #fffaf1; border-color: #d8cebf; border-radius: 0; box-shadow: none; }}
body.grammar-forest-editorial-brief .evidence-grid {{ grid-template-columns: minmax(12rem, 16vw) minmax(0, 1fr); gap: 2.2vw; }}
body.grammar-forest-editorial-brief .matrix-grid {{ grid-template-columns: minmax(17rem, 22vw) minmax(0, 1fr); }}
body.grammar-forest-editorial-brief table {{ font-size: .86rem; background: rgba(255,250,241,.58); }}
body.grammar-forest-editorial-brief td,
body.grammar-forest-editorial-brief th {{ border-top-color: #d8cebf; }}

body.grammar-neo-grid-lab .slide {{ padding: 4.6vh 4.8vw 7vh; background: linear-gradient(90deg, rgba(8,8,8,.13) 0 2px, transparent 2px 100%), var(--paper); background-size: 8.333vw 100%; color: var(--ink); }}
body.grammar-neo-grid-lab .dark {{ background: linear-gradient(90deg, rgba(215,255,47,.12) 0 2px, transparent 2px 100%), #080808; color: #fbf7e6; }}
body.grammar-neo-grid-lab .dark::before {{ display: none; }}
body.grammar-neo-grid-lab h1,
body.grammar-neo-grid-lab h2,
body.grammar-neo-grid-lab .metric strong {{ font-family: "Helvetica Neue", Arial, sans-serif; font-weight: 860; line-height: 1.04; color: currentColor; }}
body.grammar-neo-grid-lab h1 {{ max-width: 76vw; font-size: clamp(3.3rem, 7.8vw, 8.6rem); }}
body.grammar-neo-grid-lab h2 {{ max-width: 82vw; font-size: clamp(2rem, 4.05vw, 4.9rem); }}
body.grammar-neo-grid-lab .kicker {{ display: inline-block; background: #d7ff2f; color: #080808; padding: .18rem .5rem; letter-spacing: 0; }}
body.grammar-neo-grid-lab .rule {{ height: 4px; width: 20vw; background: #d7ff2f; }}
body.grammar-neo-grid-lab .metrics {{ border: 3px solid currentColor; padding: 0; gap: 0; max-width: 70vw; }}
body.grammar-neo-grid-lab .metric {{ padding: .85rem; border-right: 3px solid currentColor; }}
body.grammar-neo-grid-lab .metric:last-child {{ border-right: 0; }}
body.grammar-neo-grid-lab .metric strong,
body.grammar-neo-grid-lab td:first-child,
body.grammar-neo-grid-lab .label-board span {{ color: #d7ff2f; }}
body.grammar-neo-grid-lab .light .metric strong,
body.grammar-neo-grid-lab .light td:first-child,
body.grammar-neo-grid-lab .light .label-board span {{ color: #080808; }}
body.grammar-neo-grid-lab .two-col {{ grid-template-columns: minmax(24rem, .82fr) 1.18fr; gap: 2.6vw; margin-top: 3.6vh; }}
body.grammar-neo-grid-lab .label-board div,
body.grammar-neo-grid-lab .proof,
body.grammar-neo-grid-lab .artifact-panel {{ background: #fbf7e6; border: 3px solid currentColor; border-radius: 0; box-shadow: none; }}
body.grammar-neo-grid-lab .dark .label-board div,
body.grammar-neo-grid-lab .dark .proof,
body.grammar-neo-grid-lab .dark .artifact-panel {{ background: #111; }}
body.grammar-neo-grid-lab .evidence-grid {{ grid-template-columns: minmax(13rem, 17vw) minmax(0, 1fr); gap: 2.2vw; }}
body.grammar-neo-grid-lab .matrix-grid {{ grid-template-columns: minmax(13rem, 17vw) minmax(0, 1fr); gap: 2.2vw; }}
body.grammar-neo-grid-lab table {{ font-size: .8rem; border: 3px solid currentColor; background: #fbf7e6; }}
body.grammar-neo-grid-lab .dark table {{ background: #111; }}
body.grammar-neo-grid-lab td,
body.grammar-neo-grid-lab th {{ border-top: 3px solid currentColor; padding: .54rem .35rem; }}

body.grammar-prism-clean-room .slide {{ padding: 4.8vh 5.2vw 7vh; background: var(--paper); color: var(--ink); }}
body.grammar-prism-clean-room .slide {{ --cover-art-height: 40vh; --proof-visual-height: 55vh; --artifact-visual-height: 43vh; }}
body.grammar-prism-clean-room .dark {{ background: #f6f8fb; color: var(--ink); }}
body.grammar-prism-clean-room .dark::before {{ opacity: .06; background-size: 7vw 9vh; }}
body.grammar-prism-clean-room h1,
body.grammar-prism-clean-room h2,
body.grammar-prism-clean-room .metric strong,
body.grammar-prism-clean-room .spine b {{ font-family: "Georgia CDN", Georgia, serif; font-weight: 720; color: #172033; }}
body.grammar-prism-clean-room h1 {{ max-width: 66vw; font-size: clamp(3rem, 5.9vw, 6.4rem); line-height: 1.03; }}
body.grammar-prism-clean-room h2 {{ max-width: 78vw; font-size: clamp(1.95rem, 3.25vw, 3.95rem); line-height: 1.07; }}
body.grammar-prism-clean-room .kicker {{ color: #b38b4d; letter-spacing: .03em; }}
body.grammar-prism-clean-room .rule {{ height: 1px; background: #e4e8ef; margin-bottom: 4.6vh; }}
body.grammar-prism-clean-room .cover {{ grid-template-columns: 30vw 1fr; column-gap: 5vw; }}
body.grammar-prism-clean-room .cover-art {{ padding: .75rem; background: #fff; border-color: #e4e8ef; border-radius: 0; box-shadow: none; }}
body.grammar-prism-clean-room .cover .metrics {{ max-width: 58vw; border-top-color: #e4e8ef; }}
body.grammar-prism-clean-room .two-col {{ grid-template-columns: minmax(28rem, .88fr) 1.12fr; gap: 4vw; margin-top: 3.8vh; }}
body.grammar-prism-clean-room .label-board {{ grid-template-columns: 1fr; gap: .58rem; }}
body.grammar-prism-clean-room .label-board div,
body.grammar-prism-clean-room .proof,
body.grammar-prism-clean-room .artifact-panel {{ background: #fff; border-color: #e4e8ef; border-radius: 0; box-shadow: none; }}
body.grammar-prism-clean-room .dark .proof figcaption,
body.grammar-prism-clean-room .dark .artifact-panel figcaption {{ color: #596579; }}
body.grammar-prism-clean-room .dark .proof figcaption b,
body.grammar-prism-clean-room .dark .artifact-panel figcaption b {{ color: #172033; }}
body.grammar-prism-clean-room .evidence-grid {{ grid-template-columns: minmax(15rem, 20vw) minmax(0, 1fr); gap: 3vw; }}
body.grammar-prism-clean-room .matrix-grid {{ grid-template-columns: minmax(18rem, 23vw) minmax(0, 1fr); gap: 3vw; }}
body.grammar-prism-clean-room table {{ font-size: .86rem; background: #fff; }}
body.grammar-prism-clean-room td,
body.grammar-prism-clean-room th {{ border-top-color: #e4e8ef; padding: .66rem 0; }}

body.grammar-prism-publication-stack .slide {{ padding: 4.6vh 5vw 7vh; background: #fefffe; color: #0f172a; }}
body.grammar-prism-publication-stack .slide {{ --cover-art-height: 42vh; --proof-visual-height: 56vh; --artifact-visual-height: 44vh; }}
body.grammar-prism-publication-stack .dark {{ background: #f8fafc; color: #0f172a; }}
body.grammar-prism-publication-stack .dark::before {{ opacity: .05; background-size: 6.66vw 8vh; }}
body.grammar-prism-publication-stack h1,
body.grammar-prism-publication-stack h2,
body.grammar-prism-publication-stack .metric strong,
body.grammar-prism-publication-stack .spine b {{ font-family: "Georgia CDN", Georgia, serif; font-weight: 720; color: #0f172a; }}
body.grammar-prism-publication-stack h1 {{ max-width: 62vw; font-size: clamp(3rem, 5.7vw, 6.15rem); line-height: 1.03; }}
body.grammar-prism-publication-stack h2 {{ max-width: 78vw; font-size: clamp(1.9rem, 3.12vw, 3.78rem); line-height: 1.08; }}
body.grammar-prism-publication-stack .kicker,
body.grammar-prism-publication-stack .metric strong,
body.grammar-prism-publication-stack td:first-child,
body.grammar-prism-publication-stack .label-board span {{ color: #b88945; }}
body.grammar-prism-publication-stack .rule {{ background: #e2e8f0; margin-bottom: 4.2vh; }}
body.grammar-prism-publication-stack .cover {{ grid-template-columns: 29vw 1fr; column-gap: 5vw; }}
body.grammar-prism-publication-stack .cover-art {{ padding: .65rem; background: #fff; border-color: #e2e8f0; border-radius: 0; box-shadow: none; }}
body.grammar-prism-publication-stack .cover .metrics {{ max-width: 60vw; border-top-color: #e2e8f0; gap: 1rem; }}
body.grammar-prism-publication-stack .two-col {{ grid-template-columns: minmax(27rem, .88fr) 1.12fr; gap: 3.6vw; margin-top: 3.5vh; }}
body.grammar-prism-publication-stack .label-board {{ grid-template-columns: 1fr; gap: .42rem; }}
body.grammar-prism-publication-stack .label-board div {{ min-height: 4.1rem; padding: .68rem .85rem; background: #fff; border-color: #e2e8f0; border-radius: 0; box-shadow: none; }}
body.grammar-prism-publication-stack .label-board b {{ font-size: 1rem; line-height: 1.18; }}
body.grammar-prism-publication-stack .proof,
body.grammar-prism-publication-stack .artifact-panel {{ background: #fff; border-color: #e2e8f0; border-radius: 0; box-shadow: none; }}
body.grammar-prism-publication-stack .dark .proof figcaption,
body.grammar-prism-publication-stack .dark .artifact-panel figcaption {{ color: #64748b; }}
body.grammar-prism-publication-stack .dark .proof figcaption b,
body.grammar-prism-publication-stack .dark .artifact-panel figcaption b {{ color: #0f172a; }}
body.grammar-prism-publication-stack .evidence-grid {{ grid-template-columns: minmax(15rem, 19vw) minmax(0, 1fr); gap: 2.8vw; }}
body.grammar-prism-publication-stack .matrix-grid {{ grid-template-columns: minmax(18rem, 23vw) minmax(0, 1fr); gap: 2.8vw; }}
body.grammar-prism-publication-stack table {{ font-size: .84rem; background: #fff; }}
body.grammar-prism-publication-stack td,
body.grammar-prism-publication-stack th {{ border-top-color: #e2e8f0; padding: .58rem 0; }}

body.grammar-ia-research-archive .slide {{ padding: 5.2vh 6.8vw 7.4vh; background: var(--paper); color: var(--ink); }}
body.grammar-ia-research-archive .slide {{ --cover-art-height: 34vh; --proof-visual-height: 56vh; --artifact-visual-height: 46vh; }}
body.grammar-ia-research-archive .dark {{ background: var(--paper); color: var(--ink); }}
body.grammar-ia-research-archive .dark::before {{ opacity: .08; background-image: linear-gradient(rgba(11,85,199,.09) 1px, transparent 1px); background-size: 100% 7.2vh; }}
body.grammar-ia-research-archive h1,
body.grammar-ia-research-archive h2,
body.grammar-ia-research-archive .spine b {{ font-family: Georgia, "Times New Roman", serif; font-weight: 700; color: #111; }}
body.grammar-ia-research-archive h1 {{ max-width: 72vw; font-size: clamp(3rem, 6.1vw, 6.8rem); line-height: 1.03; }}
body.grammar-ia-research-archive h2 {{ max-width: 76vw; font-size: clamp(1.95rem, 3.25vw, 3.9rem); line-height: 1.08; }}
body.grammar-ia-research-archive .kicker,
body.grammar-ia-research-archive .tags span,
body.grammar-ia-research-archive .metric strong,
body.grammar-ia-research-archive td:first-child,
body.grammar-ia-research-archive .label-board span {{ color: #0b55c7; }}
body.grammar-ia-research-archive .rule {{ background: #d6d6d6; margin-bottom: 4.2vh; }}
body.grammar-ia-research-archive .cover {{ grid-template-columns: 25vw 1fr; }}
body.grammar-ia-research-archive .cover-art {{ padding: .45rem; border-color: #d6d6d6; background: #fff; box-shadow: none; }}
body.grammar-ia-research-archive .two-col {{ grid-template-columns: minmax(29rem, 1.08fr) minmax(14rem, .92fr); gap: 4vw; margin-top: 3.6vh; }}
body.grammar-ia-research-archive .label-board {{ grid-template-columns: 1fr; border-left: 2px solid #0b55c7; padding-left: 1rem; }}
body.grammar-ia-research-archive .label-board div,
body.grammar-ia-research-archive .proof,
body.grammar-ia-research-archive .artifact-panel {{ background: #fff; border-color: #d6d6d6; border-radius: 0; box-shadow: none; }}
body.grammar-ia-research-archive .evidence-grid {{ grid-template-columns: minmax(0, 1fr) minmax(13rem, 17vw); gap: 2.7vw; }}
body.grammar-ia-research-archive .proof {{ order: -1; padding: .62rem; }}
body.grammar-ia-research-archive .matrix-grid {{ grid-template-columns: minmax(14rem, 19vw) minmax(0, 1fr); gap: 2.8vw; }}
body.grammar-ia-research-archive table {{ font-size: .84rem; background: #fff; }}
body.grammar-ia-research-archive td,
body.grammar-ia-research-archive th {{ border-top-color: #d6d6d6; padding: .62rem 0; }}

body.grammar-pentagram-gridnote .slide {{ padding: 4.6vh 4.7vw 7vh; background: linear-gradient(90deg, rgba(17,17,17,.16) 0 2px, transparent 2px 100%), var(--paper); background-size: 8.333vw 100%; color: var(--ink); }}
body.grammar-pentagram-gridnote .slide {{ --cover-art-height: 20vh; --proof-visual-height: 54vh; --artifact-visual-height: 43vh; }}
body.grammar-pentagram-gridnote .dark {{ background: #111; color: #f7f5ee; }}
body.grammar-pentagram-gridnote .dark::before {{ display: none; }}
body.grammar-pentagram-gridnote h1,
body.grammar-pentagram-gridnote h2,
body.grammar-pentagram-gridnote .metric strong {{ font-family: "Helvetica Neue", Arial, sans-serif; font-weight: 860; line-height: 1.0; color: currentColor; }}
body.grammar-pentagram-gridnote h1 {{ max-width: 78vw; font-size: clamp(3.4rem, 8.2vw, 9rem); }}
body.grammar-pentagram-gridnote h2 {{ max-width: 82vw; font-size: clamp(2rem, 4.2vw, 5.2rem); }}
body.grammar-pentagram-gridnote .kicker {{ display: inline-block; background: #e22b1a; color: #fff; padding: .18rem .48rem; letter-spacing: 0; }}
body.grammar-pentagram-gridnote .rule {{ width: 24vw; height: 4px; background: #e22b1a; margin-bottom: 3.8vh; }}
body.grammar-pentagram-gridnote .metrics {{ border: 3px solid currentColor; padding: 0; gap: 0; max-width: 74vw; }}
body.grammar-pentagram-gridnote .metric {{ padding: .9rem; border-right: 3px solid currentColor; }}
body.grammar-pentagram-gridnote .metric:last-child {{ border-right: 0; }}
body.grammar-pentagram-gridnote .metric strong,
body.grammar-pentagram-gridnote td:first-child,
body.grammar-pentagram-gridnote .label-board span {{ color: #e22b1a; }}
body.grammar-pentagram-gridnote .two-col {{ grid-template-columns: minmax(24rem, .82fr) 1.18fr; gap: 2.8vw; margin-top: 3.6vh; }}
body.grammar-pentagram-gridnote .label-board div,
body.grammar-pentagram-gridnote .proof,
body.grammar-pentagram-gridnote .artifact-panel {{ background: #fffdf5; border: 3px solid currentColor; border-radius: 0; box-shadow: none; }}
body.grammar-pentagram-gridnote .evidence-grid {{ grid-template-columns: minmax(13rem, 17vw) minmax(0, 1fr); gap: 2.2vw; }}
body.grammar-pentagram-gridnote .matrix-grid {{ grid-template-columns: minmax(13rem, 17vw) minmax(0, 1fr); gap: 2.2vw; }}
body.grammar-pentagram-gridnote table {{ font-size: .8rem; border: 3px solid currentColor; background: #fffdf5; }}
body.grammar-pentagram-gridnote td,
body.grammar-pentagram-gridnote th {{ border-top: 3px solid currentColor; padding: .52rem .35rem; }}

body.grammar-takram-research-system .slide {{ padding: 5vh 5.6vw 7.2vh; background: var(--paper); color: var(--ink); }}
body.grammar-takram-research-system .slide {{ --cover-art-height: 36vh; --proof-visual-height: 55vh; --artifact-visual-height: 44vh; }}
body.grammar-takram-research-system .dark {{ background: #eef2ee; color: var(--ink); }}
body.grammar-takram-research-system .dark::before {{ opacity: .10; background-size: 6.25vw 8vh; }}
body.grammar-takram-research-system h1,
body.grammar-takram-research-system h2,
body.grammar-takram-research-system .metric strong {{ font-family: "Helvetica Neue", Arial, sans-serif; font-weight: 640; line-height: 1.06; color: #18201d; }}
body.grammar-takram-research-system h1 {{ max-width: 70vw; font-size: clamp(3rem, 6.2vw, 6.8rem); }}
body.grammar-takram-research-system h2 {{ max-width: 78vw; font-size: clamp(1.95rem, 3.25vw, 3.95rem); }}
body.grammar-takram-research-system .kicker,
body.grammar-takram-research-system .metric strong,
body.grammar-takram-research-system td:first-child,
body.grammar-takram-research-system .label-board span {{ color: #2f786b; }}
body.grammar-takram-research-system .rule {{ height: 1px; width: 15vw; background: #2f786b; margin-bottom: 4.8vh; }}
body.grammar-takram-research-system .cover {{ grid-template-columns: 28vw 1fr; }}
body.grammar-takram-research-system .cover-art {{ padding: .6rem; border-color: #d9ddd5; background: #fff; box-shadow: none; }}
body.grammar-takram-research-system .metrics {{ border-top-color: #d9ddd5; gap: 1rem; }}
body.grammar-takram-research-system .two-col {{ grid-template-columns: minmax(27rem, .92fr) 1.08fr; gap: 4vw; margin-top: 3.8vh; }}
body.grammar-takram-research-system .label-board div,
body.grammar-takram-research-system .proof,
body.grammar-takram-research-system .artifact-panel {{ background: #fff; border-color: #d9ddd5; border-radius: 0; box-shadow: none; }}
body.grammar-takram-research-system .evidence-grid {{ grid-template-columns: minmax(0, 1fr) minmax(14rem, 18vw); gap: 2.8vw; }}
body.grammar-takram-research-system .proof {{ order: -1; padding: .7rem; }}
body.grammar-takram-research-system .matrix-grid {{ grid-template-columns: minmax(14rem, 19vw) minmax(0, 1fr); gap: 2.8vw; }}
body.grammar-takram-research-system table {{ font-size: .84rem; background: #fff; }}
body.grammar-takram-research-system td,
body.grammar-takram-research-system th {{ border-top-color: #d9ddd5; padding: .64rem 0; }}

body.grammar-stamen-data-map .slide {{ padding: 5.1vh 5.8vw 7.4vh; background: radial-gradient(circle at 16% 20%, rgba(195,107,47,.08), transparent 28%), linear-gradient(90deg, rgba(35,54,47,.08) 0 1px, transparent 1px 100%), var(--paper); background-size: auto, 12.5vw 100%, auto; color: var(--ink); }}
body.grammar-stamen-data-map .slide {{ --cover-art-height: 26vh; --proof-visual-height: 55vh; --artifact-visual-height: 48vh; }}
body.grammar-stamen-data-map .dark {{ background: #23362f; color: #f7f0df; }}
body.grammar-stamen-data-map .dark::before {{ opacity: .10; background-size: 12.5vw 9vh; }}
body.grammar-stamen-data-map h1,
body.grammar-stamen-data-map h2,
body.grammar-stamen-data-map .metric strong {{ font-family: "Avenir Next", "Helvetica Neue", Arial, sans-serif; font-weight: 760; line-height: 1.04; color: currentColor; }}
body.grammar-stamen-data-map h1 {{ max-width: 70vw; font-size: clamp(3.2rem, 7vw, 7.6rem); }}
body.grammar-stamen-data-map h2 {{ max-width: 78vw; font-size: clamp(2rem, 3.8vw, 4.55rem); }}
body.grammar-stamen-data-map .kicker,
body.grammar-stamen-data-map .metric strong,
body.grammar-stamen-data-map td:first-child,
body.grammar-stamen-data-map .label-board span {{ color: #c36b2f; }}
body.grammar-stamen-data-map .rule {{ height: 2px; width: 17vw; background: #c36b2f; margin-bottom: 4.4vh; }}
body.grammar-stamen-data-map .cover-art {{ width: min(19vw, 22rem); bottom: 8vh; border-color: #d9cdb5; background: #fffaf0; box-shadow: none; }}
body.grammar-stamen-data-map .two-col {{ grid-template-columns: minmax(23rem, .72fr) 1.28fr; gap: 3.8vw; margin-top: 4vh; }}
body.grammar-stamen-data-map .label-board {{ grid-template-columns: 1.2fr .8fr; gap: .7rem; }}
body.grammar-stamen-data-map .label-board div:nth-child(1) {{ grid-row: span 2; }}
body.grammar-stamen-data-map .label-board div,
body.grammar-stamen-data-map .proof,
body.grammar-stamen-data-map .artifact-panel {{ background: #fffaf0; border-color: #d9cdb5; border-radius: 0; box-shadow: none; }}
body.grammar-stamen-data-map .dark .proof figcaption,
body.grammar-stamen-data-map .dark .artifact-panel figcaption {{ color: #677067; }}
body.grammar-stamen-data-map .dark .proof figcaption b,
body.grammar-stamen-data-map .dark .artifact-panel figcaption b {{ color: #1e2925; }}
body.grammar-stamen-data-map .evidence-grid {{ grid-template-columns: minmax(0, 1fr) minmax(14rem, 18vw); gap: 2.8vw; }}
body.grammar-stamen-data-map .proof {{ order: -1; padding: .6rem; }}
body.grammar-stamen-data-map .matrix-grid {{ grid-template-columns: minmax(17rem, 22vw) minmax(0, 1fr); }}
body.grammar-stamen-data-map table {{ font-size: .85rem; background: rgba(255,250,240,.62); }}
body.grammar-stamen-data-map td,
body.grammar-stamen-data-map th {{ border-top-color: #d9cdb5; }}

body.grammar-couture-exhibition .slide {{ padding: 4.9vh 5.4vw 7.2vh; background: #f7f1e4; color: #12110f; }}
body.grammar-couture-exhibition .slide {{ --cover-art-height: 25vh; --proof-visual-height: 58vh; --artifact-visual-height: 51vh; }}
body.grammar-couture-exhibition .dark,
body.grammar-couture-exhibition .light {{ background: #f7f1e4; color: #12110f; }}
body.grammar-couture-exhibition .dark::before,
body.grammar-couture-exhibition .light::before {{ display: none; }}
body.grammar-couture-exhibition .slide::after {{ content: ""; position: absolute; left: 5.4vw; right: 5.4vw; top: 4.9vh; height: 1px; background: #d8cbb8; pointer-events: none; }}
body.grammar-couture-exhibition h1,
body.grammar-couture-exhibition h2,
body.grammar-couture-exhibition .spine b {{ font-family: "Didot", "Bodoni 72", Georgia, serif; font-weight: 500; color: #12110f; }}
body.grammar-couture-exhibition h1 {{ max-width: 74vw; font-size: clamp(3.5rem, 7.6vw, 8.2rem); line-height: .99; }}
body.grammar-couture-exhibition h2 {{ max-width: 78vw; font-size: clamp(2rem, 3.9vw, 4.6rem); line-height: 1.04; }}
body.grammar-couture-exhibition .kicker {{ color: #8a6f45; letter-spacing: 0; }}
body.grammar-couture-exhibition .rule {{ width: 12vw; height: 1px; background: #8a6f45; margin-bottom: 3.8vh; }}
body.grammar-couture-exhibition .subtitle,
body.grammar-couture-exhibition .lead {{ color: #62594d; }}
body.grammar-couture-exhibition .cover-art {{ right: 5.4vw; bottom: 7.5vh; width: min(20vw, 23rem); padding: .42rem; background: #fffaf1; border-color: #d8cbb8; border-radius: 0; box-shadow: none; }}
body.grammar-couture-exhibition .cover .metrics {{ max-width: 48vw; }}
body.grammar-couture-exhibition .metrics {{ max-width: 76vw; border-top-color: #d8cbb8; }}
body.grammar-couture-exhibition .metric strong {{ color: #8a6f45; font-family: "Didot", "Bodoni 72", Georgia, serif; }}
body.grammar-couture-exhibition .two-col {{ grid-template-columns: minmax(22rem, .68fr) 1.32fr; gap: 3.2vw; margin-top: 3.8vh; }}
body.grammar-couture-exhibition .label-board {{ grid-template-columns: 1.12fr .88fr; gap: .72rem; }}
body.grammar-couture-exhibition .label-board div:nth-child(1) {{ grid-row: span 2; min-height: 8rem; }}
body.grammar-couture-exhibition .label-board div,
body.grammar-couture-exhibition .proof,
body.grammar-couture-exhibition .artifact-panel {{ background: #fffaf1; border-color: #d8cbb8; border-radius: 0; box-shadow: none; }}
body.grammar-couture-exhibition .dark .proof figcaption,
body.grammar-couture-exhibition .dark .artifact-panel figcaption {{ color: #6d665c; }}
body.grammar-couture-exhibition .dark .proof figcaption b,
body.grammar-couture-exhibition .dark .artifact-panel figcaption b {{ color: #12110f; }}
body.grammar-couture-exhibition .label-board span,
body.grammar-couture-exhibition td:first-child,
body.grammar-couture-exhibition .proof-notes span,
body.grammar-couture-exhibition .artifact-notes span {{ color: #8a6f45; }}
body.grammar-couture-exhibition .evidence-grid {{ grid-template-columns: minmax(12rem, 16vw) minmax(0, 1fr); gap: 2.2vw; }}
body.grammar-couture-exhibition .proof {{ padding: .42rem; }}
body.grammar-couture-exhibition .artifact-panel {{ padding: .48rem; }}
body.grammar-couture-exhibition table {{ font-size: .84rem; background: rgba(255,250,241,.6); }}
body.grammar-couture-exhibition td,
body.grammar-couture-exhibition th {{ border-top-color: #d8cbb8; padding: .62rem 0; }}

body.grammar-huashu-editorial-lab .slide {{ padding: 4.5vh 4.7vw 6.8vh; background: #f8f3e8; color: #0c0c0c; }}
body.grammar-huashu-editorial-lab .slide {{ --cover-art-height: 18vh; --proof-visual-height: 55vh; --artifact-visual-height: 44vh; }}
body.grammar-huashu-editorial-lab .dark {{ background: #111111; color: #f8f3e8; }}
body.grammar-huashu-editorial-lab .dark::before {{ display: none; }}
body.grammar-huashu-editorial-lab .light {{ background: linear-gradient(90deg, rgba(12,12,12,.12) 0 1px, transparent 1px 100%), #f8f3e8; background-size: 8.333vw 100%; }}
body.grammar-huashu-editorial-lab h1,
body.grammar-huashu-editorial-lab h2,
body.grammar-huashu-editorial-lab .metric strong {{ font-family: "Helvetica Neue", Arial, sans-serif; font-weight: 860; line-height: 1.02; color: currentColor; }}
body.grammar-huashu-editorial-lab h1 {{ max-width: 78vw; font-size: clamp(3.35rem, 8.1vw, 8.7rem); }}
body.grammar-huashu-editorial-lab h2 {{ max-width: 82vw; font-size: clamp(2rem, 4.1vw, 5rem); }}
body.grammar-huashu-editorial-lab .kicker {{ display: inline-block; background: #d74a2f; color: #f8f3e8; padding: .18rem .5rem; letter-spacing: 0; }}
body.grammar-huashu-editorial-lab .rule {{ width: 24vw; height: 4px; background: #d74a2f; margin-bottom: 3.8vh; }}
body.grammar-huashu-editorial-lab .subtitle,
body.grammar-huashu-editorial-lab .lead {{ color: color-mix(in srgb, currentColor 74%, transparent); }}
body.grammar-huashu-editorial-lab .tags span,
body.grammar-huashu-editorial-lab .metric strong,
body.grammar-huashu-editorial-lab td:first-child,
body.grammar-huashu-editorial-lab .label-board span,
body.grammar-huashu-editorial-lab .proof-notes span,
body.grammar-huashu-editorial-lab .artifact-notes span {{ color: #d74a2f; }}
body.grammar-huashu-editorial-lab .cover .tags {{ max-width: 52vw; }}
body.grammar-huashu-editorial-lab .metrics {{ border: 3px solid currentColor; padding: 0; gap: 0; max-width: 76vw; }}
body.grammar-huashu-editorial-lab .cover .metrics {{ max-width: 55vw; }}
body.grammar-huashu-editorial-lab .metric {{ padding: .86rem; border-right: 3px solid currentColor; }}
body.grammar-huashu-editorial-lab .metric:last-child {{ border-right: 0; }}
body.grammar-huashu-editorial-lab .two-col {{ grid-template-columns: minmax(23rem, .78fr) 1.22fr; gap: 2.6vw; margin-top: 3.6vh; }}
body.grammar-huashu-editorial-lab .label-board {{ grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .55rem; }}
body.grammar-huashu-editorial-lab .label-board div,
body.grammar-huashu-editorial-lab .proof,
body.grammar-huashu-editorial-lab .artifact-panel {{ background: #fffaf1; border: 3px solid currentColor; border-radius: 0; box-shadow: none; }}
body.grammar-huashu-editorial-lab .cover-art {{ right: 4.7vw; bottom: 7vh; width: min(20vw, 23rem); border: 3px solid currentColor; background: #f8f3e8; box-shadow: none; }}
body.grammar-huashu-editorial-lab .cover-art img {{ height: 28vh; }}
body.grammar-huashu-editorial-lab .dark .label-board div,
body.grammar-huashu-editorial-lab .dark .proof,
body.grammar-huashu-editorial-lab .dark .artifact-panel {{ background: #f8f3e8; color: #0c0c0c; }}
body.grammar-huashu-editorial-lab .dark .proof figcaption,
body.grammar-huashu-editorial-lab .dark .artifact-panel figcaption {{ color: #5f5b52; }}
body.grammar-huashu-editorial-lab .dark .proof figcaption b,
body.grammar-huashu-editorial-lab .dark .artifact-panel figcaption b {{ color: #0c0c0c; }}
body.grammar-huashu-editorial-lab .evidence-grid {{ grid-template-columns: minmax(12rem, 15vw) minmax(0, 1fr); gap: 2vw; }}
body.grammar-huashu-editorial-lab .matrix-grid {{ grid-template-columns: minmax(13rem, 17vw) minmax(0, 1fr); gap: 2.2vw; }}
body.grammar-huashu-editorial-lab table {{ font-size: .8rem; border: 3px solid currentColor; background: #fffaf1; }}
body.grammar-huashu-editorial-lab .dark table {{ background: #f8f3e8; color: #0c0c0c; }}
body.grammar-huashu-editorial-lab td,
body.grammar-huashu-editorial-lab th {{ border-top: 3px solid currentColor; padding: .52rem .35rem; }}

body.grammar-prism-newsroom-index .slide {{ padding: 4.4vh 5.1vw 6.8vh; background: #fcfdfb; color: #111827; --cover-art-height: 21vh; --proof-visual-height: 56vh; --artifact-visual-height: 43vh; }}
body.grammar-prism-newsroom-index .dark {{ background: #f5f6f1; color: #111827; }}
body.grammar-prism-newsroom-index .dark::before {{ display: none; }}
body.grammar-prism-newsroom-index h1,
body.grammar-prism-newsroom-index h2 {{ font-family: Georgia, "Times New Roman", serif; font-weight: 560; line-height: 1.1; color: #111827; }}
body.grammar-prism-newsroom-index h1 {{ max-width: 64vw; font-size: clamp(3rem, 5.7vw, 6.15rem); }}
body.grammar-prism-newsroom-index h2 {{ max-width: 78vw; font-size: clamp(1.9rem, 3.2vw, 3.85rem); }}
body.grammar-prism-newsroom-index .kicker {{ color: #b18446; letter-spacing: .02em; }}
body.grammar-prism-newsroom-index .rule {{ background: #d6dccf; margin-bottom: 4vh; }}
body.grammar-prism-newsroom-index .cover-source-rail {{ grid-template-columns: minmax(19rem, 32vw) minmax(0, 1fr); gap: 4.2vw; }}
body.grammar-prism-newsroom-index .cover-source-rail .cover-art {{ padding: 0; border: 0; background: transparent; box-shadow: none; }}
body.grammar-prism-newsroom-index .cover-art img {{ height: 31vh; border: 1px solid #dbe2d7; background: #fff; }}
body.grammar-prism-newsroom-index .metrics {{ border-top: 1px solid #d8ded4; max-width: 72vw; gap: 1.6rem; }}
body.grammar-prism-newsroom-index .metric strong {{ color: #111827; font-size: clamp(1.55rem, 2.45vw, 2.7rem); }}
body.grammar-prism-newsroom-index .metric span,
body.grammar-prism-newsroom-index .subtitle,
body.grammar-prism-newsroom-index .lead {{ color: #667085; }}
body.grammar-prism-newsroom-index .two-col {{ grid-template-columns: minmax(20rem, .7fr) 1.3fr; gap: 4vw; }}
body.grammar-prism-newsroom-index .label-board {{ gap: 0; border-top: 1px solid #dfe5dc; }}
body.grammar-prism-newsroom-index .label-board div {{ min-height: 4.9rem; border: 0; border-bottom: 1px solid #dfe5dc; background: transparent; box-shadow: none; padding: .82rem 0; }}
body.grammar-prism-newsroom-index .label-board span,
body.grammar-prism-newsroom-index td:first-child,
body.grammar-prism-newsroom-index .proof-notes span,
body.grammar-prism-newsroom-index .artifact-notes span {{ color: #b18446; }}
body.grammar-prism-newsroom-index .proof,
body.grammar-prism-newsroom-index .artifact-panel {{ background: #fff; border-color: #dfe5dc; box-shadow: none; }}
body.grammar-prism-newsroom-index .proof figcaption,
body.grammar-prism-newsroom-index .artifact-panel figcaption {{ border-top: 1px solid #e2e7df; padding-top: .72rem; color: #667085; }}
body.grammar-prism-newsroom-index table {{ font-size: .84rem; background: #fff; border-top: 2px solid #111827; }}
body.grammar-prism-newsroom-index td,
body.grammar-prism-newsroom-index th {{ padding: .62rem 0; border-top: 1px solid #e2e7df; }}

body.grammar-prism-workbench-index .slide {{ padding: 4.1vh 5vw 6.4vh; background: #fbfcf8; color: #101827; --cover-art-height: 34vh; --proof-visual-height: 57vh; --artifact-visual-height: 46vh; }}
body.grammar-prism-workbench-index .dark {{ background: #f1f4ec; color: #101827; }}
body.grammar-prism-workbench-index .dark::before {{ display: none; }}
body.grammar-prism-workbench-index h1,
body.grammar-prism-workbench-index h2,
body.grammar-prism-workbench-index .spine b {{ font-family: Georgia, "Times New Roman", serif; font-weight: 580; line-height: 1.08; color: #101827; }}
body.grammar-prism-workbench-index h1 {{ max-width: 60vw; font-size: clamp(2.7rem, 5vw, 5.7rem); }}
body.grammar-prism-workbench-index h2 {{ max-width: 78vw; font-size: clamp(1.85rem, 3vw, 3.55rem); }}
body.grammar-prism-workbench-index .kicker {{ color: #a67c3f; letter-spacing: .02em; }}
body.grammar-prism-workbench-index .rule {{ background: #dbe3d6; margin-bottom: 3.6vh; }}
body.grammar-prism-workbench-index .cover-source-rail {{ grid-template-columns: minmax(18rem, 31vw) minmax(0, 1fr); gap: 4vw; align-content: center; row-gap: .7rem; }}
body.grammar-prism-workbench-index .cover-source-rail .cover-art {{ padding: 0; border: 0; background: transparent; box-shadow: none; }}
body.grammar-prism-workbench-index .cover-art img {{ height: 40vh; border: 1px solid #dbe3d6; background: #fff; }}
body.grammar-prism-workbench-index .cover-art figcaption {{ color: #647083; border-top: 1px solid #dbe3d6; padding-top: .7rem; }}
body.grammar-prism-workbench-index .metrics {{ border-top: 1px solid #dbe3d6; max-width: 72vw; gap: 1.2rem; }}
body.grammar-prism-workbench-index .cover .metric {{ display: block; }}
body.grammar-prism-workbench-index .metric strong {{ color: #101827; font-size: clamp(1.05rem, 1.65vw, 1.9rem); overflow-wrap: anywhere; }}
body.grammar-prism-workbench-index .metric span,
body.grammar-prism-workbench-index .subtitle,
body.grammar-prism-workbench-index .lead,
body.grammar-prism-workbench-index p {{ color: #647083; }}
body.grammar-prism-workbench-index .two-col {{ grid-template-columns: minmax(24rem, .72fr) 1.28fr; gap: 3.4vw; margin-top: 3vh; }}
body.grammar-prism-workbench-index .label-board {{ gap: 0; border-top: 1px solid #dbe3d6; }}
body.grammar-prism-workbench-index .label-board div {{ min-height: 4.25rem; border: 0; border-bottom: 1px solid #dbe3d6; background: transparent; box-shadow: none; padding: .62rem 0; display: grid; grid-template-columns: 3.6rem minmax(0, 1fr); align-items: baseline; align-content: center; column-gap: .75rem; }}
body.grammar-prism-workbench-index .label-board span,
body.grammar-prism-workbench-index td:first-child,
body.grammar-prism-workbench-index .proof-notes span,
body.grammar-prism-workbench-index .artifact-notes span {{ color: #a67c3f; }}
body.grammar-prism-workbench-index .label-board b {{ font-family: "Helvetica Neue", Arial, sans-serif; font-size: 1rem; line-height: 1.22; font-weight: 640; }}
body.grammar-prism-workbench-index .proof,
body.grammar-prism-workbench-index .artifact-panel {{ background: #fff; border-color: #dbe3d6; box-shadow: none; }}
body.grammar-prism-workbench-index .proof figcaption,
body.grammar-prism-workbench-index .artifact-panel figcaption {{ border-top: 1px solid #dbe3d6; padding-top: .68rem; color: #647083; }}
body.grammar-prism-workbench-index table {{ font-size: .82rem; background: #fff; border-top: 2px solid #101827; }}
body.grammar-prism-workbench-index td,
body.grammar-prism-workbench-index th {{ padding: .56rem 0; border-top: 1px solid #dbe3d6; }}
body.grammar-prism-workbench-index .cover-source-rail .kicker {{ margin-bottom: .55rem; }}
body.grammar-prism-workbench-index .evidence-grid aside .metric,
body.grammar-prism-workbench-index .matrix-grid .metric {{ display: block; padding: .42rem 0; }}
body.grammar-prism-workbench-index .evidence-grid aside .metric strong,
body.grammar-prism-workbench-index .matrix-grid .metric strong {{ display: block; font-size: clamp(.92rem, 1.32vw, 1.48rem); line-height: 1.18; overflow-wrap: anywhere; }}
body.grammar-prism-workbench-index .evidence-grid aside .metric span,
body.grammar-prism-workbench-index .matrix-grid .metric span {{ display: block; margin-top: .18rem; font-size: .62rem; line-height: 1.22; }}

body.grammar-huashu-build-board .slide {{ padding: 4.2vh 4.4vw 6.2vh; background: #f6f3e9; color: #090909; --cover-art-height: 22vh; --proof-visual-height: 56vh; --artifact-visual-height: 45vh; }}
body.grammar-huashu-build-board .dark {{ background: #090909; color: #f6f3e9; }}
body.grammar-huashu-build-board .dark::before {{ display: none; }}
body.grammar-huashu-build-board .light {{ background: linear-gradient(90deg, rgba(9,9,9,.14) 0 1px, transparent 1px 100%), #f6f3e9; background-size: 10vw 100%; }}
body.grammar-huashu-build-board h1,
body.grammar-huashu-build-board h2,
body.grammar-huashu-build-board .metric strong {{ font-family: "Helvetica Neue", Arial, sans-serif; font-weight: 900; line-height: 1.06; color: currentColor; }}
body.grammar-huashu-build-board h1 {{ max-width: 82vw; font-size: clamp(3.45rem, 8.2vw, 9.1rem); }}
body.grammar-huashu-build-board h2 {{ max-width: 84vw; font-size: clamp(2rem, 4.15vw, 5.1rem); }}
body.grammar-huashu-build-board .kicker {{ display: inline-block; background: #ef2f24; color: #f6f3e9; padding: .18rem .52rem; letter-spacing: 0; }}
body.grammar-huashu-build-board .rule {{ height: 5px; width: 28vw; background: #ef2f24; margin-bottom: 3.6vh; opacity: 1; }}
body.grammar-huashu-build-board .metrics {{ border: 4px solid currentColor; gap: 0; padding: 0; max-width: 78vw; }}
body.grammar-huashu-build-board .metric {{ padding: .9rem .95rem; border-right: 4px solid currentColor; }}
body.grammar-huashu-build-board .metric:last-child {{ border-right: 0; }}
body.grammar-huashu-build-board .metric strong {{ color: #ef2f24; font-size: clamp(2rem, 4.5vw, 5.1rem); }}
body.grammar-huashu-build-board .metric span {{ color: currentColor; font-weight: 700; }}
body.grammar-huashu-build-board .evidence-grid {{ grid-template-columns: minmax(10.5rem, 13vw) minmax(0, 1fr); gap: 1.6vw; }}
body.grammar-huashu-build-board .evidence-grid aside .metric strong {{ font-size: clamp(1.05rem, 1.8vw, 2rem); }}
body.grammar-huashu-build-board .two-col {{ grid-template-columns: minmax(21rem, .72fr) 1.28fr; gap: 2.4vw; }}
body.grammar-huashu-build-board .label-board {{ gap: .5rem; }}
body.grammar-huashu-build-board .label-board div,
body.grammar-huashu-build-board .proof,
body.grammar-huashu-build-board .artifact-panel {{ border: 4px solid currentColor; border-radius: 0; background: #fffaf1; box-shadow: none; }}
body.grammar-huashu-build-board .dark .label-board div,
body.grammar-huashu-build-board .dark .proof,
body.grammar-huashu-build-board .dark .artifact-panel {{ background: #f6f3e9; color: #090909; }}
body.grammar-huashu-build-board .cover-art {{ border: 4px solid currentColor; background: #f6f3e9; box-shadow: none; }}
body.grammar-huashu-build-board .cover-art img {{ height: 30vh; }}
body.grammar-huashu-build-board .proof figcaption,
body.grammar-huashu-build-board .artifact-panel figcaption {{ color: #56524a; }}
body.grammar-huashu-build-board table {{ font-size: .8rem; background: #fffaf1; border: 4px solid currentColor; }}
body.grammar-huashu-build-board td,
body.grammar-huashu-build-board th {{ border-top: 3px solid currentColor; padding: .5rem .36rem; }}
body.grammar-huashu-build-board td:first-child,
body.grammar-huashu-build-board .label-board span,
body.grammar-huashu-build-board .proof-notes span,
body.grammar-huashu-build-board .artifact-notes span {{ color: #ef2f24; }}

body.grammar-huashu-issue-broadsheet .slide {{ padding: 4.05vh 4.2vw 6vh; background: #f4f0e6; color: #090909; --cover-art-height: 21vh; --proof-visual-height: 56vh; --artifact-visual-height: 46vh; }}
body.grammar-huashu-issue-broadsheet .dark {{ background: #090909; color: #f4f0e6; }}
body.grammar-huashu-issue-broadsheet .dark::before {{ display: none; }}
body.grammar-huashu-issue-broadsheet .light {{ background: linear-gradient(90deg, rgba(9,9,9,.12) 0 1px, transparent 1px 100%), #f4f0e6; background-size: 8.333vw 100%; }}
body.grammar-huashu-issue-broadsheet h1,
body.grammar-huashu-issue-broadsheet h2,
body.grammar-huashu-issue-broadsheet .metric strong {{ font-family: "Helvetica Neue", Arial, sans-serif; font-weight: 900; line-height: 1.05; color: currentColor; }}
body.grammar-huashu-issue-broadsheet h1 {{ max-width: 82vw; font-size: clamp(3rem, 7.4vw, 8.1rem); }}
body.grammar-huashu-issue-broadsheet h2 {{ max-width: 84vw; font-size: clamp(1.9rem, 3.75vw, 4.65rem); }}
body.grammar-huashu-issue-broadsheet .kicker {{ display: inline-block; border: 3px solid currentColor; background: #d6261f; color: #f4f0e6; padding: .14rem .48rem; letter-spacing: 0; }}
body.grammar-huashu-issue-broadsheet .rule {{ height: 4px; width: 34vw; background: #d6261f; margin-bottom: 3.2vh; opacity: 1; }}
body.grammar-huashu-issue-broadsheet .metrics {{ border: 3px solid currentColor; gap: 0; padding: 0; max-width: 80vw; }}
body.grammar-huashu-issue-broadsheet .metric {{ padding: .72rem .82rem; border-right: 3px solid currentColor; }}
body.grammar-huashu-issue-broadsheet .metric:last-child {{ border-right: 0; }}
body.grammar-huashu-issue-broadsheet .metric strong {{ color: #d6261f; font-size: clamp(1.6rem, 3.2vw, 3.7rem); }}
body.grammar-huashu-issue-broadsheet .metric span {{ color: currentColor; font-weight: 700; }}
body.grammar-huashu-issue-broadsheet .two-col {{ grid-template-columns: minmax(22rem, .75fr) 1.25fr; gap: 2.4vw; }}
body.grammar-huashu-issue-broadsheet .label-board {{ gap: .45rem; }}
body.grammar-huashu-issue-broadsheet .label-board div,
body.grammar-huashu-issue-broadsheet .proof,
body.grammar-huashu-issue-broadsheet .artifact-panel {{ border: 3px solid currentColor; border-radius: 0; background: #fff9ed; box-shadow: none; }}
body.grammar-huashu-issue-broadsheet .label-board div {{ min-height: 4.25rem; padding: .64rem .72rem; }}
body.grammar-huashu-issue-broadsheet .dark .label-board div,
body.grammar-huashu-issue-broadsheet .dark .proof,
body.grammar-huashu-issue-broadsheet .dark .artifact-panel {{ background: #f4f0e6; color: #090909; }}
body.grammar-huashu-issue-broadsheet .evidence-grid {{ grid-template-columns: minmax(11.5rem, 14.5vw) minmax(0, 1fr); gap: 2.1vw; }}
body.grammar-huashu-issue-broadsheet .evidence-grid aside .metrics {{ border: 3px solid currentColor; gap: 0; max-width: 100%; }}
body.grammar-huashu-issue-broadsheet .evidence-grid aside .metric {{ display: block; padding: .42rem .52rem; border-right: 0; border-bottom: 3px solid currentColor; }}
body.grammar-huashu-issue-broadsheet .evidence-grid aside .metric:last-child {{ border-bottom: 0; }}
body.grammar-huashu-issue-broadsheet .evidence-grid aside .metric strong {{ display: block; font-size: clamp(.86rem, 1.18vw, 1.35rem); line-height: 1.16; overflow-wrap: anywhere; }}
body.grammar-huashu-issue-broadsheet .evidence-grid aside .metric span {{ display: block; margin-top: .16rem; font-size: .58rem; line-height: 1.2; }}
body.grammar-huashu-issue-broadsheet .cover-art {{ border: 3px solid currentColor; background: #f4f0e6; box-shadow: none; }}
body.grammar-huashu-issue-broadsheet .cover-art img {{ height: 29vh; }}
body.grammar-huashu-issue-broadsheet .proof figcaption,
body.grammar-huashu-issue-broadsheet .artifact-panel figcaption {{ color: #514d45; }}
body.grammar-huashu-issue-broadsheet table {{ font-size: .78rem; background: #fff9ed; border: 3px solid currentColor; }}
body.grammar-huashu-issue-broadsheet td,
body.grammar-huashu-issue-broadsheet th {{ border-top: 3px solid currentColor; padding: .48rem .34rem; }}
body.grammar-huashu-issue-broadsheet td:first-child,
body.grammar-huashu-issue-broadsheet .label-board span,
body.grammar-huashu-issue-broadsheet .proof-notes span,
body.grammar-huashu-issue-broadsheet .artifact-notes span {{ color: #d6261f; }}

body.grammar-gallery-proof-room .slide {{ padding: 5vh 5.4vw 6.8vh; background: #f1ede4; color: #171412; --cover-art-height: 24vh; --proof-visual-height: 58vh; --artifact-visual-height: 47vh; }}
body.grammar-gallery-proof-room .dark {{ background: #24211d; color: #f1ede4; }}
body.grammar-gallery-proof-room .dark::before {{ display: none; }}
body.grammar-gallery-proof-room h1,
body.grammar-gallery-proof-room h2 {{ font-family: "Iowan Old Style", Georgia, serif; font-weight: 520; line-height: 1.1; }}
body.grammar-gallery-proof-room h1 {{ max-width: 72vw; font-size: clamp(3.5rem, 7.4vw, 8rem); }}
body.grammar-gallery-proof-room h2 {{ max-width: 78vw; font-size: clamp(2rem, 3.7vw, 4.45rem); }}
body.grammar-gallery-proof-room .kicker {{ color: #6f8061; letter-spacing: .04em; }}
body.grammar-gallery-proof-room .rule {{ background: #6f8061; width: 18vw; margin-bottom: 4.6vh; }}
body.grammar-gallery-proof-room .proof,
body.grammar-gallery-proof-room .artifact-panel,
body.grammar-gallery-proof-room .cover-art {{ background: #f9f6ef; border-color: #d6c9bb; box-shadow: none; }}
body.grammar-gallery-proof-room .proof {{ padding: .5rem; }}
body.grammar-gallery-proof-room .proof-gallery-split .proof-visual,
body.grammar-gallery-proof-room .artifact-showcase .artifact-visual {{ height: 58vh; min-height: 22rem; max-height: 59vh; }}
body.grammar-gallery-proof-room .proof figcaption,
body.grammar-gallery-proof-room .artifact-panel figcaption {{ font-family: "Helvetica Neue", Arial, sans-serif; text-transform: none; color: #736b61; border-top: 1px solid #d6c9bb; padding-top: .7rem; }}
body.grammar-gallery-proof-room .proof figcaption b,
body.grammar-gallery-proof-room .artifact-panel figcaption b {{ color: #171412; font-weight: 700; }}
body.grammar-gallery-proof-room .label-board div {{ background: transparent; border: 0; border-top: 1px solid #d6c9bb; box-shadow: none; padding-left: 0; }}
body.grammar-gallery-proof-room .label-board span,
body.grammar-gallery-proof-room td:first-child,
body.grammar-gallery-proof-room .proof-notes span,
body.grammar-gallery-proof-room .artifact-notes span {{ color: #6f8061; }}
body.grammar-gallery-proof-room .two-col {{ grid-template-columns: minmax(16rem, 24vw) minmax(0, 1fr); gap: 3vw; }}
body.grammar-gallery-proof-room table {{ font-size: .84rem; background: rgba(249,246,239,.78); }}
body.grammar-gallery-proof-room td,
body.grammar-gallery-proof-room th {{ border-top-color: #d6c9bb; padding: .6rem 0; }}

body.grammar-broadsheet-data-room .slide {{ padding: 4.6vh 4.8vw 6.6vh; background: #fbfaf3; color: #101010; --cover-art-height: 20vh; --proof-visual-height: 57vh; --artifact-visual-height: 43vh; }}
body.grammar-broadsheet-data-room .dark {{ background: #efede3; color: #101010; }}
body.grammar-broadsheet-data-room .dark::before {{ display: none; }}
body.grammar-broadsheet-data-room h1,
body.grammar-broadsheet-data-room h2 {{ font-family: Georgia, "Times New Roman", serif; font-weight: 620; line-height: 1.08; color: #101010; }}
body.grammar-broadsheet-data-room h1 {{ max-width: 76vw; font-size: clamp(3.1rem, 6.4vw, 7rem); }}
body.grammar-broadsheet-data-room h2 {{ max-width: 82vw; font-size: clamp(1.95rem, 3.45vw, 4.05rem); }}
body.grammar-broadsheet-data-room .kicker,
body.grammar-broadsheet-data-room .tags span,
body.grammar-broadsheet-data-room td:first-child,
body.grammar-broadsheet-data-room .label-board span,
body.grammar-broadsheet-data-room .proof-notes span,
body.grammar-broadsheet-data-room .artifact-notes span {{ color: #0b55c7; }}
body.grammar-broadsheet-data-room .rule {{ height: 2px; background: #101010; margin-bottom: 3.7vh; }}
body.grammar-broadsheet-data-room .cover-source-rail {{ grid-template-columns: minmax(18rem, 31vw) minmax(0, 1fr); gap: 3.8vw; }}
body.grammar-broadsheet-data-room .metrics {{ border-top: 2px solid #101010; border-bottom: 1px solid #d8d3c7; padding: .9rem 0; gap: 1.2rem; max-width: 78vw; }}
body.grammar-broadsheet-data-room .metric strong {{ color: #101010; font-size: clamp(1.5rem, 2.6vw, 2.9rem); }}
body.grammar-broadsheet-data-room .two-col {{ grid-template-columns: minmax(19rem, .66fr) 1.34fr; gap: 3.2vw; }}
body.grammar-broadsheet-data-room .label-board {{ gap: 0; border-top: 2px solid #101010; }}
body.grammar-broadsheet-data-room .label-board div {{ min-height: 4.7rem; border: 0; border-bottom: 1px solid #d8d3c7; background: transparent; box-shadow: none; padding: .75rem 0; }}
body.grammar-broadsheet-data-room .proof,
body.grammar-broadsheet-data-room .artifact-panel,
body.grammar-broadsheet-data-room .cover-art {{ background: #fff; border-color: #d8d3c7; box-shadow: none; }}
body.grammar-broadsheet-data-room .proof figcaption,
body.grammar-broadsheet-data-room .artifact-panel figcaption {{ color: #595959; border-top: 1px solid #d8d3c7; padding-top: .65rem; }}
body.grammar-broadsheet-data-room .proof-atlas-spread aside,
body.grammar-broadsheet-data-room .proof-marginalia aside {{ border-left-color: #101010; }}
body.grammar-broadsheet-data-room table {{ font-size: .78rem; background: #fff; border-top: 2px solid #101010; }}
body.grammar-broadsheet-data-room td,
body.grammar-broadsheet-data-room th {{ padding: .48rem 0; border-top: 1px solid #d8d3c7; }}

body.grammar-js-editorial-cascade .slide {{ padding: 4.1vh 4.4vw 6.2vh; background: #f6f7ef; color: #111316; --cover-art-height: 28vh; --proof-visual-height: 60vh; --artifact-visual-height: 52vh; }}
body.grammar-js-editorial-cascade .dark {{ background: #151618; color: #f6f7ef; }}
body.grammar-js-editorial-cascade .dark::before {{ display: none; }}
body.grammar-js-editorial-cascade .light::before {{ content: ""; position: absolute; inset: 0 auto 0 0; width: 18vw; background: #d7f249; opacity: .24; pointer-events: none; }}
body.grammar-js-editorial-cascade h1,
body.grammar-js-editorial-cascade h2,
body.grammar-js-editorial-cascade .metric strong {{ font-family: "Avenir Next", "Helvetica Neue", Arial, sans-serif; font-weight: 880; line-height: 1.08; color: currentColor; }}
body.grammar-js-editorial-cascade h1 {{ max-width: 78vw; font-size: clamp(3.4rem, 7.9vw, 8.8rem); }}
body.grammar-js-editorial-cascade h2 {{ max-width: 80vw; font-size: clamp(2rem, 4vw, 4.85rem); }}
body.grammar-js-editorial-cascade .kicker {{ display: inline-block; background: #184bff; color: #f6f7ef; padding: .2rem .54rem; letter-spacing: 0; }}
body.grammar-js-editorial-cascade .rule {{ width: 17vw; height: 5px; background: #ff5a2d; margin-bottom: 3.3vh; opacity: 1; }}
body.grammar-js-editorial-cascade .subtitle,
body.grammar-js-editorial-cascade .lead {{ color: color-mix(in srgb, currentColor 72%, transparent); }}
body.grammar-js-editorial-cascade .cover-art {{ right: 4.4vw; bottom: 6vh; width: min(26vw, 31rem); padding: .5rem; border: 0; background: #fffdf3; box-shadow: none; }}
body.grammar-js-editorial-cascade .cover-art img {{ height: 35vh; object-fit: cover; }}
body.grammar-js-editorial-cascade .cover .metrics {{ max-width: 52vw; }}
body.grammar-js-editorial-cascade .metrics {{ border: 0; padding-top: 0; gap: .75rem; max-width: 76vw; }}
body.grammar-js-editorial-cascade .metric {{ background: #fffdf3; border-top: 4px solid #111316; padding: .75rem .85rem; }}
body.grammar-js-editorial-cascade .dark .metric {{ background: #f6f7ef; color: #111316; }}
body.grammar-js-editorial-cascade .metric strong {{ color: #ff5a2d; font-size: clamp(1.8rem, 3.45vw, 4rem); }}
body.grammar-js-editorial-cascade .two-col {{ grid-template-columns: minmax(17rem, .56fr) minmax(0, 1.44fr); gap: 2.8vw; margin-top: 3.1vh; max-height: 70vh; }}
body.grammar-js-editorial-cascade .label-board {{ grid-template-columns: 1.35fr .65fr; gap: .58rem; }}
body.grammar-js-editorial-cascade .label-board div {{ min-height: 4.8rem; border: 0; background: #fffdf3; box-shadow: none; border-left: 5px solid #184bff; }}
body.grammar-js-editorial-cascade .label-board div:nth-child(1) {{ grid-row: span 2; min-height: 10.8rem; }}
body.grammar-js-editorial-cascade .label-board div:nth-child(3) {{ border-left-color: #ff5a2d; }}
body.grammar-js-editorial-cascade .label-board span,
body.grammar-js-editorial-cascade td:first-child,
body.grammar-js-editorial-cascade .proof-notes span,
body.grammar-js-editorial-cascade .artifact-notes span {{ color: #184bff; }}
body.grammar-js-editorial-cascade .proof,
body.grammar-js-editorial-cascade .artifact-panel {{ border: 0; border-radius: 0; background: #fffdf3; box-shadow: none; padding: .5rem; }}
body.grammar-js-editorial-cascade .proof figcaption,
body.grammar-js-editorial-cascade .artifact-panel figcaption {{ border-top: 4px solid #111316; padding-top: .6rem; color: #5f655d; }}
body.grammar-js-editorial-cascade .evidence-grid {{ grid-template-columns: minmax(11rem, 15vw) minmax(0, 1fr); gap: 1.9vw; margin-top: 1.8vh; }}
body.grammar-js-editorial-cascade .proof-stage .proof {{ width: min(100%, 75vw); justify-self: end; }}
body.grammar-js-editorial-cascade .proof-stage .proof-visual {{ height: 60vh; max-height: 61vh; }}
body.grammar-js-editorial-cascade .artifact-showcase .two-col {{ grid-template-columns: minmax(13rem, 19vw) minmax(0, 1fr); gap: 2vw; max-height: 72vh; }}
body.grammar-js-editorial-cascade .artifact-showcase .artifact-visual {{ height: 56vh; max-height: 57vh; }}
body.grammar-js-editorial-cascade table {{ font-size: .8rem; background: #fffdf3; border-top: 5px solid #111316; }}
body.grammar-js-editorial-cascade td,
body.grammar-js-editorial-cascade th {{ border-top: 1px solid #d9ded1; padding: .55rem 0; }}

body.grammar-sumi-research-scroll .slide {{ padding: 5.1vh 5.8vw 7vh; background: #fbf7ee; color: #17120e; --cover-art-height: 34vh; --proof-visual-height: 57vh; --artifact-visual-height: 48vh; }}
body.grammar-sumi-research-scroll .dark {{ background: #17120e; color: #fbf7ee; }}
body.grammar-sumi-research-scroll .dark::before {{ opacity: .06; background-image: linear-gradient(rgba(251,247,238,.28) 1px, transparent 1px); background-size: 100% 9vh; }}
body.grammar-sumi-research-scroll .light::before {{ content: ""; position: absolute; left: 3.4vw; top: 5vh; bottom: 7vh; width: 1px; background: #17120e; opacity: .18; pointer-events: none; }}
body.grammar-sumi-research-scroll h1,
body.grammar-sumi-research-scroll h2,
body.grammar-sumi-research-scroll .spine b {{ font-family: "Hiragino Mincho ProN", "Songti SC", "Iowan Old Style", Georgia, serif; font-weight: 520; line-height: 1.08; color: currentColor; }}
body.grammar-sumi-research-scroll h1 {{ max-width: 68vw; font-size: clamp(3rem, 6.4vw, 7rem); }}
body.grammar-sumi-research-scroll h2 {{ max-width: 76vw; font-size: clamp(1.9rem, 3.55vw, 4.2rem); }}
body.grammar-sumi-research-scroll .kicker {{ color: #b82f24; letter-spacing: .06em; }}
body.grammar-sumi-research-scroll .rule {{ width: 8vw; height: 2px; background: #b82f24; margin-bottom: 4.8vh; }}
body.grammar-sumi-research-scroll .cover-source-rail {{ grid-template-columns: minmax(18rem, 30vw) minmax(0, 1fr); gap: 5vw; align-content: center; }}
body.grammar-sumi-research-scroll .cover-art {{ background: #fffdf7; border-color: #d9cec0; border-radius: 0; box-shadow: none; padding: .55rem; }}
body.grammar-sumi-research-scroll .cover-source-rail .cover-art img {{ height: 40vh; }}
body.grammar-sumi-research-scroll .metrics {{ grid-template-columns: 1fr; max-width: 31rem; gap: 0; border-top: 2px solid currentColor; padding-top: 0; }}
body.grammar-sumi-research-scroll .metric {{ display: grid; grid-template-columns: minmax(5rem, .34fr) 1fr; align-items: baseline; border-bottom: 1px solid #d9cec0; padding: .78rem 0; }}
body.grammar-sumi-research-scroll .metric strong {{ color: #b82f24; font-family: "Hiragino Mincho ProN", "Songti SC", Georgia, serif; font-size: clamp(1.35rem, 2.2vw, 2.45rem); }}
body.grammar-sumi-research-scroll .metric span {{ font-size: .78rem; color: #70665b; }}
body.grammar-sumi-research-scroll .two-col {{ grid-template-columns: minmax(28rem, 1fr) minmax(12rem, .86fr); gap: 4.3vw; margin-top: 3.8vh; max-height: 66vh; }}
body.grammar-sumi-research-scroll .label-board {{ grid-template-columns: 1fr; border-left: 3px solid #b82f24; padding-left: 1rem; gap: 0; }}
body.grammar-sumi-research-scroll .label-board div {{ min-height: 4.2rem; border: 0; border-bottom: 1px solid #d9cec0; background: transparent; box-shadow: none; padding: .75rem 0; }}
body.grammar-sumi-research-scroll .label-board span,
body.grammar-sumi-research-scroll td:first-child,
body.grammar-sumi-research-scroll .proof-notes span,
body.grammar-sumi-research-scroll .artifact-notes span {{ color: #b82f24; }}
body.grammar-sumi-research-scroll .proof,
body.grammar-sumi-research-scroll .artifact-panel {{ background: #fffdf7; border-color: #d9cec0; border-radius: 0; box-shadow: none; padding: .58rem; }}
body.grammar-sumi-research-scroll .proof-marginalia .evidence-grid {{ grid-template-columns: minmax(0, 1fr) minmax(11rem, 14vw); gap: 2.4vw; max-height: 73vh; }}
body.grammar-sumi-research-scroll .proof-marginalia .proof {{ order: -1; }}
body.grammar-sumi-research-scroll .proof-marginalia .proof-visual {{ height: 57vh; max-height: 58vh; }}
body.grammar-sumi-research-scroll .artifact-marginalia .artifact-visual {{ height: 49vh; max-height: 50vh; }}
body.grammar-sumi-research-scroll .proof figcaption,
body.grammar-sumi-research-scroll .artifact-panel figcaption {{ border-top: 1px solid #d9cec0; padding-top: .62rem; color: #70665b; }}
body.grammar-sumi-research-scroll table {{ font-size: .8rem; background: transparent; border-top: 2px solid #17120e; }}
body.grammar-sumi-research-scroll td,
body.grammar-sumi-research-scroll th {{ border-top: 1px solid #d9cec0; padding: .58rem 0; }}

body.grammar-signal-intelligence-brief .slide {{ padding: 5vh 6.2vw 7.2vh; background: #f0ece3; color: #1a2030; --cover-art-height: 36vh; --proof-visual-height: 56vh; --artifact-visual-height: 48vh; }}
body.grammar-signal-intelligence-brief .dark {{ background: #1c2644; color: #e2dcd0; }}
body.grammar-signal-intelligence-brief .dark::before {{ opacity: .13; background-image: linear-gradient(rgba(200,168,112,.12) 1px, transparent 1px), linear-gradient(90deg, rgba(200,168,112,.08) 1px, transparent 1px); background-size: 5vw 8vh; }}
body.grammar-signal-intelligence-brief h1,
body.grammar-signal-intelligence-brief h2,
body.grammar-signal-intelligence-brief .metric strong,
body.grammar-signal-intelligence-brief .spine b {{ font-family: "Source Serif 4", "Iowan Old Style", Georgia, serif; font-weight: 650; line-height: 1.06; letter-spacing: 0; color: currentColor; }}
body.grammar-signal-intelligence-brief h1 {{ max-width: 70vw; font-size: clamp(3.2rem, 6.8vw, 7.5rem); }}
body.grammar-signal-intelligence-brief h2 {{ max-width: 80vw; font-size: clamp(2rem, 3.55vw, 4.25rem); }}
body.grammar-signal-intelligence-brief .kicker,
body.grammar-signal-intelligence-brief .metric strong,
body.grammar-signal-intelligence-brief td:first-child,
body.grammar-signal-intelligence-brief .label-board span,
body.grammar-signal-intelligence-brief .proof-notes span,
body.grammar-signal-intelligence-brief .artifact-notes span {{ color: #c8a870; }}
body.grammar-signal-intelligence-brief .rule {{ width: 14vw; height: 1px; background: #c8a870; margin-bottom: 4.6vh; }}
body.grammar-signal-intelligence-brief .subtitle,
body.grammar-signal-intelligence-brief .lead,
body.grammar-signal-intelligence-brief p {{ color: color-mix(in srgb, currentColor 72%, transparent); }}
body.grammar-signal-intelligence-brief .cover-source-rail {{ grid-template-columns: minmax(19rem, 31vw) minmax(0, 1fr); gap: 4.4vw; align-content: center; }}
body.grammar-signal-intelligence-brief .cover-art,
body.grammar-signal-intelligence-brief .label-board div,
body.grammar-signal-intelligence-brief .proof,
body.grammar-signal-intelligence-brief .artifact-panel {{ background: #f8f4eb; border: 1px solid #cac4b4; border-radius: 0; box-shadow: none; }}
body.grammar-signal-intelligence-brief .dark .cover-art,
body.grammar-signal-intelligence-brief .dark .proof,
body.grammar-signal-intelligence-brief .dark .artifact-panel {{ background: #232f55; border-color: #2e3d5c; color: #e2dcd0; }}
body.grammar-signal-intelligence-brief .cover-art img {{ height: 38vh; }}
body.grammar-signal-intelligence-brief .metrics {{ border-top: 1px solid currentColor; gap: 1.2rem; max-width: 72vw; }}
body.grammar-signal-intelligence-brief .metric strong {{ font-size: clamp(1.6rem, 2.6vw, 3rem); }}
body.grammar-signal-intelligence-brief .two-col {{ grid-template-columns: minmax(29rem, 1.02fr) minmax(14rem, .98fr); gap: 4vw; margin-top: 3.8vh; }}
body.grammar-signal-intelligence-brief .label-board {{ grid-template-columns: 1fr; border-left: 2px solid #c8a870; padding-left: 1rem; gap: 0; }}
body.grammar-signal-intelligence-brief .label-board div {{ min-height: 4.5rem; border: 0; border-bottom: 1px solid #cac4b4; background: transparent; padding: .72rem 0; }}
body.grammar-signal-intelligence-brief .evidence-grid {{ grid-template-columns: minmax(0, 1fr) minmax(15rem, 19vw); gap: 2.8vw; }}
body.grammar-signal-intelligence-brief .proof-atlas-spread .proof {{ order: -1; }}
body.grammar-signal-intelligence-brief .artifact-marginalia .artifact-visual {{ height: 50vh; }}
body.grammar-signal-intelligence-brief table {{ font-size: .84rem; background: #f8f4eb; border-top: 2px solid currentColor; }}
body.grammar-signal-intelligence-brief td,
body.grammar-signal-intelligence-brief th {{ border-top: 1px solid #cac4b4; padding: .64rem .2rem; }}

body.grammar-raw-grid-research .slide {{ padding: 4.4vh 4.6vw 6.8vh; background: #fff; color: #0a0a0a; --cover-art-height: 18vh; --proof-visual-height: 55vh; --artifact-visual-height: 45vh; }}
body.grammar-raw-grid-research .light,
body.grammar-raw-grid-research .dark {{ background: #fff; color: #0a0a0a; }}
body.grammar-raw-grid-research .light::before,
body.grammar-raw-grid-research .dark::before {{ content: ""; position: absolute; inset: 4.4vh 4.6vw 6.8vh; border: 3px solid #0a0a0a; pointer-events: none; opacity: 1; }}
body.grammar-raw-grid-research h1,
body.grammar-raw-grid-research h2,
body.grammar-raw-grid-research .metric strong {{ font-family: "Segoe UI", system-ui, -apple-system, Helvetica, Arial, sans-serif; font-weight: 900; line-height: 1.02; letter-spacing: 0; text-transform: uppercase; color: currentColor; }}
body.grammar-raw-grid-research h1 {{ max-width: 82vw; font-size: clamp(3.1rem, 7.8vw, 8.4rem); }}
body.grammar-raw-grid-research h2 {{ max-width: 84vw; font-size: clamp(2rem, 4.05vw, 5rem); }}
body.grammar-raw-grid-research .kicker {{ display: inline-block; background: #0a0a0a; color: #fff; padding: .22rem .55rem; letter-spacing: .06em; }}
body.grammar-raw-grid-research .rule {{ width: 18vw; height: 5px; background: #0a0a0a; margin-bottom: 3.4vh; }}
body.grammar-raw-grid-research .subtitle,
body.grammar-raw-grid-research .lead {{ color: #333; font-weight: 700; text-transform: uppercase; }}
body.grammar-raw-grid-research .tags span,
body.grammar-raw-grid-research .label-board span,
body.grammar-raw-grid-research td:first-child {{ color: #0a0a0a; }}
body.grammar-raw-grid-research .metrics {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0; border: 3px solid #0a0a0a; padding: 0; max-width: 76vw; box-shadow: 6px 6px 0 #0a0a0a; background: #e5edd6; }}
body.grammar-raw-grid-research .metric {{ padding: .82rem .9rem; border-right: 3px solid #0a0a0a; }}
body.grammar-raw-grid-research .metric:last-child {{ border-right: 0; }}
body.grammar-raw-grid-research .metric strong {{ font-size: clamp(1.45rem, 2.6vw, 3rem); }}
body.grammar-raw-grid-research .two-col {{ grid-template-columns: minmax(22rem, .76fr) 1.24fr; gap: 2.5vw; margin-top: 3.4vh; }}
body.grammar-raw-grid-research .label-board {{ grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0; }}
body.grammar-raw-grid-research .label-board div,
body.grammar-raw-grid-research .proof,
body.grammar-raw-grid-research .artifact-panel {{ background: #fff; border: 3px solid #0a0a0a; border-radius: 0; box-shadow: 6px 6px 0 #0a0a0a; }}
body.grammar-raw-grid-research .label-board div:nth-child(odd) {{ background: #f2d4cf; }}
body.grammar-raw-grid-research .label-board div:nth-child(even) {{ background: #e5edd6; }}
body.grammar-raw-grid-research .evidence-grid {{ grid-template-columns: minmax(12rem, 16vw) minmax(0, 1fr); gap: 2vw; }}
body.grammar-raw-grid-research .matrix-grid {{ grid-template-columns: minmax(13rem, 17vw) minmax(0, 1fr); gap: 2.2vw; }}
body.grammar-raw-grid-research table {{ font-size: .8rem; background: #fff; border: 3px solid #0a0a0a; box-shadow: 6px 6px 0 #0a0a0a; }}
body.grammar-raw-grid-research td,
body.grammar-raw-grid-research th {{ border-top: 3px solid #0a0a0a; padding: .52rem .35rem; }}
body.grammar-raw-grid-research .cover-art {{ width: min(16vw, 18rem); right: 4.6vw; bottom: 7vh; background: #fff; border: 3px solid #0a0a0a; box-shadow: 6px 6px 0 #0a0a0a; }}

body.grammar-stencil-field-tablet .slide {{ padding: 4.5vh 4.9vw 6.8vh; background: #f4efe0; color: #0a0a0a; --cover-art-height: 20vh; --proof-visual-height: 55vh; --artifact-visual-height: 48vh; }}
body.grammar-stencil-field-tablet .light,
body.grammar-stencil-field-tablet .dark {{ background: #f4efe0; color: #0a0a0a; }}
body.grammar-stencil-field-tablet .dark::before,
body.grammar-stencil-field-tablet .light::before {{ opacity: .08; background-image: linear-gradient(90deg, #000 0 1px, transparent 1px 100%); background-size: 8.333vw 100%; }}
body.grammar-stencil-field-tablet h1,
body.grammar-stencil-field-tablet h2,
body.grammar-stencil-field-tablet .metric strong,
body.grammar-stencil-field-tablet .spine b {{ font-family: "Stardos Stencil", "Arial Black", Impact, system-ui, sans-serif; font-weight: 800; line-height: .96; letter-spacing: 0; text-transform: uppercase; color: currentColor; }}
body.grammar-stencil-field-tablet h1 {{ max-width: 80vw; font-size: clamp(3.2rem, 8.1vw, 8.8rem); }}
body.grammar-stencil-field-tablet h2 {{ max-width: 82vw; font-size: clamp(2rem, 4.1vw, 5.05rem); }}
body.grammar-stencil-field-tablet .kicker {{ display: inline-block; background: #2d7e73; color: #f4efe0; padding: .22rem .6rem; letter-spacing: .04em; }}
body.grammar-stencil-field-tablet .rule {{ height: 5px; width: 22vw; background: #ee7a2e; margin-bottom: 3.7vh; }}
body.grammar-stencil-field-tablet .subtitle,
body.grammar-stencil-field-tablet .lead {{ color: #3f3b32; font-weight: 650; }}
body.grammar-stencil-field-tablet .tags span {{ border-color: #0a0a0a; background: #d8a93b; color: #0a0a0a; font-weight: 800; }}
body.grammar-stencil-field-tablet .metrics {{ grid-template-columns: repeat(3, minmax(0, 1fr)); gap: .75rem; border-top: 0; max-width: 78vw; }}
body.grammar-stencil-field-tablet .metric {{ background: #e2dcc9; border: 2px solid #0a0a0a; border-radius: 1rem; padding: .85rem 1rem; }}
body.grammar-stencil-field-tablet .metric:nth-child(1) {{ background: #d8a93b; }}
body.grammar-stencil-field-tablet .metric:nth-child(2) {{ background: #2d7e73; color: #f4efe0; }}
body.grammar-stencil-field-tablet .metric:nth-child(3) {{ background: #ee7a2e; }}
body.grammar-stencil-field-tablet .metric strong {{ font-size: clamp(1.55rem, 2.8vw, 3.25rem); }}
body.grammar-stencil-field-tablet .two-col {{ grid-template-columns: minmax(22rem, .74fr) 1.26fr; gap: 2.7vw; margin-top: 3.5vh; }}
body.grammar-stencil-field-tablet .label-board {{ grid-template-columns: 1.15fr .85fr; gap: .7rem; }}
body.grammar-stencil-field-tablet .label-board div,
body.grammar-stencil-field-tablet .proof,
body.grammar-stencil-field-tablet .artifact-panel {{ background: #e2dcc9; border: 2px solid #0a0a0a; border-radius: 1rem; box-shadow: none; }}
body.grammar-stencil-field-tablet .label-board div:nth-child(1) {{ grid-row: span 2; background: #d8a93b; }}
body.grammar-stencil-field-tablet .label-board div:nth-child(2) {{ background: #c73b7a; color: #f4efe0; }}
body.grammar-stencil-field-tablet .label-board div:nth-child(3) {{ background: #2d7e73; color: #f4efe0; }}
body.grammar-stencil-field-tablet .label-board span,
body.grammar-stencil-field-tablet td:first-child,
body.grammar-stencil-field-tablet .proof-notes span,
body.grammar-stencil-field-tablet .artifact-notes span {{ color: #ee7a2e; }}
body.grammar-stencil-field-tablet .evidence-grid {{ grid-template-columns: minmax(12rem, 16vw) minmax(0, 1fr); gap: 2.2vw; }}
body.grammar-stencil-field-tablet .artifact-showcase .artifact-visual,
body.grammar-stencil-field-tablet .proof-gallery-split .proof-visual {{ height: 54vh; }}
body.grammar-stencil-field-tablet table {{ font-size: .8rem; background: #e2dcc9; border: 2px solid #0a0a0a; border-radius: .7rem; overflow: hidden; }}
body.grammar-stencil-field-tablet td,
body.grammar-stencil-field-tablet th {{ border-top: 2px solid #0a0a0a; padding: .54rem .38rem; }}

/* Composition locks: keep layout-profile rules stronger than grammar skins. */
body .proof-led h2 {{ font-size: clamp(1.75rem, 2.85vw, 3.35rem); max-width: 86vw; }}
body .proof-led .subtitle {{ font-size: 1.02rem; max-width: 74vw; margin-top: .12rem; }}
body .proof-led .evidence-grid {{ grid-template-columns: minmax(11rem, 14vw) minmax(0, 1fr); gap: 1.8vw; margin-top: 1.3vh; max-height: 78vh; }}
body .proof-led .proof {{ padding: .62rem; }}
body .proof-led .proof-visual {{ height: 66vh; min-height: 25rem; max-height: 66vh; }}
body .proof-led .proof figcaption {{ margin-top: .82rem; font-size: .72rem; line-height: 1.24; }}
body .proof-led .proof-notes {{ grid-template-columns: repeat(2, minmax(0, 1fr)); margin-top: .9rem; gap: .2rem .62rem; font-size: .62rem; }}
body .proof-led .proof-notes li {{ padding-top: .2rem; }}
body .proof-led footer {{ display: none; }}
body .proof-atlas-spread .evidence-grid {{ grid-template-columns: minmax(0, 1fr) minmax(10rem, 12vw); gap: 1.6vw; max-height: 74vh; }}
body .proof-atlas-spread .proof {{ order: -1; }}
body .proof-atlas-spread .proof {{ padding: .48rem; }}
body .proof-atlas-spread .proof-visual {{ height: 57vh; min-height: 20rem; max-height: 58vh; }}
body .proof-atlas-spread .proof figcaption {{ margin-top: .55rem; font-size: .66rem; line-height: 1.12; }}
body .proof-atlas-spread .proof-notes {{ display: none; }}
body .proof-atlas-spread aside {{ border-left: 1px solid color-mix(in srgb, currentColor 18%, transparent); padding-left: 1.2rem; }}
body .proof-stage .evidence-grid {{ grid-template-columns: minmax(12rem, 16vw) minmax(0, 1fr); gap: 2.2vw; max-height: 71vh; }}
body .proof-stage .proof {{ width: min(100%, 72vw); justify-self: end; }}
body .proof-stage .proof-visual {{ height: 56vh; min-height: 21rem; max-height: 57vh; }}
body .proof-stage .proof-notes {{ display: none; }}
body .proof-dossier .evidence-grid {{ grid-template-columns: minmax(13rem, 17vw) minmax(0, 1fr); gap: 2.4vw; max-height: 71vh; }}
body .proof-dossier .proof {{ padding: .58rem; }}
body .proof-dossier .proof-visual {{ height: 56vh; min-height: 21rem; max-height: 57vh; }}
body .proof-dossier .proof-notes {{ display: none; }}
body .proof-ledger .evidence-grid {{ grid-template-columns: minmax(12rem, 15vw) minmax(0, 1fr); gap: 2vw; max-height: 72vh; }}
body .proof-ledger .proof-visual {{ height: 56vh; min-height: 22rem; max-height: 58vh; }}
body .proof-atlas-spread footer,
body .proof-gallery-split footer,
body .proof-stage footer,
body .proof-dossier footer,
body .proof-ledger footer {{ display: none; }}
body .proof-stage .proof-notes,
body .artifact-dossier footer {{ display: none; }}
body .proof-marginalia .evidence-grid {{ grid-template-columns: minmax(0, 1fr) minmax(11rem, 15vw); gap: 2.2vw; max-height: 72vh; }}
body .proof-marginalia .proof {{ order: -1; }}
body .proof-marginalia .proof-visual {{ height: 56vh; min-height: 22rem; max-height: 58vh; }}
body .proof-marginalia aside {{ border-left: 2px solid color-mix(in srgb, var(--gold) 72%, transparent); padding-left: 1rem; }}
body .proof-marginalia .proof {{ padding: .58rem; }}
body .proof-marginalia .proof figcaption {{ margin-top: .5rem; font-size: .66rem; line-height: 1.12; }}
body .proof-marginalia .proof-notes {{ display: none; }}
body .proof-gallery-split .evidence-grid {{ grid-template-columns: minmax(12rem, 16vw) minmax(0, 1fr); gap: 2.2vw; max-height: 70vh; }}
body .proof-gallery-split .proof {{ padding: .55rem; }}
body .proof-gallery-split .proof-visual {{ height: 56vh; min-height: 22rem; max-height: 57vh; }}
body .proof-gallery-split .proof-notes {{ display: none; }}
body.grammar-jetset-theory-grid .proof-stage .proof,
body.grammar-broadside-lab .proof-stage .proof {{ width: min(100%, 70vw); justify-self: end; }}
body.grammar-broadside-lab .proof-stage .proof-visual {{ height: 55.8vh; max-height: 56vh; }}
body.grammar-jetset-theory-grid .proof-ledger .proof-visual {{ height: 55.6vh; max-height: 56vh; }}
body.grammar-huashu-editorial-lab .proof-ledger .evidence-grid {{ grid-template-columns: minmax(10rem, 13vw) minmax(0, 1fr); gap: 1.6vw; max-height: 70vh; }}
body.grammar-huashu-editorial-lab .proof-ledger .proof {{ width: min(100%, 72vw); justify-self: end; }}
body.grammar-huashu-editorial-lab .proof-ledger .proof {{ padding: .42rem; }}
body.grammar-huashu-editorial-lab .proof-ledger .proof-visual {{ height: 53vh; min-height: 19rem; max-height: 54vh; }}
body.grammar-huashu-editorial-lab .proof-ledger .proof figcaption {{ margin-top: .42rem; font-size: .62rem; line-height: 1.1; }}
body.grammar-huashu-editorial-lab .proof-ledger .proof-notes {{ font-size: .56rem; gap: .14rem .36rem; margin-top: .14rem; }}
body.grammar-huashu-editorial-lab .proof-ledger .proof-notes li {{ padding-top: .14rem; }}
body.grammar-couture-exhibition .proof-gallery-split .evidence-grid {{ grid-template-columns: minmax(10rem, 14vw) minmax(0, 1fr); gap: 1.7vw; max-height: 72vh; }}
body.grammar-couture-exhibition .proof-gallery-split .proof-visual {{ height: 54vh; min-height: 20rem; max-height: 55vh; }}
body.grammar-couture-exhibition .proof-gallery-split .proof-notes {{ font-size: .58rem; gap: .16rem .45rem; margin-top: .16rem; }}
body.grammar-couture-exhibition .proof-gallery-split .proof-notes li {{ padding-top: .16rem; }}
body.grammar-prism-newsroom-index .cover-source-rail,
body.grammar-prism-workbench-index .cover-source-rail,
body.grammar-broadsheet-data-room .cover-source-rail {{ align-content: center; }}
body.grammar-prism-newsroom-index .cover-source-rail h1,
body.grammar-prism-workbench-index .cover-source-rail h1,
body.grammar-broadsheet-data-room .cover-source-rail h1 {{ font-size: clamp(2.45rem, 4.3vw, 4.8rem); line-height: 1.1; margin: .04em 0 .16em; }}
body.grammar-prism-newsroom-index .cover-source-rail h2,
body.grammar-prism-workbench-index .cover-source-rail h2,
body.grammar-broadsheet-data-room .cover-source-rail h2 {{ font-size: clamp(1.25rem, 1.95vw, 2.2rem); line-height: 1.18; margin: 0 0 .42rem; }}
body.grammar-prism-newsroom-index .cover-source-rail .lead,
body.grammar-prism-newsroom-index .cover-source-rail p,
body.grammar-prism-workbench-index .cover-source-rail .lead,
body.grammar-prism-workbench-index .cover-source-rail p,
body.grammar-broadsheet-data-room .cover-source-rail .lead,
body.grammar-broadsheet-data-room .cover-source-rail p {{ font-size: .92rem; line-height: 1.34; margin: .12rem 0; }}
body.grammar-prism-newsroom-index .cover-source-rail .tags span,
body.grammar-prism-workbench-index .cover-source-rail .tags span,
body.grammar-broadsheet-data-room .cover-source-rail .tags span {{ margin: .8rem .8rem 0 0; font-size: .62rem; }}
body.grammar-prism-newsroom-index .cover-source-rail .metrics,
body.grammar-prism-workbench-index .cover-source-rail .metrics,
body.grammar-broadsheet-data-room .cover-source-rail .metrics {{ margin-top: 1.5vh; padding-top: .75rem; max-width: 54vw; }}
body.grammar-prism-newsroom-index .artifact-dossier .two-col {{ max-height: 64vh; }}
body.grammar-prism-newsroom-index .artifact-dossier .two-col > ul {{ max-height: 63vh; overflow: hidden; }}
body.grammar-prism-workbench-index .artifact-dossier .two-col {{ grid-template-columns: minmax(19rem, .6fr) 1.4fr; gap: 2.6vw; max-height: 70vh; }}
body.grammar-prism-workbench-index .artifact-dossier .two-col > ul {{ max-height: 68vh; overflow: hidden; }}
body.grammar-prism-workbench-index .artifact-dossier .artifact-visual {{ height: 52vh; max-height: 53vh; }}
body.grammar-huashu-build-board .cover-poster-grid h1 {{ font-size: clamp(3rem, 6.5vw, 7rem); line-height: 1.06; }}
body.grammar-huashu-build-board .cover-poster-grid h2 {{ font-size: clamp(1.55rem, 2.5vw, 2.9rem); line-height: 1.12; }}
body.grammar-huashu-build-board .cover-poster-grid .metrics {{ margin-top: 2.4vh; max-width: 56vw; }}
body.grammar-huashu-build-board .cover-poster-grid .metric {{ padding: .58rem .64rem; }}
body.grammar-huashu-build-board .cover-poster-grid .metric strong {{ font-size: clamp(1.45rem, 2.7vw, 3rem); line-height: 1.12; }}
body.grammar-gallery-proof-room .kicker {{ display: inline-block; margin-bottom: .62rem; }}
body.grammar-gallery-proof-room h2 {{ margin-top: .22em; margin-bottom: .42em; line-height: 1.14; }}
body.grammar-gallery-proof-room .slide h2 + .subtitle,
body.grammar-gallery-proof-room .cover h2 + .lead {{ margin-top: 1.65rem; }}
body.grammar-gallery-proof-room .artifact-showcase footer,
body.grammar-broadsheet-data-room .artifact-marginalia footer {{ display: none; }}
body.grammar-gallery-proof-room .artifact-showcase .artifact-visual {{ height: 52vh; min-height: 20rem; max-height: 53vh; }}
body.grammar-gallery-proof-room .proof-gallery-split .evidence-grid {{ grid-template-columns: minmax(9.5rem, 12vw) minmax(0, 1fr); gap: 1.7vw; max-height: 74vh; }}
body.grammar-gallery-proof-room .proof-gallery-split .proof-visual {{ height: 56vh; min-height: 21rem; max-height: 57vh; }}
body.grammar-fathom-research-brief .artifact-dossier .artifact-notes {{ display: none; }}
body.grammar-prism-newsroom-index .proof-notes,
body.grammar-prism-workbench-index .proof-notes,
body.grammar-prism-clean-room .proof-notes,
body.grammar-systems-field-manual .proof-notes,
body.grammar-object-study-wall .proof-notes,
body.grammar-huashu-build-board .proof-notes,
body.grammar-huashu-issue-broadsheet .proof-notes,
body.grammar-gallery-proof-room .proof-notes,
body.grammar-gallery-proof-room .artifact-notes,
body.grammar-fathom-research-brief .proof-atlas-spread .proof-notes,
body.grammar-ia-research-archive .proof-marginalia .proof-notes,
body.grammar-broadsheet-data-room .proof-notes {{ display: none; }}
body.grammar-object-study-wall .slide h2 + .subtitle {{ margin-top: 1.2rem; }}
body.grammar-object-study-wall .evidence-grid aside .metrics {{ gap: 1.05rem; }}
body.grammar-object-study-wall .evidence-grid aside .metric {{ row-gap: 1rem; }}
body.grammar-object-study-wall .evidence-grid aside .metric strong {{ line-height: 1.2; }}
body.grammar-broadsheet-data-room .proof-atlas-spread .evidence-grid {{ grid-template-columns: minmax(0, 1fr) minmax(13rem, 16vw); }}
body.grammar-broadsheet-data-room .proof-atlas-spread .proof figcaption {{ margin-top: .85rem; font-size: .7rem; line-height: 1.24; }}
body.grammar-fathom-research-brief .proof-atlas-spread .proof figcaption,
body.grammar-ia-research-archive .proof-marginalia .proof figcaption {{ margin-top: .95rem; font-size: .7rem; line-height: 1.24; }}
body.grammar-ia-research-archive .artifact-marginalia .two-col {{ grid-template-columns: minmax(19rem, .66fr) 1.34fr; gap: 2.8vw; max-height: 70vh; }}
body.grammar-ia-research-archive .artifact-marginalia .two-col > ul {{ max-height: 68vh; overflow: hidden; }}
body.grammar-ia-research-archive .artifact-marginalia .artifact-visual {{ height: 52vh; max-height: 53vh; }}
body.grammar-ia-research-archive .artifact-marginalia .artifact-notes,
body.grammar-ia-research-archive .artifact-marginalia footer {{ display: none; }}
body.grammar-fathom-research-brief .artifact-dossier .two-col {{ grid-template-columns: minmax(18rem, .58fr) 1.42fr; gap: 2.6vw; max-height: 70vh; }}
body.grammar-fathom-research-brief .artifact-dossier .two-col > ul {{ max-height: 68vh; overflow: hidden; }}
body.grammar-fathom-research-brief .artifact-dossier .artifact-visual {{ height: 52vh; max-height: 53vh; }}
body.grammar-broadsheet-data-room .evidence-grid aside .metric strong {{ font-size: clamp(.95rem, 1.45vw, 1.62rem); line-height: 1.15; }}
body.grammar-huashu-build-board .proof-ledger .proof-visual,
body.grammar-huashu-issue-broadsheet .proof-ledger .proof-visual {{ height: 56vh; min-height: 21rem; max-height: 57vh; }}
body.grammar-huashu-build-board .proof-ledger .proof figcaption,
body.grammar-huashu-issue-broadsheet .proof-ledger .proof figcaption {{ margin-top: .82rem; font-size: .68rem; line-height: 1.22; }}
body.grammar-huashu-build-board .proof-ledger .proof,
body.grammar-huashu-issue-broadsheet .proof-ledger .proof {{ width: min(100%, 75vw); justify-self: end; }}
body.grammar-huashu-build-board .artifact-ledger footer,
body.grammar-huashu-build-board .artifact-ledger .artifact-notes,
body.grammar-huashu-issue-broadsheet .artifact-ledger footer,
body.grammar-huashu-issue-broadsheet .artifact-ledger .artifact-notes {{ display: none; }}
body.grammar-huashu-issue-broadsheet .content-field-manual footer {{ display: none; }}
body.grammar-huashu-issue-broadsheet .artifact-ledger .two-col {{ grid-template-columns: minmax(16rem, .52fr) 1.48fr; gap: 1.9vw; max-height: 70vh; }}
body.grammar-huashu-issue-broadsheet .artifact-ledger .two-col > ul {{ max-height: 68vh; overflow: hidden; }}
body.grammar-huashu-issue-broadsheet .artifact-ledger .artifact-visual {{ height: 52vh; min-height: 21rem; max-height: 53vh; }}
body.grammar-js-editorial-cascade .slide h2 + .subtitle,
body.grammar-js-editorial-cascade .cover h2 + .lead {{ margin-top: 1rem; }}
body.grammar-js-editorial-cascade h2 {{ margin-bottom: .46em; }}
body.grammar-js-editorial-cascade .cover .metric strong {{ font-size: clamp(1.18rem, 2vw, 2.25rem); line-height: 1.14; }}
body.grammar-js-editorial-cascade .cover .metric span {{ font-size: .68rem; line-height: 1.22; }}
body.grammar-js-editorial-cascade .proof-stage .evidence-grid {{ grid-template-columns: minmax(12rem, 16vw) minmax(0, 1fr); gap: 1.8vw; max-height: 68vh; }}
body.grammar-js-editorial-cascade .proof-stage .proof {{ width: min(100%, 70vw); }}
body.grammar-js-editorial-cascade .proof-stage .proof-visual {{ height: 56vh; min-height: 21rem; max-height: 57vh; }}
body.grammar-js-editorial-cascade .proof-stage .proof figcaption {{ margin-top: 1rem; font-size: .68rem; line-height: 1.2; }}
body.grammar-js-editorial-cascade .proof-stage .proof-notes,
body.grammar-js-editorial-cascade .proof-stage footer {{ display: none; }}
body.grammar-js-editorial-cascade .matrix-map footer {{ display: none; }}
body.grammar-js-editorial-cascade .evidence-grid aside .metrics {{ gap: .58rem; }}
body.grammar-js-editorial-cascade .evidence-grid aside .metric {{ padding: .48rem .58rem; }}
body.grammar-js-editorial-cascade .evidence-grid aside .metric strong {{ font-size: clamp(.95rem, 1.45vw, 1.65rem); line-height: 1.16; }}
body.grammar-js-editorial-cascade .evidence-grid aside .metric span {{ font-size: .64rem; line-height: 1.22; }}
body.grammar-js-editorial-cascade .artifact-showcase footer {{ display: none; }}
body.grammar-js-editorial-cascade .artifact-showcase .artifact-visual {{ height: 52vh; max-height: 53vh; }}
body.grammar-js-editorial-cascade .artifact-showcase .artifact-panel figcaption {{ margin-top: 1rem; font-size: .68rem; line-height: 1.18; }}
body.grammar-js-editorial-cascade .artifact-showcase .artifact-notes {{ display: none; }}
body.grammar-js-editorial-cascade .artifact-panel figcaption b,
body.grammar-js-editorial-cascade .proof figcaption b {{ color: #111316; }}
body.grammar-sumi-research-scroll .cover-source-rail {{ align-content: start; row-gap: .45rem; }}
body.grammar-sumi-research-scroll .cover-source-rail h1 {{ font-size: clamp(2.35rem, 4.45vw, 5rem); line-height: 1.1; margin: .04em 0 .18em; }}
body.grammar-sumi-research-scroll .cover-source-rail h2 {{ font-size: clamp(1.22rem, 1.9vw, 2.15rem); line-height: 1.18; margin: 0 0 .38rem; }}
body.grammar-sumi-research-scroll .cover-source-rail .lead,
body.grammar-sumi-research-scroll .cover-source-rail p {{ font-size: .9rem; line-height: 1.34; margin: .12rem 0; }}
body.grammar-sumi-research-scroll .cover-source-rail .cover-art img {{ height: 34vh; }}
body.grammar-sumi-research-scroll .cover-source-rail .metrics {{ margin-top: 1.4vh; max-width: 52vw; }}
body.grammar-sumi-research-scroll .cover-source-rail .metric {{ padding: .5rem 0; grid-template-columns: minmax(6.2rem, .38fr) 1fr; }}
body.grammar-sumi-research-scroll .cover-source-rail .metric strong {{ font-size: clamp(1.05rem, 1.7vw, 1.9rem); line-height: 1.12; }}
body.grammar-sumi-research-scroll .evidence-grid aside .metric,
body.grammar-sumi-research-scroll .matrix-grid .metric {{ display: block; padding: .5rem 0; }}
body.grammar-sumi-research-scroll .evidence-grid aside .metric strong,
body.grammar-sumi-research-scroll .matrix-grid .metric strong {{ display: block; font-size: clamp(.98rem, 1.35vw, 1.55rem); line-height: 1.18; }}
body.grammar-sumi-research-scroll .proof-marginalia .evidence-grid {{ grid-template-columns: minmax(0, 1fr) minmax(9rem, 11vw); gap: 1.5vw; }}
body.grammar-sumi-research-scroll .proof-marginalia .proof-visual {{ height: 57vh; min-height: 21rem; max-height: 58vh; }}
body.grammar-sumi-research-scroll .proof-marginalia .proof figcaption {{ margin-top: .78rem; font-size: .66rem; line-height: 1.18; }}
body.grammar-sumi-research-scroll .proof-marginalia .proof-notes,
body.grammar-sumi-research-scroll .proof-marginalia footer {{ display: none; }}
body.grammar-sumi-research-scroll .artifact-marginalia .artifact-notes,
body.grammar-sumi-research-scroll .artifact-marginalia footer {{ display: none; }}
body.grammar-sumi-research-scroll .artifact-panel figcaption b,
body.grammar-sumi-research-scroll .proof figcaption b {{ color: #17120e; }}
body.grammar-prism-newsroom-index .dark .proof figcaption b,
body.grammar-prism-newsroom-index .dark .artifact-panel figcaption b,
body.grammar-prism-workbench-index .dark .proof figcaption b,
body.grammar-prism-workbench-index .dark .artifact-panel figcaption b,
body.grammar-huashu-build-board .dark .proof figcaption b,
body.grammar-huashu-build-board .dark .artifact-panel figcaption b,
body.grammar-huashu-issue-broadsheet .dark .proof figcaption b,
body.grammar-huashu-issue-broadsheet .dark .artifact-panel figcaption b,
body.grammar-gallery-proof-room .dark .proof figcaption b,
body.grammar-gallery-proof-room .dark .artifact-panel figcaption b,
body.grammar-broadsheet-data-room .dark .proof figcaption b,
body.grammar-broadsheet-data-room .dark .artifact-panel figcaption b {{ color: #101010; }}
body.grammar-stamen-data-map .evidence-grid aside .metric {{ row-gap: .95rem; }}
body.grammar-stamen-data-map .evidence-grid aside .metric strong {{ line-height: 1.14; }}
body .proof-showcase h2 {{ font-size: clamp(1.75rem, 2.7vw, 3.25rem); max-width: 86vw; line-height: 1.04; }}
body .proof-showcase .subtitle {{ max-width: 72vw; font-size: 1.02rem; margin: .15rem 0 0; }}
body .proof-showcase .evidence-grid {{ grid-template-columns: minmax(12rem, 16vw) minmax(0, 1fr); gap: 2.3vw; margin-top: 1.7vh; max-height: 70vh; }}
body .proof-showcase .evidence-grid aside {{ gap: .85rem; max-height: 67vh; }}
body .proof-showcase li {{ margin: .52rem 0; line-height: 1.32; max-width: 22rem; font-size: .94rem; }}
body .proof-showcase .proof {{ padding: .65rem; }}
body .proof-showcase .proof {{ order: 0; }}
body .proof-showcase .proof-visual {{ height: 58vh; min-height: 23rem; max-height: 58vh; }}
body .proof-showcase .proof figcaption {{ margin-top: .55rem; font-size: .72rem; line-height: 1.2; }}
body .proof-showcase .proof-notes {{ grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .42rem .8rem; margin-top: .55rem; font-size: .72rem; }}
body .proof-showcase .proof-notes li {{ padding-top: .38rem; }}
body .matrix-ledger .matrix-grid {{ grid-template-columns: minmax(14rem, 20vw) minmax(0, 1fr); gap: 2.8vw; }}
body .matrix-map .matrix-grid {{ grid-template-columns: minmax(18rem, 24vw) minmax(0, 1fr); }}
body .artifact-rail .two-col {{ grid-template-columns: minmax(22rem, .76fr) 1.24fr; gap: 4.4vw; }}
body .artifact-dossier .two-col {{ grid-template-columns: minmax(18rem, .54fr) minmax(0, 1.46fr); gap: 2.6vw; max-height: 70vh; }}
body .artifact-dossier .two-col > ul {{ max-height: 68vh; overflow: hidden; }}
body .artifact-dossier .artifact-visual {{ height: 56vh; min-height: 21rem; max-height: 57vh; }}
body .artifact-dossier .artifact-notes {{ display: none; }}
body .artifact-showcase .two-col {{ grid-template-columns: minmax(17rem, 24vw) minmax(0, 1fr); gap: 3vw; margin-top: 2.4vh; max-height: 67vh; }}
body .artifact-showcase .two-col > ul {{ max-height: 66vh; overflow: hidden; }}
body .artifact-showcase .artifact-panel {{ padding: .65rem; }}
body .artifact-showcase .artifact-visual {{ height: 50vh; min-height: 20rem; max-height: 50vh; }}
body .artifact-showcase .artifact-notes {{ grid-template-columns: repeat(2, minmax(0, 1fr)); font-size: .72rem; }}
body .artifact-marginalia .two-col {{ grid-template-columns: minmax(26rem, .94fr) 1.06fr; gap: 4vw; margin-top: 3.4vh; max-height: 66vh; }}
body .artifact-marginalia .artifact-panel {{ border-radius: 0; box-shadow: none; }}
body .artifact-marginalia .artifact-visual {{ height: 47vh; min-height: 18rem; max-height: 49vh; }}
body .artifact-marginalia .artifact-notes {{ display: none; }}
body .artifact-ledger .two-col {{ grid-template-columns: minmax(24rem, .82fr) 1.18fr; gap: 3vw; margin-top: 3.7vh; max-height: 65vh; }}
body .artifact-ledger .artifact-visual {{ height: 42vh; min-height: 17rem; max-height: 44vh; }}
body .artifact-ledger .artifact-notes {{ display: none; }}
body .content-bento .two-col {{ grid-template-columns: minmax(22rem, .74fr) 1.26fr; gap: 3.8vw; margin-top: 4vh; max-height: 66vh; }}
body .content-bento .label-board {{ grid-template-columns: 1.18fr .82fr; gap: .75rem; }}
body .content-bento .label-board div:nth-child(1) {{ grid-row: span 2; }}
body .content-bento .label-board div {{ min-height: 5.2rem; }}
body .content-marginalia .two-col {{ grid-template-columns: minmax(28rem, 1.08fr) minmax(13rem, .92fr); gap: 4vw; margin-top: 3.7vh; max-height: 66vh; }}
body .content-marginalia .label-board {{ grid-template-columns: 1fr; border-left: 2px solid color-mix(in srgb, var(--gold) 75%, transparent); padding-left: 1rem; }}
body .content-marginalia .label-board div {{ min-height: 4.3rem; box-shadow: none; }}
body .content-workbench-index .two-col {{ grid-template-columns: minmax(24rem, .68fr) 1.32fr; gap: 3.2vw; margin-top: 2.8vh; max-height: 68vh; }}
body .content-workbench-index .two-col > ul {{ border-top: 1px solid color-mix(in srgb, currentColor 18%, transparent); padding-top: .72rem; max-height: 66vh; overflow: hidden; }}
body .content-workbench-index li {{ margin: .78rem 0; line-height: 1.42; max-width: 30rem; font-size: .92rem; }}
body .content-workbench-index .label-board {{ grid-template-columns: 1fr; gap: 0; align-self: stretch; border-top: 1px solid color-mix(in srgb, currentColor 18%, transparent); }}
body .content-workbench-index .label-board div {{ min-height: 4.15rem; border: 0; border-bottom: 1px solid color-mix(in srgb, currentColor 18%, transparent); background: transparent; box-shadow: none; padding: .58rem 0; display: grid; grid-template-columns: 3.5rem minmax(0, 1fr); align-items: baseline; align-content: center; column-gap: .72rem; }}
body .content-workbench-index .label-board b {{ font-size: .98rem; line-height: 1.22; }}
body .close.content-workbench-index .two-col {{ grid-template-columns: minmax(22rem, .62fr) 1.38fr; }}
body .close.content-workbench-index .label-board div {{ min-height: 5.05rem; }}
body .content-field-manual .two-col {{ grid-template-columns: minmax(24rem, .86fr) 1.14fr; gap: 3vw; margin-top: 3.7vh; max-height: 66vh; }}
body .content-field-manual .label-board {{ grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .55rem; }}
body .content-field-manual .label-board div {{ min-height: 4.5rem; box-shadow: none; }}
body .close.content-field-manual .two-col {{ grid-template-columns: minmax(25rem, .78fr) 1.22fr; align-items: stretch; }}
body .close.content-field-manual .label-board {{ grid-template-columns: 1fr; align-self: stretch; }}
body .close.content-field-manual .label-board div {{ min-height: 7.4rem; align-content: center; }}
body .close.content-bento .label-board div,
body .close.content-marginalia .label-board div {{ min-height: 6.6rem; }}
body .metrics-ledger .two-col {{ grid-template-columns: minmax(24rem, .85fr) 1.15fr; gap: 3vw; }}
body .metrics-ledger .two-col > .metrics {{ border: 2px solid currentColor; padding: 1rem; }}
body .cover-source-rail .cover-art {{ position: static; grid-column: 1; grid-row: 1 / span 8; width: 100%; bottom: auto; right: auto; }}
body.grammar-jetset-theory-grid .cover-poster-grid .metric strong {{ line-height: 1.08; }}
body.grammar-jetset-theory-grid .cover-poster-grid .metric span {{ display: block; }}
body.grammar-prism-publication-stack .cover-source-rail {{ grid-template-columns: minmax(18rem, 32vw) minmax(0, 1fr); gap: 4vw; align-content: center; row-gap: .7rem; }}
body.grammar-prism-publication-stack .cover-source-rail h1 {{ font-size: clamp(2.7rem, 4.7vw, 5.2rem); line-height: 1.06; margin: .05em 0 .16em; }}
body.grammar-prism-publication-stack .cover-source-rail h2 {{ font-size: clamp(1.35rem, 2.1vw, 2.4rem); line-height: 1.12; margin: 0 0 .45rem; }}
body.grammar-prism-publication-stack .cover-source-rail .lead,
body.grammar-prism-publication-stack .cover-source-rail p {{ font-size: .94rem; line-height: 1.34; margin: .12rem 0; }}
body.grammar-prism-publication-stack .cover-source-rail .tags span {{ margin-top: .7rem; }}
body.grammar-prism-publication-stack .cover-source-rail .metrics {{ margin-top: 2vh; padding-top: .8rem; }}
body.grammar-prism-publication-stack .cover-art img {{ height: 44vh; }}
body.grammar-prism-publication-stack .proof-dossier .evidence-grid {{ grid-template-columns: minmax(12rem, 15vw) minmax(0, 1fr); gap: 2vw; }}
body.grammar-prism-publication-stack .proof-dossier .proof-visual {{ height: 58vh; max-height: 59vh; }}
body.grammar-prism-publication-stack .artifact-dossier .two-col {{ grid-template-columns: minmax(18rem, .56fr) 1.44fr; gap: 2.6vw; max-height: 69vh; }}
body.grammar-prism-publication-stack .artifact-dossier .two-col > ul {{ max-height: 66vh; overflow: hidden; }}
body.grammar-prism-publication-stack .artifact-dossier .artifact-visual {{ height: 56vh; max-height: 57vh; }}
body.grammar-couture-exhibition .proof-gallery-split .evidence-grid {{ grid-template-columns: minmax(10rem, 14vw) minmax(0, 1fr); gap: 1.8vw; }}
body.grammar-couture-exhibition .proof-gallery-split .proof-visual {{ height: 59vh; max-height: 60vh; }}
body.grammar-couture-exhibition .artifact-showcase .two-col {{ grid-template-columns: minmax(14rem, 19vw) minmax(0, 1fr); gap: 2.2vw; max-height: 70vh; }}
body.grammar-couture-exhibition .artifact-showcase .artifact-visual {{ height: 54vh; max-height: 55vh; }}
body.grammar-huashu-editorial-lab .proof-ledger .evidence-grid {{ grid-template-columns: minmax(10rem, 13vw) minmax(0, 1fr); gap: 1.6vw; max-height: 70vh; }}
body.grammar-huashu-editorial-lab .proof-ledger .proof {{ width: min(100%, 72vw); justify-self: end; padding: .42rem; }}
body.grammar-huashu-editorial-lab .proof-ledger .proof-visual {{ height: 53vh; min-height: 19rem; max-height: 54vh; }}
body.grammar-huashu-editorial-lab .proof-ledger .proof figcaption {{ margin-top: .42rem; font-size: .62rem; line-height: 1.1; }}
body.grammar-huashu-editorial-lab .proof-ledger .proof-notes {{ font-size: .56rem; gap: .14rem .36rem; margin-top: .14rem; }}
body.grammar-huashu-editorial-lab .proof-ledger .proof-notes li {{ padding-top: .14rem; }}
body.grammar-huashu-editorial-lab .artifact-ledger .two-col {{ grid-template-columns: minmax(22rem, .74fr) 1.26fr; gap: 2.3vw; }}
body.grammar-huashu-editorial-lab .artifact-ledger .artifact-visual {{ height: 45vh; max-height: 47vh; }}
body.grammar-broadside-lab .cover .tags {{ max-width: 52vw; }}
body .cover-title-card .cover-art,
body .cover-title-wall .cover-art,
body .cover-poster-grid .cover-art {{ width: min(19vw, 22rem); }}
body .cover-title-card .cover-art img,
body .cover-title-wall .cover-art img,
body .cover-poster-grid .cover-art img {{ height: 24vh; }}
body .cover-title-card .metrics,
body .cover-title-wall .metrics,
body .cover-poster-grid .metrics {{ max-width: 55vw; }}
body .cover-poster-grid .tags {{ max-width: 52vw; }}
body .cover-title-card .tags {{ max-width: 52vw; }}
body .cover-title-wall .tags {{ max-width: 44vw; }}
body .slide .kicker + h1,
body .slide .kicker + h2 {{ margin-top: clamp(.72rem, 1.35vh, 1.12rem); }}
body .slide h1 + h2 {{ margin-top: clamp(1rem, 1.75vh, 1.45rem); }}
body .slide h2 + .subtitle,
body .cover h2 + .lead {{ margin-top: clamp(1.2rem, 2vh, 1.6rem); }}
body .evidence h2,
body .loop h2,
body .product h2 {{ margin-bottom: .42em; }}
body.grammar-evidence-atelier h2 {{ line-height: 1.08; margin-bottom: .36em; }}
body.grammar-catalog-atelier .metric,
body.grammar-paper-atlas .metric {{ row-gap: .9rem; }}
body.grammar-fathom-research-brief .metric strong,
body.grammar-pentagram-gridnote .metric strong {{ line-height: 1.13; }}
body.grammar-fathom-research-brief .evidence-grid aside .metric strong,
body.grammar-fathom-research-brief .matrix-grid .metric strong,
body.grammar-pentagram-gridnote .evidence-grid aside .metric strong,
body.grammar-pentagram-gridnote .matrix-grid .metric strong {{ line-height: 1.15; }}
body .slide h1,
body .slide h2,
body .slide .spine b {{ line-height: 1.12; }}
body .slide .metric strong {{ line-height: 1.14; }}
body.grammar-keynote-evidence-wall .evidence-grid aside .metric strong,
body.grammar-highsense-gallery .evidence-grid aside .metric strong,
body.grammar-jetset-theory-grid .evidence-grid aside .metric strong,
body.grammar-systems-field-manual .evidence-grid aside .metric strong,
body.grammar-lab-trace-ledger .evidence-grid aside .metric strong,
body.grammar-cobalt-research-grid .evidence-grid aside .metric strong,
body.grammar-neo-grid-lab .evidence-grid aside .metric strong,
body.grammar-broadside-lab .evidence-grid aside .metric strong,
body.grammar-stamen-data-map .evidence-grid aside .metric strong,
body.grammar-huashu-editorial-lab .evidence-grid aside .metric strong {{ line-height: 1.15; }}
body.grammar-pentagram-gridnote h1,
body.grammar-pentagram-gridnote h2 {{ line-height: 1.08; }}
body.grammar-pentagram-gridnote .proof-ledger .evidence-grid {{ grid-template-columns: minmax(9.5rem, 12vw) minmax(0, 1fr); gap: 1.4vw; max-height: 74vh; }}
body.grammar-pentagram-gridnote .proof-ledger .proof-visual {{ height: 55.2vh; min-height: 20rem; max-height: 56vh; }}
body.grammar-paper-atlas .artifact-dossier .two-col {{ grid-template-columns: minmax(22rem, .72fr) 1.28fr; gap: 3.2vw; }}
body.grammar-paper-atlas .artifact-dossier .two-col {{ max-height: 67vh; }}
body.grammar-paper-atlas .artifact-dossier .two-col > ul {{ max-height: 66vh; overflow: hidden; }}
body.grammar-paper-atlas .artifact-dossier .artifact-visual {{ height: 47vh; max-height: 49vh; }}
body.grammar-paper-atlas .dark .artifact-panel,
body.grammar-evidence-atelier .dark .artifact-panel,
body.grammar-pentagram-gridnote .dark .artifact-panel {{ background: #fff9ef; color: #1a1713; }}
body.grammar-paper-atlas .dark .artifact-panel figcaption,
body.grammar-evidence-atelier .dark .artifact-panel figcaption,
body.grammar-pentagram-gridnote .dark .artifact-panel figcaption {{ color: #4e463b; }}
body.grammar-paper-atlas .dark .artifact-panel figcaption b,
body.grammar-evidence-atelier .dark .artifact-panel figcaption b,
body.grammar-pentagram-gridnote .dark .artifact-panel figcaption b {{ color: #17120f; }}
body.grammar-vellum-research-note .cover .metrics {{ max-width: 54vw; }}
body.grammar-takram-research-system .dark .proof figcaption,
body.grammar-takram-research-system .dark .artifact-panel figcaption,
body.grammar-ia-research-archive .dark .proof figcaption,
body.grammar-ia-research-archive .dark .artifact-panel figcaption,
body.grammar-monograph-review .dark .proof figcaption,
body.grammar-monograph-review .dark .artifact-panel figcaption,
body.grammar-forest-editorial-brief .dark .proof figcaption,
body.grammar-forest-editorial-brief .dark .artifact-panel figcaption,
body.grammar-jetset-theory-grid .dark .proof figcaption,
body.grammar-jetset-theory-grid .dark .artifact-panel figcaption,
body.grammar-mono-ink-ledger .dark .proof figcaption,
body.grammar-mono-ink-ledger .dark .artifact-panel figcaption,
body.grammar-swiss-systems .dark .proof figcaption,
body.grammar-swiss-systems .dark .artifact-panel figcaption,
body.grammar-fathom-research-brief .dark .proof figcaption,
body.grammar-fathom-research-brief .dark .artifact-panel figcaption,
body.grammar-catalog-atelier .dark .proof figcaption,
body.grammar-catalog-atelier .dark .artifact-panel figcaption,
body.grammar-paper-atlas .dark .proof figcaption,
body.grammar-paper-atlas .dark .artifact-panel figcaption {{ color: #5f6872; }}
body.grammar-takram-research-system .dark .proof figcaption b,
body.grammar-takram-research-system .dark .artifact-panel figcaption b,
body.grammar-ia-research-archive .dark .proof figcaption b,
body.grammar-ia-research-archive .dark .artifact-panel figcaption b,
body.grammar-monograph-review .dark .proof figcaption b,
body.grammar-monograph-review .dark .artifact-panel figcaption b,
body.grammar-forest-editorial-brief .dark .proof figcaption b,
body.grammar-forest-editorial-brief .dark .artifact-panel figcaption b,
body.grammar-jetset-theory-grid .dark .proof figcaption b,
body.grammar-jetset-theory-grid .dark .artifact-panel figcaption b,
body.grammar-mono-ink-ledger .dark .proof figcaption b,
body.grammar-mono-ink-ledger .dark .artifact-panel figcaption b,
body.grammar-swiss-systems .dark .proof figcaption b,
body.grammar-swiss-systems .dark .artifact-panel figcaption b,
body.grammar-fathom-research-brief .dark .proof figcaption b,
body.grammar-fathom-research-brief .dark .artifact-panel figcaption b,
body.grammar-catalog-atelier .dark .proof figcaption b,
body.grammar-catalog-atelier .dark .artifact-panel figcaption b,
body.grammar-paper-atlas .dark .proof figcaption b,
body.grammar-paper-atlas .dark .artifact-panel figcaption b {{ color: #111417; }}
body.grammar-systems-field-manual .dark .proof figcaption,
body.grammar-systems-field-manual .dark .artifact-panel figcaption,
body.grammar-neo-grid-lab .dark .proof figcaption,
body.grammar-neo-grid-lab .dark .artifact-panel figcaption,
body.grammar-cobalt-research-grid .dark .proof figcaption,
body.grammar-cobalt-research-grid .dark .artifact-panel figcaption {{ color: #c9d4ca; }}
body.grammar-systems-field-manual .dark .proof figcaption b,
body.grammar-systems-field-manual .dark .artifact-panel figcaption b,
body.grammar-neo-grid-lab .dark .proof figcaption b,
body.grammar-neo-grid-lab .dark .artifact-panel figcaption b,
body.grammar-cobalt-research-grid .dark .proof figcaption b,
body.grammar-cobalt-research-grid .dark .artifact-panel figcaption b {{ color: #f6f7f1; }}
body.grammar-keynote-evidence-wall .dark .proof figcaption,
body.grammar-keynote-evidence-wall .dark .artifact-panel figcaption {{ color: #d4cec1; }}
body.grammar-keynote-evidence-wall .dark .proof figcaption b,
body.grammar-keynote-evidence-wall .dark .artifact-panel figcaption b {{ color: #f3f0e8; }}
body.grammar-swiss-systems .dark .proof figcaption,
body.grammar-swiss-systems .dark .artifact-panel figcaption {{ color: #cfd8e3; }}
body.grammar-swiss-systems .dark .proof figcaption b,
body.grammar-swiss-systems .dark .artifact-panel figcaption b {{ color: #f7f8f5; }}

/* Guardrail overrides for the template-inspired grammars: keep expressive type but never at the cost of line-box or image-slot safety. */
body.grammar-signal-intelligence-brief .slide h1,
body.grammar-signal-intelligence-brief .slide h2,
body.grammar-signal-intelligence-brief .slide .metric strong,
body.grammar-raw-grid-research .slide h1,
body.grammar-raw-grid-research .slide h2,
body.grammar-raw-grid-research .slide .metric strong,
body.grammar-stencil-field-tablet .slide h1,
body.grammar-stencil-field-tablet .slide h2,
body.grammar-stencil-field-tablet .slide .metric strong {{ line-height: 1.2; }}
body.grammar-signal-intelligence-brief .cover-source-rail h1 {{ font-size: clamp(2.2rem, 4.25vw, 4.7rem); line-height: 1.24; margin: .05em 0 .62em; }}
body.grammar-signal-intelligence-brief .cover-source-rail h2 {{ font-size: clamp(1.18rem, 1.85vw, 2.14rem); line-height: 1.42; margin: 0 0 .9rem; }}
body.grammar-signal-intelligence-brief .cover-source-rail {{ align-content: start; row-gap: .84rem; }}
body.grammar-signal-intelligence-brief .kicker,
body.grammar-raw-grid-research .kicker,
body.grammar-stencil-field-tablet .kicker {{ line-height: 1.45; margin-bottom: .9rem; }}
body.grammar-signal-intelligence-brief .slide > .kicker {{ margin-bottom: 1.55rem; }}
body.grammar-signal-intelligence-brief .cover-source-rail .lead,
body.grammar-signal-intelligence-brief .cover-source-rail p {{ font-size: .9rem; line-height: 1.46; margin: .42rem 0; }}
body.grammar-signal-intelligence-brief .cover-source-rail .metrics {{ max-width: 54vw; margin-top: 1.4vh; padding-top: .72rem; }}
body.grammar-signal-intelligence-brief .cover-source-rail .metric strong {{ font-size: clamp(.98rem, 1.55vw, 1.82rem); }}
body.grammar-signal-intelligence-brief .cover-source-rail .metric span {{ font-size: .62rem; line-height: 1.24; }}
body.grammar-raw-grid-research .cover-poster-grid h1,
body.grammar-stencil-field-tablet .cover-poster-grid h1 {{ max-width: 64vw; font-size: clamp(2.55rem, 5.6vw, 6.3rem); line-height: 1.14; }}
body.grammar-raw-grid-research .cover-poster-grid h2,
body.grammar-stencil-field-tablet .cover-poster-grid h2 {{ max-width: 60vw; font-size: clamp(1.32rem, 2.25vw, 2.6rem); line-height: 1.56; margin-bottom: 1.05rem; }}
body.grammar-raw-grid-research .cover-poster-grid .metrics,
body.grammar-stencil-field-tablet .cover-poster-grid .metrics {{ max-width: 54vw; margin-top: 1.8vh; }}
body.grammar-raw-grid-research .cover-poster-grid .metric,
body.grammar-stencil-field-tablet .cover-poster-grid .metric {{ padding: .55rem .62rem; }}
body.grammar-raw-grid-research .cover-poster-grid .metric strong,
body.grammar-stencil-field-tablet .cover-poster-grid .metric strong {{ font-size: clamp(1rem, 1.8vw, 2rem); line-height: 1.18; }}
body.grammar-raw-grid-research h2 {{ font-size: clamp(1.48rem, 2.35vw, 2.78rem); max-width: 82vw; line-height: 1.32; margin-bottom: .42em; }}
body.grammar-stencil-field-tablet h2 {{ font-size: clamp(1.16rem, 1.74vw, 2.04rem); max-width: 82vw; line-height: 1.82; margin-bottom: .8em; }}
body.grammar-signal-intelligence-brief h2 {{ font-size: clamp(1.26rem, 1.9vw, 2.22rem); max-width: 82vw; line-height: 1.58; margin-bottom: .72em; }}
body.grammar-raw-grid-research .slide h2 + .subtitle,
body.grammar-stencil-field-tablet .slide h2 + .subtitle,
body.grammar-signal-intelligence-brief .slide h2 + .subtitle {{ margin-top: 1.18rem; }}
body.grammar-raw-grid-research .proof-notes,
body.grammar-raw-grid-research .artifact-notes,
body.grammar-stencil-field-tablet .proof-notes,
body.grammar-stencil-field-tablet .artifact-notes,
body.grammar-signal-intelligence-brief .proof-notes,
body.grammar-signal-intelligence-brief .artifact-notes {{ display: none; }}
body.grammar-raw-grid-research .artifact-ledger footer,
body.grammar-raw-grid-research .artifact-showcase footer,
body.grammar-raw-grid-research .content-field-manual footer,
body.grammar-stencil-field-tablet .artifact-showcase footer,
body.grammar-stencil-field-tablet .content-field-manual footer,
body.grammar-signal-intelligence-brief .artifact-marginalia footer,
body.grammar-signal-intelligence-brief .content-marginalia footer {{ display: none; }}
body.grammar-raw-grid-research .artifact-ledger .two-col,
body.grammar-stencil-field-tablet .artifact-showcase .two-col,
body.grammar-signal-intelligence-brief .artifact-marginalia .two-col {{ grid-template-columns: minmax(15rem, .52fr) 1.48fr; gap: 2vw; max-height: 70vh; }}
body.grammar-raw-grid-research .artifact-ledger .two-col > ul,
body.grammar-stencil-field-tablet .artifact-showcase .two-col > ul,
body.grammar-signal-intelligence-brief .artifact-marginalia .two-col > ul {{ max-height: 68vh; overflow: hidden; }}
body.grammar-raw-grid-research .artifact-ledger .artifact-visual,
body.grammar-stencil-field-tablet .artifact-showcase .artifact-visual,
body.grammar-signal-intelligence-brief .artifact-marginalia .artifact-visual {{ height: 53vh; min-height: 21rem; max-height: 54vh; }}
body.grammar-raw-grid-research .matrix-grid .metrics,
body.grammar-stencil-field-tablet .matrix-grid .metrics,
body.grammar-signal-intelligence-brief .matrix-grid .metrics {{ display: block; max-width: 100%; box-shadow: none; gap: 0; overflow: hidden; }}
body.grammar-raw-grid-research .matrix-grid .metric,
body.grammar-stencil-field-tablet .matrix-grid .metric,
body.grammar-signal-intelligence-brief .matrix-grid .metric {{ display: block; padding: .48rem .56rem; border-right: 0; border-bottom: 1px solid currentColor; }}
body.grammar-raw-grid-research .matrix-grid .metric strong,
body.grammar-stencil-field-tablet .matrix-grid .metric strong,
body.grammar-signal-intelligence-brief .matrix-grid .metric strong,
body.grammar-raw-grid-research .evidence-grid aside .metric strong,
body.grammar-stencil-field-tablet .evidence-grid aside .metric strong,
body.grammar-signal-intelligence-brief .evidence-grid aside .metric strong {{ display: block; font-size: clamp(.82rem, 1.12vw, 1.32rem); line-height: 1.2; }}
body.grammar-raw-grid-research .matrix-grid .metric span,
body.grammar-stencil-field-tablet .matrix-grid .metric span,
body.grammar-signal-intelligence-brief .matrix-grid .metric span,
body.grammar-raw-grid-research .evidence-grid aside .metric span,
body.grammar-stencil-field-tablet .evidence-grid aside .metric span,
body.grammar-signal-intelligence-brief .evidence-grid aside .metric span {{ display: block; margin-top: .16rem; font-size: .58rem; line-height: 1.22; }}
body.grammar-raw-grid-research .evidence-grid aside .metrics,
body.grammar-stencil-field-tablet .evidence-grid aside .metrics,
body.grammar-signal-intelligence-brief .evidence-grid aside .metrics {{ display: grid; grid-template-columns: 1fr; gap: .78rem; padding-top: .65rem; overflow: hidden; }}
body.grammar-raw-grid-research .proof-ledger .evidence-grid,
body.grammar-stencil-field-tablet .proof-ledger .evidence-grid {{ grid-template-columns: minmax(12rem, 16vw) minmax(0, 1fr); gap: 1.75vw; max-height: 72vh; }}
body.grammar-signal-intelligence-brief .proof-atlas-spread .evidence-grid {{ grid-template-columns: minmax(0, 1fr) minmax(12rem, 16vw); gap: 1.8vw; max-height: 72vh; }}
body.grammar-raw-grid-research .proof-ledger .proof figcaption,
body.grammar-stencil-field-tablet .proof-ledger .proof figcaption,
body.grammar-signal-intelligence-brief .proof-atlas-spread .proof figcaption {{ margin-top: 1rem; font-size: .68rem; line-height: 1.22; }}
body.grammar-raw-grid-research .content-field-manual .two-col,
body.grammar-stencil-field-tablet .content-field-manual .two-col,
body.grammar-signal-intelligence-brief .content-marginalia .two-col {{ max-height: 66vh; }}
body.grammar-raw-grid-research .content-field-manual li,
body.grammar-stencil-field-tablet .content-field-manual li,
body.grammar-signal-intelligence-brief .content-marginalia li {{ font-size: 1rem; line-height: 1.42; margin: .7rem 0; }}
body.grammar-stencil-field-tablet .content-field-manual li,
body.grammar-signal-intelligence-brief .content-marginalia li {{ font-size: 1.07rem; line-height: 1.46; }}
body.grammar-raw-grid-research .content-field-manual .label-board b,
body.grammar-stencil-field-tablet .content-field-manual .label-board b,
body.grammar-signal-intelligence-brief .content-marginalia .label-board b {{ font-size: 1.22rem; line-height: 1.28; }}
body.grammar-stencil-field-tablet .content-field-manual .label-board b,
body.grammar-signal-intelligence-brief .content-marginalia .label-board b {{ font-size: 1.3rem; line-height: 1.3; }}
body.grammar-raw-grid-research .content-field-manual .label-board div,
body.grammar-stencil-field-tablet .content-field-manual .label-board div,
body.grammar-signal-intelligence-brief .content-marginalia .label-board div {{ min-height: 5.25rem; }}
body.grammar-raw-grid-research .close.content-field-manual li,
body.grammar-stencil-field-tablet .close.content-field-manual li,
body.grammar-signal-intelligence-brief .close.content-marginalia li {{ font-size: 1.16rem; line-height: 1.46; }}
body.grammar-raw-grid-research .close.content-field-manual .subtitle,
body.grammar-stencil-field-tablet .close.content-field-manual .subtitle,
body.grammar-signal-intelligence-brief .close.content-marginalia .subtitle {{ font-size: 1.32rem; line-height: 1.42; }}
body.grammar-raw-grid-research .close.content-field-manual .label-board b,
body.grammar-stencil-field-tablet .close.content-field-manual .label-board b,
body.grammar-signal-intelligence-brief .close.content-marginalia .label-board b {{ font-size: clamp(1.42rem, 2vw, 2.22rem); line-height: 1.24; }}
body.grammar-raw-grid-research .close.content-field-manual .label-board span,
body.grammar-stencil-field-tablet .close.content-field-manual .label-board span,
body.grammar-signal-intelligence-brief .close.content-marginalia .label-board span {{ font-size: .72rem; line-height: 1.25; }}
body.grammar-raw-grid-research .proof figcaption,
body.grammar-raw-grid-research .artifact-panel figcaption,
body.grammar-stencil-field-tablet .proof figcaption,
body.grammar-stencil-field-tablet .artifact-panel figcaption {{ color: #202020; background: transparent; }}
body.grammar-raw-grid-research .proof figcaption b,
body.grammar-raw-grid-research .artifact-panel figcaption b,
body.grammar-stencil-field-tablet .proof figcaption b,
body.grammar-stencil-field-tablet .artifact-panel figcaption b {{ color: #0a0a0a; }}
body.grammar-raw-grid-research .proof figcaption span,
body.grammar-raw-grid-research .artifact-panel figcaption span,
body.grammar-stencil-field-tablet .proof figcaption span,
body.grammar-stencil-field-tablet .artifact-panel figcaption span {{ color: #333; }}
body.grammar-signal-intelligence-brief .proof figcaption,
body.grammar-signal-intelligence-brief .artifact-panel figcaption {{ color: #3d4657; background: #fff; padding: .28rem .34rem; }}
body.grammar-signal-intelligence-brief .proof figcaption b,
body.grammar-signal-intelligence-brief .artifact-panel figcaption b {{ color: #1a2030; }}
body.grammar-signal-intelligence-brief .proof figcaption span,
body.grammar-signal-intelligence-brief .artifact-panel figcaption span {{ color: #2f3949; }}
body.grammar-maison-research-catalog .slide {{ padding: 4.7vh 5.1vw 6.4vh; background: var(--paper); color: var(--ink); --cover-art-height: 34vh; --proof-visual-height: 58vh; --artifact-visual-height: 56vh; }}
body.grammar-maison-research-catalog .dark {{ background: #15120e; color: #f7f4ec; }}
body.grammar-maison-research-catalog .dark::before {{ opacity: .045; background-size: 7vw 10vh; }}
body.grammar-maison-research-catalog h1,
body.grammar-maison-research-catalog h2 {{ font-family: "Didot", "Bodoni 72", "Iowan Old Style", Georgia, serif; font-weight: 600; line-height: 1.13; color: currentColor; }}
body.grammar-maison-research-catalog h1 {{ font-size: 5.45rem; max-width: 68vw; }}
body.grammar-maison-research-catalog h2 {{ font-size: 2.96rem; max-width: 80vw; margin: .62em 0 .58em; }}
body.grammar-maison-research-catalog .cover-title-wall h1 {{ margin-top: .82rem; margin-bottom: .42em; }}
body.grammar-maison-research-catalog .kicker {{ display: block; color: #9f2a25; letter-spacing: .16em; font-size: .66rem; margin-bottom: 1.65rem; }}
body.grammar-maison-research-catalog .lead,
body.grammar-maison-research-catalog .subtitle {{ line-height: 1.42; margin-top: 1.05rem; }}
body.grammar-maison-research-catalog .rule {{ width: 16vw; height: 2px; margin-bottom: 5.4vh; }}
body.grammar-maison-research-catalog .cover-title-wall .cover-art {{ right: 5.1vw; bottom: 7.4vh; width: min(28vw, 32rem); padding: .42rem; border-color: #d5c9b8; background: #fffdf8; box-shadow: none; }}
body.grammar-maison-research-catalog .cover-title-wall .cover-art img {{ height: 34vh; object-fit: contain; }}
body.grammar-maison-research-catalog .proof-gallery-split .evidence-grid {{ grid-template-columns: minmax(10rem, 14vw) minmax(0, 1fr); gap: 1.9vw; max-height: 73vh; }}
body.grammar-maison-research-catalog .proof-gallery-split .proof {{ padding: .48rem; border: 1px solid #d5c9b8; background: #fffdf8; box-shadow: none; }}
body.grammar-maison-research-catalog .proof-gallery-split .proof-visual {{ height: 59vh; max-height: 60vh; }}
body.grammar-maison-research-catalog .artifact-showcase .two-col {{ grid-template-columns: minmax(14rem, 20vw) minmax(0, 1fr); gap: 2.4vw; max-height: 71vh; }}
body.grammar-maison-research-catalog .artifact-showcase .artifact-visual {{ height: 56vh; max-height: 57vh; }}
body.grammar-maison-research-catalog .artifact-panel,
body.grammar-maison-research-catalog .label-board div {{ background: #fffdf8; border-color: #d5c9b8; border-radius: 0; box-shadow: none; color: #15120e; }}
body.grammar-maison-research-catalog .proof figcaption,
body.grammar-maison-research-catalog .artifact-panel figcaption {{ margin-top: 1.35rem; color: #4b4338; }}
body.grammar-maison-research-catalog .proof figcaption b,
body.grammar-maison-research-catalog .artifact-panel figcaption b {{ color: #15120e; }}
body.grammar-maison-research-catalog .label-board {{ grid-template-columns: 1.08fr .92fr; }}
body.grammar-maison-research-catalog .label-board div:nth-child(1) {{ grid-row: span 2; min-height: 10.8rem; }}
body.grammar-maison-research-catalog .content-bento .label-board b {{ font-size: 1.42rem; line-height: 1.24; }}
body.grammar-maison-research-catalog .content-bento .label-board div {{ min-height: 6.45rem; }}
body.grammar-maison-research-catalog .content-bento li {{ font-size: 1.08rem; line-height: 1.48; margin: .96rem 0; }}
body.grammar-maison-research-catalog .close.content-bento .label-board div {{ min-height: 7.85rem; padding: 1.08rem; }}
body.grammar-maison-research-catalog .close.content-bento h2 {{ font-size: 3.12rem; max-width: 84vw; }}
body.grammar-maison-research-catalog .close.content-bento .subtitle {{ font-size: 1.28rem; line-height: 1.45; max-width: 78vw; }}
body.grammar-maison-research-catalog .close.content-bento .label-board b {{ font-size: 1.58rem; line-height: 1.25; }}
body.grammar-maison-research-catalog .close.content-bento .label-board span {{ font-size: .82rem; line-height: 1.24; }}
body.grammar-maison-research-catalog .close.content-bento li {{ font-size: 1.2rem; line-height: 1.5; margin: 1.08rem 0; }}
body.grammar-maison-research-catalog .proof-notes,
body.grammar-maison-research-catalog .artifact-notes {{ display: none; }}
body.grammar-folio-swiss-noir .slide {{ padding: 4.1vh 4.2vw 5.9vh; background: var(--paper); color: var(--ink); --cover-art-height: 25vh; --proof-visual-height: 56vh; --artifact-visual-height: 46vh; }}
body.grammar-folio-swiss-noir .dark {{ background: #0b0b0b; color: #f7f5ed; }}
body.grammar-folio-swiss-noir .dark::before {{ display: none; }}
body.grammar-folio-swiss-noir h1,
body.grammar-folio-swiss-noir h2,
body.grammar-folio-swiss-noir .metric strong,
body.grammar-folio-swiss-noir .label-board b {{ font-family: "Helvetica Neue", Arial, sans-serif; font-weight: 820; line-height: 1.14; color: currentColor; }}
body.grammar-folio-swiss-noir .metric strong {{ line-height: 1.16; }}
body.grammar-folio-swiss-noir h1 {{ font-size: 5.25rem; max-width: 82vw; margin-bottom: .34em; }}
body.grammar-folio-swiss-noir h2 {{ font-size: 3.12rem; max-width: 82vw; margin: .44em 0 .4em; }}
body.grammar-folio-swiss-noir .cover-poster-grid h1 {{ max-width: 88vw; letter-spacing: 0; }}
body.grammar-folio-swiss-noir .kicker {{ display: inline-block; background: #0b0b0b; color: #f7f5ed; padding: .18rem .52rem; letter-spacing: .04em; margin-bottom: .92rem; }}
body.grammar-folio-swiss-noir .dark .kicker {{ background: #e2b84b; color: #0b0b0b; }}
body.grammar-folio-swiss-noir .rule {{ height: 3px; background: currentColor; margin-bottom: 4.8vh; }}
body.grammar-folio-swiss-noir .proof-ledger .evidence-grid {{ grid-template-columns: minmax(10rem, 13vw) minmax(0, 1fr); gap: 1.6vw; max-height: 73vh; }}
body.grammar-folio-swiss-noir .proof-ledger .proof {{ border: 3px solid currentColor; background: #fff; padding: .45rem; box-shadow: 8px 8px 0 currentColor; }}
body.grammar-folio-swiss-noir .proof-ledger .proof-visual {{ height: 57vh; max-height: 58vh; }}
body.grammar-folio-swiss-noir .artifact-ledger .two-col {{ grid-template-columns: minmax(13rem, .44fr) 1.56fr; gap: 1.6vw; max-height: 71vh; }}
body.grammar-folio-swiss-noir .artifact-ledger .artifact-visual {{ height: 57vh; max-height: 58vh; }}
body.grammar-folio-swiss-noir .artifact-panel,
body.grammar-folio-swiss-noir .label-board div {{ background: #fff; border: 3px solid currentColor; border-radius: 0; box-shadow: none; color: #0b0b0b; }}
body.grammar-folio-swiss-noir .proof figcaption,
body.grammar-folio-swiss-noir .artifact-panel figcaption {{ margin-top: 1.35rem; color: #333; }}
body.grammar-folio-swiss-noir .proof figcaption b,
body.grammar-folio-swiss-noir .artifact-panel figcaption b {{ color: #0b0b0b; }}
body.grammar-folio-swiss-noir .content-field-manual .label-board {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
body.grammar-folio-swiss-noir .content-field-manual .label-board div {{ min-height: 6.55rem; padding: .88rem; }}
body.grammar-folio-swiss-noir .content-field-manual .label-board b {{ font-size: 1.26rem; line-height: 1.2; }}
body.grammar-folio-swiss-noir .lead,
body.grammar-folio-swiss-noir .subtitle {{ line-height: 1.42; margin-top: .78rem; }}
body.grammar-folio-swiss-noir .content-field-manual li {{ font-size: 1.04rem; line-height: 1.44; margin: .9rem 0; }}
body.grammar-folio-swiss-noir .close.content-field-manual .label-board div {{ min-height: 8.2rem; padding: 1.05rem; }}
body.grammar-folio-swiss-noir .close.content-field-manual h2 {{ font-size: 3.28rem; max-width: 86vw; }}
body.grammar-folio-swiss-noir .close.content-field-manual .subtitle {{ font-size: 1.3rem; line-height: 1.45; max-width: 80vw; }}
body.grammar-folio-swiss-noir .close.content-field-manual .label-board b {{ font-size: 1.56rem; line-height: 1.2; }}
body.grammar-folio-swiss-noir .close.content-field-manual .label-board span {{ font-size: .82rem; line-height: 1.24; }}
body.grammar-folio-swiss-noir .close.content-field-manual li {{ font-size: 1.18rem; line-height: 1.48; margin: 1.05rem 0; }}
body.grammar-folio-swiss-noir .proof-notes,
body.grammar-folio-swiss-noir .artifact-notes {{ display: none; }}
body.grammar-chromatic-research-map .slide {{ padding: 5vh 5.3vw 6.8vh; background: var(--paper); color: var(--ink); --cover-art-height: 29vh; --proof-visual-height: 57vh; --artifact-visual-height: 52vh; }}
body.grammar-chromatic-research-map .light {{ background-image: linear-gradient(90deg, rgba(20,35,28,.055) 0 1px, transparent 1px 100%), linear-gradient(rgba(20,35,28,.035) 0 1px, transparent 1px 100%); background-size: 8vw 100%, 100% 9vh; }}
body.grammar-chromatic-research-map .dark {{ background: #10251d; color: #eef7f1; }}
body.grammar-chromatic-research-map .dark::before {{ opacity: .08; background-size: 8vw 9vh; }}
body.grammar-chromatic-research-map h1,
body.grammar-chromatic-research-map h2 {{ font-family: "Avenir Next", "Helvetica Neue", Arial, sans-serif; font-weight: 760; line-height: 1.14; color: currentColor; }}
body.grammar-chromatic-research-map h1 {{ font-size: 4.55rem; max-width: 70vw; margin-bottom: .34em; }}
body.grammar-chromatic-research-map h2 {{ font-size: 2.8rem; max-width: 80vw; margin: .62em 0 .56em; }}
body.grammar-chromatic-research-map .cover-title-wall h1 {{ margin-top: 1rem; margin-bottom: .5em; }}
body.grammar-chromatic-research-map .kicker {{ display: block; color: #e0442e; letter-spacing: .08em; margin-bottom: 1.95rem; }}
body.grammar-chromatic-research-map .lead,
body.grammar-chromatic-research-map .subtitle {{ line-height: 1.42; margin-top: .78rem; }}
body.grammar-chromatic-research-map .cover-title-wall .cover-art {{ width: min(25vw, 30rem); bottom: 7vh; right: 5.4vw; border-color: #b9d4c4; background: #fbfffc; box-shadow: none; }}
body.grammar-chromatic-research-map .proof-atlas-spread .evidence-grid {{ grid-template-columns: minmax(0, 1fr) minmax(11rem, 15vw); gap: 1.8vw; max-height: 73vh; }}
body.grammar-chromatic-research-map .proof-atlas-spread .proof {{ padding: .52rem; border-color: #b9d4c4; background: #fbfffc; box-shadow: none; }}
body.grammar-chromatic-research-map .proof-atlas-spread .proof-visual {{ height: 57vh; max-height: 58vh; }}
body.grammar-chromatic-research-map .proof-atlas-spread .proof figcaption {{ margin-top: 1.35rem; }}
body.grammar-chromatic-research-map .artifact-marginalia .two-col {{ grid-template-columns: minmax(13rem, .44fr) 1.56fr; gap: 1.8vw; max-height: 71vh; }}
body.grammar-chromatic-research-map .artifact-marginalia .artifact-visual {{ height: 57vh; max-height: 58vh; }}
body.grammar-chromatic-research-map .artifact-panel,
body.grammar-chromatic-research-map .label-board div {{ background: #fbfffc; border-color: #b9d4c4; border-radius: 0; box-shadow: none; color: #14231c; }}
body.grammar-chromatic-research-map .artifact-panel figcaption {{ margin-top: 1.35rem; }}
body.grammar-chromatic-research-map .label-board {{ grid-template-columns: 1fr 1fr; }}
body.grammar-chromatic-research-map .label-board div {{ min-height: 6.2rem; padding: .95rem; }}
body.grammar-chromatic-research-map .label-board b {{ font-size: 1.24rem; line-height: 1.25; }}
body.grammar-chromatic-research-map .label-board span,
body.grammar-chromatic-research-map .metric strong {{ color: #e0442e; }}
body .proof figcaption,
body .artifact-panel figcaption,
body .cover-art figcaption {{ margin-top: 1.35rem; }}
body.grammar-chromatic-research-map .proof figcaption,
body.grammar-chromatic-research-map .artifact-panel figcaption {{ margin-top: 1.65rem; color: #33483d; }}
body.grammar-chromatic-research-map .proof figcaption b,
body.grammar-chromatic-research-map .artifact-panel figcaption b {{ color: #14231c; }}
body.grammar-chromatic-research-map .proof-notes,
body.grammar-chromatic-research-map .artifact-notes {{ display: none; }}

/* Final slide-safety overrides.
   These sit after every grammar so expressive templates cannot reintroduce
   title/kicker collisions, tight multi-line headings, or cramped figure
   captions. The audit treats these as export blockers. */
body .slide .kicker {{
  display: block;
  width: fit-content;
  line-height: 1.45;
  margin-bottom: clamp(2.4rem, 4vh, 3.2rem);
}}
body .slide .kicker + h1,
body .slide .kicker + h2 {{
  margin-top: 0;
}}
body .slide h1,
body .slide h2,
body .slide .spine b,
body .proof-showcase h2,
body.grammar-pentagram-gridnote h1,
body.grammar-pentagram-gridnote h2 {{
  line-height: 1.16;
}}
body .proof figcaption,
body .artifact-panel figcaption,
body .cover-art figcaption,
body .proof-showcase .proof figcaption,
body .proof-atlas-spread .proof figcaption,
body .proof-ledger .proof figcaption,
body .proof-marginalia .proof figcaption,
body .proof-gallery-split .proof figcaption,
body .artifact-dossier .artifact-panel figcaption,
body .artifact-showcase .artifact-panel figcaption,
body .artifact-ledger .artifact-panel figcaption,
body .artifact-marginalia .artifact-panel figcaption,
body.grammar-huashu-editorial-lab .proof-ledger .proof figcaption {{
  margin-top: 1.65rem;
}}
body .artifact-ledger .two-col {{
  grid-template-columns: minmax(15rem, .54fr) minmax(0, 1.46fr);
  gap: 2.1vw;
  max-height: 70vh;
}}
body .artifact-ledger .two-col > ul {{
  max-height: 68vh;
  overflow: hidden;
}}
body .artifact-ledger .artifact-visual {{
  height: 54vh;
  min-height: 21rem;
  max-height: 55vh;
}}
body .artifact-showcase .two-col {{
  grid-template-columns: minmax(11rem, 15vw) minmax(0, 1fr);
  gap: 2.4vw;
}}
body .artifact-showcase .artifact-visual {{
  height: 58vh;
  min-height: 22rem;
  max-height: 59vh;
}}
body .proof-gallery-split .evidence-grid {{
  grid-template-columns: minmax(10rem, 14vw) minmax(0, 1fr);
  gap: 4vw;
}}
@media print {{ .slide {{ width: 13.333in; height: 7.5in; }} }}
</style>
</head>
<body class="grammar-{grammar}" data-visual-grammar="{grammar}">
{slides}
<script>
(() => {{
  const params = new URLSearchParams(window.location.search);
  const target = Number(params.get("slide"));
  const ready = (fn) => {{
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fn);
    else fn();
  }};
  const keepOnly = () => {{
    if (!target) return;
    document.documentElement.classList.add("single-slide");
    document.querySelectorAll(".slide").forEach((slide, index) => {{
      if (index + 1 !== target) slide.remove();
    }});
  }};
  const waitForImages = () => {{
    const images = Array.from(document.images);
    if (!images.length) return Promise.resolve();
    const waits = images.map((img) => {{
      if (img.complete && img.naturalWidth) return Promise.resolve();
      return new Promise((resolve) => {{
        const done = () => {{
          if (img.decode) img.decode().catch(() => undefined).finally(resolve);
          else resolve();
        }};
        img.addEventListener("load", done, {{ once: true }});
        img.addEventListener("error", resolve, {{ once: true }});
      }});
    }});
    return Promise.race([
      Promise.all(waits),
      new Promise((resolve) => window.setTimeout(resolve, 1500))
    ]);
  }};
  const sourceBoxFor = (img, slotRect = null) => {{
    const slot = slotRect || (img.parentElement ? img.parentElement.getBoundingClientRect() : img.getBoundingClientRect());
    const style = window.getComputedStyle(img);
    const fit = (style.objectFit || "fill").trim() || "fill";
    const supportedFit = ["contain", "cover", "scale-down"].includes(fit);
    const naturalRatio = img.naturalWidth && img.naturalHeight ? img.naturalWidth / img.naturalHeight : 1;
    const slotRatio = slot.height ? slot.width / slot.height : naturalRatio;
    let width = slot.width;
    let height = slot.height;
    if (fit === "cover") {{
      if (naturalRatio > slotRatio) {{
        height = slot.height;
        width = slot.height * naturalRatio;
      }} else {{
        width = slot.width;
        height = slot.width / naturalRatio;
      }}
    }} else if (naturalRatio > slotRatio) {{
      height = slot.width / naturalRatio;
    }} else {{
      width = slot.height * naturalRatio;
    }}
    const parts = String(style.objectPosition || "50% 50%").trim().split(/\s+/);
    const positionFor = (part, axis) => {{
      const value = (part || "50%").toLowerCase();
      if (value === "left" || value === "top") return 0;
      if (value === "right" || value === "bottom") return 1;
      if (value === "center") return .5;
      if (value.endsWith("%")) return Math.max(0, Math.min(1, Number.parseFloat(value) / 100));
      return .5;
    }};
    const posX = positionFor(parts[0], "x");
    const posY = positionFor(parts[1] || parts[0], "y");
    const left = slot.left + (slot.width - width) * posX;
    const top = slot.top + (slot.height - height) * posY;
    return {{ left, top, right: left + width, bottom: top + height, width, height, objectFit: fit, unsupported: !supportedFit }};
  }};
  const intersectBox = (a, b) => {{
    const left = Math.max(a.left, b.left);
    const top = Math.max(a.top, b.top);
    const right = Math.min(a.right, b.right);
    const bottom = Math.min(a.bottom, b.bottom);
    const width = Math.max(0, right - left);
    const height = Math.max(0, bottom - top);
    return {{ left, top, right, bottom, width, height }};
  }};
  const positionPins = () => {{
    document.querySelectorAll(".proof-visual,.artifact-visual").forEach((host) => {{
      const img = host.querySelector("img");
      if (!img || !img.naturalWidth || !img.naturalHeight) return;
      const hostRect = host.getBoundingClientRect();
      const source = sourceBoxFor(img, hostRect);
      host.querySelectorAll(".pin").forEach((pin) => {{
        const x = Number.parseFloat(pin.dataset.x || "0.5");
        const y = Number.parseFloat(pin.dataset.y || "0.5");
        pin.style.left = `${{source.left - hostRect.left + x * source.width}}px`;
        pin.style.top = `${{source.top - hostRect.top + y * source.height}}px`;
      }});
    }});
  }};
    const boxLabel = (el) => {{
      if (el.className) return `${{el.tagName.toLowerCase()}}.${{String(el.className).trim().replace(/\\s+/g, ".")}}`;
      const parent = el.parentElement;
      if (parent && parent.className) return `${{el.tagName.toLowerCase()}}@.${{String(parent.className).trim().replace(/\\s+/g, ".")}}`;
      return el.tagName.toLowerCase();
    }};
    const nearestClipBox = (el) => {{
      let current = el.parentElement;
      while (current && current !== document.body) {{
        const style = window.getComputedStyle(current);
        const overflow = `${{style.overflow}} ${{style.overflowX}} ${{style.overflowY}}`;
        if (/hidden|clip|auto|scroll/.test(overflow)) return current.getBoundingClientRect();
        current = current.parentElement;
      }}
      return null;
    }};
    const genericImageContext = (text) => {{
      const value = (text || "").trim().toLowerCase();
      if (!value) return true;
      if (/^(https?:\\/\\/|doi:|arxiv:)/i.test(value)) return false;
      if (!/\\s/.test(value) && /\\.(png|jpe?g|webp|gif|pdf|html?)$/i.test(value)) return true;
      return [
        "image", "screenshot", "figure", "chart", "proof", "source",
        "source artifact", "source surface", "homepage", "project page",
        "artifact", "fixture"
      ].includes(value);
    }};
    const parseColor = (value) => {{
      const match = String(value || "").match(/rgba?\\(([^)]+)\\)/);
      if (!match) return null;
      const parts = match[1].split(",").map((part) => Number.parseFloat(part.trim()));
      if (parts.length < 3 || parts.some((part) => Number.isNaN(part))) return null;
      return {{ r: parts[0], g: parts[1], b: parts[2], a: parts.length >= 4 && !Number.isNaN(parts[3]) ? parts[3] : 1 }};
    }};
    const compositeColor = (top, bottom) => {{
      const alpha = Math.max(0, Math.min(1, top.a));
      const under = bottom || {{ r: 255, g: 255, b: 255, a: 1 }};
      return {{
        r: top.r * alpha + under.r * (1 - alpha),
        g: top.g * alpha + under.g * (1 - alpha),
        b: top.b * alpha + under.b * (1 - alpha),
        a: alpha + under.a * (1 - alpha),
      }};
    }};
    const effectiveBackgroundColor = (el) => {{
      const stack = [];
      let current = el;
      while (current && current.nodeType === 1) {{
        stack.unshift(current);
        current = current.parentElement;
      }}
      let color = {{ r: 255, g: 255, b: 255, a: 1 }};
      stack.forEach((node) => {{
        const bg = parseColor(window.getComputedStyle(node).backgroundColor);
        if (bg && bg.a > 0) color = compositeColor(bg, color);
      }});
      return color;
    }};
    const relLum = (rgb) => {{
      const [r, g, b] = [rgb.r, rgb.g, rgb.b].map((channel) => {{
        const value = channel / 255;
        return value <= 0.03928 ? value / 12.92 : Math.pow((value + 0.055) / 1.055, 2.4);
      }});
      return 0.2126 * r + 0.7152 * g + 0.0722 * b;
    }};
    const contrastRatio = (fg, bg) => {{
      let foreground = parseColor(fg);
      let background = typeof bg === "string" ? parseColor(bg) : bg;
      if (!foreground || !background) return null;
      if (foreground.a < 1) foreground = compositeColor(foreground, background);
      const a = relLum(foreground);
      const b = relLum(background);
      const lighter = Math.max(a, b);
      const darker = Math.min(a, b);
      return (lighter + 0.05) / (darker + 0.05);
    }};
  const runLayoutAudit = () => {{
    if (params.get("audit") !== "1") return;
    const slide = document.querySelector(".slide");
    const issues = [];
    const usefulBoxes = [];
    const vw = Number(params.get("expected_width")) || window.innerWidth;
    const vh = Number(params.get("expected_height")) || window.innerHeight;
    const TEXT_CLEARANCE_PX = 20;
    const TEXT_BLOCK_CLEARANCE_PX = 18;
    const TEXT_BLOCK_SIDE_CLEARANCE_PX = 26;
    const IMAGE_TEXT_OVERLAP_MIN_AREA_PX = 16;
    const IMAGE_CLEARANCE_PX = 36;
    const IMAGE_SIDE_CLEARANCE_PX = 44;
    const FIGURE_CAPTION_CLEARANCE_PX = 18;
    const TEXT_LINE_HEIGHT_SAFE_RATIO = 1.12;
    const SUPPORT_TEXT_CONTRAST_MIN = 4.5;
    const TITLE_LINE_WARN = 3;
    const TITLE_LINE_MAX = 4;
    const COVER_TITLE_LINE_MAX = 5;
    const SUBTITLE_LINE_WARN = 5;
    const SUBTITLE_LINE_MAX = 7;
    const selectors = [
      ".slide > *",
      ".cover-source-rail:not(.slide)", ".cover-title-wall:not(.slide)", ".cover-poster-grid:not(.slide)", ".cover-title-card:not(.slide)",
      ".proof-showcase:not(.slide)", ".proof-atlas-spread:not(.slide)", ".proof-stage:not(.slide)", ".proof-dossier:not(.slide)", ".proof-ledger:not(.slide)", ".proof-marginalia:not(.slide)", ".proof-gallery-split:not(.slide)",
      ".artifact-showcase:not(.slide)", ".artifact-dossier:not(.slide)", ".artifact-rail:not(.slide)", ".artifact-marginalia:not(.slide)", ".artifact-ledger:not(.slide)",
      ".content-label-board:not(.slide)", ".content-bento:not(.slide)", ".content-marginalia:not(.slide)", ".content-field-manual:not(.slide)", ".content-workbench-index:not(.slide)", ".metrics-led:not(.slide)", ".metrics-ledger:not(.slide)", ".text-two-col:not(.slide)", ".matrix-ledger:not(.slide)", ".matrix-map:not(.slide)",
      "h1", "h2", "p", ".kicker", ".lead", ".subtitle", ".tags", ".tags span",
      ".cover-art", ".cover-art figcaption", ".proof", ".proof-visual", ".proof figcaption",
      ".artifact-panel", ".artifact-visual", ".artifact-panel figcaption", ".label-board",
      ".label-board span",
      ".evidence-grid > aside", ".evidence-grid aside > ul", ".evidence-grid aside > .metrics",
      ".two-col > ul", ".two-col > .metrics", ".two-col > .label-board", ".two-col > .artifact-panel",
      ".spine", ".spine b", ".case-row", ".case-row p",
      ".matrix-grid > .metrics", ".metrics", ".metric", ".matrix-grid table", "td", "th",
      ".proof-notes", ".proof-notes li", ".proof-notes span",
      ".artifact-notes", ".artifact-notes li", ".artifact-notes span", ".pin"
    ];
    const textSelectors = [
      "h1", "h2", "p", ".kicker", ".lead", ".subtitle", ".tags span", "li", "td", "th", ".label-board b", ".label-board span", ".spine b", ".case-row p",
      ".metric strong", ".metric span", "figcaption", "figcaption b", "figcaption span",
      ".proof-notes li", ".proof-notes span", ".artifact-notes li", ".artifact-notes span", ".pin",
      "footer"
    ];
    const containerSelectors = [
      ".cover-source-rail:not(.slide)", ".cover-title-wall:not(.slide)", ".cover-poster-grid:not(.slide)", ".cover-title-card:not(.slide)",
      ".proof-showcase:not(.slide)", ".proof-atlas-spread:not(.slide)", ".proof-stage:not(.slide)", ".proof-dossier:not(.slide)", ".proof-ledger:not(.slide)", ".proof-marginalia:not(.slide)", ".proof-gallery-split:not(.slide)",
      ".artifact-showcase:not(.slide)", ".artifact-dossier:not(.slide)", ".artifact-rail:not(.slide)", ".artifact-marginalia:not(.slide)", ".artifact-ledger:not(.slide)",
      ".content-label-board:not(.slide)", ".content-bento:not(.slide)", ".content-marginalia:not(.slide)", ".content-field-manual:not(.slide)", ".content-workbench-index:not(.slide)", ".metrics-led:not(.slide)", ".metrics-ledger:not(.slide)", ".text-two-col:not(.slide)", ".matrix-ledger:not(.slide)", ".matrix-map:not(.slide)",
      ".two-col", ".evidence-grid", ".evidence-grid aside", ".matrix-grid",
      ".proof", ".proof-visual", ".proof figcaption", ".artifact-panel", ".artifact-visual", ".artifact-panel figcaption",
      ".proof-notes", ".artifact-notes", ".tags", ".metrics",
      ".label-board", ".spine", ".case-row", ".cover-art", ".cover-art figcaption"
    ];
    const slideClasses = slide ? Array.from(slide.classList) : [];
    const slideKind = slideClasses.find((name) => !["slide", "dark", "light"].includes(name)) || "";
    const composition = () => {{
      if (!slide) return "unknown";
      if (slide.dataset.composition) return slide.dataset.composition;
      if (slide.classList.contains("cover")) return "cover";
      if (slide.classList.contains("matrix")) return "matrix";
      if (slide.classList.contains("map")) return "spine-map";
      if (slide.querySelector(".proof")) return "proof-led";
      if (slide.querySelector(".artifact-panel")) return "artifact-content";
      if (slide.querySelector(".label-board")) return "label-board";
      if (slide.querySelector(".metrics")) return "metrics-led";
      if (slide.querySelector(".two-col")) return "text-two-col";
      return slideKind || "unknown";
    }};
    const entries = [];
    const imageContracts = [];
    const seen = new Set();
    selectors.forEach((selector) => {{
      document.querySelectorAll(selector).forEach((el) => {{
        if (seen.has(el)) return;
        seen.add(el);
        const style = window.getComputedStyle(el);
        if (style.display === "none" || style.visibility === "hidden") return;
        const r = el.getBoundingClientRect();
        if (r.width < 8 || r.height < 8) return;
        entries.push({{ el, selector, label: boxLabel(el), x: r.left, y: r.top, right: r.right, bottom: r.bottom, w: r.width, h: r.height, area: r.width * r.height }});
        if (r.left < -8 || r.top < -8 || r.right > vw + 8 || r.bottom > vh + 8) {{
          issues.push({{ level: "error", type: "viewport-overflow", target: boxLabel(el), detail: `${{Math.round(r.left)}},${{Math.round(r.top)}} ${{Math.round(r.right)}}x${{Math.round(r.bottom)}}` }});
        }}
      }});
    }});
    const pseudoTargets = [slide, ...Array.from(document.querySelectorAll(
      ".slide > *, .proof, .proof-visual, .artifact-panel, .artifact-visual, .cover-art, .evidence-grid, .two-col, .matrix-grid, figure, figcaption"
    ))].filter(Boolean);
    const pseudoSeen = new Set();
    pseudoTargets.forEach((el) => {{
      if (pseudoSeen.has(el)) return;
      pseudoSeen.add(el);
      ["::before", "::after"].forEach((pseudo) => {{
        const style = window.getComputedStyle(el, pseudo);
        const content = style.content || "none";
        if (!content || content === "none" || content === "normal") return;
        const opacity = Number.parseFloat(style.opacity || "0");
        const z = style.zIndex === "auto" ? 0 : Number.parseFloat(style.zIndex || "0");
        if (opacity > .02 && Number.isFinite(z) && z > 0) {{
          issues.push({{ level: "error", type: "pseudo-overlay-front", target: `${{boxLabel(el)}}${{pseudo}}`, detail: `pseudo layer has opacity ${{opacity}} and z-index ${{z}}; visual grammar overlays must stay behind content` }});
        }}
      }});
    }});
    containerSelectors.forEach((selector) => {{
      document.querySelectorAll(selector).forEach((el) => {{
        const style = window.getComputedStyle(el);
        if (style.display === "none" || style.visibility === "hidden") return;
        const xOverflow = el.scrollWidth > el.clientWidth + 8;
        const yOverflow = el.scrollHeight > el.clientHeight + 8;
        if (xOverflow || yOverflow) {{
          const hard = [".two-col", ".evidence-grid", ".evidence-grid aside", ".matrix-grid", ".proof", ".artifact-panel"].includes(selector);
          issues.push({{ level: hard ? "error" : "warn", type: "container-overflow", target: boxLabel(el), detail: `${{el.scrollWidth}}x${{el.scrollHeight}} scroll in ${{el.clientWidth}}x${{el.clientHeight}} box` }});
        }}
      }});
    }});
    entries.forEach((a, i) => {{
      for (let j = i + 1; j < entries.length; j += 1) {{
        const b = entries[j];
        if (a.el.contains(b.el) || b.el.contains(a.el)) continue;
        const w = Math.max(0, Math.min(a.right, b.right) - Math.max(a.x, b.x));
        const h = Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.y, b.y));
        const overlap = w * h;
        if (!overlap) continue;
        const ratio = overlap / Math.max(1, Math.min(a.area, b.area));
        if (overlap > 1400 && ratio > 0.035) {{
          const footerOnly = a.selector.startsWith("footer") && b.selector.startsWith("footer");
          issues.push({{ level: footerOnly ? "warn" : "error", type: "element-overlap", target: `${{a.label}} x ${{b.label}}`, detail: `${{Math.round(ratio * 100)}}% smaller-box overlap` }});
        }}
      }}
    }});
    const fillEntries = entries.filter((entry) => !entry.selector.startsWith("footer"));
    const cellsX = 80;
    const cellsY = 45;
    const occupied = new Set();
    fillEntries.forEach((entry) => {{
      const x0 = Math.max(0, Math.floor(entry.x / vw * cellsX));
      const x1 = Math.min(cellsX - 1, Math.ceil(entry.right / vw * cellsX));
      const y0 = Math.max(0, Math.floor(entry.y / vh * cellsY));
      const y1 = Math.min(cellsY - 1, Math.ceil(entry.bottom / vh * cellsY));
      for (let y = y0; y <= y1; y += 1) {{
        for (let x = x0; x <= x1; x += 1) occupied.add(`${{x}},${{y}}`);
      }}
    }});
    const contentFill = occupied.size / (cellsX * cellsY);
    const currentComposition = composition();
    let fillTarget = .26;
    if (slide && slide.classList.contains("cover")) {{
      fillTarget = .20;
    }} else if (currentComposition.startsWith("proof-")) {{
      fillTarget = .34;
    }} else if (currentComposition.startsWith("artifact-")) {{
      fillTarget = .30;
    }} else if (currentComposition.startsWith("matrix-")) {{
      fillTarget = .30;
    }} else if (currentComposition === "content-workbench-index") {{
      fillTarget = .34;
    }} else if (currentComposition.startsWith("content-") || currentComposition === "text-two-col") {{
      fillTarget = .30;
    }}
    if (contentFill < fillTarget) {{
      issues.push({{ level: "warn", type: "content-underfilled", target: ".slide", detail: `${{Math.round(contentFill * 100)}}% occupied grid; target ${{Math.round(fillTarget * 100)}}% for ${{currentComposition}}` }});
    }}
    document.querySelectorAll(textSelectors.join(",")).forEach((el) => {{
      if (el.scrollWidth > el.clientWidth + 8 || el.scrollHeight > el.clientHeight + 24) {{
        issues.push({{ level: "error", type: "text-overflow", target: boxLabel(el), detail: `${{el.scrollWidth}}x${{el.scrollHeight}} scroll in ${{el.clientWidth}}x${{el.clientHeight}} box` }});
      }}
    }});
    document.querySelectorAll(".proof,.artifact-panel,.cover-art").forEach((figure) => {{
      const visual = figure.querySelector(".proof-visual,.artifact-visual,img");
      const caption = figure.querySelector("figcaption");
      if (!visual || !caption) return;
      const vr = visual.getBoundingClientRect();
      const cr = caption.getBoundingClientRect();
      const verticalGap = cr.top - vr.bottom;
      const horizontalOverlap = Math.max(0, Math.min(vr.right, cr.right) - Math.max(vr.left, cr.left));
      if (horizontalOverlap > 12 && verticalGap < FIGURE_CAPTION_CLEARANCE_PX) {{
        issues.push({{ level: "error", type: "figure-caption-clearance-tight", target: `${{boxLabel(visual)}} x ${{boxLabel(caption)}}`, detail: `${{Math.round(verticalGap)}}px between image slot and caption` }});
      }}
      if (cr.top < vr.bottom - 1 && horizontalOverlap > 12) {{
        issues.push({{ level: "error", type: "figure-caption-overlap", target: `${{boxLabel(visual)}} x ${{boxLabel(caption)}}`, detail: "caption overlaps rendered image slot" }});
      }}
    }});
    const textElements = Array.from(document.querySelectorAll(textSelectors.join(","))).filter((el) => {{
      const style = window.getComputedStyle(el);
      const r = el.getBoundingClientRect();
      return style.display !== "none" && style.visibility !== "hidden" && r.width >= 8 && r.height >= 8 && (el.textContent || "").trim();
    }});
    const sameSemanticTextGroup = (left, right) => {{
      if (left.label.includes("@.metric") && right.label.includes("@.metric")) return true;
      if (left.label.includes("@.tags") && right.label.includes("@.tags")) return true;
      const groups = [".tags", ".metric", ".label-board div", "figcaption", ".proof-notes li", ".artifact-notes li", "ul", "ol", "table"];
      return groups.some((selector) => {{
        const a = left.el.closest(selector);
        const b = right.el.closest(selector);
        return a && b && a === b;
      }});
    }};
    const textBlockRects = textElements.map((el) => {{
      const r = el.getBoundingClientRect();
      return {{ el, label: boxLabel(el), x: r.left, y: r.top, right: r.right, bottom: r.bottom, w: r.width, h: r.height, area: r.width * r.height }};
    }}).filter((entry) => entry.w >= 8 && entry.h >= 8);
    const textRects = [];
    const slideRect = slide ? slide.getBoundingClientRect() : null;
    textElements.forEach((el) => {{
      const range = document.createRange();
      range.selectNodeContents(el);
      const elementRects = [];
      Array.from(range.getClientRects()).forEach((rect) => {{
        if (rect.width < 4 || rect.height < 4) return;
        const entry = {{ el, label: boxLabel(el), x: rect.left, y: rect.top, right: rect.right, bottom: rect.bottom, w: rect.width, h: rect.height, area: rect.width * rect.height }};
        textRects.push(entry);
        elementRects.push(entry);
      }});
      range.detach();
      const style = window.getComputedStyle(el);
      const fontSize = Number.parseFloat(style.fontSize) || 0;
      const lineHeight = Number.parseFloat(style.lineHeight) || fontSize * 1.2;
      const sameLineTolerance = Math.max(2, fontSize * .42);
      const lineGroups = [];
      elementRects
        .slice()
        .sort((a, b) => a.y - b.y)
        .forEach((entry) => {{
          const cy = (entry.y + entry.bottom) / 2;
          let group = lineGroups.find((item) => Math.abs(item.cy - cy) < sameLineTolerance);
          if (!group) {{
            group = {{ cy, x: entry.x, y: entry.y, right: entry.right, bottom: entry.bottom }};
            lineGroups.push(group);
            return;
          }}
          group.x = Math.min(group.x, entry.x);
          group.y = Math.min(group.y, entry.y);
          group.right = Math.max(group.right, entry.right);
          group.bottom = Math.max(group.bottom, entry.bottom);
          group.cy = (group.y + group.bottom) / 2;
        }});
      const lineTops = [];
      elementRects
        .map((entry) => entry.y)
        .sort((a, b) => a - b)
        .forEach((top) => {{
          if (!lineTops.some((existing) => Math.abs(existing - top) < sameLineTolerance)) lineTops.push(top);
        }});
      if (lineTops.length > 1) {{
        const steps = lineTops.slice(1).map((top, index) => top - lineTops[index]).filter((step) => step > 0);
        const minStep = steps.length ? Math.min(...steps) : lineHeight;
        if (fontSize && (lineHeight < fontSize * TEXT_LINE_HEIGHT_SAFE_RATIO || minStep < fontSize * 1.05)) {{
          const footerOnly = boxLabel(el).startsWith("footer");
          issues.push({{ level: footerOnly ? "warn" : "error", type: "text-line-height-tight", target: boxLabel(el), detail: `line-height ${{Math.round(lineHeight)}}px / font ${{Math.round(fontSize)}}px / min line step ${{Math.round(minStep)}}px; minimum safe ratio ${{TEXT_LINE_HEIGHT_SAFE_RATIO}}` }});
        }}
        if (fontSize && (lineHeight < fontSize * 1.03 || minStep < fontSize * 1.0)) {{
          const footerOnly = boxLabel(el).startsWith("footer");
          issues.push({{ level: footerOnly ? "warn" : "error", type: "text-self-overlap", target: boxLabel(el), detail: `line-height ${{Math.round(lineHeight)}}px / font ${{Math.round(fontSize)}}px / min line step ${{Math.round(minStep)}}px` }});
        }}
        lineGroups
          .sort((a, b) => a.y - b.y)
          .forEach((group, index, groups) => {{
            if (index === 0) return;
            const prev = groups[index - 1];
            const lineOverlap = Math.max(0, prev.bottom - group.y);
            const horizontalOverlap = Math.max(0, Math.min(prev.right, group.right) - Math.max(prev.x, group.x));
            if (lineOverlap > Math.max(8, fontSize * .38) && horizontalOverlap > 8) {{
              const footerOnly = boxLabel(el).startsWith("footer");
              issues.push({{ level: footerOnly ? "warn" : "error", type: "text-self-overlap", target: boxLabel(el), detail: `${{Math.round(lineOverlap)}}px rendered line-box overlap inside one text element` }});
            }}
          }});
      }}
      const lineCount = Math.max(lineTops.length, lineGroups.length);
      if (lineCount > 1 && el.matches("h1,h2")) {{
        const maxTitleLines = slide && slide.classList.contains("cover") ? COVER_TITLE_LINE_MAX : TITLE_LINE_MAX;
        if (lineCount > maxTitleLines) {{
          issues.push({{ level: "error", type: "title-wrap-too-deep", target: boxLabel(el), detail: `${{lineCount}} rendered title lines; maximum ${{maxTitleLines}} before layout becomes unsafe` }});
        }} else if (lineCount > TITLE_LINE_WARN) {{
          issues.push({{ level: "warn", type: "title-wrap-deep", target: boxLabel(el), detail: `${{lineCount}} rendered title lines; shorten action title or split the slide` }});
        }}
      }}
      if (lineCount > 1 && el.matches(".subtitle,.lead")) {{
        if (lineCount > SUBTITLE_LINE_MAX) {{
          issues.push({{ level: "error", type: "subtitle-wrap-too-deep", target: boxLabel(el), detail: `${{lineCount}} rendered subtitle lines; maximum ${{SUBTITLE_LINE_MAX}} before layout becomes unsafe` }});
        }} else if (lineCount > SUBTITLE_LINE_WARN) {{
          issues.push({{ level: "warn", type: "subtitle-wrap-deep", target: boxLabel(el), detail: `${{lineCount}} rendered subtitle lines; move detail to bullets or notes` }});
        }}
      }}
      const clip = nearestClipBox(el);
      if (clip) {{
        const clipped = elementRects.some((entry) => entry.x < clip.left - 3 || entry.y < clip.top - 3 || entry.right > clip.right + 3 || entry.bottom > clip.bottom + 3);
        if (clipped) {{
          issues.push({{ level: "error", type: "text-clipped", target: boxLabel(el), detail: "text range extends beyond its clipping container; shorten copy or change layout" }});
        }}
      }}
      if (slideRect) {{
        const outsideSlide = elementRects.some((entry) => entry.x < slideRect.left - 3 || entry.y < slideRect.top - 3 || entry.right > slideRect.right + 3 || entry.bottom > slideRect.bottom + 3);
        if (outsideSlide) {{
          issues.push({{ level: "error", type: "text-clipped", target: boxLabel(el), detail: "text range extends beyond the slide canvas; reduce type scale, shorten copy, or switch composition" }});
        }}
      }}
    }});
    textRects.forEach((entry) => {{
      if (!entry.label.startsWith("footer")) usefulBoxes.push(entry);
    }});
    textBlockRects.forEach((a, i) => {{
      for (let j = i + 1; j < textBlockRects.length; j += 1) {{
        const b = textBlockRects[j];
        if (a.el === b.el || a.el.contains(b.el) || b.el.contains(a.el)) continue;
        const sameMicroStack = sameSemanticTextGroup(a, b);
        const footerOnly = a.label.startsWith("footer") && b.label.startsWith("footer");
        const w = Math.max(0, Math.min(a.right, b.right) - Math.max(a.x, b.x));
        const h = Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.y, b.y));
        const overlap = w * h;
        if (overlap > 80) {{
          const ratio = overlap / Math.max(1, Math.min(a.area, b.area));
          if (ratio > .055 && (!sameMicroStack || ratio > .16)) {{
            issues.push({{ level: footerOnly ? "warn" : "error", type: "text-block-overlap", target: `${{a.label}} x ${{b.label}}`, detail: `${{Math.round(ratio * 100)}}% smaller text block overlap` }});
          }}
          continue;
        }}
        const verticalGap = Math.max(0, Math.max(a.y - b.bottom, b.y - a.bottom));
        const horizontalShare = w / Math.max(1, Math.min(a.w, b.w));
        if (!sameMicroStack && w > 28 && horizontalShare > .28 && verticalGap < TEXT_BLOCK_CLEARANCE_PX) {{
          issues.push({{ level: footerOnly ? "warn" : "error", type: "text-block-clearance-tight", target: `${{a.label}} x ${{b.label}}`, detail: `${{Math.round(verticalGap)}}px vertical clearance between text blocks` }});
        }}
        const verticalOverlap = Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.y, b.y));
        const verticalShare = verticalOverlap / Math.max(1, Math.min(a.h, b.h));
        const horizontalGap = Math.max(0, Math.max(a.x - b.right, b.x - a.right));
        if (!sameMicroStack && verticalOverlap > 8 && verticalShare > .25 && horizontalGap < TEXT_BLOCK_SIDE_CLEARANCE_PX) {{
          issues.push({{ level: footerOnly ? "warn" : "error", type: "text-block-clearance-tight", target: `${{a.label}} x ${{b.label}}`, detail: `${{Math.round(horizontalGap)}}px side clearance between text blocks` }});
        }}
      }}
    }});
    textRects.forEach((a, i) => {{
      for (let j = i + 1; j < textRects.length; j += 1) {{
        const b = textRects[j];
        if (a.el === b.el || a.el.contains(b.el) || b.el.contains(a.el)) continue;
        const sameMicroStack = sameSemanticTextGroup(a, b);
        const w = Math.max(0, Math.min(a.right, b.right) - Math.max(a.x, b.x));
        const h = Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.y, b.y));
        const overlap = w * h;
        if (!overlap) {{
          const verticalGap = Math.max(0, Math.max(a.y - b.bottom, b.y - a.bottom));
          const horizontalShare = w / Math.max(1, Math.min(a.w, b.w));
          if (w > 24 && horizontalShare > .22 && verticalGap < TEXT_CLEARANCE_PX) {{
            if (sameMicroStack) continue;
            const footerOnly = a.label.startsWith("footer") && b.label.startsWith("footer");
            issues.push({{ level: footerOnly ? "warn" : "error", type: "text-clearance-tight", target: `${{a.label}} x ${{b.label}}`, detail: `${{Math.round(verticalGap)}}px vertical clearance` }});
          }}
          continue;
        }}
        const ratio = overlap / Math.max(1, Math.min(a.area, b.area));
        if (overlap > 24 && ratio > 0.12) {{
          const footerOnly = a.label.startsWith("footer") && b.label.startsWith("footer");
          issues.push({{ level: footerOnly ? "warn" : "error", type: "text-line-overlap", target: `${{a.label}} x ${{b.label}}`, detail: `${{Math.round(ratio * 100)}}% smaller-line overlap` }});
        }}
      }}
    }});
    const visualSlots = Array.from(document.querySelectorAll(".proof-visual,.artifact-visual,.cover-art")).map((el) => {{
      const r = el.getBoundingClientRect();
      return {{ el, label: boxLabel(el), x: r.left, y: r.top, right: r.right, bottom: r.bottom, w: r.width, h: r.height, area: r.width * r.height }};
    }}).filter((entry) => entry.w >= 8 && entry.h >= 8);
    document.querySelectorAll(".slide img").forEach((img) => {{
      if (!img.closest(".proof,.artifact-panel,.cover-art")) {{
        issues.push({{ level: "error", type: "untyped-image", target: boxLabel(img), detail: "all slide images must be inserted through proof, artifact, or cover channels so crop, caption, clearance, and source-pixel checks apply" }});
      }}
    }});
    document.querySelectorAll(".slide svg,.slide canvas").forEach((el) => {{
      if (!el.closest(".proof,.artifact-panel,.cover-art")) {{
        issues.push({{ level: "error", type: "untyped-vector-image", target: boxLabel(el), detail: "SVG/canvas visuals inside slides must be a renderer-owned proof/artifact surface or a documented decoration; otherwise image contracts cannot audit crop, caption, or text clearance" }});
      }}
    }});
    document.querySelectorAll(".slide, .slide *").forEach((el) => {{
      const style = window.getComputedStyle(el);
      const bg = style.backgroundImage || "none";
      if (bg === "none" || !bg.includes("url(")) return;
      issues.push({{ level: "error", type: "untyped-background-image", target: boxLabel(el), detail: "CSS background-image URLs cannot carry slide visuals; use audited img-based evidence/cover channels so source pixels, crop, caption, and clearance can be measured" }});
    }});
    textRects.forEach((text) => {{
      visualSlots.forEach((slot) => {{
        if (slot.el.contains(text.el) || text.el.contains(slot.el)) return;
        const textFigure = text.el.closest(".proof,.artifact-panel,.cover-art");
        const slotFigure = slot.el.closest(".proof,.artifact-panel,.cover-art");
        const proofNoteText = text.el.closest(".proof-notes");
        const artifactNoteText = text.el.closest(".artifact-notes");
        if (textFigure && slotFigure && textFigure === slotFigure && !proofNoteText && !artifactNoteText) return;
        const overlapType = proofNoteText ? "proof-notes-image-overlap" : (artifactNoteText ? "artifact-notes-image-overlap" : "text-image-overlap");
        const clearanceType = proofNoteText || artifactNoteText ? "notes-image-clearance-tight" : "text-image-clearance-tight";
        const w = Math.max(0, Math.min(text.right, slot.right) - Math.max(text.x, slot.x));
        const h = Math.max(0, Math.min(text.bottom, slot.bottom) - Math.max(text.y, slot.y));
        const overlap = w * h;
        if (overlap > IMAGE_TEXT_OVERLAP_MIN_AREA_PX) {{
          const ratio = overlap / Math.max(1, text.area);
          issues.push({{ level: "error", type: overlapType, target: `${{text.label}} x ${{slot.label}}`, detail: `${{Math.round(ratio * 100)}}% of text line sits on an image/proof slot (${{Math.round(overlap)}}px overlap)` }});
          return;
        }}
        const verticalGap = Math.max(0, Math.max(text.y - slot.bottom, slot.y - text.bottom));
        const horizontalShare = w / Math.max(1, Math.min(text.w, slot.w));
        if (w > 28 && horizontalShare > .24 && verticalGap < IMAGE_CLEARANCE_PX) {{
          issues.push({{ level: "error", type: clearanceType, target: `${{text.label}} x ${{slot.label}}`, detail: `${{Math.round(verticalGap)}}px between text and image/proof slot` }});
        }}
        const verticalOverlap = Math.max(0, Math.min(text.bottom, slot.bottom) - Math.max(text.y, slot.y));
        const verticalShare = verticalOverlap / Math.max(1, Math.min(text.h, slot.h));
        const horizontalGap = Math.max(0, Math.max(text.x - slot.right, slot.x - text.right));
        if (verticalOverlap > 8 && verticalShare > .22 && horizontalGap < IMAGE_SIDE_CLEARANCE_PX) {{
          issues.push({{ level: "error", type: clearanceType, target: `${{text.label}} x ${{slot.label}}`, detail: `${{Math.round(horizontalGap)}}px horizontal clearance between text and image/proof slot` }});
        }}
      }});
    }});
    document.querySelectorAll(".proof,.artifact-panel,.cover-art").forEach((figure) => {{
      const role = figure.dataset.imageRole || "";
      const hasRenderedImage = Boolean(figure.querySelector("img"));
      const needsEvidenceContract = figure.classList.contains("proof") || figure.classList.contains("artifact-panel") || figure.dataset.hasEvidence === "true";
      if (hasRenderedImage && !role) {{
        issues.push({{ level: "error", type: "image-contract-missing", target: boxLabel(figure), detail: "inserted images need data-image-role so crop, caption, source, and clearance rules can be audited" }});
      }}
      if (hasRenderedImage && needsEvidenceContract) {{
        if (figure.dataset.hasCrop !== "true") {{
          issues.push({{ level: "error", type: "image-crop-missing", target: boxLabel(figure), detail: "proof and artifact images must declare an explicit crop before insertion" }});
        }}
        if (figure.dataset.hasCaption !== "true" || figure.dataset.hasSource !== "true") {{
          issues.push({{ level: "error", type: "image-caption-source-missing", target: boxLabel(figure), detail: "proof and artifact images must carry both a specific caption and compact source line" }});
        }}
      }}
      const caption = figure.querySelector("figcaption b");
      const source = figure.querySelector("figcaption span");
      const captionText = caption ? (caption.textContent || "").trim().toLowerCase() : "";
      const sourceText = source ? (source.textContent || "").trim().toLowerCase() : "";
      if (figure.classList.contains("proof") && slide && (slide.classList.contains("evidence") || slide.classList.contains("loop") || slide.classList.contains("product"))) {{
        if (!captionText || !sourceText) {{
          issues.push({{ level: "warn", type: "proof-caption-missing", target: boxLabel(figure), detail: "primary evidence needs both a claim caption and compact source line" }});
        }} else if (genericImageContext(captionText) || genericImageContext(sourceText)) {{
          issues.push({{ level: "warn", type: "proof-caption-generic", target: boxLabel(figure), detail: "primary evidence caption/source is too generic to prove the claim" }});
        }}
      }}
      if (figure.classList.contains("artifact-panel")) {{
        if (!captionText || !sourceText || genericImageContext(captionText) || genericImageContext(sourceText)) {{
          issues.push({{ level: "warn", type: "artifact-caption-generic", target: boxLabel(figure), detail: "artifact image needs a specific caption and source, not a generic image fallback" }});
        }}
      }}
      [caption, source].forEach((el) => {{
        if (!el) return;
        const style = window.getComputedStyle(el);
        const fontSize = Number.parseFloat(style.fontSize) || 0;
        if (fontSize && fontSize < 10.5) {{
          issues.push({{ level: "warn", type: "caption-text-too-small", target: boxLabel(el), detail: `${{Math.round(fontSize * 10) / 10}}px caption/source text` }});
        }}
        const ratio = contrastRatio(style.color, effectiveBackgroundColor(figure));
        if (ratio !== null && ratio < SUPPORT_TEXT_CONTRAST_MIN) {{
          issues.push({{ level: "warn", type: "caption-contrast-low", target: boxLabel(el), detail: `${{Math.round(ratio * 10) / 10}}:1 contrast against figure background; target ${{SUPPORT_TEXT_CONTRAST_MIN}}:1 for projection-safe support text` }});
        }}
      }});
    }});
    document.querySelectorAll(".label-board b").forEach((el) => {{
      const parent = el.parentElement || el;
      const r = el.getBoundingClientRect();
      if (r.width < 4 || r.height < 4) return;
      const style = window.getComputedStyle(el);
      const ratio = contrastRatio(style.color, effectiveBackgroundColor(parent));
      if (ratio !== null && ratio < SUPPORT_TEXT_CONTRAST_MIN) {{
        issues.push({{ level: "warn", type: "label-contrast-low", target: boxLabel(el), detail: `${{Math.round(ratio * 10) / 10}}:1 contrast against label card background; target ${{SUPPORT_TEXT_CONTRAST_MIN}}:1 for projection-safe support text` }});
      }}
    }});
    document.querySelectorAll(".proof img,.artifact-panel img,.cover-art img").forEach((img) => {{
      const r = img.getBoundingClientRect();
      const parent = img.parentElement ? img.parentElement.getBoundingClientRect() : r;
      const source = sourceBoxFor(img, parent);
      const visibleSource = intersectBox(source, parent);
      const visibleAreaRatio = (visibleSource.width * visibleSource.height) / (vw * vh);
      const slotUse = (visibleSource.width * visibleSource.height) / Math.max(1, parent.width * parent.height);
      const figure = img.closest(".proof,.artifact-panel,.cover-art");
      const imageRole = img.closest(".proof") ? "proof" : (img.closest(".artifact-panel") ? "artifact" : "cover");
      if (figure) {{
        imageContracts.push({{
          role: imageRole,
          target: boxLabel(img),
          src: img.getAttribute("src") || "",
          natural_width: img.naturalWidth || 0,
          natural_height: img.naturalHeight || 0,
          rendered_width: Math.round(visibleSource.width),
          rendered_height: Math.round(visibleSource.height),
          visible_area: Number(visibleAreaRatio.toFixed(3)),
          slot_use: Number(slotUse.toFixed(3)),
          loaded: Boolean(img.complete && img.naturalWidth && img.naturalHeight),
          has_crop: figure.dataset.hasCrop === "true",
          has_caption: figure.dataset.hasCaption === "true",
          has_source: figure.dataset.hasSource === "true",
        }});
      }}
      if (visibleSource.width >= 8 && visibleSource.height >= 8) {{
        usefulBoxes.push({{
          label: boxLabel(img),
          x: visibleSource.left,
          y: visibleSource.top,
          right: visibleSource.right,
          bottom: visibleSource.bottom,
          w: visibleSource.width,
          h: visibleSource.height,
          area: visibleSource.width * visibleSource.height
        }});
      }}
      if (!img.complete || !img.naturalWidth || !img.naturalHeight) {{
        issues.push({{ level: "error", type: "image-not-loaded", target: boxLabel(img), detail: img.getAttribute("src") || "missing src" }});
      }}
      if (source.unsupported) {{
        issues.push({{ level: "error", type: "image-object-fit-unsupported", target: boxLabel(img), detail: `object-fit ${{source.objectFit}} cannot be audited safely; use contain or cover` }});
      }}
      if (r.width > parent.width + 2 || r.height > parent.height + 2) {{
        issues.push({{ level: "error", type: "image-overflow", target: boxLabel(img), detail: `${{Math.round(r.width)}}x${{Math.round(r.height)}} image in ${{Math.round(parent.width)}}x${{Math.round(parent.height)}} parent` }});
      }}
      if (img.closest(".proof") && slide && (slide.classList.contains("evidence") || slide.classList.contains("loop") || slide.classList.contains("product"))) {{
        const proofUpscale = img.naturalWidth && img.naturalHeight ? Math.max(visibleSource.width / img.naturalWidth, visibleSource.height / img.naturalHeight) : 1;
        if (proofUpscale > 1.65) {{
          issues.push({{ level: "error", type: "proof-image-upscaled-too-much", target: boxLabel(img), detail: `${{Math.round(proofUpscale * 10) / 10}}x upscale from ${{img.naturalWidth}}x${{img.naturalHeight}} source pixels` }});
        }}
        if (visibleAreaRatio < .22) {{
          issues.push({{ level: "error", type: "proof-image-too-small", target: boxLabel(img), detail: `${{Math.round(visibleAreaRatio * 100)}}% visible slide area` }});
        }} else if (visibleAreaRatio < .295) {{
          issues.push({{ level: "warn", type: "proof-image-small", target: boxLabel(img), detail: `${{Math.round(visibleAreaRatio * 100)}}% visible slide area` }});
        }}
        if (visibleSource.width < 780 || visibleSource.height < 420) {{
          issues.push({{ level: "error", type: "proof-image-rendered-too-small", target: boxLabel(img), detail: `${{Math.round(visibleSource.width)}}x${{Math.round(visibleSource.height)}} rendered source pixels` }});
        }} else if (visibleSource.width < 1000 || visibleSource.height < 540) {{
          issues.push({{ level: "warn", type: "proof-image-rendered-small", target: boxLabel(img), detail: `${{Math.round(visibleSource.width)}}x${{Math.round(visibleSource.height)}} rendered source pixels` }});
        }}
        if (slotUse < .35) {{
          issues.push({{ level: "error", type: "proof-image-letterboxed-severe", target: boxLabel(img), detail: `${{Math.round(slotUse * 100)}}% of proof slot contains source pixels; crop tighter or change slot shape` }});
        }} else if (slotUse < .55) {{
          issues.push({{ level: "warn", type: "proof-image-letterboxed", target: boxLabel(img), detail: `${{Math.round(slotUse * 100)}}% of proof slot contains source pixels; crop tighter or change slot shape` }});
        }}
      }}
      if (img.closest(".artifact-panel")) {{
        const figure = img.closest(".artifact-panel");
        const roleText = [
          img.getAttribute("src") || "",
          img.getAttribute("alt") || "",
          figure ? (figure.querySelector("figcaption")?.textContent || "") : ""
        ].join(" ").toLowerCase();
        const sourceHeavyArtifact = /(github|repo|repository|code|demo|dataset|benchmark|leaderboard|paper|arxiv|table|chart|figure|dashboard|ui|workflow|project page|homepage|screenshot|screen|interface|web|site|html|pdf)/.test(roleText);
        const artifactUpscale = img.naturalWidth && img.naturalHeight ? Math.max(visibleSource.width / img.naturalWidth, visibleSource.height / img.naturalHeight) : 1;
        if (artifactUpscale > 1.85) {{
          issues.push({{ level: "error", type: "artifact-image-upscaled-too-much", target: boxLabel(img), detail: `${{Math.round(artifactUpscale * 10) / 10}}x upscale from ${{img.naturalWidth}}x${{img.naturalHeight}} source pixels` }});
        }}
        if (sourceHeavyArtifact && visibleAreaRatio < .15) {{
          issues.push({{ level: "error", type: "artifact-role-underfeatured", target: boxLabel(img), detail: `${{Math.round(visibleAreaRatio * 100)}}% visible slide area for source-heavy artifact` }});
        }} else if (sourceHeavyArtifact && visibleAreaRatio < .20) {{
          issues.push({{ level: "warn", type: "artifact-role-underfeatured", target: boxLabel(img), detail: `${{Math.round(visibleAreaRatio * 100)}}% visible slide area for source-heavy artifact` }});
        }}
        if (sourceHeavyArtifact && (visibleSource.width < 820 || visibleSource.height < 460)) {{
          issues.push({{ level: "error", type: "artifact-role-underfeatured", target: boxLabel(img), detail: `${{Math.round(visibleSource.width)}}x${{Math.round(visibleSource.height)}} rendered source pixels for source-heavy artifact` }});
        }} else if (sourceHeavyArtifact && (visibleSource.width < 980 || visibleSource.height < 540)) {{
          issues.push({{ level: "warn", type: "artifact-role-underfeatured", target: boxLabel(img), detail: `${{Math.round(visibleSource.width)}}x${{Math.round(visibleSource.height)}} rendered source pixels for source-heavy artifact` }});
        }}
        if (visibleAreaRatio < .09) {{
          issues.push({{ level: "error", type: "artifact-image-too-small", target: boxLabel(img), detail: `${{Math.round(visibleAreaRatio * 100)}}% visible slide area` }});
        }} else if (visibleAreaRatio < .13) {{
          issues.push({{ level: "warn", type: "artifact-image-small", target: boxLabel(img), detail: `${{Math.round(visibleAreaRatio * 100)}}% visible slide area` }});
        }}
        if (visibleSource.width < 520 || visibleSource.height < 300) {{
          issues.push({{ level: "error", type: "artifact-image-rendered-too-small", target: boxLabel(img), detail: `${{Math.round(visibleSource.width)}}x${{Math.round(visibleSource.height)}} rendered source pixels` }});
        }} else if (visibleSource.width < 720 || visibleSource.height < 400) {{
          issues.push({{ level: "warn", type: "artifact-image-rendered-small", target: boxLabel(img), detail: `${{Math.round(visibleSource.width)}}x${{Math.round(visibleSource.height)}} rendered source pixels` }});
        }}
        if (slotUse < .32) {{
          issues.push({{ level: "error", type: "artifact-image-letterboxed-severe", target: boxLabel(img), detail: `${{Math.round(slotUse * 100)}}% of artifact slot contains source pixels; crop tighter or change slot shape` }});
        }} else if (slotUse < .5) {{
          issues.push({{ level: "warn", type: "artifact-image-letterboxed", target: boxLabel(img), detail: `${{Math.round(slotUse * 100)}}% of artifact slot contains source pixels; crop tighter or change slot shape` }});
        }}
      }}
      if (img.closest(".cover-art") && slotUse < .35) {{
        issues.push({{ level: "warn", type: "cover-image-letterboxed", target: boxLabel(img), detail: `${{Math.round(slotUse * 100)}}% of cover image slot contains source pixels; crop or use a smaller identity slot` }});
      }}
      if (img.closest(".cover-art") && visibleAreaRatio < .035) {{
        issues.push({{ level: "warn", type: "decorative-image-too-small", target: boxLabel(img), detail: `${{Math.round(visibleAreaRatio * 100)}}% visible slide area; cover image may read as decoration rather than evidence` }});
      }}
    }});
    document.querySelectorAll(".pin").forEach((pin) => {{
      const host = pin.closest(".proof-visual,.artifact-visual");
      if (!host) return;
      const r = pin.getBoundingClientRect();
      const box = host.getBoundingClientRect();
      const img = host.querySelector("img");
      const source = img && img.naturalWidth && img.naturalHeight ? sourceBoxFor(img, box) : box;
      const cx = r.left + r.width / 2;
      const cy = r.top + r.height / 2;
      if (r.left < box.left || r.top < box.top || r.right > box.right || r.bottom > box.bottom) {{
        issues.push({{ level: "error", type: "callout-outside-image", target: boxLabel(pin), detail: "pin marker is clipped or outside its image slot" }});
      }}
      if (cx < source.left || cy < source.top || cx > source.right || cy > source.bottom) {{
        issues.push({{ level: "error", type: "callout-outside-source-image", target: boxLabel(pin), detail: "pin center falls in letterbox whitespace rather than on the rendered source image" }});
      }}
    }});
    const pins = Array.from(document.querySelectorAll(".pin")).map((pin) => {{
      const r = pin.getBoundingClientRect();
      return {{ pin, label: boxLabel(pin), x: r.left, y: r.top, right: r.right, bottom: r.bottom, area: r.width * r.height }};
    }});
    pins.forEach((a, i) => {{
      for (let j = i + 1; j < pins.length; j += 1) {{
        const b = pins[j];
        const w = Math.max(0, Math.min(a.right, b.right) - Math.max(a.x, b.x));
        const h = Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.y, b.y));
        const overlap = w * h;
        if (overlap > 4) {{
          issues.push({{ level: "warn", type: "callout-overlap", target: `${{a.label}} x ${{b.label}}`, detail: "pin markers overlap; remove or separate callouts" }});
        }}
      }}
    }});
    const artifact = document.querySelector(".artifact-panel");
    if (artifact) {{
      const r = artifact.getBoundingClientRect();
      const artifactRatio = (r.width * r.height) / (vw * vh);
      if (artifactRatio < .16) {{
        issues.push({{ level: "error", type: "artifact-too-small", target: ".artifact-panel", detail: `${{Math.round(artifactRatio * 100)}}% slide area` }});
      }} else if (artifactRatio < .22) {{
        issues.push({{ level: "warn", type: "artifact-small", target: ".artifact-panel", detail: `${{Math.round(artifactRatio * 100)}}% slide area` }});
      }}
    }}
    if (slide && (slide.classList.contains("evidence") || slide.classList.contains("loop") || slide.classList.contains("product"))) {{
      const proof = document.querySelector(".proof");
      if (!proof) {{
        issues.push({{ level: "error", type: "missing-proof", target: ".proof", detail: "evidence-like slide has no proof surface" }});
      }} else {{
        if (proof.classList.contains("empty") || !proof.querySelector("img")) {{
          issues.push({{ level: "error", type: "missing-proof-image", target: ".proof", detail: "evidence-like slide rendered a proof placeholder instead of a loaded image" }});
        }}
        const r = proof.getBoundingClientRect();
        const proofRatio = (r.width * r.height) / (vw * vh);
        if (proofRatio < 0.28) {{
          issues.push({{ level: "error", type: "proof-too-small", target: ".proof", detail: `${{Math.round(proofRatio * 100)}}% slide area` }});
        }} else if (proofRatio < 0.36) {{
          issues.push({{ level: "warn", type: "proof-small", target: ".proof", detail: `${{Math.round(proofRatio * 100)}}% slide area` }});
        }}
      }}
    }}
    const usefulOccupied = new Set();
    usefulBoxes.forEach((entry) => {{
      const x0 = Math.max(0, Math.floor(entry.x / vw * cellsX));
      const x1 = Math.min(cellsX - 1, Math.ceil(entry.right / vw * cellsX));
      const y0 = Math.max(0, Math.floor(entry.y / vh * cellsY));
      const y1 = Math.min(cellsY - 1, Math.ceil(entry.bottom / vh * cellsY));
      for (let y = y0; y <= y1; y += 1) {{
        for (let x = x0; x <= x1; x += 1) usefulOccupied.add(`${{x}},${{y}}`);
      }}
    }});
    const usefulFill = usefulOccupied.size / (cellsX * cellsY);
    let usefulTarget = .16;
    if (slide && slide.classList.contains("cover")) {{
      usefulTarget = .12;
    }} else if (currentComposition.startsWith("proof-")) {{
      usefulTarget = .24;
    }} else if (currentComposition.startsWith("artifact-")) {{
      usefulTarget = .22;
    }} else if (currentComposition.startsWith("matrix-")) {{
      usefulTarget = .18;
    }} else if (currentComposition.startsWith("content-") || currentComposition === "text-two-col") {{
      usefulTarget = .20;
    }}
    if (usefulFill < usefulTarget) {{
      issues.push({{ level: "warn", type: "useful-fill-low", target: ".slide", detail: `${{Math.round(usefulFill * 100)}}% useful text/source fill; target ${{Math.round(usefulTarget * 100)}}% for ${{currentComposition}}` }});
    }}
    const pre = document.createElement("pre");
    pre.id = "layout-audit";
    pre.textContent = JSON.stringify({{
      slide: target || 0,
      grammar: document.body.dataset.visualGrammar || "",
      slide_kind: slideKind,
      slide_classes: slideClasses,
      composition: composition(),
      layout_intent: slide ? (slide.dataset.layoutIntent || "") : "",
      issues,
      metrics: {{ content_fill: Number(contentFill.toFixed(3)), useful_fill: Number(usefulFill.toFixed(3)) }},
      images: imageContracts,
      boxes: entries.map((entry) => ({{ selector: entry.selector, label: entry.label, x: Math.round(entry.x), y: Math.round(entry.y), w: Math.round(entry.w), h: Math.round(entry.h) }}))
    }});
    document.body.appendChild(pre);
  }};
  ready(() => {{
    keepOnly();
    waitForImages().then(() => {{
      positionPins();
      requestAnimationFrame(() => requestAnimationFrame(runLayoutAudit));
    }});
  }});
}})();
</script>
</body>
</html>
"""


def render_html(output_dir: Path, deck: Deck | None = None) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    deck = deck or DEFAULT_DECK
    cache_dir = output_dir / "asset-cache"
    html_path = output_dir / f"{slug(deck.deck_id or deck.title)}.html"
    html_path.write_text(build_html(deck, cache_dir), encoding="utf-8")
    return html_path
