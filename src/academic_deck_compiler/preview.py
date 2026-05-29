from __future__ import annotations

from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont


def render_pdf_pages(pdf_path: Path, out_dir: Path, prefix: str) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["pdftoppm", "-png", "-r", "144", str(pdf_path), str(out_dir / prefix)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return sorted(out_dir.glob(f"{prefix}-*.png"))


def contact_sheet(images: list[Path], out_path: Path, cols: int = 4) -> Path:
    thumbs = []
    for p in images:
        im = Image.open(p).convert("RGB")
        im.thumbnail((420, 236))
        thumbs.append((p, im.copy()))
    if not thumbs:
        raise ValueError("No images for contact sheet")
    rows = (len(thumbs) + cols - 1) // cols
    cell_w, cell_h = 460, 290
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), "#f5f1e8")
    draw = ImageDraw.Draw(sheet)
    for i, (p, im) in enumerate(thumbs):
        x = (i % cols) * cell_w + 20
        y = (i // cols) * cell_h + 20
        sheet.paste(im, (x, y))
        draw.rectangle([x, y, x + im.width, y + im.height], outline="#d9d0c2")
        draw.text((x, y + im.height + 10), f"{i + 1:02d}  {p.name}", fill="#5d6773")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)
    return out_path

