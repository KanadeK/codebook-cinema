"""Pure, deterministic assembly of a repository report."""

from __future__ import annotations

from collections import defaultdict

import networkx as nx

from codebook_cinema.domain.models import Chapter, Module, Report, Shot


def _safe_id(path: str) -> str:
    return "m_" + "".join(character if character.isalnum() else "_" for character in path)


def _module_reference(module: Module) -> str:
    if module.symbols:
        symbol = module.symbols[0]
        return f"{module.path}:{symbol.line} ({symbol.kind} {symbol.name})"
    return f"{module.path}:1 (unknown)"


def build_report(root: str, modules: tuple[Module, ...]) -> Report:
    """Build chapters, a dependency graph and an editable shot list from source facts."""
    ordered = tuple(sorted(modules, key=lambda module: module.path))
    graph: nx.DiGraph[str] = nx.DiGraph()
    paths = {module.path for module in ordered}
    for module in ordered:
        graph.add_node(module.path)
        for imported in module.imports:
            candidate = imported.replace(".", "/")
            matches = [
                path for path in paths if path.removesuffix(".py").removesuffix(".ts") == candidate
            ]
            for match in matches:
                graph.add_edge(module.path, match)

    warnings: list[str] = []
    entries = [module for module in ordered if module.is_entrypoint]
    if not entries:
        warnings.append("No entry point was found; narration is limited to source structure.")
    groups: dict[str, list[Module]] = defaultdict(list)
    for module in ordered:
        groups[module.path.split("/", 1)[0]].append(module)
    chapters: list[Chapter] = []
    if entries:
        chapters.append(
            Chapter(
                "Entry points",
                tuple(module.path for module in entries),
                "Verified executable entry files.",
            )
        )
    for group, grouped in sorted(groups.items()):
        evidence = tuple(module.path for module in grouped)
        chapters.append(
            Chapter(f"Module group: {group}", evidence, "Purpose unknown; inspect linked symbols.")
        )

    mermaid_lines = ["flowchart LR"]
    for module in ordered:
        mermaid_lines.append(f'    {_safe_id(module.path)}["{module.path}"]')
    for source, target in sorted(graph.edges):
        mermaid_lines.append(f"    {_safe_id(source)} --> {_safe_id(target)}")
    shots: list[Shot] = []
    evidence_modules = entries + [module for module in ordered if module not in entries]
    for number, module in enumerate(evidence_modules, start=1):
        reference = _module_reference(module)
        subject = module.symbols[0].name if module.symbols else "unknown"
        shots.append(
            Shot(
                number,
                f"Inspect {module.path}",
                reference,
                f"Show {subject} using the linked source evidence.",
            )
        )
    return Report(
        root, ordered, tuple(chapters), tuple(shots), "\n".join(mermaid_lines), tuple(warnings)
    )
