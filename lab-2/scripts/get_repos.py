import requests

def get_repos():
    headers = {
    "Authorization": "token SEU_TOKEN"
}

    repos = []
    url = "https://api.github.com/search/repositories"

    params = {
        "q": "language:Java",
        "sort": "stars",
        "order": "desc",
        "per_page": 100
    }

    for page in range(1, 11):  # 1000 repos
        params["page"] = page
        response = requests.get(url, params=params, headers=headers)

        if response.status_code != 200:
            print("Erro na API:", response.status_code)
            break

        data = response.json()

        for item in data["items"]:
            repos.append(item["clone_url"])

    return repos


def save_repos(repos):
    with open("data/repos.txt", "w") as f:
        for repo in repos:
            f.write(repo + "\n")


if __name__ == "__main__":
    repos = get_repos()
    save_repos(repos)
    print(f"{len(repos)} repositórios salvos.")