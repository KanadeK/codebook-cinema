"""Filesystem boundary for local source scans."""

from __future__ import annotations

from pathlib import Path

from codebook_cinema.adapters.source_parser import parse_module
from codebook_cinema.domain.models import Module

_IGNORED_DIRECTORIES = {".git", ".venv", "node_modules", "dist", "build", "__pycache__"}
_ELIGIBLE_SUFFIXES = {".py", ".ts", ".tsx"}


def scan_modules(root: Path) -> tuple[Module, ...]:
    """Read local Python/TypeScript files, failing clearly for malformed source."""
    if not root.exists():
        raise FileNotFoundError(f"Repository path does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {root}")
    files = [
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix in _ELIGIBLE_SUFFIXES
        and not any(part in _IGNORED_DIRECTORIES for part in path.parts)
    ]
    if not files:
        raise ValueError("No Python or TypeScript source files were found.")
    return tuple(parse_module(path, root) for path in sorted(files))
