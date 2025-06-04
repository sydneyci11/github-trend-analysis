# keyword_update.py

import duckdb
from update.fetch import fetch_all_pages, fetch_github_data
from config import DB_PATH, HEADERS

db_path = DB_PATH
headers = HEADERS

def update_one_keyword(query: str, max_pages=3, batch_size=10) -> dict:
    """
    Given one keyword, fetch GitHub repos and update DuckDB.
    Return {'inserted': X, 'updated': Y, 'skipped': Z}
    """
    print(f"\n[Keyword] {query}")
    all_repos = fetch_all_pages(query, headers, db_path, max_pages=max_pages)
    print(f"Fetched {len(all_repos)} repos")

    conn = duckdb.connect(DB_PATH)
    cursor = conn.cursor()

    insert_count = update_count = skip_count = 0
    changes_made = 0  # Track how many operations were made since last commit

    for i, repo in enumerate(all_repos):
        full_name = repo.get("full_name")
        updated_at = repo.get("updated_at")

        cursor.execute("SELECT updated_at FROM github_trends WHERE full_name = ?", (full_name,))
        result = cursor.fetchone()

        try:
            commits_url = f"https://api.github.com/repos/{full_name}/commits"
            commits_resp = fetch_github_data(commits_url, headers)
            commit_count = len(commits_resp) if isinstance(commits_resp, list) else 0
        except Exception as e:
            print(f"[Error] Commit fetch failed for {full_name}: {e}")
            commit_count = 0

        issue_count = repo.get("open_issues_count", 0)

        repo_data = (
            repo.get("name") or "Unknown",
            full_name or "Unknown",
            repo.get("description") or "No description available",
            repo.get("stargazers_count") or 0,
            repo.get("forks_count") or 0,
            repo.get("language") or "Not specified",
            repo.get("watchers_count") or 0,
            commit_count,
            issue_count,
            repo.get("created_at") or "Unknown",
            updated_at or "Unknown",
            repo.get("html_url") or "No URL available"
        )

        if result:
            db_updated_at = str(result[0])
            if db_updated_at != updated_at:
                cursor.execute("""
                    UPDATE github_trends 
                    SET description=?, stars=?, forks=?, language=?, watchers=?, commits=?, issues=?, updated_at=?, url=?
                    WHERE full_name=?
                """, repo_data[2:11] + (full_name,))
                update_count += 1
                changes_made += 1
            else:
                skip_count += 1
        else:
            cursor.execute("""
                INSERT INTO github_trends 
                (name, full_name, description, stars, forks, language, watchers, commits, issues, created_at, updated_at, url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, repo_data)
            insert_count += 1
            changes_made += 1

        # Every batch_size operations, commit
        if changes_made % batch_size == 0:
            conn.commit()

    # Final commit for remaining changes
    conn.commit()
    conn.close()

    print(f"[Done] {query}: inserted={insert_count}, updated={update_count}, skipped={skip_count}")
    return {"inserted": insert_count, "updated": update_count, "skipped": skip_count}



def update_all_keywords(keywords: list, max_pages=3, batch_size=10):
    """
    Run update for all keywords in list.
    """
    total_inserted = total_updated = total_skipped = 0

    for kw in keywords:
        result = update_one_keyword(kw, max_pages=max_pages, batch_size=batch_size)
        total_inserted += result["inserted"]
        total_updated += result["updated"]
        total_skipped += result["skipped"]

    print("\n[Summary]")
    print(f"- Total Inserted: {total_inserted}")
    print(f"- Total Updated: {total_updated}")
    print(f"- Total Skipped: {total_skipped}")
