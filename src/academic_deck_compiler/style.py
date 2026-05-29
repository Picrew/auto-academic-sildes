from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    paper: str = "F0ECE3"
    ink: str = "1A2030"
    muted: str = "5A6270"
    hair: str = "CAC4B4"
    cobalt: str = "1C2644"
    copper: str = "C8A870"
    teal: str = "0E7C7B"
    graphite: str = "1C2644"
    soft_blue: str = "E6E0D4"
    soft_copper: str = "E6E0D4"
    serif: str = "Georgia"
    sans: str = "Helvetica Neue"
    mono: str = "Menlo"


THEME = Theme()
