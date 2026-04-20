import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

GITHUB_TOKEN = "token"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

BASE_URL = "https://api.github.com"

MAX_PAGES = 2
MAX_PR_PER_REPO = 15
MAX_REPOS = 40

# -------------------------------
# TOP REPOS
# -------------------------------
def get_top_repos():
    repos = []

    for page in range(1, 3):
        url = f"{BASE_URL}/search/repositories"
        params = {
            "q": "stars:>10000",
            "sort": "stars",
            "order": "desc",
            "per_page": 100,
            "page": page
        }

        res = requests.get(url, headers=HEADERS, params=params)

        if res.status_code != 200:
            print("Erro repos:", res.status_code)
            return []

        data = res.json()

        for r in data.get("items", []):
            if r["language"] in [None, "Markdown"]:
                continue
            if r.get("fork"):
                continue
            if r.get("archived"):
                continue

            repos.append(r)

    return repos[:MAX_REPOS]

def get_pr_details(owner, repo, number):
    url = f"{BASE_URL}/repos/{owner}/{repo}/pulls/{number}"
    res = requests.get(url, headers=HEADERS)

    if res.status_code != 200:
        return None

    return res.json()

def get_reviews(owner, repo, number):
    url = f"{BASE_URL}/repos/{owner}/{repo}/pulls/{number}/reviews"
    res = requests.get(url, headers=HEADERS)

    if res.status_code != 200:
        return []

    data = res.json()
    return data if isinstance(data, list) else []

def get_prs(owner, repo):
    prs = []
    page = 1

    while page <= MAX_PAGES and len(prs) < MAX_PR_PER_REPO:
        url = f"{BASE_URL}/repos/{owner}/{repo}/pulls"
        params = {
            "state": "closed",
            "per_page": 100,
            "page": page
        }

        res = requests.get(url, headers=HEADERS, params=params)

        if res.status_code == 404:
            print(f"Repo sem PRs: {owner}/{repo}")
            return []

        if res.status_code != 200:
            print(f"Erro PR {owner}/{repo}:", res.status_code)
            break

        data = res.json()

        if not isinstance(data, list) or not data:
            break

        for pr in data:
            if len(prs) >= MAX_PR_PER_REPO:
                break

            created = pr.get("created_at")
            closed = pr.get("closed_at")

            if not created or not closed:
                continue

            fmt = "%Y-%m-%dT%H:%M:%SZ"
            created_dt = datetime.strptime(created, fmt)
            closed_dt = datetime.strptime(closed, fmt)

            analysis_time = (closed_dt - created_dt).total_seconds()

            if analysis_time < 3600:
                continue

            number = pr["number"]

            details = get_pr_details(owner, repo, number)
            if not details:
                continue

            reviews = get_reviews(owner, repo, number)
            if len(reviews) == 0:
                continue

            prs.append({
                "repo": f"{owner}/{repo}",
                "analysis_time": analysis_time,
                "comments": pr.get("comments", 0),
                "description_length": len(pr.get("body") or ""),
                "status": "merged" if pr.get("merged_at") else "closed",

                "additions": details.get("additions", 0),
                "deletions": details.get("deletions", 0),
                "files": details.get("changed_files", 0),
                "reviews": len(reviews)
            })

        page += 1

    return prs

def process_repo(r):
    owner = r["owner"]["login"]
    name = r["name"]

    print(f"Processando {owner}/{name}...")

    return get_prs(owner, name)

def main():
    repos = get_top_repos()
    dataset = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(process_repo, repos)

    for prs in results:
        dataset.extend(prs)

    print("Total PRs coletados:", len(dataset))


if __name__ == "__main__":
    main()