---
name: beautiful-html-template-deck
description: Use beautiful-html-templates as a tone-first reference or HTML template source for tasteful academic, technical, profile, and product decks.
---

# Beautiful HTML Template Deck Skill

Use this skill before choosing a visual grammar when the brief asks for less
ordinary HTML-first slides or explicitly mentions `beautiful-html-templates`.

## Workflow

1. Read `vendor/beautiful-html-templates/index.json` when the local checkout
   exists. If it does not, use the compiler's built-in academic-safe fallback.
2. Generate a tone-first shortlist:

```bash
uv run academic-deck template-shortlist \
  --brief "<occasion + mood + content density>" \
  --out outputs/template-shortlist
```

3. Pick three genuinely different candidates by mood, density, and formality.
4. Map the chosen template family into the renderer:
   - `signal` -> `signal-intelligence-brief`
   - `raw-grid`, `block-frame`, `neo-grid-bold` -> `raw-grid-research` or `neo-grid-lab`
   - `stencil-tablet` -> `stencil-field-tablet`
   - `vellum` -> `vellum-research-note`
   - `monochrome` -> `mono-ink-ledger`
   - `editorial-forest`, `cartesian`, `grove`, `mat` -> `forest-editorial-brief`, `catalog-atelier`, or `object-study-wall`
   - `cobalt-grid`, `blue-professional` -> `cobalt-research-grid` or `takram-research-system`
   - `broadside`, `bold-poster` -> `broadside-lab` or `pentagram-gridnote`
5. Render with `compare-grammars --fail-on-layout`; reject any final winner
   with hard overlap, clipping, container overflow, missing image contracts, or
   strict image/density warnings.

## Guardrails

- Treat the template library as a closed visual system. Borrow layout logic,
  rhythm, palette discipline, and component grammar; do not mix decorative
  motifs from several templates into one deck.
- For academic decks, prefer source/proof surfaces over ornamental screenshots.
- Playful templates are allowed only when the occasion asks for that tone.
- Use the vendor `AGENTS.md` only when building a bespoke HTML deck directly
  from a template; for Academic Deck Compiler outputs, use the mapping above
  and keep the DOM audit as the source of truth.

