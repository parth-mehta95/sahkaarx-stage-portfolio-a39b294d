"""
example_usage.py
Demonstration script showing DatabaseLoader extending DataHandler in action.
"""

from database_loader import DatabaseLoader, DatabaseError


def main() -> None:
    print("=" * 60)
    print("DatabaseLoader Demo: OOP Data Loading with SQLite")
    print("=" * 60)

    # Initialize the DatabaseLoader using an in-memory SQLite database
    # Can also be a file path like 'analytics.db'
    db_loader = DatabaseLoader(source=":memory:")

    print(f"Initial Status: {db_loader.get_status()}")

    # Use context manager pattern for automatic connection and cleanup
    with db_loader as db:
        print(f"\n[+] Connected status: {db.is_connected}")
        print(f"[+] Metadata: {db.metadata}")

        # 1. Create a sample table
        print("\n[+] Creating 'sales' table...")
        db.execute_query("""
            CREATE TABLE sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                category TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL
            );
        """)

        # 2. Insert sample records
        sample_sales = [
            ("Laptop Pro 15", "Electronics", 3, 1299.99),
            ("Wireless Mouse", "Electronics", 15, 29.99),
            ("Standing Desk", "Furniture", 2, 450.00),
            ("Office Chair", "Furniture", 5, 220.00),
            ("Mechanical Keyboard", "Electronics", 7, 89.50),
        ]
        print(f"[+] Inserting {len(sample_sales)} records...")
        db.execute_many(
            "INSERT INTO sales (item_name, category, quantity, unit_price) VALUES (?, ?, ?, ?);",
            sample_sales
        )

        # 3. Inspect available tables
        tables = db.get_table_names()
        print(f"[+] Tables in database: {tables}")

        # 4. Query data using load_data with parameter binding
        category_to_query = "Electronics"
        print(f"\n[+] Querying products where category = '{category_to_query}':")
        electronics = db.load_data(
            "SELECT item_name, quantity, unit_price, (quantity * unit_price) AS total_revenue "
            "FROM sales WHERE category = ? ORDER BY total_revenue DESC;",
            params=(category_to_query,)
        )

        for record in electronics:
            print(f"    - {record['item_name']}: Qty={record['quantity']}, Price=${record['unit_price']:.2f}, Total=${record['total_revenue']:.2f}")

        # 5. Load full table using helper
        print("\n[+] Loading full table using load_table():")
        all_sales = db.load_table("sales", limit=3)
        for row in all_sales:
            print(f"    {row}")

    # Outside the 'with' block, connection is closed
    print(f"\n[+] Status after context manager exit: {db_loader.is_connected}")
    print("=" * 60)
    print("Demo completed successfully!")


if __name__ == "__main__":
    main()

