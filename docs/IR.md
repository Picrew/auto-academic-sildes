# Deck IR

The compiler uses `deck.yaml` as the source of truth. Renderers should not invent content. Agents may revise the YAML, but every rendered slide should trace back to this file.

## Top-Level Fields

- `deck_id`: stable slug used for output filenames.
- `title`: deck title or speaker/person/product name.
- `subtitle`: deck-level positioning line.
- `footer`: short footer shown after the cover.
- `contact`: optional final-slide contact string.
- `assets_dir`: image folder. Relative paths are resolved first against the deck file's folder, then against the repo root.
- `slides`: ordered list of slide objects.

## Slide Fields

- `kind`: one of `cover`, `thesis`, `map`, `split`, `process`, `evidence`, `matrix`, `system`, `loop`, `product`, `stack`, `close`.
- `kicker`: short section label.
- `title`: action title. It should state a judgment.
- `subtitle`: one supporting sentence.
- `layout`: optional safety intent when automatic grammar choice is unsafe. Use this sparingly, such as `proof-showcase` for a dominant screenshot/figure or `artifact-showcase` for a source-backed content slide. These two showcase intents ask the renderer for a larger, safer proof relationship; the active visual grammar still chooses the exact composition.
- `bullets`: concise evidence or reasoning. Prefer 0-3; avoid more than 4 except for `matrix` rows.
- `metrics`: pairs of `value` and `label`.
- `labels`: short tags used by structural layouts.
- `image`: filename inside `assets_dir`. Use this only as a cover identity
  fallback. Non-cover screenshots, figures, repo pages, product screens, and
  paper crops should live in `evidence.image`; if a legacy non-cover `image`
  remains, it must mirror the exact same file as `evidence.image`.
- `evidence`: optional proof object with `image`, normalized finite `crop`,
  `caption`, `source`, and up to three finite-position `callouts`.
- `note`: optional speaker/contact/source note.

## Layout Intent

Each slide kind is a reusable pattern:

- `cover`: identity, topic, credibility anchors.
- `thesis`: the central argument and through-line.
- `map`: narrative spine or mental model.
- `split`: contrast two mechanisms or alternatives.
- `process`: 3-step method or intervention.
- `evidence`: claim plus result, figure, metric, or table.
- `matrix`: taxonomy, system surface, or capability grid.
- `system`: architecture, pipeline, interface, or failure propagation.
- `loop`: production feedback loop, training loop, or evaluation loop.
- `product`: real UI or shipped artifact as evidence.
- `stack`: strengths, agenda, or fit.
- `close`: conclusion and discussion hooks.

The optional `layout` field can force or guide a composition when the proof image
or text density needs stricter control:

- `layout: proof-showcase`: semantic safety intent for an evidence, loop, or product slide that needs a large proof surface and compact side notes. It resolves to a grammar-specific proof composition such as `proof-dossier`, `proof-atlas-spread`, `proof-ledger`, `proof-marginalia`, or `proof-gallery-split`.
- `layout: artifact-showcase`: semantic safety intent for an image-backed content slide where the source artifact must be readable rather than decorative. It resolves to a grammar-specific artifact composition such as `artifact-dossier`, `artifact-ledger`, or `artifact-marginalia`.
- `layout: proof-stage`, `proof-dossier`, `proof-atlas-spread`, `matrix-ledger`, `cover-source-rail`, and related named `data-composition` values are also accepted when a grammar bake-off identifies a specific successful composition.
- Aliases such as `proof-dominant`, `image-dominant`, and `artifact-dominant` normalize to the safe showcase layouts.

Use `layout` after a render or audit shows small proof images, letterboxing,
crowded side notes, or repeated template cadence. Do not use it as decoration.

## Image Contract

Images are role typed before rendering:

- `cover` top-level `image`: small identity/context anchor only.
- `evidence.image`: proof or artifact source that can be cropped, captioned,
  sourced, and audited.
- raw HTML images or non-cover bare `image` fields: invalid delivery input.

The compiler rejects unknown visual grammars, non-cover image/evidence mismatch,
missing non-cover evidence crops, non-finite crop/callout coordinates, and
foreground pseudo overlays before a deck is accepted for export.

## Minimal Deck

```yaml
deck_id: my-paper-talk
title: My Paper Title
subtitle: A one-line claim about why the work matters
footer: Author / Venue
contact: repo or email
assets_dir: assets/images
slides:
  - kind: cover
    kicker: Research talk
    title: The central claim in plain language
    layout: cover-source-rail
    subtitle: Venue, author, context
    metrics:
      - value: "1"
        label: central contribution
    labels: [Problem, Method, Result]
    evidence:
      image: result-figure.png
      crop: {x: 0.08, y: 0.12, w: 0.84, h: 0.72}
      caption: The cropped panel should prove the action title.
      source: Paper figure, table, product screenshot, or internal evaluation note
      callouts:
        - {x: 0.72, y: 0.32, text: effect visible here}
```

For `matrix` slides, `labels` define the row names and `bullets` may define row semantics:

```yaml
labels: [Execution, Tooling, Context]
bullets:
  - "Execution: branching plans fail -> logs + rollback gates"
  - "Tooling: API state drifts -> typed wrappers + traces"
  - "Context: memory stales out -> scoped state windows"
```

The text before `->` becomes the failure controlled; the text after `->` becomes the artifact column.

## Future Schema Direction

The next schema revision should add first-class `assets`, `citations`, `speaker_notes`, and `theme` fields. For now, the YAML stays deliberately small so Codex and Claude Code can edit it easily.
