---
name: high-sense-renderer-critic
description: Critique HTML-first slide renderer outputs for template sameness, proof scale, color rhythm, layout repetition, and generic AI visual flavor.
---

# High-Sense Renderer Critic Skill

Use after `uv run academic-deck html-pptx` generates `html-contact-sheet.png`.

## Workflow

1. Open the contact sheet and, when needed, the individual `html-shots/slide-*.png`.
2. Judge deck-wide rhythm before judging individual slides. For competing grammars, run/read `compare-grammars` output, compare composition sequences, and start from `Recommended Shortlist`.
3. Check these renderer-level signals:
   - `proof_area`: evidence/product slides should give real proof the largest surface.
   - `layout_repetition`: the same composition should not run for many slides without a reason.
   - `palette_usage`: avoid one fixed hue or generic purple-blue gradients.
   - `dark_ratio`: dark pages should match grammar intent, not dominate by accident.
   - `caption_legibility`: captions and callouts should survive contact-sheet scale.
   - `source_surface`: portraits/logos/thumbnails should not replace evidence.
   - `deck_cadence`: read the layout audit cadence sequence and reject long runs of the same non-proof composition.
   - `hard_layout`: reject `text-line-overlap`, `text-image-overlap`, `text-image-clearance-tight`, proof/artifact note-image collisions, `figure-caption-overlap`, `figure-caption-clearance-tight`, `container-overflow`, `missing-proof-image`, `callout-outside-image`, unsupported image fit modes, severe letterboxing, excessive image upscaling, missing/generic image captions, low-readability caption styling, and image size errors before judging taste.
   - `image_slot`: letterboxed proof/artifact images usually need a tighter crop or a different slot shape.
   - `decorative_thumbnail`: cover thumbnails flagged as `decorative-image-too-small` are identity cues only; do not treat them as evidence.
   - `revision_queue`: entries in `Image Revision Queue` are not accepted variants; they are candidates for crop/layout repair.
   - `repair_hints`: follow slide-specific hints before rerendering; they identify whether the next change is crop, proof scale, artifact scale, or slide split.
   - `repair_plan`: use `DECK_REPAIR_PLAN.md` when available; it is the structured worklist for the next render loop.
   - `repair_draft`: use `deck.repair.yaml` from `repair-draft` for the next strict render when a manifest exists; it keeps image paths stable after moving into an output directory.
   - `conditional_shortlist`: shortlist entries with only decorative cover warnings can be judged for taste, but the cover crop still needs adjustment before delivery.
4. Decide whether the issue is content, crop, or CSS. Do not blur the diagnosis.

## Rules

- High-end slide design is usually better crop, scale, alignment, and restraint.
- Prefer `fathom-research-brief` and `jetset-theory-grid` when the material needs more systems/design structure; keep `academic-homepage-grid` for restrained profile identity pages.
- If a proof image is unreadable, ask for crop/redraw before accepting the slide.
- If the audit reports missing proof images, container overflow, text-line overlap, or clipped callouts, stop polish and fix the renderer/content first.
- Do not accept a slide where the image DOM box is large but the visible source pixels are tiny because of letterboxing.
- Do not accept a proof slide where the visible source pixels feel underfeatured even if the outer proof panel is large.
- If a manifest already contains a clean shortlist, prefer that draft before spending time repairing a weaker grammar.
- If a deck feels generic, change composition cadence before changing accent color.
- Passing overlap checks is not enough; cadence variety is a separate gate against one-template output.
- Passing strict warnings is not enough; if a proof surface reads as a polite inset rather than the slide's evidence protagonist, score functionality and hierarchy down and request a larger proof/artifact slot.
- Do not count palette changes as diversity. Distinct grammars need different grid logic, image scale, caption treatment, density rhythm, and slide cadence.
- Reject card piles, fake dashboards, ornamental glow, floating blobs, and source screenshots used as decoration.
- Reject empty boxes: every visual container must be evidence, comparison axis, timeline/genealogy, method component, or conclusion anchor.
- Preserve strong negative space, memorable proof surfaces, and clean comparison axes.

## Output

Return:

- `Keep`: renderer choices that work.
- `Renderer fixes`: CSS or layout changes.
- `Deck fixes`: content, crop, or evidence changes.
- `Verdict`: keep grammar, revise grammar, or discard grammar.
