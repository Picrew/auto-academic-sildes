---
name: academic-deck
description: Build tasteful academic and technical slides from a deck YAML using editable PPTX and Beamer routes.
---

# Academic Deck Compiler Skill

Work from `deck.yaml` and render the deck through the local compiler.

```bash
uv run academic-deck ingest --source /path/to/source-folder --out outputs/source-pack
uv run academic-deck check --deck examples/starter/deck.yaml --out outputs/starter
uv run academic-deck evidence --deck examples/starter/deck.yaml --out outputs/starter
uv run academic-deck html-pptx --deck examples/starter/deck.yaml --out outputs/starter-html
uv run academic-deck build --deck examples/starter/deck.yaml --out outputs/starter-native
uv run academic-deck package --deck examples/starter/deck.yaml --out outputs/starter
```

Review contact sheets, `layout-audit-report.md`, `judge-report.md`, `quality-report.md`, and `evidence-report.md` before declaring the deck done. HTML-first is the design source of truth when taste and fidelity matter; PPTX-native is for editability; Beamer is the backup for formal academic PDFs.

Keep the deck claim-led, evidence-first, and free of generic AI presentation language. Evidence-heavy slides should use explicit `evidence` metadata with crop, caption, source, and at most three callouts. Treat `text-line-overlap`, `text-self-overlap`, `text-image-overlap`, proof/artifact note-image collisions, `figure-caption-overlap`, `container-overflow`, `missing-proof-image`, clipped callouts, unsupported image fit modes, severe letterboxing, excessive proof/artifact upscaling, and tiny proof/artifact images as blockers, not polish. Treat `proof-image-small`, `proof-caption-missing`, `proof-caption-generic`, `artifact-caption-generic`, `caption-text-too-small`, `caption-contrast-low`, `decorative-image-too-small`, and `cover-image-letterboxed` warnings as crop, source-context, caption-readability, or image-role ranking signals before finalizing.
