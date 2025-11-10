# arxiv/fetch_arxiv.py

import feedparser
import duckdb
import os
import pandas as pd
from datetime import datetime

# Basic Set Up
ARXIV_FEED_URL = "http://export.arxiv.org/rss/cs.AI"
DB_PATH = "arxiv/arxiv_trends.duckdb"

def fetch_arxiv_entries():
    """
    Fetch recent entries from the arXiv RSS feed.
    Parses title, summary, link, publication date, and assigns a category.
    """
    feed = feedparser.parse(ARXIV_FEED_URL)
    entries = []
    for entry in feed.entries:
        entries.append({
            "title": entry.title,
            "summary": entry.summary,
            "link": entry.link,
            "published": datetime(*entry.published_parsed[:6]),
            "category": "cs.AI"
        })
    return entries

def save_to_duckdb(entries):
    """
    Save the fetched arXiv entries into a DuckDB database.
    Creates the table if it doesn't already exist.
    """
    conn = duckdb.connect(DB_PATH)
    # Create table if it doesn't exist
    conn.execute("""
        CREATE TABLE IF NOT EXISTS arxiv_papers (
            title TEXT,
            summary TEXT,
            link TEXT,
            published TIMESTAMP,
            category TEXT
        )
    """)
    df = pd.DataFrame(entries)
    # Register the list of dicts as a temporary table
    conn.register("temp_entries", df)
    # Insert new entries into the main table
    conn.execute("INSERT INTO arxiv_papers SELECT * FROM temp_entries")
    conn.close()

if __name__ == "__main__":
    # Run the pipeline: fetch and store arXiv data
    entries = fetch_arxiv_entries()
    save_to_duckdb(entries)
    print(f"Saved {len(entries)} entries to {DB_PATH}")
