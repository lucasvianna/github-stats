import argparse
import requests
import os
from datetime import datetime, timedelta


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

def calculate_coding_time(commits):
    if not commits:
        return 0
    first_commit_time = datetime.strptime(commits[0]['commit']['committer']['date'], "%Y-%m-%dT%H:%M:%SZ")
    last_commit_time = datetime.strptime(commits[-1]['commit']['committer']['date'], "%Y-%m-%dT%H:%M:%SZ")
    coding_time = last_commit_time - first_commit_time
    return coding_time.total_seconds() / 60  # Convert to minutes

def calculate_pickup_time(pull_request, comments):
    pull_request_time = datetime.strptime(pull_request['created_at'], "%Y-%m-%dT%H:%M:%SZ")
    first_comment_time = None
    pull_request_closed_at = None

    if comments:
        first_comment_time = datetime.strptime(comments[0]['created_at'], "%Y-%m-%dT%H:%M:%SZ")
        return (first_comment_time - pull_request_time).total_seconds() / 60  # Convert to minutes

    if pull_request['state'] == "closed":
        pull_request_closed_at = datetime.strptime(pull_request['closed_at'], "%Y-%m-%dT%H:%M:%SZ")
        return (pull_request_closed_at - pull_request_time).total_seconds() / 60  # Convert to minutes

    return 0

def calculate_merge_frequency(pull_requests):
    if not pull_requests:
        return 0
    first_pull_request_time = datetime.strptime(pull_requests[-1]['created_at'], "%Y-%m-%dT%H:%M:%SZ")
    last_pull_request_time = datetime.strptime(pull_requests[0]['created_at'], "%Y-%m-%dT%H:%M:%SZ")
    total_days =(last_pull_request_time - first_pull_request_time).days
    return len(pull_requests) / max(total_days, 1)  # Avoid division by zero

def calculate_pr_size(pull_request):
    additions = pull_request.get('additions', 0)
    deletions = pull_request.get('deletions', 0)
    return additions + deletions

def print_bechmark_results(title, categories, total_pull_requests):
    print(f"\n{title}:")
    for category, count in categories.items():
        percentage = (count / total_pull_requests) * 100
        print(f"- {category.replace('_', ' ').title()}: {percentage:.2f}%")

def get_params():
    parser = argparse.ArgumentParser(description="GitHub Metrics Script")
    parser.add_argument("owner", help="GitHub repository owner")
    parser.add_argument("repository", help="GitHub repository name")
    parser.add_argument("--summary-only", action="store_true", help="Print summary only")
    return parser.parse_args()

def main():
    args = get_params()

    repo_owner = args.owner
    repo_name = args.repository

    # Set your GitHub token as an environment variable
    github_token = os.environ.get("GITHUB_TOKEN", None)
    if not github_token:
        raise Exception("Please set your GitHub token as an environment variable")

    coding_time_categories = {
        'under_0.5_hours': 0,
        'between_0.5_and_2.5_hours': 0,
        'between_2.5_and_24_hours': 0,
        'over_24_hours': 0
    }

    pickup_time_categories = {
        'under_1_hour': 0,
        'between_1_and_3_hours': 0,
        'between_3_and_14_hours': 0,
        'over_14_hours': 0
    }

    pr_size_categories = {
        'under_98_lines': 0,
        'between_98_and_148_lines': 0,
        'between_148_and_218_lines': 0,
        'over_218_lines': 0
    }

    revert_pull_requests = 0
    hotfix_pull_requests = 0

    # Specify the date since which you want closed pull requests
    closed_since_date = datetime.now() - timedelta(days=8)  # Adjust the number of days as needed

    open_pull_requests = get_pull_requests(repo_owner, repo_name, github_token, state="open")
    closed_pull_requests = get_pull_requests(repo_owner, repo_name, github_token, state="closed", merged=True, since=closed_since_date.isoformat())

    all_pull_requests = open_pull_requests + closed_pull_requests
    total_pull_requests = len(all_pull_requests)

    for pr in all_pull_requests:
        pr_number = pr['number']

        pull_request_details = get_pull_request_details(repo_owner, repo_name, pr_number, github_token)
        comments = get_comments_for_pull_request(repo_owner, repo_name, pr_number, github_token)
        commits = get_commits_for_pull_request(repo_owner, repo_name, pr_number, github_token)

        coding_time = calculate_coding_time(commits)
        pickup_time = calculate_pickup_time(pull_request_details, comments)
        pr_size = calculate_pr_size(pull_request_details)

        # Coding Time categories
        if coding_time < 30:
            coding_time_categories['under_0.5_hours'] += 1
        elif 30 <= coding_time < 150:
            coding_time_categories['between_0.5_and_2.5_hours'] += 1
        elif 150 <= coding_time < 1440:
            coding_time_categories['between_2.5_and_24_hours'] += 1
        else:
            coding_time_categories['over_24_hours'] += 1

        # Pickup Time categories
        if pickup_time < 60:
            pickup_time_categories['under_1_hour'] += 1
        elif 60 <= pickup_time < 180:
            pickup_time_categories['between_1_and_3_hours'] += 1
        elif 180 <= pickup_time < 840:
            pickup_time_categories['between_3_and_14_hours'] += 1
        else:
            pickup_time_categories['over_14_hours'] += 1

        # PR Size categories
        if pr_size < 98:
            pr_size_categories['under_98_lines'] += 1
        elif 98 <= pr_size < 148:
            pr_size_categories['between_98_and_148_lines'] += 1
        elif 148 <= pr_size < 218:
            pr_size_categories['between_148_and_218_lines'] += 1
        else:
            pr_size_categories['over_218_lines'] += 1

        if "revert" in pr['title'].lower():
            revert_pull_requests += 1

        if "hotfix" in pr['title'].lower():
            hotfix_pull_requests += 1

        if not args.summary_only:
            print(f"PR #{pr_number} - State {pr['state']} - {pr['title']}")
            print(f"- Coding Time: {coding_time:.2f} minutes")
            print(f"- Pickup Time: {pickup_time:.2f} minutes")
            print(f"- PR Size: {pr_size} lines\n")

    
    print_bechmark_results("Coding Time benchmark", coding_time_categories, total_pull_requests)
    print_bechmark_results("Pickup Time benchmark", pickup_time_categories, total_pull_requests)
    print_bechmark_results("PR Size benchmark", pr_size_categories, total_pull_requests)
    
    print(f"\nRevert PRs: {revert_pull_requests}")
    print(f"\nHotfix PRs: {hotfix_pull_requests}")

    merge_frequency = calculate_merge_frequency(closed_pull_requests)
    print(f"\nMerge Frequency: {merge_frequency:.2f} PRs per day")


if __name__ == "__main__":
    main()
