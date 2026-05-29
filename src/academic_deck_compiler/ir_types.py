from __future__ import annotations

from typing import Protocol


class DeckLike(Protocol):
    assets_dir: str
    base_dir: str
