# fetch.py

import requests
import duckdb
import time

# Check API rate limit 
def check_rate_limit(headers):
    url = "https://api.github.com/rate_limit"
    response = requests.get(url, headers=headers)
    data = response.json()
    
    remaining = data["rate"]["remaining"]
    reset_time = data["rate"]["reset"]
    
    print(f"API Requests Remaining: {remaining}")
    
    # if the remaining time is 0, set the time to wait 
    if remaining == 0:
        wait_time = reset_time - time.time()
        print(f"API rate limit reached. Waiting {wait_time:.2f} seconds...")
        time.sleep(wait_time + 1)

# Automatic retry the failed request
def fetch_github_data(url, headers, retries=3, wait_time=5):
    """
    When getting data from GitHub API, retry actumatically when error 
    - `retries`: the maximum times of retry 
    - `wait_time`: the iterval time of waiting for retry
    """
    for attempt in range(retries):
        check_rate_limit(headers)
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        
        print(f"API request failed (Attempt {attempt+1}/{retries}) - Status Code: {response.status_code}")
        
        # if it is API rate limit error (403), then wait for 60 seconds 
        if response.status_code == 403:
            print("Rate limit exceeded. Waiting 60 seconds before retrying...")
            time.sleep(60)
        elif response.status_code == 409:
            print("API Conflict (409) - Skipping this request.")
            return None
        else:
            time.sleep(wait_time)  # Other error, wait for several seconds and retry
    
    print("All retry attempts failed. Returning None.")
    return None  # retries all failed, reutrn None All

# Only get the most updated database, if this is most updated version, skip API request 
def should_fetch_repo(repo_name, last_updated, db_path):
    """check if the database needs to be updated, if it is most updated, not renew"""
    conn = duckdb.connect(db_path)
    cursor = conn.cursor()

    # Ensures the database schema exists
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
    
    cursor.execute("SELECT updated_at FROM github_trends WHERE full_name = ?", (repo_name,))
    result = cursor.fetchall()  
    
    conn.close()
    
    # if the database do not have this data, then fetch the new data
    if not result:
        return True
    
    # if the updated_at in the database is the same as API, not need to update
    db_updated_at = result[0]
    return db_updated_at != last_updated

# Enhance API paging support
def fetch_all_pages(query, headers, db_path, max_pages=3):
    """
    Traverse multiple pages of the GitHub API to get more data.
    - `max_pages`: Maximum number of requested pages
    """
    all_repos = []
    check_rate_limit(headers)  # check the API rate limit for the first time
    
    for page in range(1, max_pages + 1):
        check_rate_limit(headers)
        url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=100&page={page}"

        # recude the possibility of API conflicts
        time.sleep(2) 
        
        data = fetch_github_data(url, headers)

        if data is None:
            print(f"API return None，skip the qurey：{url}")
            break  # stop requiring 
        
        if data and "items" in data:
            for repo in data["items"]:
                if should_fetch_repo(repo["full_name"], repo["updated_at"], db_path):
                    all_repos.append(repo)
        else:
            print(f"GitHub return empty result，stop asking, there might be no matching repo")
            break  # No more data, then stop
        
        # only sleep when nearly exceed the API rate limit , avoid spedning extra time 
        if len(all_repos) % 500 == 0:
            print("Taking a short break to avoid hitting the rate limit...")
            time.sleep(10)  
    
    return all_repos
