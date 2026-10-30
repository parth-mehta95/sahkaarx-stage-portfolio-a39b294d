# Practice: Version Control — Data Loading Module Integration & Peer Review

**Repository URL**: `https://github.com/parth-mehta95/sahkaarx-stage-portfolio-a39b294d`  
**Feature Branch**: `feature/data-loading-module`  
**Base Branch**: `main`  
**Pull Request Link**: `https://github.com/parth-mehta95/sahkaarx-stage-portfolio-a39b294d/pull/24`  
**Peer PR Review Link**: `https://github.com/parth-mehta95/sahkaarx-stage-portfolio-a39b294d/pull/25`  

---

## 1. Scenario & Objectives

In production data engineering environments, collaborative Git workflows and robust Object-Oriented design are paramount. This project delivers a production-ready **`DataLoader`** module extending the team's abstract **`DataHandler`** base class, submits a Pull Request, addresses reviewer critique, resolves realistic merge conflicts with `main`, and conducts a rigorous peer code review on a teammate's PR.

### Deliverables & Minimum Artifacts:
- **Production Data Loading Module**: Implemented in [`data_loader.py`](./data_loader.py) extending [`data_handler.py`](./data_handler.py).
- **Merged Pull Request Documentation**: Documented in [`PULL_REQUEST.md`](./PULL_REQUEST.md).
- **Git Merge Conflict Resolution Walkthrough**: Detailed in [`MERGE_CONFLICT_RESOLUTION.md`](./MERGE_CONFLICT_RESOLUTION.md).
- **Peer Code Review & Feedback**: Comprehensive review documented in [`PEER_PULL_REQUEST_REVIEW.md`](./PEER_PULL_REQUEST_REVIEW.md).
- **Automated Verification Suite**: 22 unit tests passing in [`test_data_loader.py`](./test_data_loader.py).
- **Conflict Simulation Script**: Runnable automation script in [`simulate_conflict.ps1`](./simulate_conflict.ps1).

---

## 2. Architecture & Object-Oriented Design

The data loading architecture leverages Object-Oriented Programming (OOP) principles to provide an extensible, secure, and reliable interface:

```
        +---------------------------------------------+
        |             DataHandler (ABC)               |
        +---------------------------------------------+
        | + source: Optional[str]                     |
        | + is_connected: bool                        |
        | + metadata: Dict[str, Any]                  |
        +---------------------------------------------+
        | + connect() -> Any           [abstract]     |
        | + disconnect() -> None       [abstract]     |
        | + read(*args, **kwargs)      [abstract]     |
        | + write(data, *args, **kwargs) [abstract]   |
        | + __enter__() / __exit__()                  |
        | + validate_source() -> bool                 |
        | + get_metadata() -> Dict[str, Any]          |
        +---------------------------------------------+
                               ^
                               | (Inherits & Extends)
        +---------------------------------------------+
        |                 DataLoader                  |
        |          (alias: DatabaseDataLoader)        |
        +---------------------------------------------+
        | + autocommit: bool                          |
        | + timeout: float                            |
        | - _connection: Optional[sqlite3.Connection] |
        | - _cursor: Optional[sqlite3.Cursor]         |
        +---------------------------------------------+
        | + connect() -> Connection                   |
        | + disconnect() -> None                      |
        | + execute_query(query, params) -> int       |
        | + execute_many(query, seq_params) -> int    |
        | + load_data(query, params, as_dict/df)      |
        | + load_batches(query, batch_size) -> Gen    |
        | + load_table(table_name, columns, limit)    |
        | + write_records(table_name, records, ...)   |
        | + validate_schema(table_name, req_cols)     |
        | + transaction() -> ContextManager[Cursor]   |
        | + read(...) & write(...) [overrides]        |
        +---------------------------------------------+
```

### Key Engineering Features:
1. **Inheritance & Polymorphism**: `DataLoader` inherits from `DataHandler`, ensuring uniform lifecycle control and interchangeable data handlers.
2. **Context Manager Protocol**: Native `__enter__` and `__exit__` support guarantees automatic connection cleanup without resource leakage.
3. **SQL Injection Defense**: Strict parameter binding for both DDL/DML and read operations ensures untrusted inputs cannot execute arbitrary SQL.
4. **Memory-Safe Batch Chunking**: `load_batches()` streams large result sets using Python generators and `fetchmany(batch_size)`.
5. **Atomic Transactions with Rollback**: `transaction()` context manager automatically triggers `connection.rollback()` if an error occurs mid-operation.
6. **UTC Audit Lineage**: Ingestion attaches `loaded_at` (ISO 8601 UTC) and `batch_id` metadata.

---

## 3. Pull Request Workflow & Reviewer Feedback (#24)

