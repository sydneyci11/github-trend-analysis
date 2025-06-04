from update.fetch import fetch_github_data, check_rate_limit, fetch_all_pages
from config import DB_PATH, HEADERS

headers = HEADERS

# Fetch one page of GitHub search results
def test_fetch_github_search():
    url = "https://api.github.com/search/repositories?q=machine+learning&sort=stars&order=desc"
    data = fetch_github_data(url, headers)

    if data:
        print(f"Successfully fetched {len(data['items'])} repositories!")
    else:
        print("API request completely failed. No data retrieved.")

# Check GitHub API rate limit
def test_check_api_rate_limit():
    check_rate_limit(headers)

# Fetch multiple pages of repositories
# Test: get three pages 
def test_fetch_all_pages():
    all_repos = fetch_all_pages("machine learning", headers=headers, db_path=DB_PATH, max_pages=3)
    print(f"Retrieved {len(all_repos)} repositories across multiple pages.")

# Full test for fetching and processing GitHub data
# Final Test: for API data handling 
def test_api_data_handling():
    query = "machine learning"
    all_repos = fetch_all_pages(query, headers=headers, db_path=DB_PATH, max_pages=3)
    print(f"Retrieved {len(all_repos)} repositories across multiple pages.")

# Run tests manually
if __name__ == "__main__":
    test_check_api_rate_limit()
    test_fetch_github_search()
    test_fetch_all_pages()
    test_api_data_handling()
    print("All tests pass!")