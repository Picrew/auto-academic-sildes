---
name: visual-grammar-selector
description: Select varied tasteful visual grammars for HTML-first academic and technical decks so outputs do not look like one repeated template.
---

# Visual Grammar Selector Skill

Pick one grammar before writing slides:

- `editorial-profile`
- `swiss-systems`
- `dark-lab-notebook`
- `paper-atlas`
- `keynote-evidence-wall`
- `highsense-gallery`
- `academic-homepage-grid`
- `prism-dossier`
- `fathom-research-brief`
- `jetset-theory-grid`
- `monograph-review`
- `broadside-lab`
- `catalog-atelier`
- `evidence-atelier`
- `atlas-marginalia`
- `systems-field-manual`
- `lab-trace-ledger`
- `object-study-wall`
- `forest-editorial-brief`
- `cobalt-research-grid`
- `vellum-research-note`
- `mono-ink-ledger`
- `neo-grid-lab`
- `prism-clean-room`
- `prism-publication-stack`
- `ia-research-archive`
- `pentagram-gridnote`
- `takram-research-system`
- `stamen-data-map`
- `couture-exhibition`
- `huashu-editorial-lab`

Read the matching `templates/<grammar>/DESIGN.md` before rendering.

Use `forest-editorial-brief`, `object-study-wall`, `evidence-atelier`, `prism-clean-room`, or `takram-research-system` as the high-taste public researcher/profile defaults. Use `academic-homepage-grid` or `prism-dossier` as conservative public profile defaults. Use `atlas-marginalia` or `ia-research-archive` when a scholarly profile has enough homepage, paper, or project evidence. Use `cobalt-research-grid` or `systems-field-manual` for tool-use, API, benchmark, and infrastructure decks.

Use `monograph-review`, `prism-publication-stack`, or `ia-research-archive` when a profile feels too ordinary or card-like and needs PRISM/Information-Architects density. Use `catalog-atelier` when the deck needs a warmer curated research-gallery rhythm. Use `couture-exhibition` when high-end web/editorial proof plates fit the content. Use `broadside-lab`, `pentagram-gridnote`, or `huashu-editorial-lab` when a systems/profile talk needs typographic stage presence without gradients or generic AI tech styling. Use `stamen-data-map` when project or benchmark evidence reads like an ecosystem or terrain.

Use `evidence-atelier` or `object-study-wall` when source artifacts are strong but the deck feels pasted together. Use `forest-editorial-brief` when a profile needs warmth and editorial maturity without decoration. Use `vellum-research-note` for formal research notes, seminars, and defenses. Use `mono-ink-ledger` for handout/dossier decks. Use `neo-grid-lab` only for demo/product/engineering decks that can tolerate a loud grid. Use `lab-trace-ledger` when agent/RL material needs a dark research mood without generic neon AI flavor.

The current default bake-off covers 28 grammars. It favors `forest-editorial-brief`, `object-study-wall`, `evidence-atelier`, `cobalt-research-grid`, `prism-clean-room`, and `takram-research-system` as the high-taste default pool; keeps `academic-homepage-grid` and `prism-dossier` as conservative defaults; treats `prism-publication-stack`, `vellum-research-note`, `mono-ink-ledger`, `atlas-marginalia`, `ia-research-archive`, `monograph-review`, `paper-atlas`, `catalog-atelier`, and `fathom-research-brief` as formal/dossier special cases; and treats `neo-grid-lab`, `jetset-theory-grid`, `pentagram-gridnote`, `huashu-editorial-lab`, `couture-exhibition`, `keynote-evidence-wall`, and `broadside-lab` as deliberate resets, not defaults. Penalize proof/artifact scale, rendered-pixel, callout, underfilled-slide, caption/source, and decorative-cover warnings in ranking even when they do not block export.

Reject empty modules and repeated artifacts before judging taste. Labels, metrics, bento cells, and evidence boxes need real content; the same homepage/screenshot should not appear more than twice unless the crop and slide job change.

## Composition Profiles

Do not judge variety from `visual_grammar` alone. Check `layout-audit-report.md` for named compositions such as:

- `cover-source-rail`: academic identity/source rail.
- `cover-title-wall`: large title with small source surface.
- `cover-poster-grid`: bold typographic cover.
- `proof-stage`: claim/sidebar plus dominant proof surface.
- `proof-atlas-spread`: proof-first spread with notes on the side.
- `proof-dossier`: homepage-style proof and source context.
- `artifact-rail` / `artifact-dossier`: normal content slide carrying a real source artifact.
- `matrix-ledger`: scan-friendly table/ledger composition.

A pass is not diverse if every candidate has the same composition sequence with only palette changes.
