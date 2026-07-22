from pathlib import Path

import pytest

from codebook_cinema.adapters.filesystem import scan_modules
from codebook_cinema.services.analyze import analyze_repository


def test_scanner_ignores_vendor_directories_and_discovers_two_languages(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("def start(): pass\n")
    (tmp_path / "widget.ts").write_text("export function show() {}\n")
    vendor = tmp_path / "node_modules"
    vendor.mkdir()
    (vendor / "ignored.ts").write_text("export function never() {}\n")
    assert [module.path for module in scan_modules(tmp_path)] == ["main.py", "widget.ts"]


def test_missing_source_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="No Python"):
        scan_modules(tmp_path)


def test_invalid_python_is_reported(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("def broken(:\n")
    with pytest.raises(SyntaxError):
        analyze_repository(tmp_path)
