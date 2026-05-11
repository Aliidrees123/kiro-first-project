"""Tests for task_manager.cli."""

import builtins
import json
import os
import tempfile

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from task_manager.cli import run_app
from task_manager.models import Task
from task_manager.storage import save_tasks

# ---------------------------------------------------------------------------
# Hypothesis strategies
# ---------------------------------------------------------------------------

task_strategy = st.builds(
    Task,
    title=st.text(min_size=1).filter(lambda s: s.strip()),
    done=st.booleans(),
)

tasks_list_strategy = st.lists(task_strategy, max_size=5)

invalid_choice_strategy = st.text().filter(
    lambda s: s.strip() not in {"1", "2", "3", "4", "5"}
)


# ---------------------------------------------------------------------------
# Property 9: Invalid menu input leaves task list unchanged
# Validates: Requirements 2.4
# ---------------------------------------------------------------------------


@given(invalid_choice=invalid_choice_strategy, initial_tasks=tasks_list_strategy)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_invalid_menu_input_leaves_task_list_unchanged(
    monkeypatch, capsys, invalid_choice, initial_tasks
):
    """Property 9: any string not in {"1","2","3","4","5"} causes an error
    message and leaves the task list unchanged.

    **Validates: Requirements 2.4**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tasks_file = os.path.join(tmp_dir, "tasks.json")

        # Write the initial task list to the temp file (or leave absent if empty)
        if initial_tasks:
            save_tasks(initial_tasks, tasks_file)

        # Capture the expected file state before running the app
        if os.path.exists(tasks_file):
            with open(tasks_file, encoding="utf-8") as fh:
                content_before = json.load(fh)
        else:
            content_before = []

        # Feed: invalid choice → then "5" to exit
        inputs = iter([invalid_choice, "5"])
        monkeypatch.setattr(builtins, "input", lambda _prompt="": next(inputs))

        run_app(tasks_file)

        # Assert: error message was printed to stdout
        captured = capsys.readouterr()
        assert "invalid" in captured.out.lower() or "error" in captured.out.lower(), (
            f"Expected an error message for invalid choice {invalid_choice!r}, "
            f"but got: {captured.out!r}"
        )

        # Assert: task list file is unchanged
        if os.path.exists(tasks_file):
            with open(tasks_file, encoding="utf-8") as fh:
                content_after = json.load(fh)
        else:
            content_after = []

        assert content_before == content_after, (
            f"Task list changed after invalid menu input {invalid_choice!r}. "
            f"Before: {content_before}, After: {content_after}"
        )


# ---------------------------------------------------------------------------
# 7.4 Unit tests for CLI menu loop
# ---------------------------------------------------------------------------


def test_run_app_quit(monkeypatch, tmp_path):
    """Option '5' exits the loop without error."""
    tasks_file = tmp_path / "tasks.json"
    inputs = iter(["5"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(inputs))
    run_app(str(tasks_file))  # should return normally, not raise


def test_handle_add_valid_title(monkeypatch, tmp_path, capsys):
    """Adding a task with a valid title appends it and prints confirmation."""
    from task_manager.cli import handle_add

    tasks_file = tmp_path / "tasks.json"
    monkeypatch.setattr("builtins.input", lambda _prompt="": "Buy milk")
    result = handle_add([], str(tasks_file))
    assert len(result) == 1
    assert result[0].title == "Buy milk"
    out = capsys.readouterr().out
    assert "Buy milk" in out


def test_handle_add_blank_title(monkeypatch, tmp_path, capsys):
    """Adding a task with a blank title leaves the list empty and prints an error."""
    from task_manager.cli import handle_add

    tasks_file = tmp_path / "tasks.json"
    monkeypatch.setattr("builtins.input", lambda _prompt="": "")
    result = handle_add([], str(tasks_file))
    assert result == []
    out = capsys.readouterr().out
    assert "error" in out.lower()


def test_handle_complete_valid(monkeypatch, tmp_path, capsys):
    """Completing a valid task marks it done and prints confirmation with title."""
    from task_manager.cli import handle_complete

    tasks_file = tmp_path / "tasks.json"
    tasks = [Task(title="Write tests")]
    monkeypatch.setattr("builtins.input", lambda _prompt="": "1")
    result = handle_complete(tasks, str(tasks_file))
    assert result[0].done is True
    out = capsys.readouterr().out
    assert "Write tests" in out


def test_handle_complete_out_of_range(monkeypatch, tmp_path, capsys):
    """Out-of-range index leaves the list unchanged and prints an error."""
    from task_manager.cli import handle_complete

    tasks_file = tmp_path / "tasks.json"
    tasks = [Task(title="Write tests")]
    monkeypatch.setattr("builtins.input", lambda _prompt="": "99")
    result = handle_complete(tasks, str(tasks_file))
    assert result == tasks
    out = capsys.readouterr().out
    assert "error" in out.lower()


def test_handle_complete_already_done(monkeypatch, tmp_path, capsys):
    """Completing an already-done task leaves the list unchanged and prints error."""
    from task_manager.cli import handle_complete

    tasks_file = tmp_path / "tasks.json"
    tasks = [Task(title="Write tests", done=True)]
    monkeypatch.setattr("builtins.input", lambda _prompt="": "1")
    result = handle_complete(tasks, str(tasks_file))
    assert result == tasks
    out = capsys.readouterr().out
    assert "error" in out.lower()


def test_handle_delete_valid(monkeypatch, tmp_path, capsys):
    """Deleting a valid task removes it and prints confirmation with title."""
    from task_manager.cli import handle_delete

    tasks_file = tmp_path / "tasks.json"
    tasks = [Task(title="Buy milk")]
    monkeypatch.setattr("builtins.input", lambda _prompt="": "1")
    result = handle_delete(tasks, str(tasks_file))
    assert result == []
    out = capsys.readouterr().out
    assert "Buy milk" in out


def test_handle_delete_out_of_range(monkeypatch, tmp_path, capsys):
    """Out-of-range index leaves the list unchanged and prints an error."""
    from task_manager.cli import handle_delete

    tasks_file = tmp_path / "tasks.json"
    tasks = [Task(title="Buy milk")]
    monkeypatch.setattr("builtins.input", lambda _prompt="": "99")
    result = handle_delete(tasks, str(tasks_file))
    assert result == tasks
    out = capsys.readouterr().out
    assert "error" in out.lower()


def test_handle_list_empty(capsys):
    """Listing with no tasks prints a 'no tasks' message (case-insensitive)."""
    from task_manager.cli import handle_list

    handle_list([])
    out = capsys.readouterr().out
    assert "no tasks" in out.lower()


def test_handle_list_non_empty(capsys):
    """Listing with tasks prints each task's title."""
    from task_manager.cli import handle_list

    tasks = [Task(title="Alpha"), Task(title="Beta")]
    handle_list(tasks)
    out = capsys.readouterr().out
    assert "Alpha" in out
    assert "Beta" in out


