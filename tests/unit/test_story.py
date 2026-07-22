from codebook_cinema.domain.models import Module, Symbol
from codebook_cinema.domain.story import build_report


def test_report_links_shots_to_real_symbols_and_builds_edges() -> None:
    modules = (
        Module("main.py", "python", ("worker",), (Symbol("start", "function", 4),), True),
        Module("worker.py", "python", (), (Symbol("run", "function", 2),), False),
    )
    report = build_report("/fixture", modules)
    assert "m_main_py --> m_worker_py" in report.mermaid
    assert report.shots[0].evidence == "main.py:4 (function start)"
    assert not report.warnings


def test_missing_entry_is_a_visible_warning_not_a_fabricated_entry() -> None:
    report = build_report("/fixture", (Module("lib.py", "python", (), (), False),))
    assert report.warnings == (
        "No entry point was found; narration is limited to source structure.",
    )
    assert report.shots[0].evidence.endswith("(unknown)")


def test_report_is_deterministic_when_input_order_changes() -> None:
    a = Module("z.py", "python", (), (), False)
    b = Module("a.py", "python", (), (), False)
    assert build_report("/x", (a, b)).as_dict() == build_report("/x", (b, a)).as_dict()
