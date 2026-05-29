---
name: design-context-protocol
description: Run a disciplined design-context workflow for HTML-first slides: verify facts, collect assets, choose visual grammar, make 2-slide showcases, compare directions, and critique outputs to avoid AI-slop.
---

# Design Context Protocol Skill

Use before building tasteful academic, technical, profile, product, or evidence-heavy slides.

## Workflow

1. Verify facts for named people, papers, products, projects, dates, versions, and claims.
2. Build a source pack with public pages, paper/project links, screenshots, figures, and candidate images.
3. Choose a visual grammar from `docs/VISUAL_GRAMMARS.md`; if unclear, create three directions and render small demos.
4. Make a two-slide showcase before scaling to the full deck:
   - cover or identity slide
   - evidence or dense content slide
5. Run HTML-first rendering and inspect the contact sheet.
6. Run layout audit; fix hard overlap, overflow, proof-size, and underfilled-page warnings.
7. Use five-dimensional critique: philosophy alignment, visual hierarchy, craft quality, functionality, originality.
8. Export PPTX only after the HTML source passes visual review.

## Rules

- Existing context beats blank-page invention.
- Real source imagery beats decorative placeholders.
- A homepage screenshot anchors identity; a paper figure, benchmark, project page, or UI state proves claims.
- Do not accept pages with tiny text floating in large unused space.
- Avoid AI clichés: purple-blue gradients, random glow, emoji icons, generic rounded cards, fake dashboards, and stock abstraction.

## Output

Return:

- `Source pack`: sources and selected assets.
- `Visual grammar`: chosen grammar and why.
- `Showcase`: two rendered slides or paths.
- `Review`: keep/fix/quick wins using the five dimensions.
- `Delivery`: HTML, contact sheet, layout audit, and PPTX path if exported.
