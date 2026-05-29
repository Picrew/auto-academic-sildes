---
name: evidence-art-director
description: Choose, crop, and judge images for tasteful research slides, prioritizing proof surfaces over decorative screenshots, portraits, logos, or generic AI visuals.
---

# Evidence Art Director Skill

Use when slides need screenshots, figures, project pages, paper pages, charts, tables, or product visuals.

## Priority Order

1. Result figures, architecture diagrams, trace views, tables, and leaderboards.
2. Project pages or repos that show artifact shape.
3. Paper title pages when the title itself proves the claim.
4. Homepages and profiles for identity only.
5. Portraits and logos only as small cues.

## Crop Rules

- Crop the smallest readable region that proves the claim.
- One proof object per slide is usually enough.
- Add at most three pins; each pin must explain a judgment.
- If a chart label is unreadable, crop tighter or redraw natively.
- Do not use images just because the slide feels empty.
- Treat source-heavy screenshots differently from identity imagery. Repos, UIs, tables, benchmarks, paper pages, project pages, and homepages need slide-scale source pixels and should trigger a larger artifact/proof slot when they carry the claim.
- If a source-heavy screenshot only works as a small visual cue, rewrite the slide so it is clearly identity/context, or replace it with a crop that can be inspected.

Run `uv run academic-deck evidence --deck <deck.yaml> --out <out>` before visual QA.

## Evidence Mix

- Read the `Evidence Mix` section of `evidence-report.md`.
- Public profiles need identity evidence plus work evidence; a homepage alone is not enough.
- Prefer a varied source set: homepage/profile, project page, repo, paper/result figure, benchmark/leaderboard, or product workflow.
- If the report says `untyped evidence`, improve filename, caption, or `evidence.source` before polishing layout.
