"""JSON persistence: load_tasks and save_tasks."""

import json
import os
import sys
import tempfile

from task_manager.models import Task

TASKS_FILE = "tasks.json"


def load_tasks(path: str = TASKS_FILE) -> list[Task]:
    """Load tasks from JSON file.

    Returns an empty list if the file does not exist.
    Exits with status 1 if the file contains invalid JSON.
    """
    if not os.path.exists(path):
        return []

    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        print(f"Error: {path} contains invalid JSON: {exc}", file=sys.stderr)
        sys.exit(1)

    return [
        Task(title=item["title"], done=item["done"], id=item["id"]) for item in data
    ]


def save_tasks(tasks: list[Task], path: str = TASKS_FILE) -> None:
    """Serialise tasks to JSON and write atomically via a temp file + rename."""
    data = [{"id": task.id, "title": task.title, "done": task.done} for task in tasks]

    dir_name = os.path.dirname(os.path.abspath(path))
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        os.replace(tmp_path, path)
    except Exception:
        # Clean up the temp file if something goes wrong before the rename
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
