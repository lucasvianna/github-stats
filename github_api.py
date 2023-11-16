import requests

def get_pull_requests(repo_owner, repo_name, github_token, state="all", merged=False, since=None):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"
    params = {"state": state}
    
    if since:
        params["since"] = since
    if merged:
        params["merged"] = "true"

    headers = {"Authorization": f"Bearer {github_token}"}
    response = requests.get(url, params=params, headers=headers)
    return response.json()

def get_comments_for_pull_request(repo_owner, repo_name, pull_request_number, github_token):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pull_request_number}/comments"
    headers = {"Authorization": f"Bearer {github_token}"}
    response = requests.get(url, headers=headers)
    return response.json()

def get_commits_for_pull_request(repo_owner, repo_name, pull_request_number, github_token):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pull_request_number}/commits"
    headers = {"Authorization": f"Bearer {github_token}"}
    response = requests.get(url, headers=headers)
    return response.json()

def get_pull_request_details(repo_owner, repo_name, pull_request_number, github_token):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pull_request_number}"
    headers = {"Authorization": f"Bearer {github_token}"}
    response = requests.get(url, headers=headers)
    return response.json()
