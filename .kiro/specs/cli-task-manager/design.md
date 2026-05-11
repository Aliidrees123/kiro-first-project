# Design Document: CLI Task Manager

## Overview

A single-file Python 3 CLI application (`first_project.py`) that presents an interactive menu loop for managing a to-do list. Tasks are persisted between sessions as JSON. The design separates pure logic (task operations, serialisation) from I/O (menu rendering, user input, file access) so that core logic is fully unit-testable without mocking the terminal.

---

## Architecture

The application is structured as three logical layers inside `first_project.py`, with helpers extracted into a `task_manager/` package as the project grows:

```
first_project.py          # Entry point — calls run_app()
task_manager/
    __init__.py
    models.py             # Task dataclass
    storage.py            # load_tasks / save_tasks (JSON I/O)
    operations.py         # add_task, complete_task, delete_task (pure logic)
    display.py            # format_task, format_task_list, menu strings
    cli.py                # run_app — menu loop, input handling
tests/
    test_models.py
    test_storage.py
    test_operations.py
    test_display.py
    test_cli.py
tasks.json                # Runtime persistence store (created on first save)
```

For the initial implementation all modules may live in a single `task_manager/` package imported by `first_project.py`. The entry point remains `python first_project.py`.

---

## Components

### 1. Task Model (`models.py`)

Represents a single unit of work.

```python
from dataclasses import dataclass, field
import uuid

@dataclass
class Task:
    title: str
    done: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
```

- `title`: non-empty string provided by the user.
- `done`: `False` on creation; set to `True` by the complete operation.
- `id`: stable UUID used internally; not exposed in the menu UI (the 1-based Task Index is positional).

### 2. Storage (`storage.py`)

Handles all file I/O. Both functions are pure with respect to the task list — they do not mutate global state.

```python
TASKS_FILE = "tasks.json"

def load_tasks(path: str = TASKS_FILE) -> list[Task]:
    """Load tasks from JSON. Returns [] if file absent. Exits non-zero on bad JSON."""

def save_tasks(tasks: list[Task], path: str = TASKS_FILE) -> None:
    """Serialise tasks to JSON and write atomically."""
```

**JSON schema** (array of objects):

```json
[
  {"id": "uuid-string", "title": "Buy milk", "done": false},
  {"id": "uuid-string", "title": "Write tests", "done": true}
]
```

`load_tasks` behaviour:
- File absent → return `[]`.
- File present, valid JSON → deserialise and return list of `Task`.
- File present, invalid JSON → print error to stderr, call `sys.exit(1)`.

`save_tasks` writes to a temporary file then renames to `TASKS_FILE` to avoid partial writes.

### 3. Operations (`operations.py`)

Pure functions that take a task list and return a new list (or raise `ValueError` for invalid input). No I/O.

```python
def add_task(tasks: list[Task], title: str) -> list[Task]:
    """Return new list with task appended. Raises ValueError for blank title."""

def complete_task(tasks: list[Task], index: int) -> list[Task]:
    """Return new list with task at 1-based index marked done.
    Raises ValueError for out-of-range index.
    Raises AlreadyDoneError for already-completed task."""

def delete_task(tasks: list[Task], index: int) -> list[Task]:
    """Return new list with task at 1-based index removed.
    Raises ValueError for out-of-range index."""
```

Custom exception:

```python
class AlreadyDoneError(Exception):
    pass
```

### 4. Display (`display.py`)

Pure functions that produce strings. No I/O, no ANSI codes.

```python
MENU = """
(1) Add task
(2) List tasks
(3) Complete task
(4) Delete task
(5) Quit
"""

def format_task(index: int, task: Task) -> str:
    """Return a single formatted line, e.g. '1. [ ] Buy milk' or '2. [x] Write tests'."""

def format_task_list(tasks: list[Task]) -> str:
    """Return the full formatted list, or a 'No tasks' message if empty."""
```

Status markers: `[ ]` for not done, `[x]` for done.

### 5. CLI / Menu Loop (`cli.py`)

Handles all terminal I/O and orchestrates the other components.

```python
def run_app(tasks_path: str = TASKS_FILE) -> None:
    tasks = load_tasks(tasks_path)
    while True:
        print_menu()
        choice = input("Enter choice: ").strip()
        match choice:
            case "1": handle_add(tasks, tasks_path)
            case "2": handle_list(tasks)
            case "3": handle_complete(tasks, tasks_path)
            case "4": handle_delete(tasks, tasks_path)
            case "5": break
            case _:   print("Invalid option. Please enter 1–5.")
```

Each `handle_*` function:
1. Calls the relevant display/operation function.
2. On success: saves, prints confirmation.
3. On `ValueError` / `AlreadyDoneError`: prints error, returns without saving.

