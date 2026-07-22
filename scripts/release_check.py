"""Refuse a release unless source, identity, artifacts and quality gates are valid."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


def checked(command: list[str], root: Path) -> str:
    return subprocess.run(command, cwd=root, check=True, text=True, capture_output=True).stdout


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    status = checked(["git", "status", "--short"], root)
    if status:
        raise RuntimeError("Release check requires a clean working tree")
    version = re.search(
        r'^version = "([^"]+)"', (root / "pyproject.toml").read_text(), re.MULTILINE
    )
    if version is None or f"## v{version.group(1)}" not in (root / "CHANGELOG.md").read_text():
        raise RuntimeError("Version and CHANGELOG are inconsistent")
    if (
        not list((root / "dist-release").glob("*.whl"))
        or not (root / "dist-release" / "SHA256SUMS.txt").exists()
    ):
        raise RuntimeError("Release artifacts or checksums are missing")
    marker_names = [
        "TO" + "DO",
        "FIX" + "ME",
        "Not" + "Implemented",
        "place" + "holder",
        "coming " + "soon",
        "lorem " + "ipsum",
    ]
    banned = re.compile("|".join(marker_names), re.IGNORECASE)
    for path in root.rglob("*"):
        if (
            path.is_file()
            and ".git" not in path.parts
            and path.suffix in {".py", ".md", ".yml", ".toml"}
        ):
            if banned.search(path.read_text(encoding="utf-8", errors="ignore")):
                raise RuntimeError(f"Release-blocking marker in {path.relative_to(root)}")
    authors = checked(["git", "log", "--format=%an <%ae>"], root).splitlines()
    if set(authors) != {"KanadeK <121669563+KanadeK@users.noreply.github.com>"}:
        raise RuntimeError(f"Unexpected commit author: {authors}")
    subprocess.run([sys.executable, "scripts/verify.py"], cwd=root, check=True)
    print("Release check passed")


if __name__ == "__main__":
    main()
