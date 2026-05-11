# Implementation Plan: CLI Task Manager

## Overview

Implement a Python 3 CLI task manager as a `task_manager/` package with an interactive menu loop, JSON persistence, and a pytest test suite. The entry point is `first_project.py`. Code must be ruff-compliant. Implementation proceeds layer by layer — models → storage → operations → display → CLI — then wires everything together through the entry point.

---

## Tasks

- [x] 1. Set up project structure and package skeleton
  - Create `task_manager/` directory with an `__init__.py`
  - Create empty module files: `models.py`, `storage.py`, `operations.py`, `display.py`, `cli.py`
  - Create `tests/` directory with an `__init__.py` and empty test files: `test_models.py`, `test_storage.py`, `test_operations.py`, `test_display.py`, `test_cli.py`
  - Add a `pyproject.toml` (or `ruff.toml`) with ruff configuration enabling at minimum `E`, `F`, and `I` rule sets
  - _Requirements: 1.1, 9.1, 9.2, 9.3_

- [x] 2. Implement the Task model
  - [x] 2.1 Write the `Task` dataclass in `task_manager/models.py`
    - Fields: `title: str`, `done: bool = False`, `id: str` (UUID default factory)
    - _Requirements: 3.2, 7.3_

  - [x] 2.2 Write unit tests for the Task model in `test_models.py`
    - Test default field values (`done=False`, auto-generated UUID)
    - Test that two separately constructed tasks receive distinct IDs
    - _Requirements: 9.4_

- [x] 3. Implement storage (JSON persistence)
  - [x] 3.1 Write `load_tasks` and `save_tasks` in `task_manager/storage.py`
    - `load_tasks(path)`: returns `[]` when file absent; deserialises JSON to `list[Task]`; prints to stderr and calls `sys.exit(1)` on invalid JSON
    - `save_tasks(tasks, path)`: serialises to JSON; writes atomically via a temp file + rename
    - _Requirements: 1.2, 1.3, 7.1, 7.2, 7.3, 7.4_

  - [x] 3.2 Write property test for persistence round-trip (`test_storage.py`)
    - **Property 1: Persistence round-trip** — for any list of tasks, `save_tasks` then `load_tasks` returns an element-wise equivalent list
    - **Validates: Requirements 7.2, 7.3, 1.2**
    - Use `hypothesis` with `tmp_path`-style temp files
    - _Requirements: 9.4_

  - [x] 3.3 Write unit tests for storage edge cases (`test_storage.py`)
    - Test missing file returns empty list
    - Test invalid JSON triggers `sys.exit(1)` (use `pytest.raises(SystemExit)`)
    - _Requirements: 1.3, 7.4, 9.4_

- [x] 4. Implement task operations (pure logic)
  - [x] 4.1 Write `add_task`, `complete_task`, `delete_task`, and `AlreadyDoneError` in `task_manager/operations.py`
    - `add_task`: appends new Task; raises `ValueError` for blank/whitespace title
    - `complete_task`: marks task at 1-based index done; raises `ValueError` for out-of-range; raises `AlreadyDoneError` if already done
    - `delete_task`: removes task at 1-based index; raises `ValueError` for out-of-range
    - All functions return a new list and do not mutate the input
    - _Requirements: 3.2, 3.3, 5.2, 5.4, 5.5, 6.2, 6.4_

  - [x] 4.2 Write property test for `add_task` round-trip (`test_operations.py`)
    - **Property 2: Add task round-trip** — for any non-empty, non-whitespace title, the result list length is `len(tasks) + 1` and the last element has that exact title and `done=False`
    - **Validates: Requirements 3.2**

  - [x] 4.3 Write property test for whitespace title rejection (`test_operations.py`)
    - **Property 3: Whitespace titles are rejected** — for any whitespace-only string, `add_task` raises `ValueError` and the list is unchanged
    - **Validates: Requirements 3.3**

  - [x] 4.4 Write property test for valid index operations (`test_operations.py`)
    - **Property 5: Valid index operations mutate exactly one task** — `complete_task` marks only the target task done; `delete_task` removes only the target task
    - **Validates: Requirements 5.2, 6.2**

  - [x] 4.5 Write property test for invalid index operations (`test_operations.py`)
    - **Property 6: Invalid index leaves list unchanged** — out-of-range indices (zero, negative, > len) raise `ValueError` and leave the list unchanged
    - **Validates: Requirements 5.4, 6.4**

  - [x] 4.6 Write unit tests for operations edge cases (`test_operations.py`)
    - Test `AlreadyDoneError` when completing an already-done task
    - Test deleting the only task returns an empty list
    - Test adding to an empty list
    - _Requirements: 5.5, 9.4_

