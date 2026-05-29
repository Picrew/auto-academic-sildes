---
name: html-first-deck
description: Build tasteful HTML-first slide decks and export them to PPTX when visual fidelity matters more than native editability. Use for high-design academic, technical, profile, demo, or evidence-heavy slides.
---

# HTML-First Deck Skill

Use HTML as the design source of truth. Treat PPTX as an export format.

## Workflow

1. Build or edit `deck.yaml`.
2. Run `uv run academic-deck check --deck <deck.yaml> --out <out>`.
3. Run `uv run academic-deck evidence --deck <deck.yaml> --out <out>`.
4. Run `uv run academic-deck html-pptx --deck <deck.yaml> --out <out>`.
5. Inspect `html-contact-sheet.png`.
6. If the user needs editable shapes, also run `uv run academic-deck build --deck <deck.yaml> --out <out>-native --fail-on-layout`.

## Rules

- HTML route is judged first for taste, spacing, evidence readability, and image crop.
- PPTX-native is a secondary delivery route, not the design authority.
- Avoid one fixed template. Select a visual grammar before writing slides.
- Evidence pages should use large readable proof surfaces.
- Layout audit hard errors for `element-overlap`, `text-block-overlap`, `text-block-clearance-tight`, `text-line-overlap`, `text-line-height-tight`, `text-self-overlap`, `title-wrap-too-deep`, `subtitle-wrap-too-deep`, `text-clearance-tight`, `text-clipped`, `text-image-overlap`, `text-image-clearance-tight`, `proof-notes-image-overlap`, `artifact-notes-image-overlap`, `notes-image-clearance-tight`, `figure-caption-overlap`, `figure-caption-clearance-tight`, text/container/viewport overflow, missing proof images, raw/untyped inserted images, SVG/canvas/background evidence outside audited channels, missing rendered image contracts, missing image crops, missing image caption/source markers, clipped callouts, pins outside rendered source images, foreground pseudo-element overlays, unsupported image fit modes, severe letterboxing, tiny proof/artifact surfaces, too-small rendered source pixels, or excessive proof/artifact upscaling must be fixed before export is accepted.
- When text and images compete, fix the semantic layout before cosmetic polish: shorten copy, switch to `proof-showcase`/`artifact-showcase`, choose a tighter crop, or remove the image. Do not mask collisions with smaller unreadable text.
- Slides with proof or artifact images have stricter source text budgets. Keep image-backed pages to the inspected claim, compact caption/source, and at most three short bullets before trying CSS repairs.
- Image-backed pages also have a combined module budget before render: bullets, metrics, labels, and callouts are counted together. If proof/artifact slides exceed that budget, split the slide or remove a module family instead of hoping CSS can make the overlap disappear.
- Hard gate means issue type, not only raw severity label; if one of those hard-gate types appears as a warning, still treat it as blocking.
- Treat `audit-missing` as infrastructure failure, not a pass. Re-run strict export; the compiler retries Chrome audit internally, so persistent missing audit means the variant is not accepted.
- Treat `screenshot-timeout` and `screenshot-failed` as browser infrastructure failures. In `compare-grammars` they should remain visible as failed variant rows while other grammars continue, so do not discard the whole bake-off without reading `GRAMMAR_COMPARISON.md`.
- Treat `proof-image-small`, `proof-image-rendered-small`, `proof-image-letterboxed`, `artifact-image-rendered-small`, `artifact-image-letterboxed`, `artifact-role-underfeatured`, `callout-overlap`, `content-underfilled`, `useful-fill-low`, `proof-caption-missing`, `proof-caption-generic`, `artifact-caption-generic`, `caption-text-too-small`, `caption-contrast-low`, `label-contrast-low`, `decorative-image-too-small`, and `cover-image-letterboxed` warnings as crop, role, density, source-context, caption/readability, label readability, or slot-design problems, not cosmetic warnings. With `--fail-on-layout`, strict image/density/readability warnings fail the export, and quality-report errors stop before screenshots are accepted.
- Read the `Image Contracts` table in `layout-audit-report.md` after every strict render. Proof/artifact rows must show a role, loaded status, rendered source pixels, useful visible area, slot use, and crop/caption/source status before the image is considered inserted correctly.
- For repo, UI, paper, table, benchmark, project-page, and homepage screenshots, treat the source-heavy artifact target as about 980x540 rendered source pixels or better. Below roughly 820x460 is a hard image failure; between those values is still a repair candidate unless the slide is explicitly decorative.
- Compact evidence layouts should not carry visible proof-note lists. Prefer pins plus a specific caption/source line and side-rail bullets; use visible callout notes only on roomy proof-showcase pages where the audit preserves clearance.
- Treat `title-wrap-deep` and `subtitle-wrap-deep` warnings as pre-overlap warnings. The slide may look acceptable on one machine, but the title/subtitle is using too much vertical budget and should be shortened or split before delivery.
- Quality-report errors stop every export route, even when `--skip-layout-audit` is used for fast visual exploration.
- If an evidence slide's screenshot or figure is too small, set `layout: proof-showcase` in `deck.yaml`; if a content slide's source artifact must be readable, set `layout: artifact-showcase`. Treat these as semantic safety intents: they request more proof scale while the active grammar chooses the actual composition, so grammar bake-offs should still look visually different.
- Every inserted image must travel through an `evidence:` object or the cover identity channel. Do not add raw HTML `<img>` tags or bare evidence-slide `image:` fields; they bypass crop, caption, source, and clearance checks.
- Do not use CSS `background-image: url(...)` for slide visuals. The strict audit rejects it even inside proof/artifact/cover regions because it cannot measure source pixels, crop, caption, or clearance.
- Treat non-cover bare `image:` fields and missing evidence crops as blocking quality failures. A screenshot, figure, paper page, repo page, or product crop needs an `evidence:` contract with `evidence.image`, crop, caption, and source before rendering. Use `{x: 0, y: 0, w: 1, h: 1}` only when the image file is already a slide-scale crop.
- Treat full-frame source-heavy screenshots as suspect. Web pages, repos, papers, tables, dashboards, benchmarks, homepages, and UI captures need a local crop when their aspect ratio does not fit a stable slide slot; otherwise the quality gate should reject them before rendering.
- A non-cover top-level `image` can only mirror the exact same file as `evidence.image`; mismatches fail. Plain cover `image` values are identity anchors, not research proof. If a cover uses `evidence:`, it still needs crop, caption, and source.
- Crop and callout coordinates must be finite normalized numbers. NaN/infinity is a source error, not a renderer issue.
- More than three callouts is a source error; do not let the renderer silently drop extra pins.
- Over-budget bullets, metrics, and labels are source errors; the renderer must not silently drop content. Split the slide, turn it into a matrix, or move detail to notes.
- A wide screenshot-like cover image must use `evidence.image`, crop, caption, and source. Bare cover `image` is only for compact identity anchors.
- Unknown `visual_grammar` values fail in `check`, `html-pptx`, `build`, and `compare-grammars`; fix typos instead of relying on fallback behavior.
- Treat dense Chinese/Japanese/Korean copy as a layout risk even without spaces. If `quality-report.md` reports an over-budget title, bullet, caption, metric, or label, rewrite or split the slide before trying CSS fixes.
- Do not combine `--fail-on-layout` with `--skip-layout-audit`; strict delivery requires the browser DOM audit.
- If strict `html-pptx` or `build` fails, treat `DELIVERY_BLOCKED.md` and `.blocked.pptx` / `.blocked.pdf` artifacts as proof the run is review-only, not deliverable.
- Native PPTX/Beamer `build --fail-on-layout` uses the HTML render as a proxy gate for source safety and overlap. It still needs native contact-sheet inspection before final delivery.
- Keep cover thumbnails as identity anchors; if the audit reports `decorative-image-too-small`, either enlarge the identity crop or remove it.
- Keep metric cells short. The renderer reserves separate value and label rows; long metric labels should become bullets or matrix rows.
- Empty bullets, labels, metrics, bento cells, and evidence boxes are invalid. Remove the module or give it a real project, metric, source, citation, or artifact.
- The same homepage/screenshot should not appear more than twice unless the crop and slide job change materially.
- Run `compare-grammars --fail-on-layout` on at least two materially different decks before promoting a grammar or workflow change. Use `--grammars highsense-20` for the first anti-template pass when the user asks for high-end web/academic taste; use the default 42-grammar sweep for broader regression. Promote only variants with zero blocking layout errors.
- In `GRAMMAR_COMPARISON.md`, accept only the `Recommended Shortlist` as ready for taste review. Rows with decorative or letterboxed cover warnings are cover-crop repair candidates, not final shortlist entries. Treat `Image Revision Queue` entries as promising but not ready; they need tighter crops, larger proof layouts, or different slots before export.
- Follow `Repair Hints` before rerendering a queued grammar. They map warnings back to slide titles, current images, existing crops, and layout intents.
- For multi-step repair, run `uv run academic-deck repair-plan --manifest <out>/GRAMMAR_REPAIR_HINTS.json --out <out>` and work from `DECK_REPAIR_PLAN.md`.
- To create the next candidate, run `uv run academic-deck repair-draft --deck <deck.yaml> --manifest <out>/GRAMMAR_REPAIR_HINTS.json --out <draft-out>`. By default it pins a clean shortlisted grammar when available; with `--visual-grammar`, it repairs that specific variant. Always rerender the draft with `--fail-on-layout`.
- Do not let a visually clean variant pass just because it has zero blocking errors; `proof-image-small`, `artifact-small`, and letterbox warnings mean the inserted image is not doing enough evidence work.
- Do not let a visually clean variant pass if the useful-fill gate fails or a source-heavy artifact is underfeatured. A repo, UI, table, paper, project page, benchmark, or homepage screenshot must be readable at contact-sheet scale, not only present in the DOM.
- If the user asks for editable PPTX/Beamer via `build`, still read the generated `layout-audit-report.md`; native export now stops on quality errors and inherits the HTML overlap/image audit.

## Commands

```bash
uv run academic-deck html-pptx --deck examples/tech-review/deck.yaml --out outputs/html-first/tech-review
```

Read `docs/HTML_FIRST_ARCHITECTURE.md` and `docs/VISUAL_GRAMMARS.md` when choosing routes or style.
