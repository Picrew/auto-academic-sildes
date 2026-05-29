from __future__ import annotations

from pathlib import Path
import shutil

from .assets import resolve_asset
from .ir import Deck


def used_images(deck: Deck) -> tuple[str, ...]:
    refs: list[str] = []
    for slide in deck.slides:
        image = slide.evidence.image if slide.evidence and slide.evidence.image else slide.image
        if image and image not in refs:
            refs.append(image)
    return tuple(refs)


def copy_if_exists(source: Path, target: Path) -> None:
    if source.exists() and source.is_file():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def copy_tree_if_exists(source: Path, target: Path) -> None:
    if source.exists() and source.is_dir():
        shutil.copytree(source, target, dirs_exist_ok=True)


def package_build(deck_path: Path, deck: Deck, output_dir: Path, package_dir: Path | None = None) -> Path:
    package_dir = package_dir or output_dir / "package"
    package_dir.mkdir(parents=True, exist_ok=True)

    copy_if_exists(deck_path, package_dir / "deck.yaml")
    for image in used_images(deck):
        source = resolve_asset(deck, image)
        if source.exists():
            copy_if_exists(source, package_dir / "assets" / image)

    for source in output_dir.glob("*.pptx"):
        copy_if_exists(source, package_dir / source.name)
    for name in (
        "judge-report.md",
        "quality-report.md",
        "evidence-report.md",
        "pptx-contact-sheet.png",
        "beamer-contact-sheet.png",
        "html-contact-sheet.png",
    ):
        copy_if_exists(output_dir / name, package_dir / name)
    for source in output_dir.glob("*-pptx-render.pdf"):
        copy_if_exists(source, package_dir / source.name)
    for source in (output_dir / "beamer").glob("*.pdf") if (output_dir / "beamer").exists() else ():
        copy_if_exists(source, package_dir / "beamer" / source.name)
    copy_tree_if_exists(output_dir / "html", package_dir / "html")
    copy_tree_if_exists(output_dir / "html-shots", package_dir / "html-shots")

    readme = [
        "# Academic Deck Review Package",
        "",
        f"- Deck: `{deck.deck_id}`",
        "- Design route: HTML-first for visual fidelity and evidence readability.",
        "- Delivery route: PPTX-native when editability is required.",
        "- Backup route: Beamer PDF for formal handout or LaTeX-first audiences.",
        "",
        "## Contents",
        "",
        "- `deck.yaml`: source IR",
        "- `assets/`: evidence and identity images referenced by the deck",
        "- `*.pptx`: editable PowerPoint output",
        "- `*-html-image.pptx`: browser-rendered HTML slides embedded as PPTX images",
        "- `*-pptx-render.pdf`: PowerPoint-rendered PDF when available",
        "- `beamer/*.pdf`: LaTeX/Beamer backup",
        "- `html/`: editorial HTML preview",
        "- `html-shots/`: browser screenshots used for HTML-image PPTX export",
        "- `*-contact-sheet.png`: visual review sheets",
        "- `judge-report.md`, `quality-report.md`, `evidence-report.md`: QA reports",
    ]
    (package_dir / "PACKAGE.md").write_text("\n".join(readme), encoding="utf-8")
    return package_dir
