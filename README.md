# CLI Task Manager

A simple interactive to-do list app that runs in your terminal. Tasks are saved to `tasks.json` so they persist between sessions.

## Requirements

- Python 3.11+

## Setup

Install the dev dependencies (pytest, hypothesis, ruff):

```bash
pip install pytest hypothesis ruff
```

## Running the app

```bash
python first_project.py
```

You'll see a menu like this:

```
(1) Add task
(2) List tasks
(3) Complete task
(4) Delete task
(5) Quit
```

Enter a number to choose an option. Tasks are saved automatically after each change.

## Running the tests

```bash
pytest
```

## Linting and formatting

```bash
ruff check .
ruff format .
```

## Project structure

```
first_project.py        # Entry point
task_manager/
    models.py           # Task dataclass
    storage.py          # JSON load/save
    operations.py       # add, complete, delete logic
    display.py          # Formatting helpers and menu string
    cli.py              # Interactive menu loop
tests/
    test_models.py
    test_storage.py
    test_operations.py
    test_display.py
    test_cli.py
tasks.json              # Created automatically on first save
```
