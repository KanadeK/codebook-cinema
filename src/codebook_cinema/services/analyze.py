"""Use case for converting a local repository into an evidence report."""

from __future__ import annotations

from pathlib import Path

from codebook_cinema.adapters.filesystem import scan_modules
from codebook_cinema.domain.models import Report
from codebook_cinema.domain.story import build_report


def analyze_repository(root: Path) -> Report:
    resolved = root.resolve()
    return build_report(str(resolved), scan_modules(resolved))
