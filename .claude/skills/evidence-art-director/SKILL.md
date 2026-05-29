---
name: evidence-art-director
description: Choose, crop, and judge images for tasteful research slides, prioritizing proof surfaces over decoration.
---

# Evidence Art Director Skill

Use result figures, system diagrams, project pages, repos, leaderboards, and paper pages as proof. Use portraits and logos only as small identity cues.

Crop tightly, keep labels readable, add at most three pins, and run:

```bash
uv run academic-deck evidence --deck <deck.yaml> --out <out>
```

## Evidence Mix

- Read the `Evidence Mix` section of `evidence-report.md`.
- Public profiles need identity evidence plus work evidence; a homepage alone is not enough.
- Prefer a varied source set: homepage/profile, project page, repo, paper/result figure, benchmark/leaderboard, or product workflow.
- If the report says `untyped evidence`, improve filename, caption, or `evidence.source` before polishing layout.
