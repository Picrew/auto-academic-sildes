---
name: evidence-crop-composer
description: Select, crop, and annotate screenshots, paper figures, project pages, and result images so evidence slides prove claims with tasteful large proof surfaces.
---

# Evidence Crop Composer Skill

Use when a deck has screenshots, project pages, figures, charts, leaderboards, or PDFs that need to become slide evidence.

## Workflow

1. Identify the slide claim before choosing the image.
2. Choose the proof surface that directly supports that claim:
   - project page for identity or project scope
   - paper figure for method/result
   - benchmark/leaderboard for evaluation
   - UI state for product workflow
   - repo/readme only when implementation evidence matters
3. Crop to the meaningful region. Remove browser chrome, huge margins, repeated nav, and unreadable sidebars unless they are evidence.
4. Add at most three callouts. Each callout should name a judgment or signal.
5. Write a caption with what the viewer should inspect and a low-weight source line.
6. Re-render and verify the crop at contact-sheet and full-slide scale.
7. Check `layout-audit-report.md`; image overflow, unloaded images, missing proof images, clipped callouts, tiny proof/artifact images, and container overflow are hard failures.
8. Check `evidence-report.md`; `Evidence Mix` should show the deck is not relying on one repeated source type.

## Rules

- A pretty image that does not prove the claim is decorative and should be removed.
- Put the source image in `evidence.image` for every non-cover slide. Do not rely on a top-level `image` field except for a cover identity anchor; if legacy data keeps both fields, they must point to the same file.
- Every non-cover evidence crop needs `image`, `crop`, `caption`, and `source`. A full-frame crop is acceptable only when the source file is already a slide-scale crop.
- Crop and callout `x`, `y`, `w`, and `h` values must be finite normalized numbers in the source image coordinate system.
- More than three callouts is invalid; the renderer should never hide extra pins by truncating them.
- Avoid portraits as proof unless the slide is about identity.
- Prefer one large, inspectable image over several tiny screenshots.
- Crop first; scale second. Do not make unreadable images bigger without selecting the right region.
- Watch the rendered visible-pixel area, not just the `<img>` box. Heavy letterboxing means the crop or slot shape is wrong.
- Callout pins are positioned against the rendered source-image pixels after `object-fit: contain`; if the crop letterboxes heavily, pin positions can fail the audit even when x/y values look valid.
- Evidence crops should generally be at least 1000x560 effective pixels for text-heavy screenshots. Source-heavy proof crops below about 900x500 and source-heavy artifact crops below about 820x460 are rejected before render; 640x360 is only the absolute floor for simple non-text proof imagery.
- When a page is long, compose a local crop or use a figure/table close-up instead of a full-page screenshot.
- In HTML-first decks, ordinary content slides with `image`/`evidence` become artifact panels. Use this for source texture only when the crop is readable.
- Do not let callout pins cover the key text or figure legend; move the pin or shorten the annotation.
- Keep source types diverse. Identity homepage, repo, project page, benchmark, and paper/result figure each serve different slide jobs.

## Output

Return:

- `Selected evidence`: file/source and why it proves the claim.
- `Crop`: normalized `x`, `y`, `w`, `h` values or a redraw instruction.
- `Callouts`: 1-3 pin texts.
- `Caption`: short caption plus source.
