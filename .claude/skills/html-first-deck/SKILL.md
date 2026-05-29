---
name: html-first-deck
description: Build tasteful HTML-first slide decks and export them to PPTX when visual fidelity matters more than native editability.
---

# HTML-First Deck Skill

Use HTML as the design source of truth and PPTX as an export format.

```bash
uv run academic-deck check --deck <deck.yaml> --out <out>
uv run academic-deck evidence --deck <deck.yaml> --out <out>
uv run academic-deck html-pptx --deck <deck.yaml> --out <out>
```

Inspect `html-contact-sheet.png` first. If an editable deck is also required, run the native route separately with `uv run academic-deck build`.

Layout audit hard errors for `text-line-overlap`, `text-self-overlap`, `text-clearance-tight`, `text-clipped`, `text-image-overlap`, `text-image-clearance-tight`, `proof-notes-image-overlap`, `artifact-notes-image-overlap`, `notes-image-clearance-tight`, `figure-caption-overlap`, `figure-caption-clearance-tight`, text/container overflow, missing proof images, clipped callouts, pins outside rendered source images, unsupported image fit modes, severe letterboxing, tiny proof/artifact surfaces, too-small rendered source pixels, or excessive proof/artifact upscaling must be fixed before export is accepted. Hard gate means issue type, not only raw severity label; if one of those hard-gate types appears as a warning, still treat it as blocking. Treat persistent `audit-missing` as an infrastructure failure, not a pass. Treat proof/artifact letterboxing, small proof images, rendered-pixel warnings, callout overlap, underfilled slides, missing/generic proof or artifact captions, low-readability caption styling, decorative cover thumbnails, and letterboxed cover images as crop, role, density, or source-context problems. With `--fail-on-layout`, quality-report errors stop before screenshots are accepted.

If an evidence slide's screenshot or figure is too small, set `layout: proof-showcase` in `deck.yaml`; if a content slide's source artifact must be readable, set `layout: artifact-showcase`. Treat these as semantic safety intents: they request more proof scale while the active grammar chooses the actual composition, so grammar bake-offs should still look visually different.

Keep metric cells short: value first, label second. Long metric labels should become bullets or matrix rows. Empty bullets, labels, metrics, and bento modules are invalid. Before promoting renderer or grammar changes, run `compare-grammars --fail-on-layout` on at least two materially different source decks. The default bake-off now covers 28 visual grammars; promote only variants with zero blocking layout errors and zero strict image/density warning gates.

In `GRAMMAR_COMPARISON.md`, accept only the `Recommended Shortlist` as ready for taste review. Rows with decorative or letterboxed cover warnings are cover-crop repair candidates, not final shortlist entries. Treat `Image Revision Queue` entries as promising but not ready; they need tighter crops, larger proof layouts, or different slots before export. Follow `Repair Hints` before rerendering a queued grammar; they map warnings back to slide titles, current images, existing crops, and layout intents. For multi-step repair, run `uv run academic-deck repair-plan --manifest <out>/GRAMMAR_REPAIR_HINTS.json --out <out>` and work from `DECK_REPAIR_PLAN.md`, then run `uv run academic-deck repair-draft --deck <deck.yaml> --manifest <out>/GRAMMAR_REPAIR_HINTS.json --out <draft-out>` to create a non-destructive candidate deck. By default the draft pins a clean shortlisted grammar when available; with `--visual-grammar`, it repairs that specific variant. Always rerender the draft with `--fail-on-layout`. Do not let a clean-looking variant pass when `proof-image-small`, `artifact-small`, decorative-cover, or letterbox warnings show that the inserted image is not doing enough evidence work.

Read `docs/HTML_FIRST_ARCHITECTURE.md` and `docs/VISUAL_GRAMMARS.md` when choosing the route or visual grammar.
