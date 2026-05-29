# Design Reference Synthesis

This project treats HTML as the design source and PPTX/PDF as exports. The
references below are not copied as surfaces; they are distilled into reusable
slide grammar, audit gates, and agent workflow.

## PRISM

Reference: `references/PRISM` / https://github.com/xyjoey/PRISM

Transferable ideas:

- Academic homepages work because identity, selected work, publications, and
  projects are structured as source-linked information, not as generic feature
  cards.
- Serif/sans pairing, near-white surfaces, quiet slate text, and warm source
  cues help research content feel credible without looking like Beamer.
- Publication rows and project ledgers can replace overdecorated cards.
- PRISM's content architecture is as important as its look: `config.toml`,
  `about.toml`, Markdown bio/CV files, and BibTeX publications create a
  structured profile index. Deck generation should mirror that by collecting
  identity, selected work, news, publications, projects, and source links before
  choosing a visual grammar.
- The usable PRISM palette is narrow: near-white background, slate text, a warm
  gold accent, and serif display/sans body pairing. The lesson is not to copy a
  homepage screenshot; it is to make slides feel like a source-linked academic
  index.

Implemented grammars:

- `academic-homepage-grid`
- `prism-dossier`
- `prism-clean-room`
- `prism-publication-stack`
- `prism-newsroom-index`

## High-Sense Web References

Reference: https://js.design/special/article/highsense-page-design.html

Transferable ideas:

- High-end web pages often succeed through one strong visual protagonist, not
  many decorations.
- Editorial scale changes, proof plates, and gallery-like cadence make decks
  feel less like AI templates.
- Atmosphere is useful only when the content remains inspectable.
- The JS.Design reference is useful as a corpus prompt, not a slide template:
  borrow focal hierarchy, rich image/text pairing, and varied layouts; reject
  consumer landing-page decoration when the deck is academic.

Implemented grammars:

- `highsense-gallery`
- `object-study-wall`
- `couture-exhibition`
- `gallery-proof-room`

## Huashu Design

Reference: `references/huashu-design`

Transferable ideas:

- Design should be judged on philosophy alignment, visual hierarchy, craft,
  functionality, and originality.
- For technical slides, every element needs a job: evidence, comparison axis,
  method component, source cue, or conclusion anchor.
- Huashu's critique guide is now reflected in deck judging: philosophy
  alignment, hierarchy, craft, functionality, and originality. The most useful
  rule for academic slides is functional deletion: if removing an ornament does
  not weaken the claim or proof, remove it.
- Huashu's slide-deck reference also reinforces HTML-first delivery: build the
  browser deck first, then export PDF/PPTX. For our compiler, this means the
  browser DOM audit is the source of truth for text fit, image contracts, and
  proof scale before any PPTX export is trusted.
- HTML-first is the right source route because precise grid, image scale,
  captions, and export audits are easier to enforce before PPTX/PDF snapshots.
- Avoid AI cliches: purple-blue gradients, cyber neon, glass cards, floating
  blobs, stock abstraction, and fake dashboards.

Implemented grammars:

- `pentagram-gridnote`
- `takram-research-system`
- `stamen-data-map`
- `huashu-editorial-lab`
- `huashu-build-board`
- `broadsheet-data-room`

## Beautiful HTML Templates

Reference: `vendor/beautiful-html-templates` /
https://github.com/zarazhangrui/beautiful-html-templates

Transferable ideas:

- The library is built for agentic template choice: read `index.json`, match
  occasion plus mood, then inspect a real template only after shortlisting.
- Its useful academic-adjacent families are not the cute or nostalgic ones; the
  strongest transfers are `signal`, `vellum`, `monochrome`,
  `editorial-forest`, `cobalt-grid`, `raw-grid`, `stencil-tablet`,
  `blue-professional`, `cartesian`, and `broadside`.
- The template lesson is closed-system discipline. Fonts, palette, chrome,
  layout rhythm, and decorative vocabulary must belong to one source family;
  mixing several template motifs creates amateur collage.
- For this compiler, templates are used as grammar seeds and tone references,
  not as unchecked final decks. The browser audit still decides whether a
  chosen route can be delivered.

Implemented or mapped grammars:

- `signal-intelligence-brief`
- `raw-grid-research`
- `stencil-field-tablet`
- `vellum-research-note`
- `mono-ink-ledger`
- `forest-editorial-brief`
- `cobalt-research-grid`
- `broadside-lab`

Executable helper:

```bash
uv run academic-deck template-shortlist \
  --brief "academic research profile, source evidence, quiet high taste" \
  --out outputs/template-shortlist
```

## Direction Advisor Layer

The compiler now includes a 20+ item design-direction library in
`src/academic_deck_compiler/design_directions.py`. It sits above individual
visual grammars and turns references into executable choices:

- PRISM-inspired directions for publication stacks, selected-work indexes, and
  clean academic dossiers.
- JS Design-inspired directions for high-sense editorial cascades, proof rooms,
  and exhibition-like evidence slides.
- Huashu-inspired directions for Pentagram/Muller grids, Fathom evidence briefs,
  Build-style hard boards, issue broadsheets, Takram systems, Stamen data maps,
  Sumi scrolls, and 5D critique.
- Beautiful-templates-inspired directions for Signal briefings, Raw Grid boards,
  Stencil field manuals, Vellum notes, Monochrome ledgers, and editorial profile
  warmth.

`compare-grammars` writes `DESIGN_DIRECTIONS.md` next to
`GRAMMAR_COMPARISON.md`. Agents should read it before selecting a winner:
choose a design school first, then a grammar, then a two-page showcase.

## Constraint Layer

The visual references only help if the compiler rejects broken slides. Strict
HTML export therefore treats these as delivery gates:

- text block overlap, line overlap, self-overlap, clipping, and tight clearance
- text-image overlap and tight horizontal/vertical image clearance
- figure-caption overlap and tight caption clearance
- source-level text budgets that shrink when a slide includes a proof or
  artifact image, so images are not inserted into already-full text pages
- combined module budgets across bullets, metrics, labels, and callouts on
  image-backed pages, so a proof/artifact image remains the visual protagonist
- missing, generic, tiny, or low-contrast proof/artifact captions
- missing proof images, too-small source pixels, severe letterboxing, and pins
  outside rendered source pixels
- missing image insertion contracts: every proof/artifact row should appear in
  the `Image Contracts` table with role, rendered pixels, visible area, slot
  use, crop, caption, and source status
- titles/subtitles that wrap too deeply before they visibly collide; a long
  action title is a source problem, not a typography challenge
- underfilled slides when the page is visibly empty rather than intentionally
  spacious

The goal is not merely "no overlap"; it is evidence-first taste that survives a
real projection room.
