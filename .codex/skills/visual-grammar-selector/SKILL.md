---
name: visual-grammar-selector
description: Select varied tasteful visual grammars for HTML-first academic and technical decks so outputs do not look like one repeated template.
---

# Visual Grammar Selector Skill

Pick a visual grammar before rendering. Do not default every deck to the same palette, layout cadence, or typography rhythm.

## Available Grammars

- `editorial-profile`: public researcher, lab, or portfolio profile.
- `swiss-systems`: systems, architecture, benchmarks, infrastructure.
- `dark-lab-notebook`: frontier AI, experiments, agent traces, dense research notes.
- `paper-atlas`: paper reading, survey, citation-heavy academic decks.
- `keynote-evidence-wall`: demos, launch-style research talks, visual proof-heavy pitches.
- `highsense-gallery`: high-end web editorial feel for profile or product-research decks.
- `academic-homepage-grid`: PRISM-like academic homepage structure for dense researcher/project profiles.
- `prism-dossier`: polished academic homepage dossier with identity rail and selected-work flow.
- `fathom-research-brief`: scientific information-design memo for benchmarks, systems, and evaluation.
- `jetset-theory-grid`: strong typographic grid for conceptual theory and method framing.
- `monograph-review`: PRISM + Information Architects academic monograph style; dense, source-linked, serif/sans, no decoration.
- `broadside-lab`: Huashu Broadside / editorial manifesto style; dark, typographic, single fire accent, useful for strong research claims.
- `catalog-atelier`: curated research-catalog style; warm paper, sage/terracotta, gallery rhythm, good for people/project evidence decks.
- `evidence-atelier`: curated proof-artifact wall; warm paper, terracotta, irregular bento/index pages.
- `atlas-marginalia`: annotated academic atlas; near-white page, blue source accent, plate plus marginal note rail.
- `systems-field-manual`: operational systems/benchmark manual; hard grid, ledger rows, one orange signal color.
- `lab-trace-ledger`: dark experimental trace ledger for agent/RL/reasoning behavior decks.
- `object-study-wall`: gallery-like object/source study wall for project and public artifact profiles.
- `forest-editorial-brief`: warm editorial forest profile grammar; polished academic without template flavor.
- `cobalt-research-grid`: hard cobalt technical grid for systems, benchmarks, and tool-use evidence.
- `vellum-research-note`: formal dark research-note grammar for seminars, thesis, and paper defenses.
- `mono-ink-ledger`: monochrome dossier/handout grammar for source-linked reviews.
- `neo-grid-lab`: high-energy neon grid for demos, AI products, and engineering showcases.
- `prism-clean-room`: PRISM-like clean academic homepage grammar with denser publication/profile flow and no card gloss.
- `prism-publication-stack`: publication-forward academic homepage stack for people/lab/project profiles.
- `prism-newsroom-index`: PRISM-like academic news/index grammar for selected work, papers, and public-source profiles.
- `ia-research-archive`: Information Architects-style source archive with marginal rails, blue source links, and dense text-first proof.
- `broadsheet-data-room`: dense broadsheet/data-room grammar for benchmark reviews, paper dossiers, and source-heavy profiles.
- `pentagram-gridnote`: bold typographic gridnote for methods, claims, and systems talks that need poster-level confidence.
- `takram-research-system`: calm research systems memo with precise grids, thin rules, and quiet proof-first evidence.
- `stamen-data-map`: cartographic/data-map grammar for project, benchmark, geography, or public-source evidence decks.
- `couture-exhibition`: high-end editorial exhibition grammar with large proof plates and wall-label captions.
- `js-editorial-cascade`: high-sense web editorial cascade with asymmetric proof staging and strong type/image contrast.
- `sumi-research-scroll`: ink-and-paper research scroll for source-indexed academic profiles and marginal proof reading.
- `huashu-editorial-lab`: Huashu-inspired typographic lab grammar with hard grid, one accent, and anti-cliche discipline.
- `huashu-build-board`: Huashu Build-style hard benchmark board with oversized metrics and black/red rule structure.
- `huashu-issue-broadsheet`: Huashu-style issue broadsheet for bold technical profiles, benchmarks, and handout-like evidence boards.
- `gallery-proof-room`: warm gallery proof-plate grammar for artifact-rich public profiles and project evidence decks.
- `prism-workbench-index`: PRISM-inspired researcher workbench with selected-work rows and compact source-index pages.
- `signal-intelligence-brief`: institutional briefing grammar with source ledgers, serif authority, and restrained signal accents.
- `raw-grid-research`: neobrutalist research board for benchmarks, demos, and methods that need hard-framed confidence.
- `stencil-field-tablet`: archival field-manual grammar with colored tablets for mapped projects, surveys, and source specimens.
- `maison-research-catalog`: high-end catalog grammar for public profile/project decks with dominant source plates.
- `folio-swiss-noir`: black/white Swiss folio grammar for severe method, benchmark, and source-exhibit decks.
- `chromatic-research-map`: chromatic map grammar for benchmark terrain, research geographies, and multi-threaded public evidence.

