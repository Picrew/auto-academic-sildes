from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / ".codex" / "skills"
TARGET_DIRS = (
    ROOT / ".agents" / "skills",
    ROOT / ".claude" / "skills",
)


def _frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path} is missing frontmatter"
    _, block, _ = text.split("---\n", 2)
    data: dict[str, str] = {}
    for line in block.splitlines():
        if not line.strip():
            continue
        key, _, value = line.partition(":")
        value = value.strip()
        if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
            value = value[1:-1]
        data[key.strip()] = value
    return data


def _canonical_skill_paths() -> list[Path]:
    return sorted(SOURCE_DIR.glob("*/SKILL.md"))


def test_generated_skill_bridges_are_in_sync() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/sync_agent_skill_bridges.py", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_skill_frontmatter_is_strict_yaml() -> None:
    for source in _canonical_skill_paths():
        text = source.read_text(encoding="utf-8")
        _, block, _ = text.split("---\n", 2)
        data = yaml.safe_load(block)
        assert isinstance(data, dict)
        assert data["name"]
        assert data["description"]


def test_each_canonical_skill_has_codex_and_claude_bridge() -> None:
    sources = _canonical_skill_paths()
    assert len(sources) >= 10
    for source in sources:
        for target_dir in TARGET_DIRS:
            target = target_dir / source.parent.name / "SKILL.md"
            assert target.exists(), f"missing bridge for {source.parent.name}: {target}"


def test_bridge_metadata_matches_canonical_metadata() -> None:
    for source in _canonical_skill_paths():
        canonical = _frontmatter(source)
        for target_dir in TARGET_DIRS:
            bridge = _frontmatter(target_dir / source.parent.name / "SKILL.md")
            assert bridge["name"] == canonical["name"]
            assert bridge["description"] == canonical["description"]


def test_bridges_point_agents_to_canonical_workflow() -> None:
    for source in _canonical_skill_paths():
        canonical = f".codex/skills/{source.parent.name}/SKILL.md"
        for target_dir in TARGET_DIRS:
            bridge_text = (target_dir / source.parent.name / "SKILL.md").read_text(encoding="utf-8")
            assert canonical in bridge_text
            assert "docs/AGENT_WORKFLOW.md" in bridge_text
            assert "sync_agent_skill_bridges.py" in bridge_text


def test_readmes_document_agent_skill_entrypoints() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_zh = (ROOT / "README_zh.md").read_text(encoding="utf-8")
    for text in (readme, readme_zh):
        assert ".codex/skills/" in text
        assert ".agents/skills/" in text
        assert ".claude/skills/" in text
        assert "$paper-to-html-talk" in text
        assert "/paper-to-html-talk" in text
        assert "sync_agent_skill_bridges.py --check" in text
