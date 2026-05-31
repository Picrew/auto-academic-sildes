# Auto Academic Slides

A local compiler for research and technical slide decks that should feel written, designed, and checked rather than merely generated.

It starts from a claim-led `deck.yaml`, runs content and evidence checks, renders an HTML-first deck, and can export the result to PPTX or Beamer/PDF. The project is built for agent workflows, but the output contract is deliberately plain: one argument, readable evidence, no overlapping text, and no generic template gloss.

[中文说明](README_zh.md)

## Why This Exists

Most slide generators optimize for speed. Academic talks need something stricter:

- action titles instead of topic headings
- evidence images that can actually be inspected
- a layout audit that catches overlap, clipping, tiny figures, and weak crops
- visual grammars that vary by composition, not just by accent color
- HTML-level typography with PPTX and Beamer delivery routes

The workflow borrows ideas from strong presentation ecosystems such as [reveal.js](https://github.com/hakimel/reveal.js), [Slidev](https://github.com/slidevjs/slidev), [Marp](https://github.com/marp-team/marp), and agent-facing template libraries such as [beautiful-html-templates](https://github.com/zarazhangrui/beautiful-html-templates). It is not a wrapper around any one of them; it is a small compiler with its own deck schema, renderers, and quality gates.

## Install

```bash
git clone https://github.com/Picrew/auto-academic-sildes.git
cd auto-academic-sildes
uv sync
uv run academic-deck doctor
uv run --with pytest pytest -q
```

`doctor` reports optional local tools such as Chrome/Chromium, LaTeX, Poppler, and PowerPoint automation support. HTML and PPTX-image export need a browser. Beamer export needs a LaTeX toolchain.

## Quick Start

Create a neutral starter deck:

```bash
uv run academic-deck init --out examples/my-talk/deck.yaml
```

Check the source before rendering:

```bash
uv run academic-deck check --deck examples/my-talk/deck.yaml --out outputs/my-talk
uv run academic-deck evidence --deck examples/my-talk/deck.yaml --out outputs/my-talk
```

Render the HTML-first route and export it to PPTX:

```bash
uv run academic-deck html-pptx \
  --deck examples/my-talk/deck.yaml \
  --out outputs/my-talk-html \
  --fail-on-layout
```

Compare multiple visual grammars before choosing a final style:

```bash
uv run academic-deck compare-grammars \
  --deck examples/my-talk/deck.yaml \
  --out outputs/my-talk-grammar-bakeoff \
  --grammars highsense-20 \
  --fail-on-layout
```

Build editable PPTX and Beamer/PDF backups:

```bash
uv run academic-deck build \
  --deck examples/my-talk/deck.yaml \
  --out outputs/my-talk \
  --fail-on-layout
```

## Agent Usage

The recommended way to use this project with Codex or Claude Code is through repo-scoped skills plus the compiler loop. Ask the agent to invoke a skill, produce or edit `deck.yaml`, run the quality/evidence/layout checks, inspect the contact sheet, and revise before exporting.

Codex:

```text
$paper-to-html-talk Build a 12-slide HTML-first talk from <paper.pdf>. Use compare-grammars, run with --fail-on-layout, inspect the contact sheet, and package the result.
```

Claude Code:

```text
/paper-to-html-talk Build a 12-slide HTML-first talk from <paper.pdf>. Use compare-grammars, run with --fail-on-layout, inspect the contact sheet, and package the result.
```

Useful entry points:

- `$academic-deck` / `/academic-deck` for general academic or technical decks.
- `$html-first-deck` / `/html-first-deck` when visual fidelity is the priority.
- `$paper-to-html-talk` / `/paper-to-html-talk` for paper talks and journal clubs.
- `$public-profile-deck` / `/public-profile-deck` for public-source profile decks.
- `$deck-iteration-judge` / `/deck-iteration-judge` after a rendered contact sheet exists.

Skill layout:

- `.codex/skills/` is the canonical source for detailed deck skills and is kept for existing Codex desktop/local skill setups.
- `.agents/skills/` is the current repo-discovered Codex entry point.
- `.claude/skills/` is the Claude Code entry point.

When changing skills, edit `.codex/skills/<skill>/SKILL.md` first, then run:

```bash
uv run python scripts/sync_agent_skill_bridges.py
uv run python scripts/sync_agent_skill_bridges.py --check
```

## The Pipeline

```text
source notes / paper / project
        ↓
deck.yaml
        ↓
quality + evidence audit
        ↓
HTML renderer ── browser audit ── contact sheet ── image PPTX
        ↓
optional editable PPTX / Beamer backup
        ↓
grammar comparison / repair hints / review package
```

The compiler treats HTML as the design source of truth. PPTX-native remains useful when editability matters; Beamer remains useful when the final artifact should be a formal academic PDF.

## Deck Schema

Each slide has a `kind`, an action `title`, optional `subtitle`, compact `bullets`, and optional `metrics`, `labels`, `note`, or `evidence`.

Use `evidence` for figures, screenshots, tables, repositories, homepages, dashboards, and UI states:

```yaml
- kind: evidence
  kicker: Result
  title: The strongest figure should carry the result slide
  layout: proof-showcase
  bullets:
    - Keep only the part of the figure that proves the headline.
  evidence:
    image: assets/images/result-crop.png
    crop: {x: 0.08, y: 0.12, w: 0.78, h: 0.70}
    caption: Main comparison: the proposed method keeps accuracy stable under distribution shift.
    source: Paper figure or project artifact, accessed 2026-05-30.
    callouts:
      - {x: 0.62, y: 0.38, text: stable region}
```

For the full contract, see [docs/IR.md](docs/IR.md).

## Visual Grammars

The project includes a broad grammar pool: academic homepage grids, source ledgers, paper-note layouts, gallery proof rooms, hard systems boards, and HTML-template-inspired families such as `signal-intelligence-brief`, `raw-grid-research`, and `stencil-field-tablet`.

Useful presets:

- `highsense-20`: first pass for tasteful academic/technical work
- `reference-20`: alias for the same curated pool
- default compare pool: broad regression and discovery sweep

Tone-led shortlist:

```bash
uv run academic-deck template-shortlist \
  --brief "academic research profile, source evidence, quiet high taste" \
  --out outputs/template-shortlist
```

If `vendor/beautiful-html-templates` is present, the command reads its full `index.json`. Without the vendor checkout, it falls back to a small built-in academic shortlist.

Read more in [docs/VISUAL_GRAMMARS.md](docs/VISUAL_GRAMMARS.md) and [docs/DESIGN_REFERENCE_SYNTHESIS.md](docs/DESIGN_REFERENCE_SYNTHESIS.md).

## Quality Gates

Strict export treats these as blockers:

- text overlap, self-overlap, clipping, and unsafe line height
- text-image collision or tight clearance
- missing proof images, missing crops, missing captions, or missing source notes
- tiny proof/artifact surfaces and severe letterboxing
- callout pins outside the rendered source image
- over-budget bullets, metrics, labels, captions, and CJK-dense copy
- unknown visual grammar names

The browser audit writes `layout-audit-report.md`; image checks write `evidence-report.md`; content checks write `quality-report.md`. A deck is not ready until those reports are clean and the contact sheet looks good.

## Commands

```bash
uv run academic-deck init --out examples/my-talk/deck.yaml
uv run academic-deck init --example portfolio --out examples/profile-fixture/deck.yaml
uv run academic-deck ingest --source /path/to/source-folder --out outputs/source-pack
uv run academic-deck check --deck examples/my-talk/deck.yaml --out outputs/my-talk
uv run academic-deck evidence --deck examples/my-talk/deck.yaml --out outputs/my-talk
uv run academic-deck html-pptx --deck examples/my-talk/deck.yaml --out outputs/my-talk-html
uv run academic-deck compare-grammars --deck examples/my-talk/deck.yaml --out outputs/my-talk-grammar-bakeoff
uv run academic-deck repair-plan --manifest outputs/my-talk-grammar-bakeoff/GRAMMAR_REPAIR_HINTS.json --out outputs/my-talk-grammar-bakeoff
uv run academic-deck repair-draft --deck examples/my-talk/deck.yaml --manifest outputs/my-talk-grammar-bakeoff/GRAMMAR_REPAIR_HINTS.json --out outputs/my-talk-repair-draft
uv run academic-deck build --deck examples/my-talk/deck.yaml --out outputs/my-talk
uv run academic-deck package --deck examples/my-talk/deck.yaml --out outputs/my-talk
```

## Repository Layout

```text
src/academic_deck_compiler/   compiler, renderers, audits, CLI
templates/                    visual grammar design notes
examples/                     public neutral fixtures
docs/                         architecture, workflow, evidence, style notes
.codex/skills/                canonical detailed deck skills
.agents/skills/               generated Codex skill bridges
.claude/skills/               generated Claude Code skill bridges
tests/                        unit and smoke tests
```

Private harvested profiles, personal portfolio fixtures, generated screenshots, and rendered decks are intentionally ignored. See [docs/PUBLICATION_POLICY.md](docs/PUBLICATION_POLICY.md).

## Documentation

- [Project flow](docs/PROJECT_FLOW.md)
- [Intermediate representation](docs/IR.md)
- [HTML-first architecture](docs/HTML_FIRST_ARCHITECTURE.md)
- [Agent workflow](docs/AGENT_WORKFLOW.md)
- [Public profile workflow](docs/PUBLIC_PROFILE_WORKFLOW.md)
- [Image evidence](docs/IMAGE_EVIDENCE.md)
- [Visual grammars](docs/VISUAL_GRAMMARS.md)
- [Visual QA](docs/VISUAL_QA.md)
- [Publication policy](docs/PUBLICATION_POLICY.md)

## Limitations

- HTML-image PPTX preserves visual fidelity but is not deeply editable.
- PPTX-native is editable but less expressive than the HTML route.
- Dense paper figures still need careful cropping or redrawing.
- Browser screenshots, LaTeX, and PowerPoint PDF export depend on local tools.
- The visual judge is a first-pass heuristic; contact-sheet review is still part of the workflow.
