# HTML-First Architecture

The compiler treats HTML as the primary design surface when taste, evidence
scale, and typography matter. PPTX-native remains useful for editable school or
company templates, but it is no longer the design authority.

```text
source pack
→ deck.yaml
→ quality + evidence audits
→ HTML editorial deck
→ browser screenshots
→ image-based PPTX
→ optional PPTX-native / Beamer backup
```

## Routes

### HTML-image PPTX

Command:

```bash
uv run academic-deck html-pptx --deck examples/tech-review/deck.yaml --out outputs/html-first/tech-review
```

This route renders the HTML deck in Chrome, screenshots each slide, and embeds
each screenshot as a full-slide image in PPTX. It is not deeply editable, but it
preserves typography, spacing, crops, and visual rhythm.

For strict layout validation:

```bash
uv run academic-deck html-pptx \
  --deck examples/starter/deck.yaml \
  --out outputs/fixture-a \
  --visual-grammar academic-homepage-grid \
  --fail-on-layout
```

For rapid grammar exploration, use `--skip-layout-audit`, then rerun shortlisted
variants without that flag.

## Hard Layout Gates

The HTML route treats overlap and weak image insertion as build failures, not as
manual polish. The strict browser audit measures the rendered slide boxes after
Chrome has loaded images and repositioned callout pins.

The audit is retried across screenshot-backed and DOM-only Chrome passes so a
transient headless rendering issue does not masquerade as a design failure. A
missing audit block after all retries is still a hard failure.
In `compare-grammars`, a browser screenshot timeout is recorded as a
`screenshot-timeout` variant row instead of aborting the whole bake-off. This
keeps long grammar searches judgeable: failed browser infrastructure is visible
in the report, while other variants can still render and be ranked.

The enforcement happens in five layers:

1. `quality.py` rejects overloaded source slides before rendering: long titles,
   dense subtitles, too many bullets/metrics/labels, unsafe CJK-dense copy, raw
   non-cover images, missing crops, more than three callouts, low-resolution
   proof crops, and image-backed pages whose combined bullets, metrics, labels,
   and callouts would crowd the visual.
2. `deck.yaml` image insertion must use the evidence contract:
   `evidence.image`, finite `crop`, compact `caption`, compact `source`, and
   optional callouts. A non-cover bare `image:` is rejected because it bypasses
   crop, caption, source-pixel, and clearance checks.
3. `render_html.py` gives proof/artifact layouts protected image slots and
   stamps each rendered figure with `data-image-role`, crop, caption, and source
   contract markers. The DOM audit rejects a rendered proof/artifact image if
   those markers are missing.
4. The browser DOM audit checks real line boxes, figure boxes, visible source
   pixels, caption/source contrast, callout pin placement, and side-by-side
   text-image clearance at the final 16:9 viewport.
5. `--fail-on-layout` promotes all overlap, clearance, overflow, image-scale,
   caption, callout, and underfill warning gates into delivery blockers. A deck
   can be explored quickly, but it cannot be accepted without the strict pass.

Text gates:

- `element-overlap` catches any audited module overlap before the issue is
  narrowed to text, image, caption, or callout semantics.
- `text-line-overlap` catches real line-box collisions between separate text
  elements.
- `text-line-height-tight` catches wrapped text before collision: if the line
  height is below the safe ratio, the slide fails even when glyphs have not yet
  touched.
- `text-self-overlap` catches headings, metrics, labels, and captions whose own
  wrapped lines are too tight, including rendered line-box collisions inside a
  single text element.
- `title-wrap-too-deep` and `subtitle-wrap-too-deep` catch titles or subtitles
  that use the slide like a document. `title-wrap-deep` and
  `subtitle-wrap-deep` remain strict delivery warnings so near-collisions are
  repaired before final export.
- `text-clearance-tight` catches adjacent text lines with effectively no
  vertical breathing room.
