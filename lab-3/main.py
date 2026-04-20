import requests
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

GITHUB_TOKEN = "token"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

BASE_URL = "https://api.github.com"

MAX_PAGES = 2

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
            print("Erro repos:", res.status_code, res.text)
            return []

        data = res.json()
        items = data.get("items", [])

        for r in items:
            if r["language"] in [None, "Markdown"]:
                continue
            repos.append(r)

    return repos[:200]

def has_min_prs(owner, repo):
    url = f"{BASE_URL}/search/issues"
    params = {
        "q": f"repo:{owner}/{repo} type:pr state:closed"
    }

    res = requests.get(url, headers=HEADERS, params=params)

    if res.status_code != 200:
        return False

    data = res.json()
    return data.get("total_count", 0) >= 100

def get_prs(owner, repo):
    prs = []
    page = 1

    while page <= MAX_PAGES:
        url = f"{BASE_URL}/repos/{owner}/{repo}/pulls"
        params = {
            "state": "closed",
            "per_page": 100,
            "page": page
        }

        res = requests.get(url, headers=HEADERS, params=params)

        if res.status_code != 200:
            print(f"Erro PR {owner}/{repo}:", res.status_code)
            break

        data = res.json()

        if not isinstance(data, list) or not data:
            break

        for pr in data:
            created = pr.get("created_at")
            closed = pr.get("closed_at")

            if not created or not closed:
                continue

            fmt = "%Y-%m-%dT%H:%M:%SZ"
            created_dt = datetime.strptime(created, fmt)
            closed_dt = datetime.strptime(closed, fmt)

            analysis_time = (closed_dt - created_dt).total_seconds()

            # 🔥 filtro obrigatório do lab
            if analysis_time < 3600:
                continue

            pr_data = {
                "repo": f"{owner}/{repo}",
                "analysis_time": analysis_time,
                "comments": pr.get("comments", 0),
                "description_length": len(pr.get("body") or ""),
                "status": "merged" if pr.get("merged_at") else "closed"
            }

            prs.append(pr_data)

        page += 1

    return prs

def process_repo(r):
    owner = r["owner"]["login"]
    name = r["name"]

    print(f"Processando {owner}/{name}...")

    if not has_min_prs(owner, name):
        return []

    return get_prs(owner, name)


def main():
    repos = get_top_repos()

    dataset = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(process_repo, repos)

    for prs in results:
        dataset.extend(prs)

    print("Total PRs coletados:", len(dataset))


if __name__ == "__main__":
    main()