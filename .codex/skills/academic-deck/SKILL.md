---
name: academic-deck
description: Build and refine claim-led academic or technical slide decks with Academic Deck Compiler. Use when the user asks for tasteful research slides, PPTX, Beamer, paper talks, technical portfolios, or multi-agent slide iteration.
---

# Academic Deck Compiler Skill

Use the local repo as a compiler, not as a final-PPT patching surface.

## Workflow

1. Read source material and identify the central claim. For large folders, run `uv run academic-deck ingest --source <source-folder> --out <source-pack>` first.
2. Create or edit `deck.yaml`.
3. Run `uv run academic-deck check --deck <deck.yaml> --out <output-dir>`.
4. Run `uv run academic-deck evidence --deck <deck.yaml> --out <output-dir>` to audit image choices.
5. Run `uv run academic-deck html-pptx --deck <deck.yaml> --out <output-dir>` when visual fidelity matters.
6. Run `uv run academic-deck build --deck <deck.yaml> --out <output-dir>-native --fail-on-layout` when editable PPTX or Beamer are needed for delivery.
7. Inspect `html-contact-sheet.png`, `pptx-contact-sheet.png` if generated, and `beamer-contact-sheet.png`.
8. Read `layout-audit-report.md`, `judge-report.md`, `quality-report.md`, and `evidence-report.md`.
9. Prefer HTML-first for taste and PPTX-native for editability.
10. Revise the YAML, evidence crops, renderer, or assets; rerender.
11. Run `uv run academic-deck package --deck <deck.yaml> --out <output-dir>` for a review bundle.

## Taste Rules

- Use action titles.
- One judgment per slide.
- Evidence images must prove a claim.
- Use `evidence.image`, finite `crop`, `caption`, `source`, and at most three finite-position callouts for proof slides.
- Crop or redraw unreadable figures.
- Treat `element-overlap`, `text-line-overlap`, `text-line-height-tight`, `text-self-overlap`, `text-clearance-tight`, `text-clipped`, `text-image-overlap`, text-image clearance failures, proof/artifact note-image collisions, `figure-caption-overlap`, `figure-caption-clearance-tight`, `container-overflow`, `viewport-overflow`, `missing-proof-image`, missing rendered image contracts, missing image crops, missing caption/source markers, clipped callouts, unsupported image fit modes, severe letterboxing, foreground pseudo overlays, excessive proof/artifact upscaling, tiny proof/artifact images, and too-small rendered source pixels as blockers, not polish. Any real text-on-image intersection above the anti-aliasing tolerance is a failed slide.
- Use image slots as proof surfaces: every inserted proof/artifact image needs enough rendered source pixels, a specific caption/source line, and clearance from all text. A pretty screenshot that cannot be inspected is a failed slide.
- For source-heavy screenshots such as repos, UIs, tables, benchmarks, paper pages, project pages, and homepages, aim for about 980x540 rendered source pixels or better. Before rendering, proof crops below about 900x500 and artifact crops below about 820x460 are errors; after rendering, anything near or below 820x460 should be repaired as a failed source surface, even if the slide looks balanced.
- In compact proof layouts, do not rely on visible callout-note lists; they are a common overlap source. Use pins plus caption/source and side-rail claims, or move the slide to a roomier proof-showcase layout.
- Non-cover screenshots, figures, project pages, repos, and product crops must use `evidence.image`; a top-level non-cover `image` is only a legacy mirror when it exactly matches `evidence.image`. Plain cover `image` values are identity anchors, not proof.
- Unknown `visual_grammar` values fail; choose from `docs/VISUAL_GRAMMARS.md` instead of relying on fallback behavior.
- More than three callouts is a quality error. Keep only the pins that directly help inspect the crop.
- Bullets, metrics, and labels that exceed the renderer's visible budget are quality errors. Split the slide or switch to a matrix instead of relying on silent truncation.
- On any proof/artifact slide, bullets, metrics, labels, and callouts are also counted as one combined image-adjacent module budget. A readable image gets priority; overloaded image slides must be split before rendering.
- Wide screenshot-like cover images must use an `evidence:` crop/caption/source contract. Bare cover `image:` is reserved for compact identity anchors.
- Quality-report errors stop all render/export routes; fast preview may skip DOM geometry, but it cannot bypass invalid source contracts.
- Treat `proof-image-small`, `proof-image-rendered-small`, `artifact-image-rendered-small`, `artifact-role-underfeatured`, `callout-overlap`, `content-underfilled`, `useful-fill-low`, `proof-caption-missing`, `proof-caption-generic`, `artifact-caption-generic`, `caption-text-too-small`, `caption-contrast-low`, `decorative-image-too-small`, and `cover-image-letterboxed` warnings as ranking signals: fix crops, density, callout placement, caption/source context, caption readability, or image roles before calling a design final.
- Source-heavy artifacts need a larger safety threshold than identity imagery. Repos, UIs, tables, benchmarks, paper pages, project pages, and homepages must be readable as evidence surfaces, not decorative thumbnails.
- Avoid AI-template decoration.
- Keep logos and avatars small.
- Contact-sheet review beats automated scores.
- Select a visual grammar before rendering; do not make every deck look identical.

## Useful References

- `docs/IR.md`
- `docs/AGENT_WORKFLOW.md`
- `docs/IMAGE_EVIDENCE.md`
- `docs/HTML_FIRST_ARCHITECTURE.md`
- `docs/VISUAL_GRAMMARS.md`
- `docs/VISUAL_QA.md`
- `templates/tech-editorial/DESIGN.md`
