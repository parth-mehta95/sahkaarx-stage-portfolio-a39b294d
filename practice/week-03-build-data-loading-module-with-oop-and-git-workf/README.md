# Build Data Loading Module with OOP and Git Workflow

## Task Brief
Extend the DataHandler class with a database connection module, commit to feature branch, and submit a pull request with conflict resolution.

## Scenario
Your team needs a database loader module. Create it, push to a feature branch, and resolve merge conflicts when integrating with main.

## Deliverables
- DatabaseLoader class extending DataHandler
- Feature branch with pull request

## Success Criteria
- DatabaseLoader connects to SQL database
- Pull request includes clear commit messages

---

## Implementation Overview

### 1. Architecture & OOP Design
- **[`data_handler.py`](./data_handler.py)**: Abstract base class `DataHandler` establishing standard data loading interface and context manager lifecycle (`__enter__`, `__exit__`).
- **[`database_loader.py`](./database_loader.py)**: Subclass `DatabaseLoader(DataHandler)` providing:
  - SQL database connectivity (SQLite standard library out-of-the-box).
  - Secure parameterized query execution (`execute_query`, `execute_many`).
  - Structured data extraction into dictionaries, tuples, or pandas DataFrames (`load_data`, `load_table`).
  - Safe error hierarchy (`DatabaseError`, `DatabaseConnectionError`, `DatabaseQueryError`).
- **[`__init__.py`](./__init__.py)**: Exposes `DataHandler`, `DatabaseLoader`, and exceptions for import.

### 2. Verification & Testing
- **[`test_database_loader.py`](./test_database_loader.py)**: Automated unit test suite verifying inheritance, connection lifecycle, DDL/DML, parameter binding, context managers, and error handling.
- **[`example_usage.py`](./example_usage.py)**: Runnable demonstration script illustrating database setup and queries.

### 3. Git Workflow, PR & Conflict Resolution
- **[`GIT_WORKFLOW.md`](./GIT_WORKFLOW.md)**: Exact command-by-command instructions for creating feature branches, pushing commits, resolving conflicts, and merging into `main`.
- **[`PULL_REQUEST.md`](./PULL_REQUEST.md)**: Complete pull request template, description of changes, commit history, and conflict resolution documentation.

---

## Implementation Overview

### 1. Architecture & OOP Design
- **[`data_handler.py`](./data_handler.py)**: Abstract base class `DataHandler` establishing standard data loading interface and context manager lifecycle (`__enter__`, `__exit__`).
- **[`database_loader.py`](./database_loader.py)**: Subclass `DatabaseLoader(DataHandler)` providing:
  - SQL database connectivity (SQLite standard library out-of-the-box).
  - Secure parameterized query execution (`execute_query`, `execute_many`).
  - Structured data extraction into dictionaries, tuples, or pandas DataFrames (`load_data`, `load_table`).
  - Safe error hierarchy (`DatabaseError`, `DatabaseConnectionError`, `DatabaseQueryError`).
- **[`__init__.py`](./__init__.py)**: Exposes `DataHandler`, `DatabaseLoader`, and exceptions for import.

### 2. Verification & Testing
- **[`test_database_loader.py`](./test_database_loader.py)**: Automated unit test suite verifying inheritance, connection lifecycle, DDL/DML, parameter binding, context managers, and error handling.
- **[`example_usage.py`](./example_usage.py)**: Runnable demonstration script illustrating database setup and queries.

### 3. Git Workflow, PR & Conflict Resolution
- **[`GIT_WORKFLOW.md`](./GIT_WORKFLOW.md)**: Exact command-by-command instructions for creating feature branches, pushing commits, resolving conflicts, and merging into `main`.
- **[`PULL_REQUEST.md`](./PULL_REQUEST.md)**: Complete pull request template, description of changes, commit history, and conflict resolution documentation.
