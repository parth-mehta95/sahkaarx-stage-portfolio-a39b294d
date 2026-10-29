"""
Unit tests for DataHandler and DatabaseLoader modules.
"""

import unittest
from data_handler import DataHandler
from database_loader import (
    DatabaseLoader,
    DatabaseConnectionError,
    DatabaseQueryError,
)


class TestDatabaseLoader(unittest.TestCase):
    """Test suite for DatabaseLoader extending DataHandler."""

    def setUp(self) -> None:
        """Initialize an in-memory DatabaseLoader before each test."""
        self.loader = DatabaseLoader(source=":memory:")

    def tearDown(self) -> None:
        """Disconnect and clean up resources after each test."""
        if self.loader.is_connected:
            self.loader.disconnect()

    def test_oop_inheritance_and_polymorphism(self) -> None:
        """Verify that DatabaseLoader inherits from DataHandler."""
        self.assertTrue(issubclass(DatabaseLoader, DataHandler))
        self.assertIsInstance(self.loader, DataHandler)
        self.assertEqual(self.loader.source, ":memory:")
        self.assertFalse(self.loader.is_connected)

    def test_connection_lifecycle(self) -> None:
        """Test connect and disconnect state transitions."""
        conn = self.loader.connect()
        self.assertIsNotNone(conn)
        self.assertTrue(self.loader.is_connected)
        self.assertIn("engine", self.loader.metadata)
        self.assertEqual(self.loader.metadata["engine"], "sqlite3")

        self.loader.disconnect()
        self.assertFalse(self.loader.is_connected)
        self.assertIsNone(self.loader._connection)

    def test_invalid_source_connection_error(self) -> None:
        """Verify that initializing/connecting with an empty source raises DatabaseConnectionError."""
        invalid_loader = DatabaseLoader(source="")
        with self.assertRaises(DatabaseConnectionError):
            invalid_loader.connect()

    def test_context_manager(self) -> None:
        """Test that DatabaseLoader operates correctly as a context manager."""
        with DatabaseLoader(source=":memory:") as db:
            self.assertTrue(db.is_connected)
            db.execute_query("CREATE TABLE test_ctx (id INT, val TEXT);")
            db.execute_query("INSERT INTO test_ctx VALUES (1, 'hello');")
            data = db.load_data("SELECT * FROM test_ctx")
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["val"], "hello")

        # After exiting context manager, connection should be closed
        self.assertFalse(db.is_connected)

    def test_execute_query_and_load_data_dict(self) -> None:
        """Test executing DDL/DML and loading structured records as dictionaries."""
        self.loader.connect()
        self.loader.execute_query(
            "CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, salary REAL);"
        )
        self.loader.execute_query(
            "INSERT INTO employees (name, salary) VALUES (?, ?);",
            ("Alice", 75000.0)
        )
        self.loader.execute_query(
            "INSERT INTO employees (name, salary) VALUES (?, ?);",
            ("Bob", 82000.0)
        )

        records = self.loader.load_data("SELECT * FROM employees ORDER BY id ASC")
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0], {"id": 1, "name": "Alice", "salary": 75000.0})
        self.assertEqual(records[1], {"id": 2, "name": "Bob", "salary": 82000.0})

    def test_execute_many_batch(self) -> None:
        """Test executing batch insertions."""
        self.loader.connect()
        self.loader.execute_query(
            "CREATE TABLE products (sku TEXT PRIMARY KEY, price REAL, stock INT);"
        )
        batch = [
            ("SKU-001", 19.99, 100),
            ("SKU-002", 49.99, 45),
            ("SKU-003", 9.99, 200),
        ]
        self.loader.execute_many(
            "INSERT INTO products (sku, price, stock) VALUES (?, ?, ?);",
            batch
        )

        rows = self.loader.load_data("SELECT * FROM products ORDER BY sku")
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["sku"], "SKU-001")
        self.assertEqual(rows[2]["stock"], 200)

    def test_parameterized_query(self) -> None:
        """Test parameter binding prevents SQL injection and returns filtered rows."""
        self.loader.connect()
        self.loader.execute_query("CREATE TABLE users (id INT, role TEXT);")
        self.loader.execute_many(
            "INSERT INTO users VALUES (?, ?);",
            [(1, "admin"), (2, "developer"), (3, "designer"), (4, "developer")]
        )

        devs = self.loader.load_data(
            "SELECT * FROM users WHERE role = ? ORDER BY id;",
            params=("developer",)
        )
        self.assertEqual(len(devs), 2)
        self.assertEqual(devs[0]["id"], 2)
        self.assertEqual(devs[1]["id"], 4)

    def test_load_data_as_tuples(self) -> None:
        """Test loading data as tuples instead of dictionaries."""
        self.loader.connect()
        self.loader.execute_query("CREATE TABLE metrics (metric TEXT, value REAL);")
        self.loader.execute_query("INSERT INTO metrics VALUES ('accuracy', 0.94);")

        data = self.loader.load_data("SELECT metric, value FROM metrics;", as_dict=False)
        self.assertEqual(data, [("accuracy", 0.94)])

    def test_get_table_names_and_load_table(self) -> None:
        """Test metadata retrieval and load_table utility."""
        self.loader.connect()
        self.loader.execute_query("CREATE TABLE orders (order_id INT, amount REAL);")
        self.loader.execute_query("CREATE TABLE customers (cust_id INT, name TEXT);")

        tables = self.loader.get_table_names()
        self.assertIn("orders", tables)
        self.assertIn("customers", tables)

        self.loader.execute_many(
            "INSERT INTO orders VALUES (?, ?);",
            [(101, 250.0), (102, 140.0), (103, 90.0)]
        )

        # Test load_table with limit
        orders = self.loader.load_table("orders", limit=2)
        self.assertEqual(len(orders), 2)
        self.assertEqual(orders[0]["order_id"], 101)

    def test_query_error_handling(self) -> None:
        """Test that malformed queries raise DatabaseQueryError."""
        self.loader.connect()
        with self.assertRaises(DatabaseQueryError):
            self.loader.load_data("SELECT * FROM non_existent_table;")

        with self.assertRaises(DatabaseQueryError):
            self.loader.load_data("")


if __name__ == "__main__":
    unittest.main()

