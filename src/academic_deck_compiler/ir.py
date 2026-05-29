from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .content import (
    Callout,
    Crop,
    DECK_SUBTITLE,
    DECK_TITLE,
    Evidence,
    GENERIC_DECK_SUBTITLE,
    GENERIC_DECK_TITLE,
    GENERIC_SLIDES,
    SLIDES,
    Slide,
)


@dataclass(frozen=True)
class Deck:
    deck_id: str
    title: str
    subtitle: str
    slides: tuple[Slide, ...]
    visual_grammar: str = "editorial-profile"
    footer: str = ""
    contact: str = ""
    assets_dir: str = "assets/images"
    base_dir: str = ""


DEFAULT_DECK = Deck(
    deck_id="technical-research-talk",
    title=GENERIC_DECK_TITLE,
    subtitle=GENERIC_DECK_SUBTITLE,
    slides=GENERIC_SLIDES,
    visual_grammar="editorial-profile",
    footer="Academic Deck Compiler",
    contact="",
    base_dir=str(Path.cwd()),
)
PORTFOLIO_DECK = Deck(
    deck_id="research-portfolio",
    title=DECK_TITLE,
    subtitle=DECK_SUBTITLE,
    slides=SLIDES,
    visual_grammar="dark-lab-notebook",
    footer="Research Portfolio",
    contact="",
    base_dir=str(Path.cwd()),
)


def _tuple_pairs(value: Any) -> tuple[tuple[str, str], ...]:
    if not value:
        return ()
    pairs: list[tuple[str, str]] = []
    for item in value:
        if isinstance(item, dict):
            pairs.append((str(item.get("value", "")), str(item.get("label", ""))))
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            pairs.append((str(item[0]), str(item[1])))
    return tuple(pairs)


def _tuple_strings(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in (value or ()))


def _crop(value: Any) -> Crop | None:
    if not isinstance(value, dict):
        return None
    return Crop(
        x=float(value.get("x", 0)),
        y=float(value.get("y", 0)),
        w=float(value.get("w", 1)),
        h=float(value.get("h", 1)),
    )


def _callouts(value: Any) -> tuple[Callout, ...]:
    if not value:
        return ()
    callouts: list[Callout] = []
    for item in value:
        if isinstance(item, dict):
            callouts.append(
                Callout(
                    x=float(item.get("x", 0.5)),
                    y=float(item.get("y", 0.5)),
                    text=str(item.get("text", "")),
                )
            )
    return tuple(callouts)


def _evidence(data: dict[str, Any]) -> Evidence | None:
    raw = data.get("evidence")
    if isinstance(raw, dict):
        return Evidence(
            image=raw.get("image"),
            crop=_crop(raw.get("crop")),
            caption=str(raw.get("caption", "")),
            source=str(raw.get("source", "")),
            callouts=_callouts(raw.get("callouts")),
        )
    return None


def slide_from_mapping(data: dict[str, Any]) -> Slide:
    return Slide(
        kind=str(data["kind"]),
        kicker=str(data.get("kicker", "")),
        title=str(data["title"]),
        subtitle=str(data.get("subtitle", "")),
        layout=str(data.get("layout", "")),
        bullets=_tuple_strings(data.get("bullets")),
        metrics=_tuple_pairs(data.get("metrics")),
        labels=_tuple_strings(data.get("labels")),
        image=data.get("image"),
        evidence=_evidence(data),
        note=str(data.get("note", "")),
    )


def load_deck(path: str | Path | None = None) -> Deck:
    if path is None:
        return DEFAULT_DECK
    source = Path(path)
    data = yaml.safe_load(source.read_text(encoding="utf-8"))
    slides = tuple(slide_from_mapping(item) for item in data["slides"])
    return Deck(
        deck_id=str(data.get("deck_id", data.get("id", source.stem))),
        title=str(data.get("title", DECK_TITLE)),
        subtitle=str(data.get("subtitle", DECK_SUBTITLE)),
        slides=slides,
        visual_grammar=str(data.get("visual_grammar", "editorial-profile")),
        footer=str(data.get("footer", data.get("title", ""))),
        contact=str(data.get("contact", "")),
        assets_dir=str(data.get("assets_dir", "assets/images")),
        base_dir=str(source.parent.resolve()),
    )


def dump_deck(deck: Deck, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "deck_id": deck.deck_id,
        "title": deck.title,
        "subtitle": deck.subtitle,
        "visual_grammar": deck.visual_grammar,
        "footer": deck.footer,
        "contact": deck.contact,
        "assets_dir": deck.assets_dir,
        "slides": [
            {
                "kind": slide.kind,
                "kicker": slide.kicker,
                "title": slide.title,
                "subtitle": slide.subtitle,
                "layout": slide.layout,
                "bullets": list(slide.bullets),
                "metrics": [{"value": value, "label": label} for value, label in slide.metrics],
                "labels": list(slide.labels),
                "image": slide.image,
                "evidence": None
                if slide.evidence is None
                else {
                    "image": slide.evidence.image,
                    "crop": None
                    if slide.evidence.crop is None
                    else {
                        "x": slide.evidence.crop.x,
                        "y": slide.evidence.crop.y,
                        "w": slide.evidence.crop.w,
                        "h": slide.evidence.crop.h,
                    },
                    "caption": slide.evidence.caption,
                    "source": slide.evidence.source,
                    "callouts": [
                        {"x": callout.x, "y": callout.y, "text": callout.text}
                        for callout in slide.evidence.callouts
                    ],
                },
                "note": slide.note,
            }
            for slide in deck.slides
        ],
    }
    target.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return target


def dump_default_deck(path: str | Path) -> Path:
    return dump_deck(DEFAULT_DECK, path)


def dump_portfolio_deck(path: str | Path) -> Path:
    return dump_deck(PORTFOLIO_DECK, path)
