from __future__ import annotations

from dataclasses import dataclass


KNOWN_LAYOUT_INTENTS = {
    "cover-source-rail",
    "cover-title-wall",
    "cover-poster-grid",
    "cover-title-card",
    "proof-showcase",
    "proof-atlas-spread",
    "proof-stage",
    "proof-dossier",
    "proof-ledger",
    "proof-marginalia",
    "proof-gallery-split",
    "proof-led",
    "matrix-ledger",
    "matrix-map",
    "spine-map",
    "artifact-showcase",
    "artifact-dossier",
    "artifact-rail",
    "artifact-marginalia",
    "artifact-ledger",
    "metrics-led",
    "metrics-ledger",
    "content-label-board",
    "content-bento",
    "content-marginalia",
    "content-field-manual",
    "content-workbench-index",
    "text-two-col",
}


LAYOUT_ALIASES = {
    "image-dominant": "proof-showcase",
    "image-first": "proof-showcase",
    "proof-dominant": "proof-showcase",
    "proof-first": "proof-showcase",
    "full-proof": "proof-showcase",
    "source-dominant": "artifact-showcase",
    "artifact-dominant": "artifact-showcase",
    "artifact-first": "artifact-showcase",
    "source-first": "artifact-showcase",
    "compact": "text-two-col",
    "text": "text-two-col",
}


def normalize_layout_intent(value: str | None) -> str:
    layout = (value or "").strip().lower().replace("_", "-")
    if not layout:
        return ""
    layout = LAYOUT_ALIASES.get(layout, layout)
    return layout if layout in KNOWN_LAYOUT_INTENTS else ""


@dataclass(frozen=True)
class Crop:
    x: float
    y: float
    w: float
    h: float


@dataclass(frozen=True)
class Callout:
    x: float
    y: float
    text: str


@dataclass(frozen=True)
class Evidence:
    image: str | None = None
    crop: Crop | None = None
    caption: str = ""
    source: str = ""
    callouts: tuple[Callout, ...] = ()


@dataclass(frozen=True)
class Slide:
    kind: str
    kicker: str
    title: str
    subtitle: str = ""
    layout: str = ""
    bullets: tuple[str, ...] = ()
    metrics: tuple[tuple[str, str], ...] = ()
    labels: tuple[str, ...] = ()
    image: str | None = None
    evidence: Evidence | None = None
    note: str = ""


GENERIC_DECK_TITLE = "Technical Research Talk"
GENERIC_DECK_SUBTITLE = "A claim-led deck that turns evidence into a memorable argument"


GENERIC_SLIDES: tuple[Slide, ...] = (
    Slide(
        kind="cover",
        kicker="Research talk",
        title="A strong technical deck is an argument, not a document",
        subtitle="Use this starter for paper talks, systems reviews, portfolio decks, and thesis-style presentations.",
        labels=("Narrative", "Evidence", "Design", "Delivery"),
        metrics=(("1", "central claim"), ("3-5", "evidence anchors"), ("2", "render routes")),
    ),
    Slide(
        kind="thesis",
        kicker="Positioning",
        title="Make the audience remember the judgment, not the page count",
        subtitle="Every slide should answer one question: what should the room believe after seeing this evidence?",
        bullets=(
            "Replace topic titles with action titles that state the takeaway.",
            "Keep details in notes or appendix unless they change the argument.",
            "Choose images because they prove something, not because they decorate.",
            "Render both editable PPTX and disciplined Beamer, then pick the route that serves the room.",
        ),
    ),
    Slide(
        kind="map",
        kicker="Narrative spine",
        title="Build the talk as a reliability loop",
        subtitle="This default loop is generic; replace each case with your paper, system, or project evidence.",
        labels=("Question", "Failure", "Signal", "Intervention", "Result"),
        bullets=(
            "Question: what uncertainty or pain point starts the talk?",
            "Failure: what breaks in the baseline or existing practice?",
            "Signal: what measurement, artifact, or user trace makes it visible?",
            "Intervention: what design change moves the system?",
        ),
    ),
    Slide(
        kind="evidence",
        kicker="Evidence page",
        title="One strong proof beats five related screenshots",
        subtitle="Use a cropped figure, table, trace, or UI region as the visual center of the page.",
        bullets=(
            "State the claim in the headline.",
            "Crop until labels are readable at presentation distance.",
            "Add two callouts at most: one for the metric, one for the interpretation.",
        ),
        metrics=(("claim", "headline"), ("source", "caption"), ("next", "implication")),
    ),
    Slide(
        kind="close",
        kicker="Close",
        title="End with a conclusion, not a thank-you slide",
        subtitle="The closing slide should summarize the contribution and leave useful hooks for discussion.",
        labels=("What changed", "Why it matters", "Where to go next", "Questions"),
        bullets=(
            "Restate the central claim in different words.",
            "Name the evidence that made the claim credible.",
            "Offer concrete directions for Q&A or collaboration.",
        ),
        note="Replace with contact, repo, paper, or project links.",
    ),
)


DECK_TITLE = "Research Portfolio"
DECK_SUBTITLE = "A reusable profile deck for technical research and systems work"


