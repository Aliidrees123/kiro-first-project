"""Tests for task_manager.operations."""

from copy import deepcopy

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from task_manager.models import Task
from task_manager.operations import (
    AlreadyDoneError,
    add_task,
    complete_task,
    delete_task,
)

# ---------------------------------------------------------------------------
# Hypothesis strategies
# ---------------------------------------------------------------------------

task_strategy = st.builds(
    Task,
    title=st.text(min_size=1).filter(lambda s: s.strip() != ""),
    done=st.booleans(),
)

task_list_strategy = st.lists(task_strategy)

whitespace_strategy = st.text(alphabet=" \t\n\r", min_size=1)


# ---------------------------------------------------------------------------
# Property 2: Add task round-trip
# Validates: Requirements 3.2
# ---------------------------------------------------------------------------


@given(
    tasks=task_list_strategy,
    title=st.text(min_size=1).filter(lambda s: s.strip() != ""),
)
def test_add_task_round_trip(tasks: list[Task], title: str) -> None:
    """**Validates: Requirements 3.2**

    For any non-empty, non-whitespace title, add_task returns a list whose
    length is len(tasks) + 1, whose last element has that exact title, and
    whose last element has done=False.
    """
    original_len = len(tasks)
    result = add_task(tasks, title)

    assert len(result) == original_len + 1
    assert result[-1].title == title
    assert result[-1].done is False


# ---------------------------------------------------------------------------
# Property 3: Whitespace titles are rejected
# Validates: Requirements 3.3
# ---------------------------------------------------------------------------


@given(tasks=task_list_strategy, whitespace_title=whitespace_strategy)
def test_whitespace_title_raises_value_error(
    tasks: list[Task], whitespace_title: str
) -> None:
    """**Validates: Requirements 3.3**

    For any whitespace-only string, add_task raises ValueError and the
    original task list is unchanged.
    """
    tasks_before = deepcopy(tasks)

    with pytest.raises(ValueError):
        add_task(tasks, whitespace_title)

    # The original list must be identical — add_task must not mutate it
    assert tasks == tasks_before


# ---------------------------------------------------------------------------
# Property 5: Valid index operations mutate exactly one task
# Validates: Requirements 5.2, 6.2
# ---------------------------------------------------------------------------


@given(
    tasks=st.lists(
        st.builds(Task, title=st.text(min_size=1), done=st.just(False)),
        min_size=1,
    ),
    index=st.integers(min_value=1),
)
def test_complete_task_valid_index(tasks: list[Task], index: int) -> None:
    """**Validates: Requirements 5.2**

    For any non-empty task list and valid 1-based index i (where the task at i
    is NOT already done), complete_task returns a list of the same length where
    only the task at position i has done=True, and all other tasks are unchanged.
    """
    assume(index <= len(tasks))

    result = complete_task(tasks, index)

    # Same length
    assert len(result) == len(tasks)

    # Only the target task is marked done
    assert result[index - 1].done is True

    # All other tasks are unchanged
    for i, (original, updated) in enumerate(zip(tasks, result), start=1):
        if i != index:
            assert updated == original


@given(
    tasks=st.lists(
        st.builds(
            Task,
            title=st.text(min_size=1),
            done=st.booleans(),
        ),
        min_size=1,
    ),
    index=st.integers(min_value=1),
)
def test_delete_task_valid_index(tasks: list[Task], index: int) -> None:
    """**Validates: Requirements 6.2**

    For any non-empty task list and valid 1-based index i, delete_task returns
    a list of length len(tasks) - 1 that does not contain the task that was at
    position i, and all other tasks are present and unchanged.
    """
    assume(index <= len(tasks))

    removed_task = tasks[index - 1]
    result = delete_task(tasks, index)

    # Length is one less
    assert len(result) == len(tasks) - 1

    # The removed task's id is not in the result
    result_ids = [t.id for t in result]
    assert removed_task.id not in result_ids

    # All other tasks are present and unchanged (by id and content)
    expected_remaining = [t for i, t in enumerate(tasks, start=1) if i != index]
    assert result == expected_remaining


# ---------------------------------------------------------------------------
# Property 6: Invalid index leaves list unchanged
# Validates: Requirements 5.4, 6.4
# ---------------------------------------------------------------------------


@given(
    tasks=task_list_strategy,
    index=st.one_of(
        st.integers(max_value=0),
        st.integers(min_value=1),
    ),
)
def test_complete_task_invalid_index(tasks: list[Task], index: int) -> None:
    """**Validates: Requirements 5.4**

    For any task list and any integer index outside [1, len(tasks)],
    complete_task raises ValueError and the task list is unchanged.
    """
    assume(index < 1 or index > len(tasks))

    tasks_before = deepcopy(tasks)

    with pytest.raises(ValueError):
        complete_task(tasks, index)

    assert tasks == tasks_before


@given(
    tasks=task_list_strategy,
    index=st.one_of(
        st.integers(max_value=0),
        st.integers(min_value=1),
    ),
)
def test_delete_task_invalid_index(tasks: list[Task], index: int) -> None:
    """**Validates: Requirements 6.4**

    For any task list and any integer index outside [1, len(tasks)],
    delete_task raises ValueError and the task list is unchanged.
    """
    assume(index < 1 or index > len(tasks))

    tasks_before = deepcopy(tasks)

    with pytest.raises(ValueError):
        delete_task(tasks, index)

    assert tasks == tasks_before


# ---------------------------------------------------------------------------
# Unit tests for operations edge cases
# Requirements: 5.5, 9.4
# ---------------------------------------------------------------------------


def test_complete_already_done_raises_already_done_error() -> None:
    """Completing an already-done task raises AlreadyDoneError."""
    task = Task(title="Already done", done=True)
    with pytest.raises(AlreadyDoneError):
        complete_task([task], 1)


def test_delete_only_task_returns_empty_list() -> None:
    """Deleting the only task in a list returns an empty list."""
    task = Task(title="Only task")
    result = delete_task([task], 1)
    assert result == []


def test_add_to_empty_list() -> None:
    """Adding a task to an empty list produces a list with one task."""
    result = add_task([], "My task")
    assert len(result) == 1
    assert result[0].title == "My task"
    assert result[0].done is False
