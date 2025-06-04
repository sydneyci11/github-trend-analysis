# fetch_and_store.py

import duckdb
from update.fetch import fetch_all_pages, fetch_github_data
from config import DB_PATH, HEADERS

headers = HEADERS
db_path = DB_PATH

search_queries = [
    "deep learning",
    "machine learning",
    "ML",
    "AI robotics",
    "natural language processing",
    "NLP",
    "computer vision",
    "generative AI",
    "transformers",
    "open source llm",
    "autonomous vehicle",
    "AI infrastructure",
    "AI"
]

# Create & Connect to Duckdb Database
def setup_database():
    conn = duckdb.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS github_trends (
            name TEXT,
            full_name TEXT PRIMARY KEY,
            description TEXT,
            stars INTEGER,
            forks INTEGER,
            language TEXT,
            watchers INTEGER,
            commits INTEGER,
            issues INTEGER,
            created_at TEXT,
            updated_at TEXT,
            url TEXT
        )
    """)
    conn.commit()
    conn.close()  # Close connection after creating table
    print(f"Database successfully created at: {db_path}")

# Insert or update data
def save_to_db(repo_data):    
    # Reopen database connection inside function
    conn = duckdb.connect(db_path)
    cursor = conn.cursor()

    # Check if repo already exists
    cursor.execute("SELECT updated_at FROM github_trends WHERE full_name = ?", (repo_data[1],))
    result = cursor.fetchone()

    if result:
        db_updated_at = str(result[0])
        if db_updated_at != repo_data[10]: # only update the new changed data 
            # If repo exists, update the record
            sql_query = """UPDATE github_trends 
                           SET description=?, stars=?, forks=?, language=?, watchers=?, commits=?, issues=?, updated_at=?, url=? 
                           WHERE full_name=?"""

            # the UPDATE query doesn't need name, full_name, or created_at, so we slice them out.
            cursor.execute(sql_query, repo_data[2:10] + (repo_data[10], repo_data[1]))

            if cursor.rowcount > 0:
                # print(f"[UPDATE] {repo_data[1]} is updated")
                conn.commit()
                conn.close()
                return "update"  
            else:
                # print(f"[WARNING] {repo_data[1]} updated failed, please check the data!")
                conn.close()
                return None
    
    else:
        # Insert new record
        sql_query = """INSERT INTO github_trends 
                       (name, full_name, description, stars, forks, language, watchers, commits, issues, created_at, updated_at, url) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        cursor.execute(sql_query, repo_data)
        # print(f"[INSERT] {repo_data[1]} insert new data")
        return "insert"
        
    conn.commit()
    conn.close()  # Close connection after inserting

# Fetch and store main logic
def fetch_and_store_all(max_pages=3):
    setup_database()
    for search_query in search_queries:
        print(f"\nSearching for: {search_query}")
        all_repos = fetch_all_pages(search_query, headers, db_path, max_pages=max_pages)

        if all_repos:
            print(f"Successfully fetched {len(all_repos)} repositories!")
        else:
            print("No data fetched.")
        
        inserted = updated = skipped = 0

        for repo in all_repos:
            issue_count = repo.get("open_issues_count", 0)
            commits_url = f"https://api.github.com/repos/{repo['full_name']}/commits"
            commits_resp = fetch_github_data(commits_url, headers=HEADERS)
            commit_count = len(commits_resp) if isinstance(commits_resp, list) else 0

            repo_data = (
                repo.get("name") or "Unknown",
                repo.get("full_name") or "Unknown",
                repo.get("description") or "No description available",
                repo.get("stargazers_count") or 0,
                repo.get("forks_count") or 0,
                repo.get("language") or "Not specified",
                repo.get("watchers_count") or 0,
                commit_count,
                issue_count,
                repo.get("created_at") or "Unknown",
                repo.get("updated_at") or "Unknown",
                repo.get("html_url") or "No URL available"
            )
            result = save_to_db(repo_data)
            if result == "insert":
                inserted += 1
            elif result == "update":
                updated += 1
            else:
                skipped += 1
            
        print(f"{search_query} Completed → Inserted: {inserted}, Updated: {updated}, Skipped: {skipped}")
            