from pathlib import Path

import pytest

from codebook_cinema.adapters.source_parser import parse_module


def test_python_parser_extracts_imports_symbols_and_main_guard(tmp_path: Path) -> None:
    source = tmp_path / "main.py"
    source.write_text(
        "import package\nfrom core import run\nclass App: pass\n"
        "def launch(): pass\nif __name__ == '__main__': launch()\n"
    )
    module = parse_module(source, tmp_path)
    assert module.imports == ("package", "core")
    assert [(symbol.name, symbol.kind) for symbol in module.symbols] == [
        ("App", "class"),
        ("launch", "function"),
    ]
    assert module.is_entrypoint


def test_typescript_parser_extracts_real_symbols(tmp_path: Path) -> None:
    source = tmp_path / "index.ts"
    source.write_text(
        "import { run } from './run';\nexport interface Job {}\n"
        "export function start() { return run(); }\n"
    )
    module = parse_module(source, tmp_path)
    assert module.imports == ("./run",)
    assert [symbol.name for symbol in module.symbols] == ["Job", "start"]
    assert module.is_entrypoint


def test_unsupported_file_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "notes.txt"
    source.write_text("words")
    with pytest.raises(ValueError, match="Unsupported"):
        parse_module(source, tmp_path)
