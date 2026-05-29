# Design Context Protocol

This project should not generate slides from a blank generic prompt. Taste comes
from design context, source assets, and repeated visual judging.

## Reference Set

- High-sense web pages: study scale contrast, rich proof surfaces, and page-to-page rhythm.
- PRISM-like academic homepages: study identity rails, selected publication cards, compact news rows, and readable research density.
- Huashu Design: study the workflow discipline: verify facts, gather assets, make variants, and critique with explicit dimensions.
- Beautiful HTML Templates: study tone-first template selection via `index.json`, then map the chosen template family into a renderer grammar instead of mixing several template skins.

## Agent Steps

1. Verify current facts and public sources for specific people, papers, products, or projects.
2. Build a source pack: homepage, paper/project pages, representative screenshots, figures, repos, and publication metadata.
3. Select or create a visual grammar before drafting every slide.
   If tone is unclear, run `academic-deck template-shortlist --brief "<occasion + mood + content>" --out <out>` before grammar comparison.
4. Make a two-slide showcase: one cover/identity slide and one evidence/content slide.
5. Generate at least three visually distinct directions when the brief is vague; each direction should differ in composition profile, not only color.
6. For high-sense style exploration, run `compare-grammars --grammars highsense-20 --fail-on-layout` first, then inspect `grammar-comparison-overview.png`; failed candidates are repair evidence, while the final chosen grammar must be clean.
7. Render HTML and inspect `html-contact-sheet.png`.
8. Run `layout-audit-report.md`; fix hard overlap, text-line collision, container overflow, missing proof images, bad image slots, and proof-scale failures.
9. If an evidence or artifact slide fails proof scale, add a semantic safety `layout` in `deck.yaml` such as `proof-showcase` or `artifact-showcase` before touching decorative styling; the active grammar will choose the exact proof composition.
10. Use a five-dimension review: philosophy alignment, hierarchy, craft, functionality, originality.
11. Iterate one variable per pass: crop, density, typography, cadence, or palette.
12. Export PPTX only after the HTML source is visually stable.

## Layout Hard Gates

- Every renderer must treat overlap, text-line overlap, text-self-overlap, clipped text, text overflow, container overflow, viewport overflow, unloaded images, missing proof images, raw/untyped slide images, missing rendered image contracts, missing image crops, missing caption/source markers, image overflow, clipped callouts, note-image collisions, text-on-image intersections above the anti-aliasing tolerance, unsupported image fit modes, excessive proof/artifact upscaling, and tiny proof/artifact images as build failures.
- Text collision includes collisions inside one text block. A heading or bullet list whose wrapped lines overlap is a hard failure even if it does not collide with a neighboring element.
- Use CSS containment rules by default: `min-width: 0` inside grids, `overflow-wrap: anywhere` for text, fixed proof/artifact image windows, `object-fit: contain` for screenshots, and hidden overflow only inside bounded layout or image windows that are audited for scroll overflow.
- If a normal content slide needs a screenshot or figure, declare it as
  `evidence.image` with crop, caption, and source so it can render as an
  audited artifact panel. Do not use bare non-cover `image` fields or
  decorative thumbnails.
- Rendered proof/artifact figures must keep their typed insertion markers
  (`data-image-role`, crop, caption, and source flags). Losing those markers is
  an audit failure because the image can no longer prove how it entered the
  layout.
- Evidence-like slides need a dominant proof surface; content slides with screenshots need an artifact panel large enough to read at full-slide scale.
- Source-heavy screenshots, tables, repos, dashboards, paper pages, and homepages
  need enough actual crop pixels before insertion: use about 900x500 as the
  pre-render floor for proof and about 820x460 for artifact panels, then still
  verify rendered source pixels in the Image Contracts table.
- Letterboxed proof/artifact images are not style polish issues; crop tighter or change the slot shape until the visible pixels carry enough of the slide.
- Use `layout: proof-showcase` when the image is the argument and the default grammar gives too much space to bullets or metrics. Use `layout: artifact-showcase` when a content slide's screenshot should be read, not merely recognized. Treat both as safety intents; they should preserve grammar variety instead of collapsing every deck into one repeated showcase template.
- Audit all text surfaces, not just headlines: kicker, tags, label boards, spine labels, case rows, table cells, captions, callout notes, and footer text must fit without collision.
- Decks with five or more slides must show cadence variety: at least three composition types, and no three repeated non-proof layouts in a row.
- The renderer should expose `data-composition` so agents can audit actual layout cadence, not infer variety from slide kind alone.
- The DOM audit is a floor. A slide with no overlap can still fail if the crop does not prove the claim or if the page feels sparsely generated.

## Asset Rules

- Logo, portrait, homepage, project screenshots, and figures have different jobs. Do not swap them casually.
- For public profiles, homepage screenshots anchor identity; paper figures, project pages, and benchmark surfaces prove claims.
- Prefer 5 search passes, 10 candidate assets, 2 selected assets, each good enough to inspect.
- If an asset is weak, leave it out or crop tighter. Do not fill the deck with mediocre screenshots.
- Run the evidence report and read `Evidence Mix`; a polished profile should pair identity evidence with at least one work artifact such as a project page, repo, benchmark, or paper/result figure.
- Untyped evidence is a smell. Improve the filename, `evidence.caption`, or `evidence.source` until the next agent can tell why the image exists.

## Anti AI-Slop Rules

- Avoid purple-blue gradients, random glows, emoji decoration, fake dashboards, SVG people, and ornamental icons.
- Avoid giant slides with tiny text and more than half the canvas unused.
- Avoid nested cards. Use rails, bands, proof windows, publication rows, and typographic grouping.
- Do not draw empty modules. Every box, table cell, or rail should be evidence, comparison axis, timeline/genealogy, method component, or conclusion anchor.
- Use serif display faces with a restrained sans body when the deck needs academic taste.
- Use CSS Grid, `text-wrap: pretty`, consistent spacing, and real source imagery.
- DOM layout passing is a floor, not taste. A content slide can pass the audit and still feel empty.
- Avoid abstract summary cards when a paper figure, project page, repo surface, or benchmark screenshot can carry the same claim.

## Iteration Judge Output

Each design pass should end with:

- `Keep`: slide numbers and choices to preserve
- `Discard`: template-like elements or weak crops to remove
- `Scores`: five 10-point scores for philosophy, hierarchy, craft, functionality, originality
- `Density`: manual visual fill and proof-surface judgment
- `Next pass`: one variable to change, with concrete slide numbers

## Stop Condition

A pass is presentable only when:

- the viewer can read the claim at contact-sheet scale
- evidence-like slides have a large proof surface
- no hard layout audit errors remain
- content slides feel materially filled, usually around 55-65% useful visual density unless the grammar intentionally uses extreme negative space
- evidence slides have proof surfaces that dominate the slide
- the deck has at least two layout cadences
- the output does not resemble a generic AI PPT template
