---
name: design-context-protocol
description: 'Run a disciplined design-context workflow for HTML-first slides: verify facts, collect assets, choose visual grammar, make 2-slide showcases, compare directions, and critique outputs to avoid AI-slop.'
---

# Design Context Protocol Bridge

This is a generated bridge for `design-context-protocol`.
The canonical workflow lives in `.codex/skills/design-context-protocol/SKILL.md`.

## Instructions

1. Read `.codex/skills/design-context-protocol/SKILL.md` before doing substantive work.
2. Follow the canonical skill as the source of truth for commands, quality gates, artifacts, and review criteria.
3. For full deck work, also read `docs/AGENT_WORKFLOW.md` and treat slide generation as a compiler loop: source, IR, render, audit, inspect, revise.
4. Keep generated outputs under `outputs/` and avoid hand-patching final PPTX files unless the user explicitly asks.

Edit the canonical `.codex/skills` file, then run `uv run python scripts/sync_agent_skill_bridges.py` to refresh this bridge.