- `text-image-overlap`, `text-image-clearance-tight`,
  `proof-notes-image-overlap`, `artifact-notes-image-overlap`, and
  `notes-image-clearance-tight` catch titles, captions, callout notes, or
  bullets that collide with proof and artifact slots, including side-by-side
  text pressed too close to a rendered image.
- `figure-caption-overlap` and `figure-caption-clearance-tight` catch the
  common failure where the image itself is fine but its caption/source note is
  pressed against the visual surface.
- `label-contrast-low` catches label boards that fit geometrically but inherit
  an unreadable text color from a dark or light slide theme.
- `text-clipped` catches text that is visually cut by an audited overflow
  container even when browser scroll metrics do not show a collision.
- `text-overflow`, `container-overflow`, and `viewport-overflow` catch clipped
  content before export.
- `pseudo-overlay-front` catches grammar `::before` / `::after` layers that
  sit above text or evidence. Decorative overlays must stay behind content.

Image gates:

- Every strict audit prints an `Image Contracts` table with rendered source
  pixels, visible area, slot use, loaded status, and crop/caption/source status
  for proof, artifact, and cover images.
- Evidence-like slides must render a real proof image, not a placeholder.
- `untyped-image` rejects raw inserted slide images. A screenshot, crop, or
  portrait must move through the proof, artifact, or cover channel so the
  renderer can audit crop, source pixels, caption, and clearance.
- `untyped-vector-image` rejects SVG/canvas visuals outside renderer-owned
  proof/artifact/cover channels. `untyped-background-image` rejects every CSS
  `background-image: url(...)` inside a slide, because evidence and identity
  visuals must use audited `<img>` channels so source pixels, crop, caption,
  and text clearance can be measured.
- `image-contract-missing`, `image-crop-missing`, and
  `image-caption-source-missing` reject rendered images that bypass or lose the
  typed insertion contract after HTML generation.
- Non-cover images must be declared as `evidence.image`. A top-level `image`
  on non-cover slides is only tolerated as a legacy mirror when it matches
  `evidence.image`; a mismatch is a hard quality error.
- Cover `image` fields are identity anchors, not proof. If a cover uses an
  `evidence:` object, it must still provide `image`, `crop`, `caption`, and
  `source`.
- Crop and callout coordinates must be finite normalized values. NaN or
  infinity fails before rendering.
- Source-heavy web, repo, paper, table, dashboard, benchmark, homepage, and UI
  screenshots are rejected before render when they use an almost full-frame crop
  whose aspect ratio does not fit a stable slide slot. A long page needs a local
  crop, not shrink-to-fit insertion.
- More than three callouts is a quality error. The renderer must never silently
  drop annotation pins that the source deck supplied.
- Proof images must occupy enough visible slide area to be inspected.
- Proof and artifact images must also have enough rendered source pixels after
  `object-fit: contain`; a large slot with a thin unreadable strip still fails.
- Artifact panels on ordinary content slides must remain readable or be removed.
- The audit measures the visible source pixels inside `object-fit: contain`, so
  letterboxed images cannot pretend to be large.
- Source-heavy artifact panels now have two thresholds: below roughly 820x460
  rendered source pixels is a hard failure, while the strict delivery target is
  about 980x540 or better. Repo, UI, paper, table, benchmark, project-page, and
  homepage screenshots should normally clear that target before a grammar is
  shortlisted.
- Severe proof/artifact letterboxing is a hard failure; moderate letterboxing is
  a warning that should trigger a crop or slot-shape review.
- Quality-report errors stop every export route, including fast preview mode.
  `--fail-on-layout` additionally treats proof/artifact scale warnings,
  rendered-pixel warnings, callout collisions, generic image captions,
  low-readability caption styling, underfilled-page warnings, useful-fill
  failures, and source-heavy artifact underfeature warnings as strict delivery
  gates. Use `--skip-layout-audit` only for rough exploration.
- `useful-fill-low` measures useful text plus visible source evidence, not just
  decorated boxes. A slide that is visually occupied by frames but sparse in
  readable material is queued for repair.
