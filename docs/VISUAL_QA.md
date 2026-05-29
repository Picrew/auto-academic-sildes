# Visual QA

The compiler should be judged from rendered screenshots, not from source files alone.

## Blocking Checks

- No visible text clipping or internal overlap.
- No foreground pseudo-element layer covers text, proof images, captions, or
  callouts; decorative CSS layers must stay behind content.
- No line-level collisions between titles, table cells, labels, captions, callout notes, or footer text.
- No multi-line heading, caption, metric, or bullet uses unsafe line-height; `text-line-height-tight` is a hard failure because it usually becomes overlap after export or font substitution.
- No adjacent text lines with near-zero vertical clearance; cramped cross-module text is a layout failure, while compact value/label micro-stacks are audited separately.
- No hidden container overflow in `two-col`, `evidence-grid`, `matrix-grid`, proof, or artifact panels.
- Long copy must pass the language-aware text budget before rendering. Dense CJK/Japanese/Korean scripts are counted conservatively, so a paragraph without spaces cannot slip through as a short bullet.
- No title, bullet, caption, callout note, pin text, or footer text overlaps a proof/artifact image slot or sits against it with no vertical or horizontal safety gap. Any measurable text-on-image intersection above the tiny anti-aliasing tolerance is a blocking `text-image-overlap`, even if only an edge of the line crosses the slot.
- Main evidence remains readable at contact-sheet size.
- Evidence-like slides must render a real loaded image, not a placeholder proof box.
- Every slide image must be inserted through a typed channel: proof, artifact, or cover. Raw HTML images and bare evidence-slide `image:` fields are rejected because they bypass crop, caption, source, and clearance checks.
- Any non-cover screenshot or figure needs an `evidence:` contract with
  `evidence.image`, explicit crop, caption, and source even when it appears on a
  normal content slide; otherwise it is rejected before screenshot export. Use a
  full-frame crop only for source files already prepared as slide-scale crops.
- Source-heavy web, repo, paper, table, dashboard, benchmark, homepage, or UI
  screenshots cannot use an almost full-frame crop when the crop shape does not
  fit a slide slot. Crop to the readable evidence region before insertion.
- Source-heavy crops also have a pre-render pixel floor: proof crops below about
  900x500 and artifact crops below about 820x460 are rejected before browser
  layout, because they cannot survive slide-scale projection as evidence.
- A top-level non-cover `image` can only mirror the same file in
  `evidence.image`; mismatches fail before render. Plain cover images are
  identity anchors, not proof.
- Key evidence images below roughly one third of the slide are underfeatured; enlarge, crop tighter, or switch composition before final polish.
- Cover thumbnails below roughly 3.5% visible slide area are flagged as decorative; use them only as identity anchors, not proof.
- Proof/artifact images should not be heavily letterboxed; if most of the image slot is empty, crop or change the slot.
- Proof/artifact images should not be scaled far beyond their source pixels; a large but blurry crop is still failed evidence.
- Every rendered proof/artifact/cover image appears in the `Image Contracts`
  table with loaded status, rendered source size, visible area, slot use, crop,
  caption, and source status.
- Callout pins must sit on the actual rendered source pixels, not on the blank space created by `object-fit: contain`.
- Each slide has one visual focal point.
- Captions and source notes never collide with metrics or callouts.
- Proof and artifact images carry a specific claim caption and compact source line; generic fallback captions fail delivery mode.
- Evidence callouts use at most two annotations when possible and never clip outside the image slot.
- More than three callouts is a source error because extra pins would otherwise
  disappear from the rendered slide.
- Slide edges remain quiet; no important content sits on the outer margin.

## Automated Checks

`layout-audit-report.md` is the first gate for HTML-first decks. It reports
blocking errors for:

- `element-overlap`, `text-line-overlap`, `text-line-height-tight`, `text-self-overlap`, `text-clearance-tight`, and `text-clipped`
- `text-image-overlap`, `text-image-clearance-tight`, `proof-notes-image-overlap`, `artifact-notes-image-overlap`, and `notes-image-clearance-tight`
- `figure-caption-overlap` and `figure-caption-clearance-tight`
- `text-overflow`, `container-overflow`, and `viewport-overflow`
- `missing-proof`, `missing-proof-image`, `image-not-loaded`, and `image-overflow`
- `proof-too-small`, `proof-image-too-small`, `proof-image-letterboxed-severe`, `artifact-too-small`, `artifact-image-too-small`, and `artifact-image-letterboxed-severe`
- `proof-image-rendered-too-small`, `artifact-image-rendered-too-small`, `proof-image-upscaled-too-much`, and `artifact-image-upscaled-too-much`
- `image-object-fit-unsupported`
- `untyped-image`, `untyped-vector-image`, and `untyped-background-image`
- `callout-outside-image` and `callout-outside-source-image`
- `pseudo-overlay-front`

