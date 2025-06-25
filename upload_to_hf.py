# upload_to_hf.py
from huggingface_hub import upload_file
import os 

REPO_ID = "sydneyci11/github_trend_db"       
FILE_PATH = "github_trends.duckdb" # the file going to upload
TARGET_PATH = "github_trends.duckdb"        # upload to repo
TOKEN = os.environ.get("HF_TOKEN")

# upload file to HF dataset repo
upload_file(
    path_or_fileobj=FILE_PATH,
    path_in_repo=TARGET_PATH,
    repo_id=REPO_ID,
    repo_type="dataset",
    token=TOKEN  
)

print(f"Uploaded '{FILE_PATH}' to Hugging Face repo '{REPO_ID}' as '{TARGET_PATH}'")
