# scheduled_job.py

from update.keyword_update import update_all_keywords

if __name__ == "__main__":
    keywords = ["AI", "LLM", "LangChain", "Web3"]
    update_all_keywords(keywords, max_pages=3, batch_size=10)
