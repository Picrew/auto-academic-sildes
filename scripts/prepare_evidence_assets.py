from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "images"
DERIVED = SOURCE / "derived"


def crop(source: str, target: str, box: tuple[int, int, int, int], *, border: int = 0) -> None:
    DERIVED.mkdir(parents=True, exist_ok=True)
    im = Image.open(SOURCE / source).convert("RGB")
    cropped = im.crop(box)
    if border:
        cropped = ImageOps.expand(cropped, border=border, fill="white")
    cropped.save(DERIVED / target, quality=94)


def main() -> None:
    crop("constory_heatmaps.png", "constory_gap_panel.png", (1500, 0, 2352, 790), border=18)
    crop("constory_heatmaps.png", "constory_quote_gap_pair.png", (0, 0, 2352, 790), border=12)
    crop("qanything_two_stage.jpg", "qanything_chart_clean.jpg", (38, 30, 1320, 822), border=0)
    crop("seek_writer_screenshot.jpg", "seek_writer_editor_assistant.jpg", (520, 120, 3380, 1640), border=0)
    crop("seek_writer_screenshot.jpg", "seek_writer_state_panel.jpg", (0, 80, 515, 1510), border=0)


if __name__ == "__main__":
    main()
