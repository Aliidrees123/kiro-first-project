"""Display formatting: format_task, format_task_list, MENU."""

from task_manager.models import Task

MENU = """
(1) Add task
(2) List tasks
(3) Complete task
(4) Delete task
(5) Quit
"""


def format_task(index: int, task: Task) -> str:
    """Return a single formatted line.

    Examples:
        '1. [ ] Buy milk'   (not done)
        '2. [x] Write tests' (done)
    """
    marker = "[x]" if task.done else "[ ]"
    return f"{index}. {marker} {task.title}"


def format_task_list(tasks: list[Task]) -> str:
    """Return the full formatted list, or 'No tasks.' if the list is empty."""
    if not tasks:
        return "No tasks."
    return "\n".join(format_task(i + 1, task) for i, task in enumerate(tasks))
