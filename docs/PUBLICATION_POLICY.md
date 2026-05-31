# Publication Policy

This repository is meant to be public and reusable. Keep the compiler, public neutral examples, design notes, and skills here. Keep harvested personal material out.

## Commit

- `src/academic_deck_compiler/`
- `templates/`
- `tests/`
- `docs/` files that describe generic workflows
- `.codex/skills/` files that do not contain private fixture details
- generated `.agents/skills/` and `.claude/skills/` bridge files
- neutral examples such as `examples/starter`, `examples/paper-talk`, and `examples/tech-review`
- `README.md`, `README_zh.md`, `.gitignore`, `pyproject.toml`

## Do Not Commit

- private CVs, interview notes, local portfolio decks, or personal screenshots
- harvested researcher profile fixtures
- generated PPTX/PDF/HTML screenshot outputs
- browser screenshots and asset caches from real people or projects
- cloned reference repositories under `vendor/` or `references/`
- local API keys, cookies, browser profiles, or `.env` files

The `.gitignore` is intentionally strict about `outputs/`, `vendor/`, `references/`, `examples/people-profiles/`, and personal portfolio fixtures.

## Public Examples

Examples should be neutral and reusable. They can describe paper talks, technical reviews, and research portfolios, but they should not publish real people's profile data unless the repository owner explicitly decides to add a sanitized, licensed example.

## Reference Projects

When using external projects as design references, link to them in documentation instead of vendoring full copies:

- reveal.js: <https://github.com/hakimel/reveal.js>
- Slidev: <https://github.com/slidevjs/slidev>
- Marp: <https://github.com/marp-team/marp>
- beautiful-html-templates: <https://github.com/zarazhangrui/beautiful-html-templates>

If a local workflow needs a reference checkout, clone it into `vendor/` and leave it untracked.
