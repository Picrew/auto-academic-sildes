from __future__ import annotations

from pathlib import Path
from PIL import Image


def image_whitespace_score(path: Path) -> float:
    im = Image.open(path).convert("RGB").resize((160, 90))
    bg = im.getpixel((2, 2))
    diff = 0
    for pixel in im.getdata():
        if sum(abs(pixel[i] - bg[i]) for i in range(3)) > 38:
            diff += 1
    density = diff / (160 * 90)
    if 0.18 <= density <= 0.48:
        return 1.0
    if density < 0.18:
        return max(0.0, density / 0.18)
    return max(0.0, 1 - (density - 0.48) / 0.35)


def edge_pressure(path: Path) -> float:
    """Estimate whether content is too close to slide edges."""
    im = Image.open(path).convert("RGB").resize((160, 90))
    bg = im.getpixel((2, 2))
    edge_pixels = []
    for y in range(90):
        for x in range(160):
            if x < 6 or x >= 154 or y < 5 or y >= 85:
                edge_pixels.append(im.getpixel((x, y)))
    active = 0
    for pixel in edge_pixels:
        if sum(abs(pixel[i] - bg[i]) for i in range(3)) > 38:
            active += 1
    return active / max(1, len(edge_pixels))


def judge_route(name: str, images: list[Path]) -> dict[str, float | str]:
    if not images:
        return {"route": name, "score": 0.0, "notes": "No preview images found."}
    whitespace = sum(image_whitespace_score(p) for p in images) / len(images)
    edge = sum(edge_pressure(p) for p in images) / len(images)
    rhythm = min(1.0, len(images) / 10)
    score = 10 * (0.48 * whitespace + 0.42 * rhythm + 0.10 * max(0.0, 1 - edge / 0.18))
    flags = [f"{i+1:02d}" for i, path in enumerate(images) if edge_pressure(path) > 0.18]
    notes = []
    notes.append("balanced visual density" if whitespace > 0.72 else "density or emptiness needs another pass")
    if flags:
        notes.append(f"edge pressure on slides {', '.join(flags)}")
    else:
        notes.append("low edge pressure")
    return {
        "route": name,
        "score": round(score, 1),
        "density_score": round(whitespace, 2),
        "edge_pressure": round(edge, 2),
        "notes": "; ".join(notes),
    }


def write_report(out_path: Path, reports: list[dict[str, float | str]]) -> Path:
    lines = ["# Visual Judge Report", ""]
    for report in reports:
        lines.append(f"## {report['route']}")
        lines.append(f"- Score: {report['score']} / 10")
        lines.append(f"- Density score: {report.get('density_score', 'n/a')}")
        lines.append(f"- Edge pressure: {report.get('edge_pressure', 'n/a')}")
        lines.append(f"- Notes: {report['notes']}")
        lines.append("")
    lines.append("## Route Decision")
    lines.append("- Default delivery route: PPTX-native for editable, high-design academic/tech decks.")
    lines.append("- Backup route: LaTeX/Beamer for formal PDF handouts and LaTeX-first audiences.")
    lines.append("- The automated score checks density and edge pressure only; manual visual review still overrides it when route taste, evidence readability, text clipping, or audience fit disagree.")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path
