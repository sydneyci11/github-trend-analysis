import os
from dotenv import load_dotenv
import requests

def load_github_token(dotenv_path=".env") -> str:
    """
    Load GitHub token from .env file or environment variables.
    Raise error if token is not found or .env does not exist.
    """
    if dotenv_path:
        if not os.path.exists(dotenv_path):
            raise FileNotFoundError(f".env file not found at path: {dotenv_path}")
        load_dotenv(dotenv_path=dotenv_path)
    else:
        load_dotenv()  # fallback to current directory
    token = os.getenv("GITHUB_TOKEN")
    
    if not token:
        raise EnvironmentError("GitHub Token not found. Check your .env file or environment variables.")
    
    print("GitHub Token loaded successfully!")
    return token

def verify_github_token(token: str) -> bool:
    """
    Send a request to GitHub API to verify if token is valid.
    Returns True if valid, False if not.
    """
    headers = {
        "Authorization": f"token {token}"
    }
    url = "https://api.github.com/user"
    resp = requests.get(url, headers=headers)

    if resp.status_code == 200:
        print("GitHub API token is valid.")
        print(f"Authenticated as: {resp.json().get('login')}")
        return True
    else:
        print(f"Token invalid: {resp.status_code} {resp.text}")
        return False
    
if __name__ == "__main__":
    try:
        token = load_github_token()
        valid = verify_github_token(token)
        print("Test Passed" if valid else "Test Failed")
    except Exception as e:
        print(f"Error: {e}")