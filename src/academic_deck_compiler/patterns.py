from __future__ import annotations


def parse_matrix_rows(labels: tuple[str, ...], bullets: tuple[str, ...]) -> tuple[tuple[str, str, str], ...]:
    """Return (surface, failure controlled, artifact) rows for taxonomy/matrix slides."""
    parsed: list[tuple[str, str, str]] = []
    keyed: dict[str, tuple[str, str]] = {}
    ordered: list[tuple[str, str, str | None]] = []
    for bullet in bullets:
        label = None
        rest = bullet
        if ":" in bullet:
            head, rest = bullet.split(":", 1)
            label = head.strip()
        if " -> " in rest:
            failure, artifact = rest.split(" -> ", 1)
        elif " | " in rest:
            failure, artifact = rest.split(" | ", 1)
        else:
            failure, artifact = rest, "trace / check / gate"
        failure = failure.strip()
        artifact = artifact.strip()
        if label:
            keyed[label.lower()] = (failure, artifact)
        ordered.append((label or "", failure, artifact))

    fallback_failures = (
        "execute reliably",
        "bind tools safely",
        "carry working memory",
        "manage lifecycle state",
        "observe and debug",
        "verify before action",
        "govern boundaries",
    )
    fallback_artifact = "trace / check / gate"
    for i, label in enumerate(labels):
        if label.lower() in keyed:
            failure, artifact = keyed[label.lower()]
        elif i < len(ordered):
            failure, artifact = ordered[i][1], ordered[i][2] or fallback_artifact
        else:
            failure = fallback_failures[i] if i < len(fallback_failures) else "control reliability"
            artifact = fallback_artifact
        parsed.append((label, failure, artifact))
    return tuple(parsed)
