import os
import pandas as pd

def merge_class_data():
    all_data = []
    repos_dir = "repos"

    for repo in os.listdir(repos_dir):
        path = os.path.join(repos_dir, repo, "ck_outputclass.csv")

        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                df["repo"] = repo
                all_data.append(df)
            except:
                print(f"Erro lendo {path}")

    if not all_data:
        print("Nenhum dado encontrado.")
        return

    final_df = pd.concat(all_data, ignore_index=True)
    final_df.to_csv("data/final_class.csv", index=False)

    print("CSV final gerado em data/final_class.csv")

if __name__ == "__main__":
    merge_class_data()