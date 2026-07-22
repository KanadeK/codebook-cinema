"""Generate inspectable storyboards from both committed fixtures."""

from __future__ import annotations

from html import escape
from pathlib import Path

from codebook_cinema.domain.models import Report
from codebook_cinema.services.analyze import analyze_repository
from codebook_cinema.services.render import write_exports


def write_preview(report: Report, destination: Path) -> None:
    """Create the README preview directly from a generated report's first shots."""
    shots = report.shots[:3]
    rows = []
    for index, shot in enumerate(shots, start=0):
        y = 105 + index * 90
        rows.append(
            f'<rect x="45" y="{y}" width="810" height="70" rx="8" fill="#ffffff"/>'
            f'<text x="70" y="{y + 43}" font-family="monospace" font-size="21" fill="#0f4c81">'
            f"{escape(f'{shot.number}. {shot.title}   {shot.evidence}')}</text>"
        )
    destination.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="420" '
        'viewBox="0 0 900 420" role="img" '
        'aria-label="Generated Codebook Cinema storyboard preview">'
        '<rect width="900" height="420" fill="#f3f5f8"/>'
        '<text x="45" y="70" font-family="system-ui" font-size="36" fill="#172033">'
        "Codebook Cinema — generated storyboard</text>"
        + "".join(rows)
        + "</svg>\n",
        encoding="utf-8",
    )


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    output = root / "demo-output"
    preview_report = None
    for fixture in ("python_cli", "typescript_api"):
        report = analyze_repository(root / "examples" / fixture)
        if not any(module.is_entrypoint for module in report.modules):
            raise RuntimeError(f"Fixture {fixture} lost its entry point")
        if len(report.shots) < 5:
            raise RuntimeError(f"Fixture {fixture} has fewer than five shots")
        write_exports(report, output / fixture)
        if fixture == "python_cli":
            preview_report = report
    if preview_report is None:
        raise RuntimeError("Python fixture report was not generated")
    write_preview(preview_report, root / "docs" / "assets" / "storyboard-preview.svg")
    print(f"Generated storyboards in {output}")


if __name__ == "__main__":
    main()
