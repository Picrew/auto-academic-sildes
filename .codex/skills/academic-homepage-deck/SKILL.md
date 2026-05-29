---
name: academic-homepage-deck
description: Build HTML-first researcher or project profile slides that borrow the information architecture of polished academic homepages such as PRISM, with dense but clean identity, publication, project, and news-style layouts.
---

# Academic Homepage Deck Skill

Use when public researcher, lab, or project information should become slides without looking like a generic AI portfolio.

## Workflow

1. Gather public identity sources: homepage, Google Scholar/OpenReview/DBLP, project pages, selected papers, and GitHub when relevant.
2. Choose `visual_grammar: academic-homepage-grid` for profile decks that need clean density.
3. Structure slides like a homepage:
   - identity rail: name, role, institution, interests, public links
   - about block: one careful research positioning paragraph
   - publication/project cards: selected works only, with venues and one-line contribution
   - news/result rows: dated or metric-backed signals
   - evidence card: one large homepage, paper figure, leaderboard, or repo artifact
4. Put `image`/`evidence` on ordinary content slides when the claim needs a source artifact; the renderer will turn it into an artifact panel instead of a decorative thumbnail.
5. Run `uv run academic-deck html-pptx --deck <deck.yaml> --out <out> --fail-on-layout`.
6. Inspect `layout-audit-report.md` and `html-contact-sheet.png`; fix overlap, text overflow, viewport overflow, unloaded images, image overflow, tiny proof/artifact images, underfilled slides, and weak crops before judging taste.

## Rules

- Fill the slide with useful structure, not decorative objects.
- Leave whitespace around real groups, but avoid half-empty pages with tiny type.
- Use homepage screenshots as identity anchors, not as the only evidence.
- Prefer selected publications/projects over exhaustive CV lists.
- Keep claims restrained; public profiles should not infer private career narratives.
- Do not accept a slide with barely fitting text. Tighten the copy, change the layout, or crop the evidence differently.
- Screenshots must be proof surfaces: readable, cropped to the meaningful region, and supported by a caption/source line.

## Output

Return the deck path, rendered HTML, PPTX export, contact sheet, and layout audit status.
