# Agent Workflow

This repository is designed for iterative Codex or Claude Code use. The agent should treat slide generation as compilation, not decoration.

## Skill Entrypoints

Use the repo skills as the normal entrypoint for agent work:

- Codex: invoke `$academic-deck`, `$html-first-deck`, `$paper-to-html-talk`, `$public-profile-deck`, or `$deck-iteration-judge`.
- Claude Code: invoke the matching slash skill, such as `/academic-deck`, `/html-first-deck`, `/paper-to-html-talk`, `/public-profile-deck`, or `/deck-iteration-judge`.

Skill directories are intentionally split by tool:

- `.codex/skills/` is the canonical source for detailed skill instructions.
- `.agents/skills/` contains generated Codex bridge skills.
- `.claude/skills/` contains generated Claude Code bridge skills.

Edit only the canonical `.codex/skills/<skill>/SKILL.md` file, then run:

```bash
uv run python scripts/sync_agent_skill_bridges.py
uv run python scripts/sync_agent_skill_bridges.py --check
```

## Loop

1. **Ingest**: read the paper, CV, repo, screenshots, or project notes. For folders, start with `uv run academic-deck ingest --source <source-folder> --out <source-pack>`.
2. **Narrative**: write a ghost deck with only action titles.
3. **Direction**: choose three design directions before bulk rendering: one safe academic base, one proof-forward editorial route, and one bold reset. `compare-grammars` writes `DESIGN_DIRECTIONS.md` for this step.
4. **Evidence**: select images, tables, metrics, and citations that prove each claim; run `academic-deck evidence` to audit the local asset pool.
5. **IR**: encode the deck in `deck.yaml`.
6. **Render**: build the HTML-first deck and export image-based PPTX.
7. **Audit**: run `html-pptx` or `compare-grammars` with `--fail-on-layout`.
8. **Preview**: inspect contact sheets and selected full-size slides.
9. **Judge**: run automated checks, then use human or subagent critique.
10. **Revise**: change the IR, assets, or renderer patterns. Do not patch the final PPTX by hand unless the user asks.

## Subagent Roles

- **Narrative critic**: checks whether every slide advances one through-line.
- **Evidence curator**: rejects decorative images and asks what each figure proves.
- **Aesthetic judge**: reviews rhythm, type hierarchy, cropping, and AI-template smell.
- **Renderer engineer**: fixes code, schema, and export reliability.
- **Route judge**: decides whether PPTX-native, Beamer, or a hybrid output is best for the audience.

## Rules For Agents

- Prefer HTML-first as the default route for portfolio, public-profile, and high-design technical talks.
- Export PPTX as full-slide images when visual fidelity matters more than editability.
- Use PPTX-native only when the user must edit shapes in PowerPoint.
- Use Beamer as a backup or formal PDF route.
- When using PPTX-native or Beamer for delivery, still pass `--fail-on-layout`
  so the HTML audit blocks overlap, useful-fill, and image-source failures.
- Treat `DESIGN_DIRECTIONS.md` as the style-selection brief: pick a direction school before picking a final grammar.
- Use action titles; topic titles are not enough.
- Keep every slide to one judgment.
- Treat `quality-report.md` as the pre-render hard gate: over-budget title, bullet, metric, label, caption, or dense CJK copy must be rewritten before visual polish.
- On image-backed slides, respect the combined module budget across bullets, metrics, labels, and callouts. If the proof or artifact page is over budget, split it before touching CSS.
- Make evidence readable at 1920x1080 preview size.
- Treat `evidence-report.md` as the image-selection ledger: each primary proof object needs a claim, crop, caption, source, and at most three inspection pins.
- Treat `layout-audit-report.md` as the hard gate: text overlap, text-image overlap, text clearance, image scale, image overflow, source-context warnings, and callout placement errors block export.
- Treat `useful-fill-low` and `artifact-role-underfeatured` as hard taste failures under `--fail-on-layout`. A slide can be geometrically clean and still fail if the useful content is sparse or the source-heavy artifact is too small to inspect.
- If a grammar fails because caption text, proof notes, artifact notes, or side bullets collide with the image, preserve the image surface first. Shorten or hide secondary notes, switch to `proof-showcase` / `artifact-showcase`, split the slide, or crop tighter before reducing proof size.
- Do not accept "almost touching" text. `text-clearance-tight`, `text-block-clearance-tight`, and `figure-caption-clearance-tight` are treated as failures because projected slides need breathing room, not only non-overlap.
- Put every non-cover image through an `evidence:` contract with `evidence.image`, an explicit finite crop, caption, and source. Bare `image:` fields, top-level/evidence image mismatches, or missing crops on content, evidence, loop, or product slides are rejected because they bypass crop, caption, source, and clearance checks.
- Treat unknown `visual_grammar` values and foreground pseudo overlays as source/render failures, not acceptable fallbacks.
- Keep callouts to at most three. More pins is a source error because extra annotations would disappear or crowd the proof surface.
- Use `--skip-layout-audit` only for fast exploration. It is incompatible with `--fail-on-layout`, and shortlisted or deliverable variants must run the DOM audit.
- Do not use logos, avatars, or abstract art as evidence.
- Keep vendor projects in `vendor/` as references; do not make the user depend on all of them.
- Record accepted and rejected critique in `quality-report.md`, `ROADMAP.md`, or a review note.

## Review Bundle

A good completed iteration should include:

- source `deck.yaml`
- PPTX
- PPTX-rendered PDF
- Beamer PDF
- contact sheets
- `judge-report.md`
- `quality-report.md`
- `evidence-report.md`
- known issues and next steps