## Selection

- High-taste public researcher/profile defaults: `forest-editorial-brief`, `object-study-wall`, or `evidence-atelier`.
- Conservative public researcher/profile default: `academic-homepage-grid` or `prism-dossier`.
- People/profile fallback: `editorial-profile`.
- Tooling, systems, benchmarks: `systems-field-manual`; use `swiss-systems` as a quieter fallback.
- RL, agents, frontier model work: `dark-lab-notebook`.
- Literature review or paper talk: `paper-atlas`.
- Demo or product-research story: `keynote-evidence-wall`.
- When the user asks for "高级感" or a less templated public profile: `highsense-gallery`.
- When the user asks for academic personal homepage taste or fuller research-profile layouts: `academic-homepage-grid`.
- When profile decks feel too sparse or résumé-like: compare `academic-homepage-grid` and `prism-dossier`.
- When PRISM-inspired decks still feel too much like cards or résumé blocks: compare `prism-clean-room`.
- When the profile has enough papers/projects to behave like a homepage publication list: compare `prism-publication-stack`.
- When a profile needs news/index density rather than a résumé arc: compare `prism-newsroom-index`.
- When a deck should read like a serious source archive rather than a talk template: try `ia-research-archive`.
- When evidence and comparisons should read like a newspaper/data room: try `broadsheet-data-room`.
- When claims depend on measurements, benchmarks, or source-linked evaluation: use `fathom-research-brief`.
- When the deck needs a bold reset and can survive a sharper typographic voice: use `jetset-theory-grid`.
- When the deck needs a poster-grade typographic reset without neon or gradients: try `pentagram-gridnote`.
- When a technical story needs calm product/research-system taste: try `takram-research-system`.
- When the content is project geography, benchmark terrain, or public web evidence: try `stamen-data-map`.
- When the deck needs high-end web/editorial atmosphere without AI gloss: try `couture-exhibition`.
- When the user explicitly wants HTML taste translated into slides, compare `js-editorial-cascade` for web-editorial asymmetry and `sumi-research-scroll` for a quieter ink-scroll academic reading.
- When the deck needs Huashu-style typographic confidence and hard critique discipline: try `huashu-editorial-lab`.
- When benchmark/system claims need a hard Build-style board: try `huashu-build-board`.
- When a profile or benchmark deck needs a bolder issue-board treatment without gradients: try `huashu-issue-broadsheet`.
- When source artifacts are the strongest material and should dominate: try `gallery-proof-room`.
- When PRISM-style decks feel card-like and need a selected-works index instead: try `prism-workbench-index`.
- When a profile feels too card-like or too ordinary: compare `monograph-review` and `catalog-atelier`.
- When a systems/profile deck needs stronger stage presence without gradients: try `broadside-lab`.
- When a deck has strong source artifacts but feels pasted together: compare `evidence-atelier` and `object-study-wall`.
- When a profile needs warmth and editorial maturity without becoming decorative: try `forest-editorial-brief`.
- When systems evidence needs more technical bite than `systems-field-manual`: try `cobalt-research-grid`.
- When the deck should feel like a formal research note or defense: try `vellum-research-note`.
- When the output is closer to a dossier or handout than a stage talk: try `mono-ink-ledger`.
- When the brief is demo/product/engineering and can tolerate a loud grid: try `neo-grid-lab`.
- When paper/profile material needs source annotation over stage presence: try `atlas-marginalia`.
- When tool-use or benchmark material looks like a generic summary: try `systems-field-manual`.
- When agent/RL material needs a dark research mood without generic neon AI flavor: try `lab-trace-ledger`.

## Current Judging Bias

