---
name: public-profile-deck
description: Create public-source researcher, lab, company, or project profile decks with restrained claims, web evidence, homepage/project screenshots, and HTML-first visual review.
---

# Public Profile Deck Bridge

This is a generated bridge for `public-profile-deck`.
The canonical workflow lives in `.codex/skills/public-profile-deck/SKILL.md`.

## Instructions

1. Read `.codex/skills/public-profile-deck/SKILL.md` before doing substantive work.
2. Follow the canonical skill as the source of truth for commands, quality gates, artifacts, and review criteria.
3. For full deck work, also read `docs/AGENT_WORKFLOW.md` and treat slide generation as a compiler loop: source, IR, render, audit, inspect, revise.
4. Keep generated outputs under `outputs/` and avoid hand-patching final PPTX files unless the user explicitly asks.

Edit the canonical `.codex/skills` file, then run `uv run python scripts/sync_agent_skill_bridges.py` to refresh this bridge.
