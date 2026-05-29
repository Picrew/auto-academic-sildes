# Survey Decisions

This project keeps the best parts of the slide systems reviewed during planning without depending on all of them at runtime.

## What We Adopted

- From academic-pptx-skill: action titles, ghost-deck logic, citations/evidence discipline, and conclusion-over-thank-you endings.
- From ArcDeck and Auto-Slides: narrative planning, asset filtering, and critic/refiner loops.
- From frontend-slides and beautiful-html-templates: editorial composition, strong visual rhythm, and anti-template taste.
- From nbp_slides: separation between content intent and visual grammar.
- From pptx-from-layouts-skill: respect for editable PPTX and template/placeholder discipline.
- From Beamer/academic-slides: formal PDF route, typographic restraint, and reproducible handouts.

## What We Rejected For The Default Path

- Full-page image PPTX as the default. It can look beautiful, but it loses editability and is risky for small academic text.
- Generic AI presentation templates. They tend to create empty cards, gradients, and icon grids that make technical work feel shallow.
- Logo-heavy portfolio pages. Logos are provenance, not proof.
- Beamer as the main portfolio route. It is credible but often too polite and too flat for product or systems evidence.

## Current Architecture Choice

```text
deck.yaml
  -> quality checks
  -> PPTX-native renderer
  -> Beamer renderer
  -> contact sheets
  -> density judge + manual rubric
```

Future HTML work should appear as an optional evidence-panel renderer, not as a replacement for the deck IR. The goal is to bring HTML-level taste into PPTX while keeping the surrounding deck editable.

## Runtime Dependencies

The repo vendors selected projects for reference in `vendor/`, but the compiler only needs:

- Python
- `python-pptx`
- Pillow
- PyYAML
- PowerPoint for PPTX-to-PDF preview export
- `xelatex` and `pdftoppm` for Beamer and contact sheets
