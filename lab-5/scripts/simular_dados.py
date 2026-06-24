"""
Gera um dataset SIMULADO para validar todo o pipeline de análise/relatório/dashboard
ANTES de você rodar a coleta real (que precisa de internet + GITHUB_TOKEN).

Quando você rodar coletar_dados.py na sua máquina com seu token, é só substituir
o arquivo data/resultados_brutos.csv pelo gerado de verdade e rodar de novo os
scripts de análise e dashboard -- nada mais precisa mudar.

A simulação reflete o padrão observado na literatura: GraphQL tende a ter
respostas menores (menos overfetching) mas tempo de resposta similar ou
levemente maior em alguns casos (overhead de resolução de schema).
"""

import os
import csv
import random
import numpy as np
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

REPOSITORIOS = [
    "facebook/react", "vuejs/vue", "angular/angular", "torvalds/linux",
    "microsoft/vscode", "tensorflow/tensorflow", "pytorch/pytorch",
    "django/django", "rails/rails", "nodejs/node",
]

N_REPETICOES = 30
OUTPUT_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "resultados_brutos.csv")

linhas = []
base_time = datetime.utcnow()

for rep_idx in range(N_REPETICOES):
    for repo in REPOSITORIOS:
        for tratamento in ["REST", "GraphQL"]:
            if tratamento == "REST":
                # REST: 2 chamadas (repo + issues) -> tempo um pouco maior, payload maior (overfetching)
                tempo_ms = max(20, np.random.normal(loc=185, scale=35))
                tamanho_bytes = max(500, int(np.random.normal(loc=9800, scale=1400)))
            else:
                # GraphQL: 1 chamada, payload sob medida -> tempo um pouco menor, payload bem menor
                tempo_ms = max(20, np.random.normal(loc=160, scale=40))
                tamanho_bytes = max(300, int(np.random.normal(loc=3100, scale=600)))

            ts = base_time + timedelta(seconds=len(linhas) * 0.3)
            linhas.append({
                "timestamp": ts.isoformat(),
                "repositorio": repo,
                "tratamento": tratamento,
                "repeticao": rep_idx,
                "sucesso": True,
                "tempo_resposta_ms": round(tempo_ms, 2),
                "tamanho_resposta_bytes": tamanho_bytes,
            })

random.shuffle(linhas)

os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=linhas[0].keys())
    writer.writeheader()
    writer.writerows(linhas)

print(f"Dataset simulado gerado: {len(linhas)} medições em {OUTPUT_CSV}")
print("ATENÇÃO: este é um dataset SIMULADO para testar o pipeline.")
print("Rode coletar_dados.py com seu GITHUB_TOKEN para gerar dados reais.")
