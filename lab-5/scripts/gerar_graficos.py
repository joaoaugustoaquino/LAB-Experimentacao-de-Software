"""
LAB05 - Geração de gráficos (Sprint 2 / Sprint 3 - Passo 6)

Lê data/resultados_limpos.csv e gera visualizações em output/graficos/:
  - boxplot_tempo.png
  - boxplot_tamanho.png
  - histograma_tempo.png
  - histograma_tamanho.png
  - barras_media_por_repositorio_tempo.png
  - barras_media_por_repositorio_tamanho.png
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "graficos")
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(os.path.join(DATA_DIR, "resultados_limpos.csv"))

sns.set_theme(style="whitegrid", palette="Set2")
PALETA = {"REST": "#4C72B0", "GraphQL": "#DD8452"}

# 1. Boxplot - Tempo de resposta
plt.figure(figsize=(7, 5))
sns.boxplot(data=df, x="tratamento", y="tempo_resposta_ms", hue="tratamento",
            palette=PALETA, legend=False)
plt.title("Distribuição do Tempo de Resposta por Tratamento")
plt.xlabel("Tratamento")
plt.ylabel("Tempo de Resposta (ms)")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "boxplot_tempo.png"), dpi=150)
plt.close()

# 2. Boxplot - Tamanho da resposta
plt.figure(figsize=(7, 5))
sns.boxplot(data=df, x="tratamento", y="tamanho_resposta_bytes", hue="tratamento",
            palette=PALETA, legend=False)
plt.title("Distribuição do Tamanho da Resposta por Tratamento")
plt.xlabel("Tratamento")
plt.ylabel("Tamanho da Resposta (bytes)")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "boxplot_tamanho.png"), dpi=150)
plt.close()

# 3. Histograma - Tempo de resposta
plt.figure(figsize=(8, 5))
for trat in ["REST", "GraphQL"]:
    subset = df[df["tratamento"] == trat]
    sns.histplot(subset["tempo_resposta_ms"], label=trat, color=PALETA[trat],
                 kde=True, alpha=0.5)
plt.title("Histograma do Tempo de Resposta")
plt.xlabel("Tempo de Resposta (ms)")
plt.ylabel("Frequência")
plt.legend(title="Tratamento")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "histograma_tempo.png"), dpi=150)
plt.close()

# 4. Histograma - Tamanho da resposta
plt.figure(figsize=(8, 5))
for trat in ["REST", "GraphQL"]:
    subset = df[df["tratamento"] == trat]
    sns.histplot(subset["tamanho_resposta_bytes"], label=trat, color=PALETA[trat],
                 kde=True, alpha=0.5)
plt.title("Histograma do Tamanho da Resposta")
plt.xlabel("Tamanho da Resposta (bytes)")
plt.ylabel("Frequência")
plt.legend(title="Tratamento")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "histograma_tamanho.png"), dpi=150)
plt.close()

# 5. Barras - média de tempo por repositório
plt.figure(figsize=(10, 6))
media_repo_tempo = df.groupby(["repositorio", "tratamento"])["tempo_resposta_ms"].mean().reset_index()
sns.barplot(data=media_repo_tempo, x="repositorio", y="tempo_resposta_ms", hue="tratamento",
            palette=PALETA)
plt.title("Tempo Médio de Resposta por Repositório")
plt.xlabel("Repositório")
plt.ylabel("Tempo Médio de Resposta (ms)")
plt.xticks(rotation=45, ha="right")
plt.legend(title="Tratamento")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "barras_media_por_repositorio_tempo.png"), dpi=150)
plt.close()

# 6. Barras - média de tamanho por repositório
plt.figure(figsize=(10, 6))
media_repo_tamanho = df.groupby(["repositorio", "tratamento"])["tamanho_resposta_bytes"].mean().reset_index()
sns.barplot(data=media_repo_tamanho, x="repositorio", y="tamanho_resposta_bytes", hue="tratamento",
            palette=PALETA)
plt.title("Tamanho Médio de Resposta por Repositório")
plt.xlabel("Repositório")
plt.ylabel("Tamanho Médio de Resposta (bytes)")
plt.xticks(rotation=45, ha="right")
plt.legend(title="Tratamento")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "barras_media_por_repositorio_tamanho.png"), dpi=150)
plt.close()

print(f"6 gráficos gerados em {OUT_DIR}")
