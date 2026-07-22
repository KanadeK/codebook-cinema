"""Run the same quality gates used by CI."""

from __future__ import annotations

import subprocess
import sys


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def main() -> None:
    run([sys.executable, "-m", "ruff", "check", "."])
    run([sys.executable, "-m", "mypy", "src"])
    run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-fail-under=80",
        ]
    )
    run([sys.executable, "-m", "build"])


if __name__ == "__main__":
    main()
