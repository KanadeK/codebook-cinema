"""Language adapters that expose only source facts, never inferred behavior."""

from __future__ import annotations

import ast
import re
from pathlib import Path

from codebook_cinema.domain.models import Module, Symbol

_TS_IMPORT = re.compile(r"^\s*import(?:[\s\S]*?from\s+)?[\"']([^\"']+)[\"']", re.MULTILINE)
_TS_REQUIRE = re.compile(r"\brequire\(\s*[\"']([^\"']+)[\"']\s*\)")
_TS_SYMBOL = re.compile(
    r"^\s*(?:export\s+)?(?:async\s+)?(function|class|interface|type)\s+([A-Za-z_$][\w$]*)",
    re.MULTILINE,
)


def _python_module(path: Path, text: str, relative: str) -> Module:
    tree = ast.parse(text, filename=str(path))
    imports: list[str] = []
    symbols: list[Symbol] = []
    has_main_guard = False
    for node in tree.body:
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append((node.module or "").lstrip("."))
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            symbols.append(Symbol(node.name, "function", node.lineno))
        elif isinstance(node, ast.ClassDef):
            symbols.append(Symbol(node.name, "class", node.lineno))
        elif isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
            has_main_guard = any(
                isinstance(value, ast.Constant) and value.value == "__main__"
                for value in node.test.comparators
            )
    name_entry = path.name in {"main.py", "cli.py", "app.py", "__main__.py"}
    return Module(relative, "python", tuple(imports), tuple(symbols), name_entry or has_main_guard)


def _parse_typescript_tree(text: str) -> bool:
    """Run tree-sitter for TypeScript syntax validation when its grammar is available."""
    try:
        from tree_sitter import Language, Parser
        from tree_sitter_typescript import language_typescript

        language = Language(language_typescript())
        tree = Parser(language).parse(text.encode("utf-8"))
        return not tree.root_node.has_error
    except (ImportError, TypeError, ValueError):
        return True


def _typescript_module(path: Path, text: str, relative: str) -> Module:
    _parse_typescript_tree(text)
    imports = _TS_IMPORT.findall(text) + _TS_REQUIRE.findall(text)
    symbols = tuple(
        Symbol(match.group(2), match.group(1), text[: match.start()].count("\n") + 1)
        for match in _TS_SYMBOL.finditer(text)
    )
    name_entry = path.name in {"index.ts", "main.ts", "app.ts", "cli.ts"}
    is_entrypoint = name_entry or "process.argv" in text or "listen(" in text
    return Module(relative, "typescript", tuple(imports), symbols, is_entrypoint)


def parse_module(path: Path, root: Path) -> Module:
    """Parse an eligible source file into verifiable imports and top-level symbols."""
    text = path.read_text(encoding="utf-8")
    relative = path.relative_to(root).as_posix()
    if path.suffix == ".py":
        return _python_module(path, text, relative)
    if path.suffix in {".ts", ".tsx"}:
        return _typescript_module(path, text, relative)
    raise ValueError(f"Unsupported source language: {path}")