Hard gate means issue type, not only the raw severity label emitted upstream.
`untyped-background-image` applies to every CSS `background-image: url(...)`
inside a slide; use proof/artifact/cover `<img>` channels for any visual that
needs to survive audit and export.
If a hard-gate type such as `text-image-overlap`, `image-not-loaded`, severe
letterboxing, or out-of-image callouts appears as a warning, the report upgrades
it to blocking before grammar ranking.

Strict export also fails on delivery-warning gates: `proof-image-small`,
`proof-image-rendered-small`, `proof-small`, `proof-image-letterboxed`,
`artifact-image-small`, `artifact-image-rendered-small`, `artifact-small`,
`artifact-image-letterboxed`, `callout-overlap`, `content-underfilled`,
`proof-caption-missing`, `proof-caption-generic`, `artifact-caption-generic`,
`caption-text-too-small`, `caption-contrast-low`, `label-contrast-low`,
`decorative-image-too-small`, `cover-image-letterboxed`,
`useful-fill-low`, and `artifact-role-underfeatured`.
These are not cosmetic; they mean the image was inserted but is not yet
readable enough, the callout layer is confused, the image lacks source context,
the slide is too thin to feel designed, or a source-heavy repo/UI/paper/project
artifact is present but too small to inspect.

`judge-report.md` adds screenshot-level review:

- density score: whether the slide is empty, balanced, or overcrowded.
- edge pressure: whether rendered pixels are active too close to the outer frame.

These checks are deliberately conservative. A deck can pass them and still fail
taste review, but it cannot ship with hard layout errors.

## Pre-Render Text Budget

`quality-report.md` is the first overlap guard. It blocks titles, subtitles,
bullets, labels, metrics, captions, and callout text that exceed the fixed-slide
budget before CSS is involved. The budget is intentionally language-aware:
English is measured by normalized character burden, while dense CJK/Japanese/
Korean scripts get a conservative density penalty because they can form long
unbroken lines in a slide canvas.

Quality-report errors stop every export route before screenshot generation.
Fast preview mode can skip the DOM audit, but it cannot bypass invalid source
contracts such as unknown grammars, non-cover bare images, missing
caption/source, non-finite crop/callout coordinates, too-small source-heavy
crops, image-backed titles that exceed the shorter safe budget, or too many
callouts.

When this gate fires, do not solve it by shrinking text until it becomes
unreadable. Split the claim, move detail into notes, convert long metrics into
bullets, or switch to a composition that gives the proof/image more room.

Strict delivery mode must run the DOM audit. `--fail-on-layout` and
`--skip-layout-audit` are intentionally incompatible because skip mode cannot
catch text-image overlap, unloaded images, source-pixel scale, raw inserted
images, or real browser clipping.

When a strict `html-pptx` or `build` run fails after producing review artifacts,
the CLI writes `DELIVERY_BLOCKED.md` and renames generated deliverables with a
`.blocked` infix. A failed directory is still useful for contact-sheet review,
but its PPTX/PDF files are not delivery artifacts.

## Strict Bake-Off

Before promoting a new grammar or renderer change, run at least two source decks
through `compare-grammars --fail-on-layout`. The current default bake-off uses
42 visual grammars; promote a renderer change only after at least two materially
different source decks clear the strict audit with zero blocking layout issues.
When the brief is specifically "high-sense, less templated, less ordinary",
start with the curated 20-pass preset:

```bash
uv run academic-deck compare-grammars \
  --deck <deck.yaml> \
  --out <bakeoff> \
  --grammars highsense-20 \
  --fail-on-layout
```

For `compare-grammars`, `--fail-on-layout` means "fail if no ready variant is
left." Individual bad candidates are kept in the comparison report as rejected
variants so the agent can learn from the failure instead of silently deleting
the evidence. Single-deck `html-pptx` / `build` commands still fail immediately
when the chosen grammar has any hard overlap, clipping, or image-scale gate.

This preset intentionally spans PRISM academic homepage structure, JS Design
web-editorial pacing, Beautiful HTML Templates families such as Signal, Raw
Grid, and Stencil & Tablet, Huashu issue-board treatments, proof galleries,
source archives, and the newer Maison/Folio/Chromatic triad. It is the default
anti-template route before running the heavier 42-grammar sweep.

Read `GRAMMAR_COMPARISON.md` in this order:

- `Recommended Shortlist`: variants that are ready for taste review. They have
  zero blocking errors and no proof/artifact image scale warnings.
- `Shortlist Diversity`: style and composition families for the ready variants.
  Use it to avoid accepting five siblings that differ mostly by palette. A
  shorter but more distinct shortlist is better than filling the table with
  near-duplicate academic homepage or proof-grid treatments.
