"""Pure task operations: add_task, complete_task, delete_task."""

from dataclasses import replace

from task_manager.models import Task


class AlreadyDoneError(Exception):
    """Raised when attempting to complete a task that is already done."""


def add_task(tasks: list[Task], title: str) -> list[Task]:
    """Return a new list with a new Task appended.

    Raises ValueError if title is blank or whitespace-only.
    Does not mutate the input list.
    """
    if not title or not title.strip():
        raise ValueError("Task title must not be blank or whitespace.")
    return [*tasks, Task(title=title)]


def complete_task(tasks: list[Task], index: int) -> list[Task]:
    """Return a new list with the task at 1-based index marked done.

    Raises ValueError if index is out of range.
    Raises AlreadyDoneError if the task is already done.
    Does not mutate the input list.
    """
    if index < 1 or index > len(tasks):
        raise ValueError(f"Index {index} is out of range. Valid range: 1–{len(tasks)}.")
    task = tasks[index - 1]
    if task.done:
        raise AlreadyDoneError(f"Task {index} is already done.")
    new_tasks = list(tasks)
    new_tasks[index - 1] = replace(task, done=True)
    return new_tasks


def delete_task(tasks: list[Task], index: int) -> list[Task]:
    """Return a new list with the task at 1-based index removed.

    Raises ValueError if index is out of range.
    Does not mutate the input list.
    """
    if index < 1 or index > len(tasks):
        raise ValueError(f"Index {index} is out of range. Valid range: 1–{len(tasks)}.")
    return [task for i, task in enumerate(tasks, start=1) if i != index]
