import os
import shutil

def run_ck(repo_path):
    print("Executando CK...")

    command = f'java -jar "ck/ck.jar" "{repo_path}" false 0 false'
    os.system(command)

    move_outputs(repo_path)


def move_outputs(repo_path):
    output_dir = os.path.join(repo_path, "ck_output")
    os.makedirs(output_dir, exist_ok=True)

    for file in ["class.csv", "method.csv", "field.csv"]:
        if os.path.exists(file):
            shutil.move(file, os.path.join(output_dir, file))
            print(f"{file} movido para {output_dir}")


if __name__ == "__main__":
    repos = os.listdir("repos")

    if not repos:
        print("Nenhum repositório encontrado.")
        exit()

    repo_name = repos[0]
    repo_path = f"repos/{repo_name}"

    run_ck(repo_path)