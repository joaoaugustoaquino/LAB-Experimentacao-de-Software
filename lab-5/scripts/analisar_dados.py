import os
import pandas as pd
import numpy as np
from scipy import stats

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
INPUT_CSV = os.path.join(DATA_DIR, "resultados_brutos.csv")

df = pd.read_csv(INPUT_CSV)

print("=" * 70)
print("1. VALIDAÇÃO E LIMPEZA DOS DADOS")
print("=" * 70)
print(f"Total de medições carregadas: {len(df)}")

# Remove falhas
antes = len(df)
df = df[df["sucesso"] == True].copy()
print(f"Medições com sucesso=True: {len(df)} (removidas {antes - len(df)} falhas)")

# Remove outliers extremos via IQR por tratamento (apenas tempo de resposta)
def remover_outliers_iqr(grupo, coluna):
    q1 = grupo[coluna].quantile(0.25)
    q3 = grupo[coluna].quantile(0.75)
    iqr = q3 - q1
    lim_inf = q1 - 1.5 * iqr
    lim_sup = q3 + 1.5 * iqr
    return grupo[(grupo[coluna] >= lim_inf) & (grupo[coluna] <= lim_sup)]

partes = [remover_outliers_iqr(g, "tempo_resposta_ms") for _, g in df.groupby("tratamento")]
df_limpo = pd.concat(partes, ignore_index=True)
print(f"Após remoção de outliers (IQR) em tempo_resposta_ms: {len(df_limpo)} "
      f"(removidos {len(df) - len(df_limpo)})")

df = df_limpo

rest = df[df["tratamento"] == "REST"]
graphql = df[df["tratamento"] == "GraphQL"]

print("\n" + "=" * 70)
print("2. ESTATÍSTICA DESCRITIVA")
print("=" * 70)

descritivas = []
for nome, grupo in [("REST", rest), ("GraphQL", graphql)]:
    for metrica, label in [("tempo_resposta_ms", "Tempo de Resposta (ms)"),
                            ("tamanho_resposta_bytes", "Tamanho da Resposta (bytes)")]:
        desc = {
            "tratamento": nome,
            "metrica": label,
            "n": len(grupo),
            "media": grupo[metrica].mean(),
            "mediana": grupo[metrica].median(),
            "desvio_padrao": grupo[metrica].std(),
            "min": grupo[metrica].min(),
            "max": grupo[metrica].max(),
            "q1": grupo[metrica].quantile(0.25),
            "q3": grupo[metrica].quantile(0.75),
        }
        descritivas.append(desc)
        print(f"\n[{nome}] {label}")
        print(f"  n={desc['n']}  média={desc['media']:.2f}  mediana={desc['mediana']:.2f}  "
              f"dp={desc['desvio_padrao']:.2f}  min={desc['min']:.2f}  max={desc['max']:.2f}")

df_desc = pd.DataFrame(descritivas)
df_desc.to_csv(os.path.join(DATA_DIR, "estatisticas_descritivas.csv"), index=False)

print("\n" + "=" * 70)
print("3. TESTE DE NORMALIDADE (Shapiro-Wilk)")
print("=" * 70)

resultados_normalidade = {}
for nome, grupo in [("REST", rest), ("GraphQL", graphql)]:
    for metrica in ["tempo_resposta_ms", "tamanho_resposta_bytes"]:
        stat, p = stats.shapiro(grupo[metrica])
        resultados_normalidade[(nome, metrica)] = p
        normal = "SIM (p > 0.05)" if p > 0.05 else "NÃO (p <= 0.05)"
        print(f"  {nome:8s} | {metrica:25s} | W={stat:.4f} p={p:.4f} | Normal? {normal}")

print("\n" + "=" * 70)
print("4. TESTES DE HIPÓTESE (RQ1: tempo | RQ2: tamanho)")
print("=" * 70)

resultados_testes = []

for metrica, rq, label in [
    ("tempo_resposta_ms", "RQ1", "Tempo de Resposta"),
    ("tamanho_resposta_bytes", "RQ2", "Tamanho da Resposta"),
]:
    # Agrega por repositório x repetição para garantir pareamento correto
    pivot = df.pivot_table(
        index=["repositorio", "repeticao"],
        columns="tratamento",
        values=metrica,
        aggfunc="mean",
    ).dropna()

    rest_vals = pivot["REST"]
    graphql_vals = pivot["GraphQL"]

    p_rest = resultados_normalidade[("REST", metrica)]
    p_graphql = resultados_normalidade[("GraphQL", metrica)]
    ambos_normais = p_rest > 0.05 and p_graphql > 0.05

    if ambos_normais:
        stat, p_valor = stats.ttest_rel(rest_vals, graphql_vals)
        teste_usado = "t-Student pareado"
    else:
        stat, p_valor = stats.wilcoxon(rest_vals, graphql_vals)
        teste_usado = "Wilcoxon (pareado, não-paramétrico)"

    diferenca_mediana = (rest_vals - graphql_vals).median()
    significativo = p_valor < 0.05

    print(f"[{rq}] {label}")
    print(f"  Teste utilizado: {teste_usado}")
    print(f"  Estatística = {stat:.4f}   p-valor = {p_valor:.6f}")
    print(f"  Diferença mediana (REST - GraphQL) = {diferenca_mediana:.2f}")
    print(f"  Resultado: {'REJEITA H0 (diferença significativa)' if significativo else 'NÃO rejeita H0 (sem evidência de diferença)'}")
    print()

    resultados_testes.append({
        "RQ": rq,
        "metrica": label,
        "teste": teste_usado,
        "estatistica": stat,
        "p_valor": p_valor,
        "diferenca_mediana_REST_menos_GraphQL": diferenca_mediana,
        "significativo_5pct": significativo,
    })

pd.DataFrame(resultados_testes).to_csv(os.path.join(DATA_DIR, "testes_hipotese.csv"), index=False)

# Salva dataset limpo para uso no dashboard
df.to_csv(os.path.join(DATA_DIR, "resultados_limpos.csv"), index=False)

print("=" * 70)
print("Arquivos gerados em data/: estatisticas_descritivas.csv, "
      "testes_hipotese.csv, resultados_limpos.csv")
print("=" * 70)
