"""Tests for task_manager.storage."""

import tempfile

import pytest
from hypothesis import given
from hypothesis import strategies as st

from task_manager.models import Task
from task_manager.storage import load_tasks, save_tasks

# Strategy that generates arbitrary Task objects with non-empty titles
task_strategy = st.builds(
    Task,
    title=st.text(min_size=1),
    done=st.booleans(),
)


@given(st.lists(task_strategy))
def test_persistence_round_trip(tasks: list[Task]) -> None:
    """Property 1: Persistence round-trip.

    For any list of tasks, save_tasks then load_tasks returns an
    element-wise equivalent list (same id, title, done for each task).

    Validates: Requirements 7.2, 7.3, 1.2
    """
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        path = tmp.name

    save_tasks(tasks, path)
    loaded = load_tasks(path)

    assert len(loaded) == len(tasks)
    for original, restored in zip(tasks, loaded):
        assert restored.id == original.id
        assert restored.title == original.title
        assert restored.done == original.done


def test_load_tasks_missing_file(tmp_path):
    """load_tasks returns [] when the file does not exist (Requirement 1.3, 7.4)."""
    missing = tmp_path / "nonexistent.json"
    assert load_tasks(str(missing)) == []


def test_load_tasks_invalid_json(tmp_path):
    """load_tasks calls sys.exit(1) on invalid JSON (Requirement 1.3, 7.4, 9.4)."""
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(SystemExit) as exc_info:
        load_tasks(str(bad_file))
    assert exc_info.value.code == 1
