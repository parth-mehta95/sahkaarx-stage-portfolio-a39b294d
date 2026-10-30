"""
example_usage.py
Runnable end-to-end demonstration of the DataLoader module.
"""

from data_loader import DataLoader, DataValidationError


def main():
    print("=" * 70)
    print("   SAHKAARX DATA LOADER - PRODUCTION ETL DEMONSTRATION")
    print("=" * 70)

    # 1. Initialize and use DataLoader with context manager
    with DataLoader(":memory:", autocommit=True) as loader:
        print(f"\n[1] Connection established:")
        for k, v in loader.get_metadata().items():
            print(f"    - {k}: {v}")

        # 2. Ingest raw batches into database
        print("\n[2] Ingesting enterprise customer dataset with audit metadata...")
        customer_records = [
            {"customer_id": "C-101", "name": "Global Retail Partners", "tier": "ENTERPRISE", "revenue": 125000.0},
            {"customer_id": "C-102", "name": "Pacific Supply Chains", "tier": "MID_MARKET", "revenue": 45000.0},
            {"customer_id": "C-103", "name": "Apex FinTech Solutions", "tier": "ENTERPRISE", "revenue": 310000.0},
            {"customer_id": "C-104", "name": "Beacon Media Network", "tier": "GROWTH", "revenue": 18500.0},
            {"customer_id": "C-105", "name": "Summit Health Systems", "tier": "ENTERPRISE", "revenue": 520000.0},
        ]
        inserted = loader.write_records(
            table_name="customers",
            records=customer_records,
            if_exists="replace",
            add_audit_metadata=True,
            batch_id="INGEST_20261030_001"
        )
        print(f"    -> Successfully inserted {inserted} records with UTC timestamps & batch lineage.")

        # 3. Schema validation check
        print("\n[3] Validating customer table schema...")
        loader.validate_schema("customers", ["customer_id", "name", "tier", "revenue"])
        print("    -> Schema verification passed successfully!")

        # 4. Parameterized query execution (Safe from SQL injection)
        print("\n[4] Querying high-value enterprise accounts (parameterized query)...")
        query = "SELECT customer_id, name, revenue, loaded_at FROM customers WHERE tier = ? ORDER BY revenue DESC"
        results = loader.load_data(query, params=("ENTERPRISE",), as_dict=True)
        for row in results:
            rev = float(row['revenue'])
            print(f"    - [{row['customer_id']}] {row['name']:<25} | Revenue: ${rev:>9,.2f} | Loaded: {row['loaded_at']}")

        # 5. Batch streaming generator for large datasets
        print("\n[5] Streaming records via load_batches() generator (batch_size=2)...")
        batch_num = 1
        for batch in loader.load_batches("SELECT customer_id, name FROM customers", batch_size=2):
            names = [r["name"] for r in batch]
            print(f"    - Batch {batch_num} ({len(batch)} items): {', '.join(names)}")
            batch_num += 1

        # 6. Demonstrating atomic transaction management
        print("\n[6] Demonstrating transaction rollback on failure...")
        try:
            with loader.transaction() as cur:
                cur.execute("UPDATE customers SET revenue = revenue * 1.1 WHERE customer_id = 'C-101'")
                print("    - First step executed (revenue multiplied).")
                # Intentional error to demonstrate rollback
                raise RuntimeError("Simulated mid-transaction failure!")
        except RuntimeError:
            print("    -> Exception intercepted. Transaction rolled back successfully!")

        # Verify rollback took effect
        row = loader.load_data("SELECT revenue FROM customers WHERE customer_id = 'C-101'")[0]
        print(f"    -> Verified C-101 revenue unchanged: ${row['revenue']:,.2f}")

    print("\n" + "=" * 70)
    print("   DEMONSTRATION COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()
