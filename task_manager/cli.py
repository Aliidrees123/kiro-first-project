"""CLI menu loop: run_app and handle_* functions."""

from task_manager.display import MENU, format_task_list
from task_manager.models import Task
from task_manager.operations import (
    AlreadyDoneError,
    add_task,
    complete_task,
    delete_task,
)
from task_manager.storage import TASKS_FILE, load_tasks, save_tasks


def handle_add(tasks: list[Task], tasks_path: str) -> list[Task]:
    """Prompt for a title, add the task, save, and print confirmation."""
    title = input("Enter task title: ").strip()
    try:
        updated = add_task(tasks, title)
    except ValueError as exc:
        print(f"Error: {exc}")
        return tasks
    save_tasks(updated, tasks_path)
    print(f"Added task: {title}")
    return updated


def handle_list(tasks: list[Task]) -> list[Task]:
    """Print the formatted task list."""
    print(format_task_list(tasks))
    return tasks


def handle_complete(tasks: list[Task], tasks_path: str) -> list[Task]:
    """Show list, prompt for index, mark task done, save, and print confirmation."""
    print(format_task_list(tasks))
    raw = input("Enter task number: ").strip()
    try:
        index = int(raw)
        updated = complete_task(tasks, index)
    except ValueError as exc:
        print(f"Error: {exc}")
        return tasks
    except AlreadyDoneError as exc:
        print(f"Error: {exc}")
        return tasks
    title = tasks[index - 1].title
    save_tasks(updated, tasks_path)
    print(f"Completed task: {title}")
    return updated


def handle_delete(tasks: list[Task], tasks_path: str) -> list[Task]:
    """Show list, prompt for index, delete task, save, and print confirmation."""
    print(format_task_list(tasks))
    raw = input("Enter task number: ").strip()
    try:
        index = int(raw)
        updated = delete_task(tasks, index)
    except ValueError as exc:
        print(f"Error: {exc}")
        return tasks
    title = tasks[index - 1].title
    save_tasks(updated, tasks_path)
    print(f"Deleted task: {title}")
    return updated


def run_app(tasks_path: str = TASKS_FILE) -> None:
    """Load tasks, enter the interactive menu loop, and dispatch on user input."""
    tasks = load_tasks(tasks_path)
    while True:
        print(MENU)
        choice = input("Enter choice: ").strip()
        match choice:
            case "1":
                tasks = handle_add(tasks, tasks_path)
            case "2":
                tasks = handle_list(tasks)
            case "3":
                tasks = handle_complete(tasks, tasks_path)
            case "4":
                tasks = handle_delete(tasks, tasks_path)
            case "5":
                break
            case _:
                print("Invalid option. Please enter 1-5.")
