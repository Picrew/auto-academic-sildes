# Image And Evidence Rules

Good academic slides use images as proof, not ornament.

## Asset Priority

1. Experimental result figures with readable axes, model names, and metrics.
2. System architecture diagrams with clear inputs, modules, and outputs.
3. Real product screenshots with visible workflow state.
4. Data or process screenshots that reveal a failure or quality loop.
5. Logos, avatars, and decorative images.

Only the first four categories can be primary evidence. Logos and avatars are identity markers.

## Selection Questions

For every image, answer:

- What claim does this prove?
- Which region matters?
- Is it readable in a 1920x1080 preview?
- Does it need a crop, callout, or native redraw?
- Is the source or metric clear enough for an academic audience?

If the answer to the first question is vague, drop the image.

Run the asset audit before layout work:

```bash
uv run academic-deck evidence --deck examples/my-talk/deck.yaml --out outputs/my-talk
```

The report is intentionally conservative. It labels logos and avatars as identity markers, surfaces unused candidate figures, summarizes crop size, and reminds the agent when a chart should be redrawn rather than pasted.

## Insertion Gates

Images enter the deck through an explicit role:

- `proof`: primary evidence on evidence, loop, or product slides.
- `artifact`: readable source surface on an ordinary content slide.
- `cover`: small identity anchor only.

Non-cover images must be declared with an `evidence:` object that names the
image, crop, caption, and source. A bare `image:` on a content or evidence slide
is a structural error, because the renderer cannot audit proof role, source
pixels, caption specificity, or text-image clearance reliably. If the source
file is already pre-cropped for slide use, declare the intent explicitly with a
full-frame crop: `{x: 0, y: 0, w: 1, h: 1}`.

Do not use a full-frame crop as a shortcut for long source-heavy material. Web
pages, repos, papers, tables, dashboards, benchmarks, homepages, and UI captures
must be cropped to the readable claim region when their shape does not fit a
stable slide slot.

The image path belongs in `evidence.image`. Top-level `image` is only a cover
identity fallback; on non-cover slides it may exist only as a legacy mirror of
the exact same file in `evidence.image`. If `image` and `evidence.image` point
to different files, the deck fails before rendering so crop, caption, and audit
checks cannot target the wrong visual.

Cover images are not proof unless they use the full `evidence:` contract. A
plain cover `image` can establish identity or context, but it is reported as an
identity anchor rather than counted as evidence.

The HTML audit measures the rendered source-pixel box after `object-fit:
contain`, not just the outer frame. This matters because a screenshot can appear
large while most of its slot is letterboxed whitespace.

Hard failures:

- missing or unloaded primary proof image
- proof image too small to inspect
- artifact image too small to read
- image overflowing its slot
- title, bullet, caption, note, or footer text overlapping the proof/artifact slot
- text pressed against the proof/artifact slot with no visible safety gap
- unsafe multi-line caption, title, metric, or note line-height near the proof/artifact slot
- raw slide images that do not live inside `evidence:` / proof / artifact / cover channels
- SVG/canvas visuals used as slide evidence without a renderer-owned
  proof/artifact channel, and any CSS `background-image: url(...)` inside a
  slide
- non-cover `image:` fields without `evidence.image`
- non-cover `image:` / `evidence.image` mismatches
- non-cover evidence/artifact objects without an explicit `crop`
- crop or callout coordinates that are NaN, infinite, or outside the normalized source image
- source-heavy screenshots using an almost full-frame crop with a shape that will shrink into unreadable slide evidence
- more than three callouts on a single image
- cover `evidence:` objects missing crop, caption, or source
- proof or artifact image missing a caption or source line
- generic proof/artifact captions and low-readability caption styling in strict delivery mode
- callout pin outside the image slot
- callout pin placed in letterbox whitespace instead of on the source pixels

Warnings to fix before final polish:

- proof or artifact image small but not below the hard threshold
- proof or artifact slot heavily letterboxed
- cover image so small that it reads as decoration rather than identity evidence
- evidence crop below roughly 1000x560 effective pixels when text matters
- crop aspect ratio that does not match the chosen proof slot

## Cropping Rules

- Wide dense figures: crop to the key panel or rebuild the chart natively.
- Tall architecture screenshots: crop a local workflow path instead of shrinking the whole image.
- Product screenshots: show the part where a user decision or system state is visible.
- Heatmaps: use one panel and annotate two cells at most.
- Leaderboards: select representative models instead of showing the entire table.
- Homepages: crop to identity, project/publication rows, or evidence text; avoid full-page screenshots with unreadable margins.
- Portraits: use as identity anchors, not as the main proof for a research claim.

## Private Fixture Notes

Private screenshots, profile decks, and local asset caches are intentionally not documented in the public repository. Keep reusable evidence guidance generic; put person-specific crop notes in local ignored files.

## Best Evidence Page

```text
action title
one cropped evidence image declared in deck.yaml
two callouts max
one source or metric note
one implication
```

## YAML Pattern

```yaml
evidence:
  image: result-heatmap.png
  crop: {x: 0.62, y: 0.08, w: 0.34, h: 0.72}
  caption: Gap panel: the failure concentrates in a specific model and error type.
  source: Paper figure or project artifact, accessed 2026-05-30.
  callouts:
    - {x: 0.18, y: 0.22, text: spike}
    - {x: 0.72, y: 0.45, text: error cluster}
```

Cropping is normalized to the original image: `x`, `y`, `w`, and `h` are all in the `0..1` range. The PPTX renderer materializes crops into `asset-cache/`; the Beamer route reuses the same crop semantics.
