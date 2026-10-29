"""
database_loader.py
Implements DatabaseLoader class extending DataHandler for SQL database operations.
"""

import sqlite3
from typing import Any, Dict, List, Optional, Sequence, Union
import logging
from data_handler import DataHandler

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Base exception for database loader errors."""
    pass


class DatabaseConnectionError(DatabaseError):
    """Raised when establishing or terminating a database connection fails."""
    pass


class DatabaseQueryError(DatabaseError):
    """Raised when executing a query or loading data fails."""
    pass


class DatabaseLoader(DataHandler):
    """
    DatabaseLoader class extending DataHandler.
    
    Provides concrete implementations for connecting to SQL databases (e.g., SQLite),
    executing parameterized queries, loading datasets into structured records or DataFrames,
    and managing connection lifecycles safely.
    """

    def __init__(self, source: str, autocommit: bool = True, **kwargs: Any) -> None:
        """
        Initialize the DatabaseLoader.

        :param source: Database path or URI (e.g., ':memory:', 'data/app.db').
        :param autocommit: Whether to automatically commit DML operations.
        :param kwargs: Additional connection arguments (e.g., timeout, detect_types).
        """
        super().__init__(source=source, **kwargs)
        self.autocommit: bool = autocommit
        self._connection: Optional[sqlite3.Connection] = None
        self._cursor: Optional[sqlite3.Cursor] = None

    def connect(self) -> sqlite3.Connection:
        """
        Establish a connection to the SQL database.

        :return: Active sqlite3.Connection object.
        :raises DatabaseConnectionError: If connection cannot be established.
        """
        if self.is_connected and self._connection is not None:
            logger.debug("Database connection already active.")
            return self._connection

        if not self.validate_source():
            raise DatabaseConnectionError(f"Invalid database source provided: '{self.source}'")

        try:
            logger.info(f"Connecting to database at '{self.source}'...")
            self._connection = sqlite3.connect(
                self.source,
                **self.config
            )
            # Row factory can default to sqlite3.Row for flexible access
            self._connection.row_factory = sqlite3.Row
            self._cursor = self._connection.cursor()
            self.is_connected = True
            self.metadata = {
                "engine": "sqlite3",
                "source": self.source,
                "driver_version": sqlite3.version,
                "sqlite_version": sqlite3.sqlite_version,
            }
            logger.info(f"Successfully connected to database at '{self.source}'.")
            return self._connection
        except Exception as exc:
            self.is_connected = False
            self._connection = None
            self._cursor = None
            logger.error(f"Failed to connect to database at '{self.source}': {exc}")
            raise DatabaseConnectionError(f"Connection to '{self.source}' failed: {exc}") from exc

    def disconnect(self) -> None:
        """
        Close active cursor and connection to the database.
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
            logger.info(f"Disconnected from database at '{self.source}'.")
        except Exception as exc:
            logger.warning(f"Error while closing database connection: {exc}")
            self.is_connected = False
            self._connection = None
            self._cursor = None

    def _ensure_connected(self) -> None:
        """Helper to verify connection state or auto-connect."""
        if not self.is_connected or self._connection is None:
            self.connect()

    def execute_query(
        self,
        query: str,
        params: Optional[Union[Sequence[Any], Dict[str, Any]]] = None
    ) -> int:
        """
        Execute a DDL or DML statement (CREATE, INSERT, UPDATE, DELETE).

        :param query: SQL query string.
        :param params: Optional parameters for parameterized query.
        :return: Number of rows affected or cursor.rowcount.
        :raises DatabaseQueryError: If query execution fails.
        """
        self._ensure_connected()
        assert self._connection is not None

        try:
            cursor = self._connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if self.autocommit:
                self._connection.commit()

            rowcount = cursor.rowcount
            cursor.close()
            return rowcount
        except Exception as exc:
            logger.error(f"Query execution error: {exc}\nQuery: {query}")
            raise DatabaseQueryError(f"Failed to execute query: {exc}") from exc

    def execute_many(
        self,
        query: str,
        seq_of_params: Sequence[Union[Sequence[Any], Dict[str, Any]]]
    ) -> int:
        """
        Execute multiple SQL statements in batch (e.g. batch INSERT).

        :param query: SQL query string with parameter placeholders.
        :param seq_of_params: Sequence of parameter tuples or dictionaries.
        :return: Number of rows affected.
        """
        self._ensure_connected()
        assert self._connection is not None

        try:
            cursor = self._connection.cursor()
            cursor.executemany(query, seq_of_params)
            if self.autocommit:
                self._connection.commit()
            rowcount = cursor.rowcount
            cursor.close()
            return rowcount
        except Exception as exc:
            logger.error(f"Batch execution error: {exc}\nQuery: {query}")
            raise DatabaseQueryError(f"Failed to execute batch query: {exc}") from exc

    def load_data(
        self,
        query_or_params: str,
        params: Optional[Union[Sequence[Any], Dict[str, Any]]] = None,
        as_dict: bool = True,
        as_dataframe: bool = False,
        **kwargs: Any
    ) -> Any:
        """
        Load data from the database by executing a SELECT query.

        :param query_or_params: SQL SELECT statement.
        :param params: Optional query parameters for safe binding.
        :param as_dict: If True and as_dataframe is False, return list of dictionaries.
        :param as_dataframe: If True, return a pandas.DataFrame (requires pandas).
        :param kwargs: Additional options.
        :return: List of dicts, list of tuples, or pandas DataFrame.
        :raises DatabaseQueryError: If query fails.
        """
        self._ensure_connected()
        assert self._connection is not None

        query = query_or_params.strip()
        if not query:
            raise DatabaseQueryError("SQL query string cannot be empty.")

        try:
            cursor = self._connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description] if cursor.description else []
            cursor.close()

            if as_dataframe:
                try:
                    import pandas as pd
                    # Convert sqlite3.Row rows into raw tuples/dicts
                    data = [tuple(row) for row in rows]
                    return pd.DataFrame(data, columns=columns)
                except ImportError:
                    logger.warning("pandas library not installed. Falling back to list of dicts.")

            if as_dict:
                return [{col: row[col] for col in columns} for row in rows]
            else:
                return [tuple(row) for row in rows]

        except Exception as exc:
            logger.error(f"Failed to load data for query '{query}': {exc}")
            raise DatabaseQueryError(f"Error loading data: {exc}") from exc

    def load_table(
        self,
        table_name: str,
        columns: Optional[List[str]] = None,
        limit: Optional[int] = None,
        as_dict: bool = True,
        as_dataframe: bool = False
    ) -> Any:
        """
        Helper method to load an entire table.

        :param table_name: Name of the table.
        :param columns: List of columns to select (defaults to '*').
        :param limit: Maximum number of rows to return.
        :param as_dict: Return records as list of dicts.
        :param as_dataframe: Return as pandas DataFrame.
        :return: Loaded table data.
        """
        cols = ", ".join(columns) if columns else "*"
        query = f"SELECT {cols} FROM {table_name}"
        if limit is not None:
            query += f" LIMIT {int(limit)}"
        return self.load_data(query, as_dict=as_dict, as_dataframe=as_dataframe)

    def get_table_names(self) -> List[str]:
        """
        Retrieve names of all user tables in the connected database.

        :return: List of table names.
        """
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        results = self.load_data(query, as_dict=False)
        return [row[0] for row in results]

    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Retrieve schema information for a given table.

        :param table_name: Name of the table.
        :return: List of dictionaries containing column metadata.
        """
        query = f"PRAGMA table_info({table_name});"
        return self.load_data(query, as_dict=True)

