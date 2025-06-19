# config.py

from dotenv import load_dotenv
import os
from update.env_setup import verify_github_token

# Load environment variables
load_dotenv()

# GitHub API Token
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Local DuckDB file path
DB_PATH = os.getenv("DATABASE_PATH")

# GitHub request headers
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

if not verify_github_token(GITHUB_TOKEN):
    raise EnvironmentError("GitHub token is invalid or expired.")
elif not GITHUB_TOKEN:
    raise EnvironmentError("GITHUB_TOKEN is not found in environment variables.")