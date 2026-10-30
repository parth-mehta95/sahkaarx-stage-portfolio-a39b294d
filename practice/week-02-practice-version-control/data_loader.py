"""
data_loader.py
Production-ready Data Loading Module extending the DataHandler base class.

Provides robust SQL database connectivity, parameterized queries, batch chunking,
schema validation, transactional integrity, and audit metadata injection.
"""

from contextlib import contextmanager
from datetime import datetime, timezone
import logging
import sqlite3
from typing import Any, Dict, Generator, List, Optional, Sequence, Union

from data_handler import (
    DataHandler,
    DataConnectionError,
    DataExecutionError,
    DataValidationError,
)

logger = logging.getLogger("DataLoader")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class DataLoader(DataHandler):
    """
    Production-ready Data Loading Module extending DataHandler.

    Features:
    - Thread-safe SQL database management with connection lifecycles.
    - Parameterized query execution protecting against SQL injection attacks.
    - Flexible output formats: Dict records, tuples, or pandas DataFrames.
    - Memory-efficient batch chunking generator for large datasets.
    - Transaction context manager (`with loader.transaction():`) with automatic rollback on error.
    - Schema validation against required columns before ingestion.
    - UTC audit metadata tagging (`loaded_at`, `batch_id`) for lineage tracking.
    """

    def __init__(
        self,
        source: str = ":memory:",
        autocommit: bool = True,
        timeout: float = 30.0,
        **kwargs: Any
    ) -> None:
        """
        Initialize the DataLoader instance.

        :param source: Database path or URI (e.g., ':memory:', 'warehouse.db').
        :param autocommit: Whether to automatically commit DML transactions.
        :param timeout: Database connection timeout in seconds.
        :param kwargs: Additional connection configurations.
        """
        super().__init__(source=source, **kwargs)
        self.autocommit: bool = autocommit
        self.timeout: float = timeout
        self._connection: Optional[sqlite3.Connection] = None
        self._cursor: Optional[sqlite3.Cursor] = None

    def connect(self) -> sqlite3.Connection:
        """
        Establish connection to SQLite database.

        :return: Active sqlite3.Connection instance.
        :raises DataConnectionError: If connection fails.
        """
        if self.is_connected and self._connection is not None:
            logger.debug("Database connection already open.")
            return self._connection

        if not self.validate_source():
            raise DataConnectionError(f"Invalid database source provided: '{self.source}'")

        try:
            logger.info(f"Connecting to database source '{self.source}'...")
            self._connection = sqlite3.connect(
                self.source,
                timeout=self.timeout,
                **self.config
            )
            # Use sqlite3.Row for accessible dictionary-like row querying
            self._connection.row_factory = sqlite3.Row
            self._cursor = self._connection.cursor()
            self.is_connected = True
            self.status = "CONNECTED"
            self.metadata = {
                "engine": "sqlite3",
                "source": self.source,
                "timeout": self.timeout,
                "sqlite_version": sqlite3.sqlite_version,
            }
            logger.info(f"Connected successfully to '{self.source}'.")
            return self._connection
        except Exception as exc:
            self.is_connected = False
            self.status = "ERROR"
            self._connection = None
            self._cursor = None
            logger.error(f"Failed to connect to '{self.source}': {exc}")
            raise DataConnectionError(f"Database connection error for '{self.source}': {exc}") from exc

    def disconnect(self) -> None:
        """
        Safely terminate connection and release resources.
        """
        try:
            if self._cursor is not None:
                self._cursor.close()
                self._cursor = None

            if self._connection is not None:
                if self.autocommit:
                    try:
                        self._connection.commit()
                    except Exception:
                        pass
                self._connection.close()
                self._connection = None

            self.is_connected = False
            self.status = "DISCONNECTED"
            logger.info(f"Successfully disconnected from '{self.source}'.")
        except Exception as exc:
            logger.warning(f"Warning during database disconnect: {exc}")
            self.is_connected = False
            self._connection = None
            self._cursor = None

    def _ensure_connected(self) -> sqlite3.Connection:
        """Internal helper ensuring valid active connection."""
        if not self.is_connected or self._connection is None:
            return self.connect()
        return self._connection

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Cursor, None, None]:
        """
        Context manager for atomic transaction control.
        Commits on normal exit; automatically rolls back on unhandled exceptions.

        Yields:
            sqlite3.Cursor: Active transaction cursor.
        """
        conn = self._ensure_connected()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
            logger.debug("Transaction committed successfully.")
        except Exception as exc:
            conn.rollback()
            logger.error(f"Transaction rolled back due to error: {exc}")
            raise
        finally:
            cursor.close()

    def execute_query(
        self,
        query: str,
        params: Optional[Union[Sequence[Any], Dict[str, Any]]] = None
    ) -> int:
        """
        Execute a DDL or DML statement (CREATE, INSERT, UPDATE, DELETE).

        :param query: SQL statement.
        :param params: Optional query parameters for safe binding.
        :return: Number of rows affected.
        :raises DataExecutionError: If query execution fails.
        """
        conn = self._ensure_connected()
        if not query or not query.strip():
            raise DataExecutionError("SQL query string cannot be empty.")

        try:
            cursor = conn.cursor()
            if params is not None:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if self.autocommit:
                conn.commit()

            rowcount = cursor.rowcount
            cursor.close()
            return rowcount
        except Exception as exc:
            logger.error(f"Error executing query: {exc} | Query: {query}")
            raise DataExecutionError(f"Query execution failed: {exc}") from exc

    def execute_many(
        self,
        query: str,
        seq_of_params: Sequence[Union[Sequence[Any], Dict[str, Any]]]
    ) -> int:
        """
        Execute a batch parameterized query across multiple parameter sets.

        :param query: Parameterized SQL statement.
        :param seq_of_params: Sequence of parameter tuples or dictionaries.
        :return: Total number of rows affected.
        :raises DataExecutionError: If batch execution fails.
        """
        conn = self._ensure_connected()
        if not query or not query.strip():
            raise DataExecutionError("SQL query string cannot be empty.")
        if not seq_of_params:
            return 0

        try:
            cursor = conn.cursor()
            cursor.executemany(query, seq_of_params)
            if self.autocommit:
                conn.commit()
            rowcount = cursor.rowcount
            cursor.close()
            return rowcount
        except Exception as exc:
            logger.error(f"Error in batch execution: {exc} | Query: {query}")
            raise DataExecutionError(f"Batch execution failed: {exc}") from exc

    def load_data(
        self,
        query: str,
        params: Optional[Union[Sequence[Any], Dict[str, Any]]] = None,
        as_dict: bool = True,
        as_dataframe: bool = False
    ) -> Any:
        """
        Load records from database by executing a SELECT query.

        :param query: SQL SELECT statement.
        :param params: Safe parameter bindings.
        :param as_dict: Return records as list of dictionaries.
        :param as_dataframe: Return records as a pandas DataFrame.
        :return: Query results in requested format.
        :raises DataExecutionError: If query fails.
        """
        conn = self._ensure_connected()
        query_str = query.strip() if query else ""
        if not query_str:
            raise DataExecutionError("SQL query cannot be empty.")

        try:
            cursor = conn.cursor()
            if params is not None:
                cursor.execute(query_str, params)
            else:
                cursor.execute(query_str)

            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description] if cursor.description else []
            cursor.close()

            if as_dataframe:
                try:
                    import pandas as pd
                    data = [tuple(r) for r in rows]
                    return pd.DataFrame(data, columns=columns)
                except ImportError:
                    logger.warning("pandas is not installed; returning list of dicts instead.")

            if as_dict:
                return [{col: row[col] for col in columns} for row in rows]
            else:
                return [tuple(r) for r in rows]
        except Exception as exc:
            logger.error(f"Failed to load data: {exc} | Query: {query_str}")
            raise DataExecutionError(f"Data loading failed: {exc}") from exc

    def load_batches(
        self,
        query: str,
        batch_size: int = 100,
        params: Optional[Union[Sequence[Any], Dict[str, Any]]] = None,
        as_dict: bool = True
    ) -> Generator[List[Any], None, None]:
        """
        Generator yielding chunked batches of records for memory-efficient ingestion.

        :param query: SQL SELECT query.
        :param batch_size: Number of records per batch.
        :param params: Parameter bindings.
        :param as_dict: Format batches as list of dictionaries.
        :yields: Lists of records chunked by batch_size.
        """
        conn = self._ensure_connected()
        if batch_size <= 0:
            raise ValueError("batch_size must be a positive integer.")

        cursor = conn.cursor()
        try:
            if params is not None:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            columns = [col[0] for col in cursor.description] if cursor.description else []

            while True:
                rows = cursor.fetchmany(batch_size)
                if not rows:
                    break
                if as_dict:
                    yield [{col: r[col] for col in columns} for r in rows]
                else:
                    yield [tuple(r) for r in rows]
        finally:
            cursor.close()

    def load_table(
        self,
        table_name: str,
        columns: Optional[List[str]] = None,
        limit: Optional[int] = None,
        as_dict: bool = True,
        as_dataframe: bool = False
    ) -> Any:
        """
        Convenience method to load records directly from a table.

        :param table_name: Database table name.
        :param columns: Optional subset of columns to retrieve.
        :param limit: Maximum rows to return.
        :param as_dict: Format as dictionary list.
        :param as_dataframe: Format as pandas DataFrame.
        :return: Loaded records.
        """
        col_str = ", ".join(f'"{c}"' for c in columns) if columns else "*"
        query = f"SELECT {col_str} FROM {table_name}"
        if limit is not None:
            query += f" LIMIT {int(limit)}"
        return self.load_data(query, as_dict=as_dict, as_dataframe=as_dataframe)

    def write_records(
        self,
        table_name: str,
        records: List[Dict[str, Any]],
        if_exists: str = "append",
        batch_size: Optional[int] = 500,
        add_audit_metadata: bool = False,
        batch_id: Optional[str] = None
    ) -> int:
        """
        Write a list of dictionary records to a target database table.

        :param table_name: Destination table name.
        :param records: List of dictionary records to insert.
        :param if_exists: Action if table exists: 'append' or 'replace'.
        :param batch_size: Number of records to insert per batch chunk.
        :param add_audit_metadata: Whether to add 'loaded_at' and 'batch_id' fields.
        :param batch_id: Optional identifier for the batch ingestion.
        :return: Total number of rows inserted.
        :raises DataExecutionError: If write fails.
        """
        if not records:
            logger.info("No records provided to write.")
            return 0

        self._ensure_connected()

        # Normalize records and optionally enrich with audit metadata
        current_time = datetime.now(timezone.utc).isoformat()
        current_batch_id = batch_id or f"batch_{int(datetime.now(timezone.utc).timestamp())}"

        prepared_records: List[Dict[str, Any]] = []
        for r in records:
            item = dict(r)
            if add_audit_metadata:
                item["loaded_at"] = current_time
                item["batch_id"] = current_batch_id
            prepared_records.append(item)

        columns = list(prepared_records[0].keys())

        if if_exists == "replace":
            self.execute_query(f"DROP TABLE IF EXISTS {table_name}")

        # Auto-create table if not existing with inferring column types
        def _infer_type(val: Any) -> str:
            if isinstance(val, int) and not isinstance(val, bool):
                return "INTEGER"
            elif isinstance(val, float):
                return "REAL"
            elif isinstance(val, (bytes, bytearray)):
                return "BLOB"
            return "TEXT"

        sample = prepared_records[0]
        cols_def = ", ".join([f'"{col}" {_infer_type(sample.get(col))}' for col in columns])
        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({cols_def})"
        self.execute_query(create_sql)

        # Prepare parameterized insert
        col_names = ", ".join([f'"{c}"' for c in columns])
        placeholders = ", ".join(["?" for _ in columns])
        insert_sql = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})"

        values = [[rec.get(c) for c in columns] for rec in prepared_records]

        total_inserted = 0
        chunk_size = batch_size if batch_size and batch_size > 0 else len(values)

        for i in range(0, len(values), chunk_size):
            chunk = values[i : i + chunk_size]
            inserted = self.execute_many(insert_sql, chunk)
            total_inserted += len(chunk) if inserted >= 0 else 0

        logger.info(f"Successfully wrote {total_inserted} rows into table '{table_name}'.")
        return total_inserted

    def validate_schema(self, table_name: str, required_columns: List[str]) -> bool:
        """
        Validate whether the given table contains all required columns.

        :param table_name: Table to inspect.
        :param required_columns: Column names expected to be present.
        :return: True if valid.
        :raises DataValidationError: If any required column is missing.
        """
        schema = self.get_table_schema(table_name)
        existing_cols = {col["name"].lower() for col in schema}
        missing = [c for c in required_columns if c.lower() not in existing_cols]

        if missing:
            err_msg = f"Table '{table_name}' is missing required columns: {missing}"
            logger.error(err_msg)
            raise DataValidationError(err_msg)

        logger.info(f"Schema validation succeeded for table '{table_name}'.")
        return True

    def get_table_names(self) -> List[str]:
        """Retrieve list of user table names in connected database."""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        results = self.load_data(query, as_dict=False)
        return [row[0] for row in results]

    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Retrieve column schema metadata for a specified table."""
        query = f"PRAGMA table_info({table_name});"
        return self.load_data(query, as_dict=True)

    # Implement DataHandler abstract methods
    def read(self, *args: Any, **kwargs: Any) -> Any:
        """
        DataHandler abstract method implementation.
        Delegates to load_data or load_table based on arguments.
        """
        if args and isinstance(args[0], str):
            first_arg = args[0].strip()
            if first_arg.upper().startswith("SELECT"):
                return self.load_data(first_arg, *args[1:], **kwargs)
            else:
                return self.load_table(first_arg, **kwargs)
        if "query" in kwargs:
            return self.load_data(**kwargs)
        if "table_name" in kwargs:
            return self.load_table(**kwargs)
        raise DataExecutionError("read() requires a SQL query string or table_name.")

    def write(self, data: Any, *args: Any, **kwargs: Any) -> Any:
        """
        DataHandler abstract method implementation.
        Writes records or executes insert statements.
        """
        table_name = kwargs.get("table_name") or (args[0] if args else None)
        if not table_name:
            raise DataExecutionError("write() requires a 'table_name' destination.")

        if isinstance(data, list) and (len(data) == 0 or isinstance(data[0], dict)):
            return self.write_records(
                table_name=table_name,
                records=data,
                if_exists=kwargs.get("if_exists", "append"),
                batch_size=kwargs.get("batch_size", 500),
                add_audit_metadata=kwargs.get("add_audit_metadata", False),
            )
        elif hasattr(data, "to_dict"):
            # Handles pandas DataFrame
            records = data.to_dict(orient="records")
            return self.write_records(
                table_name=table_name,
                records=records,
                if_exists=kwargs.get("if_exists", "append"),
                batch_size=kwargs.get("batch_size", 500),
                add_audit_metadata=kwargs.get("add_audit_metadata", False),
            )
        else:
            raise DataExecutionError(f"Unsupported data format for write(): {type(data)}")


# Alias for backward compatibility and multi-name support
DatabaseDataLoader = DataLoader