# ---------------------------------------------------------------------------
# Property 7: Operation confirmations contain the task title
# Validates: Requirements 3.4, 5.3, 6.3
# ---------------------------------------------------------------------------

# Strategy for non-empty, non-whitespace titles
_titles = st.text(min_size=1).filter(lambda s: s.strip() != "")


@given(title=_titles)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_add_confirmation_contains_title(title, monkeypatch, capsys, tmp_path):
    """For any non-empty, non-whitespace title, stdout after handle_add
    contains the title.

    handle_add strips the raw input before storing/printing, so we assert
    against the stripped title (which is the actual task title).

    **Validates: Requirements 3.4**
    """
    from task_manager.cli import handle_add

    tasks_path = str(tmp_path / "tasks.json")
    monkeypatch.setattr("builtins.input", lambda _: title)

    handle_add([], tasks_path)

    captured = capsys.readouterr()
    # CLI strips input; confirmation uses the stripped title
    assert title.strip() in captured.out


@given(title=_titles)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_complete_confirmation_contains_title(title, monkeypatch, capsys, tmp_path):
    """For any non-empty, non-whitespace title, stdout after handle_complete
    contains the title.

    **Validates: Requirements 5.3**
    """
    from task_manager.cli import handle_complete

    tasks_path = str(tmp_path / "tasks.json")
    task = Task(title=title)
    monkeypatch.setattr("builtins.input", lambda _: "1")

    handle_complete([task], tasks_path)

    captured = capsys.readouterr()
    assert title in captured.out


@given(title=_titles)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_delete_confirmation_contains_title(title, monkeypatch, capsys, tmp_path):
    """For any non-empty, non-whitespace title, stdout after handle_delete
    contains the title.

    **Validates: Requirements 6.3**
    """
    from task_manager.cli import handle_delete

    tasks_path = str(tmp_path / "tasks.json")
    task = Task(title=title)
    monkeypatch.setattr("builtins.input", lambda _: "1")

    handle_delete([task], tasks_path)

    captured = capsys.readouterr()
    assert title in captured.out