- [x] 5. Checkpoint — Ensure all tests pass
  - Run `pytest` and confirm all tests pass; run `ruff check .` and confirm no violations. Ask the user if questions arise.

- [x] 6. Implement display formatting
  - [x] 6.1 Write `format_task`, `format_task_list`, and `MENU` constant in `task_manager/display.py`
    - `format_task(index, task)`: returns `"N. [ ] Title"` or `"N. [x] Title"`
    - `format_task_list(tasks)`: returns full formatted list or a "No tasks" message for empty list
    - `MENU`: multi-line string with options (1)–(5), with a blank line before and after the options block
    - No ANSI escape codes anywhere
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 8.1, 8.2, 8.3_

  - [x] 6.2 Write property test for task list rendering completeness (`test_display.py`)
    - **Property 4: Task list rendering is complete** — for any non-empty task list, `format_task_list` output contains every task's title, its 1-based index, and a status marker (`[ ]` or `[x]`)
    - **Validates: Requirements 4.1, 4.2, 4.3**

  - [x] 6.3 Write property test for no ANSI codes in output (`test_display.py`)
    - **Property 8: No ANSI escape codes in output** — `format_task` and `format_task_list` output never contains the pattern `\x1b[`
    - **Validates: Requirements 8.2**

  - [x] 6.4 Write unit tests for display functions (`test_display.py`)
    - Test `format_task` for done and not-done tasks
    - Test `format_task_list` with empty list returns "no tasks" message
    - Test `MENU` contains all five option strings
    - _Requirements: 4.3, 4.4, 9.4_

- [x] 7. Implement the CLI menu loop
  - [x] 7.1 Write `run_app` and all `handle_*` functions in `task_manager/cli.py`
    - `run_app(tasks_path)`: loads tasks, enters `while True` menu loop, dispatches on user input
    - `handle_add`: prompts for title, calls `add_task`, saves, prints confirmation with title
    - `handle_list`: calls `format_task_list`, prints result
    - `handle_complete`: shows list, prompts for index, calls `complete_task`, saves, prints confirmation with title; handles `ValueError` and `AlreadyDoneError`
    - `handle_delete`: shows list, prompts for index, calls `delete_task`, saves, prints confirmation with title; handles `ValueError`
    - Invalid menu choice prints error and re-displays menu without modifying task list
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.4, 5.1, 5.3, 5.5, 6.1, 6.3_

  - [x] 7.2 Write property test for confirmation messages containing task title (`test_cli.py`)
    - **Property 7: Operation confirmations contain the task title** — for any task title, the stdout output after a successful add, complete, or delete contains that title as a substring
    - **Validates: Requirements 3.4, 5.3, 6.3**
    - Use `monkeypatch` and `capsys`

  - [x] 7.3 Write property test for invalid menu input (`test_cli.py`)
    - **Property 9: Invalid menu input leaves task list unchanged** — any string not in `{"1","2","3","4","5"}` causes an error message and leaves the task list unchanged
    - **Validates: Requirements 2.4**

  - [x] 7.4 Write unit tests for CLI menu loop (`test_cli.py`)
    - Test option "5" exits the loop
    - Test add flow with valid and blank titles
    - Test complete flow with valid index, out-of-range index, and already-done task
    - Test delete flow with valid and out-of-range index
    - Test list flow with empty and non-empty task lists
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.3, 3.4, 5.1, 5.3, 5.4, 5.5, 6.1, 6.3, 6.4, 9.4_

- [x] 8. Wire up the entry point
  - [x] 8.1 Write `first_project.py` to import and call `run_app`
    - `from task_manager.cli import run_app` under `if __name__ == "__main__": run_app()`
    - _Requirements: 1.1_

- [x] 9. Final checkpoint — Ensure all tests pass
  - Run `pytest` and confirm all tests pass; run `ruff check .` and `ruff format --check .` and confirm no violations. Ask the user if questions arise.

---

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Property tests use [Hypothesis](https://hypothesis.readthedocs.io/); add it to your dependencies before running them
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at natural layer boundaries
- All output must be plain text — no ANSI codes anywhere in the codebase

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["2.1"] },
    { "id": 1, "tasks": ["2.2", "3.1"] },
    { "id": 2, "tasks": ["3.2", "3.3", "4.1"] },
    { "id": 3, "tasks": ["4.2", "4.3", "4.4", "4.5", "4.6", "6.1"] },
    { "id": 4, "tasks": ["6.2", "6.3", "6.4", "7.1"] },
    { "id": 5, "tasks": ["7.2", "7.3", "7.4", "8.1"] }
  ]
}
```
