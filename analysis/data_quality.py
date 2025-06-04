# data_quality.py

import duckdb
from config import DB_PATH

db_path = DB_PATH

def check_placeholder_entries(db_path):
    conn = duckdb.connect(db_path)
    df = conn.execute("""
        SELECT * FROM github_trends 
        WHERE description = 'No description available' OR language = 'Not specified'
    """).fetchdf()
    conn.close()

    if df.empty:
        print("No placeholder values found in the database.")
        return

    print("Repositories with placeholder description/language:")
    print(df.head(10).to_string())

    desc_count = (df['description'] == 'No description available').sum()
    lang_count = (df['language'] == 'Not specified').sum()
    total_rows = len(df)

    print("-" * 40)
    print(f"Data Quality Report")
    print(f"- Total affected repositories: {total_rows}")
    print(f"- With placeholder description: {desc_count}")
    print(f"- With unspecified language: {lang_count}")

if __name__ == "__main__":
    check_placeholder_entries(db_path)
    