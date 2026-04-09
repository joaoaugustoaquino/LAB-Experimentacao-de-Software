import os
import requests
from scripts.get_repos import get_repos, save_repos
from scripts.clone_repos import clone_repo
from scripts.run_ck import run_ck


def main():
    if not os.path.exists("data/repos.txt"):
        repos_data = get_repos()
        save_repos(repos_data)
        repos = [r["url"] for r in repos_data]
    else:
        with open("data/repos.txt") as f:
            repos = [line.strip() for line in f]

    os.makedirs("repos", exist_ok=True)

    for repo_url in repos[:1000]:
        try:
            clone_repo(repo_url)

            repo_name = repo_url.split("/")[-1].replace(".git", "")
            repo_path = f"repos/{repo_name}"

            run_ck(repo_path)

        except Exception as e:
            print(f"Erro em {repo_url}: {e}")


if __name__ == "__main__":
    main()