SLIDES: tuple[Slide, ...] = (
    Slide(
        kind="cover",
        kicker="Research portfolio",
        title="Reliable systems are designed around observable failure",
        subtitle="A neutral fixture for researchers, engineers, and technical builders who need a claim-led profile deck.",
        labels=("Evaluation", "Systems", "Evidence", "Delivery"),
        metrics=(("1", "research spine"), ("3", "proof surfaces"), ("2", "export routes")),
    ),
    Slide(
        kind="thesis",
        kicker="Positioning",
        title="The strongest profile reads as a research argument",
        subtitle="Replace biography-first chronology with a loop: define the failure, expose the signal, show the intervention, and prove the result.",
        bullets=(
            "Evaluation makes the failure measurable enough to guide iteration.",
            "Systems work keeps data, rollout, serving, and monitoring honest.",
            "Product judgment exposes the places where metrics miss user-facing failure.",
            "The deck should make the room understand why the work compounds.",
        ),
    ),
    Slide(
        kind="map",
        kicker="Narrative spine",
        title="A profile deck should show a loop, not a list",
        subtitle="Each project contributes one control surface for the same larger problem.",
        labels=("Diagnose", "Collect", "Train", "Verify", "Ship"),
        bullets=(
            "Diagnose the failure mode in the setting where it matters.",
            "Collect evidence that makes the failure inspectable.",
            "Train or redesign the system at the point of leverage.",
            "Verify with a gate that survives contact with real use.",
        ),
    ),
    Slide(
        kind="split",
        kicker="Research project",
        title="A project slide should name the leverage point",
        subtitle="Use this slot for the work that best explains your technical taste.",
        bullets=(
            "Start with the baseline failure rather than the implementation tour.",
            "Name the signal that made the failure visible.",
            "Explain the intervention as a design decision, not a bag of tricks.",
        ),
        metrics=(("failure", "what broke"), ("signal", "what changed"), ("gate", "what passed")),
    ),
    Slide(
        kind="process",
        kicker="Method",
        title="Compress the method into three design decisions",
        subtitle="A good technical slide lets the audience reconstruct the system without reading the code.",
        labels=("Represent", "Intervene", "Verify"),
        bullets=(
            "Represent the problem with the smallest signal that still matters.",
            "Intervene where behavior can change without hiding the failure.",
            "Verify on the setting where shortcuts usually survive.",
        ),
    ),
    Slide(
        kind="evidence",
        kicker="Evidence",
        title="The strongest artifact should carry the claim",
        subtitle="Add a cropped figure, trace, project page, or table that proves the action title.",
        bullets=(
            "Use a local crop with readable source pixels.",
            "Keep the caption specific enough to explain what is being inspected.",
            "Add one or two callouts only when they help the audience read the proof.",
        ),
        metrics=(("crop", "proof surface"), ("caption", "source contract"), ("claim", "headline")),
        labels=("Figure", "Trace", "Table"),
        note="Replace this placeholder with an evidence.image block before strict export.",
    ),
    Slide(
        kind="matrix",
        kicker="Systems view",
        title="System reliability is usually created around the model",
        subtitle="Use a matrix when the work spans data, model, serving, evaluation, and product surfaces.",
        bullets=(
            "Data: inputs become expensive before they become visible.",
            "Model: shortcuts often look like progress until the gate changes.",
            "Serving: latency, memory, and observability shape the method.",
            "Evaluation: good tests become the project memory.",
        ),
        labels=("Data", "Model", "Serving", "Evaluation", "Product"),
        metrics=(("5", "surfaces"), ("1", "decision"), ("trace", "evidence")),
    ),
    Slide(
        kind="system",
        kicker="Engineering detail",
        title="The engineering slide should reveal the real bottleneck",
        subtitle="Show the non-obvious constraint: dirty data, throughput, interface drift, evaluation debt, or deployment pressure.",
        bullets=(
            "Separate the research idea from the infrastructure required to make it true.",
            "Name the tradeoff that constrained the implementation.",
            "Tie performance numbers to a reproducible setting.",
        ),
        metrics=(("data", "first bottleneck"), ("scale", "second bottleneck"), ("gate", "release condition")),
    ),
    Slide(
        kind="loop",
        kicker="Operating loop",
        title="Quality improves when failures become training data",
        subtitle="This slide is for bad-case mining, regression tests, monitoring, or evaluation-driven iteration.",
        bullets=(
            "Mine failures from real traces or carefully designed probes.",
            "Assign ownership to the system surface that created the miss.",
            "Promote fixed cases into regression gates.",
        ),
        labels=("QAnything", "baseline"),
        note="probe -> mine -> train -> gate",
    ),
    Slide(
        kind="product",
        kicker="Builder track",
        title="Product work keeps the research question grounded",
        subtitle="Use this slide when a tool, demo, or workflow made the technical problem sharper.",
        bullets=(
            "Show the workflow, not a generic product screenshot.",
            "Explain what the interface taught you about the model or system.",
            "Connect user-facing failure back to the research loop.",
        ),
    ),
    Slide(
        kind="stack",
        kicker="What the deck should leave behind",
        title="The audience should remember the shape of your judgment",
        subtitle="The final profile slide names the working style, not only the project names.",
        labels=("Problem framing", "Evidence design", "Systems execution", "Product judgment"),
        bullets=(
            "Define failure modes before optimizing them.",
            "Build signals that resist shortcut learning.",
            "Treat throughput, observability, and regression gates as part of the method.",
        ),
    ),
    Slide(
        kind="close",
        kicker="Discussion hooks",
        title="End with concrete hooks, not a thank-you slide",
        subtitle="Close on the claims, artifacts, and collaboration questions the audience can actually discuss.",
        labels=("Evidence", "Systems", "Product", "Next"),
        bullets=(
            "Which failure mode is worth measuring next?",
            "Which proof surface should be made more inspectable?",
            "Which system gate would change the decision?",
        ),
        note="Replace with contact, repo, paper, or project links.",
    ),
)