- `artifact-role-underfeatured` applies a higher threshold to repo, UI, table,
  benchmark, paper, project-page, and homepage screenshots than to portraits or
  logos. If such an artifact carries the claim, it must be readable as a source
  surface.
- Cover images that are too small are reported as decorative identity anchors,
  not evidence.
- Text must keep a real safety gap from proof and artifact image slots. A
  beautiful crop still fails if a title, caption, callout note, or footer sits
  on top of it.
- Compact proof compositions hide callout-note lists by default. Use pins,
  captions, and the slide's side rail for the claim; reserve visible callout
  notes for roomier `proof-showcase` pages where the DOM audit can preserve
  clearance.
- Callout pins are positioned on the rendered source-image box, not the whole
  slot. Pins falling into letterbox whitespace fail as
  `callout-outside-source-image`.
- `check` also rejects unsafe source material early: extremely long text,
  oversized bullet budgets, low-resolution proof crops, and extreme aspect
  ratios.
- `check` counts bullets, metrics, labels, and callouts together on
  image-backed slides. A proof or artifact image cannot be inserted into a page
  that is already carrying too many neighboring text modules; split the page or
  remove a module family before rendering.
- `check` rejects unknown `visual_grammar` values. The CLI also refuses unknown
  grammars for single renders and grammar comparisons, so a typo cannot silently
  fall back to a safer default.

Use the fast path only for exploration:

```bash
uv run academic-deck html-pptx \
  --deck examples/starter/deck.yaml \
  --out outputs/fast-preview \
  --skip-layout-audit
```

Use the strict path before judging or sharing:

```bash
uv run academic-deck html-pptx \
  --deck examples/starter/deck.yaml \
  --out outputs/final-preview \
  --visual-grammar monograph-review \
  --fail-on-layout
```

For generality testing, run a grammar bake-off on at least two different source
decks. The historic 20-grammar baseline passed two materially different profile
fixtures with zero blocking layout issues. The default bake-off pool is
now 42 grammars; a full 42-grammar two-deck pass is the promotion gate after any
renderer-wide change. The latest hardening pass also validated
`prism-workbench-index`, `huashu-issue-broadsheet`, `prism-newsroom-index`, and
`js-editorial-cascade` against Fixture A and Fixture B in focused strict comparisons
with zero blocking issues. Variants can
report `proof-image-small` or `decorative-image-too-small` warnings; treat those
as evidence/crop repair signals, not as passes to ignore.

Strict CLI routes may leave screenshots and contact sheets for review even when
a delivery gate fails. When `html-pptx` or `build` fails under
`--fail-on-layout`, generated deliverables are renamed with a `.blocked` infix
and `DELIVERY_BLOCKED.md` explains why they are not shippable.

The editable PPTX/Beamer `build` route uses the HTML render as a proxy gate for
source safety, overlap, image contracts, proof scale, and useful-fill. It is not
a full native PowerPoint or LaTeX PDF geometry audit, so final native routes
still need contact-sheet inspection.

