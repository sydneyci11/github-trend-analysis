# tests/test_keyword_update.py

from update.keyword_update import update_all_keywords

if __name__ == "__main__":
    keywords = ["LLM", "LangChain", "Web3", "AI Agents"]
    update_all_keywords(keywords, max_pages=1, batch_size=10)
