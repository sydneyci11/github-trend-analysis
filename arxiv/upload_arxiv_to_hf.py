# upload_arxiv_to_hf.py
from huggingface_hub import upload_file
import os

REPO_ID = "sydneyci11/arxiv_trend_db"          # HF dataset repo
FILE_PATH = "arxiv/arxiv_trends.duckdb"        # local DuckDB file
TARGET_PATH = "arxiv_trends.duckdb"            # name on HF
TOKEN = os.environ.get("HF_TOKEN")             # token from env

# upload file to HF dataset repo
upload_file(
    path_or_fileobj=FILE_PATH,
    path_in_repo=TARGET_PATH,
    repo_id=REPO_ID,
    repo_type="dataset",
    token=TOKEN
)

print(f"Uploaded '{FILE_PATH}' to Hugging Face repo '{REPO_ID}' as '{TARGET_PATH}'")
