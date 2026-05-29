from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps

from .content import Crop
from .ir_types import DeckLike
from .paths import ROOT


def resolve_assets_dir(deck: DeckLike) -> Path:
    raw = Path(deck.assets_dir).expanduser()
    if raw.is_absolute():
        return raw
    if deck.base_dir:
        candidate = Path(deck.base_dir) / raw
        if candidate.exists():
            return candidate
    return ROOT / raw


def resolve_asset(deck: DeckLike, image_name: str) -> Path:
    path = Path(image_name).expanduser()
    if path.is_absolute():
        return path
    return resolve_assets_dir(deck) / path


def crop_asset(source: Path, crop: Crop | None, cache_dir: Path, key: str) -> Path:
    if crop is None:
        return source
    cache_dir.mkdir(parents=True, exist_ok=True)
    target = cache_dir / f"{key}.png"
    if target.exists() and target.stat().st_mtime >= source.stat().st_mtime:
        return target
    with Image.open(source) as raw:
        im = raw.convert("RGB")
        width, height = im.size
        left = max(0, min(width, round(crop.x * width)))
        top = max(0, min(height, round(crop.y * height)))
        right = max(left + 1, min(width, round((crop.x + crop.w) * width)))
        bottom = max(top + 1, min(height, round((crop.y + crop.h) * height)))
        cropped = im.crop((left, top, right, bottom))
        cropped = ImageOps.expand(cropped, border=10, fill="white")
        cropped.save(target)
    return target
