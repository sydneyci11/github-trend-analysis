from update.env_setup import load_github_token, verify_github_token

token = load_github_token(".env")
valid = verify_github_token(token)

if valid:
    print("Test Passed")
else:
    print("Test Failed")