- `Image Revision Queue`: variants whose structure may be tasteful but whose
  screenshots, figures, or artifact panels are underfeatured. These need a
  tighter crop, a larger proof layout, or a different image slot before they can
  be accepted.
- `Repair Hints`: slide-specific next actions. These are written for agents:
  they name the source slide, current image, existing crop, and whether the fix
  is a tighter crop, `proof-showcase`, `artifact-showcase`, a split slide, or
  removing a decorative image.
- `GRAMMAR_REPAIR_HINTS.json`: the same repair queue as structured data. Run
  `uv run academic-deck repair-plan --manifest <path> --out <out>` to turn it
  into `DECK_REPAIR_PLAN.md`.
- `repair-draft`: a non-destructive follow-up that turns the manifest into a
  candidate `deck.repair.yaml`. By default it chooses a clean shortlisted
  grammar if one exists; when a specific `--visual-grammar` is supplied, it
  applies conservative layout/crop edits for that variant and writes
  `DECK_REPAIR_DRAFT.md`.
- `Warning Totals`: repeated warning types across the bake-off. A pile-up of
  `proof-image-small` means the material wants proof-showcase compositions or
  better source crops; `decorative-image-too-small` or
  `cover-image-letterboxed` means cover images are only weak identity anchors
  and must be enlarged, cropped, replaced, or removed before delivery.

Rows with `decorative-image-too-small` or `cover-image-letterboxed` are not
delivery-ready even if the rest of the deck is clean; treat them as cover-crop
repair candidates, not final shortlist entries.

## Human Or Subagent Review

Ask a reviewer to inspect:

- contact sheet rhythm across the whole deck.
- full-size evidence slides.
- product screenshots and figure crops.
- whether any phrase sounds like the deck is explaining its own design.

If the rendered slide looks wrong, fix the IR, asset crop, or renderer pattern. Do not patch the final PPTX by hand unless the deck is already frozen for delivery.

## Repair Loop

Use this sequence when overlap, proof scale, or image insertion is uncertain:

```bash
uv run academic-deck compare-grammars --deck <deck.yaml> --out <bakeoff> --fail-on-layout
uv run academic-deck repair-plan --manifest <bakeoff>/GRAMMAR_REPAIR_HINTS.json --out <bakeoff>
uv run academic-deck repair-draft --deck <deck.yaml> --manifest <bakeoff>/GRAMMAR_REPAIR_HINTS.json --out <draft>
uv run academic-deck html-pptx --deck <draft>/deck.repair.yaml --out <draft>/render --fail-on-layout
```

Accept the draft only when `quality-report.md` has zero errors and
`layout-audit-report.md` has zero blocking errors and zero proof/artifact or
cover-image scale warnings. If a forced grammar still reports
`proof-image-small`, either switch to a clean shortlisted grammar, set a more
dominant explicit proof layout, split the slide, or replace the image with a
source crop that carries the claim at slide scale.

The native `build` route also accepts `--fail-on-layout`. Use it when editable
PPTX or Beamer output is required but the same HTML overlap, useful-fill, and
image-source gates should still block delivery:

```bash
uv run academic-deck build --deck <deck.yaml> --out <native-out> --fail-on-layout
```

This native route uses the HTML render as a proxy gate for source safety,
overlap, image contracts, proof scale, and useful-fill. It does not claim to be
a full per-shape PowerPoint or LaTeX PDF geometry audit; render and inspect the
native contact sheets before final delivery.

Read image scale warnings precisely:

- `proof-image-small` / `artifact-image-small` mean the visible source pixels
  are too small; tighter crop, better source image, or a larger source slot may
  help.
- `proof-image-rendered-small` / `artifact-image-rendered-small` mean the
  actual rendered source rectangle is below the projection readability target,
  even if the CSS slot itself looks large.
- `proof-image-upscaled-too-much` / `artifact-image-upscaled-too-much` mean the
  slot enlarged a low-resolution crop beyond useful source pixels. Replace the
  image, crop from a higher-resolution source, or reduce the slot.
- `proof-small` / `artifact-small` mean the container itself is too small; do
  not treat this as a crop-only problem. Use a stronger layout intent, change
  grammar, shorten side content, or split the slide.
- `useful-fill-low` means the slide has frames, rules, or whitespace without
  enough useful text/source evidence. Add a real claim, enlarge the proof
  surface, or split away decorative structure.
- `artifact-role-underfeatured` means a source-heavy screenshot, repo, table,
  paper page, benchmark, homepage, or UI is acting as evidence but is rendered
  like decoration. Use a larger artifact layout, crop tighter, or demote the
  image to an identity cue.
