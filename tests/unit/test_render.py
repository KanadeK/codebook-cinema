from pathlib import Path

from codebook_cinema.domain.models import Module, Report
from codebook_cinema.services.render import markdown, redact, write_exports


def test_redact_replaces_secret_like_assignment() -> None:
    assert redact("API_KEY='very-secret-value'") == "API_KEY=[REDACTED]"


def test_exports_create_all_human_and_machine_readable_files(tmp_path: Path) -> None:
    report = Report(
        "/fixture", (Module("main.py", "python", (), (), True),), (), (), "flowchart LR", ()
    )
    paths = write_exports(report, tmp_path / "out")
    assert set(paths) == {"json", "markdown", "html"}
    assert "flowchart LR" in paths["html"].read_text()
    assert markdown(report).startswith("# Codebook Cinema report")
