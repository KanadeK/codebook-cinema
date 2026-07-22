"""Deterministic report exports with secret-looking values redacted."""

from __future__ import annotations

import json
import re
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

from codebook_cinema.domain.models import Report

_SECRET_ASSIGNMENT = re.compile(
    r"(?i)(api[_-]?key|token|password|secret)\s*[:=]\s*(['\"]?)[^\s'\"]+\2"
)


def redact(text: str) -> str:
    return _SECRET_ASSIGNMENT.sub(lambda match: f"{match.group(1)}=[REDACTED]", text)


def markdown(report: Report) -> str:
    lines = [
        "# Codebook Cinema report",
        "",
        f"Scanned root: `{report.root}`",
        "",
        "## Architecture",
        "",
        "```mermaid",
        report.mermaid,
        "```",
        "",
        "## Chapters",
        "",
    ]
    for chapter in report.chapters:
        lines.extend(
            [
                f"### {chapter.title}",
                chapter.summary,
                "Evidence: " + ", ".join(f"`{item}`" for item in chapter.evidence),
                "",
            ]
        )
    lines.extend(["## Shot list", ""])
    for shot in report.shots:
        lines.extend(
            [
                f"{shot.number}. **{shot.title}** — `{shot.evidence}`",
                f"   Narration: {shot.narration}",
            ]
        )
    if report.warnings:
        lines.extend(["", "## Warnings", ""] + [f"- {warning}" for warning in report.warnings])
    return redact("\n".join(lines) + "\n")


def html(report: Report) -> str:
    environment = Environment(
        loader=PackageLoader("codebook_cinema", "templates"), autoescape=select_autoescape(["html"])
    )
    return environment.get_template("storyboard.html.j2").render(
        report=report, markdown=markdown(report)
    )


def write_exports(report: Report, output: Path) -> dict[str, Path]:
    output.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": output / "report.json",
        "markdown": output / "report.md",
        "html": output / "storyboard.html",
    }
    paths["json"].write_text(json.dumps(report.as_dict(), indent=2) + "\n", encoding="utf-8")
    paths["markdown"].write_text(markdown(report), encoding="utf-8")
    paths["html"].write_text(html(report), encoding="utf-8")
    return paths
