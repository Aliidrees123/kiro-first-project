"""Tests for task_manager.models."""

from task_manager.models import Task


def test_task_default_done_is_false():
    task = Task(title="Buy milk")
    assert task.done is False


def test_task_default_id_is_nonempty_string():
    task = Task(title="Buy milk")
    assert isinstance(task.id, str)
    assert len(task.id) > 0


def test_two_tasks_have_distinct_ids():
    task_a = Task(title="First task")
    task_b = Task(title="Second task")
    assert task_a.id != task_b.id
