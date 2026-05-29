from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image
import yaml

from .evidence_audit import IMAGE_SUFFIXES, classify_asset


DOC_SUFFIXES = {".pdf", ".md", ".txt", ".docx", ".pptx", ".tex", ".bib"}


def file_record(path: Path, root: Path) -> dict[str, Any]:
    rel = path.relative_to(root).as_posix() if path.is_relative_to(root) else path.name
    suffix = path.suffix.lower()
    record: dict[str, Any] = {"path": rel, "suffix": suffix}
    if suffix in IMAGE_SUFFIXES:
        role, recommendation = classify_asset(path)
        record["kind"] = "image"
        record["role"] = role
        record["recommendation"] = recommendation
        try:
            with Image.open(path) as im:
                record["width"], record["height"] = im.size
        except OSError:
            record["warning"] = "image could not be read"
    elif suffix in DOC_SUFFIXES:
        record["kind"] = "document"
    else:
        record["kind"] = "other"
    return record


def scan_source(source: Path) -> tuple[Path, list[Path]]:
    source = source.resolve()
    if source.is_file():
        return source.parent, [source]
    files = sorted(path for path in source.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES | DOC_SUFFIXES)
    return source, files


def write_source_manifest(source: Path, out_dir: Path) -> Path:
    root, files = scan_source(source)
    manifest = {
        "source_root": str(root),
        "files": [file_record(path, root) for path in files],
        "next_steps": [
            "Write a ghost deck with action titles before choosing layouts.",
            "Use result figures, system diagrams, and product workflow screenshots as primary evidence.",
            "Run academic-deck evidence after mapping assets into deck.yaml.",
        ],
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "source-manifest.yaml"
    path.write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path