### Pull Request Lifecycle
1. Branch created from `main`: `feature/data-loading-module`.
2. Initial implementation committed with conventional commits:
   - `feat(data-handler): implement abstract DataHandler base class`
   - `feat(data-loader): implement DataLoader with SQL execution and batching`
3. Pull Request opened against `main` with detailed specification (see [`PULL_REQUEST.md`](./PULL_REQUEST.md)).
4. **Addressing Peer Reviewer Feedback**:
   - **Feedback 1 (SQL Injection)**: Replaced string formatting in queries with parameterized tuples/dictionaries.
   - **Feedback 2 (Transaction Safety)**: Added `transaction()` context manager with rollback capabilities on failure.
   - **Feedback 3 (Memory Usage)**: Added generator-based chunk streaming via `load_batches()`.
5. Resolved integration conflicts and merged into `main` with commit `ae57259`.

---

## 4. Git Merge Conflict Resolution

### Conflict Overview
While the feature branch was in review, teammate updates were merged to `main` introducing schema validation logic and timeout configurations. Merging `main` into `feature/data-loading-module` resulted in merge conflicts across `data_loader.py` and `__init__.py`.

### Resolution Strategy
- **Conflict Markers**:
  ```python
  <<<<<<< HEAD (main branch)
      def validate_schema(self, table_name: str, required_columns: List[str]) -> bool:
          ...
  =======
      def load_batches(self, query: str, batch_size: int = 100, ...):
          ...
  >>>>>>> feature/data-loading-module
  ```
- **Resolution**: Both code improvements were retained and harmonized into a unified class structure:
  - Preserved teammate schema verification (`validate_schema`) and timeout settings.
  - Retained feature branch batch streaming (`load_batches`) and audit metadata.
- **Verification**: Verified using `python -m pytest practice/week-02-practice-version-control/test_data_loader.py -v`.
- Full resolution steps are documented in [`MERGE_CONFLICT_RESOLUTION.md`](./MERGE_CONFLICT_RESOLUTION.md).

---

## 5. Peer Code Review Summary (Teammate PR #25)

As part of the team's peer review culture, a code review was conducted on teammate PR #25 (*"Add Cloud Object Storage S3 Adapter to DataHandler"*).

- **Full Review Document**: [`PEER_PULL_REQUEST_REVIEW.md`](./PEER_PULL_REQUEST_REVIEW.md)
- **Key Findings Identified**:
  1. **Security**: Hardcoded AWS credentials in default parameters -> Recommended using environment variables / IAM roles.
  2. **OOP Contract**: Missing `disconnect()` method -> Recommended implementing proper cleanup.
  3. **Scalability**: Buffering entire S3 files in memory via `.read()` -> Recommended chunked streaming.
  4. **Testing Quality**: Tests made real AWS network calls -> Recommended hermetic mocking with `unittest.mock`.
- **Outcome**: Changes requested, teammate updated the branch with commit `8f9b10a`, followed by formal approval.

---

## 6. How to Run the Demonstration and Tests

### 1. Run the Verification Test Suite
```bash
python -m pytest practice/week-02-practice-version-control/test_data_loader.py -v
```

### 2. Run the End-to-End Pipeline Demo
```bash
python practice/week-02-practice-version-control/example_usage.py
```

### 3. Re-run Merge Conflict Simulation
```powershell
.\practice\week-02-practice-version-control\simulate_conflict.ps1
```

---

## 7. Artifacts Index

| Artifact | File Path | Description |
| :--- | :--- | :--- |
| **Data Handler Base Class** | [`data_handler.py`](./data_handler.py) | Abstract base class with lifecycle hooks and context manager. |
| **Data Loading Module** | [`data_loader.py`](./data_loader.py) | Concrete SQL loader with batching, audit lineage, and transactions. |
| **Unit Test Suite** | [`test_data_loader.py`](./test_data_loader.py) | 22 comprehensive unit tests covering all features and edge cases. |
| **Pipeline Demo** | [`example_usage.py`](./example_usage.py) | Runnable demonstration script. |
| **Pull Request Document** | [`PULL_REQUEST.md`](./PULL_REQUEST.md) | GitHub PR description, reviewer critique, and merge history. |
| **Conflict Resolution Doc** | [`MERGE_CONFLICT_RESOLUTION.md`](./MERGE_CONFLICT_RESOLUTION.md) | Technical analysis of merge conflict markers and resolution. |
| **Peer Code Review** | [`PEER_PULL_REQUEST_REVIEW.md`](./PEER_PULL_REQUEST_REVIEW.md) | Constructive code review on teammate's S3 adapter pull request. |
| **Conflict Script** | [`simulate_conflict.ps1`](./simulate_conflict.ps1) | PowerShell script automating git branch, conflict, and merge workflow. |
