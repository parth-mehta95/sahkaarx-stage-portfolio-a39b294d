"""
test_data_loader.py
Comprehensive unit test suite for DataLoader and DataHandler OOP inheritance.
"""

import os
import sqlite3
import pytest
import pandas as pd

from data_handler import (
    DataHandler,
    DataHandlerError,
    DataConnectionError,
    DataValidationError,
    DataExecutionError,
)
from data_loader import DataLoader, DatabaseDataLoader


class TestDataLoaderInheritance:
    """Verifies Object-Oriented design and inheritance contracts."""

    def test_subclass_contract(self):
        """DataLoader must inherit from DataHandler base class."""
        assert issubclass(DataLoader, DataHandler)
        assert issubclass(DatabaseDataLoader, DataHandler)

    def test_instance_polymorphism(self):
        """DataLoader instance must be recognized as DataHandler."""
        loader = DataLoader(":memory:")
        assert isinstance(loader, DataHandler)
        assert isinstance(loader, DataLoader)

    def test_alias_equivalence(self):
        """DatabaseDataLoader must be an alias for DataLoader."""
        assert DatabaseDataLoader is DataLoader


class TestDataLoaderLifecycle:
    """Verifies connection lifecycle, context management, and state handling."""

    def test_connect_and_disconnect(self):
        loader = DataLoader(":memory:")
        assert not loader.is_connected
        assert loader.status == "INITIALIZED"

        conn = loader.connect()
        assert loader.is_connected
        assert loader.status == "CONNECTED"
        assert isinstance(conn, sqlite3.Connection)

        loader.disconnect()
        assert not loader.is_connected
        assert loader.status == "DISCONNECTED"

    def test_context_manager(self):
        loader = DataLoader(":memory:")
        with loader as ctx:
            assert ctx is loader
            assert ctx.is_connected
            # Verify operational inside context
            ctx.execute_query("CREATE TABLE test_ctx (id INT)")
        assert not loader.is_connected

    def test_invalid_source_raises_connection_error(self):
        loader = DataLoader(source="")
        with pytest.raises(DataConnectionError):
            loader.connect()

    def test_metadata_reporting(self):
        loader = DataLoader(":memory:")
        loader.connect()
        meta = loader.get_metadata()
        assert meta["handler_class"] == "DataLoader"
        assert meta["source"] == ":memory:"
        assert meta["is_connected"] is True
        assert "sqlite_version" in meta
        loader.disconnect()


class TestDataOperations:
    """Verifies CRUD execution, parameterized queries, and format flexibility."""

    @pytest.fixture
    def memory_loader(self):
        """Fixture providing connected in-memory DataLoader."""
        loader = DataLoader(":memory:")
        loader.connect()
        # Seed test table
        loader.execute_query(
            "CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, balance REAL, region TEXT)"
        )
        sample_rows = [
            (1, "Alice Corp", 15000.50, "North"),
            (2, "Bob Logistics", 8400.00, "South"),
            (3, "Charlie Retail", 23200.75, "North"),
        ]
        loader.execute_many("INSERT INTO customers VALUES (?, ?, ?, ?)", sample_rows)
        yield loader
        loader.disconnect()

    def test_query_execution_rowcount(self, memory_loader):
        rows = memory_loader.execute_query(
            "UPDATE customers SET balance = balance + 100 WHERE region = ?", ("North",)
        )
        assert rows == 2

    def test_sql_injection_defense(self, memory_loader):
        """Parameterized query must treat malicious payload as literal text."""
        malicious_input = "'; DROP TABLE customers; --"
        results = memory_loader.load_data(
            "SELECT * FROM customers WHERE name = ?", (malicious_input,)
        )
        assert len(results) == 0
        # Verify table was NOT dropped
        tables = memory_loader.get_table_names()
        assert "customers" in tables

    def test_load_data_as_dicts(self, memory_loader):
        results = memory_loader.load_data("SELECT * FROM customers WHERE id = 1", as_dict=True)
        assert len(results) == 1
        assert results[0]["name"] == "Alice Corp"
        assert results[0]["balance"] == 15000.50

    def test_load_data_as_tuples(self, memory_loader):
        results = memory_loader.load_data(
            "SELECT id, name FROM customers ORDER BY id", as_dict=False
        )
        assert len(results) == 3
        assert results[0] == (1, "Alice Corp")

    def test_load_data_as_dataframe(self, memory_loader):
        df = memory_loader.load_data("SELECT * FROM customers", as_dataframe=True)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert list(df.columns) == ["id", "name", "balance", "region"]

    def test_load_table_helper(self, memory_loader):
        data = memory_loader.load_table("customers", columns=["name", "region"], limit=2)
        assert len(data) == 2
        assert "name" in data[0]
        assert "region" in data[0]
        assert "balance" not in data[0]

    def test_batch_generator(self, memory_loader):
        batches = list(
            memory_loader.load_batches("SELECT * FROM customers ORDER BY id", batch_size=2)
        )
        assert len(batches) == 2  # 3 rows chunked into 2 + 1
        assert len(batches[0]) == 2
        assert len(batches[1]) == 1
        assert batches[0][0]["name"] == "Alice Corp"

    def test_write_records_with_audit_metadata(self, memory_loader):
        new_data = [
            {"order_id": 501, "amount": 99.95, "status": "COMPLETED"},
            {"order_id": 502, "amount": 149.50, "status": "PENDING"},
        ]
        inserted = memory_loader.write_records(
            table_name="orders",
            records=new_data,
            if_exists="replace",
            add_audit_metadata=True,
            batch_id="TEST_BATCH_001",
        )
        assert inserted == 2

        loaded = memory_loader.load_table("orders")
        assert len(loaded) == 2
        assert loaded[0]["batch_id"] == "TEST_BATCH_001"
        assert "loaded_at" in loaded[0]

    def test_abstract_read_write_delegation(self, memory_loader):
        """read() and write() must route correctly based on inputs."""
        # Test write via DataHandler contract
        records = [{"id": 10, "label": "Sensor A"}]
        memory_loader.write(records, table_name="devices")
        # Test read via DataHandler contract
        read_back = memory_loader.read("devices")
        assert len(read_back) == 1
        assert read_back[0]["label"] == "Sensor A"


