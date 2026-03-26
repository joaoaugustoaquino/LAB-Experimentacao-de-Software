import os

def load_repos():
    with open("data/repos.txt", "r") as f:
        return [line.strip() for line in f.readlines()]


def clone_repo(url):
    name = url.split("/")[-1].replace(".git", "")
    path = f"repos/{name}"

    if os.path.exists(path):
        print(f"{name} já existe.")
        return

    print(f"Clonando {name}...")
    os.system(f"git clone {url} {path}")


if __name__ == "__main__":
    os.makedirs("repos", exist_ok=True)

    repos = load_repos()

    # ⚠️ S1 → só 1 repo
    clone_repo(repos[0])