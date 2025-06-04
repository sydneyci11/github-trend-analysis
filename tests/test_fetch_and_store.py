# test_fetch_and_store.py

import os
import duckdb
from update.fetch_and_store import fetch_and_store_all
from config import DB_PATH

def test_fetch_and_store():
    # Run the full fetch and store pipeline
    fetch_and_store_all(max_pages=1)

    # Check if the DB file exists
    assert os.path.exists(DB_PATH), f"Database not found at {DB_PATH}"

    # Connect and verify table exists and not empty
    conn = duckdb.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM github_trends")
    count = cursor.fetchone()[0]
    
    assert count > 0, "No records were inserted into github_trends table"
    print(f"Test passed: {count} records found in github_trends.")

    conn.close()

if __name__ == "__main__":
    test_fetch_and_store()
