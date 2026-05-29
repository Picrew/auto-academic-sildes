---
name: grammar-token-designer
description: Translate a slide DESIGN.md or high-end web reference into renderer-ready visual grammar tokens for HTML-first academic or technical decks.
---

# Grammar Token Designer Skill

Use before editing renderer CSS or creating a new visual grammar.

## Workflow

1. Read the target `templates/<grammar>/DESIGN.md` or a small set of design references.
2. Extract renderer tokens, not vibes:
   - `surface`: base, dark, proof, and annotation backgrounds.
   - `ink`: headline, body, muted, and metadata colors.
   - `accent`: one primary and optional secondary accent.
   - `type`: headline, body, mono, and metric families.
   - `composition`: cover, proof, map/ledger, matrix, close.
   - `cadence`: dark-page ratio, proof-page ratio, and scale contrast.
   - `evidence`: image area, crop priority, caption style, callout style.
3. Convert tokens into a CSS checklist for `render_html.py`.
4. Name anti-patterns the grammar must avoid.

## Rules

- A grammar is not a palette. It must change layout rhythm and proof treatment.
- Tokens must be concrete enough to implement without another design discussion.
- Use neutral bases and deliberate contrast spikes instead of one-note color systems.
- Do not introduce animation-only ideas unless the static screenshot/PPTX export still works.
- If a reference has strong brand styling, borrow structure and cadence only.

## Output

Return:

- `Tokens`: 8-14 concrete values or constraints.
- `CSS hooks`: selectors or variables to touch.
- `Slide cadence`: how cover, evidence, matrix, and close should differ.
- `Do not copy`: brand or decorative details to ignore.
