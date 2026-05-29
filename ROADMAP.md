# Roadmap

## v0.1 - Working Compiler

- Editable PPTX renderer.
- Beamer PDF renderer.
- YAML deck input.
- Preview contact sheets.
- Structural quality report.
- Neutral starter and portfolio fixtures.

## v0.2 - Evidence-Aware Decks

- Add `assets` and `evidence` metadata to the IR. (done for `evidence`)
- Add crop intent and asset provenance. (done for image/crop/caption/source/callouts)
- Add image-selection/evidence audit. (done via `academic-deck evidence`)
- Replace PowerPoint-style callout boxes with numbered proof pins. (done for PPTX and HTML preview)
- Rebuild key result charts as native PPTX/HTML-style panels.
- Add route parity checks between PPTX and Beamer.
- Add a richer visual judge for text length, contrast, missing assets, and image readability. (edge-pressure check added; OCR/text-overlap still open)

## v0.3 - Agent Productization

- Add `plan`, `preview`, `compare`, and `package` CLI commands. (`package` done)
- Add review-bundle generation. (done via `academic-deck package`)
- Add Codex and Claude Code skill installation docs.
- Add examples for paper talks, thesis defense, systems review, and portfolio.

## v0.4 - HTML Editorial Layer

- Add optional HTML panel rendering for dense evidence slides. (static preview route with proof pins added)
- Import reusable design tokens from `templates/*/DESIGN.md`.
- Support browser screenshot export into PPTX as high-resolution evidence panels while keeping surrounding text editable.

## v0.5 - Source-To-Deck Generalization

- Add source ingestion for PDFs, Markdown notes, CV folders, repository metadata, and screenshot directories.
- Create a `SourceManifest` with extracted figures, tables, citations, and candidate claims.
- Add `SlidePlan` normalization so PPTX, Beamer, and HTML share the same semantic layout grammar.
- Add route-parity QA for slide count, evidence assets, captions, and source references.
- Add OCR/text-overlap QA and native chart redraw suggestions.

## Current Route Decision

HTML-first should be the default for high-taste academic and technical talks when visual fidelity matters. PPTX-native remains useful when the deck must be edited in PowerPoint, and Beamer remains useful for formal academic handouts.
