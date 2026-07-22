"""Typer command-line delivery adapter."""

from __future__ import annotations

from pathlib import Path

import typer

from codebook_cinema.services.analyze import analyze_repository
from codebook_cinema.services.render import write_exports

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def analyze(
    repository: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),  # noqa: B008
    output: Path = typer.Option(Path("codebook-output"), "--output", "-o"),  # noqa: B008
) -> None:
    """Analyze a Python/TypeScript repository and write JSON, Markdown and HTML."""
    try:
        report = analyze_repository(repository)
        paths = write_exports(report, output)
    except (
        FileNotFoundError,
        NotADirectoryError,
        SyntaxError,
        UnicodeDecodeError,
        ValueError,
    ) as error:
        typer.echo(f"Analysis failed: {error}", err=True)
        raise typer.Exit(code=2) from error
    typer.echo(f"Scanned {len(report.modules)} modules; generated {len(report.shots)} shots.")
    for kind, path in paths.items():
        typer.echo(f"{kind}: {path}")


@app.command()
def version() -> None:
    """Print the installed Codebook Cinema version."""
    typer.echo("0.1.0")


if __name__ == "__main__":
    app()
