"""Evidence-first models used by every delivery adapter."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import PurePosixPath


@dataclass(frozen=True)
class Symbol:
    name: str
    kind: str
    line: int


@dataclass(frozen=True)
class Module:
    path: str
    language: str
    imports: tuple[str, ...]
    symbols: tuple[Symbol, ...]
    is_entrypoint: bool

    @property
    def label(self) -> str:
        return PurePosixPath(self.path).stem


@dataclass(frozen=True)
class Chapter:
    title: str
    evidence: tuple[str, ...]
    summary: str


@dataclass(frozen=True)
class Shot:
    number: int
    title: str
    evidence: str
    narration: str


@dataclass(frozen=True)
class Report:
    root: str
    modules: tuple[Module, ...]
    chapters: tuple[Chapter, ...]
    shots: tuple[Shot, ...]
    mermaid: str
    warnings: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)
