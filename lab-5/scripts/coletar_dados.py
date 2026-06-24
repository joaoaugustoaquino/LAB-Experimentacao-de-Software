"""
LAB05 - GraphQL vs REST - Experimento Controlado
Script de coleta de dados (Sprint 1 - Passo 2 / Sprint 2 - Passo 3)

Coleta métricas de tempo de resposta e tamanho de resposta para:
  - API REST do GitHub (api.github.com)
  - API GraphQL do GitHub (api.github.com/graphql)

Ambas consultando os MESMOS repositórios e retornando dados EQUIVALENTES
(nome, descrição, estrelas, forks, linguagem principal, top 5 issues abertas).

Uso:
  export GITHUB_TOKEN="seu_token_aqui"
  python coletar_dados.py

Gera: ../data/resultados_brutos.csv
"""

import os
import sys
import time
import json
import random
import requests
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

TOKEN = os.environ.get("GITHUB_TOKEN")
if not TOKEN:
    print("ERRO: defina a variável de ambiente GITHUB_TOKEN com seu Personal Access Token do GitHub.")
    print('Exemplo: export GITHUB_TOKEN="ghp_xxx..."')
    sys.exit(1)

HEADERS_REST = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

HEADERS_GRAPHQL = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

REST_URL = "https://api.github.com"
GRAPHQL_URL = "https://api.github.com/graphql"

N_REPETICOES = 30          # repetições por repositório por tratamento (>=30 por grupo)
OUTPUT_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "resultados_brutos.csv")

# Lista de objetos experimentais: repositórios públicos populares e estáveis.
# Mesma lista usada nos dois tratamentos (design pareado).
REPOSITORIOS = [
    ("facebook", "react"),
    ("vuejs", "vue"),
    ("angular", "angular"),
    ("torvalds", "linux"),
    ("microsoft", "vscode"),
    ("tensorflow", "tensorflow"),
    ("pytorch", "pytorch"),
    ("django", "django"),
    ("rails", "rails"),
    ("nodejs", "node"),
]

GRAPHQL_QUERY = """
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    name
    description
    stargazerCount
    forkCount
    primaryLanguage { name }
    issues(first: 5, states: OPEN, orderBy: {field: CREATED_AT, direction: DESC}) {
      nodes {
        title
        number
        createdAt
      }
    }
  }
}
"""


def medir_rest(owner, repo):
    """Faz 2 chamadas REST equivalentes aos dados buscados via GraphQL:
    1) dados do repositório  2) últimas 5 issues abertas.
    Mede tempo total e tamanho total (soma dos dois payloads), pois a
    API REST do GitHub não tem um único endpoint que junte repo+issues."""
    t0 = time.perf_counter()

    r1 = requests.get(f"{REST_URL}/repos/{owner}/{repo}", headers=HEADERS_REST, timeout=15)
    r2 = requests.get(
        f"{REST_URL}/repos/{owner}/{repo}/issues",
        headers=HEADERS_REST,
        params={"state": "open", "sort": "created", "direction": "desc", "per_page": 5},
        timeout=15,
    )

    t1 = time.perf_counter()

    ok = r1.status_code == 200 and r2.status_code == 200
    tamanho_bytes = len(r1.content) + len(r2.content)
    tempo_ms = (t1 - t0) * 1000

    return ok, tempo_ms, tamanho_bytes, r1.status_code, r2.status_code


def medir_graphql(owner, repo):
    """Faz 1 chamada GraphQL retornando os dados equivalentes."""
    payload = {"query": GRAPHQL_QUERY, "variables": {"owner": owner, "name": repo}}

    t0 = time.perf_counter()
    r = requests.post(GRAPHQL_URL, headers=HEADERS_GRAPHQL, json=payload, timeout=15)
    t1 = time.perf_counter()

    body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    ok = r.status_code == 200 and "errors" not in body
    tamanho_bytes = len(r.content)
    tempo_ms = (t1 - t0) * 1000

    return ok, tempo_ms, tamanho_bytes, r.status_code


def main():
    linhas = []
    # Monta a sequência de medições intercalando REST/GraphQL e repositórios,
    # para mitigar efeitos de hora do dia / variação de rede / cache (ameaça à validade interna).
    plano = []
    for rep_idx in range(N_REPETICOES):
        for owner, repo in REPOSITORIOS:
            plano.append((owner, repo, rep_idx))
    random.shuffle(plano)  # ordem aleatória dentro de cada leva

    total = len(plano) * 2
    contador = 0

    for owner, repo, rep_idx in plano:
        # Ordem REST/GraphQL também alternada aleatoriamente a cada par
        ordem = ["REST", "GraphQL"]
        random.shuffle(ordem)

        for tratamento in ordem:
            contador += 1
            timestamp = datetime.utcnow().isoformat()

            try:
                if tratamento == "REST":
                    ok, tempo_ms, tamanho_bytes, *status = medir_rest(owner, repo)
                else:
                    ok, tempo_ms, tamanho_bytes, *status = medir_graphql(owner, repo)
            except requests.exceptions.RequestException as e:
                print(f"  [ERRO] {owner}/{repo} ({tratamento}): {e}")
                ok, tempo_ms, tamanho_bytes = False, None, None

            linhas.append({
                "timestamp": timestamp,
                "repositorio": f"{owner}/{repo}",
                "tratamento": tratamento,
                "repeticao": rep_idx,
                "sucesso": ok,
                "tempo_resposta_ms": tempo_ms,
                "tamanho_resposta_bytes": tamanho_bytes,
            })

            print(f"[{contador}/{total}] {tratamento:8s} {owner}/{repo:12s} "
                  f"tempo={tempo_ms:.1f}ms tamanho={tamanho_bytes}B ok={ok}")

            time.sleep(0.3)  # pequena pausa para não saturar rate limit

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    import csv
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=linhas[0].keys())
        writer.writeheader()
        writer.writerows(linhas)

    print(f"\nColeta finalizada. {len(linhas)} medições salvas em {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
