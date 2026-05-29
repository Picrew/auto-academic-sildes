# Project Flow

Auto Academic Slides is organized around a simple belief: a good academic deck is a compiled argument, not a decorated summary.

## 1. Gather Source Material

Accepted inputs can be loose:

- paper PDFs or notes
- project folders
- screenshots and figures
- public profile pages
- README files, papers, benchmark tables, demos, and technical reports

Use `ingest` when the source folder is large:

```bash
uv run academic-deck ingest --source /path/to/source-folder --out outputs/source-pack
```

The source pack is not a deck. It is a working manifest that helps an agent decide what should become claims, evidence, and appendix material.

## 2. Write the Narrative Spine

Create or edit `deck.yaml`.

The first pass should answer four questions:

- What should the audience believe after the talk?
- What failure or uncertainty makes the talk necessary?
- Which evidence surfaces prove the claim?
- What should be left for notes or appendix?

Use action titles. A title such as "Method" is weak; a title such as "The method works because the failure becomes measurable" is a slide.

## 3. Choose Evidence

Images are not decoration. They are proof surfaces.

Use `evidence.image`, a finite normalized `crop`, a specific `caption`, and a compact `source` line. If the evidence is a screenshot, crop to the part the audience must inspect. If the source is too dense, redraw or split the slide.

Run:

```bash
uv run academic-deck evidence --deck examples/my-talk/deck.yaml --out outputs/my-talk
```

## 4. Select a Visual Direction

Do not pick a style by palette alone. Pick a relationship between claim, evidence, and whitespace.

Start with a shortlist:

```bash
uv run academic-deck template-shortlist \
  --brief "paper talk, formal, source evidence, quiet high taste" \
  --out outputs/template-shortlist
```

Then compare real renderings:

```bash
uv run academic-deck compare-grammars \
  --deck examples/my-talk/deck.yaml \
  --out outputs/my-talk-grammar-bakeoff \
  --grammars highsense-20 \
  --fail-on-layout
```

Read `GRAMMAR_COMPARISON.md`, `DESIGN_DIRECTIONS.md`, and the stacked contact sheet before choosing.

## 5. Render and Audit

For visual fidelity:

```bash
uv run academic-deck html-pptx \
  --deck examples/my-talk/deck.yaml \
  --out outputs/my-talk-html \
  --fail-on-layout
```

For editable PPTX and Beamer/PDF backups:

```bash
uv run academic-deck build \
  --deck examples/my-talk/deck.yaml \
  --out outputs/my-talk \
  --fail-on-layout
```

Strict export requires clean content, evidence, and browser layout reports.

## 6. Repair

If comparison produces promising but flawed variants:

```bash
uv run academic-deck repair-plan \
  --manifest outputs/my-talk-grammar-bakeoff/GRAMMAR_REPAIR_HINTS.json \
  --out outputs/my-talk-grammar-bakeoff

uv run academic-deck repair-draft \
  --deck examples/my-talk/deck.yaml \
  --manifest outputs/my-talk-grammar-bakeoff/GRAMMAR_REPAIR_HINTS.json \
  --out outputs/my-talk-repair-draft
```

Repair drafts are conservative. They may switch a slide to `proof-showcase`, enlarge an artifact surface, or tighten a crop; they should not rewrite the research story without review.

## 7. Package

```bash
uv run academic-deck package --deck examples/my-talk/deck.yaml --out outputs/my-talk
```

The package is meant for review: rendered decks, contact sheets, audit reports, and source metadata in one place.

