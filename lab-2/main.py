import os
import requests
from scripts.get_repos import get_repos, save_repos
from scripts.clone_repos import clone_repo
from scripts.run_ck import run_ck


def main():
    # 1. pegar repos
    if not os.path.exists("data/repos.txt"):
        repos = get_repos()
        save_repos(repos)
    else:
        with open("data/repos.txt") as f:
            repos = [line.strip() for line in f]

    # 2. clonar 1 repo
    os.makedirs("repos", exist_ok=True)
    clone_repo(repos[0])

    # 3. rodar CK
    repo_name = repos[0].split("/")[-1].replace(".git", "")
    repo_path = f"repos/{repo_name}"

    run_ck(repo_path)


if __name__ == "__main__":
    main()