### 6. Entry Point (`first_project.py`)

```python
from task_manager.cli import run_app

if __name__ == "__main__":
    run_app()
```

---

## Data Flow

```
startup
  └─ load_tasks(tasks.json) ──► [Task, ...]
                                      │
                              menu loop (cli.py)
                                      │
              ┌───────────────────────┼───────────────────────┐
              ▼                       ▼                       ▼
         add_task()           complete_task()          delete_task()
              │                       │                       │
              └───────────────────────┴───────────────────────┘
                                      │
                               save_tasks(tasks.json)
                                      │
                              print confirmation
                                      │
                              re-display menu
```

---

## Error Handling

| Situation | Behaviour |
|---|---|
| `tasks.json` absent on startup | Empty list, no error |
| `tasks.json` contains invalid JSON | Print error to stderr, `sys.exit(1)` |
| Blank/whitespace title on add | `ValueError` → print error, return to menu |
| Non-integer or out-of-range index | `ValueError` → print error, return to menu |
| Task already completed | `AlreadyDoneError` → print info message, return to menu |
| Invalid menu choice | Print error, re-display menu |

All error messages are plain text. No ANSI escape codes are used anywhere in the output.

---

## Testing Strategy

Tests live in `tests/` and are run with `pytest`. The split between pure logic and I/O means most tests require no mocking.

- **`test_models.py`** — Task dataclass construction and defaults.
- **`test_storage.py`** — `load_tasks` / `save_tasks` using `tmp_path` fixtures; invalid JSON exit behaviour.
- **`test_operations.py`** — `add_task`, `complete_task`, `delete_task` with various inputs including edge cases.
- **`test_display.py`** — `format_task`, `format_task_list` output strings.
- **`test_cli.py`** — Menu loop integration using `monkeypatch` / `capsys` for stdin/stdout.

Property-based tests use [Hypothesis](https://hypothesis.readthedocs.io/) and are co-located in the relevant test files.

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Persistence round-trip

*For any* list of tasks (with arbitrary titles and done statuses), calling `save_tasks` followed by `load_tasks` on the same path SHALL return a list that is element-wise equivalent to the original.

**Validates: Requirements 7.2, 7.3, 1.2**

---

### Property 2: Add task round-trip

*For any* non-empty, non-whitespace title string, calling `add_task` on any task list SHALL produce a new list whose last element has that exact title and `done=False`, and the list length SHALL be exactly one greater than before.

**Validates: Requirements 3.2**

---

### Property 3: Whitespace titles are rejected

*For any* string composed entirely of whitespace characters (spaces, tabs, newlines), `add_task` SHALL raise `ValueError` and the task list SHALL remain unchanged.

**Validates: Requirements 3.3**

---

### Property 4: Task list rendering is complete

*For any* non-empty list of tasks, `format_task_list` SHALL produce a string that contains every task's title, its 1-based index, and a status marker (`[ ]` or `[x]`) for each task.

**Validates: Requirements 4.1, 4.2, 4.3**

---

### Property 5: Valid index operations mutate exactly one task

*For any* task list and any valid 1-based index `i` (where `1 ≤ i ≤ len(tasks)`):
- `complete_task(tasks, i)` SHALL return a list of the same length where only the task at position `i` has `done` set to `True`, and all other tasks are unchanged.
- `delete_task(tasks, i)` SHALL return a list of length `len(tasks) - 1` that does not contain the task that was at position `i`, and all other tasks are unchanged.

**Validates: Requirements 5.2, 6.2**

---

### Property 6: Invalid index leaves list unchanged

*For any* task list and any integer index `i` that is outside the range `[1, len(tasks)]` (including zero, negative values, and values greater than the list length), both `complete_task` and `delete_task` SHALL raise `ValueError` and the task list SHALL be identical to the input list.

**Validates: Requirements 5.4, 6.4**

---

### Property 7: Operation confirmations contain the task title

*For any* task with an arbitrary title, the confirmation message produced after a successful add, complete, or delete operation SHALL contain that task's title as a substring.

**Validates: Requirements 3.4, 5.3, 6.3**

---

### Property 8: No ANSI escape codes in output

*For any* sequence of valid user inputs, all strings written to stdout by the application SHALL not contain ANSI escape sequences (i.e., no substrings matching the pattern `\x1b\[`).

**Validates: Requirements 8.2**

---

### Property 9: Invalid menu input leaves task list unchanged

*For any* string that is not one of `"1"`, `"2"`, `"3"`, `"4"`, or `"5"`, the menu handler SHALL display an error message and the task list SHALL remain identical to its state before the input was processed.

**Validates: Requirements 2.4**
