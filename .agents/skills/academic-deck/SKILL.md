---
name: academic-deck
description: Build and refine claim-led academic or technical slide decks with Academic Deck Compiler. Use when the user asks for tasteful research slides, PPTX, Beamer, paper talks, technical portfolios, or multi-agent slide iteration.
---

# Academic Deck Bridge

This is a generated bridge for `academic-deck`.
The canonical workflow lives in `.codex/skills/academic-deck/SKILL.md`.

## Instructions

1. Read `.codex/skills/academic-deck/SKILL.md` before doing substantive work.
2. Follow the canonical skill as the source of truth for commands, quality gates, artifacts, and review criteria.
3. For full deck work, also read `docs/AGENT_WORKFLOW.md` and treat slide generation as a compiler loop: source, IR, render, audit, inspect, revise.
4. Keep generated outputs under `outputs/` and avoid hand-patching final PPTX files unless the user explicitly asks.

Edit the canonical `.codex/skills` file, then run `uv run python scripts/sync_agent_skill_bridges.py` to refresh this bridge.