class TestSchemaValidationAndTransactions:
    """Verifies schema validation and transactional safety with rollbacks."""

    def test_schema_validation_success(self):
        with DataLoader(":memory:") as loader:
            loader.execute_query("CREATE TABLE metrics (metric_name TEXT, val REAL, ts TEXT)")
            assert loader.validate_schema("metrics", ["metric_name", "val"])

    def test_schema_validation_failure(self):
        with DataLoader(":memory:") as loader:
            loader.execute_query("CREATE TABLE metrics (metric_name TEXT, val REAL)")
            with pytest.raises(DataValidationError):
                loader.validate_schema("metrics", ["metric_name", "nonexistent_col"])

    def test_transaction_rollback_on_failure(self):
        with DataLoader(":memory:") as loader:
            loader.execute_query("CREATE TABLE accounts (acc_id INT PRIMARY KEY, balance REAL)")
            loader.execute_query("INSERT INTO accounts VALUES (1, 500.0)")

            # Atomic transaction block with intentional mid-transaction error
            with pytest.raises(Exception):
                with loader.transaction() as cur:
                    cur.execute("UPDATE accounts SET balance = balance - 100 WHERE acc_id = 1")
                    # Trigger syntax or constraint error
                    cur.execute("INSERT INTO accounts VALUES (1, 999.0)")  # Primary key collision!

            # Verify balance was NOT deducted (rollback occurred)
            records = loader.load_data("SELECT balance FROM accounts WHERE acc_id = 1")
            assert records[0]["balance"] == 500.0

    def test_transaction_commit_on_success(self):
        with DataLoader(":memory:") as loader:
            loader.execute_query("CREATE TABLE accounts (acc_id INT PRIMARY KEY, balance REAL)")
            with loader.transaction() as cur:
                cur.execute("INSERT INTO accounts VALUES (1, 1000.0)")
                cur.execute("INSERT INTO accounts VALUES (2, 2000.0)")

            records = loader.load_data("SELECT COUNT(*) AS cnt FROM accounts")
            assert records[0]["cnt"] == 2


class TestErrorConditions:
    """Verifies proper custom exception handling."""

    def test_empty_query_raises_execution_error(self):
        with DataLoader(":memory:") as loader:
            with pytest.raises(DataExecutionError):
                loader.execute_query("")

    def test_invalid_sql_raises_execution_error(self):
        with DataLoader(":memory:") as loader:
            with pytest.raises(DataExecutionError):
                loader.execute_query("SELECT * FROM non_existent_table_xyz")

