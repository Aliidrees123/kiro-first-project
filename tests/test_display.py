"""Tests for task_manager.display."""

from hypothesis import given
from hypothesis import strategies as st

from task_manager.display import MENU, format_task, format_task_list
from task_manager.models import Task

# ---------------------------------------------------------------------------
# Helpers / strategies
# ---------------------------------------------------------------------------

tasks_strategy = st.builds(
    Task,
    title=st.text(min_size=1),
    done=st.booleans(),
)


# ---------------------------------------------------------------------------
# Property 4: Task list rendering is complete
# Validates: Requirements 4.1, 4.2, 4.3
# ---------------------------------------------------------------------------


@given(tasks=st.lists(tasks_strategy, min_size=1))
def test_format_task_list_rendering_completeness(tasks: list[Task]) -> None:
    """For any non-empty list of tasks, format_task_list output contains every
    task's title, its 1-based index, and a status marker ([ ] or [x]).
    """
    output = format_task_list(tasks)

    for i, task in enumerate(tasks, start=1):
        assert task.title in output, (
            f"Title {task.title!r} not found in output for task at index {i}"
        )
        assert str(i) in output, f"1-based index {i} not found in output"
        expected_marker = "[x]" if task.done else "[ ]"
        assert expected_marker in output, (
            f"Status marker {expected_marker!r} not found in output"
            f" for task at index {i}"
        )


# ---------------------------------------------------------------------------
# Property 8: No ANSI escape codes in output
# Validates: Requirements 8.2
# ---------------------------------------------------------------------------


@given(index=st.integers(min_value=1, max_value=1000), task=tasks_strategy)
def test_format_task_no_ansi(index: int, task: Task) -> None:
    """format_task output never contains ANSI escape sequences."""
    result = format_task(index, task)
    assert "\x1b[" not in result


@given(tasks=st.lists(tasks_strategy, min_size=0, max_size=20))
def test_format_task_list_no_ansi(tasks: list[Task]) -> None:
    """format_task_list output never contains ANSI escape sequences."""
    result = format_task_list(tasks)
    assert "\x1b[" not in result


# ---------------------------------------------------------------------------
# Unit tests for display functions
# Requirements: 4.3, 4.4, 9.4
# ---------------------------------------------------------------------------


def test_format_task_not_done() -> None:
    """format_task returns '1. [ ] <title>' for a not-done task."""
    task = Task(title="Buy milk", done=False)
    assert format_task(1, task) == "1. [ ] Buy milk"


def test_format_task_done() -> None:
    """format_task returns '2. [x] <title>' for a done task."""
    task = Task(title="Write tests", done=True)
    assert format_task(2, task) == "2. [x] Write tests"


def test_format_task_list_empty() -> None:
    """format_task_list returns a 'no tasks' message for an empty list."""
    result = format_task_list([])
    assert "no tasks" in result.lower()


def test_menu_contains_all_options() -> None:
    """MENU contains all five option strings (1) through (5)."""
    for option in ("(1)", "(2)", "(3)", "(4)", "(5)"):
        assert option in MENU
