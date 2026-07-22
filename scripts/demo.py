"""Generate inspectable storyboards from both committed fixtures."""

from __future__ import annotations

from pathlib import Path

from codebook_cinema.services.analyze import analyze_repository
from codebook_cinema.services.render import write_exports


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    output = root / "demo-output"
    for fixture in ("python_cli", "typescript_api"):
        report = analyze_repository(root / "examples" / fixture)
        if not any(module.is_entrypoint for module in report.modules):
            raise RuntimeError(f"Fixture {fixture} lost its entry point")
        if len(report.shots) < 5:
            raise RuntimeError(f"Fixture {fixture} has fewer than five shots")
        write_exports(report, output / fixture)
    print(f"Generated storyboards in {output}")


if __name__ == "__main__":
    main()
