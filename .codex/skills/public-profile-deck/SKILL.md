---
name: public-profile-deck
description: Create public-source researcher, lab, company, or project profile decks with restrained claims, web evidence, homepage/project screenshots, and HTML-first visual review.
---

# Public Profile Deck Skill

Use this for people or organizations when the inputs are public web pages.

## Workflow

1. Verify at least one identity source and one work source.
2. Capture evidence screenshots: homepage/profile, project page, paper page, repo, benchmark, or leaderboard.
3. Write claim-led slides without implying endorsement or private knowledge.
4. Prefer the six-slide profile spine only as a starting point: cover, signature, contribution map, identity evidence, artifact evidence, synthesis.
5. Put every non-cover screenshot, repo, paper page, benchmark, or project page into an `evidence:` block with `evidence.image`, finite crop, caption, and source; use a full-frame crop only for images already pre-cropped for slide use.
6. Export with `uv run academic-deck html-pptx`.
7. Read `quality-report.md` for text budget errors before judging visuals.
8. Read `evidence-report.md` and verify `Evidence Mix` includes identity evidence plus at least one work artifact.

## Taste Rules

- Use portraits only as small identity cues.
- Use project pages, paper figures, leaderboards, and repos as primary proof.
- Do not let a profile deck rely only on homepages, portraits, or logos.
- Do not use bare `image:` fields, image/evidence mismatches, or missing crops outside the cover; they bypass crop, caption, source, and text-image clearance checks.
- Rewrite over-budget biography text into shorter claims; do not shrink dense copy until it merely fits.
- Replace "A strong X deck should..." with final-reader synthesis.
- Vary wording after each deck; avoid repeated "public arc" and "visible work" patterns.
- Store URLs in `evidence.source`.

Read `docs/PUBLIC_PROFILE_WORKFLOW.md` before writing a public profile deck.
