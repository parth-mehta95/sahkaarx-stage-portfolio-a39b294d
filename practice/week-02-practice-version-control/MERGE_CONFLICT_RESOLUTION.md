# Git Merge Conflict Resolution Documentation

**Repository**: `https://github.com/parth-mehta95/sahkaarx-stage-portfolio-a39b294d`  
**Target Branch**: `main`  
**Feature Branch**: `feature/data-loading-module`  
**Conflict Status**: Resolved & Verified  

---

## 1. Scenario Context

The data engineering team required a production-ready **`DataLoader`** module extending the existing abstract **`DataHandler`** base class.

During active development on `feature/data-loading-module`:
1. **Feature Branch (`feature/data-loading-module`)**:
   - Implemented `DataLoader` with memory-efficient batch chunking (`load_batches`), UTC audit metadata tagging (`loaded_at`, `batch_id`), and robust dictionary/DataFrame write capabilities.
2. **Main Branch (`main`)**:
   - Concurrently, a teammate merged updates into `main` introducing strict schema validation (`validate_schema`), explicit column type inference, and database connection timeout safeguards (`timeout=30.0`).
3. **The Conflict**:
   - Attempting to merge `feature/data-loading-module` into `main` caused Git merge conflicts in `practice/week-02-practice-version-control/data_loader.py` and `practice/week-02-practice-version-control/__init__.py`.

---

## 2. Conflicting Files and Conflict Markers

When running `git merge feature/data-loading-module`, Git flagged conflicts in two files:

```bash
Auto-merging practice/week-02-practice-version-control/data_loader.py
CONFLICT (content): Merge conflict in practice/week-02-practice-version-control/data_loader.py
Auto-merging practice/week-02-practice-version-control/__init__.py
CONFLICT (content): Merge conflict in practice/week-02-practice-version-control/__init__.py
Automatic merge failed; fix conflicts and then commit the result.
```

### Conflict Region 1: `data_loader.py` Constructor & Timeout Configuration

```python
<<<<<<< HEAD (main branch)
    def __init__(
        self,
        source: str = ":memory:",
        autocommit: bool = True,
        timeout: float = 30.0,
        **kwargs: Any
    ) -> None:
        super().__init__(source=source, **kwargs)
        self.autocommit: bool = autocommit
        self.timeout: float = timeout
        self._connection: Optional[sqlite3.Connection] = None
        self._cursor: Optional[sqlite3.Cursor] = None
=======
    def __init__(
        self,
        source: str = ":memory:",
        autocommit: bool = True,
        enable_audit_lineage: bool = True,
        **kwargs: Any
    ) -> None:
        super().__init__(source=source, **kwargs)
        self.autocommit: bool = autocommit
        self.enable_audit_lineage: bool = enable_audit_lineage
        self._connection: Optional[sqlite3.Connection] = None
        self._cursor: Optional[sqlite3.Cursor] = None
>>>>>>> feature/data-loading-module
```

### Conflict Region 2: `data_loader.py` Ingestion, Schema Checking & Batch Processing

```python
<<<<<<< HEAD (main branch)
    def validate_schema(self, table_name: str, required_columns: List[str]) -> bool:
        schema = self.get_table_schema(table_name)
        existing_cols = {col["name"].lower() for col in schema}
        missing = [c for c in required_columns if c.lower() not in existing_cols]
        if missing:
            raise DataValidationError(f"Table '{table_name}' missing required columns: {missing}")
        return True
=======
    def load_batches(
        self,
        query: str,
        batch_size: int = 100,
        params: Optional[Union[Sequence[Any], Dict[str, Any]]] = None,
        as_dict: bool = True
    ) -> Generator[List[Any], None, None]:
        conn = self._ensure_connected()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params or ())
            columns = [c[0] for c in cursor.description] if cursor.description else []
            while True:
                rows = cursor.fetchmany(batch_size)
                if not rows:
                    break
                yield [{col: r[col] for col in columns} for r in rows] if as_dict else [tuple(r) for r in rows]
        finally:
            cursor.close()
>>>>>>> feature/data-loading-module
```

### Conflict Region 3: `__init__.py` Package Exports

```python
<<<<<<< HEAD (main branch)
from data_handler import DataHandler, DataConnectionError, DataValidationError, DataExecutionError
from data_loader import DataLoader
__all__ = ["DataHandler", "DataLoader", "DataValidationError"]
=======
from data_handler import DataHandler, DataConnectionError, DataExecutionError
from data_loader import DataLoader, DatabaseDataLoader
__all__ = ["DataHandler", "DataLoader", "DatabaseDataLoader"]
>>>>>>> feature/data-loading-module
```

---

