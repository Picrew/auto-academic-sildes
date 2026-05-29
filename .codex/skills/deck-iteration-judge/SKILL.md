---
name: deck-iteration-judge
description: Review rendered contact sheets for HTML-first academic or technical decks, deciding what to keep, discard, and change next based on aesthetics, readability, evidence clarity, and slide-to-slide cadence.
---

# Deck Iteration Judge Skill

Use after each rendered contact sheet or screenshot pass. Judge the artifact, then prescribe the smallest useful next iteration.

## Workflow

1. Open the latest `html-contact-sheet.png`; inspect individual slide images when a thumbnail hides details.
2. Scan the whole deck first for cadence: repeated layouts, pacing, section turns, palette rhythm, and density changes.
   - Check `layout-audit-report.md` for `Deck Cadence`; if it reports fewer than three composition types or repeated layouts, fix cadence before polish.
   - For broad style exploration, prefer `uv run academic-deck compare-grammars --deck <deck.yaml> --out <out>` and judge the stacked `grammar-comparison-overview.png`.
3. Review each slide for claim readability, evidence legibility, crop, hierarchy, alignment, contrast, and text fit.
4. Classify issues by impact:
   - `Must fix`: unreadable text, broken crop, overlap, blank/failed render, misleading evidence, severe contrast failure.
   - `Should fix`: weak hierarchy, cramped spacing, repetitive composition, unclear annotation, decorative image.
   - `Taste pass`: color balance, crop refinement, type scale, rhythm, polish.
5. Decide what to preserve before proposing changes. Good choices should not be churned away.
6. Recommend one next pass with concrete slide numbers and CSS/content actions.
7. Score the pass on five dimensions: philosophy alignment, visual hierarchy, craft quality, functionality, originality.

## Judgment Rules

- A slide passes only if the viewer can name the claim and the proof in a few seconds.
- Evidence beats decoration. If an image does not prove, orient, or compare, remove or replace it.
- Prefer fewer, clearer objects over dense mosaics unless the slide's job is explicit comparison.
- Repetition is acceptable as a system; repetition without progression is a problem.
- A deck of five or more slides should usually contain at least three composition cadences, such as cover, proof-led, matrix, artifact-content, or synthesis.
- A grammar bake-off only counts as diverse when composition sequences differ; palette-only changes are not meaningful iteration.
- Section breaks should reset attention without feeling like unrelated deck templates.
- Captions and annotations must be readable at contact-sheet scale or clearly worth opening full-size.
- Do not accept text that barely fits. Tighten copy, resize within the system, or change the layout.
- Treat wrapped-line collision or `text-line-height-tight` inside a heading, bullet, caption, metric, or footer as a hard layout failure, not a typography quirk.
- Treat a screenshot inserted without enough clearance, readable source pixels, and a specific caption/source line as unfinished evidence even when the slide looks visually polished.
- Treat foreground pseudo-element overlays, raw/untyped images, non-cover bare `image` fields, and top-level/evidence image mismatches as hard source problems, not visual quirks.
- If a proof image is underfeatured, first try `layout: proof-showcase` or a tighter crop; if an artifact panel is decorative rather than readable, try `layout: artifact-showcase`.
- Watch for generic AI flavor: glossy gradients, floating cards, vague diagrams, random glow, placeholder screenshots, and ornamental icons.
- Preserve strong negative space, distinctive crops, clear comparison axes, and memorable proof surfaces.
- DOM layout passing is not enough. If a content slide visually feels below roughly 55% useful fill, call it underfilled even when the audit passes.
- A zero-warning render is still not a taste pass. Manually check whether the proof or artifact image is visually dominant enough for its claim; if the evidence feels subordinate to the atmosphere, enlarge the source surface or choose a proof-led composition.
- In grammar bake-offs, treat two pale serif/editorial systems as close siblings unless their composition sequence, proof scale, caption behavior, and density rhythm differ materially.
- Treat the `Shortlist Diversity` table as part of the review. A shortlist with repeated style families is a warning even when every row scores 100; prefer fewer genuinely different directions over a full list of siblings.
- Summary cards without source artifacts still carry AI flavor. Tie claims to papers, repos, project pages, figures, benchmark surfaces, or homepage evidence.
- Empty module boxes are AI flavor. Every box, card, table cell, or rail must act as evidence, comparison axis, timeline/genealogy, method component, or conclusion anchor.

## Output

Report in this order:

1. `Keep`: slide numbers and decisions worth preserving.
2. `Discard`: elements, crops, layouts, or treatments to remove.
3. `Must fix`: blocking readability or render problems.
4. `Scores`: five scores out of 10 for philosophy, hierarchy, craft, functionality, originality.
5. `Density`: visual fill judgment and proof-surface judgment.
6. `Next pass`: 3-7 concrete edits, each tied to slide numbers or shared CSS.
7. `Stop condition`: what must be true after the next render to stop iterating.
