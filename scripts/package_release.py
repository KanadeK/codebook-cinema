"""Build release artifacts and verify they install in a clean temporary environment."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    subprocess.run([sys.executable, "-m", "build"], cwd=root, check=True)
    subprocess.run([sys.executable, "scripts/demo.py"], cwd=root, check=True)
    release = root / "dist-release"
    release.mkdir(exist_ok=True)
    for artifact in (root / "dist").glob("*"):
        shutil.copy2(artifact, release / artifact.name)
    for fixture in ("python_cli", "typescript_api"):
        shutil.copy2(
            root / "demo-output" / fixture / "storyboard.html",
            release / f"codebook-cinema-0.1.0-{fixture}-storyboard.html",
        )
    archive_base = release / "codebook-cinema-0.1.0-any"
    archive = Path(
        shutil.make_archive(str(archive_base), "zip", root_dir=root, base_dir="examples")
    )
    with tempfile.TemporaryDirectory() as temporary:
        environment = Path(temporary) / "venv"
        subprocess.run([sys.executable, "-m", "venv", str(environment)], check=True)
        python = environment / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        wheel = next(release.glob("*.whl"))
        subprocess.run(
            [str(python), "-m", "pip", "install", str(wheel)], check=True, stdout=subprocess.DEVNULL
        )
        subprocess.run(
            [
                str(python),
                "-m",
                "codebook_cinema.cli",
                "analyze",
                str(root / "examples" / "python_cli"),
                "-o",
                str(Path(temporary) / "output"),
            ],
            check=True,
        )
    artifacts = sorted(release.glob("*"))
    (release / "SHA256SUMS.txt").write_text(
        "".join(
            f"{sha256(path)}  {path.name}\n" for path in artifacts if path.name != "SHA256SUMS.txt"
        ),
        encoding="utf-8",
    )
    print(f"Packaged {len(artifacts)} artifacts in {release}; archive: {archive.name}")


if __name__ == "__main__":
    main()
