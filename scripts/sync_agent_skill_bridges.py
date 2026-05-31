from __future__ import annotations

import argparse
import difflib
from dataclasses import dataclass
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / ".codex" / "skills"
TARGET_DIRS = (
    ROOT / ".agents" / "skills",
    ROOT / ".claude" / "skills",
)


@dataclass(frozen=True)
class SkillMetadata:
    slug: str
    name: str
    description: str


def _read_frontmatter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path} is missing YAML frontmatter")
    try:
        _, frontmatter, _ = text.split("---\n", 2)
    except ValueError as exc:
        raise ValueError(f"{path} has malformed YAML frontmatter") from exc

    data: dict[str, object] = {}
    for line in frontmatter.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise ValueError(f"{path} frontmatter line has no ':' separator: {line!r}")
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        data[key.strip()] = value
    return data


def _skill_metadata(path: Path) -> SkillMetadata:
    data = _read_frontmatter(path)
    name = data.get("name")
    description = data.get("description")
    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"{path} frontmatter must include a non-empty name")
    if not isinstance(description, str) or not description.strip():
        raise ValueError(f"{path} frontmatter must include a non-empty description")
    return SkillMetadata(slug=path.parent.name, name=name.strip(), description=description.strip())


def _bridge_content(metadata: SkillMetadata) -> str:
    canonical = f".codex/skills/{metadata.slug}/SKILL.md"
    title = metadata.name.replace("-", " ").title()
    frontmatter = yaml.safe_dump(
        {"name": metadata.name, "description": metadata.description},
        sort_keys=False,
        allow_unicode=False,
        width=10_000,
    ).strip()
    return "\n".join(
        [
            "---",
            frontmatter,
            "---",
            "",
            f"# {title} Bridge",
            "",
            f"This is a generated bridge for `{metadata.name}`.",
            f"The canonical workflow lives in `{canonical}`.",
            "",
            "## Instructions",
            "",
            f"1. Read `{canonical}` before doing substantive work.",
            "2. Follow the canonical skill as the source of truth for commands, quality gates, artifacts, and review criteria.",
            "3. For full deck work, also read `docs/AGENT_WORKFLOW.md` and treat slide generation as a compiler loop: source, IR, render, audit, inspect, revise.",
            "4. Keep generated outputs under `outputs/` and avoid hand-patching final PPTX files unless the user explicitly asks.",
            "",
            "Edit the canonical `.codex/skills` file, then run `uv run python scripts/sync_agent_skill_bridges.py` to refresh this bridge.",
            "",
        ]
    )


def expected_bridges() -> dict[Path, str]:
    bridges: dict[Path, str] = {}
    for source in sorted(SOURCE_DIR.glob("*/SKILL.md")):
        metadata = _skill_metadata(source)
        for target_dir in TARGET_DIRS:
            bridges[target_dir / metadata.slug / "SKILL.md"] = _bridge_content(metadata)
    return bridges


def sync(*, check: bool) -> int:
    failures = 0
    expected_paths = set(expected_bridges())

    for path, expected in sorted(expected_bridges().items()):
        if path.exists():
            current = path.read_text(encoding="utf-8")
        else:
            current = ""
        if current == expected:
            continue
        if check:
            failures += 1
            rel = path.relative_to(ROOT)
            print(f"out of sync: {rel}")
            diff = difflib.unified_diff(
                current.splitlines(),
                expected.splitlines(),
                fromfile=f"{rel} (current)",
                tofile=f"{rel} (expected)",
                lineterm="",
            )
            print("\n".join(diff))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")

    for target_dir in TARGET_DIRS:
        for existing in sorted(target_dir.glob("*/SKILL.md")):
            if existing not in expected_paths:
                if check:
                    failures += 1
                    print(f"unexpected bridge: {existing.relative_to(ROOT)}")
                else:
                    existing.unlink()
                    if not any(existing.parent.iterdir()):
                        existing.parent.rmdir()

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Synchronize generated agent skill bridge files.")
    parser.add_argument("--check", action="store_true", help="fail if generated bridge files are stale")
    args = parser.parse_args()
    return 1 if sync(check=args.check) else 0


if __name__ == "__main__":
    raise SystemExit(main())
