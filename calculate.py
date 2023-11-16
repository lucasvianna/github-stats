from datetime import datetime, timedelta

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