The historic strict bake-offs across Fixture A and Fixture B fixtures
cleared zero blocking layout errors, but renderer-wide safety rules have since
become stricter. The default pool is now 42 grammars after adding
`signal-intelligence-brief`, `raw-grid-research`, `stencil-field-tablet`, and
the Maison/Folio/Chromatic high-sense triad.
The latest focused layout-contract pass cleared `gallery-proof-room`,
`js-editorial-cascade`, `raw-grid-research`, `stencil-field-tablet`, and
`huashu-issue-broadsheet` across the two fixtures with populated
`Image Contracts`, zero blocking errors, and zero strict warnings. The latest
overlap/image repair also cleared `academic-homepage-grid` on both Fixture A and
Fixture B after compact proof layouts stopped rendering callout-note
lists and source-heavy artifacts were enlarged to roughly 1000x556 visible
source pixels. It ranks
`forest-editorial-brief`,
`object-study-wall`, `evidence-atelier`, and `cobalt-research-grid` as the
highest-taste default pool, while `academic-homepage-grid`, `prism-dossier`,
`prism-clean-room`, `prism-publication-stack`, `prism-newsroom-index`, and
`prism-workbench-index`
remain conservative or publication-forward profile defaults. Treat `vellum-research-note`,
`broadsheet-data-room`, `mono-ink-ledger`, `atlas-marginalia`, `monograph-review`, `paper-atlas`,
`catalog-atelier`, `ia-research-archive`, and `fathom-research-brief` as formal/dossier special cases.
Treat `neo-grid-lab`, `jetset-theory-grid`, `keynote-evidence-wall`, and
`broadside-lab` as deliberate resets, not defaults; `pentagram-gridnote` and
`huashu-editorial-lab`, `huashu-build-board`, and `huashu-issue-broadsheet` are more formal typographic resets, while
`couture-exhibition`, `gallery-proof-room`, and `js-editorial-cascade` are editorial proof-plate or web-editorial resets, and `sumi-research-scroll` is an ink-scroll source-index reset. Avoid selecting a grammar only because its
palette differs from another variant.

Warnings affect ranking even when they do not block export: `proof-image-small`
and `proof-image-rendered-small` mean the source pixels are underfeatured,
`artifact-image-rendered-small` means a source panel will not read at projection
scale, `callout-overlap` means the annotation layer needs repair,
`proof-caption-missing` / `proof-caption-generic` / `artifact-caption-generic`
mean the image lacks source context, `caption-text-too-small` /
`caption-contrast-low` mean the source note is not readable enough,
`label-contrast-low` means support labels fit but are not visually legible, and
`decorative-image-too-small` means a cover image is only an identity cue, not
evidence. `title-wrap-deep` and `subtitle-wrap-deep` mean the copy is close to
using the slide like a document; shorten or split before delivery. In strict
export, these warning gates fail `--fail-on-layout`.

Read `layout-audit-report.md` before trusting any shortlist. The `Image
Contracts` table should show proof and artifact images with enough rendered
source pixels, useful visible area, healthy slot use, and crop/caption/source
status. A visually polished grammar is not ready if the table shows a source
surface as a small identity cue or an uncropped decorative image.
For repo, UI, paper, table, benchmark, project-page, or homepage screenshots,
look for about 980x540 rendered source pixels or better. If the source-heavy
surface falls below roughly 820x460, repair the crop or slot before judging
style.

Before finalizing a selection, reject empty modules and repeated artifacts:
labels, metrics, bento cells, and evidence boxes need real content; the same
homepage/screenshot should not appear more than twice unless the crop and slide
job change.

Renderer truncation is a source error, not a layout trick. Do not submit more
bullets, metrics, labels, or callouts than the renderer can display; split the
slide, convert to a matrix, or move detail into notes. A wide cover screenshot
must use an `evidence:` crop/caption/source contract, not bare `image:`.

Use the diversified shortlist, not just the highest raw score. `compare-grammars`
reports `Shortlist Diversity` with a style family and composition family for
each ready grammar, and also writes `DESIGN_DIRECTIONS.md` with a 20+ school
direction library. Read that direction report before picking a winner: choose a
safe academic base, a proof-forward editorial route, and a bold reset for the
showcase. A shorter shortlist is acceptable when the remaining clean variants
are near-siblings; do not add another PRISM/homepage variant merely to fill a
quota. Prefer one academic-homepage, one proof-gallery, one systems-grid, one
formal-dossier, and one Huashu/bold reset direction when they are clean.

When the brief says the current output is too ordinary, too fixed in palette, or
too template-like, start with:

```bash
uv run academic-deck compare-grammars --deck <deck.yaml> --out <out> --grammars highsense-20 --fail-on-layout
```

The `highsense-20` preset is a curated reference pass, not a random sample: it
mixes PRISM academic homepage structures, source archives, Beautiful HTML
Templates families (`signal`, `raw-grid`, `stencil-tablet`), JS web-editorial
proof staging, Huashu issue boards, gallery proof rooms, and the
Maison/Folio/Chromatic triad. Inspect the stacked overview before choosing.
In `compare-grammars`, `--fail-on-layout` should leave rejected candidates in
the report and fail only when no clean shortlist variant remains. The final
selected grammar still must pass single-route export with zero hard layout
errors and zero strict image/density warnings.

For a tone-first template scan before grammar selection, use:

```bash
uv run academic-deck template-shortlist --brief "<occasion + mood + content>" --out <out>
```

After choosing, read the matching `templates/<grammar>/DESIGN.md`.

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
- `content-workbench-index`: selected-work rows with a compact claim column.

A pass is not diverse if every candidate has the same composition sequence with only palette changes.
