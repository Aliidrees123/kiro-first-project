# Requirements Document

## Introduction

A CLI-based task manager (to-do list app) implemented in Python 3. The application runs via `python first_project.py` and presents an interactive menu loop in the terminal. Users can add, list, complete, and delete tasks. Tasks are persisted between sessions using a `tasks.json` file stored in the project directory. Each task has a title and a completion status. The codebase is ruff-compliant and tested with pytest under a `tests/` directory.

## Glossary

- **App**: The CLI task manager application, executed via `python first_project.py`.
- **Task**: A unit of work with a title (string) and a completion status (boolean: done or not done).
- **Task List**: The in-memory collection of all tasks loaded from the persistence store.
- **Persistence Store**: The `tasks.json` file in the project directory used to save and load tasks between sessions.
- **Menu**: The interactive terminal prompt presenting numbered options to the user.
- **Menu Option**: One of the five choices available in the Menu: add task, list tasks, complete task, delete task, or quit.
- **Task Index**: The 1-based integer identifier displayed to the user when listing tasks, used to reference a specific task for completion or deletion.

## Requirements

### Requirement 1: Application Entry Point

**User Story:** As a developer, I want to run the task manager with a single command, so that I can start using it without additional setup.

#### Acceptance Criteria

1. THE App SHALL be executable via the command `python first_project.py` from the project root directory.
2. WHEN the App starts, THE App SHALL load the Task List from the Persistence Store before displaying the Menu.
3. IF the Persistence Store file does not exist on startup, THEN THE App SHALL initialise an empty Task List and continue without error.

---

### Requirement 2: Interactive Menu Loop

**User Story:** As a user, I want an interactive menu that keeps running until I choose to quit, so that I can perform multiple operations in a single session.

#### Acceptance Criteria

1. WHEN the App has loaded the Task List, THE App SHALL display the Menu with the following five numbered options: (1) Add task, (2) List tasks, (3) Complete task, (4) Delete task, (5) Quit.
2. WHILE the user has not selected the Quit option, THE App SHALL re-display the Menu after each completed operation.
3. WHEN the user enters a Menu selection, THE App SHALL accept the input as a number corresponding to a Menu Option.
4. IF the user enters a value that does not correspond to a valid Menu Option, THEN THE App SHALL display an error message and re-display the Menu without modifying the Task List.

---

### Requirement 3: Add Task

**User Story:** As a user, I want to add a new task by providing a title, so that I can track things I need to do.

#### Acceptance Criteria

1. WHEN the user selects the Add Task Menu Option, THE App SHALL prompt the user to enter a task title.
2. WHEN the user provides a non-empty title, THE App SHALL create a Task with that title and a completion status of not done, append it to the Task List, and save the Task List to the Persistence Store.
3. IF the user provides an empty or whitespace-only title, THEN THE App SHALL display an error message and return to the Menu without adding a Task.
4. WHEN a Task is successfully added, THE App SHALL display a confirmation message including the task title.

---

### Requirement 4: List Tasks

**User Story:** As a user, I want to see all my tasks with their status, so that I can review what needs to be done.

#### Acceptance Criteria

1. WHEN the user selects the List Tasks Menu Option, THE App SHALL display all Tasks in the Task List, each on its own line.
2. WHEN displaying Tasks, THE App SHALL show each Task's Task Index, title, and completion status in a readable format.
3. WHEN displaying Tasks, THE App SHALL visually distinguish completed Tasks from not-done Tasks (e.g., using a checkmark or label).
4. IF the Task List is empty, THEN THE App SHALL display a message indicating there are no tasks.

---

### Requirement 5: Complete Task

**User Story:** As a user, I want to mark a task as done, so that I can track my progress.

#### Acceptance Criteria

1. WHEN the user selects the Complete Task Menu Option, THE App SHALL display the Task List and prompt the user to enter the Task Index of the Task to mark as done.
2. WHEN the user provides a valid Task Index, THE App SHALL set the completion status of the corresponding Task to done and save the Task List to the Persistence Store.
3. WHEN a Task is successfully marked as done, THE App SHALL display a confirmation message including the task title.
4. IF the user provides a Task Index that is not a positive integer or does not correspond to an existing Task, THEN THE App SHALL display an error message and return to the Menu without modifying the Task List.
5. IF the Task identified by the provided Task Index already has a completion status of done, THEN THE App SHALL display an informational message indicating the Task is already complete and return to the Menu without modifying the Task List.

---

### Requirement 6: Delete Task

**User Story:** As a user, I want to remove a task from the list, so that I can keep the list relevant.

#### Acceptance Criteria

1. WHEN the user selects the Delete Task Menu Option, THE App SHALL display the Task List and prompt the user to enter the Task Index of the Task to delete.
2. WHEN the user provides a valid Task Index, THE App SHALL remove the corresponding Task from the Task List and save the Task List to the Persistence Store.
3. WHEN a Task is successfully deleted, THE App SHALL display a confirmation message including the task title.
4. IF the user provides a Task Index that is not a positive integer or does not correspond to an existing Task, THEN THE App SHALL display an error message and return to the Menu without modifying the Task List.

---

### Requirement 7: Task Persistence

**User Story:** As a user, I want my tasks to be saved automatically, so that they are available the next time I run the app.

#### Acceptance Criteria

1. THE App SHALL store the Task List in a file named `tasks.json` located in the project root directory.
2. WHEN the Task List is modified (task added, completed, or deleted), THE App SHALL write the updated Task List to the Persistence Store before returning to the Menu.
3. WHEN the App starts, THE App SHALL read the Task List from the Persistence Store and restore all Tasks with their titles and completion statuses.
4. IF the Persistence Store file exists but contains invalid JSON, THEN THE App SHALL display an error message and exit with a non-zero exit code.

---

### Requirement 8: Terminal Output Quality

**User Story:** As a user, I want clean and readable terminal output, so that the app is easy to use.

#### Acceptance Criteria

1. THE App SHALL use consistent formatting for all terminal output, including clear section separators between the Menu and operation results.
2. THE App SHALL display all messages in plain text without ANSI escape codes or colour sequences that may not render correctly in all terminals.
3. WHEN displaying the Menu, THE App SHALL include a blank line before and after the list of Menu Options to improve readability.

---

### Requirement 9: Code Quality and Testing

**User Story:** As a developer, I want the codebase to be linted and tested, so that it is maintainable and correct.

#### Acceptance Criteria

1. THE App SHALL produce no errors or warnings when analysed with `ruff check .` using the project's ruff configuration.
2. THE App SHALL produce no formatting violations when checked with `ruff format --check .`.
3. THE App SHALL have tests located in the `tests/` directory at the project root, executable via the `pytest` command.
4. WHEN the test suite is run, THE App's core logic (task creation, completion, deletion, persistence load/save, and input validation) SHALL each have at least one corresponding test case.