## 3. Resolution Strategy & Harmonized Implementation

Rather than picking one branch over the other (`ours` vs `theirs`), a **collaborative engineering resolution** was applied:

1. **Constructor (`__init__`)**:
   - Preserved both the `timeout` parameter and error resilience from `main` AND the `enable_audit_lineage` flexibility from `feature/data-loading-module`.
2. **Schema Validation & Batch Streaming**:
   - Retained `validate_schema` to ensure rigorous data quality before pipeline consumption.
   - Retained `load_batches` and audit tagging (`write_records` with `add_audit_metadata`) to guarantee scalability with large datasets.
3. **Module Exports (`__init__.py`)**:
   - Unified export definitions to expose `DataHandler`, `DataLoader`, `DatabaseDataLoader` (alias), and all custom exceptions (`DataValidationError`, `DataExecutionError`, `DataConnectionError`).

---

## 4. Execution Commands Used

```bash
# 1. Inspect status of conflicted files
git status

# 2. View exact diff and markers
git diff

# 3. Open conflicted files and remove markers (<<<<<<<, =======, >>>>>>>)
# Edit data_loader.py and __init__.py to include both sets of improvements

# 4. Run test suite to verify resolution logic
python -m pytest practice/week-02-practice-version-control/test_data_loader.py -v

# 5. Stage resolved files
git add practice/week-02-practice-version-control/data_loader.py
git add practice/week-02-practice-version-control/__init__.py

# 6. Finalize merge commit with descriptive message
git commit -m "Merge branch 'feature/data-loading-module' into main: Reconcile schema validation with batch chunking and audit metadata"

# 7. Confirm clean git graph
git log --graph --oneline -n 6
```

---

## 5. Verification & Test Evidence

All 22 unit tests for the data loading module pass with 100% success rate:

```text
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1
collected 22 items

practice/week-02-practice-version-control/test_data_loader.py::TestDataLoaderInheritance::test_subclass_contract PASSED
practice/week-02-practice-version-control/test_data_loader.py::TestDataLoaderInheritance::test_instance_polymorphism PASSED
practice/week-02-practice-version-control/test_data_loader.py::TestDataLoaderInheritance::test_alias_equivalence PASSED
practice/week-02-practice-version-control/test_data_loader.py::TestDataLoaderLifecycle::test_connect_and_disconnect PASSED
practice/week-02-practice-version-control/test_data_loader.py::TestDataLoaderLifecycle::test_context_manager PASSED
practice/week-02-practice-version-control/test_data_loader.py::TestDataLoaderLifecycle::test_invalid_source_raises_connection_error PASSED
practice/week-02-practice-version-control/test_data_loader.py::TestDataLoaderLifecycle::test_metadata_reporting PASSED
practice/week-02-practice-version-control/test_data_loader.py::TestDataOperations::test_query_execution_rowcount PASSED
practice/week-02-practice-version-control/test_data_loader.py::TestDataOperations::test_sql_injection_defense PASSED
practice/week-02-practice-version-control/test_data_loader.py::TestDataOperations::test_load_data_as_dicts PASSED
practice/week-02-practice-version-control/test_data_loader.py::TestDataOperations::test_load_data_as_tuples PASSED
practice/week-02-practice-version-control/test_data_loader.py::TestDataOperations::test_load_data_as_dataframe PASSED
practice/week-02-practice-version-control/test_data_loader.py::TestDataOperations::test_load_table_helper PASSED
practice/week-02-practice-version-control/test_data_loader.py::TestDataOperations::test_batch_generator PASSED
practice/week-02-practice-version-control/test_data_loader.py::TestDataOperations::test_write_records_with_audit_metadata PASSED
practice/week-02-practice-version-control/test_data_loader.py::TestDataOperations::test_abstract_read_write_delegation PASSED
practice/week-02-practice-version-control/test_data_loader.py::TestSchemaValidationAndTransactions::test_schema_validation_success PASSED
practice/week-02-practice-version-control/test_data_loader.py::TestSchemaValidationAndTransactions::test_schema_validation_failure PASSED
practice/week-02-practice-version-control/test_data_loader.py::TestSchemaValidationAndTransactions::test_transaction_rollback_on_failure PASSED
practice/week-02-practice-version-control/test_data_loader.py::TestSchemaValidationAndTransactions::test_transaction_commit_on_success PASSED
practice/week-02-practice-version-control/test_data_loader.py::TestErrorConditions::test_empty_query_raises_execution_error PASSED
practice/week-02-practice-version-control/test_data_loader.py::TestErrorConditions::test_invalid_sql_raises_execution_error PASSED

============================= 22 passed in 1.14s ==============================
```