The focused overlap/image pass in
`outputs/design-directions-fixture-a-v3/GRAMMAR_COMPARISON.md` validates
`prism-workbench-index`, `gallery-proof-room`, `huashu-issue-broadsheet`,
`fathom-research-brief`, `js-editorial-cascade`, and `ia-research-archive` with
zero blocking errors, zero warnings, and zero strict quality warnings after the
caption/proof-note and artifact-panel safety fixes.
The follow-up useful-fill and role-aware artifact pass tightened this further:
`outputs/useful-fill-fixture-a-huashu-debug/GRAMMAR_COMPARISON.md` and
`outputs/useful-fill-fixture-a-ia-debug-v2/GRAMMAR_COMPARISON.md` both report 100
scores with zero warnings after enlarging source-heavy artifacts and suppressing
secondary notes that would collide with the source image.
The complete focused rerun at
`outputs/useful-fill-fixture-a-v7/GRAMMAR_COMPARISON.md` reports all six focused
directions with score 100, zero blocking errors, zero warnings, and distinct
style/composition families under the useful-fill and role-aware artifact gates.
The current focused overlap/image contract check also validates the repaired
homepage/profile path: `outputs/repair-contract-fixture-a-v6-artifact-threshold`
and `outputs/repair-contract-fixture-b-v4-caption-image` both shortlist
`academic-homepage-grid` with zero blocking errors and zero strict warnings
after the caption-clearance, proof-note, and source-heavy artifact fixes.
`GRAMMAR_COMPARISON.md` separates ready shortlist variants from an `Image
Revision Queue`; the latter needs crop, slot, or proof-scale repair before
export. The same report includes `Repair Hints` that map each warning back to
the source slide, image, crop, and layout intent.
For agentic repair loops, run `academic-deck repair-plan` against
`GRAMMAR_REPAIR_HINTS.json` to produce `DECK_REPAIR_PLAN.md`, then run
`academic-deck repair-draft` to create a non-destructive `deck.repair.yaml`.
The draft resolves relative asset folders back to the source deck, so image
insertion is tested from the candidate file rather than accidentally failing
because the deck moved into an output directory. By default it pins the cleanest
shortlisted grammar; when a grammar is explicitly supplied, it applies only
conservative layout and crop edits before the next strict render.

```bash
uv run academic-deck compare-grammars \
  --deck examples/starter/deck.yaml \
  --out outputs/ranked-fixture-a-20-v1 \
  --fail-on-layout

uv run academic-deck compare-grammars \
  --deck examples/tech-review/deck.yaml \
  --out outputs/ranked-fixture-b-20-v1 \
  --fail-on-layout

uv run academic-deck repair-draft \
  --deck examples/starter/deck.yaml \
  --manifest outputs/ranked-fixture-a-20-v1/GRAMMAR_REPAIR_HINTS.json \
  --out outputs/fixture-a
```

The `proof-showcase` and `artifact-showcase` layout values are semantic safety
intents, not fixed templates. They ask the active grammar to choose a safer proof
relationship, so a bake-off can still produce `proof-dossier`,
`proof-atlas-spread`, `proof-ledger`, `proof-marginalia`, `proof-gallery-split`,
or a readable artifact composition.

### PPTX-native

Command:

```bash
uv run academic-deck build --deck examples/tech-review/deck.yaml --out outputs/native/tech-review
```

This route is editable and institutionally convenient. Use it when the audience
will revise the deck in PowerPoint. Judge it against the HTML route instead of
letting it define the design.

The native build stops on quality-report errors and also writes
`layout-audit-report.md` from the HTML render, so editable PPTX and Beamer
exports do not skip the same overlap and image-contract checks.
Pass `--fail-on-layout` to make those HTML overlap, useful-fill, and image
source gates blocking for native PPTX/Beamer delivery as well:

```bash
uv run academic-deck build \
  --deck examples/tech-review/deck.yaml \
  --out outputs/native/tech-review \
  --fail-on-layout
```

### Beamer

Beamer is a disciplined PDF backup. It is best for formal academic handouts,
math-heavy material, and LaTeX-first settings. It is usually weaker for public
profile briefings and visual evidence walls.

## Design Principle

HTML is allowed to be expressive. The IR should not force every deck into the
same six slides. Let agents choose slide moves and visual grammar based on the
source material.

Good HTML-first decks still obey academic taste:

- one judgment per slide
- evidence before decoration
- readable figures
- calm typography
- source provenance
- contact-sheet review
- no hard layout audit errors
- enough content fill that pages do not look like tiny text stranded on a large canvas
- images that prove a claim, not images that merely make the slide look busy

## Future Work

- Add CLI contact-sheet generation to the core HTML route.
- Add hybrid PPTX export: screenshot background plus editable title and notes.
- Add DOM-to-editable-PPTX as an experimental route.
- Add browser QA for mobile, projector, and PDF export views.
