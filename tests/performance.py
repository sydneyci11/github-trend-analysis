# performance.py

import time
import duckdb
from update.fetch import fetch_github_data
from update.fetch_and_store import save_to_db
from config import HEADERS, DB_PATH

headers = HEADERS
db_path = DB_PATH

def test_api_and_db_efficiency(query, max_pages=3):
    """
    Test GitHub API response time and database update performance.
    """
    api_call_count = 0
    total_response_time = 0
    insert_count = 0
    update_count = 0
    
    all_repos = []
    for page in range(1, max_pages + 1):
        url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=100&page={page}"
        
        start_time = time.time()
        data = fetch_github_data(url, headers)
        end_time = time.time()

        if data and "items" in data:
            all_repos.extend(data["items"])
            api_call_count += 1
            total_response_time += (end_time - start_time)
        else:
            break
        
        time.sleep(1) # To avoid rate limiting

    avg_response_time = total_response_time / api_call_count if api_call_count > 0 else 0

    # Test insert and update efficiency
    for repo in all_repos:
        issue_count = repo.get("open_issues_count", 0)
        commits_url = f"https://api.github.com/repos/{repo['full_name']}/commits"
        commits_resp = fetch_github_data(commits_url, headers)
        commit_count = len(commits_resp) if isinstance(commits_resp, list) else 0

        repo_data = (
            repo["name"] or "Unknown",
            repo["full_name"] or "Unknown",
            repo["description"] or "No description available",
            repo["stargazers_count"] or 0,
            repo["forks_count"] or 0,
            repo["language"] or "Not specified",
            repo["watchers_count"] or 0,
            commit_count,
            issue_count,
            repo["created_at"] or "Unknown",
            repo["updated_at"] or "Unknown",
            repo["html_url"] or "No URL available"
        )

        # insert or update database
        operation = save_to_db(repo_data)
        
        if operation == "insert":
            insert_count += 1
        elif operation == "update":
            update_count += 1

    print("-" * 40)
    print(f"API Test Completed:")
    print(f"- Total API Calls: {api_call_count}")
    print(f"- Average Response Time: {avg_response_time:.2f} seconds")
    print(f"DB Update Summary:")
    print(f"- Inserted: {insert_count}")
    print(f"- Updated: {update_count}")


def debug_should_fetch_repo(repo_name, last_updated, db_path):
    import duckdb
    conn = duckdb.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT updated_at FROM github_trends WHERE full_name = ?", (repo_name,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        print(f"[DEBUG] {repo_name} not in DB → fetch needed.")
        return True
    
    db_updated_at = result[0]
    if db_updated_at == last_updated:
        print(f"[SKIP] {repo_name} is already up-to-date.")
    else:
        print(f"[UPDATE] {repo_name} needs update (DB: {db_updated_at} vs API: {last_updated})")
    
    return db_updated_at != last_updated

if __name__ == "__main__":
    test_api_and_db_efficiency("AI robotics", max_pages=2)