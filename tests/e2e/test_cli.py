from pathlib import Path

from typer.testing import CliRunner

from codebook_cinema.cli import app


def _fixture(root: Path) -> None:
    (root / "main.py").write_text(
        "from worker import run\ndef main(): return run()\nif __name__ == '__main__': main()\n"
    )
    (root / "worker.py").write_text("def run(): return 1\n")
    (root / "feature.py").write_text("class Feature: pass\n")
    (root / "helper.py").write_text("def help_me(): pass\n")
    (root / "model.py").write_text("class Model: pass\n")


def test_cli_creates_real_html_markdown_and_json(tmp_path: Path) -> None:
    _fixture(tmp_path)
    result = CliRunner().invoke(app, ["analyze", str(tmp_path), "--output", str(tmp_path / "out")])
    assert result.exit_code == 0, result.output
    assert "generated 5 shots" in result.output
    assert (tmp_path / "out" / "storyboard.html").exists()
    assert "main.py:2 (function main)" in (tmp_path / "out" / "report.md").read_text(
        encoding="utf-8"
    )


def test_cli_changes_report_and_warns_after_entry_is_deleted(tmp_path: Path) -> None:
    _fixture(tmp_path)
    first = CliRunner().invoke(app, ["analyze", str(tmp_path), "-o", str(tmp_path / "first")])
    (tmp_path / "main.py").unlink()
    second = CliRunner().invoke(app, ["analyze", str(tmp_path), "-o", str(tmp_path / "second")])
    assert first.exit_code == second.exit_code == 0
    assert "No entry point was found" in (tmp_path / "second" / "report.md").read_text(
        encoding="utf-8"
    )
    assert (tmp_path / "first" / "report.json").read_text(encoding="utf-8") != (
        tmp_path / "second" / "report.json"
    ).read_text(encoding="utf-8")


def test_cli_rejects_a_directory_without_supported_source(tmp_path: Path) -> None:
    result = CliRunner().invoke(app, ["analyze", str(tmp_path)])
    assert result.exit_code == 2
    assert "No Python or TypeScript" in result.output
